# heat-transfer territory — the `-O` `assert` inventory, **RE-DERIVED**, classified, and sequenced

**Written by a `lab-lane` under `heat-transfer-supervisor`, 2026-08-26.**
**ZERO COMPUTE.** **FORWARD-ONLY: no settled verdict is reopened by this file and
no frozen instrument is edited by it.** **Nothing has been sent, filed,
submitted, uploaded, registered or posted outside this box (`CLAUDE.md` rule 7).**

---

## 0. The bound this inventory operates under, quoted so it cannot drift

From the chief's bound of 2026-08-25T22:48Z:

> The `-O` exposure is **LATENT, NOT LIVE**: no run script in the repository
> invokes `python3 -O`, `PYTHONOPTIMIZE` is unset on the host, and
> `__debug__ = True` / `PYTHONOPTIMIZE = None` was measured inside the DAFoam
> container too. **No graded verdict on record was produced under `-O`. EXISTING
> VERDICTS ARE NOT REOPENED BY THIS FINDING. THE REMEDY BELONGS IN THE NEXT
> REGISTRATIONS.**

A re-audit of settled verdicts on this ground is the meta-work Sanaa capped at
20 % and **is not authorised**. This file produces an inventory, a sequence and
specified forms. **It changes no instrument.**

## 1. THE ENUMERATION DEFECT, MEASURED — `git ls-files` IS BLIND TO THE WORST CASES

The population was re-derived from **`git ls-tree -r HEAD --name-only`**, parsing
each blob with `ast.parse` and counting `ast.Assert` **nodes** — never `grep`,
because `analyse_t8.py:652` is a docstring containing the word `assert` and is
not a node.

**`git ls-files` reads the shared INDEX, which decays under this lab's
private-index protocol.** Measured 2026-08-26 over the five territory roots:

| enumeration | `.py` files found |
|---|---|
| `git ls-tree -r HEAD` over the three `verification/runs/` roots | **113** |
| `git ls-tree -r HEAD` over all five territory roots | **115** |
| `git ls-files` over the three `verification/runs/` roots | **109** |
| `git ls-files` over all five territory roots | 111 |

**The index is missing FOUR tracked `.py` files that HEAD has, all under
`verification/runs/T-family/`:**

- **`T8_runs/analyse_t8.py`** — the file carrying the territory's **exemplar
  Class A assert**;
- **`T8_runs/build_t8.py`**;
- **`T1_runs/planted_zero_control_t1b.py`** — a **standing-rule-3 planted-zero
  control**;
- **`safe_append.py`**.

> **A sweep enumerated with `git ls-files` would have missed the single most
> serious `assert` in the territory AND a planted-zero control — the two file
> classes the sweep exists to protect. The blind spot is not random: it is
> exactly the recently-committed files, which are exactly the ones a sweep is
> most likely to be about.**

**The 113 / 115 discrepancy is explained, not split:** 113 counts the three
`verification/runs/` roots; 115 adds
`docs/campaigns/F14-cooling-ladder/compute_reference_metrics.py` and
`digitize_wibron2018.py`. **Neither carries an `Assert` node**, so the assert
population is **35 in 17 files either way** — the relayed figure is confirmed,
and the denominator is stated with its root set rather than left ambiguous.

## 2. THE CLASSIFICATION — and it disagrees with the relayed one in two places

| class | definition | count |
|---|---|---:|
| **A** | an evaporated assert can change a **VERDICT** | **11** |
| **B** | an evaporated assert produces a **silently wrong ARTIFACT** | **23** |
| **C** | a genuine sanity check | **0** |
| **D** | a **tautology / non-check** — reads as protection, performs none | **1** |
| | **total** | **35** |

**Disagreement 1 — the relayed split was "33 guards + 2 sanity checks". I find
no genuine sanity check at all.** Every one of the 35 sits in a position where
something depends on it; the two nearest candidates (`build_t10a.py:60`
`assert WRITE_INTERVAL < END_TIME` and `:168` `assert nz * 2 == N`) are still
build-time guards on a generated case and belong in Class B. Because the relayed
figure did not name which two it meant, **this is a disagreement I can state but
not map**, and it is reported rather than reconciled.

