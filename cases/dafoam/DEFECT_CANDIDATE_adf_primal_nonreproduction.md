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

---

## ADDENDUM 2026-08-24 — sweep 1 narrows D460's class to CONDITIONING / DIAGNOSABILITY, and the mechanism behind that `PASS` is narrower than the ratio makes it look

*Appended, not rewritten. Nothing above this line changed; **lines whose number
changed above this section: 0**. This file carries no version number, so there is
no version to bump — the dated addendum is the version record. This addendum
alters **no disposition, no count, no verdict, no gate and no threshold** anywhere
above it, and it is not a re-argument of a gate after the fact.*

**Landed by the DAFoam team, lab-lane, on the dafoam-supervisor's ruling of
`RESULTS.md` §9f — ruled YES, 2026-08-24.**

### What sweep 1 settled

`cases/dafoam/d460_sweep1_solver_family/` — pre-registration FROZEN at `538c9f51`
(+ AMENDMENT 1; AMENDMENT 2 at `f0448fab`, both before first compute; ADDENDUM 3
at `a7abde10` after first compute, its harness-repair exception SPENT and unused
by the grading lane). Comparator `analyse_sweep1.py`, sha256
`239c1764c6b2ff8db5736c45f0f5f00f0debba0a4a93e745b080e1e641be7e94` — equal on
disk and in the committed blob, hash-checked inside the grading invocation.
Graded 2026-08-24T16:09:30Z, exit 0, all three planted controls read back live on
that same invocation.

> ## VERDICT: `PASS`
> ## CLASS: CONDITIONING / DIAGNOSABILITY

The class question this record left **UNDETERMINED** is answered **for this case,
one solver, one mesh, np = 1, ten iterations**: the upstream ask is a
**documentation + warning change, not an AD fix**, and the more serious
**AD-correctness reading is not reached**.

### The mechanism, stated because the ratio alone flatters the result

The gated quantity is `r = |cum_F| / |cum_P|`, the ratio between the two builds'
cumulative continuity magnitudes at `Time = 1`. It fell from `10.029307` under
`GAMG` to `0.968227` under `smoothSolver`, inside the registered band of 2.0. But
**both magnitudes GREW**:

| | GAMG (on record) | `smoothSolver` (sweep 1) | change |
|---|---|---|---|
| `\|cum_F\|` — forward-AD arm | `0.05058272456310364` | `0.08515074416090457` | **×1.683** |
| `\|cum_P\|` — plain arm, **the CONTROL** | `0.00504349133910657` | `0.08794505498506013` | **×17.437** |
| `r` | `10.029307` | `0.968227` | **÷10.36** |

**`r` fell mainly because the CONTROL's own continuity error grew 17.4×, not
because the forward-AD arm's error fell — it rose 1.68×.** The honest statement of
the mechanism is therefore:

> **Under `smoothSolver` both builds converge on each other at a worse absolute
> level, and the 8th-figure AD difference is no longer the dominant term because a
> larger common term now dominates both.**

It is **not** "the amplification collapsed", and it is **not** a claim that
`smoothSolver` is a better pressure solver for this case. The registered band
gates the ratio, the ratio is inside it, and the `PASS` stands exactly as frozen —
a gate is not re-argued after the fact — but the *mechanism* is the narrower
statement above.

**This caveat travels with the class.** Any downstream statement of D460's class —
**including a revised upstream draft, if one is ever prepared** — carries it. A
`PASS` on a ratio gate is not a licence to state the ratio's fall as a property of
its numerator.

### Unchanged by sweep 1, and re-asserted here

1. **The 8th-significant-figure `he finalRes` difference between the two builds is
   still present under `smoothSolver`** — `0.06128001402295498` (forward-AD)
   against `0.06128002514528321` (plain), unchanged in every digit. Not amplified,
   not removed.
2. **Which build is *right* is untouched.** Sweep 1 measured what the difference
   *does*, never which side of it is correct.
3. **`DAFoam/OpenFOAM-AD` issue #2's opposite polarity is exactly as unresolved
   after this run as before it.** The arm avoided PBiCGStab/DILU by construction,
   so #2 is excluded as a **confound**, not connected or disconnected as a
   **mechanism**.
4. **Neither arm is a converged solve** — `endTime 10`, `primalMinIters 1000000`,
   ten-iteration probes by design.
