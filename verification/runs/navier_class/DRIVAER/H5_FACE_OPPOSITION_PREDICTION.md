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
---

## RESULT — 2026-09-12 — **REFUTED**. Measured after the freeze at `6d74171b8`.
*Lines whose number changed above this section: 0.*

### PLANT CONTROL: **PASS**, and it is what makes this a refutation rather than another H4

    POSITIVE (duplicated, offset 2 mm, normals flipped)  f_face_opp(5mm) = 1.0000  >= 0.90  PASS
    NEGATIVE (same patch unmodified)                     f_face_opp(5mm) = 0.0000  <= 0.05  PASS

**The reader can see an opposition and does not invent one.** H4's zero was uninterpretable
because its reader was never shown able to see a non-zero. This one was. **So here, a zero
is evidence.**

### The table

| group | T ≤ 25 mm | T = 42–84 mm |
|---|---|---|
| **CONTROL**, all five | **0.0000** | **0.0000** |
| **BLOCKED**, all twelve | **0.0000** | 7 of 12 still 0.0000 |

Every blocked patch reads **exactly 0.0000 at 5, 10 and 25 mm**. Seven of the twelve —
including **both brake discs**, `ExhaustSystem1`, `Mirrors2`, `CTRL_SURFACE_Outlet` and
both rim patches — read **0.0000 at every T up to 84 mm**.

### Verdict: the registered refutation condition fires

> *"Blocked patches near zero at every T → **REFUTED**; the blocked patches are not
> thin-opposed parts and the whole thin-plate story is wrong."*

**H5 REFUTED.** And the ordering clause does **not** void it: limb 3 voids a condition when
the instrument could not have come out otherwise, and the plant proves this one could.

The classifier limbs are not load-bearing here and are reported for completeness: M = 12/17,
degenerate, at **every** T, never beating the 12/17 baseline. But the refutation rests on the
**absolute values** — both groups are zero — not on any threshold, so limbs 1 and 2 are not
the reason and are not being used as one.

### 🔴 What this kills

**The thin-opposing-face story is dead for the patches it was invented to explain.**
`BrakeDiscfront` and `BrakeDiscrear` — the archetypal thin plates — carry **no opposing face
at any distance up to 84 mm**. A brake disc that is not a thin opposed plate *in this mesh*
is not being blocked by being one.

### One exception and one observation, neither promoted

- **`WheelSupportrear` reaches 0.9155 at T = 84 mm** — 92 % of its faces have an opposing
  face within the requested stack thickness. It is **one patch of twelve**, the other eleven
  do not follow it, and 84 mm is the layer-stack scale rather than a plate thickness. It
  explains nothing about the group and is recorded, not promoted.
- **Why might a brake disc have no opposing face?** Because the mesh may carry only **one
  side** of it: `BrakeDiscfront` has **14 faces** at a 50 mm cell. That would put these
  patches in the same family as `TirePlinthfront`/`rear`, which have **zero** faces — not
  thin parts that resist layers, but **parts too coarsely resolved to be closed surfaces at
  all**. **This is an observation, NOT a fourth hypothesis.** It is not promoted, it is not
  tested here, and if it is ever tested it gets its own registration with a falsifier.

### Standing

`CTRL_SURFACE_Outlet` and `Mirrors2` — the pair named in advance after three appearances —
read 0.0000 at every T, like the other five that do. **This instrument does not separate
them either**, so their distinctness remains unexplained and the requirement registered
above is unmet. §6 stays **EXHAUSTED**. Patch size stays **unpromoted**. A2 unlaunched.
---

## ADDENDUM — 2026-09-12 — CROSS-PATCH CHECK. **The refutation STANDS, now on a
qualified instrument.** *Lines whose number changed above this section: 0.*

### The defect in the instrument above, raised by the cfd-supervisor

The metric searched for an opposing face **only within the same patch**. If a plate's two
sides are authored as two named solids, `f_face_opp` reads zero for a **bookkeeping**
reason, not a geometric one — and `WheelSupportfront1`/`front2` and
`BrakeDiscfront`/`rear` are exactly that shape. **The plant above could not have caught
it**: it duplicated one patch's faces *into itself*, exercising only the same-patch path.
A control structurally incapable of failing in the direction that matters.

The physics argument is the stronger half: `medialAxisMeshMover` walks the **whole**
adapt-patch point set and has no notion of the STL's solid names. The same-patch
restriction imported the STL's bookkeeping into a measurement of the **solver's**
behaviour.

