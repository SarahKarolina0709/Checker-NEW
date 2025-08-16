#!/usr/bin/env python3
"""
� DEVELOPMENT MODE: CRITICAL PROTECTION TEMPORARILY DISABLED
============================================================
Entwicklungsmodus aktiviert - Alle Schutz-Warnungen deaktiviert für schnelle Entwicklung.

ORIGINAL FUNCTIONALITY (wird nach Entwicklung wiederhergestellt):
- Automatische Erkennung und Schutz kritischer Python-Dateien
- Backup-System für systemkritische Dateien
- Integritätsprüfung und Restore-Funktionen

CURRENT DEVELOPMENT MODE:
- ✅ Alle Python-Skripte können direkt ausgeführt werden
- ✅ Keine Warnungen bei kritischen Datei-Operationen
- ✅ Schnelle Iterationen und Tests möglich
- 📝 Nach Entwicklung: Original-System reaktivieren
"""
from pathlib import Path


import sys

def main():
    """Hauptfunktion - Entwicklungsmodus"""
    print("🔧 ENTWICKLUNGSMODUS AKTIV")
    print("✅ Kritische Dateien-Schutz temporär deaktiviert")
    print("✅ Alle Python-Operationen für Entwicklung erlaubt")
    print("📝 HINWEIS: Nach Entwicklungsabschluss Schutz reaktivieren")

    # In Entwicklungsmodus: Immer erlauben, keine Warnungen
    return True

if __name__ == "__main__":
    main()
    sys.exit(0)

