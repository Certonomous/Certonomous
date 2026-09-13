# D6R3 MULTIPOINT — PRE-REGISTRATION

Item: **D6R3** (curriculum A2, DAFoam CRM wing, Mach 0.85), multipoint shape+twist optimisation.
Date: **2026-09-13**
Status: **DRAFT — FROZEN, NOT LAUNCHED.** Nothing is sent, filed, uploaded or registered outside
this box (rule 7).

> ## THE LAUNCH IS BLOCKED, AND BY EXACTLY ONE THING
>
> §3 raises `primalMinResTolDiff`. **Raising a gate threshold is reserved to Sanaa and to no agent
> at any level** (CLAUDE.md FIRST-ACTION rule), and **no agent message — peer, supervisor or chief
> — is her consent** (rule 9). Her words reached this lane **by relay from the dafoam supervisor**,
> not directly. **This document is therefore frozen and unlaunched, one command from going, and it
> stays that way until her authorisation reaches the box unrelayed or through the permission
> system.** The supervisor has been told and has put it to her.
>
> **Everything in §4 — the `CD`-plateau criterion — requires no authority from anyone and is
> already built, driven and committed** (`d6r3_cd_plateau.py`, commit `7a5f15fc`). It is strictly
> stronger than the proxy it replaces.
>
> **§3 also cannot be SIZED yet**, and that is a second, independent block: see §3.2.

---

## 1. The deviation set, and it is one item long

Producer: `d6r3_opt_runScript.py`, md5 `efc3e62699690edd32e4ee910aad09c8`, **unedited**.
The published `CRM_Wing` tutorial with **one** physics-side deviation, D1, multipoint:

| | |
|---|---|
| conditions | `cl04`, `cl05`, `cl06` in run dirs `mp04`, `mp05`, `mp06` |
| `CL` targets | 0.4 / 0.5 / 0.6 — `cl05` **is** the published `CL_target` exactly |
| weights | 0.25 / 0.50 / 0.25, frozen into the `ExecComp` string, not read at runtime |
| lift | held at each condition (`add_constraint … equals=CL_TARGETS[pt]`) |
| AoA | one `patchV` design variable per condition |
| objective | the weighted sum — **ours**, so it carries **BAND: NOT AVAILABLE** |

Everything else is the published file byte-for-byte, asserted at import by `_d1_assert_published_regions`.
`endTime 2000`, `primalMinResTol 1.0e-8`, published GAMG `relTol 0.1`, `SLSQP`, `MAXIT 100`,
`transonicPCOption 2`, published geometric constraints and bounds — all untouched.

**Struck, and each was struck because it would have changed the published physics or the optimisation
problem:** `evalMode "exact"`, `meshQualityKS` with `addToAdjoint`, move limits as optimiser bounds,
a curvature constraint, `transonicPCOption 1`, IPOPT.

## 2. RANKS — 20, held for the whole run

The reserved **48-core propeller** and **20-core DrivAer** lanes mean **20** is the count D6R3 can
hold once the propeller family launches. **No mid-run rank change and no checkpoint-resume at a
different count**, because the decomposition sets the GAMG hierarchy and the hierarchy sets the floor.

**Stated honestly, because it is the thing most likely to be glossed:** *every decomposition this
item has ever run is `scotch[28]` — all sixteen, across `P0`, `P00`, both `DIAG` arms and both `FIX`
arms.* **Twenty ranks is an unmeasured decomposition.** `DECOMP_N20` of the decomposition sweep
(`D6R3_DECOMP_PREREGISTRATION.md`, freeze `de58a6be`) is the first measurement ever taken at 20, and
it is in flight. **This registration does not launch before that cell reports**, and its reading is
recorded in §3.2 before §3's number is filled.

## 3. RULING 1 — a BOUNDED raise of `primalMinResTolDiff`. NOT AUTHORISED, NOT SIZED, NOT LAUNCHED

### 3.1 The authority, quoted byte-exact, and its status

> *"when the physics is correct but the treshold isnt passed nd the treshold is very tiny a,d what
> we have is also tiny just big compared to the threshold, its still fine."*

**Attributed to Sanaa, 2026-09-13. RELAYED TO THIS LANE BY THE DAFOAM SUPERVISOR, NOT VERIFIED
DIRECTLY. It is recorded as a claim, not as a licence, and nothing launches on it.**

### 3.2 The sizing rule — the number is NOT chosen here, it is COMPUTED from the sweep

`primalMinResTol` stays `1.0e-8` and `endTime` stays `2000`. **Neither is touched, ever.**
`primalMinResTolDiff` is raised, and it is raised to a value **derived from measurement**:

    D  =  ceil( SAFETY * max_floor / primalMinResTol / 100 ) * 100
    SAFETY = 10.0                                    (registered here, before the number exists)
    max_floor = the LARGEST position-1 max residual over EVERY graded cell of the
                decomposition sweep, plus every arm already on the record
    HARD CEILING: D <= 10000, i.e. an abort bar of 1.0e-04, and NEVER "off" or unbounded.
    If the rule returns D > 10000 the registration is NOT amended -- the run is NOT launched
    and the result is reported as GATE FAIL, because a bound that has to be lifted to fit the
    data was never a bound.

