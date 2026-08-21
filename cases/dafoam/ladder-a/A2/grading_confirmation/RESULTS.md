# A2 MACH Tutorial Wing — grading confirmation (NO COMPUTE)

**2026-08-21, Lane A. Zero solver core-minutes: no container was started, no solve was run.** Every
number below is read out of a log already on disk, at the line number given. Nothing filed upstream.

**Grading band, cited not invented** (`../../A_stepsize_study.md:91-93`):

> Bands: **PASS ≤5%** with zero flagged components; **CONDITIONAL 5-15%**, requires a per-component
> breakdown before grading; **>15% or any flagged component → FAIL pending investigation**, regardless
> of the aggregate percentage.

A component is "flagged" when its FD value **changes sign** or **moves by >50% of its own magnitude
across one decade of step** (`../../A_stepsize_study.md:86-87`). The metric throughout is OpenMDAO's
vector-relative error `‖Jan − Jfd‖ / ‖Jfd‖` over the whole design-variable group.

**Case identity.** 38,304 cells, `DARhoSimpleFoam` (compressible RANS, Spalart–Allmaras), np=4,
`runScript_AeroOnly.py`, `check_totals` central FD `step=1e-3 step_calc=abs`, 105 design variables
(96 shape + 7 twist + 2 patchV) = 210 primal re-solves per pass
(`../../A2_mach_tutorial_wing.md:7`, §4).

---

## 1. The six graded derivative rows — SHIPPED toolchain

Source: `/home/ubuntu/certonomous-runs/A2-mach-wing/check_totals_run1.log` (52,940 lines),
the accepted 2026-07-28 run.

| # | derivative | analytic | FD (central) | rel. error | % | log line | verdict |
|---|---|---|---|---|---|---|---|
| 1 | `CD` wrt `dvs.patchV` | 5.615356e-03 | 5.616540e-03 | 2.122454e-04 | **0.0212%** | `:49498-49503` | **PASS** |
| 2 | `CD` wrt `dvs.shape` (96) | 4.801625e-02 | 4.858158e-02 | 1.713791e-02 | **1.714%** | `:49513-49518` | **PASS** |
| 3 | `CD` wrt `dvs.twist` (7) | 1.922238e-03 | 1.922103e-03 | 3.890805e-03 | **0.389%** | `:49719-49724` | **PASS** |
| 4 | `CL` wrt `dvs.patchV` | 7.040571e-02 | 7.040500e-02 | 1.450798e-05 | **0.00145%** | `:49736-49741` | **PASS** |
| 5 | `CL` wrt `dvs.shape` (96) | 8.480582e-01 | 8.572992e-01 | 1.165163e-02 | **1.165%** | `:49751-49756` | **PASS** |
| 6 | `CL` wrt `dvs.twist` (7) | 2.371825e-02 | 2.398459e-02 | 1.120617e-02 | **1.121%** | `:49882-49887` | **PASS** |

All six are ≤5% and **no component is flagged** — the record reports no sign flip anywhere in A2, at
either toolchain. **Row 4's percentage differs trivially from the frozen record**, which prints
0.0015%: the exact fraction is 1.450798e-05 = 0.001451%. Rounding, not a discrepancy; recorded so a
later reader does not treat it as one.

### The twelve constraint rows that complete the 18

| derivative | analytic | FD | rel. error | log line | reading |
|---|---|---|---|---|---|
| `geometry.thickcon` wrt `dvs.shape` | 9.718825e+00 | 9.718825e+00 | 9.553846e-13 | `:48522-48527` | machine precision |
| `geometry.volcon` wrt `dvs.shape` | 3.357042e-01 | 3.357042e-01 | 3.532922e-12 | `:49244-49249` | machine precision |
| `geometry.volcon` wrt `dvs.twist` | 2.722885e-08 | 2.722884e-08 | 1.268973e-05 | `:49481-49486` | 0.0013% |
| `geometry.lecon` wrt `dvs.shape` | 4.000000e+00 | 4.000000e+00 | 0.000000e+00 | `:48036-48041` | exact (linear constraint) |
| `geometry.tecon` wrt `dvs.shape` | 4.000000e+00 | 4.000000e+00 | 0.000000e+00 | `:48187-48192` | exact (linear constraint) |
| `geometry.thickcon` wrt `dvs.twist` | 4.127369e-15 | 3.351352e-12 | 1.000034e+00 | `:48561-48566` | **NOT A RESULT** — both sides are noise-floor zeros; the "100%" is a ratio of two numbers indistinguishable from zero. Thickness genuinely does not depend on twist in this parameterisation |
| six further rows (`lecon`/`tecon`/`thickcon`/`volcon` wrt `patchV` and `twist`) | 0.000000e+00 | 0.000000e+00 | `nan` (0/0) | `:48007`, `:48129`, `:48158`, `:48280`, `:48309`, `:49229` | **NOT A RESULT** — structural zeros |

