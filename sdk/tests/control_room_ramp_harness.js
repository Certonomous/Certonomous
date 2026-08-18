// The Cp colour ramp is anchored at zero, and pressure is untouched.
//
// WHY THIS EXISTS. The painted values arrive normalised to 0..1 across a
// clipped percentile window, and the page's diverging ramp puts its neutral off
// white stop at the MIDDLE of that window. On a signed coefficient that is the
// wrong place: every body's suction is deeper than its stagnation, so Cp = 0
// landed at 59% of the ramp on the Ahmed body, 62% on the B-52 and 74% on the
// hump, and undisturbed flow rendered warm. Warm reads as "something is
// happening here" where nothing is.
//
// Reading the page source would not show what a body is painted. This harness
// evaluates the REAL page script against a stub DOM whose canvas RECORDS every
// fillStyle it is given, hands the page the real recorded field payloads off
// disk through a stubbed fetch, and reads back the colours the triangles were
// actually filled with. It reports, per body, where Cp = 0 sits on the ramp and
// what colour the face nearest Cp = 0 was painted.
//
// It also proves the other half: a PRESSURE payload has to come out byte for
// byte identical to the page before the change. Pressure is a solver quantity
// in its own units whose zero is a gauge against an arbitrary reference, so it
// keeps its linear window. The comparison is against a reference page given on
// the command line, colour string for colour string, over every triangle.
//
// Usage:
//   node control_room_ramp_harness.js <control_room.html> [--reference <old.html>]
//   node control_room_ramp_harness.js <control_room.html> --write-golden
//
// With no --reference the pressure half is checked against a golden digest of
// the colour sequence, taken from the page as it stood before the change. That
// is the pin the test suite carries: it needs no second copy of the page, and
// one different colour on one triangle of one body breaks it.
'use strict';
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const argv = process.argv.slice(2);
const htmlPath = argv[0];
if (!htmlPath) { console.error('FAIL: usage: harness <control_room.html> [--reference old.html]'); process.exit(1); }
let referencePath = null, writeGolden = false;
for (let i = 1; i < argv.length; i++) {
  if (argv[i] === '--reference') referencePath = argv[++i];
  if (argv[i] === '--write-golden') writeGolden = true;
}
const GOLDEN = path.join(__dirname, 'fixtures', 'pressure_paint_golden.json');
const digest = fills => crypto.createHash('sha256').update(fills.join('|')).digest('hex');

const REPO = path.resolve(__dirname, '..', '..');
const CP_BODIES = [
  ['hump',  'mission-output/nasa-hump/nasa_hump_field.json'],
  ['ahmed', 'mission-output/ahmed-body/ahmed_25_field.json'],
  ['b52',   'mission-output/geometry-study/b52_field.json'],
];
const PRESSURE_BODIES = [
  // R11 moved `demo-output/plots/` to `media/plots/` at MOVE_MAP batch 4.
  // Shell and JS cannot import `scripts/lab_paths.py`, so this is the one
  // place the prefix is still spelled -- and it is spelled once.
  ['b52 pressure',       'media/plots/pressure_slices/validation/regenerated/b52_field.json'],
  ['motorBike pressure', 'media/plots/pressure_slices/validation/regenerated/motorBike_field.json'],
  ['cube pressure',      'mission-output/geometry-study/cube_field.json'],
];

