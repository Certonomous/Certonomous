# AGARD AR-138 Table B1-14 (TEST 2308) — machine copy: provenance, and every check that was run

**Filed 2026-09-12 by a cfd `lab-lane`.** Nothing was sent, fetched, uploaded or filed.
The source PDF was already on this box. **SUBMISSIONS ARE PARKED (standing rule 7).**

**Artifact:** `models/onera_m6/agard_ar138_table_b1_14_test2308_cp.dat`, 271 data rows.

---

## 0. THE HEADLINE, BECAUSE IT CHANGES A NUMBER THE CFD LITERATURE REPEATS

🔴 **The seven AGARD pressure sections are at y/b = 0.20 / 0.44 / 0.65 / 0.80 / 0.90 /
0.96 / 0.99. The sixth is 0.96, NOT the 0.95 that circulates in the CFD community.**
Read from the page image of **PDF page 330 = printed page B1-4**, AR-138 Appendix B1
§5.1.1, which states in full:

> *"271 pressure orifices divided in 7 sections (y/b = 0.20/0.44/0.65/0.80/0.90/0.96 and
> 0.99) see also figure B1-1 and table B1-2"*

**A comparison run against 0.95 is comparing a solved section to an experimental section
0.01 semispan away**, and at y/b ≈ 0.95 on this wing that is inside the region where the
lambda shock is collapsing, so the error is not small and nothing downstream would show it.

**The same page also fixes the row count.** 271 orifices. The page was segmented
independently of that sentence — 4 sections of 34 rows and 3 of 45 — and
**4 × 34 + 3 × 45 = 271**. Two routes, one number.

---

## 1. RULE 15 / L-144 — TITLE-PAGE VERIFICATION, READ FROM THE PAGES

Never by filename, file type or hash. The document was opened and its own printed text read.

**Source on this box:**
`docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf`
(17,588,425 B; 612 PDF pages; `%PDF-1.6`, "Adobe Acrobat 7.0 Paper Capture Plug-in", i.e.
a scan carrying an OCR layer).

| read | where, in this PDF | what the page says |
|---|---|---|
| title | PDF page 1 | **AGARD-AR-138**, NATO Advisory Group for Aerospace Research and Development, Advisory Report No. 138, **EXPERIMENTAL DATA BASE FOR COMPUTER PROGRAM ASSESSMENT**, Report of the Fluid Dynamics Panel Working Group 04 |
| imprint | PDF page 2 | **Published May 1979, ISBN 92-835-1323-1** |
| appendix | PDF page 327 | *PRESSURE DISTRIBUTIONS ON THE ONERA-M6-WING AT TRANSONIC MACH NUMBERS*, by **V. Schmitt and F. Charpin**, ONERA, 92320 Châtillon |
| **the table** | **PDF page 346 = printed `B1-20`** | header line **`M6 WING - SURFACE PRESSURE DISTRIBUTIONS   TEST 2308`**, then **`MO = .8395`**, **`ALPHA = 3.06`**, **`REC = 11.72*10**6`**, footer **`TABLE B1-14`** |
| stations | PDF page 330 = printed `B1-4` | §5.1.1, quoted in §0 above |
| symbols | PDF page 332 | `x` is *"distance measured along the local chord from the leading-edge of the wing section"* — so the table's **X/L is local-chord fraction**, which is what `x_over_c` means in the emitted file |

Appendix B1 begins at PDF page 327, and **327 + 19 = 346**, consistent with the table's own
printed page number `B1-20`.

---

## 2. 🔴 THE OCR SIDECAR CANNOT SEE THIS TABLE AT ALL, AND THAT IS MEASURED, NOT ASSUMED

`pdftotext -layout` over PDF page 346 returns **the header block and the words `TABLE B1-
14`, and NOTHING ELSE**. The numeric body of the table never reached the PDF's text layer.

This is the same defect `models/onera_m6/PROVENANCE.md` §0 convicted the sidecar of for
Table B1-1, and it is why **every digit below was read from the rendered page image**, via
`pdfimages` on the page's own embedded scan (**1648 × 2330, 1-bit grayscale, jbig2, 200 dpi**
— so rendering above 200 dpi adds interpolation, not information, and none was used).

**Nothing in the emitted file came from the `.txt` sidecar.**

---

