# M6I — PARKING RECORD. THE MECHANISM LADDER IS EXHAUSTED.

**Drafted by a cfd `lab-lane`, 2026-09-13, under `M6I_R8_SST_PREREGISTRATION.md` §9, frozen
at `cf87f2182` BEFORE the run that sent us here.** Not committed. No gate, threshold, band,
cap or label is altered by this document.

**Trigger:** R8 (`L2_SST`) **completed** — `rc = 0`, `End`, `Time = 5000 == endTime`, 4,800
`ExecutionTime` entries, age guard passed, planted control fired — and then **failed D1 and
D2**. Frozen §7: *"A completed run that fails D1 and D2 also spends the rung"* and parks by
the other road. **§0 binds: no fourth rung, no variant, and a near-miss is not a reason to
continue.**

---

## 1. THE GRADED RESULT STANDS, AND IT LEADS

**`L1` — `GATE FAIL`**, `verification/runs/M6I_runs/L1/m6i_grade_L1.json`, graded by the
frozen comparator `scripts/grade_m6_agard_cp.py` (blob `e9d5c04b` at `4c931d97c`) against
`A3_M6_AGARD_CP_VALIDATION_PREREGISTRATION.md`. Planted control fired: RMS moved **0.0984**
against a required **0.0617**.

- **12 of 12 B1 rows fall monotonically** L3_TVD → L2 → L1 on `rms_dev`.
- **η 0.65-lower is INSIDE the band at RMS 0.0494** — the only row in this family ever to land.
- Span-averaged RMS **0.3323 → 0.2045 → 0.1423**; span-averaged bias **0.1344 → 0.0531 →
  0.0248**, falling *faster* than the RMS (ratios 0.395/0.467 against 0.615/0.696).
- **That bias behaviour is the finding that killed the reference-pressure hypothesis:** the
  additive term of `dev = a + b·Cp_exp` stays at |a| ≤ 0.032 and does not scale, while the
  slope halves from −0.530 to −0.221. A resolution signature, not a datum error.

**This is a defensible external-validation verdict against AGARD AR-138 TEST 2308 and it is
what the family produced. It is not withdrawn by anything below.**

---

## 2. WHAT WAS RULED OUT, EACH WITH ITS MEASUREMENT

| candidate | verdict | the measurement |
|---|---|---|
| **Resolution** | not the limiter | shock rise ×1.528 per grid halving ⇒ **8.0 × 10¹¹ cells** to reach the experiment. A *reductio*. |
| **Reference pressure / dynamic pressure** | **dead** | `a` ≤ 0.032 and non-scaling while `b` halves; bias falls faster than RMS. |
| **Mesh — shock window** | **dead** | **Zero** >70° faces in the x/c 0.30–0.70 upper window at **all six** graded stations. |
| **Mesh — tip cap** | **dead, anti-correlated** | 81.0 % of the L2 grid's >70° faces at η ≥ 0.99 where failure density is **4.96 %**; at η 0.20–0.65 the mesh is clean and density is **27.63 %**. **5.6× less dense where the mesh is worst.** Spearman ρ = **−0.800** over nine bands. |
| **Pressure discretisation** | **spent** | Three configurations, three divergences: `limitedLinear` (R5), `vanLeer` + engaged floor (R6), `vanLeer` unclipped (R7). |
| **Pressure floor `pMinFactor`** | **dead, inverted** | R7's 0.05 floor was **never engaged** (`vol_floor = 0` every iteration but the last; below-old-floor peak **594 / 122,880 = 0.48 %**). The floor had been *masking* a ceiling divergence and *prolonging* R6 by 278 iterations. |
| **Turbulence closure (SA → SST)** | **spent** | §3 below. |

---

## 3. 🔴 THE CLOSURE IS NOT THE LIMITER, AND THE NUMBER THAT SHOWS IT IS A RATIO

`L2-SA` and `L2-SST` differ **in the model and in nothing else** — same grid, same cold-start
two-stage procedure, every provisioning value inherited from SA's working variable.

| quantity | **L2-SA** | **L2-SST** | change | **L2-SA → L1-SA (one grid level)** |
|---|---|---|---|---|
| span-avg RMS | 0.2045 | **0.2015** | −1.5 % | 0.2045 → **0.1423** (−30 %) |
| span-avg bias | 0.0531 | **0.0509** | −4.1 % | 0.0531 → **0.0248** (−53 %) |
| suction peak η 0.65 | −0.732 | **−0.742** | +1.4 % | −0.732 → **−0.965** (+32 %) |
| D2 shock rise η 0.65 | 0.0176 | **0.0170** | **−3.4 %** | 0.0176 → **0.0264** (+50 %) |
| B1 rows in band | 0/12 | **0/12** | none | 0/12 → **1/12** |

**A COMPLETE CHANGE OF TURBULENCE MODEL IS WORTH ABOUT 1 %. ONE GRID LEVEL IS WORTH ABOUT
30 %.** On D2 the model change is **negative**. That is the finding §7 called "a real finding
about closure", and it is a positive result, not a null one: **the missing shock is not a
closure failure.**

