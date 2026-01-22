from __future__ import annotations
from typing import Any, List, Dict
import os
import json
import csv
import datetime
import shutil

from ds_utils import fmt_percent


def export_findings(app: Any, findings: List[Dict[str, Any]], findings_grouped: List[Dict[str, Any]] | None = None, filters: Dict[str, Any] | None = None) -> str | None:
    """Exportiert Findings in TXT/JSON/CSV (+optional grouped CSV/HTML via FormatExportManager). Returns report dir or None.
    """
    try:
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        base_dir = getattr(app, 'projects_base_path', '.') or '.'
        report_dir = os.path.join(base_dir, 'reports')
        os.makedirs(report_dir, exist_ok=True)

        # Headline: Ähnlichkeitsschwellen, falls vorhanden
        used_thr = None
        try:
            full = getattr(app, 'analysis_results', {}) or {}
            used_thr = ((full.get('metrics') or {})).get('similarity_thresholds_used')
        except Exception:
            used_thr = None
        c_txt = m_txt = '–'
        try:
            if isinstance(used_thr, dict):
                c = used_thr.get('critical'); m = used_thr.get('major')
                c_txt = fmt_percent(c) if isinstance(c, (int, float)) else '–'
                m_txt = fmt_percent(m) if isinstance(m, (int, float)) else '–'
        except Exception:
            pass

        txt_path = os.path.join(report_dir, f'analysis_findings_{ts}.txt')
        with open(txt_path, 'w', encoding='utf-8') as fh:
            fh.write(f"Ähnlichkeitsschwellen: Kritisch ≥ {c_txt}, Wesentlich ≥ {m_txt}\n\n")
            for f in findings:
                fh.write(f"[{f.get('severity')}] {(f.get('rule_id') or f.get('rule') or 'rule')}: {(f.get('message') or '')}\n")

        json_path = os.path.join(report_dir, f'analysis_findings_{ts}.json')
        with open(json_path, 'w', encoding='utf-8') as jf:
            json.dump(findings, jf, ensure_ascii=False, indent=2)

        csv_path = os.path.join(report_dir, f'analysis_findings_{ts}.csv')
        with open(csv_path, 'w', encoding='utf-8', newline='') as cf:
            w = csv.writer(cf, delimiter=';')
            w.writerow(['severity', 'rule', 'checker', 'message', 'confidence'])
            for f in findings:
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

        # Optional bilingual CSV
        try:
            if any(isinstance(f, dict) and all(k in f for k in ('segment_id', 'source', 'target')) for f in findings):
                b_path = os.path.join(report_dir, f'analysis_findings_{ts}_bilingual.csv')
                with open(b_path, 'w', encoding='utf-8', newline='') as bcf:
                    bw = csv.writer(bcf, delimiter=';')
                    bw.writerow(['segment_id', 'source', 'target', 'severity', 'rule', 'message', 'suggestion', 'confidence'])
                    for f in findings:
                        if not (isinstance(f, dict) and all(k in f for k in ('segment_id', 'source', 'target'))):
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
        except Exception:
            pass

        # Optional grouped exports
        if findings_grouped:
            gsubset = findings_grouped
            if filters:
                q = (filters.get('query') or '').lower()
                sev = filters.get('severity')
                tmp = []
                for f in gsubset:
                    if sev and sev != 'ALL' and f.get('severity') != sev:
                        continue
                    if q and (q not in (f.get('message') or '').lower() and q not in (f.get('rule_id') or f.get('rule') or '').lower()):
                        continue
                    tmp.append(f)
                gsubset = tmp
            if gsubset:
                gcsv_path = os.path.join(report_dir, f'analysis_findings_{ts}_grouped.csv')
                with open(gcsv_path, 'w', encoding='utf-8', newline='') as gcf:
                    gw = csv.writer(gcf, delimiter=';')
                    gw.writerow(['severity', 'rule_id', 'message', 'count', 'confidence'])
                    for f in gsubset:
                        cnt = f.get('count') or 1
                        conf = f.get('confidence') if f.get('confidence') is not None else (f.get('avg_confidence') if isinstance(f.get('avg_confidence'), (int, float, str)) else f.get('avg_conf'))
                        try:
                            if isinstance(conf, str):
                                conf = float(conf)
                        except Exception:
                            pass
                        gw.writerow([
                            f.get('severity'),
                            (f.get('rule_id') or f.get('rule')),
                            (f.get('message') or '').replace('\n', ' '),
                            cnt,
                            conf if isinstance(conf, (int, float)) else ''
                        ])
                # HTML via optional manager
                try:
                    from src.export.format_manager import FormatExportManager  # type: ignore
                    fem = FormatExportManager(app_instance=app)
                    payload: Dict[str, Any] = {'findings': gsubset}
                    try:
                        full = getattr(app, 'analysis_results', {}) or {}
                        metrics_for_html = full.get('metrics') if isinstance(full.get('metrics'), dict) else None
                    except Exception:
                        metrics_for_html = None
                    if metrics_for_html:
                        payload['metrics'] = metrics_for_html
                    fem.export_data(payload, 'html', os.path.join(report_dir, f'analysis_findings_{ts}_grouped.html'))
                except Exception:
                    pass

        # Meta JSON
        try:
            meta = {
                'generated_at': datetime.datetime.now().isoformat(),
                'similarity_thresholds_used': ((getattr(app, 'analysis_results', {}) or {}).get('metrics') or {}).get('similarity_thresholds_used'),
                'filters': filters or {},
            }
            with open(os.path.join(report_dir, f'analysis_meta_{ts}.json'), 'w', encoding='utf-8') as mf:
                json.dump(meta, mf, ensure_ascii=False, indent=2)
        except Exception:
            pass

        return report_dir
    except Exception:
        return None


