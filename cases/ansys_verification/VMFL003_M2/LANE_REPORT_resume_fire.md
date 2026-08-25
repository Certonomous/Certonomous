# VMFL003-M2 — LANE REPORT: RESUME-FIRE, and the GRADING of arms A and B

**Lane:** `ansys-lane-opus` (Opus 5). **Supervisor:** `ansys-verification-supervisor`.
**Written:** 2026-08-25, UTC times from `date -u` reads in the working invocations.
**NOT FILED ANYWHERE.** Nothing here is sent, emailed, uploaded, filed, posted,
registered or commented outside this box (CLAUDE.md rules 7, 8). **SUBMISSIONS PARKED.**

Lane→supervisor messaging is one-way, so this file is the report of record; the
final assistant message duplicates it and may be lost.

---

## 0. THE HEADLINE, BEFORE ANYTHING ELSE

**THE FROZEN SLATE LAUNCHER WAS NEVER KILLED. IT IS STILL RUNNING.**

`pid 2218904`, `bash cases/ansys_verification/VMFL003_M2/run_vmfl003_m2.sh`, started
**2026-08-25 16:43:19Z**, **ppid 1** (orphaned to init — it survived the agent stop
because it was launched detached). Its cwd is `/home/ubuntu/Certonomous`.

The brief's premise — that the predecessor's lanes were stopped and the work must be
re-fired — is correct about the *lanes* and **wrong about the launcher**. The launcher
outlived them and has been working the slate continuously ever since. It is invisible to
a naive check for the same reason L-41 names: the thing you are looking for is not the
thing `pgrep` shows you.

**PROOF IT IS THE FROZEN INSTRUMENT, MID-SLATE, WITH A CORRECT RUNNING TOTAL** — not an
inference, arithmetic. When it launched `C_RNGkEpsilon/L2_500x5` it used `timeout 2087`.
The frozen formula is `timeout_s = min(CAP−spent, PER_ARM−arm_spent) × 60 / RANKS`. From
the `RUN_RC.txt` files on disk: arm A = 29.9500, arm B = 31.1333, C/L1 = 5.2167 core-min,
so slate spent = 66.3000 and arm-C spent = 5.2167. `min(160−66.3, 40−5.2167) = 34.783333`
core-min → `int(34.783333 × 60) = ` **2087**. Exact match.

It has since closed C/L2 (`rc=0`, wall 1416 s, 23.6 core-min) and launched
`C_RNGkEpsilon/L3_1000x5` with **`timeout 670`** — again exact:
`int((40 − 28.816667) × 60) = 670`.

**CONSEQUENCE, AND IT IS THE ONE DECISION I AM ESCALATING: `C_RNGkEpsilon/L3_1000x5`
WILL BE KILLED BY ITS OWN BUDGET, AND THAT WILL KILL THE WHOLE SLATE LAUNCHER.**
`A/L3_1000x5` needed **675 s** and `B/L3_1000x5` needed **666 s** on the identical mesh
and endTime. C/L3 has **670 s**. Even at a *zero* RNG penalty it is a coin-flip against
666–675 s, and the measured RNG penalty is **4.16×** (§4). So C/L3 will exit `rc=124`,
and the frozen launcher's own guard — `[ "$RC" -eq 0 ] || { echo ABORT…; exit 1; }` —
will then **terminate the entire slate run**. Projected at **≈18:25Z**.

What dies with it: C's wall-treatment ladder `D_500x3/4/6` (never run), arm C never
graded, **arm `D_kOmegaSST` never started at all**, and `COST.txt` never written.

I did not intervene. Rule 12: an overrun stops the run and does not get a new budget;
raising a frozen cap is not a lane's call, and this is yours.

---

## 1. THE FOUR FROZEN HASHES — RE-VERIFIED BY ME, IN THE INVOCATION THAT LAUNCHED

`HEAD` at launch = `735b7b8c5b248da16aff3c9a7249a355748abdda` (peers commit constantly;
`c5fdcad4` is the freeze commit and is an ancestor). For each file, **HEAD blob == disk
blob == the hash you verified personally**:

| file | blob | result |
|---|---|---|
| `PREREGISTRATION.md` | `cdbf2659b6eec2599fc3eda7a149aaca391461b0` | **VERIFIED** |
| `grade_vmfl003_m2.py` | `6dcc99940154ea204a598ba2118042bf972a786d` | **VERIFIED** |
| `grade_vmfl003_m2_omega.py` | `b595c86a4b8580d5928b4d4dd1458698f6de8ac2` | **VERIFIED** |
| `run_vmfl003_m2.sh` (added by me) | `29a53e035a1bb595d7dde69b0e2e6b77bcd561b4` | **VERIFIED** |

I added the launcher to the set because I reuse its code (§3). None of the four was
edited: they are frozen (rule 6).

**Manual, title-page verified against the PDF beside the sidecar (rule 15, never by
filename or hash):** page 1 of `Ansys_Fluid_Dynamics_Verification_Manual.pdf` decompresses
to *"Ansys Fluid Dynamics Verification Manual / Release 2026 R1 / ANSYS, Inc. / March 2026
/ Southpointe / 2600 Ansys Drive / Canonsburg, PA 15317"*, matching the `.txt` sidecar
head. **VMFL003, manual p. 19–20:** air, ρ = 1.225 kg/m³, μ = 1.7894e−5 kg/m·s, pipe
L = 2 m, R = 0.002 m, inlet 50 m/s, outlet 0 Pa, Re = 1.37×10⁴, half the axisymmetric
domain, friction factor from the Moody chart. **Target Δp = 21744 Pa**; Fluent 21480
(ratio 0.988), CFX 21740 (ratio 1.000) — context, never the gate.

---

## 2. WHAT I FIRED, AND WHAT I REFUSED TO FIRE

### 2.1 FIRED — `D_kOmegaSST`, all six registered levels, DETACHED

| field | value |
|---|---|
| script | `cases/ansys_verification/VMFL003_M2/resume_fire_arm_d.sh` (**new file**, not an edit to a frozen one) |
| pid | **2357892**, `ppid 1` (`nohup setsid`), launched **18:11:00Z** |
| cwd | `/home/ubuntu/Certonomous` |
| levels | `L1_250x5`, `L2_500x5`, `L3_1000x5`, `D_500x3`, `D_500x4`, `D_500x6` — the frozen `LEVELS` table verbatim, **in the frozen order** |
| budget | `PER_ARM_CAP` = 40 core-min, arm D spent 0; slate seeded from disk |
| timeout | frozen formula `min(160−spent, 40−arm_spent) × 60 / 1`; L1 gets ≈2400 s |
| record | `verification/runs/ansys_verification/VMFL003_M2/_resume_fire/` — log, `loadavg_arm_d.tsv`, `COST_ARM_D.txt` |
| state at writing | **blocked on GUARD 0**, waiting for pid 2218904 to exit — as designed |

**It is detached and it waits.** GUARD 0 polls `ps -o pid= -p 2218904` (never `pgrep -f`
— that has self-matched three times today) every 30 s and refuses to build anything while
the frozen launcher lives. That is the whole safety argument: **the live launcher owns
this run tree, and `build_case` would `mkdir -p`/`cp -a` straight into a directory it is
about to build itself — two solvers in one case.** The wait makes a collision impossible
whether the launcher dies at 18:25Z as projected or survives and builds arm D itself; in
the second case GUARD 3 refuses and the script exits without touching anything.

**Why a new script at all.** The frozen launcher carries GUARD 3: it aborts if *any*
arm/level directory exists. A and B are complete and C is partly on disk, so it can never
be re-run — and it is frozen, so it is **not edited** (rule 6). The new script changes no
gate, threshold, cap or label:

- `build_case()` and `mesh_case()` are **not re-typed**. They are extracted from the HEAD
  blob of the frozen launcher (lines 111–169), asserted against
  `sha256 = 3fee43cb254c47d2c6bf6a11817556a1958134686b42629ef2a0228e0658d43e`, and
  `eval`'d — so case materialisation, meshing, the empty-sampling-zone refusal and the
  mesh birth certificate are **provably the frozen code**.
