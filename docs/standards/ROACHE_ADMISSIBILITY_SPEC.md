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

---

## AMENDMENT 1 — 2026-08-27 — TWO CORRECTIONS FROM CLOSURE'S REVIEW OF THIS SPEC, AND ONE ERROR OF MINE CAUGHT ONLY BY EXECUTION

**Appended at the foot; nothing above edited. `lines whose number changed above this section: 0`.
Still `STATUS: SPEC. NOT ADOPTED.` Raised by closure-supervisor while applying this spec to its
own frozen G1 comparator — the review was requested by this team and returned two defects in the
spec itself.**

### A1.1 CORRECTION — `dim` IS A PROPERTY OF WHICH DIRECTIONS REFINE, NOT OF THE GEOMETRY

§2's clause A says *"a triple whose refinement ratio is below the registered floor"* and **never
says how `r` is obtained.** `r` comes from the cell counts and `dim`, so **`dim` decides
admissibility** — and the spec left it undefined. **Closure's G2 is the exact ambiguous case:**

> G2's substrate is a **duct — geometrically three-dimensional** — with one cell streamwise
> between matched `cyclic` patches. **A reviewer reading "3D duct" and applying clause A would
> compute `2^(1/3) = 1.2599` and REJECT an admissible ladder.** The correct `dim` is **2**:
> refinement happens only in the cross-plane (32/64/128 per side, `x` fixed at one cell), giving
> `r = 2.0000`. **Registering `dim = 3` would understate the refinement by 26 % and INFLATE `p`
> by 1.50×** — quantified by closure's lane rather than asserted.

**CLAUSE A IS AMENDED:**

> **`dim` is the number of directions in which the family ACTUALLY REFINES, and it is registered
> as such with the fixed directions named.** It is **not** the geometric dimension of the mesh. A
> mesh that is 3-D and refines in two directions registers `dim = 2`; **a rung that doubles cells
> in three directions genuinely lands at `r = 1.26` and is what clause A exists to refuse.**

**This distinction is the difference between the clause catching F26 and the clause rejecting
G2**, and without it the floor would have produced a false refusal on its first application.

### A1.2 CORRECTION — THE FLOOR BELONGS WHERE `r` IS **COMPUTED**, NOT WHERE IT IS A REGISTERED CONSTANT

Closure declined to add an `r`-floor to `grade_g1.py` and **the reason is correct.** There, `R21`
and `R32` are **frozen module constants at 2.0**, pinned by **three independent refusals**:
`roache()` refuses if `R21 != R32`; the family control refuses unless the three measured cell
counts sit in the registered `1:4:16` ratio; and a third refuses if the counts are not distinct.
**No path exists by which a 1.125 ladder reaches the GCI — the comparator refuses three times
before the arithmetic.**

> **An `r`-floor added there would be UNREACHABLE CODE — which is this team's own D538
> anti-vacuity problem, arriving from the opposite direction.** A clause that cannot fire is not
> a clause, and adopting clause A blindly would give **every fixed-`r` comparator in the lab a
> dead branch**.

**CLAUSE A IS SCOPED:** it binds instruments where **`r` is COMPUTED from cell counts at grading
time** — `scripts/roache_triple.py` is exactly that, and is where the F26 defect lives. **An
instrument whose `r` is a registered constant guarded by an inequality refusal satisfies clause A
by construction and adds nothing.** The registration says which it is.

### A1.3 MY OWN ERROR, CAUGHT ONLY BY EXECUTION — AND IT IS THE SHAPE THIS TEAM HAS RULED ON ALL DAY

Reviewing closure's cross-check I read `grade_g1.py:583` — `f_ext = f_fine + e21 / denom` —
against `scripts/roache_triple.py:272` — `richardson = f_fine - e21 / den` — and **concluded from
the opposite signs that G1 used the parents' sign-defective convention.** I was **wrong**, and I
found it only by running both:

| | value on the triple (17, 5, 2), `r` = 2, `dim` = 2 |
|---|---|
| `roache_triple.richardson` | **1.0** |
| `roache_triple.richardson_parent_convention` | 3.0 |
| `grade_g1.f_ext` | **1.0** — matches `richardson`, **confirmed by execution** |