def make_correction_package(app: Any, findings: List[Dict[str, Any]], findings_grouped: List[Dict[str, Any]] | None = None) -> str | None:
    """Erzeugt ein Korrekturpaket (Ordner mit Dateien + ZIP). Gibt Paketpfad zurück oder None."""
    try:
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        base_dir = getattr(app, 'projects_base_path', '.') or '.'
        pkg_dir = os.path.join(base_dir, 'reports', f'korrekturpaket_{ts}')
        os.makedirs(pkg_dir, exist_ok=True)

        # Exportiere Grunddaten wieder, aber in Paket-Pfade
        # (Wiederverwendung von export_findings wäre möglich, hier explizit um im Paket-Namespace zu bleiben)
        used_thr = None
        try:
            full = getattr(app, 'analysis_results', {}) or {}
            used_thr = ((full.get('metrics') or {})).get('similarity_thresholds_used')
        except Exception:
            used_thr = None
        c_txt = m_txt = '–'
        try:
            if isinstance(used_thr, dict):
                c = used_thr.get('critical'); m = used_thr.get('major')
                c_txt = fmt_percent(c) if isinstance(c, (int, float)) else '–'
                m_txt = fmt_percent(m) if isinstance(m, (int, float)) else '–'
        except Exception:
            pass

        with open(os.path.join(pkg_dir, 'findings.txt'), 'w', encoding='utf-8') as fh:
            fh.write(f"Ähnlichkeitsschwellen: Kritisch ≥ {c_txt}, Wesentlich ≥ {m_txt}\n\n")
            for f in findings:
                fh.write(f"[{f.get('severity')}] {(f.get('rule_id') or f.get('rule') or 'rule')}: {(f.get('message') or '')}\n")

        with open(os.path.join(pkg_dir, 'findings.json'), 'w', encoding='utf-8') as jf:
            json.dump(findings, jf, ensure_ascii=False, indent=2)

        with open(os.path.join(pkg_dir, 'findings.csv'), 'w', encoding='utf-8', newline='') as cf:
            w = csv.writer(cf, delimiter=';')
            w.writerow(['severity', 'rule', 'checker', 'message', 'confidence'])
            for f in findings:
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

        # bilingual optional
        try:
            if any(isinstance(f, dict) and all(k in f for k in ('segment_id', 'source', 'target')) for f in findings):
                with open(os.path.join(pkg_dir, 'findings_bilingual.csv'), 'w', encoding='utf-8', newline='') as bcf:
                    bw = csv.writer(bcf, delimiter=';')
                    bw.writerow(['segment_id', 'source', 'target', 'severity', 'rule', 'message', 'suggestion', 'confidence'])
                    for f in findings:
                        if not (isinstance(f, dict) and all(k in f for k in ('segment_id', 'source', 'target'))):
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
        except Exception:
            pass

        # grouped optional
        if findings_grouped:
            with open(os.path.join(pkg_dir, 'findings_grouped.csv'), 'w', encoding='utf-8', newline='') as gcf:
                gw = csv.writer(gcf, delimiter=';')
                gw.writerow(['severity', 'rule_id', 'message', 'count', 'confidence'])
                for f in findings_grouped:
                    cnt = f.get('count') or 1
                    conf = f.get('confidence') if f.get('confidence') is not None else (f.get('avg_confidence') if isinstance(f.get('avg_confidence'), (int, float, str)) else f.get('avg_conf'))
                    try:
                        if isinstance(conf, str):
                            conf = float(conf)
                    except Exception:
                        pass
                    gw.writerow([
                        f.get('severity'),
                        (f.get('rule_id') or f.get('rule')),
                        (f.get('message') or '').replace('\n', ' '),
                        cnt,
                        conf if isinstance(conf, (int, float)) else ''
                    ])
            try:
                from src.export.format_manager import FormatExportManager  # type: ignore
                fem = FormatExportManager(app_instance=app)
                payload: Dict[str, Any] = {'findings': findings_grouped}
                fem.export_data(payload, 'html', os.path.join(pkg_dir, 'findings_grouped.html'))
            except Exception:
                pass

        # README
        try:
            with open(os.path.join(pkg_dir, 'README.txt'), 'w', encoding='utf-8') as rf:
                rf.write('Korrekturpaket\n')
                rf.write('================\n\n')
                rf.write('Überblick\n---------\n')
                rf.write('Dieses Paket bündelt alle relevanten Befunde der letzten Analyse in verschiedenen Formaten.\n\n')
                rf.write('Ähnlichkeitsschwellen (genutzt)\n--------------------------------\n')
                rf.write(f"Kritisch ≥ {c_txt}, Wesentlich ≥ {m_txt}\n\n")
                rf.write('Dateien\n-------\n')
                rf.write('- findings.txt / .json / .csv\n')
                rf.write('- findings_bilingual.csv (falls möglich)\n')
                rf.write('- findings_grouped.csv / .html (falls gruppierte Daten)\n')
                rf.write('- meta.json\n')
        except Exception:
            pass

        # meta
        try:
            meta = {
                'generated_at': datetime.datetime.now().isoformat(),
                'similarity_thresholds_used': ((getattr(app, 'analysis_results', {}) or {}).get('metrics') or {}).get('similarity_thresholds_used'),
            }
            with open(os.path.join(pkg_dir, 'meta.json'), 'w', encoding='utf-8') as mf:
                json.dump(meta, mf, ensure_ascii=False, indent=2)
        except Exception:
            pass

        # zip
        zip_path = None
        try:
            zip_path = shutil.make_archive(pkg_dir, 'zip', pkg_dir)
        except Exception:
            zip_path = None

        return zip_path or pkg_dir
    except Exception:
        return None
