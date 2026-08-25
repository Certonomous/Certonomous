# F5b Physics `physics_p1` — LANE STATE (resume record)

**This file is the handoff channel for this run.** `SendMessage` to the cfd supervisor
has failed on every attempt this session, so state goes to disk and is committed. A
successor reconstructs from artifacts here, **never from an agent's memory** — a watcher
dies with the agent that armed it, and one already did on this run.

**Stamp:** 2026-08-25T16:23:27Z. **Launched:** 2026-08-25T16:14:24Z. **Ranks:** 1 (serial).

## Status: RUNNING — not yet gradeable

| what | value |
| --- | --- |
| driver pid | `2150043` (`PID.txt`) |
| last `Time` | 8.2636775 of `endTime` 21.9440 |
| steps | 9717 |
| `ExecutionTime` | 542.18 s = **9.04 core-min** of the **72.0 cap** |
| `record.json` | ABSENT (written only on driver success — D-2) |
| cap breached | **NO** |

## Do NOT

- **Do not relaunch.** One run only. The wrapper refuses if `physics_p1` exists (D-1: E2's
  `run_case` would `rmtree` the evidence).
- **Do not edit the frozen reader** `analyse_f5b_physics.py` (blob
  `6c6d34d02e6de925457dbfdbf75a0e004168f345`) — F5b has FIRED; rule 6 governs.
- **Do not arm an in-agent watcher.** It dies with you.

## The OS-level sampler

`watch_f5b.sh`, launched `setsid`, **PPID 1**, session leader. Writes:
- `WATCH_LOG.txt` — a sample every 15 s: wall, ExecutionTime, t, steps, loadavg.
- `WATCH_TERMINAL.txt` — written **once**, on exactly one of:
  `TERMINAL=COMPLETE` / `TERMINAL=DIED_NO_RECORD` / `TERMINAL=CAP_BREACH_STOPPED`.
  On cap breach it **stops the run** — an overrun does not get a new budget (rule 12).

**To resume: read `WATCH_TERMINAL.txt`.** If absent and the sampler is gone, re-read the
solver log directly; do not infer.

## Grading, when `WATCH_TERMINAL.txt` says COMPLETE

`python3 verification/runs/F5b_runs/analyse_f5b_physics.py grade --run verification/runs/F5b_runs/physics_p1`
run **unmodified**. Frozen bands: G1 `A_L >= +2.00 C_L.deg`; G2 a pair with
`|da| <= 2.00 deg` and `dC_L >= 0.40`; G3 Courant `2.00x` / `1.00 %` / `5 consecutive`.
Single grid — **rule 5 not applicable, no GCI exists or may be printed.**

## Clause 1 is a DISCLOSED, TESTED PROXY — not a measured rc

**Four limbs measured, one graded by a disclosed proxy. Never "all five measured."**
The frozen reader prints **`NO rc IS RECORDED ON DISK`** on the face of the clause and
that stays on the face of the result. The rc is **structurally unavailable** on the
registered path: `setsid` detaches so the solver outlives its launching agent, and the
wrapper then exits, so nothing ever reaps the driver.

**Disclosed circularity:** part of the proxy is `End` on the prelude logs, and `End` is
itself another limb of the same conjunctive rule. `record.json` presence is the
independent half — and even it proves only that the driver **reached its final write**,
not that it **exited cleanly**.

**The proxy was PLANTED and shown able to see a failure** —
`verification/runs/F5b_runs/plant_rc_proxy_control.py`, graded by the frozen reader's own
`check_completion`, on synthetic trees, never touching this case:

| arm | clause 1 | expected |
| --- | --- | --- |
| N clean synthetic tree | True | True — OK |
| **P1 `record.json` ABSENT (driver raised)** | **False** | False — **OK** |
| P2 `log.potentialFoam` missing | False | False — OK |
| P3 `log.blockMesh` has no `End` | False | False — OK |
| P4 `record.json` written, solver then died | True | *blind spot, bounded below* |

**P1 found a real defect in the frozen instrument's SELFTEST** (not its behaviour): both
branches of `if break_clause != 1` in `_synthetic_run` write `record.json` identically,
so every previous exercise of clause 1 tested only the prelude-`End` path. **The
load-bearing branch had never been shown able to fail, and the selftest reported green
throughout.**

**P4's blind spot, bounded precisely.** On the synthetic tree clause 2 caught it, but
**that does not generalise**: a driver dying *after* the solver completed and *after*
`record.json` was written passes clause 1 **and every other limb** — `End` present, last
time == `endTime`, fields present, counts agreeing, age guard holding. **The whole
conjunctive rule is blind to that case.** The bound that makes it acceptable: in exactly
that scenario the solve **is** complete and every field is on disk with the age guard
satisfied, so what is lost is knowledge of the driver's **post-completion exit hygiene**,
**not the integrity of the graded quantity.** It cannot reach the measurement.

## Carry-forward to the NEXT F5b pre-registration — two items, neither to be lost

1. **A real rc on disk.** Launch as `setsid bash -c 'CMD; echo $? > RC.txt; sync'` so
   clause 1 reads a measured integer and this proxy is never needed twice.
2. **A clause-1 breaker that actually breaks the `record.json` branch**, so the selftest
   stops being vacuous on the half that carries it.

Neither may be applied to the frozen artifacts now: **F5b has fired.**
