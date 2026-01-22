# Reporting Optionen

Dieses Dokument beschreibt die zentralen Reporting-Einstellungen und das optionale Korrekturpaket.

## Einstellungen

- reporting.output_dir (String, Default: "exports")
  - Ausgabeordner für zentrale Exporte.
- reporting.filename_prefix (String, Default: "analysis")
  - Präfix für exportierte Dateien.
- reporting.formats (Array[String], Werte: pdf|xlsx|txt)
  - Liste der zu erzeugenden Formate im zentralen Reporting-Flow.
- reporting.naming_pattern (String, Default: "report_{ts}")
  - Muster für Dateinamen. Platzhalter: {ts} (Zeitstempel), {fmt} (Format).
- reporting.include_charts (Bool, Default: true)
  - Steuert Diagrammeinbettungen in PDF (sofern unterstützt).
- reporting.auto_open (Bool, Default: false)
  - Öffnet erzeugte Dateien/Ordner nach Export automatisch.
- reporting.create_correction_package (Bool, Default: false)
  - Wenn true, erzeugt der zentrale Reporting-Flow zusätzlich ein Korrekturpaket.

## Korrekturpaket

Wird `reporting.create_correction_package` aktiviert, erstellt der zentrale Reporting-Flow nach dem üblichen Export einen Ordner `<basename>_korrekturpaket` mit:

- findings.txt (Kurzliste)
- findings.json (Detaildaten)
- findings.csv (ungrouped, inkl. Confidence)
- findings_bilingual.csv (optional – wenn segment_id/source/target vorhanden)
- findings_grouped.csv (aggregiert, Header: rule_id)
- findings_grouped.html (aggregiert, zeigt bei vorhandenen Metriken die verwendeten Ähnlichkeitsschwellen)
- README.txt (Kurzer Überblick, inkl. genutzter Schwellen, wenn verfügbar)
- meta.json (Metadaten inkl. similarity_thresholds_used)

Hinweise:
- Die CSV-Header sind konsistent, in gruppierten Dateien wird `rule_id` bevorzugt verwendet (Fallback auf `rule` beim Wert).
- Wenn `reporting.auto_open` aktiv ist, wird der Ordner nach Erstellung automatisch geöffnet.

## UI-Integration

- Export-Dialog: Checkbox "Korrekturpaket erstellen" (sofort persistiert)
- Einstellungen → Reporting: Checkbox "Korrekturpaket zusätzlich erstellen" wird mitgespeichert

## Troubleshooting

- Wird kein Korrekturpaket erstellt? Prüfe, ob `reporting.create_correction_package` = true.
- Leere oder fehlende Befunde: Das Paket enthält nur vorhandene Daten. Stelle sicher, dass `analysis_results` Befunde liefert.
- Gruppierte Dateien fehlen: Nur vorhanden, wenn `findings_grouped` in den Analyse-Ergebnissen enthalten ist.
