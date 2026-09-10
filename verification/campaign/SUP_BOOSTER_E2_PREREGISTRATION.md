# SUP_BOOSTER — Case-3 EXACT-tier (E2) pre-registration — Taylor-Maccoll cone, §2bc successor to E1

**STATUS: DRAFT / UNFROZEN.** Prepared by a cfd lab-lane. **Not frozen**: the freeze
(commit + blob-sha pin) and the graded launch are the **cfd-supervisor's check-1 (new grader
diff) + check-4** and are not taken here.

**§2bc fix-until-runs successor to SUP_BOOSTER E1** (E1 RUN VERDICT `NOT A RESULT`, verdict
record `SUP_BOOSTER_E1_VERDICT.md`, frozen prereg `c8510ff7`). This is a **diagnosed,
pre-registered, costed** successor — not a blind retry, and not a silent edit to frozen E1
(rule 6). E1's physics was corroborated (shock at r=0.40 vs TM 0.401; cone-surface Cp within
0.13–0.21% of TM at coarse/medium); the two failures were **instrument/mesh robustness**, and
E2 fixes exactly those two, changing nothing else.

## 1. What E1 diagnosed, and the E2 changes

- **Cause A (Gate C2 refuse):** E1's shock locator used max |Δρ/Δr|; the aggressive radial
  grading (`GR_RADIAL=12`) made near-wall cells so thin that small compression-region wiggles
  gave spurious large |Δρ/Δr| at r≈0.2–0.27, so the fitted shock line was not apex-anchored
  and the grader refused.
  **E2 change 1 — robust shock locator (freestream-density-boundary crossing).**
  `grade_sup_booster_e2.py::read_shock_angle` now scans each radial column **from the outside
  (undisturbed freestream) inward** and takes the shock as the outermost radius where density
  first exceeds the **per-station local freestream** (the outermost cell) by `SHOCK_EPS=0.03`.
  It never reaches the clustered near-wall region, so near-wall wiggles cannot be mistaken for
  the shock. **Proven on all three E1 graded solutions: β = 33.695° / 33.994° / 33.848°**
  (TM 33.9147°), all within ±0.30° and apex-anchored (intercepts 0.013–0.017 ≪ 5% L), with
  station radii growing linearly (0.25→0.58) like a true conical shock.
- **Cause B (Gate C1 DIVERGENT triple):** E1's fine-grid near-wall cell was so thin that
  shock-capture noise broke the cone-surface Cp Roache triple (p≈7.5, fine value diverged).
  **E2 change 2 — gentler radial grading (`GR_RADIAL 12 → 5`)** in `gen_cone_mesh_e2.py`. A
  more uniform near-wall distribution lets the owner-cell surface pressure converge
  monotonically (offset r_wall+Δy/2 → wall value as ~1/N) while still clustering enough to
  resolve the shock. E1 coarse/medium were already within 0.14% of TM, so a monotone triple
  is expected to CONVERGE.

- **Change 3 — C2's GATING METHOD**, per the verification-supervisor's ruling `0e9c1bcb`.
  Not a physics or mesh change and not cfd's design decision: see §3, §3.1–§3.4.

**Everything else is byte-identical to the vetted E1 grader** (rule-3 planted-zero, rule-4
completion `p U T rho` + age guard, **C1's** rule-5 Roache/Celik + iterative plateau, the
cone-Cp owner-cell plateau reader with spatial Cx-sort trim, refuse-not-degrade, exit
vocabulary) and to the E1 case (inviscid Euler, slip wall, M∞=2.0, θ_c=15°, wedge axisymmetry,
BCs, farfield).

### 1.1 Two locator constants that were ASSERTED, now MEASURED (cfd-supervisor check-1 conditions)

Both were carried into the E2 draft without a stated basis. An undocumented tuned constant in a
measurement path is what gets a grader distrusted later, so both are now measured on solutions
already on disk — the three E1 graded levels at endTime 15000 (same solver, same BCs, same
axial mesh; E2 differs from E1 only in radial grading). **No solver was run for this.**

