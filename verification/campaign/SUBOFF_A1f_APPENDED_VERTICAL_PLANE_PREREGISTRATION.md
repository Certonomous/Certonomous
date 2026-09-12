# SUBOFF **A1f** — THE VERTICAL-PLANE α-SWEEP ON THE **HULL + SAIL + FOUR STERN APPENDAGES** BODY — PRE-REGISTRATION

**STATUS: DRAFT, COMMITTED BEFORE ANY SOLVE. NOT YET FROZEN.**
No solver has been started by this document. The solve directories it registers in §9 —
`verification/runs/navier_class/SUBOFF_HULL_SAIL_4STERNPLANES/SOLVE_A*` — **do not exist**,
and no entry for this act exists in `verification/queue/cfd/`. That is the amendment
condition of CLAUDE.md rule 2, stated and **checked, not assumed**.

**Author:** cfd `lab-lane` (SUBOFF fully-appended geometry lane), 2026-09-12.
Directed by the cfd-supervisor. §12's freeze block is the cfd-supervisor's personally and
is not delegable.

**Predecessors, none of whose gates this document moves, narrows or revives:**
`SUBOFF_A1b_PREREGISTRATION.md` (frozen), `SUBOFF_A1b_CONCAVE_FORCE_SHARE_PREREGISTRATION.md`
(frozen `bc73dc0cae2063477d9d54ee5512b93a68be3249`), `SUBOFF_A1c_PREREGISTRATION.md`,
`SUBOFF_A1d_BAREHULL_PREREGISTRATION.md`, `SUBOFF_A1e_HORIZONTAL_PLANE_ARM_PREREGISTRATION.md`.
**A1e is a different act on a different body and this document does not supersede it.**

---

## 0. WHY THIS ACT EXISTS

Sanaa registered, in her own words (`docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md`):

> "Register before launch: reference = Roddy 1990 captive-model forces and moments (band per
> derivative written first), Huang 1992 surface pressure at α = 0 as the anchor; sweep points
> α = −12, −8, −4, 0, +4, +8, +12; quantities Z, M, hull/fin split; derivatives by linear fit
> over |α| ≤ 8; neutral point from Z_w and M_w. Cost estimate registered too but doesnt stop
> the run"

A peer cfd lane established, from **Roddy 1990 Table 4 read as a PAGE IMAGE on report page
19**, that the vertical-plane derivatives she named are published for **one configuration
only**, and that the lab's existing SUBOFF mesh — hull + sail, six patches
`inlet outlet farfield symm hull sail` — is not that configuration. Her sweep could not be
graded on any geometry the lab held. **This act builds the missing body.** It delivers her
instruction rather than changing it.

---

## 1. 🔴 THE FINDING THAT GOVERNS THIS WHOLE DOCUMENT: **RODDY'S "FULLY APPENDED" CARRIES RING WING NO. 1, AND THIS BODY DOES NOT**

Read from the page image of **Roddy 1990, Table 3, "Schedule of the stability and control
experiments", report pages 17 and 18** (PDF pages 25 and 26 of the filed file), rendered at
160 dpi. The six configuration headings, **exactly as printed**:

| heading, verbatim | plane |
|---|---|
| `CONFIGURATION 1 - VERTICAL PLANE, FULLY APPENDED WITH RING WING NO. 1` | vertical |
| `CONFIGURATION 2 - HORIZONTAL PLANE, FULLY APPENDED WITH RING WING NO. 1` | horizontal |
| `CONFIGURATION 3 - HORIZONTAL PLANE, BARE HULL` | horizontal |
| `CONFIGURATION 4 - HORIZONTAL PLANE, HULL AND SAIL ONLY` | horizontal |
| `CONFIGURATION 5 - HORIZONTAL PLANE, HULL AND CONTROL SURFACES ONLY` | horizontal |
| `CONFIGURATION 6 - HORIZONTAL PLANE, HULL AND RING WING NO.1 ONLY` | horizontal |

**Configuration 1 is the only vertical-plane configuration in the programme, and it is
fully appended WITH RING WING NO. 1.** The body this act builds — hull, sail and four stern
appendages — is **Roddy's Config 1 MINUS the ring wing and its four support struts.**

**This corrects the premise this lane was handed.** The brief said the vertical-plane
derivatives are published for "the FULLY APPENDED body" and that building it was the route
to the sweep. That is true only up to the ring wing. Building the ring wing and its struts
as well would reproduce Roddy's Config 1 exactly; Groves 1989 publishes the equations for
both (Table 4, report pages 15–16, and Table 5, report pages 19–20, with Figure 7 for the
placement — their existence and location verified from the page index and from the report
page 12 text, read as an image; **their contents were NOT read by this lane and nothing in
this document depends on them**). That is a separate, larger act. **It is named here as the
only route to an exactly-matched body, and it is not taken here.**

### 1.1 THE SIZE OF THE GAP, MEASURED FROM RODDY'S OWN TABLE — NOT ESTIMATED

Roddy Table 4, report page 19, "Horizontal Plane", read as a page image, lets the ring
wing's own contribution be **measured**, because Config 6 is the ring wing on the bare hull
and Config 3 is the bare hull:

| | bare hull (`Config 3`) | hull + ring wing 1 (`Config 6`) | ring-wing increment | as % of bare hull |
|---|---|---|---|---|
| `Y_v'` | −0.005948 | −0.005943 | **+0.000005** | **0.08 %** |
| `N_v'` | −0.012795 | −0.012939 | **−0.000144** | **1.13 %** |
| `K_v'` | −0.000019 | −0.000019 | 0.000000 | 0.00 % |

And the superposition of all three appendage increments onto the bare hull reproduces the
measured fully appended body to:

| | bare + Δsail + Δplanes + Δringwing | measured `Config 2` fully appended | residual, as % of measured |
|---|---|---|---|
| `Y_v'` | −0.027549 | −0.027834 | **1.02 %** |
| `N_v'` | −0.014137 | −0.013648 | **3.58 %** |

**Why the horizontal-plane bound transfers to the vertical plane here, and why the same
argument would NOT be admissible for the sail.** A ring wing is an **annular shroud,
axisymmetric about the hull axis**: it presents the identical planform to a vertical and a
horizontal cross-flow, so its increment is plane-independent **by geometry**. The sail is
not: it is broadside in drift and edge-on in pitch, so its horizontal-plane increment is
only an upper bound on its pitch increment (that is A1c §2.3's argument and it is a weaker
one). **The residual uncertainty in the transfer is the four ring-wing support struts**,
whose azimuths this lane did not read.

