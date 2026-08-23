# R5 — discharge record for the three round-5 diagnostic constraints

**Written 2026-08-23 by a closure lane, at the closure supervisor's dispatch.**
**Zero compute.** No solver ran, no fit was made, no field was written. Every
number below is quoted from a committed artefact and every artefact was opened
and read while writing this file. The four arithmetic ratios in §3.3 are
divisions of numbers already in the cited table and are labelled as such.

---

## 0. What this record is, and the four things called "R5" that it is not

`docs/closure/CLOSURE_LINE_RESTART_DOCTRINE.md` lines 210–214 define rung **R5**
of the rebuild program, verbatim:

> ### R5 — Round-5 diagnostics feed the build as constraints
>
> - **duct feature degeneracy**;
> - **`Re_y` extrapolation trap**;
> - **vortex-structure failure — structure metrics in OUR validation.**

That is the whole of the rung. It is three constraints on the build, not an
experiment. **It carries no pre-registered gate, no threshold, no cap and no
label**, and none was ever written for it. The board has therefore carried
"R5: no verdict artefact" for two sessions, correctly.

**This file is a DISCHARGE RECORD, not a verdict.** Because R5 was never
pre-registered, the standing rule that a gate is frozen before compute
(`CLAUDE.md` rule 2) forbids inventing one now, and the fixed verdict vocabulary
(`CLAUDE.md` rule 1) is deliberately **not** used anywhere below for R5 itself.
Each constraint gets a plain-words status — *discharged* / *partly discharged* /
*not discharged* — and the artefacts that carry it. Where a cited artefact
carries its own registered verdict, that verdict is quoted in its own words and
belongs to that artefact, not to R5.

**Name collisions, disambiguated once.** Four different things in this
repository are called some form of "R5". This record is about the first only:

| Name | What it is | This record's relation to it |
|---|---|---|
| **R5**, the rung | doctrine lines 210–214, the three constraints above | **the subject of this file** |
| `docs/closure/R5_DECISION_MEMO.md` | the *direction* decision after R4's GATE FAIL — options A / A' / B1 / B2 / C / D | **on Sanaa's desk; untouched here.** Cited only to disambiguate the name. No option is evaluated, recommended, ranked or advanced anywhere in this file. |
| **R5C** | the option-C ω-source repair lane, closed 2026-08-22/23 with its own registered verdict **GATE FAIL** (D465, L-243) | a different rung with its own pre-registration; not graded here |
| `verification/campaign/R5_PREREGISTRATION.md` | "R5 — the QCR forward entry", the **round-5 Closure Challenge** submission of 2026-08-07 | the *source* of the diagnostics R5-the-rung carries forward, not the rung |

The word "Round-5" in the rung's title points at the last of these: the
heterogeneous closure-challenge entry Sanaa ruled **NOT SENT** on 2026-08-18
(doctrine line 22). R5-the-rung is the instruction that the diagnostics that
entry produced must **constrain the rebuild** rather than be discarded with it.

---

## 1. Where the three constraints came from

Each constraint names a specific, measured failure of the round-5 entry. Traced
so that "what the constraint required" is not a paraphrase.

**Constraint 1 — duct feature degeneracy.** The round-5 entry's duct model ran
on seven Pope-invariant features. `research/closure/md/CLOSURE_CHALLENGE_STATUS.md`
§0b, lines 166–172, records the finding: RANS produces exactly zero secondary
flow on every duct training case, so the mean field has the form `U = (u(y,z),
0, 0)`, and for *any* gradient of that form `I3_S3` and `I4_W2S` vanish
identically — verified on the data (max |value| ~1e-14) and analytically over
50,000 random shear-rate pairs. **Two of seven features carry zero information
on the entire duct family, by mathematical necessity.** The requirement R5
carries forward: *before training, know which library columns are algebraically
dead on which family, and do not let a dead column enter a fit as if it
discriminated something.*

