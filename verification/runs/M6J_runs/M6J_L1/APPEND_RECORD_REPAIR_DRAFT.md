# DRAFT REPAIR — `scripts/append_record.py` exit-7 block on `docs/COST_CALIBRATION.md`

**STATUS: `PENDING` — DRAFTED, MEASURED, DRIVEN, AND DELIBERATELY NOT APPLIED.**
`scripts/append_record.py` is a shared gating instrument for four lab-wide registers and all six
teams. `SUPERVISION_CHARTER.md` §3 makes a measurement-script diff the supervisor's **personal,
non-delegable** check. This lane produced the diff and drove it; **it did not apply it**, and the
instrument on disk is byte-unchanged (`git status` shows no modification to `scripts/`).

**Drafted by:** `lab-lane` under `cfd-supervisor`, 2026-09-13.
**The defect is cfd's own** — established from git below, not taken on report.

---

## 1. RUN — what was done

| # | Action | Result |
|---|---|---|
| 1 | `python3 scripts/append_record.py --selftest` **BEFORE** | `VERDICT: PASS (0 control failure(s))`, rc 0 |
| 2 | Reproduced the blocker on the real row, `--dry-run` | **rc 7**, naming `HEAD:docs/COST_CALIBRATION.md:592` |
| 3 | Established provenance from git | `git blame -L 592,592` → `95408812c`; `git show 95408812c -- docs/COST_CALIBRATION.md` → the id is in the **added** lines |
| 4 | Swept **all four** `RECORDS` with `shape_audit` on HEAD's blobs | 5 offenders across 3 records — see §5 |
| 5 | Built **two** candidate widenings in the scratchpad, never in `scripts/` | both pass `--selftest`; they differ on every future id |
| 6 | Drove 7 specimens end-to-end through `main() --dry-run` on the real record, under BASE / LITERAL / CLASS | §3 |
| 7 | `--selftest` **AFTER** (on the patched copy) | `VERDICT: PASS (0 control failure(s))`, rc 0 |
| 8 | Ran the three *other* instruments that import this module, BASE vs patched | §6 |

Nothing was written to `docs/COST_CALIBRATION.md`, to `docs/LESSONS.md`, to
`docs/NUMERICS_KNOWLEDGE.md` or to `scripts/` by this lane. Every append was `--dry-run`.

---

## 2. PROBLEM

`docs/COST_CALIBRATION.md:592` carries `C-2026-09-13T202608.816749Z-9830ff70` — a **dashed**
date, `%Y-%m-%d` — where all other timestamp ids on this record carry `%Y%m%d`, the form
`--allocate-id` mints. The legacy id pattern

```
^\|\s*(?:\*\*|~~)*\s*(C-\d+)\s*(?:~~|\*\*)*\s*\|
```

matches `C-2026` and then fails on the following `-`, so it parses **no** id, while the candidate
shape `^\|[ \t]*(?:\*\*|~~)*[ \t]*C-\d` still matches. That is the D549 clause-1b refusal
condition, exit 7, on **every** append to this record by **every** team.

**Provenance, established from git and not from report.** `git blame -L 592,592 HEAD` returns
`95408812c06af67c22d366d03846c80ab1c72c1e`, *"cfd WOLF DYNAMICS DrivAer COARSE IS GRADED…"*,
2026-09-13 20:27:01Z. `git show 95408812c -- docs/COST_CALIBRATION.md` shows exactly 2 added
lines, one of which opens `+| C-2026-09-13T202608.816749Z-9830ff70`. **The id was hand-typed into
the tool's own shape by the cfd team instead of being minted by `--allocate-id`.** That is the
mechanism the module's smuggle guard exists to prevent — and it could not: `ANY_TOOL_ID` is built
from `TOOL_ID_BODY`, which is **undashed**, so the smuggle guard is structurally unable to see a
dashed hand-typed id. Clause 1b caught it, one commit later, by refusing everyone.

**Blast radius, measured:** at least three drafted cost rows are waiting on this one line —
`verification/runs/M6J_runs/M6J_L1/COST_CALIBRATION_ROW_PENDING.md` (cfd) and the two in
`cases/dafoam/ladder-a/A2/curriculum_D6R3/D6R3_FIX_COST_CALIBRATION_ROWS_PARKED.md` (dafoam).

