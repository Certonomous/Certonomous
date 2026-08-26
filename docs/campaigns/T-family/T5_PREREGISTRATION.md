# T5 — heated wall-mounted cube against Meinders 1998: pre-registration (FROZEN)

**FROZEN 2026-08-26, BEFORE ANY SOLVER HAS RUN.** This file promotes
`T5_PREREGISTRATION_DRAFT.md` (2026-08-22) to the frozen pre-registration and
**supersedes it**. The draft is retained **unedited** beside this file as the
record of what was proposed; where the two differ, **this file governs and §16
below names every difference**.

**Promoted by the heat-transfer supervisor, 2026-08-26, `[lab-attributed]`, having
read the draft in full including all eighteen INTERPRETATIONs.** Tier definitions
are reserved to Sanaa and **nothing in this promotion interprets one**.

**Condition at freeze, and how it was checked** (`CLAUDE.md` rule 2, the
pre-compute amendment clause). The registered run tree is
`verification/runs/T-family/T5_runs/`. At the moment this file is committed that
tree holds **`digitise_t5.py`, `analyse_t5.py` and `run_one_t5.sh` and NO case
directory of any kind**: no `T5_CUBE_c`, `T5_CUBE_m` or `T5_CUBE_f`, no `0/`, no
`0.orig/`, no time directory, no mesh, no `log.solve`, no `STATUS.*` and no
`DONE` marker. **Zero core-minutes have been spent on this rung.**

**The freeze binds the WHOLE GRADING PATH IN ONE COMMIT** — pre-registration,
digitiser and comparator together — because the digitiser **produces the
reference**, and a freeze that bound the comparator but not the instrument that
manufactures the numbers it compares against would protect half the distance.

---


## 1. The rung in one paragraph, and what it is for

A single copper-cored, epoxy-shelled cube of height `H = 15 mm` stands on the
floor of a 51 mm channel in air at `Re_H` between 2500 and 5000. A horseshoe
vortex wraps its base, the shear layers off its three leading edges reattach on
the top and side faces, and an arc-shaped wake vortex closes about `1.5 H`
behind the trailing face. The cube is internally heated to a **uniform** core
temperature and the epoxy shell converts that into a **non-uniform** surface
temperature, from which Meinders derived the distribution of the local
convective heat transfer coefficient `h` over the whole cube. **This is the rack
physic**: a heated bluff obstacle in a bounded channel, its wake, and the
recirculation that carries its own hot air back over it. It is the second rung
of the DC spine and the first rung in the T-family that couples a solid
conduction problem to a separated turbulent flow.

**What this rung can test:** whether a steady wall-resolved `kOmegaSST`
conjugate solution reproduces the measured face-averaged and mid-line local `h`
**at the grid limit**, and whether it puts the wake reattachment in the right
place. **What it cannot test** is in §12, and the list is long.

---

## 2. Reference status, stated first because it decides what this rung can be

### 2.0 The primary is HELD

Meinders, E. R. (1998), *Experimental study of heat transfer in turbulent flows
over wall-mounted cubes*, Proefschrift, Technische Universiteit Delft, promotor
Prof. dr Dipl.-Ing. K. Hanjalić, ISBN 90-9012103-x, 281 pp.

- On disk: `docs/papers/forced_convection_heat_transfer/meinders_1998_tudelft_thesis_wall_mounted_cubes.pdf`
- `sha256 36c89a548030eae2aac84f2453c7c531632998433da660f4b655624cff6514cb`
  (re-verified on disk 2026-08-22 under H-1; matches the index entry `36c89a54…`)
- 15,477,157 bytes, PDF 1.3, 281 pages, page size 435 × 653 pt.
- **Title page verified** (L-144): printed title page read at PDF page 5, and the
  promotor and committee page at PDF page 6. It is the thesis it claims to be.
- **It is a scanned image PDF.** `pdftotext -layout` returns **0 bytes** over all
  281 pages. There is no text layer, no `.txt` sidecar can be made by extraction,
  and every number below was read from the rendered page image. This is why §10
  exists as a separate task with a named owner.

**Page numbering.** Printed page numbers and PDF page indices differ by a
drifting offset (blank leaves were dropped in the scan). Measured on this file:
printed 5 = PDF 9; printed 11 = PDF 14; **printed 39–162 = PDF 41–164, a
constant +2 through Chapters 3 and 5.** *Every citation below gives the printed
page and the PDF page.* A citation by one number alone is not reproducible on
this artifact and is not used.

### 2.1 What the thesis states, verbatim, on the uncertainty this rung may arm

Printed **p. 59** (PDF 61), §3.2.4, under the heading *Overall accuracy of the
heat transfer coefficient*:

> "From the above analysis of the different contributions to the experimental
> uncertainty it is concluded that the accumulation of errors results in
> approximately 5% accuracy in the local heat transfer for the mid-region of the
> five faces of the cube. The heat transfer coefficients at the edges have a
> somewhat higher uncertainty of about 10 % due to, among others, mapping
> inaccuracies."

Printed **p. 55** (PDF 57), §3.2.4, on the surface temperature that the `h`
derivation rests on:

> "Application of both the in situ calibration and the image restoration
> technique resulted in an absolute accuracy of 0.4 °C in the surface
> temperature for the mid-plane of the faces, and of about 0.6 °C close to the
> edges because of the effects of image mapping."

Printed **p. 58** (PDF 60), on the numerical truncation error inside the
measurement's own inverse solve:

> "From these observations it can be concluded that for the grid size with 30 ×
> 30 surface cells (3 cells in the layer thickness) the truncation error is
> within 3%."

**These three statements are the whole band budget of this rung**, and the third
is already inside the first (§3.2.4 accumulates it). No band in this rung is
improvised, and **`VERIFICATION_CHARTER.md` §2e is not used here**: no band on
any T5 row is derived from an eigenspace or barycentric perturbation envelope,
no T5 quantity is classified as Reynolds-stress SHAPE or FORCING class, and
§2e's per-row classification requirement therefore does not arise. Every T5 band
is an experimentalist's stated uncertainty plus a digitisation increment in
quadrature (§7.3).

### 2.2 The conditions this design reproduces, and where each comes from

Every row is a read from the printed page. Nothing here is recollection.

| item | value | printed p. (PDF p.) |
| --- | --- | ---: |
| cube height `H` | 15 mm | 39 (41) |
| channel height `D` | 51 mm; `D/H = 3.4` | 39 (41) |
| channel width | 600 mm; width-to-height ratio 12 | 39 (41) |
| origin | `x = 0` at the **front centreline of the cube**; `x` streamwise, `y` normal, `z` spanwise | 39, 41 (41, 43) |
| tripping | zig-zag strip, floor and roof; for the single cube, on the floor **75 cm upstream** of the cube | 41, 123 (43, 125) |
| roof boundary layer | developing **laminar** (single-cube configuration) | 123 (125) |
| floor boundary layer | developing **turbulent**; `Re_θ = 660` at `x = 0` in the absence of the cube | 124 (126) |
| shear velocity | `u_τ ≈ 0.25 m/s` at `x = 0` | 124 (126) |
| core acceleration | `dU_∞/dx = 0.67 1/s` | 123 (125) |
| bulk velocity, LDA case | `u_B = 4.47 m/s` → `Re_H = 4440` | 123, 125 (125, 127) |
| `Re_H` definition | `u_B H / ν`, bulk velocity and cube height (confirmed by `St = f H / u_B`, p. 126) | 123, 126 (125, 128) |
| heat-transfer `Re_H` set | **2750, 3200, 4000, 4440, 4970** (`u_B` = 2.8, 3.2, 4.0, 4.5, 5.0 m/s) | 146 (148) |
| transition threshold | the strip trips only for `u_B > 2.5 m/s`, i.e. `Re_H > 2500`; a jump in `h` on top and side faces at `Re_H ≈ 2500` | 123, 160–162 (125, 162–164) |
| cube construction | copper core in a **1.5 mm** epoxy mantle, machined to ±0.01 mm | 43, 55 (45, 57) |
| copper conductivity | ≈ 390 W/mK | 44 (46) |
| epoxy conductivity | **0.24 W/mK**, isotropic, spatially and temperature independent | 44, 45 (46, 47) |
| copper core temperature | **75.0 °C** for all experiments in the thesis bar one sweep; uniform "within the tolerance of 0.05 °C" | 44 (46) |
| base plate | formaldehyde, λ = **0.33 W/mK**, ±10 % | 41 (43) |
| surface finish | thermally black paint, ε = **0.95** measured within 2 % | 50, 55 (52, 57) |
| air inlet temperature | "room temperature (**20-21 °C**)" | 147 (149) |
| **`h` is convective only** | `φ″_conv = φ″_cond − φ″_rad`, eq. (3.4); the radiative part is computed from `T_sur`, ambient, ε and view factors and **subtracted** | 45 (47) |
| `h` definition | `h_ref = φ″_conv / (T_sur − T_ref)`, eq. (3.5) | 45 (47) |
| buoyancy | `Gr/Re² = HgΔT/TU² ≈ 0.001` | 148 (150) |
| wake reattachment | `x/H = 2.4–2.5` from LDA; ≈ `1.5 H` behind the trailing face from oil film | 136, 137 (138, 139) |
| horseshoe separation saddle | ≈ **1.4 H** upstream of the leading face | 129 (131) |
| top-face reattachment | ≈ `x/H = 0.9`, intermittent | 154 (156) |
| side-face reattachment | ≈ `x/H = 0.9` | 153 (155) |
| vortex shedding | `St = f H / u_B ≈ 0.093–0.10`, slope accurate within 5 % | 126, 127, 128 (128, 129, 130) |

**Two thesis defects noticed while reading, recorded rather than smoothed.**
(i) The buoyancy parenthetical on p. 148 reads "`T = 333 °C` is the absolute
temperature"; 333 is the value in **kelvin** and the unit is a typo — the
argument and the number are unaffected. (ii) The text on p. 154 refers the
`h`-vs-`C_p` correlation to "Fig. 5.42", and p. 155 refers to "Fig 4.50"; the
figure printed on p. 155 is numbered **5.40** and a *different* figure numbered
**5.42** appears on p. 158. **Figure numbers in Chapter 5's running text do not
reliably match the printed figure captions.** The digitiser in §10 keys on the
**printed caption on the page**, never on a cross-reference in the text, and
records the page for every figure it opens.

### 2.3 The chosen operating point: `Re_H = 4440` — with the citation for why

**Registered: `Re_H = 4440`, `u_B = 4.47 m/s`. INTERPRETATION 2.**

It is the best-documented single-cube case in the thesis and it is the only one
that is best-documented in *every* channel this rung needs:

- **It is the LDA case.** "The LDA-analysis was conducted at a bulk velocity of
  4.47 m/s which corresponds to a Reynolds number of `Re_H = 4440`" — printed
  p. 123 (PDF 125). Every mean-velocity, Reynolds-stress, reattachment and
  turbulent-kinetic-energy figure in §5.3 (Figs 5.15, 5.20–5.31) is that case.
- **It is in the heat-transfer set**, printed p. 146 (PDF 148): 2750, 3200,
  4000, **4440**, 4970. It appears in the local-`h` figures 5.38 and 5.39 and
  the face-averaged figures 5.41, 5.45 and 5.46.
- **It is the case with the surface-temperature boundary-condition sweep** —
  copper core varied 60/65/70/75/80 °C — printed p. 147 and Fig. 5.37 on p. 149
  (PDF 149, 151). That sweep is the evidence §4 uses to choose the thermal
  boundary condition.
- **It is the case with the liquid-crystal cross-check** of the infrared
  surface temperatures, printed p. 147, Fig. 5.35 on p. 148 (PDF 149, 150).
- **It is the case with the tripped/untripped comparison**, Fig. 5.44 on
  printed p. 159 (PDF 161).
