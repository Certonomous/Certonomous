# M6I — ONERA M6 by IMPORT: provenance, AGARD title-page verification, and geometry comparison

**Case id: `M6I`** (ONERA M6, import route). Team: cfd. Written 2026-09-01 by a cfd lane under
`cfd-supervisor`, on Sanaa's directive `etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md`
(commit `f4c8e466`) **§6 option 1** — *"use a published M6 grid family … Import, verify the
geometry against the AGARD definition, run the three levels."*

**THIS FILE IS NOT A PRE-REGISTRATION.** Everything in it is a measurement already taken. It
registers no gate, no threshold, no cap and no label, and nothing in it may be read as one. The
ladder's gates live in `M6I_PREREGISTRATION.md` and are frozen there.

**NO SOLVER HAS RUN UNDER THIS CASE.** All compute recorded here is instrument construction —
document retrieval, geometry measurement, and a mesh-generator smoke test — and no flow field
exists.

---

## 0. REGISTER SEARCH BEFORE THE FREEZE (L-427), AND WHAT IT RETURNED

`grep -niE 'onera|\bm6\b|agard|butterfly|tip cap|su2|import|plot3d'` over
`docs/NUMERICS_KNOWLEDGE.md`, `docs/LESSONS.md`, `docs/standards/MESH_STANDARD.md`,
`docs/MESH_STANDARD.md` and `verification/campaign/`. **It did not return nothing.** What it
returned, and what each item does to this work:

| register entry | what it holds | effect here |
|---|---|---|
| **`N-C6`** (`docs/NUMERICS_KNOWLEDGE.md:4682`) | a structured butterfly tip cap on a **sharp** TE has a non-orthogonality floor that refinement makes **worse**: 81.5834° → 82.0645° rising to ~82.07°, severe fraction rising **10.7×** while cells rise **1.31×**; the mechanism is the strip-to-core arc ratio ~16:1 set by a section half-thickness going to **zero** | **Its premise is falsified for the real M6 by §3 below.** The AGARD design section does **not** go to zero at the TE. `N-C6` remains correct for a sharp TE; the M6 is not one. |
| **`F13`** (`F13_ONERA_M6_PREREGISTRATION.md`, `F13_RESULTS.md`) | R0 `GATE FAIL`, max non-orthogonality 84.64/86.02/86.78° rising with refinement; case `BLOCKED` on §5 admission; **no solver ever ran**; §5 states *"the M6 tip is a flat cut, so the cap is geometry, not a simplification"* | **That sentence is contradicted by the primary** (§3 below, AR-138 2.1.13). Recorded here; F13's verdicts are **not** revisited by this file and stand exactly as graded. |
| **`L-427`** | search the registers **before** the freeze and record what came back, including nothing | this section |
| **`L-430`** (landed 2026-09-01, hours before this work) | a generator parameter that does not scale with the ladder builds three clean meshes and a meaningless observed order; cheap check — a 3-D family's total cell-count ratio must be `r³`; max non-orthogonality must be roughly invariant | **Directly answered by the import route's architecture** (§5): the family comes from **one** generator call plus a coarsening program, so no parameter can fail to scale. The `r³` check is applied and reported in §5. |
| **`MESH_STANDARD.md` §3.1** | 70° max non-orthogonality hard gate, read off the reported **maximum**, never off `checkMesh`'s own OK line | applied in §5; the published demo family **fails** it |
| **`F1_M6_TOPOLOGY_RULING_2026-08-25.md`** and its amendment, `F1_M6_CORRECTION2_2026-08-25.md` | describe the obstruction as *"a fixed fraction of the mesh"*; `N-C6` measured that the fraction is not fixed but rising | noted; neither is disturbed here |

**Nothing else in the registers bears on an imported M6 grid, a PLOT3D import path, or AGARD
AR-138.** Searched for `su2`, `plot3d`, `cgns`, `import`, `external mesh`, `third party`:
**zero hits in `docs/NUMERICS_KNOWLEDGE.md` and `docs/LESSONS.md`.** This is the lab's first
imported external grid family.

---

## 1. NETWORK EGRESS — WHAT WAS FETCHED, AND WHAT WAS NOT SENT

**Inbound only.** Sanaa's §6 orders a published grid to be imported, which requires retrieval.
**CLAUDE.md rules 7 and 8 are not relaxed by that and were not relaxed here.** No account was
created, no steward contacted, no issue opened, no forum post made, no file uploaded, no link
shared. **Nothing left this box.** The complete outbound traffic of this work is HTTP GET.

Every retrieval below records the exact URL, the UTC retrieval timestamp, the HTTP code, the
byte size and the sha256. The manifest is reproduced in full so the provenance can be
re-derived without the fetcher.

### 1.1 The primary reference

| file | URL | retrieved (UTC) | code | bytes | sha256 |
|---|---|---|---|---|---|
| `agard_1979_ar138_experimental_data_base.pdf` | `http://web.archive.org/web/20230507000401if_/https://www.sto.nato.int/publications/AGARD/AGARD-AR-138/AGARD-AR-138.pdf` | 2026-09-01T16:38:16Z | 200 | 17,588,425 | `a96a73304c8328bd97c828cead2df9326675fd2340230d7e81fcf9f8191e7ffb` |

