"""quality_gui_reporting

Berichtserstellung / Export-Schicht (Additiv, noch Platzhalter)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable, TYPE_CHECKING
import json
import time
import csv
from pathlib import Path

@dataclass(slots=True)
class ReportMeta:
    created_ts: float
    duration_ms: int
    aborted: bool
    rule_count: int

class QualityGuiReporting:
    def build_summary(self, analysis_results: list[dict], stats: dict) -> dict:
        return {
            'meta': ReportMeta(
                created_ts=time.time(),
                duration_ms=stats.get('total_ms', 0),
                aborted=stats.get('aborted', False),
                rule_count=len(analysis_results),
            ).__dict__,
            'findings_total': sum(len(r.get('findings', [])) for r in analysis_results),
        }

    def export_json(self, summary: dict, path: str) -> bool:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    # -----------------------------------------------------------
    # DELEGIERTER MULTI-FORMAT EXPORT (Wrapper um quality_gui_export)
    # -----------------------------------------------------------
    def perform_export(self, app, fmt: Optional[str] = None):  # fmt ist optional – Default nutzt Settings
        """Extrahiert die Logik aus main_app._perform_export (thin wrapper).

        Beibehaltung der bisherigen Seiteneffekte: Status-Updates, Toasts, EventBus.
        """
        try:
            from quality_gui_export import export_multi, ExportResult  # type: ignore
        except Exception as e:  # pragma: no cover
            try:
                app._handle_error(e, context='export.module.missing', user_message=app._t('Export Modul nicht verfügbar'))
            except Exception:
                pass
            app.show_toast(app._t('Export-Modul nicht verfügbar'), 'error')
            return
        import uuid, time as _tmod, os, sys
        export_id = str(uuid.uuid4())
        export_start = _tmod.time()
        # Settings lesen (robust)
        _get_setting = _settings_getter(app)
        naming_pattern = _get_setting('reporting.naming_pattern', 'report_{ts}')
        auto_open = bool(_get_setting('reporting.auto_open', False))
        include_charts = bool(_get_setting('reporting.include_charts', True))
        out_dir = _get_setting('reporting.output_dir', 'exports')
        prefix = _get_setting('reporting.filename_prefix', 'analysis')
        export_formats = _collect_export_formats(fmt, _get_setting)
        base_dir = Path(out_dir or 'exports'); base_dir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime('%Y%m%d_%H%M%S')
        base_name = (naming_pattern or 'report_{ts}').format(ts=ts, fmt='multi').strip()
        if prefix and not base_name.startswith(prefix):
            base_name = f"{prefix}_{base_name}"
        target_base = base_dir / base_name
        report_data = _normalize_report_data(app)
        _on_event = _make_event_handler(app, export_id)
        try:
            results: list[ExportResultType] = export_multi(
                report_data,
                target_base,
                export_formats,
                include_charts=include_charts,
                event_cb=_on_event
            )
            # Zusätzliche gruppierte Exporte (HTML + CSV)
            _export_grouped(app, report_data, target_base, results)
            # Optional: Korrekturpaket zusätzlich erzeugen
            try:
                create_pkg = bool(_get_setting('reporting.create_correction_package', False))
            except Exception:
                create_pkg = False
            if create_pkg:
                _export_correction_package(app, report_data, target_base, auto_open, results)
        except Exception as e:
            try:
                app._handle_error(e, context='export.failed', user_message=app._t('Export fehlgeschlagen'))
            except Exception:
                pass
            app.show_toast(app._t('Export fehlgeschlagen'), 'error')
            return
        if not results:
            app.show_toast(app._t('Keine Dateien erzeugt'), 'warning')
            return
        # persist last export path
        try:
            if app.settings_service and results:
                app.settings_service.set('reporting.last_export_path', str(results[0].path))
        except Exception:
            pass
        success_results = [r for r in results if getattr(r, 'success', False)]
        failed_results = [r for r in results if not getattr(r, 'success', False)]
        created_names = ", ".join(r.path.name for r in success_results)
        if success_results and failed_results:
            app.show_toast(app._t('Export teilweise erfolgreich') + f": {created_names}", 'warning')
        elif success_results:
            app.show_toast(app._t('Export erstellt') + f": {created_names}", 'success')
        else:
            app.show_toast(app._t('Export fehlgeschlagen'), 'error')
        app.update_status(app._t('Export abgeschlossen') + f" ({len(results)} Dateien)")
        open_errors = 0
        if auto_open:
            open_errors = _open_after_export(results)
            if open_errors:
                app.show_toast(app._t('Einige Dateien konnten nicht automatisch geöffnet werden'), 'warning')
        # Detail Logging
        _log_results(app, export_id, results)


__all__ = [
    'QualityGuiReporting',
    'ReportMeta'
]

# ---------------------
# Internals / Helpers (module-level)
# ---------------------
@runtime_checkable
class SettingsServiceLike(Protocol):
    def get(self, key: str, default: Any | None = None) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...


@runtime_checkable
class AppLike(Protocol):
    settings_service: SettingsServiceLike
    def update_status(self, text: str) -> None: ...
    def _t(self, text: str) -> str: ...
    def _log_event(self, event_name: str, **edata: Any) -> None: ...


# Typalias für ExportResult (falls Export-Modul zur Typprüfzeit verfügbar)
if TYPE_CHECKING:
    from quality_gui_export import ExportResult as ExportResultType  # type: ignore
else:
    ExportResultType = Any  # type: ignore


def _settings_getter(app: "AppLike"):
    def _s(key, default=None):
        try:
            return app.settings_service.get(key, default)
        except Exception:
            return default
    return _s

def _collect_export_formats(fmt: Optional[str], _s) -> list[str]:
    if fmt:
        export_formats = [fmt]
    else:
        configured = _s('reporting.formats', []) or []
        export_formats = [f for f in configured if f in ('pdf', 'xlsx', 'txt')]
    if not export_formats:
        export_formats = ['txt']
    return export_formats

def _normalize_report_data(app: "AppLike") -> dict | list | Any:
    try:
        return app.analysis_results if getattr(app, 'analysis_results', None) else {'info': 'no_analysis_data'}
    except Exception:
        return {'info': 'no_analysis_data'}

def _make_event_handler(app: "AppLike", export_id: str):
    def _on_event(event_name: str, **edata):
        try:
            if event_name == 'export.started':
                app.update_status(app._t('Export gestartet'))
            elif event_name == 'export.done':
                app.update_status(app._t('Export abgeschlossen'))
            if getattr(app, '_log_event', None):
                if 'path' in edata:
                    try:
                        edata['path'] = repr(edata['path'])
                    except Exception:
                        pass
                app._log_event(event_name, export_id=export_id, **edata)
        except Exception:
            pass
    return _on_event

def _make_result(fmt: str, path: str):
    class _ER:
        def __init__(self, p: str):
            self.format = fmt
            self.path = Path(p)
            self.success = True
            self.error = None
    return _ER(path)

def _export_grouped(app: "AppLike", report_data: Any, target_base: Path, results: list[ExportResultType]) -> None:
    try:
        if isinstance(report_data, dict) and isinstance(report_data.get('findings_grouped'), list) and report_data.get('findings_grouped'):
            from src.export.format_manager import FormatExportManager  # type: ignore
            fem = FormatExportManager(app_instance=app)
            grouped_list = report_data.get('findings_grouped') or []
            grouped_payload = {'findings': grouped_list}
            try:
                if isinstance(report_data.get('metrics'), dict):
                    grouped_payload['metrics'] = report_data.get('metrics')
            except Exception:
                pass
            grouped_html_path = str(target_base) + "_grouped.html"
            ok, _ = fem.export_data(grouped_payload, 'html', grouped_html_path)
            if ok:
                results.append(_make_result('html', grouped_html_path))
            try:
                grows = []
                for f in grouped_list:
                    if not isinstance(f, dict):
                        continue
                    conf = f.get('confidence')
                    if conf is None:
                        conf = f.get('avg_confidence', f.get('avg_conf'))
                    try:
                        if isinstance(conf, str):
                            conf = float(conf)
                    except Exception:
                        pass
                    grows.append({
                        'severity': f.get('severity'),
                        'rule_id': (f.get('rule_id') or f.get('rule')),
                        'message': f.get('message'),
                        'count': f.get('count') or 1,
                        'confidence': conf if isinstance(conf, (int, float)) else ''
                    })
                if grows:
                    grouped_csv_path = str(target_base) + "_grouped.csv"
                    ok_csv, _ = fem.export_data(grows, 'csv', grouped_csv_path)
                    if ok_csv:
                        results.append(_make_result('csv', grouped_csv_path))
            except Exception:
                pass
    except Exception:
        pass

def _export_correction_package(app: "AppLike", report_data: Any, target_base: Path, auto_open: bool, results: list[ExportResultType]) -> None:
    try:
        import os, json as _json, datetime as _dt
        pkg_dir = str(target_base) + "_korrekturpaket"
        os.makedirs(pkg_dir, exist_ok=True)
        ungrouped_findings = []
        try:
            if isinstance(report_data, dict) and isinstance(report_data.get('findings'), list):
                ungrouped_findings = [f for f in report_data.get('findings') if isinstance(f, dict)]
        except Exception:
            ungrouped_findings = []
        def _write_txt():
            with open(os.path.join(pkg_dir, 'findings.txt'), 'w', encoding='utf-8') as fh:
                try:
                    thr = None
                    if isinstance(report_data.get('metrics'), dict):
                        thr = report_data['metrics'].get('similarity_thresholds_used')
                    if isinstance(thr, dict):
                        def _fmt(v):
                            try:
                                return f"{float(v):.0%}" if v is not None else '–'
                            except Exception:
                                return '–'
                        c_txt = _fmt(thr.get('critical'))
                        m_txt = _fmt(thr.get('major'))
                        fh.write(f"Ähnlichkeitsschwellen: Kritisch ≥ {c_txt}, Wesentlich ≥ {m_txt}\n\n")
                except Exception:
                    pass
                for f in ungrouped_findings:
                    try:
                        fh.write(f"[{f.get('severity')}] {(f.get('rule_id') or f.get('rule') or 'rule')}: {(f.get('message') or '')}\n")
                    except Exception:
                        continue
        _safe_write(os.path.join(pkg_dir, 'findings.txt'), _write_txt)
        def _write_json():
            with open(os.path.join(pkg_dir, 'findings.json'), 'w', encoding='utf-8') as jf:
                _json.dump(ungrouped_findings, jf, ensure_ascii=False, indent=2)
        _safe_write(os.path.join(pkg_dir, 'findings.json'), _write_json)
        def _write_csv():
            with open(os.path.join(pkg_dir, 'findings.csv'), 'w', encoding='utf-8', newline='') as cf:
                w = csv.writer(cf, delimiter=';', quoting=csv.QUOTE_ALL)
                w.writerow(['severity', 'rule', 'checker', 'message', 'confidence'])
                for f in ungrouped_findings:
                    conf = f.get('confidence')
                    try:
                        if isinstance(conf, str):
                            conf = float(conf)
                    except Exception:
                        pass
                    w.writerow([
                        f.get('severity'),
                        (f.get('rule_id') or f.get('rule')),
                        f.get('checker'),
                        (f.get('message') or '').replace('\n', ' '),
                        conf if isinstance(conf, (int, float)) else ''
                    ])
        _safe_write(os.path.join(pkg_dir, 'findings.csv'), _write_csv)
        def _has_bilingual(items):
            for it in items:
                if isinstance(it, dict) and all(k in it for k in ('segment_id', 'source', 'target')):
                    return True
            return False
        if _has_bilingual(ungrouped_findings):
            def _write_bi():
                with open(os.path.join(pkg_dir, 'findings_bilingual.csv'), 'w', encoding='utf-8', newline='') as bcf:
                    bw = csv.writer(bcf, delimiter=';', quoting=csv.QUOTE_ALL)
                    bw.writerow(['segment_id', 'source', 'target', 'severity', 'rule', 'message', 'suggestion', 'confidence'])
                    for f in ungrouped_findings:
                        if not isinstance(f, dict) or not all(k in f for k in ('segment_id', 'source', 'target')):
                            continue
                        conf = f.get('confidence')
                        try:
                            if isinstance(conf, str):
                                conf = float(conf)
                        except Exception:
                            pass
                        bw.writerow([
                            f.get('segment_id'),
                            (f.get('source') or '').replace('\n', ' '),
                            (f.get('target') or '').replace('\n', ' '),
                            f.get('severity'),
                            (f.get('rule_id') or f.get('rule')),
                            (f.get('message') or '').replace('\n', ' '),
                            (f.get('suggestion') or f.get('suggest') or ''),
                            conf if isinstance(conf, (int, float)) else ''
                        ])
            _safe_write(os.path.join(pkg_dir, 'findings_bilingual.csv'), _write_bi)
        try:
            grouped_findings = report_data.get('findings_grouped') if isinstance(report_data, dict) else None
        except Exception:
            grouped_findings = None
        if isinstance(grouped_findings, list) and grouped_findings:
            def _write_grouped_csv():
                with open(os.path.join(pkg_dir, 'findings_grouped.csv'), 'w', encoding='utf-8', newline='') as gcf:
                    gw = csv.writer(gcf, delimiter=';', quoting=csv.QUOTE_ALL)
                    gw.writerow(['severity', 'rule_id', 'message', 'count', 'confidence'])
                    for f in grouped_findings:
                        try:
                            cnt = f.get('count') or 1
                            conf = f.get('confidence') if f.get('confidence') is not None else (f.get('avg_confidence') if isinstance(f.get('avg_confidence'), (int, float, str)) else f.get('avg_conf'))
                            if isinstance(conf, str):
                                conf = float(conf)
                        except Exception:
                            conf = f.get('confidence')
                        gw.writerow([
                            f.get('severity'),
                            (f.get('rule_id') or f.get('rule')),
                            (f.get('message') or '').replace('\n', ' '),
                            cnt,
                            conf if isinstance(conf, (int, float)) else ''
                        ])
            _safe_write(os.path.join(pkg_dir, 'findings_grouped.csv'), _write_grouped_csv)
            try:
                from src.export.format_manager import FormatExportManager  # type: ignore
                fem = FormatExportManager(app_instance=app)
                payload = {'findings': grouped_findings}
                try:
                    if isinstance(report_data.get('metrics'), dict):
                        payload['metrics'] = report_data.get('metrics')
                except Exception:
                    pass
                fem.export_data(payload, 'html', os.path.join(pkg_dir, 'findings_grouped.html'))
            except Exception:
                pass
        def _write_readme():
            with open(os.path.join(pkg_dir, 'README.txt'), 'w', encoding='utf-8') as rf:
                rf.write('Korrekturpaket\n')
                rf.write('================\n\n')
                try:
                    thr = None
                    if isinstance(report_data.get('metrics'), dict):
                        thr = report_data['metrics'].get('similarity_thresholds_used')
                    def _fmt(v):
                        try:
                            return f"{float(v):.0%}" if v is not None else '–'
                        except Exception:
                            return '–'
                    c_txt = _fmt(thr.get('critical')) if isinstance(thr, dict) else '–'
                    m_txt = _fmt(thr.get('major')) if isinstance(thr, dict) else '–'
                except Exception:
                    c_txt = m_txt = '–'
                rf.write(f"Ähnlichkeitsschwellen (genutzt): Kritisch ≥ {c_txt}, Wesentlich ≥ {m_txt}\n")
                rf.write('Dateien:\n')
                rf.write('- findings.txt (Kurzliste)\n')
                rf.write('- findings.json (Detail)\n')
                rf.write('- findings.csv (ungrouped)\n')
                rf.write('- findings_bilingual.csv (falls vorhanden)\n')
                rf.write('- findings_grouped.csv/html (aggregiert, falls vorhanden)\n')
                rf.write('\nHinweis: Bitte Kritische zuerst bearbeiten, danach Wesentliche. Wiederholte Muster sind in findings_grouped.* gebündelt.\n')
        _safe_write(os.path.join(pkg_dir, 'README.txt'), _write_readme)
        def _write_meta():
            meta = {
                'generated_at': _dt.datetime.now().isoformat(),
                'similarity_thresholds_used': (report_data.get('metrics') or {}).get('similarity_thresholds_used') if isinstance(report_data.get('metrics'), dict) else None,
            }
            with open(os.path.join(pkg_dir, 'meta.json'), 'w', encoding='utf-8') as mf:
                _json.dump(meta, mf, ensure_ascii=False, indent=2)
        try:
            import datetime as _dt  # late import scope
            _safe_write(os.path.join(pkg_dir, 'meta.json'), _write_meta)
        except Exception:
            pass
        try:
            if auto_open:
                _open_path(pkg_dir)
        except Exception:
            pass
        try:
            results.append(_make_result('dir', pkg_dir))
        except Exception:
            pass
    except Exception:
        pass

def _open_after_export(results: list[ExportResultType]) -> int:
    errors = 0
    for r in results:
        try:
            if getattr(r, 'success', False) and r.path.exists():
                if not _open_path(str(r.path)):
                    errors += 1
        except Exception:
            errors += 1
    return errors

def _log_results(app, export_id: str, results: list[Any]) -> None:
    if getattr(app, '_log_event', None):
        for r in results:
            try:
                app._log_event('export.file', export_id=export_id, format=getattr(r, 'format', None), path=repr(str(r.path)), success=getattr(r, 'success', False), error=(str(getattr(r, 'error', None)) if getattr(r, 'error', None) else None))
            except Exception:
                pass

def _safe_write(path: str, writer):
    try:
        writer()
        return True
    except Exception:
        return False


def _open_path(path: str | Path) -> bool:
    """Plattform-übergreifendes Öffnen eines Pfads (Datei/Ordner)."""
    try:
        import os, sys, subprocess
        p_str = str(path)
        if os.name == 'nt':
            os.startfile(p_str)  # type: ignore[attr-defined]
            return True
        opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
        subprocess.Popen([opener, p_str])
        return True
    except Exception:
        return False
