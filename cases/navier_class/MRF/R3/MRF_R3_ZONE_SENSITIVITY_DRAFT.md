# MRF_R3 (DRAFT) — MRF ZONE SIZE AS A REGISTERED PARAMETER WITH A MEASURED SENSITIVITY

> **REVISION 2, 2026-09-12 (same day), at the cfd-supervisor's direction.** The
> premise is restated so it cannot be read as a repair. **This rung is NOT a fix
> for the `Np` deficit and never was justified as one** — §1 shows the zone is not
> undersized and the mechanism predicts the wrong sign. **Its stated purpose is
> the sensitivity itself**: a parameter with no sensitivity behind it is a
> default, which is L-561's whole point. **And it is no longer the priority rung**
> — §5, added in this revision, registers the blade-thickness rung that now
> outranks it, because an experiment at our exact tank ratios has since landed on
> the box and quantifies the deficit.

> **STATUS: DRAFT. NOT FROZEN. NOT LAUNCHED. NOT A GATE.**
> No sha binds this document, no run directory exists under it, and no verdict may
> be read from it. **The freeze is the cfd-supervisor's check 4 and is not this
> lane's to take** (`SUPERVISION_CHARTER.md` §3; CLAUDE.md rule 2). Every gate,
> threshold, cap and label below is amendable until that freeze and carries no
> evidentiary weight. **Nothing here has been queued or launched.**

- **Authored:** 2026-09-12, cfd `lab-lane`, at the cfd-supervisor's direction,
  under Sanaa's [SANAA-DIRECT] addendum of the same day (item 3).
- **Reference registration:** `verification/campaign/MRF_PAPER_REGISTRATION_REID2025.md`
- **Predecessor:** `verification/campaign/MRF_R2_PREREGISTRATION.md` (verdict
  `NOT A RESULT`, `ET8000` row; fine not iteratively converged, triple `DIVERGENT`).

---

## 1. THIS RUNG IS NOT A REPAIR — THE ZONE IS NOT UNDERSIZED, AND THE MECHANISM PREDICTS THE WRONG SIGN

The directive's item 3 says: *"if our zone is near the swept volume (~1.1D), that
is the paper's mechanism for a >12% low Np: re-register with a zone of 1.3–1.5D."*

**Two of those premises do not survive contact with the artifacts, and this draft
says so before it proposes anything.**

1. **Our zone is not at 1.1 D.** Read from
   `verification/runs/navier_class/MRF/R2/ET8000/fine/system/topoSetDict` —
   `cylinderToCell`, `radius 0.060`, `z 0.080 → 0.120` — it is **1.200 D in
   diameter and 0.400 D (= 2.00 W) thick**, against `D = 0.100 m` and blade width
   `W = D/5 = 0.020 m`.
2. **The paper recommends no 1.3–1.5 D zone, and its own numbers point the other
   way.** The only range it names is *"most studies … use MRF regions with
   dimensions within those of Zone 3 and Zone 5"* — **1.49 D to 1.93 D**, a
   description of the literature. Its Fig. 12 printed labels give `Np` = **5.4 at
   1.10 D rising to 6.2 at 1.26 D**. Our 1.20 D sits on that rise. **If their
   zone-size curve transferred, a 1.20 D zone would put `Np` at or above 5.3–5.6
   — not 20 % below it.** The zone-size mechanism predicts the wrong sign for our
   shortfall and is therefore **not** the explanation of 4.38.

**What is still true, and is the reason this rung exists.** The paper's central
result is that MRF zone size moves `Np` by more than 12 %, turbulence intensity by
19 %, and mixing time by a factor of three — and **we have never measured that
sensitivity on our own tank**. Our zone size was chosen once, in the R1
pre-registration §4, as *"a cylinder of radius ~0.6 D"*, with **no sensitivity
behind it**. That is a default, and the lesson filed with this draft is exactly
that a default is not a registration. **This rung converts our zone size from a
default into a measured parameter.** It is not proposed as a fix for `Np`.

---

## 2. THE PROPOSED SWEEP (draft values, amendable until the freeze)

Held fixed: geometry, `N`, `ν`, schemes, closure, wall treatment, mesh family,
blade angular position, and `endTime`. **One registered change per run** (Sanaa's
item 13). The only thing that varies is the `topoSet` cylinder.

| arm | zone diameter | radius (m) | thickness | z span (m) | note |
|---|---|---|---|---|---|
| Z-A | 1.10 D | 0.0550 | 2.00 W | 0.080 → 0.120 | the paper's Zone-1 diameter |
| Z-B | **1.20 D** | 0.0600 | 2.00 W | 0.080 → 0.120 | **the as-run R2 zone — the anchor arm, already on disk** |
| Z-C | **1.30 D** | 0.0650 | 2.00 W | 0.080 → 0.120 | the directive's lower edge |
| Z-D | **1.50 D** | 0.0750 | 2.00 W | 0.080 → 0.120 | the directive's upper edge |
| Z-E | 1.70 D | 0.0850 | 2.00 W | 0.080 → 0.120 | the paper's Zone 4, where its `Np` peaks |
| Z-F | 1.20 D | 0.0600 | **3.10 W** | 0.0690 → 0.1310 | thickness arm, the paper's Zone-6 thickness |

