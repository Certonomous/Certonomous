# M6I RUNG 9 — THE NON-ORTHOGONAL CORRECTION. PRE-REGISTRATION.

**Item:** `M6I_R9_NONORTHCORR`
**Team:** cfd. **Lane:** `lab-lane`. **Supervisor:** `cfd-supervisor`.
**Predecessors:** R5 `27a491e77`, R6 `49c4d39a4`, R7 `1d9433a84`+`0bfe11259` — all
`NOT A RESULT`; R8 `cf87f2182` — **completed**, `GATE FAIL`, D1/D2/D3 all failed.
**The parking record `M6I_PARKING_RECORD.md` is superseded on one point only:** its claim
that the numerics rung was spent. **Every elimination in it stands.**

## 🔴 STATUS: **DRAFT. NOT FROZEN. NO SOLVER MAY RUN UNDER THIS DOCUMENT.**
Pre-compute condition, checked by this lane: **`verification/runs/M6I_runs/L3_NOC/` does not
exist.** Launch is **through the runner as a queue entry**, never by hand; the entry is
drafted into `verification/queue/cfd/held/`, **never** into `verification/queue/cfd/`, which
is a live launch path polled by a daemon.

---

## 🔴 §0 — THE LADDER'S REMAINING LENGTH, WRITTEN IN SO THE PARKING DECISION IS BOUNDED

- **R9 (this document): `nNonOrthogonalCorrectors`.** If §4's limb fires → alive, L2 confirms.
- **R10, IF AND ONLY IF R9's LIMB DOES NOT FIRE: the `transonic` formulation itself.**
  `transonic yes` has never been switched on this family — measured, §1. That is the last
  untouched formulation switch.
- **AFTER R10 THE NUMERICS RUNG IS GENUINELY SPENT AND M6I PARKS**, whatever R10 returns.
  **No R11. No variant. By anyone.** The ladder's remaining length is two runs, and this
  clause is what makes that a fact rather than an intention.

---

## 1. WHY THIS RUNG — TWO DICTIONARY ENTRIES NEVER TOUCHED IN EIGHT CASES

Measured by this lane across every case in the family:

| case | `div(phid,p)` | `transonic` | `nNonOrthCorr` | snGrad limiter |
|---|---|---|---|---|
| L3 / L3_TVD / L3_NORAMP | `Gauss upwind` | **yes** | **2** | **limited corrected 0.33** |
| L2 | `Gauss upwind` | **yes** | **2** | **limited corrected 0.33** |
| L2_PHIDP | `Gauss limitedLinear 1` | **yes** | **2** | **limited corrected 0.33** |
| L2_VANLEER / L2_PMIN | `Gauss vanLeer` | **yes** | **2** | **limited corrected 0.33** |
| L2_SST | `Gauss upwind` | **yes** | **2** | **limited corrected 0.33** |

**`div(phid,p)` moved three times and the closure once. `transonic`, `nNonOrthogonalCorrectors`
and the snGrad limiter never moved at all — on a mesh whose maximum non-orthogonality is
87.66°.** That is the same shape this team reported against CRM (twenty attempts that never
touched `consistent`, `transonic` or `nNonOrthCorr`) and did not catch in its own family.

---

## 2. 🔴 THE CORRECTOR COUNT, DERIVED FROM THE MESH AND THE SOURCE — NOT FROM PREFERENCE

**(a) What the limiter actually does.** From `limitedSnGrad.C:60-71`, read from the installed
tree:
`limiter = min( c·|snGrad_orth| / ((1−c)·|corr|), 1 )`.
At the family's `c = 0.33` the applied correction is capped at
**`c/(1−c) = 0.4925 × the orthogonal part`.** (The header documents `c = 0.5` as the setting
where "the non-orthogonal component does not exceed the orthogonal component"; **0.33 caps it
at roughly half of that.**)

**(b) What the correction is.** From `basicFvGeometryScheme.C:341`,
`corrVecs = unitArea − delta·nonOrthDeltaCoeffs`, with
`nonOrthDeltaCoeffs = 1/max(unitArea & delta, 0.05·|delta|)` (`:266`). Writing
`delta = |d|(cosθ n̂ + sinθ t̂)` gives **`|corrVecs| = tan θ` exactly**, until the `0.05` floor
saturates at **θ = 87.13°**.

**(c) The mesh, measured — not taken from `checkMesh`'s two summary numbers.** A coded
functionObject over L3's own geometry, **validated against a known value: it returns
max = 87.66202996°, which is `checkMesh`'s 87.662 to five decimals.** 44,832 internal faces:

