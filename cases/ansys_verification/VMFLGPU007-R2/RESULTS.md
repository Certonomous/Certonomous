# VMFLGPU007-R2 — RESULTS

**Case:** GPU solver path on turbulent flow with heat transfer over a backward-facing step (VM2026R1, **p. 243**; CPU parent VMFL013).
**Verdict:** **`GATE REACHED`** — the frozen comparator GRADED the run (exit 0); limb B holds and limb C is inside its band.
**Register row:** #43. **Calibration:** C-199.
**Graded by:** the ansys-verification supervisor personally, with the frozen comparator on the box, against the run tree pulled from the GPU instance and `sha256`-verified byte-identical across the transfer. **Drafted into records by `ansys-lane-opus48`; no number in this file was re-graded or recomputed by the drafting lane.**

This case **SUCCEEDS VMFLGPU007 (R1)** under `ANSYS_VERIFICATION_CHARTER` §6. **R1 is FROZEN and PRESERVED and is NOT re-graded**; its register row #40 stands `NOT A RESULT`. R1's tree, pre-registration and comparator are untouched.

---

## 1. The headline — the honest repair worked

**R1 → R2 flipped `NOT A RESULT` → `GATE REACHED` by moving ONLY `endTime`, with the plateau tolerance byte-identical.**

R1 died at the frozen plateau clause `IG3` because its wall-temperature channel had not settled at `endTime`. R2 extends the horizon — and only the horizon — and the channel settles. `endTime` is a **cost parameter**; choosing it from R1's own measured decay rate is legitimate, where choosing the tolerance from data is not. **The tempting repair was to widen `PLATEAU_PTP_TOL`; it was NOT widened, and the case passed anyway on the legitimate lever.** This is the family's first demonstration that the honest repair works.

| Level | endTime R1 → R2 | plateau ptp R1 (K) | R1 vs 1.0e-4 K | plateau ptp R2 gpu / cpu (K) | R2 vs 1.0e-4 K |
|---|---|---|---|---|---|
| L1 | 1200 → 3200 | 0.0237893 | **238× ABOVE** | 4.181e-06 / 4.193e-06 | **24× BELOW** |
| L2 | 1800 → 4400 | 0.0120540 | **121× ABOVE** | 7.231e-06 / 7.238e-06 | **14× BELOW** |
| L3 | 3000 → 6200 | 0.00358665 | **36× ABOVE** | 6.804e-06 / 6.806e-06 | **15× BELOW** |

`PLATEAU_PTP_TOL = 1.0e-4` K is **byte-identical to R1**. The only registered quantity that moved is `endTime` (1200 / 1800 / 3000 → 3200 / 4400 / 6200), chosen from R1's own measured `wallTmin` decay rate.

---

## 2. Identity and freeze — verified

| Artifact | Blob / commit | Verification |
|---|---|---|
| Freeze commit | `ed980d33ff53f35d51530ecc8a20962cffb26851` | an **ancestor of HEAD** |
| Comparator (`grade_vmflgpu007_r2.py`) | `aae498976139cd8489c9b3de48427f1f425f875c` | **identical at the freeze, at HEAD, on the box, AND on the GPU instance where it ran** |
| Pre-registration | `163ff4a229c7b7cfb2e20707d427ddd94fd8c68b` | frozen §1–§13 |
| Launcher | `5538cdf076069c382c4fdb3bea93378cd0c68621` | frozen |

The instance `LAUNCH_RECORD.txt` records all **five** frozen blobs plus `head = 05555370…`, so the launch-time freeze guard fired correctly and **the file that ran is the file that is frozen**. Comparator **exit code 0**.

---

## 3. Strict completion (CLAUDE.md rule 4) HOLDS on all six arms

On every one of the six solves (L1/L2/L3 × GPU arm + forced-CPU control):

- `rc = 0` and `cap_fired = 0` on every `RUN_RC`;
- an `End` line in each of the six logs;
- exactly **one** `log.*Foam` per solve directory;
- `Time =` count exactly equal to the registered `endTime` (3200 / 4400 / 6200);
- fields `T U p_rgh alphat nut k epsilon` present at `endTime`, age guard met;
- every function-object tree carrying exactly **one** time directory — **the cardinality guards were SATISFIED, not merely unexercised.**

