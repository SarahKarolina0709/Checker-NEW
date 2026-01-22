"""Gemeinsame Konstanten für Quality GUI Module.

Aus `quality_gui_main_app.py` extrahiert zur Reduktion der Dateigröße.
"""

CONTEXT_DEFAULT_MAP = {
    # Files
    "files.counter.update": "Dateizähler konnte nicht aktualisiert werden",
    "files.list.refresh": "Dateiliste Refresh Fehler",
    "files.list.content": "Dateiliste Inhalt konnte nicht aktualisiert werden",
    "files.item.create": "Dateielement konnte nicht erstellt werden",
    "files.item.remove": "Dateielement konnte nicht entfernt werden",
    "files.clear": "Dateien Leeren Fehler",
    # Upload
    "upload.translation": "Übersetzungsdateien Upload fehlgeschlagen",
    "upload.source": "Upload Source Files",
    "upload.batch": "Batch Upload",
    "upload.results.enhanced": "Erweiterte Upload Ergebnisse Fehler",
    # Pairing
    "pairing.results.display": "Pairing Ergebnisse Anzeige Fehler",
    "pairing.manual.dialog": "Manueller Pairing Dialog Fehler",
    "pairing.manual.interface": "Manuelle Pairing Oberfläche Fehler",
    "pairing.manual.populate": "Manuelle Pairing Befüllung Fehler",
}

__all__ = ["CONTEXT_DEFAULT_MAP"]