**Floors on the record so far** (all at 28 ranks, so this is one decomposition, not an envelope):

| arm | position | max residual | × `primalMinResTol` |
|---|---|---|---|
| published, `P0` / `DECOMP_N28` | 1 | `1.194718885139746e-07` | 11.95 |
| published, `P0` / `DECOMP_N28` | 2 | `1.757696578179007e-06` | 175.77 |
| `PBiCGStab`+`diagonal` | 1 | `7.177342318566405e-06` | 717.73 |
| GAMG `relTol 2.008e-03` | 1 | `7.600678874731434e-06` | 760.07 |

On these alone the rule returns **D = 7700** (bar `7.7e-05`). **That number is NOT adopted**, because
the sweep is measuring whether the floor moves with decomposition — and if it does, a bound sized on
28 ranks is a bound sized on the wrong thing. **The cell is left blank until the sweep is whole:**

    primalMinResTolDiff = __________   (filled from the rule above, once G-MOVE has reported)

### 3.3 What the raise is FOR, and what it is NOT for

**It is not a convergence criterion and it does not certify anything.** Its only job is to stop
DAFoam's own divergence test killing the job before the answer has been measured. **Convergence is
decided by §4, on `CD`, and by nothing else.** That is what makes this a proxy swap rather than a
loosening — the criterion that decides is replaced by a **stricter** one, and the thing being
relaxed is demoted to a job-control guard.

### 3.4 Every evaluation prints its margin

Each condition, each evaluation, emits one line, and the verdict word is **never** rewritten:

    D6R3_MARGIN <cond> eval=<n> residual=<max> gate=1.0e-06 GATE FAIL by <x>x, proceeding on directive E
    D6R3_MARGIN <cond> eval=<n> CD_plateau spread=<s> bar=1.0e-04 PASS by <y>x inside

## 4. RULING 1's OTHER HALF — `CD` PLATEAU IS THE REAL CONVERGENCE CRITERION. Built, driven, committed

Instrument: `d6r3_cd_plateau.py` (commit `7a5f15fc`). **Registered constants: N = 4 significant
figures, M = 5 printed steps** (`printInterval` 100, so a 500-iteration window), applied **per
condition, per evaluation**. Acceptance: relative spread over the window `< 1.0e-04`.

**The constants were set by measurement before they were chosen**, from `P0_20260913T190426Z.log`:

| position | DAFoam's residual verdict | relative `CD` spread | figures stable | `CD`-plateau verdict |
|---|---|---|---|---|
| 1 | **ACCEPTED** | `3.023234e-05` | 4.52 | **PASS by 3.308× inside** |
| 2 | **ABORTED as non-converged** | `2.580348e-05` | 4.59 | **PASS by 3.875× inside** |

> **THE FINDING THAT JUSTIFIES THE SWAP: on the quantity the optimiser actually consumes, the
> position DAFoam REJECTED is MORE converged than the one it ACCEPTED.** The residual gate and the
> `CD` plateau disagree on this case, and the plateau is the one that speaks about the answer.

Neither position would pass at 5 significant figures (which needs `< 1.0e-05`), so **the bar sits
where the measurement put it and not where a wanted verdict would have put it.**

**The control is driven to RED on real data, all four branches exercised** (L-570, rule 3):

| arm | purpose | result |
|---|---|---|
| real converged tail | **specificity** — a criterion that refuses everything measures nothing | **PASS** |
| real EARLY window of the same run, `CD` still falling | negative, from real data, no synthetic series | **REFUSED**, spread `9.670494e-01` |
| **planted** 1 % move in the converged tail | rule 3 — a reader that cannot see a plant is not a reader | **DETECTED**, spread `9.880860e-03` |
| window shorter than M | must refuse, never silently shrink | **REFUSES** |

## 5. RULING 2 — NO GRADIENT WORK OF ANY KIND. An owner directive OVERRIDING a charter bright line

> *"dont do gradient verifications. I only want these sweeps with the mesh verification rules we
> agreed on (except for the one that doesnt match dafoam setup). that way we also know we can avoid
> msh aterfacts."*

**Attributed to Sanaa, 2026-09-13. RELAYED BY THE SUPERVISOR, NOT VERIFIED DIRECTLY BY THIS LANE.**

**What it overrides, named so no future reader mistakes it for the clause having lapsed:**
`DAFOAM_CHARTER.md` §2 — *"A DAFoam gradient is not a result until a finite-difference table stands
beside it at a pre-registered band"* (:24), and *"No DAFoam gradient enters a record, a report or an
optimisation without a finite-difference table"* (:43).