The machine-precision constraint rows are load-bearing: they traverse the identical FFD/DVGeo
Jacobian chain as the CD/CL shape rows but never touch the CFD solve, so they establish that the
harness — the FFD chain, the `check_totals` machinery, the DV indexing — is sound. A large number in
rows 2 or 5 therefore cannot be dismissed as a broken rig.

---

## 2. The re-measurement, and the retraction it forced

`W5_GRADIENT_REGRADE.md` §3a originally concluded that **"A2 could not be regraded, because its
published verification is no longer reproducible on this box."** That section is **RETRACTED in
place** (2026-08-02). The cause was in the harness, not the case: `run_a2_checktotals.sh`,
`run_a2_rebuild.sh` and `run_a2_twist.sh` all invoked `python runScript.py` — the tutorial's
**aerostructural** script (TACS `TacsBuilder` + FUNtoFEM `MeldBuilder`, `ScenarioAeroStructural`, a
*flexible* wing at `aoa0 = 4.65`) — where the published numbers were measured with
`runScript_AeroOnly.py` (`ScenarioAerodynamic`, `aoa0 = 4.0`). The aerostructural path is confirmed
to have executed from that session's own log: `a2_rebuilt_runmodel.log:688` reads
`Transfer scheme [0]: Creating scheme of type MELD...`.

**Run correctly, A2 reproduces exactly.** Source:
`/home/ubuntu/certonomous-runs/W4-a2-provenance/a2_ao_stock_checktotals.log`.

| derivative | published (`A2-mach-wing/check_totals_run1.log`) | re-measured stock (`a2_ao_stock_checktotals.log`) | identical? |
|---|---|---|---|
| `CD` wrt `patchV` | 2.122454e-04 `:49498` | 2.122454e-04 `:51676` | **yes, every digit** |
| `CD` wrt `shape` | 1.713791e-02 `:49513` | 1.713791e-02 `:51691` | **yes** |
| `CD` wrt `twist` | 3.890805e-03 `:49719` | 3.890805e-03 `:51836` | **yes** |
| `CL` wrt `patchV` | 1.450798e-05 `:49736` | 1.450798e-05 `:51853` | **yes** |
| `CL` wrt `shape` | 1.165163e-02 `:49751` | 1.165163e-02 `:51868` | **yes** |
| `CL` wrt `twist` | 1.120617e-02 `:49882` | 1.120617e-02 `:52247` | **yes** |
| all 12 constraint rows | see §1 | identical at every printed digit | **yes** |

**18 of 18 rows identical to every printed digit** — analytic magnitude, FD magnitude and both of
OpenMDAO's error norms. Independently re-extracted for this document with a fresh parser.

---

## 3. Verdict rows — SHIPPED and PATCHED kept separate

PATCHED = the same stock image with the IDWarp rotation fix bind-mounted on `PYTHONPATH`; source
`/home/ubuntu/certonomous-runs/W4-a2-provenance/a2_ao_patched_checktotals.log`. **The FD column is
identical between the two halves on all 18 rows**, which is the control that makes the comparison
readable — the patch touches derivative code only, so the primal and therefore the finite difference
cannot move.