**Governing rule, named before the numbers: if same-patch and cross-patch differ, the
CROSS-PATCH number governs.**

### New plant — exercises the arm the old one could not

Opposing sheet planted into a **DIFFERENT patch label**:

    POSITIVE  f_cross(5 mm) = 1.0000  >= 0.90  PASS
    NEGATIVE  f_cross(5 mm) = 0.0000  <= 0.05  PASS

### Result at T = 50 mm, over all **52 wall patches / 27,816 wall faces**

| patch | same | **CROSS** | cross partner |
|---|---|---|---|
| floorNoSlip *(control)* | 0.0000 | 0.0082 | Tiresfront, Tiresrear |
| other four controls | 0.0000 | **0.0000** | — |
| **BrakeDiscfront, BrakeDiscrear** | 0.0000 | **0.0000** | — |
| CTRL_SURFACE_Outlet, ExhaustSystem1 | 0.0000 | **0.0000** | — |
| Rimsfront, Rimsrear | 0.0000 | **0.0000** | — |
| **WheelSupportfront2, WheelSupportrear** | 0.0000 | **0.0000** | — |
| Mirrors2 | 0.0000 | 0.0154 | Mirrors1 ×1 |
| WheelSupportfront1 | 0.0723 | 0.0723 | **own patch ×5**, underbody ×1 |
| Tiresfront | 0.0075 | 0.0469 | **floorNoSlip ×19** |
| Tiresrear | 0.0101 | 0.0319 | **floorNoSlip ×13** |

**Same-patch and cross-patch agree. The restriction was harmless — established by
measurement, not assumed.**

**And the specific worry is directly answered:** `BrakeDiscfront`/`rear` and
`WheelSupportfront2`/`rear` read **0.0000 cross** as well as same. The two-halves-of-one-
plate hypothesis is **not** what was masking this; there is genuinely no opposing face
within 50 mm. Where partners do appear they are not thin plates: `Tiresfront`/`rear`
oppose **`floorNoSlip`** — the tyre-to-ground contact, not a plate.

**H5 REFUTED stands.** The thin-opposing-face story is dead for the patches it was
invented to explain, and the instrument is now shown able to see the phenomenon by both
routes.

---

## RULED OUT — the M6 last-layer-to-surface-cell criterion

Criterion from the M6 family (`0a6d3a7a`): the last layer must land within **2–4×** the
local surface cell. **Verified here from the DrivAer dicts directly, not from relayed
figures.**

**A1 / B1 / B2 config** — `relativeSizes true`, `finalLayerThickness 0.5`, `expansionRatio
1.25`, `nSurfaceLayers 5`, `level (4 4)`, base cell 0.8 m:

> The last layer **is** `0.5 × cell` by the definition of `finalLayerThickness`, so
> `surface_cell / last_layer = 1 / 0.5 = **2.00**` — **identical at every level** because
> the spec is relative. Level 4: 50.0/25.0. Level 5: 25.0/12.5.

**2.00 is INSIDE the 2–4× band, at its bottom edge → THE CRITERION IS RULED OUT for
DrivAer.** Recorded as ruled out, per its author's own kill condition.

**But it retrodicts the original defect, and that is worth keeping.** The *graded* family
(`r1_coarse`, `relativeSizes false`, `firstLayerThickness 0.00075`) has a last layer of
`0.75 × 1.25⁴ = 1.831 mm` — absolute, level-independent — against a 50 mm cell:
**ratio 27.3×, far outside the band.** So the criterion correctly flags the configuration
that produced **zero** layers and correctly clears the one that produces 50 %. It does not
explain the remaining blocked patches, which is what it was handed over to do.
---

## CORRECTION — 2026-09-12 — the M6 criterion section above is **wrong in its label**.
**`RULED OUT` → `NOT APPLICABLE`.** *Lines whose number changed above this section: 0.*

The section above concludes the M6 last-layer criterion is **RULED OUT** for DrivAer.
**That claims we learned something about DrivAer. We learned nothing.**

### Why: under `relativeSizes true` the criterion is TAUTOLOGICAL

`finalLayerThickness f` **defines** the last layer as `f × the local surface cell`, so

    surface_cell / last_layer  =  1 / f      — ALWAYS, at every refinement level

