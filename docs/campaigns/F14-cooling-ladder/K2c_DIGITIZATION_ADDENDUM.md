# K2c-A. Digitization addendum: arming the reference column from Wibron 2018

Campaign F14, rung K2c, addendum to `K2c_RACK_ROW_VALIDATION_SEARCH.md` §3.1.
Written 2026-08-17. **Zero compute spent, no solver launched, no compute
authorization requested or required.** Every figure below was re-derived by the
command named in §9 against the repository frame `fc1e3bac`; nothing was carried
over from the brief that dispatched this work.

**Frame note.** HEAD moved to `676e2bb8` while this addendum was being written.
That commit changed `LESSONS.md` and `LOCATIONS.md` and nothing else
(`git show --numstat 676e2bb8`), so none of the objects measured below moved:
the source PDF, `scripts/heat_balance.py` and
`K2c_RACK_ROW_VALIDATION_SEARCH.md` are byte-identical at both frames. Every
anchor in this document therefore stays at `fc1e3bac`, which is the frame the
measurements were taken at.

**Scope, stated first so this document cannot be misread as more than it is.**
This addendum arms the **reference column of rung K2c-A only**, and only some of
its rows. It changes nothing about:

| Unchanged by this addendum | Status as of `fc1e3bac` |
| --- | --- |
| **Rung K2c-B, raised floor / perforated tile** | **NOT OBTAINED in its entirety.** Eight papers with DOIs, every Unpaywall check dated 2026-08-17, every one `is_oa: false`. No gate rows exist and none are written here. Any K2b solve of the tile-supply configuration is **TREND-ONLY however well it converges** |
| The three NOT OBTAINED records of `K2c_RACK_ROW_VALIDATION_SEARCH.md` §4 | All three stand. The second of them (digitized reference values from Wibron 2018) is discharged by this document; the first (any raised-floor measurement primary) and the third (Hamann et al. DOE report, OA but unread) are untouched |
| Whether any solve has run against K2c-A | **None has.** The rung's own header still reads NO SOLVE MAY RUN UNTIL THE OWNER APPROVES THE K2a SPECIFICATION AND AUTHORIZES COMPUTE |
| K0d | Still TREND-ONLY, still awaiting its primary |

**What this addendum is.** Digitization was treated as a measurement and is
reported as one: a stated method, an uncertainty derived rather than asserted,
seven controls with recovery errors, and a label on every value. Where a
quantity could not be armed it is said so, by name.

---

## 1. The method

### 1.1 What was read, and what was not

The primary is `docs/papers/wibron_ljung_lundstrom_2018_en11030644.pdf`,
SHA-256 `4de4798ed5eed60feda123c7a2398674a6a9177f44906175847d90f5227d7b77`,
re-verified by the extraction command itself, which refuses to run on a
mismatch. Tier READ IN FULL.

| Figure | Journal page | PDF object | Content | Digitized here |
| --- | --- | --- | --- | --- |
| 3a, 3b | 7 | `/Im5`, `/Im6` (Form) | L1 velocity profile, three grids plus Richardson extrapolation; fine grid with GCI band | Yes, for control C2 and C5 only |
| 6a, 6b | 10 | `/Im12`, `/Im13` (Form) | Per-rack front and back temperatures, CFD and experiment, with experimental error bars | **Yes, this is the temperature reference** |
| 7a to 7e | 11 | `/Im14` (Form, five panels) | Measured and computed velocity profiles at L1 to L5 | **Yes, this is the velocity reference** |
| 8a, 8b | 11 | `/Im15`, `/Im16` (Form) | L1 and L2 profiles moved 5, 10, 15 cm toward the hot-aisle centre | Yes, for control C6 only |
| 1, 2 | 4 | `/Im3`, `/Im4` (Image) | Geometry and labelled components | No. Raster |
| 4, 5, 9, 10 | 8, 9, 12, 13 | Image objects | Streamlines, contour planes | No. Raster, and qualitative in the gate |

That every graded figure is vector and every non-graded one is raster was
measured, not assumed: `pdfimages -list` reports no image object on pages 7, 10
or 11, and pypdf reports `/Subtype /Form` for the seven objects on those pages.

### 1.2 How the points were extracted

**This is not pixel digitization.** The four graded figures are PDF Form
XObjects whose content streams carry the plotted geometry as path operators, so
the extraction reads coordinates that the plotting program wrote, not pixels a
renderer produced. The pipeline, in the order it runs:

1. **Tokenize and replay** the form's content stream, tracking the graphics
   state (stroke gray, fill gray, line width) and collecting every painted path
   with the state it was painted under.