---

## 3. SOLUTION — `RECORDS` widening, and a **literal**, chosen over the class form

### 3a. `RECORDS`, not `KNOWN_EXCLUDED` — measured, and the supervisor's reading is confirmed

The tool prescribes two register edits and forbids editing the record. Measured on the real bytes:
line 592 is a full cost row (nine cells, real figures, real artifact citations) carrying a **real,
unique, intended** id — `9830ff70` occurs nowhere else in the file. It is **not** a second block
under an id counted elsewhere, which is the canonical `KNOWN_EXCLUDED` case named in the refusal
text itself. Excluding it would drop a real id from the arithmetic — the loss this module already
writes down for `C-104`. **`RECORDS` widening. The supervisor's reading is not wrong.**

### 3b. A LITERAL, not the dashed-date class — and this is the load-bearing choice

Both widenings unblock the record and **both pass `--selftest`**, so the selftest does not decide
this. They were separated by driving the specimens both refuse-ward and accept-ward:

| specimen (end-to-end, `main() --dry-run`, real record) | BASE | **LITERAL** | CLASS |
|---|---|---|---|
| the real M6J L1 row, `--allocate-id` | **rc 7 blocked** | **rc 0** | rc 0 |
| candidate shape, no identifier at all | rc 7 | **rc 7** | rc 7 |
| **a SECOND, different hand-typed dashed id** | rc 7 | **rc 7** | **rc 3** |
| a dashed id ending in a digit run (`…-00000001`) | rc 7 | **rc 7** | **rc 3** |
| rows hand-writing a well-formed **minted** id | rc 9 | **rc 9** | rc 9 |
| `{{ALLOCATE_ID}}` row citing a minted id in prose | rc 9 | **rc 9** | rc 9 |
| **correction row whose OWN id is hand-typed dashed, with `corrects:[…]`** | rc 9 | **rc 9** | **rc 3** |

Reading the two rows that differ:

* **Row 3.** Under the class form a second hand-typed dashed id **parses as a legacy id**. The
  refusal degrades from exit 7 — *this is not an id at all* — to exit 3, *the id arithmetic
  disagrees*, which is the refusal a caller renegotiates by picking another number. Clause 1b is
  the **only** guard that can see a dashed hand-typed id, and the class form retires it for the
  whole class.
* **Row 7, the sharper one.** Clause C3 of Sanaa's 2026-09-03 plumbing amendment requires a
  correction row to carry *"its own legitimate id — … a legacy id this record's own pattern
  parses"*. Under the class form a **hand-typed** dashed id satisfies C3, and the exit-9
  smuggle/C3 refusal **disappears**. Under the literal it is byte-identical to the pre-repair
  module. **Widening what the reader may SEE must not widen what a writer may MINT.**

The evidence is one line. The admission is one line. `L-570` says a guard that cannot say no is
not a guard; tonight's `L-608` says a guard that refuses lawful work is a defect. The converse of
`L-608` is what decides here: **a guard widened beyond its evidence stops being a guard.**

### 3c. The repair is a **TWO-FILE** diff — discovered by driving, not by reading

`scripts/check_record_reconciliation.py` carries a mutation harness that greps the **literal
source text** of this `RECORDS` entry out of `append_record.py` (`:746-750`). A first draft that
reformatted the entry across several source lines made that harness report **rc 5,
`VERDICT: FAIL` — *"site occurs 0 times in append_record.py, not once — the harness is stale, not
the code"***. Driven, then fixed two ways: the pattern is kept on **one source line**, and the
harness's site **and its mutant** are updated in the same diff. With both, that module returns
`VERDICT: PASS`, rc 0 — and PASS means the mutant still flips.

**This is also the tripwire that protects the narrowness.** Any future edit to that one line — a
lane "tidying" the literal into the class form — makes `check_record_reconciliation.py --selftest`
fail until someone deliberately updates the harness. The narrowness is held by a mechanism, not
only by a comment.

---

## 4. THE DIFF — apply as one commit, per item, private-index protocol

