# T-family expertise curriculum — advanced heat-transfer cases

**STATUS: PROPOSED — awaiting Sanaa's ratification. Nothing in this file is a
pre-registration, nothing here authorises a run, and NO compute has been
launched under it.** Recorded 2026-08-23 by the heat-transfer supervisor on
the chief's relay of Sanaa's directive.

## The directive, verbatim

> "We can think of many heat transfer advanced cases so the designated heat
> transfer team can run them and become even more of an expert."

— Sanaa, 2026-08-23, relayed by the chief. Recorded, not paraphrased.

## Standing frame — what this curriculum is and is not

- **The spine is UNCHANGED.** `THERMAL_BUILDUP_DIRECTIVE.md` H-2 (T3 → T5 →
  T8 → T12 → K2 rack row) and the H-5 tier order (T4, T6, T7, T2, T9b/c,
  T10b, T11) govern; this curriculum is **additive and slots behind them.**
- **DC-cooling is the destination** (H-2 header; H-6): every candidate below
  is ranked by leverage toward the DC certificate's quantity classes —
  **inlet T, recirculation, stratification height, transient response**
  (`docs/product/DC_CERTIFICATE_TEMPLATE.md`).
- **Adoption discipline.** Any candidate Sanaa ratifies still gets its own
  frozen, committed pre-registration with a costed gate before any solver
  starts (CLAUDE.md rules 2, 12); every validation source below is adopted
  only after **title-page verification of the retrieved document** (rule 15)
  — file type, filename and hash never substitute. Sources not on disk are
  marked so; obtaining them is a pull on Sanaa's desk, not this file's act.
- **Costs are estimates, not measurements**, at the owner-stated
  $0.0513/core-h (c7a.4xlarge). "Pre-authorised" means the estimate sits
  under the $25 line; a real cost lands in the item's own pre-registration
  and an estimate here never becomes a budget.
- **VM2026R1_Fluids** (repo root, 123 files / 2.5 GB, untracked, second copy
  mid-transfer): several candidates note it as a possible comparator corpus.
  **Every such note is PENDING Sanaa's VM2026R1 instructions (chief's D-6 —
  DO NOT TOUCH EITHER COPY); nothing is graded from it, nothing is built on
  it here.**

## The candidates

Each entry: expertise built · validation source (with on-disk status) ·
T-family prerequisites · rough cost · what its pre-registration would gate on
· known failure modes.

### E1. Porous-media rack surrogate (Darcy–Forchheimer server model)
- **Expertise:** the standard room-model idiom — racks as porous zones with
  volumetric heat sources; the bridge from resolved rack (T5/K2) to room
  (T12) scale.
- **Validation:** measured server/rack pressure-drop and flow curves —
  ASHRAE datacom series and published rack ΔP–Q data. **NOT ON DISK; pull to
  Sanaa's desk; title-verify before adoption.** Internal cross-check: the
  resolved K2a rack row (itself awaiting her approval).
- **Prerequisites:** T5 (rack physic) graded; K2a approved.
- **Cost:** ~$2–5 (steady RANS, small domains, 3-level ladder). Pre-authorised class.
- **Prereg gates:** ΔP–Q curve within stated data uncertainty; exhaust-T
  energy balance closed to a registered tolerance; Roache triple on ΔP.
- **Failure modes:** Forchheimer coefficients fitted rather than measured
  (circular validation); porous-zone energy source double-counting; triple
  STAGNANT because the porous solution is mesh-insensitive by construction.

### E2. Hot-aisle/cold-aisle containment surrogate
- **Expertise:** the certificate's core comparison — contained vs open aisle,
  recirculation and inlet-T classes directly.
- **Validation:** published DC CFD/measurement comparisons (VanGilder et al.,
  ASHRAE). **NOT ON DISK; pull; title-verify.** Possible VM2026R1 room-flow
  comparator — **PENDING D-6, not built on.**
- **Prerequisites:** T8 (plume/stratification), T12 (room validation), E1.
- **Cost:** ~$15–40 per configuration pair at ~1–2 M cells steady RANS with a
  ladder — **NEEDS COSTING; likely over $25.**