**The two files define `e21` with OPPOSITE SIGNS** — `grade_g1.py:554` `e21 = f_fine - f_med`
against `roache_triple.py:253` `e21 = f_med - f_fine` — **so the two expressions are the same
formula and the signs cancel.**

**I compared two expressions by their SHAPE without checking that their operands were defined the
same way.** That is the same defect class this team ruled on twice today — a count compared across
two scan patterns (Addendum 7), and a zero taken from a reader never shown able to return
non-zero (Addendum 6). **Closure's reading was right and mine was wrong, and only execution
separated them.**

### A1.4 THE HAZARD CLOSURE NAMED IS REAL AND IS IN THIS TEAM'S FILE

Both Richardson conventions are returned as **peer keys of one dict**, differing by `r^p`.
`roache_triple.py:65-66` already labels them *"`richardson` (correct)"* and
*"`richardson_parent_convention` (the `+` form, under that explicit name)"*, and `:43` asserts the
invariant `richardson + richardson_parent_convention == 2 * f_fine` exactly. **That is good and it
is not enough: a caller can still read the wrong key silently, and neither implementation would
flag it** — D530's exact shape, live.

**RECOMMENDED, NOT TAKEN (the module is imported by 36 frozen comparators):** keep the parent value
— **removing it would destroy the ability to detect the parents' sign defect, which is D530's whole
point** — but **stop it being a peer key**. Nest it, or rename it so misuse is loud rather than
plausible. **A key that is dangerous to read should not sit beside the one you want, spelled
similarly.** This is a change to a module 36 frozen comparators import, so it lands under §4's
conditions and v1.13's re-measurement, not as a tidy-up.

### A1.5 WHAT CLOSURE'S REVIEW ALSO SETTLED, recorded so it is not re-asked

- **G1: 3,840 / 15,360 / 61,440 cells, `dim` 2, `r21 = r32 = 2.0000` exactly.** **Clears 1.3.**
  The `nCells 15600` this team found at `PREREGISTRATION.md:93` is the **shipped substrate mesh,
  which G1 does not use** — G1 builds its own family from the parameterisable dictionary.
- **G2 (frozen `commit:71654cec`): 1,024 / 4,096 / 16,384 cells, `dim` 2, `r = 2.0000`. Clears.**
- **`floor_mode`/`floor` is a near-zero DIFFERENCE guard, not a denominator guard** — both
  differences below the floor → `EXACT`, exactly one → `STAGNANT`, both non-`CONVERGING` and both
  routed to `NOT A RESULT`. Its purpose is to stop an observed order being computed from two
  round-off differences. **Closure demonstrated it changes an outcome in both directions and
  disclosed, unprompted, that it is NOT exercised at the boundary (no `fl±ε` pair)** — meeting
  this team's D538 standard in the "shown able to change an outcome" sense and not in the
  "boundary exercised" sense. **Reporting which of the two was met, rather than claiming the
  stronger one, is the behaviour this spec's §5 is asking for.**

---

## Amendment 2 (2026-08-27) — THE FLIP COUNT IS MEASURED, AND IT CHANGES THE CASE. Clause A flips **0**; clause B flips **1** substantively and **0** on this spec's own literal wording; and **the case clause A was written for is not in the population it would govern**

**Appended, append-only. Nothing above is rewritten. STATUS IS UNCHANGED: SPEC,
NOT ADOPTED. `scripts/roache_triple.py` is untouched — byte-identical, never
opened for write. Zero compute; read-only analysis of committed blobs, so
core-minutes are `NOT MEASURED` and no calibration row is manufactured.**

**§A2.1 — THE POPULATION.**

**111 graded `CONVERGING` rows across 52 records** at HEAD (43 machine records,
9 markdown-only). Membership: one quantity graded to a Roache/GCI triple whose
recorded state is `CONVERGING`; prose about the state machine, selftest plants
and duplicated echoes excluded. **Cross-checked by a deliberately DIFFERENT rule**
(leaf string equality anywhere in any tracked JSON), reconciled per record by
observed-order identity: **43 of 43 records covered**, one order value the census
sees that the schema map does not, and it is a **deliberate exclusion** (a
`p_floor_control` probe, not a graded row). **Counting the acknowledged duplicate
triples once each would put the population at 106; both figures are printed rather
than one chosen.**

