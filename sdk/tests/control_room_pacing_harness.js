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
// --caption carries the REAL mesh caption in from the backend module at run
// time. This harness deliberately holds NO copy of that text: a copy here
// would go green while the screen displayed something else, which is the same
// class of defect as a grep that survives a mutation. Without --caption the
// caption checks below prove PRESENCE AND PLACEMENT ONLY, on a synthetic
// string; the identity of the rendered text against the backend constant is
// asserted by tests/test_control_room_pacing.py, which owns the import.
// --docket carries the REAL research docket in from the server module at run
// time, for the same reason: the id sweep proves more on the live wording
// than on a synthetic stand-in, and this file holds no copy of either.
let captionArg = null;
let docketArg = null;
// --bench N drives N solve.frame events through the real dispatch and reports
// the mean cost of one. See the per-event cost block near the foot of the file
// for what that number is and what it is not.
let benchFrames = 0;
for (let i = 1; i < argv.length; i++) {
  if (argv[i] === '--replay') replayFiles.push(argv[++i]);
  else if (argv[i] === '--caption') captionArg = argv[++i];
  else if (argv[i] === '--docket') docketArg = argv[++i];
  else if (argv[i] === '--bench') benchFrames = +argv[++i] || 0;
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
//
// `src` defaults to the real page. The closing-state checks at the foot of
// this file pass a DELIBERATELY MUTATED source instead, to prove those checks
// can actually fail: an assertion never seen to fail is not evidence. The
// mutants are built in memory from the real page at run time and never exist
// on disk, so they cannot drift out of step with the file they mutate.
function newPage(src = source) {
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
    // textContent and innerHTML are one piece of content in a real element:
    // writing either REPLACES what the other was showing. The stub kept two
    // independent strings, so a panel the page had put back to its resting
    // text still answered with the markup it used to hold, and a test that
    // read the wrong one of the two could not see a reset at all.
    let _html = '';
    Object.defineProperty(el, 'innerHTML', {
      get: () => _html, set: v => { _html = String(v); }, enumerable: true });
    Object.defineProperty(el, 'textContent', {
      get: () => _html.replace(/<[^>]*>/g, ''),
      set: v => { _html = String(v); }, enumerable: true });
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
    // Memoised by selector, exactly as getElementById is memoised by id.
    // Returning a FRESH element per call silently discarded every write the
    // page makes through this door: resetMission() hides the Report tab with
    // `document.querySelector('.tab[data-view="memo"]').hidden = true`, and a
    // throwaway element meant the later read saw hidden=false and the page
    // looked like it was opening a report pane it never opens. Any page logic
    // that round-trips state through a selector was invisible here.
    querySelector: sel => byId('sel:' + sel),
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
  // Declared before the sandbox that closes over it: page.setXhr() installs a
  // url -> responseText function so one page can serve the static-replay
  // snapshot and its geometry from different URLs.
  let xhrRoutes = null;
  let fetchRoutes = null;
  const sandbox = {
    document, window: win, console,
    setTimeout: setTimeout_, clearTimeout: clearTimeout_,
    setInterval: () => 0, clearInterval: noop,
    requestAnimationFrame: fn => setTimeout_(fn, 16),
    // The two endpoints the operator's own actions hit. UPLOAD answers with the
    // real body the running server returned for b52.stl on 2026-07-31, so the
    // surface panel is driven by the shape it will actually receive; the mission
    // POST answers with an id, so a launch can be driven without a solver.
    fetch: (url, opts) => {
      const u = String(url);
      // Overridable per page via page.setFetch(), the same door setXhr opens
      // for the synchronous path. The computational grid arrives by fetch from
      // a URL nothing else here serves, and a handler that can only be shown to
      // do nothing has not been shown to do anything.
      if (fetchRoutes) {
        const answer = fetchRoutes(u, opts);
        if (answer !== undefined)
          return Promise.resolve({ ok: true, json: () => Promise.resolve(answer),
                                   text: () => Promise.resolve(JSON.stringify(answer)) });
      }
      if (u.startsWith('/api/geometry/upload'))
        return Promise.resolve({ ok: true, json: () => Promise.resolve({
          name: 'b52.stl', triangles: 13784, url: '/api/geometry?name=b52.stl',
          suggested: 'Mesh and solve b52.stl and report the drag.' }) });
      if (u.startsWith('/api/missions') && opts && opts.method === 'POST')
        return Promise.resolve({ ok: true,
                                 json: () => Promise.resolve({ mission_id: 'harness-1' }) });
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}),
                               text: () => Promise.resolve('') });
    },
    EventSource: function () {
      return { addEventListener: noop, close: noop, onmessage: null, onerror: null };
    },
    URLSearchParams: URLSearchParams,
    Date, Math, JSON, Object, Array, String, Number, Set, Map, RegExp, Promise,
    isNaN, parseFloat, parseInt, Image: function () { return makeEl('img'); },
    location: win.location, navigator: { userAgent: 'harness' },
    alert: noop, confirm: () => true, FormData: function () {},
    performance: { now: () => clock.now },
    // URL-aware, and overridable per page via page.setXhr(). The static
    // still-capture path (?static=1) fetches its event snapshot AND its
    // geometry through synchronous XHR, so a stub that ignored the URL and
    // always answered '{"events":[]}' could not drive that path at all. It is
    // the path the filmed stills come from, so it has to be drivable.
    XMLHttpRequest: function () {
      let url = '';
      return {
        open: (_method, u) => { url = String(u || ''); }, send: noop,
        get responseText() {
          const answer = xhrRoutes && xhrRoutes(url);
          return answer != null ? answer : '{"events":[]}';
        },
        status: 200,
      };
    },
  };

  // Run the page script and hand back the entry points the tests drive.
  let api;
  try {
    const names = Object.keys(sandbox);
    const fn = new Function(...names,
      src + '\n;return { dispatch, resetMission, state, revealQ, renderAgendaDocket, '
          + 'uploadSurface, launchMission, resumeMission, '
          // The fidelity chip is rendered into an element that is APPENDED to
          // the feed, and this stub's appendChild is a no-op, so the chip
          // cannot be read back off the DOM the way #viewportLabel can. The
          // renderer itself is exported instead: it is the one function all
          // four call sites in the page go through, so a check on it is a
          // check on every surface that shows a chip.
          + 'verdictBadge, credentialBadge };');
    api = fn(...names.map(n => sandbox[n]));
  } catch (err) {
    console.error('FAIL: the page script did not evaluate: ' + err.message);
    console.error(err.stack);
    process.exit(1);
  }
  return { api, byId, clock, advance, drain, setTimeout: setTimeout_,
           setXhr: fn => { xhrRoutes = fn; },
           setFetch: fn => { fetchRoutes = fn; } };
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
// Releases come back down, and stay down.
for (let i = 0; i < 4; i++) api.dispatch(ev('worker.released', { worker_id: 'w' + i }, t++));
drain();
check(kWorkers() === '0', `after every release kWorkers is ${kWorkers()}, expected 0`);
check(api.state.highWorkers === 4,
      `the numeral never reached the fleet size: high water mark is ${api.state.highWorkers}, expected 4`);