**Constraint 2 — the `Re_y` extrapolation trap.** Same file, lines 418–423,
correcting the entry's own published duct diagnosis: `I3_S3`/`I4_W2S` are zero on
*every* duct including the one the entry won, so they discriminate nothing; what
discriminated is that **`Re_y` reaches 1.85× and 2.07× its trained maximum on
the two ducts the entry was losing (0.90× on the one it won), and a
gradient-boosted tree cannot extrapolate.** `Re_y` there is the unclipped
wall-distance turbulent Reynolds number `sqrt(k)·d/(50·ν)`
(`docs/research/CLOSURE_METHODS.md` §"Where Certonomous sits in this taxonomy").
The skeptic's pass records the same pair as one disclosure item —
`verification/campaign/LADDER_V_PASS3_COLD_2026-08-11.md:242`, "Item 6 / §7.1,
the duct feature degeneracy and the `Re_y` extrapolation failure". The
requirement R5 carries forward: *check every feature's test range against its
training range before the model is trusted there, and know that a
non-extrapolating regressor fails hardest exactly where a feature leaves its
trained interval.*

**Constraint 3 — vortex-structure failure; structure metrics in OUR
validation.** The round-5 entry's duct deficit is the corner-driven secondary
vortex a linear Boussinesq closure has no mechanism to produce. §0b Finding 3
measures that the two anisotropy components implicated in Prandtl's secondary
flow of the second kind are weak or unreliable on that feature set (`b_yz`
held-out R² 0.27; `b_yy − b_zz` R² 0.04 with one fold at −0.69). The requirement
R5 carries forward is the operative half of its own wording: **structure metrics
in OUR validation** — a validation suite that scores only bulk error will not
see a missing vortex, so the vortex must be a measured quantity in the lab's own
validation, not an explanation offered afterwards.

---

## 2. Constraint 1 — duct feature degeneracy

### 2.1 What it required
Per-family degeneracy is measured **before training**; algebraically dead and
near-constant columns are flagged and excluded; the fit is not permitted to
allocate coefficient mass among columns that are exact linear combinations of
one another.

### 2.2 What discharges it

**(a) The audit exists, is per family, and ran before any R4 training.**
`cases/RANS_LES_closure_models/_common/features/FS2_DEGENERACY_REPORT.md` §1
(lines 11–20), on 110 features and 40 cases, 641,652 cells: no family reaches
full rank; **the ducts are worst — rank 96 of 110, 48 algebraically-zero
features, condition number 1.17e+33**. §2 (lines 24–39) lists all **12**
pooled-dead invariants by name and gives the physical cause: every case in the
benchmark is a statistically two-dimensional mean flow. §4 (lines 66–73)
measures the per-cell tensor-basis rank and gives the ducts as the lowest family
at **3.006–3.030** against a nominal basis of 10, never above 5 in any cell of
any case.

**(b) The audit was carried into the R4 build as registered exclusions.**
`cases/RANS_LES_closure_models/R4_sparta_build/PREREGISTRATION.md` (frozen
2026-08-21, sha256 `058444…cbbe8`, **never edited** — hash re-verified against
the working copy and against the HEAD blob while writing this record):
- §2.2, lines 95–111, carries the FS2 numbers per *training* family and excludes
  the **12 pooled-training dead features** from every fit;
- §2.1, lines 71–93, registers the duct-specific exclusion: on `AR_1_Ret_180`,
  `T4 = −T3` to machine precision (`||T3+T4||/||T3||` median **2.74e-17**), `I2 =
  −I1` identically, per-cell rank of `{T1..T4}` **exactly 3.000** — and therefore
  **`T4` and `I2` are excluded on any fit whose training set is ducts only**,
  with the design-matrix condition number reported per fit on mixed-family fits.

**(c) R4 executed the rule and reported the condition numbers.**
`R4_sparta_build/RESULTS.md` §3.2 (lines 241–282) reproduces §2.1's numbers
exactly on the baseline RANS field (median **2.7398e-17**, p99 **6.4084e-16**,
max **7.0760e-15**, rank **3.000** on all 2,209 cells), which is what fixes the
convention and proves the lane's `T4` is the pre-registration's `T4`. No
ducts-only fit was run, both terms were retained as registered, and the four
fitted design condition numbers are on the record — **653.9 / 7.707 / 54.81 /
7.707** (§11.4, lines 1203–1208).

