# K0f results — graded 2026-08-26 by the frozen comparator at ten arms

**Rung verdict, as printed by the frozen comparator: `GATE REACHED` — every one of the ten graded rows is `NOT A RESULT`, tally 0 of 10; unreached column `P` (Blay, Mergui and Niculae 1992 `NOT OBTAINED`).** No row was inside or outside a band: the ordered gate stopped at limb (1) on all ten rows because **no level is iteratively CONVERGED under the registered §7.1 criterion** — the largest change of `T` between the `endTime − 4000` and `endTime` checkpoints is 0.14–13.7 K on every case against a criterion of 1e-6 × range ≈ 2.0e-5 K. That is the finding of this grading, stated as the comparator states it. Nothing here is a graded result against the reference, and nobody may later read it as one.

Pre-registration: `docs/campaigns/F14-cooling-ladder/K0f_PREREGISTRATION.md` (v1.0 registered 2026-08-26T03:25:14Z; AMENDMENT 1 authorised L3 — ten arms, POINT 925.90 core-min; AMENDMENT 2 re-froze the launchers only). Run tree `verification/runs/F14-cooling-ladder/K0f_runs/`. Graded by a lab lane on the heat-transfer supervisor's order `[lab-attributed]`; no verdict below is the lane's — every one is the comparator's printed word.

## 1. The frozen instruments, hashed before they were believed

| instrument | §7.7 blob | `git hash-object` on disk at grading | match |
|---|---|---|---|
| `scripts/mark_done_k0f.py` | `f01e3fce18c982bdd14038598a0f10c33465d924` | `f01e3fce18c982bdd14038598a0f10c33465d924` | SAME |
| `scripts/analyse_k0f.py` | `764dedc6dadf38660becbc5d727184a363eb2d77` | `764dedc6dadf38660becbc5d727184a363eb2d77` | SAME |
| `scripts/check_k0f_extraction_equivalence.py` | `31c902de918e0c7855b0f97285a5393c27d25248` | `31c902de918e0c7855b0f97285a5393c27d25248` | SAME |

`analyse_k0f.py` was run with `--expect-sha 764dedc6…` (its own Charter §2d refusal armed) and printed the same blob. `mark_done_k0f.py --selftest`: every clause fired on a planted defect and stayed quiet on the clean counterpart, rc 0. `analyse_k0f.py --selftest`: PASSED, rc 0.

## 2. Completion — the strict rule (rule 4), ten of ten

`mark_done_k0f.py --root K0f_runs <case>` on `M2_m`, `C_lam`, `B_hi`, `I_hi`, `M1_m_seed` each printed `1/1 cases meet the strict completion rule`, rc 0; `DONE.M1_c M1_f M1_m M2_c M2_f` already existed. All ten `DONE.*` markers present; the comparator printed `ALL 10 DONE markers present`. Every `STATUS.<case>` reads `rc=0`, `checkMesh_rc=0`, `ranks=1`, `capped` not set (walls below every `timeout_s`); every `log.solve` carries `End`, last `Time = 40000` == `endTime`, 40 000 `Time =` lines.

| case | wall s | ExecutionTime s | timeout s | core-min (wall × 1 ÷ 60) |
|---|---:|---:|---:|---:|
| M1_c | 3 355 | 3 334.47 | 26 100 | 55.917 |
| M2_c | 3 162 | 3 141.26 | 26 100 | 52.700 |
| M1_m | 7 560 | 7 538.07 | 51 161 | 126.000 |
| M2_m | 6 576 | 6 375.06 | 51 161 | 109.600 |
| B_hi | 6 947 | 6 743.21 | 51 161 | 115.783 |
| I_hi | 6 855 | 6 634.60 | 51 161 | 114.250 |
| M1_m_seed | 7 145 | 6 929.93 | 51 161 | 119.083 |
| C_lam | 5 742 | 5 565.03 | 38 370 | 95.700 |
| M1_f | 17 448 | 17 400.15 | 100 530 | 290.800 |
| M2_f | 17 913 | 17 893.79 | 100 530 | 298.550 |
| **sum** | **82 703** | | | **1 378.383** |

Source: `K0f_runs/STATUS.*`, `K0f_runs/<case>/log.solve`.

## 3. Controls, in the order the comparator ran them

