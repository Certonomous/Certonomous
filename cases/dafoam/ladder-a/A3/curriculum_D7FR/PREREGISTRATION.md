# CURRICULUM D7FR — PRE-REGISTRATION **v1.0. FROZEN. NOTHING HAS FIRED AT THIS COMMIT.**

**A RE-REGISTRATION OF `curriculum_D7F`, on the dafoam-supervisor's ruling of 2026-08-26 declining
`VERIFICATION_CHARTER.md` §2d.1.**

**A NEW ITEM. It gives A3 an FD table at arm `O`'s endpoint by applying D4's LANDED `D4-DEF-4`
repair.** Date drafted: 2026-08-26. Lane: dafoam `lab-lane`, on the dafoam-supervisor's direction
of 2026-08-26.

> ## WHY THIS ITEM EXISTS, AND IT IS NOT BECAUSE §2d.1 DID NOT APPLY
>
> **D7F's arm `P1` completed, `rc = 0`, 0.733 core-min — and eleven seconds of it broke D7F's own
> repair of `D7R-GRADER-DEF-7`** (`../curriculum_D7F/D7F_DEF1_TERMINAL_CLAUSE.md`, `77a12943`). The
> supervisor **ruled that §2d.1 is ARGUABLY AVAILABLE and declined it anyway**, and the reasoning
> binds this document:
>
> 1. **THE ORDINARY PATH WAS OPEN, AND AN EXCEPTION USED WHEN THE ORDINARY PATH IS OPEN IS AN
>    EXCEPTION BEING WIDENED.** Total D7F spend is **0.733 core-min — about six-tenths of one cent**,
>    and the four expensive arms never ran. Re-registering **removes** the fitting objection instead
>    of arguing it. The same reasoning was applied to D12R three hours earlier at $0.055, and **this
>    lab will not be looser with the exception on the cheaper case than on the dearer one.**
> 2. **THE TWO LIMBS POINT IN OPPOSITE DIRECTIONS.** The `.ok`-marker limb is a **TIGHTENING** — it
>    can only remove a PASS, one-way and safe after compute. The `End`-line limb is a **RELAXATION**,
>    and *a relaxation adopted after seeing that the gate would fail an arm you believe is healthy is
>    precisely the shape rule 2 exists to prevent* — **even when the belief is well founded, as it
>    is here.** §2d.1 does not distinguish the two, and **a legitimate tightening does not get to
>    carry a relaxation through on its back.** Re-registering puts the relaxation **before** the
>    compute it governs, where it belongs.
>
> ## FROZEN AT THIS COMMIT. **NO CONTAINER HAS EVER BEEN CREATED FOR THIS ITEM** (§12).
>
> **v0.9 DRAFT was committed at `01e30d85` and is superseded by this version, not rewritten** — the
> draft's §13 named five blockers and this version discharges them one by one in §13. The freeze is
> this document's entire evidentiary content: it proves the gates, thresholds, caps and labels below
> could not have been chosen to fit an answer, because at this commit there is no answer.
>
> **The whole grading path is frozen WITH the document, in the same commit** (§14): the grader, the
> two repair instruments, the two acceptance instruments and the launcher, each by md5. **And the
> grader CHECKS ITS OWN CAPS AGAINST §7 OF THIS FILE and refuses on any disagreement** — the repair
> for `D7R-GRADER-DEF-6`, applied at its cause.

---

## 0. WHAT THIS ITEM DOES TO ITS PREDECESSOR: NOTHING

**`curriculum_D7R`'s document is SUPERSEDED, CITED, AND NEVER REWRITTEN** (`CLAUDE.md` rule 6). Its
verdicts stand exactly as recorded:

| D7R arm | verdict, standing |
|---|---|
| `P1` | **`PASS`** |
| `P2` | **`PASS`** — gates `H1` and `H2` both PASS |
| `O` | **`NOT A RESULT`** — the registered grader REFUSED, and band C missed at 30.402283 % against [3 %, 25 %] |
| `F-S`, `F-P` | **`BLOCKED`** |

**Nothing in this document alters, reinterprets or softens any of them, and nothing here reopens
D7R §11.**

### 0.1 What is CARRIED FORWARD — **RECORDED, NOT IMPORTED**

**A repeat is corroboration; a departure is a finding.** Each figure below is a D7R measurement this
item will encounter again, and **this item does not assume it:**

| carried | D7R's value | artifact |
|---|---|---|
| endpoint `CD` | `2.3048932443550496e-02` | `CURRICULUM-D7R-a3-m6-cdmin/O/opt_IPOPT.txt` |
| endpoint `CL` | `0.28761081` vs target `0.2876130251655752` | same; `O/d7_cl_target.json` |
| drag reduction | **30.402283 %** | same |
| `patchV[0]`, driver-scaled | **`29.160000000000004`** | `CURRICULUM-D7R-a3-m6-cdmin/D7R_DEF4_WITNESS.txt` |
| item spend | `P1` 0.733 + `P2` 62.733 + `O` 932.533 = **995.999** core-min | `CURRICULUM-D7R-a3-m6-cdmin/ledger.txt` |

**REGISTERED PREDICTION `C1`:** this item's arm `X` will read `patchV[0]` driver-scaled as
**`29.160000000000004`** from the FINAL `OptView.hst`. D7R's witness read that value from a
**partial, mid-run copy** at 22:48, ten minutes into a run that ended at 02:31. **A different value
from the final history is a FINDING about the witness, not a correction to it.**

---

## 1. THE DEFECT THIS ITEM EXISTS TO GET PAST, AND WHY IT IS SAFE TO GET PAST IT NOW

**`D7-DEF-4`**: OpenMDAO's `pyOptSparseDriver` applies each design variable's `scaler` **before**
pyOptSparse sees the problem; pyOptSparse's own scale is `1.0`; `OptView.hst` therefore holds
**driver-scaled** values; and `d7_extract_endpoint.py:40`'s `getValues(..., scale=False)` is
**INERT**. `d7_fd_endpoint.py:134-144` then reads `d7_endpoint_dvs.json` and applies those values as
**PHYSICAL** through `prob.set_val`. `shape`'s registered scaler is **10.0**.

**IT IS CONFIRMED BY MEASUREMENT, TWICE, AGAINST A PREDICTION FROZEN BEFORE THE ARTIFACT EXISTED**
(`5551db3d`, before any `OptView.hst` existed anywhere on this box — so it could only be confirmed or
refuted, never fitted):

* `patchV[0]` read **`29.160000000000004`**; registered prediction `291.6 × 0.1 = 29.16`. **The
  component is PINNED** (`d7_opt_runScript.py:241`, `lower[0] == upper[0] == U0`), so no optimiser
  can move it and its physical value is definitional.
* `patchV[1]` read **`0.30600000000000005`** `= 3.06 × 0.1` — **a second confirmation the prediction
  did not claim.**

**THE STANDING RULING IS THAT D7 INHERITS D4'S REPAIR RATHER THAN AUTHORING ITS OWN** (D7R §6): two
instruments would mean two chances to reintroduce a units error that is invisible to every count-,
plant- and order-based control in this family.

---

## 2. THE REPAIR — AND **THERE IS NO EXTRACTOR DIFF**

**D4's landed repair edits ZERO BYTES of any frozen file. That is its central property, not an
omission from it.** It is a **wrapper** that hashes the frozen extractor, imports it under a module
name that is not `__main__`, runs the frozen bytes, and corrects **downstream** of them.

**The supervisor asked for the extractor diff. The diff is empty, and the empty diff is the point:**

    $ diff cases/dafoam/ladder-a/A3/curriculum_D7/d7_extract_endpoint.py <the file arm X runs>
    (no output — byte-identical, md5 651d40c78cc52288a856934c108d1334, asserted at C1 before use)

**The reviewable artifacts are instead the two NEW instruments**, both committed with this document:

| instrument | ported from | what changed |
|---|---|---|
| `d7fr_endpoint_locus.py` | `../../A2/curriculum_D4/d4_endpoint_locus.py` | **the parser and BOTH controls are carried byte-for-byte.** Mechanical renames only, plus the self-test's real-source plant retargeted to D7's file and D7's registered values |
| `d7fr_endpoint_physical.py` | `../../A2/curriculum_D4/d4_endpoint_physical.py` | filenames `d4_*`→`d7_*`; the two frozen md5s replaced by **D7R §10's**; the authority paragraph extended |

**Retyping either file would have risked a transcription error in exactly the part that must not
change** — the same argument D7R §10 made for its launcher, and the reason both ports were produced
by verified token substitution with every substitution's occurrence count printed.