### 2.3 The measurement that complicates it, and does not remove it

**R4 measured that the exact duct degeneracy is a property of the baseline RANS
field and is ABSENT on the frozen field the regression actually fits.**
`RESULTS.md` §3.2 lines 255–265 and §11.4 lines 1193–1201, on the same 2,209
cells of `AR_1_Ret_180`:

| field | `\|\|T3+T4\|\|/\|\|T3\|\|` median | p99 | `\|I1+I2\|/\|I1\|` median | per-cell rank of `{T1..T4}` |
|---|---|---|---|---|
| baseline RANS (`334/U` — **the FS2 measurement**) | 2.7398e-17 | 6.4084e-16 | 0.000e+00 | **3.000** (2209 / 2209 at rank 3) |
| frozen (`U = U_LES`), OpenFOAM `grad(U)` | 1.2779e-02 | 4.6889e-01 | 7.0405e-05 | **3.965** (2132 / 2209 at rank 4) |
| frozen, finite-difference gradient | 1.2819e-02 | 4.7060e-01 | 7.1543e-05 | 3.966 |

Across all four training ducts on frozen fields the rank is **3.965, 3.977,
3.978, 3.977**. The cause is physical, not numerical: the exact cancellation is a
property of a *linear-eddy-viscosity* duct mean flow, and the DNS mean flow has
secondary motion, so the in-plane gradients do not vanish (§3.2 lines 267–272).

**What that moves.** R4 states it precisely and this record does not extend it:
the registered exclusion is scoped to ducts-only fits, this lane ran none,
**the rule is not amended and no R4 verdict turns on it** (§11.4 lines
1203–1212). What the measurement falsifies is the rule's **stated
justification** — that including both would be "an exact collinearity". On
frozen fields it is not exact. **A future lane applying §2.1's exclusion to a
ducts-only fit would be applying it for a reason that is false on the fields it
would be fitting.**

**Read against constraint 1**, this is the sharper finding: the constraint was
fed into the build **through an instrument measured on a different field than
the one the regression fits.** FS2's whole library is built from the converged
baseline RANS case — `_common/features/build_features.py` reads the latest time
directory of the baseline case (docstring lines 1–18; `case_features`, lines
96–101), and `RESULTS.md` line 260 labels that same field "`334/U`, the FS2
measurement". The R4 regression fits frozen fields (`U = U_LES`). **That
field mismatch is measured for the tensor-basis degeneracy. It is not measured
for the 110-feature FS2/FS5 library**, and this record does not assume it
transfers — see §3.4 and §6.

### 2.4 Status

**PARTLY DISCHARGED.**

- Discharged: the audit exists, is per family, ran before training, was carried
  into a frozen pre-registration as explicit exclusions, and was executed with
  condition numbers reported per fit.
- Open: the exclusion rule stands on a justification R4 measured to be false on
  frozen fields. **The rule is scoped so that nothing has yet been decided on
  that false basis**, and R4 correctly declined to amend a frozen file. The
  repair belongs in the next pre-registration that could run a ducts-only fit.
  `RESULTS.md` §11.7 (lines 1282–1306) carries two amendment candidates forward;
  **this one is not among them**, though §11.4 states it in full — recorded here
  so it is not lost between the two lists.

---

## 3. Constraint 2 — the `Re_y` extrapolation trap

### 3.1 FS5 is a standing gate and is never "closed"

`docs/charters/CLOSURE_MODELLING_CHARTER.md` §22.5 (lines 815–833) makes **FS2
and FS5 standing gates**: FS5 requires that *"every feature's test-family range
is checked against its training range. Beyond a declared factor the response is
retrain-coverage expansion, or explicit documented acceptance."* A standing gate
is **discharged per build and permanently re-armed**. Nothing in this record
closes it, and no future record may cite this file as having closed it. The
question a discharge record can answer is narrower: *was it discharged for the
R4 build?*

