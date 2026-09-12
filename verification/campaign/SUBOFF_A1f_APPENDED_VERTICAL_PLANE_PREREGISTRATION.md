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

---
---

# ADDENDUM 1 — 2026-09-12 — **THE §7.1 GATE IS STRUCK**, CHECK (C) IS ANSWERED **NO**, AND TWO LOAD-BEARING CONSTANTS WERE WRONG

**Appended at the foot. Lines whose number changed above this section: 0.** Nothing above is
edited, struck in place or renumbered. §7.1's band table is **struck by this addendum**, which
is how a departure lands; the original text stays legible above so that what was proposed, and
why it was withdrawn, can both be read.

**AMENDMENT CONDITION (rule 2), STATED AND CHECKED, NOT ASSUMED.** Amendments before first
compute are legal. The condition is that no compute has occurred under this document. Checked
at the time of writing: the solve directories this document registers —
`verification/runs/navier_class/SUBOFF_HULL_SAIL_4STERNPLANES/SOLVE_A*` — **do not exist**, no
entry for this act exists in `verification/queue/cfd/`, and no solver has been started by it.
Only a mesh has been built, which §4.4 requires *before* the freeze and which grades nothing.

---

## A1.1 THE DIRECTION, AND WHY THIS LANE ACCEPTS IT

The cfd-supervisor directed, on reading §1 and §2.1 of this document, that this lane must not
register a band against Roddy's `Configuration 1` for a body that has no ring wing, under any
circumstances; and that a check — **(C)** below — be run and reported before any route is
chosen.

**This lane had, in fact, done to itself exactly what §2 exists to prevent.** §2.1 established
that "fully appended" names two different bodies, applied that finding to a peer lane's arm,
and then **registered a band in §7.1 against the very column whose body §1 had just shown we
are not building**. The naming collision moved the target through a different door. That is
recorded here as this lane's own error, not as a correction received.

**§7.1's GATE IS STRUCK.** No `±4 %` gate on `Z_w'` or `M_w'` against Roddy `Config 1` is
registered by this document for the hull + sail + four-stern-appendage body. §7's five band
traps, §7.2's estimator ruling and §6.1's sign ruling are **methodology and stand**; what is
struck is the application of the band to a body that does not match the column.

---

## A1.2 🔴 CHECK (C), RUN AND ANSWERED: **NO DOCUMENT ON THIS BOX PUBLISHES VERTICAL-PLANE α-DERIVATIVES FOR A BODY WITHOUT A RING WING**

The question: does **any** source in the programme publish `Z_w'` / `M_w'`, or the
angle-of-attack curves they come from, for a configuration carrying **no** ring wing? If one
does, the gap evaporates. **It does not.** Six independent pieces of evidence, every one read
from a rendered page image:

1. **Roddy Table 3, "Schedule of the stability and control experiments", report pages 17–18.**
   This is the schedule of what was actually run. `CONFIGURATION 1` is headed **VERTICAL
   PLANE**; Configurations **2, 3, 4, 5 and 6 are every one of them headed HORIZONTAL PLANE.**
   No vertical-plane experiment was run on any body other than Configuration 1.
2. **Roddy LIST OF TABLES, report page vi.** The report contains **exactly four tables**:
   1 geometry, 2 hull offsets, 3 the schedule, 4 the derivatives. **There is no appendix table
   of further derivatives.** Table 4 (report p.19) is the only derivative table in the
   document, and its "Vertical Plane" half has **one column**.
3. **Roddy LIST OF FIGURES, report pages iv–vi.** Every figure whose caption carries "angle of
   attack", "sternplane angle", "normal force" or "pitching moment" as a primary variable —
   figures 7 through 21 — names **Configuration I**. No other configuration appears in a
   vertical-plane figure.
4. **The two apparent exceptions are not exceptions, and they are the interesting rows.**
   Figure **65**, *"Effect of angle of DRIFT on the out-of-plane normal force and pitching
   moment for Configuration 2"*, and figure **68**, the same for **Configuration 4 (HULL AND
   SAIL ONLY)**. These do carry `Z` and `M` for a hull-and-sail body — but as the **out-of-plane
   response to DRIFT β**, i.e. the cross-derivatives `∂Z/∂β` and `∂M/∂β`. **They are not
   `Z_w'` and `M_w'` and cannot be fitted into them**, because β and α are different
   independent variables.
