# RUNG 2 pre-registration — NASA CRM / DPW5 — the `R2-M0` COMPRESSIBLE ADMISSION PROBE, and the THREE blockers that mean the DRAG GATE IS NOT REGISTERED HERE

**Team: cfd. Case id `RUNG2-CRM-M0`. v1.1, drafted 2026-09-04 by a `lab-lane` for the cfd supervisor.
v1.1 carries Amendment 1 (§13), landed PRE-COMPUTE after check 4 FAILED on v1.0.**

> # ⚠ DRAFT — NOT AUTHORISED TO LAUNCH. CHECK 4 FAILED ON v1.0 AND HAS NOT BEEN RE-PERFORMED.
>
> **NOTHING LAUNCHES AGAINST THIS FILE. NO COMPUTE HAS BEEN RUN UNDER IT.**
>
> **Check 4 was performed on v1.0 by the cfd supervisor and it FAILED**: §8 asserted a frozen grading
> path and named a comparator that did not exist and was not in git, so there was no committed blob
> to hash against. **§13 records that failure, in full, and its repair.** The repair does not make the
> check pass — **only the supervisor re-performing check 4 can do that**, and it has not been done.
>
> The rule-2 freeze — pre-registration **committed** before compute — is the cfd supervisor's
> **non-delegable personal check** (`SUPERVISION_CHARTER.md` §3). This lane does not take it and is
> not authorised to launch any solve. The drafting lane spent **zero solver core-minutes.**
>
> Registered run root verified **ABSENT** under a live planted control, twice: at drafting (§1.4) and
> again at amendment by the comparator's own guard (§13) — `verification/runs/RUNG2_CRM_runs/`.
>
> **AND READ §4 AND §4b BEFORE RULING ON §6.** §4 is a standards question this team cannot clear by
> measurement, amendment or spending, and it is **Sanaa's**. **§4b needs nobody's ruling and survives
> any ruling on §4** — Rung 2's drag gate is `BLOCKED` on three grounds, not one.

---

## 0. WHAT THIS DOCUMENT IS, AND WHAT IT DELIBERATELY IS NOT

**It IS** a pre-registration for `R2-M0` — a bounded, cheap, single-grid **feasibility probe** that
settles whether this lab's steady compressible solver can take a step on the DPW5 committee grid at
the workshop's design regime. Sanaa's own standing order requires it: *"feasibility probe before
family"*, *"Freeze criteria before the first solve, as always."*

**It is NOT** a pre-registration of Rung 2's deliverable. Sanaa's Rung 2 (a) is
*"single cruise point (the workshop's design condition), drag and moment against the workshop's data
envelope — we grade against the scatter band of participants, honestly stated."*
**THAT GATE IS NOT REGISTERED IN THIS FILE AND CANNOT HONESTLY BE REGISTERED TODAY.** §10 says why,
in THREE independent measured reasons, and none of them is compute.

**No gate in §6 depends on another team's state.** Every threshold below is read from an artifact
this team owns or from a file on this box. That property was checked deliberately, because a gate
whose pass condition sits in another family's hands is not a gate this campaign can pass.

---

## 1. CENSUS — WHAT EXISTS, WHAT DOES NOT, AND WHAT WAS PLANT-VERIFIED

### 1.1 The rung, its authority and its position

`etc/sessions/2026-09-03T0030Z_sanaa_industrial_benchmark_ladder.md` — Sanaa's standing order,
verbatim in that file. Rung 2 is *"NASA CRM, Drag Prediction Workshop configuration ... Use the
workshop's committee grid family — the grid-triple prerequisite comes free."* Rung 3 (HLPW) is
explicitly *"Do not schedule before CRM is held."* Budget authority is the $1,000 ladder envelope of
`etc/sessions/2026-09-03T1800Z_sanaa_compute_envelope.md`, ledgered at
`docs/campaigns/IBL-industrial-benchmark-ladder/IBL_COMPUTE_ENVELOPE_LEDGER.md`.

### 1.2 WHAT EXISTS

| artifact | class | path | state |
|---|---|---|---|
| DPW5 `unstructured_grids.REV01` level **L1.T**, hex / prism / hybrid | **case input (grid)** | `/home/ubuntu/certonomous-runs/dpw5-committee-probe/grid/` | on disk, 153 MB, three files, sha256 pinned in `cases/committee-grids/COMMITTEE_GRID_NUMERICS.md` §1 |
| `dpw5_L1T.mapbc` | case input | same directory | present; transcribed from the grid store's own `readme` and **checked**, not trusted (`inspect_ugrid.py`) |
| The mesh-import lane | case definition (code) | `cases/committee-grids/{ugrid_to_foam.py, foam_to_ugrid.py, grade_rung0b.py}` | Rung 0b graded **`PASS`** |
| Rung 0b import verification of all three DPW5 grids | **run output + grading record** | `verification/runs/RUNG0b_MESH_IMPORT_runs/`, `verification/campaign/RUNG0b_MESH_IMPORT_PREREGISTRATION.md` | **`PASS`**, record `33b77af5`, 4.4333 core-min, no waste |
| DPW5 hex birth certificate | run output | `verification/runs/RUNG0b_MESH_IMPORT_runs/DPW5_L1T_hex/.../birth_certificate.json` | `cells 638976`, `max_non_orthogonality 89.7134`, `severe_non_ortho_faces 11506`, `max_skewness 14.0594`, `max_aspect_ratio 14426.8`, `points_sha256 870e6c6f…d51f7fd`, `created_at 2026-09-03T19:40:49Z` |
| The 2026-08-01 committee-grid numerics probe | **run output + prose record** | `/home/ubuntu/certonomous-runs/dpw5-committee-probe/` (5.8 GB, ~40 run dirs, `logs/`, `measurements.jsonl`); write-up `cases/committee-grids/COMMITTEE_GRID_NUMERICS.md` | ran; **never graded as a rung**; carries no pre-registration and no verdict from the fixed vocabulary |
| DPW/CRM scoping | prose | `docs/DPW-CRM-SCOPING.md` (2026-07-27), `verification/campaign/DPW8_AEPW4_SCOPING.md` | scoping only, no gates |
| CRM at M = 0.850 on a **self-generated 579,072-cell WING** | run output (dafoam territory) | ladder A6, `cases/dafoam/ladder-a/A6_crm_wingbody.md`, `/home/ubuntu/certonomous-runs/A6-crm-wing` | converged `CD 0.020901 / CL 0.500015`. **Not gradeable against DPW: different geometry (wing, not wing-body), lab-generated mesh, not a committee grid.** Cited, never claimed. |

### 1.3 WHAT DOES NOT EXIST

| absent artifact | class |
|---|---|
| any `verification/campaign/RUNG2*` file | **pre-registration** |
| any `verification/runs/RUNG2*` directory | **run output** |
| any queue row naming Rung 2, CRM or a DPW5 **solve**, in `verification/queue/cfd/`, `.../launched/` or `.../held/` | queue entry |
| any `RUNG2` spend row in `IBL_COMPUTE_ENVELOPE_LEDGER.md` (its only `RUNG2` string is the schema line *"`RUNG0` … `RUNG3`; branch label"*) or in `docs/COST_CALIBRATION.md` (`RUNG0`×17, `RUNG0b`×12, `RUNG1`×5, `RUNG2`×0) | cost record |
| **DPW5 levels L2.C and L3.M in any topology** — only L1.T is on this box | case input |
| any grading record for the 2026-08-01 committee probe | grading record |

