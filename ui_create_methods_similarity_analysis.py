#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI CREATE* METHOD SIMILARITY ANALYSIS (Option A)
================================================

Zweck:
  - Rein lesende Analyse der _create_* Methoden in `quality_gui_main_app.py`
  - Ermittelt paarweise Ähnlichkeit (kombinierter Score aus Sequenz + strukturellem Pattern Overlap)
  - Bildet Cluster (Threshold-basiert) zur Identifikation von Merge-Kandidaten für spätere Factory/Refactor Schritte (Option B)
  - Generiert zwei Artefakte:
      1. JSON Rohdaten: ui_create_methods_similarity.json
      2. Markdown Kurz-Report: REPORT_UI_CREATE_METHOD_SIMILARITY.md

Warum separate Datei und nicht Erweiterung bestehender Analyzer?
  - `quality_gui_comprehensive_duplicate_analysis.py` arbeitet auf Dateiebene (ganze Dateien) und nicht methodenfeingranular.
  - Diese Analyse ist hochspezifisch (Intra-Datei, Methodenkörper einer einzelnen Klasse, UI-Konstruktionsmuster) und würde den Scope des bestehenden Tools verkomplizieren.
  - Keine Funktionalitätsüberschneidung: Dieses Skript verändert keine Dateien und führt keine Konsolidierung durch (reine Entscheidungsgrundlage).

Nicht-Ziele:
  - Keine automatische Modifikation oder Konsolidierung
  - Keine Änderung bestehender Signaturen / Code

Guidelines berücksichtigt:
  - Script-Duplikat-Prävention: Begründete neue Datei, kein vorhandenes Skript deckt diese Granularität ab.
  - Read-Only / Kein Schreibzugriff außer Output-Artefakte (Reports)
  - Keine externen Abhängigkeiten (nur Standardbibliothek)

Benutzung:
  python ui_create_methods_similarity_analysis.py

Ergebnisbewertung:
  - Score Bereich 0..1 (je höher desto ähnlicher)
  - KombiScore = 0.6 * SequenceMatcherRatio + 0.4 * StructuralTokenJaccard
  - Cluster Threshold Default: 0.72 (anpassbar via CLI arg --threshold)

