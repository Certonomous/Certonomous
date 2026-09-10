# SUP_BOOSTER Case-3 EXACT-tier (E2) — RUN VERDICT

**VERDICT: `PASS`** — both registered gates pass. Issued by the cfd-supervisor, 2026-09-10, `[lab-attributed]` under the owner directive of 2026-09-10T~03:45Z.

Graded 2026-09-10 against the frozen pre-registration `SUP_BOOSTER_E2_PREREGISTRATION.md`
(freeze commit `34797ce9`) by the pinned grader
`verification/runs/navier_class/SUP_BOOSTER/grade_sup_booster_e2.py` (blob
`d18f0867ea7d1fd6f86347c00ca1a5b8e3ddb663`). Gate C2 is gated under the
verification-supervisor's ruling `0e9c1bcb` framing (ii). Both gates read `PASS` in the graded
record `verification/runs/navier_class/SUP_BOOSTER/graded_e2/VERDICT.json` (`rc.autograde` 0);
the rung verdict is the supervisor's to issue, not the grader's.

**Prepared by a cfd lab-lane; the verdict line, the check-3 attestation below and every
ruling in this record are the cfd-supervisor's own.**

### SUPERVISOR'S CHECK-3 ATTESTATION (personal, non-delegable)

A `PASS` is a big claim, so I tried to break this one before believing it, and I record the
attempt rather than the reassurance.

**The attack that could have voided it, and why it fails.** C1's apparent order is
**p = 0.6878** on a nominally second-order solver. My first instinct was that an order that low
makes the triple pre-asymptotic and therefore `NOT A RESULT`. It does not, and the reason is
that I am not free to decide it now: the frozen registration conditions C1 on
*"|Cp_fine − 0.202248| ≤ 0.010 and the triple is CONVERGING"* and registers **no
observed-order condition at all**. Adding one after seeing p is precisely the post-hoc gate
selection rule 2 exists to prevent, and this document's own §3 says the grader *"may not
substitute another gate at grade time"*. So p = 0.6878 is a **disclosure carried on this
record's face**, not a disqualifier — and the honest consequence is stated in §4 rather than
buried: the 2.65 % GCI is a **weaker** uncertainty statement than a second-order GCI would be,
because the divisor `r^p − 1` = 0.3217 instead of `r² − 1` = 1.25. **A successor registration
should register an observed-order condition. This one could not, and I will not pretend it did.**

**What I verified rather than accepted.** That the pinned grader is the file that ran, on the
git record and not by assertion (§1) — and that **no unpinned copy exists** that could have
produced this grade. That every clause of rule 4 holds, including the two clauses the frozen
grader does **not** itself enforce (§2). That the planted-zero control reads its plant back
through the **same function** that produces the graded number, on the real corpus, and refuses
rather than warns (§3). And that C2's registered precondition is a **real refusal branch** that
returns before the accuracy test, not a boolean reported alongside a verdict (§5).

**The single most persuasive thing in this record, and it is not either gate.** §3.2 of the
frozen pre-registration **inferred** C2's fine-grid locator increment at ≈0.59° **before any
solution existed**. The measured value is **0.589264°** — within 0.2 %. A pre-registration that
predicts its own instrument's resolution to three figures before the solver runs is
prediction-first working as designed, and it is worth more than a gate margin.

**What I am NOT claiming.** This rung is code-verified against an exact analytic reference
(Taylor–Maccoll), not experiment-validated. C2's consistency clears `B_cons` = 0.60° by only
0.072°, and the **correlated-worst locator increment at the fine level, 1.2464°, exceeds the
±1.0° band** — disclosed in the freeze rather than discovered after it, and a reader who prefers
that uncertainty channel should read C2's accuracy margin as **not established**. I am not
resolving that channel here; I am refusing to hide it.

## 1. Rule 2 — the frozen grader IS the file that ran

The launch omitted the `grading_freeze` key from the queue entry, so the runner recorded the
grading path as `UNPINNED` and its mechanical launch-time cross-check was never made (frozen
prereg, ADDENDUM 2026-09-10). That check is therefore discharged by hand, here:

