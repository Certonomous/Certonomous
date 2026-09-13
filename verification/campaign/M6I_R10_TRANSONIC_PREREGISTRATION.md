# M6I RUNG 10 — THE `transonic` FORMULATION. **THE LAST RUNG.**

**Item:** `M6I_R10_TRANSONIC`
**Team:** cfd. **Lane:** `lab-lane`. **Supervisor:** `cfd-supervisor`.
**Predecessors:** R5 `27a491e77`, R6 `49c4d39a4`, R7 `1d9433a84`+`0bfe11259` — `NOT A RESULT`;
R8 `cf87f2182` — completed, `GATE FAIL`, D1/D2/D3 failed; R9 `ed1f053ce` — completed,
`GATE FAIL`, **limb did not fire**.

## 🔴 STATUS: **DRAFT. NOT FROZEN. NO SOLVER MAY RUN UNDER THIS DOCUMENT.**
Pre-compute condition, checked by this lane: **`verification/runs/M6I_runs/L3_TRNS/` does not
exist.** Launch is **through the runner**, entry drafted into `verification/queue/cfd/held/`,
fail-closed, **never** into `verification/queue/cfd/`.

---

## 🔴 §0 — THIS IS THE END, AND IT CANNOT BE RELITIGATED

**WHATEVER R10 RETURNS — limb fired, limb silent, divergence, or refusal — THE NUMERICS RUNG
IS SPENT, THE M6I MECHANISM LADDER IS EXHAUSTED, AND M6I PARKS.**
**No R11. No variant. Not by this lane, not by a successor, not by the supervisor.**
The parking record's ADDENDUM 2 is **drafted alongside this document and before the run**, at
`verification/campaign/M6I_PARKING_RECORD_ADDENDUM2_DRAFT.md`, so it lands the moment the limb
is read. *A parking record written after the fact reads as an excuse; one written before reads
as a plan.*

---

## 1. WHY THE FORMULATION — IT IS WHAT REMAINS

R9 measured the corrector half of the untouched pair and closed it: **`nNonOrthogonalCorrectors`
2 → 5 moved the raw-trace steepest gradient by −0.0000 against a registered threshold of
+1.8328**, with the change **verified in effect at six pressure solves per outer iteration
against three**, at 2.65× the cost. Span-averaged RMS 0.3328 → 0.3327; D1 0.0875 → 0.0876.

**`transonic` is the last dictionary entry this family has never varied.** It read `yes` in all
eight cases while `div(phid,p)` moved three times and the closure once.

---

## 2. 🔴 WHAT `transonic no` ACTUALLY CHANGES — FOUR CONSEQUENCES, READ FROM SOURCE

**This is not one word. Read from `applications/solvers/compressible/rhoSimpleFoam/pEqn.H` in
the installed tree, both branches:**

| # | under `transonic yes` (the family, all eight cases) | under `transonic no` (R10) |
|---|---|---|
| 1 | pEqn carries **`fvm::div(phid, p)`**, with `phid = (interp(psi)/interp(rho))·phiHbyA` | **the term is ABSENT from the equation entirely** |
| 2 | **`pEqn.relax()` is called**, under the source's own comment *"Relax the pressure equation to ensure diagonal-dominance"* | **`pEqn.relax()` is NOT called** |
| 3 | no `adjustPhi` | **`closedVolume = adjustPhi(phiHbyA, U, p)` IS called** — a global flux adjustment |
| 4 | `phiHbyA -= interp(psi·p)·phiHbyA/interp(rho)` | **that subtraction does not happen** |

🔴 **CONSEQUENCE 1 MEANS `div(phid,p) Gauss upwind` BECOMES DEAD CONFIGURATION.** The term
R5, R6 and R7 spent 42.54 core-minutes moving **ceases to exist in the equation**. The
`fvSchemes` entry stays on disk, unread. **"Same schemes" would imply more sameness than
exists, and this document says so rather than letting the phrase carry it.**

🔴 **CONSEQUENCE 2 MAKES THE LAUNCHER'S OWN ASSERT MESSAGE MISLEADING, AND IT IS NOT CHANGED.**
`launch_m6i_v3.sh` asserts `relaxationFactors.equations.p 1` with the failure message
*"pEqn.H:36 needs it for diagonal dominance"*. Under `transonic no` **`pEqn.relax()` is never
called, so that entry is inert for the pressure equation.** The assert still passes and its
stated reason no longer applies. **The launcher is left alone** — it is a measurement script
and changing it is the supervisor's to read as a diff — and the discrepancy is disclosed here
instead.

---

## 3. THE ONE CHANGE, AND THE LEVEL

**`system/fvSolution`: `transonic       yes;` → `transonic       no;`**
**`system/fvSolution.startup`: the same**, so the ramp and the graded stage agree.
**Nothing else moves** — grid, `nNonOrthogonalCorrectors 2` (**R9's 5 is NOT carried forward:
it was a numerics-rung change that moved nothing, and carrying it would confound the
formulation rung with a closed one**), `limited corrected 0.33`, every `div` scheme including
the now-dead `div(phid,p)`, every relaxation factor, `pMinFactor 0.2`, `pMaxFactor 2.0`,
`SpalartAllmaras`, `fvOptions`, `writeInterval 200`, `purgeWrite 2`, `endTime 3000`,
`decomposeParDict`. **Plus** the verdict-inert `clipCount` instrument.

**Expected diff against L3, recomputed from that list:** `constant/` **byte-identical**;
`system/` **3 differing files** (`fvSolution`, `fvSolution.startup`, `controlDict`) carrying
**3 changed/added lines** (two `transonic`, one `clipCount` include); **1 new file**
(`system/clipCount.fo`). **Nothing launches if the staged case does not match.**

