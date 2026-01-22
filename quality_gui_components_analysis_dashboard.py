"""Analysis Dashboard Komponenten (Design-System konform).

Refaktor:
 - Entfernung harter Pixelwerte (Spacing via app.get_spacing / Design System)
 - Verwendung definierter Border-Radii aus Design-System statt "20"
 - Deutsche UI-Texte (No-Icons / No-Emoji Policy)
 - Dynamische Metriken aus aktueller Analyse (Fallbacks sicher)
 - Keine hartcodierten Farben außer über app.get_color()

Öffentliche API:
 - build_analysis_dashboard(app): Baut/aktualisiert das Analyse-Dashboard.

Erfordert (am App-Objekt):
 - get_color(token), get_typography(token), get_spacing(token)
 - event_bus.subscribe(name, fn) und optional event_bus.unsubscribe(...)
 - output_frame (CTkFrame), _t(text) (Lokalisierung)

Optionale Hooks am App-Objekt:
 - _create_metric_card(parent, title, value, color, desc, column, *, show_progress=False, value_max=100)
 - _show_analysis_placeholder(parent) oder _show_analysis_placeholder()
 - _show_analysis_results(parent) oder _show_analysis_results()
 - trigger_analysis() (wird für den CTA genutzt, falls vorhanden)
"""
from __future__ import annotations
import customtkinter as ctk
from typing import Any, Dict, Optional, Tuple
import time

__all__ = ["build_analysis_dashboard"]

# Lokalisierungsschlüssel – alle UI-Texte zentral
TEXT: Dict[str, str] = {
    'dashboard_title': "Translation Quality Analysis Dashboard",
    'quality_score': "Qualitätswert",
    'issues_found': "Gefundene Auffälligkeiten",
    'files_processed': "Verarbeitete Dateien",
    'analysis_time': "Analysedauer",
    'severity_mix': "Schweregrad-Mix",
    'no_analysis_yet': "Noch keine Analyse vorhanden",
    'phase_prefix': "Phase",
    'overall_quality_rating': "Gesamtbewertung der Übersetzungsqualität",
    'issues_detected_desc': "Erkannte potenzielle Übersetzungsauffälligkeiten",
    'files_processed_desc': "Anzahl verarbeiteter Dateien",
    'processing_time_desc': "Laufzeit der letzten Analyse",
    'severity_distribution_desc': "Verteilung kritisch / major / minor",
    'cta_analyze_now': "Jetzt analysieren",
    'timeouts_label': "Timeouts",
    'aborted_label': "Abgebrochen",
    'executed_label': "Ausgeführt",
    'total_time_label': "Gesamtzeit",
    'yes': "Ja",
    'no': "Nein",
}

# Phasen-Mapping für Fortschritt
PHASE_MAP: Dict[str, str] = {
    'load': 'Laden',
    'analyze': 'Analysieren',
    'finalize': 'Abschließen',
}

# Einheitliche Farb-Token Verwendung (nur Namen, Auflösung über _ds_get_color)
COLOR_TOKENS: Dict[str, str] = {
    'primary': 'primary',
    'info': 'info',
    'error': 'error',
    'success': 'success',
    'warning': 'warning',
    'text_muted': 'text_muted',
}


# -----------------------------
# Utility / Design-System-Helper
# -----------------------------
def run_on_ui_thread(app, fn) -> None:
    """Sichere Ausführung im UI-Thread (falls möglich)."""
    try:
        root = getattr(app, 'root', None)
        if root and hasattr(root, 'after'):
            root.after(0, fn)
        else:
            fn()
    except Exception:
        try:
            fn()
        except Exception:
            pass


def add_accessibility(app, widget, role: str, name: str) -> None:
    """Einfache Accessibility-Hilfe: bindet Enter/Space auf Buttons und optionalen Tooltip.

    Hinweis: CustomTkinter hat keinen eingebauten Tooltip – ein einfacher Tooltip via Toplevel
    wird nur erstellt, wenn name gesetzt ist und Events verfügbar sind.
    """
    try:
        # Optionaler Minimal-Tooltip
        if name and hasattr(widget, 'bind'):
            tip = {'win': None}
            def _show_tip(_=None):
                try:
                    if tip['win'] is not None:
                        return
                    x = widget.winfo_rootx() + 10
                    y = widget.winfo_rooty() + widget.winfo_height() + 6
                    tw = ctk.CTkToplevel() if hasattr(ctk, 'CTkToplevel') else None
                    if tw is None:
                        return
                    tw.overrideredirect(True)
                    tw.geometry(f"+{x}+{y}")
                    lbl = ctk.CTkLabel(tw, text=name, fg_color=_ds_get_color(app, 'surface_elevated', None),
                                       text_color=_ds_get_color(app, COLOR_TOKENS['text_muted'], _ds_get_color(app, 'gray_500', None)),
                                       font=ctk.CTkFont(*_ds_get_font(app, 'caption')))
                    lbl.pack(padx=6, pady=4)
                    tip['win'] = tw
                except Exception:
                    tip['win'] = None
            def _hide_tip(_=None):
                try:
                    if tip['win'] is not None:
                        tip['win'].destroy()
                        tip['win'] = None
                except Exception:
                    tip['win'] = None
            try:
                widget.bind('<Enter>', _show_tip)
                widget.bind('<Leave>', _hide_tip)
            except Exception:
                pass
        if isinstance(widget, ctk.CTkButton):
            try:
                cmd = getattr(widget, 'cget', lambda x: None)('command')
                if callable(cmd):
                    widget.bind('<Return>', lambda e: cmd())
                    widget.bind('<space>', lambda e: cmd())
            except Exception:
                pass
    except Exception:
        pass


