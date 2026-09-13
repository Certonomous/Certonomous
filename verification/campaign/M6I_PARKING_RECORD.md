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