- **Pre-grading equivalence gate (§V.4) on `M1_f` at t = 40000, OpenFOAM `postProcess -func sample` vs the in-comparator reader:** worst |diff| `T` 8.08e-08 / 1.86e-08 K (criterion 2.00e-05), `U.x` 2.66e-09 / 8.10e-11 m/s (criterion 5.70e-07) on the vertical / horizontal mid-planes — **AGREE, GATE PASSED**.
- **Planted zero (§8.1 superseded):** P1 `PLANT_T` 1.234e-03 K into cell 0 of a copy of `T` — **seen** by the production scalar reader; P2 `PLANT_U` 1.234e-03 m/s into the x-component of cell 0 of a copy of `U` — **seen** by the production vector reader; P3 negative control — a 0.0 plant on a 0.0 background is not distinguishable, as registered.
- **Convergence (§7.1), every case `converged=False`** — max |ΔT| between the 36000 and 40000 checkpoints vs 1e-6 × range: M1_c 8.713 K vs 1.971e-05; M1_m 3.444 vs 1.973e-05; M1_f 6.539 vs 1.993e-05; M2_c 1.607 vs 1.953e-05; M2_m 2.924 vs 1.966e-05; M2_f 0.1379 vs 1.976e-05; C_lam 13.675 vs 1.988e-05; B_hi 7.928 vs 2.029e-05; I_hi 9.968 vs 1.975e-05; M1_m_seed 5.074 vs 1.989e-05.
- **y⁺ max:** M1_c 3.046, M1_m 2.260, M1_f 1.639, M2_c 3.628, M2_m 2.789, M2_f 2.044, C_lam 2.193, B_hi 2.234, I_hi 2.255, M1_m_seed 2.464 — `M1_f` 1.639 reported inside the window.
- **Guards (each withdraws the run, never the hypothesis):** B — worst |dΘ| 1.6017 K at G1@0.95 exceeds 1.0 K (the floor temperature awaits the primary); I — dG5a 0.032747 m/s, dG8 0.000000 m, quiet; DC — UNMEASURED, `C_lam` is not converged; **SEED — the finding: G1 differs between `M1_m` and `M1_m_seed` by 1.75591 at G1@0.95, more than its registered band**; M0 Boussinesq model-form floor 1.65 % on velocity, 0.031 % on Nusselt, reported beside every row, never subtracted.
- **Reference:** NOT OBTAINED (`K0f_runs/K0d_reference_primary.json` absent).

## 4. The ten graded rows, verbatim from the comparator

Every row: verdict **`NOT A RESULT`**, ground `level(s) NOT CONVERGED: L1, L2, L3`. The triples, printed beside each row as rule 5 requires (c/m/f; GCI quoted only where the comparator quoted it, i.e. only on monotone CONVERGING triples):

| row | band | M1 triple | M1 state / p / GCI | M2 triple | M2 state / p / GCI |
|---|---|---|---|---|---|
| G1 | ±1 K | [290.433, 290.226, 290.451] @0.1 | OSCILLATORY, p n/a, GCI not quoted | [291.164, 291.321, 291.969] @0.05 | DIVERGENT, p 4.2409, not quoted |
| G2 | ±1 K | [289.998, 289.93, 290.382] @0.95 | OSCILLATORY | [292.113, 292.252, 293.025] @0.05 | DIVERGENT, p 5.1214 |
| G3 | ±0.057 m/s | [−0.489102, −0.484406, −0.453787] @0.05 | DIVERGENT, p 5.5973 | [−0.375644, −0.374397, −0.370962] @0.05 | DIVERGENT, p 3.0266 |
| G4 | ±0.057 m/s | [0.447281, 0.459335, 0.44473] @0.05 | OSCILLATORY | [0.368237, 0.367201, 0.340813] @0.05 | DIVERGENT, p 9.6613 |
| G5a | ±0.057 m/s | [0.714303, 0.526305, 0.476772] | CONVERGING, p 3.9437, GCI 4.6890 % | [0.614428, 0.575937, 0.332725] | DIVERGENT, p 5.5037 |
| G5b | ±0.0208 m | [0.017, 0.0205, 0.0275] | DIVERGENT, p 2.0757 | [0.018, 0.0185, 0.0935] | DIVERGENT, p 14.9487 |
| G6 | ±10 % of |q_ref| | [173.379, 161.642, 155.143] | CONVERGING, p 1.7416, GCI 6.5719 % | [213.079, 208.274, 194.419] | DIVERGENT, p 3.1654 |
| G7 | ±1 K | [0.0105342, −0.00849967, −0.00271193] | OSCILLATORY | [0.00232381, −0.00593317, −0.0115231] | CONVERGING, p 1.1458, GCI 128.9107 % |
| G8 | ±0.104 m | [0.0122837, 0.006432, 0.00384112] | CONVERGING, p 2.4050, GCI 67.6607 % | [0.0154574, 0.0083692, 0.00511869] | CONVERGING, p 2.3009, GCI 67.9134 % |
| S1 | exact match | STRUCTURAL: exact match across L1/L2/L3 required | DIVERGENT, no triple, no order, no GCI | same | DIVERGENT |

Reported, never graded: R1 turbulent kinetic energy on both mid-planes; M0 as above.

