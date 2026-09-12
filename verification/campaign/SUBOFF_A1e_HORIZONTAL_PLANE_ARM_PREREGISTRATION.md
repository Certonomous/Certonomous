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

---

## DATED ADDENDUM 1 — 2026-09-12, same day, by the author: **THE §4.1 EXTENSION TEST WAS RUN AND IT SPLITS. `Y_v'` IS ADMITTED ON A CHECKED GROUND. `N_v'` FAILS IT AND FALLS TO REPORTED, NOT GRADED, UNDER §4.1's OWN FAILURE BRANCH.**

*lines whose number changed above this section: 0*

### A. THIS TEST WAS NOT PRE-REGISTERED, AND SAYING SO IS THE POINT

The cfd-supervisor proposed a checkable ground for §4.1's extension and asked that the
test and its two outcomes be registered before it was run. **That was not possible and
this lane will not pretend otherwise.** The whole of Roddy's Table 4 — including the
`Config 2 / Fully Appended` column this test needs — was read as a page image at
~22:2xZ while verifying the `Config 4` band, and both columns were already in hand
before the test was proposed. **A freeze written after the inputs are known is
decoration.** This addendum is therefore a **POST-HOC CHECK, LABELLED AS ONE**, and it
carries none of the evidentiary weight of §4's frozen band.

What it does carry: the rule it applies was stated by someone who had not seen the
numbers, and the outcome is **against us**, which is the direction that makes a post-hoc
check worth reading at all.

### B. THE GROUND

A relative uncertainty quoted for one body carries an **absolute** error floor set by the
rig. Transferring that relative percentage to a body whose derivative is **smaller** in
magnitude yields an absolute band **narrower** than the floor — conservative, erring
against us. Transferring it to a **larger** derivative yields a band **wider** than the
floor — **erring in our favour, which we may not do.**

Roddy's 4-to-5 % is scoped "for fully appended submarines", i.e. to the `Config 2`
column. The test is `|Config 4|` against `|Config 2|`, same table, same page.

### C. THE RESULT