**INFRASTRUCTURE, never refusing (L-342):** the `ExecutionTime` line count is `endTime + 2` at every level (**3202 / 4402 / 6202**) — petsc4Foam prints two initialisation-timing lines before the first solve. The frozen comparator reports this and does not refuse on it.

**No `CAP_OVERRUN` or `CAP_EXCEEDED` file exists** for this case — proven by `find` over the whole run root and the case directory. (Contrast VMFLGPU005, which carried a mis-scoped launch-level overrun file.)

---

## 4. The gate — per level

| Level | cells | endTime | peak Nu gpu @ x/H | peak Nu cpu @ x/H | limb B \|dq\|/\|q\| | y+(gate patch) [min, not gated] |
|---|---|---|---|---|---|---|
| L1 | 3648 | 3200 | 64.825965 @ 4.5312 | 64.825965 @ 4.5312 | 8.215e-10 | 36.5 [2.85] |
| L2 | 7776 | 4400 | 64.109422 @ 4.6875 | 64.109412 @ 4.6875 | 1.561e-07 | 36.3 [1.75] |
| L3 | 16128 | 6200 | 63.792470 @ 4.6528 | 63.792470 @ 4.6528 | 7.365e-09 | 36.2 [2.64] |

Birth certificate matched at every level (3648 / 7776 / 16128, measured pre-freeze). `Nu` is DERIVED by the comparator from the frozen constants `q'' = 1000 W/m²`, `κ = 1.408 W/m-K`, `H = 1 m`, `T_inlet = 300 K` — a solver-side Nusselt number is never trusted.

**LIMB A — GPU execution established at every level, and R1's silent false pass DEMONSTRATED REPAIRED ON REAL BYTES.** R2 locates columns by the PETSc `-log_view` table's own header via two independent derivations that must agree or refuse — **GPU %F = col 25, CpuToGpu Count = col 21 of 26** — and reports **GPU %F in [100, 100] over 13 MatMult/KSPSolve rows at every level**:

| Level | CpuToGpu Count by event | total |
|---|---|---|
| L1 | KSPSolve 9601, MatMult 19200 | **73606** |
| L2 | KSPSolve 13201, MatMult 26400 | **101206** |
| L3 | KSPSolve 18601, MatMult 37200 | **142606** |

The forced-CPU control reports **GPU %F max 0 and CpuToGpu Count total 0 at every level**. R1's reader took GPU %F as `max()` of trailing tokens and returned the CpuToGpu size in MBytes (**210.0 / 672.0 / 2320.0**, figures a percentage cannot reach — a silent FALSE PASS at clause A3), and its clause A4 `h2d` regex was UNPASSABLE by construction (it matched only the legend line). **R2's counts are non-zero, real, and read from the table header.**

**LIMB B (HOLDS, PASS-CAPABLE — a same-discrete-problem identity):** worst `|dq|/|q|` = **1.561e-07** against band **1.0e-04** (identical mesh, identical scheme, so discretisation error cancels on both sides).

**LIMB C (HOLDS, CEILING GATE REACHED — a continuum claim without a triple):** finest-level peak Nu **63.792470** vs reference **64.853000** (rel **0.0164**, band **0.2000**); peak location **4.6528** vs **5.8209** (abs **1.1681 x/H**, band **1.5000**) — inside both. Reference: Vogel & Eaton peak Nu **64.8530** @ x/H **5.8209** (experimental), parsed from VMFL013's archive into the tracked `reference/vmfl013_vogel_eaton_nu.csv`. **Experimental reference → limb C's ceiling is `GATE REACHED`, never `PASS`.**

---

## 5. Mesh-sensitivity spread — the registered uncertainty channel

This family's registered uncertainty channel is a **BOUND on observed variation over the meshes actually built — never an error estimate and never extrapolated.** Peak Nu over L1/L2/L3 = **63.792470 .. 64.825965**, **spread 1.033495 = 1.620 % of the finest**; peak-location spread **0.1562 x/H**.

