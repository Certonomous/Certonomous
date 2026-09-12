# T23G2Rn2 — RESULTS. THE §2ba NUMERICS SUCCESSOR: THE LINEAR-SOLVER REPAIR WORKED, THE LADDER BECAME CONVERGING, AND THE RUNG IS STILL `NOT A RESULT`

## RUNG VERDICT: **NOT A RESULT**

**Read verbatim from the comparator's own final line**, recorded in
`verification/runs/T-family/T23G2Rn2_runs/T23G2Rn2_RUNG_VERDICT.txt`:

> `RUNG VERDICT: NOT A RESULT`

**One gate produced this verdict and one only: `G-RATIO`.** Every other gate on
the rung PASSED — `G-MESHSIM` PASS, `G-CONV` PASS, `G-YPLUS` PASS, `G-PLATEAU`
PASS, `G-ORDER` PASS
(`T23G2Rn2_RUNG_VERDICT.txt`, the per-gate block). The three levels ran clean to
`endTime` with `rc = 0`, every one of the twenty registered planted-zero controls
was constructed and read its plant back, and the Roache triple is `CONVERGING` at
`dim = 2` on all five graded quantities. **This is a real graded outcome, not an
execution failure and not an instrument crash** — the comparator exited **3**,
which its own interpretation block fixes as *"graded verdict (0=PASS, 1=GATE
FAIL, 3=NOT A RESULT)"*.

**This record does not re-grade the rung.** Every number below is transcribed
from the frozen comparator's captured stdout; nothing was hand-read, no GCI was
computed outside the comparator, and no verdict here differs from the one the
comparator printed on 2026-09-10.

| artifact | path |
|---|---|
| whole-rung verdict (the record of record) | `verification/runs/T-family/T23G2Rn2_runs/T23G2Rn2_RUNG_VERDICT.txt` |
| frozen comparator stdout (every number below) | `verification/runs/T-family/T23G2Rn2_runs/T23G2Rn2_COMPARATOR_STDOUT.txt` |
| frozen registration | `docs/campaigns/T-family/T23G2Rn2_PREREGISTRATION.md` |
| comparator (grading path) | `docs/campaigns/T-family/analyse_t23g2rn2.py` |
| per-level completion + cost records | `verification/runs/T-family/T23G2Rn2_runs/T23G2Rn2_L{1,2,3}/STATUS.T23G2Rn2_L*` |
| detached autograder log | `verification/runs/T-family/T23G2Rn2_runs/autograde_rung.watch.log` |
| predecessor cost row this rung closes | `docs/COST_CALIBRATION.md` row `C-20260909T183500.000000Z-t23g2rn` |

---

## 1. THE SINGLE GROUND — `G-RATIO`, AND WHY IT IS A REFUSAL AND NOT A FAILURE

`G-RATIO` (registration §5.3, reused unchanged from T23G2R) requires the ratio of
the **smallest inter-level difference** to the **finest iterative change** to be
`>= 10`, on every graded quantity. What the comparator measured, on all six
(`T23G2Rn2_COMPARATOR_STDOUT.txt`, the `G-PLATEAU and G-RATIO` block):

| q | plateau | finest iterative change | smallest inter-level difference | ratio | cell |
|---|---|---|---:|---:|---|
| `Q1` | PLAT/PLAT/PLAT | `0.000000e+00` | `4.325366e-01` | `inf` | **NOT A RESULT** |
| `Q2` | PLAT/PLAT/PLAT | `0.000000e+00` | `4.291944e-01` | `inf` | **NOT A RESULT** |
| `Q3` | PLAT/PLAT/PLAT | `0.000000e+00` | `4.286144e-01` | `inf` | **NOT A RESULT** |
| `Q4` | PLAT/PLAT/PLAT | `0.000000e+00` | `4.278386e-01` | `inf` | **NOT A RESULT** |
| `Q5` | PLAT/PLAT/PLAT | `0.000000e+00` | `2.787029e-05` | `inf` | **NOT A RESULT** |
| `Q6` | PLAT/PLAT/PLAT | `0.000000e+00` | `4.290088e-01` | `inf` | **NOT A RESULT** |

**The ratio is `inf`, which numerically clears a `>= 10` bar, and the comparator
refused it anyway.** Its stated ground, quoted verbatim from the stdout:

> *"the iterative change is EXACTLY 0.0, so this gate's zero-branch returns
> infinity REGARDLESS OF THE NUMERATOR ENTIRELY. The numerator was never
> consulted, so a PASS here would be attributable to the denominator being zero
> and to NO PROPERTY OF THE LADDER — a pass from a degenerate path. The ratio is
> UNINTERPRETABLE, not meaningless."*