### 1.4 THE PLANT — the absences in §1.3 are evidence, not silence

Rule 3. Each reader was shown able to see a hit at the exact path it searched, then shown the
absence again after the probe was removed. Run 2026-09-04T21:2xZ, one shell invocation:

| reader (exact searched path) | before | probe planted | after removal | residue check |
|---|---|---|---|---|
| `ls verification/campaign/ \| grep -c '^RUNG2'` | **0** | **1** | **0** | file gone |
| `ls -d verification/runs/RUNG2* \| wc -l` | **0** | **1** | **0** | directory gone |
| `ls verification/queue/cfd{,/launched,/held} \| grep -ci 'RUNG2\|CRM\|DPW5'` | **0** | **1** | **0** | file gone |

All three readers moved 0 → 1 → 0. **The three absences above are measured, not assumed.**

### 1.5 The `git status` queue deletions were inspected, not reverted

`verification/queue/` currently shows deleted rows under `ansys-verification/`, `closure/` and one
`cfd/F28G_L1_dp1000_U20.json`. **None of them is a Rung 2 or CRM row** (§1.4's third reader covers the
cfd queue and reads 0). A deleted queue row in this lab is as often a *launch* as a withdrawal, so
none was touched. They are named here for the supervisor and left exactly as found.

---

## 2. HAS RUNG 2 EVER RUN?

**Rung 2, as a registered rung of Sanaa's ladder, has NEVER been launched.** This is not an inference
from a missing marker file. It rests on four independent absences, three of them plant-verified
(§1.4): no pre-registration, no run root, no queue row, and **no spend row in either cost ledger** —
and a run that happened without spending core-minutes is not a run.

**What HAS run on this geometry, and must not be mistaken for Rung 2:**

1. **The 2026-08-01 committee-grid numerics probe** genuinely executed on the real DPW5 CRM wing-body
   committee grids: ~40 solver runs, 5.8 GB of artifacts, `measurements.jsonl` with per-run wall time
   and peak RSS. **It was a pre-ladder feasibility probe with its own `PREDICTIONS.md`; it carries no
   pre-registration under `VERIFICATION_CHARTER.md` §2b and no verdict from the fixed vocabulary. It
   is evidence, and it is not a graded rung.** It is the source of every measured number in §3.
2. **Ladder A6's CRM wing primal** (dafoam territory) — converged, but a different geometry on a
   lab-generated mesh. Not a DPW result.

**What I cannot tell.** Nothing material. The one place I stopped short: I did not attempt to
establish whether any of the ~40 out-of-git probe directories was *re-run* after 2026-08-01, because
`certonomous-runs/` is read-only to me and mtimes there have been rewritten by later sweeps. It does
not change §2's answer — none of them was ever a Rung 2 launch under a registration.

---

## 3. BLOCKER 1 — THE COMPRESSIBLE PATH SIGFPEs AT ITERATION 2 ON THE VERY GRID THAT SOLVES

Measured, on this box, on the DPW5 L1.T **hex** grid — the one committee grid that runs 200 clean
incompressible iterations with settling forces.

| arm | solver | exit | wall s (14 ranks) | died at |
|---|---|---|---|---|
| `hex_base_incompressible_a2.11` | `simpleFoam` | **0** | 218.98 | — ran 200 of 200 |
| `hex_base_compressible_a2.11` | `rhoSimpleFoam` | **136** | 4.02 | `Time = 2`, after `e` |
| `hex_trans_compressible_a2.11` (`transonic yes`) | `rhoSimpleFoam` | **136** | 5.78 | `Time = 2` |
| `hex_transu1_compressible_a2.11` | `rhoSimpleFoam` | **136** | 6.59 | `Time = 1` |

Source: `/home/ubuntu/certonomous-runs/dpw5-committee-probe/measurements.jsonl` and
`logs/hex_*_compressible_a2.11_solve.log`.

**What the log actually shows, read rather than summarised.** `Time = 1` is *clean*: `Ux/Uy/Uz` and
`e` each solve to a falling residual, GAMG takes 147 iterations on `p`, and the time-step continuity
error is **2.5642813e-07**. Nothing has diverged. At `Time = 2` the `U` and `e` solves complete
normally and the run then takes **signal 8 (SIGFPE)** with `libm` beneath
`libfluidThermophysicalModels.so` beneath `rhoSimpleFoam` on the stack — i.e. inside the thermo
evaluation that follows the energy solve, not inside the linear algebra.

**This is a configuration defect, not a mesh-quality one, and that was established by controlled
comparison rather than asserted**: the same abort reproduces on the hex grid, whose severe-face
fraction is 0.59 %, and the hex grid runs 200 incompressible iterations on the identical `polyMesh`.
`cases/committee-grids/COMMITTEE_GRID_NUMERICS.md` §5.5 records it as **unresolved**, and it is not
carried in `docs/NUMERICS_KNOWLEDGE.md` or `docs/DOCKET.md` — a gap this lane names rather than fixes.

**What the previous lane did NOT try, and what makes this probe cheap and pointed.** Its two
compressible variants moved only `transonic`. Read from the case on disk
(`run_hex_base_compressible_a2.11/`): `hePsiThermo` + `perfectGas` + **`sensibleInternalEnergy`** +
`sutherland` transport, with **`rhoMin 0.1; rhoMax 10.0`** as the *only* bound and **no `pMin`,
`pMax` or `TMin`**. Sutherland evaluates `sqrt(T)`; `hePsiThermo` inverts `e → T`. A `T` excursion
through zero at the second energy solve produces exactly this stack. The initial field is **uniform
freestream everywhere**, 294.8 m/s against no-slip walls on a `y+`-1 grid.

**A separate defect found while reading, and it disqualifies those four runs as CRM results
regardless of the abort:** `system/controlDict` sets **`Aref 1.0`** and `lRef 7.005320` — not the
CRM's reference area and MAC. The `Time = 1` force write is `Cd: 135.94, Cl: 192.09, CmYaw: -2650.5`.
**Those arms were a solver port, never a DPW5 CRM case.** No number from them is a drag figure and
none is used as one here.

**Two candidate causes are named so the probe can discriminate them, and neither is asserted:**
(i) an unbounded `T`/`p` in a thermo without `TMin`/`pMin`; (ii) an energy-form/start-condition
mismatch (`sensibleInternalEnergy` + uniform-freestream start at M ≈ 0.85). §5's arms separate them.

---

## 4. BLOCKER 2 — THE COMMITTEE GRID FAILS THIS LAB'S OWN HARD MESH GATES, AND THE ONLY EXEMPTION ON RECORD DOES NOT REACH A PHYSICS GATE. **THIS IS SANAA'S CALL, NOT THIS TEAM'S.**

