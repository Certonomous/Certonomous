# Credentials-view reframe — proposal for GUI-1 (control_room.html)

**Author:** BG-2. **Status:** proposal — I did NOT edit `control_room.html`
(it's GUI-1's file tonight). This is the tight, self-contained diff to apply,
flagged for merge ordering. The server side it depends on is already landed on
`feat/website-pipeline` (`/api/lab-stats`).

Covers coordinator items **v2-G2** (lifetime-counter header, never a "4 of 8"
fraction) and **v2-G5 / v3-N3** (8 canonical bodies collapse into ONE expandable
calibration row; no toy cases headline the view).

A complete, working reference implementation of exactly this layout is already
built and self-contained at **`demo-output/website/wall/wall.html`** (screenshot
verified). GUI-1 can lift its markup/CSS directly; the two hooks below are all
that differ inside the live control room.

## 1. New data source (already live)

`GET /api/lab-stats` returns:

```json
{
  "missions_run": 309,
  "solver_core_hours": 0.63,
  "knowledge_entries": 8,
  "experimental_anchors": 8,
  "benchmarks_active": 2,
  "detail": { "ledger_evaluations": 309, "persisted_missions": 0, "per_solver": {…} }
}
```

`missions_run` is durable — it counts the all-night mega-batch ledger
(`demo-output/website/mega-batch/ledger.jsonl`) plus any persisted server
missions. It grows honestly and survives restarts; never rounded.

## 2. Header: lead with counters, not a fraction

Replace the credentials-view headline (currently the tier fraction) with a
five-tile counter row fed from `/api/lab-stats`:

```js
const s = await fetch('/api/lab-stats').then(r => r.json());
renderCounters([
  ['missions run',          s.missions_run.toLocaleString()],
  ['solver core-hours',     String(s.solver_core_hours)],
  ['knowledge entries',     String(s.knowledge_entries)],
  ['experimental anchors',  String(s.experimental_anchors)],
  ['benchmarks active',     String(s.benchmarks_active)],
]);
```

The "N of 8 validated" fraction must NOT be the headline. If a validated count
is still wanted, it belongs *inside* the calibration row summary (see below),
not at the top.

## 3. Collapse the 8 canonical bodies into ONE calibration row

The eight `/api/credentials` cards (cube, sphere, cylinder, flat_plate,
naca0012_wing, naca4412_wing, ahmed_25, ahmed_35) are canonical calibration
geometry — they must not each occupy a headline card. Fold them into a single
`<details>` "Calibration suite" row:

```html
<details class="cal-suite">
  <summary>
    <span class="cal-title">Calibration suite</span>
    <span class="cal-sub">8 canonical bodies benchmarked against published
      experiment · 4 validated within band</span>
  </summary>
  <!-- table: Body | Measured vs reference | Envelope | Tier | Source -->
</details>
```

The full measured-vs-reference table (with cited sources and honest tiers) lives
inside the collapsed row. See `wall.html` for the exact table markup + CSS.

## 4. Verdict text ≤ 2 lines, expandable reasoning (v2-G5)

For any body card that remains expanded, cap the verdict to ≤ 2 lines and put
the full reasoning behind a "why" toggle. The credential JSON already carries a
short `reason`; keep the on-card text to the tier + one clause, reasoning on
demand.

## Merge ordering note

Apply this AFTER GUI-1's own layout work for the night is settled, so the
counter row and calibration `<details>` slot into the final structure. The only
backend dependency (`/api/lab-stats`) is already merged on this branch.
