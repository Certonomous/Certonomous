# SUBOFF A1h L1M SWEEP — THE `bounding k` QUESTION, ANSWERED FROM THE FIELDS

**Drafted by a cfd lab-lane, 2026-09-14. Evidence file, not a grade. The only grading
path for this act is `cases/navier_class/SUBOFF_A1/grade_suboff_a1h.py`.**

## 1. WHY THE LOG CANNOT ANSWER "HOW MANY CELLS", AND THE SOURCE THAT SAYS SO

`/usr/lib/openfoam/openfoam2606/src/finiteVolume/cfdTools/general/bound/bound.C` prints
`min`, `max` and `average` and **no count**. Worse for a later reader: it does **not** set
the offending cells to the floor. It sets them to

    max( max(vsf, fvc::average(max(vsf,lowerBound)) * pos0(-vsf)), lowerBound )

i.e. a cell with `k <= 0` is replaced by the **face-interpolated neighbour average**.
**The repair therefore leaves no fingerprint in the written field**: there is no
"cells sitting at the floor" population to count afterwards, and no per-cell diagnostic
field is written. **The per-iteration clipped-cell count is not on disk in any form** and
cannot be recovered without instrumenting the solver, which was not done — the seven runs
were read-only throughout.

## 2. WHAT *IS* ON DISK, COUNTED AND NOT HISTOGRAMMED

Written `k`, all four ranks, latest time common to the four (artifact
`BOUNDING_K_FIELD_READ_BETA_p08.json`; the count sweep covers all seven points):

| point | time | cells | **cells with k <= 0** | cells with k < 1e-6 | min k | mean k |
|---|---|---|---|---|---|---|
| BETA_m12 | 2745 | 6,537,226 | **0** | 0 | 3.2837e-06 | 3.025022e-02 |
| BETA_m08 | 2790 | 6,537,226 | **0** | 3 | 7.3525e-07 | 3.018839e-02 |
| BETA_m04 | 2820 | 6,537,226 | **0** | 0 | 1.6248e-06 | 3.022947e-02 |
| BETA_p00 | 2880 | 6,537,226 | **0** | 0 | 4.5791e-06 | 3.027842e-02 |
| BETA_p04 | 2805 | 6,537,226 | **0** | 0 | 1.6054e-06 | 3.023071e-02 |
| BETA_p08 | 2835 | 6,537,226 | **0** | 3 | 7.7012e-07 | 3.018996e-02 |
| BETA_p12 | 2670 | 6,537,226 | **0** | 0 | 3.1211e-06 | 3.024999e-02 |

**RULE 3.** The zero above is a **seen** zero. A copy of `BETA_p08/processor1/<t>/k` was
taken to scratch, `k = -1.234e-03` was written into local cell **777777** by byte offset,
and the same reader was required to report **exactly one** non-positive cell **at that
index** or refuse with exit 2. It read it back exactly.

**A caution against a misreading:** 737,263 cells sit below `1e-5` on BETA_p08. That is
**not** a defect — the registered freestream is `k_inf = 1.118157e-05` (prereg §1), so
those cells are simply undisturbed far field.

## 3. WHERE THE LOW-k CELLS ARE — COORDINATES, NOT ADJECTIVES

The 200 lowest-k cells on BETA_p08 (50 per rank), cell centroids as the **vertex average**
of each cell's own points (not OpenFOAM's volume-weighted centroid; the difference is
smaller than one cell):

- The 15 lowest all sit in **x ∈ [1.2892, 1.2905] m, y ∈ [0.2540, 0.2542] m,
  z ∈ [0.0009, 0.0014] m**.
- `sail` patch bounding box: x ∈ [0.92445, **1.29095**], y ∈ [0.25179, 0.47625],
  z ∈ [−0.03334, +0.03334]. `hull` patch: |y|,|z| ≤ 0.254, x ∈ [0, 4.3566].
- So the population is the **sail trailing-edge / hull junction**, on the centreplane —
  the aft corner where the fairwater meets the hull.

**DO THEY TOUCH THE FORCE PATCHES? YES, MEASURED.** Nearest-point distance from each
centroid to the `hull` and `sail` surfaces of the global mesh (scipy cKDTree over 233,372
hull faces and 166,582 sail faces):

- lowest 15: **d_hull 0.00004–0.0002 m, d_sail 0.00006–0.0001 m** — the first cell layer.
- of the 200: **50 within 0.01 m of `hull`, 51 within 0.01 m of `sail`**; the remaining
  ~149 are far field (out to 5.6 m from the hull).

## 4. CAN IT CONTAMINATE THE GRADED FORCE? THE BOUND, MEASURED

Turbulence enters the force only through the **viscous** part. At `Time = 2835`
(`BETA_p08/postProcessing/forcesHull/0/force.dat`, last row), z-component:

- `hull`: total **−4.5431474077e-02**, pressure **−4.6811205304e-02**, viscous
  **+1.3797312267e-03** → **pressure 103.0 %, viscous −3.04 %** of the total.
- `sail` (`forcesSail/0/force.dat`): total +2.6965705402e-02, viscous +1.7415296146e-04 →
  **viscous 0.65 %**.

So even total corruption of `nut` in that corner is bounded by ~3 % of hull `F_z`, and the
hull/sail sign disagreement under investigation is a **pressure-side** phenomenon.

## 5. THE TEMPORAL BEHAVIOUR — AND A CORRECTION TO "SHRINKING"

From the single named artifact `BETA_p08/log.simpleFoam`, every `bounding k` line paired
with its `Time`: **2,804 events in 2,835 iterations** — it bounds on essentially every
iteration.

| window | events | worst `min` | worst `|min|` / its own `average` |
|---|---|---|---|
| 1–500 | 469 | −1.0546e-02 | **13.19** |
| 501–1000 | 500 | −3.9939e-04 | 1.323e-02 |
| 1001–2000 | 1000 | −4.1503e-04 | 1.375e-02 |
| 2001–2500 | 500 | −4.0118e-04 | 1.329e-02 |
| 2501–end | 335 | −4.0182e-04 | 1.331e-02 |

The startup transient (excursion 13× the mean) cleared by iteration ~500. **From 501
onward the worst excursion is FLAT at 1.32–1.38 % of the mean, not shrinking** — the
supervisor's relayed reading of "shrinking" is corrected here to **plateaued**. The final
event reads `min: −2.4869e-04` against `average: 3.01899556e-02`, i.e. **0.82 %**.

## 6. THE JUDGEMENT, WITH THE NUMBER THAT JUSTIFIES THE WORD

**BENIGN CLIPPING.** The numbers that carry the word:

- **0 of 6,537,226 cells** are at or below the bound in the written field, on every one of
  the seven points, from a reader **proven** able to see a planted negative.
- the excursion is **0.82 % of the mean** at the last event and has been **flat** at
  ~1.33 % for 2,300 iterations — a DrivAer-class signature needs a negative minimum
  *comparable to the mean* and *growing*; this is two orders of magnitude smaller and
  stationary.
- the affected corner touches both force patches, but its only route into the force is the
  viscous share, measured at **3.04 %** of hull `F_z`.

**HONEST LIMIT.** "Benign" describes the excursion's size and trend and the bound on its
force route. It is **not** a claim that the sweep is sound: the act is `NOT A RESULT` on
grounds that have nothing to do with `k` (see `LANDING.txt`).
