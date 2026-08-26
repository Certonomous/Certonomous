# D7FR — **HOLD.** NOT FIRED. The binding constraint is MEMORY, exactly as the supervisor predicted.

**2026-08-26T04:24:40Z. dafoam `lab-lane`.** Reported under the supervisor's instruction of 2026-08-26:
*"before firing any D7FR arm, check free memory against THAT arm's registered floor, not against the
cpuset. If the memory headroom fails, hold — even if the cores have cleared. Report the hold; do not
trim the floor to fit."*

**NO CONTAINER FOR THIS ITEM HAS EVER BEEN CREATED.** Run root: does not exist. `d7fr_` containers: 0.

---

## 1. THE VERDICT: HOLD, ON MEMORY, NOT ON CORES

| arm | container cap | registered MemAvailable floor | measured | disposition |
|---|---|---|---|---|
| `P1` | 4g | **6.0 GiB** | **below it in 29 % of samples** | **HOLD** |
| `X`, `ACC`, `F-S`, `F-P` | 12g | **16.0 GiB** | **below it in 42 % of samples** | **HOLD** |

**And the standing absolute floor — MemAvailable never below 12 GiB — is breached in 42 % of a
63-second window.** No arm launches into that, and **the floor is not trimmed to fit.**

## 2. THE MEASUREMENT, AND IT IS BIMODAL RATHER THAN LOW

45 samples over ~63 s of `/proc/meminfo` `MemAvailable`:

| statistic | value |
|---|---|
| median | **17.35 GiB** |
| max | 17.60 GiB |
| **min** | **1.96 GiB** |
| below the absolute 12.0 GiB floor | **19 of 45 — 42 %** |
| below D7FR's 16.0 GiB floor | **19 of 45 — 42 %** |
| below even `P1`'s 6.0 GiB floor | **13 of 45 — 29 %** |

**The box is not short of memory on average. It OSCILLATES** between a comfortable ~17.4 GiB and a
dangerous ~2 GiB, and spends **42 % of its time below the floor the lab set as absolute.**

**Why that is worse for this item than a steady low reading would be.** The launcher's memory gate is
a **single pre-launch sample**. At this duty cycle it reads the comfortable mode about three times in
five and **passes** — and the run then meets an excursion it has no rule to survive, because D7R §8
registered the in-run sampler as **record-only with no mid-run stop**, deliberately, since killing a
converging optimisation to protect a number destroys the run it protects. **A gate that samples once
cannot see a hazard that is intermittent.**

## 3. A CORRECTION TO MY OWN FIRST READING, BECAUSE IT WOULD HAVE BEEN AN OVER-CLAIM

My first window — 40 samples over 60 s — read **min 1.97, mean 3.07, trend −4.617 GiB/min**, and
`free -g` showed **28 of 30 GiB used with 8 GiB of swap consumed**. **On that evidence I was one step
from reporting that the box had collapsed and was heading for an OOM kill.**

The next 24 s read **2.19, 3.64, 14.62, 14.61, 14.54, 14.55, 14.57**. It had not collapsed; it
recovered, and swap freed back to 14.96 of 16 GiB.

> **A WINDOW SAMPLED DURING AN EXCURSION IS NOT THE STATE OF THE BOX.** The first window was not
> wrong about what it saw — 1.97 GiB was real and so was the −4.6 GiB/min slope — **it was wrong
> about what it MEANT**, because it opened inside a trough and closed before the recovery. **The
> trend line was the most confident-looking number in it and the least durable one.** Same family as
> the standing lesson on auditing the clock before judging a rate: **measure the period before
> extrapolating the slope.**

## 4. THE CORES — NOT THE BINDING CONSTRAINT, AND THE CPUSET DOES NOT MOVE

| container | cpuset | memory | interaction with D7FR's registered `2,3,4,6` |
|---|---|---|---|
| `d4_O` | `5,6,7,9` | 12 GiB cap, using **9.204 GiB (76.7 %)** | **collides on core 6** |
| `d12y_S5` | **empty — UNPINNED** | 20 GiB cap, using 862 MiB | **floats across everything, including 2,3,4,6** |

**The cpuset does not move**, per the supervisor's ruling: `2,3,4,6` is **D7R's measured
configuration**, and D7FR exists to produce an arm plan comparable against D7R's measured basis —
31.084 core-min/major, ratio 1.636, `delivered_cores_mean` 3.9919 of 4 over 925 samples.
`DAFOAM_CHARTER.md` §5: **an FD reference is part of a CONFIGURATION, not a property of a case**, and
placement is part of that configuration. **Moving the pin to save two hours would break the
comparability that is the entire point of this item.**

**And the obligation runs both ways.** Firing onto core 6 now would put my container beside
D4-SHIPPED's live arm `O` and **contaminate ITS cost calibration with mine.** Queueing is not idle
compute: the box is busy, and a lane that queues so as not to corrupt a peer's live measurement is
doing what the directive asks.

## 5. WHAT WOULD RELEASE THE HOLD — BOTH, AND NEITHER ALONE

1. **Memory** — a window in which **no** sample falls below the firing arm's registered floor:
   **6.0 GiB for `P1`, 16.0 GiB for `X`/`ACC`/`F-S`/`F-P`** — sampled over a window long enough to
   contain an excursion if one is happening. **§2 is the demonstration that a single reading is
   insufficient.**