- **`SHOCK_EPS = 0.03`** was justified as "≫ the uniform-freestream noise floor, ≪ the conical
  shock jump ~10–20%". **The bracket holds, with margin, and is now written into the comment
  with its numbers:**
  - *Lower bound — the noise floor.* Max |ρ/ρ_∞ − 1| over the undisturbed outer column
    (cells at r ≥ 1.15 r_shock, all six stations): **coarse 1.9×10⁻⁶, medium 8.5×10⁻¹⁰, fine
    exactly 0**. `SHOCK_EPS` sits **≥1.6×10⁴×** above the worst of these. The fine-grid **zero
    is planted-verified** (rule 3): planting 1.234×10⁻³ into one far-field cell made the same
    reader report 1.234×10⁻³, so the zero comes from a reader shown able to see a non-zero.
  - *Upper bound — the signal.* Density rise just behind the shock foot, over all six stations
    and all three levels: **18.2–21.5%** (theory: the normal-Mach relation at β=33.9147°,
    M_∞=2 gives **19.6%**). Total compression to the cone surface, coarse and medium:
    **37.3–37.8%** (theory **37.8%**). `SHOCK_EPS` is **6.1× below** the smallest measured
    shock jump and **12× below** the wall compression.
  - *Recorded, not used as a bound.* On the E1 **fine** grid the near-wall density maximum
    reaches **89%**, far above the 37.8% cone-surface value. That overshoot is E1's
    `GR_RADIAL=12` near-wall pathology — the very failure E2's gentler grading targets, and
    independent corroboration of Cause B in §1. It lies in the cone-surface region, not at the
    shock, and the locator stops at the **outermost** crossing, so it cannot reach it.
  - *Honest note, not a defect.* Because the 3% crossing lies 3–5 cells inside a shock smeared
    over 4–7 cells, the located radius carries a systematic inward offset of a few cells that
    shrinks with the mesh. That offset is precisely why β does not Richardson-extrapolate and
    why the locator increment, not a GCI, is the right uncertainty channel for it — it supports
    the `0e9c1bcb` framing rather than undermining it.
- **The station band, `0.03·L → 0.02·L`.** Narrowed in the E2 draft with **no stated basis**.
  It is now the named grader constant `STATION_HALFWIDTH` with the arithmetic in its comment,
  and it is **kept at 0.02**:
  - *Why narrow.* r_s = x·tan β = 0.6725x, so a half-width w·L smears the located radius over
    ±0.6725·w·L: **±0.0201 m at w=0.03, ±0.0134 m at w=0.02**. Against the E2 fine radial cell
    at the shock (0.00495–0.00704 m) that is **5.1–8.1 cells at w=0.03 versus 3.4–5.4 at
    w=0.02** — a 33% reduction, exactly proportional. The locator scans inward and stops at the
    first crossing, so the smear enters as a systematic **outward** bias on every located
    radius.
  - *Why not narrower.* The band must still hold **≥2 axial columns at every station on the
    coarsest grid**. Measured at w=0.02 on coarse: **3, 3, 2, 2, 2, 2** columns — already at
    the floor. The axial cell at the last station is 0.0223 m there, so w=0.015 would span
    0.0296 m and could isolate a single column. **0.02 is the narrowest admissible width, not
    a tuned value.** Column counts at w=0.02: coarse 3–2, medium 5–2, fine 7–4.
  - *Measured, not asserted:* the E2 fine radial cell sizes come from the blockMesh
    `simpleGrading` law, validated to 1% against the E1 fine mesh on disk (predicted
    0.00449–0.00799 m vs measured 0.00445–0.00791 m). Marked **INFERRED** for E2 until the E2
    fine solution exists; the grader measures them at runtime and gates on the measurement.

## 2. EXACT reference (unchanged from E1, sound)

Regenerated Taylor-Maccoll ODE reference, reused byte-identical:
`taylor_maccoll_reference.py` → `tm_reference_M2p0_tc15.json` (β=33.9147°, M_c=1.70687,
**Cp=0.202248**, pc/p∞=1.56629; ODE grid-independent to 1e-13). No external PDF.

## 3. Gates, thresholds, labels (E1 bands reused; C2's gating METHOD reframed by ruling `0e9c1bcb`)