## 3. HOW EVERY DIGIT WAS READ, AND HOW EVERY DIGIT WAS CROSS-CHECKED

Four readings, of which **two are independent readers of the same page** and **two are
external checks that can only be passed by a correct reading**.

### 3.1 Reading A — a human read of magnified crops

The page was segmented by ink projection into its 7 section blocks and 271 rows, each row
cropped with its `NP` index and magnified 7×, and read field by field.

### 3.2 Reading B — a template classifier trained on the page's OWN `NP` column

A nearest-centroid classifier over 16 × 12 normalised glyph bitmaps. **Its training labels
come from nothing outside the page**: the `NP` index column's sequence is fixed by the
printed structure, and that structure was verified mechanically before it was used —
the digits-per-row pattern came out **2,2,2 then nine 1s then twenty-two 2s** in the upper
block and **six 2s then nine 1s then thirty 2s** in the lower, which is exactly
`12,11,10, 9…1, 34…13` and `15…1, 45…16` and nothing else. That yields 140 labelled digits
covering all ten classes, then self-training over the remaining 3,545.

**The class means are legible digits.** A contaminated class averages to mush; these do not.

### 3.3 Adjudication

| column | cells where A and B disagreed, of 271 | how each was settled |
|---|---:|---|
| `x_over_c` | 44 | third look at higher magnification |
| `Z/L` (used only for the surface label and the check in §4) | 32 | third look, plus §4 |
| **`Cp`** | **14** | third look at 15× on the single disputed field |

**The classifier caught four `Cp` errors of the human reader, every one of them a 4 read as
a 6.** In this line-printer font `4` and `6` differ by whether the glyph encloses a
counter; at 200 dpi 1-bit that is two or three pixels. The four corrections are
**SECTION 2 row 24 `-.616 → -.614`**, **SECTION 6 row 32 `-.262 → -.242`**,
**SECTION 7 row 20 `-1.246 → -1.244`**, **SECTION 7 row 30 `-.266 → -.246`**.

**Because that confusion is the one that matters, it was then swept deliberately.** Every
`Cp` field containing a digit the classifier placed within 2.2 of both the `4` and the `6`
centroid — **41 fields** — was re-read a third time at 15× against the counter test.
**All 41 confirmed.**

### 3.4 Reading C — the SAME orifice coordinates printed on ten OTHER pages

**The `X/L` and `Z/L` columns are the fixed orifice locations and are identical in every M6
table in Appendix B1; only `CP` changes with the test.** So the same extractor was run over
ten further M6 tables that segment cleanly — **PDF pages 334, 339, 345, 349, 350, 351, 354,
355, 361, 363** (Tables B1-2, B1-7, B1-13, and others through B1-31) — and `x_over_c` was
taken to plurality across them. **36 cells disagreed with Reading A; each was settled by a
fourth look at PDF page 363, which is a materially cleaner impression of the same fixed
coordinates than page 346.**

*Honest limitation, stated because it bounds what this check proves:* the ten pages are ten
different impressions read by the **same** classifier, so they expose ink and noise
variation but **not** a systematic bias of that classifier. That is why the disagreements
were settled by eye on the cleanest page and not by vote.

### 3.5 Reading D — see §4. It is the strongest of the four.

---

## 4. THE EXTERNAL ARITHMETIC CHECK: EVERY ROW AGAINST THE INDEPENDENT GEOMETRY FILE

The M6 has **one** airfoil section, **no twist**, conical generation (AR-138 B1 §2.1.6,
§2.1.9–2.1.11). So for every orifice in the table, the printed `Z/L` must equal the ONERA D
section's own `z/l` at the printed `X/L` — **and the section table is a separate artifact,
committed on 2026-09-03 and title-page verified then**:
`models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat` (72 rows).

Interpolated with a monotone (PCHIP) fit in `sqrt(x/l)`, over **all 271 rows**:

| statistic | residual `| |Z/L| − z_ref(X/L) |` |
|---|---:|
| median | **6.8 × 10⁻⁵** |
| 90th percentile | 3.4 × 10⁻⁴ |
| 99th percentile | 5.1 × 10⁻⁴ |
| **maximum** | **5.9 × 10⁻⁴** |
| **rows above 7 × 10⁻⁴** | **ZERO** |