### 2.1 SATISFIABILITY, PROVEN BEFORE THE FREEZE AND NOT ASSERTED

**The single largest risk in the port was that D4's parser cannot read D7's registration.** It was
measured first, and it can:

    d7fr_endpoint_locus.parse_registration("d7_opt_runScript.py")
      U0     291.6                                    READ from the source, not typed
      twist  lower -10.0  upper 10.0   scaler 0.1
      shape  lower  -1.0  upper  1.0   scaler 10.0
      patchV lower [291.6, 0.0] upper [291.6, 10.0]  scaler 0.1

**`patchV[0]` is pinned, so `CONTROL P` HAS A WITNESS and does not refuse itself** (L-302).

**`d7fr_endpoint_locus.py --selftest`: 22 units, 22 PASS**, byte-identical under `python3 -O`;
**`ast.Assert` nodes: 0**. Among those 22, and these are the ones that matter:

* the **real D7-DEF-4 vector** makes **both** controls refuse — `CONTROL B` reporting
  `excess: 262.44` on `patchV[0]` (`291.6 − 29.16`);
* `mutant/pinned left driver-scaled (29.16 == THE MEASURED D7 WITNESS)` — **refuses**;
* a registration with **no** pinned component makes `CONTROL P` **refuse itself**;
* a pinned value off by `1e-13` does **not** fire, and off by `1e-9` **does** — the tolerance is a
  representation tolerance, four orders tighter than the smallest defect it exists to catch, and it
  cannot be tuned to admit one because no defect lives in that gap.

**`d7fr_endpoint_physical.py`'s refusal chain was DRIVEN, not read:**

| condition driven | result |
|---|---|
| `--age-datum` omitted | **REFUSE** — "without it C3 cannot distinguish this arm's artifact from a stale one" |
| extractor absent | **REFUSE** `C1 ... absent` |
| extractor present but **not the frozen bytes** | **REFUSE**, with both md5s printed |
| both frozen instruments present | **C1 OK, C2 OK**, then the **frozen extractor's own** refusal fires: `D7_EXTRACT REFUSE history file OptView.hst absent` |

**The last row is the important one: the frozen bytes do the extraction and the frozen bytes do the
refusing.**

---

## 3. HOW `D7R-DEF-8` AND `D7R-DEF-9` ARE FIXED, PER ARTIFACT, BY ARM AND BY LINE

**An arm plan whose launcher cannot produce the artifacts its grader requires must not be frozen a
second time.** D7R's launcher invoked `d7_extract_endpoint.py` in **one place only — line 325,
inside the `F-S`/`F-P` branch that §6 blocked** — so arm `O` could never write
`d7_major_history.json` or `d7_endpoint_dvs.json`, and the grader refused at `G2`.

**REQUIRED-ARTIFACT TABLE. Every artifact the grading path reads, the arm that writes it, and the
line that writes it. A freeze is not legal until every cell below is filled and checked.**

| artifact | read by | written by arm | written at |
|---|---|---|---|
| `d7_endpoint_dvs_DRIVERSCALED.json` | `H3`, the record | **`X`** | `d7fr_endpoint_physical.py` C4 |
| `d7_endpoint_dvs_PHYSICAL.json` | `H3`, `d7_fd_endpoint.py` | **`X`** | `d7fr_endpoint_physical.py` C8 |
| `d7_endpoint_dvs.json` | `d7_fd_endpoint.py:134` | **`X`** | `d7fr_endpoint_physical.py` C9 |
| `d7_major_history.json` | `G2` bands A/B, `G4` cross-check | **`X`** | the **frozen** `d7_extract_endpoint.py`, invoked at C3 — **VERIFIED: `d7_extract_endpoint.py:21` writes it** |
| `opt_IPOPT.txt`, `OptView.hst` | `G1` age guard, `G3`, `G4` | **inherited from D7R arm `O`** — gate `H4`, §5 | `d7fr_run_arm.sh` `stage_endpoint()`, by md5 |
| `_final_CD` / `_final_CL` in the DV artifact | **`ACC-1`'s target cross-check** | **`X`** | the **frozen** extractor's `out["_final_" + short]`, `d7_extract_endpoint.py:68`, carried through the wrapper's C8 `dict(scaled_doc)` |
| `d7fr_accept_primal.json` | `ACC-1` | **`ACC`** | `d7fr_accept_primal.py`, rank 0, fsync |
| `d7fr_accept_verdict.json` | the `F-S`/`F-P` launch gate (`LIMIT 1`) | **`ACC`** | `d7fr_accept_compare.py --out` |
| `d7fr_locus_gate.json` | `H3` | **`X`** | `d7fr_endpoint_locus.py --gate` |
| `d7_fd_endpoint.json` | `G5` (the bright line), `G6`, `G6b`, `G7` | **`F-S`, `F-P`** | `d7_fd_endpoint.py` |
| `d7_decomp_A/B.json` | `G8` | **`P1`** | launcher `P1` branch |
| `d7_placement_rank*.json` | `G12` | every arm | launcher, each branch |
| `ledger.txt` | `G1`, `G9`, `G10`, `G11`, `G12` | launcher | every arm |

**`D7R-DEF-9` IS FIXED BY ARMING `F-S` AND `F-P`.** `map_verdict` hard-fails `G6`/`G6b`/`G7` on
**absent** FD artifacts; D7F's whole purpose is to produce them, so the absence that made D7R's
registered outcome unreachable does not arise. **`G9` — two rows carrying DISTINCT IDWarp `.so`
md5s — becomes reachable for the first time in this family's A3 line**, because `F-P` is armed.

**FALSIFIER `F-SAT`, registered here:** if, at the moment of freezing, any cell of the table above
is unfilled, **THE ITEM IS NOT FROZEN.** This is checked by re-reading the launcher, not by
recalling it. **DISCHARGED AT THIS COMMIT: every cell is filled and the launcher was re-read to fill
it.**

> **AND THE TABLE EARNED ITS KEEP BEFORE THE FREEZE, WHICH IS THE POINT OF HAVING IT.** While
> filling the `_final_CD` row I could not find that string anywhere in `d7_extract_endpoint.py` and
> was one step from recording that `ACC-1` could never grade — **the same `D7R-DEF-8` shape,
> reproduced inside its own repair.** It resolves the safe way: line 68 builds the key by
> *concatenation*, `out["_final_" + short]` for `short in ("CD", "CL")`, so a literal search for
> `_final_CD` finds nothing while the key is written on every run. **D4's own landed acceptance
> artifact carries `endpoint_final_CD_from_history: 0.021125978108239574`, which is D4's `CD_OPT` to
> all digits — the chain is not merely plausible, it has run once.** Recorded because the near-miss
> is the evidence that the table is a check and not a formality.

---

## 4. BAND C DOES NOT ARISE IN THIS ITEM, AND I AM NOT REGISTERING A NEW ONE

**The supervisor put this as a live question and offered the honest exit. I am taking it.**

**I cannot justify a drag-reduction band from the physics and the case without pointing at
30.4 %, and I am not going to pretend otherwise.** D7's [3 %, 25 %] was reasoned from a comparison
with D4's A2 band; nothing I can say about M 0.84 shock-dominated transonic drag on a 42,120-cell
ONERA M6 predicts a *ceiling* to better than a factor of two. Any number I proposed today would be
chosen by somebody who already knows the answer, and **`CLAUDE.md` rule 2 exists precisely because
that choice is undetectable afterwards.**

**IT DOES NOT MATTER, BECAUSE D7F RUNS NO OPTIMISER.** This item takes arm `O`'s endpoint as given
and measures a **gradient** there. **It produces no drag reduction of its own, so there is nothing
for band C to gate.**

* **The 30.402283 % is carried as a RECORDED D7R number, REPORTED AND NOT GATED** (§0.1). No gate in
  this item reads it, and **no verdict of this item may be stated in terms of it.**
* **The bright line here is `G5`** — endpoint FD versus adjoint, band D, **5.0 % per component and
  5.0 % aggregate**, inherited unchanged and **not re-derived by a lane that has seen an answer**,
  because **no D7 FD number exists yet in any direction.** That band was frozen at `0e229a0a` before
  any FD artifact existed and it is the one band in this family a re-registration cannot be accused
  of fitting.

---

## 5. GATES

`G1`–`G13` are graded by **`d7fr_grade.py`**, this item's own port, md5
**`923662ef398ca229cc3734699670418a`** (§14) — **not** D7's blob, and §6 says exactly what changed
and why. **`G10` IS SPLIT INTO TWO LIMBS AND THE SPLIT IS REGISTERED HERE, BEFORE COMPUTE:**