This is rule 3's discipline applied to a gate rather than to a reader: a verdict
produced by a path that could not have returned anything else is not evidence.
The registered threshold was **not** moved to accommodate it — the stdout records
that `RATIO_MIN = 10` is **UNTOUCHED** and `G-RATIO` **remains registered on every
graded quantity**, with every number the unlicensed gate would have graded
printed beside it. The gate turned rows that would otherwise have read `PASS` or
`GATE FAIL` **into** `NOT A RESULT`, which is the only direction `CLAUDE.md`
rule 5 permits.

**Rule 5 step (1) did NOT fire.** Every level is iteratively converged and every
quantity plateaued. The `NOT A RESULT` comes from the `G-RATIO` cell, and that
distinction is most of what this rung bought.

---

## 2. THE LADDER — AS REGISTERED, MEASURED FROM THE BUILT `polyMesh`

| level | cells (total) | `endTime` | `r` vs next |
|---|---:|---:|---:|
| `T23G2Rn2_L1` | 40,320 | 8,000 | — |
| `T23G2Rn2_L2` | 90,720 | 16,000 | `r21 = 1.5000` |
| `T23G2Rn2_L3` | 204,120 | 28,000 | `r32 = 1.5000` |

Cell counts are the comparator's registered `CELLS` values, asserted against the
built mesh (`analyse_t23g2rn2.py:91`; the assertion at `:851`). `G-MESHSIM`
measured, from the built `polyMesh` and not from the dictionary
(`T23G2Rn2_COMPARATOR_STDOUT.txt`, `G-MESHSIM` block):

- cell-count ratio **exactly `2.250000000`** in **every** region (`fluid`,
  `housing`, `core`) at **both** steps — six ratios, six `PASS`;
- first-cell-height ratio `1.500024 / 1.500024 / 1.499995 / 1.500024` (L1/L2) and
  `1.500016 / 1.500016 / 1.499997 / 1.500016` (L2/L3) across
  `centrebody_down`, `centrebody_up`, `duct_wall`, `fluid_to_housing` — all
  inside the registered `1.500 ± 0.005`;
- cells across the housing wall at the **coarsest** level: **8**, against the
  registered floor of 8 (the note records that T23G carried 4).

**`G-MESHSIM: PASS`.** `r21 = r32 = 1.5000` exactly and `dim = 2` — the case is a
wedge one cell thick circumferentially, so a 2.25× cell count is `r = 1.5`, not
`r = 2.25^(1/3)`.

---

## 3. `G-CONV` — **PASS ON ALL THREE LEVELS**, AND THIS IS THE REPAIR THAT THIS RUNG EXISTED TO TEST

| level | `G-CONV` | worst asserted | `Ux` exclusion, measured |
|---|---|---|---|
| `T23G2Rn2_L1` | **CONVERGED** | all within tolerance | `max|Ux|/max|Uz| = 1.930e-16` |
| `T23G2Rn2_L2` | **CONVERGED** | all within tolerance | `max|Ux|/max|Uz| = 3.242e-16` |
| `T23G2Rn2_L3` | **CONVERGED** | all within tolerance | `max|Ux|/max|Uz| = 5.075e-16` |

(`T23G2Rn2_COMPARATOR_STDOUT.txt`, `G-CONV` block.) The gate is `h <= 1e-9` and
the others `<= 1e-8`, **reused unchanged** from T23G2R — registration §3 states
the 1e-8 `p_rgh` threshold is not moved, and §2 lowers only the *linear-solver*
floor so the run can **meet** the frozen gate. `Ux` is excluded with the exclusion
itself measured per level rather than asserted.

**`G-CONV: PASS`.** T23G2R failed exactly here (`tolerance == gate` floor-pinned
`p_rgh`); T23G2Rn over-corrected with `relTol 0` and was stopped `PENDING` on a
cost-model miss. The §2.1 edit — `p_rgh` `tolerance 1e-08 → 1e-09`, `relTol 0.01`
held, `maxIter 100` inserted — is the first configuration in this lineage under
which all three levels clear the unchanged convergence gate.

**`G-PLATEAU: PASS`** on all six quantities, all three levels (`PLAT/PLAT/PLAT`
in the §1 table).

---

## 4. `G-YPLUS` — PASS ON EVERY WALL PATCH, EVERY LEVEL, TWO INSTRUMENTS

Gate: `max y+ <= 1.0`, every wall patch, every level, two instruments agreeing to
within 2 % (registration §3, reused unchanged). Measured
(`T23G2Rn2_COMPARATOR_STDOUT.txt`, `G-YPLUS` block):

| patch | L1 max | L2 max | L3 max |
|---|---:|---:|---:|
| `centrebody_down` | 0.3475 | 0.2333 | 0.1563 |
| `centrebody_up` | 0.8606 | 0.6372 | 0.4720 |
| `duct_wall` | 0.6177 | 0.4574 | 0.3388 |
| `fluid_to_housing` | 0.3562 | 0.2392 | 0.1602 |

The worst value on the rung is `0.8606` on `centrebody_up` at L1 — 14 % of head
room below the gate, and falling monotonically with refinement. On every level
the comparator recorded *"primary instrument PRESENT and agrees with the
independent reader to within 2%"*, so the inherited `R6` refusal branch (absent
primary log ⇒ REFUSE) never had to fire. **`G-YPLUS: PASS`.**

