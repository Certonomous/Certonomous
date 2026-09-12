# PPTC VP1304 — geometry admission record

Companion to the frozen pre-registration
`cases/PPTC_VP1304/PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md`, committed at
**`09396b48990da3ce8e91714cd1a35f3fbc07e4de`**. This file carries **measurements**; the
pre-registration carries the frozen gates, thresholds and outcome rules. Nothing here
alters anything frozen there.

Admitted file: `case2-1_open_water_test_geometry/closed hub fillets/case2-1_PPTC_geo_no_gap.stp`,
sha256 `d08aaf690b22e5f418f8a20473d502046f815ce8b3fc67378fd36f6d55543d2d`.
No solver has run for this act; `verification/runs/PPTC_VP1304/` does not exist.

---

## 1. Healing-invariance check — **PASS on all five invariants**

The check and its five thresholds were registered in pre-registration §2.5 and frozen in
commit `09396b48` at 22:37:16Z, **before this check was run**. The unhealed and healed
geometries were tessellated with identical settings (uniform 0.8 mm, curvature refinement
off); the only difference is OpenCASCADE healing (`OCCFixDegenerated`, `OCCFixSmallEdges`,
`OCCFixSmallFaces`, `OCCSewFaces`, tolerance 1e-4).

| invariant | unhealed | healed | change | registered threshold | verdict |
|---|---|---|---|---|---|
| enclosed volume | 1 174 942.0297 mm³ | 1 174 948.4365 mm³ | **+0.0005%** | ≤ 0.10% | **PASS** |
| bbox x extent | 489.6900 mm | 489.6900 mm | **+0.0000 mm** | ≤ 0.10 mm | **PASS** |
| bbox y extent | 244.6934 mm | 244.6934 mm | **+0.0000 mm** | ≤ 0.10 mm | **PASS** |
| bbox z extent | 245.3690 mm | 245.3706 mm | **+0.0016 mm** | ≤ 0.10 mm | **PASS** |
| max radius | 124.9905 mm | 124.9905 mm | **+0.0000 mm** | ≤ 0.05 mm | **PASS** |
| mean chord at r/R = 0.7 | 104.3028 mm | 104.2788 mm | **−0.0230%** | ≤ 0.5% | **PASS** |
| **root-band area, r ∈ [35, 40] mm** | 14 719.8996 mm² | 14 722.1046 mm² | **+0.0150%** | ≤ 2.0% | **PASS** |

Five blades resolved in both. Total surface area changes by +0.0123% (163 525.827 →
163 545.982 mm²); triangle count 645 012 → 651 282.

**The root-band area — the quantity that would have moved if healing had touched the closed
root — changes by 0.0150% against a 2.0% threshold, a margin of 130×.** Healing does not
move the root.

**Consequence, per the registered outcome rule of §2.5:** the registered modelling state
survives its own preparation. **The root closure remains SVA's and does not become the
lab's.** Modelling choice (a) stands as registered, and the certificate carries this in one
line.

---

## 2. Orientation and axis — established from the CAD

