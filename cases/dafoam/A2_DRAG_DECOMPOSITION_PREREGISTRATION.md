# A2 — decomposing the 28.3% drag reduction — PRE-REGISTRATION (frozen, NOT launched)

Filed 2026-09-01, dafoam lane, against Sanaa's Act D feedback fix 2 of
2026-09-01T0042Z (`etc/sessions/2026-09-01T0042Z_sanaa_actD_feedback.md`, item 2):
*"how much of the drag drop is twist (spanload/induced drag) vs section shape vs AoA
retrim? ... One table: baseline -> twist-only -> twist+shape -> final, Cd at each."*

**No compute has been spent on this and none will be until the supervisor gives the
launch go.** The run root asserted absent below does not exist at freeze time.

---

## 1. Provenance of the subject — verified at source before anything was frozen

The claim is A2's **28.3% drag reduction at matched CL = 0.5** on the MACH Tutorial
Wing (38,304 cells, `DARhoSimpleFoam`, compressible SA RANS),
`DAFOAM_CASE_STATUS.md:72`.

`W5_GRADIENT_REGRADE.md` §3a (2026-08-01) ruled this line's gradient rows
**NOT REGRADED / "cannot currently be re-verified"**. That section is **struck through
in the file itself** at `W5_GRADIENT_REGRADE.md:213` and marked *"RETRACTED 2026-08-02
(well W4). Every A2 run in this section invoked the wrong script."* The original text is
retained beneath it (rule 6, supersede-not-delete). The supersession is verified here
independently, at source, and it holds:

| what the supersession asserts | source | verified |
|---|---|---|
| W5 ran `runScript.py` (aerostructural, TACS+FUNtoFEM, `aoa0=4.65`); the published numbers are `runScript_AeroOnly.py` (`aoa0=4.0`) | `PROOF.md:2489-2499` | yes — and the two scripts separate cleanly in the logs, 0 vs 6 `MELD`/`Tacs` mentions (`PROOF.md:2502-2505`) |
| pristine-clone primal returns CD 0.02772949388 / CL 0.4775877833 to all ten printed digits | `PROOF.md:2516-2519` | yes |
| `check_totals` returns **18 of 18 rows identical to the published log to every printed digit** | `PROOF.md:2544` | yes |
| regraded under the corrected IDWarp derivative, **all six VERIFIED rows HOLD, PASS at both toolchains** | `PROOF.md:2596-2598` | yes |

One independent corroboration found while checking: the pristine clone's
`runScript_AeroOnly.py` hashes **md5 2906d52a5dbed2bacbaeaf85a37d3fe8**, byte-identical
to the preserved case's copy and to the hash `PROOF.md:2512-2513` records. The instrument
this decomposition will run is the same instrument that produced the published numbers.

**One narrowing, stated plainly because the brief's wording is slightly wider than the
record.** What was re-measured and re-graded is the **gradient verification underneath**
the 28.3%. `PROOF.md:2599` puts it exactly: *"the gradients behind the 28.3% drag
reduction are verified."* The **optimisation run itself has never been re-executed**, and
`W5_GRADIENT_REGRADE.md:373` still lists *"S11 (28.3% drag reduction): still NOT
REGRADED"* — a line the retraction block above it does not individually withdraw. So the
28.3% rests on: a preserved history file, plus verified gradients, plus a preserved
optimiser log. This pre-registration is the first work to re-evaluate its endpoints.

## 2. What is recoverable — checked before costing, at zero compute

`/home/ubuntu/certonomous-runs/A2-mach-wing/OptView.hst`
(sha256 `7c062f7c629f6a09758059f3c645f54f1a21dca934cdeff7d9e326a96f89f8a1`) is a
pyOptSparse history in SQLite: **242 records, 146 of them carrying evaluated
functions**, each with the full design-variable vector (`twist` 7, `shape` 96, `patchV`
2) and CD, CL, `thickcon`, `volcon`. **The design-variable vector IS recoverable.**

`xuser` is stored in **driver space**; physical values are recovered with the script's own
`scaler`s (`runScript_AeroOnly.py:173-175`), and the recovery is self-proving because
driver `patchV[0] = 10.0` maps to the script's `U0 = 100.0`:

| group | scaler | driver -> physical |
|---|---|---|
| `twist` | 0.1 | x 10 |
| `shape` | 10.0 | x 0.1 |
| `patchV` | 0.1 | x 10 |

Endpoints, physical units, from records 0 and 241:

| quantity | baseline (rec 0) | final (rec 241) |
|---|---|---|
| CD | 0.029619634 | 0.021241506 |
| CL | 0.499999958 | 0.499948193 |
| angle of attack | 4.32612781 deg | 1.10765738 deg |
| twist, 7 stations root->tip | all 0 | -0.020, -0.235, -0.842, -1.683, -0.367, -2.596, -2.265 deg |
| shape, 96 FFD | all 0 | min -0.3871, max +0.3871 (bounds +/-1.0; none at bound) |
| thickness / baseline, 100 pts | 1.000 everywhere | 0.500101 to 1.727944; **9 pts pinned at the 0.5 floor** |
| `volcon` | 1.000000 | 1.00007830 (lower bound 1.0, active) |

Reduction from these two rows: **28.2857%**, reproducing the published 28.3%.

**Three premise corrections, recorded here because they change what the page may say:**

1. **"Twist moved -3 deg outboard" is high.** Measured maximum is **-2.596 deg** at the
   second-outboard station, **-2.265 deg** at the tip. Report the vector, not "-3".
   Separately: `runScript_AeroOnly.py:141-143` negates the design variable into
   `rot_z` (`geo.rot_z[...].coef[i] = -val[i-1]`), so the **sign of the physical twist
   is not readable off the design variable alone**. This pre-registration does not
   assert washout or washin; row A1 measures which it is.
2. **"Section shape moved 31% of local thickness" reconciles, but only as an RMS.** The
   RMS of |thickness change| / baseline thickness over the 100 constraint points is
   **31.90%**; the mean is 25.91%. The far more informative measured statement is the
   range: **0.50x to 1.73x baseline thickness, with 9 of 100 points pinned exactly at
   the 0.5 lower limit** — the optimiser thinned the section to the floor it was allowed,
   and held total volume at its minimum (`volcon` 1.0000783 against a bound of 1.0).
3. **The baseline is already lift-matched, and this is the strongest single piece of
   evidence against the trap Sanaa is testing for.** `findFeasibleDesign`
   (`runScript_AeroOnly.py:241`) re-trimmed angle of attack to CL = 0.5 **before**
   iteration 0, moving the reference point from CD 0.02772949 at CL 0.4776 to CD
   0.02961963 at CL 0.5000 — **a 6.816% drag INCREASE, paid into the baseline before the
   optimiser started**. The 28.3% is measured from the more expensive, lift-matched point,
   not the cheaper unmatched one.

## 3. The structural point that decides the AoA question in advance — and how it is tested

CL = 0.5 is an **equality constraint** (`runScript_AeroOnly.py:179`) and it is satisfied
at both endpoints (0.4999999 and 0.4999482). Angle of attack is therefore not a free
drag lever in this problem: **at matched lift it is slaved to the geometry.** It follows
that "twist + shape, re-trimmed to CL = 0.5" **is** the final design — there is no
remaining degree of freedom. The AoA share of the reduction at matched lift is
**structurally zero**, not an empirical finding.

That is an argument, so it is registered as a prediction and it is given a way to fail:
row **B2** re-trims twist+shape to CL = 0.5 independently and must land on row **A4**
(gate G5). If it does not, the argument is wrong and Path B is NOT A RESULT.

The trap Sanaa names — *"a 30% reduction that was mostly AoA"* — would show up as a
baseline that is **not** at the target lift. The pre-registered test for it is therefore
G6 below, on the CL column, not on an AoA share.

## 4. The rows — frozen in `a2_decomposition_rows.json`

sha256 `7a3ec1b34f72fd38e040f8abc8e47adf184045c8f0faf390dda49bd46cb0655b`. Evaluated in
this order, in one container session. **Both gate rows land in the first five solves**, so
a cap-stop still decides the gates.

| row | twist | shape | angle of attack | purpose |
|---|---|---|---|---|
| `A0_baseline` | 0 | 0 | 4.32613 deg | gate G1; reproduction control |
| `A1_twist_only` | final | 0 | 4.32613 deg | Sanaa's twist-only row, lift NOT matched |
| `A2_twist_shape` | final | final | 4.32613 deg | Sanaa's twist+shape row, lift NOT matched |
| `A3_aoa_only` | 0 | 0 | 1.10766 deg | **the trap row**, shown deliberately |
| `A4_final` | final | final | 1.10766 deg | gate G1; **planted control**; warm-start control |
| `B1_twist_only_CL05` | final | 0 | re-trimmed | twist share at matched lift |
| `B2_twist_shape_CL05` | final | final | re-trimmed | gate G5 against A4 |