- It is comfortably above the `Re_H ≈ 2500` tripping threshold, so the floor
  boundary layer is turbulent and the flow structure documented in §5.3 applies
  (printed p. 123: "the presented flow field analysis applied to the Reynolds
  number range of about 2500 < `Re_H` < 5000").

`Re_H = 4970` is the only competitor and it has no LDA field of its own. The
choice costs nothing to revisit before the freeze; after the freeze it is fixed.

Derived, and registered as the case's kinematic viscosity:
`ν = u_B H / Re_H = 4.47 × 0.015 / 4440 = 1.510e-05 m²/s` — air near 20 °C.
The thesis states no `ν`; this is the value **implied by its own two numbers**
and it is labelled as derived, not read. `Pr = 0.71`.

### 2.4 `NOT OBTAINED`, in the four fields Charter §6b requires

The primary is held. **Seven things this rung would use are still not held**,
and each is stated in the four fields rather than absorbed.

| # | what is missing | which rows it blocks or degrades | why it was not obtained | acquisition path and its price |
| --- | --- | --- | --- | --- |
| 1 | **Tabulated numerical values for any figure.** The thesis has no data appendix; Appendix A is thermal-conductivity measurement, pp. 247–257. | Every graded row. All reference values must be **digitised** (§10). | The document is a 1998 print scan with no text layer (`pdftotext` → 0 bytes). Nothing to extract. | Digitisation by a named lane (§10). No spend. A dataset request to TU Delft or to the Hanjalić group is **a send and is Sanaa's alone** (Standing Rule 7) — not proposed here. |
| 2 | **The coefficient `A` in `h̄ = A(Re_H)^B`.** Printed p. 157 (PDF 159) states *"A least squares fit through the data suggests an exponent of `B = 0.65`"* and calls `A` and `B` "constants" without giving `A`. | Would have given a **FORMULA-tier** cross-check on `h̄`, independent of digitisation. It does not exist. | The value is simply not printed. | None. The correlation is **unusable as a formula** and this rung does not pretend otherwise; the exponent alone is recorded as a REPORTED shape check (row R2, §7.2). |
| 3 | **A stated uncertainty on the reattachment length.** pp. 136–137 (PDF 138–139) give `x/H = 2.4–2.5` and "approximately 1.5H downstream of the trailing face" with no error bar. | **G4 is REPORTED, never graded** — an experiment's band is its stated uncertainty and there is none. | Not stated by the author. | None available. G4 stays REPORTED. |
| 4 | **Inflow turbulence quantities at the cube plane.** `Re_θ = 660` and `u_τ = 0.25 m/s` at `x = 0` are given (p. 124), and `u′²/u_τ²` profiles in Fig. 5.4 — but no `ω`, no `v′²` at that station, and the profile figure is at `x/H = 6.7`, not at `x = 0`. | Degrades the inflow specification; makes I1 (§6) a **check row with a registered tolerance** rather than a matched boundary condition. | The thesis measured what it measured. | None. §5 states the precursor construction and I1 the tolerance; a miss flags G1–G3 to REPORTED. |
| 5 | **A single air temperature.** "20-21 °C" is a range (p. 147). | Contributes a **1.7 % intrinsic floor** on every `h` row (§7.4) — 0.5 K of ambiguity on a driving difference of about 30 K. | Stated as a range by the author. | None. Registered as a floor, not hidden. |
| 6 | **The roof boundary layer's thickness/state at the cube plane.** Described only as "a developing laminar boundary layer at the opposing wall" (p. 123). | Affects channel blockage and the core acceleration; feeds the I2 check (§6). | Not measured in the thesis for this configuration. | None. Modelled fully turbulent with the departure disclosed (INTERPRETATION 6). |
| 7 | **Vogel & Eaton 1985 — T3's primary.** Not this rung's reference, named here only because T5 sits behind T3 in the spine. | Nothing in T5. | `T3_PREREGISTRATION.md` §2 records the whole search. | Unchanged; not this lane's item. |

---

## 3. §2a — the identity test, row by row

Charter §2a refuses a row whose value is fixed by **algebra**: derivable by
construction from its own inputs, so that a wrong treatment reproduces it
exactly. The test is applied to every proposed row **before** the row is
written, not after it passes.

| row | quantity | is it fixed by construction? | verdict |
| --- | --- | --- | --- |
| G1–G3 | mid-line mean `h` on front / top / rear | No. `h = φ″_conv/(T_sur − T_in)` with `φ″_conv` from the solved near-wall temperature gradient and `T_sur` from the conjugate solve. Neither is imposed. | **admissible** |
| G1a–G3a | face-averaged `h` on front / top / rear | No, same reason. | **admissible** |
| G4 | reattachment `x_R/H` | No — a solved wall-shear sign change. | **admissible (REPORTED)** |
| G5a–G5c | mid-line mean `T_sur` per face | **Partly.** `T_sur` is bounded above by the imposed copper 348.15 K and below by the inlet 293.65 K, so a row whose reference value sits within a few kelvin of either bound would be nearly satisfied by the boundary conditions alone. **Registered guard:** G5 is admissible only where the reference `T_sur` lies at least 5 K from both bounds; the digitised value is checked against that condition by the comparator, and a face failing it returns **NOT A RESULT — identity**, not a PASS. From the printed Figs 5.35/5.37 the mid-line values sit near 46–68 °C against bounds of 20.5 and 75.0 °C, so the condition is expected to hold on all three faces — but it is **checked, not assumed**. | **admissible under a guard** |
| I1, I2 | inflow `Re_θ`, `u_τ`, `dU_∞/dx` | These *are* set by the inflow construction — which is exactly why they are **check rows, not graded rows**, and are counted toward no verdict. | **GUARD** |
| HB | heat-balance closure | Fixed by construction in a *correct* solve — which is the point; it is a **GUARD** and a §2c-exempt self-check (L-218, §9). | **GUARD** |

---

## 4. The thermal boundary condition: conjugate, and the thesis's own words for why

**Registered: conjugate. The epoxy shell is meshed as a solid region;
`T = 348.15 K` (75.0 °C) is imposed on its inner surface. INTERPRETATION 3.**

The choice is between (a) a constant-temperature cube surface and (b) a
conjugate epoxy shell. The thesis speaks to both sides and the two statements
must not be conflated.

**The thesis says the surface is not isothermal.** Printed p. 49 (PDF 51):

> "A consequence of this approach is that the surface temperature of the cube is
> not isothermal in the powered situation, nor in the unpowered situation. This
> epoxy layer makes the experiment different from that of Moffat et al."

and printed p. 44 (PDF 46), on why the *core* is:

> "The temperature change across the copper core is, therefore, negligible
> compared to that across the epoxy-layer which resulted in an almost uniform
> copper temperature within the tolerance of 0.05 °C."

**The thesis also says `h` did not depend on the surface temperature *level*.**
Printed p. 148 (PDF 150), on the `T_co` = 60/65/70/75/80 °C sweep at
`Re_H = 4440`:

> "the heat transfer coefficients calculated from these surface temperature
> boundary conditions differed about 5%. These differences are within the
> experimental uncertainty of the method and measurement technique. Taking this
> experimental uncertainty into account, it can be concluded that the convective
> heat transfer did not depend on the boundary condition imposed by the
> different surface temperatures."

**These are not the same claim, and the design turns on the difference.** The
sweep varied the *level* of the surface temperature while the epoxy shell kept
the same *shape* in every arm — every case in that sweep had the same
non-uniform distribution, scaled. It therefore says nothing about what happens
when the distribution is replaced by a flat one. A constant-`T` CFD surface
imposes a distribution the experiment never had, and then `h = φ″/(T_sur −
T_ref)` is evaluated against a reference `h` that was derived with a
**different** `T_sur` field in its denominator. The size of that mismatch is
unknown, it is largest exactly where the surface gradients are largest — the
leading edges of the top and front faces, where the rung's most interesting
physics is — and **removing unknown model floors is what this rung is for.**

How large is the non-uniformity? From the printed Figs 5.35 (p. 148) and 5.37
(p. 149) the mid-line surface temperature at `Re_H = 4440` with a 75.0 °C core
runs roughly **46 °C at the leading edges to 68 °C on the top face**, against an
ambient of 20–21 °C — a local driving difference between about **26 K and 47 K,
a factor of 1.8 across one cube.** *(Those two numbers are eyeball reads of the
printed figure by this lane, made to justify a design choice. They are not a
digitisation product, they grade nothing, and no comparator will ever read
them.)*

The conjugate route is also **fully specified by the thesis and cheap**:
λ_epoxy = 0.24 W/mK, δ = 1.5 mm ± 0.01 mm, inner surface at 75.0 °C uniform
within 0.05 °C. The copper core need not be meshed at all, because the thesis
itself replaced it with a Dirichlet condition — printed p. 44 (PDF 46):

> "The uniform copper temperature of the measurement cube provided the Dirichlet
> temperature boundary condition for the inner bound of the epoxy layer."

**The constant-`T` surface is retained as a registered arm, `S_m`** (§8), so the
rung *measures* the size of the effect instead of asserting it. If `S_m` and the
conjugate medium level agree within the band, the thesis's insensitivity claim
is confirmed to extend from level to shape and the finding is worth its case; if
they disagree, the conjugate choice is vindicated with a number.

**Radiation is OFF** (`radiationModel none`). This is not a simplification, it is
the correct match: Meinders **subtracts** the radiative flux (eq. 3.4, p. 45)
and reports `h` as convective only. A CFD run with radiation on would be
comparing a different quantity. Registered, and stated in §12 as a thing the
rung consequently cannot see.

**The cube's bottom face is adiabatic on the solid side**; the formaldehyde base
plate is not meshed. INTERPRETATION 4. The thesis's own reading of that loss,
printed p. 46 (PDF 48):

> "It is noted that conduction through the base plate preheats the oncoming
> flow. This will affect the local reference temperature and thus the heat
> transfer coefficient. This effect is only of minor importance (second order
> effect) and is, therefore, not taken into account."

and printed p. 151 (PDF 153), on the horseshoe-vortex region specifically:
"although the effect was estimated to be smaller then 5% (this was estimated
from a global energy balance)." **The horseshoe-vortex foot of the front face is
therefore the one place where this design's adiabatic floor is known to be worth
up to 5 %**, and G1's mid-line mean is defined over the central 80 % of the face
partly for that reason (§7.1).

---

## 5. The design, with the reason for each decision

### 5.1 Solver

**`chtMultiRegionSimpleFoam`**, OpenFOAM ESI **v2606**, two regions (fluid
`air`, solid `epoxy`), `g = (0 0 0)`, `radiationModel none`, steady SIMPLE.
INTERPRETATION 5.

Toolchain checked rather than assumed, 2026-08-22T18:12:38Z:

```
$ which buoyantSimpleFoam chtMultiRegionSimpleFoam simpleFoam
rc=1                                   # none on PATH
$ echo FOAM_TUTORIALS=[$FOAM_TUTORIALS]
FOAM_TUTORIALS=[]                      # unset in this shell
```

**The solvers exist; the environment is simply not sourced in a bare shell.**
`/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/` holds 139
`*Foam` executables including `simpleFoam`, `buoyantSimpleFoam`,
`chtMultiRegionSimpleFoam`, `chtMultiRegionFoam` and
`buoyantBoussinesqSimpleFoam`; `META-INFO/api-info` reads `api=2606 patch=0`.
Every T5 script sources `/usr/lib/openfoam/openfoam2606/etc/bashrc` explicitly
and asserts `$FOAM_TUTORIALS` is non-empty before it does anything else.

**A `chtMultiRegionSimpleFoam` tutorial exists, and it is the right one.**
`tutorials/heatTransfer/chtMultiRegionSimpleFoam/` holds `cpuCabinet`,
`externalCoupledHeater`, `heatExchanger`, `jouleHeatingSolid` and
`multiRegionHeaterRadiation`. **`cpuCabinet` is an electronics-cooling
conjugate case** — the closest shipped precedent to this rung's physics — and
`heatExchanger` carries an `Allrun-parallel`, which is the decomposition
pattern T5 needs. `buoyantSimpleFoam/circuitBoardCooling` is a second,
fluid-only precedent for the `S_m` arm. **These are read as dictionary
templates. No tutorial number is a T5 result** and no tutorial case is copied
into the run tree without every dictionary being re-read line by line (the
T1c/L-142 lesson: a build chain can quote a wrong wall cell as correct at every
link).

Why not `buoyantBoussinesqSimpleFoam`, the T1b/T1c/T3 solver: it is
single-region and cannot carry the epoxy shell, which §4 makes the point of the
rung. Why not `chtMultiRegionFoam`: it is transient, and this rung is steady by
construction (§12 says what that costs).

`g = 0` is justified by the thesis's own number, printed p. 148 (PDF 150):
`Gr/Re² ≈ 0.001`, quoted in §2.2, together with its observation that the
isotherm distributions on a **vertically mounted** test section were symmetric,
which is the experimental demonstration that buoyancy was negligible.

### 5.2 Domain

Half-domain, symmetry at the cube centre plane `z/H = 0`. INTERPRETATION 7.

| extent | value | why |
| --- | --- | --- |
| streamwise inlet | `x/H = −8` | the horseshoe separation saddle is at `−1.4 H` (p. 129) and the thesis measured `C_p` from `x/H = −2.7` (p. 131); 8 H leaves the inflow free to develop and the upstream influence contained |
| streamwise outlet | `x/H = +20` | reattachment at 2.4–2.5 (p. 137); the thesis's own wake profiles run to `x/H = 8` (Fig. 5.21); 20 H puts the outlet 12 H beyond the last measured station |
| channel height | `y/H = 0 → 3.4` | `D = 51 mm`, `D/H = 3.4`, printed p. 39 |
| spanwise | `z/H = 0 → 5`, symmetry at `z/H = 0`, slip at `z/H = 5` | the thesis's spanwise traverses (Figs 5.28, 5.29, p. 142–143) show the profiles asymptoting to boundary-layer values by `z/H ≈ 2`; the real channel is 40 `H` wide and modelling it is unaffordable and pointless |

**The symmetry plane is a real restriction and it is named here, not buried in
§12:** the thesis measured vortex shedding from the side faces at `St ≈ 0.093`
(p. 126) with *alternating*, quasi-periodic side-face reattachment (p. 153). A
symmetry plane forbids antisymmetric shedding by construction. So does steady
RANS. The half-domain therefore costs nothing that the steady formulation had
not already cost — and the thesis's own justification is on printed p. 137
(PDF 139): "flow symmetry was demonstrated from measurements across the entire
flow domain." A full-span sensitivity case is named as a deferred option, not
run.

### 5.3 Inflow