**Disagreement 2 — the relayed "21 build-time guards" is reconciled exactly, and
the reconciliation is worth keeping.** 21 is the count in files named
`build_*.py`. My Class B is **23** because it also contains the two guards in
`T9aH_runs/check_t9aH_mesh.py` (lines 50, 52), a **mesh-check** script rather
than a build script — same failure mode, different filename prefix. **A census
keyed on filename prefix undercounts by exactly the files that check rather than
build.**

**Class D exists because Class C would have flattered the population.** A
tautological assertion is **not** a sanity check — it is a non-check, and folding
it into C or A gets the severity wrong in opposite directions. See §3.1.

## 3. CLASS A — every instance, by path and line

| # | path : line | what evaporates under `-O` | why a verdict can move |
|---|---|---|---|
| A1 | `verification/runs/T-family/T8_runs/analyse_t8.py:1054` | the **rule-5 one-way gate** in `grade_row()` | **THE EXEMPLAR.** Measured: mutated to emit a forbidden verdict, plain `python3` gives `AssertionError` rc 3; `python3 -O` returns **`GATE REACHED` rc 0**. |
| A2 | `verification/runs/T-family/T9aH_runs/analyse_t9aH.py:270` | restoration guard on the **frozen** `exact_t9a.WALL_LAYERS` after an in-memory override | if the restore silently fails, **every later call to the frozen exact reference uses the wrong conductivity**. The comparator would grade against a reference it thinks is frozen and is not. |
| A3 | `verification/runs/T-family/T9aH_runs/analyse_t9aH.py:291` | same, for `analyse_t9a.REG["wall"]["layers"]`, **inside a `finally:` block** | same mechanism, and a `finally:` guard is the one a reader is least likely to re-check. |
| A4 | `verification/runs/T-family/T10a_runs/exact_t10a.py:296` | polygon **inward-orientation** guard in the analytic reference module | `analyse_t10a.py:72` imports it as `EXACT`. A sign-flipped patch normal makes **the exact reference itself wrong in sign** on that patch — the value a verdict is measured against. |
| A5 | `verification/runs/T-family/T3_runs/digitise_t3_secondary.py:190` | axis-calibration guard (`y-axis not at x/H = 0`) | this script **produces the reference data** (`T3_secondary_digitisation.json`). A mis-calibrated axis yields a silently wrong reference. |
| A6 | `verification/runs/T-family/T3_runs/digitise_t3_secondary.py:191` | axis-calibration guard (`x-axis not at −0.002`) | same. |
| A7 | `verification/runs/F14-cooling-ladder/K0b_D403_rerun/analyse_k0b_mesh.py:270` | **near-identity cross-check** between the grid-mapped Nusselt estimator and the x-fastest-ordering shortcut | it sits in the function that **returns the graded `Nu_avg_hot`**. If the two orderings disagree, the returned Nusselt is from the wrong one and nothing says so. |
| A8 | `verification/runs/F14-cooling-ladder/K0b_D406_repair/analyse_k0b_mesh.py:270` | same | same. |
| A9 | `verification/runs/F14-cooling-ladder/K0b_mesh_sensitivity/analyse_k0b_mesh.py:350` | same | same. |
| A10 | `verification/runs/THERMAL_K0_runs/analyse.py:67` | reader shape check `len(nums) == 3*n` on a **vector** `internalField` | a mis-parsed field is **silently reshaped** and every number downstream is wrong. This is the truncating-reader class reached through the interpreter. |
| A11 | `verification/runs/THERMAL_K0_runs/analyse.py:69` | reader shape check `len(nums) == n` on a **scalar** `internalField` | same. |

**A5–A6 are a judgement this lane makes explicitly rather than silently.** They
do not match the supervisor's Class A exemplars (comparator gates, rule-5 guards,
planted-zero controls, completion/age-guard limbs), but they cannot be Class B
either: **Class B's defining property is that the failure surfaces downstream as
a broken or refused solve, and a wrongly-digitised reference surfaces as nothing
at all — it surfaces as a wrong verdict.** Classified by **effect on a verdict**,
which is the class definition, not by which script it lives in.

