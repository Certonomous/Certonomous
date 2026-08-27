# Curriculum item AV-2 — forward-AD vs reverse-AD duality at the total level on A1's NACA0012: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-27 by lane A of the DAFoam team.** The governing document is `PREREGISTRATION.md`
in this directory, frozen before any container started at commit **`3e2cbf74`**. **This file does not
revise the pre-registration.** No gate, threshold, cap, band edge or label was altered by this lane,
and **no grader or instrument was edited**.

**Launched by the queue-runner daemon with no agent alive** — `verification/queue/LAUNCH_LOG.tsv`
row `2026-08-26T23:19:58Z dafoam AV2_chain 622367 622367 1 15.3 3e2cbf74…`.

---

# 1. Item verdict: `NOT A RESULT`

The frozen comparator `av2_grade.py` **REFUSED (exit 2)** at gate G1 and printed its own label:

    REFUSAL: {"REFUSE": "G1", "detail": {"age_reference_absent":
      "/home/ubuntu/certonomous-runs/CURRICULUM-AV2-a1-naca0012-duality/X-S/0/U"}} -> NOT A RESULT

The item's registered composition (§3) orders the outcomes: *"any refusal → **`NOT A RESULT`**; either
row `BLOCKED` → `BLOCKED`; else …"*. **The refusal comes first and it is what this item is.** No G-DP
number, no `ε_k`, no row verdict is quoted.

**§2 below records what the forward-AD arms did, because it is a real reading of the toolchain that
the instrument itself was frozen to make and did make — but it is NOT the item verdict, and this
record does not promote it to one.**

## 2. The forward-AD channel — the registered `BLOCKED` branch fired

The pre-registration §2 registered a `BLOCKED` branch in advance: *"if `libs/ADF` does not import, no
subsystem exposes `add_dvgeo` …, **or forward mode raises on this case**, the instrument writes the row
`blocked` with the exception text, still writes the artefact, and exits 0 with `AV2_FAD_BLOCKED` in the
log."* **The third condition is the one that was met.**

From `FAD-S/av2_FAD.json` and `FAD-P/av2_FAD.json`, both rows:

| field | reading |
|---|---|
| `blocked_any` | **`true`** |
| `n_rows` / `n_components_requested` | 5 / 5 — `shape[0]`, `shape[3]`, `shape[6]`, `shape[7]`, `patchV[1]` |
| every row's `status` | **`BLOCKED`** (5 of 5, both images) |
| every row's `error` | `AnalysisError("'scenario1.coupling.solver' <class DAFoamSolver>: Error calling solve_nonlinear(), Primal solution failed!")` |
| `n_add_dvgeo` per row | **1** — a subsystem DOES expose `add_dvgeo`; the seed was placed |
| `useAD` per row | `{"dvName": "shape"/"patchV", "mode": "forward", "seedIndex": k}` — forward mode was requested per component |
| `control_fail` | **`false`** |
| `AV2_FAD_BLOCKED` in the arm log | present, both arms |
| `AV2_PLANTED_CONTROL_SEEN` in the arm log | present, both arms |

**Three things follow, and no more than three.**

1. **The registered silent-no-op hazard did NOT materialise.** The hazard note fixed at the freeze —
   DAFoam v4's mphys forward hooks are silent no-ops that `om.issue_warning(...)` and fall through
   (`mphys_dafoam.py:380/:437/:673/:754`) — would have produced a forward value of exactly `0.0`, and
   the instrument's registered triple refusal (exact 0.0 / exact 1.0 / function echo within 1e-6)
   would have fired. **`control_fail` is `false`: none of the three fired.** The failure is upstream
   of any forward value being produced at all.
2. **Seeding forward mode makes the PRIMAL fail.** `add_dvgeo` is present, the seed is placed, and the
   solve then raises `Primal solution failed!` — DAFoam's own `DASolver::checkPrimalFailure()`
   mechanism — on **all five components, on BOTH toolchain images**. It is not an IDWarp-row property.
3. **The instrument behaved exactly as frozen**: it wrote the exception text into every row, still
   wrote the artefact, printed `AV2_FAD_BLOCKED`, and exited 0.

**Under a comparator that could read these artefacts, the registered mapping is `BLOCKED` for both rows
and for the item.** It is not what this record certifies, because the comparator refused first at G1
for the reason in §3, and **`BLOCKED` is not a verdict a lane may award by reading the mapping rule
itself.** That determination is the supervisor's.

## 3. Why the grader refused — established from disk, and it is NOT physics