### 1.2 🔴 THE BAND IS **NOT** WIDENED FOR THIS GAP

The gate below stays at **±4 %**. A result outside ±4 % is **GATE FAIL**, with the
ring-wing gap and its measured 0.08 % / 1.13 % / 1.02 % / 3.58 % figures **printed beside
it** as a pre-quantified candidate cause. Widening a band to swallow a known missing
appendage after the numbers exist is gating at the kind end, which §7's trap 4 forbids
outright. **The gap is disclosed, quantified in advance, and does not buy tolerance.**

---

## 2. THE CONFIGURATION-NAMING RULE — BINDING, AND IT IS WORSE THAN THE RULE'S AUTHORS KNEW

Established by the peer SUBOFF lane
(`SUBOFF_A1b_CONCAVE_FORCE_SHARE_PREREGISTRATION.md` §6, frozen `bc73dc0ca`; restated in
`SUBOFF_A1e_HORIZONTAL_PLANE_ARM_PREREGISTRATION.md` §2) and **cited, not re-derived**.
This lane verified every label below **independently, from the page images**, and adds a
third collision the rule did not previously name.

**THE INTEGERS COLLIDE.**

| label, as printed | document and page (image-read) | body |
|---|---|---|
| `CONFIGURATION 1` | Roddy 1990, Table 3, report p.17 | **fully appended with ring wing no. 1** |
| `Config. 1` / `1 Bare Hull` | Liu & Huang 1998, report p.6 and Table 14 p.23 | **bare hull** |
| `Config 3 Bare Hull` | Roddy 1990, Table 4, report p.19 | bare hull |
| `Config. 3 Hull with four stern appendages` | Liu & Huang 1998, report p.6 | hull + 4 appendages |

**The same integer, `1`, names the emptiest and the fullest body in the programme, in two
official reports on that programme.**

**AND LIU & HUANG SWITCH SCHEMES WITHIN ONE PAGE.** Report page 6, read as an image: the
towing-tank list reads `Config. 1 Bare hull only / Config. 3 Hull with four stern
appendages / Config. 8 Hull with sail and four stern appendages / Config. 6 Hull with ring
wing #1 / Config. 7 Hull with ring wing #2`; four paragraphs below, on the same page, the
PMM list reads `Vertical plane statics … Configuration 1, Configuration 6` and `Horizontal
Plane Statics … Configuration 2`, which is **Roddy's** scheme. A reader citing
"Configuration 1" from that page gets the bare hull or the fully appended model depending
on which paragraph their eye was on.

### 2.1 🔴 THE NEW COLLISION THIS LANE ADDS: **THE PHRASE "FULLY APPENDED" IS ITSELF AMBIGUOUS**

It is not only the numbers.

- **Roddy 1990, Table 3, report p.17**: `FULLY APPENDED WITH RING WING NO. 1`.
- **Liu & Huang 1998, Table 14, report p.23**, `Config. No.` column: `8  Fully Appended` —
  with `6 Ringed Wing #1` and `7 Ringed Wing #2` as **separate rows**, and the footnote on
  that page naming only *"Hull, bridge fairwater and four identical stern appendages"*.

**Liu & Huang's "Fully Appended" has no ring wing. Roddy's has one. The same two words name
two different bodies.** Therefore the rule is extended here and binds this family:

> **A configuration is named by its APPENDAGE INVENTORY — which appendages are present and
> which are absent — never by a bare number and never by the phrase "fully appended" alone.
> Every table is cited by report, page, and the label exactly as printed in that document.**

**THE BODY OF THIS ACT, NAMED BY ITS GEOMETRY:** the DARPA SUBOFF axisymmetric hull
(DTRC Model 5470/5471), **WITH** the bridge fairwater (sail) at top dead centre, **WITH**
four identical stern appendages at the **BASELINE** axial position, **WITHOUT** any ring
wing and **WITHOUT** ring-wing support struts. In Liu & Huang's towing-tank scheme this is
`Config. 8`; in their Table 14 it is the row printed `8  Fully Appended`; in Roddy's scheme
it has **no column at all**.

---

## 3. THE GEOMETRY — EVERY DIMENSION CITED TO ITS REPORT AND PAGE, READ AS PAGE IMAGES

**Source, title page verified under CLAUDE.md rule 15 by RENDERING PDF page 1 and READING
it** (never by filename, file type or hash), this lane, 2026-09-12:

> David Taylor Research Center, Bethesda MD 20084-5000 · **DTRC/SHD-1298-01 · March 1989** ·
> Ship Hydromechanics Department · **"GEOMETRIC CHARACTERISTICS OF DARPA SUBOFF MODELS
> (DTRC MODEL NOS. 5470 and 5471)"** · by **Nancy C. Groves, Thomas T. Huang, Ming S. Chang**
> · **AD-A210 642** · "Approved for public release; Distribution unlimited."
> `docs/papers/benchmark_test_cases/groves_1989_dtrc_shd1298_darpa_suboff_geometry.pdf`

**That PDF is a pure image scan. Its `.txt` sidecar is Internet Archive OCR and its own
sidecar says so. No number in this document came from that sidecar.**

Corroborating source, title page verified the same way: NSWCCD, **CRDKNSWC/HD-1298-11, June
1998**, *"Summary of DARPA Suboff Experimental Program Data"*, **Han-Lieh Liu, Thomas T.
Huang**. This PDF **has no text layer at all** (`pdftotext` returns empty on all 28 pages),
so it can only be read as images, which is how it was read.

### 3.1 HULL AND SAIL — INHERITED, NOT REBUILT

`build_hull_stl()` and `build_sail_stl()` are **imported** from the already-validated
`cases/navier_class/SUBOFF_A1/build_suboff_a1_geometry.py` and called with the SUBOFF_A1
pipeline's own resolution arguments. **They are not copied and not re-typed.**

### 3.2 THE STERN APPENDAGES — Groves Table 3, report page 14, read as an image

Narrative, **Groves report page 6** (PDF p.13), read as an image, verbatim:

> "The stern appendages consist of four identical appendages mounted on the model hull at
> angles of 0 degrees (top dead center), 90 degrees, 180 degrees, and 270 degrees."

**Table 3, "Equations to define stern appendages", report page 14** (PDF p.21), read as an
image. Its own header: *"These equations define the upper rudder stern appendage. The three
remaining stern appendages are located on the hull at 90° azimuthal increments."*

