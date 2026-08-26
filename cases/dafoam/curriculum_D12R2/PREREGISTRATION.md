# CURRICULUM D12R2 — UNSTEADY ADJOINT, 2D CYLINDER, TIME-AVERAGED DRAG — PRE-REGISTRATION

**Version 1.0. FROZEN.** Dated **2026-08-26**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.
**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).

---

## 0. WHY THIS ITEM EXISTS, AND WHAT IT SUPERSEDES

Authority: the **dafoam-supervisor's ruling of 2026-08-26**, which reads, in its own words,
**"RE-REGISTER. NOT REPAIR, NOT PATCH."**

**This item SUPERSEDES `cases/dafoam/curriculum_D12R/PREREGISTRATION.md`**, which itself
superseded `curriculum_D12`. Both are **CITED, NEVER REWRITTEN** (rule 6). D12R's phase 1
verdict — **`NOT A RESULT`** — **stands on the record**, its run root is preserved
byte-for-byte, and the full diagnosis lives at
`cases/dafoam/curriculum_D12R/PHASE1_GRADE_REFUSAL.md` (commits `9d26801e`, `60e838aa`).

**This is not a failed solve.** All 33 of D12R's phase-1 stages returned `rc=0`. What failed is
that **the frozen document froze a launcher/comparator pair that is mutually contradictory**, and
that is a property of the document, not of the compute.

### 0.1 THE §2d.1 REPAIR EXCEPTION WAS CONSIDERED AND REFUSED, ON ITS OWN TERMS

The supervisor's reasoning is adopted verbatim into this document because a successor must not
read the re-registration as ceremony:

> Its four conditions are: (1) a demonstrable error; (2) established by an instrument
> INDEPENDENT OF THE HYPOTHESIS, one that grades nothing; (3) the record discloses it, names
> that instrument, and **QUANTIFIES WHAT MOVED**; (4) the pre-repair values are recorded beside
> the published ones. Conditions (1) and (2) hold. **But (3) and (4) are satisfiable here only
> VACUOUSLY: nothing moved, because no number was ever produced.** Gates 1/2/3/3b/4 never ran;
> there are no pre-repair values to record beside anything. **A condition met by an empty set is
> not met.**

**And the re-run is nearly free**: 63.95 core-min, **$0.055 derived**. Repairing and re-grading
the existing artifacts would save that and buy a permanent doubt, because **any repair authored
now is authored knowing exactly which row fails**. Paying $0.055 to remove a fitting objection
is not a close call.

**D12R's 63.95 core-min is now WASTE** (`COMPUTE_BUDGET_CHARTER.md` §6), named separately in its
own calibration row and never absorbed into any ratio.

