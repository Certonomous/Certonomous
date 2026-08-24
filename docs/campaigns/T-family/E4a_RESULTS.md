# E4a. fanPressure boundary-condition verification — results

**Written 2026-08-24T16:12:06Z** (the stamp is `date -u` output read in the same shell
invocation that wrote this file). Pre-registration
`docs/campaigns/T-family/E4a_PREREGISTRATION.md`, **FROZEN BY COMMIT
`628e29c4`** (2026-08-24 15:58:53 +0000) before any case directory existed.

---

## 1. Rung verdict

**NOT A RESULT.**

Three registered rows PASS (**I1**, **I2**, **P1** — the BC-identity half of
the rung). Five rows are **NOT A RESULT** (**R1**, **G1**, **G2**, **N1**,
**D1**): **no case met the registered iterative-convergence gate**, and rule 5
order (1) makes every row that needs a converged level NOT A RESULT whatever
its value. The comparator exited **1** (`EXIT_FAIL`, `analyse_e4a.py:67`) —
**not 2**; it did not refuse, and the planted-zero control **Z1** held on all
three readers in all five cases.

What the rung therefore establishes and does not establish: `fanPressure`
**does impose its own registered equation** on the fields as written (I1, three
decades inside its registered floor and about six decades below the
convention-error signature it exists to catch), mass is conserved across the
patch (I2), and no fan-patch face carries outflow (P1). It establishes
**nothing** about the operating point's agreement with the exact Poiseuille
intersection, about the observed order of the ladder, or about the §1.5 error
model — those are the five voided rows.

The voiding cause is **not a crash and not a solver failure**: every case
returned rc=0 with an `End` line, reached `endTime` 20000, and passed the
strict completion rule 5/5. The registered convergence gate demands that every
parsed value of `p`, `U` and `phi` (internal and boundary) be **bit-identical**
between checkpoints 15000 and 20000 (`analyse_e4a.py:395-417`, no tolerance,
`writePrecision 12`); the fields still move in their **last written digit**
after 20000 iterations, so the gate does not close. **Triage of that gate is
the supervisor's, not this lane's; no gate, threshold, cap or label has been
touched — after first compute they are closed (rule 2).**

---

## 2. Registered rows — every row, as the comparator graded it

Comparator `verification/runs/T-family/E4_runs/analyse_e4a.py`, sha256
`a9f31c3f569181f27b17bcaca318ce1f1a0a3f0e85e788a4214c8d8d5d63ff4b`, verified
identical to the `FREEZE_CHECK.txt` table **and** to the blob committed at
`628e29c4`. Full output:
`verification/runs/T-family/E4_runs/log.analyse_e4a.20260824T160518Z.txt`.

| row | verdict | measured value | registered interval | falsifier fired? |
| --- | --- | --- | --- | --- |
| **I1** | **PASS** | max fan-patch face residual **3.794e-11 m²/s²** (worst case F_f) | `<= 8.1e-8 m²/s²` | **no.** The convention-error signature 0.5·U_m² ~ 1.125e-4 that this row exists to catch is **~6.5 decades above** the measured residual |
| **I2** | **PASS** | max abs(Q_in − Q_out)/abs(Q_in) **7.082e-10** (worst case S_f) | `<= 1e-4` | **no** |
| **P1** | **PASS** | **0** fan-patch faces with phi >= 0 in any case | `= 0` | **no** |
| **R1** | **NOT A RESULT** | triple on Q* = (**1.5205486849494e-07**, **1.5078820910875e-07**, **1.5021570613088e-07**) for F_c/F_m/F_f; comparator order **None** | `p in [1.6, 2.4]` | **n/a — not reached.** A level is not iteratively converged, so rule 5 order (1) applies before the interval. **No order and no GCI are quoted here**, per the pre-registration and rule 5 |
| **G1** | **NOT A RESULT** | F_f not converged (checkpoints 15000 and 20000 differ) | `[1.498350e-7, 1.504650e-7]` | **n/a — not reached** |
| **G2** | **NOT A RESULT** | S_f not converged (checkpoints 15000 and 20000 differ) | `[0.999800e-7, 1.004000e-7]` | **n/a — not reached** |
| **N1** | **NOT A RESULT** | N_f not converged (checkpoints 15000 and 20000 differ) | `[1.498200e-7, 1.507500e-7]` | **n/a — not reached** |
| **D1** | **NOT A RESULT** | triple not CONVERGING | dev `[-0.35, -0.08] %` | **n/a — not reached.** No corrected-Richardson figure is quoted |
| **Z1** | **PASS (control)** | planted-zero exact-float rule held for the `p`, `U` and `phi` readers in **every** case | exact-float, no tolerance | **no.** A failure would have been a **refusal (exit 2)**; the comparator exited 1 |

