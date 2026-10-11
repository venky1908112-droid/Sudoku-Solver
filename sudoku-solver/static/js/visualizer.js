const $ = id => document.getElementById(id);
const blank = () => Array.from({length: 9}, () => Array(9).fill('.'));
const copy = b => b.map(r => r.slice());
let values = blank(), origin = Array(81).fill(''); // origin: 'clue' | 'user' | ''
let initial = null, events = [], pos = 0, mode = 'edit', timer = null, stats = null;
const cells = [], wraps = [];

// ---- build grid ----
for (let i = 0; i < 81; i++) {
  const wrap = document.createElement('div'); wrap.className = 'cell';
  const inp = document.createElement('input');
  inp.maxLength = 1; inp.inputMode = 'numeric'; inp.setAttribute('aria-label', `Row ${Math.floor(i / 9) + 1}, column ${i % 9 + 1}`);
  const mark = document.createElement('span'); mark.className = 'mark';
  inp.addEventListener('keydown', e => onKey(e, i));
  inp.addEventListener('input', () => { inp.value = ''; }); // real edits happen in keydown
  wrap.append(inp, mark); $('grid').append(wrap); cells.push(inp); wraps.push(wrap);
}
function onKey(e, i) {
  const r = Math.floor(i / 9), c = i % 9, arrows = {ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1]};
  if (arrows[e.key]) {
    const [dr, dc] = arrows[e.key], nr = Math.min(8, Math.max(0, r + dr)), nc = Math.min(8, Math.max(0, c + dc));
    cells[nr * 9 + nc].focus(); e.preventDefault(); return;
  }
  if (e.ctrlKey || e.metaKey || e.key === 'Tab') return;
  e.preventDefault();
  if (mode !== 'edit') return;
  if (/^[1-9]$/.test(e.key)) { values[r][c] = e.key; origin[i] = 'user'; }
  else if (['Backspace', 'Delete', '0', ' '].includes(e.key)) { values[r][c] = '.'; origin[i] = ''; }
  else return;
  render();
}

// ---- rendering ----
function render() {
  const last = pos > 0 ? events[pos - 1] : null;
  const done = mode === 'viz' && last && last.type === 'solved';
  for (let i = 0; i < 81; i++) {
    const r = Math.floor(i / 9), c = i % 9, v = values[r][c];
    const kind = origin[i] || (v !== '.' ? 'algo' : '');
    let cls = 'cell ' + kind, mark = '';
    if (last && last.row === r && last.col === c) {
      cls += ' active ' + last.type; mark = last.type === 'place' ? '▲' : '✕';
    }
    if (done && kind === 'algo') { cls += ' solved'; mark = '✓'; }
    wraps[i].className = cls; wraps[i].lastChild.textContent = mark;
    cells[i].value = v === '.' ? '' : v; cells[i].readOnly = mode !== 'edit';
  }
  $('progress').max = Math.max(1, events.length); $('progress').value = pos;
  $('progressText').textContent = `Event ${pos} / ${events.length}`;
  $('action').textContent = mode === 'viz' ? describe(last) : 'No visualization loaded.';
  updateControls();
}
function describe(e) {
  if (!e) return 'Initial puzzle. Press Play or Step Forward.';
  const cell = `row ${e.row + 1}, column ${e.col + 1}`;
  if (e.type === 'place') return `Depth ${e.depth}: try ${e.digit} in ${cell}. It does not conflict with its row, column or box.`;
  if (e.type === 'backtrack') return `Depth ${e.depth}: every continuation after ${e.digit} in ${cell} failed, so remove it and try the next candidate.`;
  if (e.type === 'solved') return 'All empty cells are filled: puzzle solved. Search stops.';
  return 'Every candidate was tried: this puzzle has no solution.';
}
function setStatus(msg) { $('status').textContent = msg; }
function showStats(s, note) {
  const items = [['Recursive calls', s.recursive_calls], ['Placements attempted', s.placements_attempted],
    ['Successful placements', s.successful_placements], ['Backtracks', s.backtracks], ['Initially empty cells', s.empty_cells],
    ['Recorded events', s.events], ['Solving time (ms)', s.time_ms]];
  $('stats').innerHTML = items.map(([k, v]) => `<div class="stat"><b>${v}</b><span>${k}</span></div>`).join('') +
    `<p style="grid-column:1/-1;color:var(--mut)">${note}</p>`;
}

