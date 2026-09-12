# MRF R2 ET8000 — y+ TRAJECTORY ACROSS THE FAMILY — **DIAGNOSTIC ONLY**

> 🔴 **THIS CHANGES NO GATE, NO THRESHOLD, NO BAND AND NO LABEL.** The triple
> prestatement is frozen at `5c6869f7` and `grade_triple_r2.py` (blob `b3758cc5…`) is the
> grader. **Nothing in this file goes near the grading path.** Rule 5 governs the verdict:
> a triple that is not `CONVERGING` is `NOT A RESULT` whatever the y+ says, and a
> `CONVERGING` triple is not retroactively condemned or rescued by it. This is context
> reported **beside** a verdict, never folded into one. **No verdict is issued here.**

**Status: TWO OF THREE LEVELS. `fine` was still solving when this was written (iteration
~6,700 of 8,000) and is NOT measured here.** The trajectory is the whole claim and a
two-point trajectory is a line through two points; **fine is what makes it a trajectory.**

---

## 1 — THE HYPOTHESIS, AND ITS FALSIFIER, FIXED BEFORE THE NUMBERS EXISTED

Raised by the cfd-supervisor 2026-09-12. Falsifier committed at **01:05Z, before any
`yPlus` artifact existed anywhere in the ET8000 tree** — verified by `find`, which returned
nothing; **nobody had ever looked.**

**Hypothesis.** MRF R2 uses `nutkWallFunction` — a **high-Re** wall function — on a family
with **no prism layers** (`addLayers false`, empty `layers {}`), so the first cell height is
set by the local hex and **shrinks with refinement**. If y+ then crosses `nutkWallFunction`'s
own switch at `yPlusLam` (the linear/log intersection, **≈ 11.53** at κ = 0.41, E = 9.8), the
wall-shear model is answering a different question at each level, and a force coefficient
computed under it has no reason to converge monotonically. Three DIVERGENT triples stand
behind it: R1b, MRF R1 (observed order −5.2311), MRF R2 at 4000 (−5.7784); and
`SUBOFF_A1_PREREGISTRATION.md` §1.2 diagnosed this exact mechanism elsewhere, in its own
words — *"high-Re wall functions on a family that refines y+ from 25 to ~11"*.

**The three registered falsifiers, verbatim from the pre-commitment:**

- **(L1) PREMISE FALSE** — y+ does not fall monotonically coarse → medium → fine.
- **(L2) NO REGIME CHANGE** — patch-average stays above ~30 at all levels and **no level has
  a material fraction of wall faces below `yPlusLam` ≈ 11.53**.
- **(L3) MOVEMENT TOO SMALL TO MATTER** — patch-average moves < ~30 % across the family and
  stays on one side of `yPlusLam`.

It **survives** (survives, *not* is confirmed) only if the family **straddles** `yPlusLam`:
fractions below 11.53 growing materially with refinement.

---

## 2 — THE MEASUREMENT (observation of the output, not input wearing units)

`simpleFoam -postProcess -func yPlus -time 8000` against each **completed** level, run
`nice -n 19` so it did not compete with the live fine solve. rc 0 both. **The six fields the
frozen grader reads (`U p k omega nut phi` at `8000`) carry byte-identical mtimes before and
after** — checked, not assumed; the post-process added `8000/yPlus` and `log.yPlus` and
touched nothing else.

**PROVENANCE, stated because it is the difference between evidence and arithmetic:** every
number below is computed by OpenFOAM from the **solved** `U` and `nut` fields of a completed
run. **Nothing here is derived from the dict, the cell size or the Reynolds number.** The
one figure that is *not* an observation is `yPlusLam ≈ 11.53`, which is the wall function's
own analytic switch constant — a property of the model, labelled as such.

### 2.1 — Per-patch y+ (min / average / max)

| patch | coarse min/avg/max | medium min/avg/max | avg change |
|---|---|---|---|
| tankWall | 3.415 / **131.84** / 485.35 | 2.070 / **78.80** / 375.03 | **−40.2 %** |
| tankBottom | 2.393 / **105.25** / 232.39 | 2.342 / **65.09** / 155.75 | **−38.2 %** |
| tankLid | 0.306 / **43.65** / 153.57 | 0.566 / **35.99** / 106.48 | −17.5 % |
| baffles | 3.060 / **58.19** / 312.21 | 1.502 / **28.12** / 192.34 | **−51.7 %** |
| **shaft** ★ | 3.251 / **25.41** / 62.21 | 1.291 / **21.30** / 63.21 | −16.2 % |
| **impeller** ★ | 4.086 / **37.68** / 89.74 | 5.326 / **25.41** / 62.43 | **−32.6 %** |

★ = the only two patches that enter the graded quantity (§3).

### 2.2 — Fraction of wall faces BELOW `yPlusLam` = 11.53 — the sharp test

A minimum can be one face. The fraction is the quantity the hypothesis is actually about.