```
z(ξ)/c(y) = 0.29690 √ξ − 0.12600 ξ − 0.35160 ξ² + 0.28520 ξ³ − 0.10450 ξ⁴
for 0 ≤ ξ = (x − h)/c(y) + 1.0 ≤ 1
h = x coordinate of the stern appendage trailing edge
c(y) = −0.466308 y + 0.88859 = chord length
Three values of h:  12.729617 · 13.146284 = BASELINE · 13.562950
HULL/STERN APPENDAGE INTERSECTION:  [R_HA(ξ)]² = y² + [z(ξ)]²
```

**Cross-read against Groves Appendix C**, *"Listing of computer code to generate stern
appendages"* (`DARPA2STERNAPP.FOR`), report pages 62–65 (PDF pp.69–72), also read as images.
It repeats every coefficient **identically** and supplies the **tip**, which Table 3 does not
state:

```
DELR = 0.05 ;  DO 850 I=1,NP ;  RR = RBSMAX + I*DELR
IF(RR.GT.RMAX) RR = RMAX            PARAMETER RMAX = 0.833333
```

> **THE APPENDAGE TIP LIES ON THE HULL'S OWN MAXIMUM-RADIUS CYLINDER, R = 0.833333 ft = 5/6 ft.**
> The appendages do not protrude beyond the parallel-middle-body diameter.

**A DISCREPANCY IN THE SOURCE, RECORDED AND NOT SILENTLY RESOLVED.** Groves **report page
12** (PDF p.19) prints the forward appendage trailing edge as `x=12.729167 Ft (3.880 m)`.
**Table 3 (p.14), Figure 5 (p.11) and Appendix C (p.62) all print `12.729617`.** Two of the
three digit-bearing sources agree and the outlier is the running text. **This act uses the
BASELINE `h = 13.146284`, on which all four sources agree, so the discrepancy does not touch
it.**

### 3.3 🔴 THREE SELF-CHECKS ON THE DIGITS — each broken by one transposed digit, all asserted at run time

A scanned page is exactly where a transposed digit enters, and no downstream check would
catch it. These three are internal consistency tests that a misread would fail:

| check | value required | **MEASURED** | what a misread would do |
|---|---|---|---|
| section coefficients sum to zero | `0` exactly | **−1.39 × 10⁻¹⁷** | the section would not close at the trailing edge |
| chord at the tip radius | `0.500000 ft` exactly | **0.5000002 ft** | chord slope, intercept and `RMAX` would be mutually inconsistent |
| maximum `z/c` and its station | `0.10003` at `ξ = 0.2997` | **0.100029 at ξ = 0.29970** | it would not be the 20 %-thick, 30 %-chord NACA-0020 thickness family |

The generator **refuses (exit 2)** on any of the three, with the message telling the reader
to re-read the page as an image.

### 3.4 THE BUILT APPENDAGE — measured from the emitted STL, not from the generator's variables

| quantity | value |
|---|---|
| trailing edge (BASELINE `h`) | 13.146284 ft = **4.006987 m** |
| tip radius from the hull axis | 0.833333 ft = **0.254000 m** |
| tip chord | 0.500000 ft = **0.152400 m** |
| root radius at the TE station | 0.271278 ft = **0.082685 m** |
| root chord at that station | 0.762091 ft = **0.232285 m** |
| exposed span | 0.562056 ft = **0.171315 m** |
| exposed planform area, one fin | **0.032951 m²** |
| exposed aspect ratio, one fin | **0.8907** |
| taper ratio tip/root | **0.6561** |
| maximum full thickness, root / tip | **46.47 mm / 30.49 mm** |
| section | closed-TE NACA-0020 thickness form, max at 30 % chord |