def _ds_get_color(app, token: str, fallback: Optional[str] = None):
    cache = getattr(app, '_ds_color_cache', None) or {}
    if token in cache:
        return cache[token]
    try:
        val = app.get_color(token) if hasattr(app, 'get_color') else fallback
    except Exception:
        val = fallback
    if val is None and fallback is None:
        try:
            val = app.get_color('text') if hasattr(app, 'get_color') else '#000000'
        except Exception:
            val = '#000000'
    cache[token] = val
    setattr(app, '_ds_color_cache', cache)
    return val


def _ds_get_font(app, token: str) -> Tuple[str, int, str]:
    cache = getattr(app, '_ds_font_cache', None) or {}
    if token in cache:
        return cache[token]
    try:
        val = tuple(getattr(app, 'get_typography')(token))  # type: ignore
    except Exception:
        # Fallback: übliche Defaults
        val = ('Segoe UI', 14, 'normal')
    cache[token] = val
    setattr(app, '_ds_font_cache', cache)
    return val  # type: ignore


def _ds_get_spacing(app, token: str, fallback: int = 16) -> int:
    cache = getattr(app, '_ds_spacing_cache', None) or {}
    if token in cache:
        return cache[token]
    try:
        val = int(getattr(app, 'get_spacing')(token))  # type: ignore
    except Exception:
        val = fallback
    cache[token] = val
    setattr(app, '_ds_spacing_cache', cache)
    return val


def _fmt_percent(val) -> str:
    """Formatiert 0..1 oder 0..100 als "NN%"; None -> "-"."""
    try:
        if val is None:
            return "-"
        x = float(val)
        if 0 <= x <= 1:
            x *= 100.0
        return f"{x:.0f}%"
    except Exception:
        return "-"


def _fmt_duration(seconds) -> str:
    """Formatiert Sekunden in "Ns"; Werte < 0.01s -> "-"."""
    try:
        if seconds is None:
            return "-"
        s = float(seconds)
        if s < 0.01:
            return "-"
        return f"{s:.1f}s"
    except Exception:
        return "-"


def ensure_percent_number(val) -> float:
    """Skaliert 0..1 nach 0..100 und klemmt auf [0,100]. None -> 0.0"""
    try:
        if val is None:
            return 0.0
        x = float(val)
        if 0 <= x <= 1:
            x *= 100.0
        return max(0.0, min(100.0, x))
    except Exception:
        return 0.0


def _to_yes_no(app, val: Any) -> str:
    try:
        return app._t(TEXT['yes']) if bool(val) else app._t(TEXT['no'])
    except Exception:
        return TEXT['yes'] if bool(val) else TEXT['no']


def _get_ds_border_radius(app, token: str, fallback: int = 12) -> int:
    """Liest einen Border-Radius Token sicher aus dem Design-System."""
    try:
        ds = getattr(app, 'design_system', None)
        if isinstance(ds, dict):
            return int(ds.get('components', {}).get('borders', {}).get(token, fallback))
    except Exception:
        pass
    return fallback


def invalidate_ds_caches(app) -> None:
    """Leert DS-Caches, z. B. nach Theme-Wechsel."""
    for attr in ('_ds_color_cache', '_ds_font_cache', '_ds_spacing_cache'):
        if hasattr(app, attr):
            try:
                delattr(app, attr)
            except Exception:
                pass


def get_total_files(app) -> int:
    """Sichere Ermittlung der hochgeladenen Dateien (source + translation)."""
    try:
        uf = getattr(app, 'uploaded_files', {}) or {}
        s = uf.get('source') or []
        t = uf.get('translation') or []
        return (len(s) if hasattr(s, '__len__') else 0) + (len(t) if hasattr(t, '__len__') else 0)
    except Exception:
        return 0


def debounce_ui(app, key: str, fn, ms: int = 80):
    """Einfache Debounce-Funktion für UI-Thread-Operationen mittels root.after_cancel."""
    try:
        root = getattr(app, 'root', None)
        if not root or not hasattr(root, 'after'):
            return fn()
        timers = getattr(app, '_debounce_timers', None) or {}
        if key in timers:
            try:
                root.after_cancel(timers[key])
            except Exception:
                pass
        def _run():
            try:
                fn()
            finally:
                try:
                    timers.pop(key, None)
                except Exception:
                    pass
        tid = root.after(ms, _run)
        timers[key] = tid
        setattr(app, '_debounce_timers', timers)
    except Exception:
        fn()


def is_empty_metric(val: Optional[str]) -> bool:
    try:
        return (val is None) or (str(val).strip() in ('', '-'))
    except Exception:
        return True


def _should_show_telemetry(app) -> bool:
    try:
        settings = getattr(app, 'settings', {}) or {}
        dev = bool(getattr(app, '_dev_mode', False))
        # Default: Dev=True, Prod=False; Setting überschreibt
        default = True if dev else False
        return bool(settings.get('dashboard.show_telemetry', default))
    except Exception:
        return bool(getattr(app, '_dev_mode', False))


def _safe_update_metric(card_obj, key: str, *, value_new: Optional[str] = None, desc_new: Optional[str] = None, progress_value: Optional[float] = None, force: bool = False) -> None:
    """Verhindert unnötige Updates (Flackern), cached letzte Werte auf card_obj."""
    try:
        last_cache = getattr(card_obj, '_last_metric_values', None) or {}
        last_value = last_cache.get('value')
        last_desc = last_cache.get('desc')
        last_prog = last_cache.get('progress')
        same = (value_new == last_value and desc_new == last_desc and progress_value == last_prog)
        if not force and same:
            return
        if hasattr(card_obj, 'update_metric'):
            card_obj.update_metric(value_new=value_new, desc_new=desc_new, progress_value=progress_value)
        last_cache['value'] = value_new
        last_cache['desc'] = desc_new
        last_cache['progress'] = progress_value
        setattr(card_obj, '_last_metric_values', last_cache)
    except Exception:
        try:
            card_obj.update_metric(value_new, desc_new, progress_value)  # type: ignore
        except Exception:
            pass