The shaft axis is **x**. The nose cap occupies **x = +25.0 to +133.69 mm** and the
dynamometer shaft runs to **x = −356.0 mm**. Since the cap is upstream in the test
arrangement (pull configuration, dynamometer H39 behind the propeller — Report 3752 §5, and
"Propeller shaft downstream" in all eleven of the report's test-table headers), **the
freestream runs from +x toward −x**: inlet at +x, outlet at −x. The CAD is therefore in
SVA's ship coordinate system (SCS, x pointing upstream), consistent with the smp'11 geometry
sheet's statement that the SCS is the system employed for the open water tests.

Registered import scale **1e-3 exactly** (mm → m), confirmed in pre-registration §2.3 by
max radius 124.9905 mm against R = 125.000 mm.

*Recorded discrepancy, not load-bearing:* Report 3752 annex A1 says of the dynamometer
"The configuration is with the shaft in upstream direction", which reads against §5 and the
eleven table headers. The table headers and §5 are taken as authoritative and agree with
Sanaa's registered arrangement; the annex sentence is disclosed here and used for nothing.

---

## 3. Axial profile of the admitted body, measured

Maximum and minimum radius by axial station, from the 0.8 mm tessellation:

| x range (mm) | r_min (mm) | r_max (mm) | feature |
|---|---|---|---|
| −356.0 … −355.9 | 0.146 | 20.000 | shaft end cap (closed) |
| −355.9 … −200 | 20.000 | 20.000 | **dynamometer shaft, r = 20.000 mm exactly** |
| −200 … −100 | 20.000 | 26.132 | aft fairing, expanding |
| −100 … −50 | 26.133 | 32.955 | aft fairing, expanding |
| −50 … +20 | 36.84 | 124.99 | **hub with the five blades** |
| +20 … +25.5 | 36.16 | 116.86 | hub / cap junction |
| +25.5 … +133.69 | 0.000 | 112.82 | **nose cap**, tapering to a point |

### 3.1 A fourth, independent confirmation of the hub diameter

At x = −10 mm and x = +10 mm the hub surface measures **r = 37.600 mm**, i.e.
**dh = 75.20 mm ≈ 0.075 m**. This is now the **fourth** independent confirmation of the
registered hub diameter, and the first taken directly off the CAD surface:

1. Report 3752 Table 1, dh/D = 0.300;
2. Report 3752's three dummy-hub pages, `dh [m] 0.075` as an absolute length;
3. SVA's `case2-1_PPTC_hubcap2D.dat` with cap length 108.690 = 1.5 × 72.460 = 1.5 × (2 × 36.230);
4. **the admitted CAD's own hub surface at r = 37.600 mm.**

The smp'11 geometry sheet's "Hub diameter ratio dh/D = 0.1500" would require r = 18.75 mm.
The measured hub surface is **twice** that. The sheet's value is a radius ratio under a
diameter-ratio label, as recorded in pre-registration §2.1, and is used for nothing.

### 3.2 Cap base radius

At x = +24 mm the cap/hub junction measures **r = 36.2300 mm**, reproducing the first row
of SVA's own `case2-1_PPTC_hubcap2D.dat` (`0.0000  36.230`) to five decimal places. The CAD
and the published hub-cap profile are the same body.

---

## 4. ⚠ CONFLICT BETWEEN A REGISTERED MODELLING CHOICE AND THE FIRST-PARTY CAD — **ESCALATED, NOT DECIDED**

**Registered choice (b)**, Sanaa's section 2, byte-exact: *"The hub is modelled with its cap
upstream and the dynamometer shaft downstream as a cylinder of diameter 0.075 m extending to
the outlet, rotating with the propeller."*

**What the CAD she instructed us to use actually contains:** the shaft is a cylinder of
**radius 20.000 mm — diameter 0.040 m**, and it does not meet the hub directly; a tapering
**aft fairing** carries the body from the hub (r ≈ 33 mm) down to the shaft over roughly
150 mm of length. There is no 0.075 m cylinder anywhere aft of the hub.

**0.075 m is exactly dh**, the hub diameter, which is the most likely origin of the figure.

**Why this is not a detail.** The shaft is a wetted, rotating surface inside the control
volume, and it contributes to both T and Q, which are the graded quantities. Replacing a
0.040 m shaft behind a fairing with a bare 0.075 m cylinder nearly doubles the shaft
diameter, deletes the fairing, and changes the base area behind the hub — all of it in the
region the comparator's "corrected with idle torque and gap force" table was constructed to
represent.

**No document states a shaft diameter numerically.** Report 3752 gives the arrangement
("dynamometer H39 arranged behind the propeller model", shaft inclination 0°, photographs
pages 4.2–4.3) but no shaft dimension; neither does the smp'11 setup sheet, which describes
the aft end only qualitatively ("The downstream end of the propeller hub is designed to
avoid a pressure build-up") — a description the CAD's aft fairing matches and a bare 0.075 m
cylinder does not. **The CAD is the only numeric authority on this dimension, and it says
0.040 m.**

**Status: PENDING.** This is a registered geometry parameter in a frozen pre-registration
and it is Sanaa's own wording, so it is **not** changed by this lane. It is raised to the
cfd supervisor for routing. The lane's recommendation, stated as a recommendation:
**model the shaft as the CAD's own 0.040 m cylinder with its aft fairing, extended
downstream at 0.040 m to the outlet**, because (i) the CAD is the first-party source Sanaa
directed us to and the only numeric authority, (ii) the fairing is corroborated by the setup
sheet's description of the aft end, and (iii) adopting 0.075 m would substitute a figure
that matches dh exactly for a dimension the source states differently — the same
diameter-versus-something-else confusion already found and resolved in the smp'11 geometry
sheet.

**Either way the shaft must be extended**, because the CAD stops at x = −356 mm while the
outlet is at 6D = −1500 mm from the propeller plane. Only the diameter of that extension is
in question.

Whatever is decided is recorded on the certificate under the modelling choices, with this
conflict and its resolution stated, and it is registered **before** the mesh is built.

---

## 5. Patches to be tagged

From §3, the four patch groups Sanaa's §5 requires are separable by their measured extent:

| patch | definition from the measured profile |
|---|---|
| `blades` | the five blade surfaces, r from the hub fillet out to 124.99 mm |
| `hub` | the cylindrical body, r ≈ 36.2–37.6 mm, x ≈ −50 … +25 |
| `cap` | the nose cap, x = +25 … +133.69, r tapering 36.23 → 0 |
| `shaft` | the aft fairing plus the shaft, x < −50, plus its registered extension to the outlet |

---

## 6. Instruments

- CAD kernel read and tessellation: gmsh 4.12.1 with the OpenCASCADE factory.
- Metrics: `stl_metrics.py` and `compare_sections.py` (triangle areas; enclosed volume by
  the divergence theorem; sections measured in the unrolled cylindrical surface).
  Both are copied into this case directory beside this record when the mesh script lands,
  so that no repository document cites a scratch path (L-186).