**A FIRST ATTEMPT FAILED AND IS RECORDED BECAUSE IT IS THE POINT OF THE RULE.** The direct
NATO STO URL `https://www.sto.nato.int/publications/AGARD/AGARD-AR-138/AGARD-AR-138.pdf`
returned **HTTP 302 then 403**, delivering **4,547 bytes of HTML** into a file named
`AGARD-AR-138.pdf`, sha256
`179527b5f5d25474f75d1022d5c97d2d4dec27bd899b6079ae9dc458001e6246`. **A filename-based or
hash-manifest-based check would have recorded that as the report.** `file(1)` reported
`HTML document, ASCII text` and it was discarded. This is L-144's failure mode caught in the
act, on the very document L-144 is about.

**Licence / distribution, stated exactly as printed on the page opened (page ii):**
*"Published May 1979 / Copyright © AGARD 1979 / All Rights Reserved / ISBN 92-835-1323-1"*.
**The document asserts All Rights Reserved on its own face.** NATO STO publishes it for open
download from its public publications portal and the search index reports it as open access;
**those two statements are in tension and this lane does not resolve the tension.** One copy is
held on this box for reading. **It is not redistributed, and rule 8 forbids it leaving.**

### 1.2 The published geometry and grid artifacts (NASA TMR / TMBWG)

All from `https://tmbwg.github.io/turbmodels/…`, retrieved 2026-09-01T16:38:20–22Z, all HTTP 200:

| file | path suffix | bytes | sha256 (leading 32) |
|---|---|---|---|
| `ONERA_M6_Test_Case_TMR.pdf` | `Onerawingnumerics_val/` | 4,341,049 | `aff893dd355fb07074e…` |
| `profile_ONERA-D.dat` | `Onerawingnumerics_val/` | 12,636 | `855972cf06b1bcd7530…` |
| `profile_M6_streamwise_alongy=0.dat` | `Onerawingnumerics_val/` | 1,712 | `cd9531b8720eb9ac2c6…` |
| `case_2308.dat` | `Onerawingnumerics_val/` | 22,695 | `020c5fcc58060737024eb87d9404f56bc563f3f6f15e337675c47477fa91f0d0` |
| `case_2565.dat` | `Onerawingnumerics_val/` | 22,695 | `6345287f200034492fe…` |
| `AileM6_with_sharp_TE.igs` | `Onerawingnumerics_grids/` | 256,608 | `cbca6850bd30dedf813…` |
| `AileM6_with_sharp_TE.stp` | `Onerawingnumerics_grids/` | 197,124 | `0ed2862f3952d04b747…` |
| `AileM6_with_thick_TE.igs` | `Onerawingnumerics_grids/` | 150,903 | `407ba52c4e3d23761a7…` |
| `input.nml_wing_strct_stt` | `Onerawingnumerics_grids/` | 3,708 | `da161bca069a2f44cce…` |
| `input.nml_wing_strct_2_stt` | `Onerawingnumerics_grids/` | 3,708 | `d88af755eff3a401c16…` |
| `input_coarsen.nml_wing_strct_stt` | `Onerawingnumerics_grids/` | 1,238 | `1b71012d7d08d954239…` |

| `wing-release-072319.zip` | `https://www.nasa.gov/wp-content/uploads/2026/04/wing-release-072319.zip` | 2026-09-01T16:38:22Z | 200 | 125,194 | `b8005774fff3bcf2c86…` |

**Licence:** the TMBWG repository that hosts the same artifacts carries
`https://raw.githubusercontent.com/TMBWG/turbmodels/main/LICENSE` (200, 7,048 B, sha256
`a2010f343487d3f7618…`) = **Creative Commons CC0 1.0 Universal**, a public-domain dedication.
**Clear.** The `wing-release-072319.zip` archive itself carries **no licence file**; it is
hosted on `nasa.gov` and mirrored in the CC0 repository. **That is an inference about the zip,
not a statement printed on it, and it is recorded as an inference.**

**RETRIEVALS THAT FAILED, recorded so the manifest is not silently selective:**
`hcf-grid-generator_description_v4.pdf` **404** (9,379 B error page);
`.../Onerawingnumerics_grids/wing_release_072319.tar.gz` via `raw.githubusercontent.com` **404**
(14 B). **The generator description document is therefore NOT held**, and no statement below
rests on it.

### 1.3 The SU2-distributed mesh

| file | URL | retrieved (UTC) | code | bytes | sha256 (leading 32) |
|---|---|---|---|---|---|
| `mesh_ONERAM6_turb_hexa_43008.su2` | `https://raw.githubusercontent.com/su2code/Tutorials/master/compressible_flow/Turbulent_ONERAM6/mesh_ONERAM6_turb_hexa_43008.su2` | 2026-09-01T16:38:22Z | 200 | 5,959,428 | `08631f6bfd443fcbd3d…` |
| `turb_ONERAM6.cfg` | same directory | 2026-09-01T16:38:23Z | 200 | 11,289 | `c7143ab3a1efc3eb12e…` |

