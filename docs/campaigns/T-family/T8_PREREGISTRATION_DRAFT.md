# T8 entry rung — MTT pure-plume self-similarity: pre-registration (template form)

# **DRAFT — NOT ARMED, awaiting supervisor read.**

**Status: DRAFT. NOT FROZEN. NOT ARMED. ZERO COMPUTE SPENT.** Nothing in this
document gates anything until the heat-transfer supervisor has read it as a diff
and committed it as frozen. **No solver may be launched against it in its present
state.** Written 2026-08-25 by a heat-transfer lane, on Sanaa's 10-line template
("standard verification/validation cases use the 10-line prereg form"), plus the
cost registration rule 12 makes non-optional.

**Why this case, and why now.** It is the **next spine item that is neither
stalled nor on Sanaa's desk.** The DC spine (H-2) is `T3 → T5 → T8 → T12 → K2`:
T3 is stopped at gate (1) of its own §7.1 and needs a fourth mesh level with its
own 150–200 core-h registration; T5's pre-registration is a draft with 12
INTERPRETATIONs on Sanaa's desk. **T8 is next, its reference is closed form so
nothing needs acquiring, and it moves matrix cell C7 — `axisymmetric ×
buoyant-thermal`, currently `V NONE / G NONE / P NONE / NEVER RUN` — off zero.**

---

1. **Case.** `T8_MTT_c`, `T8_MTT_m`, `T8_MTT_f` at
   `verification/runs/T-family/T8_runs/` — an axisymmetric (5° wedge) turbulent
   pure plume rising from a small circular buoyancy source of diameter `D` into a
   quiescent, unstratified, adiabatic-walled domain of radius `12 D` and height
   `40 D`, solved steady with `buoyantBoussinesqSimpleFoam`, standard `kEpsilon`,
   `Prt` 0.85, gravity `-9.81 m/s²` in `z`. **No case directory exists at the
   moment this draft is written**, and the arming guard (rule 4) must refuse if
   `0/` or any time directory is already present when the run is launched.

2. **Reference.** **Morton, Taylor & Turner (1956) top-hat plume theory** — the
   closed-form self-similar solution for a pure plume from a point source of
   buoyancy flux `F0` in an unstratified environment. **It is derived in this
   document, not cited from a file**, so no paper acquisition blocks this rung and
   rule 15 does not apply. The three far-field power laws, exact consequences of
   the MTT conservation equations and **independent of the entrainment coefficient
   `α`**, are: centreline vertical velocity `w ∝ z^(-1/3)`; centreline temperature
   excess `ΔT ∝ z^(-5/3)`; volume flux `Q ∝ z^(+5/3)`. The plume radius law
   `b = (6α/5) z` **does** carry `α` and is therefore **REPORT-ONLY**, never graded.

3. **Quantities.** Three graded exponents, each obtained by ordinary least squares
   of `log(quantity)` on `log(z - z0)` over the registered window, plus one
   report-only number:
   - `n_w` — exponent of centreline `w(z)`. Exact value **−1/3 = −0.33333**.
   - `n_T` — exponent of centreline `ΔT(z) = T(z) − T_amb`. Exact **−5/3 = −1.66667**.
   - `n_Q` — exponent of `Q(z) = ∫ 2πr·w dr` over the plume cross-section. Exact **+5/3 = +1.66667**.
   - `α` — entrainment coefficient from the fitted radius slope, `α = (5/6)·db/dz`.
     **REPORT-ONLY, ungraded**, quoted beside the published 0.11–0.13 range for
     pure plumes as context and **not as a gate**.