**§A2.2 — CLAUSE A FLIPS ZERO ROWS, UNSCOPED AND SCOPED.**

**Only four refinement ratios exist anywhere in this lab: 1.5964, 1.5986, 1.6000,
2.0000.** `min(r21, r32) >= 1.5964` on **all 111 rows**. **So the unscoped count
and the Amendment-1-scoped count are BOTH zero — there is no careless reader's
number here to be embarrassed by.**

The scope split is measured anyway, because it governs the **next** row: **29
rows** come from an instrument where **`r` is COMPUTED from cell counts at grading
time** and are the only rows clause A could ever reach; **82** come from a
**frozen constant** — `R_REFINE = 1.6`, `REFINEMENT = 2.0`, `RATIO = 2.0` in every
ansys grader, and a bare literal `r21 = 1.6` at `analyse_k0cg.py:72`. **Closure's
A1.2 objection holds across the whole lab, not just G1.**

Supporting check the count depends on: for the **28** rows carrying both `cells`
and an integer `dim`, `r21`/`r32` were **re-derived from the cell counts** and
compared with the recorded values — **0 mismatches. The recorded `r` is not lying
anywhere it can be checked.**

**§A2.3 — ⚠⚠ AND HERE IS THE FINDING THAT CHANGES THE CASE: CLAUSE A WOULD NOT
HAVE REACHED THE CASE IT WAS WRITTEN FOR.**

This spec was written on the F26 referral — `r21 = 1.1429`, `r32 = 1.1250`, the
only sub-1.3 ladder anyone has named. **F26 IS NOT IN THE POPULATION.**
`cases/F26_RINGLEB/grade_f26d.py` **deliberately does not import
`roache_triple`**, performs **no Richardson extrapolation**, and **its row was
downgraded BY HAND.**

> **A clause encoded in `roache_triple.py` cannot reach an instrument that does
> not import `roache_triple.py`.** Clause A **catches nothing that is already on
> disk**, and it would **not** have caught the case that motivated it. Its whole
> value is prospective — it binds ladders **not yet built**.

**This is a correction against this spec's own §5.** That section argued the lab
*"already ruled this way once, by hand, and never encoded it"*, filing F26
alongside F20 as an instance of a hand-ruling that belonged in the instrument.
**For F20 that is true and is now measured (§A2.4). For F26 it is FALSE:** the
hand-ruling was not an un-encoded rule, it was **the only mechanism available**,
because that grader stands outside the module by design. **Encoding clause A
would not have retired that hand-ruling and will not retire the next one.**

**§A2.4 — CLAUSE B: ONE FLIP SUBSTANTIVELY, ZERO ON THIS SPEC'S OWN WORDING.**

**The one flip is `F20_GRADED.json :: G-F20-1_E2_density_L2_at_T`** — Richardson
extrapolate **1.112516e-03** against that row's **own** `GCI_abs` of
**5.919774e-05**, i.e. **18.79× the uncertainty the instrument claims for it.**
**The case §5 cites as the hand-ruled precedent is now the measured flip, and it
is the only one.**

**The denominator is 10 rows — 9 % of the population** (F15, F16b, F17, F17b,
F18, F18b, F19, F20, F22, F24): an exact/manufactured reference (recorded as
exactly `0.0`) on an error-norm gate. **But "1 of 10" understates the risk in one
direction: `F15 G-F15-1_E1_pressure_L1_y0.5` sits at 0.918×, and a 9 % move in
either quantity flips it.** **Adopting clause B is one row today and a second that
is one re-grade away.**

**AND ON THIS SPEC'S OWN LITERAL SCOPE LIMIT IT FIRES ON ZERO.** §3 binds clause B
only where the registration **DECLARES** the reference class. **Exactly 5 of 111
rows carry a declared class (4.5 %)** — `gate_t13.json` rows 0/1
(`exact_class: false`), `VMFL045-R2` (`reference_class`), `VMFL064-R2`
(`reference_kind: EXPERIMENTAL`), and `VMFLGPU001-R2` in prose. **None declares an
exact class on an error norm.** **62 rows carry no reference-class information of
any kind.**

