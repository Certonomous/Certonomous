# D12-F′ — PRE-REGISTRATION — the finite-difference table for the D12 probe's UNSTEADY adjoint

**Version 1.0. FROZEN.** Dated **2026-08-25**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.

**NOTHING IN THIS ARM IS FILED, SENT, UPLOADED, REGISTERED, POSTED OR COMMENTED**
(`CLAUDE.md` rule 7). Sending is Sanaa's decision alone.

---

## 0. THE AMENDMENT CONDITION, AND HOW IT WAS CHECKED

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D12F` DOES NOT EXIST.**

**How it was checked:** `test -e /home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D12F`
returned **false** at **2026-08-25T21:24:42Z**, immediately before this document was
written. State at that moment: **DOES_NOT_EXIST**.

`d12f_stage_and_run.sh` **refuses with exit 6** if that path exists when it starts, so the
condition is enforced by the instrument, not only asserted here. **A guard that refuses a case
whose run directory already exists is the guard working.** After the first container starts this
document's gates are **CLOSED**; changes land only as dated addenda that cannot alter a gate, a
threshold, a cap or a label.

---

## 1. WHY THIS ARM EXISTS — AND THE COUNTER-ARGUMENT, ON THE RECORD

**`DAFOAM_CHARTER.md` §2:** *"No DAFoam gradient enters a record, a report or an optimisation
without a finite-difference table beside it."*

The D12 probe reported `max |d(obj)/d(shape)| = 1.1622935280e-01` — obj = time-averaged CD over
a 5-step window — and **has no FD table beside it**. `PROBE_REPORT_D10_D11_D12.md` §7(b)
flagged this and declined to rule on it.

**THE COUNTER-ARGUMENT, RECORDED RATHER THAN SUPPRESSED:** D12's verdict is `GATE REACHED` on
**reachability**, and its RESULTS.md §4 disclaims *"nothing about the correctness, accuracy, FD
agreement or sign"* of the number. On that reading the gradient is an existence witness and §2
may genuinely not bite. **The supervisor ruled the other way; this lane agrees**, because a
disclaimer reads to a later reader exactly like a complete control and records get quoted
onward stripped of their caveats — a mechanism this family has been burned by twice.

### THE SCOPE FENCE — TIGHT, AND BINDING

**D12's reachability verdict DOES NOT MOVE.** `GATE REACHED` stands for arm E′/the D12 probe
whatever this arm returns. This arm converts a disclaimed gradient into a verified or a refuted
one and **does nothing else**. It is **not** a re-grade and **cannot become one**.

---

## 2. TWO COMPONENTS ARE BOUGHT, NOT ONE — AND THE SECOND IS THE INTERESTING ONE

| idx | adjoint `d(obj)/d(shape[idx])` | why it is bought |
|---|---|---|
| **3** | **−1.1622935280e-01** | the **headline** `max \|·\|` component — the number §2 actually bites on |
| **0** | **+3.5023163495e-02** | **because the probe's own PLANT STAGE is already a one-sided FD point on this component, and it DISAGREES** |

**The disagreement, computed from committed artifacts before any compute in this arm:**
`obj_plant = 8.9960310069e-02` at `shape[0] = 1.234e-03`, `obj_base = 8.9903939104e-02`, so
the **one-sided forward difference is `4.5682e-02`** against an adjoint of `3.5023e-02` —
a **≈ 30 % gap**.

**That gap proves nothing on its own.** A one-sided difference at a single, comparatively large
step is **exactly as consistent with curvature** (a one-sided difference carries an
`O(h·f'')` truncation error that a central difference cancels) **as it is with a wrong
gradient.** The only instrument that separates those two is a **central difference over a step
sweep** — which is precisely what this arm runs.

**Buying idx 3 alone would have left that gap sitting unexamined beside a fresh FD table, which
is worse than leaving it beside a disclaimer**: the table would look like the question had been
answered. The second component is bought for that reason and the reason is recorded here,
before the data.

`DAFOAM_CHARTER.md` §3: *"a flat curve is per component or it is not flat."* **Every plateau,
every reference step and every relative error in this arm is PER COMPONENT. No aggregate over
the two is formed, quoted or implied anywhere in the grader.**

---

## 3. THE CASE, THE TOOLCHAIN, AND THE DECOMPOSITION

**The case is the probe's case**: the upstream DAFoam `Cylinder` tutorial (2,450 cells), the
probe's **own committed** `d12_controlDict_probe` (`endTime 0.05`, `deltaT 1e-2`, **5 steps**,
cold start from `0_orig`), `fvSchemes_pimple`, `fvSolution_pimple`. The controlDict is copied
from the probe's directory, **not re-authored**, and the launcher asserts `endTime 0.05` before
spending anything.

**Toolchain, BY IMAGE ID, never by tag** (`DAFOAM_CHARTER.md` §11):

> `dafoam/opt-packages` — **`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`**

Asserted by the launcher before a single core-minute is spent.

**np = 1 on every stage, `numberOfSubdomains 1`, so core-min = wall-min and the
parallel-determinism question is ANSWERED rather than left blank.** No claim is made about any
other np, and none may be carried to one (`DAFOAM_CHARTER.md` §5).

### THE TWO-ROW SHIPPED/PATCHED RULE — THE PATCHED ROW IS **UNBOUGHT**, WITH ITS CONSEQUENCE

- **SHIPPED**: `dafoam/opt-packages` at the id above. **BOUGHT.**
- **PATCHED**: `dafoam-idwarp-rot:v1` (`2927768a16ac`), `dafoam-subpclu:v1/v2`,
  `dafoam-kspopts:v1`. **NOT BOUGHT, AND NAMED HERE AS UNBOUGHT.**

**The consequence, stated rather than implied — and here it is SHARPER than for D10-F′.** The
D12 DV is a **shape** DV: `OM_DVGEOCOMP` → pyGeo FFD → **IDWarp volume warp** → `aero_vol_coords`.
**The IDWarp patch class is therefore squarely IN this derivative's chain**, unlike D10-F′'s
`patchVelocity` DV where it is absent. `ROOTCAUSE_getRotationMatrix3d.md` and
`UPSTREAM_BUG_REPORT_mesh_warpDeriv.md` (**both NOT FILED**) describe a defect class in exactly
that chain. **So a reader may NOT carry any verdict this arm renders to the patched build, and
the gap is not academic here.**

**Why the row is unbought anyway:** the gradient under test — the probe's `dobj_dshape` — was
itself produced on the shipped image only. A patched row here would be an FD table for a
gradient nobody has computed. **Buying the patched row means re-running the probe's
`compute_totals` on the patched image first, which is a different arm with its own
pre-registration.** It is named as outstanding, not quietly skipped.

---

## 4. THE INSTRUMENTS, FROZEN BY MD5 AT THIS COMMIT

| file | md5 | role |
|---|---|---|
| `d12f_run_script.py` | `531615f37dd299cd44cc1952c7e52a9b` | the run script |
| `d12f_grade.py` | `3331c66408c2e680ec52d26a9f1a002e` | **the grading path** |
| `d12f_stage_and_run.sh` | `174d06c1737446ca677db21c2ba5c32c` | the launcher |

**The grading path is fixed at this commit**; hash it against the committed blob before
believing anything it prints (`CLAUDE.md` rule 2).

### THE RUN SCRIPT IS A FOUR-DELTA DERIVATIVE, AND THE DELTAS ARE REPRODUCIBLE

Generated from the frozen `d12_run_script.py` (md5 `a57676f6a1003d7d483cb2d799081512`) by
**exactly four explicit substitutions**:

1. **the module docstring**;
2. **`-shapeIdx`** (int) selecting which component carries the value, with a **refusal** if it
   is negative or ≥ `nShapes`;
3. **`-shapeSign`** — the literal **word** `plus` or `minus` — and **`-shapeMag`**, a
   **non-negative** float, with a refusal otherwise. **A NEGATIVE FD STEP IS NEVER WRITTEN ON A
   COMMAND LINE.** `argparse` reads a leading `-` on a value as an option flag, and that exact
   mechanism is a **measured** 0.7167 core-min of waste in this family (D11-O′). The sign and
   magnitude are combined **inside** the script;
4. the single hard-wired assignment into component 0 becomes an assignment into component
   `shapeIdx` of the signed value, plus `shapeIdx`/`shapeSign`/`shapeMag`/`shapeValue`
   recorded in the output JSON.

**The generator ASSERTED, and the assertion held, that `daOptions` AND `meshOptions` are
BYTE-IDENTICAL between the two files** (1,879 bytes) — so `normalizeStates`, the
`unsteadyAdjoint` block (`timeAccurate`, `reduceIO: True`, `PCMatUpdateInterval 1`) and every
`adjEqnOption` are pinned across every FD step.

**Backward compatibility is exact:** at the defaults (`-shapeIdx 0 -shapeSign plus -shapeMag 0.0`)
`shape0` is all zeros — the probe's own baseline. `d12_run_script.py` **is not edited** (rule 6).

---

## 5. THE STEP SWEEP — PROVED, NOT ASSERTED — AND δ_repeat COMES FIRST

**Registered steps on `shape[idx]` (baseline 0.0), central differences, run for BOTH components:**

| tag | h |
|---|---|
| `s1` | 1.0e-6 |
| `s2` | 1.0e-5 |
| `s3` | 1.0e-4 |
| `s4` | 1.0e-3 |
| `s5` | 1.0e-2 |

**Plateau definition, frozen:** adjacent central-FD values within **1.0e-2** relative; a plateau
is **≥ 3 consecutive** steps. **Reference step, FIXED BEFORE THE DATA:** the middle step of the
longest consecutive run, ties broken toward the **smaller** step. **No plateau on a component →
that component is `NOT A RESULT`.**

### δ_repeat IS MEASURED IN THIS ARM, AND ITS SCOPE IS FENCED IN ADVANCE

`rep0` and `rep1` are two runs at the unperturbed DV. **N-D15 at its worst is a time-averaged
objective on a shedding flow: an FD step sized without knowing the run-to-run scatter is a step
sized against nothing.** So δ_repeat is measured and printed beside the FD signal at the
reference step.

**AND ITS SCOPE IS FENCED HERE SO IT CANNOT BE QUOTED ONWARD STRIPPED OF THE FENCE:** this window
is **5 steps from a COLD START at np=1**, **not** a developed vortex-shedding limit cycle.
**A δ_repeat measured here is a statement about THIS window and IS NOT the δ_repeat
D12-proper's 300-step time-average needs.** Limit-cycle phase noise is a different quantity on a
different flow, and **D12-proper must buy its own before sizing any FD step.** The grader prints
this fence next to the number.

---

## 6. THE GATES — every threshold numeric, every label fixed here

**The statistic is NAMED** (`DAFOAM_CHARTER.md` §2): the **single-component relative error**
`|D_adj − D_fd| / |D_fd|` at that component's reference step. **NOT** the vector-relative error,
**NOT** the DAFoam papers' per-component average. Comparing the three is forbidden.

| gate | what it reads | threshold | label if it fails |
|---|---|---|---|
| **G12F-C1** instrument identity | `base/d12f_base.json`: all **four** `dobj_dshape` components, `obj`, and `nShapes` vs the committed probe values | **BIT-FOR-BIT; threshold is ZERO** | **REFUSE, exit 2** → `NOT A RESULT` |
| **G12F-C2** planted zero, physical | `plant/d12f_plant.json` vs base, `shape[0] = 1.234e-03` | response **≥ 1.0e-9** relative | **REFUSE, exit 2** → `NOT A RESULT` |
| **G12F-C3** planted zero, reader-level, **PER COMPONENT** | a known **+3.719e-04** written into a **COPY** of an FD JSON on disk, **RE-READ FROM DISK**, FD recomputed | movement within **1.0e-9** relative of the analytic prediction | **REFUSE, exit 2** → `NOT A RESULT` |
| **G12F-C4** non-emptiness **BY COUNT, PRINTED, PER COMPONENT** | usable FD steps found on disk | **≥ 4** of 5, **for each component** | **REFUSE, exit 2** → `NOT A RESULT` |
| **G12F-C6** DV read-back | every FD stage's own `shape` vector, read from its JSON — never assumed from the directory name | `shape[idx] == ±h` to 1e-15 relative **and every OTHER component EXACTLY 0.0** | **REFUSE, exit 2** → `NOT A RESULT` |
| **G12F-C5** δ_repeat | `rep0` vs `rep1` | **MEASURED AND PRINTED; no threshold** | n/a — reported, not gated |
| **G12F-P** plateau, per component | adjacent central-FD values | longest run **≥ 3** | that component `NOT A RESULT` |
| **G12F-G** THE GATE, per component | `\|D_adj − D_fd\|/\|D_fd\|` at the reference step | **≤ 5.0e-2 → `PASS`** | see mapping |

**G12F-C6 exists because a shape FD that leaked a non-zero into another component would not be
a partial derivative at all**, and nothing else in the chain would notice.

### THE VERDICT MAPPING, FROZEN

| table band (§2) | condition | **component verdict** |
|---|---|---|
| PASS | err ≤ 5.0e-2 | **`PASS`** |
| CONDITIONAL | 5.0e-2 < err ≤ 1.5e-1 | **`GATE FAIL`** — outside the pre-registered PASS band, breakdown printed |
| FAIL | err > 1.5e-1, **or any sign flip regardless of magnitude** | **`GATE FAIL`** |
| — | any control refused, or no plateau | **`NOT A RESULT`** |

**THE ARM VERDICT IS THE WORST PER-COMPONENT VERDICT** (`NOT A RESULT` < `GATE FAIL` < `PASS`).
**A table with a failing component is a failing table; an aggregate never rescues a component.**

**A `GATE FAIL` here is a real possible outcome and would be a finding, not a failure of the
arm** — the 30 % one-sided gap on component 0 in §2 is a live reason to expect one.

### WHY THE COMPARATOR REFUSES RATHER THAN DEGRADES

`d12f_grade.py` **exits 2** on any failed control. It never drops a component, never widens a
tolerance, never reports over a short set. Its `--selftest` builds **fourteen** synthetic run
trees — including a **deliberately blinded reader** for C3, a **leaked off-component**, and
single-component 40 % mutants proving the worst-of rule bites from either side — and **every one
flips the verdict as registered.**

---

## 7. THE COMPLETION RULE, AND WHAT THIS ARM CAN AND CANNOT CARRY

| limb (`CLAUDE.md` rule 4) | carried? | how |
|---|---|---|
| `rc = 0` | **YES** | `docker inspect '{{.State.ExitCode}} {{.State.OOMKilled}}'`, no `--rm` |
| fields present | **YES, as the graded artifact** | every stage's JSON must exist with `status: COMPLETE` |
| cold start / age guard | **YES** | fresh copy per stage; launcher **refuses** if `0.01`, `0.05` or `processor*` exists; run-root guard refuses a pre-existing root |
| last time == `endTime` | **PARTIALLY — and named** | `endTime 0.05` is asserted in the controlDict **before** launch; the probe verified the `0.05` directory exists. This arm grades from the **driver's JSON**, and a driver that did not reach `endTime` raises and returns non-zero rc. |
| an `End` line, `ExecutionTime` count == `endTime` | **NO — NAMED AS NOT CARRIED** | these are OpenFOAM-solver-log limbs; these stages are OpenMDAO/DAFoam driver invocations. **A completion rule quoted with limbs silently dropped is worse than one quoted honestly.** |

---

## 8. COST — PREDICTED, WITH A NUMERIC STOP THRESHOLD

**Cost constraints are LIFTED (Sanaa, 2026-08-25). The cap is a RUNAWAY GUARD reported to the
supervisor, not a budget rigor is trimmed to fit.**

**Prediction, anchored on MEASURED stages of THE SAME CASE ON THIS BOX:**

| stage class | count | measured anchor | core-min |
|---|---|---|---|
| mesh (pyHyp → renumberMesh) | 1 | D12 probe mesh ≈ 0.037 | 0.0370 |
| `compute_totals` (primal + unsteady adjoint) | 1 | D12 `base` = 0.4833 | 0.4833 |
| `run_model` (primal only) | 23 | D12 `plant` 0.1667 / `clean` 0.1500, take 0.1667 | 3.8341 |
| **PREDICTED TOTAL** | **25 containers** | | **4.3544 core-min** |

**Derived dollars: $0.003723** at $0.0513/core-h, c7a.4xlarge, **reported-by-owner**.
**DERIVED, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5).

> **NUMERIC STOP THRESHOLD: `CAP_CORE_MIN = 15.0` core-min**, cumulative over every container,
> mesh included, evaluated **before each stage**; on a trip the stage is **not launched** and
> `RUNAWAY GUARD TRIPPED` is written to `ledger.txt`. **An overrun stops the arm; it does not
> get a new number.** 15.0 is **3.45×** the prediction — loose on purpose, because a guard set at
> the prediction fires on ordinary contention.

**MEMORY.** The probe measured **peak RSS 1.3269 GiB** after the adjoint at this window. The
container limit is **12 GiB, `--memory == --memory-swap`, `--oom-score-adj=500`** — identical to
the probe, so the container configuration is not a variable between them. **A cgroup limit is a
limit, not a reservation**: it consumes nothing. The standing hold — **never drop MemAvailable
below 12 GiB** — is checked with `free -g` immediately before launch and the reading is recorded
in RESULTS.

**Contention will NOT be claimed to be zero.** `--bind-to none` is carried on every stage;
**avoiding a known mechanism is not measuring the residual**, and **no uncontended control is
bought.** RESULTS will say so.

**Calibration row owed in `docs/COST_CALIBRATION.md`** at completion, id derived tolerantly by
hand against HEAD inside the committing invocation (`append_record.py` hands out colliding ids
and is not used).

---

## 9. WHAT THIS ARM WILL NOT ESTABLISH — WRITTEN BEFORE THE DATA

- **Nothing about a developed limit cycle.** 5 steps, cold start. `obj = 0.0899` **is not a
  physical drag coefficient and is never to be quoted as one.**
- **Nothing about D12-proper's δ_repeat**, its window length, or its checkpoint envelope at 300
  steps. §5 fences this explicitly.
- **Nothing about components 1 and 2** beyond the bit-for-bit identity check.
- **Nothing about any np other than 1**, and nothing about any decomposition.
- **Nothing about the patched toolchain** — §3 names the row unbought and states a consequence
  that is *sharper* here than for D10-F′ because IDWarp **is** in this chain.
- **Nothing about a forward-AD or complex-step reference.** `DAFOAM_CHARTER.md` §2 requires a
  record to state that it did not reach for one and why: **this arm did not reach for
  `libDASolverADF.so`**, because standing up an ADF reference for an *unsteady* adjoint is a
  separate instrument with its own pre-registration. Kenway et al. (PAS 2019) §5.1 explicitly
  **decline** finite differences as a reference and reach 10 digits with a non-FD one, so the
  ceiling on what an FD table can prove here is real and is named.
- **Nothing about `reduceIO: False`**, which moves the same checkpoint state to disk.
