# T10a-R2 results — the 2LI c/m/f ladder on T10a's B1 ceiling, graded 2026-08-26

**Summary as the frozen comparator printed it: 2 PASS, 5 GATE FAIL, 2 NOT A RESULT against this arm's own registered rows.** The identity row holds exactly (RR1: `qr(R2_f) ≡ qr(R_q)` to 0.0 W/m² over 7 056 faces, F sha identical `801700cf…`), the headline dev reproduces (RR3), and **the B1 2LI c/m/f triple is OSCILLATORY** — so the order row (RR2) and the dev/band row (RR5) are `NOT A RESULT`, and the four level-ratio / move rows fall outside both registered branches H1 and H2: the 2LI move is **+7.44 / +3.24 / +1.50 W/m²** at c/m/f, scaling faster than the level error, not mesh-independent (H1) and not proportional to it (H2). The registered expectation "the 2LI ladder is CONVERGING at p ≈ 1.48" is refuted by measurement.

Pre-registration `docs/campaigns/T-family/T10aR2_PREREGISTRATION.md` (v1.0 frozen; AMENDMENT 1 at `9fa66065` re-froze the launcher guard only, pre-first-compute). Run tree `verification/runs/T-family/T10aR2_runs/`. Launched by the queue runner from `T10aR2_R2_{c,m,f}_v2.json` (17:46:00Z / 17:47:05Z / 17:50:20Z). Graded by a lab lane on the heat-transfer supervisor's order `[lab-attributed]`; no verdict is the lane's.

## 1. Frozen instruments, hashed before they were believed

| instrument | §9 blob | `git hash-object` on disk at grading | match |
|---|---|---|---|
| `T10aR2_runs/mark_done_t10aR2.py` | `4fbff6a7` | `4fbff6a7de2cf1bdfcea8a75ad2d5f9018241d35` | SAME |
| `T10aR2_runs/analyse_t10aR2.py` | `a252463b` | `a252463b015f81f0c45cd9ddc6079c1f4d476d17` | SAME |

The comparator's own provenance block printed `analyse_t10aR2.py` sha256 `efe25789f09f77a9…` blob `a252463b…` (§9's row) and the frozen imports `analyse_t10aR.py` `bf13efee`, `analyse_t10a.py` `3c70263b`, `exact_t10a.py` `63c2cdef`, `analyse_t1c.py` `3d566802`, `roache_triple.py` `78e56a3b`, `T10aR2_registered.json` `d52c2ac6`. `analyse_t10aR2.py --selftest`: **17/17**, rc 0 (retained as `T10aR2_runs/log.analyse_t10aR2.selftest.20260826T205552Z.txt`).

## 2. Completion — the strict rule, three of three, and the 1-second level stated as a finding

`mark_done_t10aR2.py R2_c`, `R2_m`, `R2_f`: each `DONE`, rc 0; markers read `strict rule met (physics-critical clauses 1-6)`. Disclosed: the lane's first invocation was `mark_done_t10aR2.py --help`; the frozen script has no `--help` and treats an unrecognised flag as "no case named", so it evaluated all three levels and wrote the three markers at 20:52:23Z. The per-level re-runs confirmed each; nothing was retracted or edited.

| level | cells | wall s (STATUS) | ExecutionTime s | `Time =` lines / last | End | fields at 20 newer than `0/T` | core-min |
|---|---:|---:|---:|---|---|---|---:|
| R2_c | 2 048 | **1** | 1.62 | 20 / 20 == endTime 20 | yes | 5,10,15,20 at 17:46:01 > 0/T 17:46:00 | 0.017 |
| R2_m | 8 788 | 12 | 12.6 | 20 / 20 | yes | yes (ended 17:47:17Z) | 0.200 |
| R2_f | 37 044 | 531 | 529.51 | 20 / 20 | yes | 20/T, 20/qr 17:59:10 > 0/T 17:50:20 | 8.850 |

**R2_c's 1 s wall is genuine, not smoothed over:** 2 048 cells × 20 registered iterations (`endTime 20`, fixed-T walls, the parent's `B_c` measured `ExecutionTime` 1.63 s and that figure is §4's POINT basis); the wrapper's integer-second wall rounds a 1.62 s solve to 1. Every clause holds on inspection — `rc=0`, `End`, last time 20 == `endTime`, four written checkpoints, `qr` present, age guard by one second. It is a complete solve of a registered 20-iteration case, and it is a case whose cost is dominated by start-up and reading an 18 MB `F` (§4 said so in advance).