Gate **C1** is decided only through the Roache triple (Celik F_s=1.25); non-CONVERGING or
not-plateaued → NOT A RESULT (rule 5). GCI printed. Gate **C2** is decided by value-in-band +
a separate tighter consistency bound, with **no Roache instrument applied to it at all** — see
the ruling and its conditions below. **Rung PASS iff BOTH gates PASS**; C2 cannot rescue C1.

- **Gate C1 — cone-surface Cp (PRIMARY).** PASS iff **|Cp_fine − 0.202248| ≤ 0.010** and the
  triple is CONVERGING; else GATE FAIL / NOT A RESULT. **Unchanged in every particular.**
- **Gate C2 — conical shock angle β (SECONDARY).**
  - **ACCURACY.** PASS iff **|β_fine − 33.9147°| ≤ 1.0°**. Band and reference **UNCHANGED**.
  - **CONSISTENCY.** PASS iff **max|β_i − β_j| ≤ B_cons = 0.60°** over the three levels.
  - **REPORTING.** β_fine is reported **with its sub-cell locator increment**, always.
  - **PRECONDITION.** The band must strictly exceed the fine-grid locator increment. If it does
    not, C2 is measuring locator resolution rather than accuracy, the registered framing does
    not hold, and C2 is **NOT A RESULT** — not GATE FAIL, because the instrument and not the
    solution is what failed. The grader may not substitute another gate at grade time (rule 2).
  - **FORBIDDEN INSTRUMENT.** No Roache triple, GCI, observed order or Richardson value is
    computed, printed or reported for C2.

### 3.1 GOVERNING RULING — verification-supervisor, 2026-09-09, commit `0e9c1bcb`

`verification/campaign/SUP_BOOSTER_E2_C2_SHOCK_ANGLE_GATING_RULING_2026-09-09.md` **GRANTS
framing (ii) and GOVERNS.** Its eight conditions are binding and are implemented in
`grade_sup_booster_e2.py`. Gate design under standing rule 5 is verification's charter
territory, not cfd's.

**Legality as a pre-first-compute amendment (rule 2).** *Condition, and how it was checked:*
the E2 graded run root `verification/runs/navier_class/SUP_BOOSTER/graded_e2/` **does not
exist** — checked 2026-09-10, `ls -d` reports "No such file or directory", and the earlier
plant-verified absence check at 2026-09-10T04:04:39Z (`os.path.exists`/`lexists`/`isdir` all
False, with the reader shown able to see a non-absence in the same invocation by creating and
removing the directory, standing rule 3) stands. **No byte of E2 graded compute has been
bought.** The sibling root `graded/` holds **E1's** compute only, under E1's separate freeze
`c8510ff7` and E1's pinned grader `3c8d418a`.

**Where each condition landed.**

| # | condition | where |
|---|---|---|
| 1 | C1 stays the primary Roache-gated accuracy gate; rung PASS needs both | §3 above; C1 path byte-unchanged in the grader |
| 2 | no band, reference or threshold moves | §3 above; `CP_BAND`, `BETA_BAND_DEG`, TM values unchanged |
| 3 | β_fine reported with its sub-cell locator increment | grader `read_shock_angle` → `locator_increment_deg()`; printed in the C2 report as `beta_fine_reported_as` |
| 4 | the band must exceed the locator increment | §3.2; enforced in `grade_gate_shock_angle` as a NOT A RESULT precondition |
| 5 | consistency is a separate, tighter, pre-registered bound | §3.3, `B_cons = 0.60°`, constant `BETA_CONS_DEG` |
| 6 | C2's locator is the one that passed check-1 | unchanged apex-anchored freestream-crossing locator; β reproduces 33.6946 / 33.9943 / 33.8479° bit-identically after the change |
| 7 | one localized grader change, pre-registered and frozen before compute | commit `8f77d94c`; freeze still held for the supervisor's check-1 + check-4 |
| 8 | no Roache instrument quoted for C2 | grader computes none, and `run_grade` asserts none of `triple`/`apparent_order_p`/`gci_fine`/`richardson_extrap` appears in the C2 report (exit 70 if it does); selftest asserts the same on all four C2 branches |

### 3.2 Condition 4 — the fine-grid locator increment, STATED

