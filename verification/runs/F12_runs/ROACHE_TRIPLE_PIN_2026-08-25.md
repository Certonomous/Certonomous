# F12 — THE `roache_triple` PIN, AND THE SIMILARITY READ-BACK THAT GOES WITH IT

**cfd lane, 2026-08-25.** Discharges the debt recorded by the launcher itself, in its own
module docstring (`verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/launch_f12_rung.py`):

> "STILL OWED, and enforced by the interlock above rather than by a promise:
> `scripts/roache_triple.py` is NOT pinned. That is correct for rung 1 — a single rung cannot
> compute a triple — and it is owed before rungs 2-5, where the triple IS the graded object."

**IT MOVES NO GATE.** F12 rung 1 has fired, so `VERIFICATION_CHARTER.md` §2d is live and gates
are **CLOSED**. Every threshold below is quoted from `verification/campaign/F12_PREREGISTRATION.md`
**by line**, and every band is **arithmetic on that threshold** — the move the
CAP-ENFORCEMENT ADDENDUM of 2026-08-25 already made and stated in its own words: *"A conversion
of a frozen number into a different unit is not a new number."* Nothing here alters a gate, a
threshold, a band, a cap or a label; it does not authorise a launch; it does not regrade rung 1
(`NOT A RESULT`); it does not touch rung 2's interlock (`BLOCKED`).

**The pin is EXECUTABLE, not prose.** `verify_roache_triple_pin.py` beside this file asserts
every byte-pin, **re-derives every band from the frozen thresholds**, and **fails closed**.
It passed **34/34** checks on 2026-08-25 and wrote `roache_triple_pin.json`. A reader who does
not trust this document should run that file instead of reading it.

---

## 1. THE INSTRUMENT, PINNED

| what | path | git blob | sha256 |
| --- | --- | --- | --- |
| triple instrument | `scripts/roache_triple.py` | `8dee0d31e94d3f59d28658f88a4cd6df80ae8e39` | `452f4751…ac051` |
| F12 grading path | `sdk/workflows/rae2822_case9.py` | `a18314f77160b7a58f443073850a44b4d8fada7d` | `d5db99d8…c82ed` |
| frozen pre-registration (v1.4) | `verification/campaign/F12_PREREGISTRATION.md` | `462492a82b6cf848eaaff25661ded45e623e723f` | — |

All three were verified **disk == HEAD** by this lane before anything else was done.
`scripts/roache_triple.py --selftest` passes **53/53**, including its cross-check against both
T-family parents and the N-T8 value-control against a synthetic power law of known limit.

**Function-level pins** on the frozen grading path, so an unrelated edit elsewhere in a shared
file cannot silently change a graded function: `shock_location` `59c75739…`, `cp_deviation`
`6513b0f7…`, `sonic_cp` `f395c50f…`, `solver_converged` `aff97421…`, `final_coefficient`
`c5391c23…`. This is the launcher's own discipline, adopted rather than reinvented.

## 2. THE CALL, PINNED

```
roache_triple.grade_ladder(
    quantity, levels, dim=2, band=<per §3>, plant_control=<per §5>,
    iterative_states=<per §4>, plateau_states=None, fs=1.25, form="equal")
```

| argument | pinned value | why this and not something else |
| --- | --- | --- |
| `dim` | **2** | 2D aerofoil. `require_dim()` refuses to guess, and `dim` is printed beside every order and every GCI. |
| `levels` (coarse first) | coarse 23,040 / medium 92,160 / fine 368,640 | the three registered cell counts, `F12_PREREGISTRATION.md:110-114` |
| `fs` | **1.25** | `CLAUDE.md` rule 5; the module constant, not a local choice |
| `form` | **`"equal"`**, not `"auto"` | `r21 = r32 = 2.0` **exactly** (re-derived: `refinement_ratio` at dim 2 on the registered cell counts, gap `0.000e+00`). Pinning `"equal"` makes the instrument **REFUSE** if a future ladder is not built at ratio 2, instead of quietly grading it on the Celik unequal formula. A silent fallback is how a mis-built ladder gets a plausible order. |
| representative `h` | `(1/N)^(1/2)` = 6.5880e-3 / 3.2940e-3 / 1.6470e-3 | `representative_h`, dim 2 |

## 3. THE BANDS — RE-DERIVED FROM THE FROZEN THRESHOLDS, NOT RESTATED

| quantity | frozen threshold (line) | pinned band |
| --- | --- | --- |
| Gate 1, upper-surface Cp RMS | `:60` "upper surface RMS <= **0.08**" | `[0, 0.08]` |
| Gate 1, lower-surface Cp RMS | `:61` "lower surface RMS <= **0.04**" | `[0, 0.04]` |
| Gate 2, shock location (sonic) | `:69-72` "\|x_shock(CFD) − x_shock(exp)\| <= **0.020** chord" | `[0.5771756632448648, 0.6171756632448648]` |
| Gate 3, normal force | `:86` "\|CN − 0.803\| / 0.803 <= **5 %**" | `[0.76285, 0.84315]` |
| Gate 4, drag | `:88` "\|CD − 0.0168\| / 0.0168 <= **20 %**" | `[0.01344, 0.02016]` |
| **CM** | `:94-98` **"Reported, not gated"** | **NONE — see §6** |