5. **D460 sweep 2 (case family) is UNRUN and UNAUTHORISED**, and neither sweep 1
   nor this addendum authorises it; it needs its own costed pre-registration.
6. The registered prediction **P5 MISSED**, and not narrowly: removing multigrid
   drove the two builds' pressure-sweep counts **219 apart** (206 vs 425) where
   the registered expectation was *fewer* than the `GAMG` pair's 2.

*Sources for every number above:*
`cases/dafoam/d460_sweep1_solver_family/RESULTS.md` §4, §5, §5a, §5b, §6, §8;
`GRADE_sweep1.txt`, `fsm.log`, `psm.log`, `ledger.txt` in
`/home/ubuntu/certonomous-runs/D460-sweep1-solver-family/`.
*Records landed from this close-out:* `docs/LESSONS.md` L-274, L-275, L-276;
`docs/NUMERICS_KNOWLEDGE.md` N-D30, N-D31; `docs/DOCKET.md` D498;
`docs/COST_CALIBRATION.md` C-22.

### Filing status — re-asserted, unchanged

**This note remains NOT FILED ANYWHERE.** The `NOT FILED` marker stands where rule
7 requires it — in this file's **opening lines, at the top** — unamended by this
addendum, and not moved, weakened, superseded or replaced by anything written
here. No issue has been opened, no maintainer contacted, nothing posted, pushed,
uploaded, registered or commented.

