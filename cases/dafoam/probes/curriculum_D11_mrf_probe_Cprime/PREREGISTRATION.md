# D11-C′ — the COMPONENT-1 FD STEP SWEEP the D11-F′ probe did not buy — PRE-REGISTRATION

**Form:** the 10-line mini-prereg (Sanaa, 2026-08-25: *"standard verification/validation cases
use the 10-line prereg form … minutes to freeze, not sessions"*). **Rigor standard unchanged.**
**Frozen at the commit that adds this file; no container of D11-C′ has run — the run directory
`/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D11C` DOES NOT EXIST at this commit.**
**Author:** dafoam `lab-lane`, 2026-08-25. Nothing filed, sent or posted (rule 7).

---

## 0. Why this is a separate buy, and what it does NOT touch

**D11-F′ is not edited. Not one byte.** Its verdict `GATE REACHED` stands as recorded. This is a
new tree, a new pre-registration and new gates, because the thing being bought was never inside
D11-F′'s frozen gate set and cannot be added to it after compute (rule 2).

**The finding this repairs.** D11-F′ reports *"MRF-ON adjoint vs central FD: relative error
`1.704895e-07`"*. Its gate G11-5 sets **`adj = dP[0]`** — it compares **component 0 only**.
`dTPIn_dpatchV` has **two** components: `[0] = ∂TPIn/∂(inlet speed)` in 1/(m/s), and
`[1] = ∂TPIn/∂(angle of attack)` in 1/deg. Read off the D11-F′ artifacts on disk
(`/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D11F/{omegaP,omega0}/d11f_*.json`):

| component | MRF off (ω = 0) | MRF on (ω = 30 rad/s) | relative change | FD-checked by D11-F′? |
|---|---|---|---|---|
| 0 | `0.23061616252401435` | `0.23058711100900367` | `1.26e-04` | **yes** — this is the `1.704895e-07` |
| 1 | `3.1484221063860114e-09` | `-1.366011909783860e-04` | ~4–5 orders of magnitude | **no** |

**The FD-checked component is ~99.99 % non-MRF; the component MRF dominates was never checked.**
D11-F′'s agreement figure is therefore a strong check of the derivative's **non-MRF part** and says
little about the MRF contribution itself. This document buys the missing check.

## 1. Case, capability, substrate

Identical substrate to D11-F′ and D11-O′: a **720-cell 2D channel**, `DASimpleFoam`,
Spalart–Allmaras, carrying an MRF **cellZone** `rotor` over `0.08 ≤ x ≤ 0.12`. `d11c_case/` is a
byte-for-byte copy of `d11f_case/` (`MRFProperties.template` md5 `e7d601ae02d9a3bc1c9f221b6792dea5`,
**identical to D11-D′, D11-O′ and D11-F′**). Capability under test: **MRF/rotating-frame adjoint
correctness on the component the MRF term dominates**.

**Carried in as measured, not to be rediscovered:** DAFoam's MRF is a **cell-zone** formulation,
not an interface; it reads a scalar `omega` in **rad/s, not rpm**; it ships **no `DAInput` for
MRF**; and a **300 rad/s zone STALLS this steady primal**, which is why ω = 30 is used.

## 2. Reference / anchors

There is **no external reference value** for this derivative; the reference is the **central
finite-difference estimate at a step proved to lie in a plateau**, which is what
`DAFOAM_CHARTER.md` §1 fixes as the line and §3 fixes as *"read PER COMPONENT, not off the
vector"*. Anchors on disk: D11-F′'s five stage JSONs (above) and its ledger
`.../D11F/ledger.txt` for per-stage cost.

## 3. Quantities

1. `adj1 = dTPIn_dpatchV[1]` at ω = 30 — **the quantity that reaches the verdict**.
2. `adj1_inert = dTPIn_dpatchV[1]` at ω = 0 — the plant's inert arm, on the same quantity.
3. `FD1(h) = [TPIn(aoa = +h) − TPIn(aoa = −h)] / (2h)` over the frozen aoa sweep.
4. `δ_repeat`, `δ_crosstask` — the **measured** noise floor, taken **before any step is sized**.
5. `adj0`, `FD0(h)` over the frozen U sweep — the **secondary**, separately registered question.
6. `sched_affinity` per stage — container placement **read back from the process**.

## 4. Bands and constants — FROZEN BEFORE COMPUTE

| constant | value | meaning |
|---|---|---|
| `OMEGA_PLANT` / `OMEGA_INERT` | `30.0` / `0.0` rad/s | the plant, unchanged from D11-F′ |
| `N_COMPONENTS_REQUIRED` | `2` | refuse on an EMPTY **or SHORT** set, **by count, count printed** |
| `COMPONENT_UNDER_TEST` | `1` | the component D11-F′ did not check |
| `FLOOR_DERIV` | `1.0e-12` | at or below → silently-zero derivative |
| `PLANT_ATTRIB_MIN` | `0.5` | ≥ half of \|adj1(ω=30)\| must be MRF-attributable, else REFUSE |
| `NOISE_FACTOR` | `10.0` | an FD signal must exceed this many measured noise floors to be usable |
| `PLATEAU_TOL_REL` | `2.0e-2` | max relative spread of FD estimates inside a plateau window |
| `PLATEAU_MIN_STEPS` | `3` | a plateau is ≥ 3 **consecutive** usable steps of one sign |
| `FD_BAND_REL` | `5.0e-2` | adjoint-vs-FD band — **the same 5 % D11-F′ used for component 0** |
| aoa sweep (deg) | `1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e0` | 6 steps, 12 stages |
| U sweep (m/s) | `1e-4, 1e-3, 1e-2, 1e-1` | 4 steps, 8 stages |

**The plateau reference step is fixed by rule, not by choice:** the longest qualifying window
(ties → lowest start index), and within it the **middle** step. No step is selected after seeing
the agreement.

## 5. Criteria / gates — fixed vocabulary only

| gate | test | verdict mapping |
|---|---|---|
| **G11C-0** | `len(dTPIn_dpatchV) == 2` in **both** ω-stages | wrong length → **REFUSE (exit 2), count printed**; a *COMPLETED* stage returning **no** derivative key → **BLOCKED**; a *missing or non-COMPLETE* stage → **NOT A RESULT** |
| **G11C-1** | `\|adj1\| > FLOOR_DERIV` | else **GATE FAIL** (silently-zero MRF adjoint) |
| **G11C-2** | **THE PLANT, ON THE VERDICT QUANTITY**: `\|adj1 − adj1_inert\| / \|adj1\| ≥ 0.5`; bit-identity → REFUSE | blind plant → **REFUSE (exit 2)** |
| **G11C-3** | noise floor `= max(δ_repeat, δ_crosstask, ε·\|TPIn\|)`, **measured** | reported; feeds G11C-4 |
| **G11C-4** | some registered aoa step resolves above `10 ×` the floor | else **NOT A RESULT** |
| **G11C-5** | **plateau demonstrated** → `\|adj1 − FD1(h*)\| / \|FD1(h*)\| ≤ 5.0e-2` | no plateau → **NOT A RESULT**; in band → **PASS**; outside → **GATE FAIL** |
| **G11C-6** | the **secondary** U sweep on component 0, and whether `h = 1.0e-3 m/s` lies inside its plateau | **REGISTERED IN ADVANCE AS NOT ALTERING THE PROBE VERDICT** — it is a separately registered finding about D11-F′ |
| **G11C-7** | measured `sched_affinity == [13]` in every stage | mismatch → **GATE FAIL on the COST-ATTRIBUTION row only, never on the derivative verdict** |

**Probe verdict** = worst of the component-1 chain G11C-0…G11C-5 in the order
`PASS/GATE REACHED < GATE FAIL < NOT A RESULT < BLOCKED`; all clean → **`GATE REACHED`**.

**REGISTERED HONEST OUTCOME, written before the run:** *if no plateau is found, the verdict is
**`NOT A RESULT`** and that is a good outcome.* An agreement quoted from a single step that was
never shown to sit in a plateau is exactly what `DAFOAM_CHARTER.md` §1 forbids, and this lane will
not manufacture one by picking a step after seeing the numbers.

## 5a. The plant, and the D3 defect it is shaped against

`cases/dafoam/ladder-a/A4/curriculum_D3/d3_grade.py` returns **`PASS` at 0.0000 % with zero sign
flips over an EMPTY COMPONENT SET**: its refusal tests **key presence** and never non-emptiness, the
plateau loop iterates zero times, and its trivial-baseline control **fires correctly while
certifying a result it did not measure — because it measures a different quantity from the one that
reaches the verdict.** Two consequences are registered here:

1. **G11C-0 refuses on an EMPTY *or SHORT* set explicitly, by count, with the count printed.**
2. **G11C-2 places the discrimination control on component 1 itself** — the quantity that reaches
   the verdict — not on `TPIn` and not on the vector. D11-F′'s plant was on `TPIn`, which is why a
   derivative component could be ~99.99 % non-MRF and pass a plant that fired correctly.

**Proven able to refuse before this commit:** `python3 d11c_grade.py --selftest` → **12/12 PASS**
(healthy; empty set refuses *with the count*; short set refuses *with the count*; zero component
→ GATE FAIL; bit-identical plant refuses; a 90-%-non-MRF plant refuses; a jittered sweep →
NOT A RESULT; disagreement → GATE FAIL; a noise-swamped sweep → NOT A RESULT; completed-but-no-key
→ BLOCKED; misplacement caught without touching the derivative verdict; a short sweep table
refuses). **`rc = 1` and `rc = 2` are different failures and a harness exit code is not a solver
exit code**: a missing stage JSON maps to **NOT A RESULT**, never to `BLOCKED`, so this lane's own
harness cannot trip a gate that would record a capability as absent that was never reached.

## 5b. Rule 4, and the clause that is NOT EXERCISED

**`0/U` is gzipped to `0/U.gz` mid-solve by DAFoam, so rule 4's age guard is unsatisfiable on this
family** — the file the guard dates against ceases to exist during the run. Recorded as
**`NOT EXERCISED`, with the reason**, and its evidentiary purpose discharged by a **stronger,
PRE-LAUNCH** assertion in `d11c_stage_and_run.sh`: the arm directory is destroyed, re-copied from
the mesh tree, and the **answer file, any time directory and `0/U.gz` are asserted ABSENT while the
container is not yet running** (`COLDSTART_PROVED` in the ledger). A pre-launch proof that no
answer file existed is stronger than a post-hoc mtime inference, and **no `0/U.gz` end-of-run mtime
is permitted to manufacture a green.**

**Disclosed as a `VERIFICATION_CHARTER.md` §2d.1 matter, four conditions enumerated:**
(i) **the defect is in the rule's applicability, not in the result** — the field the guard needs is
deleted by the toolchain, not by this lane; (ii) **it is disclosed before compute, here, in the
frozen document**, not discovered afterwards; (iii) **the substitute is strictly stronger** — an
absence proved before the process starts versus an ordering inferred after it ends; (iv) **no gate,
threshold, cap or label moves** — G11C-0…G11C-7 are unchanged by it, and the substitute can only
*refuse*, never *pass*, a stage. The other clauses of rule 4 (`rc`, `docker inspect` exit code and
`OOMKilled`, artifact presence, finite values) are exercised and recorded per stage in the ledger.

## 6. Cost — with a NUMERIC stop threshold

- **Predicted: 3.2 core-min.** Measured basis, from `.../D11F/ledger.txt`: mesh 0.2167, a
  `compute_totals` stage 0.2 and 0.1667, a `run_model` stage 0.1167–0.1333 core-min. This probe
  runs 1 mesh + 2 `compute_totals` + 22 `run_model` containers = **25 containers**:
  `0.22 + 0.20 + 0.17 + 22 × 0.12 ≈ 3.2`.
- **REGISTERED CAP: 8.0 core-min**, cumulative over every container including the mesh build,
  240 s per-stage timeout. **An overrun STOPS the probe; it does not get a new budget** (rule 12).
  The cap sits at 2.5× the prediction because 25 container starts against a live sibling (`D8`) can
  stretch per-stage wall time, and a guard that trips on ordinary contention is a guard that gets
  raised. **The launcher ASSERTS that the enforced cap equals this literal** — it aborts unless
  `grep -qF "REGISTERED CAP: 8.0 core-min"` finds this line in this file. A peer lane today
  registered 3.0 and enforced 6.0 by copy-forward with no assertion; that is a freeze-integrity
  defect in kind even where harmless in outcome, and it is not repeated.
- `$0.0027` **derived, NOT MEASURED**.
- `cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED.`
- **The D11 chain's prior spend — 0.7166 + 0.8334 + 0.7167 + 0.7501 = 3.0168 core-min — is named
  separately in `docs/COST_CALIBRATION.md` and is NOT absorbed into this row's ratio.**

## 7. np, decomposition, and placement

**`np = 1`; `numberOfSubdomains 1`. With np = 1 the parallel-determinism question does not
arise** and is not claimed to have been tested.

**Placement is registered and read back.** `mpirun` inside a `--cpus=N` container binds rank 0 to
the **first core of the host topology**, so concurrent containers collide on one core while the box
reports itself idle — measured on this box today at **0.250 cores delivered against a 1.0-core
quota** with the host **61 % idle**. Every container here is pinned `--cpuset-cpus=13`; the peer
`d8_opt` container running at this commit carries `cpuset=[]` and will sit on core 0.
**G11C-7 compares the affinity READ BACK from inside each process against `[13]`** — placement is
never inferred from the flag that was passed. **Correctness is unaffected by contention; cost is
not, so a placement mismatch is attributed to the CONTENTION channel and never absorbed into the
actual/predicted ratio** (rule 12; `COMPUTE_BUDGET_CHARTER.md` §6).

## 8. Toolchain — by IMAGE ID, not by tag

| item | identity |
|---|---|
| image | `dafoam/opt-packages:latest`, **ID `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`** — the **stock** digest |
| IDWarp | **stock**; this probe warps no mesh and has no IDWarp in its chain |
| DAFoam / OpenFOAM / PETSc | 5.0.0 / v2506 / 3.15.5, as recorded for this image |

**A version string is not an identity** (`DAFOAM_CHARTER.md` §6). The launcher resolves and logs
the image ID at run time and aborts if it cannot.

## 9. The two-row shipped/patched rule — and which row is bought

`DAFOAM_CHARTER.md` §6: *two rows or it is not a verdict about DAFoam.*

| row | toolchain | bought? |
|---|---|---|
| **shipped** | stock `dafoam/opt-packages:latest`, ID `sha256:9d45679d…90f07fc` | **YES** |
| **patched** | `dafoam-idwarp-rot:v1` / `dafoam-subpclu:v2` | **NOT BOUGHT** |

**Named, with the reason and the consequence.** The patched images differ from stock in
`DALinearEqn.C` (adjoint linear solver) and in IDWarp's rotation derivative. **This probe warps no
mesh**, so the IDWarp patch cannot reach it; the `subpclu` path could in principle affect the
adjoint solve. The row is not bought because the registered question is *which component the MRF
term reaches*, which is a property of the residual linearisation rather than of the preconditioner.
**Consequence, stated plainly: this item CANNOT claim a toolchain-independent result.** Whatever
D11-C′ returns is a statement about the stock image only.

## 10. What this probe does NOT establish

It establishes **nothing about MRF at engineering rotational rates**. Whatever it returns is a
statement about a **30 rad/s zone on a 720-cell channel**. The measured fact that a **300 rad/s
zone STALLS this steady substrate stands** and must be carried into D11's own pre-registration,
which will need a rotating-frame-appropriate case or an unsteady formulation.

It also does **not** transfer between components or units: a plateau demonstrated in **degrees on
component 1** says nothing about a plateau in **m/s on component 0**, which is precisely why the
secondary U sweep is run rather than inferred. **`FD_H = 1.0e-3` was the single step used for
component 0 and no plateau was demonstrated for it; that figure may not be quoted as a verified
gradient unless G11C-6 places it inside a demonstrated plateau, and G11C-6 may equally find it
outside one.** Both outcomes are registered here in advance as reportable.

## 11. Frozen instruments (md5 at this commit)

| file | md5 |
|---|---|
| `d11c_run_script.py` | `f567cb451fee13f522f910d06efeebd5` |
| `d11c_grade.py` | `9987e18d33a2c210625294b55084dc87` |
| `d11c_stage_and_run.sh` | `3dd1beafcc7183408dc5b2123b5eed10` |
| `d11c_case/constant/MRFProperties.template` | `e7d601ae02d9a3bc1c9f221b6792dea5` |

**The grading path is fixed at this commit.** After the run, each file is hashed against its
committed blob and the equality recorded in `RESULTS.md`; a mismatch is a `NOT A RESULT`.