| pinned path | pinned blob (§10) | on disk | `HEAD:` | `34797ce9:` | agree |
|---|---|---|---|---|---|
| `verification/runs/navier_class/SUP_BOOSTER/grade_sup_booster_e2.py` | `d18f0867ea7d1fd6f86347c00ca1a5b8e3ddb663` | same | same | same | **yes** |
| `cases/navier_class/SUP_BOOSTER/gen_cone_mesh_e2.py` | `be6cc10481fb93ba541ca025ee44145b32b85ba1` | same | same | same | **yes** |
| `tm_reference_M2p0_tc15.json` (provenance, non-`.py`) | `c442a94bfd3166e443124e92248c5d96a929d8a5` | same | same | same | **yes** |

Shas are **git blob** shas (`git hash-object` / `git rev-parse <commit>:<path>`), which is what
§10 pins; no sha256 pin appears in this document, so none is compared. **The pinned grader is
the path that ran** — `autograde_sup_booster_e2.sh` invokes `$REPO/verification/runs/.../
grade_sup_booster_e2.py` directly, and **no copy of the grader exists anywhere else** (there is
no `cases/navier_class/SUP_BOOSTER/grade_sup_booster_e2.py`), so no unpinned copy could have
produced this grade. The grader's mtime (04:47Z) precedes the launch (04:54:46Z). The frozen
document itself has changed since `34797ce9` by exactly one **appended** dated addendum — `diff`
reports `390a391,435`, a pure append, so `lines whose number changed above this section: 0` is
true as asserted, and §10's pin cells are byte-unchanged.

## 2. Rule 4 — strict completion, all five clauses plus the age guard

Verified from the artifacts, not from `VERDICT.json`. **All three levels pass every clause.**

| clause | coarse | medium | fine |
|---|---|---|---|
| (a) `rc.solve` / `rc.wrapper` | 0 / 0 | 0 / 0 | 0 / 0 |
| (b) `End` line in `log.rhoCentralFoam` | 1 | 1 | 1 |
| (c) last `Time` == `endTime` (controlDict) | 15000 == 15000 | 15000 == 15000 | 15000 == 15000 |
| (d) fields at `endTime` | `p U T rho` + `rDeltaT` | same | same |
| (e) `ExecutionTime` count == round(`endTime`/`deltaT`) | 15000 == 15000 | 15000 == 15000 | 15000 == 15000 |
| age guard: oldest `endTime` field minus this case's own `0/T` | **+288.948 s** | **+584.492 s** | **+1179.760 s** |

- **(d) is this solver's field set, not the thermal family's.** `rhoCentralFoam` is compressible
  and inviscid here, so the registered set is `p U T rho` (frozen prereg §6); `k omega nut
  alphat p_rgh phi` do not exist in this case and are not expected. `rDeltaT` is additionally
  present because the run is LTS. `C Cx Cy Cz` also sit in each `15000/` directory: they are
  **grader-derived** (`postProcess -func writeCellCentres`, written 05:29:01–05:29:04Z, after
  the solves), not solution fields, and they are newer than `0/T` too, so they cannot weaken the
  age guard.
- **(e) is the FIXED-`deltaT` clause-5 path, not the adaptive one.** Every level's
  `system/controlDict` carries `deltaT 1;` with **`adjustTimeStep no;`** and
  `writeControl runTime; writeInterval 1000;`. The 15000 pseudo-iterations are LTS *local* time
  steps under a fixed outer step of 1, so `n_exec == round(endTime/deltaT) == endTime == 15000`
  is the right test and it holds exactly. The adaptive `n_exec == steps written` variant does not
  apply.
- The age-guard margins are the oldest field at `endTime` (`rho` in every case) against that
  level's own `0/T`; the margin equals that level's solver wall time, as it should.

**Disclosure on the instrument, not on the run.** The grader's own `check_completion` enforces
clauses (b), (c), (d) and the age guard, but **not** (a) `rc` and **not** (e) the `ExecutionTime`
count. Those two clauses were discharged by hand for this rung, above; both hold. The grader is
frozen and is not edited (rule 6) — this is recorded so a successor registration widens the
check rather than a reader assuming it was always complete.

