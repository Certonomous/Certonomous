# T5 — **DRAFT** PETITION TO `verification-supervisor` FOR A §2d.1 POST-COMPUTE GRADING-PATH RULING ON TWO LIMBS THAT MUST BE RULED SEPARATELY

> # ⚠ **DRAFT. NOT FILED. NOT SENT.**
>
> **This document has not been filed with verification and no agent may file it.**
> It was drafted by a heat-transfer lane on the heat-transfer supervisor's
> instruction; **filing it is the supervisor's act, and its content is the
> supervisor's to approve before it goes anywhere.** No message has been sent to
> the verification team about it. `CLAUDE.md` rule 7: submissions are parked, and
> readiness is not sending.
>
> **Drafted 2026-09-03. Solver compute to produce everything cited here: 0
> core-min, $0.00.**

---

## 0. THE DIRECTION TEST — **FIRST, BEFORE ANY ARGUMENT**, BECAUSE IT IS THE TEST OF THIS PETITION'S MOTIVE

**If both limbs are granted, T5 moves from an ungradeable rung toward graded rows
whose verdicts we DO NOT KNOW.** We do not know whether they would `PASS` or
`GATE FAIL`. **Nothing in this petition should be read as implying otherwise, and
we have not run the numbers through the gate to find out.**

**AND WE NAME, RATHER THAN ARGUE AROUND, THE DIFFERENCE FROM THE CASE THAT MOST
RESEMBLES THIS ONE.** `§2ai.2` (`VERIFICATION_CHARTER.md:6373`) rules:

> *"A `§2d.1` REPAIR MAY CONVERT A LANDED `NOT A RESULT` INTO A GRADED VERDICT
> ONLY WHEN THE DIRECTION IS NOT THE PETITIONER'S. Two grounds, and either
> suffices: (i) the graded verdict it lands on is AGAINST the petitioner's
> interest, or (ii) the defect was established by an instrument that cannot know
> which direction is wanted."*

**T25R6a met ground (i) outright: its repair landed on a `GATE FAIL`, against the
petitioner.** **T5's posture is materially different and we state it plainly:**

| | T25R6a | **T5, this petition** |
|---|---|---|
| pre-repair state | landed `NOT A RESULT` | landed `NOT A RESULT` |
| **post-repair verdict** | **`GATE FAIL` — known, and against the petitioner** | **UNKNOWN. Not computed. We are not able to tell verification which way it goes** |
| ground (i) available? | **yes** | **NO — the direction is not known, so it cannot be shown to be against us** |
| ground (ii) available? | yes | **argued in §4.5 and §5.5, and it is the only ground we can offer** |

**We do not argue that "unknown" is equivalent to "against us."** It is not, and
`§2ai.2`'s own closing warning — *"Had the repaired predicate landed on a `PASS`,
THIS GRANT WOULD NOT HAVE BEEN GIVEN"* — is a warning we cannot discharge by
measurement, because the measurement does not exist until the repair is made.
**Whether `§2ai.2` permits a grant on ground (ii) alone, where the direction is
unknown rather than adverse, is verification's ruling. We put the question; we do
not answer it.**

**One thing we can offer against ourselves on the direction.** The recovered `y+`
maxima (§3.4) are **all below the registered sublayer bound `YPLUS_MAX = 5.0`
and all within `2.0 ×` their level target**, so on their face the `y+` gate would
return `MET` rather than fire. **That is the direction we would prefer, and we say
so rather than let verification find it.** It decides nothing about the row
verdicts, which depend on bands, references and triples this petition does not
touch — but a supervisor testing our motive should have that fact in hand from
us.

---

## 1. THE FIVE FACTS THAT CUT AGAINST THIS PETITION, CONCEDED BEFORE ANY ARGUMENT

### 1.1 ⚠ **HEAT-TRANSFER HAS ALREADY RULED AGAINST LIMB A, IN A FROZEN DOCUMENT, IN TERMS**

`T5b_PREREGISTRATION.md:88` — a **FROZEN** pre-registration, committed
`35df9762`, 2026-08-27 — states:

> **"`postProcess` may NOT be re-run on T5's completed cases to recover `y+`."**

and at `:97`:

> **"T5's `NOT A RESULT` STANDS. It is not reopened, restated, relaxed or graded
> again by this document."**

Its stated ground (`:91-96`) is that T5 §16.3.1 registered the absence of `y+` as
`NOT A RESULT` **before compute**, that *"manufacturing the missing measurement
after the fact, specifically to escape a registered verdict, is answer-changing"*,
and it quotes Sanaa's standing directive of 2026-08-27T16:54Z §3: *"Answer-changing
choices … are never selected by agreement with the reference. … Frozen gates never
edited post-compute."*

**Limb A asks verification to rule on a question this team has already answered
against itself, in a document it froze.** We are not entitled to overturn our own
frozen ruling by re-asking it, and **we are not asking verification to bless a
change of mind — we are asking whether the ruling was right.** If verification
holds it, Limb A is closed and this petition loses half its subject.

**The same document at `:339-350` (`T5_AMENDMENT10_DRAFT.md` item A12) records the
question as expressly reserved:** *"Reserved to the supervisor, and the
registration half may be Sanaa's. The driver neither does it nor assumes it."*

### 1.2 ⚠ **THE LEGITIMATE SUCCESSOR ROUTE WAS NOT MERELY AVAILABLE — IT WAS BUILT, IT RAN, AND IT WORKED**