Z-B costs nothing: it is the existing `ET8000` fine solve, re-read, **not re-run**.

### 2.1 How the interface is placed, and against what

The directive requires the interface **out of the blade wake and clear of the
baffles**. Both are checkable against our own geometry, and both are checked
**before** a launch, not argued afterwards:

- **Clear of the baffles.** Our baffles are `T/10 = 0.030 m` wide on a
  `T/2 = 0.150 m` tank, so their inner edge sits at **r = 0.120 m**. A zone of
  diameter `1.50 D` has its interface at **r = 0.075 m**, leaving a radial gap of
  **0.045 m = 0.45 D**. The largest arm, `1.70 D`, leaves **0.035 m = 0.35 D**.
  **Registered clearance rule: the interface radius must be ≤ 0.100 m, i.e. at
  least `0.20 D` clear of the baffle inner edge.** `1.70 D` (r = 0.085) satisfies
  it; anything at or beyond `2.00 D` does not and is excluded by this rule rather
  than by judgement. This is the paper's own warning made into a number: it
  reports that the artificial turbulence at the MRF interface *"becomes larger as
  the MRF interface gets closer to the baffles and tank walls"*.
- **Out of the blade wake.** The wake of a Rushton blade is a trailing vortex pair
  shed from the blade tip at `r = 0.050 m`, decaying over roughly one blade length
  (`L = D/4 = 0.025 m`) downstream. An interface at `r = 0.055 m` (Z-A) sits
  **inside** that decay length; at `r = 0.075 m` (Z-D) it sits **one full blade
  length beyond it**. **Registered placement rule: the interface radius must be
  ≥ `0.5 D + L` = 0.075 m for any arm claimed to be "out of the blade wake".**
  By that rule only **Z-D and Z-E qualify**, and Z-A, Z-B and Z-C are registered
  in advance as **in-wake arms**, which is a property to be measured, not a defect
  to be hidden. The wake-decay length is a **stated modelling assumption**, not a
  measurement; it is falsified by the measurement in §2.2.
- **Measured, not assumed.** For every arm the interface position is reported as a
  fraction of the local `k` and `|U|` gradient scale read from the solved field on
  the interface surface, so "in the wake" or "out of it" becomes a number rather
  than a claim.

### 2.2 Graded quantities

Primary: `Np` per arm. Beside it, at every arm, the quantities the paper reports
and that this lane has already built readers for: agitation index `Ig`, mean
turbulence intensity `I` under **both** normalisations, the velocity and TKE
profiles at `r/D = 0.538`, `0.645`, `0.753`, and — as the paper's own diagnostic
for interface artefacts — the **volume fraction of the tank with `I > 20 %`** and
the peak `k` on the interface surface itself.

**Sensitivity, which is the actual deliverable:** `dNp/d(zone diameter/D)` across
the arms, with the azimuthal-scatter uncertainty already measured in
`PAPER_PARITY_RESULTS.json` carried through. **The rung's product is a sensitivity
curve for OUR tank, not a value inside somebody else's band.**

---

## 3. WHAT THIS DRAFT DELIBERATELY DOES NOT DO

- **It does not register a `Np` band.** The two tanks are not geometrically
  similar (baffles 3× wider, blades 4× thicker relative to `D`), so `5.3–5.6` is
  registered as **context** in
  `verification/campaign/MRF_PAPER_REGISTRATION_REID2025.md`, not as a gate. A
  band for this rung, if the supervisor wants one, must be argued on **our**
  geometry and frozen before compute.
- **It does not claim the zone explains 4.38.** §1 shows it does not.
- **It does not carry a cost estimate yet.** Rule 12 requires one **in the frozen
  pre-registration**; this draft is not frozen, and the estimate must be built
  from the R2 `ET8000` actuals (`…/R2/ET8000/` cost records) by whoever freezes
  it, not guessed here. **A proposal with no cost is disqualified — so this is a
  draft, and is labelled one.**
- **It does not re-mesh.** All arms reuse the R2 fine mesh; only the `topoSet`
  cylinder changes, which is what makes the sweep cheap and what makes it a clean
  one-variable experiment.

---

## 4. THE MECHANISM THAT DOES EXPLAIN THE DEFICIT — SUPERSEDED BY §5, KEPT FOR THE RECORD

If `Np` is 20 % low and zone size cannot explain it, the measured geometry
differences are the leading candidates: **baffle width `0.300 D` against the
paper's `0.100 D`**, and **blade/disc/baffle thickness `0.040 D` against `0.010 D`**
(`cases/navier_class/MRF/mesh/generate_geometry.py:35–38`). Both are documented
first-order drivers of a Rushton power number. **No source for that is on this
box**, so the direction is background and the magnitude is **unregistered**.

