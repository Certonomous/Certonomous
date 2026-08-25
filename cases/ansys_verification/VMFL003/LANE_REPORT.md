# VMFL003 — LANE REPORT (`ansys-lane-opus`, Opus 5)

**Report of record.** `SendMessage` from a lane to `ansys-verification-supervisor` is
one-way and fails as unreachable (the mechanical cause of L-306), so this file, and its
commit, is the report. **NOT FILED ANYWHERE; SUBMISSIONS PARKED.**

**Written 2026-08-25T02:06:43Z (`date -u`, read in the writing invocation).**

---

## 1. VERDICT ON THE TASK

**`PENDING` — not yet run, by design.** The task was a pre-registration and the case
artifacts, with **zero compute**, and that is what was delivered. **No `blockMesh`, no
`checkMesh`, no `topoSet`, no `simpleFoam`.**
`verification/runs/ansys_verification/VMFL003/` **did not exist at 01:59:15Z and did
not exist at 02:06:43Z** — checked with `ls -d`, which returned *No such file or
directory*. The only execution of any kind was `grade_vmfl003.py --selftest`
(**60 checks, 0 failures**, no run tree touched). **Cost of this lane's compute: 0.00
core-minutes.**

**Compute stays locked until you personally verify the freeze** (`SUPERVISION_CHARTER.md`
§3 check 4). No agent message is Sanaa's consent (rule 9).

## 2. THE TWO COMMITS, IN THE ORDER THAT MAKES THE FREEZE EVIDENTIARY

| | commit | what |
|---|---|---|
| 1 | **`9fea6a65fc294ff8e8f2d83c0db89f7496581932`** | case inputs, launcher, comparator — 14 files, **2077 insertions, 0 deletions**, all status `A` |
| 2 | **`9195d25e8783b9ff4f5aca6c20a298c1bceec63a`** | **THE FREEZE** — `PREREGISTRATION.md`, 1 file, **908 insertions, 0 deletions** |

Five peer commits landed between them; `git merge-base --is-ancestor 9fea6a65 HEAD`
confirms nothing was lost and all 15 VMFL003 paths are present at HEAD.

**Frozen `PREREGISTRATION.md` blob: `e969e65416f7eec56dee02a20778abf6b9e28fcf`** —
re-hashed after commit and byte-identical to HEAD.
**Frozen comparator blob: `15b14d40f166cc31770ead452c27905332670c97`** —
`grade_vmfl003.py --verify-frozen HEAD` returns rc = 0.

**Git discipline, as instructed.** Private index in scratch; base sha captured in the
**same shell invocation** as the commit; `rm -f` on the index and raw files first;
**path + status assertion before `commit-tree`**, gated with `|| { echo ABORT; exit 1; }`
on the heredoc, **not** `set -e`; unchanged-tree guard; CAS `update-ref`; **mandatory
post-commit audit** on both. No `git add -A`, no bare `git commit`, no touching the
shared index. **The gating pattern demonstrably worked:** commit 1's first attempt
**ABORTED** because `git diff-tree --raw` without `-r` reported the tree entry `cases`
as a foreign path — the assertion stopped the commit rather than printing past it.
Both files end in a trailing newline; neither commit touched a shared ledger, so the
append hazard did not arise here.

## 3. THE GATE AND ITS BAND

> **G-VMFL003:** at `L3_1000x5`, **|Δp_lab − 21744 Pa| / 21744 ≤ 0.025 (2.5 %)**.

**Δp_lab = 1.225 × (areaAverage(p)_inlet − areaAverage(p)_outlet)** at `endTime` — the
manual's own definition of the compared quantity (p. 19: *"pressure difference between
inlet and outlet"*). Target **21744 Pa**, Tables .03.1 and .03.2, **p. 20**, both
solvers' "Target" column.

**The 2.5 % is derived, not chosen.** Declared systematics sum to ≈ **0.98 %** linear
worst case (chart-read ±0.176 %, print rounding ±0.0023 %, entrance excess +0.28…+0.70 %,
wedge +0.0953 %); the manual's own two "standard k-ε" codes differ from each other by
**1.210428 %**; (i) + (ii) ≈ **2.2 %**; the manual's own stated goal is 3 % (§1.3, p. 5)
and the lab holds itself inside it at 2.5 %.