`T5b` is the successor rung. It repaired the configuration defect, **ran all three
levels cleanly** (`T5b_runs/STATUS.T5_CUBE_{c,m,f}`: `rc=0`, `capped=0`,
`note=clean`, **451.833 core-min actual** against caps totalling 838.4), and its
`postProcessing/air/yPlus/0/yPlus.dat` carries **30 data rows on every level**.
Its comparator reads what the solver actually writes
(`T5b_runs/analyse_t5b.py:337-345`) rather than a `yPlus.json` no producer in this
repository has ever written.

**So the argument "there is no other way to get this number" is unavailable to
us.** The number exists, lawfully, in a successor rung, obtained by the route
`§2d.1`'s own T20 ruling calls the right one (`:4540`: *"A gap in a registration
is closed by the next registration, not by repairing the rung that revealed
it."*). **What Limb A buys is not the measurement. It is T5's rows.** Verification
is entitled to weigh that as a much smaller prize than "recovering a lost
measurement", and we would rather state it than have it inferred.

### 1.3 ⚠ **§2d's OWN BOUNDARY TEST IS FAILED, UNAMBIGUOUSLY, AND WE DO NOT DISPUTE IT**

`§2d` (`:1839-1843`) fixes *"every band, every reference, every row definition,
every verdict rule, the discrimination test and the mutation control"* at the
pre-registration commit. The question that decides on-path status is whether the
change **could move a number a verdict depends on**.

**For Limb A the answer is YES and it is not close.** Without the input, **every
row is `NOT A RESULT` by `gate_yplus` (`analyse_t5.py:166-168`)**. With it, the
rows become gradeable. **That is the definition of on-path**, and no `§2ah`
off-path route is available to either limb. We claim no such route.

### 1.4 ⚠ **THE RECONSTRUCTION IS PROPOSED AFTER THE TEAM ALREADY KNOWS THE GATE RETURNS `NOT A RESULT`**

This is exactly the circumstance `§2d.1` condition (2) exists to police. The
absence was found by reading the frozen registration against the run tree, **after
the cases had solved and after the verdict was known**, and the repair being
proposed is the one that changes that verdict. `§2d.1`'s closing sentence
(`:4436`, quoted in the T20 ruling): *"Nothing a verdict depends on may be repaired
on the authority of the verdict it produces."* **We are inside the shape that
sentence forbids unless condition (2) is independently satisfied**, and §4.5 is
where we try — and where we may fail.

### 1.5 ⚠ **LIMB B's MUTATION HARNESS IS EMBEDDED IN THE FILE IT TESTS, UNLIKE EVERY OTHER MUTATION INSTRUMENT THIS FAMILY KEEPS**

`analyse_t5.A10_PROPOSED.py` carries its nine mutations at `:1547-1576` and drives
them at `:1577-1606` — **inside the file under test**, mutating
`open(os.path.abspath(__file__)).read()`. **The T-family keeps its other mutation
instruments as separate files on disk**, measured by enumeration:

| instrument | path |
|---|---|
| T20 | `verification/runs/T-family/T20_runs/mutation_controls_t20.py` |
| T20c | `verification/runs/T-family/T20_runs/mutation_controls_t20c.py` |
| T16c | `verification/runs/T-family/T16c_runs/mutation_controls_t16c.py` |
| T24 | `verification/runs/T-family/T24_runs/mutation_controls_t24.py` |
| T19b | `verification/runs/T-family/T19b_runs/mutation_controls_t19b.py` |

**`§2d.1`(2) demands an instrument INDEPENDENT OF THE HYPOTHESIS — one that grades
nothing.** The T20 grant (`:4383`) turned on exactly that property:
*"`mutation_controls_t20c.py` … grades nothing and cannot know which direction a
verdict wants, which is exactly the property `§2d.1` is cut around."*

> **WE DO NOT CLAIM THAT A SELF-HOSTED HARNESS SATISFIES CONDITION (2). WHETHER
> IT DOES IS VERIFICATION'S RULING AND WE PUT IT AS A QUESTION.** The harness
> lives in the same file as the grading code, is edited in the same commits, and
> a mutation list written by the author of the code it mutates is not obviously
> "independent of the hypothesis" in `§2d.1`'s sense. **If verification holds that
> it is not, the right remedy is to lift the harness into
> `T5_runs/mutation_controls_t5.py` before any grant, and we would rather be told
> to do that than be granted on a reading we did not earn.**

### 1.6 A FIGURE WE WERE HANDED AND COULD NOT REPRODUCE, DISCLOSED RATHER THAN REPEATED

This lane was briefed that `analyse_t5.A10_PROPOSED.py` introduces **"fourteen new
constants"**, all tracing to registered text. **We could not reproduce the figure
fourteen and we do not assert it.** What we measured:

- `T5_AMENDMENT10_DRAFT.md` §(d) (`:133-165`) enumerates **21** registered
  quantities, each with its frozen text beside it and each marked `moved? no`.
- A count of module-level `ALL_CAPS =` names present in
  `analyse_t5.A10_PROPOSED.py` and absent from the frozen `analyse_t5.py` gives
  **28** — a set that includes non-threshold names such as `MUTATIONS`,
  `LEVEL_CASE` and the `VERDICT_*` labels, so it is an over-count of "constants"
  in the sense that matters.

**Neither number is fourteen, and we do not know where fourteen came from.** The
substantive claim we do make, and it is the §(d) table's own claim, is stated in
§5.4 and is about **thresholds**, not about a count of names.

---

## 2. THE POSITION IN ONE PARAGRAPH