**Licence:** `https://raw.githubusercontent.com/su2code/Tutorials/master/LICENSE` (200, 26,526 B,
sha256 `20c17d8b8c48a600800…`) = **GNU Lesser General Public License v2.1**. **Clear.**

---

## 2. AGARD AR-138 — TITLE-PAGE VERIFICATION (RULE 15 / L-144)

**Verified by opening the retrieved PDF and reading the rendered pages. Never by filename,
never by file type, never by hash** — and the discarded 403 page in §1.1 is why.

**Quoted exactly as printed on the title page (PDF page 1), including its printed report
number in the top right corner:**

> `AGARD-AR-138`
> NORTH ATLANTIC TREATY ORGANIZATION
> ADVISORY GROUP FOR AEROSPACE RESEARCH AND DEVELOPMENT
> (ORGANISATION DU TRAITE DE L'ATLANTIQUE NORD)
> **AGARD Advisory Report No.138**
> **EXPERIMENTAL DATA BASE FOR COMPUTER PROGRAM ASSESSMENT**
> REPORT OF THE FLUID DYNAMICS PANEL
> WORKING GROUP 04

**From the imprint page (PDF page 2, printed page ii):** *"Published May 1979 / Copyright ©
AGARD 1979 / All Rights Reserved / ISBN 92-835-1323-1"*, printed by Technical Editing and
Reproduction Ltd, Harford House, 7–9 Charlotte St, London, W1P 1HD.

**The chapter that carries the M6, quoted exactly as printed on page B1-1 (PDF page 327):**

> 1. PRESSURE DISTRIBUTIONS ON THE ONERA-M6-WING AT TRANSONIC MACH NUMBERS
> by
> **V. SCHMITT and F. CHARPIN**
> OFFICE NATIONAL D'ETUDES ET DE RECHERCHES AEROSPATIALES
> 92320 — CHATILLON — FRANCE

**This IS AGARD AR-138 and it does carry the M6 chapter. No substitution was made.**

**One discrepancy, disclosed rather than smoothed:** the report's own abstract card (PDF page 3)
states **"642 pages"**; the retrieved PDF contains **612 pages**. The scan is an Adobe Paper
Capture OCR of 2007-05-08. **The page-count difference is not explained by this lane** and every
citation below is given by PDF page **and** by the printed page number stamped on the sheet, so
a reader with a different copy can find it.

---

## 3. THE AGARD GEOMETRY, READ FROM THE PRINTED PAGE

**All of the following is transcribed from PDF page 327 = printed page B1-1, §2.1 "Wing data",
and PDF page 328 = B1-2, except where marked.**

| AR-138 clause | printed value |
|---|---|
| 2.1.1 Wing planform | swept back (figure B1-1) |
| 2.1.2 Aspect ratio | **3.8** |
| 2.1.3 Leading-edge sweep | **30°** |
| 2.1.4 Trailing-edge sweep | **15.8°** |
| 2.1.5 Taper ratio | **0.562** |
| 2.1.6 Twist | **without twist** |
| 2.1.7 Mean aerodynamic chord | **c = 0.64607 m** |
| 2.1.8 Span or semispan | **b = 1.1963 m** |
| 2.1.9 Number of airfoil sections used to define wing | **1** |
| 2.1.10 Section | *"y/b = 0 section coordinates of the symmetrical profile (design values): see table B1-1. The section is **ONERA D** normal to the generator at **40.18 % chord**"* |
| 2.1.11 Lofting | **conical generation** |
| 2.1.12 Fillets / strakes | no body, no strake, no fillet |
| **2.1.13 Form of wing tip** | **"truncation parallel to wing root and addition of a half body of revolution"** |
| 2.3 Fabrication tolerance / waviness | **0.15 mm** |
| 4.7 (B1-4) Areas and lengths used to form coefficients | **S = 0.7532 m², c = 0.64607 m** |

### 3.1 THE TRAILING EDGE IS NOT SHARP — AND THIS IS THE DECISIVE FINDING

**Table B1-1 (PDF page 333 = printed B1-7), 72 streamwise design points, `x/l` from `0.0` to
`1.0000000`. Its final row reads `x/l = 1.0000000`, `z/l = 0.0007052`.** The section is
**symmetrical** (2.1.10), so the design trailing edge carries a full thickness of

> **2 × 0.0007052 = 0.0014104 chord = 0.14104 % chord.**

**`N-C6`'s mechanism requires the section half-thickness `t2` to go to ZERO at the trailing
edge. In the AGARD primary definition it does not.** `N-C6` is not wrong — it is a correct
statement about sharp trailing edges — but **the ONERA M6 as AGARD defines it does not have
one**, and the F13 ladder's ~16:1 strip-to-core arc ratio is therefore a property of the
**sharpened** geometry the lab meshed, not of the M6.

Corroborated independently by the NASA TMR page for this case, which states that the geometry
it distributes *"features a sharp trailing edge"* while *"The original ONERA M6 wing has a
moderately thick trailing edge."*

### 3.2 THE TIP IS ROUNDED, NOT A FLAT CUT

**2.1.13, quoted above, is "truncation parallel to wing root AND ADDITION OF A HALF BODY OF
REVOLUTION."** `F13_ONERA_M6_PREREGISTRATION.md` §5 states *"the M6 tip is a flat cut, so the
cap is geometry, not a simplification."* **The primary says otherwise.** F13's verdicts are not
touched by this; its recorded description of the tip is.

### 3.3 THE SEVEN SPANWISE STATIONS — F13's REGISTERED UNBLOCK CONDITION IS SATISFIED

**PDF page 330 = printed B1-4, §5.1.1, quoted exactly:**

> *"271 pressure orifices divided in 7 sections (y/b = 0.20/0.44/0.65/0.80/0.90/0.96 and 0.99)"*

`F13_ONERA_M6_PREREGISTRATION.md` §2 registered, before any compute:

> *"UNBLOCK, registered now: if AGARD AR-138 reaches this box and title-page verifies (never by
> filename, file type or hash), the seven stations are read from it and P becomes claimable
> WITHOUT changing any gate, band, threshold, cap or label."*