5. **Liu & Huang 1998, report page 6, PMM list**, read as an image: *"Vertical plane statics -
   angle of attack variation, −20° < α < 20°: **Configuration 1, Configuration 6**"*. Even the
   second vertical-plane configuration **carries a ring wing in BOTH naming schemes in play** —
   Roddy's Config 6 is `HULL AND RING WING NO.1 ONLY` and Liu & Huang's own AFF list item 6 is
   `axisymmetric body with ring wing 1`. **Both vertical-plane bodies in the entire programme
   have a ring wing.**
6. **Nothing else on the box carries values.** Liu & Huang 1998 is a data **catalogue** whose
   tables are directories, test numbers, file structures and a tap inventory (A1c §3.1);
   Huang 1989 SHD-1298-02 is a **test plan** written in the future tense. A filesystem sweep
   for further SUBOFF documents returns only two `.url` stubs in an off-repository reference
   pack.

> **ANSWER TO (C): NO.** The vertical-plane derivative set Sanaa named exists for ring-wing
> bodies only. **Route (B) therefore cannot become a graded arm by finding a better table, and
> this is an evidence-based refusal that a better download cannot overturn.**

---

## A1.3 I NARROW MY OWN §1.1 CLAIM — THE SUPERVISOR'S OBJECTION IS PARTLY RIGHT

§1.1 argued that a ring wing is axisymmetric about the hull axis, so its increment is
plane-independent **by geometry**, and that the horizontal-plane bound therefore transfers to
the vertical plane. **That argument is sound for the ISOLATED ring wing on the BARE HULL and is
NOT sound for its increment on the APPENDED body**, and the distinction was not drawn.

- **Where it holds:** Roddy's `Config 6` is hull + ring wing 1 and nothing else. That body is
  genuinely axisymmetric, so a cross-flow at α sees exactly what a cross-flow at β sees, and
  `|Z_w'| = |Y_v'|` for it — the same argument A1c §2.2 uses for the bare hull.
- **Where it fails:** on the fully appended body the ring wing sits **downstream of the sail
  and of four appendages at four clock positions**. Its inflow is their wake and is **not**
  axisymmetric. **The ring wing's increment on the appended body is therefore not
  plane-independent, and Roddy publishes no vertical-plane increment for anything, so there is
  nothing to check a transfer against.**

**The measured horizontal-plane figures of §1.1 stand as measurements** — ring wing alone:
`+0.000005` in `Y_v'` (0.08 %), `−0.000144` in `N_v'` (1.13 %); appendage superposition
reproducing `Config 2` to 1.02 % and 3.58 %. **What is withdrawn is using them as a bound on a
vertical-plane gap.** They are reported as what they are: evidence that appendage superposition
holds on this body to about the level of Roddy's own stated uncertainty, in the drift plane.

---

## A1.4 🔴 TWO LOAD-BEARING CONSTANTS IN §6.2 WERE WRONG, AND BOTH WOULD HAVE CORRUPTED EVERY GRADED NUMBER SILENTLY

§6.2 registered the normalisation as `PENDING` on one named image-verification and inherited
`L = 14.291667 ft = 4.356100 m`, the **overall length**. That verification has now been done,
and **the inherited value was wrong**. Roddy, report page 3 (PDF p.11), read as a page image,
verbatim:

> "The hydrodynamic force and moment measurements were nondimensionalized using **the length
> between perpendiculars of 13.9792 feet (4.261 m)**. The notation used in this report is given
> in Reference 6."

and, on the same page:

> "The values of the derivatives determined from the data in the appendix are given in Table 4.
> These derivatives are referred to the axes which have their **origin 6.6042 feet (2.013 m)
> aft of the forward perpendicular (nose) on the hull centerline.** The location of the
> reference point did not correspond with the longitudinal location of the center of buoyancy
> for any of the configurations evaluated."

**CORRECTION 1 — THE REFERENCE LENGTH IS THE LBP, NOT THE LOA.**
`L_ref = 13.9792 ft`. Groves' own aft perpendicular is at `x = 13.979167 ft`, so the two agree
and the 0.3125 ft afterbody cap lies **beyond** the reference length. Registered:
**`L_ref = 13.979167 ft = 4.260851 m`**.
**Magnitude of the error avoided, computed:** using the overall length would inflate `M'` by
`(4.356100 / 4.260851)³ = 1.0690` — a **6.90 % error** — and `Z'` by `1.0453`, a **4.53 %
error**. **Both exceed the ±4 % band.** A correct solve would have been graded `GATE FAIL`
with confidence, and nothing downstream would have caught it.

