# T4d — impinging round jet, H/D = 2, Re = 23 000: whole-rung grade. Verdict: **NOT A RESULT**

**Pre-registration frozen at commit `eae8e96c`**
(`heat-transfer T4d FROZEN: T4c cost-recalibration successor (caps re-sized from
measured T4c per-cell rates), grading path pinned by sha`), which contains
`docs/campaigns/T-family/T4d_PREREGISTRATION.md` and the five-file freeze set in
`verification/runs/T-family/T4d_runs/`, under which **no `T4d_IJ_*` case existed**.
All three case directories were built and run after it.

Toolchain: OpenFOAM ESI **v2606**, `/usr/lib/openfoam/openfoam2606`,
solver `buoyantBoussinesqSimpleFoam`
(`platforms/linux64GccDPInt32Opt/bin/buoyantBoussinesqSimpleFoam`,
per `STATUS.T4d_IJ_{c,m,f}`).

Verdict vocabulary fixed by `CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE FAIL
/ NOT A RESULT / BLOCKED / PENDING.**

**SUBMISSIONS PARKED** (rule 7). Nothing here authorises a send.

---

## 1. Headline

**RUNG VERDICT: `NOT A RESULT` on all three graded rows (G1, G2, G3), whole-rung.**

Each row reaches `NOT A RESULT` by **two independent grounds**, either of which is
sufficient under the frozen path:

1. **Gate-(1) iterative-plausibility failures (rule 5, clause 1).** The
   coarse level fails **C2** (nozzle-exit `U_c/U_bulk` = **1.1793**, outside
   ±3 % of 1.2245, i.e. below the 1.18777 floor), and the fine level fails
   **C6.3** (max G1/G2/G3 peak-`U/U_bulk` change between its last two
   checkpoints = **0.01518**, against the 2e-04 tolerance). A gate-(1) reason on
   any level turns a would-be PASS or GATE FAIL **into** `NOT A RESULT`; the gate
   can only make a verdict worse (rule 5).
2. **The Roache grid triples are not `CONVERGING`.** G1 is `OSCILLATORY`; G2 and
   G3 are `DIVERGENT`. A non-`CONVERGING` triple is `NOT A RESULT` whatever its
   value (rule 5, clause 2). No GCI is quoted for any row — the three values are
   not monotone, and a GCI on a non-monotone triple is never quoted.

The rung does **not** discharge the impinging-jet ladder. It owes a **state-(b)
successor** whose sole substantive task is the fine-level field convergence
diagnosed in §5.

---

## 2. Provenance and freeze verification (rule 2)

The frozen comparator `verification/runs/T-family/T4d_runs/analyse_t4d.py` was
verified to **be** the committed file before grading: its on-disk git blob is
`d616754e2e868d18a95bd77b339f8e2ed1d52370` == the committed blob `d616754e`
recorded in the pre-registration §12 freeze table. It imports the frozen
`analyse_t4.py` unchanged.

The comparator prints its own `sha256_of()` provenance at runtime; the values
this grade ran under:

| file | sha256 |
| --- | --- |
| `analyse_t4.py` (frozen, imported) | `9842dbc8146d4f156cd7fc343117b383139097989463139f884dd14769d777ad` |
| `analyse_t4d.py` | `0e9b13f79601463146606e536e459da969ada7b88cb5f62a536f4e4f5942b8c0` |
| `T4d_registered.json` | `2ad1fea29dc4c5342f4fbd799bec5c28a9147f5e41216a98aa373208a147c305` |

Shared Roache floors imported from `scripts/roache_triple.py`:
`STAGNANT_FLOOR = 0.5`, `P_MIN = 0.05`. Refinement ratio `r = 2.0`, factor of
safety `Fs = 1.25`.

---

## 3. Strict completion (rule 4)

The completion instrument is `verification/runs/T-family/T4d_runs/mark_done_t4d.py`,
git blob `8a281d728ae067352f12d5c72dc3cac495c94ac1` == HEAD, `CASES =
("T4d_IJ_c", "T4d_IJ_m", "T4d_IJ_f")`. It enforces the all-or-nothing rule
(`rc = 0`; an `End` line; last time == `endTime`; fields
`T U p_rgh alphat nut k omega phi` present at `endTime`; `ExecutionTime` count ==
`endTime`; every field newer than the case's own `0/T`, the age guard). It wrote
all three markers `DONE.T4d_IJ_{c,m,f}` = `strict rule met (physics-critical
clauses 1-6)`.

| level | case | `endTime` | STATUS | `core_min` | marker |
| --- | --- | ---: | --- | ---: | --- |
| coarse | `T4d_IJ_c` | 30 000 | `rc=0`, `note=clean`, `capped=no` | 21.667 | `DONE.T4d_IJ_c` |
| medium | `T4d_IJ_m` | 60 000 | `rc=0`, `note=clean`, `capped=no` | 206.100 | `DONE.T4d_IJ_m` |
| fine | `T4d_IJ_f` | 64 000 | `rc=0`, `note=clean`, `capped=no` | 1 200.233 | `DONE.T4d_IJ_f` |

The comparator's DONE gate (which checks the three markers exist, never invoking
`mark_done`) passed on the second grading run once `DONE.T4d_IJ_f` was present.
The first grading run correctly **refused (exit 2)** at that gate — `no
DONE.T4d_IJ_f` — because `mark_done_t4d.py` had not yet certified the fine level
(the coarse/medium markers were placed 2026-09-07 14:33Z, before the fine solve
even started at 2026-09-07 14:40Z; the fine solve completed 2026-09-08 10:41Z and
was certified after). The refusal, then the completion, then the grade is the
correct sequence: the comparator refuses rather than degrades.

---

## 4. Planted-zero controls (rule 3) — all four readers GREEN

All four readers on the grading path planted a known perturbation and read it
back from disk; every one saw its plant, and the blind arm read 0. **None
refused.** Run live on the real case directories.

| reader | outcome |
| --- | --- |
| G-row profile (frozen `planted_zero_control`, `PLANT = 1.234e-03`) | recovered **3.64454e-05** from 0.001234 at line 70469; demonstrated floor 1e-06 |
| y+ (`-postProcess -func yPlus`) | blind generic path returns **0 on every patch**; registered path plate max 0.6901; U ×4 → y+ ×2.000000000000 (expected 2) |
| exit-line (`U_c` reader) | recovered **4.71031e-05** from 0.001234 at line 6936; floor 1e-06 |
| flux (`φ` reader) | inlet φ ×1.01 → imbalance **0.00990095762** (predicted 0.00990095762, exact) |

The blind reader shown blind is what makes the seeing reader's zero evidence
(rule 3).

---

## 5. The grade — per level and per row

### 5.1 Iterative-plausibility controls (C1–C6), per level

| level | `t` | C1 plate y+max | C1b pipe y+max | C2 `U_c/U_b` | C3 imbalance | C6.1 floor max | C6.2 ratio | C6.3 Δfield |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| c | 30 000 | 0.6901 ✓ | 0.3991 ✓ | **1.1793 ✗** | 3.28e-08 ✓ | 5.703e-08 ✓ | 0.99964 ✓ | 1.396e-06 ✓ |
| m | 60 000 | 0.3492 ✓ | 0.2021 ✓ | 1.1936 ✓ | 1.11e-09 ✓ | 4.354e-09 ✓ | 1.00893 ✓ | 3.390e-06 ✓ |
| f | 64 000 | 0.1764 ✓ | 0.1022 ✓ | 1.2047 ✓ | 4.77e-09 ✓ | 2.534e-08 ✓ | 1.00648 ✓ | **0.01518 ✗** |

Two gate-(1) failures: **coarse C2** (`U_c/U_bulk` 1.1793 below the ±3 %-of-1.2245
band) and **fine C6.3** (field change 0.01518 > 2e-04). Both feed every row's
gate-(1) reason list.

### 5.2 The three graded rows (peak `U/U_bulk` of the radial profile at r/D)

| row | r/D | triple (c, m, f) | classification | observed `p` | GCI | fine value | reference | band | deviation | verdict |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| G1 | 1.0 | 1.0778, 1.0825, 1.0591 | **OSCILLATORY** | n/a | n/a | 1.0591 | 1.0890 | [1.0690, 1.1090] | −0.0299 | **NOT A RESULT** |
| G2 | 2.0 | 0.8265, 0.8173, 0.6615 | **DIVERGENT** | n/a | n/a | 0.6615 | 0.7888 | [0.7688, 0.8088] | −0.1273 | **NOT A RESULT** |
| G3 | 3.0 | 0.5490, 0.5409, 0.4403 | **DIVERGENT** | n/a | n/a | 0.4403 | 0.4632 | [0.4432, 0.4832] | −0.0229 | **NOT A RESULT** |

Gate-(1) note on every row (verbatim from the grade): *level c: C2 U_c/U_bulk
1.1793 outside +/-3% of 1.2245; level f: C6.3 field change 0.015178230567379214 >
0.0002*. No triple is `CONVERGING`, so no GCI is quoted (rule 5). References are
the ERCOFTAC Classic Collection case025 `ij2lr` bands carried from T4c/T4b
unchanged (pre-registration §6).

---

## 6. Physics finding — the fine level is not field-converged (owed triage)

The fine level reached `endTime` 64 000 with `rc=0`, `note=clean`, `capped=no`,
and passed the strict completion rule — **but it is not field-converged.** Its
**C6.3 field change of 0.01518 is ~76× the 2e-04 tolerance**, against coarse
1.396e-06 and medium 3.390e-06. The peak `U/U_bulk` at the graded stations was
still moving substantially between the fine level's last two checkpoints (60 000
and 64 000), which is directly consistent with the fine-level triple values
(1.0591 / 0.6615 / 0.4403) diverging from the coarse/medium trend rather than
converging toward it.

**A clean STATUS is not field convergence.** The pre-registration foresaw exactly
this risk: §3 and §11 record that the refined-mesh + relaxation-0.6 **decay rate
was never measured** (T4c was SIGTERM-stopped before its first checkpoint, so it
measured only the compute rate), and the `endTime` schedule was sized against
T4b's decay `ρ` with a disclosed thin margin. The C6.3 miss is that predicted
risk realised on the fine grid.

**What the successor must decide, not assume.** The pre-registration's registered
contingency was under-relaxation 0.6 → 0.5 (P5/P9). But the fine-level C6.3 miss
of ~76× the floor is far larger than a residual under-relaxation limit-cycle would
explain, and the medium level (same relaxation, same schedule shape) cleared C6.3
at 3.39e-06. The state-(b) successor must **diagnose** whether the fine grid needs
a substantially larger `endTime` (a still-decaying transient that simply had not
reached the floor at 64 000) **or** whether the case is physically unsteady at
Re = 23 000 on the fine mesh (a steady solver chasing an unsteady flow, where no
`endTime` clears C6.3) — the two have different repairs, and the frozen record
does not distinguish them. This is a measured finding for the successor, not a
terminal capability gap.

---

## 7. Cost — registered vs actual (rule 12)

Estimate-versus-actual lands as a row in `docs/COST_CALIBRATION.md`
(id `C-20260908T181918.303155Z-558dd067`) and is not duplicated in full here.
Summary:

| | predicted (prereg §9) | actual (STATUS `core_min`) | ratio |
| --- | ---: | ---: | ---: |
| coarse | 22.1 | 21.667 | 0.980 |
| medium | 898.6 | 206.100 | 0.229 |
| fine | 5 411.6 | 1 200.233 | 0.222 |
| **rung** | **6 332.3** (cap 12 669) | **1 428.0** | **0.226** |

Dollars **derived, not measured** (rule 12; the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5), at $0.0513/core-h, reported-by-owner: predicted
$5.41, actual **$1.221** (23.80 core-h). **Waste 0.000 core-min** — all three
legs `note=clean`, `capped=no`.

**Disclosure on the 3 600-s stall figure.** The fine leg ran **72 014 wall s
(≈20.0 h)** at `ranks = 1`, which exceeds the charter §2 3 600-s stall figure.
It is **not** a stall: it reached `endTime` cleanly with `ExecutionTime` count ==
64 000 and passed the strict completion rule — a scheduled long single-tenant
solve, productive compute, not a hung row. Gross == cleaned; the long fine leg is
disclosed rather than cleaned out.

**Attribution: favourable misprediction (over-estimate), not waste, not a crash.**
The coarse leg predicted accurately (0.980) because its rate basis came from the
T4c coarse **completion**. The medium/fine legs came in at ~0.22× because the T4d
caps were re-sized from T4c per-cell rates (medium 2.60e-05, fine 3.67e-05
core-s/cell-it) **measured on SIGTERM-truncated T4c legs during a contended
window**; the true single-tenant rates measured here (medium ~5.96e-06, fine
~8.14e-06 core-s/cell-it) are **~4.4–4.5× lower**. **Calibration lesson:** cap
re-sizing must use per-cell rates from **completed single-tenant** runs; rates
from SIGTERM-truncated legs over-price by ~4.5×. Note the **sign flip** of the
estimate error across the chain: T4c *under*-provisioned (its legs were
SIGTERM'd), and T4d — correcting from those inflated truncated rates —
*over*-provisioned by ~4.5×.

---

## 8. Disclosures

**Cosmetic (frozen file, not edited — rule 6).** `analyse_t4d.py`'s DONE-gate
refusal message names *"mark_done_t4b.py decides"* — a stale string carried over
from the T4b→T4c→T4d rename lineage. The actual completion instrument for this
rung is **`mark_done_t4d.py`** (blob `8a281d72`), and the comparator only checks
the `DONE.<case>` markers on disk — it never invokes `mark_done` — so the wrong
name in the message cannot affect any grade. It is flagged here for a future
dated addendum to the frozen file; it is **not** edited by this record.

**No Nu row is graded** (BLOCKED, T4 §2.1); a PASS on G1–G3 would have been a
joint code-plus-closure statement. No eigenspace band is armed.

**SUBMISSIONS PARKED** (rule 7). Nothing in this record authorises a send.

---

## 9. Deliverables and paths

| what | where |
| --- | --- |
| pre-registration (frozen, commit `eae8e96c`) | `/home/ubuntu/Certonomous/docs/campaigns/T-family/T4d_PREREGISTRATION.md` |
| this file | `/home/ubuntu/Certonomous/docs/campaigns/T-family/T4d_RESULTS.md` |
| frozen comparator (blob `d616754e`) | `/home/ubuntu/Certonomous/verification/runs/T-family/T4d_runs/analyse_t4d.py` |
| completion instrument (blob `8a281d72`) | `/home/ubuntu/Certonomous/verification/runs/T-family/T4d_runs/mark_done_t4d.py` |
| machine-readable grade JSON | `/home/ubuntu/Certonomous/verification/runs/T-family/T4d_runs/t4d_grade.json` |
| completion markers | `/home/ubuntu/Certonomous/verification/runs/T-family/T4d_runs/DONE.T4d_IJ_{c,m,f}` |
| per-level STATUS | `/home/ubuntu/Certonomous/verification/runs/T-family/T4d_runs/STATUS.T4d_IJ_{c,m,f}` |
| cost calibration row | `docs/COST_CALIBRATION.md` id `C-20260908T181918.303155Z-558dd067` |

*Graded by the T4d grade lane, 2026-09-08. Not committed by this lane: the
heat-transfer supervisor commits `T4d_RESULTS.md` and the `COST_CALIBRATION.md`
row under the private-index protocol (rule 10).*
