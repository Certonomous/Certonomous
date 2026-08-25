# D7R — `P1` PASS. `P2` HELD ON CAPACITY. Two findings, one of them in this item's own registration.

**Date:** 2026-08-25. **Lane:** dafoam `lab-lane`. **Pre-registration frozen `88690717`, before any
compute for this item.**

## 1. `P1` — PASS

| | |
|---|---|
| rc | **0** |
| wall | **11 s** |
| cost | **0.733 core-min** against CAP **8.0**, CEILING **32.0** |
| runaway guard | `cap_reported=no`, `ceiling_hit=no` |
| kernel | `inspect(exit,oomkilled)=[0 false]` |
| memory | `memavail_pre 16.93`, `min_during [16.787 n=1]`, floor 6.0 — held |
| placement | cpuset `2,3,4,6` |

**The new launcher works.** `D7R_RUNAWAY_GUARD arm=P1 cap_core_min=8.0 ceiling_core_min=32.0
mode=report_then_stop_at_ceiling` — the detached-run + poll architecture replacing D7's `timeout`
SIGKILL, with the new `cap_reported` / `ceiling_core_min` / `ceiling_hit` ledger fields populated.

**The sibling census now carries real content**, which D7's `P2` could not demonstrate because
nothing else was running: `siblings_pre` and `siblings_post` both name
`d12r_S3b…` and `d4_F3…`. In D7 those fields were empty and the emptiness was (correctly) read as
"no sibling contention" — **but an empty field cannot distinguish "no siblings" from "the census is
broken", and this run is the first evidence that the census can actually see something.**

### 1a. G8 re-derived on THIS item's own evidence, not inherited

`d7r_g8_token.py --selftest`: **4 units, 4 passed** — the real evidence passes, and **three
mutations each make G8 fail** (one differing cell, `n=3` subdomains, cell sum 42113 vs the
registered 42120). Then, on D7R's own `P1` artifacts:

```
D7_G8_EVALUATED pass=True identical=True n_subdomains=4 sum_cells=42120 registered=42120
  map_A={"processor0":10635,"processor1":10506,"processor2":10538,"processor3":10441}
  map_B={"processor0":10635,"processor1":10506,"processor2":10538,"processor3":10441}
```

**D7R did not inherit D7's G8 verdict; it re-derived it from its own arm's artifacts**, through the
committed `curriculum_D7/d7_grade.py`'s own `g8_decomp`.

## 2. FINDING — §8's REGISTERED MEMORY FLOOR IS NOT STRICT ENOUGH TO GUARANTEE THE ABSOLUTE FLOOR

**Found by arithmetic before it mattered, in this lane's own registration, written 40 minutes ago.**

At 2026-08-25T22:18:41Z, MemAvailable **16.88 GiB**, two peer dafoam containers live, load 15.37/16:

| | |
|---|---|
| §8 registered launch floor for a 12g arm | **16.0 GiB** → 16.88 **CLEARS** |
| D7 `P2` measured peak consumption | **≈ 9.4 GiB** (`memavail` 26.55 → `min_during` 17.125) |
| MemAvailable during an equivalent run | **≈ 7.48 GiB** |
| the supervisor's **ABSOLUTE** floor | **12.0 GiB** → **BREACHED** |

**§8's floor gates the reading at launch; it does not gate the reading during the run.** Those are
different quantities, and on a box with live peers the second is the one that matters. **A launch
that passes the registered gate can still drive the box below the absolute floor**, and this item
would have done exactly that.

**`P2` IS THEREFORE HELD.** Required MemAvailable for a ≈9.4 GiB consumer to keep 12.0 GiB free is
**≥ 21.4 GiB**.

**What was NOT done, and why it is not an amendment.** §8's floor is a **threshold**, and **first
compute for D7R has happened** (`P1` fired), so rule 2 closes it — it cannot be altered by an
addendum. **It has not been.** The registered gate stands exactly as frozen and still applies. What
this lane is additionally doing is **declining to launch on the supervisor's standing absolute
floor**, which is an external operational constraint that **can only ever make launching stricter,
never permit one the registered gate would refuse.** **Tightening is not widening**, and the
distinction is why this is legal where an amendment would not be.

**For the next registration:** the memory gate should be stated against **projected MemAvailable
during the run** — launch reading minus the measured peak consumption — not against the launch
reading alone.

## 3. FINDING — GATE `H1` IS UNTESTED, AND THE ATTEMPT TO TEST IT IS WHY I KNOW

`H1` (§5) is this item's guard that the colouring `O` inherits was built by an arm of **this** item
returning `rc = 0` — the gate that stops the cache D7R declined to reuse from re-entering by
accident.

**It was deliberately tested and the test did not reach it.** D7's cache — 3,076,152 bytes, built
by an arm that returned `rc=124` — was planted in D7R's run root with **no provenance record**, and
arm `O` was fired. It returned **exit 5**, but on a **different guard**:

> `ABORT arm O requires …/P2/d7_baseline.json (the measured baseline primal); sec.1 forbids a
> typed-in CL target`

**The CL-target guard sits ahead of `stage_coloring` in the `O` branch, so `H1` can only ever be
reached after `P2` has produced a baseline.** The planted cache was removed immediately, the staged
`O/` directory deleted, and **no container was created** — D7R is cold.

> **`H1` IS REGISTERED AND UNTESTED. It is NOT claimed as a working control.** The exit-5 refusal
> observed was the CL-target guard doing its job, and reporting it as an `H1` pass would be exactly
> the substitution this lane has refused three times today. **`H1` is tested after `P2` completes,
> by restoring the same planted cache with the provenance record moved aside.**

## 4. Cost so far

| arm | predicted | actual | ratio |
|---|---|---|---|
| `P1` | 0.30 | **0.733** | **2.44** |

**Attribution, and it is not a mispricing of the work.** D7's `P1` measured **0.267** core-min at
wall 4 s and that was the basis. D7R's `P1` did the **same work** — two `decomposePar` runs on the
same 42,120-cell mesh, identical maps — in **11 s**. The difference is **box load: 15.37 of 16 with
two peer dafoam containers live**, against a quiet box for D7. **Contention, not misprediction**,
and it is named separately rather than folded into the ratio. The absolute figure (0.73 core-min
against an 8.0 cap) makes it immaterial to any budget, but it is a **measured contention factor of
≈ 2.7× on a short arm** and that is worth carrying into future estimates.

**Arm `O` H1-control attempt: 0.000 core-min** — refused pre-launch, no container created.

Calibration row deferred to this item's completion, per rule 12's process-completion trigger.

## 5. Standing

* `P1` — **PASS**.
* `P2` — **PENDING**, held on capacity (§2). Not a `GATE FAIL`, not `BLOCKED`: nothing has been
  attempted and nothing has refused it.
* `O`, `F-S`, `F-P` — **PENDING** behind `P2`; `F-S`/`F-P` additionally gated on the `D4-DEF-4`
  repair this item does not author (§6 of the registration).
* **`D7-DEF-4`'s `29.16`-vs-`291.6` pinned-witness prediction remains UNTESTED** — it needs an
  `OptView.hst` and none exists.
* **`d7_grade.py` has still never run on a real arm** (registration R4, open).
* **Toolchain: SHIPPED bought for `P1`. PATCHED NOT BOUGHT** — registered to `F-P` only, which is
  gated. **This is not a two-row DAFoam verdict and does not claim to be.**