The inflow is the hardest part of this rung and it gets a **precursor**, not a
guess. INTERPRETATION 8.

`X_2d`: a 2D developing-channel case, `D = 51 mm`, floor and roof no-slip,
`kOmegaSST`, run to a converged state. The plane whose profile is mapped onto
the 3D inlet at `x/H = −8` is chosen so that, **after 8 H of further development
inside the 3D domain and in the absence of the cube**, the floor boundary layer
reaches `Re_θ = 660` at `x = 0`. That selection is an iterated pre-run
adjustment, it is made **before any graded case is launched**, and each
iteration's plane and resulting `Re_θ` are logged in `T5_INFLOW_LOG.md` in the
run tree. It touches no `h`.

The roof is modelled as a fully turbulent no-slip wall although the experiment's
roof layer was laminar (p. 123). **This is a disclosed departure**
(INTERPRETATION 6), it makes the roof displacement thickness too large, and its
observable consequence is the core acceleration — which is why `dU_∞/dx` is
check row **I2** against the thesis's stated `0.67 1/s`. The alternative, a slip
roof, removes the roof layer entirely rather than getting it wrong, and is named
as the fallback if I2 fails.

### 5.4 Mesh and the ladder

Block-structured hexahedral, body-fitted around the cube, built by
`build_t5.py` from one parametric recipe with a single refinement factor
`r = 1.6` applied to **every** direction including the first wall layer, so that
the three levels are geometrically similar and the triple is a true refinement
(this is the T1b lesson: a ladder that holds the first cell fixed refines
something other than the near-wall solution and its triples came back DIVERGENT).

**Registered default ladder — the FALLBACK-sized one, and §11 says why it is the
default.** INTERPRETATION 1, and it is the one most likely to be argued with.

| level | fluid cells | epoxy cells | total | first layer on cube | predicted `y+_max` on cube |
| --- | ---: | ---: | ---: | ---: | ---: |
| `C` coarse | 5.1e4 | 3.0e3 | **5.4e4** | 0.128 mm | ≈ 2.6 |
| `M` medium | 2.09e5 | 1.1e4 | **2.20e5** | 0.080 mm | ≈ 1.6 |
| `F` fine | 8.57e5 | 4.6e4 | **9.03e5** | 0.050 mm | ≈ **1.0** |

Effective cell-count ratios 4.07 and 4.11, i.e. **1.60 and 1.61 per direction**.
Epoxy shell resolved with 2 / 3 / 5 cells through its 1.5 mm — the medium level
therefore matches **the thesis's own discretisation of the same layer**, which
used 3 cells for most of its results and measured a truncation error within 3 %
there (printed p. 57–58, PDF 59–60).

**Stretch ladder, if and only if the measured rate on `C` beats §11's Model A**
(the same recipe one step up): 1.39e5 / 5.77e5 / **2.37e6** total cells, first
layers 0.080 / 0.050 / 0.031 mm, `y+_max` ≈ 1.6 / 1.0 / 0.63.

**The `y+ ≤ 1` requirement, honestly stated.** On the registered default ladder
it is met **on the fine level — the level whose value is graded** — and not on
the coarse and medium levels, which carry `y+_max ≈ 2.6` and `1.6`. That is a
departure from the brief's design constraint and it is disclosed as
INTERPRETATION 1 rather than papered over. Three things bound the damage: (i)
`y+ = 2.6` is still deep inside the viscous sublayer, so **no wall function is
active anywhere on the ladder** and the SST low-Re treatment is continuous
across all three levels; (ii) achieved `y+` is **measured** per case, per face,
and printed beside every row — it is not a design assertion; (iii) the
alternative that would satisfy `y+ ≤ 1` on all three levels is to fix the first
layer at 0.050 mm and refine tangentially only, which produces a triple that
does not contain the wall-normal discretisation error at all and a GCI that
therefore understates it. **A ladder that hides the error it is measuring is
worse than a coarse level at `y+ 2.6`**, and the choice is put to the reviewer
in those terms.

`checkMesh` birth certificate on every case (Charter §9). Near-wall aspect
ratios of order 30–70 are expected on a wall-resolved 3D mesh and are reported
with their numbers, not hidden. `check_t5_mesh.py` reads every `points` file and
refuses before any solver runs; **its planted-positive test (an inverted
grading) must FIRE** or the build stops.

### 5.5 Numerics and convergence

`endTime 5000`, `deltaT 1`, `writeInterval 1000`, `purgeWrite 3` —
`writeInterval` strictly less than `endTime` because that is a durability
property (L-140) and because the convergence test needs two checkpoints.
**`residualControl` is not written** (L-141: in T1c a genuinely unconverged case
sat at residual 4e-05, and in T3 the residual was again not the instrument).

**CONVERGED** means: the largest change of any cell value of `T` in either
region, and separately of `U` in the fluid, between the checkpoints at
`endTime − 1000` and `endTime`, is at most **1e-6 of that field's range**. This
is T1c's and T3's criterion, unchanged, registered here before any case exists.
The zero is verified by a **live planted control** (`1.234e-03` written into a
copy and read back from disk) before the comparator reads anything (§9).

Extension from `latestTime` is permitted under the T1b §6 disclosure rule — new
log, new `STATUS`, first extension `Time` exactly `endTime + 1`, marker
re-judged across both segments — and **the decision to extend is taken on the
convergence state alone, never with an `h` in view.**

### 5.6 The conjugate interface scheme — carried from T9a-D, with its own disclaimer

**Registered: `laplacian(alpha,e) Gauss harmonic corrected` in the solid region.
INTERPRETATION 12.**

`T9aD_RESULTS.md` (reported 2026-08-22, D454, L-227) measured on an EXACT-tier
1-D composite wall that replacing `Gauss linear` with `Gauss harmonic` moved the
wall flux error from **+1.806 % to +0.0000000 %** — harmonic is not merely
better there, it is exact, because a harmonic face conductivity is the
two-half-cells-in-series algebra written out. Row A1 PASSed with the error
dropping by more than three orders at every level, and `Gauss harmonic
corrected` was accepted by ESI v2606.

**T9a-D's own §2.5 forbids carrying that straight into this rung, and it is
quoted rather than paraphrased:**

> "**It does not establish that `Gauss harmonic` is correct for a conjugate
> rung.** It establishes that harmonic is *exact* for **piecewise-constant `k`
> with the interface on a mesh face on a 1-D orthogonal mesh**. T9b's coupled
> interface, a non-orthogonal mesh, a graded `k`, or a temperature-dependent
> `k` are all outside what was measured. The algebra in §2.1 is a statement
> about two half-cells in series, not about conjugate heat transfer."

T5 is exactly the case that disclaimer names: a **coupled fluid–solid
interface**, a mesh that is non-orthogonal at the cube edges, and a
conductivity jump of about **9:1** (epoxy 0.24 W/mK against air's effective
near-wall value). So the scheme is adopted **as the registered default because
it is the lab's best-measured choice, and its adoption is tested rather than
assumed**: `H_c` runs the coarse level with `Gauss linear` on the solid
laplacian, everything else identical, and the difference in the `h` and `T_sur`
rows is **REPORTED**. It costs 0.04 USD (§11.1) and it is the cheapest way to
find out whether an EXACT-tier finding survives the transfer to a coupled
interface. If `H_c` moves a graded row by more than its band, **the scheme
choice becomes a named uncertainty of this rung** rather than a settled input,
and that is a finding worth more than the case cost.

---

## 6. Check rows and guards, measured on every case

| row | quantity | registered tolerance | consequence of a miss |
| --- | --- | --- | --- |
| **I1** | `Re_θ` on the floor at `x = 0`, cube absent (from `X_2d` + the empty-channel 3D run) | `660 ± 7.5 %`, i.e. `[610, 710]`; `u_τ` in `[0.23, 0.27] m/s` | G1–G3, G1a–G3a and G5 carry the flag "inlet condition outside the registered window" and are **REPORTED, not graded** |
| **I2** | core acceleration `dU_∞/dx` over `−6.7 ≤ x/H ≤ +6.7`, cube absent | `0.67 ± 25 % 1/s` — wide on purpose, because the roof layer is knowingly wrong (§5.3) | same flag as I1; and the slip-roof fallback becomes the registered remedy for a re-run, **not** a post-hoc tuning of the case that already ran |
| **HB** | conjugate heat-balance closure: convective heat leaving the five air-exposed faces vs conductive heat entering through the epoxy inner surface | `0.5 %` (`physics_rules.yaml`) | **GUARD.** It withdraws the run, never the hypothesis, and is counted in no tally |
| **MB** | mass in/out on the fluid region | `0.1 %` | GUARD |
| **YP** | achieved `y+` on each cube face: max, mean, and the fraction of faces above `y+ = 5` | reported, no threshold | printed beside every row; a non-zero fraction above `y+ = 5` is a finding about the mesh and is stated as one |

---

## 7. The rows, the bands, and the gate that is binding

### 7.1 Definitions, written before any value is seen

`x = 0` is the **front centreline of the cube** (thesis p. 41), so `x/H = 1` is
the trailing face. Every length below uses that origin and says so, because a
reattachment quoted from the wrong origin is the classic way to be exactly `1 H`
wrong.

- **Mid-line, front face**: the vertical line on the front face in the symmetry
  plane `z/H = 0`, from the channel floor to the top leading edge. It is
  partition **CD** of the thesis's path `ABCD` (Fig. 5.39, printed p. 151).
- **Mid-line, top face**: the streamwise centre-line on the top face,
  `z/H = 0`, leading edge to trailing edge. Partition **BC** of `ABCD`.
- **Mid-line, rear face**: the vertical line on the rear face, `z/H = 0`.
  Partition **AB** of `ABCD`.
- **Mid-line mean**: the arc-length-weighted mean of `h` over the **central
  80 %** of each mid-line, excluding `0.1 H` at each end. Two reasons, both
  registered: the excluded strips are the "edges" where the thesis's own
  uncertainty is 10 % rather than 5 % (p. 59), and on the front face the lower
  strip is the horseshoe foot where the unmodelled base-plate conduction is
  worth up to 5 % (p. 151). The **full-line** mean with a 10 % band is computed
  and **REPORTED** beside it.
- **Face average**: the area-weighted mean of `h` over the whole face,
  the quantity the thesis plots in Figs 5.41 and 5.45.
