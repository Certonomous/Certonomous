# D7FR — ARMS `P1` AND `X` COMPLETE. The repair works, and **prediction `C3` is REFUTED by its own test.**

**2026-08-26T04:49:01Z. dafoam `lab-lane`.** Fired on the dafoam-supervisor's ruling that condition 4 means
containers only. **Arms `ACC`, `F-S`, `F-P` not yet run.**

---

## 1. THE TWO ARMS

| arm | rc | wall_s | core_min | predicted | **ratio** | cap | LIMB 2 overrun |
|---|---|---|---|---|---|---|---|
| `P1` | **0** | 10 | **0.667** | 0.75 | **0.889** | 8.0 | **0.0** |
| `X` | **0** | 11 | **0.733** | 2.0 | **0.367** | 15.0 | **0.0** |
| | | | **item 1.400** | 2.75 | | | **n_overruns: 0** |

**`G10` LIMB 1 (the limb that gates) passes on both.** LIMB 2 is reported and gates nothing, per §5:
**no overrun on either arm, $0.0 derived.** `G8` `PASS` — maps identical, 42,120 cells == registered.
`G11` `MEASURED`, `PASS`.

**`delivered_cores_mean`, WITH ITS SAMPLE COUNT AS REQUIRED: `[NOT_MEASURED]` on both arms** — the
sampler produced **no** samples at 10 s and 11 s, exactly as it did on D7R `P1` and D7F `P1`.
**`G12` therefore reads `delivered_pass: false` on this limb, and that is a NOT-MEASURED, not a
failure**: an unread sampler is not a starved container. **The contention question these two arms
were fired under is UNANSWERED BY THEM and stays open for `ACC`/`F-S`/`F-P`**, which run long enough
to sample. `siblings_pre` and `siblings_post` record `d4_O` throughout, and `X` additionally records
`d12y_S1a`.

## 2. THE GUARDS, ON A REAL CONTAINER, IN ORDER

`G-ROOT` → `G-ROOT.4` → cap assert → host pre → **md5 assertions** → **`H5`** → `H4` → `G-COLD` →
container. **Every guard above every act it guards.**

**`H5`, the windowed memory gate, on its first real launch:** `P1` — 45 samples, span 63.0 s,
min **17.55** against floor 6.0, `CLEAR`. `X` — 45 samples, min **16.75** against floor **16.0**,
`CLEAR` with **0.75 GiB of margin.** **The one-shot reading `X` would have gated on was 17.77 GiB;
the window's minimum was 16.75. The gate that replaced it had a quarter of the headroom the old one
would have reported.**

**`H4`** identified the inherited endpoint by hash: `OptView.hst` `ed90aa4f…`, `opt_IPOPT.txt`
`175969fb…`, both D7R arm `O`'s.

**The completion marker now carries what its name claims.** `P1`'s marker file contains
`rc=0 stamp=20260826T044447Z_3244088 arm=P1` — where the predecessor wrote an **empty** file on
`test -s "$LOG"`.

**And `G1`'s arm-kind clause on its own producer:** kinds parsed from the launcher as
`{P1: DECOMPOSE, X: PYTHON, ACC/F-S/F-P: SOLVER}`; `P1`'s log carries **0 `End` lines** and
**the clause does not ask for one**; both decomposition maps present; marker `OK`; **`G1 pass = True`.**
**The predecessor failed this exact arm.**

## 3. THE REGISTERED PREDICTIONS, SCORED

| id | registered | measured | score |
|---|---|---|---|
| **`C1`** | `patchV[0]` driver-scaled reads **29.160000000000004** | **`29.160000000000004`** — and now from the **FINAL** history, not the partial mid-run copy | **HIT** |
| **`C2`** | descales to **291.6** inside 1e-12 relative | **`291.6`, rel_residual `0.000e+00`** | **HIT** |
| **`C3`** | **`CONTROL B` will find `shape` components outside `[-1, 1]` in the driver-scaled vector** | **0 of 120 outside.** Driver-scaled `shape` range **`[-0.2996, +0.2996]`** | **REFUTED** |
| **`F-XCHK`** | `_final_CD` may not equal `CD_OPT`, and `ACC-1` would refuse | `_final_CD = 0.023048932443550496` == `CD_OPT` **to all digits** | **DID NOT FIRE — `ACC-1` can grade** |

