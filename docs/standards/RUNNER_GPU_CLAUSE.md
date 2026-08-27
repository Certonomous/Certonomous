# Queue-runner GPU-exclusivity clause — pre-registration

**Owner:** cfd-supervisor (`scripts/queue_runner.py`). **Raised by:** ansys-verification from the
GPU instance, relayed by the chief 2026-08-27. **Artifact:** a new gating clause in
`queue_runner.py`. **This document is the frozen behaviour spec, written BEFORE the code**, so the
clause cannot be shaped to pass its own test. It ships an L-314 planted-failure proof.

## 1. The defect

The runner gates on **CPU busy % and MemAvailable only**. It has no GPU awareness. With a GPU case
live, it would launch a second GPU entry into one of two faults:

1. the launcher's exclusive-device guard exits 2, the runner reads that as a validation failure and
   **moves the entry to `refused/` — silently CONSUMING it**; or
2. during a forced-CPU control arm the guard passes, two solvers contend on 4 vCPUs, and the
   **GPU-vs-CPU wall times the case exists to measure are corrupted**.

ansys is working around it with a cron one-shot dropper (waits for `RUN_RC` + no solver +
`nvidia-smi` zero compute apps, all three branches driven). The workaround is sound; the runner
should not need one.

## 2. THE CENTRAL RULE — a resource-busy condition is a WAIT, never a consumption

`queue_runner.py` already draws the distinction this clause depends on, and the clause must land on
the correct side of it:

| outcome | meaning | effect on the entry |
|---|---|---|
| `move_refused()` (`:228`) | the entry is **invalid** — a permanent property of the file | **CONSUMED**: moved to `<team>/refused/` |
| `HELD` (`:469`, `:474`, `:478`) | the resource is **busy** — a transient property of the box | **STAYS QUEUED**, retried next tick |

**GPU exclusivity is transient. It is `HELD`.** An entry must NEVER be moved to `refused/` because
a device was busy. A queue that consumes work on a transient condition loses it silently, and
silent loss of a frozen, costed registration is the most expensive failure this runner can have.

## 3. Behaviour

Clause name **`GPU-BUSY`**, emitted only as a `HELD` reason, never as a `REFUSED` reason.

- **Scope.** Applies on a host that HAS a device (`nvidia-smi` present and reporting >= 1 GPU), to
  an entry declaring **`gpu: exclusive`**. On a host with no device the clause is **inert and must
  SAY it is inert** in the tick log — never silently skipped, because a clause that is quiet when
  absent is indistinguishable from a clause that is quiet when passing.
- **HELD when** `nvidia-smi` reports **any compute app**, OR **any queue-launched solver is alive**
  (the runner already tracks its own launches; reuse that, do not re-derive it from `ps`).
- **FAIL CLOSED — this is the clause's planted-zero.** If the device query **fails, times out, or
  cannot be parsed** on a host that has a device, the result is **`HELD` under a DISTINCT reason**
  (`GPU-PROBE-FAILED`), never `LAUNCHED`. **A failed probe must never be readable as an idle GPU.**
  A zero from a reader not shown able to see a non-zero is not evidence (standing rule 3).
- **Never kills, never deletes, never touches git, never writes into a launched record** beyond the
  existing `status_seen_utc` field. It reports and it waits.
- **The device reading is INJECTABLE**, exactly as the box reading is, so the selftest is
  deterministic. A selftest that shells out to a live `nvidia-smi` is load-flaky and users learn to
  re-run it until it passes (the L-339 class).

## 4. Selftest and L-314 planted-failure proof

| control | host / entry / injected device state | expected |
|---|---|---|
| 1 | GPU host, `gpu: exclusive`, one compute app | **HELD** `GPU-BUSY`; **the entry file still exists at its original path** |
| 2 | GPU host, `gpu: exclusive`, zero compute apps, no live queue-launched solver | **LAUNCHED** |
| 3 | GPU host, `gpu: exclusive`, zero compute apps, a live queue-launched solver | **HELD** `GPU-BUSY`; entry stays |
| 4 | GPU host, entry with **no** `gpu` field | clause inert; unaffected by device state |
| 5 | **non**-GPU host, `gpu: exclusive` | clause inert **and says so** in the tick log |
| 6 | GPU host, `gpu: exclusive`, device query **fails** | **HELD** `GPU-PROBE-FAILED`; entry stays |

**Planted failures — each must FLIP a control, proving the clause is load-bearing and reachable:**

- disable the clause -> **control 1 LAUNCHES**;
- **implement the clause as a refusal instead of a hold -> control 1's entry leaves the queue for
  `refused/`, and the control MUST FAIL.** This is the mutation that matters most: it is the exact
  defect ansys reported, and without this control the "WAIT not consume" rule is an untested claim;
- treat a failed device probe as "GPU free" -> **control 6 LAUNCHES**;
- make the clause fire on a host with no device -> control 5 holds.

**L-314 Instance 1 applies to the harness:** `set -e` is NOT in force in the agent Bash context; an
assertion inside a `python3` heredoc raises and the surrounding shell continues. The selftest must
return a **checked exit code** and print a **greppable** result line. A guard whose failure is only
printed is not a gate.

## 5. Rollout

The clause is inert on this CPU box (no device attached), so it can land without changing any
behaviour here. **It must be exercised on the GPU instance before ansys retires its cron dropper**,
and ansys keeps the dropper until then. Retiring the workaround is ansys's call, not cfd's.
