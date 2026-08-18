# Ahmed 25° c3 draw scatter — leg 1 results

Pre-registration: `R4_AHMED_TURN_DRAW_SCATTER_PREREGISTRATION.md`, commit
**`e543bc5e`**, committed before any new mesh existed. Leg 1 only (8.6 core-min
predicted, **6.8 measured**); **leg 2 was not taken.**

> **This leg cannot and does not declare a SIGNAL verdict** (pre-registration
> §2). What follows is the Ground-2 increment-movement test and nothing more.

---

## 1. The pre-registered branch fires: **DISSOLVES**

| | value |
| --- | --- |
| published increment c3 → c4 | **+8.895 × 10⁻⁴** |
| c3 mean over {c3, **c3b**} | 0.076909876 |
| c4 mean over {c4, c4b} | 0.074930654 |
| **re-estimated increment** | **−1.979 × 10⁻³** |

The pre-registered bar: *DISSOLVES if the re-estimated increment falls below 50%
of the published one **or the sign flips**.* **The sign flips and the magnitude
grows 2.2×.** Branch: **DISSOLVES**.

**And the reason is one number:**

| draw | divisions | cells | **Cd** | Cl |
| --- | --- | --- | --- | --- |
| c3 (published) | (98 21 59) | 254 911 | **0.073992743** | 0.1217398 |
| **c3b (new)** | (99 21 58) | 251 113 (−1.49%) | **0.079827008** | 0.1490356 |

> **Two same-recipe meshes at the same nominal resolution differ by
> 5.834 × 10⁻³ in Cd — 6.6× the ladder increment the turn consists of, and 60×
> the c4/c4b pair's 9.7 × 10⁻⁵.**

## 2. Before believing it — the checks I ran

**The instrument was validated against published values first**, as on the B-52
arm. My reader reproduces `c2` and `c3` **exactly** (0.079359699, 0.073992743)
and `c1`/`c4`/`c4b` to within 4 × 10⁻⁷ — six orders of magnitude below the
effect. Not a convention mismatch.

**c3b is not a defective mesh.** It is *cleaner* than the original:

| | max aspect ratio | max non-orthogonality | max skewness | checkMesh |
| --- | --- | --- | --- | --- |
| c3 | 4.301 | 49.416 | 2.003 | OK |
| **c3b** | **3.668** | 49.607 | **1.500** | OK |

Birth certificate `clean`, admitted by hash at entry.

**c3b converged on the ladder's own rule.** `SIMPLE solution converged` in **203
iterations** against c3's 220 — `residualControl` met, not a cap-stop. G3 passes.

**Cl moves with Cd** (0.1217 → 0.1490, +22%). A force-integration or windowing
artifact would not move both coefficients coherently. **This is a change of flow
state, not of arithmetic.**

**Named hypothesis, not a claim:** the Ahmed 25° slant is the textbook
bistable-separation geometry — 25° sits at the edge of the fully-attached /
fully-separated transition. A mesh draw flipping the slant state would produce
exactly this signature: both force coefficients shift together, both solves
converge cleanly, both meshes are good. **Not tested here, and not claimed.**

## 3. The honest limitation — this rests on n = 2

**c3c was REFUSED by G1 and its re-draw allowance is exhausted.** All three
pre-registered candidates undershot the ±2.0% band:

| attempt | divisions | product | delivered cells | vs c3 | |
| --- | --- | --- | --- | --- | --- |
| c3b | (99 21 58) | 120 582 | 251 113 | −1.49% | **admitted** |
| c3c #1 | (97 21 60) | 122 220 | 248 599 | −2.48% | re-draw |
| c3c #2 | (96 21 61) | 122 976 | 244 315 | −4.16% | re-draw |
| c3c #3 | (100 21 57) | 119 700 | 242 597 | −4.83% | **refused, allowance exhausted** |

**The allowance was not extended.** The pre-registration fixed ≤2 re-draws, and
quietly taking a fourth candidate after seeing that the third missed is exactly
the motivated-reading breach this arm is about.