## 1. THE AMENDMENT CONDITION, AND HOW IT WAS CHECKED

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady` DOES NOT EXIST.**

**`test -e` returned false at 2026-08-26T03:29:38Z**, immediately before this document was written; state
at that moment: **DOES_NOT_EXIST**. The launcher **refuses with exit 6** if it exists at phase 1,
so the condition is enforced by the instrument and not merely asserted. After the first
container, gates are **CLOSED**.

---

## 2. THE THREE DEFECTS THIS ITEM CARRIES

### 2.1 `D12R2-DEF-1` — THE STATUS LIMB WAS NOT STAGE-KIND AWARE WHILE ITS SIBLING WAS

`d12x_grade.py:204` refused any stage whose `status` was not `"COMPLETE"`, unconditionally.
Thirty-six lines below it, at `:240`, the **step-count limb carried an explicit `[D4]` banner
making it stage-kind aware** — *"gates the step proxy only on unsteady stages, and reports it on
steady ones."*

> **THE SAME BLINDNESS WAS FIXED IN ONE LIMB AND LEFT IN THE OTHER, IN THE SAME FUNCTION, IN THE
> SAME COMMIT.** That is the finding, and it is worth more than the phase-1 table would have
> been. A repair that names a class of error and then repairs one instance of it has not
> finished; **the lesson generalises and the patch did not.**

### 2.2 `D12R2-DEF-2` — S0 VANISHED FROM THE MANIFEST AND NOTHING REFUSED

D12R's `ledger.txt` carries **33 `STAGE=` lines**; its `manifest.jsonl` carries **32 rows**. The
difference is `S0`, the mesh stage. `63.8833 + 0.0667 = 63.95` exactly — the residue is `S0` and
nothing else.

> **`S0` DID NOT FAIL A CHECK. IT VANISHED.** The completion gate graded 32 of the 33 stages
> that ran, and the one it did not grade is the one that builds the mesh every other stage rests
> on. **A completeness gate that cannot see the mesh is not a completeness gate.** This is L-302
> at the manifest level: *an instrument that cannot say "I measured nothing" will report a number
> it did not measure.*

**This is the more dangerous of the two. `DEF-1` refused loudly; `DEF-2` was silent**, and was
found only by reconciling the ledger's cost total against the manifest's own `core_min` column.

**BY DESIGN OR BY OMISSION? — SETTLED, AS THE RULING REQUIRED, BEFORE THIS RE-FREEZE.** The
launcher's manifest-append path was read. **The answer is: the bootstrap is BY DESIGN, the missing
row is BY OMISSION.** The evidence, all of it from the frozen instruments themselves:

| # | evidence | reading |
|---|---|---|
| 1 | The manifest row is appended in exactly two places, **both inside `run_stage`** (`d12x_stage_and_run.sh:248` blocked-row, `:348`/`:499` normal row). | The row is a **side effect of the function that runs a stage**. |
| 2 | `run_stage:254` opens with `cp -a "$ROOT/mesh" "$D"` — **every stage copies the mesh S0 creates**. | **S0 structurally CANNOT call `run_stage`**; it must precede it. The bootstrap is **by design**. |
| 3 | `d12x_grade.py:241` enumerates `"mesh"` as one of exactly **three legal `stage_kind` values**, and `:251` carries a live `elif kind == "mesh": pass` branch. | **The comparator's author expected a mesh row to arrive.** |
| 4 | **There is no `export STAGE_KIND=mesh` anywhere in the launcher** (`:618` steady, `:623/647/673/705` unsteady, and nothing else). | The value is **legal in the comparator and never produced by the launcher**. |
| 5 | The launcher names `S0` in three places only (`:590` comment, `:608` abort, `:611` ledger echo) — **no comment anywhere states or implies deliberate exclusion**. | Nothing was decided; something was **missed**. |
| 6 | `PREREGISTRATION.md` §3 lists **S0 in the same stage table** as every other stage. | S0 was **registered as a stage**, not as a pre-step. |

> **THE COUPLING IS THE DEFECT: "a row gets written" was tied to "the stage went through
> `run_stage`", so a stage that could not use that function silently got no row.** The
> comparator's `mesh` branch is **dead code on that run** — a reader of the code sees mesh
> stages handled and would reasonably conclude mesh stages are graded, while the manifest never
> presents one.

### 2.3 `D12R2-DEF-3` — THE LAUNCHER WRITES A NULL ITS OWN COMPARATOR MUST REFUSE

`d12x_stage_and_run.sh:413` sets `row["status"] = None` in an explicit `else` branch when a stage
has no per-stage JSON. `S1a`'s task is `shell` — the spin-up runs `runPrimalSimple.py`, not the
run-script — so `d12x_S1a.json` is never written. **Both instruments frozen in the same commit
`f9c8b9c8`; the launcher by design emits a row the comparator by design must refuse.**

---

## 3. WHAT THE NEW INSTRUMENTS DO — THE FOUR THINGS THE RULING REQUIRED

### 3.1 THE STATUS LIMB IS TASK-AWARE (`D12R2-DEF-1`)

A **REGISTERED TAXONOMY**, not a lookup built from whatever the manifest contains — *a taxonomy
derived from the data it classifies cannot refuse an unknown member*:

    JSON_TASKS     = ("run_model", "compute_totals")
    EVIDENCE_TASKS = ("shell", "mesh")

- `JSON_TASKS` **must** carry `status == "COMPLETE"`. **This is D12R's refusal, PRESERVED: the
  repair widens the question, it does not weaken it.**
- `EVIDENCE_TASKS` carry completion in their own evidence — `rc`, the `End` line, the age guard,
  the time limb (shell) or the mesh limbs (mesh). **This branch is NOT a waiver: a `shell` or
  `mesh` stage that genuinely failed still refuses**, and a no-JSON task that *does* carry a
  status refuses too, because that is **two instruments disagreeing about what a stage is**.
- An **unregistered task REFUSES** rather than being guessed at.

**PRESENCE BEFORE VALUE, AND IT IS THE FIRST THING THE LOOP DOES.** `REQUIRED_ROW_KEYS` must all
be **present**; absence is refused **by name**. `.get()` collapses *absent* and *present-but-None*
into one value, and where a value is not gated, **absence reads as a pass**.

> **A DEFECT THIS FILE'S OWN UNIT CAUGHT, RECORDED RATHER THAN QUIETLY MOVED.** The first draft
> put the presence block *after* the `rc` and `oomkilled` limbs, so a row **missing** `oomkilled`
> refused with `"OOMKilled=None"` — a message blaming the container for a key the row never
> carried. **Both are refusals, so no test that merely asserts "it refused" could tell them
> apart.** `U-15e` requires the refusal to **NAME the missing key**, and that is what caught it.

**AND THE MESH LIMBS REPLACE A LIMB THAT COULD NOT FAIL.** A mesh stage has no time, so
`last_time == endTime` on a mesh row can only ever be `0.0 == 0.0`. **A limb that cannot fail is
not a limb** — it is the vacuous shape this lab amended against, wearing the costume of a check.
A `mesh` task must instead present: `mesh_check_ok` (**checkMesh's own verdict**, not this gate's
opinion), a **positive integer** `mesh_n_cells` read from the mesh it wrote, and
`mesh_polymesh_files` containing all of `points faces owner neighbour boundary`. `.gz` is
stripped, because `writeCompression` is on for this case and **the superseded item's D2 defect
was a typed datum `0/U` against a real `U.gz`**.

### 3.2 `G12R-0b` — THE COUNT ASSERTION BINDING MANIFEST ROWS TO LEDGER LINES (`D12R2-DEF-2`)

**Registered:** `EXPECTED_STAGE_ROWS_PHASE1 = 33`
= S0 1 + S1a 1 + S1b 1 + S2a 1 + S2b 1 + S3 3 + S3b 16 + S4 6 + S5 1 + S7 2.

**It is a number this document types, not a length measured from the thing being checked.**
Deriving it as `len(<the stage list>)` and comparing it against that same list is the **tautology
amended against**: it can only ever be true.

`G12R-0b` refuses on: a name mismatch **in either direction, naming the stages**; a count
disagreeing with the frozen 33; **duplicate rows** (a duplicate can pad a short manifest back to
the right count); a **nameless row**; an **absent ledger**; and a ledger with **zero `STAGE=`
lines** — because *the reader must be shown able to see a stage before its zero is evidence*
(rule 3), and a zero there means the ledger format moved, not that no stage ran.

**WHY THE LEDGER IS AN ADMISSIBLE SECOND WITNESS when a second md5 reader was ruled not to be
one.** D12R's own §3.1: *INDEPENDENCE OF READERS IS NOT INDEPENDENCE OF QUESTIONS.* The ledger is
**not a second reader of the manifest**. It is a separate artifact appended by a **different
statement** — a shell `echo … | tee -a` versus a python `open(…, "a")` — and **in D12R those two
statements disagreed**, which is how the defect is visible at all. **And agreement between the
two is still not enough**, which is why the frozen 33 is also required: both could lose the same
stage. `U-16c` makes exactly that happen.

**`G12R-0b` RUNS FIRST**, before `G12R-0` and every gate after it, because those gates grade a set
of rows **whose completeness is what this gate establishes**. Grading first and counting
afterwards would publish numbers from a set already known to be short.

### 3.3 S0 WRITES A MANIFEST ROW (`D12R2-DEF-3`)

The bootstrap ordering is **kept** — it is by design. The row is written **inline, immediately
after S0's ledger line**, from the mesh on disk: `mesh_n_cells` read from the polyMesh `owner`
header (**not from the log**, so the number is backed by the artifact the next stage solves on),
`mesh_check_ok` from checkMesh's verdict, and an **age guard whose datum is the instant this
launcher started the container** — there is no `0/U` yet, since S0 is what makes one possible,
and every polyMesh file must be newer. The launcher then **aborts** if the row is absent, so the
repair cannot silently fail to fire.

### 3.4 PHASE 1'S MEASUREMENTS ARE RECORDED AND **NOT IMPORTED**

| quantity | measured, and where | status |
|---|---|---|
| limit cycle | 221 sign changes, p2p **19.40 %**, mean `CD = 0.6563506540` | **curriculum_D12 phase 1. NOT IMPORTED.** |
| shedding period | **18.9955 timesteps** | measured; **NOT re-used as a registration** |
| `δ_window` at `W = 300` | **`1.274958e-03`**, `W/period = 15.7932`, not degenerate | measured; **NOT IMPORTED** |
| phase-1 stage graph | 33 stages, all `rc=0`, 63.95 core-min | **D12R. Its verdict is `NOT A RESULT`.** |
| `S0` mesh | **`nCells = 2450`**, checkMesh `Mesh OK.` | D12R artifact; **re-measured by this item** |

**EVERY NUMBER THIS ITEM GRADES IS RE-MEASURED ON THIS ITEM'S OWN RUN.** A **repeat is
corroboration**; a **departure is a FINDING**. D12R's 32 stage directories stay byte-for-byte as
evidence and are neither deleted nor re-graded.

---

## 4. INSTRUMENTS, FROZEN BY MD5 AT THIS COMMIT

| file | md5 | note |
|---|---|---|
| `d12y_run_script.py` | `2790c39a09cd458d5a3263d7f1811da5` | **BYTE-IDENTICAL to `d12x_run_script.py` and to `d12r_run_script.py` before it** — asserted by `cmp`, 7,010 bytes. **It has never carried a defect and is carried forward unchanged for the third time.** |
| `d12y_grade.py` | `33f7a006e15dce2988a63b2e937cf07b` | the comparator, 2,488 lines |
| `d12y_stage_and_run.sh` | `5f5c5e9fe3224c6c2474d8d355f01073` | the launcher, 898 lines |

The launcher **verifies both python instruments against their committed HEAD blobs before every
launch** and aborts with code 4 otherwise — rule 2's grading-path clause **executed**, not
merely stated.

---

## 5. THE DEMONSTRATION — REFUSALS MADE TO FIRE, UNDER BOTH FLAGS

The ruling, verbatim: *"DEMONSTRATE every new limb by making the condition it guards actually
occur … Under plain `python3` AND under `python3 -O`. A count of units is not a demonstration,
and a selftest that passes under `-O` is the weak test — what matters is whether the REFUSALS
FIRE."*

`--demo` **builds broken artifacts and runs this comparator on them in a CHILD PROCESS under both
flags**, requiring the child to have refused **and to have said why**. A selftest calls a
function; **this runs the program.** It is **seeded from D12R's REAL phase-1 manifest**, so the
rows under test are **the actual bytes that failed on 2026-08-25**, not a hand-written
idealisation. The one fixture is the S0 row — D12R never wrote one, which is the defect — and it
is labelled as a fixture wherever it appears.

**MEASURED, 13 of 13 scenarios, IDENTICAL under `python3` and `python3 -O`:**

| # | scenario | expect |
|---|---|---|
| 0 | **CONTROL — healthy 33-row pair MUST PASS** | **0** |
| 1 | `S1a` as a JSON task with status null — **the D12R refusal, PRESERVED** | 2 |
| 2 | `S1a` shell with `rc=1` — the evidence branch is **no waiver** | 2 |
| 3 | `S1a` shell, age guard FAILED | 2 |
| 4 | `S1a` shell **carrying** a status — instruments disagree | 2 |
| 5 | `S1a` with `age_guard_ok` **DELETED** — absence named, not read as a pass | 2 |
| 6 | `S1a` with an unregistered task | 2 |
| 7 | `S0` mesh: checkMesh did **not** pass | 2 |
| 8 | `S0` mesh: **ZERO cells** — *a vacuous `0==0` limb would have passed this* | 2 |
| 9 | `S0` mesh: polyMesh missing `owner` | 2 |
| 10 | **`S0` DROPPED from the manifest, kept in the ledger — THE D12R DEFECT** | 2 |
| 11 | `S0` dropped from **BOTH** — self-consistent, both wrong | 2 |
| 12 | a ledger with **zero `STAGE=` lines** — rule 3, a blind reader | 2 |

> **SCENARIO 0 IS THE POINT OF THE OTHERS.** A demonstration in which everything refuses proves
> only that the file refuses. **The control PASSES and every defect REFUSES**, so the refusals
> are *discriminating* and not a comparator that simply says no.

**AND THE REPAIR IS VALIDATED ON THE REAL FAILURE.** D12R's 32 real rows plus the real S0 row
this launcher now writes — measured from D12R's own mesh, `nCells = 2450`, checkMesh `Mesh OK.`,
8 polyMesh files, age guard armed — are accepted: `G12R-0b` **PASS** (33 rows, 33 ledger lines,
registered 33) and `G12R-0` **PASS** (33 stages). **This is instrument validation, NOT a grade of
D12R: D12R phase 1 is `NOT A RESULT` and that verdict stands.**

**THE BATTERY.** `EXPECTED_UNITS = 82` (frozen constant, not derived from the list it checks):
**82 registered / 82 in the list / 82 returned a result / 0 failures**, all **15** emitted gates
exercised, **0 gates emitted but never exercised**. **ZERO `assert` statements by AST** — because
`-O` deletes `assert X` and does not delete `if not X: raise`, and only statement type
distinguishes them. `--olimb` runs mutants under both flags and its `-O` limb passes.

> **COUNTING UNITS MEASURES THE BATTERY'S SIZE, NOT ITS COVERAGE.** The gate list is the
> coverage claim; 82 is not. This document says so before any number is produced.

---

## 6. GATES

Unchanged from D12R except as §3 names: `G12R-0` (completion, **refusal**, now task-aware),
**`G12R-0b` (manifest↔ledger binding, refusal, NEW)**, `G12R-1` (limit cycle), `G12R-2`
(`δ_repeat`), `G12R-3` (`δ_window` + degeneracy), `G12R-3b` (`δ_pert`, model-free), `G12R-4`
(`δ_eff := max(δ_repeat, δ_window, δ_pert)`, step sizing), `G12R-5` (plateau, positional, never
reads the adjoint), `G12R-6` (the bright line; PASS ≤ 5 %, CONDITIONAL 5–15 %, FAIL > 15 % or any
sign flip), `G12R-7` (trivial baseline at `10·h*`), `G12R-8` (envelope, `3σ`), `G12R-9` (planted
zeros), `G12R-10` (two rows), `G12R-11` (optimisation), `G12R-W` (the WHERE-control).

`h_max = 0.05`, `EPS_NOISE_TARGET = 0.01`, `W = 300`, `W2 = 900` contingency,
`MemAvailable` floor **14.0 GiB**, `TRANSIENT_DISCARD = 0` **by construction** (S2a ends at the
discard point, so its write is a **final** write).

**`δ_window` MAY NEVER BE REPORTED AS A NUMERIC ZERO.** When `|W/P − round(W/P)| ≤ 0.05` with
`P` **MEASURED** by `G12R-1`, the term is **EXCLUDED BY NAME**, `δ_window` is `None`, and the
record says it was cancelled by construction. `G12R-4` accepts an excluded term and **REFUSES a
`None` that was not flagged degenerate** — *missing is not the same as excluded.*

---

## 7. COST

Phase 1 (S0–S7): **70.0 core-min** predicted. **The basis is stated because the last ratio's
quality was not what it looked like:** D12R's ~70 was priced from the *superseded* item's stages
and D12R then **changed the stage graph**, so its 0.914 was **closer to coincidence than to
estimating skill**. This item's 70.0 is priced from **D12R's own measured 63.95 core-min on the
identical stage graph**, plus headroom for the one added artifact (the S0 manifest row, which
costs no container). **That is a like-for-like basis, and this is the first D12 prediction that
has one.** Whole item **~270 core-min** including S8.

> **REGISTERED RUNAWAY GUARD: `CAP_CORE_MIN = 600.0` total, `CAP_S8 = 350.0`**, asserted by the
> launcher against the values this document names and evaluated **before every stage**.
> **Cost constraints are LIFTED (Sanaa, 2026-08-25): these are guards reported to the
> supervisor, not budgets rigor is trimmed to fit. Equally, lifted cost is NOT a licence to let
> a known-broken run continue.**

Phase 1 derived **$0.0599** at $0.0513/core-h, c7a.4xlarge — **REPORTED-BY-OWNER, DERIVED, NOT
MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5: the box cannot read its own billing). Calibration row
owed at completion, id derived **by hand inside the committing invocation**.

## 8. STANDING CAVEATS — CARRIED FORWARD IN FULL

1. **`St` IS NEVER TO BE QUOTED AS A STROUHAL MEASUREMENT.** The measured period gives
   `f ≈ 5.26 Hz` and **`St ≈ 0.5264`**, roughly **2.6× the accepted ≈0.2**. On a **2,450-cell 2D
   URANS mesh with wall functions** that is **far more likely a RESOLUTION ARTIFACT than a
   discovery**. The estimator is **mean-crossing**, which underestimates the fundamental on a
   harmonic signal, so **18.9955 is a LOWER bound on the period and 0.5264 an UPPER bound on
   `St`**. It is a **window-sizing diagnostic and nothing else**. No mesh-convergence study is
   bought here, so the artifact hypothesis is **not tested and not refuted**.
2. **D12 MAY BE A CASE WHERE THE FD BRIGHT LINE CANNOT BE CROSSED AT ALL.** With `δ_window` at
   `1.27e-03`, direction-only arithmetic gives `h_min ≈ 1.10` against `h_max = 0.05` — **~22×
   over**. **That would be a GENUINE FINDING ABOUT THE METHOD–CASE PAIR, NOT A FAILURE OF
   EITHER**, and it is registered here in advance so it cannot later be read as a consequence of
   an instrument defect. The `G12R-4` no-admissible-step branch is a **RESULT**.
   **`G12R-4` WAS NEVER REACHED IN D12R, so no prior item is entitled to state that outcome, and
   neither is this one until the gate runs.**

## 9. WHAT THIS ITEM WILL NOT ESTABLISH

Nothing at `np > 1`; nothing about `reduceIO: False`; nothing about forward-AD or complex-step as
a reference; **no grid family, so rule 5 has no row to gate and no GCI is quoted**; **nothing
about the physical accuracy of `CD`** at `Re_D = 1.0e6` on 2,450 cells; **nothing about `St`**
(§8.1); nothing about the endpoint gradient as a gate. **The PATCHED row is UNBOUGHT unless
`--image patched` is run, and is named as unbought in any record that quotes a shipped number.**