// ---------------------------------------------------------------- test 4
// A mission that ends while the queue is still revealing must not close out
// on a stale count. mission.completed arrives immediately after a burst.
//
// 2026-07-31. What "the right count" means at the end changed: Katie's shape is
// "start at 0, then # workers as soon as the meshing starts, then 0 when the
// run is complete". Six workers were provisioned and never released, so the
// fleet numeral rests at 6 here; the release case is test 3 and the recorded
// missions below, every one of which ends on 0.
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
      `six provisioned slots that were never released`);
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
    // Katie's shape, on the wire and on the screen: 0, the fleet size while the
    // meshing and solving happen, 0 when the run is complete. A "bounce" is the
    // numeral leaving zero AGAIN after it has come back to zero. Counting it on
    // both sides is what says who owns one: a bounce the backend declared is the
    // act's, a bounce only the screen shows is the page's.
    wireShape: ['0'].concat(wire.map(x => x.v)).filter((v, i, a) => v !== a[i - 1]),
    screenShape: ['0'].concat(w.timeline.map(c => c.v)).filter((v, i, a) => v !== a[i - 1]),
    highWorkers: p.api.state.highWorkers, peakAgents: p.api.state.peakAgents,
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
  const bounces = shape => shape.filter((v, i) => i > 1 && v !== '0' && shape[i - 1] === '0').length;
  console.log(`  SHAPE  wire ${r.wireShape.join(' -> ')}` +
    `   screen ${r.screenShape.join(' -> ')}` +
    `   (bounces: wire ${bounces(r.wireShape)}, screen ${bounces(r.screenShape)})`);
  if (bounces(r.wireShape))
    console.log(`  NOTE   the mission stands its fleet down and declares one again ` +
      `mid run, so the shape on camera cannot be cleaner than 0 -> N -> 0. ` +
      `That belongs to the act, not the page.`);
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
  // THE END STATE IS ZERO. Katie, 2026-07-31: "start at 0, then # workers as
  // soon as the meshing starts, then 0 when the run is complete." A completed
  // mission holds no slots, so the numeral reads none. This check used to
  // demand the opposite — that the run ends on its PEAK — and the peak being
  // restored by finish() is exactly the "6 to 0 to 6" that was on camera.
  const lastWire = r.wire.length ? r.wire[r.wire.length - 1].v : '0';
  if (lastWire === '0') {
    check(r.kWorkers.resting === '0',
          `${label} the mission stood its fleet down but the numeral rests at ` +
          `${r.kWorkers.resting}: the count climbs back up after the run is complete`);
  }
  // Every value on camera has to be one the mission actually declared — the
  // page may lag a stand down onto its beat, but it may not synthesise a number.
  const declared = new Set(r.wire.map(x => x.v).concat('0'));
  check(r.kWorkers.timeline.every(c => declared.has(c.v)),
        `${label} the numeral showed ` +
        `${r.kWorkers.timeline.filter(c => !declared.has(c.v)).map(c => c.v).join(', ')}, ` +
        `which the mission never put on the wire`);
  // The page must not invent a bounce the mission did not emit.
  check(bounces(r.screenShape) <= bounces(r.wireShape),
        `${label} the screen bounces ${bounces(r.screenShape)} time(s) ` +
        `(${r.screenShape.join(' -> ')}) but the mission only declared ` +
        `${bounces(r.wireShape)} (${r.wireShape.join(' -> ')})`);
}

