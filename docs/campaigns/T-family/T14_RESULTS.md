# T14 results — 2-D transient conduction in a square (T11b), Robin faces, EXACT tier

Graded 2026-08-27 by the frozen comparator at three levels plus a temporal-bias control.
**RUNG VERDICT: `PASS` — three of three graded rows PASS, all four registered
predictions HIT.**

Pre-registration: `docs/campaigns/T-family/T14_PREREGISTRATION.md`.
Run root: `verification/runs/T-family/T14_runs/`.
Comparator stdout at `verification/runs/T-family/T14_runs/log.analyse_t14.20260827T164421Z.txt`;
machine record at `verification/runs/T-family/T14_runs/gate_t14.json`.

---

## 1. The freeze set — six of six MATCH on both channels

| file | registered blob | registered sha256₁₆ | on disk | |
| --- | --- | --- | --- | --- |
| `exact_t14.py` | `4f72de8d` | `251ea2afd6c350fd` | both | MATCH |
| `build_t14.py` | `677363da` | `71ef5e247f213464` | both | MATCH |
| `analyse_t14.py` | `386181db` | `67888ce0056fc811` | both | MATCH |
| `mark_done_t14.py` | `680eddd3` | `b6b16ce3f7df8430` | both | MATCH |
| `run_one_t14.sh` | `8b2b7b52` | `9ff22e41c486ca1a` | both | MATCH |
| `T14_registered.json` | `149bbf0b` | `ad3930a7a9fc6673` | both | MATCH |

**No drift. No frozen file edited.** `__pycache__` cleared before the run.

## 2. Completion — the strict rule (rule 4), four of four

`mark_done_t14.py` (frozen, `680eddd3`): **`DONE` on `T14_SQ_c`, `T14_SQ_m`,
`T14_SQ_f` and `T14_SQ_f_CT`**, rc 0. All four `STATUS.*` read `rc=0 …
capped=no checkmesh_rc=0 note=clean`, solver `laplacianFoam`.

## 3. The referent, verified before it was used — Route B plus a cross-check

`exact_t14.verify`: PDE residual **7.60e-06**; symmetry gradients **0.0e+00**;
Robin faces **9.5e-08**; initial condition **3.6e-05**; `theta(x,y) = theta(y,x)`;
Simpson agrees to **3.7e-12**. **And it is cross-checked against a DIFFERENT
rung's registered values: T11 at Bi = 1, Fo = 0.2 — PASS.** A referent checked
only against itself is checked against nothing; this one is checked against a
prior registration. `C_REF` further requires that a 1 % mutation of `C_n` be
REFUSED by `exact_t14.py --selftest`.

## 4. Gate (1) controls — all clear on every level

- **`C_CONV`**: every level *"reached endTime, every step converged: True"* —
  each timestep's `T` solve final residual ≤ 1e-10, with an `End` line.
- **`W0` transposition symmetry witness** (floor 1e-9): **c 3.01e-14, m 3.01e-14,
  f 6.01e-14** — four to five orders inside the floor.
- **`C_VF`** (L-341): `valueFraction` on each level read from `CASE.txt` must
  equal `Bi/(Bi + 2N)`; the comparator refuses otherwise and did not.

## 5. Planted-zero controls (rule 3) — three readers, three PASS

| reader | plant | cells planted | recovered | |
| --- | ---: | ---: | ---: | --- |
| G1 (volume average) | 1.234e-03 | **40 000 — ALL CELLS** | 1.234e-03 | PASS |
| G2 (point, cell 0) | 1.234e-03 | 1 | 2.7765e-03 | PASS |
| G3 (point, cell N_f−1) | 1.234e-03 | 1 | 2.7765e-03 | PASS |

Detection floor 1e-07 on each. **The sizing is the point** (L-340): G1 averages
over the quarter square, so a one-cell plant would be attenuated by 40 000 and
the reader would look blind when it is not — the registration plants **every
cell** for the averaging reader and **recovers the plant exactly**, 1.234e-03 for
1.234e-03. The point readers get a one-cell plant and recover 2.25×
it through the separable linear extrapolation, as a point reader should.

## 6. THE THREE GRADED ROWS — 3 of 3 `PASS`, every triple `CONVERGING` at p ≈ 2

| row | quantity | fine value | reference | deviation | band | triple | state | p | GCI | verdict |
| --- | --- | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | --- |
| **G1** | `theta_mean` over the quarter square | 0.7252180490 | 0.7252148236 | +4.448e-06 (rel +6.13e-06) | ±5e-5 rel | (7.252379e-01, 7.252220e-01, 7.252180e-01) | **CONVERGING** | **1.9999** | 2.2836e-04 % | **PASS** |
| **G2** | `theta` at (0,0), centre of the full square | 0.9037256580 | 0.9037197910 | +6.492e-06 (rel +7.18e-06) | ±1e-4 rel | (9.038461e-01, 9.037497e-01, 9.037257e-01) | **CONVERGING** | **2.0000** | 1.1106e-03 % | **PASS** |
| **G3** | `theta` at (1,0), mid-face on the symmetry plane | 0.6116455064 | 0.6116341596 | +1.855e-05 (rel +3.03e-05) | ±1e-4 rel | (6.117877e-01, 6.116739e-01, 6.116455e-01) | **CONVERGING** | **2.0066** | 1.9192e-03 % | **PASS** |