Patch names carry the geometry, never a number alone: `fin000_upper_rudder` (azimuth 0°,
top dead centre — Groves Table 3's own "upper rudder"), `fin090_horizontal`,
`fin180_lower_rudder`, `fin270_horizontal`.

### 3.5 REGISTERED DEPARTURES FROM THE REFERENCE GEOMETRY — four, all stated before any mesh

| id | departure | magnitude, **measured** |
|---|---|---|
| **D1** | fin trailing edge truncated at **0.98 c**; the reference closes to a mathematical cusp (`z(ξ=1) = 0` exactly, asserted) | base **1.4630 mm** at the tip, **2.2299 mm** at the root; **0.960 %** of the tip chord; chord removed 3.05 mm (tip) / 4.65 mm (root) |
| **D2** | **flat fin tip**: Groves stops the appendage at `RMAX` and states no tip shape; a planar cap normal to the span is applied | exact, by construction |
| **D3** | **buried fin root**: the solid is extended inward to R = 0.10 ft (Groves' own Appendix C starting radius) so snappyHexMesh unions it with the hull; the true root is Table 3's intersection curve, which is **computed and reported** but not used to cut the STL | verified inside the hull at 401 chord stations; the generator refuses if any point reaches the hull radius |
| **D4** | sail TE truncated at 0.995 c — **inherited unchanged** from SUBOFF_A1 | base 1.3109 mm, 0.356 % of chord |

**WHY D1 IS 0.98 c AND NOT 0.995 c, DECIDED OPENLY AND BEFORE THE MESH.** At 0.995 c the fin
base is 0.37 mm (tip), and eight cells across it would need a level-11 refinement box costing
roughly 4 × 10⁶ cells **per fin arm** at L1. At 0.98 c the base is **1.4630 mm — within
12 % of the sail's own 1.3109 mm base**, and the family's existing level-9 box resolves it at
**9.5 cells at the tip and 14.5 at the root**, clearing the floor of 8 at every spanwise
station. The departure is larger in *relative* terms only because the fin chord is 2.4×
smaller than the sail's. The alternative and its cost are named here so the choice cannot
later be read as a discovery.

### 3.6 🔴 THE BYTE-IDENTITY REGRESSION — THE APPENDED BODY INHERITS THE HULL'S VERIFICATION

`hull.stl` and `sail.stl` emitted by this generator are **byte-identical to the SUBOFF_A1
build at BOTH stages**, and the pipeline **refuses** otherwise:

| stage | file | sha256 |
|---|---|---|
| raw generator output vs a fresh A1 reference build | `hull.stl` | `0560a975d26c34ba…` |
| raw generator output vs a fresh A1 reference build | `sail.stl` | `a1a44f6ce01f99b1…` |
| after `surfaceOrient`, vs **the A1 geometry on disk that the live A1 solves are running on** | `hull.stl` | `7185c45ed0869078b6961b11a779235e2f12bbec94e83c09947022f85e6f98f6` |
| after `surfaceOrient`, vs **the A1 geometry on disk** | `sail.stl` | `4fe939c36f6faf136001edf01e8fb0a378e9c3de572ac51248d3d4283c66589e` |

### 3.7 CORROBORATION AGAINST THE SOURCE, BY MEASUREMENT ON THE STL FILES

`verify_appended_geometry.py` measures **29 quantities from the STL vertices on disk** —
not from the generator's own variables, which would only prove the generator agrees with
itself — against numbers read from page images, at a tolerance of **0.1 mm**. The pattern is
the peer lane's, which matched the sail leading and trailing edges (3.0330 / 4.2413 ft,
Liu & Huang p.2) to the millimetre.

**ALL 29 MATCH. The largest deviation is 0.3 µm.** Representative rows:

| quantity | source (image-read) | expected | measured | Δ |
|---|---|---|---|---|
| hull overall length | Liu & Huang p.2: 14.2917 ft (4.356 m) | 4.356100 m | 4.356100 m | 0.0 µm |
| hull radius at the aft perpendicular | Groves Table 1: `rh`·`Rmax`, `rh` = 0.1175 | 0.029845 m | 0.029845 m | 0.0 µm |
| sail leading edge x | Liu & Huang p.2: 3.0330 ft | 0.924454 m | 0.924454 m | 0.0 µm |
| sail cap apex height | Groves Table 2: `Y_cap + Zmax/2` | 0.476250 m | 0.476250 m | 0.0 µm |
| fin tip radius (each of four) | Groves App. C: `RMAX = 0.833333` | 0.254000 m | 0.254000 m | 0.0 µm |
| fin TE x at the tip (each of four) | Groves Table 3: `h` = 13.146284, minus D1 | 4.006225 m | 4.006225 m | 0.0 µm |
| fin LE x at the tip (each of four) | Groves Table 3: `h − c(y)` | 3.854587 m | 3.854587 m | 0.0 µm |
| fin max full thickness at the tip (each of four) | Groves Table 3: `2·max(z/c)·c` | 0.030489 m | 0.030488 m | 0.3 µm |
| azimuth placement (0/90/180/270) | Groves p.6 | 0.025670 m | 0.025670 m | 0.2 µm |

**TWO CHECKS IN THE FIRST DRAFT OF THAT FILE WERE WRONG AND ARE RECORDED, NOT DELETED.** A
"parallel mid-body start" check read 3.28 ft against an expected 3.333333 ft and reported
MISMATCH. **The hull was not wrong; the check was** — Groves' forebody meets the parallel
middle body **tangentially**, so the radius is inside 10⁻⁵ of `Rmax` well upstream of the
join and the measurement located the tangency. Proven rather than asserted: the hull radius
at x = 3.333333 ft equals `Rmax` to < 10⁻¹² ft, and the verifier **refuses** if it does not.
It was replaced by the **sharper** aft-perpendicular row above. A second check compared the
sail cap *attachment* height against the sail's maximum y with a 20 mm tolerance that would
have passed almost anything; it was replaced by the cap **apex** height at the same 0.1 mm
tolerance as everything else. **Both replacements make the check harder, not looser.**

### 3.8 CLOSURE

All six surfaces (`hull`, `sail`, four fins) pass `surfaceCheck` after `surfaceOrient`:
**"Surface is closed"**, **"no illegal triangles"**, **"consistent normal) : 1"**. The
generator additionally refuses on any non-manifold directed edge or non-positive signed
volume before `surfaceCheck` is ever reached. Each fin: 155,118 triangles, signed volume
**1.30145 × 10⁻³ m³**, identical across the four as four identical appendages must be.

---

## 4. THE MESH FAMILY — ONE SCRIPT, THREE LEVELS

Sanaa: *"the family is generated from one script so L1/L2/L3 stay similar."*
`cases/navier_class/SUBOFF_HULL_SAIL_4STERNPLANES/build_appended_mesh.py` emits every level.

**FAMILY GENERATING RULE, inherited verbatim from the SUBOFF_A1 family so the two bodies'
ladders are comparable:** base cell × 1.5 per coarsening step, `nLayers` − 1, **every octree
level identical**. Nothing is tuned toward a target cell count; the delivered refinement
ratio is **measured from the built meshes afterwards, never fitted beforehand**.

| level | base cell | hull | sail | fin | sail-TE box | fin-TE box | junction | nLayers |
|---|---|---|---|---|---|---|---|---|
| L1 | 78.70 mm | 4 | 6→7 | 6→7 | 9 | 9 | 6 | 6 |
| L2 | 52.50 mm | 4 | 6→7 | 6→7 | 9 | 9 | 6 | 7 |
| L3 | 35.00 mm | 4 | 6→7 | 6→7 | 9 | 9 | 6 | 8 |

Hull and sail base cells and octree levels are **the SUBOFF_A1 family's, unchanged**, so
those two surfaces are resolved identically on both bodies and any difference in the graded
forces is attributable to the appendages rather than to the ladder.

### 4.1 HALF MODEL — AND WHY IT REMAINS EXACT WITH FOUR FINS

The body is mirror-symmetric about **z = 0**: the hull is axisymmetric, the sail lies in
that plane, the fins at 0° and 180° lie in it, and the fins at 90° and 270° are mirror
images of each other through it. Sanaa's sweep is in **PITCH**, so the free stream lies in
that same plane at every α. **The symmetry therefore holds for the whole sweep and the half
model is exact, not an approximation.**

**FORCE ACCOUNTING, REGISTERED HERE AND NOT DISCOVERED LATER.** The half domain contains
HALF of `fin000`, ALL of `fin090`, HALF of `fin180` and NONE of `fin270`. `fin270.stl` is
deliberately **not** copied into the case — it lies entirely outside the half domain and
would produce an empty patch. **Total body forces are 2 × the half-model forces**, and the
hull/fin split doubles the same way. All four fin STLs are nevertheless built and kept, so
the full body is reproducible.

### 4.2 GATES — `docs/standards/MESH_STANDARD.md`, unchanged, nothing relaxed

| gate | threshold | source |
|---|---|---|
| max non-orthogonality | **≤ 70°** hard, 65–70 warning band | §3.1 |
| max skewness, **boundary faces included** | **≤ 4** | §3.2 |
| aspect ratio | advisory 1000, never a lone rejection | §3.3 |
| cell-volume ratio | warn below 0.01 | §3.4 |
| grid levels | **three**, converging, with observed order and GCI at Fs = 1.25 | §9.1 (Sanaa's ruling) |
| non-orthogonality is read from | **the reported maximum**, never `checkMesh`'s verdict line | §14 |

### 4.3 🔴 THE CHECK THAT WAS `N/A` ON THE HULL+SAIL BODY AND IS **LIVE** HERE

Sanaa named it: *"the same layer check (growth ratio, layer coverage on the hull, sail and
fins, **cells across the appendage roots**)"*. On a finless body it was vacuous. **Here it
is the point.** Three root metrics are registered, each with its definition fixed **before
the mesh was built**, because "cells across a root" is exactly the phrase that can be
re-read after the fact to fit whatever the mesh delivered:

| id | **definition, fixed here** | floor | per |
|---|---|---|---|
| **RM1** — *"cells across the appendage root"*, Sanaa's named check | the fin's full thickness at the root maximum-thickness station (**46.47 mm**, from the source geometry) divided by the **MEASURED** median chordwise cell spacing on the fin patch within the root band | **≥ 16** | each fin |
| **RM2** | a direct **COUNT** of distinct cell-centre levels across the fin's root trailing-edge base (2.2299 mm) in the wake window — the same counting function the SUBOFF_A1 family uses on the sail base | **≥ 8** | each fin |
| **RM3** | a direct **COUNT** of distinct cell-centre levels along the fin's exposed span (171.3 mm) just off the fin surface | **≥ 24** | each fin |

**RM2 and RM3 are counts and therefore carry the rule-3 PLANTED-ZERO CONTROL**: a known
number of synthetic cell centres is pushed through the same counting function on every
invocation **before any mesh is read**, and the probe **refuses (exit 2)** unless the
function returns exactly that number and returns **0** for a window that excludes the plant.
A zero from a reader not shown able to see a non-zero is not evidence — and on a half model
at a fin root, zero is exactly what a probe in the wrong coordinate, the wrong units or the
wrong half looks like.

**RM1 is a ratio, not a count, and is labelled as one.** Its numerator is the source
geometry and its denominator is measured from the built mesh. It is reported as a ratio
because there are no cells **inside** a solid fin: a probe that tried to count cell centres
through the appendage would return zero for a perfectly good mesh.

**Also reported per patch (hull, sail, and each fin), from the `snappyHexMesh` layer table:**
layer coverage (% of patch faces carrying the full layer stack), achieved layer count, and
achieved growth ratio against the registered `expansionRatio 1.2`. The peer lane's hull
figure — **99.0 % coverage at 5.92 layers against a target of 6** — is the comparison point.

### 4.4 THE **MEASURED** MESH LINE — MESH_STANDARD §8.1

> *"No cfd mesh-ladder pre-registration is frozen until at least one level has been BUILT,
> `checkMesh`'d, and SHOWN ADMISSIBLE against the gates that registration will carry."*

**This is why this document is committed as a DRAFT first and frozen only after §11's
measured row is filled in.** The two rules compose without conflict: CLAUDE.md rule 2 gates
the **SOLVE**; MESH_STANDARD §8.1 gates the **FREEZE**. The order is therefore: build L1 →
`checkMesh` → fill §11 → freeze and commit → queue. **No solver runs before the freeze.**

**§11 IS EMPTY AT THIS COMMIT AND THAT IS DELIBERATE.** An assumed mesh line is exactly what
§8.1 exists to prevent: the F1 (ONERA M6) ladder was frozen from an assumed mesh,
arithmetically exact and **inadmissible at every level** (84.64 / 86.02 / 86.78° against a
70° gate, worsening under refinement).

---

## 5. 🔴 THE CONCAVE-CELL POPULATION — REGISTERED **BEFORE** THE MESH WAS BUILT

`snappyHexMesh` generates concave cells at refinement-level transitions. Measured by a peer
lane on this very case tonight: **≈ 12 % of transition cells are concave**, and **95.12 % of
concave cells sit on a refinement jump against a 15.93 % mesh baseline**. **This mesh will
have that population.** It is registered here, before the build, so that measuring it later
is a confirmation and not a discovery.

**WHEN THIS SECTION WAS WRITTEN, STATED PRECISELY BECAUSE "BEFORE" IS THE WHOLE
EVIDENTIARY CONTENT OF IT.** This section was written on 2026-09-12 between 22:55Z and
23:05Z. At that moment **no concave measurement of any kind had been taken on this body**:
`probe_appended_features.py` had not been written, no `checkMesh` had been run on any
appended mesh, and no `concaveCells` set existed anywhere under
`verification/runs/navier_class/SUBOFF_HULL_SAIL_4STERNPLANES/`. A first L1 castellation
attempt had been started at 22:54Z and was **stopped before completion** for the box-sizing
defect recorded in §4 — it produced no mesh, no `checkMesh` and no concave count. The
prediction below therefore precedes every number it will be checked against, and that is
checkable from the commit containing this file.

**THE PREDICTION, FALSIFIABLE AND RECORDED BEFORE MEASUREMENT:**

1. Concave cells will be present at every level.
2. **≥ 90 %** of them will sit on a refinement-level jump.
3. The population will be **denser on the fins than on the hull**, because the fins carry
   three octree levels within 80 mm of a 152 mm chord and the hull carries one.

**THE GATED QUANTITY IS AN AREA SHARE, NOT A CELL SHARE.** The two differ by more than a
factor of twelve, because concave cells live where the small cells are and small cells carry
small area. A cell share would overstate the population's weight on an integrated force by
an order of magnitude, in the flattering direction. The quantities and thresholds are
**inherited unchanged** from `SUBOFF_A1b_CONCAVE_FORCE_SHARE_PREREGISTRATION.md` (frozen
`bc73dc0cae2063477d9d54ee5512b93a68be3249`) — **this document invents no rival definition and
moves no threshold of that one**:

| id | quantity | available |
|---|---|---|
| **Q1** | `sum(area over C) / sum(area over all graded wall faces)` | from the mesh alone |
| **Q2** | `sum(\|viscous force\| over C) / sum(\|viscous force\| over all graded wall faces)` | at convergence |
| **Q3** | `sum(\|pressure force\| over C) / sum(\|pressure force\| over all graded wall faces)` | at convergence |

**F = max(Q2, Q3)** decides. Thresholds, unchanged: **F ≤ 1.0 %** disclosed nuisance,
CLOSED; **1.0 % < F ≤ 3.0 %** disclosed with the number quoted beside every force, every
time; **F > 3.0 %** material — forces **REPORTED, NOT GRADED**.

**THE ONE EXTENSION, STATED AS AN EXTENSION.** In A1b, `C` was the set of **hull** boundary
faces whose owner cell is in `concaveCells`. Here `C` is extended to **all graded wall
patches — `hull`, `sail`, and each fin** — and **Q1/Q2/Q3 are additionally reported per
patch**, so a population concentrated on the fins cannot hide inside a body-wide average
dominated by the hull's much larger area. The thresholds are not changed by the extension.

---

## 6. THE REFERENCE

> **Roddy, R. F. (1990), "Investigation of the Stability and Control Characteristics of
> Several Configurations of the DARPA SUBOFF Model (DTRC Model 5470) from Captive-Model
> Experiments", David Taylor Research Center, DTRC/SHD-1298-08, September 1990, AD-A227 715,
> Ship Hydromechanics Department.** Title page verified **as an image** under rule 15.

Band values from **Table 4, report page 19** (PDF p.27), **"Vertical Plane"**, the single
column headed `Config 1 / Fully Appended`, read as a page image at 160 dpi by this lane:

| item | value |
|---|---|
| **`Z_w'`** | **−0.013910** |
| **`M_w'`** | **+0.010324** |
| `Z_q'` | −0.007545 |
| `M_q'` | −0.003702 |
| `Z_ẇ'` | −0.014529 |
| `M_ẇ'` | −0.000561 |
| `Z_q̇'` | −0.000633 |
| `M_q̇'` | −0.000860 |
| `G` (margin of stability) | −1.162874 |
| `Z_δs'` | −0.005603 |
| `M_δs'` | −0.002409 |

### 6.1 SIGN AND AXIS CONVENTION — **INHERITED, ALREADY RULED, NOT RE-DERIVED**

The `M_w'` sign chain was settled in `SUBOFF_A1c_PREREGISTRATION.md` §7.1 and **signed by
the cfd-supervisor** (§7.1a, 2026-09-12). Gertler & Hagen axes: x-forward, y-starboard,
z-downward, right-handed; hence `M_w' = −N_v'` and `M_w' > 0` (the destabilising bow-up Munk
moment). **The discriminator is that the competing mapping predicts `M_w' = −0.012795` while
every `M_w'` Roddy measured is positive.** This act adopts that ruling and adds nothing to
it.

### 6.2 ⚠️ ONE NAMED ITEM THAT MUST BE IMAGE-VERIFIED BEFORE ANY GRADED NUMBER IS PRODUCED

The nondimensionalisation is registered as the **Gertler & Hagen (1967) prime system**:

```
Z' = Z / (½ ρ U² L²)      M' = M / (½ ρ U² L³)      w' = w/U = sin α
L = 14.291667 ft = 4.356100 m
```

**This lane did NOT read a Roddy nomenclature page stating it.** It is inherited from the
standard system that Roddy's own method section refers to. **It is registered as
`PENDING: <Roddy nomenclature page not yet image-verified>`** — a display/queue state under
CLAUDE.md rule 1, not a softened failure — and **no graded `Z_w'` or `M_w'` may be quoted
against the §7 band until that page is read as an image and this line is replaced by a dated
addendum.** A wrong normalisation would scale every derivative and the band would be
meaningless.

### 6.3 WHAT A STATIC SWEEP CANNOT PRODUCE, SAID PLAINLY

`Z_q'` and `M_q'` are **rotary** derivatives. Roddy obtained them from PMM oscillation and
rotating-arm experiments, not from a static sweep. **This act does not attempt them and
registers no band for them.** Roddy's own uncertainty for the rotary class is ~10 %
(report p.105).

### 6.4 THE α = 0 ANCHOR — `PENDING`, INHERITED FROM A1c §3.1

Sanaa specified *"Huang 1992 surface pressure at α = 0 as the anchor"*. A1c established, by
reading both Huang-authored reports, that **neither carries the `Cp` values**: SHD-1298-02 is
a test plan written in the future tense, and HD-1298-11 is a data **catalogue** whose Table 4
is a tap **inventory** (222 taps), not a data listing. **`Cp(α = 0)` is registered
`PENDING: <data files not held>`.** It is not a softened failure and it does not block the
sweep; it means the anchor is not yet gradeable.

---

## 7. 🔴 THE BAND — AND ALL FIVE BAND TRAPS CHECKED **BEFORE** THE FREEZE

Five ways a band has been got wrong in this team tonight. Each is answered explicitly.

**TRAP 1 — STATE THE BAND'S CENTRE.**
The centre is **Roddy's published value itself**: `Z_w' = −0.013910`, `M_w' = +0.010324`.
It is **not** our prediction, not a mid-point of anything we computed, and not a value
chosen after seeing a solve.

**TRAP 2 — STATE THE STATISTIC, AND WHY.**
Roddy's **total uncertainty** `U_tf`, combining bias `U_f` and precision `U_rf` in
quadrature: `U_tf² = U_f² + U_rf²` (report p.105, read as an image). Its precision component
comes from **the slope of normal force versus angle of attack being read independently by 10
engineers**: sample mean `Z_w' = −0.006489`, sample standard deviation `0.000262`,
`t₁ = 2.262`, `U_rf = 0.0289 f`. It is chosen because it is **the source's own combined
figure for exactly the two derivatives being gated**, verbatim:

> "The total uncertainties in the stability derivatives `Z_w'` and `M_w'` are calculated to
> be **about 4 percent** for both derivatives."

**TRAP 3 — IS THE PUBLISHED FIGURE A FULL WIDTH OR A HALF WIDTH?**
**A HALF WIDTH.** `U_rf = 0.0289 f` is expressed as a fraction **of the value** and enters
as a `±`; `U_tf` is the standard `±U` uncertainty interval half-width of the
Abernethy–Thompson methodology the page is using. **The band is value ± 4 %, total width
8 %.** Stated explicitly because reading 4 % as a *full* width would halve the band to ± 2 %
and gate this lab against an interval the source never stated.

**TRAP 4 — THE SOURCE GIVES A RANGE: GATE ON THE END THAT COULD EMBARRASS US.**
The same page assigns **"4 to 5 percent"** to the static-derivative class, and **"about 4
percent"** specifically to `Z_w'` and `M_w'`. **THE GATE IS ± 4 %** — the tighter and
therefore the less favourable end. **The ± 5 % reading is recorded beside it and DOES NOT
GATE.** A band taken at the kind end of a stated range is the easiest gate rather than the
honest one.

**TRAP 5 — WHAT BODY OR CONDITION WAS THE SOURCE'S UNCERTAINTY *FOR*?**
Verbatim from report p.105: *"…the following overall uncertainty errors may be assigned to
the experimental values of the stability and control derivatives **for fully appended
submarines**: (1) static derivatives `Z_w'`, `M_w'`, `Y_v'`, and `N_v'` 4 to 5 percent…"*

> 🟢 **THIS IS THE ONE PLACE TONIGHT WHERE THAT PHRASE HELPS RATHER THAN HURTS, AND IT IS
> SAID EXPLICITLY BECAUSE THE TEAM HAS BEEN BITTEN BY IT FOUR TIMES.** The peer lane's
> hull-and-sail arm had to **extend the source's own stated scope** to use this figure, and
> disclosed the extension as a weakness of its band (A1e §4.1). **This act does not extend
> it. Our body is an appended body and the scope is matched** — with the one residual
> geometry gap of §1, the ring wing, which is disclosed separately and, per §1.2, **buys no
> tolerance**.
>
> A second, smaller point in the same direction: the peer lane flagged the second symbol in
> item (1) as ambiguous in the scan between `M_q'` and `M_w'`. On this lane's 160 dpi render
> it reads **`M_w'`**, and item (2) separately lists the rotary set `Z_q', M_q', Y_r', N_r'`,
> which makes `M_w'` the only coherent reading. **Item (1) therefore names `Z_w'` and `M_w'`
> explicitly — the two quantities gated here.** Confirmed independently, not relayed.

### 7.1 THE BANDS

| quantity | Roddy `Config 1` value | **GATE, ± 4 %** | outer ± 5 % (recorded, does **not** gate) |
|---|---|---|---|
| **`Z_w'`** | −0.013910 | **[−0.01446640, −0.01335360]** | [−0.01460550, −0.01321450] |
| **`M_w'`** | +0.010324 | **[+0.00991104, +0.01073696]** | [+0.00980780, +0.01084020] |

**Neutral point**, `x_np/L = −M_w'/Z_w'` = `−0.010324 / −0.013910` = **0.742200**.
Roddy publishes **no uncertainty on the neutral point**, so its band is **PROPAGATED**, not
measured, and is labelled a tier below the two above: treating the two ± 4 % uncertainties as
independent gives ± 5.66 %, i.e. **[0.700186, 0.784214]**. **A propagated band is reported
and is not a measured-tier gate.**

**Reported, never gated:** the margin of stability `G` (Roddy: −1.162874), the hull / sail /
appendage force split, `y⁺` per patch at every α, and the `Z'(α)` and `M'(α)` curves
themselves.

### 7.2 🔴 THE ESTIMATOR — A MISMATCH BETWEEN SANAA'S METHOD AND RODDY'S, FOUND AND FIXED BEFORE THE NUMBERS EXIST

Sanaa registered *"derivatives by linear fit over |α| ≤ 8"*. **Roddy did not do that.**
Report page 4 (PDF p.12), read as a page image, verbatim:

> "The values for the static derivatives were determined directly **from the slopes at the
> origin** of curves of force and moment coefficients versus angle of attack and drift…
> All derivatives with respect to angular quantities are given as 'per radian.'"

A least-squares straight line over ±8° and the slope **at the origin** are **different
estimators**, and they differ by exactly the amount of cross-flow nonlinearity in the curve.
**This is settled now, before any solve, and the rule cannot be re-read afterwards:**

- **`D_fit`** — least-squares straight line through the five points `|α| ≤ 8`. **This is
  Sanaa's registered method and it is the PRIMARY GATE.**
- **`D_origin`** — the slope at the origin, obtained from the **same five points** by
  least-squares fit of the standard Gertler–Hagen form `Z'(w') = a₁ w' + a₃ w'|w'|`, with
  `Z_w' = a₁`. **This is the SOURCE-MATCHED estimator and is reported beside every gated
  row, always.**
- **The ESTIMATOR MISMATCH `|D_fit − D_origin| / |D_origin|` is computed and printed for
  every derivative, every time.** If it exceeds **4 %** — the band half-width — the row is
  labelled **ESTIMATOR MISMATCH MATERIAL** and **both** verdicts are printed, neither
  suppressed and neither chosen after the fact.

**Both instructions are honoured: Sanaa's fit gates, Roddy's estimator is shown, and which
one gates was fixed before the first solve.**

---

## 8. THE SWEEP, AND THE HULL / FIN SPLIT — WHICH IS NOW MEANINGFUL

- **Sweep points: α = −12, −8, −4, 0, +4, +8, +12 degrees** — Sanaa's, unchanged. Inside
  Roddy's own tested range (Table 3, report p.17: `Config 1` static stability at ± 18°;
  Liu & Huang p.6: vertical-plane statics −20° < α < 20°).
