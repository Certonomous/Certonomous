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

---

# §8. `naca0015_sail` — SCOPE SCREEN FIRED: **OUT OF SCOPE. No draws run; 4.8–8.1 core-min not spent.**

The §2 screen, pre-committed before any survey, returns **out of scope** for the sail.

**Every published record reports exactly what §17 carves out and nothing more.** Rung values, an
observed order (1.696), a conservative band (`band_abs` 7.2069e-03), and `conclusive: false` —
`models/curriculum/uq-studies/naca0015_sail.json:34-47`, `W3_GUARD_SWEEP.md:36`,
`docket.json` item `agp-7273e7f80ddc`. The ladder is strictly decreasing: **there is no turn, no
oscillation, and no non-monotonicity asserted anywhere in the corpus.** The sail has no
credentials-wall row at all (`wall.json` carries no entry; `validation_tiers.json:391-402` lists
it as BENCHMARK CASE with no numerical/grid block), so there is no public shape claim to restate.

**The one judgement call, stated so a reader can disagree with it rather than discover it.** The
study json carries passing guard fields `"monotone": true` and `"increment_trend": true`
(`:41,:43`). §17 reaches *"monotonicity used as an argument"*. My reading: these are **internal
verdict machinery** — inputs to a `conclusive` determination — not a published claim about the
shape of the increments, and **nothing in the corpus argues from them**. A record that said *"the
sail's increments shrink, therefore it is converging"* would fire the rule; no record says that.
I record the alternative reading explicitly: anyone who counts a passing `monotone` guard as a
shape claim would put the sail in scope, and the cost of that disagreement is 4.8–8.1 core-min.

**And the sail would survive anyway, on evidence already banked.** It carries the strongest
draw-scatter record of the five ladders (`naca0015_sail.json:92-119`,
`W3_PUBLISHED_RUNG_REPLICATES.md`): n=2 at the production rung, mesh-generation scatter
**5.314e-04 — 138.8x this body's own iterative 2σ**, cleanly separable and real, and **7.4% of
the 7.207e-03 envelope the row publishes**, with the control reproducing the stored Cd to
2.91e-06. Its envelope is measured to be conservative against its own mesh scatter.

**Verdict: the rule does not reach `naca0015_sail`. No restatement, no withdrawal, no draws.**
The retrofit's five-ladder scope is corrected to four for the rule's purposes, and my half's
price drops from 8.0–13.5 to the cube line alone.

# §9. `cube` — FEATURE CONFIRMED, and the turn rung is GONE. A reconstruction gate is required before any draw.

**In scope, decisively.** Non-monotonicity is asserted as this ladder's verdict on at least five
live surfaces: `cube.json:34,36,42,44` (`"monotone": false`, `guards_failed: ["monotone"]`,
`"rungs not monotone; conservative band…"`), `W3_GUARD_SWEEP.md:38` and its json,
`docket.json:3324`, `NOT_PASSING_REGISTER.md:596` (*"non-monotone ladder"*), and the
credentials-wall row's inconclusive reason (`wall.json:267-283`). Two records additionally raise
an **oscillation** reading, hedged and labelled `mechanism_named_not_claimed`
(`W3_CUBE_SETTLE_RESULTS.md:64-67`, `cube.json:166`).

**The blocking discovery: the rung the feature turns on does not exist on disk, and neither do
its dictionaries.** The turn is at the **medium** rung (103,934 cells). Per the survey:
`cube-rung-coarse` and `cube-rung-medium` have **no case directory anywhere, no points file, no
mesh** — because `sdk/scripts/run_uq_studies.py:80-85` clears the body-keyed mesh cache before
each rung *by design* (*"a ladder MUST NOT reuse a different rung's mesh"*), so **only the finest
rung's mesh survives**. The cube's coarse/medium `blockMeshDict`/`snappyHexMeshDict` were never
archived either (the sail at least kept a `blockMeshDict.scaled`).

**The existing replicate evidence is at the wrong rung and it failed.** `cube.json:88-149` is n=2
at the **production** rung, and it reports its own failure: *"The mesh scatter CANNOT be extracted
from this experiment on this body… at 1.488e-02 it is the same size as run A's own iterative
2-sigma of 1.4686e-02"* — and that control did not reproduce the stored Cd (apart 4.217e-03).
So under §17 there is **no draw-scatter evidence at the rung the feature turns on**, which is
precisely the gap the retrofit exists to close.

## §9.1 PRE-REGISTERED RECONSTRUCTION GATE — fixed before any mesh is built