**The document has reached this box (§1.1). It title-page verifies (§2). The seven stations are
read from it (above).** **This lane records the condition as satisfied and does nothing further
with it:** amending F13 is F13's owner's act, not this lane's, and no gate of F13 is touched
here.

**The reference accuracy F13 recorded as UNAVAILABLE is also now held.** PDF page 330 = B1-4,
§6.1: **`Cp` accuracy at `Mo = 0.84` is `ΔCp = ±0.02`**; force/moment accuracies
`ΔCX = ±0.002`, `ΔCZ = ±0.009`, `ΔCl = ±0.002`, `ΔCm = ±0.0006`, `ΔCn = ±0.0003`. **PDF page 331
= B1-5, §6.2: "Wall interference corrections — no corrections"**, and §6.3.6–6.3.8 record that
no wall-interference, aeroelastic or other corrections are included. **§4.2 records wing
semispan to tunnel width = 0.7.** Any future validation against this data inherits an
uncorrected-wall systematic that the report itself declines to quantify.

### 3.4 THE HELD `case_2308.dat` IS NOW PROVENANCED

`cases/dafoam/ladder-a/logs_A3/case_2308.dat` (sha256
`020c5fcc58060737024eb87d9404f56bc563f3f6f15e337675c47477fa91f0d0`, 22,695 B) is
**BYTE-IDENTICAL** to NASA TMR's published `case_2308.dat` retrieved at
2026-09-01T16:38:21Z — same sha256, same length, `cmp` reports no difference. F13 §2 disclosed
that the artifact's attribution rested *"on this lab's own prose and on a filename."*
**It now rests on a byte-identical match to the copy NASA TMR publishes for this test case,
whose page cites Schmitt & Charpin, AGARD AR-138.** That is a stronger chain and it is still
**not** a transcription check against the printed tables, which has **not** been performed.

### 3.5 THE AGARD DEFINITION IS INTERNALLY CONSISTENT — CHECKED, NOT ASSUMED

AR-138 prints `b`, `AR`, taper, MAC and `S` but **not** the root and tip chords. Deriving them
from `S = 0.7532 m²` and `λ = 0.562`:

- `c_mean = S/b = 0.7532 / 1.1963 = 0.629608 m`
- `c_root = 2 c_mean /(1+λ) = **0.806156 m**`, `c_tip = λ c_root = **0.453060 m**`
- **Cross-check, MAC recomputed** `= (2/3) c_root (1+λ+λ²)/(1+λ) = **0.646110 m**` against the
  printed **0.64607 m** — **difference +3.99e-05 m, +0.0062 %.**
- **Cross-check, aspect ratio** from full span `2b` and full area `2S`:
  `(2×1.1963)² / (2×0.7532) = **3.7999**` against the printed **3.8**.

**Two independent printed quantities reproduce from the other three to better than 0.01 %.**
The definition is self-consistent and the derived chords are safe to compare against.

---

## 4. GEOMETRY OF THE IMPORTED GRID, MEASURED AGAINST THAT DEFINITION

**Instrument:** `mesh_ONERAM6_turb_hexa_43008.su2` (§1.3), wall marker `WING`, 1,408 quad faces,
**1,453 wall nodes**. The wall surface is a C-O topology whose surface lines are **not** at
constant span, so sections were taken by marching the surface **ring by ring** from the root
through the face-edge adjacency (17 rings; 1,453 of 1,453 nodes covered), and the leading and
trailing edges taken as the actual extreme nodes of each ring.

**REJECTED INSTRUMENTS, recorded so the reported numbers are not mistaken for the first thing
tried.** Two earlier readers were discarded **before** their numbers were reported:
(a) constant-`y` sectioning returned 720 "stations" of 1 node each and a straight-edge residual
of **4.3e-01 m** on a 0.8 m chord; (b) spanwise binning returned residuals of **1.4e-01 m (LE)**
and **2.6e-01 m (TE)**. **Both were incapable of measuring a planform and neither is quoted.**
The ring reader's straight-edge residuals are **8.7e-08 m (LE)** and **3.4e-05 m (TE)**.

### 4.1 The planform