| patch | faces (c / m) | **coarse frac** | **medium frac** | factor |
|---|---|---|---|---|
| tankWall | 3,168 / 9,752 | 3.31 % | 6.49 % | ×1.96 |
| tankBottom | 920 / 2,313 | 0.76 % | 2.46 % | ×3.24 |
| tankLid | 1,120 / 2,720 | 13.75 % | **10.00 %** | **×0.73 — FALLS** |
| baffles | 2,400 / 6,080 | 3.25 % | **15.16 %** | ×4.66 |
| **shaft** ★ | 2,236 / 3,024 | 4.34 % | **25.00 %** | **×5.76** |
| **impeller** ★ | 7,984 / 21,368 | 0.25 % | 1.14 % | ×4.56 |

---

## 3 — SCORING THE THREE FALSIFIERS, ON TWO LEVELS

- **(L1) NOT TRIGGERED.** Every patch average falls from coarse to medium. The premise holds.
- **(L2) NOT TRIGGERED.** Five of six patches have a materially growing fraction below
  `yPlusLam`, and **one quarter of the shaft's wall faces are in the viscous branch at the
  medium level.** This is not a boundary effect at a single face.
- **(L3) NOT TRIGGERED.** Averages move 16–52 %; fractions move ×2 to ×5.8.

**The hypothesis therefore SURVIVES on two levels. It is NOT confirmed.** A surviving
hypothesis is one that has not yet been killed.

**One honest counter-current, reported rather than dropped:** `tankLid`'s fraction below
`yPlusLam` **falls**, 13.75 % → 10.00 %, against the trend on every other patch. It is a
slip lid with `zeroGradient` on `nut`, so it is the least representative wall in the model —
but the hypothesis predicts a direction and one patch goes the other way, and that is stated.

---

## 4 — A BOUND THE FALSIFIERS DID NOT ANTICIPATE, AND IT CUTS AGAINST THE HYPOTHESIS

**This is the most important section in this file, and it weakens the mechanism I was
asked to test.**

The graded quantity is `Np`, derived from `total_z` of the `impellerForces` function object,
whose definition reads `patches (impeller shaft)` — **read from the case's own
`system/controlDict`, not assumed.** So `baffles` and `tankWall`, which carry the largest y+
movement in §2, **do not enter the graded number at all.** Of the two patches that do, the
impeller's fraction below `yPlusLam` is **0.25 % → 1.14 %** — small in absolute terms.

And the decisive figure. A wall function sets the **wall shear stress**, which is the
**viscous** part of the moment. Measured at `endTime` 8000 from `moment.dat`:

| level | `total_z` | `pressure_z` | `viscous_z` | **viscous share of the graded moment** |
|---|---|---|---|---|
| coarse | −0.166520 | −0.165945 | −0.000575 | **0.345 %** |
| medium | −0.170000 | −0.169772 | −0.000229 | **0.134 %** |

> **THE DIRECT CHANNEL BY WHICH THE WALL FUNCTION REACHES THE GRADED QUANTITY IS UNDER
> HALF A PERCENT OF IT, AND IT HALVES BETWEEN LEVELS.** The coarse→medium change in `Np` is
> **+2.09 %** (`0.170000 / 0.166520`, matching the prestatement's 4.193491 → 4.281132).
> **Even annihilating the entire viscous moment would move `Np` by 0.345 %, about one sixth
> of the observed level-to-level change.** The regime-change mechanism **cannot account for
> the divergence through its direct channel.**

**What survives of it, stated precisely and not inflated.** The wall function also sets
`nut` at the wall, which feeds `k` and `ω` and therefore the turbulence field, and the
turbulence field sets the blade **pressure** distribution — which is 99.7 % of the graded
moment. That indirect path is **not bounded by 0.345 %** and is **not measured by anything
in this file.** So the hypothesis is not refuted; it has been **moved off the channel that
was easy to check and onto one that is not**, and it now owes a measurement it did not owe
before.

**A second observation that is interesting and is NOT evidence for the hypothesis:** the
viscous share itself falls by a factor of 2.6 between levels. That is a large relative change
in exactly the component the wall function sets — consistent with a non-level-invariant wall
treatment — but it is equally consistent with a thinner resolved near-wall region simply
carrying less modelled shear. **Two explanations, one observation, and this file does not
choose between them.**

---

## 5 — WHAT IS AND IS NOT ESTABLISHED

**Established:** the configuration that produced a diagnosed divergence elsewhere is present
here; it *does* move y+ materially across this family; five of six patches move the
predicted way; and **nobody had measured any of it before 2026-09-12** — the first `yPlus`
artifact in this tree was created by this diagnostic.

**NOT established:** that this is the cause of the MRF divergence. The direct channel is
bounded at 0.345 % against a 2.09 % effect (§4), and the indirect channel is unmeasured.

**OWED, and cheap:** fine's y+ when it lands — the same `-postProcess -func yPlus`, no solve.
Fine is where the hypothesis is decided, because a two-point trajectory is a line.

**A cost note (rule 12):** this diagnostic cost **0.567 core-min** measured — coarse 9 wall s
+ medium 25 wall s, 1 rank, `nice -n 19` — = **$0.0005 DERIVED, NEVER MEASURED** at
$0.0513/core-h. No solve was run; both levels were already complete.

*— cfd `lab-lane`, 2026-09-12. DIAGNOSTIC. No gate moved. No verdict issued.*