All three triples are monotone, so each GCI at Fs = 1.25 is quoted. **Every row is
graded under rule 5 (3): `CONVERGING` and inside the pre-registered band.** No row
needed the NOT-A-RESULT path, and no GCI is quoted anywhere it should not be.

## 7. The temporal-bias control `C-T` — REPORTED, never gated

`T14_SQ_f_CT` is the fine mesh with `deltaT` halved (5e-05 against 1e-04,
40 000 steps against 20 000). **It moves G1 by −1.310e-06 relative = 0.026 of the
G1 band.** Registered as *"REPORTED as a fraction of the band, never gated"*, and
it is reported here as exactly that. **It is not subtracted from any graded value
and it does not enter any verdict** — it is the measurement that says the
temporal discretisation is not carrying the spatial result, and at 2.6 % of the
band it says so comfortably.

## 8. THE FOUR REGISTERED PREDICTIONS — four HIT, none missed

- **P1 — HIT.** *"G1, G2, G3 all PASS: G1 inside ±5e-5 relative, G2/G3 inside
  ±1e-4."* Measured relative deviations **+6.13e-06**, **+7.18e-06**, **+3.03e-05** —
  inside by 8.2×, 13.9× and 3.3× respectively.
- **P2 — HIT.** *"all three triples CONVERGING with observed order p in
  [1.5, 2.5]."* Measured **1.9999, 2.0000, 2.0066** — a second-order scheme
  delivering second order on all three rows.
- **P3 — HIT.** *"C-T moves G1 by less than 10 % of the G1 band (|move| < 5e-6
  relative)."* Measured **1.310e-06 relative, 2.6 % of the band** — inside by 3.8×.
- **P4 — HIT.** *"W0 < 1e-12 on every level."* Measured **3.01e-14, 3.01e-14,
  6.01e-14**.

## 9. Cost — rule 12, and the estimate was very nearly right

- **Predicted:** the registration names the **scratch rate** as the POINT the
  ledger compares against — **7.244 core-min** (0.137 + 0.547 + 2.187 + 4.373),
  from 1.64e-07 core-s per cell-step measured on 2 000 steps of a scratch copy of
  the coarse case. The T11-rate figure is **23.210**; the cap total is **100**.
- **Measured: 6.884 core-min** = (7 + 30 + 141 + 235) wall s × 1 rank ÷ 60.
- **Gross = cleaned.** **No row is anywhere near the 3 600 wall-s stall figure**
  (longest 235 s). **WASTE: 0.000 core-min**, named separately — no re-fire, no
  abandoned case. **No case approached its cap**: c 5.9 %, m 6.3 %, f 7.8 %,
  f_CT 6.5 %, total **6.9 % of 100**. The registration is explicit that these caps
  are **hang guards**, not forecasts, so the 6.9 % is not a calibration miss.
- **Ratio actual/POINT 0.950.** Per case: c 0.854, m 0.914, f **1.075**, f_CT 0.896.
- **Attribution: essentially none to attribute — this is a good estimate, and
  saying so is as much the ledger's job as recording a miss.** Measured core-s per
  cell-step: **c 1.400e-07, m 1.500e-07, f 1.7625e-07, f_CT 1.469e-07** against the
  registered scratch rate 1.64e-07. **The rate is very nearly mesh-independent: it
  rises only 1.26× across a 16× increase in cells.**
- **AND THAT IS THE FINDING, BECAUSE IT CONTRADICTS T13 GRADED THE SAME DAY.**
  T13 (`buoyantBoussinesqSimpleFoam`, coupled SIMPLE, same three-level structure,
  same scratch-rate methodology) saw its per-cell-iteration rate rise **4.33×**
  across a 16× cell increase and missed its POINT by **3.17×**, with the fine
  level breaking through the T4 ceiling rate. T14 (`laplacianFoam`, linear
  transient conduction) rises **1.26×** and lands at **0.950**. **The
  mesh-scaling penalty is a property of the SOLVER, not of the estimating method:
  a coupled pressure–velocity–temperature SIMPLE loop degrades with mesh size
  because its inner iterations and its matrix conditioning do; a single linear
  Laplacian solve at a fixed step count does not.** The correction recorded at
  T13 — scale a coarse-level POINT rate with cell count — **must therefore be
  applied per solver class and not lab-wide**, or it will over-predict linear
  transient rungs by 2–3× in the other direction.
- **Dollars, DERIVED, NOT MEASURED** at the owner-stated $0.0513/core-h
  (`COMPUTE_BUDGET_CHARTER.md` §5): **$0.0059** against a POINT of $0.0062.
- Ledger row: `docs/COST_CALIBRATION.md`, id assigned at commit from the tail.

## 10. Disclosures

- **The C-T arm is a control, not a fourth graded level.** It carries its own
  `DONE` marker and its own cost, and it is excluded from every triple. Anyone
  reading four `DONE` markers as four graded levels would be wrong.
- **Interpolation error enters G2 and G3's triples and is disclosed rather than
  removed**: both are pointwise rows read by separable linear extrapolation from
  the four nearest cell centres, and the registration says so where it grounds
  their ±1e-4 band.
- No frozen file edited (rule 6). **Nothing was sent, filed, uploaded, posted or
  registered outside this box** (rule 7).
