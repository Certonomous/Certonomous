# F23-HP-WEDGE — Hagen–Poiseuille flow in a circular pipe on an AXISYMMETRIC WEDGE (`simpleFoam`, streamwise cyclic, fixed body force G = 0.32, Re_D = 100, 4 ranks) — GRADED RECORD

Team cfd. Pre-registration `verification/campaign/F23_HP_WEDGE_PREREGISTRATION.md`
frozen at **`058e77719c57332aff245e58d536a343cbde49e5`** (Amendment 1, the L-349
pre-spend projector; the original freeze is `a5f335a640994da21c0ae570c30090c935215b84`).
Amendment 1 was **pre-first-compute**, stated its condition and how it was checked
(run root `test -e` **ABSENT** at 2026-08-27T17:00:07Z, zero core-minutes in the
tree), and moved the **pre-spend projector only** — the cap stayed at **1,100**, and
no gate, band, label, ladder, iterative floor or case dictionary moved.
Capability-grid cell **068c2bf0 — axisym · steady · incompressible**.

Launched by the queue runner 2026-08-28T07:03:49Z (pid/sid 1771573,
`verification/queue/cfd/launched/F23_HP_WEDGE.json` `_launch`), terminated
07:54:26Z with no agent attached. Levels registered: coarse 64 × 2048, medium
128 × 4096, fine 256 × 8192, 4,000 SIMPLE iterations each on 4 ranks
(`decomposePar simple n (1 4 1)`, graded from `processor*/`, never reconstructed).

---

## 1. VERDICTS — fixed vocabulary

| gate | verdict |
|---|---|
| G-F23-1 `E2_normalised_profile` (fine value in [2.376227e−06, 2.138605e−05]) | **NOT A RESULT** |
| G-F23-2 `f_Re` (fine value in [63.998628773, 64.001371227], exact 64) | **NOT A RESULT** |
| **rung F23_HP_WEDGE** | **NOT A RESULT** |

| level | status |
|---|---|
| coarse (64 × 2048, 131,072 cells) | ran to completion; **NOT A RESULT** (rule 5 limb 1 and the Class C plateau limb both fail) |
| medium (128 × 4096, 524,288 cells) | ran to completion; **NOT A RESULT** (same two limbs) |
| fine (256 × 8192, 2,097,152 cells) | **PENDING** — the level was **never launched**; no solver ever started on it |

**The verdict rests on TWO INDEPENDENT grounds, and the ordering matters.** The
mesh guard was the **visible** failure — it is what stopped the launcher and what
the status line reports. The **iterative floor was the fatal one**: it would have
produced `NOT A RESULT` on this rung even if the fine level had built, meshed,
decomposed and run to 4,000 iterations without incident. **Ground 2 is the more
serious finding and is recorded as such.**

The gate-vocabulary direction of travel is the one rule 5 fixes: the triple gate
can only turn a `PASS` or a `GATE FAIL` **into** `NOT A RESULT`, never the reverse.
Here there is no triple at all (two levels), and each of the two levels that did
run independently fails limb 1 and the plateau limb. There is nothing for the
Roache classifier to be asked, and no value from this rung is quotable as a result.

---

## 2. GROUND 1 — THE LADDER IS INCOMPLETE: two levels are not a Roache triple

### 2.1 What stopped, and where

`build_f23.py` refuses a level whose `checkMesh`-reported wedge angle differs from
the registered half angle by more than a **fixed absolute 1e−6 degrees**:

```
cases/F23_HP_WEDGE/build_f23.py:128-130
    for _p, ang in m_wa:
        if abs(float(ang) - EX.HALF_ANGLE_DEG) > 1e-6:
            die("checkMesh wedge angle %s is not the registered half angle %g" % (ang, EX.HALF_ANGLE_DEG))
```

with `EX.HALF_ANGLE_DEG = 0.04` at `cases/F23_HP_WEDGE/exact_f23.py:83`.

Measured, each from that level's own `log.checkMesh` (line 92/93, both wedge
patches, identical to the last digit at every level):

| level | cells | wedge angle reported by `checkMesh` | deviation from 0.04 | fraction of the 1e−6 budget | growth over previous level | `checkMesh` verdict |
|---|---|---|---|---|---|---|
| coarse | 131,072 | 0.0400002766821 | 2.766821e−07 | **0.28×** | — | `Mesh OK.` |
| medium | 524,288 | 0.0400007984975 | 7.984975e−07 | **0.80×** | ×2.886 | `Mesh OK.` |
| fine | 2,097,152 | 0.0400027202903 | 2.7202903e−06 | **2.72× — REFUSED** | ×3.406 | `Mesh OK.` |