### 3.2 What discharges it

**(a) The FS5 instrument exists and was run.** `FS2_DEGENERACY_REPORT.md` §6
(lines 124–139): every TEST case's cells against the per-feature min/max over
the 32 non-TEST cases. Four hills at **0.00–0.06 %** of cells outside on ≥1
feature, three ducts at **0.96–3.07 %**, and **`NASA_2DWMH` at 31.79 %, with 49
of 110 features out of range somewhere on it** — a third independent instrument
agreeing with the Mahalanobis statistic and with the measured hump blow-up of
every tensor-basis model. Per-feature worst excursions on the hump are tabulated
at lines 141–157. Artefact on disk: `/home/ubuntu/closure-data/features/fs2_audit.json`
(key `coverage.per_test_case`), read while writing this record.

**(b) The trap's own mechanism is structurally absent from the R4 model.** Two
independent reasons, both registered before compute:
- **The regressor.** The round-5 failure mode was *"a gradient-boosted tree
  cannot extrapolate"*. R4's model is a **symbolic polynomial in `I1` and `I2`**
  — `MODEL.md` lines 43–67 — which extrapolates by construction (well or badly,
  but it is not a step function that flattens outside its trained box).
- **The feature.** `Re_y` carries molecular viscosity. R4 `PREREGISTRATION.md`
  §2.3 (lines 113–121) registers that `I1`, `I2` are formed with `τ = 1/ω`,
  which **carries no molecular viscosity and is therefore Reynolds-similar**,
  and **excludes the entire Durbin-bounded feature block for exactly that
  reason** — it contains `ν` through `6·sqrt(ν/ε)`, "so two geometrically
  identical flows at different `Re` do not map to the same feature value". That
  clause is the closest thing in the frozen file to a direct answer to
  constraint 2, and it answers it structurally rather than by measurement.
  **`Re_y` / `q1_wallRe` is not among R4's selected terms at all** (`MODEL.md`
  lines 45–61).

**(c) No test exposure occurred, so no extrapolation could be spent.**
`RESULTS.md` lines 12–17 and §7 lines 787–791: `r4_lib.assert_no_test_case`
raises on any member of the benchmark README's TEST or validation set and is
called at the top of the case builder, the dataset assembler, the FS3 selector
and both scorers. The boundary is asserted in code, not promised in prose.

### 3.3 What does not discharge it — three measured gaps

**(i) The registered per-model coverage document did not ship.**
`PREREGISTRATION.md` §7 (lines 199–205) registers, in full:

> `COVERAGE.md` ships with `MODEL.md` and states: each selected feature's range
> on each training family against the others; the pooled training range; and
> **what a future test exposure must check** — for every selected term, the
> fraction of test cells outside the training range, and the per-cell rank of
> the selected tensor set on the test family.

**No such file exists.** `git ls-tree -r HEAD` over the whole repository returns
no `COVERAGE.md`, and `find cases/RANS_LES_closure_models -iname 'COVERAGE*'`
returns nothing on disk. (Planted control on the reader: the same `git ls-tree`
sweep returns eight other paths matching "coverage", so the search is able to
see a non-zero.) Further, **the strings `FS5` and `coverage` appear zero times
in `R4_sparta_build/RESULTS.md`** — control: `FS2` appears 6 times in the same
file by the same grep — and **none of the twelve departures D-1…D-12 (§9, lines
870–970) discloses the non-delivery**, nor does §7 "What this lane cannot see"
(lines 782–830), which is otherwise unusually complete. This is the one thing
about the R4 record that a reader could not have learned from the R4 record.
Charter §22.5 line 819 states the same duty in charter form — *"a coverage
report ships with every model"*. **Whether that constitutes a §22.5 standing-gate
failure is a grading call and is not made here**; the measured fact is stated
and referred.

