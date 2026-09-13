# PPTC VP1304 open-water act — PRE-REGISTRATION

**Status: FROZEN at the commit that introduces this file.** Gates, thresholds, caps and
labels below are closed to change from that commit onward. After first compute, changes
land only as dated addenda that cannot alter a gate, threshold, cap or label; originals
are struck, never rewritten (CLAUDE.md rule 2, `VERIFICATION_CHARTER.md` §2b/§2d).

- Team: cfd. Lane: the 16-rank propeller reserve of Sanaa's 2026-09-12 ~21:40Z core table.
- Governing instruction: `docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md`
  section B, byte-exact, sections 1–10, written by Sanaa. Nothing below is chosen by an
  agent at run time except where this document says "lab choice" and gives its reason.
- General run rules: `docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md` (checkpoints,
  launch, monitoring, stop rules, hygiene), unchanged.
- Written before any solve. No solver has been launched for this act at the time of this
  commit; the run directory `verification/runs/PPTC_VP1304/` does not exist.

---

## 1. Sources — retrieved, title-page verified, hashed

Every artifact below was opened at its title page and the title page read (CLAUDE.md
rule 15: never by file type, filename or hash). Retrieval into the box only; nothing
leaves the box (rule 8); submissions are parked (rule 7) — nobody was contacted, nothing
registered, posted or filed anywhere outside this repository.

### 1.1 The comparator and the primary reference

| file | bytes | sha256 |
|---|---|---|
| `docs/papers/propeller_rotating_machinery/barkmann_2011_sva_report_3752_pptc_open_water_tests.pdf` | 1281875 | `f9b32f2b68f8d038709de75392130b07840d8394b6b365d151fce32148c2d988` |

Title page, quoted: "Potsdam Propeller Test Case (PPTC) / Open Water Tests with the Model
Propeller VP1304 / Report 3752 / Potsdam, April 2011 / Schiffbau-Versuchsanstalt Potsdam
GmbH". Page 1.1 carries "Author  Dipl.-Ing. U. H. Barkmann" and "Potsdam, 15/04/2011".
Sanaa's required verification string — "Report 3752, Potsdam, April 2011, author
Dipl.-Ing. U. H. Barkmann" — is satisfied in full.
Source URL: `https://www.sva-potsdam.de/wp-content/uploads/2016/04/SVA_report_3752.pdf`.

### 1.2 The remaining documents

| file | bytes | sha256 | title-page identity |
|---|---|---|---|
| `mach_2011_sva_report_3754_pptc_ldv_velocity_measurements.pdf` | 12018877 | `71da14db7198e065fe32f62f8d43b2671ce0716a420640fd1b9e57f9d6e69f23` | "PPTC / LDV Velocity Measurements with the Model Propeller VP1304 / Report 3754 / Potsdam, April 2011"; page 1.1 "Author Dipl.-Ing. K.-P. Mach" |
| `barkmann_2011_smp11_pptc_test_case_description.pdf` | 507412 | `5b66771f60ad3999d481336e3f5a498fd5700134a8cdbbb2d6e5c16596160dcf` | "Second International Symposium on Marine Propulsors smp'11, Hamburg, Germany, June 2011 / Workshop: Propeller performance / Potsdam Propeller Test Case (PPTC) Test Case Description / Ulf Barkmann, Hans-Jürgen Heinke, Lars Lübke" |
| `barkmann_2011_smp11_case21_open_water_presentation.pdf` | 1041953 | `15f764619059e410a754e17ca894849990aae3bf918898059ee3b949883e6dc0` | "Potsdam Propeller Test Case (PPTC) / Open Water Tests / Case 2.1 / Ulf Barkmann / Potsdam Model Basin (SVA)" |
| `sva_2011_smp11_case21_open_water_evaluation.pdf` | 2420091 | `569ce93307742c9ed9333946d8d5ce502b69a12b4428826012089e484650ea90` | "Second International Symposium on Marine Propulsors 2011 / Workshop: Propeller Performance / PPTC / Open Water Test with the Model Propeller VP1304 / Case 2.1 / Potsdam, May 2011" — **this is the band's source** |
| `sva_2011_smp11_case2_pptc_geometry_table.pdf` | 150759 | `1c0bed50d1d7a7f99625a5367223860814b3a77ad6b9d8b4f609ce8aeb4b73d3` | "Case 2: Geometry PPTC" |
| `sva_2011_smp11_pptc_propeller_geometry_annotation.pdf` | 288309 | `9def9e96c5412a2f0142cbf202c1dd7ef493ddc8e63e3db9de84bd8df1643392` | "Propeller geometry: PPTC (VP1304)" |
| `sva_2011_smp11_case21_open_water_test_setup.pdf` | 122334 | `5e292c221a63839c8735f740672bf5d753aac99892a42bc046c8a512576393ff` | "Case 2.1: Open water tests PPTC" |
| `sva_2011_smp11_open_water_correction_explanation.pdf` | 559009 | `c697d5efd6cbc8fe5a83d2bee56ed5ff85be065bdee96b3eb5e3ae8087a6bac6` | "Pre-tests I, V = 0 m/s"; the idle-torque / gap-force correction algebra |
| `sikirica_2019_jmse_7_374_grid_type_turbulence_model_propeller.pdf` | 57547735 | `8c21b06a0cc91e0a0212d3031218ef328e6510e082516d982f9f2f67232554af` | "Journal of Marine Science and Engineering / Article / Grid Type and Turbulence Model Influence on Propeller Characteristics Prediction / Ante Sikirica, Zoran Čarija, Lado Kranjčević, Ivana Lučin / Published 20 October 2019" |
| `lungu_2020_jmse_8_297_des_sst_pptc_propeller.pdf` | 3446968 | `21f70ba00acbfa6bbd24dd03f81edbdf98374c9edb7582ad50bd0a22c238f3f2` | "Article / A DES-SST Based Assessment of Hydrodynamic Performances of the Wetted and Cavitating PPTC Propeller / Adrian Lungu / Published 23 April 2020" |

Each PDF has a matching `.txt` sidecar in the same directory (`FILING_CHARTER`).
Report 3753 (cavitation, Heinke) is explicitly a later rung and is NOT retrieved for this act.

### 1.3 The CAD — provenance, and one disclosed reading of Sanaa's wording

Sanaa: "Geometry (CAD): SVA Potsdam PPTC page, section 'CAD Geometry of PPTC Propeller'
… Do not use any third-party STL of this propeller."

**What is actually on that page.** The string "CAD Geometry of PPTC Propeller." on
`https://www.sva-potsdam.de/en/potsdam-propeller-test-case-pptc/` is the caption of a
photograph (`PPTC_Bild1_PPTC_VP1304_final.jpg`), not a download section. The page's body
links five data sets; the geometry lives under the first, "smp11 Propeller Workshop"
(`https://www.sva-potsdam.de/en/pptc-smp11-workshop/`), on the same first-party SVA host.
This is recorded because it is a departure from the literal wording of the instruction,
not from its intent: the file is SVA's own, served by SVA, and no third-party STL is used.

| file | bytes | sha256 |
|---|---|---|
| `cases/PPTC_VP1304/sources/case2-1_open_water_test_geometry.zip` | 10219299 | `0dace7c63e3f292522c6f219681fa884182093bfaa6b9cdbb54ca7df9158e122` |
| `cases/PPTC_VP1304/sources/case2-1_PPTC_hubcap2D.dat_.zip` | 408 | `e8774c8070866942ffc661c08ae5977c3db482491ca44e1cc5e9fc11aae747ad` |

Archive members (extracted to `cases/PPTC_VP1304/sources/cad/`):

| member | bytes | sha256 |
|---|---|---|
| `closed hub fillets/case2-1_PPTC_geo_no_gap.stp` | 1029355 | `d08aaf690b22e5f418f8a20473d502046f815ce8b3fc67378fd36f6d55543d2d` |
| `closed hub fillets/case2-1_PPTC_geo_no_gap.igs` | 2210571 | `06c25a7b0edea46c73243bbb61992c3af041c7f1ef7fd2f89e4cbb3c3c028fba` |
| `closed hub fillets/case2-1_PPTC_geo_no_gap.3dm` | 7574902 | `2941455f17a5d0ecec02b7361ae6c9d6c10e55ee6190324052b2634a480cb7b4` |
| `detailed model/case2-1_PPTC_geo.stp` | 1686182 | `0eba616b84ace44f1dbde3eea36d661618250067d91aac737c6897097d945a1f` |
| `detailed model/case2-1_PPTC_geo.igs` | 4552767 | `e79ec122207121bb192309bfb84807b957a0f5d1e2c53418032e986f8f020ddc` |
| `detailed model/case2-1_PPTC_geo.3dm` | 1772358 | `082f3dcdec2709b73980201923a55f38d6d0c20bc20f3276b5c1fe37bb4f2db1` |

**The file that enters the mesh is `closed hub fillets/case2-1_PPTC_geo_no_gap.stp`**,
sha256 `d08aaf690b22e5f418f8a20473d502046f815ce8b3fc67378fd36f6d55543d2d`. See §2.2.

---

## 2. The propeller — registered geometry

### 2.1 Values, and what corroborates each

From Report 3752 Table 1 (read from the PDF, not recalled), corroborated where stated:

| quantity | registered value | corroboration |
|---|---|---|
| Diameter D | 0.250 m | Table 1; page 2.11 table header `D [m] 0.25000`; page 2.13 header; CAD bounding box (§2.3) |
| Pitch ratio P0.7/D | 1.635 | Table 1; page 2.11 header `P0.7/D 1.63500`; workshop sheet `P0.7/D 1.6350` |
| Expanded area ratio AE/A0 | 0.77896 | Table 1; workshop sheet gives 0.7790 (same number, fewer digits) |
| Chord at r/R = 0.7, c0.7 | 0.10417 m | Table 1; page 2.11 header `c0.7 [m] 0.10417`; workshop sheet `C0.70 104.1670 mm` |
| Skew | 18.837 deg | Table 1, symbol θ_EXT. The workshop sheet gives 18.8000 deg under symbol θ_eff — a **different definition**, not a conflicting measurement. Registered value is Report 3752's. |
| Hub diameter dh | **0.075 m**, dh/D = 0.300 | Table 1 `dh/D 0.300`; page 2.11 and 2.13 headers `dh/D 0.30000`; and decisively Report 3752's three dummy-hub test pages, each of which states **`dh [m] 0.075`** as an absolute dimension, not a ratio |
| Number of blades Z | 5 | Table 1; workshop sheet |
| Sense of rotation | right-handed (pressure side) | Table 1; page 2.11 header; workshop sheet "right-handed (SCS)" |
| Type | controllable-pitch propeller, 0.3 mm hub/root gap near LE and TE | Report 3752 §2; workshop sheet |

**The dh/D question is RESOLVED, and it resolves to agreement.** The smp'11 case-2
geometry sheet prints "Hub diameter ratio  dh/D  [-]  0.1500", exactly half Report 3752's
0.300. Two independent measurements settle it as a convention, not a disagreement:

1. Report 3752 gives the hub as an absolute length, `dh [m] 0.075`, three times. A ratio
   of 0.1500 taken as a **radius**-to-diameter ratio against D = 0.250 m gives
   r_hub = 0.0375 m, i.e. dh = 0.075 m — the identical physical hub.
2. The SVA hub-and-cap profile file `case2-1_PPTC_hubcap2D.dat` gives the nose cap running
   from radius 36.230 mm at x = 0 to radius 0 at x = 108.690 mm. The setup sheet states
   "The nose cap length corresponds to 1.5 times the boss diameter at the forward end";
   108.690 / 1.5 = 72.460 mm = 2 × 36.230 mm exactly. The boss is therefore ~72.5 mm in
   **diameter**, which is consistent with dh = 75 mm and inconsistent with dh = 37.5 mm
   by a factor of two.

Recorded outcome: **three documents agree on one physical hub, dh = 0.075 m.** The
workshop sheet's "diameter ratio" label on a radius ratio is a label error in a secondary
sheet; it is disclosed here and the sheet's number is never used.

### 2.2 Registered modelling choices (Sanaa's section 2) and one measured departure

- **(a) The 0.3 mm root gap is CLOSED — blade fused to hub.** Registered as Sanaa wrote it.
  **Departure in method, not in state:** SVA ships its own gap-closed geometry in the same
  archive ("closed hub fillets", `case2-1_PPTC_geo_no_gap.*`). We consume that file rather
  than fusing the root ourselves. This reaches the identical registered modelling state
  from the first-party source and removes a class of our own geometric error. The departure
  carries its own evidence: §2.4 measures the two variants against each other, and the
  substitution is admitted only on that measurement, never on the assertion.
- **(b) Hub modelled with the nose cap upstream and the dynamometer shaft downstream** as a
  cylinder of diameter 0.075 m extending to the outlet, rotating with the propeller.
  Basis: Report 3752 §5 and photographs pages 4.2–4.3; the pull configuration with
  dynamometer H39 behind the propeller.
- **(c) Shaft inclination 0 deg.**

### 2.3 Units and axis — confirmed at kernel level

The STEP file was read through OpenCASCADE (gmsh 4.12.1, `SetFactory("OpenCASCADE")`).
It parses as **one solid with 35 faces**. Bounding box, in file units:
x ∈ [−356.000, 133.690], y ∈ [−119.753, 124.965], z ∈ [−120.700, 124.666].
Maximum radius from the axis is 124.965, and the propeller's known radius is R = D/2 = 125.
**The file is therefore in millimetres and D = 0.250 m is confirmed** — a 5-bladed
propeller's bounding box touches R only where a tip lies, so 124.965 against 125.000 is the
expected signature of a correct-scale, discretely-bladed body and not a scale error.
Registered import scale: **exactly 1e-3** (mm → m). The shaft axis is x.

### 2.4 CAD equivalence measurement — the departure's evidence

The substitution in §2.2(a) is admitted **only on the measurement below**, never on the
assertion that two files "are the same". Two independent comparisons were made: one exact
and tessellation-free at the CAD-kernel level, one geometric.

#### 2.4.1 Control-point localisation — exact, on the unhealed STEP text

Every `CARTESIAN_POINT` was parsed out of both STEP files and binned by radius from the
shaft axis. This is the decisive comparison because it touches no mesher and no tolerance.

| radius band (mm) | no_gap points | detailed points | note |
|---|---|---|---|
| 0 – 30 | 102 | 102 | **100% identical points** |
| 30 – 35 | 4 | 4 | **100% identical points** |
| **35.0 – 37.5** | **1 800** | **4 287** | **root gap region** |
| **37.5 – 40.0** | **1 861** | **6 242** | **root gap region** |
| 40 – 45 | 526 | 564 | +7% |
| 45 – 50 | 19 | 19 | **100% identical points** |
| 50 – 62.5 | 907 | 927 | +2% |
| 62.5 – 75 | 437 | 447 | +2% |
| 75 – 87.5 | 4 | 4 | **100% identical points** |
| 87.5 – 100 | 870 | 890 | +2% |
| 100 – 112.5 | 435 | 445 | +2% |
| 112.5 – 126 | 2 540 | 2 660 | +5% |
| **total unique** | **9 512** | **16 598** | |

The population difference is **7 086 points, of which 6 868 — 96.9% — lie in the two
radial bands spanning the blade root**, with the hub radius r = 37.5 mm falling exactly
between them. Every other band differs by 5% or less, and four bands are 100%
point-identical. The direction is also right: the gap-closed variant has **fewer** points
at the root, which is what closing a 0.3 mm gap does — it deletes the narrow faces that
needed them.

**Stated limit on this claim.** The two files carry **different NURBS parameterisations**
(only 237 control points are shared across the whole model), so this is **not** a proof of
surface identity. The claim actually made here is the **count-by-band localisation** of the
difference, and nothing stronger.

#### 2.4.2 Geometric invariants — identical tessellation settings on both

Both variants tessellated with the *same* settings (uniform 0.8 mm target, curvature
refinement off, OCC healing on), so any difference is geometry or discretisation, not
settings.

| invariant | no_gap | detailed | difference |
|---|---|---|---|
| triangles | 651 282 | 632 450 | — |
| enclosed volume | 1 174 948.436 mm³ | 1 174 678.190 mm³ | **−270.246 mm³ = 0.023%** |
| surface area | 163 545.982 mm² | 164 492.793 mm² | 946.811 mm² = 0.579% |
| bbox x | −356.0000 … 133.6900 | −356.0000 … 133.6900 | **identical to the digit** |
| bbox y, z extents | 244.6934, 245.3706 | 244.7179, 245.3702 | ≤ 0.025 mm |
| max radius | 124.9905 mm | 124.9902 mm | 0.0003 mm |

**Where the surface-area difference sits, and the test that proves it is geometry.**
At 0.8 mm the radial area difference is **827.154 mm² inside the two root bands (87.4% of
the total) and 119.657 mm² everywhere else** — that residual being **0.073% of the model's
surface area**. Outside the root, no band exceeds 0.21% except the outermost tip shell at
0.71%.

The residual is named for what it is by a **convergence test**, not by assertion. Repeating
the identical comparison at a 3.0 mm tessellation instead of 0.8 mm:

| | 3.0 mm | 0.8 mm | change |
|---|---|---|---|
| area difference **inside** the root bands | 887.506 mm² | 827.154 mm² | −6.8% |
| area difference **outside** the root bands | 2 059.324 mm² | 119.657 mm² | **−94.2% (17.2× smaller)** |

**Refinement collapses the outside-root difference and leaves the root difference standing.
That is the signature of discretisation error outside the root and real geometry at it.**
The outside-root residual is therefore recorded as **tessellation noise of magnitude
0.073% of surface area**, not as a geometric difference.

#### 2.4.3 Independent corroboration of the CAD against Report 3752

The blade section at r/R = 0.7, measured on the gap-closed variant in the unrolled
cylindrical surface and averaged over all five blades, gives
**chord = 104.2788 mm (five-blade sd 0.1927 mm)** against **Report 3752 Table 1's
c0.7 = 104.1670 mm** — agreement to **+0.10%**. Five blades are resolved, as Z = 5 requires.
This checks the admitted geometry against the *report's own table*, not merely against its
own bounding box, and it independently confirms the millimetre unit registered in §2.3.

#### 2.4.4 Verdict

The gap-closed variant differs from the detailed variant **only at the blade root**, by
96.9% of the control-point difference and 87.4% of the surface-area difference, with
enclosed volume agreeing to 0.023% and the bounding box to the digit. **The substitution
of §2.2(a) is admitted.**

### 2.5 Healing invariance — REGISTERED HERE, BEFORE THE CHECK IS RUN

SVA's gap-closed CAD does not tessellate cleanly: gmsh's Frontal-Delaunay algorithm fails
on roughly 10 of its 35 faces and falls back to a far slower one, and the initial-mesh-only
algorithm **segfaults** on one face unless OpenCASCADE healing is enabled. Healing
(`OCCFixDegenerated`, `OCCFixSmallEdges`, `OCCFixSmallFaces`, `OCCSewFaces`, tolerance
1e-4) clears it, and the production STL is therefore generated with healing **on**.

**This is a live risk to the registered modelling state, and it is registered as one.**
Healing removes and sews *small and near-degenerate faces*. The region that distinguishes
the gap-closed variant from the detailed one is the blade root — which is precisely where
the small, nearly-degenerate faces live (§2.4.1 measures 96.9% of the difference there).
We adopted SVA's closed-root file specifically so that the closure would be **theirs and
not ours**; a healing pass that moves the root would quietly make it ours again. The
equivalence of §2.4 is a property of the file **before** healing; the mesh is built from the
file **after**.

**The check, and its thresholds, frozen before the numbers are seen.** The same invariants
are measured on the healed geometry and compared against the **unhealed** gap-closed
geometry, tessellated with identical settings:

| invariant | threshold for "healing-invariant" |
|---|---|
| enclosed volume | \|Δ\| ≤ **0.10%** |
| every bounding-box extent | ≤ **0.10 mm** |
| maximum radius | ≤ **0.05 mm** |
| mean chord at r/R = 0.7 | ≤ **0.5%** |
| summed surface area in the root bands r ∈ [35, 40] mm | ≤ **2.0%** |

**Outcome rule, registered:** if every invariant holds, the registered modelling state
survives its own preparation and the certificate says so in one line. **If any is breached,
the registered geometry is no longer SVA's and modelling choice (a) has become the lab's
own** — that is recorded as such on the certificate, choice (a) is re-registered to say the
root closure is ours, and the act does not claim otherwise. The result lands in
`cases/PPTC_VP1304/GEOMETRY_ADMISSION_RECORD.md`, not in this frozen file.

---

## 3. Test conditions and the gate data

- Fluid: fresh water, tW = 15.6 °C, ν = 1.124e-6 m²/s, ρ = 998.99 kg/m³ (page 2.11 header).
- n = 15.0 s⁻¹ (ω = 94.2478 rad/s); V = J n D = 3.75 J m/s.
  Disclosed: the test's own tachometer rows (page 2.12) read n = 14.97–15.08 s⁻¹, e.g.
  n = 14.974 at the design point. J is the controlled similarity parameter and KT, KQ are
  non-dimensional, so the registered n = 15.0 is used throughout; the ≤0.5% rev-rate
  spread is recorded, not modelled.
- Re (Report 3752 annex) = c0.7 √(V² + (0.7 π n D)²) / ν. At J = 1.2021, tabulated
  Re = 0.870e6.
- **Comparator: Report 3752, test 11F0395, 08.04.2011, page 2.11, table headed
  "Open water test, corrected with idle torque and gap force (represents the
  characteristics of the propeller blades including the hub)".** Our CFD models blades +
  hub + shaft, which is what that table represents.