2. **Find the axes rectangle** (the white-filled `re` the plotting program emits
   as the plot box) and the **tick marks**, which are short stroked segments
   planted on the box edges.
3. **Calibrate** by least squares of tick position against the tick label values
   read from the same stream's text operators. The fit residual is reported per
   panel and IS the calibration error; it is in the table of §2.
4. **Read the data primitives.**
   - Figure 6 bar charts: the bar is an `re` and its height is the value. White
     fill is the CFD series, black fill the experimental series; the pairing was
     taken from the legend keys in the same stream (`CFD model` label at raw x
     2310 with the white swatch at 1980 to 2280, `Exp.` at 3500 with the black
     swatch at 3170 to 3470) and is corroborated by the fact that only the black
     series carries error bars, which the paper calls experimental.
   - Error bars: stroked segments. The **cap midpoint is a second, independent
     encoding of the same datum** and is compared against the bar height as
     control C7.
   - Figures 7 and 8 experimental points: closed eight-segment polygons, that
     is, circles drawn as octagons. The centre is the mean of the vertex
     extrema, which is exact for a symmetric marker.
   - Figures 3, 7 and 8 computed profiles: 500-vertex polylines. Each vertex is
     a datum.
5. **Exclude legend keys explicitly.** In Figure 7 the legend sits above the
   panels and a box test suffices. In Figure 8 the legend sits **inside** the
   axes box, so a box test alone silently admits the legend's own marker as a
   fourth data point at 1.32 m/s. It did, on the first run of this extraction,
   and it inflated the velocity digitization uncertainty by a factor of 140
   before the check in §2.3 caught it. The extractor now excludes the bounding
   box of the legend line keys, extended by one inter-key row pitch, because the
   marker key has no line sample and sits one row outside the line keys' own box.

**Resolution.** The graded values were read at these resolutions, which are the
resolutions of the primitives themselves and not of any raster:

| Quantity | Raw stream units per data unit | Coordinate precision in the stream | Resolution before any other error |
| --- | --- | --- | --- |
| Figure 6 temperature | 77.1250 per degree C | 6 significant figures | 6.5e-5 deg C |
| Figure 7 velocity | 718.752 per m/s | 6 significant figures | 7e-6 m/s |
| Figure 7 height | 771.430 per m | 6 significant figures | 6e-6 m |

Stroke width never enters any value. Curve thickness is a pixel-reading error
source and there is no pixel reading here.

**Reader repeatability is zero by construction.** The extraction is
deterministic and re-running the command in §9 reproduces byte-identical output.
That removes what is normally the dominant digitization error and replaces it
with the four measured ones of §2.

### 1.3 Which curve is which

Figure 7's three computed curves are drawn in three grays with no colour and the
legend labels are laid out shifted by one entry relative to the swatches, so the
pairing was derived rather than eyeballed, and then checked twice:

| Stroke gray | Legend label | How the pairing was established | Independent check |
| --- | --- | --- | --- |
| 0.800781 | k-epsilon model | Label drawn as glyph outlines (the epsilon and the en dash force outlining, so it does not appear in the text layer at all) spanning raw x 3680 to 4242, immediately right of the swatch at 3350 to 3650 | Differs from the RSM curve by up to 0.585 m/s, the largest of the three, which is the paper's own statement that k-epsilon fails in the low velocity regions |
| 0.501953 | RSM | Text label at raw x 4620, immediately right of the swatch at 4290 to 4590 | **Control C5**: identical to Figure 3a's "Fine grid" curve, which the Figure 3 caption states is RSM at L1, to 1.2e-5 m/s over 500 vertices |
| 0.0 | DES | Text label at raw x 5290, immediately right of the swatch at 4960 to 5260 | Differs from RSM by at most 0.171 m/s, rms 0.043, against k-epsilon's 0.585 and 0.269. The paper's "RSM and DES produce very similar results" |

Figure 6's panel identification was taken from content, not from stream order:
`/Im12` reads 19.7 to 20.2 deg C and `/Im13` reads 32 to 36 deg C, so `/Im12` is
panel (a), the cold front side, and `/Im13` is panel (b), the hot back side, as
the caption states. Figure 8's panels were identified by data: `/Im15`'s
experimental points reproduce Figure 7a's L1 points and `/Im16`'s reproduce
Figure 7b's L2 points.

---

## 2. The digitization uncertainty, derived

### 2.1 What contributes, and what each contribution measures

