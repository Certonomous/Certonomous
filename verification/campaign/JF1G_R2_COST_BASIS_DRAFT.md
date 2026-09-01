# JF1G-R2 — COST BASIS FOR A SUCCESSOR REGISTRATION — **DRAFT, NOT FROZEN, NOT LAUNCHED**

> **THIS IS NOT A PRE-REGISTRATION AND IT MUST NOT BE TREATED AS ONE.** It is
> deliberately **not** named `*_PREREGISTRATION.md`, so that no freeze checker,
> launcher or audit sweep mistakes it for a frozen document. **No gate, threshold,
> cap or label in this file is in force. Nothing may be launched against it.**
> It carries one thing: the **measured** cost basis that a successor registration
> would need, recorded while the measurement is fresh.

**Why it exists.** `cfd-supervisor` directed that the lawful route to a larger C2
allowance is a **new** pre-registration carrying the now-measured basis, and that the
draft be prepared but **not launched**. This is that draft.

**Why it cannot be frozen yet.** The disposition of Gate G1 of `038f4bca` — whose
`Mesh OK` clause rejects C3 on an aspect ratio the lab's own `MESH_STANDARD.md` §3.3
calls *"advisory … never a lone rejection"* — is **reserved and unruled**
(`verification/campaign/JF1G_MESH_GATE_FINDING.md` §5). **A successor cannot be
frozen while the clause it would replace is still before the chief**, and this lane
has been instructed not to reissue, not to amend and not to run C3. **Freezing this
draft is blocked on that ruling, not on any measurement.**

---

## 1. WHAT IS NOW MEASURED THAT WAS NOT MEASURED AT `038f4bca`

`038f4bca` §8 priced the ladder from a **single** 40k-cell case, at a unit rate of
`4.0798e-06` core-s per cell per iteration, applied **linearly** to every level.
**That linear model is refuted.** Landed as calibration row
`C-20260901T163701.774550Z-1b8633ba`:

| level | cells | core-s per cell per iteration | source |
|---|---|---|---|
| C1 | 39,984 | **4.0798e-06** | completed run, 1,305 wall s / 8,000 it / 1 rank |
| C2 | 89,964 | **7.7867e-06** | mid-run `ExecutionTime`, same box, same three concurrent solvers |

**1.909× worse per cell at 2.25× the cells.** Contention is **not** the attribution —
both readings were taken under the same live load. Cost therefore grows as roughly
the **4.3 power of `r`** on this 2-D family, not `r²`.

**Realised consequence, not a forecast:** C2 Pass-0's registered estimate of 48.9
core-min projects to **93.4**, against a frozen cap of **80.0**. The cap stands and
is not raised; C2 stops when it strikes it.

## 2. THE COST TABLE A SUCCESSOR WOULD CARRY

Built from the **measured** per-level rates above, with the C3 and C4 rates
**extrapolated on the measured exponent and labelled as extrapolation, not
measurement.** A successor must re-derive C3's rate from C3's own completed run
before pricing C4.

| item | cells | `endTime` | rate basis | estimate | proposed cap |
|---|---|---|---|---|---|
| Pass 0 C1 | 39,984 | 8,000 | **measured** | 21.8 | 40 |
| Pass 0 C2 | 89,964 | 8,000 | **measured** | **93.4** | **130** |
| Pass 0 C3 | 202,180 | 8,000 | *extrapolated* | ~350 | 480 |
| Pass 1 C1 | 39,984 | 30,000 | **measured** | 81.6 | 110 |
| Pass 1 C2 | 89,964 | 30,000 | **measured** | **350.4** | **470** |
| Pass 1 C3 | 202,180 | 30,000 | *extrapolated* | ~1,310 | 1,760 |

**Every extrapolated figure is marked as such and none may be quoted as measured.**
Dollars at the recorded `$0.0513/core-h` are **derived, not measured** — this box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