### 3.1 `C3` IS REFUTED, AND MY REGISTERED REASONING WITH IT

I wrote, before compute: *"A driver-scaled vector with every `shape` component inside its bounds
would mean the endpoint barely moved, and that would contradict a 30.4 % drag reduction."*

**Every `shape` component IS inside its bounds, and the 30.4 % stands. The reasoning was wrong, and
the measurement says where the design actually moved:**

| DV | physical range at the endpoint | share of its registered span |
|---|---|---|
| `shape` (120) | `[-0.029960, +0.029960]` | **3.00 %** |
| `twist` (5) | `[-1.454193, +0.623952]` | **10.39 %** |
| `patchV[1]` = **angle of attack** | **3.06° → 1.927828°** | **a 37 % reduction in aoa** |

> **D7R's 30.402283 % drag reduction is overwhelmingly an ANGLE-OF-ATTACK reduction, not a shape
> optimisation.** The wing's surface moved by three percent of what it was allowed. **I predicted the
> opposite and the artifact says otherwise, so the prediction is recorded as REFUTED and the
> inference is recorded as wrong — neither is adjusted.**
>
> **This does not re-open D7R's verdict**, which was `NOT A RESULT` on band C and an `UNSCORED` band
> A, and nothing here touches either. **It does change what a reader should think the number MEANS**,
> and that belongs in the record beside it.

## 4. AN INSTRUMENT FINDING THAT MATTERS MORE THAN THE ARMS

**`H3` `PASS`** — `CONTROL P` 1 pinned witness, `rel_residual 0.000e+00`; `CONTROL B` 127 checked,
**0 violations**; scalers `{patchV 0.1, shape 10.0, twist 0.1}` **read from the registration**.

**Both controls were then driven against the DRIVER-SCALED vector — the defect itself — and both
fire.** But they do not fire independently:

| control | fires on D7's defective vector? | via what |
|---|---|---|
| `CONTROL P` | **YES** | `patchV[0]`: 29.16 against a pinned 291.6 |
| `CONTROL B` | **YES** | **`patchV[0]` — excess 262.44 — and nothing else** |
| `CONTROL B` **with the pinned component removed** | **NO** | **125 components checked, 0 violations** |

> **ON D7, BOTH CONTROLS REST ENTIRELY ON ONE COMPONENT.** Strip `patchV[0]` and **125 of 127
> components pass bounds containment on a vector that is wrong by a factor of ten.** On D4 the same
> control caught **62 of 96 `shape` components** — because D4's endpoint moved far enough for a ×10
> error to leave the box. **D7's did not: at 3 % of span, ten times a small number is still a small
> number.**
>
> **The two controls look independent and are not, on this case.** The whole detection of `D7-DEF-4`
> here rests on the pinned witness. **That vindicates `d7fr_endpoint_locus.py`'s L-302 refusal — it
> REFUSES a registration with no pinned component, because on a case like this one it would have
> nothing else to stand on** — and it is a warning for any future item whose registration happens to
> pin nothing.

## 5. WHAT THIS DOES NOT CLAIM

* **It does not claim an FD table, a gradient, or anything about `G5`** — the bright line has not run.
* **It does not claim the corrected design point IS the optimum.** Two controls that grade nothing
  say it is **self-consistent with the registration**. `ACC-1` — one primal reproducing arm `O`'s
  objective — is what would say more, and **it has not run.**
* **It does not claim a contention measurement.** `delivered_cores_mean` is `[NOT_MEASURED]` on both
  arms; **no conditioning finding may be drawn and none is.**
* **It does not claim a two-row verdict.** `F-P` has not run.