| Contribution | Temperature (Fig 6) | Velocity (Fig 7 markers) | Height (Fig 7 markers) | How it was obtained |
| --- | --- | --- | --- | --- |
| Axis-tick calibration error | 4.9e-7 deg C | 5.8e-9 m/s | 5.0e-9 m | Maximum residual of the least-squares fit of tick position against tick label value; 9 ticks on Fig 6, 4 and 7 ticks per Fig 7 panel |
| Pixel-to-data scale error | not applicable | not applicable | not applicable | There is no pixel stage. The scale is the tick fit above |
| Coordinate quantization in the stream | 6.5e-5 deg C | 7e-6 m/s | 6e-6 m | Coordinates printed to 6 significant figures, so plus or minus half a unit in the last place |
| Curve thickness | 0 | 0 | 0 | Values come from path geometry. The 5, 15, 25 and 30 unit stroke widths never enter |
| Reader repeatability | 0 | 0 | 0 | Deterministic extraction, byte-identical on re-run |
| Primitive placement | 6.5e-5 deg C (C7) | **0.0060 m/s (C6)** | **0.0043 m (C6)** | The dominant term for markers, and it is not derivable from the stream: it is measured by digitizing the same datum from two different figures |
| Independent physical bound | **0.029 K (C4)** | not applicable | not applicable | Residual of Eq. (9) over eight racks, which also carries the paper's own front-face averaging term and therefore over-states the reading error |

### 2.2 The increments adopted

Each adopted increment is the **largest control-established bound** for its
quantity class, rounded up to the reporting step. The conservative bound was
taken deliberately: a gate band that under-states the reading error claims a
precision this extraction did not measure.

| Quantity class | Measured bound | Control it came from | **Adopted increment** |
| --- | --- | --- | --- |
| Temperature, Figure 6 bars | 6.5e-5 deg C internal; 0.029 K independent | C7 internal, C4 independent | **plus or minus 0.03 K** |
| Velocity, Figure 7 experimental markers | 0.0060 m/s max, 0.0037 m/s rms | C6 | **plus or minus 0.007 m/s** |
| Height, Figure 7 experimental markers | 0.0043 m max | C6 | **plus or minus 0.005 m** |
| Velocity, computed polylines | 1.2e-5 m/s | C5 | plus or minus 0.0001 m/s (not used in any gate reference) |

The temperature increment is 460 times the internal estimate. That gap is
deliberate and is the honest reading: C7 measures only whether two encodings of
the same drawn number agree, while C4 measures whether the drawn numbers satisfy
a relation the paper states in prose with tabulated inputs. Only C4 can catch a
systematic error common to both encodings, so C4 is the bound that is adopted.

### 2.3 What could not be quantified, stated so it is not claimed

**Whether the value the authors plotted equals the value they measured.** Any
rounding, averaging or transcription between instrument and figure is invisible
to every control above and is not covered by any of them. The digitization
uncertainty reported here is the uncertainty of **reading the figure**, and
nothing more. A reader who needs the difference must ask the authors for the
data; the CC-BY licence does not supply it.

**Two secondary unknowns, named:**

- The measurement heights recovered as 0.506, 0.998, 1.504 and 1.996 m, which
  are consistent with a nominal 0.5, 1.0, 1.5, 2.0 m ladder to within 0.006 m.
  **The paper never states the heights**, so that consistency is a corroborating
  observation and not a control, and the digitized heights are carried as
  digitized.
- The rack face area implied by control C4's fitted constant is about 0.72 m
  squared. The paper does not tabulate it, so it is reported as a by-product and
  is not used for anything.

---

## 3. The controls, and their recovery errors

Without a control the digitization has no established accuracy and cannot arm a
gate. Three quantities the paper states in its own text were digitized back out
of three different figures; four further controls test the pipeline against
itself and against the paper's own arithmetic. All seven run every time the
extraction command runs.

