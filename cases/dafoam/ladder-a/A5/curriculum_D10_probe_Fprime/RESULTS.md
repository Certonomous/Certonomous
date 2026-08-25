# D10-F′ — THE FD PAIR FOR THE D10-P′ ADJOINT GRADIENT — RESULTS

Dated **2026-08-25**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.
**Nothing here was filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).

---

## 1. VERDICT

# `PASS`

The adjoint gradient `d(HFX)/d(patchV[0])` agrees with a central finite difference, at a step
**proved** to lie in a plateau, to **`4.401007e-08` relative** — against a pre-registered PASS
band of **`5.0e-2`**.

**`DAFOAM_CHARTER.md` §2's bright line is now satisfied for D10-P′.** The gradient that entered
the record with a disclaimer instead of a table has a table.

Pre-registration frozen at **`120dddd2`**, committed **before any container started**; run root
verified absent by `test -e` immediately before it was written. Grading path `d10f_grade.py`
md5 **`7aaf2c67f1f63910238ab378aa7ac873`**, **re-verified against the committed HEAD blob
immediately before grading**, and again before the archived run. **No amendment, no addendum;
nothing was changed after the freeze.**

### THE SCOPE FENCE HELD

**D10-P′'s reachability verdict DID NOT MOVE and could not have.** `GATE REACHED` stands for
arm P′ exactly as it did before this arm ran. This arm converted a disclaimed gradient into a
verified one and did nothing else.

---

## 2. THE NUMBERS

| | |
|---|---|
| **adjoint** `d(HFX)/d(patchV[0])` | **`1.9771502962421681e+02`** |
| **central FD at the reference step** | **`1.9771503832566850e+02`** |
| **reference step h** | **`1.000e-03`** m/s (`h/DV = 1e-4` on a 10 m/s DV) |
| **relative error** `\|D_adj − D_fd\| / \|D_fd\|` | **`4.401007e-08`** |
| sign flip | **no** |
| band | PASS ≤ `5.0e-2` → **`PASS`** |
| **δ_repeat** | **`0.000000e+00` absolute and relative** |
| FD signal at the reference step | `\|HFX(+h) − HFX(−h)\| / \|HFX\| = 1.389284e-04` |

**The statistic is NAMED**, as `DAFOAM_CHARTER.md` §2 requires: the **single-component relative
error**. It is **NOT** the vector-relative error this ladder's multi-component records quote and
**NOT** the per-component average the DAFoam papers quote. **Those three are different
statistics and this record does not compare them.**

## 3. THE FD TABLE, AND THE PLATEAU — PROVED, NOT ASSERTED

Every registered step ran. **None is hidden**: `VERIFICATION_CHARTER.md` §7 — a sweep that hides
its failed steps is reporting a plateau it did not measure.

| tag | h (m/s) | HFX(+h) | HFX(−h) | central FD | rel err vs adjoint |
|---|---|---|---|---|---|
| `s1` | 1.000e-05 | 2.8462889054364482e+03 | 2.8462849511449826e+03 | 1.9771457327806272e+02 | 2.308100e-06 |
| `s2` | 1.000e-04 | 2.8463066997738761e+03 | 2.8462671567526118e+03 | 1.9771510632153877e+02 | 3.879185e-07 |
| **`s3`** | **1.000e-03** | 2.8464846408921103e+03 | 2.8460892108154590e+03 | **1.9771503832566850e+02** | **4.401007e-08** |
| `s4` | 1.000e-02 | 2.8482638360803971e+03 | 2.8443095347884710e+03 | 1.9771506459630928e+02 | 1.768813e-07 |
| `s5` | 1.000e-01 | 2.8660343037838120e+03 | 2.8264910502881157e+03 | 1.9771626747848131e+02 | 6.260800e-06 |
| `s6` | 5.000e-01 | 2.9445563512401786e+03 | 2.7468021297945838e+03 | 1.9775422144559479e+02 | 1.982238e-04 |

**Plateau: all six steps, spanning `h` over four and a half orders of magnitude**, adjacent
values agreeing to between `1.3e-07` and `1.9e-04` relative against a registered tolerance of
`1.0e-2`.

| adjacent pair | relative difference | in plateau? |
|---|---|---|
| s1→s2 | 2.696018e-06 | IN |
| s2→s3 | 3.439084e-07 | IN |
| s3→s4 | 1.328712e-07 | IN |
| s4→s5 | 6.083881e-06 | IN |
| s5→s6 | 1.919249e-04 | IN |

The reference step was selected by the **rule frozen before the data** — the middle step of the
longest consecutive run, ties to the smaller step — which returned `s3`.

### THE INDEPENDENT CORROBORATION THIS TABLE CARRIES, AND WHY IT MATTERS

