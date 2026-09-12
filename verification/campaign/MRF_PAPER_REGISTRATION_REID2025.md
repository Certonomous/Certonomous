# MRF — REGISTRATION OF Reid, Rossi, Cottini & Benassi (2025), arXiv:2508.03176

**STATUS: REGISTRATION OF A REFERENCE, NOT A GATE FREEZE.** This document records
what an external paper says, what of it transfers to our tank and what does not,
and it **supersedes the earlier `Np ∈ [4.0, 6.0]` band instruction**. It does not
by itself re-open, re-grade or re-freeze any pre-registration: the R1 and R2
pre-registrations are struck-and-legible by dated amendment at their own feet
(CLAUDE.md rule 6), not rewritten here. **No compute was run to produce this
document** — every one of our numbers is post-processing of fields already on
disk from the R2 `ET8000` tree.

- **Authority:** `docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md` §addendum
  ~19:10Z, and her clarification the same evening relayed by the cfd-supervisor:
  *"It might be that we dont have exactly the same dimensions as them in which
  case we dont need to get the same values, but i want all the results in there
  presented for our case. And the paper registered."*
- **Paper:** `docs/papers/CFD_simulation_rushton.pdf`, sidecar
  `docs/papers/CFD_simulation_rushton.txt` (written with this registration).
- **Our case:** `cases/navier_class/MRF/`, run tree
  `verification/runs/navier_class/MRF/R2/ET8000/`.
- **Our parity outputs:** `verification/runs/navier_class/MRF/R2/PAPER_PARITY/`.

---

## 1. Title-page verification (CLAUDE.md rule 15 / L-144) — DONE

Page 1 of the PDF was **rendered to an image and read**, not identified by file
name, file type or checksum. It carries, as printed: *"CFD simulation of a
Rushton turbine stirred-tank using open-source software with critical evaluation
of MRF-based rotation modeling"*; Alfred Reid, Riccardo Rossi, Ciro Cottini,
Andrea Benassi; Red Fluid Dynamics / Chiesi Farmaceutici / SISSA;
`arXiv:2508.03176v1 [physics.flu-dyn] 5 Aug 2025`. That is the paper the
directive names. sha256 of the PDF, recorded for later re-identification only
and **not** used as the identification: `9d28d6971a7bdaf7b1bcfeb230af16bf088afe47739b80137b251b139b18220e`.

---

## 2. WHAT THE PAPER REGISTERS — its own numbers, and where each one comes from

### 2.1 MRF zone diameter and thickness (the directive's item 1)

| zone | diameter | thickness | source |
|---|---|---|---|
| Zone 1 | **1.10 D** | **1.55 W** (W = blade width = D/5, so 0.31 D) | §3.3.1, sidecar "five different zones are compared with diameters of 1.10D, 1.26D, 1.49D, 1.70D and 1.93D with a constant thickness of 1.55W" |
| Zone 2 | 1.26 D | 1.55 W | same |
| Zone 3 | 1.49 D | 1.55 W | same |
| Zone 4 | 1.70 D | 1.55 W | same |
| Zone 5 | 1.93 D | 1.55 W | same |
| Zone 6 | 1.10 D | **3.1 W** (0.62 D) | §3.3.1, "comparing Zone 1 to Zone 6, which have the same diameter but respective thicknesses of 1.55W and 3.1W" |

Zone 1 is described as *"slightly greater than the volume swept by the impeller"*.

### 2.2 y+ per surface (the directive's item 1)

- Final (fine) mesh, **average over blades, tank and shaft surfaces: y+ ≈ 4.13**.
- **On the blades only: average y+ = 7**, maximum ≈ **35** near the blade edges,
  minimum ≈ **0.1** near the baffle recirculation zones.
- Their Table 1, per mesh, over all solid surfaces:

| mesh | coarse | medium | fine |
|---|---|---|---|
| max element size (mm) | 7 | 5 | 4 |
| min element size (mm) | 0.44 | 0.31 | 0.25 |
| cells (million) | 1.51 | 3.33 | 5.76 |
| min y+ | 0.13 | 0.11 | 0.07 |
| **average y+** | **6.5** | **5.1** | **4.1** |
| max y+ | 55.3 | 39.9 | 29.9 |

Wall treatment: y+-insensitive wall functions (`kqRWallFunction`,
`omegaWallFunction`, `nutUWallFunction`), k-ω SST, `simpleFoam`, OpenFOAM ESI
v2206.

### 2.3 The Np band (the directive's item 1) — and the one thing about it a reader must know

Their Table 2, the **mesh family**:

| grid | coarse | medium | fine | medium-vs-fine |
|---|---|---|---|---|
| **Np (-)** | **5.46** | **5.44** | **5.49** | 0.9 % |
| Ig (%) | 13.70 | 13.61 | 13.33 | 2.2 % |
| I (%) | 6.18 | 6.29 | 6.34 | 0.8 % |

**REGISTERED BAND: `Np ∈ [5.3, 5.6]`**, from that family, as the directive
instructs. **The Rushton/Costich/Everett (1950) correlation plateau value
`Np ≈ 5.0` is registered as a SECONDARY reference only**, not as the anchor.

Three facts about this band are registered **with** it, because a reader who
quotes it without them will quote it wrongly:

1. **It is a CFD-to-CFD band, not an experimental one.** The paper reports **no
   measured power number at all**; a text search of the whole sidecar for a
   reference, correlation or experimental Np returns nothing. Its external
   experimental anchor is Wu & Patterson (1989) **velocity and TKE**, not power.