- The running total is **seeded from disk** by summing `core_min` across every
  `RUN_RC.txt` already written. Spent is spent.
- The age-guard datum (`touch` every file in the level's own `0/`, then `sleep 1`, then
  the solver) is reproduced verbatim — comparator clause C6.
- The one-iteration pre-flight smoke test for arm D is kept, in a scratch tree outside
  `verification/runs/`.

**Two departures, both stated, neither touching the data.** (1) **It does not grade** —
your standing instruction, and the frozen comparator can be run against the arm root at
any later time with nothing lost. (2) **It fires one arm** — A, B and C are read only for
their recorded cost.

**I did NOT reorder the levels to protect the gate level.** Under the frozen greedy
budget the order `L1, L2, L3, …` means a slow L1 starves L3, which is the gate. Moving
L3 first would protect the gate quantity — and it would be an outcome-affecting change to
a frozen executor made by a lane after seeing that C was starving. That is exactly the
shape of an answer-directed edit. It stays in the frozen order and I report the risk
instead (§6).

### 2.2 REFUSED — `C_RNGkEpsilon/L3_1000x5` and C's ladder

Your brief listed C/L3 as "never started" and told me to fire it. **I did not**, and the
reason is not the one in the brief: at 18:01Z it had no directory, but by **18:13Z the
live frozen launcher had created it and started the solver in it**. Firing it would have
put a second `simpleFoam` in a directory a live solver owns. C's ladder `D_500x3/4/6` is
the launcher's next work and is refused for the same reason.

### 2.3 Also established, as instructed

**Yes — `C_RNGkEpsilon` registers the `D_500x*` ladder exactly as A and B do.** Frozen
§10: *"The ladder D_500x3/4/6 … is run for **every** model. Both M2 comparators require it
(they refuse if a ladder level is missing)."* The launcher's `LEVELS` table is shared
across all four arms. So C's registered level set is six, not three, and D's is six.

---

## 3. EXISTING-BUT-INCOMPLETE DIRECTORIES — ENUMERATED, UNTOUCHED, AWAITING YOUR RULING