## 3. WHAT A SUCCESSOR WOULD ALSO HAVE TO CARRY, AND WHICH IS NOT COSTED HERE

Recorded so the next author does not have to rediscover it:

1. **The mesh gate**, aligned to `MESH_STANDARD.md` §3.3 and §11 — gate on
   non-orthogonality and skewness; **report** aspect ratio and cell-volume ratio.
   **Blocked on the unruled question. Not drafted here.**
2. **`--normal-smooth = 500·s²`** as a similarity clause. Derived from the
   `sqrt(passes)` diffusion length **before** it was measured; the sweep's minimum
   lands on the predicted value at every level, and under it max non-orthogonality
   reads **57.53 / 58.62 / 58.89** across a 5× cell-count range instead of drifting
   57.53 → 67.64 → 75.14. C1 is unchanged (`500·1² = 500`), so C1 stays
   bit-identical to the grid the five 2026-08-31 sweep rows ran on.
3. **The honest iterative floor.** Two runs of the same case at the same settings
   from different initial conditions settle **2.23e-05** apart in `CL`, while each
   run's apparent drift is **~3e-07** — the initial-condition sensitivity is **~70×**
   the drift a tightness rule reads. A successor's tightness clause should read the
   **floor**, not the drift.
4. **The similarity clauses of `038f4bca` §2.2 are measured PASSING** on the emitted
   meshes and would carry over unchanged: ratios 1.4966–1.5017, total cell ratio
   2.2500 / 2.2473 against `r²`, growth identity `g_fine^r = g_coarse` to 3e-4.

---

**SUBMISSIONS PARKED.** Nothing in or derived from this draft is sent, filed,
uploaded, posted or registered outside this box. **And nothing is launched against
it: it is a draft, and the freeze it anticipates is blocked on a ruling that is not
this lane's to make.**

---

# ADDENDUM A — 2026-09-01, C2 COMPLETED. §1 AND §2 ARE SUPERSEDED AND THE DIRECTION IS TOWARD THE LAB, NOT AWAY

**Nothing above is edited.** §1 and §2 were built from a **mid-run** `ExecutionTime`
reading of C2 and are left standing so the correction is visible. The calibration
row that landed them said so in advance — *"C2's COMPLETED figures will be added as
a further row and supersede the mid-run marginal rate used here"* — and this
addendum is that obligation discharged.

**C2 is now COMPLETE.** `rc = 0`, one `End` line, last `Time = 8000 == endTime`,
`stage_at_exit done`, **70.8833 core-min measured against its frozen 80.0 cap**
(`verification/runs/JF1_jet_flap/JF1G_P0_C2_CMU010_A0/RUN_STATUS.*.txt`).

## A.1 THE MID-RUN READING WAS 32 % HIGH, AND §1's HEADLINE CLAIM IS FALSIFIED

| level | cells | core-s per cell per iteration | basis |
|---|---|---|---|
| C1 | 39,984 | **4.0491e-06** | completed, `ExecutionTime` 1,295.2 s / 8,000 it / 1 rank |
| C2 | 89,964 | **5.8908e-06** | **completed**, `ExecutionTime` 4,239.7 s / 8,000 it / 1 rank |
| C2 | 89,964 | ~~7.7867e-06~~ | *§1's mid-run reading — **superseded**, 32 % high* |

**§1 said: *"Realised consequence, not a forecast: C2 Pass-0's registered estimate
of 48.9 core-min projects to 93.4, against a frozen cap of 80.0. The cap stands and
is not raised; C2 stops when it strikes it."*
**C2 DID NOT STRIKE ITS CAP.** It completed all 8,000 iterations at 70.8833
core-min, 89 % of the 80.0 ceiling. The projection was 32 % over the outturn, and
the sentence that called it *realised rather than forecast* was wrong to: it was a
mid-run extrapolation wearing a completed run's clothes.

