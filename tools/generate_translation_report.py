#!/usr/bin/env python3
"""Utility to analyze translation pairs and export a markdown report.

The script pairs source and target documents, runs quality checks reused from the
GUI code base, and aggregates the findings per project. It is intended as a
non-interactive helper so project managers can share a concise defect list with
translators.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from neutral_pairing_service import FilePair, PairingService
from quality_gui_phase1_checkers import QAIssue, run_phase1_checks
from quality_gui_phase2_checkers import run_phase2_checks

SOURCE_HINTS = (
    "ausgang",
    "quelle",
    "source",
    "_src",
    "01_",
)
TARGET_HINTS = (
    "ziel",
    "target",
    "translation",
    "_tgt",
    "uebersetzung",
    "übersetzung",
    "03_",
    "04_",
)
SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json"}


def load_checker_config(cfg_path: Path) -> Dict[str, object]:
    if not cfg_path.is_file():
        return {}
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def resolve_base_path(base_arg: str | None, cfg: Dict[str, object]) -> Path:
    if base_arg:
        base = Path(base_arg).expanduser().resolve()
    else:
        cfg_base = str(cfg.get("projects_base_path") or "").strip()
        base = Path(cfg_base).expanduser().resolve() if cfg_base else Path("Checker_Projekte").resolve()
    if not base.exists():
        fallback = Path(__file__).resolve().parent.parent / "Checker_Projekte"
        if fallback.exists():
            base = fallback
    if not base.exists():
        raise SystemExit(f"Base path not found: {base}")
    return base


def classify_role(path: Path) -> str:
    name = path.stem.lower()
    parent_tokens = " ".join(part.lower() for part in path.parent.parts)
    if any(h in name for h in TARGET_HINTS):
        return "translation"
    if any(h in name for h in SOURCE_HINTS):
        return "source"
    if any(h in parent_tokens for h in TARGET_HINTS):
        return "translation"
    if any(h in parent_tokens for h in SOURCE_HINTS):
        return "source"
    tokens = f"{parent_tokens} {name}"
    if any(h in tokens for h in TARGET_HINTS):
        return "translation"
    if any(h in tokens for h in SOURCE_HINTS):
        return "source"
    return "unknown"


def project_key(path: Path, base: Path) -> str:
    rel = path.relative_to(base)
    parts = rel.parts
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return "/".join(parts)


def read_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return read_docx_text(path)
    if suffix in SUPPORTED_TEXT_EXTENSIONS:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""
    return ""


def read_docx_text(path: Path) -> str:
    try:
        import docx  # type: ignore

        document = docx.Document(str(path))
        paragraphs = [p.text for p in document.paragraphs if p.text]
        return "\n".join(paragraphs)
    except Exception:
        pass
    try:
        import re
        import zipfile
        from html import unescape

        with zipfile.ZipFile(path) as archive:
            xml_bytes = archive.read("word/document.xml")
        xml = xml_bytes.decode("utf-8", errors="ignore")
        xml = xml.replace("<w:br/>", "\n").replace("</w:p>", "\n")
        text = re.sub(r"<[^>]+>", "", xml)
        return unescape(text)
    except Exception:
        return ""


def iter_supported_files(base: Path) -> Iterable[Path]:
    supported = {".docx"} | SUPPORTED_TEXT_EXTENSIONS
    for path in base.rglob("*"):
        if path.is_file() and path.suffix.lower() in supported:
            yield path


def compute_untranslated_ratio(src: str, tgt: str) -> Tuple[int, int]:
    if not src or not tgt:
        return 0, 0
    src_lines = [line.strip() for line in src.splitlines() if len(line.strip()) > 25]
    tgt_set = {line.strip() for line in tgt.splitlines() if line.strip()}
    if not src_lines:
        return 0, 0
    hits = sum(1 for line in src_lines if line in tgt_set)
    return hits, len(src_lines)


def build_segments(src: str, tgt: str) -> List[Tuple[str, str]]:
    src_lines = [line.strip() for line in src.splitlines() if line.strip()]
    tgt_lines = [line.strip() for line in tgt.splitlines() if line.strip()]
    length = max(len(src_lines), len(tgt_lines))
    segments: List[Tuple[str, str]] = []
    for idx in range(length):
        left = src_lines[idx] if idx < len(src_lines) else ""
        right = tgt_lines[idx] if idx < len(tgt_lines) else ""
        if left or right:
            segments.append((left, right))
    if not segments and (src or tgt):
        segments.append((src, tgt))
    return segments


def issue_to_dict(item: QAIssue) -> Dict[str, object]:
    return {
        "code": item.code,
        "severity": item.severity,
        "category": item.category,
        "message": item.message,
        "source_excerpt": (item.source_text or "")[:160],
        "target_excerpt": (item.target_text or "")[:160],
        "meta": item.meta,
    }


def _format_table_text(value: str) -> str:
    if not value:
        return ""
    safe = value.replace("|", "\\|").replace("\n", "<br>")
    return safe.strip()


def build_report(base: Path, glossary_path: Path | None, validation_cfg: Dict[str, object]) -> Dict[str, object]:
    pairing = PairingService()
    projects: Dict[str, Dict[str, List[Path]]] = defaultdict(lambda: {"source": [], "translation": [], "unknown": []})
    for path in iter_supported_files(base):
        role = classify_role(path)
        key = project_key(path, base)
        projects[key][role].append(path)
    results: Dict[str, object] = {"projects": []}
    summary_severity = Counter()
    total_pairs = 0
    glossary = str(glossary_path) if glossary_path and glossary_path.is_file() else ""
    for key, buckets in sorted(projects.items()):
        sources = sorted(set(buckets.get("source", [])))
        targets = sorted(set(buckets.get("translation", [])))
        unknown = sorted(set(buckets.get("unknown", [])))
        project_entry = {
            "project": key,
            "pairs": [],
            "unmatched_source": [str(p) for p in sources],
            "unmatched_translation": [str(p) for p in targets],
            "unknown_files": [str(p) for p in unknown],
        }
        if not sources or not targets:
            results["projects"].append(project_entry)
            continue
        source_paths = [str(p) for p in sources]
        target_paths = [str(p) for p in targets]
        pair_objs, unmatched_src, unmatched_tgt = pairing.pair(source_paths, target_paths)
        if not pair_objs and source_paths and target_paths:
            fallback_pairs: List[FilePair] = []
            limit = min(len(source_paths), len(target_paths))
            for idx in range(limit):
                src_item = source_paths[idx]
                tgt_item = target_paths[idx]
                fallback_pairs.append(
                    FilePair(
                        source=src_item,
                        translation=tgt_item,
                        similarity=0.0,
                        source_name=Path(src_item).name,
                        translation_name=Path(tgt_item).name,
                    )
                )
            pair_objs = fallback_pairs
            unmatched_src = source_paths[limit:]
            unmatched_tgt = target_paths[limit:]
        project_entry["unmatched_source"] = [str(item) for item in unmatched_src]
        project_entry["unmatched_translation"] = [str(item) for item in unmatched_tgt]
        for pair in pair_objs:
            src_path = Path(pair.source)
            tgt_path = Path(pair.translation)
            src_text = read_text(src_path)
            tgt_text = read_text(tgt_path)
            segments = build_segments(src_text, tgt_text) if (src_text or tgt_text) else []
            issues: List[QAIssue] = []
            if segments:
                issues.extend(run_phase1_checks(segments))
                issues.extend(
                    run_phase2_checks(
                        segments,
                        glossary_path=glossary,
                        config=validation_cfg,
                    )
                )
            issue_dicts = [issue_to_dict(item) for item in issues]
            for issue in issues:
                summary_severity[issue.severity.lower()] += 1
            hits, total = compute_untranslated_ratio(src_text, tgt_text)
            project_entry["pairs"].append(
                {
                    "source": str(src_path),
                    "translation": str(tgt_path),
                    "similarity": round(pair.similarity, 3),
                    "issues": issue_dicts,
                    "untranslated_hits": hits,
                    "untranslated_total": total,
                }
            )
            total_pairs += 1
        results["projects"].append(project_entry)
    results["summary"] = {
        "total_projects": len(results["projects"]),
        "total_pairs": total_pairs,
        "severity_counts": dict(summary_severity),
    }
    return results


def render_markdown(report: Dict[str, object]) -> str:
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    summary = report.get("summary", {})
    sev_counts = summary.get("severity_counts", {})
    header = ["# Translation Quality Report", "", f"Generiert am: {now}"]
    lines = header
    lines.append("")
    lines.append("| Kennzahl | Wert |")
    lines.append("| --- | ---: |")
    lines.append(f"| Projekte | {summary.get('total_projects', 0)} |")
    lines.append(f"| Dokument-Paare | {summary.get('total_pairs', 0)} |")
    if sev_counts:
        for sev, count in sorted(sev_counts.items()):
            lines.append(f"| Findings {sev.upper()} | {count} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    for project in report.get("projects", []):
        lines.append(f"## {project['project']}")
        unmatched_src = project.get("unmatched_source", [])
        unmatched_tgt = project.get("unmatched_translation", [])
        pair_list = project.get("pairs", [])
        project_severity = Counter()
        for pair in pair_list:
            for issue in pair.get("issues", []):
                sev = str(issue.get("severity", "")).lower()
                if sev:
                    project_severity[sev] += 1
        if unmatched_src:
            lines.append(f"- Nicht zugeordnete Ausgangsdateien: {len(unmatched_src)}")
        if unmatched_tgt:
            lines.append(f"- Nicht zugeordnete Übersetzungsdateien: {len(unmatched_tgt)}")
        if project_severity:
            total_project_findings = sum(project_severity.values())
            breakdown = " · ".join(f"{sev.upper()} {count}" for sev, count in sorted(project_severity.items()))
            lines.append(f"- Findings gesamt: {total_project_findings} ({breakdown})")
        if not pair_list:
            lines.append("")
            lines.append("Keine zugeordneten Paare gefunden.")
            lines.append("")
            continue
        lines.append("")
        for idx, pair in enumerate(pair_list, 1):
            source_path = Path(pair["source"])
            target_path = Path(pair["translation"])
            lines.append(f"### Paar {idx}: {source_path.name} → {target_path.name}")
            lines.append(f"- Quelle: `{source_path}`")
            lines.append(f"- Übersetzung: `{target_path}`")
            lines.append(f"- Ähnlichkeit: {pair['similarity']}")
            if pair.get("untranslated_total"):
                ratio = pair["untranslated_hits"] / max(1, pair["untranslated_total"])
                lines.append(
                    f"- Unübersetzte Segmente: {pair['untranslated_hits']} von {pair['untranslated_total']} (Quote {ratio:.2%})"
                )
            issues = pair.get("issues", [])
            issue_counts = Counter()
            for issue in issues:
                sev = str(issue.get("severity", "")).upper()
                if sev:
                    issue_counts[sev] += 1
            if issue_counts:
                total_pair_findings = sum(issue_counts.values())
                breakdown = " · ".join(f"{sev} {count}" for sev, count in sorted(issue_counts.items()))
                lines.append(f"- Findings gesamt: {total_pair_findings} ({breakdown})")
            if not issues:
                lines.append("- Findings: keine")
                lines.append("")
                continue
            lines.append("")
            lines.append("| # | Schweregrad | Regel | Hinweis | Quelle | Übersetzung |")
            lines.append("| ---: | --- | --- | --- | --- | --- |")
            for issue_idx, issue in enumerate(issues, 1):
                sev = issue.get("severity", "?").upper()
                code = issue.get("code", "?")
                message = _format_table_text(issue.get("message", ""))
                src_excerpt = _format_table_text(issue.get("source_excerpt", ""))
                tgt_excerpt = _format_table_text(issue.get("target_excerpt", ""))
                lines.append(
                    f"| {issue_idx} | **{sev}** | `{code}` | {message} | {src_excerpt} | {tgt_excerpt} |"
                )
            lines.append("")
        lines.append("")
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate translation quality report")
    parser.add_argument("--base", help="Base directory containing project folders")
    parser.add_argument("--config", help="Path to checker_config.json", default="checker_config.json")
    parser.add_argument("--output", help="Output markdown file", default=None)
    args = parser.parse_args(list(argv) if argv is not None else None)

    cfg = load_checker_config(Path(args.config))
    base_path = resolve_base_path(args.base, cfg)
    validation_cfg = {}
    try:
        validation_cfg = cfg.get("analysis", {}).get("validation", {})  # type: ignore[assignment]
    except Exception:
        validation_cfg = {}
    glossary_path = None
    try:
        phase2_cfg = cfg.get("analysis", {}).get("phase2", {})  # type: ignore[assignment]
        glossary_value = phase2_cfg.get("glossary_path") if isinstance(phase2_cfg, dict) else None
        if glossary_value:
            glossary_path = Path(glossary_value)
    except Exception:
        glossary_path = None

    report = build_report(base_path, glossary_path, validation_cfg if isinstance(validation_cfg, dict) else {})
    markdown = render_markdown(report)

    output_path = Path(args.output) if args.output else Path("reports") / f"translation_quality_report_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Report written to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
