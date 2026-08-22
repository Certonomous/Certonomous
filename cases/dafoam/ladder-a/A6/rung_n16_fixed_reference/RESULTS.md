# A6 CRM wing-alone, rung N=16 (41,760 cells), np=1: FIXING THE FD REFERENCE — RESULTS

**Run 2026-08-22, DAFoam team LANE B.** Pre-registration: `PREREGISTRATION.md` in this directory,
committed **before any arm launched** (commit `8028d9ab`, subject *"dafoam team: A6 N=16 fixed FD
reference - pre-registration"*). **This file does not revise it.** Departures are recorded in §10
(Amendments), dated, and never by editing the frozen file.
**Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and is Sanaa's alone.**

**This is a PATCHED-IMAGE row** — `dafoam-idwarp-rot:v1`, image ID `2927768a16ac`,
`IDWARP_SO_MD5 85f59e87253e0a71a813f64ca6e4c425` asserted by every arm. It does not replace, merge
with, or re-grade the shipped-toolchain row at `../rung_n16_np1/RESULTS.md` §6.2. Two rows, never one.

---

## HEADLINE

**The item reached for the forward-AD reference that `DAFOAM_CHARTER.md` §2 says no lane had ever
reached for, found it, ran it — and measured why it cannot be used on this case as it stands.
The FD half is authorised by its own registered gate and is BLOCKED on host memory, not on physics.**

1. **Forward-mode AD is reachable in this image and this lane has now reached for it.**
   `libDASolverADF.so` ships, `DARhoSimpleCFoam` is compiled into it (**28 symbols**), the ADF Python
   binding imports, `IDWarp` exposes `warpDerivFwd`, and `DASolver.C:445` returns the **derivative**
   from `getTimeOpFuncVal` under `CODI_ADF` while `DASolver.C:376` prints an ` ADF-Deriv:` value on
   every objective line. Arm **s1b** ran it: `rc=0`, `EDIT4_ADD_DVGEO_OK path=coupling.solver`, and a
   finite `ADF-Deriv: -2.417306771789842e-05` for CD at iteration 1. **§4.**
2. **And the forward-AD build does not reproduce the plain build's primal on this case.** Same image,
   same mesh, same `daOptions`, cold start: the momentum equations are **bit-identical**, the energy
   equation diverges at the **8th significant figure** at iteration 1, the GAMG pressure solve stops
   at **5 sweeps instead of 7**, the cumulative continuity error is **10× worse**
   (`-0.05058272456310364` against `-0.00504349133910657`), CD at iteration 1 is **13.5% off**, and
   every state is **NaN within 10 iterations**. The returned derivative is `nan`. **§5.**
   **This is a measured, reproducible DAFoam finding that is not on any record in this lab, and it
   belongs to BOTH rows**: `libDASolverADF.so` is **md5-identical** (`44538ed4ac157ecb5dbb6850cf4bde64`)
   between `dafoam/opt-packages:latest` and `dafoam-idwarp-rot:v1`, so it is a statement about the
   **shipped** toolchain measured on the patched one.
3. **The registered FD gate PASSES on its own registered arithmetic** — with `η = 9.0085e-06`
   (recomputed here from the patched arm's own baseline primal, §3.2) three of the four subset
   components clear the `C ≥ 5` bar at `step = 3e-2`, so the fixed-step FD reference is authorised.
   **It was not bought: the host's `MemAvailable` fell to 8.7–11.5 GiB under another family's
   `viewFactorsGen` job (16.7 GiB RSS) and stayed below the registered 12 GiB floor. The arms are
   `BLOCKED`, priced, and named. No cap was raised to get past it.** **§6, §8.**
4. **Sanaa's N=29 gate is NOT met and is not moved by this item.** The A6 N=16 adjoint remains
   unverified except on `patchV` idx1 at 3.29%. **§9.**
5. **Zero-compute finding, from the predecessor's own log, that reframes the whole repair:** the N=16
   primal does not converge *slowly*, it is **flat**. `nuTilda initRes` sits within **±4%** of
   5.9e-06 from iteration 100 to 1000 and the all-equation maximum within **±5%** of 1.7e-05 from
   iteration 400. **"Converge harder" is very unlikely to be the repair, and the registered P1 says so
   in advance.** **§3.1.**

6. **The toolchain already ships two mechanisms for exactly this failure and nobody in this lab has
   used either.** `primalFuncStdTol {stdTol, slopeTol, funcNames, nStepsFrac}` — converge on the
   objective's standard deviation and slope instead of on a residual the primal never meets — and
   `useMeanStates`, whose own DAFoam comment reads *"can be useful when the primal solution exhibits
   LCO"*. Both default OFF (`-1.0`, `False`); both are absent from `cases/` and `docs/`. **They attack
   `η` itself, which is the only term in the noise floor `η/(2s)` that no step-size choice can
   touch — and it is the term that makes `twist` idx6 ungradeable at every step.** Not registered,
   therefore **not run**; costed and listed for Sanaa instead. **§3.4, §11.**

Raw logs: `/home/ubuntu/certonomous-runs/P3-a6-n16-ref/{s1b.log}`; ledger `.../ledger.txt`;
RSS samples `.../rss_s1b.txt`; queue `.../queue_stage1.out`.

---

## 1. Arms as executed

| arm | purpose | `endTime` | `primalMinResTolDiff` | rc | wall | core-min | peak RSS | status |
|---|---|---|---|---|---|---|---|---|
| **s1b/1** | fwd-AD probe, `patchV` idx1 | 10 | 1.0e12 | **1** | 26 s | 0.433 | 0.505 GiB | harness error (Edit 4 in `setup()`), §10 A2 |
| **s1b/2** | same, Edit 4 relocated | 10 | 1.0e12 | **0** | 78 s | 1.300 | 0.632 GiB | ran; spurious 2-iteration exit |
| **s1b/3** | same, `primalMinIters` raised | 10 | 1.0e12 | **0** | 323 s | 5.383 | 0.636 GiB | ran 10 iterations; **NaN**, §5 |
| **s1a** | primal probe, 6,000 iterations | 6000 | **1.0e2 (shipped default)** | — | — | 0 | — | **BLOCKED** on host memory |
| **s1d** | FD repeatability, 2 primals | 1000 | 1.0e4 | — | — | 0 | — | **BLOCKED** |
| **s1e** | fwd-AD, warm-started (staged) | 20 | 1.0e4 | — | — | 0 | — | **BLOCKED** |
| **s2b-pV / s2b-tw** | the FD reference + trivial baseline | 1000 | 1.0e4 | — | — | 0 | — | **BLOCKED**, gate PASSED |
| **s2a-\*** | fwd-AD reference, 4 seeds | 1000 | 1.0e4 | — | — | 0 | — | **BLOCKED**, gate not met (§5) |

**Assertions, mandatory per prereg §2, on every arm that ran.** `IDWARP_SO_MD5:
85f59e87253e0a71a813f64ca6e4c425` (**ASSERT_MD5 OK**), `transonicPCOption 1;`, `nProcs : 1`. No arm
is void on any of those grounds. **The staged `base/` is byte-identical to the predecessor's**:
`md5sum` on `runScript.py` → `0de915d21166a91a9a54b37ab11214cf` and on
`constant/polyMesh/points.gz` → `11b84f0de5fdf2d3e947fee8cea412a9`, equal on both trees.

**One registered assertion could NOT be applied, and saying so matters.** Prereg §2 makes the
cold-start proof a match of the first cumulative continuity error against the predecessor's
`-0.00504349133910657`. **The only arms that ran are forward-AD arms, and §5.2 shows the ADF build
changes that very number** (it reads `-0.05058272456310364`). So on s1b the assertion is not a
warm-start test at all — it is the finding. **No plain-build arm ran, so the cold-start assertion of
this item is untested, and no arm here is certified cold by it.** All arms ran on `dafoam-idwarp-rot:v1` at np=1 under
`--cpus=1 --memory=12g --rm`, foreground under `timeout`, with the **record-only** RSS watcher.

## 2. Costs — measured, against a registered 74.0 and a hard ceiling of 120.0

| item | core-min | note |
|---|---|---|
| pre-launch image inspection (`ls`/`nm`/`grep`/`import`, no solver) | **0.400** | registered at 0.4 in prereg §7; **HIT** |
| two `md5sum` inspections of `libDASolverADF.so` (§5.2) | **0.100** | unregistered, disclosed; buys the two-row identity result |
| source/option inspections for §3.4, §5.1, §11 (`grep`/`sed`/`nm` in the image, no solver) | **0.150** | unregistered, disclosed |
| s1b/1 | **0.433** | waste — harness error, §10 A2 |
| s1b/2 | **1.300** | waste — spurious exit, §5.1 |
| s1b/3 | **5.383** | the measurement of §5; **not** waste |
| **TOTAL SPENT** | **7.766** | **6.5% of the 120 core-min ceiling** |
| arms BLOCKED and not spent | **60.3** | s1a 8.5, s1d 3.2, s1e ~3.0, s2b-pV 7.9, s2b-tw 19.3, s2a ×4 18.4 |

**Cost at \$0.0513/core-hour: 7.766 core-min = 0.1294 core-h = \$0.0066.** Of that, **1.733 core-min
(22.5%, \$0.0015) is waste** — one harness error and one arm that exited on a mechanism nobody had
recorded. **The registered ceiling was not reached; the item stopped on the host, not on money.**

**Billing basis, and a simplification the departure produced.** Prereg §7 quoted core-minutes at
`ranks × wall` (np=1) and disclosed that `COMPUTE_BUDGET_CHARTER.md`'s "cores × wall" convention read
against a `--cpus=4` cap would multiply every figure by 4. **Amendment 1 dropped the cap to
`--cpus=1`, so the two readings now coincide and the ambiguity is gone.** Every figure above is both
`ranks × wall` and `cores × wall`.

**Contention, disclosed because it is billed.** Every arm ran at host `load average` 20–24 against a
16-core box, driven by another family's `buoyantBoussinesq*`/`buoyantSimpleFoam`/`viewFactorsGen`
jobs. `s1b/2` and `s1b/3` share ~78 s of identical setup work; the arithmetic in §5.2 uses that
figure and is therefore contention-inclusive on both sides, which is the comparison that matters.

## 3. What was measured at zero compute, before any arm ran

### 3.1 The primal is flat, not slow — and this is why P1 was registered predicting a gate FAIL

From `/home/ubuntu/certonomous-runs/P2-a6-n16/stock.log`, the predecessor's own graded arm, at **zero
new compute** (prereg §0, §1.1). `nuTilda initRes` — the equation that sets `primalMaxRes` — over the
baseline primal:

| iter | 1 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 1000 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `nuTilda initRes` | 1.00 | 6.014e-6 | 5.629e-6 | 5.482e-6 | 5.778e-6 | 5.566e-6 | 5.708e-6 | 5.647e-6 | 5.742e-6 | 5.687e-6 | 5.909e-6 |
| all-eqn max | 1.00 | 1.161e-2 | 5.488e-4 | 4.058e-5 | 1.881e-5 | 1.629e-5 | 1.654e-5 | 1.734e-5 | 1.602e-5 | 1.607e-5 | 1.692e-5 |

**±4% over 900 iterations on the first row, ±5% over 600 on the second. This is a residual limit
cycle, not slow convergence.** It is the DAFoam instance of `VERIFICATION_CHARTER.md` §7's caution
*"do not prescribe 'converge harder' before checking whether convergence is available"*, and of A5's
measured case where tightening tolerances and running 10× longer moved the aggregate 46.64% → 46.21%
and made the sign flips **worse**.

### 3.2 `η` recomputed independently, and a sampling limitation nobody had stated

The predecessor's noise figure is **9.00e-6**. Recomputed here from the **patched** arm's own baseline
primal (`patched.log`, `Running Primal Solver 001`), independently of the predecessor's arithmetic:

```
last-200 CD samples: 0.03505666073433948 (t=800), 0.03505448562063092 (t=900), 0.03506349413916734 (t=1000)
p2p = 9.008518536419985e-06
```

**Confirmed to three significant figures. But the measurement rests on THREE samples**, because
DAFoam's `printInterval` defaults to 100 and the objective is printed only every 100th iteration.
**A three-sample peak-to-peak is a lower bound on the true wobble**, and no record has said so. Arm
s1a was staged with `printInterval 10` (numerically inert — `DASolver.C:124` calls
`calcAllFunctions(printToScreen_)` every iteration and the flag controls only the `Info` output) to
resolve the wobble 10× more densely at zero extra compute. **It did not run. The limitation stands
and `η = 9.0085e-06` is used below as a lower bound, which makes every clearance figure an UPPER
bound — stated so the gate is not read as stronger than it is.**

### 3.3 The predecessor's adjoint column, re-read from the raw log rather than from its table

Prereg §9.8 said the transcription is checkable; it has been checked, against
`/home/ubuntu/certonomous-runs/P2-a6-n16/patched.log:5008-5021`:

```
Raw Analytic Derivative (Jfor)
[[-0.0021009  -0.00175073 -0.00146945 -0.00101098 -0.0006277  -0.00037973 -0.00013619]]
Raw FD Derivative (Jfd)
[[ 0.00087282 -0.00413086 -0.00458151  0.00170351 -0.00146185 -0.00386132  0.00259113]]
```
and `:4995-5006` for `patchV`: `Jfor [[0.0007334 0.00901684]]`, `Jfd [[0.00426041 0.0087296]]`.
**The predecessor's §6.1 table is correct.** One limitation it does not state: OpenMDAO prints these
arrays at numpy's default **6 significant figures**, which caps any grading against them at about
that precision. Irrelevant at the percent level; relevant if a future arm claims agreement to more.

### 3.4 The toolchain already ships two mechanisms for exactly this failure, and nobody in this lab has used either

Read out of `pyDAFoam.py` in the image, at zero compute, while diagnosing §5.1's exit condition:

```
pyDAFoam.py:91   self.primalFuncStdTol = {"stdTol": -1.0, "slopeTol": -1.0,
                                          "funcNames": ["CD"], "nStepsFrac": 0.2}
pyDAFoam.py:83-90  "The case is converged only if both stdTol and slopeTol is lower than the
                    prescribed values ... nStepsFrac: the fraction of elapsed iterations to use
                    as the std window, here 0.2 means we always use the last 20% of elapsed
                    iterations to compute the std"

pyDAFoam.py:486  self.useMeanStates = False
pyDAFoam.py:483-485  "whether to use step-averaged state variables. This can be useful when the
                      primal solution exhibits LCO."
```

and the exit condition of `DASolver::loop` (`DASolver.C:188`) already carries the second branch —
`(funcStd_ < primalFuncStdTol_ && fabs(funcSlope_) < primalFuncSlopeTol_)` — beside the residual one,
with `calcAllFunctions` printing ` std: ` and ` slope: ` when it is enabled (`DASolver.C:365-372`).
`DASolver::getTimeOpRange` supports a `timeOp: "average"` function with its own `nStepsFrac`.
`useMeanStates` is wired end to end: `mphys_dafoam.py:349-350` calls `DASolver.solver.meanStatesToStates()`
after the primal and before the functions are evaluated, and `DASolver.C:4210-4230` copies each
`<state>Mean` field over its state — so the mechanism needs a `fieldAverage` function object declared
in `system/controlDict` for every state (`U p T nuTilda phi`) and nothing else. **The recipe is two
edits and neither of them touches a derivative.**

**A6 N=16 is a limit cycle (§3.1), and DAFoam's own comment uses the word LCO for the condition these
options exist to handle. Both are OFF by default (`-1.0`, `False`), and a grep of `cases/` and `docs/`
finds them nowhere.** This item did not buy them — they are not registered in `PREREGISTRATION.md` and
are **not** run here, because a preregistration is not amended by a good idea found mid-run. **They are
the most promising untried repair for this rung's FD reference and they go to Sanaa's desk (§11) with a
price, not into an arm.** The reason they are promising is arithmetic, not enthusiasm: the FD noise
floor is `η/(2s)`, `η` is the objective's limit-cycle amplitude, and `useMeanStates` attacks `η`
directly — the one term in that expression that no step-size choice can touch, and the term that
makes `twist` idx6 ungradeable at every step (§6.2).

## 4. P4 — forward-AD reachability. **Reached for, and it RUNS.**

`DAFOAM_CHARTER.md` §2: *"where a complex-step or forward-AD reference is available, it is the
reference … A record that reports only an FD table where a forward-AD or complex-step reference was
reachable states that it did not reach for it, and why. **No lane has yet done this.**"*

**Measured in `dafoam-idwarp-rot:v1`, at zero compute (four inspection commands):**

| probe | result |
|---|---|
| `find / -name "libDASolverAD*.so"` | `/home/dafoamuser/dafoam/OpenFOAM/sharedLibs/libDASolverADF.so` (9,534,464 B), `…ADR.so` (11,415,712 B) |
| `nm -D --defined-only libDASolverADF.so \| c++filt \| grep -c DARhoSimpleCFoam` | **28**, incl. `DARhoSimpleCFoam::solvePrimal()`, `::initSolver()` |
| `from dafoam.libs.ADF.pyDASolvers import pyDASolvers` | imports; **67** methods |
| `dir(idwarp.USMesh)` | `warpDeriv`, **`warpDerivFwd`**, `verifyWarpDeriv` |

**And measured by arm s1b/3, which ran:** `rc=0`; `EDIT4_ADD_DVGEO_OK path=coupling.solver`;
`CD: 0.01835565832247826 final: 0.01835565832247826 ADF-Deriv: -2.417306771789842e-05` and
`CL: … ADF-Deriv: -0.0003198438322461133` at iteration 1. **The forward-AD tape is live, the seed
reaches the objective, and the derivative comes back out.**

**P4a, graded against its three registered clauses:**

| registered clause | measured | outcome |
|---|---|---|
| `rc=0` | 0 | **HIT** |
| an ` ADF-Deriv:` value printed on the CD line | printed, finite, non-zero | **HIT** |
| `prob.get_val` returning a **finite** non-zero number | **`nan`** | **MISS** |

**P4a is MISSED on the clause that mattered, and the prediction was specific enough to catch it.**
The registered falsifier list named an `ImportError`, a `calcFFD2XvSeeds` error, a missing
`ADF-Deriv:` line, a returned `0.0`, and the `mphys` forward-mode warning path. **It did not name
`nan`, and `nan` is what happened** — recorded as a gap in the prediction, not smoothed over.

**P4b (`twist` idx0, the warp-crossing seed) is NOT EVALUATED.** Arm s1c is staged and was not
launched. What s1b **does** establish for it is that registered Edit 4 works: `add_dvgeo` is reachable
at `scenario1.coupling.solver` and returns cleanly. The `calcFFD2XvSeeds` →
`DVGeo.totalSensitivityProd` → `IDWarp.warpDerivFwd` chain is **untested**.

## 5. Why the forward-AD reference could not be used, measured rather than guessed

### 5.1 A spurious two-iteration exit, and the mechanism, from the source

Arm s1b/2 stopped after 2 iterations printing
`Minimal residual -10000000000 satisfied the prescribed tolerance 1e-08`. The mechanism is
`DASolver::loop`, `src/adjoint/DASolver/DASolver.C:188`:

```
if ((daGlobalVarPtr_->primalMaxRes < primalMinResTol_ || (...)) && runTime.timeIndex() > primalMinIters_)
```
with `primalMaxRes` re-initialised to `-1e10` at the bottom of the same function (`:222`) and
`primalMinIters` defaulting to **1** (`pyDAFoam.py:639`). **`-1e10 < 1e-8` is true**, so the guard is
the iteration counter alone. Raising `primalMinIters` to 1e6 in s1b/3 removed the early exit and the
arm ran its full 10 iterations. **A DAFoam run can print "satisfied the prescribed tolerance" while
having satisfied nothing, and `-10000000000` in that line is the tell.** This is a diagnosability
finding of the same class as the already-recorded **D-C** (`KSPSetFromOptions` silently discarded).

### 5.2 The ADF build does not reproduce the plain build's primal. Iteration 1, side by side.

Same image, same mesh, same `daOptions`, both cold from a pristine `base/`. Plain figures from
`P2-a6-n16/patched.log:528-542`; ADF from `P3-a6-n16-ref/s1b.log:528-542`.

| quantity, iteration 1 | plain (reverse-mode build) | **forward-AD (ADF) build** | |
|---|---|---|---|
| `U0 initRes` / `finalRes` | 0.9999999999999988 / 0.07283048716260687 | identical / identical | **bit-identical** |
| `U1 finalRes`, `U2 finalRes` | 0.003381492464613624 / 0.07283327010584476 | identical / identical | **bit-identical** |
| `he initRes` | 0.9999999999746546 | 0.9999999999746546 | bit-identical |
| **`he finalRes`** | **0.06128002514528321** | **0.06128001402295498** | **differs at the 8th s.f.** |
| **`p finalRes` / `nIters`** | **0.08186984767127925 / 7** | **0.07694766099874849 / 5** | **2 fewer GAMG sweeps** |
| **continuity, global** | **-0.00504349133910657** | **-0.05058272456310364** | **10.0× worse** |
| **CD** | **0.02122521539888314** | **0.01835565832247826** | **13.5% low** |
| by iteration 10 | (runs to 1,000) | **every state NaN** | — |

**The reading, with its uncertainty stated.** What is *measured* is the table. What is *inferred* is
the chain: the momentum equations are bit-identical, so the divergence enters at the **energy
equation** at the 8th significant figure — the round-off signature of arithmetic performed on CoDiPack's
forward type rather than on a bare `double`. That perturbation is then **amplified** by the pressure
solve, which is `GAMG` with `relTol 0.1, tolerance 0` (`base/system/fvSolution`): a relative-tolerance
stopping rule crosses its threshold one V-cycle earlier, delivers a 6% larger `finalRes`, and leaves a
continuity error **ten times** larger. On a transonic cold start that is enough, and the run reaches
NaN inside ten iterations. **A tighter statement than "forward AD is broken" is not supported by one
arm, and is not made.**

**And this finding is NOT a patched-row finding — it belongs to BOTH rows.** `libDASolverADF.so` is
**md5-identical between the shipped and the patched image**:

```
$ docker run --rm dafoam/opt-packages:latest  md5sum .../sharedLibs/libDASolverADF.so
44538ed4ac157ecb5dbb6850cf4bde64
$ docker run --rm dafoam-idwarp-rot:v1        md5sum .../sharedLibs/libDASolverADF.so
44538ed4ac157ecb5dbb6850cf4bde64
```

The three images differ only in `DALinearEqn.C` and its rebuilt library
(`TOOLCHAIN_INVENTORY.md` §3), and the IDWarp rotation patch is a different library again. **The
forward-AD build is byte-identical across the toolchain, so §5.2 is a statement about the SHIPPED
DAFoam and this item's patched row carries it without needing a shipped arm to say so.**
`DAFOAM_CHARTER.md` §6 wants two rows; here the identity hash makes one measurement serve both, and
the hash is what licenses that — not a version string.

**Two consequences that ARE supported.**
* **The 27 s/iteration figure for the ADF build is NOT a cost measurement and is not reported as one.**
  s1b/3 spent ~245 s on 9 iterations, but those iterations were operating on NaN, where GAMG's
  convergence test can never succeed and the solver runs to its iteration limit. **P5 (the ADF cost
  factor, predicted 2.0–4.0×) is NOT EVALUATED.** The one clean comparison available —
  `ExecutionTime` at iteration 1, 4.98 s (ADF) against 4.67 s (plain) — is dominated by solver
  construction and is not a per-iteration factor either.
* **The repair is warm-starting, and it is staged.** Arm s1e was staged with the converged fields from
  `P2-a6-n16/patched/1000/` written into `0/` (fields only — `polyMesh` deliberately **not** copied,
  since that directory holds a perturbed design's deformed mesh), `endTime 20`, `printInterval 1`.
  Starting the tangent at the attractor avoids the cold transient that reaches NaN, **and it is the
  right state for a tangent reference anyway, because it is the state the stored adjoint was
  linearised about.** **It did not run** — §6.2.

### 5.3 Gate B-AD — **NOT MET**, on the evidence available

Prereg §6 Gate B-AD: *"passes iff at least one of S1b/S1c returned `rc=0` with a finite non-zero
` ADF-Deriv:` for CD."* s1b returned `rc=0` and a finite non-zero ADF-Deriv **at iteration 1**, and a
`nan` at the end. **Read against the purpose the gate was written for — enabling a forward-AD
*reference* — it is NOT MET.** Reading it as met on the iteration-1 value would be choosing the
reading after seeing the number, which `DAFOAM_CHARTER.md` §8 names as the `GATE REACHED` misuse.
**The honest verdict is that Gate B-AD is not met by a cold-started ADF primal, and is UNDECIDED for a
warm-started one.**

## 6. The Stage-2 gate, evaluated as written

### 6.1 Branch selection — **UNDECIDED**, because s1a did not run

Prereg §6 Branch A/B turns on P1. **s1a was BLOCKED**, so P1 is **NOT EVALUATED** and the branch is
formally undecided. §3.1's zero-compute trace is *evidence* for Branch B and is not a substitute for
the arm; it is not scored as a HIT.

### 6.2 Gate B-FD — **PASSES on its own registered arithmetic**

The rule (prereg §4.2(b)) with `η = 9.0085e-06` (§3.2, a lower bound) and the patched adjoint
magnitudes of §3.3, using `|J_adj|` as the registered proxy for `|J_fd|`:

| step `s` | floor `η/2s` | `twist` 0 | `twist` 3 | `twist` 6 | `patchV` 1 |
|---|---|---|---|---|---|
| 1e-3 (predecessor's) | 4.504e-3 | 0.466× | 0.224× | 0.030× | 2.00× |
| 1e-2 | 4.504e-4 | 4.66× | 2.24× | 0.302× | **20.0×** |
| 3e-2 | 1.501e-4 | **14.0×** | **6.73×** | 0.907× | **60.1×** |
| 1e-1 (`twist` only) | 4.504e-5 | **46.6×** | **22.4×** | 3.02× | — |

**Three of four components clear `C ≥ 5`. The registered gate required two. Gate B-FD PASSES**, and
the registered fail condition (`η > 8.0e-5`) is 8.9× away from the measured value.

**And the registered prediction P8's hardest clause is confirmed by arithmetic before any arm runs:
`twist` idx6 reaches a maximum clearance of 3.02× at `s = 1e-1` and NEVER reaches 5×.**
**FD cannot grade `twist` idx6 on this rung at any registered step.** Its only possible reference is a
non-FD one. That is `DAFOAM_CHARTER.md` §2 arriving as an operational necessity rather than as advice,
and it is the single most useful sentence this item produced — **and forward AD, the only instrument
that could have supplied it, is the one §5 shows does not run cleanly on this case.**

### 6.3 Why the authorised FD arms were not bought — **BLOCKED on host memory, and no cap was raised**

The registered launch condition (prereg §8) is `load1 ≤ 8` **and** `MemAvailable ≥ 12 GiB`, bounded
loop, 40 minutes. Amendment 1 (§10) departs on the **load** half under supervisor direction. The
**memory** half was explicitly re-affirmed by the supervisor and **was not departed from.**

Measured host state across the launch window: `MemAvailable` **8.7–11.5 GiB, never reaching 12**, held down by another
family's `viewFactorsGen` at **16.7 GiB RSS**; `load average` 20–24. The preflight loop polled and
declined. **Per prereg §8 and `DAFOAM_CHARTER.md` §7 — "a stop is not a measurement" — the arms are
recorded `BLOCKED`, priced in §2, and claim nothing.**

**A departure to a 6 GiB floor was requested from the supervisor and could not be delivered (no
reachable session). It is carried to Sanaa's desk in §11 instead of being taken unilaterally.**
The evidence for it, since it will be asked for: **every arm in this item is primal-only** — no
adjoint is computed anywhere, the adjoint column being inherited from the predecessor's converged run
— and the measured peaks are **0.636 GiB** (s1b, with *two* solver instances live) against a
predecessor primal-phase peak of **3.197 GiB** and an *adjoint* peak of 9.787 GiB. **The 12 GiB floor
was calibrated on adjoint arms and is roughly 3× what these arms need.**

## 7. Predictions, scored honestly

| # | registered | measured | outcome |
|---|---|---|---|
| **P1** | primal stagnates at 6,000 iters; gate FAILS | arm BLOCKED | **NOT EVALUATED** |
| **P2** | wobble at 6,000 in [3e-6, 1.5e-5] | arm BLOCKED | **NOT EVALUATED** |
| **P3** | `δ_repeat` in [1e-7, 2e-5] | arm BLOCKED | **NOT EVALUATED** |
| **P4a** | fwd-AD `patchV`: rc=0 **+** ADF-Deriv printed **+** finite non-zero `get_val` | rc=0 ✓, ADF-Deriv ✓, `get_val` = **nan** ✗ | **MISS** (2 of 3 clauses) |
| **P4b** | fwd-AD `twist` idx0 runs | arm BLOCKED; Edit 4 itself validated | **NOT EVALUATED** |
| **P5** | ADF cost factor 2.0–4.0× | only NaN-contaminated timings exist | **NOT EVALUATED** |
| **P6** | fwd-AD vs adjoint ≤1% on all four | no usable reference | **NOT EVALUATED** |
| **P7** | tangent relative p2p in [1e-4, 1e-1] | no usable tangent | **NOT EVALUATED** |
| **P8** | `twist` 0/3 recover sign; **`twist` 6 flagged at every step**; `patchV` 1 ≤5% | the `twist` 6 clause is **CONFIRMED BY ARITHMETIC** (max 3.02×, §6.2); the rest need the arms | **PARTIAL** — one clause established, three NOT EVALUATED |
| **P9** | trivial baseline at 1e-8 > 50% | arm BLOCKED | **NOT EVALUATED** — the predecessor's `PENDING` is **NOT** closed |
| **P-RSS** | ≤4.5 GiB primal / ≤8.0 GiB fwd-AD; ceiling 12 GiB | **0.636 GiB** on the only arm class measured | **consistent, not confirmed** (10-iteration run) |
| **P-COST** | 74.0 core-min registered, ceiling 120 | **7.516** spent | **HIT** on the ceiling; the registered total was not reached because the item was blocked |

**One prediction MISSED, one PARTIAL, one HIT, nine NOT EVALUATED.** The registered falsifier lists
did their job on P4a — the prediction was written specifically enough that a `nan` counts as a miss
rather than as a caveat — and failed to anticipate `nan` as a *mode*, which is recorded as a defect in
the prediction rather than in the run.

## 8. Verdicts

| item | verdict |
|---|---|
| forward-mode AD **reachable** in `dafoam-idwarp-rot:v1` and reached for | **PASS** — Charter §2's clause discharged for the first time in this lane |
| forward-mode AD **usable** as a reference on A6 N=16 as configured | **GATE FAIL** — the ADF primal reaches NaN in 10 cold iterations (§5.2) |
| Gate B-FD (fixed-step FD reference authorised) | **PASS** — 3 of 4 components clear `C ≥ 5`, gate required 2 |
| the fixed-step FD reference itself | **BLOCKED** — host `MemAvailable` 8.7–11.5 GiB against a registered 12 GiB floor |
| forward-AD reference on the four-component subset | **BLOCKED** — gate B-AD not met; warm-start repair staged, not run |
| P9 trivial baseline (inherited from the predecessor) | **PENDING** — still not run, still not absorbed |
| `twist` idx6 is FD-ungradeable on this rung at every registered step | **PASS** (established by the registered arithmetic, §6.2) |
| **the item as a whole** | **BLOCKED** |

**`BLOCKED`, not `GATE FAIL`.** The physics gate the item registered passed; the host is what stopped
it. Per prereg §10 an arm stopped by the launch condition is `BLOCKED` and never `GATE FAIL`, and per
`DAFOAM_CHARTER.md` §7 a stop is not a measurement.

## 9. Sanaa's N=29 gate — **STILL NOT MET, and this item does not move it**

The predecessor's condition, as held: **N=29 is approved only if N=16 passes on the patched image.**
N=16 does not pass. The reason it does not pass is the FD reference, and **this item did not fix the
FD reference** — it authorised the fix, priced it, and was blocked before buying it.

**The adjoint is still unverified except on `patchV` idx1 at 3.29%.** Nothing here changes the eight
failing components or the three sign flips. **N=29 remains NOT RUN.** No N=29 arm was launched, staged
or queued, and no compute was spent on it.

**What this item adds to the decision, and it is not nothing:** the repair path is now costed, gated
and partly de-risked — the FD half is authorised by measured arithmetic and needs **27.2 core-min**
(\$0.023); the forward-AD half needs a warm-start fix that is staged and unproven; and one component
(`twist` idx6, the wing tip) is now known to be **outside FD's reach at any step**, so a fully graded
N=16 requires a non-FD reference or an honest permanent exclusion by name.

## 10. Amendments — departures from the frozen pre-registration, dated

**Amendment 1 (2026-08-22, ~18:10Z) — launch-condition departure, on supervisor direction.**
Prereg §8 registers `load1 ≤ 8`. The supervisor directed that the registered cap was derived from the
Open-MPI spin-wait mechanism measured on **np=4** arms, which is absent at np=1, and authorised
launching at load ~22 with **`--cpus=1`** (tightened from the registered `--cpus=4`, so the arms never
take more than one core from the T-family spine), `--memory=12g` unchanged, and the `MemAvailable ≥
12 GiB` half of the condition **unchanged and still required**. Expected clock inflation ≤1.3×.
Implemented as `LOADCAP=60` on the preflight loop. **Measured consequence:** every arm ran at load
20–24; the cost basis simplification is in §2. **The memory half was never departed from** (§6.3).

**Amendment 2 (2026-08-22, ~18:12Z) — registered Edit 4 relocated from `setup()` to `configure()`.**
Prereg §3 Edit 4 registers one line, `self.scenario1.coupling.solver.add_dvgeo(self.geometry.DVGeo)`.
Placed in `Top.setup()` it raises `AttributeError: 'ScenarioAerodynamic' object has no attribute
'coupling'`, because mphys builds the `coupling` subgroup inside the scenario's **own** setup, after
`Top.setup()` has run (`mphys/scenario_aerodynamic.py:_mphys_scenario_setup`). Moved to `configure()`
with a two-path lookup and an `EDIT4_ADD_DVGEO_OK` assertion print. **Cost of the error: 0.433
core-min (arm s1b/1), recorded as waste in §2.** The line itself is unchanged.

**Amendment 3 (2026-08-22, ~18:15Z) — `primalMinResTolDiff 1.0e12` on the 10-iteration probes only.**
Prereg §4.1 registers `1.0e4` for s1b/s1c. At 10 iterations no residual tolerance can be met, so
`checkPrimalFailure()` fires regardless and Gate B-AD's `rc=0` clause would have been unreachable **by
construction** — the same defect shape as the predecessor's P3 CL clause. Raised to `1.0e12` for the
two probes so the gate could be evaluated as written. **It affects no derivative**: the value gates
only a post-hoc acceptance test. **All Stage-2 measurement arms remain at the registered `1.0e4`.**

**Amendment 4 (2026-08-22, ~18:19Z) — `primalMinIters` raised to 1e6 on the ADF probes.**
Not registered anywhere. Required by the mechanism in §5.1: with `primalMaxRes` reset to `-1e10` each
iteration and `primalMinIters` defaulting to 1, the ADF primal exits after two iterations claiming it
"satisfied the prescribed tolerance". **It affects no derivative**; it removes a spurious stop.
Disclosed rather than absorbed, because a raised iteration floor is exactly the class of edit the
predecessor's §7.2 warned about inheriting silently.

**Amendment 5 (2026-08-22, ~18:33Z) — `printInterval 10` staged on s1a.**
Prereg §3 registers no `printInterval`. The default of 100 is why `η` rests on three samples (§3.2).
`DASolver.C:124` calls `calcAllFunctions(printToScreen_)` **every** iteration and the flag controls
only the `Info` output, so the change is numerically inert and buys a 10× denser wobble measurement at
zero compute. **s1a did not run; the amendment is recorded because the arm is staged and the next
holder of this item will find it in the tree.**

**Amendment 6 (2026-08-22, ~18:36Z) — s1e warm-started from a non-pristine state.**
Prereg §2 mandates a cold start from `base/` with an asserted continuity error. Arm s1e departs: the
six field files from `P2-a6-n16/patched/1000/` are written into `s1e/0/`. Justification in §5.2 —
the tangent must be evaluated at the state the adjoint was linearised about, and the cold transient is
what reaches NaN. `polyMesh` was deliberately **not** copied, because that directory carries the
deformed mesh of a perturbed design. **s1e did not run.** Any future use of it must assert that the
ADF primal's converged CD matches the plain build's `0.03506349413916734`, or the ADF derivative is of
a different function.

**Amendment 7 (2026-08-22, ~18:38Z) — arm ordering within Stage 1.**
Prereg §4.3 registers `S1a → S1b → S1c → S1d → …` as a **priority** order governing what is dropped at
the ceiling. The forward-AD probes were run first, because they are 90-second arms that de-risk the
item's largest unknown and nothing in Stage 1 depends on order. **No arm was dropped by this and the
priority order was preserved for the queue that followed.**

## 11. What this item cannot see, and what goes to Sanaa's desk

**Prereg §9's eight limitations stand unchanged and unweakened.** Three more, created by this run:

9. **It cannot say whether forward AD would work on this case warm-started.** s1e is staged and unrun.
   One cold arm is not a verdict on the instrument, and §5.2 deliberately stops short of one.
10. **It cannot say what a forward-AD reference would cost.** The only ADF timings on the record are
    NaN-contaminated (§5.2).
11. **It cannot say whether the ADF/plain divergence is specific to `GAMG`, to the transonic solver, to
    a cold start, or general.** The mechanism in §5.2 is an inference from one arm. A `PBiCGStab`
    pressure arm would discriminate it and was not run.

**For Sanaa's desk, priced, with the discriminating outcome, and none of it taken:**

| item | price | what it decides |
|---|---|---|
| **Departure to `MemAvailable ≥ 6 GiB`** for primal-only arms | \$0 | Unblocks everything below. Evidence in §6.3: measured peaks 0.636 GiB (fwd-AD, two solvers) and 3.197 GiB (primal phase) against a floor calibrated on a 9.787 GiB **adjoint**. |
| s2b-pV + s2b-tw — **the fixed-step FD reference**, gate already PASSED | **27.2 core-min, \$0.023** | Whether `twist` idx0/idx3's sign flips are FD noise or a real adjoint defect — the question the predecessor's GATE FAIL left open, and the input to the N=29 decision. Includes the inherited **P9 trivial baseline**. |
| s1a + s1d — the primal-convergence gate and `δ_repeat` | **11.7 core-min, \$0.010** | Whether `η` is 9.0e-6 or larger, i.e. whether the clearance table in §6.2 is right; and whether "converge harder" is available at all. |
| s1e — warm-started forward-AD probe | **~3 core-min, \$0.003** | Whether a forward-AD reference exists on this case at all. **The only instrument that can grade `twist` idx6.** |
| a `PBiCGStab`-pressure ADF arm | **~5 core-min, \$0.004** | Whether §5.2's GAMG-amplification mechanism is the cause. Would make the finding filing-ready. |
| **`useMeanStates: True` + `function-fieldAverage`, one primal + one re-differenced FD pair** (§3.4) | **~4 core-min, \$0.003** | **Whether `η` itself can be reduced.** This is the only lever that reaches `twist` idx6, because clearance is `\|J\|·2s/η` and no `s` in the feasible window rescues it. If `η` drops one decade, every one of the nine components the predecessor GATE FAILed becomes gradeable at `s = 1e-2`. |
| `primalFuncStdTol {stdTol, slopeTol}` as the convergence criterion (§3.4) | **~2 core-min, \$0.002** | Whether A6's primal can be declared converged **honestly** — on objective stationarity rather than on a residual it never meets — which would retire the `primalMinResTolDiff 1e4` widening the predecessor's §7.2 warned about, rather than inheriting it forever. |
| **Total to finish this item** | **~53 core-min, \$0.045** | inside the registered 120 core-min ceiling with 59 core-min to spare |

**A prepared defect note is NOT written and NOT filed.** §5.1 (a DAFoam run printing *"satisfied the
prescribed tolerance"* with `primalMaxRes = -1e10`) and §5.2 (the ADF build not reproducing the plain
build's primal) are both candidate upstream items of the **diagnosability** and **AD-correctness**
classes respectively. Per `DAFOAM_CHARTER.md` §10, preparing a report is work an agent does and filing
it is a decision only Sanaa takes. **Nothing has been filed, sent, uploaded or pushed.**
