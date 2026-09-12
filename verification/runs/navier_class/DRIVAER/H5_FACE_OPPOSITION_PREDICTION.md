# Face-normal opposition across thickness — INSTRUMENT + PREDICTION, WRITTEN FIRST

**cfd lane, 2026-09-12. Zero compute.** Reads
`LAYERFIX_A1_coarse_relativeSizes/constant/polyMesh`, already on disk and committed at
`01401740f`. **No mesh is rebuilt.** If this ever rebuilds one it needs a registration
committed before compute; it does not. **No face pair, normal or fraction has been
computed for any patch.**

## Why this instrument, and what was wrong with the last one

H4 measured **point** normals accumulated onto shared points. On a thin plate the two
opposing sides **meet at the rim and share those points**, so the averaging destroyed the
opposition it was built to detect. `f_opp` came back ~0 on all seventeen patches — the
degenerate classifier, exactly the 12/17 baseline. **`NOT A RESULT`**, and the claim it
was meant to test is **untested**, not refuted.

This instrument compares **FACE** normals between distinct faces, which cannot be
averaged away.

## The instrument

For each patch, for each face *i* with unit normal `nᵢ` and centroid `cᵢ`, face *i* is
**OPPOSED** if there exists another face *j* of the same patch with

    nᵢ · nⱼ < −0.8        and        |cᵢ − cⱼ| < T

**`f_face_opp(T)`** = fraction of the patch's faces that are opposed.

**T is NOT fitted.** It is reported across a geometry- and dict-derived ladder, so no
single value is chosen after seeing the answer:

| T | where it comes from |
|---|---|
| 5 mm, 10 mm | below any layer the dict can produce |
| **25 mm** | level-5 surface cell |
| **50 mm** | level-4 surface cell |
| **42 mm / 84 mm** | the total requested layer stack at level 5 / level 4 (`1.6808 × cell`) |

The `−0.8` cosine is fixed here, before any measurement, and corresponds to 143°.

## 🔴 PLANT CONTROL — RUNS FIRST, AND A FAILURE REFUSES THE WHOLE MEASUREMENT

**A reader not shown able to see a known opposition proves nothing by reporting zero.**
Before any patch is measured:

1. **POSITIVE PLANT.** Take a control patch's faces, duplicate them offset by 2 mm along
   their own normals with the normals **flipped**, and run the reader on the union.
   **It must report `f_face_opp(5 mm) ≥ 0.9`.**
2. **NEGATIVE PLANT.** Run the reader on that same control patch **unmodified**.
   **It must report `f_face_opp(5 mm) ≤ 0.05`.**

**If either plant fails, the instrument is refused (exit 2) and no patch number is
reported.** A zero from a reader that cannot see a planted non-zero is not evidence.

## PREDICTION

> **Blocked patches carry a materially higher `f_face_opp` than controls at the small T
> values.** Brake discs, wheel supports and the exhaust tip are thin parts whose two
> sides face each other across a few millimetres. Controls are contiguous body panels
> with no self-opposing face at any T below the panel's own size.

Concretely: **controls near zero at T ≤ 50 mm; blocked patches showing a visible opposed
population at T ≤ 25 mm.**

## WHAT WOULD REFUTE IT — named before looking

- **Controls show comparable or higher `f_face_opp`** → **REFUTED**, wrong-signed.
- **Blocked patches near zero at every T** → **REFUTED**; the blocked patches are not
  thin-opposed parts and the whole thin-plate story is wrong.

## LIMBS, ALL THREE, FIXED NOW

1. **MAJORITY-CLASS BASELINE: 12/17 = 0.706.** A classifier calling everything blocked
   scores exactly that. **Any M not exceeding 12/17 is `NOT A RESULT`.**
2. **DEGENERACY LIMB:** if the best single threshold places all seventeen in one class,
   the metric has no resolution and M is meaningless **regardless of value**.
3. 🔴 **ORDERING CLAUSE — NEW, AND IT OUTRANKS ROWS 1 AND 2 AND EVERY CONDITION ABOVE:**
   **where a registered limb and the instrument's demonstrated capability disagree, THE
   INSTRUMENT GOVERNS.** A pre-registered condition earns its authority from the
   assumption that the measurement could have come out otherwise; when the plant control
   shows it could not, the condition is **void**. Voiding it is not a breach of the
   freeze — it is the freeze's own premise having failed. *(Standing in this family after
   H4, where a clean refutation was available on my own committed words and the
   instrument could not have seen the alternative either.)*

## 🔴 THE TWO PATCHES THIS MUST EXPLAIN — NAMED IN ADVANCE

**`CTRL_SURFACE_Outlet` and `Mirrors2` have now appeared together three times:**

1. **B1** — the only two of fourteen to move, 0.48 and 0.55, both refused by the 1.00 floor.
2. **B2** — the same two again, 0.48 and 0.63, refused again.
3. **H4** — the only two misclassified by the post-hoc median threshold.

**Three independent appearances is not coincidence: those two are qualitatively different
from the other ten.** A hypothesis that cannot say why is **incomplete**, and that is
registered as a requirement now rather than discovered as an excuse later. If this
instrument separates the other ten and fails on those two, the result is **PARTIAL at
best**, and the pair's distinctness is the finding rather than the noise.

## Held fixed

`nMedialAxisIter` absent-and-unlimited, untouched, named. Patch size stays an
**unpromoted** correlation. The §6 enumeration stays **EXHAUSTED**. The H4 median result
stays a **post-hoc observation**, not a result — if tested it gets its own registration
with a threshold **not** taken from the run that discovered it. A2 unlaunched.