T5's three levels solved cleanly, and **not one row of the rung has ever been
graded**, on two independent grounds: the registered `y+` gate input was never
produced by the inline function object, so `gate_yplus` returns `NOT A RESULT` on
every row by construction; and the frozen comparator **has no grading driver at
all** — its `main()` prints completion status and stops. We ask verification to
rule, **separately and item by item, because they could be ruled differently**, on
**(A)** whether the missing `y+` gate input may be reconstructed post-compute from
the `endTime` fields already frozen on disk, at zero solver compute, via the
solver's own `-postProcess` mode; and **(B)** whether
`analyse_t5.A10_PROPOSED.py` may be adopted as the grading driver, a post-compute
change squarely on the grading path touching all six `§2d` elements. **We lead
with the facts against ourselves (§1), we state the direction test first (§0), and
on the two questions where we believe the answer may go against us — `§2ai.2`'s
direction ground and `§2d.1`(2)'s independence for a self-hosted harness — we ask
rather than assert.**

---

## 3. THE STATE THAT IS NOT IN DISPUTE — measured, with the artifact beside each

### 3.1 The rung solved. Post-compute is beyond argument.

| level | `rc` | `capped` | completion | core-min |
|---|---|---|---|---|
| `T5_CUBE_c` | 0 | 0 | `done=True — all clauses hold` | see `STATUS.T5_CUBE_c` |
| `T5_CUBE_m` | 0 | 0 | `done=True — all clauses hold` | see `STATUS.T5_CUBE_m` |
| `T5_CUBE_f` | 0 | 0 | `DONE.T5_CUBE_f` present | see `STATUS.T5_CUBE_f` |

`S_m` is a separate landed **`NOT A RESULT`** (`T5_RESULTS.md:359`, §19: the
registered solver cannot start a fluid-only case) and **this petition does not
touch it, does not re-grade it and asks nothing about it.**

### 3.2 ZERO ROWS HAVE EVER BEEN GRADED, and the absence is NAMED rather than asserted

`§2d.3` (the T20 ruling, `:4391-4397`) permits conditions (3) and (4) to be
satisfied **by disclosing an absence** — *"but the absence must be MEASURED AND
NAMED, never asserted"* — and warns that the route **"is available only while that
count is zero. The moment one graded solve exists under the registration, (3) and
(4) bite in full."**

**The count of graded rows under T5's registration is ZERO.** Named, resolvably:

- `verification/runs/T-family/T5_runs/T5_VERDICT.json` — **does not exist**
- `verification/runs/T-family/T5_runs/T5_GRADE_OUTPUT.txt` — **does not exist**
- `verification/runs/T-family/T5_runs/T5_ROWS.json` — **does not exist**
- a `find` for any `*verdict*` or `*grade*` artifact under `T5_runs/` returns
  **nothing**
- `T5_RESULTS.md:323`, the rung's own record: *"Still no graded row: the frozen
  comparator has no grading driver."*

**⚠ AND A DEFECT IN THE FROZEN COMPARATOR THAT WE FOUND WHILE MEASURING THIS, AND
REPORT AGAINST OURSELVES BECAUSE IT IS A FALSE STATEMENT IN AN ARTIFACT WE OWN.**
`analyse_t5.py:393-411`: `main()` prints per-case completion — which on the
committed logs reads `T5_CUBE_c: done=True`, `T5_CUBE_m: done=True` — and then
**unconditionally** prints

> `"No case has run: no rows are graded and no verdict is written."`

**The first clause of that sentence is false and is contradicted two lines above in
the comparator's own output** (`log.analyse_t5.20260826T223248Z.txt`). The second
and third clauses are true. **This is `L-472`'s shape — a claim and its own
refutation in one document — inside a frozen instrument.** We disclose it; **we do
not repair it in this petition and we ask for no grant covering it**, because it
emits no gate and moves no verdict. It is relevant only in that a reader who
believed that line would conclude the cases never ran.

### 3.3 The `y+` gate input was never produced, and the mechanism is measured

`T5_PREREGISTRATION.md` §16.3.1 registers five clauses of the `y+` gate, each
returning `NOT A RESULT`, including **`yPlus.json` absent → `NOT A RESULT`**. The
frozen reader is `analyse_t5.py:150-160` (`read_yplus`, path
`os.path.join(case_dir, "yPlus.json")` at `:156`) and the gate is
`analyse_t5.py:163-168`.

**`<case>/yPlus.json` does not exist in any T5 case directory**, verified by
`find verification/runs/T-family/T5_runs -name 'yPlus.json'` → **0 hits**.

**And the inline function object never emitted.** On all three levels
`T5_CUBE_*/postProcessing/air/yPlus/0/yPlus.dat` is **114 bytes: two header lines,
ZERO data rows.** The mechanism, measured:

- Both function objects carry the **identical** control —
  `writeControl writeTime; writeInterval 1000;` — preserved byte-for-byte as
  `verification/runs/T-family/T5_runs/YPLUS_RECOVERABILITY_2026-09-03/DIAG_asrun_T5_CUBE_m_controlDict.txt`.
- `wallHeatFlux` emits its table from `execute()` (`executeControl` unset → every
  timestep) and wrote **30,000 rows**. `yPlus` emits from `write()` (`yPlus.C:219`,
  inside `write()` at `:191`) and wrote **0**. Under `ocWriteTime` the fire
  condition (`timeControl.C:197-205`) is `writeTime` **and**
  `executionIndex % 1000 == 0`; the run had **five** write times, so `write()`
  never executed.
- **The mtimes settle it.** `T5_CUBE_m/postProcessing/air/yPlus/0/yPlus.dat` is
  stamped **2026-08-26 20:57:25**, at function-object construction, while
  `log.solve` and the sibling `wallHeatFlux.dat` are stamped **22:13:03**. The file
  was never touched after it was created.

Filed as **`L-480`** in `docs/LESSONS.md`, with the executable check
`scripts/check_fo_table_is_evidence.py`.