| quantity | AGARD | measured on the mesh | difference | AGARD basis |
|---|---|---|---|---|
| semispan `b` [m] | 1.196300 | **1.216363** | **+1.677 %** | printed 2.1.8 (tip **section**) |
| root chord `c_r` [m] | 0.806156 | **0.805899** | **−0.032 %** | derived §3.5 |
| tip chord `c_t` at `y=b` [m] | 0.453060 | **0.453253** | **+0.043 %** | derived §3.5 |
| leading-edge sweep [deg] | 30.000 | **29.8989** | **−0.337 %** (−0.101°) | printed 2.1.3 |
| trailing-edge sweep [deg] | 15.800 | **15.6548** | **−0.919 %** (−0.145°) | printed 2.1.4 |
| taper ratio | 0.562 | **0.562433** | **+0.077 %** | printed 2.1.5 |
| MAC [m] | 0.64607 | **0.646025** | **−0.007 %** (−45 µm) | printed 2.1.7 |

**Six of the seven agree with the AGARD definition to better than 1 %, and MAC to 45 µm.**

**The seventh is not a disagreement — it is the tip cap, and it is quantitatively confirmed.**
The mesh's maximum span exceeds the AGARD **tip-section** station by **0.020063 m**, and
**95 of 1,453 wall nodes lie outboard of `y = b`**. AGARD 2.1.13 adds *a half body of
revolution* beyond the truncated tip section; a half body of revolution about the tip chord adds
**half the tip-section maximum thickness** in span, which from the measured root
`t/c = 0.097804` and `c_t = 0.453253 m` predicts **0.022155 m** of extra span.

**The prediction was made from AGARD 2.1.13 before the publisher's own figure was read, and the
publisher's figure then confirmed it.** The NASA TMR case page, quoted from the copy of the page
held on this box, states its CAD's geometry as *"Root chord: 810.491484086 mm · Semispan (last
section): 1196.300000084 mm · Tip chord (last section): 455.914415721 mm · Leading Edge Sweep:
29.9990 degrees · Trailing Edge Sweep: 15.6918 degrees · **Rounded Tip Semispan: 1218.535 mm**"*.

> **TMR's rounded tip adds `1218.535 − 1196.300 = 22.235 mm`. The AGARD 2.1.13 prediction is
> `22.155 mm`. Ratio 0.9964 — agreement to 0.36 %.**

**The M6 tip is a half body of revolution, as AGARD prints, and the published CAD implements it.**
The SU2 **mesh** stops **2.172 mm** short of TMR's CAD rounded-tip semispan (20.063 mm of extra
span against 22.235 mm), i.e. **the mesh is a slightly truncated discretisation of that cap**;
whether that is deliberate or a surface-projection artefact is **not** determined here.

### 4.2 The trailing edge — the imported grid is SHARP and AGARD is not

**Measured on the mesh's root section (88 nodes at `y = 0` exactly): the trailing edge is a
SINGLE node. `t_TE/c = 0.000000000`.**

**That zero is planted, not assumed (rule 3).** The same reader, on a copy in which the TE node
was split by `2.000e-04 m` in the thickness axis, returned **`t_TE/c = 2.48170e-04` on 2 nodes**.
**The reader is demonstrably able to report a non-zero TE thickness, so its zero is evidence.**

> **imported grid: `t_TE/c = 0.00000 %` · AGARD Table B1-1: `t_TE/c = 0.14104 %`.**

This is the **one** substantive geometric departure of the imported grid from the AGARD
definition, and it is **the same departure NASA TMR documents on its own page.**

**And it explains the +1.677 % / −0.032 % pattern above quantitatively.** TMR's own published
planform for the sharpened geometry gives root chord **810.491484086 mm** against AGARD's
derived **806.156 mm** — **+0.538 %**, the chord growth from extending the surfaces to a point.
The generator's namelist carries `b = 1.476017976219800` **per unit root chord**; at TMR's root
chord that is `1.476018 × 0.810491 = **1.196296 m**` against AGARD's `b = 1.1963 m` —
**agreement to 4e-06 m, 0.0003 %.** **The sharpening is the whole of the discrepancy, and once
it is accounted for the published geometry reproduces AGARD's semispan exactly.**

### 4.3 The root section against Table B1-1

The machine copy of Table B1-1 used is TMR's `profile_M6_streamwise_alongy=0.dat`, **verified
against the printed table before use**: **72 points in the file, 72 rows counted on printed
page B1-7**; first row `0.0000000 / 0.0000000`, second `0.0000165 / 0.0006914`, last three
`0.9952090 / 0.0012985`, `0.9978030 / 0.0009773`, `1.0000000 / 0.0007052` — **identical in both**.

| quantity | value |
|---|---|
| mesh upper-surface points on the root section | **45** |
| B1-1 design points compared (0.001 ≤ x/l ≤ 0.999) | **64** |
| **max │Δz│/c** | **6.783e-04** |
| **RMS │Δz│/c** | **2.261e-04** |
| max `t/c`, mesh | **0.097804** |
| max `t/c`, Table B1-1 | **0.097859** |

**Planted control (rule 3):** with `+5.000e-04 c` added to every B1-1 ordinate the comparator
returned **1.178e-03** against its as-read **6.783e-04**. **The plant was seen; the agreement
figure is evidence, not a blind zero.**

