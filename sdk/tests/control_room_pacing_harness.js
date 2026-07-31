// Behavioural harness for the control room's paced reveal queue.
//
// WHY THIS EXISTS. Katie's rule is "KPIs must read live DURING runs, in
// lockstep with the paced narration", and the complaint that produced this
// file was that the Agents and Workers numerals ran ahead of the operations
// on screen. `agent.started`, `worker.provisioned` and `worker.released` used
// to mutate the KPI row the instant they arrived off the SSE stream, while
// everything the viewer actually watches (narration, geometry, fields, plots,
// traces, tables, dispatch) went through `enqueue(...)`.
//
// Asserting that from Python by reading the HTML would only prove the source
// says "enqueue". This runs the real page script on a stub DOM with a virtual
// clock, so it proves the BEHAVIOUR: the numeral does not move until the beat
// that earned it is revealed, and the resting values are still right after
// the queue drains.
//
// SECOND COMPLAINT (2026-07-31). Katie kept seeing "4/4 Cycle, 4 Agents,
// 4 Workers" land only at the very end, on every act, and on the Monte Carlo
// race in particular: "the workers should appear as soon as either reduced or
// mc start". The synthetic tests below all passed, because they feed the
// counter events the page was taught to pace. Real missions never emit those
// events at all: the counts arrive on `roster.update`, which rides the same
// paced queue behind every narration beat and therefore surfaced minutes late.
// The replay mode added here settles that by argument-free measurement: it
// pushes a RECORDED mission stream through `dispatch` at its real inter-event
// timing on the virtual clock, samples the KPI row after every beat, and
// reports how many counter updates land while the events are still arriving
// versus how many land at or after the last event.
//
// Usage:
//   node control_room_pacing_harness.js <control_room.html>
//   node control_room_pacing_harness.js <control_room.html> --replay <a.jsonl> ...
'use strict';
const fs = require('fs');
const path = require('path');

const argv = process.argv.slice(2);
const htmlPath = argv[0];
if (!htmlPath) { console.error('FAIL: usage: harness <control_room.html> [--replay f.jsonl]'); process.exit(1); }
const html = fs.readFileSync(htmlPath, 'utf8');
const replayFiles = [];
for (let i = 1; i < argv.length; i++) {
  if (argv[i] === '--replay') replayFiles.push(argv[++i]);
}

// ---- extract the page script -------------------------------------------
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (!scripts.length) { console.error('FAIL: no <script> block found'); process.exit(1); }
const source = scripts.join('\n');

