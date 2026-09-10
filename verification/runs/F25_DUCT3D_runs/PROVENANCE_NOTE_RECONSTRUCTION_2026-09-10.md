# F25_DUCT3D — provenance note: reconstructed time directories added 2026-09-10

**The `PASS` is INTACT. Every artifact the grader read is untouched.** This note exists
so that a future auditor does not read a 2026-09-10 timestamp inside a tree graded
2026-08-28 as tampering or as a re-run.

## What happened

A chief-dispatched export lane ran `reconstructPar -latestTime` on all three levels on
**2026-09-10 ~17:47–17:49Z**, to produce openable fields for demo filming. F25's graded
run was **decomposed only** (`processor0-3/`), so ParaView needed either Decomposed Case
mode or a reconstruction.

## What I verified, personally, before writing this

| artifact | mtime | touched today? |
|---|---|---|
| `F25_GRADED.json` (the verdict record) | 2026-08-28 16:15:06 | **no** |
| `fine/processor0/4000/` (a GRADED field) | 2026-08-28 07:00:06 | **no** |
| `fine/processor0/4000/U` | 2026-08-28 07:00:06 | **no** |
| `fine/0/` | 2026-08-28 05:09:35 | **no** |
| `fine/log.simpleFoam` | 2026-08-28 07:00:06 | **no** |
| `fine/RC.txt` | 2026-08-28 07:00:06 | **no** |
| **`fine/4000/` (NEW, derived)** | **2026-09-10 17:49:03** | **yes — created** |
| **`fine/4000/U`** | **2026-09-10 17:48:54** | **yes — created** |

**The decomposed fields the grader actually read predate the grading and were not
modified.** The reconstruction is a derived view of them. No input, no `0/`, no solver
log and no `RC.txt` was altered. The verdict in
`verification/campaign/F25_DUCT3D_RESULTS.md` stands unchanged.

## THE GENERAL FINDING, which is worth more than this case

**CLAUDE.md rule 4's age guard cannot distinguish a field written by the SOLVER from a
field written by a POST-PROCESSOR.** The guard requires every field at `endTime` to be
NEWER than the case's own `0/T`, because `0/T` is touched last at launch and so dates
the run allowed to produce the answer. A `reconstructPar` run today satisfies that
condition trivially — `fine/4000/U` at 2026-09-10 is newer than `fine/0` at 2026-08-28 —
**so the guard PASSES, and it passes on an artifact the solver did not write.**

That is not a defect in this export, which was benign, disclosed, and touched nothing
load-bearing. It is a property of the guard: **it dates a run by field mtime, and any
post-processor that writes fields re-dates it.** A run reconstructed a year later would
still clear the age guard. The guard's real protection is against a case whose `0/` is
NEWER than its results — a stale tree presented as fresh — and it remains sound for
that. It was never able to certify that the fields at `endTime` are the solver's own.

**What would close it, offered and not adopted here:** the age guard would need to be
paired with a check that the `endTime` fields are older than, or contemporaneous with,
the solver log's own last write — which for this tree they are not, and correctly so.

*Recorded by the cfd-supervisor, 2026-09-10, on a check prompted by a routine export.
No verdict is revised and no gate is touched.*