### 3.4 The measurement is recoverable at zero solver compute — **and the obvious way of recovering it fabricates zeros**

Driven on a **scratch copy** of `T5_CUBE_m`, OpenFOAM **v2606** build
`_481094f-20260618`. **No file in any T5 case directory was created or modified: a
503-file mtime-and-size manifest of `T5_CUBE_c`, `T5_CUBE_m`, `T5_CUBE_f` and
`S_m` is identical before and after.** Everything below is preserved at
`verification/runs/T-family/T5_runs/YPLUS_RECOVERABILITY_2026-09-03/`.

**Run A — the BLIND reader.** `postProcess -func yPlus -region air -time 5000`
finds no turbulence model in the registry (`yPlus.C:173`), warns on stderr,
`execute()` returns `false`, **`write()` runs anyway**, and it writes **six
well-formed rows in which every value is exactly `0.0000000000e+00`, exit code
0** (`DIAG_runA_yplus_table_ZEROS.dat`, `DIAG_runA_postProcess_blind.log`).

**Run B — the SIGHTED reader.** `chtMultiRegionSimpleFoam -postProcess -func yPlus
-region air -time 5000` loads the registry and returns genuine `y+`
(`DIAG_runB_yplus_table_NONZERO.dat`, `DIAG_runB_solver_postProcess.log`):

| patch | max `y+` | average |
|---|---:|---:|
| `cube_front` | **2.960969226** | 1.275375915 |
| `floor` | **2.389443862** | 0.7473188351 |
| `cube_top` | **1.903105528** | 0.9037585379 |
| `cube_side_n` | **1.732353011** | 0.7656388027 |
| `cube_rear` | **1.443516718** | 0.8190484404 |
| `roof` | **1.212625584** | 0.5640505831 |

The recovered patch set is **exactly** the frozen `YPLUS_WALLS`
(`analyse_t5.py:53-54`).

**The two runs are each other's live control (`CLAUDE.md` rule 3)** — same case,
same fields, same time directory, one reader blind to the quantity and one not.
**That pair is the entire reason the non-zero numbers are evidence, and it is also
a standing warning to this petition's readers: a lane that had run only Run A
would have obtained a clean `rc = 0` and a perfectly-formatted table of zeros, and
grading on it would have been grading on fabricated data — which would have
PASSED the sublayer bound.**

### 3.5 WHAT THIS TEAM DELIBERATELY DID NOT DO

**`<case>/yPlus.json` was NOT created, and nothing was written into any T5 case
directory.** Creating that file would have *performed* the repair Limb A merely
asks about. Every preserved file carries a `DIAG_` prefix and none is named
`yPlus.json`, so no glob or future reader can mistake one for the gate input.
**`T5_PREREGISTRATION.md`, `T5_RESULTS.md` and `analyse_t5.py` are untouched.**

---

## 4. LIMB A — MAY THE `y+` GATE INPUT BE RECONSTRUCTED POST-COMPUTE?

### 4.1 What is asked, precisely

> **May the registered `y+` gate input, which the inline function object never
> produced, be reconstructed post-compute from the `endTime` fields already frozen
> on disk, by running the solver's own `-postProcess` mode over those fields at
> zero solver compute — and may the result be presented to the frozen
> `gate_yplus` in the form `analyse_t5.py:156` reads?**

**Two sub-questions verification may wish to separate, and we flag them rather
than blur them:** (A-i) may the *measurement* be reconstructed at all; and (A-ii)
if so, may it be *materialised at the path the frozen reader looks for*, which is
a second change — the registration names `yPlus.json` and the solver writes
`yPlus.dat`, so a converter would sit between them and that converter is itself
grading-path code that does not exist yet and is not frozen.

### 4.2 The case FOR

1. **It is a deterministic function of fields that are already frozen.** The
   `5000/air/{U,nut,...}` fields are on disk, unaltered, and their mtimes satisfy
   the age guard against `0/T`. `y+` is computed from them by the same library
   code the inline function object would have called. **Nothing is re-solved and
   no field is regenerated.**
2. **It produces the numbers the inline function object would have written at that
   same time.** Not an approximation of them, not a substitute quantity — the same
   `yPlus` function object, on the same fields, at the same time directory.
3. **No band, threshold, row definition or verdict rule moves.** `YPLUS_MAX = 5.0`,
   `YPLUS_TARGET`, `YPLUS_TARGET_TOL = 2.0` and `YPLUS_WALLS` are the frozen
   values and stay untouched. The gate keeps all five of its `NOT A RESULT`
   clauses and can still fire on every one of them.
4. **Zero solver compute and zero cost.** Both diagnostic runs together advanced no
   timestep.
5. **The absence is a MISSING INSTRUMENT OUTPUT, not a disputed number.** No
   published `y+` value is being revised; there is no prior value to move.

### 4.3 The case AGAINST — **stated properly, not as a formality**

1. **§2d's boundary test is failed unambiguously.** *Could this change move a
   number a verdict depends on?* **YES.** Without the input, every row is
   `NOT A RESULT`. With it, the rows become gradeable. **This is the most on-path a
   change can be: it does not adjust a verdict, it creates the possibility of one.**
   No `§2ah` route is available and we claim none.
