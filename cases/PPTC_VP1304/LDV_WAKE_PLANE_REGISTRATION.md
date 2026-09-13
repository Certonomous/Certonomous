# PPTC VP1304 — LDV wake planes: REGISTERED BEFORE ANY EXTRACTION

Sanaa's §8, byte-exact: *"Wake: axial and tangential velocity in the planes of Report 3754
(**read the exact plane positions and radii from that report; register them before
extracting**), compared with the LDV data at the J closest to the LDV condition."*

**This is that registration, and it precedes any extraction.** At the commit that introduces
this file no field exists for this act: `verification/runs/PPTC_VP1304/` is not on disk, no
mesh has been built and no solver has run. Planes chosen before a field exists cannot be chosen
to suit one.

**Source:** `docs/papers/propeller_rotating_machinery/mach_2011_sva_report_3754_pptc_ldv_velocity_measurements.pdf`,
sha256 `71da14db7198e065fe32f62f8d43b2671ce0716a420640fd1b9e57f9d6e69f23`, 12 018 877 bytes.
Title page: *"Potsdam Propeller Test Case (PPTC) / LDV Velocity Measurements with the Model
Propeller VP1304 / Report 3754 / Potsdam, April 2011"*; page 1.1 *"Author Dipl.-Ing.
K.-P. Mach"*. Every number below carries its page.

---

## 1. ⚠ THIS IS A DIFFERENT EXPERIMENT FROM THE OPEN-WATER ACT — FOUR MATERIAL DIFFERENCES

The open-water gate (§3) is the towing tank. **The LDV data are not.** Registered up front
because every one of these changes what a CFD comparison would have to reproduce.

| | open-water act (Report 3752) | LDV (Report 3754) | page |
|---|---|---|---|
| facility | towing tank, 9.0 m × 4.5 m | **cavitation tunnel K15A, small section 0.600 × 0.600 m with rounded edges** | 1.5, 2.1 |
| **blockage** | free field | **disc 0.049087 m² / section 0.3600 m² = 13.64 %** | derived |
| **rig configuration** | dynamometer H39 **behind** the propeller — PULL, shaft downstream | **dynamometer J25 IN FRONT of the propeller — PUSH, SHAFT UPSTREAM** | 1.5 |
| rotation rate | n = 15 s⁻¹ | **n = 23 s⁻¹** | 1.7 |
| advance ratio | six registered points | **J = 1.253**, not one of them | 1.7 |
| Reynolds number | 0.870e6 at the design point | **1.3487e6 — 1.55× higher** | derived, 3752 annex definition |

**The reversed rig is the heaviest of these.** Our registered geometry (§2.2 b, amendment 1)
puts the cap upstream and the shaft downstream, because that is the open-water arrangement.
**The LDV tests had the shaft upstream of the propeller and the dynamometer body ahead of it.**
A wake comparison against this data therefore compares our open-water geometry against a
measurement taken on a *different body*, in a *confined* section, at a *different Reynolds
number*. **This is disclosed as a comparison, not claimed as a validation of our geometry.**

### 1.1 One corroboration that survives all of it

Report 3754's working point (page 1.7): VA = 7.204 m/s, n = 23 s⁻¹, J = 1.253, KT = 0.250,
10KQ = 0.725. Self-consistent: VA/(nD) = 1.2529 against the tabulated 1.253.

Report 3752 page 2.11 linearly interpolated to J = 1.253 gives **KT 0.2514, 10KQ 0.7132**.
The tunnel measured **0.250 and 0.725** — **−0.57 % and +1.66 %.**

**Two facilities, two rig configurations, two Reynolds numbers, agreeing on loading to under
2 %.** The tunnel coefficients are Glauert-corrected for test-section influence (annex A2.1),
which is what makes this comparison legitimate, and the agreement is a genuine cross-check
between the two reports this act depends on.

---

## 2. THE PLANES — Report 3754 Table 3, page 1.7, transcribed exactly

Seven planes, "with respect to the propeller plane" (page 1.4):

| x/D | x (mm), Report 3754 | **x (mm), OUR axis** | position |
|---|---|---|---|
| **−0.200** | −50.0 | **+50.0** | in front of the propeller |
| **0.094** | 23.5 | **−23.5** | behind |
| **0.100** | 25.0 | **−25.0** | behind |
| **0.110** | 27.5 | **−27.5** | behind |
| **0.130** | 32.5 | **−32.5** | behind |
| **0.160** | 40.0 | **−40.0** | behind |
| **0.200** | 50.0 | **−50.0** | behind |

### 2.1 THE COORDINATE TRANSFORMATION, WITH ITS NUMBER — not "the planes are downstream"

Report 3754 places "in front of the propeller" at **x = −50.0 mm** and "behind the propeller"
at **x = +23.5 … +50.0 mm**, so **in its convention POSITIVE x is DOWNSTREAM**.

Our CAD is in SVA's ship coordinate system with the nose cap at **+x** and the shaft at **−x**,
so **in our convention POSITIVE x is UPSTREAM** (`GEOMETRY_ADMISSION_RECORD.md` §2).

> **REGISTERED TRANSFORMATION:  x_ours = − x_3754  (millimetres, origin at the propeller
> reference plane).**  Radius and the tangential sense are unchanged.