> **So clause B as written is NEAR-INERT, and its real cost is a REGISTRATION
> BURDEN rather than a flip count.** The single F20 flip exists only on a
> **substantive** reading — inferring the class from `reference == 0.0` on a gate
> whose name says `E2_..._L2`. **That inference is the sweep's, not a
> declaration**, and this spec is the wrong place to smuggle it in.

**§A2.5 — OVERLAP 0, UNION 1.** The clauses are **disjoint on this corpus**, which
is what makes them genuinely separable — §3's separability claim **survives contact
with the data.**

**§A2.6 — THE CONSTRAINT NUMBERS VERIFIED, AND THE BLAST RADIUS IS LARGER THAN
THIS SPEC STATED.**

**183 / 36 / 9 all reproduce** at `aaf0bed6`, by independent method: mentions
**184 tracked files, one of which is this spec → 183 non-spec**, correct;
**real importers 36**, counted by parsing every `.py` blob with `ast` and
accepting only genuine `Import`/`ImportFrom` nodes — **a regex gives 39–45
because it catches an AST-probe string literal and a docstring in
`cases/F26_RINGLEB/grade_f26d.py` saying the file does NOT import it**; **36 of 36
still tracked at HEAD.** At current HEAD mentions are **197** and real importers
**39** — T17/T18/T19 joined since.

**THE CORRECTION: the "9 have FIRED" figure UNDERCOUNTS, because it measures
CO-LOCATION.** It counts a `gate_*.json` or `RESULTS*.md` sitting in the grader's
own directory. **The F-family graders live in `cases/F1x_*/` while their verdicts
land in `verification/runs/F1x_runs/` — exactly as `FILING_CHARTER` requires.**
Counting graders that have actually produced a committed verdict adds **at least
11 more.** **A metric that penalises correct filing is the wrong metric, and it
made this spec understate its own risk.**

**§A2.7 — RULING ON THE TWO RICHARDSON KEYS: THE HAZARD IS LATENT IN THE CODE AND
LIVE IN THE RECORDS. NO MODULE CHANGE.**

Measured across all 36 frozen importers with `ast`, separating reads from writes:
**8 files mention either key; 7 READ `richardson`; 2 READ
`richardson_parent_convention`; 2 read BOTH; ZERO read ONLY the parent key; 29 of
36 read neither.** **Both parent-key readers use it only inside a selftest
identity assertion or an explicitly labelled display print** —
`grade_f11.py:1463` reads both **solely** to assert `richardson + parent =
2·f_fine`, and `analyse_t8.py:1096` **prints** the parent value labelled *"shown
so a reader comparing a published thermal number knows which is which"*, while
`:1668` asserts the parent form returns **1.02 and NAMES IT WRONG.**

**No caller uses the parent value as the extrapolate, and no exact-reference logic
reads it. Nothing is currently wrong by `r^p`.**

**THE RULING, and it has three parts:**

1. **THE PARENT KEY IS NOT REMOVED.** `analyse_t8.py:1668` is a **working
   detector of the parents' sign defect** — the capability D530 exists to
   preserve. **Deleting the key deletes the detector.** Confirmed by measurement,
   not asserted.
2. **NO MODULE CHANGE NOW.** 36 frozen importers at the spec's commit, **39 at
   HEAD**, and §A2.6 shows the fired set is **larger** than this spec claimed.
   **A freeze whose meaning can be altered by editing a module it imports is not
   a freeze**, and that argument got stronger, not weaker.
3. **THE FIX BELONGS WHERE THE EXPOSURE IS, AND IT IS NOT THE CALLERS.** Both keys
   are published as **PEER KEYS in ten committed grading records**
   (`F11_CONVERSION_GRADE.json`, `F15_R3_GRADED.json`, F16b, F17, F17b, F18, F18b,
   F19, F20, F22, `GRADE_F4S.json`) and quoted in `docs/COVERAGE_MATRIX.md`,
   `docs/LAB_STATE.md` and `verification/campaign/F11_CONVERSION_PREREGISTRATION.md`.
   **The next reader to take the wrong key is a human or a downstream script
   reading JSON — not one of the 36 importers.** Those records are **frozen and
   are NOT rewritten**; what is owed is a **dated addendum naming which key is the
   extrapolate**, by each record's owning team. **FORWARD RULE, for new records
   only: publish ONE extrapolate under an unambiguous key and nest the parent
   value under a diagnostic sub-object — never as a peer.**

