# A1WCT — WALL-RESOLVED COMPRESSIBLE TRIAGE — **PRE-REGISTRATION, DRAFT**

> ## ⚠ THIS IS A DRAFT. IT IS NOT FROZEN, NOT COMMITTED AS A FREEZE, NOT ENQUEUED, AND NO SOLVE HAS BEEN RUN AGAINST IT.
>
> No compute of any kind has been spent on this item. No run root exists. No queue row
> exists. The gate names, thresholds, caps, labels, verdict class and verdict ceiling
> below are **proposed**, and the cap arithmetic is **evaluated but not ratified**.
> `dafoam-supervisor` reads this personally and checks the cap arithmetic himself before
> anything here is frozen — that is `SUPERVISION_CHARTER.md` §3 check 4 and it is not
> delegable. **Nothing in this file is filed, sent, uploaded, registered or posted
> outside this box (`CLAUDE.md` rule 7).**

**Item id:** `A1WCT`
**Family:** dafoam, ladder A, A1 (NACA0012)
**Purpose:** separate the three candidate mechanisms named in `docs/LAB_STATE.md` dafoam
`S-27` §9 — **one variable per arm** — for the established failure of `DARhoSimpleFoam`
on the A1WR L3 wall-resolved mesh.
**Drafted:** 2026-09-03 (`date -u` in the drafting invocation)

---

## 1. WHAT IS ALREADY ESTABLISHED, AND WHAT THIS ITEM IS THEREFORE NOT ALLOWED TO RE-ASK

These are **measured** and are cited from `S-27` as corrected by `S-28`. Where `S-28`
corrected an `S-27` figure, the corrected value is used and the superseded one is not
quoted.

