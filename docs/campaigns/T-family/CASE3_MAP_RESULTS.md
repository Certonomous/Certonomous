# CASE 3 — the 16-point motor-in-duct CHT map, assembled: what it shows, and what it is not entitled to say

**DRAFT for Sanaa. Prepared by a heat-transfer `lab-lane` at the
heat-transfer-supervisor's dispatch, 2026-08-31.** This document assembles two
already-graded rungs into one picture. **It assigns no verdict of its own**; every
verdict below is quoted from a grading artifact that already recorded it.

Gates frozen at two documents, and no gate in either is reopened here:

| rung | rows | frozen registration | commit |
|---|---|---|---|
| **T23** | 4 — `P_loss` 305 W × `U_inf` {10, 20, 30, 40} m/s | `docs/campaigns/T-family/T23_PREREGISTRATION.md` | `fe666fd5` |
| **T24** | 12 — `P_loss` {80, 155, 230} W × `U_inf` {10, 20, 30, 40} m/s | `docs/campaigns/T-family/T24_PREREGISTRATION.md` | `b9057489` |

Power levels are **Sanaa's own**, under her one-word ruling **"5. Rescale"**
(`etc/sessions/2026-08-31T1615Z_sanaa_six_answers.md`, answer 5, the chief's
verbatim capture read at source), frozen into T23 §2.6 and inherited unchanged by
T24 §0.1.

**THE GRADING PATH WAS VERIFIED TO BE THE FILE THAT RAN** (`CLAUDE.md` rule 2,
last bullet). The T24 comparator `analyse_t24.py` in the worktree is
**byte-identical to the committed blob at `d9082bfb`**, both sha256
`ef72d5754231ce6ca650b9bf957fe1a0c5fec84ea8dcf9feacce711ede3eee6a` — **the frozen
comparator IS the file that ran.** That check was performed **personally by the
heat-transfer supervisor** under `SUPERVISION_CHARTER.md` §3 and is cited here as
his, not claimed by this lane. The equivalent check for T23 is recorded at
`T23_RESULTS.md` (worktree registration hashing to blob `c341476f`, identical to
`HEAD`).

**Verdict vocabulary fixed by `CLAUDE.md` rule 1: PASS / GATE REACHED / GATE FAIL
/ NOT A RESULT / BLOCKED / PENDING.** No other word appears below as a verdict.
Every figure carries a tag: **MEASURED / DERIVED / INTERPOLATED / EXTRAPOLATED /
ASSUMED**.

---

## HEADLINE