**Honest reading of the residual.** `6.78e-04 c` on a 0.806 m chord is **0.55 mm**, which is
**larger than AGARD 2.3's stated 0.15 mm fabrication tolerance**. **It is not asserted here that
the CAD deviates from the design section by that much**: the mesh section carries only 45 upper
points, so the comparison is dominated by linear interpolation of a coarse surface, and the
deviation is concentrated near the leading edge where curvature is highest. **Separating
interpolation error from geometry error requires the CAD, and was not done.**

---

## 5. IS THE PUBLISHED FAMILY GEOMETRICALLY SIMILAR? — MEASURED, NOT ASSUMED

### 5.1 The SU2 mesh is NOT a family, and that is a finding

`mesh_ONERAM6_turb_hexa_43008.su2` is **one** grid of 43,008 hexahedra. **SU2 distributes single
meshes for this tutorial, not a refinement ladder.** §0 of Sanaa's directive cannot be satisfied
from it, and no observed order can be computed from it. **The literal reading of "import a
published mesh" does not reach three levels.**

### 5.2 The route that does: ONE generator call plus a published coarsening program

The NASA TMR grids page distributes `wing-release-072319.zip` (§1.2) containing
`hcf_wing_v5p0.f90` (356,409 B) and `hcf_coarsening_v3p9.f90` (425,788 B) with the M6 namelists
and `om6_wing_section_sharp.dat`. Both compiled clean with `gfortran 13.3.0 -O2`.

**This architecture answers `L-430` structurally rather than by discipline.** The three levels
are **not** three generator calls with a scale argument — they are **one** generator call
followed by the publisher's coarsening program, which removes every other node. **No generator
parameter can fail to scale with the ladder, because the generator is invoked once.**

**The coarsening program asserts the nesting itself**, printing on the run recorded here:
*"Good. Exactly twice as many f-cells as c-cells in a line"* and *"Must have (nested nodes) =
(ncnodes): Nested nodes = 279, ncnodes = 279."*

### 5.3 Measured similarity of the demo family

Built from the **published demo namelist** `input.nml_strct` as distributed
(`nnodes_cylinder_input = 32`, `nre = 64`, `nr_gs = 8`, `target_y_plus = 1.0`,
`stretching_tanh_towards_lete = 4.5`, `R_outer = 100` root chords):

| level | PLOT3D dims `i×j×k` | cells | ratio to next coarser | `r` implied |
|---|---|---|---|---|
| L1 (fine) | 41 × 65 × 49 | **122,880** | **8.0000** | **2.000000** |
| L2 | 21 × 33 × 25 | **15,360** | **8.0000** | **2.000000** |
| L3 (coarse) | 11 × 17 × 13 | **1,920** | — | — |

**`L-430`'s cheap check applied: for a 3-D family the total cell-count ratio must be `r³`.
It reads 8.0000 on both pairs, exactly, and `r = 2.000000` in every direction by construction.**
`r = 2.0` sits at the top of §0's admissible band (1.5–2.0). A fourth level (L4, 240 cells) is
produced by the same chain and is available for §0 step 4(c).

### 5.4 The generator's own reported wing characteristics vs AGARD

Printed by `hcf_wing` at root chord = 1: semispan **1.4760179762198**, reference area
**1.1531508411923**, aspect ratio **3.7785673622219**, MAC **0.80167295851234**.

| quantity | AGARD | generator | difference |
|---|---|---|---|
| MAC / `c_root` | 0.801420 | **0.801673** | **+0.032 %** |
| aspect ratio | 3.8 | **3.77857** | **−0.564 %** |
| semispan (physical, at TMR `c_root`) [m] | 1.1963 | **1.196296** | **−0.0003 %** |

The **−0.564 %** on aspect ratio is against a value AR-138 prints to **two significant figures**;
it is also computed by the generator *"assuming a trapezoidal wing"*, i.e. ignoring the rounded
tip. **Neither is a discrepancy this lane can call a defect.**

### 5.5 MESH QUALITY OF THE DEMO FAMILY — IT DOES NOT CLEAR THE 70° GATE

Imported into OpenFOAM v2606 via `plot3dToFoam` (the generator writes Fortran-unformatted
multiblock PLOT3D; converted to ASCII by a reader that verifies every record marker and the
`nblocks / dims / coords` record lengths against `ni·nj·nk·3·8`), then `checkMesh`:

| level | cells | internal faces | **max non-orthogonality** | severe (> 70°) | **severe fraction** | max skewness |
|---|---|---|---|---|---|---|
| L3 | 1,920 | 5,448 | **88.9306°** | 484 | **8.884 %** | 2.94156 |
| L2 | 15,360 | 44,832 | **88.3866°** | 3,874 | **8.641 %** | 2.30290 |
| L1 | 122,880 | 363,648 | **86.5861°** | 26,566 | **7.305 %** | 6.57679 |

**Against `MESH_STANDARD.md` §3.1's 70° hard gate this family FAILS at every level**, and the
finest level additionally reports 3 highly skew faces. **`checkMesh` prints `Mesh OK` on L3
while its maximum is 88.93°** — §3.1's instruction to read the maximum and never the tool's OK
line, exercised again.

