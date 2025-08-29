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
"""
from __future__ import annotations
import time
import customtkinter as ctk
from typing import Any, Dict, List

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
    summary = data.get('summary', {}) or {}
    metrics = data.get('metrics') if isinstance(data.get('metrics'), dict) else {}
    findings: List[Dict[str, Any]] = data.get('findings', []) if isinstance(data.get('findings'), list) else []
    grammar_used = summary.get('grammar_checkers_used') if isinstance(summary, dict) else None
    grammar_disabled = summary.get('grammar_checkers_disabled') if isinstance(summary, dict) else None
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
    spacing_xl = app.get_spacing('xl') if hasattr(app, 'get_spacing') else 32
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
    view_state = {'mode': 'overview'}
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

    def _clear_body():
        for w in list(body_container.winfo_children()):
            try: w.destroy()
            except Exception: pass

    def _section_card(parent, title: str, tone: str='surface_hover'):
        frm = ctk.CTkFrame(parent, fg_color=app.get_color(tone), corner_radius=radius_md)
        frm.pack(fill='x', pady=(0, spacing_lg))
        try:
            ctk.CTkLabel(frm, text=title, font=ctk.CTkFont(*app.get_typography('subheading')),
                         text_color=app.get_color('text_primary')).pack(anchor='w', padx=spacing_lg, pady=(spacing_lg//1.5, 2))
        except Exception:
            pass
        inner = ctk.CTkFrame(frm, fg_color=app.get_color('transparent'))
        inner.pack(fill='x', padx=spacing_lg, pady=(0, spacing_lg))
        return inner

    # Originaler body Inhalt wird in _render_overview() verschoben
    def _render_overview(body: ctk.CTkFrame):
        # Score Frame + Summary + Severity (re-Use bestehender Code unten)
        _render_score_block(body)
        _render_summary_block(body)
        _render_severity_block(body)
        _render_grammar_status(body)

    def _render_phases(body: ctk.CTkFrame):
        phase_reports = []
        for key,label in [ ('phase1_report', 'Phase 1'), ('phase2_report', 'Phase 2'), ('phase3_report','Phase 3'), ('phase4_report','Phase 4') ]:
            rep = summary.get(key) if isinstance(summary, dict) else None
            if isinstance(rep, dict):
                phase_reports.append((label, rep))
        if not phase_reports:
            ctk.CTkLabel(body, text=app._t('Keine Phasenberichte verfügbar'), font=ctk.CTkFont(*app.get_typography('body')),
                         text_color=app.get_color('text_secondary')).pack(anchor='w')
            return
        # Erklärende Texte je Phase (UX)
        phase_explain = {
            'Phase 1': app._t('Prüft Zahlen, Datumsangaben und Maßeinheiten auf Übereinstimmung zwischen Quelle und Ziel.'),
            'Phase 2': app._t('Analysiert die Länge der Segmente (Zeichen) und erkennt untypische Abweichungen.'),
            'Phase 3': app._t('Überprüft Vollständigkeit: Fehlen Teile oder bleiben Segmente unübersetzt?'),
            'Phase 4': app._t('Strukturelle Konsistenz: Klammern, Anführungszeichen und Platzhalter in beiden Sprachen identisch?')
        }
        for label, rep in phase_reports:
            inner = _section_card(body, app._t(label))
            try:
                # Beschreibung oben
                desc = phase_explain.get(label)
                if desc:
                    ctk.CTkLabel(inner, text=desc, font=ctk.CTkFont(*app.get_typography('caption')),
                                 text_color=app.get_color('text_secondary'), justify='left').pack(anchor='w', pady=(0,4))
                # Kennzahlen extrahieren
                lines = []
                for k,v in rep.items():
                    if isinstance(v,(int,float,str)) and k not in ('samples','by_severity','by_code','by_category'):
                        lines.append(f"{k}: {v}")
                if 'by_severity' in rep and isinstance(rep['by_severity'], dict):
                    sev_map = rep['by_severity']
                    sev_line = ", ".join(f"{k}={v}" for k,v in sev_map.items())
                    lines.append(app._t('Schweregrade')+': '+sev_line)
                ctk.CTkLabel(inner, text='\n'.join(lines) or app._t('Keine Daten'),
                             font=ctk.CTkFont(*app.get_typography('body')), justify='left',
                             text_color=app.get_color('text_primary')).pack(anchor='w')
                # Samples (optional)
                if isinstance(rep.get('samples'), dict) and rep['samples']:
                    samples_frame = ctk.CTkFrame(inner, fg_color=app.get_color('surface_hover'), corner_radius=radius_md)
                    samples_frame.pack(fill='x', pady=(spacing_md,0))
                    try:
                        ctk.CTkLabel(samples_frame, text=app._t('Beispiele'), font=ctk.CTkFont(*app.get_typography('caption')),
                                     text_color=app.get_color('text_secondary')).pack(anchor='w', padx=spacing_md, pady=(spacing_md//2,2))
                    except Exception: pass
                    for code,msg in rep['samples'].items():
                        ctk.CTkLabel(samples_frame, text=f"[{code}] {msg}"[:300], font=ctk.CTkFont(*app.get_typography('body')),
                                     text_color=app.get_color('text_primary'), anchor='w', justify='left').pack(fill='x', padx=spacing_md, pady=2)
            except Exception:
                continue

    def _render_findings(body: ctk.CTkFrame):
        # Re-use bestehendes Findings UI unten – hier nur Einhängen
        _render_findings_block(body)

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
        score_frame = ctk.CTkFrame(parent, fg_color=app.get_color('surface_hover'), corner_radius=radius_md)
        score_frame.pack(fill='x', pady=(0, spacing_lg))
        try:
            lbl_score = ctk.CTkLabel(score_frame,
                                     text=app._t('Overall Quality Score: ') + score_view,
                                     font=ctk.CTkFont(*app.get_typography('heading')),
                                     text_color=app.get_color('success'))
            lbl_score.pack(anchor='w', padx=spacing_lg, pady=(spacing_lg//1.5, 4))
        except Exception: pass
        if isinstance(score_pct, (int, float)):
            try:
                score_bar = ctk.CTkProgressBar(score_frame)
                score_bar.pack(fill='x', padx=spacing_lg, pady=(0, spacing_lg//2))
                score_bar.set(score_pct/100)
            except Exception: pass
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
                # Accordion Toggle
                acc_state = {'open': False}
                header_row = ctk.CTkFrame(breakdown_frame, fg_color=app.get_color('transparent'))
                header_row.pack(fill='x')
                if grade:
                    ctk.CTkLabel(header_row, text=app._t('Quality grade') + f": {grade}",
                                 font=ctk.CTkFont(*app.get_typography('subheading')),
                                 text_color=app.get_color('text_primary')).pack(side='left')
                toggle_btn = ctk.CTkButton(header_row, text=app._t('Details anzeigen'), width=140, height=28,
                                            fg_color=app.get_color('primary'), hover_color=app.get_color('primary_hover'),
                                            text_color=app.get_color('text_inverse'))
                toggle_btn.pack(side='right')
                details_container = ctk.CTkFrame(breakdown_frame, fg_color=app.get_color('transparent'))
                def _render_details():
                    for w in list(details_container.winfo_children()):
                        try: w.destroy()
                        except Exception: pass
                    if not acc_state['open']:
                        toggle_btn.configure(text=app._t('Details anzeigen'))
                        return
                    toggle_btn.configure(text=app._t('Details ausblenden'))
                    for title, val_txt, desc in sub_scores:
                        row = ctk.CTkFrame(details_container, fg_color=app.get_color('transparent'))
                        row.pack(fill='x', pady=2)
                        ctk.CTkLabel(row, text=f"{title}: {val_txt}", font=ctk.CTkFont(*app.get_typography('body')),
                                     text_color=app.get_color('text_primary')).pack(anchor='w')
                        if desc:
                            ctk.CTkLabel(row, text=desc, font=ctk.CTkFont(*app.get_typography('caption')),
                                         text_color=app.get_color('text_secondary')).pack(anchor='w')
                def _toggle():
                    acc_state['open'] = not acc_state['open']
                    _render_details()
                toggle_btn.configure(command=_toggle)
                details_container.pack(fill='x', pady=(spacing_md//2,0))
                _render_details()
        except Exception: pass

    def _render_summary_block(parent):
        # Zusammenfassung Kennzahlen
        metrics_block = []
        try:
            if isinstance(metrics, dict) and metrics:
                def _fmt_pct(v):
                    try:
                        if v is None: return '–'
                        if isinstance(v,(int,float)) and v <= 1: return f"{v*100:.1f}%"
                        return f"{v:.2f}" if isinstance(v,(int,float)) else str(v)
                    except Exception: return str(v)
                if 'numeric_consistency' in metrics:
                    metrics_block.append(app._t('Numerische Konsistenz (Zahlen/Einheiten)') + f": {_fmt_pct(metrics.get('numeric_consistency'))}")
                if 'untranslated_ratio' in metrics:
                    try: inv = 1 - float(metrics.get('untranslated_ratio') or 0)
                    except Exception: inv = None
                    metrics_block.append(app._t('Anteil übersetzter Segmente') + f": {_fmt_pct(inv)}")
                if 'avg_length_ratio' in metrics:
                    metrics_block.append(app._t('Durchschnittliches Längenverhältnis') + f": {metrics.get('avg_length_ratio')}" )
                if 'length_ratio_deviation' in metrics:
                    metrics_block.append(app._t('Längenabweichung (Standardabweichung)') + f": {metrics.get('length_ratio_deviation')}" )
                if 'completeness' in metrics:
                    metrics_block.append(app._t('Vollständigkeit (nicht leer)') + f": {_fmt_pct(metrics.get('completeness'))}")
        except Exception: pass
        if metrics_block:
            inner = _section_card(parent, app._t('Zusammenfassung'))
            ctk.CTkLabel(inner, text="\n".join(f"• {l}" for l in metrics_block),
                         font=ctk.CTkFont(*app.get_typography('body')),
                         text_color=app.get_color('text_primary'), justify='left').pack(anchor='w')

    def _render_severity_block(parent):
        crit = summary.get('critical') if isinstance(summary, dict) else None
        maj = summary.get('major') if isinstance(summary, dict) else None
        mino = summary.get('minor') if isinstance(summary, dict) else None
        if not any(isinstance(x,int) for x in (crit,maj,mino)):
            return
        sv_inner = _section_card(parent, app._t('Severity'))
        total_s = sum(x for x in [crit, maj, mino] if isinstance(x,int) and x>=0)
        lines = []
        if isinstance(crit,int): lines.append(app._t('Critical')+f": {crit}")
        if isinstance(maj,int): lines.append(app._t('Major')+f": {maj}")
        if isinstance(mino,int): lines.append(app._t('Minor')+f": {mino}")
        if total_s:
            lines.append(app._t('Total')+f": {total_s}")
        ctk.CTkLabel(sv_inner, text=' | '.join(lines), font=ctk.CTkFont(*app.get_typography('body')),
                     text_color=app.get_color('text_primary')).pack(anchor='w')
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

    def _render_grammar_status(parent):
        if not (grammar_used or grammar_disabled): return
        inner = _section_card(parent, app._t('Grammar Checker Status'))
        parts = []
        if grammar_used: parts.append(app._t('Aktiv')+': '+", ".join(grammar_used))
        if grammar_disabled: parts.append(app._t('Deaktiviert')+': '+", ".join(grammar_disabled))
        status_line = ' | '.join(parts)
        if summary.get('grammar_cache_hit'): status_line += ' ['+app._t('Cache-Treffer')+']'
        ctk.CTkLabel(inner, text=status_line, font=ctk.CTkFont(*app.get_typography('caption')),
                     text_color=app.get_color('text_secondary'), anchor='w', justify='left').pack(fill='x')

    # Findings Block (vollständig neu implementiert – Virtualisierung, Sortierung, Counts, Tastatur)
    def _render_findings_block(parent):
        if not findings:
            ctk.CTkLabel(parent, text=app._t('No findings detected'),
                         font=ctk.CTkFont(*app.get_typography('body')),
                         text_color=app.get_color('text_secondary')).pack(anchor='w')
            return
        container = _section_card(parent, app._t('Findings'))
        controls = ctk.CTkFrame(container, fg_color=app.get_color('transparent'))
        controls.pack(fill='x')
        state = {
            'severity': 'ALL',
            'checker': 'ALL',
            'query': '',
            'sort': 'severity',
            'sort_dir': 'asc',
            'selected_index': None,
            'virtual_enabled': False,
        }
        try:
            if _cfg:
                for k in ('severity','checker','sort','sort_dir'):
                    val=_cfg.get(f'analysis.ui.findings.{k}')
                    if isinstance(val,str): state[k]=val
        except Exception: pass

        # Helper: persist
        def _persist():
            try:
                if _cfg:
                    _cfg.set('analysis.ui.findings.severity', state['severity'])
                    _cfg.set('analysis.ui.findings.checker', state['checker'])
                    _cfg.set('analysis.ui.findings.sort', state['sort'])
                    _cfg.set('analysis.ui.findings.sort_dir', state['sort_dir'])
            except Exception: pass

        # Severity Filter
        sev_frame=ctk.CTkFrame(controls, fg_color=app.get_color('transparent'))
        sev_frame.pack(side='left')
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
                b.pack(side='left', padx=2)
                severity_buttons.append((b,val))
            except Exception: continue

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

        # Actions
        actions=ctk.CTkFrame(controls, fg_color=app.get_color('transparent'))
        actions.pack(side='right')
        def _subset():
            base=findings
            try:
                sub=[f for f in base if (state['severity']=='ALL' or f.get('severity')==state['severity'])]
                if state['checker']!='ALL':
                    sub=[f for f in sub if (f.get('checker') or '').lower()==state['checker']]
                if state['query']:
                    q=state['query']
                    sub=[f for f in sub if q in (f.get('message') or '').lower() or q in (f.get('rule_id') or f.get('rule') or '').lower()]
                reverse=(state['sort_dir']=='desc')
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

        # Scroll+Virtualisation Setup
        list_wrap=ctk.CTkFrame(container, fg_color=app.get_color('transparent'))
        list_wrap.pack(fill='both', expand=True, pady=(spacing_md,0))
        canvas=ctk.CTkCanvas(list_wrap, highlightthickness=0, bg=app.get_color('surface'))
        vsb=ctk.CTkScrollbar(list_wrap, orientation='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        inner_holder=ctk.CTkFrame(canvas, fg_color=app.get_color('transparent'))
        window_id=canvas.create_window((0,0), window=inner_holder, anchor='nw')

        # Dynamic rows
        ROW_HEIGHT=38  # heuristisch (Label + padding)
        VIRTUAL_THRESHOLD=5000
        rendered={}  # index -> (frame, label)
        last_visible=(None,None)

        # Selection Highlight
        def _highlight():
            for idx,(frm,lbl) in list(rendered.items()):
                try:
                    if idx==state['selected_index']:
                        frm.configure(fg_color=app.get_color('surface_hover'))
                    else:
                        frm.configure(fg_color=app.get_color('transparent'))
                except Exception: pass

        def _update_counts():
            try:
                base=[f for f in findings]
                # apply checker+query only
                def ok(f):
                    if state['checker']!='ALL' and (f.get('checker') or '').lower()!=state['checker']: return False
                    if state['query']:
                        q=state['query']
                        if q not in (f.get('message') or '').lower() and q not in (f.get('rule_id') or f.get('rule') or '').lower(): return False
                    return True
                base=[f for f in base if ok(f)]
                sev_counts={'critical':0,'major':0,'minor':0}
                checker_counts={}
                for f in base:
                    s=f.get('severity')
                    if s in sev_counts: sev_counts[s]+=1
                    chk=(f.get('checker') or '').lower() or '—'
                    checker_counts[chk]=checker_counts.get(chk,0)+1
                total=len(base)
                for b,v in severity_buttons:
                    try:
                        base_lab=b.cget('text').split(' (')[0]
                        if v=='ALL': b.configure(text=f"{base_lab.split(' (')[0]} ({total})")
                        else: b.configure(text=f"{base_lab.split(' (')[0]} ({sev_counts.get(v,0)})")
                    except Exception: pass
                for b,v in checker_buttons:
                    try:
                        base_lab=b.cget('text').split(' (')[0]
                        if v=='ALL': b.configure(text=f"{base_lab} ({total})")
                        else: b.configure(text=f"{base_lab} ({checker_counts.get(v,0)})")
                    except Exception: pass
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
            sev=f.get('severity') or 'info'
            return f"[{sev}] {(f.get('rule_id') or f.get('rule') or 'rule')}: {(f.get('message') or '')}"[:900]

        def _severity_token(sev):
            return {'critical':'error','major':'warning','minor':'info'}.get(sev,'text_primary')

        def _create_row(parent, idx, f):
            sev=f.get('severity') or 'info'
            row=ctk.CTkFrame(parent, fg_color=app.get_color('transparent'))
            row.place(x=0, y=idx*ROW_HEIGHT, relwidth=1, height=ROW_HEIGHT)
            bar=ctk.CTkFrame(row, width=6, fg_color=app.get_color(_severity_token(sev)))
            bar.pack(side='left', fill='y')
            txt=_format_text(f)
            lbl=ctk.CTkLabel(row,text=txt,anchor='w',justify='left',font=ctk.CTkFont(*app.get_typography('body')),
                              text_color=app.get_color(_severity_token(sev)))
            lbl.pack(side='left', fill='both', expand=True, padx=spacing_md, pady=2)
            def _wrap(e=None,l=lbl): _debounce_wrap(l)
            lbl.bind('<Configure>', _wrap)
            def _copy_single(e=None, _text=txt):
                try:
                    if getattr(app,'root',None): app.root.clipboard_clear(); app.root.clipboard_append(_text)
                    _toast(app, app._t('Eintrag kopiert'),'success')
                except Exception: pass
            lbl.bind('<Double-Button-1>', _copy_single)
            def _select(e=None):
                state['selected_index']=idx; _highlight()
            row.bind('<Button-1>', _select); lbl.bind('<Button-1>', _select)
            rendered[idx]=(row,lbl)
            return row

        def _subset_and_mode():
            sub=_subset()
            state['virtual_enabled']=len(sub) >= VIRTUAL_THRESHOLD
            return sub

        current_subset=[]

        def _build_scrollregion():
            try:
                if state['virtual_enabled']:
                    h=len(current_subset)*ROW_HEIGHT
                    inner_holder.configure(height=h)
                    canvas.configure(scrollregion=(0,0, inner_holder.winfo_width(), h))
                else:
                    canvas.configure(scrollregion=canvas.bbox('all'))
            except Exception: pass

        def _render_visible():
            if not state['virtual_enabled']: return
            try:
                first=int(canvas.canvasy(0)//ROW_HEIGHT)-5; last=int(canvas.canvasy(canvas.winfo_height())//ROW_HEIGHT)+5
                if first<0: first=0
                if last>len(current_subset): last=len(current_subset)
                nonlocal last_visible
                if last_visible==(first,last): return
                # remove out-of-range
                for idx in list(rendered.keys()):
                    if idx < first-10 or idx > last+10:
                        frm,_=rendered.pop(idx)
                        try: frm.destroy()
                        except Exception: pass
                for idx in range(first,last):
                    if idx not in rendered:
                        _create_row(inner_holder, idx, current_subset[idx])
                last_visible=(first,last)
                _highlight()
            except Exception: pass

        def _render_list():
            # clear
            for idx,(frm,lbl) in list(rendered.items()):
                try: frm.destroy()
                except Exception: pass
            rendered.clear()
            nonlocal current_subset
            current_subset=_subset_and_mode()
            if not current_subset:
                for w in inner_holder.winfo_children():
                    try: w.destroy()
                    except Exception: pass
                inner_holder.configure(height=ROW_HEIGHT)
                ctk.CTkLabel(inner_holder,text=app._t('Keine Ergebnisse'),font=ctk.CTkFont(*app.get_typography('body')),
                             text_color=app.get_color('text_secondary')).place(x=0,y=0,relwidth=1,height=ROW_HEIGHT)
                _update_counts(); return
            # Non virtual path (uses simple pack + optional lazy batches for medium size)
            if not state['virtual_enabled']:
                for w in inner_holder.winfo_children():
                    try: w.destroy()
                    except Exception: pass
                # Decide lazy batches for >600
                if len(current_subset) <= 600:
                    for idx,f in enumerate(current_subset):
                        _create_row(inner_holder, idx, f)
                else:
                    status_lbl=ctk.CTkLabel(inner_holder,text=app._t('Lade Ergebnisse ...'),font=ctk.CTkFont(*app.get_typography('caption')),
                                             text_color=app.get_color('text_secondary'),anchor='w',justify='left')
                    status_lbl.place(x=0,y=0,relwidth=1,height=ROW_HEIGHT)
                    created={'v':0}
                    def _batch(start):
                        end=min(start+160, len(current_subset))
                        for idx in range(start,end): _create_row(inner_holder, idx, current_subset[idx])
                        created['v']=end
                        try: status_lbl.configure(text=app._t('Geladen')+f": {end}/{len(current_subset)}")
                        except Exception: pass
                        if end < len(current_subset) and getattr(app,'root',None):
                            app.root.after(15, lambda: _batch(end))
                        else:
                            try: status_lbl.configure(text=app._t('Alle Ergebnisse geladen')+f" ({len(current_subset)})")
                            except Exception: pass
                    _batch(0)
                inner_holder.configure(height=len(current_subset)*ROW_HEIGHT)
                _build_scrollregion(); _highlight(); _update_counts(); return
            # Virtual path
            inner_holder.configure(height=len(current_subset)*ROW_HEIGHT)
            _build_scrollregion(); _render_visible(); _update_counts()

        # Events
        def _on_config(event=None):
            _build_scrollregion(); _render_visible()
        inner_holder.bind('<Configure>', _on_config)
        canvas.bind('<Configure>', lambda e: (_build_scrollregion(), _render_visible()))
        canvas.bind('<Scroll>', lambda e: _render_visible())
        def _on_mousewheel(e):
            try:
                delta=-1*(e.delta//120)
                canvas.yview_scroll(delta,'units')
                _render_visible()
            except Exception: pass
        canvas.bind_all('<MouseWheel>', _on_mousewheel)

        # Keyboard navigation
        def _move_selection(delta):
            if not current_subset: return
            idx=state['selected_index'] if state['selected_index'] is not None else 0
            idx=max(0, min(len(current_subset)-1, idx+delta))
            state['selected_index']=idx; _highlight()
            # ensure visible
            if state['virtual_enabled']:
                y0=idx*ROW_HEIGHT; y1=y0+ROW_HEIGHT
                top=canvas.canvasy(0); bottom=canvas.canvasy(canvas.winfo_height())
                if y0 < top: canvas.yview_moveto(y0/(len(current_subset)*ROW_HEIGHT))
                elif y1 > bottom: canvas.yview_moveto((y1-canvas.winfo_height())/(len(current_subset)*ROW_HEIGHT))
                _render_visible()
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
        list_wrap.bind_all('<Control-l>', lambda e: (_set_severity('ALL'), _set_checker('ALL'), query_var.set(''), _set_sort('severity')) if 'query_var' in locals() else None)

        # Initial render
        _render_list()
        _set_severity(state['severity']); _set_checker(state['checker']); _set_sort(state['sort'])
        _update_counts();

    # Initial Render
    _rerender_body()
    _set_mode(view_state['mode'])  # initial Tab (persisted)
    try:
        if tab_buttons: tab_buttons[0][0].focus_set()
    except Exception: pass
    # Keyboard Navigation (Left/Right)
    try:
        def _cycle(delta:int):
            modes=[v for _,v in tab_buttons]
            cur=view_state['mode']
            if cur in modes:
                idx=modes.index(cur); new=modes[(idx+delta)%len(modes)]; _set_mode(new)
        card.bind('<Left>', lambda e: _cycle(-1))
        card.bind('<Right>', lambda e: _cycle(1))
        card.bind('<Control-Tab>', lambda e: _cycle(1))
        card.bind('<Control-1>', lambda e: _set_mode('overview'))
        card.bind('<Control-2>', lambda e: _set_mode('phases'))
        card.bind('<Control-3>', lambda e: _set_mode('findings'))
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
                    try:
                        inv = 1 - float(metrics.get('untranslated_ratio') or 0)
                    except Exception:
                        inv = None
                    lines.append(app._t('Translated ratio') + f": {_fmt_pct(inv)}")
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
                        ctk.CTkLabel(plug_container, text=f"• {rid}: {summ}"[:400], font=ctk.CTkFont(*app.get_typography('body')),
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


def _safe_radius(app, token: str, fallback: int) -> int:
    try:
        ds = getattr(app, 'design_system', None)
        if isinstance(ds, dict):
            return int(ds.get('components', {}).get('borders', {}).get(token, fallback))
    except Exception:
        pass
    return fallback