**`checkMesh` itself reports `Mesh OK.` at all three levels, fine included.** The
guard refused a mesh that OpenFOAM's own checker passed, on a quantity `checkMesh`
prints as information rather than as a failure.

`fine/log.build` carries exactly one line and it is the guard's own:

```
ABORT (build_f23): checkMesh wedge angle 0.0400027202903 is not the registered half angle 0.04
```

### 2.2 Positive evidence that no solver ran on the fine level

Not a missing `grep` hit — the **complete** contents of `fine/`, enumerated:
`box_before.txt`, `constant/` (`fvOptions`, `polyMesh/`, `transportProperties`,
`turbulenceProperties`), `log.blockMesh`, `log.build`, `log.checkMesh`, `system/`
(`blockMeshDict`, `controlDict`, `decomposeParDict`, `fvSchemes`, `fvSolution`).
**Eight entries and nothing else.**

There is **no** `log.simpleFoam`, **no** `RC.txt`, **no** `0/`, **no**
`processor0..3/`, **no** `log.decomposePar`, **no** `box_after.txt`, **no**
`MESH_LINE.txt`, **no** `log.writeCellCentres`, **no** `log.writeCellVolumes`. The
comparison with `coarse/` and `medium/`, which each carry all nine of those, is the
control: the reader that finds them at two levels finds none at the third.

The **mechanism** of that absence is in the code, not inferred from the listing.
The guard sits at `build_f23.py:129-130`; the very next statement that touches disk
is `os.makedirs(os.path.join(dest, "0"))` at `build_f23.py:132`. The guard fires
**before the level's `0/` directory is created at all**, which is why `fine/0/`
does not exist. The launcher's `mpirun` is a further 14 lines down a different
file, `run_f23.sh:233`, behind three intervening guards
(`0/U` present, `MESH_LINE.txt` present, `decomposePar` rc and rank count).

*Correction to the brief this lane was given:* the guard is **not** "eight lines
before `mpirun`". It is three statements before `build_f23.py:132` and fourteen
lines before `run_f23.sh:233`. The substance — the build stopped well short of the
solver — is unchanged; the line count was wrong and is corrected rather than
transcribed.

### 2.3 It was NOT a cap stop, and the launcher's own numbers say so

`cases/F23_HP_WEDGE/STATUS.F23_HP_WEDGE` reads
`launcher_rc=1 end=2026-08-28T07:54:26Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc`.

**`1` is the build-failure exit**, `run_f23.sh:219-220`:

```
  python3 "$BUILD" "$CD" --level "$NAME" > "$CD/log.build" 2>&1 \
    || { echo "ABORT: build_f23.py failed at level $NAME; see $CD/log.build"; exit 1; }
```

A **cap halt in this launcher is `exit 3`**, and there are exactly two such sites,
`run_f23.sh:215` and `run_f23.sh:251`. Neither fired. The pre-spend projection the
launcher printed immediately before the fine build is decisive:

> `level fine: free cores 2.0, ranks 4 -> PROJECTED 656.672459 core-min (cumulative would be 851.405792 of 1100)`

851.4 of 1,100 — **HALT = 0, the projector said proceed.** The cap was not
approached, not crossed, and was never raised.

### 2.4 The finding about the GUARD, which is a registration defect and not a mesh defect

The mesh is fine. `checkMesh` says so three times.

**A fixed ABSOLUTE tolerance was registered against a quantity that GROWS with
refinement.** The angle `checkMesh` recovers from the wedge's cell geometry drifts
further from the nominal 0.04° at every refinement — the near-axis cell gets
thinner in the wedge-normal direction as `dr = R/NR` halves, so the geometric
recovery of the half angle loses precision monotonically. Measured growth is
**×2.886 then ×3.406 per level** — roughly ×3 per halving of h. Against a *fixed*
1e−6 ceiling, that guard was **guaranteed to refuse at some level**; the only open
question was which one.

**And it was predictable at run time, from artefacts the run itself printed.**
Coarse sat at 0.28× of budget and medium at **0.80×** — 80 % consumed with one
refinement still to come and a measured per-level growth factor of 2.886 already in
hand. Extrapolating the coarse→medium factor onto medium gives 2.30e−06 for the
fine level, i.e. **2.3× over budget, predictable before the fine level was built**.
Both readings were written into `cases/F23_HP_WEDGE/launcher.queue.out` as they
happened (the `level <name> built:` rows carry `wedge_angles_deg=`). **Nobody
computed the third value, at registration time or at run time.**

