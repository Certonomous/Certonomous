# Curriculum item D4S-F3S — the A2 wing endpoint FD table under a stationarity acceptance rule, both rows: RESULTS

**Item verdict: `NOT A RESULT`.** Read from this item's own frozen grader, not composed here.
**The FD bright line PASSED on both rows** — ~~**⚠ but both aggregates sit BELOW `VERIFICATION_CHARTER.md:861-863`'s 2.5–5 % harness-sound floor and are therefore claims about the harness; see ADDENDUM 1 at the foot before reading either as a sub-percent verification.**~~ **[⚠ STRUCK 2026-09-03 — ADDENDUM 2. Both aggregates sit below the floor of `VERIFICATION_CHARTER.md` **§2al as amended** (v1.56, `fc8d06e2`); the "claim about the harness" clause was REMOVED from the charter as INVENTED. See ADDENDUM 2.]** The item is `NOT A RESULT` on one limb of one gate —
`G1`'s age clause, on a file this item never produces — and that limb was **unsatisfiable by
construction**.

**Written 2026-09-03 by a dafoam lane, on the dafoam-supervisor's instruction, as this item's FIRST
results record.** `D4S-F3S` ran on 2026-08-27 and has had no record since; `docs/LAB_STATE.md:9139`
listed it as OWED. A reader who came to this directory for the item's conclusion found a grade JSON
and nothing that told them what the item concluded.

> ## THIS IS A SCRIBE'S RECORD, AND THAT CONSTRAINS EVERY NUMBER IN IT
>
> **Nothing here was graded, re-graded, re-derived or computed by the lane that wrote it.** No
> comparator was run, no artefact was written, no preserved run root was modified, no container was
> invoked and **zero solver core-minutes were spent.** Every verdict, gate reading, residual, count
> and cost below is **copied from an artefact on disk and cited to it** by path and by JSON key,
> ledger field or line. Where a figure a reader might want is **not** on record, this document says
> so rather than supplying one.

> ## ⚠ THIS ITEM RAN UNDER A DISARMED ACCEPTANCE CRITERION, AND §5 SAYS SO IN FULL
>
> The instrument **DISARMS** DAFoam's own primal-acceptance clause — `primalMinResTolDiff`
> `1e3` → **`1.0e12`** — and replaces it with a stationarity rule. That was **registered before
> compute**, is **gated by a read-back**, and is the reason **one of the two FD tables below exists
> at all**. A reader must not have to find the pre-registration to learn this, so it is in the
> heading and again at **§5**.

---

# 1. Item verdict — `NOT A RESULT`, **READ FROM THE GRADER, NOT COMPOSED HERE**

| | |
|---|---|
| **verdict of record** | **`NOT A RESULT`** |
| authority | `verdicts.ITEM_two_row_endpoint_fd` = `NOT A RESULT` |
| artefact | `/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3S-a2-wing-cdmin/d4s_f3s_grade_20260827T194848Z.json` |
| the grader | `d4s_f3s_grade.py`, `grader_md5` **`2ed0651c786cb5bd8832f8660ba6c670`** as recorded in that JSON |
| where it is computed | `d4s_f3s_grade.py`, item composition, `PREREGISTRATION.md` §5 |

**THE GRADER DOES COMPOSE AN ITEM VERDICT, AND IT LIVES INSIDE `verdicts`.** This is stated
explicitly because the successor item's record asserted the opposite about the same grader family
and published a hand-composed verdict on that premise; that error is corrected at
`curriculum_D4_SHIPPED_F3SR/RESULTS.md` **CORRECTION 1**. The key is
`verdicts.ITEM_two_row_endpoint_fd`; the four **top-level** keys are `grader_md5`, `registered`,
`report`, `verdicts`, and no item verdict sits among them. **Looking for a top-level key, not
finding one, and concluding no verdict exists is the failure that record made.** Here the verdict
is read from where it lives.

