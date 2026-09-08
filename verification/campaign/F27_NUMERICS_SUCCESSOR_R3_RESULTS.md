# F27-WOMERSLEY EINF-TOPOLOGY SUCCESSOR — R3 RESULTS (Roache triple, graded)

> **RECORD ONLY.** This document transcribes a verdict produced by the frozen,
> pinned grader. It does not re-grade and it decides nothing. The gates,
> thresholds and bands are those frozen in
> `verification/campaign/F27_NUMERICS_SUCCESSOR_R3_PREREGISTRATION.md`
> (freeze commit `c3b1d898`); this record cites that frozen document, it does not
> rewrite it (rule 6).
>
> **Dated 2026-09-08.**

---

## 0. WHAT THIS RESOLVES

The R2 numerics successor graded **PASS on E2 / GATE FAIL on Einf**
(`F27_NUMERICS_SUCCESSOR_R2_RESULTS.md`): a **CONVERGING** but low-order
(`1.272`) Einf triple whose fine value `4.136e-03` sat **above** the band upper
bound — diagnosed as a localized D4 corner-mode artifact of the square core/ring
block interface. **R3 is the mesh-topology fix**: a rounded-square core/ring
interface, byte-identical gates/thresholds/bands/cap to R2 (only the builder
mesh topology and the run root/pre-registration commit change). The R3 run
completed all three levels and graded below. **This RESOLVES the R2 Einf GATE
FAIL: with the rounded-corner interface the Einf triple recovers to design order
`2.274` and its fine value falls INSIDE the band → PASS.** The D4 corner mode was
a mesh-topology artifact, not a capability gap.

- **Run root:** `verification/runs/F27_NUMERICS_SUCCESSOR_R3_runs`
- **Frozen pre-registration:** `verification/campaign/F27_NUMERICS_SUCCESSOR_R3_PREREGISTRATION.md`, freeze `c3b1d898c096dea45c0b0e7307604bff44dd6772`
- **Grader (pinned, frozen):** `cases/F27_WOMERSLEY_PIPE/einf_topology_successor/grade_f27_r3.py`,
  git blob `01acbec95f5d161c7fbb7694ebeedab1f0c4bd13` — confirmed at grade time to
  equal both the disk file and `HEAD:<path>` (rule-2 hash). Supervisor check-1 PASS.
- **Graded artifact (cited by every number below):**
  `verification/runs/F27_NUMERICS_SUCCESSOR_R3_runs/F27_GRADED.json`, `prereg_commit c3b1d898c096dea45c0b0e7307604bff44dd6772`
- **Grading invocation:** the frozen grader's own `--root` default already points
  at the R3 root (§2d.1 lesson from R2 carried forward into this new file); the
  recorded grade was produced with an explicit
  `--root=verification/runs/F27_NUMERICS_SUCCESSOR_R3_runs` for the record, agreeing
  with the default. Reads the four `processor*/` directories directly (decomposed,
  never reconstructed); no `reconstructPar` is used or needed.

---

## 1. THE TWO GATE VERDICTS (Roache triple, rule 5)

Coarse/medium/fine = 3,840 / 30,720 / 245,760 cells, refined by exactly 2 in all
three directions (r = 2). `Fs = 1.25`, `BAND_FACTOR = 5.0`, reference 0.0. Both
triples strictly complete (§2), both planted controls green (§2).

### G-F27R-1 — `E2_velocity_locked_phase` = **PASS**

- triple state: **CONVERGING** (monotone)
- level values: coarse `7.922849350655155e-03` / medium `1.9851465947020976e-03` / fine `5.339607682840979e-04`
- observed order: `2.032672602780843`
- GCI: `109.8847460724523 %` ( = `0.0005867414343554963` absolute at Fs = 1.25)
- band: `[6.052738753361828e-05, 0.001513184688340457]`
- **fine value `5.339607682840979e-04` is INSIDE the band → PASS.**

### G-F27R-2 — `Einf_axial_velocity_locked_phase` = **PASS**

- triple state: **CONVERGING** (monotone)
- level values: coarse `1.199025758080605e-02` / medium `3.402871640055304e-03` / fine `1.6271073318049128e-03`
- observed order: `2.273778922008423`
- GCI: `35.56427340732606 %` ( = `0.0005786689001137473` absolute at Fs = 1.25)
- band: `[0.00011397841172247245, 0.002849460293061811]`
- **fine value `1.6271073318049128e-03` is INSIDE the band → PASS.**

### Overall = **PASS**

Both gated triples are **CONVERGING** (monotone), so this is a **REAL graded
result — NOT `NOT A RESULT`** (rule 5). Both gated fine values sit inside their
pre-registered bands: the numerics-change successor on the rounded-corner mesh
**PASSes on E2 (RMS error) AND on Einf (max error)**.

The reported-not-gated channels are recorded in the graded artifact and enter no
gate: `R-F27-W` bulk mean (CONVERGING, order `1.958`, values ~`0.6423 / 0.6428 /
0.6429`); `R-F27-E_perp`, `R-F27-A_z`, `R-F27-A_theta` all at round-off
(≤ `1.4e-11`), read DIVERGENT on triples formed from noise — expected for
channels the exact solution is identically zero along, and each also enters rule 5
limb 1 as a UNIFORMITY state (all **PLATEAUED**, §2).