For scale, the same deviations expressed **relatively**: 6.9e−06, 2.0e−05 and
6.8e−05 of the 0.04° angle — the worst is **0.0068 %**. This is recorded as a
measured fact about the guard's shape, **not** as a prescription: F23's
registration is closed and the successor's tolerance is F23b's business.

---

## 3. GROUND 2 — THE FATAL ONE: neither level that ran was iteratively converged, and neither plateaued

**Even had the fine level built and run, this rung would have graded
`NOT A RESULT`.** Ground 1 removed the third rung of the ladder; Ground 2 removes
the two that exist. The two grounds are independent: repairing the wedge guard
alone would have bought a complete ladder of three non-results.

### 3.1 Rule 5 limb 1 — the `Ux` initial-residual census

Registered (prereg `:157`): the solver's **`Ux` initial residual ≤ 1e−8 at every
iteration of the census window**, the window being **iterations 2801–4000**
(prereg `:275`). Measured by this lane directly from each level's own
`log.simpleFoam`, all 4,000 `GAMG: Solving for Ux, Initial residual =` lines
parsed:

| level | census lines counted | worst `Ux` initial residual in 2801–4000 | at iteration | multiple of the 1e−8 floor | value at iteration 4000 | iterations of 4000 EVER at ≤ 1e−8 |
|---|---|---|---|---|---|---|
| coarse | 1,200 | **7.32534266572e−05** | 2801 | **7,325×** | 2.54086320517e−05 | **0** |
| medium | 1,200 | **2.64854032205e−04** | 2801 | **26,485×** | 1.49473294723e−04 | **0** |

The last column is the sharper statement and is why this is not a near miss:
**neither level reached the registered floor at any iteration of the run**, not
merely inside the census window. Both levels fail limb 1 outright.

The registration's own `Uy`, `Uz` and `p` residual channels are **excluded at the
freeze** under N-AV8 and are not used here to soften or to sharpen the verdict; the
gated channel `Ux` fails on its own.

### 3.2 The Class C plateau limb — the graded quantity is still moving

Registered (prereg `:153-155`): Class C plateau on the graded quantity itself,
40 checkpoints 100 iterations apart, window 12 = 1,200 iterations, **trend
tolerance 2e−4**, computed by `grade_f23.py:274-292` as

```
drift = |fitted_slope| * (t_last - t_first) / max(|mean(window)|, 1e-14)
```

This lane reproduced that formula independently, over checkpoints
**2900 → 4000** (the last 12), from `<level>/processor{0,1,2,3}/<t>/U` with
volume weights from `processor{0,1,2,3}/0/V`:

| level | window mean f·Re | fitted slope (per iteration) | relative drift over window | registered tolerance | multiple of tolerance |
|---|---|---|---|---|---|
| coarse | 68.047093 | −3.463456e−03 | **5.5988e−02** | 2.0e−04 | **280×** |
| medium | 121.908898 | −2.277666e−02 | **2.0552e−01** | 2.0e−04 | **1,028×** |

Both levels are `NOT_PLATEAUED_TREND` — by two and three orders of magnitude.

### 3.3 The flow was still accelerating from rest at the last checkpoint

The bulk velocity, volume-weighted over the whole domain (on this axially uniform
wedge the volume weight *is* the area weight, so this equals the cross-section
average), read from `processor*/4000/U`:

| level | Ubar at iteration 2900 | Ubar at iteration 4000 | Ubar exact | f·Re at 4000 | f·Re exact |
|---|---|---|---|---|---|
| coarse | 0.910772 | **0.963749** | 1.0 | **66.4073** | 64 |
| medium | 0.471412 | **0.579086** | 1.0 | **110.5190** | 64 |

`f·Re = 2 D² G / (ν Ubar)`, the same closed form the registration's planted-zero
control uses, which at `G = 8 ν Ubar_exact / R²` gives exactly 64 at
`Ubar = Ubar_exact`.

The medium level had reached **58 % of its own steady bulk velocity** after 4,000
iterations, and was still rising by 23 % across the last 1,200. This is not a
converged solution being graded slightly early; it is a startup transient. Note
that the finer mesh is **further** from steady state than the coarser one at the
same iteration count — the ordering that gives the mechanism away.

### 3.4 The mechanism, measured — and GAMG is not the culprit