// ---------------------------------------------------------------- the page
function newPage(source) {
  const fills = [];   // every fillStyle the page assigned while painting
  function makeEl(id) {
    const el = {
      id, textContent: '', innerHTML: '', hidden: false, value: '',
      className: '', dataset: {}, style: {}, scrollTop: 0, scrollHeight: 0,
      classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
      appendChild() {}, removeChild() {}, insertAdjacentHTML() {},
      addEventListener() {}, removeEventListener() {}, remove() {},
      querySelector() { return makeEl('q'); }, querySelectorAll() { return []; },
      getContext() {
        const any = { addColorStop() {}, width: 40, height: 20,
                      actualBoundingBoxAscent: 8, actualBoundingBoxDescent: 2,
                      data: [0, 0, 0, 0] };
        const store = { fillStyle: '', strokeStyle: '', font: '11px sans',
                        textAlign: 'left', globalAlpha: 1, lineWidth: 1 };
        const ctx = {
          canvas: el, measureText: t => ({ width: String(t).length * 6 }),
          // A fill is only counted when it actually lands on the canvas, so the
          // record is the sequence of colours the body was painted with.
          fill() { fills.push(store.fillStyle); },
        };
        return new Proxy(ctx, {
          get(t, k) { return k in t ? t[k] : (k in store ? store[k] : () => any); },
          set(t, k, v) { if (k in store) store[k] = v; else t[k] = v; return true; },
        });
      },
      getBoundingClientRect() { return { width: 800, height: 400, left: 0, top: 0 }; },
      setAttribute() {}, getAttribute() { return null; }, removeAttribute() {},
      hasAttribute() { return false; }, closest() { return null; },
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
  const legendBar = makeEl('legend-bar');
  const document = {
    getElementById: byId, createElement: tag => makeEl('new-' + tag),
    querySelector: sel => (sel === '#legend .bar' ? legendBar : makeEl('sel')),
    querySelectorAll: () => [], addEventListener() {}, body: makeEl('body'),
  };
  const clock = { now: 0, seq: 0, timers: [], errors: [] };
  const setTimeout_ = (fn, ms) => {
    clock.timers.push({ at: clock.now + (ms || 0), fn, seq: clock.seq++ });
    return clock.seq - 1;
  };
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
  let served = null;   // the payload the next fetch answers with
  const noop = () => {};
  const win = { addEventListener: noop, removeEventListener: noop, devicePixelRatio: 1,
                innerWidth: 1920, innerHeight: 1080,
                location: { search: '', href: 'http://localhost:8765/' } };
  const sandbox = {
    document, window: win, console,
    setTimeout: setTimeout_, clearTimeout: h => { clock.timers = clock.timers.filter(t => t.seq !== h); },
    setInterval: () => 0, clearInterval: noop,
    requestAnimationFrame: fn => setTimeout_(fn, 16),
    fetch: () => Promise.resolve({ ok: true, json: () => Promise.resolve(served),
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
      '\n;return { dispatch, resetMission, state, drawGeometry, coolwarm };'
    )(...names.map(n => sandbox[n]));
  } catch (err) {
    console.error('FAIL: the page script did not evaluate: ' + err.message);
    console.error(err.stack);
    process.exit(1);
  }
  return { api, byId, legendBar, fills, drain, serve: v => { served = v; }, clock };
}

// Paint one body and hand back the colours it was painted with, plus whatever
// the page left on the field after loading it.
async function paint(source, payload) {
  const p = newPage(source);
  p.api.resetMission();
  p.serve(JSON.parse(JSON.stringify(payload)));
  p.api.dispatch({ event: 'field.ready',
                   payload: { url: '/api/field/x/y.json', label: 'body' },
                   timestamp: 1 });
  await p.drain();
  return { fills: p.fills.slice(), field: (p.api.state.mesh || {}).field || null,
           legend: p.legendBar.style.background || '', errors: p.clock.errors };
}

const failures = [];
const check = (cond, msg) => { if (!cond) failures.push(msg); };
const read = rel => JSON.parse(fs.readFileSync(path.join(REPO, rel), 'utf8'));

(async () => {
  const source = [...fs.readFileSync(htmlPath, 'utf8')
    .matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
  const refSource = referencePath
    ? [...fs.readFileSync(referencePath, 'utf8')
        .matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n')
    : null;

  // ------------------------------------------------------- Cp, anchored
  console.log('Cp bodies — where Cp = 0 sits on the ramp');
  for (const [name, rel] of CP_BODIES) {
    const payload = read(rel);
    const raw = payload.field;
    const lo = Number(raw.color_min), hi = Number(raw.color_max);
    const before = -lo / (hi - lo);        // the linear window's position for 0
    const r = await paint(source, payload);
    check(r.errors.length === 0,
          `${name}: ${r.errors.length} error(s) while painting, first: ` +
          (r.errors[0] && r.errors[0].message));
    check(r.field && Array.isArray(r.field.values),
          `${name}: the page never loaded a field`);
    if (!r.field) continue;
    check(r.fills.length > 0, `${name}: no triangle was ever filled`);

    // Measure the mapping the page actually used. The control is the SAME page
    // fed the SAME body with the `cp` marker taken off, which is the linear
    // window it has always drawn; both runs go through the same display-only
    // island drop, so face i of one is face i of the other. Face i's Cp is read
    // off the control, and its ramp position off the anchored run.
    const span = hi - lo;
    const flat = JSON.parse(JSON.stringify(payload));
    delete flat.field.quantity;
    const c = await paint(source, flat);
    check(c.field && c.field.values.length === r.field.values.length,
          `${name}: the control render painted a different number of faces`);
    const pairs = (c.field ? c.field.values : []).map((t, i) => ({
      cp: lo + Math.max(0, Math.min(1, Number(t))) * span,
      ramp: Number(r.field.values[i]),
    })).filter(q => Number.isFinite(q.cp) && Number.isFinite(q.ramp))
       .sort((a, b) => a.cp - b.cp);
    // The control must be the untouched linear window, or the comparison is
    // measuring the change against itself.
    check(c.field && c.field.ramp_anchor === undefined,
          `${name}: the control render was anchored too, so it is no control`);
    // Straddle zero and interpolate: this is where the ramp puts undisturbed flow.
    let after = null;
    for (let i = 1; i < pairs.length; i++) {
      if (pairs[i - 1].cp <= 0 && pairs[i].cp >= 0) {
        const d = pairs[i].cp - pairs[i - 1].cp;
        after = d === 0 ? pairs[i].ramp
              : pairs[i - 1].ramp + (0 - pairs[i - 1].cp) / d * (pairs[i].ramp - pairs[i - 1].ramp);
        break;
      }
    }
    // And the colour the nearest-to-zero face was actually painted.
    const nearest = pairs.reduce((a, b) => Math.abs(b.cp) < Math.abs(a.cp) ? b : a);
    const neutral = r.field ? String((await paintColour(source, nearest.ramp))) : '';
    console.log(`  ${name.padEnd(6)} window [${lo}, ${hi}]  ` +
      `Cp=0 was at ${(before * 100).toFixed(1)}% of the ramp, now at ` +
      `${after == null ? 'n/a' : (after * 100).toFixed(1) + '%'}  ` +
      `(nearest face Cp ${nearest.cp.toFixed(5)} paints ${neutral})`);
    check(after != null && Math.abs(after - 0.5) < 0.005,
          `${name}: Cp = 0 sits at ${after == null ? 'n/a' : (after * 100).toFixed(1) + '%'} ` +
          `of the ramp, not the neutral midpoint`);
    // The ends still reach the ends: nothing is squeezed off the ramp.
    check(Math.min(...pairs.map(q => q.ramp)) < 0.001,
          `${name}: the deepest suction no longer reaches the cool end of the ramp`);
    check(Math.max(...pairs.map(q => q.ramp)) > 0.999,
          `${name}: the highest pressure no longer reaches the warm end of the ramp`);
    // Monotone in Cp: the mapping is still a ramp, not a fold.
    let monotone = true;
    for (let i = 1; i < pairs.length; i++) if (pairs[i].ramp < pairs[i - 1].ramp - 1e-9) monotone = false;
    check(monotone, `${name}: the anchored ramp is not monotone in Cp`);
    // The legend bar has to move its stops with the paint, or the labels lie.
    check(/linear-gradient/.test(r.legend) && r.legend.includes('#f2f2f2'),
          `${name}: the legend bar was not re-stopped for the anchored ramp: ` +
          JSON.stringify(r.legend));
    const stop = /#f2f2f2\s+([\d.]+)%/.exec(r.legend);
    check(stop && Math.abs(parseFloat(stop[1]) / 100 - before) < 0.005,
          `${name}: the legend's neutral stop sits at ${stop ? stop[1] : 'n/a'}%, ` +
          `not at the value position of zero (${(before * 100).toFixed(1)}%)`);
  }

  // -------------------------------------------- pressure, byte identical
  if (refSource) {
    console.log('Pressure bodies — against the reference page');
    for (const [name, rel] of PRESSURE_BODIES) {
      const payload = read(rel);
      const now = await paint(source, payload);
      const ref = await paint(refSource, payload);
      check(ref.fills.length > 0, `${name}: the reference page painted nothing`);
      check(now.fills.length === ref.fills.length,
            `${name}: ${now.fills.length} triangles painted, reference painted ${ref.fills.length}`);
      let first = -1;
      const n = Math.min(now.fills.length, ref.fills.length);
      for (let i = 0; i < n; i++) if (now.fills[i] !== ref.fills[i]) { first = i; break; }
      check(first === -1,
            `${name}: triangle ${first} paints ${now.fills[first]} but the reference ` +
            `painted ${ref.fills[first]}: pressure rendering changed`);
      console.log(`  ${name.padEnd(19)} ${now.fills.length} triangles, ` +
        `${first === -1 ? 'byte for byte identical to the reference' : 'DIFFERS at ' + first}` +
        `, legend bar ${now.legend === ref.legend ? 'unchanged' : 'CHANGED'}`);
      check(now.legend === ref.legend,
            `${name}: the legend bar gradient changed on a pressure field`);
    }
  } else {
    // The golden digest of the colour sequence, taken from the page before the
    // Cp change. Pressure must still paint exactly this.
    console.log('Pressure bodies — against the checked in golden digest');
    const golden = writeGolden ? {} : JSON.parse(fs.readFileSync(GOLDEN, 'utf8'));
    for (const [name, rel] of PRESSURE_BODIES) {
      const now = await paint(source, read(rel));
      const got = { triangles: now.fills.length, sha256: digest(now.fills),
                    legend: now.legend };
      if (writeGolden) { golden[name] = got; console.log(`  ${name.padEnd(19)} ${got.triangles} triangles, ${got.sha256.slice(0, 16)}…`); continue; }
      const want = golden[name];
      check(!!want, `${name}: no golden entry to compare against`);
      if (!want) continue;
      check(got.triangles === want.triangles,
            `${name}: ${got.triangles} triangles painted, golden has ${want.triangles}`);
      check(got.sha256 === want.sha256,
            `${name}: the painted colour sequence is ${got.sha256.slice(0, 16)}…, ` +
            `golden is ${want.sha256.slice(0, 16)}…: pressure rendering changed`);
      check(got.legend === want.legend,
            `${name}: the legend bar gradient changed on a pressure field`);
      console.log(`  ${name.padEnd(19)} ${got.triangles} triangles, ` +
        `${got.sha256 === want.sha256 ? 'byte for byte identical to the golden' : 'DIFFERS'}` +
        `, legend bar ${got.legend === want.legend ? 'unchanged' : 'CHANGED'}`);
    }
    if (writeGolden) {
      fs.writeFileSync(GOLDEN, JSON.stringify(golden, null, 2) + '\n');
      console.log('wrote ' + GOLDEN);
      return;
    }
  }

  if (failures.length) {
    console.error('CP RAMP FAILURES:');
    for (const f of failures) console.error('  * ' + f);
    process.exit(1);
  }
  console.log('cp ramp: all checks passed');
})();

// The page's own colour lookup, asked directly, so the reported colour at
// Cp = 0 is the page's answer and not this file's opinion of it.
async function paintColour(source, t) {
  const p = newPage(source);
  return p.api.coolwarm(t);
}