| Id | Control | Paper's stated value and where | Recovered by digitization | **Recovery error** |
| --- | --- | --- | --- | --- |
| **C1** | Figure 6 experimental error-bar half-width | **plus or minus 1 deg C**, Raritan DPX2-T1H1 accuracy, Section 3.5 p. 7 | 1.000000 deg C over all 15 error bars, spread exactly zero | **1.3e-7 deg C** |
| **C2** | Figure 3b GCI band maximum half-width | **0.0521 m/s**, "the maximum discretization uncertainty", Section 4.1 p. 7 | 0.052073 m/s, at height 2.083 m | **2.7e-5 m/s (0.05 %)** |
| **C3** | Figure 7 height-axis upper limit | **3.150 m** room height, Section 3.1 p. 3 | 3.149997 m, identical on all five panels | **2.9e-6 m** |
| **C4** | Eq. (9) with Table 2: T_back = mean(T_front) + q/(m_dot c_p), so (dT)(v)/q is one constant across racks | Eq. (9) p. 5, Table 2 p. 6, both tabulated | 1.147581e-3 plus or minus 2.3e-6, maximum deviation 0.202 % over the 8 full racks | **0.029 K** on a 13 K rise |
| **C5** | Figure 3a "Fine grid" curve against Figure 7a's RSM curve, the same L1 profile plotted twice on axes with different limits (1.2 against 1.6 m/s full scale) | identity | 500 vertices, maximum 1.2e-5 m/s, rms 4.9e-6 | **1.2e-5 m/s** |
| **C6** | The L1 and L2 experimental points plotted in both Figure 7a,b and Figure 8a,b | identity | 6 common points; velocity maximum 0.0060 m/s, rms 0.0037; height maximum 0.0043 m | **0.0060 m/s, 0.0043 m** |
| **C7** | Figure 6 bar height against the midpoint of its own error-bar caps, two independent encodings of one datum | identity | 15 values | **6.5e-5 deg C** |

**C8, the semantic control, run by hand.** The digitized values must reproduce
the paper's own sentences about its own figures. They do, and the test is
two-sided, because it would fail on a series mix-up or a calibration offset:

| Paper's sentence, Section 4.3 p. 10 | What the digitized values give |
| --- | --- |
| "All the values predicted by the CFD model are within the experimental error bars" (front side) | **8 of 8**. Largest deviation 0.445 K at R7, against the 1 K bars |
| "In this case, all values except for two are within the experimental error bars" (back side) | **Exactly two outside: R2 at 1.625 K and R3 at 2.683 K.** The other five are inside |

**Verdict on the controls.** The digitization is **CONTROLLED**. It is not filed
digitized-uncontrolled, and it does not need to be: the paper offered three
text-stated cross-check values and one tabulated relation, and all four were
recovered.

---

## 4. The digitized reference values

**Every value in this section is DIGITIZED, with its figure number. None is
tabulated in the paper.** Values are quoted at the adopted increment, per L-28:
a value must not be quoted finer than the instrument that read it. The machine
copies carry more decimals only so the files round-trip, and their headers
restate the increments.

Machine copies, written by the command in §9:

- `reference-data/wibron_2018_digitized/fig6_rack_temperatures.dat`
- `reference-data/wibron_2018_digitized/fig7_velocity_profiles.dat`

### 4.1 Rack temperatures at the sensor point, 1.09 m above the lower edge of the rack doors

| Rack | T_exp front, **Fig 6a digitized** (deg C) | T_CFD front, **Fig 6a digitized** (deg C) | T_exp back, **Fig 6b digitized** (deg C) | T_CFD back, **Fig 6b digitized** (deg C) |
| --- | --- | --- | --- | --- |
| R1 | 20.15 | 20.00 | **NO DATUM** | 34.87 |
| R2 | 20.22 | 19.90 | 34.49 | 32.87 |
| R3 | 20.13 | 19.70 | 34.98 | 32.30 |
| R4 | 20.08 | 19.71 | 33.70 | 32.82 |
| R5 | **NO DATUM** | 19.70 | **NO DATUM** | 19.85 |
| R6 | **NO DATUM** | 19.83 | **NO DATUM** | 33.90 |
| R7 | 20.25 | 19.80 | 35.97 | 35.49 |
| R8 | 20.10 | 19.80 | 34.31 | 33.86 |
| R9 | 20.07 | 19.87 | 35.14 | 34.43 |
| R10 | 20.12 | 19.90 | 34.84 | 35.20 |

All values plus or minus 0.03 K digitization, on top of the paper's stated
plus or minus 1 K sensor accuracy for the experimental columns.

**NO DATUM is a finding, not a gap in this extraction.** The paper plots an
experimental bar of height exactly zero, with a zero-length error bar, for R5 and
R6 on the front side and for R1, R5 and R6 on the back side. R5 is the empty rack
and R6 holds six servers of eighteen, so the absence is physically plausible, but
the paper does not remark on it anywhere in its text. **The consequence for this
gate is direct: the rack-front temperature row can be armed for 8 racks, not 10,
and `K2c_RACK_ROW_VALIDATION_SEARCH.md` §3.1's "per rack" wording was written
before this was known.**

### 4.2 Measured velocity profiles