```diff
--- a/scripts/append_record.py
+++ b/scripts/append_record.py
@@ -495,7 +495,69 @@
     # a pipe. The planted negatives in `run_controls` assert this pattern parses
     # NEITHER of them as an id -- a looser pattern would mint ids out of table
     # furniture and the arithmetic would be judged against them.
-    "docs/COST_CALIBRATION.md": r"^\|\s*(?:\*\*|~~)*\s*(C-\d+)\s*(?:~~|\*\*)*\s*\|",
+    # ONE HAND-TYPED ID, ADMITTED BY ITS EXACT BYTES AND BY NOTHING ELSE.
+    # 2026-09-13: `docs/COST_CALIBRATION.md:592` carries
+    # `C-2026-09-13T202608.816749Z-9830ff70` -- a DASHED date, `%Y-%m-%d`,
+    # where `--allocate-id` mints `%Y%m%d`. It was HAND-TYPED into the tool's
+    # own shape by commit `95408812c` (cfd, Wolf Dynamics DrivAer COARSE)
+    # instead of being minted. The pattern matched `C-2026` and then failed on
+    # the following `-`, so the line matched the CANDIDATE SHAPE and yielded no
+    # id: the D549 clause-1b refusal, exit 7, on EVERY append to this record by
+    # EVERY team. Measured on HEAD: exactly 1 such line; 492 ids parse.
+    #
+    # WHY `RECORDS` AND NOT `KNOWN_EXCLUDED`, measured before choosing: :592 is
+    # a full cost row carrying a REAL, UNIQUE, INTENDED id -- not a second
+    # block under an id counted elsewhere, which is what `KNOWN_EXCLUDED` is
+    # for. Excluding it would drop a real id from the arithmetic; that is the
+    # loss this module already writes down for `C-104` and it is not warranted
+    # here.
+    #
+    # WHY A LITERAL AND NOT THE CLASS FORM, and this is the load-bearing half.
+    # The obvious widening is the dashed-date CLASS
+    # `C-\d{4}-\d{2}-\d{2}T\d{6}\.\d{6}Z-[0-9a-f]{8}`. Both unblock the record
+    # and BOTH PASS `--selftest`, so the selftest does not decide this. They
+    # differ on every FUTURE hand-typed id, and the difference was DRIVEN on
+    # this record rather than reasoned about:
+    #   * a SECOND, different hand-typed dashed id in a rows file --
+    #       literal -> exit 7 (still not an id: the guard holds)
+    #       class   -> exit 3 (parsed as a LEGACY id; all that is left is the
+    #                          id ARITHMETIC, a refusal a caller renegotiates,
+    #                          not one that says the form is illegitimate)
+    #   * a correction row whose OWN id is hand-typed dashed, carrying a
+    #     `corrects:[...]` field -- clause C3 of the 2026-09-03 amendment, "the
+    #     line must ALSO carry ... a legacy id this record's own pattern
+    #     parses" --
+    #       literal -> exit 9, byte-identical to the pre-repair module
+    #       class   -> exit 3; C3 is SATISFIED by the hand-typed id and the
+    #                  smuggle/C3 refusal is GONE.
+    # The class widening hands the dashed spelling the one privilege the
+    # undashed spelling is denied: `ANY_TOOL_ID` is built from `TOOL_ID_BODY`
+    # and is UNDASHED, so the smuggle guard is STRUCTURALLY unable to see a
+    # dashed hand-typed id and clause 1b is the only thing that catches one.
+    # WIDENING WHAT THE READER MAY SEE MUST NOT WIDEN WHAT A WRITER MAY MINT.
+    # The evidence is one line; the admission is one line.
+    #
+    # TRAP: this must NOT be "tidied" into the class form, nor into
+    # `C-[\d-]+T...`. There is no measured second instance. L-570 says a guard
+    # that cannot say no is not a guard; the converse is equally true and is
+    # what this comment exists to hold -- a guard widened beyond its evidence
+    # stops being a guard.
+    # TRAP: this alternative must never match the MINTED form `C-20260913T...`.
+    # The `--selftest` limb "tool-id/legacy separation proved on all 4 records"
+    # asserts exactly that, and is what stops a loosening here from letting an
+    # allocated id enter the legacy arithmetic.
+    # TRAP: this entry is a MUTATION SITE in `check_record_reconciliation.py`,
+    # which greps its source text LITERALLY. It is kept on ONE source line for
+    # that reason, and that module's site+mutant were updated in the SAME
+    # commit -- a site that no longer occurs makes the harness report itself
+    # stale (rc 5), which was DRIVEN before this was written.
+    # ORDERING, measured: `C-\d+` is tried first, matches `C-2026`, fails at
+    # the following `-`, and the alternation backtracks into the literal. Both
+    # branches are `(?:...)`, so the pattern keeps EXACTLY ONE capturing group,
+    # which the load-time check below asserts.
+    # IF THIS STOPS MATCHING ANYTHING it is not harmless: :592 was struck or
+    # rewritten, and this alternative is then to be REMOVED, not kept.
+    "docs/COST_CALIBRATION.md": r"^\|\s*(?:\*\*|~~)*\s*((?:C-\d+)|(?:C-2026-09-13T202608\.816749Z-9830ff70))\s*(?:~~|\*\*)*\s*\|",
 }
 
 #: CANDIDATE SHAPES -- one per record, keyed identically to `RECORDS`.
--- a/scripts/check_record_reconciliation.py
+++ b/scripts/check_record_reconciliation.py
@@ -746,8 +746,8 @@
     ("COST_CALIBRATION: the id's hyphen tidied away -- the trap named in the "
      "pattern's own comment; it then parses nothing at all",
      "append_record.py",
-     '    "docs/COST_CALIBRATION.md": r"^\\|\\s*(?:\\*\\*|~~)*\\s*(C-\\d+)\\s*(?:~~|\\*\\*)*\\s*\\|",',
-     '    "docs/COST_CALIBRATION.md": r"^\\|\\s*(?:\\*\\*|~~)*\\s*(C\\d+)\\s*(?:~~|\\*\\*)*\\s*\\|",'),
+     '    "docs/COST_CALIBRATION.md": r"^\\|\\s*(?:\\*\\*|~~)*\\s*((?:C-\\d+)|(?:C-2026-09-13T202608\\.816749Z-9830ff70))\\s*(?:~~|\\*\\*)*\\s*\\|",',
+     '    "docs/COST_CALIBRATION.md": r"^\\|\\s*(?:\\*\\*|~~)*\\s*((?:C\\d+)|(?:C-2026-09-13T202608\\.816749Z-9830ff70))\\s*(?:~~|\\*\\*)*\\s*\\|",'),
     # ---- the TOOL-ALLOCATED half (Sanaa 2026-08-31) ----------------------
     # THE MUTANT THAT MATTERS MOST: the reconciler reading the LEGACY pattern
     # alone, which is exactly what this module did before this build. It is
```

