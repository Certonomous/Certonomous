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
    // The golden pins the PROPERTIES of the painted surface, not the order the
    // triangles happened to be drawn in. See the header of `surfaceEvidence`
    // and the `_why` block inside the fixture for what each clause is for.
    console.log('Pressure bodies — against the checked in golden invariants');
    const file = writeGolden ? { bodies: {} }
                             : JSON.parse(fs.readFileSync(GOLDEN, 'utf8'));
    const golden = file.bodies || {};
    const instrumented = instrument(source);
    for (const [name, rel] of PRESSURE_BODIES) {
      const now = await paintFacets(instrumented, read(rel));
      // PLANTED CONTROL: a reader that sees nothing must refuse, not pass. If
      // the injection stopped firing, every geometry clause below would be
      // vacuously true and this harness would go green on anything.
      check(now.facets.length > 0,
            `${name}: the paint-loop probe recorded no facet — the geometry ` +
            `clauses would be vacuous, so this is a refusal, not a pass`);
      if (!now.facets.length) continue;
      const paintedCount = now.facets.filter(t => t.kept).length;
      check(paintedCount === now.fills.length,
            `${name}: the probe counted ${paintedCount} painted facets but the ` +
            `canvas recorded ${now.fills.length} fills — the probe is not ` +
            `watching the paint that reaches the screen`);
      const ev = now.cullSense ? surfaceEvidence(now.facets) : null;
      const got = {
        facets: now.facets.length,
        painted: paintedCount,
        cull_sense: now.cullSense,
        distinct_colours: new Set(now.fills).size,
        // Order-independent by construction: this survives a re-sort of the
        // paint and still pins every colour and how many facets carry it.
        colour_multiset_sha256: digest([...now.fills].sort()),
        legend: now.legend,
        surface: ev && { silhouette_cells: ev.covered,
                         silhouette_cells_lost: ev.lost,
                         nearest_facet_is_painted: ev.nearestPainted,
                         disagreements_on_silhouette_edge: ev.edge,
                         disagreements_interior: ev.interior,
                         worst_depth_margin_pct: ev.worstMarginPct },
      };
      if (writeGolden) {
        golden[name] = got;
        console.log(`  ${name.padEnd(19)} ${got.painted}/${got.facets} painted, ` +
          `cullSense ${got.cull_sense}, ${got.colour_multiset_sha256.slice(0,16)}…`);
        continue;
      }
      const want = golden[name];
      check(!!want, `${name}: no golden entry to compare against`);
      if (!want) continue;
      // 1. CULLING IS ONLY EVER APPLIED TO A BODY MEASURED CLOSED AND
      //    CONSISTENTLY WOUND. b52 and motorBike are not; a change that starts
      //    culling them is dropping geometry from an open shell.
      check(got.cull_sense === want.cull_sense,
            `${name}: cullSense is ${got.cull_sense}, golden has ${want.cull_sense}` +
            (want.cull_sense === 0
              ? ' — this body is NOT measured closed and must never be culled'
              : ' — the measured cull sense of a closed body changed'));
      check(got.facets === want.facets,
            `${name}: ${got.facets} facets projected, golden has ${want.facets}: ` +
            `the geometry itself changed, not the painting of it`);
      check(got.painted === want.painted,
            `${name}: ${got.painted} facets painted, golden has ${want.painted}`);
      // 2. THE COLOUR MAPPING. Order-independent, so a legitimate re-sort
      //    cannot red this, but a changed ramp or window will.
      check(got.colour_multiset_sha256 === want.colour_multiset_sha256,
            `${name}: the painted colour multiset is ` +
            `${got.colour_multiset_sha256.slice(0,16)}…, golden is ` +
            `${want.colour_multiset_sha256.slice(0,16)}…: the pressure colour ` +
            `mapping changed (this is NOT sensitive to paint order)`);
      check(got.distinct_colours === want.distinct_colours,
            `${name}: ${got.distinct_colours} distinct colours, golden has ` +
            `${want.distinct_colours}`);
      check(got.legend === want.legend,
            `${name}: the legend bar gradient changed on a pressure field`);
      if (want.surface) {
        const s = got.surface, w = want.surface;
        check(!!s, `${name}: the golden expects a culled body and nothing was culled`);
        if (s) {
          // 3. THE BODY IS STILL FULLY DRAWN.
          check(s.silhouette_cells_lost === 0,
                `${name}: culling lost ${s.silhouette_cells_lost} silhouette cells ` +
                `— the body is not fully drawn any more`);
          check(s.silhouette_cells === w.silhouette_cells,
                `${name}: the body covers ${s.silhouette_cells} cells, golden has ` +
                `${w.silhouette_cells}: the projected size of the body changed`);
          // 4. AND IT IS THE HALF FACING THE CAMERA. The only clause that can
          //    tell the near half of a closed body from the far half.
          check(s.disagreements_interior === 0,
                `${name}: ${s.disagreements_interior} INTERIOR cells where the ` +
                `nearest facet was culled — that is a hole in the body, not a ` +
                `silhouette artefact`);
          // THE THRESHOLD, AND WHY IT IS NOT 100%. Measured on the cube
          // 2026-09-01: 70 of 239,152 covered cells disagree, ALL of them on the
          // silhouette edge, worst depth margin 0.0965% of the body's depth
          // range. At the silhouette the near and far sheets are COINCIDENT, so
          // which one wins a cell centre is float noise and must be. DO NOT
          // TIGHTEN THIS TO 100% — it would red the suite on sheets that are
          // required to be coincident. The interior clause above is the sharp
          // one; this is a loose backstop on the edge population.
          const frac = s.nearest_facet_is_painted / s.silhouette_cells;
          check(frac >= 0.995,
                `${name}: the nearest facet is a painted one at only ` +
                `${(100*frac).toFixed(3)}% of covered cells (floor 99.5%): the ` +
                `cull is keeping the wrong side of the body`);
          check(s.worst_depth_margin_pct <= 1.0,
                `${name}: a culled facet beat the painted sheet by ` +
                `${s.worst_depth_margin_pct}% of the depth range (ceiling 1.0%) ` +
                `— too deep to be a coincident silhouette sheet`);
        }
      }
      const line = ev
        ? `${ev.covered} cells covered, ${ev.lost} lost, nearest painted ` +
          `${(100*ev.nearestPainted/ev.covered).toFixed(3)}%, ${ev.interior} interior`
        : 'not culled — the painted set is the whole body';
      console.log(`  ${name.padEnd(19)} ${got.painted}/${got.facets} painted, ` +
        `cullSense ${got.cull_sense}, colour multiset matches the golden, ` +
        `legend bar ${got.legend === want.legend ? 'unchanged' : 'CHANGED'}`);
      console.log(`  ${' '.repeat(19)} ${line}`);
    }
    if (writeGolden) {
      file.bodies = golden;
      fs.writeFileSync(GOLDEN, JSON.stringify(file, null, 2) + '\n');
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

// ===================== THE PAINTED SURFACE, MEASURED =====================
//
// WHY THIS EXISTS AT ALL. The pressure check used to be a digest of the colour
// SEQUENCE. That pin broke twice on two changes that were both correct: the
// depth-sort repair reordered the paint on b52 and motorBike without altering a
// single colour, and back-face culling halved the cube's painted facets on a
// body measured closed. A sequence pin cannot tell those apart from a defect,
// so it is replaced by pins on the PROPERTIES that must hold.
//
// The instrumentation reads the page's own paint loop rather than recomputing
// the projection here. A second implementation of the screen map would drift
// from the page and go green on a body the page draws wrongly. The anchor below
// is asserted: if the paint loop is rewritten this harness REFUSES rather than
// silently skipping the geometry clauses.
const PAINT_ANCHOR = `  const keep = cullSense(m);
  const tris = [];
  m.faces.forEach((f,idx) => {
    const a=scr(f[0]), b=scr(f[1]), cc=scr(f[2]);`;

// The second anchor is the page's own decision to draw a facet. `kept` is
// OBSERVED at this line, never re-derived from the cull expression.
//
// This was a live defect in the first cut of this harness and it is the reason
// the clause is written the way it is. A probe that recomputes
// `area2 * keep <= 0` for itself agrees with a mutated page BY CONSTRUCTION.
// Measured 2026-09-01 by planting an inverted cull comparison — `>= 0` for
// `<= 0`, so the page keeps the far half of the cube while cullSense still
// reports -1:
//
//   probe mirrors the expression   nearest painted 99.971%, 0 interior — GREEN
//   probe observes the draw        nearest painted  0.029%, 237,068 interior
//
// The mirrored form passed every geometry clause on a page painting the wrong
// half of the body. It went red only on the colour multiset, and only because
// the far half happens to carry different field values; on a symmetric field it
// would have passed outright.
const KEEP_ANCHOR =
  `    tris.push({ a, b, c: cc, depth:(a[2]+b[2]+cc[2])/3, fi: idx });`;

function instrument(source) {
  for (const [anchor, what] of [[PAINT_ANCHOR, 'the projection loop'],
                                [KEEP_ANCHOR, 'the draw decision']]) {
    if (source.includes(anchor)) continue;
    console.error(`FAIL: ${what} this harness instruments has moved. It reads ` +
      'the page\'s own screen map and the page\'s own control flow on purpose — ' +
      'recomputing either here could go green on a body the page draws wrongly. ' +
      'Re-point the anchor at the new loop; do not delete the geometry clauses.');
    process.exit(1);
  }
  return source
    .replace(PAINT_ANCHOR, PAINT_ANCHOR + `
    if (globalThis.__CR_PROBE) {
      globalThis.__CR_PROBE.keep = keep;
      globalThis.__CR_PROBE.facets.push({ a, b, c: cc,
                                          d:(a[2]+b[2]+cc[2])/3, kept: false });
    }`)
    .replace(KEEP_ANCHOR, KEEP_ANCHOR + `
    if (globalThis.__CR_PROBE) {
      const __f = globalThis.__CR_PROBE.facets;
      __f[__f.length - 1].kept = true;
    }`);
}

// Every facet the page projected, with the page's own screen coordinates, the
// page's own depth, and whether the cull kept it.
async function paintFacets(instrumented, payload) {
  const probe = { facets: [], keep: null };
  globalThis.__CR_PROBE = probe;
  const r = await paint(instrumented, payload);
  // Read the recorder we handed out, not whatever is on globalThis now. If the
  // page clears or replaces it mid-paint the facets we DID capture still come
  // back and the emptiness check downstream reports it as a refusal — this used
  // to dereference globalThis and died with a bare TypeError instead, which
  // fails in the safe direction but tells the next reader nothing.
  globalThis.__CR_PROBE = null;
  return { ...r, facets: probe.facets, cullSense: probe.keep };
}

// Rasterise a facet onto the sampling grid, calling back with each cell centre
// that lands inside it. Half-plane signs; a cell straddling an edge counts.
const GW = 1200, GH = 600, SW = 800, SH = 400;
function raster(t, fn) {
  const [a, b, c] = [t.a, t.b, t.c];
  const x0 = Math.max(0, Math.floor(Math.min(a[0],b[0],c[0])/SW*GW));
  const x1 = Math.min(GW-1, Math.ceil(Math.max(a[0],b[0],c[0])/SW*GW));
  const y0 = Math.max(0, Math.floor(Math.min(a[1],b[1],c[1])/SH*GH));
  const y1 = Math.min(GH-1, Math.ceil(Math.max(a[1],b[1],c[1])/SH*GH));
  for (let iy = y0; iy <= y1; iy++) for (let ix = x0; ix <= x1; ix++) {
    const px = (ix+0.5)/GW*SW, py = (iy+0.5)/GH*SH;
    const d1 = (px-b[0])*(a[1]-b[1]) - (a[0]-b[0])*(py-b[1]);
    const d2 = (px-c[0])*(b[1]-c[1]) - (b[0]-c[0])*(py-c[1]);
    const d3 = (px-a[0])*(c[1]-a[1]) - (c[0]-a[0])*(py-a[1]);
    if (((d1<0)||(d2<0)||(d3<0)) && ((d1>0)||(d2>0)||(d3>0))) continue;
    fn(iy*GW + ix);
  }
}

// IS THE BODY STILL FULLY DRAWN, AND IS IT THE RIGHT HALF?
//
// Two separate questions, and only the second is hard. Silhouette coverage
// answers the first: every cell the whole body covers must still be covered by
// the facets that survived the cull. It CANNOT answer the second — on a closed
// body the near half and the far half project to the SAME silhouette, so a cull
// that kept exactly the wrong half scores 100% here. That is why the z-buffer
// clause exists: depth-sort the whole body, and require that the facet nearest
// the camera at each covered cell is one the cull kept.
function surfaceEvidence(facets) {
  const painted = facets.filter(t => t.kept);
  const cover = new Uint8Array(GW*GH), keptCover = new Uint8Array(GW*GH);
  const best = new Float64Array(GW*GH).fill(-Infinity);
  const win = new Int32Array(GW*GH).fill(-1);
  facets.forEach((t, i) => raster(t, cell => {
    cover[cell] = 1;
    if (t.d > best[cell]) { best[cell] = t.d; win[cell] = i; }
  }));
  const bestKept = new Float64Array(GW*GH).fill(-Infinity);
  for (const t of painted) raster(t, cell => {
    keptCover[cell] = 1; if (t.d > bestKept[cell]) bestKept[cell] = t.d;
  });
  let covered = 0, lost = 0, nearestPainted = 0;
  const bad = [];
  for (let i = 0; i < cover.length; i++) {
    if (!cover[i]) continue;
    covered++;
    if (!keptCover[i]) lost++;
    if (win[i] >= 0 && facets[win[i]].kept) nearestPainted++;
    else if (win[i] >= 0) bad.push(i);
  }
  // A disagreeing cell ON THE SILHOUETTE EDGE is where the near and far sheets
  // MEET, so their depths are equal there and the winner is float noise. An
  // INTERIOR one is a real hole in the body and is never allowed.
  let edge = 0, interior = 0, worstMargin = 0;
  const ds = facets.map(t => t.d);
  const span = (Math.max(...ds) - Math.min(...ds)) || 1;
  for (const i of bad) {
    const ix = i % GW, iy = (i / GW) | 0;
    let onEdge = false;
    for (let dy = -1; dy <= 1 && !onEdge; dy++) for (let dx = -1; dx <= 1; dx++) {
      const jx = ix+dx, jy = iy+dy;
      if (jx < 0 || jy < 0 || jx >= GW || jy >= GH || !cover[jy*GW+jx]) { onEdge = true; break; }
    }
    if (onEdge) edge++; else interior++;
    const m = (best[i] - bestKept[i]) / span;
    if (m > worstMargin) worstMargin = m;
  }
  return { covered, lost, nearestPainted, edge, interior,
           worstMarginPct: Number((100*worstMargin).toFixed(4)) };
}
