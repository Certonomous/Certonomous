# DEFECT CANDIDATE — DAFoam's forward-AD build does not reproduce the plain build's primal, and on a transonic case it reaches NaN in ten iterations

> **Status: NOT FILED ANYWHERE, AND NOT FILING-READY.** No issue has been opened, no maintainer
> contacted, nothing posted, pushed or uploaded. Filing is **Sanaa's decision alone**
> (`DAFOAM_CHARTER.md` §10; `FAMILY_SUPERVISION_GUIDELINES.md` §3.6). Prepared 2026-08-22 by the
> DAFoam team, Lane B, from the A6 N=16 fixed-reference item.
>
> **Why NOT FILING-READY, stated precisely rather than as boilerplate.** A **partial** novelty sweep
> **was** run for this note (§9 — 25 issue/PR queries, 12 Discussions queries, 2 web searches, 1
> methodology control, all 2026-08-22, all read-only) and **found no prior art**. But it is **39
> searches across 4 venues against the house protocol's 63 across 10**
> (`LIAISON_NOVELTY_SWEEP_decomposition_defect.md`), and **the mechanism is unidentified** — §7's
> sweep 1, the one arm that would decide the defect class, **has not been run**. **Two things are
> missing before this is filing-ready: the full-protocol sweep, and sweep 1.** Both are priced in §7
> and §9 and neither is taken here.

**Target if filed:** `mdolab/dafoam` (v5 series). **Class: UNDETERMINED** — *AD correctness* or
*numerical robustness/diagnosability*, and **which one is decided by a single 5-core-minute arm that
has not been run** (§7 sweep 1). **A defect note that does not know its own class says so.**

**Adjacent, separately prepared, same lane:** §8, the `-1e10` false-convergence print, which is the
same diagnosability class as the prepared **D-C** (`DEFECT_CANDIDATE_ksp_options_override.md`) and
would be a comment on that rather than a new issue.

---

## 1. Summary

DAFoam ships three builds of its solver library: the plain build, the reverse-AD build
(`libDASolverADR.so`) and the **forward-AD build (`libDASolverADF.so`, compiled with `CODI_ADF`)**.
The forward build is selected by `daOptions["useAD"]["mode"] = "forward"`, and DAFoam's own
regression harness (`tests/testFuncs.py::run_tests`) and its published verification section both use
it as the **reference** against which the Jacobian-free adjoint is checked.

**On `DARhoSimpleCFoam` the forward build does not reproduce the plain build's primal.** Same image,
same mesh, same `daOptions`, same cold start: the momentum equations are bit-identical, **the energy
equation diverges at the 8th significant figure at iteration 1**, the GAMG pressure solve stops
**two sweeps early**, the cumulative continuity error is **10× worse**, and the run reaches **NaN
within ten iterations**. The derivative `run_model` returns is `nan`.

**The consequence is the one that matters:** on this case the toolchain's own sanctioned verification
reference is unavailable, and it fails **loudly** (NaN) rather than silently — which is the single
piece of good news here and should be stated in any filing.

## 2. What is measured, and on what

| | |
|---|---|
| image | `dafoam-idwarp-rot:v1`, image ID `2927768a16ac` (and see §4 — this is **not** a patched-build finding) |
| DAFoam / OpenFOAM / PETSc | 5.0.0 / v2506 / 3.15.5 |
| case | A6 CRM wing-alone, coarsened, **41,760 cells**, `DARhoSimpleCFoam`, transonic, `primalMinResTol 1e-8`, `transonicPCOption 1`, **np = 1, serial, undecomposed** |
| arms | `s1b` (cold, `endTime 10`), `s1e` (warm-started, `endTime 20`) |
| logs | `/home/ubuntu/certonomous-runs/P3-a6-n16-ref/{s1b,s1e}.log`; plain reference `/home/ubuntu/certonomous-runs/P2-a6-n16/patched.log` |
| record | `cases/dafoam/ladder-a/A6/rung_n16_fixed_reference/RESULTS.md` §5, §6.6 |

## 3. The diagnostic — iteration 1, one line of each log, four numbers

Plain figures from `P2-a6-n16/patched.log:528-542`; forward-AD from `P3-a6-n16-ref/s1b.log:528-542`.

