# PROPOSED — `mpirun -np 1` in a container binds every rank to CPU 0

**NOT FILED. NOT APPLIED TO ANY FROZEN FILE. NOT SENT ANYWHERE.** This is a lane's
draft note for its supervisor, written beside the case it was found in
(CLAUDE.md rule 13 — the scratchpad is not a handoff channel). Whether it becomes a
lesson, a docket item or a change to any launcher is not this lane's call.

**Found:** 2026-08-25, DAFoam lane D8, while the D8 `opt` arm was running.

## The defect, measured

Four DAFoam containers were live on this box (D8's `opt`, and three D13 lane arms
`d13_s1/s2/s3`). Every one had been launched with `--cpus=1`, and the box has
**16 cores with 61 % of them idle**. Every container was nevertheless running at
**exactly 25 % of one core**.

The cause is not the cgroup. `cpu.max` read `100000 100000` (one full core) and
`cpu.stat` showed `nr_throttled 6` in 1,483 periods — negligible. The cause is
**process affinity**:

| container | pid | comm | affinity list |
|---|---|---|---|
| `d8_opt_…` | 2230086 | `mpirun` | `0-15` |
| `d8_opt_…` | 2230463 | `python` | **`0`** |
| `d13_s3_…` | 2229080 | `python` | **`0`** |
| `d13_s2_…` | 2228276 | `python` | **`0`** |
| `d13_s1_…` | 2227626 | `python` | **`0`** |

**OpenMPI binds by default (`--bind-to core`), and inside a container whose cpuset
is the full `0-15` it binds rank 0 to the FIRST core — core 0 — in every container
independently.** `--cpus=1` is a CFS *quota*, not a *placement*: it caps a container
at one core-equivalent but says nothing about WHICH core. So N concurrent
single-rank DAFoam containers all land on core 0 and each runs at **1/N speed**,
with the other 15 cores idle. Nothing in the container's own log or in
`docker inspect` says so.

## The measurement, before and after

Measured on D8's own container as `usage_usec` delta over a wall interval:

| | CPU fraction of one core |
|---|---|
| **before** (rank on core 0, four containers colliding) | **0.2504** |
| **after** `taskset -a -pc 8-15 <pid>` | **0.9994** |

**A 3.99× speed-up, at zero compute cost, from one affinity call.** The solver's
own clocks agree: over the affected window `ExecutionTime` advanced 17.23 s while
`ClockTime` advanced 69 s — a ratio of **0.2497**, against ≈1.00 on a quiet box
(`P2-a6-n16/patched.log` line 539: `ExecutionTime = 4.67 s  ClockTime = 5 s`).

## Why nobody has seen it before

Every prior A6 item ran **alone**. `P3-a6-n16-rem` measured 102.1 s per primal as
the only DAFoam container on the box; with a second concurrent container the same
primal would have taken ~204 s and the item would simply have looked "contended".
**This defect is invisible to a single-arm item and is exactly proportional to how
many lanes the lab runs at once** — so it gets worse the harder the lab is pushed,
which is the opposite of what a contention allowance assumes.

It also means a `core_min` figure from any multi-lane DAFoam day is inflated by
close to the number of concurrent DAFoam containers, and **cost calibration rows
that attribute such a gap to "contention" are attributing it to the wrong cause**:
this is not scheduler contention on a loaded box, it is self-inflicted
serialisation on an idle one.

## What D8 did, and did not do

* **Did:** retarget **its own** two processes with `sudo taskset -a -pc 8-15`.
  This touches no frozen file, alters no gate, threshold, cap or label, and
  changes no computed quantity — the same binary and the same inputs on a
  different core. Disclosed as a dated amendment in D8's `RESULTS.md`, with the
  cost of the affected window named separately as waste, never absorbed into the
  actual/predicted ratio.
* **Did NOT:** touch the three D13 containers. They are a peer lane's **running
  solvers**. Moving D8 off core 0 raised their share from 25 % to 33 % as a side
  effect; nothing was done to them directly.
* **Did NOT:** edit `d8_run_arm.sh`. It is frozen by md5 in D8's pre-registration
  §9 and first compute had already occurred.

## Proposed remedy — for a FUTURE launcher, not a frozen one

Either of these, in whichever launcher a supervisor decides to change:

```
mpirun --allow-run-as-root --bind-to none -np 1 ...
```

or, per container at `docker run` time,

```
--cpuset-cpus=<a distinct core or range per concurrent lane>
```

`--bind-to none` is the smaller change and needs no cross-lane coordination.
**Neither is applied here.** A launcher change is a supervisor's call, and every
launcher it would touch is frozen inside somebody's pre-registration.

## What is NOT established

* Whether the same collision affects **multi-rank** arms (`-np 4`). A rank set is
  bound to cores 0..n-1, so two concurrent `-np 4` arms would collide on all four.
  **Not measured here** — stated absent, not approximated.
* Whether any specific historical `core_min` figure is inflated by this. Deciding
  that requires knowing how many DAFoam containers were live during each run, and
  **no such record was consulted.** No past row is corrected by this note.