Under-relaxation at `alpha_U = 0.7` (`system/fvSolution:42`; `p` at 0.3, `:41`)
adds `(1 − α)/α = 0.42857 × diag(A_P)` to the momentum matrix. That term is
O(1) while the diffusion operator's smoothest mode on a pipe of radius R at
spacing h is O((h/R)²), so the added diagonal **dominates** the mode that carries
the bulk acceleration. The **outer SIMPLE loop** therefore contracts at
`1 − O(h²)` per iteration **no matter how well the linear solver performs**.

Four independent confirmations, all measured:

1. **GAMG is doing its job.** `No Iterations 1` on `Ux` throughout both runs —
   the linear system is solved to its final-residual tolerance in a single
   V-cycle. The linear solve is not the bottleneck; the outer loop is.
2. **The decay rate scales as h².** Log-linear fit of the bulk error
   `e = 1 − Ubar` over checkpoints 2900→4000:

   | level | NR | e at 2900 | e at 4000 | fitted decay rate k (per iteration) |
   |---|---|---|---|---|
   | coarse | 64 | 0.089228 | 0.036251 | **8.1883e−04** |
   | medium | 128 | 0.528588 | 0.420914 | **2.0706e−04** |

   **k_coarse / k_medium = 3.955.** Halving h quarters the decay rate — `k ∝ h²`
   to within 1.1 % of the theoretical 4.000.
3. **The registration's own instrument run converged.** The scratch 16 × 64
   instrument arm (1,024 cells) reached 1e−8 by iteration ≈ 60 and 2e−16 by 4,000
   (prereg `:275-277`) — on a mesh **128× smaller than F23's coarse level** and
   **2,048× smaller than its fine level**. *(Correction to the brief: "128×
   smaller than its fine level" is wrong; 128× is the ratio to the **coarse**
   level. 131,072 / 1,024 = 128; 2,097,152 / 1,024 = 2,048.)* The registration
   read convergence off a mesh three orders of magnitude smaller than the one it
   registered, and 4,000 iterations was sized against that reading.
4. **The extrapolation is ruinous.** From the measured rates, iterations to drive
   the bulk error below 1e−8:

   | level | measured / projected k | total iterations required | order of magnitude |
   |---|---|---|---|
   | coarse | 8.1883e−04 measured | ≈ 22,400 | ~2.5 × 10⁴ |
   | medium | 2.0706e−04 measured | ≈ 88,800 | ~1 × 10⁵ |
   | fine | 5.1764e−05 projected at k ∝ h² | ≈ 356,000 | ~4 × 10⁵ |

   These are **order-of-magnitude extrapolations from a fitted rate, not
   measurements**, and are labelled so. The supervisor's brief carried ≈ 25,000 /
   100,000 / 395,000; this lane's independent reconstruction gives ≈ 22,400 /
   88,800 / 356,000 — the same order at every level, ~11 % lower, the difference
   being the target tolerance the extrapolation is run to. Either set says the
   same thing: **the registered 4,000 iterations is short by one to two orders of
   magnitude**, and the fine level alone would cost ~80,700 core-min at the
   supervisor's iteration count (~72,700 at this lane's) against a **1,100
   core-min cap for the whole ladder**.

**So: the wedge guard was the visible failure and the iterative floor was the
fatal one.**

---

## 4. FROZEN FILES — disk == blob at the pre-registration commit, checked by THIS LANE

The F23 grader requires `--prereg-commit` and refuses without one (verified: run
bare, it exits 2 with `REFUSED: --prereg-commit is required for a real grade
(rule 2)`), but it performs no blob comparison of its own. That check was therefore
done by this lane — `git hash-object <disk>` against `git rev-parse 058e7771:<path>`
over **every path the pre-registration commit carries for this case, plus the
gating script** — **19 of 20 SAME**:

| path | blob |
|---|---|
| `cases/F23_HP_WEDGE/build_f23.py` | `2632f9f6` |
| `cases/F23_HP_WEDGE/exact_f23.py` | `c9fc9412` |
| `cases/F23_HP_WEDGE/foam_io_f23.py` | `c0495ae7` |
| `cases/F23_HP_WEDGE/grade_f23.py` | `67c9c5c2` |
| `cases/F23_HP_WEDGE/proj_f23.py` | `dce335ff` |
| `cases/F23_HP_WEDGE/run_f23.sh` | `36b3a679` |
| `case/0/U.template`, `case/0/p` | `6698c822`, `178fed48` |
| `case/constant/fvOptions`, `transportProperties`, `turbulenceProperties` | `b57105f5`, `28780e5f`, `82fba332` |
| `case/system/blockMeshDict.template`, `controlDict`, `decomposeParDict`, `fvSchemes`, `fvSolution` | `9870b585`, `8db8f6ff`, `942f8681`, `e3314097`, `fe429019` |
| `cases/F23_HP_WEDGE/queue_entry_F23_HP_WEDGE.WITHDRAWN_2026-08-26T225538Z.json` | `f1f085b2` |
| `scripts/roache_triple.py` | `78e56a3b` |
| `verification/campaign/F23_HP_WEDGE_PREREGISTRATION.md` | `3af1bca4` |

