# M1_multimodel_sweep queue entries -- FROZEN, VALIDATED, NOT IN THE DROP PATH

78 entries: 39 benchmark cases x 2 arms. `kOmegaSST_null` is the **planted
control** (standing rule 3), not padding; `kOmega` is the treatment arm.

## What these are

**Frozen.** Every entry carries
`prereg_commit = 73cd5ac578c4916a07ae05a9618e166832fdef75`, the full 40-character
sha, and `prereg_path = cases/RANS_LES_closure_models/M1_multimodel_sweep/PREREGISTRATION.md`.

**The pre-registration on disk IS the committed document.** Its sha256 is
`e15d0df3ee960b907b50a978db864cd1a112cd4723274f7bd2876df643d87572`, byte-equal to
`git show 73cd5ac5:cases/RANS_LES_closure_models/M1_multimodel_sweep/PREREGISTRATION.md`.
All five frozen M1 files hash identically at disk, at `73cd5ac5` and at HEAD.
(`PREREGISTRATION.md` and `stage_m1.py` were changed BY the amendment and so do
not match the earlier `7b00b3ec`; see the re-freeze section at the foot.)

**Every entry was ACCEPTED by `scripts/queue_entry_check.py`** -- 78 accepted, 0
refused -- with `--selftest` run FIRST and passing, so the validator was shown able
to refuse before its acceptance was believed (standing rule 3: a zero from a reader
not shown able to see a non-zero is not evidence). Acceptance is a mechanical guard
only. `SUPERVISION_CHARTER.md` sec.3 check 4 was performed personally by the
closure-supervisor and is recorded verbatim in each entry's `enqueued_by`.

**Byte-reproducible.** Re-running the frozen `make_queue_entries_m1.py` with the
same `--prereg-commit` and `--enqueued-by` reproduces all 78 entries byte for byte.
No entry is hand-edited. Cell counts are read live from each case's
`constant/polyMesh/owner`; all 39 match the frozen section 2.3 table (590,026 cells).

## THESE FILES ARE NOT IN THE DROP PATH, AND THAT IS DELIBERATE

`verification/queue/closure/` is a **launch button** (D535 / L-348). A valid entry
copied there is picked up by a cron-restarted daemon and **LAUNCHED** when the box
drops under the busy ceiling. Copying one of these files there starts a solver.
Filing is the supervisor's act, taken deliberately, never a side effect of tidying.

## `host` IS OMITTED ON ALL 78 -- READ THIS BEFORE ASSUMING IT WAS DECLARED

No entry here carries a `host` key. `scripts/queue_entry_check.py` **does not
validate that field at all** -- the string `host` does not occur in it -- so its
absence is not a validation finding and no ACCEPTED line speaks to it.
`scripts/queue_runner.py` line 461 reads `entry.get("host", "local")`, so an
omitted `host` means **this box**. That is the intended target for M1, but it is a
DEFAULT, not a declaration, and a reader must not mistake the one for the other.

## Cost, as registered

| quantity | value |
|---|---|
| sum `cost_core_min_estimate` | 1298.058 core-min (registered 1,298.1, section 9.2) |
| per arm | 649.029 core-min each (registered 649.0) |
| sum `cap_core_min_registered` | 1892.780 core-min |
| `ranks` | 1 on all 78 |
| `memory_floor_gb` | 1.0 on all 78 -- ESTIMATED, not measured |

The entries carry the **section 2.3 per-entry cap column** (summing to 1,892.780),
which section 9.2 line 914 is the clause that binds them. Section 9.2's headline cap
of **1,900.0** is a 0.38 % round-UP of the same figure; the entries sum BELOW it, so
the difference is conservative in the safe direction. Dollar figures anywhere in
this campaign are DERIVED at the owner-stated $0.0513/core-h and are NOT measured:
this box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` section 5).

## Disclosed defect: the generator's README template is stale

`make_queue_entries_m1.py` writes its own `README.md` into whatever output
directory it is given, and that template still opens
`# DRAFT -- NOT FROZEN, NOT COMMITTED, NO COMPUTE AUTHORISED` and states that
`prereg_commit` is the literal `PENDING_SUPERVISOR_FREEZE` and that "Nothing here
can launch" -- **regardless of the sha it was actually given**. All three statements
are false of the 78 frozen entries beside this file. The generator is frozen and was
NOT edited (standing rule 6); its emitted README was **superseded by this file**,
and the defect is recorded here rather than silently papered over. The same class --
a draft banner outliving the draft, because freezing updates the sha and never the
text that says "not frozen" -- was measured independently in
`G1_grid_triple/grade_g1.py:611`, which prints "(DRAFT, NOT FROZEN)" while frozen at
`03be2015`. `QUEUE_ENTRIES_DRAFT/` beside this directory is the genuine pre-freeze
draft set and its copy of the banner is true of it.

## Re-frozen at `73cd5ac5` -- M1 AMENDMENT 1, pre-compute

These entries were first cut against `7b00b3ec`. **M1 AMENDMENT 1** landed at
`73cd5ac578c4916a07ae05a9618e166832fdef75`, PRE-COMPUTE and with no gate,
threshold, cap or label touched, and the entries were re-cut against it: only
`prereg_commit` and `enqueued_by` moved, on all 78 and on no other key.

The amendment repaired `stage_m1.py` (`empty_residual_control` emptied at most one
`residualControl` block while its docstring claimed every one) and struck the
document's own closing line, which read "NOT FROZEN. NOT COMMITTED. NOT ENQUEUED."
under an opening paragraph reading "FROZEN by the closure supervisor on
2026-08-27" -- the same class as the stale generator README disclosed above.

Verified here, not relayed: the amendment is a **single diff hunk at line 1249**,
appended at the foot, 1,253 lines to 1,321, with **no line above it moved**. The
section 2.3 table (line 163: 39 cases, 590,026 cells, 649.0 / 946.4) and the
section 9.2 clauses (lines 911 and 914) are byte-unchanged, so every cost figure
below still cites the clause it names. `make_queue_entries_m1.py`, `run_m1.sh` and
`grade_m1.py` are byte-identical at `7b00b3ec` and `73cd5ac5`; only
`PREREGISTRATION.md` and `stage_m1.py` changed.
