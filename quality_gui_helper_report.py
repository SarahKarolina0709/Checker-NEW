"""Helper-Modul für dynamischen Qualitätsbericht (umbenannt).

Ehemals: helper_quality_report.py
Ziel: Konsistenter Prefix quality_gui_*

Regeln:
  - No-Icons / No-Emoji in UI (hier nur HTML-Ausgabe, keine GUI-Labels verändert)
  - Light Mode Farben ausschließlich über app.get_color()
  - High Contrast Unterstützung (setzt schwarze Schrift im HC-Modus)
"""
from __future__ import annotations
import os, json, datetime, html
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # nur für Typprüfung
    from quality_gui_main_app import ProfessionelleUebersetzungsqualitaetsApp


def _safe_color(app: 'ProfessionelleUebersetzungsqualitaetsApp', token: str, fallback: str = 'white') -> str:
    """Robuster Farbzugriff über app.get_color mit Fallback-Kaskade."""
    try:
        return app.get_color(token)
    except Exception:
        try:
            return app.get_color(fallback)
        except Exception:
            return '#FFFFFF'


def generate_dynamic_report(app: 'ProfessionelleUebersetzungsqualitaetsApp') -> str | None:
    """Erzeugt einen dynamischen HTML-Bericht (Pfad zurück) oder None bei Fehler.

    Anforderungen:
      - Keine Icons / Emojis in GUI-Elementen (hier nur HTML/Text)
      - Light Mode only (Farben aus Design-System, keine Dark-Colors)
      - High-Contrast Unterstützung (schwarzer Text, klarere Kontraste) ohne Dark Mode
    """
    try:
        analysis_results = getattr(app, 'analysis_results', None)
        if not analysis_results or not isinstance(analysis_results, dict):
            return None

        base_dir = os.path.dirname(__file__)
        target_path = os.path.join(base_dir, 'Bericht_Dynamisch.html')

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        meta = {
            'generated_at': now,
            'source': 'quality_gui_main_app',
            'item_counts': {}
        }

        for k, v in analysis_results.items():
            try:
                if isinstance(v, (list, tuple, dict)):
                    meta['item_counts'][k] = len(v)
            except Exception:
                pass

        payload = {'meta': meta, 'reportData': analysis_results}
        try:
            json_blob = json.dumps(payload, ensure_ascii=False, indent=2)
        except Exception:
            json_blob = '{}'

        counts_html = ' '.join(
            f"<span>{html.escape(k)}: {v}</span>" for k, v in meta['item_counts'].items()
        ) or '<em>Keine Strukturmetriken</em>'

        # Farb-Mini-Cache
        _clr_cache: dict[str, str] = {}
        def C(tok: str, fb: str = 'white') -> str:
            if tok in _clr_cache:
                return _clr_cache[tok]
            val = _safe_color(app, tok, fb)
            _clr_cache[tok] = val
            return val

        hc = bool(getattr(app, '_high_contrast_enabled', False))
        color_surface = C('surface')
        color_text = ('#000000' if hc else C('gray_700'))
        color_panel = C('gray_50') if not hc else C('white')
        color_border = C('surface_border')
        color_badge_border = color_border
        color_badge_bg = C('white') if not hc else C('gray_100')
        color_footer = ('#111111' if hc else C('gray_500'))
        color_button = ('#000000' if hc else C('primary'))
        color_button_hover = (C('gray_700') if hc else C('primary_hover'))
        color_filter_border = C('input_border')
        color_table_header = (C('gray_200') if hc else C('gray_100'))
        color_white = C('white')  # für Buttons

        # Template
        template = """<!DOCTYPE html>
<html lang=\"de\">
<head>
<meta charset=\"UTF-8\" />
<title>Dynamischer Qualitätsbericht</title>
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
<style>
 body{{font-family:Segoe UI,Arial,sans-serif;background:{color_surface};margin:24px;color:{color_text};}}
 h1{{font-size:24px;margin:0 0 8px;font-weight:600;}}
 h2{{font-size:18px;margin:32px 0 12px;font-weight:600;}}
 .meta, .summary{{background:{color_panel};border:1px solid {color_border};border-radius:8px;padding:16px;margin-bottom:20px;}}
 code,pre{{font-family:Consolas,monospace;font-size:12px;}}
 .counts span{{display:inline-block;margin:4px 8px 4px 0;padding:4px 8px;border:1px solid {color_badge_border};border-radius:6px;background:{color_badge_bg};}}
 .raw-container{{border:1px solid {color_border};border-radius:8px;padding:16px;white-space:pre;overflow:auto;max-height:480px;background:{color_surface};}}
 .footer{{margin-top:40px;font-size:12px;color:{color_footer};}}
 button{{background:{color_button};color:{color_white};border:none;padding:8px 14px;border-radius:6px;cursor:pointer;font-size:14px;font-weight:600;}}
 button:hover{{background:{color_button_hover};}}
 .toolbar{{margin:0 0 16px;}}
 .filter-box{{border:1px solid {color_filter_border};border-radius:6px;padding:8px;margin:0 0 16px;}}
 input[type=text]{{padding:6px 8px;border:1px solid {color_filter_border};border-radius:4px;width:260px;}}
 table{{border-collapse:collapse;width:100%;margin-top:12px;}}
 th,td{{border:1px solid {color_border};padding:6px 8px;font-size:12px;text-align:left;vertical-align:top;}}
 th{{background:{color_table_header};font-weight:600;}}
 .hidden{{display:none;}}
</style>
</head>
<body>
<h1>Qualitätsbericht (Dynamisch)</h1>
<div class=\"meta\">\n  <strong>Erstellt:</strong> {generated_at}<br/>\n  <strong>Quelle:</strong> {source}<br/>\n</div>
<div class=\"summary\">\n  <h2>Struktur Zusammenfassung</h2>\n  <div class=\"counts\">{counts_html}</div>\n  <p>Gefilterte Ansicht: Suchfeld verwenden. Rohdaten unten vollständig.</p>\n</div>
<div class=\"filter-box\">\n  <input id=\"filterInput\" type=\"text\" placeholder=\"Suchen...\" oninput=\"applyFilter()\" />\n  <button onclick=\"resetFilter()\">Zurücksetzen</button>\n</div>
<div id=\"dynamicTables\"></div>
<h2>Rohdaten JSON</h2>
<div class=\"raw-container\" id=\"rawJson\"></div>
<div class=\"footer\">Automatisch generiert – temporäre Datei (Bericht_Dynamisch.html).</div>
<script>
var payload = __JSON_PAYLOAD__;
var reportData = payload.reportData || {};
function esc(s){return String(s).replace(/[&<>"']/g, function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c];});}
function buildTables(){
  var container=document.getElementById('dynamicTables');
  container.innerHTML='';
  var keys=Object.keys(reportData);
  if(!keys.length){container.innerHTML='<em>Keine Daten</em>';return;}
  keys.forEach(function(k){
    var section=document.createElement('div');
    section.className='data-section';
    var val=reportData[k];
    var html='';
    if(Array.isArray(val) && val.length && typeof val[0]==='object'){
       var cols=[]; val.forEach(function(o){Object.keys(o).forEach(function(c){if(cols.indexOf(c)===-1) cols.push(c);});});
       html += '<h2>'+esc(k)+'</h2><table><thead><tr>' + cols.map(function(c){return '<th>'+esc(c)+'</th>';}).join('') + '</tr></thead><tbody>';
       val.forEach(function(row){ html+='<tr>'+cols.map(function(c){return '<td>'+esc(row[c]!==undefined?row[c]:'')+'</td>';}).join('')+'</tr>'; });
       html+='</tbody></table>';
    } else if (Array.isArray(val)) {
       html += '<h2>'+esc(k)+'</h2><div>' + val.map(function(i){return '<div>- '+esc(i)+'</div>';}).join('') + '</div>';
    } else if (val && typeof val==='object') {
       html += '<h2>'+esc(k)+'</h2><pre>'+esc(JSON.stringify(val,null,2))+'</pre>';
    } else {
       html += '<h2>'+esc(k)+'</h2><div>'+esc(val)+'</div>';
    }
    section.innerHTML=html;
    container.appendChild(section);
  });
}
function applyFilter(){
  var q=document.getElementById('filterInput').value.toLowerCase();
  Array.prototype.forEach.call(document.querySelectorAll('.data-section'), function(sec){
    sec.classList.remove('hidden');
    if(q && sec.textContent.toLowerCase().indexOf(q)===-1){ sec.classList.add('hidden'); }
  });
}
function resetFilter(){document.getElementById('filterInput').value='';applyFilter();}
function init(){
  buildTables();
  document.getElementById('rawJson').textContent=JSON.stringify(payload,null,2);
}
init();
</script>
</body>
</html>
""".format(
            color_surface=color_surface,
            color_text=color_text,
            color_panel=color_panel,
            color_border=color_border,
            color_badge_border=color_badge_border,
            color_badge_bg=color_badge_bg,
            color_footer=color_footer,
            color_button=color_button,
            color_button_hover=color_button_hover,
            color_filter_border=color_filter_border,
            color_table_header=color_table_header,
            color_white=color_white,
            generated_at=html.escape(meta['generated_at']),
            source=html.escape(meta['source']),
            counts_html=counts_html
        )
        template = template.replace('__JSON_PAYLOAD__', json_blob)

        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(template)
        except Exception:
            return None

        # Events / Logging (geräuschlos bei Fehlern)
        payload_event = {
            "path": target_path,
            "items": meta.get('item_counts', {}),
            "generated_at": meta.get('generated_at'),
            "high_contrast": hc
        }
        try:
            if hasattr(app, '_log_event'):
                app._log_event("report.dynamic.generated", payload_event)
        except Exception:
            pass
        try:
            if getattr(app, 'event_bus', None):
                app.event_bus.publish('report.dynamic.generated', payload_event)
        except Exception:
            pass
        return target_path
    except Exception:
        return None

__all__ = ["generate_dynamic_report"]