// ---- a fresh page instance ----------------------------------------------
// Every element is a bag of properties that records what was written to it.
// Nothing is rendered; the only thing under test is which values land when.
// Each call evaluates the real page script against its own stub DOM and its
// own virtual clock, so replays cannot leak state into one another.
function newPage() {
  function makeEl(id) {
    const el = {
      id, textContent: '', innerHTML: '', hidden: false, value: '',
      className: '', dataset: {}, style: {}, scrollTop: 0, scrollHeight: 0,
      classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
      appendChild() {}, removeChild() {}, insertAdjacentHTML() {},
      addEventListener() {}, removeEventListener() {}, remove() {},
      querySelector() { return makeEl('q'); },
      querySelectorAll() { return []; },
      // A canvas context that answers every call with one permissive object,
      // so gradients (`.addColorStop`), text metrics (`.width`) and image data
      // never come back undefined. A throw inside a paint routine would break
      // the setTimeout chain that IS the reveal queue, and the run would look
      // like it stalled when only the stub was thin.
      getContext() {
        const any = {
          addColorStop() {}, width: 100, height: 20,
          actualBoundingBoxAscent: 8, actualBoundingBoxDescent: 2,
          data: [0, 0, 0, 0],
        };
        return new Proxy({ canvas: el, ...any }, {
          get(t, k) { return k in t ? t[k] : () => any; },
          set(t, k, v) { t[k] = v; return true; },
        });
      },
      getBoundingClientRect() { return { width: 800, height: 400, left: 0, top: 0 }; },
      setAttribute() {}, getAttribute() { return null; }, removeAttribute() {},
      hasAttribute() { return false; },
      closest() { return null; }, focus() {}, click() {}, blur() {},
      insertBefore() {}, replaceChildren() {}, scrollIntoView() {},
      getElementsByClassName() { return []; }, getElementsByTagName() { return []; },
      children: [], firstChild: null, lastChild: null, parentNode: null,
      childNodes: [], offsetWidth: 800, offsetHeight: 400,
      clientWidth: 800, clientHeight: 400, width: 800, height: 400,
      checked: false, disabled: false, files: [], selectedIndex: 0,
      toDataURL() { return 'data:,'; },
    };
    return el;
  }
  const els = new Map();
  const byId = id => {
    if (!els.has(id)) els.set(id, makeEl(id));
    return els.get(id);
  };

  const document = {
    getElementById: byId,
    createElement: tag => makeEl('new-' + tag),
    querySelector: () => makeEl('sel'),
    querySelectorAll: () => [],
    addEventListener() {},
    body: makeEl('body'),
  };

  // ---- virtual clock -----------------------------------------------------
  // setTimeout callbacks queue by due time; the steppers run everything due so
  // the test can walk the reveal queue one beat at a time and read the KPI row
  // between beats. That mid-flight read is the whole point. `onBeat` fires
  // after every callback, which is where replay samples the numerals.
  const clock = { now: 0, seq: 0, timers: [], onBeat: null };
  const setTimeout_ = (fn, ms) => {
    const t = { at: clock.now + (ms || 0), fn, seq: clock.seq++ };
    clock.timers.push(t);
    return t.seq;
  };
  const clearTimeout_ = handle => { clock.timers = clock.timers.filter(t => t.seq !== handle); };
  const fire = t => {
    clock.now = t.at;
    try { t.fn(); } catch (e) { clock.errors.push(e); }
    if (clock.onBeat) clock.onBeat(clock.now);
  };
  clock.errors = [];
  function advance(ms) {
    const until = clock.now + ms;
    for (;;) {
      clock.timers.sort((a, b) => a.at - b.at || a.seq - b.seq);
      const next = clock.timers[0];
      if (!next || next.at > until) break;
      clock.timers.shift();
      fire(next);
    }
    clock.now = until;
    if (clock.onBeat) clock.onBeat(clock.now);
  }
  function drain(limitMs = 3600000) {
    const stop = clock.now + limitMs;
    while (clock.timers.length && clock.now < stop) {
      clock.timers.sort((a, b) => a.at - b.at || a.seq - b.seq);
      fire(clock.timers.shift());
    }
  }

  // ---- remaining globals the page touches --------------------------------
  const noop = () => {};
  const win = {
    addEventListener: noop, removeEventListener: noop,
    devicePixelRatio: 1, innerWidth: 1920, innerHeight: 1080,
    location: { search: '', href: 'http://localhost:8765/' },
  };
  const sandbox = {
    document, window: win, console,
    setTimeout: setTimeout_, clearTimeout: clearTimeout_,
    setInterval: () => 0, clearInterval: noop,
    requestAnimationFrame: fn => setTimeout_(fn, 16),
    fetch: () => Promise.resolve({ ok: true, json: () => Promise.resolve({}),
                                   text: () => Promise.resolve('') }),
    EventSource: function () {
      return { addEventListener: noop, close: noop, onmessage: null, onerror: null };
    },
    URLSearchParams: URLSearchParams,
    Date, Math, JSON, Object, Array, String, Number, Set, Map, RegExp, Promise,
    isNaN, parseFloat, parseInt, Image: function () { return makeEl('img'); },
    location: win.location, navigator: { userAgent: 'harness' },
    alert: noop, confirm: () => true, FormData: function () {},
    performance: { now: () => clock.now },
    XMLHttpRequest: function () {
      return { open: noop, send: noop, responseText: '{"events":[]}', status: 200 };
    },
  };

  // Run the page script and hand back the entry points the tests drive.
  let api;
  try {
    const names = Object.keys(sandbox);
    const fn = new Function(...names,
      source + '\n;return { dispatch, resetMission, state, revealQ };');
    api = fn(...names.map(n => sandbox[n]));
  } catch (err) {
    console.error('FAIL: the page script did not evaluate: ' + err.message);
    console.error(err.stack);
    process.exit(1);
  }
  return { api, byId, clock, advance, drain, setTimeout: setTimeout_ };
}