**Sweep 1 closing does not make this note filing-ready and does not authorise a
send.** It answers §7's class question and closes §10 item 1's "mechanism
unidentified" blocker **for this case only**; §10 items 2–7 stand unchanged, sweep
2 (case family) is unrun, and **filing remains Sanaa's decision alone**
(`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10; `FAMILY_SUPERVISION_GUIDELINES.md`
§3.6).

**On §11's suggested tone, if this note is ever revised:** the class may then be
stated as **CONDITIONING / DIAGNOSABILITY for this case** rather than undetermined
— and **any such revision must carry the mechanism paragraph above**. A draft that
reported `r` falling from `10.029307` to `0.968227` without saying that the
control's own continuity error grew 17.4× would tell a maintainer something this
lab did not measure.

**Nothing in this addendum has been sent, filed, posted, uploaded or pushed.
Filing is Sanaa's alone.**

---

## ADDENDUM 2026-08-24 (second) — Filing-readiness reassessment, 2026-08-24T17:50:53Z

*Appended, not rewritten. Nothing above this line changed; **lines whose number
changed above this section: 0** — asserted and machine-checked: the first **446**
lines of the amended file were `cmp`-ed byte-for-byte against `git show
HEAD:cases/dafoam/DEFECT_CANDIDATE_adf_primal_nonreproduction.md` inside the same
shell invocation that wrote the commit, and the commit was gated on that `cmp`
returning 0.*

***Version bump.*** This file carries no version field in its header and its
header is frozen, so the version cannot be written there. **The version is
therefore declared here and this declaration is the version record:** this file is
now **v3** — **v1** the body of 2026-08-22 (`757eccf0`, lines 1–331), **v2** the
sweep-1 class addendum of 2026-08-24T16:35:55Z (`20dd303e`, lines 333–446), **v3**
this addendum. ADDENDUM 1 declined to number itself; numbering it retrospectively
here changes no line above and is the same house practice its sibling
`LIAISON_NOVELTY_SWEEP_adf_primal_nonreproduction.md` uses.

**This addendum alters no gate, no threshold, no cap, no label, no count, no
disposition and no verdict anywhere above it.** It is a **readiness assessment and
a set of PROPOSED wordings**. **Nothing in it is applied to the body**, which is
frozen, and **nothing in it authorises, prepares or performs a send.**

> ### NOTHING HERE AUTHORISES OR PERFORMS A SEND.
> This is a document about whether a document is ready to be read by its owner.
> **No issue has been opened, no maintainer contacted, nothing posted, pushed,
> uploaded, registered or commented, by this lane or any other.** Filing is
> **Sanaa's decision alone** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10;
> `FAMILY_SUPERVISION_GUIDELINES.md` §3.6). A readiness state of
> `READY-FOR-SANAA'S-READ` would mean *this file is worth her ten minutes* and
> would mean **nothing else**; the phrase "ready to file" does not appear in this
> lab's vocabulary and is not used here.

**`NOT FILED` marker, machine-checked before and after this append.** `grep -c
'NOT FILED'` over the file's **first five lines** — the placement
`DAFOAM_CHARTER.md` §10 requires, "in their opening lines, with the marker at the
top of the file and not in a closing paragraph" — returned **1 before** and **1
after**. Whole-file `grep -c 'NOT FILED'` returned **2 before** and **6 after**
(this addendum re-asserts it four times). The opening-lines count is the one the
charter binds and it is **unchanged**; the commit was gated on it, and had it
changed the commit would have aborted. Line 3's status block is untouched.

**Scope of this reassessment.** It is written from **this evidence set only**: the
body (v1), ADDENDUM 1 (v2), `LIAISON_NOVELTY_SWEEP_adf_primal_nonreproduction.md`
including its two 2026-08-23 addenda, `cases/dafoam/d460_sweep1_solver_family/RESULTS.md`,
`docs/LESSONS.md` L-274/L-275/L-276, `docs/NUMERICS_KNOWLEDGE.md` N-D30/N-D31,
`docs/DOCKET.md` D498, `docs/charters/DAFOAM_CHARTER.md` §6 and §10, and
`docs/dafoam/README.md` §3 and §6. **Zero compute was spent on it.** Anything
outside that set is not assessed and is not asserted about.

**A citation correction, stated because the brief that commissioned this section
carried it.** The **two-row shipped/patched rule and the toolchain-identity rule
(an image ID and a library hash, never a version string)** are `DAFOAM_CHARTER.md`
**§6**, not §11 — §11 of that charter is the lessons/numerics numbering clause, and
§11 of *this file* is "Suggested tone if filed". The prose convention for the
two-row table is `docs/dafoam/README.md` §3 (rule **R11**: a patched grade is
recorded *beside* a shipped grade and never in place of it). This section assesses
against §6 and R11.

**Checklist form.** The table in §A1 below reuses the house **"Submission
readiness"** form already used by the two prepared upstream reports —
`UPSTREAM_BUG_REPORT_decomposition_adjoint.md:330-336` and
`UPSTREAM_BUG_REPORT_mesh_warpDeriv.md:287-294` — `| requirement | state |`, with
each state **Done** or **NOT DONE** and the evidence named. That form is reused
rather than invented so D460 can be read beside D-A/D-A2 and D-B/D-B2 without a
translation step. **D-C and D-E carry no such table**: D-C states readiness as a
bare status line (`DEFECT_CANDIDATE_ksp_options_override.md:1,3,169`) and D-E
(`ladder-b/B3/DEFECT_NOTE_ilu_zero_pivot.md`) carries no readiness section at all —
so there was no fifth form to reconcile.

---

### A1. What a reader upstream would need to reproduce this, and whether the draft has it

**Assessed by line against the frozen body.** "Present" means a maintainer who
opens this file and nothing else can act on it.

| # | requirement | present in the draft? | by line |
|---|---|---|---|
| 1 | **Image identity — an ID, not a version string** (`DAFOAM_CHARTER.md` §6) | **Done.** `dafoam-idwarp-rot:v1`, image ID `2927768a16ac`; DAFoam 5.0.0 / OpenFOAM v2506 / PETSc 3.15.5 | **:49, :50** |
| 2 | **Library hash** for the library under test | **Done.** `libDASolverADF.so` md5 `44538ed4ac157ecb5dbb6850cf4bde64`, shown equal on `dafoam/opt-packages:latest` and `dafoam-idwarp-rot:v1` | **:83–:86** |
| 3 | **Both rows, shipped and patched** (§6; README §3 R11) | **Done for the FORWARD-AD arm, NOT DONE for the CONTROL arm.** See §A1.1 — this is the one genuinely new gap this reassessment found | **:89–:93** (the argument), **:49** (the single image row) |
| 4 | **The case** | **Done as a description, NOT DONE as an artifact.** A6 CRM wing-alone coarsened, 41,760 cells, `DARhoSimpleCFoam`, transonic, `primalMinResTol 1e-8`, `transonicPCOption 1`, np=1 serial undecomposed. **The mesh is lab-built and the draft says nowhere how a maintainer obtains it** | **:51**; record pointer **:54**, logs **:53** — both are paths *inside this box*, which a maintainer cannot read |
| 5 | **Exact commands** | **Partially done.** The invocation is exact — `mpirun -np 1 -x PYTHONPATH python runScript.py -task run_model` — and the three `daOptions` deltas and the three traps are stated. **`runScript.py` itself is neither supplied nor pointed at**, so the one command given cannot be run | **:123–:132** (the block), **:135–:145** (the traps), **:147–:148** (what to compare) |
| 6 | **The GAMG stopping-rule lever** — the load-bearing mechanism claim | **Done in the body, and it is the draft's best line.** `GAMG` with **`relTol 0.1, tolerance 0`**, named as a *relative*-tolerance stopping rule crossing its threshold one V-cycle early | **:73–:75** |
| 6b | **The counter-configuration that removes the failure** — `smoothSolver`/`GaussSeidel`/`nSweeps 1` on `p` | **Present in the FILE (ADDENDUM 1), absent from the REPRODUCER.** A maintainer reading §6 is told how to make it fail and not how to make it stop failing, and the fact that it stops failing is now the report's whole class argument | body **:122–:148** has it **not at all**; ADDENDUM 1 **:344–:394**; measured detail in `N-D31`'s sibling `N-D30` |
| 7 | **Both arms' `fvSolution` differing in exactly one block** | **NOT DONE in the draft.** Measured and recorded elsewhere — five lines in the `"(p\|p_rgh\|G)"` block, the two files otherwise byte-identical (`N-D30`) — but the draft never states it | — |

#### A1.1 The two-row gap this reassessment found, stated as a reading and not as a measurement

§4 (**:89–:93**) argues that the md5 identity of `libDASolverADF.so` across the two
images "licenses one measurement covering both rows". **That argument covers the
forward-AD arm and only the forward-AD arm.** Line **:89** states that the lab's
images "differ only in `DALinearEqn.C` and its rebuilt library", and `N-D31`
records that the **plain control arm loads `libDASolver.so` and `libDASolverADR.so`**,
not `libDASolverADF.so`. **`DALinearEqn.C` compiles into the `libDASolver*` family.**
So on the face of the draft's own two sentences, **the control arm may well have run
on a patched library whose hash is nowhere established**, and §4's "this is a
statement about SHIPPED DAFoam" therefore rests on an identity that has been proved
for one of the two arms.

**This is a reading of :89 against `N-D31`, not a measurement.** It is not a claim
that the control arm is contaminated; it is a claim that **the draft does not
contain what would rule that out**, and §6 of the charter asks for exactly that.
Closing it is one `md5sum` per image on `libDASolver.so` — see §A5 item 6.

---

### A2. What the sweep-1 `PASS` changes in the draft's CLAIM — the class is CONDITIONING / DIAGNOSABILITY, not AD correctness

**The settled position, from `d460_sweep1_solver_family/RESULTS.md` §5 and D498:**
the class is **CONDITIONING / DIAGNOSABILITY** for **this case, one solver, one
mesh, np = 1, ten iterations**. The upstream ask is a **documentation + warning
change, not an AD fix**, and **the AD-correctness reading is not reached**. The
liaison sweep adds the framing: this is an **opposite-polarity second instance of
the open, maintainer-authored `DAFoam/OpenFOAM-AD` #2** — #2 reports AD builds
blowing up under `PBiCGStab`/`DILU` and *fixed* by `GAMG`; D460 measures the
forward-AD build failing under `GAMG` and *not* failing under `smoothSolver`.

**Four sentences in the frozen body still read as an AD-correctness claim** — that
is, they assert, hold open, or offer as a live branch the reading that the
forward-AD *arithmetic* may be wrong. Each is quoted, and each carries a
**PROPOSED** replacement. **The proposals are proposals. The body is frozen; not
one character of it is changed by this addendum; adopting any of them is the
supervisor's ruling and would itself be a further dated addendum.**

---

**AD-CORRECTNESS SENTENCE 1 — lines :17–:19** *(the first screen, and therefore the
most consequential)*

> **Target if filed:** `mdolab/dafoam` (v5 series). **Class: UNDETERMINED** — *AD correctness* or
> *numerical robustness/diagnosability*, and **which one is decided by a single 5-core-minute arm that
> has not been run** (§7 sweep 1). **A defect note that does not know its own class says so.**

Two independent defects now: the class is no longer undetermined, and the arm is no
longer unrun. **PROPOSED replacement:**

> **Target if filed:** a comment on the open `DAFoam/OpenFOAM-AD` **#2**, with
> `mdolab/dafoam` (v5 series) as the alternative venue. **Class: CONDITIONING /
> DIAGNOSABILITY**, decided 2026-08-24 by the redesigned sweep 1
> (`cases/dafoam/d460_sweep1_solver_family/`, `PASS`) **for this case, one solver,
> one mesh, np = 1 and ten iterations, and for nothing wider**. The ask is a
> **documentation + warning change, not an AD fix**; the AD-correctness reading is
> **not reached**. **The class rests on a ratio whose fall is mostly the control's —
> see ADDENDUM 1's mechanism paragraph, which travels with this class wherever it
> is stated.**

---

**AD-CORRECTNESS SENTENCE 2 — line :162** *(the strongest one, and now doubly
unavailable)*

> | **NaN persists** | the divergence is in the AD arithmetic itself, independent of the pressure solver | **AD correctness.** A materially more serious report |

This row is unavailable for **two independent reasons**, and the second survives
even if the first is ignored. **(i)** The arm ran and the NaN did **not** persist
(`RESULTS.md` §4 G2: 0 NaN tokens against 14 in `s1b.log`). **(ii)** The liaison
sweep §5b established **before any compute** that the row's inference was
**confounded by construction**: `PBiCGStab` is the exact configuration
`OpenFOAM-AD` #2 already reports as breaking AD builds, so a NaN under it would
have been fully explained by a separately-reported known defect; and `DIC` is a
*symmetric* preconditioner that the asymmetric transonic `fvm::div(phid, p)`
pressure equation would likely have refused before computing anything.
**PROPOSED replacement for the whole §7 sweep-1 table (:159–:162):**

> **Sweep 1 was redesigned and run.** The `PBiCGStab`/`DIC` design sketched below
> was **withdrawn before compute as confounded** — see
> `LIAISON_NOVELTY_SWEEP_adf_primal_nonreproduction.md` §5b. The executed arm swaps
> `p` to **`smoothSolver`/`GaussSeidel`/`nSweeps 1`**, which is neither multigrid
> nor the `PBiCGStab`/`DILU` pair upstream reports as broken, and is the solver the
> maintainer himself named as the fix in `OpenFOAM-v1812-AD` #2 (2020-12-07).
> **Outcome: the NaN disappears — `PASS`, class CONDITIONING / DIAGNOSABILITY.**
> **The "NaN persists → AD correctness" branch was never reachable by the design it
> was registered against, and is struck rather than merely unexercised.**

---

**AD-CORRECTNESS SENTENCE 3 — line :308**

> Sweep 1 is unrun, so **the defect class is undetermined** and §"Target if filed" says so.

**PROPOSED replacement:**

> Sweep 1 ran 2026-08-24 and graded `PASS`: **the class is CONDITIONING /
> DIAGNOSABILITY for this case only.** What §10 item 1 still withholds is narrower
> and is not closed: **the sweep did not confirm §3's inferred mechanism.** `r` fell
> from `10.029307` to `0.968227` mainly because the **control's** own continuity
> error grew **×17.437** while the forward-AD arm's **rose ×1.683** — both builds
> converge on each other at a *worse* absolute level. **§3's GAMG-amplification
> story remains an inference from two arms on one case.**

---

**AD-CORRECTNESS SENTENCE 4 — lines :325–:326**

> State the class as **undetermined** and **offer sweep 1's result** rather than asserting a mechanism.

**PROPOSED replacement** — and note that the liaison sweep §5a item 3 independently
requires **all** of §11 rewritten, because the filing is no longer "here is a new
defect":

> State the class as **CONDITIONING / DIAGNOSABILITY for this case**, give sweep 1's
> result and its `smoothSolver` counter-configuration, and **state the mechanism
> caveat in the same breath as the class** — that `r`'s fall is mostly the control's
> error growing. Frame the report as **a second instance of the maintainer's own
> open `OpenFOAM-AD` #2, at the opposite solver polarity, on a compressible
> transonic case, with the divergence located to the 8th significant figure of the
> energy equation at iteration 1** — which is a *better* report than a new-defect
> filing, because it attaches to an issue the maintainer already owns and supplies
> the digit-level entry point #2 lacks. Cite `mdolab/CMPLXFOIL` **#28** as the
> merged, mdolab-authored precedent for the remedy. Keep §8 separate.

---

**Three further sentences are NOT AD-correctness claims but read to a maintainer as
unconditional properties of the forward-AD build**, when what is measured is a
property of the **build × pressure-solver pair**. They are listed because a reader
upstream will not make the distinction the draft does not make for them.

| line | text | why it now misreads | PROPOSED |
|---|---|---|---|
| **:1** (title) | "…and on a transonic case it reaches NaN in ten iterations" | true **under `GAMG`**; false under `smoothSolver` | append "**under `GAMG` on `p`**" |
| **:38–:39** | "the run reaches **NaN within ten iterations**. The derivative `run_model` returns is `nan`." | same | "…reaches **NaN within ten iterations under `GAMG` on `p`**, and completes ten finite iterations when `p` is switched to `smoothSolver`" |
| **:41–:43** | "on this case the toolchain's own sanctioned verification reference is unavailable" | **now falsified in its unconditional form** — under `smoothSolver` the forward build completes and prints a finite value | "…is unavailable **in this case's shipped `fvSolution` configuration**, and is recoverable by changing the pressure solver — which is what makes this a conditioning report rather than an AD one" |

**Count: 4 sentences read as AD-correctness claims (:17–:19, :162, :308,
:325–:326); 3 more read as solver-unconditional properties (:1, :38–:39,
:41–:43). Seven flagged in total.**

**One row is stale rather than wrong and is recorded here for completeness:** line
**:152**, *"Neither has been run. The first is what makes this note filing-ready."*
Sweep 1 has now run, and **its running did not make this note filing-ready** — see
§A5. The sentence overstated what one arm could buy, which is a claim about
readiness rather than about AD, and §A6 is the correction.

---

### A3. The §5a mechanism caveat — is it in the abstract-level text?

**No. It is not, and this is a placement finding, not a content finding.**

The caveat is stated, correctly and at length, in **ADDENDUM 1 at :363–:394**, and
ADDENDUM 1 at **:390–:394** explicitly binds it to *"any downstream statement of
D460's class — including a revised upstream draft, if one is ever prepared"*. So
the caveat exists, is committed, and is bound.

**But this file's abstract-level text is lines :1–:44** — the title, the status
block, the "Target if filed" block and §1 Summary — and the caveat appears **319
lines below the first of them**. `DAFOAM_CHARTER.md` §10 is explicit that a defect
record says what it must **"on its first screen"**. A reader who reads the first
screen of this file today is told the class is **UNDETERMINED** (:17) and meets the
caveat **never**. The two failure modes that follows are opposite and both real:
the first-screen reader gets a **stale, more-alarming** class, and a reader who
skips to ADDENDUM 1 gets the **correct** class with the caveat attached.

**PROPOSED** (again: proposed, not applied — and this one cannot be applied by
appending, which is precisely why it is flagged): the class-plus-caveat pair
belongs in the same sentence at :17, and any revised draft prepared for Sanaa's
read should carry it in its opening block. **Until a revision exists, this addendum
is the pointer**, and the pointer is: *the class is CONDITIONING / DIAGNOSABILITY;
`r` fell mainly because the control's error grew 17.4×, not because the AD arm's
fell — it rose 1.68×.*

---

### A4. Novelty — the `CMPLXFOIL` #28 analogue, and the unstruck §9.4

**Does the draft cite `mdolab/CMPLXFOIL` #28? No — zero occurrences.** Measured:
`grep -c 'CMPLXFOIL'` over the whole file at HEAD returns **0**.
`grep -c 'OpenFOAM-AD'` returns **1**, at **:403**, inside ADDENDUM 1, and there it
appears only to say that #2's opposite polarity is *"exactly as unresolved after
this run as before it"* — it is **never introduced as prior art anywhere in this
file**.

**What #28 is.** `mdolab/CMPLXFOIL` **#28**, *"Match complex version convergence
tolerances to real version"*, 2024-07-17, **merged**, author `eytanadler` (mdolab):
the primal (real) build of XFOIL converges while the gradient evaluation with the
complex build does not, and **one identified cause is that the tolerances of the
real and complex builds do not match**. It is **analogue prior art of the family
from mdolab's own tree** — a differentiated build failing where the plain build
succeeds, with the lever being **the stopping tolerance rather than the
differentiated arithmetic**, and the accepted fix being to make the two builds'
stopping rules agree. That is **D460's conditioning branch, with a merged
maintainer precedent for the exact remedy the class implies**. It is **not** prior
art of D460's finding — different code, Fortran, complex-step not CoDiPack
forward-AD, different equation set, and it reports a *gradient* failing rather than
a primal *differing at the 8th digit* — and it **does not narrow the novelty
statement**. It belongs in any filing (liaison §A4, §A9 item 2).

**The larger novelty problem, which #28 is not.** **§9.4 at :291 still reads *"No
prior art was found for either finding"*, and the liaison sweep's full-protocol
verdict is that this sentence is "not sustainable for the primal finding"** —
`DAFoam/OpenFOAM-AD` **#2** is an **open, maintainer-authored** report of AD builds
generating wrong, rapidly-blowing-up flow solutions as a function of the
`fvSolution` linear solver. That is D460's family. **§9.4 has not been struck.** Its
"Not covered" list at **:293–:296** is also wrong in both directions: the venues it
names are now covered (mdolab mailing lists **do not exist**; CFD-Online, the
OpenFOAM forums, Google Scholar, `OpenFOAM-v1812-AD` and MeDiPack were all swept),
**and the venue that mattered — `DAFoam/OpenFOAM-AD` — was not on the list at all.**

**Quota, for the record, because it is the one blocker that IS closed.** The
full-protocol sweep now stands at **127 recorded searches across 18 venues** (17
read, 1 `BLOCKED`) with **11 controls**, against the house standard of 63 across
10. **Blocker 1 of the two named at :13–:15 is met and exceeded.**

---

### A5. What is STILL MISSING before Sanaa could file, if she chose to

**Numbered, each labelled zero-compute or needs-a-run. A "core-min class" below is
an order-of-magnitude class for triage and is NOT a registration, NOT a cost basis
and NOT an authorisation** — every run named here would need its own costed,
frozen, prediction-first pre-registration before anything launched
(`CLAUDE.md` rules 2 and 12). **Items 6, 7, 8 and 10 are named, not proposed for
launch.**

| # | what is missing | zero-compute or needs a run | class |
|---|---|---|---|
| **1** | **§9.4's novelty verdict (:291) is falsified and unstruck.** `OpenFOAM-AD` #2 is prior art of the family. Requires a dated addendum narrowing the sentence to *no prior report of this measurement* (liaison §5a item 1) | **zero-compute** | — |
| **2** | **§9.4's "not covered" list (:293–:296) is wrong in both directions** and must be struck (liaison §5a item 2) | **zero-compute** | — |
| **3** | **`mdolab/CMPLXFOIL` #28 is cited nowhere** (0 occurrences) and belongs in any filing as the merged mdolab precedent for the remedy | **zero-compute** | — |
| **4** | **§11's tone section (:321–:327) still frames a new-defect filing.** The filing is now "a second instance of your open #2, at the opposite polarity" (liaison §5a item 3) | **zero-compute** | — |
| **5** | **§7's sweep-1 design (:154–:162) is superseded and its "AD correctness" branch was unreachable by construction**; it needs striking with a pointer to the executed `smoothSolver` arm (liaison §5b) | **zero-compute** | — |
| **6** | **The control arm's library identity across the two rows is not established** (§A1.1). §4 proves md5 identity for `libDASolverADF.so`; the control loads `libDASolver.so`, and :89 says that is the family the images differ in | **needs a run** — two `docker run --rm … md5sum`, no solver, no mesh | **< 1 core-min class** |
| **7** | **No from-nothing reproducer bundle.** The house bar is D-A's `upstream_repro/run_repro.sh` (fresh clone of the official tutorials at a pinned commit, nothing-to-results in ~2 min); D-B records the same requirement as **NOT DONE**. D460 gives an invocation (**:132**) without the `runScript.py` it invokes, and a 41,760-cell lab-built mesh with no recipe a maintainer can run (**:51**) | **needs a run** — build the bundle and execute it end-to-end | **~10–50 core-min class** (sweep 1's two 10-iteration arms actually charged **4.717** core-min; mesh generation and a shakedown dominate) |
| **8** | **Scope is one case.** §10 item 2 stands: one solver, one mesh, np = 1. **Sweep 2 (case family, A1/A4) is UNRUN and UNAUTHORISED**, and neither sweep 1, ADDENDUM 1 nor this addendum authorises it | **needs a run** + its own costed pre-registration | **~10 core-min class** as §7 sketches at **:164** |
| **9** | **One novelty venue is `BLOCKED`** — OpenFOAM's own upstream tracker, and it is the venue nearest D460's mechanism claim (liaison §A6). Whether a `BLOCKED` venue blocks filing is **the supervisor's judgement and then Sanaa's, not this lane's** | **zero-compute to re-attempt**, but it may stay `BLOCKED` — a `BLOCKED` is recorded as `BLOCKED`, never as a zero | — |
| **10** | **Which build is right is untouched** (§10 item 4; ADDENDUM 1 item 2). Sweep 1 measured what the difference *does*, never which side of it is correct. **No arm for this has been designed**, so it is unpriced | **needs a run, undesigned** | **unpriced — no estimate is offered rather than a guessed one** |
| **11** | **§3's inferred mechanism is still an inference.** Sweep 1 removed the NaN but did **not** confirm the GAMG-amplification story — `r` fell mostly on the control's growth, and prediction **P5 MISSED and not narrowly** (the two builds' pressure-sweep counts ended **219 apart**, 206 vs 425, where *fewer* than the GAMG pair's 2 was registered) | **needs a run, undesigned** | **unpriced** |

