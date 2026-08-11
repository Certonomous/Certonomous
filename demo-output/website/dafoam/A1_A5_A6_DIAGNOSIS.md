# A1, A5, A6 — diagnosis from the record and the archives

**2026-08-11. Zero solver core-min. No solver, no DAFoam run, no container, no mesh
generation was launched; compute authorisation for this work was not given and was not
taken.** Everything below is read out of logs, dictionaries and committed records that
already existed. Where a question needs a run to close, it is written down as a priced
request in §5 rather than answered.

Anchored at commit `1393b8b4` (`main`, 2026-08-11). Numbers below carry their frame and
filter beside them.

## Frames used

| tag | frame | how enumerated |
|---|---|---|
| **R** | the repo at `1393b8b4` | `/usr/bin/grep -rn --include=*.md` over `docs/` and `demo-output/website/` |
| **L** | `*.log` under `/home/ubuntu/certonomous-runs/` | `find /home/ubuntu/certonomous-runs -type f -name '*.log'` → **595 files**, 66 GB tree |
| **L-stat** | the subset of L printing `Printing Primal Residual Statistics` | `find … -print0 \| xargs -0 /usr/bin/grep -l` → **301 of 595** |

**This shell's `grep` is `ugrep --ignore-files`** and honours `.gitignore`; every count and
every quotation below was taken with `/usr/bin/grep` and `find`. The run archive is outside
the repo and is invisible to a repo-scoped sweep.

---

# 1. A1 — the sign flip. Two mechanisms, same component, both decided on the record

## 1.1 The symptom, quoted

The A1 rung is the DAFoam NACA0012 incompressible tutorial, 4,032 cells, 8 shape FFD design
variables plus a 2-component `patchV`. The graded failure is `CD wrt shape`. From the stock
re-run log, `/home/ubuntu/certonomous-runs/W5-regrade/a1_unpatched_stock.log:2981-2996`,
verbatim:

```
  Full Model: 'scenario1.aero_post.functionals.CD' wrt 'dvs.shape'
    Analytic Magnitude: 6.460294e-02
          Fd Magnitude: 6.489575e-02 (fd:central)
    Absolute Error (Jan - Jfd) : 7.415918e-03 *

    Relative Error (Jan - Jfd) / Jfd : 1.142743e-01 *

    MPI Rank 0

    Raw Analytic Derivative (Jfor)
[[-0.01134166 -0.02217955  0.00679853  0.01238019  0.03893835  0.0423425
   0.00569076  0.0034668 ]]

    Raw FD Derivative (Jfd)
[[-0.01013195 -0.01986336  0.00726445  0.01290186  0.03998419  0.04339013
  -0.00105334  0.00353133]]
```

**The sign flip is component 6 and only component 6.** Analytic `+0.00569076` against a
finite difference of `−0.00105334`. Seven of the eight components agree in sign; the
aggregate is 11.43%. Per-component absolute errors, recomputed from those two vectors:

| comp | 0 | 1 | 2 | 3 | 4 | 5 | **6** | 7 |
|---|---|---|---|---|---|---|---|---|
| Jan − Jfd | −1.210e-3 | −2.316e-3 | −4.659e-4 | −5.217e-4 | −1.046e-3 | −1.048e-3 | **+6.744e-3** | −6.45e-5 |

Component 6 is the only positive error, is 2.9× the next largest in absolute terms, and sits
on the smallest true derivative in the vector (|Jfd| = 1.05e-3 against 4.0e-2 at comps 4/5).
Both facts push it over zero. Component 6 is the **leading-edge combination FFD mode**
(`UPSTREAM_BUG_REPORT_mesh_warpDeriv.md:692`).

**There is a second, separate A1 sign flip, at the same component index**, in a variant that
adds a slope limiter. `/home/ubuntu/certonomous-runs/W4-defect-robustness/a1lim_np1.log:2317-2329`:

```
  Full Model: 'scenario1.aero_post.functionals.CD' wrt 'dvs.shape'
    Analytic Magnitude: 1.066449e-01
          Fd Magnitude: 6.194868e-02 (fd:central)
    Relative Error (Jan - Jfd) / Jfd : 9.284586e-01 *

    Raw Analytic Derivative (Jfor)
[[-0.03489979 -0.03723728  0.00629101  0.01037603  0.0614431   0.06441492
  -0.02591213  0.00503046]]

    Raw FD Derivative (Jfd)
[[-0.0090538  -0.02034151  0.00701134  0.0134931   0.03731132  0.04048882
   0.00849673  0.00264465]]
```

Again exactly one sign disagreement, again component 6 — and this time the analytic is
**negative** where the FD is positive, the opposite orientation to the stock flip. This run
carries `IDWARP_IMPORTED_FROM: /patch/idwarp/idwarp/__init__.py` at line 3, i.e. **the
rotation-guard patch was already applied when this flip was measured.** The two are not the
same defect.

## 1.2 Ranked candidate mechanisms, with what kills each

A gradient sign error has a small enumerable cause set. All seven classical causes are
decidable from artifacts already in the archive. Taking them in order of how cheaply they
die:

| # | mechanism | supporting evidence | killing evidence — **executed** |
|---|---|---|---|
| 1 | **Objective sign convention** (CD defined with the opposite sign somewhere in the chain) | a flipped objective flips the gradient | **DEAD.** A convention error is global. 7 of 8 components in the *same printed vector* agree in sign (`a1_unpatched_stock.log:2990-2996`). Also `CD wrt patchV` reads 0.2317% with correct sign in the same run. |
| 2 | **Adjoint residual / transpose convention** (a global sign or transpose slip in the adjoint solve) | would produce a wrong gradient at converged Krylov | **DEAD.** Same globality argument as #1; and the four-line fix that removes the flip touches only `src/adjoint/outputReverse/vectorUtils_{b,d}.f90` in IDWarp — the adjoint linear solve is not in the patch's footprint, and `PetscConvergedReason` and Krylov counts are unchanged. |
| 3 | **Mesh orientation / flipped face normal in the primal** | the mechanism *is* about surface normals | **DEAD.** The primal is bit-identical between the runs that differ in the flip: `CD: 0.02090808860837286` and `Minimal residual 9.917819850026459e-09`, identical to all 17 digits in both `a1_unpatched_stock.log` and `a1_patched_patched.log`, both terminating at `Time = 435`. A flipped normal changes the flow field. |
| 4 | **Summation over patches** (a sign lost while integrating the objective over wall patches) | classic for force objectives | **DEAD.** Two ways. (a) The geometric constraints `volcon`/`thickcon`/`rcon` — pure surface functions over the same patch set, sharing the whole FFD/DVGeo Jacobian chain but no CFD — read 4.37e-12 %, 1.27e-11 % and 1.36e-08 % and **do not move** under the patch (`W5_GRADIENT_REGRADE.md` §1). (b) IDWarp's `sum(dXs)` is bit-identical with the rotation term present and absent on all five of upstream's own regression meshes, i.e. the term at issue sums to exactly zero over the surface — a patch-summation error cannot be invisible in that sum and visible per component. |
| 5 | **The finite difference is the wrong one** (a limiter kink, or FD noise, making the FD's sign meaningless) | idx6 has the smallest true derivative, so it is the most FD-fragile component | **DEAD, twice, and this is the axis that could have gutted the finding.** (a) Step study on upstream's own failing DOFs: FD stable to 6 significant figures across `h` = 1e-4 → 1e-6, roundoff appearing only at 1e-8 (`ROOTCAUSE_getRotationMatrix3d.md` §4.1). (b) For the *limiter* flip, the one-sided slopes were reconstructed free from the FD legs' own printed converged CD values: at component 6 both the forward (`+0.009660`) and backward (`+0.007334`) secants are positive at h=1e-3 and at h=3e-3, while the analytic is `−0.025912` — **the analytic lies outside the [backward, forward] bracket, on the wrong side of zero, at 3× the magnitude** (`VERIFICATION_A1_serial_limiter_supervisor_sweep.md` axis 3c). No branch selection available to the FD produces a negative slope there. |
| 6 | **Mesh decomposition** (the A4 mechanism: a parallel transposed-Jacobian product that is not the transpose of the discrete residual) | it is a proven defect in this stack on A4 | **DEAD for A1.** np=1 vs np=4-scotch analytic vectors agree to 3.9446e-04 vector-relative, per-component max 0.197% (`a1lim_np1.log` vs `a1lim_np4scotch.log`, recomputed in the supervisor sweep axis 2). The flip is present identically in serial. A1 is decomposition-invariant — which certifies consistency, not correctness. |
| 7 | **Frozen wall distance** (`forceMeshWaveFrozen=True` omitting `d(yWall)/d(shape)`, concentrated at the leading edge) | the leading LE-localised candidate for two sessions; it is the mechanism the A1 ladder record still names | **DEAD, and this is the archive deciding a live claim.** `forceMeshWaveFrozen 1;` is active in both runs (`a1_patched_patched.log:436`) — the lever is unchanged between them — yet the four-line IDWarp derivative patch collapses component 6 from `+0.00569076` to `−0.00106561` against an FD that does not move a digit. A mechanism that is identically active on both sides of a change cannot explain a difference the change produces. `PROOF.md` records this as refuted at 8 separate summary tables; **`ladder-a/A1_naca0012_incompressible.md:166-169` still carries it as the standing candidate, uncorrected.** |

### The surviving mechanisms

**M1 — IDWarp 2.6.2's degenerate-rotation guard (stock A1).** `src/utils/vectorUtils.f90:58`
replaces a removable coordinate singularity with `angle = 0`; Tapenade's reverse
(`vectorUtils_b.f90:123-128`) correctly differentiates the branch that was taken and therefore
returns `dMi/dnormals = 0` exactly. At an undeformed baseline — the state at which every
`check_totals` and every first design iteration is evaluated — the guard is guaranteed to fire,
so `warpDeriv` returns a derivative from which the surface-normal-rotation term is exactly
absent. Full derivation, source citations and seven pre-registered predictions:
`ROOTCAUSE_getRotationMatrix3d.md`.

**M2 — the slope limiter's min/max selection in the AD tape (A1 + `cellLimited`).** With M1
already patched, adding two lines to `fvSchemes` — `limited cellLimited Gauss linear 1;` in
`gradSchemes` and `div(phi,U) bounded Gauss linearUpwind limited;` — takes the same case from
0.043% to 92.8% with a component-6 flip, curable by changing the single word `limited` →
`default` (0.121%).

## 1.3 What the archives already decide

Five things, all of them free, and three of them are the strongest evidence in the file:

1. **M1's lever activity is proven, not asserted (L-40).** The direct proof is the
   fingerprint, not a dictionary echo. `REPRO_ANFINGERPRINT useRotations=on
   ||dXs||=1.495168856286067e+03` (`W5-rotation-branch/D1a_pl_real_rot_ON.log:838`) is
   **identical to every digit** to the rotations-OFF run at the undeformed baseline — that
   identity *is* the branch being dead — and it **differs** (`1.566420804338303e+03`) once the
   baseline is pre-deformed so the guard stops firing. The switch's state is read off the
   derivative it produces.

2. **The AD moved to the FD, not the reverse.** Component 6 goes `+0.00569076` →
   `−0.00106561` against an FD that stays bit-identical at `−0.00105334`, and the other seven
   components move in the 4th-to-5th digit only
   (`a1_patched_patched.log:2990-2996`). A comparison-zeroing artifact cannot move one column
   onto an already-converged other column while leaving the primal at 17 identical digits.

3. **M1 and M2 are independent, and the archive proves it rather than arguing it.** M2's four
   arms all carry `IDWARP_IMPORTED_FROM: /patch/idwarp/…` at line 3. The patched, unlimited
   baseline (`a1fs_np1`) reads 0.043%. So M2 is a defect that survives M1's repair.

4. **M2's lever activity is proven behaviourally, which is stronger than the echo it lacks.**
   `/usr/bin/grep -n -E "cellLimited|linearUpwind|divSchemes"` over `a1fs_np1.log`,
   `a1lim_np1.log` and `a1limdef_np1.log` returns **nothing but the IDWarp stamp** — these
   logs do not echo `fvSchemes` at all, so the L-40 dictionary-echo route is unavailable.
   The primal settles it instead:

   | arm | `div(phi,U)` | stops at | converged CD |
   |---|---|---|---|
   | `a1fs_np1` (clean baseline) | `bounded Gauss linearUpwindV grad(U)` | `Time = 251` | 0.02087031456925589 |
   | `a1lim_np1` (limiter on) | `bounded Gauss linearUpwind limited` | `Time = 242` | 0.01956447711316437 |
   | `a1limdef_np1` (the one-word cure) | `bounded Gauss linearUpwind default` | `Time = 232` | 0.01904188196895532 |

   Three different iteration counts and three different converged drag values. The scheme
   reached the discretisation; it is not a dead lever.

   **But the same table names a caveat the record does not.** M1's repair was
   primal-bit-identical by construction *and* by measurement. M2's is not: the one-word cure
   moves the converged CD by 2.7% (0.019564 → 0.019042). R7f2's 0.121% is therefore measured
   against a **different converged flow**, not a repaired derivative of the same one. That is
   a legitimate result about which discretisation has a differentiable tape, but it is not the
   same kind of claim as M1's, and the two should not be read as a matched pair.

5. **A5 and A2 are not exposed to M2.** `W4-a5-decomp/a5_scotch/system/fvSchemes:23-31`,
   `W5-regrade/a5pl_stock/system/fvSchemes` and `W5-rotation-branch/UBend_Channel/system/fvSchemes`
   all carry `gradSchemes { default Gauss linear; }` and `div(phi,U) bounded Gauss linearUpwindV
   grad(U)` — **no `cellLimited` token anywhere.** The L-40 asymmetry matters here and is worth
   stating as a method note: a lever that *is* requested may nonetheless be inert, so
   dictionary evidence cannot prove activity; but a lever that is *not* requested cannot
   become active, so dictionary evidence **can** prove absence. This elimination is sound in
   the direction it is used.

## 1.4 What the archives do not decide

**One stated check is confounded, and it is stated as passed.** `ROOTCAUSE_getRotationMatrix3d.md`
§4.7 answers Katie's standing reordering question with prediction P6 — "adjoint matrix reordering
(`rcm` vs `natural`) must not move the result at all" — and reports 207.04% vs 207.05% at idx8,
concluding *"Reordering is not a factor, exactly as a purely geometric defect requires."*

The activity evidence for `rcm` in those two runs is
`W5-rotation-branch/D5a_pl_real_rotON_RCM.log:825` `Mat ReOrdering: rcm` — which
`docs/DEAD_LEVER_AUDIT.md` §4 U-1 identifies as the **requested-value** print, not a readback.
Checked directly: `/usr/bin/grep -c "matrix ordering"` returns **0** for
`D5a_pl_real_rotON_RCM.log`, `D5b_pl_real_rotOFF_RCM.log` and `D1a_pl_real_rot_ON.log`, and
neither D5 log contains a `KSP Object` block at all.

**Positive control for that negative**, as this lab requires: the identical grep against
`/home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock/control_rcm.log` returns
`12:    matrix ordering: rcm`. The method finds the readback when it is present; its absence
in D5a/D5b is a fact about those logs, not about the search.

So **P6's null result is exactly what an inert `rcm` lever would produce**, and the check as
written does not discriminate. This does **not** threaten M1: M1 is established upstream of
any linear solver by the `||dXs||` fingerprint (§1.3 item 1), by the rotations-off collapse to
0.0000 on all 27 components, and by the CFD-free reproduction of upstream issue #57. The
finding survives; the *stated* elimination of reordering does not, and it should be relabelled
rather than relied on. Filed as **D40**.

## 1.5 Verdict on A1

**The sign flip is diagnosed, twice over, and both diagnoses are defended by the archives.**
The graded FAIL against the shipped toolchain is M1 and holds at 11.43%; under the corrected
derivative the same case reads 0.03745%, with the primal and the FD both bit-identical. The
same case under a limited convection scheme carries an independent, unrelated component-6 flip
(M2) that the M1 patch does not touch.

Two record defects fall out, neither fatal:

* `ladder-a/A1_naca0012_incompressible.md:166-169` still names `forceMeshWaveFrozen` as A1's
  candidate mechanism for the idx6 flip. `PROOF.md` refutes it in eight summary tables and the
  patch refutes it independently (§1.2 row 7). The ladder record is the case's own primary
  document and under the family's own record-hygiene rule (`FAMILY_SUPERVISION_GUIDELINES.md`
  §7) it should be corrected first, quote-and-strike.