- **`h`**: `φ″_conv / (T_sur − T_ref)` per eq. (3.5), with **`T_ref` = the
  channel inlet air temperature**, registered at `293.65 K` (20.5 °C, the
  midpoint of the thesis's "20-21 °C"). INTERPRETATION 9. For a *single* heated
  cube this is unambiguous: the thesis's §3.2 discussion of `T_in` vs `T_∞` vs
  `T_m` vs an adiabatic reference temperature (pp. 47–50) exists for **arrays**,
  where upstream cubes preheat the air. Here the mixed-mean rise is
  `ΔT_m = φ_tot/(ṁ c_p) ≈ 2.5 W / (0.164 kg/s × 1005 J/kgK) ≈ 0.015 K` — the
  power from Fig. 5.47 (p. 161) and the mass flow from `ρ u_B D W`. Fifteen
  millikelvin on a thirty-kelvin difference. The distinction that dominates
  Chapters 6–8 is **absent** for the single cube, and the arithmetic that shows
  it is printed here rather than asserted.
- **`x_R/H`**: the streamwise station of the last negative-to-positive crossing
  of the floor wall shear in the symmetry plane, searched downstream of
  `x/H = 1.0`. The thesis's 2.4–2.5 is quoted **on the same origin**.

### 7.2 The rows

| row | quantity | kind | band | verdict path |
| --- | --- | --- | --- | --- |
| **G1** | mid-line mean `h`, **front** face, fine level | GRADE | §7.3 combined, mid-face 5 % basis | PASS / GATE FAIL / NOT A RESULT |
| **G2** | mid-line mean `h`, **top** face | GRADE | as G1 | as G1 |
| **G3** | mid-line mean `h`, **rear** face | GRADE | as G1 | as G1 |
| **G1a** | **face-averaged** `h`, front face | GRADE | §7.3, 10 % basis (a face average contains its edges) | as G1 |
| **G2a** | face-averaged `h`, top face | GRADE | as G1a | as G1a |
| **G3a** | face-averaged `h`, rear face | GRADE | as G1a | as G1a |
| **G4** | reattachment `x_R/H` behind the cube | **REPORTED** | none — the thesis states no uncertainty (§2.4 item 3) | REPORTED with the thesis's 2.4–2.5 printed beside it |
| **G5a-c** | mid-line mean `T_sur`, front / top / rear | GRADE, under the §3 identity guard | `0.4 °C` (p. 55) ⊕ digitisation of Fig. 5.37 | as G1, or **NOT A RESULT — identity** |
| **R1** | full-mid-line mean `h`, all three faces | REPORTED | 10 % basis | REPORTED |
| **R2** | `h̄_cube` vs `Re_H` exponent across a two-point `Re` sweep, against the thesis's `B = 0.65` | REPORTED | none — `A` is not held (§2.4 item 2) | REPORTED. *Requires a second `Re_H`; see INTERPRETATION 10 — it is NOT in the registered case list and is costed at zero.* |
| **R3** | side-face and top-face reattachment `x/H` against the thesis's ≈ 0.9 (pp. 153–154) | REPORTED | none stated | REPORTED |
| **DP** | `Pr_t` 0.85 vs 0.50, on G1a–G3a | discrimination | against the row's own band | SEPARATED / NOT SEPARATED |
| **DC** | laminar baseline vs SST at the medium level | Charter §2c | §8 | MET / NOT MET / UNMEASURED |
| **DS** | constant-`T` surface vs conjugate, medium level, all `h` rows | comparison | REPORTED against the band | REPORTED |
| **DH** | `Gauss harmonic` vs `Gauss linear` on the solid laplacian, coarse level (§5.6) | comparison | REPORTED against the band | REPORTED |
| **I1, I2, HB, MB, YP** | §6 | GUARD | §6 | withdraw the run, never the hypothesis |

**The `N of M` tally of this rung is `0 of 9` until it has run.** A plan is not a
capability (`T_FAMILY_INDEX.md` §4).

### 7.3 Bands: stated uncertainty ⊕ digitisation increment, and the arithmetic is printed

Every band is `sqrt( stated² + digitisation² )` in relative terms, per Charter
§6b's treatment of a digitised referent. **The digitisation increments below are
estimates made from the figures' axis resolution before any point was taken**;
§10 requires the digitiser to *measure* its own increment and the comparator to
use the measured value, refusing if the measured increment exceeds the estimate
by more than 50 %.

| row | stated | digitisation source | est. increment | est. combined band |
| --- | ---: | --- | ---: | ---: |
| G1a–G3a face-averaged `h` | 10 % | **Fig. 5.45**, printed p. 160 (PDF 162): `h` [W/m²K] vs `Re_H`, **linear axes**, 0–90 over ≈ 35 mm, distinct symbol per face | ≈ 1.3 W/m²K on `h ≈ 55–80` → **≈ 2 %** | **≈ 10.2 %** |
| G1–G3 mid-line mean `h` | 5 % | **Fig. 5.39** p. 151 (PDF 153) for the *shape* `h/h_tot` ⊕ **Fig. 5.45** p. 160 for the *scale* `h̄_cube` | shape ≈ 0.05 in `h/h_tot` → **≈ 5 %**; scale ≈ 0.6 W/m²K after averaging five faces → **≈ 1 %** | **≈ 7.2 %** |
| G5a–c `T_sur` | 0.4 °C | **Fig. 5.37** p. 149 (PDF 151), `T_sur` 40–70 °C over ≈ 30 mm | ≈ 0.5 °C | **≈ 0.64 °C** |

**The most important line in this table is the second one, and it is a finding
before the rung has run.** Fig. 5.39 is a small scanned plot carrying **five
overlapping Reynolds-number symbol series** on an axis 0–3.0; the increment a
careful digitiser can achieve on it is about 5 % of `h/h_tot = 1`, which is
**the same size as the experiment's own 5 % stated uncertainty.** Digitising
that figure roughly `√2`-doubles the band of the rows built on it. Fig. 5.45 —
linear axes, absolute units, one symbol type per face — is about **five times
better conditioned**, which is why G1a–G3a exist alongside the brief's G1–G3 and
why **INTERPRETATION 11 proposes that, if the reviewer wants one set of graded
`h` rows rather than two, it should be the face-averaged set.**

**`h̄_cube` is reconstructed from Fig. 5.45, not from Fig. 5.41.** Fig. 5.41
(p. 156, PDF 158) plots the same data on **log-log** axes spanning one decade in
`h` in about 30 mm, where a digitisation increment is several percent. Fig. 5.45
plots it linearly. `h̄_cube = (h_front + h_side,N + h_side,S + h_rear + h_top)/5`
— the five faces are equal in area — and averaging five independent reads
reduces the increment by `√5`. The comparator recomputes it that way and
**refuses** if the reconstruction disagrees with a direct read of Fig. 5.41 by
more than 8 %.

### 7.4 Intrinsic floors, quantified before the run (T10a §5.3 discipline)

| floor | size | why it exists | rule |
| --- | ---: | --- | --- |
| ambient temperature ambiguity | **1.7 %** on every `h` row | the thesis states "20-21 °C", a 0.5 K half-range on a ≈ 30 K driving difference | a deviation below 1.7 % is **GATE REACHED**, reported not graded — the rung cannot resolve it |
| base-plate conduction, front-face foot | up to **5 %**, local | thesis p. 151, quoted in §4 | the excluded 0.1 H strips (§7.1) keep it out of the graded mid-line mean; it is stated on the R1 full-line row |
| the measurement's own truncation | **within 3 %**, already inside the 5 % | thesis p. 58 | not added again — double counting a stated accumulation is a new number |

### 7.5 The triple gate is BINDING

**A graded row whose grid triple is not CONVERGING returns `NOT A RESULT`, with
the fine value and the triple printed beside it. It cannot return `PASS`.**
Standing Rule 5; T3 §7.1; D440's amendment made binding before this rung's first
solve. `analyse_t5.py` reads the triple **first**. Order of evaluation for every
graded row:

1. any ladder level NOT CONVERGED → **NOT A RESULT**;
2. triple DIVERGENT, STAGNANT, OSCILLATORY or EXACT → **NOT A RESULT**, value,
   both triples and observed orders printed;
3. reference file absent or its `digitised` flag false with no values →
   **BLOCKED**, fine value and triple printed as REPORTED information;
4. G5 only: identity guard of §3 violated → **NOT A RESULT — identity**;
5. deviation below the applicable intrinsic floor (§7.4) → **GATE REACHED**;
6. otherwise **PASS** inside the band, else **GATE FAIL**, GCI printed.

GCI at `Fs = 1.25`, unequal-ratio fixed-point form on the **effective** ratios
from the actual cell counts; **never quoted when the three values are not
monotone.** `--selftest` proves every branch on synthetic triples, including
that a DIVERGENT triple with a value **inside** the band still returns NOT A
RESULT, and that with a CONVERGING triple the verdict is reachable both ways by
moving the fine value (the mutation control).

### 7.6 The reference slot — schema only, values absent by design

`verification/runs/T-family/T5_runs/T5_reference_primary.json`, **absent today
and absent at comparator-freeze time by construction** (§10):

```
{"provenance": {"citation": "Meinders, E.R. (1998), Experimental study of heat
                             transfer in turbulent flows over wall-mounted
                             cubes, TU Delft, ISBN 90-9012103-x",
                "sha256": "36c89a548030eae2aac84f2453c7c531632998433da660f4b655624cff6514cb",
                "title_verified_page1": true,
                "digitised": true,
                "digitiser": "<lane id>", "digitised_utc": "<iso8601>",
                "page_offset_printed_to_pdf": 2},
 "conditions": {"Re_H": 4440.0, "u_B_m_s": 4.47, "H_m": 0.015,
                "T_core_C": 75.0, "T_in_C": 20.5},
 "rows": {"G1":  {"value": 0.0, "uncertainty": 0.0, "units": "W/m2K",
                  "figure": "5.39", "page_printed": 151, "page_pdf": 153,
                  "partition": "CD", "digitisation_increment": 0.0,
                  "increment_units": "h/h_tot"},
          "G2":  {"...": "figure 5.39, partition BC"},
          "G3":  {"...": "figure 5.39, partition AB"},
          "G1a": {"value": 0.0, "uncertainty": 0.0, "units": "W/m2K",
                  "figure": "5.45", "page_printed": 160, "page_pdf": 162,
                  "face": "front", "digitisation_increment": 0.0,
                  "increment_units": "W/m2K"},
          "G2a": {"...": "figure 5.45, face top"},
          "G3a": {"...": "figure 5.45, face rear"},
          "G5a": {"value": 0.0, "uncertainty": 0.4, "units": "degC",
                  "figure": "5.37", "page_printed": 149, "page_pdf": 151},
          "G5b": {"...": ""}, "G5c": {"...": ""}},
 "reported": {"G4_thesis_text": {"x_R_over_H_low": 2.4, "x_R_over_H_high": 2.5,
                                 "page_printed": 137, "page_pdf": 139,
                                 "uncertainty_stated": false},
              "h_bar_cube": {"value": 0.0, "units": "W/m2K",
                             "reconstructed_from": "figure 5.45, five faces"}}}
```

`uncertainty` is the author's stated figure in the row's units;
`digitisation_increment` is the **measured** increment and the comparator adds it
in quadrature. **The person who fills this file reads it from the printed page
(L-144) and writes the page number.** Nothing in `analyse_t5.py` changes when it
appears — that is §10's whole point.

---

## 8. Discrimination, with a registered trivial baseline (Charter §2c)

**DC — the laminar baseline.** `L_m`: the medium level, identical mesh,
identical boundary conditions, **turbulence model off** (`laminar`). This is the
recognition control in the K0cS/D411 shape: the row that grades a closure must
return a *different* verdict for the closure and for the closure's absence.

`DC` is **MET** when **both** hold:

1. the laminar arm's face-averaged front-face `h` differs from the SST medium
   value by **more than 25 %**; and
2. **the set of graded rows the SST arm passes that the laminar arm does not
   pass is non-empty.**

Clause 2 is the load-bearing one and clause 1 alone would not be enough: D411's
failure was a control that passed *more* rows than the closure it was
controlling, with the two sitting 0.0055 % apart on the row that mattered. If
`L_m` does not converge, `DC` is **UNMEASURED**, not satisfied (Charter §2c
boundary clause 1) — and at `Re_H = 4440` a laminar solution of a separated
bluff-body flow may well refuse to reach a steady state. That is anticipated,
not a surprise to be explained afterwards.

**DP — the `Pr_t` arm.** `P_m`: medium level, `Pr_t = 0.50` against the
registered `0.85`. **SEPARATED** if it moves any of G1a–G3a by more than that
row's own band (≈ 10.2 %); NOT SEPARATED otherwise, in which case the rung
**cannot discriminate a thermal closure parameter at this band** and says so
rather than reporting a PASS as though it meant something.

**DS — the constant-`T` arm.** `S_m`: medium level, fluid region only, cube
surface at a uniform temperature equal to the **area-averaged** conjugate
surface temperature from the conjugate medium case (so the two arms carry the
same mean driving difference and the comparison isolates the *shape*).
**REPORTED**, not graded — it grades a modelling choice of this design, not a
hypothesis about the physics, and §4 says what it is for.

---

## 9. Controls, including the planted zero and the boring one

**The planted zero (Standing Rule 3).** `PLANT = 1.234e-03` — the same constant
as `analyse_t3.py` — written into a **copy** of the surface `h` field on disk and
read back through the comparator's own reader. `analyse_t5.py` **refuses (exit
2)** if the reader cannot see it. A zero from a reader that has not been shown
able to see a non-zero is not evidence. The plant is live at every run, not a
unit test.

**The mutation control.** `--selftest` proves each branch of §7.5's order on
synthetic triples and proves the verdict is reachable both ways.

**Two registered predictions that ought to be boring (L-218).** *"Register one
prediction you expect to be boring: it is the only thing that tells you the
other predictions mean anything."*

- **B1 — the conjugate heat balance closes.** The total convective heat leaving
  the five air-exposed cube faces equals the total conductive heat arriving
  through the epoxy inner surface to within **0.5 %** on every case. This is
  true *by construction* of the steady solid energy equation in a correct solve.
  **It is registered as a self-check and it is stated in advance that a number
  materially above 0.5 % means the reader or the region coupling is wrong, not
  the physics.** It costs nothing and it is the difference between a finding and
  an artefact.
- **B2 — the two cube averages differ by 1–3 %.** The thesis computed `h̄` two
  ways — flux-weighted (eq. 5.6) and mean-of-local (eq. 5.7) — and measured, on
  printed p. 156 (PDF 158): *"Differences between both averages appeared to be
  only a couple of percent (1-3%) for all heat transfer results given in this
  thesis."* The comparator computes both from the conjugate fine case. A
  difference far outside 1–3 % means this rung's surface temperature
  non-uniformity is wrong — which is the one thing §4 chose the conjugate model
  to get right. **A pass here is boring. That is the point.**

**Registered predictions that are not boring, written before any solve.**

1. **`x_R/H` on the fine level between 1.8 and 3.2.** Steady two-equation
   closures habitually under-predict the wall-mounted-cube wake; the thesis's
   2.4–2.5 sits inside. Outside that window, the momentum lever points at the
   mesh or the inflow before anything thermal is read.
2. **Face-averaged front-face `h` within ±20 % of the digitised value; top face
   within ±35 %.** The front face is impingement-dominated and RANS does it
   tolerably; the top face is a bound-vortex-plus-reattachment problem and it is
   where the closure is expected to be worst. If the top face comes back
   *better* than the front, something is wrong with the reading, not with
   turbulence modelling.
3. **`Pr_t` 0.85 → 0.50 raises `h` by 12–25 %.** T1b measured 7.4–10.0 % for a
   0.85 → 1.0 change (an 18 % change in `Pr_t`); this is a 41 % change in the
   opposite direction, so the scaled expectation is roughly double.
4. **The conjugate surface temperature range on the fine level spans at least
   15 K** between its coolest and hottest mid-line point. The thesis's figures
   show roughly 22 K. A CFD surface that comes back nearly flat has an epoxy
   conductivity or a shell thickness wrong.
