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

**THE FD REFERENCE IS FIXED, AND IT CLEARS THE ADJOINT.** All three of the predecessor's sign flips
were finite-difference noise: at a step sized from the measured wobble every one of them reverses back
to the adjoint's sign, and the graded subset agrees to **1.0099%** where the predecessor read
57–341%. Three independent instruments — reverse-mode adjoint, central FD, forward-mode AD — close on
`patchV` idx1 to within **1.53%**. The A6 N=16 adjoint is **VERIFIED on three of the four components
graded**, and `twist` idx6 is **FLAGGED** exactly as predicted before the run.

0. **THE GRADE: PASS.** Graded subset `patchV` 1 → **0.940%**, `twist` 0 → **1.706%**, `twist` 3 →
   **1.817%**; vector-relative error over the graded subset **1.0099%**; **zero sign flips**;
   `twist` idx6 flagged and excluded by name. Against the predecessor's **GATE FAIL** on the same
   components — 3.29%, 341.51%, 159.35%, 105.26%, three of them sign-flipped. **§6.8.**

0b. **The calibration triangle closes.** `patchV` idx1: adjoint
   `9.016840e-03`; central FD at step 1e-2 `8.984509e-03` (**0.359%**); at the registered graded step
   3e-2 `8.932878e-03` (**0.931%**); forward-mode AD `9.070934e-03` (**0.600%**). **Spread 1.534% of
   the mean across three instruments that share no code path below the objective.** Against the
   predecessor's single-instrument **3.2904%** at a step whose clearance was 1.60×. **§6.4, §6.7.**
   **And the forward-AD tangent was converging monotonically ONTO the adjoint — 11.4 → 8.0 → 4.5 →
   1.55 → 0.60% over iterations 9–13 — when the ADF primal blew up at iteration 14. §6.6.**

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
3. **"Converge harder" is not available on this case, and that is now measured, not argued.**
   Arm **s1a** ran 6,000 iterations with DAFoam's convergence guard at its **shipped default**.
   `primalMaxRes` went from 5.909e-06 at 1,000 to **5.6999e-06 at 6,000 — a 3.5% improvement for 6×
   the compute** — the string `satisfied the prescribed tolerance` appears **zero** times, and the
   guard correctly refused the run (`rc=1`). **P1 HIT on all three clauses; P2 HIT.** The objective's
   wobble does not even decay monotonically: it **rises 57%** from 1,000 to 2,000 before falling, and
   ends only **1.8× better** than at 1,000. **§3.5.**
4. **A predecessor number is OVERTURNED, and the cause is sampling.** The N=16 record's noise figure
   `η = 9.00e-06` rests on **three** CD samples, because `printInterval` defaults to 100. Resolved at
   `printInterval 10` — numerically inert, zero extra compute — the same window reads
   **`η = 1.0910e-05`, 21% larger.** Every clearance derived from it was 21% optimistic. **The
   predecessor's conclusion is strengthened, not weakened: more of its FD column is noise-dominated
   than it claimed.** The frozen file is not edited; the correction lives here. **§3.2 NOTE.**
5. **The registered FD gate PASSES on the MEASURED noise** — `twist` 0 at **11.55×**, `twist` 3 at
   **5.56×**, `patchV` 1 at **49.59×** at `step = 3e-2`, three of four clearing the `C ≥ 5` bar the
   gate required two of. **And `twist` idx6 tops out at 2.50× and never clears at any registered
   step: FD structurally cannot grade the wing-tip twist component on this rung.** **§6.2.**
6. **The registered trivial baseline fired.** The inherited `step = 1e-8` arm the predecessor left
   `PENDING` returns **152.94** against an adjoint of `9.017e-03` — **99.9941%**, registered as >50%.
   The same harness that returns 0.36% at a well-clearing step returns 99.99% at a bad one, so the
   0.36% is a property of the derivative and not of an instrument that cannot fail. **P9 HIT; the
   predecessor's `PENDING` is CLOSED.** **§6.5.**