**(ii) FS5's "declared factor" has never been declared.** The clause requires a
factor declared *in advance*, with two permitted responses beyond it
(retrain-coverage expansion, or explicit documented acceptance). A repository
sweep for "declared factor" returns exactly three hits — the doctrine line 252
and charter lines 822 and 827, i.e. **the three statements of the requirement
and no instance of the requirement being met.** FS2 §6 reports *fractions of
cells outside* and *worst excursions in training spans*, which is the
measurement the factor would be compared against; no threshold was set and
neither permitted response was invoked.

**(iii) The FS5 numbers that do exist are not the R4 build's numbers.** Three
mismatches, each checkable:
- **Training set.** FS2 §6 line 126 defines the training range over the **32
  non-TEST cases**, which includes the five validation cases
  (`fs2_training_only.json` key `val_excluded`: `AR_7_Ret_180`,
  `alpha_05_10071_2024`, `alpha_05_10071_4048`, `alpha_15_7929_2024`,
  `alpha_15_7929_4048`). R4's registered training set is 27 cases and its
  **realised** training set is **12** (`RESULTS.md` §11.3(c), lines 1165–1176).
  A range measured on 32 cases is not the range the R4 coefficients were fitted
  inside.
- **Feature set.** FS5 §6 covers the **110-feature FS1 library**. R4's model
  uses `I1`, `I2` and the tensors `T1..T3` built with `τ = 1/ω` on frozen
  fields. Those are not columns of the FS1 library.
- **Field.** As established in §2.3, FS1/FS2/FS5 are computed on baseline RANS
  fields; R4 fits frozen fields. **This is inference from two measured facts**
  (the build script's input, and R4's own baseline-vs-frozen table), **not a
  measurement of FS5 coverage on frozen fields.** No such measurement exists and
  making one is compute this record did not spend.

**A structural note on the trap's own feature, measured.** The FS1 library's
wall-distance Reynolds number is `q1_wallRe = min(sqrt(k)·d/(50·ν), 2)` —
**clipped at 2** (`_common/features/FEATURE_LIBRARY.md:174`). Its pooled
statistics in `fs2_audit.json` are `max = 2.0`, `p99 = 2.0`, **`p50 = 2.0`**:
the column is saturated at its clip on more than half of all cells. A test cell
whose true `Re_y` is 1.85× or 2.07× the trained maximum therefore **cannot
register as "above the training range" on that column**, because the training
maximum is the clip. `q1_wallRe` appears in the reported worst-features list for
no test case (those lists are truncated at 12 entries where more features are
outside, so this is "not in the reported worst 12", not "not outside"). The
round-5 trap was measured on the **unclipped** `Re_y`. **The FS5 instrument as
built is blind to the excursion that named this constraint** — stated as a
property of the clip and the reported statistics, not as a claim that any R4
number is wrong, since R4 does not use this feature.

### 3.4 Status

**PARTLY DISCHARGED, and the gate stays armed.**

- Discharged: an FS5 instrument exists, ran, and produced the finding that
  matters most operationally (`NASA_2DWMH` 31.79 % out of range, 49/110
  features) — which is the hump, the case every tensor-basis model in this
  programme blows up on. The specific round-5 mechanism is structurally absent
  from R4 (symbolic model, Reynolds-similar normaliser, `Re_y` not selected, no
  test exposure).
- Not discharged: the per-model coverage document registered at
  `PREREGISTRATION.md` §7 did not ship and its absence is undisclosed; FS5's
  declared factor does not exist; the coverage numbers on record are for a
  different feature set, a different training set and a different field than the
  R4 build's; and the library's own `Re_y` analogue is clipped where the trap
  lives.

---

## 4. Constraint 3 — vortex-structure failure, structure metrics in OUR validation

### 4.1 What it required
The corner-driven secondary vortex must be a **measured quantity inside the
lab's own validation instrument**, on the same footing as bulk error, so that a
model that misses it cannot look good.

### 4.2 What discharges it