5. **`DS` moves the graded `h` rows by 5–15 %** — the shape effect §4 argues
   for. Below 5 % and the thesis's level-insensitivity extends to shape, the
   conjugate machinery bought little, and this rung should say so plainly.
6. **The triples.** *Honest statement, and it is the prediction most likely to
   be right:* **at least one of G1–G3 / G1a–G3a comes back not CONVERGING.**
   T1b's `Nu` triples were DIVERGENT or STAGNANT at comparable `y+` targets;
   T3's four rows returned NOT A RESULT on gates (1)/(2) with **no case
   reaching 1e-6 at 20 000 iterations in 2D**. This rung asks a 3D conjugate
   separated flow to reach 1e-6 in **5 000**. If it does not, every affected row
   is NOT A RESULT under §7.5 and the record says which — **the criterion is not
   relaxed after the fact.** A fourth level or an extension is *proposed* in
   that event, not run.

---

## 10. The digitisation task — and the order it must happen in

**The order is: write the comparator → freeze it → digitise → freeze the
reference → run. Not any other order.** Charter §2d asks what was readable
before the freeze; the answer for T5 must be *"the comparator's author had never
seen a Meinders `h` value."* `analyse_t5.py` is written against the §7.6 schema
with the values absent, committed, and its sha recorded, **before**
`T5_reference_primary.json` is created. `scripts/check_comparator_freeze.py`
enforces the comparator half; the ordering half is enforced by commit order and
is stated here so a reviewer can check it.

**Who does it.** A T-family `lab-lane`, **not** the lane that wrote
`analyse_t5.py` and **not** the lane that writes `build_t5.py`. The digitiser's
lane id and the UTC timestamp go into the `provenance` block. This separation is
disclosed here because it is a claim about how the number was produced, and an
undisclosed one would be worthless.

**What must be digitised.**

| # | figure | printed p. (PDF p.) | what is taken | feeds |
| --- | --- | ---: | --- | --- |
| D1 | **Fig. 5.45** — face-averaged `h` [W/m²K] vs `Re_H`, five faces | 160 (162) | the five face values at the abscissa nearest 4440; **the digitiser reads the abscissa and refuses if it is not within ±100 of 4440** | G1a–G3a; `h̄_cube` for G1–G3 |
| D2 | **Fig. 5.39** — `h/h_tot` and `T_sur` along path `ABCD` (rear–top–front, symmetry plane `z/H = 0`), parametric in `Re_H` | 151 (153) | the `Re_H = 4440` series (△), partitions AB, BC, CD, at ≥ 40 points per partition | G1–G3 shape; R1 |
| D3 | **Fig. 5.37** — `T_sur` along `ABCD` for the `T_co` sweep | 149 (151) | the `T_co = 75 °C` series only | G5a–c |
| D4 | **Fig. 5.38** — `h/h_tot` along path `ABCDA` (side–front–side–rear) at `y/H = 0.5` | 150 (152) | the `Re_H = 4440` series | R1, horizontal mid-line, REPORTED only |
| D5 | **Fig. 5.41** — cube- and face-averaged `h` on log-log | 156 (158) | one direct read of `h̄_cube` at 4440 | the ±8 % cross-check of §7.3 |
| D6 | **Figs 5.2 and 5.3** — centreline `u(y)` at `x/H = 6.7`; `U_∞(x)` giving `dU_∞/dx` | 124 (126) | the profile and the slope | I1, I2 |

**Increment measurement, not increment assertion.** For each figure the
digitiser records, in the JSON: the pixel-to-data scale from two axis
fiducials, the plotted symbol radius in data units, and the digitiser's own
repeatability from **re-digitising five points blind and reporting the spread**.
`digitisation_increment` is the larger of the symbol radius and that spread.
The estimates in §7.3 (0.05 in `h/h_tot`; 1.3 W/m²K on Fig. 5.45; 0.5 °C on
Fig. 5.37) are **this lane's forecasts from axis resolution**, and the
comparator refuses if the measured increment exceeds its forecast by more than
50 % — because a band that silently grew is a band that was chosen after the
fact.

**Path bookkeeping, which is where this will go wrong if it goes wrong.**
Fig. 5.39's abscissa is "location on path", not a coordinate. The partitions
are labelled on the figure `A|REAR|B|TOP|C|FRONT|D` and the thesis confirms the
front face is partition **CD** of `ABCD` and **BC** of `ABCDA` (printed p. 150,
PDF 152). The digitiser records, per partition, which end is which physical
edge, and the comparator asserts that the front-face partition's `h` maximum
sits in its upper half (the stagnation region at `y/H ≈ 2/3`, printed p. 150) —
a cheap orientation check that catches a reversed path.

---

## 11. Cost, predicted — and the two models disagree by a factor of four

**Estimate, labelled as such per the Compute Budget Charter. Nothing here is
measured on a 3D conjugate case, because this lab has never run one.**

**Basis.** `T3_RESULTS.md` §9 measured cell-iteration throughput on this box for
2D turbulent `buoyantBoussinesqSimpleFoam` and found it is **not a constant**:
`3.78e5` cell-it/core-s at 28 160 cells falling to **`7.73e4` at 235 520
cells** — a 4.9× degradation over an 8.4× size increase, attributed to cache
residency. Fitting those two points gives `rate ∝ N^(−0.747)`.

Two models are carried because the honest answer is that nobody knows which is
right above 236 k cells:

- **Model A — power-law extrapolation.** `rate = 7.73e4 (N/2.355e5)^(−0.747)`,
  continued all the way. This extrapolates **9.5× beyond the measured range**;
  `VERIFICATION_CHARTER.md` §3's own rule refuses growing-increment
  extrapolation for a discretisation order and the same scepticism applies here.
  It is the **pessimistic bound**.
- **Model B — plateau.** The same law below 236 k cells, and a **floor at
  `7.73e4`** above it, on the physical argument that once the working set is out
  of L3 the rate becomes memory-bandwidth-bound and stops falling. It is the
  **registered planning basis**.

**Both models are then divided by a registered penalty of `2.0×` for 3D and
conjugate**: a 3D cell has six face neighbours against four, the pressure system
is materially harder, and `chtMultiRegionSimpleFoam` runs an outer region-coupling
loop that 2D single-region `buoyantBoussinesqSimpleFoam` does not.
**That 2.0 is an assumption, not a measurement**, and the first thing this rung
measures is whether it is right — `C` reports its own rate before `M` launches.

Parallel efficiency **0.85** assumed on 4 ranks (`scotch`). Core-hours are
rank-seconds and do not change with `nProcs`; only wall does.
**`nProcs = 4`** for `C`, `M` and the arms; **`nProcs = 8` for `F` if eight
cores are free at launch, else 4.** `0.0513 USD` per core-hour.

### 11.1 The registered default ladder (5.4e4 / 2.20e5 / 9.03e5), `endTime 5000`

| case | cells | `nProcs` | Model B core-h | Model B USD | Model A core-h | Model A USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `X_2d` precursor inflow (2D) | 3.0e4 | 1 | 0.44 | 0.023 | 0.44 | 0.023 |
| `C` coarse | 5.4e4 | 4 | 0.76 | 0.039 | 0.76 | 0.039 |
| `M` medium | 2.20e5 | 4 | 8.84 | 0.453 | 8.84 | 0.453 |
| `F` fine | 9.03e5 | 8 | 38.47 | 1.974 | 105.64 | 5.419 |
| `P_m` `Pr_t = 0.50` | 2.20e5 | 4 | 8.84 | 0.453 | 8.84 | 0.453 |
| `L_m` laminar baseline | 2.20e5 | 4 | 6.19 | 0.317 | 6.19 | 0.317 |
| `S_m` constant-`T` arm | 2.10e5 | 4 | 8.15 | 0.418 | 8.15 | 0.418 |
| `H_c` `Gauss linear` interface twin | 5.4e4 | 4 | 0.76 | 0.039 | 0.76 | 0.039 |
| **total** | | | **72.5** | **3.72** | **139.7** | **7.16** |

**This ladder fits under both models**, at 15 % and 29 % of the 25 USD ceiling
(487 core-h). Predicted wall on the critical path (`F`): **4.8 h on 8 ranks**
under Model B, **13.2 h on 8 ranks** under Model A.

### 11.2 The stretch ladder (1.39e5 / 5.77e5 / 2.37e6) — and it breaches

| case | cells | Model B core-h | Model B USD | Model A core-h | Model A USD |
| --- | ---: | ---: | ---: | ---: | ---: |
| `X_2d` | 3.0e4 | 0.44 | 0.023 | 0.44 | 0.023 |
| `C` | 1.39e5 | 3.96 | 0.203 | 3.96 | 0.203 |
| `M` | 5.77e5 | 24.39 | 1.251 | 47.65 | 2.445 |
| `F` | 2.37e6 | 100.20 | 5.140 | **562.58** | **28.861** |
| `P_m` | 5.77e5 | 24.39 | 1.251 | 47.65 | 2.445 |
| `L_m` | 5.77e5 | 17.08 | 0.876 | 33.36 | 1.711 |
| `S_m` | 5.45e5 | 23.04 | 1.182 | 43.13 | 2.213 |
| `H_c` interface twin | 1.39e5 | 3.96 | 0.203 | 3.96 | 0.203 |
| **total** | | **197.5** | **10.13** | **742.8** | **38.10** |

**Under Model A the stretch ladder costs 38.10 USD and breaches Sanaa's standing
25 USD ceiling. Its fine level alone costs 28.86 USD — more than the whole
ceiling.** Wall for that one case would be **141 h on 4 ranks, 70 h on 8** — most
of a week on a box with 14+ of 16 cores already committed.

**This is why §5.4's default ladder is the smaller one.** The stretch ladder is
launched only if `C` and `M` measure a rate at or above Model B, and even then
only on a fresh cost registration.

### 11.3 The stop threshold, and what is cut — with the consequence stated

- **Stop threshold: 20 USD (390 core-h) cumulative measured spend.** Recomputed
  from `STATUS.<case>` after every completion. On breach, **no further case
  launches** and the rung reports what it has. A budget overrun stops the run;
  it does not get a new budget (Standing Rule 12).
- **Per-case guard:** any case whose measured core-h exceeds **3×** its Model B
  prediction is stopped at its next checkpoint, and the measured rate is
  reported as a cost-science finding (T3's §9 was worth its 2 USD for exactly
  this reason).
- **What is cut first, and it is always the fine level.** `F` is 53 % of the
  registered default and 76 % of the stretch under Model A.

**The consequence of cutting `F`, stated so it cannot be discovered later.**
With only `C` and `M` there are **two levels, not three**. A Roache triple
cannot be formed. The comparator's `triple` field is then **UNMEASURED**, and
UNMEASURED is not CONVERGING, so §7.5 gate (2) fires on every graded row:

> **Every graded row — G1, G2, G3, G1a, G2a, G3a, G5a, G5b, G5c — returns
> `NOT A RESULT` by construction. The rung's tally becomes `0 of 9`. G4 and the
> other REPORTED rows still report; the discrimination arms still report; and
> the rung is a cost-science and feasibility result, not a validation result.**

That is not a degradation to be argued about after the fact; it is the
registered consequence, and it is the reason the *smaller* ladder — which
preserves a real three-level triple under both cost models — is the registered
default rather than the fallback.

---

## 12. What this rung cannot see

- **Vortex shedding, and everything downstream of it.** The thesis measured
  `St ≈ 0.093–0.10` (pp. 126–128) and traced quasi-periodic side-face
  separation and reattachment to it (p. 153). A steady RANS with a symmetry
  plane forbids it twice over. Where the measured `h` owes its value to the
  shedding — the side faces above all — this rung is comparing different
  objects, and the side faces are therefore **not graded** (G1–G3 and G1a–G3a
  are front, top and rear only).
- **Time-dependent heat transfer**, Chapter 3.3 and §5.4.3 of the thesis.
  Nothing here is transient.
- **Radiation.** Off by construction, correctly, because the reference
  subtracts it (§4). This rung consequently says nothing about combined-mode
  exchange from a heated obstacle — that is T10b.
- **Arrays.** The row of cubes (Ch. 6), the tandem (Ch. 7) and the 4×4 matrix
  (Ch. 8) are where the adiabatic-reference-temperature machinery of §3.2 bites
  and where the actual rack recirculation lives. **A single cube has no
  upstream heated neighbour**, so this rung backs no *inlet-temperature* claim
  at all (see §14).
- **The base plate**, hence up to 5 % locally at the horseshoe foot (§4).
- **Any closure but `kOmegaSST`**, and any `Pr_t` but 0.85 and 0.50.
  `NUMERICS_KNOWLEDGE` K0c-T: "quote two models or quote none" — a second
  closure is the first extension to propose if this rung gates.
- **Whether the digitised curve is the `Re_H = 4440` series.** Fig. 5.39 carries
  five overlapping series; §10's abscissa check protects Fig. 5.45 but Fig. 5.39
  has no abscissa to check against. **This is the single largest
  provenance risk in the rung** and it is stated as such.
- **A mesh-converged `h` if the triples come back not CONVERGING** —
  prediction 6, §9, which this lane expects to be right.
- **Anything about `h̄ = A(Re_H)^0.65` as a formula**, because `A` is not held.