2. **All three values in it were computed with Zone 1 — the paper's SMALLEST MRF
   zone, 1.10 D** (sidecar, §3.1: *"The base MRF zone used for the mesh
   sensitivity study and for the turbulence model comparison is the Zone 1"*).
   The band is therefore a **1.10 D-zone band**, not a general one. The paper's
   own Fig. 12 gives, as **printed data labels on the bars** (so: printed
   values, not digitised, ±0.05 rounding): Np = **5.4, 6.2, 6.3, 6.3, 6.1** for
   Zones 1 to 5. **At every zone larger than 1.10 D the paper's own Np is ABOVE
   the registered band.**
3. **The triple 5.46 → 5.44 → 5.49 is not monotone.** Under this lab's rule 5 it
   is an `OSCILLATORY` triple, and no Richardson order or GCI may be quoted from
   it. It is a **scatter band across three meshes**, which is how it is
   registered here, and never a converged value with an uncertainty.

### 2.4 The other quantities the paper defines

- `Np = P/(ρN³D⁵)`, `P = 2πMN`, torque `M` by integrating pressure + viscous
  force over the **impeller blade surfaces** (their method 1 of three).
- Agitation index `Ig = Û/Utip × 100`, `Utip = πND`, `Û` the spatially averaged
  mean velocity.
- Turbulence intensity `I = u'/Û × 100`, `u' = sqrt(2k/3)`.
- Profiles: **circumferentially averaged from 0° to 350° in 10° steps**, at
  r = 5, 6 and 7 cm from the shaft, over a vertical extent 2.5 W, plotted
  against `2z/W`; velocities normalised by `Utip`, TKE by `Utip²`.
- Wu & Patterson uncertainty, as the paper states it: **4 % on velocity, 15 % on
  turbulent kinetic energy**.

**A DEFINITIONAL AMBIGUITY IN THE PAPER, REGISTERED RATHER THAN RESOLVED
SILENTLY.** Their eq. 19 writes `I = u'/Û`, i.e. normalised by the **mean
velocity**. Their Table 2 then reports `I ≈ 6.2–6.3 %` alongside `Ig ≈ 13.3–13.7 %`.
Taking both at face value gives `u' = 0.0634 × 0.1297 = 0.0082 m/s`, hence a
whole-tank `k̄/Utip² ≈ 1.1e-04` — **two to three orders below the `k/Utip²` of
0.01 to 0.07 their own Fig. 16 plots near the impeller**, which is not credible
for a volume average. Reading `I = u'/Utip` instead gives
`k̄/Utip² ≈ 6.0e-03`, which **is** consistent with their Fig. 16 and with our own
measured `5.1e-03`. **Both readings are therefore computed for our case and both
are reported**; only the tip-speed reading reconciles the paper with itself, and
that is recorded as our reading of their ambiguity, not as their statement.

---

## 3. THE SIMILARITY QUESTION — and it is a finding, not a formality

The directive calls this paper *"our exact geometry"*. **On the numbers it is
not.** Every ratio below is computed from artifacts on disk: ours from
`cases/navier_class/MRF/mesh/generate_geometry.py` lines 21–38 and
`verification/campaign/MRF_R1_PREREGISTRATION.md` §4; theirs from the paper's
§2.1 and the dimension labels on its Fig. 1.

| ratio | ours | Reid 2025 | ours / theirs |
|---|---|---|---|
| T/D | 3.0000 | 2.9032 | 1.033 |
| C/D | 1.0000 | 0.9677 | 1.033 |
| H/T | 1.0000 | 1.0000 | 1.000 |
| blade L/D | 0.2500 | 0.2500 | 1.000 |
| blade W/D | 0.2000 | 0.2000 | 1.000 |
| disc diameter / D | 0.7500 | 0.7742 | 0.969 |
| shaft diameter / D | 0.2000 | 0.1613 | 1.240 |
| **baffle width / D** | **0.3000** | **0.1000** | **3.000** |
| **blade & baffle thickness / D** | **0.0400** | **0.0100** | **4.000** |
| number of baffles | 4 | 4 | 1.000 |
| Re = N D²/ν | 5.00e4 | 2.883e4 | 1.734 |
| Utip = πND (m/s) | 1.5708 | 0.9729 | 1.615 |

**THE TWO TANKS ARE NOT GEOMETRICALLY SIMILAR.** Impeller, clearance, fill
height and blade aspect transfer to within 3.3 %. **Baffle width and blade
thickness do not**: our baffles are **three times wider relative to D** and our
blades, disc and baffles are **four times thicker relative to D**.

Two caveats on that last row, both disclosed:

- **The paper contradicts itself on thickness.** Its Fig. 1 labels the blade,
  disc and baffle thickness **D/100**; its body text at *"For the blades, disc
  and baffles thickness, there is no standard value in the literature but T/100
  has been used"* says **T/100**. Under the figure reading we are **4.0×**
  thicker; under the text reading, **1.38×**. Both are recorded; neither is
  chosen. **We are thicker either way.**
- Blade thickness and baffle width are both documented first-order drivers of a
  Rushton `Np` in the mixing literature (thicker blades lower it; baffling
  raises it toward the fully-baffled plateau). **No such source is on this box
  and none is cited here as a measurement.** The *direction* is stated as
  background; the *magnitude* is **NOT REGISTERED** and would need its own
  title-verified reference or its own solve.

### 3.1 What this means for band transfer — the per-quantity call

Sanaa's clarification removes the requirement to match and replaces it with the
requirement to present. So the band is registered **per quantity**, and each
quantity carries its own match / no-match call:

| quantity | geometry match? | band registered? |
|---|---|---|
| `Np` | **NO** — baffle width 3×, blade thickness 4× (or 1.4×), both first-order for `Np` | **NO BAND.** `Np ∈ [5.3,5.6]` is recorded as **context, not a gate**, and our value is reported beside it with the difference stated in per cent |
| `Ig` (agitation index) | partial — a velocity-scale quantity, normalised by `Utip`; the drivers that break `Np` act on it far more weakly | context band 13.3–15.4 % across their zones; **no gate** |
| `I` (turbulence intensity) | partial, and the definition is ambiguous (§2.4) | context only; **no gate** |
| velocity profiles at matched `r/D` | **partial** — impeller and station geometry match; baffle/thickness differ | Wu & Patterson LDA with their stated **4 %** is the honest external reference; **no gate registered tonight** |
| TKE profile at matched `r/D` | partial, as above | Wu & Patterson LDA with their stated **15 %**; **no gate registered tonight** |
| y+ per surface | **NO** — a deliberate design difference: they resolve (`y+ ≈ 4`), we wall-function (`y+` 26–60) | no band; reported per patch as a fact |
| MRF zone diameter / thickness | comparable, both in units of D and W | no band; registered as a **parameter with a sensitivity** (§5) |

**What would falsify the transfer assumption if anyone ever did register the
band as a gate:** a solve of **our** geometry with the blade/baffle thickness cut
to `D/100` and the baffle width cut to `D/10`, holding everything else, landing
`Np` inside 5.3–5.6. That is the experiment; it has not been run, and until it
is, `Np` band transfer stays **unregistered**.

---

## 4. OUR NUMBERS, AND THE HONEST GRADE OF 4.38

All values from `verification/runs/navier_class/MRF/R2/PAPER_PARITY/PAPER_PARITY_RESULTS.json`,
computed from `…/R2/ET8000/<level>/8000/` under a **planted-zero control that
passed on all three readers** (planted 1.234e-03; volume-average reader, profile-k
reader and profile-velocity reader each recovered it to 1e-17).

| quantity | coarse | medium | fine | Reid 2025 (fine, Zone 1) |
|---|---|---|---|---|
| cells | 154,715 | 601,696 | 2,418,780 | 5,760,000 |
| base cell (mm) | 10.00 | 6.28 | 3.90 | 4 |
| min cell (mm) | 0.78 | 0.45 | 0.27 | 0.25 |
| **Np** | **4.194** | **4.281** | **4.382** | **5.49** |
| **Ig (%)** | **14.90** | **14.80** | **14.65** | **13.33** |
| **I = u'/Utip (%)** | **4.63** | **5.37** | **5.83** | **6.34** |
| I = u'/Û (%) | 31.07 | 36.28 | 39.79 | — (see §2.4) |
| k̄/Utip² | 3.22e-03 | 4.33e-03 | 5.10e-03 | ≈6.0e-03 (implied) |
| mean y+, all walls | 59.5 | 39.7 | 25.9 | 4.1 |
| liquid volume (m³) | 0.020936 | 0.020929 | 0.020931 | — |

### 4.1 THE GRADE — said plainly, because the old line would mislead a reader

> **Under the superseded band `Np ∈ [4.0, 6.0]`, our fine-level `Np = 4.38` was
> INSIDE the band. Under the band registered here, `Np ∈ [5.3, 5.6]`, it is
> 17.3 % to 22.0 % LOW and CLEARLY OUTSIDE IT.**

(4.382 against 5.3 is −17.3 %; against 5.6, −21.8 %; against their fine 5.49,
−20.2 %.) A reader of the old line would believe we had a passing number. **We
did not, on the reference that now stands.**

**THE VERDICT DOES NOT FLIP, AND NOT BECAUSE THE BAND CHANGED.** The R2 `ET8000`
row is **`NOT A RESULT`** and was already `NOT A RESULT` before any of this, for
two independent reasons that sit **above** any band under rule 5: the fine level
is graded **not iteratively converged**, and the grid triple
4.193 → 4.281 → 4.382 is **`DIVERGENT`** at observed order **−0.297**. Rule 5 is
one-way — a gate may only turn a result **into** `NOT A RESULT` — so the new band
changes the honest description of the number and changes **nothing** about the
verdict. Artifact: `…/R2/ET8000/MRF_R2_GRADED_ROW_ET8000.json`.

**The per-cent figures above are therefore a DESCRIPTION OF AN UNGRADED NUMBER,
not a graded error.** They may be quoted as "our ungraded fine-level value sits
17–22 % below the paper's band"; they may not be quoted as an accuracy.

---

## 5. THE ZONE-SIZE MECHANISM — VERIFIED FROM DISK, AND IT DOES NOT EXPLAIN 4.38

**Our zone, read by this lane from the run's own dictionary**
(`verification/runs/navier_class/MRF/R2/ET8000/fine/system/topoSetDict`, and
identically in `cases/navier_class/MRF/R2/system/topoSetDict`):
`cylinderToCell`, `radius 0.060`, `point1 (0 0 0.080)`, `point2 (0 0 0.120)`.

- diameter **0.120 m = 1.200 D**
- axial extent **0.040 m = 0.400 D = 2.00 W**
- blade swept volume: r ≤ 0.050 (1.00 D), z 0.090…0.110 (1.00 W)

So our zone is **1.20 D in diameter and 2.00 W thick**. Against the paper's
family it sits **between Zone 1 (1.10 D) and Zone 2 (1.26 D)** in diameter, and
**between Zone 1 (1.55 W) and Zone 6 (3.1 W)** in thickness.

**THIS REFUTES THE MECHANISM THE BRIEF PROPOSED, AND THE REFUTATION IS THE POINT.**

1. **The paper recommends no 1.3–1.5 D zone.** The only range it names is
   *"Most studies reported in the literature use MRF regions with dimensions
   within those of Zone 3 and Zone 5"* — i.e. **1.49 D to 1.93 D**, and that is a
   description of the literature, not a recommendation. Its own conclusion runs
   the other way: the **smallest** zone gave the best turbulent kinetic energy
   prediction and the clearest double peak, and larger zones **manufacture**
   turbulence at the MRF interface. A "recommended 1.3–1.5 D" is not in the paper.
2. **Their Np RISES with zone diameter through exactly our zone size.** Fig. 12,
   printed labels: 1.10 D → 5.4, 1.26 D → 6.2. Our 1.20 D sits on the steep part
   of that rise. If their zone-size curve transferred at all, a 1.20 D zone would
   predict `Np` **at or above** the 5.3–5.6 band — **not 20 % below it**. The
   zone-size mechanism predicts the wrong sign of the error for our case.
3. **What the geometry table actually points at** is §3: baffles 3× wider and
   blades 4× (or 1.4×) thicker relative to D — both first-order `Np` drivers, and
   both large. **That is a hypothesis, not a finding**, and it is registered as
   the leading candidate to be tested, not as an explanation to be believed.

**A zone sensitivity is still worth running** — the paper's central result is
that zone size moves `Np` by >12 % and mixing time by a factor of three, and we
have never measured that sensitivity on *our* tank. It is drafted at
`cases/navier_class/MRF/R3/MRF_R3_ZONE_SENSITIVITY_DRAFT.md`, **NOT FROZEN AND
NOT LAUNCHED** — the freeze is the cfd-supervisor's check 4 and is not this
lane's to take.

---

## 6. MEASURED-TIER CHECKS ADDED (the directive's item 4)

Registered as **measured-tier checks**, computed and plotted, **ungated** until a
supervisor freezes a band for them:

- radial, tangential and axial velocity at **r/D = 0.538** (our 5.38 cm, the
  station matched to the paper's 5 cm), plus **0.645** and **0.753**, and the
  paper's **absolute** 5, 6, 7 cm for completeness;
- turbulent kinetic energy at the same stations, against Wu & Patterson (1989)
  LDA **digitised exactly from the paper's Fig. 16 vector paths**;
- **agitation index and mean turbulence intensity reported beside Np** in the
  table of §4 and in `figures/fig06_global_parameters.png`.

**A station caveat that matters.** The paper's r = 5 cm is `r/D = 0.538` — about
one blade width outside its blade tip. **Our blade tip is at exactly r = 5 cm**,
so the paper's *absolute* radius is our *tip circle*, not a discharge-stream
station. The matched station is `r/D = 0.538` → **r = 5.38 cm**, and that is the
one used for every comparison; the absolute 5 cm profile is plotted separately
and labelled as the tip circle.

**Sampling method, disclosed:** nearest-cell values at 36 azimuths × 101 heights
per station, circumferentially averaged exactly as the paper does (0° to 350° in
10° steps). Nearest-cell, **not** interpolated — which is why our curves are
visibly stepped where the paper's are smooth. The azimuthal standard deviation
over the 36 samples is plotted as a shaded band and is a real uncertainty channel
the paper does not report.

---

## 7. DIGITISATION PROVENANCE (the directive's honesty constraint)

| paper value used here | provenance |
|---|---|
| Np 5.46 / 5.44 / 5.49; Ig 13.70 / 13.61 / 13.33; I 6.18 / 6.29 / 6.34 | **TABULATED** — their Table 2 |
| mesh sizes, cell counts, y+ min/avg/max | **TABULATED** — their Table 1 |
| zone diameters 1.10–1.93 D, thicknesses 1.55 W / 3.1 W | **TEXT** — their §3.3.1 |
| Np 5.4/6.2/6.3/6.3/6.1, Ig 13.7/14.8/15.1/15.4/15.1, I 6.3/6.6/7.0/7.4/7.5 per zone | **PRINTED DATA LABELS on their Fig. 12** — printed, not digitised; uncertainty is rounding only, ±0.05 |
| Wu & Patterson LDA k/Utip² points and their Zone 1 curve | **DIGITISED** — and **exactly**, from the PDF's own vector path coordinates, not from pixels and not by eye; script `cases/navier_class/MRF/digitise_reid2025_fig16.py`, output `…/PAPER_PARITY/REID2025_FIG16_DIGITISED.json` |

The digitiser carries its own reader control: the axis calibration comes from the
tick-mark path coordinates in the same content stream, and **every recovered
error bar has a half-width of 15.0 ± 0.4 % of its own centre value** — which is
precisely the Wu & Patterson TKE uncertainty the paper states. The script
**exits 2** if any bar violates that. Eleven points were recovered; all eleven
passed.

---

## 8. WHAT IS NOT AVAILABLE FOR OUR CASE, AND WHY

Reported as **NOT AVAILABLE with the reason**, never estimated, never left as a
silent gap in a figure that has a slot for it:

| the paper's item | our status |
|---|---|
| Fig. 6, 7, 8, 9 — k-ε comparison | **NOT AVAILABLE** — no k-ε solve exists for this case; k-ω SST only |
| Fig. 11–14, 16–19 — the five-zone sweep | **NOT AVAILABLE** — one zone (1.20 D) solved; this is exactly what the §5 draft proposes to fix |
| Fig. 20, 21 — zone thickness sweep | **NOT AVAILABLE** — one thickness (2.00 W) solved |
| Fig. 22–25, Table 3 — passive-scalar mixing time | **NOT AVAILABLE** — no scalar transport run; would need a fresh registration and fresh compute |
| Fig. A1, A2 — blade angular sensitivity | **NOT AVAILABLE** — one frozen-rotor position solved; the position dependence is already a disclosed ungated uncertainty in the R1 pre-registration §4 |
| an experimental power number | **NOT AVAILABLE IN THE PAPER EITHER** — it reports none (§2.3) |

---

## 9. COMPUTE (rule 12)

**No solver ran.** All of this is post-processing of fields already on disk.
Measured cost: `postProcess -func writeCellCentres/writeCellVolumes` on three
levels plus the Python extraction and figures, **1 rank**, wall time under
25 minutes end to end ⇒ **under 25 core-minutes**, derived ≈ **$0.02** at
$0.0513/core-h — **derived, not measured**, the box cannot read its own billing.
No pre-registered estimate existed for a desk task, so **no estimate-vs-actual
calibration row is owed**; the row that IS owed remains the R2 solve's, at
`verification/runs/navier_class/MRF/R2/COST_CALIBRATION_ROW_PENDING.md`.

---

## 10. ARTIFACTS

| artifact | path |
|---|---|
| paper | `docs/papers/CFD_simulation_rushton.pdf` |
| sidecar (new) | `docs/papers/CFD_simulation_rushton.txt` |
| our parity numbers | `verification/runs/navier_class/MRF/R2/PAPER_PARITY/PAPER_PARITY_RESULTS.json` |
| our mesh table | `verification/runs/navier_class/MRF/R2/PAPER_PARITY/MESH_TABLE_OURS.json` |
| exact Fig. 16 digitisation | `verification/runs/navier_class/MRF/R2/PAPER_PARITY/REID2025_FIG16_DIGITISED.json` |
| figures | `verification/runs/navier_class/MRF/R2/PAPER_PARITY/figures/` |
| extraction script | `cases/navier_class/MRF/paper_parity_extract.py` |
| work-copy setup | `cases/navier_class/MRF/paper_parity_setup.sh` |
| figure script | `cases/navier_class/MRF/paper_parity_figures.py` |
| digitiser | `cases/navier_class/MRF/digitise_reid2025_fig16.py` |
| graded row this grades against | `verification/runs/navier_class/MRF/R2/ET8000/MRF_R2_GRADED_ROW_ET8000.json` |
| zone sensitivity draft (NOT FROZEN) | `cases/navier_class/MRF/R3/MRF_R3_ZONE_SENSITIVITY_DRAFT.md` |

---

## 11. DATED SECTION, 2026-09-12 (same day, later) — **THE `Np` DEFICIT IS QUANTIFIED, FROM AN EXPERIMENT AT OUR EXACT TANK RATIOS, AND OUR 4.38 MAY SIMPLY BE RIGHT FOR OUR TANK**

Appended, not inserted: **lines whose number changed above this section: 0.**

The cfd-supervisor asked, in writing, whether blade thickness explains the deficit
**quantitatively, from a source the box actually holds**, and instructed that
*"geometry differs"* must not be allowed to become an unfalsifiable excuse. At the
time of §3 the answer was **no source**. A retrieval was made and the answer is now
**yes**, with the evidentiary weight of each part stated separately.

### 11.1 The source, title-page verified

`docs/papers/stirred_tanks_and_mixing/beshay_2001_acta_polytechnica_impeller_power_input.pdf`,
sidecar `.txt` beside it. **Page 1 rendered and read** (rule 15): *"Power Input of
High-Speed Rotary Impellers"*, K. R. Beshay, J. Kratěna, I. Fořt, O. Brůha, **Acta
Polytechnica Vol. 41 No. 6/2001**, Czech Technical University Publishing House,
open access.

### 11.2 The measurement, and why it matters more than the correlation

Its **small test rig** (its Table 1, Table 3 and §2) is, ratio for ratio, **our
tank**:

| ratio | Beshay small rig | ours | match |
|---|---|---|---|
| T | 0.300 m | 0.300 m | ✔ |
| H/T | 1.0 | 1.0 | ✔ |
| baffles | 4 at b = 0.1 T | 4 at T/10 | ✔ |
| D | 100 mm | 100 mm | ✔ |
| D/T | 1/3 | 1/3 | ✔ |
| l/D (blade length) | 0.25 | 0.25 | ✔ |
| w/D (blade width) | 0.2 | 0.2 | ✔ |
| D₁/D (disc) | 0.75 | 0.75 | ✔ |
| blades | 6 | 6 | ✔ |
| clearance h/T | 0.33 | 0.333 | ✔ |
| Re | 3×10⁴ – 6×10⁴ | 5.0×10⁴ | ✔ inside |
| **t/D (thickness)** | **0.0155** (t = 1.55 mm) | **0.0400** (t = 4.00 mm) | ✘ **2.58×** |

**Measured power number, strain-gauge torquemeter: `Po = 5.41` at h/T = 0.33**
(5.44 at h/T = 0.5). Their stated scatter: average relative standard deviation
**2.3 % to 16 %**.

**Everything differs by one dimension, and it is the one §3 named.** This is the
controlled comparison that Reid 2025 could never be, because Reid's tank differs
in baffle width *and* T/D *and* thickness at once.

### 11.3 The correlation, labelled as secondary and extrapolated

Beshay's eq. (5) reproduces **Bujalski, Nienow, Chatwin & Cooke (1987)**,
*Chem. Eng. Sci.* **42**(2) 317–326:

    Po = 2.512 (t/D)^(-0.195) (T/T0)^(0.063),   T0 = 1 m

**Bujalski 1987 is NOT on this box.** The correlation is a **secondary-source
reproduction**, and **the source we hold does not state its range of validity in
`t/D`**. Our `t/D = 0.0400` may lie beyond the data it was fitted to. Its own
accuracy, on the rigs in the paper that carries it: **2–3 %** (6.2 vs 6.4; 5.3 vs
5.425).

| evaluation | result |
|---|---|
| at their `t/D = 0.0155`, T = 0.300 | Po = **5.248** vs their measured **5.41** → correlation is 3.1 % low |
| at our `t/D = 0.0400`, T = 0.300 | Po = **4.362** |
| **thickness factor 0.0155 → 0.0400** | **×0.8312, i.e. −16.9 %** |

### 11.4 THE ANSWER, WITH ITS SIGN AND ITS MAGNITUDE

Anchor on the **measurement**, correct only for the one dimension that differs:

> **5.41 (measured, our tank ratios) × 0.8312 (thickness factor) = `Np ≈ 4.50`.
> Our ungraded fine-level value is `4.382` — **2.6 % below that**, and on the low
> side, which is the documented direction of steady-MRF under-prediction that
> this case's own R1 pre-registration §3 predicted **before any compute**.**

Against the Reid band the same number is **17.3 % to 21.8 % low**. **The two
statements are both true and they are about different tanks.**

**CONCLUSION, STATED AS A HYPOTHESIS WITH ITS EVIDENCE AND ITS WEAKNESSES, NOT AS
A FINDING.** The `Np` deficit against Reid 2025 is **quantitatively consistent
with blade thickness alone**, and our `4.382` is **plausibly correct for our
tank**. The honest verdict on the band is therefore the one the supervisor
anticipated: **the band does not transfer, and this is not a mesh defect or a
zone defect to be repaired.**

**What is weak in it, said plainly:**
- The correlation is **secondary-source** and **extrapolated to an unstated reach**.
- 2.6 % agreement is **inside the correlation's own 2–3 % accuracy and well inside
  the experiment's 2.3–16 % scatter**, so it is agreement, not precision. It must
  not be quoted as a validation.
- **It changes no verdict.** `4.382` remains part of a row graded **`NOT A
  RESULT`** — fine level not iteratively converged, triple `DIVERGENT` at order
  −0.297. A number that is not a result cannot be vindicated by a correlation.
- Baffle width is **not** in this correlation. Ours (`T/10`) matches Beshay's rig,
  so it drops out of *this* comparison — but it remains untested against Reid's
  narrow `D/10` baffles, and that is now the **only** unexplained geometric
  difference between the two papers.

**WHAT WOULD FALSIFY IT, AND IT IS CHEAP.** Rebuild our geometry with
`BLADE_T = DISC_T = BAF_T = 0.00155 m` (`t/D = 0.0155`, Beshay's own impeller),
hold everything else including the MRF zone, and re-solve the fine level. The
correlation and the experiment together predict `Np ≈ 5.2–5.4`. **If it lands
there, thickness is the mechanism and the case has an experimental anchor at its
own geometry. If it does not, this section is refuted and the deficit is
something else.** Registered in
`cases/navier_class/MRF/R3/MRF_R3_ZONE_SENSITIVITY_DRAFT.md` §5 as the rung that
now outranks the zone sweep.

### 11.5 A REFERENCE-TIER CONSEQUENCE THAT IS NOT THIS LANE'S TO TAKE

Reid 2025 is a **CFD-to-CFD** reference: it reports no measured power number.
Beshay 2001 is an **experiment at our exact tank ratios**, in our Re range, with a
stated uncertainty. If a future rung is graded against `5.41 × (thickness
correction)` rather than against Reid's band, this case's reference tier could
move from **bounded-agreement** toward **experiment-validated**. **That call
belongs to the verification supervisor and to the frozen registry, not here**
(`MRF_R1_PREREGISTRATION.md` §2 registry note). It is recorded as an available
upgrade path and nothing more.

*Appended by a cfd `lab-lane`, 2026-09-12, answering the cfd-supervisor's written
question. Submissions parked. No agent's message is Sanaa's consent.*

---

# DATED SECTION, 2026-09-12 (later still) — **THE PAPER'S ONLY EXPERIMENTAL ANCHOR, MEASURED BOTH WAYS: OUR TKE PROFILE AND THEIR OWN, AGAINST THE SAME ELEVEN WU & PATTERSON POINTS**

Appended, not inserted: **lines whose number changed above this section: 0.**
Alters no gate, threshold, band, cap or label. **Registers no band and produces no
verdict.** Filed by a cfd `lab-lane` at the cfd-supervisor's dispatch; no solver ran.

## 12.0 🔴 THESE NUMBERS ARE **PENDING** THE SUPERVISOR'S SCRIPT READ

The instrument below is a **new measurement script**. Under the cfd-supervisor's
standing condition, a script that produces a measured number is **not believed until the
supervisor has read its diff personally** — a check that is not delegable. The unified
diff has been sent. **Until it is read, every number in §12 is `PENDING`**, in the
display sense of rule 1, and may not be quoted as a measurement.

## 12.1 WHY THIS COMPARISON AND NOT ANOTHER

**The paper reports no experimental power number at all** (§2.3). Its one external
experimental anchor is **Wu & Patterson (1989) LDA velocity and TKE**. So the question
"how good is our solve" cannot honestly be answered by the `Np` gap alone, which is a
gap against **their CFD**. The answerable question is: *against the same experiment, how
far is our TKE profile, and how far is theirs?* Both curves are measured against the
**identical eleven digitised LDA points** by the identical reader.

## 12.2 RESULT

Station: `r/D = 0.538`, the station matched to the paper's r = 5 cm (§6). Quantity
`k/Utip²`. Deviations expressed in units of **each LDA point's own stated half-width**,
which is Wu & Patterson's **15 %** TKE uncertainty as the paper states it.

| | **ours, fine level** | **Reid 2025, their MRF Zone 1** |
|---|---:|---:|
| LDA points evaluated | 11 of 11 | 11 of 11 |
| **points inside the experiment's own error bar** | **7** | **1** |
| RMS deviation, in half-widths | **1.12** | **6.40** |
| RMS deviation, absolute `k/Utip²` | **0.00713** | **0.00918** |
| mean signed relative deviation | **−5.26 %** | **+66.42 %** |

Per point, `dev/half-width` (positive = above the experiment):

| 2z/W | LDA k/Utip² | **ours** | in bar? | **their Zone 1** | in bar? |
|---:|---:|---:|:--:|---:|:--:|
| −2.053 | 0.00316 | +1.87 | no | **+14.07** | no |
| −1.549 | 0.00417 | +0.93 | **YES** | **+13.11** | no |
| −1.036 | 0.01903 | −0.84 | **YES** | +1.11 | no |
| −0.491 | 0.04909 | −0.98 | **YES** | +2.23 | no |
| −0.209 | 0.05418 | −1.33 | no | +1.22 | no |
| +0.001 | 0.03547 | +0.12 | **YES** | +2.21 | no |
| +0.201 | 0.03886 | −0.46 | **YES** | +2.75 | no |
| +0.526 | 0.07185 | −1.79 | no | +0.06 | **YES** |
| +1.100 | 0.01802 | +0.29 | **YES** | +1.25 | no |
| +1.604 | 0.00652 | −1.60 | no | **+4.10** | no |
| +2.117 | 0.00382 | −0.04 | **YES** | **+6.50** | no |

**THE CLEAN SIGNAL IS THE SIGN, NOT THE SIZE.** The paper's own Zone 1 curve is **above
the experiment at every one of the eleven points** — a systematic positive bias, present
in the peak region (+1.1 to +2.8 half-widths) as well as in the tails. Ours **straddles**
the data, both signs, within ±1.9 half-widths everywhere. A systematic one-sided bias at
11 of 11 points is not a tail artifact.

## 12.3 WHAT THIS DOES **NOT** MEAN — and each of these is load-bearing

1. **IT DOES NOT MAKE OUR SOLVE A RESULT.** The R2 `ET8000` row is **`NOT A RESULT`** and
   stays so: the fine level is **not iteratively converged** and the triple
   4.193 → 4.281 → 4.382 is **`DIVERGENT`** at observed order −0.297. Rule 5 runs one way.
   **§12 is a deviation computed on an ungraded number and cannot upgrade it.**
2. **IT DOES NOT MAKE OUR SOLVE "BETTER THAN THE PAPER'S".** The tanks differ: Wu &
   Patterson / Reid are T = 0.27 m, D = 0.093 m, Re 28,830; ours is T = 0.30 m,
   D = 0.100 m, Re 50,000, with **3× wider baffles and 4× thicker blades relative to D**
   (§3). Their Zone-1 curve is at r = 5 cm in **their** tank against LDA taken in **their**
   tank — an internally matched comparison. Ours is at the matched `r/D` in **ours**. A
   smaller deviation across different tanks is **one number, on one profile**, and is not
   evidence of a better method.
3. **TWO OF THE THREE STATISTICS ARE TAIL-SENSITIVE AND THAT IS SAID HERE, NOT LEFT TO BE
   FOUND.** The half-width is 15 % of each point's own value, so both `dev/half-width` and
   the mean signed relative % are amplified where `k` is small. The **least tail-sensitive**
   statistic is the absolute RMS, and on that one ours is **22 % lower** (0.00713 vs
   0.00918) — a far more modest gap than 1.12 vs 6.40 suggests. **The honest headline is
   the absolute figure plus the one-sided sign, not the half-width ratio.**
4. **IT REGISTERS NO BAND.** §3.1 records this comparison as measured-tier with **no gate**.
   Nothing here is turned into one after seeing the answer (rule 2).

## 12.4 INSTRUMENT AND ITS PLANTED CONTROLS (rule 3)

`cases/navier_class/MRF/tke_vs_wu_patterson.py`, output
`verification/runs/navier_class/MRF/R2/PAPER_PARITY/TKE_VS_WU_PATTERSON.json`.

| control | what is planted | what must move | result |
|---|---|---|---|
| our-profile reader | `PLANT = 1.234e-03` added to **every** `k/Utip²` value in a **copy on disk** of `PAPER_PARITY_RESULTS.json`, re-read through the same reader the numbers come from | every returned `k` by exactly `PLANT` | **PASSED**, worst error < 1e-12 |
| reference reader | `PLANT` added to **every** Zone-1 ordinate in a **copy on disk** of the digitised file | **the deviation statistic the conclusion is built on** — not merely the raw array — by the predicted amount | **PASSED** |
| **arming proof** | one LDA point's `half_width_k_over_Utip2` set to `null` in the real file | the script must **REFUSE**, never treat a missing error bar as a zero-width one | **REFUSED, exit 2**; the file was then restored and verified **byte-identical to HEAD** |

The script also **refuses rather than extrapolating**: an LDA point outside a curve's span
is reported as `OUTSIDE THE CURVE'S SPAN — not evaluated, not zero`, and an empty
comparison refuses rather than returning a zero deviation. All 11 points fell inside both
spans, so no point was skipped.

## 12.5 INDEPENDENT RECOMPUTATION OF `Np`, DONE BEFORE ANY OF THE ABOVE WAS BELIEVED

Before using any number from `PAPER_PARITY_RESULTS.json`, this lane recomputed `Np` from
the run's **own** `postProcessing/impellerForces/0/moment.dat`, by a reimplementation
written without reference to the peer script: `Np = 2π|M_z| / (ρ N² D⁵)`, with
`ρ = 998 kg/m³` read from the case's own `forces` dictionary (`rhoInf 998`), `N = 5.0`
rev/s from `constant/MRFProperties` (`omega 31.4159`), `D = 0.1 m`.

| level | last `|M_z|` (N·m) | **Np, this lane** | **Np, peer script** | agreement |
|---|---:|---:|---:|---|
| coarse | 0.166519986 | 4.193491 | 4.193491 | **7 significant figures** |
| medium | 0.170000157 | 4.281132 | 4.281132 | **7 significant figures** |
| fine | 0.173994385 | 4.381719 | 4.381719 | **7 significant figures** |

**The peer's `Np` is confirmed by an independent route.** One observation recorded
against it, not as a defect: the values are taken from the **last** sample of
`moment.dat`, not from a trailing window. A trailing-500 mean gives 4.211 / 4.228 / 4.418
— up to **1.25 %** away on the medium level. The plateau states were graded `PLATEAUED`
on coarse and medium, so the last value is defensible; **the 1.25 % is the scale of the
choice and is stated so a reader knows it exists.**

## 12.6 THE GRADE OF 4.38 — ARITHMETIC RE-DERIVED, AND ONE INTERNAL INCONSISTENCY CORRECTED

| against | value | deviation |
|---|---:|---:|
| registered band low, 5.3 | 4.381719 | **−17.33 %** |
| registered band high, 5.6 | 4.381719 | **−21.76 %** |
| their fine level, 5.49 | 4.381719 | **−20.19 %** |
| Rushton correlation plateau ≈ 5.0 (**SECONDARY** reference) | 4.381719 | **−12.37 %** |

**§4.1's headline reads "17.3 % to 22.0 % LOW" while its own parenthetical reads
"−21.8 %".** The correct upper figure is **−21.76 %, i.e. 21.8 %, not 22.0 %.** Recorded
as a correction of a rounding inconsistency inside §4.1; **§4.1 is not rewritten** (rule 6)
and the substance — `4.38` is **clearly outside** the registered band, and a reader of the
superseded `[4.0, 6.0]` line would wrongly believe we had a passing number — is unchanged.

## 12.7 COMPUTE (rule 12)

**No solver ran.** Post-processing of fields already on disk plus one Python script: 1
rank, **under 2 core-minutes**, ≈ **$0.002 DERIVED, NOT MEASURED** at $0.0513/core-h,
owner-stated — the box cannot read its own billing. No pre-registered estimate exists for
a desk task, so **no estimate-versus-actual calibration row is owed for §12**.

*Appended by a cfd `lab-lane`, 2026-09-12. Registers no band, alters no gate, threshold,
cap or label. Numbers `PENDING` the supervisor's non-delegable read of the instrument
diff. No agent's message is Sanaa's consent. Submissions parked.*

## 12.8 REVISION, 2026-09-12 — **§12.0's `PENDING` STAMP IS STRUCK; TWO REQUIRED ADDITIONS MADE; THE SIGN CLAIM IS NARROWED FROM 11 OF 11 TO 10 OF 11**

Appended, not inserted: **lines whose number changed above this section: 0.**
**A READER WHO STOPS AT §12.0 WILL READ A STATUS THAT NO LONGER HOLDS.** §12.0 said every
number in §12 was `PENDING` the cfd-supervisor's non-delegable read of the instrument.
**That read is done — check 1 discharged, all 202 lines read as code — and the `PENDING`
is LIFTED, subject to the two additions below, which are now made.** §12.0 is **struck by
this section, not rewritten** (rule 6).

### 12.8.A THE TWO PLANTED CONTROLS WERE ASYMMETRIC, AND THE WEAKER ONE GUARDED THE NUMBER THAT FLATTERS US

Revision 1 planted into **our** array and checked only that the array moved, while the
**reference** control planted into the conclusion's statistic. **Ours is the side
reporting 7 of 11 inside the error bar and RMS 1.12 half-widths — the side that looks
good had the looser control.** Raised by the cfd-supervisor; the criticism is correct and
this record says so rather than absorbing it.

**Both controls now run BOTH limbs and fail if either limb fails:**

| control | limb 1 — raw array | limb 2 — the conclusion's statistic |
|---|---|---|
| **ours** | every `k` moves by exactly `PLANT`; worst error **2.39e-18** | `mean_signed_rel_pct` of OURS-vs-LDA must move by the predicted `100·mean(PLANT/k_LDA)`. Predicted **13.304301928 %**, observed **13.304301928 %** |
| **reference** | every Zone-1 ordinate moves by exactly `PLANT`; worst error **1.08e-18** | same statistic for Zone-1-vs-LDA. Predicted **13.304301928 %**, observed **13.304301928 %** |

**All four limbs PASSED.** As the supervisor put it: the point is not that it was expected
to fail, but that **the record now shows it could have.**

### 12.8.B DIGITISATION UNCERTAINTY — ANSWERED TWO WAYS, AND IT NARROWS THE CLAIM

Revision 1 treated the digitised Zone-1 ordinates as **exact** and banded only the LDA
points. A one-sided sign at 11 of 11 is **precisely what a small systematic digitisation
offset would manufacture**, so it is answered here rather than left to a hostile reader.

**LIMB 1 — ANALYTIC, and it is the stronger of the two.** Both the LDA markers and the
Zone-1 polyline are recovered from the **same PDF content stream** and mapped through the
**same affine calibration** `k(x) = XV0 + (x − X0)·s` (`digitise_reid2025_fig16.py`, `xs`).
Therefore:

* **Offset error** — if `X0` is wrong by `d`, every recovered `k` shifts by `−d·s`, **both
  curves alike**, and the **difference (Zone1 − LDA) is EXACTLY unchanged**. A calibration
  offset cannot create, destroy or flip a single sign.
* **Scale error** — if `s` is wrong by `(1+e)`, the difference is multiplied by a
  **positive** factor. That changes magnitude, never sign.

**The one-sided sign result is therefore invariant under ANY affine axis calibration
error, by construction.** This is an argument about the reader's algebra, labelled
`ANALYTIC, not a measurement` in the output.

**LIMB 2 — EMPIRICAL, from the digitiser's own known truth.** Every LDA bar in this figure
has a true half-width of **exactly 15.0 %** of its centre, so the recovered
`half_width_pct` has a **known truth** and its departure from 15.0 **measures** the
digitiser's reading error:

| | |
|---|---:|
| bars checked | 11 |
| worst departure from 15.0 | **0.17 percentage points** |
| mean departure | 0.051 pp |
| ⇒ worst relative reading error on `k` | **1.133 %** |
| ⇒ band on a **difference** (both ordinates, summed not in quadrature — the conservative direction) | **2.267 %** |

**Transfer caveat, stated not buried:** this band is measured on the LDA **markers** and
transferred to the Zone-1 **polyline**, which the known-truth check cannot reach. **The
transfer is an assumption.** All of the departure is also attributed to the **ordinate**,
though some certainly belongs to the cap positions — again the conservative direction.

### 12.8.C THE RESULT: THE CLAIM SURVIVES, AND IS NARROWED

| curve vs the 11 LDA points | positive | negative | **signs surviving the 2.267 % band** |
|---|---:|---:|---:|
| **Reid 2025 Zone 1** | **11** | 0 | **10 of 11** |
| **ours, fine** | 4 | 7 | 9 of 11 |

**THE ONE EXCEPTION, NAMED.** At `2z/W = +0.526` — the profile's peak — Zone 1's excess
over the experiment is **0.94 % of the LDA value**, which is **below** the 2.267 % band.
That is the same point already reported in §12.2 as Zone 1's only one inside the
experiment's error bar (+0.06 half-widths).

> **THE CLAIM IS THEREFORE RESTATED, AND IT IS NARROWER THAN §12.2's:
> the paper's own Zone-1 curve lies ABOVE the Wu & Patterson experiment at 11 of 11
> points, and at 10 of those 11 the excess exceeds a conservative digitisation band.
> At the 11th — the peak — the excess is inside that band and the sign there is NOT
> claimed.** §12.2's "every one of the eleven points" is correct as a raw sign count and
> is **struck as a robustness claim** by this line.

**The finding survives**, and on the supervisor's own criterion it is now the one to lead
with: a **one-sided bias at 10 of 11 points, immune to affine calibration error by
construction**, is scale-free in a way the RMS ratios are not. Our own curve, by
contrast, is genuinely **two-sided** (4 positive, 7 negative) — which is what "straddles
the data" was asserting in §12.2 and is now demonstrated rather than asserted.

**NOTHING IN §12.3's FOUR LIMITS IS WEAKENED BY THIS.** R2 `ET8000` remains
`NOT A RESULT`; nothing here says our solve is better than theirs; the tail-sensitivity
disclosure stands; and **no band is registered.**

### 12.8.D INSTRUMENT

`cases/navier_class/MRF/tke_vs_wu_patterson.py`, revision 2026-09-12. **No result,
statistic or caveat of revision 1 was removed** — the revision only adds limbs and
uncertainty analysis. Output regenerated at
`verification/runs/navier_class/MRF/R2/PAPER_PARITY/TKE_VS_WU_PATTERSON.json`, which now
carries `calibration_invariance`, `digitisation_band`, `sign_robustness_paper_Zone1` and
`sign_robustness_ours` **inside the JSON**, so they travel with the number rather than
living only in this prose.

**The revised diff has been sent to the cfd-supervisor. The numbers in §12.8 are
themselves `PENDING` that second read**, by the same rule that produced §12.0 — a lane
does not get to exempt its own repair from the check that caught it.

*Appended by a cfd `lab-lane`, 2026-09-12. Registers no band, alters no gate, threshold,
cap or label. No agent's message is Sanaa's consent. Submissions parked.*

## 12.9 — **THE LAST PLACE THIS RESULT COULD HAVE BEEN WRONG IS CLOSED, AND §12.8's INVARIANCE IS STRONGER THAN §12.8 CLAIMED IT**

Appended, not inserted: **lines whose number changed above this section: 0.**
Completes §12.8's two limbs at the cfd-supervisor's second-pass direction. Registers no
band; alters no gate, threshold, cap or label.

### 12.9.A THE RESIDUAL NON-AFFINE TERM IS NOT SMALL — IT IS **ABSENT BY CONSTRUCTION**

§12.8.B argued the sign result is invariant under any **affine** calibration error, and
left "per-point reading noise" as the residual. **For this extraction method, affine error
is the ONLY calibration error there is**, and that is a property of the reader, not a
happy accident:

* Coordinates are taken from `m`, `l` and Bézier path operators **in a vector content
  stream**. There is no rasterisation step — no pixel grid, no page image, no photograph
  of a figure.
* **A non-affine distortion — skew, warp, perspective, lens or scan error — can only enter
  through a raster stage.** With none present, the class of possible calibration errors is
  exhausted by offset and scale, and §12.8.B has already shown neither can alter a sign.
* **The line-width point is the same insight.** A stroke has width, but `m`/`l` give the
  path **centreline**; width would only bias a reading taken from a rendered image. It is
  stated rather than left silent precisely so silence is not read as an oversight.

So the correct statement is stronger than §12.8.B's: **the one-sided sign result is
invariant under the whole class of calibration errors this reader can sustain**, and what
remains is per-point reading noise alone — which §12.8.B measured at 1.133 % and banded at
2.267 % on a difference.

### 12.9.B THE CATEGORICAL RISK — SELECTION BY COLOUR — CLOSED FROM THE STREAM

**No uncertainty band in §12.8 touches this, and that is why it had to be closed
separately.** The Zone-1 polyline is selected by RGB triple. A wrong selection would make
every downstream number **internally consistent and wrong**, which is the one failure an
error analysis cannot see.

Instrument: `cases/navier_class/MRF/verify_fig16_polyline_identity.py`, output
`verification/runs/navier_class/MRF/R2/PAPER_PARITY/FIG16_POLYLINE_IDENTITY.json`.

| question | answer, from the PDF's own content stream |
|---|---|
| distinct stroke colours in the figure | **6** |
| black (`0 0 0`) | set **47** times — axes, ticks, the LDA markers and their error bars. **Never a data curve.** |
| non-black colours | **5**, and **each is set EXACTLY ONCE** |
| paths matching `0.87451 0 0` | **exactly 1** (block 46: `m`=2, `l`=44 — one legend key line plus one data polyline of 43 segments) |
| what the paper's legend calls that colour | **`Zone 1`** |

**THE LEGEND BINDING USES NO ASSUMPTION ABOUT LEGEND ORDER.** Each colour is bound to a
label **two independent ways**, and the script refuses if they disagree on any colour:

| RGB | key-line y | positional label | sequential label | agree | offset |
|---|---:|---|---|:--:|---:|
| `0.87451 0 0` (red) | 19.852 | **Zone 1** | **Zone 1** | ✔ | 2.498244 |
| `0 0 0.545098` (blue) | 26.500 | Zone 2 | Zone 2 | ✔ | 2.500244 |
| `0.113725 0.427451 0.113725` (green) | 33.148 | Zone 3 | Zone 3 | ✔ | 2.502244 |
| `0.647059 0.647059 0.647059` (grey) | 39.801 | Zone 4 | Zone 4 | ✔ | 2.499244 |
| `1 0.752941 0` (orange) | 46.449 | Zone 5 | Zone 5 | ✔ | 2.501244 |

*Positional* = the text baseline sits a constant offset from its key line; *sequential* =
the label is emitted immediately before that colour is set. **Offset spread 0.004 against
a derived tolerance of 0.332 — 5 % of the 6.648 legend row spacing, a margin of 83×.**

**Five coloured curves for five MRF zones, one per zone.** There is no second red path to
confuse, and no unlabelled coloured curve.

### 12.9.C THE CATEGORICAL PLANT — because a number plant proves nothing about a selection

A perturbation of a **value** cannot test a **choice**. So a **second path carrying the
identical RGB triple** was spliced into a **copy of the stream**, and the selector was
required to see it and refuse:

| | |
|---|---:|
| paths matching the target, before the plant | **1** |
| after the plant | **2** |
| selector refused on the planted ambiguity | **YES, exit 2** |

**A selector never shown able to see a second match is not evidence that there is only
one.** It was shown. The script also refuses on **zero** matches rather than substituting
a curve.

### 12.9.D A THRESHOLD OF MINE WAS WRONG, AND IT IS DISCLOSED RATHER THAN QUIETLY FIXED

The positional binding first used a hard-coded tolerance of `1e-6` and **REFUSED**, at a
measured offset spread of 0.004. **The binding was fine; my threshold was wrong** — PDF
path coordinates are written to three decimal places, so an exactly constant offset
cannot read as constant to 1e-6. The tolerance is now **derived from the figure** (5 % of
the legend row spacing — the distance a label would have to travel to be captured by its
neighbour) instead of chosen by me, and both the spread and the 83× margin are reported.
**The instrument refused rather than degrading, which is the behaviour that surfaced it;
no output of the 1e-6 version was ever believed or recorded.**

### 12.9.E WHAT REMAINS UNBANDED

**Nothing this lane can name.** Affine calibration error — invariant by construction.
Non-affine — absent by construction. Per-point reading noise — measured and banded at
2.267 %, and 10 of 11 signs survive it. Categorical mis-selection — closed above with its
own plant. **If a further route to a wrong answer exists here, it has not been found, and
that is stated as the limit of this lane's search rather than as a proof of correctness.**

*Appended by a cfd `lab-lane`, 2026-09-12. Registers no band, alters no gate, threshold,
cap or label. No agent's message is Sanaa's consent. Submissions parked.*