**Triple state:** the comparator did **not** classify the triple, because it
refuses to form an order over an unconverged level (`order None` printed). The
three values are monotone decreasing, which is an observation about the printed
numbers and **is not a triple state**; **p and GCI are not quoted and cannot be
recovered from this record.**

---

## 3. Per-case readings (all NOT A RESULT — carried for the supervisor's triage only)

These are the Q values the comparator printed beside `converged=False`. **They
carry no verdict, and rule 5 forbids converting them into one** — the gate can
turn a PASS into NOT A RESULT, never the reverse. They are recorded because
suppressing a computed number is worse than labelling it.

| case | curve | Ny | cells | Q measured (m³/s) | Q exact (m³/s) | dev | comparator verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| F_c | A | 8 | 800 | 1.520548685e-07 | 1.5e-07 | **+1.3699 %** | NOT A RESULT |
| F_m | A | 12 | 1 800 | 1.507882091e-07 | 1.5e-07 | **+0.5255 %** | NOT A RESULT |
| F_f | A | 18 | 4 050 | 1.502157061e-07 | 1.5e-07 | **+0.1438 %** | NOT A RESULT |
| S_f | B | 18 | 4 050 | 1.002387044e-07 | 1.0e-07 | **+0.2387 %** | NOT A RESULT |
| N_f | NULL | 18 | 4 050 | 1.504314707e-07 | 1.5e-07 | **+0.2876 %** | NOT A RESULT |

Source: `log.analyse_e4a.20260824T160518Z.txt`, the per-case block under Z1.

---

## 4. Pre-registration §1.5 predictions versus the measured deviations

§1.5 registered, before any case existed, a wall-discretisation term and an
entrance term. The comparison below is **diagnostic**: it grades nothing, and
none of these rows becomes a verdict.

| case | §1.5 wall term | §1.5 entrance term (central) | §1.5 net central | measured dev | measured − predicted |
| --- | ---: | ---: | ---: | ---: | ---: |
| F_c (Ny 8) | +1.5625 % | -0.197 % | +1.366 % | +1.3699 % | **+0.004 pp** |
| F_m (Ny 12) | +0.6944 % | -0.197 % | +0.497 % | +0.5255 % | **+0.028 pp** |
| F_f (Ny 18) | +0.3086 % | -0.197 % | **+0.111 %** | +0.1438 % | **+0.033 pp** |
| S_f (Ny 18) | +0.3704 % | -0.158 % | **+0.213 %** | +0.2387 % | **+0.026 pp** |
| N_f (Ny 18) | +0.6173 % | -0.394 % | **+0.223 %** | +0.2876 % | **+0.065 pp** |

The F_c/F_m entrance terms are §1.5's level-independent central value applied
at the coarse and medium levels; §1.5 registers the entrance term as
level-independent to leading order.

**This is recorded, and it is not a verdict.** The rung's own gate voided every
row these numbers would have fed. Whether the agreement above is evidence of
anything is a question for the supervisor, and **it cannot be settled inside
this rung** — the pre-registration's gate has already spoken.

---

## 5. Convergence diagnostic — why the gate did not close

Every case is deeply converged **in residual terms** and still fails the
registered **digit-exact** gate. Final iteration residuals at time 20000
(`<case>/log.solve`, last `Solving for` lines):

| case | Ux initial residual | Uy initial residual | p initial residual |
| --- | ---: | ---: | ---: |
| F_c | 2.830e-11 | 1.555e-08 | 4.637e-10 |
| F_m | 1.257e-11 | 2.163e-08 | 4.034e-10 |
| F_f | 3.531e-12 | 1.746e-09 | 3.699e-10 |
| S_f | 2.837e-12 | 2.488e-09 | 2.567e-10 |
| N_f | 6.171e-14 | 1.974e-09 | 1.003e-10 |

Maximum **absolute** value-for-value change between checkpoints 15000 and
20000, measured by aligned text comparison of the written field files (no new
physics reader; the two checkpoints have identical file structure, so
non-numeric lines align to themselves at zero difference):

| case | max abs(dp) (m²/s²) | max abs(dphi) (m³/s) |
| --- | ---: | ---: |
| F_c | 3.200e-12 | 3.288e-17 |
| F_m | 1.600e-12 | 2.800e-18 |
| F_f | 2.600e-12 | 5.123e-18 |
| S_f | 6.000e-13 | 1.348e-18 |
| N_f | 1.000e-13 | 6.663e-19 |