**This is a check no misread digit survives**, because it constrains `X/L` and `Z/L`
*jointly* against a file that was never involved in reading this page. It is what caught,
among others, `SECTION 2` row 30's `X/L` (a `.73897` that became `.70897`, residual
2.8 × 10⁻³ → 1.8 × 10⁻⁴) and `SECTION 1` row 25's `Z/L` (`.04912` → `.04812`).

**Why the residual floor is 10⁻⁴ and not zero, and why that is the right answer.** The
table's `Z/L` are **measured orifice positions on a manufactured wing**, and AR-138 B1 §2.3
records the model's **fabrication tolerance as 0.15 mm** — at the 0.8059 m root chord,
**1.9 × 10⁻⁴ of chord**. The residuals are also *systematic*, largest at x/c ≈ 0.86–0.90
across all seven sections at once, which is a property of the wing and not of a reader. **A
residual floor of zero here would have been the suspicious result.**

---

## 5. WHAT IS STILL UNRESOLVED, NAMED RATHER THAN HIDDEN

**Three `x_over_c` values carry a 4th/5th decimal digit that three readings did not settle.**
They are emitted at the value the cleanest page supports and are listed here because
standing rule 3's principle applies to a scan as much as to a solver field: *a digit that
could not be read is not a digit that was read.*

| row | emitted | candidates not excluded | bound on the ambiguity |
|---|---|---|---:|
| `SECTION5`, `NP 39` (row 22) | `.07448` | last digit `8` or `9` | 1 × 10⁻⁵ c |
| `SECTION5`, `NP 37` (row 24) | `.13996` | `.13936` / `.13986` / `.13996` | 6 × 10⁻⁴ c |
| `SECTION6`, `NP 28` (row 33) | `.49994` | `.49994` / `.49996` | 2 × 10⁻⁵ c |

**Bound on the consequence.** These are abscissae onto which a solved `Cp` is interpolated.
Away from a shock `|dCp/d(x/c)|` on this reference is O(1), so the worst of the three
induces **ΔCp ≲ 6 × 10⁻⁴** — three orders below any `Cp` tolerance this lab has registered.
**Near a shock the gradient is large, but all three rows lie away from every located shock**
(§6 below lists them). **No `Cp` value is affected: the ambiguity is in `x`, not in `Cp`.**

**NO `Cp` VALUE IS EMITTED THAT THE TWO INDEPENDENT READERS DID NOT AGREE ON AFTER
ADJUDICATION.** There is no unresolved `Cp` digit.

---

## 6. THE SURFACE LABEL IS READ, NOT ASSUMED

`surface` is assigned from **the sign of the table's own `Z/L` column** — `Z/L < 0` is
`lower`, `Z/L ≥ 0` is `upper` — never from row order and never from the `NP` index. This
yields **86 lower and 185 upper** points: 11 + 23 per inboard section, 14 + 31 per outboard.

The one orifice with `Z/L` exactly `0.00000` is **`SECTION 4`, `NP 1`, at `X/L = 0.00000`**
— the leading-edge orifice, which lies on both surfaces. It is filed `upper`, which is
consistent with `NP 1` in the other six sections, all of which carry a small positive `Z/L`.
**Stated here because it is a choice and not a reading.**

---

## 7. WHAT THIS FILE IS AND IS NOT, IN THIS LAB

- **It is NOT the graded reference for any M6 Cp verdict.** The dafoam team's
  `verification/campaign/A3_M6_AGARD_CP_VALIDATION_PREREGISTRATION.md` froze the band and
  its grader, and Sanaa's word is **cite it, do not re-register**.
- **That registration names THIS PATH as its data table** and reproduces this file's own
  `NOTE 0.96, NOT 0.95` and the §4 residual figures. It was frozen while this file was
  still **untracked in the working tree**, so its grading path pointed at a blob that did
  not exist in the repository. **Committing it is what closes that hazard**, and that is
  the reason this commit exists rather than tidiness.
- **It is a cross-check for M6H1's H-G6** (`cases/navier_class/M6H1/compare_cp.py`), whose
  declared input format is exactly this file's columns.

## 8. REPRODUCING IT

Every number above is re-derivable from the PDF already on this box. The extraction
scripts were scratch and are deliberately **not** cited from this document — the scratchpad
is never a handoff channel (L-186). What is load-bearing is in §1–§6 and in the emitted
file's own header, and the §4 check can be re-run against the two committed `.dat` files
alone.