| Location | Height, **Fig 7 digitized** (m) | Velocity, **Fig 7 digitized** (m/s) | Row status |
| --- | --- | --- | --- |
| L1 | 0.506 | 0.480 | REPORT-ONLY |
| L1 | 0.998 | 0.703 | REPORT-ONLY |
| L1 | 1.504 | 0.911 | REPORT-ONLY |
| L2 | 0.506 | 0.501 | REPORT-ONLY |
| L2 | 0.998 | 0.668 | REPORT-ONLY |
| L2 | 1.504 | 0.960 | REPORT-ONLY |
| **L3** | **0.506** | **0.487** | **ARMED** |
| **L3** | **0.998** | **0.570** | **ARMED** |
| **L3** | **1.504** | **0.668** | **ARMED** |
| L4 | 0.506 | 0.252 | REPORT-ONLY |
| L4 | 0.998 | 0.266 | REPORT-ONLY |
| L4 | 1.504 | 0.140 | REPORT-ONLY |
| L4 | 1.996 | 0.182 | REPORT-ONLY |
| **L5** | **0.506** | **0.466** | **ARMED** |
| **L5** | **0.998** | **0.522** | **ARMED** |
| **L5** | **1.504** | **0.550** | **ARMED** |
| **L5** | **1.996** | **0.146** | **ARMED** |

Heights plus or minus 0.005 m, velocities plus or minus 0.007 m/s, digitization
only. Every reading falls inside 0.05 to 1 m/s, the range the Dantec 54T33's
stated plus or minus 2 % plus or minus 0.02 m/s accuracy covers, so no reading
needs the coarser above-1 m/s figure.

---

## 5. The armed gate rows, with their bands

The band on every armed row combines the paper's own stated instrument accuracy
with the digitization increment of §2.2. Neither term was dropped. The
combination is additive, not root-sum-square, because that is the form
`K2c_RACK_ROW_VALIDATION_SEARCH.md` §3.1 already prescribed
("within plus or minus (1.0 K + digitization increment)") and because an
additive floor is the conservative reading of L-28's rule.

### 5.1 Row 1, rack-front temperature. ARMED, 8 of 10 racks

| Rack | Reference, **Fig 6a digitized** (deg C) | Sensor accuracy | Digitization | **Pass band on T_front at the sensor point** |
| --- | --- | --- | --- | --- |
| R1 | 20.15 | plus or minus 1.00 K | plus or minus 0.03 K | **plus or minus 1.03 K** |
| R2 | 20.22 | plus or minus 1.00 K | plus or minus 0.03 K | **plus or minus 1.03 K** |
| R3 | 20.13 | plus or minus 1.00 K | plus or minus 0.03 K | **plus or minus 1.03 K** |
| R4 | 20.08 | plus or minus 1.00 K | plus or minus 0.03 K | **plus or minus 1.03 K** |
| R5 | NO DATUM | | | **NOT ARMABLE. No experimental value exists in Fig 6a** |
| R6 | NO DATUM | | | **NOT ARMABLE. No experimental value exists in Fig 6a** |
| R7 | 20.25 | plus or minus 1.00 K | plus or minus 0.03 K | **plus or minus 1.03 K** |
| R8 | 20.10 | plus or minus 1.00 K | plus or minus 0.03 K | **plus or minus 1.03 K** |
| R9 | 20.07 | plus or minus 1.00 K | plus or minus 0.03 K | **plus or minus 1.03 K** |
| R10 | 20.12 | plus or minus 1.00 K | plus or minus 0.03 K | **plus or minus 1.03 K** |

### 5.2 Row 3, velocity profiles at L3 and L5. ARMED, 7 points

Band per point, following the row's existing rule: the larger of 15 % of the
local reading, or the additive floor of instrument accuracy plus the paper's
0.0521 m/s fine-grid GCI plus the 0.007 m/s digitization increment. The GCI term
is the paper's own **text-stated** 0.0521, not this addendum's digitized
0.052073; C2 is the control that established the reading, not a replacement for
the stated number.

| Location | Height, digitized (m) | Reference, **Fig 7 digitized** (m/s) | 15 % of reading | Additive floor (instr + GCI + digit) | **Pass half-band (m/s)** | Which term binds |
| --- | --- | --- | --- | --- | --- | --- |
| L3 | 0.506 | 0.487 | 0.073 | 0.0297 + 0.0521 + 0.007 = 0.089 | **plus or minus 0.089** | floor |
| L3 | 0.998 | 0.570 | 0.086 | 0.0314 + 0.0521 + 0.007 = 0.090 | **plus or minus 0.090** | floor |
| L3 | 1.504 | 0.668 | 0.100 | 0.0334 + 0.0521 + 0.007 = 0.093 | **plus or minus 0.100** | 15 % |
| L5 | 0.506 | 0.466 | 0.070 | 0.0293 + 0.0521 + 0.007 = 0.088 | **plus or minus 0.088** | floor |
| L5 | 0.998 | 0.522 | 0.078 | 0.0304 + 0.0521 + 0.007 = 0.089 | **plus or minus 0.089** | floor |
| L5 | 1.504 | 0.550 | 0.082 | 0.0310 + 0.0521 + 0.007 = 0.090 | **plus or minus 0.090** | floor |
| L5 | 1.996 | 0.146 | 0.022 | 0.0229 + 0.0521 + 0.007 = 0.082 | **plus or minus 0.082** | floor |

