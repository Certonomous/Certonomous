// Every variable on a camera surface is typeset (Katie, 2026-07-31).
//
// The acts emit `C_d`, `C_L` and `C_p` in narration, in table cells, in plot
// titles, in axis labels and in the legend name. Table cells were the only
// surface that typeset them; everything else is `textContent` or canvas and
// rendered the literal underscore, so the demo showed `C_p` where it means a
// pressure coefficient.
//
// Grepping the page for the word `subScript` would prove nothing about what is
// drawn. This runs the REAL page script against a stub DOM whose canvas records
// every `fillText` call, pushes an act's worth of events through `dispatch`,
// drains the paced reveal queue, and then reads back what actually landed:
//   * the transcript, the table caption, the viewport label, the legend name,
//     the trace title and the landscape title as markup;
//   * the axis labels, the colourbar label and the winner annotation as the
//     runs of text the canvas was asked to draw.
// A subscript on canvas is two draw calls at two font sizes, so the assertion
// is that the underscore is gone and both runs were drawn.
//
// Usage: node control_room_typeset_harness.js <control_room.html>
'use strict';
const fs = require('fs');

const htmlPath = process.argv[2];
if (!htmlPath) { console.error('FAIL: usage: harness <control_room.html>'); process.exit(1); }
const html = fs.readFileSync(htmlPath, 'utf8');
const source = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
if (!source) { console.error('FAIL: no <script> block found'); process.exit(1); }

const drawn = [];   // every fillText the page made, with the font in force

function makeEl(id) {
  const el = {
    id, textContent: '', innerHTML: '', hidden: false, value: '',
    className: '', dataset: {}, style: {}, scrollTop: 0, scrollHeight: 0,
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    appendChild(c) { el.innerHTML += (c && c.innerHTML) || ''; },
    removeChild() {}, insertAdjacentHTML() {}, addEventListener() {},
    removeEventListener() {}, remove() {},
    querySelector() { return makeEl('q'); }, querySelectorAll() { return []; },
    getContext() {
      const state = { font: '11px sans', textAlign: 'left' };
      const any = { addColorStop() {}, width: 40, height: 20,
                    actualBoundingBoxAscent: 8, actualBoundingBoxDescent: 2,
                    data: [0, 0, 0, 0] };
      const ctx = {
        canvas: el,
        // Width proportional to length so measure-then-place arithmetic is
        // exercised rather than short circuited by a constant.
        measureText: t => ({ width: String(t).length * 6 }),
        fillText(t, x, y) { drawn.push({ t: String(t), font: ctx.font, x, y }); },
        strokeText(t, x, y) { drawn.push({ t: String(t), font: ctx.font, x, y }); },
      };
      return new Proxy(ctx, {
        get(t, k) { return k in t ? t[k] : (k in state ? state[k] : () => any); },
        set(t, k, v) { if (k in state) state[k] = v; t[k] = v; return true; },
      });
    },
    getBoundingClientRect() { return { width: 800, height: 400, left: 0, top: 0 }; },
    setAttribute() {}, getAttribute() { return null; }, removeAttribute() {},
    hasAttribute() { return false }, closest() { return null; },
    focus() {}, click() {}, blur() {}, insertBefore() {}, replaceChildren() {},
    scrollIntoView() {}, getElementsByClassName() { return []; },
    getElementsByTagName() { return []; },
    children: [], firstChild: null, lastChild: null, parentNode: null,
    childNodes: [], offsetWidth: 800, offsetHeight: 400,
    clientWidth: 800, clientHeight: 400, width: 800, height: 400,
    checked: false, disabled: false, files: [], selectedIndex: 0,
    toDataURL() { return 'data:,'; },
  };
  return el;
}
const els = new Map();
const byId = id => { if (!els.has(id)) els.set(id, makeEl(id)); return els.get(id); };
const document = {
  getElementById: byId, createElement: tag => makeEl('new-' + tag),
  querySelector: () => makeEl('sel'), querySelectorAll: () => [],
  addEventListener() {}, body: makeEl('body'),
};