* `docs/PRODUCT_LIST.md:166-175` states A1 "fully root-caused" naming only M1. That is true of
  the graded configuration and I am not calling it an error; but a reader of that line cannot
  learn that a one-word scheme change reintroduces a same-component flip through a different
  defect, which is the fact that bears on whether the patch is sufficient for the family.

---

# 2. A6 — the CRM case. The primal is sound; three published statements about it are not

**Naming hazard, honoured throughout.** `A6` names two different objects in this archive
(`docs/PRODUCT_LIST.md:3142`): a NASA-hump sub-LU adjoint run, and the CRM wing-alone case.
**Everything in this section is the CRM wing-alone object** at
`/home/ubuntu/certonomous-runs/A6-crm-wing/`. No hump evidence is mixed in.

## 2.1 The symptom — and the first finding is that the framing is wrong

There is no CRM primal failure. `run_model_run1.log` runs to completion:

```
Time = 1000
...
CD: 0.02090143421526141 final: 0.02090143421526141
CL: 0.5000146055201552 final: 0.5000146055201552
ExecutionTime = 403.99 s  ClockTime = 404 s

End
```
(`/home/ubuntu/certonomous-runs/A6-crm-wing/run_model_run1.log:875-892`)

No `FOAM FATAL`, no SEGV, no PETSc error, no OOM in that log; the only `Floating point
exception` string is `trapFpe: Floating point exception trapping enabled` at line 31, a
startup banner. The last processor time directory is `1000`, matching `endTime 1000` in
`system/controlDict`.

**There is a crash in the A6 archive, and it is a different run.** `run_model_run2.log` ends in
`PETSC ERROR: Caught signal number 11 SEGV` on three ranks and `MPI_ABORT … errorcode 59`. Per
Supervision Charter §3 check 2 it is guilty until shown to be a mere bug — and it is showable,
from its own first error at `run_model_run2.log:47`:

```
--> FOAM FATAL ERROR: (openfoam-2506)
Case is already decomposed with 4 domains…
```

after which the run **proceeded anyway** from `Create mesh for time = 250` and every rank hit
`cannot find file ".../processorN/250/p"` and `Istream not OK for reading dictionary` — a
restart against a truncated checkpoint. The SEGV is the downstream consequence of reading a
half-written field, not an independent numerical event. **This is the identical defect class
the A1 ladder record already named as its own Lesson**
(`ladder-a/A1_naca0012_incompressible.md`: *"must not be launched into a case directory that
still holds `processorN/` state from a previous container invocation"*). The mechanism has a
name and a prior instance; it is not an unexplained crash. Not a finding about the CRM
physics.

## 2.2 Statement 1: "CONVERGED below 1e-8" — the claim reads the wrong column

`runScript.py:36` requests `"primalMinResTol": 1.0e-8`. DAFoam enforces that by printing a
line and terminating early. Positive control, from a case where it fires
(`W5-regrade/a1_unpatched_stock.log:2723-2724`):

```
Time = 218
Minimal residual 9.917819850026459e-09 satisfied the prescribed tolerance 1e-08
```

`/usr/bin/grep -n "satisfied the prescribed tolerance\|Minimal residual"` over
`A6-crm-wing/run_model_run1.log` returns **nothing** (exit 1). The same grep returns **21**
hits in `a1_unpatched_stock.log`. **A6 never triggered its own convergence test.** It stopped
because it reached `endTime = 1000`.

The residuals it stopped at, verbatim (`run_model_run1.log:877-884`):

```
U0 initRes: 2.329009005138466e-08   finalRes: 1.742194091036054e-09
U1 initRes: 3.004163067026288e-08   finalRes: 1.823763983190351e-09
U2 initRes: 2.380868760913451e-08   finalRes: 1.53927642199333e-09
he initRes: 4.658548854958758e-08   finalRes: 3.552058518763733e-09
p  initRes: 1.009350711521818e-07   finalRes: 9.878745080529403e-09
nuTilda initRes: 1.181681057385885e-07 finalRes: 7.485783071701252e-09
```

`ladder-a/A6_crm_wingbody.md:120-124` reads the **`finalRes`** column and concludes *"All six
field `finalRes` values at t=1000 are below 1e-8 … this satisfies `primalMinResTol=1e-8` on
every field"*. `finalRes` is the inner linear solver's own residual after its 2–9 iterations
for that one outer step; it is bounded by the linear solver's tolerance regardless of whether
the outer SIMPLE loop has converged. The quantity `primalMinResTol` gates is the **initial**
residual, which at t=1000 stands at **1.18e-7**, twelve times the requested tolerance.

That the gated quantity is the initial residual is inferred behaviourally, not read from
DAFoam source (no DAFoam source exists on this host — `find / -name DASolver.C` returns
nothing): at `a1_unpatched_stock.log:2708-2716`, `Time = 200`, the *smallest* initial residual
is already 1.43e-10 and the run continues, terminating only at `Time = 218` when the largest
falls to 9.92e-9. The inference is not load-bearing anyway — **the operative fact is the
absence of the line**, which is independent of what quantity the line measures.

**What survives.** The primal is *force-stationary*, which is the honest word and is the word
`NOT_PASSING_REGISTER.md` already adopted for seven other cases in this lab. Over the last
four write points CD moves 0.02090108 → 0.02090261 → 0.02090181 → 0.02090143. It is not
converged to its own stated criterion, and nothing in the log suggests it would not have
continued closing.

## 2.3 Statement 2: "matches the published tutorial to 0.0067%" — below the resolution of both instruments

The reference is DAFoam's own tutorial page, quoted at `ladder-a/A6_crm_wingbody.md:143`:
**"the original CD was 0.02090"**. Four significant figures.

* A four-significant-figure reference resolves agreement to no better than **±0.0239%**
  (half of the last printed digit, 0.000005/0.02090). The claimed 0.0067% is **3.5× finer than
  the number it is compared against can distinguish.**
* Independently, the run's own CD is still moving. Peak-to-peak over the last four write points
  (t = 700, 800, 900, 1000 — window stated) is 1.531e-6, i.e. **0.00732% of CD** — larger than
  the 0.00686% deviation being claimed as the agreement.

Two independent instruments, both coarser than the figure. **The correct statement is that A6
reproduces the published tutorial baseline to within the reference's own precision** — which is
a real and creditable result, and is what the case actually earned. `0.0067%` should not be
quoted.

## 2.4 Statement 3: the "~8.5e8 temperature-residual signature" — refuted by the archive, three ways

The claim (`docs/PRODUCT_LIST.md:192`) is *"temperature-residual ~8.5e8 signature (same
precursor as A4's field collapse) filed open"*. Source, appearing exactly once in the run
(`run_model_run1.log:894-910`):

```
Printing Primal Residual Statistics.
U Residual Norm2: (9825746.041633999 4157172.438707694 6532035.818793524)
p Residual Norm2: 263303.8258586535
T Residual Norm2: 850899542.2772245
nuTilda Residual Norm2: 17006.32299935754
phi Residual Norm2: 64.3969501231297
Total Residual Norm2: 850991536.6944678
```

**(a) The statistic is un-normalized, so it ranks fields by physical units, not by health.**
Frame L-stat (301 of 595 logs). Reading four of them:

| case | solver | `T Residual Norm2` | `U Residual Norm2` (x) | T as % of Total |
|---|---|---|---|---|
| **A6 CRM wing** | `DARhoSimpleCFoam` | **8.509e8** | 9.826e6 | 99.99% |
| A3 ONERA M6, n28 | `DARhoSimpleCFoam` | **5.914e8** | 9.458e6 | 99.99% |
| A2 MACH wing | `DARhoSimpleFoam` | 2.611e5 | 3.356e4 | 99.1% |
| A5 U-bend | `DASimpleFoam` | 41.16 | 25.55 | 73.8% |

Sources: `A3-onera-m6-sweep-n28_42120/run_opt5_onera_n28_42120.log:803-818`;
`W4-a2-provenance/a2_ct_simple.log:900-915`;
`W4-repro-fromscratch/repro_ubend_pressure-loss_real_np4.log:851-866`.

The A3 ONERA M6 row is the discriminator, and it was sitting unread. That case's primal is
graded **DONE and validated** (CD = 0.02299556, Cp against AGARD AR-138,
`docs/PRODUCT_LIST.md:176-179`). It is the same solver on the same class of transonic wing,
and it reads 5.91e8 — the same order of magnitude, with T at the same 99.99% of Total. A6's
8.5e8 is 1.44× a number the lab already accepts as healthy.

**(b) "One raw residual dominating the Total" is what every one of these logs does**, including
the two the lab grades as good. It is a property of the units of the dominating state (T ~ 300 K
with energy-equation scaling; ω ~ 1e3–1e5 s⁻¹ on the incompressible Ahmed body), not a
property of convergence. It carries no diagnostic content.

**(c) A4 — the case the "same precursor" points at — has no temperature residual at all.** A4
is `DASimpleFoam` (`W5-regrade/a4_stock_checktotals.log:344`), incompressible. Its
residual-statistics block (`:4258-4274`) prints `U`, `p`, `omega`, `k`, `phi`, `Total` — and
**no `T` line**; `/usr/bin/grep -c "T Residual Norm2"` on that log returns 0. A4's collapse was
in **omega** (`omega Residual Norm2: 1848.2911` of `Total 1848.3467`). The two phenomena share
a *shape* — a dominant raw residual beside a stable headline — and that shape is generic per
(b).

## 2.5 And the trace the register said could not be done is in the log

`demo-output/website/campaign/NOT_PASSING_REGISTER.md:616-619` files the item and states the
obstacle: *"this solver's log does not print per-field Initial-vs-Final residuals in the same
format used to trace A4's collapse, so the trend behind the raw statistic could not be checked
line by line"*, and asks: *"Trace T's per-iteration Initial residual across the run … to
determine whether it decays, plateaus honestly, or collapses to a falsely-reassuring fixed
value."*

**It prints them, at every one of the 11 write steps, and the format is identical to A4's.**
A4: `omega initRes: 0.23098657 finalRes: 0.017151049 nIters: 3`
(`W5-regrade/a4_stock_checktotals.log:670`). A6: `he initRes: … finalRes: … nIters: …`. The
obstacle was the **field name**, not the format: the end-of-run statistic names the derived
state `T`, while the per-iteration line names the solved energy variable `he`. A grep for
`T initRes` returns nothing and the item was filed as untraceable.

The trace, `/usr/bin/grep -n "^he initRes" run_model_run1.log`:

| t | 1 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 1000 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `he initRes` | 1.000 | 3.096e-3 | 1.635e-3 | 3.244e-4 | 1.166e-4 | 3.209e-5 | 7.690e-6 | 2.073e-6 | 6.514e-7 | 1.555e-7 | 4.659e-8 |

**Strictly decreasing at every one of the ten steps, 7.33 decades in total, still falling by
3.3× per 100 iterations at the last step.** No plateau, no collapse to a fixed value, no growth.

For contrast, at the same instrument, A4's omega at its last three write points:
`0.0027840578`, `0.0027595544`, `0.0027173750` — flat at ~2.7e-3, per-step ratio ≈ 1.00
(`W5-regrade/a4_stock_checktotals.log:10162, 10879, 11596`). **That** is the
collapse-to-a-fixed-value signature the register was looking for, and A6 is its opposite.

The register's own resolution condition is met. The item is closable at **zero core-min**, and
the CD number's "provisional" tag can come off for this reason (the convergence and precision
findings of §2.2 and §2.3 are separate and stand).