---

## 5. THE TWENTY PLANTED-ZERO CONTROLS — **20 OF 20 CONSTRUCTED AND PASSED**

Rule 3 requires that a reader be shown able to see a non-zero before its zero is
believed. The registration commits 6 quantities × 3 levels + 2 y+ readers = **20**.
All twenty were constructed and all twenty passed
(`T23G2Rn2_COMPARATOR_STDOUT.txt`):

- **18 quantity controls**, `PLANT = 0.001234`, `Q1`–`Q6` × L1/L2/L3, every one
  `PASSED`; the stdout's own tally reads *"18 of the 18 registered quantity
  controls CONSTRUCTED AND PASSED"*.
- **Control [19/20] — independent y+ field reader @L3**: planted
  `x(1 + 0.001234)` into **181,694** vectors of `U`; every wall patch moved by
  `sqrt(1 + PLANT) = 1.000616809773`, worst relative miss `2.219e-16` on
  `centrebody_down` — **PASSED**.
- **Control [20/20] — primary y+ log reader @L3**: planted `0.001234`, read back
  `0.001234` — **PASSED**.

Each graded quantity additionally carries its per-row control in the `G-ORDER`
block: `reader Q<n> @T23G2Rn2_L3 saw 0.0012340000000108375` against a plant of
`0.001234`, on `Q1`, `Q2`, `Q3`, `Q4` and `Q6`.

**Consequence for §1.** The exactly-zero iterative changes that made `G-RATIO`
uninterpretable are *not* blind zeros — the readers producing them are the same
readers that saw `1.234e-03`. `G-RATIO`'s refusal is a statement about the gate's
arithmetic, not about the instrument's eyesight.

---

## 6. THE SIX QUANTITIES — VALUES, TRIPLES, ORDERS, GCI

Roles are reused unchanged from `T23G2_PREREGISTRATION.md` §3: `Q4` core
volume-averaged `T` is the **primary order quantity**; `Q5` housing surface heat
flux is **REPORTED, NEVER GATED**; `Q1` max(T) housing, `Q3` max(T) core and `Q2`
areaAvg(T) on `housing_to_fluid` **receive `Q4`'s band** `[46.0, 56.0] K`; `Q6`
housing volume-averaged `T` is carried and receives no band. Temperatures are
graded on `ΔT = T − 288.0 K`. `Fs = 1.25`, `dim = 2`.

Every triple below is `('T23G2Rn2_L1','T23G2Rn2_L2','T23G2Rn2_L3')`, cells
`(40320, 90720, 204120)`, `r21 = r32 = 1.5000 (equal)`, state **`CONVERGING`** —
so the three values are monotone and the GCI the comparator printed is quotable.

| q | fine value | three values (coarse→fine) | state | order `p` | GCI @ `Fs = 1.25` | band cell as printed |
|---|---:|---|---|---:|---|---|
| `Q4` core vol-avg `T` | `52.5146` | `53.58202682, 52.9424286, 52.51459002` | CONVERGING | `0.9917` | `2.0575 %` = `1.0805` abs | **NOT A RESULT** (no band registered for `Q4`) |
| `Q1` max(T) housing | `51.9184` | `52.99910236, 52.35092296, 51.91838637` | CONVERGING | `0.9976` | `2.0888 %` = `1.08448` abs | `PASS` |
| `Q2` areaAvg(T) `housing_to_fluid` | `50.1037` | `51.17419862, 50.53285142, 50.10365705` | CONVERGING | `0.9906` | `2.1662 %` = `1.08535` abs | `PASS` |
| `Q3` max(T) core | `56.0211` | `57.09118375, 56.44973901, 56.02112464` | CONVERGING | `0.9943` | `1.9260 %` = `1.07897` abs | **`GATE FAIL`** |
| `Q6` housing vol-avg `T` | `50.1664` | `51.23642968, 50.59536851, 50.16635968` | CONVERGING | `0.9906` | `2.1627 %` = `1.08492` abs | **NOT A RESULT** (no band registered for `Q6`) |

**These cells are `G-ORDER`/band cells, and the rung verdict above them is
`NOT A RESULT`.** `G-RATIO` (§1) fires on every one of these quantities, and rule
5 lets a gate turn a `PASS` or a `GATE FAIL` **into** `NOT A RESULT` and never
the reverse. Nothing in this table is awarded.

**`Q4` and `Q6` were downgraded by the comparator itself, before `G-RATIO`.** The
`T23G2_PREREGISTRATION.md` §3 role table transfers `Q4`'s band to `Q1` (`:452`),
`Q3` (`:453`) and `Q2` (`:454`) **and to nobody else**, so the band verdicts
printed for `Q4` and `Q6` are recorded in the stdout as *"DISCLOSED, NOT GRADED …
it licenses nothing"*, and the rows read `VERDICT DOWNGRADED PASS -> NOT A
RESULT: with no registered band there is no band claim to make.* The rows were
**not removed** from the rung rollup — the rollup-exclusion limb of `R4` was
refused.