- **Quantities per point:** normal force `Z` and pitching moment `M`, nondimensionalised per
  §6.2, plus the axial force `X` reported.
- **THE HULL / FIN SPLIT.** On the hull+sail body this phrase was undefined — there were no
  fins. Here it is registered as a **three-way** split so that nothing is silently folded
  into the wrong group:

  | group | patches | full-body factor |
  |---|---|---|
  | **HULL** | `hull` | 2 × half-model |
  | **SAIL** (the bridge fairwater — neither hull nor stern appendage) | `sail` | 2 × half-model |
  | **STERN APPENDAGES** (the "fins") | `fin000_upper_rudder` + `fin090_horizontal` + `fin180_lower_rudder` | 2 × half-model, which reconstructs `fin000 + fin090 + fin180 + fin270` exactly |

  Sanaa's "hull/fin split" is satisfied by **HULL vs STERN APPENDAGES**; the sail is printed
  as its own row so that a reader can never be shown a "hull" number that quietly contains
  the fairwater, nor a "fin" number that does.
- **Derivatives over `|α| ≤ 8`** by both estimators of §7.2.
- **Neutral point** from `Z_w'` and `M_w'`, propagated band (§7.1).

---

## 9. TURBULENCE MODELLING — THE EXPERIMENT WAS TRIPPED, SO FULLY TURBULENT IS THE **MATCHED** CHOICE