The locator increment is the angular quantum of this instrument: each station's located radius
is quantised by one local radial cell `dr_i`, and that quantum propagates through the same
least-squares slope the locator fits. The grader **measures** `dr_i` at runtime from the single
axial column nearest each station and reports three figures. The **registered** increment is
the rms one — independent one-cell quantisation at every station, propagated in quadrature.

| level | dr at the shock (m) | locator increment Δβ_loc (deg) — rms, REGISTERED | single-station | correlated-worst |
|---|---|---|---|---|
| E1 coarse (measured) | 0.01045–0.01802 | 1.3913 | 1.0215 | 2.8649 |
| E1 medium (measured) | 0.00714–0.01225 | 0.9364 | 0.6896 | 1.9345 |
| E1 fine (measured) | 0.00475–0.00814 | **0.6243** | 0.4596 | 1.2965 |
| E2 fine (INFERRED) | 0.00495–0.00704 | **≈0.59** | ≈0.41 | ≈1.24 |

The E2 row is **INFERRED**, not measured: the E2 mesh has no solution yet. It comes from the
blockMesh `simpleGrading` law at `GR_RADIAL=5`, `nr=135`, scaled by the 1.038 ratio by which
the same computation under-predicts the E1 fine mesh it can be checked against (predicted
0.6015° vs measured 0.6243°). The underlying cell sizes agree with the E1 mesh on disk to 1%.
**The grader re-measures this on the actual E2 fine solution and gates on the measured value,
never on this table.**

**CONDITION 4 IS SATISFIED: 0.59° < 1.0°, a factor 1.7.** Stated plainly because the margin is
not large: this is a factor 1.7, not a factor 10. The adversarial correlated-worst figure
(≈1.24°) does **not** clear the band — it is reported by the grader and is disclosed here, but
it is a conspiracy of sign patterns across all six stations, not the instrument's resolution;
E1's observed rung-to-rung spread of 0.2997° is half the rms figure and a quarter of the
correlated-worst one, which is the empirical evidence that the rms scale is the right one.

### 3.3 Condition 5 — B_cons = 0.60 deg, and its derivation

**`B_cons = 0.60°`** (grader constant `BETA_CONS_DEG`; the grader does **not** compute it at
runtime — it is a pre-registered number, frozen with this document).

**Primary derivation, prior to and independent of any E2 or E1 β value.** The rung-to-rung
spread of a discretely-located quantity is bounded below by the locator's own quantum. Setting
`B_cons = 1.0 × Δβ_loc,fine`: three values agreeing to within one fine-grid angular cell are
consistent; a spread larger than one fine cell is not explicable by the fine locator's
resolution and is a real consistency failure. Δβ_loc,fine ≈ 0.59° (§3.2) → **B_cons = 0.60°**.

**Cross-checks, not the derivation.**
1. 0.60° is 1.5 × the single-station one-cell increment on the E2 fine mesh (≈0.41°).
2. 0.60° is **3.3× tighter** than the 2.0° that re-using the ±1.0° accuracy band would imply.
   Condition 5 calls that re-use "toothless" and it is: any three values within 1.0° of the
   reference are trivially within 2.0° of each other. B_cons is load-bearing.
3. It is sub-degree, as condition 5 requires.
4. The only measured rung-to-rung spread of this locator on a corroborated solution — E1's
   three graded levels, **0.2997°** — sits at half of it.

**THE COST OF THIS BOUND, ACCEPTED AND STATED BEFORE COMPUTE.** The **coarse** grid's own
locator increment is ≈1.3° — more than twice B_cons. If coarse-grid quantisation dominates the
E2 spread, C2 **GATE FAILs** on consistency and the rung is not a PASS even if C1 passes. That
is a registered possible outcome of a bound with teeth, not a defect of the case, and it is
written here before the run so that it cannot be renegotiated after it.

### 3.4 WITHDRAWN — the cfd framing-(i) ruling of 2026-09-10 (struck, not deleted)

**STRUCK IN FULL AND WITHDRAWN by the cfd-supervisor, 2026-09-10.** It is preserved verbatim
below because the lab strikes originals rather than rewriting them (rule 6 discipline), and
because a reader is entitled to see what was decided against and why it was reversed.

