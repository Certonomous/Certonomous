# THE rule-12 COST ROW FOR M6J_L1 IS DRAFTED AND **BLOCKED**. THE BLOCKER IS OURS.

**Status: `BLOCKED`.** Not `PENDING` — nothing is queued and waiting its turn; a landing was
attempted, it was refused, and the refusal is correct.

**The comparison itself is NOT blocked and is NOT owed.** Rule 12's estimate-versus-actual is
done and filed at `GRADING_RECORD_M6J_L1.md` §9, with the ratio, all four attribution lines
(misprediction / re-rank / waste / contention) and dollars labelled derived. **What is blocked
is the LEDGER LANDING of that comparison as a row in `docs/COST_CALIBRATION.md`.** The drafted
row is `COST_CALIBRATION_ROW_PENDING.md` beside this file, ready to land unchanged.

## WHAT REFUSED, AND WHY IT IS RIGHT TO

`scripts/append_record.py --path docs/COST_CALIBRATION.md --allocate-id` refuses:

> REFUSED: a line matches this record's id-bearing CANDIDATE SHAPE and the id pattern parses
> NO id from it. That is a REFUSAL CONDITION, not an absence (D549, upheld by verification at
> `a0e2e9a2`): the maximum this module asserts against would silently omit these lines.
> HEAD:docs/COST_CALIBRATION.md:592

**MEASURED, on HEAD's bytes, before anything was concluded:**

| | |
|---|---:|
| ids in the file matching the strict pattern | 269 |
| ids of the **dashed-date** shape `C-2026-09-13T…` | **1** |
| line | `HEAD:docs/COST_CALIBRATION.md:592` |
| the id | `C-2026-09-13T202608.816749Z-9830ff70` |
| landed by | **`95408812c`** — *"cfd WOLF DYNAMICS DrivAer COARSE IS GRADED…"* |

**THE DEFECT IS CFD'S OWN, FROM TWO COMMITS AGO.** Every other timestamp id in the file is
`C-%Y%m%dT…` — no dashes in the date — which is the shape `--allocate-id` mints. This one
carries `%Y-%m-%d`. **It was hand-typed into the tool's shape instead of being minted by the
tool**, and the id pattern `^\|\s*(?:\*\*|~~)*\s*(C-\d+)\s*…` cannot parse it, because after
`C-` it requires digits and finds `2026-09-13T…` — it matches `C-2026` and then fails on the
`-`. It is one character class away from parsing and it is blocking the whole ledger.

**Blast radius: every team.** `docs/COST_CALIBRATION.md` is one flat `C-` series and this
module is the only sanctioned way into it. Until this is repaired **no team can land a rule-12
row**, and rule 12 makes a completion report without one incomplete. This is not an M6J problem.

## WHY THIS LANE DID NOT FIX IT

The module names the two legal repairs and forbids the third:

> The fix is one of TWO REGISTER EDITS in `scripts/append_record.py`, **never an edit to the
> record**: widen that record's entry in `RECORDS` if the line carries a real id in a form the
> pattern cannot see, or add its form to `KNOWN_EXCLUDED` if it deliberately is not an id.
> **Measure which, on the real bytes, before choosing.**

**Measured, the answer is `RECORDS`, not `KNOWN_EXCLUDED`:** line 592 carries a *real, unique,
intended* id — it is a substantive cfd calibration row, not a second block under an existing id.
So the repair is to widen the `RECORDS` pattern for this record to admit the dashed-date form.

**This lane did not make that edit, on purpose.** `scripts/append_record.py` is a **shared
gating instrument used by all six teams**, and `SUPERVISION_CHARTER.md` §3 makes
measurement-script diffs a supervisor's **personal, non-delegable** check — *"a relayed check is
a summary, not a check."* Widening an id-parsing pattern is exactly that class of diff: it
changes what every future append is allowed to call an id, in every record the module guards.
**A lane slipping that into a grading commit is how a gate gets loosened by someone with no
mandate to loosen it**, and the fact that the loosening would be convenient for this lane right
now is the reason to refuse it, not a reason to make it.

**And the record is NOT to be edited to make the tool happy.** Retyping line 592's id would
mutate a landed row in an append-only ledger — the one repair the module explicitly forbids.

## WHAT IS ASKED OF THE SUPERVISOR

1. **Read the `RECORDS` diff as a diff** and decide the pattern widening for
   `docs/COST_CALIBRATION.md` (admit `C-\d{4}-\d{2}-\d{2}T…` alongside `C-\d+`), with
   `--selftest` driven after.
2. **Then land `COST_CALIBRATION_ROW_PENDING.md` unchanged** via `--allocate-id`. Its numbers
   are measured and final; nothing in it waits on the repair.
3. **Consider whether `95408812c`'s row wants a correction row** naming the hand-typed id, so
   the next cfd lane mints instead of types. That is a judgement above this lane.

**Nothing here changes the M6J_L1 verdict.** `GATE FAIL` is a physics verdict from the
hash-pinned frozen grader and does not touch, and is not touched by, this ledger.