## 3. Rule 3 — the planted-zero control is genuine

- **Real corpus, not a fixture.** `run_grade` calls `planted_zero_control(args.fine, 15000)`
  **before** any graded number is trusted, on the actual fine-grid `p` field on disk.
- **Same reader path.** The plant is written to a real perturbed copy of that field and read
  back through `read_cone_pressure` — the identical function that produces the graded Cp, with
  the identical cone-owner-cell selection, spatial `Cx` sort and trim; only the file path
  differs. The plant target is `cells[lo]`, chosen to sit **inside** the trimmed plateau, so a
  reader that trimmed it away would not see it.
- **It refuses, it does not warn.** `if not ctrl["passed"]: refuse(...)` → `sys.exit(2)`.
- **Measured:** planted 1000.0 Pa at cell 8116; base surface p 158544.892 Pa → seen
  158551.984 Pa; `reader_delta` **7.092198581551202** Pa against `expected_delta`
  **7.092198581560283** Pa (= 1000/141 cells in the plateau), agreeing to 11 significant
  figures.
- **The control has a proven negative arm.** `--selftest` runs the same control on a throwaway
  400-cell case with the reader deliberately blinded to the perturbed copy, and **requires**
  `passed: false` (measured `reader_delta` 0.0) — a neutered control is caught rather than
  certified. Selftest rc=0 and byte-identical output under **both** `python3` and `python3 -O`.
- **0 executable `assert` nodes** in the grader by `ast.parse` (not `grep`): `ast.Assert` count
  is **0**, so no refusal, guard, control or gate is compiled out under `-O`.

## 4. Gate C1 — cone-surface Cp: the triple CONVERGES but is PRE-ASYMPTOTIC

| level | nCells | h (1/√N) | cone-surface Cp | dev vs TM 0.2022475 |
|---|---|---|---|---|
| coarse | 6,000 | 0.0129099 | 0.20487297 | +1.30% |
| medium | 13,500 | 0.0086066 | 0.20305782 | +0.40% |
| fine | 30,375 | 0.0057378 | **0.20168444** | **−0.28%** |

Monotone (`e32/e21` = +1.32), so the triple is **CONVERGING**; refinement ratio r = 1.5 exactly
in both steps, asserted against the meshes actually graded. `|Cp_fine − 0.2022475| =
0.000563090 ≤ band 0.010` → **`PASS`**. GCI_fine (Celik, F_s = 1.25) = **0.026462 (2.65%)**;
Richardson extrapolation 0.1974149.

**On its face, not in a footnote: the apparent order is p = 0.6878.** `rhoCentralFoam` with
these schemes is nominally second-order, so **the triple is converging but PRE-ASYMPTOTIC** —
p ≈ 0.69 is first-order-ish, and on this grid family the solution has not reached the asymptotic
range. **Consequence, stated plainly: the 2.65% GCI is a WEAKER uncertainty statement than a
second-order GCI would be.** The Celik GCI divides the fine-grid relative difference by
(r^p − 1) = 0.3217 at p = 0.6878, where a second-order triple on this r = 1.5 family would
divide by (r^2 − 1) = 1.25 — so the same 0.681% level-to-level difference (e21/f1) inflates into a
**2.65% band instead of the 0.68% one** a second-order triple would have given, a factor 3.9
wider, and the extrapolated value 0.19741 sits **2.12% below** the fine value rather than a few
tenths of a percent.
A GCI computed off a pre-asymptotic order is a wider and less trustworthy interval, and it
should be read that way.

**And, equally plainly: no observed-order condition was registered, so this is a DISCLOSURE and
not a DISQUALIFIER.** Frozen prereg §3 registers C1 as *"PASS iff |Cp_fine − 0.202248| ≤ 0.010
and the triple is CONVERGING"* — and nothing else. It registers no admissible band on p beyond
the grader's structural (0.1, 6.0) window, inside which 0.688 sits. Adding a
"p must be near 2" condition at grade time would be substituting a gate after the answer is
known, which rule 2 forbids and which §3 forbids in terms. **The right remedy is a successor
registration that registers an observed-order condition before compute — not a re-grade of
this one.**