**Items 1–5 and 9 are zero-compute and are six of the eleven.** They are also the
ones that matter most for a read, because each is a place where **this file
currently contradicts a committed sibling record of this lab**.

**Not on this list, deliberately:** §8's adjacent `-1e10` false-convergence finding
(**:183–:212**). It has a **clean-zero** novelty result in every venue swept
(`primalMinIters`, `primalMaxRes` and `-10000000000` are zeros in issues,
Discussions and GitHub-global alike), a one-condition fix, and §11 already says it
should not ride on the AD question. **Its readiness is a separate assessment and
this readiness state does not carry it.**

---

### A6. READINESS STATE

> ## READINESS STATE: **NOT READY**
>
> **Missing:** §A5 items **1, 2, 3, 4, 5** (zero-compute — the draft's own §9.4
> novelty verdict, its "not covered" list, the uncited `CMPLXFOIL` #28, §11's tone
> section, and §7's superseded sweep-1 design); item **6** (control-arm library
> identity, < 1 core-min class); items **7** and **8** (no from-nothing reproducer;
> scope is one case — both need runs and their own pre-registrations); item **9**
> (one `BLOCKED` venue, supervisor's judgement); items **10** and **11** (which
> build is right, and §3's mechanism — undesigned and unpriced).
>
> **The determining reason, in one sentence:** sweep 1 closed the *class* question
> and the full-protocol sweep closed the *quota* question, but **the draft's own
> §9.4 still asserts a novelty verdict that a committed sibling record of this lab
> has falsified**, and a note that contradicts its own lab's evidence is not a note
> to put in front of its owner.
>
> **The alternative state was `READY-FOR-SANAA'S-READ` and it was not reached. The
> phrase "ready to file" is not in this lab's vocabulary and is not used here.**

**What would change it.** §A5 items **1–5** are zero-compute and are entirely
within the supervisor's gift as dated addenda; landing them would leave items 6–11,
of which only 6 is cheap. **This lane does not rule on whether that would be
enough** — `READY-FOR-SANAA'S-READ` is a supervisor's call on a lane's assessment,
and the four §3 supervision checks are not delegable.

---

**Cost of this reassessment: ZERO compute.** No container was launched, no solver
run, no image pulled, no network request made. The work was `git show` at a single
captured HEAD, `grep`, `cmp` and this write.

**Nothing in this addendum has been sent, filed, posted, uploaded, registered or
commented, and nothing in it authorises or performs a send. The defect candidate
remains NOT FILED ANYWHERE. Filing is Sanaa's decision alone.**
