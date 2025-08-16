# Typography Governance Lock

Migration vollständig abgeschlossen am 2025-08-08.

Alle Legacy-Tokens werden jetzt HARD BLOCKED:

```text
micro_bold, caption_bold, metric_value, input,
heading_lg, heading_xl, title_lg, title_xl
```

Durchgesetzte Mechanismen:

- PowerShell Analyse (`typography-analysis.ps1`) → Exit 2 bei Fund
- CI Workflow Schritt (PowerShell Enforcement) → Build Fail
- Hard Block in `quality_gui_main_app.py::get_typography`
- Stylelint Regeln gegen direkte font-size/weight Angaben

Zero-Tolerance aktiv: Neue Verwendungen müssen Pull Requests blockieren.

Zur Einführung neuer Typographie-Stufen: Architektur-Review + Update aller Guardrails.