| band | faces | % |
|---|---:|---:|
| 0 – 26.22° | 25,856 | **57.67 %** |
| 26.22 – 40° | 7,550 | 16.84 % |
| 40 – 60° | 5,664 | 12.63 % |
| 60 – 80° | 4,032 | 8.99 % |
| 80 – 85° | 1,434 | 3.20 % |
| 85 – 90° | 296 | **0.66 %** — past the `0.05` floor, where the decomposition itself saturates |

**(d) The number.** The cap binds where `tan θ · G > 0.4925`, with `G` the ratio of tangential
to normal gradient magnitude. **At `G = 1` the threshold is `atan(0.4925) = 26.22°`, and
42.33 % of internal faces are clipped.** Each corrector then removes at most a fraction
`0.4925` of the remaining non-orthogonal error, so the residual after `n` correctors is
`0.4925ⁿ`:

| n | residual | reduction vs the family's n = 2 |
|---|---:|---:|
| **2 (the family, all eight cases)** | **24.26 %** | — |
| 3 | 11.95 % | 2.0× |
| 4 | 5.88 % | 4.1× |
| **5 — REGISTERED** | **2.90 %** | **8.4×** |
| 6 | 1.43 % | 17× |

**REGISTERED: `nNonOrthogonalCorrectors 2 → 5`** — the smallest value in the supervisor's
4–6 range whose residual falls **below 3 %**. n = 4 (5.88 %) and n = 6 (1.43 %) are tabled
above so the choice can be overruled with the numbers in view rather than re-argued.

🔴 **`G = 1` IS AN ASSUMPTION, NOT A MEASUREMENT, AND IT IS LOAD-BEARING FOR THE 26.22° AND
THE 42.33 %.** In a boundary layer normal gradients dominate (`G < 1`), which would raise the
threshold and lower the clipped fraction. **The measured quantity is the angle distribution;
the clipped fraction is an estimate built on it.** The corrector table does not depend on
`G` — only on the cap — and the registered change does not depend on the clipped fraction.

---

## 3. THE ONE CHANGE, AND THE LEVEL

**`system/fvSolution`: `nNonOrthogonalCorrectors 2;` → `nNonOrthogonalCorrectors 5;`**
**`system/fvSolution.startup`: the same**, so the ramp and the graded stage agree.
**Nothing else moves** — grid, `limited corrected 0.33`, `transonic yes`, every `div` scheme,
every relaxation factor, `pMinFactor`, `pMaxFactor`, `SpalartAllmaras`, `fvOptions`,
`writeInterval`, `purgeWrite`, `endTime 3000`, `decomposeParDict`.
**Also added:** the `clipCount` instrument (verdict-inert, carried from R7).

**LEVEL: L3 first** (15,360 cells, minutes), **then L2 only if §4's limb fires.**
Under-corrected non-orthogonality is a **discretisation** effect, visible at any resolution.

---

## 4. 🔴 THE DIAGNOSTIC LIMB — AND A CORRECTION TO THE ONE THAT WAS ASKED FOR

The dispatch asked for limbs on **both** the raw trace's steepest gradient **and** the share
of recompression carried by the largest interval. **The share limb is NOT registered, because
it is resolution-confounded in the direction that would make a coarse grid look shock-like.**
Measured on the raw single-row upper-surface trace at η ≈ 0.65, aft of x/c 0.15:

| | cells aft of 0.15 | total rise | **largest interval** | **share** | **steepest gradient** |
|---|---:|---:|---:|---:|---:|
| **L3** | **4** | +0.1926 | +0.1191 | **61.9 %** | **+1.1222** |
| L2 | 8 | +0.3725 | +0.1211 | 32.5 % | +1.4800 |
| L1 | 17 | +0.5084 | +0.0926 | 18.2 % | +1.5800 |
| AGARD | 15 | +0.8890 | +0.4240 | 47.7 % | **+8.4600** |

**The share falls 61.9 → 32.5 → 18.2 % purely because the cell count rises 4 → 8 → 17.
L3's 61.9 % already exceeds the experiment's 47.7 %, and there is no shock in L3.** Registering
that limb would hand a coarse grid a pass. It is rejected and the rejection is recorded here.

**REGISTERED LIMB — L3's raw-trace steepest `dCp/d(x/c)` aft of x/c 0.15 must reach
`≥ +1.8328`.** Derivation, from measured noise in this family rather than from choice:
- the **ramp** change (L3_NORAMP vs L3) moved it **+0.0022** — the floor of "no effect";
- the **scheme** change (L3_TVD vs L3) moved it **−0.3553**, the largest movement any prior
  registered change produced on L3, and in the **wrong** direction;
