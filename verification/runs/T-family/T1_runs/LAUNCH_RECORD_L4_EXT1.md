# T1b L4 extension (ext1): launch record

Launched 2026-08-25 16:36:43-16:36:44 Z under
`docs/campaigns/T-family/T1b_L4_EXT2_PREREGISTRATION.md`, frozen at commit
`72e9b58aed484a99a09b00f400f11a5f0854a56a` **before any of these solvers
started**. Protocol: `T1b_L4_AMENDMENT.md` section 4 (registered 2026-08-21,
frozen, not edited). **No verdict and no tier is assigned by this record.**

## Processes

| case | wrapper pid | solver pid | cwd | start (UTC) | added its | new endTime | cap (core-min) | ranks | enforced timeout (s) |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `R_10k_x` | 2199763 | 2203927 | `verification/runs/T-family/T1_runs/R_10k_x` | 2026-08-25T16:36:43Z | 12 000 | 32 000 | 1 100 | 1 | 66 000 |
| `R_100k_x` | 2201241 | 2203944 | `verification/runs/T-family/T1_runs/R_100k_x` | 2026-08-25T16:36:44Z | 14 000 | 94 000 | 1 300 | 1 | 78 000 |
| `R_300k_x` | 2202714 | 2203947 | `verification/runs/T-family/T1_runs/R_300k_x` | 2026-08-25T16:36:44Z | 30 000 | 110 000 | 2 750 | 1 | 165 000 |

`R_30k_x` converged exactly at its registered `endTime` and is **NOT
extended**; its `controlDict` is untouched at `endTime 80000`.

Timeout is enforced as the pre-registered identity
`timeout_s = cap_core_min * 60 / ranks`, coded that way in the runner. On cap
the solver is killed, `rc = 124` lands in `STATUS_ext1.<case>`, and the frozen
`mark_done_t1b_L4.py` refuses the case. **An overrun stops the run; it does not
get a new budget.**

## Restart verified at launch

First `Time` line of `log.solve.ext1`: **20001 / 80001 / 80001**, exactly one
past each case's `ExecutionTime` count in `log.solve` (20000 / 80000 / 80000) —
the frozen marker's replay/skip test (`check_ext`) is satisfied at the resume
point. `checkMesh` re-run into `log.checkMesh.ext1`, `End` reached in all three.

## What was preserved, and what was not written

`log.solve`, `log.checkMesh`, `STATUS.<case>` and `0/T` are **never written** by
the extension runner. Because `purgeWrite 2` unlinks the graded checkpoints as
new ones appear, the two graded time directories of each extended case were
**hardlink-preserved before launch** (verified by matching inode) at
`verification/runs/T-family/T1_runs/PRESERVED_L4_graded/<case>/`:

| case | preserved | plus |
| --- | --- | --- |
| `R_10k_x` | `18000/`, `20000/` | `controlDict.pre_ext1` (`endTime 20000`) |
| `R_100k_x` | `78000/`, `80000/` | `controlDict.pre_ext1` (`endTime 80000`) |
| `R_300k_x` | `78000/`, `80000/` | `controlDict.pre_ext1` (`endTime 80000`) |

Hardlinks, so no extra disk is consumed and the data survives the purge.
Today's graded numbers keep their artifact on disk.

The existing `DONE.R_*_x` markers now certify a superseded pre-extension state.
The frozen `mark_done_t1b_L4.py` removes them itself, with reasons printed, once
an `ext1` log is present and the extended case does not yet meet the rule — that
is its registered behaviour and it is left to do it.

## Files added by this launch

| path | role |
| --- | --- |
| `run_one_t1b_L4_ext1.sh` | detached extension runner of the section-4 `run_one_ext1.sh` form, writing `STATUS_ext1.<case>` (the name the frozen marker reads) and enforcing the cap |
| `launch_t1b_L4_ext1.sh` | foreground guarded launcher, `setsid nohup` detach |
| `PRESERVED_L4_graded/` | hardlinked graded checkpoints and pre-extension controlDicts |

No frozen file was edited: not `T1b_L4_AMENDMENT.md`, `analyse_t1b_L4.py`,
`mark_done_t1b_L4.py`, `mark_done_t1b_ext1.py`, `run_one_ext1.sh`,
`analyse_t1b.py` or `analyse_t1c.py`. The only edit to a tracked case input is
`endTime` in the three `system/controlDict` files, which is the extension
itself.

## Gap in section 4, reported as a finding

Section 4 registers the extension runner "of the `run_one_ext1.sh` form ...
`STATUS_ext1.<case>` beside `STATUS.<case>`", but the existing
`run_one_ext1.sh` writes **`STATUS3.<case>`**, which `mark_done_t1b_L4.py`
(`STATUS_EXT = "STATUS_ext1"`) does not read. Running that script verbatim
would have produced a case the marker refuses for "no STATUS_ext1 file". A new
runner carrying the registered form under the required name was therefore
written rather than reusing the file. Section 4 also registers no cap, no
timeout and no collision guards for an extension; those come from the
pre-registration and from the guard structure of `run_one_t1b_L4.sh`, and
neither adds to, subtracts from nor reinterprets any gate.