**A7–A9 are the §2d.1 instrument class.** A near-identity that grades nothing is
exactly the *"instrument INDEPENDENT OF THE HYPOTHESIS"* §2d.1 condition (2)
requires. **Writing that instrument as an `assert` makes the lab's own
error-finding mechanism removable by a command-line flag.**

## 3.1 CLASS D — the single instance, and why it needs its own class

**`verification/runs/T-family/T8_runs/analyse_t8.py:1329`.**

```
1325:            rec["verdict"] = VERDICT_NAR
1326-1328:       rec["why"] = ("control C1 failed: ...")
1329:            assert rec["verdict"] in (rec["band"], VERDICT_NAR)
```

`rec["verdict"]` is **assigned** `VERDICT_NAR` two lines above, and `VERDICT_NAR`
is unconditionally a member of the tested tuple. **It cannot fail under `-O`, and
it cannot fail under plain `python3` either.** Nor is it a latent `KeyError`:
`rec["band"]` is set unconditionally at `:1031`.

> **AN ASSERTION PLACED IMMEDIATELY AFTER THE ASSIGNMENT THAT SATISFIES IT IS A
> CHECK OF NOTHING.** It is **L-332's shape in its assertion form** — L-332 says
> never put an unconditional success `print` after a check, because deleting the
> check leaves the claim. Here **there was never a check to delete; the claim was
> standing alone from the start.**

**Counting it as a Class A guard overstates the guarded surface by one AND
understates the unguarded surface by one — it flatters the file in both
directions at once.** Counting it as Class C would call a non-check a sanity
check. It gets its own class, and the population is stated as
**11 A / 23 B / 0 C / 1 D**, never as "33 guards".

Full disclosure: `docs/campaigns/T-family/T8_PREREGISTRATION.md`, Amendment A2
(2026-08-26, post-compute, disclosure only, v1.1 → v1.2).

## 4. THE REMEDIATION SEQUENCE — Class A first, and **nothing in this territory is editable today**

**Sequence: A1 → A2/A3 → A4 → A7–A9 → A10/A11 → A5/A6 → Class B → Class D.**
Class A first because its output is *a wrong ANSWER that looks graded*; Class B
after, because its failure surfaces downstream as a broken or refused solve.

**AND THE DELIVERABLE COLLAPSES TO A DISCLOSURE, FOR A REASON WORTH STATING.**
The brief asked for repaired forms *"for instruments that are NOT frozen"*.
**Checked, per instrument: there are none in Class A.** Every Class A instance
sits in a comparator or reference module under a rung that has both a committed
`*_PREREGISTRATION.md` and a `*_RESULTS.md` — T8, T9aH, T10a, T3, K0b (D403
rerun, D406 repair, mesh sensitivity) and THERMAL_K0. Editing any of them is a
**grading-path change after first compute**, forbidden by `CLAUDE.md` rule 2 and
`VERIFICATION_CHARTER.md` §2d.

**And §2d.1 does not rescue it** — the same reasoning as Amendment A2 §A2.3.
Its conditions (3) *quantify what moved* and (4) *record pre-repair values beside
published ones* are **vacuous** for an `assert` → `sys.exit(2)` conversion, which
under plain `python3` refuses in exactly the same state. **There is nothing to
quantify.**

> **INVOKING A NARROW EXCEPTION WHERE IT IS NOT NEEDED STRETCHES IT, AND A
> STRETCHED EXCEPTION IS HOW THE NEXT REAL ONE GETS WAVED THROUGH.**

So for **all eleven** Class A instances the remedy is identical and is the §A1
pattern: **a dated foot-amendment disclosing the defect, plus the repaired form
specified for the successor.** A1's amendment is landed. **A2–A11 are owed the
same amendments, and this lane has not written them** — each belongs at the foot
of its own rung's record and each needs its rung's freeze state verified first.
**That is named as outstanding rather than reported as done.**