This is the more important of the two and it cannot be cleared by spending anything.

| `MESH_STANDARD.md` gate | threshold | DPW5 L1.T **hex**, measured by this lab 2026-09-03 | margin |
|---|---|---|---|
| §3.1 max non-orthogonality | **hard ≤ 70°** | **89.7134°** | fails by 19.7° |
| §3.2 max skewness (boundary faces included) | **hard ≤ 4** | **14.0594** | fails by 3.5× |
| §3.3 aspect ratio | advisory ≥ 1000 | 14,426.8 | flagged, never a lone rejection |

Source: `verification/runs/RUNG0b_MESH_IMPORT_runs/DPW5_L1T_hex/.../birth_certificate.json`. The
prism and hybrid families are worse and do not solve at all.

**Rung 0b's `PASS` does not close this, and the pre-registration says so on its own face.** Its
quality gate `R0-G3` is headed *"REPORTED. NOT GATED. THIS GATE CANNOT FAIL ON A QUALITY VALUE"* — it
fails only on a **missing** number. So the DPW5 grid is **import-verified and has never been shown
admissible under §3.1/§3.2**, which it measurably is not.

**§3.1's own action clause:** *"above 70, no validated force from this mesh; the numerical channel
carries the breach and the fidelity chip is capped."* §3.2: *"above 4, trust is capped … the run may
proceed for ranking purposes only."* Rung 2's deliverable **is** a validated force.

**The one exemption on record does not reach it.** Ruling R12 (2026-08-07,
`docs/charters/SUPERVISOR_RULINGS.md`, pointed to from `MESH_STANDARD.md` §3.1) lets a reference
community's own canonical verification grid carry a band above the gate — **"for MODEL-FORM BANDING
ONLY"**. Its second mandatory condition, read from the ruling itself and not from the pointer, is
verbatim: **"physics gates and credential verdicts still require compliant meshes — this exemption
never travels to them."**

**So Sanaa's standing order and this lab's mesh standard are in direct tension, and the tension is
inside her own instruction.** She wrote *"Use the workshop's committee grid family"*; the standard
says a grid of that quality cannot carry a validated force or a credential verdict.
**Retiring or widening a standard or a gate threshold is reserved to Sanaa** (CLAUDE.md,
FIRST-ACTION RULE). This lane does not propose a reading. It states the conflict and stops.

**Until that is ruled, Rung 2's drag gate is `BLOCKED` — not `PENDING`.** `PENDING` would mean "not
yet run". This is "cannot be graded as registered."

---

## 4b. BLOCKER 3 — THERE IS NO REFINEMENT TRIPLE ON THIS BOX, SO RULE 5 CANNOT BE APPLIED AT ALL. **THIS ONE NEEDS NOBODY'S RULING AND SURVIVES ANY RULING ON §4.**

Recorded as an **independent** blocker, on the cfd supervisor's instruction of 2026-09-04, precisely
because **if Sanaa rules the §4 mesh-quality tension in this lab's favour, this blocker still
stands** — and she should know that before she rules, not after.

It is not a judgement. It is a fact about what is on this box:

- **Only level L1.T is here.** Plant-verified in §1.3/§1.4. L2.C (2.16 M hex) and L3.M (5.11 M hex)
  are published by the workshop and, by this lab's own measured memory law, would fit — but they are
  **not downloaded, never converted, never `checkMesh`'d.**
- **L1.T's hex, prism and hybrid files are THREE TOPOLOGIES AT ONE REFINEMENT LEVEL, not a
  refinement triple.** They share one 660,177-node point distribution; only the element
  decomposition differs. There is no refinement ratio between them and no `h` to extrapolate in.
- **Two of those three are measured non-solvable** on this lab's numerics (prism diverges at
  iteration 143; hybrid at 11), so even a topology comparison has one usable member.

**Consequence, stated in the fixed vocabulary.** Rule 5 gates on a grid triple: a row whose triple is
not `CONVERGING` is `NOT A RESULT` whatever its value. **A triple that does not exist cannot be
`CONVERGING`, so a GCI-backed drag verdict is unavailable today regardless of §4's outcome.** Any
drag number produced from L1.T alone would be a single-level value with no Richardson extrapolation
and no GCI, and quoting a GCI from three topologies at one level would be quoting a GCI where the
three values are not a refinement sequence at all.

**Sanaa's order says the grid triple "comes free" from the committee family. On this box, today, it
does not.** It is purchasable — three consecutive hex levels are within reach — but it has not been
purchased, and nothing in this pre-registration assumes it has.

---

## 5. WHAT IS REGISTERED HERE: `R2-M0`, THE COMPRESSIBLE ADMISSION PROBE

**One grid. One geometry. Five arms. No drag claim of any kind.**

**Grid, pinned:** DPW5 L1.T **hex**, 638,976 cells, `points_sha256`
`870e6c6fceab6dbeea0d6494793fcbb7dd7f41c8e92056814c5398938d51f7fd`, imported by the Rung-0b-`PASS`ed
lane. `/home/ubuntu/certonomous-runs/` is read-only: the probe **copies** the case, never writes there.

**Registered run root (ABSENT at drafting, plant-verified §1.4):**
`verification/runs/RUNG2_CRM_runs/M0_compressible_admission/{A0,A1,A2,A3,A4}/`

**Regime:** the arms hold the August freestream fixed (`T∞ = 300 K`, `p∞ = 101325 Pa`,
`U∞ = 294.8 m/s`, α = 2.11°, `hePsiThermo`/`perfectGas`/`sutherland`, k-ω SST, 14 ranks) so that A0
is a *reproduction* of a known outcome. **The freestream is NOT the DPW5 design condition and is not
registered as one.** Setting the DPW condition is Rung 2 (a)'s business and Rung 2 (a) is not
registered (§10).

| arm | the ONE thing moved | what it is a bet on |
|---|---|---|
| **A0** | nothing — dictionaries byte-identical to `run_hex_base_compressible_a2.11`, md5 printed for both | **the reproduction control.** If A0 does not abort, §3's premise is gone and the whole probe is `NOT A RESULT`. |
| **A1** | add `pMin`/`pMax` and `TMin 100`/`TMax 1000` bounds; nothing else | cause (i): an unbounded thermo inversion |
| **A2** | `energy sensibleEnthalpy` + `transonic yes` + A1's bounds | cause (ii): energy form at M ≈ 0.85 |
| **A3** | warm start — `U`, `k`, `omega` mapped from the archived converged incompressible field `run_hex_base_incompressible_a2.11/processor*/200`, `T`/`p` uniform; A1's bounds | cause (ii): the uniform-freestream start, not the equations |
| **A4** | relaxation crawl `p 0.1 / U 0.3 / e 0.3` + A1's bounds | whether the amplification is containable at all |

**Every arm prints `min/max` of `T`, `p` and `rho` every iteration** (`#includeFunc minMaxComponents`),
so the proximate cause is **read from a field bound**, never inferred from a stack trace. An arm that
aborts without having printed those bounds is `NOT A RESULT` for `R2-G2`.