def _extract_dynamic_metrics(app) -> Dict[str, Any]:
    """Pipeline-synchronisierte Metrik-Extraktion (robust gegen fehlende Felder)."""
    container = getattr(app, 'analysis_results', None) or getattr(app, 'current_analysis', None) or {}
    if not isinstance(container, dict):
        container = {}
    summary = container.get('summary', {}) if isinstance(container, dict) else {}
    metrics = container.get('metrics', {}) if isinstance(container, dict) else {}
    findings = container.get('findings', []) if isinstance(container, dict) else []
    issues_count = len(findings) if isinstance(findings, list) else 0

    # Quality Score (0..1 oder 0..100), Fallback auf metrics.overall_score
    raw_score = summary.get('quality_score') if isinstance(summary, dict) else None
    quality_numeric = None
    if isinstance(raw_score, (int, float)):
        quality_numeric = (raw_score * 100.0) if raw_score <= 1 else float(raw_score)
    else:
        oscore = metrics.get('overall_score')
        if isinstance(oscore, (int, float)):
            quality_numeric = (oscore * 100.0) if oscore <= 1 else float(oscore)
    quality_score = _fmt_percent(quality_numeric if quality_numeric is not None else None)

    # Dauer: summary.duration_s / summary.duration_seconds / metrics.duration_ms
    duration_s = None
    if isinstance(summary, dict):
        duration_s = summary.get('duration_s') or summary.get('duration_seconds')
    if not isinstance(duration_s, (int, float)):
        dm = metrics.get('duration_ms')
        duration_s = (dm / 1000.0) if isinstance(dm, (int, float)) else None
    duration = _fmt_duration(duration_s)

    # Files / Pairs: pair_count bevorzugt
    pair_count = metrics.get('pair_count')
    if isinstance(pair_count, int) and pair_count >= 0:
        files_processed = str(pair_count)
    else:
        try:
            files_processed = str(get_total_files(app))
        except Exception:
            files_processed = "-"

    # Severity Aggregation: metrics['severity'] dict akzeptieren und mit summary-Werten mergen (summary hat Priorität)
    sev_agg = {'critical': None, 'major': None, 'minor': None}
    try:
        if isinstance(metrics, dict):
            sev_m = metrics.get('severity')
            if isinstance(sev_m, dict):
                for k in ('critical', 'major', 'minor'):
                    v = sev_m.get(k)
                    if isinstance(v, (int, float)):
                        sev_agg[k] = int(v)
    except Exception:
        pass
    try:
        if isinstance(summary, dict):
            for k2, key in (('critical', 'critical'), ('major', 'major'), ('minor', 'minor')):
                v2 = summary.get(key)
                if isinstance(v2, (int, float)):
                    sev_agg[k2] = int(v2)  # summary priorisiert
    except Exception:
        pass
    parts = []
    if isinstance(sev_agg.get('critical'), int):
        parts.append(f"kritisch:{sev_agg['critical']}")
    if isinstance(sev_agg.get('major'), int):
        parts.append(f"major:{sev_agg['major']}")
    if isinstance(sev_agg.get('minor'), int):
        parts.append(f"minor:{sev_agg['minor']}")
    severity_summary = " | ".join(parts) if parts else "-"

    return {
        'quality_score': quality_score,
        'quality_numeric': quality_numeric,
        'issues_count': str(issues_count),
        'files_processed': files_processed,
        'duration': duration,
        'severity': severity_summary
    }


def _ensure_event_listener(app):
    """analysis.done Listener – akzeptiert sowohl wrapped als auch top-level Payload."""
    try:
        if getattr(app, '_analysis_dashboard_listener_bound', False):
            return
        bus = getattr(app, 'event_bus', None)
        if not bus or not hasattr(bus, 'subscribe'):
            return

        # Registrierung und spätere Abmeldung unterstützen
        subs = getattr(app, '_analysis_dashboard_subscriptions', None)
        if subs is None:
            subs = []
            setattr(app, '_analysis_dashboard_subscriptions', subs)

        def _on_analysis_done(event):
            try:
                data = event if isinstance(event, dict) else {}
                results = data.get('results') if isinstance(data.get('results'), dict) else None
                if results:
                    app.analysis_results = results
                elif any(k in data for k in ('file_pairs', 'metrics', 'summary', 'plugins', 'findings')):
                    app.analysis_results = data
                if getattr(app, 'analysis_results', None):
                    try:
                        app.current_analysis = app.analysis_results
                    except Exception:
                        pass
                    run_on_ui_thread(app, lambda: build_analysis_dashboard(app))
            except Exception:
                pass
        try:
            sid = bus.subscribe('analysis.done', _on_analysis_done)
        except Exception:
            sid = None
            try:
                bus.subscribe('analysis.done', _on_analysis_done)
            except Exception:
                pass

        subs.append(('analysis.done', sid))
        _try_bind_unsubscribe_on_close(app)
        app._analysis_dashboard_listener_bound = True
    except Exception:
        pass