**The cfd-supervisor's reason for withdrawing it, as he stated it:** verification's framing
rests on precedent that **predates this case** (DMR Gate P2, F19, F4S — verified at source by
verification, not taken from cfd's citation), and its conditions 4 and 5 are **stricter** than
the framing cfd had objected to — condition 5 expressly forbids re-using the ±1.0° accuracy
band as the consistency bound, calling that "toothless". The gate-fitting objection recorded in
struck reason 1 below therefore does not bite: the bound that decides C2's consistency
(B_cons = 0.60°) is **tighter** than anything framing (i) would have imposed, and it is derived
from the locator increment rather than from the known β values. Gate design under standing
rule 5 is verification's charter territory, not cfd's. **The conflict recorded in the struck
text below is resolved by withdrawal, not by arbitration; nothing goes to Sanaa.**

> ~~**SUPERVISOR RULING — 2026-09-10 — cfd-supervisor — FRAMING (i) RULED. THE GRADER IS NOT
> CHANGED.** RULED: (i). NOT (ii). Reason 1: gate-fitting is the deciding argument — E1's three
> beta values (33.70/33.99/33.85) are already known to be non-monotone while inside the ±1.0°
> band, so choosing (ii) with that outcome in hand would convert a likely NOT A RESULT into a
> likely PASS. Reason 2: (i) is the status quo, so the freeze requires no instrument edit.
> Reason 3: I accept the likely cost — if beta wiggles again the triple is OSCILLATORY, C2 is
> NOT A RESULT, and the rung is NOT A RESULT even though C1's physics may be corroborated to
> 0.13–0.21%. Reason 4: separately, the general question is referred to verification as a
> standards question. — Also struck with it: the "CONFLICTING RULING OF RECORD — DISCLOSED, NOT
> RESOLVED HERE" note recorded by the preparing lane on 2026-09-10, which held that reconciling
> the two rulings was cross-family arbitration reserved to Sanaa. It is not: the cfd ruling has
> been withdrawn by its author.~~

**The question that was before the supervisor, preserved so a reader can see both options.** A
captured shock's located radius wiggles at the sub-cell level across grids, so the β Roache
triple may be OSCILLATORY even with a correct locator (on the E1 solutions the three β were
33.70/33.99/33.85 — all within ±0.30° of TM and inside the ±1.0° band, but not monotone). Two
admissible framings were before the lab — **(i)** keep C2 as a Roache-gated gate
(OSCILLATORY → NOT A RESULT); or **(ii)** the DMR precedent: report β_fine with its locator
increment as a measurement and gate accuracy plus a separate consistency bound, with no Roache
triple. **(ii) governs, per `0e9c1bcb`.**

- **Labels:** fixed vocabulary. Rung PASS iff both gates PASS.

## 4. Grid triple for Celik F_s=1.25 (E2 gentler grading)

`gen_cone_mesh_e2.py`, r=1.5 uniform (2.25× cells/level). All three meshed clean at pre-flight:

| level | cells | max non-orth | max skew | neg-vol | h (rel) |
|---|---|---|---|---|---|
| coarse | 6,000 | 14.94° | 0.667 | 0 | 2.25 |
| medium | 13,500 | 14.95° | 0.668 | 0 | 1.50 |
| fine | 30,375 | 14.96° | 0.668 | 0 | 1.00 |

Hard gates PASS (≤70° non-orth, ≤4.0 skew, 0 neg-vol). Graded endTime = 15000 LTS
pseudo-iterations (deltaT=1, writeInterval 1000); iterative plateau enforced by the grader
(rule 5 clause 1). The grader asserts the actual 2.25× cell-count family (refuse otherwise).

### 4.1 REGISTERED RUN ROOT and LAUNCHER

| what | path | status |
|---|---|---|
| E2 graded run root | `verification/runs/navier_class/SUP_BOOSTER/graded_e2/` | **verified ABSENT** 2026-09-10 (§3.1) |
| E2 launcher | `verification/runs/navier_class/SUP_BOOSTER/run_graded_triple_e2.sh` | written 2026-09-10 |
| E2 autograder | `verification/runs/navier_class/SUP_BOOSTER/autograde_sup_booster_e2.sh` | written 2026-09-10 |

**The run root is `graded_e2/`, and it is NOT `graded/`.** `graded/` exists and holds **E1's**
three graded levels and E1's refusal text. E1's launcher `rm -rf`s each level before it runs,
so pointing E2 at `graded/` would **destroy E1's evidence** and defeat the rule-4 age guard.
The E2 launcher writes only under `graded_e2/` and names E1's root nowhere.

**The E2 launcher pins the E2 grading path** — `grade_sup_booster_e2.py` and
`gen_cone_mesh_e2.py` — and carries **this document's 60 core-min cap**, not E1's 90, as
per-level wall timeouts **800 / 1200 / 1600 s** (sum **3600 s = 60 core-min at 1 rank**,
exactly the registered cap). The split gives every level headroom over its E1 measured wall
time — coarse 800/243 = **3.3×**, medium 1200/501 = **2.4×**, fine 1600/1107 = **1.45×** — with
the tightest margin on the level that dominates the bill, which is where an LTS surprise (§5)
would show first. A level that hits its timeout is **stopped** (rc 124) and does not get a new
budget (rule 12); the grader then refuses it on rule-4 completion. The timeout bounds the
**solver** wall as E1's launcher did; `blockMesh` and the generator run outside it and cost a
few seconds per level, so the enforced ceiling is the cap plus that, not below it. Real exit codes are captured **inside** the detached wrapper —
`setsid timeout cmd` returns 0 for every outcome, so a rc read around the `setsid` line is
meaningless.

**Queue-entry note.** `scripts/queue_entry_check.py` does **not** verify that `launch_cmd[1]`
exists: an entry naming an absent launcher validates cleanly and then dies at launch behind a
stale LAUNCHED record. The launcher above exists on disk before any entry is placed.

## 5. Compute cap and cost basis

Point estimate from the E1 measured actual (same solver/endTime, near-identical cell counts):
**~31 core-min**; **CAP = 60 core-min** (≈2× margin). cost_basis: c7a.4xlarge at
**$0.0513/core-h** (owner-stated; box cannot read its own billing → **derived, not measured**,
COMPUTE_BUDGET_CHARTER §5). Derived cost at the cap: 60/60 × $0.0513 = **$0.0513 (derived)** —
under the $25 pre-auth. Overrun stops the run (rule 12). Serial (1 rank), sequential
coarse→medium→fine (good citizen). Estimate-vs-actual calibration filed to
`docs/COST_CALIBRATION.md` at completion.

**THE LIKELIEST-WRONG TERM IN THIS ESTIMATE, NAMED BEFORE THE RUN.** The 31 core-min anchor is
E1's measured actual (30.85 core-min serial: coarse 243 s + medium 501 s + fine 1107 s,
`docs/COST_CALIBRATION.md` row `C-20260909T214553.000000Z-supbe1`) at **identical cell counts**.
But E2 changes `GR_RADIAL` 12 → 5, and the local time step of an LTS run is set by the local
cell size: a gentler near-wall distribution changes the local Δt field and therefore
**iterations-to-plateau at the fixed endTime 15000** — a quantity that has **never been measured
on the E2 mesh**. The wall time per iteration should carry (same cell count, same solver), but
the *number of useful iterations before plateau* need not. If E2 needs materially more wall
time per level than E1 did, the per-level timeouts in §4.1 stop it and the run is reported
stopped, not extended. **The cap is NOT changed on account of this risk** — naming a risk is
not a reason to buy more budget (rule 12).