`k-ω SST`, fully turbulent, no transition model — and this is **not** a mismatch to be
disclosed but a **match to be registered**.

**Liu & Huang 1998, report page 23, footnote to Table 14**, read as a page image by this lane:

> "Hull, bridge fairwater and four identical stern appendages all have tripwires installed
> at 5 percent of chord length."

> "Ringed wings have no turbulence stimulators applied to them"

**All four stern appendages carried tripwires, as did the hull and the sail. Transition was
forced by design, so the measured body was fully turbulent by design.** Registered with the
quotation and its page rather than carried as an unexamined assumption.

**The second footnote is recorded too, and it is not idle**: the ring wings were **not**
tripped. If the ring-wing arm of §1 is ever built, its boundary layer is **not** covered by
this justification and needs its own.

**A resistance reference exists for THIS body and does not exist for the hull+sail body.**
Liu & Huang Table 14, report page 23, read as a page image, `Config. No.` column:

| config as printed | 5.93 kt | 10.00 kt | 11.85 kt | 13.92 kt | 16.00 kt | 17.79 kt | residual resistance coeff. |
|---|---|---|---|---|---|---|---|
| `8  Fully Appended` (hull + sail + 4 appendages) | 102.3 N | 283.8 N | 389.2 N | 526.6 N | 675.6 N | 821.1 N | 0.00065 |
| `1  Bare Hull` | 87.40 N | 242.2 N | 332.9 N | 451.5 N | 576.9 N | 697.0 N | 0.00030 |