**The experiment that would settle it** is a thickness arm: our tank with
`BLADE_T = DISC_T = BAF_T = 0.001 m` (`0.010 D`, the paper's figure value),
everything else held, same zone. That is a **separate rung with its own
registration** — it changes the geometry, so it cannot ride inside a zone sweep
whose whole value is that it changes one thing.

*Drafted by a cfd `lab-lane`, 2026-09-12. NOT FROZEN. NOT LAUNCHED. Submissions
parked. No agent's message is Sanaa's consent.*

---

## 5. ADDED IN REVISION 2 — **THE BLADE-THICKNESS RUNG, WHICH NOW OUTRANKS THE ZONE SWEEP**

§4 was written when the box held **no** source that could quantify a thickness
effect. It now holds one, title-page verified:
`docs/papers/stirred_tanks_and_mixing/beshay_2001_acta_polytechnica_impeller_power_input.pdf`
— Beshay, Kratěna, Fořt & Brůha, *Power Input of High-Speed Rotary Impellers*,
Acta Polytechnica **41**(6) 2001. Its **small test rig is our tank, ratio for
ratio**: T = 0.300 m, H = T, four baffles at `b = 0.1 T`, D = 100 mm, D/T = 1/3,
l/D = 0.25, w/D = 0.2, D₁/D = 0.75, six blades, h/T = 0.33, water,
3×10⁴ < Re < 6×10⁴ (our Re = 5.0×10⁴ is inside). **Its measured power number is
`Po = 5.41`, by strain-gauge torquemeter.** The one ratio that differs is the one
that matters: **its impeller is `t/D = 0.0155`; ours is `t/D = 0.0400`.**

Correcting the measurement for that single dimension with the Bujalski et al.
(1987) correlation the same paper reproduces —
`Po = 2.512 (t/D)^-0.195 (T/T0)^0.063`, a **secondary-source** reproduction whose
range of validity the source we hold **does not state** — gives a thickness factor
of **×0.8312** and an **experiment-anchored prediction of `Np ≈ 4.50` for our
tank**. Our ungraded fine-level value is **4.382**, i.e. **2.6 % low**, on the
side that steady MRF is documented to err and that this case's own R1
pre-registration §3 predicted before any compute.

**THE RUNG.** One arm, one change, on the existing fine mesh with the existing MRF
zone held at 1.200 D × 2.00 W: rebuild the geometry with
`BLADE_T = DISC_T = BAF_T = 0.00155 m` (`t/D = 0.0155`, Beshay's own impeller) in
`cases/navier_class/MRF/mesh/generate_geometry.py`, and re-solve the three levels.

**PREDICTION, CARRIED BEFORE THE DATA.** `Np` lands in **5.2 to 5.4**. If it does,
thickness is the mechanism, our 4.382 was correct for our tank, and the case gains
an **experimental** anchor at its own geometry. **If it does not, §11.4 of
`verification/campaign/MRF_PAPER_REGISTRATION_REID2025.md` is refuted** and the
deficit is something else — which is the point of writing the prediction down
first.

**WHY IT OUTRANKS THE ZONE SWEEP.** The zone sweep measures a sensitivity we
should have and cannot currently exonerate. The thickness rung tests a **named,
quantified, falsifiable mechanism against an experiment at our own tank ratios**,
and it is the same cost. **It should be frozen and run first**; the zone sweep
follows, on its own merits, unchanged.

**Still not frozen, still not launched, and this section carries no cost estimate
either** — rule 12 requires the estimate in the frozen document, built from the R2
`ET8000` actuals by whoever freezes it.

*Revision 2 by a cfd `lab-lane`, 2026-09-12. NOT FROZEN. NOT LAUNCHED.*

---

## REVISION 3 NOTE — 2026-09-12, scope of Sanaa's ruling recorded

Her ruling of this evening, relayed: *"we dont need to do the fine mesh conv,
provided that we dont have exactly the same thickness or exactly same dimensions;
if we do but we dont record the same values, thats an issue."*

**What it drops:** the three-level re-run-from-zero grid family that §5's
thickness rung was to sit behind. That family is **not drafted further, not frozen
and not launched**. The thickness rung is now a **single-grid** run with its own
document, `verification/campaign/MRF_R4_PREREGISTRATION.md`, which supersedes §5
of this draft — **§5 is struck and left legible**, as the record of where the rung
came from.

**What it does NOT drop:** this zone sweep. It is a **sensitivity**, not a
convergence family, and her ruling is about grid convergence. It stays drafted,
unfrozen and unlaunched, **behind R4**, and its purpose is unchanged: a parameter
with no sensitivity behind it is a default (L-561).

*Revision 3 by a cfd `lab-lane`, 2026-09-12.*