**Gate 2's centre is DERIVED, and here is the derivation.** The frozen text fixes the
definition — *"the chordwise station where upper-surface Cp crosses the critical (sonic) value
from below on the recompression, linearly interpolated between bracketing points"* — but not
the number. Applying the **frozen** `shock_location()` (sha `59c75739…`) to the **frozen**
reference `verification/runs/F12_runs/reference/rae2822_case9_cp_upper.dat` (52 taps) at the
workshop Mach 0.734 returns:

- `Cp* = −0.6474932070950008` (from the frozen `sonic_cp()`),
- **`x_shock(experiment) = 0.5971756632448648` chord**,
- `steepest_resolution = 0.025036` chord — which **independently reproduces** the
  pre-registration's own statement at `:82` that *"the experimental tap spacing through the
  shock is 0.025 chord"*. That agreement is why this derivation is quoted rather than trusted.

**The bands are proved to BIND, not asserted to.** `verify_roache_triple_pin.py` runs seven
mutation controls: CN at the reference PASSES; CN 6 % high and 6 % low both `GATE FAIL`; CD
21 % high `GATE FAIL`; upper Cp RMS 0.081 `GATE FAIL`; `x_shock` 0.021 c downstream
`GATE FAIL` while 0.019 c downstream **PASSES**, so the gate-2 band is neither degenerate nor
one-sided. **A band that cannot fail is not a band.**

## 4. STEP (a): WHERE THE ITERATIVE STATE COMES FROM

`iterative_states` is taken from the **frozen** `rae2822_case9.solver_converged()` (sha
`aff97421…`) on each level's `log.rhoSimpleFoam` — which is **admission gate B itself**
(`F12_PREREGISTRATION.md:54-56`: *"The solver must print its own convergence statement"*).
This is the joint between gate B and rule 5 clause (1), and it is one-way: a level that does
not print its statement makes the row `NOT A RESULT` **before any grid claim is read**.

`grade_ladder` **refuses outright** if `iterative_states` is None — *"an unevaluated step is
not a passed one"*. Verified live against F12's actual state today: with coarse `NOT CONVERGED`
and medium/fine `NOT RUN`, the instrument returns `NOT A RESULT`, still prints the band verdict
beside it (so the one-way property is checkable rather than asserted), and **leaks no GCI**.