## 5. THE REPAIRED FORM, SPECIFIED — three arms, adopting the shape cfd already registered

Per §4b.3's rule that the territory **adopts an existing registered shape rather
than invent one**, this is cfd's adopted three-arm shape
(`verification/campaign/CFD_ASSERT_RULE_REFINEMENT_2026-08-25.md` §1), not a new
one:

1. **Refusals `raise` or `sys.exit(2)`, never `assert`** — and the runtime guard
   becomes the **primary** check, with behavioural coverage as a second arm.
   §4e.4 establishes why coverage cannot substitute: `analyse_t8.py:1659-1668` is
   `ok(...)`-based and survives `-O`, **but lives inside `selftest()` and does not
   run during grading.** A test is not a runtime guard.
2. **Every registered refusal DRIVEN under `python3 -O` and shown to FIRE
   identically**, against a sacrificial mutant, on the guarded path. **Not "the
   selftest passes under `-O`"**: a passing selftest exercises the clean path, and
   the clean path is the one an evaporated guard still walks. **A mutation battery
   cannot see this hole unless the battery is itself run under `-O`, because the
   battery and the hole live under different flags.**
3. **A statement-type check over the instrument's own AST requiring ZERO `Assert`
   nodes**, catching a revert **without running anything**. Arms 1 and 2 prove
   refusals fire *today*; only arm 3 catches the *later edit*, because a selftest
   exercising the clean path passes either way.
4. **Class D's shape is forbidden outright**: no check may be placed immediately
   after the assignment that satisfies it.

### 5.1 Arm 3 is now a committed instrument: `scripts/check_assert_guards.py`

**Arm (c) was the one the cfd supervisor called *"the one I would not have thought
of and the cheapest of the three"*, and until now no committed instrument
implemented it.** This one does.

- `--require-clean <path>…` is the **gate** form: rc 0 when every named file has
  zero `Assert` nodes, **rc 2 — a refusal, not an exception —** when any does.
- `--root <prefix>…` enumerates from **`git ls-tree -r HEAD`**, never
  `git ls-files`, with §1's measurement quoted in the source as the reason.
- **It contains zero `assert` statements and applies the check to itself.**
- **Its selftest carries a planted control (rule 3):** it writes a sacrificial
  fixture containing one `assert`, and **refuses if the checker cannot see it** —
  a clean report from this checker is only evidence because the checker is shown
  able to report a dirty one. It also verifies that a **docstring containing the
  word `assert` is NOT counted**, because the check is on statement type.
- **Arm 2 is built into arm 3's own selftest:** it re-invokes itself under
  **`python3 -O`** against the dirty fixture and requires **rc 2 under both
  interpreters**. Measured, both flags: `4 arms, 0 FAILED`, rc 0.
- Every success print sits **inside the passing branch** (L-332).

**Driven against the territory:** `scanned 115 file(s) from HEAD: 35 ast.Assert
node(s) in 17 file(s)` — reproducing §1 and §2 from the committed instrument
rather than from a one-off script. **Driven against the exemplar:**
`--require-clean verification/runs/T-family/T8_runs/analyse_t8.py` → **rc 2**,
naming `:1054` and `:1329`.

**Filing note, flagged rather than decided:** the instrument is placed in the
shared `scripts/` directory (`FILING_CHARTER` R3, `lower_snake.py`) because the
defect is lab-wide and cfd, dafoam, closure and ansys-verification all have open
work on it. **It sits outside heat-transfer's territory and this lane does not
claim it for the team.** Whether it is adopted lab-wide, rehomed, or wired into
`scripts/check_harness.py` is for the verification and cfd supervisors.

## 6. Cost

**Zero core-minutes.** AST parsing and sub-second `-O` drives on the login box.
No solver was launched. `docs/COST_CALIBRATION.md` gains no row: there is no
compute to calibrate.

---

## 7. ADDENDUM, same day — the ten owed amendments: **EIGHT WRITTEN, THREE HAVE NOTHING TO AMEND**

§4 named A2–A11 as owed and not written. **Eight of the eleven Class A instances are now
disclosed.** The remaining three produced a finding of their own.