| quantity | \|Config 4\| (ours) | \|Config 2\| (band's scope) | C4 vs C2 | band at 4 % on C4 | rig floor at 4 % on C2 | verdict |
|---|---|---|---|---|---|---|
| `Y_v'` | 0.023008 | 0.027834 | **smaller** | 9.203e-04 | 1.113e-03 | **CONSERVATIVE** — 17.3 % tighter than the floor |
| `N_v'` | 0.015534 | 0.013648 | **LARGER** | 6.214e-04 | 5.459e-04 | **ERRS IN OUR FAVOUR** — 13.8 % LOOSER than the floor |

The expectation behind the test — that stern planes add side force, so the fully appended
body's derivatives are larger — **holds for `Y_v'` and FAILS for `N_v'`.** Physically
unsurprising in hindsight: stern planes sit aft of the reference point, so they add side
force while *reducing* the destabilising yawing moment of a hull-and-sail body whose sail
is forward. Hindsight is not a prediction and is not offered as one.

### D. THE CONSEQUENCE, WHICH IS §4.1's OWN FAILURE BRANCH FIRING

- **`Y_v'` REMAINS GATED** at ±4 %, `[−0.023928, −0.022088]`, and the extension of
  Roddy's scope is now admitted on a **checked** ground rather than an assumed one.
- **`N_v'` IS REPORTED, NOT GRADED.** §4.1 states: "If the supervisor or Sanaa judges the
  extension impermissible, this arm has no measured-tier band and must be reported, not
  graded." For `N_v'` the extension is not merely unproven — it is **measurably in our
  favour**, and a band that is looser than the rig that produced it is not a gate.
  ~~`N_v'` −0.015534 gated in [−0.016155, −0.014913]~~ — **struck for `N_v'` only**, and
  the value with its interval is still reported beside every result.

### E. WHAT IS NOT DONE HERE, BECAUSE THE RULES FORBID IT

A tighter gate for `N_v'` is **available and is not taken by this lane.** Gating `N_v'`
on the rig's absolute floor rather than the relative percentage gives **±5.4592e-04
absolute = ±3.51 %**, which is tighter than the frozen ±4 % and defensible on the same
ground that admits `Y_v'`. **An addendum may not alter a gate, threshold, cap or label**,
so this lane does not apply it. It is recorded here as the available remedy; adopting it
requires a **superseding registration**, which is the cfd-supervisor's and Sanaa's call,
not this lane's. That such a registration would *tighten* the gate, and that our own
`N_v'` does not yet exist so no gate could be fitted to it, are both arguments for it —
and neither is this lane's to accept on its own behalf.

---

## DATED ADDENDUM 2 — 2026-09-12, same day, by the author: **THE RETRIEVAL QUESTION IS ANSWERED AND THE ANSWER IS NO. `N_v'` STAYS REPORTED, NOT GRADED. Two findings from the same page: the experiment was TRIPPED, and the `Config 1` collision is now verified from a table image.**

*lines whose number changed above this section: 0*

### A. THE RETRIEVAL QUESTION — NO SUCH UNCERTAINTY EXISTS IN THE PROGRAMME'S SUMMARY

The cfd-supervisor set the test that would legitimately grade `N_v'`: does any source
state an uncertainty **for a body that is not fully appended**, or state one **in absolute
terms**? Liu & Huang 1998, the summary of the whole programme's data, was the place to
look. **It does not.**

Its entire uncertainty content is the **AFF wind-tunnel measurement chain**, not forces:

- §A "AFF Velocity Uncertainty Analysis" — hot-film bias and precision, from Blanton,
  Forlini & Purtell (Ref. 6). **Table 5 "Velocity Bias Uncertainty" and Table 6 "Velocity
  Precision Uncertainty" are columned `u/Uref %`, `v/Uref %`, `w/Uref %`** — velocity
  components, nothing else.
- §B "AFF Pressure Uncertainty" — pressure and shear-stress measurement error, from
  Gowing (Ref. 7).

**There is no uncertainty statement anywhere in it for a force, a moment, or a stability
derivative** — therefore none for a non-fully-appended body and none in absolute terms.
**Table 14, the tow-tank results, carries no uncertainty or repeatability column at all.**
Refs. 6 and 7 are separate reports, not held on this box, and both concern velocity and
pressure rather than force, so neither would answer this question if retrieved.

**Consequence: `N_v'` REMAINS REPORTED, NOT GRADED**, with its value and interval printed
beside every result. `Y_v'` carries the arm. The act is honest and slightly smaller.

### B. THE EXPERIMENT WAS TRIPPED, AND THIS STRENGTHENS THE COMPARISON

Liu & Huang 1998, **report page 23, footnote to Table 14**, read as a page image:

> "Hull, bridge fairwater and four identical stern appendages all have tripwires
> installed at 5 percent of chord length."
>
> "Ringed wings have no turbulence stimulators applied to them"

**The hull and the bridge fairwater — both of our patches — carried tripwires at 5 % of
chord.** Transition was deliberately forced, so the measured body was **fully turbulent
by design**. Our solve is fully-turbulent k-ω SST with no transition model, which on an
untripped model would be a modelling mismatch to disclose. **Here it is the matched
choice**, and it is recorded as a point in the comparison's favour rather than left as an
unexamined assumption. This changes no gate.

### C. NO TOW-TANK RESISTANCE REFERENCE EXISTS FOR OUR GEOMETRY EITHER

Table 14's configurations are **8 Fully Appended, 3 Stern Appendages, 1 Bare Hull,
6 Ringed Wing #1, 7 Ringed Wing #2**. **There is no hull-and-fairwater-only row.** So the
hull+sail body has no measured tow-tank resistance in the programme summary, which is
consistent with `SUBOFF_A1b_PREREGISTRATION.md` holding its `CT` gate at **NOT A RESULT
by construction** and the tier at CODE-VERIFIED with the disavowal "NOT
experiment-validated". Recorded so that no later reader mistakes Table 14 for a
`CT` reference for this mesh.

### D. THE `Config 1` COLLISION, NOW VERIFIED FROM A TABLE IMAGE

§2 recorded the `Config 3` collision. **Table 14 supplies a sharper one on `Config 1`
itself**, printed in its own "Config. No." column:

- **Liu & Huang 1998, Table 14, page 23: `Config 1 = Bare Hull`.**
- **Roddy 1990, Table 4, page 19: `Config 1 = Fully Appended`.**

**The same integer names the emptiest and the fullest body in the programme, in two
official reports on that programme, both read here as page images.** §2's naming rule —
cite the configuration by which appendages are present, never by a bare number — is not a
precaution. It is the minimum required to avoid comparing a bare hull against a fully
appended one while citing correctly.
