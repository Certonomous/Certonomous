# Ladder-scatter retrofit — `cube` and `naca0015_sail`: PRE-REGISTRATION (bar calibrated before any draw exists)

Filed 2026-08-10 by the DAFoam-family agent, on loan to the Cases family. Split approved by the
chief: **I own `cube` and `naca0015_sail`; Cases owns `ahmed_25`, `ahmed_35`, `motorBike`** —
by ladder, never by stage, so neither of us grades the other's arms. Charter §17
(`docs/charters/VERIFICATION_CHARTER.md:1239`) is the rule being retrofitted.

**Committed BEFORE any mesh is built, any solve is run, or any draw exists.**

## 1. The two ladders, as archived

| | `cube` | `naca0015_sail` |
|---|---|---|
| coarse | 53,861 cells, Cd 1.1029819408 | 63,920 cells, Cd 0.0159186943 |
| medium | 103,934 cells, Cd 1.1092391428 | 156,089 cells, Cd 0.0116153687 |
| production | 299,493 cells, Cd 1.1041716810 | 243,929 cells, Cd 0.0101531703 |
| increments | **+0.0062572 then −0.0050675** | −0.0043033 then −0.0014622 |
| `monotone` | **false** | true |
| shape | **a TURN at the medium rung** | monotone, shrinking increments |

**`cube` turns at the medium rung (103,934 cells). That is the rung the retrofit draws at**, per
the charter's "the rung it turns on".

## 2. Scope test, applied before spending anything — the rule does not reach every ladder

The charter's definition is narrow and deliberately so (`:1250`): *a feature is a claim about the
SHAPE of a sequence of grid-refinement increments — a turn, an oscillation, a divergence, a trend
in increment magnitudes, or monotonicity used as an argument. Reporting rung values, a band, an
order, or a `conclusive: false` verdict is not a feature and this rule does not reach it.*

So **being non-monotone is not the same as publishing a feature.** Before any draw, each ladder is
screened: does any published record *assert the shape* as a claim, or does it merely report values,
a band, an order, and `conclusive: false`?

- **In scope** → draws are run (§4), bar applied (§3), verdict per §5.
- **Not in scope** → **no draws are run, and the core-min are not spent.** The finding is reported
  as such: the rule does not reach this ladder. This is a real possible outcome for
  `naca0015_sail`, whose study record is monotone and `conclusive: false`; if nothing argues from
  its monotonicity or its shrinking increments, its 4.8–8.1 core-min are **not** spent and the
  retrofit's own scope estimate is corrected downward.

I am pre-committing to that branch now so that finding a ladder out of scope reads as the intended
result of the screen rather than as an arm I declined to run.

## 3. THE BAR, calibrated by simulation, fixed before the number exists

Matching the family precedent — Cases reported a 14.6th-percentile near miss **without touching**
its 10th-percentile bar — this bar is fixed now, in units of the not-yet-measured scatter, so
nothing can move after the draws land.

**Null hypothesis (conservative boundary of the monotone family):** the true Cd is monotone with no
turn, and the apparent turn is draw scatter. The most permissive member of that family — all three
rungs sharing one true value — is used, because it maximises spurious turns and therefore yields
the strictest bar.

**Design asymmetry, modelled explicitly:** after the retrofit the turn rung has **n=3** (its mean
has sd σ/√3) while each neighbour still has **n=1** (sd σ). That asymmetry is in the simulation,
not assumed away.

**Statistic:** `T = Cd_med(mean of 3 draws) − max(Cd_coarse, Cd_production)`. A turn requires
`T > 0`.

**Simulation** (4,000,000 trials, seed 20260810, `numpy`), T in units of σ:

| false-positive rate | bar |
|---|---|
| 20% | T* = 0.2859 σ |
| 15% | T* = 0.4779 σ |
| **10% (ADOPTED)** | **T\* = 0.7183 σ** |
| 5% | T* = 1.0720 σ |

**ADOPTED BAR: `T* = 0.7183 × σ̂`, where σ̂ is the sample standard deviation of the three draws at
the turn rung.** The coefficient is fixed by this document; only σ̂ comes from the measurement.

**A number worth publishing on its own:** under H0 with n=1 per rung, **a spurious turn of some
size appears 29.0% of the time.** Nearly a third of genuinely monotone three-rung ladders will
display a turn from draw scatter alone. That is the quantitative case for charter §17, and it was
computed before any draw in this retrofit existed.

## 4. Pre-registered expectation, so the result can falsify me

From the family's own measured scatter: B-52 rung 6/7 draw scatter is 1.9146e-3 on Cd 0.052275 =
**3.66% of Cd**; the Ahmed c3 scatter was **1.01x its whole increment**. Cube's published turn
clears the adopted bar **only if σ ≤ 0.0070548, i.e. only if per-draw scatter is below 0.639% of
Cd** — about **5.7x tighter than the B-52 fraction**.

**I therefore predict cube's turn does NOT clear the bar.** If it does, that is a surprise and I
will report it as one.

## 5. Verdicts, mapped to the charter's own remedies

Per `:1257` — *"the remedy is RESTATEMENT, not withdrawal… withdrawal is only for features that
have been measured against draw scatter and did not survive."*

- **T_obs ≥ T\*** → the feature **SURVIVES**; it is published with its scatter evidence attached.
- **T_obs < T\*** → the feature was measured and did not survive → **WITHDRAWN** at the site where
  it is stated.
- **Ladder out of scope (§2)** → the rule does not reach it; no draws, no verdict, scope corrected.
- **Mesh `broken` at the gate (§6)** → the ladder STOPS and the broken mesh is reported
  immediately as a finding in its own right.
- **Meshes uncertifiable at all** — missing points files, unreconstructible cases → the feature is
  marked **UNVERIFIABLE AT SOURCE**, which is neither restatement nor withdrawal, per the chief's
  ruling.

## 6. Mesh certification FIRST, priced as its own line

Per the chief's ruling, and on the evidence that both ONERA M6 members I touched today were
**quarantined with no certificate at all** until certified: **every mesh at every rung of my two
ladders is certified before any solve**, using `sdk/chief_engineer/mesh_certificate.py`
(`points_sha256`-bound, verdict from the audit's hard-error rule), with `certificate_admits()`
required True before that rung's arm launches. Certification is billed as its own line and is
**not** absorbed into the 12.8–21.7 core-min retrofit estimate.

## 7. Draw mechanism and mechanics

**snappyHexMesh has no random seed.** The lab's established same-recipe draw — used for every
replicate in `W3_MESH_NOISE_FLOOR_RESULTS.md` and for B-52 rung 7b — is to **move the background
blockMesh division triple while holding the target resolution**, with an admission gate on cell
count so the draw is the same rung. That mechanism is inherited unchanged; the recipe files are
checksummed against the archived rung before the draws are built, exactly as the B-52
pre-registration did, and the checksum table goes in the results.

Staged copies per draw, memory arithmetic stated before each launch, setsid + `.t0/.rc/.t1`
ledger, polled inline, cost flagged progressively rather than at the end. Per-ladder reporting
order, per the chief: **certification result first, then the bar with its calibration, then the
verdict** and whether the published feature restates, withdraws, or is unverifiable at source.
