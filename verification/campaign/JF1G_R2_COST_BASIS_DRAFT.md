# JF1G-R2 — COST BASIS FOR A SUCCESSOR REGISTRATION — **DRAFT, NOT FROZEN, NOT LAUNCHED**

> **THIS IS NOT A PRE-REGISTRATION AND IT MUST NOT BE TREATED AS ONE.** It is
> deliberately **not** named `*_PREREGISTRATION.md`, so that no freeze checker,
> launcher or audit sweep mistakes it for a frozen document. **No gate, threshold,
> cap or label in this file is in force. Nothing may be launched against it.**
> It carries one thing: the **measured** cost basis that a successor registration
> would need, recorded while the measurement is fresh.

**Why it exists.** `cfd-supervisor` directed that the lawful route to a larger C2
allowance is a **new** pre-registration carrying the now-measured basis, and that the
draft be prepared but **not launched**. This is that draft.

**Why it cannot be frozen yet.** The disposition of Gate G1 of `038f4bca` — whose
`Mesh OK` clause rejects C3 on an aspect ratio the lab's own `MESH_STANDARD.md` §3.3
calls *"advisory … never a lone rejection"* — is **reserved and unruled**
(`verification/campaign/JF1G_MESH_GATE_FINDING.md` §5). **A successor cannot be
frozen while the clause it would replace is still before the chief**, and this lane
has been instructed not to reissue, not to amend and not to run C3. **Freezing this
draft is blocked on that ruling, not on any measurement.**

---

## 1. WHAT IS NOW MEASURED THAT WAS NOT MEASURED AT `038f4bca`

`038f4bca` §8 priced the ladder from a **single** 40k-cell case, at a unit rate of
`4.0798e-06` core-s per cell per iteration, applied **linearly** to every level.
**That linear model is refuted.** Landed as calibration row
`C-20260901T163701.774550Z-1b8633ba`:

| level | cells | core-s per cell per iteration | source |
|---|---|---|---|
| C1 | 39,984 | **4.0798e-06** | completed run, 1,305 wall s / 8,000 it / 1 rank |
| C2 | 89,964 | **7.7867e-06** | mid-run `ExecutionTime`, same box, same three concurrent solvers |

**1.909× worse per cell at 2.25× the cells.** Contention is **not** the attribution —
both readings were taken under the same live load. Cost therefore grows as roughly
the **4.3 power of `r`** on this 2-D family, not `r²`.

**Realised consequence, not a forecast:** C2 Pass-0's registered estimate of 48.9
core-min projects to **93.4**, against a frozen cap of **80.0**. The cap stands and
is not raised; C2 stops when it strikes it.

## 2. THE COST TABLE A SUCCESSOR WOULD CARRY

Built from the **measured** per-level rates above, with the C3 and C4 rates
**extrapolated on the measured exponent and labelled as extrapolation, not
measurement.** A successor must re-derive C3's rate from C3's own completed run
before pricing C4.

| item | cells | `endTime` | rate basis | estimate | proposed cap |
|---|---|---|---|---|---|
| Pass 0 C1 | 39,984 | 8,000 | **measured** | 21.8 | 40 |
| Pass 0 C2 | 89,964 | 8,000 | **measured** | **93.4** | **130** |
| Pass 0 C3 | 202,180 | 8,000 | *extrapolated* | ~350 | 480 |
| Pass 1 C1 | 39,984 | 30,000 | **measured** | 81.6 | 110 |
| Pass 1 C2 | 89,964 | 30,000 | **measured** | **350.4** | **470** |
| Pass 1 C3 | 202,180 | 30,000 | *extrapolated* | ~1,310 | 1,760 |

**Every extrapolated figure is marked as such and none may be quoted as measured.**
Dollars at the recorded `$0.0513/core-h` are **derived, not measured** — this box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

## 3. WHAT A SUCCESSOR WOULD ALSO HAVE TO CARRY, AND WHICH IS NOT COSTED HERE

Recorded so the next author does not have to rediscover it:

1. **The mesh gate**, aligned to `MESH_STANDARD.md` §3.3 and §11 — gate on
   non-orthogonality and skewness; **report** aspect ratio and cell-volume ratio.
   **Blocked on the unruled question. Not drafted here.**
2. **`--normal-smooth = 500·s²`** as a similarity clause. Derived from the
   `sqrt(passes)` diffusion length **before** it was measured; the sweep's minimum
   lands on the predicted value at every level, and under it max non-orthogonality
   reads **57.53 / 58.62 / 58.89** across a 5× cell-count range instead of drifting
   57.53 → 67.64 → 75.14. C1 is unchanged (`500·1² = 500`), so C1 stays
   bit-identical to the grid the five 2026-08-31 sweep rows ran on.
3. **The honest iterative floor.** Two runs of the same case at the same settings
   from different initial conditions settle **2.23e-05** apart in `CL`, while each
   run's apparent drift is **~3e-07** — the initial-condition sensitivity is **~70×**
   the drift a tightness rule reads. A successor's tightness clause should read the
   **floor**, not the drift.
4. **The similarity clauses of `038f4bca` §2.2 are measured PASSING** on the emitted
   meshes and would carry over unchanged: ratios 1.4966–1.5017, total cell ratio
   2.2500 / 2.2473 against `r²`, growth identity `g_fine^r = g_coarse` to 3e-4.

---

**SUBMISSIONS PARKED.** Nothing in or derived from this draft is sent, filed,
uploaded, posted or registered outside this box. **And nothing is launched against
it: it is a draft, and the freeze it anticipates is blocked on a ruling that is not
this lane's to make.**