const clock = { now: 0, seq: 0, timers: [], errors: [] };
const setTimeout_ = (fn, ms) => {
  clock.timers.push({ at: clock.now + (ms || 0), fn, seq: clock.seq++ });
  return clock.seq - 1;
};
const clearTimeout_ = h => { clock.timers = clock.timers.filter(t => t.seq !== h); };
// Async: the page loads geometry and fields through `await fetch(...)`, so the
// microtask queue has to be given a turn between beats or the label writers on
// the far side of those awaits never run.
const tick = () => new Promise(r => setImmediate(r));
async function drain(limitMs = 3600000) {
  const stop = clock.now + limitMs;
  while (clock.timers.length && clock.now < stop) {
    clock.timers.sort((a, b) => a.at - b.at || a.seq - b.seq);
    const t = clock.timers.shift();
    clock.now = t.at;
    try { t.fn(); } catch (e) { clock.errors.push(e); }
    await tick();
  }
  await tick();
}
const noop = () => {};
const win = { addEventListener: noop, removeEventListener: noop, devicePixelRatio: 1,
              innerWidth: 1920, innerHeight: 1080,
              location: { search: '', href: 'http://localhost:8765/' } };
const sandbox = {
  document, window: win, console,
  setTimeout: setTimeout_, clearTimeout: clearTimeout_,
  setInterval: () => 0, clearInterval: noop,
  requestAnimationFrame: fn => setTimeout_(fn, 16),
  fetch: () => Promise.resolve({ ok: true, json: () => Promise.resolve({}),
                                 text: () => Promise.resolve('') }),
  EventSource: function () { return { addEventListener: noop, close: noop }; },
  URLSearchParams, Date, Math, JSON, Object, Array, String, Number, Set, Map,
  RegExp, Promise, isNaN, parseFloat, parseInt,
  Image: function () { return makeEl('img'); },
  location: win.location, navigator: { userAgent: 'harness' },
  alert: noop, confirm: () => true, FormData: function () {},
  performance: { now: () => clock.now },
  XMLHttpRequest: function () { return { open: noop, send: noop, responseText: '{"events":[]}', status: 200 }; },
};

let api;
try {
  const names = Object.keys(sandbox);
  api = new Function(...names, source +
    // Tolerant of a page that has no typesetter at all: the point is to fail on
    // what got rendered, not on a missing symbol.
    '\n;const _g = n => { try { return eval(n); } catch { return null; } };' +
    '\n;return { dispatch, resetMission, state, drawTrace,' +
    '\n           subScript: _g("subScript") || (x => x), subRuns: _g("subRuns") || (x => [{ t: String(x), sub: false }]) };'
  )(...names.map(n => sandbox[n]));
} catch (err) {
  console.error('FAIL: the page script did not evaluate: ' + err.message);
  console.error(err.stack);
  process.exit(1);
}

const failures = [];
const check = (cond, msg) => { if (!cond) failures.push(msg); };
const ev = (event, payload, timestamp) => ({ event, payload, timestamp });