- **Not the comparator:** page 2.13, "corrected with idle torque and hub resistance"
  (blades only). Recorded as a secondary reference. Measured difference at J = 1.2021:
  KT 0.2797 (2.11) vs 0.2922 (2.13) = **0.0125**, i.e. 4.5% — Sanaa's disclosure of
  "about 0.01" is confirmed and sharpened here.
  **Structural fact, and it matters: 10KQ is IDENTICAL between the two tables** (0.7676 at
  J = 1.2021, and at every J). The hub-resistance correction acts on thrust only. **Our
  torque gate is therefore completely insensitive to which of the two tables a reader
  believes we used.** Only the thrust gate depends on that choice, and it is registered
  here as page 2.11.

### 3.1 The six registered advance ratios (transcribed from page 2.11, verified digit for digit)

| J | KT measured | 10KQ measured | eta_O measured |
|---|---|---|---|
| 0.7985 | 0.5052 | 1.1836 | 0.542 |
| 0.9314 | 0.4297 | 1.0493 | 0.607 |
| 1.0683 | 0.3538 | 0.9096 | 0.661 |
| 1.2021 | 0.2797 | 0.7676 | 0.697 |
| 1.3308 | 0.2082 | 0.6300 | 0.700 |
| 1.4594 | 0.1394 | 0.4944 | 0.655 |

All six rows reproduce Sanaa's section-3 table exactly. Design point for the grid family:
**J = 1.2021**.

Polynomials (page 2.11, valid 0 ≤ J ≤ 1.677), recorded but **not used in any gate**:
KT = 0.955438 − 0.346932 J − 0.629537 J² + 0.586304 J³ − 0.175174 J⁴;
10KQ = 2.076022 − 0.949651 J − 0.719299 J² + 0.873861 J³ − 0.306054 J⁴.
Disclosed: these are fits, not the data. At J = 1.2021 the KT polynomial returns 0.28135
against the tabulated 0.2797, a residual of 0.0017 (0.6%). This is precisely why the
registered gate uses the six **measured** points and no interpolation enters it.

### 3.2 Definitions (Report 3752 annex A2.2)

J = V/(nD); KT = T/(ρ n² D⁴); KQ = Q/(ρ n² D⁵); eta_O = J·KT/(2π·KQ).
T is the axial force in the thrust direction and Q the torque about the shaft axis, both
on blades + hub + cap + shaft.

---

## 4. BANDS — frozen before the first solve

Report 3752 states no measurement uncertainty. Per Sanaa's section 4 the band is the
smp'11 participant scatter at each J, read from the workshop summary and recorded with
its page.

**The scatter CAN be read to a number, so the permitted fallback (±3% KT / ±4% KQ for
J ≤ 1.33, ±6% / ±8% at J = 1.46, "stated as a lab judgement") is NOT USED, and no lab
judgement enters the band's magnitude.**

### 4.1 Source, with pages

`docs/papers/propeller_rotating_machinery/sva_2011_smp11_case21_open_water_evaluation.pdf`,
sha256 `569ce93307742c9ed9333946d8d5ce502b69a12b4428826012089e484650ea90`.
Sections 7.20–7.24, "Comparison of open water characteristics", at
**J = 0.6 (printed page 27), J = 0.8 (page 28), J = 1.0 (page 29), J = 1.2 (page 30),
J = 1.4 (page 31)** — PDF pages 28–32 respectively. Each page tabulates every participant
submission's KT, 10KQ and eta_O.

### 4.2 Population — a lab choice, declared

19 submissions from 14 groups. **Five are potential-flow / panel / vortex-lattice methods
(HSVA-PPB, HSVA-QCM, INSEAN-PFC, SVA-Vortex, UniGenua-Panel) and are EXCLUDED**, leaving
**n = 14 viscous submissions**. Reason: our method is steady RANS with a wall-function
closure, and a band is a statement about the spread of methods of our own class. This is a
lab choice; it is registered here, before any solve, and it is the choice that makes the
band *narrower* (at J = 1.2, all-19 gives ±9.12% on KT against ±7.49% for the viscous
subset), i.e. it is the harder gate, not the convenient one.

### 4.3 Statistic — a lab choice, declared, with the alternatives recorded

Sanaa wrote "the participant scatter". She did not name a statistic. The statistic is
therefore an agent choice that moves the gate by a factor of two or more, and is registered
explicitly:

> **REGISTERED STATISTIC: two standard deviations (2σ) of the n = 14 viscous-participant
> population, expressed as a percentage of that population's mean.**

Reason 2σ is the honest reading rather than the convenient one: "scatter" in a workshop
summary describes the interval that contains essentially the whole participant field, not
the interval that contains two thirds of it. At every J the 2σ interval is narrower than
the observed min-to-max range, so 2σ remains a conservative summary of the actual spread
while 1σ would exclude roughly a third of the participants from their own scatter band.
2σ is also not the widest available choice — min-to-max is wider — so it is not the
maximally permissive reading either.

All three candidate statistics, at all five workshop J, viscous subset, n = 14:

| J | KT 1σ% | **KT 2σ%** | KT min% | KT max% | 10KQ 1σ% | **10KQ 2σ%** | 10KQ min% | 10KQ max% |
|---|---|---|---|---|---|---|---|---|
| 0.6 | 2.20 | **4.39** | −3.78 | +2.85 | 1.61 | **3.22** | −1.65 | +3.00 |
| 0.8 | 1.92 | **3.83** | −3.69 | +2.89 | 2.64 | **5.27** | −5.19 | +6.46 |
| 1.0 | 2.69 | **5.39** | −3.87 | +4.38 | 3.74 | **7.47** | −7.64 | +9.42 |
| 1.2 | 3.75 | **7.49** | −5.01 | +5.78 | 4.05 | **8.10** | −6.86 | +10.48 |
| 1.4 | 6.32 | **12.65** | −8.35 | +10.94 | 4.25 | **8.50** | −8.11 | +8.63 |

(percentages of the viscous-participant mean; means are
KT 0.6184 / 0.5015 / 0.3880 / 0.2779 / 0.1659 and
10KQ 1.4204 / 1.2024 / 0.9906 / 0.7784 / 0.5496 at J = 0.6 / 0.8 / 1.0 / 1.2 / 1.4.)

### 4.4 Mapping to our J — a lab choice, declared

The workshop reports at J = 0.6, 0.8, 1.0, 1.2, 1.4; our six J do not coincide with those.
**Registered rule: the relative 2σ percentage is linearly interpolated in J between the
bracketing workshop values, and HELD CONSTANT (not extrapolated) beyond J = 1.4.**
Our J = 1.4594 lies outside the workshop range; holding the J = 1.4 value rather than
extrapolating an obviously growing scatter gives a *narrower* band there than extrapolation
would, so the clamp makes that gate harder, not easier. Disclosed as a likely
under-estimate of the true scatter at J = 1.4594.

### 4.5 Centring — declared, and only one of the two gates

The participants were graded by the workshop against the workshop's own "Measurement" row,
which is **not** our comparator (see §4.6). A spread computed about the participant mean
and then applied about our page-2.11 value would silently merge two different centrings.
Both are therefore registered with their numbers, and which one gates is named.

> **GATING CENTRING (B): the band is centred on the Report 3752 page 2.11 MEASURED value,
> with half-width equal to the interpolated relative 2σ percentage of §4.3–4.4.**

Reason: the act's claim is agreement between our CFD and the towing-tank measurement, with
the community's own spread supplying the tolerance. A band centred on the participant mean
would instead gate agreement with the participants, which this act does not claim.

**The registered gate band (centring B) — frozen:**

| J | KT meas | 2σ% | **KT low** | **KT high** | 10KQ meas | 2σ% | **10KQ low** | **10KQ high** |
|---|---|---|---|---|---|---|---|---|
| 0.7985 | 0.5052 | 3.84 | **0.4858** | **0.5246** | 1.1836 | 5.26 | **1.1214** | **1.2458** |
| 0.9314 | 0.4297 | 4.85 | **0.4088** | **0.4506** | 1.0493 | 6.72 | **0.9788** | **1.1198** |
| 1.0683 | 0.3538 | 6.11 | **0.3322** | **0.3754** | 0.9096 | 7.69 | **0.8397** | **0.9795** |
| 1.2021 | 0.2797 | 7.55 | **0.2586** | **0.3008** | 0.7676 | 8.10 | **0.7054** | **0.8298** |
| 1.3308 | 0.2082 | 10.86 | **0.1856** | **0.2308** | 0.6300 | 8.36 | **0.5773** | **0.6827** |
| 1.4594 | 0.1394 | 12.65 (clamped) | **0.1218** | **0.1570** | 0.4944 | 8.50 (clamped) | **0.4524** | **0.5364** |

**RECORDED, NOT GATING — centring A**, participant mean ± 2σ, stated only at the five J
where the participants were actually reported (no interpolated mean is quoted, because a
mean interpolated past the end of its own range is not a measurement):

| J | mean KT | KT low | KT high | mean 10KQ | 10KQ low | 10KQ high |
|---|---|---|---|---|---|---|
| 0.6 | 0.6184 | 0.5912 | 0.6456 | 1.4204 | 1.3746 | 1.4662 |
| 0.8 | 0.5015 | 0.4823 | 0.5207 | 1.2024 | 1.1390 | 1.2658 |
| 1.0 | 0.3880 | 0.3671 | 0.4089 | 0.9906 | 0.9166 | 1.0646 |
| 1.2 | 0.2779 | 0.2571 | 0.2987 | 0.7784 | 0.7153 | 0.8415 |
| 1.4 | 0.1659 | 0.1449 | 0.1869 | 0.5496 | 0.5029 | 0.5963 |

A result may land inside one centring and outside the other. **Centring B gates. Centring A
is reported alongside, always, and never substituted after the fact.**

### 4.6 What the workshop's own reference actually was — established by arithmetic

The workshop's "Measurement" row at J = 1.2 reads KT = 0.295, 10KQ = 0.776. Evaluating
Report 3752's **page 2.13 (blades-only)** polynomial at J = 1.2 gives KT = 0.294921 and
10KQ = 0.776009 — a six-digit match. The page 2.11 polynomial gives KT = 0.282479 at the
same J and does not match. **The smp'11 workshop graded its participants against the
blades-only table, not against our comparator.** This is the reason §4.5 transfers the
scatter only as a relative width and never as an absolute deviation, and the reason
centring is registered rather than assumed.

### 4.7 Honest statement of what this band costs us

**At the headline design point the band we are required to read is two and a half times
WIDER than the fallback we were permitted to use** (±7.55% vs ±3% on KT at J = 1.2021;
±8.10% vs ±4% on 10KQ). Read/fallback ratios at the six J: KT 1.28, 1.62, 2.04, 2.52,
1.81, 2.11; 10KQ 1.31, 1.68, 1.92, 2.03, 1.04, 1.06. We are not banking the easier gate
quietly: the registered band is the one Sanaa's instruction specifies, the fallback numbers
are recorded above as a declared-secondary tighter reading, and **the certificate will
report our result against BOTH** so a reader can see what a ±3%/±4% tolerance would have
said. The ordering is the protection — this is frozen before a single solve, so neither
band can have been fitted to our answer.

