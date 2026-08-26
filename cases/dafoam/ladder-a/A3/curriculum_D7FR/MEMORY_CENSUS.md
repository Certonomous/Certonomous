# BOX MEMORY CENSUS — facts only. Nothing ruled, nothing re-pinned, nothing killed, nothing fired.

**2026-08-26, ~04:28–04:33 UTC. dafoam `lab-lane`.** Requested by the dafoam-supervisor. **This
document rules nothing and recommends nothing.** Every figure is a reading; where I have an
association rather than a cause, §4 says so and stops there.

**Read-only throughout:** `docker ps`, `docker inspect`, `/sys/fs/cgroup/.../memory.*`, `/proc`.
**No other lane's files were opened and no container was signalled.** D7FR remains **HELD** and its
run root does not exist.

---

## 1. THE CONDITION HAS CHANGED SINCE IT WAS DESCRIBED, AND THAT IS THE FIRST FACT

**The 32-GiB-on-30 overcommit is real and I confirm it for the moment it was measured. It is NOT
present now.** `d12y_S7_plant` — the 20 GiB-capped, unpinned D12R2 container — **has exited.**

| | at the supervisor's reading | **at this census** |
|---|---|---|
| live dafoam containers | 2 | **1** |
| sum of registered caps | **32 GiB** | **12.0 GiB** |
| physical `MemTotal` | 30.64 GiB | 30.64 GiB |
| overcommit | **+1.4 GiB, 104 % of physical** | **−18.6 GiB, 39 % of physical** |

**A census reports what is, not what was.** The overcommit condition cleared **by a peer container
exiting**, not by anything being fixed — so **it recurs the moment D12R2 launches its next stage.**

## 2. EVERY LIVE DAFOAM CONTAINER — A SERIES, NOT A SAMPLE

50 samples over ~85 s (04:30:32 → 04:32:13), 1.7 s apart.

| field | reading |
|---|---|
| name | `d4_O_20260826T040414Z_3177545` |
| item | **D4-SHIPPED**, arm `O` |
| registered memory cap | **12 GiB** |
| cpuset | **`5,6,7,9`** — pinned, compliant |
| present in | **50 of 50 samples** — the whole window |
| RSS min / median / max | **9.68 / 9.68 / 9.68 GiB** — flat to two decimals |
| cgroup `memory.peak` | **9.68 GiB = 81 % of its cap** |
| cgroup `memory.swap.current` | **0.000 GiB at every sample** |

**It is the only live dafoam container.** Its RSS is flat and its peak equals its current, so it has
**not** ballooned and retreated inside this window.

## 3. THE SUM OF CAPS AGAINST PHYSICAL MEMORY — AND THE SUM OF CAPS IS NOT THE DEMAND

| term | GiB |
|---|---|
| physical `MemTotal` | **30.64** |
| sum of live dafoam container caps | **12.00** |
| **host-side solver RSS, under NO container cap** | **1.88** |
| caps + host-side actual | **13.78 — 45 % of physical** |

> **AND THIS IS THE FINDING I DID NOT EXPECT. THERE ARE 10 `buoyantBoussinesq*` SOLVER PROCESSES
> RUNNING ON THIS BOX RIGHT NOW, OUTSIDE ANY CONTAINER.** Their cgroup is
> `/user.slice/user-1000.slice/session-1843.scope` — **not a docker cgroup, so no container memory
> cap covers them** — and their CPU affinity is **`0-15`: every core, unpinned**, including D7FR's
> registered `2,3,4,6` and D4-SHIPPED's `5,6,7,9`.
>
> **A rule that sums dafoam CONTAINER caps is necessary and not sufficient on this box**, because a
> whole class of load is not a container at all. Stated as a measurement for the supervisor to do
> with as they judge; **this lane rules nothing and has not touched them.**

## 4. DO THE EXCURSIONS COINCIDE WITH A D12R2 STAGE? — **I CANNOT SAY, AND HERE IS EXACTLY WHY**

**I have neither causation nor a clean correlation. I have a coincidence at WINDOW granularity, and
that is all.**

| window | dafoam containers live | `MemAvailable` |
|---|---|---|
| A, ~04:1x | `d12y_S5` (20 GiB, **unpinned**) + `d4_O` | **min 1.96**, 19 of 45 samples below the 12 GiB floor |
| B, ~04:2x | `d12y_S7_plant` + `d4_O` | 20 samples, **min 17.47** — clean |
| C, this census | **`d4_O` alone** | 50 samples, **min 17.31, 0 below either floor** |

**Window B is the one that forbids the easy conclusion.** A D12R2 container was live in B and there
were **no excursions**. So *"a D12R2 container is present"* does **not** predict the excursions, and
any claim that it does is contradicted by my own data.

**AND THE HONEST LIMIT IS AN INSTRUMENT LIMIT, NOT AN INFERENCE ONE: my window-A sampler recorded
`MemAvailable` ONLY. It did not record container identity per sample**, so I cannot align an
excursion with a stage even in principle from that data. **A per-sample container census exists now**
— it is what produced §2 — **but the condition it would resolve is not currently on the box.**

> **What I have: three windows, and excursions in one of them. What I do not have: a single sample
> in which an excursion and a named stage are recorded together. I am not going to name a stage on
> that.**

## 5. SWAP — WHO TOUCHED IT, AND IT WAS NOT A DAFOAM CONTAINER

| | |
|---|---|
| `SwapTotal` | 16.00 GiB |
| `SwapFree` now | **15.00 GiB** — **1.00 GiB in use** |
| `SwapFree` at the excursion (window A) | **7.04 GiB — ~8.96 GiB in use**, since recovered |
| **`d4_O`'s cgroup `memory.swap.current`** | **0.000 GiB at every one of 50 samples** |

**NO DAFOAM CONTAINER HAS BEEN SWAPPED.** D4-SHIPPED's arm `O` shows exactly zero cgroup swap across
the window, so **its MPI ranks' timing is not swap-corrupted** and its cost figures are not
contaminated on that ground.

**The swap that IS held, attributed by `/proc/<pid>/status VmSwap`:**

| holder | `VmSwap` |
|---|---|
| **10 host-side `buoyantBoussinesq*` processes** | **0.532 GiB total** |
| this session's own `claude` process | 0.124 GiB |
| remainder | unattributed among smaller processes |

**HONEST LIMIT ON THE ~8.96 GiB SWAPPED DURING WINDOW A: I cannot attribute it.** The container that
was live then has exited and **its cgroup is gone with it**, so `memory.swap.current` for
`d12y_S5` is unreadable now and unrecoverable. **That figure is measured at the box level and
unattributed at the process level, and it will stay that way** — naming a holder retrospectively
would be a guess wearing a number.

## 6. D7FR'S OWN STATUS, UNCHANGED

**HELD.** Run root does not exist; `d7fr_` containers: 0. **The memory limb of the release condition
reads clear in this window** (0 of 50 below 16.0 GiB) — **and by §2 of `HOLD_RECORD.md` I do not read
85 clean seconds as durable evidence**, which is the same over-read I corrected myself for there.
**The cores limb is not met**: `d4_O` still occupies core 6, which is inside D7FR's registered
`2,3,4,6`. **The hold stands until the supervisor lifts it.**