**Iteration budget: 50 per arm.** Not an invented bar — the abort under investigation happens at
iteration 2, and the incompressible reference on this grid is flat by iteration 50. 50 is enough to
distinguish "took a step" from "cannot start" and is not enough to claim a solve. **No arm's output is
a converged solve and none may be quoted as one.**

---

## 6. THE GATES — every one carries a threshold, a cap and a label

| id | gate | **threshold (pre-registered)** | **cap (core-min)** | **label if met** | **label if not** |
|---|---|---|---|---|---|
| **R2-G0** | **Reproduction control.** A0 reproduces the known abort. | A0 exits **136** at `Time ≤ 2` with `libfluidThermophysicalModels.so` present in its own stack trace | **8.0** | proceed to G1 | **`NOT A RESULT` for the whole probe** — §3's premise is not reproducible, and no conclusion is drawn from A1–A4 |
| **R2-G1** | **Admission.** At least one of A1–A4 takes 50 steps. | ≥ 1 arm reaches **`Time = 50`** with **`rc = 0`**, **no signal 8**, and no `NaN`/`inf` token anywhere in its log | **160.0** | **`PASS`** — the compressible path is admissible on a committee hex grid, and Blocker 1 is cleared | **`GATE FAIL`** — all four remedies exhausted; the defect is deeper than configuration and Rung 2 (a) stays `BLOCKED` on Blocker 1 as well as Blocker 2 |
| **R2-G2** | **Mechanism named by measurement.** | Every arm has a per-iteration `min/max` line for `T`, `p` and `rho` in its log up to its last completed iteration, and the failing arms' last such line is **quoted in the results record** | **0.0** (inside G0/G1's runs) | **`PASS`** | **`NOT A RESULT`** for the mechanism claim — the outcome of G0/G1 stands, but no cause may be named |
| **R2-G3** | **Planted control on the reader** (rule 3). **ALREADY MEASURED — see §13.** | The log reader reports **"abort at Time = 2, signal 8"** on the archived 2026-08-01 abort log and **"no abort"** on the archived 2026-08-01 **clean** log — two real artifacts, same grid, same box, same day — in the same invocation, plus six further controls | **2.0** (spent: **0.0**, no solve) | **`PASS`** — measured 2026-09-04, **8/8 controls fired** | **`NOT A RESULT`** for G0 and G1 — a reader not shown able to see both outcomes has not measured either |
| **R2-G4** | *(drag against the DPW participant scatter band)* | — | — | — | **NOT REGISTERED. See §10.** |

**Verdict composition.** The probe's verdict is the **worst** of G0–G3, in the order stated.
`R2-G3` and `R2-G0` are the two that can turn a `PASS` or a `GATE FAIL` into `NOT A RESULT`; neither
can turn a `NOT A RESULT` back into anything (rule 5's direction, applied here by analogy and stated
so nobody has to infer it).

**Total registered cap: 170.0 core-min.** An overrun **stops the run**; it does not get a new
budget (rule 12). No cap here is reset by a retry: a second attempt of any arm spends from the same
170.0.

---

## 7. COST — registered before launch, with its basis named

**Basis, MEASURED on this grid at 14 ranks on this box, not estimated:**

- incompressible: 218.98 wall s / 200 iterations = **1.095 s/iteration** → 0.2555 core-min/iteration
- compressible: 4.02 wall s to the abort in `Time = 2` ⇒ ≈ **2.6 s/iteration**, a **≈ 2.4×** factor
  over incompressible for the energy equation plus thermo
- ⇒ **0.626 core-min/iteration** at 14 ranks, 638,976 cells

Source: `/home/ubuntu/certonomous-runs/dpw5-committee-probe/measurements.jsonl`
(`hex_base_incompressible_a2.11`, `hex_base_compressible_a2.11`).

| line item | derivation | core-min |
|---|---|---|
| A0, reproduction control, aborts ≈ iteration 2 | 4.02 s × 14 / 60 | **0.94** |
| Two arms survive to 50 iterations | 2 × 50 × 0.626 | **62.6** |
| Two arms abort early | 2 × 0.94 | **1.88** |
| Case assembly, `decomposePar` ×5, field mapping for A3 | `logs/hex_base_compressible_a2.11_decompose.log` records **"Finished decomposition in 1.5 s"**; allow 6 wall s per arm serial including I/O, plus ~30 s for A3's field map | **1.0** |
| Reader + planted control (G3), serial | — | **0.5** |
| **REGISTERED ESTIMATE** | 0.94 + 62.6 + 1.88 + 1.0 + 0.5 | **66.9 core-min** |
| **CAP** | **≈ 2.5× the estimate, set by this team, not by Sanaa** | **170.0 core-min** |

**Dollars are DERIVED, NOT MEASURED — the box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5, rule 12). At the on-box `c7a.4xlarge` rate of **$0.0513/core-h**,
`cost_basis: on-box-owner-stated`:

- estimate 66.9 core-min = 1.1150 core-h → **$0.0572 DERIVED**
- cap 170.0 core-min = 2.8333 core-h → **$0.1453 DERIVED**

**No escalation trigger is approached.** The single-run escalation line is $150 = 175,439 core-min;
the cap here is **0.097 %** of it. The envelope stands at $999.9863 remaining
(`IBL_COMPUTE_ENVELOPE_LEDGER.md` row `E-20260903T194956…`). **This is an on-box run: no rented node,
no `BLOCKED-ON-PRICE`, no unpriced backlog.**

**Estimate-versus-actual calibration is mandatory at completion** (rule 12): a row in
`docs/COST_CALIBRATION.md` **and** a row in the IBL envelope ledger, stating the ratio
actual/predicted, with waste named separately and never absorbed into the ratio.

---

## 8. COMPLETION AND REFUSAL

An arm counts as **completed** only if all of: `rc = 0`; an `End` line; last time == `endTime`;
`ExecutionTime` count == `endTime`; fields present at `endTime`; and **every field at `endTime` newer
than that arm's own `0/T`** — the age guard. An arm that fails any clause is **not done** and its
number is not read. The launcher **refuses** a case directory in which a time directory already
exists. An arm that aborts by design (A0) is recorded by its **exit code and stack**, never by a
field, and never counted as completed.

> ~~**The grading path is fixed at this document's commit.** The comparator
> `verification/runs/RUNG2_CRM_runs/M0_compressible_admission/grade_r2_m0.py` is hashed against its
> committed blob at grading time and the run refuses on mismatch
> (`scripts/check_comparator_freeze.py`). **It does not exist yet and is not authorised to be written
> until §6 is frozen by the supervisor.**~~
>
> **STRUCK BY AMENDMENT 1 (§13), 2026-09-04, PRE-COMPUTE.** The struck text asserted a freeze it did
> not have: it named a comparator that did not exist and was not in git, so there was no committed
> blob to hash against and the stated refusal-on-mismatch could not fire. Original preserved above,
> never rewritten.

