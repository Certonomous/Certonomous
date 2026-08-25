# THERMAL TIER AUDIT — supervisor's ruling, 2026-08-25

**The headline, stated first because it is the finding: under this ruling the
thermal family has ZERO rows at `HOLDS`.** The honest §3 census becomes
**`HOLDS` 0 / `GATE REACHED` 6 / `SURVEYED` 13 / `NOT HELD` 12 / `NEVER RUN` 6 =
37**, against the recorded **5 / 1 / 13 / 12 / 6**.

**No verdict moves. Not one.** Every gate verdict in the corpus stands exactly as
its frozen comparator returned it. **What moves is the tier** — the claim about
what the case establishes for the lab — and it moves **down** in five places.

Audited by a lane against artifacts, then **the load-bearing pieces re-verified
personally by the supervisor**, each with a positive control. Ruled under
`THERMAL_TIERING_DIRECTIVE.md` §3.1, whose prohibitions this exercise was written
to enforce.

---

## 0. THE MOST IMPORTANT SENTENCE IN THIS DOCUMENT, so it is not lost below

**Thermal's `G` column is NOT empty. It is the strongest in the lab.** The
verification team found `G` **structurally empty across dafoam and closure** —
`GCI`, `Roache` and `CONVERGING` appear in zero files in either tree. **In this
family `G` is real and artifacted**: S6, S8, S13, S19 and S22 carry genuine
`CONVERGING` triples with observed orders and GCIs at Fs = 1.25, and their
per-level plateau checks pass against registered tolerances.

**What defeats those rows is `P`, not `G`.** They are graded against **exact
analytic solutions**, and an analytic solution is **code verification** — it
supplies **V**, and it cannot supply **P**, which requires validation against a
**public primary source**. **The lab can converge a grid. It cannot yet point at
the world on those rows.** That is a far more precise statement of the family's
position than "zero HOLDS", and it is the one that should be carried upward.

---

## 1. RULING 1 — an exact analytic solution supplies V, and NEVER P

**This is the rubric ruling that turns four of the five rows, so it is stated
before the rows and can be overturned on its own terms.**

The three columns as defined: **V** = code verification — *an exact solution, a
manufactured solution, or a correlation*. **P** = validation against a **public
primary source**, with the pre-registration on disk.

**RULING: the same artifact cannot supply both V and P.** An exact solution is
named in V's own definition. If an exact solution could also discharge P, then
**every code-verification row would become `HOLDS` automatically and the P column
would certify nothing** — a column that cannot be missing is not a column. P
exists to ask a different question: *has this been checked against the world?*
An analytic solution is a check against the mathematics, which is what V asks.

**Consequence, and it is not a criticism of these rows:** S6, S13, S19 and S22
are **genuinely strong on V and G**. They are not `HOLDS` because **nothing in
them is a claim about the world.**

---

## 2. RULING 2 — K0c: CONFIRMED, and the tier falls

**Verification's finding is confirmed on artifacts and is worse than stated.**
Re-verified personally, with a positive control:

| check | result |
|---|---|
| run tree | **four PAIRS, not triples** — `Ra1e3_m32/m64`, `Ra1e4_m40/m80`, `Ra1e5_m64/m128`, `Ra1e6_m128/m192`. **Eight directories, no third level at any Rayleigh number.** |
| `gate_k0c.json` triple machinery | **`gci` 0, `richardson` 0, `triple` 0, `observed_order` 0** |
| **positive control**, same reader, same invocation | `gate_t3.json`: **`gci` 4, `richardson` 2, `triple` 17** — the reader is not blind |
| every one of the 20 `gate_rows` | carries exactly `coarse_mesh` and `fine_mesh` |
| the pre-registration | registered a pair **deliberately** — `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md:110-113`, *"a **two-mesh pair** (refinement factor ≥ 1.5 in each direction)"* |

**The quoted orders belong to K0b, whose own record forbids their use.**
`K0c_RESULTS.md:333-336`, read personally, verbatim:

> K0b's Pr = 0.706814 and its `limitedLinear`/`linearUpwind` schemes are kept
> deliberately, so **the de Vahl Davis values do not apply to these cases and are
> not used**: K0b is a capability rung graded against no published datum and this
> does not change that.

**A further defect verification did not name: the quoted range is not a range.**
The matrix quotes *"`p` 1.94–2.33"*. K0b's table at `K0c_RESULTS.md:340-345` runs
**1.75 to 2.98**. "1.94–2.33" is **neither the min nor the max** — two interior
values presented as a span, **tighter than the truth in both directions**, and
the record's own prose one line below (`:351-352`) states the correct span.
**Borrowed numbers were additionally narrowed in the borrowing.**

**`fine_value_3pt_estimator` is not a third level** and does not rescue the
triple: `analyse_k0c.py:48` defines it as a **three-point wall-gradient stencil
on one mesh**, reported as a discretisation sensitivity (`:55`).

**K0c's own gate document rules against the tier**
(`K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md:18-21`): *"the turbulent rung … is the
only rung on this gate that can feed a trust tier above TREND ONLY."* The
turbulent rung is `GATE FAIL`.

**P also fails:** de Vahl Davis 1983 is **not on disk** — a filesystem-wide
search returns nothing. Only the secondary `han_xie_2019_1903.09506.pdf` is held.

**What K0c does have, and it is real:** an armed, met, per-level plateau
criterion — peak-to-peak of `Nu_avg` below **0.02 %** over the last 400 outer
iterations, with all eight graded cases at **0.00022–0.00359 %**. **K0c's failure
is the missing third level, not the plateau.**

**VERDICT: `PASS` — untouched.** The frozen comparator returned 0 of 20 failed
and nothing here disturbs it.
**TIER: falls from `HOLDS`. Missing G and P; V doubtful.**

### 2.1 A VOCABULARY GAP, ESCALATED RATHER THAN PAPERED OVER

`GATE REACHED` is defined as *"**One** of V/G/P missing — the entry must name
which."* **K0c is missing two, and arguably three.** `SURVEYED` is *"breadth
evidence, **ungated**"* — but K0c **was** gated and its gate passed, so
`SURVEYED` understates it.

**The tier vocabulary has no word for "gated, passed, and two columns missing",
and inventing one is not mine to do** — the four words are Sanaa's.

**Ruling, with the disagreement recorded rather than hidden:** K0c is tiered
**`GATE REACHED`, naming BOTH G and P as missing**, because naming two missing
columns is more honest than naming one, and because `SURVEYED` would erase a gate
that genuinely ran. **The contrary argument is recorded here in full: `GATE
REACHED` is the higher tier, this family's errors have all run in the flattering
direction, and a reader may reasonably hold that `SURVEYED` is the honest word.**
**The question goes to Sanaa's desk. It is not settled here.**

---

## 3. RULING 3 — the five HOLDS: CONFIRMED, and they are S1, S6, S13, S19, S22

All five fall. **The missing column is `P` in all five; S1 is additionally
missing `G`.** No verdict moves.

| row | rung | verdict (UNCHANGED) | tier | missing |
|---|---|---|---|---|
| **S1** | K0c laminar cavity | `PASS` | `GATE REACHED` | **G and P** (V doubtful — see §2.1) |
| **S6** | T9a wall flux + interface 2 | `PASS ×2` | `GATE REACHED` | **P** — closed-form composite wall; no public primary exists |
| **S13** | E4a2 fan BC | `PASS ×8` | `GATE REACHED` | **P** — and see §3.1 |
| **S19** | T1c `f·Re` + constant-`q″` `Nu` | `PASS ×3` → see §4.1 | `GATE REACHED` | **P** |
| **S22** | T10a box floor/x-walls/y-walls | `PASS ×3` | `GATE REACHED` | **P** |

### 3.1 S13 additionally does not belong in a THERMAL holds-count at all

