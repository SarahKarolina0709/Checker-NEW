// Team Mode Enhancer – fügt Interaktion hinzu ohne Basis-Renderer zu duplizieren
import { createStateManager, renderReport, ensureBaseStyles, normalizeData } from './report_core.js';

export async function bootTeam({ source }) {
  ensureBaseStyles();
  const res = await fetch(source, { cache: 'no-store' });
  if (!res.ok) throw new Error('Report laden fehlgeschlagen: ' + res.status);
  const raw = await res.json();
  const norm = normalizeData(raw); // Einheitliches Schema (inkl. reportId, Defaults)
  const state = createStateManager(norm, { persist: true });
  const container = document.getElementById('app');
  renderReport({ container, data: norm, mode: 'team' });
  mountControls(container, state);
  state.subscribe(() => updateBadges(container, state));
  updateBadges(container, state);
}

// Lokale normalize()-Funktion entfällt – normalizeData aus report_core.js stellt Konsistenz sicher

function mountControls(root, state){
  injectToolbar(root, state);
  root.querySelectorAll('[data-interactive]').forEach(slot => {
    const id = slot.closest('.issue').dataset.id;
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
    const a = e.target.getAttribute('data-action');
    if(!a) return;
    if(a==='clear'){ root.querySelector('.team-search').value=''; applySearch(root,'',state); }
    if(a==='export-json'){ download(JSON.stringify(state.exportData(),null,2),'report_team.json','application/json'); }
    if(a==='export-csv'){ exportCSV(state); }
    if(a==='clear-interactive'){ state.clearInteractive(); }
  });
  toolbar.querySelector('.team-search').addEventListener('input', e=>applySearch(root, e.target.value.trim().toLowerCase(), state));
  ensureTeamStyles();
}

function buildButtonBar(id, state){
  const wrap = document.createElement('div');
  wrap.className='actions';
  wrap.innerHTML = `
    <button type="button" data-act="mark" aria-pressed="false">Markieren</button>
    <button type="button" data-act="resolve" aria-pressed="false">Erledigt</button>
    <button type="button" data-act="add-note">Notiz</button>
    <button type="button" data-act="add-comment">Kommentar</button>`;
  wrap.addEventListener('click', e=>{
    const act = e.target.getAttribute('data-act');
    if(!act) return;
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
    const el = root.querySelector(`.issue[data-id="${issue.id}"] [data-status-badges]`);
    if(!el) return;
    const cur = state.map.get(issue.id);
    const parts = [];
    if(cur.status.marked) parts.push('<span class="sb sb-marked">Markiert</span>');
    if(cur.status.resolved) parts.push('<span class="sb sb-resolved">Erledigt</span>');
    el.innerHTML = parts.join('');
    const markBtn = root.querySelector(`.issue[data-id="${issue.id}"] [data-act="mark"]`);
    const resBtn = root.querySelector(`.issue[data-id="${issue.id}"] [data-act="resolve"]`);
    if(markBtn) markBtn.setAttribute('aria-pressed', cur.status.marked);
    if(resBtn) resBtn.setAttribute('aria-pressed', cur.status.resolved);
  });
}

function applySearch(root, term, state){
  state.data.issues.forEach(i=>{
    const node = root.querySelector(`.issue[data-id="${i.id}"]`);
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
  const rows = [['id','priority','category','location','description','marked','resolved','notes','comments']];
  state.exportData().forEach(i=>rows.push([
    i.id,
    i.priority,
    i.category,
    i.location,
    i.description,
    i.status.marked,
    i.status.resolved,
    i.notes.length,
    i.comments.length
  ].map(esc)));
  const csv = rows.map(r=>r.join(';')).join('\n');
  download(csv,'report_team.csv','text/csv');
}

function esc(v){ return '"' + String(v ?? '').replace(/"/g,'""') + '"'; }
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

// Auto-Boot falls direkt eingebunden
if (document.currentScript && document.currentScript.dataset.autoboot === 'team') {
  bootTeam({ source: document.currentScript.dataset.source || 'report_sample.json' });
}

// --- Unified Report Integration Exports ---
// Stelle mountControls & updateBadges als named exports bereit, damit der Unified Report
// fallback-fähig bleibt und ohne zweiten Fetch arbeiten kann.
export { mountControls, updateBadges };

// Default Adapter: Erwartet, dass der Unified Report bereits gerendert hat und
// einen State (createStateManager) übergibt.
export default function ({ container, state }) {
  if (!container || !state) return;
  mountControls(container, state);
  state.subscribe(() => updateBadges(container, state));
  updateBadges(container, state);
}