def _ensure_progress_listener(app):
    """Registriert einmalig Listener für analysis.progress für Echtzeit-Metrik-Updates."""
    try:
        if getattr(app, '_analysis_dashboard_progress_listener_bound', False):
            return
        bus = getattr(app, 'event_bus', None)
        if not bus or not hasattr(bus, 'subscribe'):
            return

        # Registrierung und spätere Abmeldung unterstützen
        subs = getattr(app, '_analysis_dashboard_subscriptions', None)
        if subs is None:
            subs = []
            setattr(app, '_analysis_dashboard_subscriptions', subs)

        def _update_cards(payload: dict):
            try:
                cards = getattr(app, '_analysis_metric_cards', {}) or {}
                if not cards:
                    return  # Noch keine Dashboard-Karten vorhanden

                # Start/Ende-Timestamps merken
                phase = payload.get('phase')
                if phase == 'start':
                    setattr(app, '_analysis_start_time', time.perf_counter())
                    setattr(app, '_analysis_end_time', None)
                if phase in ('done', 'completed', 'finalize'):
                    setattr(app, '_analysis_end_time', time.perf_counter())

                def _apply():  # UI Thread
                    try:
                        # Quality Score (0..1 -> %)
                        if 'quality_score' in payload and 'quality' in cards:
                            qs = payload.get('quality_score')
                            if isinstance(qs, (int, float)):
                                pct = ensure_percent_number(qs)
                                _safe_update_metric(cards['quality'], 'quality', value_new=_fmt_percent(pct), progress_value=pct)

                        # Issues (Aliase: issues | issues_count | findings | findings_count)
                        if 'issues' in cards:
                            issues_val = None
                            for k in ('issues', 'issues_count', 'findings', 'findings_count'):
                                if k in payload and isinstance(payload.get(k), (int, float)):
                                    issues_val = int(payload.get(k))
                                    break
                            if isinstance(issues_val, int):
                                _safe_update_metric(cards['issues'], 'issues', value_new=str(issues_val))

                        # Severity Mix (critical / major / minor)
                        if ('critical' in payload or 'major' in payload or 'minor' in payload) and 'severity' in cards:
                            c = payload.get('critical')
                            m = payload.get('major')
                            mi = payload.get('minor')
                            parts = []
                            if isinstance(c, (int, float)):
                                parts.append(f"kritisch:{int(c)}")
                            if isinstance(m, (int, float)):
                                parts.append(f"major:{int(m)}")
                            if isinstance(mi, (int, float)):
                                parts.append(f"minor:{int(mi)}")
                            if parts:
                                _safe_update_metric(cards['severity'], 'severity', value_new=" | ".join(parts))

                        # Duration (laufend) + Phase Beschreibung + Telemetrie (timeouts, aborted, executed, total_ms)
                        start_ts = getattr(app, '_analysis_start_time', None)
                        end_ts = getattr(app, '_analysis_end_time', None)
                        if start_ts and 'duration' in cards:
                            elapsed_src = (end_ts - start_ts) if (isinstance(end_ts, float) and end_ts >= start_ts) else (time.perf_counter() - start_ts)
                            elapsed = elapsed_src
                            phase_txt = payload.get('phase')
                            desc = None
                            if isinstance(phase_txt, str):
                                # Übersetzbarer Phasen-Text
                                try:
                                    phase_de = PHASE_MAP.get(phase_txt, phase_txt)
                                    desc = f"{app._t(TEXT['phase_prefix'])}: {app._t(phase_de)}"
                                    # Header-Phase aktualisieren
                                    try:
                                        ph = getattr(app, '_analysis_phase_label', None)
                                        if ph:
                                            if phase_txt in ('done', 'completed', 'finalize'):
                                                ph.configure(text=f"{app._t(TEXT['phase_prefix'])}: {app._t('Abgeschlossen')}")
                                            else:
                                                ph.configure(text=f"{app._t(TEXT['phase_prefix'])}: {app._t(phase_de)}")
                                    except Exception:
                                        pass
                                except Exception:
                                    desc = f"{TEXT['phase_prefix']}: {phase_txt}"
                            # Telemetrie ergänzen, falls vorhanden (mit Alias-Unterstützung)
                            try:
                                tmo = payload.get('timeouts')
                                if tmo is None:
                                    tmo = payload.get('timeouts_count')
                                abr = payload.get('aborted')
                                exe = payload.get('executed')
                                if exe is None:
                                    exe = payload.get('executed_count')
                                total_ms = payload.get('total_ms')
                                if total_ms is None:
                                    total_ms = payload.get('duration_ms')
                                parts = []
                                if _should_show_telemetry(app) and isinstance(tmo, (int, float)):
                                    parts.append(f"{app._t(TEXT['timeouts_label'])}: {int(tmo)}")
                                if _should_show_telemetry(app) and isinstance(abr, (bool, int)):
                                    parts.append(f"{app._t(TEXT['aborted_label'])}: {_to_yes_no(app, abr)}")
                                if _should_show_telemetry(app) and isinstance(exe, (int, float)):
                                    parts.append(f"{app._t(TEXT['executed_label'])}: {int(exe)}")
                                if _should_show_telemetry(app) and isinstance(total_ms, (int, float)) and total_ms >= 0:
                                    # Nur als Zusatzinfo – Hauptwert bleibt die live gemessene elapsed
                                    parts.append(f"{app._t(TEXT['total_time_label'])}: {_fmt_duration(total_ms/1000.0)}")
                                if parts:
                                    desc = (desc + " | " if desc else "") + " ".join(parts)
                            except Exception:
                                pass
                            _safe_update_metric(cards['duration'], 'duration', value_new=_fmt_duration(elapsed), desc_new=desc)

                        # Files (optional: bleibt statisch – könnte bei Bedarf dynamisch ergänzt werden)
                        if 'files' in cards and not getattr(cards['files'], '_locked', False):
                            try:
                                total_files = get_total_files(app)
                                _safe_update_metric(cards['files'], 'files', value_new=str(total_files))
                            except Exception:
                                pass
                    except Exception:
                        pass
                # Debounced UI-Update
                debounce_ui(app, 'analysis_progress', lambda: run_on_ui_thread(app, _apply), ms=80)
            except Exception:
                pass

        def _on_progress(event):
            payload = event if isinstance(event, dict) else {}
            _update_cards(payload)
        try:
            sid = bus.subscribe('analysis.progress', _on_progress)
        except Exception:
            sid = None
            try:
                bus.subscribe('analysis.progress', _on_progress)
            except Exception:
                pass
        subs.append(('analysis.progress', sid))
        # Dev/Test-Hooks: direkte Progress-Emission in Dev-Mode
        try:
            setattr(app, '_analysis_progress_updater', _update_cards)
            def _emit_fake_progress(payload: dict):
                if getattr(app, '_dev_mode', False):
                    _update_cards(payload or {})
            setattr(app, '_emit_fake_progress', _emit_fake_progress)
        except Exception:
            pass
        _try_bind_unsubscribe_on_close(app)
        app._analysis_dashboard_progress_listener_bound = True
    except Exception:
        pass


