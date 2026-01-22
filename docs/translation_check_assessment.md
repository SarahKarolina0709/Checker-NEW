# Translation Check Assessment

Updated: 2025-10-01

## Current Signals Collected

- **Fallback pipeline (`_run_analysis_pipeline`)**
  - Computes basic metrics only (pair count, token overlap similarity, average length ratio, glossary hit ratio when a glossary CSV/TSV is loaded, readability, passive voice rate).
  - Does **not** run the phase-based checkers that already exist (`quality_gui_phase1_checkers`, `quality_gui_phase2_checkers`, `quality_gui_phase3_checkers`).
  - Does not enrich per-pair data with `numbers_missing`, placeholder diffs, HTML balance findings, etc.; therefore, downstream plugins cannot act on those signals.
- **Plugin execution (`QualityGuiAnalysisPipeline`)**
  - Loads rule classes from `plugins/…`, but the UI only invokes the plugin pipeline in the background report path (see `_run_background_analysis_safe`).
  - The analysis context currently contains only metadata (`analysis_id`, file paths). Rules that expect rich fields such as `pairs`, `source_texts`, `translation_texts`, or number diff summaries never receive them.
- **Config defaults**
  - `checker_config.json` has no `analysis.*` overrides; phase-2 defaults (coverage ratio 0.6, min source length 40) remain compiled defaults.
  - UI thresholds (similarity low = 0.85, completeness low = 0.98) differ from the semantic checker’s hard-coded threshold (0.70 + dynamic adjustments), so the warning banner and per-segment semantic issues are not aligned.

## Observed Gaps

1. **Phase checkers are currently unused** for interactive analyses, so placeholders, terminology drift, HTML mismatches, and number/unit checks never surface in the dashboard.
2. **Plugin rules cannot evaluate translation content**, because the context lacks pre-computed per-pair diffs and the rules are not invoked during the main analysis flow.
3. **Semantic similarity threshold mismatch**: UI shading expects <0.85 to be problematic, but the checker only flags segments below 0.65–0.75 (depending on length), which under-reports issues compared to what the dashboard warns about.
4. **No explicit configuration surface**: important knobs (coverage ratio, proper-name whitelist, semantic threshold, plugin timeouts) rely on code defaults; there is no documented JSON to tune them per project.

## Recommended Next Steps

1. **Wire the phase checkers into `_run_analysis_pipeline`** (or migrate to the plugin pipeline) so the UI receives `issues_phase1..3`. This automatically surfaces placeholder, HTML, number/unit, and terminology findings that already exist.
2. **Populate plugin context** with `pairs`, `source_texts`, `translation_texts`, and computed diffs (missing/extra numbers, placeholders) before calling `_analyze_with_plugins`. That enables `NumberConsistencyRule`, `TerminologyGlossaryRule`, and `UntranslatedSegmentsRule` to contribute real findings.
3. **Expose analysis configuration in `checker_config.json`** under an "analysis" section (phase toggles, coverage thresholds, semantic settings) and load it via `ConfigManager`. This keeps tuning outside of source code.
4. **Align similarity thresholds**: either raise the checker threshold to match the UI (0.85) or adjust the UI to reflect the dynamic 0.65–0.75 range used by `check_semantic_similarity`.
5. **Add automated tests** that feed sample pairs through the integrated pipeline to ensure numeric consistency, terminology enforcement, and semantic alerts stay enabled after future refactors.

These changes would bring the translation validation system in line with the existing design assets and ensure the dashboard reflects the full breadth of the quality checks that already live in the repository.
