# D11-C′ — the COMPONENT-1 FD STEP SWEEP — RESULTS

**Probe verdict: `GATE REACHED`.**
**A PLATEAU WAS DEMONSTRATED FOR COMPONENT 1** — five consecutive usable steps — and the adjoint
agrees with the plateau FD to **`1.906351e-04`** relative against a pre-registered band of
`5.0e-2`.

**Pre-registration:** `PREREGISTRATION.md`, frozen and committed at **`a02de9fa`**, blob
`fab55707777e4b38e32e56e34e7fba814e657990`. **Re-verified at grading time**: the disk file, the
`a02de9fa` blob and the HEAD blob are all the same hash. No gate, threshold, cap or label moved.
**Run:** `/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D11C/`, stamp
`20260825T175244Z_2328716`. Nothing filed, sent or posted (rule 7).

---

## 1. The grading path was the frozen path

Each instrument hashed against its committed blob at grading time. **All four MATCH**, and the
md5s are the ones §11 of the frozen document registered:

| file | md5 | blob vs HEAD |
|---|---|---|
| `d11c_run_script.py` | `f567cb451fee13f522f910d06efeebd5` | **MATCH** |
| `d11c_grade.py` | `9987e18d33a2c210625294b55084dc87` | **MATCH** |
| `d11c_stage_and_run.sh` | `3dd1beafcc7183408dc5b2123b5eed10` | **MATCH** |
| `d11c_case/constant/MRFProperties.template` | `e7d601ae02d9a3bc1c9f221b6792dea5` | **MATCH** |

`python3 d11c_grade.py --selftest` → **12/12 PASS** at grading time, unchanged from the freeze.
`python3 scripts/check_grader_self_blindness.py d11c_grade.py` → **clean on both probes**, which is
**not a proof of correctness** and is not offered as one.

## 2. Completion — all 25 registered containers ran, none was re-run

The registered container set was **1 mesh + 2 `compute_totals` + 22 `run_model` = 25**. The ledger
`.../D11C/ledger.txt` carries **all 25**, every one `rc=0`, `inspect(exit,oomkilled)=[0 false]`,
`measured_affinity=[13]`, and a `COLDSTART_PROVED` line **preceding** each container start.
`TOTAL_SPENT_CORE_MIN=3.0337` against `CAP=8.0`. **No stage was re-run and no stage was skipped.**

**Rule 4's age guard: `NOT EXERCISED`, with the reason**, exactly as §5b of the frozen document
disclosed **before** compute — DAFoam gzips `0/U` to `0/U.gz` mid-solve, so the file the guard
dates against ceases to exist. The substitute is the **pre-launch** absence proof: for every one of
the 25 arms the answer file, any time directory and `0/U.gz` were asserted **absent while the
container was not yet running**. The other clauses of rule 4 — `rc`, `docker inspect` exit code and
`OOMKilled`, artifact presence, finite values — **are** exercised and are recorded per stage.

## 3. The verdict quantity, and the plant that reaches it

`dTPIn_dpatchV` came back with **length 2 in both ω-stages**, equal to the registered
`N_COMPONENTS_REQUIRED = 2`, count printed:

| | component 0 | component 1 |
|---|---|---|
| ω = 30 rad/s (MRF ON) | `2.3058711101e-01` | **`-1.3660119098e-04`** |
| ω = 0 (inert arm) | `2.3061616252e-01` | `3.1484221064e-09` |

**G11C-2, the plant, is on component 1 itself — the quantity that reaches the verdict**, not on
`TPIn` and not on the vector. The **MRF-attributable fraction of component 1 is `1.0000230483`**:
essentially all of it moves with the plant. This is the control D11-F′ did not have. Its plant sat
on `TPIn`, which is why a derivative component could be ~99.99 % non-MRF and still pass a plant that
fired correctly.

## 4. THE ANSWER — a plateau, demonstrated, on component 1

**G11C-5. Component 1 = ∂TPIn/∂aoa in 1/deg, MRF ON at ω = 30 rad/s.**

| h (deg) | central FD | signal | usable? |
|---|---|---|---|
| `1.0e-05` | `-1.3646204167e-04` | `2.729e-09` | usable |
| `1.0e-04` | `-1.3689936740e-04` | `2.738e-08` | usable |
| **`1.0e-03`** | **`-1.3657515496e-04`** | `2.732e-07` | **usable — the reference step** |
| `1.0e-02` | `-1.3772887703e-04` | `2.755e-06` | usable |
| `1.0e-01` | `-1.3614950458e-04` | `2.723e-05` | usable |
| `1.0e+00` | `-1.4387590902e-04` | `2.878e-04` | usable, **outside the window** |

**PLATEAU DEMONSTRATED: `h ∈ [1.0e-05, 1.0e-01]`, five consecutive usable steps of one sign**,
relative spread inside the window `≈ 1.15e-02` against the registered `PLATEAU_TOL_REL = 2.0e-2`.
The reference step is `h = 1.0e-03` — **the middle of the longest qualifying window, fixed by the
rule frozen in §4 of the pre-registration, not chosen after seeing the agreement.** `h = 1.0e+00`
sits ~5 % away and is correctly excluded.

**Adjoint `-1.3660119098e-04` vs plateau FD `-1.3657515496e-04` → relative error `1.906351e-04`,
inside the pre-registered band `5.0e-2` by a factor of ~262.**

