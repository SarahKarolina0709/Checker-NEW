# Quality GUI Prefix Vereinheitlichung

Alle relevanten Quality GUI Dateien erhalten jetzt den konsistenten Prefix:

```text
quality_gui_main_app.py
quality_gui_starter.py
quality_gui_diagnose.py (Alias für diagnose_quality_gui.py)
quality_gui_error_analysis.py (Alias für error_analysis.py)
quality_gui_comprehensive_diagnosis.py (Alias für comprehensive_diagnosis.py)
quality_gui_final_validation.py (Alias für final_validation.py)
```

Ziel:

- Bessere Gruppierung im Explorer
- Schnellere Auffindbarkeit
- Keine riskante Umbenennung kritischer Originaldateien (Backwards Compatibility)

Strategie:

- Neue Alias-Dateien mit Prefix, die alte Implementierungen importieren
- Alte Dateien bleiben bestehen (kein Bruch externer Referenzen)
- Schrittweise Migration möglich; nach Stabilität können Originale archiviert werden

Weiter möglich:

- quality_gui_tools.py (Sammel-Hilfsfunktionen)
- quality_gui_export.py (Export-spezifisch)

Anpassung welcome_screen: nutzt jetzt `quality_gui_starter.py`.
