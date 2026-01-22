#!/usr/bin/env python3
"""CLI-Helfer, um lokale Ollama-Modelle mit Übersetzungskontext zu befragen.

Das Skript nutzt dieselben Pairing- und Segmentierungsfunktionen wie
``generate_translation_report.py``. So kann man gezielt Quelle/Ziel-Segmente
an ein Ollama-Modell schicken und etwaige Fragen zur Übersetzung stellen.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from neutral_pairing_service import FilePair, PairingService
from tools import generate_translation_report as report_tool

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def format_context(segments: List[Tuple[str, str]], max_segments: int | None = None) -> str:
    if max_segments:
        segments = segments[:max_segments]
    lines: List[str] = []
    for idx, (src, tgt) in enumerate(segments, 1):
        lines.append(f"Segment {idx}\nSOURCE: {src}\nTARGET: {tgt}")
    return "\n\n".join(lines)


def fetch_pairs(base: Path, target_project: str | None) -> Dict[str, List[FilePair]]:
    projects: Dict[str, Dict[str, List[Path]]] = defaultdict(lambda: {"source": [], "translation": [], "unknown": []})
    for path in report_tool.iter_supported_files(base):
        key = report_tool.project_key(path, base)
        if target_project and key != target_project:
            continue
        role = report_tool.classify_role(path)
        projects[key][role].append(path)
    result: Dict[str, List[FilePair]] = {}
    pairing = PairingService()
    for key, buckets in projects.items():
        sources = sorted(set(buckets.get("source", [])))
        targets = sorted(set(buckets.get("translation", [])))
        if not sources or not targets:
            continue
        source_paths = [str(p) for p in sources]
        target_paths = [str(p) for p in targets]
        pairs, unmatched_src, unmatched_tgt = pairing.pair(source_paths, target_paths)
        if not pairs and source_paths and target_paths:
            fallback: List[FilePair] = []
            limit = min(len(source_paths), len(target_paths))
            for idx in range(limit):
                fallback.append(
                    FilePair(
                        source=source_paths[idx],
                        translation=target_paths[idx],
                        similarity=0.0,
                        source_name=Path(source_paths[idx]).name,
                        translation_name=Path(target_paths[idx]).name,
                    )
                )
            pairs = fallback
        if pairs:
            result[key] = pairs
    return result


def collect_segments(pair: FilePair) -> List[Tuple[str, str]]:
    src_text = report_tool.read_text(Path(pair.source))
    tgt_text = report_tool.read_text(Path(pair.translation))
    return report_tool.build_segments(src_text, tgt_text)


def call_ollama(model: str, prompt: str, url: str = DEFAULT_OLLAMA_URL, stream: bool = False) -> str:
    payload = {"model": model, "prompt": prompt, "stream": stream}
    data = json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json"})
    with urlopen(request) as response:  # noqa: S310
        raw = response.read().decode("utf-8")
    if stream:
        parts = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                parts.append(json.loads(line).get("response", ""))
            except json.JSONDecodeError:
                continue
        return "".join(parts).strip()
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return raw.strip()
    return str(obj.get("response", "")).strip()


def summarize_findings(segments: List[Tuple[str, str]]) -> str:
    counts = Counter()
    for src, tgt in segments:
        if src == tgt:
            counts["identisch"] += 1
        elif not tgt:
            counts["leer"] += 1
    parts = [f"Segments insgesamt: {len(segments)}"]
    if counts:
        parts.append(", ".join(f"{label}: {count}" for label, count in counts.items()))
    return " | ".join(parts)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Frage Ollama zu einer Übersetzung")
    parser.add_argument("--question", "-q", help="Frage an das Modell", required=True)
    parser.add_argument("--project", help="Projekt-Key (z. B. basti/2025-08-12)")
    parser.add_argument("--pair", type=int, default=1, help="1-basierter Index des Paars im Projekt")
    parser.add_argument("--model", default="llama3", help="Ollama-Modellname")
    parser.add_argument("--base", help="Basisordner mit Projekten")
    parser.add_argument("--config", default="checker_config.json", help="Pfad zur checker_config.json")
    parser.add_argument("--segments", type=int, help="Maximalzahl Segmente im Kontext")
    parser.add_argument("--show-context", action="store_true", help="Kontext vor der Anfrage anzeigen")
    args = parser.parse_args(list(argv) if argv is not None else None)

    cfg = report_tool.load_checker_config(Path(args.config))
    base_path = report_tool.resolve_base_path(args.base, cfg)

    pairs_per_project = fetch_pairs(base_path, args.project)
    if not pairs_per_project:
        available = sorted({report_tool.project_key(p, base_path) for p in report_tool.iter_supported_files(base_path)})
        print("Keine Paare gefunden. Verfügbare Projekte:")
        for key in available:
            print(f"  - {key}")
        return 1

    if args.project:
        if args.project not in pairs_per_project:
            print(f"Projekt '{args.project}' enthält keine Paarungen. Verfügbare Projekte:")
            for key in sorted(pairs_per_project.keys()):
                print(f"  - {key}")
            return 1
        selected_project = args.project
    else:
        selected_project = sorted(pairs_per_project.keys())[0]

    project_pairs = pairs_per_project[selected_project]
    if args.pair < 1 or args.pair > len(project_pairs):
        print(f"Ungültiger Paar-Index {args.pair}. Projekt '{selected_project}' enthält {len(project_pairs)} Paare.")
        return 1
    pair = project_pairs[args.pair - 1]

    segments = collect_segments(pair)
    if not segments:
        print("Keine Segmente im ausgewählten Paar gefunden.")
        return 1

    context = format_context(segments, args.segments)
    summary = summarize_findings(segments)

    if args.show_context:
        print("Kontext:\n" + context + "\n")

    prompt = (
        "Analysiere die folgende Übersetzungsaufgabe und beantworte danach die Frage."
        " Achte auf Zahlen, Terminologie und Stilvorgaben."
        f"\n\nFrage: {args.question}\n\nKontext:\n{context}\n\nZusammenfassung: {summary}\n"
    )

    try:
        response = call_ollama(args.model, prompt)
    except URLError as exc:
        print(f"Fehler beim Aufruf von Ollama ({exc}). Läuft der Server auf {DEFAULT_OLLAMA_URL}?" )
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Fehler bei der Modellabfrage: {exc}")
        return 1

    print(f"Projekt: {selected_project}")
    print(f"Quelle: {pair.source}")
    print(f"Übersetzung: {pair.translation}")
    print(f"Segmente: {len(segments)}")
    print(f"Zusammenfassung: {summary}")
    print("\nAntwort:")
    print(response or "<keine Antwort>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