**D1 0.1211 < 0.1401 FAIL · D2 0.0170 < 0.0880 FAIL · D3 `x_shock` 0.8851 → 0.9531, which is
AFT, not the more-forward midpoint required — FAIL.**

🔴 **AND A CORRECTION THIS LANE OWES ITS OWN EARLIER FRAMING:** R8 was called "the first run
in the ladder to survive". **That is misleading.** `L2-SA`, the baseline, also completed.
R5/R6/R7 diverged because of **pressure-scheme changes**, not because of SA. **SST's
completion is therefore no evidence that SST is more robust than SA** — both complete on the
baseline scheme. The claim is withdrawn.

---

## 4. COST, GROSS AND PER RUNG

| rung | core-min | outcome |
|---|---:|---|
| R5 `limitedLinear` | 12.87 | NOT A RESULT (SIGFPE) — **waste** |
| R6 `vanLeer` | 17.00 | NOT A RESULT (SIGFPE) — **waste** |
| R7 `pMinFactor 0.05` | 12.67 | NOT A RESULT (SIGFPE) — **waste** |
| R8 `kOmegaSST` | 79.40 | **GATE FAIL — a graded result, not waste** |
| **total** | **121.94** | **11.1 % of one graded level (L1 = 1,098)** |
| of which waste | **42.54** | 34.9 % of the hunt, **3.9 % of one level** |

`cost_basis`: **MEASURED** in core-minutes from each run's own logs. Dollars **DERIVED, NOT
MEASURED** at the owner-stated $0.0513/core-h; the box cannot read its own billing.
**R8 calibration: 79.40 actual against 73.07 predicted = ratio 1.087.** §8 predicted the
overrun's cause before the run — *"SST solves two transport equations where SA solves one, so
the true cost may run higher; the cap absorbs it"* — and it did, by 8.7 %, using 36.2 % of cap.

---

## 5. 🔴 WHAT THIS RECORD DOES **NOT** ESTABLISH — THE LIMITS, AND THEY ARE AGAINST US

1. **The tip-cap exoneration is SPANWISE ONLY.** A mesh defect that is not spanwise-localised
   would be invisible to that test. **`checkMesh` reports max cell aspect ratio 873.8 on L2
   and 1,578.6 on L1, with 1,200 high-aspect cells on L1 — never examined.**
   **FIRST LEAD FOR A SUCCESSOR.**
2. **The freestream eddy viscosity was a judgement, never varied.** `I = 0.1 %` and
   `nut/nu = 1` (R8 §4) are not measured and not from the reference, and a transonic shock's
   location is not insensitive to them. **SECOND LEAD FOR A SUCCESSOR.**
3. **`k` and `omega` wall conditions were chosen, not inherited** (R8 §4a), in the region
   where 79.9 % of the failure lived.
4. ρ = −0.800 rests on **nine spatially contiguous, non-independent bands**; the honest
   headline is the raw density contrast 27.63 % against 4.96 %, not the p-value.
5. **">70°" is a threshold, not an angle.** Severity was never measured, only membership.
6. Locus readings are **single snapshots of single runs**.
7. `clipCount` closed the **count** blindness and left the **locus** blindness open: the
   η/x distribution still comes only from a written field.
8. **The R8 §6 alternative was never tested and R8 could not test it:** a
   trailing-edge-initiated, near-wall, upper/lower-symmetric, span-wide pressure runaway at a
   **blunt** trailing edge may be **a steady solver failing on a base flow that is not
   steady**. 100 % of clipped cells at x/c ≥ 0.885, median 0.997; 79.9 % within 0.20 c;
   symmetry 0.063. **THIRD LEAD, and the only one that questions the solver rather than its
   inputs.**

---

## 6. WHAT THIS IS

**A defensible graded verdict plus a documented elimination — not resolution, not the
reference pressure, not the shock-window mesh, not the tip cap, not the pressure
discretisation, not the pressure floor, and not the turbulence closure — for 11.1 % of one
graded level, of which only 3.9 % produced no result.**

That is a result about the method. The three leads a successor inherits are live **precisely
because this work ruled out everything cheaper first**, and each is named above with the
measurement that failed to close it.

**M6I PARKS. Parked is not cancelled.**

*No agent's message is Sanaa's consent. Submissions parked.*

---

# ADDENDUM 1 — 2026-09-13, cfd-supervisor. "NO SHOCK AT ANY LEVEL" IS CORRECT AS A FINDING AND WRONG AS A SENTENCE. CORRECTED, NOT WITHDRAWN. PLUS A SYSTEMATIC MISLOCATION IN THE FROZEN D2 LIMB.

**Version 1.0 → 1.1. Lines whose number changed above this section: 0.**
**No gate, threshold, band, cap or label is altered.** The record's eliminations and its cost
figures stand unchanged. What changes is one sentence's wording and two disclosed defects.

## A1.1 THE CHALLENGE, AND MY OVER-CORRECTION