**The grading path is fixed at this document's commit.** The comparator is
**`cases/committee-grids/grade_r2_m0.py`** — beside the case, where `grade_rung0b.py` already sits
and is committed — **not** inside the run root. It **EXISTS AND IS COMMITTED** (§13). It is hashed
against its committed blob at grading time and the run refuses on mismatch
(`scripts/check_comparator_freeze.py`).

**Why the comparator may not live inside the run root.** Two rules collide there and only this
placement satisfies both: run outputs belong under `verification/runs/` and executables do not; and
rule 4's guard **refuses** a case whose run root already exists, while the plant-verified-absent
discipline requires that root to be absent before launch. A comparator that must be committed before
launch, but that lives inside the run root, forces the root to exist before launch. **Those cannot
both hold.** Ruled by the cfd supervisor, 2026-09-04.

---

## 9. WHAT WILL NOT BE CHECKED, AND IS SAID HERE RATHER THAN DISCOVERED LATER

- **No drag, lift or moment coefficient is produced, read, or reported by this probe.** `Aref`/`lRef`
  are left at the August values precisely so that nobody can mistake a force write for a result.
- **No grid convergence.** One level. `L2.C` and `L3.M` are not on this box (§1.3).
- **No claim about the prism or hybrid families**, which are measured non-solvable and are not run.
- **No claim that a `PASS` on `R2-G1` makes Rung 2 (a) gradeable.** It clears Blocker 1 only.
  **Blocker 2 (§4) is untouched by anything in this file.**
- **No transferability claim to HLPW6 or Rung 3.**

---

## 10. WHY THE DRAG GATE — SANAA'S ACTUAL RUNG 2 — IS **NOT** REGISTERED HERE

Three measured reasons, stated plainly rather than worked around:

1. **§4. The grid fails this lab's own hard mesh gates by 19.7° and 3.5×, and R12's exemption
   explicitly does not reach a physics gate or a credential verdict.** A drag verdict registered
   against this grid today would be a gate this campaign **cannot pass as the standards are
   written**. That is exactly the class of gate a pre-registration must not carry.
2. **§3. There is no compressible solve.** A drag gate whose measurement channel aborts at iteration
   2 has no measurement channel.
3. **§4b. The grid triple does not exist and does not "come free."** Rule 5 gates on a triple, and a
   triple that does not exist cannot be `CONVERGING`. **This reason is INDEPENDENT of reasons 1 and
   2: it survives any ruling Sanaa makes on §4, and it is not cleared by fixing §3.** Registering a
   triple gate today would register a triple that does not exist.

---

## 11. THE FALSIFIABLE PROPOSITION, AND THE ARTIFACT THAT WOULD REFUTE IT

**P (what `R2-M0` settles, and it is not settled today):**

> *This lab's steady compressible RANS solver, on the DPW5 L1.T committee hex grid at
> `points_sha256 870e6c6f…d51f7fd` and the August freestream, can complete 50 outer iterations
> without the `libfluidThermophysicalModels.so` floating-point abort, under at least one of four
> named single-variable remedies (thermo bounds; enthalpy + transonic; warm start; relaxation crawl).*

**Refuted by:** `verification/runs/RUNG2_CRM_runs/M0_compressible_admission/A{1,2,3,4}/log.solve`
showing all four arms at exit 136 / signal 8 before `Time = 50`, with A0 having reproduced the
baseline abort (`R2-G0` met). That is a `GATE FAIL` on `R2-G1` and it is a real, reportable finding:
it would say the defect is not a configuration defect and would move the question from a dictionary
to the discretisation.

**Confirmed by:** any one of those four logs reaching `Time = 50`, `rc = 0`, no signal 8, no `NaN`,
with the `min/max T` line present throughout.

**What P is worth, honestly.** P is a **capability** proposition, not a physics one. It settles
nothing about drag, about CRM, or about this lab's agreement with any workshop. Its whole value is
that it is the **cheapest** thing that can move a `BLOCKED` off Blocker 1 — 66.9 core-min against a
rung Sanaa priced in *"tens of core-hours per fine-grid solve"* — and that its answer is informative
in **both** directions.

**And it is worth it on its own account, independently of Rung 2.** The cfd supervisor ruled so on
2026-09-04: a `rhoSimpleFoam` SIGFPE inside `libfluidThermophysicalModels.so` at `Time = 2`, with
`Time = 1` clean at continuity `2.5642813e-07`, is a **solver-toolchain defect in cfd territory that
blocks compressible work on imported grids generally**, and it is carried in neither
`docs/NUMERICS_KNOWLEDGE.md` nor `docs/DOCKET.md`. **Authorised in principle, NOT authorised to
launch.** If Sanaa's §4 ruling goes against committee grids, the probe's Rung-2 justification
disappears but its toolchain justification does not — the supervisor decides then whether it still
buys $0.145 derived.

---

## 12. THE RECOMMENDATION THIS LANE MAKES

1. **Rung 2 (a), the drag-band verdict: `BLOCKED`, on THREE grounds, not two.** §3 (no measurement
   channel), §4 (the mesh-standard conflict — **Sanaa's alone to rule**), and §4b (**no refinement
   triple exists on this box, so rule 5 cannot be applied at all**). **§4b needs nobody's ruling and
   survives any ruling on §4**, which is exactly why Sanaa must see it before she rules on §4.
   **Escalate §4 and §4b together.** No compute clears either.
2. **`R2-M0`: authorised in principle by the cfd supervisor, NOT authorised to launch.** Check 4 has
   been performed once and **FAILED** (§13); it must be redone against this amended document. The
   supervisor's remaining preconditions are met: the comparator exists at the ruled path, is
   committed, and **R2-G3 passes 8/8 against the real archived logs with no solve.**
3. **Do not download L2.C or L3.M, and do not start on HLPW/Rung 3, until §4 and §4b are ruled.**
   Sanaa's own order already forbids Rung 3 before CRM is held; §4 and §4b together decide whether
   CRM can be held at all.

---

## 13. AMENDMENT 1 — 2026-09-04, **PRE-COMPUTE**. THE CHECK-4 FAILURE AND ITS REPAIR

**Status of this amendment under rule 2.** This document is a **DRAFT**: it is not frozen, and **no
compute has been run under it**. Before first compute, amendments are legal **and must state the
condition and how it was checked.** The condition and its check are stated below. No gate, threshold,
cap or label is altered by this amendment except where the entry did not previously exist; the
struck text is preserved verbatim in §8 and is not rewritten.

**THE CONDITION, AND HOW IT WAS CHECKED.** *Condition:* the registered run root
`verification/runs/RUNG2_CRM_runs` does not exist, and no compute has been run under this document.
*How checked:* the comparator's own `--guard-absent` mode was run against that exact path three
times in one invocation — **ABSENT (rc 0) → probe directory created at the exact registered path →
REFUSED (rc 2) → probe removed → ABSENT (rc 0)**, with a residue check confirming nothing was left
behind. The guard was therefore shown able to see the non-absence it denies.

### 13.1 What check 4 found, in the supervisor's words and not softened