| limb | what it checks | disposition |
|---|---|---|
| **`G10` LIMB 1** | **`enforced cap == REGISTERED cap`, per arm, READ BACK OUT OF THE LEDGER THE LAUNCHER WROTE**, never from the launcher's claim | **GATES.** It is an integrity check that the launcher enforced what this document registered — the `D7R-DEF-8` / D12R class, a launcher and a document disagreeing, which bit this family three times in one night. `g10_caps`'s `pass` is this limb **and this limb alone** |
| **`G10` LIMB 2** | **`actual ≤ cap`** | **REPORTED, GATES NOTHING.** Under §7's reporting-cap design this limb **is** the runaway guard, and a runaway guard that hard-fails a grade contradicts its own purpose. Precedent for registering a reported-not-gating channel in advance: D4's `ACC-2` (*"REPORTED, GATES NOTHING, exactly as registered"*) and D12R2's steady-stage step proxy (*"recorded and REPORTED, never gated"*) |

> **NON-GATING IS NOT NON-REPORTING, AND THAT IS THE HAZARD ATTACHED TO IT.** *A printed discrepancy
> labelled "diagnostic only" is worse than one never computed.* **Every limb-2 crossing is reported
> with its number in core-minutes AND in derived dollars, in the RESULTS headline and in the cost
> calibration row — never in a footnote and never as a bare "within tolerance".** The grader emits it
> under the key `LIMB2_REPORTED_NOT_GATING__CARRY_INTO_HEADLINE`, so a reader who lifts `G10`
> cannot lift it without seeing the crossing and a lane that omits it has dropped a key whose own
> name says it may not be dropped. **A quiet overrun is a defect.**

**AND `G1`'s COMPLETION EVIDENCE IS ARM-KIND AWARE FROM BIRTH, REGISTERED HERE BEFORE THE COMPUTE
IT GOVERNS.** This is the relaxation half of `D7F-DEF-1`, and it is registered rather than repaired
after the fact for exactly the reason the supervisor gave.

**The rule is NOT "accept absence". It is "ask the right question, and refuse if it cannot be
answered."** A Python arm that runs no solve emits no `End` line **by design**, so demanding one asks
a solver question of a non-solver — the same shape as D12R2's status limb and `[D4]`'s step-count
limb. **Every kind must present SOMETHING, and no kind is exempt.**

| arm kind | which arms | what it MUST present | why that and not an `End` line |
|---|---|---|---|
| **`SOLVER`** | `ACC`, `F-S`, `F-P` | **an `End` line in the arm's own log** | these run `mpirun` DAFoam primals, which do print one |
| **`DECOMPOSE`** | `P1` | **`d7_decomp_A.json` AND `d7_decomp_B.json`** — the maps the arm exists to write | `decomposePar`'s output is redirected into `d7_decomp_{A,B}.log` **inside the work directory**, so the arm log never sees an `End`. **MEASURED: `grep -c '^End'` is `0` on D7F's `P1` log and on BOTH of D7R's** |
| **`PYTHON`** | `X` | **`d7_endpoint_dvs_PHYSICAL.json`**, its own named output | it runs no OpenFOAM solve at all |

**THE KINDS ARE READ OUT OF THE LAUNCHER, NEVER TYPED INTO THE GRADER.**
`d7fr_grade.py:parse_arm_kinds()` parses `d7fr_run_arm.sh`'s own `case "$ARM" in` command branches
and classifies each. **A table copied by hand drifts from the file that actually runs the arms —
which is `D7R-GRADER-DEF-6` one level up.** Measured against the real launcher, the parser returns
`{P1: DECOMPOSE, X: PYTHON, ACC: SOLVER, F-S: SOLVER, F-P: SOLVER}`. **An arm whose kind cannot be
determined is a REFUSAL, and an absent or unparseable launcher is a REFUSAL** — never a pass.

**AND THE COMPLETION MARKER NOW MEANS COMPLETION.** D7F's launcher wrote
`test -s "$LOG" && touch "$LOG.ok.$STAMP"` — **a non-emptiness test wearing a success name**, which
would have read a container that crashed after one banner line as clean. This launcher writes
**three distinguishable outcomes**, and the third is what a bare `.ok`/no-`.ok` pair could never
express:

| marker | meaning |
|---|---|
| `.ok.<stamp>` | the producer ran **and returned `rc = 0`** |
| `.fail.<stamp>` | the producer ran **and returned `rc != 0`**, with the `rc` in the file |
| **neither** | **the launcher itself died before recording an outcome — the arm is `UNKNOWN` and is NOT read as either** |

Three gates are added:

| gate | threshold | refusal |
|---|---|---|
| **`H3`** | the published `d7_endpoint_dvs_PHYSICAL.json` re-passes `CONTROL P` and `CONTROL B` **at grading time, re-read from disk** — never on the producer's say-so | `d7fr_endpoint_locus.py --gate` refuses; the FD table is at the wrong design point |
| **`H4`** | the `OptView.hst` and `opt_IPOPT.txt` arm `X` reads were produced by **D7R arm `O`**, identified by md5 against `CURRICULUM-D7R-a3-m6-cdmin/O/`, and are **strictly older** than this item's launch datum while every artifact **derived** from them is strictly newer | `ENDPOINT_PROVENANCE` — refuses an unattributed or re-run endpoint. **The age guard runs in BOTH directions here and that is deliberate: an inherited input must be OLD, a produced output must be NEW, and one rule cannot say both** |
| **`ACC-1`** | **`LIMIT 1`.** One primal at the corrected physical design point reproduces arm `O`'s IPOPT objective `CD = 2.3048932443550496e-02` to **≤ 1e-3 relative** | the repair is **NOT FROZEN** and no FD number from it is graded. D4's own ACC-1 measured `2.34e-4` against this same band with a planted-zero control that PASSED |

**`ACC-1` IS A PRECONDITION OF THE FREEZE OF THE REPAIR, NOT A FOLLOW-UP.** Two controls that grade
nothing say the corrected point is *self-consistent with the registration*. **Only a solve says it is
the optimum.** **The launcher enforces it mechanically**: arms `F-S` and `F-P` refuse to start unless
`ACC/d7fr_accept_verdict.json` exists and reads `"verdict": "PASS"`.

**GATE `H1` IS NOT CARRIED FORWARD, AND THAT IS A DISCLOSURE, NOT AN OMISSION.** D7R needed `H1`
because a colouring cache built by one arm was inherited by another and the `.bin.info` sidecar could
not refuse a foreign one. **This item inherits no colouring: `F-S` and `F-P` each BUILD FRESH, and
§7 prices the build into BOTH of them at 24.2 core-min each.** The price of dropping the gate is
24.2 core-min on arm `F-P`; the gain is one whole class of provenance risk removed. **A gate dropped
is disclosed; a gate quietly omitted is a defect.**

---

## 6. THE THREE INHERITED GRADER DEFECTS — **REPAIRED AT THEIR CAUSE, NOT DECLARED AWAY**

**D7R §5 claimed its gates were "inherited unchanged". That was true of the logic and FALSE of three
thresholds, and this item does not repeat the claim — it ports the instrument and fixes it.**

**The v0.9 draft asked the supervisor to assent to declaring `G10` non-binding. THE SUPERVISOR
REFUSED THE DECLARATION AS FRAMED AND WAS RIGHT TO** (ruling 3, 2026-08-26): *"declaring a gate
non-binding because your instrument carries the wrong numbers is repairing the RECORD instead of the
INSTRUMENT, and it would trade a five-minute fix for a permanent blind spot."* **This item is a new
item porting a new instrument; no frozen file stood in the way; the remedy for a wrong constant is
the right constant.**

