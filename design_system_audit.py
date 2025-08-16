#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Design System Audit

Prüft Python-Dateien im Workspace auf Verstöße gegen das zentrale Design-System:
- Direkte Hex-Farben (#RRGGBB)
- Direkte CTkFont size= (statt get_typography()/get_font())
- Direkte Font-Tuples (font=(...))
- Direkte Padding-Werte (padx/pady/ipadx/ipady) ohne get_spacing()
- Direkte corner_radius Zahlen oder get_spacing() statt Tokens
- Dark Mode Nutzung
- Icon-Nutzung
- Emoji im UI-Text

Ausgabe: Konsolen-Zusammenfassung und JSON-Report (design_system_audit_report.json)
Exit-Code: 1 bei Verstößen (konfigurierbar via --fail-on=any|none)
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent

SKIP_DIRS = {".git", ".github", "__pycache__", ".venv", "venv", "env", ".vscode", "build", "dist", "node_modules"}
ALLOWLIST_FILES = {"design_system.py"}

# Aktiver Scope: Nur zentrale UI-Dateien prüfen (reduziert Rauschen)
ACTIVE_INCLUDE_DIRS = {"sections"}
ACTIVE_INCLUDE_FILES = {"welcome_screen.py", "ui_theme.py", "modern_translation_quality_gui.py"}

# Regex-Regeln
HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{6}")
CTKFONT_DIRECT_SIZE = re.compile(r"CTkFont\s*\([^)]*size\s*=\s*\d+", re.MULTILINE)
FONT_TUPLE_DIRECT = re.compile(r"\bfont\s*=\s*\(")
DIRECT_PADDING = re.compile(r"\b(i?padx|i?pady)\s*=\s*\d+")
DIRECT_CORNER_RADIUS_NUM = re.compile(r"corner_radius\s*=\s*\d+")
DIRECT_CORNER_RADIUS_SPACING = re.compile(r"corner_radius\s*=\s*[^\n]*get_spacing\(")
DARK_MODE = re.compile(r"set_appearance_mode\s*\(\s*['\"]dark['\"]|dark_image\s*=")
ICON_USAGE = re.compile(r"get_icon\(|icon_name\s*=")
# Emoji nur in UI-Textzuweisungen detektieren (nicht in Prints/Docstrings)
TEXT_PROP_EMOJI = re.compile(
    r"\b(text|placeholder_text)\s*=\s*([\'\"])"  # text= oder placeholder_text=
    r"(?:(?!\2).)*"                                   # Inhalt bis zum schließenden Quote
    r"[\u2600-\u27BF\U0001F300-\U0001FAFF]"        # Emoji-Codepoints
    r"(?:(?!\2).)*\2",
)

@dataclass
class Finding:
    file: str
    line: int
    rule: str
    text: str

def iter_python_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".py"):
                files.append(Path(dirpath) / fn)
    return files

def _is_in_active_scope(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if rel.name in ACTIVE_INCLUDE_FILES:
        return True
    return any(part in ACTIVE_INCLUDE_DIRS for part in rel.parts)


def scan_file(path: Path, scope: str = "active") -> List[Finding]:
    findings: List[Finding] = []
    fname = path.name
    allowlisted = fname in ALLOWLIST_FILES

    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    # Scope-Filter: im active-Scope nur ausgewählte Dateien/Ordner
    if scope != "all" and not _is_in_active_scope(path):
        return findings

    def add_matches(pattern: re.Pattern, rule: str):
        for m in pattern.finditer(content):
            line = content.count("\n", 0, m.start()) + 1
            findings.append(Finding(str(path), line, rule, content[m.start(): m.end()]))

    if not allowlisted:
        add_matches(HEX_COLOR, "HEX_COLOR_DIRECT")
        add_matches(CTKFONT_DIRECT_SIZE, "CTKFONT_DIRECT_SIZE")
        add_matches(FONT_TUPLE_DIRECT, "FONT_TUPLE_DIRECT")
        add_matches(DIRECT_PADDING, "DIRECT_PADDING")
        add_matches(DARK_MODE, "DARK_MODE_USAGE")
        add_matches(ICON_USAGE, "ICON_USAGE")
        # Emoji nur in UI-Text/Placeholder-Zuweisungen erfassen
        add_matches(TEXT_PROP_EMOJI, "EMOJI_IN_UI_TEXT")
        # corner_radius Checks
        add_matches(DIRECT_CORNER_RADIUS_NUM, "DIRECT_CORNER_RADIUS")
        add_matches(DIRECT_CORNER_RADIUS_SPACING, "DIRECT_CORNER_RADIUS_SPACING")

    return findings

def build_report(root: Path, scope: str = "active") -> Dict:
    all_findings: List[Finding] = []
    for p in iter_python_files(root):
        all_findings.extend(scan_file(p, scope=scope))

    summary: Dict[str, int] = {}
    for f in all_findings:
        summary[f.rule] = summary.get(f.rule, 0) + 1

    return {
        "summary": summary,
        "findings": [f.__dict__ for f in all_findings],
    }

def main(argv: List[str]) -> int:
    fail_on = "error"  # error|any|none
    scope = "active"   # active|all
    if "--fail-on=any" in argv:
        fail_on = "any"
    elif "--fail-on=none" in argv:
        fail_on = "none"
    if "--scope=all" in argv:
        scope = "all"
    elif "--scope=active" in argv:
        scope = "active"

    report = build_report(ROOT, scope=scope)
    # Save JSON
    try:
        (ROOT / "design_system_audit_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("Audit-Report gespeichert: design_system_audit_report.json")
    except Exception as e:
        print(f"Report-Schreiben fehlgeschlagen: {e}")

    # Console summary
    summary = report.get("summary", {})
    if not summary:
        print("Keine Verstöße gefunden.")
    else:
        print("===== Design System Audit Zusammenfassung =====")
        for rule, cnt in sorted(summary.items(), key=lambda x: x[0]):
            print(f"{rule}: {cnt}")
        # Top 10 Findings
        findings = report.get("findings", [])
        print("\nTop 10 Fundstellen:")
        for f in findings[:10]:
            print(f"- {f['file']}:{f['line']} [{f['rule']}] -> {f['text']}")

    # exit code
    error_rules = {
        "HEX_COLOR_DIRECT",
        "CTKFONT_DIRECT_SIZE",
        "FONT_TUPLE_DIRECT",
        "DIRECT_CORNER_RADIUS",
        "DIRECT_CORNER_RADIUS_SPACING",
        "DARK_MODE_USAGE",
        "ICON_USAGE",
        "EMOJI_IN_UI_TEXT",
    }
    warning_rules = {"DIRECT_PADDING"}

    errors = sum(summary.get(r, 0) for r in error_rules)
    warnings = sum(summary.get(r, 0) for r in warning_rules)

    if fail_on == "any" and (errors or warnings):
        return 1
    if fail_on == "error" and errors:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