**Table 14 has no hull-and-fairwater-only row.** That asymmetry is in this act's favour and
is stated plainly. **These resistance numbers are recorded as available, and NO band is
registered on them here** — this act's registered quantities are `Z`, `M` and the vertical
plane derivatives, and adding a drag gate after the fact would be a new gate, not this one.

---

## 10. COST — REGISTERED, AND IT DOES NOT STOP THE RUN

Sanaa, same directive: *"Cost estimate registered too but doesnt stop the run"*, and
directive #17 of 2026-09-12 (NO CAP): no run is stopped by a time or budget cap.

**Measured basis, not assumed.** The live SUBOFF_A1 `SOLVE_L1_R3` (a peer lane's run, read
**read-only** and not touched): 3,268,613 cells, 4 ranks, 564 iterations at
`ExecutionTime = 3225.8 s` → **0.1166 core-min per million cells per iteration**.

| item | cells (est.) | iterations | ranks | **core-min (est.)** |
|---|---|---|---|---|
| L1 mesh build | — | — | 16 | **filled in §11 from the measurement** |
| 7 sweep points at the graded level | ~6 × 10⁶ | 3,000 | 16 | **≈ 14,700** |
| L2 for the Roache triple at α = +8 | ~17 × 10⁶ | 3,000 | 32 | **≈ 5,950** |
| L3 for the Roache triple at α = +8 | ~47 × 10⁶ | 3,000 | 64 | **≈ 16,700** |
| **TOTAL** | | | | **≈ 37,300 core-min = 622 core-h** |