**BUT THE REFINEMENT DIRECTION IS THE OPPOSITE OF `N-C6`'s, AND THAT IS THE USEFUL RESULT.**
`N-C6`'s signature of a **geometric** floor is a maximum **rising** to an asymptote with the
severe fraction **rising** an order of magnitude. Here **both fall**: maximum
**88.93 → 88.39 → 86.59°**, severe fraction **8.884 → 8.641 → 7.305 %**. `N-C6`'s own
operational reading item 2 says *"Two levels are enough to tell rising from falling, and rising
settles the question."* **It is falling. This is a resolution artefact of a deliberately crude
demo grid, not the F13/N-C6 structural defect.**

**Where the bad faces are.** All 26,566 severe faces on L1 lie within **r ≤ 2.26 root chords**
of the root leading edge (median **1.96**, 1st percentile **0.95**), in a far field extending to
**r = 100**. **They are in the near-field/tip region, not the outer boundary.**

**One further observation, recorded because it is the F13 failure mode's fingerprint.**
`plot3dToFoam` produced **124,865 points from 130,585 PLOT3D nodes** — **5,720 nodes merged**,
i.e. the published topology contains **collapsed lines**. The demo grid's first cell is sized
for `y+ = 1` at `Re = 14.6e6`, giving maximum aspect ratios of **284 / 1,203 / 637** across the
three levels. **A very thin cell on a collapsed line is exactly where an 88° face comes from.**

### 5.6 WHAT THIS DOES AND DOES NOT SETTLE

**SETTLED.** A published M6 family exists; it is retrievable; its licence is CC0; it produces
`r = 2.000000` node-nested levels from one generator call; its geometry reproduces the AGARD
definition to better than 1 % on six of seven planform quantities and to 45 µm on MAC.

**NOT SETTLED, and no verdict is claimed on it.** **The production namelist has NOT been run.**
Everything in §5.3 and §5.5 is the **demo** namelist as distributed. The published production
namelist `input.nml_wing_strct_2_stt` differs materially — `nnodes_cylinder_input` **32 → 320**,
`nre` **64 → 448**, `nr_gs` **8 → 64**, `target_y_plus` **1.0 → 0.5**,
`stretching_tanh_towards_lete` **4.5 → 1.0** — and the last of those is precisely the parameter
that controls clustering into the leading and trailing edges, where the severe faces sit.
**Whether the production grid clears 70° is UNKNOWN and is the first thing the ladder must
measure.**

**Also not settled:** the sharp trailing edge. The published generator ships
`om6_wing_section_sharp.dat`, whose final ordinate is `0.0000000` where AGARD B1-1 reads
`0.0007052`. **Three separate facts say the blunt-TE route is open and none of them is a
measurement that it works.** (a) The generator supports blunt sections and rounded tips — it
ships `input.nml_naca0012_blunt` and `input.nml_naca0012_round`. (b) **NASA TMR distributes the
AGARD-faithful CAD**: its page states *"(The original ONERA M6 wing has a moderately thick
trailing edge; see `AileM6_with_thick_TE.igs`.)"*, and that file **is held on this box**
(§1.2, 150,903 B). (c) AGARD Table B1-1 supplies the blunt section directly, and the machine
copy in §4.3 is verified against the printed table. **None of this has been attempted and no
claim is made that it will clear the gate.**

**A cross-check on the flow conditions, recorded because it corroborates the chord bookkeeping.**
TMR specifies `Re_c_root = 14.6e6` *"based on root chord with sharp trailing edge"*; AGARD's
Reynolds number is formed on the MAC. Converting, `14.6e6 × (0.64607/0.810491) = **11.64e6**`
against the `REC = 11.72e6` carried in the `case_2308.dat` header — **0.7 %**. The two
conventions are consistent, and **a solve that used 14.6e6 on the MAC would be wrong by 25 %.**

---

## 6. COST

**Rule 12. Unit: core-minutes. Dollars DERIVED at the recorded c7a.4xlarge rate of
$0.0513/core-h and labelled derived-not-measured — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).**

| item | ranks | wall | **core-minutes** | derived $ |
|---|---|---|---|---|
| document + artifact retrieval (network-bound) | 1 | ~70 s | **1.17** | $0.0010 |
| `gfortran -O2` × 2 | 1 | ~25 s | **0.42** | $0.0004 |
| `hcf_wing` (demo, L1) | 1 | **1 s** | **0.02** | $0.0000 |
| `hcf_coarsening` (L2, L3, L4) | 1 | **1 s** | **0.02** | $0.0000 |
| PLOT3D → ASCII × 3 | 1 | ~12 s | **0.20** | $0.0002 |
| `plot3dToFoam` + `checkMesh` × 3 | 1 | ~85 s | **1.42** | $0.0012 |
| geometry measurement scripts | 1 | ~20 s | **0.33** | $0.0003 |
| **TOTAL, this record** | | | **≈ 3.6 core-min** | **≈ $0.003 (derived)** |

**Contention disclosure, because a cost quoted without it has just been corrected twice in this
team today (`bd84e7f8`, `4c9c0744`, `03ee19c5`).** Every figure above was measured at a
1-minute load average of **14.30 on 16 cores** with sister lanes running JF1. All work was run
`nice -n 15` on a single core. **These are wall-clock-derived core-minutes under contention and
they are gross, not cleaned.** At this scale the absolute error is under a core-minute and
changes nothing; **it is recorded because the practice, not the magnitude, is the rule.**

