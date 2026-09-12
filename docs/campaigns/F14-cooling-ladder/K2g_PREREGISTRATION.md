# K2g — the rack-row module graded on a quantity that has signal: PRE-REGISTRATION

**Rung:** `K2g`. **Family:** F14 cooling ladder. **Successor to:** `K2f`, which is
`BLOCKED` and closed. **Status of this document:** frozen at its commit; nothing
below may be changed afterwards except as a dated addendum that cannot alter a
gate, threshold, cap or label (CLAUDE.md rule 2).

**No compute has been spent against this document.** `verification/runs/F14-cooling-ladder/K2g_runs/K2f_L3`
does not exist at the moment of this freeze, and that is the condition under
which amendments to this draft were legal (rule 2, first bullet).

---

## 0. WHAT IS AND IS NOT PREDICTION-FIRST HERE — SAID FIRST, BECAUSE IT LIMITS THE FREEZE

`K2f_L1` and `K2f_L2` already exist on disk, so the L1 and L2 value of **any**
quantity this document could have chosen was knowable before the freeze, and the
freeze therefore does **not** prove the gate quantity was not chosen to fit
them — it was chosen from them, by the measurement in §2. The genuinely
prediction-first content of this registration is exactly three things, and §7
registers a losable number for each: **the L3 value, the triple's
classification, and the observed order with its GCI.**

---

## 1. THE CASE, AND WHY K2f'S GATE COULD NOT BE REPAIRED IN PLACE

K2a's rack-row module: a four-rack row in a cold-aisle/hot-aisle room,
`buoyantBoussinesqSimpleFoam`, `kOmegaSST`, supply 289 K, rack exhaust 301 K, a
registered 12 K rack rise. Geometry, boundary conditions, properties, schemes and
solver settings are inherited **by citation** from
`docs/campaigns/F14-cooling-ladder/K2f_PREREGISTRATION.md` §2 and are not
restated or altered.

K2f is `BLOCKED`. Its §20.6 declines L3 on validity grounds, states that no L3
cost is authorised there, and an addendum cannot grant one. Three of K2f's four
graded rows (`G1` `T_in,max`, `G2` `θ_max`, `G3` `T_in,1`) are functions of
`T_in,i`, and K2f §20.2 **measured** that this quantity carries no signal on this
module: `θ_max` = 4.876e-05 at L1 and 4.678e-05 at L2, on a healthy 289.000 →
301.000 K field. A third registration resting on `T_in` or `θ` would repeat that
for a third time. This document does not.

---

## 2. THE GATE QUANTITY, CHOSEN BY MEASUREMENT ON THE TWO EXISTING LEVELS

Twenty-three candidate scalars were computed from the `K2f_L1` and `K2f_L2`
fields at `endTime` 3000 — zero solver compute, post-processing reads only. The
test applied was **not** physical largeness but **mesh sensitivity measured
against the level's own iteration noise**: a quantity whose L1→L2 change is not
large compared with its checkpoint-to-checkpoint wobble cannot support an
observed order.