**`cost_basis`: REPORTED-BY-OWNER, NOT MEASURED — and the stated rate is now additionally
STALE.** CLAUDE.md fixes the rate at **c7a.4xlarge, $0.0513/core-h**, owner-stated
2026-08-21/22. At that rate 622 core-h **derives** to **≈ $31.90**. But the box this lane is
running on reports **`nproc` = 96 and 739 GiB of memory** (measured, 2026-09-12T22:42Z) —
**it is not a c7a.4xlarge and it is not the 16-core r7a.4xlarge of the 2026-09-12 resize
census either.** The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so
the dollar figure is **derived, not measured, at a rate that belongs to a different instance
type**. It is reported that way and nothing is gated on it. **The instance-type change is
flagged to the cfd-supervisor as a cost-calibration item under CLAUDE.md rule 12.**

Estimate-versus-actual calibration is owed at completion, per rule 12, into
`docs/COST_CALIBRATION.md`.

---

## 11. THE MEASURED MESH ROW — **EMPTY AT THIS COMMIT** (MESH_STANDARD §8.1)

*To be filled from the BUILT L1 mesh before the freeze block in §12 is signed. An assumed
row here is precisely what §8.1 exists to prevent.*

| quantity | gate | **MEASURED** |
|---|---|---|
| cells, L1 | — | |
| max non-orthogonality (the **reported maximum**, §14) | ≤ 70° | |
| max skewness (boundary faces included) | ≤ 4 | |
| max aspect ratio | advisory 1000 | |
| **RM1 cells across the appendage root**, per fin | ≥ 16 | |
| **RM2 cells across the fin root TE base**, per fin | ≥ 8 | |
| **RM3 cells along the fin exposed span**, per fin | ≥ 24 | |
| cells across the sail TE base | ≥ 8 | |
| layer coverage / achieved layers — hull | reported | |
| layer coverage / achieved layers — sail | reported | |
| layer coverage / achieved layers — each fin | reported | |
| achieved growth ratio vs `expansionRatio 1.2` | reported | |
| concave cells: count, % on a refinement jump, **Q1 AREA share** per patch | §5 | |
| L1 mesh cost, core-min | reported | |

---

## 12. WHAT THIS ACT DOES **NOT** CLAIM

1. It is **not** Roddy's Configuration 1. It lacks ring wing no. 1 and four support struts
   (§1), and the gap is disclosed in every band this act produces.
2. It produces **no** `Z_q'` and **no** `M_q'` (§6.3).
3. It produces **no** graded `Cp` anchor (§6.4).
4. It registers **no** drag band, despite holding a matched resistance reference (§9).
5. It says nothing about the hull+sail body of A1b/A1e, and moves none of their gates.
6. Its neutral-point band is **propagated**, not measured (§7.1).
7. Its nondimensionalisation is `PENDING` on one named image-verification (§6.2), and **no
   graded derivative may be quoted until that is discharged**.

---

## 13. FREEZE

**NOT FROZEN AT THIS COMMIT.** This document is committed as a draft so that §5's concave
prediction and §7's bands are on the record **before** the mesh exists and **before** any
solver starts. It is frozen by a dated addendum that fills §11 from the built mesh and
carries the cfd-supervisor's signature. After that freeze no band, threshold, gate, cap or
label above may be altered; departures land as dated addenda that strike the original
legibly and never rewrite it.

**Nothing is sent, filed, uploaded or submitted anywhere (CLAUDE.md rule 7).**
