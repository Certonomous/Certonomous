# SPEC — two admissibility clauses for `scripts/roache_triple.py`

**STATUS: SPEC. NOT ADOPTED. NOT A STANDARD. NOTHING HERE BINDS ANYBODY, AND NO
INSTRUMENT IS CHANGED BY THIS FILE.** Written by verification-supervisor
2026-08-27 on the chief's referral of a cfd lane's F26 finding. It sits in
`docs/standards/` beside real standards and **is not one**, on the precedent of
`docs/standards/SWEEP_PRECONDITION_PROPOSAL.md`. **Clause A is reserved to Sanaa
and is NOT taken (§4). Nothing is sent anywhere (`CLAUDE.md` rule 7).**

---

## 1. THE FINDING, RE-MEASURED BEFORE BEING ACCEPTED

Referred: F26's converged cell counts **294 / 384 / 486** pass
`scripts/roache_triple.py` at `dim = 2` and return `CONVERGING`; the human
downgrade to `NOT A RESULT` was correct and the instrument would not have made
it.

**Confirmed at source by this supervisor:**

- The ratios are `r21 = sqrt(384/294) = 1.1429`, `r32 = sqrt(486/384) = 1.1250`.
- **The module's ONLY ratio refusal is `r <= 1.0`** — `scripts/roache_triple.py:251`
  (equal path) and `:296-298` (unequal path, *"the ladder does not refine"*).
  Between `1.0` and `1.3` there is nothing.
- The `CONVERGING` branch at `:334-338` is reached whenever `p >= STAGNANT_FLOOR`
  (`0.5`), with `P_MIN = 0.05` catching only `DEGENERATE`. **No refinement-ratio
  test stands between a 1.125 ladder and a quoted GCI.**
- **No minimum-`r` clause exists in `VERIFICATION_CHARTER.md`,
  `docs/standards/MESH_STANDARD.md` or `docs/MESH_STANDARD.md`** — searched with
  a control that fired (`CONVERGING` returns 2 in `MESH_STANDARD.md`); every
  `1.3` hit in the charter is a version number or an unrelated value. **The
  referral is correct.**

**Why small `r` is not merely imprecise but meaningless.** The observed order is
`p = ln|e32/e21| / ln r`. The denominator carries the whole sensitivity:
`ln(1.125) = 0.1178` against `ln(1.3) = 0.2624`. **The same relative noise in the
error ratio produces 2.23x the error in `p` at `r = 1.125`.** Roache's `r >= 1.3`
is the conventional floor; **the ground for a floor is this amplification, not
the citation**, and a spec should say so, because the citation is a convention
and the amplification is a fact.

## 2. CLAUSE A (PROPOSED, NOT ADOPTED) — a minimum refinement ratio

> A triple whose refinement ratio is below the registered floor is
> **`NOT A RESULT`**, whatever its observed order, with `r21`, `r32` and the
> floor printed beside it and **no GCI quoted**. The floor is a registered
> constant; `r >= 1.3` is the proposed value on Roache's convention.

**It must be a `NOT A RESULT` and not a refusal (exit 2).** A refusal says the
instrument could not read the case; this instrument read it perfectly. **The
ladder is the defect, and a defective ladder is a rung-level finding the record
should carry** — exactly as `DIVERGENT` and `STAGNANT` are.

## 3. CLAUSE B (PROPOSED) — an exact-solution error norm that extrapolates to non-zero

**This is the stronger of the two and the referral is right about that.**

> Where a registration declares a quantity to be **an error norm against an
> EXACT or MANUFACTURED solution**, its Richardson extrapolate must be
> indistinguishable from **zero**. If it is not, the triple is
> **`NOT A RESULT` — a SATURATION, not a Richardson result** — with the
> extrapolate and the band printed.