| fact | value | artefact |
|---|---|---|
| `DARhoSimpleFoam` on A1WR L3 | **0 of 11 solves converged**, min residuals **0.6363–0.8993** | `S-27` §1 |
| bounding on every failing solve | `p`, `rho`, `e` **and** `U`, first appearing in the **`Time = 1`** block | `S-27` §1, §3 |
| `DASimpleFoam` on the **same** L3 mesh, same item, np=1 | **CONVERGED**, `Minimal residual 9.997083655914609e-09 satisfied the prescribed tolerance 1e-08` | `S-27` §1 (MAAOA `INCOMP`) |
| bounding on that converging solve | **`nuTilda` only**; zero `p`/`rho`/`e`/`U`. Count **138** (final; `S-27`'s 71 was a mid-run read, corrected by `S-28` §2) | `S-28` §2 |
| `DARhoSimpleFoam` on the **coarse** wall-functioned mesh (4,032 cells, AR 97.87) | **CONVERGED at iteration 502**, wall **5.755 s**, bounding = 6 × `nuTilda` and nothing else | `S-27` §1 (Pair B) |
| failure is not Mach and not alpha | fails at **α = 0** and at M 0.288, the family's converged anchor | `S-27` §2 |
| residual trajectory | `1.000 → 0.6075 → 0.3762 → 0.5246 → … → 0.6363` — falls, **reverses**, stalls high; **never below 0.3762** | `S-27` §3 |

**Therefore it is neither the solver alone nor the mesh alone: it is the combination, and
each half is proved harmless by the other pair.** This item does not re-establish that.
It takes it as the premise and asks **which** difference between the two grounds drives it.

**The residual trajectory is consistent with all three candidates and discriminates
between none** (`S-27` §3). That is precisely why the arms below vary one thing each.

---

## 2. THE THREE CANDIDATES, AND THE MEASUREMENTS THAT DEFINE THEM

Taken from `S-27` §9 and re-measured for this draft from the artefacts, not relayed.

### (a) Extreme cell aspect ratio meeting the pressure–density–energy coupling

| level | R | cells | `nSurfaceCells` | `nWallNormalCells` | `s0` | growth | `ZSpan` | `marchDist` |
|---|---|---|---|---|---|---|---|---|
| L1 | 1 | 8,064 | 126 | 64 | 2.5e-06 | 1.25483 | 0.1 | 20 |
| L2 | 2 | 32,640 | 255 | 128 | 1.25e-06 | 1.11964 | 0.1 | 20 |
| **L3** | **4** | **130,304** | **509** | **256** | **6.25e-07** | **1.05800** | **0.1** | **20** |

*(`/home/ubuntu/certonomous-runs/A1WR/STAGE0.log`, `BUILT` lines and the generator's own
level table; `/home/ubuntu/certonomous-runs/A1WR/a1wr_genmesh.py:65,158,179,216.)*

**⚠ A CORRECTION TO `S-27` §9's OWN PROPOSAL, FOUND WHILE DRAFTING THIS.** `S-27` §9
proposes candidate (a) be tested by *"a mesh level with a sane aspect ratio (L1/L2 already
exist)"*. **That arm would be a four-variable change and this draft refuses it.** Moving
L3 → L1 changes, simultaneously: cell count (16×), chordwise spacing (4×), first-cell
height `s0` (4×), and aspect ratio (4×). A result from it could not attribute a mechanism
to any one of them. **This family has refused a two-variable change three times; a
four-variable one is not the way to end that streak.**

**What the aspect ratio is actually made of, measured.** `a1wr_genmesh.py:216` registers
`MUST_NOT_SCALE = ["marchDist", "ZSpan", "nSpan"]` — the span width is held **constant at
0.1** across the refinement family while `s0` scales as `1/R`. The maximum aspect ratio is
therefore governed by the span-to-first-cell-height ratio and scales as `R`:

| level | `ZSpan / s0` | implied max AR at the measured L3 ratio 1.32565 |
|---|---|---|
| L1 | 40,000 | ≈ **53,025.9** |
| L2 | 80,000 | ≈ **106,051.8** |
| **L3** | **160,000** | **212,103.67 — MEASURED**, printed by every MAAOA log (`S-27` §1) |

The constant 1.32565 = 212103.6706991908 × 6.25e-07 / 0.1 is exact at L3 and reproduces
L1 and L2 by pure scaling; it is the geometric factor relating `checkMesh`'s governing
long dimension to the bare span, and it is **not** re-derived here — the L1 and L2 figures
above are therefore **DERIVED, not measured**, and Arm `A` does not depend on them.

**The clean knob this exposes.** The mesh is a 2-D case, **one cell thick in z**
(`a1wr_genmesh.py:65`, `:402`), with `empty` end patches. **The span carries no physical
content whatever.** Shrinking `ZSpan` therefore changes the maximum aspect ratio by
exactly the factor applied, at **identical cell count, identical chordwise resolution,
identical `s0`, identical y+, identical boundary conditions and identical physics.** That
is the only genuinely one-variable aspect-ratio change available in this family, and it is
strictly better than the L1/L2 arm `S-27` proposed.

### (b) `alphat` wall treatment — the difference that exists only on the failing side

**Measured directly from the two logs, not relayed:**

| ground | log line |
|---|---|
| A1WR L3 (fails) | `Setting alphat wall BC for wingBCType=fixedValue` |
| coarse AOAC (converges) | `Setting alphat wall BC for wingBCType=compressible::alphatWallFunction. Default Prt=0.85` |
| A1WR L3, `nut` | `Setting nut wall BC for wing. BCType=nutLowReWallFunction` |

`alphat` is the **turbulent thermal diffusivity** and is a **compressible-only field** —
the incompressible arm does not have one. **This difference exists on precisely the side
that fails and cannot exist on the side that works**, which is what makes it a candidate
rather than a coincidence. It is set by `useWallFunction: False`
(`cases/dafoam/ladder-a/A1/wall_resolved_aoa_polar/a1wr_runScript_comp.py:76`).

### (c) `system/fvSolution` never retuned for the finer, higher-AR mesh

**Byte-identity re-verified for this draft, by hashing both files:**

```
ff25e4462dbee92b9bfa72513dc51662  /home/ubuntu/certonomous-runs/A1WR/STAGE12/sweep_C/case/system/fvSolution
ff25e4462dbee92b9bfa72513dc51662  /home/ubuntu/certonomous-runs/CURRICULUM-AOAC-.../case/system/fvSolution
```

The contents, both meshes:

```
relaxationFactors { fields    { "(p|p_rgh|rho)"                     0.30; }
                    equations { "(U|T|e|h|nuTilda|k|epsilon|omega)" 0.70; } }
SIMPLE            { nNonOrthogonalCorrectors 0; }
```

A steady compressible SIMPLE solve on a **32× finer** grid with **2,167×** the aspect
ratio inherited, unchanged, the relaxation schedule tuned on a 4,032-cell wall-functioned
grid. **`nNonOrthogonalCorrectors = 0` is part of that same inheritance** and is treated
below as a separate sub-candidate, because it is a different physical mechanism (skewness
/ non-orthogonality error in the pressure equation) from the relaxation schedule and
cannot share an arm with it.

### A fourth measured fact, recorded because it explains why nothing objected

`a1wr_runScript_comp.py:70` sets `checkMeshThreshold: {"maxAspectRatio": 5.0e5, ...}`.
**The threshold was set above the mesh's own aspect ratio of 212,103.67**, so DAFoam's own
mesh check could not object to it. This is recorded as context; **it is not a candidate
mechanism and no arm varies it.**

---

## 3. VERDICT CLASS, CEILING, AND WHAT MAY NEVER BE CLAIMED HERE

**`VERDICT_CLASS = G-NOBAND`.** This mesh family has **no Roache triple** for any quantity
this item measures. L1/L2/L3 exist, but they are not a valid refinement triple for a
convergence-behaviour question because, as §2(a) shows, they move four things at once.
**Nothing this item produces is grid-converged, and no band may be claimed for any value
it reports.**

**`VERDICT_CEILING = "GATE REACHED"`.** The item can reach `GATE REACHED` at most and
**can never reach `PASS`**, because `PASS` in this lab requires a value inside a
pre-registered band and there is no band to be inside. Any grading path that emits `PASS`
for this item is defective and its output is `NOT A RESULT`.

**Available verdicts, and only these:** `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` /
`BLOCKED` / `PENDING` (`CLAUDE.md` rule 1). No synonyms.

**Registered in advance:** an arm whose reproduction control `R0` does not reproduce the
established failure signature makes **the whole item `NOT A RESULT`**, not that arm alone.

---

## 4. THE ARMS — ONE VARIABLE EACH

All arms: **np = 1**, on the L3 ground unless the arm's variable is the mesh; identical
image; identical `a1wr_runScript_comp.py` except for the arm's single registered change;
**iteration budget fixed at 500** for every solver arm, so the cost anchor in §6 transfers
exactly and so no arm can be given more iterations than another.

**Why 500 and not 1,500.** The failure is present in the **`Time = 1`** block and the
residual floor of 0.3762 is reached within the first few hundred iterations (`S-27` §3).
500 iterations is sufficient to read the registered gates in §5 and is 3× cheaper than the
probe's 1,500. **It is not sufficient to reach 1e-8 under strong under-relaxation, and §5
is written so that no arm's verdict depends on reaching 1e-8.**

### Arm `MESHA` — build the reduced-span L3 mesh (Arm `A`'s ground; not itself a treatment)

Run `a1wr_genmesh.py` at `R = 4` with **`ZSpan: 0.1 → 0.001`** and **every other parameter
byte-identical**, then `checkMesh`. Produces `L3S` — 130,304 cells, `s0` 6.25e-07,
`nSurfaceCells` 509, `nWallNormalCells` 256, growth 1.05800, `marchDist` 20.

**Registered acceptance for `MESHA`, checked before Arm `A` may launch:**
`nCells(L3S) == 130304` **exactly**, and `checkMesh` max aspect ratio on `L3S` is within
**±2 %** of `212103.6706991908 / 100 = 2121.0367`. If either fails, **Arm `A` is `BLOCKED`
and is not run** — a ground that is not the registered ground makes the arm's single
variable no longer single.

### Arm `R0` — REPRODUCTION CONTROL. **Changes nothing.**

The frozen A1WR compressible configuration, L3, α = 0, 500 iterations. **This arm exists
because "arm X still fails" is uninterpretable without a demonstration, in this item and
on this box, that the failure reproduces at all.** `S-28` §2 is the standing reminder that
a figure carried from one context into another is false the moment it travels; `R0` is
this item refusing to carry `S-27`'s failure signature on trust.

### Arm `A` — ASPECT RATIO, ALONE

`R0`'s configuration, on `L3S` instead of L3. **The only difference between `R0` and `A`
is the span width, and therefore the maximum aspect ratio (100× lower).** Cell count,
chordwise resolution, `s0`, y+, every boundary condition, `fvSolution` and the run script
are byte-identical.

**⚠ REGISTERED DISCLOSURE — `A0` IS NOT CHANGED, AND ARM `A`'s COEFFICIENTS ARE
UNGRADEABLE.** `a1wr_runScript_comp.py:61` sets `A0 = 0.1`, the reference area = chord 1.0
× span 0.1. Arm `A`'s span is 0.001, so its `CL` and `CD` are scaled by 100× relative to
every other arm. **`A0` is deliberately left unchanged**, so that the run script differs
from `R0`'s in **zero** bytes and the arm's single variable stays in the mesh where it
belongs. **The consequence is registered here, before any run: Arm `A`'s `CL` and `CD` are
NOT COMPARABLE to any other arm's and are NOT READ BY ANY GATE.** §5's gates for Arm `A`
read the residual trajectory and the bounding census **only**. Reporting Arm `A`'s
coefficients as an aerodynamic result is a defect of grading, and its output would be
`NOT A RESULT`.

### Arm `B` — `alphat` WALL TREATMENT, ALONE

`R0`'s configuration on L3, with the `wing` patch's `alphat` boundary condition set to
`compressible::alphatWallFunction` with `Prt = 0.85`, **and `nut` left at
`nutLowReWallFunction`** — i.e. the wall-resolved momentum path is preserved and only the
thermal wall treatment moves.

**⚠ REGISTERED REFUSAL, WRITTEN BEFORE THE ATTEMPT.** DAFoam's `useWallFunction` flag sets
`nut` **and** `alphat` together. Arm `B` is only a one-variable arm if the two can be
separated. **The verification channel is the solver's own log, and it is registered as
binding:** the arm is valid **if and only if**, in the same log, the `alphat` line reads
`compressible::alphatWallFunction` **and** the `nut` line reads `nutLowReWallFunction`.
**If both lines move together, Arm `B` is `BLOCKED` — not repaired, not reinterpreted, and
not silently reported as a two-variable result.** This refusal is registered now so that
it cannot be renegotiated after the log is read.

### Arm `C1` — THE RELAXATION SCHEDULE, ALONE — one knob, `λ`

`R0`'s configuration on L3, with **every** relaxation factor in `system/fvSolution`
multiplied by a **single registered scalar `λ = 1/3`**, and nothing else in that file
touched:

| entry | frozen | Arm `C1` |
|---|---|---|
| `"(p\|p_rgh\|rho)"` | 0.30 | **0.10** |
| `"(U\|T\|e\|h\|nuTilda\|k\|epsilon\|omega)"` | 0.70 | **0.2333333333333333** |
| `nNonOrthogonalCorrectors` | 0 | **0 — unchanged** |

**One variable is `λ`, not "two numbers".** Both factors move by the same registered
scalar; neither is chosen independently. Choosing them separately would be a two-variable
arm and is refused.

### Arm `C2` — NON-ORTHOGONAL CORRECTORS, ALONE

`R0`'s configuration on L3, with `nNonOrthogonalCorrectors: 0 → 2` and **every relaxation
factor unchanged at the frozen 0.30 / 0.70.** This is a different mechanism from `C1`
(non-orthogonality error in the pressure equation, not the relaxation schedule) and
therefore a different arm.

**Arms explicitly NOT proposed, and why:** any arm moving the mesh *level* (four variables,
§2(a)); any arm moving `s0` (changes y+, and the y+ gate is on Sanaa's desk per `S-28`);
any arm combining `C1` and `C2`; any arm changing solver or discretisation schemes.

---

## 5. GATES, THRESHOLDS AND LABELS — ALL FIXED HERE, BEFORE ANY COMPUTE

**The gates do not read "did it converge to 1e-8".** At a 500-iteration budget an
under-relaxed arm can be genuinely repaired and still not have arrived, so a
convergence-only gate would score `C1` as a failure for being slower. The gates read the
**shape and floor of the residual trajectory**, both of which are readable inside the
budget.

| gate | reads | threshold | label if met | label if not |
|---|---|---|---|---|
| `G-REPRO` | `R0`'s min residual over 500 it | in **[0.60, 0.92]** — the established 0.6363–0.8993 span, widened symmetrically | continue | **whole item `NOT A RESULT`** |
| `G-REPRO.2` | `R0`'s bounding census | `p`, `rho`, `e`, `U` **all present**, first occurrence in the `Time = 1` block | continue | **whole item `NOT A RESULT`** |
| `G-FLOOR` | arm's min residual over 500 it | **< 0.3762** — the established floor no compressible solve on this ground has ever crossed | `GATE REACHED` for that arm | `GATE FAIL` for that arm |
| `G-MONO` | arm's residual series after iteration 200 | **zero reversals** (no `r[i+1] > r[i]`) at the log's own print cadence | `GATE REACHED` for that arm | `GATE FAIL` for that arm |
| `G-BOUND` | arm's bounding census | `p`, `rho` and `e` **all absent** for the whole run | `GATE REACHED` for that arm | `GATE FAIL` for that arm |
| `G-CAP` | arm's `core_min` from the ledger | **≤ that arm's §6 cap** | continue | `GATE FAIL` for that arm |
| `G-CEIL` | summed `core_min` after every arm | **≤ 120.0 core-min** | continue | **chain stops, exit 9** (rule 12) |
| `G-NP` | arm's ranks | **== 1** for every arm | continue | `NOT A RESULT` for that arm |
| `G-MESH` | `MESHA`'s output | `nCells == 130304` and max AR within ±2 % of 2121.0367 | Arm `A` may launch | Arm `A` **`BLOCKED`** |
| `G-BC` | Arm `B`'s log | `alphat` line == `compressible::alphatWallFunction`, `nut` line == `nutLowReWallFunction` | Arm `B` valid | Arm `B` **`BLOCKED`** |

**Item-level composition, fixed now:** the item is `GATE REACHED` if `G-REPRO` and
`G-REPRO.2` hold **and** at least one treatment arm reaches all three of `G-FLOOR`,
`G-MONO` and `G-BOUND`; `GATE FAIL` if `G-REPRO` holds and **no** treatment arm does;
`NOT A RESULT` if `G-REPRO` or `G-REPRO.2` fails, or if any control in §7 refuses.
**The item can never be `PASS` (§3).**

**Registered in advance: a `GATE FAIL` here is a real finding, not a failure of the item.**
If all four treatments miss, the answer is *"none of the three named candidates is
sufficient alone"* — which is a result, is reportable, and is what closes `S-27` §9's
list rather than extending it.

---

## 6. COST — EVERY ARM COSTED, THE DEADLINE ARITHMETIC SHOWN **AND EVALUATED**

### 6.1 The anchors

| figure | value | basis | artefact |
|---|---|---|---|
| L3 compressible, np=1, quiet-ish box (**2-way** concurrency) | 1,500 iterations in **961.61 s** solver, **982 s** container wall, **16.3667 core-min** → **1.5599 it/s** | **MEASURED** | `/home/ubuntu/certonomous-runs/A1WR/STAGE12/CHAIN_LEDGER.tsv` row `probe_C`; `.../probe_C/out/sweep.log` |
| L3 compressible, np=1, **busy** box (**8-way** concurrency) | 1,600 iterations in **3200.07 s** solver, 3,316 s wall, 55.2667 core-min, `rc=97` (timeout) → **0.5000 it/s** | **MEASURED** | same ledger, row `cold_C_4`; `.../cold_C_4/out/sweep.log` |
| **contention factor for THIS solver on THIS mesh** | **3.1198×** | **DERIVED** from the two MEASURED rates above | — |
| L3 mesh build wall | **≈ 14.5 s** (L2 dir 17:18:22.58 → L3 dir 17:18:37.08) | **DERIVED from directory mtimes, NOT a ledger figure** — weaker evidence, labelled as such | `/home/ubuntu/certonomous-runs/A1WR/` `stat` |

**⚠ THE CONTENTION FACTOR USED HERE IS THIS ARM'S OWN, NOT A BORROWED ONE.** `S-26`/`S-27`
record 0.56 it/s at 8-way against ~2.36 it/s at 3-way — **those are the INCOMPRESSIBLE
cold's rates** (`cold_I_4`: 1,800 it / 3206.51 s = 0.5613 it/s, which is that 0.56). Using
them here would import an incompressible measurement into a compressible cost basis. The
compressible pair `probe_C` / `cold_C_4` gives **3.1198×** and is used instead.

**⚠ `S-27` §9 SAYS THE DISCRIMINATING EVIDENCE *"COSTS A FEW CORE-MINUTES, NOT A
CAMPAIGN"*. THAT IS WRONG BY A FACTOR OF ABOUT THIRTY AND THIS DRAFT SAYS SO RATHER THAN
SIZING THE CAPS TO FIT IT.** At the measured busy-box rate, a single 500-iteration
compressible solve on L3 costs **16.67 core-min**, not "a few". The item is **~94
core-min** predicted on a busy box. It is still cheap in dollars (§6.4) and still well
inside the pre-authorisation — but a cap sized to `S-27`'s sentence instead of to this
box's measured rate is exactly how A1WR lost 331.7 core-min for zero physics.

### 6.2 The deadline arithmetic — **and the assert D19T did not have**

`TMO = int(cap × 60 / ranks) − CAP_MARGIN_S`, with `CAP_MARGIN_S = 60` (teardown).

**The solver does not get `cap`. It gets `cap − CAP_MARGIN_S × ranks / 60`.** The
launcher's usual back-check — `(TMO + CAP_MARGIN_S) × ranks / 60 == cap` — **passes
precisely because it adds back the margin the solver never receives**, so it is a
consistency check that is structurally incapable of noticing an under-budgeted arm.
**`TMO > 0` is necessary and is not sufficient.**

**REGISTERED FREEZE-TIME ASSERT, TO BE EXECUTED FOR EVERY ARM BEFORE THE FREEZE COMMIT:**

```
for every arm:
    TMO = int(cap*60/ranks) - CAP_MARGIN_S
    assert TMO > 0                                   # D19T's assert
    assert TMO >= SAFETY * pred_wall_busy_s           # THE ONE D19T DID NOT HAVE
    assert abs((TMO + CAP_MARGIN_S)*ranks/60 - cap) <= 1e-6
with SAFETY = 1.25 and pred_wall_busy_s taken from the 0.5000 it/s MEASURED busy rate.
```

### 6.3 The table, **evaluated** — every arm, every clause

`CAP_MARGIN_S = 60`, `SAFETY = 1.25`, `ranks = 1` throughout, busy rate **0.5000 it/s**:

| arm | iters | cap (core-min) | ranks | `TMO` (s) | back-check | pred wall busy (s) | `TMO`/pred | `TMO>0` | `TMO ≥ 1.25·pred` | pred (core-min) |
|---|---|---|---|---|---|---|---|---|---|---|
| `MESHA` | — | **3.0** | 1 | **120** | 3.000000 | 45.2 | **2.65×** | PASS | **PASS** | 0.753 |
| `R0` | 500 | **22.0** | 1 | **1260** | 22.000000 | 1000.0 | **1.26×** | PASS | **PASS** | 16.667 |
| `A` | 500 | **22.0** | 1 | **1260** | 22.000000 | 1000.0 | **1.26×** | PASS | **PASS** | 16.667 |
| `B` | 500 | **22.0** | 1 | **1260** | 22.000000 | 1000.0 | **1.26×** | PASS | **PASS** | 16.667 |
| `C1` | 500 | **22.0** | 1 | **1260** | 22.000000 | 1000.0 | **1.26×** | PASS | **PASS** | 16.667 |
| `C2` | 500 | **35.0** | 1 | **2040** | 35.000000 | 1600.0 | **1.27×** | PASS | **PASS** | 26.667 |

`C2`'s predicted wall carries a **1.6×** factor for two extra non-orthogonal pressure
solves per outer iteration — **EXTRAPOLATED, not measured**, and the most uncertain figure
in this table. Its cap carries the same 1.25 safety on that extrapolated basis; if `C2`
overruns, that is where the miss will be and the calibration row must say so.

`MESHA`'s predicted wall is 14.5 s × 3.1198 = 45.2 s — **DERIVED from a mtime-based figure
times a measured contention factor**, the weakest basis in the table, which is why its
headroom is 2.65× rather than 1.26×.

**All six arms pass all three clauses. Evaluated 2026-09-03, not asserted.**

### 6.4 Item totals

| quantity | value |
|---|---|
| sum of arm caps | **126.0 core-min** |
| **predicted item spend (busy box, the registered figure)** | **94.09 core-min** |
| predicted item spend (quiet box, optimistic bound) | 30.16 core-min |
| **ITEM CEILING** | **120.0 core-min**, checked after **every** arm |
| ceiling / predicted | **1.28×** |
| ceiling < sum of arm caps | **TRUE — deliberate.** The ceiling binds first and stops the chain before every arm could exhaust its own cap |
| dollars, predicted | 94.09 core-min = 1.568 core-h → **$0.0804 DERIVED** |
| dollars, ceiling | 120.0 core-min = 2.000 core-h → **$0.1026 DERIVED** |

**Dollars are DERIVED and reported-by-owner, never measured** — the box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER.md` §5), at the owner-stated c7a.4xlarge $0.0513/core-h.
Under the $25 pre-authorisation, **and costed anyway, because a blanket is not a per-item
read** (rule 9).

**An overrun stops the run and does not get a new budget** (rule 12), enforced per-arm and
at the ceiling after every arm.

**A `docs/COST_CALIBRATION.md` row is OWED AT ITEM COMPLETION** — predicted 94.09
core-min against the ledger's actual, ratio stated, waste named **separately** and never
folded into the ratio, dollars derived and labelled derived-not-measured.

---

## 7. PLANTED-ZERO CONTROLS — **EVERY FIXTURE STATIC AND INDEPENDENT OF THE GRADED RUN**

`CLAUDE.md` rule 3: a zero from a reader not shown able to see a non-zero is not evidence.

**⚠ THE L-435 REQUIREMENT, ASSERTED EXPLICITLY FOR EVERY CONTROL BELOW.** MAAOA's entire
grading was voided because control `M1`'s fixture was `MA288/out/trim.log` — **a live
artifact of the very run being graded**. MA288 failed, so the fixture never acquired the
property the control needed, the control's premise was falsified by the run's own outcome,
and the reader refused everything. **Not one control in this item reads anything produced
by this item's own solves.**

Every fixture is a file **authored at freeze time**, stored at
`cases/dafoam/ladder-a/A1/compressible_wallresolved_triage/controls/`, **md5-pinned in the
frozen document**, and never written to by any arm.

| control | reader under test | fixture (STATIC) | must return | refusal if not |
|---|---|---|---|---|
| `P1` | bounding census | `controls/P1_bounding.log` — 40 frozen lines carrying exactly **3** `Bounding p<500000` and **5** `Bounding nuTilda>1e-16` | `(p=3, nuTilda=5)` | `CONTROL_READER_NOT_BORN` |
| `P1n` | bounding census, **negative leg** | `controls/P1n_clean.log` — 40 frozen lines with **zero** bounding of any kind | `(0, 0)` | `CONTROL_READER_ALWAYS_FIRES` |
| `P2` | residual reader | `controls/P2_residual.log` — a frozen series whose minimum is **0.4242424242** at a known iteration | `0.4242424242` to 1e-12 | `CONTROL_READER_NOT_BORN` |
| `P3` | monotonicity reader | `controls/P3_reversal.log` — a frozen series with **exactly one** reversal at a known index | that index | `CONTROL_READER_NOT_BORN` |
| `P3n` | monotonicity reader, **negative leg** | `controls/P3n_monotone.log` — a frozen strictly-decreasing series | **zero** reversals | `CONTROL_READER_ALWAYS_FIRES` |
| `P4` | `alphat`/`nut` BCType reader (**Arm `B`'s validity rests on it**) | `controls/P4_wallfn.log` and `controls/P4_fixed.log` — one frozen line each, `compressible::alphatWallFunction. Default Prt=0.85` and `fixedValue` | must **distinguish** them | `CONTROL_READER_NOT_BORN` |
| `P5` | `checkMesh` aspect-ratio reader (**Arm `A`'s validity rests on it**) | `controls/P5_checkmesh.log` — a frozen excerpt with `Max aspect ratio = 1234.5678` | `1234.5678` | `CONTROL_READER_NOT_BORN` |

**Two-sided by construction.** `P1n` and `P3n` exist because a reader that *always* reports
bounding, or *always* reports a reversal, is exactly as blind as one that never does, and a
one-sided planted control cannot tell them apart.

**THE STATIC-FIXTURE PROPERTY IS ASSERTED BY EXECUTION AT GRADE TIME, NOT CLAIMED:**

```
for every fixture f:
    assert md5(f) == <pin frozen in this document>          # it is the file that was frozen
    assert mtime(f) < mtime(<run root>)                     # it PRE-DATES the graded run
    assert f is not under <run root>                        # it is not an artifact of it
```

**The mtime clause is the executable form of "independent of the run being graded".** A
fixture younger than the run root is, by construction, something the run could have
written, and the grader refuses the whole grading rather than reason about it.

**Any control refusal makes the WHOLE ITEM `NOT A RESULT`** — not the arm, not the gate.
A refusal is not a verdict (`S-28` §1), the grading path is fixed at the freeze commit, and
**no other reader may be substituted.**

---

## 8. LAUNCH PATH

**The durable queue daemon, and nothing else.** A row under
`verification/queue/dafoam/`, picked up by `scripts/queue_runner.py --daemon`. **No lane
launches a container or a driver directly.** Deadlines live **inside the containers**
(`timeout -s TERM -k 30 $TMO`), sized per §6.3.

**Run root:** `/home/ubuntu/certonomous-runs/A1WCT-a1-naca0012-compressible-triage`, whose
**absence is asserted by execution** immediately before staging and which **refuses (exit
3) if it exists** — never deletes it. An existing root may carry a `0/` or a time directory
from an earlier attempt, and rule 4's age guard exists because that case is not
distinguishable after the fact.

**Placement:** a cpuset distinct from every live chain's registered pool, chosen and gated
(`G-PLACE`) **at freeze time against the census then**, not now.

---

## 9. PREDICTIONS — REGISTERED BEFORE THE ANSWER EXISTS, AND EACH WITH ITS REFUTER

**The house rule applied here: where a boring outcome and an exciting one are both
available, the boring one is the registered prediction.** The exciting outcome for this
item is *"one line in `fvSolution` unblocks the compressible ladder"*, and it would flatter
us. It is therefore **not** what is predicted below.

| arm | **PREDICTION** | what would **REFUTE** it |
|---|---|---|
| `R0` | **The failure reproduces**: min residual in [0.60, 0.92], `p`/`rho`/`e`/`U` bounding present from `Time = 1` | `R0` converging, or bounding absent → the established finding does not reproduce on this box, and **the whole item is `NOT A RESULT`** |
| `A` | **Aspect ratio alone is NOT sufficient.** At 100× lower max AR the solve **still fails** `G-FLOOR` — min residual stays above 0.3762 | `A` crossing 0.3762 with `G-MONO` and `G-BOUND` also met → aspect ratio **is** the mechanism, and the ladder is unblocked by a span change |
| `B` | **`alphat` alone is NOT sufficient.** Restoring `compressible::alphatWallFunction` still fails `G-FLOOR`. A `fixedValue` `alphat` is the ordinary wall-resolved choice, and the failure appears in the **momentum and pressure** fields at `Time = 1`, before the energy wall treatment could plausibly act | `B` crossing 0.3762 → the thermal wall treatment **is** the mechanism |
| `C1` | **The registered prediction is the boring one: `C1` does NOT converge to 1e-8 inside 500 iterations** — under-relaxation slows convergence and the budget is not sized to reach tolerance. **`G-FLOOR` and `G-MONO` are the discriminating gates for this arm, and they are predicted to be MET** while 1e-8 is not reached | `C1` failing `G-MONO` — the trajectory still reverses at λ = 1/3 → the relaxation schedule is **not** the mechanism, which is the outcome that would most surprise this drafter and is why it is written down |
| `C2` | **Non-orthogonal correctors alone are NOT sufficient.** `checkMesh` fails exactly one check on L3 and it is the aspect-ratio check, **not** non-orthogonality (`S-27` §3) — so the correctors are treating a problem this mesh does not have | `C2` meeting all three gates → non-orthogonality **is** implicated despite `checkMesh` |
| **item** | **`GATE FAIL`** — `G-REPRO` holds and **no** arm meets all three treatment gates, i.e. **none of `S-27`'s three candidates is sufficient alone.** That is the boring outcome and it is the registered one | any single arm meeting all three gates → the item is `GATE REACHED` and the mechanism is named |

**Recorded so it cannot be reframed later:** the drafter's private expectation is that
`C1` is the most likely mechanism (`S-27` §3's *"falls, REVERSES, and stalls high"* is the
classic signature of too-aggressive relaxation on a stiff system). **That expectation is
NOT the registered prediction**, precisely because it is the one that would flatter us, and
recording the gap here is what stops it being claimed as a prediction afterwards.

---

## 10. WHAT THIS ITEM CANNOT DO — STATED NOW

1. **It cannot produce a grid-converged anything** (§3, `G-NOBAND`).
2. **It cannot separate two mechanisms that are only jointly sufficient.** Every arm is
   single-variable, so a mechanism requiring, say, both `A` and `C1` will read as
   `GATE FAIL` on both. **That is registered as a known limit, not discovered afterwards
   as an excuse**; the follow-on would be a factorial item, which this draft does not
   propose and does not pre-authorise.
3. **It says nothing about NACA0012.** It is a statement about a case setup
   (`S-27` §5), and the cause class is **SETUP/NUMERICS**, never `PHYSICS-FAIL`.
4. **It does not touch the incompressible line**, which is where this family's live
   results are.
5. **It does not re-open the y+ gate question**, which is reserved to Sanaa (`S-28` §5).

---

## 11. OPEN ITEMS FOR THE SUPERVISOR BEFORE FREEZE

1. **The cap arithmetic in §6.3 is evaluated but is yours to ratify** — §3 check 4.
2. **`C2`'s 1.6× cost factor is EXTRAPOLATED** and is the weakest number in §6.3.
3. **Arm `B` may prove unseparable** and be `BLOCKED` at `G-BC`; §4 registers the refusal
   in advance, but you may prefer to resolve the DAFoam question first and drop the arm.
4. **`G-FLOOR`'s 0.3762 threshold is the established floor over 11 solves** and is a
   **one-sided** bound — nothing has ever gone below it, so crossing it is informative and
   *how far* below is not gradeable here.
5. **Placement (`G-PLACE`) is deliberately unset** and must be chosen against the census
   at freeze, not against tonight's.
6. **The `S-27` §9 corrections in §2(a) and §6.1 are mine and are on the record**: the
   L1/L2 aspect-ratio arm is four-variable, and *"a few core-minutes"* understates the
   cost by roughly 30×.

**SUBMISSIONS PARKED. Nothing here is sent, filed, uploaded, registered or posted outside
this box.**