## 6. Planted-zero (rule 3), completion (rule 4), refuse-not-degrade — unchanged from E1

Byte-identical to the vetted E1 grader: PLANT=1000.0 Pa into a cone owner-cell of a copy of the
finest `p`, read back through the same reader, refuse unless seen; rule-4 completion (rc 0,
End, last==endTime, `p U T rho` present and newer than 0/T); refuse (exit 2) not degrade;
exit 70 only for an internal defect. Verified live: planted-zero PASSED on the smoke case
(reader delta 10.6383 = 1000/94 exact); all three Roache verdict branches classify correctly.

## 7. Cross-cuts (unchanged from E1)

Celik F_s=1.25 (§4); Menter y+ N/A for the inviscid slip-wall rung (binds the MEASURED-tier
successor, PENDING-data); Spalart–Rumsey farfield (R_top 1.2 > L·tanβ 0.673, shock exits the
outlet); curvature LE-check geometrically inapplicable to a sharp cone (controls behave);
blockage N/A (unbounded external cone).

## 8. Amendment provision

Before first graded compute, amendments legal with a stated condition. After first graded
compute the gate/threshold/cap/label are closed (rule 2). The grading path (grader +
generator) is pinned by blob sha at the freeze commit and hashed against the committed blob
(scripts/check_comparator_freeze.py).