| candidate | L1 | L2 | rel. change | verdict |
|---|---|---|---|---|
| **Δp_module = areaAvg(p_rgh, tile) − areaAvg(p_rgh, return)** | **27.189119361** | **27.729679616** | **+1.988 %** | **REGISTERED** |
| vol-avg p_rgh, whole domain | 26.782304 | 27.314529 | +1.987 % | rejected: same information, no patch definition |
| vol-avg k, whole domain | 0.02230290 | 0.02292992 | +2.796 % | **rejected: L2 checkpoints oscillate 6e-05 = 10 % of the L1→L2 signal** |
| vol-avg T, hot-aisle zone | 295.679740 | 295.775150 | +0.032 % | rejected: L2 still climbing 3.5e-03 per 500 iterations at 3000 |
| `U_ha` (K2f's contrast quantity) | 0.5242578 | 0.5312822 | +1.340 % | rejected: K2f §20.2 measured trend fraction 0.9212 — not plateaued |
| vol-avg \|U\|, whole domain | 0.6266399 | 0.6243244 | −0.370 % | rejected: L2 still climbing, 2.7 % of signal per window |
| flux-weighted return air temperature | 293.00796 | 293.00936 | +0.0005 % | **rejected: pinned by the global energy balance to 0.008 K, and its L2 checkpoints swing 0.010 K — seven times its own grid signal** |
| vol-avg T, cold-aisle zone (K2f's `G4`) | 289.0000344 | 289.0000206 | −4e-08 % | **rejected: G4 has no signal either — recorded, because K2f never graded it** |
| max T in the domain | 301.000000 | 301.000000 | 0 | rejected: pinned exactly by the rack-exhaust `fixedValue` |
| per-rack Δp (four rows) | 0.52628 … 0.64060 | 0.52574 … 0.65119 | −0.46 … +1.65 % | rejected: L1 is symmetric, L2 is not; the symmetry break is the same size as the signal |
| volume fraction above T thresholds | — | — | −1.4 … +1.7 % | rejected: sign flips with the threshold |

**REGISTERED GATE QUANTITY — `DP_module`**, the module pressure drop, units
m²/s² (kinematic; ×1.2 kg/m³ for Pa):

> `DP_module` = area-weighted average of `p_rgh` over the `tile` supply patch
> minus the area-weighted average of `p_rgh` over the `return` patch,
> evaluated on the field written at that level's `endTime`.

It is the flow resistance of the cooling path — the quantity that sets fan duty —
and it is not pinned by any conservation statement: the enthalpy balance fixes
the return temperature, not the pressure field.

**Why it survives and the others do not — the measured signal-to-noise:**

| level | Δp at endTime | Δp at endTime − 500 | iteration drift | drift ÷ grid signal |
|---|---|---|---|---|
| `K2f_L1` | 27.189119361 | 27.189119394 | **3.25e-08** | 6e-08 |
| `K2f_L2` | 27.729679616 | 27.728510157 | **1.169e-03** | 2.2e-03 |

Grid signal **e21 = f2 − f1 = 0.540560254 m²/s²**. L2's own iteration drift is
**0.22 %** of it, and ≈0.4 % of the L2→L3 difference §7 predicts. No other
candidate in the table reaches better than 3 %.

---

## 3. THE LADDER

| level | case directory | cells | `endTime` | provenance |
|---|---|---|---|---|
| `K2g_L1` | `verification/runs/F14-cooling-ladder/K2f_runs/K2f_L1` | 58,368 | 3000 | **reused by citation** |
| `K2g_L2` | `verification/runs/F14-cooling-ladder/K2f_runs/K2f_L2` | 196,992 | 3000 | **reused by citation** |
| `K2g_L3` | `verification/runs/F14-cooling-ladder/K2g_runs/K2f_L3` | 664,848 | **2000** | built by this rung |

**L1 and L2 are not re-run. Their rule-4 evidence, cited:** `STATUS.K2f_L1`
rc=0, wall 199 s, 4 ranks, **13.267 core-min**; `STATUS.K2f_L2` rc=0, wall 960 s,
4 ranks, **64.000 core-min**; both certified **DONE on all six clauses including
the age guard** by `mark_done_k2f.py`, recorded at K2f §20.1. The same unedited
instrument certifies L3. **Compute already paid for and reused: 77.267 core-min.**

**Refinement.** N(L2)/N(L1) = **3.37500**; N(L3)/N(L2) = **3.37500**. An equal
ladder with representative-h ratio **r = 3.375^(1/3) = 1.5 exactly**.
**`G-MESHSIM`: both ratios must lie in [3.2063, 3.5438]** — carried from K2f §5.4
unchanged. A ratio outside it REFUSES at exit 2.

**The L3 directory is named `K2f_L3` deliberately**, so that the frozen
`build_k2f.py` and the frozen `mark_done_k2f.py` — the instruments that built and
certified L1 and L2 — are reused **bit for bit with no edit** (rule 6).

---

## 4. THE GRADING PATH

`verification/runs/F14-cooling-ladder/K2g_runs/analyse_k2g.py`, with the reader
`foam_patch_reader.py` beside it. **Reused rather than reinvented:**
`scripts/roache_triple.py` supplies rule 5's floors, the Fs = 1.25 GCI and the
one-way gate; `mark_done_k2f.py` supplies rule 4's six clauses; the refusal
discipline is `K2f_runs/analyse_k2f.py`'s.

**ONE reader, every level.** L1 and L2 carry no `p_rgh` monitor and L3 would;
grading the coarse levels through one instrument and the fine level through
another is how a defect hides. `foam_patch_reader.area_average` computes the
area-weighted patch average from the field files, from a reconstructed time
directory or from the union of `processor*`, and **reproduces OpenFOAM's own
`surfaceFieldValue areaAverage` exactly on both existing levels** —
27.189119361484 and 27.729679615660 against the function object's
2.7189119361e+01 and 2.7729679615e+01. Both paths are asserted equal at
`endTime`, where both exist (`C-RECON`, driven in the selftest).

### 4.1 ORDER OF EVALUATION — THE T5b DEFECT IS THE REASON THIS IS §4.1

This week a lab ladder diverged twenty-one orders of magnitude, exited rc=0,
passed the completion rule and **reached grading**, because the registered
convergence clause was **absent from the comparator** and a neighbouring gate
silently supplied its number. The clauses below are therefore registered **and
implemented**, in this order, and `roache_triple.grade_ladder` **refuses
outright if the convergence states are not supplied at all**:

1. **`D-CONV` and `D-PLATEAU` — evaluated BEFORE any triple is classified.**
   Any level not iteratively converged or not plateaued → **`NOT A RESULT`**.
2. A triple that is `DIVERGENT`, `STAGNANT`, `OSCILLATORY`, `EXACT` or
   `DEGENERATE` → **`NOT A RESULT`**, with the value, every triple and every
   order printed beside it, and the reason no GCI is quoted.
3. `CONVERGING` → **`PASS`** inside §5's band, else **`GATE FAIL`**, GCI at
   Fs = 1.25, never quoted when the three values are not monotone.

The gate is one-way: it may turn a `PASS` or a `GATE FAIL` **into**
`NOT A RESULT` and never the reverse.

### 4.2 `D-CONV` — iterative convergence, from the solver's own log

For each of `Ux`, `T`, `p_rgh` (first pressure corrector), from `log.solve`, **all
three must hold**: final initial-residual ≤ **5.0e-03**; fallen ≥ **2.5 decades**
from the normalised start; and **not rising** — mean of the last 100 ≤ **2.0** ×
min of the last 400. Otherwise the level is `NOT_CONVERGED` and step 1 fires.

**Stated plainly, because these numbers were set knowing the answers (§0):**
`K2f_L2` limit-cycles — `Ux` 1.756e-04 over 3.76 decades, rise 1.151; `p_rgh`
1.777e-03 over 2.75 decades, rise 1.150. The floors admit it. The defensible
reason is that for a steady SIMPLE solve the absolute floor is the weakest of the
three tests — a pressure equation routinely plateaus near 1e-03 — and the
**discriminating** tests are the decade drop and the non-rise, which reject a
dead solve (0 decades) and a diverging one (rise 2.9e+05) by margins of orders of
magnitude. The selftest drives all three cases.

### 4.3 `D-PLATEAU` — two-sided, because a dead solve also has a small delta

A level is `PLATEAUED` only if **both** hold:

* **drift:** |Δp(`endTime`) − Δp(`endTime` − 500)| ≤ **1.0e-02 m²/s²**;
* **`D-ALIVE`:** rms over internal cells of *T*(`endTime`) − *T*(0) ≥ **0.10 K**.

`D-ALIVE` is the clause my supervisor required. **A frozen solve shows a
late-checkpoint delta of ~0 and would sail through a one-sided plateau test**; it
must not. Measured departures: `K2f_L1` **4.1142 K**, `K2f_L2` **4.1281 K**,
against the 0.10 K floor. A case whose field never left its initial condition
returns ~0 and is `NOT_PLATEAUED: DEAD`.

### 4.4 `D-PLANT` — rule 3, the planted zero

The comparator shadows the case with symlinks, adds **1.234e-03** to every
`tile` face value of a **copy** of the `endTime` `p_rgh` file, and requires the
production reader to read exactly that back **from disk**. Nothing under a real
case directory is written. If the reader cannot see it the comparator **exits 2
and grades nothing**. The negative arm — a plant the reader cannot see — is
driven in the selftest and must refuse.

### 4.5 Mesh admission, carried from K2f §5.4 unchanged

`G-CHECKMESH` zero failed checks and `Mesh OK.`; `G-3D` three geometric
directions with no `empty`/`wedge` patch; `G-MINCELL` every named feature
≥ 5.0 mm; `G-CELLS` the mesh's own cell count equals the registered one.

---

## 5. THE GATE

> **`G-DP`.** The **fine-level** value of `DP_module` must lie in
> **[27.9699, 28.0901] m²/s²** → **`PASS`**; inside a `CONVERGING` triple and
> outside the band → **`GATE FAIL`**; a triple that is not `CONVERGING`, or any
> level failing `D-CONV` or `D-PLATEAU` → **`NOT A RESULT`**.

**The band is not chosen, it is derived.** With f1 and f2 fixed and r = 1.5, an
observed order p implies f3 = f2 + e21/1.5^p. The band is exactly the interval
implied by **p ∈ [1.0, 2.0]**: p = 2.0 → 27.96993, p = 1.0 → 28.09005. That
interval is the scheme set's own admissible range — momentum `linearUpwind`
(second order), *T* `limitedLinear 1` (second order limited), *k* and *ω*
`upwind` (first order) — so a converged, correctly refining solve of **this**
discretisation should land inside it, and a solve whose order falls outside
[1.0, 2.0] is telling us something and is graded `GATE FAIL`, not smoothed.

**The band can lose, and the selftest proves each way**: f3 = 28.11 grades
`GATE FAIL` at order 0.867; f3 = 27.95 grades `GATE FAIL` at order 2.214;
f3 = 28.30 grades `NOT A RESULT` (`DIVERGENT`); f3 = 27.60 grades
`NOT A RESULT` (non-monotone), with no GCI quoted beside either.

---

## 6. COMPLETION — CLAUDE.md RULE 4, ALL SIX CLAUSES, NO DEGRADATION

A level is DONE only if **all** hold, on `mark_done_k2f.py` unedited: `rc = 0`;
an `End` line; **last time == `endTime`**; fields `T U p_rgh alphat nut k omega
phi` present; `ExecutionTime` count == `round(endTime/deltaT)` (`deltaT` = 1, so
== `endTime`); and **every field at `endTime` NEWER than the case's own `0/T`** —
the age guard, because `0/T` is touched last at launch and so dates the run
allowed to produce the answer. Clause 7, the launch guard, refuses a case where
`0/` or a time directory already exists. A level failing any clause is not DONE
and the comparator **refuses at exit 2 rather than degrade**.

**`endTime` 2000 for L3 against 3000 for L1 and L2 — registered, with its
reason.** Δp is plateaued at **both** existing levels by iteration 1500:
`K2f_L1` moves 1.1e-07 between 1500 and 3000, `K2f_L2` moves 1.0e-04 — the
latter **0.04 %** of the L2→L3 difference §7 predicts. `K2d_L3`, the only run
ever made on this exact 664,848-cell mesh, was already at `Ux` 1.573e-04 —
`K2f_L2`'s own limit-cycle floor — by iteration 995. 2000 iterations is a third
more than the resolution at which both existing levels had settled. **The
shortcut cannot smuggle an unconverged level through: `D-PLATEAU` and `D-CONV`
are evaluated at L3 exactly as at L1 and L2, and an L3 still moving at 2000 is
`NOT A RESULT`, with the run's cost spent and reported.**

**`E-ENDTIME`** is the single registered edit, applied by the launcher to the
**generated** `system/controlDict` and never to the frozen builder: exactly one
line, `endTime 3000;` → `endTime 2000;`, asserted present and asserted that no
`endTime 3000;` line survives, refusing at exit 2 otherwise.

**`M-REPRO`.** The mesh is built fresh by the frozen `build_k2f.py K2f_L3`. An
independently built 664,848-cell mesh of this module already exists at
`verification/runs/F14-cooling-ladder/K2d_runs/RETIRED_2026-09-11/K2d_L3/constant/polyMesh`
— verified by me: `nCells` 664,848, 68 blocks, 147 vertices **byte-identical to
`K2f_L1`'s**, divisions exactly 2.25× L1's, the same twelve patches with face
counts exactly 5.0625× L1's, `checkMesh` `Mesh OK.` with three geometric
directions. It is **not** used as the mesh. It is used as a **control**: the
launcher refuses unless the fresh build reproduces that mesh's cell count and
every patch face count.

---

## 7. REGISTERED PREDICTIONS — LOSABLE, AND SCORED EITHER WAY

With f1 = 27.189119361, f2 = 27.729679616, e21 = 0.540560254, r = 1.5:

* **`P-K2g-1` — the L3 value.** **Δp(L3) = 28.049 m²/s²**, ±0.030. Reasoning:
  the scheme set is mixed first/second order and the functional is dominated by
  wall friction and separation loss in the momentum equation, so the observed
  order should sit nearer the momentum scheme's than the turbulence scheme's;
  p = 1.30 gives e32 = 0.3191.
* **`P-K2g-2` — the classification.** The finest triple is **`CONVERGING`**.
  This can lose four ways: L3 below f2 (non-monotone), e32 ≥ e21 (`DIVERGENT`),
  p < 0.5 (`STAGNANT`), |p| < 0.05 (`DEGENERATE`).
* **`P-K2g-3` — the order and the GCI.** Observed order **p = 1.30**, band
  [1.0, 2.0]; **GCI = 2.05 %**, equivalently **0.575 m²/s² absolute**, at
  Fs = 1.25, dim = 3.
* **`P-K2g-4` — the verdict.** **`PASS`**.
* **`P-K2g-5` — the cost.** L3 spends **598 core-min ± 25 %** on the CPU basis;
  charged core-minutes (wall × ranks ÷ 60) land between **654 and 1,076**.

---

## 8. COST — RULE 12, COSTED BEFORE COMPUTE

**The unit is core-minutes = wall seconds × ranks ÷ 60.** It is charged against
allocated ranks, not against work done, so **on a contended box a run burns
budget whether or not it is computing.** The box carried load 68 on 16 cores at
02:59Z tonight and load 40 at 03:22Z. Contention is therefore measured, not
managed: the launcher records both `ClockTime` and `ExecutionTime` in `STATUS`.

**The anchor, and the disagreement stated rather than resolved.** `K2d_L3` is
the only run ever made at 664,848 cells on this box with this solver: 994
iterations, `ExecutionTime` 4,459.15 s at 4 ranks — **17.944 core-s per
iteration**. `K2f`'s own L1→L2 rate law (N^1.2937) extrapolates **5.626**, and
its registered law (N^1.765) **9.992** — a spread of 3.2×. **Two cell counts
cannot separate the anchor from the exponent** and this document does not
pretend otherwise; it registers the **measured** figure and not the flattering
one.

**POINT: 598 core-min** (17.944 core-s/iter × 2000 iterations ÷ 60, CPU basis).
**CAP: 1,200 core-min.** Derivation: the measured-contention projection below is
1,076, and the cap is that with 12 % headroom. This departs from K2f's 3×-POINT
convention deliberately — 3× would be 1,794 core-min, and a cap that cannot bind
is not a cap. **An overrun stops the run; it does not get a new budget.**

**Ranks — the counter-intuitive question, with my number.**

| ranks | total CPU, 2000 iter | assumed CPU efficiency | **wall** | **core-min charged** | basis |
|---|---|---|---|---|---|
| 1 | 32,299 core-s | 98.5 % | **9.11 h** | **547** | **extrapolated** |
| 2 | 34,094 core-s | 93 % | **5.09 h** | **611** | **extrapolated** |
| **4** | **35,888 core-s** | **55.6 %** (K2d_L3's own) | **4.48 h** | **1,076** | **measured** |
| 4 | 35,888 core-s | 91.4 % (K2f_L2's own) | 2.73 h | 654 | measured |

**RECOMMENDATION: 4 ranks, and the premise behind the 1-rank case does not
survive measurement.** The 42 % efficiency figure belongs to
`chtMultiRegionSimpleFoam`, a different solver with region coupling; measured at
03:22Z tonight a 6-rank `simpleFoam` alongside it was at 91 %.
**`buoyantBoussinesqSimpleFoam`'s own 4-rank efficiencies on this box are 97.9 %
(`K2f_L1`) and 91.4 % (`K2f_L2`)**, and the pessimistic 55.6 % is `K2d_L3`'s own
measurement, which is the figure registered above. The 1- and 2-rank rows are
**extrapolations — there is no measurement at 664,848 cells at either** — and
they buy at most 529 core-min (**$0.45, derived at $0.0513/core-h, never
measured**) at a cost of 4.6 extra wall-hours the day before a demo. Registering
a point on an unmeasured configuration to save $0.45 is the worse trade.

**Registered launch row:** `K2f_L3`, **4 ranks, hang guard 18,000 s**
(= 1,200 core-min ÷ 4 × 60). Alt row: 2 ranks, 36,000 s — the same cap. The
launcher's registered table is the only legitimate source of either number and a
hand-passed pair refuses at exit 2; `K2d_L3` died on a hand-passed 8,034 s guard
against a registered 20,250 s and lost 535.600 core-min.

**Memory.** `K2d_L3` ran 995 iterations at 4 ranks on this 30 GB box **without an
OOM**, on this exact mesh, and left a 233 MB case directory. That is what is
measured; no resident-set figure survives the run and none is claimed.

**Total registered spend for the rung:** 77.267 core-min already paid (L1, L2,
reused by citation) + L3 at POINT 598, CAP 1,200. **$1.03 at POINT, derived at
$0.0513/core-h and reported-by-owner, never measured** — the box cannot read its
own billing.

---

## 9. ORDER OF OPERATIONS — BINDING ONCE FROZEN

1. This document and the grading path are committed. **Nothing is built before
   the commit exists.**
2. `python3 analyse_k2g.py --selftest` → must print `SELFTEST PASSED`.
3. `bash launch_k2g.sh --stage` → builds `K2f_L3`, applies `E-ENDTIME`, runs
   `M-REPRO`. **Launches nothing.**
4. `bash launch_k2g.sh --check-only K2f_L3 4 18000` → must print `ASSERT OK`.
5. **The launch is authorised personally by the heat-transfer supervisor and by
   nobody else**, after reading this document and the comparator diff:
   `bash launch_k2g.sh K2f_L3 4 18000`.
6. `python3 analyse_k2g.py --grade --json K2g_GATE.json`.

**Exit map:** 0 OK, 1 GATE FAIL, 2 REFUSE, 3 NOT A RESULT. **No verdict may be
read from an exit code**; the verdict is the word the comparator prints.

*Nothing in this rung is sent, filed, uploaded, registered, posted or commented
outside this box (rule 7).*

---

## 10. FREEZE BLOCK — sha256 OF THE DISK BYTES OF EVERY FILE ON THE GRADING PATH

The comparator re-reads this block at grade time and **refuses if any file on
disk is not the file pinned here**. This document's own hash is not in the table:
it is the table.

```json FREEZE
{
 "verification/runs/F14-cooling-ladder/K2g_runs/analyse_k2g.py": "f8383461bfbd9ca02886e263da26c2540c88a5417090501b243ce69f510815c3",
 "verification/runs/F14-cooling-ladder/K2g_runs/foam_patch_reader.py": "f3ee1fcf6d971724613a899d90b8cc654bf5d341794ae00a042193e678d06e03",
 "verification/runs/F14-cooling-ladder/K2f_runs/build_k2f.py": "9c369c68d155faed3f86ca0fb2bed9a6f65d32535e238e687529ce19e29f6583",
 "verification/runs/F14-cooling-ladder/K2f_runs/mark_done_k2f.py": "5c3674b3ffd4ce3f23ec0028fb5bb44ad63b0701e5139fa873105f270ca9bc89",
 "scripts/roache_triple.py": "fcae041ffb22c48735cbd6b045507818802f504eda503adf612ae2a581aa79d8"
}
```

`launch_k2g.sh` is pinned by this document's own commit and is not in the table:
it starts the run and cannot be a grading-path input.
