# D10-F′ — PRE-REGISTRATION — the finite-difference table for the D10-P′ adjoint gradient

**Version 1.0. FROZEN.** Dated **2026-08-25**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.

**NOTHING IN THIS ARM IS FILED, SENT, UPLOADED, REGISTERED, POSTED OR COMMENTED**
(`CLAUDE.md` rule 7). Sending is Sanaa's decision alone.

---

## 0. THE AMENDMENT CONDITION, AND HOW IT WAS CHECKED

`CLAUDE.md` rule 2: before first compute, amendments are legal **and must state the
condition and how it was checked**. The condition is:

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D10F` DOES NOT EXIST.**

**How it was checked:** `test -e /home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D10F`
returned **false** at **2026-08-25T21:23:08Z**, immediately before this document was
written. State at that moment: **DOES_NOT_EXIST**.

The launcher `d10f_stage_and_run.sh` **refuses with exit 6** if that path exists when it
starts, so the condition is enforced by the instrument and not only asserted here. **A guard
that refuses a case whose run directory already exists is the guard working.** It is never
disabled, edited or worked around, and a completed stage is never deleted to get past it.

After the first container starts, this document's gates are **CLOSED**. Changes land only as
dated addenda that cannot alter a gate, a threshold, a cap or a label.

---

## 1. WHY THIS ARM EXISTS — AND THE COUNTER-ARGUMENT, ON THE RECORD

**`DAFOAM_CHARTER.md` §2, the bright line:** *"No DAFoam gradient enters a record, a report
or an optimisation without a finite-difference table beside it."*

D10-P′ reported `max |d(HFX)/d(patchV)| = 1.9771502962e+02` and **has no FD table beside it**.
`PROBE_REPORT_D10_D11_D12.md` §7(b) flagged this and declined to rule on it.

**THE COUNTER-ARGUMENT IS REAL AND IS RECORDED HERE RATHER THAN SUPPRESSED.** D10-P′'s verdict
is `GATE REACHED` on **reachability**; its RESULTS.md §4 explicitly disclaims *"nothing about
the correctness, accuracy or sign"* of the gradient. On that reading the gradient is an
existence witness, not a gradient result, and §2 may genuinely not bite.

**The supervisor ruled the other way and this lane agrees, for a reason the lane can state
independently:** a disclaimer reads to a later reader exactly like a complete control, and
records get quoted onward stripped of their caveats. This family has been burned by that exact
mechanism twice — `d3_grade.py` returned `PASS` at 0.0000 % over an **empty component set**
while the same file refused an unseen plant citing rule 3 by name, and D4's supplement ran 21
units and never once mutated the FD table. **When the strict reading costs one FD pair and the
loose reading costs permanent ambiguity in the gate that is this family's whole product, you
buy the pair.**

### THE SCOPE FENCE — TIGHT, AND BINDING ON THIS DOCUMENT

**D10-P′'s reachability verdict DOES NOT MOVE.** `GATE REACHED` stands for arm P′ whatever
this arm returns. This arm converts a disclaimed gradient into a verified or a refuted one and
**does nothing else**. It is **not** a re-grade of D10-P′, **not** a re-fire of a settled
pre-registration, and **cannot become one**. No gate below can change D10-P′'s label.

---

## 2. THE CASE, THE TOOLCHAIN, AND THE DECOMPOSITION

**The case is D10-P′'s own case, not a copy.** `SRC` points at
`cases/dafoam/ladder-a/A5/curriculum_D10_probe_Pprime/d10p_case`. An FD table is a table about
D10-P′'s gradient only if it ran on D10-P′'s case; pointing at the one directory makes that
true by construction rather than by a hash somebody has to remember to check.

**Toolchain, BY IMAGE ID, never by tag** (`DAFOAM_CHARTER.md` §11):

> `dafoam/opt-packages` — **`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`**

The launcher **asserts this id before spending a single core-minute** and aborts otherwise.
This is the same image as all nine probe arms.

**np = 1 on every stage, `numberOfSubdomains 1`, so core-min = wall-min and the
parallel-determinism question is ANSWERED rather than left blank** (`DAFOAM_CHARTER.md` §5:
serial before parallel; a gradient verified at one np is a statement about that np and is never
carried to another). **This arm makes no claim about any other np.**

### THE TWO-ROW SHIPPED/PATCHED RULE — THE PATCHED ROW IS **UNBOUGHT**, AND HERE IS ITS CONSEQUENCE

`DAFOAM_CHARTER.md` §1: *"a DAFoam verdict is two rows — shipped and patched — or it is not a
verdict about DAFoam."* **This arm buys the SHIPPED row only.**

- **SHIPPED**: `dafoam/opt-packages` at the id above. **BOUGHT.**
- **PATCHED**: `dafoam-idwarp-rot:v1` (`2927768a16ac`) and the `subpclu`/`kspopts` builds.
  **NOT BOUGHT, AND NAMED HERE AS UNBOUGHT.**

**The consequence, stated rather than implied:** whatever verdict §5 renders is a verdict about
**the shipped toolchain at this image id and nothing else.** If the patched IDWarp changes the
gradient — and `W4_IDX16_IS_THE_REFERENCE.md` records that A5's stored FD reference was cited
from a run whose `PYTHONPATH` pointed at the patched IDWarp, so this family has already made
exactly that mistake in the other direction — this arm would not see it. **A reader may not
carry this number to the patched build.** The reason the row is unbought is that **D10-P′'s
gradient, the thing under test, was itself produced on the shipped image only**; a patched row
here would be an FD table for a gradient nobody has computed.

**The mitigation this arm CAN claim:** `d(HFX)/d(patchV)` is a **boundary-condition** derivative.
Per `S1_FIML_FIELD_INVERSION.md` §1's instrument distinction, a `patchVelocity` DV has **no mesh
warp in its chain**, so the IDWarp patch class — which is what separates shipped from patched
here — is not in this derivative's path at all. **That is an argument, not a measurement, and it
is labelled as one.**

---

## 3. THE INSTRUMENTS, FROZEN BY MD5 AT THIS COMMIT

| file | md5 | role |
|---|---|---|
| `d10f_run_script.py` | `3d56e4549f81ffe49af10259387a6885` | the run script |
| `d10f_grade.py` | `7aaf2c67f1f63910238ab378aa7ac873` | **the grading path** |
| `d10f_stage_and_run.sh` | `7f14d55fa2fd7fd33042db71a4f8596e` | the launcher |

**The grading path is fixed at this commit.** Before believing anything `d10f_grade.py` prints,
hash it against the committed blob (`CLAUDE.md` rule 2).

### THE RUN SCRIPT IS A THREE-DELTA DERIVATIVE, AND THE DELTAS ARE REPRODUCIBLE

`d10f_run_script.py` was generated from the frozen `d10p_run_script.py`
(md5 `1d04151dba68061fce2c34b35f9fcb4e`) by **exactly three explicit substitutions**:

1. **the module docstring**;
2. **a `-patchV0` argument**, `type=float`, default `10.0`, with a **refusal** if it is
   non-positive. It is **positive-only by construction**: every registered step gives
   `10.0 ± h > 0`, so **no negative number is ever written on a command line**. `argparse`
   reading a leading `-` on a value as an option flag is a **measured** 0.7167 core-min of
   waste in this family (D11-O′);
3. `val=np.array([U0, aoa0])` → `val=np.array([args.patchV0, aoa0])`, plus recording
   `patchV0_arg` in the output JSON.

**The generator ASSERTED, and the assertion held, that the `daOptions` block is BYTE-IDENTICAL
between the two files** (1,595 bytes). That matters for one specific reason: `normalizeStates["U"]`
stays pinned at the **literal 10.0** across every FD step. **A normalisation that moved with the
step would make the difference quotient measure the normalisation as well as the flow.**

`d10p_run_script.py` **is not edited**. It is read and a new file is written (rule 6).

---

## 4. THE STEP SWEEP — THE STEP IS *PROVED* TO LIE IN THE PLATEAU, NOT ASSERTED

`DAFOAM_CHARTER.md` §3: *"The step is proved to lie in the plateau by a sweep, and a flat curve
is per component or it is not flat."* This arm sweeps **one component**, so it is per component
by construction.

**Registered steps on `patchV[0]` (baseline 10.0 m/s), central differences:**

| tag | h (m/s) | h/DV |
|---|---|---|
| `s1` | 1.0e-5 | 1e-6 |
| `s2` | 1.0e-4 | 1e-5 |
| `s3` | 1.0e-3 | 1e-4 |
| `s4` | 1.0e-2 | 1e-3 |
| `s5` | 1.0e-1 | 1e-2 |
| `s6` | 5.0e-1 | 5e-2 |

**Plateau definition, frozen:** adjacent central-FD values `D_i`, `D_{i+1}` are *in plateau* iff
`|D_i − D_{i+1}| / |D_{i+1}| ≤ 1.0e-2`. A **plateau** is a run of **≥ 3 consecutive** steps.

**Reference step, FIXED BEFORE THE DATA:** the **middle step of the longest consecutive plateau
run**, ties broken toward the **smaller** step. This is a deterministic rule computable without
seeing a number, which is the point: it cannot be chosen to fit the answer.

**If no run of ≥ 3 consecutive steps exists, the arm is `NOT A RESULT`.** A step not proved to
lie in a plateau is not a proved step, and the FD table would then not be admissible evidence
about the adjoint either way.

---

## 5. THE GATES — every threshold numeric, every label fixed here

**The statistic is NAMED** (`DAFOAM_CHARTER.md` §2 requires this): the **single-component
relative error** `|D_adj − D_fd| / |D_fd|` at the reference step. It is **NOT** the
vector-relative error this ladder's multi-component records quote, and **NOT** the
per-component average the DAFoam papers quote. **Those three are different statistics and this
document forbids comparing them.**

| gate | what it reads | threshold | label if it fails |
|---|---|---|---|
| **G10F-C1** instrument identity | `base/d10f_base.json` `dHFX_dpatchV` and `HFX` vs the committed D10-P′ values | **BIT-FOR-BIT; threshold is ZERO, not a tolerance** | **REFUSE, exit 2** → `NOT A RESULT` |
| **G10F-C2** planted zero, physical | `plant/d10f_plant.json` vs base, +1.234 K on the lowerWall `fixedValue` | response **≥ 1.0e-6** relative | **REFUSE, exit 2** → `NOT A RESULT` |
| **G10F-C3** planted zero, reader-level | a known **+7.531e-02** written into a **COPY** of an FD JSON on disk, **RE-READ FROM DISK**, FD recomputed | recomputed movement within **1.0e-9** relative of the analytic prediction | **REFUSE, exit 2** → `NOT A RESULT` |
| **G10F-C4** non-emptiness **BY COUNT, PRINTED** | usable FD steps found on disk | **≥ 4** of 6 | **REFUSE, exit 2** → `NOT A RESULT` |
| **G10F-C5** δ_repeat | `rep0` vs `rep1`, same DV, two runs | **MEASURED AND PRINTED; no threshold** | n/a — it is reported, not gated |
| **G10F-P** plateau | adjacent central-FD values | longest run **≥ 3** consecutive steps | `NOT A RESULT` |
| **G10F-G** THE GATE | `\|D_adj − D_fd\|/\|D_fd\|` at the reference step | **≤ 5.0e-2 → `PASS`** | see mapping |

### THE VERDICT MAPPING, FROZEN SO IT CANNOT BE CHOSEN AFTER THE NUMBER IS SEEN

`DAFOAM_CHARTER.md` §2 grades the **table** in three bands; `CLAUDE.md` rule 1 fixes the
**verdict** vocabulary, which has no "CONDITIONAL". The mapping is therefore stated here:

| table band (§2) | condition | **arm verdict** (rule 1 vocabulary) |
|---|---|---|
| PASS | err ≤ 5.0e-2 | **`PASS`** |
| CONDITIONAL | 5.0e-2 < err ≤ 1.5e-1 | **`GATE FAIL`** — outside the pre-registered PASS band, with the per-component breakdown printed |
| FAIL | err > 1.5e-1, **or any sign flip regardless of magnitude** | **`GATE FAIL`** |
| — | any control refused, or no plateau | **`NOT A RESULT`** |

**A `GATE FAIL` here is a real possible outcome and is not a failure of the arm.** It would say
that the adjoint and the finite difference disagree on this component, which is a finding.

### WHY THE COMPARATOR REFUSES RATHER THAN DEGRADES

`d10f_grade.py` **exits 2** on any failed control and prints `VERDICT: NOT A RESULT`. It never
drops a component, never widens a tolerance, and never reports an aggregate over a short set.
Its `--selftest` builds **eleven** synthetic run trees — including a **deliberately blinded
reader** for C3 — and **every one of them flips the verdict as registered**. A selftest that has
never been shown able to fail is not a selftest.

---

## 6. THE COMPLETION RULE, AND WHAT THIS ARM CAN AND CANNOT CARRY

`CLAUDE.md` rule 4 is registered in the limbs this arm can carry, and the limbs it cannot are
**named rather than quietly dropped**:

| limb | carried? | how |
|---|---|---|
| `rc = 0` | **YES** | `docker inspect '{{.State.ExitCode}} {{.State.OOMKilled}}'`, no `--rm`, into `ledger.txt` |
| fields present | **YES, as the graded artifact** | every stage's JSON must exist and carry `status: COMPLETE` or the grader refuses |
| cold start / age guard | **YES** | every stage is a fresh copy; the launcher **refuses** if a time dir or `processor*` exists, and the run root guard refuses a pre-existing root |
| an `End` line, last time == `endTime`, `ExecutionTime` count == `endTime` | **NO — NAMED AS NOT CARRIED** | these are OpenFOAM-solver-log limbs. This arm's stages are **OpenMDAO/DAFoam driver** invocations of a **steady** `DASimpleFoam` whose convergence is governed by `primalMinResTol 1.0e-8`, not by an `endTime` the driver reaches. **A DAFoam `AnalysisError` is a non-zero rc and is caught by the rc limb.** Stating this is the point: a completion rule quoted with limbs silently dropped is worse than one quoted honestly. |

---

## 7. COST — PREDICTED, WITH A NUMERIC STOP THRESHOLD

**Cost constraints are LIFTED (Sanaa, 2026-08-25): no run stops to save compute. The cap below
is a RUNAWAY GUARD reported to the supervisor, not a budget rigor is trimmed to fit.**

**Prediction, anchored on MEASURED stages of THE SAME CASE ON THIS BOX** — the highest-quality
prediction class this family has (probe report §9 lesson 3: measured-stage predictions land
within ~30 % and usually within 12 %; guessed ones were the 0.167× and 0.213× outliers):

| stage class | count | measured anchor | core-min |
|---|---|---|---|
| mesh (`blockMesh`+`checkMesh`) | 1 | D10-P′ mesh container | 0.0167 |
| `compute_totals` (primal + adjoint) | 1 | D10-P′ `base` = 0.1667 | 0.1667 |
| `run_model` (primal only) | 15 | D10-P′ `plant`/`clean` = 0.1167 each | 1.7505 |
| **PREDICTED TOTAL** | **17 containers** | | **1.9339 core-min** |

**Derived dollars: $0.001653** at $0.0513/core-h, c7a.4xlarge, **reported-by-owner**.
**DERIVED, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

> **NUMERIC STOP THRESHOLD: `CAP_CORE_MIN = 8.0` core-min**, cumulative over **every** container
> this arm launches, mesh included. The launcher evaluates it **before each stage** and, on a
> trip, **does not launch that stage** and writes `RUNAWAY GUARD TRIPPED` to `ledger.txt`.
> **An overrun stops the arm; it does not get a new number** (`CLAUDE.md` rule 12).
> 8.0 is **4.14×** the prediction — deliberately loose, because it is a runaway guard and not a
> budget, and a guard set at the prediction would fire on ordinary contention.

**Contention is expected and will NOT be claimed to be zero.** Peer lanes are live on this box.
`--bind-to none` is carried on every stage (it avoided the measured 3.99× CPU-0 collision), but
**avoiding a known mechanism is not measuring the residual**, and **no uncontended control is
bought by this arm.** The RESULTS record will say so.

**Calibration (`CLAUDE.md` rule 12): a row is owed in `docs/COST_CALIBRATION.md` at completion**,
with actual/predicted, the gap attributed, and waste named separately and never absorbed into
the ratio. The id is derived **tolerantly by hand, against HEAD, inside the committing shell
invocation** — `append_record.py` hands out colliding ids and is not used.

---

## 8. WHAT THIS ARM WILL NOT ESTABLISH — WRITTEN BEFORE THE DATA

- **Nothing about D10 at its own scale.** The substrate is a 720-cell 2D heated channel, not a
  U-bend, not CHT, not `DAHeatTransferFoam`.
- **Nothing about `patchV[1]`** (the flow-angle component, adjoint `−3.7575031648e+01`) beyond
  the bit-for-bit identity check. Only component **0** gets a table.
- **Nothing about any np other than 1**, and nothing about any decomposition.
- **Nothing about the patched toolchain** — §2 names that row unbought and states the consequence.
- **Nothing about a forward-AD or complex-step reference.** `DAFOAM_CHARTER.md` §2 requires a
  record to state that it did not reach for one and why: **this arm did not reach for
  `libDASolverADF.so`.** The reason is scope — this arm exists to satisfy the FD clause of §2 at
  the cost of one pair, and standing up an ADF reference is a separate instrument with its own
  pre-registration. **That gap is real and is named, not hidden.**
- **Nothing about the correctness of `HFX` as a physical wall heat flux.** An adjoint agreeing
  with its own finite difference proves the linearisation is consistent with the primal; it does
  not prove the primal is right.