**One file differs and it is named rather than omitted:**
`cases/F23_HP_WEDGE/queue_entry_F23_HP_WEDGE.json` — blob `6ad48ca7` at the
pre-registration commit, `ec3f345e` on disk. **Structural, not a defect**, and the
same shape F25 recorded: the queue entry is re-issued **against** each freeze, so
it cannot be inside the commit it names. The blob at `058e7771` still carries the
superseded prereg sha `a5f335a6`; the disk copy carries `058e7771` and is
**byte-identical to HEAD** (`ec3f345e` both). Its `grade_cmd` and its
`--prereg-commit` argument both name `058e77719c57332aff245e58d536a343cbde49e5`,
which is the sha checked above. It is an **INFRASTRUCTURE** record by the case's own
`_field_classes` and no verdict reads it.

The launched copy at `verification/queue/cfd/launched/F23_HP_WEDGE.json`
(`04c99f37`) differs from the case copy in exactly two added keys, `_launch` and
`_field_classes`, both written by the queue runner at launch, both INFRASTRUCTURE;
every registered field is byte-identical.

---

## 5. RULE 4 — strict completion, re-read from the run root by this lane

Registered clauses (prereg `:163-165`): `RC.txt` = 0; `End`; latest + 1 > endTime;
`Time` lines == 4000; `U` and `p` at `4000/` in **every one of the 4 processor
directories**, each **newer than the serial `0/U`** (written last at build, before
`decomposePar`).

| level | `RC.txt` | `End` lines | `Time =` lines | `ExecutionTime` lines | last time == endTime | fields at `4000/` | age guard | ClockTime / ExecutionTime | rule 4 |
|---|---|---|---|---|---|---|---|---|---|
| coarse | 0 | 1 | 4000 | 4000 | 4000 == 4000 | `U p phi uniform` in all 4 processor dirs | **16/16 files newer than `coarse/0/U`** | 564 s / 559.51 s | **COMPLETE** |
| medium | 0 | 1 | 4000 | 4000 | 4000 == 4000 | `U p phi uniform` in all 4 processor dirs | **16/16 files newer than `medium/0/U`** | 2,357 s / 2,356.39 s | **COMPLETE** |
| fine | **ABSENT** | **ABSENT** | **ABSENT** | **ABSENT** | **ABSENT** | **ABSENT — no `processor*` directory exists** | **ABSENT — no `fine/0/` exists** | — | **NOT RUN** |

`endTime 4000` confirmed in each level's own `system/controlDict:12`, matching
`exact_f23.N_ITER`.

**Coarse and medium are COMPLETE on every clause of rule 4.** This is worth stating
plainly because it is the trap in this record: *the runs finished cleanly and are
still not results.* Rule 4 asks whether the run was **allowed to produce** an
answer; rule 5 asks whether the answer **converged**. F23 passes the first at two
levels and fails the second at both. A reader who stops at §5 will draw the wrong
conclusion.

**Decomposed, never reconstructed.** `simple n (1 4 1)`, 4 radial bands,
decomposition seed `none` (deterministic geometric, no RNG). Every artefact this
record cites is `<level>/processor{0,1,2,3}/<t>/{U,V}`; `reconstructPar` was never
invoked and no reconstructed time directory exists in the run root.

**Mesh admissibility** from each level's `MESH_LINE.txt` (source `log.checkMesh`):
max non-orthogonality **0°**, max skewness **0.333332683483**, max aspect ratio
**2.00000048739** at coarse and medium, against gates 70° / 4 — as registered. The
fine level's `log.checkMesh` reports **0**, **0.333332683483** and
**2.00000048738** (the aspect ratio differs from the coarser levels in the last
digit only) and `Mesh OK.`, but the build aborted before `MESH_LINE.txt` was
written, so the fine row is read from `fine/log.checkMesh:97,100,103` directly and
is stated as such.

---

## 6. COST — rule 12 estimate-versus-actual