**`Q3` is the one substantive band exceedance on the rung.** Fine value
`56.0211 K` against a ceiling of `56.0 K`: over by **`0.0211 K`**, i.e. **0.038 %**
of the value — while the comparator's own discretisation uncertainty on that same
row is `GCI = 1.9260 % = 1.07897 K absolute`. The exceedance is roughly **1/51 of
the uncertainty band around it.** That is recorded here as an observation, not as
a licence: the row's cell is `NOT A RESULT` and no claim about `Q3` is made.

### `Q5` — REPORTED, NEVER GATED

Values `[-1.898150286178, -1.898122415891, -1.898062766386]`, state **`DIVERGENT`**,
order `-1.876671248976905`. **No GCI is quoted and none was computed** — the three
values are not monotone and rule 5 forbids it. The registration pre-registers this
as prediction **P4**: *"A DIVERGENT or STAGNANT reading here is PRE-REGISTERED as
the expected outcome (P4) and is NOT a failure of this rung: the quantity is
pinned by the imposed 305 W source to ~4e-5 relative. A CONVERGING reading in
[1.5, 2.5] would mean P4 LOST."* The spread across the three levels is
`4.6e-5` relative, matching the registration's "~4e-5 relative" — P4 held.

---

## 7. `G-ORDER`, AND `A2.1` — THE DISCRIMINATING OBSERVATION

**`G-ORDER: PASS`** — `p(Q4) = 0.9917`, registered band `[0.5, 1.5]`
(`T23G2_PREREGISTRATION.md:834`, `A1.2`), finest triple `CONVERGING`
(`T23G2Rn2_COMPARATOR_STDOUT.txt`, final `G-ORDER` block).

The band is `[0.5, 1.5]` and **not** `[1.5, 2.5]` for a reason the comparator
prints beside it: the formal order of the energy convection term is **one**, at
`T23G_F/system/fluid/fvSchemes` line 33, `div(phi,h) bounded Gauss upwind`.
Sanaa's §0 point 3 is scheme-relative. The five measured orders — `0.9906`,
`0.9906`, `0.9917`, `0.9943`, `0.9976` — span **0.0070** and sit within **0.01**
of the formal first order of the scheme actually discretising the energy equation.

**`A2.1`, registered before the run:** `p(Q4) = 0.9917`, `p(Q1) = 0.9976`,
**spread = 0.0059**. The registration predicts `H-MESH`: spread `< 0.05` with `p`
in `[0.7, 1.3]`; and `H-IFACE`: spread `> 0.15` with `p` in `[0.25, 0.65]` and the
housing quantity **lower**. Measured: spread `0.0059` — an order of magnitude
inside `H-MESH`'s bound and a factor of 25 below `H-IFACE`'s floor; both `p`
values inside `[0.7, 1.3]`; and the housing quantity `Q1` is **higher**, not
lower. On T23G the spread was `0.0027`, already recorded before this run as a
point against `H-IFACE`. **This is a second, independent point against `H-IFACE`,
recorded on a rung whose overall verdict is `NOT A RESULT`** — and it is
therefore an observation, not a settled discrimination.

---

## 8. WHAT THIS RUNG ESTABLISHED, DESPITE THE VERDICT

The verdict is `NOT A RESULT` and stays that way. A `NOT A RESULT` still buys
knowledge, and this one bought four things:

1. **The L-514 linear-solver repair is measured, not argued.** `p_rgh` `tolerance
   1e-09` + `relTol 0.01` + `maxIter 100` clears the **unchanged** `G-CONV` gate
   on all three levels (§3). T23G2R failed that gate; T23G2Rn's `relTol 0`
   over-correction was stopped on cost. The repair is now demonstrated on a
   completed three-level ladder rather than projected.
2. **The cost model built on the T23G2Rn measurement held.** Predicted uplift
   `[1.5, 2.2]×` the T23G2R per-iteration cost; measured **`1.79×`** campaign-wide
   (§10). That closes the loop the T23G2Rn calibration row explicitly opened.
3. **The ladder is `CONVERGING`, and that is new.** Five graded quantities, all
   `CONVERGING` at `dim = 2` with `r21 = r32 = 1.5000` exactly, orders clustered
   in `[0.9906, 0.9976]`. Prediction **P-TRIP** — that fixing `G-CONV` makes the
   triple gradeable — **held**. The triple that T23G2R could not form exists.
4. **A defect in `G-RATIO`'s own arithmetic is now measured and named.** An
   exactly-zero denominator makes the gate return `inf` without ever consulting
   its numerator. The gate cannot distinguish a ladder whose iterative error is
   genuinely negligible from one whose iterative-change *reader* returns a
   structural zero. The comparator refused rather than banking the free `PASS`,
   and it did so with twenty passing planted controls proving the readers are not
   blind (§5) — so the defect is located precisely in the gate, not in the
   instrument around it.