| row | arm | image / toolchain | analytic | FD | % | log line | verdict |
|---|---|---|---|---|---|---|---|
| `CD`/`patchV` | SHIPPED | `dafoam/opt-packages:latest` | 5.615356e-03 | 5.616540e-03 | 0.0212% | stock `:51676` | **PASS** |
| `CD`/`patchV` | PATCHED | stock + patched IDWarp | 5.615356e-03 | 5.616540e-03 | 0.0212% | patched `:51880` | **PASS** (bit-identical — does not cross the warp) |
| `CD`/`shape` | SHIPPED | `dafoam/opt-packages:latest` | 4.801625e-02 | 4.858158e-02 | **1.714%** | stock `:51691` | **PASS** |
| `CD`/`shape` | PATCHED | stock + patched IDWarp | 4.856968e-02 | 4.858158e-02 | **0.0506%** | patched `:51895` | **PASS** (33.9× tighter) |
| `CD`/`twist` | SHIPPED | `dafoam/opt-packages:latest` | 1.922238e-03 | 1.922103e-03 | **0.389%** | stock `:51836` | **PASS** |
| `CD`/`twist` | PATCHED | stock + patched IDWarp | 1.927847e-03 | 1.922103e-03 | **0.505%** | patched `:52182` | **PASS — but this row DEGRADES under the patch.** The only row in the whole regrade that moves the wrong way. Both ends are deep inside PASS; recorded as the counter-instance it is |
| `CL`/`patchV` | SHIPPED | `dafoam/opt-packages:latest` | 7.040571e-02 | 7.040500e-02 | 0.00145% | stock `:51853` | **PASS** |
| `CL`/`patchV` | PATCHED | stock + patched IDWarp | 7.040571e-02 | 7.040500e-02 | 0.00145% | patched `:52199` | **PASS** (bit-identical) |
| `CL`/`shape` | SHIPPED | `dafoam/opt-packages:latest` | 8.480582e-01 | 8.572992e-01 | **1.165%** | stock `:51868` | **PASS** |
| `CL`/`shape` | PATCHED | stock + patched IDWarp | 8.573170e-01 | 8.572992e-01 | **0.0219%** | patched `:52214` | **PASS** (53.2× tighter) |
| `CL`/`twist` | SHIPPED | `dafoam/opt-packages:latest` | 2.371825e-02 | 2.398459e-02 | **1.121%** | stock `:52247` | **PASS** |
| `CL`/`twist` | PATCHED | stock + patched IDWarp | 2.398291e-02 | 2.398459e-02 | **0.00974%** | patched `:52607` | **PASS** (115.1× tighter) |
| all 12 constraint rows | both | — | unchanged | unchanged | unchanged | — | machine precision / NOT A RESULT, both toolchains |

**Overall: PASS against the shipped toolchain, on all six graded rows, with zero flagged components.
PASS against the patched toolchain as well.**

**The uncomfortable half of that PASS.** A2's shipped rows were **~97–99% rotation defect**. The
factors of 33.9, 53.2 and 115.1 say that what looked like ordinary numerical noise in the 1–2% band
was almost entirely one upstream bug. A2 passed its gate *and* was carrying the defect at nearly
full strength. The band A2 was originally graded against — the retired "1–12% normal for this
problem class" — was, in the regrade's own words, *"not a property of the problem class at all. It
was one upstream bug, measured four times."* The grade is unchanged; the reason it deserved the
grade is not what the record said it was.

---

## 4. The optimisation — a separate row, and it is not a graded result

| row | value | source |
|---|---|---|
| classification | **OPTIMISATION RUN, NOT A RESULT (time-boxed, unconverged)** | — |
| optimiser | IPOPT 3.13.5 via pyOptSparse, MUMPS linear solver, limited-memory BFGS | `../../A2_optimization_history.json`, `optimizer` |
| settings | `tol = 1e-5`, `max_iter = 100` | `.tol`, `.max_iter_setting` |
| major iterations completed | **47 of ~100** | `.major_iterations_completed` |
| converged to optimiser tolerance | **false** | `.converged_to_optimizer_tolerance` |
| convergence statement in log | **null** — *"IPOPT prints no EXIT line and no convergence statement anywhere in `opt_IPOPT.txt`; the table simply stops after iteration 47."* Verified by grep: zero occurrences of `EXIT` | `.convergence_statement_in_log`, `.convergence_statement_note` |
| baseline (IPOPT iter 0, CL-trimmed) | CD = 0.029619634, CL = 0.499999958 | `.baseline` |
| final evaluated (iter 47) | CD = 0.021244538, CL = 0.499985632, `inf_pr` = 1.44e-05, `inf_du` = 9.0e-05 | `.final` |
| drag reduction | **28.275488%**, basis `(0.029619634 − 0.021244538)/0.029619634`, both points at CL = 0.5 | `.drag_reduction_pct`, `.drag_reduction_basis` |
| time box | 60 min, started 2026-07-28T03:26:19Z, last write 04:26:19Z, elapsed 3600 s | `.time_box_evidence` |
| cost | 3606 s × 4 ranks = **240.40 core-min** = $0.206 at $0.0513/core-hour | `../../A2_mach_tutorial_wing.md` §6 |
| provenance of the extraction | `opt_IPOPT.txt`, sha256 `638504c1c412ee5254e1d90b7967764c3f6461a70d339f735fb6f9f039011036`, 6,546 bytes, plus the pyoptsparse history DB | `._primary_sources` |

