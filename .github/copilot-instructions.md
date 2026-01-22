# Copilot instructions for this repo

Purpose: Make AI agents productive fast in this CustomTkinter-based Checker app by capturing architecture, workflows, and project-specific rules.

## Big picture
- GUI app built on CustomTkinter. Core UI is a Welcome Screen split into modular feature blocks (e.g., customer management).
- Central design system in `design_system.py` provides single source of truth for colors, spacing, typography, and component presets.
- Config is read from `config.json` (essential, protected) and lightweight overrides like `checker_config.json` (e.g., `projects_base_path`).
- Some features delegate to business logic if present (e.g., `CustomerManager`), with legacy JSON/file-based fallbacks.
- Critical-file protection is tracked via `CRITICAL_FILES_REGISTRY.json`.

## Developer workflows
- Quick UI run (minimal): `einfacher_welcome_screen.py` launches a simple, clean Welcome Screen using the design system.
- Welcome Screen test: use the VS Code task “Run Welcome Screen Test” (runs `final_test.bat` if present in the workspace root).
- Logging/helpers: import from `common_imports.py` and use `setup_common_logger()`; avoid raw prints in production code paths.

## Project conventions you must follow
- Light mode only: never set or depend on dark mode. Appearance is enforced to light.
- No icons in UI text: labels/buttons are text-only (German). Do not add emoji/icons to visible UI; keep strings professional and concise.
- Use the design system exclusively:
  - Colors: `DesignSystem.get_color('token')` or `from design_system import get_color`.
  - Spacing: `DesignSystem.get_spacing_value('sm|md|lg|xl')` or `get_spacing('md')`.
  - Fonts: `ctk.CTkFont(*DesignSystem.get_font('body_md'))` or `get_font('body_md')`.
  - Components: `DesignSystem.create_button_style('primary'|'secondary'|'warning')`, `DesignSystem.create_card_style()`.
- Modular orchestrator pattern for UI: create small helpers per section; avoid monolith methods.
- Preserve existing behavior: don’t change method signatures, event handlers, or public attributes on existing screens; only additions/refinements.
- German UI copy: keep UI labels/messages in German; stay consistent with existing wording.

## Cross-component contracts (common in Welcome Screen modules)
- Parent screen provides style helpers and context:
  - `self.get_color()`, `self.get_typography()`, `self.get_spacing()`, and often `self.get_component_value('borders.radius_sm')` style accessors.
  - `self.projects_base_path` used for per-customer folders.
  - `self.show_toast(message, type, duration=...)` for feedback.
  - `self.after(ms, fn)` for UI updates from background logic.
- Business logic integration: prefer `CustomerManager` (if importable) and fall back to JSON file ops (see `welcome_screen_customer.py`).

## Examples (repo-specific patterns)
- Button with design system:
  - `btn = ctk.CTkButton(parent, **create_button(style='primary', text='Speichern'))`
- Card/container with tokens:
  - `frame = ctk.CTkFrame(p, fg_color=get_color('surface'), border_width=1, border_color=get_color('surface_border'))`
- Typography usage:
  - `title = ctk.CTkLabel(f, text='Kunden-Management', font=ctk.CTkFont(*get_font('heading_md')))`

## Safety/constraints
- Protected/critical files: consult `CRITICAL_FILES_REGISTRY.json`; avoid editing `config.json`, `modern_translation_quality_gui.py`, `ui_theme.py`, etc., without explicit intent and backups.
- Never hardcode hex colors, spacings, font sizes, or DPI scaling; always fetch from `design_system.py`.
- Windows shell specifics: native folder opens use `subprocess.run(['explorer', path])` (see `welcome_screen_customer.py`).

## Calendar and workflows
- Calendar (if present): the enhanced calendar shows “day details” with direct file links and file-type groups. Typical functions to look for: `_show_enhanced_day_details`, `_create_enhanced_project_card_v2`, `_open_source_file`, `_batch_quality_check`. Keep styling via `DesignSystem` (no hardcoded colors), light mode only, and use grid inside content containers.
- Corner radius and borders: pull values from `DesignSystem.get_component_property('borders', 'radius_*'|'width_*')` and colors from `get_color('surface'|'surface_border')` for cards/frames.
- Workflows: launch sub-apps via `subprocess.Popen([sys.executable, workflow_file])` as shown in `einfacher_welcome_screen.py`. Files like `modern_translation_quality_gui.py` are protected; review `CRITICAL_FILES_REGISTRY.json` before edits.

## Upload (Best Practices)
- Datei-Auswahl: nutze `filedialog.askopenfilenames` und filtere anhand `config.json -> paths.projects.allowed_extensions`.
- IO/Performance: große Dateien (>10MB) in Chunks lesen/schreiben; Datei- und Kopier-Operationen in Threads ausführen; UI-Updates via `self.after(...)` (siehe `async_file_operations.py`).
- Zielpfad: unter `Path(self.projects_base_path) / aktueller_kunde` ablegen; Metadaten analog zu `welcome_screen_customer.py` (`customer_info.json`) strukturieren.
- Feedback: Fortschritt mit `CTkProgressBar` (0..1) und `self.show_toast(...)`; keine UI-Blocks, immer `with`-Kontext für Filehandles.

## Quality-Check (Best Practices)
- Start: Workflows per `subprocess.Popen([sys.executable, workflow_file])` (siehe `einfacher_welcome_screen.py`); kritische Dateien wie `modern_translation_quality_gui.py` nicht direkt bearbeiten (siehe `CRITICAL_FILES_REGISTRY.json`).
- Übergaben: Datei-/Projektpfade via CLI-Args oder temporäre JSON-Bridge übergeben (falls unterstützt); Logging mit `setup_common_logger` aus `common_imports.py`.
- Laufzeit: Lange Prüfungen im Hintergrund ausführen; Status/Ergebnis über `self.after(...)` in die UI bringen; Nutzerhinweise per `self.show_toast` (DE-Text, keine Icons).
- Styling: Dialoge/Frames strikt über `design_system.py` stylen (Farben/Fonts/Abstände), Light-Mode only.

## Where to look first
- Styling and tokens: `design_system.py` (get_color/get_font/create_button/create_card).
- Welcome Screen patterns: `welcome_screen_customer.py` (orchestrator + business-logic fallback).
- Minimal runnable UI: `einfacher_welcome_screen.py`.
- Configuration: `config.json`, `checker_config.json` (e.g., `projects_base_path`).
- Common imports/logger: `common_imports.py`.

If anything here is unclear or you find a conflicting pattern, surface it and propose a precise update to this file referencing the exact lines/files you found.