**So the branch fires on n = 2 at c3, and with n = 2 you cannot separate
"genuine large draw scatter" from "one anomalous draw".** The DISSOLVES verdict
is the pre-registered reading of the data obtained; **it is not a demonstration
that the Ahmed turn is noise.** What it demonstrates is narrower and still
serious: **a single same-recipe redraw at c3 moves the ladder's increment past
zero.** A turn that one mesh can invert is not a turn anyone should be building
cross-family claims on — which is the standing the B-52's had this morning.

## 4. A second finding, free: the Ahmed recipe controls delivered cells even worse than the B-52's

Five triples, sorted by background-cell product:

| product | delivered cells |
| --- | --- |
| 119 700 | 242 597 |
| 120 582 | 251 113 |
| **121 422 (the original)** | **254 911 ← the maximum** |
| 122 220 | 248 599 |
| 122 976 | 244 315 |

**Delivered cells rise then fall as the product rises, and the published c3 draw
sits at the peak.** `B52_RECIPE_NOTE_BACKGROUND_PRODUCT.md` found the product
does not control the delivered count on the B-52; on the Ahmed it is worse —
**locally anti-correlated**, with the incumbent draw at a local maximum. Four of
five candidates could not even reach the resolution band, which is why leg 1
returned n = 2 instead of n = 3.

## 5. What this does and does not change

**Does not change:** `ahmed_25.json`'s band, order or verdict — `conclusive:
false`, unchanged. No SIGNAL/NOISE verdict on the Ahmed turn (leg 1 cannot give
one). Nothing about `ahmed_35` or any other body. The B-52 withdrawal is not
revisited.

**Does change the standing of one claim, and it is not mine to rule on:**
`R4_ASYMPTOTIC_RESULTS.md` §4 states *"Not one unlucky mesh"* on the strength of
the c4/c4b pair, and concludes *"the turn is a property of the resolution, not of
a particular mesh."* That conclusion was drawn from a replicate at the turn's
**upper** end. **Its lower end, tested here for the first time, moves by 6.6× the
increment.** I have applied **no** amendment to that record — the chief rules,
and n = 2 is thin evidence to amend a headline on.

## 6. Cost

| | predicted | measured |
| --- | --- | --- |
| meshes (4 built: 39.0 + 42.9 + 50.5 + 60.1 s, 1 core) | 1.8 | **3.2** |
| c3b solve (ClockTime 47 s × 4 ranks) | 6.8 | **3.1** |
| potentialFoam + decomposePar + reconstructPar | — | ~0.5 |
| **total** | **8.6** | **6.8** |

Under budget, and for a stated reason that is not good news: **three of the four
meshes were built for a draw that G1 then refused**, so a third of the spend
bought a refusal — which is the gate working, and is recorded as cost rather
than netted out.

## 7. Recommended next step — priced, not taken

**The question leg 1 raises is worth more than the one it was asked.** The choice
is the chief's:

| option | what it settles | core-min |
| --- | --- | --- |
| **A — two more c3 draws** (n = 4), with a division search that can actually reach the band | whether 5.8 × 10⁻³ is the rung's scatter or one anomalous mesh. **The decisive question.** | ≈**10–14** (higher than leg 1's per-draw price: the band is hard to hit on this recipe, so budget refused attempts) |
| B — leg 2, one more c4 draw | the CI verdict on `T` | 17.6–72.8 (**a floor**: c4 took 623 iterations, c4b 1 668) |
| C — stop | the turn's standing is recorded as contested at n = 2 | 0 |

**I recommend A, and explicitly not B.** Leg 2 buys a CI on a `T` computed from
an `s_c3` that is currently one pairwise difference from a possibly-anomalous
draw — refining the interval around a badly-estimated centre. **A is cheaper,
answers the question that actually moved, and would make B interpretable if it is
still wanted afterwards.**
