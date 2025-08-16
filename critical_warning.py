#!/usr/bin/env python3
"""
🚨 PRE-EDIT CRITICAL FILES WARNING SYSTEM
=========================================
Automatische Warnung vor dem Bearbeiten kritischer Dateien.
Integrierbar in IDEs und Editoren.
"""

from pathlib import Path
import json
import os
import sys

def check_if_critical_file(file_path):
    """Prüft ob eine Datei kritisch ist und zeigt Warnung"""

    # Normalisiere Pfad
    file_path = Path(file_path).resolve()
    project_root = file_path.parent

    # Suche nach Registry
    registry_file = None
    current_dir = file_path.parent
    for _ in range(10):  # Maximal 10 Ebenen nach oben suchen
        test_registry = current_dir / "CRITICAL_FILES_REGISTRY.json"
        if test_registry.exists():
            registry_file = test_registry
            project_root = current_dir
            break
        current_dir = current_dir.parent
        if current_dir == current_dir.parent:  # Root erreicht
            break

    if not registry_file:
        return False  # Keine Registry gefunden

    # Lade Registry
    try:
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    except Exception as e:
        print(f"❌ Fehler beim Laden der Registry: {e}")
        return False

    # Prüfe ob Datei kritisch ist
    relative_path = file_path.relative_to(project_root)
    file_name = file_path.name

    critical_file_info = None

    # Suche in Registry
    for file_id, file_info in registry.get("critical_files", {}).items():
        registry_path = Path(file_info["file"])

        # Exakter Pfad-Vergleich oder Dateiname-Vergleich
        if (str(relative_path) == file_info["file"] or
            str(relative_path).replace("\\", "/") == file_info["file"] or
            file_name == registry_path.name):
            critical_file_info = file_info
            break

    if not critical_file_info:
        return False  # Nicht kritisch

    # ⚠️ KRITISCHE DATEI ERKANNT - WARNUNG ANZEIGEN!
    print("\n" + "🚨" * 50)
    print("🚨 WARNUNG: KRITISCHE DATEI ERKANNT!")
    print("🚨" * 50)
    print()
    print(f"📁 DATEI: {file_path}")
    print(f"🎯 STATUS: {critical_file_info['status']} (Priorität: {critical_file_info['priority']})")
    print(f"📝 BESCHREIBUNG: {critical_file_info['description']}")

    if critical_file_info.get("dependencies"):
        print(f"📦 ABHÄNGIGKEITEN: {', '.join(critical_file_info['dependencies'])}")

    print()
    print("⚠️ DIESE DATEI IST SYSTEMKRITISCH!")
    print("⚠️ ÄNDERUNGEN KÖNNEN DAS SYSTEM BESCHÄDIGEN!")
    print()
    print("🛡️ EMPFOHLENE SCHRITTE VOR BEARBEITUNG:")
    print("   1. 💾 python protect_critical_files.py --backup")
    print("   2. 🔍 python protect_critical_files.py --verify")
    print("   3. ⚡ Änderungen vorsichtig durchführen")
    print("   4. ✅ python protect_critical_files.py --verify (nach Änderung)")
    print()
    print("🔒 BACKUP-VERZEICHNIS: CRITICAL_FILES_BACKUP/")
    print()

    # Interaktive Bestätigung
    priority_messages = {
        1: "🚨 PRIORITÄT 1 - SYSTEM FUNKTIONIERT NICHT OHNE DIESE DATEI!",
        2: "⚠️ PRIORITÄT 2 - WICHTIGE FUNKTIONALITÄT BETROFFEN!",
        3: "📝 PRIORITÄT 3 - NÜTZLICHE FEATURES BETROFFEN!"
    }

    priority = critical_file_info.get("priority", 3)
    print(priority_messages.get(priority, "📝 UNBEKANNTE PRIORITÄT"))
    print()

    # Frage nach Bestätigung
    while True:
        response = input("Möchten Sie trotzdem fortfahren? (j/n/backup): ").lower().strip()

        if response in ['j', 'ja', 'y', 'yes']:
            print("✅ Fortfahren bestätigt. VORSICHTIG BEARBEITEN!")
            print("💡 Tipp: Erstellen Sie häufige Zwischenspeicherungen!")
            return True

        elif response in ['n', 'nein', 'no']:
            print("🛑 Bearbeitung abgebrochen. Datei bleibt unverändert.")
            return False

        elif response in ['backup', 'b']:
            print("💾 Starte Backup-Prozess...")
            try:
                import subprocess
                result = subprocess.run([sys.executable, "protect_critical_files.py", "--backup"],
                                     capture_output=True, text=True, cwd=project_root)
                if result.returncode == 0:
                    print("✅ Backup erfolgreich erstellt!")
                    print("✨ Sie können jetzt sicher fortfahren.")
                    return True
                else:
                    print(f"❌ Backup-Fehler: {result.stderr}")
                    print("⚠️ Bearbeitung auf eigenes Risiko!")
                    return True
            except Exception as e:
                print(f"❌ Backup-Prozess fehlgeschlagen: {e}")
                print("⚠️ Bearbeitung auf eigenes Risiko!")
                return True
        else:
            print("❌ Ungültige Eingabe. Bitte 'j' (ja), 'n' (nein) oder 'backup' eingeben.")

def main():
    """Hauptfunktion für Command Line Interface"""

    if len(sys.argv) < 2:
        print("🚨 CRITICAL FILES WARNING SYSTEM")
        print("=" * 40)
        print("VERWENDUNG:")
        print("  python critical_warning.py <DATEI_PFAD>")
        print()
        print("BEISPIELE:")
        print("  python critical_warning.py modern_translation_quality_gui.py")
        print("  python critical_warning.py ui_theme.py")
        print()
        print("INTEGRATION IN IDE:")
        print("  VS Code: Pre-edit hook")
        print("  PyCharm: External tool")
        print("  Git: Pre-commit hook")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"❌ Datei nicht gefunden: {file_path}")
        sys.exit(1)

    is_critical = check_if_critical_file(file_path)

    if is_critical:
        print("🔒 Kritische Datei wurde zur Bearbeitung freigegeben.")
        sys.exit(0)  # OK zu bearbeiten
    else:
        print(f"✅ {file_path} - Nicht kritisch, sicher zu bearbeiten.")
        sys.exit(0)

if __name__ == "__main__":
    main()