// ---- assertions ----------------------------------------------------------
const failures = [];
function check(cond, msg) { if (!cond) failures.push(msg); }

const page = newPage();
const { api, byId, advance, drain } = page;
// textContent is written as a Number by the page; compare as text.
const kAgents = () => String(byId('kAgents').textContent);
const kWorkers = () => String(byId('kWorkers').textContent);
const kCycle = () => String(byId('kCycle').textContent);

const ev = (event, payload, timestamp) => ({ event, payload, timestamp });

// ---------------------------------------------------------------- test 1
// Counters must NOT move on arrival. Ten events land back to back, as the
// backend emits them; before the queue has revealed anything the KPI row
// still reads the reset state.
api.resetMission();
check(kAgents() === '0', `after reset kAgents is ${kAgents()}, expected 0`);
check(kWorkers() === '0', `after reset kWorkers is ${kWorkers()}, expected 0`);
check(!kCycle().includes('—') && !kCycle().includes('–'),
      `kCycle placeholder is a dash: ${JSON.stringify(kCycle())}`);
check(kCycle() === '0/4', `kCycle placeholder is ${kCycle()}, expected 0/4`);

let t = 1000;
for (let i = 0; i < 4; i++) api.dispatch(ev('worker.provisioned', { worker_id: 'w' + i }, t++));
for (let i = 0; i < 3; i++) api.dispatch(ev('agent.started', { agent_id: 'a' + i }, t++));

// An idle queue reveals its head item synchronously, so exactly ONE of the
// seven is legitimately on screen already (the queue must not add latency to
// the first beat of a mission). The other six have to wait their turn. Before
// the fix all seven landed at once, which is what the viewer was complaining
// about.
const early = Number(kAgents()) + Number(kWorkers());
check(early === 1,
      `${early} of 7 counter events applied before the queue paced them, ` +
      `expected exactly 1 (the synchronous head of an idle queue)`);

// ---------------------------------------------------------------- test 2
// As the queue drains, the numerals climb. Step the clock and watch.
advance(2000);
const mid = Number(kWorkers());
check(mid > 0, `after 2 s of reveal kWorkers is still ${kWorkers()}, the queue is not moving`);

drain();
check(kWorkers() === '4', `after the queue drained kWorkers is ${kWorkers()}, expected 4`);
check(kAgents() === '3', `after the queue drained kAgents is ${kAgents()}, expected 3`);

// ---------------------------------------------------------------- test 3
// Releases come back down, and the peak is remembered for the summary.
for (let i = 0; i < 4; i++) api.dispatch(ev('worker.released', { worker_id: 'w' + i }, t++));
drain();
check(kWorkers() === '0', `after every release kWorkers is ${kWorkers()}, expected 0`);
check(api.state.peakWorkers === 4,
      `peakWorkers is ${api.state.peakWorkers}, expected 4 so the summary can show it`);

// ---------------------------------------------------------------- test 4
// A mission that ends while the queue is still revealing must not close out
// on a stale count. mission.completed arrives immediately after a burst.
api.resetMission();
t = 2000;
for (let i = 0; i < 6; i++) api.dispatch(ev('worker.provisioned', { worker_id: 'x' + i }, t++));
for (let i = 0; i < 4; i++) api.dispatch(ev('agent.started', { agent_id: 'b' + i }, t++));
api.dispatch(ev('mission.completed', { status: 'complete' }, t++));
check(Number(kWorkers()) < 6,
      `the burst was applied instantly, so there was nothing left to pace ` +
      `(kWorkers ${kWorkers()})`);