def _try_bind_unsubscribe_on_close(app):
    """Bindet eine Unsubscribe-Routine an app.on_close(), sofern möglich und noch nicht gebunden."""
    try:
        if getattr(app, '_analysis_dashboard_unsubscribe_bound', False):
            return
        bus = getattr(app, 'event_bus', None)
        subs = getattr(app, '_analysis_dashboard_subscriptions', None) or []
        if not bus or not subs:
            return

        def _unregister():
            try:
                for name, sid in list(subs):
                    try:
                        if hasattr(bus, 'unsubscribe'):
                            try:
                                bus.unsubscribe(name, sid)
                            except TypeError:
                                # Fallback: evtl. nur ID
                                bus.unsubscribe(sid)
                    except Exception:
                        pass
                subs.clear()
            except Exception:
                pass

        setattr(app, 'unregister_analysis_dashboard_listeners', _unregister)

        # Bestehendes on_close patchen (sanft)
        orig_on_close = getattr(app, 'on_close', None)
        if callable(orig_on_close) and not getattr(app, '_analysis_dashboard_close_patched', False):
            def _wrapped_on_close(*args, **kwargs):
                try:
                    res = orig_on_close(*args, **kwargs)
                finally:
                    try:
                        _unregister()
                    except Exception:
                        pass
                return res

            setattr(app, 'on_close', _wrapped_on_close)
            setattr(app, '_analysis_dashboard_close_patched', True)

        # Zusätzlich WM_DELETE_WINDOW des Root-Fensters patchen
        root = getattr(app, 'root', None)
        if root and hasattr(root, 'protocol') and not getattr(app, '_analysis_dashboard_wm_delete_patched', False):
            try:
                def _wm_close_handler():
                    try:
                        _unregister()
                    finally:
                        try:
                            if callable(orig_on_close):
                                orig_on_close()
                            elif hasattr(root, 'destroy'):
                                root.destroy()
                        except Exception:
                            try:
                                if hasattr(root, 'destroy'):
                                    root.destroy()
                            except Exception:
                                pass
                root.protocol('WM_DELETE_WINDOW', _wm_close_handler)
                setattr(app, '_analysis_dashboard_wm_delete_patched', True)
            except Exception:
                pass

        setattr(app, '_analysis_dashboard_unsubscribe_bound', True)
    except Exception:
        pass


def _fallback_metric_card(app, parent, title: str, value: str, color: str, description: str, column: int):
    """Fallback Karte ohne erweitertes Metric-Widget (saubere Farbverwendung)."""
    try:
        frame = ctk.CTkFrame(
            parent,
            fg_color=_ds_get_color(app, 'surface', None),
            corner_radius=_get_ds_border_radius(app, 'radius_md', 8),
            border_width=1,
            border_color=_ds_get_color(app, 'surface_border', None)
        )
        frame.grid(row=0, column=column, sticky="nsew", padx=4, pady=4)
        frame.grid_propagate(False)
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(*_ds_get_font(app, 'body')),
            text_color=_ds_get_color(app, 'text_secondary', _ds_get_color(app, 'text_muted', None))
        ).pack(pady=(8, 2))
        try:
            # Leere Werte dezent darstellen
            if is_empty_metric(value):
                value_color = _ds_get_color(app, 'text_muted', _ds_get_color(app, 'gray_500', None))
            else:
                value_color = _ds_get_color(app, color, _ds_get_color(app, 'primary', None))
        except Exception:
            value_color = _ds_get_color(app, 'primary', None)
        ctk.CTkLabel(
            frame,
            text=value,
            font=ctk.CTkFont(*_ds_get_font(app, 'heading')),
            text_color=value_color
        ).pack(pady=(0, 4))
        lbl_desc = ctk.CTkLabel(
            frame,
            text=description,
            font=ctk.CTkFont(*_ds_get_font(app, 'caption')),
            text_color=_ds_get_color(app, 'text_muted', _ds_get_color(app, 'gray_500', None)),
            wraplength=160,
            justify='center'
        )
        lbl_desc.pack(padx=6, pady=(0, 8))
        def _sync_wrap(_=None):
            try:
                w = frame.winfo_width()
                if w > 0:
                    lbl_desc.configure(wraplength=max(140, int(w * 0.85)))
            except Exception:
                pass
        frame.bind('<Configure>', _sync_wrap)
    except Exception:
        pass