**No calibration row is filed to `docs/COST_CALIBRATION.md` for this record**, because no
process registered a **predicted** cost against which to compare an actual. The ladder's
estimate-versus-actual comparison belongs to `M6I_PREREGISTRATION.md` and is filed at its
completion.

---

## 7. WHAT THIS LANE DID NOT VERIFY

Stated plainly, because a supervisor's check on a relayed confidence is not a check.

1. **No solver has run.** No flow field, no `C_D`, no `C_L`, no shock position exists for `M6I`.
2. **The production grid has not been built.** §5.5's numbers are the demo namelist only.
3. **The tip-cap construction is not verified** — §4.1's ratio 0.905 is consistent with AGARD
   2.1.13, not a proof of it.
4. **`case_2308.dat` has not been checked row-by-row against the printed AR-138 tables.**
   §3.4 establishes a byte-identical match to NASA TMR's published copy, which is a provenance
   chain, not a transcription audit.
5. **The 0.55 mm root-section residual is not attributed** between mesh coarseness and CAD
   deviation.
6. **The AGARD PDF's 612-vs-642 page discrepancy is not explained.**
7. **The `wing-release-072319.zip` licence is inferred from its hosts, not printed on it.**
8. **The generator description PDF is not held** (404) and nothing here rests on it.
9. **No `M6I` mesh has been admitted** under `MESH_STANDARD.md` §3.1, and on the only family
   measured, it would not be.

---

## 8. ARTIFACTS

- `docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf` — the retrieved
  primary, sha256 `a96a73304c8328bd97c828cead2df9326675fd2340230d7e81fcf9f8191e7ffb`,
  17,588,425 B, 612 pages.
- `docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.txt` — the required
  sidecar (`FILING_CHARTER` R9), 1,385,107 B, produced by `pdftotext -layout`.
- Every URL, timestamp, HTTP code, byte size and sha256 in §1 above. **Those are the provenance;
  they re-derive without any file this lane wrote.**

---

## ADDENDUM 1 — 2026-09-01: THE `checkMesh` VERDICT-LINE DEFECT IS ALREADY A STANDARD, AND THIS IS ITS THIRD INSTANCE

**Dated addendum, appended at the foot. Nothing above is edited, reordered, inserted or
deleted.** Filed on the cfd supervisor's instruction of 2026-09-01, **and the cited section was
read by this lane directly before citing it** — a supervisor's description of a standard is
evidence, not this lane's reading of it (rule 9).

§5.5 above records that `checkMesh` printed **`Mesh OK`** on the demo L3 at a maximum
non-orthogonality of **88.9306°**, and treats it as an observation. **It is not a new
observation. It is a known, registered defect of the instrument**, and the next reader should be
sent to the standard rather than rediscovering it a fourth time.

**`docs/standards/MESH_STANDARD.md` §14** — *"READING THE NON-ORTHOGONALITY GATE — the reported
maximum, never `checkMesh`'s verdict line"* (v1.9, 2026-09-01) — settles it as a
**discrimination test**, which is the planted-control standard of CLAUDE.md rule 3 applied to
the instrument itself:

- **§14.1:** `CONTROL_nofill_L1` at **51.2554°** (admissible) and `t1_SHELL` at **81.5834°**
  (inadmissible by 11.6°) both print **`Non-orthogonality check OK.`** *"The line reads the same
  on the mesh that passes and the mesh that fails."*
- **§14.3:** the two closing lines run the **wrong way** — the **admissible** mesh reports
  `Failed 2 mesh checks.` and the **inadmissible** one `Failed 1 mesh checks.`, because the
  counts sum over metrics that exclude non-orthogonality entirely.

**THIS LANE'S MEASUREMENT IS A THIRD INSTANCE AND IS CLEANER THAN EITHER.** Both of §14.3's
examples carry a confounding failed check. **The `M6I` demo L3 carries none:**

> **1,920 cells · maximum non-orthogonality `88.9306°`, `18.93°` over the §3.1 gate · 484
> severely non-orthogonal faces · closing line `Mesh OK.` · no failed check of any kind.**

**A total pass on the tool's own terms, at 88.93°.** Recorded here so §14 gains a third
independently produced instance, on a mesh from an **external** generator rather than one of
this lab's, which is the case §14 did not previously cover.

**No gate value moves.** §3.1's 70° hard gate is untouched in either direction; retiring,
widening or narrowing a gate threshold is reserved to Sanaa. What is affected is only **where
the gate is read from**, and §5.5 above already read it from the reported maximum.

### Assertions, MEASURED after the write

| assertion | value |
|---|---|
| lines edited, reordered, inserted or deleted above this section | **none** |
| **lines whose number changed above this section** | **0** |
| md5 of this file's first 545 lines BEFORE the append | `b201299794bb76b6528327ed72d7bbdb` |
| md5 of this file's first 545 lines AFTER the append | `b201299794bb76b6528327ed72d7bbdb` |
| the two digests | **EQUAL — assertion MEASURED, verified after the write** |