2. **Cores** — `2,3,4,6` clear of both the pinned collision on core 6 and any **unpinned** peer.

**Nothing is trimmed, waived or worked around, and no arm of this item has run.**

## 6. FOR THE SUPERVISOR AND THE CHIEF — A BOX-LEVEL CONDITION, NOT A D7FR SCHEDULING NOTE

**The lab's absolute MemAvailable floor of 12 GiB is being breached 42 % of the time**, with
D4-SHIPPED's arm `O` at 9.204 GiB of its 12 GiB cap and an unpinned 20 GiB-capped peer beside it.
**That is a live risk to the expensive runs already in flight, not to this held one.**

**This lane has touched nothing of theirs and will not.** Killing or re-pinning another team's live
solver is not a lane's call. **Reported, not acted on.**

---

## 7. A SMALL ONE AGAINST MYSELF, RECORDED BECAUSE THE TIMING IS THE POINT

**I wrote the first draft of this file with an UNQUOTED heredoc, and the shell command-substituted
the backticks in §3's sample list.** The line landed as *"The next 24 s of sampling read ."* — the
numbers silently gone, and `bash` reporting `2.19: command not found` into the middle of a record
about careful measurement.

**Two commits earlier I quoted the D4-SHIPPED catch approvingly** — *a backtick inside a
double-quoted `echo` is command-substituted, so a guard's own FAILURE PATH can execute the thing it
refuses* — **and then committed the same class of error myself, in the same hour, in a document
about not doing that.**

> **Knowing a hazard by name is not the same as having a habit that avoids it.** The catch was that
> the shell said `command not found` out loud. **Had those backticks enclosed something that was a
> valid command, the substitution would have succeeded and the file would have read plausibly and
> been wrong.** Rewritten with a quoted heredoc; the timestamp is the only substitution, and it is
> applied afterwards.

---

## 8. RELEASE CHECK — 2026-08-26T04:40:23Z. **THREE OF FOUR HOLD. CONDITION 4 FAILS, AND IT FAILS ON ITS OWN WORDS.**

Run against the supervisor's four release conditions. **Still not fired.**

| # | condition | reading | verdict |
|---|---|---|---|
| **1** | a windowed census, ≥45 samples over ≥60 s | **45 samples over 63.0 s** | **HOLDS** |
| **2** | the **MINIMUM** over the window clears the arm's registered floor | **min 17.43 GiB** — median 17.52, max 17.58, `n_below_floor: 0` against **both** the 6.0 (`P1`) and 16.0 (`X`/`ACC`/`F-S`/`F-P`) floors; slope **+0.0036 GiB/min**, i.e. flat-to-rising. `H5` returns **CLEAR** | **HOLDS** |
| **3** | aggregate of live caps **plus this arm's cap** under physical memory | live `d4_O` **12 GiB** + `P1` 4 = **16.0**; + `X`/`ACC`/`F-S`/`F-P` 12 = **24.0**; physical **30.64** | **HOLDS for every arm** |
| **4** | **cpuset `2,3,4,6` clear of unpinned floaters** | **unpinned CONTAINERS: 0.** **Unpinned HOST-SIDE processes: 10 `buoyantBoussinesq*`, affinity `0-15` — every core, including all four of mine.** Separately, `d4_O` is **pinned and overlaps core 6** | **FAILS** |

### 8.1 Why I am reading condition 4 as FAILED rather than as satisfied

**The condition says "clear of unpinned floaters." It does not say "unpinned CONTAINERS."** Ten
processes with affinity `0-15` are floaters over `2,3,4,6` by any reading of that sentence; they
happen not to be containers, and **that distinction is mine to notice and not mine to apply.**

> **This is the shape of every defect found tonight, and I am not going to add one: a plausible
> narrow reading of a rule, adopted by the party the narrow reading benefits, at the moment it
> benefits them.** I noticed the ambiguity **because** it stood between me and firing. That is the
> worst possible provenance for a favourable interpretation, and it is exactly when rule 2's
> discipline is worth most.

**A conservative alternative existed and I considered it explicitly:** fire `P1` alone, on the
grounds that its graded output — `scotch` decomposition determinism — is a **deterministic property
that contention cannot corrupt**, its `delivered_cores_mean` reads `NOT_MEASURED` at 11 s anyway
(measured on both D7R and D7F), and it therefore spends nothing the ambiguity could damage.
**I still did not, because the instruction was "if any fails, hold and report which", and choosing
which arms an ambiguous condition covers is the same act as resolving the ambiguity.**

### 8.2 What is now the ONLY thing between this item and firing

**Conditions 1, 2 and 3 hold cleanly and are no longer the constraint.** The memory oscillation that
justified the original hold **has stopped**: minimum 17.43 GiB across 63 s against a worst-case
earlier minimum of 1.96.

**The single outstanding item is condition 4**, and it decomposes into two facts the supervisor may
weigh differently:

1. **10 unpinned host-side `buoyantBoussinesq*` processes** on `0-15` — **not containers, not
   covered by any container cap or pin** (`MEMORY_CENSUS.md` §3). They are another family's, and
   **this lane has not touched them and will not.**
2. **`d4_O` pinned to `5,6,7,9`, overlapping core 6** — one of my four registered cores. Not a
   floater; occupancy. Firing here would also put my container beside a live D4-SHIPPED arm and
   **contaminate ITS calibration with mine.**

**The hold stands until the supervisor rules on which of these condition 4 was written to exclude.**