**Two grade runs exist and they AGREE.** `d4s_f3s_grade_20260827T140921Z.json` (in-chain, recorded
in `STATUS.chain` as `grade_rc=0 … note=grader-exit-status-INFRASTRUCTURE-L-342-not-the-verdict`)
and `d4s_f3s_grade_20260827T194848Z.json` (later, same `grader_md5`) both emit
`ITEM_two_row_endpoint_fd` = `NOT A RESULT`, the same `G1` failing limbs and the same `G5`
aggregates to six decimals. **Nothing moved between them**, and both are on disk.

---

# 2. The twenty gate readings — **19 `PASS`, and the one that is not is not the physics**

Read directly from the `verdicts` object, every value tested against the `CLAUDE.md` rule-1
vocabulary with **no assumption that a verdict cell is a dict** — the shape assumption that produced
a false all-clear on the successor item.

| gate | F-S (SHIPPED) | F-P (PATCHED) |
|---|---|---|
| **`G5_endpoint_fd`** — THE BRIGHT LINE | **`PASS`** | **`PASS`** |
| `G_ACC_stationarity` | `PASS` | `PASS` |
| `G6_planted_zero` | `PASS` | `PASS` |
| `G6b_negative_control` | `PASS` | `PASS` |
| `G7_count_refusal_control` | `PASS` | `PASS` |
| `G9_toolchain_identity` | `PASS` | `PASS` |
| `G12_cpu_placement` | `PASS` (delivered 3.9802) | `PASS` (delivered 3.9561) |
| **`G1_completion_and_age`** | **`NOT A RESULT`** | **`NOT A RESULT`** |

plus `G9_two_rows_distinct` `PASS`, `G10_cap_discipline` `PASS`, `G11_memory_envelope` `PASS`.

**THE FD BRIGHT LINE PASSED ON BOTH ROWS**, five of five registered components graded on each
(`n_graded` 5 of `n_registered` 5), **0 sign flips, 0 without plateau, 0 ungradeable, 0 near-zero**:

| row | aggregate vector-relative error | band |
|---|---|---|
| **F-S** (SHIPPED) | **0.350109 %** | 5 % — **⚠ 7.14× BELOW the 2.5–5 % harness-sound floor, see ADDENDUM 1** |
| **F-P** (PATCHED) | **0.163445 %** | 5 % — **⚠ 15.30× BELOW the 2.5–5 % harness-sound floor, see ADDENDUM 1** |

---

# 3. WHY `NOT A RESULT` — `G1`'s age clause fired on a STAGED INPUT, and the clause was unsatisfiable by construction

`rc = 0` on both arms. `oomkilled = false` on both. The terminal clause passed on both. **The single
failing limb is `age_clause_pass`, `n_stale = 1`, and the stale file is `OptView.hst` on both arms.**
From the grade JSON's `report.G1[arm].age_rows`:

| arm | age datum (epoch) | `OptView.hst` mtime | newer than datum? | the other five artefacts |
|---|---|---|---|---|
| **F-S** | `1787838479` | `1787728010` | **`false`** — 30.7 h older | all five **`true`** |
| **F-P** | `1787839128` | `1787689205` | **`false`** — 41.6 h older | all five **`true`** |

**`OptView.hst` IS A STAGED INPUT OF THIS ITEM AND IS NEVER A PRODUCT.** It is the optimiser history
the endpoint is *read from*, copied in by `d4s_f3s_stage_arm.sh` with `cp -a` — mtime PRESERVE — and
**this item runs no optimiser and never writes it**. A file that is never produced can never
post-date the launch, so **the age clause on it could not be satisfied by any run, ever.** The entry
at `d4s_f3s_grade.py:61` was inherited from the optimiser-arm shape, where `D5`'s `SOLVER_ARTEFACTS`
uses the same filename **correctly**, because there it genuinely is a product.

**AND THE 26/26 GRADER SELFTEST COULD NOT CATCH IT.** Its fixture **created `OptView.hst` fresh**
(`d4s_f3s_grade.py:599-601`) against a datum pinned at epoch `1000000000`, so real staging semantics
were never exercised. **A passing selftest is what makes this class dangerous** — the instrument was
green on a fixture that could not reproduce the case.