## 2.6 What the A6 record does not decide

* **"Adjoint not attempted (memory wall)" is an unmeasured attribution.** Both A6 logs are
  `-task run_model`; the adjoint branch in `runScript.py` was configured and never entered.
  A6's own record states *"No host memory distress occurred at any point in this sequence
  (`MemAvailable` stayed >29 GB throughout); the failure was pure process management, not a
  resource wall"* (`ladder-a/A6_crm_wingbody.md:84-86`), and `DAFOAM_CASE_STATUS.md:275` says
  A6 *"was consequently never attempted for the same structural reason"* — the reason being
  A3's. **The wall is projected from a different case at a different mesh size, not measured on
  A6.** It may well be right; it is not a measurement, and the product-list phrasing reads as
  one.
* **The T-residual has no per-iteration trace of its own.** §2.5 traces `he`, the solved
  energy variable. `T` is derived from `he` through the `hePsiThermo`/`perfectGas` model each
  pass. That the energy equation's residual decays monotonically is strong evidence the
  temperature field is not diverging, but it is one step of inference, and I am naming it.
* **37 `act9-crm_wingbody-*` directories carry final-state fields at t=1000 and no log of any
  kind.** They share A6's byte-identical `runScript.py`. Nothing about them can be verified —
  they can neither corroborate nor contradict anything here. Filed as **D39**.

---

# 3. A5 — the internal-flow adjoint. Diagnosed to a link in the chain by bisection

## 3.1 The symptom, quoted

A5 is the DAFoam `UBend_Channel` tutorial reconfigured to a pure pressure-loss objective
`OBJ.val = TP1 − TP2` (total pressure at `inlet` minus at `outlet`), 4,800 cells,
`DASimpleFoam`, incompressible SA, 27 `shapexUpper` design variables. From
`W5-regrade/a5pl_stock_checktotals.log`, reproducing the published table to every digit of all
three columns:

```
  Full Model: 'OBJ.val' wrt 'shapexUpper'
    Analytic Magnitude: 1.938364e+01
          Fd Magnitude: 3.340851e+01 (fd:central)
    Relative Error (Jan - Jfd) / Jfd : 4.663773e-01 *
```

**46.6377% aggregate, with exactly two sign flips**, idx8 and idx17:

| idx | analytic | FD | rel. err | sign |
|---|---|---|---|---|
| **8** | **−8.43372580e-01** | **+7.87898342e-01** | **207.0%** | **FLIPPED** |
| **17** | **−6.28812054e-01** | **+2.91315567e+00** | **121.6%** | **FLIPPED** |

