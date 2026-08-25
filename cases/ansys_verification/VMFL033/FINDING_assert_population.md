# FINDING — the forbidden-`assert` population is **TWELVE**, not two, and the miscount has the same cause the supervisor's own message warns about

**Measured 2026-08-25T23:0xZ by `ansys-lane-opus`.** Filed in this lane's case directory
because the supervisor is not reachable by message. **This lane repaired NOTHING outside
its own case** — the corrected population is handed over for dispatch, not acted on
unilaterally, because sweeping other lanes' frozen comparators mid-run is exactly the
collision that cost this team a record tonight.

---

## 1. THE CORRECTION

The supervisor's brief named **two** comparators still carrying Amendment 6's forbidden
`assert verdict in VERDICTS`:

    cases/ansys_verification/VMFL021/R2/grade_vmfl021_r2.py:467
    cases/ansys_verification/VMFL017/R2/grade_vmfl017_r2.py:333

**Enumerated from HEAD, there are TWELVE**, and the two named are among them:

| # | file | line |
|---|---|---|
| 1 | `cases/ansys_verification/VMFL001/R2/grade_vmfl001_r2.py` | 649 |
| 2 | `cases/ansys_verification/VMFL001/grade_vmfl001.py` | 589 |
| 3 | `cases/ansys_verification/VMFL005/grade_vmfl005.py` | 532 |
| 4 | **`cases/ansys_verification/VMFL017/R2/grade_vmfl017_r2.py`** | **333** |
| 5 | `cases/ansys_verification/VMFL019/grade_vmfl019.py` | 306 |
| 6 | **`cases/ansys_verification/VMFL021/R2/grade_vmfl021_r2.py`** | **467** |
| 7 | `cases/ansys_verification/VMFL021/grade_vmfl021.py` | 325 |
| 8 | `cases/ansys_verification/VMFL022/grade_vmfl022.py` | 325 |
| 9 | `cases/ansys_verification/VMFL045/R2/grade_vmfl045_r2.py` | 800 |
| 10 | `cases/ansys_verification/VMFL045/grade_vmfl045.py` | 800 |
| 11 | `cases/ansys_verification/VMFL050/grade_vmfl050.py` | 346 |
| 12 | `cases/ansys_verification/VMFL051/grade_vmfl051.py` | 771 |

**Ten were missing from the dispatch list.** Every one is the same line — rule 1's
verdict-vocabulary guard, the single enforcement point for the fixed vocabulary, which
`python3 -O` strips.

## 2. THE CAUSE IS THE SUPERVISOR'S OWN POINT 2, APPLIED TO ITS POINT 1

The same message that carried the two-file list also warned, correctly:

> *"ENUMERATE POPULATIONS FROM HEAD, NEVER FROM `git ls-files`. The shared index is
> decayed… For comparators specifically, `ls-files` finds 3 where HEAD has 23."*

**Measured here, in the same invocation:**

    comparators at HEAD (git ls-tree -r HEAD)  : 23
    comparators via git ls-files (decayed index):  3

**A population of 3 cannot contain 12 hits.** The two-file list is consistent with an
`ls-files`-shaped enumeration and is **not** consistent with a HEAD-shaped one. **The
warning was written and the miscount was shipped in the same message** — which is the
useful part of this finding, not the arithmetic: *a lesson stated is not a lesson applied,
and the instrument has to be changed at every call site (CLAUDE.md rule 14).*

## 3. METHOD, so the count can be checked without trusting this lane

    git ls-tree -r HEAD --name-only \
      | grep -E 'cases/ansys_verification/.*grade_.*\.py$'          # 23 comparators
    # then, per file, from HEAD rather than from disk:
    git show HEAD:<path> | grep -nE '^\s*assert\b'

**Planted control on the count** (rule 3): the counting expression was handed a
constructed line containing a known `assert` and **returned it**, so the reader is shown
able to see a non-zero and its zeros are evidence. Files reported as zero are zero.

## 4. WHAT THIS LANE DID AND DID NOT DO

- **DID:** measure the true population and file it here, committed.
- **DID NOT:** touch any of the twelve. Eleven belong to other cases; `VMFL021/R2` grades a
  family that was in flight. **Repairing another lane's frozen comparator mid-run without
  dispatch is the VMFL036 collision repeated**, and the supervisor's own message states the
  exposure is **LATENT, not live** (nothing in this repository invokes `python3 -O`;
  `PYTHONOPTIMIZE` unset). There is no urgency that outweighs the collision risk.
- **This lane's own comparator, `grade_vmfl033.py`, carries ZERO `assert` statements** and
  is not on the list.

## 5. WHAT THIS LANE COULD NOT VERIFY

- **How the two-file list was actually produced.** §2 states what the evidence is
  *consistent with*; the supervisor's method was not observed and this lane does not assert
  it. The count itself is independent of that question.
- Whether any of the twelve has a *second* `assert` beyond the verdict guard: the sweep
  reports one per file and printed up to three per file, so a fourth-or-later `assert` in a
  single file would not have been shown.