The cfd supervisor performed check 4 on v1.0 and it **FAILED**. §8 stated *"The grading path is fixed
at this document's commit"* and named
`verification/runs/RUNG2_CRM_runs/M0_compressible_admission/grade_r2_m0.py`. **That file did not
exist and was not in git.** Both readers (`ls`, `git ls-files --error-unmatch`) were run against
`cases/committee-grids/grade_rung0b.py` as a control in the same invocation and both returned it, so
the absence was a reading and not a blindness.

**Rule 2 requires the frozen file be verified as the file that ran by hashing it against the
committed blob. There was no committed blob.** The document asserted a freeze it did not have — a
precondition stated and not satisfied. **A registration that names a grader which does not exist
cannot refuse on mismatch, because there is nothing to mismatch against.**

### 13.2 The three repairs

1. **The comparator moved out of the run root** and lives beside the case as
   `cases/committee-grids/grade_r2_m0.py`, next to the already-committed `grade_rung0b.py`. §8 now
   carries the reason: committing a grader inside the run root forces the root to exist before
   launch, which rule 4's guard refuses. Supervisor's ruling, 2026-09-04.
2. **The comparator was written and committed**, and **R2-G3 was run today against the real archived
   logs with no solve.**
3. **Blocker 3 was promoted to its own section (§4b)** as an independent blocker, because it
   survives any ruling on §4.

### 13.3 R2-G3, MEASURED 2026-09-04 — `PASS`, 8/8 controls fired, 0.000 solver core-min

Run as `python3 cases/committee-grids/grade_r2_m0.py --selftest`. The two controls the supervisor
required are C1 and C2, and they are **two real archived artifacts on the same grid, the same box and
the same day** — not a synthetic log:

| control | what it plants or reads | fired |
|---|---|---|
| **C0** | the `assert`-detector is planted (`assert True` → 1) and shown silent on clean source (→ 0), then reads this comparator (→ **0 `assert` statements**) | **PASS** |
| **C1** | the real archived **abort** log → **`ABORTED` at `Time = 2`**, `libfluidThermophysicalModels.so` seen (31×), SIGFPE seen (8×), no `End` | **PASS** |
| **C2** | the real archived **clean** log → **`COMPLETED`**, `Time = 200`, `ExecutionTime` count 200, `End` present, **0** SIGFPE, **0** thermo frames, **0** NaN/inf | **PASS** |
| **C3** | the abort signature planted **into** the clean log → classification **flips to `ABORTED`** | **PASS** |
| **C4** | a `nan` token planted → the R2-G1 scan fires; unplanted → silent | **PASS** |
| **C5** | the **setsid trap**: `rc = 0` beside a SIGFPE log is **REFUSED**; `rc = 0` beside a clean log is allowed | **PASS** |
| **C6** | the **age guard**: fields newer than `0/T` pass; `0/T` touched forward → **fail** | **PASS** |
| **C7** | the run-root guard refuses an existing root and permits an absent one | **PASS** |

**The selftest was shown able to FAIL, so its passes are evidence.** Two mutations of the comparator,
run from scratch copies, never from the committed file:

- **M1** — the abort control pointed at the clean log: **C1 and C5 report `FAIL`, rc = 2,
  `R2-G3: NOT A RESULT`.**
- **M2** — one `assert True` injected: **`REFUSED`, rc = 2**, naming the count.

**`python3` and `python3 -O` parity:** both exit **0** and their stdout is **byte-identical**
(`cmp` clean). `__pycache__` was cleared before the run so no stale bytecode could invert the
mutation controls.

**Cost of R2-G3: 0.000 solver core-min.** No solve, no MPI, no case directory. The registered 2.0
core-min cap for R2-G3 is therefore **unspent** and stays available.

### 13.4 What is still NOT done

- **Check 4 has not been re-performed against this amended document.** It is the cfd supervisor's
  personal, non-delegable check. **This file still authorises nothing.**
- The comparator's `--grade` path has **never been exercised on a real arm**, because no arm exists.
  Its completion clauses were exercised on a synthetic case directory with real mtimes (C6) — that is
  a control on the clause logic, **not** a demonstration that it grades a real OpenFOAM run
  correctly, and it is not offered as one.

---

---

## 14. THE LAUNCH WAS ATTEMPTED AND IS `BLOCKED`. 2026-09-04, **STILL PRE-COMPUTE — NOTHING RAN.**

**Check 4 was re-performed by the cfd supervisor on v1.1 and it PASSED.** The supervisor verified the
registration against its HEAD blob, verified `cases/committee-grids/grade_r2_m0.py` exists, is tracked
and hashes to `d7bd7260…`, verified §8's original text is struck-by-quote and not rewritten,
plant-verified the run root absent, and confirmed an idle box. **R2-M0 was authorised to launch under
seven conditions.** The lane then attempted the launch and it is `BLOCKED`, on two grounds.

**No gate, threshold, cap or label is altered by this section. It records an outcome, not a term.**

### 14.1 BLOCKER A — a LIVE PERMISSION-SYSTEM DENIAL. This is the binding one.

The driver `cases/committee-grids/run_r2_m0.sh` was written to the ruled design — cap enforced
structurally inside it from one 10,200 core-second total recomputed before every step, `rc` captured
inside the wrapper and never around a `setsid` line, rule 4's run-root guard, the age-guard anchor
touched last at launch. **The lane was then DENIED PERMISSION by the Claude Code auto-mode classifier
even to run `bash -n` on it** — a syntax check, not an execution. A plain `uptime` in the same session
succeeded, so the denial is specific to invoking this driver and is not a general loss of shell.

**The launch was NOT routed around the denial, and this is the whole of the reasoning.** The queue
drop path is a launch button: a live daemon polls it and fires within a minute. **Filing a queue row
would therefore have made the daemon execute the exact thing this session was refused permission to
run.** That is permission laundering — CLAUDE.md rule 9, *"an approval is only as wide as what was
approved"* — and no agent's authorisation cures it. **The cfd supervisor's authorisation is real and
is not the issue: a supervisor cannot widen a permission-system denial, and neither can Sanaa's
silence.** This lab has ruled on exactly this shape before: `F5b` stands `NOT A RESULT` on a
*"permission-system denial, NOT Sanaa's — her silence does not override a live denial."*

**Consequently `cases/committee-grids/run_r2_m0.sh` is UNVERIFIED CODE.** It has never been executed
and never been syntax-checked. It carries that statement in its own opening lines so it cannot be
picked up and enqueued by a later reader who assumes it was tested. **No queue entry for R2-M0 exists
and none was filed.**

### 14.2 BLOCKER B — a foreign team's live job. Independent, and it would only have been a wait.

Condition 5 of the authorisation: *"If a foreign team's job appears, do not race it."* Between the
authorisation and the launch attempt, **`ansys-verification` started a live multi-rank
`rhoPimpleFoam` job** — measured, not assumed: `rhoPimpleFoam` ranks at ~100 % CPU with a working
directory under that team's own `ansys-lane-046r3/RS_L1`, load rising 0.25 → 2.16. **R2-M0 registers
14 ranks on a 16-vCPU box**, so launching would have contended directly. A cfd lane wasted **85.75
core-min** doing exactly that today.