Artifacts: `verification/runs/T-family/E4_runs/<case>/15000/{p,phi}` and
`verification/runs/T-family/E4_runs/<case>/20000/{p,phi}`, present on disk.
**No relative figure is quoted**: the text method cannot cleanly separate field
values from structural integers in the denominator, and a ratio it cannot
defend is not reported.

**Observation, offered to the supervisor and decided by no one here:** with p
of order 5.4e-2 m²/s², a drift of ~1e-12 absolute sits at about the **twelfth
significant digit** — i.e. at `writePrecision 12`, the precision the
pre-registration chose so that "the equality bites at ~1e-12 relative" (§2).
Whether that means the registered gate is measuring solver drift or
write-precision flicker is **a gate question, and gates are closed after first
compute (rule 2)**. Nothing here proposes changing it.

---

## 6. Execution record

Build: `log.build.20260824T160001Z.txt` — `build_e4a.py` rc=0, five case
dictionaries, `verify()` one-change-per-case passed; zero numeric time
directories and zero markers immediately after build.

Launch: serial, one case at a time, via `launch_e4a.sh` (guards **G1** atomic
lock, **G2** /proc cwd scan, **G3** no stray numeric time dir — all passed for
all five cases; per-case `LAUNCH_LOCK/launch.log`), `nice 15`, one core,
detached with setsid/nohup. Three T1b L4 buoyantBoussinesqSimpleFoam solvers
were live in `../T1_runs` throughout and were not touched.

| case | rc | solver wall (s) | blockMesh rc | checkMesh rc | maxRSS (kB) | end (UTC) |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| F_c | 0 | 13 | 0 | 0 | 59 108 | 2026-08-24T16:00:37Z |
| F_m | 0 | 23 | 0 | 0 | 59 756 | 2026-08-24T16:01:30Z |
| F_f | 0 | 45 | 0 | 0 | 61 444 | 2026-08-24T16:02:36Z |
| S_f | 0 | 45 | 0 | 0 | 61 408 | 2026-08-24T16:03:41Z |
| N_f | 0 | 43 | 0 | 0 | 61 484 | 2026-08-24T16:04:46Z |

Source: `verification/runs/T-family/E4_runs/STATUS.<case>`, five files, all
present.