---

## 9. THE REGISTERED PREDICTIONS — WHAT HELD AND WHAT LOST

| id | prediction (`T23G2Rn2_PREREGISTRATION.md` §4) | outcome |
|---|---|---|
| **P-CONV** | `p_rgh` outer residual descends below 1e-8 on all three levels → `G-CONV` PASS | **HELD** — `G-CONV: PASS`, all three levels CONVERGED (§3) |
| **P-COST** | completes at ~1.5× (POINT), no more than ~2.2× (CAP) the T23G2R per-iteration cost, **not** 13–15× | **HELD** — measured **1.79×** campaign, inside the band; no level capped (§10) |
| **P-TRIP** | with all levels converged the Roache triple becomes gradeable; `G-RATIO`/`G-ORDER` become live cells | **HELD IN PART** — the triple is gradeable and `CONVERGING`, `G-ORDER` went live and PASSED; **`G-RATIO` went live and returned `NOT A RESULT`**. The registration's own loss mode is explicit that making the triple gradeable is not making it pass |
| **P-YM** | a linear-solver-settings edit cannot move y+ or the mesh → `G-YPLUS` PASS, `G-MESHSIM` PASS | **HELD** — both PASS (§2, §4) |
| **P4** (`Q5`) | `Q5` reads DIVERGENT or STAGNANT; a CONVERGING reading in [1.5,2.5] would mean P4 LOST | **HELD** — `Q5` DIVERGENT, order `-1.8767` (§6) |

**No prediction was lost.** The rung is `NOT A RESULT` on a gate whose registered
loss mode P-TRIP anticipated in writing, and on the specific branch of it — a
gate going live and refusing — that the registration named in advance.

---

## 10. COST CALIBRATION — RULE 12

Actuals are the wrapper-captured `core_min` in each level's `STATUS` file
(`verification/runs/T-family/T23G2Rn2_runs/T23G2Rn2_L{1,2,3}/STATUS.T23G2Rn2_L*`),
`ranks = 1`. POINT and CAP are the frozen §6 figures.

| level | POINT | **actual** | CAP | actual/POINT | `capped` | `rc` |
|---|---:|---:|---:|---:|---:|---:|
| `T23G2Rn2_L1` | 39.11 | **50.8167** | 57.35 | **1.299** | 0 | 0 |
| `T23G2Rn2_L2` | 226.80 | **261.5000** | 332.64 | **1.153** | 0 | 0 |
| `T23G2Rn2_L3` | 906.12 | **1087.3000** | 1328.98 | **1.200** | 0 | 0 |
| **CAMPAIGN** | **1172.03** | **1399.6167** | **1718.97** | **1.194** | — | — |

**The ratio actual/predicted is 1.194** against the POINT and **0.814** against
the CAP. **No level was capped**; the frozen §6 cap was neither hit nor
re-budgeted.

**Gap attribution.** Not contention: `ClockTime / ExecutionTime` is
`3049 / 3011.31 = 1.0125` (L1), `15689 / 15603.01 = 1.0055` (L2),
`65235 / 65001.78 = 1.0036` (L3) — at most 1.3 %, from each level's
`log.solve` final line. Not waste: every level ran `rc = 0` to its `endTime`
(`Time = 8000 / 16000 / 28000`, one `End` line each), nothing was discarded and
nothing was re-run. **The residual ~19 % is misprediction in the conservative
direction** — the §6 POINT was set at `×1.5` of the T23G2R actual deliberately
"to hedge", and the measured figure came in above that hedge but well under the
`×2.2` `maxIter`-100 ceiling. **This figure is gross and cleaned alike**: there is
no stall and no discarded work to separate out.

**The calibration figure the predecessor row asked for.** Against T23G2R's
measured per-level actuals (26.07 / 151.20 / 604.08 core-min, campaign 781.35):

| level | uplift vs T23G2R |
|---|---:|
| L1 | **1.949×** |
| L2 | **1.730×** |
| L3 | **1.800×** |
| **CAMPAIGN** | **1.791×** |

**`1.791×` lands inside the `[1.5, 2.2]×` band the §6 model predicted**, which is
precisely the loop `docs/COST_CALIBRATION.md` row
`C-20260909T183500.000000Z-t23g2rn` registered as owed — that row recorded a
**misprediction** of 13–15× against an assumed ×1.15, and the corrected model
built from it is now measured correct to within its own band.

> **`cost_basis`: REPORTED-BY-OWNER, DERIVED, NEVER MEASURED.** Core-minutes are
> the measured unit and come from the per-level `STATUS` files. The rate
> `$0.0513/core-h` is owner-stated (`CLAUDE.md` rule 12), and the box cannot read
> its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar here is
> derived at that rate. Actual **1399.6167 core-min = 23.327 core-h → `$1.20`
> derived**, against the registered POINT `$1.00` and CAP `$1.47`. Under the
> `$25`/run pre-authorisation.