**Verification the supervisor should re-run after applying, in this order:**

```
python3 scripts/append_record.py --selftest                              # expect VERDICT: PASS, rc 0
python3 scripts/check_record_reconciliation.py --selftest                # expect VERDICT: PASS, rc 0
python3 scripts/append_record.py --path docs/COST_CALIBRATION.md \
        --rows verification/runs/M6J_runs/M6J_L1/COST_CALIBRATION_ROW_PENDING.md \
        --allocate-id --dry-run                                          # expect rc 0
```

---

## 5. ALSO REPORTED — is this one malformed id, or the first of a class?

**It is one malformed id of ITS class, and the tool is blocked on two OTHER records for a
DIFFERENT reason.** `shape_audit` swept across all four `RECORDS` on HEAD's blobs, and each
result was then **driven** with a probe append (`--dry-run`) rather than inferred:

| record | candidate lines | ids parsed | **offenders** | probe append | class of defect |
|---|---:|---:|---:|---|---|
| `docs/COST_CALIBRATION.md` | 503 | 491 | **1** | **rc 7 BLOCKED** | a real id in a form the pattern cannot see → **`RECORDS`** |
| `docs/DOCKET.md` | 668 | 686 | **0** | rc 3 (my probe's own id arithmetic — the audit passed) | none |
| `docs/LESSONS.md` | 615 | 607 | **3** | **rc 7 BLOCKED** | deliberately-not-ids → **`KNOWN_EXCLUDED`** |
| `docs/NUMERICS_KNOWLEDGE.md` | 161 | 147 | **1** | **rc 7 BLOCKED** | deliberately-not-ids → **`KNOWN_EXCLUDED`** |

**THREE OF THE FOUR LAB-WIDE REGISTERS ARE CLOSED TO EVERY TEAM RIGHT NOW, not one.** The diff in
§4 reopens `docs/COST_CALIBRATION.md` and **nothing else** — it is deliberately not expanded to
cover records this lane does not own.

The four other offenders, with their parents checked on disk:

* `docs/LESSONS.md:27929` `## L-570 (second block) — …` — parent `## L-570 —` at `:27808`. **A
  FOURTH SPELLING** of "second block": `KNOWN_EXCLUDED` holds the comma form (`L-43,`, `L-61,`)
  and the `AMENDMENT` form (`L-426`), and this one uses **`(second block)` in parentheses**.
* `docs/LESSONS.md:28255` `## L-573 (second block) — …` — parent `## L-573 —` at `:28019`. Same
  spelling; two instances, so it is a convention now, not a slip.
* `docs/LESSONS.md:28306` `## L-<n> block count      : 576` — **not an id at all**: a line inside
  a fenced code block, quoting rule 11's own derivation, that happens to open `## L-`. `shape_audit`
  is line-based and cannot see the fence. This one is a `CANDIDATE_SHAPES`/`KNOWN_EXCLUDED`
  judgement of a different kind and deserves saying out loud.
* `docs/NUMERICS_KNOWLEDGE.md:6723` `**N-D44 EVIDENCE ADDENDUM — 2026-09-10 …` — parent
  `**N-D44.** …` at `:6695`. A second block in a **fifth** spelling.

**Referral, not action.** `docs/LESSONS.md` and `docs/NUMERICS_KNOWLEDGE.md` are lab-wide
registers and this module's declared owner is `verification-supervisor` (the module's own
`CANNOT SEE` line names the owner and the re-read trigger: *"any change to a guarded record's
heading/row grammar"* — which is exactly what has happened four times). Three of the four
offenders are `KNOWN_EXCLUDED` cases; the fourth is a fenced-code false positive. **This lane
neither drafted nor applied those; they are named here so the supervisor can refer them.**

---

## 6. ALSO REPORTED — the other three instruments that import this module

Run BASE vs patched, same repo, same bytes:

| instrument | BASE | patched | reading |
|---|---|---|---|
| `scripts/check_record_reconciliation.py --selftest` | rc 0 PASS | **rc 0 PASS** | repaired by the §4 companion edit; a first draft made it rc 5 (see §3c) |
| `scripts/check_docket_reconciliation.py` | imports `RECORDS`; unaffected (it has no `--selftest` flag — that was this lane's error, not a red) | same | no change |
| `scripts/mutation_harness_append_record_corrects.py` | **rc 1, `VERDICT: FAIL (3 arm(s) failed of 42)`** | **rc 1, same 3 arms** | **PRE-EXISTING RED, NOT CAUSED BY THIS DIFF** |
| `scripts/check_record_reconciliation.py --path docs/COST_CALIBRATION.md` | **rc 4, `VERDICT: FAIL`, `DUPLICATE IDS … C-217`** | **rc 4, identical** | **PRE-EXISTING RED, NOT CAUSED BY THIS DIFF** |

The two reds are reported, not waved through. Their outputs under BASE and patched are **identical
except for the harness's own `subject:` path/sha line** (`diff` of the normalised outputs: 4 lines,
all of them that one line), so the diff in §4 changes neither of them in either direction. The
failing arms are `P1d`, `P1e`, `P2` of the `corrects:` harness, and the duplicate is `C-217` — the
very id the smuggle guard's own refusal text cites as the mechanism it exists to prevent. **Neither
appears in `docs/NOT_PASSING_REGISTER.md`** (grepped: no hits for `append_record`,
`record_reconciliation` or `docket_reconciliation`). That is a second referral for the supervisor,
independent of this repair.

---

## 7. ALSO REPORTED — should `:592`'s hand-typed id ALSO be corrected?

**This lane's position: NO to editing the row; YES to a correction row; and the correction row is
NOT urgent and must not be bundled into this repair.**

* **The row is never edited.** The module forbids it in its own refusal text (*"never an edit to
  the record"*), and `docs/COST_CALIBRATION.md`'s append rule 1 says a correction is *a new row
  naming the row it corrects*. Retyping `:592` would mutate a landed row in an append-only ledger
  and would silently invalidate the literal in §4 — which is why that literal's comment says that
  if it ever stops matching, it is to be **removed**, not kept.
* **A correction row is the right instrument, and it has a real job**: the id `9830ff70` is a
  citable key, and the next reader grepping `C-20260913T2026` will not find the row. A correction
  row can carry the hand-typed id in a `corrects:[…]` field only if the field's body parses, and
  `CORRECTS_BODY` is built from the **undashed** `TOOL_ID_BODY` — so the dashed id **cannot** go in
  a `corrects:` field, and the correction row would have to name `:592` in prose. That is a real,
  measured limitation and it is the honest reason this is a judgement rather than a mechanical step.
* **Not bundled.** Landing a correction row requires the tool to be unblocked, i.e. the §4 diff
  applied first. Doing both in one commit would put a record edit and an instrument edit behind one
  review. **Commit per item.**
* **The lesson that is worth more than the correction row**: the smuggle guard cannot see a dashed
  hand-typed id, so *hand-typing an id in a shape the minter does not produce* routes around the
  one guard built to stop hand-minted ids. That is a lessons-file finding, and it is above this
  lane.

---

## 8. WHAT THIS LANE COULD NOT VERIFY

* **That the literal is right rather than merely narrow.** It admits exactly the bytes measured on
  HEAD today. If a second dashed id is ever found on another record or in an unpushed worktree, the
  choice should be re-argued from that evidence — not widened by reflex.
* **Whether the narrowness survives a future edit by anything other than §3c's tripwire.** Measured
  plainly: the **class** form also passes `--selftest`, so `append_record.py`'s own controls would
  not catch a future loosening. Only `check_record_reconciliation.py`'s literal-source mutation site
  would, and only by going stale. **A planted control that drives the two specimens in §3b rows 3
  and 7 would make the narrowness a limb rather than a comment** — the fixtures and their measured
  exits are in §3b and are ready to be lifted. **This lane did not add it: it is a further widening
  of an instrument diff the supervisor has not yet read.**
* **The two pre-existing reds in §6.** Reproduced and shown unchanged by this diff; **not triaged**.
  A crash is a finding until triage says otherwise, and that triage is not this lane's.
* **Nothing here touches the `M6J_L1` verdict.** `GATE FAIL` is a physics verdict from the
  hash-pinned frozen grader and neither touches nor is touched by this ledger.

---

## 9. RESULT

| | |
|---|---|
| `--selftest` BEFORE | `VERDICT: PASS (0 control failure(s))`, rc 0 |
| `--selftest` AFTER (patched copy) | `VERDICT: PASS (0 control failure(s))`, rc 0 |
| `check_record_reconciliation --selftest` AFTER | `VERDICT: PASS`, rc 0 |
| real M6J L1 append, `--allocate-id --dry-run` | **rc 7 → rc 0** |
| shape-audit refusal on a no-id candidate line | **rc 7, unchanged** |
| a second hand-typed dashed id | **rc 7, unchanged** |
| hand-minting guard (`HAND-WRITE tool-allocated id(s)`) | **rc 9, unchanged**, both drives |
| C3 "no id of its own" refusal | **rc 9, unchanged** |
| offenders on `docs/COST_CALIBRATION.md` | **1 → 0** |
| ids parsed / `max_for_series('C-')` | 491 → 492 / **20260833, unchanged** |
| **verdict on the draft** | **`PENDING` — awaiting the supervisor's personal diff read. NOT APPLIED.** |

**COST OF THIS LANE:** instrument drafting and control drives only — no solver, no ranks. Not a
compute row; rule 12's calibration does not apply to it and none is invented here.
