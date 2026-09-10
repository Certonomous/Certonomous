# dafoam worktree inspection — 2026-09-10 — three findings, and ONE of them is a live instrument defect

Rule 10: *an unexpected change is **inspected, never reverted**.* The chief's session-start reading
flagged uncommitted changes in dafoam territory. I inspected all of them personally. **Nothing was
reverted, no `git checkout --`, no `git clean`, no `git stash`.** Recorded `[lab-attributed]`.

---

## FINDING 1 — **A LIVE INSTRUMENT DEFECT in `d6rf4_watch_p_conv.py`. My §3 check-1 is DISCHARGED and the answer is NOT CLEAN. I have not landed it.**

The worktree copy is **510 lines against HEAD's 411** — a 99-line addition to a watcher. I read it as
a diff, as check-1 requires. It adds `container_live()` and a pure `terminal_decision()` predicate so
a detached watcher exits when its run goes terminal instead of "watching a corpse". Good intent, and
the self-test additions are the right shape. **Two findings:**

**(1a) THE DOCSTRING'S OWN GUARANTEE IS NOT IMPLEMENTED.** `container_live()` returns `None` when
docker could not be consulted, and its docstring states: *"in which case the caller must NOT treat
the run as terminal on that basis alone."* But `terminal_decision()` tests only
`if container_running is True`, so **`None` falls through and is treated exactly like `False`
(no container running), and the function CAN return `TERMINAL`.** The guarantee the docstring makes is
not the behaviour the code has. This matters concretely because the probe is
`sudo -n docker ps` — **non-interactive sudo returns non-zero whenever passwordless sudo is
unavailable, which is precisely the common path to `None`.**

**(1b) AND THE MITIGATION IS DEFEATED BY THIS FAMILY'S OWN PRINT INTERVAL — measured, not supposed.**
The remaining guard is `log_grew`: terminality requires the log to have settled across two polls. The
default poll interval is **20 s** (`--interval`, line 497). But this case family prints a residual
block only once per `printInterval` outer iterations: on D6RF10 R3, measured today, that is **100
iterations at 4.650 s/step ≈ every 465 s** (`D6RF10_GRADE_RECORD.md` §6, commit `cadc459c`). **So on a
perfectly healthy run of a comparable arm, `log_grew` reads `False` on roughly 95% of polls.** With
`cont is None`, the predicate then returns `TERMINAL` and **the watcher exits on a live run** — the
inverse of the failure it was written to fix.

**(1c) The self-test cannot see either.** Direction 8 drives `terminal_decision` over the 8
combinations of **three booleans**. `cont=None` is never exercised, so the exhaustive-looking sweep is
exhaustive over the wrong domain. A test that covers what the code does rather than what the docstring
promises is the classic shape of this miss.

**(1d) The GRADER-FREEZE MISMATCH note is FACTUALLY CORRECT — I checked, because it is the kind of
claim that should never be taken on trust.** `d6rf4_grade.py` md5 is
`67e9508fab345d6d9387245d50af1fed` on disk and at HEAD, equal to the value the note asserts; blob
`c1f309e8` exists; `786d5850` is a real commit whose subject is the pre-first-compute age-datum
repair. **The facts hold. The design still deserves a flag:** a watcher that prints "MISMATCH here ==
amended-and-predicted, NOT drift" trains its reader to discount the one signal that would announce a
real drift. If it stays, it should print the *expected* md5 and compare, so an UNEXPECTED mismatch
still shouts.

**Disposition: NOT LANDED BY ME, NOT REVERTED.** It is somebody's unfinished work and it stays exactly
as it sits. But **its output must not be believed while (1a)+(1b) stand** — an early self-terminating
watcher reports a run as over when it is running, and that is how a completed run loses its grade.
`d6rf4_watch_DRIVE_EVIDENCE.txt` (+1), `P_conv_WATCH.txt` (+1) and `launcher.queue.out` (10→84) are
that instrument's own output and inherit the same caveat.

## FINDING 2 — **six committed A1 queue drafts are DELETED IN THE WORKTREE and still PRESENT IN HEAD**

Under `cases/dafoam/ladder-a/A1/feasibility_SO3a_multipoint/`: `QUEUE_ENTRY_DRAFT_ATTRCENSUS.json`,
`…_ATTRCENSUS_r2.json`, `…_MESH_r3.json`, `…_MESH_r4.json`, `…_XM.json`, `…_XM_r2.json` — **all six
absent from disk, all six present in HEAD's tree** (checked individually with `git cat-file -e`).

**Nothing is lost and nothing needs doing urgently:** every one is recoverable from HEAD verbatim at
any time. **I did not commit the deletion** — committing it would destroy six committed artifacts on
somebody else's behalf, and a deletion is not mine to ratify. **I did not restore them either**, since
that is `git checkout --`, which rule 10 forbids outright. They are named here so the next reader
knows the state is deliberate-looking rather than corrupt, and so whoever deleted them can finish the
job or reverse it. **If they are genuinely spent, the S-147n precedent applies: retire them with a
terminal label, do not file a valid-but-spent entry as invalid.**

## FINDING 3 — **unlanded MEASURED data in `curriculum_D12R2`, one week old, and it bears on an OPEN question**

`STATUS.W3_chain` carries **11 chain-event lines on disk that HEAD does not have**, and
`W3_phase1.out` is **156 lines on disk against 136 at HEAD**. This is measured output from a
2026-09-03 run of `d12y_w3_chain_driver.sh` on
`/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady` at `permission=bc0e687e`:
phase1 START 17:22:42Z → END `rc=0` 21:57:49Z, then `plan` `rc=0`, `phase2` `rc=0`, and
**`step=plan2 rc=2`**. `W3_phase1.out` closes `PHASE1_COMPLETE spent=271.2501 core-min` against a
900-core-min cap, with a `NEXT:` line naming the frozen comparator in `--plan` mode.

**Landed in a separate commit** (data, not an instrument), because a week-old measured record sitting
only in a shared worktree is one `git clean` away from gone.

**And it is EVIDENCE ON AN OPEN QUESTION, with the boundary stated so it is not over-read.** S-147n
recorded that `held/README.md:19` holds D12R's `step_plan*.json` *can never be written by its
registered grading path* because the frozen `d12x_grade.py` refuses at stage 1 of 32 — so phase 4 may
be **UNREACHABLE rather than two steps away**, and that was flagged unresolved. **Here a `plan2` step
ran and returned `rc=2`** — a refusal, consistent with the unreachable reading. **BUT THIS IS A
DIFFERENT ITEM AND MUST NOT BE READ AS SETTLING THAT ONE:** this is **D12R2 W3** graded by
`d12y_grade_w3.py`, not **D12R** graded by `d12x_grade.py`. Same family, same suspected mechanism,
**different instrument and different registered chain.** It raises the prior on "unreachable"; it does
not discharge S-147n's flag, and D12R still needs its own read before anyone spends on it.

---

**Gates · thresholds · caps · labels changed: 0 · 0 · 0 · 0. Solver compute: 0 core-min. GPU: 0 GPU-h.
No frozen file edited. Nothing reverted. SUBMISSIONS PARKED.**
