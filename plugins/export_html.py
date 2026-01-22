from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def _esc(s: Any) -> str:
    try:
        from html import escape
        return escape(str(s), quote=True)
    except Exception:
        return str(s)

def generate_html_report(results: Dict[str, Any], out_dir: Path) -> Path:
    """Erzeugt einen einfachen HTML-Report zu Analyse-Ergebnissen."""
    out_dir.mkdir(parents=True, exist_ok=True)
    fn = out_dir / f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    html = ["<html><head><meta charset='utf-8'><title>Quality Report</title></head><body>"]
    html.append("<h1>Übersetzungsqualität – Report</h1>")
    findings = results.get('findings', []) or []
    html.append(f"<p>Befunde gesamt: {len(findings)}</p>")
    html.append("<ul>")
    for f in findings:
        rule_id = _esc(f.get('rule_id') or f.get('rule') or 'unbekannt')
        sev = _esc(f.get('severity', 'info'))
        msg = _esc(f.get('message', ''))
        conf = f.get('confidence')
        conf_txt = ''
        try:
            if isinstance(conf, str):
                conf = float(conf)
            if isinstance(conf, (int, float)):
                conf_txt = f" <em>(Confidence: {conf:.2f})</em>"
        except Exception:
            pass
        html.append(f"<li><strong>{rule_id}</strong> [{sev}]: {msg}{conf_txt}</li>")
    html.append("</ul></body></html>")
    fn.write_text("\n".join(html), encoding="utf-8")
    return fn
