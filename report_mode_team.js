// report_mode_team.js
// Team-Layer für Unified Report (mode=team)

export default function initTeam({ container, state }) {
  ensureTeamStyles();
  mountControls(container, state);

  // Badges & Counter live halten
  state.subscribe(() => {
    updateBadges(container, state);
    applyFilters(container, state);
  });
  updateBadges(container, state);
  applyFilters(container, state);
}

// ------- öffentliche (named) Exporte für Fallback-Aufruf -------
export function mountControls(root, state) {
  injectToolbar(root, state);
  root.querySelectorAll('[data-interactive]').forEach((slot) => {
    const host = slot.closest('.issue');
    if (!host) return;
    const id = host.dataset.id;
    slot.appendChild(buildButtonBar(id, state));
    slot.appendChild(buildNotesSection(id, state));
  });
}

export function updateBadges(root, state) {
  state.data.issues.forEach((issue) => {
    const el = root.querySelector(
      `.issue[data-id="${cssEsc(issue.id)}"] [data-status-badges]`
    );
    if (!el) return;
    const cur = state.map.get(issue.id);
    const parts = [];
    if (cur?.status.marked) parts.push('<span class="sb sb-marked">Markiert</span>');
    if (cur?.status.resolved) parts.push('<span class="sb sb-resolved">Erledigt</span>');
    el.innerHTML = parts.join('');
    const host = root.querySelector(`.issue[data-id="${cssEsc(issue.id)}"]`);
    host?.querySelector('[data-act="mark"]')?.setAttribute('aria-pressed', !!cur?.status.marked);
    host?.querySelector('[data-act="resolve"]')?.setAttribute('aria-pressed', !!cur?.status.resolved);
  });
}

// ------------------- UI / Interaktionen -------------------
function injectToolbar(root, state) {
  const toolbar = document.createElement('div');
  toolbar.className = 'team-toolbar';
  toolbar.innerHTML = `
    <div class="filter-row">
      <input type="search" placeholder="Suche..." class="team-search" aria-label="Suchen" />
      <div class="pickers"></div>
      <span class="count" data-count></span>
      <div class="spacer"></div>
      <button data-action="clear">Filter zurücksetzen</button>
      <button data-action="export-json">JSON</button>
      <button data-action="export-csv">CSV</button>
      <button data-action="clear-interactive">Interaktion leeren</button>
    </div>`;
  root.prepend(toolbar);

  // dynamische Filter aus Daten
  const picks = toolbar.querySelector('.pickers');
  const prios = unique(state.data.issues.map((i) => i.priority)).sort(orderPriority);
  const cats = unique(state.data.issues.map((i) => i.category)).sort((a, b) => a.localeCompare(b, 'de'));
  picks.appendChild(buildSelect('Priorität', 'priority', ['alle', ...prios]));
  picks.appendChild(buildSelect('Kategorie', 'category', ['alle', ...cats]));

  toolbar.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;
    const a = btn.getAttribute('data-action');
    if (a === 'clear') {
      toolbar.querySelector('.team-search').value = '';
      toolbar.querySelector('select[data-filter="priority"]').value = 'alle';
      toolbar.querySelector('select[data-filter="category"]').value = 'alle';
      applyFilters(root, state);
    }
    if (a === 'export-json') {
      download(JSON.stringify(state.exportData(), null, 2), 'report_team.json', 'application/json');
    }
    if (a === 'export-csv') {
      exportCSV(state);
    }
    if (a === 'clear-interactive') {
      state.clearInteractive();
    }
  });

  toolbar.querySelector('.team-search')
    .addEventListener('input', () => applyFilters(root, state));
  toolbar.querySelectorAll('select[data-filter]')
    .forEach((sel) => sel.addEventListener('change', () => applyFilters(root, state)));

  ensureTeamStyles();
}

