# VMFL059 — `NOT A RESULT`, and the cause is a MIS-SPECIFIED GATE QUANTITY, not a failed solve

**Author:** `ansys-verification-supervisor`, personally, 2026-08-25.
**SUPERVISION_CHARTER §3 check 3.** The run and the grading were a lane's; **the diagnosis
below is mine and was checked against the case files, not inferred from the lane's summary.**

**NOT FILED ANYWHERE** (CLAUDE.md rules 7, 8).

---

## The run was clean. Every control passed.

Fired 2026-08-25T19:19:56Z under its frozen, committed pre-registration. All three levels:
**`rc = 0`**, `End` present, last `Time` == `endTime 0.05`, **age guard passed**,
planted-zero control passed on both patches at all three levels. **0.417 core-min of a
frozen 15 core-min cap — 2.78 %.**

**There is nothing wrong with this solve.** The verdict is not about the solver.

## THE VERDICT: `NOT A RESULT`, on rule 5, and it stands

| quantity | f_coarse | f_med | f_fine | state | p | GCI_fine |
|---|---|---|---|---|---|---|
| **rightWall (cooled)** | 378.0 | 378.0 | 378.0 | **`EXACT`** | undefined | undefined |
| leftWall (adiabatic) | 412.7916667 | 412.8958333 | 412.9479167 | `CONVERGING` | 1.00 | 0.01576 % |

CLAUDE.md rule 5 step 2: a triple that is `EXACT` → **`NOT A RESULT`**, whatever the value.
The cooled wall lands on **378.0000 K against a reference of 378.0 K — a deviation of
exactly zero** — and that is precisely why the row cannot be a credential. **The gate can
only turn a result INTO `NOT A RESULT`, never the reverse**, and I am not reaching past it.
The adiabatic wall's 412.9479 K against 413.0 K (0.0126 %, inside the frozen 1 % band) does
not rescue the row: the pre-registration requires **both** walls.

## A hypothesis I formed and KILLED before writing it down

Three identical values across three refinements is the signature of **grading your own
boundary condition** — a gate quantity that is an input rather than an output. That would
have been a serious self-blind-gate finding, of exactly the family this team hunts.

**It is false.** I read the field. `rightWall` is a **`codedMixed` Robin condition**, not a
`fixedValue`: it sets `refValue = 303 K`, `refGrad = 0` and
`valueFraction = h/(h + DT·deltaCoeffs)` with h = 1000 W/m²K, and it looks `DT` up from the
patch so it stays correct if the conductivity is edited. **The wall temperature is genuinely
solved for, not imposed.**

## What is actually happening — and it is a verification-methodology finding

**The cooled-wall temperature is fixed by a GLOBAL CONSERVATION LAW, not by discretisation.**
At steady state every watt generated in the block must leave through the one non-adiabatic
face, so `h·A·(T_s − T∞) = Q_total`, giving `T_s = T∞ + Q_total/(h·A)` — an integral balance
carrying **no mesh-dependent term**. A conservative finite-volume scheme satisfies that
balance **exactly on every mesh, to round-off**. So `T_s` is identical at 75, 1,120 and 4,480
cells not by accident but **necessarily**.

**Roache gating a quantity that a conservative scheme gets exactly right on every grid is a
category error.** The triple is `EXACT` by construction, so rule 5 returns `NOT A RESULT`
**for every possible run of this case as registered** — no mesh, no solver setting and no
amount of compute can change it. The gate could never have been passed.

**The second quantity is only marginally better.** The adiabatic wall gives
`R = 0.0520834/0.1041666 = 0.5000` **exactly**, hence `p = ln(2)/ln(2) = 1.00` exactly.
Orders and ratios do not come out at round numbers to four figures from a genuine asymptotic
fit; they come out that way when the underlying field is **piecewise linear** and the residual
error is a boundary-face interpolation artefact that halves exactly under uniform refinement.
So the second limb is a geometric artefact too — **and its p = 1.00 sits BELOW the formal
spatial order of 2**, which is its own warning.

**Conclusion: as registered, VMFL059 cannot exercise grid convergence in either gate
quantity.** One is conservation-determined, the other is exactly linear.

## What follows — and what does NOT

**The `NOT A RESULT` is recorded as it is and is not softened.** It goes in the register with
that reason. It is not a credential; only `PASS` rows are.

**This is NOT a case to re-run.** Re-running changes nothing — the outcome is structural.
Under Sanaa's directive of 2026-08-25 lifting cost as a reason to stop, more compute is now
freely available to this team, and **this is precisely the case where spending it would be
waste**: the constraint is not budget, it is that the registered quantity carries no
discretisation signal. *Cost being no longer a reason to refuse is not a reason to run
something that cannot answer.*

**The legitimate next step is a NEW frozen registration**, not an amendment — post-compute
gates are closed (rule 2) and a gate, threshold, cap or label cannot be moved by addendum.
The successor should gate on a quantity that is genuinely discretisation-sensitive: an
**interior temperature at a fixed physical point**, or the **flux through the material-1 /
material-2 interface**, where the composite conductivity jump (75 vs 150 W/m·K) actually
makes the answer depend on how well the mesh resolves it. **That interface is the physics the
manual is testing, and neither registered quantity looks at it.**

## The lesson for this team's freezes, effective immediately

**Before freezing a gate, ask whether the chosen quantity CAN vary with the mesh.** A
quantity pinned by a global conservation balance, or one lying in a region where the exact
solution is linear, will return `EXACT` or a spurious round-numbered order — and the case
burns a registration, a run and a grading to discover something derivable at the freeze in
one line of reasoning. **The pre-flight smoke test proves a case RUNS; it does not prove the
gate quantity can MOVE.** That is a distinct check and this team did not have it until now.