I applied the strict completion rule (rule 4, in the comparator's stricter C1–C6 form) to
all 14 directories present. **Thirteen are COMPLETE.** One is not, and one more is being
created as I write.

**`C_RNGkEpsilon/L2_500x5` — WAS incomplete at 18:06Z, and COMPLETED ITSELF at 18:13Z.**
It was never an abandoned run: it was the live solver. At 18:06Z it failed C1 (no
`RUN_RC.txt`), C2 (no `End`), C3 (last `Time = 11457` ≠ endTime 18000), C4 (no `18000/`)
and C5 (`ExecutionTime` count 11456 ≠ 18000) — **all five for the single reason that it
was 63.7 % of the way through.** It has since closed clean: `rc=0`, wall 1416 s,
23.6 core-min. **No ruling needed. This is the case for reading a directory's state
together with the process table before calling it a failure.**

**`C_RNGkEpsilon/L3_1000x5` — WILL BE INCOMPLETE, by budget, at ≈18:25Z.** Running now
under `timeout 670`, needing ≥666–675 s at zero model penalty and ~2800 s at the measured
penalty. It will fail **C1 (`rc=124`)**, and consequently **C2 (no `End` line)**,
**C3 (last `Time` < endTime 22000)**, **C4 (no `22000/` time directory)** and
**C5 (`ExecutionTime` count < 22000)**. C6 is not reached. **I am not touching it and I
am not re-launching it. That is your ruling, exactly as the predecessor team refused on
VMFL051 and was upheld.** Re-running it needs a new budget, and rule 12 does not give one.

The thirteen complete: `A_kEpsilon` 6/6, `B_realizableKE` 6/6, `C_RNGkEpsilon/L1_250x5`,
each passing C1 `rc=0`, C2 one `End`, C3 last time == its **own** `system/controlDict`
endTime, C4 the family field list, C5 `ExecutionTime` count == endTime, C6 every field at
endTime newer than that case's own `0/`.

---

## 4. THE SLOWDOWN IS NOT CONTENTION. IT IS THE MODEL. MEASURED.

You asked me to name contention. I measured it and it does not carry the effect, so I am
correcting the attribution rather than repeating it.

`C_RNGkEpsilon/L2_500x5` ran **4.16× slower** than `A_kEpsilon/L2_500x5` on the identical
mesh and endTime — 12.54 vs 52.23 iterations/s. The cause is in the logs:

| level | mean **p** linear-solver iterations per SIMPLE step | Ux | k | ε |
|---|---|---|---|---|
| `A_kEpsilon/L2_500x5` | **32.50** | 2.00 | 2.00 | 2.00 |
| `B_realizableKE/L2_500x5` | **27.14** | 2.00 | 2.00 | 2.00 |
| `C_RNGkEpsilon/L2_500x5` | **261.70** | 2.00 | 2.00 | 2.00 |

(means over the last 2000 iterations.) The momentum and turbulence equations are
**unchanged at 2.00**; the entire cost increase is the pressure equation, an
**8.05× conditioning penalty** that dilutes to 4.16× in wall time. `C/L1_250x5` shows the
same effect small (114.88 vs A's 96.47 p-iterations, 1.14× wall time) — consistent, and
it is why C/L1 finished inside budget and C/L2 did not.

**Contention, named separately and measured as not the cause.** Live on the box
throughout: three `buoyantBoussinesqSimpleFoam` (pids 2203927/2203944/2203947, started
≈16:37Z, `timeout` 66000/78000/165000 s), one DAFoam `docker` optimisation
(`d8_opt_20260825T165153Z`, `--cpus=1`, started ≈16:52Z, `timeout` 10800 s), and one
python at ~95 %. That is **five CPU-bound processes on 16 vCPU**; `/proc/loadavg` read
9.19–10.48 with 6 runnable of ~483. **Arms A and B ran alongside all of it at 53.90 and
55.74 it/s** — full speed. Your reading that load average is not CPU saturation here is
right, and the stronger statement the logs support is that **contention did not measurably
slow this case at all**. `N-`-family note offered for your read: *RNGkEpsilon degrades the
pressure-equation conditioning on this pipe by ~8× in linear iterations at fixed mesh,
while leaving momentum and turbulence solves untouched.*

---

## 5. GRADING — ARMS A AND B (your second task; arms C and D NOT graded)

### (a) Comparator identity and exit code

`cases/ansys_verification/VMFL003_M2/grade_vmfl003_m2.py`, blob re-verified **in the
grading invocation**: HEAD == disk == `6dcc99940154ea204a598ba2118042bf972a786d`. Its own
`--verify-frozen HEAD` passed. `--selftest`: **63 checks, 0 failures**. **Exit code 0 for
both arms** — the comparator did not refuse; it graded and returned a verdict.
No edits, no workarounds, nothing hand-computed.

### (b) Planted-zero controls — all three fired, read back from disk

| control | planted | expected | seen |
|---|---|---|---|
| Δp **and ρ** | `PLANT_DP = 1.234` m²/s² into the **kinematic** inlet column | move Δp by `1.234 × 1.225 =` **1.51165 Pa** | **1.5116500000003725 Pa** (both arms) |
| wall y+ | `PLANT_YPLUS = 7.77` into the `average` column | 7.77 | **7.770000000000003** |
| f_dev | `PLANT_SLAB = 2.345` m²/s² into `pSlabA` `volAverage(p)` | **9.38e−06** | **9.379999999992866e−06** (A), **9.379999999999805e−06** (B) |

Tolerance `PLANT_TOL = 1e−9`, all three inside it. The Δp control is the strong one: it
plants a **kinematic** value and demands the graded number move by `PLANT × ρ`, so a
ρ-blind reader is refused rather than believed. The reader was shown able to see a
non-zero before its zero was accepted.

### (c) Per arm at the gate level `L3_1000x5`

| | **M2-A `kEpsilon`** | **M2-B `realizableKE`** |
|---|---|---|
| Δp_lab | **20800.824488 Pa** | **20278.128649 Pa** |
| dev vs 21744 Pa | **−4.337636 %** | **−6.741498 %** |
| gate band (frozen §5) | ±2.5 % | ±2.5 % |
| **gate verdict before rule 5** | **`GATE FAIL`** | **`GATE FAIL`** |
| **VERDICT** | **`NOT A RESULT`** | **`NOT A RESULT`** |
| tier ceiling | `GATE REACHED` | `GATE REACHED` |
| reference kind | **V** (category 2, correlation; ruled) | **V** |
| dev vs Colebrook 21792.88 Pa | −4.552199 % | −6.950670 % |
| f_dev at L3 | 0.027147309072 | 0.026462670384 |
| mean wall y+ / min y+ | 37.600 / **23.812** | 37.491 / **23.784** |
| ladder spread (max 5 %) | **1.7356 %** | **0.6746 %** |

Both are `NOT A RESULT` for one reason, and it is **not** the gate: **every level of both
arms fails the registered iterative-convergence leg** (final initial residuals of p, Ux,
k, ε each < 1e−8). Under rule 5 step 1 that precedes the triple and precedes the band.
The gate can only turn a verdict **into** `NOT A RESULT`, never the reverse — and it did.

**The finding inside that, and it matters: the endTime bump did NOT repair Defect B.**
§12 registered 15000/18000/22000 as the repair for run 1's residual miss. At A/L3 with
22000 iterations, p = 2.38e−10, Ux = 4.62e−09, k = 1.94e−09 all clear 1e−8 comfortably —
and **ε = 2.494e−08 does not**, missing by 2.5×. Run 1's L3 missed on **ε alone at
2.523e−08**. Ten thousand extra iterations moved ε's residual by 1 %. **ε's residual is
stalled, not slow, and more iterations will not clear it.** B/L3 misses on ε (7.49e−08)
and k (1.38e−07). Meanwhile Δp at A/L3 = 20800.8245 Pa against run 1's 20800.82 — agreeing
to 8 significant figures across 12000 vs 22000 iterations, with plateau ptp 5.35e−06 Pa.
**The answer is converged; the residual is not.** Defect A and Defect B are confirmed
genuinely separate, and Defect B is now shown to be un-repairable by iteration count.

### (d) The L1/L2/L3 triples

| arm | f_coarse (L1) | f_med (L2) | f_fine (L3) | monotone | state | observed order p | GCI |
|---|---|---|---|---|---|---|---|
| A | 20802.991897 | 20800.985808 | 20800.824488 | true | **`CONVERGING`** | **3.6364** | **NOT QUOTED** |
| B | 20280.507376 | 20278.466838 | 20278.128649 | true | **`CONVERGING`** | **2.5930** | **NOT QUOTED** |

Both triples are `CONVERGING`, so the triple is not what makes these rows `NOT A RESULT`.
**No GCI is quoted for either**, and the comparator suppressed it itself
(`gci_quoted: false`, `gci_fine: null`, `f_extrap: null`) because the verdict is
`NOT A RESULT` — it will not attach a discretisation-uncertainty number to a row that is
not a result. Both observed orders also sit **outside the frozen trust window [0.5, 2.5]**
(A at 3.6364; B at 2.5930, only just outside), extracted from level differences of
−0.161 Pa and −2.006 Pa on a ~20800 Pa quantity — 8 ppm. Exactly the carried-forward
limitation §9 pre-declared. The orders are reported, not trusted, and no GCI stands on
them.

### (e) The five §7 arms, registered before any number existed

**Arm 1 — the gate (reproduction). FIRED AS `GATE FAIL` FOR BOTH.** Registered: in-band →
`GATE REACHED`; outside → `GATE FAIL`. A at −4.3376 % and B at −6.7415 % are both outside
±2.5 %. Rule 5 then supervenes on the reported verdict.

**Arm 2 — f_dev (mechanism), threshold > 1.0 % from 0.027147.**
- **A: NOT materially moved** — f_dev 0.027147309, **+0.001139 %**. Expected: it is the
  same model as run 1, and it reproduced it.
- **B: MATERIALLY MOVED — −2.5208 %** vs the registered 0.027147, and **−2.5219 %** vs
  M2-A. Over the 1.0 % threshold by 2.5×.

**Arm 3 — the M2-A prediction. CONFIRMED, on both limbs.** Registered: `GATE FAIL` at
−4.0…−4.6 %, f_dev within 0.3 % of 0.027147. Measured: **−4.337636 %**, inside the
predicted window; **f_dev +0.001139 %** from 0.027147, inside 0.3 % by 263×. Its
falsification condition — *"falsified if the converged baseline lands in-band"* — did not
occur. **A gate failure predicted in advance to a quarter of a percent, and delivered.**

**Arm 4 — the M2-B/C prediction. REFUTED. This is the reportable finding.** Registered:
both stay `GATE FAIL` **within ~1 % of M2-A on Δp and f_dev**, on the stated mechanism
that *"with a standard log-law wall function the wall shear τ_w is imposed by the log law
from the first-cell k, not computed by the interior closure, so high-Re k-ε variants
sharing the wall function share their friction."* Registered falsification: *"Falsified
(and the reportable finding) if either lands in-band **or moves f_dev > 1 % from M2-A**."*
**B moved f_dev by −2.5219 % and Δp by −2.5129 % from M2-A — both over 1 %.** The
falsification condition fired on its own terms. **The mechanism claim is wrong:
`realizableKE` shares `nutkWallFunction` with `kEpsilon` and still moved wall friction by
2.5 %.** The interior closure reaches the wall shear through the first-cell k it feeds the
wall function; the wall function does not insulate the friction from the model. Arm 4's
other limb held — B did stay `GATE FAIL` — but the registration said *either* condition
refutes, and one did. C, which would have been Arm 4's second test, is not graded.

**Arm 5 — the falsification arm. DOES NOT FIRE, and this is already final.** Registered:
if all four models' L3 Δp deviations lie within a band of width **≤ 1.0 %** of each other
**and** all four are `GATE FAIL` in −4.0…−5.0 %, then model selection is not the answer.
Measured on A and B alone: the band is **2.403862 percentage points wide** (−4.3376 % to
−6.7415 %), and **B at −6.7415 % is outside the −4.0…−5.0 % window**. **Adding C and D can
only widen a max−min spread, never narrow it, so the ≤ 1.0 % limb is permanently
falsified with two arms outstanding.** The registration's own hypothesis therefore stands:
**model selection is NOT irrelevant here — it moved Δp by 2.5 %.** It moved it the wrong
way. `realizableKE` is **further** from the manual target than `kEpsilon`, not closer:
−6.74 % against −4.34 %. The ~4.6 % deficit is not a wall-function artefact common to all
k-ε variants, and no model in the slate has yet recovered it.

**On the wall-treatment ladder, reported and kept out of the gate.** The `D_500x*` levels
are the y+/wall-treatment ladder, not the grid family, and no D-level number entered the
gate. A spans 20503.59→20863.12 Pa across N_r = 3/4/6 (**1.7356 %**, mean y+ 60.02→31.66);
B spans 20142.03→20263.74 Pa (**0.6746 %**, y+ 59.93→31.48). Both clear the 5 % one-way
clause. **A's wall channel is 2.6× B's**, so the two models' friction responds to wall
placement quite differently — a per-closure measured output, as §10 intended.

### (f) Estimate-versus-actual calibration (rule 12)

| | Roache legs | ladder | **arm total** | pred | **ratio** | arm cap 40 |
|---|---|---|---|---|---|---|
| **A** | 21.3833 (pred 16.8, **1.273×**) | 8.5667 (pred 11.3, **0.758×**) | **29.9500** | 28.1 | **1.0658** | 74.9 % used |
| **B** | 21.4333 (pred 16.8, **1.276×**) | 9.7000 (pred 11.3, **0.858×**) | **31.1333** | 28.1 | **1.1079** | 77.8 % used |

**A + B measured 61.0833 core-min against 56.2 predicted — ratio 1.0869.** Dollars:
1.018056 core-h × $0.0513/core-h = **$0.05223**, **DERIVED, NOT MEASURED**; `cost_basis` =
owner-stated rate (c7a.4xlarge, Sanaa 2026-08-21/22) — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 CPU blanket, still costed per item.

**The gap attributed, with contention named separately and NOT absorbed.** The frozen
basis was a single aggregate 5.806e−6 s/(cell·iter). Measured against arm A:

| level | wall s | s/(cell·iter) | × basis |
|---|---|---|---|
| L1_250x5 | 274 | 1.4613e−05 | **2.517** |
| L2_500x5 | 334 | 7.4222e−06 | 1.278 |
| L3_1000x5 | 675 | 6.1364e−06 | 1.057 |
| D_500x3 | 153 | 5.6667e−06 | 0.976 |
| D_500x4 | 131 | 3.6389e−06 | 0.627 |
| D_500x6 | 230 | 4.2593e−06 | 0.734 |

The rate is **not constant** — it falls monotonically with mesh size, from 2.52× basis at
1250 cells to 1.06× at 5000. That is a **fixed per-iteration overhead floor**, exactly the
confound §0 flagged when it abandoned run 1's 1.6× multiplier. **Misprediction, +8.7 %,
is the whole of the gap.** **Contention: named, and measured at ~0 for these two arms** —
three `buoyantBoussinesqSimpleFoam`, one DAFoam docker container (`--cpus=1`) and a python
at 95 % were live throughout arms A and B, five CPU-bound processes on 16 vCPU, loadavg
9.19–10.48 with 6 runnable of ~483, and A/L2 and B/L2 still ran at 53.90 and 55.74 it/s.
**Waste: none identified for A and B.** Separately, the slate's real cost overrun is arm C
(§4), a model-conditioning effect, not contention and not contention's to absorb.

Slate running total on disk: **89.9000 of the frozen 160 core-min cap** (A 29.9500 +
B 31.1333 + C/L1 5.2167 + C/L2 23.6000). Arm C is at **28.8167 of its 40**, which is what
leaves C/L3 only 670 s.

### (g) Register rows — DRAFTED, **NOT APPENDED**. Your ruling.

Next id derived **by hand** from the HEAD blob: existing rows are 1–8, maximum **8**
(a maximum, never a count — rule 11), so these are **#9** and **#10**.
`scripts/append_record.py` was not used; it hands out colliding ids.

> **#9** | **VMFL003-M2-A** — Pressure Drop in Turbulent Flow Through a Pipe, model slate
> arm A `kEpsilon` (VM2026R1, pp. 19–20) | 2026-08-25 | **`NOT A RESULT`** | Δp =
> **20800.824488 Pa** at `L3_1000x5`, **−4.3376 %** vs target; gate verdict before rule 5
> **`GATE FAIL`**; `NOT A RESULT` because all three levels fail the registered
> iterative-convergence leg (L3 on **ε alone, 2.494e−08 vs < 1e−08**). Triple
> `CONVERGING`, observed order 3.6364 **outside the frozen trust window [0.5, 2.5]**, **no
> GCI quoted**. Three planted-zero controls fired (Δp·ρ 1.51165 Pa; y+ 7.77; f_dev
> 9.38e−06). Ladder spread 1.7356 %; mean y+ 37.600, min 23.812 | **21744 Pa** —
> Moody-chart / Colebrook smooth-pipe correlation as printed in the manual's Target
> column, **manual p. 19**. Context only: Fluent 21480, CFX 21740 | **2.5 % relative at
> `L3_1000x5`** (frozen §5) | `verification/runs/ansys_verification/VMFL003_M2/A_kEpsilon/`
> | `cdbf2659b6eec2599fc3eda7a149aaca391461b0` | `6dcc99940154ea204a598ba2118042bf972a786d`
> | **29.9500** | **$0.02561** (derived) | *pending supervisor ruling* |
> **Tier: `GATE REACHED` ceiling (not attained). Reference kind: V.**

> **#10** | **VMFL003-M2-B** — same case, arm B `realizableKE` (VM2026R1, pp. 19–20) |
> 2026-08-25 | **`NOT A RESULT`** | Δp = **20278.128649 Pa** at `L3_1000x5`, **−6.7415 %**
> vs target; gate verdict before rule 5 **`GATE FAIL`**; `NOT A RESULT` on the same
> iterative-convergence leg (L3 ε 7.49e−08, k 1.38e−07). Triple `CONVERGING`, observed
> order 2.5930 outside [0.5, 2.5], **no GCI quoted**. Three planted-zero controls fired.
> Ladder spread 0.6746 %; mean y+ 37.491, min 23.784. **Refutes registered Arm 4**: f_dev
> moved **−2.5219 %** from arm A against a 1.0 % falsification threshold, so a shared
> log-law wall function does **not** fix wall friction across k-ε variants | **21744 Pa**,
> manual p. 19 | **2.5 % at `L3_1000x5`** |
> `verification/runs/ansys_verification/VMFL003_M2/B_realizableKE/` |
> `cdbf2659b6eec2599fc3eda7a149aaca391461b0` | `6dcc99940154ea204a598ba2118042bf972a786d`
> | **31.1333** | **$0.02662** (derived) | *pending supervisor ruling* |
> **Tier: `GATE REACHED` ceiling (not attained). Reference kind: V.**

**Neither row is a credential.** Only `PASS` rows are. The credential-count line moves
`3 PASS of 8 run` → **`3 PASS of 10 run`** — **the denominator only**. Rows #1–#8 are not
edited. A `COST_CALIBRATION.md` row is owed for each; ids must be derived by hand from the
HEAD blob in the committing invocation, not from `append_record.py`.

### (h) Charter / doc update line

**NOT `NONE`.** One line is owed, and it is a numerics fact rather than a charter change:
**`docs/NUMERICS_KNOWLEDGE.md`** — *RNGkEpsilon degrades pressure-equation conditioning by
~8× in linear-solver iterations per SIMPLE step on this R⁺ = 408 pipe at fixed mesh
(261.70 vs 32.50 for `kEpsilon`, 27.14 for `realizableKE`), while leaving momentum and
turbulence solves unchanged at 2.00 — a 4.16× wall-time penalty that a cost model built on
one aggregate s/(cell·iter) figure cannot see, and which starved the frozen per-arm cap.*
A second, for the same file or `LESSONS.md` at your discretion: *a wall-function-modelled
k-ε variant does not inherit its friction from the wall function — `realizableKE` moved
f_dev 2.52 % while sharing `nutkWallFunction` with `kEpsilon` (M2 Arm 4, refuted).*
I draft; the append and the numbering are yours.

---

## 6. WHAT I COULD NOT DO, WITH NAMED BLOCKERS

| item | state | **named blocker** |
|---|---|---|
| `C_RNGkEpsilon/L3_1000x5` | **NOT FIRED BY ME** | A live solver owns the directory (pid 2360989, under the frozen launcher, `timeout 670`). Firing = two solvers in one case. |
| `C_RNGkEpsilon/D_500x3/4/6` | **NOT FIRED** | The live frozen launcher owns them next. Also: arm C has **11.18 of its 40 core-min** left and C/L3 will consume all of it. |
| Arm C grading | **NOT DONE** | Your instruction, and correct: an incomplete arm has no triple. |
| Arm D grading | **NOT DONE** | Your instruction. |
| **Arm D completing all six levels** | **AT RISK** | The frozen **40 core-min per-arm cap** against an unknown `kOmegaSST` pressure-conditioning penalty. If D behaves like A/B (~30 core-min) all six run. If it behaves like C (4.16×) the greedy frozen order spends the cap on L1 and L2 and **the gate level L3 never runs.** I did not reorder to protect it (§2.1). |
| The slate launcher surviving past ≈18:25Z | **WILL NOT** | `rc=124` on C/L3 trips its own `[ "$RC" -eq 0 ] \|\| exit 1` guard. Rule 12 gives no new budget; raising a frozen cap is not a lane's call. |

**On your desk, and only yours:** (1) whether C/L3's budget-killed directory may be
re-launched as a new rung under a fresh cap — I will not touch it; (2) whether arm C's
ladder is re-fired after the launcher dies; (3) whether arm D's per-arm cap survives
contact with an 8× pressure penalty, should one appear; (4) the two register rows and the
credential denominator; (5) the two `NUMERICS_KNOWLEDGE` lines. **No agent message is
Sanaa's consent (rule 9)**, and nothing above was sent anywhere.