**The error column is a clean V with its minimum exactly at `s3`** — 2.3e-06, 3.9e-07,
**4.4e-08**, 1.8e-07, 6.3e-06, 2.0e-04. That is the textbook central-difference error signature:
**subtractive-cancellation roundoff rising as `h` falls** (s2→s1 grows ≈ 6× for a 10× smaller
step, the `1/h` side) and **`O(h²)` truncation rising as `h` grows** (s4→s5 grows ≈ 35× for 10×,
s5→s6 ≈ 32× for 5×).

**This matters because the reference-step rule and the error minimum are independent.** The rule
is a *positional* rule over the plateau structure and knows nothing about the adjoint; it landed
on the step that independently minimises disagreement with a number it never reads. **A grader
that had been fitting the step to the answer could not produce that coincidence, because the
rule cannot see the answer.**

---

## 4. THE CONTROLS — every one PASSED, and every one had been shown able to FAIL

| control | what it did | result |
|---|---|---|
| **C1** instrument identity, **BIT-FOR-BIT** | the new run script's `compute_totals` at the unperturbed DV vs the committed D10-P′ values | `HFX = 2.8462869282732759e+03` and **both** adjoint components reproduced **exactly**, threshold **ZERO** |
| **C2** planted zero, **physical** | +1.234 K on the lowerWall `fixedValue`, read back from `plant/0/T` on disk | `HFX_plant = 2.9048255627647618e+03`, **response `2.056667e-02`** against floor `1.0e-6` |
| **C3** planted zero, **reader-level** | **+7.531e-02** written into a **COPY** of `d10f_fdp_s4.json` on disk, **re-read from disk**, FD recomputed | moved **`3.7655000000086147e+00`** against a predicted **`3.7654999999999998e+00`** — agreement to **`2.3e-12`** relative |
| **C4** non-emptiness **by count, printed** | usable FD steps found on disk | **6 of 6**, registered minimum 4 |
| **C5** δ_repeat | two identical `run_model` runs at the unperturbed DV | **`0.000000e+00`** — `2.8462869282732759e+03` twice, to the last digit |

**C3 exists because C2 does not cover it.** C2 proves the *solver* responds to a perturbation.
It says nothing about whether **this grader's FD arithmetic** responds — a different reader, and
the one that actually produces the graded number. **A zero from a reader not shown able to see a
non-zero is not evidence, and there are two readers here.**

**Every control's FAILURE path was walked before the arm ran.** `d10f_grade.py --selftest` builds
**eleven** synthetic run trees and **all eleven flip the verdict as registered** — including a
**deliberately blinded reader** for C3, which is the one control whose failure path is otherwise
never exercised by a passing run. **A selftest that has never been shown able to fail is not a
selftest.**

`scripts/check_grader_self_blindness.py`: **clean on both probes.** **That is NOT a proof of
correctness and is not offered as one** — probe B fires on `os.path.join` and is silent on
`pathlib` and f-strings (commit `3dc99590`).

---

## 5. WHY `4.4e-08` IS NOT AUTOMATICALLY A CLAIM ABOUT THE HARNESS — AND WHERE THAT ARGUMENT STOPS

An agreement at `4.4e-08` is four to six orders tighter than anything else in this family, and a
number that good deserves suspicion rather than celebration. `VERIFICATION_CHARTER.md` §7 step 4
puts a **2.5–5 %** floor on vector-relative FD error on this stack and warns that *"a number
below that is a claim about the harness."*

**`DAFOAM_CHARTER.md` §2 records, in its own words, that that floor is the wrong instrument
here:** it *"is calibrated on shape derivatives through IDWarp; a per-cell field DV has no mesh
warp in its chain at all."* **`patchV` is a `patchVelocity` DV — a boundary condition. There is
no IDWarp, no FFD and no mesh warp anywhere in this derivative's chain.** The charter makes that
distinction explicitly so that the S1 field-inversion numbers (0.085 %, 0.032 %, 0.0211 %) are
not read as accusations, and the same reasoning applies here a fortiori.

**Three independent facts make the tightness expected rather than surprising:**

1. **δ_repeat is EXACTLY zero.** A steady np=1 solve converged to `primalMinResTol 1.0e-8` is
   bit-deterministic on this box, measured, twice. There is no stochastic floor to hide behind.
2. **The V-shape (§3) is real.** The error rises on **both** sides of `s3` with the right
   scalings. A spuriously tight number produced by the FD and the adjoint sharing a linearisation
   would be flat across `h`, not V-shaped, because it would not carry a truncation term at all.
3. **`HFX(+h)` and `HFX(−h)` are visibly independent primal solves** whose spread tracks `h`
   correctly across four and a half decades.

**WHERE THE ARGUMENT STOPS, STATED PLAINLY.** All three facts are consistency arguments. **None
of them is an independent measurement of the gradient**, and this arm bought no such measurement:
§6 names the forward-AD reference it did not reach for. **An adjoint agreeing with its own finite
difference proves the linearisation is consistent with the primal. It does not prove the primal
is right, and this record claims nothing about the physical correctness of `HFX`.**

---

## 6. WHAT THIS ARM DOES **NOT** ESTABLISH