> **CASE 3 MAP: 16 of 16 rows PASS. 0 physics-adverse ( — ) / 0 non-physics ( — ).**
>
> Per Sanaa's GRADING TRANSPARENCY ORDER of 2026-08-31
> (`etc/sessions/2026-08-31T2055Z_sanaa_grading_transparency_order.md`, `4116024a`,
> read at source): the split is stated in her format **because the format is
> standing, not because the map contains anything to classify.** There is no
> non-PASS verdict in this map, and a PASS carries no cause class — cause classes
> attach to non-PASS verdicts only ("Every non-PASS verdict now carries a
> mandatory CAUSE CLASS"). **Both lists are empty and the reason they are empty is
> that nothing failed, not that nothing was looked at.**
>
> **Tier of this map under the CONSOLIDATION-WEEK vocabulary
> (`docs/COVERAGE_MATRIX.md` §1, Ruling 1 final form): SURVEYED — zero green
> columns on V / G / P.** Not `HOLDS`. See §4.

---

## 0. READ THIS FIRST — WHAT 16/16 PASS DOES AND DOES NOT MEAN

**A clean sweep here confirms a registered prediction. It discovers nothing.**
That is not a modest gloss written after the fact; it is what the frozen
registration said **before the solver started**, and it said it in these words
(`T24_PREREGISTRATION.md` lines 233-246, at `b9057489`):

> **"AND HERE IS THE HONEST PART, REGISTERED BEFORE COMPUTE RATHER THAN
> DISCOVERED AFTER IT: B1 IS A WEAK DISCRIMINATOR ON THIS ROW SET, AND THIS
> DOCUMENT SAYS SO INSTEAD OF CLAIMING A GATE IT EXPECTS TO CLEAR TRIVIALLY."**

and, at line 230-231 of the same frozen file:

> **"Zero flags was never the requirement of this tier and must not be engineered
> for."**

The registration predicted, before compute, that **B1 would pass on all twelve
T24 points unflagged, with a smallest predicted margin of +118.2 K**, and it
predicted the twelve `T_max` values themselves to within a registered 2 %
tolerance. **All three predictions came true.** The strongest honest statement
available from these sixteen rows is therefore:

> **A registered prediction about this case was made in advance and was not
> falsified. That is worth recording and it is not a discovery.** The gate that
> was cleared sixteen times was registered, in advance, as one that could not
> discriminate on this row set. **Read as a demonstration of thermal margin, this
> map is weak evidence.**

Three further limits belong on this page and not in a footnote, and each has its
own section: this is a **physicality tier and not a verified one** (§4);
**buoyancy is switched off**, which voids the directive's own Richardson check
(§5); and there is **one unexplained systematic pattern in the twelve T24 rows**
that no verdict depends on and that is nevertheless open (§6).

### 0.1 Sanaa's own words on this result, 2026-08-31, and what they do NOT license

> **"Beautiful work on the 16/16."** — **Sanaa, 2026-08-31**, on receiving this
> result, relayed verbatim through the heat-transfer supervisor.

**Recorded here because she said it, and placed AFTER the section above rather
than before it, deliberately.** The relay names what earned the commendation: the
map, the blind comparator, the falsified-then-corrected level-selection model,
and **the honest `VERIFY` flags**.

> **THE FLAGS EARNED THE COMMENDATION; THEY DID NOT QUALIFY IT.** Nothing in this
> quotation retires §0, §4, §5 or §6, and none of those sections is softened by a
> single word on account of it. **A commendation for honesty that is then used to
> justify claiming more is the one way to forfeit the thing being commended.** The
> map is still `SURVEYED` and not `HOLDS`; it is still not grid-converged;
> buoyancy is still off; and the sign pattern of §6 is still open and still tagged
> `VERIFY`.

---

## 1. THE MAP

**Q1 = `T_max` = max(T) over the whole `housing` region, in °C.** All sixteen
values **MEASURED**, read from the `internalField` of each case's own
`10000/housing/T` at `writePrecision 12`.

| `P_loss` \ `U_inf` | **10 m/s** | **20 m/s** | **30 m/s** | **40 m/s** |
|---:|---:|---:|---:|---:|
| **80 W**  | **38.1374** | **29.0795** | **25.5462** | **23.5897** |
| **155 W** | **59.9609** | **42.3896** | **35.5104** | **31.6747** |
| **230 W** | **81.7844** | **55.6997** | **45.4746** | **39.7598** |
| **305 W** | **103.6078** | **69.0098** | **55.4389** | **47.8448** |

**Provenance by row, because a map that does not say which rung measured which
row is not auditable** (T24 §6.5):

| power row | rung | grading artifact |
|---|---|---|
| 80 / 155 / 230 W | **T24** | `verification/runs/T-family/T24_runs/gate_t24.json` |
| 305 W | **T23** | `verification/runs/T-family/T23_runs/T23_GRADE.json`, `T23_GRADE.txt` |

**The shape, stated plainly.** `T_max` rises linearly with power at fixed
airspeed and falls steeply and non-linearly with airspeed at fixed power. The
hottest corner of the entire map is **(305 W, 10 m/s) at 103.6078 °C**; the
coolest is **(80 W, 40 m/s) at 23.5897 °C**. The whole 16-point surface spans
**80.0 K**, and **every point of it lies below both registered bounds** — the
120 °C design isotherm and B1's 200 °C engineering bound.

**Airspeed buys more than power costs, over this range.** Going from 10 to
40 m/s at fixed power removes **62–63 %** of the temperature rise above `T_inf`;
going from 80 W to 305 W at fixed airspeed multiplies it by 3.81× exactly
[DERIVED from the measured rows].

---

## 2. THE HOLD-THIS-POWER PICTURE — and where it stops being a measurement

This is the engineering question the map exists to answer, and the honest answer
has two halves that must not be run together.

### 2.1 Inside the measured map: **every registered point holds, with margin**

| bound | worst point on the map | measured value | margin |
|---|---|---:|---:|
| **120 °C design isotherm** | (305 W, 10 m/s) | 103.6078 °C | **+16.3922 K** [DERIVED] |
| **B1, 200 °C** | (305 W, 10 m/s) | 103.6078 °C | **+96.3922 K** [MEASURED, `T23_RESULTS.md` §1] |

**MEASURED ANSWER: at every one of the four registered airspeeds, the full
registered power range 80–305 W is held under both bounds.** The 120 °C isotherm
is **crossed nowhere on the map** — which is exactly what T24 §2.3(b) registered
as a prediction *before compute*, and it is confirmed rather than discovered:

> `T24_PREREGISTRATION.md` §2.3(b): *"REGISTERED CONSEQUENCE, before compute: the
> 120 °C isotherm is predicted to be CROSSED NOWHERE on the rescaled 16-point map,
> and the 200 °C bound to be approached nowhere."*

**The consequence is that the map cannot trace the isotherm it was built to
trace** (§4.5 of the registration; T23 deferred the trace because four points
cannot make one, T24 defers it because the isotherm lies off the map entirely).
**The level set was chosen to bracket 120 °C and, on solved physics, brackets
nothing.** That is a finding about the level-selection instrument — already
recorded, already falsified at T23 §2 by 1.90×–3.54× — and it is not a finding
about the solver.

### 2.2 Beyond the map: the crossing powers are **EXTRAPOLATED, not measured**

The rung's registered predictor is an exactness claim about a linear PDE
(`T24_PREREGISTRATION.md` §2.4): with `g = (0 0 0)`, constant properties,
radiation off and both solids `constIso`, the flow field does not depend on
`P_loss` and the temperature rise is exactly proportional to source power at
fixed `U_inf`. Inverting it gives the power at which each bound would be reached:

| `U_inf` | measured rise at 305 W, K | **P at 120 °C** | ×305 W | **P at 200 °C** | ×305 W |
|---:|---:|---:|---:|---:|---:|
| 10 m/s | 88.758 | **361 W** | 1.18× | **636 W** | 2.09× |
| 20 m/s | 54.160 | **592 W** | 1.94× | **1043 W** | 3.42× |
| 30 m/s | 40.589 | **790 W** | 2.59× | **1391 W** | 4.56× |
| 40 m/s | 32.995 | **972 W** | 3.19× | **1711 W** | 5.61× |

> **EVERY FIGURE IN THAT TABLE IS `EXTRAPOLATED`. NOT ONE OF THEM IS A
> MEASUREMENT, AND NOT ONE OF THEM IS AN INTERPOLATION.** The highest power
> anywhere in the map is **305 W**. Each entry sits **1.18× to 5.61× beyond the
> highest power that was ever solved**, on a linearity relation that was
> registered as **REPORTED AND NEVER GATED** (§2.4) and that has been checked only
> **inside** 80–305 W. Nothing in this lab has solved this case above 305 W.

**What IS defensible, and the distinction is the point of this section:**

- **MEASURED** — the sixteen `T_max` values of §1, at the sixteen registered
  points.
- **INTERPOLATED, and defensible** — `T_max` at any power **between 80 W and
  305 W** *at one of the four measured airspeeds*, by the linear relation, which
  the twelve T24 rows measured to be accurate to **≤ 0.99 %** of the predicted rise
  across the whole range (§6). A reader who needs 200 W at 20 m/s may take it.
- **NOT COVERED AT ALL** — anything **between** the four airspeeds. The linearity
  argument is exact in **power** and says nothing whatever about **airspeed**; the
  U-dependence is the full non-linear convective problem, and the map holds four
  samples of it. **There is no registered relation licensing interpolation in U**,
  and this document does not supply one.
- **EXTRAPOLATED, and not a result** — the crossing powers of the table above.

**The blunt version, so the map is not over-read.** Asked *"what power can I hold
at this airspeed?"*, this map answers: **"at least 305 W at every airspeed
measured, with at least 16.4 K to the design isotherm."** Everything past that is
arithmetic on an ungated predictor, at a single mesh level, with no discretisation
error bar, with buoyancy off. **The honest boundary of the deliverable is 305 W.**

### 2.3 The one point that was registered as genuinely undecided — and how it landed

`T23_PREREGISTRATION.md` §2.7 registered **(305 W, 20 m/s) as UNDECIDED before
compute**, at a margin of **+2.70 K** to the 200 °C bound under the
Dittus-Boelter closure against **+79.67 K** under the flat-plate closure — two
closures of the same lumped model disagreeing by **1.763× in h**. It registered,
one-way, that the point **might legitimately flag under B1**, and that a flag
would be *"a real finding"* and *"NOT evidence that the levels were chosen
badly."*

> **IT LANDED AT 69.0098 °C — a clean PASS, 130.99 K under the bound, unflagged**
> [MEASURED, `T23_RESULTS.md` §1.1].

**It landed on one of its two registered sides.** That is the correct reading and
the only one available: the registration predicted **the question**, not the
answer, and a registered-in-advance outcome arriving on one of its declared sides
is not a surprise. **Had it flagged, that too was registered** — which is exactly
why neither outcome could afterwards be read as a level-selection error. The
+2.70 K margin is now known to have been an artifact of the lumped model, which
the same rung falsified by 1.90×–3.54× on all four of its points.

---

## 3. CAUSE CLASSES — Sanaa's standing headline, applied

**Format per the GRADING TRANSPARENCY ORDER, `4116024a`, read at source.**

> **0 physics-adverse ( none ) / 0 non-physics ( none ).**

- **Physics-adverse classes** (`PHYSICS-FAIL`, `MODEL-LIMIT`) — **none.** No row
  in this map returned a value outside a pre-registered band.
- **Non-physics classes** (`REFERENT-CEILING`, `GATE-DESIGN`, `INSTRUMENT`,
  `BOOKKEEPING`, `NAMING/PLUMBING`, `BUDGET/KILL`) — **none.** No row was
  degraded, capped, misfiled or blinded.
- **All sixteen verdicts are PASS**, and per the order a cause class attaches to a
  non-PASS verdict. **There is nothing to classify.**

**Two things this zero is NOT, stated because a bare 0/0 invites both misreadings:**

1. **It is not a claim that nothing went wrong anywhere near this map.** Two
   infrastructure defects were met and are recorded. **First, the queue runner's
   clobber of `STATUS.<case>`, which hit 12 OF 12 T24 cases** — every one carries
   only `launcher_rc`, `end` and `note`, and the `rc`, `wall_s`, `ranks`,
   `core_min`, `cap_core_min`, `timeout_s`, `capped` and `solver` fields the
   launcher wrote are destroyed in all twelve [MEASURED, on disk]. **There are
   ZERO `STATUS.queue.*` files anywhere under `T24_runs/`**, so cfd's R5 namespace
   repair was never exercised here — consistent with all twelve launching before
   that repair reached disk at 20:17:09Z. Counting the earlier occurrences the two
   registrations record (`T22_CHTb_L1`, then all four `T23_P305_U*`; T23 §5.1,
   T24 §3.5a), this defect has now hit **17 cases across three rungs**. **Second,
   a false zero in `run_t24.sh`'s `solvers_already_running` field**, which read
   **0 on all twelve launches while eleven solvers were running**, because `pgrep
   -c chtMultiRegionSim` matches a 17-character pattern against a `comm` the
   kernel truncates to 15
   (`verification/runs/T-family/T24_runs/T24_CONCURRENCY_CONTENTION_NOTE.md` §6).
   **Neither touched a verdict**: the first was routed around by deriving `rc` from
   the log, registered in advance at §3.5a; the second decides nothing, because the
   registered saturation instrument is the **load average**, which was read
   correctly in all twelve. **Under Sanaa's universal rule of 2026-08-26 —
   bookkeeping never voids physics — these are infrastructure and they void no
   row.** They are named here so the 0/0 is not read as "nothing was broken".
2. **It is not a statement about the lab's ability to do the physics at a verified
   tier.** Per the order's own standing definition, *"Can the lab run and
   post-process X?"* is answered by **SURVEYED-or-better with cause classes
   excluding INSTRUMENT / BOOKKEEPING / NAMING**. This map is **SURVEYED** and its
   cause-class list is empty, so it answers that question **affirmatively and at
   exactly that strength** — the lab can run and post-process Case 3. **It answers
   no stronger question, and §4 is why.**

---

## 4. THIS IS A PHYSICALITY TIER, NOT A VERIFIED ONE — **the map is not grid-converged**

`T24_PREREGISTRATION.md` §0.3, frozen before compute:

> **"T24 registers the PHYSICALITY TIER of the map and NOTHING ELSE … NO ROACHE
> TRIPLE, NO GCI, NO OBSERVED ORDER, NO NUSSELT NUMBER, NO HEAT-BALANCE CLOSURE.
> Every point runs at L1 only."**
>
> **"A SINGLE MESH LEVEL ADMITS NO TRIPLE. Any Roache classification, GCI or
> observed order quoted from a T24 artifact is a CATEGORY ERROR."**

The same holds of T23 (`T23_RESULTS.md` §0). Therefore, and stated without
softening:

> **ALL SIXTEEN POINTS OF THIS MAP RAN AT MESH LEVEL L1 AND ONLY L1. THE MAP IS
> NOT GRID-CONVERGED. THERE IS NO DISCRETISATION ERROR BAR ON ANY POINT OF IT, AND
> NONE CAN BE CONSTRUCTED FROM WHAT WAS RUN.** No number in §1 carries a
> quantified numerical uncertainty of any kind.

`CLAUDE.md` rule 5 is **not weakened by this and is not evaded**: rule 5 governs a
grid triple, and this map produces none, so there is no row here whose triple
could be non-`CONVERGING`. **The absence is total, and it is registered, not
discovered.**

**What that costs, item by item, each with the registration that deferred it:**

| deliverable the directive asked for | status | why |
|---|---|---|
| mean Nusselt on the housing vs an annular correlation to 25 % | **DEFERRED** | §4.1 — its 300 W operating point is not a level of the rescaled set; no title-page-verified annular-flow paper on disk (`CLAUDE.md` rule 15); no wall-Nusselt instrument; and **max y+ > 1 at U ≥ 30 m/s**, where §3.4 of the directive forbids wall functions |
| Roache triple on `T_max`, p ∈ [1.3, 2.5], GCI_fine < 2 % | **BLOCKED** | §4.2 — a single mesh level admits no triple; the y+ breach blocks it independently; and `CASE3-DEP-1`, the cross-team dependency asserted to gate it, **is not registered anywhere** and is asserted only in an uncommitted draft that freezes nothing |
| heat balance closed to 1 % | **DEFERRED** | §4.3 — the mutation-tested instrument does not exist for this case |
| 120 °C isotherm traced across the map | **NOT DELIVERED** | §4.5 — the isotherm lies off the map entirely (§2.1) |
| radiative upper bound ε σ (T⁴ − T_inf⁴) A per point | **DEFERRED** | §4.6 — needs a registered emissivity the directive does not supply |

**Tier assignment, under `docs/COVERAGE_MATRIX.md` §1 and Ruling 1 (count the
green columns):** V — no exact solution, no manufactured solution, no correlation
comparison → **not green**. G — no Roache triple at all → **not green**. P — no
public primary source; the 200 °C and 120 °C figures are Sanaa's own engineering
numbers, registered as bounds and expressly **not referents**
(`T24_PREREGISTRATION.md` §1 line 2: *"REFERENCE. NONE, and that is the point of
this tier"*) → **not green**.

> **ZERO GREEN COLUMNS ⇒ `SURVEYED`.** Breadth evidence, ungated on V / G / P —
> *whatever lab gates these rows passed, and they passed sixteen.* **This map is
> not `HOLDS` and not `GATE REACHED`.**

**One deliberate limit on my own reading:** I have applied the matrix's stated
rule to this map's evidence, but **assigning a row's tier in
`docs/COVERAGE_MATRIX.md` is verification's mechanic**, and this document files no
matrix row. The word above is a reading, offered for the supervisor to route.

**The y+ figure, measured and reported and never gated** (§4.4): max y+ on
`fluid_to_housing` is **0.4037 / 0.7515 / 1.0790 / 1.3970** at U = 10 / 20 / 30 /
40 m/s. **Above 1 at U ≥ 30 m/s**, against a directive that requires y+ ≤ 1. It
blocks the correlation tier and the triple; it does **not** void the physicality
rows, whose content is a temperature bound and not a heat-transfer coefficient.
**The twelve T24 cases reproduced T23's four values to every printed digit**, each
measured through the solver's own `-postProcess` route in that case's own
`log.yPlus.fluid` [MEASURED, 12 per-case logs on disk] — which is the registered
consequence of the flow field being independent of `P_loss`, and was registered in
advance at §4.4 as *"not new information"*.

---

## 5. BUOYANCY IS OFF, AND THE DIRECTIVE'S OWN CHECK IS THEREFORE VACUOUS

`T24_PREREGISTRATION.md` §3.3 registers **`constant/g` present in every case with
`value (0 0 0)`**. Directive §3.3 requires *"verify Richardson number
Ri = g β ΔT L / U² < 0.1 on every run"*.

> **WITH g = (0 0 0), Ri ≡ 0 IDENTICALLY, BY CONSTRUCTION, AT EVERY POINT OF THE
> MAP. THE CHECK CANNOT FAIL AND CANNOT INFORM.**

**Ri is not reported anywhere in this document as a passing check, and the
registration prohibited reporting it as one** (§3.4): writing `Ri = 0 < 0.1, PASS`
would be *"evidence annotated as non-binding in its worst form — a criterion
satisfied by the modelling choice that removed the physics it was meant to
police."*

> **THE HONEST STATEMENT, and it is the registered one: buoyancy is switched OFF
> across all sixteen points. Its neglect is a declared omission. WHETHER FORCED
> CONVECTION GENUINELY DOMINATES IS NOT ESTABLISHED BY THIS MAP.**

**And it matters more at the low-speed corner than anywhere else.** The map's
least-favourable combination for that assumption is the **10 m/s column** — the
lowest forced velocity in the set — where the driving ΔT runs from 23.3 K at 80 W
to 88.8 K at 305 W. **The ratio of buoyant to forced transport is not estimated
here and this document will not estimate it**: an estimate needs a β and a g this
case does not carry, and inventing them is precisely what the frozen registration
prohibits (§2.2, §3.4).

**Radiation is likewise OFF** and is a second declared omission with no bound
computed (§4.6). One honest note the deferral does not hide: the twelve T24
temperatures are **lower** than T23's, so the neglected radiative term is
**smaller** than at the point where it was already not bounded — **the omission
does not grow across the map, and it is not bounded anywhere on it.**

---

## 6. THE ONE UNEXPLAINED PATTERN — **all twelve linearity departures share a sign** `VERIFY`

`T24_PREREGISTRATION.md` §2.4 registered the linear-source predictor as
**REPORTED BESIDE EVERY ROW AND USED AS NO GATE**, with a one-way contingency at
**2 %** of the predicted rise. **The contingency did not fire. Nothing in this
section touches any verdict, and no verdict below §1 depends on it.**

**MEASURED, twelve rows, `gate_t24.json` key `linearity_departure_pct`:**

| `P_loss` \ `U_inf` | 10 m/s | 20 m/s | 30 m/s | 40 m/s |
|---:|---:|---:|---:|---:|
| **80 W**  | +0.0285 % | +0.1661 % | +0.4691 % | **+0.9853 %** |
| **155 W** | +0.0097 % | +0.0570 % | +0.1611 % | +0.3386 % |
| **230 W** | **+0.0031 %** | +0.0190 % | +0.0540 % | +0.1137 % |

**Every one of the twelve is POSITIVE — the solved rise exceeds the predicted
rise at every point, without exception.** Largest **+0.9853 %** at (80 W,
40 m/s), smallest **+0.0031 %** at (230 W, 10 m/s); all twelve inside the
registered 2 % tolerance, with the worst using **49 %** of it.

> **WHY THIS IS NOT SCATTER.** Under a null of random sign — the null a
> convergence-noise explanation would imply — twelve independent rows sharing a
> sign has probability **2 × 0.5¹² ≈ 4.9e-04** two-sided (**2.4e-04** one-sided)
> [DERIVED]. **The pattern is systematic, not noise.**

**The arithmetic structure, offered as arithmetic on the twelve numbers and as
nothing else** [DERIVED]. The departure in kelvin is not scattered across the
grid; at each airspeed it is proportional to `(305 − P)` to within **5 %**:

| `U_inf` | departure ÷ (305 − P), K/W, at P = 80 / 155 / 230 | implied intercept `b(U)` = 305 × that, K |
|---:|---|---:|
| 10 m/s | 2.951e-05 / 2.926e-05 / 2.804e-05 | **≈ 0.009 K** |
| 20 m/s | 1.048e-04 / 1.045e-04 / 1.036e-04 | **≈ 0.032 K** |
| 30 m/s | 2.220e-04 / 2.216e-04 / 2.205e-04 | **≈ 0.068 K** |
| 40 m/s | 3.790e-04 / 3.785e-04 / 3.772e-04 | **≈ 0.115 K** |

Read arithmetically: the twelve solved rises are consistent with
`rise = a(U)·P + b(U)` carrying a small **power-independent positive offset**
`b(U)` of **0.009 K to 0.115 K**, growing monotonically with airspeed — which
would vanish identically at P = 305 W, where the predictor is anchored to the T23
measurement by construction. That is why the *percentage* departure grows as the
temperature rise gets small: a fixed offset against a shrinking rise.

> **THIS DOCUMENT CLAIMS NO MECHANISM FOR `b(U)` AND NAMES NO CAUSE.** The table
> above is a decomposition of twelve measured numbers, not an explanation of them.
> Several physical and numerical stories would fit it; **a plausible story is not
> a measurement**, and writing one here would be the exact defect this family
> caught at T23 §2 — an instrument that keeps its advisory role because its output
> is convenient.

**STATUS: OPEN, tagged `VERIFY`.** What would close it, none of which is claimed
or done here: a fifth power level at a measured airspeed to test the intercept
directly; a second mesh level, which the map does not have; or an independent
re-derivation of the departure on a path not using `analyse_t24.py`. **This is a
question for a later registration to take, and it is not this document's to
register** (`ESCALATION_CHARTER` §4.1).

**And the honest counterweight: this is the only thing in the whole map that
could have been surprised, and it is the only thing that was.** T24 §6.4
registered the linearity test as *"the only thing in this rung that can be
surprised"*. **It was — mildly, systematically, below every threshold, and it is
the one item in sixteen rows that is not a confirmation.**

---

## 7. THE SIXTEEN ROWS IN FULL

All values **MEASURED** unless tagged. Q1 from `internalField` of
`<10000>/housing/T`; Q2 = area-weighted average of the `value` entry of the
`housing_to_fluid` patch (never `refValue`), face areas computed from the
housing's own `constant/housing/polyMesh`.

| # | case | rung | P, W | U, m/s | **Q1, °C** | Q2, °C | Q1−Q2, K | B3 | B2 | B1 margin to 200 °C, K | y+ max housing | dep. % | **VERDICT** |
|---:|---|---|---:|---:|---:|---:|---:|---|---|---:|---:|---:|---|
| 1 | `T24_P080_U10` | T24 | 80 | 10 | 38.1374 | 37.5714 | +0.5660 | PASS | PASS | +161.8626 | 0.4037 | +0.0285 | **PASS** |
| 2 | `T24_P080_U20` | T24 | 80 | 20 | 29.0795 | 28.6010 | +0.4785 | PASS | PASS | +170.9205 | 0.7515 | +0.1661 | **PASS** |
| 3 | `T24_P080_U30` | T24 | 80 | 30 | 25.5462 | 25.1178 | +0.4284 | PASS | PASS | +174.4538 | 1.0790 | +0.4691 | **PASS** |
| 4 | `T24_P080_U40` | T24 | 80 | 40 | 23.5897 | 23.1974 | +0.3923 | PASS | PASS | +176.4103 | 1.3970 | +0.9853 | **PASS** |
| 5 | `T24_P155_U10` | T24 | 155 | 10 | 59.9609 | 58.8643 | +1.0967 | PASS | PASS | +140.0391 | 0.4037 | +0.0097 | **PASS** |
| 6 | `T24_P155_U20` | T24 | 155 | 20 | 42.3896 | 41.4622 | +0.9274 | PASS | PASS | +157.6104 | 0.7515 | +0.0570 | **PASS** |
| 7 | `T24_P155_U30` | T24 | 155 | 30 | 35.5104 | 34.6796 | +0.8308 | PASS | PASS | +164.4896 | 1.0790 | +0.1611 | **PASS** |
| 8 | `T24_P155_U40` | T24 | 155 | 40 | 31.6747 | 30.9132 | +0.7615 | PASS | PASS | +168.3253 | 1.3970 | +0.3386 | **PASS** |
| 9 | `T24_P230_U10` | T24 | 230 | 10 | 81.7844 | 80.1570 | +1.6273 | PASS | PASS | +118.2156 | 0.4037 | +0.0031 | **PASS** |
| 10 | `T24_P230_U20` | T24 | 230 | 20 | 55.6997 | 54.3234 | +1.3763 | PASS | PASS | +144.3003 | 0.7515 | +0.0190 | **PASS** |
| 11 | `T24_P230_U30` | T24 | 230 | 30 | 45.4746 | 44.2414 | +1.2332 | PASS | PASS | +154.5254 | 1.0790 | +0.0540 | **PASS** |
| 12 | `T24_P230_U40` | T24 | 230 | 40 | 39.7598 | 38.6290 | +1.1307 | PASS | PASS | +160.2402 | 1.3970 | +0.1137 | **PASS** |
| 13 | `T23_P305_U10` | T23 | 305 | 10 | **103.6078** | 101.4498 | +2.1580 | PASS | PASS | **+96.3922** | 0.4037 | — | **PASS** |
| 14 | `T23_P305_U20` | T23 | 305 | 20 | 69.0098 | 67.1846 | +1.8252 | PASS | PASS | +130.9902 | 0.7515 | — | **PASS** |
| 15 | `T23_P305_U30` | T23 | 305 | 30 | 55.4389 | 53.8032 | +1.6356 | PASS | PASS | +144.5611 | 1.0790 | — | **PASS** |
| 16 | `T23_P305_U40` | T23 | 305 | 40 | 47.8448 | 46.3448 | +1.4998 | PASS | PASS | +152.1552 | 1.3970 | — | **PASS** |

`dep. %` is the §2.4 linearity departure, which exists only for the twelve T24
rows: the four T23 rows are the predictor's own anchor and their departure is
zero by construction, not by measurement — hence "—" and not "0".

**Controls that stand behind these rows, each recorded in `gate_t24.json` per
row** [MEASURED]:

- **Planted-zero, `CLAUDE.md` rule 3** — both readers were shown able to see a
  planted `1.234e-03 K` before either zero was believed: `control_Q1_at_plant` and
  `control_Q2_at_plant` read **1.234000e-03** with a detection floor of
  **1e-06 K** on all twelve rows. **A reader that cannot see the plant refuses at
  `exit 2` rather than degrading.**
- **Anti-degeneracy (B3)** — Q1 and Q2 are two readers of the same solution on
  different code paths with different extents; **Q1 > Q2 and Q1 ≠ Q2 on all
  sixteen rows**, smallest separation **+0.3923 K** at (80 W, 40 m/s), four orders
  above the `writePrecision 12` quantum.
- **Mesh identity** — `mesh_identical_to_T23: true` on all twelve; the
  `points` files of all three regions hash byte-identical across the twelve cases
  and to `T23_P305_U10`.
- **Convergence assertion** — holds on all twelve over `Uy, Uz, h, p_rgh, k,
  omega` at 1e-06. **`Ux` is excluded and the exclusion is justified per case by
  that case's own measured max|Ux|/max|Uz|, between 1.561e-16 and 2.189e-16** — in
  a 5° wedge `x` is circumferential and `Ux` is zero by geometry, so its residual
  is a 0/0 normalisation. **The excluded value is printed, never suppressed**, and
  the exclusion moves no gate because this tier registers no residual gate at all.

---

## 8. COST — `CLAUDE.md` rule 12, estimate versus actual

**The twelve T24 cases** (T23's four were calibrated separately at
`docs/COST_CALIBRATION.md` row `C-20260831T183346.079343Z-d971eca8`, ratio
**0.9751**):

| figure | value | tag |
|---|---:|---|
| registered SUBSET POINT (§5.2) | **360.4 core-min** | **REGISTERED** |
| registered SUBSET CAP, hard | **540.0 core-min** | **REGISTERED** |
| per-case CAP, hard, enacted as `timeout 2700s` | **45.0 core-min** | **REGISTERED** |
| **actual, twelve cases** | **457.0753 core-min** | **MEASURED** |
| **ratio actual / predicted** | **1.2683** | **DERIVED** |
| per-case actual, mean | 38.0896 core-min | **DERIVED** |
| per-case actual, range | 37.2587 – 39.0853 core-min | **MEASURED** |
| **cases capped** | **ZERO** — longest case 2345.12 wall s against a 2700 s timeout | **MEASURED** |
| subset cap utilisation | **84.64 %** of the registered 540.0, leaving 82.92 unused | **DERIVED** |
| worst single case against its own 45.0 cap | **86.86 %** — `T24_P155_U30` at 39.0853 core-min | **DERIVED** |
| USD at actual | **$0.3908** | **DERIVED, NOT MEASURED** |

Per-case core-minutes are `wall_s × ranks ÷ 60` taken from each case's own
`log.solve` `ExecutionTime` line at 1 rank — **not from `STATUS`**, which the
queue runner destroyed again (§3.5a registered that derivation in advance rather
than discovering the loss at grading time).

**WASTE, NAMED SEPARATELY AND NEVER FOLDED INTO THE RATIO**
(`COMPUTE_BUDGET_CHARTER.md` §6): **0.0 core-min.** Twelve launches, twelve
completions, no relaunch, no capped case. **GROSS = CLEANED**: the §2 stall rule
matches a row over 3600 wall s and the longest ran 2345.12 s, so the rule matches
nothing and no judgement enters the figure.

**ATTRIBUTION: the entire 26.83 % overrun is CONCURRENCY CONTENTION, and it was
measured rather than inferred.** The twelve ran **twelve-concurrent** on a 16-core
box under Sanaa's 2026-08-31T15:45Z standing order that the box must be full; the
registered POINT of 30.0321 core-min per case was measured on T23 at
**four**-concurrent. `T24_CONCURRENCY_CONTENTION_NOTE.md` measures the penalty at
**26.7 % – 29.9 %** by two independent probes at matched iteration bands, and the
realised per-case ratio against T23's mean is **+26.83 %** (mean `ExecutionTime`
**2285.3767 s** twelve-concurrent against T23's four-concurrent **1801.9275 s**);
longest against longest, 2345.12 s against 1829.39 s, is **+28.19 %**. **Both sit
inside the pre-compute bracket, the mean 0.13 points off its lower edge.** §5.3
registered that a penalty **above ~48 %** caps a case; the measured 26.83 % sits
**55.9 % of the way** to that trigger, which is why no case capped and why the
1.4984× headroom held.

> **The mispredicted component is therefore approximately zero: the estimate was
> right about the physics and wrong about nothing except the concurrency it was
> registered as not covering.** §5.3 of the frozen document registered that
> exposure **before compute**, in these terms: *"this rung borrows across NO
> geometry change but across a THREEFOLD change in concurrency, and whether a rate
> survives that is NOT established by anything the lab has measured."*
>
> **It does not survive it. That is the calibration figure this rung existed to
> produce (§5.5), and it is a NEGATIVE answer reported as negative: a per-case
> cost measured at one concurrency does not transfer to another, and a cap
> calibrated at low concurrency under-provisions at high concurrency.**

**Four honesty notes on the cost figures:**

1. **The dollar figure is DERIVED, not measured.** The rate is the owner-stated
   c7a.4xlarge **$0.0513/core-h**, reported-by-owner 2026-08-21/22. **The box
   cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5).
2. **The §5.5 saturation exclusion did not fire, and I checked it rather than
   assuming it.** A case whose `START.<case>` records a 1-minute load average above
   `nproc` = 16 produces a cost but **not** a calibration row. **In LAUNCH ORDER
   the twelve readings are 5.40, 5.69, 3.91, 3.42, 3.81, 5.82, 6.02, 6.67, 7.63,
   8.66, 9.76, 11.15** [MEASURED, the `start` blocks of `gate_t24.json`, ordered by
   each case's own `start_utc`]. **The sequence is NOT monotonic: it rises, drops
   to its floor of 3.42 at `T24_P080_U40` and 3.81 at `T24_P155_U10`, and only
   then climbs to 11.15.** The maximum is **11.15 < 16**, so **no case crossed the
   threshold, none is excluded, and the calibration row admits all twelve.** **The
   registration expected some to be excluded by construction; none was.** The
   ruling turns only on the maximum, so the shape of the sequence changes nothing
   — it is stated correctly because a sorted list described as a sequence is a
   claim about the box that was never measured.
3. **`loadavg` OVERSTATES this contention and must not be used to size it** — it
   read **24.47** on a 16-core box at an instant when **11.9 cores** were genuinely
   consumed, roughly a factor of two (contention note §4a). It is the eligibility
   instrument §5.5 registered; it is **not** the sizing instrument, and the
   attribution above uses the matched-band probes instead.
4. **ONE COMPONENT OF THE TRUE SPEND IS STATED AS ABSENT RATHER THAN
   APPROXIMATED.** The mesh and post-processing utility compute — `blockMesh`,
   `splitMeshRegions`, three `checkMesh` per case, `yPlus` — is **NOT QUANTIFIED**,
   because those logs carry **zero `ExecutionTime` lines** and no other artifact
   times them. It sits outside the registered POINT as well, which prices
   39,680 cells × 10,000 iterations of solve and nothing else, so the ratio above
   is like-for-like; **but the run's true total spend is 457.0753 core-min PLUS an
   unmeasured utility increment**, and saying so is worth more than a number
   nobody can cite.

**The whole map, both rungs:** 120.1285 + 457.0753 = **577.2038 core-min**
[DERIVED from two MEASURED figures], against the directive's Case 3 cap of **700
core-min** — **inside**, at 82.5 % of it. The directive's own estimate of *"~8
core-h"* = 480 core-min is exceeded by **20.3 %**, and the whole of that excess is
the concurrency penalty measured above.

---

## 9. WHAT THIS DOCUMENT IS NOT, AND WHAT IS STILL OWED

- **It assigns no verdict.** Every PASS above is quoted from `gate_t24.json` or
  `T23_GRADE.json`. **This document grades nothing and marks nothing.**
- **It amends nothing.** Both registrations are frozen and neither is edited
  (`CLAUDE.md` rule 6). T23's committed figures — including §2.5's "9 of 16 /
  2 of 16" flag arithmetic, now known to have been computed from an instrument the
  same rung falsified — **stand as committed and are not rewritten.**
- **`T24_RESULTS.md` DOES NOT EXIST AND THIS DOCUMENT DOES NOT SUBSTITUTE FOR
  IT.** `T24_PREREGISTRATION.md` §6.5 registers a results record carrying, per row,
  the full residual set with `Ux` printed and excluded, the `START.<case>` load
  reading, and the per-case core-minutes. This map report carries the map, the
  verdicts, the controls and the calibration; **it does not carry the full §6.5
  per-row residual record, and that record is still owed.**
- **The cost-calibration row is FILED, and this document does not file it.**
  **`docs/COST_CALIBRATION.md` row `C-20260831T210913.811885Z-2663ea60`**, landed
  at commit `c667c10f` [MEASURED, read at line 336 of that file]. **Rule 12's
  estimate-versus-actual clause is therefore discharged in filing as well as in
  substance**, and §8 above is a summary of that row, not a substitute for it. The
  id was minted by `scripts/append_record.py --allocate-id`, which is the sole
  producer of that form and refuses a hand-written one.
- **It files no `COVERAGE_MATRIX.md` row.** §4's `SURVEYED` reading is offered,
  not registered.
- **It sends nothing.** `CLAUDE.md` rules 7 and 8: submissions are **PARKED**,
  Certonomous is **permanently private**, and this is a repository document that
  stays in the repository.

---

## 10. WHERE THIS LANE DIFFERS FROM ITS SUPERVISOR'S BRIEF

Recorded rather than silently applied, so the supervisor rules on each.

1. **The hold-this-power figures are EXTRAPOLATED, not interpolated.** The brief
   asked me to state where I interpolate rather than measure. **On this map, the
   engineering answer is not reached by interpolation at all.** Every point of the
   16-point surface lies under both bounds, so the bound-crossing power at every
   airspeed lies **outside** the solved set — 1.18× to 5.61× beyond the highest
   power ever solved for this case. §2.2 therefore labels those figures
   `EXTRAPOLATED` and reserves `INTERPOLATED` for the one thing it genuinely
   licenses: power **between 80 W and 305 W at a measured airspeed**. **The
   distinction is not pedantic — an interpolated value sits between two
   measurements and an extrapolated one sits beyond all of them.** **RULED:
   `EXTRAPOLATED` stands and is not dialled back**, the supervisor recording that
   his brief was wrong on this point and that calling it interpolation would have
   been an overclaim in the one section an engineer would act on.
2. **I added a limit the brief did not name: there is no licence to interpolate
   in AIRSPEED.** The §2.4 linearity argument is an exactness claim in `P_loss`
   only. Between the four measured airspeeds the map holds four samples of the
   full non-linear convective problem and **no registered relation connects
   them.** I judged this the likeliest way the map gets over-read, so it is stated
   in §2.2 in the same breath as the licensed interpolation. **RULED: kept**, as a
   strengthening the brief should have asked for.
3. **The p-value is stated two-sided and one-sided.** The brief's `p ≈ 0.0005` is
   the two-sided figure and I reproduce it as **4.9e-04**; the one-sided figure is
   **2.4e-04**. Both are printed so nobody has to guess which null was meant.
4. **I added an arithmetic decomposition of the linearity departures, and no
   mechanism with it.** §6 records that the twelve departures are proportional to
   `(305 − P)` to within 5 % at each airspeed, implying a power-independent offset
   of 0.009–0.115 K growing with airspeed. **This is arithmetic on twelve measured
   numbers, not an explanation of them**, and §6 says so in terms and names no
   cause. **RULED: kept** — as DERIVED arithmetic, out of the headline, with the
   sign test printed independently and "a plausible story is not a measurement"
   retained in terms. The supervisor's ground for keeping it is that it makes the
   finding **more falsifiable**: a successor can now test *"is there a
   power-independent offset that grows with airspeed?"* rather than only *"why are
   they all positive?"*
5. **The 0/0 cause-class headline carries two named infrastructure defects
   underneath it.** The brief's 0/0 is correct and I state it in Sanaa's format.
   I judged that a bare 0/0 would misread as "nothing was broken", when in fact
   the `STATUS` clobber and the `pgrep` false zero both occurred and **neither
   touched a verdict**, so neither earns a cause class. §3 names them and says why
   they are not classified. **RULED: kept.** A clean 0/0 headline that hides
   referee trouble is the same inversion Sanaa's order exists to end, read from the
   other side: **referee trouble must not wear a physics costume, and a physics
   headline must not conceal referee trouble.**
6. **Filing: the intended path is legal and I did not change it.**
   `docs/campaigns/T-family/CASE3_MAP_RESULTS.md` satisfies `check_filing.py`'s R7
   basename pattern (`^[A-Z][A-Za-z0-9]*(_[A-Z0-9][A-Z0-9_-]*)?\.md$`), verified
   against the regex in the script rather than assumed from the charter prose.
   **One caveat the supervisor may want to weigh: `CASE3` is a directive family
   name, not a rung id like `T23`/`T24`, and every other record in this directory
   leads with a rung.** The check accepts it; the convention arguably points at a
   rung-led name. I left it as briefed rather than renaming on my own judgement.

### 10.1 Corrections applied after review — **including one of this lane's own**

Boarded rather than silently absorbed. Each was re-measured at source by this lane
before the edit was made, rather than applied on the strength of the message that
reported it.

1. **THE LAUNCH LOAD-AVERAGE SEQUENCE — a defect in this lane's first draft.**
   This lane **sorted the twelve values and described the sorted list as the launch
   sequence**, calling it monotonic with a floor of 5.40. Ordered by each case's
   own `start_utc` it reads **5.40, 5.69, 3.91, 3.42, 3.81, 5.82, 6.02, 6.67,
   7.63, 8.66, 9.76, 11.15** — **not monotonic; floor 3.42 at `T24_P080_U40`, with
   a second dip to 3.81 at `T24_P155_U10`.** Corrected at §8. **The §5.5 ruling is
   unchanged**, because it turns only on the maximum, 11.15 < 16. **The supervisor
   made the mirror-image error independently** — reading one `START` file and
   taking 5.40 for the floor — so this is boarded as a correction against **both**
   readings and not one. **The generalisable form: a sorted list presented as a
   sequence is a claim about the box's behaviour over time that was never
   measured, and it survives review precisely because the conclusion it supports
   happens to be right.**
2. **The `STATUS` clobber count** was understated as "nine cases". Measured: **12
   of 12 in T24**, every one reduced to `launcher_rc`/`end`/`note`, and **17 cases
   across three rungs** counting the occurrences the two registrations already
   record. **Zero `STATUS.queue.*` files under the run root.** Corrected at §3.
3. **The cost-calibration row** was reported as owed; it had **landed** as
   `C-20260831T210913.811885Z-2663ea60` at `c667c10f` after this lane's grep ran.
   Corrected at §9. **A "not filed" claim ages, and this one aged in minutes.**
4. **The rule-2 grading-path hash check** was reported as not performed by this
   lane. The supervisor **performed it personally**; the header now asserts the
   frozen comparator is the file that ran, with the commit and sha256, attributed
   to him rather than claimed here.

---

## 11. ARTIFACTS — every number above cites one of these

| what | path |
|---|---|
| T24 frozen registration | `docs/campaigns/T-family/T24_PREREGISTRATION.md` (`b9057489`) |
| T23 frozen registration | `docs/campaigns/T-family/T23_PREREGISTRATION.md` (`fe666fd5`) |
| T23 results record | `docs/campaigns/T-family/T23_RESULTS.md` |
| T24 grading output — the twelve rows | `verification/runs/T-family/T24_runs/gate_t24.json` |
| T23 grading output — the four rows | `verification/runs/T-family/T23_runs/T23_GRADE.json`, `T23_GRADE.txt` |
| T24 grader / marker | `verification/runs/T-family/T24_runs/analyse_t24.py`, `mark_done_t24.py` |
| T23 grader / marker | `verification/runs/T-family/T23_runs/analyse_t23.py`, `mark_done_t23.py` |
| completion markers, 16 | `verification/runs/T-family/T24_runs/DONE.T24_P{080,155,230}_U{10,20,30,40}`, `verification/runs/T-family/T23_runs/DONE.T23_P305_U{10,20,30,40}` |
| solver logs, 16 | each case's `log.solve` |
| y+ logs, 16 | each case's `log.yPlus.fluid` |
| launch-instant load readings, 12 | `verification/runs/T-family/T24_runs/T24_P*/START.T24_P*` |
| the contention measurement | `verification/runs/T-family/T24_runs/T24_CONCURRENCY_CONTENTION_NOTE.md` |
| T24 comparator, frozen and hash-verified | `analyse_t24.py` at commit `d9082bfb`, sha256 `ef72d575…3eee6a` |
| T24 verdict artefacts | committed at `cc5f1af4` |
| **T24 calibration row** | `docs/COST_CALIBRATION.md`, **`C-20260831T210913.811885Z-2663ea60`** (`c667c10f`) |
| T23 calibration row | `docs/COST_CALIBRATION.md`, `C-20260831T183346.079343Z-d971eca8` |
| STATUS files, all twelve clobbered | `verification/runs/T-family/T24_runs/T24_P*/STATUS.T24_P*` |
| Sanaa's rescale ruling | `etc/sessions/2026-08-31T1615Z_sanaa_six_answers.md`, answer 5 |
| Sanaa's grading transparency order | `etc/sessions/2026-08-31T2055Z_sanaa_grading_transparency_order.md` (`4116024a`) |
| Sanaa's box-full standing order | `etc/sessions/2026-08-31T1545Z_sanaa_box_full.md` |

---

## 12. AUTHORITY, AND WHAT IS NOT CLAIMED

Prepared by a heat-transfer `lab-lane` at the heat-transfer-supervisor's dispatch.

**Sanaa's 14-day rule freeze is honoured**
(`etc/sessions/2026-08-31T1544Z_sanaa_plumbing_freeze.md`): this document proposes
**no new procedural or bookkeeping rule and creates no new tool.** Every figure in
it is read from an artifact that already existed; nothing was re-run to produce
it.

**A supervisor's check is not claimed as performed here.**
`SUPERVISION_CHARTER.md` §3's four checks are the supervisor's own, and the
measurement-script diff and the pre-registration-committed-before-compute check
are **not** claimed by this lane.

**No agent's message is Sanaa's consent** (`CLAUDE.md` rule 9). The session files
cited are the chief's verbatim capture of her own words and are cited as such.

**SUBMISSIONS ARE PARKED** (`CLAUDE.md` rule 7) and **Certonomous is permanently
private** (rule 8). **This document is not sent, filed, uploaded, posted or
published anywhere. It stays in this repository.**
