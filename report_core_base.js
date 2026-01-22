// Core Report Renderer (Mode: export | team) - renamed from report_core.js
export async function loadReportData({ source }) {
  if (typeof source === 'object') return structuredClone(source);
  const res = await fetch(source, { cache: 'no-store' });
  if (!res.ok) throw new Error('Report laden fehlgeschlagen: ' + res.status);
  return await res.json();
}
export function normalizeData(data) {
  const issues = (data.issues || []).map((i, idx) => ({
    id: i.id || 'issue_' + (idx + 1),
  code: i.code || '', // optional Code aus Upstream-Checkern
    priority: i.priority || 'mittel',
    category: i.category || 'Allgemein',
    location: i.location || '',
    description: i.description || '(Keine Beschreibung)',
    sourceText: i.sourceText || '',
    currentText: i.currentText || '',
    suggestedText: i.suggestedText || '',
    recommendation: i.recommendation || '',
    status: i.status || { marked: false, resolved: false },
    notes: i.notes || [],
    comments: i.comments || []
  }));
  return { meta: data.meta || { reportId: crypto.randomUUID(), generatedAt: new Date().toISOString() }, issues };
}
export function createStateManager(data, { persist = true } = {}) {
  const key = 'checker:team:report:' + data.meta.reportId;
  const listeners = new Set();
  const state = {
    data,
    map: new Map(data.issues.map(i => [i.id, i])),
    subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
    emit() { listeners.forEach(l => l(state)); if (persist) save(); },
    toggle(id, field) { const issue = this.map.get(id); if (!issue) return; issue.status[field] = !issue.status[field]; this.emit(); },
    addNote(id, text, author = 'User') { const issue = this.map.get(id); if (!issue) return; issue.notes.push(makeEntry(text, author)); this.emit(); },
    addComment(id, text, author = 'User') { const issue = this.map.get(id); if (!issue) return; issue.comments.push(makeEntry(text, author)); this.emit(); },
    deleteNote(id, entryId) { mutateList(id, 'notes', entryId); },
    deleteComment(id, entryId) { mutateList(id, 'comments', entryId); },
    exportData() { return JSON.parse(JSON.stringify([...this.map.values()])); },
    clearInteractive() { this.map.forEach(i => { i.status = { marked: false, resolved: false }; i.notes = []; i.comments = []; }); this.emit(); }
  };
  function mutateList(id, field, entryId) { const issue = state.map.get(id); if (!issue) return; issue[field] = issue[field].filter(e => e.id !== entryId); state.emit(); }
  function makeEntry(text, author) { return { id: Date.now() + Math.random(), text, author, time: new Date().toISOString() }; }
  function save() { try { localStorage.setItem(key, JSON.stringify([...state.map.values()].map(i => ({ id: i.id, status: i.status, notes: i.notes, comments: i.comments })))); } catch { /* ignore */ } }
  function load() { try { const raw = localStorage.getItem(key); if (!raw) return; const arr = JSON.parse(raw); arr.forEach(s => { const issue = state.map.get(s.id); if (issue) { issue.status = s.status || issue.status; issue.notes = s.notes || issue.notes; issue.comments = s.comments || issue.comments; } }); } catch { /* ignore */ } }
  if (persist) { load(); }
  return state;
}
export function renderReport({ container, data, mode = 'export' }) {
  container.innerHTML = '';
  const frag = document.createDocumentFragment();
  // Nur Hauptcontainer (nicht innerhalb gruppierter Sektionen) bekommt Aspekt-Box
  const isGrouped = container.classList && container.classList.contains('group-issues');
  if (mode === 'export' && !isGrouped) {
    frag.appendChild(renderAspectSummary(data.issues));
  }
  data.issues.forEach(issue => frag.appendChild(renderIssue(issue, mode)));
  container.appendChild(frag);
  if (mode === 'export') applyExportStyling(container);
}
function renderIssue(issue, mode) {
  const art = document.createElement('article');
  art.className = 'issue';
  const catSlug = (issue.category || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  art.dataset.id = issue.id;
  art.innerHTML = `
    <header class="issue-header">
      <h3 class="issue-title">${escapeHTML(issue.description)}</h3>
      <div class="meta-line">
        <span class="badge priority-${issue.priority}">${issue.priority}</span>
        <span class="badge category ${catSlug}">${escapeHTML(issue.category)}</span>
        ${issue.location ? `<span class="location">${escapeHTML(issue.location)}</span>` : ''}
        ${mode === 'team' ? '<span class="status-badges" data-status-badges></span>' : ''}
      </div>
    </header>
    <section class="comparison">
      <table class="cmp-table">
        <thead><tr><th>Original</th><th>Aktuell</th><th>Vorschlag</th></tr></thead>
        <tbody><tr>
          <td>${escapeMulti(issue.sourceText)}</td>
          <td>${escapeMulti(issue.currentText)}</td>
          <td>${escapeMulti(issue.suggestedText || '—')}</td>
        </tr></tbody>
      </table>
    </section>
    ${issue.recommendation ? `<p class="recommendation"><strong>Empfehlung:</strong> ${escapeMulti(issue.recommendation)}</p>` : ''}
    ${mode === 'team' ? '<div class="interactive-slot" data-interactive></div>' : ''}
    ${mode === 'export' && issue.notes && issue.notes.length ? `<ul class="notes">${issue.notes.map(n=>`<li>${escapeMulti(n.text)} – <em>${escapeHTML(n.author||'')}</em></li>`).join('')}</ul>` : ''}
    ${mode === 'export' && issue.comments && issue.comments.length ? `<ul class="comments">${issue.comments.map(c=>`<li>${escapeMulti(c.text)} – <em>${escapeHTML(c.author||'')}</em></li>`).join('')}</ul>` : ''}
  `;
  return art;
}
function applyExportStyling(root) { root.querySelectorAll('.interactive-slot, .status-badges').forEach(n => n.remove()); }
export function escapeHTML(str) { return String(str).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
export function escapeMulti(str) { return escapeHTML(str).replace(/\n/g, '<br>'); }
export function ensureBaseStyles() {
  if (document.getElementById('report-core-styles')) return;
  const style = document.createElement('style');
  style.id = 'report-core-styles';
  style.textContent = `
  :root { --c-border:#e2e8f0; --c-bg:#fff; --c-text:#111; --c-muted:#555; --c-accent:#1F4E79; }
  .issue { border:1px solid var(--c-border); border-radius:8px; padding:16px; margin:0 0 20px; background:var(--c-bg); page-break-inside: avoid; }
  .issue-header { display:flex; flex-direction:column; gap:4px; margin-bottom:8px; }
  .issue-title { margin:0; font-size:1.05rem; line-height:1.3; }
  .meta-line { display:flex; flex-wrap:wrap; gap:6px; font-size:.75rem; color:var(--c-muted); }
  .badge { background:#f1f5f9; padding:2px 6px; border-radius:4px; }
  .priority-kritisch { background:#DC2626; color:#fff; }
  .priority-hoch { background:#F97316; color:#fff; }
  .priority-mittel { background:#2563EB; color:#fff; }
  .priority-hinweis { background:#64748B; color:#fff; }
  /* Kategorie-spezifische Badges */
  .badge.category.terminology { background:#9333EA; color:#fff; }
  .badge.category.style { background:#0D9488; color:#fff; }
  .badge.category.semantic { background:#7C3AED; color:#fff; }
  .badge.category.completeness { background:#4338CA; color:#fff; }
  .badge.category.numbers { background:#0369A1; color:#fff; }
  table.cmp-table { width:100%; border-collapse:collapse; font-size:.75rem; }
  .cmp-table th, .cmp-table td { border:1px solid var(--c-border); padding:6px 8px; vertical-align:top; }
  .recommendation { font-size:.75rem; margin:10px 0 0; }
  .notes, .comments { list-style:disc; margin:8px 0 0 18px; padding:0; font-size:.65rem; color:var(--c-muted); }
  .notes li, .comments li { margin:0 0 2px; }
  .notes em, .comments em { font-style:normal; color:var(--c-text); }
  /* Aspekt-Zusammenfassung */
  .aspect-summary { border:1px solid var(--c-border); border-radius:8px; background:var(--c-bg); padding:12px 14px; margin:0 0 18px; page-break-inside: avoid; }
  .aspect-summary .aspect-title { margin:0 0 8px; font-size:.95rem; color:var(--c-text); }
  .aspect-summary .aspect-list { display:grid; grid-template-columns: repeat(auto-fit, minmax(110px,1fr)); gap:10px; padding:0; margin:0; list-style:none; }
  .aspect-summary .aspect-kpi { display:flex; align-items:center; gap:8px; border:1px dashed var(--c-border); border-radius:6px; padding:8px 10px; }
  .aspect-summary .kpi { display:inline-block; min-width:2ch; text-align:right; font-weight:600; color:var(--c-accent); }
  .aspect-summary .kpi-label { color:var(--c-muted); font-size:.8rem; }
  @media print { body { color:#000; } .issue { box-shadow:none; } }
  `;
  document.head.appendChild(style);
}
/**
 * Liefert aggregierte Dimensionen für Header-Zusammenfassung.
 * Dimensions:
 *  - numbersUnits: NUMBER_MISSING / NUMBER_ADDED / UNIT_DRIFT
 *  - spelling: grammar.lt.* / hunspell.spelling / heuristic.*
 *  - completeness: PLACEHOLDER_* / URL_* / EMAIL_* / HTML_* / SEMANTIC_LOW / COVERAGE_RATIO_LOW
 *  - names: TERM_PREFERRED_MISSING / PROPER_NAME_MISSING
 */
export function summarizeIssueDimensions(issues = []) {
  const res = { total: issues.length, numbersUnits:0, spelling:0, completeness:0, names:0 };
  for (const i of issues) {
    const c = i.code || '';
    if (c === 'NUMBER_MISSING' || c === 'NUMBER_ADDED' || c === 'UNIT_DRIFT') res.numbersUnits++;
    else if (c.startsWith('grammar.lt.') || c === 'hunspell.spelling' || c.startsWith('heuristic.')) res.spelling++;
    else if (/^(PLACEHOLDER_|URL_|EMAIL_|HTML_)/.test(c) || c === 'SEMANTIC_LOW' || c === 'COVERAGE_RATIO_LOW') res.completeness++;
    else if (c === 'TERM_PREFERRED_MISSING' || c === 'PROPER_NAME_MISSING') res.names++;
  }
  res.toString = () => `Zahlen/Einheiten: ${res.numbersUnits} • Rechtschreibung: ${res.spelling} • Vollständigkeit: ${res.completeness} • Namen: ${res.names}`;
  return res;
}

// --- Heuristik für 4 Kern-Aspekte (breiter, nutzt Beschreibung/Kategorie) ---
function summarizeAspects(issues) {
  const out = { names: 0, numbers: 0, completeness: 0, spelling: 0 };
  for (const it of issues) {
    const code = String(it.code || '').toLowerCase();
    const cat  = String(it.category || '').toLowerCase();
    const desc = String(it.description || '').toLowerCase();
    // Namen / Terminologie / Proper Names
    if (cat.includes('terminolog') || code.startsWith('term') || code.includes('proper_name') || /\bname(n)?\b|eigenname|proper/.test(desc)) out.names++;
    // Zahlen / Einheiten
    if (code.startsWith('number') || code.startsWith('unit') || /\bzahl(en)?\b|einheit(en)?|\bproz|percent|unit|number/.test(desc)) out.numbers++;
    // Vollständigkeit
    if (code.includes('missing') || code.includes('unclosed') || code.includes('unbalanced') || /\bfehlt|fehlend|nicht vorhanden/.test(desc)) out.completeness++;
    // Rechtschreibung / Grammatik
    if (code.startsWith('hunspell') || code.startsWith('grammar.lt') || code.startsWith('ollama.grammar') || /rechtschreib|schreibfehler|typo|spelling|grammatik/.test(desc)) out.spelling++;
  }
  return out;
}

function renderAspectSummary(issues) {
  const a = summarizeAspects(issues);
  const wrap = document.createElement('section');
  wrap.className = 'aspect-summary';
  wrap.innerHTML = `
    <h2 class="aspect-title">Prüf-Aspekte</h2>
    <ul class="aspect-list" role="list">
      <li class="aspect-kpi"><span class="kpi">${a.names}</span><span class="kpi-label">Namen</span></li>
      <li class="aspect-kpi"><span class="kpi">${a.numbers}</span><span class="kpi-label">Zahlen</span></li>
      <li class="aspect-kpi"><span class="kpi">${a.completeness}</span><span class="kpi-label">Vollständigkeit</span></li>
      <li class="aspect-kpi"><span class="kpi">${a.spelling}</span><span class="kpi-label">Rechtschreibung</span></li>
    </ul>`;
  return wrap;
}