| id | what it was | what this item did |
|---|---|---|
| **`D7R-GRADER-DEF-6`** | the ported grader hard-coded **D7's** `CAPS = {P1 8.0, P2 60.0, O 600.0, …}` and `ITEM_CEILING = 928.0` against D7R's registered 900.0 and none, so `g10_caps` read `overrun_core_min: 332.533` against a threshold that was never D7R's | **REPAIRED AT ITS CAUSE.** `d7fr_grade.py` carries **this item's** `CAPS`, `CEILINGS` and `PREDICTED`, and `ITEM_CEILING_CORE_MIN` is **derived by `sum(CEILINGS.values())`, not typed.** And they are **CHECKED, NOT COPIED**: `assert_caps_against_document()` parses **§7 of this file** and REFUSES on any disagreement. **Measured at the freeze: 15 values checked (5 arms × cap, ceiling, prediction), all agreeing.** Driven both ways — moving one cap by 1.0 in a copy of this document makes it refuse and name the arm and the field; an unparseable document makes it refuse by count (L-302). An arm with no registered cap **refuses** rather than being skipped |
| **`D7R-GRADER-DEF-7`** | `g1_completion`'s docstring named three clauses and implemented two; in that whole 74,338-byte file the string `End` occurred **exactly once — inside the docstring that claimed the check** | **REPAIRED.** The terminal clause is now executable: it reads the **producer's own log FILE** — not the ledger's summary of it — and requires an `End` line **and** the `.log.ok.<stamp>` marker. **Driven in both directions in the selftest**, each mutant first asserting *that the mutation applied* so no unit can pass vacuously: marker removed → fails; `End` removed → fails; log absent → fails and is **not read as clean**; restored → passes again, so the clause is not a one-way switch. **`scripts/check_docstring_clauses.py` (L-335) reports `d7fr_grade.py:g1_completion` as `RC_ZERO OK / LOG_TERMINAL OK / AGE_GUARD OK`, 0 alibis — against `d7_grade.py:g1_completion`'s 1 alibi, run side by side** |
| **`D7R-GRADER-DEF-5`** | the `--selftest` exit contract the file documents ("exit 3, used by nothing else") is not the one it has: success returns **0**, the same code a clean grade returns | **NOT repaired, and handled instead — because changing an exit contract is the kind of change that breaks a caller silently.** The selftest's result is read from its **stdout** `D7FR_SELFTEST units=… passed=… failed=…` line and from the **absence** of an `--out` file, **never from its exit code**, and this record says so before compute so no reader of it infers a grade from an exit 0 |
| **`D7F-DEF-1`** | **the defect that caused this re-registration, and it was mine.** D7F's repair of `D7R-GRADER-DEF-7` demanded an `End` line of **every** arm and cited a `.ok` marker that meant only *log non-empty*. `G1` is a **hard** gate, so a full grade would have returned `NOT A RESULT` on a **healthy `rc = 0` P1** — after the FD arms had spent 970.0 core-min — while the other limb would have **passed** an arm that crashed after printing a banner | **BOTH LIMBS REGISTERED BEFORE COMPUTE, HERE, and DRIVEN.** §5's kind table and marker table are the repair. **A THIRD CLASS, distinct from L-335's `ABSENT` and from `VACUOUS`: the clause was PRESENT, NOT VACUOUS — it fired, and I drove it firing — AND POINTED AT THE WRONG EVIDENCE.** `check_docstring_clauses.py` reported it `OK` and was right to. **And the selftest could not have caught it because I WROTE THE FIXTURE**: my fixture log contained `End` because I put it there, so it encoded the same assumption twice and tested it zero times |
| **`D7F-ACC-DEF-1`** | **found while porting, and it is a `-O` exposure**: D4's landed `d4_accept_compare.py:199` guards its verdict vocabulary with a bare `assert verdict in VOCAB`, and **`python3 -O` deletes it** — so under `-O` nothing stands between that instrument and a token outside `CLAUDE.md` rule 1's fixed vocabulary | **REPAIRED IN THIS PORT ONLY.** `d7fr_accept_compare.py` raises a real refusal instead. **D4's frozen file is NOT edited** and the finding is reported to the supervisor. `ast.Assert` nodes across all five of this item's new instruments: **0** |

## 7. ARMS, CAPS, CEILINGS AND COST — priced from **D7R's own measured arms**

| arm | task | row | **prediction (core-min)** | **CAP** | **CEILING** |
|---|---|---|---|---|---|
| `P1` | decomposition determinism ×2 + placement | SHIPPED | **0.75** | 8.0 | 32.0 |
| `X` | the `D7-DEF-4` repair: frozen extractor + `CONTROL P`/`B` + PHYSICAL artifact | SHIPPED | **2.0** | 15.0 | 60.0 |
| `ACC` | **`LIMIT 1`** — one primal at the corrected point | SHIPPED | **25.0** | 60.0 | 240.0 |
| `F-S` | endpoint FD, 5 components | SHIPPED | **485.0** | 750.0 | 3000.0 |
| `F-P` | endpoint FD, 5 components | **PATCHED** | **485.0** | 750.0 | 3000.0 |
| | | | **ITEM 997.75** | | |

**EVERY TERM IS A D7R MEASUREMENT, AND THE ONE PLACE THE LOGS CANNOT ANSWER IS NAMED AS SUCH.**

* `P1` **0.75** — D7R `P1` measured **0.733**.
* `X` **2.0** — the D7R `D7-DEF-4` witness probe was the same shape of container and **its cost was
  never recorded**; 2.0 is a **guess bounded by `P1`'s measured 0.733 and by `X` doing strictly more
  I/O and no solve.** It is labelled a guess, not a measurement, and the cap is 7.5× it.
* `ACC` **25.0** — one converged primal. See the primal basis below.
* `F-S`/`F-P` **485.0** = **22 primals × 20.27** + **24.2 colouring** + **14.6 cold `compute_totals`**.

> **THE PRIMAL COST IS AN UPPER BOUND AND IS REGISTERED AS ONE.** D7R's logs **cannot separate**
> primal from adjoint: arm `O` interleaves them inside single OpenFOAM runs. What IS measurable is
> that arm `O` spent **932.533 core-min** delivering **46 objective evaluations** and 31 gradient
> evaluations (`O/opt_IPOPT.txt` summary block). **Charging the WHOLE arm to its objective
> evaluations alone gives 20.27 core-min/primal, which necessarily OVERSTATES a primal**, because it
> bills the adjoints to it. **This item registers the overstatement rather than a decomposition it
> cannot measure**, and the calibration row will report the ratio honestly as a deliberate
> over-prediction if it comes in low.
>
> **The colouring is priced with a number, per `C-89`: 24.2 core-min**, measured from **D7R's own**
> `P2` log — `Calculating dRdW Coloring... 34.74 s` → `Completed! 397.31 s`, 362.57 s × 4 ÷ 60 =
> **24.17**. D7R registered 24.43 from D7's log and measured 24.17 in its own: **ratio 0.99.**
> **This item BUILDS FRESH** (D7R §R3's ruling, unchanged: the `.bin.info` sidecar carries no mesh
> identity, so no cache control that can refuse is designable).
>
> **The 14.6 cold `compute_totals`** is D7R §4's adjoint term, which was registered there as a
> **FLOOR** and is still one.

**WASTE, NAMED SEPARATELY AND NEVER ABSORBED INTO ANY RATIO** (`COMPUTE_BUDGET_CHARTER.md` §6):
**D7F arm `P1`, 0.733 core-min, $0.0006 DERIVED.** It returned `rc = 0` and its numbers were sound —
`0.733` against a registered `0.75`, **ratio 0.977** — but **the item it belonged to is superseded,
so the spend bought a finding and not a graded row.** It is carried here as **RECORDED, NOT
IMPORTED**: this item's own `P1` re-measures it, and **a repeat is corroboration while a departure is
a finding.** It is **not** subtracted from this item's prediction and **not** folded into its ratio.

**Cost basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Item **997.75** core-min → **$0.8531 DERIVED**.

**THE CAP REPORTS AND THE CEILING STOPS** — D7R §R1's design, carried forward unchanged, **and the
charter question it raises is referred to Sanaa's desk and is NOT answered by this document.** Until
it is ruled, this item registers both thresholds and the record names which one acted.

---

## 8. TOOLCHAIN — two rows, by digest, never by tag

| row | image | digest | `libidwarp.so` md5 |
|---|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` |
| **PATCHED** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` |

**Both digests were RE-MEASURED LIVE on 2026-08-26** by `docker inspect` and landed in
`docs/dafoam/TOOLCHAIN_INVENTORY.md` Amendment 1 — which, until that amendment, **named
`dafoam-idwarp-rot:v1` nowhere at all.** `DAFOAM_CHARTER.md` §11: the hash is the identity; **both
libraries report IDWarp `2.6.2` and both are 491,344 bytes**, so the version string discriminates
nothing.

**`F-P` IS ARMED, SO THIS ITEM CAN BE A TWO-ROW DAFOAM VERDICT — AND IT IS NOT ONE UNTIL `F-P`
RETURNS `rc=0` AND `G9` SEES TWO DISTINCT `.so` md5s.** If `F-P` is blocked or fails, **the record
says SHIPPED-only and says so in its headline**, exactly as D7R's did.

---

## 9. STRICT COMPLETION, THE AGE GUARD, AND THE COLD GUARD