f = 0.5 → 2.00. f = 0.3 → 3.33. f = 0.7 → 1.43. **The ratio is a restatement of the dict
entry. It has no failing branch, so it cannot rule anything out.** Measured across levels:

| level | cell | last layer | ratio |
|---|---|---|---|
| 4 | 50.00 mm | 25.000 mm | **2.00** |
| 5 | 25.00 mm | 12.500 mm | **2.00** |
| 6 | 12.50 mm | 6.250 mm | **2.00** |
| 7 | 6.25 mm | 3.125 mm | **2.00** |

### 🔴 The tell was in my own sentence, and I wrote it as a feature

The section above says, in the same breath as its conclusion:

> *"= **2.00** — **identical at every level** because the spec is relative."*

**A quantity identical at four refinement levels is not measuring the mesh.** I recorded
the exact fact that voids the conclusion and presented it as corroboration. This is not a
case of missing the defect — **I documented it and drew the wrong conclusion anyway.**

### And the check that would NOT have saved it

The instruction was *"verify it from the dict yourself, do not take my arithmetic"* —
guarding against a relayed-number error. **I did verify it from the dict, and the
arithmetic was correct.** An independent second party would have confirmed 2.00 and
recorded the same falsehood, **because the defect was upstream of the arithmetic.**

> **A relayed-number check catches transcription. It does not catch a test that cannot
> fail.** The two need different controls, and only the second one requires asking what
> the test's failing branch would look like.

### What survives, and it is not nothing

Under `relativeSizes **false**` — the ORIGINAL graded family — the ratio is **not**
tautological, because an absolute `firstLayerThickness` does not scale with the cell:

| level | cell | last layer | ratio | |
|---|---|---|---|---|
| 4 | 50.00 mm | 1.831 mm | **27.31** | outside |
| 5 | 25.00 mm | 1.831 mm | 13.65 | outside |
| 6 | 12.50 mm | 1.831 mm | 6.83 | outside |
| 7 | 6.25 mm | 1.831 mm | **3.41** | **inside 2–4** |

**It varies 27.3 → 3.4 and has a real failing branch.** So the criterion *is* applicable
to the absolute-thickness configuration, and it flags `r1_coarse` — the build that
produced **zero** layers — at 27.3×, while predicting the breach would clear at level 7.
That is an independent retrodiction of the A1 finding from another family's physics and
it is kept.

### Record

- **A1 / B1 / B2 (`relativeSizes true`): NOT APPLICABLE.** No conclusion drawn.
- **`r1_coarse` (`relativeSizes false`): applicable, and outside the band at 27.3×** —
  corroborating, not new.
- The corrected form of the criterion is **total ACHIEVED stack thickness against local
  boundary-layer thickness, measured on the achieved mesh, never from the dict.** It is
  **structurally untestable on the blocked patches**: where layers are not forming there
  is no achieved stack to measure. **You cannot diagnose a failure-to-produce by measuring
  the thing that was not produced.** Recorded as a limit, not a gap to route around.
---

## CORRECTION 2 — 2026-09-12 — the retrodiction points the OTHER WAY.
*Lines whose number changed above this section: 0.*

Correction 1 kept the `r1_coarse` 27.3× result as *"an independent retrodiction of the A1
finding from another family's physics."* **That direction is wrong.**

**Both DrivAer ratios are functions of the dict alone.** `relativeSizes false` +
`firstLayerThickness 0.00075` → 1.831 mm against a 50 mm cell → 27.3×. `relativeSizes
true` + `f = 0.5` → 2.00. Neither number touches a built mesh. **A re-encoding of the
input cannot be independent evidence about the outcome that input produced.**

**What the exercise actually validates is M6's 2–4× BAND.** The threshold is the one
genuinely independent element — derived from M6's boundary-layer physics with no
knowledge of DrivAer — and it correctly separates a **known-zero-layer** configuration
(27.3×, outside) from a **known-50 %** one (2.00×, inside).

> **The band is validated against a known outcome pair. DrivAer learns nothing about
> itself.** That is a genuine gift to M6 and it is **not** a finding about these patches.

**Status of the criterion, final:** a **dict-level screen** computable before any build,
not a measurement of an achieved mesh — and therefore structurally incapable of
explaining why specific patches fail. Its diagnostic form (total **achieved** stack
against local boundary-layer thickness, on the achieved mesh) remains untestable here:
where layers are not forming there is no achieved stack to measure.