---

## 13. Open decisions for review — INTERPRETATION 1..12

1. **The ladder is the small one (5.4e4 / 2.20e5 / 9.03e5), so `y+ ≤ 1` holds on
   the fine level only** (`y+_max` ≈ 2.6 / 1.6 / 1.0). §5.4. This is a departure
   from the brief's design constraint. Alternatives: the stretch ladder
   (`y+` 1.6/1.0/0.63, 10.13 USD under Model B but **38.10 USD and a ceiling
   breach under Model A**), or a fixed first layer with tangential-only
   refinement (`y+ ≤ 1` everywhere, but a triple that does not contain the
   wall-normal error and a GCI that understates it). **The reviewer's call.**
2. **`Re_H = 4440`** rather than 4970 (§2.3). Cheap to change before the freeze.
3. **Conjugate epoxy shell rather than a constant-temperature surface** (§4),
   with the constant-`T` case demoted to the `S_m` arm. Overruling this halves
   the rung's cost and changes what it measures.
4. **The formaldehyde base plate is not meshed; the cube's bottom face is
   adiabatic on the solid side** (§4). Alternative: a third solid region at
   λ = 0.33 W/mK, more faithful and more expensive.
5. **`chtMultiRegionSimpleFoam`** rather than `buoyantSimpleFoam` plus an
   externally-imposed shell resistance (§5.1).
6. **The channel roof is modelled fully turbulent** although the experiment's
   roof layer was laminar (§5.3). Fallback: a slip roof. The check that decides
   is I2.
7. **Half-domain with a symmetry plane at `z/H = 0`, spanwise extent 5 H**
   (§5.2). Alternative: full span at roughly double the cell count, which buys
   nothing under steady RANS but removes one stated restriction.
8. **Precursor inflow with the mapping plane tuned so `Re_θ = 660` at `x = 0`**
   (§5.3), rather than an analytic profile. The tuning is logged and happens
   before any graded launch.
9. **`T_ref` = inlet air temperature at 293.65 K** (§7.1), with the 15 mK
   mixed-mean argument printed. The residual "20-21 °C" ambiguity is carried as
   a 1.7 % intrinsic floor, not hidden.
10. **A second `Re_H` (row R2, the 0.65 exponent check) is NOT in the registered
    case list.** It would need a full second ladder. Named so it is a visible
    omission rather than an oversight; costed at zero because it is not run.