E4a2 grades a **flow** quantity (exact `Q = 1.5e-07 m³/s`), not a heat-transfer
one — **the certificate says so itself.** Its `G` is genuine (`p` 1.959 inside
the registered [1.6, 2.4], GCI 0.393 %, all five levels plateaued at
`r_last ≤ 6.8e-10` against a 1e-08 floor, and `E4a2_runs/FREEZE_CHECK.txt`
records **0 case dirs, 0 time dirs, 0 markers at freeze**). It is a good row in
the wrong column.

---

## 4. FOUR DEFECTS THE VERIFICATION AUDIT DID NOT NAME

### 4.1 S19's "PASS ×3" is TWO measurements, not three — verified personally

`gate_t1c.json` rows 1 and 3 (both `fRe`) carry a band **bit-identical to
sixteen significant figures**: `0.023589269742053554`, both `CONVERGING`. **The
momentum field does not depend on the thermal boundary condition**, so L1 and L3
are **one number graded twice**.

**This inflates a NUMERATOR** — the D414/D420 defect shape, which this team has
now met three times, and this is the first instance found inflating rather than
deflating.

**And the 2026-08-25 addendum's claim that L1/L3 carry "NO observed order" is
wrong in substance.** It is a **JSON-persistence artifact**: `analyse_t1c.py:463-470`
builds the `fRe` row without an `order` key, but `gci()` (`:321-337`) **cannot
return `CONVERGING` and a `GCI_pct` without computing `p`** — `p` is in the
denominator `r^p − 1`. **The row understates itself.**

**Bounded honestly:** the lane back-derives `p = 2.005054` by applying the frozen
`gci()` algebra to the stored triple. **That is arithmetic on an artifact, not a
re-execution, and it is recorded as such** — it is not quoted as a measured
order, and no tier is moved on it.

### 4.2 K0cT's denominator is inflated 18 → 14 — verified personally

`gate_k0ct.json` records **`graded_rows` = 14** and **`reported_never_graded` =
4** (the peak-velocity *location* rows). `K0cT_RESULTS.md` states at **both**
line 19 and line 217: *"**GATE FAIL. 8 of 18 graded rows failed.**"* — **four
never-graded rows sitting inside a "graded" denominator**, and the artifact
itself already carries the split.