> ~~**OWED:** the rule-12 row for T23G2Rn2 in `docs/COST_CALIBRATION.md` is **not
> yet landed** — `grep 'T23G2Rn2' docs/COST_CALIBRATION.md` returns nothing as of
> this record. The numbers it needs are the table above.~~
>
> **STRUCK 2026-09-12 — THIS WAS FALSE. The row was already landed on 2026-09-10.**
> See **§14**. The row is `C-20260910T160352.997613Z-3be0aa0e` (commit `b6e95ecc`),
> and every figure in the table above agrees with it to the digit. **Nothing is
> owed and no second row is to be landed** — this ledger is append-only and a
> duplicate is exactly what its id discipline exists to refuse.

---

## 11. THE GRADING-PATH SHA CHAIN — TWO COMMITS, AND WHY THE COMPARATOR'S OWN TABLE READS `DIFFERS`

`T23G2Rn2_RUNG_VERDICT.txt` names `comparator_pin: 2c3f193c…` and `freeze_commit:
9ff29322…`, while the comparator's own `GRADING-PATH SHAS` table prints
`analyse_t23g2rn2.py` as `DIFFERS` (working tree `2c3f193c…` vs frozen
`099aaf55…`). Both are correct, and the reason is the two-commit freeze:

| commit | time (UTC) | `analyse_t23g2rn2.py` blob |
|---|---|---|
| `9ff29322` FREEZE 1/2 | `2026-09-09T19:04:05Z` | `099aaf554bf7943807e0a4a45aae8e011f94f3b5` (`GRADING_PATH_FREEZE_COMMIT = "PIN-AT-FREEZE"`) |
| `6c29b259` FREEZE 2/2 (pin-set) | `2026-09-09T19:04:32Z` | `2c3f193c1f76aba16c53a2747d8c8baff233056a` |
| **on disk** | — | **`2c3f193c1f76aba16c53a2747d8c8baff233056a`** |

A file cannot contain the sha of the commit that commits it, so the pin is set in
a second commit; the table's "frozen" column is pinned to commit 1/2 and therefore
necessarily differs from the pin-set blob that actually ran. **The file on disk is
byte-identical to the pin-set blob `2c3f193c`, which is the blob the verdict
names.** The other five grading-path files — the pre-registration
(`27e2eef4…`), `t23g_readonly_diagnosis.py` (`73804c02…`),
`mark_done_t23g2rn2.py` (`ee1bc912…`), `mark_done_t23.py` (`982e1db6…`) and
`scripts/roache_triple.py` (`78e56a3b…`) — all read **`IDENTICAL`**.

**The freeze preceded first compute.** Freeze 2/2 committed `19:04:32Z`; the
earliest run artifact,
`verification/runs/T-family/T23G2Rn2_runs/T23G2Rn2_L1/START.T23G2Rn2_L1`, is
stamped `2026-09-09 19:15:25Z` — 11 minutes later. Rule 2 is satisfied on the
ordering.

The stdout's own disclaimer is retained here rather than paraphrased: *"THIS
RECORDER DOES NOT RESTORE THE REGISTERED PROVENANCE AND DOES NOT CLAIM TO"*, and
*"NO GRADED SOLVE WAS EVER PRODUCED UNDER A COMPARATOR CARRYING THIS RECORDER"* —
the `:671` repair-R2 recorder contemplated shas present from the first graded
solve, and only the forward half of that is available.

**Rule-4 completion** was delegated to
`verification/runs/T-family/T23_runs/mark_done_t23g2rn2.py` and called: `DONE` on
`T23G2Rn2_L1`, `L2` and `L3`, each with `rc_source = READ-FROM-STATUS`.

---

## 12. WHAT THIS RUNG DOES NOT LICENSE

- **No temperature claim.** `Q1 = 51.9184 K`, `Q2 = 50.1037 K`, `Q3 = 56.0211 K`,
  `Q4 = 52.5146 K`, `Q6 = 50.1664 K` (ΔT above 288.0 K) are recorded values whose
  gate cells are `NOT A RESULT`. None may be quoted as a graded result, in the
  sixteen-point map, in Act A, or anywhere else.
- **No grid-convergence claim, and no GCI quotation as a certified uncertainty.**
  The triples are `CONVERGING` and the GCIs were computed by the frozen
  comparator, but the rung's verdict is `NOT A RESULT`; the GCIs are reported
  here because the comparator reported them, not because they are awarded.