The digitization increment is 8 % of the smallest band and never binds it. That
is worth saying plainly: the band is set by the paper's instrument and its own
discretization uncertainty, and this addendum's contribution to it is small but
is **carried, not dropped**.

**Height tolerance is part of the row.** Each comparison is made at the digitized
height plus or minus 0.005 m. On these profiles' local gradients that is worth
under 0.003 m/s and does not change any band above, but a solve that samples at a
different height must say which height it sampled.

### 5.3 What stays REPORT-ONLY, and why

| Row | Digitized here? | Status | The primary's own reason |
| --- | --- | --- | --- |
| Rack-back temperature, per rack (Fig 6b) | Yes, 7 racks with data, values in §4.1 | **REPORT-ONLY** | The authors document 2 of 7 outside their own error bars and attribute the misses to the uniform-outlet-temperature simplification against real non-uniformity (p. 10, p. 13). Grading a solve where the abstraction is known approximate would grade the abstraction. **The digitized values here confirm the authors' own count exactly**, which is C8, and that is the strongest argument for leaving the row ungraded |
| Velocity at L1, L2, L4 (Fig 7a, 7b, 7d) | Yes, values in §4.2 | **REPORT-ONLY with the mandatory position-sensitivity sweep of plus or minus 0.15 m** | The primary's own comparison fails at face value at L1 and L2 and recovers only 10 to 15 cm toward the hot-aisle centre (their Fig. 8), attributed to gaps behind the rack doors. L4 sits outside the containment door where the paper reports model spread rather than agreement |
| Above-rack low-velocity region (Fig 9) | **No** | **REPORT: present / absent** | Figure 9 is a raster contour plane. There is no vector geometry to extract and the row was never quantitative. Nothing in this addendum changes it |
| Heat-balance closure, advective | Not applicable | **BLOCKED** | KV1 is open. See §7 |
| R5 and R6 front temperature; R1, R5, R6 back temperature | Extraction ran; the paper plots no experimental value | **NOT ARMABLE** | New, from §4.1. These are not REPORT-ONLY by judgement, they are unarmable by absence of a reference |

**Do not arm a row the paper's own authors would not stand behind.** Every
REPORT-ONLY row above is REPORT-ONLY because the authors said so in their own
text, and the digitized values reproduce the sentence in which they said it.

---

## 6. Two findings the digitization surfaced

### 6.1 The experimental series has five missing values and the paper does not say so

Recorded in §4.1. Filed as a docket item.

### 6.2 R6's plotted back-side CFD temperature does not satisfy the paper's own Eq. (9)

Control C4 fitted the constant 1/(rho A c_p) = 1.147581e-3 K m /(W s) over the
eight full racks, to 0.202 % maximum deviation. Applied as a **prediction** to the
two partial racks:

| Rack | q, Table 2 (W) | v, Table 2 (m/s) | Eq. (9) predicts dT (K) | Fig 6b minus Fig 6a gives dT (K) | Residual (K) |
| --- | --- | --- | --- | --- | --- |
| R5 | 0 | 0.26 | 0.000 | 0.152 | **+0.152** |
| R6 | 1762 | 0.41 | 4.932 | 14.071 | **+9.139** |

R5's 0.152 K is explained and is not a defect: §3.3 states the back temperature
was built on the **average** front-face temperature, while Figure 6a plots the
value at the **sensor point**, so the difference of the two figures carries that
offset as well as dT. That offset is of order 0.15 K and is one reason C4's
residual, at 0.029 K, was adopted as the temperature increment rather than C7's
6.5e-5.

**R6's 9.139 K is not explained by that.** Reading it backwards, the plotted rise
corresponds to a heat load near 5030 W at R6's tabulated flow, close to a full
rack rather than the tabulated 1762 W of six servers. This addendum does not
claim to know which of the three possibilities is true (the simulation applied a
different load than Table 2 records; Table 2's R6 entry is a misprint; the
Figure 6b bar is misplotted), and it cannot: the underlying data is not
published. **What it does do is refuse to put R6 in any armed row, and record the
inconsistency so a later solve that reproduces Table 2 faithfully and then
disagrees with Figure 6b at R6 is not read as the solve's failure.** R6's
rack-back row was already REPORT-ONLY and R6 has no experimental value on either
face, so nothing downstream changes; the finding is recorded because it is a
property of the reference, and a reference's defects belong in the record next
to the reference.