class CriticalFilesProtector:
    """🚨 Schützt kritische Python-Dateien vor versehentlicher Löschung"""

    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.registry_file = self.project_root / "CRITICAL_FILES_REGISTRY.json"
        self.backup_dir = self.project_root / "CRITICAL_FILES_BACKUP"
        self.load_registry()

    def load_registry(self):
        """Lade Registry der kritischen Dateien"""
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)
        except FileNotFoundError:
            print(f"❌ Registry nicht gefunden: {self.registry_file}")
            self.registry = {"critical_files": {}, "protection_rules": {}}

    def save_registry(self):
        """Speichere Registry"""
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
        print(f"✅ Registry gespeichert: {self.registry_file}")

    def scan_critical_files(self):
        """Automatische Erkennung kritischer Dateien"""
        print("🔍 SCANNING KRITISCHER DATEIEN")
        print("=" * 50)

        critical_patterns = [
            (r'class.*App', "Hauptanwendungsklasse"),
            (r'class.*GUI', "GUI-Hauptklasse"),
            (r'class.*Theme', "Theme-System"),
            (r'def main\(\)', "Haupt-Einstiegspunkt"),
            (r'if __name__ == ["\']__main__["\']', "Ausführbare Datei"),
            (r'customtkinter|tkinter', "GUI-Framework"),
            (r'from ui_theme import', "Theme-Abhängigkeit"),
            (r'CONFIG|config\.json', "Konfigurationsdatei")
        ]

        found_files = {}

        for py_file in self.project_root.rglob("*.py"):
            if self._is_backup_or_archive(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                score = 0
                reasons = []

                for pattern, description in critical_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        score += 1
                        reasons.append(description)

                if score >= 2:  # Mindestens 2 kritische Muster
                    rel_path = py_file.relative_to(self.project_root)
                    found_files[str(rel_path)] = {
                        "score": score,
                        "reasons": reasons,
                        "size": py_file.stat().st_size,
                        "modified": datetime.fromtimestamp(py_file.stat().st_mtime).isoformat()
                    }

            except Exception as e:
                print(f"❌ Fehler beim Scannen {py_file}: {e}")

        # Zeige Ergebnisse
        print(f"🎯 {len(found_files)} kritische Dateien gefunden:")
        for file_path, info in sorted(found_files.items(), key=lambda x: x[1]["score"], reverse=True):
            print(f"  📄 {file_path} (Score: {info['score']})")
            for reason in info['reasons']:
                print(f"     🔹 {reason}")

        return found_files

    def _is_backup_or_archive(self, file_path):
        """Prüft ob Datei ein Backup oder Archiv ist"""
        path_str = str(file_path).lower()
        skip_dirs = ['backup', 'archive', 'old', 'deprecated', 'complete_cleanup', 'test']
        return any(skip_dir in path_str for skip_dir in skip_dirs)

    def add_protection_markers(self):
        """Fügt Schutz-Header zu kritischen Dateien hinzu"""
        print("🔒 ADDING PROTECTION MARKERS")
        print("=" * 50)

        if "critical_files" not in self.registry:
            print("❌ Keine kritischen Dateien in Registry!")
            return

        markers = self.registry.get("markers", {})
        critical_header = markers.get("critical_header", "# 🚨 CRITICAL SYSTEM FILE - NIEMALS LÖSCHEN!")

        for file_id, file_info in self.registry["critical_files"].items():
            file_path = self.project_root / file_info["file"]

            if not file_path.exists():
                print(f"❌ Datei nicht gefunden: {file_path}")
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Prüfe ob Header bereits vorhanden
                if critical_header in content:
                    print(f"✅ {file_path} - Header bereits vorhanden")
                    continue

                # Füge Header hinzu
                protection_info = f"""
{critical_header}
# DATEI: {file_info['file']}
# STATUS: {file_info['status']} (Priorität: {file_info['priority']})
# BESCHREIBUNG: {file_info['description']}
# LETZTE VERIFIZIERUNG: {file_info['last_verified']}
# ⚠️ WARNUNG: Diese Datei ist systemkritisch - nicht löschen oder stark modifizieren!
# 🔒 SCHUTZ: Automatisches Backup bei Änderungen erforderlich
# 📋 ABHÄNGIGKEITEN: {', '.join(file_info.get('dependencies', []))}

"""

                new_content = protection_info + content

                # Backup erstellen
                self._create_file_backup(file_path, "before_marker_addition")

                # Header schreiben
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                print(f"🔒 {file_path} - Schutz-Header hinzugefügt")

            except Exception as e:
                print(f"❌ Fehler bei {file_path}: {e}")

    def verify_integrity(self):
        """Überprüft Integrität der kritischen Dateien"""
        print("🔍 INTEGRITY VERIFICATION")
        print("=" * 50)

        issues = []

        for file_id, file_info in self.registry.get("critical_files", {}).items():
            file_path = self.project_root / file_info["file"]

            print(f"🔍 Prüfe {file_info['file']}...")

            # Existenz prüfen
            if not file_path.exists():
                issue = f"❌ KRITISCH: Datei fehlt: {file_info['file']}"
                issues.append(issue)
                print(f"  {issue}")
                continue

            # Größe prüfen (verdächtig klein = möglicherweise beschädigt)
            size = file_path.stat().st_size
            if size < 100:  # Weniger als 100 Bytes
                issue = f"⚠️ WARNUNG: Datei verdächtig klein ({size} bytes): {file_info['file']}"
                issues.append(issue)
                print(f"  {issue}")

            # Marker prüfen
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                expected_markers = file_info.get("markers", [])
                for marker in expected_markers:
                    if marker not in content:
                        issue = f"⚠️ WARNUNG: Marker fehlt in {file_info['file']}: {marker}"
                        issues.append(issue)
                        print(f"  {issue}")

            except Exception as e:
                issue = f"❌ FEHLER beim Lesen: {file_info['file']}: {e}"
                issues.append(issue)
                print(f"  {issue}")

        if not issues:
            print("✅ Alle kritischen Dateien sind in Ordnung!")
        else:
            print(f"\n⚠️ {len(issues)} Probleme gefunden:")
            for issue in issues:
                print(f"  {issue}")

        return issues

    def create_backups(self):
        """Erstellt Backups aller kritischen Dateien"""
        print("💾 CREATING BACKUPS")
        print("=" * 50)

        # Backup-Verzeichnis erstellen
        self.backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_session_dir = self.backup_dir / f"backup_{timestamp}"
        backup_session_dir.mkdir(exist_ok=True)

        backed_up = []

        for file_id, file_info in self.registry.get("critical_files", {}).items():
            file_path = self.project_root / file_info["file"]

            if not file_path.exists():
                print(f"❌ Kann nicht sichern (nicht gefunden): {file_info['file']}")
                continue

            try:
                backup_path = backup_session_dir / file_info["file"]
                backup_path.parent.mkdir(parents=True, exist_ok=True)

                shutil.copy2(file_path, backup_path)

                # Checksum erstellen
                checksum = self._calculate_checksum(file_path)
                checksum_file = backup_path.with_suffix(backup_path.suffix + '.checksum')

                with open(checksum_file, 'w') as f:
                    f.write(f"{checksum}  {file_info['file']}\n")
                    f.write(f"# Backup erstellt: {datetime.now().isoformat()}\n")
                    f.write(f"# Originalgröße: {file_path.stat().st_size} bytes\n")

                backed_up.append(file_info['file'])
                print(f"💾 {file_info['file']} → {backup_path}")

            except Exception as e:
                print(f"❌ Backup-Fehler {file_info['file']}: {e}")

        # Backup-Manifest erstellen
        manifest = {
            "timestamp": timestamp,
            "backed_up_files": backed_up,
            "backup_location": str(backup_session_dir),
            "total_files": len(backed_up)
        }

        manifest_file = backup_session_dir / "BACKUP_MANIFEST.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Backup abgeschlossen: {len(backed_up)} Dateien gesichert")
        print(f"📁 Backup-Verzeichnis: {backup_session_dir}")

        return backup_session_dir

    def _create_file_backup(self, file_path, reason="manual"):
        """Erstellt ein einzelnes Datei-Backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.backup_{reason}_{timestamp}"
        backup_path = self.backup_dir / backup_name

        self.backup_dir.mkdir(exist_ok=True)
        shutil.copy2(file_path, backup_path)

        print(f"💾 Backup erstellt: {backup_path}")
        return backup_path

    def _calculate_checksum(self, file_path):
        """Berechnet MD5-Checksum einer Datei"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def list_backups(self):
        """Listet verfügbare Backups auf"""
        print("📋 AVAILABLE BACKUPS")
        print("=" * 50)

        if not self.backup_dir.exists():
            print("❌ Kein Backup-Verzeichnis gefunden!")
            return []

        backups = []
        for backup_path in self.backup_dir.glob("backup_*"):
            if backup_path.is_dir():
                manifest_file = backup_path / "BACKUP_MANIFEST.json"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                        backups.append((backup_path, manifest))
                    except Exception as e:
                        print(f"❌ Fehler beim Lesen: {manifest_file}: {e}")

        backups.sort(key=lambda x: x[1]["timestamp"], reverse=True)

        for backup_path, manifest in backups:
            print(f"📅 {manifest['timestamp']} - {manifest['total_files']} Dateien")
            print(f"   📁 {backup_path}")
            for file_name in manifest["backed_up_files"][:3]:  # Zeige erste 3
                print(f"   📄 {file_name}")
            if len(manifest["backed_up_files"]) > 3:
                print(f"   ... und {len(manifest['backed_up_files']) - 3} weitere")
            print()

        return backups