- ~~**No `Q3` band conclusion.** The `0.0211 K` exceedance is an observation. It
  is not a `GATE FAIL` this rung is entitled to declare, because `G-RATIO` voided
  the cell first.~~ **STRUCK 2026-09-12 — SUPERSEDED BY A SUPERVISOR'S RULING
  ALREADY ON THE RECORD.** The heat-transfer supervisor ruled on 2026-09-10, in
  `docs/COST_CALIBRATION.md` row `C-20260910T160352.997613Z-3be0aa0e`, that
  **`Q3` = 56.0211 K against the registered [46.0, 56.0] K is `GATE FAIL` AND IT
  STANDS**, expressly declining to let either the 51×-larger GCI or the in-band
  Richardson value `55.157948` rescue it. See §14.2. This lane does not re-open a
  supervisor's ruling.
- **No settled `H-MESH` / `H-IFACE` discrimination.** `A2.1`'s spread of `0.0059`
  is a second point against `H-IFACE`, on a rung that is `NOT A RESULT`.
- **No Richardson extrapolate claim.** The extrapolates the comparator printed
  (`51.650186`, `51.050804`, `49.235378`, `55.157948`, `49.29842`) are **REPORTED
  AND NEVER GATED ON**, at any level, for any quantity — the registration says so
  and this record repeats it.
- **No retirement of `G-RATIO`.** `RATIO_MIN = 10` is untouched and the gate
  stays registered on every graded quantity. Nothing here is a petition to
  relax it.

---

## 13. WHAT WOULD TURN THIS INTO A RESULT

The rung's only failing cell is `G-RATIO`, and it fails on a **degenerate
arithmetic path**, not on a measured shortfall. Two candidate routes, neither of
which this record chooses — the choice is the supervisor's, and either needs its
own frozen registration before any compute:

1. ~~**An iterative-change reader with resolution below the plateau.** The finest
   iterative change is `0.000000e+00` because the quantity is written at a
   precision at which consecutive plateau samples are bit-identical. A reader
   that resolves the sub-print-precision iterative change would give `G-RATIO` a
   real denominator…~~ **STRUCK 2026-09-12 — THIS WAS A GUESS, AND THE MEASURED
   CAUSE IS DIFFERENT.** It is not a print-precision limit. See §14.3: the
   supervisor measured the mechanism at source on 2026-09-10 — the `h` linear
   solver runs at `No Iterations 0` because its `tolerance 1e-09` collides with
   `G-CONV`'s own `1e-9` criterion on `h`, so `h` is never updated and `T` is
   **bit-identical between writes**. A finer reader would read the same zero. The
   repair is to separate the solver tolerance from the gate criterion, and that
   is a registration change, not a reader change.
2. **A registered zero-branch disposition for `G-RATIO`.** The gate currently has
   no licensed answer for an exactly-zero denominator, so the comparator refuses.
   A successor could register, prediction-first, what an exact zero means — but
   that is a change to a registered gate and is therefore **reserved**: it is not
   a repair a lane or a successor comparator may make on its own reading.

Neither route may touch the `T23G2Rn2` record. Rule 2 closed this arm's gates at
first compute on `2026-09-09T19:15:25Z`.

---

*Recorded by a heat-transfer `lab-lane`, 2026-09-12, from the artifacts on disk.
**Zero solver core-minutes were spent producing this record** — the rung was
graded on 2026-09-10 by the detached autograder `autograde_t23g2rn2.sh` (pid
767940) and this file transcribes that grading. No verdict was re-derived, no gate
was re-evaluated, and the comparator was not re-run.*

---

## ⚠ 14. CORRECTION, 2026-09-12 — THREE THINGS THIS RECORD GOT WRONG ON THE DAY IT WAS WRITTEN, AND THE SUPERVISOR'S RULINGS THAT ALREADY SETTLED TWO OF THEM

*Appended the same day the record was written, on discovering that a
`COST_CALIBRATION` row for this rung had existed since 2026-09-10 and carried
material this record contradicted. Nothing above §14 was deleted; the three
affected passages are struck in place and point here. **No verdict changes: the
rung is `NOT A RESULT` and every measured figure in §1–§11 stands unaltered and
agrees with the supervisor's row to the digit.***

### 14.1 THE RULE-12 ROW WAS NEVER OWED — IT WAS LANDED TWO DAYS BEFORE THIS RECORD

**`docs/COST_CALIBRATION.md` row `C-20260910T160352.997613Z-3be0aa0e`**, dated
2026-09-10, team heat-transfer, landed at commit **`b6e95ecc`**. §10's `OWED`
paragraph is struck.

Every figure §10 computed independently agrees with that row exactly: actual
**1399.6167 core-min** (`50.8167 / 261.5000 / 1087.3000`), POINT `1172.03`, CAP
`1718.97`, ratio **1.194** against POINT and **0.814** against CAP, per-level
`1.2993 / 1.1530 / 1.1999`, campaign uplift **×1.7912** against T23G2R inside the
registered `[1.5, 2.2]×` band, contention ruled out by measurement, waste
**0.00 core-min**. The agreement is the useful part: two independent passes over
the same `STATUS` files produced the same numbers.