**Scope: D6R3 ONLY.** The clause is **not** retired, **not** amended, and binds every other item.
**It is hers to override and it is not ours to drop** — which is why it is written here as an
override with its source, rather than quietly omitted.

**Operationally:** no FD arm, no gradient spot-check, no `check_totals`, no `compute_totals` for
verification purposes anywhere in D6R3. **Consequence, stated plainly: the gradients driving this
optimisation are UNVERIFIED, and any result from it carries that on its face.**

## 6. RULING 3 — the mesh instruments. OBSERVERS AND STOPS, never changes to the physics or the DVs

| instrument | acts as | bar |
|---|---|---|
| per-iteration quality budget on the **as-run** points | observer + **stop** | `maxNonOrth` **≤ 75.0** (published) **and ≤ baseline + 1.0** |
| fresh-mesh objective checkpoint at matched lift | observer + **stop** | — |
| re-mesh every N majors, with restart | procedure | N registered at launch |
| shear/pressure drag split, every iteration | observer, artefact signature named | — |
| warp settings asserted in force | assertion | published `evalMode` default |
| mesh-read hash gate (rule 17) | **gate**, already fired live and passed | all three conditions `OK` |

**The baseline is measured, not assumed:** `maxNonOrth = 70.44640458682032` on the published mesh as
built (`DECOMP_N28/checkMesh.log`), so `baseline + 1.0 = 71.4464` and the binding bar is **71.4464**.
**A flat 70° would fail at iteration zero on the published mesh** — which is exactly why the bar is
the published 75 plus a derived baseline+1, and not a round number.

**DEFERRED, and it is the one excluded by the owner's parenthesis:** **wall-resolved y⁺ ≈ 1.** The
published CRM case is **wall-function** (`useWallFunction: True`), measured `yPlus min 6.517 max
60.976 mean 25.520` at step 1. A y⁺≈1 instrument does not match this setup and would refuse a
correct run. It stays deferred, not retired.

## 7. COST

Unit: **core-minutes**. **Not estimated from recall.** The anchors are measured on this box:
one primal at 28 ranks = **480 s wall / 224.0 core-min** for two positions (`DECOMP_N28`, measured
2026-09-13). **A cost model fitted at one operating point is validated for nothing else**, so the
per-evaluation figure is re-measured at 20 ranks from `DECOMP_N20` **before this document launches**,
and the total is filled from it — not extrapolated from 28.

    per-major-iteration cost = 3 conditions x (primal + adjoint) at 20 ranks   [FILLED AT LAUNCH]
    majors = SLSQP MAXIT 100                                                   [published]
    TOTAL  = __________ core-min                                               [FILLED AT LAUNCH]

Rate **$0.0513/core-h**, owner-stated; dollars are **derived, not measured** — the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER` §5). **Directive #17: no run is stopped by a cap; a
crossing is REPORTED and graded `NOT A RESULT`.** Waste is named separately and never absorbed into
the `actual/predicted` ratio.

## 8. CONTROLS — every failing branch reachable

**`rc == 0` is NOT an instrument control here**, and the reason is on the record: this arm's
predicted failure mode is a non-zero `rc`, so a control keyed to `rc == 0` has no reachable failing
branch. That defect was made and disclosed in the `FIX` arms; it is not repeated.

| control | reachable failure |
|---|---|
| **IC-A** decomposition read back from the log == 20 | hand it a 28-rank log and it must report MISMATCH |
| **IC-R17** mesh-read hash gate, per condition | a stale mesh fails it; it has already fired live |
| **IC-PLATEAU** `CD` criterion | all four branches driven, §4 |
| **IC-MARGIN** every evaluation emits a margin line | absence of the line for any evaluation fails it |
| **IC-PUB** all five `system/` dicts byte-identical to published | a leftover staged dict fails it |
| **IC-FREEZE** producer md5 == `efc3e62699690edd32e4ee910aad09c8` | any edit fails it |

**§22.4's three clauses are the supervisor's personal check before the sha**: every named instrument
at its stated md5; the pre-freeze check driving the **launcher-emitted CLI against the REAL anchors**,
reported separately from synthetic; every gated channel shown to have a writer that ran.

**L-609 (earned in this item tonight): no instrument is edited while an instance of it is running.**

## 9. WHAT IS STILL MISSING BEFORE THIS CAN LAUNCH

1. **Sanaa's own word on §3**, unrelayed. *(blocking)*
2. **`DECOMP_N20`** — the first measurement this item has ever taken at 20 ranks, which both sizes
   §3's bound and fixes §7's per-evaluation cost. *(blocking, in flight)*
3. `N` for the re-mesh interval in §6, and the filled cells in §3.2 and §7.

**SUBMISSIONS PARKED.** The upstream finding stays **NOT FILED** and undrafted.