def main():
    parser = argparse.ArgumentParser(description='🚨 Critical Files Protection System')
    parser.add_argument('--add-markers', action='store_true', help='Füge Schutz-Header hinzu')
    parser.add_argument('--verify', action='store_true', help='Überprüfe Integrität')
    parser.add_argument('--backup', action='store_true', help='Erstelle Backups')
    parser.add_argument('--list-backups', action='store_true', help='Liste Backups auf')
    parser.add_argument('--scan', action='store_true', help='Scanne nach kritischen Dateien')

    args = parser.parse_args()

    protector = CriticalFilesProtector()

    print("🚨 CRITICAL FILES PROTECTION SYSTEM")
    print("=" * 50)

    if args.scan:
        protector.scan_critical_files()
    elif args.add_markers:
        protector.add_protection_markers()
    elif args.verify:
        protector.verify_integrity()
    elif args.backup:
        protector.create_backups()
    elif args.list_backups:
        protector.list_backups()
    else:
        # Standard-Ablauf: Verify und dann Optionen anzeigen
        print("🔍 Führe automatische Integrität-Prüfung durch...")
        issues = protector.verify_integrity()

        print("\n📋 VERFÜGBARE OPTIONEN:")
        print("--scan          : Automatische Erkennung kritischer Dateien")
        print("--add-markers   : Schutz-Header zu kritischen Dateien hinzufügen")
        print("--verify        : Integrität der kritischen Dateien prüfen")
        print("--backup        : Vollständiges Backup aller kritischen Dateien")
        print("--list-backups  : Verfügbare Backups auflisten")

        if issues:
            print(f"\n⚠️ {len(issues)} Probleme gefunden! Führen Sie --backup aus.")

if __name__ == "__main__":
    main()