This defect, its measurement and its repair are the whole reason the successor exists; they are
registered at `curriculum_D4_SHIPPED_F3SR/PREREGISTRATION.md` §1 and §3.3, which also records that
a sweep of eight sibling items came back clean — **across the dafoam corpus this was the only
age-checked entry an item does not produce** — and that `opt_IPOPT.txt`, the same kind of file
carried by the same copy, was **unclassified rather than failing** and is classified in the repair.

**THE VERDICT IS NOT SOFTENED BY ANY OF THAT.** `D4S-F3S` is `NOT A RESULT` and stays so. Its gates
are closed (`CLAUDE.md` rule 2), and rule 5 is one-way: nothing here repairs it. **What the
successor bought is a readable item, not a better verdict for this one.**

---

# 4. The arms — both ran, both `rc = 0`, two rows

| arm | row | image | `rc` | wall s | ranks | core-min | cap |
|---|---|---|---|---|---|---|---|
| **F-S** | SHIPPED | `dafoam/opt-packages:latest` `9d45679d…` | **0** | **577** | 4 | **38.467** | 120.0 |
| **F-P** | PATCHED | `dafoam-idwarp-rot:v1` `2927768a…` | **0** | **561** | 4 | **37.400** | 120.0 |

[MEASURED, `/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3S-a2-wing-cdmin/ledger.txt`, the two
`ARM=` rows.] Both `inspect(exit,oomkilled)=[0 false]`, `memory=12g`, `cpuset=5,6,7,9`,
`enforced_wall_s=1800`. Chain: `arm=F-S rc=0`, `arm=F-P rc=0`, `chain=COMPLETE stamp=20260827T140921Z`.

> **A FIGURE THAT IS EASY TO MISREAD, carried forward from the successor's record because the hazard
> is identical here.** A careless parse of the `ARM=` rows returns `core_min=120.000000` for both
> arms. **That is `enforced_core_min` — the CAP — spliced onto the wrong key.** The measured spends
> are **38.467** and **37.400**.

**Two rows, both present, both distinct** (`G9_two_rows_distinct` `PASS`), so the shape
`DAFOAM_CHARTER.md` §6 requires is available — on an item whose verdict is `NOT A RESULT`.

---

# 5. ⚠ THE DISARMED ACCEPTANCE CRITERION — what it is, why it is here, and exactly what it bought

## 5.1 What was disarmed

`d4s_f3s_fd_endpoint.py:69-70` sets `DISARM_KEY = "primalMinResTolDiff"`,
`DISARM_TOL_DIFF = 1.0e12`, writes it into the exec'd producer's `daOptions`, **reads the effective
value back off the constructed `DASolver`, and REFUSES (rc 2) if it did not take.**

`primalMinResTolDiff` is the **ratio bar** in `DASolver::checkPrimalFailure()`
(`src/adjoint/DASolver/DASolver.C:2744-2752`, quoted verbatim in this lab's own record at
`cases/dafoam/ladder-a/A6/rung_n16_np1/RESULTS.md:79-84`):

    scalar tolMax = daOptionPtr_->getOption<scalar>("primalMinResTolDiff");
    if (daGlobalVarPtr_->primalMaxRes / primalMinResTol_ > tolMax) { … return 1; }

A primal fails iff `primalMaxRes / primalMinResTol > primalMinResTolDiff`, so the effective accept
floor is their product. Printed by the instrument in **both** arm logs of this item, identically:

    D4S_F3S_DISARM primalMinResTolDiff registered_before=1000.0 effective=1000000000000.0 primalMinResTol=1e-08

**The floor moves from `1e-8 × 1e3` = `1e-5` to `1e-8 × 1e12` = `1e+4`** — a level no primal reaching
`endTime` can exceed. The producer's threshold clause **cannot fire**.

*Provenance caveat: the toolchain source was NOT read from the image by the lane writing this record
— no container was invoked. The extract above is this lab's own verbatim quotation, cited by path
and line.*

## 5.2 Why — `D4S-PREREG-DEF-1`, measured rather than argued

| row | endpoint `nuTilda` floor | against the producer's `1e-5` |
|---|---|---|
| PATCHED (`curriculum_D4` F3) | **9.780100659e-06** | accepted, by **2.2 %** |
| SHIPPED (`D4-SHIPPED` F3 r2) | **1.115891818e-05** | rejected, by **11.6 %** |

