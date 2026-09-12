# DRIVAER — **SOLVED** y⁺ REPLACES THE ESTIMATE. THE ESTIMATE WAS MATERIALLY WRONG, AND ONE OF THIS LANE'S OWN CLAIMS IS CORRECTED BY IT.

**Filed 2026-09-12 by a cfd `lab-lane`. No solver was run. No graded tree was touched — PROVEN
by census below. Alters no gate, threshold, cap or label.**

---

## 0. 🔴 THE METHOD WAS WRONG FIRST, AND A PLANTED CONTROL IS THE ONLY REASON THAT IS KNOWN

The obvious invocation — **`postProcess -func yPlus -time 2000`** — ran cleanly (`rc = 0`, an
`End` line) and returned **`min = 0, max = 0, average = 0` on ALL 52 PATCHES, on BOTH ARMS.**

**That zero was not reported as a measurement.** Rule 3: *a zero from a reader not shown able to
see a non-zero is not evidence.* So the same method was driven against a **POSITIVE CONTROL with
a known answer** — CRM wing-alone, whose own `yPlus` functionObject wrote
`min 3.11461128 / max 4.43703852e+01 / average 1.84164053e+01` during the solve, with that field
**removed from the probe copy** so the probe had to produce it independently.

| probe on the CRM control | result |
|---|---|
| `postProcess -func yPlus` | **0 / 0 / 0 — THE CONTROL FAILED. THE METHOD IS BROKEN.** |
| **`rhoSimpleFoam -postProcess -func yPlus`** | **3.1146113 / 44.370385 / 18.416405 — matches the truth to every digit** |

**The generic `postProcess` does not construct the solver's turbulence model, so the wall
functions are absent and y⁺ is identically zero. It exits 0 and prints `End` while doing it.**
Had the control not been run, this record would have reported "solved y⁺ = 0 everywhere" — a
clean-looking, entirely false result that would have destroyed the Y1 analysis.

**All DrivAer numbers below come from `simpleFoam -postProcess -func yPlus -time 2000`**, the
solver-mode form, **52 of 52 patches non-zero on both arms.**

---

## 1. SOLVED vs MESH-DERIVED — THE ESTIMATE IS MATERIALLY WRONG

| group | patches | **SOLVED** avg | solved min | solved max | **ESTIMATE** (area-wtd median) | |
|---|---:|---:|---:|---:|---:|---|
| layered | 27 | **460.15** | 3.06 | 4613.49 | 481.56 | **4.4 % apart — close** |
| unlayered | 20 | **791.82** | 3.94 | 4228.97 | 1941.00 | **THE ESTIMATE IS 2.45× TOO HIGH** |

**Per patch the disagreement is worse: median 36.3 % over 47 vehicle patches**, and the largest
are systematic rather than scattered:

| patch | faces | estimate | **SOLVED** | apart |
|---|---:|---:|---:|---:|
| `BodyFasciafront2` | 51 | 797.0 | **42.7** | 94.6 % |
| `BodyFasciafront1` | 1,076 | 495.4 | **37.8** | 92.4 % |
| `BodyHeadlamps` | 210 | 401.5 | **31.5** | 92.2 % |
| `ClosedGrillLowerInsert` | 90 | 274.6 | **24.8** | 91.0 % |
| `ClosedGrillUpperInsert` | 152 | 404.4 | **37.1** | 90.8 % |
| `BrakeDiscfront` | 14 | 1726.8 | **572.3** | 66.9 % |
| `Rimsfront` | 179 | 1857.3 | **630.6** | 66.0 % |

**The pattern is physical, not random: the worst disagreements are the FRONT STAGNATION patches**
— fascia, headlamps, grill inserts. The estimate's basis is `u_tau` from **`U_inf` ALONE**, and
free-stream `u_tau` is exactly wrong where the flow stagnates. **An input-based estimate cannot
know where the flow slowed down.**

---

## 2. 🔴 A CLAIM OF THIS LANE'S OWN IS CORRECTED

`DRIVAER_R2C_B2_RESULTS_2026-09-12.md` §5 and the per-patch record state, on the **estimate**,
that layered-group y⁺ minimum is 34.235 and unlayered 56.062, and conclude:

> *"the ENTIRE BODY is above the crossover, with nothing in the buffer layer for the blending to
> act on."*

**ON SOLVED y⁺ THAT SENTENCE IS FALSE.** The solved minimum is **3.056** (control) and **4.125**
(blended), and **one patch — `ClosedGrillLowerInsert` — has an AVERAGE y⁺ of 24.8, inside the
buffer layer.** Parts of the body are **not** above the crossover.