## 5. Gate C2 — shock angle β: NON-MONOTONE, which is exactly why the Roache instrument is forbidden here

| level | β (deg) | locator increment Δβ_loc, rms (deg) |
|---|---|---|
| coarse | 33.89439 | 1.30781 |
| medium | **34.19677** | 0.87423 |
| fine | **33.66881** | **0.58926** |

**β is NON-MONOTONE across the levels — medium is the extremum, not an endpoint.** Put through a
Roache triple these three values give a sign change in `e32/e21` and classify **`OSCILLATORY`**,
which under rule 5 would make C2 `NOT A RESULT` however close to the reference the fine value
sat. **That is precisely the outcome ruling `0e9c1bcb` (framing (ii)) exists to address**: a
shock's located radius is *quantised by the local cell size*, so it wiggles at the sub-cell level
across grids even when the locator is correct, and Richardson-extrapolating a quantised locator
is the wrong instrument. The ruling therefore gates C2 by **value-in-band plus a separate,
tighter, pre-registered consistency bound**, and **forbids the Roache instrument on it outright**
(condition 8).

- **ACCURACY.** `|33.66881 − 33.91470| = 0.24589 ≤ band 1.0°` → passes. Reported, always, with
  its increment: **33.6688 ± 0.5893 deg (locator increment)**.
- **CONSISTENCY.** `max|β_i − β_j| = 0.52797 ≤ B_cons 0.60°` → passes. This bound has teeth and
  came within **0.072°** of failing; the frozen §3.3 named exactly this risk before the run
  ("if coarse-grid quantisation dominates the E2 spread, C2 GATE FAILs on consistency").
- **PRECONDITION (condition 4), EVALUATED not merely reported.** The grader's
  `grade_gate_shock_angle` tests `if not (inc < band)` and, when it fails, **returns
  `NOT A RESULT` with its reason and never reaches the accuracy or consistency tests**. It is a
  refusal branch, not a boolean field — and the boolean `band_exceeds_locator_increment: true` is
  reported *in addition*. Measured: **0.589264 < 1.0**, a factor **1.697**. The frozen §3.2
  INFERRED ≈0.59° before the mesh had a solution; the measured value is 0.589264°, inside 0.2%
  of the prediction.
- **FORBIDDEN INSTRUMENT, verified in the output.** The C2 object in `VERDICT.json` carries none
  of `triple`, `apparent_order_p`, `gci_fine`, `richardson_extrap` — and no occurrence of
  `triple`/`apparent_order`/`gci`/`richardson` appears anywhere at or after the C2 object's byte
  offset (all four occurrences in the file sit at offsets 4763–4880, inside C1's object, which
  ends before C2 begins at 5015). The prohibition is executable twice over: `run_grade` calls
  `defect(...)` → exit 70 if any of the four keys reaches a C2 report, and `--selftest` asserts
  the same on all four C2 branches.
- **On its face: the adversarial CORRELATED-WORST locator increment at fine is 1.2464°, and it
  EXCEEDS the ±1.0° accuracy band.** It was **disclosed in the freeze, not discovered after it**
  — frozen §3.2 states the E2 figure as ≈1.24° and says in terms that it "does **not** clear the
  band". It is a conspiracy of one-cell displacements in the single sign pattern across all six
  stations that maximises the fitted slope change, not the instrument's resolution; the
  **registered** increment is the rms one (independent quantisation propagated in quadrature),
  and the measured rung-to-rung spread 0.5280° sits below even that. The single-station figure is
  0.4041°. All three are printed by the grader whatever the verdict. **A reader who prefers the
  correlated-worst channel should read C2's accuracy margin as not established** — that is the
  honest boundary of this gate, and it was drawn before the run.

## 6. Cost — rule 12

**34.23 core-min MEASURED** (serial, ranks = 1; per-level solver wall 290 + 584 + 1180 = 2054 s)
against **31.0 core-min registered** and a **60 core-min cap** → **ratio 1.104**, cap utilisation
0.571. Derived cost **$0.0293** at $0.0513/core-h — **derived, not measured**, the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Waste 0.000 core-min**, named separately: every
level returned rc 0, met strict completion, and produced a gate reading. No stall (longest wall
1180 s); no per-level timeout (800/1200/1600 s) fired.