G1's age guard fixes its reference at `av2_grade.py:63`:

    DATUM_REF = {a: ("0.orig/U" if a == "MESH" else "0/U") for a in ARMS_REQUIRED}

**The NACA0012 incompressible tutorial runs with `writeCompression on`, and AV-2 runs every solver arm
at `np = 1` by registration.** On a serial arm the solver rewrites time-0 back to disk compressed,
replacing `0/U` with `0/U.gz`. Measured on this run root — all four solver arms:

| arm | `0/U` | `0/U.gz` | `.av2_age_datum` | `0/U.gz` mtime | age guard's substance |
|---|---|---|---|---|---|
| X-S | **absent** | present | 1787786539 | 1787786594 | **satisfied** — 55 s newer |
| FAD-S | **absent** | present | 1787786666 | 1787787068 | **satisfied** — 402 s newer |
| X-P | **absent** | present | 1787787227 | 1787787278 | **satisfied** — 51 s newer |
| FAD-P | **absent** | present | 1787787353 | 1787787770 | **satisfied** — 417 s newer |

**On every arm the artefact IS strictly newer than the datum. Only the reference PATH vanished, by
compression.** Because AV-2 is registered at `np = 1` throughout, **this item could not have reached a
verdict on any arm as frozen** — the refusal was structurally certain before the first container
started. The same defect refused AV-1's two `np = 1` arms on the same night (`curriculum_AV1/RESULTS.md`
§3): **one cause, two items.**

**Not repaired by this lane.** After first compute the gates are closed; a comparator repair is
`VERIFICATION_CHARTER.md` §2d.1's four-condition exception and is the supervisor's ruling. The frozen
file is untouched. Under `CLAUDE.md` rule 4 and this item's L-342 field classes `age_guard` is a
**physics** field and an absent physics field REFUSES: the grader did what it was frozen to do.

## 4. What ran

Five of five arms `rc = 0` from `docker inspect .State.ExitCode`, `OOMKilled false` on all five,
`chain=COMPLETE` at `20260826T234431Z`. MESH/X-S/FAD-S on `dafoam/opt-packages:latest`, X-P/FAD-P on
`dafoam-idwarp-rot:v1`.

| arm | row | ranks | wall s | core-min | cap | cpuset |
|---|---|---|---|---|---|---|
| MESH | SHIPPED | 1 | 10 | 0.167 | 5.0 | 0,1 |
| X-S | SHIPPED | 1 | 61 | 1.017 | 10.0 | 0,1 |
| FAD-S | SHIPPED | 1 | 496 | 8.267 | 25.0 | 0,1 |
| X-P | PATCHED | 1 | 61 | 1.017 | 10.0 | 0,1 |
| FAD-P | PATCHED | 1 | 517 | 8.617 | 25.0 | 0,1 |
| **total** | | | | **19.085** | 75.0 | |

Six artefacts exist and are non-empty: `av2_X.json` + `av2_X_planted.json` in each X arm, `av2_FAD.json`
in each FAD arm. The reverse-mode totals were computed (`X-S`/`X-P` carry `adjoint` with `CD` and `CL`
entries, `CD_baseline` `0.02091051000679216`, `CL_baseline` `0.49876526415423195` on the shipped row).
**No G-DP reading is quoted from them** — there is no forward channel to compare them against, every
forward row being `BLOCKED`.

## 5. Predictions