**Why this is not a result.** First-order metrics sit an order of magnitude above their own
tolerance (`inf_pr` 1.44e-05 and `inf_du` 9.0e-05 against 1e-5), IPOPT emitted no termination
statement, and the run stopped because a wall clock ran out. It is a genuine 47-iteration
optimisation trajectory and a real 28.3% drag reduction *at the point where the clock stopped*; it
is not a converged optimum and must never be quoted as one.

**And it destroyed its own case directory.** The IPOPT run left the mesh deformed in
`/home/ubuntu/certonomous-runs/A2-mach-wing/`, so that directory's baseline now reads
CD = 0.03142017502 against the published 0.02772949388; a `preProcessing.sh` mesh rebuild lands at
0.02964132667, still 6.9% off, because the preserved `runScript.py` carries the CL-trimmed angle of
attack. Finding that out cost **238.4 core-min** at perturbation 132 of 211
(`W5_GRADIENT_REGRADE.md` §3a, §5). The reproducible copy is
`/home/ubuntu/certonomous-runs/W4-a2-provenance/a2_aeroonly_fresh/`.

**This is the single most transferable operational lesson on Ladder A: an optimisation run is not a
read-only operation on its case directory.** Any future A2 work must start from a pristine clone.

---

## 5. What this grading cannot see

1. **It cannot see the limiter defect.** A2's `fvSchemes` was not audited for a `cellLimited`
   gradient scheme feeding `linearUpwind`, and no `limited` → `default` arm was ever run on A2. On
   A1 that lever moves `CD wrt shape` from 92.8% to 0.121% **with the rotation guard already
   patched** (`../../DEFECT_ROBUSTNESS_mesh_and_setup.md` R7). A2's patched rows at 0.02–0.05% are
   evidence *against* a large limiter contribution here, but that is an inference from the result,
   not a measurement of the lever.
2. **It cannot see a decomposition defect at np=1**, because every A2 arm ran at np=4. A2 *is*
   recorded as decomposition-clean (scotch vs simple agreeing at ~1e-04,
   `a2_ct_scotch.log` / `a2_ct_simple.log`), so this is closed by a different measurement — but not
   by this grading.
3. **`check_totals` is all-or-nothing.** It buffers its table until every perturbation finishes. A2
   has now lost a full sweep twice — once to an OOM plus host reboot (207.13 core-min) and once to
   the deformed-mesh mesh-quality abort (238.4 core-min). Any future wide-DV sweep on this case
   should be split into `of`/`wrt` subsets by default.
4. **A vector norm over 96 components can hide a single bad one.** A2's aggregate is graded; no
   per-component table for the 96 shape DVs was ever extracted from these logs, and the `Raw Analytic
   Derivative (Jfor)` / `Raw FD Derivative (Jfd)` rows needed to do it *are* present in the logs
   (`compact_print` is off). This is exactly how A5's idx16 was missed until it was looked for. **A
   free, zero-compute follow-up exists and has not been done.**
5. **It says nothing about the optimisation's gradients after iteration 0.** The gate was passed at
   the undeformed baseline. Every subsequent IPOPT iteration evaluated the gradient at a *deformed*
   mesh, where the degenerate-rotation guard no longer fires and the second, ill-conditioned regime
   takes over instead (`../../ROOTCAUSE_getRotationMatrix3d.md` §4.9). The 28.3% trajectory was
   driven by gradients this verification never examined.

---

## 6. Ledger

| item | value |
|---|---|
| solver core-minutes spent by this document | **0.00** |
| dollars spent | **$0.00** |
| containers started | 0 |
| frozen files edited | 0 |
| filed upstream | nothing |