(`ROOTCAUSE_getRotationMatrix3d.md` §4.4; `ladder-a/A5_ubend_internal.md:159`.)

**This is a magnitude-plus-sign failure of a converged run, not a crash and not a
non-convergence.** The primal converges cleanly in every A5 log; the objective is stationary
to 2.8e-12 over four identical re-solves.

## 3.2 The archives bisect the chain, and this is the strongest evidence in the A5 file

A5's gradient chain is `shape → (DVGeo/FFD) → Xs → (IDWarp warpDeriv) → Xv → (CFD adjoint) →
OBJ`. **Three in-repo logs measure each link separately, and two of the three links are
exonerated by executed checks rather than by argument.**

**Link 1, DVGeo/FFD (`dXs/dShape`) — exact.** `a5_dobjdxv_np1_run1.log:768-773`:
```
A5DXSDSHAPE idx=8  h=1.0e-04 max_abs_diff=1.085365e-12 max_rel=3.315425e-12
A5DXSDSHAPE idx=17 h=1.0e-04 max_abs_diff=1.047984e-12 max_rel=3.201237e-12
A5DXSDSHAPE idx=2  h=1.0e-04 max_abs_diff=9.063791e-13 max_rel=2.788343e-12
```
The FFD Jacobian agrees with its own finite difference to 3e-12 at all three probed
components, at two step sizes. Nothing upstream of the warp is broken.

**Link 3, the CFD adjoint with the warp bypassed — the flip disappears.**
`a5_noisefloor_np1_run1.log:2512` and `a5_dobjdxv_np1_run1.log:1366,1761` perturb the *volume*
coordinates directly through `setVolCoords`, so `warpDeriv` is never called:
```
A5DOBJDXV_RESULT idx=8 h=1.0e-04 AN=7.870912446398e-01 FD=7.940838366238e-01
                 rel_err=8.805861e-03 sign=agree framework_dOBJdshape=-8.445468952456e-01
A5DOBJDXV_RESULT idx=8 h=5.0e-05 AN=7.870927461098e-01 FD=7.884141547976e-01
                 rel_err=1.676034e-03 sign=agree framework_dOBJdshape=-8.445468952456e-01
```
With the warp out of the loop, analytic and FD **agree in sign** and to 0.88% at h=1e-4,
tightening to **0.168% when the step is halved** — the residual behaves like FD truncation, not
like a defect. The framework's own full-chain analytic for the same component is
`−0.8445`.

**Four instruments at idx8, and three of them agree:**

| instrument | idx8 value | source | routes through `warpDeriv`? |
|---|---|---|---|
| framework FD (`check_totals`) | **+0.78391094** | `a5pl_stock_checktotals.log:13570` | no — it perturbs the shape and re-solves |
| direct-`Xv` FD, warp bypassed | **+0.79408384** | `a5_noisefloor_np1_run1.log:2512` | no |
| direct-`Xv` analytic, warp bypassed | **+0.78709124** | `a5_noisefloor_np1_run1.log:2512` | no |
| **framework analytic (`check_totals`)** | **−0.84337258** | `a5pl_stock_checktotals.log:13562` | **yes** |

The outlier is the one path that crosses the warp. This is a bisection, not an analogy, and it
kills for A5 — by direct measurement rather than by transfer from A1 — the adjoint boundary
condition, the residual/transpose convention, and the objective's patch handling: all of those
live in the link that reads 0.17%.

**Stated against the bisection: it is clean at idx8 and it is not clean everywhere.** The same
probe at the other two components it covers (`a5_dobjdxv_np1_run1.log:2156, 2551, 2946, 3341`)
reads idx17 at 0.67% for h=1e-4 but **56.7%** at h=5e-5, and idx2 at 390% then 268% with the
sign flipping between the two steps. The probe perturbs the volume mesh directly, and
`||delta_Xv||` is 2.6–3.1 — a large perturbation whose direct-`Xv` finite difference is plainly
leaving its linear regime at those components. **So the bisection is decisive at idx8 and
inconclusive at idx2 and idx17**, and I am not extending it beyond the component where its own
step-refinement behaves. idx8 is the flagship flip and it is enough to carry the localisation;
it is not enough to characterise the whole vector, which is what P-4 in §5 would buy.

**The FD instrument itself is exonerated by an executed noise-floor control**
(`a5_noisefloor_np1_run1.log:2116-2117`):
```
A5NOISEFLOOR n=4 vals=[52.345227439913 52.345227439915 52.345227439912 52.345227439914]
             spread_max_min=2.849276e-12