drain();
check(api.state.finished === true,
      'the mission never finished: finish() is still waiting on the queue');
check(kWorkers() === '6',
      `mission ended on a stale count: kWorkers reads ${kWorkers()}, expected the ` +
      `peak of 6 once the queue drained`);
check(kAgents() === '4',
      `mission ended on a stale count: kAgents reads ${kAgents()}, expected 4`);

// ---------------------------------------------------------------- test 5
// Lockstep: a counter event sandwiched between two narration beats must be
// revealed between them, not before both. Order in equals order out.
api.resetMission();
const order = [];
t = 3000;
api.dispatch(ev('transcript.entry', { role: 'CHIEF ENGINEER', message: 'First beat.' }, t++));
api.dispatch(ev('worker.provisioned', { worker_id: 'z0' }, t++));
api.dispatch(ev('transcript.entry', { role: 'CHIEF ENGINEER', message: 'Second beat.' }, t++));
// Step in small slices and record when the numeral changed relative to how
// many items are still queued.
let last = kWorkers();
for (let i = 0; i < 200 && (api.revealQ.length || page.clock.timers.length); i++) {
  advance(100);
  if (kWorkers() !== last) { order.push(api.revealQ.length); last = kWorkers(); }
}
check(order.length === 1,
      `the worker numeral changed ${order.length} times for one worker event`);
check(order[0] === 1,
      `the worker numeral moved with ${order[0]} items still queued, expected 1 ` +
      `(the second narration beat), which is what "in lockstep" means`);

// ================================================================ replay
// Push a RECORDED mission stream through the page at its real inter-event
// timing and watch the KPI row. This is the measurement Katie's complaint
// actually needs: the synthetic tests above prove the queue paces the counter
// events, but real missions carry their counts on `roster.update`, so only a
// real stream shows whether the numerals move while the work is on screen.
// The measurement that matters is LAG: for every distinct fleet size the
// backend put on the wire, how long before that number is on screen. Katie's
// complaint is a lag of tens of seconds, so the number only ever arrives once
// the work it describes is over.
//
// THIRD COMPLAINT (2026-07-31, same day). "Reverify that the worker count is
// exactly in sync with the meshing/solving." Not "within a few seconds": the
// numeral has to be up while the mesh is being built and the solver is
// running, and come down when the slots are released. A separate run of this
// harness against the then-current page found the numeral first reading non
// zero only at the very END of the hump and adjoint acts, which the six second
// budget below did not catch because those two acts declare their fleet in a
// single instant and the old time based catch up applied the rise and the
// release in the same frame.
//
// So the replay now measures TWO things per stream, and prints both:
//
//   WIRE   the moment the mission first put meshing or solving on the wire,
//          against the moment it first declared a non zero fleet. This is the
//          backend's own honesty and no page change can move it.
//   SCREEN the moment that meshing/solving beat is REVEALED to the viewer,
//          against the moment the Workers numeral first leaves zero, plus how
//          long the numeral holds its non zero value. A count that flashes for
//          one frame is not "in sync with the solve" either.
//
// "Meshing or solving on screen" is deliberately read off the narration the
// viewer is looking at (WORK_RE below), not off a private event name, and the
// matched line is printed so the measurement can be audited.
const RISE_BUDGET_MS = 500;   // wire to screen budget on the fleet GROWING
const HELD_SHARE = 0.15;      // least share of a run the numeral must stand at a fleet size
const WORK_RE = /\bmesh|solv|simplefoam|residual|iterat|rank|parallel/i;