### 4.8 The gate

- **PASS at a J point** when both KT and 10KQ lie inside their §4.5 centring-B bands.
- **GATE FAIL** when either lies outside.
- **The act's headline gate is the design point J = 1.2021 on the FINE level of the family.**
- The sweep is graded on the MEDIUM level, with the family band inherited and disclosed.
- Roache triple gating (CLAUDE.md rule 5) overrides in one direction only: a row whose grid
  triple is not CONVERGING is **NOT A RESULT** whatever its value, and the gate can only
  turn a PASS or GATE FAIL *into* NOT A RESULT, never the reverse. GCI at Fs = 1.25; no GCI
  is quoted when the three values are not monotone.

---

## 5. The registered PREDICTION — it must be able to fail

> **Prediction (Sanaa's section 4, registered verbatim in effect): fully turbulent RANS
> over-predicts KQ slightly at this Reynolds number because laminar regions on the model
> blades are not captured. At J = 1.2: CFD 10KQ ABOVE measured by 1 to 4 percent, and CFD
> KT within 2 percent of measured.**

Against the page 2.11 comparator at J = 1.2021 this predicts
**10KQ ∈ [0.7753, 0.7983]** and **KT ∈ [0.2741, 0.2853]**.

**Evidence that it can fail, gathered before any of our compute.** Across the 14 viscous
smp'11 submissions at J = 1.2, deviation from the workshop reference runs **−6.57% to
+10.82% on 10KQ** and **−10.51% to −0.34% on KT**. Roughly half the field falls outside the
predicted 1–4% window on 10KQ. Their mean lands at +1.4% on 10KQ and −0.6% on KT relative
to our comparator, i.e. inside the prediction — so the prediction is well-posed rather than
a truism, and a lab result outside it is a real and reasonably likely outcome.

**A prediction miss is recorded as a miss. It does not alter any gate, band or label.**

---

## 6. Mesh and domain

### 6.1 Domain

Cylinder coaxial with the shaft: inlet 3D upstream of the propeller plane, outlet 6D
downstream, outer radius 4D. **Single blade passage of 72 deg with cyclic periodic
boundaries** (registered choice). The coarse level is additionally run once as the full
360 deg propeller, and the passage-versus-full difference in KT and KQ is recorded as a
check that **must be under 0.5 percent**.

### 6.2 MRF zone — A REGISTERED PARAMETER WITH A SENSITIVITY, NEVER A DEFAULT

Cylinder about the blades, **diameter 1.3D**, axial extent **0.5D upstream to 0.5D
downstream** of the propeller plane. The interface must not cut the blade tips' wake within
0.5D. Zone diameter and extent are registered parameters. **Sensitivity is mandatory, not
optional: 1.3D versus 1.6D on the coarse level at J = 1.2021, difference in KT recorded.**
Provenance of this rule: this lab's Rushton impeller act, where an MRF zone left near the
swept volume cost more than 12% on the power number — the lesson being that MRF zone size
is a registered parameter with a sensitivity, never a default.

### 6.3 Generator and family

`snappyHexMesh` (OpenFOAM v2606, on disk at `/usr/lib/openfoam/openfoam2606`), from the
admitted STL tessellated to the physics tolerance. **All three levels from ONE script**,
uniform ratio **1.5** in the refinement levels and the surface size.

| level | target cells per 72° passage |
|---|---|
| coarse | ~0.8 M |
| medium | ~2.7 M |
| fine | ~9 M |

Resolution requirements: leading-edge radius resolved by **at least 8 cells across**, tip by
**at least 6 cells across the tip chord**. Refinement box around the blades and a cylinder
along the tip-vortex path 1D downstream. Prism layers on blades, hub, cap and shaft:
**6 layers, growth ratio 1.2**, first-cell height set for **y+ 30 to 60 with wall
functions** (registered wall treatment; wall-resolved y+ ≈ 1 is the next rung and is not
claimed here).

### 6.4 Quality gates, and the divergence from the lab standard, disclosed

Sanaa's section 5 names three: **non-orthogonality below 70 deg, skewness below 4,
cell-volume growth capped at 1.25.**

Checked against `docs/standards/MESH_STANDARD.md` v1.2, as required:

| gate | Sanaa's instruction | `MESH_STANDARD.md` | divergence |
|---|---|---|---|
| max non-orthogonality | < 70 deg | §3.1 hard gate **70 deg**, warning band 65–70 | **none** |
| max skewness | < 4 | §3.2 hard gate **4**, boundary faces included | **none** |
| cell-volume growth | capped at **1.25** | §3.4 is a *different quantity*: a **proposed** gate warning when the adjacent-cell volume **ratio falls below 0.01** | **divergence, disclosed** |
| aspect ratio | not named | §3.3 advisory at 1000, never a lone rejection | recorded, advisory only |

On the volume gate: the standard's §3.4 bounds the ratio from below at 0.01 (a factor of
100 between adjacent cells) and is explicitly *proposed*, not enforced. Sanaa's 1.25 is a
growth **cap** — roughly eighty times stricter, and it is strictly contained within the
standard's proposed gate, so following Sanaa's number cannot violate the standard.
**Registered resolution: Sanaa's 1.25 is enforced.** Instrument: the max adjacent-cell
volume ratio is computed directly from `polyMesh` (owner/neighbour arrays against cell
volumes), because `checkMesh` does not report a growth ratio; the instrument is recorded
with the birth certificate. A breach is disclosed on the certificate with its number and
face count, and caps the fidelity chip rather than being silently relaxed.

### 6.5 Birth certificate — per level, mandatory

Cells; y+ per patch after the design-point solve; max non-orthogonality, max skewness,
max adjacent-cell volume ratio, max aspect ratio, negative-volume count; measured cells
across the leading-edge radius and across the tip chord; the mesh hash. A level without a
birth certificate does not enter the family (`VERIFICATION_CHARTER.md` §9: born clean or it
does not enter).

### 6.6 Published envelope, for context only

smp'11 participants ran 2–20 M cells for the full propeller. Our medium single passage
(~2.7 M × 5 = ~13.5 M full-propeller equivalent) sits inside that envelope.
`sikirica_2019_jmse_7_374` and `lungu_2020_jmse_8_297` are retrieved as the published mesh
practice on this exact propeller. **Context, not a gate.**

---

## 7. Solver and numerics

- `simpleFoam` (steady, incompressible), OpenFOAM **v2606**, with `MRFProperties` for the
  rotating zone. Turbulence: **k-omega SST** with `nutkWallFunction`.
- Convection second-order bounded: `linearUpwind` for U, `limitedLinear 1` for turbulence.
  SIMPLE with the consistent formulation. Relaxation: U 0.7, p 0.3, turbulence 0.7.
  Non-orthogonal correctors 1.
- Boundary conditions: inlet fixed velocity V = 3.75 J m/s along the axis, turbulence
  intensity 1%, mixing length 0.1 D; outlet fixed pressure; outer boundary slip; blades,
  hub, cap and shaft no-slip rotating walls; cyclic patches periodic.
- **Sign convention:** right-handed propeller, axis and rotation per Report 3752 annex A3.
  Verified by the smoke run producing positive thrust at J = 0.8 (KT ≈ 0.5).
  **A negative KT STOPS THE CASE and flips the registered rotation sign, recorded.** It is
  not quietly corrected.
- **Convergence:** residuals below 1e-5 on p and U; KT and KQ stationary within 0.1 percent
  over the last 500 iterations. Solver (linear-system) tolerance strictly tighter than the
  0.1 percent stationarity gate — the T23G2Rn2 rule.
- Iteration cap **4,000 per point** (see §9 on caps).

---

## 8. Bug check, planted-zero control, and smoke

### 8.1 Bug check (Sanaa's section 7 item 1), before any graded solve

`checkMesh` on all three levels; every dictionary read back onto the record; dead-lever
audit (every dictionary entry that the case sets is shown to change the answer or is
removed); the `forces` functionObject shown to be reading the **right patches** — blades,
hub, cap, shaft — with the registered rho, and the rotation axis and centre of rotation
read back.

### 8.2 PLANTED FORCE PERTURBATION — the comparator refuses if it cannot see it

CLAUDE.md rule 3: a zero from a reader not shown able to see a non-zero is not evidence.
Before any force is believed, a known perturbation is written into the force data the
comparator reads, the comparator is run, and **it must report the perturbed value**. If the
reader cannot see the plant, the comparator **refuses (exit 2) rather than degrading to a
warning**. Registered plant magnitude: a multiplicative factor of **1.0500** applied to the
axial force column, expected to move KT by exactly +5.00% ± 0.01%. The refusal path is
exercised and its exit code recorded before the first graded number is read.

### 8.3 Smoke (Sanaa's section 7 item 2) — predictions registered here

Coarse level, **J = 0.7985, 300 iterations**. Registered predictions:

1. **KT sign POSITIVE.**
2. **KT between 0.4 and 0.6 at iteration 300.**
3. Cost per iteration within the §9 band.

**A NEGATIVE KT STOPS THE CASE** and flips the registered rotation sign, recorded as a
finding, not as a quiet fix.

---

## 9. Compute — estimate, cap, and cost basis

**Unit: core-minutes (wall seconds × ranks ÷ 60).** Lane: the 16-rank propeller reserve,
never lent.

Estimate basis, declared as an **estimate and not a measurement**: **3.0e-6 core-seconds
per cell per iteration** for `simpleFoam` + k-omega SST with one non-orthogonal corrector.
This is an engineering figure, not a lab-measured rate for this case; the lab's nearest
measured basis (`docs/COST_CALIBRATION.md` row C-4, 1.904 core-s/iter on DPW8 arm B) is not
transferable because its cell count and rank count differ. Per the C-4 calibration lesson,
the load average is recorded beside the basis at the moment of each launch. **The smoke run
measures the true rate**, and the measured rate is recorded by dated addendum — which
changes no gate, threshold, cap or label.

| item | cells | ranks | iterations | core-min (est.) |
|---|---|---|---|---|
| smoke, coarse, J = 0.7985 | 0.8 M | 4 | 300 | 12 |
| design point, coarse | 0.8 M | 4 | 4000 | 160 |
| design point, medium | 2.7 M | 4 | 4000 | 540 |
| design point, fine | 9 M | 8 | 4000 | 1800 |
| full-360 check, coarse | 4.0 M | 8 | 4000 | 800 |
| MRF sensitivity, coarse 1.6D | 0.8 M | 4 | 4000 | 160 |
| sweep, 5 points on medium | 2.7 M | 4 each | 4000 each | 2700 |
| meshing (4 meshes + tessellation + feature extraction) | — | 4–8 | — | 308 |
| checkMesh, decompose/reconstruct, post-processing, ParaView renders | — | — | — | 150 |
| **TOTAL ESTIMATE** | | | | **6,630 core-min ≈ 110.5 core-hours** |

