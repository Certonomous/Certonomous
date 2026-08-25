# VMFL036 — PRE-REGISTRATION ADDENDUM 02 — A COMPARATOR REPAIR UNDER §2d.1

**Dated 2026-08-25.** A change was made **on the grading path after first
compute**. `VERIFICATION_CHARTER.md` §2d forbids that; **§2d.1's four-condition
repair exception permits it when, and only when, all four hold.** All four are
answered below, in order, so the exception can be checked rather than claimed.

The frozen `PREREGISTRATION.md` is **unchanged and still byte-identical** to its
blob at `ff9e28daea7aa2cc502d1ee32efc5c138e1deef7`. **No gate, threshold, band, reference
value, cap, window, level list or label moved.**

## THE DEFECT

`run_vmfl036.sh` writes each level's exit record as
`rc = 0` — **with spaces around the `=`**. `grade_vmfl036.py` parsed
that file with

    re.findall(r"(\w+)=(.*)", open(rc_path).read())

which requires the `=` to **abut** the key. Against `rc = 0` the pattern matches
**nothing**: `\w+` consumes `rc`, then demands `=` and finds a space.
**Every field therefore fell back to its default**, `rc` defaulted to `"1"`, and
the strict-completion guard refused every level with

    REFUSE[C1]: ... records rc=None -- a non-zero exit is a finding, triage it

## THE REPAIR

    re.findall(r"(\w+)\s*=\s*(.*)", ...)   with the value .strip()ped

Nothing else in either file was touched.

## THE FOUR CONDITIONS

**(1) A DEMONSTRABLE ERROR, not a preference.** The regex cannot match the string,
and that is provable by inspection and was proved by execution: the guard refused
on real, complete, `rc = 0` runs. There is no reading on which `rc = 0` should
parse to `rc = None`.

**(2) ESTABLISHED BY AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS — the
load-bearing condition.** The defect was found by the **rule-4 strict-completion
guard**, which §2d.1 names explicitly as qualifying ("a near-identity, **a
guard** or a control"). **That guard grades nothing.** It emits no Cd, no St, no
band comparison and no verdict — it only refuses. Decisively: **the defect made
the comparator produce NO NUMBER AT ALL (exit 2).** A repair to a component that
was returning a refusal rather than a value **cannot have been selected to move a
verdict in a wanted direction**, because before the repair there was no verdict
and no direction to select. This is the shape the exception is cut to fit.

**(3) DISCLOSED, THE INSTRUMENT NAMED, AND WHAT MOVED QUANTIFIED.** Disclosed
here. The instrument is named above. **What moved, quantified: NOTHING in any
gate.** The repair changes which characters a key/value reader accepts. It makes
`rc`, `wall_s`, `core_min`, `ranks`, `timeout_s_granted` and the cap
fields readable where they were previously invisible. It does not touch the
reference value, the band, the level list, the window, the Roache classifier, the
planted controls, the mesh birth certificate or the tier ceiling. **The gate
arithmetic is bit-identical before and after; it simply could not be reached.**

**(4) THE PRE-REPAIR VALUES RECORDED BESIDE THE PUBLISHED ONES.**
**The pre-repair value is a REFUSAL, not a value.** For the record, in full:

| level | PRE-REPAIR comparator output | POST-REPAIR |
|---|---|---|
| every level of this case | `REFUSE[C1] ... rc=None`, **exit 2, no number emitted** | reads `rc = 0` and proceeds to the completion clauses |

No published number has a different pre-repair counterpart, because **no number
was published, or publishable, before the repair.**

## WHAT ELSE WAS CHECKED BEFORE REPAIRING, so this is ONE repair and not several

Before touching either file, **both comparators were run in memory against every
level that had completed**, with the regex emulated rather than edited, to find
every defect the guards could catch in one pass. **The regex was the only one.**
Everything else came back clean on real artifacts — mesh birth certificates,
residuals, plateau/settling, and both planted controls. That evidence is in
`RESULTS.md`.

## OPERATIONAL CONSEQUENCE, STATED SO IT IS NOT A SURPRISE

`grade_vmfl036.py` on disk **no longer hashes equal to its blob at
`ff9e28daea7aa2cc502d1ee32efc5c138e1deef7`**. That is correct and intended: any
**future** launch of this case must name **this repair's commit** as its
`--prereg-sha`, and the launcher will refuse the old one. The runs already in
flight recorded the blobs they verified in their own `LAUNCH_RECORD.txt` at
launch, so what those runs were graded against remains provable from the record.
