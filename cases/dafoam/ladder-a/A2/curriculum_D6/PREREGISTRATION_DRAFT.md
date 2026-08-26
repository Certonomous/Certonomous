# Curriculum D6 — Multipoint cruise on D4's case: three CL targets, weighted composite objective

**DRAFT v0.1, 2026-08-26. NOT FROZEN. NOT A PRE-REGISTRATION UNTIL RE-COMMITTED AS `PREREGISTRATION.md` WITH A FREEZE SECTION.**
Drafted by dafoam `lab-lane` at a teammate's request for `dafoam-supervisor`'s freeze decision. Nothing here is fired, filed or sent (rule 7).
Short form: everything not stated here is **inherited verbatim from D4-SHIPPED-R's family** (`curriculum_D4_SHIPPED/d4s_run_arm.sh`, ruling R4 amended at `6109aa45`) and from `curriculum_D4/PREREGISTRATION.md` §1, §5, §6, §7, §9, §10. Curriculum row: `cases/dafoam/EXPERTISE_CURRICULUM.md:96`.

## 1. What changes, and only this

| | D4 (PATCHED row) | D6 |
|---|---|---|
| case, mesh, np, FFD (6×2×8, 96 DVs), twist, launcher family | as D4 | **identical**; launcher `d6_run_arm.sh` derived exactly as D5 §1 (G-ROOT from birth naming D4/D4-SHIPPED(-R)/D5 roots forbidden; explicit cpuset by measurement at freeze; H5 14.0 GiB; rc from inspect; no `--rm`; deadline inside the container; `setsid nohup` bookkeeping driver with rc captured inside; no bare `assert`; launch record cites `bc0e687e`) |
| scenarios | one, CL = 0.5 | **three OpenMDAO scenarios sharing one geometry: CL targets 0.4 / 0.5 / 0.6**, each with its own `patchV` (AoA) DV and its own CL equality constraint |
| objective | CD | **composite `J = Σ wᵢ·CDᵢ`, weights FROZEN HERE: w = (0.25, 0.50, 0.25)** for (0.4, 0.5, 0.6). Weights are not tuned after a run; a second weight set is a new item |
| optimizer | IPOPT `max_iter` 100 | **identical** |

## 2. Arms

| arm | task | new compute |
|---|---|---|
| O_mp | IPOPT run_driver on J, `max_iter` 100 | yes |
| ACC_mp | cold primal at the endpoint, per point (three primals) | yes |
| F_mp | endpoint FD table of **J** over five registered components (named from the endpoint locus, D4 §6) — the bright line for the composite | yes |
| REF_off | D4's PATCHED optimum geometry re-trimmed to CL 0.4 and 0.6 (`findFeasibleDesign` on `patchV` only, no shape change) — the off-design reference that makes "single-point dominance" measurable | yes, two primals |

## 3. Gates — per point AND composite, both mandatory

* **G-D6-1 per-point verdicts (the curriculum's named failure mode):** for each CL target, `CDᵢ(mp) ≤ CDᵢ(REF_off)` → `PASS` for that point, else `GATE FAIL` for that point. **A composite `PASS` with any point `GATE FAIL` is reported as three verdicts, never as one.**
* **G-D6-2 composite:** `J_f < J₀` with reduction band **[15, 40] %** (D4's single-point reduction was 28.6758 % in band [25, 45]; a composite is bounded by its worst point, so the band opens downward).
* **G-D6-3 the single-point price:** `CD₀.₅(mp) − CD_f(D4) ∈ [0, 1.0e-3]` — multipoint cannot beat single-point at its own point (a negative value is a finding about D4, not about D6, and is `NOT A RESULT` for this gate pending triage).
* **G-D6-4 bright line:** F_mp aggregate vector-relative error ≤ 5 %, sign flips named per component. No grid family: **no GCI quoted.**

## 4. Cost — measured-derived from D4's rows

| arm | anchor | prediction (core-min) | cap |
|---|---|---|---|
| O_mp | 6.389 core-min/major (D4 PATCHED) × **3 scenarios** (three primals + three adjoints per major; the coloring is shared) × 80 majors point | **1,533.4** (point); 100-major reading 1,916.7 | 2,000.0 |
| ACC_mp | 3.0 × 3 (C-94) | **9.0** | 10.0 each |
| F_mp | 47.267 (C-96) × 3 points per FD primal pair | **141.8** | 180.0 |
| REF_off | 3.0 × 2 + `findFeasibleDesign` ≈ 5 primals ≈ 4.5 | **10.5** | 20.0 |
| **total** | | **1,694.7 core-min = $1.45 DERIVED, NOT MEASURED** (c7a.4xlarge $0.0513/core-h, reported-by-owner) | ceiling **2,230.0** |

**Exposure stated:** the ×3 per-major scaling assumes three independent adjoint solves per major and no shared-primal saving; D4-SHIPPED's measured 7.317 core-min/major (contended, C-117) would put O_mp at 1,756 (80 majors) — inside the cap. Above the curriculum's ~1,500 for a stated reason (three adjoints, not one).

## 5. Predictions, scored HIT/MISS afterwards, never adjusted

| # | prediction | number |
|---|---|---|
| P1 | `EXIT: Optimal Solution Found.` within `max_iter` 100 | majors **[60, 100]**, point 80 |
| P2 | composite reduction `(J₀ − J_f)/J₀` | **[15, 40] %, point 22 %** |
| P3 | single-point price at CL 0.5 | `CD₀.₅(mp) − 2.1125978e-02 ∈ [0, 1.0e-3]`, point **+3.0e-4** |
| P4 | off-design gain: `CD₀.₆(REF_off) − CD₀.₆(mp)` | **> 0**, point +8.0e-4; and at 0.4 **> 0**, point +2.0e-4 |
| P5 | O_mp cost | **[1,200, 2,000]** core-min, point 1,533.4 |
| P6 | per-point verdicts: **all three `PASS`** (the pathology does NOT appear at w = 0.25/0.50/0.25) | |

## 6. What this item does NOT claim
Nothing about the SHIPPED row (unbought; named unbought). Nothing about weight sensitivity — that is a second item. Nothing at np≠4. No Strouhal, no grid family, no GCI.

## 7. Freeze — NOT YET
Freeze requires: launcher and runScript diffs read by the supervisor as diffs; the comparator (per-point + composite) with its planted control; `test -e` on `/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint` returning false, stamped; then a commit whose sha this document names.