4. **Bands.** Frozen here, before any solver runs, and **not derived from any run
   of this case**: **`n_w` ∈ [−0.3833, −0.2833]`, `n_T` ∈ [−1.7167, −1.6167]`,
   `n_Q` ∈ [+1.6167, +1.7167]` — that is ±0.05 absolute on each exponent.** These
   are **modelling-tolerance bands, not numerical-error bands**: MTT is an
   asymptotic self-similar theory and a steady RANS plume is not obliged to
   reproduce it to machine precision, so a tight band would grade the closure and
   claim to grade the code. **±0.05 is registered as the widest band that still
   discriminates**: it excludes the two nearby wrong answers — a jet
   (`n_w = −1`, `n_Q = +1`) and a non-entraining column (`n_w = 0`) — by more than
   twelve band widths. **The fit window is frozen as `z/D ∈ [10, 30]`**, chosen to
   sit clear of the source near field below and of the outlet influence above; the
   virtual origin `z0` is refit independently at each grid level and its spread
   across the three levels is **reported as a control**, not gated.
   **No band may be widened, narrowed or reinterpreted after the first solver starts.**

5. **Ladder.** T-family, DC spine position 3, rung **T8**, entry arm. **Three grid
   levels at refinement ratio `r = 2` exactly in both directions** — the lab's
   Roache-standard minimum as ruled 2026-08-25 — `c` 40×160 = **6,400** cells,
   `m` 80×320 = **25,600**, `f` 160×640 = **102,400**. Iteration counts
   **8,000 / 12,000 / 20,000**. GCI at **`Fs = 1.25`**. **CLAUDE.md rule 5 binds
   without exception**: any level not iteratively converged or not plateaued sends
   the row to `NOT A RESULT` at gate (1) before the triple is consulted; a triple
   that is `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` sends it to
   `NOT A RESULT` at gate (2) with both triples and both orders printed beside it;
   only a `CONVERGING` triple reaches the band. **No GCI is quoted when the three
   values are not monotone.**

6. **Decomposition seed.** **Serial, 1 rank, no decomposition** — `nProcs = 1`, no
   `decomposeParDict` is written, `decomposePar` is not run, and each solver is
   invoked directly rather than through `mpirun`. **There is no partitioner and
   therefore no seed to record.** *This field is recorded because the form requires
   it, not because the value is in doubt.* If the concurrency directive later moves
   this rung to a parallel batch, that is a **new registration**, not an amendment:
   the decomposition method and seed would then have to be pinned before any run.

7. **Criteria.** Per exponent, in this order, no other order permitted:
   (1) all three levels iteratively converged (last-two-checkpoint relative change
   `≤ 1e-6`) **and** plateaued, else **`NOT A RESULT`**;
   (2) triple `CONVERGING`, else **`NOT A RESULT`** with both triples and orders printed;
   (3) `PASS` if the Richardson-extrapolated value lies inside its §4 band, else **`GATE FAIL`**, GCI printed either way.
   **Strict completion (rule 4) is required of every level before it is read**:
   `rc = 0` **recorded to a file, not inferred from the log**; an `End` line; last
   time == `endTime`; fields `T U p_rgh alphat nut k epsilon` present at `endTime`
   — **`epsilon`, not `omega`, because the closure is `kEpsilon`**; `ExecutionTime`
   count == `endTime`; and **every field at `endTime` newer than the case's own
   `0/T`** (the age guard). A level failing any clause is not read at all.

8. **Cost, and a real cap.** **Predicted 335.3 core-minutes total** — `c` 7.1,
   `m` 42.8, `f` 285.4 — from a **measured** lab rate of **1.196e5
   cell·steps/(core·s)**, derived from `K2bU3_L025` (11,600 cells × 1,918 steps in
   3.100 core-minutes, `verification/runs/F14-cooling-ladder/K2b_runs/K2bU3_L025/COST.txt`),
   the same 2D Boussinesq solver family on this box. At $0.0513/core-h that is
   **$0.287 derived, not measured** — the box cannot read its own billing.
   **CAP: 15 / 80 / 500 core-minutes per level, 595 core-minutes total**
   (9.92 core-h, $0.509 derived). **An overrun stops that level; it does not get a
   new budget.** **The cap is enforced as `timeout = cap_core_min × 60 ÷ ranks`,
   which at 1 rank is `900 s`, `4800 s`, `30000 s`** — a wall-clock timeout is not
   a core-minute cap and must never be registered as one. A level killed by its cap
   is **`PENDING`**, a right-censored measurement, **never `GATE FAIL`**. At
   completion the actual is compared with this prediction and lands as a row in
   `docs/COST_CALIBRATION.md` (rule 12).

9. **Controls, and the planted zero.** The comparator **must plant a known
   perturbation into a copy of the fine level's `T` field on disk, read it back
   through the same reader that produces `ΔT(z)`, and REFUSE (exit 2) if it cannot
   see it** — rule 3, non-negotiable, and this family has already been caught with
   three unarmed readers (`T1b_L4_PLANTED_ZERO_CONTROL_PREREGISTRATION.md`).
   Additional registered controls, each reported whichever way it falls:
   **(C1)** ambient far-field `ΔT` at `r = 12D` must be `< 1 %` of centreline `ΔT`
   at the same `z`, or the domain is too narrow and the row is `NOT A RESULT`;
   **(C2)** integrated buoyancy flux `F(z)` must be conserved to `< 5 %` across
   the fit window, since MTT's derivation assumes it — a violation invalidates the
   reference, not the solver;
   **(C3)** `z0` spread across the three levels, reported;
   **(C4)** a jet discriminator — the fitted `n_w` must sit further from `−1` than
   from `−1/3`, proving the fit can tell a plume from a jet.

10. **What this does not claim, stated before it runs.** **This rung can reach
    `GATE REACHED` at best and can NEVER reach `HOLDS`.** MTT is an analytic
    reference, and under Sanaa's ruling of 2026-08-25 (*"a. Uphold"*) an exact or
    analytic reference scores **V**, never **P**; validation requires measured
    physical reality from a public primary with its pre-registration on disk.
    **No such primary is held for T8** — measured plume data (Papanicolaou & List
    1988 class) is **NOT ON DISK** and is not sought by this document. So the
    matrix consequence is precise: **cell C7 moves from `NEVER RUN` to a graded
    `V`+`G` cell with `P NONE`, and nothing in this rung is a claim about the
    world.** It also does **not** create, move or retire any gate, threshold, band,
    cap or label belonging to any other rung, and it touches no frozen file.

---

**Supervisor's read is what arms this.** Four things need ruling before it is
frozen: (i) the ±0.05 band — is a modelling-tolerance band acceptable on a V row,
or should the exponents be report-only and the gate moved to the jet/plume
discrimination alone; (ii) the `z/D ∈ [10, 30]` window against a 40 D domain —
30 D may be close enough to the outlet to matter; (iii) whether `kEpsilon` or
`kOmegaSST` is the registered closure for a free shear plume (this draft picks
`kEpsilon`, the conventional choice for free shear, against the family's usual
`kOmegaSST`); (iv) serial versus a parallel batch under the concurrency directive
— **a parallel run is a new registration, not an amendment to this one.**

**Nothing here has been sent, filed, submitted or registered anywhere outside this
box.**
