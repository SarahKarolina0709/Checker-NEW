// Core Report Renderer (Mode: export | team)
// Gemeinsame Datenbasis, keine interaktiven Controls hier

export async function loadReportData({ source }) {
  if (typeof source === 'object') return structuredClone(source);
  const res = await fetch(source, { cache: 'no-store' });
  if (!res.ok) throw new Error('Report laden fehlgeschlagen: ' + res.status);
  return await res.json();
}

export function normalizeData(data) {
  const issues = (data.issues || []).map((i, idx) => ({
    id: i.id || 'issue_' + (idx + 1),
    priority: i.priority || 'mittel',
    category: i.category || 'Allgemein',
    location: i.location || '',
  code: i.code || '',
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
  if (mode === 'export') {
    const aspects = summarizeAspects(data.issues);
    const summaryDiv = document.createElement('div');
    summaryDiv.className = 'report-aspects-summary';
    summaryDiv.textContent = `Namen: ${aspects.names} • Zahlen: ${aspects.numbers} • Vollständigkeit: ${aspects.completeness} • Rechtschreibung: ${aspects.spelling}`;
    frag.appendChild(summaryDiv);
  }
  data.issues.forEach(issue => frag.appendChild(renderIssue(issue, mode)));
  container.appendChild(frag);
  if (mode === 'export') applyExportStyling(container);
}

function renderIssue(issue, mode) {
  const art = document.createElement('article');
  art.className = 'issue';
  const catSlug = (issue.category || '').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
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
  ${issue.recommendation ? `<p class="recommendation"><span class=\"rec-label\">Empfehlung:</span> ${escapeMulti(issue.recommendation)}</p>` : ''}
  ${mode === 'team' ? '<div class="interactive-slot" data-interactive></div>' : ''}
  ${mode === 'export' && issue.notes && issue.notes.length ? `<ul class="notes">${issue.notes.map(n=>`<li>${escapeMulti(n.text)} – <em>${escapeHTML(n.author||'')}</em></li>`).join('')}</ul>` : ''}
  ${mode === 'export' && issue.comments && issue.comments.length ? `<ul class="comments">${issue.comments.map(c=>`<li>${escapeMulti(c.text)} – <em>${escapeHTML(c.author||'')}</em></li>`).join('')}</ul>` : ''}
  `;
  return art;
}

function applyExportStyling(root) {
  root.querySelectorAll('.interactive-slot, .status-badges').forEach(n => n.remove());
}

export function escapeHTML(str) { return String(str).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
export function escapeMulti(str) { return escapeHTML(str).replace(/\n/g, '<br>'); }

// Basic CSS (optional injection if not already present)
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
  /* Kategorie-spezifische Varianten */
  .badge.category.terminology { background:#9333EA; color:#fff; }
  .badge.category.style { background:#10B981; color:#fff; }
  .badge.category.consistency { background:#0EA5E9; color:#fff; }
  .badge.category.semantic { background:#7C3AED; color:#fff; }
  .badge.category.completeness { background:#4338CA; color:#fff; }
  .badge.category.numbers { background:#0369A1; color:#fff; }
  table.cmp-table { width:100%; border-collapse:collapse; font-size:.75rem; }
  .cmp-table th, .cmp-table td { border:1px solid var(--c-border); padding:6px 8px; vertical-align:top; }
  .recommendation { font-size:.72rem; margin:10px 0 0; padding:8px 10px; border-left:4px solid #1F4E79; background:#f0f6fb; border-radius:4px; }
  .recommendation .rec-label { font-weight:600; margin-right:4px; }
  .notes, .comments { list-style:disc; margin:8px 0 0 18px; padding:0; font-size:.65rem; color:var(--c-muted); }
  .notes li, .comments li { margin:0 0 2px; }
  .notes em, .comments em { font-style:normal; color:var(--c-text); }
  .report-aspects-summary { font-size:.7rem; font-weight:600; margin:0 0 14px; padding:6px 10px; background:#f1f5f9; border:1px solid var(--c-border); border-radius:6px; }
  @media print { body { color:#000; } .issue { box-shadow:none; } }
  `;
  document.head.appendChild(style);
}

// Aspekt-Zusammenfassung für Export
function summarizeAspects(issues = []) {
  const r = { names:0, numbers:0, completeness:0, spelling:0 };
  for (const i of issues) {
    const code = i.code || '';
    const cat = (i.category || '').toLowerCase();
    if (cat === 'terminology' || code === 'TERM_PREFERRED_MISSING' || code === 'PROPER_NAME_MISSING') r.names++;
    if (code.startsWith('NUMBER') || code === 'UNIT_DRIFT') r.numbers++;
    if (code.includes('MISSING') || code === 'SEMANTIC_LOW' || code === 'COVERAGE_RATIO_LOW' || /^PLACEHOLDER_|^URL_|^EMAIL_|^HTML_/.test(code)) r.completeness++;
    if (cat === 'style' && (code.startsWith('grammar') || code === 'hunspell.spelling' || code.startsWith('heuristic.'))) r.spelling++;
  }
  return r;
}