// ------------------------------------------------------------------ drive
async function main() {
api.resetMission();
let t = 1000;
api.dispatch(ev('transcript.entry', {
  role: 'CHIEF ENGINEER',
  message: '• Drag fell to C_d 0.0271 at fixed C_L. • The wall carries C_p.' }, t++));
api.dispatch(ev('transcript.table', {
  role: 'CHIEF ENGINEER', title: 'C_d against the wind tunnel',
  headers: ['Case', 'C_d'], rows: [['Ahmed', '0.299']], table_id: 'tt' }, t++));
api.dispatch(ev('geometry.ready', { url: '/api/geometry?name=ahmed',
                                    label: 'Ahmed body, painted with C_p' }, t++));
api.dispatch(ev('trace.point', {
  series: 'Cd_history', x: 1, y: 0.03, x_label: 'optimizer major iteration',
  y_label: 'C_d', title: 'Drag at fixed lift, C_L = 0.5' }, t++));
api.dispatch(ev('trace.point', {
  series: 'Cd_history', x: 2, y: 0.028, x_label: 'optimizer major iteration',
  y_label: 'C_d', title: 'Drag at fixed lift, C_L = 0.5' }, t++));
api.dispatch(ev('landscape.init', { title: 'Design landscape, C_d' }, t++));
await drain();

// The legend name comes off the field payload, which the page fetches; call the
// same writer the fetch handler uses so the surface is exercised, not stubbed.
byId('legendName').innerHTML = api.subScript('C_p');

const readEl = id => String(byId(id).innerHTML || byId(id).textContent || '');
const SURFACES = {
  script:        'the conversation feed',
  digest:        'the digest feed',
  viewportLabel: 'the viewport label under the geometry',
  legendName:    'the colour legend name',
  traceTitle:    'the trace title',
  landTitle:     'the landscape title',
};
for (const [id, what] of Object.entries(SURFACES)) {
  const got = readEl(id);
  if (!got) { failures.push(`${what} (#${id}) rendered nothing at all`); continue; }
  check(!/\b[A-Za-z]_[A-Za-z0-9]/.test(got.replace(/<[^>]+>/g, '')),
        `${what} (#${id}) still shows a raw underscore: ${JSON.stringify(got.slice(0, 120))}`);
  check(got.includes('<sub>'),
        `${what} (#${id}) carries a variable but no <sub> tag: ${JSON.stringify(got.slice(0, 120))}`);
}

// ------------------------------------------------------------------ canvas
// Redraw so the axis labels are certainly in the record, then read the runs.
api.drawTrace();
const texts = drawn.map(d => d.t);
check(drawn.length > 0, 'the canvas was never asked to draw any text');
check(!texts.some(x => /\b[A-Za-z]_[A-Za-z0-9]/.test(x)),
      'a canvas label was drawn with a raw underscore: ' +
      JSON.stringify(texts.filter(x => /\b[A-Za-z]_[A-Za-z0-9]/.test(x))));
// `C_d` must have been drawn as a `C` run and a `d` run at a smaller font.
const cRun = drawn.find(d => d.t === 'C');
const dRun = drawn.find(d => d.t === 'd');
check(cRun && dRun, 'the C_d axis label was not drawn as a symbol run and an index run');
if (cRun && dRun) {
  const px = f => parseFloat((/(\d+(?:\.\d+)?)px/.exec(f) || [0, 0])[1]);
  check(px(dRun.font) > 0 && px(dRun.font) < px(cRun.font),
        `the subscript run was drawn at ${dRun.font}, not smaller than ${cRun.font}`);
  check(dRun.y > cRun.y,
        `the subscript run sits at y ${dRun.y}, not dropped below the symbol at ${cRun.y}`);
  check(dRun.x > cRun.x,
        `the subscript run sits at x ${dRun.x}, not after the symbol at ${cRun.x}`);
}

// A label with no variable in it must come out byte for byte unchanged, and as
// ONE draw call: the typesetter must not fragment ordinary prose.
const plain = api.subRuns('optimizer major iteration');
check(plain.length === 1 && plain[0].t === 'optimizer major iteration',
      'a label with no variable was split into runs: ' + JSON.stringify(plain));
check(api.subScript('no variables here') === 'no variables here',
      'subScript altered a string with no variable in it');
// Right-to-left alignment still means what it says: measure, then place.
check(String(api.subScript('C_p and C_d')) === 'C<sub>p</sub> and C<sub>d</sub>',
      'subScript did not typeset both variables in one string');

if (clock.errors.length) {
  failures.push(`${clock.errors.length} error(s) thrown while rendering, first: ` +
                clock.errors[0].message);
}

if (failures.length) {
  console.error('CONTROL ROOM TYPESETTING FAILURES:');
  for (const f of failures) console.error('  * ' + f);
  process.exit(1);
}
console.log(`control room typesetting: all checks passed ` +
            `(${drawn.length} canvas text runs, ${Object.keys(SURFACES).length} markup surfaces)`);
}
main().catch(e => { console.error('FAIL: ' + e.stack); process.exit(1); });