**§1's exponent is also superseded.** Measured on the two **completed** levels,
cost grows as **N^1.4623**, i.e. as **r^2.925** on this 2-D family — not §1's
*"roughly the 4.3 power of r"*. Superlinearity is real (1.4623 ≠ 1.0, so the
`038f4bca` linear model stays refuted) but it is **markedly milder** than the
mid-run reading made it look.

## A.2 C3's WALL-CLOCK FORECAST, FROM TWO INDEPENDENT BASES

C3 is **202,180 cells** (`038f4bca` §2's level table), `endTime` 8,000, 1 rank.

| basis | exponent | C3 rate | C3 solve | wall-clock |
|---|---|---|---|---|
| total `ExecutionTime`, C1 and C2 completed | 1.4623 | 1.7318 s/it | 13,854 s = **230.9 core-min** | **3.85 h** |
| marginal rate over each level's **final 4,000** iterations (0.1544 → 0.5058 s/it) | 1.4633 | 1.6541 s/it | 13,233 s = **220.5 core-min** | **3.68 h** |

**The two bases agree to 4.7 %, and neither is the §2 figure of ~350 core-min.**

> **C3's honest ETA is 3.7 to 3.9 wall-hours — call it 3.8 h — for about 221 to
> 231 core-min on one rank.** Add ~1 core-min for the mesh build and `checkMesh`,
> which measured in seconds at C1 and C2.

**THE HONEST WEAKNESS OF THIS FORECAST, STATED RATHER THAN BURIED.** It is a
**two-point power law**, so it has **zero degrees of freedom**: there is no
residual against which to test it and it cannot see curvature. The superlinear
part is the GAMG pressure solve, whose cost per cell is not guaranteed to keep the
same exponent across another 2.25× in cell count. **A third completed level could
move it, and the figure is an extrapolation, not a measurement.** It is quoted to
three digits because that is what the arithmetic gives, not because it is known to
three digits.

## A.3 THE FINDING THAT MATTERS FOR THE RULING: C3 CANNOT FINISH INSIDE THE FROZEN PASS-0 CAP

`038f4bca` §8 registers **Pass 0 C3 at 110.0 core-min** inside a **Pass-0 subtotal
cap of 250**. Against the measured actuals:

| | registered | measured / forecast |
|---|---|---|
| Pass 0 C1 | 21.8 | **21.7500 measured** (ratio 0.998) |
| Pass 0 C2 | 48.9 | **70.8833 measured** (ratio 1.450) |
| Pass 0 C3 | 110.0 | **~221–231 forecast** (ratio ~2.0–2.1) |
| **Pass 0 subtotal** | **180.7, cap 250** | **~314–324** |

**C1 and C2 have already consumed 92.63 of the 250.** At the forecast rate the
remaining **157.37 core-min** buys **about 5,450 to 5,710 of C3's 8,000
iterations — roughly 68 to 71 % of the level.**

**So, stated plainly: run as registered, C3 would be stopped by its own cap at
about seven-tenths of its iterations, and CLAUDE.md rule 12 forbids raising the
cap — an overrun stops the run, it does not get a new budget.** A cap-struck C3 is
not a level; it produces no `CL` at `endTime`, fails the strict completion rule,
and under rule 5 clause 1 would void the whole triple as **`NOT A RESULT`**.

**This is a second, independent reason C3 must not be launched against `038f4bca`,
and it is arithmetic rather than judgement.** It does **not** touch the Gate G1
aspect-ratio question, which is reserved to the chief and remains unruled
(`JF1G_MESH_GATE_FINDING.md` §5). It says only that even a favourable ruling on
G1 would hand C3 a budget it cannot finish in, so the lawful route was already a
successor registration — which is what this draft is for.

**Pass 0 stands at `PENDING` — 2 of 3 levels.** That is a queue state, not
progress toward a result, and Pass 0 scores nothing in any case (`038f4bca` §6:
no `PASS`, no `GATE REACHED`, no observed order, no GCI).

**No cap, gate, threshold or label of `038f4bca` is changed by this addendum, and
nothing here is launched against.**
