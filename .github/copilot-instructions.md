# Copilot instructions for this repo

Purpose: Translation quality checker for professional translators. Web-app built with NiceGUI (Python).

## Big picture
- Web-app built on NiceGUI (Python 3.12), runs on localhost, accessible in browser.
- Main app in `nicegui_app/main.py` (~1.600 lines) — all UI in one file.
- Backend: 12 Python modules for analysis (Phase 1-4), pairing, upload, OCR, glossary.
- Config: `config.json`, `checker_config.json` (user-editable).
- 62 unit tests in `tests/test_quality_gui_phase*.py`.

## Entry points
- `python nicegui_app/main.py` — Start app (opens browser at http://localhost:8111)
- `python -m pytest tests/ -q` — Run tests

## Architecture
Simple, no Mixins, no classes — just functions + module-level state.

### App (nicegui_app/main.py)
- Upload: Source + Translation files (PDF, DOCX, TXT, images with OCR)
- Auto-Pairing via `QualityGuiPairingManager`
- Analysis: Phase 1 (numbers/formats), Phase 2 (terminology/names), Phase 3 (grammar/style), Phase 4 (Ollama KI)
- Results: Score (0-100), severity filter, search, findings with source/target preview
- Export: TXT, PDF, Excel, correction package (ZIP)
- Customer management + project structure
- Calendar view at `/kalender`
- Session save/restore

### Backend modules (root directory)
- `quality_gui_phase1_checkers.py` — Numbers, URLs, brackets, quotes
- `quality_gui_phase2_checkers.py` — Company names, glossary, terminology, HTML
- `quality_gui_phase3_checkers.py` — Grammar, readability, style, passive voice
- `quality_gui_phase4_ki_checker.py` — Ollama KI semantic checks
- `quality_gui_grammar.py` — LanguageTool + heuristic grammar backend
- `quality_gui_consistency_checker.py` — Cross-segment terminology consistency
- `quality_gui_ocr_checker.py` — OCR-specific error detection
- `quality_gui_pairing_manager.py` — Smart file pairing
- `neutral_pairing_service.py` — Pairing service
- `neutral_upload_service.py` — Upload service
- `ki_module.py` — Ollama API integration
- `quality_gui_ollama_suggestions.py` — KI correction suggestions

### Data directories
- `Checker_Projekte/` — Customer projects (source files + translations)
- `glossaries/` — Glossary files (CSV/XLSX/JSON)
- `reports/` — Analysis reports
- `test_files/` — Test data

## Rules
- All UI text in German
- Use Tailwind CSS classes in NiceGUI (`.classes('...')`)
- Dependencies in `requirements.txt`
- Existing `_legacy/` folder contains old CustomTkinter app — do not modify