**(a) The metric is registered as a gate line, before compute.**
`PREREGISTRATION.md` §6 (lines 167–197), fourth a-posteriori bullet, lines
186–188:

> **structure**: duct secondary-flow magnitude as % of bulk (training ducts;
> DNS values from `BASELINES.md` sec. 4) and reattachment on training hills and
> `CBFS13700` against LES;

This is the constraint written into a frozen file before the solver started. It
is registered as a **reporting** duty; **no threshold is attached to it** (see
§4.3).

**(b) The metric ran, on every configuration, and it discriminates.**
`RESULTS.md` §5.3 (lines 668–682), duct secondary flow as RMS in-plane velocity,
% of bulk:

| case | LES | NULL | CEILING | `ξ=0.1` † | `R`-only † |
|---|---|---|---|---|---|
| `AR_1_Ret_180` | 1.7630 | **0.0000** | 1.7522 | 0.1981 | **0.0000** |
| `AR_3_Ret_180` | 1.6504 | **0.0000** | 1.6440 | 0.2767 | **0.0000** |
| `AR_5_Ret_180` | 1.4622 | **0.0000** | 1.4574 | 0.2498 | **0.0000** |
| `AR_10_Ret_180` | 1.2238 | **0.0000** | 1.2227 | 0.2137 | **0.0000** |

† unregistered diagnostic arms, departure D-7, **reported and not graded**.

The linear EVM produces **exactly zero** — the textbook failure this constraint
names — and the frozen-field ceiling recovers the vortex where a linear model
gives nothing. `R`-only produces exactly zero too, which R4 calls the cleanest
statement in its file of what the two corrections do: `R` corrects the `k`
budget and cannot make a secondary vortex; only `b^Δ` can. That is constraint 3
doing work: **the structure metric separated two configurations that a bulk
error would have ranked together.**

**(c) A second structure metric ran beside it.** Reattachment on the bottom wall
by the registered instrument (`_common/sst_baseline_metrics.py::hill_wall_metrics`,
longest-reversed-run criterion, same row and criterion for every configuration
and for the LES), `RESULTS.md` §5.3 lines 684–703: the shipped baseline
over-predicts the bubble by **39–100 %**; the ceiling lands **within 0.9–3.4 %**
of the LES on all seven cases where it converged; NULL reproduces the shipped
baseline exactly on seven of eight and to 0.07 % on `CBFS13700`.

**(d) The result is stated with its boundary.** `RESULTS.md` §11.2 (lines
1104–1143) is explicit that every ceiling number is an **upper bound available
only when the answer is already known** — "It is not a model, it predicts
nothing, and no sentence anywhere may present it as this lane's closure model."
§11.3 states what was not established. The structure metric is reported inside
that boundary, not outside it.

### 4.3 What remains open

**(i) The structure metric carries no threshold, so nothing can fail on it.**
`RESULTS.md` §6, gate **G5** (line 753): *"structure: duct secondary flow as %
of bulk, and reattachment against LES | reported in sec. 5.3 | **reported**"* —
the verdict column says "reported", not a gate verdict, because §6 registered no
bar. The same shape as **G4** (realisability), whose thresholdlessness R4 puts
on the record twice as a defect (§7 lines 806–811, §11.7 item 1, lines
1288–1298) — *"This preregistration repeated the omission"*. **R4 flagged the
missing realisability bar and did not flag the missing structure bar.** Read
against constraint 3, which asks for structure metrics *in* validation, a
metric that is printed but cannot fail is a weaker discharge than a metric that
gates — R4's own words about G4, at §11.7 item 1, apply unchanged to G5: a
model "reached propagation without failing on that axis". This is the single
largest open item on constraint 3.

**(ii) The metric exists on ducts only.** Secondary-flow magnitude is a duct
metric; the hills and `CBFS13700` are covered by reattachment. No structure
metric is registered for `NASA_2DWMH`, the case every model in this programme
fails on — and none could be, since it is a TEST case no lane may open before
the scoring call.