**D420 was applied to K0cX** (`K0cX_RESULTS.md:418-422`, 60 → 42, *"the evidence
base was overstated by 43 %"*) **and never to K0cT.** Direction: **flattering** —
8/18 = 44 % reads better than **8/14 = 57 %**. **The `GATE FAIL` verdict and the
`NOT HELD` tier do not move; the denominator does.**

**Also found:** `gate_k0ct.json` carries **73 bare `"FAIL"` strings against 1
`GATE FAIL`** — the D-5 rule-1 vocabulary conflict, which the chief ruled is to
be corrected **by owning teams, by quote-and-strike, never by rewriting**.
Docketed; not swept.

### 4.3 The 43–722× attribution's FINEST LEVEL has no plateau artifact

The K0cG triple spans two run trees: coarse and fine are K0cS's
`S_SST_c`/`S_SST_f`; the finest is K0cG's `S_SST_x`. `gate_k0cs.json` carries a
per-level plateau check **that demonstrably fires** (`S_LS_c`/`S_LS_f` fail →
LaunderSharmaKE **REFUSED**). **`gate_k0cg.json` holds no convergence field of
any kind for the finest level.**

**The record already admits it** — `K0cG_RESULTS.md`'s own dated addendum §4:
*"**Section 5's convergence figures cite no artifact** … appear in no file on disk
… **neither is section 5's iterative-convergence monitor** … **Re-derivation was
not performed and is not claimed.**"*

**This is the VMFL051 mode sitting on the family's headline positive finding.**
The tiers do not inflate (S4 `NOT HELD`, S5d `SURVEYED`), so **nothing needs
downgrading** — but **the attribution's `G` is not verifiable from artifacts**,
and it may not be claimed as grid-established until a **new pre-registration**
with a per-level plateau precondition produces one. Additionally, **three of the
five orders exceed formal second order** (3.121, 4.078, 3.698), so **the GCI is
indicative, not exact** — and per CLAUDE.md rule 5 a GCI is never quoted where
the three values are not monotone.

### 4.4 A claim that a primary is NOT held, refuted by the artifact — and it is the ONE error that does not flatter us

The matrix says of K2c-B that VanGilder & Schmidt 2005 and its siblings have *"no
repository copies found"*, and calls the rung **BLOCKED — no primary**.

**`docs/papers/data_center_indoor_airflow/vangilder_schmidt_2005_ipack.pdf`
is on disk** (693 825 B) **with its `.txt` sidecar** (39 407 B), both dated
**2026-08-18** — **six days before the matrix was written.** Verified by
**title page**, per L-144, not by filename: *"IPACK2005-73375 … Roger R. Schmidt,
IBM … James W. VanGilder, American Power Conversion … a typical raised-floor data
center … perforated tile airflow."*

**Tier `NEVER RUN` is unaffected** — no solver ran. **The "no primary exists"
reasoning is refuted by an artifact**, and the rung is **not blocked for the
reason given**.

**This is the only error found in the conservative direction, and it is recorded
as prominently as the flattering ones.** A team that only reports the errors
running against it is not auditing, it is negotiating.

---

## 5. CENSUS — the arithmetic was sound; the tiers being counted were not

**Re-derived independently by parsing the §3 table positionally**, not from the
prose: **37 distinct ids, no duplicates.** The file's recorded
**5 / 1 / 13 / 12 / 6 = 37** is arithmetically correct.

| tier | recorded | **RULED** |
|---|---|---|
| `HOLDS` | 5 | **0** |
| `GATE REACHED` | 1 | **6** |
| `SURVEYED` | 13 | 13 |
| `NOT HELD` | 12 | 12 |
| `NEVER RUN` | 6 | 6 |
| **total** | **37** | **37** |

**§8.3's headline *"One clean gate PASS in the whole family"* SURVIVES as a
statement about a VERDICT** — K0c's frozen comparator did return `PASS` on 20
rows — **and ceases to be a statement about a TIER.** That distinction is exactly
what `THERMAL_TIERING_DIRECTIVE.md` §3 exists to keep, and it is the first time
the directive has done work.

---

## 6. WHAT WAS NOT VERIFIED — stated plainly, because a bounded audit is worth more than a confident one

- **No comparator was re-run.** T1c's `p = 2.005054` is **back-derived arithmetic
  on a stored artifact**, not a re-execution. No tier rests on it.
- **The V-column rubric is an INTERPRETATION, not a measurement.** Whether a
  1980s numerical benchmark (de Vahl Davis) counts as code verification, and
  whether an analytic solution can ever supply P (§1), are rubric questions. They
  are read strictly here, and **that reading is what turns four of the five
  rows.** Overturning §1 restores those four to `HOLDS`. **It is Sanaa's to
  overrule.**
- **K0cG's finest-level plateau was NOT re-derived** from
  `K0cG_runs/S_*_x/postProcessing/`; that is compute-adjacent work not authorised
  for this audit.
- **Plateau tolerances are not stated in four pre-registrations.** T9a, T10a,
  T1b and T1c carry `tol = 1e-6` as a **default inside the comparator**
  (`analyse_t9a.py:191`). Those comparators **were frozen before any case
  existed**, so the criterion is **genuinely pre-committed** — but *a reader
  checking the pre-registration prose alone finds no number.* K0c, K0cS, K0cT and
  K0cX all state theirs numerically. **Recorded as a convention defect, not a
  gate defect.**
- **T1b's ladder is LIVE.** `R_30k_x` and `R_100k_x` are still solving. **S21 is
  `PENDING` in the queue sense** and is not graded here.

---

## 7. WHAT THIS RULING DOES NOT DO

- **It moves no verdict.** Every frozen comparator's output stands as returned.
- It creates, retires and moves **no gate, threshold, band, cap or label**.
- It does **not** settle **D389** (S13 peak-to-peak normalisation) — that
  re-grades the whole corpus and stays on Sanaa's desk.
- It does **not** settle the **§2.1 tier-vocabulary gap**, which is escalated.
- It does **not** settle whether an analytic row can ever hold P — §1 is a
  ruling, and it is **flagged for Sanaa to overrule**, because it is the single
  interpretation on which four tiers turn.
- It authorises **no send**. **SUBMISSIONS REMAIN PARKED.**

---

## 8. FOLLOW-UP, ordered, none of it done here

1. **K0c** — a **third mesh level** is what a Roache triple requires. Wants a
   **new pre-registration**, never an edit to the frozen one.
2. **K0cG** — an **artifacted per-level iterative-convergence monitor at the
   finest level**, under a new pre-registration, before the 43–722× attribution
   may be called grid-established.
3. **K0cT** — correct the denominator 18 → 14 by **quote-and-strike**, applying
   D420's already-established repair; and correct the 73 bare `FAIL` strings to
   `GATE FAIL` per the chief's D-5 ruling.
4. **S19** — record that L1 and L3 are one measurement; withdraw the "no observed
   order" addendum as a persistence artifact.
5. **S18 / §5** — correct the VanGilder & Schmidt 2005 "not held" claim.
6. **Convention note** — plateau tolerances stated **numerically in the
   pre-registration**, not only as a comparator default.

---

## AMENDMENT 1 — 2026-08-25 — I AUDITED §3 AND CALLED IT THE FAMILY. §2 WAS NEVER AUDITED.

**Lines whose number changed above this section: 0.**

**This amendment corrects an error in my own audit, and the error ran in the
flattering direction** — the direction §4 of the ruling above names as this
family's standing prior. **Found by checking a desk item I had raised, not by an
auditor**, but it was mine to find before I reported.

### A1.1 The scope error, stated plainly

The ruling above says **"the thermal family has ZERO rows at `HOLDS`"**. That is
**true of `MATRIX_CONTRIBUTION.md` §3 — the 37 sub-rows — and it is FALSE of the
file.** The file carries **two** tables with a tier column:

| table | rows | `HOLDS` rows | audited by the ruling above |
|---|---|---|---|
| **§3** *Sub-rows inside the occupied cells* | 37 | **5** — S1, S6, S13, S19, S22 | **YES**, all five ruled down |
| **§2** *The 18 cells* | 19 | **4** — C1, C2, C10, C15 | **NO. Never examined.** |

**I audited the sub-rows, found five over-claims, and generalised to "the family"
without checking the cell table sitting eleven lines above it.** The census
`5 → 0` is correct **for §3** and the ruling should have said so.

### A1.2 A cell cannot hold more than its sub-rows — and these four rest on exactly the rows I downgraded

The linkage is not approximate. Each of the four §2 `HOLDS` cells is the cell-level
aggregate of a sub-row the ruling above downgraded:

| cell | rests on | §3 sub-row I downgraded |
|---|---|---|
| **C1** | K0c laminar cavity | **S1** |
| **C2** | T9a solid conduction | **S6** |
| **C10** | T1c `f·Re` / constant-`q″` `Nu` | **S19** |
| **C15** | T10a black box enclosure | **S22** |

**Downgrading a sub-row and leaving its parent cell at `HOLDS` is not a partial
correction, it is an inconsistent record** — and it is the more visible of the
two, because §2 is the summary table a reader reaches first.

### A1.3 Disposition — C1 was ALREADY correct; three were not

**C1 needs no tier correction and I record that rather than claiming a fourth
scalp.** An earlier pass already appended to its tier cell: *"under
`COVERAGE_MATRIX.md` Ruling 3 (`:168-171`) `P SECONDARY` DOES NOT SCORE P, so
this maps to matrix tier `GATE REACHED` (missing P), not HOLDS. The `PASS`
verdict is UNDISTURBED."* **That correction stands and reached the right answer
by a different route than mine** — via `P SECONDARY`, where mine goes via the
missing triple.

**C2, C10 and C15 carry `P ANALYTIC-HELD` and are still tiered `HOLDS`.** Under
**`COVERAGE_MATRIX.md` Ruling 4** — *`P` requires validation against MEASURED
PHYSICAL REALITY; an exact solution scores `V`, never `P`* — **`P ANALYTIC-HELD`
does not score P.** Each therefore holds at most two green columns.

**RULED:**

| cell | was | **now** | missing |
|---|---|---|---|
| **C2** | `HOLDS` | **`GATE REACHED`** | **P** — closed-form composite wall is analytic; no measured reality |
| **C10** | `HOLDS` | **`GATE REACHED`** | **P** — `f·Re` = 64, 48/11 and Graetz `λ₀²` are analytic |
| **C15** | `HOLDS` | **`GATE REACHED`** | **P** — closed-form view factors and the two-surface network are analytic |

**No verdict moves.** Every `PASS` in those cells stands as its frozen comparator
returned it. **All three parenthetical scope caveats stand unaltered** — C2's
*"pure solid conduction only, fluid–solid CHT has NEVER RUN"*, C10's
*"constant-`Ts` `Nu` NOT HELD; turbulent pipe NOT HELD"*, C15's *"ceiling NOT
HELD, grey spheres NOT HELD, participating media NEVER RUN"*.

### A1.4 A SECOND, INDEPENDENT DEFECT IN C1 THAT ITS TIER CORRECTION DID NOT TOUCH

**C1's `V` cell reads:** *"`V YES` — K0c triples CONVERGING, `p` 1.94–2.33 on the
Richardson ladder."*

**Every clause of that is false, and it is the single most concentrated
statement of the K0c defect anywhere in this repository:**

- **"K0c triples"** — K0c has **no triples**. It is **four mesh PAIRS**
  (`Ra1e3_m32/m64`, `Ra1e4_m40/m80`, `Ra1e5_m64/m128`, `Ra1e6_m128/m192`), and
  `gate_k0c.json` carries `gci` 0 / `richardson` 0 / `triple` 0 /
  `observed_order` 0 against a positive control of 4 / 2 / 17 on `gate_t3.json`.
- **"`p` 1.94–2.33"** — those are **K0b's** orders, whose own record states at
  `K0c_RESULTS.md:335` that they *"do not apply to these cases and are not
  used"*; **and the range was NARROWED in the borrowing**, K0b's own table
  running **1.75–2.98**; **and K0b's orders are themselves `NOT A RESULT`**,
  fitted across an iteration-count fork whose effect is **~8× the grid step**
  (`THERMAL_RECIPE_FORK_RULING_2026-08-25.md` §2).
- **"on the Richardson ladder"** — there is no Richardson ladder here to be on.

**C1's tier was corrected for a `P` reason and its `V` claim was left standing.
Correcting a tier does not correct the sentence underneath it**, and a reader
quoting C1's `V` cell today would repeat a three-times-wrong number with a green
label beside it. **`V YES` on C1 is WITHDRAWN**, by quote-and-strike; the text
stays visible, struck, citing this amendment.

### A1.5 What this changes about the headline

**Corrected headline: `MATRIX_CONTRIBUTION.md` carries ZERO rows at `HOLDS` in
EITHER table** — §3's five ruled down by the ruling above, §2's four now
disposed (C1 already, C2/C10/C15 here.)

**The conclusion is unchanged. The evidence for it was half-gathered when I first
stated it**, and that is the part worth recording: **the answer came out the same
is not a defence, because it was not known to come out the same at the time.**

### A1.6 What is unchanged

- **No gate verdict moves.** No gate, threshold, band, cap or label is created,
  moved or retired.
- **§3's census stands: `HOLDS` 0 / `GATE REACHED` 6 / `SURVEYED` 13 / `NOT HELD`
  12 / `NEVER RUN` 6 = 37.** §2's 19 cells are a **different table with its own
  tally** and the two are **not summed** — pooling them would double-count every
  sub-row against its own parent.
- **Ruling 1 (`V` never `P`) stands** and remains **flagged for Sanaa**. It is
  what turns C2, C10 and C15 as well, so **overruling it restores seven rows, not
  four.**