**The band is a bar, and every row is asserted in `--selftest` with zero compute:**
laminar 3578.80 Pa (**−83.54 %**) **FAILS**; inviscid 0 Pa **FAILS**; **Blasius
22366.01 Pa (+2.8606 %) FAILS**; ±2.6 % **FAILS**; ±2.4 % passes.

**Declared before compute, and it is the opposite of VMFL045's posture: this band
PASSES both Ansys solvers** (Fluent 21480 = −1.2141 %, CFX 21740 = −0.0184 %). VMFL045
could fail Fluent because its target was a closed-form shock solution with no
uncertainty of its own. Here the target is a **chart read** and the two Ansys codes
disagree by 1.21 %, so **a band that failed one of them would assert a resolution the
reference does not have.** The finer statement is carried by the f_dev diagnostic
instead. **If you judge 2.5 % too loose, 2.0 % still contains (i)+(ii) marginally —
that is your call, made before you unlock compute. My recommendation is 2.5 %.**

## 4. THE REFERENCE, DERIVED HERE

The manual names the **Moody chart**, so the reference is the smooth-pipe
**Colebrook / Prandtl–von Kármán** branch — **not Blasius**, and that reading is
confirmed arithmetically, not assumed:

| quantity | value | note |
|---|---|---|
| ν = μ/ρ | **1.4607346938775508e-05 m²/s** | derived from the manual's own properties |
| Re = ρUD/μ | **13691.740248127866** | manual says 1.37 × 10⁴ — 0.06 % |
| q = ½ρU² | **1531.2500000000002 Pa** | |
| **f_Colebrook** | **0.028464169573919965** | |
| **Δp_Colebrook** | **21792.879830032474 Pa** | **+0.224797 %** vs the printed target. **A DIAGNOSTIC (2 % band), never the gate.** |
| f implied by the target | **0.02840032653061224** | |
| Δp at f = 0.0284 | **21743.750000000004 Pa** | **reproduces the printed 21744 to six significant figures** |
| Δp_Blasius | 22366.01057087875 Pa | +2.8606 % — cannot be what the manual used |
| Δp_laminar | 3578.7999999999997 Pa | −83.54 % — negative control |

## 5. THE GRID TRIPLE, THE y+ TARGET, AND THE WALL TREATMENT

**Wall treatment: `nutkWallFunction` + `kqRWallFunction` + `epsilonWallFunction`** —
the OpenFOAM analogue of Fluent's and CFX's **standard** wall function, which is the
treatment the manual names. `nutUSpaldingWallFunction` was considered and **declined**
(it is a different wall treatment from the one the manual ran).

**y+ target: 40.835033970764385** — mid-log-layer — with a **one-way `NOT A RESULT`
band of [25, 65]** on the measured mean wall y+.

| level | N_x × N_r | **cells** | h = Δx | endTime | predicted y+ |
|---|---|---|---|---|---|
| `L1_250x5` | 250 × 5 | **1250** | 0.008 m | 6000 | 40.835 |
| `L2_500x5` | 500 × 5 | **2500** | 0.004 m | 8000 | 40.835 |
| `L3_1000x5` | 1000 × 5 | **5000** | 0.002 m | 12000 | 40.835 |

**Refinement ratio 2 exactly, by construction, in the AXIAL direction. The radial mesh
is HELD FIXED — and §6 below is why.**

## 6. THE FINDING THAT SHAPES THE CASE, AND IT GENERALISES TO THE OTHER 29 TURBULENT CASES

**R⁺ = R·u_τ/ν = 408.3503397076439.** The entire pipe radius is 408 wall units.

A log-layer wall function needs the first cell centre at y⁺ ≳ 30 and y/R ≲ 0.2, i.e.
**y⁺ ∈ [30, 81.67] — a factor of 2.72**. With a uniform radial mesh that is
**N_r ∈ [2.50, 6.81]**. **A three-level ratio-2 family spans a factor of 4. It does not
fit**, and no grading rescues it, because adding radial cells can only make the wall
cell smaller (δ₁ < R/N_r always).