Path A is the literal table Sanaa asked for. It holds angle of attack fixed, so **CL will
not be 0.5 on rows A1, A2 and A3** and their drag is not comparable to the baseline's.
Path B is the lift-matched decomposition — the only one from which a drag attribution may
be quoted. **Both are reported; the CL column is printed beside every drag figure so no
row can be read without its lift.**

## 5. Predictions — committed before the solver starts

Registered so the answer cannot be fitted afterwards. Being wrong here costs nothing;
editing them after the run would cost everything.

| row | predicted CD | predicted CL | reasoning |
|---|---|---|---|
| A0 | 0.029619634 | 0.5000 | reproduction |
| A1 | 0.0255 – 0.0290 | 0.44 – 0.49 | twist removes outboard load; **if CL rises instead, the `rot_z` sign is opposite to my reading and I will say so** |
| A2 | 0.045 – 0.075 | 0.70 – 0.90 | geometry must add ~0.29 CL at fixed incidence, since 3.22 deg of incidence was given back at fixed CL |
| A3 | 0.013 – 0.019 | 0.16 – 0.26 | baseline wing at the final incidence: a 35–55% "drag cut" at roughly half the lift |
| A4 | 0.021241506 | 0.49995 | reproduction |
| B1 | 0.0290 – 0.0310 | 0.5000 | angle of attack must RISE above 4.326 deg to recover the lift twist removed |
| B2 | = A4 within 0.5% | 0.5000 | no free variable remains |

**Headline predictions, as shares of the 8.378e-3 total drag reduction, at matched lift:**

- twist share: **+2%**, admissible band **-5% to +8%**
- section shape share: **~98%**, admissible band **92% to 105%**
- angle-of-attack retrim share: **0%**, structurally (§3)

**If the measurement contradicts these, the measurement is the finding and it goes on the
page.** Specifically: if the lift-matched twist share exceeds 50% the headline becomes
"mostly twist"; if the angle-of-attack share exceeds 5% at matched lift, §3's argument is
falsified, the trap is confirmed, and the 28.3% is DOWNGRADED on the customer page to a
lift-corrected figure per Sanaa's own alternative.

## 6. Gates — binary, fixed here, graded on the run's own log

| id | gate | threshold | on failure |
|---|---|---|---|
| **G1** | reproduction | A0 CD within **0.5%** of 0.029619634 AND A4 CD within **0.5%** of 0.021241506 | whole decomposition **NOT A RESULT** |
| **G2** | geometry control | `thickcon` at A0 = 1.0 on all 100 pts to 1e-6; at A4 min in [0.4995, 0.5006] and max in [1.726, 1.730] | **NOT A RESULT** — the shape vector never reached the mesh |
| **G3** | trim tolerance | every Path-B row reaches \|CL - 0.5\| <= **5e-4** | that row **BLOCKED**, reported as such, not estimated |
| **G4** | completion | per row: `rc = 0`, primal meets the case's own `primalMinResTol = 1e-8`, CD and CL read from that row's own `DECOMP_RESULT` line | that row **NOT A RESULT**; it is reported, never dropped |
| **G5** | self-consistency | \|CD(B2) - CD(A4)\| / CD(A4) <= **0.5%** | Path B **NOT A RESULT**; §3's argument is falsified and that is reported |
| **G6** | the trap test | baseline CL and final CL both within **1e-3** of 0.500 | the 28.3% is not a matched-lift comparison and is **DOWNGRADED** on the page |

**Planted-zero control (rule 3), two independent witnesses, both wired into the driver:**

1. **Design-variable readback.** Every row reads its vector back out of the problem and
   **refuses** (`DECOMP_REFUSE`, `RuntimeError`) on any mismatch above 1e-12. A row whose
   vector silently failed to take would otherwise return the baseline drag and read as a
   result.
2. **`thickcon` as a geometry-side witness.** It is exactly 1.0 on all 100 points at
   baseline and spans [0.500101, 1.727944] at the final geometry. A shape vector that
   never reached the mesh reads 1.0. This is a known non-zero the reader is required to
   see, and G2 refuses if it does not.

Row **A4** is additionally the **warm-start control**: it runs fifth, after three rows
have moved the state, and must still reproduce a value 28% away from the baseline. It is
placed late deliberately — reproducing it from a warmed state is the evidence that
sequential evaluation in one process is not biasing the table.

## 7. Instrument, frozen

