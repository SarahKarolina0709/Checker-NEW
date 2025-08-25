#!/usr/bin/env python3
"""
Sichert alle .py-Dateien des Projekts unter backups/py_backup_<timestamp>/
- erhält die Ordnerstruktur
- erzeugt manifest.txt (relative Pfade) und manifest.json (mit SHA256)
- erstellt zusätzlich ein ZIP-Archiv
Nutzung: python tools/backup_all_py.py [wurzelpfad]
"""
from __future__ import annotations
import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    backup_root = root / 'backups'
    backup_root.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = backup_root / f'py_backup_{ts}'
    dest.mkdir(parents=True, exist_ok=True)

    # Alle .py-Dateien einsammeln, backups-Verzeichnis ausschließen
    files: list[Path] = []
    for p in root.rglob('*.py'):
        try:
            if 'backups' in p.parts:
                continue
            files.append(p)
        except Exception:
            continue

    # Kopieren mit Ordnerstruktur
    for src in files:
        rel = src.relative_to(root)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)

    # Manifeste schreiben
    manifest_txt = dest / 'manifest.txt'
    manifest_json = dest / 'manifest.json'

    rel_paths = [str(p.relative_to(root)).replace('\\', '/') for p in files]
    manifest_txt.write_text('\n'.join(rel_paths), encoding='utf-8')

    records = [{
        'path': str(p.relative_to(root)).replace('\\', '/'),
        'sha256': sha256_of(p),
    } for p in files]
    manifest_json.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')

    # ZIP erstellen
    zip_base = backup_root / f'py_backup_{ts}'
    if (zip_base.with_suffix('.zip')).exists():
        (zip_base.with_suffix('.zip')).unlink()
    shutil.make_archive(str(zip_base), 'zip', root_dir=str(dest), base_dir='.')

    # Ausgabe
    print(f"Backup-Ordner: {dest}")
    print(f"Backup-ZIP:    {zip_base.with_suffix('.zip')}")
    print(f"Dateien kopiert: {len(files)}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