I will not declare the cube unverifiable-at-source without testing whether the rung is
reproducible, and I will not draw against a rung I cannot show is the archived one. The B-52
precedent required the replicates be **proven same-recipe by checksum**; for cube's medium rung
that checksum is impossible because the reference dictionaries are gone. **Cell count is the
available fingerprint, and it is a sharp one.**

**Gate:** regenerate the medium rung through the archived code path from the body's production
dictionaries at the medium refinement setting, then:

- **Regenerated cell count == 103,934 exactly** → the recipe is reproduced, the rung is
  **verified-by-fingerprint**, and the draws proceed (§3's bar unchanged, §4's prediction
  unchanged). The match is recorded as the evidence standing in for the missing checksum.
- **Regenerated cell count != 103,934** → the rung that produced the published Cd cannot be
  reproduced from what survives, so **draw scatter at the turn rung cannot be measured against the
  archived recipe**. The cube's feature is then marked **UNVERIFIABLE AT SOURCE** per the chief's
  ruling — neither restated nor withdrawn — with the regenerated count reported beside the
  archived one so the size of the discrepancy is on the record.
- **Regeneration fails or the code path no longer produces this rung** → same UNVERIFIABLE AT
  SOURCE verdict, with the failure quoted.

Certification (§6) applies to every mesh that does come into existence, before any solve.

# §10. Record-hygiene finding, reported because a live record is wrong about disk state

`DEAD_LEVER_AUDIT_2026-08-08.md:323,364` and `W3_PUBLISHED_RUNG_REPLICATES.md:67` state that
`certonomous-runs/study-cube-2904cb/` *"no longer exists on disk"* / was *"deleted"*. **It exists
now**, complete with `constant/polyMesh/points`, `processor0–15` and `log.simpleFoam`; the same
applies to `study-naca0015_sail-fdd45c`, which `W3_LADDER_RECIPE_AUDIT.md:160` treats as a sole
survivor. Flagged rather than fixed — those are other agents' records — but any conclusion resting
on the cube production case being unavailable should be re-checked, and the case is available for
anyone who needs it.

**Also inherited, not created here:** the 2026-08-08 birth-certificate audit marked
`.mesh-cache/cube`, `.mesh-cache/naca0015_sail`, `w3-published-rung-cube/b` and
`w3-published-rung-naca0015_sail/b` as *"CERTIFIED (pre-existing record)"* — but that verdict
means **a `log.checkMesh` exists, not that a certificate file was written.** A repo-wide find
returns 28 `birth_certificate.json` files and **none is under a cube or sail path.** So the
certification gate mints these from scratch, exactly as the chief's ruling anticipated.

# §11. CROSS-FAMILY SCREENING SIGNAL — handed to Cases, not a verdict on their arms

The mechanism that deleted cube's turn rung is **generic to the ladder runner**, not specific to
my body: `sdk/scripts/run_uq_studies.py:80-85` keys the mesh cache by body label alone and clears
it before each rung *by design*, so **only the finest rung's mesh survives** unless a ladder was
run under a scheme that writes per-rung keys. Both schemes are present in the cache
(`/home/ubuntu/certonomous-runs/.mesh-cache/`, 36 entries):

| retrofit ladder | per-rung cache entries | implication for a draw at a NON-FINAL turn rung |
|---|---|---|
| `ahmed_35` | **`ahmed_35-rung-coarse-s23-b0.7`, `ahmed_35-rung-medium-s23`** | mesh survives — draws feasible |
| `ahmed_25` | body-label entry only | **likely same problem as cube** |
| `motorBike` | body-label entry only | **likely same problem as cube** |
| `cube` (mine) | body-label entry only | **confirmed gone** — exhaustively searched, no case dir, no points file, no dicts |
| `naca0015_sail` (mine) | body-label entry only | moot — out of scope (§8) |

(Other bodies carrying per-rung entries: `airliner_wing_span52`, `naca0012_wing`, `naca4412_wing`.)

**Stated as a screening signal and deliberately not as a finding about Cases' ladders.** A
body-label-only cache entry does not *prove* a rung's mesh is gone — the cache is one location,
and for cube the exhaustive search across run dirs, mission-output and the cache is what
established it. **The split says I do not grade their arms, so I do not.** What I hand over is the
cheap screen and the method: *check whether your turn rung's mesh exists before pricing its
draws*, because for three of the five retrofit ladders the retrofit's premise — that two draws can
be taken at the rung the feature turns on — may not hold.

If it does not hold for `ahmed_25` or `motorBike`, the honest outcome there is the same one
pre-registered here in §9.1: a reconstruction gate on exact cell count, and
**unverifiable-at-source** if it misses.