**General form, registered before any result and drafted for `NUMERICS_KNOWLEDGE`:** a
three-level ratio-2 family fits inside [30, 0.2 R⁺] only if **R⁺ ≥ 600**; for a pipe
R⁺ = (Re/2)√(f/8), so the threshold is **Re ≈ 21252**. **VMFL003 at Re = 13692 is below
it.** Every turbulent case in the campaign now has a cheap test for whether a 2-D
ratio-2 wall-function family is even possible.

**Consequence, stated on the face of the freeze:** the GCI this family produces bounds
the **AXIAL** channel only. **A small GCI will NOT license calling the remaining
deviation numerical** (`N-AV7`). A declared **wall-treatment ladder** at N_r = 3/4/5/6
(y⁺ = 68.06 / 51.04 / 40.84 / 34.03), fixed N_x = 500 — **not a Roache triple, never
Richardson-extrapolated** — measures the channel the GCI cannot see, with a one-way
`NOT A RESULT` clause if its spread exceeds 5 %.

## 7. THE THREE HAZARDS, EACH ADDRESSED BEFORE COMPUTE

**(a) The turbulence-model difference.** The coefficient sets are **identical** (C_μ
0.09, C₁ 1.44, C₂ 1.92, σ_k 1.0, σ_ε 1.3) and `constant/turbulenceProperties` writes
them out explicitly rather than defaulting them — so the remaining difference **is** the
wall treatment. **The manual measured this itself and never remarked on it:** Fluent
21480 and CFX 21740, **a 1.210428 % spread between two implementations of the same
stated model**, which does not shrink with refinement. Fluent's is *low* despite also
carrying the entrance excess, so its k-ε wall friction sits ~1.5–1.9 % under Moody.
Addressed by: the declared wall treatment, the frozen y⁺ target and band, the ladder,
the f_dev diagnostic, and the explicit statement in §7a/§12 of the freeze that a small
GCI licenses nothing.

**(b) The wedge area deficit (`N-AV9`).** Half-angle **2.5° (5° total)**, wall vertices
at exact radius R. Area ratio sin(2α)/(2α) = 0.9987312439537492 ⇒ deficit
**0.1268756046250763 %**, which **reproduces `N-AV9`'s recorded constant exactly** — an
independent confirmation of the team's own number. Wetted-area ratio sin(α)/α ⇒
0.03172796079918827 %.

> **CORRECTION TO HOW `N-AV9` TRANSFERS — please read this one.** The recorded ≈ **+0.25 %**
> Δp consequence was derived for **VMFL005**: laminar, **fixed Q**, R⁻⁴. **VMFL003 fixes
> a VELOCITY (50 m/s uniform) and is turbulent** (τ_w ∝ U^1.75). **The +0.25 % does not
> transfer and would over-state the term by 2.6×.** The correct transfer is the
> streamwise force balance Δp·A_cross = τ_w·A_wall, whose ratio is **exactly sec α**:
>
> **Δp is HIGH by sec(2.5°) − 1 = +0.09526851633199218 %**, azimuthal, removed by no
> refinement. Budgeted as a one-sided +0.0953 %. Drafted as an addendum to `N-AV9`.

**(c) Plateau / iterative convergence.** VMFL051's failure mode, translated to a steady
solver: **per-level convergence checked BEFORE the triple is formed**, in two
independent legs, both frozen — final **initial** residuals of p, Ux, k, ε each
**< 1.0e−8**; and peak-to-peak of **the gate quantity itself** over its last 20 %
**≤ 1.0e−2 Pa**. Predicted level-to-level differences are **6–45 Pa**, so the plateau
tolerance sits **600–4500× below the signal** — the separation VMFL051 showed to be
necessary. **A level that fails either leg is `NOT A RESULT` and re-runs at a longer
endTime as a NEW RUNG, never re-graded in place.**

**Expected observed order, registered before measurement: p ≈ 1**, because the axial
error of the gate quantity lives almost entirely in the limited (`limitedLinear`)
entrance region while the ~96 % fully-developed pipe contributes essentially zero (its
pressure is linear in x and exact on every level). **And the warning is on the face:
a p in [1.90, 2.10] here would be a coincidence to report and interrogate, NOT a
confirmation — a suspiciously good order is the failure mode nobody reports.**

## 8. WHAT IS INTERNALLY INCONSISTENT OR UNDER-SPECIFIED IN THE MANUAL'S VMFL003

