# Ahmed 25° c3 — two more draws (n = 4): results

Pre-registration: `R4_AHMED_C3_LEG2_PREREGISTRATION.md`, commit **`f4dec659`**,
committed before any new mesh existed. Chief-approved at ~10–14 core-min.
Record: `R4_runs/c3_leg2_record.json`.

> **No SIGNAL/NOISE verdict is claimed.** The c4 CI leg was deliberately not
> taken; `T` is not computed here.

---

## 1. The four draws

| draw | divisions | cells | vs c3 | **Cd** |
| --- | --- | --- | --- | --- |
| **c3s4** | (100 21 59) | 254 211 | −0.27% | **0.073943978** |
| **c3 (published)** | (98 21 59) | 254 911 | — | **0.073992743** |
| **c3s3** | (99 21 60) | 255 991 | +0.42% | **0.075521791** |
| **c3b** (leg 1) | (99 21 58) | 251 113 | −1.49% | **0.079827008** |

All four: birth certificate `clean`, `residualControl` **met** (181–210
iterations), G1 admitted. The mesh-first screening design worked — **5 of 5
candidates admitted**, against leg 1's 1 of 4.

## 2. The pre-registered branch: **B3 — broad scatter, and it is a near miss**

| | |
| --- | --- |
| `s_c3` (all four) | **2.769 × 10⁻³** |
| `s_c3` excluding the most extreme draw | 8.972 × 10⁻⁴ |
| **`R` = ratio** | **0.324** |
| pre-registered bar | `R ≤ 0.28` → outlier-dominated |
| most extreme draw | **c3b** (a redraw, not the original) |

**`R = 0.324` is above the 0.28 bar, so B3 fires: broad scatter — BOTH the
published number and the recipe are implicated, no single draw at this rung is
trustworthy, and the increment cannot be read from single draws at all.**

**It is a near miss and I am not going to round it.** `R = 0.324` sits at the
**14.6th percentile** of the pure-scatter null (median 0.594), so the data lean
toward outlier structure without reaching the bar I set. Had I set the bar at
the 15th percentile instead of the 10th, this would have read B2. **The bar was
fixed by simulation before the draws existed and it is not moving now** — that
is the whole point of setting it that way. What is honest to say is that
**n = 4 has low power to separate B2 from B3**, and this result sits in the
overlap.

## 3. The finding that does not depend on the branch at all

> **Even with the suspected outlier removed, `s_c3` = 8.97 × 10⁻⁴ — which is
> 1.01× the entire c3 → c4 increment of 8.895 × 10⁻⁴.**

The three clustered draws span 0.073944, 0.073993, 0.075522. Their own scatter
alone equals the increment the turn consists of. **So the turn is unreadable from
single draws whether c3b is an outlier or not**, and the B2/B3 question, while
interesting, does not change that conclusion.

## 4. The increment, and a sensitivity that is not a verdict

| basis | re-estimated increment | vs published +8.895 × 10⁻⁴ | leg-1 bar |
| --- | --- | --- | --- |
| **all four draws** (pre-registered) | **−8.907 × 10⁻⁴** | **−1.001×** — sign flips | **DISSOLVES** |
| excluding c3b *(sensitivity only)* | +4.445 × 10⁻⁴ | +0.500× | PARTIAL |

**DISSOLVES is confirmed at n = 4**, the same branch leg 1 fired at n = 2 — so
the n = 2 reading was not premature.

**The exclusion row is a sensitivity and must not be read as a verdict.** The
pre-registration forbids dropping any draw for its Cd; G1 excludes on delivered
cell count alone, before any solve. It is shown because a reader will otherwise
ask, and the answer is that **the published increment does not survive either
way** — it either inverts or halves.

## 5. What this establishes, and what it does not

**Establishes:** the Ahmed 25° c3 rung carries draw scatter of the same order as
the ladder increment that starts there, on four same-recipe meshes, three of
which are within 0.42% of the published cell count. **A ladder feature read from
one draw per rung is not readable at this rung.**

**Does not establish:**
- **No SIGNAL/NOISE verdict on the Ahmed turn** (§ header). That needs the c4 leg,
  which remains deliberately untaken.
- **Not whether c3b is a distinct flow state.** `R` leans that way and Cl moved
  with Cd in leg 1, but B3 fired and n = 4 cannot separate the hypotheses.
  Distinguishing them needs field inspection, not more draws — stated in the
  pre-registration and still true.
- **No amendment applied to `R4_ASYMPTOTIC_RESULTS.md`.** Its caveat (`4f73e0af`)
  says n = 2 of a planned 4; that is now n = 4 of 4 and the chief rules on what,
  if anything, moves.
- Nothing about `ahmed_35` or any other body.

## 6. Cost

| | predicted | measured |
| --- | --- | --- |
| five meshes (50.5 + 44.8 + 53.2 + 56.9 + 48.7 s, 1 core) | 4.0 | **4.2** |
| two solves (ClockTime 55 + 46 s × 4 ranks) | 6.2 | **6.7** |
| potentialFoam + decomposePar + reconstructPar ×2 | 0.5 | ~0.5 |
| **total** | **10.7** | **≈11.4** |

Inside the approved 10–14. **The design change paid for itself:** meshing all
five candidates cost 4.2 core-min and returned 5 admissible draws, where leg 1
spent 3.2 on meshes to get one — the cheap step bought the expensive step's
admission, exactly as pre-registered.

Three admitted meshes (c3s0, c3s1, c3s2) were **built and not solved**, per the
pre-registration's stop-at-n=4 rule. They are on disk and would cost ~3.1
core-min each to add if the chief ever wants n = 7.