function replay(file) {
  const events = fs.readFileSync(file, 'utf8').split('\n')
    .map(l => l.trim()).filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean)
    .filter(e => e.timestamp != null);
  if (!events.length) throw new Error(`no timestamped events in ${file}`);

  const p = newPage();
  const g = id => String(p.byId(id).textContent);
  const t0 = events[0].timestamp;
  const at = e => (e.timestamp - t0) * 1000;   // ms on the virtual clock

  // What the backend put on the wire: the fleet size each roster update
  // declared, keeping only the changes, with the time it was emitted.
  //
  // Every declared size is demanded, including one the backend supersedes in
  // the same instant. That used to be forgiven, and forgiving it is what let
  // the hump and adjoint acts pass while showing nothing: both declare their
  // fleet and stand it down on a single timestamp, so the only fleet size those
  // missions ever put on the wire was the one being excused.
  const wire = [];
  for (const e of events) {
    if ((e.event || e.type) !== 'roster.update') continue;
    const n = (e.payload || e).workers;
    if (n == null) continue;
    if (wire.length && wire[wire.length - 1].v === String(n)) continue;
    wire.push({ t: at(e), v: String(n) });
  }

  // The wire's own answer: when did the mission first say it was meshing or
  // solving, and when did it first declare a fleet? These come off the recorded
  // stream alone, with no page in the picture.
  let wireWork = null, wireWorkLine = '', wireFleet = null;
  for (const e of events) {
    const kind = e.event || e.type, pay = e.payload || e;
    if (wireWork == null) {
      if (kind === 'mesh.stats' || kind === 'race.lane' || kind === 'race.init') {
        wireWork = at(e); wireWorkLine = kind;
      } else if (kind === 'transcript.entry' && WORK_RE.test(String(pay.message || ''))) {
        wireWork = at(e); wireWorkLine = String(pay.message).slice(0, 76);
      }
    }
    if (wireFleet == null && kind === 'roster.update' && Number(pay.workers || 0) > 0) {
      wireFleet = at(e);
    }
  }

  const changes = { kAgents: [], kWorkers: [], kCycle: [] };
  const seen = { kAgents: null, kWorkers: null, kCycle: null };
  let finishedAt = null;
  // When a queued beat is REVEALED. revealQ is drained one item per timer, and
  // onBeat fires after every timer, so watching the head of the queue between
  // beats stamps each item with the moment it went on screen.
  let queued = [], screenWork = null, screenWorkLine = '';
  const noteRevealed = (item, now) => {
    if (screenWork != null || item.kind !== 'entry') return;
    const msg = String((item.p && item.p.message) || '');
    if (!WORK_RE.test(msg)) return;
    screenWork = now; screenWorkLine = msg.slice(0, 76);
  };
  const sample = now => {
    const q = p.api.revealQ;
    if (queued.length) {
      // Anything that was in the queue last beat and is not in it now was
      // revealed in between.
      const still = new Set(q);
      for (const item of queued) if (!still.has(item)) noteRevealed(item, now);
    }
    queued = q.slice();
    for (const id of Object.keys(changes)) {
      const v = g(id);
      if (v !== seen[id]) { seen[id] = v; changes[id].push({ t: now, v }); }
    }
    if (finishedAt == null && p.api.state.finished) finishedAt = now;
  };

  p.api.resetMission();
  // resetMission's zeroing is the baseline, not a counter update.
  seen.kAgents = g('kAgents'); seen.kWorkers = g('kWorkers'); seen.kCycle = g('kCycle');
  p.clock.onBeat = sample;

  const marks = {};
  for (const e of events) {
    const kind = e.event || e.type;
    p.setTimeout(() => {
      if (marks[kind] == null) marks[kind] = p.clock.now;
      marks._last = p.clock.now;
      try { p.api.dispatch(e); } catch (err) { p.clock.errors.push(err); }
      // The race lanes are rendered live and unpaced, so a lane IS the work
      // going on screen the instant it arrives.
      if (screenWork == null && (kind === 'race.lane' || kind === 'race.init')) {
        screenWork = p.clock.now; screenWorkLine = kind;
      }
    }, at(e));
  }
  p.drain();
  sample(p.clock.now);

  const streamEnd = marks._last != null ? marks._last : 0;
  // The mission is on screen from the first event until finish() lands, which
  // in a paced page is later than the last event. That span is "the run".
  const runEnd = Math.max(streamEnd, finishedAt ?? 0);

  // For each fleet size the backend declared, when does the numeral first
  // READ that size, at or after the wire said so? The rendered timeline is a
  // step function starting at the reset zero, so a numeral that already shows
  // the value costs nothing and one that has to wait costs its wait.
  const steps = [{ t: 0, v: '0' }].concat(changes.kWorkers);
  const valueAt = t => {
    let v = steps[0].v;
    for (const st of steps) { if (st.t > t) break; v = st.v; }
    return v;
  };
  // What the numeral read the instant BEFORE the wire spoke. A rise the page
  // honours lands on the very same virtual millisecond, so `valueAt` would
  // already be showing it and no rise would ever be seen.
  const valueBefore = t => {
    let v = steps[0].v;
    for (const st of steps) { if (st.t >= t) break; v = st.v; }
    return v;
  };
  const matched = wire.map(w => {
    // A RISE is the wire declaring MORE than the numeral is showing at that
    // moment: the viewer needs it while the work is happening, so it is owed
    // immediately. A FALL is the fleet standing down, which belongs to the beat
    // that reports the work finishing and is paced on purpose; it is still owed
    // before the mission ends. Classifying against what is on screen rather
    // than against the previous wire value is what makes a fleet the backend
    // stood down and reopened inside one instant read as the stand down it is.
    const rise = Number(w.v) > Number(valueBefore(w.t));
    if (valueAt(w.t) === w.v) return { wire: w, rise, lag: 0 };
    const hit = steps.find(st => st.t > w.t && st.v === w.v);
    return { wire: w, rise, lag: hit ? hit.t - w.t : null };
  });
  const lagsOf = f => matched.filter(m => m.lag != null && f(m)).map(m => m.lag);
  const riseLags = lagsOf(m => m.rise), fallLags = lagsOf(m => !m.rise);

  const stat = id => {
    const cs = changes[id];
    return {
      total: cs.length,
      during: cs.filter(c => c.t < runEnd).length,
      atEnd: cs.filter(c => c.t >= runEnd).length,
      firstNonZero: (cs.find(c => c.v !== '0' && c.v !== '0/4') || {}).t ?? null,
      resting: cs.length ? cs[cs.length - 1].v : g(id),
      timeline: cs,
    };
  };
  // How long the numeral actually stood at a non zero value while the mission
  // was on screen. A count that flashes for one frame is not in sync with a
  // solve that runs for a minute.
  const w = stat('kWorkers');
  let heldMs = 0;
  const wsteps = [{ t: 0, v: '0' }].concat(w.timeline);
  for (let i = 0; i < wsteps.length; i++) {
    if (wsteps[i].v === '0') continue;
    const until = Math.min(wsteps[i + 1] ? wsteps[i + 1].t : runEnd, runEnd);
    if (until > wsteps[i].t) heldMs += until - wsteps[i].t;
  }
  return {
    file: path.basename(file), events: events.length, streamEnd, runEnd, finishedAt,
    marks, errors: p.clock.errors, wire, matched,
    worstRiseLag: riseLags.length ? Math.max(...riseLags) : null,
    worstFallLag: fallLags.length ? Math.max(...fallLags) : null,
    missed: matched.filter(m => m.lag == null).length,
    kAgents: stat('kAgents'), kWorkers: w, kCycle: stat('kCycle'),
    wireWork, wireWorkLine, wireFleet, screenWork, screenWorkLine, heldMs,
    finished: p.api.state.finished,
    peakWorkers: p.api.state.peakWorkers, peakAgents: p.api.state.peakAgents,
  };
}