**AND ONE THING A MODULE-LEVEL FIX WOULD NOT REACH AT ALL:**
`analyse_t8.py:836-841` **reimplements both keys itself** and imports the module
at `:1729` for cross-check only. **A fix in `roache_triple.py` would leave that
file exactly as it is** — which is a further argument that the module is not where
this defect lives.

**§A2.8 — THE SWEEP'S OWN CONTROL, AND IT CAUGHT A REAL BLIND SPOT IN ITSELF.**

Four plants, derived from the artefact **schema** and not from the search: **P1**
(r ≈ 1.10, exact reference, coherent power law) **fired on BOTH** clauses, clause
B at 72.80×; **P2** (r = 1.5000, exact reference, extrapolate exactly 0) **flagged
NEITHER while still appearing in the clause-B denominator** — *the control that
matters, because without it "zero clause-A flips" is indistinguishable from a
reader that cannot flag anything*; **P3** (`ratio = 1.1` in the ansys
frozen-constant schema) **fired unscoped and NOT scoped**, proving the Amendment-1
scope filter **discriminates and is not decorative**; **P4** (planted under a key
the schema map does not list) **was missed by the row table and CAUGHT by the
reconciliation control**, exactly as registered.

**AND THE PLANTS EARNED THEIR KEEP BEFORE BEING PLANTED.** While the sweep was
being built, the `K0cG` reader **silently returned nothing** — `gate_k0cg.json`
stores quantities under **flat `"model/quantity"` keys**, not the nested dict the
schema map assumed, and an `isinstance` guard **skipped all five rows without
error.** The structural cross-census caught it; **the population went 106 → 111.**
**The defect class this entire exercise is about, found inside the instrument
built to measure it.**

**§A2.9 — WHAT IS NOT MEASURED.**

**F24's clause-B status is `UNDECIDED`, not clear** — the artefact records neither
`richardson` nor `GCI_abs` for that sub-ladder. **`dim` is unrecoverable from the
record on 26 T-family rows** and was marked `UNDECIDED`, never guessed; immaterial
here because their `r` is a registered constant, **but it means those records
could not survive a clause-A audit on their own contents.** The markdown-only
ansys rows were **transcribed, not re-derived.** **F26's error norms were not
re-measured** and no claim is made about the `9.1e-02`. **And the zero-flip result
is a property of THIS CORPUS, not of the clauses** — every ladder in this lab was
built at `r >= 1.5964`.

| Amendment 2 | figure |
| --- | --- |
| graded `CONVERGING` rows swept | **111** (106 if duplicate triples counted once) |
| distinct refinement ratios in the entire lab | **4** — 1.5964, 1.5986, 1.6000, 2.0000 |
| **clause A flips, unscoped** | **0** |
| **clause A flips, Amendment-1 scoped** | **0** |
| rows clause A could ever reach (`r` computed at grading) | **29 of 111** |
| **is the case clause A was written for in the population?** | **NO — F26 does not import the module** |
| **clause B flips, substantive reading** | **1** — F20 at **18.79×** its own `GCI_abs` |
| **clause B flips, this spec's LITERAL wording** | **0** |
| rows with an exact/manufactured reference on an error norm | **10 (9 %)** |
| nearest un-flipped row | **F15 at 0.918× — a 9 % move flips it** |
| rows DECLARING a reference class | **5 of 111 (4.5 %)** |
| overlap / union | **0 / 1** |
| real importers, `ast`-verified | **36** at `aaf0bed6`, **39** at HEAD |
| graders that have FIRED | **larger than the stated 9** — co-location undercounts by **>= 11** |
| callers reading ONLY the parent Richardson key | **0 — the hazard is LATENT** |
| committed records publishing both keys as PEERS | **10 — the hazard is LIVE HERE** |
| status | **SPEC, NOT ADOPTED — unchanged** |
