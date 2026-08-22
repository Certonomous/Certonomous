# A3 ONERA M6, sweep rung 2 (42,120 cells) — the patched-IDWarp arm at np=4: RESULTS

**Run 2026-08-22, Lane A.** Pre-registration: `PREREGISTRATION.md` in this directory — body committed
`a5605f54` **before any arm launched**, Amendment 1 `a94e8317` (pre-compute), Amendment 2 `674cab89`
(post-first-compute, before the graded arms). **This file does not revise any of them.** Nothing is
filed, sent, uploaded or pushed. Filing stays NOT APPROVED and is Sanaa's alone.

> **HEADLINE. The patched row PASSES — and the patch makes A3 worse.** Every row that crosses the
> mesh-warp chain moves *away* from a fixed, independently measured FD reference: `shape[115]`
> **0.0172% → 0.1586%** (~~9.22×~~ **9.208×** worse — *corrected, see Correction 1*), `twist[1]` **0.2740% → 0.9279%** (3.39× worse). `patchV`,
> which does not cross the warp chain, is **bit-identical**. Both moved rows still sit inside the
> 5% band, so the verdict is **PASS**, but this is the **first row on Ladder A where the rotation
> patch degrades a gradient the shipped toolchain already got right** — and it is the answer to
> `../grading_confirmation/RESULTS.md` §5.1's open question, in the surprising direction.
>
> **Both controls held.** The FD column is bit-identical between images on every printed digit, and
> the Charter-§4 trivial baseline was refused by the rung's own evaluability gate.
>
> **One registered guard was breached and did not fire, and it is my fault.** See §9.1.

Raw logs: `/home/ubuntu/certonomous-runs/P3-a3-rung2-patched/{patched,wrongstep,np1_patched}.log`.
Ledger `ledger.txt`; contemporaneous adjudications `adjudications.txt`; gate logs
`launch_condition{,_np1,_np4}.txt`; RSS traces `rss_*.txt`; colouring watchdog
`coloring_watchdog.log`.

---

## 1. Arms as executed

| arm | image | `IDWARP_SO_MD5` printed by the run itself | np | task | FD step | rc |
|---|---|---|---|---|---|---|
| **P-A PATCHED** | `dafoam-idwarp-rot:v1` | `85f59e87253e0a71a813f64ca6e4c425` on **all 4 ranks** | 4 | `fd3` | 1e-2 / 2e-2 | **0** |
| **P-B TRIVIAL BASELINE** | `dafoam-idwarp-rot:v1` | `85f59e87253e0a71a813f64ca6e4c425` | 4 | `fd1wrong` | **1e-8** | **0** |
| SHIPPED-equivalent (comparator) | `dafoam-subpclu:v1`, env unset | `f0fcb488…` (stock) | 4 | `fd3` | 1e-2 / 2e-2 | **not re-run** — cited from `A3-rung2-n28-tpc1/fd3_run.log`, per frozen §3 departure 1 |
| N-P np=1 (withdrawn config) | `dafoam-idwarp-rot:v1` | `85f59e87…` | 1 | `fd3` | — | **stopped early, §6** |

**Activity proofs, asserted from the arms' own logs.** `transonicPCOption 1;` present;
**zero** occurrences of `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU`; `idwarp`
version reads `2.6.2` on the patched stack — recorded as the demonstration that the version string
discriminates nothing (`../../patched_build/idwarp_rot/BUILD.md` §2), not as a check.