**How the error was made, stated plainly because the mechanism will repeat.** The
check that produced `OWED` was `grep 'T23G2Rn2' docs/COST_CALIBRATION.md`. It
**did** match — twice — but the command's output exceeded the display limit, was
truncated to a preview, and the preview showed only the first match (the
predecessor T23G2Rn row at `:490`, which mentions `T23G2Rn2` in its own prose).
The second match, the actual row at `:513`, was never on screen. **A truncated
preview was read as a complete result.** Two independent guards would each have
caught it: reading the match *count* rather than the first page, and asking the
committed blob (`git show HEAD:docs/COST_CALIBRATION.md`) rather than the
worktree copy, which this ledger's own header says diverges from HEAD by design.

**Consequence: no second row is to be landed.** The ledger is append-only and its
id discipline exists precisely to make a duplicate refusable.

### 14.2 THE `Q3` BAND — THE SUPERVISOR RULED IT `GATE FAIL` AND IT STANDS

§12 said this rung was not entitled to a `Q3` band conclusion. That was already
superseded. The supervisor's ruling, made in the row above on 2026-09-10 and
quoted from it:

> *"`Q3` = 56.0211 K against the registered [46.0, 56.0] K is `GATE FAIL` AND IT
> STANDS."*

The ruling expressly considers and rejects both escapes this record raised: the
miss of `0.0211 K` = `0.0377 %` is ~51× smaller than the row's own GCI
(`1.9260 % = 1.07897` absolute), and the Richardson value `55.157948` **is**
inside the band — and neither rescues it, because
`T23G2_PREREGISTRATION.md:460-465` freezes *"Grade the FINE value. The Richardson
extrapolate is REPORTED beside the fine value and is NEVER GATED ON"*. Reaching
for the in-band extrapolate after seeing the answer is choosing the graded value
to fit it. The band's width relative to this ladder's GCI is a design question
for a successor's pre-registration, **not a licence to move a frozen threshold**.

§12's struck bullet is replaced by this ruling. The **rung** verdict is unchanged
and remains `NOT A RESULT`.

### 14.3 THE EXACT-ZERO DENOMINATOR IS STRUCTURAL, AND THE MEASURED CAUSE IS NOT THE ONE §13 GUESSED

§13 guessed that the `0.000000e+00` iterative change was a print-precision
artefact. It is not, and the real mechanism — measured at source by the
supervisor and recorded in the same row — is both simpler and worse:

`T23G2Rn2_L*/system/fluid/fvSolution` sets `"(U|h|k|omega)"` `tolerance 1e-09`,
and **`G-CONV`'s criterion for `h` is also `1e-9`** (Sanaa's tightened criterion;
the rest of `G-CONV` is `1e-8`). The final step of every level shows `h`, `k` and
`omega` at **`No Iterations 0`** with initial == final residual
**`9.48179125592e-10` (L1) / `9.78783688541e-10` (L2) / `9.98660613323e-10`
(L3)** — **94.8 %, 97.9 % and 99.87 % of the criterion, tightening with
refinement.** The solver declines to iterate because the initial residual is
already under its tolerance; `h` is therefore never updated; `T` is
**bit-identical between writes**; and `G-RATIO`'s denominator is exactly `0.0`.

A finer reader would read the same zero, so §13's route 1 is struck. Two further
consequences the supervisor drew, recorded here because they bear on any
successor:

- **The collapse is of one limb, not the gate.** `G-CONV`'s `p_rgh` limb keeps a
  full decade of margin (solver tolerance `1e-9` against a `1e-8` gate) and is
  genuinely `maxIter`-bound, so its residual is physical.
- **A gate criterion set EQUAL to the linear-solver tolerance certifies the
  solver's own stopping decision** and cannot distinguish *converged* from
  *declined to iterate*. At L3's 0.13 % margin the limb is **nearly-vacuous
  rather than safely vacuous**, and a fourth level would plausibly not pass it.

**Therefore §13's remaining route is the operative one, and it is a registration
change**: a successor must separate the solver tolerance from the gate criterion,
or register a different iterative-error instrument, **before freezing**. That is
not a lane's call and none was made here.

### 14.4 ONE CALIBRATION ITEM §10 MISSED ENTIRELY

The supervisor's row names, separately and without laundering it into the ratio,
**784.50 core-min of post-plateau compute = 56.3 % of the campaign's
`ExecutionTime`**: all six graded quantities go bit-constant at 12–13 significant
digits well before `endTime` on every level (L1 at iteration 3,000 of 8,000; L2
at 6,000 of 16,000; L3 at 12,400 of 28,000). **This is not waste** — `endTime`
was frozen pre-compute and running to it is compliance — but it is the largest
calibration item the rung produced, and §10 did not surface it. The lesson the
row draws: register `endTime` against a **measured** plateau iteration from a
pilot.

*Correction appended by a heat-transfer `lab-lane`, 2026-09-12. Zero solver
core-minutes; no artifact re-read produced a different number, and no gate,
threshold, band, cap or label was touched.*