---

## 7. KV1, the prerequisite checked while here

**Verdict: the UNVALIDATED stamp on `scripts/heat_balance.py`'s advective path is
still accurate at `fc1e3bac`, KV1 is open and unattempted, and the true state is
one step worse than K2a §8 describes.**

Verified rather than recalled: the worktree copy of `scripts/heat_balance.py` is
byte-identical to the HEAD blob at `fc1e3bac`.

| What K2a §8 states | What the file at `fc1e3bac` does | Verdict |
| --- | --- | --- |
| The docstring stamps the advective path UNVALIDATED | Present, lines 143 and 149 | **Accurate** |
| The script REFUSES non-wall patches unless `--allow-advective` | Present, line 551, `return 2` | **Accurate** |
| `--allow-advective` "adds the term but the report is then stamped UNVALIDATED" | **Neither half holds.** The only per-patch heat computed anywhere is `Q = kcond * G` at line 633, pure conduction; `rho cp integral T (U.n) dA` appears nowhere outside prose. `a.allow_advective` is read at exactly one place, line 551, the refusal guard. It sets no key in the `res` dict at lines 728 to 748 and prints no line in `emit()` | **Aspirational, not implemented** |
| Every advective closure number is reported UNVALIDATED in the script's own words | A run with `--allow-advective` produces a report and a JSON with **no UNVALIDATED marking at all**. Worse, `sealed = not nonwall` at line 708 is then False, so `closure_is_identity_class` is False and `emit()` prints "NOT of the identity class, so the balance is a genuine constraint here rather than a restatement of the discretisation" over a ledger whose advective term was never computed | **Not enforced.** The stamp is doc-only, and the printed report actively vouches for the number |

No KV1 case, run tree, JSON or docket row exists anywhere in the repository. The
only occurrences of the string are five forward-looking lines in the K2a spec and
one gate row in the K2c search. No test in `scripts/` or `sdk/tests/` exercises
the advective path; the file's only self-calibration, `--selftest-conduction`, is
explicitly the laminar wall path.

**Proposal, written and stopped as instructed. No solve was launched.**

| KV1, as it should be run | Value |
| --- | --- |
| Case | Straight duct, one inlet, one outlet, adiabatic walls, imposed m_dot and inlet T, plus a planted volumetric source of known watts through `fvOptions`, so the audited net must recover the plant |
| Why open rather than sealed | On a sealed case the balance is an identity by construction, which is the thing K1c already established and which W-2 forbids gating on. The advective enthalpy flux is the only genuinely independent contribution and it exists only with through-flow |
| Pass criterion | `heat_balance_source_recovery_tol_pct`, 0.1 %, the same constant K1c's sealed planted-source control used, already in `docs/physics_rules.yaml` |
| **Code that must be written first** | **The advective term itself.** KV1 cannot be run against HEAD's script because HEAD's script does not compute the quantity KV1 would validate. `--allow-advective` currently only silences the refusal |
| Second code change | Stamp the report. `res["advective_unvalidated"]` and a line in `emit()`, and suppress the "genuine constraint here" sentence while the term is unvalidated |
| Compute | One coarse laminar duct, in the K2b control budget's KV1 line item. Not requested here |

**Consequence for this addendum: none, and that is deliberate.** The
heat-balance row of `K2c_RACK_ROW_VALIDATION_SEARCH.md` §3.1 is explicitly
necessary-not-sufficient and is never cited as validation evidence, so KV1 does
not gate the VALIDATED verdict of §8. It does gate quoting any K2b closure
figure, which is a separate and still-closed door.

---

## 8. Is K2c-A now eligible for VALIDATED?

**No, and the reason is not this addendum.**

The lab's tier is earned against a published experiment with the result inside
its band. Two things are needed and only one of them is now in place:

| Requirement for a VALIDATED grade on K2c-A | State at `fc1e3bac` |
| --- | --- |
| A published experimental reference, with a quantified band | **Done by this addendum.** Reference values digitized, controlled by seven controls, labelled, and banded with the instrument accuracy and the digitization increment both carried |
| A solve of the case, landing inside that band | **Not done. No solve has run, and none is authorized.** The rung's header still requires owner approval of the K2a specification and a compute authorization |

So the accurate statement of the change is narrower than "the rung is armed":