---

## 2. STRICT COMPLETION, ITERATIVE/PLATEAU STATE, AND PLANTED CONTROLS

- **Strict completion (rule 4):** all three levels strictly complete in the grader's
  `completion()` — rc = 0, an `End` line, last time == `endTime` (`5.25`), the
  fixed-deltaT `Time`-line identity holds, `U`/`p` present at endTime in all four
  processor directories and each **newer than the serial `0/U`** (age guard),
  `U` at `endTime − PERIOD` present, `0/C` and `0/V` present. `done=True` for
  coarse, medium and fine.
- **Iterative convergence (rule 5 limb 1):** all three levels **CONVERGED** (every
  time step's final p, Ux, Uy, Uz residual within the solver tolerances).
- **Plateau limbs:** periodicity and both uniformity states **PLATEAUED** at every
  level (coarse/medium/fine, and each `/uniformity`) — the A_z / A_theta instrument
  that would catch an F21-style wall-localized mode reads uniform throughout.
- **Planted-zero controls (rule 3):** both gate planted-zero controls **PASSED** on
  the REAL fine artifact `verification/runs/F27_NUMERICS_SUCCESSOR_R3_runs/fine/processor*/5.25/U`:
  - `e2_of`: planted axial offset `6.752399908146562e-03`, reader moved by
    `6.752399908146593e-03` (predicted == read-back to 1e-12).
  - `einf_of`: planted axial offset `6.584605807730147e-03`, reader moved by
    `6.58460580773014e-03` (predicted == read-back to 1e-12).
  - Plus 16 instrument controls green in the grader (readers zero on the exact field
    with each of four planted defects seen by its own channel and no other;
    periodicity and both uniformity limbs driven both ways; iterative census driven
    both ways; L-342 field-class separation incl. age guard; exactly one
    `grade_ladder` call node; reader parses real solver `U` on this box). A zero here
    is a planted-control-backed zero, not a blind read.

---

## 3. WHAT THIS SETTLES ABOUT THE D4 CORNER-MODE MESH-TOPOLOGY FIX

| quantity | R2 (square interface) | R3 (rounded-square interface) | band |
|---|---|---|---|
| E2 fine value | `7.285879634110018e-04` PASS | `5.339607682840979e-04` **PASS** | `[6.053e-05, 1.513e-03]` |
| E2 observed order | `2.0671` | `2.0327` | design 2 |
| Einf fine value | `4.136254537709814e-03` **GATE FAIL (above band)** | `1.6271073318049128e-03` **PASS** | `[1.140e-04, 2.849e-03]` |
| Einf observed order | `1.2718` (order-degraded) | `2.2738` (**order recovered**) | design 2 |
| Einf triple | CONVERGING | CONVERGING | — |

The R2 Einf failure was a **CONVERGING but order-degraded** max-error localized at
the square core/ring corner (a D4 corner mode the L-infinity norm is set by).
Rounding the core/ring interface **restored the Einf triple to design order 2**
(`1.272 → 2.274`), cut the fine max error by ~2.5x (`4.136e-03 → 1.627e-03`), and
brought it inside the band **without touching any gate, threshold, band or the
numerics** — E2 remains PASS at order ~2.03. The corner mode was therefore a
**mesh-topology artifact**, resolved by the topology fix; F27 numerics-successor
now PASSes on both gated norms.

---

## 4. COST

- **Actual: 459.800 core-min** (coarse `0.667` + medium `14.200` + fine `444.933`),
  ClockTime × 4 ranks ÷ 60, from `F27_GRADED.json::cost_claim` (per-level ClockTime
  10 / 213 / 6674 s in each level's `log.pimpleFoam`). No infrastructure defects.
- **Cap: 625 core-min** (frozen R3 cap, retained byte-identical from R2). Spend is
  under cap; no cap breach.
- **Registered point estimate: 417.667 core-min** → ratio actual/estimate =
  **1.1009** (+10.1 %). The R3 estimate reused the R2 actual as its point estimate;
  the +10 % gap is contention/misprediction on the fine level (fine ClockTime
  6674 s vs the R2 fine 6047 s that fixed the estimate), not waste — no stalled row
  (all levels well under 3600 wall s except the genuinely long fine solve).
- **Dollars DERIVED, NOT MEASURED:** 459.8 core-min = 7.6633 core-h × $0.0513/core-h
  = **$0.3931 (derived)**, reported-by-owner — the box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER.md` §5).
- **Calibration (rule 12):** a `docs/COST_CALIBRATION.md` row is filed with this
  record (est 417.667 / cap 625 vs actual 459.800, ratio 1.1009).

---

## 5. VERDICT VOCABULARY

Verdicts stated: **PASS** (G-F27R-1), **PASS** (G-F27R-2), overall **PASS**. No
softer word is used and none is implied.