**A threshold sitting at the instrument's own residual floor decides the arm by which side of the
floor the endpoint lands** (`PREREGISTRATION.md` §1). Both series were stationary to better than
`1e-6` relative over their last 200 iterations. The supervisor's ruling that created this item
**explicitly refused** the alternative — restating the threshold `1e3 → 2e3` — as *"a threshold
moved after seeing which side the endpoint sat on"*, and required one rule applied to **both** rows,
with the PATCHED row **re-bought** so it could not be a SHIPPED-only relaxation.

`d4s_f3s_accept.py` is that rule: per-equation stationarity to `1e-3` relative over the last 200
iterations, continuity `sum local ≤ 1e-6`, everything finite, and **a capture yielding zero
`Time =` lines REFUSES rather than accepts.** It **never compares a residual to a level**, so it is
blind to which side of `1e-5` a floor sits.

## 5.3 Registered by value, and gated

`PREREGISTRATION.md:67` — *"The producer's threshold clause is **DISARMED, not loosened** … set to
`DISARM_TOL_DIFF = 1.0e12` — an accept floor of 1e4 that no primal reaching `endTime` can exceed —
and the EFFECTIVE value is READ BACK from the constructed `DASolver`; if it is not 1e12 the
instrument REFUSES (rc 2)."* `PREREGISTRATION.md:87` makes **`G-ACC`** `PASS` only if *"every capture
re-evaluates ACCEPTED ∧ every instrument record agrees ∧ **disarm read-back = 1e12**"* — and
`G_ACC_stationarity` is `PASS` on both rows.

## 5.4 ⚠ THE BOUNDING MEASUREMENT — the disarm's operational effect is exactly one thing

From the per-primal acceptance records `d4s_f3s_accept.jsonl`, key `r_end`, both arm directories of
this item — **44 primals, 22 per arm**, every one `accepted`:

| arm | row | primals | end residual (`nuTilda`, the worst equation) | against the undisarmed `1e-5` |
|---|---|---|---|---|
| **F-S** | SHIPPED | 22 | **1.116021650e-05** | **all 22 ABOVE** |
| **F-P** | PATCHED | 22 | **9.781615363e-06** | all 22 below |

**Every SHIPPED-row primal would have been rejected by the undisarmed threshold. No PATCHED-row
primal would.** So **the disarm's entire operational effect is that the SHIPPED row's FD table
exists at all.** It buys nothing on the patched path.

*The counts above came from a reader whose first pass returned `primals = 0` on every arm — it read
a key the record does not use. That false zero was caught by a control counting records carrying an
`accepted` field (22 per arm, not 0) and the reader was repaired before any number was written here.
Disclosed under `CLAUDE.md` rule 3.*

## 5.5 And the falsifier registered for exactly this question was **HIT**

`P3` — *"PATCHED reproduces `D4` F3 to printed digits"* — was registered before compute as the test
of whether the disarm changed the answer where the old threshold was already satisfied:

| | |
|---|---|
| `P3_patched_reproduces_D4_F3_to_printed_digits` | **`HIT`** |
| tolerance | `1e-12` relative |
| **`worst_rel_diff` across all five components** | **`0.0`** |
| components | `shape[46]`, `shape[18]`, `shape[0]`, `twist[0]`, `patchV[1]` — each `rel_diff_J_adj` `0.0` **and** `rel_diff_d_hi` `0.0` |
| reference | `curriculum_D4` arm F3, produced under the **undisarmed** `primalMinResTolDiff = 1e3` |

**The PATCHED row, run with the disarm live, reproduces bit-for-bit the table produced under the
threshold. The disarm demonstrably moved nothing where the old threshold was satisfied.**

**What this does NOT licence:** relaxing a convergence criterion anywhere else. What makes this one
admissible is the whole set together — registered by value before compute, justified by a
*measurement* of the residual floor, gated by a read-back that refuses if it did not take, replaced
by a rule that never compares a residual to a level and is applied identically to both rows, and
bounded by a falsifier registered in advance that was hit at `0.0`. **A relaxation missing any one
of those is a different object.**