**CORRECTION 2 — THE MOMENT REFERENCE POINT IS NOT THE MID-LENGTH AND NOT THE CENTRE OF
BUOYANCY.**
Registered: **`CofR = (2.013 m, 0, 0)`** in the case frame (nose at `x = 0`), i.e.
`6.6042 ft = 0.47243 L_ref` aft of the nose. Roddy says explicitly that it does **not**
coincide with the LCB of any configuration, so the LCB must not be substituted for it. A wrong
moment origin shifts `M` by `Δx · Z`, which at the outer sweep points is a first-order error on
the graded quantity.

**CORRECTION 3 — THE MATCHED CONDITION.** Roddy, same page: *"The static stability experiments
were conducted at a model speed of 6.5 knots which corresponds to a Reynolds number (based on
the length between perpendiculars) of about 14 million."* Registered condition:
`U = 6.5 kn = 3.343333 m/s`, `ν = 1.0 × 10⁻⁶ m²/s`, `L_ref = 4.260851 m`, giving
**`Re_LBP = 1.4245 × 10⁷`** — which reproduces Roddy's "about 14 million". **This differs from
the SUBOFF_A1 family's registered `Re_L = 1.2 × 10⁷` on the overall length**, and the
difference is a change of both reference length and speed, not a rescaling of one.

**The functional form of the prime system remains inherited**, not read: `Z' = Z/(½ρU²L_ref²)`,
`M' = M/(½ρU²L_ref³)`, `w' = w/U = sin α`, from Gertler & Hagen, which is what Roddy's
"Reference 6" notation and his Reference 4 reduction procedure point to. **Reference 6 itself
was not retrieved.** That much of §6.2's `PENDING` is **not** discharged and is carried
forward, narrowed to the form alone: the two constants that would have done the damage are now
read from the page.

---

## A1.5 THE ROUTES, AND THIS LANE'S READING — **THE DECISION IS THE SUPERVISOR'S AND IS NOT TAKEN HERE**

**A fact that changes the cost calculus and was not in the supervisor's framing:
Roddy's `Configuration 1` is a strict SUPERSET of the body already built.**
`Config 1 = (hull + sail + four stern appendages) + ring wing no. 1 + four support struts`.
So route (A) is an **increment on this build, not a replacement for it**: every STL, the
byte-identity regression, the corroboration suite, the mesh family script and the root metrics
carry forward unchanged, and the ring wing enters as two further closed solids.

**Its geometry source is on the box and is dimensioned to the same standard as the appendages
already built** — Groves 1989 **Table 4** (ring wings, report pp.15–16), **Table 5** (struts,
report pp.19–20, including `Strut leading edge attaches to: at x = 13.589, R = 0.14726`),
**Figure 7** (placement), and **Appendices D and E** (the generating FORTRAN). Their existence
and location are verified; **their contents have not been read by this lane and nothing here
depends on them.** Route (A) is therefore not blocked on retrieval.

**AND RUNNING BOTH BODIES PRODUCES, BY SUBTRACTION, THE ONE NUMBER RODDY NEVER PUBLISHED.**
The supervisor is right that the vertical-plane ring-wing increment cannot be estimated from
Roddy's data. **It can be MEASURED by us**, because the two bodies differ by exactly the ring
wing and struts. That converts the §1 gap from an unquantifiable disclosure into a measured
result of our own, and it is the strongest scientific argument for doing both.

**Against route (A), stated because it is real and cuts against this lane's own preference:**
the ring wings were **not tripped** — Liu & Huang p.23, second footnote, *"Ringed wings have no
turbulence stimulators applied to them"* — so §9's fully-turbulent justification, which is
**matched** on hull, sail and appendages, is **not** justified on the ring wing. Route (A) buys
a matched geometry at the price of an unmatched transition treatment on the added surface.
Route (A)'s body is also a research configuration, not the body the CFD community validates
against, so no external result would be comparable to it.

