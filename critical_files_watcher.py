
#!/usr/bin/env python3
"""
🚨 CRITICAL FILES WATCHER
========================
Überwacht kritische Dateien auf Änderungen und warnt vor ungeschützten Modifikationen.
"""


from pathlib import Path

class CriticalFilesWatcher:
    """Überwacht kritische Dateien auf gefährliche Änderungen"""

    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.registry_file = self.project_root / "CRITICAL_FILES_REGISTRY.json"
        self.checksums_file = self.project_root / "CRITICAL_FILES_CHECKSUMS.json"
        self.load_registry()
        self.load_checksums()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='🚨 Critical Files Watcher')
    parser.add_argument('--check', action='store_true', help='Überprüfe auf Änderungen')
    parser.add_argument('--update-checksums', action='store_true', help='Aktualisiere Checksums')
    parser.add_argument('--status', action='store_true', help='Zeige Schutzstatus')

    args = parser.parse_args()

    watcher = CriticalFilesWatcher()

    if args.update_checksums:
        watcher.update_checksums()
    elif args.status:
        watcher.show_protection_status()
    else:
        # Standard: Änderungen prüfen
        watcher.check_modifications()

if __name__ == "__main__":
    main()