11. **Two sets of graded `h` rows — mid-line (G1–G3, the brief's) and
    face-averaged (G1a–G3a, this lane's addition).** They cost the same solve.
    §7.3 shows the face-averaged set has a band about 10.2 % against the
    mid-line set's 7.2 % *on a much better-conditioned digitisation* — Fig. 5.45
    is linear-axis and single-symbol, Fig. 5.39 is a five-series overlay whose
    digitisation increment alone is the size of the experiment's stated
    uncertainty. **If only one set is to be graded, this lane recommends the
    face-averaged set** and the mid-line set becomes REPORTED. G5 (surface
    temperature, band 0.4 °C from a *stated absolute* accuracy) is also this
    lane's addition and is the cleanest row in the rung.

12. **`Gauss harmonic corrected` on the solid laplacian**, carried from T9a-D's
    EXACT-tier A1 PASS into a coupled fluid–solid interface that T9a-D's own
    §2.5 explicitly says it does not cover (§5.6). Tested by the `H_c` twin at
    0.04 USD rather than assumed. Overruling this means registering
    `Gauss linear` and expecting a known first-order interface error.

---

## 14. Certificate lines this rung can add (H-6)

`docs/product/DC_CERTIFICATE_TEMPLATE.md` §1 rule 1: **a line enters on a PASS or
GATE REACHED verdict from a FROZEN comparator and on nothing else.** Nothing
below is held; every row is PENDING and stays PENDING until `analyse_t5.py` says
otherwise.

| quantity class | DC meaning | backing row | template status | note |
| --- | --- | --- | --- | --- |
| **recirculation** | hot air returning across the top or ends of a rack | **G4** (`x_R/H`) plus R3 (top/side reattachment) | **already in §4 of the template**, PENDING, named for T5 → T8 | **G4 is REPORTED, not graded** (§2.4 item 3). Template rule 1 admits a line only on PASS or GATE REACHED. **A REPORTED row does not qualify, so on the design as it stands T5 cannot add the `recirculation` line.** This is a real gap between the directive's expectation and this rung's evidence, and it is flagged rather than finessed |
| **local `h` on a heated obstacle** | convective heat removal from a powered component's own surfaces — the die/package/heat-sink-face class | **G1a–G3a** (face-averaged), **G1–G3** (mid-line) | **NOT in the template today** — it would be a **new quantity class** | This is T5's real contribution and the first line in the whole certificate that would be **backed by a published measurement** rather than a closed-form reference. §2 of the template records that no line is yet so backed |
| **conjugate surface temperature on a heated obstacle** | component surface temperature under a known internal load — the junction-temperature class | **G5a–c** | **NOT in the template today** — a second new class | Complements T9a's conjugate interface line, which is exact-tier; this would be its measured-tier counterpart |
| **inlet temperature** | rack-inlet air temperature, the class the ASHRAE 27 °C guideline is stated about | **none** | template §4 names **T5** for this class | **T5 cannot back it.** A single isolated cube has no upstream heated neighbour and therefore no inlet-temperature quantity; the thesis's own adiabatic-reference-temperature machinery (pp. 47–50) exists for the array chapters. **Backing this class needs the row, tandem or 4×4 matrix — Chapters 6, 7 and 8 of the same held primary — which is a different rung.** Recorded here as a correction to the template's §4 expectation, for the supervisor to rule on |

**Two of the four lines T5 might add are new classes; one is blocked by the
verdict rule; one is a class T5 was expected to back and cannot.** Saying so now
is what H-6 is for — *"so the product artifact grows with the validation instead
of after it"* — and a spec that grew a line before its rung passed is the failure
H-6 exists to prevent.

---

## 15. Build, verification and launch discipline

- `build_t5.py` writes every case from one recipe; `check_t5_mesh.py` reads
  every `points` file and refuses on the contract's geometry, first-layer and
  region-interface conditions **before any solver runs**; its planted-positive
  test (an inverted grading) must FIRE.
- `checkMesh` birth certificate per case (Charter §9), aspect ratios reported
  with their numbers.
- Geometric constants and cell counts are **READ from
  `constant/*/polyMesh/points`**, never inferred from the generator's inputs
  (T1c's 9 % `D/2` error; L-142's 210×-too-thick wall cell that every link of
  the build chain quoted as correct).
- Solver libraries are inserted with an **assert, never replaced** — Standing
  Rule 14, `scripts/foam_libs.py` and `scripts/lint_foam_libs.py`, at **every**
  call site.
- Launch via `launch_t5.sh`: atomic `LAUNCH_LOCK`; refusal if any process holds
  a case as cwd (`readlink /proc/pid/exe`); refusal if any numeric time
  directory other than `0` exists (L-143). `run_one_t5.sh` detached with
  `setsid nohup`. Nothing in this rung kills a process.
- Completion under the **strict rule** (Standing Rule 4), including the age
  guard: every field at `endTime` newer than the case's own `0/T`.
  `mark_done_t5.py`; the comparator refuses without every marker.
- **Concurrency cap: 4 solver processes**, and this rung launches nothing until
  the supervisor says cores are free. 14+ of 16 are committed today.
- **Tooling disclosure, to be completed before the freeze.** If a smoke test of
  the `cpuCabinet` tutorial or of a `C`-sized case is run to confirm the
  dictionaries are accepted, it happens **in scratch, outside the run tree**,
  its fields are deleted, and it is disclosed here with what was readable:
  dictionary acceptance, field lists, measured throughput. **A measured
  throughput is exactly what §11 needs and it is not a result about `h`.**
  Nothing a verdict depends on may be readable before the freeze (Charter §2d).

---

## 16. Status

**DRAFT. NOT FROZEN. NOT COMMITTED. NOT BUILT. NOT RUN. Zero compute spent.**
No builder, no comparator, no mesh, no case; `verification/runs/T-family/T5_runs/`
does not exist and the `find` that establishes it is at the head of this file
with its UTC timestamp. **The primary is HELD and its sha256 re-verified on
disk; the reference *values* are NOT HELD and will not be until §10 runs, in the
order §10 fixes.** Reference-slot schema frozen here; values absent by design.

This file freezes on Sanaa's reading or on the supervisor's promotion. Until
then every INTERPRETATION in §13 is open, §11's ceiling arithmetic is the item
that most needs a decision, and **T5 is a plan, not a capability**
(`T_FAMILY_INDEX.md` §4).

---

# 16. PROMOTION RULINGS — every difference from the draft, named

**Supervisor's rulings, 2026-08-26, applied at promotion. Nothing above §16 has
been reworded; the two draft sentences that had to change are STRUCK AND
REPLACED HERE, in view, rather than edited in place.**

## 16.1 ⛔ B1 — `setsid nohup` is STRUCK. It would have FABRICATED `rc = 0` FOR A CRASHED SOLVER.

**Struck from §15:**

> ~~"…detached with `setsid nohup`. Nothing in this rung kills a process."~~

**Measured on this box, 2026-08-26, before the launcher was written:**

| invocation | rc |
|---|---|
| `timeout 5 bash -c 'exit 7'` | **7** — correct |
| `setsid timeout 5 bash -c 'exit 7'` | **0** — WRONG |
| `setsid nohup bash -c 'exit 7'` | **0** — WRONG |
| `timeout 5 bash -c 'kill -8 $$'` | **136** (SIGFPE, core dumped) |
| **`setsid timeout 5 bash -c 'kill -8 $$'`** | **0** — **A CORE DUMP REPORTED AS SUCCESS** |

`setsid` **forks** when it is not already a process-group leader: the parent exits
0 immediately while the child carries the real status into a new session where
nothing collects it.

> **THE LAST ROW IS THE ONE THAT MATTERS. A SOLVER THAT DIES OF A FLOATING-POINT
> EXCEPTION AND DUMPS CORE WOULD BE RECORDED `rc = 0` — A FALSE PASS ON THE
> LOAD-BEARING LIMB OF THE STRICT COMPLETION RULE, WITH NOBODY WATCHING.** T8's
> level `m` died exactly that way and returned an honest 136 **only because it was
> not launched under `setsid`.**
>
> **That is STRICTLY WORSE than K0d's absent STATUS, which at least produced an
> honest `NOT DONE`. A missing rc is a gap; a fabricated rc is a lie.**

**REGISTERED IN ITS PLACE** — `run_one_t5.sh`, adopting the architecture
`scripts/launch_k0f.sh` already proves rather than inventing one:

1. the caller starts the launcher, which **re-execs ITSELF ONCE under `setsid`**;
2. **the wrapper's own exit status is meaningless and is not used**;
3. the solver runs under `timeout` **in the wrapper's OWN FOREGROUND**, with no
   `setsid` between them, so **`$?` is genuinely the solver's**;
4. `capped = (wall_s >= timeout_s)` — an **independent witness** from the wall
   clock, which no dying process can forge by choosing its exit status;
5. **`exit "$RC"` as the last line**, so a foreground caller gets the truth too.

**`timeout --preserve-status` IS FORBIDDEN**, and the reason is measured:
`timeout --preserve-status 1 sleep 5` → **143**, and `timeout 5 bash -c 'kill -15
$$'` → **143**. Expiry and a genuine SIGTERM death become indistinguishable.

**DRIVEN, NOT ASSUMED — four arms against a fake solver:**

| arm | launcher rc | `STATUS` |
|---|---|---|
| solver dies SIGFPE, foreground | **136** | `rc=136 capped=0 note=KILLED_BY_SIGNAL_8` |
| clean exit | 0 | `rc=0 capped=0 note=clean` |
| cap expiry (`timeout 3`, solver sleeps 60) | 124 | `wall_s=3 timeout_s=3 **capped=1**` |
| **solver dies SIGFPE, DETACHED** | — | **`rc=136 capped=0 note=KILLED_BY_SIGNAL_8`** |

**The fourth arm is the proof**: detached, through `setsid`, the real status still
reaches `STATUS`. And an unreachable solver **REFUSES (`exit 2`) and writes NO
`STATUS`** — nothing ran, there is no rc, and inventing one would be back-dating.

## 16.2 ⛔ B2 — the libs guard is a `raise`, NOT a Python `assert`; and the WORDING COLLISION IS REFERRED, NOT RESOLVED

**Struck from §15:**

> ~~"Solver libraries are inserted with an **assert, never replaced** — Standing
> Rule 14"~~

**Rule 14's requirement is SEMANTIC** — *verify, then insert, never replace* — and
the word in the rule is not an instruction to use the Python keyword. **A Python
`assert` evaporates under `python3 -O`, so rule 14's guarantee would be removable
by an interpreter flag.**

**REGISTERED IN ITS PLACE:** every libs call site in this rung raises or
`sys.exit(2)`, at **every** call site (rule 14: *"a lesson is not applied until
EVERY call site asserts it"*), driven under `-O` in the selftest.

**⚠ THE WORDING COLLISION, FLAGGED FOR THE CHIEF AND NOT RESOLVED HERE.**
`CLAUDE.md` rule 14 says *"inserted with an **assert**"* while L-332 and this
territory's `-O` inventory say **no `assert` may carry a refusal, guard, control
or gate.** **Two standing rules point opposite ways on one word.** Resolving that
is not a lane's and not a supervisor's.

**And it is not hypothetical — measured at promotion:**
**`scripts/foam_libs.py` carries 22 `ast.Assert` nodes.** Read rather than
counted: **all 22 sit inside its `t_*` test functions** (`t_absent`, `t_dup`,
`t_merge`, `t_subdict`, `t_idem`, `t_nobanner`, `t_bracetrap`), and its **runtime**
path raises a real exception — the tests assert on `str(exc)`.

> **So rule 14's RUNTIME guarantee is intact, and its VERIFICATION BATTERY is not
> `-O`-safe. Under `-O` the battery passes silently, so a regression introduced
> under that flag would clear its own tests.** This is `analyse_t8.py` §4e.4's
> shape with the halves swapped. **`scripts/` is shared territory and this rung
> repairs nothing there — it is reported.**

## 16.3 INTERPRETATION 1 — ADOPTED: the small ladder, `y+` 2.6 / 1.6 / 1.0

**Ruling, in the supervisor's words:** *fixing the first layer and refining
tangentially produces **a triple that does not contain the wall-normal
discretisation error, so its GCI understates the very thing it reports.***

> **A LADDER THAT HIDES THE ERROR IT IS MEASURING IS WORSE THAN A COARSE LEVEL AT
> `y+` 2.6.**

### 16.3.1 THE CONDITION, AND IT IS NOT OPTIONAL — a `y+` gate that CAN FAIL, on EVERY wall

**Registered:** `YPLUS_WALLS` = **`cube_front`, `cube_top`, `cube_rear`,
`cube_side_n`, `cube_side_s`, `floor`, `roof`` — seven walls, the five cube faces
plus the floor **and the roof**.

| clause | registered value | failure |
|---|---|---|
| sublayer bound, every wall | **`y+ ≤ 5.0`** | **`NOT A RESULT`** |
| level target | `c` 2.6 / `m` 1.6 / `f` 1.0 | — |
| ladder tolerance | achieved ≤ **2.0 ×** the level target | **`NOT A RESULT`** — the ladder is not the registered ladder |
| a wall not reported | — | **`NOT A RESULT`** — an unmeasured precondition is not a satisfied one |
| `yPlus.json` absent | — | **`NOT A RESULT`** |

**WHY EVERY WALL IS NAMED, AND IT IS A MEASUREMENT FROM TONIGHT:** T4's control C1
fired at `y+` **1.248 on the plate** while **the pipe wall sat at `y+` ≈ 30** under
low-Re wall functions, **and no registered gate could see it because C1 named only
the plate.**

> **A GATE THAT NAMES ONE WALL CERTIFIES ONE WALL.** Without a gate that can fail,
> *"2.6 is fine, it is inside the sublayer"* is an assertion with nothing behind
> it.

**The gate is exercised in the comparator's selftest by four arms** — compliant
set MET; **`roof` at 30 fires**; an **unreported** wall fires; an absent
`yPlus.json` fires.

## 16.4 INTERPRETATION 11 — ADOPTED: grade the FACE-AVERAGED set; mid-line becomes REPORTED

| rows | disposition |
|---|---|
| **G1a–G3a** face-averaged `h`, front / top / rear | **GRADED**, band **10.2 %** basis |
| **G1–G3** mid-line mean `h` | **REPORTED** — no longer graded |
| **G4** reattachment `x_R/H` | **REPORTED** — the thesis states no uncertainty |
| **G5a–c** mid-line mean `T_sur` | **GRADED** under the §3 identity guard |

> **A NARROWER BAND COMPUTED FROM A WORSE MEASUREMENT IS NOT A BETTER BAND.**

Fig. 5.39 is a five-series overlay *"whose digitisation increment alone is the size
of the experiment's stated uncertainty"* — **and a band whose digitisation
increment equals the experimental uncertainty is not a band.** The face-averaged
rows read **Fig. 5.45**, a linear-axis single-symbol plot, with the `√5` reduction
from five equal-area faces.

**G5 is the cleanest row in the rung and the record says so**: `0.4 °C` is a
**stated absolute accuracy** from printed p. 55, not a percentage inferred from a
figure.

## 16.5 INTERPRETATION 12 — ADOPTED: the `H_c` interface scheme is **TESTED**, not carried

T9a-D's own §2.5 says it does not cover a coupled fluid–solid interface, so
carrying its EXACT-tier A1 `PASS` across that boundary would be the extrapolation
this lab keeps catching. **Registered as an `H_c` twin at $0.04 derived — the best
value in the rung: $0.04 to test rather than assume.**

## 16.6 INTERPRETATIONS 2–10 — ADOPTED as drafted

**INTERPRETATION 9's 15 mK mixed-mean arithmetic is the model for the whole
document: it PRINTS THE NUMBER THAT MAKES THE DISTINCTION IRRELEVANT instead of
asserting that it is irrelevant.** INTERPRETATION 6's roof departure carries **I2
as the check that decides**, with a named fallback — a pre-decided disposition.
**INTERPRETATION 10 is accepted as a VISIBLE OMISSION costed at zero**: naming an
un-run row is worth more than quietly not mentioning it.

## 16.7 THE DIGITISATION UNCERTAINTY IS NOW **MEASURED**, and §7.3's estimate is superseded

**Struck from §7.3:** ~~"≈ 1.3 W/m²K on `h ≈ 55–80` → ≈ 2 %"~~ — self-described in
the draft as *"estimates made from the figures' axis resolution before any point
was taken."*

**REGISTERED IN ITS PLACE, from the planted raster control in `digitise_t5.py`:**

| | measured |
|---|---|
| `h` digitisation error, **MAX** | **`0.2263 W/m²K` = `0.2514 %` of the 0–90 span** |
| `h` digitisation error, RMS | `0.1374 W/m²K` |
| `Re_H` error, MAX | `7.07` = `0.1178 %` of span |
| planted / recovered | **6 / 6** |

**The control travels the SAME CHANNEL as the real artifact**, and the channel was
measured, not assumed: `pdfimages` on PDF page 162 gives **1926 × 2816, bpc = 1,
CCITT G4, 301 × 300 ppi**, and the render carries **3 grey levels with 99.988 % of
pixels exactly 0 or 255**. The control is rendered at **300 dpi**, skewed by the
measured **0.1006°**, dilated 1 px for ink spread, hard-thresholded to **1 bit**,
speckled at the measured **4.40 %** with areas 1–4 px from a fixed seed, and
round-tripped through **CCITT G4**.

**IT CAUGHT A Y-AXIS SIGN INVERSION ON ITS FIRST RUN** — planted `28.70` returned
as `61.37`, and `90 − 28.70 = 61.30` — **while the x axis recovered to 0.097 % of
span in the same run.** An x-only or count-only check would have passed a digitiser
that was wrong in y everywhere, **and the inversion would have entered the frozen
reference values.**

### 16.7.1 THE STATED LIMIT, registered beside the band and not in a footnote

**`0.2514 %` is the error of an ISOLATED marker.** The real Fig. 5.45 has series
that **overlap and touch** at low `Re_H`. **Marker overlap is the largest
un-modelled error source**, and it is un-modelled because modelling it honestly
means deciding what a merged blob's centroid *means* — a design decision, not a
measurement. **The band carries this as a floor, not a total.**

### 16.7.2 TWO UNCERTAINTIES, NAMED SEPARATELY, NEVER MERGED

| source | value | provenance |
|---|---|---|
| **EXPERIMENTAL** | **~5 %** local `h`, mid-region of the **five** faces; **~10 %** at edges | Meinders printed p. 59, **read from the rendered page image**, not OCR. **Both are hedged in the source** — *"approximately"*, *"about"* |
| **DIGITISATION** | **`0.2514 %` of span**, MAX | measured, §16.7 |

**They are combined only by the rule §7.3 registers, and both components are
printed beside every band.** An uncertainty absorbed into another is an
uncertainty nobody can audit later.

## 16.8 §14's CERTIFICATE FINDINGS — ACCEPTED IN FULL, INCLUDING THE ONE AGAINST THE TEMPLATE

- **G4 is `REPORTED`, so under template rule 1 T5 CANNOT add the `recirculation`
  line.** Accepted, flagged, **not finessed.**
- **`DC_CERTIFICATE_TEMPLATE.md` §4 names T5 for the `inlet temperature` class and
  T5 CANNOT BACK IT** — a single isolated cube has no upstream heated neighbour,
  and the thesis's own adiabatic-reference machinery exists for the array
  chapters.

> **That is a correction to a template written under Sanaa's H-6 directive, so it
> goes to HER DESK with the supervisor's recommendation: correct §4 to name the
> row / tandem / 4×4 rung instead.** H-6 exists so the product artifact grows
> *with* the validation — **a spec that named a rung for a class that rung cannot
> back is precisely the failure it was written to prevent, and finding it BEFORE
> the solve is the directive working.** **NOT SENT** (rule 7).

## 16.9 THE FREEZE SET

| path | blob at this commit | role |
|---|---|---|
| `docs/campaigns/T-family/T5_PREREGISTRATION.md` | *(this file)* | the registration |
| `verification/runs/T-family/T5_runs/digitise_t5.py` | `e55d6208c511` | **produces the reference** |
| `verification/runs/T-family/T5_runs/analyse_t5.py` | `17703b78dad5` | the comparator — the only thing that writes a verdict |
| `verification/runs/T-family/T5_runs/run_one_t5.sh` | `313df45c85b3` | the launcher |

**All four land in ONE commit**, so the freeze binds the whole grading path at the
same instant. **`build_t5.py` is NOT in this set and is NOT written**: no case has
been built, and a builder frozen before it exists would be a freeze over nothing.
**It is registered as owed before any case is armed.**

## 16.10 INSTRUMENT DISCIPLINE, verified at the freeze

- **zero `ast.Assert` nodes** in `analyse_t5.py` and `digitise_t5.py` —
  `scripts/check_assert_guards.py --require-clean` returns `CLEAN`;
- `analyse_t5.py` **selftest: 16 arms, 0 FAILED, rc 0 under BOTH `python3` and
  `python3 -O`**, with the **one-way gate refusal DRIVEN under `-O`** and required
  to return rc 2 — shown to *fire*, not merely shown not to crash;
- `digitise_t5.py` **selftest: 3 arms, 0 FAILED**, both interpreters, with the
  negative arm driving a **mis-anchored** figure under `-O` and requiring rc 2;
- **C2 is DIRECTIONAL** (`analyse_e4a2.py:308`'s registered `not growing`), never
  trend-over-spread — the selftest requires a **decaying** series to PASS, a
  growing one to FAIL, and **a plateau four decades above the floor to FAIL**;
- a **`P_MIN = 0.05`** floor on the observed order, added because the selftest
  found that a triple with an exact ratio of 1 computes `1.0000000000000002` and
  was classified `CONVERGING` with `p = 3e-16` — **a boundary decided by
  floating-point noise, producing a meaningless GCI.**

## 16.11 WHAT IS **NOT** DONE, AND IS OWED BEFORE ANY CASE IS ARMED

1. **`build_t5.py` does not exist.** No mesh, no case, no `0.orig/`.
2. **The reference values are NOT YET DIGITISED.** The digitiser is frozen and its
   error is measured; **Figs. 5.45, 5.37 and 5.39 have not been run through it**,
   and §7.6's reference slot is **schema only, values absent by design**.
3. **`scripts/check_case_provenance.py` and `scripts/check_launcher_can_launch.py`
   must both run against the built case before it is armed** — the first because
   T4 shipped a contaminated compressible template three times, the second because
   a frozen launcher can still be unable to launch.
4. **No solver has been launched and nothing is queued. Zero core-minutes.**

**`PENDING`. Nothing here has been sent, filed, submitted, uploaded, registered or
posted anywhere outside this box (`CLAUDE.md` rule 7).**

---

## AMENDMENT 1 — 2026-08-26 (PRE-FIRST-COMPUTE): the precursor launcher `run_one_t5_x2d.sh`; X_2d registered UNGRADED

**Document version 1.0 -> 1.1; 1.0 = the `0fcbb92e` freeze** (the frozen text carried no version line; this amendment declares the numbering). **Lines whose number changed above this section: 0.** Ruled by the heat-transfer supervisor `[lab-attributed]`, drafted by lane a442775b.

**Condition (`CLAUDE.md` rule 2), and how it was checked.** `verification/runs/T-family/T5_runs/` holds **no `STATUS.*` from a run and no `DONE.*`** (`ls` at commit time: zero of each at the tree root). The one STATUS-shaped file in the tree, `X_2d/STATUS.T5_X_2d` (`rc=0 end=2026-08-26T16:28:57Z`), **is a FALSE file written by cfd's queue runner for a launch the frozen launcher REFUSED** (`X_2d/log.launch`: `REFUSE: no 0/**/T, so the age guard has no datum`); no solver started. It is **bookkeeping only, EXCLUDED from every completion judgement, left in place undeleted**. `mark_done_t5.py` driven against it returns `NOT DONE X_2d: ... no log.solve` (rc 1) and writes no marker; its rule requires `End`, last time = endTime, fields and the age guard regardless of `rc`. **Zero core-minutes have been spent on this rung.**

**What changes.** A NEW file `run_one_t5_x2d.sh` launches the X_2d precursor only. It is line-for-line the frozen `run_one_t5.sh` (blob `313df45c`, untouched) with the age-guard datum `0/**/T` replaced by **`0/**/U`**, because a `simpleFoam` precursor carries no `T`. Diff against the frozen file, changed lines only: `AGE_DATUM="$(find "$CASE_DIR/0" -name T ...)"` -> `-name U`; the refusal text `no 0/**/T` -> `no 0/**/U`; plus a header comment. Nothing else moves.

**X_2d is UNGRADED.** It produces the inflow profile (§5.3) and the I1/I2 check rows; nothing a verdict depends on is readable from it (Charter §2d), so it may run before the reference values are fixed (§10's order concerns the graded cases).

---

## AMENDMENT 2 — 2026-08-26 (PRE-FIRST-COMPUTE): every 3-D case runs SERIAL; §11's `nProcs 4 / 8` superseded visibly

**Document version 1.1 -> 1.2. Lines whose number changed above this section: 0.** Ruled by the heat-transfer supervisor `[lab-attributed]` (F15 Ruling 2: a ladder differs only in mesh), drafted by lane a442775b. **Condition:** as AMENDMENT 1 — no `STATUS.*` from a run, no `DONE.*`, zero core-minutes; the runner's false `X_2d/STATUS.T5_X_2d` remains in place, excluded. Housekeeping disclosed: `X_2d/0`, armed from `0.orig` by the refused launch and verified byte-identical to `0.orig` (`diff -r`), was removed so the case can be armed again; no solver output existed.

**Superseded, not deleted** — §11: *"`nProcs = 4` for `C`, `M` and the arms; `nProcs = 8` for `F` if eight cores are free at launch, else 4"* and *"Parallel efficiency 0.85 assumed on 4 ranks (`scotch`)"*. The frozen launcher `run_one_t5.sh` (313df45c) runs the solver in its own foreground with no `mpirun`; `--ranks` scales only `timeout_s` and the `core_min` it writes, so a `--ranks 4` launch would record a fabricated four-fold cost for a one-core run.

**Registered in their place.** `C`, `M`, `F`, `P_m`, `L_m`, `S_m`, `H_c` run at **ranks = 1**; core-minutes unchanged (Model B, §11.1); wall = core-minutes; `--timeout` = per-case guard (3× Model B, §11.3) × 60 / 1:

| case | Model B core-min | cap 3× core-min | timeout s (ranks 1) |
|---|---|---|---|
| X_2d | 26.4 | 79.2 | 4752 |
| T5_CUBE_c, H_c | 45.6 | 136.8 | 8208 |
| T5_CUBE_m, P_m | 530.4 | 1591.2 | 95472 |
| L_m | 371.4 | 1114.2 | 66852 |
| S_m | 489.0 | 1467.0 | 88020 |
| T5_CUBE_f | 2308.2 | 6924.6 | 415476 |

The critical-path wall for `F` becomes 38.5 h under Model B and 105.6 h under Model A (against §11.1's 4.8 h / 13.2 h on 8 ranks). `CASE.txt` `registered_nProcs` lines and `build_t5.py`'s case table now say 1; `system/decomposeParDict` files are inert.

---

## AMENDMENT 3 — 2026-08-26 (PRE-FIRST-COMPUTE): `YPLUS_WALLS` on the half domain — **PROPOSED, NOT ADOPTED**

**Document version 1.2 -> 1.3. Lines whose number changed above this section: 0.** Condition as AMENDMENT 1 (no run STATUS, no DONE, zero core-minutes; the false runner file excluded). Drafted by lane a442775b on the supervisor's triage; **the supervisor's read of the diff, required before it is believed, could not be obtained in-session (the lane's messages to the supervisor did not deliver), so the frozen `analyse_t5.py` (blob `17703b78`) is UNCHANGED.**

**Proposed change**, held as `verification/runs/T-family/T5_runs/analyse_t5.A3_PROPOSED.py` (blob `9c2c1d44`): `YPLUS_WALLS` drops `cube_side_s`, which names a patch that does not exist on the registered half domain (§5.2, symmetry at `z/H = 0`). The set becomes the actual wall-patch set read from the built case's `constant/air/polyMesh/boundary` at `b98f3930`: `cube_front cube_top cube_rear cube_side_n floor roof`. Diff, changed lines only: line 48 `"cube_side_n", "cube_side_s", "floor", "roof")` -> `"cube_side_n", "floor", "roof")`, plus a six-line comment. No threshold, band or logic moves; selftest 16 arms, 0 FAILED under `python3` and `python3 -O`. **Until adopted, §16.3.1's "a wall not reported -> NOT A RESULT" fires on every level by construction.**

---

## AMENDMENT 4 — 2026-08-26 (PRE-FIRST-COMPUTE): the configuration contradiction, disclosed

**Document version 1.3 -> 1.4. Lines whose number changed above this section: 0.** Condition as AMENDMENT 1. Ruled by the heat-transfer supervisor `[lab-attributed]`.

`docs/campaigns/T-family/T5_CONFIGURATION_RULING.md` (2026-08-25) ruled T5 onto the Meinders **matrix** (`S_x/H = S_z/H = 4`, one periodic cube, `Re_H = 3854`, Figs 8.23/8.24/8.26). This file, frozen 2026-08-26 at `0fcbb92e`, registers the **single cube** at `Re_H = 4440` (Figs 5.45/5.37/5.39, channel with an X_2d precursor). The two documents contradict each other and neither is rewritten. **Ruling: the frozen single-cube registration stands for T5; the matrix becomes a separate rung, `T5m`, with its own pre-registration when written.** The ruling's binding constraints that survive here are the ones this file already carries independently: `r = 1.6` does not move, no dimensional local-`h` gate near an edge, two error channels never summed.

---

## AMENDMENT 5 — 2026-08-26 (PRE-FIRST-COMPUTE): mesh quality — expectation, not precondition; the mismatch disclosed

**Document version 1.4 -> 1.5. Lines whose number changed above this section: 0.** Condition as AMENDMENT 1. Ruled by the heat-transfer supervisor `[lab-attributed]`, established by lane a442775b from the frozen text, quoted:

- §5.4: *"`checkMesh` birth certificate on every case (Charter §9). Near-wall aspect ratios of order 30–70 are **expected** on a wall-resolved 3D mesh and are **reported with their numbers, not hidden**. `check_t5_mesh.py` reads every `points` file and refuses before any solver runs; **its planted-positive test (an inverted grading) must FIRE** or the build stops."*
- §15: *"`checkMesh` birth certificate per case (Charter §9), aspect ratios reported with their numbers."*

**No clause registers "Mesh OK" or an aspect-ratio bound as a launch precondition.** The only registered mesh precondition is `check_t5_mesh.py` with its planted positive, and it passes on every built case (first layers 0.128 / 0.080 / 0.050 mm read back on all six named walls; planted inverted grading fires under both interpreters). **Disclosed against the expectation:** the built air regions report max aspect ratio **133.2 / 135.2 / 140.4** (c / m / f) and `checkMesh -allGeometry` flags small-determinant cells (**4406 / 15727 / 59818**, "Failed 1 mesh checks"); non-orthogonality 0, skewness ~1e-13; epoxy regions "Mesh OK". The aspect ratio is the near-wall cell (0.128 mm) against the streamwise/spanwise spacing of the block lattice; halving it would need a first layer of ~0.26 mm at level `c` (`y+` ≈ 5, the sublayer bound of §16.3.1, i.e. NOT A RESULT) or roughly 2× the tangential counts (≈ 4× the cells, outside §11's ladder). **The cases proceed as built; every `y+` is measured per wall and printed beside every row.**

**AMENDMENT 3 — FROZEN 2026-08-26.** The supervisor's personal diff read: blob `9c2c1d44` differs from `17703b78` only by dropping `"cube_side_s"`, and `cube_front / cube_top / cube_rear / cube_side_n / floor / roof` all exist on the built air mesh (`cube_side_s`: 0 faces). `analyse_t5.py` is now blob **`9c2c1d44`** (selftest 16 arms, 0 FAILED under `python3` and `python3 -O`, re-run before the freeze); `analyse_t5.A3_PROPOSED.py` deleted. §16.9's freeze-set row for the comparator reads `9c2c1d44` from this commit.

---

## AMENDMENT 6 — 2026-08-26 (PRE-FIRST-GRADED-COMPUTE): the S5.3 map reader repaired; launch mechanics under the queue runner ruled

**Document version 1.5 -> 1.6. Lines whose number changed above this section: 0.** Disclosure only: no gate, band, threshold, cap or label moves. Ruled by the heat-transfer supervisor `[lab-attributed]` after a personal read of the diff; drafted by the T5 lane. **Condition (`CLAUDE.md` rule 2), and how it was checked:** the only compute on this rung is the UNGRADED precursor `X_2d` (AMENDMENT 1), DONE under the strict rule at 16:58:41Z (`T5_runs/STATUS.X_2d`: rc=0, wall 313 s, 5.217 core-min; `DONE.X_2d`); no graded case has been armed — `ls` of `T5_CUBE_c H_c T5_CUBE_m P_m L_m T5_CUBE_f` at this write shows `0.orig` and no `0/` or numeric time directory in any of them; no `STATUS.*` and no `DONE.*` exists for any graded case at the `T5_runs` root; nothing a verdict depends on has been read (the map touches no `h`). The runner-written `X_2d/STATUS.T5_X_2d` remains the false bookkeeping file of AMENDMENT 1, excluded.

**(a) The map reader.** `verification/runs/T-family/T5_runs/map_inflow_t5.py` (blob `ade7b753`, committed `c0da599a`; **NOT in the S16.9 freeze set**, an owed instrument) REFUSED on `DONE.X_2d`, rc 2, verbatim: `REFUSED: sample files missing for station 8: /home/ubuntu/Certonomous/verification/runs/T-family/T5_runs/X_2d/postProcessing/t5InflowSample/5000`. Cause, measured: `postProcess -func t5InflowSample -time 5000` completed (rc 0, `End`) and openfoam-2606's `sets` writer emits ONE raw file per station, `L<s>_k_omega_U.xy` (34 files, 400 rows x 6 columns `y k omega Ux Uy Uz`); the committed reader expected two files per station (`L<s>_U.xy`, `L<s>_k_omega.xy`). **Repair: the reader now opens the single combined file, refuses unless every row carries exactly 6 columns, and splits it into the `U` (y, Ux, Uy, Uz) and `k/omega` (y, k, omega) rows the unchanged arithmetic consumes. Changed lines: the station loop of `sample()` only (20 lines); plane selection, the three registered refusals (no `DONE.X_2d`; 660 outside the sampled range; plane within 2 H of inlet/outlet), `re_theta()`, `write_boundary_data()` and the log are byte-unchanged; 0 `ast.Assert`.** Blob in force: **`dc2b4f74`** (was `ade7b753`). Driven before adoption in a scratch copy of `X_2d` with `--dry-run`: `Re_theta crossing x/H=63.790; plane x_p/H=55.790; mapped station x/H=56 (Re_theta 592.1)`; the in-tree run appends its iteration to the registered log `T5_INFLOW_LOG.md` when it executes (see `LAUNCH_RECORD.md` for when that was).

**(b) Launch mechanics under the queue runner (`docs/standards/QUEUE_RUNNER.md`).** S15's *"Launch via `launch_t5.sh`"* is **superseded visibly for runner launches**: the runner's fixed form `setsid nohup bash -c 'cd <cwd> && <argv> ...'` makes both that wrapper and `launch_t5.sh` itself hold the case directory as cwd, so `launch_t5.sh` guard G2 refuses every runner launch by construction; and the frozen launcher's self-detaching mode returns in ~1 s, which would hand the runner a `launcher_rc=0` before any iteration (the F8 shape, `LAUNCH_RECORD.md`) and blind its cap watch. **Registered in its place: every graded case is enqueued with the argv `run_one_t5.sh --case-dir <case> --timeout <s> --ranks 1 --solver chtMultiRegionSimpleFoam --no-detach`, with `<s>` from AMENDMENT 2's table (C, H_c 8208; M, P_m 95472; L_m 66852; F 415476), the runner supplying the detachment.** `--no-detach` is a documented option of the frozen `run_one_t5.sh` (blob `313df45c`, untouched): the solver still runs in the wrapper's own foreground under `timeout`, `capped` is still read from the wall clock, the rc is still captured in-wrapper into `T5_runs/STATUS.<case>` and carried by `exit "$RC"` (S16.1 arms 3–5 unchanged); the runner's `<case>/STATUS.<case_id>` remains an infrastructure record of the launch argv's exit and is never the solver's rc (L-342). `launch_t5.sh` remains the gate for any hand launch, which this rung does not use while the runner is live. Nothing here kills a process.

**Not done by this amendment:** the digitiser (S16.11 item 2) is untouched — a later amendment on it is numbered 7; `analyse_t5.py` stays blob `9c2c1d44`; `run_one_t5.sh` stays `313df45c`; every band, floor and gate of S7 stands.