// =============================================== the surface panel, test 6
// THE FILE THE ACT IS RUNNING ON STAYS ON SCREEN, FOR THE WHOLE ACT.
// Katie, 2026-07-31: "Everywhere we must see loaded_surface.stl in the load
// surface section ... throughout the entire act." Reported twice. The launch
// CONSUMES the attachment on purpose (one surface, one launch: carrying it
// invisibly routed the next act onto the previous act's body), and clearing the
// attachment used to blank the panel with it, so the acts she films lost the
// filename the moment they started.
//
// This lives here because it is the same page script on the same stub DOM, and
// because it is the same class of complaint: what the panel says while the act
// is running. The operator's two actions are driven for real -- upload, then
// launch -- and the panel is read at every stage of the act that follows.
const text = el => String(el.innerHTML || el.textContent).replace(/<[^>]+>/g, '');
(async () => {
  const sp = newPage();
  const label = () => text(sp.byId('surfaceLabel'));
  const note = () => (sp.byId('surfaceNote').hidden ? '' : text(sp.byId('surfaceNote')));
  sp.api.resetMission();

  await sp.api.uploadSurface({ target: { files: [{ name: 'b52.stl',
    arrayBuffer: async () => new ArrayBuffer(8) }], value: 'x' } });
  await new Promise(r => setImmediate(r));
  check(label().includes('b52.stl'),
        `after the upload the panel reads ${JSON.stringify(label())}, expected the filename`);
  check(sp.api.state.uploaded === 'b52.stl',
        `the surface was not attached to the next launch (${sp.api.state.uploaded})`);

  sp.byId('goal').value = 'Solve the external aerodynamics of the supplied B-52 geometry.';
  await sp.api.launchMission();
  await new Promise(r => setImmediate(r));
  // The router's rule is untouched: the attachment is spent by this launch.
  check(sp.api.state.uploaded === null,
        `the launch left the surface attached (${sp.api.state.uploaded}): the next act ` +
        `would silently run on this body too`);
  check(label().includes('b52.stl'),
        `the launch blanked the panel: it reads ${JSON.stringify(label())}`);
  check(note().includes('running on it'),
        `the panel does not say the mission is running on the file: ${JSON.stringify(note())}`);
  // No dashes and nothing "held", "saved" or "prepared" on a camera surface.
  check(!/[\u2013\u2014]|\b(stored|held|saved|cached|prepared)\b/i.test(label() + note()),
        `the surface panel breaks house style: ${JSON.stringify(label() + ' ' + note())}`);

  // Through the act, and past the end of it.
  let n = 0;
  for (const e of ['transcript.entry', 'roster.update', 'mesh.stats', 'plot.ready']) {
    sp.api.dispatch({ event: e, payload: { role: 'CHIEF ENGINEER', message: 'Meshing.',
                                           workers: 6 }, timestamp: 1000 + n++ });
  }
  sp.drain();
  check(label().includes('b52.stl'),
        `mid act the panel reads ${JSON.stringify(label())}`);
  sp.api.dispatch({ event: 'mission.completed', payload: {}, timestamp: 1100 });
  sp.drain();
  check(sp.api.state.finished && label().includes('b52.stl'),
        `at completion the panel reads ${JSON.stringify(label())}`);

  // The NEXT act, launched with no surface, must not inherit this one's body.
  sp.byId('goal').value = 'Solve the NASA wall mounted hump and check separation.';
  await sp.api.launchMission();
  await new Promise(r => setImmediate(r));
  check(!label().includes('b52.stl'),
        `an act launched with no surface still names the last one: ${JSON.stringify(label())}`);

  // ------------------------------------------------- closing states (D-1)
  // WHY THIS IS HERE AND NOT IN A NEW FILE. The label a mission closes under
  // is written by finish(), which this harness already drives and already
  // owns checks for. A second harness would mean a second stub DOM and a
  // second notion of what "the page" is, and the two would drift.
  //
  // THE DEFECT. The page decided the closing label from the literal string
  // 'complete' passed at the call site, never from the status the backend
  // sent. A request the lab openly DECLINES to run publishes
  //   mission.completed {"status": "incomplete", "reason": ...}
  // (measured: chief_engineer/server.py _explain_unparsed, reached by any
  // prompt that matches no workflow, e.g. "Blown slot jet momentum sweep"
  // with no surface attached, which routes to general-mission). The screen
  // put MISSION COMPLETE over it, contradicting the refusal the transcript
  // had just given in plain words.
  //
  // FOUR STATES, AND THEY MUST STAY DISTINCT. Collapsing any pair of these
  // back together is the regression:
  //   complete   -> MISSION COMPLETE
  //   scoped     -> the backend's own headline
  //   incomplete -> a refusal that does not read as a completion
  //   failed     -> MISSION ENDED
  const SCOPED_HEADLINE = 'COMPLETE: PART OF THE REQUEST NOT RUN';
  const scopedPayload = {
    scoped: true, headline: SCOPED_HEADLINE, not_run: ['a blowing sweep'],
  };

  // Close one mission on a given terminal event and report the resting label.
  // Each scenario gets a FRESH page: a scope-down that leaked across missions
  // would otherwise be read as a pass here.
  function closeWith(events, src) {
    const p = newPage(src);
    p.api.resetMission();
    let t = 1000;
    for (const [event, payload] of events) p.api.dispatch({ event, payload, timestamp: t++ });
    p.drain();
    return {
      status: String(p.byId('globalStatus').textContent),
      conf: String(p.byId('routeConf').textContent),
      view: p.api.state.currentView,
    };
  }
  const routed = ['mission.routed', { intent: 'geometry-study', confidence: 0.99, rationale: 'x' }];
  // The payloads below are the ones the backend really emits, not invented
  // shapes: the incomplete one is copied from an executed _run_mission.
  const CLEAN = [routed, ['mission.completed', { status: 'complete' }]];
  const SCOPED = [routed, ['mission.scoped', scopedPayload],
                  ['mission.completed', Object.assign({ status: 'complete' }, scopedPayload)]];
  const REFUSED = [['mission.completed', { status: 'incomplete',
    reason: 'The request needs a measurable objective or a named geometry.' }]];
  const FAILED = [routed, ['mission.failed', { reason: 'boom' }]];

  const clean = closeWith(CLEAN), scoped = closeWith(SCOPED);
  const refused = closeWith(REFUSED), failed = closeWith(FAILED);

  // -- the positive arm: a declined request never closes under a completion.
  check(refused.status !== 'MISSION COMPLETE',
        `a request the lab DECLINED to run closes under ${JSON.stringify(refused.status)}: ` +
        `the label contradicts the refusal the transcript just gave`);
  check(!/complete/i.test(refused.status),
        `the refusal label still reads as a completion: ${JSON.stringify(refused.status)}`);

  // -- the negative arm: a clean run must be left alone. A guard that
  //    qualifies everything is as broken as one that qualifies nothing.
  check(clean.status === 'MISSION COMPLETE',
        `a run that answered the whole request no longer reads MISSION COMPLETE: ` +
        `${JSON.stringify(clean.status)}`);
  check(!/not run/i.test(clean.conf),
        `a clean run picked up a scope-down it did not earn: ${JSON.stringify(clean.conf)}`);

  // -- the four states stay distinct.
  const labels = [clean.status, scoped.status, refused.status, failed.status];
  check(new Set(labels).size === 4,
        `the closing states collapsed into one another: ${JSON.stringify(labels)}`);
  check(scoped.status === SCOPED_HEADLINE,
        `a scoped run closes under ${JSON.stringify(scoped.status)}`);
  check(failed.status === 'MISSION ENDED',
        `a failed run closes under ${JSON.stringify(failed.status)}`);
  // A declined request has no report to show, so it must not swing the
  // viewer to the report pane on the way out.
  check(refused.view !== 'memo',
        `a declined request opened the report pane: there is no report to show`);

  // -- THE UNKNOWN-STATUS DEFAULT IS FAIL-OPEN, AND IS PINNED HERE SO IT IS
  //    NEVER SILENT. `(p && p.status) || 'complete'` sends any status this
  //    page does not name to MISSION COMPLETE. For the statuses the backend
  //    emits today that is right: the only unnamed one is 'complete' itself.
  //    But a fifth status added later would inherit MISSION COMPLETE without
  //    a word, and be found on camera. The companion assertion lives in
  //    tests/test_scope_down.py, which reads the statuses the backend really
  //    publishes and fails if one appears that this page does not name. This
  //    check pins the fallback itself, so the behaviour is deliberate and
  //    recorded rather than accidental.
  const unknown = closeWith([routed, ['mission.completed', { status: 'quiesced' }]]);
  check(unknown.status === 'MISSION COMPLETE',
        `the unknown-status fallback changed: a status this page does not name ` +
        `now closes under ${JSON.stringify(unknown.status)}. That may well be an ` +
        `improvement, but it is a deliberate behaviour change and the comment at ` +
        `the finish() call site must be rewritten to match it`);

  // -- house style, on the strings this page puts on camera itself. These
  //    literals live in the HTML, which the python register rails do NOT
  //    scan (they read workflows/*.py and a named list of chief_engineer
  //    modules). Unscanned is exactly how a dash gets back onto a camera
  //    surface, so the rails are applied here, at the rendered label.
  for (const [name, text] of [['clean', clean.status], ['scoped', scoped.status],
                              ['refused', refused.status], ['failed', failed.status]]) {
    check(!/[–—]/.test(text), `the ${name} label carries a dash: ${JSON.stringify(text)}`);
    check(!/\s--\s|\w--\w/.test(text), `the ${name} label carries a prose double hyphen: ${JSON.stringify(text)}`);
    check(text === text.toUpperCase(), `the ${name} label breaks the label register: ${JSON.stringify(text)}`);
  }

  // -- PLANTED CONTROLS. Each mutant reverts one half of the behaviour above
  //    and the check that covers it MUST go red. A check never seen to fail
  //    proves nothing, and the defect this section exists for survived a
  //    suite that only grepped the page's text.
  function mutate(from, to) {
    if (!source.includes(from)) {
      failures.push(`planted control could not be built: the page no longer contains ` +
                    `${JSON.stringify(from)}. Re-aim the mutant at the current source ` +
                    `rather than deleting this control.`);
      return null;
    }
    return source.split(from).join(to);
  }
  const noRefusal = mutate(
    "    : status === 'incomplete' ? 'NOTHING WAS RUN FOR THIS REQUEST'\n", '');
  const noScoped = mutate("(state.scope && state.scope.headline) || 'MISSION COMPLETE'",
                          "'MISSION COMPLETE'");
  const alwaysRefusal = mutate("status === 'incomplete' ?", "true ?");

  if (noRefusal) {
    check(closeWith(REFUSED, noRefusal).status === 'MISSION COMPLETE',
          'PLANTED CONTROL DEAD: reverting the refusal label did not bring back ' +
          'MISSION COMPLETE, so the refusal check is not testing that code');
  }
  if (noScoped) {
    check(closeWith(SCOPED, noScoped).status === 'MISSION COMPLETE',
          'PLANTED CONTROL DEAD: reverting the scoped headline did not change the ' +
          'label, so the scoped check is not testing that code');
  }
  if (alwaysRefusal) {
    // The negative arm, proven live: force the refusal branch on and the
    // clean run must break. Without this, "a clean run reads MISSION
    // COMPLETE" could be passing for free.
    check(closeWith(CLEAN, alwaysRefusal).status !== 'MISSION COMPLETE',
          'PLANTED CONTROL DEAD: forcing the refusal branch on left the clean run ' +
          'reading MISSION COMPLETE, so the negative arm is vacuous');
  }

  // ----------------------------------------------- the mesh caption (Act D)
  // WHY. The backend emitted a mandatory mesh caption on every frame and the
  // viewport rendered it on none: the field simply had no reader. The word
  // "caption" occurred zero times in the page while p.label and p.url each
  // occurred four times, so the field was absent, not merely unread.
  //
  // THREE PAINTING SITES, NOT TWO. Enumerated rather than inherited:
  // state.mesh is assigned in exactly three places, loadGeometry, loadField
  // and the synchronous block inside resumeMission(id, staticReplay), and
  // each is paired with a viewportLabel write. The third is the ?static=1
  // still capture, which is what actually goes on camera; a caption wired
  // only into the first two would pass a live check and fail the shoot.
  // Rule 14: a lesson is not applied until EVERY call site asserts it.
  const CAP = 'A caption the backend put on this frame.';
  const capOf = p => String(p.byId('viewportCaption').textContent || '');
  // loadGeometry/loadField await a VIRTUAL timer and then a REAL promise
  // (fetch). drain() is synchronous, so it fires the timer but cannot run the
  // microtask that follows it. Interleave the two until the frame settles.
  const settlePage = async p => {
    for (let i = 0; i < 8; i++) { p.drain(); await new Promise(r => setImmediate(r)); }
  };

  // -- live geometry frame.
  {
    const p = newPage();
    p.api.resetMission();
    p.api.dispatch({ event: 'geometry.ready',
                     payload: { url: '/api/geometry?name=w.stl', label: 'Wing', caption: CAP },
                     timestamp: 1000 });
    await settlePage(p);
    check(capOf(p) === CAP,
          `a geometry frame carrying a caption rendered ${JSON.stringify(capOf(p))}`);
  }
  // -- live field frame. Rule 14: the same lesson, the other call site.
  {
    const p = newPage();
    p.api.resetMission();
    p.api.dispatch({ event: 'field.ready',
                     payload: { url: '/api/geometry?name=w.stl', label: 'Cp', caption: CAP },
                     timestamp: 1000 });
    await settlePage(p);
    check(capOf(p) === CAP,
          `a field frame carrying a caption rendered ${JSON.stringify(capOf(p))}`);
  }
  // -- THE NEGATIVE ARM: a frame with no caption must not inherit the last
  //    one's. This is the same stale-qualifier leak the scope-down guards.
  {
    const p = newPage();
    p.api.resetMission();
    p.api.dispatch({ event: 'geometry.ready',
                     payload: { url: '/api/geometry?name=a.stl', label: 'A', caption: CAP },
                     timestamp: 1000 });
    await settlePage(p);
    const captioned = capOf(p);
    p.api.dispatch({ event: 'geometry.ready',
                     payload: { url: '/api/geometry?name=b.stl', label: 'B' },
                     timestamp: 1001 });
    await settlePage(p);
    check(captioned === CAP && capOf(p) === '',
          `an uncaptioned frame kept the previous frame's caption: ` +
          `${JSON.stringify(capOf(p))} is still standing under a new body`);
    // And a reset must not carry it into the NEXT mission either.
    p.api.dispatch({ event: 'geometry.ready',
                     payload: { url: '/api/geometry?name=a.stl', label: 'A', caption: CAP },
                     timestamp: 1002 });
    await settlePage(p);
    p.api.resetMission();
    check(capOf(p) === '',
          `a caption survived resetMission and would caption the next mission: ` +
          `${JSON.stringify(capOf(p))}`);
  }
  // -- THE FILMED PATH: ?static=1 still capture, driven for real through
  //    resumeMission's synchronous branch rather than asserted about.
  {
    const p = newPage();
    const snapshot = JSON.stringify({ mission_id: 'm-cap', closed: true, events: [
      { event: 'mission.routed', payload: { intent: 'shape-optimization', confidence: 0.9, rationale: 'x' }, timestamp: 1 },
      { event: 'geometry.ready', payload: { url: '/api/geometry?name=w.stl', label: 'Wing', caption: CAP }, timestamp: 2 },
      { event: 'mission.completed', payload: { status: 'complete' }, timestamp: 3 },
    ] });
    p.setXhr(url => url.includes('/events.json') ? snapshot
                  : url.includes('/api/geometry') ? '{"vertices":[],"faces":[]}' : null);
    await p.api.resumeMission('m-cap', true);
    await new Promise(r => setImmediate(r));
    // READ BEFORE DRAINING, ON PURPOSE. This is the synchronous window the
    // static block exists to fill: a headless still can be grabbed before the
    // paced queue and the async geometry load have run. The live handlers
    // cannot have written anything yet, because loadGeometry awaits a timer
    // on the virtual clock that only drain() fires. So a caption present here
    // was put there by the static block and by nothing else.
    check(capOf(p) === CAP,
          `THE FILMED STILL HAS NO CAPTION. In the synchronous window the ` +
          `?static=1 capture grabs, the caption read ${JSON.stringify(capOf(p))}. ` +
          `A caption wired only into the live handlers is absent from every ` +
          `captured frame, and the captured frames are what goes on camera`);
    await settlePage(p);
    check(capOf(p) === CAP,
          `the caption did not survive the replay settling: ${JSON.stringify(capOf(p))}`);
  }
  // -- IDENTITY AGAINST THE BACKEND CONSTANT, when it is handed in. The text
  //    is never written here. It arrives on --caption from the module that
  //    defines it, is driven through a real frame, and must come back off the
  //    element byte for byte. subText escapes before writing, so a caption
  //    carrying markup or an entity would be caught here as a mismatch rather
  //    than reaching the screen mangled.
  if (captionArg != null) {
    const p = newPage();
    p.api.resetMission();
    p.api.dispatch({ event: 'geometry.ready',
                     payload: { url: '/api/geometry?name=w.stl', label: 'Wing',
                                caption: captionArg },
                     timestamp: 1000 });
    await settlePage(p);
    check(capOf(p) === captionArg,
          `the caption on screen is not the caption the backend defines.\n` +
          `      backend: ${JSON.stringify(captionArg)}\n` +
          `      screen : ${JSON.stringify(capOf(p))}`);
  }

  // -- PLANTED CONTROLS for the caption, same discipline as the closing
  //    states: strip each reader and the matching check must go red.
  const noGeomCap = mutate("    subText('viewportCaption', p.caption || '');\n", '');
  const noStaticCap = mutate("          subText('viewportCaption', gp.caption || '');\n", '');
  if (noGeomCap) {
    const p = newPage(noGeomCap);
    p.api.resetMission();
    p.api.dispatch({ event: 'geometry.ready',
                     payload: { url: '/api/geometry?name=w.stl', label: 'W', caption: CAP },
                     timestamp: 1000 });
    await settlePage(p);
    check(capOf(p) === '',
          'PLANTED CONTROL DEAD: removing the live caption readers left the ' +
          'caption on screen, so the live caption checks test nothing');
  }
  if (noStaticCap) {
    const p = newPage(noStaticCap);
    const snap = JSON.stringify({ mission_id: 'm-cap', closed: true, events: [
      { event: 'geometry.ready', payload: { url: '/api/geometry?name=w.stl', label: 'W', caption: CAP }, timestamp: 2 }] });
    p.setXhr(url => url.includes('/events.json') ? snap
                  : url.includes('/api/geometry') ? '{"vertices":[],"faces":[]}' : null);
    await p.api.resumeMission('m-cap', true);
    await new Promise(r => setImmediate(r));
    // Read in the same synchronous window the real check uses. The replayed
    // event still reaches the LIVE handler once the queue drains, so draining
    // here would hide the regression behind the live writer: the mutant is
    // only distinguishable before the queue runs, which is exactly the window
    // a still capture grabs.
    check(capOf(p) === '',
          'PLANTED CONTROL DEAD: removing the static-replay caption writer left ' +
          'a caption in the capture window, so the filmed-path check is not ' +
          'testing the static block');
  }

  // -------------------------------------------- agenda wall curation (GUI)
  // The research agenda rendered EVERY proposal the server sent as a full
  // card. Measured on the live docket: 320 proposals, 123 done and 15
  // dismissed, so 138 decided cards carrying no action stood in front of the
  // work, with all 182 open ones listed underneath as digest rows.
  //
  // Curation is display-only: the docket is served whole, nothing is edited
  // and nothing is deleted. What is asserted here is that the screen shows a
  // bounded, current view AND says truthfully what it is not showing. A wall
  // that quietly dropped items would be worse than the wall.
  const proposal = (id, status, objective) => ({
    id, status, objective, rationale: 'why', expected_knowledge_gain: 'gain',
    est_core_min: 1, cost_basis: 'estimate', citations: [],
  });
  const renderDocket = (p, proposals) =>
    p.api.renderAgendaDocket({ proposals });
  const cardsIn = html => (html.match(/class="rp-card"/g) || []).length;

  {
    const p = newPage();
    // 12 open, 9 decided: enough of each to prove both halves.
    const props = [];
    for (let i = 0; i < 12; i++) props.push(proposal('open-' + i, 'proposed', 'Open item ' + i));
    for (let i = 0; i < 6; i++) props.push(proposal('done-' + i, 'done', 'Decided item ' + i));
    for (let i = 0; i < 3; i++) props.push(proposal('drop-' + i, 'dismissed', 'Dropped item ' + i));
    const html = renderDocket(p, props);

    check(!/Decided item|Dropped item/.test(html),
          'a decided proposal is still rendered as a card: the wall is showing ' +
          'history that carries no action and no buttons');
    // 6 open cards + the digest card + the "what is not shown" card.
    check(cardsIn(html) === 8,
          `the agenda wall rendered ${cardsIn(html)} cards, expected 8 ` +
          `(six open proposals, the digest, and the line saying what is not shown)`);
    check(/6 more proposals are open/.test(html),
          `the wall does not say how many open proposals it is not showing: ` +
          `12 open, 6 shown, so 6 must be named. Got: ` +
          JSON.stringify((html.match(/\d+ more proposal[^<]*/) || [''])[0]));
    check(/9 already decided and kept on the record/.test(html),
          `the wall does not say the decided proposals are kept: 9 were ` +
          `decided and the record must be named, not silently dropped`);
  }
  // -- THE NEGATIVE ARM: a small, entirely current docket must be shown in
  //    full, with no "not showing" line invented for it.
  {
    const p = newPage();
    const props = [proposal('a', 'proposed', 'First'), proposal('b', 'proposed', 'Second')];
    const html = renderDocket(p, props);
    check(/First/.test(html) && /Second/.test(html),
          'a small docket lost a proposal that should have been shown in full');
    check(!/more proposal/.test(html) && !/already decided/.test(html),
          'a docket with nothing hidden still claims it is hiding something: ' +
          JSON.stringify((html.match(/(\d+ more proposal|\d+ already decided)[^<]*/) || [''])[0]));
    check(cardsIn(html) === 3,
          `a two-proposal docket rendered ${cardsIn(html)} cards, expected 3 ` +
          `(both proposals and the digest, and no remainder line)`);
  }
  // -- NO INTERNAL ID SURVIVES ONTO A VISIBLE CARD.
  //    The card renderer interpolated the citation VALUES straight into the
  //    wall: `from the record · demo-output/website/hlpw6/FEASIBILITY_PROBE.md`.
  //    Internal paths, rung ids and lesson ids never belong on a filmed
  //    surface. The phrase stays because it is the honest claim that the
  //    proposal came from a record; the values are gone.
  //
  //    Asserted on the RENDERED TEXT, not on the source. Tags are stripped
  //    first, so `data-id="..."` on the buttons is correctly out of scope: it
  //    is an attribute, never on camera. And the reader is proven able to see
  //    a non-zero before its zero is believed.
  const visibleText = html => html.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ');
  const ID_SHAPED = new RegExp(
    ['\\b[A-Z]{1,3}\\d+[a-z]?\\b',            // rung ids: R5, T1b, F14, K0c
     '\\bL-\\d+\\b', '\\bD\\d{3,}\\b',        // lesson and docket ids
     '\\bm-[0-9a-f]{6,}\\b',                  // mission ids
     '[\\w./-]*\\.(?:py|md|json|jsonl|html)\\b',        // file names
     '\\b(?:docs|sdk|cases|verification|scripts|demo-output)/[\\w./-]+',
     'https?://'].join('|'), 'g');
  const idsIn = html => [...new Set(visibleText(html).match(ID_SHAPED) || [])];

  {
    // A docket whose citations are exactly the internal paths the live one
    // carries. None of them may reach the screen.
    const p = newPage();
    const withCites = [0, 1, 2, 3, 4, 5].map(i => Object.assign(
      proposal('c-' + i, 'proposed', 'A plainly worded objective ' + i),
      { citations: ['demo-output/website/hlpw6/FEASIBILITY_PROBE.md',
                    'docs/LESSONS.md L-186', 'https://autocfd.org/dates/'] }));
    const html = renderDocket(p, withCites);
    check(/from the record/.test(html),
          'the "from the record" line was dropped entirely. The phrase is the ' +
          'credibility claim and must stay; only the id values go');
    check(idsIn(html).length === 0,
          `an internal id reached a visible card: ${JSON.stringify(idsIn(html))}`);

    // PLANTED CONTROL FOR THE READER ITSELF. A zero from a reader not shown
    // able to see a non-zero is not evidence. The page now WITHHOLDS a card
    // whose wording carries an id, so planting one on the real page proves
    // nothing about the reader: it renders nothing and the reader correctly
    // reports nothing. Turning the withholding OFF is what puts a leaking
    // card on screen, and only then does the reader's zero mean something.
    const leaky = mutate('const sayable = p => !INTERNAL_ID.test(',
                         'const sayable = p => true || !INTERNAL_ID.test(');
    if (leaky) {
      const planted = renderDocket(newPage(leaky), [Object.assign(
        proposal('p-0', 'proposed', 'Regrade T1b against docs/LESSONS.md L-186'),
        { citations: ['demo-output/website/hlpw6/FEASIBILITY_PROBE.md'] })]);
      const seen = idsIn(planted);
      check(seen.length >= 2 && seen.some(s => /T1b|L-186|LESSONS/.test(s)),
            `PLANTED CONTROL DEAD: with the withholding turned off, a card ` +
            `deliberately carrying "T1b" and "docs/LESSONS.md L-186" rendered ` +
            `and the id reader still saw only ${JSON.stringify(seen)}. Its zero ` +
            `on the real cards is therefore worth nothing`);
      // And the same mutant proves the WITHHOLDING is what keeps them off.
      check(/T1b/.test(planted),
            'PLANTED CONTROL DEAD: turning the withholding off did not put the ' +
            'id-carrying card on screen, so the withholding checks test nothing');
    }
  }
  // -- A CARD WHOSE OWN WORDING CARRIES AN ID IS WITHHELD, NOT REWORDED, and
  //    is still counted. Measured on the live docket: 27 of 131 open
  //    proposals name a rung, a lesson or a file in their own text, none in
  //    today's top six, so the wall was clean only by luck of the ranking.
  {
    const p = newPage();
    const props = [
      proposal('a', 'proposed', 'Solve the transonic wing and report the drag'),
      proposal('b', 'proposed', 'Regrade F5c against docs/LESSONS.md'),
      proposal('c', 'proposed', 'Check the mesh independence of the cooling duct'),
    ];
    const html = renderDocket(p, props);
    check(!/Regrade|F5c|LESSONS/.test(html),
          'a proposal naming an internal rung and a repository file was rendered ' +
          'on a visible card instead of being withheld');
    check(/transonic wing/.test(html) && /cooling duct/.test(html),
          'withholding one card took clean cards down with it');
    // Withheld is still COUNTED: 3 open, 2 sayable, so exactly 1 is not shown.
    check(/1 more proposal is open/.test(html),
          `a withheld card vanished from the count as well as the wall. Got: ` +
          JSON.stringify((html.match(/\d+ more proposal[^<]*/) || [''])[0]));
  }
  // -- THE NEGATIVE ARM ON THE FILTER ITSELF. A guard that withholds the
  //    demo's own subjects is worse than the exposure it prevents: "ONERA M6"
  //    and "B52" are letter-digit tokens and must survive.
  {
    const p = newPage();
    const legit = ['ONERA M6 wing at Mach 0.84', 'NACA 0012 finite wing',
                   'B52 external aerodynamics', 'Mach 3 cone at Re 5e6',
                   'A 25 degree Ahmed body', 'CRM wing-body at y+ below 1'];
    const html = renderDocket(p, legit.map((o, i) => proposal('L' + i, 'proposed', o)));
    for (const o of legit) {
      check(html.includes(o),
            `the id filter withheld legitimate demo wording: ${JSON.stringify(o)}. ` +
            `A filter that hides the real work is worse than the exposure it prevents`);
    }
    check(!/more proposal/.test(html),
          'six clean proposals should all be shown with nothing withheld');
  }

  // -- The live docket, when the python driver hands it in: the same zero, on
  //    the real wording rather than on a synthetic stand-in.
  if (docketArg != null) {
    const live = JSON.parse(fs.readFileSync(docketArg, 'utf8'));
    const html = renderDocket(newPage(), live.proposals || live);
    check(idsIn(html).length === 0,
          `an internal id reached a visible card on the LIVE docket: ` +
          `${JSON.stringify(idsIn(html).slice(0, 8))}`);
  }

  // -- PLANTED CONTROL: restore the uncurated wall and the checks must go red.
  const uncurated = mutate(
    "    + digest + shown.map(card).join('')",
    "    + digest + props.map(card).join('')");
  if (uncurated) {
    const p = newPage(uncurated);
    const props = [];
    for (let i = 0; i < 12; i++) props.push(proposal('open-' + i, 'proposed', 'Open item ' + i));
    for (let i = 0; i < 6; i++) props.push(proposal('done-' + i, 'done', 'Decided item ' + i));
    const html = renderDocket(p, props);
    check(/Decided item/.test(html) && cardsIn(html) > 8,
          'PLANTED CONTROL DEAD: restoring the uncurated wall did not bring the ' +
          'decided cards back, so the curation checks are not testing the wall');
  }

  // -------------------------------------- the grid reaches the stage
  // WITH ITS OWN PLANTED CONTROL. `mesh.grid` is a NEW event type, and this
  // page's `switch (t)` has no `default:` branch, so a type with no case
  // renders nothing at all and says nothing about it -- that is how 1,270 of
  // this act's events once fell through it silently. A check that can only
  // report "the label is there" proves nothing unless it has been seen to
  // report "the label is not there", so the same drive is run against a page
  // with the `mesh.grid` case removed, and THAT must fail.
  {
    // A four-cell grid, the smallest thing that is still a grid: two rows of
    // two, one wall edge and one slot edge. Real shape, trivial size.
    const grid = {
      cells: 4,
      nodes: [[0,0],[1,0],[2,0],[0,1],[1,1],[2,1],[0,2],[1,2],[2,2]],
      quads: [[0,1,4,3],[1,2,5,4],[3,4,7,6],[4,5,8,7]],
      wall: [[3,4]], slot: [[4,5]],
      bounds: [0,0,2,2], body_box: [0,0,2,2], slot_box: [0.9,0.4,1.6,1.1],
    };
    // ASYNC BECAUSE THE HANDLER IS. `loadGrid` fetches, so its work happens in
    // a microtask; a synchronous drive returns before the promise ever settles
    // and would report the handler dead when it is only unawaited.
    const drive = async src => {
      const p = newPage(src);
      p.setFetch(u => (u === '/api/grid.json' ? grid : undefined));
      p.api.dispatch({ event: 'mesh.grid', payload: {
        stage: 'meshing', url: '/api/grid.json', cells: 4,
        label: 'the grid the lift and the pressures are computed on',
        caption: 'Four cells, drawn one at a time.' } });
      for (let i = 0; i < 8; i++) { await new Promise(r => setImmediate(r)); p.drain(20000); }
      return { label: String(p.byId('viewportLabel').textContent),
               stats: String(p.byId('viewportStats').textContent),
               head: String(p.byId('viewportHead').textContent),
               gridShown: p.byId('gridCanvas').hidden === false,
               bodyShown: p.byId('viewportCanvas').hidden === false };
    };
    const got = await drive();
    check(/the grid the lift/.test(got.label),
          `the grid announcement did not reach #viewportLabel, which read ` +
          `${JSON.stringify(got.label)}`);
    check(got.stats === '4 cells',
          `the cell count did not reach #viewportStats, which read ` +
          `${JSON.stringify(got.stats)}`);
    check(got.head === 'Computational grid',
          `the panel head did not follow the stage, it read ` +
          `${JSON.stringify(got.head)}`);
    check(got.gridShown && !got.bodyShown,
          'the grid canvas is not the visible layer after mesh.grid ' +
          `(grid shown ${got.gridShown}, body shown ${got.bodyShown})`);

    // -- PLANTED CONTROL: take the case away and the four checks must go red.
    const blind = mutate("    case 'mesh.grid': enqueue('grid', p, ts); break;",
                         "    case 'mesh.grid.disabled': enqueue('grid', p, ts); break;");
    if (blind) {
      const dead = await drive(blind);
      check(!/the grid the lift/.test(dead.label) && dead.stats !== '4 cells'
            && dead.head !== 'Computational grid',
            'PLANTED CONTROL DEAD: removing the mesh.grid case still left the ' +
            'grid on the stage, so these checks are not testing the handler');
    } else {
      check(false, 'PLANTED CONTROL DEAD: the mesh.grid dispatch line could ' +
                   'not be found to mutate, so the grid checks prove nothing');
    }
  }

  // ------------------------- the rendered panel, and the count it must match
  // WHAT CHANGED AND WHY IT NEEDS A NEW CHECK. The grid used to be DRAWN here
  // from a payload sliced out of the very polyMesh directory the on-screen cell
  // count cites, so a picture of some other grid could not reach the stage
  // without the number beside it moving too. This campaign has two grids on
  // reference areas differing by a hundred, and that coupling is the guard that
  // keeps them apart. A rendered panel carries no cell list, so the coupling
  // survives as an ASSERTION instead: the panel's own provenance count, the
  // count the backend says will be printed, and the count this page ACTUALLY
  // printed must all agree, or the panel is refused.
  //
  // BOTH LIMBS ARE PLANTED. A guard exercised only against the bad case is half
  // a guard: it cannot tell "refuses a mismatch" from "renders nothing ever".
  {
    const panel = (over) => Object.assign({
      stage: 'meshing', panel: 'mesh', url: '/api/plot/demo-panels/grid.png',
      cells: 39984, printed_cells: 39984,
      label: 'the grid the numbers on this screen are computed on',
      caption: '39,984 cells.' }, over || {});
    const card = (cells) => ({ stage: 'meshing', banner: 'meshing', cells,
                               zoom: 'the wall layers at the trailing-edge slot' });
    // `events` are driven in the order given, then the queue is drained.
    const drivePanels = async (events, src) => {
      const p = newPage(src);
      p.api.resetMission();
      let t = 1000;
      for (const [event, payload] of events)
        p.api.dispatch({ event, payload, timestamp: t++ });
      for (let i = 0; i < 8; i++) { p.drain(60000); await new Promise(r => setImmediate(r)); }
      return { src: String(p.byId('viewportField').getAttribute('src') || p.byId('viewportField').src || ''),
               shown: p.byId('viewportField').hidden === false,
               empty: p.byId('viewportEmpty').hidden === false,
               emptyText: String(p.byId('viewportEmpty').textContent || ''),
               stats: String(p.byId('viewportStats').textContent),
               head: String(p.byId('viewportHead').textContent),
               label: String(p.byId('viewportLabel').textContent),
               canvas: p.byId('viewportCanvas').hidden === false,
               refused: p.api.state.panelRefused === true };
    };

    // -- LIMB ONE: the honest pair renders. Run FIRST, because a reader that
    //    has not been seen to say yes cannot be believed when it says no.
    const good = await drivePanels([
      ['demo.mesh', card('39,984 cells')],
      ['mesh.panel', panel()],
    ]);
    check(good.shown && /grid\.png$/.test(good.src),
          `the honest panel did not reach the stage (shown ${good.shown}, ` +
          `src ${JSON.stringify(good.src)})`);
    check(good.stats === '39,984 cells',
          `the panel's cell count did not reach #viewportStats, which read ` +
          `${JSON.stringify(good.stats)}`);
    check(good.head === 'Computational grid',
          `the panel head did not follow the stage: ${JSON.stringify(good.head)}`);
    check(!good.canvas,
          'the geometry canvas is still the visible layer under a rendered panel');
    check(!good.refused && !good.empty,
          'the honest pair was refused: a guard that refuses everything is ' +
          'not a guard');

    // -- LIMB TWO: a panel claiming the OTHER grid's count is REFUSED, and the
    //    refusal is VISIBLE. A guard whose failure mode is "render nothing
    //    quietly" is indistinguishable from a quiet moment.
    const bad = await drivePanels([
      ['demo.mesh', card('39,984 cells')],
      ['mesh.panel', panel({ cells: 46180, printed_cells: 46180 })],
    ]);
    check(bad.refused, 'a panel whose count is not the printed count was not refused');
    check(!bad.shown && !/grid\.png/.test(bad.src),
          `the mismatched panel is on the stage anyway (shown ${bad.shown}, ` +
          `src ${JSON.stringify(bad.src)})`);
    check(bad.empty && /disagree/.test(bad.emptyText),
          `the refusal is not on screen: the panel reads ` +
          `${JSON.stringify(bad.emptyText)}. A refusal nobody can see is an ` +
          `absence, and an absence is what hid this class of defect for months`);
    check(bad.stats === '',
          `a refused panel still prints a cell count: ${JSON.stringify(bad.stats)}`);

    // -- ORDERING MUST NOT BUY A PICTURE PAST THE GUARD. The surface panel
    //    lands beats BEFORE the meshing card prints anything, so a check that
    //    only ran when a panel arrived would never see the number.
    const late = await drivePanels([
      ['mesh.panel', panel({ panel: 'geometry', url: '/api/plot/demo-panels/surface.png',
                             cells: 46180, printed_cells: 46180 })],
      ['demo.mesh', card('39,984 cells')],
    ]);
    check(late.refused && !late.shown,
          `a panel that arrived BEFORE the count was printed stayed on screen ` +
          `once the count contradicted it (shown ${late.shown})`);

    // -- A REFUSAL BELONGS TO ONE MISSION. Left standing it would accuse the
    //    next act with the last one's sentence.
    {
      const p = newPage();
      p.api.resetMission();
      p.api.dispatch({ event: 'demo.mesh', payload: card('39,984 cells'), timestamp: 1 });
      p.api.dispatch({ event: 'mesh.panel', payload: panel({ cells: 46180, printed_cells: 46180 }), timestamp: 2 });
      for (let i = 0; i < 8; i++) { p.drain(60000); await new Promise(r => setImmediate(r)); }
      check(p.api.state.panelRefused === true, 'the refusal did not fire before the reset check');
      p.api.resetMission();
      check(p.api.state.panelRefused === false &&
            !/disagree/.test(String(p.byId('viewportEmpty').textContent)),
            `a refusal survived resetMission and would stand over the next act: ` +
            JSON.stringify(String(p.byId('viewportEmpty').textContent)));
    }

    // -- PLANTED CONTROL ON THE HANDLER ITSELF. `mesh.panel` is a new type and
    //    this page's switch sends an unknown type to a counter that draws
    //    nothing, so a case that was never added would render nothing and say
    //    nothing. Take the case away and the LIMB ONE checks must go red.
    const blind = mutate("    case 'mesh.panel': enqueue('meshPanel', p, ts); break;",
                         "    case 'mesh.panel.disabled': enqueue('meshPanel', p, ts); break;");
    if (blind) {
      const dead = await drivePanels([
        ['demo.mesh', card('39,984 cells')],
        ['mesh.panel', panel()],
      ], blind);
      check(!dead.shown && dead.stats !== '39,984 cells',
            'PLANTED CONTROL DEAD: removing the mesh.panel case still put the ' +
            'panel on the stage, so these checks are not testing the handler');
      check(dead.src === '' || !/grid\.png/.test(dead.src),
            'PLANTED CONTROL DEAD: the panel image was still loaded with no ' +
            'handler for its event');
    } else {
      check(false, 'PLANTED CONTROL DEAD: the mesh.panel dispatch line could ' +
                   'not be found to mutate, so the panel checks prove nothing');
    }

    // -- PLANTED CONTROL ON THE REFUSAL. Force the comparison to pass and the
    //    mismatched panel must render, which is what proves LIMB TWO is
    //    testing the assertion rather than some unrelated absence.
    const noGuard = mutate('function panelCountsAgree() {',
                           'function panelCountsAgree() { return true;');
    if (noGuard) {
      const leaked = await drivePanels([
        ['demo.mesh', card('39,984 cells')],
        ['mesh.panel', panel({ cells: 46180, printed_cells: 46180 })],
      ], noGuard);
      check(leaked.shown && /grid\.png/.test(leaked.src) && !leaked.refused,
            'PLANTED CONTROL DEAD: with the count assertion forced true, the ' +
            'mismatched panel STILL did not render, so the refusal check is ' +
            'not testing the assertion');
    }
  }

  // ---------------------------------- the fidelity chip may not raise a rank
  // The sixth copy of a mapping five Python surfaces have already had removed:
  // 'TREND ONLY' and 'REFERENCE REGIME MISMATCH' were rendered as
  // 'SOLVER-BACKED', which is not a rename but an upgrade. SOLVER-BACKED is the
  // UNLABELED default, so the symptom was not a wrong word on screen -- it was
  // NO WORD AT ALL, indistinguishable from an ordinary solve.
  {
    const p = newPage();
    const badge = tier => String(p.api.verdictBadge(tier) || '');
    check(/TREND ONLY/.test(badge('TREND ONLY')),
          `a TREND ONLY record renders ${JSON.stringify(badge('TREND ONLY'))}: ` +
          `the screen is still grading it as something other than what it is`);
    check(!/SOLVER-BACKED/.test(badge('TREND ONLY')) &&
          !/SOLVER-BACKED/.test(badge('REFERENCE REGIME MISMATCH')),
          'a retired grade is still being renamed onto SOLVER-BACKED, which ' +
          'is an upgrade rather than a rename');
    check(/REFERENCE REGIME MISMATCH/.test(badge('REFERENCE REGIME MISMATCH')),
          `a REFERENCE REGIME MISMATCH record renders ` +
          `${JSON.stringify(badge('REFERENCE REGIME MISMATCH'))}`);
    check(/UNCONVERGED/.test(badge('NEEDS WORK')),
          `the one legitimate rename, NEEDS WORK to UNCONVERGED, was lost: ` +
          `${JSON.stringify(badge('NEEDS WORK'))}`);
    // THE CONTROL ON THE CONTROL: a genuine SOLVER-BACKED record must still
    // render exactly as it did before, with no chip at all. A fix that put a
    // badge on everything would be as wrong as the upgrade it replaced.
    check(badge('SOLVER-BACKED') === '',
          `a genuine SOLVER-BACKED record picked up a chip it never had ` +
          `(${JSON.stringify(badge('SOLVER-BACKED'))}): the unlabeled default ` +
          `is this platform's baseline and must be left alone`);
    check(badge('VALIDATED').includes('VALIDATED'),
          'a VALIDATED record lost its chip');
    // A string this page cannot rank does not pass through wearing a grade.
    check(badge('MOSTLY FINE') === '',
          `an unranked string reached the screen as a tier: ` +
          `${JSON.stringify(badge('MOSTLY FINE'))}`);
    // THE CREDENTIALS WALL IS A DIFFERENT SURFACE. There an absent grade must
    // be WRITTEN, because a card with no chip reads as the unlabeled default,
    // which is the exact confusion that hid the upgrade on five surfaces.
    check(/TIER UNESTABLISHED/.test(String(p.api.credentialBadge(null) || '')),
          'a credential card with no establishable tier renders no words, so ' +
          'it reads as an ordinary solve');
    check(String(p.api.credentialBadge('SOLVER-BACKED') || '') === '',
          'the credentials wall started badging the baseline');
  }

  // ------------------------------------------------------- per-event cost
  // WHY THIS IS MEASURED AND NOT ARGUED. The solving stage's frames render
  // UNPACED, because the paced queue drains at 45 ms per item at its fastest
  // tier while the stage puts 1,225 events on the wire in 44.9 s -- 36.7 ms
  // each -- so the queue is structurally behind at any setting. That 36.7 ms is
  // the budget every change to a solve-frame handler is spent against, and the
  // small-multiple monitors are exactly such a change: five traces where there
  // was one. This drives real `solve.frame` payloads through the real
  // `dispatch` on the stub DOM and reports the mean cost of one, so the claim
  // "it still fits" is a number rather than an opinion.
  //
  // WHAT IT DOES NOT MEASURE, said plainly: this box executes no layout and no
  // rasterisation, so the figure is the page's JavaScript cost per event and
  // nothing else. It is a floor, not a frame budget.
  if (benchFrames > 0) {
    const p = newPage();
    const points = 5, per = Math.max(1, Math.round(benchFrames / points));
    const labels = [];
    for (let i = 0; i < points; i++) labels.push('blowing ' + (i * 0.1).toFixed(1));
    p.api.dispatch({ event: 'solve.begin',
                     payload: { stage: 'solving', points, labels,
                                iterations_per_point: labels.map(() => per * 4) } });
    // Built before the clock starts: the cost under test is the page's, not
    // this harness's object construction.
    const frames = [];
    for (let k = 1; k <= per; k++) {
      for (let i = 0; i < points; i++) {
        frames.push({ event: 'solve.frame', payload: {
          stage: 'solving', point_index: i + 1, points, label: labels[i],
          iteration: k * 4, iterations: per * 4, elapsed_s: k * 0.5,
          residuals: { p: Math.pow(10, -1 - 4 * k / per), Ux: 1e-4, Uy: 1e-5 },
          coefficients: { Cl: 0.4 + 0.1 * i + 0.01 * Math.sin(k / 7) },
          envelope: {}, source_row: k } });
      }
    }
    // THE CLOCK IS ADVANCED BETWEEN EVENTS, 36.7 ms, THE REAL ARRIVAL GAP.
    // Dispatching the whole burst synchronously would be the wrong measurement
    // and flatteringly so: a page that defers its draw to an animation frame
    // would coalesce 1,225 events into ONE draw, which is not what happens on a
    // screen where the frames arrive 36.7 ms apart. Stepping the virtual clock
    // makes every scheduled animation frame and every queue beat run in its
    // place, so the figure includes the drawing the events actually cause.
    const t0 = process.hrtime.bigint();
    for (const f of frames) { p.api.dispatch(f); p.advance(36.7); }
    p.drain(1000);
    const ms = Number(process.hrtime.bigint() - t0) / 1e6;
    console.log(`per-event cost: ${frames.length} solve.frame events over ` +
                `${points} points, ${ms.toFixed(1)} ms total, ` +
                `${(ms / frames.length).toFixed(3)} ms per event ` +
                `(budget 36.7 ms; JavaScript only, no layout on this box)`);
  }

  // ---------------------------------------------------------------- report
  if (failures.length) {
    console.error('CONTROL ROOM PACING FAILURES:');
    for (const f of failures) console.error('  * ' + f);
    process.exit(1);
  }
  console.log('control room pacing: all checks passed');
})();