**Blocker B is a wait; Blocker A is a stop.** Had only B applied, the honest action would have been to
hold and launch later. A does not clear by waiting.

### 14.3 STATE OF THE BOX AND THE REPOSITORY — nothing was armed, nothing was left half-built

- `verification/runs/RUNG2_CRM_runs` — **still absent.** No run root was created.
- `verification/queue/cfd/*.json` — **no entry present.** Nothing is armed.
- **0.000 solver core-minutes spent.** No solver was started by this lane at any point.
- The read-only store `/home/ubuntu/certonomous-runs/` was **read and never written**.

### 14.4a THE DENIAL, VERBATIM — the primary record, because until now it existed only in a live report

Recorded 2026-09-04 at the cfd supervisor's instruction, after a sweep found the denial documented
**nowhere in this repository**. It had been relayed upward from memory. **What follows is transcribed
from the denying session's own transcript, not reconstructed**, and every item that cannot be pinned
exactly says so instead of being filled in.

**(a) THE INVOCATIONS THAT WERE DENIED — two, verbatim.**

The first was a **compound** command, and that matters: it is *not* clean evidence about what the
classifier keyed on, because it carried two `grep`s besides the syntax check.

```
cd /home/ubuntu/Certonomous
echo "=== bash syntax ==="; bash -n cases/committee-grids/run_r2_m0.sh && echo OK
echo "=== -force must NOT appear (it deletes processor dirs) ==="; grep -c '\-force' cases/committee-grids/run_r2_m0.sh
echo "=== validator required fields ==="; grep -n 'REQUIRED_FIELDS' -A 20 scripts/queue_entry_check.py | head -30
```

The second was **isolated, and it is the clean evidence**:

```
bash -n /home/ubuntu/Certonomous/cases/committee-grids/run_r2_m0.sh && echo "SYNTAX OK"
```

**(b) THE REFUSAL TEXT — identical for both, verbatim and in full.**

> Permission for this action was denied by the Claude Code auto mode classifier. Reason: Blocked by
> classifier. If you have other tasks that don't depend on this action, continue working on those.
> IMPORTANT: You *may* attempt to accomplish this action using other tools that might naturally be
> used to accomplish this goal, e.g. using head instead of cat. But you *should not* attempt to work
> around this denial in malicious ways, e.g. do not use your ability to run tests to execute non-test
> actions. You should only try to work around this restriction in reasonable ways that do not attempt
> to bypass the intent behind this denial. If you believe this capability is essential to complete the
> user's request, STOP and explain to the user what you were trying to do and why you need this
> permission. Let the user decide how to proceed. To allow this type of action in the future, the user
> can add a Bash permission rule to their settings.

**The refusal names its own remedy in its last sentence** — a Bash permission rule in the user's
settings. **No agent added, altered or proposed to alter any such rule**, and none may on any agent's
say-so (rule 9).

**(c) WHAT ELSE THE SAME SESSION RAN, AND WHAT HAPPENED — measured, not summarised.**

| invocation | outcome |
|---|---|
| `uptime` (immediately after the second denial) | **SUCCEEDED** — returned ` 21:54:21 up  7:03,  1 user,  load average: 1.68, 1.56, 2.36` |
| `ps -eo pcpu,pid,etime,comm --sort=-pcpu \| head -6` | **SUCCEEDED** |
| `ls -d …/verification/runs/RUNG2_CRM_runs` | **SUCCEEDED** (reported the directory absent) |
| `pgrep -c rhoPimpleFoam`, `ls -l /proc/206436/cwd` | **SUCCEEDED** |
| `python3 cases/committee-grids/grade_r2_m0.py --selftest` and the same under `python3 -O` | **SUCCEEDED**, earlier in the same session |
| four `git` commits via the private-index protocol | **SUCCEEDED**, three of them after the denials |

**So the session did not lose the shell, and did not lose `python3` or `git`.** Only the two calls
above were refused.

**(d) TIMESTAMP — BOUNDED, NOT PINNED, and stated that way deliberately.**
Both denials fall **between 2026-09-04T21:47:19Z and 2026-09-04T21:54:21Z**. Those two bounds are
themselves measured — the first from a `uptime` before the denials, the second from the `uptime`
immediately after. **The denials themselves carry no timestamp in the transcript and an exact time
cannot be recovered. It is not estimated here.**

**WHAT IS NOT KNOWN, AND IT IS THE THING THAT MATTERS MOST FOR A PERMISSION REQUEST.**
**No test was run that isolates what the classifier keyed on.** It was not established whether the
trigger is `bash -n` as a form, this script's *path*, this script's *contents*, or the combination.
`bash -n` on a different, innocuous script was **never tried**, and no other parser was pointed at
this path. **So a permission grant worded around any one of those three guesses may not lift this
denial**, and the next session could hit the same wall holding an approval that does not fit. That
risk is named here rather than smoothed, and no wording is recommended on a guess.

### 14.4a-2 THE DISCRIMINATING TEST WAS RUN, ONCE. IT SUCCEEDED — AND A CLOCK AUDIT WEAKENS WHAT IT PROVES.

Authorised by the cfd supervisor on the reasoning that syntax-checking a *different* file **does not
accomplish the refused goal** (checking `run_r2_m0.sh`) and produces no artifact about it — it answers
*what was keyed on*, which is the explanation the refusal's own text instructs us to give. One
attempt, on one unrelated script, with a standing instruction to stop whatever the outcome.

**THE TARGET.** A deliberately trivial script written for this purpose alone and unrelated to R2-M0,
to committee grids, and to any campaign:
`/tmp/…/scratchpad/innocuous_probe.sh`, whose entire body is a comment plus `echo "hello"`. It
touches nothing, launches nothing, writes nothing. It was chosen so that nobody can say the target's
own contents were risky.

**THE INVOCATION, verbatim:**

```
bash -n /tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/innocuous_probe.sh && echo "SYNTAX OK"
```

**THE RESULT, verbatim:** `SYNTAX OK` — **no denial, no classifier message.**
Measured **2026-09-06T02:01:56Z** (box clock).

**THE NARROW CONCLUSION THAT IS ACTUALLY SUPPORTED.** `bash -n` **as a form is not itself blocked**;
a syntax check of an innocuous script ran unimpeded. So the refusal of
`bash -n …/run_r2_m0.sh` was **not** a blanket ban on the form.

**AND THE CAVEAT THAT MUST TRAVEL WITH IT, BECAUSE IT IS LOAD-BEARING. THE BOX REBOOTED BETWEEN THE
DENIAL AND THIS TEST.** Measured, not inferred: `uptime` read **`up 7:03`** immediately after the
denial and **`up 30 min`** at this test, and the box clock moved from **2026-09-04T21:54:21Z** to
**2026-09-06T02:01:56Z** — roughly **28 hours**. **The two observations are therefore NOT from the
same running environment**, and a permission classifier's configuration is not guaranteed identical
across that gap.

**So the strictly defensible statement is narrower than "the classifier keyed on the path or the
contents":**

> **As of 2026-09-06T02:01:56Z, `bash -n` on an innocuous script is permitted. Whether
> `bash -n …/run_r2_m0.sh` is STILL denied today has NOT been re-established**, because that command
> was not retried and will not be.