def create_or_fallback_metric_card(
    app,
    parent,
    title: str,
    value: str,
    color: str,
    description: str,
    position,  # Kann int (column) oder tuple (row, col) sein
    *,
    show_progress: bool = False,
    value_max: float = 100.0
):
    """Erstellt eine Metrik-Karte über App-Hook oder Fallback-Variante.
    Fängt inkompatible Signaturen (show_progress) ab und loggt eine Warnung.
    
    position kann sein:
    - int: Legacy column-only Position
    - tuple(row, col): Grid-Position für 2D-Layout
    """
    # Parse position
    if isinstance(position, tuple) and len(position) == 2:
        row, column = position
    else:
        row, column = 0, int(position) if isinstance(position, int) else 0
    
    # Prefer dedizierte Metric-Komponente falls verfügbar
    try:
        from quality_gui_components_metrics import build_metric_card as _build_metric_card  # type: ignore
    except Exception:
        _build_metric_card = None  # type: ignore

    card_obj = None
    if _build_metric_card and callable(_build_metric_card):
        try:
            # Versuche neue Signatur mit Grid-Position
            card_obj = _build_metric_card(app, parent, title, value, color, description, (row, column), show_progress=show_progress, value_max=value_max)
        except TypeError:
            # Fallback auf Legacy-Signatur mit column only
            try:
                card_obj = _build_metric_card(app, parent, title, value, color, description, column, show_progress=show_progress, value_max=value_max)
            except TypeError:
                # Ältere Variante ohne show_progress
                try:
                    card_obj = _build_metric_card(app, parent, title, value, color, description, column)
                    logger = getattr(app, 'logger', None)
                    if logger and hasattr(logger, 'warning'):
                        logger.warning("Metric-Card unterstützt 'show_progress' nicht – ohne Fortschrittsbalken erstellt.")
                except Exception:
                    card_obj = None
        except Exception:
            card_obj = None

    if card_obj is None:
        # App-Hook als zweite Option
        create_metric = getattr(app, '_create_metric_card', None)
        if callable(create_metric):
            try:
                card_obj = create_metric(parent, title, value, color, description, column, show_progress=show_progress, value_max=value_max)
            except TypeError:
                try:
                    card_obj = create_metric(parent, title, value, color, description, column)
                except Exception:
                    card_obj = None
            except Exception:
                card_obj = None

    if card_obj is None:
        _fallback_metric_card(app, parent, title, value, color, description, column)
        return None
    return card_obj


