# T5b — Meinders 1998 heated wall-mounted cube, with the instrument connected: pre-registration (FROZEN)

**Version 1.0. Rung `T5b`. Family: T. Team: heat-transfer.**
**Status: FROZEN at this commit. No T5b case has run.**

`T5b` is the successor rung to `T5`. It registers the **same geometry, the same
`r = 1.6` mesh ladder, the same closure, the same schemes, the same `endTime` and
the same reference** as `T5`, and changes **one thing**: the function objects that
were configured so that they never executed now execute. Everything a verdict
rests on that T5 could not measure, T5b measures.

This document is prediction-first. The gate, the band, the threshold, the cap and
the label below are committed **before** any T5b solver starts, and the freeze is
this document's entire evidentiary content.

---

## 1. WHY THIS RUNG EXISTS — three defects, each MEASURED, none inferred

T5's `y+` gate (`T5_PREREGISTRATION.md` §16.3.1) registers five clauses, each of
which returns `NOT A RESULT`. **Three independent defects each fire one of those
clauses on every graded row of every level, by construction.** Any one of them
alone is sufficient.

### D1 — the function object never executed

T5's `system/controlDict` gives both function objects:

```
writeControl    writeTime;
writeInterval   1000;
```

The run's own `writeInterval` is **1000 timeSteps** and `endTime` is **5000**, so
the run has exactly **five** write times. `writeControl writeTime` with
`writeInterval 1000` means *"on every 1000th write time"* — and only five exist.
`write()` therefore **never ran**.

**Measured, not reasoned.** On T5's coarse level,
`verification/runs/T-family/T5_runs/T5_CUBE_c/postProcessing/air/yPlus/0/yPlus.dat`
carries **two header lines and ZERO data rows**. The same holds on `m` and `f`.
No `yPlus` field exists in any time directory.

`wallHeatFlux`, under the **identical** control, wrote **30,002 lines** to
`.../wallHeatFlux/0/wallHeatFlux.dat` — because *its* `.dat` rows come from
`execute()` (default `executeControl timeStep`, interval 1) while its **field**
comes from `write()`. One mechanism; the two objects differ only in which method
emits which artefact. That asymmetry is why the defect was invisible for a day.

**Third consequence, and it is the expensive one.** `write()` also never emitted
the local `wallHeatFlux` **field**, so only per-patch `min`/`max`/`integral` were
recorded. A face-averaged `h` is

    h̄_face = (1/A) ∫ φ″_conv / (T_sur − T_ref) dA

and that is **not** `∫φ″ / (A (T̄_sur − T_ref))` when `T_sur` varies over the face
— and making `T_sur` vary is the entire point of a conjugate rung. Without the
local field, T5's graded rows **G1a–G3a are not evaluable**.

### D2 — a registered wall that cannot exist

T5's `YPLUS_WALLS` names **seven** walls including `cube_side_s`. The registered
geometry (T5 §5.2) is a **half domain** with a symmetry plane at `z/H = 0`, so
`cube_side_s` **is not a patch in any T5 mesh**. Confirmed directly: the six
patches the `yPlus` function object reports are `cube_front`, `cube_rear`,
`cube_side_n`, `cube_top`, `floor`, `roof` — and the function object reports
*every* wall patch, so that list **is** the mesh's wall set.

T5's own **AMENDMENT 3** found this, proposed the repair, and records it as
**PROPOSED, NOT ADOPTED**, with its consequence stated in the document's own
words:

> *"Until adopted, §16.3.1's 'a wall not reported -> NOT A RESULT' fires on every
> level by construction."*

### D3 — a reader with no writer

T5's comparator reads **`yPlus.json`**. **Nothing in this repository has ever
written `yPlus.json`** — the function object writes
`postProcessing/air/yPlus/0/yPlus.dat`. A repository-wide search for a producer
returns only the two comparators that *read* it. Even a firing function object
and a correct wall list would still have returned `NOT A RESULT`.

---

## 2. THE RULING THAT T5's VERDICT STANDS — and why `postProcess` was not re-run