| item | value |
|---|---|
| predicted, registered | **519.4 core-min** for the full three-level ladder (coarse **9.7**, medium **65.7**, fine **444.0**), prereg §7 table, frozen at `058e7771`. Registered **CAP 1,100 core-min**. Rate basis DERIVED, not measured on this case: F17's measured 0.59 µs/cell-iteration grown +30 % per doubling |
| **comparison basis for this row** | **75.4 core-min** — coarse 9.7 + medium 65.7, the two levels that actually ran. The fine level's registered 444.0 is excluded because no compute was spent against it |
| actual, MEASURED from the logs' `ClockTime × ranks ÷ 60` (4 ranks) | coarse 564 s → **37.6000**; medium 2,357 s → **157.1333**; **194.7333 core-min gross** |
| corroboration | the launcher's own running tally in `cases/F23_HP_WEDGE/launcher.queue.out` — *"level medium COMPLETE: ClockTime 2357s x 4 ranks -> cumulative 194.73333333333332 core-min of 1100"* — agrees to every digit |
| ExecutionTime basis, stated beside it | (559.51 + 2,356.39) × 4 ÷ 60 = **194.3933 core-min** |
| the 3,600-second row | no level exceeded 3,600 wall s (max 2,357 s at medium). **There is no stall row and nothing to clean.** ExecutionTime/ClockTime = 0.99204 coarse, 0.99974 medium — the four ranks delivered CPU for 99.2 % and 100.0 % of their wall |
| actual cleaned | **194.7333 — cleaned == gross**, for the reason in the row above |
| **waste, named separately** | **194.7333 core-min — the ENTIRE spend.** See §6.1. Not folded into the ratio below |
| quantisation | `ClockTime` is integer-second: ± 0.0333 core-min per level at 4 ranks |
| share of cap | **17.70 %** (194.7333 / 1,100). The cap was **not crossed, not approached and never raised** |
| dollars | 194.7333 / 60 = 3.24556 core-h × $0.0513/core-h = **$0.1665 — DERIVED, NOT MEASURED** (c7a.4xlarge, reported-by-owner; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5) |
| **ratio actual/predicted** | **2.583** (194.7333 / 75.4); per level **coarse 3.876** (37.600 / 9.7), **medium 2.392** (157.133 / 65.7) |

### 6.1 The waste, stated without laundering (`COMPUTE_BUDGET_CHARTER.md` §6)

**This rung spent 194.7333 core-min and produced no result.** Not a partial result,
not a bounded result, not a diagnostic that a later rung inherits as evidence: two
levels of unconverged startup transient that no gate can read. The full
**194.7333 core-min is waste**, named here separately and deliberately kept **out of
the ratio column**.

The distinction against the C-4 precedent is worth drawing, because the two look
alike and are not. At DPW8_V2 the solver crashed at iteration 182 of 600 and that
spend was **not** waste — *the crash was the measurement*, and the diagnosis rested
on its partial log. Here nothing was measured that the registration set out to
measure. What §3 establishes about the SIMPLE contraction rate was extracted by this
lane **from the wreckage after the fact**; it was not the run's object and does not
retrospectively convert the spend into a purchase.

### 6.2 Gap attribution — TWO causes, and they are different in kind

**(a) MISPREDICTION of the rate — a cost error, worth 2.583×.** The registration
priced F23 from **F17's** measured rate on a **different case** (0.59 µs per
cell-iteration, Kovasznay on a Cartesian mesh) grown +30 % per doubling. Measured on
F23's own levels: **4.303 µs/cell-iteration at coarse** and **4.496 at medium**,
against the registered 1.112 and 1.879 — the base rate was imported from a case with
a different cell topology and a different per-cell cost, and it ran low on an
axisymmetric wedge. Note the direction of the *growth* term is the opposite of the
usual finding: measured level-to-level rate drift is **1.0448**, i.e. **+2.2 % per
doubling against +30 % modelled** — the same over-modelled growth exponent F25
priced at C-4/C-194, but here sitting on a **base rate that was too low by ~4×**, so
the two errors did not cancel and the estimate missed low at both levels. The
registration itself disclosed the better anchor and then did not use it, and the
disclosure was false on the registration's own table. Prereg §7 names VMFL005's
**measured 2.1 µs/cell-iteration** on the lab's other `simpleFoam` wedge and
asserts that the +30 %/doubling growth *"places every F23 level at or above that
reading"*. **It does not:** the registered rates are 1.112 (coarse) and 1.879
(medium), both **below** 2.1 — only the fine level's 3.175 clears it. Measured,
both levels came in at 4.303 and 4.496, i.e. **above** the disclosed anchor. The
wedge anchor was the closer predictor of the two available at registration time,
it was written into the document, and the estimate was built from the other one.