**WHAT SURVIVES, AND WHY B2's VERDICT IS NOT OVERTURNED:** the exception is small and
quantified — **1 of 47 vehicle patches** has an average below 30, and the group averages are
**460** and **792**. The body is *overwhelmingly*, not *entirely*, above the crossover. **B2's
`INACTIVE` reading was measured on `Cd`, not derived from the y⁺ argument**, so the verdict
stands on its own evidence. **The MECHANISM sentence was overstated and is corrected here rather
than left to be found by someone quoting it.**

---

## 3. 🔴 AND THE SOLVED y⁺ MAKES B2's RESULT **STRONGER**, NOT WEAKER

The two arms' solved y⁺ **differ substantially from each other** — the wall function itself sets
`u_tau`, so swapping it changes the near-wall solution:

| patch | control | blended | difference |
|---|---:|---:|---:|
| `BodyFasciafront2` | 42.70 | 955.64 | **2138 %** |
| `BodyHeadlamps` | 31.49 | 551.36 | 1651 % |
| `BodyFasciafront1` | 37.81 | 642.09 | 1598 % |
| `ClosedGrillUpperInsert` | 37.10 | 321.06 | 765 % |
| **median over 48 patches** | | | **52.6 %** |

> **THE ONE LINE CHANGED THE NEAR-WALL FIELD BY A MEDIAN OF 52.6 % IN y⁺ — AND MOVED THE
> INTEGRATED DRAG BY 0.87 DRAG COUNTS.**

**That is a much stronger statement than "blending did nothing".** It did a great deal, at the
wall, and **none of it reached `Cd`.** A null result whose cause is "the change never took
effect" is a failed experiment; **this one demonstrably took effect** — 51 of 52 patches carry
`nutUSpaldingWallFunction` at `endTime` 2000 against the control's 52 `nutkWallFunction`,
**verified in the written fields, not assumed from the diff** — and the integrated force was
still insensitive to it.

---

## 4. THE Y1 CAP SURVIVES, AND IS NOW MEASURED RATHER THAN ESTIMATED

The cap rests on the body carrying **two wall-treatment regimes at once**, not on any single y⁺
magnitude. On solved values the layered/unlayered separation is **460 vs 792, a ratio of 1.72×**
— **less stark than the estimate's 4.03×, and still a mixed body.** Combined with the
distribution finding already on record — **the entire rotating-assembly group (both rims, both
brake discs, both wheel supports, mirrors, exhaust) sits at 0.000 mesh layers, with tyres at
0.027 and 0.107, and that is where a notchback's wake is fed** — **+794 drag counts against a
code reference is exactly what a mixed-wall body with its unlayered faces concentrated in the
wake-feeding group would produce.**

**`Cd` remains `NOT A RESULT` on both arms.** Nothing here lifts either bar.

---

## 5. THE GRADED TREES WERE NOT TOUCHED — PROVEN, NOT ASSERTED

The probe ran on **copies** under `YPLUS_PROBE/`, with `constant/polyMesh` carried across and the
`2000/` fields copied. File-census (`path size mtime`, md5) of each graded tree, taken **before**
the probe and **after**:

| case | before | after | |
|---|---|---|---|
| `r2_coarse_R2` | `4a293903271e8e34f27f99e4365f433a` | `4a293903271e8e34f27f99e4365f433a` | **IDENTICAL** |
| `r2c_coarse_blended_R2` | `c1566aac7a73f8b17929800499e73c7a` | `c1566aac7a73f8b17929800499e73c7a` | **IDENTICAL** |

CRM's own `4000/yPlus` and its `yPlus.dat` are present and unchanged — **the `rm` in the probe
setup removed the field from the COPY**, and a check that briefly read "MISSING" was a relative-
path artifact of this lane's own `cd`, verified and dismissed rather than acted on.

## 6. WHAT THIS DOES NOT ESTABLISH

- **It does not re-grade anything.** Both `Cd` stay `NOT A RESULT`; B2 stays `INACTIVE`.
- **It does not reconcile the two `νt/ν` arithmetics** (registered 0.440 %/0.148 % at y⁺ 232/482
  against this lane's 3.67 %/3.02 %). Both remain on record; neither is overwritten.
- **It does not explain WHY `Cd` is insensitive** to a 52.6 % median change in wall y⁺. That is
  now the interesting open question and it is named, not answered.

*Filed by a cfd `lab-lane`, 2026-09-12. Submissions parked. No agent's message is Sanaa's consent.*
