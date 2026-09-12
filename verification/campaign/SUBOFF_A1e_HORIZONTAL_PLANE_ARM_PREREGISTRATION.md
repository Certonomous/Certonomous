# SUBOFF A1e — HORIZONTAL-PLANE DRIFT ARM ON THE HULL-AND-SAIL BODY

**This is its own act, under its own name, with its own band. It is NOT "the SUBOFF
sweep" and it is NOT a stand-in for Z and M.** Sanaa's vertical-plane sweep — α, normal
force, pitching moment, hull/fin split, neutral point from Z_w and M_w — requires the
fully appended geometry and is registered separately. Two clearly separated acts cannot
be confused for one; a re-aimed act wearing the original's name can.

Author: cfd lab-lane, 2026-09-12. Directed by the cfd-supervisor.

---

## 1. WHY THIS ARM EXISTS

Roddy 1990 publishes **vertical-plane** derivatives for **one body only**. Verified from
the page image, not from OCR: Table 4, report page 19, "Vertical Plane" has a **single
column**, headed `Config 1 / Fully Appended`. Our meshed body — patches `inlet outlet
farfield symm hull sail` — is a hull with a fairwater and nothing else, so no
vertical-plane comparison against Roddy is possible on it, and quoting Config 1's
numbers against a hull+sail mesh would be comparing different bodies.

The same table's **"Horizontal Plane"** half has five columns, and the fourth is headed
**`Config 4 / B.H. + Sail`** — **our exact geometry**. So a matched, measured-tier
comparison exists today, in the drift plane, on the mesh that is already solving.

---

## 2. THE CONFIGURATION, NAMED BY GEOMETRY (binding rule, §6 of the concave-share
pre-registration)

**The body under test is the DARPA SUBOFF axisymmetric hull WITH the bridge fairwater
(sail) and WITHOUT stern appendages, ring wings or struts.** In Roddy 1990's own scheme
this is the column printed `Config 4  B.H. + Sail`.

**IT IS CITED THAT WAY AND NEVER BY A BARE NUMBER, BECAUSE THE NUMBERS COLLIDE ACROSS
DOCUMENTS AND EVEN WITHIN ONE PAGE.** Measured, both quotations read from page images:

- **Roddy 1990, Table 4, report page 19** — `Config 3 / Bare Hull`, `Config 4 / B.H. +
  Sail`, `Config 5 / B.H. + 4 Planes`, `Config 6 / B.H. + Ring Wing 1`, `Config 2 /
  Fully Appended`.
- **Liu & Huang 1998, report page 6**, towing-tank list — "Config. 1 Bare hull only /
  Config. 3 Hull with four stern appendages / Config. 8 Hull with sail and four stern
  appendages / Config. 6 Hull with ring wing #1 / Config. 7 Hull with ring wing #2".

**Roddy's Config 3 is the bare hull; Liu & Huang's Config 3 is the hull with four stern
appendages.** Same integer, different bodies, both official reports on one programme.

**And Liu & Huang switch schemes WITHIN A SINGLE PAGE.** Four paragraphs below that
towing-tank list, on the same page 6, the PMM list reads "Vertical plane statics - angle
of attack variation, -20° < α < 20°: Configuration 1, Configuration 6" and "Horizontal
Plane Statics - Angle of Drift Variation, -20° < β < 20°: Configuration 2" — which is
consistent with **Roddy's** scheme, not with the AFF scheme used immediately above it. A
careful reader citing "Configuration 1" from that page gets **either the bare hull or the
fully appended model depending on which paragraph their eye was on**, and nothing in the
citation would record which.

That is a fabrication mechanism that **survives care**, which is the only kind worth
writing a rule against.

**Geometry independently corroborated before any band was hung on it.** Liu & Huang
1998, report page 2: model length 14.2917 ft (4.356 m); fairwater leading edge
x = 3.0330 ft (0.924 m), trailing edge x = 4.2413 ft (1.293 m). Our `sail.stl` bounding
box measures x = 0.92445 .. 1.29091 m and the case length is 4.3561 m. Matched to the
millimetre.

---

## 3. THE REFERENCE AND THE GATED QUANTITIES