**For route (B), also stated plainly:** its body **is** the community-standard validation
configuration, and it is the one body in this programme for which **this box holds a matched,
tripwire-matched, measured reference that the hull+sail body does not have** — Liu & Huang
Table 14, report p.23, the row printed `8  Fully Appended`, six speeds with a residual
resistance coefficient of 0.00065 (§9). **That is a resistance reference, not a `Z`/`M` one,
and no band on it is registered here** — it would be a new gate, needs its own submergence and
Reynolds-matching analysis, and is named only so the supervisor's decision is taken with it in
view.

> **THIS LANE'S READING, submitted and not acted on:** route **(A)**, built as an increment on
> what already exists, with route (B)'s body retained as the second arm — because it is the
> only route to Sanaa's sweep with a matched measured-tier band, because it costs the existing
> build nothing, and because the two arms together measure the ring-wing increment that no
> document publishes. **If the supervisor takes route (B) instead, this document's §8 sweep
> runs unchanged and Z, M, the split, the derivatives and the neutral point are REPORTED, NOT
> GRADED, with the absence of a comparator disclosed rather than manufactured.**
>
> **Neither is chosen by this lane. Nothing is queued. No solver is started.**

---
---

# ADDENDUM 2 — 2026-09-12 — **ROUTE (A) IS RULED**, AND THE RING WING AND STRUTS ARE DEFINED FROM THE PRIMARY SOURCE, WITH **FOUR SCAN DEFECTS FOUND AND RESOLVED**

**Appended at the foot. Lines whose number changed above this section: 0.**

**AMENDMENT CONDITION (rule 2), STATED AND CHECKED.** No compute has occurred under this
document: `verification/runs/navier_class/SUBOFF_HULL_SAIL_4STERNPLANES/SOLVE_A*` do not
exist, no `verification/queue/cfd/` entry references this act, and no solver has been started
by it. Only mesh building has occurred, which §4.4 requires before the freeze.

---

## A2.1 THE RULING

The cfd-supervisor ruled **route (A), built as an increment, with route (B)'s body kept as the
second arm**, on the grounds that (i) only (A) delivers Sanaa's registered instruction, since
Addendum 1's check (C) established that no vertical-plane derivative exists for a non-ring-wing
body; (ii) `Config 1` is a strict **superset** of the body already built, so (A) costs the
existing work nothing; and (iii) **the two-body pair MEASURES the vertical-plane ring-wing
increment that Roddy never published**, because the two bodies differ by exactly the ring wing
and struts.

**A CAVEAT THAT IS SCOPED, AND THE SCOPING IS THE POINT.** §9 registers a fully-turbulent
closure as **matched**, on the tripwire footnote. Liu & Huang's **second** footnote on the same
page reads *"Ringed wings have no turbulence stimulators applied to them"*. That mismatch
applies **only to comparing the ring-wing arm against Roddy's measured `Config 1`**. It does
**not** touch the ring-wing increment, because **both of our solves are fully turbulent, so the
DIFFERENCE between them is internally consistent whatever the transition treatment.** One
clearly-scoped caveat on one arm, not a defect in both results.

**No band is registered on Liu & Huang Table 14's resistance row.** It would be a new gate and
needs its own submergence and Reynolds-matching analysis.

---

## A2.2 🔴 A BINDING RULE FOR THIS FAMILY, MADE BY THE cfd-SUPERVISOR ON ADDENDUM 1's FINDING

> **A DERIVATIVE'S BAND IS MEANINGLESS WITHOUT THE REFERENCE LENGTH, REFERENCE AREA AND MOMENT
> ORIGIN THE SOURCE USED. All three are quoted from the source's own page into every
> registration, beside the value.**

Discharged here, verbatim from **Roddy 1990, report page 3** (PDF p.11), read as a page image:

> "The hydrodynamic force and moment measurements were nondimensionalized using **the length
> between perpendiculars of 13.9792 feet (4.261 m)**."

> "These derivatives are referred to the axes which have their **origin 6.6042 feet (2.013 m)
> aft of the forward perpendicular (nose) on the hull centerline.** The location of the
> reference point **did not correspond with the longitudinal location of the center of
> buoyancy** for any of the configurations evaluated."

> "The static stability experiments were conducted at a model speed of **6.5 knots** which
> corresponds to a Reynolds number (based on the length between perpendiculars) of **about 14
> million**."

