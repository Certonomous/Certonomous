# A3-era run-root `setsid` rc audit — the NOT ESTABLISHED half of UPDATE 11 §11.3, now ESTABLISHED

**Dated 2026-08-26.** Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`. Nothing here is filed, sent or posted (`CLAUDE.md` rule 7).
**Every settled A3 verdict this record touches is NAMED, NOT REOPENED** (standing bound; `75f1074b`).

## 0. The question, and the hazard shape measured rather than quoted

`heat-transfer` measured lab-wide that `$?` read from a `setsid …` line can be 0 for every outcome. `75f1074b` (dafoam UPDATE 11)
verified every **tracked** dafoam launcher CLEAN and stated the one place it did not look: the A3-era launchers described by
eleven pre-registrations as "setsid + `.t0/.rc/.t1` self-ledger", which live in run roots **outside git**. This record looks there.

**Planted control, run 2026-08-26 on kernel `7.0.0-1011-aws`** (sacrificial copies under the lane scratchpad; the numbers, not the path, are the evidence):

| shape | line | rc captured |
|---|---|---|
| foreground in a non-interactive script | `setsid timeout 5 false; echo $?` | **1** — propagated (setsid `exec`s when the caller is not a process-group leader) |
| foreground **with job control** (`set -m`; the interactive-shell launch shape) | `setsid timeout 5 false; echo $?` | **0** — **THE HAZARD SHAPE, REPRODUCED**: setsid forks and the parent returns 0 before the child runs |
| backgrounded | `setsid nohup timeout 5 false … &; echo $?` | **0** — the background-launch status, not the command's |
| rc captured **inside** the session, both job-control settings | `setsid bash -c 'timeout 5 false; echo $? > x.rc'` | **1** — the safe shape |

So the hazard is not "setsid" as a word; it is **an rc read on the launching side of a setsid that forked**. The safe shape is
the rc written by the detached process itself. That is the distinction every row below is graded on.

**Grep control (L-337).** `grep -rl --include='*.sh' setsid` over every `A3-*` root plus `f5c-stageA-A3` returns **nothing**; the
same command with a planted `PLANTED_A3_control.sh` (`setsid timeout 5 false`) added to the search set returns the plant. The
empty result is a reading, not a blind reader.

## 1. Census — run roots outside git (`/home/ubuntu/certonomous-runs/`)

`grep -rl --include='*.sh' setsid /home/ubuntu/certonomous-runs/` returns exactly two files, **neither in an A3 root**:
`D12R2W2R_phase1_wrapper.sh` (this lane's own wrapper, fired today; `setsid` appears only in a comment; rc is `rc=$?` of the
launcher in-session → `STATUS.phase1`; CLEAN) and `F12_field_observation_2026-08-25/run_obs.sh` (cfd territory; audited by cfd at
`4225ef0c`; NAMED, NOT AUDITED HERE).

Twenty-three A3 roots exist (`A3-*` ×22, `f5c-stageA-A3`). Seventeen carry a `.rc` self-ledger. Seven launcher scripts survive on disk:

| root | launcher (outside git) | `setsid` in file | where `.rc` comes from | `.rc` on disk | verdict |
|---|---|---|---|---|---|
| `A3-onera-m6-adjoint-vcoarse` | `run_arm.sh` | no | `:14 echo $? > "$BASE/.rc"` after the **foreground** `sudo -n docker run` at `:8-13` | **1** | **CLEAN** — rc captured inside the detached script; the value 1 proves the channel carries non-zero (`A3_SUBLU_RESULT.md:26` cites exactly this `.rc = 1`) |
| `A3-onera-m6-sweep-n15_21840` | `run_arm.sh` | no | `:14`, same shape | **0** (last writer) | **CLEAN** — attempts 1/2 of the same root wrote rc=1 and rc=137 (`A3_SUBLU_SWEEP_PREREGISTRATION.md:98,125`), so the channel carried non-zero twice before the 0 |
| same root | `run_arm_fd3.sh` | no | `:13`, same shape | (shared `.rc`) | **CLEAN**; `A3_FD3_PREREGISTRATION.md:78` cites rc=0 from this channel with 197 s wall and a log |
| same root | `run_arm_ctrl.sh` | no | `:13`, same shape | (shared) | **CLEAN** as to setsid. `A3_SUBLU_RESULT.md:292` records "rc=0 (the wrapper's known false-success)" — **that is the DAFoam/mphys wrapper returning 0 on KSP reason −5, a solver-side hazard already named in that record, NOT the setsid hazard.** Not conflated here. |
| same root | `run_arm_tpc1.sh` | no | `:13`, same shape | (shared) | **CLEAN** |
| `A3-rung2-n28-tpc1` | `run_arm_a.sh` | no | `:24 echo $? > "$BASE/.rc"` after foreground `docker run` `:17-23` | **0** | **CLEAN**; log `fd3_run.log` ends `End` + `Finalising parallel run`; `A3_RUNG2_N28_RESULT.md:37` cites rc=0 with 606 s wall |
| same root | `run_arm_b.sh` | no | `:24`, same shape | (shared) | **CLEAN** |

Every other `.sh` in an A3 root (`preProcessing.sh`, `preProcessing_snappyHexMesh.sh`, `Allclean.sh` — tutorial-stock) contains
no `setsid` and writes no rc anywhere.

**Thirteen `.rc` roots have NO launcher script on disk** (the launch was an inline command; the pre-registrations describe it).
The `.rc` shape is still readable from the value the channel carried:

| root | `.rc` | corroboration | verdict |
|---|---|---|---|
| `A3-diag-rung2`, `A3-diag-rung3`, `A3-gateB-restoration`, `A3-rung3-fill1`, `A3-rung3-n52`, `A3-rung3-restart1000`, `A3-saad-overlap2`, `A3-stage2-lgmres` | **1** | non-zero reached disk — a launching-side `$?` after a forked setsid cannot produce 1 | **CLEAN — proven by the value** (`A3_RUNG3_N52_RESULT.md:25`, `A3_RUNG3_RESTART_CHALLENGE_PREREGISTRATION.md:110`, `A3_SAAD_DELIBERATE_CONDITIONING_PREREGISTRATION.md:237`, `A3_RUNG3_FILL1_ENGINEERING_PREREGISTRATION.md:67` cite these rc=1 values) |
| `A3-stage2-gamg` | **137** | SIGKILL reached disk (`A3_STAGE2_UNREACHABLE_CLASS_PREREGISTRATION.md:158`) | **CLEAN — proven by the value** |
| `A3-gateA-regression`, `A3-stage0-n28-richardson`, `A3-triage-fill1`, `A3-triage-restart1000`, `A3-triage-richardson` | **0** | launcher absent, so the shape is **not** readable from the file; each log carries `End` and `Finalising parallel run` (`gateA.log:811`, `stage0_richardson.log:800`, `triage_fill1.log:811`, `triage_restart1000.log:811`, `triage_richardson.log:811`), and sibling roots launched under the same pre-registration (`A3_TRIAGE_LEVERS_PREREGISTRATION.md:104`, `A3_SAAD_DELIBERATE_CONDITIONING_PREREGISTRATION.md:115`) wrote rc=1 through the same convention | **CLEAN by convention + log corroboration; the launcher file itself is gone and I say so.** No graded verdict rests on these five `.rc = 0` values alone — each record cites the log's own content beside it. |

Six roots carry no `.rc` at all (`A3-onera-m6-adjoint-coarse`, `-probe80k`, `-sweep-n28_42120`, `-sweep-n8_10920`, `-transonic`,
`f5c-stageA-A3`): no rc channel exists there for a setsid line to poison. Not in scope of the hazard.

## 2. Census — tracked A3 launchers at HEAD (`git ls-tree -r HEAD cases/dafoam/ladder-a/A3/`, never `ls-files`)

Twenty-one `.sh` blobs; **zero contain `setsid`** (`git show HEAD:<f> | grep -q setsid` over each). The two graded drivers take rc
from the foreground line into the arm ledger — `rung1_patched_idwarp_np4/drive.sh:81 local RC=$?` and
`rung3_patched_idwarp_np4_attempt2/drive.sh:87 RC=$?`, each echoed into the ledger line at `:89` / `:96` — the harness-`$?`
reading already named as latent lab-wide in UPDATE 2, not the setsid hazard. **CLEAN as to setsid.**

## 3. Verdict table

| launcher set | verdict |
|---|---|
| 7 surviving A3 run-root launchers (§1) | **CLEAN** — rc captured inside the detached script from a foreground `docker run`; `setsid` lives only on the invoking line and its `$?` feeds nothing |
| 9 `.rc`-only roots with non-zero `.rc` (§1) | **CLEAN**, proven by the value the channel carried |
| 5 `.rc`-only roots with `.rc = 0` (§1) | **CLEAN by convention + log corroboration**; launcher file absent, stated |
| 21 tracked A3 `.sh` at HEAD (§2) | **CLEAN** — no `setsid` anywhere |
| EXPOSED-LATENT | **none found** |
| EXPOSED-REALISED | **none found** |

**Settled A3 verdicts NAMED, NOT REOPENED:** `A3_SUBLU_RESULT.md`, `A3_RUNG2_N28_RESULT.md`, `A3_RUNG3_N52_RESULT.md`, the
FD3 / TPC1 / control / triage / SAAD / stage-2 / restart-challenge pre-registration outcomes, and
`ladder-a/A3/rung{1,3}_patched_idwarp_np4{,_attempt2}/RESULTS.md`. Nothing above changes a number, gate or label in any of them.

## 4. What this does not establish

The audit reads **rc channels**. It does not re-grade any log, does not touch the separate solver-side "wrapper false-success"
(rc=0 on KSP reason −5) that `A3_SUBLU_RESULT.md` already names, and does not audit cfd's `run_obs.sh`. The five rc=0 roots whose
inline launch command was never a file cannot be graded from a file; they are graded from the value, the log and the
convention, and that is a weaker claim than the other rows and is labelled as one.
