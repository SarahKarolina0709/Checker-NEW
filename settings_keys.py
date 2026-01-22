"""Zentrale Konstantenliste für Settings-Keys (Vorbereitung).

Hinweis: Diese Datei dient als zentrale Referenz. Bestehender Code bleibt vorerst unverändert
und kann schrittweise auf diese Konstanten umgestellt werden.
"""

# Analyse/Sprachen
ANALYSIS_LANG_SOURCE = 'analysis.lang.source'
ANALYSIS_LANG_TARGET = 'analysis.lang.target'

# Analyse/Tiefe
ANALYSIS_DEPTH = 'analysis.depth'

# Analyse/Qualitätskriterien
ANALYSIS_QC_ORDER = 'analysis.qc.order'
ANALYSIS_QC_ENABLED = 'analysis.qc.enabled'
ANALYSIS_QC_COLLAPSED = 'analysis.qc.collapsed'

# Semantik / Ollama
ANALYSIS_PHASE3_SEMANTIC = 'analysis.phase3.semantic'
ANALYSIS_PHASE3_USE_OLLAMA = 'analysis.phase3.semantic.use_ollama'
ANALYSIS_PHASE3_OLLAMA_MODEL = 'analysis.phase3.semantic.ollama_model'

# Module toggles
ANALYSIS_PHASE2_ENABLED = 'analysis.phase2.enabled'
ANALYSIS_PHASE3_ENABLED = 'analysis.phase3.enabled'

# Phase 2 Glossar
ANALYSIS_PHASE2_GLOSSARY_PATH = 'analysis.phase2.glossary_path'

# Logging / Performance (Beispiele aus quality_gui_settings_ui)
LOGGING_ROTATE_KB = 'logging.event_log_rotate_kb'
LOGGING_GENERATIONS = 'logging.event_log_generations'
PERF_DELTA_SNAPSHOTS = 'performance.delta_snapshots_experimental'
PERF_SNAPSHOT_WARN_KB = 'performance.snapshot_memory_warn_kb'