| quantity, **iteration 1** | plain build | **forward-AD (ADF) build** | |
|---|---|---|---|
| `U0 initRes` / `finalRes` | `0.9999999999999988` / `0.07283048716260687` | identical / identical | **bit-identical** |
| `U1 finalRes`, `U2 finalRes` | `0.003381492464613624` / `0.07283327010584476` | identical / identical | **bit-identical** |
| `he initRes` | `0.9999999999746546` | `0.9999999999746546` | bit-identical |
| **`he finalRes`** | **`0.06128002514528321`** | **`0.06128001402295498`** | **first divergence, 8th s.f.** |
| **`p finalRes` / `nIters`** | **`0.08186984767127925` / 7** | **`0.07694766099874849` / 5** | **2 fewer GAMG sweeps** |
| **cumulative continuity** | **`-0.00504349133910657`** | **`-0.05058272456310364`** | **10.0× worse** |
| **CD** | **`0.02122521539888314`** | **`0.01835565832247826`** | **13.5% low** |
| by iteration 10 | (runs to 1,000 normally) | **every state `NaN`** | |

**The reading, with its uncertainty stated.** What is **measured** is the table. What is **inferred**
is the chain: momentum is bit-identical, so the divergence enters at the **energy equation** at the
8th significant figure — the round-off signature of arithmetic performed on CoDiPack's forward type
rather than on a bare `double`. That perturbation is then **amplified by the pressure solve**, which
is `GAMG` with `relTol 0.1, tolerance 0`: a *relative*-tolerance stopping rule crosses its threshold
one V-cycle earlier, returns a 6% larger `finalRes`, and leaves a continuity error ten times larger.
On a transonic cold start that is enough. **A tighter claim than this is not supported by two arms on
one case and is not made here.**

## 4. It is NOT a patched-build artefact — the md5 makes one measurement serve both rows

```
$ docker run --rm dafoam/opt-packages:latest  md5sum .../sharedLibs/libDASolverADF.so
44538ed4ac157ecb5dbb6850cf4bde64
$ docker run --rm dafoam-idwarp-rot:v1        md5sum .../sharedLibs/libDASolverADF.so
44538ed4ac157ecb5dbb6850cf4bde64
```

The lab's images differ only in `DALinearEqn.C` and its rebuilt library
(`TOOLCHAIN_INVENTORY.md` §3); the IDWarp rotation patch is a different library again. **The
forward-AD build is byte-identical across the toolchain, so this is a statement about SHIPPED DAFoam
that happens to have been measured on a patched row.** `DAFOAM_CHARTER.md` §6 requires two rows; here
the identity hash is what licenses one measurement covering both — **not a version string.**

## 5. The warm-start arm — this separates the ADF *primal* from the ADF *derivative machinery*

Started from a converged state (fields only), `endTime 20`, `printInterval 1`, seed `patchV[1]`.
First-iteration cumulative continuity is **`7.535e-07`**, four orders quieter than the cold arm's
`-5.06e-02`, so the warm start took. The full ` ADF-Deriv:` trace for CD against the case's
reverse-mode adjoint value `9.016840e-03`:

| iter | ` ADF-Deriv` | vs adjoint | | iter | ` ADF-Deriv` | vs adjoint |
|---|---|---|---|---|---|---|
| 1 | `8.031390e-03` | 10.93% | | 9 | `7.991144e-03` | 11.38% |
| 5 | `7.843976e-03` | 13.01% | | 10 | `8.291961e-03` | **8.04%** |
| 6 | `7.754665e-03` | 14.00% | | 11 | `8.608182e-03` | **4.53%** |
| 7 | `7.724776e-03` | 14.33% | | 12 | `8.877116e-03` | **1.55%** |
| 8 | `7.790858e-03` | 13.60% | | **13** | **`9.070934e-03`** | **0.600%** |
| | | | | **14** | CD jumps `0.0353` → **`0.1039`** | **primal blew up** |
| | | | | 15–18 | `-nan` | |

**Read the right-hand column from iteration 9: 11.38 → 8.04 → 4.53 → 1.55 → 0.600%. The tangent was
converging monotonically onto the adjoint and reached 0.600% of it, and then the primal destabilised.**

**This is the most useful sentence in the note: what fails is the ADF primal's stability, not the ADF
derivative machinery.** A filing that said "forward AD is broken" would be wrong and would send a
maintainer after the tape. It also shows the cold-start transient is **not** the cause — the failure
happens from a warm, near-converged state too, after thirteen good iterations.

## 6. Minimum reproducer — two arms, one variable changed

```
# ARM P (plain):        daOptions unchanged.
# ARM F (forward AD):   daOptions["useAD"] = {"mode":"forward","dvName":"patchV","seedIndex":1}
#                       AND, in configure() -- NOT setup():
#                           self.<scenario>.coupling.solver.add_dvgeo(self.geometry.DVGeo)
# BOTH arms:
#   "primalMinIters": <endTime>   # else the ADF run exits after 2 iterations -- see s8
#   "printInterval": 1            # so the divergence point is visible at all
#   system/controlDict: endTime 10
#   cold start from a pristine 0/ (no warm-start contamination)
mpirun -np 1 -x PYTHONPATH python runScript.py -task run_model
```

