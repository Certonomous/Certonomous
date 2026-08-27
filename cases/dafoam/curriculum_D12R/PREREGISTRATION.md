# CURRICULUM D12R — UNSTEADY ADJOINT, 2D CYLINDER, TIME-AVERAGED DRAG — PRE-REGISTRATION

**Version 1.0. FROZEN.** Dated **2026-08-25**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.
**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).

---

## 0. WHY THIS ITEM EXISTS, AND WHAT IT SUPERSEDES

Authority: **`cases/dafoam/curriculum_D12/SUPERVISOR_D12_PHASE1_RULINGS.md` §7**, committed
`93966756`, which rules **one re-registration, not four patches**.

**This item SUPERSEDES `cases/dafoam/curriculum_D12/PREREGISTRATION.md`.** That document and
its instruments are **CITED, NEVER REWRITTEN** (rule 6). Its phase 1 verdict — **`NOT A RESULT`**
— **stands on the record**, its run root is preserved byte-for-byte, and **nothing is lost but a
document**: phase 1 produced **zero graded output**.

**Two of the four defects could not be repaired by addendum**, which is why a new item and not
an amendment:

- **Defect 1 was a PIPELINE error, not an instrument error.** `FIELD_B` was taken from a
  **per-step write**, which emits only what `writeControl` selects — a **diagnostic subset**.
  A restart field must carry **full state**. Fixing that changes the stage graph.
- **Defect 3 was in the FROZEN DOCUMENT ITSELF.** §5 froze *"the LAST `average:` value"* as the
  objective reading; the solver prints `average:` on **both** the `CD` and `CL` lines, so the
  registered comparison **could never have passed**. **A pre-registration specifying a quantity
  that cannot produce the registered comparison is not repairable into a correct one by
  addendum** — §2d.1 was cut for a comparator script, and stretching it to rewrite what a
  document says to measure would hollow out rule 2.

