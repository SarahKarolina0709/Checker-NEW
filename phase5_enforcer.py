"""DEPRECATED: Datei wurde nach quality_gui_phase5_enforcer.py migriert – bitte neuen Modulnamen nutzen.

Phase 5 – Durchsetzung & Auto-Fix (Enforcer)

Konzept:
 1. Nimmt Roh-Issues (Phasen 1–3) + Phase4-Konsolidierung.
 2. Wendet deterministische Safe-Autofixes auf Zielsegmente an (keine Platzhalter / Tags / Zahlen-Struktur verletzen).
 3. Optional: Guard Re-Run von Phase1 (Regression verhindern) – Platzhalter / Klammern unverändert.
 4. CI-Gate: Schwellwerte + block_on Codes/Prafixe. Berücksichtigt Baseline/Waivers mit Ablaufdatum.
 5. Artefakte: Unified Diff Patch, Markdown Summary, JSON Summary, optional SARIF.

Keine externen Dependencies. Drop‑in nutzbar ohne UI‑Änderung.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Iterable, List, Tuple, Dict, Any, Optional
import re, difflib, json, os, datetime

try:  # QAIssue Fallback falls Modul nicht importierbar
    from quality_gui_phase1_checkers import QAIssue  # type: ignore
except Exception:  # pragma: no cover
    @dataclass
    class QAIssue:  # type: ignore
        code: str; severity: str; category: str; message: str; source_text: str; target_text: str; meta: dict | None = None

# ---------------------- KONFIG ----------------------
THRESHOLDS = {
    "critical_max": 0,
    "major_max": 8,
    "risk_score_max": 0.55,
    # block_on Einträge: Präfix (z.B. SECURITY_) oder exakter Code
    "block_on": ["SECURITY_", "PLACEHOLDER_MISSING", "HTML_UNBALANCED"],
}

# Safe Auto-Fix Codes (rein textuelle Mikro-Korrekturen)
SAFE_AUTOFIX_CODES = {
    "WS_DOUBLE_SPACE", "WS_TRAILING", "WS_LEADING",
    "PUNCT_DOUBLE", "QUOTE_PLAIN", "QUOTE_MIX", "QUOTE_DE_MISMATCH"
}

# Baseline Datei (optional). Format:
# {"generated":"2025-08-26","waivers":[{"fingerprint":"...","expires":"2025-09-25","reason":"Legacy"}]}
BASELINE_DEFAULT = "qa_baseline.json"

# ---------------------- HELFER: TEXT TRANSFORMATIONEN ----------------------
TAG_SPLIT = re.compile(r"(<[^>]+>)")
MD_LINK_BROKEN = re.compile(r"\[(?P<txt>[^\]\[]+)]\((?P<url>[^)\s]+)\s")  # fehlende schließende Klammer Heuristik
DOUBLE_PUNCT = re.compile(r"([!?\.]){2,}")

UNIT_PATTERN = r"(€|kg|km|m|cm|mm|°C|§)"

def _map_text_parts(s: str, fx):
    parts = TAG_SPLIT.split(s or "")
    for i, p in enumerate(parts):
        if not p or p.startswith("<"):
            continue
        parts[i] = fx(p)
    return "".join(parts)

def _fix_ws(txt: str) -> str:
    txt = re.sub(r"[ \t]{2,}", " ", txt)  # doppelte Spaces
    txt = re.sub(r"[ \t]+$", "", txt, flags=re.MULTILINE)  # trailing
    txt = re.sub(r"^[ \t]+", "", txt, flags=re.MULTILINE)  # leading
    return txt

def _fix_quotes_de(txt: str) -> str:
    # Gerade Anführungszeichen in deutsch „…“ wenn Anzahl gerade
    if txt.count('"') % 2 == 0 and txt.count('"') > 0:
        out, toggle = [], True
        for ch in txt:
            if ch == '"':
                out.append("„" if toggle else "“")
                toggle = not toggle
            else:
                out.append(ch)
        txt = "".join(out)
    return txt

def _fix_percent_spacing_de(txt: str) -> str:
    # Kein Space vor %, NBSP vor Einheiten & §
    txt = re.sub(r"\s+%", "%", txt)
    txt = re.sub(rf"(\d)\s+{UNIT_PATTERN}", r"\1\u00A0\2", txt)
    return txt

def _fix_double_punct(txt: str) -> str:
    return DOUBLE_PUNCT.sub(lambda m: m.group(0)[0], txt)

def _fix_md_links(txt: str) -> str:
    # Schließt fehlende ) am Ende einfacher Muster heuristisch
    return MD_LINK_BROKEN.sub(lambda m: f"[{m.group('txt')}]({m.group('url')})", txt)

def _apply_safe_fixes(s: str) -> str:
    # Reihenfolge bewusst klein → idempotent
    s2 = _map_text_parts(s, _fix_ws)
    s2 = _map_text_parts(s2, _fix_double_punct)
    s2 = _map_text_parts(s2, _fix_quotes_de)
    s2 = _map_text_parts(s2, _fix_percent_spacing_de)
    s2 = _map_text_parts(s2, _fix_md_links)
    return s2

# ---------------------- AUTO-FIX PIPELINE ----------------------
@dataclass
class AppliedFix:
    code: str
    before: str
    after: str
    idx: int
    note: str = ""

def apply_autofixes(pairs: Iterable[Tuple[str, str]], issues: List[Any]) -> Tuple[List[Tuple[str, str]], List[AppliedFix]]:
    """Wendet Safe-Autofixes auf alle Zielsegmente an.

    Aktuell: Unabhängig von individuellen Issue-Matches – globaler Text-Cleanup.
    (Optional: Später granular pro Issue-Code if code in SAFE_AUTOFIX_CODES)
    """
    new_pairs: List[Tuple[str, str]] = []
    applied: List[AppliedFix] = []
    for idx, (src, tgt) in enumerate(pairs):
        cleaned = _apply_safe_fixes(tgt)
        if cleaned != tgt:
            applied.append(AppliedFix(code="AUTO_SAFE", before=tgt, after=cleaned, idx=idx, note="whitespace/typografie/punct/md"))
        new_pairs.append((src, cleaned))
    return new_pairs, applied

# ---------------------- PHASE1 GUARD (Regression) ----------------------
PLACEHOLDER_RE = re.compile(r"(%\w|\{[^}]+\}|\$\w+|\d+%|\$\{[^}]+\})")
TAG_RE = re.compile(r"<[^>]+>")
NUMBER_RE = re.compile(r"\b\d+[.,]?\d*\b")

def _fingerprint_structural(text: str) -> str:
    # Extrahiert strukturkritische Tokens
    ph = PLACEHOLDER_RE.findall(text)
    tg = TAG_RE.findall(text)
    nums = NUMBER_RE.findall(text)
    return "|".join([
        ",".join(sorted(ph)),
        ",".join(sorted(tg)),
        ",".join(sorted(nums))
    ])

def phase1_guard(original_pairs: List[Tuple[str, str]], new_pairs: List[Tuple[str, str]]) -> Tuple[bool, List[str]]:
    """Vergleicht strukturkritische Token-Sets (Platzhalter, Tags, Zahlen).
    Verhindert stille Zerstörung durch Auto-Fixes. True=OK."""
    reasons: List[str] = []
    for idx, ((_, old_tgt), (_, new_tgt)) in enumerate(zip(original_pairs, new_pairs)):
        if _fingerprint_structural(old_tgt) != _fingerprint_structural(new_tgt):
            reasons.append(f"struct_change_idx_{idx}")
            if len(reasons) > 5:  # Limit
                break
    return (len(reasons) == 0), reasons

# ---------------------- BASELINE / WAIVER ----------------------
def _load_baseline(path: str | None) -> Dict[str, Any]:
    if not path or not os.path.exists(path):
        return {"waivers": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"waivers": []}

def _issue_fingerprint(issue: QAIssue) -> str:
    src_part = (issue.source_text or "")[:40]
    tgt_part = (issue.target_text or "")[:40]
    return f"{issue.code}|{hash(src_part)}|{hash(tgt_part)}"

def _waived(issue: QAIssue, baseline: Dict[str, Any], today: datetime.date) -> bool:
    fp = _issue_fingerprint(issue)
    for w in baseline.get("waivers", []):
        if w.get("fingerprint") == fp:
            exp = w.get("expires")
            try:
                if exp and datetime.date.fromisoformat(exp) < today:
                    return False  # abgelaufen
            except Exception:
                pass
            return True
    return False

# ---------------------- CI-GATE ----------------------
def gate_and_summarize(phase4_result: Dict[str, Any], raw_issues: List[QAIssue], baseline_path: str | None = None) -> Tuple[bool, List[str]]:
    sev = phase4_result.get("severity_distribution", {}) or {}
    risk = float(phase4_result.get("risk_score", 0.0))
    reasons: List[str] = []
    today = datetime.date.today()
    baseline = _load_baseline(baseline_path)

    # Filter Issues nach Baseline für Zählung (waived werden ignoriert)
    effective_issues = [i for i in raw_issues if not _waived(i, baseline, today)]
    sev_counts: Dict[str, int] = {"critical": 0, "major": 0}
    for i in effective_issues:
        s = (i.severity or "").lower()
        if s in ("critical", "major"):
            sev_counts[s] += 1

    if sev_counts.get("critical", 0) > THRESHOLDS["critical_max"]:
        reasons.append(f"critical>{THRESHOLDS['critical_max']}")
    if sev_counts.get("major", 0) > THRESHOLDS["major_max"]:
        reasons.append(f"major>{THRESHOLDS['major_max']}")
    if risk > THRESHOLDS["risk_score_max"]:
        reasons.append(f"risk>{THRESHOLDS['risk_score_max']}")

    # Block-On Codes/Praefixe
    block_patterns = THRESHOLDS["block_on"]
    for iss in effective_issues:
        code = iss.code
        if any(code == pat or code.startswith(pat) for pat in block_patterns):
            reasons.append(f"block_code:{code}")
            break

    return (len(reasons) == 0), reasons

# ---------------------- ARTIFACT EXPORT ----------------------
def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def export_diff(original: List[Tuple[str, str]], changed: List[Tuple[str, str]]) -> str:
    lines: List[str] = []
    for idx, ((s1, t1), (s2, t2)) in enumerate(zip(original, changed)):
        if t1 == t2:
            continue
        diff = difflib.unified_diff(
            t1.splitlines(), t2.splitlines(),
            fromfile=f"segment_{idx}_before", tofile=f"segment_{idx}_after", lineterm=""
        )
        lines.extend(list(diff))
    return "\n".join(lines)

def export_markdown_summary(phase4_result: Dict[str, Any]) -> str:
    lines = ["### QA Zusammenfassung"]
    lines.append(f"- Total Issues: {phase4_result.get('total',0)}")
    lines.append(f"- Risiko-Score: {phase4_result.get('risk_score',0.0):.2f}")
    if phase4_result.get("primary_focus"):
        lines.append(f"- Primärer Fokus: **{phase4_result['primary_focus']}**")
    sd = phase4_result.get("severity_distribution", {})
    lines.append(f"- Severity: critical {sd.get('critical',0)}, major {sd.get('major',0)}, minor {sd.get('minor',0)}")
    lines.append("")
    lines.append("#### Empfehlungen (Top):")
    for r in phase4_result.get("recommendations", [])[:6]:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("#### Quick-Fixes nach Gruppe:")
    for grp, info in (phase4_result.get("quick_fixes", {}) or {}).items():
        actions = "; ".join(info.get("actions", [])[:3]) or "—"
        lines.append(f"- **{grp}** ({info.get('count',0)}): {actions}")
    return "\n".join(lines)

def export_sarif(raw_issues: List[QAIssue], outfile: str):  # Minimal SARIF 2.1.0
    runs = [{
        "tool": {"driver": {"name": "CheckerPhase5", "informationUri": "https://example.local/qa", "version": "1.0.0"}},
        "results": [
            {
                "ruleId": i.code,
                "level": ("error" if i.severity == "critical" else ("warning" if i.severity == "major" else "note")),
                "message": {"text": i.message},
                "properties": {"category": i.category}
            } for i in raw_issues
        ]
    }]
    sarif = {"version": "2.1.0", "$schema": "https://json.schemastore.org/sarif-2.1.0.json", "runs": runs}
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(sarif, f, ensure_ascii=False, indent=2)

# ---------------------- HAUPT ORCHESTRATOR ----------------------
def enforce_phase5(
    pairs: List[Tuple[str, str]],
    phase1_issues: List[QAIssue],
    phase2_issues: List[QAIssue],
    phase3_issues: List[QAIssue],
    phase4_result: Dict[str, Any],
    baseline_path: str | None = BASELINE_DEFAULT,
    recheck_phase1_fn = None,  # Callable[[Iterable[(src,tgt)]], List[QAIssue]] optional
    out_dir: str = "qa_artifacts",
    write_artifacts: bool = True,
    export_sarif_flag: bool = True,
) -> Dict[str, Any]:
    """Führt Phase 5 End-to-End aus.

    Returns dict mit: pass(bool), reasons(list), applied_fixes(list), artifact_paths(dict)
    """
    original_pairs = list(pairs)
    changed_pairs, applied = apply_autofixes(original_pairs, phase1_issues + phase2_issues + phase3_issues)

    guard_ok, guard_reasons = phase1_guard(original_pairs, changed_pairs)
    if not guard_ok:
        # Revert – Sicherheit vor Veränderung struktureller Tokens
        changed_pairs = original_pairs
        applied.append(AppliedFix(code="AUTO_REVERT", before="", after="", idx=-1, note="phase1_guard_failed:"+",".join(guard_reasons)))

    # Optional erneuter Phase1 Lauf (Regression genau prüfen)
    regression_new: List[QAIssue] = []
    if recheck_phase1_fn and guard_ok:
        try:
            regression_new = recheck_phase1_fn([(s, t) for s, t in changed_pairs])  # type: ignore
        except Exception:
            regression_new = []
    # Nur neue Phase1-Issues im Vergleich? – hier minimal: wenn neue critical → revert
    if any(i.severity == "critical" for i in regression_new):
        changed_pairs = original_pairs
        applied.append(AppliedFix(code="AUTO_REVERT", before="", after="", idx=-1, note="regression_phase1_critical"))

    raw_issues_all = phase1_issues + phase2_issues + phase3_issues
    gate_pass, reasons = gate_and_summarize(phase4_result, raw_issues_all, baseline_path)

    artifacts: Dict[str, str] = {}
    if write_artifacts:
        _ensure_dir(out_dir)
        # Diff
        diff_txt = export_diff(original_pairs, changed_pairs)
        diff_path = os.path.join(out_dir, "phase5_patch.diff")
        with open(diff_path, "w", encoding="utf-8") as f:
            f.write(diff_txt)
        artifacts["diff"] = diff_path
        # Markdown
        md_txt = export_markdown_summary(phase4_result)
        md_path = os.path.join(out_dir, "phase5_summary.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_txt)
        artifacts["markdown"] = md_path
        # JSON Summary
        summary = {
            "pass": gate_pass,
            "reasons": reasons,
            "applied_fixes": [asdict(a) for a in applied],
            "risk_score": phase4_result.get("risk_score"),
            "severity_distribution": phase4_result.get("severity_distribution"),
        }
        json_path = os.path.join(out_dir, "phase5_summary.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        artifacts["json"] = json_path
        # SARIF
        if export_sarif_flag:
            sarif_path = os.path.join(out_dir, "phase5_results.sarif.json")
            try:
                export_sarif(raw_issues_all, sarif_path)
                artifacts["sarif"] = sarif_path
            except Exception:
                pass

    return {
        "pass": gate_pass,
        "reasons": reasons,
        "applied_fixes": applied,
        "artifacts": artifacts,
        "pairs_changed": changed_pairs,
    }

__all__ = [
    "apply_autofixes", "phase1_guard", "gate_and_summarize", "export_markdown_summary",
    "export_diff", "export_sarif", "enforce_phase5", "AppliedFix"
]