def build_analysis_dashboard(app):
    """Erstellt das Analyse-Dashboard (Design-System gereinigt & lokalisiert)."""
    _ensure_event_listener(app)
    _ensure_progress_listener(app)
    _ensure_misc_listeners(app)
    # Output Frame leeren (bestehende Logik beibehalten)
    for w in list(app.output_frame.winfo_children()):
        try:
            w.destroy()
        except Exception:
            pass

    # Spacing Tokens
    spacing_xl = _ds_get_spacing(app, 'xl', 32)
    spacing_lg = _ds_get_spacing(app, 'lg', 24)
    spacing_md = _ds_get_spacing(app, 'md', 16)

    dashboard_container = ctk.CTkFrame(app.output_frame, fg_color=_ds_get_color(app, 'transparent', None))
    dashboard_container.pack(fill="both", expand=True, padx=spacing_xl, pady=spacing_xl)
    try:
        dashboard_container.pack_propagate(False)
    except Exception:
        pass

    # 🎨 MODERNISIERTER HEADER mit Gradient-Effekt-Simulation
    header_card = ctk.CTkFrame(
        dashboard_container,
        fg_color=_ds_get_color(app, 'primary', None),
        corner_radius=_get_ds_border_radius(app, 'radius_xl', 12),
        border_width=2,
        border_color=_ds_get_color(app, 'primary_hover', _ds_get_color(app, 'primary', None))
    )
    header_card.pack(fill="x", pady=(0, spacing_lg))

    header_content = ctk.CTkFrame(header_card, fg_color=_ds_get_color(app, 'transparent', None))
    header_content.pack(fill="x", padx=spacing_xl, pady=spacing_lg + 4)  # Mehr vertikaler Raum
    try:
        header_content.grid_columnconfigure(0, weight=1)
        header_content.grid_columnconfigure(1, weight=0)
    except Exception:
        pass

    # Haupttitel mit verbesserter Hierarchie
    title_container = ctk.CTkFrame(header_content, fg_color=_ds_get_color(app, 'transparent', None))
    try:
        title_container.grid(row=0, column=0, sticky="w")
    except Exception:
        title_container.pack(side='left')
    
    dashboard_title = ctk.CTkLabel(
        title_container,
        text=app._t(TEXT['dashboard_title']),
        font=ctk.CTkFont(*_ds_get_font(app, 'title'), weight='bold'),
        text_color=_ds_get_color(app, 'white', None)
    )
    dashboard_title.pack(anchor="w")
    
    # Subtitel für mehr Kontext
    subtitle = ctk.CTkLabel(
        title_container,
        text=app._t("Live-Übersicht Ihrer Übersetzungsanalyse"),
        font=ctk.CTkFont(*_ds_get_font(app, 'body')),
        text_color=_ds_get_color(app, 'white', None)
    )
    subtitle.pack(anchor="w", pady=(4, 0))

    # Phase-Badge mit verbessertem Design
    phase_container = ctk.CTkFrame(
        header_content,
        fg_color=_ds_get_color(app, 'white', None),
        corner_radius=_get_ds_border_radius(app, 'radius_md', 8)
    )
    try:
        phase_container.grid(row=0, column=1, sticky="e", padx=(spacing_md, 0))
    except Exception:
        phase_container.pack(side='right', padx=(spacing_md, 0))
    
    phase_label = ctk.CTkLabel(
        phase_container,
        text=f"{app._t(TEXT['phase_prefix'])}: –",
        font=ctk.CTkFont(*_ds_get_font(app, 'body'), weight='bold'),
        text_color=_ds_get_color(app, 'primary', None)
    )
    phase_label.pack(padx=spacing_md, pady=spacing_md//2)
    try:
        app._analysis_phase_label = phase_label
    except Exception:
        pass

    # 🎨 VERBESSERTES METRIKEN-GRID mit besserer Anordnung
    metrics_grid = ctk.CTkFrame(dashboard_container, fg_color=_ds_get_color(app, 'transparent', None))
    metrics_grid.pack(fill="x", pady=(0, spacing_lg))
    
    # Responsive Grid: 3 Spalten für primäre Metriken in erster Reihe
    # 2 Spalten für sekundäre Metriken in zweiter Reihe
    for col in range(3):
        try:
            metrics_grid.grid_columnconfigure(col, weight=1, uniform="metrics")
        except Exception:
            pass
    try:
        metrics_grid.grid_rowconfigure(0, weight=1)
        metrics_grid.grid_rowconfigure(1, weight=1)
    except Exception:
        pass

    dyn = _extract_dynamic_metrics(app)
    # Header-Phase initial aus current_analysis ziehen (falls vorhanden)
    try:
        phase_label_text = None
        ca = getattr(app, 'current_analysis', None)
        if isinstance(ca, dict):
            summ = ca.get('summary') if isinstance(ca.get('summary'), dict) else {}
            phase = summ.get('phase')
            if isinstance(phase, str) and phase:
                mapped = PHASE_MAP.get(phase, phase)
                phase_label_text = f"{app._t(TEXT['phase_prefix'])}: {app._t(mapped)}"
            # abgeschlossen?
            if isinstance(summ.get('completed'), bool) and summ.get('completed'):
                phase_label_text = f"{app._t(TEXT['phase_prefix'])}: {app._t('Abgeschlossen')}"
        if phase_label_text:
            try:
                app._analysis_phase_label.configure(text=phase_label_text)
            except Exception:
                pass
    except Exception:
        pass
    # Quality Score Karte getrennt behandeln um ProgressBar sicher zu aktivieren (numerischer Wert erforderlich)
    # 🎨 NEUE ANORDNUNG: Reihe 1 (3 Spalten): Quality, Issues, Files
    #                    Reihe 2 (2 Spalten zentriert): Duration, Severity
    analysis_metrics = [
        # Reihe 1 - Primäre Metriken
        (app._t(TEXT['quality_score']), dyn['quality_score'], COLOR_TOKENS['success'], app._t(TEXT['overall_quality_rating']), 0, 0),
        (app._t(TEXT['issues_found']), dyn['issues_count'], COLOR_TOKENS['warning'], app._t(TEXT['issues_detected_desc']), 0, 1),
        (app._t(TEXT['files_processed']), dyn['files_processed'], COLOR_TOKENS['info'], app._t(TEXT['files_processed_desc']), 0, 2),
        # Reihe 2 - Sekundäre Metriken
        (app._t(TEXT['analysis_time']), dyn['duration'], COLOR_TOKENS['primary'], app._t(TEXT['processing_time_desc']), 1, 0),
        (app._t(TEXT['severity_mix']), dyn['severity'], COLOR_TOKENS['error'], app._t(TEXT['severity_distribution_desc']), 1, 1)
    ]
    metric_cards: Dict[str, Any] = {}
    metric_keys = ['quality', 'issues', 'files', 'duration', 'severity']

    for i, (title, value, color, description, row, col) in enumerate(analysis_metrics):
        # Sonderfall erste Karte (Quality Score): ProgressBar aktivieren
        show_progress = (i == 0)
        initial_val = dyn.get('quality_numeric') if show_progress else None
        display_value = (f"{int(initial_val):d}%" if isinstance(initial_val, (int, float)) else (value or '-'))
        if is_empty_metric(display_value):
            display_value = "--"
        card_obj = create_or_fallback_metric_card(
            app,
            metrics_grid,
            title,
            display_value,
            color,
            description,
            (row, col),  # Übergebe Tuple für Grid-Position
            show_progress=show_progress,
            value_max=100.0
        )

        if card_obj is not None and hasattr(card_obj, 'update_metric'):
            metric_cards[metric_keys[i]] = card_obj

    # Telemetrie sofort einblenden, falls in current_analysis vorhanden (inkl. Aliase)
    try:
        stats = None
        if isinstance(getattr(app, 'current_analysis', None), dict):
            stats = app.current_analysis.get('stats')
        if isinstance(stats, dict):
            timeouts = stats.get('timeouts') if stats.get('timeouts') is not None else stats.get('timeouts_count')
            aborted = stats.get('aborted')
            executed = stats.get('executed') if stats.get('executed') is not None else stats.get('executed_count')
            total_ms = stats.get('total_ms') if stats.get('total_ms') is not None else stats.get('duration_ms')
            if 'duration' in metric_cards and any(v is not None for v in (timeouts, aborted, executed, total_ms)) and _should_show_telemetry(app):
                desc_parts = []
                if isinstance(timeouts, (int, float)):
                    desc_parts.append(f"{app._t(TEXT['timeouts_label'])}: {int(timeouts)}")
                if isinstance(aborted, (bool, int)):
                    desc_parts.append(f"{app._t(TEXT['aborted_label'])}: {_to_yes_no(app, aborted)}")
                if isinstance(executed, (int, float)):
                    desc_parts.append(f"{app._t(TEXT['executed_label'])}: {int(executed)}")
                if isinstance(total_ms, (int, float)) and total_ms >= 0:
                    desc_parts.append(f"{app._t(TEXT['total_time_label'])}: {_fmt_duration(total_ms/1000.0)}")
                if desc_parts:
                    _safe_update_metric(metric_cards['duration'], 'duration', desc_new=" ".join(desc_parts))
    except Exception:
        pass

    # Referenz auf App legen für progress Listener
    # Dashboard Objekt bereitstellen (erweiterbar)
    dashboard_obj = {
        'cards': metric_cards,
        'container': dashboard_container,
        'metrics_grid': metrics_grid
    }
    try:
        app._analysis_metric_cards = metric_cards  # Backwards compatibility
        app.analysis_dashboard = dashboard_obj
    except Exception:
        pass

    results_section = ctk.CTkFrame(
        dashboard_container,
        fg_color=_ds_get_color(app, 'surface', None),
        corner_radius=_get_ds_border_radius(app, 'radius_xl', 12),
        border_width=0,
    )
    results_section.pack(fill="both", expand=True)

    results_header = ctk.CTkLabel(
        results_section,
        text=app._t("Detailed Analysis Results"),
        font=ctk.CTkFont(*_ds_get_font(app, 'heading')),
        text_color=_ds_get_color(app, COLOR_TOKENS['info'], None)
    )
    results_header.pack(pady=(spacing_lg, spacing_md))
    try:
        add_accessibility(app, results_header, role='heading', name='Analyseergebnisse')
    except Exception:
        pass

    if not getattr(app, 'current_analysis', None):
        if hasattr(app, '_show_analysis_placeholder'):
            try:
                app._show_analysis_placeholder(results_section)
            except TypeError:  # ältere Variante ohne parent
                try:
                    app._show_analysis_placeholder()
                except Exception:
                    pass
        else:
            # Hinweis + CTA (optional)
            info_container = ctk.CTkFrame(results_section, fg_color=_ds_get_color(app, 'transparent', None))
            info_container.pack(pady=(spacing_md, spacing_md))
            ctk.CTkLabel(
                info_container,
                text=app._t(TEXT['no_analysis_yet']),
                font=ctk.CTkFont(*_ds_get_font(app, 'body')),
                text_color=_ds_get_color(app, 'text_secondary', _ds_get_color(app, 'text_muted', None))
            ).pack(pady=(0, spacing_md))
            if hasattr(app, 'trigger_analysis') and callable(getattr(app, 'trigger_analysis')):
                try:
                    btn = ctk.CTkButton(
                        info_container,
                        text=app._t(TEXT['cta_analyze_now']),
                        fg_color=_ds_get_color(app, 'primary', None),
                        hover_color=_ds_get_color(app, 'primary_hover', _ds_get_color(app, 'primary', None)),
                        text_color=_ds_get_color(app, 'white', None),
                        command=lambda: run_on_ui_thread(app, app.trigger_analysis)
                    )
                    btn.pack()
                    try:
                        add_accessibility(app, btn, role='button', name=app._t(TEXT['cta_analyze_now']))
                    except Exception:
                        pass
                except Exception:
                    pass
    else:
        try:
            app._show_analysis_results()
        except TypeError:
            # Falls neue Signatur doch parent benötigt – fallback stumm
            try:
                app._show_analysis_results(results_section)
            except Exception:
                pass


def _ensure_misc_listeners(app):
    """Zusätzliche Listener: analysis.start (Reset) und theme.changed (Rebuild)."""
    try:
        if getattr(app, '_analysis_dashboard_misc_listener_bound', False):
            return
        bus = getattr(app, 'event_bus', None)
        if not bus or not hasattr(bus, 'subscribe'):
            return

        subs = getattr(app, '_analysis_dashboard_subscriptions', None)
        if subs is None:
            subs = []
            setattr(app, '_analysis_dashboard_subscriptions', subs)

        # analysis.start → Reset Karten & Timer
        def _on_start(event):
            try:
                setattr(app, '_analysis_start_time', time.perf_counter())
                cards = getattr(app, '_analysis_metric_cards', {}) or {}
                if cards:
                    def _reset():
                        try:
                            if 'quality' in cards:
                                _safe_update_metric(cards['quality'], 'quality', value_new="--", progress_value=0.0, force=True)
                            if 'issues' in cards:
                                _safe_update_metric(cards['issues'], 'issues', value_new="--", force=True)
                            if 'severity' in cards:
                                _safe_update_metric(cards['severity'], 'severity', value_new="--", force=True)
                            if 'duration' in cards:
                                _safe_update_metric(cards['duration'], 'duration', value_new="--", desc_new=None, force=True)
                            if 'files' in cards:
                                try:
                                    _safe_update_metric(cards['files'], 'files', value_new=str(get_total_files(app)), force=True)
                                except Exception:
                                    _safe_update_metric(cards['files'], 'files', value_new="--", force=True)
                            # Phase Label zurücksetzen
                            try:
                                ph = getattr(app, '_analysis_phase_label', None)
                                if ph:
                                    ph.configure(text=f"{app._t(TEXT['phase_prefix'])}: –")
                            except Exception:
                                pass
                        except Exception:
                            pass
                    run_on_ui_thread(app, _reset)
            except Exception:
                pass
        try:
            sid1 = bus.subscribe('analysis.start', _on_start)
        except Exception:
            sid1 = None
            try:
                bus.subscribe('analysis.start', _on_start)
            except Exception:
                pass
        subs.append(('analysis.start', sid1))

        # theme.changed → DS-Cache leeren und Dashboard neu bauen
        def _on_theme_changed(event):
            try:
                invalidate_ds_caches(app)
                run_on_ui_thread(app, lambda: build_analysis_dashboard(app))
            except Exception:
                pass
        try:
            sid2 = bus.subscribe('theme.changed', _on_theme_changed)
        except Exception:
            sid2 = None
            try:
                bus.subscribe('theme.changed', _on_theme_changed)
            except Exception:
                pass
        subs.append(('theme.changed', sid2))

        _try_bind_unsubscribe_on_close(app)
        app._analysis_dashboard_misc_listener_bound = True
    except Exception:
        pass