**NO Roache triple is registered** (`H1 = 0.07 m` held identical at every level for the wall functions, so refinement is not systematic). Rule 5's triple gating does not fire because no triple is registered — **A LIMITATION, NOT AN EXEMPTION** — while rule 5's limb (1) (not iteratively converged or not plateaued → `NOT A RESULT`) **FIRES IN FULL, and the case passed it.** **NO GCI, no observed order, no extrapolated uncertainty is computed or printed by the comparator, and none may be quoted from this record.**

---

## 6. Controls live

- **Planted-zero (rule 3):** `plant fired` at all three levels.
- **Instrument health (this drafting lane, after clearing `__pycache__`):** `--selftest` **40/40 under `python3` AND 40/40 under `python3 -O`**, rc 0 both; **`ast.Assert` = 0** by an AST walk, so the `-O` run is a real check.

---

## 7. Cost (CLAUDE.md rule 12) — this family's best calibration

From `COST.txt` and the six `RUN_RC.*`: `total_wall_s` **1682**, `gpu_h_total` **0.467222**, `cpu_arm_core_min` **9.7833**. Per-arm wall_s: GPU 151 / 291 / 646; CPU 36 / 114 / 437.

| Quantity | Registered (PREREGISTRATION §9 @ `ed980d33`, carried byte-identical from R1) | Measured | Ratio |
|---|---|---|---|
| GPU | 0.6780 GPU-h (cap 1.5) | 0.467222 GPU-h | **0.6892×** |
| CPU | 13.5104 core-min (cap 90) | 9.7833 core-min | **0.7241×** |

Both **UNDER**, both within 31 % — **by far this family's best calibration** (vs C-182's 0.4385× / 0.1133× on the sister case). Caps: **31.15 %** of the GPU cap, **10.87 %** of the CPU cap; `cap_fired = 0` on all six arms — neither fired, neither approached. **WASTE 0.000 for the run.**

**Attribution — the lesson worth recording:** the estimate was built from **R1's OWN MEASURED run of the SAME case on the SAME meshes** (an `endTime`-only change is a pure horizon extension), and it landed within 31 %. C-182 missed by 2–9× because it TRANSFERRED a per-iteration cost model from a **different solver and mesh family**. **A cost model is accurate within a case and unreliable across one** — this is the standing rule this row earns (calibration C-199).

**Dollars DERIVED, NOT MEASURED** at the published-list **$0.8048/GPU-h** (g6.xlarge us-east-2): **$0.3760 derived**. The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5); the console figure is owed and supersedes.

**The idle is separate and is NOT this case's:** the card idled 03:20:39Z → 16:07:50Z = 767.18 min = 12.786 GPU-h = $10.29 derived before this run, and idles again from 16:35:52Z. INFRASTRUCTURE, boarded, **NEVER folded into this or any case's ratio** (`COMPUTE_BUDGET_CHARTER.md` §6).

---

## 8. What this row does NOT claim

- Nothing about **Ansys** — this box has no Fluent.
- Nothing about **GPU performance** — a GPU arm SLOWER than the CPU arm passed every limb, and it was slower at every level here (GPU 151/291/646 s vs CPU 36/114/437 s), corroborating C-182 and row #39 that at these mesh sizes the GPU path is a **correctness vehicle, not a speedup**.
- **No PASS on limb C** — the experimental-reference ceiling is `GATE REACHED`.
- **No discretisation-converged physics result** — without systematic refinement the case cannot claim one, and does not.

**Credential:** limb B's GPU==CPU identity PASS at 1.561e-07 is a NUMERICAL-PATH credential, not the physics-verification credential the register's PASS count tracks. **The PASS count does NOT move; it stays at 6** (rows #2, #3, #7, #13, #15, #28).

---

## 9. Primary evidence

- `verification/runs/ansys_verification/VMFLGPU007-R2/GRADE_OUTPUT_2026-08-28.txt` — the comparator's verbatim stdout, committed as primary evidence per rule 13.
- The full run bundle (`COST.txt`, six `RUN_RC.*`, per-level logs and `postProcessing`, `LAUNCH_RECORD.txt`) was produced on the GPU instance and pulled to the box `sha256`-verified byte-identical; `**/postProcessing/` is gitignored (`.gitignore:67`), so the gate reader's series exist on disk only — not force-added, `.gitignore` not edited. *Gitignored is not filed.*