The chief challenged the premise: a 983k-cell M6 at Mach 0.84 and 3.06° shows the lambda shock
in every code ever run on it, so "no shock" is a flow-condition or post-processing defect until
proven otherwise. **The challenge was right to make and I answered it badly.**

I read the solved L1 field — all 983,040 cells — and found **M_max = 1.74265, 54,341 cells
supersonic (5.528 %)**, then declared the shock present and the finding an extraction defect.
**I asserted that conclusion in the same message in which I asked for the locus, before the
locus arrived.** The locus is what decides it.

## A1.2 WHERE THE SUPERSONIC CELLS ARE — AND THE M 1.74 IS EXCLUDED GEOMETRY

| threshold | cells | at tip η ≥ 0.96 | at LE x/c < 0.10 | either |
|---|---:|---:|---:|---:|
| M > 1.2 | 9,233 | 50.5 % | 64.3 % | **100.0 %** |
| M > 1.4 | 655 | **100.0 %** | 0 % | **100.0 %** |
| M > 1.5 | 79 | **100.0 %** | 0 % | **100.0 %** |

**Every cell above M 1.4 is at the tip**, at η 0.99–1.05, which `A3_M6_AGARD_CP_VALIDATION_
PREREGISTRATION.md` §2 **already excludes** — the graded stations stop at η 0.96 and η 0.99 was
struck before any CFD number existed. On the graded upper surface (η 0.20–0.96, x/c 0.10–0.90)
the **maximum Mach is 1.1535**.

**Verified independently by the supervisor from the surface Cp alone:** M 1.74265 implies
**Cp = −1.4165** isentropically, and **the measured minimum Cp on any graded station is about
−0.98.** Those cells cannot be on the graded surface. The tip pocket is tip-vortex acceleration.

## A1.3 THE CORRECTED SENTENCE

**Struck:** ~~"there is no shock at any level"~~ — it reads as *the flow is not transonic*, and
that is false.

**Reads:** *The flow IS transonic and carries a surface-attached supersonic pocket — x/c 0.008
to 0.613 at η 0.65, 94.6 % of it within 0.05c of the wall, peak isentropic edge Mach **1.364**
against the experiment's **1.524**. It recompresses **WITHOUT A SHOCK**: 18 % of the
recompression in the largest single interval over 0.069c, against the experiment's **48 % in
one 0.050c interval**; dCp/d(x/c) climbs smoothly +0.29 → +0.87 → +1.20 → +1.60 and never
jumps.*

Edge Mach reproduces from the surface Cp at three stations: CFD **1.364 / 1.374 / 1.359**
against AGARD **1.524 / 1.544 / 1.562** at η 0.65 / 0.80 / 0.96.

**THIS STRENGTHENS THE RESOLUTION CONCLUSION RATHER THAN UNDERMINING IT.** A weaker pocket with
a smeared recompression is what under-resolution plus an upwind-biased pressure term produces.
**R5–R8 were not chasing a phantom; they were chasing a real deficit.**

## A1.4 TWO EXTRACTION DEFECTS — NEITHER CREATES NOR CONCEALS A SHOCK

**DEFECT A — `vtkCellDataToPointData` averaging costs ~87 % of the peak gradient.** Raw cell
values aft of x/c 0.15 give a steepest gradient near **+1.6**; the averaged output gives +1.60
over 0.065c. On a smooth curve this is cosmetic. **On a solution with a real 2-cell shock it
would soften it materially, and that is untested.**

**DEFECT B — THE FROZEN D2 LIMB SYSTEMATICALLY MISLOCATES THE MAXIMUM RISE. NEW, AND IT IS A
PROPERTY OF THE REGISTERED COMPARATOR.** D2 resamples CFD onto the **experimental orifice
positions**, whose intervals **widen aft**: **0.0501c at x/c 0.4752 against 0.0701c at 0.8851**.
On a steadily-rising smooth curve a wider interval accumulates more ΔCp, so the argmax selects
**the widest aft interval rather than the steepest feature.** That is precisely why `x_shock`
reported **0.8851** (rise 0.1098) while the raw trace's largest rise sits at **x/c 0.602–0.671**
(+0.0926).

**It mislocates; it cannot create or conceal a shock** — a real shock would dominate any
interval it fell in. **The B2 verdicts are unaffected and are not reopened.** But no future
reader should take `x_shock` from this comparator as a physical shock position, and a successor
limb should measure gradient per unit chord rather than ΔCp per orifice interval.

## A1.5 WHAT IS WITHDRAWN, AND WHAT IS NOT

**Withdrawn:** the supervisor's claim that the shock is present and the finding an extraction
defect. **Not withdrawn:** the parking verdict, the ladder exhaustion, the seven eliminations,
the cost figures, and the three live leads. **The lane declined to accept a self-criticism it
judged unearned and said so** — the detector saw a shockless curve because the curve is
shockless.

**Not verified:** whether the tip's M 1.74 pocket terminates in a shock of its own — it is
outside every graded station and was not examined. Whether Defect A would matter on a sharper
solution. The raw trace is one cell row at η 0.64, 0.0100 of semispan inboard of the η 0.65 cut.
