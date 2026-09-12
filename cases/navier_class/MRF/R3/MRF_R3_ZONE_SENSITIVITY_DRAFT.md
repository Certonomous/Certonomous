# MRF_R3 (DRAFT) — MRF ZONE SIZE AS A REGISTERED PARAMETER WITH A MEASURED SENSITIVITY

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

## 1. WHY THIS RUNG IS NOT WHAT THE DIRECTIVE ASSUMED, AND WHY IT IS STILL WORTH RUNNING

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

## 4. THE LEADING ALTERNATIVE HYPOTHESIS, REGISTERED SO IT IS NOT LOST

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
