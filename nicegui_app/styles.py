# -*- coding: utf-8 -*-
"""CSS design system fuer das Qualitaets-Framework.

Einzige Quelle fuer APP_CSS – wird von main.py, page_kalender.py und
page_kunden.py via `ui.add_head_html(APP_CSS)` eingebunden.
"""

APP_CSS = '''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800;1,9..40,400&display=swap');

:root{
  --primary:#0a1628;--primary-light:#1a365d;--accent:#d4af37;
  --success:#16a34a;--warning:#d97706;--error:#dc2626;--info:#2563eb;
  --surface:#ffffff;--surface-alt:#f8fafc;--surface-border:#e2e8f0;
  --surface-border-light:#f1f5f9;--surface-border-strong:#d1d5db;
  /* Semantic tint borders */
  --border-warning:#fed7aa;--border-success:#bbf7d0;--border-info:#93c5fd;
  /* Rollen-Farben (Datei-Zuordnung) — Quelle weicher als --primary */
  --role-source:#2563eb;
  --text:#0f172a;--text-muted:#64748b;--text-light:#94a3b8;
  /* Semantic text colors for colored backgrounds */
  --text-body:#334155;--text-inverse:#ffffff;
  --success-text:#064e3b;--warning-text:#92400e;--error-text:#7f1d1d;
  --radius-sm:6px;--radius-md:10px;--radius-lg:14px;--radius-pill:50px;
  /* Typography scale (7 Stufen) */
  --fs-xs:11px;--fs-sm:12px;--fs-md:13px;--fs-lg:14px;
  --fs-xl:16px;--fs-2xl:18px;--fs-3xl:24px;
  --lh-tight:1.35;--lh-normal:1.5;--lh-loose:1.65;
  --fw-regular:400;--fw-medium:500;--fw-semibold:600;--fw-bold:700;
  /* Background tints (soft = light tint, tint = noch heller) */
  --bg-primary:#0f2744;--bg-muted:#f1f5f9;
  --bg-info-soft:#eff6ff;--bg-info-tint:#f0f9ff;
  --bg-warning-soft:#fef3c7;--bg-warning-tint:#fff7ed;
  --bg-success-soft:#ecfdf5;--bg-success-tint:#f0fdf4;
  --bg-error-soft:#fecaca;--bg-error-tint:#fef2f2;
  /* Brand-Verlaeufe — zentral statt inline dupliziert; Badge-Variante wird
     im Dark-Mode unten auf eine Volltonfarbe gesetzt (ersetzt den frueheren
     fragilen [style*=...]-Override). */
  --brand-grad:linear-gradient(135deg,#0a1628 0%,#0f2744 40%,#1a365d 100%);
  --brand-grad-badge:linear-gradient(135deg,#0f2744,#1a365d);
}
html,body{overflow-x:hidden!important}

/* ── Einheitliche Schriftart überall (DM Sans überschreibt Quasar Roboto) ── */
*,*::before,*::after{
  font-family:'DM Sans','Segoe UI',system-ui,-apple-system,sans-serif!important;
}
/* Material Icons / icon-Elemente MÜSSEN ihre eigene Schrift behalten */
.material-icons,.material-icons-outlined,.material-icons-round,
.material-symbols-outlined,.material-symbols-rounded,
.q-icon,i.q-icon,[class*="notranslate"]{
  font-family:'Material Icons','Material Icons Outlined','Material Symbols Outlined',
              'Material Symbols Rounded'!important;
}
/* Ausnahmen: Monospace-Elemente behalten ihre Schriftart */
code,pre,kbd,samp,.monospace{
  font-family:'Courier New',Courier,monospace!important;
}
body{font-size:var(--fs-md)!important;line-height:var(--lh-normal);
    color:var(--text);background:var(--surface-alt);
    -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
    text-rendering:optimizeLegibility}
/* Zahlen mit gleicher Breite (Score, Counter, Listen) */
.tabular-nums,.q-badge,.score-inner{font-variant-numeric:tabular-nums!important;
    font-feature-settings:"tnum"!important}

/* Typography — clear hierarchy */
.t-caption{font-size:var(--fs-sm)!important;color:var(--text-muted)}
.t-body{font-size:var(--fs-md)!important}
.t-label{font-size:var(--fs-md)!important;font-weight:600!important}
.t-heading{font-size:var(--fs-lg)!important;font-weight:700!important}
.t-title{font-size:var(--fs-2xl)!important;font-weight:700!important}
.section-label{font-size:var(--fs-sm)!important;font-weight:700!important;
    text-transform:uppercase;letter-spacing:1.5px;color:var(--text-light)}

/* Quasar component overrides */
.q-checkbox__label{font-size:var(--fs-md)!important}
.q-select .q-field__native,.q-input .q-field__native{font-size:var(--fs-md)!important}
.q-field__label{font-size:var(--fs-sm)!important}
.q-expansion-item__toggle,.q-item__label{font-size:var(--fs-md)!important}

/* Cards — elevated with subtle shadow */
.q-card{border-radius:var(--radius-md)!important;
    border:1px solid var(--surface-border)!important;
    box-shadow:0 1px 3px rgba(0,0,0,.04)!important;transition:all .2s ease}
.q-card:hover{box-shadow:0 4px 12px rgba(0,0,0,.08)!important;
    border-color:rgba(0,0,0,.1)!important}

/* Buttons — rounded, with hover */
.q-btn{border-radius:var(--radius-sm)!important;font-weight:600!important;
    letter-spacing:.2px!important;transition:all .15s ease!important}
.q-btn:hover{transform:translateY(-1px)!important}
.q-btn:active{transform:translateY(0)!important}
.q-badge{border-radius:var(--radius-pill)!important}

/* ── Sichtbarer Tastatur-Fokus (Barrierefreiheit) ──
   Nur bei Tastatur-Navigation (:focus-visible), nicht bei Maus-Klick.
   !important, da Quasar/Browser-Defaults teils ueberschrieben werden. */
*:focus-visible{outline:2px solid var(--info)!important;outline-offset:2px!important;
    border-radius:var(--radius-sm)}
/* Custom-klickbare Elemente (sofern fokussierbar) ebenfalls deutlich markieren */
.stat-pill:focus-visible,.choice-card:focus-visible,.cust-card:focus-visible,
.finding-card:focus-visible,.file-row:focus-visible{
    outline:2px solid var(--info)!important;outline-offset:2px!important}

/* Klickbare Kundenkarten — deutlicher Hover + Chevron-Verschiebung */
.cust-card{transition:transform .15s ease,box-shadow .15s ease,border-color .15s ease,background .15s ease}
.cust-card:hover{transform:translateX(2px);
    border-color:var(--border-info)!important;
    background:var(--bg-info-tint)!important;
    box-shadow:0 3px 10px rgba(15,39,68,.08)!important}
.cust-card .cust-chevron{opacity:.35;transition:opacity .15s ease,transform .15s ease}
.cust-card:hover .cust-chevron{opacity:.9;transform:translateX(2px)}

/* Finding-Cards — dezenter Hover-Lift (nicht im Split-Modus) */
.finding-card{transition:box-shadow .15s ease,transform .15s ease}
.finding-card:hover{box-shadow:0 4px 14px rgba(15,39,68,.10)!important;transform:translateY(-1px)}

/* Aktivitätsliste-Zeilen */
.act-row:hover{background:var(--bg-info-soft)!important}

/* Summary-Stat-Pills — klickbar als Severity-Filter */
.stat-pill{transition:transform .15s ease,box-shadow .15s ease,background .15s ease;
    border-radius:var(--radius-md);cursor:pointer}
.stat-pill:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(15,39,68,.10)}
.stat-pill.stat-active{box-shadow:0 0 0 2px currentColor inset}

/* Score ring — @property enables smooth CSS custom property transitions */
@property --pct { syntax: '<percentage>'; inherits: false; initial-value: 0%; }
@property --sc { syntax: '<color>'; inherits: false; initial-value: #e2e8f0; }
.score-ring{background:conic-gradient(var(--sc) var(--pct),
    rgba(0,0,0,.06) var(--pct));border-radius:50%;padding:4px;
    transition:--pct 700ms cubic-bezier(.4,0,.2,1),--sc 700ms ease}
.score-inner{background:var(--surface);border-radius:50%;display:flex;
    align-items:center;justify-content:center;width:100%;height:100%}

/* Upload zones: hidden chrome */
.q-uploader{border-radius:var(--radius-sm)!important;overflow:hidden;
    box-shadow:none!important;border:none!important;background:transparent!important}
.q-uploader__subtitle,.q-uploader__list,.q-uploader__file{display:none!important}
.q-uploader__list:empty{display:none!important}
/* Transparent header so the dashed wrapper is the visual drop zone */
.q-uploader__header{background:transparent!important;padding:6px 8px!important;
    min-height:unset!important}
.q-uploader__header-content{padding:0!important;min-height:unset!important;gap:4px}
.q-uploader__title{font-size:var(--fs-sm)!important;line-height:1.3!important;
    white-space:normal!important;font-weight:600!important;color:var(--text-body)!important}

/* Scrollbar — thin & subtle */
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:rgba(0,0,0,.12);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:rgba(0,0,0,.2)}

/* Animations */
@keyframes fadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}
.animate-in{animation:fadeIn .25s ease-out}

/* Folder expansion — inherit colors */
.folder-exp .q-icon{color:inherit!important}
.folder-exp .q-expansion-item__toggle-icon{color:var(--text-light)!important}
/* Ordner-Header: Icon naeher an den Titel (Quasar-Avatar-Min-Breite zu gross) */
.folder-exp .q-item__section--avatar{min-width:unset!important;padding-right:10px!important}
.folder-exp>.q-expansion-item__container>.q-item{padding:6px 4px!important;min-height:unset!important}
/* Datei-Liste: dezent eingerueckt unter dem Ordner */
.folder-exp .q-expansion-item__content{padding-left:8px!important}

/* Datei-Zeilen (Projektordner-Ansicht) — Rollen-Akzent + Hover-Reveal */
.file-row{transition:background .12s ease,border-color .12s ease}
.file-row:hover{background:var(--bg-muted)!important}
.file-row .file-del{opacity:0;transition:opacity .12s ease}
.file-row:hover .file-del{opacity:1}
.folder-empty{opacity:.7;transition:opacity .12s ease}
.folder-empty:hover{opacity:1}
.folder-empty .folder-up{opacity:0;transition:opacity .12s ease}
.folder-empty:hover .folder-up{opacity:1}
/* Count-Badge im Ordner-Header */
.folder-badge{display:inline-flex;align-items:center;justify-content:center;
    min-width:18px;height:18px;padding:0 6px;border-radius:9px;
    font-size:var(--fs-xs);font-weight:700;line-height:1;
    background:var(--bg-muted);color:var(--text-muted)}
/* Zuordnungs-Abschnitt */
.assign-box{background:var(--surface-alt);border:1px solid var(--surface-border);
    border-radius:var(--radius-md);padding:12px}
.pair-row{transition:background .12s ease}
.pair-row .pair-del{opacity:0;transition:opacity .12s ease}
.pair-row:hover .pair-del{opacity:1}
/* Top-Kategorien-Heatmap: Zeilen-Hover */
.cat-row{transition:background .12s ease}
.cat-row:hover{background:var(--bg-muted)}
/* Klickbare Auswahl-Karten (Entfernen-Dialog) */
.choice-card{cursor:pointer;border-radius:var(--radius-md);border:1px solid var(--surface-border);
    background:var(--surface);transition:border-color .12s ease,background .12s ease,
    box-shadow .12s ease,transform .06s ease}
.choice-card:hover{border-color:var(--primary);background:var(--surface-alt);
    box-shadow:0 2px 10px rgba(0,0,0,.08)}
.choice-card:active{transform:translateY(1px)}
.choice-card .choice-go{color:var(--text-light);transition:transform .12s ease,color .12s ease}
.choice-card:hover .choice-go{color:var(--primary);transform:translateX(3px)}
.choice-card-danger:hover{border-color:var(--error);background:var(--bg-error-tint)}
.choice-card-danger:hover .choice-go{color:var(--error)}

/* Dark mode */
body.body--dark{--surface:#0f172a;--surface-alt:#1e293b;--surface-border:#334155;
    --surface-border-light:#273449;--surface-border-strong:#475569;
    --border-warning:#78350f;--border-success:#14532d;--border-info:#1e3a5f;
    --role-source:#60a5fa;
    --text:#e2e8f0;--text-muted:#94a3b8;--text-light:#64748b;
    /* --primary dient app-weit als Vordergrund/Textfarbe → im Dark-Mode hell
       (Hintergruende laufen ueber --bg-primary, das dunkel bleibt) */
    --primary:#e8eef8;--accent:#d4af37;--info:#60a5fa;
    --text-body:#cbd5e1;--success-text:#6ee7b7;--warning-text:#fbbf24;--error-text:#fca5a5;
    --bg-primary:#0a1628;--bg-muted:#1e293b;
    --bg-info-soft:#0c1a2e;--bg-info-tint:#0c1827;
    --bg-warning-soft:#2d2006;--bg-warning-tint:#1f1505;
    --bg-success-soft:#052e16;--bg-success-tint:#031f0e;
    --bg-error-soft:#3b0a0a;--bg-error-tint:#260606;
    /* Avatar-/Badge-Verlauf wird im Dark-Mode zu Vollton (wie zuvor) */
    --brand-grad-badge:#0a1628}
body.body--dark .score-inner{background:var(--surface)}
body.body--dark .q-card{border-color:var(--surface-border)!important;background:var(--surface-alt)!important}

/* Save indicator */
.save-indicator{opacity:0;transition:opacity 300ms ease}
.save-indicator.visible{opacity:1}

/* Header-Buttons: Hover-Akzent (Quasar overrides .q-btn:hover transform; setze opacity) */
.q-header .q-btn{transition:opacity .15s ease,background .15s ease!important}
.q-header .q-btn:hover{opacity:1!important;background:rgba(255,255,255,.08)!important}

/* Responsive Header: Beschriftungen unter 1024px ausblenden (Icon-only + Tooltip),
   damit die rechten Aktionen nicht abgeschnitten werden */
@media (max-width:1023px){
  .hdr-label{display:none!important}
  .hdr-subtitle{display:none!important}
}

/* Responsive: Split-/Mehrspalten-Layouts unter 900px untereinander stapeln
   (sonst werden feste Panel-Breiten — Sidebar, Detail-Panel — gequetscht). */
@media (max-width:900px){
  .qf-stack{flex-direction:column!important;flex-wrap:nowrap!important;gap:12px!important}
  .qf-stack>*{width:100%!important;max-width:100%!important;min-width:0!important;
      max-height:none!important;border-right:none!important}
}
</style>'''