"""
from __future__ import annotations

import argparse
import difflib
import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Any

TARGET_FILE = Path("quality_gui_main_app.py")
CLASS_NAME = "ProfessionelleUebersetzungsqualitaetsApp"
OUTPUT_JSON = Path("ui_create_methods_similarity.json")
OUTPUT_REPORT = Path("REPORT_UI_CREATE_METHOD_SIMILARITY.md")

# Struktur-Tokens (UI & Layout Muster)
STRUCTURE_TOKEN_REGEX = [
    (re.compile(r"CTkFrame"), "CTKFRAME"),
    (re.compile(r"CTkLabel"), "CTKLABEL"),
    (re.compile(r"CTkButton"), "CTKBUTTON"),
    (re.compile(r"CTkEntry"), "CTKENTRY"),
    (re.compile(r"create_button\("), "CREATE_BUTTON"),
    (re.compile(r"create_card_frame\("), "CREATE_CARD"),
    (re.compile(r"get_color\("), "GET_COLOR"),
    (re.compile(r"get_typography\("), "GET_TYPO"),
    (re.compile(r"grid\("), "GRID"),
    (re.compile(r"pack\("), "PACK"),
    (re.compile(r"place\("), "PLACE"),
    (re.compile(r"bind\("), "BIND"),
    (re.compile(r"configure\("), "CONFIGURE"),
    (re.compile(r"add_command"), "ADD_COMMAND"),
]

NORMALIZATION_SUBS = [
    (re.compile(r"self\.get_color\([^)]*\)"), "GET_COLOR"),
    (re.compile(r"self\.get_typography\([^)]*\)"), "GET_TYPO"),
    (re.compile(r"self\.get_spacing\([^)]*\)"), "GET_SPACE"),
    (re.compile(r"self\.logger\.[a-z_]+\([^)]*\)"), "LOG_CALL"),
    (re.compile(r"self\.show_toast\([^)]*\)"), "TOAST"),
]

COMMENT_RE = re.compile(r"^\s*#")
DEF_SIG_RE = re.compile(r"^\s*def\s+(_create_[a-zA-Z0-9_]+)\s*\(")

@dataclass
class MethodInfo:
    name: str
    signature: str
    raw_body: str
    norm_body: str
    structure_tokens: List[str]
    loc: int

@dataclass
class SimilarityPair:
    method_a: str
    method_b: str
    seq_ratio: float
    structural_ratio: float
    combined: float
    loc_a: int
    loc_b: int

# ---------------- Extraction ----------------

def extract_create_methods(path: Path) -> List[MethodInfo]:
    if not path.exists():
        raise FileNotFoundError(f"Zieldatei nicht gefunden: {path}")
    content = path.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()

    # Finden des Klassenblocks
    class_start = None
    for i, line in enumerate(lines):
        if line.startswith(f"class {CLASS_NAME}"):
            class_start = i
            break
    if class_start is None:
        raise RuntimeError(f"Klasse {CLASS_NAME} nicht gefunden")

    methods: List[MethodInfo] = []
    i = class_start + 1
    total_lines = len(lines)
    while i < total_lines:
        line = lines[i]
        # Signatur einer _create_ Methode auf Klassen-Ebene (Indent 4 Spaces)
        if line.startswith("    def _create_") and line.strip().endswith(":"):
            sig_line = line
            name_match = re.match(r"\s*def\s+(_create_[a-zA-Z0-9_]+)\(", line)
            if not name_match:
                i += 1
                continue
            name = name_match.group(1)
            # Körper sammeln bis nächste def mit gleicher Einrückung oder Klassenende
            body_lines: List[str] = []
            j = i + 1
            while j < total_lines:
                next_line = lines[j]
                if next_line.startswith("    def ") and not next_line.startswith("        "):
                    break  # nächste Methode gleicher Ebene
                if next_line.startswith("class "):
                    break
                body_lines.append(next_line)
                j += 1
            raw_body = "\n".join(body_lines)
            norm_body = normalize_body(raw_body)
            structure_tokens = extract_structure_tokens(norm_body)
            loc = sum(1 for l in raw_body.splitlines() if l.strip())
            methods.append(MethodInfo(name=name, signature=sig_line.strip(), raw_body=raw_body, norm_body=norm_body, structure_tokens=structure_tokens, loc=loc))
            i = j
            continue
        i += 1
    return methods

# ---------------- Normalization ----------------

def normalize_body(body: str) -> str:
    cleaned: List[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if COMMENT_RE.match(stripped):
            continue
        if 'logger.' in stripped or 'show_toast(' in stripped:
            continue
        # generische Platzhalter für Farb-/Font-/Spacing-/Pfad-Konstanten
        line2 = stripped
        for pattern, repl in NORMALIZATION_SUBS:
            line2 = pattern.sub(repl, line2)
        # Entferne numerische Literale (Grids, Größen)
        line2 = re.sub(r"\b\d+\b", "N", line2)
        # Entferne Hex-Farben (sollten ohnehin Design System sein) – falls noch vorhanden
        line2 = re.sub(r"#[0-9A-Fa-f]{6}", "HEX", line2)
        cleaned.append(line2)
    return "\n".join(cleaned)

# ---------------- Structural Tokens ----------------

def extract_structure_tokens(norm_body: str) -> List[str]:
    tokens: List[str] = []
    for line in norm_body.splitlines():
        for regex, token in STRUCTURE_TOKEN_REGEX:
            if regex.search(line):
                tokens.append(token)
    return tokens or ["NO_STRUCT"]

# ---------------- Similarity Calculation ----------------

def seq_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a.splitlines(), b.splitlines()).ratio()

def structural_similarity(toks_a: List[str], toks_b: List[str]) -> float:
    if not toks_a or not toks_b:
        return 0.0
    set_a = set(toks_a)
    set_b = set(toks_b)
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0

# ---------------- Clustering (Union-Find) ----------------
class UnionFind:
    def __init__(self, items: List[str]):
        self.parent = {x: x for x in items}
    def find(self, x: str) -> str:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x
    def union(self, a: str, b: str):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra
    def groups(self) -> Dict[str, List[str]]:
        out: Dict[str, List[str]] = {}
        for k in self.parent:
            r = self.find(k)
            out.setdefault(r, []).append(k)
        return out

# ---------------- Main Analysis ----------------

def analyze(threshold: float = 0.72) -> Dict[str, Any]:
    methods = extract_create_methods(TARGET_FILE)
    name_to_method = {m.name: m for m in methods}
    pairs: List[SimilarityPair] = []
    for i, m1 in enumerate(methods):
        for m2 in methods[i+1:]:
            seq_r = seq_similarity(m1.norm_body, m2.norm_body)
            struct_r = structural_similarity(m1.structure_tokens, m2.structure_tokens)
            combined = round(0.6 * seq_r + 0.4 * struct_r, 4)
            if combined < 0.15:
                continue  # ignoriere komplett abweichende
            pairs.append(SimilarityPair(method_a=m1.name, method_b=m2.name, seq_ratio=round(seq_r,4), structural_ratio=round(struct_r,4), combined=combined, loc_a=m1.loc, loc_b=m2.loc))

    # Ranking
    pairs_sorted = sorted(pairs, key=lambda p: p.combined, reverse=True)

    # Clustering
    uf = UnionFind([m.name for m in methods])
    for p in pairs_sorted:
        if p.combined >= threshold:
            uf.union(p.method_a, p.method_b)
    clusters_raw = uf.groups()

    # Nur Cluster mit >=2 Methoden zeigen
    clusters = {root: members for root, members in clusters_raw.items() if len(members) >= 2}

    # Cluster-Stats
    cluster_stats = []
    for root, members in clusters.items():
        locs = [name_to_method[m].loc for m in members]
        total_loc = sum(locs)
        base_loc = min(locs) if locs else 0
        # naive Einsparungsschätzung: total - (base + overhead_per_adapter * (n-1))
        overhead_per_adapter = 6  # Annahme: dünne Wrapper delegieren
        potential_saving = total_loc - (base_loc + overhead_per_adapter * (len(members)-1))
        cluster_stats.append({
            'cluster_id': root,
            'members': members,
            'size': len(members),
            'total_loc': total_loc,
            'base_loc': base_loc,
            'potential_saving_loc': max(potential_saving, 0),
        })

    result = {
        'threshold': threshold,
        'methods_analyzed': len(methods),
        'pairs_considered': len(pairs),
        'pairs_above_threshold': sum(1 for p in pairs_sorted if p.combined >= threshold),
        'top_pairs': [asdict(p) for p in pairs_sorted[:25]],
        'clusters': cluster_stats,
        'methods': [{
            'name': m.name,
            'loc': m.loc,
            'structure_tokens': m.structure_tokens,
        } for m in methods],
    }
    return result

# ---------------- Reporting ----------------

def write_outputs(data: Dict[str, Any]):
    OUTPUT_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    # Markdown Report
    lines: List[str] = []
    lines.append("# UI CREATE* METHOD SIMILARITY REPORT")
    lines.append("")
    lines.append(f"**Threshold:** {data['threshold']}")
    lines.append(f"**Analysierte Methoden:** {data['methods_analyzed']}")
    lines.append(f"**Bewertete Paare:** {data['pairs_considered']}")
    lines.append(f"**Paare >= Threshold:** {data['pairs_above_threshold']}")
    lines.append("")
    lines.append("## Top 15 Paare (kombinierter Score)")
    lines.append("")
    for p in data['top_pairs'][:15]:
        lines.append(f"- {p['method_a']} ↔ {p['method_b']} | combined={p['combined']} (seq={p['seq_ratio']}, struct={p['structural_ratio']})")
    lines.append("")
    lines.append("## Cluster (Merge-Kandidaten)")
    lines.append("")
    if not data['clusters']:
        lines.append("(Keine Cluster ≥ 2 Methoden beim aktuellen Threshold)")
    else:
        for c in sorted(data['clusters'], key=lambda x: (-x['size'], -x['potential_saving_loc'])):
            lines.append(f"### Cluster {c['cluster_id']} – {c['size']} Methoden")
            lines.append(f"Mitglieder: {', '.join(c['members'])}")
            lines.append(f"LOC gesamt: {c['total_loc']} | Basis: {c['base_loc']} | Pot. Ersparnis (grobe Schätzung): {c['potential_saving_loc']}")
            lines.append("")
    lines.append("---")
    lines.append("*Automatisch generiert – rein analytisch, keine Codeänderungen.*")
    OUTPUT_REPORT.write_text("\n".join(lines), encoding='utf-8')

# ---------------- CLI ----------------

def main():  # pragma: no cover
    parser = argparse.ArgumentParser(description="Analyse Ähnlichkeit _create_* Methoden")
    parser.add_argument('--threshold', type=float, default=0.72, help='Cluster Threshold (default 0.72)')
    args = parser.parse_args()
    data = analyze(threshold=args.threshold)
    write_outputs(data)
    print(f"✅ Analyse abgeschlossen. JSON: {OUTPUT_JSON} | Report: {OUTPUT_REPORT}")
    # Kurzer Konsolen-Teaser
    if data['clusters']:
        print("📦 Cluster Übersicht:")
        for c in data['clusters']:
            print(f"  - {c['cluster_id']}: {c['size']} Methoden (pot. Saving {c['potential_saving_loc']} LOC)")
    else:
        print("ℹ️ Keine Cluster beim aktuellen Threshold – ggf. Threshold senken (z.B. --threshold 0.65)")

if __name__ == '__main__':  # pragma: no cover
    main()