Completion: `log.mark_done.20260824T160511Z.txt` — `mark_done_e4a.py` rc=0,
**5/5 cases meet the strict completion rule** (rc=0; `End` line; last time ==
`endTime` 20000; `p U phi` present at endTime; `ExecutionTime` count == 20000;
every endTime field newer than the case's own `0/U`). Markers `DONE.F_c`,
`DONE.F_f`, `DONE.F_m`, `DONE.N_f`, `DONE.S_f`.

**No run was stopped, killed, relaunched or discarded.** No case approached its
10x per-case stop threshold (F_c 1 300 s, F_m 2 800 s, F_f/S_f/N_f 6 200 s
each) and no wall exceeded 3 600 s, so the rule-12 stall rule matches nothing.

---

## 7. Cost — registered versus actual (rule 12, Sanaa's 2026-08-23 law)

Rate **$0.0513/core-h**, c7a.4xlarge, **owner-stated / reported-by-owner** —
the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so
**every dollar figure below is derived, not measured**. Serial, nProcs 1, so
core-s equals wall s.

| case | cells | predicted core-s (prereg §4) | actual solver wall (core-s) | actual wrapper gross (core-s) | ExecutionTime (s) | s per cell-iteration | ratio gross/predicted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| F_c | 800 | 130 | 13 | 13 | 12.68 | 7.925e-07 | **0.100x** |
| F_m | 1 800 | 280 | 23 | 24 | 23.77 | 6.603e-07 | **0.086x** |
| F_f | 4 050 | 620 | 45 | 45 | 44.56 | 5.501e-07 | **0.073x** |
| S_f | 4 050 | 620 | 45 | 45 | 44.49 | 5.493e-07 | **0.073x** |
| N_f | 4 050 | 620 | 43 | 44 | 43.43 | 5.362e-07 | **0.071x** |
| blockMesh + checkMesh x5 | — | 15 | — | *(inside the wrapper-gross column: 2 core-s total)* | — | — | — |
| **total** | | **2 285** | **169** | **171** | **168.93** | | **0.0748x** |

The wrapper-gross column is wrapper start to wrapper end from each case's
`LAUNCH_LOCK/launch.log`, and therefore **includes** blockMesh and checkMesh;
the solver-wall column is `STATUS.<case>` `wall=`, solver only. The difference,
**2 core-s across all five cases**, is the whole meshing cost against a
registered 15.

**Totals.** Predicted **2 285 core-s = 38.083 core-min = 0.6347 core-h =
$0.0326 derived**. Actual gross **171 core-s = 2.850 core-min = 0.0475 core-h =
$0.00244 derived**. **Actual cleaned = actual gross**: the longest wall on the
box is 45 s, nearly two decades below the 3 600-s stall rule, so there is
nothing to clean out.

**Ratio: 0.0748x gross = cleaned / predicted.** No overrun. The rung consumed
**0.75 %** of its registered 10x stop-and-investigate threshold (6.35 core-h);
the per-case 10x thresholds were never approached.

**Waste: none.** No run was stopped, relaunched or discarded; no case tree was
rebuilt; the comparator ran once. There is no waste figure to name separately,
and none is folded into the ratio.

**Gap attribution — misprediction, in the conservative direction, from a
solver-class mismatch in the cost basis.** Prereg §4 took **7.5e-6 s per
cell-iteration** from the T1c-class buoyantBoussinesqSimpleFoam replicates
(`T1_runs/STATUS.L_Ts_P_*`) and called it "conservative for a momentum-only
solver". It was conservative by **13.6x**: this rung's simpleFoam laminar solve
measures **5.50e-7 s per cell-iteration** at F_f (44.56 s / (4 050 x 20 000)).
The cited basis solves a coupled buoyant energy equation plus alphat/k/omega
transport; this rung solves momentum and pressure only, laminar, on a 2D
channel. **The calibration lesson is that a per-cell-iteration basis is not
portable across solver classes** — a momentum-only laminar estimate borrowed
from a buoyant turbulent basis over-predicts by an order of magnitude, and the
honest fix is a basis measured on the solver that will actually run. Meshing
was over-predicted on the same pattern: 15 core-s registered against 2 core-s
measured across five cases.

**Contention is not the explanation and pushed the other way.** Three peer
buoyantBoussinesqSimpleFoam solvers were live on the 16-core box throughout
(load average 3.63 at launch) and this lane ran at `nice 15` on one core.
Contention can only inflate the actual, so it cannot account for a 0.075x
ratio; the figure is stated gross rather than netted off.

**Ready row for `docs/COST_CALIBRATION.md`** (id re-derived from the table tail
at commit time per rule 11 — the tail read while writing this file was
**C-14**; the id below is a placeholder and must not be copied blind):

| id | date | team | process | predicted | actual gross | actual cleaned | ratio | attribution | record ref |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C-(re-derive at commit) | 2026-08-24 | heat-transfer | E4a (fanPressure BC verification, exact operating-point class; five cases built, launched, completed 5/5 and graded — **rung verdict NOT A RESULT**: I1/I2/P1 PASS, R1/G1/G2/N1/D1 voided by the registered iterative-convergence gate) | **2 285 core-s = 38.083 core-min = 0.6347 core-h = $0.0326 derived**, registered at `E4a_PREREGISTRATION.md` §4, frozen `628e29c4` (10x stop threshold 6.35 core-h) | **171 core-s = 2.850 core-min = 0.0475 core-h = $0.00244 derived** — wrapper start-to-end from the five `E4_runs/<case>/LAUNCH_LOCK/launch.log` files (13 + 24 + 45 + 45 + 44), which **includes** blockMesh + checkMesh (2 core-s of the 171); solver-only from `E4_runs/STATUS.<case>` `wall=` is 169 core-s, and ExecutionTime from the five `log.solve` files sums to 168.93 s. Serial, nProcs 1, so core-s equals wall s | **= gross.** Longest wall on the box is 45 s, nearly two decades below the 3 600-s stall rule, so the stall rule matches nothing and there is nothing to clean out | **0.0748x** gross = cleaned / predicted; **0.0075x** of the 10x stop threshold. **No overrun; no run stopped** | **Misprediction, conservative direction, from a solver-class mismatch in the cost basis.** §4 took 7.5e-6 s/cell-iteration from buoyantBoussinesqSimpleFoam T1c replicates and called it conservative for a momentum-only solver; measured here at **5.50e-7 s/cell-iteration** (F_f: 44.56 s / (4 050 x 20 000)), i.e. conservative by **13.6x**. The basis solves a coupled energy equation plus alphat/k/omega; this rung solves momentum + pressure only, laminar, 2D. **Calibration lesson: a per-cell-iteration basis is not portable across solver classes — measure it on the solver that will run.** Meshing was also over-predicted: 15 core-s registered against **2 core-s** measured across five cases. **Contention is not the explanation and pushed the other way**: three peer buoyantBoussinesqSimpleFoam solvers were live on the 16-core box throughout (load1 3.63 at launch) with this lane at `nice 15` on one core — contention can only inflate the actual, so it cannot produce a 0.075x ratio, and the figure is stated gross rather than netted off. **WASTE: none** — no run stopped, relaunched or discarded; the comparator ran once | `docs/campaigns/T-family/E4a_RESULTS.md` §7 (this table) and §1 (verdict); prereg frozen at `628e29c4`; per-case markers `verification/runs/T-family/E4_runs/STATUS.*` (5 files, all rc=0) and `DONE.*` (5 files); logs `verification/runs/T-family/E4_runs/log.build.20260824T160001Z.txt`, `.../log.mark_done.20260824T160511Z.txt`, `.../log.analyse_e4a.20260824T160518Z.txt` |

---

## 8. Instrument provenance

All seven instruments hash **identical** in three places — the
`FREEZE_CHECK.txt` table, the working tree at run time, and the blob committed
at `628e29c4` — verified before the build and re-verified immediately before
the comparator ran (recorded at the head of
`log.analyse_e4a.20260824T160518Z.txt`):

| file | sha256 |
| --- | --- |
| `E4_runs/E4a_registered.json` | `bb363d0232683f50a8f75ecbd15aef436bd72762686764c56027aac6f0401b05` |
| `E4_runs/build_e4a.py` | `451eae3682bff7f89f31147c1d2d74fe1badc4c2af2c0e0f40e76ca665e46956` |
| `E4_runs/analyse_e4a.py` | `a9f31c3f569181f27b17bcaca318ce1f1a0a3f0e85e788a4214c8d8d5d63ff4b` |
| `E4_runs/mark_done_e4a.py` | `b152ed0071bfe8cea060fc8164587ffeec7ca02ab0c6ce259565935d4b10fbe6` |
| `E4_runs/run_one_e4a.sh` | `226fd26b019a7fe73b559dda36451ca328ee371bcb1c8fb6b776d024f12ffe19` |
| `E4_runs/launch_e4a.sh` | `0e2b893fd134cba67975792d3defefb453ed929ca4d122f22022e4cad9c81274` |
| `T1_runs/analyse_t1c.py` (imported frozen) | `60893b28e284127f61b41842c520897a2202cb024d5a4d260272c6ee7e6c5135` |

`E4a_PREREGISTRATION.md` and `FREEZE_CHECK.txt` also hash identical on disk and
at `628e29c4`
(`2ebe2fc89ed7467730310d51630df837fb0f3dd578a05ef702c9b05d32150765` and
`3adf081526abe137627f8a01d23dbbca33a10a464fd9616fddff86db7f6cd329`).

**No frozen file was edited and no existing file was modified by this lane.**
The only files written are the five case directories built by `build_e4a.py`,
their run outputs, the three stamped logs named above, the `STATUS.*` /
`DONE.*` markers, `BUILD_MANIFEST.txt`, and this results file.

---

## 9. What must be verified personally before this is committed

Reserved to the supervisor (`SUPERVISION_CHARTER.md` §3; not delegable):

1. **The convergence-gate finding is the rung's whole outcome and needs a
   personal read.** Five registered rows are void because a digit-exact
   equality gate did not close on fields whose residuals are at 1e-10 to
   1e-14. This lane has deliberately **not** classified that as solver
   non-convergence, as a gate defect, or as anything else — it reports the
   measurement and stops. Any re-run at a longer `endTime`, any addendum, and
   any statement about what the gate was measuring is the supervisor's call and
   must respect rule 2 (gates closed after first compute; originals struck,
   never rewritten).
2. **§4's diagnostic agreement is a big claim and is not this lane's to make.**
   The measured deviations sit within about 0.07 pp of §1.5's registered
   central predictions on all five cases. That is recorded as arithmetic and
   **carries no verdict**; converting it into one would invert rule 5, which
   permits the gate to turn a PASS into NOT A RESULT and never the reverse.
3. **The cost row's id must be re-derived from the ledger tail in the same
   shell invocation as the commit** (rule 11); the `C-14` tail read here is
   already stale by construction under the private-index protocol.
4. **This lane committed nothing and touched no git state.**