**Registered, and every case is built on these from the start rather than corrected later:**
`L_ref = 13.979167 ft = 4.260851 m` · `CofR = (2.013, 0, 0) m` · `U = 3.343333 m/s` ·
`ν = 1.0 × 10⁻⁶ m²/s` · `Re_LBP = 1.4245 × 10⁷`.

---

## A2.3 THE RING WING — Groves 1989 **Table 4, report pages 15–16**, cross-read against **Appendix D, report pages 68–71**

Both read as rendered page images. Appendix D's own header states the section family, which is
itself a corroboration of the coefficient set:

> "THE DARPA2 WINGS USE THE **NACA 66 (DTNSRDC MOD) THICKNESS DISTRIBUTION** AND THE **NACA
> a = 0.4 MEANLINE**."

**RING WING 1** (the one in Roddy's `Configuration 1`), from Table 4 and confirmed by
Appendix D's `DATA` statements:

| | x (ft) | R (ft) |
|---|---|---|
| leading edge | **13.46990** | **0.43004** |
| trailing edge | **14.21661** | **0.35659** |

Derived: chord `C = 0.750314 ft`, setting angle `φ = atan2(R_TE − R_LE, x_TE − x_LE) =
−5.6178°` (a converging shroud). Radial clearance to the hull: **77.39 mm at the LE, 89.29 mm
at the TE** — the gap the struts bridge.

**Meanline** (`0 ≤ x ≤ 1`, `D = 0.4 − x`, `E = 1 − x`):
`y_c = −0.049921 [0.5 D² ln|D| − 0.5 E² ln E + 0.25 E² − 0.25 D²] + 0.029953 [x ln x + 0.227828 − 0.531076 x]`
**Slope** (Appendix D, needed for the surface construction and **not printed in Table 4**):
`y_c' = −0.049921 [E ln E − D ln|D|] + 0.02995253 [ln x + 0.4689244]`, and `θ = atan(y_c')`.

**Thickness**, two branches of one curve:
`y_t = 0.1 Σ_{n=1..17} b_n sin(n ω)`, `ω = arccos(2x − 1)`, for `0 ≤ x < 0.45`;
`y_t = 0.1 [0.033333 + 1.696969 X + −1.441945 X² − 0.366363 X³ + 0.333049 X⁴]`, `X = 1 − x`,
for `0.45 ≤ x ≤ 1`.

**Surface and placement** (Appendix D, which also resolves Table 4's duplicated label):
`x_U = x − y_t sinθ`, `R_U = y_c + y_t cosθ`, `x_L = x + y_t sinθ`, `R_L = y_c − y_t cosθ`;
then `x_D = x_LE + C(x_* cosφ − R_* sinφ)` and `R_D = R_LE + C(x_* sinφ + R_* cosφ)`, with the
**pre-rotation** `x_*` used in the `R_D` line — a detail the listing makes explicit
(`XUU`, `XLL`) and which a careless implementation gets wrong.

### A2.3.1 🔴 FOUR DEFECTS IN THE PRINTED TABLES, FOUND AND RESOLVED — THIS IS WHY THE PAGES ARE READ AS IMAGES AND CROSS-READ AGAINST THE LISTING

| # | what Table 4 / Table 5 prints | what it must be | how it was settled |
|---|---|---|---|
| **1** | thickness coefficient **`b₅ = −0.90185`** | **`b₅ = −0.00185`** | Appendix D's `DATA B` array reads `−0.00185`, **and a numerical discriminator settles it independently** — see below |
| **2** | camber: `… + 0.029953 [x ℓnx + 0.227828 **=** 0.531076x]` | `… **−** 0.531076 x` | Appendix D: `YC(I) = YC(I) + 0.029953*(X*ALOG(X) + 0.227828 - 0.531076*X)` |
| **3** | placement block prints **`R_DU`** twice; the fourth line has no `R_DL` | the fourth line is **`R_DL`** | Appendix D computes `YL(I)` there |
| **4** | strut section: `… + 0.28520 ξ**²** …` | **`ξ³`** | the same five coefficients as Groves Table 3's stern appendage, where the exponent is 3; and the coefficients sum to zero only as a quartic in the 4-digit form |

> **THE DISCRIMINATOR FOR DEFECT 1, AND IT OWES NOTHING TO THE LISTING.** The 17-term sine
> series and the quartic polynomial are **two branches of one curve** and must agree where they
> meet at `x = 0.45`. **With `b₅ = −0.00185` they agree to `1.34 × 10⁻⁶`. With the printed
> `b₅ = −0.90185` they disagree by `7.89 × 10⁻²` — fifty-nine thousand times worse.** The
> correct value is therefore established by an internal consistency test of the table against
> itself, not merely by preferring one scan to another.

### A2.3.2 SELF-CHECKS ON THE RING-WING DIGITS, ALL **MEASURED**

| check | result | what it confirms |
|---|---|---|
| thickness branches agree at `x = 0.45` | **series 0.0499987 vs polynomial 0.0500000**, diff `1.3 × 10⁻⁶` | all 17 `b_n` and all five polynomial coefficients |
| maximum full thickness | **`t/c = 0.09999`** — a round 10 % | the NACA 66 (DTNSRDC mod) family the listing names |
| meanline vanishes at both ends | `y_c(0) = +1 × 10⁻⁷`, `y_c(1) = −1 × 10⁻⁷` | the camber constants and the `−0.531076x` correction of defect 2 |
| maximum camber and its station | **`0.01960 c` at `x/c = 0.3948`** | the **NACA a = 0.4** meanline the listing names — the peak sits at 0.4 |

---

## A2.4 THE RING-WING STRUTS — Groves 1989 **Table 5, report pages 19–20**

Narrative, report page 18 (PDF p.25), read as an image: *"Four separate, identical struts are
mounted equally-spaced along the hull girth. The struts attach at the same axial position on
the hull, x = 13.589 Ft (4.142 m)… At the inner surface of each wing, the struts are contoured
to match each wing."* Table 5's own header adds: *"These equations define a single strut which
attaches to the DARPA2 axisymmetric hull **along the upper surface (i.e., the surface with the
fairwater)**."*

```
x = x₀ + 0.243995 ξ
y = y₀ − 0.054465 ξ
z = ± 0.15 (0.29690 √ξ − 0.12600 ξ − 0.35160 ξ² + 0.28520 ξ³ − 0.10450 ξ⁴)
x₀ = 0.223221 y₀ + 13.556128        R1 ≤ y₀ ≤ R2
Ring Wing 1:  R1 = 0.14726,  R2 = 0.36886
0 ≤ ξ = (x − x₀)/0.243995 ≤ 1
HULL/STRUT INTERSECTION:      [R_HA(x)]² = y² + z²
RING WING/STRUT INTERSECTION: [R_WL(x)]² = y² + z²
```

### A2.4.1 SELF-CHECKS ON THE STRUT DIGITS — **THE WHOLE EQUATION SET IS CONFIRMED TO MICROMETRES BY THE REPORT'S OWN QUOTED ATTACHMENT POINTS**

| check | computed | Table 5 prints | Δ |
|---|---|---|---|
| `x₀(y₀ = R1 = 0.14726)` | **13.589000** | `Hull at x = 13.589` | **exact** |
| `x₀(y₀ = R2 = 0.36886)` | **13.638465** | `Ring Wing 1 at x = 13.63845` | 1.5 × 10⁻⁵ ft = **4.6 µm** |
| hull radius at the LE attachment, from **Table 1's** afterbody equation | **0.147256** | `R = 0.14726` | 4 × 10⁻⁶ ft = **1.2 µm** |
| **hull/strut TE intersection**, solved through Table 1's hull from the Table 5 generator | **x = 13.83582, R = 0.10546** | `x = 13.83582, R = 0.10547` | x **exact to 5 dp**, R = **3 µm** |
| section coefficients sum | **−1.39 × 10⁻¹⁷** | — | closed trailing edge |
| maximum thickness | **`t/c = 0.12299` at `ξ = 0.2997`** | — | the same NACA 4-digit family, 12.3 % thick |

**The fourth row is the strong one.** It computes the strut's trailing-edge attachment by
intersecting Table 5's generator with **Table 1's hull equation** — two different tables of the
report, neither of which knows about the other — and lands on the third table's printed answer
to five decimal places in `x`. A transposed digit anywhere in that chain breaks it.

### A2.4.2 ONE ITEM LEFT OPEN RATHER THAN GUESSED: THE STRUT AZIMUTHS

Table 5 says the defined strut attaches **along the upper surface, the surface with the
fairwater** — i.e. at top dead centre, azimuth 0° — and that four identical struts are
**equally spaced**, which gives **0°, 90°, 180°, 270°: the same azimuths as the four stern
appendages.** But the same paragraph also says the four struts sit *"at a 45° increment from
the wing surface pressure tap locations"*, which is a statement about the **taps**, not about
the appendages, and **Figure 9** — *"a typical cross section showing the arrangement of the
strut to the hull and the ring wing"*, report page 18 — has **not been read by this lane**.

> **REGISTERED AS `PENDING: <Groves Figure 9 not yet read as an image>`.** The working reading
> is **0/90/180/270**, and it is **not** frozen. The alternative, struts at **45/135/225/315**
> staggered between the appendages, is the more usual engineering choice and would place the
> struts **out of** the appendage wakes rather than in them. **The two differ physically** — a
> strut in an appendage's wake is a different flow — so this is not a cosmetic choice and it is
> not settled by preference. **No ring-wing geometry is emitted until Figure 9 is read.**

---

## A2.5 WHAT EXISTS AND WHAT DOES NOT, AT THIS COMMIT

**Exists, built and verified:** the hull + sail + four-stern-appendage geometry (§3), its
byte-identity regression (§3.6), its 29-check corroboration (§3.7), the family mesh script
(§4) and the L1 mesh build.

**Does NOT exist:** any ring-wing or strut STL, any ring-wing generator code, any mesh of the
`Config 1` body, and any solve of anything. **The ring wing and struts are DEFINED here and are
NOT BUILT here.** The definition is recorded first, with its four scan defects resolved and its
digits checked to micrometres, because that is the irreversible half of the work; the generator
is mechanical once the definition is right, and it is blocked on one named image-read (§A2.4.2).

---
---

# ADDENDUM 3 — 2026-09-12 — **§A2.4.2's `PENDING` IS DISCHARGED, AND THE WORKING READING WAS WRONG**

**Appended at the foot. Lines whose number changed above this section: 0.**
**AMENDMENT CONDITION (rule 2), CHECKED:** `SOLVE_A*` absent, no queue entry, no solver run.

**Groves 1989, Figure 9, report page 22** (PDF p.29), *"Typical cross section showing ring wing
strut arrangement"*, read as a rendered page image — **which §A2.4.2 registered as the one item
blocking any ring-wing geometry, and which this lane had not read when it wrote that section.**

**THE FOUR STRUTS ARE AT 45°, 135°, 225° AND 315° — STAGGERED BETWEEN THE STERN-APPENDAGE
AZIMUTHS, NOT ALIGNED WITH THEM.**

> **§A2.4.2's WORKING READING WAS `0/90/180/270` AND IT WAS WRONG.** The alternative it named
> is the correct one. The `PENDING` was the thing that saved it: had the working reading been
> frozen, the ring-wing assembly would have been built with all four struts sitting **in** the
> four stern-appendage wakes instead of clear of them, which §A2.4.2 stated in advance is a
> **physical** difference and not a cosmetic one. **This is what a `PENDING` on a specific,
> named image-read is for, and it is recorded as a near miss rather than as a tidy result.**

**THREE INDEPENDENT LINES OF EVIDENCE, ALL ON THAT ONE PAGE:**

1. **The drawing.** The hull circle sits at the centre, the ring wing as an annulus around it,
   and the four members labelled `STRUT` are drawn on the **diagonals**, plainly not on the
   axes.
2. **The tap names are cardinal directions, which fixes the absolute rotation.** The pressure
   taps are drawn **on** the axes and are labelled `W1U1`, `W1L1`, `W1P1`, `W1S1` —
   **U**pper, **L**ower, **P**ort, **S**tarboard. So the taps lie at 0° (top dead centre),
   180°, 270° and 90° — **the same four azimuths as the stern appendages** — and the struts
   lie between them.
3. **Table 5's own sentence then reads correctly for the first time:** the four struts sit
   *"at a 45° increment from the wing surface pressure tap locations"*. With the taps fixed at
   the cardinal directions by their own names, that sentence **is** the 45/135/225/315 answer.
   Table 5's other phrase — the defined strut attaching *"along the upper surface (i.e., the
   surface with the fairwater)"* — is now read as naming the **half-space** its equations are
   written in, not an azimuth, because the figure is direct evidence about azimuth and the
   sentence is not.

### A3.1 A CONSEQUENCE THAT MATTERS FOR THE MESH, AND IT IS FAVOURABLE

**The half model of §4.1 REMAINS EXACT with the ring wing and struts fitted.** Struts at
45/135/225/315 are mirror-symmetric about `z = 0` — 45° ↔ 315° and 135° ↔ 225° — and a ring
wing is a surface of revolution, so the whole `Config 1` body keeps the mirror symmetry the
half model rests on, at every α of the pitch sweep. The half domain will contain the struts at
**45° and 135°**, with 315° and 225° as their mirrors, and the force doubling of §4.1 applies
to them unchanged.

**A second consequence, recorded because it will be asked:** the struts being clear of the
appendage wakes also means the ring wing's inflow is less disturbed than it would otherwise be
— but it does **not** restore the §A1.3 argument. The ring wing still sits downstream of the
sail and of four appendages, so its increment on the appended body is still not plane-independent
and is still not estimable from Roddy's horizontal-plane data. **It is measured by the pair, as
§A2.1 rules, and it is not estimated.**

### A3.2 STATUS OF THE RING-WING DEFINITION AFTER THIS ADDENDUM

Every constant needed to emit ring wing 1 and its four struts is now read from a page image and
checked: the wing's LE/TE points, camber, camber slope, both thickness branches, the surface and
placement transforms (§A2.3), the strut generator and its two intersections (§A2.4), and now the
strut azimuths. **The block on emission is lifted.** What is still **not** done, and is reported
as not done: no generator code exists, no ring-wing or strut STL exists, no `Config 1` mesh
exists, and no solve of anything exists.

---
---

# ADDENDUM 4 — 2026-09-12 — **THE RUNG ID `A1f` NOW NAMES TWO DIFFERENT ACTS IN THIS TEAM**

**Appended at the foot. Lines whose number changed above this section: 0.**
**AMENDMENT CONDITION (rule 2), CHECKED:** `SOLVE_A*` absent, no queue entry, no solver run.

**Reported, not resolved: renaming or renumbering an act is the cfd-supervisor's call and is
not taken by this lane.**

Two pre-registrations committed to this repository within about ninety minutes of each other,
by two lanes of the same team, on the same case, both carrying the rung id **`A1f`**:

| file | act | plane |
|---|---|---|
| `verification/campaign/SUBOFF_A1f_APPENDED_VERTICAL_PLANE_PREREGISTRATION.md` | this one — the α-sweep on the hull + sail + four stern appendages, later ruled to become Roddy `Configuration 1` | **vertical** |
| `verification/campaign/SUBOFF_A1f_MATCHED_RE_DRIFT_SWEEP_PREREGISTRATION.md` (commit `e7db97605`) | a peer lane's matched-Reynolds drift sweep | **horizontal** |

> **THIS IS THE FAILURE MODE §2 OF THIS DOCUMENT EXISTS TO STOP, OCCURRING INSIDE OUR OWN LAB,
> IN OUR OWN TEAM, ON THE SAME CASE, ON THE SAME NIGHT.** §2 was written about Roddy's
> `Configuration 1` and Liu & Huang's `Config. 1` naming the fullest and the emptiest body in
> the DARPA programme. The lesson is not about 1989: **a bare index collides because indices
> are assigned locally and read globally, and two careful people working in good faith will
> assign the same one.**

**WHAT SAVED IT IS EXACTLY WHAT §2 PRESCRIBES, AND THAT IS THE USABLE FINDING.** Neither
document can be confused for the other, because **each filename carries what the act IS** —
`APPENDED_VERTICAL_PLANE` against `MATCHED_RE_DRIFT_SWEEP` — and not merely which index it was
given. A reader citing "SUBOFF A1f" alone gets the wrong act half the time; a reader citing
either filename cannot. **The naming rule therefore extends from the source's configurations to
the lab's own act identifiers:**

> **An act is cited by a name that carries what it is — its body, its plane and its condition —
> never by a bare rung id alone. The rung id is an ordering device, not an identifier.**

**One corroboration taken from that peer commit and recorded because it supports §A2.2
independently:** its message states that *"EVERY STATIC DERIVATIVE FOR ALL SIX CONFIGURATIONS
WAS MEASURED AT ONE SPEED, 6.5 knots"*. That is the same 6.5 knots this document registers in
§A2.2 from Roddy report page 3, reached by a different lane through a different question, and
it strengthens the matched-condition registration here.
