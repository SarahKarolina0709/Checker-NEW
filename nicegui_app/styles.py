# -*- coding: utf-8 -*-
"""CSS design system fuer das Qualitaets-Framework.

Einzige Quelle fuer APP_CSS – wird von main.py, page_kalender.py und
page_kunden.py via `ui.add_head_html(APP_CSS)` eingebunden.
"""

APP_CSS = '''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

:root{
  --primary:#0a1628;--primary-light:#1a365d;--accent:#d4af37;
  --success:#16a34a;--warning:#d97706;--error:#dc2626;
  --surface:#ffffff;--surface-alt:#f8fafc;--surface-border:#e2e8f0;
  --text:#0f172a;--text-muted:#64748b;--text-light:#94a3b8;
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
}
body{font-family:'DM Sans','Segoe UI',system-ui,sans-serif!important;
    font-size:var(--fs-md)!important;line-height:var(--lh-normal);
    color:var(--text);background:var(--surface-alt);
    -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
    text-rendering:optimizeLegibility}
/* Zahlen mit gleicher Breite (Score, Counter, Listen) */
.tabular-nums,.q-badge,.score-inner{font-variant-numeric:tabular-nums!important;
    font-feature-settings:"tnum"!important}

/* Typography — clear hierarchy */
.t-caption{font-size:12px!important;color:var(--text-muted)}
.t-body{font-size:13px!important}
.t-label{font-size:13px!important;font-weight:600!important}
.t-heading{font-size:14px!important;font-weight:700!important}
.t-title{font-size:18px!important;font-weight:700!important}
.section-label{font-size:12px!important;font-weight:700!important;
    text-transform:uppercase;letter-spacing:1.5px;color:var(--text-light)}

/* Quasar component overrides */
.q-checkbox__label{font-size:13px!important}
.q-select .q-field__native,.q-input .q-field__native{font-size:13px!important}
.q-field__label{font-size:12px!important}
.q-expansion-item__toggle,.q-item__label{font-size:13px!important}

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

/* Score ring */
.score-ring{background:conic-gradient(var(--sc,var(--accent)) var(--pct,0%),
    rgba(0,0,0,.06) var(--pct,0%));border-radius:50%;padding:4px}
.score-inner{background:var(--surface);border-radius:50%;display:flex;
    align-items:center;justify-content:center;width:100%;height:100%}

/* Upload zones: hidden chrome */
.q-uploader{border-radius:var(--radius-sm)!important;overflow:hidden;
    box-shadow:none!important;border:none!important}
.q-uploader__subtitle,.q-uploader__list,.q-uploader__file{display:none!important}
.q-uploader__list:empty{display:none!important}

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

/* Dark mode */
body.body--dark{--surface:#0f172a;--surface-alt:#1e293b;--surface-border:#334155;
    --text:#e2e8f0;--text-muted:#94a3b8;--text-light:#64748b;
    --primary:#0a1628;--accent:#d4af37;
    --bg-primary:#0a1628;--bg-muted:#1e293b;
    --bg-info-soft:#0c1a2e;--bg-info-tint:#0c1827;
    --bg-warning-soft:#2d2006;--bg-warning-tint:#1f1505;
    --bg-success-soft:#052e16;--bg-success-tint:#031f0e;
    --bg-error-soft:#3b0a0a;--bg-error-tint:#260606}
body.body--dark .score-inner{background:var(--surface)}
body.body--dark .q-card{border-color:var(--surface-border)!important;background:var(--surface-alt)!important}
body.body--dark [style*="background:white"],
body.body--dark [style*="background:#fff"],
body.body--dark [style*="background:#ffffff"]{background:var(--surface-alt)!important}
body.body--dark [style*="background:#f8fafc"]{background:#1e293b!important}
body.body--dark [style*="border-bottom:1px solid #f1f5f9"],
body.body--dark [style*="border:1px solid #e2e8f0"]{border-color:var(--surface-border)!important}
/* Finding-Karten im Dark Mode */
body.body--dark [style*="border-top:1px solid #e5e7eb"],
body.body--dark [style*="border-right:1px solid #e5e7eb"],
body.body--dark [style*="border-bottom:1px solid #e5e7eb"]{border-color:#334155!important}
body.body--dark [style*="color:#334155"]{color:#cbd5e1!important}
body.body--dark [style*="color:#064e3b"]{color:#6ee7b7!important}
body.body--dark [style*="background:linear-gradient(135deg,#0f2744"]{background:#0a1628!important}
/* Severity-Gruppenheader */
body.body--dark [style*="background:#1e293b"]{background:#1e293b!important}
/* Finding-Karten im Dark Mode */
body.body--dark [style*="border-top:1px solid #e5e7eb"],
body.body--dark [style*="border-right:1px solid #e5e7eb"],
body.body--dark [style*="border-bottom:1px solid #e5e7eb"]{border-color:#334155!important}
body.body--dark [style*="background:#fef3c7"]{background:#2d2006!important}
body.body--dark [style*="color:#334155"]{color:#cbd5e1!important}
body.body--dark [style*="color:#064e3b"]{color:#6ee7b7!important}
body.body--dark [style*="background:#ecfdf5"]{background:#052e16!important}
body.body--dark [style*="background:#eff6ff"]{background:#0c1a2e!important}
body.body--dark [style*="background:#f0f9ff"]{background:#0c1827!important}
/* Sidebar + Header bleiben dunkel */
body.body--dark [style*="background:#0f2744"],
body.body--dark [style*="background:linear-gradient(135deg,#0f2744"]{background:#0a1628!important}
/* Severity-Gruppenheader */
body.body--dark [style*="background:#1e293b"]{background:#1e293b!important}

/* Save indicator */
.save-indicator{opacity:0;transition:opacity 300ms ease}
.save-indicator.visible{opacity:1}

/* Header-Buttons: Hover-Akzent (Quasar overrides .q-btn:hover transform; setze opacity) */
.q-header .q-btn{transition:opacity .15s ease,background .15s ease!important}
.q-header .q-btn:hover{opacity:1!important;background:rgba(255,255,255,.08)!important}
</style>'''