`CLAUDE.md` rule 4: `rc = 0`; an `End` line; the `.log.ok.<stamp>` marker; fields present; every
**produced** artifact strictly newer than the arm's launch datum. **A guard refuses a case whose arm
directory already holds a time directory, `processor*`, `reports/`, an `OptView.hst`, a colouring
cache or any `d7_endpoint_dvs*.json`. A guard that refuses is the guard working and is never
disabled to get past it.**

**`H4`'s inherited-input clause runs the age comparison the other way** (§5) and the two directions
are registered separately so neither is mistaken for the other.

---

## 10. WHAT WOULD MAKE THIS ITEM A FAILURE — registered in advance

* **`ACC-1` misses its 1e-3 band** → the repair is **NOT FROZEN**, no FD number is graded, and that
  is a finding about the reconstruction, recorded before any regrade.
* **`CONTROL P` or `CONTROL B` refuses on the real vector** → the endpoint is not where the
  registration says it is; **`NOT A RESULT`**, and the FD arms do not run.
* **`G5` fails band D** → **`GATE FAIL`**, reported as a miss and **never re-banded**.
* **Any `G8` failure** → every np=4 number in this item is **`NOT A RESULT`**.
* **`F-P` blocked or `rc≠0`** → **not a two-row verdict**, said in the headline.
* **The grader refuses again on real artifacts** → a finding **before** any regrade, and §3's table
  is what will have been wrong.
* **`F-XCHK`, registered because it cannot be tested before compute.** `d7fr_accept_compare.py`
  cross-checks its typed `CD_OPT` against the `_final_CD` the frozen extractor selected, at `1e-15`
  relative, and **refuses** on a mismatch — so a typo in the comparator cannot pass silently. **The
  extractor takes the LAST row of `OptView.hst`, and D7R's arm `O` log prints CL values from
  post-optimisation evaluations AFTER the IPOPT summary.** If the history's last row is one of those
  rather than the final major, `_final_CD` will not equal `2.3048932443550496e-02` and **`ACC-1`
  will refuse.** That refusal is **a finding about which row the extractor selects**, recorded
  before any regrade, and **the tolerance is not widened to admit it.** It cannot be settled before
  compute because reading `OptView.hst` requires `pyoptsparse`, which lives only in the container.

## 11. PREDICTIONS, REGISTERED BEFORE COMPUTE

| id | prediction |
|---|---|
| `C1` | arm `X` reads `patchV[0]` driver-scaled as **`29.160000000000004`** from the FINAL history |
| `C2` | after descaling, `patchV[0]` reconstructs to **`291.6`** inside `1e-12` relative and `CONTROL P` passes |
| `C3` | **`CONTROL B` will find `shape` components outside `[-1, 1]` in the DRIVER-SCALED vector** — D4 measured 62 of 96. **A driver-scaled vector with every `shape` component inside its bounds would mean the endpoint barely moved, and that would contradict a 30.4 % drag reduction** |
| `C4` | `ACC-1` lands inside `1e-3`; D4's landed at `2.34e-4` |
| `C5` | `G5` **PASSES** band D on at least 4 of 5 components. **Registered as UNLIKELY-to-be-clean on `shape[115]`**, which A3 rung 2 measured at `0.0172 % → 0.1586 %` and rung 1 at `0.9273 % → 0.3826 %` — **the same component has moved in opposite directions on two rungs of this ladder** |
| `C6` | `F-S` and `F-P` return **DISTINCT** `.so` md5s and `G9` passes for the first time on this A3 line |

## 12. CONDITION AT THE FREEZE COMMIT, TAKEN HERE

**Taken at 2026-08-26T04:10:53Z**, at this commit's own clock.

| check | reading |
|---|---|
| run root `/home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd` | **0** — does not exist |
| containers named `d7fr_` | **0** — none has ever been created |
| arm directories `P1 X ACC F-S F-P` | **0 of 5** |

**D7F's run root still exists and is NOT deleted, reused or written by this item** — it holds arm
`P1`'s evidence and the `D7F-DEF-1` finding, and `G-ROOT.2` **names it a forbidden root** so this
launcher cannot touch it.

---

## 13. THE SUPERVISOR'S SIX REQUIREMENTS FOR THIS DOCUMENT, DISCHARGED

| # | requirement | discharged |
|---|---|---|
| 1 | **evidence selection ARM-KIND AWARE FROM BIRTH**; name which evidence is admissible per kind, and require every kind to present some | **§5's kind table.** Kinds **read out of the launcher**, not typed. `{P1: DECOMPOSE, X: PYTHON, ACC/F-S/F-P: SOLVER}` measured against the real file. **Undeterminable kind → REFUSAL; absent or unparseable launcher → REFUSAL** |
| 2 | **a success marker that means success** | **§5's marker table.** `.ok` on `rc = 0`, `.fail` on `rc != 0` with the `rc` in the file, **neither = `UNKNOWN`**. `G-ROOT.4` recognises both markers |
| 3 | **DEMONSTRATE both limbs by making the conditions occur**, under `python3` and `-O` | **§14.1**, and the decisive one is against a **REAL** arm, not a fixture |
| 4 | **P1 carried RECORDED-not-imported; the 0.733 becomes WASTE, named separately** | **§0.1 and §7** |
| 5 | **`G-ROOT` from birth** | **in the launcher at lines 50–89 and 193–209, above every destructive act**, with D7F's own run root among the named forbidden roots |
| 6 | **ruling 3 carried unchanged** | **§5's `G10` split and §6's caps-asserted-against-§7 are byte-carried from D7F.** The grader still reads **15 values, all agreeing.** Not reopened by this re-registration |

### 13.1 THE REPORTING CAP — WHAT IS RULED AND WHAT IS EXPLICITLY NOT, IN THE SUPERVISOR'S OWN TERMS

**RULED, `[lab-attributed]`, by the dafoam-supervisor, for this family, effective now:** a dafoam
pre-registration **may register a cap as a runaway guard that REPORTS to the supervisor and does not
itself stop a sound run**, provided the crossing is (i) reported to the supervisor, (ii) **named
separately in the cost row and never absorbed into any ratio**, and (iii) accompanied by **a hard
ceiling that does stop the run.** §7 registers all three.

**NOT RULED, BY THE SUPERVISOR OR BY ANY AGENT AT ANY LEVEL: whether `CLAUDE.md` rule 12's *"an
overrun stops the run"* is retired, widened or amended. That is constitutional text and it is
Sanaa's.** The chief's reading of her cost-lift converts caps into runaway guards, **but that lift
named three teams and dafoam's inclusion is the chief's own explicitly-correctable inference — so no
charter reading rests on it** (`CLAUDE.md` rule 9: no agent message is her consent).

> **THE BOUNDARY, STATED SO A SUCCESSOR CANNOT READ AN OPERATIONAL RULING AS A CHARTER AMENDMENT:
> the supervisor ruled on HOW DAFOAM REGISTERS AND TREATS ITS OWN CAPS. Nobody ruled on rule 12.**
> The family's practice is `[lab-attributed]` and effective now; the constitutional question stays
> on Sanaa's desk with the supervisor's recommendation already lodged — ratify the reporting cap
> where a hard kill would destroy a registered ladder, and require the crossing to be reported and
> named.

---

## 14. THE GRADING PATH, FROZEN IN THIS COMMIT

**`CLAUDE.md` rule 2: the grading path is fixed at the pre-registration commit.** Every instrument is
committed here, with this document, **before any container for this item exists.**

| instrument | md5 at freeze | what it is |
|---|---|---|
| `d7fr_grade.py` | `cda7c0492663a3926f2a023476ce9b83` | **arm-kind-aware `G1`** (§5), the `G10` split, caps asserted against §7. Selftest **87 units, 87 passed, `UNEXERCISED=0`**, identical under `-O`, `ast.Assert` **0** |
| `d7fr_run_arm.sh` | `43bc15a84455ef23be377676d48431bf` | `G-ROOT.1`–`.4` from birth, the **three-state completion marker**, all six instrument md5s and the two endpoint md5s asserted before every launch |
| `d7fr_endpoint_locus.py` | `ef2941bd8c4ba71ecb000de02799bba0` | `CONTROL P` / `CONTROL B`, carried from D4's landed instrument. Selftest **22/22**, identical under `-O` |
| `d7fr_endpoint_physical.py` | `26b8265f30bcdd1a7612cd4a5d030e7f` | the `D7-DEF-4` repair wrapper. **Edits zero frozen bytes** |
| `d7fr_accept_primal.py` | `2bfc49e764e999054386e858ec4a0cd8` | `LIMIT 1`'s primal at the corrected point |
| `d7fr_accept_compare.py` | `ef416652abd8e9b64f5a0886915789bf` | `ACC-1`, planted-zero control, target cross-check, **and the verdict-vocabulary guard as a REFUSAL and not a bare `assert`** (`D7F-ACC-DEF-1`) |