**All seven predictions P1–P7 are `NOT_MEASURED`.** The comparator refused before scoring any.
Two ledger figures are stated as raw readings and **not** as prediction outcomes: `FAD-S / X-S` =
**8.267 / 1.017 = 8.13** (P5's registered band is [1.0, 4.0]) and total graded core-min **19.085**
(P5's band [8, 40]). P5 remains unscored, and the 8.13 is not reported as a MISS.

## 6. What this item establishes, and what it does not

**It establishes nothing about forward/reverse duality.** No `ε_k` was computed and none is quotable.

**It records two toolchain readings that are on the artefacts and cost real compute:**

- **Forward-mode AD, seeded through `add_dvgeo` on an FFD `shape` component of the A1 NACA0012 case,
  makes DAFoam's primal fail — on all five registered components, on both IDWarp images.** Forward
  mode had been used by no lab case before this one (`curriculum_D10_probe_Fprime/RESULTS.md:149`).
  This is the first attempt and the first recorded outcome.
- **The registered silent-no-op hazard is NOT what blocks this path here.** The three echo controls all
  passed; the failure is a primal failure, one layer down. Anyone repairing this should look at the
  primal under a forward-seeded tape, not at the mphys hooks' warning-and-fall-through.

**It does not establish** that the forward path is unusable in general (one case, one mesh, one DAFoam
build, one component family), nor anything about the reverse tape's correctness, nor anything the FD
rows of D13/D15 already carry. The pre-registration's own reason for buying this test — *"a 1e-5
discrepancy here is a defect"*, against an FD comparison's noise floor — **remains untested.**

## 7. Cost — actual against the frozen estimate, and the waste named

| arm | predicted point | actual core-min | ratio |
|---|---|---|---|
| MESH | 0.3 | 0.167 | 0.557 |
| X-S / X-P | 2.5 each | 1.017 / 1.017 | 0.407 / 0.407 |
| FAD-S / FAD-P | 5.0 each | 8.267 / 8.617 | **1.653 / 1.723** |
| **total** | **15.3** | **19.085** | **1.247** |

Gross = cleaned; no arm near the 3,600-s stall figure. **$0.0163 DERIVED, NOT MEASURED** at
$0.0513/core-h, c7a.4xlarge, `cost_basis` REPORTED-BY-OWNER (`COMPUTE_BUDGET_CHARTER.md` §5).
Predicted $0.0131 DERIVED. Every arm was inside its cap; G10 was never composed because the grade
refused, so the cap compliance here is a ledger reading, not a gate verdict.

**WASTE: 19.085 core-min = $0.0163 DERIVED — the ENTIRE spend, named separately and never absorbed
into the ratio** (`COMPUTE_BUDGET_CHARTER.md` §6: *"Waste is reported, not absorbed"*). Five arms ran
correctly and bought **no graded number**. Of that, **16.884 core-min (the two FAD arms) did buy the
instrument-level reading of §2**, which is on the record and reusable; **2.201 core-min (MESH + the two
X arms) bought nothing at all.** Both figures are stated rather than netted.

**Gap attribution — the ONE arm pair that overran is the forward-AD pair, and the overrun is the
finding paying for itself.** §4 priced the FAD arm as *"one ordinary primal + five forward-mode
primals … adopted at 3× a plain cold primal"* = 0.3 + 5 × 0.9 ≈ 5.0. Measured, **8.267 and 8.617** —
**1.65–1.72× the point**. The reason is legible in the artefact: each of the five forward-seeded
components ran a **full primal attempt before failing**, at `wall_s` 95.9–99.9 s per component
(479.4 s summed on FAD-S, 496.1 s on FAD-P), i.e. **the forward-mode primal is ≈ 1.6 core-min against
a plain cold primal's ≈ 0.3 — a factor of ≈ 5.3, not the assumed 3×, and it is paid IN FULL even when
the primal then fails.** A failing forward primal is not cheap. Contention was nil: the aggregate
records show `live: []` on every AV-2 arm.

**Carry forward:** price a forward-mode (CoDiPack tangent) primal on A1's 4,032-cell mesh at **≈ 1.6
core-min, ≈ 5× a plain cold primal**, and price it for the failing case too — a `checkPrimalFailure`
exit costs the whole primal. The X arms confirm AV-1's finding independently: a cold primal + two
adjoints at np = 1 on this mesh is **1.0 core-min**, not the 2.5 that C-31-plus-a-CL-adjoint predicted.

The calibration row is `C-159` in `docs/COST_CALIBRATION.md`.

## 8. What is owed, and to whom

Three things, all the supervisor's and none of them a lane's: **(a)** whether the G1 age-reference
defect is repaired under `VERIFICATION_CHARTER.md` §2d.1, which would let the registered `BLOCKED`
mapping of §2 be awarded properly; **(b)** whether the forward-mode primal failure is triaged as a
DAFoam finding, a case finding or a toolchain finding — it is a crash and a crash is a finding until
triage says otherwise; **(c)** whether anything is re-fired, and at whose cost. **This lane has
proposed none of them and edited nothing.**

## 9. Artefacts, all still on disk

Run root `/home/ubuntu/certonomous-runs/CURRICULUM-AV2-a1-naca0012-duality/`:
`AV2_grade_20260826T234431Z.json` and `.out` (the refusal), `ledger.txt` (5 `ARM=` rows),
`STATUS.chain` and the five per-arm `STATUS.*`, per-arm `*.inspect.txt` kernel records,
`X-{S,P}/av2_X.json` and `av2_X_planted.json`, `FAD-{S,P}/av2_FAD.json`, per-arm `.av2_age_datum`,
the two 144 KB FAD solver logs carrying `AV2_FAD_BLOCKED` and `AV2_PLANTED_CONTROL_SEEN`, and memory
windows.