### 7.1 Written

| instances | record amended | commit |
|---|---|---|
| A2, A3 — `analyse_t9aH.py:270`, `:291` | `docs/campaigns/T-family/T9aH_PREREGISTRATION.md` | `080095bd` |
| A4 — `exact_t10a.py:296` | `docs/campaigns/T-family/T10a_PREREGISTRATION.md` | `b2a13fd6` |
| A5, A6 — `digitise_t3_secondary.py:190`, `:191` | `docs/campaigns/T-family/T3_PREREGISTRATION.md` | `196c9ba5` |
| A7 — `K0b_D403_rerun/analyse_k0b_mesh.py:270` | `docs/campaigns/F14-cooling-ladder/K0b_D403_RERUN_PREREGISTRATION.md` | `9a16a899` |
| A8 — `K0b_D406_repair/analyse_k0b_mesh.py:270` | `docs/campaigns/F14-cooling-ladder/K0b_D406_REPAIR_PREREGISTRATION.md` | `efa53c8a` |
| A1 — `analyse_t8.py:1054` | `docs/campaigns/T-family/T8_PREREGISTRATION.md` (Amendment A2) | `40adda9f` |

Each is a dated foot-amendment, **v1.0 → v1.1** (T8: v1.1 → v1.2), post-compute,
disclosure only, altering no gate, threshold, cap or label, reopening no verdict, and
editing no instrument. **The rule-6 assertion `lines whose number changed above this
section: 0` was MEASURED in every case** — each file was rebuilt from its blob at
`HEAD` plus the amendment, and the prefix compared byte-for-byte before the commit was
allowed (821 / 525 / 513 / 222 / 295 / 630 lines respectively). **A claimed assertion
and a measured one are different artifacts, and this is the measured one.**

**A version convention was introduced and is stated rather than assumed:** none of the
five records outside T8 carried an explicit version string. Each amendment names the
document **v1.0 as it stood** and takes it to **v1.1**, and says so in its own text, so
that no earlier version is implied to have existed.

### 7.2 **A9, A10 AND A11 HAVE NO REGISTRATION TO AMEND — AND THAT IS THE FINDING**

| instance | instrument | record to amend |
|---|---|---|
| **A9** | `verification/runs/F14-cooling-ladder/K0b_mesh_sensitivity/analyse_k0b_mesh.py:350` | **NONE EXISTS** |
| **A10** | `verification/runs/THERMAL_K0_runs/analyse.py:67` | **NONE EXISTS** |
| **A11** | `verification/runs/THERMAL_K0_runs/analyse.py:69` | **NONE EXISTS** |

Searched: there is **no `K0b_MESH_SENSITIVITY_PREREGISTRATION.md`** and **no THERMAL_K0
pre-registration of any kind** in `docs/campaigns/`. `THERMAL_K0_runs/analyse.py` appears
in `docs/FAIL_OPEN_GATE_AUDIT.md:509` and in `CHECKPOINT_GATE_AUDIT_2026-08-25.md` — **in
audits of it, never in a freeze set naming it.**

> **AN INSTRUMENT WITH NO PRE-REGISTRATION HAS NO FOOT TO APPEND A DISCLOSURE TO. The
> `-O` exposure is the smaller problem here: the larger one is that the disclosure
> mechanism this lab relies on ASSUMES a registration exists, and for these two
> instruments it does not.**

**Inventing a record to hold the disclosure would be worse than naming the gap**, because
a pre-registration written after the compute is not a pre-registration — it is a
document with a misleading name, and rule 2's entire evidentiary content is the freeze
that these would not have.

**Referred upward, not resolved here.** Whether these two instruments are retrospectively
registered (they cannot be), retired, superseded by a registered successor, or simply
recorded as unregistered legacy is a **supervisor's call at minimum** and touches
`VERIFICATION_CHARTER` §2d's scope. **This lane states the gap and stops.**

**Neither instrument is re-graded and no verdict resting on either is reopened** — the
2026-08-25T22:48Z bound holds regardless of whether a registration exists to disclose
against.