A5NOISEFLOOR implied_FD_noise h=1.0e-04 = 1.424638e-08 (spread/(2h))
```
An implied FD noise of 1.4e-8 against a disagreement of order 1 — eight decades of margin. Two
of A1's dead candidates (FD noise; the primal plateau) are closed here quantitatively.

## 3.3 Ranked mechanisms for A5

| # | mechanism | evidence for | killing evidence — **executed** |
|---|---|---|---|
| 1 | **IDWarp degenerate-rotation guard (M1)** — the same line as A1 | the bisection above localises to the warp link; rotations-OFF sends all 27 components to `0.0000` while the analytic vector is bit-identical; the patched full chain reads 2.2372% with **0 flips, 26/27 in band** | would have died if the analytic had moved when rotations were switched off (`||dXs||` identical to 16 digits at the baseline, `1.495168856286067e+03`, both runs) — it did not |
| 2 | **A1's "combination-mode" sub-hypothesis** — that the defect needs opposing-direction FFD modes | it was the original upstream-report framing | **DEAD.** A5's DVs are built one `PointSelect("list", …)` + one `nom_addLocalDV(axis=…)` at a time — **single-point, single-axis**, no combination construction anywhere in `runScript.py:179-212`. `ROOTCAUSE_getRotationMatrix3d.md:8` says so explicitly, and this is what forced the narrowing to the degenerate branch. |
| 3 | **KD-tree fast-sum truncation** (the two passes truncating differently) | a genuine documented approximation, `errTol=5e-4` | **DEAD.** `evalMode="exact"` — no truncation at all — leaves idx8 at 204.7% and idx17 at 123.8% (`ROOTCAUSE` §4.6, D3). Independently dead because rotations-off collapses the error while `evalMode` is still `fast`. |
| 4 | **Slope-limiter AD tape (A1's M2)** | it is a proven live defect in this stack | **DEAD.** `W4-a5-decomp/a5_scotch/system/fvSchemes:23-31`, `W5-regrade/a5pl_stock/system/fvSchemes` and `W5-rotation-branch/UBend_Channel/system/fvSchemes` all read `gradSchemes { default Gauss linear; }` and `div(phi,U) bounded Gauss linearUpwindV grad(U)`. No `cellLimited` token exists in any A5 dictionary. (Sound in this direction only — see §1.3 item 5.) |
| 5 | **Mesh decomposition (A4's mechanism)** | A4's 89% was decomposition | **DEAD as the carrier.** `W4-a5-decomp` runs `compute_totals` under scotch and under `simple` 4×1×1 at np=4. idx8: `0.78790074` vs `0.7866546` — **0.158%**; component 0: `0.11581860` vs `0.11644847` — 0.54%. Decomposition moves A5's gradient by a few tenths of a percent and cannot carry 46.6%. |

## 3.4 What the archives do NOT decide about A5, and what is confounded

**(a) The 2.24% that survives the patch is unexplained, and it is 60× A1's residual.**
`a5pl_patched_checktotals.log` reads `Analytic Magnitude: 3.350432e+01` against an unchanged
`Fd Magnitude: 3.340851e+01` — 2.2372%. A1's patched CD/shape sits at 0.03745%, FD-truncation
level. `W5_GRADIENT_REGRADE.md` §4 names this and declines to explain it, correctly. Ranked
candidates for the residual, with what each predicts:

1. **Regime 2** — the ill-conditioned band just above the guard threshold
   (`ROOTCAUSE` §1.6, §7). It survives the patch by construction and is measured at 1.0–1.3% on
   ONERA M6. A5's 2.24% is in that band. **But this is an inference from an error-vs-angle
   curve, not a measurement**: `ROOTCAUSE` §7.6 states against itself that *"no direct
   measurement of normal-tilt-angle distributions on a real case exists here."* Discriminator:
   patched `check_totals` with `useRotations=False`. If the residual is regime 2 it must
   collapse; if it survives, regime 2 is not the carrier.
2. **The CFD-adjoint link's own residual.** The bypass test reads 0.168–0.88% at idx8. That is
   the same order as 2.24% and it is not zero. A share of A5's post-patch residual may not be
   in IDWarp at all. Discriminator: the same bypass probe run across all 27 components rather
   than three.
3. **Decomposition.** Bounded above at ~0.5% by §3.3 row 5, so it can be a contributor but not
   the carrier.

**(b) The decomposition-invariance test was run on the PATCHED stack.** `W4-a5-decomp/run.sh:28`
sets `export PYTHONPATH=/patch/idwarp:$PYTHONPATH`. So it demonstrates decomposition-invariance
of the **corrected** gradient, not of the stock one. The product-list claim "A1/A2/A5
decomposition-invariant" is carried for A1 by a stock-stack measurement and for A5 by a patched
one. I have no reason to expect the stock branch to couple across processors — it is a local
per-node geometric test — but the measurement that is cited does not cover the case it is cited
for, and that should be said rather than assumed.

**(c) Two different probes are quoted as one finding.** `docs/PRODUCT_LIST.md:188-190` reads
*"solve-free pure-geometry test reproduces idx8 207% flip component-by-component; standalone
stock reproducer: 13/27 components >30%"*. These are two artifacts with **different contraction
seeds**:
* the 207% flip is `a5_realseed_np4_run1.log`, contracting with the **real captured
  `d(OBJ)/dXv`** seed;
* the 13/27 is `W4-repro-fromscratch/repro_ubend_stock_real_np4.log`, contracting with a
  **per-DV one-hot** direction under the *stock* objective, and its own summary line reads
  `REPRO_SUMMARY … sign_flips=0`.

Both are legitimate and both implicate the same code path, but **the 13/27 table contains no
sign flip**, and a reader of that sentence would reasonably think it did. This is a precision
defect in the summary, not a wrong number.

**(d) The seed was itself a dead lever once, and the record shows it.** `DAFOAM_CASE_STATUS.md`
ruled A5 **out** of A1's mechanism on 2026-07-29 on a **random-seed** `warpDeriv` probe that
showed idx8/idx17 agreeing to 0.32–1.30% with no flip, then retracted that on 2026-07-31 once
the real seed was used. That is the same trap that hid the defect from upstream for five years:
`UnstructuredMesh.py:460`'s `verifyWarpDeriv(…, randomSeed=314)`. **The lever that was inert was
the seed** — the instrument reported clean because it was pointed in a direction the defect does
not live in. It is an L-40 instance in an unusual place (the probe direction, not a switch), and
it is worth naming as one, because the natural reading of "we tested it and it was clean" was
wrong for two days.

## 3.5 Verdict on A5

**Diagnosed, and better supported than A1's, because A5's chain was bisected rather than
argued.** The FAIL against the shipped toolchain holds at 46.64% and is attributed to
IDWarp 2.6.2's degenerate-rotation guard; the corrected derivative takes it to 2.24% with zero
sign flips. The residual 2.24% is genuinely open, has three ranked candidates and a
discriminator for each, and should not be described as root-caused.

---

# 4. Cross-cutting: what could not be established, stated plainly

* **A6's "memory wall" cannot be diagnosed from this archive, because the run that would show
  it was never made.** Both A6 logs are `-task run_model`; the adjoint was configured and never
  entered. A6's own record measures the opposite for the primal (`MemAvailable` >29 GB
  throughout). The classification is inherited from A3 at a different mesh size. This is a
  records finding: **there is no A6 adjoint log to read, and the product list states the
  conclusion of one.** Executed: across `A6-crm-wing/` and all 37 `act9-crm_wingbody-*`
  directories there are **4 `*.log` files in total** (all four in `A6-crm-wing/`), and
  `/usr/bin/grep -l "Solving the adjoint\|adjoint equation\|dRdWTPsi\|Main iteration.*KSP
  Residual"` matches **0** of them. **Positive control:** the same pattern returns 2 hits in
  `a5_dobjdxv_np1_run1.log`, a log that does contain an adjoint solve — the search finds an
  adjoint when one is there.