## 9. §2bb pre-flight — verdict at draft

| screen | result |
|---|---|
| E2 robust locator recovers the shock angle | β 33.70/33.99/33.85° on the three E1 solutions, all within ±0.30° of TM, apex-anchored — PASS |
| 3 E2 meshes admissible | non-orth ≤14.96°, skew ≤0.668, 0 neg-vol — PASS |
| Solver stability (E2 smoke, gentler mesh) | rc 0, End, last time == endTime 300, wall 10 s — PASS |
| Planted-zero control fires | reader sees 1000 Pa exactly — PASS |
| Roache verdict branches | CONVERGING→PASS, OSCILLATORY→NOT A RESULT, CONVERGING-outside-band→GATE FAIL — PASS |
| Reference regenerable, grid-independent | reused E1 frozen JSON (1e-13) — PASS |
| C2 gate branches under ruling `0e9c1bcb` | in-band+consistent→PASS, out-of-band→GATE FAIL, spread>B_cons→GATE FAIL, locator increment ≥ band→NOT A RESULT — PASS |
| Condition 8, executable | no `triple`/`apparent_order_p`/`gci_fine`/`richardson_extrap` key in any C2 report; asserted in `run_grade` and in all four selftest branches — PASS |
| Locator unchanged by the condition-7 edit | β reproduces 33.6946 / 33.9943 / 33.8479° on the three E1 solutions, bit-identical to §1 — PASS |
| Condition 4 satisfied on the E2 fine mesh | Δβ_loc ≈ 0.59° < band 1.0°, factor 1.7 (INFERRED; re-measured at runtime) — PASS, margin stated as modest |
| `SHOCK_EPS` bracket measured, not asserted | noise floor ≤1.9e-6 (fine zero planted-verified), shock jump 18–20% — PASS |
| Station half-width has a numerical basis | 0.02·L is the narrowest width keeping ≥2 axial columns at every coarse station — PASS |
| E2 run root distinct from E1's | `graded_e2/` verified absent; launcher names E1's `graded/` nowhere — PASS |

**§2bb pre-flight verdict: ADMISSIBLE** — awaiting supervisor check-1 (new grader diff) + freeze (check-4).

## 10. Frozen grading path (pinned by git blob sha) — TO BE COMPLETED AT FREEZE

*(The supervisor pins these at the freeze commit; left as a placeholder table so the freeze
edit only fills the shas — the checker parses only `|`-table rows.)*

| file (pinned grading path) | git blob sha |
| --- | --- |
| `verification/runs/navier_class/SUP_BOOSTER/grade_sup_booster_e2.py` | TO BE PINNED AT FREEZE |
| `cases/navier_class/SUP_BOOSTER/gen_cone_mesh_e2.py` | TO BE PINNED AT FREEZE |

Provenance (non-.py): reused frozen reference tm_reference_M2p0_tc15.json git blob
c442a94bfd3166e443124e92248c5d96a929d8a5 (unchanged from E1).

---

*Artifacts:* new grader `verification/runs/navier_class/SUP_BOOSTER/grade_sup_booster_e2.py`;
E2 launcher `.../run_graded_triple_e2.sh` and autograder `.../autograde_sup_booster_e2.sh`;
governing ruling `verification/campaign/SUP_BOOSTER_E2_C2_SHOCK_ANGLE_GATING_RULING_2026-09-09.md`;
gentler generator `cases/navier_class/SUP_BOOSTER/gen_cone_mesh_e2.py`; E2 mesh checks
`verification/runs/navier_class/SUP_BOOSTER/e2_meshcheck_{coarse,medium,fine}/`; E2 smoke
`.../e2_smoke_medium/`; E1 verdict `verification/campaign/SUP_BOOSTER_E1_VERDICT.md`.
*DRAFT / UNFROZEN — new-grader diff (check-1) + freeze + launch are the cfd-supervisor's.*