**Reference: Roddy, R. F. (1990), "Investigation of the Stability and Control
Characteristics of Several Configurations of the DARPA SUBOFF Model (DTRC Model 5470)
from Captive-Model Experiments", DTRC/SHD-1298-08, September 1990, AD-A227 715.**
Title page verified **as an image** under rule 15 — not by filename, not by hash, not
from the OCR sidecar. Band values from **Table 4, report page 19, "Horizontal Plane",
column `Config 4 / B.H. + Sail`**, read as an image.

| quantity | Roddy Config 4 value |
|---|---|
| **Y_v'** | **−0.023008** |
| **N_v'** | **−0.015534** |
| K_v' (reported, not gated) | −0.000697 |
| G, margin of stability (reported, not gated) | −4.081818 |

---

## 4. THE BAND — GATED AT ±4 %, THE TIGHTER AND LESS FAVOURABLE END

Roddy's uncertainty statement, **report page 105, read as an image**, verbatim:

> "The total uncertainties in the stability derivatives Z_w' and M_w' are calculated to
> be about 4 percent for both derivatives."

and, for the data base as a whole:

> "…the following overall uncertainty errors may be assigned to the experimental values
> of the stability and control derivatives **for fully appended submarines**: (1) static
> derivatives Z_w', M_w', Y_v', and N_v' 4 to 5 percent…"

**THE GATE IS ±4 %. The ±5 % reading is recorded beside it and does not gate.** Both
ends are available in the source; **4 % is the tighter and therefore the less favourable
one**, and a band taken at the kind end of a stated range is the easiest gate rather than
the honest one.

| quantity | value | **GATE, ±4 %** | outer reading, ±5 % (recorded, does not gate) |
|---|---|---|---|
| Y_v' | −0.023008 | **[−0.023928, −0.022088]** | [−0.024158, −0.021858] |
| N_v' | −0.015534 | **[−0.016155, −0.014913]** | [−0.016311, −0.014757] |

### 4.1 TWO DISCLOSURES THAT WEAKEN THIS BAND, STATED HERE AND NOT IN A FOOTNOTE

1. **Roddy's 4-to-5 percent assignment is written explicitly "for fully appended
   submarines". Our body is Config 4, hull and sail, which is NOT fully appended.**
   Applying that figure here is an **EXTENSION OF THE SOURCE'S OWN STATED SCOPE**. The
   extension is defensible — the quoted uncertainty is a property of the PMM/rotating-arm
   measurement chain rather than of the appendage set — but it is an extension, it is
   ours and not Roddy's, and the alternative would be no band at all. **If the
   supervisor or Sanaa judges the extension impermissible, this arm has no
   measured-tier band and must be reported, not graded.**
2. **The second symbol in that list is ambiguous in the scan.** It renders as `M_q'` or
   `M_w'` depending on the reading; item (2) of the same list separately names the
   rotary derivatives `Z_q', M_q', Y_r', N_r'`, so `M_w'` is the coherent reading of item
   (1). **Either reading contains Y_v' and N_v' explicitly**, which are the only two
   quantities gated here, so the ambiguity does not touch this band. Recorded because it
   is visible in the artifact.

---

## 5. THE SWEEP

- **Drift angles β = −12, −8, −4, 0, +4, +8, +12 degrees** (inside Roddy's own tested
  −20° < β < 20°).
- Quantities per point: lateral force Y and yawing moment N, nondimensionalised on
  Roddy's own convention; **hull/sail split reported** (both patches exist, so this split
  is real here, unlike the hull/fin split the vertical-plane act needs).
- **Derivatives Y_v' and N_v' by linear fit over |β| ≤ 8**, the linear range.
- Reported, not gated: K_v', the margin of stability G, and the y+ per patch at each
  point.

**The mesh is the existing hull+sail family. No new geometry is built for this arm.**

---

## 6. WHAT THIS ARM DOES NOT CLAIM

It does not deliver Sanaa's vertical-plane sweep and is not offered as it. It produces
no Z, no M, no neutral point from Z_w and M_w, and no hull/fin split — there are no fins
on this body. It says nothing about the fully appended configuration. The concave-cell
force share governed by `SUBOFF_A1b_CONCAVE_FORCE_SHARE_PREREGISTRATION.md` (frozen
`bc73dc0cae2063477d9d54ee5512b93a68be3249`) applies to this arm's forces exactly as it
applies to any other, and **F = max(Q2, Q3) is unmeasured at the time of writing**.

## 7. FREEZE

Frozen at the commit adding this file. No band, threshold or quantity above may be
altered afterwards; departures land as dated addenda that strike the original legibly.