* **37 `act9-crm_wingbody-*` directories hold final-state fields at t=1000 and no log of any
  kind.** Byte-identical `runScript.py` to A6's. Nothing about them is checkable. → **D39**.
* **`ROOTCAUSE` §4.7's P6 (reordering) is confounded** by the dead `jacMatReOrdering rcm`
  lever and should be relabelled rather than relied on (§1.4). → **D40**.
* **No DAFoam source exists on this host** (`find / -name "DASolver.C"` → nothing;
  `find /home/ubuntu -name pyDAFoam.py` → nothing), so the definition of DAFoam's `Minimal
  residual` is inferred behaviourally in §2.2 rather than read. The §2.2 conclusion does not
  depend on it.
* **The IDWarp reference paper (Secco et al., AIAA J. 59(4), doi 10.2514/1.J059491) remains
  unread**, so the "undocumented approximation" framing rests on code, docs and release notes
  only. Unchanged by this session; tracked at `agenda/BLOCKERS.md` B-5.

---

# 5. The cheapest measurements that would settle the rest — priced, and NOT run

Every price below is built from a **measured** wall time in this archive, cited. Nothing here
was executed; all of it is a request for Katie's authorisation.

| # | measurement | what it settles | price | basis |
|---|---|---|---|---|
| **P-1** | Patched A5 pressure-loss `check_totals`, one arm, `useRotations=False` | Whether A5's surviving **2.24%** is regime 2. Collapse ⇒ regime 2 is the carrier; survival ⇒ it is not, and candidate 2 (the CFD-adjoint link) moves to rank 1. This is the single highest-value open question in the family. | **~16 core-min** | `W5_GRADIENT_REGRADE.md` §0: the a5pl stock+patched **pair** measured 235 s + 250 s at 4 ranks = 32.3 core-min (contended). One arm is half. |
| **P-2** | A6 restart from the existing `processor*/1000` fields to `endTime 1250`, unchanged otherwise | Whether A6's primal reaches its own `primalMinResTol=1e-8` and whether CD is unchanged when it does. Converts "force-stationary" to "converged" or exposes a plateau. Also re-verifies CD at a genuinely converged state, which is what the 0.0067% claim needed and never had. | **~7 core-min** | `run_model_run1.log:891` `ExecutionTime = 403.99 s` for 1000 iterations at np=4 → 26.9 core-min/1000 iters; the observed 3.3×-per-100-iterations decay puts the crossing ~250 iterations out. |
| **P-3** | `-ksp_view` readback on two arms of the existing hump rung-4 configuration, one `natural`, one `rcm` | `docs/DEAD_LEVER_AUDIT.md` M-A, unchanged. Settles at the **class** level whether DAFoam's `jacMatReOrdering` key reaches PETSc — 257 archived runs inherit the answer, and A5's P6 (§1.4) is one of them. | **~8 core-min** | already priced in `DEAD_LEVER_AUDIT.md` M-A from `hump_adjoint_run1.log:2268`; not re-derived here. |
| **P-4** | The `A5DOBJDXV` warp-bypass probe extended from 3 components to all 27, np=1 | Bounds how much of A5's 2.24% lives outside IDWarp. Complements P-1: together they partition the residual. | **~25 core-min** | `a5_dobjdxv_np1_run1.log` covers 3 components × 2 steps in one np=1 session; 27 components at one step is ~4.5× that work. Coarse — this is the least well-based number in the table and should be re-scoped before it is bought. |
| **P-5** | Operator-level cross-residual on A1 **serial** with the limiter, the A4 instrument applied to M2 | Whether M2 is an operator defect (like A4's) or an FD-visible tape inconsistency only. M2 is currently established at gradient level and one-sided-slope level, not operator level, in serial. | **~2 core-min** | `ledger_r7.txt`: `a1lim_np1` was 192 s at `cpus_cap=2` = 6.4 core-min for a full 17-primal `check_totals`; an operator probe needs one adjoint, not 17 primals. |

**And one thing no run can buy.** A6's "matches the published tutorial baseline to 0.0067%"
cannot be rescued by any measurement, because the limit is the *reference*: DAFoam's tutorial
page publishes `0.02090`, four significant figures, resolving agreement to ±0.0239%. **No
amount of compute on our side makes a four-significant-figure reference into a
five-significant-figure one.** The fix is documentary, it is free, and it is in §2.3.

---

# 6. Summary table

| | graded symptom | mechanism | status | what is still open |
|---|---|---|---|---|
| **A1** | `CD wrt shape` 11.43%, **idx6 sign flip** (`+0.00569076` vs FD `−0.00105334`) | IDWarp 2.6.2 degenerate-rotation guard (**M1**) | **root-caused**; 7 classical sign-flip causes eliminated on the record incl. `forceMeshWaveFrozen`; patched reads 0.03745% with primal and FD bit-identical | P6 reordering check confounded (D40); ladder record still names the refuted candidate; **M2** (limiter tape, same component, patch-independent) is a second defect whose cure moves the primal by 2.7% |
| **A5** | `OBJ.val wrt shapexUpper` 46.64%, **idx8 + idx17 flips** | same **M1** line | **root-caused, and bisected**: FFD link exact to 3e-12, CFD-adjoint link agrees in sign to 0.17% with the warp bypassed, only the warp-crossing path is the outlier | the **2.24%** surviving the patch — 3 ranked candidates, discriminator P-1; decomposition-invariance cited from a patched-stack run |
| **A6** | *no primal failure*; CD `0.02090143421526141` at `Time = 1000`, clean exit | n/a — the crash in the archive is `run_model_run2`, a restart against a truncated checkpoint, a named defect class with a prior instance in A1's own Lesson | **three published statements corrected from the archive at zero cost**: never reached `primalMinResTol` (no `satisfied the prescribed tolerance` line, positive control 21 hits in A1); 0.0067% is below both instruments' resolution; the T-residual "signature" is a units artifact that a validated ONERA M6 run shows at 5.9e8, and A4 — the "same precursor" — has no T residual at all | the "memory wall": no A6 adjoint was ever attempted, so the log that would settle it does not exist |