**The ground is a self-contradiction, not a tolerance.** An error against an
exact solution is **zero in the limit by construction**. A family whose error
extrapolates to `9.1e-02` (as reported; **this supervisor did not re-measure
F26's norms**) is converging — to something that is not the exact solution. **A
`CONVERGING` state and an observed order on that sequence describe the rate at
which the scheme approaches its own floor.** That is a real and interesting
number and it is **not** a discretisation order.

**AND IT INTRODUCES NO NEW CONSTANT, which is why it is separable from clause A.**
*"Indistinguishable from zero"* is read against **the instrument's own already-
computed `GCI_abs`** — if `|richardson| > GCI_abs`, the extrapolate is outside
the uncertainty the instrument itself claims for the row. **No threshold is
invented; the existing uncertainty estimate is turned on the extrapolate.**

**SCOPE LIMIT, stated so the clause cannot be over-applied: it binds ONLY where
the reference is EXACT or MANUFACTURED.** Against an experiment or a
correlation, a **non-zero limit is expected** — it is model-form error, and
refusing it would void most of this lab's validation work. **The registration
must therefore DECLARE the reference class; an undeclared reference class is
treated as non-exact, and clause B does not fire.**

**The lab has already ruled this way once, by hand, and never encoded it:** cfd's
**F20** was downgraded to `CAN DO, CAVEATS` on *"Richardson extrapolate
1.1125e-03 != 0 against an exact reference — converges to a non-zero floor"*
(audited at `ca6a3164`). **That is the third instance today of a rule applied by
hand over an instrument's output and never put into the instrument** — after
T1b's rule-5 limb (2) and the `analyse_t1b_L4` selftest. **The pattern, not the
case, is the finding.**

## 4. ⚠ THE CONSTRAINT THE REFERRAL DID NOT RAISE — 36 FROZEN IMPORTERS, 9 OF THEM FIRED

Measured here, and it changes how this must land:

| quantity | value |
|---|---|
| files **mentioning** `roache_triple` | 183 |
| files with a real **import** | **36** |
| of those, **tracked at HEAD** (frozen) | **36 of 36** |
| grader directories carrying a `gate_*.json` or `RESULTS*.md` (have **fired**) | **9** |

**Changing `gci()` / `gci_unequal()` in place retroactively changes the behaviour
of thirty-six frozen comparators, nine of which have already produced verdicts.**
A freeze whose meaning can be altered by editing a module it imports is not a
freeze. **The referral described a verdict-equality sweep; it did not name this
as a §2d boundary event, and it is one.**

**What makes it survivable, and it is the same argument this team used on T1b:**
standing rule 5's gate is **ONE-WAY** — it may turn a `PASS` or a `GATE FAIL`
**into** a `NOT A RESULT` and never the reverse. **Both clauses move only in that
direction**, so no frozen row can be *rescued* by them and none can be made more
favourable. **That is what makes the change admissible; it is not what makes it
free.**

**THE LANDING CONDITIONS, and they are not negotiable downward:**

1. **Pre-registered before the module is touched** — the sweep's expected output
   registered in advance, so "which rows flipped" cannot be chosen after seeing
   them.
2. **Every flipped row is re-recorded as a dated amendment to ITS OWN record, by
   ITS OWNING TEAM.** A module bump must not silently restate nine teams' rows.
   **A verdict that changes without its record changing is the defect this lab
   keeps finding.**
3. **The flipped list is published in full, including the count that is
   embarrassing.** If clause A flips a row this lab has cited as a credential,
   that is the finding.
4. **Clause A is NOT ADOPTED BY THIS TEAM.** A minimum refinement ratio is a
   **new gate threshold**, and `r >= 1.3` appears nowhere in `CLAUDE.md`.
   **Adding a gate threshold is reserved to Sanaa exactly as retiring one is**
   (this team's own D539). **Clause B is the closer call** — it introduces no
   constant and reads as an encoding gap rather than a new gate — **but it flips
   frozen rows, so it goes to her with clause A rather than being taken alone.**
   **Recommended to her, through the chief. Not taken.**

## 5. THE PLANTED FAILURE — required, and this is v1.13's first live test

`VERIFICATION_CHARTER` **v1.13** (landed 2026-08-27, ~90 minutes before this
spec) requires that any amendment to an instrument carrying a measured rate
re-measure it from committed blobs over the same frozen sample in one process,
**with a harness that carries a planted control proving the reported rows can
MOVE**. **This amendment is the first thing to arrive after that clause, and it
is squarely inside it.**

The module already has the machinery: `PLANT = 1.234e-03`, `plant_into_T()` and a
`--selftest` that imports both parents and cross-checks against them.

**Required controls, each of which must FIRE before the clause is believed:**

| # | control | must |
|---|---|---|
| A+ | the F26 triple `294/384/486` at `dim 2` | return **`NOT A RESULT`** under clause A, and `CONVERGING` under the pre-amendment blob — **the same three numbers through both blobs, in one process** |
| A− | a triple identical in every way but built at `r = 1.5` | **still `CONVERGING`** — proves the clause discriminates on `r` and not on the data |
| A0 | a triple at `r` exactly at the floor | returns the **registered** side of the boundary, stated in advance |
| B+ | a synthetic exact-solution error family extrapolating to a known non-zero | **`NOT A RESULT`**, saturation named |
| B− | a synthetic family extrapolating to zero within `GCI_abs` | **still `CONVERGING`** |
| B∅ | the same non-zero-extrapolating family with the reference declared **non-exact** | **`CONVERGING`** — proves the scope limit in §3 is real and not decorative |
| S | the verdict-equality sweep harness itself | a **deliberate mutation** of the amended module must **move the reported rows** (v1.13 §3) — *a harness that has not been shown able to report a change has not measured that nothing changed* |

**Control B∅ is the one most likely to be skipped and the one that matters most**:
without it, clause B is indistinguishable from a clause that voids every
validation row in the lab.

## 6. WHAT THIS SPEC DOES NOT CLAIM

- **F26's error norms were NOT re-measured by this supervisor.** The `9.1e-02`
  extrapolate is **as reported**, and clause B is specified structurally, not
  fitted to it.
- **How many existing rows would flip is `NOT MEASURED`.** No sweep has been run.
  Quoting a number here would be the coverage-as-census defect this team
  published against itself (`L342_GRADER_AUDIT` Addendum 1).
- **Whether `r >= 1.3` is the right floor is not settled here.** The
  amplification argument in §1 justifies *a* floor; it does not pick `1.3` over
  `1.2` or `1.5`. **The value is Sanaa's to set**, and the spec deliberately
  carries the floor as a **registered constant** rather than a literal so that
  setting it is a registration act and not a code edit.
- **Nothing here changes `scripts/roache_triple.py`.** The file is untouched.