**LEVEL: L3 first** (15,360 cells, minutes). **L2 only if §4's limb fires.**

---

## 4. THE LIMB, AND THE CEILING THAT BOUNDS IT

**REGISTERED: L3's raw-trace steepest `dCp/d(x/c)` aft of x/c 0.15, on the single-row
upper-surface trace at η ≈ 0.65, must reach `≥ +1.8328`.**

**The threshold is unchanged from R9 and here is why that is correct rather than lazy:** it is
`1.1222 + 2 × 0.3553`, L3's measured baseline plus twice the largest movement any prior
registered change produced (L3_TVD, **−0.3553**, wrong direction; the ramp, **+0.0022**).
**R9 added a third data point — `−0.0000` — which does not enlarge the noise floor, so the
construction returns the same number.**

**KILL-ONLY, NEVER PROMOTING.** §5 is the only cure gate.

🔴 **THE CEILING CLAUSE, CARRIED FORWARD FROM R9 BECAUSE IT IS WHAT STOPPED R9's RESULT BEING
OVER-READ.** L3 has **4 cells over 0.481c = 0.120c spacing. Even a perfect shock carrying the
experiment's entire +0.4240 across one L3 cell reads +3.53 against the experiment's +8.46.
L3 CANNOT RESOLVE A SHOCK.** The registered +1.8328 sits inside that ceiling, so the limb is
answerable — but **a pass means "the formulation sharpens the recompression" and NEVER "the
shock is recovered".**

---

## 5. THE CURE GATE — TRANSCRIBED UNCHANGED, WITH ITS DISCLOSURE ATTACHED

From R5 §4.2, unchanged through R6–R9: **D1** ≥ **0.1401**; **D2** ≥ **0.0880**; **D3**
`x_shock_cfd` must leave **0.8851** for a strictly more forward admissible midpoint.
**S1** ≥ 0.212 / ≥ 0.320; **S2** < 0.85; **B1** ≤ 0.050 on 12 rows; **B2** ≤ Δ_local.

🔴 **D2 AND D3 MISLOCATE AND THE DISCLOSURE TRAVELS WITH THEM.** The comparator resamples onto
experimental orifices whose intervals widen aft — **0.0501c at x/c 0.4752 against 0.0701c at
0.8851** — so its argmax picks **the widest aft interval, not the steepest feature**. That is
why `x_shock` reads 0.8851 while the real maximum rise sits at **x/c 0.602–0.671**. **No reader
may take `x_shock` from this comparator as a physical shock position** (parking addendum
`801391c00`, Defect B). The gate is frozen and is not edited; §4 exists because of this.

---

## 6. 🔴 BOTH MECHANISMS, NAMED BEFORE THE RUN, POINTING OPPOSITE WAYS

**FOR:** `div(phid,p)` is discretised **`Gauss upwind` — first order — at every level of this
family**, and consequence 1 removes it from the equation outright. Removing a first-order
implicit term could reduce smearing of the recompression.

**AGAINST, and this lane judges it the more likely:** the `transonic` switch **exists** for
M∞ = 0.84 flow. Turning it off removes the implicit compressibility coupling from the pressure
equation and drops `pEqn.relax()` (consequence 2). **`transonic no` at M∞ = 0.8395 is expected
to be worse, or to diverge.**

**The rung is run because "we never tried it" is not a measurement, not because it is expected
to work.** If it diverges, that is a result: the last untouched switch was untouched for a
reason, and §0 parks the family either way.

---

## 7. COST (rule 12)

Measured basis: **L3 cost 5.87 core-minutes** (0.40 ramp + 5.47, 3,000 iterations, 4 ranks).
`transonic no` assembles a **simpler** pressure equation (one fewer implicit term) but adds
`adjustPhi`'s global reduction.
- **Predicted: 5.9 core-minutes** — the measured L3 rate, unchanged.
- **Cap: 46.6 core-minutes** — **3 × R9's MEASURED 15.53**, the worst factor this family has
  ever recorded (×2.65 where the estimate said ×1.6). **The cap is set from a measured worst
  case, not from this prediction**, which is the only reason R9's miss cost nothing.
  A crossing grades the row `NOT A RESULT`; the cap is never raised; nothing is killed on
  spend or clock (Sanaa directive #17).
- `cost_basis`: **MEASURED** in core-minutes from the run's own logs; dollars **DERIVED, NOT
  MEASURED** at $0.0513/core-h → ≈ $0.005.
- Family R5–R9 to date: **137.47 core-minutes = 12.5 % of one graded level** (L1 = 1,098).

---

## 8. PRECONDITIONS, CONTROLS, AND WHAT THIS DOES NOT DO

Graded by **`scripts/grade_m6_agard_cp.py`, blob `e9d5c04b` at `4c931d97c`**, unchanged,
**hash-verified in the same shell invocation as the run**; its planted control must print
`reader_saw_the_plant: true` or the result is `NOT A RESULT`. Strict completion rule in full
**including the age guard**. The queue entry registers **`memory_footprint_gb` 0.5**,
transcribed from the frozen R1 memory table (L3, 15,360 cells, **declared not measured**) —
**R9's entry omitted it and the runner refused it at gate B; that is not repeated.**

**DOES NOT:** carry R9's 5 correctors forward (§3); change any `div` scheme, the limiter, the
closure, the grid, `pMinFactor`/`pMaxFactor`, or any relaxation factor; edit the launcher
(§2, consequence 2); register anything beyond this rung (§0); or claim L3 can resolve a shock
(§4).

*Drafted by a cfd `lab-lane`, 2026-09-13. NOT FROZEN — NOT COMMITTED — NO RUN AUTHORISED.
Alters no existing gate, threshold, band, cap or label. No agent's message is Sanaa's consent.
Submissions parked.*