**Colouring cache READ, not rebuilt** — the supervisor's registered check. `patched.log:845` `Checking
if Coloring file exists..` → `:853` `Reading Coloring dRdWColoring_4` → `:857` `dRdWTPC: 0 of 1315`,
with **no** `Calculating dRdW Coloring` anywhere. Cache md5 `a2e5f3172f3b889656e51b67ca4e55a6`,
byte-identical to `A3-rung2-n28-tpc1/dRdWColoring_4.bin` — the file the graded stock arms read.
*A rebuild also prints a `Reading Coloring` line afterwards* (archived log `:884` then `:892`), so the
discriminator is the **absence** of `Calculating`; that is what the watchdog enforced.

**Cold start proved:** first `Time step continuity errors : sum local = 0.6833296303785072` —
**bit-identical to all 16 digits** of this mesh's np=4 signature, with `initRes ≈ 1` on all six fields.

### 1.1 The full assertion set, read from arm P-A's own log

| assertion | required | read from `patched.log` | |
|---|---|---|---|
| `IDWARP_SO_MD5` | `85f59e87253e0a71a813f64ca6e4c425` | that value, and **only** that value, on ranks **0,1,2,3** | ✓ |
| solver `nProcs` | 4 | **`nProcs : 4`** (`:83`) | ✓ |
| decomposition | `scotch`, 4 subdomains | `scotch`; **4** `processor*` dirs created | ✓ |
| `transonicPCOption` | `1;` | `transonicPCOption 1;` (`:430`) — the record log reads `2;` | ✓ |
| sub-LU banner | **absent** | **0** occurrences | ✓ |
| `Reading Coloring dRdWColoring_4` | present | **1** occurrence (`:853`) | ✓ |
| `Calculating dRdW Coloring` | **absent** | **0** occurrences | ✓ |
| colours | 1315 | `dRdWTPC: 0 of 1315` (`:857`) | ✓ |
| cold signature | `0.6833296303785072` | that value, 16/16 digits | ✓ |

*`nProcs : 1` also appears at `:50`; that is the serial `decomposePar` utility's own header, not the
solver's. The solver's is `:83`. Stating the distinction because reading the wrong one would make
this table say the opposite of what it says.*

### 1.2 Gate history and the gate-bound extension

This item was gated three times and the gate was re-specified twice. Recorded so the launch
conditions are auditable rather than remembered.

| attempt | condition | polls | reading | outcome |
|---|---|---|---|---|
| np=4, first | frozen §7: `load1 ≤ 8` **and** MemAvailable ≥ 12 GiB | 12 | **min `load1` 18.28**; MemAvailable 20.96–23.57 GiB — the memory limb **never** bound | never met; **nothing launched, 0.000 core-min** |
| np=1 (Amendment 1) | `MemAvailable ≥ 12 GiB` | 25 | 8.9–10.8 GiB, then 20.93 | met at poll 25 |
| np=4, graded (Amendment 2) | `free_cores ≥ 4` **and** MemAvailable ≥ 12 GiB | 9 | opened at **`free_cores = 4`, MemAvailable 15.28 GiB, `load1` 13.84** | met at poll 8 |

**Dated gate-bound extension, 2026-08-22T18:27:50Z** (`launch_condition_np1.txt`): the np=1 bounded
poll was extended from **100 to 240 polls (100 min → 4 h)**, poll interval unchanged at 60 s, and
**the 12 GiB floor was NOT changed**. Reason, verified from `ps -eo pid,rss,comm` rather than taken
on report: a single **foreign** `viewFactorsGen` process, **pid 810930, RSS 14.96 GiB** (another
team's radiation view-factor generation, transient, not touched). At the extension: MemAvailable
9.57 GiB, arms launched 0, solver core-min 0.000.

**The load-average limb never measured the resource the arm consumes.** Twelve single-core T-family
solvers put `load1 ≥ 12` by construction on a 16-core box, while the four cores a `--cpus=4`
container needs were sometimes genuinely free. `free_cores`, defined in Amendment 2 §A2.3 as
`nproc − median(5 samples of runnable-thread count)`, opened in **9 polls** what `load1 ≤ 8` had not
opened in 12 and could not have opened before 2026-08-25/26.

## 2. Verdict rows — SHIPPED-equivalent and PATCHED are two rows and are not merged

Band (`../../A_stepsize_study.md:91-93`): PASS ≤5% with zero flagged components; CONDITIONAL 5–15%;
>15% **or any sign flip** → FAIL. Statistic: **per-component relative error** `|J_an − J_fd(h)|/|J_fd(h)|`
— *not* a vector norm, and never quoted against one (Charter §2).

| row | toolchain | predicted | measured | verdict |
|---|---|---|---|---|
| `CD`/`patchV[1]` | **SHIPPED-equiv ‡** | — (cited) | **0.0077%** | **PASS** |
| `CD`/`patchV[1]` | **PATCHED** | bit-identical | **0.0077%** — analytic `7.90292882576689e-03`, *bit-identical* | **PASS** |
| `CD`/`twist[1]` | **SHIPPED-equiv ‡** | — (cited) | **0.2740%** | **PASS** |
| `CD`/`twist[1]` | **PATCHED** | 0.05–2.0% | **0.9279%** — **3.39× worse than stock** | **PASS** |
| `CD`/`shape[115]` | **SHIPPED-equiv ‡** | — (cited) | **0.0172%** | **PASS** |
| `CD`/`shape[115]` | **PATCHED** | 0.001–1.5% | **0.1586%** — ~~9.22×~~ **9.208× worse than stock** (*Correction 1*) | **PASS** |
| trivial baseline `patchV[1]` @1e-8 | PATCHED | delta below gate | **NOT EVALUABLE**, ratio **100.0293%**, sign-flipped | **NOT A RESULT — control behaved as designed** |

**‡** the stock row is `dafoam-subpclu:v1` with `DAFOAM_SUBPC_TYPE` unset — *SHIPPED-equivalent, not
`dafoam/opt-packages:latest`*. §10 item 5 stands; this item did not close it.

**Arm verdict: PASS** — all three components evaluable, step-consistent, inside 5%, zero sign flips
against their own FD. **Per R11 this does not move the shipped grade** and never could
(`FAMILY_SUPERVISION_GUIDELINES` §3.4).

**The withdrawal falsifier did NOT fire, and it was live.** Frozen §5 P13 registered: *"if the wrong
step both **clears** the evaluability gate **and** returns ≤ 5%, then the gate is not measuring what
it claims, and per Charter §4 arm P-A's verdict is withdrawn, not defended."* The wrong step
**failed the gate** (`delta/threshold = 0.0668`, i.e. 15× short) **and** returned **100.0293%** with
the sign reversed. Neither conjunct was satisfied. **Arm P-A's PASS stands, and it stands against a
control that was capable of destroying it.**

**Evaluability and step-consistency, stated with the numbers** (registered rule, `A3_RUNG2_N28_PREREGISTRATION.md` §5,
carried by frozen §4): repeat-baseline drift **8.093e-07**; gate = delta > 10 × drift =
**8.09e-06**. Measured `|CD(+h) − CD(−h)|`: `patchV[1]` **`1.58046469e-04`**, `twist[1]`
**`3.61764738e-05`**, `shape[115]` **`2.60156156e-03`** — **all three evaluable**, clearing the gate
by 19.5× / 4.47× / 321×.

*Convention, stated because the archived record uses the other one.* `../grading_confirmation/RESULTS.md`
§2c reports these clearances as *"45×–3,213×"*, which is delta **relative to the drift**, not to the
gate. On that convention the same three deltas read **195× / 44.7× / 3,214×** — reproducing the
record's quoted range to three significant figures. The two statistics differ by exactly the factor
10 in the gate's definition and **are not quoted against each other**. Step-consistency `|FD(h) − FD(2h)|/|FD(h)|`:
**0.0366% / 0.3065% / 0.0048%**, all under the 1% gate, and all **identical to the stock arm's**
because the FD column did not move (§3).

## 3. The control that makes the comparison readable: the FD did not move

Registered falsifier P4: *"any FD or baseline digit differing → stop and report."* It did not fire.

| quantity | SHIPPED-equiv | PATCHED | moved? |
|---|---|---|---|
| baseline1 `CD` | `3.31180586539945e-02` | `3.31180586539945e-02` | **no** |
| baseline2 `CD` | `3.31188679497014e-02` | `3.31188679497014e-02` | **no** |
| repeat-baseline drift | `8.093e-07` | `8.093e-07` | **no** |
| `FD(h)` `patchV[1]` | `7.90232345e-03` | `7.90232345e-03` | **no** |
| `FD(h)` `twist[1]` | `1.80882369e-03` | `1.80882369e-03` | **no** |
| `FD(h)` `shape[115]` | `-1.30078078e-01` | `-1.30078078e-01` | **no** |
| `FD(2h)` all three | `7.90521694e-03` / `1.80327914e-03` / `-1.30084297e-01` | identical | **no** |
| step-consistency all three | 0.0366% / 0.3065% / 0.0048% | identical | **no** |

A `diff` of every `FD3` line between the two logs differs **only** on the `twist` and `shape`
*adjoint* and *relerr* fields — i.e. exactly the patched quantities and nothing else. **The two arms
are demonstrably derivatives of the same function**, which is what licenses §2 and §5.

**And the adjoint is bit-identical too (P3).** All **11** printed `(iteration, KSP residual norm)`
pairs match the stock run digit for digit — `2.121211553380e-02` at iteration 0 through
`2.119555554540e-06` at **987**, `PetscConvergedReason: 2` — only the wall-clock stamps differ.
This is the empirical settlement of §2's two-image comparability argument: `dafoam-idwarp-rot:v1`
(stock `DALinearEqn`) and `dafoam-subpclu:v1` (env unset) **do share a numeric path**, and the
IDWarp patch does not touch the Krylov solve. Per Charter §6 this is an *identity* check, not
evidence of a correct operator.

## 4. Per-component table

| component | analytic SHIPPED-equiv | analytic PATCHED | analytic moved | FD(h) (unchanged) | rel err S | rel err P |
|---|---|---|---|---|---|---|
| `patchV[1]` (AoA) | `7.90292882576689e-03` | `7.90292882576689e-03` | **0** | `7.90232345e-03` | 0.0077% | **0.0077%** |
| `twist[1]` | `1.80386731629814e-03` | `1.79204040523569e-03` | 0.6556% | `1.80882369e-03` | 0.2740% | **0.9279%** |
| `shape[115]` | `-1.30055677346768e-01` | `-1.29871804107421e-01` | 0.1414% | `-1.30078078e-01` | 0.0172% | **0.1586%** |

**The direction is the finding.** On A1 the patched analytic moved *toward* the pre-existing,
unchanged FD on every component — *"the direction a genuine fix must move"*
(`../../A1/reverify_patched_idwarp_np1/RESULTS.md` §4.2). **Here it moves away on both
warp-crossing rows.** The FD reference is fixed and bit-identical, so this is not an artifact of
the comparison.

## 5. The patch effect, analytic vs analytic (P9)

Full 120-component `CD wrt shape` row, both analytic, no FD involved. Stock row
`A3-rung2-n28-tpc1/tpc1_computetotals_attempt2.log:899-938`; patched from the D2 dump.

| | |
|---|---|
| `‖g_stock‖₂` | `4.4998703612e-01` |
| `‖g_patched‖₂` | `4.4793317077e-01` |
| `‖g_patched − g_stock‖₂` | `6.6129487022e-03` |
| **patch effect L2** | **1.469586%** — registered band 0.005–5%, **HIT** |
| components differing at printed precision | **120 of 120** |
| **analytic-vs-analytic sign flips** | **3** — idx 12, 13, 24 |

**The tolerance confound the frozen P9 carried is measured away, not argued away.** The stock
full-row dump ran at `primalMinResTol 1e-6` and the patched `fd3` at `1e-8`. On all three components
that *both* stock logs printed, the 1e-6 dump and the 1e-8 table agree to printed precision
(`shape[115]` `-1.30055677e-01` both; `patchV[1]` `7.90293000e-03` vs `7.90292883e-03`; `twist[1]`
`1.80387000e-03` vs `1.80386732e-03`). The confound is below the printed precision.

**The three sign flips are between two analytic vectors and carry no verdict**, because no FD was
measured at those indices — nothing here says which sign is right. They are small: idx12
`-1.26769052e-04 → +1.01963000e-03`, idx13 `-7.77318637e-04 → +6.78340000e-04`, idx24
`-1.55683069e-04 → +1.31430000e-04`, i.e. **0.097%, 0.598% and 0.120%** of the row's largest
component. Reported as evidence, and as a reason a future full-vector `check_totals` would be worth
buying.

**Cross-case consistency worth recording.** `CD/twist` moves **0.6593%** in L2 here. A6's N=16 rung
measured **0.664%** for the same patch on the same DV class (`LADDER_A_STATUS.md` row 27) — two
different cases, two different meshes, agreeing to three significant figures. Against **97–99.5%**
for the same defect on A1/A2/A5 shape rows.

## 6. The withdrawn np=1 attempt — a deliberate stop, and NOT a measurement

Amendment 1 moved the arms to np=1 to escape a host gate; **arm N-P measured that decision and
refuted it**, and Amendment 2 withdrew the configuration before the graded arms ran. Recorded here
because it was bought.

| quantity | np=4 (archived, same mesh) | np=1 (measured) | ratio |
|---|---|---|---|
| `nUniqueCols` | 125,870 | **381,558** | **3.03×** |
| `AllNonZeros` | 60,419,908 | 59,719,202 | 0.99× — the same matrix |
| s per 100 `ColorSweep` | 12.28 | **42.91** | **3.49×** |
| decoloured per sweep | 405.0 | 397.4 | **0.98×** |

Per-sweep efficiency is unchanged; there are simply three times as many colours, because the dRdW
distance-2 colouring graph is **per-partition** and becomes global at one rank. Projection from the
measured rates: **4,074 s CPU** for the whole arm, ~8,314 s wall at the observed 49% CPU share, and
**4,074 s even on an idle box** against Amendment 1's own 4,200 s cap. At that cap the run would
have held ~2,058 s CPU — **still inside the colouring, never reaching the adjoint** — spending
**70.0 core-min for no number**.

**Arm N-P was therefore stopped deliberately at 11.950 core-min.** Per `DAFOAM_CHARTER` §7 **a stop
is not a measurement**: *no conditioning, memory or gradient claim is drawn from it in any
direction.* Authority: `FAMILY_SUPERVISION_GUIDELINES` §6 item 5 and §9. The registered decision
rule was honoured — the np=1 shipped and control arms were never launched and their logs do not
exist.

## 7. Predictions scored

**Frozen P1–P14 — the graded set (`a5605f54`).**

| # | prediction | measured | score |
|---|---|---|---|
| P1 | provenance, 4 limbs | md5 `85f59e87…` on 4/4 ranks; `transonicPCOption 1;`; 0 sub-LU banners; ver `2.6.2` | **HIT** |
| P2 | cold sig, exact | `0.6833296303785072`, 16/16 digits | **HIT** |
| P3 | 987 iters, reason 2, residual path bit-identical | 987, reason 2, **11/11 pairs bit-identical** | **HIT** |
| P4 | FD column bit-identical | baselines, drift, all FD(h), FD(2h), stepcons identical | **HIT** |
| P5 | selection `patchV[1]`, `twist[1]`, `shape[115]` | same three | **HIT** |
| P6 | `patchV` bit-identical, 0.0077% | bit-identical, 0.0077% | **HIT** |
| P7 | `twist[1]` 0.05–2.0%, PASS, no flip | **0.9279%**, PASS, no flip | **HIT** |
| P8 | `shape[115]` 0.001–1.5%, PASS, no flip | **0.1586%**, PASS, no flip | **HIT** |
| P9 | patch effect L2 0.005–5% | **1.469586%** | **HIT** |
| P10a | peak RSS 9.0–11.5 GiB | **9.263 GiB** (cap 12) | **HIT** |
| P10b | host `MemAvailable` never below 8 GiB | **5.85 GiB min; 82 of 156 samples below** | **MISS — see §9.1** |
| P11 | wall 271–633 s, 18.1–42.2 core-min | **955 s, 63.667 core-min** | **MISS** |
| P12a | control delta 1.0e-10 – 2.5e-10 | **5.402995e-07**, 2,161× above the band | **MISS** |
| P12b | control fails the evaluability gate | delta/threshold **0.0668** → **NOT EVALUABLE** | **HIT** |
| P13 | control ratio > 20% | **100.0293%**, and **sign-flipped**; FD is **3,418×** the analytic | **HIT** |
| P14 | control wall 60–200 s, 4.0–13.3 core-min | **152 s, 10.133 core-min** | **HIT** |

**Amendment 2 P29** — wall 452–950 s / 1.0–2.1× / 30.1–63.3 core-min: measured **955 s, 2.11×,
63.667 core-min**. **MISS**, by 5 s of wall (0.5%). Reported as a miss rather than rounded into the
band.

**Amendment 1 P15–P28** — **NOT APPLICABLE, CONFIGURATION WITHDRAWN**, except the three actually
measured: **P15 HIT**; **P16 MISS** (I registered the cold signature to ≥10 significant figures
across np; it is np-*specific* and differed at the 2nd figure, `0.7019005906092856` vs
`0.6833296303785072` — the arm was provably cold on the `initRes ≈ 1` limb, and §1 above confirms
the signature reproduces bit-for-bit at *matched* np); **P28 MISS** (core-minutes are not conserved
across a rank change).

**Score: 12 HIT, 5 MISS, of 17 scored limbs.** Every miss is a band I set too tight or derived
wrongly, not a run that misbehaved.

**P12's miss is instructive and is not a rescue.** I predicted the wrong-step delta from the *true
derivative* (`~3.16e-10`). The measured delta is `5.402995e-07`, **1,709× larger** — because at
h=1e-8 the difference between two perturbed primals is set by **primal re-convergence noise**, not
by the derivative. The measured drift in that same arm is `3.227678e-07`, the same order. So the
band was wrong for a reason worth keeping: *a wrong-step FD delta is bounded below by the primal
noise floor, not by the signal it is trying to measure.* The **conclusion** P12 was bought for —
that the gate refuses the wrong step — held.

## 8. Cost

Registered ceiling **120.0 core-min** (Amendment 1 §A1.0). Basis: cores × wall for the whole clock,
$0.0513/core-hour.

| item | ranks | wall | core-min | note |
|---|---|---|---|---|
| pre-flight identity check | 4 | 3 s | **0.200** | no solver, no case |
| np=4 gate, first attempt (12 polls) | — | — | **0.000** | nothing launched |
| **arm N-P np=1 — stopped early** | 1 | 717 s | **11.950** | **waste, no number** |
| **arm P-A PATCHED** | 4 | **955 s** | **63.667** | rc=0, inflation **2.11×** |
| **arm P-B trivial baseline** | 4 | **152 s** | **10.133** | rc=0 |
| **TOTAL** | | | **85.950** | **71.6% of ceiling; $0.0735** |

**Graded 73.800 core-min; waste 12.150 (14.1%).** Predicted for this attempt (Amendment 2 §A2.5)
≈65.6; measured 73.800 — **12.5% over**, driven by P29's inflation miss. The ceiling was not
reached and no arm was dropped for cost. **Nothing approached $25**: the total is **0.29%** of it.

## 9. Disclosures

### 9.1 A registered guard was breached, did not fire, and the fault is mine

Frozen §5 P10 registered: *"host `MemAvailable` below 8 GiB → the arm is stopped by memory and
recorded as such."* **Arm P-A drove host `MemAvailable` to 5.85 GiB and held it below 8 GiB for 82
of 156 samples (52.6% of the arm), and no stop occurred.**

**It was my container.** Pearson `r(myRSS, hostMemAvailable) = −0.999` over 156 samples; my RSS rose
0.710 → 9.263 GiB as host availability fell 14.44 → 5.85 GiB.

**Why it did not fire:** I registered the watcher as **record-only** and registered a stop condition,
with *nothing connecting them* — no kill path, no live polling. **A stop rule with no enforcement
path is a preference, not a control**, which is `DAFOAM_CHARTER` §13's own admission arriving in my
own preregistration.

**Disposition, stated rather than smoothed.** The arm was **not** stopped, so it is not *"stopped by
memory"* and the NOT A RESULT branch — which describes a *stopped* arm — does not apply. The
numbers stand, and they stand on evidence independent of the breach: rc=0, no OOM, container peak
**9.263 of 12 GiB** (23% headroom), and the adjoint reproduced the stock residual path **bit-for-bit
on 11/11 points** with the FD column bit-identical — direct evidence the numerics were unaffected.
The 8 GiB floor is a **neighbourliness guard protecting the shared box and the T-family**, not a
validity guard on this measurement. **P10b is scored a MISS and the breach is reported at the
headline of this section rather than in a footnote.** No T-family process was killed and no OOM was
recorded, but the risk was real and I created it.

### 9.2 Contention

Arm P-A ran with **4 free cores** at launch (gate `free_cores = 4`, `MemAvailable 15.28 GiB`,
`load1 13.84`) while the T-family held 12 unpinned cores. `docker stats` read **`cpu=399.91%`**
against the 4-core cap — near-full occupancy — yet wall still came in at 2.11× the 452 s idle basis.
**These wall clocks are contended and are not a clean cost basis for scaling.**

### 9.3 The colouring cache was inherited, not computed

Both arms read `dRdWColoring_4.bin` md5 `a2e5f3172f3b889656e51b67ca4e55a6` rather than building it,
disclosed as frozen §3 departure 2. The file is byte-identical to the one the graded stock arms
read, and the reuse is what makes the two rows cost-comparable. A fresh colouring would cost
**+28.0 core-min** and, the colouring being a deterministic function of mesh and partition, is
predicted to change no digit.

## 10. What this item cannot see — the frozen §9 limits, restated against what was found

1. **The full-vector aggregate.** Three components carry the verdict. §5 measures the patch effect
   across all 120 shape components, **but that row has no FD beside it** — and it turned up **3
   analytic sign flips** at indices nobody has ever FD'd. A5's `idx16` is the standing warning.
2. **The decomposition axis** — np=4 `scotch`, one partition, on every graded arm. A4's **16,600×**
   split between two decompositions of one mesh is why this matters. The np=1 attempt was stopped
   before it produced a gradient, so **A3 still has no decomposition datum.**
3. **Regime 2 of the rotation defect** — invisible; `fd3` evaluates at the undeformed baseline and
   ±1e-2, where the `sqrt(eps)` guard fires. Regime 2 survives the patch by design.
4. **The limiter lever and the DAFoam-side defects** — untouched.
5. **The literal shipped image at this rung** — **NOT closed.** The comparator remains
   `dafoam-subpclu:v1` with the env unset (SHIPPED-equivalent ‡). §3's bit-identical adjoint is
   strong evidence the numeric paths coincide, but this item did not run
   `dafoam/opt-packages:latest` at rung 2.
6. **The other rungs** — rungs 1 and 3 and the 399,360-cell campaign keep **PENDING** in the
   PATCHED column.
7. **The `CL` rows** — `fd3` computes totals for **CD only**. `dCL/d*` is unmeasured on both images.
8. **A converged adjoint is not a correct operator** (L-35, L-36). P3's `reason 2` is an identity
   check between two images. The FD table grades the gradient, and it grades three components of it.

## 11. Ledger

| item | value |
|---|---|
| solver core-minutes | **85.950** (ceiling 120.0, 71.6% used) |
| dollars | **$0.0735** |
| graded / waste | 73.800 / **12.150 (14.1%)** |
| containers started | 4 (1 pre-flight, 1 np=1 stopped, 2 graded), all `--rm`, none left running |
| arms that produced a number | 2 of 3 launched |
| processes needing a kill | 1 (arm N-P, deliberate, §6) |
| frozen files edited | **0** |
| published case directories written into | **0** (staged copies throughout) |
| `LESSONS.md` / `DOCKET.md` / `NUMERICS_KNOWLEDGE.md` / `INDEX.md` / `LADDER_A_STATUS.md` / charters edited | **0** — supervisor's appends |
| filed upstream | **nothing** |


---

## Correction 1 — 2026-08-22, dated, quote-and-strike

**What was written, in §Headline and §2:** *"`shape[115]` **0.0172% → 0.1586%** (9.22× worse)"*.

**What is correct: 9.208×.** The original lines are struck in place above and are **not rewritten**;
this note is the correction of record (L-32).

**How the error was made, since that is the reusable part.** I formed the ratio by dividing the two
*already-rounded 4-decimal percentages the log prints* — `0.1586 / 0.0172 = 9.2209` — instead of
dividing the underlying quantities. Recomputed from the full-precision analytic and FD values, with
the FD reference identical on both sides:

| | value |
|---|---|
| `FD(h)` `shape[115]` (identical both images) | `-1.30078077925157e-01` |
| stock analytic | `-1.30055677346768e-01` → rel err **0.01722087%** |
| patched analytic | `-1.29871804107421e-01` → rel err **0.15857693%** |
| **ratio** | **9.2084** |

`twist[1]` was checked the same way and is unaffected: stock **0.27401084%**, patched
**0.92785628%**, ratio **3.3862** — **3.39×** as published stands.

**Provenance of the catch:** the DAFoam supervisor recomputed the headline from the raw analytic and
FD values before recording D462/N-D18 and obtained **9.21×**. That disagreed with this file, so the
quantity was recomputed here from full precision and the supervisor's figure is confirmed. **The
board is right and this file was wrong.** No verdict, band, gate or cost figure is affected — the
ratio is descriptive, both rel errs are unchanged, and `shape[115]` remains a **PASS** at 0.1586%.

**The general rule this earns:** a ratio of two rounded percentages is not the ratio of the two
quantities. Derived figures are computed from the underlying values, not from the printed summary.
