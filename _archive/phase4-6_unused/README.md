# Archivierte Phase 4-6 Module

**Archiviert am:** 2026-01-22

## Warum archiviert?

Diese Module wurden nie in die Hauptanwendung integriert:
- Die Flags `phase4_enabled`, `phase5_enabled`, `phase6_enabled` existierten zwar
- Aber es gab **keine Imports** und **keine Funktionsaufrufe** in `quality_gui_main_app.py`

## Was machen diese Module?

| Datei | Funktion | Status |
|-------|----------|--------|
| `quality_gui_phase4_checkers.py` | Issue-Konsolidierung, Deduplikation, Quick-Fix Hints | ✅ Inline in Pipeline implementiert |
| `quality_gui_phase5_enforcer.py` | Auto-Fix (Whitespace, Interpunktion, Quotes) | ❌ Nie integriert |
| `quality_gui_phase6_suggestions.py` | Priorisierte Verbesserungsvorschläge | ✅ Einfache `recommendations[]` inline |
| `qa_phase4_checkers.py` | Duplikat von Phase 4 | ❌ Nie benutzt |
| `phase5_enforcer.py` | Ältere Version von Phase 5 (DEPRECATED) | ❌ Nie benutzt |

## Test-Dateien

- `test_phase4_ux.py` - Tests für Phase 4
- `test_quality_gui_phase6_suggestions.py` - Tests für Phase 6

## Wiederherstellung

Falls diese Module später benötigt werden:
```powershell
Move-Item -Path ".\_archive\phase4-6_unused\*.py" -Destination ".\"
```

Dann die Flags wieder hinzufügen und die Module importieren/aufrufen.