**Corroborated by where the planes land, not asserted.** Under this mapping the first "behind"
plane, x/D = 0.094, sits at x_ours = **−23.5 mm**, and the blades' aft extent is
**−24.6 mm** — the plane is **1.1 mm clear of the blade trailing edge**. That is precisely why
SVA chose the odd value 0.094 rather than a round number: **it is the first plane that clears
the blades.** The upstream plane maps to +50.0 mm, ahead of the blades and inside the cap
region (the cap spans +25.0 to +133.69 mm). A sign error or an origin offset would not produce
either result.

**Stated limitation:** the coincidence of the two origins at the propeller reference plane is
**inferred from this geometric agreement**, not stated numerically in either report. If the
extraction ever disagrees with the data by a constant axial offset, this is the first thing to
re-examine.

---

## 3. THE RADII — Report 3754 Table 4, page 1.7, transcribed exactly

| plane | r/R from | r/R to | step r/R | step (mm) |
|---|---|---|---|---|
| **in front, x/D = −0.20** | 0.40 | 1.10 | 0.050 | 6.250 |
| **behind** (0.094, 0.10, 0.11, 0.13, 0.16, 0.20) | 0.40 | 0.70 | 0.050 | 6.250 |
| | 0.70 | 0.90 | 0.025 | 3.125 |
| | 0.90 | 0.95 | 0.010 | 1.250 |
| | **0.95** | **1.05** | **0.002** | **0.250** |
| | 1.05 | 1.10 | 0.025 | 3.125 |

**The 0.002 step through r/R = 0.95 → 1.05 is the tip-vortex band** and is 25× finer than the
inboard sampling. R = 0.125 m, so r/R = 1.0 is r = 125.0 mm and the band spans
r = 118.75 → 131.25 mm at 0.250 mm intervals.

### 3.1 The measurement line — angular, and it is a LINE not a plane

Page 1.7: *"The LDV measurements had been carried out along a line at the rotation angle
225 degrees."* **The data are a radial traverse at one blade-phase angle, not an area survey.**
The extraction must sample the same line, and the 225° convention is Report 3754's annex A3.1
cylindrical propeller coordinate system, looking on the pressure side.

### 3.2 Instrument resolution, for context

Measuring volume 65 µm diameter × 0.9 mm length, **L/D = 0.0036**; minimum radial point spacing
Δr/R = 0.002, so the measuring volumes **partly overlap**; rotation angle resolved in 0.25°
steps into 1440 angle classes; 90 s or 40 000 samples per component, ≈2070 propeller rotations
(pages 1.6, 1.7).

---

## 4. THE BAND — AND ITS ABSENCE, REGISTERED EXPLICITLY

Sanaa's §8: *"Measured-tier gate, band from the report's stated repeatability if given, else
disclosed as a comparison."*

> **REPORT 3754 STATES NO MEASUREMENT UNCERTAINTY AND NO REPEATABILITY FOR THE VELOCITIES.**

The whole report was searched for uncertainty, accuracy, repeatability, tolerance, error and
confidence statements. What it contains is **standard deviations used to compute the turbulence
degree** within each angle class (annex A2.2, equations 2 and 7) — a *measured physical
quantity*, the flow's unsteadiness, **not an instrument uncertainty**. Treating Tu as an error
bar would convert turbulence into tolerance and make a noisy region look permissive.

**Consequence, per her own wording: the wake comparison is DISCLOSED AS A COMPARISON, not
gated.** No band is invented, and **this absence is registered here so that nobody later
supplies one from memory** — the same discipline applied to the absent shaft dimension
(pre-registration amendment 1, §A1.1).

Available and registered as context rather than tolerance: the turbulence-degree fields for the
axial, tangential and radial components across x/D = 0.094–0.20 (pages 3.25, 3.26, 3.27).

---

## 5. NORMALISATION — a registered ambiguity

Page 1.4: *"All measured values were made dimensionless using the inflow velocity."*

Annex A2.1 records that the **coefficients** were corrected for test-section influence by
**Glauert's method**, and gives both the raw and corrected forms (J and J_c, V and V_c).
**Table 2 does not say whether its VA = 7.204 m/s is the corrected or the uncorrected inflow
speed**, and Glauert corrects the coefficients rather than the local velocity field.

> **REGISTERED: the comparison is made in the report's own normalisation, V/VA with
> VA = 7.204 m/s as tabulated, and the ambiguity is disclosed on the certificate.** If the
> corrected and uncorrected inflow differ materially it shifts every normalised velocity by a
> common factor, which is a systematic offset and not a shape change — so the comparison of
> *profile shape*, and the tip-vortex position in r/R, are robust to it while absolute levels
> are not. Shape and position are what the comparison claims.

---

## 6. WHICH J — registered

Our six registered advance ratios do not include 1.253. Nearest is **J = 1.2021**
(Δ = 0.051) against 1.3308 (Δ = 0.078).

> **REGISTERED: the wake comparison uses our J = 1.2021 solve — which is also the design point
> and the family's headline condition — against Report 3754's J = 1.253 data, with the 4.2 %
> advance-ratio mismatch disclosed beside every figure.** No interpolation between our solves is
> performed, and no solve is added at J = 1.253, because §7's run plan does not register one.

---

## 7. What is extracted

At each of the seven planes, on the 225° radial line, over the registered radii: **axial and
tangential velocity**, normalised by VA. The extraction reads the registered plane list from
this file; it does not choose planes.