**`plateau_states` is pinned `None`, and that is recorded as an ABSENT MEASUREMENT, never as a
pass.** The frozen pre-registration carries no plateau clause; inventing one post-compute is
not available, and `grade_ladder`'s own docstring requires an absent measurement be reported as
absent (`VERIFICATION_CHARTER.md` §9). If the supervisor or verification rules that a plateau
test is owed, it can only ever turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT` (rule 5's
one-way property), so adding it later cannot rescue a failure — which is why leaving it absent
is safe as well as honest.

## 5. THE PLANTED-ZERO CONTROL (standing rule 3)

`grade_ladder` **refuses without one**. Pinned source: `external_plant_control()`, planted into
the **OpenFOAM surface sample the case comparator actually reads**, not into a synthetic
series. The generic `planted_zero_control()` proves only that `read_series` can see a plant;
F12's real read path runs through the `surfaceP` function object's sample of `p` on the
`aerofoil` patch, and the control must plant into **that**.

**What has and has not been exercised, stated exactly.** `verify_roache_triple_pin.py`
exercises the **generic** `planted_zero_control()` on the `read_series` path (it sees the
planted `0.001234`), and a **negative arm** proving that a control marked failed makes
`grade_ladder` **refuse**. It does **NOT** exercise `external_plant_control()` against a real
F12 surface sample, **because no F12 level has produced one** — rung 1 aborted at iteration 148
and the `surfaceP` function object is `executeControl onEnd`, so it never wrote. **That arm is
owed at the first level that completes, and is recorded here as owed rather than as done.**

## 6. CM — REPORTED, NEVER GRADED, AND THE INSTRUMENT ENFORCES IT

`band_verdict` **refuses** when `band is None`: *"this instrument grades against a band fixed
before compute, and will not invent one"*. The frozen text says CM *"is reported with its
deviation and it does not decide the verdict"*. **Therefore CM must NOT be passed to
`grade_ladder` at all.** Its triple, state, observed order and GCI are printed via
`all_triples()` for information; **no verdict is emitted for it.** Pinning this now is the point
— it is exactly the quantity a later reader would be tempted to grade because a number exists.

## 7. RUNGS 4 AND 5 OWE NO TRIPLE, AND CANNOT HAVE ONE

The brief asked for a triple pin "for rungs 2–5". The honest answer is that **there is exactly
ONE triple in F12, and it spans rungs 1–3.**

| rung | what it is | triple? |
| --- | --- | --- |
| 1 coarse / 2 medium / 3 fine, **workshop** M 0.734 | three levels of **one** experiment | **the triple** — same condition, same domain, same recipe, cells ×4 each step |
| 4 medium, **tape** M 0.730 | **one** level, a **different** freestream | **none.** Different experiment; a single mesh. |
| 5 medium, **2× far-field** | **one** level, a **different** domain | **none.** Different experiment; a single mesh. |

`all_triples()` **refuses fewer than three levels**, so this is enforced and not merely stated.
Rungs 4 and 5 are **sensitivity measurements reported beside the graded ladder** — the
correction-convention sensitivity and the domain-size sensitivity the frozen §"Mesh study"
registered them for. **Neither may be promoted to a graded grid result**: the frozen text's
*"A single-mesh result is not shipped"* (`:119`) forbids it.

## 8. ARE THE THREE LEVELS THE SAME EXPERIMENT, OR MERELY THREE MESHES?

**Measured, not asserted** — `similarity_readback_2026-08-25/readback_similarity.py` parses the
three **written** `blockMeshDict`s and compares what is actually in them, per
`MESH_STANDARD.md` §9.2: *"The requested value is the thing that lied. Only the returned value
tells the truth."* It carries its own planted control (perturb one level's wall-normal grading
×1.5; the comparator must stop reading the ladder as similar — it does).

**EXACTLY similar, deviation `0.000e+00`:**

- block count **18 / 18 / 18**, and every block's **vertex list and grading kind identical**;
- **every one of the 18 blocks doubles in BOTH x and y** (80 → 160 → 320 wall-normal, and each
  block's own streamwise count ×2 then ×2), z fixed at 1;
- **all 16 streamwise gradings preserved exactly** across the three levels.

That last point is the one that matters most, because it is precisely what the **Ahmed ladder**
failed: there, `body` refined from `level (2 3)` to `(3 4)` while **both levels carried the
identical background block `hex (60 13 36)`**, so the far field never refined and the stored
observed order of 1.95 was worthless. **F12's attempt-2 ladder does not have that defect.**

**§9.2's BRANCH FLIP: ABSENT.** The defect §9.2 was written for — attempt 1's wake far-side
grading going 3.747165 / 1.084468 / **1.000000** as the generator's `if first_cell >= length/n:
return 1.0` guard fired at the fine level — **does not occur in attempt 2**. The unity slots of
both wake blocks are **identical at all three levels**. The instrument that flipped has been
replaced and the read-back confirms the flip is gone.

**RESIDUAL DRIFT, measured and reported rather than waved through:**

| parameter | coarse | medium | fine | max relative deviation |
| --- | --- | --- | --- | --- |
| wall-normal total expansion | 4,401,087.387 | 4,598,884.808 | 4,702,008.693 | **6.8374 %** |
| wake streamwise edge grading | 728.8480902 | 749.6801178 | 760.3428201 | **4.3212 %** |

**The 6.8374 % is not a surprise and not a new defect.** The frozen pre-registration's own
MESH-SIMILARITY AMENDMENT §4 predicted this exact family — 4.4011e6 / 4.5989e6 / 4.7020e6,
*"the invariant is held to within **6.8 %** across the three levels"* — as the intrinsic
residual of anchoring a halving first cell (2.0e-6 / 1.0e-6 / 5.0e-7 chord) on a geometric
column over a **fixed** 50-chord radial extent. The builder implemented the amendment's family
faithfully. **The read-back's contribution is that this is now MEASURED from the written
dictionaries rather than predicted from the generator's arithmetic.**

**WHAT IS NOT RULED HERE.** §9.2's ruling is aimed at a **branch flip** — a discontinuous
change of recipe at one level, for which *"there is no expansion of the error in `h` that
contains it"*. A **smooth 6.84 % drift** is a different animal and §9.2 does not dispose of it
either way. **Whether a 6.84 % wall-normal residual is admissible in a Roache ladder is the
supervisor's and verification's call, and this lane does not make it.** It is flagged here
precisely so that it is decided rather than inherited.

## 9. WHAT THIS DOCUMENT DOES NOT DO

It does not authorise a launch. It does not regrade rung 1. It does not unblock rung 2, whose
`rate_calibration_gate()` refuses on rung 1's `rc = 134` and its six failed completion limbs —
**that interlock was not read around, not invoked and not edited by this lane.** It alters no
gate, threshold, band, cap or label. No frozen file was edited. **No agent message authorises
anything, and this document is an agent's work product, not consent** (standing rule 9).