**(iii) An arithmetic discrepancy in the closed R4 record, found while checking
this cite.** `RESULTS.md` §5.3 line 679 and §11.2 line 1128 both state the
ceiling recovers the vortex "to **0.4–0.6 %** of the DNS value". Dividing the
same table's own numbers gives relative deficits of **0.613 %, 0.388 %, 0.328 %,
0.090 %** — a range of **0.09–0.61 %**, not 0.4–0.6 %. Two of the four rows fall
below the stated interval. **The error runs in the ceiling's favour** (the
ceiling is closer to the DNS than the record claims) and **no verdict moves**,
because G5 is a reported row with no bar. Recorded, not corrected: the R4 file
is a closed record with its verdict already on the docket, and correcting it is
its owner's call, not this lane's.

### 4.4 Status

**DISCHARGED as a measurement; PARTLY DISCHARGED as a validation duty.**

The vortex is a registered, measured, per-configuration quantity in the lab's
own validation, and it demonstrably discriminated between configurations. What
is missing is the second half of "in OUR validation": it cannot fail, because no
threshold was ever registered for it.

---

## 5. The R4 pre-registration against R5, clause by clause

**Measured, with a planted control on the reader.** `grep -n "R5"
R4_sparta_build/PREREGISTRATION.md` returns **zero lines**; the same grep for
`doctrine` on the same file returns line 6 (`## 0. ZERO-SHOT DISCIPLINE (charter
§22.3, doctrine R1)`), so the reader can see a non-zero. **The R4
pre-registration cites the doctrine by rung name — R1 — and never names R5.**
`MODEL.md` names R5 zero times; `RESULTS.md` names it once, at line 1311, and
that single occurrence is a pointer to `R5_DECISION_MEMO.md`, i.e. to the
direction decision, not to the rung.

The board's line — *"the R4 prereg does not cite R5 by name"* — is therefore
literally correct. What it does not say, and what this section supplies, is that
**all three constraints do have corresponding clauses**:

| R5 constraint | Corresponding clause in the frozen R4 pre-registration | What kind of clause |
|---|---|---|
| 1. duct feature degeneracy | **§2.1** (lines 71–93): `T4`/`I2` excluded on ducts-only fits, condition number reported per fit — and **§2.2** (lines 95–111): the 12 pooled-training dead features excluded from every fit | **an exclusion rule**, executed; justification later measured false on frozen fields (§2.3 above) |
| 2. `Re_y` extrapolation trap | **§2.3** (lines 113–121): no `ν`-carrying normaliser anywhere, Durbin-bounded block excluded because two identical flows at different `Re` would not map to the same value — and **§7** (lines 199–205): `COVERAGE.md` ships with `MODEL.md` — and **§0** (lines 6–46) zero-shot discipline | **one structural exclusion**, executed; **one deliverable, NOT DELIVERED** |
| 3. vortex-structure failure | **§6** (lines 186–188): duct secondary-flow magnitude as % of bulk and reattachment against LES | **a reporting duty with no threshold**, executed as written |

**No constraint is without a clause.** The honest form of the gap is different
from "no clause exists": constraint 2's clause exists and **its registered
deliverable did not ship**, and constraint 3's clause exists but **is a
reporting duty that cannot fail**. Neither of those is visible from the "does
not cite R5 by name" formulation, and both are visible from the frozen file.

**Why the naming matters at all, and how far it matters.** The freeze is the
pre-registration's entire evidentiary content (`CLAUDE.md` rule 2). Naming R5 in
it would not have added evidentiary weight; the clauses are what bind. What the
absent name costs is **traceability**: nothing in the frozen file, and nothing
in `RESULTS.md`, tells a reader that §2.1, §2.3, §7 and §6 are discharging a
standing doctrine rung, so nobody grading R4 was ever prompted to ask whether
R5's three constraints had been met — which is how the undelivered `COVERAGE.md`
of §3.3(i) survived a lane that otherwise documented twelve departures and ten
things it could not see.

---

## 6. Summary of statuses, and what would close each