Six findings, all in §1a of the freeze, all recorded **before** any number existed. The
four substantive ones:

1. **The friction factor is never printed and the target is a 3-s.f. Moody-chart read.**
   f = 0.0284 reproduces 21744 to six significant figures. The target therefore carries
   **±0.176 %** of its own uncertainty, and the exact Colebrook value sits **0.2248 %**
   away from it. **CFX's printed ratio of "1.000" is a coincidence at a precision the
   target does not support** — a reader would take it as agreement to 0.1 %, and the
   target is not known to 0.1 %.
2. **The analytical target and the compared quantity are not the same quantity.** The
   target comes from the **fully-developed** formula; the comparison is
   **inlet-to-outlet** under the only inlet condition given, a **uniform** 50 m/s.
   Entrance length 4.4·Re^(1/6)·D = **0.08608400083579049 m = 21.52 D = 4.30 % of the
   pipe**, worth **+0.28 % to +0.70 %** of Δp, unstated and unbudgeted — **larger than
   the CFX ratio's implied precision.**
3. **No inlet turbulence boundary condition is specified anywhere in the section.** A
   k-ε run cannot start without one. Resolved as a declared choice (I = 5 %,
   l = 0.07 D ⇒ k = 9.375, ε = 16845.37817870935), the Fluent/CFX pipe defaults.
4. **A 1.21 % spread between the manual's own two implementations of the same model**,
   printed in adjacent tables and never remarked on.

Also: geometry under-specified beyond "half of the axisymmetrical domain" (no wedge
angle, no mesh, no inlet-plane treatment); and Re is internally **consistent** (13691.74
vs the stated 1.37 × 10⁴), recorded so the consistency is on the record too.

## 9. A DEFECT IN THIS TEAM'S OWN RECORD — reported, not fixed

**`VMFL005/PREREGISTRATION.md` §9 states its per-cell-iteration rates with exponents
1000× too small.** It writes *"VMFL001's measured per-cell-iteration rates: L1 6.51e-10,
L2 1.06e-9, L3 2.12e-9 s/(cell·iter) (from VMFL001 R1: 2 s / 13 s / 104 s at 3000 iters
× 1024 / 4096 / 16384 cells)"*. The stated basis gives **2/(3000 × 1024) = 6.51e−7**,
**13/(3000 × 4096) = 1.06e−6**, **104/(3000 × 16384) = 2.12e−6** — i.e. **e−7/e−6/e−6,
not e−10/e−9/e−9**. The same section then quotes *"L1 1000×2000×6.51e-10 = 1.3 s"*,
which is only true at 6.51e−7 (the stated exponent gives 1.3 **milliseconds**).

**Nothing downstream is wrong:** the products quoted (1.3 / 12.7 / 203.1 s, total ~295 s
≈ 4.9 core-min) are internally correct and consistent with VMFL005's actual cost. It is
a **labelling** error in the exponents only, and it changes no VMFL005 verdict, band or
cost. I caught it because I tried to *reuse* the rate and got a cost estimate 1000×
too cheap.

**I have not touched the file** — frozen files are never edited (rule 6), and whether it
warrants a dated addendum is your call, not mine. VMFL003's §9 uses the **corrected**
basis: VMFL005's measured aggregate **2.18e−6 s/(cell·iter)** (240 s for 1.1e8
cell-iterations), which independently corroborates VMFL001's 2.12e−6.

## 10. COST (CLAUDE.md rule 12)

