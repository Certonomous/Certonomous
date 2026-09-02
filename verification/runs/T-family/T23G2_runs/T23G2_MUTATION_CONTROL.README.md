# READ THIS BEFORE READING `T23G2_MUTATION_CONTROL.out`

**Sidecar to a capture. The capture is not edited and must not be.**
`T23G2_MUTATION_CONTROL.out` is the clean-control run of the T23G2 comparator for
the mutation exercise of 2026-09-02. Its evidential value is that it is what the
run emitted; a capture that has been edited is no longer a capture. This file
exists because the capture contains five lines that a reader opening it on its
own would reasonably misread, and the capture cannot be annotated in place.

---

## 1. THE FIVE `ABSENT-AT-FREEZE` LINES ARE A HARNESS ARTIFACT, NOT A FINDING

Lines **11, 14, 17, 20 and 23** of the capture each read:

```
      pre-registration (frozen)  : ABSENT-AT-FREEZE   DIFFERS
```

**All five grading-path members appear to differ from the freeze. They do not.**

The control ran in a **disposable scratch mini-repo with no git object store**.
`grading_path_shas()` in `analyse_t23g2.py` resolves the frozen column with
`git rev-parse 976776f4:<path>` through the module's `_git()` helper, which
returns `None` on a non-zero exit; the caller then substitutes the literal
`ABSENT-AT-FREEZE`, and the `IDENTICAL`/`DIFFERS` comparison against that literal
can only ever produce `DIFFERS`. Every one of the five is the same failed lookup,
not five measurements.

**This is already recorded** in `docs/campaigns/T-family/T23G2_RESULTS.md` §15.1,
which states that the control is line-for-line identical to `T23G2_GRADE.out`
except these five lines and the capture wrapper's `EXIT_CODE=3` trailer, and that
**all 161 remaining lines are byte-identical — no gate, value, order, GCI or
verdict differs.** This sidecar closes a gap in the standalone artifact only, not
a gap in the record.

**The consequence §15.1 draws, restated because it bounds the exercise:** because
the frozen sha column read `ABSENT-AT-FREEZE` throughout the harness, **no kill in
the mutation exercise could have come from the frozen-sha comparison.** The
`I`-family kills are on-disk-presence kills, not sha kills.

---

## 2. THE REAL VALUES — PINNED, AND THEY DRIFT

**These values are a reading at one commit. They are not a property of the
grading path, and they must be re-derived, never quoted forward.**

- **Measured at HEAD `b1d9070cb4ed4495a31f4eccb1e53527ff61d796`**
- **2026-09-02T23:06:16Z**
- **Command, per member:** `git hash-object <path>` compared against
  `git rev-parse 976776f4:<path>`

| grading-path member | at that commit |
|---|---|
| `docs/campaigns/T-family/T23G2_PREREGISTRATION.md` | **DIFFERS** |
| `docs/campaigns/T-family/analyse_t23g2.py` | **DIFFERS** |
| `docs/campaigns/T-family/t23g_readonly_diagnosis.py` | **IDENTICAL** |
| `verification/runs/T-family/T23_runs/mark_done_t23.py` | **DIFFERS** |
| `scripts/roache_triple.py` | **IDENTICAL** |

**Two identical, three differing — at that commit and no other.**

**Why the pin is not pedantry.** The lane that ran the exercise measured this
column earlier the same evening and read **three** identical and two differing.
That reading was correct when taken and was wrong within the hour, because
**Addendum A3 landed at `b1d9070c`, 2026-09-02T23:04:31Z**, moving
`T23G2_PREREGISTRATION.md` from `IDENTICAL` to `DIFFERS` through a change that was
entirely proper. A sidecar written to correct a misleading permanent artifact
must not itself become one.

---

## 3. A `DIFFERS` IS NOT PER SE ALARMING — THE QUESTION IS WHETHER IT IS ACCOUNTED FOR

At the commit above, each of the three is accounted for by a **licensed, recorded**
change:

- `analyse_t23g2.py` — the granted §2d.1 grading-path repairs (R2, R3, R4 band
  limb, R5), recorded in its own in-file amendment block.
- `mark_done_t23.py` — REPAIR R1, the `CASES` allow-list widening, recorded in its
  amendment record at the foot.
- `T23G2_PREREGISTRATION.md` — **Addendum A3** at `b1d9070c`, the §7
  comparator-path correction, which touches no gate.

**A `DIFFERS` with no such account is the thing that would matter, and there is
none here.**

---

## 4. THE FINDING THAT SURVIVES ALL OF THIS, AND IS THE REASON THE COLUMN MATTERS

**The recorder's discriminating power is spent on precisely the two files that
hold every constant the surviving mutations exploited** — the bands, the
convergence and plateau tolerances, `BAND_TRANSFER_REGISTERED`, `YPLUS_MAX`,
`RATIO_MIN`, `GRADING_PATH`. Those constants live in `analyse_t23g2.py` and
`mark_done_t23.py`, and both already read `DIFFERS` for licensed reasons, so a
further content change to either is **invisible in that column**.

**And nothing compares the printed sha against a recorded expected value.** The
recorder prints; it does not assert. Detection therefore rests on a human diffing
against a number nobody has committed. Separately, `analyse_t23g2.py` has **no
freeze coverage at all**: `scripts/check_comparator_freeze.py` walks only
`verification/` and `cases/`, and this comparator lives under `docs/campaigns/`.

---

## 5. PROVENANCE NOTE ON HOW THE FIGURES IN THIS FILE WERE OBTAINED

In this environment **`grep` is a shell function wrapping `ugrep`**, while
`timeout grep`, `xargs grep`, `env grep` and `find -exec grep` `execvp` the
**binary — GNU grep 3.11** — a different program with no ignore-file logic. A
ugrep-only flag under the wrapper can exit 2 having searched nothing, and when
stdout is piped `$?` is the pipeline's last element, so it can read as a clean
zero.

**Applicability to this exercise: the three findings that rested on a search were
re-derived with the GNU binary and independently in Python, and all three
reproduced exactly.**

| finding | bare (ugrep wrapper) | `env grep` / `find -exec` (GNU 3.11) | Python |
|---|---|---|---|
| scripts naming `analyse_t23g2` | 0 files | 0 files | — |
| freeze-report rows naming `T23G2` | 0 | 0 | 0 |
| `sys.flags.optimize` occurrences | — | — | comparator 0, `roache_triple` 1, `mark_done` 0 |

The only path ignored under `scripts/` is `scripts/__pycache__`, which holds no
source. **No count in the mutation exercise was taken from a wrapped recursive
sweep whose denominator a bare search would have narrowed.** The `assert` counts
reported for `t23g_readonly_diagnosis.py` (4) and the other three instruments (0)
were taken by AST walk, not by search.

---

## 6. WHAT THIS FILE IS NOT

It is **not** a correction to the capture, **not** a re-run, and **not** a gate
verdict. The rung verdict is `NOT A RESULT` and nothing here affects it. The
`KILLED` / `SURVIVED` / `SURVIVED-CHANGED` / `UNCONSTRUCTABLE` labels in the
exercise are the driver's own mutation-outcome labels and are **never** to be read
as `CLAUDE.md` rule 1 gate verdicts.

Full analysis: `docs/campaigns/T-family/T23G2_RESULTS.md` §15.
Companion sidecar: `T23G2_MUTATION_SET_REGISTERED.README.md` in this directory.