- **threshold = 1.1222 + 2 × 0.3553 = 1.8328**, i.e. more than twice the largest prior effect,
  upward.

**KILL-ONLY, NEVER PROMOTING**, exactly as R5's limbs were: failing it makes the rung dead;
passing it does not make anything a `PASS`. §5 is the only cure gate.

🔴 **AND L3's CEILING IS REGISTERED WITH IT, BECAUSE IT BOUNDS WHAT THIS RUN CAN SHOW.**
With 4 cells over 0.481c the mean spacing is **0.120c**. **Even a perfect shock carrying the
experiment's entire +0.4240 across one L3 cell could only read `+3.53`, against the
experiment's +8.46. L3 cannot resolve a shock.** The registered 1.8328 sits inside that
ceiling, so the limb asks for something achievable — but **a pass on L3 means "correctors
sharpen the recompression", never "the shock is recovered".**

---

## 5. THE CURE GATE — TRANSCRIBED UNCHANGED, RE-INVENTED NOWHERE

From R5 §4.2, unchanged through R6, R7 and R8: **D1** `cfd_cp_rise_at_shock` at η 0.65
**≥ 0.1401**; **D2** Cp rise across the experiment's own shock interval at η 0.65 **≥ 0.0880**;
**D3** `x_shock_cfd` must leave **0.8851** for a strictly more forward admissible midpoint.
**S1** ≥ 0.212 / ≥ 0.320; **S2** < 0.85; **B1** ≤ 0.050 on 12 rows; **B2** ≤ Δ_local.

🔴 **D2 AND D3 ARE NOW KNOWN TO MISLOCATE AND THAT DISCLOSURE TRAVELS WITH THEM.** The
detector resamples onto the experimental orifices, whose intervals widen aft (**0.0501c at
0.4752 against 0.0701c at 0.8851**); on a smoothly rising curve the argmax picks **the widest
aft interval, not the steepest feature**. That is why `x_shock` reads 0.8851 while the raw
maximum rise sits at x/c 0.602–0.671. **No reader may take `x_shock` from this comparator as a
physical shock position** (parking addendum `801391c00`, Defect B). The gate is not edited —
it is frozen — but it is read with this disclosure attached, which is why §4's limb exists.

---

## 6. COST (rule 12)

Measured basis: **L3 cost 5.87 core-minutes** — 0.40 (200-iteration ramp, 6 s) + 5.47
(2,800 iterations, 82 s) at 4 ranks.
- `nNonOrthogonalCorrectors 2 → 5` takes the pressure solves per outer iteration from **3 to
  6**. The pressure solve's share of the step is **not measured on this case**, so the
  prediction is stated with that gap named.
- **Predicted: 9.4 core-minutes** (×1.6 on the measured 5.87).
- **Cap: 35.2 core-minutes** — 3× a ×2.0 worst case, deliberately not 3× the prediction, for
  the reason R6 §8 records: a run that is merely slow must not be graded `NOT A RESULT` on
  cost. Nothing is killed on spend or clock (Sanaa directive #17).
- `cost_basis`: **MEASURED** in core-minutes from the run's own logs; dollars **DERIVED, NOT
  MEASURED** at $0.0513/core-h → ≈ $0.008.
- Family to date: **121.94 core-minutes**, 11.1 % of one graded level (L1 = 1,098).

---

## 7. PRECONDITIONS, CONTROLS, AND WHAT THIS DOES NOT DO

Graded by **`scripts/grade_m6_agard_cp.py`, blob `e9d5c04b` at `4c931d97c`**, unchanged,
**hash-verified in the same shell invocation as the run**; its planted control must print
`reader_saw_the_plant: true` or the result is `NOT A RESULT`. The strict completion rule
applies in full **including the age guard**. The launcher's model assert (`6cc90e0b`) accepts
`SpalartAllmaras`, which is what this rung runs.

**DOES NOT:** change the snGrad limiter, `transonic`, any `div` scheme, the closure, the
grid, or any relaxation factor; register R10 (§0 makes it a *consequence*); register the
share-of-recompression limb (§4 rejects it); claim `G = 1` is measured (§2d); or claim L3 can
resolve a shock (§4).

*Drafted by a cfd `lab-lane`, 2026-09-13. NOT FROZEN — NOT COMMITTED — NO RUN AUTHORISED.
Alters no existing gate, threshold, band, cap or label. No agent's message is Sanaa's
consent. Submissions parked.*