- **Prereg gates:** rack-inlet T distribution vs reference within its stated
  uncertainty; recirculation index registered in advance (D389 caveat: no
  mean-normalised spread metric); capture/containment effectiveness band.
- **Failure modes:** reference geometries under-specified in papers (leakage
  areas dominate and are rarely reported); steady RANS on an unsteady aisle;
  inlet-T class inheriting the S13/D389 normalisation trap.

### E3. Cooling-failure / ride-through transient (buoyancy-coupled thermal mass)
- **Expertise:** the certificate's transient-response class — chiller-loss
  temperature rise against thermal inertia.
- **Validation:** staged — (a) exact lumped-capacitance and semi-infinite
  solid solutions (derivable, no paper needed); (b) published DC ride-through
  measurements. **(b) NOT ON DISK; pull; title-verify.**
- **Prerequisites:** T11 (transients) graded; E1; T12 for the room stage.
- **Cost:** stage (a) ~$1–3 pre-authorised; room-scale stage ~$20–60 —
  **NEEDS COSTING.**
- **Prereg gates:** stage (a) as EXACT identity rows (T9a discipline); stage
  (b) time-to-threshold within the data's stated uncertainty; time-step
  convergence triple alongside the mesh triple.
- **Failure modes:** unmeasured thermal mass inventory in references; solver
  under-resolution of initial plume transition; transient checkpoints
  violating L-140 durability if writeInterval is careless.

### E4. Fan and air-mover boundary verification (fan curves, MRF)
- **Expertise:** `fanPressure`/fan-curve BCs and MRF zones — every DC model's
  air movers, currently unverified in this lab.
- **Validation:** manufacturer fan curves (manual/datasheet — title-verify
  the document itself) plus an exact duct-network balance derivation.
- **Prerequisites:** none beyond T1-class verification discipline.
- **Cost:** ~$1–2. Pre-authorised class.
- **Prereg gates:** operating point on the registered curve to a registered
  tolerance; mass conservation identity across the fan face.
- **Failure modes:** curve digitised from a plot (uncertainty unstated);
  static-vs-total pressure convention mismatch — a classic silent factor.

### E5. Conjugate heat transfer at blade/board scale
- **Expertise:** solid–fluid coupling with realistic conductivity ratios at
  electronics scale — the step past T9a/T9b/c toward a served blade.
- **Validation:** Meinders 1998 (HELD, sha256 `36c89a54…`, title-verified)
  matrix chapters — the T5 draft already notes they need their own rung;
  plus ERCOFTAC conjugate entries. **ERCOFTAC copy NOT ON DISK; pull;
  title-verify.**
- **Prerequisites:** T5 graded (its conjugate solver choice inherits); T9b/c.
- **Cost:** ~$4–8. Pre-authorised class.
- **Prereg gates:** interface temperature continuity as an identity row
  (`Gauss harmonic` per T9a-D/L-227); local h against thesis data within its
  5 %/10 % stated uncertainty.
- **Failure modes:** the T9a interface-scheme defect class (D454) at any new
  interface; property-jump under-resolution; conjugate triples STAGNANT at
  affordable levels (T9a-D A1 measured exactly this).

### E6. Impinging jet arrays
- **Expertise:** array interaction, crossflow degradation of Nu — beyond
  T4's single jet; relevant to targeted cooling and (long-run) liquid-adjacent
  work.
- **Validation:** Florschuetz et al. 1981 (NASA CR — jet-array Nu
  correlations with stated uncertainty). **NOT ON DISK; pull; title-verify.**
  T4's own closed ASME primaries remain a separate, already-recorded pull.
- **Prerequisites:** T4 graded rows (currently blocked on primaries).
- **Cost:** ~$5–12. Pre-authorised class.
- **Prereg gates:** row-resolved Nu vs correlation within stated uncertainty;
  the shelf-D band-containment question (H-5) carried to arrays.