| Constraint | Status | Citing artefacts | What is still open |
|---|---|---|---|
| **1. duct feature degeneracy** | **partly discharged** | `_common/features/FS2_DEGENERACY_REPORT.md` §1/§2/§4; `R4/PREREGISTRATION.md` §2.1, §2.2; `R4/RESULTS.md` §3.2, §11.4 | the ducts-only exclusion rests on a justification measured false on frozen fields; scoped so nothing has been decided on it; repair belongs in the next pre-registration |
| **2. `Re_y` extrapolation trap** | **partly discharged; standing gate stays armed** | `FS2_DEGENERACY_REPORT.md` §6; `/home/ubuntu/closure-data/features/fs2_audit.json`; `R4/PREREGISTRATION.md` §2.3, §7; `R4/MODEL.md`; `R4/RESULTS.md` §7 | `COVERAGE.md` (prereg §7) never shipped and its absence is undisclosed; FS5's declared factor has never been declared; existing coverage is on a different feature set, training set and field; `q1_wallRe` is clipped at 2 where the trap lives |
| **3. vortex-structure failure** | **discharged as a measurement; partly discharged as a validation duty** | `R4/PREREGISTRATION.md` §6; `R4/RESULTS.md` §5.3, §6 (G5), §11.2 | no threshold registered, so G5 is "reported" and cannot fail; duct-only metric; a 0.4–0.6 % vs 0.09–0.61 % arithmetic discrepancy in the closed record |

**Three things that would close, or move, each item — none of them this lane's
to authorise, and each costing compute that is not spent here:**

1. A per-model coverage document meeting `PREREGISTRATION.md` §7's four listed
   contents, computed on the **frozen** fields and the **12-case** realised
   training set, for the terms actually in `MODEL.md`. This is the item that
   would move constraint 2 furthest, and it is the item the R4 lane owed.
2. A declared FS5 factor, written into the next pre-registration before compute,
   with the two permitted responses named.
3. A registered structure **threshold** in the next pre-registration, so that
   the vortex metric can fail. `CLOSURE_MODELLING_CHARTER.md` §4's realisability
   wording is the model for the shape; the number is not this lane's to pick.

---

## 7. What this record cannot see

* **It grades nothing.** R5 has no pre-registered gate and none is invented
  here. No `PASS`, `GATE FAIL`, `NOT A RESULT` or any other fixed-vocabulary
  verdict is issued on R5, on any of the three constraints, or on any clause of
  a frozen file. Where R4's own verdicts are quoted they are R4's.
* **It measured nothing new.** Zero compute. Every number is transcribed from a
  cited artefact, except four divisions of numbers already in the §4.2 table,
  which are labelled where they appear (§4.3 iii).
* **It did not verify FS5 coverage on frozen fields.** The field-mismatch
  argument in §3.3(iii) is **inference from two measured facts** — what
  `build_features.py` reads, and R4's own baseline-versus-frozen table. Whether
  the 110-feature coverage numbers would change materially on frozen fields is
  **unmeasured**, and it is a fit-free but non-trivial compute item.
* **It did not re-derive the round-5 diagnostics.** The 1.85×/2.07× `Re_y`
  excursions and the §0b expressivity findings are quoted from
  `research/closure/md/CLOSURE_CHALLENGE_STATUS.md` as the round-5 record, not
  independently reproduced. That entry is `NOT SENT` and its record is internal
  R&D by Sanaa's ruling.
* **It says nothing about the R5 direction decision.** `R5_DECISION_MEMO.md`
  options A / A' / B1 / B2 / C / D are Sanaa's. No option is evaluated,
  compared, recommended or advanced by anything above, and no reader may take
  any status in §6 as an argument for or against any of them.
* **It does not touch the board.** `docs/LAB_STATE.md` is the supervisor's.
* **Nothing was sent.** Nothing here is filed, uploaded, registered, submitted
  or communicated outside this box (`CLAUDE.md` rule 7, rule 8).

**Compute:** 0 core-minutes. No solver, no fit, no field written. Artefact reads
and text only.