## 1. THE AMENDMENT CONDITION, AND HOW IT WAS CHECKED

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-D12R-cylinder-unsteady` DOES NOT EXIST.**

**`test -e` returned false at 2026-08-25T22:44:00Z**, immediately before this document was written;
state at that moment: **DOES_NOT_EXIST**. The launcher **refuses with exit 6** if it exists at phase 1, so the
condition is enforced by the instrument and not merely asserted. After the first container,
gates are **CLOSED**.

---

## 2. WHAT IS MEASURED, AND WHAT IS ALREADY KNOWN

Carried forward from the superseded item's phase 1, which **did** produce sound measurements
before it died:

| quantity | measured | status |
|---|---|---|
| limit cycle | 221 sign changes, p2p **19.40 %** of `\|mean\|`, mean `CD = 0.6563506540` | **established** |
| shedding period | **18.9955 timesteps** | measured; **NOT re-used as a registration** |
| `δ_window` at `W = 300` | **`1.274958e-03`**, `W/period = 15.7932`, **NOT degenerate** | measured |

**THESE ARE PRIOR MEASUREMENTS AND ARE NOT IMPORTED AS THIS ITEM'S VALUES.** They ran on a
`FIELD_B` that could not start a solve and on a different stage graph. **Every number this item
grades is re-measured on this item's own configuration**, exactly as `DAFOAM_CHARTER.md` §5
requires of an FD reference. They are recorded here so that a **repeat** of them is a
corroboration and a **departure** is a finding, rather than either being a surprise.

### 2.1 THE STROUHAL CAVEAT, IN THIS DOCUMENT'S OWN WORDS

The measured period gives `f ≈ 5.26 Hz` and **`St ≈ 0.5264`** — roughly **2.6× the accepted
≈0.2** for a circular cylinder. **On a 2,450-cell 2D URANS mesh with wall functions that is far
more likely a RESOLUTION ARTIFACT than a discovery.** Further, the estimator is
**mean-crossing**, which underestimates the fundamental on a harmonic signal, so **18.9955 is a
LOWER bound on the period and 0.5264 an UPPER bound on `St`.**

> **`St` FROM THIS ITEM IS NEVER TO BE QUOTED AS A STROUHAL MEASUREMENT.** It is a
> **window-sizing diagnostic** and nothing else. No mesh-convergence study is bought here, so
> the artifact hypothesis is **not tested and not refuted** — it is simply the more likely
> reading, and this document says so before any number is produced.

### 2.2 A POSSIBLE OUTCOME, REGISTERED IN ADVANCE RATHER THAN DISCOVERED LATER

With `δ_window` live at `1.27e-03`, direction-only arithmetic gives
`h_min = 100·δ_eff/|g| ≈ 1.10` against a registered `h_max = 0.05` — **~22× over**.

> **D12 MAY BE A CASE WHERE THE FD BRIGHT LINE CANNOT BE CROSSED AT ALL. That would be a
> GENUINE FINDING ABOUT THE METHOD–CASE PAIR, NOT A FAILURE OF EITHER**, and it is registered
> here as an anticipated outcome so it cannot later be read as a consequence of an instrument
> defect. D12-F′ pointed the same way: *on that window an FD verification could not have beaten
> ~5 % even in principle.* The `G12R-4` no-admissible-step branch is a **RESULT**.

---

## 3. THE PIPELINE — AND THE ONE CHANGE THAT IS THE REASON FOR THIS ITEM

All stages np=1, `numberOfSubdomains 1`, `--user 0:0`, `--cpus=1`,
`--memory=20g --memory-swap=20g --oom-score-adj=500`, **no `--rm`**, `--bind-to none`.

| stage | what | kind | steps |
|---|---|---|---|
| **S0** | mesh | mesh | — |
| **S1a** | `potentialFoam` + `simpleFoam` spin-up | **steady** | 500 outer |
| **S1b** | PIMPLE to `t = 10` → **FIELD_A** | unsteady | 200 |
| **S2a** | **300 steps from FIELD_A, ENDING AT THE DISCARD POINT → FIELD_B** | unsteady | 300 |
| **S2b** | the diagnostic series, from FIELD_B | unsteady | 2400 |
| **S3** | `δ_repeat`, 3 identical runs at `W` | unsteady | 3 × 300 |
| **S3b** | `δ_pert`, 2 probe steps a decade apart × 4 components × 2 signs | unsteady | 16 × 300 |
| **S4** | envelope, `compute_totals` at `n ∈ {20,40,80}`, ×2 | unsteady | 6 |
| **S5** | the adjoint at `W` | unsteady | 300 |
| **S7** | plant + clean | unsteady | 2 × 300 |
| S6 / S6b / S6c / S8 | sweep, trivial baseline, vector FD, IPOPT | unsteady | phases 2–4 |

### 3.1 **`FIELD_B` COMES FROM A FINAL WRITE, AND ITS COMPLETENESS IS CHECKED**

**MEASURED AND CONFIRMED ON TWO INDEPENDENT STAGES** of the superseded run:

| write | fields |
|---|---|
| **FINAL-time** (S1b `t=10`; S2 `t=24`) | **11 + `uniform`** — `U U_0 betaFINuTilda fvSource meshPhi nuTilda nuTilda_0 nut p p_0 phi` |
| **INTERMEDIATE per-step** (S1b `t=5`; S2 `t=3`) | **4** — `U nuTilda p phi`. **No `nut`.** |

So **S2a ENDS at the discard point**, making its write a **final** write, and `FIELD_B` is taken
from it. The transient discard is therefore **done by construction**, and the comparator's
registered discard is **0**: every sample S2b emits is retained.

**THE COMPLETENESS CHECK.** Before `FIELD_B` is frozen, its field list is compared against the
case's **own** complete write (`FIELD_A`) — a **measured** reference, not a typed one — and any
missing field **REFUSES**. **The check carries its own planted control**: it is pointed at an
intermediate per-step write, which is known incomplete, and **must find something missing**, or
the launcher aborts. *A check never shown able to refuse is not a check.*

**WHY THIS AND NOT A SECOND md5 READER.** The supervisor's own lesson, and it is the most
general thing in this item:

> **INDEPENDENCE OF READERS IS NOT INDEPENDENCE OF QUESTIONS.** Two independent readers defeat a
> self-consistent manifest **about the same question**; they are powerless against a **shared
> wrong question**. The md5 control asks *"is this the file we staged?"* — **it never asks "is
> this enough to start a solve?"**

The md5 manifest is **KEPT** (it answers its own question well) and is **SUPERSEDED, not
supplemented**, by the completeness check.

---

## 4. INSTRUMENTS, FROZEN BY MD5 AT THIS COMMIT

| file | md5 | note |
|---|---|---|
| `d12x_run_script.py` | `2790c39a09cd458d5a3263d7f1811da5` | **BYTE-IDENTICAL to the superseded `d12r_run_script.py`** — asserted, 7,010 bytes. **It carried no defect and is carried forward unchanged.** |
| `d12x_grade.py` | `1e757cffffda5fdf675b6dedbf5a7ca8` | the comparator |
| `d12x_stage_and_run.sh` | `e7be9ea468c700e1c6e3463cf443c7a9` | the launcher |

The launcher **verifies both python instruments against their committed HEAD blobs before every
launch** and aborts with code 4 otherwise — rule 2's grading-path clause **executed**.

---

## 5. THE FOUR REPAIRS, AND THE GATES THAT CARRY THEM

| # | defect in the superseded item | repair, and where it lives |
|---|---|---|
| **D1** | `FIELD_B` could not start a solve | §3.1 — final write + **completeness check with a planted control** |
| **D2** | the age guard could not arm (`writeCompression on` ⇒ `U.gz`, typed datum `0/U`) | the datum is **resolved from the file that exists** (`0/U` **or** `0/U.gz`) and the stage is **NOT LAUNCHED** if neither is there. **It failed SAFE before — `None` was a refusal — and that distinction is worth more than the repair**: compare `D7-GRADER-DEF-3`, where a blind guard returned `pass=True`. Same blindness, opposite direction, and only one can certify a wrong result. |
| **D3** | `obj_from_log` read `CL` | an **anchored `^CD:`** reader, plus a **structural witness**: `CD` is positive-definite here and `CL` oscillates about zero, so **zero negatives in the CD series is a POSITIVE demonstration** that the reader read `CD`. `G12R-0` **refuses** on any negative and on an uncounted sign. |
| **D4** | `Time =` compared against a steady solver's outer iterations | every stage **declares its kind**; `G12R-0` **REFUSES on an unknown kind** rather than comparing incomparable counts, gates the step proxy only on **unsteady** stages, and **reports it** on steady ones. |

**`δ_window` MAY NEVER BE REPORTED AS A NUMERIC ZERO.** When `|W/P − round(W/P)| ≤ 0.05` with
**`P` MEASURED by `G12R-1`** — never predicted — the term is **EXCLUDED BY NAME**, `δ_window`
is `None`, and the record says it was cancelled by construction. **A zero reads downstream as
"measured, and small"; the truth is "cancelled by construction, and unmeasurable at this `W`".**
`G12R-4` accepts an excluded term and **REFUSES a `None` that was not flagged degenerate** —
*missing is not the same as excluded.*

**`applied_magnitude` UNITS ARE REGISTERED BEFORE PHASE 3.** The WHERE-control is **strong on
index and sign** — a positive scaler moves neither — and **conditional on magnitude**. Phase 3
calls `G12R-W` with `require_units=True`, which **refuses** an unregistered unit string.
**Comparing a magnitude without naming its units is `D4-DEF-4` surviving inside the control
built to catch it.**

---

## 6. THE COMPARATOR SURVIVES `python3 -O` — MEASURED, WITH A MUTANT

The superseded comparator carried **59 `assert` statements, ALL inside its battery**, none in
any gate. **The gates were never the exposure. THE EVIDENCE THAT THE GATES WORK WAS.**

**MEASURED on the superseded file:** a gate mutant (PASS band `0.05 → 0.50`) is caught
unflagged (`rc = 1`) and **ESCAPES under `-O` (`rc = 0`)**.

This comparator carries **ZERO `assert` statements**, proven by **AST, on statement type** —
because a grep matches `raise AssertionError` and a behavioural test passes a file whose
asserts happen to hold; **only the statement type distinguishes `assert X`, which `-O` deletes,
from `if not X: raise`, which it does not.** Registered requirements, all implemented:

1. **Every unit tallies an explicit counted result.** `check()` raises a real exception.
2. **The battery exits non-zero BY COUNTING**, against a **FROZEN** `EXPECTED_UNITS = 72`.
   *(The first draft derived that constant from the list it checked, making the comparison
   tautological — the **M3 class inside the control built to satisfy this very ruling**, found
   by mutation in this lane's own new code and recorded rather than quietly fixed.)*
3. **`--olimb` runs MUTANTS under both flags**, because comparing healthy input under two
   flags proves nothing — healthy input passes either way, which is exactly what a **completely
   disabled** battery produces. **M-A** is behavioural; **M-B** reverts one `check()` to an
   `assert`, which is what a well-meaning future edit looks like.
4. **`__debug__` is asserted INSIDE THE IMAGE** and written to the ledger **beside the digest**
   (launcher assert A6), because a grader proved flag-proof on the host with a **producer**
   dropping asserts in the image is the self-consistent-manifest shape again.

---

## 7. GATES — thresholds and labels unchanged from the superseded item except where §5 names

`G12R-0` (completion, **refusal**), `G12R-1` (limit cycle), `G12R-2` (`δ_repeat`),
`G12R-3` (`δ_window` + degeneracy), `G12R-3b` (`δ_pert`, **model-free**), `G12R-4`
(`δ_eff := max(δ_repeat, δ_window, δ_pert)`, step sizing), `G12R-5` (plateau, **positional,
never reads the adjoint**), `G12R-6` (the bright line; PASS ≤ 5 %, CONDITIONAL 5–15 %, FAIL
> 15 % or any sign flip), `G12R-7` (trivial baseline at `10·h*`), `G12R-8` (envelope,
`3σ` resolution rule), `G12R-9` (planted zeros), `G12R-10` (two rows), `G12R-11`
(optimisation, authorised **by the comparator**), `G12R-W` (the WHERE-control).
`h_max = 0.05`, `EPS_NOISE_TARGET = 0.01`, `W = 300`, `W2 = 900` contingency,
`MemAvailable` floor **14.0 GiB**.

---

## 8. COST

Phase 1 (S0–S7): **~70 core-min** predicted, from the superseded run's own measured stages
(S0 0.05, S1a 0.2, S1b 0.77, S2b ≈ 7.5 at 2400 steps, plus 22 window-length runs at ≈ 1.1 and
6 envelope runs). Whole item **~270 core-min** including S8.

> **REGISTERED RUNAWAY GUARD: `CAP_CORE_MIN = 600.0` total, `CAP_S8 = 350.0`**, asserted by the
> launcher against the values this document names and evaluated **before every stage**.
> **Cost constraints are LIFTED (Sanaa, 2026-08-25): these are guards reported to the
> supervisor, not budgets rigor is trimmed to fit. Equally, lifted cost is NOT a licence to let
> a known-broken run continue** — the superseded phase 1 was **arrested by the lane** on exactly
> that ground and this document adopts it.

Derived **$0.2308** at $0.0513/core-h, c7a.4xlarge, reported-by-owner — **DERIVED, NOT
MEASURED**. Calibration row owed at completion, id derived **tolerantly by hand inside the
committing invocation**, table **and prose** (the `C-91` lesson).

## 9. WHAT THIS ITEM WILL NOT ESTABLISH

Nothing at `np > 1`; nothing about `reduceIO: False`; nothing about forward-AD or complex-step
as a reference; **no grid family, so rule 5 has no row to gate and no GCI is quoted**; **nothing
about the physical accuracy of `CD`** at `Re_D = 1.0e6` on 2,450 cells; **nothing about `St`**
(§2.1); nothing about the endpoint gradient as a gate. **The PATCHED row is UNBOUGHT unless
`--image patched` is run, and is named as unbought in any record that quotes a shipped number.**

---

## 10. AMENDMENT 1 — 2026-08-27, POST-COMPUTE. The L-342 field-class split at the status limb. No gate, threshold, cap, band, label, cpuset or cost moves.

**Version 1.0 → 1.1.** Dated **2026-08-27**. Lane: dafoam `lab-lane` (B). Supervisor: `dafoam-supervisor` (`[lab-attributed]`). **Lines whose number changed above this section: 0 — proved ON BYTES, not on a line count**: the HEAD blob of this file is asserted a byte-exact PREFIX of the amended file, by `cmp`, inside the committing invocation. **Sections 1–9 stand and are not rewritten.** §4's md5 row for `d12x_grade.py` is **SUPERSEDED BY §10.6 AND LEFT WHERE IT IS** — an original is struck on the record, never rewritten in place (rule 2).

**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).

### 10.1 Authority — a standing rule ENFORCED, not an exception granted

**This amendment's authority is `L-342` and ruling `R-RC`, and it is deliberately NOT `VERIFICATION_CHARTER.md` §2d.1.** This family has refused §2d.1 four times on the ground that an exception used where the ordinary path is open is an exception being widened; invoking it here would be a fifth widening. §2d.1's four conditions are checked in §10.7 as procedural diligence and all hold — **but they are not the authority.**

`L-342` is Sanaa's own universal rule (2026-08-26T16:15Z), verbatim:

> *"a bookkeeping failure invalidates the bookkeeping, never the physics artifacts — and graders must separate physics-critical fields from infrastructure fields so a dead poller can never void a run again."*

and its own application clause names this repair by name: *"Repair of a conflating grader is a pre-registered amendment that touches no band, threshold or verdict logic."*

`R-RC` was **APPROVED BY SANAA HERSELF** on 2026-08-27, standing directives §0 (`etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md`), verbatim:

> **R-RC: APPROVED — rc value is physics, rc record is infrastructure; absent record -> NOT MEASURED only when the other four rule-4 conditions hold.**

**A grader that refuses on a launcher-metadata field is not exercising a gate — it is in BREACH of a standing rule, and bringing it into compliance is the freeze's own terms ENFORCED, not a discretionary departure from them.** `R-RC` is cited for the SHAPE of the split (a strict fatal limb; a present-but-unfilled record refuses; only an absent one defers), not because `status` is `rc`; the field-class principle that covers `status` is `L-342` directly.

**Sanaa can overrule any of this.**

### 10.2 The condition, and how it was checked — the post-compute honesty clause

Gates are **CLOSED** on this item: 63.95 core-min were spent and the comparator has fired. So the ordinary pre-compute amendment clause is **NOT** available and this amendment does not claim it. What is claimed instead is checkable and was re-driven at **2026-08-27T18:49:23Z**, not carried over:

> **NO GATE DOWNSTREAM OF `G12R-0` HAS EVER PRODUCED A VALUE ON THIS RUN.**

`G12R-0` is the first gate in `plan()` and it refused on the first row, so `G12R-1`, `G12R-2`, `G12R-3`, `G12R-3b` and `G12R-4` never ran. Driven at the timestamp above against `/home/ubuntu/certonomous-runs/CURRICULUM-D12R-cylinder-unsteady`: `step_plan.json` **ABSENT**, `step_plan2.json` **ABSENT**, `grade.json` **ABSENT**, `GRADING.txt` **ABSENT**, `RESULTS.md` **ABSENT**. **There is no number in this item's own artefacts to tune this amendment to.**

**AND THE HALF THAT IS NOT CLEAN, STATED BY THIS LANE RATHER THAN LEFT TO BE FOUND.** The successor item **D12R2 has already graded phase 1 on an equivalent stage graph** and published its gates (`C-115`: nine gates returned, `h_min = 1.742838e-01` against `h_max = 5.000e-02`, no admissible FD step). **So the DOWNSTREAM ANSWER FOR THIS CASE IS ALREADY BROADLY KNOWN, and this amendment is authored in that knowledge.** It cannot be claimed as prediction-first for `G12R-1`–`G12R-4`. **Two things fence it, and neither is an argument that the knowledge is absent:**

1. **The amendment touches nothing those gates read.** It changes one limb of `G12R-0`, a REFUSAL-ONLY gate that emits no number. Every band, threshold, window and label they use is byte-unchanged (§10.3).
2. **The instrument is committed BEFORE it is run** on the preserved artefacts, and the order is recorded in the commit graph rather than asserted in prose.

**What this re-grade may therefore be claimed to buy is stated narrowly:** the recovery of 63.95 core-min from WASTE, and a **corroboration-or-departure** reading against D12R2. **It may NOT be quoted as an independent measurement of the FD bright line for this case.**

### 10.3 What moves, and what deliberately does not

| clause in `d12x_grade.py` | before | after | class |
| --- | --- | --- | --- |
| `g0_completion` `status != "COMPLETE"` on a task that **writes** a per-stage JSON (`run_model`, `compute_totals`, `opt`) | REFUSAL | **REFUSAL, unchanged** — absent, `None` or a wrong string all still refuse | PHYSICS-EVIDENCE |
| `g0_completion` `status != "COMPLETE"` on a task that **writes none** (`shell`) | REFUSAL | **`NOT MEASURED`, reported BY NAME beside the verdict** | INFRASTRUCTURE |
| a `shell` row that nonetheless **carries** a status | not checked at all | **REFUSAL, new** — the launcher and the gate then disagree about what kind of stage it is | PHYSICS-EVIDENCE |
| a row whose `task` is absent or unregistered | not checked at all | **REFUSAL, new** — the taxonomy limb, mirroring the [D4] unknown-`stage_kind` refusal | PHYSICS-EVIDENCE |
| `rc`, `oomkilled`, `end_line_present`, `last_time == endTime`, `coldstart_ok`, `age_guard_ok`, `stage_kind`, `time_line_count`, `execution_time_count`, the CD sign witness, `field_b_md5_ok`, the JSON-vs-log objective cross-check, the `MemAvailable` floor, the empty-stage-list refusal | REFUSAL | **REFUSAL, all unchanged** | PHYSICS |

**Counted, not asserted:** `g0_completion` carried **17** `raise Refusal` sites at the freeze and carries **19** now — **one site replaced by three, and sixteen untouched.** The count is derived by AST on `ast.Raise` nodes, not by grep.

**Unmoved:** `CAP_CORE_MIN = 600.0`, `CAP_S8_CORE_MIN = 350.0`, `W_PRIMARY = 300`, `W_CONTINGENCY = 900`, `H_MAX = 0.05`, `EPS_NOISE_TARGET = 0.01`, `MEMAVAIL_FLOOR_GIB = 14.0`, `BAND_PASS = 0.05`, `BAND_CONDITIONAL = 0.15`, `TRANSIENT_DISCARD = 0`, `PLANT_SHAPE`, `DPERT_HA/HB`, `WINDOW_DEGEN_TOL`, every gate `G12R-0`…`G12R-11` and `G12R-W`, every stage in §3's graph, `np = 1`, `--cpus=1`, `--memory=20g`, and the §8 cost estimate. **Zero core-min are spent by this amendment or by the re-grade it enables.**

### 10.4 Precedent, and one deliberate narrowing against it

The successor comparator `cases/dafoam/curriculum_D12R2/d12y_grade_w3.py` **already carries exactly this repair**, as `[D12R2-DEF-1] THE STATUS LIMB IS TASK-AWARE` (W3 AMENDMENT 2, `af44d244`). This amendment is a **back-port of a shipped, selftested design**, not an invention.

**The narrowing.** D12R2's `EVIDENCE_TASKS` also holds `"mesh"`, because ITS launcher writes `mesh_check_ok`, `mesh_n_cells` and `mesh_polymesh_files` and its gate demands all three. **This launcher writes none of them**, so admitting `mesh` here would grade a mesh stage on evidence that does not exist. `EVIDENCE_TASKS = ("shell",)` and a `mesh` row **REFUSES on the taxonomy limb**. That is **stricter** than the precedent and deliberately so.

### 10.5 Planted-failure proof — Sanaa's §1, L-314 standard, zero compute

> *"Every guard ships its planted-failure proof."*

`--amend1-proof --root <run root>`: **14 legs, 14 OK, 0 failures, under `python3` AND `python3 -O`**, `__pycache__` cleared before every invocation. **ONE permissive leg (P0); THIRTEEN strict legs.** Every plant is written to a COPY of the manifest on disk, **read back from disk, and the round trip asserted** before the gate is asked anything — a refusal produced by a plant that never reached the file would be a false positive. Evidence: `cases/dafoam/curriculum_D12R/d12x_grade_amendment1_proof_evidence.txt`.

| leg | planted onto the preserved manifest | required |
| --- | --- | --- |
| P0 | nothing — the real 32 rows | GRADES, with the unread record NAMED and every substitute limb named individually |
| P1–P6 | `rc=1`; no `End`; `last_time != endTime`; age guard failed; `OOMKilled`; cold-start failed — **all on the exempted `S1a` row itself** | **STILL REFUSE, each on its OWN limb** — refusing for the wrong reason is scored a failure |
| P7, P8 | short `Time =` count on `S2b`; `rc=137` on `S5` | STILL REFUSE — the exemption did not leak into the other 31 rows |
| P9, P10 | `status=None` on `S1b`; the `status` key **deleted** from `S1b` | **STILL REFUSE — this is the original D12R refusal, preserved** |
| P11 | `status="COMPLETE"` planted onto the `shell` row | REFUSE — launcher and gate disagree about what the stage is |
| P12 | `task = mesh / sweep / None` | REFUSE on the taxonomy limb |
| P13 | the plant reader driven at a value that was never planted, then at one that was | the reader is shown able to see **both** a plant and its absence (rule 3) |

**The proof is shown able to FAIL.** A mutant removing the evidence-branch leak guard (`if st.get("status") is not None:` → `if False:`) is **caught by P11 under both flags (rc = 1)**.

**AND A MEASURED FINDING AGAINST THIS LANE'S OWN FIRST DRAFT.** The first `--olimb` mutant built for this amendment widened `EVIDENCE_TASKS` to hold every task — and it is **INERT**, because `if task in JSON_TASKS` is tested FIRST, so a task in both tuples still takes the strict branch. **A mutant that changes a constant and not a behaviour is not a mutant, and a battery "catching" it would have proved nothing.** Driven, recorded in the evidence file, and **REPLACED** in `--olimb` by `M-C` (the JSON-branch status demand removed) rather than quietly dropped.

**The inherited battery: 84 units, 0 failures, under both flags** — 72 at the freeze plus 12 added here (`U-A1a`…`U-A1l`). Two inherited fixtures (`base_stage`, `_g0row`) gained a `task` field for the same reason and by the same rule RULING 5 used when it added the age guard: *a fixture missing a limb is a stage missing evidence*; the field is added, the gate is not weakened, and both fixtures default to a JSON task so every inherited unit drives the **unchanged** refusal path. `u01b`'s refusal matrix gains `task="sweep"`, `task=None` and `status=None`. **`--olimb`: four mutants (M-A, M-B, M-C, plus the unmutated control), every one caught under both flags.** **`ast.Assert` count 0**, with the counter shown counting **1** on a sacrificial copy carrying one planted assert.

### 10.6 The instrument re-frozen at this commit

| file | md5 at v1.0 (§4) | md5 at v1.1 | change |
| --- | --- | --- | --- |
| `d12x_grade.py` | `1e757cffffda5fdf675b6dedbf5a7ca8` **(SUPERSEDED, and §4 is left as written)** | `f2e6cd48af3890a2c0a9e427d09c416a` | the task taxonomy, the task-aware status limb, the infrastructure channel, 12 units, the `M-C` mutant and `--amend1-proof`. Deltas: `d12x_grade_DELTAS_amendment1.diff`, 545 lines |
| `d12x_run_script.py` | `2790c39a09cd458d5a3263d7f1811da5` | **unchanged** | — |
| `d12x_stage_and_run.sh` | `e7be9ea468c700e1c6e3463cf443c7a9` | **unchanged** | **THE LAUNCHER IS NOT TOUCHED.** It is not wrong: writing `status = None` for a stage that produces none is correct behaviour. The defect was the PAIR, and the pair is repaired on the side that reads |

The launcher verifies both python instruments against their **committed HEAD blob** before every launch (`d12x_stage_and_run.sh:161-162`, abort code 4), so this file must be committed before anything can run against it — **the freeze is executed, not asserted.** No launch is made by this amendment: the re-grade is **zero compute** on preserved artefacts.

### 10.7 §2d.1's four conditions, checked as diligence and NOT relied on

Stated because a reader will ask, and refused as an authority because §10.1 does not need it.

1. **The defect is in the instrument, not the result** — held: the launcher's `else` branch and this grader's unconditional limb, frozen in the same commit `f9c8b9c8`, disagree by design.
2. **The repair is disclosed and dated** — held: this section, appended, prefix byte-proved.
3. **What moved is quantified** — held: §10.3's table, and 17 → 19 refusal sites counted by AST.
4. **Pre-repair values sit beside the published ones** — **held only VACUOUSLY, and that is exactly why §2d.1 is not the authority: no number was ever produced, so there is no pre-repair value to place beside anything, and a condition met by an empty set is not met.** `C-107` made this same reading on 2026-08-26 and used it to argue for a re-run; `L-342` and `R-RC` were not yet available to it.

### 10.8 What this amendment does NOT establish

Nothing about `St` (§2.1 stands in full). Nothing about the physical accuracy of `CD`. **No grid family, so rule 5 has no row to gate and no GCI is quoted.** It does **not** repair `S0`'s absence from the manifest (§8 addendum of `PHASE1_GRADE_REFUSAL.md`) — `G12R-0` still grades 32 of the ledger's 33 stages and **still never sees the mesh stage**, and that finding is **carried forward unrepaired and undiminished**. It does not repair the `ExecutionTime` line-count conflation the lab-wide L-342 audit flagged in ~60 comparators: **measured on this run, `execution_time_count >= expected_steps` holds on 32 of 32 rows, so the clause is not refusing here, and repairing a limb that is not refusing would be a permissive widening bought with no evidence.** It does not touch the `stage_kind` unknown-kind refusal, which refuses because the gate cannot name the quantity it is comparing — **that is the gate working, and `R-RC` does not license repairing it.**
