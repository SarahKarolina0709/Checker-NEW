"""Analyse Placeholder & Ergebnisse (Design-System & dynamisch).

Aktualisiert gemäß Vorgaben:
 - i18n via app._t()
 - Keine Emojis / Icons (Policy-konform)
 - Farben ausschließlich über app.get_color(); Header Text nutzt 'text_inverse'
 - Dynamische Daten aus app.analysis_results (summary/findings)
 - Thread-sicher: Rendering per root.after(0, ...) eingereiht
 - Vereinheitlichte Toast-API: _show_toast (Wrapper in Haupt-App ergänzt)
 - Optionale Plugins & Report defensiv
 - Erst Render, dann Events/Report
 - UI-Optimierungen: Kategorie-Prefix, Hilfetexte, Lösungsvorschläge
"""
from __future__ import annotations
import time
import re
import customtkinter as ctk
from typing import Any, Dict, List, Tuple

# UI-Optimierungen importieren
try:
    from ui_optimization_helpers import (
        get_enriched_finding_info,
        format_finding_help_text,
        get_quick_actions,
        CATEGORY_INFO
    )
    UI_OPTIMIZATION_AVAILABLE = True
except ImportError:
    UI_OPTIMIZATION_AVAILABLE = False

# ------------------------------------------------------------
# Loading Overlay API (während laufender Analyse)
# ------------------------------------------------------------
def show_analysis_loading(app, phase_title: str | None = None):
    """Zeigt/erstellt ein Overlay für Analyse-Fortschritt.

    Robust gegen Mehrfachaufrufe und fehlenden root."""
    try:
        root = getattr(app, 'root', None)
        if not root:
            return
        overlay = getattr(app, '_analysis_loading_overlay', None)
        if overlay and overlay.winfo_exists():
            update_analysis_loading(app, phase_title=phase_title)
            return
        overlay = ctk.CTkFrame(root, fg_color=app.get_color('surface'))
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay.configure(border_width=1, border_color=app.get_color('surface_border'))
        setattr(app, '_analysis_loading_overlay', overlay)
        spacing_lg = app.get_spacing('lg') if hasattr(app, 'get_spacing') else 24
        inner = ctk.CTkFrame(overlay, fg_color=app.get_color('surface_hover'), corner_radius=12)
        inner.pack(expand=True, padx=spacing_lg*2, pady=spacing_lg*2, fill='both')
        title = ctk.CTkLabel(inner, text=app._t('Analyse läuft...'), font=ctk.CTkFont(*app.get_typography('heading')),
                             text_color=app.get_color('text_primary'))
        title.pack(pady=(spacing_lg, spacing_lg//2))
        phase_lbl = ctk.CTkLabel(inner, text=phase_title or '', font=ctk.CTkFont(*app.get_typography('body')),
                                 text_color=app.get_color('text_secondary'))
        phase_lbl.pack()
        bar = ctk.CTkProgressBar(inner)
        bar.pack(fill='x', padx=spacing_lg, pady=(spacing_lg, spacing_lg//2))
        bar.set(0)
        info = ctk.CTkLabel(inner, text=app._t('Bitte warten...'), font=ctk.CTkFont(*app.get_typography('caption')),
                            text_color=app.get_color('text_secondary'))
        info.pack(pady=(0, spacing_lg))
        overlay._phase_lbl = phase_lbl  # type: ignore
        overlay._progress_bar = bar     # type: ignore
        overlay._info_lbl = info        # type: ignore
    except Exception:
        pass

def update_analysis_loading(app, phase_title: str | None = None, progress: float | None = None, info: str | None = None):
    """Aktualisiert Overlay (Phase/Progress/Text)."""
    try:
        overlay = getattr(app, '_analysis_loading_overlay', None)
        if not overlay or not overlay.winfo_exists():
            return
        if phase_title is not None:
            try: overlay._phase_lbl.configure(text=phase_title)  # type: ignore
            except Exception: pass
        if isinstance(progress,(int,float)):
            try:
                overlay._progress_bar.set(max(0.0,min(1.0,progress)))  # type: ignore
            except Exception: pass
        if info is not None:
            try: overlay._info_lbl.configure(text=info)  # type: ignore
            except Exception: pass
    except Exception:
        pass

def hide_analysis_loading(app):
    """Entfernt Overlay falls vorhanden."""
    try:
        overlay = getattr(app, '_analysis_loading_overlay', None)
        if overlay and overlay.winfo_exists():
            overlay.destroy()
    except Exception:
        pass

# ------------------------------------------------------------
# Helper: zentrales Toast & Debug & Score Extraction
# ------------------------------------------------------------
def _toast(app, msg: str, level: str = 'info') -> None:
    """Vereinheitlichte Toast-Ausgabe (falls vorhanden)."""
    try:
        if hasattr(app, '_show_toast') and callable(getattr(app, '_show_toast')):
            app._show_toast(msg, level)
        elif hasattr(app, 'show_toast') and callable(getattr(app, 'show_toast')):
            app.show_toast(msg, level)
    except Exception:
        pass

def _debug(app, msg: str) -> None:
    """Optionales Debug-Logging ohne harte Abhängigkeit."""
    try:
        if hasattr(app, 'logger') and hasattr(app.logger, 'debug'):
            app.logger.debug(msg)
    except Exception:
        pass

def _extract_score(summary: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Normalisiert Score (0..1 oder 0..100) und liefert View/Pct.

    Rückgabe:
      raw_0_100: float|None  (0..100)
      view:      str (z.B. "87/100" oder '–')
      pct:       float|None  (0..100)
    """
    raw = None
    try:
        if isinstance(summary, dict):
            val = summary.get('quality_score')
            if isinstance(val, (int, float)):
                raw = val * 100 if val <= 1 else val
            else:
                alt = summary.get('overall_score_norm')
                if isinstance(alt, (int, float)):
                    raw = (alt * 100) if alt <= 1 else alt
        if raw is None and isinstance(metrics, dict):
            mv = metrics.get('overall_score')
            if isinstance(mv, (int, float)):
                raw = mv * 100 if mv <= 1 else mv
    except Exception:
        raw = None
    if isinstance(raw, (int, float)):
        clamped = max(0.0, min(100.0, raw))
        return {
            'raw_0_100': clamped,
            'view': f"{int(round(clamped))}/100",
            'pct': clamped
        }
    return {'raw_0_100': None, 'view': '–', 'pct': None}

try:  # Optionale Modelle
    from core.model import AnalysisReport, Finding
except Exception:  # Fallback ohne harte Abhängigkeit
    AnalysisReport = None  # type: ignore
    Finding = None  # type: ignore

def show_analysis_placeholder(app, parent):
    """Zeigt Platzhalter (i18n / theming / no-icons)."""
    try:
        # Bereich leeren
        for w in list(parent.winfo_children()):
            try: w.destroy()
            except Exception: pass
        spacing_lg = app.get_spacing('lg') if hasattr(app, 'get_spacing') else 24
        spacing_xl = app.get_spacing('xl') if hasattr(app, 'get_spacing') else 32
        # Placeholder Card/Frame – korrekt innerhalb try
        frame = ctk.CTkFrame(parent, fg_color=app.get_color('transparent'))
        frame.pack(fill="both", expand=True, padx=spacing_xl, pady=spacing_xl)
        text = (
            app._t("Ready for analysis") + "\n\n" +
            app._t("Upload your source and translation files to start a comprehensive quality check.") + "\n\n" +
            app._t("The system detects languages, analyses translation quality and provides detailed improvement suggestions.")
        )
        ctk.CTkLabel(
            frame,
            text=text,
            font=ctk.CTkFont(*app.get_typography('body_bold')),
            text_color=app.get_color('text_primary'),
            justify="center"
        ).pack(expand=True, padx=spacing_lg, pady=spacing_lg)
    except Exception:
        pass

def show_analysis_results(app):
    """Thread-sicher einreihen und dann UI rendern."""
    try:
        root = getattr(app, 'root', None)
        if root and hasattr(root, 'after'):
            import threading
            if threading.current_thread().name != 'MainThread':
                return root.after(0, lambda: _render_results_ui(app))
        _render_results_ui(app)
    except Exception:
        pass


def _render_results_ui(app):
    """Interner Renderer für Analyse-Ergebnisse (dynamisch/i18n)."""
    data = getattr(app, 'analysis_results', {}) or {}
    if not isinstance(data, dict):
        data = {}
    print(f"DEBUG _render_results_ui: app.analysis_results keys = {list(data.keys())}")
    print(f"DEBUG _render_results_ui: data has {len(data)} top-level keys")
    try:
        existing_preview = getattr(app, '_ingest_preview_window', None)
        if existing_preview and existing_preview.winfo_exists():
            existing_preview.destroy()
    except Exception:
        pass
    try:
        setattr(app, '_ingest_preview_window', None)
    except Exception:
        pass
    summary = data.get('summary', {}) or {}
    metrics = data.get('metrics') if isinstance(data.get('metrics'), dict) else {}
    
    # CRITICAL FIX: Aggregate findings from phase issues if empty
    findings: List[Dict[str, Any]] = data.get('findings', []) if isinstance(data.get('findings'), list) else []
    print(f"DEBUG _render_results_ui: Got {len(findings)} findings from analysis_results initially")
    
    # If findings empty, aggregate from phase issues
    if not findings:
        print(f"DEBUG _render_results_ui: Findings empty - aggregating from phase issues")
        for phase_key in ('issues_phase1', 'issues_phase2', 'issues_phase3'):
            phase_issues = data.get(phase_key, [])
            if isinstance(phase_issues, list) and phase_issues:
                print(f"DEBUG _render_results_ui: Found {len(phase_issues)} issues in {phase_key}")
                findings.extend(phase_issues)
    
    print(f"DEBUG _render_results_ui: Final findings count = {len(findings)}")
    print(f"DEBUG _render_results_ui: findings type = {type(findings)}")
    print(f"DEBUG _render_results_ui: issues_phase1={len(data.get('issues_phase1', []) or [])}, issues_phase2={len(data.get('issues_phase2', []) or [])}, issues_phase3={len(data.get('issues_phase3', []) or [])}")
    # Quick debug: log how many raw findings the analysis produced (helps distinguish empty-results vs. filter hide)
    try:
        count_msg = f"Findings raw count: {len(findings)}"
        if hasattr(app, 'logger') and hasattr(app.logger, 'info'):
            app.logger.info(count_msg)
        else:
            _debug(app, count_msg)
        # DEBUG: Log unique phase keys in findings
        if findings:
            unique_phases = set()
            for f in findings:
                phase_key = f.get('phase') or f.get('category') or ''
                if phase_key:
                    unique_phases.add(phase_key)
            debug_phases_msg = f"DEBUG: Unique phase keys in findings: {sorted(unique_phases)}"
            if hasattr(app, 'logger') and hasattr(app.logger, 'info'):
                app.logger.info(debug_phases_msg)
            print(debug_phases_msg)
        else:
            print("DEBUG: findings is empty - no phase keys to log")
    except Exception as e:
        print(f"DEBUG: Exception during findings analysis: {e}")
    phases_info = data.get('phases', {}) if isinstance(data.get('phases'), dict) else {}
    phase_issue_lists = {
        'phase1': data.get('issues_phase1') if isinstance(data.get('issues_phase1'), list) else [],
        'phase2': data.get('issues_phase2') if isinstance(data.get('issues_phase2'), list) else [],
        'phase3': data.get('issues_phase3') if isinstance(data.get('issues_phase3'), list) else []
    }
    pair_details_raw = data.get('pair_details')
    if isinstance(pair_details_raw, list):
        pair_details = [entry for entry in pair_details_raw if isinstance(entry, dict)]
    else:
        pair_details = []
    if not phases_info:
        fallback_phases: Dict[str, Dict[str, Any]] = {}
        phase_counts = data.get('phase_issue_counts') if isinstance(data.get('phase_issue_counts'), dict) else {}
        for key, issues in phase_issue_lists.items():
            count = len(issues)
            if count:
                fallback_phases[key] = {'issue_total': count}
        for key, count in phase_counts.items() if isinstance(phase_counts, dict) else []:
            try:
                if count and key not in fallback_phases:
                    fallback_phases[key] = {'issue_total': count}
            except Exception:
                continue
        consolidated = data.get('consolidated') if isinstance(data.get('consolidated'), dict) else {}
        if consolidated:
            total = consolidated.get('total')
            risk = consolidated.get('risk_score')
            # DEBUG: Log consolidation data
            try:
                print(f"DEBUG [analysis_results]: Consolidation data - total={total}, risk={risk}")
            except Exception:
                pass
            
            # WICHTIG: 0 Befunde = 0 Risiko (nicht None oder 100!)
            if total == 0:
                risk = 0.0
            
            if total is not None or risk is not None:
                fallback_phases['consolidation'] = {
                    'name': 'Konsolidierung',
                    'description': 'Gesamtbewertung aller Befunde'
                }
                if total is not None:
                    fallback_phases['consolidation']['total'] = total
                if risk is not None:
                    fallback_phases['consolidation']['risk_score'] = risk
        suggestions = data.get('suggestions') if isinstance(data.get('suggestions'), list) else []
        if suggestions:
            fallback_phases['recommendations'] = {
                'name': 'Empfehlungen',
                'suggestions': len(suggestions),
                'description': 'Automatisch generierte Verbesserungsvorschläge'
            }
        phases_info = fallback_phases
    def _normalize_checker_list(value: Any) -> List[str]:
        if isinstance(value, (list, tuple, set)):
            return [str(item) for item in value if item]
        if isinstance(value, str):
            return [value] if value else []
        if value is None:
            return []
        try:
            return [str(value)]
        except Exception:
            return []

    grammar_used = _normalize_checker_list(summary.get('grammar_checkers_used') if isinstance(summary, dict) else None)
    grammar_disabled = _normalize_checker_list(summary.get('grammar_checkers_disabled') if isinstance(summary, dict) else None)
    grammar_force = bool(summary.get('grammar_force_override')) if isinstance(summary, dict) else False
    grammar_cache_hit = bool(summary.get('grammar_cache_hit')) if isinstance(summary, dict) else False
    # Score
    score_info = _extract_score(summary, metrics)
    raw_score = score_info['raw_0_100']
    score_view = score_info['view']
    score_pct = score_info['pct']
    # UI reinigen
    for w in list(app.output_frame.winfo_children()):
        try:
            w.destroy()
        except Exception:
            pass

    spacing_lg = app.get_spacing('lg') if hasattr(app, 'get_spacing') else 24
    spacing_md = app.get_spacing('md') if hasattr(app, 'get_spacing') else 16
    spacing_sm = app.get_spacing('sm') if hasattr(app, 'get_spacing') else 8
    spacing_xl = app.get_spacing('xl') if hasattr(app, 'get_spacing') else 32
    wrap_length = max(int(spacing_xl * 18), 560)
    radius_xl = _safe_radius(app, 'radius_xl', 12)
    radius_md = _safe_radius(app, 'radius_md', 8)

    card = ctk.CTkFrame(app.output_frame, fg_color=app.get_color('surface'), corner_radius=radius_xl, border_width=1, border_color=app.get_color('surface_border'))
    card.pack(fill='both', expand=True, padx=spacing_xl, pady=spacing_xl)

    header = ctk.CTkFrame(card, fg_color=app.get_color('primary'))
    header.pack(fill='x')
    header_inner = ctk.CTkFrame(header, fg_color=app.get_color('transparent'))
    header_inner.pack(fill='x', padx=spacing_xl, pady=(spacing_lg//1.2, spacing_lg//2))
    title_frame = ctk.CTkFrame(header_inner, fg_color=app.get_color('transparent'))
    title_frame.pack(side='left')
    title_lbl = ctk.CTkLabel(title_frame,
                 text=app._t('Quality Analysis Complete'),
                 font=ctk.CTkFont(*app.get_typography('title')),
                 text_color=app.get_color('text_inverse'))
    title_lbl.pack(anchor='w')
    # Phase-Titel Platzhalter (falls letzte Phase bekannt, dynamisch aktualisierbar)
    phase_title = getattr(app, 'last_analysis_phase_title', None)
    phase_sub_lbl = ctk.CTkLabel(title_frame,
                 text=(app._t('Phase')+': '+phase_title) if phase_title else '',
                 font=ctk.CTkFont(*app.get_typography('caption')),
                 text_color=app.get_color('text_inverse'))
    phase_sub_lbl.pack(anchor='w')
    try:
        app._analysis_phase_sub_label = phase_sub_lbl  # Referenz für spätere Live-Updates
    except Exception:
        pass

    # View Mode Tabs (Übersicht / Phasen / Befunde)
    view_state = {'mode': 'overview', 'phase_filter': 'ALL'}
    tabs_frame = ctk.CTkFrame(header_inner, fg_color=app.get_color('transparent'))
    tabs_frame.pack(side='right')
    # Persist last tab
    _cfg = None
    try:
        from config_manager import ConfigManager  # optional
        _cfg = getattr(app, '_config_manager', None) or ConfigManager()
        if not hasattr(app, '_config_manager'):
            app._config_manager = _cfg
        last_tab = _cfg.get('analysis.ui.last_tab')
        if isinstance(last_tab, str) and last_tab in ('overview','phases','findings'):
            view_state['mode'] = last_tab
        saved_phase = _cfg.get('analysis.ui.findings.phase')
        if isinstance(saved_phase, str):
            view_state['phase_filter'] = saved_phase
    except Exception:
        _cfg = None
    def _set_mode(mode: str):
        try:
            view_state['mode'] = mode
            _rerender_body()
            # Button Highlight
            for btn, val in tab_buttons:
                try:
                    active = (val == mode)
                    btn.configure(fg_color=app.get_color('secondary') if active else app.get_color('surface_hover'),
                                  text_color=app.get_color('text_inverse') if active else app.get_color('text_primary'))
                except Exception:
                    pass
            try:
                if _cfg:
                    _cfg.set('analysis.ui.last_tab', mode)
            except Exception:
                pass
        except Exception:
            pass
    tab_buttons = []
    for lab, val in [ (app._t('Übersicht'), 'overview'), (app._t('Phasen'), 'phases'), (app._t('Befunde'), 'findings') ]:
        try:
            b = ctk.CTkButton(tabs_frame, text=lab, width=110, height=32,
                              fg_color=app.get_color('surface_hover'), hover_color=app.get_color('surface_hover'),
                              text_color=app.get_color('text_primary'),
                              command=lambda _v=val: _set_mode(_v))
            b.pack(side='left', padx=4)
            tab_buttons.append((b, val))
        except Exception:
            continue

    # Body Frame (wird dynamisch neu befüllt je nach Tab)
    body_container = ctk.CTkFrame(card, fg_color=app.get_color('transparent'))
    body_container.pack(fill='both', expand=True, padx=spacing_xl, pady=spacing_lg)
    preview_state: Dict[str, Any] = {'window': None}

    def _clear_body():
        for w in list(body_container.winfo_children()):
            try: w.destroy()
            except Exception: pass

    def _section_card(parent, title: str, tone: str='surface_hover'):
        frm = ctk.CTkFrame(parent,
                           fg_color=app.get_color(tone),
                           corner_radius=radius_md,
                           border_width=1,
                           border_color=app.get_color('surface_border'))
        frm.pack(fill='x', pady=(0, spacing_lg))
        try:
            ctk.CTkLabel(frm, text=title, font=ctk.CTkFont(*app.get_typography('subheading')),
                         text_color=app.get_color('text_primary')).pack(anchor='w', padx=spacing_lg, pady=(spacing_lg//1.5, 2))
        except Exception:
            pass
        inner = ctk.CTkFrame(frm, fg_color=app.get_color('transparent'))
        inner.pack(fill='x', padx=spacing_lg, pady=(0, spacing_lg))
        return inner

    def _open_ingest_preview(pair_rows: List[Dict[str, Any]], metrics_snapshot: Dict[str, Any] | None = None) -> None:
        """Öffnet eine modale Vorschau mit den eingelesenen Segmenten."""
        launch_fn = getattr(app, '_launch_pair_details_preview', None)
        if callable(launch_fn):
            try:
                launch_fn(pair_rows, metrics_snapshot)
                return
            except Exception:
                pass
        if not pair_rows:
            _toast(app, app._t('Keine Segmentdaten zum Anzeigen.'), 'info')
            return
        try:
            current = preview_state.get('window')
            if current and current.winfo_exists():
                current.destroy()
        except Exception:
            pass
        try:
            master_widget = getattr(app, 'root', None)
        except Exception:
            master_widget = None
        if not master_widget:
            try:
                master_widget = app.output_frame.winfo_toplevel()
            except Exception:
                master_widget = app.output_frame
        top = ctk.CTkToplevel(master_widget)
        preview_state['window'] = top
        try:
            setattr(app, '_ingest_preview_window', top)
        except Exception:
            pass
        top.title(app._t('Eingelesener Text'))
        try:
            top.configure(fg_color=app.get_color('surface'))
        except Exception:
            pass
        try:
            top.geometry('940x720')
            top.minsize(720, 480)
        except Exception:
            pass
        try:
            top.transient(master_widget)
        except Exception:
            pass

        spacing_container = spacing_lg
        container = ctk.CTkFrame(top, fg_color=app.get_color('transparent'))
        container.pack(fill='both', expand=True, padx=spacing_container, pady=spacing_container)

        header_frame = ctk.CTkFrame(container, fg_color=app.get_color('transparent'))
        header_frame.pack(fill='x')
        ctk.CTkLabel(
            header_frame,
            text=app._t('Eingelesener Text'),
            font=ctk.CTkFont(*app.get_typography('heading')),
            text_color=app.get_color('text_primary')
        ).pack(anchor='w')

        metrics_snapshot = metrics_snapshot or {}
        total_segments = len(pair_rows)
        translated_segments = metrics_snapshot.get('segments_translated') if isinstance(metrics_snapshot, dict) else None
        untranslated_segments = metrics_snapshot.get('segments_untranslated') if isinstance(metrics_snapshot, dict) else None
        avg_ratio = metrics_snapshot.get('avg_length_ratio') if isinstance(metrics_snapshot, dict) else None
        try:
            total_source_chars = sum(len((str(entry.get('source_text') or '').strip())) for entry in pair_rows)
        except Exception:
            total_source_chars = 0
        try:
            total_target_chars = sum(len((str(entry.get('target_text') or '').strip())) for entry in pair_rows)
        except Exception:
            total_target_chars = 0

        stats_lines = [
            app._t('Segmente gesamt') + f": {total_segments}",
            app._t('Zeichen Quelle') + f": {total_source_chars}",
            app._t('Zeichen Ziel') + f": {total_target_chars}"
        ]
        if isinstance(translated_segments, int):
            stats_lines.append(app._t('Übersetzte Segmente') + f": {translated_segments}")
        if isinstance(untranslated_segments, int):
            stats_lines.append(app._t('Unübersetzte Segmente') + f": {untranslated_segments}")
        if isinstance(avg_ratio, (int, float)):
            stats_lines.append(app._t('Durchschnittliches Längenverhältnis') + f": {avg_ratio:.3f}")

        stats_label = ctk.CTkLabel(
            container,
            text='\n'.join(stats_lines),
            font=ctk.CTkFont(*app.get_typography('body')),
            text_color=app.get_color('text_secondary'),
            justify='left'
        )
        stats_label.pack(anchor='w', pady=(spacing_sm, spacing_md))

        display_limit = 120
        rows_to_render = pair_rows[:display_limit]
        truncated = total_segments > display_limit

        if truncated:
            ctk.CTkLabel(
                container,
                text=app._t('Hinweis: Anzeige auf {limit} Segmente begrenzt.').format(limit=display_limit),
                font=ctk.CTkFont(*app.get_typography('caption')),
                text_color=app.get_color('warning'),
                justify='left'
            ).pack(anchor='w', pady=(0, spacing_sm))

        text_frame = ctk.CTkFrame(container, fg_color=app.get_color('transparent'))
        text_frame.pack(fill='both', expand=True)

        text_box = ctk.CTkTextbox(
            text_frame,
            wrap='word',
            fg_color=app.get_color('surface'),
            text_color=app.get_color('text_primary'),
            font=ctk.CTkFont(*app.get_typography('body'))
        )
        text_box.pack(side='left', fill='both', expand=True)
        scrollbar = ctk.CTkScrollbar(text_frame, command=text_box.yview)
        scrollbar.pack(side='right', fill='y')
        try:
            text_box.configure(yscrollcommand=scrollbar.set)
        except Exception:
            pass

        segment_lines: List[str] = []
        for idx, entry in enumerate(rows_to_render, start=1):
            try:
                source_text = str(entry.get('source_text') or '').strip()
            except Exception:
                source_text = ''
            try:
                target_text = str(entry.get('target_text') or '').strip()
            except Exception:
                target_text = ''
            page_hint = entry.get('page') or entry.get('page_number') or entry.get('page_index')
            if page_hint:
                header_line = app._t('Segment {idx} – Seite {page}').format(idx=idx, page=page_hint)
            else:
                header_line = app._t('Segment {idx}').format(idx=idx)
            segment_lines.extend([
                header_line,
                app._t('Quelle') + ':',
                source_text or '–',
                '',
                app._t('Ziel') + ':',
                target_text or '–',
                '\n' + ('-' * 48)
            ])

        if truncated:
            segment_lines.append(
                app._t('Restliche Segmente bitte in der Analyse speichern oder exportieren.')
            )

        try:
            text_box.insert('1.0', '\n'.join(segment_lines))
            text_box.configure(state='disabled')
        except Exception:
            pass

        actions = ctk.CTkFrame(container, fg_color=app.get_color('transparent'))
        actions.pack(fill='x', pady=(spacing_md, 0))

        def _on_close() -> None:
            try:
                if preview_state.get('window') and preview_state['window'].winfo_exists():
                    preview_state['window'].destroy()
            except Exception:
                pass
            preview_state['window'] = None
            try:
                setattr(app, '_ingest_preview_window', None)
            except Exception:
                pass

        def _copy_all() -> None:
            try:
                text_box.configure(state='normal')
                content = text_box.get('1.0', 'end-1c')
                text_box.configure(state='disabled')
                top.clipboard_clear()
                top.clipboard_append(content)
                _toast(app, app._t('Segmenttext kopiert.'), 'success')
            except Exception:
                _toast(app, app._t('Kopieren nicht möglich.'), 'error')

        copy_btn = ctk.CTkButton(
            actions,
            text=app._t('In Zwischenablage kopieren'),
            width=220,
            height=32,
            fg_color=app.get_color('secondary'),
            hover_color=app.get_color('secondary_hover'),
            text_color=app.get_color('text_inverse'),
            command=_copy_all
        )
        copy_btn.pack(side='left')

        close_btn = ctk.CTkButton(
            actions,
            text=app._t('Schließen'),
            width=140,
            height=32,
            fg_color=app.get_color('surface_hover'),
            hover_color=app.get_color('surface_hover'),
            text_color=app.get_color('text_primary'),
            command=_on_close
        )
        close_btn.pack(side='right')

        try:
            top.protocol('WM_DELETE_WINDOW', _on_close)
        except Exception:
            pass
        try:
            top.bind('<Escape>', lambda _evt: _on_close())
        except Exception:
            pass

        try:
            text_box.focus_set()
        except Exception:
            pass

    # Originaler body Inhalt wird in _render_overview() verschoben
    def _render_overview(body: ctk.CTkFrame):
        # Score Frame + Quick Stats + Summary + weitere Blocks
        _render_score_block(body)
        _render_quick_stats(body)
        _render_export_actions(body)  # Export-Buttons prominent unter Quick-Stats
        _render_summary_block(body)
        _render_severity_block(body)
        _render_guidance_block(body)
        _render_grammar_status(body)

    def _format_issue_excerpt(value: Any) -> Tuple[str, bool]:
        if value is None:
            return '', False
        try:
            text = str(value).strip()
            if not text:
                return '', False
            text = text.replace('\n', ' ')
            text = re.sub(r'\s+', ' ', text)
            text = text.replace('\u0000', '')
            looks_binary = False
            if text.startswith('PK') or '[Content_Types]' in text:
                looks_binary = True
            if any(ord(ch) < 32 and ch not in (' ', '\t') for ch in text):
                looks_binary = True
            if not looks_binary:
                alpha_digits = sum(1 for ch in text if ch.isalpha() or ch.isdigit())
                readability = alpha_digits / max(len(text), 1)
                if readability < 0.2:
                    looks_binary = True
            if len(text) > 160:
                text = text[:160] + ' …'
            return ('' if looks_binary else text, looks_binary)
        except Exception:
            return str(value), False

    def _format_issue_text(value: Any) -> str:
        try:
            if isinstance(value, (list, tuple, set)):
                seq = list(value)
                if not seq:
                    return ''
                preview: List[str] = []
                for idx, item in enumerate(seq):
                    if idx >= 4:
                        break
                    if isinstance(item, (list, tuple, set)):
                        preview.append(', '.join(str(x) for x in list(item)[:4]))
                    else:
                        preview.append(str(item))
                text = '; '.join(preview)
                remaining = len(seq) - len(preview)
                if remaining > 0:
                    text += app._t(' … noch {count} weitere').format(count=remaining)
                return text
            if isinstance(value, dict):
                preview = []
                for idx, (k, v) in enumerate(value.items()):
                    if idx >= 4:
                        break
                    preview.append(f"{k}: {v}")
                text = '; '.join(preview)
                if len(value) > len(preview):
                    text += app._t(' … zusätzliche Einträge')
                return text
            text = str(value)
            text = text.strip()
            if '[' in text and ']' in text:
                try:
                    tokens = re.findall(r"'([^']+)'", text)
                    if tokens:
                        preview_tokens = ', '.join(tokens[:4])
                        remaining_tokens = len(tokens) - 4
                        if remaining_tokens > 0:
                            preview_tokens += app._t(' … {count} weitere').format(count=remaining_tokens)
                        text = re.sub(r"\[[^\]]*\]", preview_tokens, text, count=1)
                except Exception:
                    pass
            if len(text) > 220:
                text = text[:220] + ' …'
            return text
        except Exception:
            return str(value)

    def _render_phases(body: ctk.CTkFrame):
        if not phases_info:
            ctk.CTkLabel(body, text=app._t('Keine Phaseninformationen verfügbar'),
                         font=ctk.CTkFont(*app.get_typography('body')),
                         text_color=app.get_color('text_secondary')).pack(anchor='w')
            return

        def _phase_counts(phase_issues: List[Dict[str, Any]]) -> Dict[str, int]:
            counts = {'critical': 0, 'major': 0, 'minor': 0}
            try:
                for issue in phase_issues:
                    sev = str(issue.get('severity', '')).lower()
                    if sev in counts:
                        counts[sev] += 1
            except Exception:
                pass
            return counts

        def _phase_status(details: Dict[str, Any] | None, phase_issues: List[Dict[str, Any]]):
            counts = _phase_counts(phase_issues)
            total_from_details = None
            if isinstance(details, dict):
                total_from_details = details.get('issue_total')
                if total_from_details is not None:
                    try:
                        total_from_details = int(total_from_details)
                    except Exception:
                        total_from_details = None
            total_issues = total_from_details if total_from_details is not None else sum(counts.values())
            risk_score = None
            suggestions = None
            if isinstance(details, dict):
                risk_score = details.get('risk_score')
                suggestions = details.get('suggestions')
            color_token = 'success'
            status_text = app._t('Keine Befunde in dieser Phase')
            if total_issues and total_issues > 0:
                if counts.get('critical'):
                    color_token = 'error'
                    status_text = app._t('Kritische Befunde vorhanden')
                elif counts.get('major'):
                    color_token = 'warning'
                    status_text = app._t('Schwerwiegende Befunde vorhanden')
                else:
                    color_token = 'info'
                    status_text = app._t('Hinweise vorhanden')
            elif isinstance(risk_score, (int, float)):
                # Detaillierte Risiko-Stufen für bessere UX
                if risk_score >= 90:
                    color_token = 'error'
                    status_text = app._t('Kritisches Risiko – Sofortige Prüfung erforderlich')
                elif risk_score >= 70:
                    color_token = 'error'
                    status_text = app._t('Hohes Risiko – Überarbeitung empfohlen')
                elif risk_score >= 50:
                    color_token = 'warning'
                    status_text = app._t('Erhöhtes Risiko – Überprüfung ratsam')
                elif risk_score >= 30:
                    color_token = 'warning'
                    status_text = app._t('Moderates Risiko – Kleinere Korrekturen')
                elif risk_score > 0:
                    color_token = 'info'
                    status_text = app._t('Niedriges Risiko – Qualität gut')
                else:
                    color_token = 'success'
                    status_text = app._t('Exzellente Qualität – Kein Risiko')
            elif suggestions:
                color_token = 'info'
                status_text = app._t('Empfehlungen verfügbar')
            return color_token, status_text, total_issues, counts, risk_score, suggestions

        def _metrics_caption(total_issues, counts, risk_score, suggestions):
            parts: List[str] = []
            try:
                if total_issues is not None:
                    parts.append(app._t('Befunde') + f": {int(total_issues)}")
            except Exception:
                pass
            
            # Detaillierte Severity-Counts mit Icons
            if counts.get('critical'):
                parts.append(f"🔴 {app._t('Kritisch')}: {counts['critical']}")
            if counts.get('major'):
                parts.append(f"🟠 {app._t('Schwerwiegend')}: {counts['major']}")
            if counts.get('minor'):
                parts.append(f"🔵 {app._t('Leicht')}: {counts['minor']}")
            
            # Risiko-Score mit visuellem Indikator
            if isinstance(risk_score, (int, float)):
                risk_icon = '🔴' if risk_score >= 70 else '🟡' if risk_score >= 50 else '🟢'
                parts.append(f"{risk_icon} {app._t('Risiko')}: {risk_score:.0f}/100")
            
            if suggestions:
                parts.append(f"💡 {app._t('Empfehlungen')}: {suggestions}")
            
            return ' | '.join(parts)

        # Hole Phasen-Namen aus analysis_results (falls vorhanden)
        phase_names = data.get('phase_names', {}) if isinstance(data, dict) else {}
        
        phase_order: List[Tuple[str, str, str]] = [
            ('phase1', 
             phase_names.get('phase1', app._t('Phase 1 – Format & Struktur')),
             app._t('Prüft Platzhalter, URLs, E-Mails und strukturelle Elemente auf Konsistenz.')),
            ('phase2', 
             phase_names.get('phase2', app._t('Phase 2 – Inhalt & Konsistenz')),
             app._t('Analysiert Zahlen, Einheiten, Glossar-Begriffe und Eigennamen auf Übereinstimmung.')),
            ('phase3', 
             phase_names.get('phase3', app._t('Phase 3 – Semantik & Grammatik')),
             app._t('Überprüft Lesbarkeit, Rechtschreibung und grammatikalische Strukturen.')),
            ('consolidation', 
             phase_names.get('consolidation', app._t('Konsolidierung')),
             app._t('Bewertet alle Befunde und berechnet einen Gesamt-Risiko-Score.')),
            ('recommendations', 
             phase_names.get('recommendations', app._t('Empfehlungen')),
             app._t('Automatisch generierte Verbesserungsvorschläge basierend auf der Analyse.'))
        ]
        token_map = {
            'issue_total': app._t('Anzahl Befunde'),
            'phase_specific': app._t('Phasenspezifische Befunde'),
            'total': app._t('Gesamtbefunde'),
            'risk_score': app._t('Risiko-Score'),
            'suggestions': app._t('Empfehlungen')
        }
        rendered_keys: set[str] = set()

        def _open_findings(phase_key: str, severity_hint: str | None):
            view_state['phase_filter'] = phase_key
            view_state['pending_severity'] = severity_hint
            _set_mode('findings')

        def _render_phase_section(key: str, heading: str, description: str):
            rendered_keys.add(key)
            details = phases_info.get(key)
            issues = phase_issue_lists.get(key, []) if key in phase_issue_lists else []
            if not details and not issues:
                return
            color_token, status_text, total_issues, counts, risk_score, suggestions = _phase_status(details if isinstance(details, dict) else None, issues)
            metrics_caption = _metrics_caption(total_issues, counts, risk_score, suggestions)
            severity_hint = 'critical' if counts.get('critical') else 'major' if counts.get('major') else None
            phase_key = key

            section_frame = ctk.CTkFrame(body,
                                         fg_color=app.get_color('surface'),
                                         corner_radius=radius_md,
                                         border_width=1,
                                         border_color=app.get_color('surface_border'))
            section_frame.pack(fill='x', pady=(0, spacing_md))

            header_frame = ctk.CTkFrame(section_frame, fg_color=app.get_color('transparent'))
            header_frame.pack(fill='x', padx=spacing_md, pady=(spacing_sm, spacing_sm))

            title_container = ctk.CTkFrame(header_frame, fg_color=app.get_color('transparent'))
            title_container.pack(side='left', fill='x', expand=True)

            title_row = ctk.CTkFrame(title_container, fg_color=app.get_color('transparent'))
            title_row.pack(fill='x')

            indicator = ctk.CTkFrame(title_row, width=14, height=14, corner_radius=7,
                                     fg_color=app.get_color(color_token))
            indicator.pack(side='left', pady=(spacing_sm//4, spacing_sm//4))
            try:
                indicator.pack_propagate(False)
            except Exception:
                pass

            heading_lbl = ctk.CTkLabel(title_row, text=heading,
                                       font=ctk.CTkFont(*app.get_typography('subheading')),
                                       text_color=app.get_color('text_primary'))
            heading_lbl.pack(side='left', padx=(spacing_sm, 0))

            status_lbl = ctk.CTkLabel(title_container, text=status_text,
                                      font=ctk.CTkFont(*app.get_typography('caption')),
                                      text_color=app.get_color(color_token),
                                      justify='left')
            status_lbl.pack(anchor='w', pady=(spacing_sm//2, 0))
            if metrics_caption:
                ctk.CTkLabel(title_container, text=metrics_caption,
                             font=ctk.CTkFont(*app.get_typography('caption')),
                             text_color=app.get_color('text_secondary'),
                             justify='left',
                             wraplength=wrap_length).pack(anchor='w', pady=(spacing_sm//4, 0))

            # Spezial-Behandlung für Phase 4: Risiko-Score-Visualisierung
            if key == 'consolidation' and isinstance(risk_score, (int, float)):
                risk_visual_frame = ctk.CTkFrame(section_frame, fg_color=app.get_color('surface_hover'), corner_radius=radius_sm)
                risk_visual_frame.pack(fill='x', padx=spacing_md, pady=(spacing_sm, spacing_sm))
                
                # Risiko-Header
                risk_header = ctk.CTkFrame(risk_visual_frame, fg_color=app.get_color('transparent'))
                risk_header.pack(fill='x', padx=spacing_md, pady=(spacing_sm, 0))
                
                ctk.CTkLabel(
                    risk_header,
                    text=app._t('Gesamtrisiko-Bewertung'),
                    font=ctk.CTkFont(*app.get_typography('label_bold')),
                    text_color=app.get_color('text_primary')
                ).pack(side='left')
                
                # Risiko-Score mit Farbe
                risk_color = app.get_color('error') if risk_score >= 70 else app.get_color('warning') if risk_score >= 50 else app.get_color('info')
                ctk.CTkLabel(
                    risk_header,
                    text=f"{int(risk_score)}/100",
                    font=ctk.CTkFont(*app.get_typography('heading')),
                    text_color=risk_color
                ).pack(side='right')
                
                # Progress-Bar für visuelles Feedback
                risk_bar_container = ctk.CTkFrame(risk_visual_frame, fg_color=app.get_color('transparent'))
                risk_bar_container.pack(fill='x', padx=spacing_md, pady=(spacing_sm, spacing_sm))
                
                risk_bar = ctk.CTkProgressBar(risk_bar_container, height=16, progress_color=risk_color)
                risk_bar.pack(fill='x')
                risk_bar.set(min(risk_score / 100, 1.0))
                
                # Risiko-Beschreibung
                risk_desc_map = {
                    (90, 100): app._t('🔴 Kritisch: Mehrere schwerwiegende Probleme gefunden'),
                    (70, 89): app._t('🟠 Hoch: Signifikante Qualitätsprobleme vorhanden'),
                    (50, 69): app._t('🟡 Erhöht: Einige Verbesserungen empfohlen'),
                    (30, 49): app._t('🔵 Moderat: Kleinere Optimierungen möglich'),
                    (1, 29): app._t('🟢 Niedrig: Gute Qualität mit wenigen Hinweisen'),
                    (0, 0): app._t('✅ Exzellent: Keine Probleme gefunden')
                }
                
                risk_desc = ''
                for (low, high), desc in risk_desc_map.items():
                    if low <= risk_score <= high:
                        risk_desc = desc
                        break
                
                if risk_desc:
                    ctk.CTkLabel(
                        risk_visual_frame,
                        text=risk_desc,
                        font=ctk.CTkFont(*app.get_typography('body')),
                        text_color=app.get_color('text_secondary')
                    ).pack(padx=spacing_md, pady=(0, spacing_sm), anchor='w')

            actions = ctk.CTkFrame(header_frame, fg_color=app.get_color('transparent'))
            actions.pack(side='right')

            view_btn = ctk.CTkButton(actions,
                                     text=app._t('Befunde anzeigen'),
                                     width=140,
                                     height=28,
                                     fg_color=app.get_color('primary'),
                                     hover_color=app.get_color('primary_hover'),
                                     text_color=app.get_color('text_inverse'),
                                     command=lambda _k=key, _sev=severity_hint: _open_findings(_k, _sev))
            view_btn.pack(side='right')

            toggle_btn = ctk.CTkButton(actions,
                                       text=app._t('Details anzeigen'),
                                       width=130,
                                       height=28,
                                       fg_color=app.get_color('surface_hover'),
                                       hover_color=app.get_color('surface_hover'),
                                       text_color=app.get_color('text_primary'))
            toggle_btn.pack(side='right', padx=(0, spacing_sm))

            content_holder = ctk.CTkFrame(section_frame,
                                          fg_color=app.get_color('surface_hover'),
                                          corner_radius=radius_md)
            content_state = {'built': False, 'visible': False}

            def _build_content():
                if content_state['built']:
                    return
                content_state['built'] = True
                inner = ctk.CTkFrame(content_holder, fg_color=app.get_color('transparent'))
                inner.pack(fill='x', padx=spacing_md, pady=spacing_md)
                if description:
                    ctk.CTkLabel(inner,
                                 text=description,
                                 font=ctk.CTkFont(*app.get_typography('caption')),
                                 text_color=app.get_color('text_secondary'),
                                 justify='left',
                                 wraplength=wrap_length).pack(anchor='w', pady=(0, spacing_sm))
                if phase_key == 'phase3':
                    grammar_lines: List[str] = []
                    if grammar_used:
                        grammar_lines.append(app._t('Aktiv') + ': ' + ", ".join(grammar_used))
                    if grammar_disabled:
                        grammar_lines.append(app._t('Deaktiviert') + ': ' + ", ".join(grammar_disabled))
                    if grammar_cache_hit:
                        grammar_lines.append(app._t('Cache-Treffer: Ergebnisse aus dem Zwischenspeicher.'))
                    if grammar_force:
                        grammar_lines.append(app._t('Die Grammatikprüfung ist durch die Konfiguration erzwungen.'))
                    if grammar_lines:
                        grammar_card = ctk.CTkFrame(inner,
                                                    fg_color=app.get_color('surface'),
                                                    corner_radius=radius_md,
                                                    border_width=1,
                                                    border_color=app.get_color('surface_border'))
                        grammar_card.pack(fill='x', pady=(0, spacing_sm))
                        ctk.CTkLabel(grammar_card,
                                     text=app._t('Grammar Checker Status'),
                                     font=ctk.CTkFont(*app.get_typography('label_bold')),
                                     text_color=app.get_color('text_primary')).pack(anchor='w', padx=spacing_md, pady=(spacing_sm, spacing_sm//2))
                        for line in grammar_lines:
                            ctk.CTkLabel(grammar_card,
                                         text=line,
                                         font=ctk.CTkFont(*app.get_typography('caption')),
                                         text_color=app.get_color('text_secondary'),
                                         justify='left',
                                         wraplength=wrap_length).pack(anchor='w', padx=spacing_md, pady=(0, spacing_sm//2))
                total_counts = sum(counts.values())
                metrics: List[Tuple[str, str, str]] = []
                total_display = total_issues if total_issues is not None else total_counts
                if total_display is not None:
                    try:
                        metrics.append((app._t('Befunde gesamt'), f"{int(total_display)}", 'text_primary'))
                    except Exception:
                        metrics.append((app._t('Befunde gesamt'), str(total_display), 'text_primary'))
                if counts.get('critical'):
                    metrics.append((app._t('Kritisch'), str(counts.get('critical', 0)), 'error'))
                if counts.get('major'):
                    metrics.append((app._t('Schwerwiegend'), str(counts.get('major', 0)), 'warning'))
                if counts.get('minor'):
                    metrics.append((app._t('Leicht'), str(counts.get('minor', 0)), 'info'))
                if isinstance(risk_score, (int, float)):
                    if risk_score >= 80:
                        risk_token = 'error'
                    elif risk_score >= 50:
                        risk_token = 'warning'
                    else:
                        risk_token = 'info'
                    metrics.append((app._t('Risiko-Score'), f"{risk_score:.0f}", risk_token))
                if suggestions:
                    metrics.append((app._t('Empfehlungen'), str(suggestions), 'info'))

                if metrics:
                    metrics_row = ctk.CTkFrame(inner, fg_color=app.get_color('transparent'))
                    metrics_row.pack(fill='x', pady=(0, spacing_sm))
                    for idx, (label_txt, value_txt, token) in enumerate(metrics):
                        card = ctk.CTkFrame(metrics_row,
                                            fg_color=app.get_color('surface'),
                                            corner_radius=radius_md,
                                            border_width=1,
                                            border_color=app.get_color('surface_border'))
                        card.pack(side='left', padx=(0 if idx == 0 else spacing_sm, 0), pady=(0, spacing_sm))
                        ctk.CTkLabel(card,
                                     text=label_txt,
                                     font=ctk.CTkFont(*app.get_typography('caption')),
                                     text_color=app.get_color('text_secondary')).pack(anchor='w', padx=spacing_sm, pady=(spacing_sm//2, 0))
                        value_color = app.get_color(token) if token in {'error', 'warning', 'info', 'success'} else app.get_color('text_primary')
                        ctk.CTkLabel(card,
                                     text=value_txt,
                                     font=ctk.CTkFont(*app.get_typography('label_bold')),
                                     text_color=value_color).pack(anchor='w', padx=spacing_sm, pady=(0, spacing_sm))
                if isinstance(details, dict):
                    info_frame = ctk.CTkFrame(inner, fg_color=app.get_color('transparent'))
                    info_frame.pack(fill='x', pady=(0, spacing_sm))
                    for d_key, label_text in token_map.items():
                        if d_key not in details:
                            continue
                        value = details.get(d_key)
                        if value is None:
                            continue
                        row = ctk.CTkFrame(info_frame, fg_color=app.get_color('transparent'))
                        row.pack(fill='x', pady=(0, spacing_sm//2))
                        ctk.CTkLabel(row, text=label_text,
                                     font=ctk.CTkFont(*app.get_typography('body')),
                                     text_color=app.get_color('text_secondary')).pack(side='left')
                        val_txt = f"{value:.2f}" if isinstance(value, float) and d_key == 'risk_score' else str(value)
                        chip = ctk.CTkFrame(row,
                                            fg_color=app.get_color('surface'),
                                            corner_radius=radius_md,
                                            border_width=1,
                                            border_color=app.get_color('surface_border'))
                        chip.pack(side='right')
                        ctk.CTkLabel(chip, text=val_txt,
                                     font=ctk.CTkFont(*app.get_typography('label_bold')),
                                     text_color=app.get_color('text_primary')).pack(padx=spacing_sm, pady=spacing_sm//2)
                if issues:
                    issues_frame = ctk.CTkFrame(inner, fg_color=app.get_color('surface'))
                    issues_frame.pack(fill='x', pady=(0, spacing_sm))
                    ctk.CTkLabel(issues_frame, text=app._t('Beispiele (max. 3)'),
                                 font=ctk.CTkFont(*app.get_typography('caption')),
                                 text_color=app.get_color('text_secondary')).pack(anchor='w', padx=spacing_md, pady=(spacing_sm, spacing_sm//2))
                    for issue in issues[:3]:
                        msg_raw = issue.get('message') or issue.get('code') or app._t('Ohne Beschreibung')
                        formatted_msg = _format_issue_text(msg_raw)
                        target_preview, target_binary = _format_issue_excerpt(issue.get('target_excerpt') or issue.get('target_text') or issue.get('target'))
                        source_preview, source_binary = _format_issue_excerpt(issue.get('source_excerpt') or issue.get('source_text') or issue.get('source'))
                        sev = (issue.get('severity') or 'info').lower()
                        color_token_issue = 'warning' if sev == 'major' else 'error' if sev == 'critical' else 'info'
                        entry = ctk.CTkFrame(issues_frame, fg_color=app.get_color('transparent'))
                        entry.pack(fill='x', padx=spacing_md, pady=(0, spacing_sm//2))
                        bullet = ctk.CTkLabel(entry,
                                               text='•',
                                               font=ctk.CTkFont(*app.get_typography('body')),
                                               text_color=app.get_color(color_token_issue))
                        bullet.pack(side='left', padx=(0, spacing_sm//2))
                        text_container = ctk.CTkFrame(entry, fg_color=app.get_color('transparent'))
                        text_container.pack(side='left', fill='x', expand=True)
                        primary_text = target_preview or formatted_msg or app._t('Ohne Beschreibung')
                        ctk.CTkLabel(text_container, text=primary_text,
                                     font=ctk.CTkFont(*app.get_typography('body')),
                                     text_color=app.get_color('text_primary'),
                                     justify='left', wraplength=wrap_length).pack(anchor='w')
                        if target_binary:
                            ctk.CTkLabel(text_container,
                                         text=app._t('Keine Zieltext-Vorschau (binäre Datei)'),
                                         font=ctk.CTkFont(*app.get_typography('caption')),
                                         text_color=app.get_color('text_secondary'),
                                         justify='left', wraplength=wrap_length).pack(anchor='w')
                        if source_binary and not source_preview:
                            ctk.CTkLabel(text_container,
                                         text=app._t('Keine Quellen-Vorschau (binäre Datei)'),
                                         font=ctk.CTkFont(*app.get_typography('caption')),
                                         text_color=app.get_color('text_secondary'),
                                         justify='left', wraplength=wrap_length).pack(anchor='w')
                        if source_preview:
                            ctk.CTkLabel(text_container,
                                         text=app._t('Quelle') + ': ' + source_preview,
                                         font=ctk.CTkFont(*app.get_typography('caption')),
                                         text_color=app.get_color('text_secondary'),
                                         justify='left', wraplength=wrap_length).pack(anchor='w')
                        if target_preview and formatted_msg and target_preview != formatted_msg:
                            ctk.CTkLabel(text_container, text=formatted_msg,
                                         font=ctk.CTkFont(*app.get_typography('caption')),
                                         text_color=app.get_color('text_secondary'),
                                         justify='left', wraplength=wrap_length).pack(anchor='w')
                        elif not target_preview and formatted_msg:
                            ctk.CTkLabel(text_container, text=formatted_msg,
                                         font=ctk.CTkFont(*app.get_typography('body')),
                                         text_color=app.get_color('text_primary'),
                                         justify='left', wraplength=wrap_length).pack(anchor='w')
                        code_value = issue.get('code') or ''
                        if code_value:
                            ctk.CTkLabel(text_container, text=app._t('Regel') + f": {code_value}",
                                         font=ctk.CTkFont(*app.get_typography('caption')),
                                         text_color=app.get_color(color_token_issue)).pack(anchor='w')
                if not issues:
                    ctk.CTkLabel(inner,
                                 text=app._t('Keine Befunde für diese Phase'),
                                 font=ctk.CTkFont(*app.get_typography('body')),
                                 text_color=app.get_color('text_secondary'),
                                 justify='left').pack(anchor='w')

            def _toggle_section():
                section_open = not content_state['visible']
                content_state['visible'] = section_open
                if section_open:
                    _build_content()
                    content_holder.pack(fill='x', padx=spacing_md, pady=(0, spacing_md))
                    toggle_btn.configure(text=app._t('Details verbergen'))
                else:
                    try:
                        content_holder.pack_forget()
                    except Exception:
                        pass
                    toggle_btn.configure(text=app._t('Details anzeigen'))

            toggle_btn.configure(command=_toggle_section)
            title_container.bind('<Button-1>', lambda _e: _toggle_section())
            title_row.bind('<Button-1>', lambda _e: _toggle_section())
            heading_lbl.bind('<Button-1>', lambda _e: _toggle_section())
            status_lbl.bind('<Button-1>', lambda _e: _toggle_section())

        for key, heading, description in phase_order:
            _render_phase_section(key, heading, description)

        remaining = [k for k in phases_info.keys() if k not in rendered_keys]
        for key in remaining:
            details = phases_info.get(key) or {}
            heading = details.get('title') if isinstance(details, dict) else None
            if not heading:
                heading = (app._t('Phase') + f" {key.replace('phase', '')}") if key.startswith('phase') else key
            description = details.get('description') if isinstance(details, dict) else ''
            _render_phase_section(key, heading, description or '')

    def _render_findings(body: ctk.CTkFrame):
        # Game Changer 2: Statistik-Dashboard vor Findings anzeigen
        _render_statistics_dashboard(body)
        
        # Re-use bestehendes Findings UI unten – hier nur Einhängen
        print(f"DEBUG _render_findings: Called, about to render findings block with {len(findings)} findings")
        _render_findings_block(body)
        print(f"DEBUG _render_findings: Finished rendering findings block")
    
    def _render_statistics_dashboard(parent):
        """Game Changer 2: Visuelles Statistik-Dashboard mit Fehlerverteilung."""
        from collections import Counter
        
        dashboard = ctk.CTkFrame(
            parent,
            fg_color=app.get_color('surface'),
            corner_radius=radius_md,
            border_width=1,
            border_color=app.get_color('surface_border')
        )
        dashboard.pack(fill='x', padx=spacing_lg, pady=(0, spacing_lg))
        
        # Titel
        title_label = ctk.CTkLabel(
            dashboard,
            text=app._t('Statistik-Übersicht'),
            font=ctk.CTkFont(*app.get_typography('heading')),
            text_color=app.get_color('text_primary')
        )
        title_label.pack(anchor='w', padx=spacing_lg, pady=(spacing_lg, spacing_sm))
        
        # Grid für Statistiken
        stats_grid = ctk.CTkFrame(dashboard, fg_color=app.get_color('transparent'))
        stats_grid.pack(fill='both', padx=spacing_lg, pady=(0, spacing_lg))
        stats_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        # 1. Severity-Verteilung
        severity_counts = Counter(str(f.get('severity', '')).lower() for f in findings)
        sev_frame = ctk.CTkFrame(stats_grid, fg_color=app.get_color('surface_hover'), corner_radius=radius_sm)
        sev_frame.grid(row=0, column=0, sticky='nsew', padx=(0, spacing_sm), pady=0)
        
        ctk.CTkLabel(
            sev_frame,
            text=app._t('Nach Schweregrad'),
            font=ctk.CTkFont(*app.get_typography('label_bold')),
            text_color=app.get_color('text_secondary')
        ).pack(anchor='w', padx=spacing_md, pady=(spacing_md, spacing_sm))
        
        # Balken für Severity
        for sev, count in [('critical', severity_counts.get('critical', 0)), 
                           ('major', severity_counts.get('major', 0)), 
                           ('minor', severity_counts.get('minor', 0))]:
            sev_row = ctk.CTkFrame(sev_frame, fg_color=app.get_color('transparent'))
            sev_row.pack(fill='x', padx=spacing_md, pady=(0, spacing_sm))
            
            sev_label_map = {'critical': 'Kritisch', 'major': 'Schwerwiegend', 'minor': 'Geringfügig'}
            sev_color_map = {'critical': 'error', 'major': 'warning', 'minor': 'info'}
            
            label = ctk.CTkLabel(
                sev_row,
                text=f"{sev_label_map.get(sev, sev)}: {count}",
                font=ctk.CTkFont(*app.get_typography('caption')),
                text_color=app.get_color('text_primary'),
                width=120,
                anchor='w'
            )
            label.pack(side='left')
            
            # Progressbar als visuelle Darstellung
            if len(findings) > 0:
                bar = ctk.CTkProgressBar(sev_row, height=12, progress_color=app.get_color(sev_color_map.get(sev, 'info')))
                bar.pack(side='left', fill='x', expand=True)
                bar.set(count / len(findings))
        
        # 2. Kategorie-Verteilung
        category_counts = Counter(f.get('category', 'other') for f in findings)
        cat_frame = ctk.CTkFrame(stats_grid, fg_color=app.get_color('surface_hover'), corner_radius=radius_sm)
        cat_frame.grid(row=0, column=1, sticky='nsew', padx=(spacing_sm, spacing_sm), pady=0)
        
        ctk.CTkLabel(
            cat_frame,
            text=app._t('Nach Kategorie'),
            font=ctk.CTkFont(*app.get_typography('label_bold')),
            text_color=app.get_color('text_secondary')
        ).pack(anchor='w', padx=spacing_md, pady=(spacing_md, spacing_sm))
        
        cat_labels = {
            'placeholders': 'Platzhalter',
            'references': 'Verweise',
            'whitespace': 'Leerzeichen',
            'structure': 'Struktur',
            'html': 'HTML',
            'terminology': 'Terminologie',
            'security': 'Sicherheit',
            'completeness': 'Vollständigkeit',
            'formatting': 'Formatierung',
            'typography': 'Typografie',
            'consistency': 'Konsistenz',
            'other': 'Sonstige'
        }
        
        # Top 5 Kategorien
        top_categories = category_counts.most_common(5)
        for cat, count in top_categories:
            cat_row = ctk.CTkFrame(cat_frame, fg_color=app.get_color('transparent'))
            cat_row.pack(fill='x', padx=spacing_md, pady=(0, spacing_sm))
            
            label = ctk.CTkLabel(
                cat_row,
                text=f"{cat_labels.get(cat, cat.title())}: {count}",
                font=ctk.CTkFont(*app.get_typography('caption')),
                text_color=app.get_color('text_primary'),
                width=140,
                anchor='w'
            )
            label.pack(side='left')
            
            if len(findings) > 0:
                bar = ctk.CTkProgressBar(cat_row, height=12)
                bar.pack(side='left', fill='x', expand=True)
                bar.set(count / len(findings))
        
        # 3. Phasen-Verteilung
        phase_counts = Counter(f.get('phase', 'unknown') for f in findings)
        phase_frame = ctk.CTkFrame(stats_grid, fg_color=app.get_color('surface_hover'), corner_radius=radius_sm)
        phase_frame.grid(row=0, column=2, sticky='nsew', padx=(spacing_sm, 0), pady=0)
        
        ctk.CTkLabel(
            phase_frame,
            text=app._t('Nach Phase'),
            font=ctk.CTkFont(*app.get_typography('label_bold')),
            text_color=app.get_color('text_secondary')
        ).pack(anchor='w', padx=spacing_md, pady=(spacing_md, spacing_sm))
        
        phase_label_map = {
            'phase1': 'Phase 1: Format',
            'phase2': 'Phase 2: Inhalt',
            'phase3': 'Phase 3: Semantik'
        }
        
        for phase in ['phase1', 'phase2', 'phase3']:
            count = phase_counts.get(phase, 0)
            phase_row = ctk.CTkFrame(phase_frame, fg_color=app.get_color('transparent'))
            phase_row.pack(fill='x', padx=spacing_md, pady=(0, spacing_sm))
            
            label = ctk.CTkLabel(
                phase_row,
                text=f"{phase_label_map.get(phase, phase)}: {count}",
                font=ctk.CTkFont(*app.get_typography('caption')),
                text_color=app.get_color('text_primary'),
                width=150,
                anchor='w'
            )
            label.pack(side='left')
            
            if len(findings) > 0:
                bar = ctk.CTkProgressBar(phase_row, height=12)
                bar.pack(side='left', fill='x', expand=True)
                bar.set(count / len(findings))

    def _render_findings(body: ctk.CTkFrame):
        # Re-use bestehendes Findings UI unten – hier nur Einhängen
        print(f"DEBUG _render_findings: Called, about to render findings block with {len(findings)} findings")
        _render_findings_block(body)
        print(f"DEBUG _render_findings: Finished rendering findings block")

    def _rerender_body():
        _clear_body()
        mode = view_state['mode']
        body = ctk.CTkFrame(body_container, fg_color=app.get_color('transparent'))
        body.pack(fill='both', expand=True)
        if mode == 'overview':
            _render_overview(body)
        elif mode == 'phases':
            _render_phases(body)
        else:
            _render_findings(body)

    # Hilfs-Renderer aus bestehendem Code extrahiert -------------------------
    def _render_score_block(parent):
        # Prominente Score-Card mit modernem Design
        score_frame = ctk.CTkFrame(parent, fg_color=app.get_color('surface'), corner_radius=radius_md,
                                   border_width=2, border_color=app.get_color('primary'))
        score_frame.pack(fill='x', pady=(0, spacing_lg))
        score_token = 'success'
        if isinstance(raw_score, (int, float)):
            if raw_score < 50:
                score_token = 'error'
            elif raw_score < 75:
                score_token = 'warning'
        try:
            # Header
            header_row = ctk.CTkFrame(score_frame, fg_color=app.get_color('transparent'))
            header_row.pack(fill='x', padx=spacing_xl, pady=(spacing_xl, spacing_sm))
            ctk.CTkLabel(header_row,
                         text=app._t('Gesamtergebnis'),
                         font=ctk.CTkFont(*app.get_typography('subheading')),
                         text_color=app.get_color('text_secondary')).pack(anchor='w')
            
            # Großer prominenter Score
            score_display_frame = ctk.CTkFrame(score_frame, fg_color=app.get_color('transparent'))
            score_display_frame.pack(fill='x', padx=spacing_xl, pady=(0, spacing_md))
            ctk.CTkLabel(score_display_frame,
                         text=score_view,
                         font=ctk.CTkFont(size=48, weight='bold'),
                         text_color=app.get_color(score_token)).pack(anchor='w')
        except Exception:
            pass
        if isinstance(score_pct, (int, float)):
            try:
                score_bar_frame = ctk.CTkFrame(score_frame, fg_color=app.get_color('transparent'))
                score_bar_frame.pack(fill='x', padx=spacing_xl, pady=(0, spacing_md))
                score_bar = ctk.CTkProgressBar(score_bar_frame, height=20, corner_radius=10,
                                              progress_color=app.get_color(score_token))
                score_bar.pack(fill='x')
                score_bar.set(score_pct/100)
            except Exception:
                pass
        # Breakdown
        try:
            sub_scores = []
            grade = summary.get('quality_grade') if isinstance(summary, dict) else None
            # Nutzerfreundliche Bezeichnungen + Kurzbeschreibung
            label_map = {
                'numeric_consistency_score': (
                    app._t('Numerische Konsistenz'),
                    app._t('Stimmen Zahlen, Datumswerte und Maße überein?')
                ),
                'length_balance_score': (
                    app._t('Längenbalancierung'),
                    app._t('Ungewöhnliche Längenabweichungen zwischen Quelle und Übersetzung?')
                ),
                'translation_completeness_score': (
                    app._t('Übersetzungs-Vollständigkeit'),
                    app._t('Sind alle Segmente vollständig übertragen?')
                ),
                'untranslated_completeness_score': (
                    app._t('Anteil übersetzter Segmente'),
                    app._t('Wie viele Segmente sind nicht leer / nicht identisch mit der Quelle?')
                )
            }
            for key, view_label in label_map.items():
                val = metrics.get(key)
                if isinstance(view_label, tuple):
                    title, desc = view_label
                else:
                    title, desc = view_label, ''
                if isinstance(val, (int, float)):
                    pct = f"{val*100:.1f}%" if val <= 1 else f"{val:.2f}"
                    sub_scores.append((title, pct, desc))
            if sub_scores or grade:
                breakdown_frame = ctk.CTkFrame(score_frame, fg_color=app.get_color('transparent'))
                breakdown_frame.pack(fill='x', padx=spacing_lg, pady=(0, spacing_lg//2))
                
                # Header mit Grade (ohne Toggle-Button)
                header_row = ctk.CTkFrame(breakdown_frame, fg_color=app.get_color('transparent'))
                header_row.pack(fill='x', pady=(0, spacing_md))
                if grade:
                    ctk.CTkLabel(
                        header_row, 
                        text=app._t('Quality grade') + f": {grade}",
                        font=ctk.CTkFont(*app.get_typography('label_bold')),
                        text_color=app.get_color('text_primary')
                    ).pack(side='left')
                
                # Details immer anzeigen (ohne Accordion)
                details_container = ctk.CTkFrame(breakdown_frame, fg_color=app.get_color('transparent'))
                details_container.pack(fill='x', pady=(spacing_sm, 0))
                
                for title, val_txt, desc in sub_scores:
                    row = ctk.CTkFrame(details_container, fg_color=app.get_color('transparent'))
                    row.pack(fill='x', pady=spacing_sm//2)
                    ctk.CTkLabel(
                        row, 
                        text=title, 
                        font=ctk.CTkFont(*app.get_typography('body')),
                        text_color=app.get_color('text_primary')
                    ).pack(side='left')
                    ctk.CTkLabel(
                        row, 
                        text=val_txt, 
                        font=ctk.CTkFont(*app.get_typography('label_bold')),
                        text_color=app.get_color('text_primary')
                    ).pack(side='right')
                    if desc:
                        ctk.CTkLabel(
                            details_container, 
                            text=desc, 
                            font=ctk.CTkFont(*app.get_typography('caption')),
                            text_color=app.get_color('text_secondary')
                        ).pack(anchor='w', pady=(0, spacing_sm))
        except Exception: pass

    def _render_quick_stats(parent):
        """Zeigt wichtige Schnell-Statistiken in Karten an."""
        stats_container = ctk.CTkFrame(parent, fg_color=app.get_color('transparent'))
        stats_container.pack(fill='x', pady=(0, spacing_lg))
        stats_container.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Statistik-Karte Helfer
        def _stat_card(col, label, value, icon_text=''):
            card = ctk.CTkFrame(stats_container, fg_color=app.get_color('surface_hover'),
                              corner_radius=radius_md, border_width=1,
                              border_color=app.get_color('surface_border'))
            card.grid(row=0, column=col, sticky='nsew', padx=(0 if col==0 else spacing_sm//2, 
                                                               spacing_sm//2 if col<3 else 0))
            
            if icon_text:
                icon_label = ctk.CTkLabel(card, text=icon_text,
                                        font=ctk.CTkFont(size=24),
                                        text_color=app.get_color('primary'))
                icon_label.pack(pady=(spacing_md, spacing_sm//2))
            
            value_label = ctk.CTkLabel(card, text=str(value),
                                     font=ctk.CTkFont(size=28, weight='bold'),
                                     text_color=app.get_color('text_primary'))
            value_label.pack(pady=(spacing_sm if not icon_text else 0, spacing_sm//2))
            
            label_label = ctk.CTkLabel(card, text=label,
                                     font=ctk.CTkFont(*app.get_typography('caption')),
                                     text_color=app.get_color('text_secondary'))
            label_label.pack(pady=(0, spacing_md))
        
        # Statistiken sammeln
        try:
            segment_count = metrics.get('segments_total') or metrics.get('pair_count') or 0
            findings_count = len(findings) if findings else 0
            
            # Sprachpaar
            lang_pair = metrics.get('length_ratio_label', '–')
            if lang_pair == '–':
                src_lang = metrics.get('length_ratio_languages', {}).get('source', 'auto')
                tgt_lang = metrics.get('length_ratio_languages', {}).get('target', 'auto')
                if src_lang != 'auto' and tgt_lang != 'auto':
                    lang_pair = f"{src_lang.upper()}→{tgt_lang.upper()}"
            
            # Zeit
            analysis_time = metrics.get('analysis_time_ms', 0)
            if analysis_time >= 1000:
                time_str = f"{analysis_time/1000:.1f}s"
            else:
                time_str = f"{analysis_time}ms"
            
            # Karten anzeigen
            _stat_card(0, app._t('Segmente'), segment_count, '📄')
            _stat_card(1, app._t('Sprachpaar'), lang_pair, '🌐')
            _stat_card(2, app._t('Befunde'), findings_count, '🔍')
            _stat_card(3, app._t('Analysezeit'), time_str, '⏱')
        except Exception as e:
            app.logger.error(f"Error rendering quick stats: {e}")
    
    def _render_export_actions(parent):
        """Zeigt prominente Export-Buttons für professionelle Berichte."""
        export_frame = ctk.CTkFrame(parent, fg_color=app.get_color('surface'),
                                    corner_radius=radius_md, border_width=1,
                                    border_color=app.get_color('surface_border'))
        export_frame.pack(fill='x', pady=(0, spacing_lg))
        
        # Header
        header_frame = ctk.CTkFrame(export_frame, fg_color=app.get_color('transparent'))
        header_frame.pack(fill='x', padx=spacing_lg, pady=(spacing_md, spacing_sm))
        ctk.CTkLabel(header_frame,
                     text=app._t('Bericht exportieren'),
                     font=ctk.CTkFont(*app.get_typography('subheading')),
                     text_color=app.get_color('text_primary')).pack(side='left')
        ctk.CTkLabel(header_frame,
                     text=app._t('Professioneller Bericht für Kunden'),
                     font=ctk.CTkFont(*app.get_typography('caption')),
                     text_color=app.get_color('text_secondary')).pack(side='right')
        
        # Button Container
        btn_frame = ctk.CTkFrame(export_frame, fg_color=app.get_color('transparent'))
        btn_frame.pack(fill='x', padx=spacing_lg, pady=(0, spacing_md))
        
        # Export-Funktion
        def _do_export(fmt: str):
            try:
                if hasattr(app, '_perform_export') and callable(app._perform_export):
                    app._perform_export(fmt)
                elif hasattr(app, 'reporting') and hasattr(app.reporting, 'perform_export'):
                    app.reporting.perform_export(app, fmt)
                else:
                    _toast(app, app._t('Export-Funktion nicht verfügbar'), 'warning')
            except Exception as e:
                app.logger.error(f"Export error: {e}")
                _toast(app, app._t('Export fehlgeschlagen'), 'error')
        
        # PDF Button (Haupt-Button)
        pdf_btn = ctk.CTkButton(btn_frame,
                                text=app._t('PDF Bericht'),
                                width=140, height=40,
                                fg_color=app.get_color('primary'),
                                hover_color=app.get_color('primary_hover'),
                                text_color=app.get_color('text_inverse'),
                                font=ctk.CTkFont(*app.get_typography('body_bold')),
                                command=lambda: _do_export('pdf'))
        pdf_btn.pack(side='left', padx=(0, spacing_sm))
        
        # Excel Button
        excel_btn = ctk.CTkButton(btn_frame,
                                  text=app._t('Excel Export'),
                                  width=120, height=40,
                                  fg_color=app.get_color('secondary'),
                                  hover_color=app.get_color('secondary_hover'),
                                  text_color=app.get_color('text_inverse'),
                                  font=ctk.CTkFont(*app.get_typography('body')),
                                  command=lambda: _do_export('xlsx'))
        excel_btn.pack(side='left', padx=(0, spacing_sm))
        
        # TXT Button
        txt_btn = ctk.CTkButton(btn_frame,
                                text=app._t('Textdatei'),
                                width=100, height=40,
                                fg_color=app.get_color('surface_hover'),
                                hover_color=app.get_color('surface_border'),
                                text_color=app.get_color('text_primary'),
                                font=ctk.CTkFont(*app.get_typography('body')),
                                command=lambda: _do_export('txt'))
        txt_btn.pack(side='left')
        
        # Info-Text
        info_frame = ctk.CTkFrame(export_frame, fg_color=app.get_color('transparent'))
        info_frame.pack(fill='x', padx=spacing_lg, pady=(0, spacing_md))
        ctk.CTkLabel(info_frame,
                     text=app._t('PDF enthält Score, Befunde und Empfehlungen. Ideal zur Weitergabe an Kunden.'),
                     font=ctk.CTkFont(*app.get_typography('caption')),
                     text_color=app.get_color('text_secondary'),
                     wraplength=400).pack(anchor='w')
    
    def _render_summary_block(parent):
        # Zusammenfassung Kennzahlen
        metrics_rows: List[Tuple[str, str, str, str, str]] = []
        try:
            # DEBUG: Log verfügbare Metriken
            if isinstance(metrics, dict):
                available_keys = list(metrics.keys())
                app.logger.info(f"Available metrics keys: {available_keys}")
            if isinstance(metrics, dict) and metrics:
                def _fmt_pct(v):
                    try:
                        if v is None: return '–'
                        if isinstance(v,(int,float)) and v <= 1: return f"{v*100:.1f}%"
                        return f"{v:.2f}" if isinstance(v,(int,float)) else str(v)
                    except Exception: return str(v)
                def _status_for(metric_key: str, raw_value: Any) -> Tuple[str, str]:
                    try:
                        val = float(raw_value)
                    except Exception:
                        return app._t('Keine Bewertung möglich.'), 'info'
                    if metric_key == 'numeric_consistency':
                        if val >= 0.95:
                            return app._t('Sehr konsistent – keine Auffälligkeiten.'), 'success'
                        if val >= 0.85:
                            return app._t('Leichte Abweichungen – bitte prüfen.'), 'warning'
                        return app._t('Starke Abweichungen – korrigieren erforderlich.'), 'error'
                    if metric_key == 'translated_ratio':
                        if val >= 0.98:
                            return app._t('Fast alle Segmente bearbeitet.'), 'success'
                        if val >= 0.9:
                            return app._t('Einige Segmente offen – nacharbeiten.'), 'warning'
                        return app._t('Viele Segmente unübersetzt.'), 'error'
                    if metric_key == 'avg_length_ratio':
                        expected = metrics.get('length_ratio_expected')
                        tolerance = metrics.get('length_ratio_tolerance')
                        label = metrics.get('length_ratio_label') or app._t('Automatisch erkannt')
                        try:
                            expected = float(expected)
                        except Exception:
                            expected = 1.0
                        try:
                            tolerance = float(tolerance)
                        except Exception:
                            tolerance = 0.05
                        deviation = abs(val - expected)
                        half_tol = tolerance / 2
                        if deviation <= half_tol:
                            return app._t('Im erwarteten Bereich für {label}.').format(label=label), 'success'
                        if deviation <= tolerance:
                            return app._t('Leichte Abweichung für {label} – prüfen.').format(label=label), 'warning'
                        return app._t('Deutliche Abweichung für {label} – Text angleichen.').format(label=label), 'error'
                    if metric_key == 'length_ratio_deviation':
                        if val <= 0.1:
                            return app._t('Gleichmäßige Längenverteilung.'), 'success'
                        if val <= 0.2:
                            return app._t('Uneinheitlich – stichprobenartig prüfen.'), 'warning'
                        return app._t('Sehr ungleich – Qualität prüfen.'), 'error'
                    if metric_key == 'completeness':
                        if val >= 0.99:
                            return app._t('Alle Segmente vollständig.'), 'success'
                        if val >= 0.95:
                            return app._t('Kleine Lücken vorhanden.'), 'warning'
                        return app._t('Mehrere Segmente fehlen.'), 'error'
                    return app._t('Keine Bewertung möglich.'), 'info'

                def _add_row(label: str, value: str, hint: str = '', status: Tuple[str, str] | None = None):
                    status_text, status_token = status if status else (None, 'info')
                    metrics_rows.append((label, value, hint, status_text, status_token))

                if 'numeric_consistency' in metrics:
                    raw_val = metrics.get('numeric_consistency')
                    _add_row(app._t('Numerische Konsistenz'), _fmt_pct(raw_val),
                             app._t('Vergleicht Zahlen, Datumswerte und Maße.'),
                             _status_for('numeric_consistency', raw_val))
                if 'untranslated_ratio' in metrics:
                    translated_ratio_val = None
                    untranslated_ratio_val = None
                    try:
                        untranslated_ratio_val = float(metrics.get('untranslated_ratio') or 0)
                        translated_ratio_val = max(0.0, min(1.0, 1 - untranslated_ratio_val))
                    except Exception:
                        translated_ratio_val = None
                    segments_total = metrics.get('segments_total') or metrics.get('pair_count')
                    segments_translated_val = metrics.get('segments_translated')
                    segments_untranslated_val = metrics.get('segments_untranslated')
                    value_parts: list[str] = []
                    if translated_ratio_val is not None:
                        translated_txt = f"{app._t('Übersetzt')}: {_fmt_pct(translated_ratio_val)}"
                        if isinstance(segments_translated_val, int) and isinstance(segments_total, int) and segments_total > 0:
                            translated_txt += f" ({segments_translated_val}/{segments_total})"
                        value_parts.append(translated_txt)
                    if untranslated_ratio_val is not None:
                        untranslated_txt = f"{app._t('Unübersetzt')}: {_fmt_pct(untranslated_ratio_val)}"
                        if isinstance(segments_untranslated_val, int) and isinstance(segments_total, int) and segments_total > 0:
                            untranslated_txt += f" ({segments_untranslated_val}/{segments_total})"
                        value_parts.append(untranslated_txt)
                    value_txt = ' • '.join(value_parts) if value_parts else _fmt_pct(translated_ratio_val)
                    _add_row(app._t('Übersetzungsquote'), value_txt,
                             app._t('Zeigt Übersetzte und unveränderte Segmente im Vergleich.'),
                             _status_for('translated_ratio', translated_ratio_val))
                length_label = metrics.get('length_ratio_label') or app._t('Automatisch erkannt')
                length_expected = metrics.get('length_ratio_expected')
                length_tol = metrics.get('length_ratio_tolerance')
                length_lower = metrics.get('length_ratio_lower')
                length_upper = metrics.get('length_ratio_upper')
                try:
                    length_expected = float(length_expected)
                except Exception:
                    length_expected = 1.0
                try:
                    length_tol = float(length_tol)
                except Exception:
                    length_tol = 0.05
                try:
                    length_lower = float(length_lower)
                except Exception:
                    length_lower = length_expected - length_tol
                try:
                    length_upper = float(length_upper)
                except Exception:
                    length_upper = length_expected + length_tol
                range_text = f"{length_lower*100:.0f}% – {length_upper*100:.0f}%"
                
                # Sprachpaar immer anzeigen, wenn verfügbar
                if length_label and length_label != f"{app._t('Automatisch erkannt')}->{app._t('Automatisch erkannt')}":
                    _add_row(
                        app._t('Sprachpaar'),
                        length_label,
                        app._t('Erkannte Konfiguration aus Quelle und Ziel.'),
                        None
                    )
                
                if 'avg_length_ratio' in metrics:
                    raw_val = metrics.get('avg_length_ratio')
                    _add_row(
                        app._t('Durchschnittliches Längenverhältnis'),
                        _fmt_pct(raw_val),
                        f"{app._t('Erwarteter Bereich')} ({length_label}): {range_text}",
                        _status_for('avg_length_ratio', raw_val)
                    )
                if 'length_ratio_deviation' in metrics:
                    raw_val = metrics.get('length_ratio_deviation')
                    _add_row(app._t('Variation Länge'), _fmt_pct(raw_val),
                             app._t('Zeigt die Streuung zwischen einzelnen Segmenten.'),
                             _status_for('length_ratio_deviation', raw_val))
                if 'completeness' in metrics and 'untranslated_ratio' not in metrics:
                    raw_val = metrics.get('completeness')
                    _add_row(app._t('Vollständigkeit'), _fmt_pct(raw_val),
                             app._t('Bewertet, ob Segmente nicht leer oder identisch sind.'),
                             _status_for('completeness', raw_val))
        except Exception as e:
            app.logger.error(f"Error building metrics rows: {e}", exc_info=True)
        if metrics_rows:
            inner = _section_card(parent, app._t('Zusammenfassung'))
            for idx, (label, value, hint, status_text, status_token) in enumerate(metrics_rows):
                last_row = idx == len(metrics_rows)-1
                
                # Status-Farben definieren
                if status_token == 'success':
                    border_color = app.get_color('success')
                    bg_color = app.get_color('success_light')
                    value_color = app.get_color('success')
                elif status_token == 'warning':
                    border_color = app.get_color('warning')
                    bg_color = app.get_color('warning_light')
                    value_color = app.get_color('warning')
                elif status_token == 'error':
                    border_color = app.get_color('error')
                    bg_color = app.get_color('error_light')
                    value_color = app.get_color('error')
                else:
                    border_color = app.get_color('surface_border')
                    bg_color = app.get_color('surface_elevated')
                    value_color = app.get_color('text_primary')
                
                # Metric Card mit farbiger Status-Border
                metric_card = ctk.CTkFrame(inner,
                                          fg_color=app.get_color('surface'),
                                          corner_radius=radius_md,
                                          border_width=2,
                                          border_color=border_color)
                metric_card.pack(fill='x', pady=(0, spacing_md if not last_row else 0))
                
                # Header mit Label
                header = ctk.CTkFrame(metric_card, fg_color=app.get_color('transparent'))
                header.pack(fill='x', padx=spacing_md, pady=(spacing_md, spacing_sm))
                ctk.CTkLabel(header,
                             text=label,
                             font=ctk.CTkFont(*app.get_typography('label_bold')),
                             text_color=app.get_color('text_primary')).pack(side='left')
                
                # Großer prominenter Wert
                value_container = ctk.CTkFrame(metric_card, fg_color=app.get_color('transparent'))
                value_container.pack(fill='x', padx=spacing_md, pady=(0, spacing_sm))
                ctk.CTkLabel(value_container,
                             text=value,
                             font=ctk.CTkFont(size=24, weight='bold'),
                             text_color=value_color).pack(anchor='w')
                
                # Status-Bewertung prominent
                if status_text:
                    status_frame = ctk.CTkFrame(metric_card,
                                               fg_color=bg_color,
                                               corner_radius=radius_sm)
                    status_frame.pack(fill='x', padx=spacing_md, pady=(0, spacing_sm))
                    status_label = ctk.CTkLabel(status_frame,
                                                text=status_text,
                                                font=ctk.CTkFont(*app.get_typography('body')),
                                                text_color=value_color,
                                                justify='left',
                                                wraplength=wrap_length)
                    status_label.pack(anchor='w', padx=spacing_sm, pady=spacing_sm)
                
                # Hint als dezente Info
                if hint:
                    ctk.CTkLabel(metric_card,
                                 text=hint,
                                 font=ctk.CTkFont(*app.get_typography('caption')),
                                 text_color=app.get_color('text_secondary'),
                                 justify='left',
                                 wraplength=wrap_length).pack(anchor='w', padx=spacing_md, pady=(0, spacing_md))
            if pair_details:
                try:
                    preview_btn = ctk.CTkButton(
                        inner,
                        text=app._t('Eingelesenen Text anzeigen'),
                        width=240,
                        height=32,
                        fg_color=app.get_color('primary'),
                        hover_color=app.get_color('primary_hover'),
                        text_color=app.get_color('text_inverse'),
                        command=lambda rows=pair_details, snap=metrics: _open_ingest_preview(rows, snap)
                    )
                    preview_btn.pack(anchor='w', pady=(spacing_md, 0))
                except Exception:
                    pass

    def _render_severity_block(parent):
        crit = summary.get('critical') if isinstance(summary, dict) else None
        maj = summary.get('major') if isinstance(summary, dict) else None
        mino = summary.get('minor') if isinstance(summary, dict) else None
        if not any(isinstance(x,int) for x in (crit,maj,mino)):
            return
        sv_inner = _section_card(parent, app._t('Severity'))
        total_s = sum(x for x in [crit, maj, mino] if isinstance(x,int) and x>=0)
        chips_frame = ctk.CTkFrame(sv_inner, fg_color=app.get_color('transparent'))
        chips_frame.pack(fill='x')
        label_defs = [
            (app._t('Critical'), crit, 'error'),
            (app._t('Major'), maj, 'warning'),
            (app._t('Minor'), mino, 'info')
        ]
        for label_txt, current_val, token in label_defs:
            if not isinstance(current_val, int):
                continue
            try:
                share = f"{(current_val/total_s)*100:.0f}%" if total_s else '0%'
            except Exception:
                share = '0%'
            chip = ctk.CTkFrame(chips_frame,
                                 fg_color=app.get_color('surface'),
                                 corner_radius=radius_md,
                                 border_width=1,
                                 border_color=app.get_color(token))
            chip.pack(side='left', padx=(0, spacing_sm), pady=(0, spacing_sm))
            ctk.CTkLabel(chip,
                         text=f"{label_txt}: {current_val} ({share})",
                         font=ctk.CTkFont(*app.get_typography('caption')),
                         text_color=app.get_color('text_primary')).pack(padx=spacing_md//2, pady=spacing_sm//2)
        if total_s:
            ctk.CTkLabel(sv_inner,
                         text=app._t('Total') + f": {total_s}",
                         font=ctk.CTkFont(*app.get_typography('body')),
                         text_color=app.get_color('text_primary')).pack(anchor='w', pady=(0, spacing_sm))
        ctk.CTkLabel(sv_inner,
                     text=app._t('Der Schweregrad hilft bei der Priorisierung:\nKritisch = sofort prüfen, Schwerwiegend = zeitnah klären, Leicht = nach Bedarf anpassen.'),
                     font=ctk.CTkFont(*app.get_typography('caption')),
                     text_color=app.get_color('text_secondary'),
                     justify='left',
                     wraplength=wrap_length).pack(anchor='w')
        # Balken
        if total_s>0:
            bar_container = ctk.CTkFrame(sv_inner, fg_color=app.get_color('transparent'))
            bar_container.pack(fill='x', pady=(spacing_md//2,0))
            for val, token in [ (crit,'error'), (maj,'warning'), (mino,'info') ]:
                if not isinstance(val,int) or val <=0: continue
                seg = ctk.CTkProgressBar(bar_container, height=10)
                seg.pack(side='left', expand=True, fill='x', padx=2)
                try: seg.configure(progress_color=app.get_color(token))
                except Exception: pass
                try: seg.set(val/total_s)
                except Exception: pass

    def _render_guidance_block(parent):
        inner = _section_card(parent, app._t('Hinweise zur Auswertung'), tone='surface_hover')
        guidance_lines = [
            app._t('Das durchschnittliche Längenverhältnis vergleicht die Länge der Übersetzung mit der Quelle. Werte um 1,0 bedeuten ähnliche Textmenge, deutlich höhere oder niedrigere Werte weisen auf gekürzte oder verlängerte Passagen hin.'),
            app._t('Die Übersetzungsquote kombiniert "Übersetzt" und "Unübersetzt"; fehlende Segmente erscheinen zusätzlich als Befunde, damit du sie gezielt nacharbeiten kannst.'),
            app._t('Passen Sprachpaare nicht zum Standard, kannst du in checker_config.json unter quality.thresholds.length.language_pairs eigene Erwartungsbereiche hinterlegen, zum Beispiel für Deutsch->Englisch.'),
            app._t('Nutze den Schweregrad, um zuerst kritische Probleme zu beheben und dich anschließend um schwerwiegende sowie leichte Hinweise zu kümmern.')
        ]
        for line in guidance_lines:
            ctk.CTkLabel(inner,
                         text=line,
                         font=ctk.CTkFont(*app.get_typography('caption')),
                         text_color=app.get_color('text_secondary'),
                         justify='left',
                         wraplength=wrap_length).pack(anchor='w', pady=(0, spacing_sm))

    def _render_grammar_status(parent):
        if not (grammar_used or grammar_disabled or grammar_force or grammar_cache_hit):
            return
        inner = _section_card(parent, app._t('Grammar Checker Status'))
        info_lines: List[str] = []
        if grammar_used:
            info_lines.append(app._t('Aktiv') + ': ' + ", ".join(grammar_used))
        if grammar_disabled:
            info_lines.append(app._t('Deaktiviert') + ': ' + ", ".join(grammar_disabled))
        if grammar_cache_hit:
            info_lines.append(app._t('Cache-Treffer: Ergebnisse aus dem Zwischenspeicher.'))
        if grammar_force:
            info_lines.append(app._t('Hinweis: Die Konfiguration erzwingt derzeit die Grammatikprüfung.'))
        for idx, line in enumerate(info_lines):
            ctk.CTkLabel(inner,
                         text=line,
                         font=ctk.CTkFont(*app.get_typography('caption')),
                         text_color=app.get_color('text_secondary'),
                         anchor='w',
                         justify='left',
                         wraplength=wrap_length).pack(anchor='w', fill='x', pady=(0 if idx else 0, spacing_sm//2))

    # Findings Block (vollständig neu implementiert – Virtualisierung, Sortierung, Counts, Tastatur)
    def _render_findings_block(parent):
        # DEBUG: Check if findings variable is accessible
        print(f"DEBUG _render_findings_block: Called with findings count = {len(findings) if findings else 0}")
        print(f"DEBUG _render_findings_block: findings type = {type(findings)}")
        print(f"DEBUG _render_findings_block: findings list = {findings}")  # NEW: Print entire list
        if findings:
            print(f"DEBUG _render_findings_block: First finding = {findings[0]}")
        
        # If there are no raw findings, show a clear German message and log entry.
        if not findings:
            print("DEBUG: No findings - showing empty message")
            try:
                ctk.CTkLabel(parent,
                             text=app._t('Keine Befunde erkannt') + f" (0)",
                             font=ctk.CTkFont(*app.get_typography('body_bold')),
                             text_color=app.get_color('text_secondary')).pack(anchor='w', pady=(8,0))
            except Exception:
                try:
                    ctk.CTkLabel(parent, text=app._t('Keine Befunde erkannt'),
                                 font=ctk.CTkFont(*app.get_typography('body')),
                                 text_color=app.get_color('text_secondary')).pack(anchor='w')
                except Exception:
                    pass
            try:
                _debug(app, 'Render: no findings to show (raw list empty)')
            except Exception:
                pass
            return
        
        print("DEBUG: Creating findings container")
        container = _section_card(parent, app._t('Findings'))
        print(f"DEBUG: Container created, type={type(container)}")
        controls = ctk.CTkFrame(container, fg_color=app.get_color('transparent'))
        controls.pack(fill='x')
        print("DEBUG: Controls frame created and packed")
        state = {
            'severity': 'ALL',
            'checker': 'ALL',
            'category': 'ALL',  # Quick Win 2: Kategorie-State initialisieren
            'query': '',
            'sort': 'severity',
            'sort_dir': 'asc',
            'selected_index': None,
            'virtual_enabled': False,
            'phase': view_state.get('phase_filter', 'ALL'),
        }
        
        # DEBUG: Log initial state
        print(f"DEBUG: Initial findings state - severity={state['severity']}, phase={state['phase']}, category={state['category']}, checker={state['checker']}")

        def _normalize_phase_key(value: str | None) -> str:
            if not value:
                return ''
            try:
                return re.sub(r'[^a-z0-9]+', '', value.lower())
            except Exception:
                return str(value).lower()
        try:
            if _cfg:
                for k in ('severity','checker','sort','sort_dir'):  # REMOVED 'phase' from config loading
                    val=_cfg.get(f'analysis.ui.findings.{k}')
                    if isinstance(val,str): state[k]=val
                # DEBUG: Log loaded config values
                print(f"DEBUG: Loaded from config - severity={state.get('severity')}, phase={state.get('phase')}, checker={state.get('checker')}")
        except Exception: pass
        # ALWAYS reset phase filter to 'ALL' on render to ensure findings are visible
        state['phase'] = 'ALL'
        view_state['phase_filter'] = 'ALL'
        print(f"DEBUG: Phase filter forced to ALL to ensure findings visibility")
        pending_severity = view_state.pop('pending_severity', None)
        if isinstance(pending_severity, str) and pending_severity:
            state['severity'] = pending_severity

        # Helper: persist
        def _persist():
            try:
                if _cfg:
                    _cfg.set('analysis.ui.findings.severity', state['severity'])
                    _cfg.set('analysis.ui.findings.category', state.get('category', 'ALL'))  # Quick Win 2
                    _cfg.set('analysis.ui.findings.checker', state['checker'])
                    _cfg.set('analysis.ui.findings.sort', state['sort'])
                    _cfg.set('analysis.ui.findings.sort_dir', state['sort_dir'])
                    _cfg.set('analysis.ui.findings.phase', state['phase'])
                    _cfg.set('analysis.ui.findings.grouped', state.get('grouped', False))  # Game Changer 1
            except Exception: pass

        # Severity Filter
        sev_frame=ctk.CTkFrame(controls, fg_color=app.get_color('transparent'))
        sev_frame.pack(side='left')
        ctk.CTkLabel(
            sev_frame,
            text=app._t('Schweregrad'),
            font=ctk.CTkFont(*app.get_typography('caption')),
            text_color=app.get_color('text_secondary')
        ).pack(anchor='w')
        severity_defs=[(app._t('All'),'ALL'),(app._t('Critical'),'critical'),(app._t('Major'),'major'),(app._t('Minor'),'minor')]
        severity_buttons=[]
        def _set_severity(val):
            state['severity']=val; _persist(); _render_list();
            for b,v in severity_buttons:
                try: b.configure(fg_color=app.get_color('primary') if v==val else app.get_color('surface_hover'), text_color=app.get_color('text_inverse') if v==val else app.get_color('text_primary'))
                except Exception: pass
        for lab,val in severity_defs:
            try:
                b=ctk.CTkButton(sev_frame,text=lab,width=92,height=26,fg_color=app.get_color('surface_hover'),hover_color=app.get_color('surface_hover'),text_color=app.get_color('text_primary'),command=lambda _v=val:_set_severity(_v))
                b.pack(side='left', padx=2, pady=(2,0))
                severity_buttons.append((b,val))
            except Exception: continue
        print(f"DEBUG: Severity filter setup complete with {len(severity_buttons)} buttons")

        # Quick Win 2: Kategorie-Filter
        cat_frame=ctk.CTkFrame(controls, fg_color=app.get_color('transparent'))
        cat_frame.pack(side='left', padx=spacing_lg)
        ctk.CTkLabel(
            cat_frame,
            text=app._t('Kategorie'),
            font=ctk.CTkFont(*app.get_typography('caption')),
            text_color=app.get_color('text_secondary')
        ).pack(anchor='w')
        
        # Kategorien aus Findings extrahieren
        categories_in_findings = set()
        for finding in findings:
            cat = finding.get('category', '')
            if cat:
                categories_in_findings.add(cat)
        
        # Kategorie-Labels (nur die vorhandenen)
        cat_labels = {
            'placeholders': 'Platzhalter',
            'references': 'Verweise',
            'whitespace': 'Leerzeichen',
            'structure': 'Struktur',
            'html': 'HTML',
            'terminology': 'Terminologie',
            'security': 'Sicherheit',
            'completeness': 'Vollständigkeit',
            'formatting': 'Formatierung',
            'typography': 'Typografie',
            'consistency': 'Konsistenz',
        }
        
        category_defs = [(app._t('All'), 'ALL')]
        for cat in sorted(categories_in_findings):
            label = cat_labels.get(cat, cat.title())
            category_defs.append((label, cat))
        
        state['category'] = state.get('category', 'ALL')
        category_buttons = []
        
        def _set_category(val):
            state['category'] = val
            _persist()
            _render_list()
            for b, v in category_buttons:
                try:
                    b.configure(
                        fg_color=app.get_color('primary') if v==val else app.get_color('surface_hover'),
                        text_color=app.get_color('text_inverse') if v==val else app.get_color('text_primary')
                    )
                except Exception:
                    pass
        
        for lab, val in category_defs[:6]:  # Max 6 Buttons
            try:
                b = ctk.CTkButton(
                    cat_frame,
                    text=lab,
                    width=85,
                    height=26,
                    fg_color=app.get_color('surface_hover'),
                    hover_color=app.get_color('surface_hover'),
                    text_color=app.get_color('text_primary'),
                    command=lambda _v=val: _set_category(_v)
                )
                b.pack(side='left', padx=2, pady=(2,0))
                category_buttons.append((b, val))
            except Exception:
                continue

        phase_frame=ctk.CTkFrame(controls, fg_color=app.get_color('transparent'))
        phase_frame.pack(side='left', padx=spacing_lg)
        ctk.CTkLabel(phase_frame,text=app._t('Phase'),font=ctk.CTkFont(*app.get_typography('caption')),
                     text_color=app.get_color('text_secondary')).pack(anchor='w')
        phase_buttons: List[Tuple[ctk.CTkButton, str]] = []
        # Hole Phasen-Namen aus analysis_results
        phase_names = data.get('phase_names', {}) if isinstance(data, dict) else {}
        
        phase_label_map = {
            'phase1': phase_names.get('phase1', app._t('Format & Struktur')),
            'phase2': phase_names.get('phase2', app._t('Inhalt & Konsistenz')),
            'phase3': phase_names.get('phase3', app._t('Semantik & Grammatik')),
            'consolidation': phase_names.get('consolidation', app._t('Konsolidierung')),
            'recommendations': phase_names.get('recommendations', app._t('Empfehlungen')),
        }
        
        # Prüfe welche Phasen tatsächlich Daten haben
        available_phase_keys: List[str] = []
        for candidate in ['phase1','phase2','phase3','consolidation','recommendations']:
            if (candidate in phase_issue_lists and phase_issue_lists.get(candidate)) or phases_info.get(candidate):
                available_phase_keys.append(candidate)
        for key in phases_info.keys():
            if key.startswith('phase') and key not in available_phase_keys:
                available_phase_keys.append(key)
        for key in phase_issue_lists.keys():
            if key.startswith('phase') and key not in available_phase_keys and phase_issue_lists.get(key):
                available_phase_keys.append(key)
        phase_button_defs: List[Tuple[str, str]] = [(app._t('All'), 'ALL')]
        for key in available_phase_keys:
            label_base = phase_label_map.get(key, (app._t('Phase') + f" {key.replace('phase', '')}"))
            phase_button_defs.append((label_base, _normalize_phase_key(key)))
        if state['phase'] not in [val for _, val in phase_button_defs]:
            state['phase'] = 'ALL'
            view_state['phase_filter'] = 'ALL'

        def _set_phase(val: str):
            normalized = val if val == 'ALL' else _normalize_phase_key(val)
            state['phase'] = normalized
            view_state['phase_filter'] = normalized
            _persist()
            _render_list()
            for b, v in phase_buttons:
                try:
                    active = (v == normalized)
                    b.configure(fg_color=app.get_color('primary') if active else app.get_color('surface_hover'),
                                text_color=app.get_color('text_inverse') if active else app.get_color('text_primary'))
                except Exception:
                    pass

        for lab, val in phase_button_defs:
            try:
                b = ctk.CTkButton(phase_frame, text=lab, width=90, height=24,
                                   fg_color=app.get_color('surface_hover'), hover_color=app.get_color('surface_hover'),
                                   text_color=app.get_color('text_primary'),
                                   command=lambda _v=val: _set_phase(_v))
                b.pack(side='left', padx=2, pady=(2,0))
                phase_buttons.append((b, val))
            except Exception:
                continue
        print(f"DEBUG: Phase filter setup complete with {len(phase_buttons)} buttons -> defs={phase_button_defs}")

        # Checker Filter
        chk_frame=ctk.CTkFrame(controls, fg_color=app.get_color('transparent'))
        chk_frame.pack(side='left', padx=spacing_lg)
        ctk.CTkLabel(chk_frame,text=app._t('Checker'),font=ctk.CTkFont(*app.get_typography('caption')),
                     text_color=app.get_color('text_secondary')).pack(anchor='w')
        checker_defs=[(app._t('All'),'ALL'),('heuristic','heuristic'),('hunspell','hunspell'),('languagetool','languagetool'),('ollama','ollama')]
        checker_buttons=[]
        def _set_checker(val):
            state['checker']=val; _persist(); _render_list();
            for b,v in checker_buttons:
                try: b.configure(fg_color=app.get_color('primary') if v==val else app.get_color('surface_hover'), text_color=app.get_color('text_inverse') if v==val else app.get_color('text_primary'))
                except Exception: pass
        for lab,val in checker_defs:
            try:
                b=ctk.CTkButton(chk_frame,text=lab,width=80,height=24,fg_color=app.get_color('surface_hover'),hover_color=app.get_color('surface_hover'),text_color=app.get_color('text_primary'),command=lambda _v=val:_set_checker(_v))
                b.pack(side='left', padx=2, pady=(2,0))
                checker_buttons.append((b,val))
            except Exception: continue
        print(f"DEBUG: Checker filter setup complete with {len(checker_buttons)} buttons")

        # Search
        search_frame=ctk.CTkFrame(controls, fg_color=app.get_color('transparent'))
        search_frame.pack(side='left', padx=spacing_lg)
        ctk.CTkLabel(search_frame,text=app._t('Suche'),font=ctk.CTkFont(*app.get_typography('caption')),
                     text_color=app.get_color('text_secondary')).pack(anchor='w')
        query_var=ctk.StringVar(value='')
        def _on_query(*_):
            state['query']=query_var.get().strip().lower(); _render_list()
        try:
            ent=ctk.CTkEntry(search_frame,textvariable=query_var,width=180)
            ent.pack(anchor='w')
            query_var.trace_add('write', _on_query)
            body_container._findings_search_entry=ent  # type: ignore
        except Exception: pass
        print("DEBUG: Search field initialized")

        # Sort
        sort_frame=ctk.CTkFrame(controls, fg_color=app.get_color('transparent'))
        sort_frame.pack(side='left', padx=spacing_lg)
        ctk.CTkLabel(sort_frame,text=app._t('Sortierung'),font=ctk.CTkFont(*app.get_typography('caption')),
                     text_color=app.get_color('text_secondary')).pack(anchor='w')
        sort_defs=[(app._t('Schwere'),'severity'),(app._t('Regel'),'rule'),(app._t('Text'),'message')]
        sort_buttons=[]
        def _set_sort(val):
            state['sort']=val; _persist(); _render_list();
            for b,v in sort_buttons:
                try: b.configure(fg_color=app.get_color('primary') if v==val else app.get_color('surface_hover'), text_color=app.get_color('text_inverse') if v==val else app.get_color('text_primary'))
                except Exception: pass
        for lab,val in sort_defs:
            try:
                b=ctk.CTkButton(sort_frame,text=lab,width=70,height=24,fg_color=app.get_color('surface_hover'),hover_color=app.get_color('surface_hover'),text_color=app.get_color('text_primary'),command=lambda _v=val:_set_sort(_v))
                b.pack(side='left', padx=2, pady=(2,0))
                sort_buttons.append((b,val))
            except Exception: continue
        print(f"DEBUG: Sort buttons ready ({len(sort_buttons)}) with state sort={state['sort']} dir={state['sort_dir']}")
        def _toggle_sort_dir():
            state['sort_dir']='desc' if state['sort_dir']=='asc' else 'asc';
            try: dir_btn.configure(text='ASC' if state['sort_dir']=='asc' else 'DESC')
            except Exception: pass
            _persist(); _render_list()
        try:
            dir_btn=ctk.CTkButton(sort_frame,text='ASC' if state['sort_dir']=='asc' else 'DESC',width=60,height=24,fg_color=app.get_color('primary'),hover_color=app.get_color('primary_hover'),text_color=app.get_color('text_inverse'),command=_toggle_sort_dir)
            dir_btn.pack(side='left', padx=(6,0), pady=(2,0))
        except Exception:
            dir_btn=None
        print("DEBUG: Sort direction control initialized")

        # Gruppierungs-Toggle (Game Changer 1)
        group_frame=ctk.CTkFrame(controls, fg_color=app.get_color('transparent'))
        group_frame.pack(side='right', padx=spacing_lg)
        state['grouped'] = state.get('grouped', False)
        
        def _toggle_grouping():
            state['grouped'] = not state['grouped']
            _persist()
            _render_list()
            try:
                group_btn.configure(
                    fg_color=app.get_color('primary') if state['grouped'] else app.get_color('surface_hover'),
                    text_color=app.get_color('text_inverse') if state['grouped'] else app.get_color('text_primary')
                )
            except Exception:
                pass
        
        try:
            group_btn = ctk.CTkButton(
                group_frame,
                text=app._t('Gruppieren'),
                width=95,
                height=26,
                fg_color=app.get_color('primary') if state.get('grouped') else app.get_color('surface_hover'),
                hover_color=app.get_color('primary_hover'),
                text_color=app.get_color('text_inverse') if state.get('grouped') else app.get_color('text_primary'),
                command=_toggle_grouping
            )
            group_btn.pack()
        except Exception:
            pass

        # Actions
        actions=ctk.CTkFrame(controls, fg_color=app.get_color('transparent'))
        actions.pack(side='right')
        def _subset():
            base=findings
            print(f"DEBUG _subset: Starting with {len(base)} findings")
            try:
                sub=[f for f in base if (state['severity']=='ALL' or str(f.get('severity') or '').lower()==state['severity'])]
                print(f"DEBUG _subset: After severity filter ({state['severity']}): {len(sub)} findings")
                
                # Quick Win 2: Kategorie-Filter anwenden
                if state.get('category') and state['category'] != 'ALL':
                    sub = [f for f in sub if f.get('category') == state['category']]
                    print(f"DEBUG _subset: After category filter ({state['category']}): {len(sub)} findings")
                
                if state['phase']!='ALL':
                    target = state['phase']
                    # DEBUG: Log phase filtering
                    print(f"DEBUG _subset: Filtering by phase='{target}', before filter: {len(sub)} items")
                    sub=[f for f in sub if _normalize_phase_key(f.get('phase') or f.get('category') or '')==target]
                    print(f"DEBUG _subset: After phase filter: {len(sub)} items")
                else:
                    print(f"DEBUG _subset: Phase filter is ALL, keeping all {len(sub)} items")
                if state['checker']!='ALL':
                    print(f"DEBUG _subset: Filtering by checker '{state['checker']}'")
                    sub=[f for f in sub if (f.get('checker') or '').lower()==state['checker']]
                    print(f"DEBUG _subset: After checker filter: {len(sub)} items")
                if state['query']:
                    q=state['query']
                    print(f"DEBUG _subset: Filtering by query '{q}'")
                    sub=[f for f in sub if q in (f.get('message') or '').lower() or q in (f.get('rule_id') or f.get('rule') or '').lower()]
                    print(f"DEBUG _subset: After query filter: {len(sub)} items")
                reverse=(state['sort_dir']=='desc')
                print(f"DEBUG _subset: Sorting by '{state['sort']}', direction={state['sort_dir']}")
                try:
                    if state['sort']=='severity':
                        order={'critical':0,'major':1,'minor':2,'info':3}
                        sub=sorted(sub,key=lambda f:(order.get(f.get('severity') or 'info',9), (f.get('rule_id') or f.get('rule') or ''), (f.get('message') or '')),reverse=reverse)
                    elif state['sort']=='rule':
                        sub=sorted(sub,key=lambda f:((f.get('rule_id') or f.get('rule') or ''),(f.get('severity') or ''),(f.get('message') or '')),reverse=reverse)
                    else:
                        sub=sorted(sub,key=lambda f:((f.get('message') or ''),(f.get('severity') or ''),(f.get('rule_id') or f.get('rule') or '')),reverse=reverse)
                except Exception: pass
                return sub
            except Exception:
                return base
        def _copy_all():
            try:
                lines=[f"[{f.get('severity')}] {(f.get('rule_id') or f.get('rule') or 'rule')}: {(f.get('message') or '')}" for f in _subset()]
                blob='\n'.join(lines)
                if getattr(app,'root',None):
                    app.root.clipboard_clear(); app.root.clipboard_append(blob)
                _toast(app, app._t('Copied to clipboard'),'success')
            except Exception: pass
        def _copy_critical():
            try:
                crit=[f for f in _subset() if f.get('severity')=='critical']
                if not crit: _toast(app, app._t('Keine kritischen Einträge'),'info'); return
                blob='\n'.join([f"[{f.get('severity')}] {(f.get('rule_id') or f.get('rule') or 'rule')}: {(f.get('message') or '')}" for f in crit])
                if getattr(app,'root',None):
                    app.root.clipboard_clear(); app.root.clipboard_append(blob)
                _toast(app, app._t('Kritische kopiert'),'success')
            except Exception: pass
        def _export():
            try:
                import os, datetime, json, csv
                subset=_subset(); ts=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                base_dir=getattr(app,'projects_base_path','.') or '.'
                report_dir=os.path.join(base_dir,'reports'); os.makedirs(report_dir, exist_ok=True)
                with open(os.path.join(report_dir,f'analysis_findings_{ts}.txt'),'w',encoding='utf-8') as fh:
                    for f in subset: fh.write(f"[{f.get('severity')}] {(f.get('rule_id') or f.get('rule') or 'rule')}: {(f.get('message') or '')}\n")
                with open(os.path.join(report_dir,f'analysis_findings_{ts}.json'),'w',encoding='utf-8') as jf: json.dump(subset,jf,ensure_ascii=False,indent=2)
                with open(os.path.join(report_dir,f'analysis_findings_{ts}.csv'),'w',encoding='utf-8',newline='') as cf:
                    w=csv.writer(cf, delimiter=';'); w.writerow(['severity','rule','checker','message'])
                    for f in subset: w.writerow([f.get('severity'), (f.get('rule_id') or f.get('rule')), f.get('checker'), (f.get('message') or '').replace('\n',' ')])
                _toast(app, app._t('Export created'),'success')
            except Exception: pass
        try:
            ctk.CTkButton(actions,text=app._t('Copy'),width=70,height=26,fg_color=app.get_color('primary'),hover_color=app.get_color('primary_hover'),text_color=app.get_color('text_inverse'),command=_copy_all).pack(side='left', padx=4)
            ctk.CTkButton(actions,text=app._t('Export'),width=80,height=26,fg_color=app.get_color('secondary'),hover_color=app.get_color('secondary_hover'),text_color=app.get_color('text_inverse'),command=_export).pack(side='left', padx=4)
            ctk.CTkButton(actions,text=app._t('Kritisch'),width=80,height=26,fg_color=app.get_color('error'),hover_color=app.get_color('error_hover') if hasattr(app,'get_color') else app.get_color('error'),text_color=app.get_color('text_inverse'),command=_copy_critical).pack(side='left', padx=4)
        except Exception: pass
        print("DEBUG: Action buttons configured")

        # Scrollbare Container-Variante für zuverlässige Darstellung
        summary_frame = ctk.CTkFrame(
            container,
            fg_color=app.get_color('surface_hover'),
            corner_radius=_safe_radius(app, 'radius_md', 8),
            border_width=1,
            border_color=app.get_color('surface_border')
        )
        summary_frame.pack(fill='x', padx=spacing_sm, pady=(spacing_md, spacing_sm))
        ctk.CTkLabel(
            summary_frame,
            text=app._t('Gefilterte Befunde'),
            font=ctk.CTkFont(*app.get_typography('caption')),
            text_color=app.get_color('text_secondary')
        ).pack(side='left', padx=(spacing_md, spacing_sm), pady=spacing_sm)
        summary_value = ctk.CTkLabel(
            summary_frame,
            text='—',
            font=ctk.CTkFont(*app.get_typography('body_bold')),
            text_color=app.get_color('text_primary')
        )
        summary_value.pack(side='left', padx=(0, spacing_md), pady=spacing_sm)

        list_wrap = ctk.CTkScrollableFrame(container, fg_color=app.get_color('transparent'))
        list_wrap.pack(fill='both', expand=True, pady=(spacing_sm, 0))
        list_wrap.grid_columnconfigure(0, weight=1)
        print("DEBUG: Scrollable findings container created")

        rendered: Dict[int, Dict[str, Any]] = {}
        current_subset: List[Dict[str, Any]] = []

        def _ensure_visible(idx: int) -> None:
            canvas = getattr(list_wrap, "_parent_canvas", None)
            if not canvas:
                return
            try:
                total = max(len(current_subset), 1)
                fraction = max(0.0, min(1.0, idx / total))
                canvas.yview_moveto(fraction)
            except Exception:
                pass

        def _highlight() -> None:
            for idx, info in list(rendered.items()):
                try:
                    active = idx == state['selected_index']
                    frame_bg = app.get_color('primary_light') if active else app.get_color('surface')
                    frame_border = app.get_color('primary') if active else app.get_color('surface_border')
                    info['frame'].configure(fg_color=frame_bg, border_color=frame_border)
                    info['title'].configure(text_color=app.get_color('text_primary'))
                    message_color = app.get_color('text_primary') if active else app.get_color(info['severity_token'])
                    info['message'].configure(text_color=message_color)
                    for lbl in info['meta_labels']:
                        lbl.configure(text_color=app.get_color('text_primary') if active else app.get_color('text_secondary'))
                    if info.get('detail_label'):
                        info['detail_label'].configure(text_color=app.get_color('text_primary') if active else app.get_color('text_secondary'))
                    if info.get('badge') and info.get('badge_label'):
                        badge_color = app.get_color('primary') if active else app.get_color(info['badge_bg'])
                        info['badge'].configure(fg_color=badge_color)
                        badge_text_color = app.get_color('text_inverse') if active else app.get_color(info['severity_token'])
                        info['badge_label'].configure(text_color=badge_text_color)
                except Exception:
                    pass

        def _update_counts():
            try:
                def _matches_common_filters(f: Dict[str, Any]) -> bool:
                    checker_val = state['checker']
                    if checker_val != 'ALL' and (f.get('checker') or '').lower() != checker_val:
                        return False
                    if state['query']:
                        q = state['query']
                        message = (f.get('message') or '').lower()
                        rule_text = (f.get('rule_id') or f.get('rule') or '').lower()
                        if q not in message and q not in rule_text:
                            return False
                    return True

                filtered = [f for f in findings if _matches_common_filters(f)]
                filtered_phase = [f for f in filtered if state['phase']=='ALL' or _normalize_phase_key(f.get('phase') or f.get('category') or '')==state['phase']]

                sev_counts = {'critical': 0, 'major': 0, 'minor': 0}
                for f in filtered_phase:
                    sev = str(f.get('severity') or '').lower()
                    if sev in sev_counts:
                        sev_counts[sev] += 1
                total_phase = len(filtered_phase)
                for b, v in severity_buttons:
                    try:
                        base_lab = b.cget('text').split(' (')[0]
                        if v == 'ALL':
                            b.configure(text=f"{base_lab.split(' (')[0]} ({total_phase})")
                        else:
                            b.configure(text=f"{base_lab.split(' (')[0]} ({sev_counts.get(v, 0)})")
                    except Exception:
                        pass

                checker_counts: Dict[str, int] = {}
                for f in filtered:
                    chk = (f.get('checker') or '').lower() or '—'
                    checker_counts[chk] = checker_counts.get(chk, 0) + 1
                total_filtered = len(filtered)
                for b, v in checker_buttons:
                    try:
                        base_lab = b.cget('text').split(' (')[0]
                        if v == 'ALL':
                            b.configure(text=f"{base_lab} ({total_filtered})")
                        else:
                            b.configure(text=f"{base_lab} ({checker_counts.get(v, 0)})")
                    except Exception:
                        pass

                phase_counts: Dict[str, int] = {}
                for f in filtered:
                    phase_key = _normalize_phase_key(f.get('phase') or f.get('category') or '') or '—'
                    phase_counts[phase_key] = phase_counts.get(phase_key, 0) + 1
                for b, v in phase_buttons:
                    try:
                        base_lab = b.cget('text').split(' (')[0]
                        if v == 'ALL':
                            b.configure(text=f"{base_lab} ({total_filtered})")
                        else:
                            b.configure(text=f"{base_lab} ({phase_counts.get(v, 0)})")
                    except Exception:
                        pass
            except Exception: pass

        # Debounced wrap helper
        _wrap_after={'id':None}
        def _debounce_wrap(lbl):
            try:
                if _wrap_after['id'] and getattr(app,'root',None): app.root.after_cancel(_wrap_after['id'])
                def _apply():
                    try:
                        w=lbl.winfo_width()
                        if w>0: lbl.configure(wraplength=int(w*0.97))
                    except Exception: pass
                _wrap_after['id']=app.root.after(60,_apply) if getattr(app,'root',None) else None
            except Exception: pass

        def _format_text(f):
            sev = str(f.get('severity') or 'info').lower()
            rule_txt = (f.get('rule_id') or f.get('rule') or 'rule').strip()
            message_txt = (f.get('message') or '').strip()
            phase_key = _normalize_phase_key(f.get('phase') or f.get('category') or '')
            phase_label = phase_label_map.get(phase_key, phase_key.upper()) if phase_key else ''
            checker_txt = (f.get('checker') or '').strip()
            parts = [f"[{sev.upper()}] {rule_txt}: {message_txt}" if message_txt else f"[{sev.upper()}] {rule_txt}"]
            if phase_label:
                parts.append(app._t('Phase') + f": {phase_label}")
            if checker_txt:
                parts.append(app._t('Checker') + f": {checker_txt}")
            tgt = _format_issue_excerpt(f.get('target_excerpt') or f.get('target_text') or f.get('target'))[0]
            if tgt:
                parts.append(app._t('Ziel') + f": {tgt}")
            src = _format_issue_excerpt(f.get('source_excerpt') or f.get('source_text') or f.get('source'))[0]
            if src:
                parts.append(app._t('Quelle') + f": {src}")
            blob = '\n'.join(parts)
            return blob[:900]

        def _severity_styles(sev: str) -> Tuple[str, str, str]:
            if sev == 'critical':
                return 'error', 'error_light', app._t('Kritisch')
            if sev == 'major':
                return 'warning', 'warning_light', app._t('Schwerwiegend')
            if sev == 'minor':
                return 'info', 'info_light', app._t('Leicht')
            return 'info', 'info_light', app._t('Hinweis')

        def _create_row(parent, idx, f, in_group=False):
            """Erstellt eine Finding-Row. in_group=True für kompaktere Darstellung in Gruppen."""
            sev = str(f.get('severity') or 'info').lower()
            color_token, badge_bg_token, severity_label = _severity_styles(sev)
            
            # UI-Optimierung: Erweiterte Informationen laden
            enriched = {}
            if UI_OPTIMIZATION_AVAILABLE:
                try:
                    enriched = get_enriched_finding_info(f)
                except Exception:
                    pass

            # Quick Win 1: Severity Accent-Bar (farbiger linker Rand)
            accent_colors = {
                'critical': app.get_color('error'),
                'major': app.get_color('warning'),
                'minor': app.get_color('info'),
                'info': app.get_color('info')
            }
            accent_color = accent_colors.get(sev, app.get_color('info'))
            
            row = ctk.CTkFrame(
                parent,
                fg_color=app.get_color('surface'),
                corner_radius=_safe_radius(app, 'radius_md', 8),
                border_width=1,
                border_color=accent_color  # Severity-Farbe statt Standard-Border
            )
            # Quick Win 5: Mehr Whitespace (8px statt 4px)
            row.grid(row=idx, column=0, sticky='ew', padx=spacing_sm, pady=(0, spacing_md))
            row.grid_columnconfigure(1, weight=1)
            
            # Zusätzlicher farbiger Accent-Balken links
            accent_bar = ctk.CTkFrame(
                row,
                fg_color=accent_color,
                width=4,
                corner_radius=0
            )
            accent_bar.grid(row=0, column=0, rowspan=5, sticky='ns', padx=0, pady=0)

            badge = ctk.CTkFrame(
                row,
                fg_color=app.get_color(badge_bg_token),
                corner_radius=_safe_radius(app, 'radius_sm', 6)
            )
            badge.grid(row=0, column=1, rowspan=4, sticky='ns', padx=(spacing_md, spacing_md), pady=spacing_md)
            
            # Badge-Inhalt mit Kategorie-Prefix
            badge_text = severity_label
            if enriched.get('category_prefix'):
                badge_text = f"{enriched['category_prefix']}\n{severity_label}"
            
            # Quick Win 3: Segment-Position (falls verfügbar)
            segment_idx = f.get('segment_index') or f.get('index')
            total_segments = f.get('total_segments')
            if segment_idx is not None:
                if total_segments:
                    badge_text += f"\n#{segment_idx}/{total_segments}"
                else:
                    badge_text += f"\n#{segment_idx}"
            
            badge_label = ctk.CTkLabel(
                badge,
                text=badge_text,
                font=ctk.CTkFont(*app.get_typography('caption')),
                text_color=app.get_color(color_token)
            )
            badge_label.pack(padx=spacing_sm, pady=(spacing_sm//2, spacing_sm//2))

            # Titel mit Kategorie-Info - jetzt mit klarer deutscher Beschreibung
            rule_id = (f.get('rule_id') or f.get('rule') or '').strip()
            
            # Benutzerfreundliche Regel-Beschreibungen
            rule_friendly_names = {
                'PLACEHOLDER_MISSING': 'Fehlende Platzhalter',
                'PLACEHOLDER_EXTRA': 'Zusätzliche Platzhalter',
                'PLACEHOLDER_ORDER': 'Platzhalter-Reihenfolge',
                'URL_MISSING': 'Fehlende URL',
                'URL_EXTRA': 'Zusätzliche URL',
                'EMAIL_MISSING': 'Fehlende E-Mail-Adresse',
                'EMAIL_EXTRA': 'Zusätzliche E-Mail-Adresse',
                'WS_DOUBLE_SPACE': 'Doppelte Leerzeichen',
                'WS_TRAILING': 'Leerzeichen am Ende',
                'WS_LEADING': 'Leerzeichen am Anfang',
                'ZERO_WIDTH_CHAR': 'Unsichtbare Zeichen',
                'BRACKET_UNBALANCED': 'Klammern nicht geschlossen',
                'BRACKET_MISMATCH': 'Klammer-Fehler',
                'BRACKET_UNCLOSED': 'Offene Klammer',
                'QUOTE_UNBALANCED': 'Anführungszeichen unausgeglichen',
                'NUMBER_MISMATCH': 'Zahlen stimmen nicht überein',
                'NUMBER_CHANGED': 'Zahl wurde verändert',
                'UNIT_MISMATCH': 'Einheit stimmt nicht',
                'HTML_TAG_MISSING': 'HTML-Tag fehlt',
                'HTML_TAG_EXTRA': 'Zusätzliches HTML-Tag',
                'HTML_ATTR_CHANGED': 'HTML-Attribut verändert',
                'UNTRANSLATED_SEGMENT': 'Nicht übersetzt',
                'TARGET_LANGUAGE_MIX': 'Falsche Sprache erkannt',
                'TERMINOLOGY_LOW': 'Glossar nicht beachtet',
                'LENGTH_DRIFT': 'Ungewöhnliche Textlänge',
                'PROPER_NAME_MISSING': 'Eigenname fehlt/verändert',
                'COVERAGE_RATIO_LOW': 'Text zu kurz übersetzt',
            }
            rule_txt = rule_friendly_names.get(rule_id, rule_id) or app._t('Prüfung')
            
            title_lbl = ctk.CTkLabel(
                row,
                text=f"⚠️ {rule_txt}",
                font=ctk.CTkFont(*app.get_typography('label_bold')),
                text_color=app.get_color('text_primary'),
                anchor='w',
                justify='left'
            )
            title_lbl.grid(row=0, column=1, sticky='w', padx=(0, spacing_md), pady=(spacing_md, 0))

            message_txt = (f.get('message') or '').strip() or app._t('Keine Beschreibung verfügbar')
            
            # Klare Handlungsanweisung basierend auf Regel-Typ
            action_hints = {
                'PLACEHOLDER_MISSING': '→ Bitte den Platzhalter aus dem Quelltext in die Übersetzung übernehmen.',
                'PLACEHOLDER_EXTRA': '→ Bitte den zusätzlichen Platzhalter aus der Übersetzung entfernen.',
                'URL_MISSING': '→ Bitte die URL aus dem Quelltext unverändert übernehmen.',
                'EMAIL_MISSING': '→ Bitte die E-Mail-Adresse aus dem Quelltext übernehmen.',
                'NUMBER_MISMATCH': '→ Bitte die Zahl aus dem Quelltext korrekt übernehmen.',
                'NUMBER_CHANGED': '→ Zahlen dürfen nicht verändert werden - bitte korrigieren.',
                'UNIT_MISMATCH': '→ Bitte Einheit prüfen und ggf. an Zielsprache anpassen.',
                'HTML_TAG_MISSING': '→ HTML-Tags müssen exakt übernommen werden.',
                'UNTRANSLATED_SEGMENT': '→ Dieses Segment muss noch übersetzt werden.',
                'TERMINOLOGY_LOW': '→ Bitte Glossar-Begriffe verwenden.',
                'PROPER_NAME_MISSING': '→ Eigennamen müssen unverändert bleiben.',
            }
            action_hint = action_hints.get(rule_id, '')
            
            # Nachricht + Handlungsanweisung kombinieren
            full_message = message_txt
            if action_hint:
                full_message = f"{message_txt}\n{action_hint}"
            
            message_lbl = ctk.CTkLabel(
                row,
                text=full_message,
                font=ctk.CTkFont(*app.get_typography('body')),
                text_color=app.get_color(color_token),
                anchor='w',
                justify='left'
            )
            message_lbl.grid(row=1, column=1, sticky='ew', padx=(0, spacing_md), pady=(2, spacing_sm))
            message_lbl.bind('<Configure>', lambda e, lbl=message_lbl: _debounce_wrap(lbl))
            
            # Lösung prominent anzeigen (falls verfügbar)
            solution_txt = enriched.get('rule_help', {}).get('solution')
            if solution_txt and UI_OPTIMIZATION_AVAILABLE:
                solution_frame = ctk.CTkFrame(
                    row,
                    fg_color=app.get_color('success_light') if hasattr(app, 'get_color') else app.get_color('info_light'),
                    corner_radius=4
                )
                solution_frame.grid(row=2, column=1, sticky='ew', padx=(0, spacing_md), pady=(spacing_sm, spacing_sm))
                
                solution_label = ctk.CTkLabel(
                    solution_frame,
                    text=f"💡 LÖSUNG: {solution_txt}",
                    font=ctk.CTkFont(*app.get_typography('caption')),
                    text_color=app.get_color('success') if hasattr(app, 'get_color') else app.get_color('text_primary'),
                    anchor='w',
                    justify='left'
                )
                solution_label.pack(padx=spacing_sm, pady=spacing_sm//2, fill='x')

            meta_parts: List[str] = []
            phase_key = _normalize_phase_key(f.get('phase') or f.get('category') or '')
            if phase_key:
                meta_parts.append(app._t('Phase') + f": {phase_label_map.get(phase_key, phase_key.upper())}")
            checker_txt = (f.get('checker') or '').strip()
            if checker_txt:
                meta_parts.append(app._t('Checker') + f": {checker_txt}")
            
            # Auswirkung hinzufügen
            if enriched.get('impact_level'):
                meta_parts.append(f"Auswirkung: {enriched['impact_level']}")
            
            meta_lbl = None
            if meta_parts:
                meta_lbl = ctk.CTkLabel(
                    row,
                    text=' • '.join(meta_parts),
                    font=ctk.CTkFont(*app.get_typography('caption')),
                    text_color=app.get_color('text_secondary'),
                    anchor='w',
                    justify='left'
                )
                meta_lbl.grid(row=3, column=1, sticky='w', padx=(0, spacing_md), pady=(0, spacing_sm))

            detail_parts: List[str] = []
            meta = f.get('meta') or {}
            def _meta_value(*keys):
                for key in keys:
                    val = meta.get(key)
                    if val not in (None, ''):
                        if isinstance(val, list):
                            return ', '.join(str(x) for x in val)
                        return str(val)
                return ''
            
            def _get_text_safe(finding, *keys):
                """Holt Textfelder sicher aus Finding oder Meta."""
                for key in keys:
                    # Erst direkt im Finding suchen
                    val = finding.get(key)
                    if val and isinstance(val, str) and val.strip():
                        return val.strip()
                    # Dann in Meta suchen
                    val = meta.get(key)
                    if val and isinstance(val, str) and val.strip():
                        return val.strip()
                return None

            # ==========================================
            # VERGLEICHS-BOX: Quelle vs. Übersetzung
            # ==========================================
            src_text = _get_text_safe(f, 'source', 'source_text', 'source_excerpt')
            tgt_text = _get_text_safe(f, 'target', 'target_text', 'target_excerpt')
            
            # Zeige Quelle/Ziel immer wenn verfügbar - das ist das Wichtigste!
            if src_text or tgt_text:
                compare_frame = ctk.CTkFrame(row, fg_color=app.get_color('surface'),
                                            corner_radius=6, border_width=1,
                                            border_color=app.get_color('surface_border'))
                compare_frame.grid(row=4, column=1, sticky='ew', padx=(0, spacing_md), pady=(spacing_sm, spacing_sm))
                
                if src_text:
                    src_excerpt, is_binary = _format_issue_excerpt(src_text)
                    if src_excerpt and not is_binary:
                        src_row = ctk.CTkFrame(compare_frame, fg_color=app.get_color('transparent'))
                        src_row.pack(fill='x', padx=spacing_sm, pady=(spacing_sm, 0))
                        ctk.CTkLabel(src_row, text="📥 AUSGANGSTEXT:",
                                   font=ctk.CTkFont(*app.get_typography('caption')),
                                   text_color=app.get_color('info')).pack(anchor='w')
                        ctk.CTkLabel(src_row, text=src_excerpt,
                                   font=ctk.CTkFont(*app.get_typography('body')),
                                   text_color=app.get_color('text_primary'),
                                   wraplength=500).pack(anchor='w', pady=(2, 0))
                
                if tgt_text:
                    tgt_excerpt, is_binary = _format_issue_excerpt(tgt_text)
                    if tgt_excerpt and not is_binary:
                        tgt_row = ctk.CTkFrame(compare_frame, fg_color=app.get_color('transparent'))
                        tgt_row.pack(fill='x', padx=spacing_sm, pady=(spacing_sm, 0))
                        ctk.CTkLabel(tgt_row, text="📤 ÜBERSETZUNG:",
                                   font=ctk.CTkFont(*app.get_typography('caption')),
                                   text_color=app.get_color('success')).pack(anchor='w')
                        ctk.CTkLabel(tgt_row, text=tgt_excerpt,
                                   font=ctk.CTkFont(*app.get_typography('body')),
                                   text_color=app.get_color('text_primary'),
                                   wraplength=500).pack(anchor='w', pady=(2, 0))
                
                # Fehler-Details (was genau fehlt/falsch ist)
                error_details = []
                
                missing_txt = _meta_value('missing')
                if missing_txt:
                    error_details.append(f"❌ Fehlt in Übersetzung: {missing_txt}")
                
                extra_txt = _meta_value('extra')
                if extra_txt:
                    error_details.append(f"➕ Zusätzlich in Übersetzung: {extra_txt}")
                
                expected_txt = _meta_value('expected', 'expected_text', 'expected_value', 'should')
                if expected_txt:
                    error_details.append(f"✓ Erwartet: {expected_txt}")
                
                actual_txt = _meta_value('actual', 'actual_text', 'actual_value', 'is')
                if actual_txt:
                    error_details.append(f"✗ Gefunden: {actual_txt}")
                
                if error_details:
                    error_row = ctk.CTkFrame(compare_frame, fg_color=app.get_color('error_light'),
                                           corner_radius=4)
                    error_row.pack(fill='x', padx=spacing_sm, pady=spacing_sm)
                    for error_text in error_details:
                        ctk.CTkLabel(error_row, text=error_text,
                                   font=ctk.CTkFont(*app.get_typography('body')),
                                   text_color=app.get_color('error'),
                                   anchor='w').pack(anchor='w', padx=spacing_sm, pady=(spacing_sm//2, 0))
                    # Letztes Element: Padding unten
                    error_row.winfo_children()[-1].pack_configure(pady=(spacing_sm//2, spacing_sm//2))
                else:
                    # Padding am Ende der compare_frame
                    ctk.CTkFrame(compare_frame, fg_color=app.get_color('transparent'), height=spacing_sm).pack()
            
            detail_lbl = None  # Für Kompatibilität
            
            # Game Changer 3: Quick-Fix-Buttons (falls anwendbar)
            fix_buttons_row = None
            rule_id = f.get('rule_id', '') or f.get('rule', '')
            
            # Definiere Quick-Fixes für häufige Fehler
            quick_fixes = []
            
            if 'BOUNDARY_SPACE' in rule_id or 'whitespace' in rule_id.lower():
                quick_fixes.append({
                    'label': 'Leerzeichen hinzufügen',
                    'action': 'add_space',
                    'icon': '→ ',
                    'description': 'Fügt fehlendes Leerzeichen hinzu'
                })
            
            if 'PLACEHOLDER' in rule_id:
                quick_fixes.append({
                    'label': 'Platzhalter kopieren',
                    'action': 'copy_placeholder',
                    'icon': '{} ',
                    'description': 'Kopiert Platzhalter aus Quelle'
                })
            
            if 'HTML' in rule_id or 'TAG' in rule_id:
                quick_fixes.append({
                    'label': 'HTML-Tag korrigieren',
                    'action': 'fix_html',
                    'icon': '<> ',
                    'description': 'Korrigiert HTML-Struktur'
                })
            
            if 'PUNCTUATION' in rule_id:
                quick_fixes.append({
                    'label': 'Interpunktion anpassen',
                    'action': 'fix_punctuation',
                    'icon': '., ',
                    'description': 'Korrigiert Satzzeichen'
                })
            
            # Zeige Quick-Fix-Buttons wenn vorhanden
            if quick_fixes:
                fix_buttons_row = ctk.CTkFrame(row, fg_color=app.get_color('transparent'))
                fix_buttons_row.grid(row=5, column=1, sticky='w', padx=(0, spacing_md), pady=(0, spacing_md))
                
                fix_label = ctk.CTkLabel(
                    fix_buttons_row,
                    text='Schnellkorrektur:',
                    font=ctk.CTkFont(*app.get_typography('caption')),
                    text_color=app.get_color('text_secondary')
                )
                fix_label.pack(side='left', padx=(0, spacing_sm))
                
                for fix in quick_fixes[:2]:  # Max 2 Buttons pro Finding
                    def _apply_fix(finding=f, action=fix['action'], fix_info=fix):
                        try:
                            # Callback zum Haupt-App für Datei-Modifikation
                            if hasattr(app, 'apply_quick_fix'):
                                success = app.apply_quick_fix(finding, action)
                                if success:
                                    _toast(app, f"✓ {fix_info['description']}", 'success')
                                    # Optional: Finding aus Liste entfernen
                                else:
                                    _toast(app, 'Korrektur fehlgeschlagen', 'error')
                            else:
                                # Fallback: Nur Info kopieren
                                _toast(app, 'Quick-Fix-System noch nicht verfügbar', 'warning')
                        except Exception as e:
                            _toast(app, f'Fehler: {str(e)}', 'error')
                    
                    fix_btn = ctk.CTkButton(
                        fix_buttons_row,
                        text=f"{fix['icon']}{fix['label']}",
                        width=160,
                        height=24,
                        fg_color=app.get_color('success') if hasattr(app, 'get_color') else app.get_color('primary'),
                        hover_color=app.get_color('success_hover') if hasattr(app, 'get_color') else app.get_color('primary_hover'),
                        text_color=app.get_color('text_inverse'),
                        font=ctk.CTkFont(*app.get_typography('caption')),
                        command=_apply_fix
                    )
                    fix_btn.pack(side='left', padx=(0, spacing_sm))

            # 🎯 Navigation: "Zum Segment" Button
            nav_row = ctk.CTkFrame(row, fg_color=app.get_color('transparent'))
            nav_row.grid(row=6, column=1, sticky='w', padx=(0, spacing_md), pady=(0, spacing_md))
            
            def _navigate_to_segment(finding=f):
                """Öffnet die Segment-Vorschau und scrollt zum betroffenen Segment."""
                try:
                    # Segment-Index ermitteln
                    seg_idx = finding.get('segment_index') or finding.get('index')
                    seg_hash = finding.get('hash') or (finding.get('meta') or {}).get('hash')
                    source_text = finding.get('source') or finding.get('source_text') or ''
                    
                    # Preview-Fenster öffnen mit Scroll-Ziel
                    if hasattr(app, '_launch_pair_details_preview_with_scroll'):
                        app._launch_pair_details_preview_with_scroll(seg_idx, seg_hash, source_text)
                    elif hasattr(app, '_launch_pair_details_preview'):
                        # Fallback: Normal öffnen
                        app._launch_pair_details_preview()
                        _toast(app, f'Segment #{seg_idx if seg_idx else "?"} im Textfenster suchen', 'info')
                    else:
                        _toast(app, 'Segment-Navigation nicht verfügbar', 'warning')
                except Exception as e:
                    _toast(app, f'Navigation fehlgeschlagen: {str(e)[:50]}', 'error')
            
            nav_btn = ctk.CTkButton(
                nav_row,
                text='🔍 Zum Segment',
                width=120,
                height=26,
                fg_color=app.get_color('primary'),
                hover_color=app.get_color('primary_hover'),
                text_color=app.get_color('text_inverse'),
                font=ctk.CTkFont(*app.get_typography('caption')),
                command=_navigate_to_segment
            )
            nav_btn.pack(side='left', padx=(0, spacing_sm))

            copy_payload = _format_text(f)

            def _copy_single(e=None, _text=copy_payload):
                try:
                    if getattr(app, 'root', None):
                        app.root.clipboard_clear()
                        app.root.clipboard_append(_text)
                    _toast(app, app._t('Eintrag kopiert'), 'success')
                except Exception:
                    pass

            message_lbl.bind('<Double-Button-1>', _copy_single)
            title_lbl.bind('<Double-Button-1>', _copy_single)
            if detail_lbl:
                detail_lbl.bind('<Double-Button-1>', _copy_single)

            def _select(e=None):
                state['selected_index'] = idx
                _highlight()
                _ensure_visible(idx)

            for widget in (row, badge, badge_label, title_lbl, message_lbl, meta_lbl, detail_lbl):
                if widget is not None:
                    widget.bind('<Button-1>', _select)

            rendered[idx] = {
                'frame': row,
                'title': title_lbl,
                'message': message_lbl,
                'meta_labels': [lbl for lbl in (meta_lbl,) if lbl],
                'detail_label': detail_lbl,
                'severity_token': color_token,
                'badge': badge,
                'badge_label': badge_label,
                'badge_bg': badge_bg_token
            }

        def _render_list():
            nonlocal current_subset
            current_subset = _subset()
            visible = len(current_subset)
            try:
                summary_value.configure(
                    text=app._t('{visible} von {total} Befunden sichtbar').format(
                        visible=visible,
                        total=len(findings)
                    )
                )
            except Exception:
                pass
            if not current_subset:
                state['selected_index'] = None
            elif state['selected_index'] is None or state['selected_index'] >= len(current_subset):
                state['selected_index'] = 0

            for child in list_wrap.winfo_children():
                try:
                    child.destroy()
                except Exception:
                    pass
            rendered.clear()

            if not current_subset:
                empty_card = ctk.CTkFrame(
                    list_wrap,
                    fg_color=app.get_color('surface_hover'),
                    corner_radius=_safe_radius(app, 'radius_md', 8),
                    border_width=1,
                    border_color=app.get_color('surface_border')
                )
                empty_card.grid(row=0, column=0, sticky='ew', padx=spacing_sm, pady=spacing_sm)
                ctk.CTkLabel(
                    empty_card,
                    text=app._t('Keine Ergebnisse'),
                    font=ctk.CTkFont(*app.get_typography('body')),
                    text_color=app.get_color('text_secondary')
                ).pack(anchor='w', padx=spacing_md, pady=spacing_md)
                _update_counts()
                return

            # Game Changer 1: Gruppierte Darstellung
            if state.get('grouped'):
                _render_grouped(current_subset)
            else:
                for idx, finding in enumerate(current_subset):
                    _create_row(list_wrap, idx, finding)

            _highlight()
            _update_counts()
            list_wrap.update_idletasks()

        # Game Changer 1: Gruppierte Darstellung
        group_states = {}  # {category: {'expanded': bool, 'frame': ctk.CTkFrame}}
        
        def _render_grouped(subset):
            """Rendert Findings gruppiert nach Kategorie."""
            from collections import defaultdict
            
            # Gruppiere nach Kategorie
            groups = defaultdict(list)
            for finding in subset:
                cat = finding.get('category', 'other')
                groups[cat].append(finding)
            
            # Kategorie-Labels
            cat_labels = {
                'placeholders': 'Platzhalter',
                'references': 'Verweise',
                'whitespace': 'Leerzeichen',
                'structure': 'Struktur',
                'html': 'HTML',
                'terminology': 'Terminologie',
                'security': 'Sicherheit',
                'completeness': 'Vollständigkeit',
                'formatting': 'Formatierung',
                'typography': 'Typografie',
                'consistency': 'Konsistenz',
                'other': 'Sonstige'
            }
            
            # Sortiere Gruppen nach Anzahl (absteigend)
            sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)
            
            row_counter = 0
            global_idx = 0
            
            for cat, cat_findings in sorted_groups:
                cat_label = cat_labels.get(cat, cat.title())
                cat_count = len(cat_findings)
                
                # Gruppenkopf
                group_container = ctk.CTkFrame(
                    list_wrap,
                    fg_color=app.get_color('surface_hover'),
                    corner_radius=_safe_radius(app, 'radius_md', 8),
                    border_width=1,
                    border_color=app.get_color('surface_border')
                )
                group_container.grid(row=row_counter, column=0, sticky='ew', padx=spacing_sm, pady=(spacing_md, 0))
                row_counter += 1
                
                # State für diese Gruppe
                is_expanded = group_states.get(cat, {}).get('expanded', True)
                
                # Header mit Expand/Collapse
                header = ctk.CTkFrame(group_container, fg_color=app.get_color('transparent'))
                header.pack(fill='x', padx=spacing_md, pady=spacing_sm)
                
                toggle_symbol = '▼' if is_expanded else '▶'
                header_label = ctk.CTkLabel(
                    header,
                    text=f"{toggle_symbol} {cat_label} ({cat_count})",
                    font=ctk.CTkFont(*app.get_typography('label_bold')),
                    text_color=app.get_color('text_primary'),
                    anchor='w'
                )
                header_label.pack(side='left', fill='x', expand=True)
                
                # Content-Container
                content = ctk.CTkFrame(group_container, fg_color=app.get_color('transparent'))
                
                def _toggle_group(cat=cat, content=content, header_label=header_label, cat_label=cat_label, cat_count=cat_count):
                    current = group_states.get(cat, {}).get('expanded', True)
                    group_states[cat] = {'expanded': not current}
                    
                    if group_states[cat]['expanded']:
                        content.pack(fill='x', padx=spacing_sm, pady=(0, spacing_sm))
                        header_label.configure(text=f"▼ {cat_label} ({cat_count})")
                    else:
                        content.pack_forget()
                        header_label.configure(text=f"▶ {cat_label} ({cat_count})")
                
                header.bind('<Button-1>', lambda e, cat=cat: _toggle_group(cat))
                header_label.bind('<Button-1>', lambda e, cat=cat: _toggle_group(cat))
                
                # Findings in dieser Gruppe
                if is_expanded:
                    content.pack(fill='x', padx=spacing_sm, pady=(0, spacing_sm))
                    
                    for finding in cat_findings:
                        _create_row(content, global_idx, finding, in_group=True)
                        global_idx += 1
                else:
                    global_idx += len(cat_findings)

        # Keyboard navigation
        def _move_selection(delta):
            if not current_subset: return
            idx=state['selected_index'] if state['selected_index'] is not None else 0
            idx=max(0, min(len(current_subset)-1, idx+delta))
            state['selected_index']=idx
            _highlight()
            _ensure_visible(idx)
        def _copy_selected():
            try:
                if state['selected_index'] is None or state['selected_index']>=len(current_subset): return
                f=current_subset[state['selected_index']]
                txt=_format_text(f)
                if getattr(app,'root',None): app.root.clipboard_clear(); app.root.clipboard_append(txt)
                _toast(app, app._t('Eintrag kopiert'),'success')
            except Exception: pass
        list_wrap.bind_all('<Up>', lambda e: _move_selection(-1))
        list_wrap.bind_all('<Down>', lambda e: _move_selection(1))
        list_wrap.bind_all('<Return>', lambda e: _copy_selected())
        list_wrap.bind_all('<Control-c>', lambda e: _copy_selected())
        def _reset_all_filters():
            try:
                _set_severity('ALL')
                _set_checker('ALL')
                query_var.set('')
                _set_sort('severity')
            except Exception:
                pass
        list_wrap.bind_all('<Control-l>', lambda e: _reset_all_filters())
        
        # CRITICAL: Initial render - call directly and synchronously
        print("DEBUG: ========== INITIAL RENDER STARTING ==========")
        print(f"DEBUG: current_subset before render = {len(current_subset)} items")
        print(f"DEBUG: state = {state}")
        try:
            _render_list()
            print(f"DEBUG: Initial _render_list() completed - current_subset now has {len(current_subset)} items")
            print(f"DEBUG: rendered dict has {len(rendered)} entries")
            print("DEBUG: ========== INITIAL RENDER COMPLETE ==========")
        except Exception as e:
            print(f"DEBUG ERROR: Initial _render_list() FAILED: {e}")
            import traceback
            traceback.print_exc()

    # === END OF _render_findings_block function ===
    
    # --- REMOVED BROKEN CALLS: _set_phase, _set_severity etc. were calling functions that only exist inside _render_findings_block ---
    # These calls were causing NameError crashes. The _render_findings_block function is now self-contained.
    
    # Quick Win 4: Keyboard Navigation (J/K für Navigation, Space für Details, C für Copy)
    try:
        # Findings-spezifische Navigation
        def _navigate_findings(direction: int):
            """Navigate up/down in findings list (J/K keys)."""
            if view_state['mode'] != 'findings':
                return
            
            # Zugriff auf findings state (über closure)
            try:
                findings_container = body_container.winfo_children()[0] if body_container.winfo_children() else None
                if not findings_container:
                    return
                    
                # Simuliere Pfeiltasten für Scroll
                if direction < 0:  # Up
                    findings_container.event_generate('<Up>')
                else:  # Down
                    findings_container.event_generate('<Down>')
            except Exception:
                pass
        
        def _copy_selected():
            """Copy selected finding to clipboard (C key)."""
            if view_state['mode'] != 'findings':
                return
            try:
                if getattr(app, 'root', None):
                    app.root.event_generate('<<Copy>>')
            except Exception:
                pass
        
        # Tab Navigation (Left/Right)
        def _cycle(delta:int):
            modes=[v for _,v in tab_buttons]
            cur=view_state['mode']
            if cur in modes:
                idx=modes.index(cur); new=modes[(idx+delta)%len(modes)]; _set_mode(new)
        
        # Keyboard Shortcuts
        card.bind('<Left>', lambda e: _cycle(-1))
        card.bind('<Right>', lambda e: _cycle(1))
        card.bind('<Control-Tab>', lambda e: _cycle(1))
        card.bind('<Control-1>', lambda e: _set_mode('overview'))
        card.bind('<Control-2>', lambda e: _set_mode('phases'))
        card.bind('<Control-3>', lambda e: _set_mode('findings'))
        
        # Quick Win 4: J/K Navigation, Space, C
        card.bind('<j>', lambda e: _navigate_findings(1))
        card.bind('<k>', lambda e: _navigate_findings(-1))
        card.bind('<c>', lambda e: _copy_selected())
        card.bind('<space>', lambda e: _navigate_findings(1))  # Space = next
        
        # Ctrl+F Fokus auf Suchfeld (falls Findings Tab)
        def _focus_search():
            try:
                if view_state['mode']!='findings':
                    _set_mode('findings')
                ent=getattr(body_container,'_findings_search_entry',None)
                if ent and ent.winfo_exists():
                    ent.focus_set(); ent.icursor('end')
            except Exception: pass
        card.bind('<Control-f>', lambda e: _focus_search())
    except Exception: pass
    # AB HIER: Legacy Code (Summary/Severity/Grammar/Findings) verbleibt unten für Rückwärtskompatibilität (teilweise jetzt durch neue Renderer genutzt)
    lines = []  # (Legacy Variable – wird teils nicht mehr genutzt, belassen für Abwärtskompatibilität)
    # Zusätzliche Kennzahlen falls verfügbar
    try:
        if isinstance(metrics, dict) and metrics:
                def _fmt_pct(v):
                    try:
                        if v is None:
                            return '–'
                        if isinstance(v, (int, float)) and v <= 1:
                            return f"{v*100:.1f}%"
                        return f"{v:.2f}" if isinstance(v, (int, float)) else str(v)
                    except Exception:
                        return str(v)
                if 'numeric_consistency' in metrics:
                    lines.append(app._t('Numeric consistency') + f": {_fmt_pct(metrics.get('numeric_consistency'))}")
                if 'untranslated_ratio' in metrics:
                    translated_ratio_val = None
                    untranslated_ratio_val = None
                    try:
                        untranslated_ratio_val = float(metrics.get('untranslated_ratio') or 0)
                        translated_ratio_val = max(0.0, min(1.0, 1 - untranslated_ratio_val))
                    except Exception:
                        translated_ratio_val = None
                    segments_total = metrics.get('segments_total') or metrics.get('pair_count')
                    segments_translated_val = metrics.get('segments_translated')
                    segments_untranslated_val = metrics.get('segments_untranslated')
                    legacy_parts: list[str] = []
                    if translated_ratio_val is not None:
                        translated_txt = f"{app._t('Übersetzt')}: {_fmt_pct(translated_ratio_val)}"
                        if isinstance(segments_translated_val, int) and isinstance(segments_total, int) and segments_total > 0:
                            translated_txt += f" ({segments_translated_val}/{segments_total})"
                        legacy_parts.append(translated_txt)
                    if untranslated_ratio_val is not None:
                        untranslated_txt = f"{app._t('Unübersetzt')}: {_fmt_pct(untranslated_ratio_val)}"
                        if isinstance(segments_untranslated_val, int) and isinstance(segments_total, int) and segments_total > 0:
                            untranslated_txt += f" ({segments_untranslated_val}/{segments_total})"
                        legacy_parts.append(untranslated_txt)
                    legacy_value = ' | '.join(legacy_parts) if legacy_parts else _fmt_pct(translated_ratio_val)
                    lines.append(app._t('Übersetzungsquote') + f": {legacy_value}")
                if 'avg_length_ratio' in metrics:
                    lines.append(app._t('Avg length ratio') + f": {metrics.get('avg_length_ratio')}")
                if 'length_ratio_deviation' in metrics:
                    lines.append(app._t('Length ratio deviation') + f": {metrics.get('length_ratio_deviation')}")
                if 'completeness' in metrics:
                    lines.append(app._t('Completeness') + f": {_fmt_pct(metrics.get('completeness'))}")
    except Exception:
        pass
    crit = summary.get('critical') if isinstance(summary, dict) else None
    maj = summary.get('major') if isinstance(summary, dict) else None
    mino = summary.get('minor') if isinstance(summary, dict) else None
    total_find = summary.get('count') if isinstance(summary, dict) else None
    if 'critical' in summary:
        lines.append(app._t('Critical issues') + f": {crit}")
    if 'major' in summary:
        lines.append(app._t('Major issues') + f": {maj}")
    if 'minor' in summary:
        lines.append(app._t('Minor issues') + f": {mino}")
    if 'count' in summary:
        lines.append(app._t('Total findings') + f": {total_find}")
    if 'analysis_time_sec' in data and isinstance(data['analysis_time_sec'], (int, float)):
        lines.append(app._t('Analysis time') + f": {data['analysis_time_sec']:.1f}s")
    if lines:
        # Legacy Summary Anzeige entfällt im neuen Overview (bereits integriert) – belassen falls externe Aufrufe erwarten
        lbl_summary = None
        def _wrap_sum(_=None):
            try:
                if lbl_summary and lbl_summary.winfo_exists():
                    w = lbl_summary.winfo_width()
                    if w>0:
                        lbl_summary.configure(wraplength=int(w*0.95))
            except Exception:
                pass
        if lbl_summary:
            lbl_summary.bind('<Configure>', _wrap_sum)

        # Severity Balken (kritisch/major/minor) falls Daten vorhanden
    # Legacy Severity Block entfällt (neue Severity Darstellung in Overview)
        # Hinweisbanner für Checker Verfügbarkeit
    # Legacy Grammar Status entfällt (jetzt in Overview integriert)
    # (Legacy Findings Block entfernt – neue Tabs verwenden Befunde-Ansicht)

        try:
            if hasattr(app, 'update_status'):
                app.update_status(app._t('Quality analysis completed') + (f" – {score_view}" if score_view != '–' else ''))
        except Exception as e:
            _debug(app, f"Status Update Fehler: {e}")
        try:
            _toast(app, app._t('Quality analysis completed successfully!'), 'success')
        except Exception as e:
            _debug(app, f"Toast Fehler: {e}")

        # Plugins optional
        plugin_results: List[Any] = []
        try:
            if getattr(app, 'loaded_rules', None) and hasattr(app, '_analyze_with_plugins'):
                ctx = {"phase": "post", "ts": time.time()}
                plugin_results = app._analyze_with_plugins(ctx) or []
        except Exception:
            plugin_results = []
        if plugin_results:
            plugin_parent = card  # Übersichtlicher unter Hauptkarte anhängen
            plug = ctk.CTkFrame(plugin_parent, fg_color=app.get_color('surface_hover'), corner_radius=radius_md)
            plug.pack(fill='x', pady=(spacing_lg, 0))
            header_plug = ctk.CTkFrame(plug, fg_color=app.get_color('transparent'))
            header_plug.pack(fill='x')
            ctk.CTkLabel(header_plug, text=app._t('Plugin results'), font=ctk.CTkFont(*app.get_typography('subheading')),
                         text_color=app.get_color('text_primary')).pack(side='left', padx=spacing_lg, pady=(spacing_lg, spacing_lg//3))
            accordion_state = {'open': False}
            def _toggle_plugins():
                try:
                    accordion_state['open'] = not accordion_state['open']
                    _render_plugins()
                except Exception:
                    pass
            btn_plug = ctk.CTkButton(header_plug, text=app._t('Show'), command=_toggle_plugins,
                                      fg_color=app.get_color('primary'), hover_color=app.get_color('primary_hover'),
                                      text_color=app.get_color('text_inverse'), width=90, height=28)
            btn_plug.pack(side='right', padx=spacing_lg)
            plug_container = ctk.CTkFrame(plug, fg_color=app.get_color('transparent'))
            plug_container.pack(fill='x')

            def _render_plugins():
                for w in list(plug_container.winfo_children()):
                    try: w.destroy()
                    except Exception: pass
                if not accordion_state['open']:
                    btn_plug.configure(text=app._t('Show'))
                    return
                btn_plug.configure(text=app._t('Hide'))
                for res in plugin_results:
                    try:
                        rid = getattr(res, 'rule', 'plugin')
                        summ = getattr(res, 'summary', str(res))
                        ctk.CTkLabel(plug_container, text=f"- {rid}: {summ}"[:400], font=ctk.CTkFont(*app.get_typography('body')),
                                     text_color=app.get_color('text_primary'), anchor='w', justify='left').pack(fill='x', padx=spacing_lg, pady=2)
                    except Exception:
                        continue
            _render_plugins()  # initial collapsed

        # Events & Report nach UI
        try:
            if getattr(app, 'event_bus', None):
                # Vereinheitlichte Payload analog analysis.done (summary + findings)
                payload = {
                    'summary': summary,
                    'findings': findings,
                    'plugins': plugin_results,
                    'ui_completed_ts': time.time(),
                    # Zusatz für rückwärtskompatible Listener
                    'findings_count': len(findings),
                    'plugins_count': len(plugin_results),
                    'overall_score': raw_score if isinstance(raw_score, (int, float)) else None
                }
                app.event_bus.publish('analysis.ui.completed', payload)
        except Exception: pass
        try:
            if hasattr(app, '_export_and_publish_report'):
                if AnalysisReport and Finding:
                    # Findings in Modell mappen (severity Konvertierung)
                    model_findings: List[Any] = []
                    for f in findings:
                        try:
                            sev = f.get('severity') or 'info'
                            sev_norm = {
                                'critical': 'error',
                                'major': 'warning',
                                'minor': 'info'
                            }.get(sev, sev if sev in ('error','warning','info') else 'info')
                            rule = f.get('rule_id') or f.get('rule') or 'rule'
                            msg = f.get('message') or ''
                            model_findings.append(Finding(rule=rule, message=msg[:400], severity=sev_norm))
                        except Exception:
                            continue
                    ctx = {
                        'source_files': getattr(app.uploaded_files, 'get', lambda *_: [])('source', []) if hasattr(app, 'uploaded_files') else [],
                        'translation_files': getattr(app.uploaded_files, 'get', lambda *_: [])('translation', []) if hasattr(app, 'uploaded_files') else [],
                        'ui_completed_ts': time.time(),
                        'phase': 'ui'
                    }
                    report = AnalysisReport.create(
                        overall_score=raw_score if isinstance(raw_score, (int, float)) else None,
                        plugins_run=len(plugin_results),
                        findings=model_findings,
                        context=ctx
                    )
                    try:
                        report.file_counts = {
                            'source': len(ctx['source_files']),
                            'translation': len(ctx['translation_files'])
                        }
                    except Exception:
                        pass
                    app._export_and_publish_report(report)
                else:  # Fallback ursprünglicher Dict Weg
                    app._export_and_publish_report({
                        'summary': summary, 'findings': findings,
                        'quality_score': raw_score if isinstance(raw_score, (int, float)) else None,
                        'context': {
                            'source_files': getattr(app.uploaded_files, 'get', lambda *_: [])('source', []) if hasattr(app, 'uploaded_files') else [],
                            'translation_files': getattr(app.uploaded_files, 'get', lambda *_: [])('translation', []) if hasattr(app, 'uploaded_files') else [],
                            'ui_completed_ts': time.time()
                        }
                    })
        except Exception:
            pass
    # (Global Fehler bereits in Teilblöcken abgefangen)
    
    # CRITICAL FIX: Initial render - must call _set_mode to show default tab content
    print(f"DEBUG: Triggering initial render for mode '{view_state['mode']}'")
    try:
        _set_mode(view_state['mode'])
        print(f"DEBUG: Initial _set_mode('{view_state['mode']}') completed successfully")
    except Exception as e:
        print(f"DEBUG ERROR: Initial _set_mode failed: {e}")
        import traceback
        traceback.print_exc()


def _safe_radius(app, token: str, fallback: int) -> int:
    try:
        ds = getattr(app, 'design_system', None)
        if isinstance(ds, dict):
            return int(ds.get('components', {}).get('borders', {}).get(token, fallback))
    except Exception:
        pass
    return fallback