**Three traps, each of which cost this lane an arm and each of which a reproducer must state:**

1. **`add_dvgeo` must be called in `configure()`, not `setup()`.** In `setup()` it raises
   `AttributeError: 'ScenarioAerodynamic' object has no attribute 'coupling'`, because mphys builds
   the `coupling` subgroup inside the scenario's own setup, **after** `Top.setup()` has run
   (`mphys/scenario_aerodynamic.py::_mphys_scenario_setup`). Cost of learning this: 0.433 core-min.
2. **`primalMinIters` must be raised**, or the ADF primal exits after two iterations announcing a
   convergence it has not reached (§8). Cost: 1.300 core-min.
3. **`printInterval` defaults to 100**, so at `endTime 10` only iteration 1 prints and the divergence
   is invisible. Set it to 1. It is numerically inert: `DASolver.C:124` calls
   `calcAllFunctions(printToScreen_)` every iteration and the flag gates only the `Info` output.

**Then compare the four numbers of §3 at `Time = 1`.** That is the whole diagnostic; no gradient, no
adjoint, no optimiser is needed.

## 7. Characterisation — two sweeps, their prices, and what each OUTCOME would prove

**Neither has been run. The first is what makes this note filing-ready.**

### Sweep 1 — solver family. **~5 core-min ($0.004). This decides the defect class.**

Re-run ARM F with the `p` solver switched from `GAMG` to `PBiCGStab`/`DIC` in `system/fvSolution`,
everything else held byte-identical.

| outcome | what it proves | class |
|---|---|---|
| **NaN disappears** | the mechanism is §3's inferred one: a *relative*-tolerance stopping rule on a value-dependent multigrid cycle, amplifying an 8th-digit AD round-off difference | **conditioning / diagnosability.** The ask becomes a documentation + warning change, not an AD fix |
| **NaN persists** | the divergence is in the AD arithmetic itself, independent of the pressure solver | **AD correctness.** A materially more serious report |

### Sweep 2 — case family. **~10 core-min ($0.009). This decides the report's SCOPE.**

The same two arms on **A1 naca0012** (4,032 cells, incompressible, `DASimpleFoam`) and **A4 Ahmed-25**
(2,777 cells) — both already staged in this lab, both with converged FD references on record.

| outcome | what it proves |
|---|---|
| **ARM F reproduces ARM P on both** | the finding is specific to the transonic/compressible solver and must be reported as such, not as a general AD claim |
| **ARM F diverges there too** | forward-mode AD is unusable across this lab's entire Ladder A, and **every record that assumed it as a fallback reference needs the caveat** |

### Why a MESH-family sweep is explicitly NOT the first one

The obvious next move — run N=16 against the archived N=53 (579,072 cells) — **varies size, not
mechanism.** It cannot distinguish a GAMG stopping artefact from an AD-arithmetic defect, which is the
open question; it would only tell us the failure also happens on a bigger mesh, which nobody doubts.
It is also the **most expensive** of the three and **A6 at full size is `BLOCKED` on two independent
grounds** (`ladder-a/A6/adjoint_feasibility/RESULTS.md`). **Cheapest discriminating arm first, and
that is sweep 1.**

## 8. The adjacent finding — a primal that announces a convergence it has not reached

`DASolver::loop`, `src/adjoint/DASolver/DASolver.C:188`:

```c
if ((daGlobalVarPtr_->primalMaxRes < primalMinResTol_ || (funcStd_ < primalFuncStdTol_ && ...))
    && runTime.timeIndex() > primalMinIters_)
{
    Info << "Minimal residual " << daGlobalVarPtr_->primalMaxRes
         << " satisfied the prescribed tolerance " << primalMinResTol_ << endl;   // :194
```