**INHERITED AND ASSERTED, NEVER COPIED:** `d7_opt_runScript.py`
`e43902ed2cfc99022c6e21e075f88695`; `d7_extract_endpoint.py`
`651d40c78cc52288a856934c108d1334` (**carries `D7-DEF-4`, corrected DOWNSTREAM, never edited**);
`d7_fd_endpoint.py` `92b3fa8d20a41da029590ed3bdde4203`.

**GATE `H4`'s endpoint identifiers**, from D7R arm `O`: `OptView.hst`
`ed90aa4f0a38b2fadf93cdc0b601ec41`; `opt_IPOPT.txt` `175969fb3e4fa609af708f4f49aa4a6a`.

### 14.1 `D7F-DEF-1` DRIVEN IN BOTH DIRECTIONS, BEFORE COMPUTE

**Requirement 3. Every unit below first asserts THAT THE MUTATION APPLIED, so none can pass
vacuously; and the last row is the one that matters, because it is a REAL arm and not a fixture I
wrote.**

| condition driven | required | measured |
|---|---|---|
| a **healthy `PYTHON` arm**, `rc = 0`, whose log has **no `End` line at all** | **PASS** | **PASSES** — the exact condition that failed the predecessor |
| the same arm with **its own artifact removed** | **FAIL** | **FAILS** — it was not passing by exemption; every kind must present something |
| the artifact restored | **PASS** | **PASSES** — the clause is not a one-way switch |
| a **crashed arm**, `rc = 1`, **with an `End` line present** and a `.fail` marker | **REFUSED by the marker** | marker state **`FAILED`**, `G1` **does not pass** — the false-clean limb closed |
| **neither marker** present | **`UNKNOWN`, read as neither** | marker state **`UNKNOWN`**, `G1` does not pass |
| a launcher that is **absent**, and one that is **unparseable** | **REFUSAL** both | **REFUSES** both (L-302) |
| **THE REAL D7F ARM `P1`** — `rc = 0`, kind `DECOMPOSE`, **zero `End` lines in its log** | **PASS** | **`marker OK`, `d7_decomp_A.json` and `d7_decomp_B.json` both present, `G1 pass = True`.** The predecessor's clause on the same bytes: **`End` found = False → it fails a healthy arm** |

**All of it identical under `python3 -O`**, and `ast.Assert` nodes across all five instruments: **0**.

**FROZEN. Nothing fires before this document and every instrument above are committed.**

---

## AMENDMENT 1 — 2026-08-26T04:37:32Z. **PRE-COMPUTE.** GATE `H5`: THE MEMORY GATE SAMPLES A WINDOW, NOT A READING.

**`CLAUDE.md` rule 2: before first compute, amendments are legal AND MUST STATE THE CONDITION AND HOW
IT WAS CHECKED.** This one ADDS a gate. It moves no existing gate, threshold, cap or label, and §7's
cap table is byte-unchanged — `assert_caps_against_document()` still reads **15 values, all
agreeing**.

### A1.1 The condition, checked by name

| check | reading |
|---|---|
| `ls -d /home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd` — **the run directory that does not exist** | **0** |
| `sudo -n docker ps -a --filter name=d7fr_` | **0** containers, none ever created |
| arm directories `P1 X ACC F-S F-P` | **0 of 5** |

### A1.2 Why — and it is a wrong-instrument finding, not a weak-threshold one

**MEASURED on this box, `MEMORY_CENSUS.md` and `HOLD_RECORD.md`:** `MemAvailable` does not sit low,
it **OSCILLATES** — median **17.35 GiB**, minimum **1.96 GiB**, below the lab's **absolute 12 GiB**
floor in **19 of 45 samples**.

The frozen launcher gates on **one reading taken immediately before launch**. At that duty cycle it
reads the comfortable mode about **three times in five** and **passes** — and the run then meets an
excursion it has no rule to survive, because D7R §8 registered the in-run sampler **record-only with
no mid-run stop**, deliberately.

> **A SINGLE-SAMPLE GATE ON A TIME-VARYING QUANTITY IS NOT A WEAK GATE. IT IS THE WRONG INSTRUMENT
> FOR THE QUANTITY.** This is heat-transfer's Class A → Class C shape, and that team already built
> the answer (`analyse_e4a2.py:300`, `analyse_k0cx.py:644`): a sustained window, a trend rejection, a
> stationarity check, and a refusal below a minimum sample count. It is the same shape as cfd's T8
> lesson — **one residual reading is not evidence of convergence, because a converging trend is a
> property of a HISTORY and not of a sample. Memory headroom is a history too.**

### A1.3 The gate, with its window and sample minimum NAMED

**`H5` — `d7fr_mem_gate.py`, invoked by the launcher after the frozen-instrument md5 assertions and
before any container is created.**

| parameter | registered value |
|---|---|
| **minimum sample count** | **45** |
| **minimum window span** | **30.0 s** (the launcher samples **45 × 1.4 s ≈ 63 s**) |
| **floor** | **the arm's own REGISTERED floor** — 6.0 GiB for `P1`, 16.0 GiB for `X`/`ACC`/`F-S`/`F-P`. **The gate holds no threshold of its own** |

| refusal | fires when |
|---|---|
| **`R1_COUNT`** | fewer than 45 readings — a window that is not a window cannot show an excursion (L-302) |
| **`R2_SPAN`** | window shorter than 30 s — *N* samples taken instantaneously are one sample with extra steps |
| **`R3_EXCURSION`** | **ANY** sample below the floor. **Never the median, never the mean, never the last reading** |
| **`R4_TREND`** | a downward slope projecting below the floor inside the arm's registered wall budget, **even if no sample has crossed yet** |

**`H5` CAN ONLY REFUSE.** It cannot turn a refusal into a launch.

### A1.4 DEMONSTRATED ON THE DATA THAT MOTIVATED IT

**A gate that has never seen the data that motivated it is a gate nobody has tested.** The 45-sample
series is committed beside this document as `d7fr_mem_series_windowA.txt`; the clean census series as
`d7fr_mem_series_windowC.txt`.

| replay | required | measured |
|---|---|---|
| **window A**, floor 16.0 | **REFUSE** | **`R3_EXCURSION`, exit 2** — `n_below_floor: 19`, `min: 1.96`, **`median: 17.35`** |
| **window A**, floor 6.0 (`P1`) | **REFUSE** | **`R3_EXCURSION`, exit 2** — first excursion at index 6 |
| **window C**, floor 16.0 | **CLEAR** | **exit 0** — `min 17.31`, `n_below_floor: 0`, slope −0.016 GiB/min |

> **THE UNIT THAT MATTERS IS THE ONE ABOUT THE STATISTIC.** Window A's **median is 17.35 GiB and
> would PASS a median gate.** Its minimum is **1.96**. The selftest asserts both facts side by side,
> so the record carries the reason the median is not the statistic rather than asserting it.

**Selftest: 10 units, 10 passed**, each mutant first asserting *that the mutation applied*.
**Identical under `python3 -O`; `ast.Assert` nodes: 0.**

### A1.5 A PLACEMENT DEFECT IN MY OWN WIRING, CAUGHT BEFORE THE COMMIT

**I first wired `H5` thirty-five lines too high — above the frozen-instrument md5 assertions — where
it would have EXECUTED `d7fr_mem_gate.py` BEFORE that file's identity was checked.**

> That is the `G-ROOT` lesson **in its dual form**: not a guard that runs after the act it guards,
> but **an instrument used before its identity is asserted.** Same error, mirrored. Caught by an
> ordering audit of my own wiring. **Ordering now: `TMO` 218 → `FLOOR` 231 → single-sample check 241
> → md5 assertions …255 → `H5` 274–286 → container creation.**

**The single-sample check is RETAINED and not replaced.** It is cheap, it fails fast, and `H5` sits
after it: two instruments asking the same question at different time scales.

### A1.6 The struck row

**§14's `d7fr_run_arm.sh` row is STRUCK, not rewritten.** At the freeze its md5 was
`43bc15a84455ef23be377676d48431bf`; **at this amendment it is `91a561eaf41110be8b914dab7e63086c`**.
**`d7fr_mem_gate.py` is ADDED to the frozen grading path at `d78caea6af6bf997d734959b6954c517`**, and the launcher
asserts it before every launch. Every other §14 row is unchanged.