**This is what D11-C′ was bought to establish.** D11-F′'s headline `1.704895e-07` was a strong check
of the derivative's **non-MRF part** on a component that is ~99.99 % non-MRF. The component the MRF
term actually dominates — the one that moves four to five orders of magnitude when the zone spins
up — now has an FD table beside it **at a step proved to lie in a plateau**, which is the bright
line `DAFOAM_CHARTER.md` §1 draws.

## 5. The measured noise floor, and an honest limit on it

**G11C-3.** The floor was **measured, not assumed**: repeat `|base1 − base2| = 0.000000e+00`,
cross-task `|base1 − omegaP| = 0.000000e+00`, representational `ε·|TPIn| = 2.633418e-16` with
`TPIn = 1.1859858226134654e+00` → **floor `2.633418e-16`**.

**Stated plainly, and it limits the strength of the result: a zero repeat bounds REPRODUCIBILITY
only. It does NOT bound iterative-truncation jitter.** The re-runs are bit-identical because the
substrate is deterministic at np = 1, so the floor falls back to the representational epsilon. What
actually bounds truncation here is the **sweep itself** — six steps spanning five decades, five of
which agree to ~1 %. That is disclosed rather than absorbed, and it is the reason the plateau, not
the repeat, carries the evidentiary weight.

## 6. G11C-6 — the secondary finding, and it DEFENDS D11-F′

**Registered in advance as NOT altering the probe verdict**, and it does not. But it settles a
question this lane raised against D11-F′ and it settles it **in D11-F′'s favour**:

**Component 0 = ∂TPIn/∂U in 1/(m/s), MRF ON.** `h ∈ [1.0e-04, 1.0e-01]`, four consecutive usable
steps, **PLATEAU DEMONSTRATED**, reference `h = 1.0e-03`; adjoint `2.3058711101e-01` vs plateau FD
`2.3058707170e-01` → **`1.704895e-07`**.

**D11-F′'s `FD_H = 1.0e-3` LIES INSIDE the demonstrated plateau.** The reservation recorded in the
brief — *"a FIXED step with NO plateau demonstration, so `1.704895e-07` is NOT a verified gradient
and may not be quoted as one"* — was correct **when it was written**, because nothing had shown the
step was in a plateau. It is now shown. **`1.704895e-07` is RETROACTIVELY DEFENDED as a
plateau-step agreement** and may be quoted as one **from this record**, citing this sweep rather
than D11-F′ alone. **D11-F′ itself is not edited. Not one byte.** Its verdict `GATE REACHED` stands
as recorded; what changed is that a separate, later, frozen document supplies the plateau its
figure needed.

## 7. Placement

**G11C-7 PASS.** Every one of the 25 stages reports `measured_affinity=[13]`, equal to the
registered cpuset. **Placement was READ BACK FROM THE PROCESS, never inferred from the flag passed
to `docker run`** — which is the whole point of the gate, given the measured trap that `mpirun`
inside a `--cpus=N` container binds rank 0 to the first core of the host topology.

## 8. Cost

| | core-min |
|---|---|
| predicted (§6 of the frozen document) | **3.2** |
| **actual, gross** | **3.0337** |
| **actual, cleaned** | **3.0337** — identical; the longest stage wall was **10 s**, nowhere near the 3600 s stall rule |
| **waste, named separately and NOT absorbed into the ratio** | **0.0** — no re-run, no stall, no abandoned container |
| registered cap | 8.0 (**38 % used**) |
| **ratio actual/predicted** | **0.948** |

**$0.0026 — DERIVED, NOT MEASURED.** `cost_basis: c7a.4xlarge at $0.0513/core-h,
REPORTED-BY-OWNER, NOT MEASURED.`

**Gap attribution.** The 5.2 % underspend is **concentrated almost entirely in the mesh stage**:
predicted 0.22 core-min from D11-F′'s figure, **measured 0.0167** — a 0.203 core-min overprediction
on that one stage. The 22 `run_model` containers were predicted at 0.12 core-min each and **measured
a mean of 0.12198**, an error of **1.6 %**; the two `compute_totals` stages were predicted 0.37
combined and measured 0.3334. **Contention: nil measurable** — stage walls held at 7–8 s throughout
against an 8 s expectation and affinity `[13]` was confirmed on all 25 stages, so no contention
channel is claimed and none is needed to explain the gap.

**The D11 chain's prior spend — 0.7166 + 0.8334 + 0.7167 + 0.7501 = 3.0168 core-min — is named
separately and is NOT absorbed into this row's ratio**, exactly as §6 of the frozen document
registered.

Calibration row: **`C-75`** in `docs/COST_CALIBRATION.md`.

## 9. What this does NOT establish

Unchanged from §10 of the frozen document, and worth restating because the result is a green:

- **Nothing about MRF at engineering rotational rates.** This is a statement about a **30 rad/s
  zone on a 720-cell channel**. The measured fact that a **300 rad/s zone STALLS this steady
  substrate** stands and must be carried into D11's own pre-registration, which will need a
  rotating-frame-appropriate case or an unsteady formulation.
- **Nothing toolchain-independent.** Only the **shipped** row was bought
  (`dafoam/opt-packages:latest`, ID `sha256:9d45679d…90f07fc`). The patched row is **NOT BOUGHT**;
  this probe warps no mesh so the IDWarp patch cannot reach it, but the `subpclu` adjoint-solver
  path could in principle, and that was not tested.
- **A plateau in degrees on component 1 does not transfer to m/s on component 0**, which is why the
  secondary sweep was run rather than inferred — and the same non-transferability applies in
  reverse to any future component.