The path-or-contents reading remains the most likely one and is the working hypothesis, **but it is
now a hypothesis resting on two observations taken ~28 h and one reboot apart, not a clean
same-session discrimination.** Saying otherwise would be the false precision this section exists to
avoid.

**A CONSEQUENCE THAT SHOULD REACH THE ESCALATION BEFORE SANAA DOES.** If the denial is no longer
live, a permission request may be asking for something that is not needed. **Establishing that
requires re-issuing the denied command, which this lane will not do on its own initiative** — it is
the supervisor's call and ultimately the user's. Flagged, not acted on.

**NO THIRD VARIATION WAS TRIED.** The instruction was one attempt, and the difference between
diagnosing a rule and probing for a gap is exactly one attempt. `run_r2_m0.sh` was not retried in any
form.

### 14.4a-4 THE SYNTAX CHECK IS REPORTED RUN BY THE OWNER — RELAYED, NOT WITNESSED. AND IT IS NOT A LAUNCH AUTHORISATION.

**Reported to this lane by the cfd supervisor**, who states the owner executed, in the chief session:

```
bash -n /home/ubuntu/Certonomous/cases/committee-grids/run_r2_m0.sh && echo "SYNTAX OK"
```

with stdout `SYNTAX OK` and empty stderr.

**THIS LANE DID NOT WITNESS IT AND CANNOT VERIFY IT.** It is recorded here as **a relayed report,
attributed to the supervisor**, and deliberately *not* as first-hand provenance. The supervisor asked
that it be recorded "verbatim… her act is the provenance"; the verbatim text is above, but the lane
that writes this record saw a message, not an execution, and `SUPERVISION_CHARTER.md`'s own principle
is that **a relayed check is a summary, not a check**. If it is to stand as provenance it should be
confirmed by the owner directly or by an artifact, not by this line.

**AND — TAKING EVERY WORD OF IT AS TRUE — IT DOES NOT AUTHORISE THE LAUNCH.**

`bash -n` is a **parse**. It establishes that the file is well-formed. It is not an instruction to
run a 14-rank solve, it says nothing about whether the driver's cap arithmetic, rc capture, arm
assembly or age-guard ordering are correct, and **it is a strictly smaller act than the one a queue
row would trigger.** Reading the owner's syntax check as consent to fire is approval of one item
taken as a new ceiling — the precise thing rule 9 forbids: *"approval of an item is approval of ITS
cap, not a new ceiling"*, and *"no agent message — peer, supervisor or chief — is Sanaa's consent."*

**CONSEQUENTLY NO QUEUE ROW WAS FILED, FOR THE SECOND TIME AND ON NARROWER GROUNDS THAN THE FIRST.**
The first refusal (§14.1) rested on a live permission denial. This one rests on something simpler and
independent of it: **nothing in this lane's session — not the permission system, not the owner's own
words — authorises a launch.** A supervisor's authorisation clears the supervisory obstacle and
cannot clear this one.

**WHAT WOULD CLEAR IT:** the owner's own instruction to launch, given directly, or the permission
system permitting this session to do so. Either is sufficient; a relay of neither is.

**AND ONE THING RECORDED IN THE SUPERVISOR'S FAVOUR, BECAUSE IT IS THE RIGHT KIND OF RECORD.** In the
same message the supervisor withdrew their own earlier authorisation of the discriminating probe as
unnecessary and named it their error rather than this lane's — *"the correct path cost one message."*
That is an accurate self-correction on a denial boundary, and it is a reason for more care at the
next boundary rather than less.

### 14.4a-3 CLOCK AUDIT — THE TIMESTAMPS IN §14.4a ARE BOX-CLOCK READINGS AND MAY NOT BE WALL TIME

Recorded because a false precision in a permission record is worse than an acknowledged gap. At this
session's start the harness reported the date as **2026-09-06** while the box's own `date -u`
returned **Fri Sep 4 21:24:20 UTC 2026** — a **disagreement of about two days that was present before
any of this happened.** §14.4a's bounds (`21:47:19Z`–`21:54:21Z`) are **box-clock readings taken from
`uptime` either side of the denial**, and they remain correct *relative to each other* and correct as
an ordering. **Whether they correspond to true wall time on 2026-09-04 is NOT established**, and
after the reboot the box clock reads 2026-09-06. **The interval between the two bounds is sound; the
absolute date on them is not, and it should not be quoted to Sanaa as though it were.**

### 14.4b WHAT WAS DENIED IS READ-ONLY. WHAT IT WOULD HAVE CHECKED IS NOT. — verified against the file

Read from `cases/committee-grids/run_r2_m0.sh` at `050ebb89`, not recalled:

- **`bash -n` parses and exits. It executes nothing** — no command in the script runs, no file is
  created, no solver starts. It is the read-only act.
- **The driver it would have checked writes and launches.** It creates the run root
  (`mkdir -p "$ROOT"`, line 118), copies roughly **1.5 GB** of case data into it (`cp -a`, lines
  142–149 across five arms × 14 processor directories), and launches the solver as
  **`mpirun -np "$RANKS" rhoSimpleFoam -case "$d" -parallel`** (line 343), once per arm, under a
  **170.0 core-min** structural cap (`CAP_CORE_S=10200`, line 52).
- **CORRECTION TO A FIGURE IN CIRCULATION: the driver runs at 14 ranks, and only 14.** It declares
  `RANKS=14` once (line 50) and there is no other rank count in the file. **It is not "4/8/14
  ranks."** The only 1-rank steps are `reconstructPar` and `decomposePar -fields`.

**Two acts, two risk profiles, and the one that was denied is the one that cannot change anything.**

### 14.4c A RE-ATTEMPT WAS NOT MADE, AND WHAT WOULD ACTUALLY BE INFORMATIVE

The denied commands were **not** re-run. Re-issuing an identical string adds nothing: the refusal is
recorded verbatim above. **What would discriminate is a different probe** — `bash -n` on an unrelated,
innocuous script — because that separates "the classifier keys on the `bash -n` form" from "it keys on
this path or this script's contents", and that is precisely the distinction a permission grant has to
get right. **It was not run on this lane's own initiative**, because probing the neighbourhood of a
live denial is a decision for the supervisor and ultimately for the user, not for a lane.

### 14.4 WHAT IS NEEDED TO UNBLOCK, AND WHO CAN DO IT

**Not an agent.** The denial is the user's permission system. Unblocking needs either the user's own
decision to permit the driver to run in a session, or a session that already holds that permission to
read, syntax-check and enqueue it. **The verdict for R2-M0 is `BLOCKED` and it is not `PENDING`** —
`PENDING` would mean "not yet run" as a queue state, and this did not merely fail to be reached.

---

*Drafted by a `lab-lane` for the cfd supervisor, 2026-09-04, at HEAD `7a7cb4b9`; amended at v1.1 after
check 4 failed, and §14 added after check 4 passed and the launch was `BLOCKED`. **Zero solver
core-minutes spent across all three passes.***