with `primalMaxRes` **re-initialised to `-1e10`** at the bottom of the same function (`:222`) and
`primalMinIters` **defaulting to 1** (`pyDAFoam.py:639`, whose own comment reads *"The default is 1:
the primal has to run for at least one iteration"*).

**Where `primalMaxRes` is not updated on the first step, `-1e10 < 1e-8` is trivially true and the
guard reduces to the iteration counter alone.** The run then stops at iteration 2 and prints:

```
Time = 3
Minimal residual -10000000000 satisfied the prescribed tolerance 1e-08
```

**A DAFoam run can print "satisfied the prescribed tolerance" having satisfied nothing, and
`-10000000000` in that line is the tell.** Observed on `s1b.log`; removed by raising `primalMinIters`.

**Minimal upstream change:** guard the comparison on `primalMaxRes > 0`, or initialise it to `+VGREAT`
rather than `-1e10`, or refuse to print the convergence line when the sentinel is unchanged. **One
condition.** Class **diagnosability**, same as **D-C**; if filed it belongs as a comment there.

## 9. Novelty sweep — run 2026-08-22, read-only, and PARTIAL

**Method.** GitHub REST `search/issues` (`repo:<r>+<q>`, all states, issues **and** PRs) for the code
venues; the Discussions **HTML** search for the discussions venue, because **REST does not index
Discussions** — that is protocol trap #1 in `LIAISON_NOVELTY_SWEEP_decomposition_defect.md` and it is
covered here. Two web searches for non-GitHub venues. **Every request a GET. Nothing posted, no
account touched, no issue opened.**

### 9.0 A methodology control, run first, because the Discussions counts are otherwise unreadable

| query | distinct thread links returned |
|---|---|
| `zzzqqxnonsensetoken12345` (nonsense) | **1** |
| `forward AD` | 24 |

**The floor is 1, not 0.** Discussion **#883** — *"Have 30 minutes? Meet with us to share your DAFoam
feedback!"* — is **pinned and returned for every query including nonsense**. **Effective hits =
distinct threads − 1**, and every count in §9.2 must be read that way. Without this control a
`primalMaxRes` result of "1 thread" would read as a hit; it is a **zero**.

### 9.1 Venue 1 — `mdolab/dafoam` issues + PRs (25 queries, REST, all states)

| # | query | hits | disposition |
|---|---|---|---|
| 1 | `forward AD` | **2** | **#154** *Added forward AD* (PR, 2021-06-28, closed same day, **empty body, 0 comments**); **#155** *Fix forward AD* (PR, 2021-06-30, same). **Establish that the feature exists and was patched once; describe nothing resembling non-reproduction.** |
| 2 | `useAD forward` | 0 | negative |
| 3 | `ADF` | 0 | negative |
| 4 | `CODI_ADF` | 0 | negative |
| 5 | `forward mode` | **2** | **#833** *A question about the accuracy of the gradient* (open, 2025-05-21, promoted from Discussion #714) — a **user asking how to FD-verify**, noting that *"in the verification section, you introduced forward-mode differentiation to check the correctness of the gradients."* **Near-miss, not prior art** — see §9.4. #322 (propeller aerostructural) unrelated. |
| 6 | `tangent` | 0 | negative |
| 7 | `codipack` | 1 | #586 (GPU/OGL feature request) — unrelated |
| 8 | `NaN forward` | 0 | negative |
| 9 | `ADF-Deriv` | 0 | negative |
| 10 | `libDASolverADF` | 0 | negative |
| 11 | `forward AD diverge` | 0 | negative |
| 12 | `seedIndex` | 0 | negative |
| 13 | `primalMinIters` | **0** | negative — **§8 has no issue-tracker trace at all** |
| 14 | `primalMaxRes` | 0 | negative |
| 15 | `satisfied the prescribed tolerance` | 1 | not the `-1e10` signature |
| 16 | `-10000000000` | **0** | negative — **the §8 tell has never been posted** |
| 17 | `primalMinResTolDiff` | 0 | negative |
| 18 | `false convergence` | 0 | negative |
| 19 | `primal solution failed` | 1 | the ordinary `AnalysisError`, not the sentinel print |
| 20–22 | `mdolab/idwarp`: `forward mode` / `primal` / `OpenFOAM` | 0 / 1 / 7 | none on point |
| 23–25 | `SciCompKL/CoDiPack`: `OpenFOAM` / `GAMG` / `reproducib` | 0 / 0 / 0 | **the AD library's own tracker has never discussed OpenFOAM or multigrid reproducibility** |

### 9.2 Venue 2 — `mdolab/dafoam` Discussions (12 queries, HTML; read with §9.0's −1 floor)

| # | query | threads | **effective** | disposition |
|---|---|---|---|---|
| 26 | `forward AD` | 24 | 23 | broad OR-match on common words; no thread title on point |
| 27 | `useAD` | 9 | 8 | includes **#714**, the source of #833 |
| 28 | `ADF` | 17 | 16 | OR-match noise |
| 29 | `forward mode` | 23 | 22 | OR-match noise |
| 30 | **`tangent`** | **1** | **0** | **clean negative** |
| 31 | `codipack` | 9 | 8 | includes **#1008** *AD implementation for custom topology optimization variables* — AD-adjacent, **not** about ADF/plain divergence |
| 32 | **`primalMinIters`** | **2** | **1** | #970 *cyclicAMI problem* — unrelated. **Effectively negative.** |
| 33 | **`primalMaxRes`** | **1** | **0** | **clean negative** |
| 34 | `satisfied the prescribed tolerance` | 9 | 8 | convergence traffic; none carries the `-1e10` sentinel |
| 35 | `primalMinResTolDiff` | 13 | 12 | ordinary option traffic |
| 36 | `NaN primal` | 5 | 4 | ordinary divergence traffic; none contrasts ADF against plain |
| 37 | `GAMG` | 6 | 5 | ordinary solver traffic |

**Caveat on this venue, stated rather than hidden:** GitHub's Discussions search appears to **OR** the
terms, so multi-word queries return large, weakly-relevant sets. **The evidential weight here sits on
the single-token queries** — `tangent` (0), `primalMaxRes` (0), `primalMinIters` (1, unrelated) —
**not on the large counts.**

### 9.3 Venue 3 — open web (2 searches)

| # | query | disposition |
|---|---|---|
| 38 | `DAFoam forward mode AD "useAD" primal diverges NaN differs from reverse mode` | **No prior report found.** Returned DAFoam's own docs and `DAFoam/OpenFOAM-v1812-AD`. **Confirms the upstream posture:** the published verification section uses **forward-mode AD as the reference** against the Jacobian-free adjoint. |
| 39 | `DAFoam "Minimal residual" "satisfied the prescribed tolerance" primalMinIters false convergence -1e10` | **No prior report found.** Returned the DAOPTION doxygen page and generic OpenFOAM residual guidance. |

### 9.4 Verdict of the sweep

> **No prior art was found for either finding, in 39 recorded searches across 4 venues on 2026-08-22.**
> **This is NOT the same statement as "novel."** The house protocol is **63 searches across 10
> venues**; this sweep covered **4**. **Not covered:** the mdolab mailing lists, CFD-Online, the
> OpenFOAM forums, Google Scholar, `DAFoam/OpenFOAM-v1812-AD`'s own tracker, and the MeDiPack
> repository. **Completing it is zero-compute and is the second of the two things standing between
> this note and filing-readiness.**
>
> **The one near-miss is worth stating plainly**, because it cuts against the finding's obscurity
> rather than for it: **#833 / Discussion #714 is a user reaching for FD verification precisely
> because forward-mode differentiation is what the documentation points them at.** If forward mode
> is unusable on compressible cases, that user is being pointed at an unavailable instrument. **That
> raises the value of filing; it does not constitute prior art, because the thread never mentions
> ADF-versus-plain divergence, NaN, or the primal at all.**

## 10. What this note does NOT establish

1. **The mechanism.** §3's GAMG amplification is an **inference from two arms on one case**.
   Sweep 1 is unrun, so **the defect class is undetermined** and §"Target if filed" says so.
2. **The scope.** One case, one solver (`DARhoSimpleCFoam`), one mesh size, np = 1. Nothing here says
   whether incompressible or other solvers are affected. Sweep 2 is unrun.
3. **That the ADF derivative is wrong.** §5 is evidence for the **opposite** — the tangent converged
   to 0.600% of the adjoint before the primal failed.
4. **That the plain build is right and the ADF build is wrong.** The two builds differ; **which one
   the 8th-digit `he finalRes` difference favours is not determined by anything measured here.**
5. **Novelty**, per §9.4.
6. **Any parallel behaviour.** Every arm is np = 1, undecomposed (`DAFOAM_CHARTER.md` §5).
7. **A memory or performance claim.** The 27 s/iteration observed on the cold arm is **NaN-contaminated**
   — GAMG cannot satisfy a convergence test on NaN and runs to its iteration limit — and is
   **explicitly not reported as an AD cost factor.**

## 11. Suggested tone if filed

Report **§3's four numbers and §6's reproducer** first and let them stand on their own; they are
cheap for a maintainer to run and need no lab context. Report **§5 second and prominently**, because
it tells the maintainer where *not* to look. State the class as **undetermined** and **offer sweep 1's
result** rather than asserting a mechanism. Keep §8 separate — it is a one-condition diagnosability
fix and does not need to ride on an unresolved AD question.

**Nothing in this file has been sent, filed, posted, uploaded or pushed. Filing is Sanaa's alone.**
