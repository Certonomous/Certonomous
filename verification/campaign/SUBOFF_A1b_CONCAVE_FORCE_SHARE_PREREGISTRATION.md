# SUBOFF A1b — CONCAVE-CELL FORCE SHARE: PRE-REGISTRATION

**Status: FROZEN AT COMMIT. Thresholds and conclusions written BEFORE any of the three
numbers was computed.** The area share (Q1) is computable from the mesh alone and was
therefore available at the moment this document was written; it was NOT computed first.
That ordering is the entire evidentiary content of this file and it is the reason the
file exists separately from the measurement.

Author: cfd lab-lane. Directed by the cfd-supervisor, 2026-09-12, on his ruling that
**cell share is a proxy and force share is the graded quantity**.

---

## 1. WHY THIS EXISTS

`checkMesh -allGeometry -allTopology` on the SUBOFF A1 L1 mesh failed two checks. One —
a single under-determined cell — is closed by the supervisor's ruling: it sits at
d = 0.2077 m from the wall, twenty-two layer thicknesses out, on the sail tip
trailing-edge corner, and **that corner is the builder's own registered departure**,
named in `cases/navier_class/SUBOFF_A1/build_suboff_a1_geometry.py`'s docstring as "the
only one" with its magnitude written to the manifest. It is a known departure appearing
where it was predicted to appear, not a surprise explained afterwards. Disclosed, not
gating.

The other is not closed. **65,027 concave cells, 1.989 % of 3,268,613**, and the located
population is near-body, not far-field: 99.2 % sit axially alongside the hull, the whole
population tops out at r = 0.8346 m in a domain of radius 2.952 m, and **4,677 of them
lie inside the prism layer** (0 < d <= 0.00943 m) on the graded surface.

4,677 is **0.67 % of the layer cell population** (116,686 hull faces x 6 layers ~= 700 k
cells). That number is a **PROXY AND NOT THE GRADED QUANTITY.** Forces are not
integrated over cells. They are pressure and wall shear integrated over **FACES, WEIGHTED
BY AREA**, and wall shear on a hull carrying a sail is strongly non-uniform. A population
scattered over the hull carries roughly its cell share; a population clustered where the
shear is high carries several times it. Those two cases warrant different verdicts and
the difference is not visible in the cell count.

This lab spent 2026-09-12 learning what a proxy read as the thing itself costs — M6's
skew faces, all at the tip, refuting the mechanism they were cited for. This file is the
refusal to repeat it.

---

## 2. THE THREE QUANTITIES

Let **C** = the set of hull boundary faces whose owner cell is a member of the
`concaveCells` set written by checkMesh to `L1/constant/polyMesh/sets/concaveCells`.

| id | quantity | source | available |
|---|---|---|---|
| **Q1** | `sum(area over C) / sum(area over all hull faces)` | mesh alone | now |
| **Q2** | `sum(\|viscous force\| over C) / sum(\|viscous force\| over all hull faces)` | converged solve | at convergence |
| **Q3** | `sum(\|pressure force\| over C) / sum(\|pressure force\| over all hull faces)` | converged solve | at convergence |

Q2 and Q3 are magnitude-summed so that cancellation between opposing faces cannot make a
material population look immaterial. The **signed** contributions are reported alongside,
because a population whose signed contribution nearly cancels is a different physical
situation from one whose contributions align, and the reader is entitled to both.

**F = max(Q2, Q3)** is the deciding figure. Q1 is the mesh-side predictor and is reported
whatever it says.

---

## 3. THE PRE-REGISTERED PREDICTION (falsifiable, recorded before measuring)

**Q1 ~= 0.7 %, within a factor of two** — i.e. 0.35 % to 1.4 %. Reasoning: prism-layer
cells on a hull of near-uniform surface refinement have comparable face areas, so an area
share should track the cell share of 0.67 %. **If Q1 lands outside 0.35–1.4 % the
prediction is WRONG and is recorded as wrong**, and the reason (clustering in a
finer-refined region such as the sail junction, or in a coarser one aft) is then part of
the finding rather than an explanation invented afterwards.

**Directional prediction on F:** F > Q1. Concave cells are produced by mesh distortion,
distortion concentrates where the geometry turns — the sail-hull junction and the stern
taper — and those are high-shear regions. A population biased toward high shear carries
more force share than area share. **If F < Q1 this prediction is WRONG**, and the honest
reading then is that the concave population sits preferentially in LOW-shear regions,
which strengthens the case for closure rather than weakening it.

---

## 4. THE THRESHOLDS AND WHAT EACH ONE MEANS — FIXED BEFORE THE ANSWER

| band | verdict on the concave finding | what happens to the forces |
|---|---|---|
| **F <= 1.0 %** | disclosed nuisance; **CLOSED** | forces graded normally, the three numbers printed in the certificate |
| **1.0 % < F <= 3.0 %** | **DISCLOSED WITH A NUMBER**; not closed | forces graded, and F is quoted in the uncertainty channel **beside every force number, every time it is printed** |
| **F > 3.0 %** | **MATERIAL TO THE GRADED QUANTITY** | forces are **REPORTED, NOT GRADED**, until either the mesh is repaired or a sign-resolved analysis demonstrates the contribution does not bias Z or M |

Rationale for 3.0 %: Roddy's own stated experimental uncertainty on the static
derivatives is **4 to 5 percent** (DTRC/SHD-1298-08). A mesh-quality contribution that
approaches the reference's own uncertainty cannot be called a nuisance, because it is no
longer small compared with the band it will be graded against. 3.0 % sits deliberately
below 4 % so the mesh error is required to be strictly smaller than the experiment's.

Rationale for 1.0 %: the round figure immediately above the predicted 0.67 %, so that
confirming the prediction closes the finding and exceeding it does not.

**Under the two-tier standard the finding is DISCLOSED in every band.** What these
thresholds decide is whether the disclosure carries a number or a shrug.

---

## 5. WHAT THIS DOES NOT DO

It does not admit the mesh, grade any force, or license a solve. It does not re-run
checkMesh — the sets were already on disk from the `-allGeometry -allTopology` run, and
Q1 is computed by indexing them, touching no live case. It says nothing about the L2
mesh, which carries its own checkMesh record and gets its own measurement under this same
document.

## 6. THE CONFIGURATION-NAMING RULE, BINDING ON THIS FAMILY

Adopted by the cfd-supervisor 2026-09-12 as a standing rule after this lane found the
collision. **Three numbering schemes are in play and two collide on the same integer:**
our own `build_suboff_a1_geometry.py` docstring calls the hull+sail body "Configuration
2"; **Roddy's Configuration 2 is the FULLY APPENDED model**; the DTRC experiment reports
additionally use AFF-n labels. Citing any of these by bare number is a mechanism that
produces a fabricated band while every person involved is being careful.

**Therefore: every band this family registers names the configuration BY ITS GEOMETRY —
which appendages are present — and cites its table by report, page, and the label exactly
as printed in that document. Never by a bare number.**

---

## 7. FREEZE

Frozen at the commit that adds this file. No threshold, band or conclusion in sections 3
or 4 may be altered afterwards; departures land as dated addenda that strike the original
legibly and never rewrite it.