function buildButtonBar(id, state) {
  const wrap = document.createElement('div');
  wrap.className = 'actions';
  wrap.innerHTML = `
    <button data-act="mark" aria-pressed="false">Markieren</button>
    <button data-act="resolve" aria-pressed="false">Erledigt</button>
    <button data-act="add-note">Notiz</button>
    <button data-act="add-comment">Kommentar</button>`;
  wrap.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-act]');
    if (!btn) return;
    const act = btn.getAttribute('data-act');
    if (act === 'mark') state.toggle(id, 'marked');
    else if (act === 'resolve') state.toggle(id, 'resolved');
    else if (act === 'add-note') promptAdd(id, 'note', state);
    else if (act === 'add-comment') promptAdd(id, 'comment', state);
  });
  return wrap;
}

function promptAdd(id, type, state) {
  const text = prompt(type === 'note' ? 'Notiz eingeben' : 'Kommentar eingeben');
  if (!text) return;
  if (type === 'note') state.addNote(id, text, 'Sie');
  else state.addComment(id, text, 'Sie');
}

function buildNotesSection(id, state) {
  const sec = document.createElement('div');
  sec.className = 'notes';
  sec.dataset.id = id;
  renderEntries(id, state, sec);
  state.subscribe(() => renderEntries(id, state, sec));
  return sec;
}

function renderEntries(id, state, root) {
  const issue = state.map.get(id);
  if (!issue) return;
  const frag = document.createDocumentFragment();
  const combined = [
    ...issue.notes.map((n) => ({ ...n, _t: 'note' })),
    ...issue.comments.map((c) => ({ ...c, _t: 'comment' })),
  ].sort((a, b) => a.id - b.id);
  combined.forEach((entry) => {
    const div = document.createElement('div');
    div.className = 'entry entry-' + entry._t;
    div.innerHTML = `
      <div class="entry-head">
        <span>${entry._t === 'note' ? 'Notiz' : 'Kommentar'}</span>
        <time>${formatTime(entry.time)}</time>
        <button data-del="${entry.id}" aria-label="Löschen">×</button>
      </div>
      <div class="entry-text"></div>`;
    div.querySelector('.entry-text').textContent = entry.text;
    div.querySelector('[data-del]').addEventListener('click', () => {
      entry._t === 'note' ? state.deleteNote(id, entry.id) : state.deleteComment(id, entry.id);
    });
    frag.appendChild(div);
  });
  root.replaceChildren(frag);
}

// ------------------- Suche + Filter + Counter -------------------
function applyFilters(root, state) {
  const toolbar = root.querySelector('.team-toolbar');
  if (!toolbar) return;
  const term = (toolbar.querySelector('.team-search')?.value || '').trim().toLowerCase();
  const fPrio = toolbar.querySelector('select[data-filter="priority"]')?.value || 'alle';
  const fCat = toolbar.querySelector('select[data-filter="category"]')?.value || 'alle';

  let visible = 0;
  state.data.issues.forEach((i) => {
    const node = root.querySelector(`.issue[data-id="${cssEsc(i.id)}"]`);
    if (!node) return;

    const hay = (
      (i.description || '') + ' ' +
      (i.category || '') + ' ' +
      (i.location || '') + ' ' +
      (i.recommendation || '') + ' ' +
      (i.sourceText || '') + ' ' +
      (i.currentText || '') + ' ' +
      (i.suggestedText || '')
    ).toLowerCase();

    const matchTerm = !term || hay.includes(term);
    const matchPrio = fPrio === 'alle' || i.priority === fPrio;
    const matchCat = fCat === 'alle' || i.category === fCat;

    const show = matchTerm && matchPrio && matchCat;
    node.style.display = show ? '' : 'none';
    if (show) visible += 1;
  });

  const countEl = toolbar.querySelector('[data-count]');
  if (countEl) countEl.textContent = `${visible} / ${state.data.issues.length} sichtbar`;
}

// ------------------- Exporte -------------------
function exportCSV(state) {
  const rows = [['id','priority','category','location','description','marked','resolved','notes','comments']];
  state.exportData().forEach((i) =>
    rows.push([
      i.id, i.priority, i.category, i.location || '',
      esc(i.description), !!i.status.marked, !!i.status.resolved,
      (i.notes || []).length, (i.comments || []).length,
    ])
  );
  const csv = rows.map((r) => r.map(String).join(';')).join('\n');
  download(csv, 'report_team.csv', 'text/csv');
}