**(b) REGISTRATION DEFECT — NOT a cost misprediction, and must not be filed as
one.** Two registered parameters were wrong on their own terms, independently of
what anything cost:

- **The iterative floor was three to four orders too loose for the iteration count
  bought.** 4,000 iterations was sized against a 1,024-cell instrument run; the
  registered levels need ~2×10⁴, ~9×10⁴ and ~4×10⁵. **No amount of correct cost
  prediction fixes this** — a perfectly-predicted 519.4 core-min ladder would have
  produced three non-results at three times the price.
- **The mesh guard was refinement-fragile by construction** — a fixed absolute
  tolerance on a quantity that grows ~3× per level (§2.4), with the medium level
  already at 80 % of budget and nobody computing the third value.

**A row that reported 2.583 and stopped would say the estimate was merely
optimistic. It was not: the rung was unrunnable as registered.**

### 6.3 The cap arithmetic, CORRECTED — the earlier 1,265 core-min figure was wrong

An earlier supervisor reading projected F23's measured **2.583×** two-level
over-run onto the **registered** fine estimate of 444.0 core-min and landed the
ladder near **1,265 core-min, above the 1,100 cap** — the reading that the cap
would have bitten. **That figure is withdrawn, and the reason is a double count:**
it re-applies to the registered estimate the very rate misprediction that estimate
already contains. The 2.583× *is* the gap between the registered rate and the
measured one; multiplying the registered fine figure by it charges the same error
twice.

Built instead from the **measured** rate — medium's 4.495621e−06 core-s per
cell-iteration over the fine level's 8.388608 × 10⁹ cell-iterations:

| basis | fine level | ladder total | share of the 1,100 cap |
|---|---|---|---|
| measured medium rate, no growth term | 628.53 | 823.27 | 74.8 % |
| **× the case's OWN measured level drift 1.0448** — the launcher's own projector, printed in `launcher.queue.out` | **656.67** | **851.41** | **77.4 %** |
| **× a conservative +30 %/level growth allowance** | **817.09** | **1,011.83** | **92.0 %** |
| *(withdrawn: registered 444.0 × 2.583, added to actual)* | *1,146.8* | *1,341.5* | *122 % — the double count* |

**Under every honest construction the ladder lands UNDER its cap** — by 22.6 % on
the case's own projector and by 8.0 % on the conservative one. **The cap was never
F23's binding constraint**, and no reading of this rung should suggest it was.

*Provenance of the 817 / 1,012 pair, stated because it is not in any artefact:*
this lane reconstructed it as 628.53 × 1.30 = 817.09, i.e. the medium measured rate
carrying one +30 % growth step. The reconstruction reproduces both figures to the
digit, but the 1.30 is a **modelling choice, not a measurement**, and F23's own
measured drift is 1.0448 — which is why the launcher's 656.67 / 851.41 row is
printed above it and is the one an artefact actually carries.

