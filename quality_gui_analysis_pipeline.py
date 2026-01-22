"""quality_gui_analysis_pipeline

Modularer Analyse-Pipeline Layer (additiv, zerstört keine bestehende Logik).
Ziel:
- Orchestrator-Funktion(en) für Plugin-/Regel-Analyse
- Trennung von GUI und Analysefluss
- Testbare, kleine Einheiten

WICHTIG:
- Keine Dark-Mode Implementierung
- Keine Icons / Emojis (UI-Texte bleiben icon-frei)
- DesignSystem Zugriffe nur indirekt (App liefert get_color/get_typography)

Integration:
    from quality_gui_analysis_pipeline import QualityGuiAnalysisPipeline
    self.analysis_pipeline = QualityGuiAnalysisPipeline()
    results = self.analysis_pipeline.run(app=self, context={...})

Platzhalter – konkrete Logik wird schrittweise aus quality_gui_main_app extrahiert.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional
import time, copy, concurrent.futures, threading, inspect

# Copilot: Prüfe und straffe Imports. Entfernt: Any, Callable, List (nicht genutzt).
# Copilot: Behalte nur tatsächlich verwendete Module.

# --- ProcessPool: Top-level Entry (picklable) ---
def _invoke_proc_entry(rule_cls, base_ctx, copy_mode: str):
    """ProcessPool-Entry-Callable (muss picklable sein).

    Hinweis: cancel_event kann im Process nicht genutzt werden und wird ignoriert.
    Plugin-Interface: def analyze(context: dict, cancel_event: Optional[threading.Event]=None)
    Rückgabe: dict | list[dict] | RuleResult-ähnliches Objekt
    """
    import copy as _copy, inspect as _inspect
    inst = rule_cls()
    if copy_mode == 'deep':
        local_ctx = _copy.deepcopy(base_ctx)
    elif copy_mode == 'shallow':
        try:
            local_ctx = dict(base_ctx)
        except Exception:
            local_ctx = _copy.deepcopy(base_ctx)
    else:
        # Achtung: 'none' nur bei rein lesenden Plugins/Context verwenden
        local_ctx = base_ctx
    try:
        _ = _inspect.signature(inst.analyze)  # nur Probe; keine Übergabe von cancel_event
    except Exception:
        pass
    return inst.analyze(local_ctx)

@dataclass(slots=True)
class AnalysisRuleResult:
    rule_name: str
    duration_ms: int
    timed_out: bool = False
    error: Optional[str] = None
    findings: list[dict] = field(default_factory=list)

@dataclass(slots=True)
class AnalysisStats:
    executed: int = 0
    timeouts: int = 0
    aborted: bool = False
    threshold: float = 0.0
    total_ms: int = 0

class QualityGuiAnalysisPipeline:
    """Orchestrator für regelbasierte Analyse.

    Diese Klasse kapselt den Ablauf; konkrete Regel-Discovery & Thread-Pool
    verbleibt vorerst in der Haupt-App und wird via Callbacks injiziert.
    
    Plugin-Interface (Erwartung):
    def analyze(context: dict, cancel_event: Optional[threading.Event] = None) -> dict | list[dict] | RuleResultLike
    - Plugins sollen, wenn cancel_event übergeben wurde, periodisch darauf prüfen und früh beenden.
    - Kontext ist read-only zu behandeln. Bei Bedarf eigene Kopien erstellen.
    """
    def __init__(self):
        self._last_stats: Optional[AnalysisStats] = None

    # -----------------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------------
    def _log_timeout(self, app, rule_name: str, duration: float, threshold: float):
        """Sicheres Timeout-Logging (keine Exceptions nach außen)."""
        try:
            lvl = 'warning'
            if getattr(app,'settings_service', None):
                try:
                    lvl = str(app.settings_service.get('plugins.timeout_log_level','warning') or 'warning').lower()
                except Exception:
                    lvl = 'warning'
            log_fn = None
            if getattr(app, 'logger', None):
                log_fn = getattr(app.logger, lvl, None)
            msg = f"Plugin Timeout ({str(rule_name)}) nach {duration:.2f}s (Schwelle {threshold:.2f}s)"
            (log_fn or print)(msg)
        except Exception:  # final fallback
            try:
                print(f"[WARN][Timeout] {rule_name} {duration:.2f}/{threshold:.2f}s")
            except Exception:
                pass

    def _log_abort(self, app, ratio: float, abort_ratio: float):
        """Sicheres Abort-Logging."""
        try:
            lvl = 'warning'
            if getattr(app,'settings_service', None):
                try:
                    lvl = str(app.settings_service.get('plugins.timeout_log_level','warning') or 'warning').lower()
                except Exception:
                    lvl = 'warning'
            log_fn = None
            if getattr(app, 'logger', None):
                log_fn = getattr(app.logger, lvl, None)
            msg = f"Plugin Analyse früh abgebrochen (Timeout-Quote {ratio*100:.0f}% > {abort_ratio*100:.0f}%)"
            (log_fn or print)(msg)
        except Exception:
            try:
                print(f"[WARN][Abort] ratio={ratio:.2f} threshold={abort_ratio:.2f}")
            except Exception:
                pass

    def _log_plugin_error(self, app, rule_name: str):
        """Sicheres Error-Logging für Plugin-Ausnahmen."""
        try:
            if getattr(app,'logger',None):
                try:
                    app.logger.exception("Plugin Fehler (%s)", str(rule_name))
                    return
                except Exception:
                    pass
            # Fallback
            print(f"[ERROR][Plugin] {rule_name}")
        except Exception:
            pass

    def _normalize_findings(self, raw_val) -> list[dict]:
        """Normalisiert beliebige Rückgaben in eine Liste von Dicts.

        Regeln:
        - None -> []
        - dict -> [dict]
        - list -> jede Komponente konvertiert:
            * dict bleibt
            * Objekt mit Attributen rule/passed/details -> spezielles Dict
            * sonst -> {'value': repr(item)}
        - Einzel-Objekt mit rule/passed/details -> entsprechendes Dict
        - alles andere -> [{'value': repr(obj)}]
        Exceptions werden intern geschluckt.
        """
        out: list[dict] = []
        try:
            if raw_val is None:
                return out
            # Einzelobjekt mit RuleResult-ähnlichen Attributen
            try:
                if hasattr(raw_val, 'rule') and hasattr(raw_val, 'passed') and hasattr(raw_val, 'details'):
                    out.append({
                        'rule': getattr(raw_val, 'rule', ''),
                        'passed': bool(getattr(raw_val, 'passed', False)),
                        'details': getattr(raw_val, 'details', {})
                    })
                    return out
            except Exception:
                pass
            if isinstance(raw_val, dict):
                out.append(raw_val)
            elif isinstance(raw_val, list):
                for item in raw_val:
                    if isinstance(item, dict):
                        out.append(item)
                        continue
                    if hasattr(item, 'rule') and hasattr(item, 'details'):
                        try:
                            out.append({
                                'rule': getattr(item, 'rule', ''),
                                'passed': bool(getattr(item, 'passed', False)),
                                'details': getattr(item, 'details', {})
                            })
                            continue
                        except Exception:
                            pass
                    # Fallback generisch
                    try:
                        out.append({'value': repr(item)})
                    except Exception:
                        out.append({'value': '<unrepr>'})
            else:
                try:
                    out.append({'value': repr(raw_val)})
                except Exception:
                    out.append({'value': '<unrepr>'})
        except Exception:
            # Falls gesamte Normalisierung scheitert -> safe fallback
            out = []
        return out

    def run(self, app, context: dict) -> dict:
        """Führt eine Analyse aus (vereinheitlichte Rückgabe-Struktur).

        Args:
            app: Haupt-App Instanz (liefert Logger, Settings, EventBus)
            context: Analyse-Kontext (Dateien, Profil, etc.)
        Returns:
            dict mit keys: results (List[AnalysisRuleResult]), stats (AnalysisStats as dict)
        """
        start = time.perf_counter()
        results: list[AnalysisRuleResult] = []
        # Settings laden (robust)
        try:
            timeout_ms = int(app.settings_service.get('plugins.timeout_ms', 2000)) if getattr(app,'settings_service',None) else 2000
        except Exception:
            timeout_ms = 2000
        timeout_s = max(0.05, timeout_ms / 1000.0)
        try:
            abort_ratio = float(app.settings_service.get('plugins.abort_timeout_ratio', 0.4)) if getattr(app,'settings_service',None) else 0.4
            if abort_ratio <= 0 or abort_ratio >= 1:
                abort_ratio = 0.4
        except Exception:
            abort_ratio = 0.4
        # Konfigurierbare Mindestanzahl ausgeführter Regeln bevor Abort-Ratio greift
        try:
            abort_min_executed = int(app.settings_service.get('plugins.abort_min_executed', 5)) if getattr(app,'settings_service',None) else 5
            if abort_min_executed < 1:
                abort_min_executed = 5
        except Exception:
            abort_min_executed = 5
        # Kontext Copy Mode: deep | shallow | none
        try:
            context_copy_mode = (app.settings_service.get('plugins.context_copy_mode', 'deep') or 'deep').lower() if getattr(app,'settings_service',None) else 'deep'
            if context_copy_mode not in ('deep','shallow','none'):
                context_copy_mode = 'deep'
        except Exception:
            context_copy_mode = 'deep'
        # Process Pool Optional (hartes Killen möglich, nur wenn Plugins picklable)
        use_process_pool = False
        try:
            use_process_pool = bool(app.settings_service.get('plugins.use_process_pool', False)) if getattr(app,'settings_service',None) else False
        except Exception:
            use_process_pool = False
        stats = AnalysisStats(threshold=abort_ratio)
        loaded_rules = list(getattr(app, 'loaded_rules', []) or [])
        if not loaded_rules:
            self._last_stats = stats
            return {'results': [], 'stats': asdict(stats)}
        max_workers = min(len(loaded_rules), 6)
        overall_budget = max(timeout_s, 5.0)  # Gesamtbudget (harte Deadline)
        start_wall = time.perf_counter()
        deadline = start_wall + overall_budget
        # Neue kooperative Cancellation
        cancel_event = threading.Event()
        aborted = False
        # Hinweis: rule_entries entfernt (nicht genutzt). if needed for future telemetry, can be reintroduced.
        try:
            ExecutorCls = concurrent.futures.ProcessPoolExecutor if use_process_pool else concurrent.futures.ThreadPoolExecutor
            executor_kwargs = {'max_workers': max_workers}
            if not use_process_pool:
                executor_kwargs['thread_name_prefix'] = 'plugin'
            with ExecutorCls(**executor_kwargs) as ex:
                # Basis-Kontext: keine tiefe Kopie hier; pro Regel abhängig von context_copy_mode
                snap = context
                future_meta: Dict[concurrent.futures.Future, dict] = {}
                for rule_cls in loaded_rules:
                    if getattr(app, '_plugin_cancel_requested', False):
                        break
                    rname_raw = getattr(rule_cls, 'name', None)
                    rname = rname_raw or getattr(rule_cls, '__name__', 'rule')
                    if isinstance(rname, str) and rname.lower() in ('base','rule'):
                        rname = getattr(rule_cls,'__name__', rname)
                    submitted = time.perf_counter()
                    # Falls Regel analyze(cancel_event=...) akzeptiert -> kooperativ (robust via inspect.signature)
                    if use_process_pool:
                        fut = ex.submit(_invoke_proc_entry, rule_cls, snap, context_copy_mode)
                    else:
                        def _invoke(rc=rule_cls):
                            inst = rc()
                            if context_copy_mode == 'deep':
                                local_ctx = copy.deepcopy(snap)
                            elif context_copy_mode == 'shallow':
                                try:
                                    local_ctx = dict(snap)
                                except Exception:
                                    local_ctx = copy.deepcopy(snap)
                            else:
                                local_ctx = snap
                            kwargs = {}
                            try:
                                sig = inspect.signature(inst.analyze)
                                if 'cancel_event' in sig.parameters:
                                    kwargs['cancel_event'] = cancel_event
                            except (ValueError, TypeError):
                                pass
                            return inst.analyze(local_ctx, **kwargs)
                        fut = ex.submit(_invoke)
                    future_meta[fut] = {'name': rname, 'start': submitted}

                # Polling-Schleife bis alle erledigt oder Budget abgelaufen
                # Konfigurierbares Polling-Intervall (ms)
                try:
                    poll_ms = int(app.settings_service.get('plugins.poll_interval_ms', 50)) if getattr(app,'settings_service',None) else 50
                except Exception:
                    poll_ms = 50
                check_interval = max(0.005, poll_ms / 1000.0)
                while future_meta:
                    # Harte Gesamt-Deadline prüfen
                    if time.perf_counter() > deadline:
                        for fut, meta in list(future_meta.items()):
                            rname = meta['name']
                            try:
                                fut.cancel()
                            except Exception:
                                pass
                            stats.timeouts += 1
                            # duration für Logging hier als overall Budget
                            self._log_timeout(app, rname, timeout_s, timeout_s)
                            results.append(AnalysisRuleResult(rule_name=rname, duration_ms=int(timeout_s*1000), timed_out=True))
                            future_meta.pop(fut, None)
                            stats.executed += 1
                        aborted = True
                        cancel_event.set()
                        break
                    if getattr(app,'_plugin_cancel_requested', False):
                        cancel_event.set()
                    done_now = []
                    for fut, meta in list(future_meta.items()):
                        rname = meta['name']; started = meta['start']
                        duration = time.perf_counter() - started
                        if fut.done():
                            err_text=None
                            try:
                                val = fut.result()
                                findings = self._normalize_findings(val)
                                results.append(AnalysisRuleResult(rule_name=rname, duration_ms=int(duration*1000), findings=findings))
                            except Exception as e:
                                err_text = str(e)[:400]
                                self._log_plugin_error(app, rname)
                                results.append(AnalysisRuleResult(rule_name=rname, duration_ms=int(duration*1000), error=err_text))
                            stats.executed += 1
                            done_now.append(fut)
                        else:
                            # Timeout prüfen
                            if duration > timeout_s:
                                try:
                                    fut.cancel()
                                except Exception:
                                    pass
                                stats.timeouts += 1
                                self._log_timeout(app, rname, duration, timeout_s)
                                results.append(AnalysisRuleResult(rule_name=rname, duration_ms=int(duration*1000), timed_out=True))
                                stats.executed += 1
                                done_now.append(fut)
                        # Frühabbruch evaluieren
                        try:
                            if stats.executed >= abort_min_executed and not aborted:
                                ratio = stats.timeouts / max(1, stats.executed)
                                if ratio > abort_ratio:
                                    aborted = True
                                    cancel_event.set()
                                    setattr(app,'_plugin_cancel_requested', True)
                                    self._log_abort(app, ratio, abort_ratio)
                                    try:
                                        if getattr(app,'event_bus',None):
                                            app.event_bus.publish('plugins.analysis.aborted', {
                                                'reason':'timeout_ratio',
                                                'timeout_ratio': ratio,
                                                'executed': stats.executed,
                                                'timeouts': stats.timeouts,
                                                'threshold': abort_ratio
                                            })
                                    except Exception:
                                        pass
                                    try:
                                        app.update_status(app._t("Analyse früh abgebrochen") + f" (Timeouts {ratio*100:.0f}% > {abort_ratio*100:.0f}%)", status_type="warning")
                                    except Exception:
                                        pass
                                    # alle laufenden Futures abbrechen
                                    for f2 in future_meta:
                                        try: f2.cancel()
                                        except Exception: pass
                                    break
                        except Exception:
                            pass
                    for d in done_now:
                        future_meta.pop(d, None)
                    if aborted:
                        break
                    if future_meta:
                        time.sleep(check_interval)
        except Exception as outer_e:
            if hasattr(app,'_handle_error'):
                app._handle_error(outer_e, context='plugins.analysis', user_message=None, toast=False)
        finally:
            stats.aborted = aborted
            stats.total_ms = int((time.perf_counter() - start_wall) * 1000)
            self._last_stats = stats
            # Completed Event paritätisch zu alter Implementierung
            try:
                if getattr(app,'event_bus',None):
                    app.event_bus.publish('plugins.analysis.completed', {
                        'count': len(results),
                        'rules': [r.rule_name for r in results],
                        'timeouts': stats.timeouts,
                        'aborted': stats.aborted,
                        'stats': asdict(stats)
                    })
            except Exception:  # pragma: no cover
                pass
        # Vereinheitlichte Rückgabe (Dicts) + Kompatibilitätsfelder
        return {
            'results': [asdict(r) for r in results],  # bevorzugte Form
            'stats': asdict(stats),
            # DEPRECATED: Legacy Rückgabeobjekte - werden in zukünftiger Version entfernt
            'results_objects': results,
            'stats_obj': stats
        }

    def get_last_stats(self) -> Optional[AnalysisStats]:
        return self._last_stats

__all__ = [
    'QualityGuiAnalysisPipeline',
    'AnalysisRuleResult',
    'AnalysisStats'
]
