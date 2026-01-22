#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 Typography Unification – Pro/CLI
- Rekursiv über Ordner oder einzelne Datei
- Robuste Regex (unterstützt " und ' sowie Leerzeichen)
- Dry-Run, Backup, Undo
- Atomisches Schreiben und Statistik

Nutzung Beispiele:
  python unify_typography_pro.py                      # Standarddatei quality_gui_main_app.py
  python unify_typography_pro.py path/to/file.py      # Einzelne Datei
  python unify_typography_pro.py src/ -r              # Ordner rekursiv
  python unify_typography_pro.py quality_gui_main_app.py --dry-run
  python unify_typography_pro.py quality_gui_main_app.py --undo
"""
from __future__ import annotations
import argparse
import sys
import re
from pathlib import Path
import shutil
import uuid

# --- Mapping: von -> nach (logische Namen) ----------------------------------
# Wir matchen: get_typography(<quote>old</quote>) mit optionalen Spaces.

def pat(name: str) -> re.Pattern:
    return re.compile(rf"get_typography\(\s*(['\"]){re.escape(name)}\1\s*\)")

REPLACEMENTS: list[tuple[re.Pattern, str]] = [
    # Buttons
    (pat("button_lg"),        "get_typography('body_bold')"),
    (pat("button_md"),        "get_typography('body_bold')"),
    (pat("button"),           "get_typography('body_bold')"),
    # Headings
    (pat("heading_lg"),       "get_typography('heading')"),
    (pat("heading_md"),       "get_typography('subheading')"),
    (pat("heading_sm"),       "get_typography('subheading')"),
    # Body
    (pat("body_sm"),          "get_typography('body')"),
    (pat("body_lg"),          "get_typography('body_bold')"),
    # Labels
    (pat("label_bold"),       "get_typography('body_bold')"),
    (pat("label"),            "get_typography('body')"),
    # Cards
    (pat("card_header"),      "get_typography('subheading')"),
    # Kleine Texte
    (pat("small_normal"),     "get_typography('caption')"),
    (pat("small"),            "get_typography('caption')"),
    (pat("menu"),             "get_typography('caption')"),
    # Große Texte
    (pat("page_title"),       "get_typography('title')"),
    (pat("section"),          "get_typography('heading')"),
    (pat("hero"),             "get_typography('title')"),
    (pat("display"),          "get_typography('title')"),
]

FINAL_HIERARCHY = [
    "caption (12px) – kleine Labels, Menü",
    "body (14px) – Standard-Text, Inputs",
    "body_bold (14px) – Buttons, wichtige Labels",
    "subheading (18px) – Card Headers, Sections",
    "heading (22px) – Hauptüberschriften",
    "title (26px) – Page Titles, Hero Text",
]

# --- Core --------------------------------------------------------------------

def backup_file(path: Path, suffix: str) -> Path:
    candidate = path.with_name(path.name + suffix)
    if candidate.exists():
        candidate = path.with_name(f"{path.name}{suffix}.{uuid.uuid4().hex[:8]}")
    shutil.copy2(path, candidate)
    return candidate

def restore_backup(path: Path, suffix: str) -> bool:
    backup = path.with_name(path.name + suffix)
    if backup.exists():
        shutil.copy2(backup, path)
        return True
    return False

def process_text(content: str) -> tuple[str, int, dict[str, int]]:
    total = 0
    per_pattern: dict[str, int] = {}
    new = content
    for rx, repl in REPLACEMENTS:
        new, n = rx.subn(repl, new)
        if n:
            total += n
            per_pattern[rx.pattern] = n
    return new, total, per_pattern

def process_file(path: Path, *, dry_run: bool, backup_suffix: str, no_backup: bool) -> int:
    try:
        old = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ Kann Datei nicht lesen: {path} ({e})")
        return 0
    new, total, per_pattern = process_text(old)
    if total == 0:
        return 0
    print(f"✏️  {path} – Änderungen: {total}")
    for patt, n in per_pattern.items():
        print(f"   • {n}× {patt}")
    if dry_run:
        return total
    if not no_backup:
        backup_path = backup_file(path, backup_suffix)
        print(f"   ↳ Backup: {backup_path.name}")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(new, encoding="utf-8")
    tmp.replace(path)
    return total

def iter_targets(target: Path, exts: set[str], recursive: bool):
    if target.is_file():
        yield target
    else:
        if recursive:
            yield from (p for p in target.rglob("*.py") if p.suffix in exts)
        else:
            yield from (p for p in target.glob("*.py") if p.suffix in exts)

# --- CLI ---------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Vereinheitlicht get_typography(...) Aufrufe in Python-Dateien."
    )
    ap.add_argument("path", nargs="?", default="quality_gui_main_app.py",
                    help="Datei oder Ordner (Default: quality_gui_main_app.py)")
    ap.add_argument("-r", "--recursive", action="store_true",
                    help="Ordner rekursiv verarbeiten")
    ap.add_argument("--dry-run", action="store_true",
                    help="Nur anzeigen, nichts schreiben")
    ap.add_argument("--no-backup", action="store_true",
                    help="Kein Backup anlegen")
    ap.add_argument("--backup-suffix", default=".backup_typography",
                    help="Backup-Suffix (Default: .backup_typography)")
    ap.add_argument("--undo", action="store_true",
                    help="Backups mit gegebenem Suffix zurückspielen")
    args = ap.parse_args(argv)

    target = Path(args.path)
    if not target.exists():
        print(f"❌ Pfad nicht gefunden: {target}")
        return 2

    if args.undo:
        if target.is_file():
            ok = restore_backup(target, args.backup_suffix)
            print("✅ Wiederhergestellt" if ok else "❌ Kein Backup gefunden")
            return 0 if ok else 1
        else:
            print("ℹ️ Undo erwartet eine Datei, nicht einen Ordner.")
            return 2

    exts = {".py"}
    total_changes = 0
    files_seen = 0

    for p in iter_targets(target, exts, args.recursive):
        files_seen += 1
        total_changes += process_file(
            p,
            dry_run=args.dry_run,
            backup_suffix=args.backup_suffix,
            no_backup=args.no_backup,
        )

    print("\n📊 Zusammenfassung")
    print(f"   Dateien geprüft:   {files_seen}")
    print(f"   Änderungen gesamt: {total_changes}")
    print("\n📋 Finale Typography-Hierarchie:")
    for line in FINAL_HIERARCHY:
        print(f"   • {line}")

    return 0 if total_changes > 0 or args.dry_run else 1

if __name__ == "__main__":
    sys.exit(main())