const s = ms => (ms / 1000).toFixed(1) + ' s';
for (const file of replayFiles) {
  let r;
  try { r = replay(file); }
  catch (e) { console.error(`FAIL: replay of ${file}: ${e.message}`); failures.push(String(e.message)); continue; }
  console.log(`\nreplay ${r.file}: ${r.events} events, on screen for ${s(r.runEnd)} ` +
              `(last event ${s(r.streamEnd)}, finish at ${r.finishedAt == null ? 'never' : s(r.finishedAt)})`);
  for (const id of ['kCycle', 'kAgents', 'kWorkers']) {
    const k = r[id];
    console.log(`  ${id.padEnd(8)} ${k.during} update(s) during the run, ${k.atEnd} at or after the end, ` +
      `first non zero ${k.firstNonZero == null ? 'never' : s(k.firstNonZero)}, ` +
      `resting ${JSON.stringify(k.resting)}`);
    console.log(`           ${k.timeline.map(c => `${s(c.t)}=${c.v}`).join('  ') || '(no change)'}`);
  }
  console.log(`  fleet size wire to screen: ` +
    r.matched.map(m => `${m.wire.v}${m.rise ? ' up' : ' down'}@${s(m.wire.t)}` +
                       `${m.lag == null ? ' NEVER SHOWN' : ` after ${s(m.lag)}`}`).join(', '));
  console.log(`  worst lag on a rise ${r.worstRiseLag == null ? 'n/a' : s(r.worstRiseLag)}, ` +
    `on a stand down ${r.worstFallLag == null ? 'n/a' : s(r.worstFallLag)}, ` +
    `${r.missed} wire value(s) never reached the numeral`);
  // The two numbers Katie asked to be adjacent.
  console.log(`  WIRE   meshing/solving declared at ` +
    `${r.wireWork == null ? 'never' : s(r.wireWork)}, fleet declared non zero at ` +
    `${r.wireFleet == null ? 'never' : s(r.wireFleet)}` +
    (r.wireWork != null && r.wireFleet != null
      ? `, gap ${s(r.wireFleet - r.wireWork)}` : '') +
    `   [${r.wireWorkLine}]`);
  console.log(`  SCREEN meshing/solving on screen at ` +
    `${r.screenWork == null ? 'never' : s(r.screenWork)}, numeral first moves at ` +
    `${r.kWorkers.firstNonZero == null ? 'never' : s(r.kWorkers.firstNonZero)}` +
    (r.screenWork != null && r.kWorkers.firstNonZero != null
      ? `, gap ${s(r.kWorkers.firstNonZero - r.screenWork)}` : '') +
    `, held non zero ${s(r.heldMs)} of ${s(r.runEnd)}   [${r.screenWorkLine}]`);
  if (r.errors.length) console.log(`  ${r.errors.length} error(s) thrown, first: ${r.errors[0].message}`);

  // ---- the behavioural bar --------------------------------------------
  const raceStart = r.marks['race.init'] ?? r.marks['race.lane'];
  const label = `${r.file}:`;
  check(r.errors.length === 0,
        `${label} ${r.errors.length} error(s) thrown during replay, first: ` +
        (r.errors[0] && r.errors[0].message));
  check(r.finished === true, `${label} the mission never reached finish()`);
  check(r.kWorkers.firstNonZero != null,
        `${label} kWorkers never left 0 for the whole mission`);
  // A fleet numeral that only wakes up in the back half of the run is the
  // "it looks hardcoded" failure Katie reported.
  check(r.kWorkers.firstNonZero != null && r.kWorkers.firstNonZero < r.runEnd / 2,
        `${label} kWorkers first reads non zero at ` +
        `${r.kWorkers.firstNonZero == null ? 'never' : s(r.kWorkers.firstNonZero)}, ` +
        `past the halfway mark of a ${s(r.runEnd)} run: the fleet count lands at the end`);
  // A rise is owed immediately: the moment the backend says the fleet grew,
  // the numeral says so, whatever the narration queue is doing.
  check(r.worstRiseLag != null && r.worstRiseLag <= RISE_BUDGET_MS,
        `${label} the worst wire to screen lag on a fleet RISE is ` +
        `${r.worstRiseLag == null ? 'infinite' : s(r.worstRiseLag)}, over the ` +
        `${s(RISE_BUDGET_MS)} budget: the numeral is not tracking the fleet as it grows`);
  // A stand down is paced, but it still has to land before the mission ends.
  check(r.worstFallLag == null || r.worstFallLag <= r.runEnd,
        `${label} a fleet stand down took ${s(r.worstFallLag)} to reach the numeral ` +
        `on a ${s(r.runEnd)} run`);
  // Every distinct fleet size the backend declared has to reach the numeral.
  // The last one is allowed to be swallowed by finish()'s peak restore.
  check(r.missed <= 1,
        `${label} ${r.missed} of ${r.wire.length} fleet sizes never reached the ` +
        `numeral at all, so the climb and fall was never on camera`);
  // The count has to STAND at the fleet size while the fleet is working, not
  // flash it. Before the guard in `rosterCounts` the B-52 act held its 6 for
  // 0.4 s of a 64.5 s run and the Ahmed act held its 6 for 1.0 s of 57.3 s,
  // because a stale idle roster queued ahead of the fleet roster wiped the rise
  // one beat after it landed.
  check(r.heldMs >= r.runEnd * HELD_SHARE,
        `${label} the Workers numeral stood at a fleet size for only ${s(r.heldMs)} ` +
        `of a ${s(r.runEnd)} run (${(r.heldMs / r.runEnd * 100).toFixed(0)}%), under the ` +
        `${(HELD_SHARE * 100).toFixed(0)}% bar: the count flashes rather than tracking the solve`);
  check(r.kAgents.during >= 2,
        `${label} kAgents moved ${r.kAgents.during} time(s) during the run, ` +
        `expected the team to build up on camera`);
  check(r.kCycle.during >= 2,
        `${label} kCycle moved ${r.kCycle.during} time(s) during the run`);
  if (raceStart != null) {
    // Katie: "the workers should appear as soon as either reduced or mc start".
    // AT OR BEFORE the moment the first lane appears, not "soon after".
    check(r.kWorkers.firstNonZero != null && r.kWorkers.firstNonZero <= raceStart + RISE_BUDGET_MS,
          `${label} the race lanes start at ${s(raceStart)} but kWorkers first reads ` +
          `non zero at ${r.kWorkers.firstNonZero == null ? 'never' : s(r.kWorkers.firstNonZero)}, ` +
          `more than ${s(RISE_BUDGET_MS)} later`);
  }
  // And on any mission, the numeral must not be waiting on the narration queue:
  // the fleet reaches the KPI row no later than the wire declared it.
  if (r.wireFleet != null) {
    check(r.kWorkers.firstNonZero != null &&
          r.kWorkers.firstNonZero <= r.wireFleet + RISE_BUDGET_MS,
          `${label} the backend declared its fleet at ${s(r.wireFleet)} but the numeral ` +
          `first reads non zero at ` +
          `${r.kWorkers.firstNonZero == null ? 'never' : s(r.kWorkers.firstNonZero)}`);
  }
  check(r.kWorkers.resting === String(r.peakWorkers) || r.peakWorkers === 0,
        `${label} the resting kWorkers is ${r.kWorkers.resting} but the peak was ` +
        `${r.peakWorkers}: the end state lost the mission's effort`);
}

// ---------------------------------------------------------------- report
if (failures.length) {
  console.error('CONTROL ROOM PACING FAILURES:');
  for (const f of failures) console.error('  * ' + f);
  process.exit(1);
}
console.log('control room pacing: all checks passed');