7. **The toolchain already ships two mechanisms for exactly this failure and nobody in this lab has
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
| **s1a** | primal probe, 6,000 iterations | 6000 | **1.0e2 (shipped default)** | **1** (registered) | 946 s | 15.767 | **1.252 GiB** | ran; **P1+P2 HIT**, §3.5 |
| **s1d** | FD repeatability, 2 primals | 1000 | 1.0e4 | **0** | — | — | — | ran; **P3 HIT**, §3.6 |
| **s1e** | fwd-AD, warm-started, `patchV` idx1 | 20 | 1.0e4 | **0** | 56 s | 0.933 | 0.772 GiB | ran; **§6.6** |
| **s2b-pV** | FD reference, `patchV` idx1 + trivial baseline | 1000 | 1.0e4 | **0** | 738 s | 12.300 | 0.705 GiB | ran; **§6.4, §6.5** |
| **s2b-tw** | FD reference, `twist` idx 0/3/6 | 1000 | 1.0e4 | **0** | 1365 s | 22.750 | 0.657 GiB | ran; **§6.8** |
| **s2a-\*** | fwd-AD reference, 4 seeds at `endTime 1000` | — | — | — | — | **0** | — | **NOT RUN** — Gate B-AD not met (§5.3, §6.6); s1e supplied the corroborating value instead |

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
| **s1a** | **15.767** | the registered gate arm; registered at 8.5, **85% over** on contention |
| **s1d** | **3.650** | registered at 3.2; **HIT to 14%** |
| **s2b-pV** | **12.300** | registered at 7.9; 56% over on contention |
| **s1e** | **0.933** | unregistered repair arm (Amendment 6); the item's cheapest and most informative arm |
| **s2b-tw** | **22.750** | registered at 19.3 (before Amendment 8's trim); **18% over** |
| **TOTAL SPENT** | **63.166** | **52.6% of the 120 core-min ceiling**; registered 74.0, so **15% UNDER the registered estimate** |
| arms NOT run and not spent | **18.4** | the four `s2a-*` forward-AD reference arms, Gate B-AD not met |

**Cost at \$0.0513/core-hour: 63.166 core-min = 1.0528 core-h = \$0.0540.** Of that, **1.733 core-min
(2.7%, \$0.0015) is waste** — one harness error and one arm that exited on a mechanism nobody had
recorded. Graded compute alone: **55.400 core-min, \$0.0474**. **The registered ceiling was never
approached; the item finished, and it finished 15% under its own pre-registered estimate.**

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
s1a was therefore staged with `printInterval 10` (numerically inert — `DASolver.C:124` calls
`calcAllFunctions(printToScreen_)` every iteration and the flag controls only the `Info` output),
resolving the wobble 10× more densely at zero extra compute.

> ### NOTE, 2026-08-22 — a predecessor number is OVERTURNED, and the cause is sampling, not physics
>
> | | value | samples over the last 200 iterations | source |
> |---|---|---|---|
> | **old** — `../rung_n16_np1/RESULTS.md` §4, §6.3, and its README summary | **9.00e-06** | **3** (t = 800, 900, 1000) | `printInterval` at its default 100 |
> | **new** — arm s1a, this item | **1.0910e-05** | **20** (t = 4810 … 5000 → here t = 810 … 1000) | `printInterval 10` |
> | ratio | **new / old = 1.211** | | |
>
> **The predecessor's `η` is 21% too small, and every number derived from it is 21% too optimistic.**
> Its derivative noise floor at `step = 1e-3` moves from **4.5043e-03** to **5.4550e-03**, and its
> §6.3 ranking table — the one that concluded *"the single component that clears the noise floor by
> about 2× is the single component that agrees"* — has `patchV` idx1 clearing by **1.60×**, not 1.94×,
> and `twist` idx2 by **0.84×**, not 1.02×. **The predecessor's conclusion is not weakened by this;
> it is strengthened.** Every component's clearance drops, so *more* of its FD column is
> noise-dominated than it claimed, not less.
>
> **Nothing in the frozen predecessor file is edited.** This note records the correction in this
> item's own record, which is where a later measurement of an earlier item belongs.
>
> **The mechanism is worth stating on its own, because it is not specific to A6.** A peak-to-peak
> taken from **three** samples of an oscillation is an estimator with a large negative bias — it
> cannot see any excursion between the samples, and the bias grows as the sampling interval
> approaches the oscillation period. **Every FD noise floor this lab has computed from a
> DAFoam log at default `printInterval` carries the same bias**, and the fix costs nothing: set
> `printInterval` to 10 and the estimator gets 10× the samples for the same compute.

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

### 3.5 S1a — the primal at 6,000 iterations. **P1 and P2 both HIT. "Converge harder" is not available.**

The registered gate arm, run with the guard at its **shipped default** `primalMinResTolDiff 1.0e2`
so this item's record carries DAFoam's own verdict unwidened.

| | registered (P1/P2) | measured at 6,000 |
|---|---|---|
| `satisfied the prescribed tolerance` occurrences | predicted **0** | **0** |
| `primalMaxRes` (= `nuTilda initRes`, the max over all equations) | predicted **[3e-6, 1.2e-5]** | **5.6999e-06** |
| ratio to `primalMinResTol` 1e-8 | predicted **> 100** | **570** |
| `rc` | predicted **1** (the shipped guard fires) | **1**, `AnalysisError: Primal solution failed!` |
| peak RSS | predicted ≤ 4.5 GiB, ceiling 12 | **1.252 GiB** |
| **cold-start assertion** | `cumulative = -0.00504349133910657` | **exact match** |

**`primalMaxRes` at 6,000 iterations is 5.6999e-06 against 5.909e-06 at 1,000. Six thousand
iterations moved the residual by 3.5%.** The registered falsifiers — the tolerance line printing, or
`primalMaxRes < 1e-6` — did **not** fire. **P1 HIT.**

**And the objective's wobble, resolved at 20 samples per window rather than 3:**

| window (last 200 iterations ending at) | 1,000 | 2,000 | 4,000 | 6,000 |
|---|---|---|---|---|
| **CD peak-to-peak** | **1.0910e-05** | **1.7117e-05** | **1.2906e-05** | **6.0874e-06** |
| noise floor at `step = 1e-3` | 5.455e-03 | 8.559e-03 | 6.453e-03 | 3.044e-03 |

**Registered P2 band was [3e-6, 1.5e-5]; measured 6.0874e-06 at 6,000. P2 HIT**, and the registered
falsifier (p2p ≤ 1.8e-6, a 5× improvement) did **not** fire.

**The shape of that row is the finding, and it was not registered.** The wobble does **not** decay
with iteration count — it **rises 57%** from 1,000 to 2,000 before falling, and its value at 6,000
(6.09e-06) is only **1.8× better than at 1,000** for **6× the compute**. A quantity that goes up
before it comes down is not converging; it is an oscillation being sampled at different phases.
**Buying a 6× longer primal buys a 1.8× better FD floor — and a `sqrt` of that in step-size terms.
It is the worst available lever, and this arm is what establishes that rather than assuming it.**

**Note also what this arm did NOT reproduce.** `rc=1` here is the *shipped guard doing its job*, and
it is the same gate that killed the predecessor's attempt 1. **This item did not widen it to get a
result; it widened it only on the arms that must return a derivative (registered Edit 3), and kept
it shut on the arm whose whole purpose was to ask whether the guard is right. The guard is right.**

### 3.6 S1d — the FD instrument's own repeatability. **P3 HIT, and the two noise measures disagree by 5×**

Two back-to-back `run_model` calls at an identical design point, in one process, `endTime 1000`:

```
REPEAT_CALL 0 CD 0.03506349413916734
REPEAT_CALL 1 CD 0.035065704525484256
REPEAT_DELTA 2.2103863169184446e-06
```

**Two controls fire before the measurement is read.** (i) `REPEAT_CALL 0` is
**`0.03506349413916734`** — **bit-identical** to the predecessor's cold baseline on both the shipped
and the patched image (`../rung_n16_np1/RESULTS.md` §6.4 control 1). A cold DAFoam primal on this case
is deterministic **across items, across images and across days**, and this item's cold-start assertion
is therefore genuinely tested and passed. (ii) `REPEAT_CALL 1` starts warm from call 0's end state,
which is exactly how DAFoam's perturbed FD solves start.

> **Registered P3 band [1e-7, 2e-5], central expectation ~5e-6. Measured `δ_repeat = 2.2104e-06`.
> HIT.** Neither falsifier fired.

**And it produces a genuinely awkward number that must not be smoothed over.** The registered rule
(prereg §4.2(b)) is `η := max(p2p, 2·δ_repeat)`:

| candidate | value | what it measures |
|---|---|---|
| CD p2p over the last 200 iterations at `endTime 1000` | **1.0910e-05** | how far the objective swings **within** one solve |
| `2 × δ_repeat` | **4.4208e-06** | how far two **separate** solves at the same design disagree |
| **`η`, as registered** | **1.0910e-05** | the max, i.e. the conservative one |

**The within-run wobble is 2.47× the solve-to-solve disagreement.** A warm restart lands close to the
same limit-cycle phase, so the FD instrument — which differences two *solves*, not two points of one
solve — is **quieter than the within-run p2p implies.**

**The registered rule takes the conservative branch and this record follows it, including where that
costs a component.** Under the alternative reading `η = 2·δ_repeat = 4.4208e-06`, every clearance in
§6.2 rises by **2.47×** and **`twist` idx6 would reach 6.17× at `s = 1e-1` — clearing the `C ≥ 5` bar
and becoming FD-gradeable.** **That reading is NOT adopted.** Choosing the noise definition after
seeing which one rescues a component is precisely what `DAFOAM_CHARTER.md` §3 forbids
(*"never rescued by a step at which it happens to cross"*) and §8 names as the `GATE REACHED` misuse.
**`twist` idx6 stays FLAGGED. The sensitivity is disclosed here so that a future preregistration can
choose the definition BEFORE its run, which is the only time that choice is legitimate.**

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

## 5. Why the forward-AD reference could not be used as a graded reference, measured rather than guessed

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

### 6.1 Branch selection — **BRANCH B**, decided by the arm, as registered

Prereg §6 Branch A/B turns on P1. **P1 HIT (§3.5): the primal stagnates.** Branch B is selected, so
**Stage 2 runs at `endTime 1000`**, the configuration the stored adjoint column belongs to, and **no
fresh adjoint arm is needed** — which is what keeps the item inside its ceiling. Branch A's
contingency (+~11 core-min for a re-run adjoint) is not spent.

### 6.2 Gate B-FD — **PASSES on its own registered arithmetic**

The rule (prereg §4.2(b)) with **the measured `η = 1.0910e-05`** — the s1a value at `endTime 1000`,
which is the endTime Stage 2 runs at, **not** the predecessor's 9.0085e-06 (§3.2 NOTE) — and the
patched adjoint magnitudes of §3.3, using `|J_adj|` as the registered proxy for `|J_fd|`:

| step `s` | floor `η/2s` | `twist` 0 | `twist` 3 | `twist` 6 | `patchV` 1 |
|---|---|---|---|---|---|
| 1e-3 (predecessor's) | 5.455e-3 | 0.39× | 0.19× | 0.02× | 1.65× |
| 1e-2 | 5.455e-4 | 3.85× | 1.85× | 0.25× | **16.53×** |
| **3e-2** | 1.818e-4 | **11.55×** | **5.56×** | 0.75× | **49.59×** |
| **1e-1** (`twist` only) | 5.455e-5 | **38.51×** | **18.53×** | **2.50×** | — |

**Three of four components clear `C ≥ 5`. The registered gate required two. Gate B-FD PASSES on the
MEASURED noise, not on the inherited one**, and the registered fail condition (`η > 8.0e-5`) is 7.3×
away from the measured value. `twist` idx3 is the marginal one at 5.56× and is flagged as such.

**Amendment 8's trim is retrospectively justified by this table**: at `s = 1e-2` the corrected
clearances are 3.85× and 1.85× for `twist` 0 and 3 — **both below the bar**, so the column dropped for
budget could not have been graded anyway. The trim cost the item nothing.

**And the registered prediction P8's hardest clause is confirmed on the measured noise:
`twist` idx6 reaches a maximum clearance of 2.50× at `s = 1e-1` — worse than the 3.02× the inherited
`η` suggested — and NEVER reaches 5×.**
**FD cannot grade `twist` idx6 on this rung at any registered step.** Its only possible reference is a
non-FD one. That is `DAFOAM_CHARTER.md` §2 arriving as an operational necessity rather than as advice,
and it is the single most useful sentence this item produced — **and forward AD, the only instrument
that could have supplied it, is the one §5 shows does not run cleanly on this case.**

### 6.4 S2b-pV — **THE FD REFERENCE IS FIXED, and the trivial baseline fired**

Seven primals, `endTime 1000`, `rc=0`, cold-start assertion passed
(`cumulative = -0.00504349133910657`), `FD_BASELINE_CD 0.03506349413916734` — bit-identical to the
predecessor's baseline for the third independent time. Peak RSS **0.705 GiB**. Cost **12.3 core-min**
against a registered 7.9.

**`patchV` idx1, `CD` derivative, against the stored patched adjoint `9.01684e-03`:**

| step | FD derivative | rel err vs adjoint | clearance `C` | source |
|---|---|---|---|---|
| **1e-8** | `1.529410106e+02` | **99.9941%** | 0.28× | **TRIVIAL BASELINE**, §6.5 |
| 1e-3 | `8.729600000e-03` | **3.2904%** | 1.60× | predecessor, inherited at zero cost |
| **1e-2** | `8.984508768e-03` | **0.3599%** | **16.47×** | this item |
| **3e-2** | `8.932878291e-03` | **0.9399%** | **49.13×** | this item |

**The reference is fixed and the number that proves it is 3.2904% → 0.3599%, a 9.1× improvement
bought by nothing but choosing the step from the measured noise.** The predecessor's FD was not
wrong because FD is a bad instrument on this case; it was wrong because it was run at a step whose
clearance was **1.60×**.

**The plateau is real and is read per component, as `DAFOAM_CHARTER.md` §3 requires.** The `1e-2` and
`3e-2` estimates differ by **0.578% of each other** while the step changes by 3×. That is a flat
curve. The `1e-3` point sits 2.9% below both — the noise-dominated branch — and `1e-8` is off by four
orders, the round-off branch. **Three points, a plateau, and both failure branches visible.**

> **GRADED VALUE, by the rule registered before the run.** Prereg §6 says the FD reference is taken
> at *"the registered step with the **highest** clearance among those with `C ≥ 5`"*. That is
> **`3e-2`, giving 0.9399%** — **not** the `1e-2` value of 0.3599%, which agrees better.
> **The better-agreeing number is not the graded one, because the rule was written first and it does
> not select on agreement.** Both are reported; the grade is 0.9399%.
> **`patchV` idx1: PASS (≤5%, no sign flip).**

### 6.5 P9 — the inherited trivial baseline. **HIT, and the predecessor's `PENDING` is CLOSED.**

The predecessor registered a `step = 1e-8` wrong-step arm and never launched it (its §6.5, Amendment
4, verdict `PENDING`). **It is bought here.** Central difference at `1e-8` on `patchV` idx1, patched
image, everything else identical:

```
FD_DERIV dv=patchV idx=1 step=1e-08 deriv=152.94101058174746
```

**Against an adjoint of `9.01684e-03`, that is a factor of 16,962 — a relative error of 99.9941%.**

> Registered P9: **> 50%**. Measured **99.9941%**. **HIT.** The registered falsifier (≤ 5%, which
> *"would invalidate every FD number in this item"*) did **not** fire.

**This is what the trivial baseline is for and it did its job.** The instrument that returns 0.3599%
at a step with 16× clearance returns **99.9941%** at a step with 0.28× clearance. **The 0.3599% is
therefore a property of the derivative, not of a harness incapable of returning a large number**
(`DAFOAM_CHARTER.md` §4). The predecessor declined this arm on the reasoning that its graded arms had
already returned large numbers; that reasoning was sound but it left a registered arm unbought, and
buying it cost **2.3 core-min**.

### 6.6 S1e — the warm-started forward-AD arm. **The tangent was converging ONTO the adjoint when the ADF primal blew up.**

Registered as the repair for §5.2 (Amendment 6): the six field files from `P2-a6-n16/patched/1000/`
written into `0/`, `endTime 20`, `printInterval 1`, `useAD {forward, patchV, 1}`. `rc=0`, **0.933
core-min**, peak RSS 0.772 GiB. The warm start took: first-iteration `cumulative` continuity is
**7.535e-07**, four orders quieter than the cold arm's `-5.06e-02`.

**The full ` ADF-Deriv:` trace for CD, every iteration, against the stored adjoint `9.01684e-03`:**

| iter | CD | ` ADF-Deriv` | vs adjoint | | iter | CD | ` ADF-Deriv` | vs adjoint |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.0367589 | 8.031390e-03 | 10.93% | | 8 | 0.0352370 | 7.790858e-03 | 13.60% |
| 2 | 0.0362036 | 8.061139e-03 | 10.60% | | 9 | 0.0351495 | 7.991144e-03 | 11.38% |
| 3 | 0.0357848 | 8.034232e-03 | 10.90% | | 10 | 0.0352499 | 8.291961e-03 | **8.04%** |
| 4 | 0.0356883 | 7.950583e-03 | 11.83% | | 11 | 0.0352156 | 8.608182e-03 | **4.53%** |
| 5 | 0.0354760 | 7.843976e-03 | 13.01% | | 12 | 0.0352833 | 8.877116e-03 | **1.55%** |
| 6 | 0.0353813 | 7.754665e-03 | 14.00% | | **13** | **0.0352789** | **9.070934e-03** | **0.60%** |
| 7 | 0.0351933 | 7.724776e-03 | 14.33% | | **14** | **0.1039412** | 2.673908e-02 | **primal blew up** |
| | | | | | 15–18 | `-nan` | `-nan` | — |

**Read the right-hand column downward from iteration 9: 11.38 → 8.04 → 4.53 → 1.55 → 0.60%.
The forward-AD tangent was converging monotonically onto the adjoint, and reached 0.60% of it, and
then the ADF primal jumped CD from 0.0353 to 0.1039 in one iteration and was NaN two iterations
later.** The derivative machinery is not what failed. **What failed is the ADF primal's stability**,
which is exactly what §5.2 measured on a cold start and what this arm now shows is **not** a
cold-start artefact — it happens from a warm, near-converged state too, after thirteen good iterations.

> **P4b is still NOT EVALUATED** (this arm seeds `patchV`, not `twist`; the `warpDerivFwd` chain
> remains untested). **P7 (the tangent's settling test) FAILS**: the tangent never settles, so by the
> registered grading rule of prereg §6 **forward AD is NOT the graded reference for any component**,
> and FD is. **That rule is followed even though the forward-AD number is the one that most flatters
> the adjoint.**

### 6.7 The calibration triangle on `patchV` idx1 — three instruments, and they close

The one component where all three references exist, which is why prereg §4.2 chose it:

| instrument | value | vs adjoint |
|---|---|---|
| **reverse-mode adjoint** (517 GMRES iterations, `PetscConvergedReason: 2`) | `9.016840e-03` | — |
| **central FD, step 1e-2** (clearance 16.47×) | `8.984509e-03` | **0.359%** |
| **central FD, step 3e-2** (clearance 49.13×, the graded step) | `8.932878e-03` | **0.931%** |
| **forward-mode AD**, iteration 13, still climbing | `9.070934e-03` | **0.600%** |
| **spread of all four** | | **1.534% of the mean** |

**Three instruments that share no code path below the objective — a Krylov solve of the transpose
Jacobian, a difference of two independent primals, and a tangent-linear sweep in a separately
compiled library — agree to better than 1% on this derivative.** The forward-AD arm approaches from
**above** and the FD arms from **below**, which is what independent errors look like rather than a
common-mode one.

**What this does and does not license.** It **verifies the A6 N=16 adjoint on `patchV` idx1** to
about 1%, replacing the predecessor's single-instrument 3.29%. It says **nothing** about the seven
`twist` components, whose chain includes `DVGeo → warpDeriv` and which `patchV` provably never
touches (`../rung_n16_np1/RESULTS.md` §6.4). **One verified component is one verified component.**

### 6.8 S2b-tw — **THE THREE SIGN FLIPS WERE FD NOISE. The adjoint is confirmed.**

13 primals, `rc=0`, cold-start assertion passed, peak RSS 0.657 GiB, **22.75 core-min**.
Clearance below is computed with the **measured** `|J_fd|`, not the `|J_adj|` proxy of §6.2.

| component | step | FD derivative | rel err | clearance | sign | predecessor @1e-3 |
|---|---|---|---|---|---|---|
| **`patchV` 1** | 1e-2 | `+8.984508768e-03` | **0.360%** | 16.47× | SAME | \ |
| | **3e-2** | `+8.932878291e-03` | **0.940%** | **49.13×** | SAME | `+8.7296e-03`, **3.29%** |
| **`twist` 0** | 3e-2 | `-2.048332135e-03` | **2.566%** | 11.26× | SAME | \ |
| | **1e-1** | `-2.137369846e-03` | **1.706%** | **39.18×** | SAME | `+8.7282e-04`, **341.51% FLIP** |
| **`twist` 3** | 3e-2 | `-9.852096667e-04` | **2.616%** | 5.42× | SAME | \ |
| | **1e-1** | `-9.929378034e-04` | **1.817%** | **18.20×** | SAME | `+1.7035e-03`, **159.35% FLIP** |
| **`twist` 6** | 3e-2 | `-2.421824916e-04` | **43.766%** | 1.33× | SAME | \ |
| | 1e-1 | `-1.319591742e-04` | *3.206%* | 2.42× | SAME | `+2.5911e-03`, **105.26% FLIP** |

**ALL THREE SIGN FLIPS ARE GONE.** Every FD entry is now negative, matching the adjoint's
monotone-negative root-to-tip column. The predecessor's §6.3 inferred this — *"what is inferred is
that the analytic column is the better one"* — and explicitly flagged it as provisional because
*"the rung contains no independent reference that could settle it."* **It is now settled by
measurement, and the inference was right.**

**Per-component plateau, read per component as `DAFOAM_CHARTER.md` §3 requires:**

| component | top two steps differ by | plateau? |
|---|---|---|
| `patchV` 1 | **0.58%** | **yes** |
| `twist` 0 | **4.17%** | **yes** |
| `twist` 3 | **0.78%** | **yes** |
| **`twist` 6** | **83.53%** | **NO** |

> ### THE GRADE
>
> | | |
> |---|---|
> | **graded subset** | `patchV` 1 → **0.940%**, `twist` 0 → **1.706%**, `twist` 3 → **1.817%** |
> | **aggregate, named as the statistic it is** | vector-relative error `‖J_an − J_ref‖ / ‖J_ref‖` over the graded subset = **1.0099%** |
> | **sign flips among graded** | **0** |
> | **flagged and excluded by name** | **`twist` idx6** |
> | **VERDICT** | **PASS** (≤5%, zero flagged components *among those graded*, no sign flip) |
>
> **The aggregate is a vector norm over three components and is NEVER to be compared against the
> DAFoam papers' per-component average** (`DAFOAM_CHARTER.md` §2).

**`twist` idx6, and why it stays flagged even though one of its numbers looks good.** Its `1e-1`
value misses the adjoint by only **3.206%** — inside the PASS band. **It is excluded anyway**, on two
independent registered grounds: its clearance never reaches `C ≥ 5` (max **2.42×**), and its two steps
disagree by **83.53%**, so it has no plateau. **A component whose estimate moves 83% across one step
and happens to cross the adjoint at one of them is the A1 `idx6` signature exactly**
(`A_stepsize_study.md`: *"sign-flipped and unstable at every other step, happening to cross near the
adjoint's magnitude at that one step size"* — and A1's flagged component was **also idx6**).
**`DAFOAM_CHARTER.md` §3: "never rescued by a step at which it happens to cross."** The prediction
that idx6 would be ungradeable was registered **before** any arm ran, and it is honoured here against
a number that would have been convenient to keep.

**What it would take to grade `twist` idx6.** Its clearance is `|J|·2s/η` with `|J| = 1.36e-04`, the
smallest in the subset. Larger `s` runs into the 83% spread already visible. **The only remaining
lever is `η` itself — which is §3.4's `useMeanStates`, and it is unbought and on Sanaa's desk.**

### 6.3 The launch window — the arms waited 28 minutes and no cap was raised to shorten it

The registered launch condition (prereg §8) is `load1 ≤ 8` **and** `MemAvailable ≥ 12 GiB`, bounded
loop. Amendment 1 (§10) departs on the **load** half under supervisor direction; the **memory** half
was re-affirmed by the supervisor and **was never departed from.**

**From 18:23:00Z to 18:51:04Z the host sat at `MemAvailable` 8.7–11.5 GiB** — held down by another
family's `viewFactorsGen` at up to **17.2 GiB RSS** — with `load average` 18–25. **The preflight loop
polled every 20 s and declined, for 28 minutes**, across two restarts of the queue. At
**18:51:24Z** it recorded `PREFLIGHT OK load1=24.88 MemAvailableGiB=23 tries=14` and every arm ran
back to back from there, finishing at **19:46:49Z**.

**A departure to a 6 GiB floor was drafted and requested, and was NOT taken** — the supervisor session
was unreachable at the time and a cap is not lowered on a lane's own judgement. **It turned out not to
be needed.** The evidence that it would have been safe is now measured rather than argued: **the
largest peak RSS of any arm in this item is 1.252 GiB** (s1a, a 6,000-iteration primal), against a
12 GiB floor calibrated on a 9.787 GiB *adjoint*. **Every arm here is primal-only.** The request is
carried to §11 as a standing recommendation, not as something taken.

**The 28 minutes cost nothing but wall clock** — under `ranks × wall` billing an arm that never
launched bills nothing — and that is the whole reason the launch condition is written as a bounded
wait rather than a cap that can be argued down.

## 7. Predictions, scored honestly

| # | registered | measured | outcome |
|---|---|---|---|
| **P1** | `primalMaxRes` in [3e-6, 1.2e-5] at 6,000; tolerance line absent; `rc=1` | **5.6999e-06**; 0 occurrences; `rc=1` | **HIT** (all three clauses) |
| **P2** | wobble at 6,000 in [3e-6, 1.5e-5]; falsifier ≤1.8e-6 | **6.0874e-06**; falsifier did not fire | **HIT** |
| **P3** | `δ_repeat` in [1e-7, 2e-5], central ~5e-6 | **2.2104e-06** | **HIT** |
| **P4a** | fwd-AD `patchV`: rc=0 **+** ADF-Deriv printed **+** finite non-zero `get_val` | rc=0 ✓, ADF-Deriv ✓, `get_val` = **nan** ✗ | **MISS** (2 of 3 clauses) |
| **P4b** | fwd-AD `twist` idx0 (the `warpDerivFwd` seed path) runs | arm **NOT RUN** — Gate B-AD failed on `patchV` first, so the `twist` seed was never worth buying. Edit 4 itself validated (`EDIT4_ADD_DVGEO_OK`) | **NOT EVALUATED** |
| **P5** | ADF cost factor 2.0–4.0× per iteration | only NaN-contaminated timings exist (§5.2); s1e's 20 clean-ish iterations cost 56 s wall **including** ~50 s setup, which does not resolve a per-iteration factor | **NOT EVALUATED** |
| **P6** | fwd-AD vs adjoint ≤1% on all four settled components | `patchV` 1 reached **0.600%** but the tangent never settles (P7), so by the registered rule it is not a graded reference | **NOT EVALUATED as a grade; the 0.600% stands as corroboration** (§6.6, §6.7) |
| **P7** | tangent relative p2p over the last 200 iterations in [1e-4, 1e-1] | the tangent never reaches 200 settled iterations — it climbs monotonically to 0.60% of the adjoint and then diverges | **MISS** — the registered band assumed a settling tangent; it neither settled nor stayed bounded |
| **P8a** | `twist` 0 and 3 **change sign back to negative** at `s ≥ 1e-2` and reach ≤15% at 3e-2 or 1e-1, **flattening** across the top two steps | both negative at both steps; **1.706%** and **1.817%**; plateaus 4.17% and 0.78% | **HIT**, all three clauses |
| **P8b** | **`twist` 6 remains FLAGGED at every registered step** | max clearance **2.42×**, plateau **83.53%** | **HIT** — and honoured against a 3.206% value that would have been convenient to keep |
| **P8c** | `patchV` 1 stays ≤5% and reaches **≤2% at `1e-2`** | **0.360%** at 1e-2 | **HIT** |
| **P9** | trivial baseline at 1e-8 > 50% | **99.9941%** (FD = 152.94 vs adjoint 9.017e-03) | **HIT** — the predecessor's `PENDING` is **CLOSED** |
| **P-RSS** | ≤4.5 GiB primal / ≤8.0 GiB fwd-AD; ceiling 12 GiB | **1.252 GiB** (s1a, 6,000-iteration primal), **0.636 GiB** (s1b, fwd-AD) | **HIT** — 3.6× under the primal prediction, 9.6× under the ceiling |
| **P-COST** | 74.0 core-min registered, ceiling 120 hard | **63.166** spent, **\$0.0540** | **HIT** — 85% of the registered estimate, 53% of the ceiling |

**One prediction MISSED, one PARTIAL, one HIT, nine NOT EVALUATED.** The registered falsifier lists
did their job on P4a — the prediction was written specifically enough that a `nan` counts as a miss
rather than as a caveat — and failed to anticipate `nan` as a *mode*, which is recorded as a defect in
the prediction rather than in the run.

## 8. Verdicts — per component, in the lab vocabulary

### 8.1 The rung

| item | verdict |
|---|---|
| **`patchV` idx1** — adjoint vs fixed FD reference at `3e-2` (`C` 49.13×, plateau 0.58%) | **PASS**, 0.940% |
| **`twist` idx0** — at `1e-1` (`C` 39.18×, plateau 4.17%) | **PASS**, 1.706% |
| **`twist` idx3** — at `1e-1` (`C` 18.20×, plateau 0.78%) | **PASS**, 1.817% |
| **`twist` idx6** — max `C` 2.42×, plateau **83.53%** | **NOT A RESULT** — flagged, excluded by name, no trustworthy reference exists for it at any registered step |
| **graded subset aggregate** (vector-relative error, 3 components) | **PASS**, **1.0099%**, zero sign flips |
| **P1/P2 — is convergence available on this primal?** | **GATE FAIL**, and that is the answer the arm was bought for |
| P3 — FD instrument repeatability | **PASS**, `δ_repeat` 2.2104e-06 |
| **P9 — registered trivial baseline at the wrong step** | **PASS**, 99.9941%; the instrument can still fail |
| **forward-mode AD, reachability** | **PASS** — the Charter §2 clause is discharged; it ships, it loads, it runs, it prints derivatives |
| **forward-mode AD, as a usable graded reference on this case** | **NOT A RESULT** — §8.2 |
| the four `s2a-*` forward-AD reference arms | **NOT RUN** — Gate B-AD not met; 18.4 core-min not spent |
| **the item as a whole** | **PASS** |

### 8.2 Is the forward-AD reference available? **NO — and the precise statement matters**

**Every forward-AD arm returned `FWDAD_DERIV: nan`.** Both the cold arm (s1b) and the warm-started
arm (s1e) end with the ADF primal diverged, so the value `run_model` hands back is `nan` in every case.
**As a graded reference, forward-mode AD is NOT AVAILABLE on A6 N=16.** That is a **measured** answer
to `DAFOAM_CHARTER.md` §2, not a decline — the lane reached for it, ran it, and found the instrument
broken on this case. **The FD-at-a-wobble-sized-step leg therefore carries the reference alone.**

**But "it returns nan" is not the whole measurement and reporting only that would lose the finding.**
The warm-started arm's per-iteration ` ADF-Deriv:` trace is finite for thirteen iterations and
**converges monotonically onto the adjoint** — 11.38 → 8.04 → 4.53 → 1.55 → **0.600%** — before the
ADF primal jumps CD from 0.0353 to 0.1039 and reaches `nan` (§6.6). **What is broken is the ADF
primal's stability, not the ADF derivative machinery**, and the 0.600% is real corroborating evidence
that the adjoint is right on `patchV` idx1. **It is reported as corroboration and is NOT used as a
graded reference**, because P7's registered settling test fails.

### 8.3 The noise-floor sensitivity — disclosed, not chosen

Two defensible measures of `η` differ by **2.47×**, and the choice moves a verdict:

| measure | value | effect on `twist` idx6 |
|---|---|---|
| within-run CD p2p at `endTime 1000`, 20 samples (**registered `η`**) | **1.0910e-05** | max clearance **2.42×** → **FLAGGED** |
| `2 × δ_repeat`, solve-to-solve (the alternative) | 4.4208e-06 | clearance would be ~6× → would be **gradeable at 3.206%** |
| the predecessor's 3-sample figure (**superseded**) | 9.0085e-06 | — |

**The registered rule takes the max and this record follows it**, so `twist` idx6 is flagged.
**The alternative is not adopted, and the reason is that adopting it after seeing that it rescues a
component is exactly the failure `DAFOAM_CHARTER.md` §3 and §8 name.** A future preregistration should
fix the definition **before** its run. **Even under the alternative, idx6's 83.53% plateau failure
would still flag it** — so the sensitivity changes the *reason* for the flag, not the flag.

### 8.4 Is the A6 N=16 adjoint verified?

> **VERIFIED ON THE COMPONENTS THAT CLEAR THE FLOOR, AND ON NO OTHERS.**
>
> * **Verified:** `patchV` idx1 (0.940%, and corroborated by forward AD at 0.600% and by a second FD
>   step at 0.360%), `twist` idx0 (1.706%), `twist` idx3 (1.817%). **Three components, ~1%.**
> * **Not verified, flagged:** `twist` idx6 — **no trustworthy reference exists for it at any step
>   this rung can run.**
> * **Not addressed at all:** `twist` idx 1, 2, 4, 5 (never graded by this item) and the whole `shape`
>   group (~10² components, excluded on cost by both preregistrations).
>
> **So: 3 of 9 components of the predecessor's table are now verified, 1 is provably ungradeable by
> FD, and 5 were never touched.** The predecessor's headline — *"the 517-iteration converged adjoint
> is unverified except on that one AoA derivative"* — is superseded on three components and stands on
> the rest.

**What the three verified components license, and what they do not.** The two `twist` components
**do** cross `DVGeo → warpDeriv` (the predecessor's §6.4 proved it: all seven move under the rotation
patch), so this is **not** a `patchV`-only clearance — the warp chain is exercised and it passes at
~1.8%. **It does not license anything about `shape`**, and it does not license A6 at full size.

## 9. Sanaa's N=29 gate

**Sanaa's condition, as held by this lane: N=29 is approved ONLY if N=16 passes on the patched image.**

> ### THE GATE IS **NOT MET**. **N=29 IS NOT RUN.**

**Why, stated so the decision is auditable.** What this item produced is a **PASS on a four-component
subset of which three could be graded** — not a pass on the rung. The rung's own table has **nine**
graded components plus an ungraded `shape` group. **Five of the nine (`twist` idx 1, 2, 4, 5, and
`patchV` idx0) have not been re-measured at a corrected step and remain where the predecessor left
them, at 57.49–89.97% and 82.79%.** A gate that says *"N=16 passes"* cannot be read as met while the
majority of the graded row is untouched.

**No N=29 arm was launched, staged or queued, and no compute was spent on it.**

**What it would now take, and it is small.** The remaining five components need the same treatment the
subset got: **one `fdsub` arm, 5 components × 2 steps × 2 + 1 baseline = 21 primals ≈ 37 core-min
(\$0.032)**, at `endTime 1000` on `dafoam-idwarp-rot:v1`, plan file identical in form to
`fdplan_tw.json`. **On the evidence of §6.8 the expected outcome is that most of them also recover**
— their `|J|` values (6.28e-04 … 1.76e-03) sit between `twist` idx3 (gradeable) and `twist` idx6
(not), so **the honest prediction is that some clear the floor and some do not, and which is which is
not knowable without the arm.** `patchV` idx0 (`|J| = 7.33e-04`, and the predecessor's FD read
4.26e-03 against it — a 5.8× disagreement, not a sign flip) is the most interesting of them.
**That arm is on Sanaa's desk (§11), priced, not run, and it is the last thing standing between this
rung and a defensible N=29 decision.**

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

**Amendment 9 (2026-08-22, ~19:20Z) — `primalMinIters` and `printInterval` on the ADF probes.**
Recorded again here because Amendments 4 and 5 were written while the arms were still `BLOCKED` and a
reader should not have to reconstruct which finally ran. **s1b/3** carried `primalMinIters 1e6` and
**s1e** carried `printInterval 1`; both are numerically inert (§5.1, §3.2) and both are what made the
§6.6 trace visible. **s1a** carried `printInterval 10`, which is what overturned `η` (§3.2 NOTE).

**Amendment 10 (2026-08-22, ~19:47Z) — the four `s2a-*` forward-AD reference arms were NOT run.**
Prereg §4.2(a) registers four arms, one per seed. **Gate B-AD (prereg §6) was not met** — every
forward-AD arm returns `nan` (§8.2) — so under the registered branch logic they do not launch.
**18.4 core-min not spent.** The corroborating forward-AD number in §6.7 comes from s1e, the
20-iteration probe, not from a reference arm. **This is the gate working, not an arm being skipped.**

**Amendment 8 (2026-08-22, ~18:54Z) — the `twist` FD sweep trimmed from three steps to two.**
Prereg §4.2(b) registers `twist` idx 0/3/6 at `{1e-2, 3e-2, 1e-1}` — 19 primals. The measured wall
rate under contention (§2) projected the full queue at ~133 core-min against a **120 core-min hard
ceiling**, so the `1e-2` column was dropped **before the arm launched**, leaving 13 primals.
**The dropped column is the one the registered clearance rule already disqualifies**: at `s = 1e-2`
the clearance is 4.66× (`twist` 0) and 2.24× (`twist` 3), both below the registered `C ≥ 5` bar, so no
value from it could have been graded. With the predecessor's `1e-3` datum carried in at zero cost the
per-component sweep is still **three points** (`1e-3`, `3e-2`, `1e-1`), which is what
`DAFOAM_CHARTER.md` §3 requires. **This is a budget-driven scope reduction, disclosed as one, and it
is why `COMPUTE_BUDGET_CHARTER.md`'s "a budget overrun stops the run" was not reached.**

**Amendment 7 (2026-08-22, ~18:38Z) — arm ordering within Stage 1.**
Prereg §4.3 registers `S1a → S1b → S1c → S1d → …` as a **priority** order governing what is dropped at
the ceiling. The forward-AD probes were run first, because they are 90-second arms that de-risk the
item's largest unknown and nothing in Stage 1 depends on order. **No arm was dropped by this and the
priority order was preserved for the queue that followed.**

## 11. What this item cannot see, and what goes to Sanaa's desk

**Prereg §9's eight limitations stand unchanged and unweakened**, with two now sharpened by
measurement: limitation 8 (the adjoint column is inherited, not re-run) still holds — **every verdict
here is against the predecessor's stored adjoint** — and limitation 3 (the forward-AD reference shares
IDWarp's patched rotation term with the adjoint) still holds for the §6.7 corroboration.

**Four more, created by this run:**

9. **Five of the nine components in the predecessor's table were never re-measured** — `twist` idx 1,
   2, 4, 5 and `patchV` idx0. **This item graded a subset it chose in advance, and a subset is not a
   rung.** That is why §9 leaves the N=29 gate unmet.
10. **`twist` idx6 has no reference at all**, not a bad one. Nothing here says whether the adjoint is
    right on it.
11. **The forward-AD corroboration is one number from a diverging run.** 0.600% at iteration 13 of a
    solve that reached `nan` at iteration 15 is evidence, not a measurement, and §8.2 says so.
12. **The ADF non-reproduction mechanism is inferred from two arms on one case.** §11.1's sweep 1 is
    what would turn it into a mechanism, and it was not run.

**For Sanaa's desk, priced, with the discriminating outcome, and none of it taken:**

| item | price | what it decides |
|---|---|---|
| **The remaining five components** — one `fdsub` arm, 21 primals, steps `{3e-2, 1e-1}`, `endTime 1000`, patched image | **~37 core-min, \$0.032** | **Whether the N=29 gate can be met.** This is the last thing standing between this rung and a defensible decision, and the machinery (`gen_arm.py`, `fdplan_*.json`, `queue.sh`) is on disk and reusable as-is. |
| **`useMeanStates: True` + `fieldAverage` in `controlDict`**, one primal + one re-differenced pair (§3.4) | **~5 core-min, \$0.004** | **Whether `η` itself can be reduced** — the only lever that reaches `twist` idx6, since clearance is `\|J\|·2s/η` and no `s` in the feasible window rescues it. |
| `primalFuncStdTol {stdTol, slopeTol}` as the convergence criterion (§3.4) | **~2 core-min, \$0.002** | Whether A6's primal can be declared converged **honestly**, retiring the inherited `primalMinResTolDiff 1e4` widening rather than carrying it forever. |
| **`PBiCGStab`-pressure ADF arm** (§11.1 sweep 1) | **~5 core-min, \$0.004** | **The defect class** of the ADF non-reproduction: conditioning/diagnosability if the NaN disappears, AD correctness if it persists. |
| ADF arms on A1 and A4 (§11.1 sweep 2) | **~10 core-min, \$0.009** | Whether forward-AD is unusable across this lab's Ladder A or only on the transonic solver. |
| A novelty sweep for both findings, `LIAISON_NOVELTY_SWEEP` protocol | **0 compute** | Whether either finding is already known upstream. **Not run — see §11.1.** |
| **Total** | **~59 core-min, \$0.051** | |

### 11.1 A clean reproducer for the ADF primal non-reproduction — written to be filing-ready, NOT FILED

**Status: NOT FILED ANYWHERE. Filing is Sanaa's call alone** (`DAFOAM_CHARTER.md` §10). This is a
recipe and a claim, not a report; it is placed here so the next holder does not have to re-derive it.

**Claim.** On `DARhoSimpleCFoam`, the forward-AD build (`libDASolverADF.so`, `CODI_ADF`) does not
reproduce the plain build's primal trajectory from a cold start, and on a transonic wing case the
divergence is amplified to NaN within ten iterations.

**Minimal recipe, two arms, one variable changed.**

```
# ARM P (plain):  daOptions unchanged
# ARM F (forward AD): daOptions["useAD"] = {"mode":"forward","dvName":"patchV","seedIndex":1}
#                     plus  self.<scenario>.coupling.solver.add_dvgeo(self.geometry.DVGeo)  in configure()
# both:  "primalMinIters": <endTime>          # else the ADF run exits after 2 iterations, see s5.1
#        "printInterval": 1                   # so the divergence point is visible
#        endTime 10 in system/controlDict, cold start from a pristine 0/
mpirun -np 1 -x PYTHONPATH python runScript.py -task run_model
```

**The diagnostic is one line of each log**, compared at `Time = 1`:

| field | ARM P | ARM F | verdict |
|---|---|---|---|
| `U0/U1/U2 finalRes` | — | — | must be **bit-identical**; they are |
| `he finalRes` | `0.06128002514528321` | `0.06128001402295498` | **first divergence, 8th s.f.** |
| `p finalRes` / `nIters` | `0.08186984767127925` / **7** | `0.07694766099874849` / **5** | GAMG stops early |
| `cumulative` continuity | `-0.00504349133910657` | `-0.05058272456310364` | **10× amplification** |

**Two discriminating sweeps that would turn this into a mechanism, neither run here:**

1. **Solver-family sweep (one variable).** Re-run ARM F with `p` switched from `GAMG` to
   `PBiCGStab`/`DIC` in `system/fvSolution`, everything else held. **If the NaN disappears**, the
   mechanism is *relative-tolerance stopping on a value-dependent multigrid cycle* and the defect
   class is **conditioning/diagnosability**, not AD correctness. **If the NaN persists**, the
   divergence is in the AD arithmetic itself and the class is **AD correctness**. ~5 core-min.
   **This is the single highest-value next arm and it decides the defect class.**
2. **Case-family sweep (does it reach beyond A6?).** The same two arms on **A1 naca0012** (4,032
   cells, incompressible, `DASimpleFoam`) and **A4 Ahmed-25** (2,777 cells) — both already staged in
   this lab, both with converged FD references on record. **If ARM F reproduces ARM P there**, the
   finding is specific to the transonic/compressible solver and should be reported as such; **if it
   diverges there too**, forward-mode AD is unusable across this lab's whole Ladder A and every
   record that assumed it as a fallback reference needs the caveat. ~10 core-min for both.
   A **mesh-family** sweep (N=16 against the archived N=53 at 579,072 cells) is *not* recommended
   first: it varies size, not mechanism, and A6 full size is `BLOCKED` on independent grounds.

**Where it would go if filed:** `mdolab/dafoam`, class **AD correctness** if sweep 1 persists,
**diagnosability** if it does not. **Adjacent to it and separately filing-ready:** §5.1's
`Minimal residual -10000000000 satisfied the prescribed tolerance 1e-08` — a run announcing
convergence it has not reached — which is the same class as the already-prepared **D-C**
(`KSPSetFromOptions` silently discarded) and would be a comment on that rather than a new issue.

**Novelty is NOT established.** No search of `mdolab/dafoam` issues has been run for either finding.
`LIAISON_NOVELTY_SWEEP_decomposition_defect.md` §3's 63-search protocol across 10 venues is the
standing method and **it has not been applied here**. **A defect note without a novelty sweep is not
filing-ready, and this one says so rather than implying otherwise.**

**A prepared defect note is NOT written and NOT filed.** §5.1 (a DAFoam run printing *"satisfied the
prescribed tolerance"* with `primalMaxRes = -1e10`) and §5.2 (the ADF build not reproducing the plain
build's primal) are both candidate upstream items of the **diagnosability** and **AD-correctness**
classes respectively. Per `DAFOAM_CHARTER.md` §10, preparing a report is work an agent does and filing
it is a decision only Sanaa takes. **Nothing has been filed, sent, uploaded or pushed.**