*Provenance of the withdrawn 1,265, stated honestly:* this lane could **not**
reproduce that number exactly from any artefact. The nearest reconstructions are
194.733 + 444.0 × 2.392 = **1,256.6** (medium's ratio) and 194.733 + 444.0 × 2.583
= **1,341.5** (the ladder ratio). The withdrawal stands regardless of which was
meant, because every construction of that family double-counts the same way.

**Contention, present and not separable.** `box_before.txt` / `box_after.txt`
record load1 **12.92 → 15.06 → 14.00** of 16 cores across the run, free cores
3.08 → 0.94 → 2.00, MemAvailable steady at 26.2–28.2 GB. The medium level launched
into the tightest window (0.94 free cores against 4 requested) and still returned
ExecutionTime/ClockTime = 0.9997 — the ranks were not descheduled. The measured
rates already carry the load they ran under and **no separable contention figure
can be extracted from them, so none is invented.**

**Estimate-versus-actual calibration lands as a row in `docs/COST_CALIBRATION.md`,
appended at the file's foot under its own append rules and the rule-10
private-index protocol.**

---

## 7. WHAT THIS RUNG SETTLED, AND WHAT IT DID NOT

**Settled, and it is a real finding even though the rung failed:** the outer SIMPLE
loop on this problem contracts at `1 − O(h²)` under `alpha_U = 0.7`, measured at
`k_coarse/k_medium = 3.955` against a theoretical 4.000 over a 4× cell ratio, with
GAMG reporting `No Iterations 1` throughout. A fixed iteration count is therefore
**not** a mesh-independent convergence criterion for a body-force-driven pipe
started from rest, and any ladder that fixes one is buying non-results at the fine
end. That is transferable to every rung in the family that inherits this
`fvSolution`.

**Not settled, and not claimed:** nothing about Hagen–Poiseuille discretisation
error, nothing about the observed order of the `simpleFoam` wedge, nothing about
the N-AV9 wedge bias in practice, no `E2n` value, no `f·Re` value, no GCI, no
capability-grid cell. The values in §3.3 are printed to **evidence the transient**,
and are explicitly **not** results: they are unconverged, and quoting 66.41 or
110.52 as an `f·Re` measurement would be exactly the error rule 5 exists to
prevent.

**The capability-grid cell 068c2bf0 (axisym · steady · incompressible) is
UNCHANGED by this rung.** Whether it moves is the supervisor's call and is not
taken here.

---

## 8. THE REGISTRATION IS NOT AMENDED; THIS RECORD STANDS ON F23's OWN TERMS

**F23_HP_WEDGE is `NOT A RESULT`, graded against the pre-registration exactly as
frozen at `058e7771`.** This case is **post-compute**: its gates, thresholds, cap
and labels are **closed** (rule 2), and nothing in this record alters, relaxes,
reinterprets or excuses any of them. The registered iterative floor of 1e−8 was not
met; the registered plateau tolerance of 2e−4 was not met; the registered ladder was
not completed. Those are the terms F23 chose for itself before it ran, and they are
the terms it is graded on.

**In particular:** the two registration defects identified in §6.2(b) are recorded
as **findings**, not as grounds for amendment. A registration that turns out to
have been badly chosen is graded as it stands and is **superseded by a successor,
never rewritten** — the whole evidentiary content of the freeze is that the gate
could not have been chosen to fit the answer, and that content is destroyed the
moment a post-compute registration is allowed to move.

**The successor is F23b, separately registered** at
`verification/campaign/F23b_HP_WEDGE_PREREGISTRATION.md`. It is a different case
with its own freeze, its own gates and its own cap. Nothing in this record
authorises, constrains, pre-approves or pre-grades it; no figure here may be
carried into it as a measured basis without being re-derived under its own
registration. **F23's row in any register reads `NOT A RESULT` permanently.**

---

## 9. BOOKKEEPING — L-342 infrastructure fields; none touches a verdict

- `cases/F23_HP_WEDGE/STATUS.F23_HP_WEDGE` reads `launcher_rc=1
  end=2026-08-28T07:54:26Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc`,
  written by the queue runner. Per the case's own `_field_classes`, `STATUS` is
  PHYSICS_CRITICAL and `_launch.pid`/`sid`/`utc`, `LAUNCH_LOG.tsv`,
  `cost_core_min_estimate` and the runner log lines are INFRASTRUCTURE. The
  **solver** rc per level is `RC.txt` = 0 at both levels that ran, cited in §5.
  `launcher.queue.out` under the case directory is the runner's record; not
  committed by this lane.
- **No grade artefact exists in the run root.** `verification/runs/F23_HP_WEDGE_runs/`
  contains exactly three entries — `coarse/`, `medium/`, `fine/` — and no
  `F23_GRADED.json` or `.out` file. The frozen grader was **never run to
  completion against this ladder**: invoked bare by this lane it exits 2 with
  `REFUSED: --prereg-commit is required for a real grade (rule 2)`, and it was not
  re-invoked with the sha, because a two-level ladder gives its `grade_ladder` call
  nothing to classify and the verdict does not turn on its output. **That refusal
  is recorded rather than worked around.**
- **No `CAP_OVERRUN.txt` and no `ESTIMATE_OVERRUN.txt` exist**, consistent with
  §2.3 and §6: the cap did not fire.
- `cases/F23_HP_WEDGE/queue_entry_F23_HP_WEDGE.WITHDRAWN_2026-08-26T225538Z.json`
  is the pre-compute withdrawal record from 2026-08-26 (L-346), kept rather than
  deleted; it is inside the freeze and is byte-identical to it (§4).
- Field data stays on disk under `verification/runs/F23_HP_WEDGE_runs/` and is not
  committed.

## 10. NOT REGISTERED, NOT SENT

No re-grade of any row; **no amendment to the frozen pre-registration** (§8); no
claim about turbulence, discretisation order, or any Reynolds number; `p` is not
graded; no GCI is quoted, and none could be — rule 5 forbids quoting a GCI when
there are not three monotone values, and here there are two values and no triple.
**Nothing is sent, filed, uploaded, registered, posted or submitted** (rule 7).