---

# 6. The four scored predictions

| # | prediction | outcome |
|---|---|---|
| **P1** | both rows: every primal of the sweep accepted under the stationarity rule, and both FD tables exist | **`HIT`** — 22/22 on each row |
| **P2** | SHIPPED `shape[18]` outside band D or sign-flipped → SHIPPED `G5` `GATE FAIL` | **`MISS`** — `shape[18]` came in at **0.10803 % relative error**, in band, plateau met, no sign flip. **The predicted two-row divergence did not happen** |
| **P3** | PATCHED reproduces `D4` F3 to printed digits (the disarm's falsifier) | **`HIT`**, `worst_rel_diff` `0.0` at `1e-12` |
| **P4** | per-arm cost ratio in `[0.8, 1.5]` | **`MISS`** — `F-P` **0.7912**, `F-S` **0.8138** against a predicted 47.267 per arm; both arms cheaper than predicted, `F-P` just outside the band |

**P2's MISS is the substantive scientific content of this item and it is not buried.** The item was
predicted to show the SHIPPED row's FD table failing the bright line. **It did not: both rows passed,
and the shipped row's worst component passed by a factor of ~46 against its band.** Under a
threshold-free acceptance rule the two toolchain rows produce endpoint FD tables that **both** satisfy
the bright line. That is a real finding about the two rows and it is recorded here as one.

---

# 7. COST

| | core-min | note |
|---|---|---|
| F-S | **38.467** | MEASURED, `ledger.txt` |
| F-P | **37.400** | MEASURED, `ledger.txt` |
| **total** | **75.867** | MEASURED; `report.G10.total_core_min` agrees |
| caps | 120.0 per arm | REGISTERED; `cap_equals_registered` `true`, `within_cap` `true`, both arms |
| ceiling | 240.0 | REGISTERED, Σ caps; **0.316×** used |

`G10_cap_discipline` = `PASS`. **Dollars DERIVED, never measured:** 75.867 core-min = 1.26445 core-h
→ **$0.0649** at the owner-stated $0.0513/core-h, `cost_basis` **REPORTED-BY-OWNER** — the box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**A rule-12 calibration row for `D4S-F3S` is OWED and this record does not fabricate one.** The
successor's row is landed (`docs/COST_CALIBRATION.md`, `C-20260831T164216.179599Z-19ea8c16`); this
item's is not, and filing it is a separate act through that file's own append path.

---

# 8. WHAT THIS ITEM MAY NOT CONCLUDE

* **Nothing that repairs its own verdict.** `D4S-F3S` is `NOT A RESULT`; its gates are closed and
  rule 5 is one-way.
* **No claim that the age-clause failure was harmless.** It is a **registration/instrument defect**,
  measured and repaired in a successor, and the verdict stands regardless.
* **No optimality claim, and no attribution of the shipped-versus-patched difference.** The two arms
  ran different images; this chain contains no control that separates an image term from a patch term.
* **No GCI, anywhere** — there is no grid family here.
* **Nothing about the successor's verdict.** `D4S-F3SR` is graded separately; its record and its
  2026-09-03 corrections stand on their own.
* **A `NOT A RESULT` is a result and is reported as one.**

---

# 9. WHAT IS OWED

1. **The rule-12 calibration row** for this item (§7) — owed, not fabricated here.
2. **Nothing else.** This record discharges `docs/LAB_STATE.md:9139`'s standing `RESULTS.md` debt for
   `D4S-F3S`.

**Nothing in this item or this record is filed, sent, emailed, uploaded, posted or commented outside
this box, now or ever** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**

---

# ADDENDUM 1 — 2026-09-03. Both FD aggregates sit **below** `VERIFICATION_CHARTER.md` §7 step 4's harness-sound floor, and this record did not say so

**Ruled by the dafoam-supervisor, 2026-09-03.** Written by a dafoam lane. **NOTHING WAS RE-GRADED
AND NO COMPUTE WAS SPENT** — no instrument run, no artefact written, no run root touched, no
container invoked. **The item verdict does not move: `ITEM_two_row_endpoint_fd` remains
`NOT A RESULT`**, on `G1`'s age clause, exactly as §1 and §3 state. No gate moves. No threshold
moves. This is a **disclosure repair**, landed in the same pass as `CORRECTION 3` on the sibling
record `curriculum_D4_SHIPPED_F3SR/RESULTS.md`, which carries the full treatment.

**What changed above this section, stated so no reader has to diff for it.** Two edits, both
**additive markers appended inside existing lines**, so **lines whose number changed above this
section: 0**:

1. The head sentence *"The FD bright line PASSED on both rows"* now carries the caveat and a pointer
   to this addendum. Its original wording is intact and unreworded.
2. §2's aggregate table's two `band` cells now carry the same pointer. **The two figures themselves
   are untouched.**

Nothing else above this line was altered, and nothing in the repository cites this record by line
number.

## A1.1 THE NUMBERS AND THE FLOOR

~~`VERIFICATION_CHARTER.md:861-863`, the fourth of five reporting-protocol steps, none optional:~~ **[⚠ STRUCK — ADDENDUM 2. Cite `§2al` as amended, not retired line numbers.]**

> ~~*"The harness-sound floor on this stack, for a case with no flagged components, is 2.5 to 5~~
> ~~percent vector-norm relative error. A number below that is a claim about the harness."*~~ **[⚠ STRUCK — ADDENDUM 2. The second sentence was REMOVED as INVENTED; "on this stack" is now "for THIS DATASET".]**

The precondition is met — `n_sign_flips` `0`, `n_without_plateau` `0`, `n_ungradeable` `0`,
`n_near_zero` `0` on both arms — so this row is **inside** the clause's scope.

| row | aggregate, as graded | against the floor's lower edge | restricted to the floor's own warp-chain instrument |
|---|---|---|---|
| **F-S** (SHIPPED) | **0.350109 %** | **7.14× below** | **0.861604 %** (2.90× below) |
| **F-P** (PATCHED) | **0.163445 %** | **15.30× below** | **0.391451 %** (6.39× below) |

[MEASURED. The as-graded values are `report.G5.<arm>.aggregate_rel_err_pct` in
`/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3S-a2-wing-cdmin/d4s_f3s_grade_20260827T194848Z.json`,
grader md5 `2ed0651c786cb5bd8832f8660ba6c670`. The restricted values were recomputed by this lane
from that file's own `report.G5.<arm>.graded` array, on the grader's own reference `d_hi` and the
grader's own statistic `‖J_adj − J_fd‖ / ‖J_fd‖`; the unrestricted recomputation reproduces the
grader's printed value to six decimals, which is what shows the recomputation is on the grader's
convention and not on this lane's.]

~~**Stated plainly, in the form four sibling records already use (`curriculum_D19M/RESULTS.md:99`,~~
~~`curriculum_D19O/RESULTS.md:86-93`, `curriculum_D8/RESULTS.md:322-329`,~~
~~`curriculum_SO3/RESULTS.md:195`): these are claims about the harness, and this record does not claim~~
~~a sub-percent verification of the DAFoam gradient.**~~ **[⚠ STRUCK — ADDENDUM 2: leaned on the invented sentence.]** The floor is **REPORTED, NEVER GATED** — `G5`'s
registered band is 5 % and is unchanged. **This addendum does not argue that the floor does not
apply.**

## A1.2 THE MECHANISM, AND THE SAME-MESH COMPARATOR — the short form; the full treatment is in the sibling record

- **The instrument mix.** `patchV[1]` is `"type": "patchVelocity"` — **angle of attack, a boundary
  condition with no mesh warp in its derivative chain** [MEASURED,
  `/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3S-a2-wing-cdmin/d4_opt_runScript.py` md5
  `2906d52a5dbed2bacbaeaf85a37d3fe8`, `:78-79`, `:166`, `:241`]. It carries **91.37 %** (F-S) and
  **90.87 %** (F-P) of the vector norm's magnitude and has the smallest error of the five, pulling
  the aggregate down by **2.46×** and **2.40×** [MEASURED, same grade JSON]. The floor is calibrated
  *"on shape derivatives through IDWarp"* (`docs/dafoam/V_STANDARD_FD_VS_ADJOINT.md:155`), so a floor
  derived for a warp-chain instrument does not straightforwardly reach an aggregate 90 % dominated by
  a component with no warp chain. **Whether it does is `VERIFICATION_CHARTER.md`'s to rule and has
  been routed to the verification supervisor; it is not ruled here.**
- **The same-mesh comparator.** The floor's source is
  `/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A_stepsize_study.md:89-90` (md5
  `b6fcde0f55e9b357d43140f591db399b`), which rests it on **two** points — A1 at 4,032 cells
  (2.5-3.0 %) and *"A2 independently achieved **1.71 %** at **38304 cells / 96 DVs** — consistent
  with the floor tightening on finer meshes."* **This item runs on 38,304 cells with 96 shape DVs**
  [MEASURED, `F-S_20260827T134911Z_790602.log:207` `Global Cells: 38304`; `adjoint.shape` length 96
  in `F-S/d4s_f3s_fd_endpoint.json`]. **Same rung, same mesh, same shape-DV count as the one data
  point in the floor's own establishing dataset that already sits below the floor.**

## A1.3 A DETERMINISM FACT THIS RECORD IS THE RIGHT PLACE TO CARRY

`D4S-F3S` (2026-08-27) and `D4S-F3SR` (2026-08-31) ran the same two arms with the same frozen
instrument (md5 `9ce78caab9c46d13398ee1d0643cf982`) four days apart. Their FD tables are
**byte-identical**: `d4s_f3s_fd_endpoint.json` md5 **`04742db0af8a28ce26ac9dda2bdd3d22`** (F-S) and
**`3515eb10dcf3c3c58dd90afddd2ecf5a`** (F-P) in **both** run roots, and all 22 per-arm `CD` values
agree to 17 significant figures.

**The control that makes this a determinism statement and not a copied file:** across the same 22
legs, `wall_s` agrees in **0 of 22** — F3S 19.5-21.7 s per primal, F3SR 13.8-15.0 s. **A copied
artefact would carry the wall times too.** [MEASURED, `{F-S,F-P}/d4s_f3s_accept.jsonl` in both run
roots.] The registered falsifier `P6_both_rows_reproduce_D4S_F3S_to_printed_digits` was **`HIT`**
independently of this lane.

**Under `DAFOAM_CHARTER.md` §6 this is a claim about a toolchain, not about arithmetic in general**:
it holds for `dafoam/opt-packages:latest`
(`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`) and
`dafoam-idwarp-rot:v1`
(`sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`), on this case at
`np = 4` with `cpuset=5,6,7,9`, and is **asserted for no other image, rank count or decomposition.**

**Nothing in this item or this record is filed, sent, emailed, uploaded, posted or commented outside
this box, now or ever** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**

---

# ADDENDUM 2 — 2026-09-03. ADDENDUM 1 was written against a clause that has since been amended: the sentence it leaned on was **REMOVED FROM THE CHARTER AS INVENTED**

**Ruled by the dafoam-supervisor, 2026-09-03.** Written by a dafoam lane. **ZERO COMPUTE**, nothing
re-graded, no artefact written, no run root touched, no container invoked. **The verdict does not
move: `ITEM_two_row_endpoint_fd` remains `NOT A RESULT`. No gate moves. No threshold moves.** `G5`'s
registered band is 5 % and is unchanged. 

## A2.1 WHAT HAPPENED, AND IT IS NOT A CHANGE OF MIND

ADDENDUM 1 was drafted and committed (`65709a94`) against
`VERIFICATION_CHARTER.md:861-863` as it then stood. **While it was being drafted, the verification
team amended that clause** — `fc8d06e2`, **`VERIFICATION_CHARTER.md` v1.56, new `§2al`** — and made
three changes:

1. **`"on this stack"` → `"for THIS DATASET"`.** The transcription had widened one study into a
   whole stack.
2. **The n=2 base is RESTORED into the clause**: 2.5-3.0 % at 4,032 cells, and A2's **1.71 % at
   38,304 cells / 96 DVs**, *"consistent with the floor TIGHTENING ON FINER MESHES."*
3. **⚠ The sentence *"A number below that is a claim about the harness"* is STRUCK AS INVENTED.**
   `§2al.2`: it *"APPEARS NOWHERE IN THE SOURCE and is CONTRADICTED BY the source's own SECOND DATA
   POINT, which is BELOW the floor and is read there as CONFIRMING it. On a FINE MESH a sub-floor
   number is WHAT THE ESTABLISHING STUDY PREDICTS, not an anomaly and not a claim about the harness."*

**The third change removes the sentence ADDENDUM 1 quoted and leaned on.** `§2al.2` names the
propagation it caused — two frozen pre-registrations, a grader status string, and at least five
`RESULTS` records. **ADDENDUM 1, written after the referral but before the amendment landed, was a
further propagation of it, and this correction is the lane's own repair of its own record.**

## A2.2 WHAT IS STRUCK ABOVE, AND WHAT SURVIVES UNTOUCHED

**Struck in place, byte-identical inside every `~~…~~`, never reworded or deleted — FOUR sites, all
markers or citations, none a measurement:** the head sentence's pointer marker; A1.1's citation of
the retired line numbers; A1.1's block quotation of the old clause; and A1.1's *"these are claims
about the harness"* sentence. **This record carries no equivalent of the sibling's C3.4 strike — its
§A1.2 never made the "no derivation on its face" claim, so there was nothing there to strike, and
this addendum does not invent a fifth site to match its sibling.** **Lines whose number changed
above this section: 0** — every strike is inline and no line was added or removed.

**EVERY MEASUREMENT IN ADDENDUM 1 STANDS UNCHANGED AND IS RE-AFFIRMED HERE.** Nothing measured
depended on the invented sentence: the aggregates 0.350109 % / 0.163445 %; the restricted
0.861604 % / 0.391451 %; `patchV[1]`'s 91.37 % / 90.87 % share and the 2.46× / 2.40× ratio; the
38,304-cell, 96-shape-DV match to the source study's A2 datum. **The amendment changes what the
charter says about such numbers. It changes none of the numbers.**

## A2.3 THE CAVEAT, RESTATED AGAINST `§2al` AS AMENDED

Following the form of `curriculum_D19O/PREREGISTRATION.md:188` — **its structure, not its wording,
because D19O's own sentence quotes the struck text and `§2al.2` names it as a propagation site.**

* **The harness floor.** `VERIFICATION_CHARTER.md` **`§2al` as amended (v1.56, `fc8d06e2`)**: the
  harness-sound floor **for THIS DATASET**, for a case with no flagged components, is **2.5-5 %
  vector-norm relative error**, on a **stated base of n = 2** — 2.5-3.0 % at 4,032 cells and
  **1.71 % at 38,304 cells / 96 DVs** — and qualified by the mesh, *"consistent with the floor
  tightening on finer meshes."* **Published beside every aggregate. Turning it into a gate would
  convert an honest caveat into a `GATE FAIL` the charter does not authorise.**
* **This item's figures against it:** F-S **0.350109 %**, F-P **0.163445 %**; restricted to the
  floor's own warp-chain instrument, **0.861604 %** and **0.391451 %**. This item runs at **38,304
  cells with 96 shape DVs** — **the mesh and DV count of the amended clause's own second data
  point.**
* **This record does not describe either figure as an anomaly, and does not describe it as a claim
  about the harness.** Under `§2al` as amended, a sub-floor number on a fine mesh is what the
  establishing study predicts.

**WHAT THIS IS, FINALLY.** A **consistency-of-disclosure** repair, and only that: `curriculum_D19M`,
`curriculum_D19O`, `curriculum_D8` and `curriculum_SO3` all carry a sub-floor disclosure on the
artefact's face and this record carried none. **It is not a warning about a `PASS`.** The `PASS` is
untouched, and was never in question.

**Nothing in this item or this record is filed, sent, emailed, uploaded, posted or commented outside
this box, now or ever** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**