Source: `T10aR2_runs/STATUS.R2_{c,m,f}`, `DONE.R2_{c,m,f}`, `R2_*/log.solve`, `R2_*/{0,20}/`.

## 3. Controls

- Constants and closed forms: σ_OF reproduced two ways (rel 0 / 1.07e-11); T10a-1 spheres, T10a-2 black box (Howell vs Stokes contour, max reciprocity defect 0.0), Hottel 2-D — every registered decimal AGREE; reference-side plants C1 +104.17 %, C2 −35.53 %, outer black +22.50 %, swapped −23.44 %, cube matrix departures −2.30 / −40.89 / −40.95 / −25.59 % — all fire.
- **Planted zero on every case** (B_c, B_m, B_f, R_q, R2_c, R2_m, R2_f): +1.234e-03 W/m² recovered as `0.0012340000002950546` = `fl(old + plant) − old`, seen.
- Iterative convergence: CONVERGED on every case (max change 0.0 between the last two checkpoints, as fixed-T walls require).
- F-side: lean reader vs frozen reader bit-identical on R2_c/m/f (n = 1 024 / 2 704 / 7 056); radiosity and reciprocity 0.0; row-sum max defect 0.018976 / 0.038700 / 0.029235; closure_F 2.026e-03 / 1.339e-03 / 8.939e-04; python-vs-solver ≤ 1.2e-14 — ok, not VOID.
- **RR1 identity precondition:** sha256(F) R2_f == R_q `801700cf89dbd7b5…`, IDENTICAL; max |qr(R2_f) − qr(R_q)| = 0.000000e+00 W/m² over 7 056 faces at t = 20.

## 4. The graded rows — verbatim values, verdicts from the fixed vocabulary

B1 ceiling, 2LI c/m/f: **−3268.222601 → −3268.384010 → −3268.097795 W/m²**, exact −3265.532221, errors **−2.6904 / −2.8518 / −2.5656**, triple state **OSCILLATORY**; dev_f 0.07857 %; no band armed, no Richardson quoted.

| row | measured | registered point | interval (PASS) | verdict | note |
|---|---:|---:|---|---|---|
| RR1 | 0 | 0 | [0, 0] | **PASS** | identity, precondition met |
| RR2 | — (p n/a) | 1.48 | [1.0, 2.0] | **NOT A RESULT** | triple is OSCILLATORY |
| RR3 | 0.0785653 % | 0.07857 | [0.078, 0.0792] | **PASS** | the R_q headline, restated (triple OSCILLATORY) |
| RR4a | 0.943401 | 1.883 | [1.70, 2.10] | **GATE FAIL** | H2 would give 1.664; measured below both |
| RR4b | 1.11156 | 1.786 | [1.70, 2.10] | **GATE FAIL** | H2 1.495; below both |
| RR5 | — | 1.024 | [0.85, 1.30] | **NOT A RESULT** | no band armed (triple OSCILLATORY) |
| RR6a | 7.44159 W/m² | 1.504 | [1.0, 2.0] | **GATE FAIL** | H2 3.75; move at c is 4.9× H1 |
| RR6b | 3.23559 W/m² | 1.504 | [1.0, 2.0] | **GATE FAIL** | H2 2.25 |
| RR7 | 1.54063 | 1.0 | [0.7, 1.3] | **GATE FAIL** | the raw row-sum defect DOES move with the mesh under 2LI |

Reported, never graded (2LI ladder): B0 [6482.2306, 6483.2667, 6483.8976] CONVERGING, dev_f 0.01578 %, band 0.01893 %; B2 [−1264.8114, −1260.9135, −1258.5810] CONVERGING, dev_f 0.30999 %, band 0.34513 %; B3 [−1975.5203, −1971.3510, −1968.8206] CONVERGING, dev_f 0.20988 %, band 0.24807 %.

Source: `T10aR2_runs/gate_t10aR2.json` (written by the comparator 20:55:03Z), `T10aR2_runs/log.analyse_t10aR2.20260826T205552Z.txt` (full stdout, 148 lines).