| | value |
|---|---|
| **point estimate** | **9.6 core-minutes** (1.395e8 cell-iterations × 3.5e−6 s + 40 s meshing + 49 s FO margin ≈ 577 s) |
| **enforced cap** | **24 core-minutes** = 2.5 ×, enforced by `timeout` against a **running total** across all six meshes |
| requested from you | **25 core-minutes** — a per-item cost, not a new ceiling (rule 9) |
| dollars at the estimate | **$0.008208** — **DERIVED, NOT MEASURED** |
| dollars at the cap | **$0.020520** — **DERIVED, NOT MEASURED** |
| `cost_basis` | owner-stated $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). The per-cell-iteration rate is a **measurement**; the **k-ε multiplier of 1.6**, the iteration counts, the meshing time and the FO margin are **ESTIMATES**. |
| honest note | the optimistic end (VMFL001's small-mesh rate, closer to these 1250–5000-cell levels) gives **5.0 core-min**. The point estimate is deliberately the pessimistic one because the k-ε multiplier is unmeasured. |

**The launcher uses the GENERAL formulae**, with `RANKS` in them, so a future parallel
copy inherits a correct cap: **`TIMEOUT_S = REMAINING_CORE_MIN * 60 / RANKS`** and
**`CORE_MIN = WALL_S * RANKS / 60`**.

**The k-ε multiplier of 1.6 is the specific figure the completion calibration should
test** — its measured value is reusable across the other 29 turbulent cases, which is a
second reason this case was worth running first. One row for
`docs/COST_CALIBRATION.md` at completion; a completion report without it is incomplete.

## 11. YOUR TWO ADDITIONS — both applied

**(1) Pre-flight smoke test.** `run_vmfl003.sh` runs **one iteration on the coarsest
mesh in a `mktemp -d` scratch directory outside `verification/runs/`**, and **aborts the
whole run** if `blockMesh`, `checkMesh`, `topoSet` or the first timestep fails, or if no
`End` line appears. The scratch tree is deleted and nothing it produces is ever graded.
Written into the file with the reason on the face: a comparator `--selftest` proves the
**grader**, not the **case**. **It has not been run** — running it is compute.

**(2) `fvSolution` covers every variable actually solved.** `simpleFoam` + `kEpsilon`
solves p, U, k, ε; `nut` is algebraic. `fvSolution` carries `p` plus the regex
**`"(U|k|epsilon)"`** — a **class**, not three named instances (the L-221/L-222
posture). Relaxation factors are set for U, k, ε and p. `nut` correctly has no entry.

**On `set -e`:** applied throughout. `run_vmfl003.sh` states in its header that `set -e`
is deliberately not relied on, and **every** check — the freeze check, the
`--verify-frozen` call, the pre-existing-directory guard, the OpenFOAM sourcing, the
case build, the meshing, the empty-zone check, the budget check, the age-guard touch,
the solver rc — gates with an explicit `|| { echo ABORT…; exit 1; }`.

## 12. WHAT I COULD NOT VERIFY — plainly

- **That the mesh builds.** No `blockMesh` has run, so there is no `checkMesh` summary
  to quote. The 5° wedge is 500 D long with aspect ratio Δx/Δr of 20 (L1) to 5 (L3);
  that is unremarkable, but it is a judgement, not a measurement.
- **That `topoSet` fills both frozen zones.** Derived arithmetic, not measured. The
  launcher refuses before the solver if either is empty.
- **The live `.dat` files.** Readers are built from the v2606 writer sources
  (`surfaceFieldValue.C:719-745`, `volRegion.C:133-143`, `yPlus.C:50-60`); no run has
  produced one. `--dryrun-reader` prints structure only, never a value (L-286).
- **The predicted y+ is a prediction**, resting on u_τ from *Colebrook*. The [25, 65]
  band is a clause, not a forecast.
- **That 6000 / 8000 / 12000 iterations reach residual < 1e−8.** An estimate.
- **The order, the GCI, the ladder spread and f_dev.** All findings, whatever they are.
- **Anything about the manual's own runs.** I could not determine what inlet turbulence,
  wedge angle or near-wall y⁺ Fluent and CFX used. Their archives were not opened and
  this box has neither code. **So the 1.21 % Fluent–CFX spread is a measurement of
  *something*, and I cannot say how much of it is wall treatment and how much is mesh.**

## 13. WHAT I NEED FROM YOU

1. Your **personal** read of `grade_vmfl003.py` **as a diff** and of the freeze
   (`SUPERVISION_CHARTER.md` §3, checks 1 and 4) — a relayed check is a summary, not a
   check.
2. A ruling on the **2.5 % band** (my recommendation) versus 2.0 %. **A change is legal
   only before compute** and only as a pre-compute amendment stating the condition and
   how it was checked.
3. Authorisation of **25 core-minutes** for this case, and the compute unlock.
4. Whether **`N-AV9` should carry my correction** (§7b) and whether **`VMFL005`'s
   exponent labelling** (§9) warrants a dated addendum — both are yours, not mine.