**TALLY 0 of 10. RUNG VERDICT (comparator): `GATE REACHED`; unreached column P.** The rule-5 order held: limb (1) turned every row `NOT A RESULT` before any band was read, so no row is `PASS` or `GATE FAIL`, and the four CONVERGING triples (G5a-M1, G6-M1, G7-M2, G8 both) carry their p and GCI beside the `NOT A RESULT` they cannot lift.

Source: `verification/runs/F14-cooling-ladder/K0f_runs/log.analyse_k0f.20260826T205552Z.txt` (the comparator's full stdout, 100 lines).

## 5. What the grading says, and what it does not

1. **Not one level converged under §7.1.** The registered instrument is the checkpoint-to-checkpoint change, not the residual; at 40 000 iterations the flow on every case is still moving by 0.1–14 K somewhere in the cavity. §7.1 registers **one** extension of +20 000 iterations, decided "on the convergence state alone, never with a graded value in view" — that decision is the supervisor's, and this record makes no recommendation. The graded values above are on the record only because rule 5 prints the triple beside a `NOT A RESULT`; they are not to be quoted as results.
2. **The seed guard fired**: 1.756 K at G1@0.95 between `M1_m` and `M1_m_seed`, above its band, on two unconverged cases. With both levels unconverged this is not yet separable from item 1.
3. The extraction equivalence (§V) is closed by measurement on K0f's own `M1_f`, not only on K0d's preserved evidence: 4 of 4 sets AGREE.
4. Predictions scored: the registration made no numeric physics prediction (§0/A1.4 registered the reachable columns — best verdict `GATE REACHED` naming `P`: **HIT**, that is what printed); the cost expectation of A1.2c (≈ 1.2 × POINT ≈ 1 111 core-min) — **MISS**, measured 1 378.383 = 1.489 × POINT (§6); the `nA = 18` parity prediction (§G) was checked at build, not here.

## 6. Cost — rule 12, measured against the registered lines

- **Predicted (A1.2, ten arms): POINT 925.90 core-min** (S 912.40 + I 13.50), CEILING 2 750.70, carried guard 2 748.64. Registered expectation A1.2c ≈ 1 111.
- **Measured solver spend: 1 378.383 core-min** = 82 703 wall s × 1 rank ÷ 60 from the ten `STATUS.*`; gross = cleaned — every row is over 3 600 wall s (all ten walls 3 162–17 913 s) and **none is a stall**: each ran monotonically to `Time = 40000` with `ExecutionTime` 97.0–99.9 % of `ClockTime`. Instruments this session (`mark_done` ×5, equivalence gate, `analyse` and both selftests) under 1 core-min, inside the 13.50 bound.
- **Ratio actual/POINT 1.489; actual/CEILING 0.501; actual/S 1.511.** Per case vs its line: M1_c 1.285, M2_c 1.211, M1_m 1.478, M2_m 1.285, B_hi 1.358, I_hi 1.340, M1_m_seed 1.397, C_lam 1.497 (the registered ESTIMATE line), M1_f 1.736, M2_f 1.782.
- **Attribution: rate misprediction that grows with cell count, not wall contention and not waste.** Measured s per cell-iteration: L1 3.07–3.26e-06, L2 3.18–3.76e-06, L3 4.41–4.54e-06 against the registered POINT 2.549e-06 — the L3 rate is 1.73–1.78× the basis, the L1 rate 1.21–1.28× (K0d's C-99 measured 1.21 on L1, reproduced). Contention on wall: present, not limiting — `ClockTime − ExecutionTime` ≤ 3.1 % on every case (worst M2_m 201 s of 6 576). **WASTE: 0.000 core-min** named separately — no re-fire, no refused-after-arming case, no cap crossing (largest wall/timeout 0.178, M2_f).
- **Dollars, DERIVED, NOT MEASURED** at the owner-stated $0.0513/core-h (`COMPUTE_BUDGET_CHARTER.md` §5): **$1.1785** against POINT $0.7916. The `C_lam` laminar 0.75 factor is calibrated: 5 742 s vs the L2 turbulent mean 6 866 s = 0.836, not 0.75.
- Ledger row: `docs/COST_CALIBRATION.md`, id assigned at commit.

## 7. Disclosures

- The supervisor's brief listed `DONE` markers as existing for `M1_c M1_f M1_m M2_c M2_f` only; that matched disk. The five markers written here carry the strict rule's clause list (`strict rule met`), not a lane's word.
- `analyse_k0f.py` writes no JSON; its stdout is the record and is retained under the run tree at the path in §4.
- The shared index carried other teams' staged deletions at grading time (T10aR2/T4b run files); inspected, never reverted; this record's commit names its own paths only (rule 10).
