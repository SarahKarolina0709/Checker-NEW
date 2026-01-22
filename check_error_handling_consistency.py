"""Governance Guard: Prüft zentrale Error-Handling Konsistenz & Namespace-Policy.

Checks (Policy v2):
1. Direkte logger.error / self.logger.error Aufrufe in `quality_gui_main_app.py` (ausgenommen innerhalb _handle_error)
2. Alle gefundenen _handle_error Kontexte existieren im `error_context_inventory.json`
3. Namespace-Policy: Keine neuen Top-Level Namespaces ohne Freigabe
     (Top-Level = Präfix vor erstem Punkt, z.B. "files", "upload").

Exit Codes:
 0 = OK
 1 = Allgemeiner Lauf- / IO-Fehler
 2 = Inventory Drift (fehlende / entfernte Kontexte) – auto-update (falls kein Namespace-Verstoß)
 3 = Direkter logger.error Verstoß
 4 = Neuer Namespace erkannt (KEIN auto-update der Inventory-Datei, manuelle Freigabe nötig)

Namespace-Freigabe Workflow:
 - Wenn Exit Code 4 auftritt: Prüfen ob neuer Namespace legitim ist.
 - Bei Freigabe: Inventory neu generieren (generate_error_context_inventory.py) und Commit durchführen.
 - Alternativ: Kontext umbenennen auf bestehenden Namespace.

Nutzung:
    python check_error_handling_consistency.py
"""
from __future__ import annotations
import json, re, sys, pathlib

MAIN_FILE = pathlib.Path("quality_gui_main_app.py")
INVENTORY_FILE = pathlib.Path("error_context_inventory.json")

RE_LOGGER_ERROR = re.compile(r"(^|[^A-Za-z0-9_])(self\.)?logger\.error\s*\(")
RE_HANDLE_CALL = re.compile(r"_handle_error\s*\(.*?context\s*=\s*['\"]([^'\"]+)['\"]", re.DOTALL)


def load_file(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def get_handle_contexts(text: str) -> set[str]:
    return {m.group(1).strip() for m in RE_HANDLE_CALL.finditer(text) if m.group(1).strip()}


def find_direct_logger_errors(text: str) -> list[tuple[int,str]]:
    lines = text.splitlines()
    # Grob den Bereich der _handle_error Funktion bestimmen und exkludieren
    in_handler = False
    handler_indent = None
    violations = []
    for idx, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("def _handle_error"):
            in_handler = True
            handler_indent = len(line) - len(stripped)
        elif in_handler:
            # Ende sobald Zeile mit geringerer Einrückung (oder Funktionsdef) auftritt
            if (stripped.startswith("def ") or stripped.startswith("class ")) and (len(line)-len(stripped) <= handler_indent):
                in_handler = False
        if RE_LOGGER_ERROR.search(line):
            if not in_handler:  # nur außerhalb _handle_error relevant
                violations.append((idx, line.strip()))
    return violations


def main() -> int:
    if not MAIN_FILE.exists():
        print("Main file nicht gefunden", file=sys.stderr)
        return 1
    text = load_file(MAIN_FILE)

    # 1. Direkte logger.error Verstöße
    violations = find_direct_logger_errors(text)

    # 2. Inventory Vergleich
    current_contexts = get_handle_contexts(text)
    current_namespaces = {c.split('.', 1)[0] for c in current_contexts if c}
    inventory_contexts: set[str] = set()
    inventory_namespaces: set[str] = set()
    drift_missing: set[str] = set()
    drift_removed: set[str] = set()
    if INVENTORY_FILE.exists():
        try:
            data = json.loads(INVENTORY_FILE.read_text(encoding="utf-8"))
            inventory_contexts = set(data.get("all_contexts", []))
            # Namespaces aus Keys falls vorhanden (neues Format) sonst aus contexts ableiten
            if "namespaces" in data and isinstance(data["namespaces"], dict):
                inventory_namespaces = set(data["namespaces"].keys())
            else:
                inventory_namespaces = {c.split('.', 1)[0] for c in inventory_contexts if c}
            drift_missing = current_contexts - inventory_contexts
            drift_removed = inventory_contexts - current_contexts
        except Exception as e:
            print(f"Warnung: Inventory konnte nicht gelesen werden: {e}")

    exit_code = 0

    if violations:
        print("DIRECT LOG ERROR VERSTOESSE:")
        for line_no, content in violations:
            print(f"  Zeile {line_no}: {content}")
        exit_code = 3

    # 3) Namespace Policy Prüfung (neue Namespaces ohne Freigabe blockieren)
    new_namespaces = current_namespaces - inventory_namespaces if inventory_namespaces else set()

    if new_namespaces:
        print("NEUER NAMESPACE VERSTOSS:")
        for ns in sorted(new_namespaces):
            print(f"  + {ns}")
        print("Bitte pruefen und manuell freigeben (generate_error_context_inventory.py ausfuehren, Commit).")
        if exit_code == 0:
            exit_code = 4  # Vorrang vor Drift-Autoupdate

    # 4) Inventory Drift (nur falls kein Namespace-Verstoß)
    if exit_code != 4 and (drift_missing or drift_removed):
        print("INVENTORY DRIFT erkannt:")
        if drift_missing:
            print("  Neue Kontexte (im Code, nicht im Inventory):")
            for c in sorted(drift_missing):
                print(f"    + {c}")
        if drift_removed:
            print("  Veraltete Kontexte (im Inventory, nicht mehr im Code):")
            for c in sorted(drift_removed):
                print(f"    - {c}")
        # Auto-Update nur wenn keine Namespace Policy verletzt wurde
        updated = {
            "total_contexts": len(current_contexts),
            "all_contexts": sorted(current_contexts),
            # Fuege Namespaces hinzu fuer spaetere Policy Vergleiche
            "namespaces": {ns: [] for ns in sorted(current_namespaces)}
        }
        INVENTORY_FILE.write_text(json.dumps(updated, indent=2, ensure_ascii=False), encoding="utf-8")
        print("Inventory auto-updated (inkl. Namespaces).")
        if exit_code == 0:
            exit_code = 2

    if exit_code == 0:
        print("OK: Error-Handling Konsistenz - keine Verstoesse, kein Drift.")
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