// ------------------- Helfer -------------------
function esc(v) {
  return '"' + String(v).replace(/"/g, '""') + '"';
}
function download(content, name, type) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([content], { type }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 500);
}
function formatTime(iso) {
  try {
    return new Intl.DateTimeFormat('de-DE', { dateStyle: 'short', timeStyle: 'short' })
      .format(new Date(iso));
  } catch { return iso; }
}
function unique(arr) { return [...new Set(arr.filter(Boolean))]; }
function orderPriority(a, b) {
  const order = ['kritisch', 'hoch', 'mittel', 'hinweis'];
  return order.indexOf(a) - order.indexOf(b);
}
function buildSelect(label, key, options) {
  const wrap = document.createElement('label');
  wrap.className = 'picker';
  const sel = document.createElement('select');
  sel.setAttribute('data-filter', key);
  options.forEach((v) => {
    const opt = document.createElement('option');
    opt.value = v;
    opt.textContent = v[0].toUpperCase() + v.slice(1);
    sel.appendChild(opt);
  });
  wrap.append(document.createTextNode(label + ': '), sel);
  return wrap;
}
// CSS.escape Fallback
function cssEsc(val) {
  try { return CSS.escape(val); } catch { return String(val).replace(/"/g, '\\"'); }
}

// ------------------- Styles -------------------
function ensureTeamStyles() {
  if (document.getElementById('report-team-styles')) return;
  const s = document.createElement('style');
  s.id = 'report-team-styles';
  s.textContent = `
  .team-toolbar { position:sticky; top:0; background:#fff; padding:10px 0 14px; display:flex; flex-direction:column; gap:8px; z-index:50; }
  .filter-row { display:flex; flex-wrap:wrap; gap:8px; align-items:center; }
  .team-toolbar .team-search { padding:6px 8px; border:1px solid #cbd5e1; border-radius:6px; min-width:220px; }
  .team-toolbar select { padding:6px 8px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; }
  .team-toolbar .picker { font-size:.8rem; color:#0f172a; display:flex; gap:6px; align-items:center; }
  .team-toolbar .count { font-size:.8rem; color:#475569; margin-left:6px; }
  .team-toolbar .spacer { flex:1 1 auto; }
  .team-toolbar button { background:#1F4E79; color:#fff; border:none; padding:6px 10px; border-radius:4px; cursor:pointer; font-size:.75rem; }
  .team-toolbar button:hover { background:#16374f; }
  .actions { display:flex; gap:6px; flex-wrap:wrap; margin:8px 0 6px; }
  .actions button { background:#f1f5f9; border:1px solid #cbd5e1; padding:4px 8px; border-radius:4px; font-size:.65rem; cursor:pointer; }
  .actions button[aria-pressed="true"] { background:#1F4E79; color:#fff; }
  .notes { border-top:1px dashed #e2e8f0; margin-top:6px; padding-top:6px; display:flex; flex-direction:column; gap:4px; }
  .entry { background:#f8fafc; border:1px solid #e2e8f0; padding:6px 8px; border-radius:4px; font-size:.65rem; }
  .entry-head { display:flex; gap:8px; align-items:center; font-weight:600; }
  .entry-head time { font-weight:400; color:#475569; }
  .entry-head button { margin-left:auto; background:#fff; border:1px solid #cbd5e1; border-radius:4px; cursor:pointer; padding:2px 6px; }
  .sb { display:inline-block; padding:2px 6px; font-size:.6rem; border-radius:4px; font-weight:600; background:#e2e8f0; margin-right:4px; }
  .sb-marked { background:#2563EB; color:#fff; }
  .sb-resolved { background:#16A34A; color:#fff; }
  `;
  document.head.appendChild(s);
}

// Team Mode Enhancer – report_team.js (mit Filtern & Counter)
import {
  createStateManager,
  renderReport,
  ensureBaseStyles,
  normalizeData,
} from './report_core_base.js';

export async function bootTeam({ source }) {
  ensureBaseStyles();
  const raw = await (await fetch(source, { cache: 'no-store' })).json();
  const norm = normalizeData(raw);
  const state = createStateManager(norm, { persist: true });
  const container = document.getElementById('app');

  renderReport({ container, data: norm, mode: 'team' });
  mountControls(container, state);

  state.subscribe(() => {
    updateBadges(container, state);
    applyFilters(container, state); // Counter aktuell halten
  });
  updateBadges(container, state);
  applyFilters(container, state);
}

function mountControls(root, state){
  injectToolbar(root, state);
  root.querySelectorAll('[data-interactive]').forEach(slot => {
    const host = slot.closest('.issue');
    if (!host) return;
    const id = host.dataset.id;
    slot.appendChild(buildButtonBar(id, state));
    slot.appendChild(buildNotesSection(id, state));
  });
}

function injectToolbar(root, state){
  const toolbar = document.createElement('div');
  toolbar.className='team-toolbar';
  toolbar.innerHTML = `
    <div class="filter-row">
      <input type="search" placeholder="Suche..." class="team-search" aria-label="Suchen" />
      <div class="pickers"></div>
      <span class="count" data-count></span>
      <div class="spacer"></div>
      <button data-action="clear">Filter zurücksetzen</button>
      <button data-action="export-json">JSON</button>
      <button data-action="export-csv">CSV</button>
      <button data-action="clear-interactive">Interaktion leeren</button>
    </div>`;
  root.prepend(toolbar);

  // --- Dynamische Filter (aus Daten gebaut)
  const picks = toolbar.querySelector('.pickers');
  const prios = unique(state.data.issues.map(i => i.priority)).sort(orderPriority);
  const cats  = unique(state.data.issues.map(i => i.category)).sort((a,b)=>a.localeCompare(b,'de'));

  picks.appendChild(buildSelect('Priorität', 'priority', ['alle', ...prios]));
  picks.appendChild(buildSelect('Kategorie', 'category', ['alle', ...cats]));

  toolbar.addEventListener('click', e=>{
    const btn = e.target.closest('[data-action]');
    if(!btn) return;
    const a = btn.getAttribute('data-action');
    if(a==='clear'){
      toolbar.querySelector('.team-search').value='';
      toolbar.querySelector('select[data-filter="priority"]').value='alle';
      toolbar.querySelector('select[data-filter="category"]').value='alle';
      applyFilters(root, state);
    }
    if(a==='export-json'){ download(JSON.stringify(state.exportData(),null,2),'report_team.json','application/json'); }
    if(a==='export-csv'){ exportCSV(state); }
    if(a==='clear-interactive'){ state.clearInteractive(); }
  });

  toolbar.querySelector('.team-search')
    .addEventListener('input', () => applyFilters(root, state));
  toolbar.querySelectorAll('select[data-filter]')
    .forEach(sel => sel.addEventListener('change', () => applyFilters(root, state)));

  ensureTeamStyles();
}

function buildButtonBar(id, state){
  const wrap = document.createElement('div');
  wrap.className='actions';
  wrap.innerHTML = `
    <button data-act="mark" aria-pressed="false">Markieren</button>
    <button data-act="resolve" aria-pressed="false">Erledigt</button>
    <button data-act="add-note">Notiz</button>
    <button data-act="add-comment">Kommentar</button>`;
  wrap.addEventListener('click', e=>{
    const btn = e.target.closest('[data-act]');
    if(!btn) return;
    const act = btn.getAttribute('data-act');
    if(act==='mark') state.toggle(id,'marked');
    else if(act==='resolve') state.toggle(id,'resolved');
    else if(act==='add-note') promptAdd(id,'note',state);
    else if(act==='add-comment') promptAdd(id,'comment',state);
  });
  return wrap;
}

function promptAdd(id,type,state){
  const text = prompt(type==='note'?'Notiz eingeben':'Kommentar eingeben');
  if(!text) return;
  if(type==='note') state.addNote(id,text,'Sie'); else state.addComment(id,text,'Sie');
}

function buildNotesSection(id,state){
  const sec = document.createElement('div');
  sec.className='notes';
  sec.dataset.id = id;
  renderEntries(id, state, sec);
  state.subscribe(()=>renderEntries(id, state, sec));
  return sec;
}

function renderEntries(id,state,root){
  const issue = state.map.get(id); if(!issue) return;
  const frag = document.createDocumentFragment();
  const combined = [
    ...issue.notes.map(n=>({...n,_t:'note'})),
    ...issue.comments.map(c=>({...c,_t:'comment'}))
  ].sort((a,b)=>a.id-b.id);
  combined.forEach(entry=>{
    const div = document.createElement('div');
    div.className = 'entry entry-'+entry._t;
    div.innerHTML = `
      <div class="entry-head">
        <span>${entry._t==='note'?'Notiz':'Kommentar'}</span>
        <time>${formatTime(entry.time)}</time>
        <button data-del="${entry.id}" aria-label="Löschen">×</button>
      </div>
      <div class="entry-text"></div>`;
    div.querySelector('.entry-text').textContent = entry.text;
    div.querySelector('[data-del]').addEventListener('click', ()=>{
      entry._t==='note' ? state.deleteNote(id, entry.id) : state.deleteComment(id, entry.id);
    });
    frag.appendChild(div);
  });
  root.replaceChildren(frag);
}

function updateBadges(root, state){
  state.data.issues.forEach(issue=>{
    const el = root.querySelector(`.issue[data-id="${CSS.escape(issue.id)}"] [data-status-badges]`);
    if(!el) return;
    const cur = state.map.get(issue.id);
    const parts = [];
    if(cur?.status.marked) parts.push('<span class="sb sb-marked">Markiert</span>');
    if(cur?.status.resolved) parts.push('<span class="sb sb-resolved">Erledigt</span>');
    el.innerHTML = parts.join('');
    const host = root.querySelector(`.issue[data-id="${CSS.escape(issue.id)}"]`);
    host?.querySelector('[data-act="mark"]')?.setAttribute('aria-pressed', !!cur?.status.marked);
    host?.querySelector('[data-act="resolve"]')?.setAttribute('aria-pressed', !!cur?.status.resolved);
  });
}

// --- Suche + Filter + Counter
function applyFilters(root, state){
  const toolbar = root.querySelector('.team-toolbar');
  if(!toolbar) return;
  const term = (toolbar.querySelector('.team-search')?.value || '').trim().toLowerCase();
  const fPrio = toolbar.querySelector('select[data-filter="priority"]')?.value || 'alle';
  const fCat  = toolbar.querySelector('select[data-filter="category"]')?.value || 'alle';

  let visible = 0;
  state.data.issues.forEach(i=>{
    const node = root.querySelector(`.issue[data-id="${CSS.escape(i.id)}"]`);
    if(!node) return;

    const hay = (
      (i.description||'') + ' ' +
      (i.category||'') + ' ' +
      (i.location||'') + ' ' +
      (i.recommendation||'') + ' ' +
      (i.sourceText||'') + ' ' +
      (i.currentText||'') + ' ' +
      (i.suggestedText||'')
    ).toLowerCase();

    const matchTerm  = !term || hay.includes(term);
    const matchPrio  = (fPrio === 'alle') || i.priority === fPrio;
    const matchCat   = (fCat  === 'alle') || i.category === fCat;

    const show = matchTerm && matchPrio && matchCat;
    node.style.display = show ? '' : 'none';
    if (show) visible += 1;
  });

  const countEl = toolbar.querySelector('[data-count]');
  if (countEl) countEl.textContent = `${visible} / ${state.data.issues.length} sichtbar`;
}

// --- Exporte
function exportCSV(state){
  const rows = [['id','priority','category','location','description','marked','resolved','notes','comments']];
  state.exportData().forEach(i => rows.push([
    i.id, i.priority, i.category, i.location||'',
    esc(i.description), !!i.status.marked, !!i.status.resolved,
    (i.notes||[]).length, (i.comments||[]).length
  ]));
  const csv = rows.map(r=>r.map(String).join(';')).join('\n');
  download(csv,'report_team.csv','text/csv');
}

// --- Helpers & Styles
function esc(v){ return '"'+String(v).replace(/"/g,'""')+'"'; }
function download(content,name,type){
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([content],{type}));
  a.download=name; a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href),500);
}
function formatTime(iso){
  try{ return new Intl.DateTimeFormat('de-DE',{dateStyle:'short', timeStyle:'short'}).format(new Date(iso)); }
  catch{return iso;}
}
function unique(arr){ return [...new Set(arr.filter(Boolean))]; }
function orderPriority(a,b){
  const order = ['kritisch','hoch','mittel','hinweis'];
  const ia = order.indexOf(a); const ib = order.indexOf(b);
  return (ia===-1?99:ia) - (ib===-1?99:ib);
}
function buildSelect(label, key, options){
  const wrap = document.createElement('label');
  wrap.className = 'picker';
  const sel = document.createElement('select');
  sel.setAttribute('data-filter', key);
  options.forEach(v=>{
    const opt = document.createElement('option');
    opt.value = v; opt.textContent = v[0].toUpperCase()+v.slice(1);
    sel.appendChild(opt);
  });
  wrap.append(document.createTextNode(label+': '), sel);
  return wrap;
}

function ensureTeamStyles(){
  if(document.getElementById('report-team-styles')) return;
  const s=document.createElement('style');
  s.id='report-team-styles';
  s.textContent=`
  .team-toolbar { position:sticky; top:0; background:#fff; padding:10px 0 14px; display:flex; flex-direction:column; gap:8px; z-index:50; }
  .filter-row { display:flex; flex-wrap:wrap; gap:8px; align-items:center; }
  .team-toolbar .team-search { padding:6px 8px; border:1px solid #cbd5e1; border-radius:6px; min-width:220px; }
  .team-toolbar select { padding:6px 8px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; }
  .team-toolbar .picker { font-size:.8rem; color:#0f172a; display:flex; gap:6px; align-items:center; }
  .team-toolbar .count { font-size:.8rem; color:#475569; margin-left:6px; }
  .team-toolbar .spacer { flex:1 1 auto; }
  .team-toolbar button { background:#1F4E79; color:#fff; border:none; padding:6px 10px; border-radius:4px; cursor:pointer; font-size:.75rem; }
  .team-toolbar button:hover { background:#16374f; }
  .actions { display:flex; gap:6px; flex-wrap:wrap; margin:8px 0 6px; }
  .actions button { background:#f1f5f9; border:1px solid #cbd5e1; padding:4px 8px; border-radius:4px; font-size:.65rem; cursor:pointer; }
  .actions button[aria-pressed="true"] { background:#1F4E79; color:#fff; }
  .notes { border-top:1px dashed #e2e8f0; margin-top:6px; padding-top:6px; display:flex; flex-direction:column; gap:4px; }
  .entry { background:#f8fafc; border:1px solid #e2e8f0; padding:6px 8px; border-radius:4px; font-size:.65rem; }
  .entry-head { display:flex; gap:8px; align-items:center; font-weight:600; }
  .entry-head time { font-weight:400; color:#475569; }
  .entry-head button { margin-left:auto; background:#fff; border:1px solid #cbd5e1; border-radius:4px; cursor:pointer; padding:2px 6px; }
  .sb { display:inline-block; padding:2px 6px; font-size:.6rem; border-radius:4px; font-weight:600; background:#e2e8f0; margin-right:4px; }
  .sb-marked { background:#2563EB; color:#fff; }
  .sb-resolved { background:#16A34A; color:#fff; }
  `;
  document.head.appendChild(s);
}

// optional Auto-Boot via <script data-autoboot="team" data-source="...">
if (document.currentScript && document.currentScript.dataset.autoboot === 'team') {
  bootTeam({ source: document.currentScript.dataset.source || 'report_data_sample.json' });
}

// Team Mode Enhancer – renamed from report_team.js
import { createStateManager, renderReport, ensureBaseStyles, normalizeData } from './report_core_base.js';

export async function bootTeam({ source }) {
  ensureBaseStyles();
  const raw = await (await fetch(source, { cache: 'no-store' })).json();
  const norm = normalizeData(raw); // zentrale Normalisierung inkl. code, status, notes, comments
  const state = createStateManager(norm, { persist: true });
  const container = document.getElementById('app');
  renderReport({ container, data: norm, mode: 'team' });
  mountControls(container, state);
  state.subscribe(() => updateBadges(container, state));
  updateBadges(container, state);
}
function mountControls(root, state){
  injectToolbar(root, state);
  root.querySelectorAll('[data-interactive]').forEach(slot => {
    const host = slot.closest('.issue');
    if(!host) return;
    const id = host.dataset.id;
    slot.appendChild(buildButtonBar(id, state));
    slot.appendChild(buildNotesSection(id, state));
  });
}
function injectToolbar(root, state){
  const toolbar = document.createElement('div');
  toolbar.className='team-toolbar';
  toolbar.innerHTML = `
    <div class="filter-row">
      <input type="search" placeholder="Suche..." class="team-search" aria-label="Suchen" />
      <button data-action="clear">Filter zurücksetzen</button>
      <button data-action="export-json">JSON</button>
      <button data-action="export-csv">CSV</button>
      <button data-action="clear-interactive">Interaktion leeren</button>
    </div>`;
  root.prepend(toolbar);
  toolbar.addEventListener('click', e=>{
    const btn = e.target.closest('[data-action]');
    if(!btn) return;
    const a = btn.getAttribute('data-action');
    if(a==='clear'){ root.querySelector('.team-search').value=''; applySearch(root,'',state); }
    if(a==='export-json'){ download(JSON.stringify(state.exportData(),null,2),'report_team.json','application/json'); }
    if(a==='export-csv'){ exportCSV(state); }
    if(a==='clear-interactive'){ state.clearInteractive(); }
  });
  toolbar.querySelector('.team-search')
    .addEventListener('input', e=>applySearch(root, e.target.value.trim().toLowerCase(), state));
  ensureTeamStyles();
}
function buildButtonBar(id, state){
  const wrap = document.createElement('div');
  wrap.className='actions';
  wrap.innerHTML = `
    <button data-act="mark" aria-pressed="false">Markieren</button>
    <button data-act="resolve" aria-pressed="false">Erledigt</button>
    <button data-act="add-note">Notiz</button>
    <button data-act="add-comment">Kommentar</button>`;
  wrap.addEventListener('click', e=>{
    const btn = e.target.closest('[data-act]');
    if(!btn) return;
    const act = btn.getAttribute('data-act');
    if(act==='mark') state.toggle(id,'marked');
    else if(act==='resolve') state.toggle(id,'resolved');
    else if(act==='add-note') promptAdd(id,'note',state);
    else if(act==='add-comment') promptAdd(id,'comment',state);
  });
  return wrap;
}
function promptAdd(id,type,state){
  const text = prompt(type==='note'?'Notiz eingeben':'Kommentar eingeben');
  if(!text) return;
  if(type==='note') state.addNote(id,text,'Sie'); else state.addComment(id,text,'Sie');
}
function buildNotesSection(id,state){
  const sec = document.createElement('div');
  sec.className='notes';
  sec.dataset.id = id;
  renderEntries(id, state, sec);
  state.subscribe(()=>renderEntries(id, state, sec));
  return sec;
}
function renderEntries(id,state,root){
  const issue = state.map.get(id); if(!issue) return;
  const frag = document.createDocumentFragment();
  const combined = [ ...issue.notes.map(n=>({...n,_t:'note'})), ...issue.comments.map(c=>({...c,_t:'comment'})) ].sort((a,b)=>a.id-b.id);
  combined.forEach(entry=>{
    const div = document.createElement('div');
    div.className = 'entry entry-'+entry._t;
    div.innerHTML = `<div class="entry-head"><span>${entry._t==='note'?'Notiz':'Kommentar'}</span><time>${formatTime(entry.time)}</time><button data-del="${entry.id}" aria-label="Löschen">×</button></div><div class="entry-text"></div>`;
    div.querySelector('.entry-text').textContent = entry.text;
    div.querySelector('[data-del]').addEventListener('click', ()=>{ entry._t==='note'? state.deleteNote(id, entry.id): state.deleteComment(id, entry.id); });
    frag.appendChild(div);
  });
  root.replaceChildren(frag);
}
function updateBadges(root, state){
  state.data.issues.forEach(issue=>{
    const selId = CSS.escape(issue.id);
    const el = root.querySelector(`.issue[data-id="${selId}"] [data-status-badges]`);
    if(!el) return;
    const cur = state.map.get(issue.id);
    const parts = [];
    if(cur?.status.marked) parts.push('<span class="sb sb-marked">Markiert</span>');
    if(cur?.status.resolved) parts.push('<span class="sb sb-resolved">Erledigt</span>');
    el.innerHTML = parts.join('');
    const host = root.querySelector(`.issue[data-id="${selId}"]`);
    host?.querySelector('[data-act="mark"]')?.setAttribute('aria-pressed', !!cur?.status.marked);
    host?.querySelector('[data-act="resolve"]')?.setAttribute('aria-pressed', !!cur?.status.resolved);
  });
}
function applySearch(root, term, state){
  state.data.issues.forEach(i=>{
    const node = root.querySelector(`.issue[data-id="${CSS.escape(i.id)}"]`);
    if(!node) return;
    const hay = (
      (i.description||'') + ' ' +
      (i.category||'') + ' ' +
      (i.location||'') + ' ' +
      (i.recommendation||'') + ' ' +
      (i.sourceText||'') + ' ' +
      (i.currentText||'') + ' ' +
      (i.suggestedText||'')
    ).toLowerCase();
    node.style.display = hay.includes(term)? '' : 'none';
  });
}
function exportCSV(state){
  const rows = [['id','priority','category','description','marked','resolved','notes','comments']];
  state.exportData().forEach(i=>rows.push([i.id,i.priority,i.category,esc(i.description),i.status.marked,i.status.resolved,i.notes.length,i.comments.length]));
  const csv = rows.map(r=>r.join(';')).join('\n');
  download(csv,'report_team.csv','text/csv');
}
function esc(v){ return '"'+String(v).replace(/"/g,'""')+'"'; }
function download(content,name,type){ const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([content],{type})); a.download=name; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href),500); }
function formatTime(iso){ try{ return new Intl.DateTimeFormat('de-DE',{dateStyle:'short', timeStyle:'short'}).format(new Date(iso)); }catch{return iso;} }
function ensureTeamStyles(){
  if(document.getElementById('report-team-styles')) return;
  const s=document.createElement('style');
  s.id='report-team-styles';
  s.textContent=`
  .team-toolbar { position:sticky; top:0; background:#fff; padding:10px 0 14px; display:flex; flex-direction:column; gap:8px; z-index:50; }
  .team-toolbar input { padding:6px 8px; border:1px solid #cbd5e1; border-radius:6px; }
  .team-toolbar button { background:#1F4E79; color:#fff; border:none; padding:6px 10px; border-radius:4px; cursor:pointer; font-size:.75rem; }
  .team-toolbar button:hover { background:#16374f; }
  .actions { display:flex; gap:6px; flex-wrap:wrap; margin:8px 0 6px; }
  .actions button { background:#f1f5f9; border:1px solid #cbd5e1; padding:4px 8px; border-radius:4px; font-size:.65rem; cursor:pointer; }
  .actions button[aria-pressed="true"] { background:#1F4E79; color:#fff; }
  .notes { border-top:1px dashed #e2e8f0; margin-top:6px; padding-top:6px; display:flex; flex-direction:column; gap:4px; }
  .entry { background:#f8fafc; border:1px solid #e2e8f0; padding:6px 8px; border-radius:4px; font-size:.65rem; }
  .entry-head { display:flex; gap:8px; align-items:center; font-weight:600; }
  .entry-head time { font-weight:400; color:#475569; }
  .entry-head button { margin-left:auto; background:#fff; border:1px solid #cbd5e1; border-radius:4px; cursor:pointer; padding:2px 6px; }
  .sb { display:inline-block; padding:2px 6px; font-size:.6rem; border-radius:4px; font-weight:600; background:#e2e8f0; margin-right:4px; }
  .sb-marked { background:#2563EB; color:#fff; }
  .sb-resolved { background:#16A34A; color:#fff; }
  `;
  document.head.appendChild(s);
}
// optional Auto-Boot via <script data-autoboot="team" data-source="...">
if (document.currentScript && document.currentScript.dataset.autoboot === 'team') {
  bootTeam({ source: document.currentScript.dataset.source || 'report_data_sample.json' });
}