**Cost: 110.5 core-h × $0.0513/core-h = $5.67.**
**`cost_basis`: the rate $0.0513/core-h (c7a.4xlarge) is REPORTED BY THE OWNER, NOT
MEASURED. The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so the
dollar figure is DERIVED, never measured.** Core-minutes are measured from logs.

**Registered cap: 3× the estimate = 19,890 core-min.** Per Sanaa's standing NO CAP ruling
(directive #17, 2026-09-12) **no run is stopped by a time or budget cap and no wrapper kills
one**; the cap is registered so that a run which crosses it **grades NOT A RESULT**, and the
cap is **never raised** (her item 7: "cap → NOT A RESULT, never raised").
A **MemAvailable guard is a physics guard and is permitted.**

Estimate-versus-actual calibration is mandatory at every process completion (CLAUDE.md rule
12), landing as a row in `docs/COST_CALIBRATION.md` with the ratio actual/predicted, waste
named separately and never absorbed into the ratio.

### 9.1 Declared memory footprints (gate B: footprint vs MemAvailable − 4 GB)

At 2.0 GB per million cells for the solver and 4.0 GB per million for `snappyHexMesh`:
coarse 1.6 GB, medium 5.4 GB, fine 18 GB, full-360 8 GB; fine meshing 36 GB.
The design-point wave (4 + 4 + 8 = 16 ranks) declares **25 GB** concurrent.

### 9.2 Checkpointing (gate A: writeInterval ≤ 1800 s ÷ iteration_rate_s; purgeWrite ≥ 2)

**`writeInterval` 200 iterations, `purgeWrite` 2, on every run.** At the estimated rates the
30-minute bound permits 3000 (coarse, 4 ranks), 889 (medium, 4 ranks) and 533 (fine, 8
ranks) iterations, so 200 satisfies the gate everywhere with at least 2.7× margin, and it is
also the rule for an unknown rate (Sanaa's checkpoint item: every 200 iterations until the
rate is known). Revised only downward, never upward, if the measured rate is slower.

---

## 10. Run plan, in Sanaa's order

1. Bug check on all three levels; planted force perturbation detected (§8.1–8.2).
2. Smoke: coarse, J = 0.7985, 300 iterations (§8.3).
3. **Design point family: J = 1.2021 on coarse (4 ranks), medium (4), fine (8)** — one wave
   filling the 16-rank reserve exactly. Observed order and GCI on KT and KQ; iterative error
   at least 10× smaller than the level differences; band attached. **This is the
   certificate's headline.**
4. Full-360 check on coarse at J = 1.2021 (≈5× the passage cells, 8 ranks, once). Must agree
   with the passage to **under 0.5%** in KT and KQ.
5. MRF zone sensitivity on coarse at J = 1.2021: 1.6D versus 1.3D, difference in KT recorded.
6. Sweep on medium: the remaining five J points, 4 ranks each, **in waves of four**; band
   inherited from the family and disclosed.
7. Checkpoints every 30 minutes, last two kept; **as `ubuntu`, never root**; detached under
   the runner, parented to init; memory guard; core gate against nproc = 96.
8. **Every launch goes through the queue runner. Nothing launched by hand counts as a case**
   (Sanaa's run-rules item 19). **One registered change per run**; never the same action
   twice on the same state; two stops on the same cause → climb the ladder
   (mesh → numerics → model).

### 10.1 Stop rules

General rules per `SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md` items 11–13. The
specific one for this act: **KT oscillating with a fixed period at J = 0.8** (heavy loading,
possible unsteady root separation) → **mark, time-average, disclose** — the physics voting
unsteady, not a failure to be relaxed away.

### 10.2 ParaView at every completion (Sanaa's ~20:30Z addendum)

At **every** run completion, saved beside that run, never batched: the **COARSE level mesh**
visualisation (medium if coarse did not converge), with the result **FIELDS from the finest
completed level available at that time**, updated when a finer level lands.

---

## 11. Deliverables

Open-water curve (KT, 10KQ, eta_O vs J, measured with band, CFD with band, on the report's
page 3.3 axes); family figure at J = 1.2021 with observed order and GCI; blade Cp at
r/R = 0.7 and 0.9 (physics, **not a gate** — no measured Cp exists); blade surface pressure
at J = 0.8, 1.2, 1.46; Q-criterion tip vortex at J = 1.2021; wake planes against Report 3754
LDV (plane positions and radii read from that report and **registered before extraction**);
convergence histories with the stationarity window; mesh figures with the level captioned
and the y+ map; compute table (ranks, core-min, total, wall); certificate.

---

## 12. What this act does NOT claim

Cavitation inception or extent (Report 3753, next rung); unsteady blade-passage effects
(sliding mesh / AMI, next rung); laminar–turbulent transition on the model blades (the
measured Reynolds effect is disclosed, not modelled); behind-hull operation; free surface;
shaft inclination other than 0 deg; the closed root gap as a physical feature of the real
propeller. Each is repeated on the certificate under "what was not checked".

---

## 13. Freeze

Hashes of the CAD, every mesh level, the settings and the comparator are recorded on the
certificate. The grading path is fixed at this commit; the frozen comparator file is
verified to be the file that ran by hashing it against the committed blob
(`scripts/check_comparator_freeze.py`). **Amendments after first compute are dated addenda
that cannot alter a gate, threshold, cap or label.**

---

## AMENDMENT 1 — 2026-09-12, before first compute. THE SHAFT DIAMETER IS 0.040 m, MEASURED, AND 0.075 m IS EXCLUDED BY THE REPORT'S OWN PHOTOGRAPHS

*lines whose number changed above this section: 0*

**Version 1.1.** This amendment **alters no gate, threshold, cap or label.** It corrects one
registered modelling dimension, §2.2(b). The bands of §4, the gate of §4.8, the prediction of
§5, the cost and cap of §9 and every verdict label are untouched.

**Legality.** CLAUDE.md rule 2: before first compute, amendments are legal and must state the
condition and how it was checked. **The condition is that no compute has occurred for this
act, and it was checked by the absence of the run directory
`verification/runs/PPTC_VP1304/`, which does not exist on disk at the time of this
amendment.** No solver has been launched, no queue entry has been placed, and no mesh has
been built.

**Authority for making it.** Sanaa, 2026-09-12 ~22:55Z, byte-exact: *"pptc shaft diameter:
find out."* She ruled on who answers the question, not on the answer. This is that answer,
with its evidence.

### A1.1 What §2.2(b) says, and what is wrong with it

Registered: *"the dynamometer shaft downstream as a cylinder of diameter 0.075 m extending
to the outlet"*, on the stated basis of *"Report 3752 section 5 and photographs page 4.2 to
4.3"*.

**That basis carries no shaft dimension.** Report 3752 §5 gives the arrangement — dynamometer
H39 from Kempf & Remmers arranged behind the propeller model, shaft inclination 0° — and
names the photographs, but states no shaft diameter anywhere. Neither does the smp'11 setup
sheet, the case description, the open-water presentation, the evaluation, Report 3754, or
either participant paper (Sikirica *et al.* 2019 and Lungu 2020 both model a shaft and
neither dimensions it). **The search is recorded so that the absence is established rather
than assumed.** 0.075 m is exactly dh, the hub diameter, which is the most probable origin
of the figure.

### A1.2 The measurement that settles it

**(i) The CAD — first-party, numeric, and the only document that states the dimension.**
The admitted geometry (`case2-1_PPTC_geo_no_gap.stp`, sha256
`d08aaf690b22e5f418f8a20473d502046f815ce8b3fc67378fd36f6d55543d2d`, from the SVA Potsdam
PPTC page and no third party) contains a shaft cylinder at **r = 20.000 mm exactly —
diameter 0.040 m** — running from x ≈ −200 mm to the CAD's aft termination at x = −356.0 mm,
behind a **tapering aft fairing** that carries the body from the hub (r ≈ 33 mm) down to it.
Measured in `GEOMETRY_ADMISSION_RECORD.md` §3.

**(ii) Report 3752 page 3.2, the drawing "VP1304 in open water configuration".** Shows the
nose cap, the hub with five blades, a tapering aft fairing and a slender shaft — the CAD's
configuration exactly, and not a bare cylinder of hub diameter.

**(iii) Report 3752 page 4.2, the photographs, measured in pixels against a known length.**
The hub diameter is known (0.075 m), so the photograph carries its own scale. Segmenting the
body from the blue cloth and the shadow and taking the largest contiguous vertical run per
image column:

| photograph | hub, px | shaft, px | shaft / hub |
|---|---|---|---|
| "Dummy hub configuration" (upper) | 107 | 31 | **0.29** |
| "VP1304 with caps" (lower) | 124 | 27 | **0.22** |

The CAD predicts 40 / 75 = **0.53**; the registered 0.075 m predicts **1.00**, i.e. a shaft
as thick as the hub. The photographs measure 0.22–0.29. **Both readings are biased LOW by
perspective — the shaft recedes from the camera, and the measured section narrows by 16%
along its own visible length, which fixes the direction of that bias — so they cannot
discriminate 0.040 m from something thinner. They exclude 0.075 m decisively: the registered
value is out by a factor of about 3.5 on a quantity the photograph resolves to a few
percent.**

### A1.3 The correction

> **§2.2(b) is amended, with the original struck and not rewritten:**
>
> ~~"the dynamometer shaft downstream as a cylinder of diameter 0.075 m extending to the
> outlet"~~
>
> **The hub is modelled with its cap upstream and, downstream, the CAD's own aft fairing
> followed by the dynamometer shaft as a cylinder of diameter 0.040 m extended to the
> outlet, rotating with the propeller. Shaft inclination 0°.**

The fairing is retained because the CAD has it and because the smp'11 setup sheet states
that "the downstream end of the propeller hub is designed to avoid a pressure build-up" — a
description the fairing matches and a bare cylinder contradicts. The extension runs from the
CAD's termination at x = −356 mm to the outlet at x = −1500 mm at constant 0.040 m diameter.

### A1.4 Why this mattered enough to block the mesh — the sizing, registered before it was run

The method was fixed in `cases/PPTC_VP1304/shaft_sizing_estimate.py` before the arithmetic
was run: ITTC-1957 friction line on the shaft's own Reynolds number, wall stress resolved
into tangential and axial components, torque ∝ r³ and drag ∝ r, identical wetted length for
both candidates so only the radius differs. **It is an ESTIMATE, order of magnitude, not a
measurement**, and it decides nothing — it only sizes the question.

| | 0.040 m (CAD) | 0.075 m (as registered) | difference |
|---|---|---|---|
| shaft torque | 0.0546 N m | 0.4099 N m | **7.5×** |
| contribution to 10KQ | +0.32% of measured | +2.43% | **+2.11%** = **26% of the gate half-width** |
| contribution to KT | −2.66% of measured | −5.68% | **−3.02%** = **40% of the gate half-width** |

**The two candidates are not interchangeable.** Against a KT band half-width of 7.55% and a
10KQ half-width of 8.10%, choosing the wrong shaft moves the answer by a quarter to two
fifths of the band — and the KT figure is a **lower** bound, because the base-pressure change
behind the hub and the deleted fairing are form effects a friction line cannot reach and they
act in the direction of making a bare cylinder differ more. Building the family on the
unsourced dimension would have put a systematic error of this size under a gate, invisibly.

### A1.5 Status

**Resolved and closed.** `GEOMETRY_ADMISSION_RECORD.md` §4, which recorded this as BLOCKED
and escalated, is superseded by this amendment. The certificate records the amended choice,
this evidence, and the fact that the originally registered 0.075 m had no source in the
document it cited.

---

## AMENDMENT 2 — 2026-09-12, before first compute. THE COMPARATOR'S TORQUE IS BLADE TORQUE ONLY, AND THE INTEGRATION PATCH LISTS ARE REGISTERED HERE

*lines whose number changed above this section: 0*

**Version 1.2.** This amendment **alters no gate, threshold, cap or label.** Every measured
value in §3.1, every band in §4.5, the gate of §4.8, the prediction of §5 and the cost and cap
of §9 are untouched. What it fixes is **which surfaces our CFD integrates** to produce the
numbers those bands are applied to — a methodology definition, not a gate.

**Legality.** Before first compute, per CLAUDE.md rule 2. **Condition checked:
`verification/runs/PPTC_VP1304/` does not exist on disk**; no solver has been launched, no
queue entry placed, no mesh built.

### A2.1 What §3.2 got wrong

§3.2 registered: *"T is the axial force in the thrust direction and Q the torque about the
shaft axis, both on blades + hub + cap + shaft."* The thrust half is right. **The torque half
is wrong, and the report says so in three independent places.**

**(i) Report 3752 annex A2.1, verbatim:**

> "The measured torque will be corrected for the effect frictional values of torque, taken
> with the shaft rotating at the same speed with an **axis symmetric mass mounted at the
> position of the rotor**."

An axisymmetric mass in place of the rotor is a bladeless body. Running it at the same speed
and subtracting measures and removes **every rotating friction torque that is not the
blades** — shaft, bearings, seals and the hub-shaped body alike.

**(ii) SVA's own correction algebra**, published as
`sva_2011_smp11_open_water_correction_explanation.pdf` (sheets 4 and 5):

| configuration | thrust | torque |
|---|---|---|
| "Open water test (blades and hub)" — **our comparator, page 2.11** | T − T_gap − T_bearing | **Q − Q_gap − Q_hub − Q_bearing** |
| "Open water test (blades only)" — page 2.13 | T − T_gap − T_bearing − T_hub | **Q − Q_gap − Q_bearing − Q_hub** |

**The two torque expressions are identical.** `Q_hub` is subtracted in both — and Report 3752
§6 says `Q_hub` came from tests 11F0392/11F0393, "the resistance and torque of the hub without
blades", i.e. the whole bladeless rotating assembly.

**(iii) The empirical check that closes it.** 10KQ is **identical digit-for-digit between
pages 2.11 and 2.13 at every one of the fourteen tabulated J** (0.7676 at J = 1.2021, and so
on). Two tables with different torque content could not do that. §3's observation that the
hub-resistance correction "acts on thrust only" is confirmed, and now has its algebraic
reason rather than only its empirical one.

> **CONCLUSION: the measured 10KQ we gate against is BLADE TORQUE ONLY. The measured KT we
> gate against is blades + the hub assembly.**

### A2.2 The correction — integration patch lists, registered

> **THRUST integration (KT): `blades` + `hub` + `cap` + `shaft`.**
> Matches the comparator, whose thrust retains the hub assembly's resistance (page 2.11,
> "corrected with idle torque and gap force"). Unchanged from §3.2.
>
> **TORQUE integration (KQ): `blades` ONLY.**
> Matches the comparator, whose torque has every non-blade rotating friction subtracted.
> **This is the change.**
>
> **`shaftExtension` is EXCLUDED from BOTH graded integrations.**
> The extension from the CAD's termination at x = −356 mm to the outlet at x = −1500 mm is an
> artefact of our domain, not part of the physical model the dynamometer measured. It is
> present as a rotating no-slip **flow boundary** and contributes to neither graded number.

Five patches are therefore tagged, not four: `blades`, `hub`, `cap`, `shaft` (the CAD's own
fairing and shaft, x ≥ −356 mm) and `shaftExtension` (x < −356 mm). §6.5's birth certificate
and §8.1's patch check both use this five-patch list, and the planted perturbation of §8.2
confirms the reader sees exactly this set.

### A2.3 Why it matters — sized by the already-registered method

The friction-line method registered in `cases/PPTC_VP1304/shaft_sizing_estimate.py` (fixed
before its own arithmetic was run), applied unchanged to each non-blade rotating surface at
J = 1.2021. **ESTIMATE, order of magnitude, not a measurement.**

| surface | contribution to 10KQ | as % of measured |
|---|---|---|
| hub cylinder | 0.00180 | 0.23% |
| nose cap | 0.00023 | 0.03% |
| aft fairing | 0.00130 | 0.17% |
| CAD shaft (x −200…−356) | 0.00042 | 0.05% |
| **model non-blade subtotal** | **0.00376** | **0.49%** |
| **`shaftExtension` (artificial, x −356…−1500)** | **0.00205** | **0.27%** |
| **total if both were wrongly left in** | **0.00581** | **0.76%** |

**+0.76% is only 9% of the 10KQ band half-width, so this could not by itself flip the gate.
It is 19% of the top of the prediction window in §5, and it carries the SAME SIGN.** §5
predicts CFD 10KQ above measured by 1 to 4% because fully turbulent RANS misses laminar
regions on the model blades. An uncorrected non-blade torque of +0.76% would push 10KQ up for
a reason that has nothing to do with transition, and would be indistinguishable from the
predicted physics after the fact. **That is why this is fixed before the solve and not
explained afterwards.** The `shaftExtension` term is the worst of it in principle, because it
scales with a length we chose rather than one the experiment had: at 1.144 m it is three
times the shaft length the CAD actually contains.

### A2.4 What is NOT claimed here

The friction-line estimate is not offered as a correction to be subtracted from a result. It
sizes the error that the patch-list change **avoids**. Nothing is subtracted from any computed
force at any point: the correct patches are integrated, and that is the whole of the fix.

Also disclosed, again: annex A2.1's sentence "The configuration is with the shaft in upstream
direction" contradicts §5 and the eleven test-table headers reading "Propeller shaft
downstream". The headers and §5 remain authoritative, as recorded in
`GEOMETRY_ADMISSION_RECORD.md` §2, and that sentence is used for nothing here either — the
torque-correction sentence quoted in A2.1(i) above is a different sentence on the same page
and is corroborated independently by (ii) and (iii).

---

## AMENDMENT 3 — 2026-09-12, before first compute. THE THRUST SIDE, ESTABLISHED RATHER THAN INHERITED, AND THE COMPLETE TERM-BY-TERM MAPPING

*lines whose number changed above this section: 0*

**Version 1.3.** **No registered quantity changes.** The thrust patch list of Amendment 2 is
confirmed exactly as it stands. What changes is its **basis**: Amendment 2 carried the thrust
list forward as "unchanged", and "unchanged" meant *unchanged from the same sentence of §3.2
that Amendment 2 had just shown to be Sanaa's gloss rather than the annex's words.* **A gloss
that failed on one half of a pair is not evidence for the other half.** This amendment
establishes the thrust half from the sources, and it happens to confirm it.

**Legality.** Before first compute; **`verification/runs/PPTC_VP1304/` does not exist.**
Alters no gate, threshold, cap or label.

### A3.1 The thrust chain, read the same way the torque chain was read

SVA's correction sheets, in full:

| sheet | thrust | torque |
|---|---|---|
| Pre-test I (V = 0) | T_meas = T_gap + T_bearing | Q_meas = Q_gap + Q_hub + Q_bearing |
| Pre-test II (dummy hub, V > 0) | T_meas = T_gap + T_bearing + **T_hub** | Q_meas = Q_gap + Q_bearing + Q_hub |
| Open water test | T_meas = T_gap + T_bearing + T_hub + **T_blade** | Q_meas = Q_gap + Q_bearing + Q_hub + Q_blade |
| **Sheet 4, "blades and hub" — PAGE 2.11, OUR COMPARATOR** | **T = T_meas − T_gap − T_bearing = T_blade + T_hub** | **Q = Q_meas − Q_gap − Q_hub − Q_bearing = Q_blade** |
| Sheet 5, "blades only" — page 2.13 | T = T_meas − T_gap − T_bearing − T_hub = T_blade | Q = Q_meas − Q_gap − Q_bearing − Q_hub = Q_blade |

**The asymmetry is now explained rather than observed.** `Q_hub` is subtracted in *both*
configurations, so the two torque columns are identical — which is exactly why 10KQ matches
digit-for-digit at all fourteen J. `T_hub` is subtracted in *only one*, so the two thrust
columns differ by precisely `T_hub` — which is exactly why KT differs by 0.0125 at
J = 1.2021 (0.2797 against 0.2922), the sign being negative because the bladeless assembly
produces drag, so removing it raises KT. **One algebra predicts both the identity and the
difference, and both are observed.**

**What `T_hub` contains.** Report 3752 §6: tests 11F0392 and 11F0393 "show the resistance and
torque of the hub without blades", using a dummy hub "having the same shape and mass as the
real propeller hub". Report 3752 page 4.2's photograph "Dummy hub configuration" shows that
assembly: nose cap, hub body, aft fairing and the wetted shaft, mounted on the dynamometer at
the same 1.5 D submergence. **`T_hub` is therefore the axial drag of the entire bladeless
rotating assembly including its wetted shaft — and page 2.11 RETAINS it.**

> **Therefore page 2.11's KT represents blades PLUS the whole hub assembly including the
> wetted shaft. Sanaa's gloss is correct on thrust, and it is now established from the
> sources instead of inherited from a sentence that failed on torque.**

### A3.2 The complete term-by-term mapping

Every term in SVA's algebra, against what our CFD produces:

| experiment term | in page 2.11 KT? | in page 2.11 10KQ? | does our CFD produce it? |
|---|---|---|---|
| `T_blade` / `Q_blade` | **yes** | **yes** | yes — patch `blades` |
| `T_hub` / `Q_hub` (bladeless assembly: cap, hub, fairing, wetted shaft) | **YES** | **no, subtracted** | yes — patches `hub`, `cap`, `shaft` |
| `T_gap` / `Q_gap` (flow in the gap between hub and dynamometer shaft, pre-test I at V = 0) | no, subtracted | no, subtracted | **no** — that gap is not in our geometry; the CPP root gap is closed per §2.2(a) and the hub/shaft gap is not modelled |
| `T_bearing` / `Q_bearing` (dynamometer bearings) | no, subtracted | no, subtracted | **no** — mechanical, not fluid |

**Every term the comparator retains, our integration produces; every term the comparator
subtracts, our geometry does not produce.** The two correspond without any residual
correction on either side, which is the condition for the comparison to be clean. The
Amendment 2 patch lists follow from this table and are unchanged by it:

> **KT: `blades` + `hub` + `cap` + `shaft`.  KQ: `blades` only.
> `shaftExtension`: excluded from both.**

`shaftExtension` remains excluded because `T_hub` was measured on the model's *wetted* shaft
at the rig's fixed submergence, not on the 1.144 m of additional rotating wall our outlet
placement requires. The CAD's own aft termination at x = −356 mm is SVA's representation of
the model, and it is taken as the wetted extent.

### A3.3 FOR THE CERTIFICATE — excluded from the integration is NOT excluded from the physics

A reader who sees "KQ over blades only" and "`shaftExtension` excluded from both" could
reasonably conclude the shaft need not have been meshed at all. **It does, and it is.**

> The hub, cap, shaft and shaft extension are **fully modelled** — meshed, with prism layers,
> as rotating no-slip walls — and they shape the flow the blades work in: the hub blockage at
> the blade roots, the aft fairing's pressure recovery, and the wake the shaft trails
> downstream. They are **excluded from the graded surface integrals only**, because the
> measurement we grade against had their contribution removed by the idle-torque correction
> (torque) or bounded to the physical model (the shaft extension). **Modelled, not
> integrated.** Removing them from the mesh would change the answer on the blades; removing
> them from the integral is what makes the answer comparable.

---

## AMENDMENT 4 — 2026-09-13, before first compute. THE SMOKE MAY RUN ON A LAYERLESS MESH UNDER THE WALL-FUNCTION CLAUSE, THE y+ WINDOW IS WIDENED TO THE LOG-LAYER RANGE, AND NEITHER OF THOSE CURES §6.4

*lines whose number changed above this section: 0*

**Version 1.4.** This amendment **alters no gate, threshold, cap or label** of the graded
result. It changes one *mesh specification* (§6.3) and one *wall-treatment window* (§6.3,
§5 of Sanaa's directive). The bands of §4, the gate of §4.8, the prediction of §5, the
smoke predictions of §8.3 and every verdict label are untouched.

**Legality.** CLAUDE.md rule 2: before first compute, amendments are legal **and must state
the condition and how it was checked.** *The condition is that no compute has occurred for
this act.* **How it was checked:** a recursive search of the act's entire run tree
`/home/ubuntu/certonomous-runs/PPTC_VP1304/` for any solver time directory, any
`postProcessing/`, any `forces*` output and any `log.simpleFoam*` returned **nothing**, and
**that reader was shown able to return something**: the identical search over a planted tree
containing one empty `log.simpleFoam` and one empty `postProcessing/` returned both
(CLAUDE.md rule 3 — a zero from a reader not shown able to see a non-zero is not evidence).
Mesh builds have occurred; no solver has been launched, and no `KT` or `KQ` value exists
anywhere in this act.

### A4.1 What §6.3 says, and what is being changed

Registered, §6.3: *"Prism layers on blades, hub, cap and shaft: **6 layers, growth ratio
1.2**, first-cell height set for **y+ 30 to 60 with wall functions** (registered wall
treatment…)"*.

Two distinct clauses live in that sentence and this amendment separates them.

**(a) The layer clause.** Registered: 6 layers at ratio 1.2 on four patches.
**Amended: the smoke of §8.3 may be run on a mesh carrying ZERO prism layers.** The
justification is the sentence's own second clause: the registered wall treatment is a
**wall function**, and a wall function does not require a prism layer — it requires the
first cell centre to lie in the logarithmic layer. A layerless hexahedral cell at the
surface satisfies that condition or it does not, and which it is, is a measurement.
Layer coverage remains **DISCLOSED, never a gate**, and a shortfall caps the fidelity chip
rather than moving a band (the standing ruling already carried on every birth certificate of
this act). **This amendment applies to the SMOKE of §8.3 only. The graded design-point
family of §10 item 3 is not amended and still carries the §6.3 layer specification.**

**(b) The y+ window.** Registered: **30 to 60**. **Amended: 30 to 300**, the validity range
of the log-layer wall function, for the smoke only. This is registered as what it is — a
**widening of a registered specification**, made before the measurement that tests it, and
declared so that the measurement can still fail: y+ outside 30–300 fails it.

### A4.2 THE y+ PREDICTION, REGISTERED HERE BEFORE IT IS MEASURED

The mesh this applies to carries a **0.625 mm** surface cell on `blades` (refinement level
5 on a 20 mm background). With no layer, the first cell centre sits at **0.3125 mm**. From a
flat-plate skin-friction estimate `Cf = 0.058 Re_c^-0.2` at J = 0.7985, n = 15 s⁻¹,
ν = 1.124e-6 m²/s, ρ = 998.99 kg/m³:

| station | U [m/s] | Re_c | u_τ [m/s] | **predicted y+** |
|---|---|---|---|---|
| r/R = 0.30 (root) | 4.632 | 3.02e5 | 0.2233 | **62** |
| r/R = 0.70 | 8.773 | 8.13e5 | 0.3831 | **107** |
| r/R = 0.90 | 11.018 | 8.25e5 | 0.4804 | **134** |

> **REGISTERED PREDICTION.** Measured `blades` y+ after 300 iterations lies in **50 to 200**
> (mean over the patch), i.e. **inside the amended 30–300 window and ABOVE the originally
> registered 30–60 window.** A measurement outside 50–200 falsifies this prediction and is
> recorded as a miss; a measurement outside 30–300 fails clause (b) and stops the layerless
> route.

**The instrument is fixed here and may not be chosen at run time.** y+ is read with the
solver's own spelling `simpleFoam -postProcess -func yPlus` and **never** with the generic
`postProcess`, which on this build (OpenFOAM v2606, `_481094f-20260618`) returns zero on
every patch and exits clean — measured 53 of 53 patch readings across two solvers. The
reading passes through `scripts/yplus_reader_guard.py`, which refuses both failure modes.

### A4.3 WHAT THIS AMENDMENT DOES NOT DO — and the reason it is written in the same breath

**It does not waive §6.4 and it does not waive §6.5.** The only 360° mesh on disk,
`/home/ubuntu/certonomous-runs/PPTC_VP1304/F360_coarse`, **fails four blocking gates**
(`BIRTH_CERTIFICATE.txt`, `log.checkMesh`): max non-orthogonality 162.92° against < 70; max
skewness 191.88 against < 4; max adjacent-cell volume ratio 3383.04 against ≤ 1.25; and
**316 cells of negative volume**, minimum −5.72499e-10 m³, against the lab's `> 0`.
§6.5 is unchanged: *born clean or it does not enter.*

**Consequence, registered:** a solver run on that mesh can produce a y+ field and a
dead-lever reading, and it **cannot produce a KT or a KQ of any grade.** Any thrust
coefficient obtained from it is labelled **NOT A RESULT** on the mesh gate alone, before its
value is looked at. Nothing in this amendment permits otherwise, and no later reading of it
may be used to argue otherwise.

### A4.4 COST — the registered smoke line does not cover this mesh

§9 sizes the smoke at **0.8 M cells, 4 ranks, 300 iterations, 12 core-min** — a 72° passage.
The 360° mesh is **19,700,035 cells**, 24.6× that. At §9's own declared basis of
3.0e-6 core-s per cell per iteration the same 300 iterations cost **295.5 core-min**, and the
§9 table's full-360 line assumed 4.0 M cells, which is **4.9× short of the mesh that was
built**. Registered here so the overrun is a predicted number and not a discovery:
**a 300-iteration smoke on F360_coarse is estimated at 295.5 core-min**, against the 12
core-min smoke line. Per Sanaa's NO CAP ruling no run is stopped by it; the act's registered
cap of 19,890 core-min is **not raised**, and the calibration row is mandatory at completion.

### A4.5 Status

**Pre-compute. No gate, threshold, cap or label is altered.** The layer clause is relaxed for
the smoke only; the y+ window is widened for the smoke only; the quality gates of §6.4, the
admissibility rule of §6.5, and the smoke predictions of §8.3 (KT sign POSITIVE, KT between
0.4 and 0.6, a NEGATIVE KT stops the case) stand exactly as frozen.

---

## AMENDMENT 5 — 2026-09-13, before first compute. HOW THE FREEZE IS RESOLVED, AND NOTHING ELSE: THE COMPARATOR'S C1 CHECK FAILED PRECISELY WHEN THIS DOCUMENT DID THE LEGAL THING

**Legality.** CLAUDE.md rule 2: before first compute, amendments are legal and must state
the condition and how it was checked. **Condition: no PPTC solve has been graded by
`analyse_pptc.py`.** **Checked at the location the runs ACTUALLY USE** —
`/home/ubuntu/certonomous-runs/PPTC_VP1304/` — swept for any solver time directory, any
`postProcessing/`, any `forces*` output and any `log.simpleFoam*`, the same sweep A4 ran.
🔴 **This amendment deliberately does NOT cite `verification/runs/PPTC_VP1304/`, which
AMENDMENTS 1–3 named.** That path is not the run root and never was; those amendments'
condition was therefore *true of a path that was never going to exist* — vacuous, though
substantively correct (A1–A3 were committed 22:54–23:07Z on 2026-09-12 and the first run
directory anywhere under the real root is 2026-09-13 04:32Z, five and a half hours clear).
**A control checked against the wrong location cannot fail, which makes it not a control.**
A4 corrected the method; this amendment keeps the correction.

**Nothing registered moves.** No gate, threshold, band, cap or label is touched. Verified
mechanically: every module-level constant in `analyse_pptc.py` is byte-identical except the
freeze-mechanism names themselves (`PREREG_BLOB`/`PREREG_SHA256` replaced by
`PREREG_BLOB_AT_COMMIT`/`PREREG_SHA256_AT_COMMIT`, and `PREREG_VERSION`). `PREREG_COMMIT`
is unchanged.

### A5.1 The defect — the check was not implementing the rule it cited

Rule 2 requires verifying that the frozen file **is** the file that ran **by hashing it
against the committed blob**. The check being replaced hashed **the whole file on disk**
against one stored `sha256`. Because rule 2 *also* permits dated amendments before first
compute, **every legal amendment invalidated the pin**, which then had to be re-set by hand.

**Measured 2026-09-13:** `analyse_pptc.py --selftest` exited 2 at C1 and printed no
coefficient, because AMENDMENT 4 had been appended that day while the pin still carried the
v1.3 `sha256`. **The comparator was correct by its own written rule and wrong in substance,
and it was blocking every PPTC grade.**

**The document was verified innocent before the instrument was touched.** The change since
the freeze commit `09396b48` is a **single hunk at the foot** — `@@ -752,3 +752,415 @@`,
754 → 1166 lines — and **the first 754 lines are byte-identical**, `sha256
5611e24bee05ecc5862f1907166efc9015f3875c7035265e922a3174f777ad38` on both sides. Pure
append, exactly as rule 6 requires.

### A5.2 🔴 A second defect, found while repairing the first: the pin named a pairing that does not exist

The old constants named **a blob and a commit that do not go together**:
`PREREG_BLOB = 845974fab273…` is the blob at commit **`4f3e99de6`** (AMENDMENT 3), while the
blob at `PREREG_COMMIT = 09396b48…` is **`7047d9aad5da…`**. A previous re-pin updated the
`sha256` and the blob to v1.3 and left the commit at the original freeze. **The refusal
message the comparator printed — "committed blob 845974fab… at 09396b48…" — asserted a
pairing that has never existed.** The constants are now mutually consistent and each is
verified against `git` rather than transcribed.

### A5.3 The replacement, and why it is strictly stronger

Two clauses, drawn from **two different sources** — the git object store and the filesystem —
so this is not an assert comparing a thing with itself:

| | clause | source |
|---|---|---|
| **F1** | the frozen text read at `PREREG_COMMIT` must hash to the declared blob **and** `sha256` | `git cat-file` — **no edit on disk can defeat it** |
| **F2** | the file on disk must **begin with** that frozen text, byte for byte | the filesystem |

**F2 is a clause the old whole-file hash could not express at all**: it enforces rule 6's
*"lines whose number changed above this section: 0"* mechanically. A legal appended
amendment passes; an in-place edit anywhere above the appended tail fails. **The old check
verified one thing weakly; this verifies two, one of which was previously unenforced.**

This is the mechanism CRM's `ADDENDUM 13 D0` identified and `A14.8` ruled for that act —
*"a document that is pinned as a frozen instrument cannot also be the document that grows an
addendum for every subsequent rung"* — **pin by commit, resolve with `git cat-file`, never
from disk.** PPTC carried the identical defect and it bit harder: CRM's only threatened a
spurious `DRIFTED` stamp, PPTC's stopped the comparator dead.

### A5.4 🔴 The failing-direction controls, because a freeze check that cannot fail is worse than one that fails too often

**Six clauses, each driven to REFUSE on a case built to break it, and then the real pin
required to PASS.** They run **on every invocation, before the instrument is pointed at
anything** — the habit taken from `verification/runs/PPTC_VP1304_runs/spd_gate.py:257`;
an instrument armed once and trusted thereafter is an instrument nobody is checking.

| control | construction | required |
|---|---|---|
| `F1/blob` | declared blob mutated | REFUSE |
| `F1/sha256` | declared `sha256` mutated | REFUSE |
| `F1/commit` | pin pointed at `HEAD` instead of the freeze | REFUSE |
| `F2/append-accepted` | frozen text **+ an appended amendment** | **PASS** |
| `F2/inplace-refused` | **one byte flipped inside the frozen region** | REFUSE |
| `F2/truncation-refused` | frozen text truncated | REFUSE |

The fixtures are written to a temporary directory **outside the repository**; nothing is
written into the working tree by a control.

### A5.5 Status

**Pre-compute for the grading path. C1 and C2 pass; C3 still requires a case with forces
output. This amendment is itself the first live exercise of the repair: appending it changes
this document's whole-file `sha256`, which is exactly what used to break C1 — and C1 now
passes, because the frozen text at `09396b48` is unchanged and this text is appended below
it.**

---

## AMENDMENT 6 — 2026-09-13, before first compute. C4: A FORCE MAY NOT BE READ FROM A RUN THAT DID NOT FINISH, OR FROM A PROPELLER THAT DID NOT ROTATE

**Legality.** Rule 2, before first compute. **Condition: no PPTC solve has been graded by
`analyse_pptc.py`.** Checked at `/home/ubuntu/certonomous-runs/PPTC_VP1304/` — the run root
the runs actually use — as A5 established. **Nothing registered moves.** C4 is
**refusal-only**: standing rule 5 lets a gate turn a reading *into* `NOT A RESULT` and never
the reverse, so C4 can withhold a KT and **can never produce, improve or rescue one**. No
gate, threshold, band, cap or label is touched.

### A6.1 The gap

C1, C2 and C3 test the freeze, the physics constants and the parser. **None of them asks
whether the run finished or whether the propeller rotated.** Without C4 this comparator
reads KT and KQ off a force file whatever produced it.

### A6.2 The hazard is measured, not hypothesised

On the CRM wing-body act, `SOLVE_T_SST` died of SIGFPE at iteration 22 with its field at
`p max 3.86761822375e+129`, and **six of its twenty-one steps still carried a pressure Cd
inside the admissible band [0, 0.2]** — +0.0800, +0.0538, +0.0404, +0.0170, +0.0004,
+0.0091 — while the total ran to −4.414128e+88. A plausible, band-passing coefficient out of
a destroyed solution.

**On this act the same shape has a sharper form.** `dead_lever_audit.sh:8-12`: a `cellZone`
naming a zone that does not exist means **MRF silently does nothing, the propeller does not
rotate**, and the case converges to a tidy number that looks like a bad mesh rather than
like no rotation at all. **A KT from a stationary propeller is the same family as SST's quiet
pressure Cd: a plausible number from a dead configuration.**

### A6.3 The clauses

| | clause | basis |
|---|---|---|
| **G-1** | the run satisfies **standing rule 4** in full — rc, `End`, last time == `endTime`, fields at `endTime`, the step set, and the **age guard** | the D631 **strongest** reading: distinct physics steps **unioned across log segments**, set == {1…endTime}, via `scripts/solver_log_set.py` |
| **G-2** | the **MRF lever is live** — `MRFProperties` names a `cellZone`, that zone is on disk, it is non-empty, and `omega` ≠ 0 | structural; **needs no registered threshold** |
| **G-3** | a field ceiling | 🔴 **`BLOCKED` pending registration — and deliberately not invented** |

**On G-3, stated plainly because the temptation was real.** CRM's comparator gates `p` and
`max|U|` against `2·p₀` and `2·U∞`. **Those numbers do not transfer**: PPTC is
incompressible, its `p` is kinematic, and its velocity scale is blade tip speed, not a
freestream. **This pre-registration registers no field bound or divergence criterion** —
swept for one before writing this. Importing CRM's constants would be exactly the error this
act has already made three times: *a number carried across from the run that is not the run.*
**G-1 alone would have refused the SST artifact G-3 exists for** — rc=136, no `End` line, 21
steps of its registered length.

### A6.4 The controls, driven in both directions, on every invocation

Nine clauses. **Eight fixtures each built to break exactly one clause and required to
REFUSE *on that clause* — a gate that refuses for the wrong reason is not evidence about the
right one — and the clean fixture required to stay READABLE, because a gate that refuses
everything is not a gate.**

| fixture | required |
|---|---|
| clean run | **READABLE** |
| `rc != 0` (SST's shape) | REFUSE on G-1 |
| no `End` line (SST's shape) | REFUSE on G-1 |
| stopped short (SST reached 21 of its length) | REFUSE on G-1 |
| no `endTime` fields | REFUSE on G-1 |
| `endTime` fields older than `0/` — the age guard | REFUSE on G-1 |
| MRF `cellZone` absent from disk — **dead lever** | REFUSE on G-2 |
| MRF `omega` == 0 — **dead lever** | REFUSE on G-2 |
| `MRFProperties` absent entirely | REFUSE on G-2 |

They run **before the instrument is pointed at anything**, as C1's do. Fixtures are built in
a temporary directory and never in a run tree.

### A6.5 Status

**Pre-compute. C1 PASS, C2 PASS, C4 armed. C3 still requires a case with forces output.**
Exercised against the real staged `SMOKE360_J0.7985`, which C4 refuses on G-1: it carries
`0.orig`, `constant` and `system` and has not solved.

---

## AMENDMENT 7 — 2026-09-13, before first compute. 🔴 G-2's CELL COUNT WAS READING THE FoamFile HEADER: 1 WHERE THE TRUTH IS 11,412,958, AND THE "NON-EMPTY" CLAUSE AMENDMENT 6 CLAIMED DID NOT EXIST

**Legality.** Rule 2, before first compute. Condition: no PPTC solve has been graded by
`analyse_pptc.py`; checked at `/home/ubuntu/certonomous-runs/PPTC_VP1304/`. **Nothing
registered moves.** Still refusal-only.

**This amendment corrects AMENDMENT 6, which overstated what G-2 checked.** A6.3 says G-2
requires the MRF zone to be *"on disk, non-empty, and `omega` ≠ 0"*. **The non-emptiness
clause was not implemented, and the count it reported was wrong.**

### A7.1 How it was found — the ordered read, on the first real file

The supervisor ordered one real read of a decomposed `cellZones` before the design-point
family launches, because that path had only ever seen a hand-written ASCII fixture. **The
first real read caught it**, on `SMOKE360_J0.7985`:

| | |
|---|---|
| G-2 reported | `cells_in_zone: 1` |
| the file's own declaration | `cellLabels List<label>` **`11412958`** |

### A7.2 The fault

A real `cellZones` names the zone **twice**: once in the FoamFile header —

```
    meta
    {
        names           ( MRFzone );
    }
```

— and once as the zone's own definition. **The parser split on the FIRST textual occurrence,
landed in the header, and took the first digits-only line after it: `1`, the NUMBER OF
ZONES.** Real files are also `format binary`; the count is ASCII and precedes the payload.

**The verdict was not wrong** — nothing gated on the count — **but that is the accident, not
the design.** An empty zone would have reported `1` and **passed the clause written to catch
exactly that**, which is the dead lever this act has already produced once.

### A7.3 The repair

`zone_cell_count()` locates the zone's **own block** — a line that *is* the zone name
followed by `{` — and reads the count from its `cellLabels … List<label> <n>` declaration,
the only place the cell count is stated. Only the file head is decoded; the binary payload is
never parsed. **G-2 now gates on `ncells > 0`, as A6.3 claimed.**

Verified against the real file: **11,412,958, matching its own declaration exactly.**
Verified decomposed: **eight trees carrying real binary `cellZones` heads summed to their
exact total**, and an empty zone now **REFUSES**.

### A7.4 🔴 The fixture is the lesson

The hand-written fixture that preceded this had **no `meta { names ( … ) }` header**, so it
**could not reproduce the fault** — the parser passed a test that did not contain the trap.
**Every fixture for this parser now carries the header**, and a regression control asserts
the count is 11,412,958 and not 1.

**A fixture simpler than the artifact is not a control; it is a rehearsal.** The naive parser
passed nine clauses of its own suite and was caught by one read of a real file.

### A7.5 Status

**Pre-compute. C4 controls now 12 clauses — 11 driven to REFUSE, the clean fixture to
READABLE — including the header-trap regression and a decomposed eight-tree sum. The
supervisor's ordered pre-flight is DISCHARGED and it fired.**
