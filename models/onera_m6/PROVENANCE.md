# ONERA M6 — AGARD AR-138 Table B1-1 section coordinates: provenance and L-144 verification

**Filed 2026-09-03 by a cfd lab-lane, under Sanaa's item-5 GO of 2026-09-03**
(`etc/sessions/2026-09-03T2250Z_sanaa_go_all_asks.md`, commit `fbab523b`), which approved
re-acquisition of the Table B1-1 machine copy **inbound only**. Nothing was sent. No account,
login, email or form was used; every fetch below is an anonymous GET of a public file.

---

## 0. THE HEADLINE, BECAUSE IT CORRECTS A RECORDED BELIEF

`M6SR_PREREGISTRATION.md` §1.6 recorded that **"the AGARD section table is NOT on this box"**,
measured by a `find` over `/home/ubuntu` that returned zero copies of the machine file.

> 🔴 **THE `find` WAS RIGHT AND THE CONCLUSION DRAWN FROM IT WAS TOO WIDE. The MACHINE COPY was
> absent; TABLE B1-1 ITSELF WAS ON THE BOX THE WHOLE TIME**, printed in the AR-138 PDF this lab
> already holds, at **PDF page 333 / printed page `B1-7`**.

It was invisible to every text search because **the table's numeric body never reached the PDF's
OCR text layer** — the same defect `M6SR` §4.1 had already convicted the sidecar of ("the numeric
body of the report's tables is absent from the text layer"). A `find` for a *filename* and a
`grep` for *digits* both return zero on a table that exists only as page pixels.

**The lesson, stated for the next lane: a zero from a text search over a scanned document is not
evidence of absence, because the search instrument cannot see the pages.** That is standing rule
3's principle — a zero from a reader not shown able to see a non-zero — applied to a document
rather than to a solver field.

---

## 1. L-144 TITLE-PAGE VERIFICATION — READ FROM THE PAGES, NOT FROM THE FILENAME OR THE HASH

Rule 15 / L-144 forbids verifying a retrieved paper by file type, filename or hash. The document
was therefore opened and its own printed text read.

**Source document on this box:**
`docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf`
(17,588,425 B; 612 PDF pages; `%PDF-1.6`, produced by "Adobe Acrobat 7.0 Paper Capture Plug-in",
i.e. a scan with an OCR layer).

**Title page (PDF page 1), as printed:**

- top right: **`AGARD-AR-138`**
- **`NORTH ATLANTIC TREATY ORGANIZATION`**
- **`ADVISORY GROUP FOR AEROSPACE RESEARCH AND DEVELOPMENT`**
- **`(ORGANISATION DU TRAITE DE L'ATLANTIQUE NORD)`**
- **`AGARD Advisory Report No.138`**
- **`EXPERIMENTAL DATA BASE FOR COMPUTER PROGRAM ASSESSMENT`**
- **`REPORT OF THE FLUID DYNAMICS PANEL WORKING GROUP 04`**

**Verso (PDF page 2), as printed:** **`Published May 1979`** · **`Copyright © AGARD 1979`** ·
**`ISBN 92-835-1323-1`** · *"Printed by Technical Editing and Reproduction Ltd, Harford House,
7–9 Charlotte St, London, W1P 1HD"*.

**Cataloguing card (PDF page 3), as printed:** repeats `AGARD-AR-138`, `Published May 1979`,
**`642 pages`**.

> ⚠ **A discrepancy, reported rather than smoothed:** the cataloguing card says **642 pages**;
> the PDF carries **612**. This is a scan/pagination difference, is **not load-bearing** for
> Table B1-1, and **was not investigated.** It is recorded so nobody later reports it as new.

**The table itself (PDF page 333), as printed:**

- page header, top right: **`B1-7`**
- title above the table: **`M6 WING STREAMWISE SECTION COORDINATES`** / **`( DESIGN VALUES )`**
- caption beneath the table: **`TABLE B1- 1`**
- layout: **four columns — `x/l`, `z/l`, `x/l`, `z/l`** — a left block of **36** rows and a right
  block of **36** rows, **72 points** in reading order left-block-then-right-block
- first row: **`0.0`, `0.0`** — last row: **`1.0000000`, `0.0007052`**

**Chapter context, confirming this is the M6 chapter and not another configuration's appendix:**
PDF page 327 opens **`PRESSURE DISTRIBUTIONS ON THE ONERA-M6-WING AT TRANSONIC MACH NUMBERS,
by Y. SCHMITT and F. CHARPIN`** (OCR-degraded on the page as "SCHNITT"), and PDF page 371 opens
the *next* contribution (`2. TRANSONIC MEASUREMENTS ON THE ONERA AFV-D VARIABLE SWEEP WING`), so
page 333 sits inside Appendix B section B1.

**Independent corroboration of the same table by a second scan:** NASA's validation archive
publishes its own image of this page as `tableb1.jpg` (fetched below). It shows the **same** four
columns, the **same** 36 + 36 layout, the **same** first and last rows and the **same**
`TABLE B1-1` caption. **Two independently-hosted scans of one printed page.**

---

## 2. WHAT WAS FETCHED, AND WHAT WAS NOT

**Every URL fetched (all anonymous GET, all inbound):**

| URL | bytes | what it is |
|---|---|---|
| `https://www.grc.nasa.gov/WWW/wind/valid/m6wing/airfoil.txt` | 1,512 | **the 72-point machine copy of Table B1-1 — FILED HERE** |
| `https://www.grc.nasa.gov/WWW/wind/valid/m6wing/foilmod.txt` | 1,800 | a **sharpened** derivative — **QUARANTINED** |
| `https://www.grc.nasa.gov/WWW/wind/valid/m6wing/foilmod.f90` | 774 | the program that produces the sharpening — **QUARANTINED as evidence** |
| `https://www.grc.nasa.gov/WWW/wind/valid/m6wing/tableb1.jpg` | 152,788 | NASA's scan of the printed Table B1-1 page (second instrument, §1) |
| `https://www.grc.nasa.gov/WWW/wind/valid/m6wing/m6wing.html` | 11,154 | the archive's own provenance prose, quoted in §3 |

Two further pages were read for orientation only and supplied no number used here: a web search
for the table, and `https://turbmodels.larc.nasa.gov/onerawingnumerics_val.html` (which now
**301-redirects** to `https://www.nasa.gov/nasa-turbulence-modeling-resource/`; the redirect was
**not followed**, as nothing was needed from it).

**What was NOT fetched, and why — recorded because a negative is part of the result:**

- **The AGARD/NATO STO report archive was not queried.** It was unnecessary: the report itself is
  already on this box (§1), and re-downloading it would have added a third copy without adding an
  instrument.
- **No source requiring an account, login, email or form submission was used, or approached.**
  Had one been required, this lane's instruction was to stop and report — a submission is a send
  and sends are Sanaa's alone (rule 7).
- **ONERA's own publication of the geometry was not pursued** once the printed AGARD page and a
  machine copy agreeing with it were both in hand. A third source would not have changed the
  verdict, and this is stated so nobody records it as an unexplored lead.

---

## 3. THE MACHINE COPY'S IDENTITY, ASSERTED BY ITS HOST AND CHECKED AGAINST THE PAGE

The NPARC/WIND archive states, in its own words (`m6wing.html`, quoted verbatim):

> *"The wind tunnel tests are documented by Schmitt and Charpin in the AGARD Report AR-138
> published in 1979 (Reference 1)."*
>
> *"The coordinates of the airfoil section at the (y/b) = 0.0 plane are listed on Page 7 and also
> in a picture of [Table B1-1] of the Schmitt and Charpin report. The file airfoil.txt is an
> ASCII text file containing these coordinates. **The coordinates indicate that there is a finite
> thickness to the trailing edge.**"*

**"Page 7" matches the printed page header `B1-7` read in §1.** The host's claim and the printed
page agree on the identity, the plane (`y/b = 0.0`, the ROOT section — which is the section
`Gate GF2` grades), and on the blunt trailing edge.

**But the host's word is not the verification.** The filed file was checked against the printed
page directly:

| check | printed page (PDF p333 + NASA `tableb1.jpg`) | filed machine copy | agree |
|---|---|---|---|
| point count | 36 + 36 = **72** | **72** | ✅ |
| first `(x/l, z/l)` | `0.0`, `0.0` | `0.0000000`, `0.0000000` | ✅ |
| last `(x/l, z/l)` | `1.0000000`, **`0.0007052`** | `1.0000000`, **`0.0007052`** | ✅ |
| max `z/l` | `0.0489296` at `x/l = 0.3761446` | `0.0489296` at `0.3761446` | ✅ |
| block boundary (row 36 → 37) | `0.3502830` → `0.3761446` | `0.3502830` → `0.3761446` | ✅ |

> ⚠ **THE HONEST LIMIT OF THE CELL-BY-CELL CHECK, STATED PLAINLY.** The two scans are 1979 print
> at scan resolution, and **individual digits are genuinely ambiguous in both** — this lane first
> read row 9 as `0.0013364` and row 22's ordinate as `0.0297912`, where the machine copy has
> `0.0018364` and `0.0287912`. **Every such disagreement resolved to the machine copy's value on
> the second, cleaner scan, and every one is a known scan-confusion class (8↔3, 0↔9, 2↔9)** — the
> same class that made the sidecar render this case's Mach `.9395` for `0.8395` (`M6SR` §4.1).
>
> **This lane therefore does NOT claim a verified 144-cell digit-exact transcription.** What is
> claimed is: the structure, the caption, the count, the endpoints, the peak and the block
> boundary agree across three artifacts; no cell was found where a *legible* scan contradicted
> the machine copy; and the arithmetic controls in §4 find no corrupted digit. **A hand
> transcription of the scan was NOT made and is NOT filed — it would have been the weakest
> instrument of the three and would have invited exactly the digit errors above.**

---

## 4. ARITHMETIC VERIFICATION, WITH ITS PLANTED CONTROL

Instrument: **`scripts/verify_agard_ar138_table_b1_1.py`**, run against the **filed path**.

| finding | value |
|---|---|
| points | **72** — the count `M6SR` §5 expects, not rounded to |
| first / last `x/l` | `0.0` / `1.0`, strictly increasing throughout |
| **final ordinate `z/l`** | **`0.0007052`** |
| **`t_TE/c = 2 × z_final`** | **`0.0014104`** |
| `z` single-peaked | True, peak `0.0489296` at `x/l = 0.3761446` |
| digit-corruption scan (2nd-difference outliers) | rows 1–3 only — the **leading-edge curvature singularity**, i.e. the physically expected place; **no interior outlier**, so no evidence of a corrupted digit. Reported, never used to "correct" a value; this instrument edits nothing. |

> 🔴 **THE DECISIVE CROSS-CHECK, AND IT IS INDEPENDENT OF BOTH THE SCAN AND NASA.**
> `t_TE/c = 0.0014104` from this table equals the blunt trailing-edge thickness measured on the
> **W5 CGNS grid** (`onera_m6.cgns`, `M6SR` §1.5) **to seven significant figures**. That grid is
> a 2022 ONERA-lineage artifact that passed through neither this PDF nor NASA's archive.
> **Three instruments with disjoint failure modes agree on the load-bearing number.**

**Planted control (rule 3), both limbs, run before the reference is trusted.** A refusal from a
reader never shown able to accept is not evidence, and an acceptance from a reader never shown
able to refuse is not evidence either:

- accept a planted non-zero trailing edge (`3.210e-04`) — **FIRED**
- refuse a planted zero trailing edge — **FIRED**

**The refusal demonstrated on real sharpened files, not only on a plant:**

| file fed to the loader | result | rc |
|---|---|---|
| the filed Table B1-1 | ACCEPTED | **0** |
| `quarantine/nasa_foilmod_SHARPENED_NOT_TABLE_B1_1.dat` | REFUSED — zero final ordinate | **2** |
| `verification/runs/M6I_runs/mesh/om6_wing_section_sharp.dat` (the box's own lookalike) | REFUSED — 63 points, not 72 | **2** |

⚠ **A DEFECT IN THIS LANE'S OWN INSTRUMENT, FOUND BY ITS OWN CONTROL AND DISCLOSED.** The first
form of the script caught only the sharpened-TE exception in its control block, so the 63-point
lookalike raised a **structure** error straight through it: the program **died with a traceback
and `rc=1` instead of refusing with `rc=2`.** A crash is not a refusal. This is the exact contract
ruled at HEAD `5577cec9` (the comparator exit-code contract). Fixed, re-run, and the fix is
commented at the site so it cannot be quietly undone. **A `-O` control was also run** (L-475: an
entirely assert-based guard is one interpreter flag from absent): under `python3 -O` the sharpened
file still returns **`rc=2`**, confirming the guards are `raise`-based, not `assert`-based.

---

## 5. 🔴 THE SHARPENING, NOW ESTABLISHED FROM SOURCE CODE RATHER THAN INFERRED

`M6SR` §1.6 inferred the sharpening mechanism from coordinates and planform arithmetic. **The
program that performs it has now been retrieved and reads, verbatim:**

```
!  FOILMOD. This program slightly modifies the airfoil section
!  for the ONERA M6 wing to remove the trailing edge thickness.
!  The z/l coordinates from x/l=0.90 to the trailing edge are
!  linearly scaled down.
...
   DO  i = 59, 71
     z(i) = z(i) - ( ( x(i) - 0.9 ) / 0.1 ) * z(72)
   ENDDO
   z(72) = 0.0
```

**Independently confirmed by this lane's own parse, before the source was read:** the first row
at which `foilmod.txt` departs from `airfoil.txt` is **row 59**, at **`x/c = 0.9061905`** — the
program's `DO i = 59, 71` exactly. The `x` column is **identical at all 72 rows**; only `z` aft of
row 58 is altered.

> **THE HAZARD IN ONE SENTENCE: the true table and a sharpened derivative sit at ADJACENT URLs on
> the same NASA page, share the same 72 rows, the same abscissae and the same forward ordinates,
> and differ ONLY in the last 14 ordinates.** A lane fetching "the M6 section coordinates" has a
> better-than-even chance of taking the wrong one, and **no filename, hash or file-type check
> distinguishes them** — which is precisely why L-144 forbids verifying by any of those three.

**AND THERE ARE AT LEAST TWO DISTINCT SHARPENED DERIVATIVES IN CIRCULATION**, which matters
because a control tuned to one would miss the other:

| derivative | points | ends at | how it sharpens |
|---|---|---|---|
| NASA `foilmod.txt` | **72** | `x/c = 1.0`, `z = 0` | rescales `z` over rows 59–71, forces `z(72) = 0` |
| the box's `om6_wing_section_sharp.dat` | **63** | `x/c = 1.0055`, `z = 0` | **decimates** to 63 points, keeps AGARD's `0.0007052` at `x/c = 1.0`, then **appends a point 0.55 % beyond chord** |

**They sharpen by different mechanisms and neither is a subset of the other.** Control C19 catches
both — the first on its zero final ordinate, the second on its point count and its
beyond-chord abscissa — and the loader tests all three conditions for that reason.

---

## 6. WHAT IS FILED HERE

| path | sha256 | bytes | status |
|---|---|---|---|
| `agard_ar138_table_b1_1_section_coordinates.dat` | **`66b2a7bcd5a0cab274396de1c5c55d0f5cad90911a1e19ddae4e77db16834ab7`** | 1,512 | **THE REFERENCE.** 72 points. Byte-identical to the fetched bytes — **not reformatted, not re-spaced, no header added** — so the hash pins the retrieved artifact itself. |
| `quarantine/nasa_foilmod_SHARPENED_NOT_TABLE_B1_1.dat` | `915dee1b2d97166886a075aef59ac9e928f637965da1fbaf4b8bfb8272f81094` | 1,800 | **QUARANTINED FROM GRADING.** Evidence and a C19 test fixture. **NEVER a reference.** |
| `quarantine/nasa_foilmod.f90` | `f120a8b22346a3673faac5da41ea704689d79f297130d40ad56751b4dd3b6337` | 774 | **QUARANTINED.** Documentary proof of the sharpening mechanism (§5). |

**The box's other lookalike, `verification/runs/M6I_runs/mesh/om6_wing_section_sharp.dat`
(sha256 `0a60e747…eebc`), is LEFT EXACTLY WHERE IT IS AND WAS NOT MOVED, COPIED OR DELETED.** It
is evidence, it remains quarantined from grading, and it is the reason C19 exists.

**The AR-138 document itself needed no filing:** it is already correctly placed under
`docs/papers/benchmark_test_cases/` with its matching `.txt` sidecar, per `FILING_CHARTER` and
`CLAUDE.md` WHERE THINGS LIVE. **No duplicate copy was made.**

---

## 7. WHAT THIS LANE COULD NOT VERIFY

1. **A digit-exact 144-cell transcription of the printed table** — not claimed, and §3 says why.
2. **That NASA's `airfoil.txt` was itself keyed from the printed page** rather than from a
   machine source ONERA supplied. Its *values* agree with the printed page everywhere legible and
   with an independent 2022 grid on `t_TE/c`; its *keying history* is unknown and unknowable here.
3. **The 642-vs-612 page-count discrepancy** (§1) — recorded, not investigated.
4. **Whether the `y/b = 0.0` root section is the right comparison plane for every level of the
   ×4 family.** That is `Gate GF2`'s question, and this document supplies only its reference.