// ---- controls state ----
function updateControls() {
  const viz = mode === 'viz', edit = mode === 'edit', playing = timer !== null;
  $('btnValidate').disabled = !edit; $('btnSolve').disabled = !edit; $('btnViz').disabled = !edit;
  $('btnEdit').disabled = edit; $('btnPlay').disabled = !(viz && !playing && pos < events.length);
  $('btnPause').disabled = !playing; $('btnFwd').disabled = !(viz && pos < events.length);
  $('btnBack').disabled = !(viz && pos > 0); $('btnReset').disabled = !(viz && pos > 0);
}

// ---- replay engine: apply / reverse exactly one event ----
function step(dir) {
  if (dir > 0) {
    if (pos >= events.length) return false;
    const e = events[pos];
    if (e.type === 'place') values[e.row][e.col] = e.digit;
    else if (e.type === 'backtrack') values[e.row][e.col] = '.';
    pos++;
  } else {
    if (pos <= 0) return false;
    pos--; const e = events[pos];
    if (e.type === 'place') values[e.row][e.col] = '.';
    else if (e.type === 'backtrack') values[e.row][e.col] = e.digit; // restore removed digit
  }
  render(); return true;
}
const delay = () => Math.round(1000 * Math.pow(1 - $('speed').value / 100, 2)) + 5;
function pause() { clearTimeout(timer); timer = null; updateControls(); }
function tick() {
  if (!step(1)) { timer = null; updateControls(); return; }
  timer = setTimeout(tick, delay());
}
function play() { if (timer === null && pos < events.length) { timer = setTimeout(tick, 0); updateControls(); } }

// ---- API helpers ----
async function api(path, body) {
  const res = await fetch(path, body ? {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)} : undefined);
  return {ok: res.ok, status: res.status, data: await res.json()};
}
const msgs = d => (d.errors || ['Unknown error']).join(' ');
function exitViz() { pause(); mode = 'edit'; events = []; pos = 0; }

$('btnExample').onclick = async () => {
  exitViz(); const {data} = await api('/api/example');
  values = copy(data.board); origin = values.flat().map(v => v === '.' ? '' : 'clue');
  render(); showStats({recursive_calls: 0, placements_attempted: 0, successful_placements: 0, backtracks: 0, empty_cells: values.flat().filter(v => v === '.').length, events: 0, time_ms: 0}, 'Run the solver to see measurements.');
  setStatus('Example loaded.');
};
$('btnClear').onclick = () => { exitViz(); values = blank(); origin = Array(81).fill(''); $('stats').innerHTML = ''; render(); setStatus('Board cleared.'); };
$('btnValidate').onclick = async () => {
  const {data} = await api('/api/validate', {board: values});
  setStatus(data.valid ? 'Puzzle is valid (shape, characters and no duplicates).' : 'Invalid puzzle: ' + msgs(data));
};
$('btnSolve').onclick = async () => {
  const {data} = await api('/api/solve', {board: values});
  if (!data.valid) return setStatus('Invalid puzzle: ' + msgs(data));
  showStats(data.stats, 'Solving time is the Python solver run only; it excludes network and animation time.');
  if (!data.solvable) return setStatus('This puzzle is valid but has no solution. Your board was left unchanged.');
  values = data.board; render(); setStatus('Solved. Solver-filled cells are shown in a different color.');
};
$('btnViz').onclick = async () => {
  const {data} = await api('/api/visualize', {board: values});
  if (!data.valid) return setStatus('Invalid puzzle: ' + msgs(data));
  if (data.errors) return setStatus(msgs(data));
  initial = copy(values); events = data.events; pos = 0; mode = 'viz';
  showStats(data.stats, 'Statistics come from the solver run; playback speed does not affect them.');
  render(); setStatus(data.solvable ? `Recorded ${events.length} real solver events. Replaying in your browser.` : 'Valid puzzle with no solution: replay shows the whole failed search, ending in "unsolvable".');
};
$('btnEdit').onclick = () => { exitViz(); values = initial ? copy(initial) : values; render(); setStatus('Editing.'); };
$('btnPlay').onclick = play; $('btnPause').onclick = pause;
$('btnFwd').onclick = () => { pause(); step(1); }; $('btnBack').onclick = () => { pause(); step(-1); };
$('btnReset').onclick = () => { pause(); values = copy(initial); pos = 0; render(); setStatus('Visualization reset to the initial puzzle.'); };
render();