**`postProcess` may NOT be re-run on T5's completed cases to recover `y+`.**
T5 §16.3.1 registered the absence of `y+` as `NOT A RESULT` **before compute**.
Manufacturing the missing measurement after the fact, specifically to escape a
registered verdict, is answer-changing, and Sanaa's standing directive of
2026-08-27T16:54Z §3 forbids it in terms:

> *"Answer-changing choices (model, scheme class, formulation) are never selected
> by agreement with the reference. ... Frozen gates never edited post-compute."*

**T5's `NOT A RESULT` STANDS.** It is not reopened, restated, relaxed or graded
again by this document. `T5_PREREGISTRATION.md` and `T5_RESULTS.md` are untouched.
The legitimate route is a successor rung with the defect repaired, and D2 and D3
independently confirm the ruling: even with recovered `y+` data, two of the three
defects would still fire.

---

## 3. THE REPAIR, AND THE PROOF THAT IT FIRES — measured 2026-08-27

**A registration whose central repair is unproven is worthless**, so the repair
was driven on a scratch copy of the built coarse case **before this document was
frozen**, in a planted-failure pair (Sanaa §1: *"Every guard ships its
planted-failure proof"*).

Four arms, each 20 iterations of `chtMultiRegionSimpleFoam` on the 52,684-cell
coarse mesh, `endTime 20`, run `writeInterval 10` (so the run has two write
times, the same 1:1 relation the production case has at 5000/1000). All four
`rc = 0`, all four reached `Time = 20` with an `End` line.

| arm | `yPlus` function object | `yPlus.dat` DATA ROWS | `yPlus` field | `wallHeatFlux` field |
| --- | --- | ---: | --- | --- |
| **CONTROL** — the defect preserved verbatim | `writeControl writeTime; writeInterval 10` | **0** | absent | absent |
| **FIX** — the one keyword changed | `writeControl timeStep; writeInterval 10` | **12** | present | absent |
| **FIX2** — both objects changed | `timeStep` on both | **12** | present | **present** |
| **REGISTERED** — the configuration this rung freezes | `executeControl timeStep; executeInterval 1; writeControl timeStep; writeInterval 10` | **12** | present | **present** |

**The CONTROL arm reproduces the defect exactly: zero rows.** The FIX arm differs
from it in one keyword and produces rows. That is the planted-failure proof: the
guard is shown able to fail before it is believed when it passes.

The REGISTERED arm additionally shows:

- **12 y+ data rows** = 2 write events × **6 walls**, and the six are exactly
  `cube_front, cube_rear, cube_side_n, cube_top, floor, roof` — the mesh's own
  wall set, with `cube_side_s` correctly absent (D2).
- **120 `wallHeatFlux` data rows** = 20 timeSteps × 6 patches: T5's dense
  per-iteration convergence trace is **preserved**, not traded away.
- The `wallHeatFlux` **field** at `20/air/wallHeatFlux` is `nonuniform
  List<scalar>` with **98 face values on `cube_front`** — the local `φ″_conv`
  that makes G1a–G3a evaluable (D1's third consequence).
- **Exactly two time directories** (`10`, `20`) — the run's own write times. No
  extra directory is created and `purgeWrite 3` is unaffected. This is why
  `writeInterval` on the function object is set **equal to the run's own**
  `writeInterval` rather than to something smaller: a smaller value would write
  fields at non-write times, create dozens of time directories, and interact
  badly with `purgeWrite`.

**Cost of this instrument proof: 0.337 core-minutes** (four arms, ExecutionTime
4.37 + 4.13 + 5.72 + 6.01 s at 1 rank), spent in scratch, on no registered case,
producing no graded value. USD 0.00029 **derived at $0.0513/core-h, not measured**
— this box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

---

## 4. THE DESIGN — what is the same, and the one thing that is not

**REGISTERED UNCHANGED FROM T5**, and this is the point of a successor rung:
geometry (`H = 15 mm`, half domain, symmetry at `z/H = 0`), the `r = 1.6` ladder
and its cell counts, `kOmegaSST` at `Pr_t = 0.85`, `Gauss harmonic corrected` on
the solid laplacian, every scheme and relaxation factor, `endTime 5000`,
`deltaT 1`, `writeInterval 1000`, `purgeWrite 3`, all boundary conditions, the
thermophysical properties, and the `X_2d` precursor inflow map.

The inflow map is **copied from T5's built cases and digest-verified**, not
re-derived: measured byte-identical across T5's three levels — 4 files,
83,071 bytes, directory digest
`b1741eb9ae4288e1f8e8bfaba3fad43fba422b872f2d761602b6724197b0e103`. `build_t5b.py`
**refuses** if that digest moves, because a different inflow is a different rung.

**THE ONE SUBSTANTIVE CHANGE**, on **both** function objects:

```
executeControl  timeStep;
executeInterval 1;
writeControl    timeStep;
writeInterval   1000;
```

`build_t5b.py` is a **wrapper**, not a fork: it drives the frozen
`../T5_runs/build_t5.py` and then applies exactly this change, asserting on
**content** (never a line count — a line-count check passes on a substituted file
of the right length) and reading the result back from disk. A supervisor's
check-1 is therefore a thirty-second diff.

### The ladder, MEASURED

| level | case | cells (from its own `log.checkMesh`) | `y+_max` target |
| --- | --- | ---: | ---: |
| `c` | `T5_CUBE_c` | **52,684** | 2.6 |
| `m` | `T5_CUBE_m` | **212,942** | 1.6 |
| `f` | `T5_CUBE_f` | **882,024** | 1.0 |

Refinement ratios **derived from those counts, never typed**:
**`r21 = 1.6060`** (fine/medium) and **`r32 = 1.5929`** (medium/coarse). The
comparator is passed the measured ratios. Leaving the `r = 2.0` default is not a
rounding choice: on a synthetic triple it moves the observed order from
**2.709 to 1.807**, which the comparator's selftest prints.

---

## 5. THE `y+` GATE — six walls, checked in BOTH directions

**Registered `YPLUS_WALLS` = `cube_front`, `cube_top`, `cube_rear`,
`cube_side_n`, `floor`, `roof` — SIX.**

| clause | registered value | failure |
| --- | --- | --- |
| sublayer bound, every wall | **`y+_max ≤ 5.0`** | `NOT A RESULT` |
| level target | `c` 2.6 / `m` 1.6 / `f` 1.0 | — |
| ladder tolerance | achieved ≤ **2.0 ×** the level target | `NOT A RESULT` |
| a wall not reported | — | `NOT A RESULT` |
| `yPlus.dat` absent **or carrying zero data rows** | — | `NOT A RESULT` |
| a **registered** wall absent from the mesh | — | **REFUSAL (exit 2)** |
| a **mesh** wall the gate does not name | — | **REFUSAL (exit 2)** |

The last two rows are new and they are D2's repair. T5's gate could name a wall
that did not exist and only discovered it at grade time. T5b's comparator reads
`constant/air/polyMesh/boundary`, takes every patch whose type ends in `wall`
(measured: `floor` and `roof` are `wall`; the four cube faces are `mappedWall`,
because they *are* the conjugate interface — a check accepting only `wall` would
silently drop every face this rung grades), and **refuses in either direction**.
T4's control C1 is the reason: it fired at `y+ 1.248` on the plate while the pipe
wall sat at `y+ ≈ 30`, unseen, because the gate named one wall.

---

## 6. THE ROWS, THE BANDS, THE PREDICTION AND ITS FALSIFIER

**Reference:** `verification/runs/T-family/T5_runs/T5_reference_primary.json`,
HEAD blob **`04dfd7e2e56adf1cd0924046500904af2243b747`**, digitised 2026-08-26
under T5 AMENDMENT 7 from Meinders (1998) Figs 5.45 and 5.37. **T5b does not
re-digitise anything.** Band arithmetic is T5 §7.3's, unchanged:
`band = sqrt(stated² + digitisation²)`.

| row | quantity | class | band basis |
| --- | --- | --- | --- |
| **G1a** | face-averaged `h`, front face, fine level | **GRADED** | Fig. 5.45, 10 % stated ⊕ digitisation |
| **G2a** | face-averaged `h`, top face | **GRADED** | as G1a |
| **G3a** | face-averaged `h`, rear face | **GRADED** | as G1a |
| **G5a–c** | area-mean `T_sur`, front / top / rear | **GRADED** under the §3 identity guard | 0.4 °C stated ⊕ digitisation of Fig. 5.37 |
| G1–G3, G4, R1–R3 | mid-line `h`, reattachment, shape rows | **REPORTED** | — |

**Intrinsic floor carried unchanged from T5 §7.4:** a deviation below **1.7 %**
returns `GATE REACHED`, not `PASS` — the rung cannot resolve it. (The floor is
the thesis's "20–21 °C" ambient half-range on a ≈ 30 K driving difference.)

**Ruling D534** (Sanaa APPROVED 2026-08-27): `REPORTED` is a **ROW CLASS, not a
verdict**. Every REPORTED row is **excluded from the N-of-M census**, and the
comparator's tally line says so in words, naming the excluded rows.

### THE PREDICTIONS, AND WHAT WOULD FALSIFY EACH

**P1 — the instrument.** All three levels produce `yPlus.dat` with **6 rows at
`Time = 5000`**, one per registered wall, and a `wallHeatFlux` field at
`5000/air`. *Falsifier:* fewer than 6 rows on any level, or an absent field. This
is the prediction the rung exists to test and it is the one most likely to be
right, because it was driven in §3 before the freeze.

**P2 — the `y+` gate.** The gate returns **MET on all three levels**: every wall
at `y+_max ≤ 5.0` and within 2× the level target.
*Falsifier:* any wall over. **THE KNOWN RISK, STATED RATHER THAN HIDDEN:** in the
§3 probe at **iteration 20 — a transient, not a converged value, and it is not a
result** — `cube_front` read `y+_max = 5.28`, above the 5.0 bound. T5's design
predicts `y+_max ≈ 2.6` on the coarse level *at convergence*, and the probe's
number is 250× short of the run. But it is the honest reason P2 is a prediction
and not an assumption: **if the converged coarse level lands above 5.0, the
coarse level is `NOT A RESULT` and the triple collapses with it.** That outcome is
registered here in advance so it cannot later be presented as a surprise.

**P3 — the graded rows.** **At least two of G1a, G2a, G3a PASS** inside their
bands at the fine level. *Falsifier:* fewer than two PASS.
**Named in advance as the most likely to fail: G1a, the front face.** T5 §7.4
registers up to **5 % local** unmodelled base-plate conduction at the front-face
foot, and the horseshoe-vortex foot is the least well resolved region on the
ladder. If exactly one row fails and it is G1a, the prediction is **correct**; if
one fails and it is not G1a, the prediction is **half wrong and will be recorded
as half wrong.**

**P4 — the triple.** All three graded `h` rows return a **CONVERGING** triple.
*Falsifier:* any of DIVERGENT / STAGNANT / OSCILLATORY / EXACT — which returns
`NOT A RESULT` whatever the value, rule 5, and cannot be argued out of.

---

## 7. TRIPLE GATING — the registered order, binding

A graded row's verdict is decided top to bottom and stops at the first clause
that fires:

1. any level's `y+` gate not `MET` → **`NOT A RESULT`**;
2. triple `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` → **`NOT A RESULT`**,
   the fine value and the triple printed beside it;
3. reference value absent → **`BLOCKED`**, fine value and triple REPORTED;
4. G5 only: the reference `T_sur` within **5.0 K** of either imposed bound
   (20.5 °C inlet, 75.0 °C copper core) → **`NOT A RESULT — identity`**;
5. deviation below the **1.7 %** intrinsic floor → **`GATE REACHED`**;
6. otherwise **`PASS`** inside the band, else **`GATE FAIL`**, GCI printed.

GCI at **`Fs = 1.25`**, unequal-ratio fixed-point form on the **measured**
`r21 = 1.6060` / `r32 = 1.5929`. **Never quoted when the three values are not
monotone.** The gate can turn a PASS or a GATE FAIL **into** `NOT A RESULT`, never
the reverse.

---

## 8. CONTROLS — every one driven, none asserted

### 8.1 Rule 3, planted zero, SIZED TO EACH READER'S SHAPE (L-340)

A constant offset is **invisible to a range or dispersion reader by
construction**, so planting only one shape proves only one reader. T5b plants
**two**, into a copy, and reads both back through the **real** readers before any
value is graded:

- **constant offset `1.234e-03`** through the **area-mean** reader — refuses if
  the mean does not move by exactly that amount;
- **single-cell spike `9.876e+02`** through the **range/max** reader — refuses if
  the maximum does not move by it.

A failure of either is a **refusal (exit 2)**, not a degraded run.

### 8.2 L-342 field classes, DECLARED IN THE GRADER

Copying the shape the audit names as the family's best,
`verification/runs/T-family/T3_runs/mark_done_t3_rff.py:8-18` (classes declared
in the docstring) with a selftest at `:143-144` driving **both** halves:

- **PHYSICS-CRITICAL** (failure → `NOT A RESULT`; absence refuses): the solver
  `rc` **value**; the `End` line; last time == `endTime`; `T U p_rgh alphat nut k
  omega` present at `endTime`; the `ExecutionTime` **iteration** count; the age
  guard; and the `y+` measurement.
- **GATE INPUT, never infrastructure:** `yPlus.dat`. §5 registers its absence as
  `NOT A RESULT`; reclassifying a registered gate input as infrastructure would
  convert a registered `NOT A RESULT` into a bookkeeping note, which is the gaming
  shape. The comparator's negative control **N4** mutates exactly that
  classification and the selftest fails.
- **INFRASTRUCTURE** (reported, stated `NOT MEASURED`, **never** a refusal):
  `wall_s`, `ranks`, `core_min`, `cap_core_min`, `timeout_s`, `capped`,
  `checkMesh_rc`, the `ExecutionTime` **line** count as distinct from the
  iteration count, ledger rows, pids, `log.launch`, `CAP_ENFORCED.txt`, marker
  mtimes.

**Ruling R-RC** (Sanaa APPROVED 2026-08-27) is implemented literally: the `rc`
**value** is physics, the `rc` **record** is infrastructure. An absent `STATUS`
file is `NOT MEASURED`, and `rc = 0` is then printed **as a labelled inference,
never as a reading** — and only when the other four rule-4 conditions hold. A
`FOAM FATAL` or a signal token in `log.solve` **still refuses** regardless.

### 8.3 The patch-area reader, proven against a value known by construction

The graded `h` is area-weighted, so the comparator reads face areas from
`constant/air/polyMesh`. That reader is **proven, not trusted**: on the built
coarse mesh it returns `cube_front`, `cube_top` and `cube_rear` at
**1.125000000e-04 m²** each — exactly the analytic `H × (H/2)` on the half domain
— and `cube_side_n` at **2.250000000e-04 m² = H × H**, to ten significant figures.
The floor comes back at **3.138750000e-02 m²**, which is `28H × 5H` **minus the
cube footprint**, again exact. The selftest drives the `cube_front` identity.

### 8.4 Discipline

**0 `ast.Assert`** in `analyse_t5b.py` and in `build_t5b.py` (L-332).
`--selftest` output is **byte-identical under `python3` and `python3 -O`**:
**42 arms, 0 failed** for the comparator; 7 arms, 0 failed for the builder.
Four **negative controls** mutate the real source, clear `__pycache__` between
the control and the mutant, and each makes the selftest fail:

| control | mutation |
| --- | --- |
| **N1** | the `y+` sublayer bound raised so a wall at 30 passes |
| **N2** | `cube_side_s` put back into `YPLUS_WALLS` — **defect D2 restored** |
| **N3** | a `DIVERGENT` triple allowed to reach the band |
| **N4** | `yPlus.dat` reclassified as infrastructure |

### 8.5 The reference-leak control, which is enforced rather than promised

**THE AUTHOR OF THIS RUNG'S COMPARATOR HAS READ THE REFERENCE VALUES.** They are
at HEAD and this lane read them while scoping T5b. T5 §S10 registered the opposite
ordering and for T5b it is **broken and cannot be repaired by anything written
here.** The one auditable mitigation is that **no reference value is hard-coded
in the comparator** — and that is not asserted, it is **enforced**: `--selftest`
reads the comparator's own bytes, scans them for every `value`, `uncertainty` and
`digitisation_increment` in the frozen reference JSON, and **fails if one
appears.**

---

## 9. COST — MEASURED basis, and every figure sourced

**The basis is T5's own triple**, which is the ideal calibration: the same mesh,
the same solver, the same `endTime`, the same ranks, on this box. From
`verification/runs/T-family/T5_runs/STATUS.T5_CUBE_{c,m,f}` (all `rc = 0`,
`capped = 0`):

| level | cells | wall s | core-min | **s per cell-iteration** |
| --- | ---: | ---: | ---: | ---: |
| `c` | 52,684 | 965 | **16.083** | 965 / (52,684 × 5000) = **3.664e-06** |
| `m` | 212,942 | 4,539 | **75.650** | **4.263e-06** |
| `f` | 882,024 | 19,150 | **319.167** | **4.342e-06** |

The rate rises mildly with size and is converging toward ≈ 4.34e-06 s per
cell-iteration — consistent with cache pressure, and it is *reported*, not
smoothed away.

**POINT = measured × 1.02.** The 2 % is an **ALLOWANCE** for the repaired function
objects' extra field writes (five per case per object). It is **NOT measured**: at
the 20-iteration probe scale the effect is smaller than the contention noise on an
88 %-busy box, so it is declared as an allowance rather than dressed up as a
measurement.

**CAP = 2.0 × POINT.** The 2.0 is **contention headroom on a saturated box, not
model uncertainty** — the POINT is a same-case measurement whose expected
actual/predicted ratio is 1.00. The cap is a runaway guard, never a target.

| level | POINT core-min | **CAP core-min** | derived timeout s at 1 rank |
| --- | ---: | ---: | ---: |
| `c` | 16.4 | **32.8** | 1,967 |
| `m` | 77.2 | **154.4** | 9,264 |
| `f` | 325.6 | **651.2** | 39,072 |
| **total** | **419.2** | **838.4** | — |

**419.2 core-min = 6.987 core-hours. USD 0.3584 at the POINT and USD 0.7168 at the
CAP**, derived at the owner-stated $0.0513/core-h — **derived, not measured**: the
box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25
pre-authorisation by a factor of about 70; still costed, because a blanket is not
a per-item read (rule 9).

The derived timeout is **truncated**, not rounded (1,967 s from 32.8 × 60 = 1,968).
Truncation is the safe direction: a cap can only come out **smaller** than
registered, never larger.

**Estimate-versus-actual calibration** (rule 12, Sanaa 2026-08-23) will be filed
as a row in `docs/COST_CALIBRATION.md` at each level's completion, stating the
actual/predicted ratio and attributing the gap, with waste named separately.

---

## 10. THE CAP IS ENFORCED — and the proof is driven

**Finding F6 against T5, quoted verbatim from
`verification/runs/T-family/T5_runs/T5_CUBE_c/CAP_OVERRUN.txt`:**

> *"CAP OVERRUN REPORTED, NOT ENFORCED: case T5_C elapsed 11433 s > 1.10 x
> registered 2736 s (45.6 core-min / 1 ranks). The run was NOT killed (caps
> report; COMPUTE_BUDGET_CHARTER)."*

That breaches rule 12, under which **an overrun stops the run**. The mechanism is
now understood and it is worth naming precisely, because the diagnosis changes the
fix: `run_one_t5.sh` **does** run its solver under `timeout` and would have killed
it. What failed is that **the wall-seconds in the queue argv were typed by hand,
independently of the registered cap** — `STATUS.T5_CUBE_c` records
`timeout_s = 8208` (136.8 core-min) against a registered 45.6. The overrun
detector that printed the file above is the **queue runner's**, and *it* reports
without killing. **A cap that reports is not a cap, and a cap an argv can widen is
not a cap either.**

`run_one_t5b.sh` closes both halves:

1. **There is no `--timeout`.** It takes `--cap-core-min` and derives the wall
   seconds itself. It reads the **frozen `T5B_CAPS.txt`** and **REFUSES** unless
   the argv's cap equals the registered row for that case, printing
   `CAP AGREES <case> <cap>` before the solver starts.
2. **`timeout --kill-after=120 --signal=TERM`.** Bare `timeout` sends SIGTERM; a
   solver that ignores it keeps running and the cap is advisory again. SIGKILL
   follows the 120 s grace, and nothing survives SIGKILL.
3. On expiry it writes `CAP_ENFORCED.txt` and a `STATUS` note naming the stop as
   a right-censored `PENDING`, not a failure. `capped` is still taken from the
   **wall clock**, an independent witness no dying process can forge —
   `run_one_t5.sh`'s B1 finding is adopted verbatim, and `--preserve-status` is
   still refused for the reason recorded there.

**PROVEN, 2026-08-27, by `run_one_t5b.sh --drive-cap-kill`** — the same
enforcement line the solver runs under, driven against known children:

| arm | child | cap | wall | rc | outcome |
| --- | --- | ---: | ---: | ---: | --- |
| 1 | well-behaved `sleep 600` | 5 s | **5 s** | 124 | **STOPPED at the cap** by SIGTERM |
| 2 | **SIGTERM-ignoring** `sleep 600` | 5 s (grace 3 s) | **8 s** | 137 | **KILLED** by SIGKILL after the grace |
| 3 | `sleep 2` — the negative half | 30 s | 2 s | 0 | **untouched**, ran to completion |

Arm 3 is not decoration: a killer that kills everything is not a cap either. The
drive uses a 3 s grace so the proof finishes in seconds; production uses 120 s, and
a longer grace can only **delay** a kill, never prevent one.

Three further refusals are driven and each leaves **no `STATUS` file and no `0/`**
— nothing is armed by a refusal: a cap that disagrees with `T5B_CAPS.txt`; a case
with no row in that table; a controlDict that still carries a `writeTime` control
(the launcher refuses to burn the budget reproducing the defect this rung exists
to remove).

---

## 11. THE FREEZE SET

Frozen at this commit. The grading path is fixed here and every file is verified
by hashing it against the committed blob before it is believed.

| file | role |
| --- | --- |
| `docs/campaigns/T-family/T5b_PREREGISTRATION.md` | this document |
| `verification/runs/T-family/T5b_runs/build_t5b.py` | the builder — drives the frozen `build_t5.py` and applies the one change |
| `verification/runs/T-family/T5b_runs/analyse_t5b.py` | the comparator; **its `main()` grades** |
| `verification/runs/T-family/T5b_runs/run_one_t5b.sh` | the launcher, with the cap enforced |
| `verification/runs/T-family/T5b_runs/T5B_CAPS.txt` | the cap table the launcher checks against |
| `verification/runs/T-family/T5_runs/T5_reference_primary.json` @ `04dfd7e2` | the reference, unchanged and not re-digitised |

**Carried unchanged and NOT re-frozen:** `../T5_runs/build_t5.py` and the T5
registration, both cited by path and blob. **Rule 6: no frozen file was edited.**
`T5_PREREGISTRATION.md`, `T5_RESULTS.md`, `analyse_t5.py` and every T5 amendment
are untouched by this rung.

---

## 12. WHAT THIS RUNG CANNOT SEE

- **It does not re-open T5.** T5's `NOT A RESULT` stands (§2).
- **It inherits every model-form limitation of T5** — the roof boundary layer is
  modelled fully turbulent against a thesis that describes it as "a developing
  laminar boundary layer" (T5 INTERPRETATION 6); the copper core is not meshed;
  radiation is off; the base plate is not conducting.
- **It inherits the digitised reference and its band**, including T5 §16.4's
  finding that Fig. 5.39's digitisation increment is the size of the experiment's
  own stated uncertainty — which is why the **face-averaged** set is graded and
  the mid-line set is REPORTED.
- **The comparator's author has read the reference values** (§8.5). No ordering
  claim is made that this rung cannot support.
- **P2 may fail on the coarse level** and take the triple with it (§6). That is
  registered in advance, not discovered afterwards.

---

## 13. STATUS

**FROZEN.** Three cases built and unarmed — `T5_CUBE_c`, `T5_CUBE_m`,
`T5_CUBE_f` under `verification/runs/T-family/T5b_runs/`, cell counts verified
against §4, **none holding a `0/` or a numeric time directory** (checked by the
comparator's `--selftest`, which prints the condition).

**`N of M` is `0 of 6` until it has run.** A plan is not a capability.

**Nothing in this rung was sent, filed, uploaded, posted, registered or commented
outside this box (`CLAUDE.md` rule 7).**