- **Failure modes:** stagnation-Nu bias documented for k–ω-class models (the
  known T4 physics); array cases amplify turbulence-model sensitivity;
  second-hand uncertainty (the exact defect T4's board note records).

### E7. High-Ra natural convection cavity
- **Expertise:** near-wall resolution and (U)RANS choices at Ra ~ 1e9–1e10 —
  the aisle buoyancy regime, ahead of T6's scaling study.
- **Validation:** Ampofo & Karayiannis 2003 (Ra 1.58e9 benchmark, stated
  uncertainties); de Vahl Davis numerical benchmark as the low-Ra control.
  **Both NOT ON DISK; pull; title-verify.** Possible VM2026R1 natural-
  convection comparator — **PENDING D-6, not built on.**
- **Prerequisites:** T6 (its ladder defines the family); T8 shares physics.
- **Cost:** 2D ladder ~$3–8 pre-authorised; a 3D/URANS stage **NEEDS
  COSTING** (~$20–50).
- **Prereg gates:** wall Nu profiles within stated uncertainty; stratification
  parameter (certificate class) with a registered definition; laminar low-Ra
  control row against de Vahl Davis as near-EXACT.
- **Failure modes:** transition modelling at mid-Ra (models disagree
  strongly); stratification metric definition drift; 2D surrogacy of a 3D
  cavity overstating agreement.

### E8. Stratified plume / displacement ventilation
- **Expertise:** filling-box dynamics, interface height — the stratification
  class with an analytical spine.
- **Validation:** Baines & Turner plume theory and Linden's emptying–filling
  boxes (analytical primaries — derivable and checkable in-file; the papers
  themselves **NOT ON DISK; pull; title-verify** for the constants' stated
  ranges).
- **Prerequisites:** T8 (this is T8's natural deepening).
- **Cost:** ~$5–12. Pre-authorised class.
- **Prereg gates:** interface height vs the analytical prediction within the
  entrainment constant's published spread (the band IS the spread, stated);
  plume volume-flux scaling exponent as a registered row.
- **Failure modes:** entrainment-constant circularity (fitting the constant
  the band depends on); RANS plume spreading known biased; sensitivity to
  source Richardson number specification.

### E9. Ribbed-channel turbulent forced convection (Vogel & Eaton class)
- **Expertise:** separated-reattaching thermal boundary layers with
  roughness elements — heat-sink and channel physics; directly the T3
  experimental family.
- **Validation:** Vogel & Eaton 1985 (the H-1 primary — **NOT ON DISK**, the
  standing pull); Rau et al. 1998 ribbed-duct data. **NOT ON DISK; pull;
  title-verify.**
- **Prerequisites:** T3 graded (needs the ext1 ladder outcome AND the
  primary).
- **Cost:** ~$3–8. Pre-authorised class.
- **Prereg gates:** reattachment-zone Nu distribution within stated
  uncertainty; friction-factor augmentation row; Roache triples per rib
  configuration.
- **Failure modes:** T3's own lesson — separated-flow thermal ladders
  converge slowly (its triples went DIVERGENT/OSCILLATORY at 4/4); periodic-
  segment boundary conditions leaking into the graded row.

### E10. Pin-fin heat sink arrays
- **Expertise:** endwall + pin conjugate augmentation — the actual server
  heat-sink geometry.
- **Validation:** Metzger et al. 1982/1984 pin-fin Nu data. **NOT ON DISK;
  pull; title-verify.**
- **Prerequisites:** E9 (shares the separated-flow discipline), E5 for the
  conjugate variant.
- **Cost:** ~$4–10. Pre-authorised class.
- **Prereg gates:** row-averaged Nu vs data within stated uncertainty;
  ΔP–Q row (ties to E1's porous coefficients — a real cross-check).
- **Failure modes:** as E9, plus horseshoe-vortex under-resolution at the
  pin–endwall junction dominating the graded quantity.

### E11. Participating-media radiation (fvDOM)
- **Expertise:** the lab's radiation verification (T10a family) extended past
  transparent media; fvDOM angular discretisation as a new ladder axis.
- **Validation:** published absorbing–emitting enclosure benchmarks with
  semi-analytic solutions (Hsu & Farmer class). **NOT ON DISK; pull;
  title-verify.** Low DC leverage (air is transparent at DC temperatures) —
  ranked accordingly; expertise value is the radiation toolchain itself.
- **Prerequisites:** T10b (combined convection+radiation cavity).
- **Cost:** ~$1–4. Pre-authorised class.
- **Prereg gates:** angular + spatial double ladder (both triples registered
  — the T10a-R lesson L-244 applies squarely: no band from a pre-asymptotic
  triple); flux divergence vs benchmark within its stated digits.
- **Failure modes:** ray effects masquerading as convergence; angular/spatial
  error cancellation producing a false plateau (exactly the implied-order
  trap L-244 records).

### E12. Humidity and psychrometrics — capability-gated
- **Expertise:** moisture transport, condensation risk at economiser
  setpoints — a certificate-adjacent class Sanaa's market will ask about.
- **Capability, stated honestly:** ESI v2606 ships
  `humidityTemperatureCoupledMixed` (condensing-wall BC, chtMultiRegion
  tutorials) but **no full psychrometric room solver**; a room-scale
  humidity field means a custom scalar-transport layer — new code, its own
  verification ladder, and code is lane work under a its own prereg.
- **Validation:** ASHRAE psychrometric relations as EXACT rows (derivable);
  condensing-plate experiments **NOT ON DISK; pull; title-verify.**
- **Prerequisites:** T12; the capability question settled first.
- **Cost:** BC-verification stage ~$2–5 pre-authorised; the capability build
  itself **NEEDS COSTING and its own approval — not runnable as-is.**
- **Prereg gates:** saturation-curve identity rows; condensate mass balance
  closure.
- **Failure modes:** treating a tutorial BC as a validated model; humidity
  source terms unbalancing the Boussinesq assumption silently.

## Tiering — behind the spine, with cumulative cost

Order inside the curriculum = certificate leverage (H-6), then physics
prerequisite chains. **Nothing starts ahead of the spine or the H-5 tier.**

| tier | items | est. cost | cumulative | authorisation |
|---|---|---:|---:|---|
| **spine + H-5** (unchanged) | T3→T5→T8→T12→K2; then T4, T6, T7, T2, T9b/c, T10b, T11 | per own preregs | — | as already recorded |
| **C-A certificate-direct** | E1 ($2–5), E4 ($1–2), E3-a ($1–3), E2 (**$15–40**), E3-b (**$20–60**) | $39–110 | $39–110 | E1/E4/E3-a pre-authorised class; **E2, E3-b NEEDS COSTING + approval** |
| **C-B physics depth** | E5 ($4–8), E8 ($5–12), E7-2D ($3–8), E6 ($5–12), E7-3D (**$20–50**) | $37–90 | $76–200 | E7-3D **NEEDS COSTING**; rest pre-authorised class |
| **C-C breadth / expertise** | E9 ($3–8), E10 ($4–10), E11 ($1–4), E12-BC ($2–5), E12-build (**uncosted**) | $10–27 + build | $86–227 + build | E12-build **NEEDS COSTING + capability approval** |

Estimates only; each adopted item is re-costed in its own pre-registration
and the $25 line is applied there, not here (a blanket is not a per-item
read — rule 9).

## VM2026R1 comparator notes — all PENDING, none acted on

Candidates E2, E7 (and possibly E5) may find Fluent/CFX verification
counterparts in `VM2026R1_Fluids/`. **Chief's D-6 stands: both copies
untouched, nothing enumerated, graded or cited from them in this file.
Every such use is PENDING Sanaa's VM2026R1 instructions.**

## Ratification asks (Sanaa)

1. Ratify / reorder / strike candidates E1–E12 (the tiering is a proposal).
2. The paper pulls flagged NOT ON DISK — which to obtain (rule 15
   verification follows retrieval; purchases individually confirmed).
3. E2 / E3-b / E7-3D / E12-build cost approvals when their preregs are
   written.
4. VM2026R1 instructions (D-6) before any comparator note is acted on.

*Cross-references: `THERMAL_BUILDUP_DIRECTIVE.md` (H-1…H-7, spine and tier
order), `docs/product/DC_CERTIFICATE_TEMPLATE.md` (H-6 classes),
`T1b_L4_AMENDMENT.md`/L-244 (triple gating carried into every candidate's
gates), CLAUDE.md rules 2, 5, 9, 12, 15.*
