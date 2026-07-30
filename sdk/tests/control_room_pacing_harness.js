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
// Usage: node control_room_pacing_harness.js <path to control_room.html>
'use strict';
const fs = require('fs');

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, 'utf8');

// ---- extract the page script -------------------------------------------
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (!scripts.length) { console.error('FAIL: no <script> block found'); process.exit(1); }
const source = scripts.join('\n');

// ---- stub DOM ------------------------------------------------------------
// Every element is a bag of properties that records what was written to it.
// Nothing is rendered; the only thing under test is which values land when.
function makeEl(id) {
  const el = {
    id, textContent: '', innerHTML: '', hidden: false, value: '',
    className: '', dataset: {}, style: {}, scrollTop: 0, scrollHeight: 0,
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    appendChild() {}, removeChild() {}, insertAdjacentHTML() {},
    addEventListener() {}, removeEventListener() {}, remove() {},
    querySelector() { return makeEl('q'); },
    querySelectorAll() { return []; },
    getContext() {
      return new Proxy({}, { get: () => () => {}, set: () => true });
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

// ---- virtual clock -------------------------------------------------------
// setTimeout callbacks queue by due time; `tick()` runs everything due so the
// test can step the reveal queue one beat at a time and read the KPI row
// between beats. That mid-flight read is the whole point.
let now = 0;
let seq = 0;
let timers = [];
const setTimeout_ = (fn, ms) => {
  const t = { at: now + (ms || 0), fn, seq: seq++ };
  timers.push(t);
  return t.seq;
};
const clearTimeout_ = handle => { timers = timers.filter(t => t.seq !== handle); };
function advance(ms) {
  const until = now + ms;
  for (;;) {
    timers.sort((a, b) => a.at - b.at || a.seq - b.seq);
    const next = timers[0];
    if (!next || next.at > until) break;
    timers.shift();
    now = next.at;
    next.fn();
  }
  now = until;
}
function drain(limitMs = 600000) {
  const stop = now + limitMs;
  while (timers.length && now < stop) {
    timers.sort((a, b) => a.at - b.at || a.seq - b.seq);
    const next = timers.shift();
    now = next.at;
    next.fn();
  }
}

// ---- remaining globals the page touches ---------------------------------
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
  performance: { now: () => now },
};

// Run the page script and hand back the two entry points the test drives.
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

// ---- assertions ----------------------------------------------------------
const failures = [];
function check(cond, msg) { if (!cond) failures.push(msg); }
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
for (let i = 0; i < 200 && (api.revealQ.length || timers.length); i++) {
  advance(100);
  if (kWorkers() !== last) { order.push(api.revealQ.length); last = kWorkers(); }
}
check(order.length === 1,
      `the worker numeral changed ${order.length} times for one worker event`);
check(order[0] === 1,
      `the worker numeral moved with ${order[0]} items still queued, expected 1 ` +
      `(the second narration beat), which is what "in lockstep" means`);

// ---------------------------------------------------------------- report
if (failures.length) {
  console.error('CONTROL ROOM PACING FAILURES:');
  for (const f of failures) console.error('  * ' + f);
  process.exit(1);
}
console.log('control room pacing: all checks passed');