**The +3.38 core-min gap splits into two measured channels that close it exactly, and it is 80%
the registered mesh change, not contention.** At identical cell counts, identical `endTime` and
identical 15000 iterations, total `ExecutionTime` rose from 1829.93 s (E1) to 1992.55 s (E2):
**+2.710 core-min = 80.1%**, i.e. `GR_RADIAL` 12 → 5 costs **+8.9% CPU per iteration** (per level
1.193 / 1.166 / 1.066 — the increase shrinks as the mesh refines, a near-wall-distribution
signature). The wall-minus-CPU channel accounts for the other **+0.673 core-min = 19.9%**
(`ExecutionTime/ClockTime` 0.9212 / 0.9711 / 0.9832 for E2 against 0.9857 / 0.9847 / 0.9919 for
E1). Rounding is real but minor (≤0.40 core-min, ≤11.8%): the registered 31.0 rounds E1's 30.85
up, and `COST.txt`'s integer `core_min=34` truncates 34.25 down. Full row, with the concurrency
window characterised from dated artifacts inside 04:54:46Z–05:29:04Z, in the calibration draft
`verification/runs/navier_class/SUP_BOOSTER/graded_e2/CALIBRATION_ROW.e2.CORRECTION.pending.md`.

**LEDGER DEFECT, DISCLOSED HERE BECAUSE IT IS ALREADY COMMITTED.** The row landed for this rung at
commit `4749ae1d` (`C-20260910T052907.204386Z-e9df493d`) records actual **0.00 core-min**, cleaned
0.00, ratio **0.00x**, and "waste 0.00 core-min (every level returned rc=0)". Those are **false
zeros**: `cases/navier_class/watch_grade_calibrate.py::read_kv` parses one `key=value` pair per
line, this launcher writes four pairs on one line, so no `wall_s` or `rc_solve` key was ever
parsed and `.get(key, "0")` defaulted the cost to zero and the rc to `"absent"`. **No gate verdict
is affected** — the grader reads solution fields, never these sidecars. The correction is a new
row naming the row it corrects (ledger append rule 1); the existing row is not edited.

## 7. What is not verified

- The mechanism behind the +8.9% CPU per iteration is **inferred**, not profiled: no profiler was
  run and no hardware counter read.
- The concurrent-solver count in E2's window (**≥4 on `nproc`=16**) is a **lower bound** from an
  mtime sweep; a solver that wrote nothing in the window is invisible to it, a retrospective load
  average cannot be measured, and fleet agents are invisible to `pgrep` after the fact (L-41). The
  contention/IO-versus-memory-bandwidth split inside the 0.673 core-min is **not separable** from
  these artifacts.
- Whether p ≈ 0.69 would rise toward 2 on a finer family is **untested** — it needs a fourth level,
  which is not registered here.

*Artifacts:* graded record
`verification/runs/navier_class/SUP_BOOSTER/graded_e2/VERDICT.json` (+ `verdict_stdout.txt`,
`rc.autograde` 0, `COST.txt`, `LAUNCHER_DONE`); per-level
`.../graded_e2/{coarse,medium,fine}/{rc.solve,rc.wrapper,wall_s,STATUS,log.rhoCentralFoam,
system/controlDict,0/,15000/}`; frozen prereg
`verification/campaign/SUP_BOOSTER_E2_PREREGISTRATION.md` (freeze `34797ce9`, ADDENDUM
2026-09-10); governing ruling
`verification/campaign/SUP_BOOSTER_E2_C2_SHOCK_ANGLE_GATING_RULING_2026-09-09.md` (`0e9c1bcb`);
pinned grader blob `d18f0867`, pinned generator blob `be6cc104`, frozen reference blob
`c442a94b`; predecessor `verification/campaign/SUP_BOOSTER_E1_VERDICT.md` and its graded runs
`.../SUP_BOOSTER/graded/`; calibration draft
`.../graded_e2/CALIBRATION_ROW.e2.CORRECTION.pending.md`.
