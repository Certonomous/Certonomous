# RUNG 2 pre-registration — NASA CRM / DPW5 — the `R2-M0` COMPRESSIBLE ADMISSION PROBE, and the two blockers that mean the DRAG GATE IS NOT REGISTERED HERE

**Team: cfd. Case id `RUNG2-CRM-M0`. v1.0, drafted 2026-09-04 by a `lab-lane` for the cfd supervisor.**

> # ⚠ DRAFT — NOT AUTHORISED TO LAUNCH. SUPERVISOR CHECK 4 NOT PERFORMED.
>
> **NOTHING LAUNCHES AGAINST THIS FILE. NO COMPUTE HAS BEEN RUN UNDER IT.**
>
> The rule-2 freeze — pre-registration **committed** before compute — is the cfd supervisor's
> **non-delegable personal check** (`SUPERVISION_CHARTER.md` §3). This lane does not take it and is
> not authorised to launch any solve. The drafting lane spent **zero solver core-minutes.**
>
> Registered run root verified **ABSENT** at drafting under a live planted control (§1.4):
> `verification/runs/RUNG2_CRM_runs/` and every path beneath it.
>
> **AND READ §4 BEFORE RULING ON §6.** §4 is a blocker this team cannot clear by measurement, by
> amendment, or by spending. It is a standards question and it is **Sanaa's**.

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
in two independent measured reasons, and neither of them is compute.

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
| **R2-G3** | **Planted control on the reader** (rule 3). | The log reader reports **"abort at Time = 2, signal 8"** on the archived 2026-08-01 log and **"no abort"** on a synthetic clean log, in the same invocation | **2.0** | **`PASS`** | **`NOT A RESULT`** for G0 and G1 — a reader not shown able to see both outcomes has not measured either |
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

**The grading path is fixed at this document's commit.** The comparator
`verification/runs/RUNG2_CRM_runs/M0_compressible_admission/grade_r2_m0.py` is hashed against its
committed blob at grading time and the run refuses on mismatch
(`scripts/check_comparator_freeze.py`). **It does not exist yet and is not authorised to be written
until §6 is frozen by the supervisor.**

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
3. **The grid triple does not exist and does not "come free."** Sanaa's order says the committee
   family makes the triple free. **Only L1.T is on this box.** L2.C (2.16 M) and L3.M (5.11 M) are
   published and, by this lab's own measured memory law, would fit here — but they are **not
   downloaded, never converted, and never `checkMesh`'d.** A Roache triple assembled from L1.T's
   hex/prism/hybrid files would be **three topologies at one refinement level, not a refinement
   triple**, and two of those three are measured non-solvable. Registering a triple gate today would
   register a triple that does not exist.

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
that it is the **cheapest** thing that can move a `BLOCKED` off Blocker 1 — 67 core-min against a
rung Sanaa priced in *"tens of core-hours per fine-grid solve"* — and that its answer is informative
in **both** directions. **If Sanaa rules on §4 that a committee grid cannot carry a physics gate here,
P stops being worth 67 core-min for Rung 2's sake and this probe should be cancelled unspent.**

---

## 12. THE RECOMMENDATION THIS LANE MAKES

1. **Rung 2 (a), the drag-band verdict: `BLOCKED`.** Two independent measured blockers, and the
   binding one (§4) is a standards conflict inside Sanaa's own instruction. **Escalate §4 to Sanaa.**
   No compute clears it.
2. **`R2-M0`: launch it only if the supervisor judges it worth 67 core-min on its own account** —
   as capability work for the mesh-import line and for Rung 3, independent of whether Rung 2 (a)
   survives §4. It is honest, cheap and falsifiable either way. **If §4 goes against committee grids,
   cancel it unspent.**
3. **Do not download L2.C or L3.M, and do not start on HLPW/Rung 3, until §4 is ruled.** Sanaa's own
   order already forbids Rung 3 before CRM is held; §4 is what decides whether CRM can ever be held.

---

*Drafted by a `lab-lane` for the cfd supervisor, 2026-09-04, at HEAD `7a7cb4b9`. Zero solver
core-minutes spent in drafting. **Supervisor check 4 — pre-registration committed before compute — has
NOT been performed. This file authorises nothing.***
