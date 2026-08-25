# D12-E′ — CHECKPOINT-ENVELOPE SECOND POINT — RESULTS

## 1. Verdict

**`NOT A RESULT`** for the registered two-point fit — **the branch this probe's own §4
registered in advance**, fired exactly as written.

Pre-registration frozen `612c3705`; the run was launched only after `git cat-file -e HEAD:…` passed.

## 2. What ran

One stage, `base`, `compute_totals`, np=1, `rc = 0`, `OOMKilled false`, 39 s wall,
**0.65 core-min**. Case, mesh, `daOptions` and run script **byte-identical to D12's**
(`d12e_run_script.py` md5 `a57676f6a1003d7d483cb2d799081512`); the only difference is
`endTime 0.05 → 0.10`, i.e. **5 steps → 10 steps**.

## 3. The measurement, and the fit that refused

| | n = 5 (D12) | n = 10 (this probe) |
|---|---|---|
| `maxrss` after primal, GiB | 0.794338 | 0.789463 |
| `maxrss` after adjoint, GiB | 1.326874 | 1.320686 |
| **adjoint RSS rise ΔR, GiB** | **0.532536** | **0.531223** |
| case-dir disk delta, B | 2,843,578 | 3,940,021 |

The fit, applied exactly as frozen in §3 of the pre-registration and **not chosen after
the fact**:

    per_step_GiB = (ΔR(10) − ΔR(5)) / 5 = (0.531223 − 0.532536) / 5 = −0.000262
    fixed_GiB    = ΔR(5) − 5 × per_step_GiB                          =  0.533848

**The slope is NEGATIVE.** The registered §4 branch — *"`per_step_GiB ≤ 0` →
`NOT A RESULT`, stated plainly rather than reported as 'zero per-step cost'"* — fires.

## 4. What is honestly known, and what is not

**Known, and it is worth more than the fit would have been:** `ΔR` at 10 steps is
`0.531223 GiB` against `0.532536 GiB` at 5 — a difference of **1.3 MiB, or 0.25 %**.
**Doubling the window did not measurably change the adjoint's resident memory.** The
0.53 GiB is therefore dominated by the **fixed** `dRdWTPC` term (317 colours), as §0
suspected.

**Not known, and not to be dressed up as known:**
- The difference (1.3 MiB) is **below the run-to-run RSS noise scale** — the primal
  figures alone differ by 4.9 MiB between the two runs. With **one run per point** the
  noise floor is **unmeasured**, so the per-step term is **UNRESOLVED**, not zero.
- A non-positive slope means either `reduceIO: True` is not holding per-step state in
  resident memory, **or** the allocator is not returning the difference to `ru_maxrss`.
  **This probe cannot tell those apart and does not pretend to.**
- Two points cannot detect curvature; linearity was assumed, never tested.

**The consequence that matters, and it is a retraction of an alarm this lane nearly
published:** the single-point extrapolation of `0.1065 GiB/step` projected `≈ 32 GiB` at
the tutorial's own 300-step window — **above this 30 GiB box**. **That projection is NOT
supported.** It was an upper bound with no lower bound beside it, and the second point
shows the fixed term dominating. **Equally, "the envelope is flat" is NOT established.**
D12's memory question is **open**, and §5 names the arm that would close it.

## 5. The arm that would settle it — proposed, not run, not costed as authorised

Two window lengths an order apart (e.g. **50 and 100 steps**) with **repeats at each**,
so the RSS noise floor is measured rather than assumed, and `reduceIO: False` as a second
arm to see the same state on disk. **Neither is run here, neither is pre-registered, and
proposing is not authorising.**

## 6. Cost

| | |
|---|---|
| predicted | **0.75 core-min** |
| actual gross | **0.6833 core-min** |
| ratio | **0.911×** |
| cap | 3.0 core-min; **`0.228×` of cap**, guard never fired |
| derived | **$0.000584 DERIVED, NOT MEASURED**, $0.0513/core-h c7a.4xlarge, reported-by-owner |
| waste | **0.000 core-min.** The run completed and returned the number it was registered to return; **a registered refusal is not waste** |

### 6.1 INSTRUMENT DEFECT, disclosed — the registered cap and the enforced cap were different numbers

**The pre-registration §6 registers a cap of `3.0` core-min. The launcher enforced
`6.0`** — `d12e_stage_and_run.sh:33` reads `CAP_CORE_MIN="${CAP_CORE_MIN:-6.0}"`,
inherited unchanged from D12's launcher, which this probe was derived from. The
substitution list that rewrote every path and the `endTime` assertion **did not include
the cap**, and no assertion checked it.

**It changed nothing here** — the run cost `0.6833 core-min`, `0.228×` of the registered
cap and `0.114×` of the enforced one, so neither guard was approached and no verdict,
number or gate is affected. **It is recorded because a cap that is not the cap you
registered is not a cap**, and the only reason it is harmless on this row is that the
run was cheap. **This is the same defect class the ansys-verification team recorded at
`C-51` item (8)** — a cap whose registered unit and enforced unit diverge — reached by a
different route: theirs was a unit conversion, this one is a copy-forward that no
assertion caught.

**Transferable fix, proposed and not adopted here** (changing a launcher idiom across a
family is not a lane's call, `CLAUDE.md` rule 9): a probe launcher should **assert its
own `CAP_CORE_MIN` against the value its pre-registration names**, the same way this
launcher already asserts `endTime 0.10` and the plant landing. Every derived-by-copy
launcher in this lane's eight probes is exposed to the same class; the other seven were
checked and their caps **do** match their pre-registrations.

Calibration row **C-69**.

## 7. Ungraded observations

At 10 steps, `obj = 0.2837585712362738` and
`d(obj)/d(shape) = [0.3463794565, 0.4382630472, 0.1919384682, −0.9765809719]` — both
differ from the 5-step run, as a different averaging window must. **Not graded, not
compared to anything, and not evidence**: this probe registered no capability gate.