**STILL FROZEN. STILL NOTHING FIRED.**

---

## ADDENDUM 2 — 2026-08-26T16:31:03Z. **POST-COMPUTE.** `d7fr_grade.py` SEPARATES PHYSICS-CRITICAL FROM INFRASTRUCTURE FIELDS (Sanaa's universal rule, `d4d0c29d`, L-342)

**Version 1.2. This addendum ALTERS NO GATE, THRESHOLD, CAP OR LABEL** (rule 2: after first compute, changes land only as dated addenda that cannot). **Lines whose number changed above this section: 0** — it is appended, and every §14 citation above it is untouched. Approved as a pre-registered amendment by dafoam-supervisor, ruling [lab-attributed] 2026-08-26, on conditions C1–C3, each DRIVEN in the selftest under plain `python3` and `-O`.

### A2.1 The rule, and the condition under which this addendum is legal

Sanaa, verbatim (`d4d0c29d`): *"a bookkeeping failure invalidates the bookkeeping, never the physics artifacts — and graders must separate physics-critical fields from infrastructure fields so a dead poller can never void a run again."* Addendum consequence 4 of that boarding: *"this rule licenses no change to bands, thresholds or verdict logic."* This addendum stays inside that licence: `_map_verdict_core` is the frozen `map_verdict` body byte-for-byte; every band, threshold and cap constant is unchanged; `assert_caps_against_document()` still reads 15 values, all agreeing.

**Condition at this addendum:** arms `P1`, `X`, `ACC`, `F-S` complete (`ledger.txt`, rc = 0 each); `F-P` RUNNING under the launcher's md5 assertion of the **run-root** copy (`d7fr_run_arm.sh:254`, `cda7c0492663a3926f2a023476ce9b83`). **Nothing has been graded under either version of the grader** — `F-S` is HELD ungraded until this addendum lands (supervisor's order). The run-root copy is NOT touched; it exists for the launcher's assertion, and the grading path is the repository copy fixed below.

### A2.2 Field classes, declared in the file (`PHYSICS_FIELDS`, `INFRA_FIELDS`)

| class | fields | absent → |
|---|---|---|
| **PHYSICS** — gates read these | `rc`, `inspect(exit,oomkilled)` — the kernel's record | **REFUSE** (unchanged) |
| **INFRASTRUCTURE** — disclosed | `wall_s`, `core_min`, `cap_core_min`, `enforced_core_min`, `enforced_wall_s`, `memavail_*`, `delivered_cores_mean`, `siblings_*` | **`NOT_MEASURED`**, named in the verdict line, grade proceeds |

### A2.3 The three conditions, and where each is met

| | condition | implementation | driven by |
|---|---|---|---|
| **C1** | ABSENT (key missing / None) → `NOT_MEASURED`; PRESENT-BUT-UNPARSEABLE → REFUSE naming key and value | `_infra()`; `_f()` unchanged for physics | `G1_L342_absent_infra_field_is_NOT_MEASURED_and_proceeds`, `G1_L342_present_GARBAGE_infra_field_REFUSES_naming_key_and_value`, `G10_L342_present_GARBAGE_cap_field_REFUSES`, `G1_L342_absent_PHYSICS_rc_still_REFUSES` |
| **C2** | a missing ledger ROW is bookkeeping: rc from the launcher's own marker (`.ok/.fail`, itself `docker inspect`, launcher :564/:632-636) or from the surviving container; `wall_s` from `StartedAt/FinishedAt`, `core_min = wall_s × 4 / 60`, `_source` per field; `NOT_MEASURED` only when neither has it; arm absent only when neither exists | `_rc_from_marker_or_container()`; G1 fallback branch; G11 container fallback | `G1_L342_row_ABSENT_marker_present_grades_rc_from_marker`, `G1_L342_container_survives_wall_s_from_inspect_core_min_derived`, `G1_L342_NEITHER_marker_nor_container_is_None`, `G11_L342_row_lacking_OOM_bit_reads_the_CONTAINER`, `G11_L342_row_lacking_OOM_bit_and_no_container_stays_HARD` |
| **C3** | `NOT_MEASURED` never composes to PASS silently: every such limb is NAMED in the verdict's `because` as a stated limitation; G11 stays hard; G10 limb 1 `NOT_MEASURED` is disclosed, not passed | `map_verdict()` wrapper around the byte-unchanged `_map_verdict_core()`; G10 `status: NOT_MEASURED`, `pass` False, listed | `MAP_L342_NOT_MEASURED_limbs_are_NAMED_in_the_verdict_line` (asserts the wrapper returns exactly the core's verdict token), `MAP_L342_clean_gates_carry_an_EMPTY_limitation_list`, `G10_L342_absent_cap_fields_NOT_MEASURED_disclosed_not_passed`, `G1_L342_row_lacking_wall_s_PROCEEDS_and_DISCLOSES`, `G1_L342_rc_1_still_FAILS` |

One consequential line outside the §2 hunks, disclosed: G10's item total now EXCLUDES a `NOT_MEASURED` actual and names the exclusion (`total_excludes_NOT_MEASURED_arms`) instead of crashing on `float("NOT_MEASURED")` — found by the selftest, not by inspection.

### A2.4 Measured at this addendum

Diff against the frozen blob `35f62221aa17` (`git diff --no-index`): **333 insertions, 15 deletions**, hunks only in `_f` (insertion after it), `g1_completion`, `g10_caps`, `g11_oom`, `map_verdict`, `grade` (one line: `base=base` into G11), `selftest`. Selftest: **102 units, 102 passed, `UNEXERCISED=0`**, identical under `python3 -O`; `ast.Assert` nodes **0**.

### A2.5 The struck row

**§14's `d7fr_grade.py` row is STRUCK, not rewritten.** At the freeze its md5 was `cda7c0492663a3926f2a023476ce9b83`; **at this addendum the repository copy is md5 `c451af9f2d2c496a1dd9f3231213884b`, blob `4df305e460e218bbb30485874bba3b741d1b0c68`**, and that is the grading path for `F-S` and `F-P`. The run-root copy remains at the frozen md5 for the launcher's :254 assertion and is NOT the grading instrument. Every other §14 row is unchanged.

---

## ADDENDUM 3 — 2026-08-26T16:40:09Z. **POST-COMPUTE.** THE AGE GUARD STOPS TESTING A STAGED INPUT AS AN OUTPUT, AND `G13` READS THE ADJOINT THIS ITEM ACTUALLY RUNS