2. **The proposal is made AFTER the team knows the answer.** The gate's `NOT A
   RESULT` was established first; the repair that changes it is proposed second.
   That is the sequence `§2d.1`(2) exists to police, and it is not cured by the
   repair being cheap.
3. **This team has already ruled against it in a frozen document** — §1.1. A
   petition that asks verification to reverse the petitioner's own frozen ruling
   should carry a heavier burden, not a lighter one.
4. **The legitimate route was taken and succeeded** — §1.2. `T5b` exists, ran, and
   holds the measurement lawfully. The T20 ruling's principle (`:4540`) — *"A gap
   in a registration is closed by the next registration, not by repairing the rung
   that revealed it"* — points directly at refusal here.
5. **A-ii is a second, unfrozen piece of grading-path code.** Materialising
   `yPlus.json` requires a converter from `yPlus.dat`. That converter would be
   written now, after the answer is known, by us, and would be on the grading path.
   **We have not written it and we do not propose it in this petition** — but
   verification should know a grant of A-i alone does not by itself make the gate
   readable.
6. **`§2ai.2`'s direction ground (i) is unavailable to us** — §0.

### 4.4 The pre-repair values, and exactly what would move

Per `§2d.1`(3)/(4) and `§2d.3`'s absence-disclosure form:

| quantity | **pre-repair (published / landed)** | post-repair, if granted |
|---|---|---|
| `<case>/yPlus.json` | **DOES NOT EXIST** on `c`, `m`, `f` — `find` returns 0 hits | would exist (A-ii only) |
| `yPlus.dat` data rows, as-run | **0** on all three levels, 114 bytes | unchanged — the as-run file is preserved and not overwritten |
| `gate_yplus(<any level>)` | **`NOT A RESULT`** — *"no yPlus.json: the sublayer assumption is UNMEASURED"* (`analyse_t5.py:166-168`) | `MET` or one of four other `NOT A RESULT` clauses; **on the recovered numbers it would be `MET`, and we disclose that in §0** |
| graded rows under T5's registration | **ZERO** — `T5_VERDICT.json`, `T5_GRADE_OUTPUT.txt`, `T5_ROWS.json` all absent | still zero without Limb B; Limb A alone unblocks a **precondition**, not a verdict |
| `YPLUS_MAX`, `YPLUS_TARGET`, `YPLUS_TARGET_TOL`, `YPLUS_WALLS` | frozen values | **unchanged — 0 moved** |
| T5's rung verdict | `NOT A RESULT` | **unchanged by Limb A alone** |

**Note what this table shows and what it does not: Limb A alone grades nothing.**
It removes one of the two independent reasons no row can be graded. The other is
Limb B.

### 4.5 The four `§2d.1` conditions (`VERIFICATION_CHARTER.md:1936`), addressed one by one — **stated, not ruled**

**(1) A DEMONSTRABLE ERROR RATHER THAN A PREFERENCE — we say MET.** The function
object was configured in a way that meant `never`, and the mechanism is arithmetic
rather than taste: five write times against `executionIndex % 1000 == 0`
(`timeControl.C:197-205`), with the mtime evidence in §3.3. **Nobody chose not to
measure `y+`; the configuration silently meant "never" and nothing signalled it.**
**⚠ The honest qualification:** the *error* is in the case configuration, not in
the comparator's grading path. `§2d.1` is cut for repairs *to the grading path*.
Whether an error in the INPUT-PRODUCING configuration is the kind of error
`§2d.1` admits — as opposed to a defect that simply means the rung has no data —
**is a threshold question we cannot answer for verification, and we flag it as
possibly fatal to Limb A on its own.**

**(2) ESTABLISHED BY AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS — argued, and it
is the load-bearing condition.** We offer two candidates and rank them honestly:

- **The stronger one: the rule-3 control pair itself.** Run A and Run B grade
  nothing and know nothing about T5's bands, rows or verdicts. **Neither can know
  which direction a verdict wants.** What the pair established is not *"the y+ is
  acceptable"* but *"a reader blind to the quantity writes zeros and exits 0"* —
  a fact about instruments, not about T5. It is now an executable instrument on
  disk (`scripts/check_fo_table_is_evidence.py`), driven over 14 arms, 8 of them
  planted failures, 0 misbehaved under `python3` and `python3 -O`, and a mutant
  with its all-zero limb disabled flips exactly the two arms that limb owns.
- **The weaker one, and we mark it weaker: the mtime comparison.** `yPlus.dat`
  stamped before `log.solve` is a near-identity — a file cannot record a run that
  had not happened — and it grades nothing. **But it was computed by us, after the
  verdict was known, while looking for exactly this.** We do not think that
  disqualifies it, and we do not think our thinking so settles it.

**⚠ AND THE OBJECTION WE CANNOT ANSWER:** neither instrument was *running* before
the verdict was known. `§2d.1`'s exemplar — K0cS's heat balance — was a standing,
reported, never-gated near-identity that was already there. **Ours were built to
investigate a known failure. Whether condition (2)'s protection survives that is
verification's call and we do not claim it does.**

**(3) THE RECORD DISCLOSES IT, NAMES THE INSTRUMENT, AND QUANTIFIES WHAT MOVED —
MET, in `§2d.3`'s absence form.** This petition and
`YPLUS_RECOVERABILITY_2026-09-03/README.md` disclose the defect, name both
instruments, and quantify what moved (§4.4) — including, per `§2d.3`, **the
measured count of graded solves under the registration: ZERO**, with the
non-existent artifacts named resolvably (§3.2).

**(4) PRE-REPAIR VALUES RECORDED BESIDE THE PUBLISHED ONES — MET.** §4.4 is that
record. `T5_RESULTS.md` and `T5_PREREGISTRATION.md` stand unaltered and are struck
by this document, never rewritten (rule 6). **The as-run zero-row `yPlus.dat` is
preserved byte-identically** at
`YPLUS_RECOVERABILITY_2026-09-03/DIAG_asrun_T5_CUBE_m_yplus_table_ZERO_ROWS.dat`
(sha256 `0d913b6c…`, verified equal to the live case file), so the pre-repair state
survives any grant.

---

## 5. LIMB B — MAY `analyse_t5.A10_PROPOSED.py` BE ADOPTED AS THE GRADING DRIVER?

### 5.1 What is asked

> **May `verification/runs/T-family/T5_runs/analyse_t5.A10_PROPOSED.py` (1,791
> lines; diff at `analyse_t5.A10.diff`, 1,411 lines; frozen comparator 415 lines)
> be adopted post-compute as T5's grading driver?**

### 5.2 Why `§2ah`'s off-path route is unavailable, stated by us rather than tested against us

`§2ah` (`:6187`) exempts a post-compute change that is **off** the grading path,
and `§2ah.1` (`:6206`) rules that **off-path status is MEASURED, NEVER ASSERTED**
— *"'off-path' is the one claim a team has an interest in."*

**We do not claim it.** The proposed driver touches **all six** `§2d` elements
(`:1839-1843`): it computes bands (`band_for()`), reads the reference JSON, defines
the graded row set (`GRADED_ROWS`, `REPORTED_ROWS`,
`UNGRADED_BY_REGISTRATION`), implements the verdict rules including `§7.5`'s
six-branch order, carries the discrimination test, and carries the mutation
control. **`§2d.1` governs, in full.**

### 5.3 In its favour — measured, from the amendment's own enumeration

`T5_AMENDMENT10_DRAFT.md` §(d) (`:133-165`) is titled *"THE DEMONSTRATION THAT NO
GATE, THRESHOLD, CAP OR LABEL MOVES"* and is **enumerated with the frozen text
beside each entry rather than asserted** — **21 rows, every one marked
`moved? no`.** The substantive claim, which we do make:

> **It introduces no unregistered band, threshold or tolerance.** Every threshold
> in the driver is quoted from registered text: `§7.3`'s
> `sqrt(stated² + digitisation²)`, `§7.4`'s 1.7 % floor, `§16.3.1`'s `y+ ≤ 5.0`
> and 2.0× ladder tolerance, `§7.5`'s `Fs = 1.25`, `§16.10`'s `P_MIN = 0.05`,
> `§5.5`'s `1e-6`, `§6`'s 0.1 %/0.5 %, `§10`'s 50 %, `§7.3`'s 8 % cross-check,
> `§3`'s 5 K identity margin, `§7.1`'s 293.65 K and central-80 % window, `§9`'s
> `PLANT = 1.234e-03`.

**The single sharpest point in its favour, and it is a restraint rather than a
capability:** `FLOOR_PCT` (`:1238-1239`) registers **`None` — not `0` — for the
`T_sur` rows `G5a/G5b/G5c`**, because `§7.4` (`T5_PREREGISTRATION.md:630-634`)
scopes the 1.7 % intrinsic floor to *"every `h` row"* and names no floor for a
`T_sur` row. **Inventing one would have been adding a threshold; recording `0`
would have silently asserted "no floor" as a registered fact.** The file's own
comment says so in terms: *"a floor for the `h` rows, and None -- not zero, None
-- for G5."* **A driver that refuses to fill a gap in the registration is the
behaviour `§2d.1` is trying to protect.**

**And it retains the `y+` gate's failure mode rather than routing around it.**
Mutation **N4** is *"the `y+` gate made to pass an absent `yPlus.json`"* — the
driver mutation-tests the very clause Limb A would satisfy, **which is evidence
that Limb B does not smuggle Limb A in.** The two limbs are genuinely separable
and verification can grant either without the other.

### 5.4 Against it

1. **⚠ THE MUTATION HARNESS IS SELF-HOSTED** — §1.5, and it is the objection we
   cannot answer. **We do not claim it satisfies condition (2).**
2. **The change is very large.** 415 frozen lines → 1,791 proposed; a 1,411-line
   diff. A `§2d.1` grant on a change of that size is not the same object as a grant
   on the one-character and one-predicate repairs verification has ruled on
   recently, and **the supervisor's personal diff read (`SUPERVISION_CHARTER.md`
   §3) is owed on it in full before any grant is acted on.** This lane has **not**
   read the 1,411-line diff line by line and does not claim to have.
3. **Twelve declared ambiguities remain open** (`T5_AMENDMENT10_DRAFT.md` §(f),
   `:187-350`, items A1–A12), each expressly *"left for the supervisor's call"* —
   including **A12, which IS Limb A** (`:339-350`). **A grading driver adopted
   while twelve of its interpretive choices are unresolved is a different risk from
   a settled instrument**, and verification may reasonably require the ambiguity
   list closed before, not after.
4. **It was written after the rung's state was known.** Every line of it postdates
   the knowledge that no row could be graded.
5. **`§2p.3(e)`'s positive control is owed.** Verification ruled (`:4864`, §2p.8)
   that a restrictive repair is not self-certifying: the same run must show the
   instrument **still passes what it should pass**, driven through the production
   path over a planted input constructed to deserve a pass. The proposed driver's
   nine mutations are **negative** controls. **We do not know that a positive
   control has been driven for it, and we do not assert one.**

### 5.5 The four `§2d.1` conditions — **stated, not ruled**

**(1) DEMONSTRABLE ERROR RATHER THAN A PREFERENCE — we say MET, and the ground is
absence rather than incorrectness.** The frozen comparator **implements no grading
driver**: `main()` (`analyse_t5.py:393-411`) prints completion status for three
cases and returns 0. `§7.5` registers a six-branch verdict order; three of those
branches are not implemented at all (`T5_AMENDMENT10_DRAFT.md` §(e), `:167-186`).
**This is `§2d.5`'s shape — a REGISTERED FEATURE THAT WAS NEVER BUILT**, which the
T23G2 ruling (`:4448`) treats as *"a different legal object"* from a departure,
condition (1) being satisfied *"by reading the frozen text against the code, with
no judgement call."* **Additionally, and against ourselves: `main()` closes with an
unconditional sentence that is false on its own output (§3.2).**

**(2) INDEPENDENT INSTRUMENT — ⚠ WE DO NOT CLAIM THIS CONDITION IS MET AND WE ASK
VERIFICATION TO RULE.** The defect was found by **reading the frozen registration
against the code**, which is exactly the route the T23G2 ruling examined at
`:4492`: *"Read literally, five of six fail condition (2) and `§2d` stands on all
of them"* — before ruling that reading would be wrong, on grounds specific to that
petition. **We do not assume that reasoning transfers.** The only executable
instrument on offer is the nine-mutation harness, and it is **self-hosted** (§1.5).
**If verification holds that a self-hosted harness cannot satisfy (2), we ask to be
told to lift it to `T5_runs/mutation_controls_t5.py` and re-petition, rather than
granted on a reading we did not earn.**

**(3) DISCLOSED, INSTRUMENT NAMED, WHAT MOVED QUANTIFIED — MET in `§2d.3`'s
absence form.** Pre-repair: **zero graded rows**, artifacts named and measured
absent (§3.2); the frozen `main()` writes no verdict; three `§7.5` branches
unimplemented. Post-repair: rows `G1a`–`G3a`, `G5a`–`G5c` become gradeable and
`X_2d` stays `UNGRADED BY REGISTRATION`. **`§2d.3` warns this route closes the
moment one graded solve exists; T5's count is zero and we measured it rather than
recalled it.**

**(4) PRE-REPAIR VALUES BESIDE THE PUBLISHED ONES — MET, vacuously, and we say
`vacuously` rather than let it look stronger than it is.** There are no published
row values to record beside, because **no row was ever graded**. What is recorded
is the absence, per (3). `T5_RESULTS.md` and `T5_PREREGISTRATION.md` are untouched
and `analyse_t5.py` is not overwritten — the proposal sits beside it as
`analyse_t5.A10_PROPOSED.py`, exactly as `§2d.11.3` (`:5246-5252`) endorsed for
`T5c`: **not committing a grading path whose `§2d.1` question is unruled is the
right instinct**, and we have kept to it.

---

## 6. WHETHER EITHER REPAIR ALTERS A GATE, THRESHOLD, BAND, CAP OR LABEL

| | Limb A | Limb B |
|---|---|---|
| gates created / moved / retired | **0 / 0 / 0** | **0 / 0 / 0** |
| thresholds added / widened / narrowed | **0 / 0 / 0** | **0 / 0 / 0** (`§(d)`, 21 rows enumerated) |
| bands changed | **0** | **0** — computed from `§7.3`'s registered expression |
| caps changed | **0** | **0** — the driver launches nothing |
| labels changed | **0** | **0** |
| **verdicts that could move** | **every row, from `NOT A RESULT` to gradeable** | **every row, from ungraded to graded** |
| solver compute required | **0 core-min** | **0 core-min** |

**The last two rows are the honest answer to "does this move a number".** Both
limbs move nothing *registered* and yet **both are decisively on-path**, and we
would rather put that contradiction in a table than bury it in prose.

---

## 7. IF VERIFICATION DECLINES

**Both limbs refused.** T5's `NOT A RESULT` stands unchanged, exactly as
`T5b_PREREGISTRATION.md:97` already records. The preserved diagnostic directory
stays as a diagnostic and is cited by no verdict. **T5b already carries the
measurement lawfully**, so nothing scientific is lost — only T5's own rows, which
have never existed. **We would record the refusal and close A12 in the negative.**

**Limb A refused, Limb B granted.** The driver could be adopted, but **every row
would still return `NOT A RESULT` through `gate_yplus`**, so the rung would gain a
working instrument and no verdicts. That is a coherent outcome and we would accept
it: an instrument that correctly reports `NOT A RESULT` is worth more than no
instrument.

**Limb A granted, Limb B refused.** The `y+` precondition would be satisfiable and
**still no row could be graded**, because nothing implements the grading. Also
coherent.

**Both granted.** The rung becomes gradeable and **we do not know what it grades
to.**

**A fifth outcome we would welcome: refused ON THE INSTRUMENT, referred
prospectively**, as `R6` was (`:4540`). If the ruling is *"lift the mutation
harness out of the file, close the twelve ambiguities, and register the `y+`
reconstruction prospectively in the next rung"*, that is a refusal we can act on
and it costs no compute.

---

## 8. THE EXACT LIST, FOR RULING ONE BY ONE

| # | item | what is asked |
|---|---|---|
| **A-i** | reconstruct the `y+` **measurement** post-compute from frozen `endTime` fields via `<solver> -postProcess`, 0 core-min | **grant / refuse** |
| **A-ii** | **materialise** the reconstructed measurement at the path the frozen reader reads (`<case>/yPlus.json`, `analyse_t5.py:156`), which requires a converter that does not yet exist and would be grading-path code | **grant / refuse — may be refused even if A-i is granted** |
| **A-iii** | whether `§2ai.2` permits a `NOT A RESULT` → graded conversion where the direction is **UNKNOWN** rather than adverse (§0) | **rule** |
| **A-iv** | whether an error in the INPUT-PRODUCING CONFIGURATION, as opposed to in the comparator's grading path, is the kind of error `§2d.1` admits at all (§4.5(1)) | **rule** |
| **B-i** | adopt `analyse_t5.A10_PROPOSED.py` as T5's grading driver | **grant / refuse** |
| **B-ii** | whether a **self-hosted** mutation harness can satisfy `§2d.1`(2) (§1.5, §5.5) | **rule — we do NOT claim that it can** |
| **B-iii** | whether a grant should be conditioned on closing the twelve declared ambiguities (`§(f)`, A1–A12) first | **rule** |
| **B-iv** | whether `§2p.3(e)`'s positive control is owed before the driver's output is believed (§5.4(5)) | **rule** |
| **C** | the frozen comparator's `main()` prints *"No case has run"* unconditionally, contradicted by its own output two lines above (§3.2) | **RECORDED for awareness. NO REPAIR REQUESTED AND NONE SHOULD BE READ INTO THIS PETITION.** |

---

## 9. WHAT HEAT-TRANSFER HAS NOT DONE, PENDING THIS RULING

- **Not created `<case>/yPlus.json`, or anything else, in any T5 case directory.**
  Verified: `find … -name 'yPlus.json'` → 0 hits; the 503-file manifest of
  `T5_CUBE_c`, `T5_CUBE_m`, `T5_CUBE_f` and `S_m` is identical before and after
  the diagnostic work.
- **Not run the recovered numbers through `gate_yplus`**, so we genuinely do not
  know the verdicts (§0).
- **Not adopted, copied, committed or run `analyse_t5.A10_PROPOSED.py` against any
  real case.** It sits beside the frozen comparator, unadopted, per `§2d.11.3`.
- **Not edited `analyse_t5.py`, `T5_PREREGISTRATION.md`, `T5_RESULTS.md`, or the
  frozen `T5b` registration.**
- **Not repaired the `main()` false-statement defect at `analyse_t5.py:393-411`.**
- **Not re-graded, reopened or restated T5's landed `NOT A RESULT`, or touched
  `S_m`'s.**
- **Not filed this petition.** It is a draft; filing is the supervisor's act.

---

## 10. COST

| item | value |
|---|---|
| solver compute for everything cited here | **0 core-min, $0.00** |
| both diagnostic runs | advanced no timestep; read `5000/` and exited |
| `T5b`, cited in §1.2 as the lawful route already taken | **451.833 core-min actual** (`STATUS.T5_CUBE_{c,m,f}`: 16.783 + 87.533 + 347.517), against caps totalling 838.4 — **ratio actual/cap 0.539**, no level capped |
| if both limbs are granted | the reconstruction is **0 core-min**; the driver launches nothing |

---

## 11. ARTIFACTS THIS PETITION CITES

| artifact | what it carries |
|---|---|
| `verification/runs/T-family/T5_runs/YPLUS_RECOVERABILITY_2026-09-03/` | both diagnostic runs, the as-run defect artifact, the as-run `controlDict`, sha256 manifest, and the standing warning that it is a **DIAGNOSTIC, NOT A GATE INPUT** |
| `verification/runs/T-family/T5_runs/analyse_t5.py` | the frozen comparator — `:53-54`, `:150-160`, `:163-194`, `:393-411` |
| `verification/runs/T-family/T5_runs/analyse_t5.A10_PROPOSED.py` | the proposed driver — `:1238-1239`, `:1547-1606` |
| `verification/runs/T-family/T5_runs/analyse_t5.A10.diff` | the 1,411-line diff, **not yet read line by line by this lane** |
| `docs/campaigns/T-family/T5_PREREGISTRATION.md` | `§16.3.1` (`:1232`), `§7.4` (`:630-634`) |
| `docs/campaigns/T-family/T5_AMENDMENT10_DRAFT.md` | `§(d)` (`:133-165`), `§(e)` (`:167-186`), `§(f)` A1–A12 (`:187-350`), **A12** (`:339-350`) |
| `docs/campaigns/T-family/T5b_PREREGISTRATION.md` | **the ruling against Limb A** (`:88`, `:97`) |
| `verification/runs/T-family/T5b_runs/analyse_t5b.py` | the successor's `y+` reader (`:337-345`) |
| `docs/campaigns/T-family/T5_RESULTS.md` | `:323` *"Still no graded row"*; `:359` `S_m` |
| `docs/charters/VERIFICATION_CHARTER.md` | `§2d` `:1839`, `§2d.1` `:1936`, `§2d.3` `:4391-4397`, `§2ah` `:6187`, `§2ah.1` `:6206`, `§2ai.1` `:6338`, **`§2ai.2` `:6373`** |
| `docs/LESSONS.md` | **`L-480`** — the transferable form of the defect |
| `scripts/check_fo_table_is_evidence.py` | the executable check, 14 arms, 0 misbehaved under `python3` and `python3 -O` |

**Every line number above was read at the moment of writing, from the file on
disk, not carried from a brief. Where a figure we were handed could not be
reproduced, we said so rather than repeat it (§1.6).**

**⚠ One citation caveat, disclosed, because `§2u` — *"a witness in an uncommitted
file is not a witness"* — makes it worth stating rather than assuming.**
`docs/charters/VERIFICATION_CHARTER.md` carried **135 insertions and 3 deletions
of uncommitted working-tree drift** at the moment these line numbers were first
read. A peer has since committed it, and **every one of the seven cited charter
lines was RE-RESOLVED against the committed file and still lands on the quoted
text** — `:1839` `§2d`'s six elements, `:1936` `§2d.1`'s four conditions, `:4391`
`§2d.3`'s presupposition clause, `:6187` `§2ah`, `:6206` `§2ah.1`, `:6338`
`§2ai.1`, `:6373` `§2ai.2`. The charter's amendments append at the foot under
*"lines whose number changed above this section: 0"*, which is why they held.
**The citations are to committed bytes; we say what they were before rather than
present a re-check we did not do.**