Written in the pre-registration **before** the data and repeated here unchanged:

- **Nothing about D10 at its own scale** — the substrate is a 720-cell 2D heated channel, not a
  U-bend, not CHT, not `DAHeatTransferFoam`.
- **Nothing about `patchV[1]`**, the flow-angle component (adjoint `−3.7575031648e+01`), beyond
  the bit-for-bit identity check. Only component **0** has a table.
- **Nothing about any np other than 1**, and nothing about any decomposition. Every stage ran at
  np=1, `numberOfSubdomains 1`, so the parallel-determinism question is **answered rather than
  left blank** and core-min = wall-min. **An FD reference is part of a configuration, not a
  property of a case** (`DAFOAM_CHARTER.md` §5) — this number is not carried to any other np.
- **NOTHING ABOUT THE PATCHED TOOLCHAIN. THE PATCHED ROW IS UNBOUGHT AND IS NAMED AS UNBOUGHT**
  (`DAFOAM_CHARTER.md` §1: a DAFoam verdict is two rows or it is not a verdict about DAFoam).
  **Consequence, stated rather than implied: this `PASS` is a verdict about the SHIPPED image
  `sha256:9d45679d…f07fc` and nothing else, and a reader may not carry it to
  `dafoam-idwarp-rot:v1` or any other build.** The mitigating argument — a `patchVelocity` DV has
  no IDWarp in its chain, so the patch class that separates the two rows is absent from this
  derivative — is **an argument, not a measurement**, and is labelled as one.
- **NO FORWARD-AD OR COMPLEX-STEP REFERENCE WAS REACHED FOR**, and `DAFOAM_CHARTER.md` §2 requires
  a record to say so and why. The images ship `libDASolverADF.so`. **This arm did not use it**,
  because it exists to satisfy the FD clause at the cost of one pair and an ADF reference is a
  separate instrument with its own pre-registration. Kenway et al. (PAS 2019) §5.1 reach **10
  digits** against a non-FD reference and explicitly decline FD as one — **so the ceiling on what
  this table can prove is real, and it is named rather than hidden.**

---

## 7. COST — ACTUAL vs PREDICTED (`CLAUDE.md` rule 12)

| | |
|---|---|
| **predicted** | **1.9339 core-min** (17 containers, from D10-P′'s measured stages) |
| **actual gross** | **1.7501 core-min** — 16 solver stages summing 1.7334 + mesh 0.0167 |
| **ratio actual/predicted** | **0.905×** |
| runaway guard | **8.0 core-min**; spend was **0.219×** of it; **the guard never fired** |
| **derived dollars** | **$0.001496** at $0.0513/core-h, c7a.4xlarge, reported-by-owner — **DERIVED, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5: the box cannot read its own billing) |
| **waste** | **0.000 core-min.** Every one of the 16 stages returned `rc=0`, `OOMKilled false`, and produced a graded artifact. No stage was re-bought. |

**Attribution of the 9.5 % gap: MISPREDICTION, and it is a small one in the good direction.**
The prediction used D10-P′'s `plant`/`clean` anchor of 0.1167 core-min (7 s) for `run_model`;
the measured stages came in at **6 s** for 14 of 16 and 7 s for one, with a single 13 s outlier
(the `base` `compute_totals`, which carries the adjoint). **No contention penalty appeared, and
no waste is absorbed into that ratio** (`COMPUTE_BUDGET_CHARTER.md` §6): the waste line is
independently zero.

**This confirms the probe report's §9 lesson 3 for a third time: a prediction anchored on the
same stages of the same case on the same box lands within ~30 %, and here within 10 %.**

**CONTENTION IS NOT CLAIMED TO BE ZERO.** Peer lanes were live on this box throughout — three
`buoyantBoussinesqSimpleFoam` ranks at 99.9 % CPU and a load average near 6 at launch.
`--bind-to none` was carried on every stage (it avoided the measured 3.99× CPU-0 collision), but
**avoiding a known mechanism is not measuring the residual**, and **no uncontended control was
bought by this arm. Residual contention in these figures is UNMEASURED.**

Calibration row: **C-85** in `docs/COST_CALIBRATION.md`.

---

## 8. ARTIFACTS — every number above cites one still on disk

Run root **`/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D10F/`** (27 MB, outside
git per `docs/LOCATIONS.md`).

- `ledger.txt` — per-stage `rc`, `wall_s`, `core_min`, `docker inspect (exit, OOMKilled)`, the
  asserted image id, and the plant landing line.
- `GRADE_OUTPUT.txt` — the frozen comparator's full output, archived.
- `base/`, `rep0/`, `rep1/`, `plant/`, `fdp_s1..s6/`, `fdm_s1..s6/` — each with its own JSON and
  its own container log plus `.ok` sentinel.
- Toolchain, **asserted by the launcher before a single core-minute was spent**:
  `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`.

**A number whose artifact is gone is not a result. None of these is gone.**