**Version 1.3. ALTERS NO BAND, THRESHOLD, CAP OR LABEL. Lines whose number changed above this section: 0.** Approved narrowly by dafoam-supervisor, ruling [lab-attributed] 2026-08-26, under Sanaa's rule `d4d0c29d`/L-342 **and** `VERIFICATION_CHARTER.md` §2d.1, whose four conditions are met **non-vacuously** here: (1) demonstrable on disk — `d7fr_grade_FS_interim.json` shows G1 failing on exactly one artefact, `X/OptView.hst`, `mtime 1787711453 < datum 1787719601`, and G13 `arm_absent_from_ledger` for an arm `O` this item never registered; (2) the independent instrument is **the launcher's own H4 record** for the arm — `D7FR_H4_PASS arm=X endpoint=D7R/O OptView.hst=ed90aa4f… opt_IPOPT.txt=175969fb…` in `X_attempt.log` (and the same line, same md5s, in `ACC_`/`F-S_`/`F-P_chain_launcher.out`); (3) what moves is the item verdict only — every gate number is unchanged; (4) **the pre-repair verdict is recorded beside the post-repair one**: pre-repair `NOT A RESULT` (`because = [G1 completion/age guard, G13 adjoint health (band F)]`, `d7fr_grade_FS_interim.json`, graded under Addendum 2's blob `4df305e4…`), post-repair verdict in `RESULTS_FS.md`/`RESULTS_FP.md` under this addendum's blob.

### A3.1 A correction to the ruling's premise, stated before it is relied on

The ruling said the staged files are *"recorded in H4's own ledger line."* **H4 writes no ledger line.** `ledger.txt` carries no `H4` token; the record is the `D7FR_H4_PASS …` line the launcher prints to its own stdout (`d7fr_run_arm.sh:361`), captured per arm in `<ARM>_attempt.log` or `<ARM>_chain_launcher.out`. The grader therefore reads the exemption list from **that** file, for **that** arm only (`_h4_staged_inputs`), and it is still a frozen record written by the frozen launcher before compute — the ruling's bound holds, at a different path.

### A3.2 (a) G1 — the exemption, bounded to named files and verified by md5

The age guard's artefact list is unchanged (`opt_IPOPT.txt`, `OptView.hst`, `d7_major_history.json`, `d7_endpoint_dvs.json`). For each, if the arm's own H4 line names it **with an md5**, the grader computes the file's md5: **match → `STAGED_INPUT_EXEMPT`**, recorded with the H4 source path and listed in the verdict line as a limitation; **mismatch → REFUSE** (`staged_input_md5_mismatch`). Unnamed files, and every produced artefact, are age-checked exactly as before; `_n_artifacts_checked` counts only age-checked artefacts and the L-302 zero-trip refusal stands. An H4 line for another arm exempts nothing.

**THIS IS A RELAXATION ADOPTED POST-COMPUTE**, and it is said plainly: last night the supervisor refused to relax D7F's `G1` after compute (the D7F-DEF-1 re-registration instead). What differs now: **Sanaa's universal rule intervened** (`d4d0c29d`, 16:15Z today) and classes a provenance check tripping on a deliberately staged input as a bookkeeping failure; **§2d.1's conditions 3 and 4 are non-vacuous** here (numbers unchanged; both verdicts recorded); and **the scope is bounded by a frozen record** — two files, by name and md5, written before compute by the frozen launcher. The relaxation cannot reach a produced artefact, cannot be widened by editing a launcher output (a moved md5 refuses), and cannot turn a `GATE FAIL` into a `PASS`.

### A3.3 (b) G13 — where this item's adjoint gradient actually comes from

**In-item.** Each FD arm's `compute_totals` runs one adjoint and prints one `PetscConvergedReason` (measured: `F-S_20260826T160553Z_80216.log` — 1 line, non-negative; `ACC`/`X` — 0, they run no adjoint). `g13_in_item` reads band F from the FD arms present in the graded set (`F-S`, `F-P`), passes only if every present arm passes, and returns `NOT_MEASURED` (pass False, hard) when no FD arm is graded. Nothing is staged from D7R for this gate, so the ruling's second branch (cite D7R's measured G13) does not arise. `_map_verdict_core` is byte-unchanged; `G13` remains in its hard list.

### A3.4 Driven, plain `python3` and `-O`

`G1_A3_old_staged_file_UNNAMED_by_H4_fails_age_guard`; `G1_A3_staged_files_NAMED_by_H4_with_matching_md5_are_EXEMPT` (`_n_artifacts_checked` 2); `G1_A3_exemption_does_not_reach_PRODUCED_artefacts`; `G1_A3_named_staged_file_with_MOVED_md5_REFUSES`; `G1_A3_H4_line_for_ANOTHER_arm_exempts_nothing`; `G13_A3_in_item_reads_the_FD_arm_and_passes`; `G13_A3_no_FD_arm_is_NOT_MEASURED_not_health`; `G13_A3_a_MINUS9_in_an_FD_arm_fails_band_F`. **110 units, 110 passed, `UNEXERCISED=0`**, identical under `-O`; `ast.Assert` 0. Diff against Addendum 2's blob: 157 insertions, 1 deletion; hunks only in the new H4 helper, `g1_completion` (age loop), the new `g13_in_item`, `map_verdict` (limitation naming), one line in `grade()`, `selftest`.

### A3.5 The struck row

**Addendum 2's grader row is STRUCK, not rewritten:** `c451af9f2d2c496a1dd9f3231213884b` / blob `4df305e460e218bbb30485874bba3b741d1b0c68` → **md5 `b96f550daf1ac193364ac5ea1b42d279`, blob `265b9680233ae89efb537f092329c1520d2df23d`**, the grading path for the item verdict. The run-root copy stays at the frozen md5 for the launcher's `:254` assertion. Every other §14 row is unchanged.

---

## ADDENDUM 4 — 2026-08-26T16:45:27Z. **POST-COMPUTE.** `D7FR-GRADER-DEF-1` (COMPOSITION): THE ITEM VERDICT IS COMPOSED FROM THE GATES THIS DOCUMENT REGISTERS, AND `G2`/`G3`/`G4` ARE REPORTED, NOT GATED — AS §4 SAYS

**Version 1.4. ALTERS NO BAND, THRESHOLD, CAP OR LABEL. Lines whose number changed above this section: 0.** Approved by dafoam-supervisor, ruling [lab-attributed] 2026-08-26, who read §4 at `b424b44e` personally.

### A4.1 The defect, recorded as `D7FR-GRADER-DEF-1`

§4 (lines 211–226, frozen at `b424b44e`): *"It produces no drag reduction of its own, so there is nothing for band C to gate. … The 30.402283 % is carried as a RECORDED D7R number, REPORTED AND NOT GATED. No gate in this item reads it, and no verdict of this item may be stated in terms of it. The bright line here is `G5`."* The ported grader's `map_verdict` nevertheless composed the item verdict from `G2`/`G3`/`G4` — D7R arm `O`'s CL bands, IPOPT exit and drag-reduction band — and returned **`NOT A RESULT`** on band C with every registered gate of this item passing (`d7fr_grade_FS_a3.json`). **The document is the registration; the grader is its instrument; where they disagree the document governs.** An instrument gating on quantities the document says no gate reads is the `D7R-GRADER-DEF-6` stale-inheritance class, now in the composition. **Removing it is not a relaxation: it deletes gates the item never registered.**

### A4.2 The composition (`_map_verdict_core`), and what is kept beside it

1. **Hard gates**, unchanged in identity: `G1`, `G8`, `G11`, `G13`, and `G9` when two rows are present → `NOT A RESULT`.
2. **Per-row verdict** for **SHIPPED** (`F-S`) and **PATCHED** (`F-P`): `G6`/`G6b`/`G7` for that row fail → `NOT A RESULT`; `G5` holds (bands D and E, 5.0 % per component and aggregate, sign flips) → `PASS`; `G5` missed → `GATE FAIL`; FD artefact absent → `PENDING`.
3. **The item verdict is stated only when BOTH rows are graded** (else `PENDING`, per-row verdicts shown). It is the worse of the two rows under the one-way rule; **a shipped-vs-patched divergence is named as the FINDING this item registers (§8's two-row rule), reported, never a failure by itself.**
4. **`G2`/`G3`/`G4` are REPORTED, NOT GATED**, carried under `reported_not_gated` with §4 quoted verbatim.
5. **The pre-Addendum-4 composition is KEPT** as `_map_verdict_core_D7PORT` and written into every verdict as `pre_addendum4_composition_D7PORT`, so the two compositions sit side by side in the record (§2d.1 condition 4). Pre-repair files: `d7fr_grade_FS_interim.json`, `d7fr_grade_FS_a3.json`.

### A4.3 Driven, plain `python3` and `-O`

`MAP_A4_both_rows_PASS_composes_PASS_with_G2G3G4_REPORTED_NOT_GATED` (pre-composition reads `GATE REACHED` on the same fixture); `MAP_A4_G2_G4_OUT_OF_BAND_leaves_verdict_UNCHANGED_and_REPORTS_the_number` (30.4 % reported, verdict unchanged; pre-composition `NOT A RESULT`); `MAP_A4_G5_FAIL_on_one_row_fails_the_item_and_NAMES_the_divergence`; `MAP_A4_G9_FAIL_is_NOT_A_RESULT`; `MAP_A4_one_row_ABSENT_is_per_row_only_and_item_PENDING`; `MAP_A4_planted_zero_FAIL_on_a_row_is_NOT_A_RESULT_for_that_row_and_the_item`; `MAP_A4_every_composed_token_is_in_the_fixed_vocabulary`. `CAPSTOP_never_PASS` and `CONVERGED_is_PASS_and_flagged_a_SURPRISE` now drive the RECORDED pre-composition explicitly. **117 units, 117 passed, `UNEXERCISED=0`**, identical under `-O`; `ast.Assert` 0. Diff against Addendum 3's blob: 162 insertions, 3 deletions; hunks only in `map_verdict`/`_map_verdict_core` and `selftest`.

### A4.4 The struck row

**Addendum 3's grader row is STRUCK, not rewritten:** `b96f550daf1ac193364ac5ea1b42d279` / blob `265b9680233ae89efb537f092329c1520d2df23d` → **md5 `4303704523de7e1c8fa6d6a34a858ded`, blob `1b810913de3a0d0d381988a26789ebf577b5c978`**, the grading path for the item verdict. The run-root copy stays at the frozen md5 (the launcher's `:254` assertion; every arm has now run under it). Every other §14 row is unchanged.