> **As of this addendum, K2c-A's reference column is armed and controlled on two
> rows. The rung is VALIDATED-ELIGIBLE on those two rows and on nothing else. It
> is not VALIDATED, and cannot become VALIDATED until a solve runs and is
> graded.** Until then the rung's tier is unchanged.

**Exactly what remains, in order:**

1. Owner approval of the K2a specification and a compute authorization scoped to
   K2b. Nothing may run before this.
2. The solve itself. The primary is direct evidence this is not routine: its own
   authors could not converge a steady solve of this module class and used 600 s
   of transient averaging.
3. Grading against §5's rows. **8 racks, not 10**, on the temperature row, and 7
   points on the velocity row.
4. The turbulence-model caveat, unchanged and still on the rung's face: K2a's
   default is k-omega SST, which this primary did not test. A graded SST solve is
   a **new model-form result**, not a reproduction, and may not borrow the
   primary's "within error bars" as an expectation. It can still earn VALIDATED,
   because the tier is about the experiment and the band, not about matching
   another code's model.
5. KV1 before any closure figure from that solve is quoted. §7.
6. **K2c-B remains NOT OBTAINED and no amount of this reaches it.** No
   raised-floor gate rows exist, and a tile-supply solve stays TREND-ONLY however
   well it converges.

**An honest "still TREND-ONLY, and here is why" was the alternative and it was
close.** What tipped it is that the blocker K2c named was specifically the
unarmed reference column, that column is now armed against a controlled reading,
and the controls were strong enough that the digitization is not the weakest link
in any band. What it is not is a grade, and nothing here should be read as one.

---

## 9. Re-deriving every figure in this document

Every number above comes out of one command and nowhere else:

```
python3 docs/campaigns/F14-cooling-ladder/digitize_wibron2018.py
python3 docs/campaigns/F14-cooling-ladder/digitize_wibron2018.py --write
```

Run from the repository root. The command re-verifies the source PDF's SHA-256
before reading a single path and exits 2 on a mismatch. Without `--write` it only
prints; with it, it refreshes the two `.dat` files under
`reference-data/wibron_2018_digitized/`.

The KV1 findings of §7 were re-derived with:

```
git show HEAD:scripts/heat_balance.py > /tmp/hb_head.py
diff -q /tmp/hb_head.py scripts/heat_balance.py
grep -n "UNVALIDATED\|allow_advective\|Q = kcond" /tmp/hb_head.py
git log --oneline -- scripts/heat_balance.py
```

The vector-versus-raster classification of §1.1 was re-derived with
`pdfimages -list docs/papers/wibron_ljung_lundstrom_2018_en11030644.pdf` and with
pypdf's `/Subtype` on the page resources.

## 10. Claim, source, domain rows (charter section 3 format)

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| The rack-front temperatures measured on a real 10-rack hard-floor module were 20.07 to 20.25 deg C at the 1.09 m sensor point on the 8 racks that carry a sensor | **DIGITIZED from Wibron 2018 Fig 6a**, primary READ IN FULL, controlled by C1, C4, C7, C8 | Arming K2c-A's rack-front row at plus or minus 1.03 K | R5 and R6, which have no experimental value; any other facility; any other sensor height |
| The measured velocities at L3 and L5 were 0.487, 0.570, 0.668 and 0.466, 0.522, 0.550, 0.146 m/s at 0.506, 0.998, 1.504 and 1.996 m | **DIGITIZED from Wibron 2018 Fig 7c, 7e**, controlled by C2, C3, C5, C6 | Arming K2c-A's velocity row with the bands of §5.2 | L1, L2, L4, which stay REPORT-ONLY on the primary's own evidence |
| A digitization of vector figure geometry, controlled against three text-stated values from the same paper, carries a reading uncertainty of 0.03 K and 0.007 m/s on this primary | VERIFIED, this addendum's own controls C1 to C7 at `fc1e3bac` | Any band built on these reference values | Any raster figure, any other paper, and the separate question of whether plotted equals measured, which no control here touches |
| Figure 6 plots no experimental value for R5 and R6 (front) or R1, R5 and R6 (back) | **DIGITIZED from Wibron 2018 Fig 6a, 6b**; the paper's text does not remark on it | Scoping the rack-front row to 8 racks | Any claim about why the sensors are missing, which is not in the paper |
| The advective path of `scripts/heat_balance.py` was UNVALIDATED and unimplemented at `fc1e3bac`, and `--allow-advective` neither computed the term nor stamped the report | VERIFIED by reading the HEAD blob, this session | KV1's scope, and any quotation of a K2b closure number | The sealed conduction path, which K1c validated and which is unaffected |