## 5. Predictions scored (§5, all H1)

P-RR1 **HIT**; P-RR3 **HIT**; P-RR2 untestable (OSCILLATORY → NOT A RESULT); P-RR5 untestable; P-RR4a, P-RR4b, P-RR6a, P-RR6b, P-RR7 **MISS** — and the H2 alternative misses them too. What the measurement says: under 2LI the c-level error (−2.69) is already almost the f-level error (−2.57) — the ladder no longer shrinks with h, the residual ≈ −2.6 W/m² is common to all three levels and is not a discretisation error of the 2LI ladder. That is a finding for the supervisor to place; this record does not name its cause.

## 6. Cost — rule 12

- **Predicted (§4): POINT 11.32 core-min** (0.03 / 0.22 / 11.07), CEILING 44.63, cap 160; $0.0097 derived.
- **Measured: 9.067 core-min** = (1 + 12 + 531) wall s × 1 rank ÷ 60 from `STATUS.R2_{c,m,f}` (`core_min` 0.017 + 0.200 + 8.850); gross = cleaned (longest row 531 s). Per level: R2_c 0.56 (integer-second quantised, ±1 s), R2_m 0.91, R2_f 0.80.
- **Ratio 0.801** (0.203 of CEILING; 0.057 of cap). **Attribution: the POINT priced R2_f from R_q's contended CPU time (664 s); this solve ran essentially uncontended — ExecutionTime 529.5 s vs ClockTime 530 s (99.9 %)** — a conservative misprediction of the contention margin, not of the work. Contention: none limiting. **WASTE 0.000 core-min**, named separately: the three AMENDMENT-1 refusals of 17:24–17:26Z ran no solver. Generation 3.43 core-min was spent before the freeze (§1.1) and is named beside, not inside, the ratio.
- **$0.00775 DERIVED, NOT MEASURED** at the owner-stated $0.0513/core-h (`COMPUTE_BUDGET_CHARTER.md` §5).
- Ledger row: `docs/COST_CALIBRATION.md`, id assigned at commit.

## 7. Disclosures

- The runner's `R2_*/STATUS.T10aR2_R2_*` files are infrastructure records of the launch argv's exit (L-342); the physics-critical rc is the in-wrapper `T10aR2_runs/STATUS.R2_*`.
- The shared index carried staged deletions of this run tree's committed files at grading time; inspected, never reverted; this commit names its own paths only.

---

## 8. APPENDED NOTE, 2026-08-26 — **THE B1 SUCCESSOR IS SKIPPED, AND THIS RECORD IS THE REASON**

**Appended by a heat-transfer lane, `[lab-attributed]`, ZERO COMPUTE. Nothing above this line is altered; lines whose number changed above this section: 0.** Nothing has been sent, filed, submitted, uploaded, registered or posted outside this box (`CLAUDE.md` rule 7).

A successor arm to T10a's B1 ceiling row (`GATE FAIL`, 0.12463 % against a 0.07676 % band, `T10a_RESULTS.md:65`) was considered for registration and **is not registered.** The decision rests on this record's own closing sentence and on nothing else: §5 states, of the finding that *"the residual ≈ −2.6 W/m² is common to all three levels and is not a discretisation error of the 2LI ladder"*, that **"That is a finding for the supervisor to place; this record does not name its cause."** §4 records the 2LI c/m/f triple as **OSCILLATORY**, so RR2 and RR5 are `NOT A RESULT` and no order or band survives to be refined; §7 names no arm; and the parent record is no more forthcoming — `T10a_RESULTS.md` §1.1 says of its own B1 reading that *"That reading uses the exact reference, so it is not an instrument independent of the hypothesis and **grounds no repair**"*. **Neither record names a cause, and neither names a next diagnostic arm.** A pre-registration written now would have to invent the hypothesis it claims to test, which is the one thing a pre-registration exists to prevent: the gate would be chosen by the lane rather than by the record, and its "prediction" would be a guess dressed as a design. Registering the arm is therefore **deferred to the supervisor's placement of the §5 finding**, which is the owner this record itself names. **No T10a or T10a-R2 verdict moves on this note, no band is widened, narrowed or reinterpreted, and no frozen file is edited.**