| file | sha256 |
|---|---|
| `cases/dafoam/a2_decomposition_driver.py` | `c4f421497ae221ae1f8fb2f655530ea552e6372a935a6d3e0355ce81a4389cf0` |
| `cases/dafoam/a2_decomposition_rows.json` | `7a3ec1b34f72fd38e040f8abc8e47adf184045c8f0faf390dda49bd46cb0655b` |
| `cases/dafoam/run_a2_decomposition.sh` | `14f946457d868cd92efc0f989e5954a65f1985371185791213ab46613b3444ca` |

The driver is the pristine `runScript_AeroOnly.py`
(md5 `2906d52a5dbed2bacbaeaf85a37d3fe8`) with **one added `elif` block, 72 lines added,
zero lines deleted or modified**. The launcher re-asserts that md5 before it copies
anything and writes the full diff to `driver_vs_pristine.diff` beside the run, so the
"one added block" claim is checkable without trusting this document.

**Run root, asserted ABSENT at freeze time:**
`/home/ubuntu/certonomous-runs/ACTD-a2-decomposition` — checked 2026-09-01,
`ls` returns "No such file or directory". The launcher refuses (exit 2) if it exists.

## 8. Cost — pre-registered per rule 12

Basis, measured, not guessed: the optimiser evaluated **146 primals in 3606 s wall at 4
ranks** (`A2_mach_tutorial_wing.md:80,§6`) = **24.7 s per evaluation**; the W4 pristine
rebuild cost **2.67 core-min** including mesh generation (`PROOF.md:2526`).

| item | count | basis | core-min |
|---|---|---|---|
| mesh build + OpenMDAO/DAFoam setup | 1 | ~80 s wall x 4 | 5.3 |
| Path A primals | 5 | 24.7 s x 4 | 8.2 |
| B1 re-trim + confirm | 6 | 24.7 s x 4 | 9.9 |
| B2 re-trim + confirm | 5 | 24.7 s x 4 | 8.2 |
| **predicted total** | **16 primals** | | **~32 core-min** |

**Hard cap: 60 core-min = 900 s wall at 4 ranks**, enforced by `timeout 900s` inside the
container. **An overrun stops the run; it does not get a new budget.** Rows completed
before the cap are graded on their own gates; rows not reached are **PENDING**, never
estimated.

Dollars, **derived not measured**: 32 core-min = 0.533 core-h -> **$0.027**; at the cap,
1.0 core-h -> **$0.051**. Rate **$0.0513/core-h, c7a.4xlarge, reported-by-owner
(2026-08-21/22), never measured — this box cannot read its own billing.** Under the $25
pre-authorisation with four orders of magnitude to spare.

Per rule 12's calibration clause, the completion report will carry actual core-minutes
from the run's own `t0`/`t1` ledger against the 32 predicted here, with the ratio and its
attribution.

## 9. Status

**FROZEN, NOT LAUNCHED.** Awaiting the supervisor's check 4 and launch go. No solver has
been started; the run root does not exist.

## 10. Pre-compute amendment 1 — 2026-09-01, variable paths verified

**Condition, and how it was checked:** legal under rule 2 because no compute has been
spent. The run root `/home/ubuntu/certonomous-runs/ACTD-a2-decomposition` **still does
not exist** — `ls` returns "No such file or directory" at the time of this amendment.
No gate, threshold, cap, label or prediction above is altered by it.

The driver reads four model variables that had never been executed. All four are now
confirmed present, at zero compute, in the **published verification log's own output**
(`/home/ubuntu/certonomous-runs/A2-mach-wing/check_totals_run1.log`, the log
`PROOF.md:2544` reproduced 18 of 18 rows against):

`scenario1.aero_post.functionals.CD`, `scenario1.aero_post.functionals.CL`,
`geometry.thickcon`, `geometry.volcon` — all four appear verbatim as `Full Model: '...'`
row headers. The design variables are `dvs.twist`, `dvs.shape`, `dvs.patchV` there; the
driver sets them by their promoted names `twist`, `shape`, `patchV`, which is the same
form the script itself uses at `runScript_AeroOnly.py:168-170`, valid because `dvs` is
added with `promotes=["*"]` (`:104`).

**Residual untested path, disclosed:** `optFuncs.findFeasibleDesign` has never been
called mid-sequence, only once at the start of a run. It is used only by rows **B1** and
**B2**, which execute **after** both gate rows. A failure there costs the Path B rows and
leaves Path A and both gates intact and gradeable.
