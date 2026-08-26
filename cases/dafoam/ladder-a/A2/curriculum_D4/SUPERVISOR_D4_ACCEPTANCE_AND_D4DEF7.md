# D4 — SUPERVISOR'S ACCEPTANCE RULING, and `D4-DEF-7` in the instrument that graded it

**Written 2026-08-26T03:08:13Z by dafoam-supervisor (twelfth session), personally.** This is
`SUPERVISION_CHARTER.md` §3 check 3 — big-claim verification before belief — and §3 check 1,
the measurement-script read done **as a read of the code**, not as a relay of a lane's report.
D4's `GATE REACHED` is large enough to change this family's direction: D5, D6 and D14 are
queued behind it. So it was defended against its own evidence before it was repeated upward.

**Nothing here is sent, filed, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). **No frozen file was edited** (rule 6). **No gate, threshold, band, cap
or label is altered** (rule 2) — this record strikes an *emitted verdict* on the ground that the
instrument did not perform the registered check, which is the same disposition
`RESULTS.md` §11.6 already applied to G2 band A, and it is **one-way: it can only remove a
`PASS`, never create one.**

---

## 1. THE RULING

> **D4's rung verdict `GATE REACHED` is ACCEPTED.**
>
> **`G1_completion_and_age` is STRUCK from `PASS` and is recorded `NOT ESTABLISHED`.**

D4's answer does not change. **What changes is what D4 is entitled to say it proved.**

## 2. THE FROZEN GRADER EMITS NO ITEM VERDICT — so the rung label is a composition, and I say whose

`d4_grade.py:main()` assembles a `verdicts` dict of **thirteen gate verdicts**, checks each
against `VOCAB`, writes the JSON and exits. **There is no composition function** — not in the
frozen grader and not in `d4_grade_SUPPLEMENT.py`. Nothing in either file maps thirteen gate
verdicts onto one rung verdict.

**Therefore `D4 = GATE REACHED` is a supervisor's POST-COMPUTE composition with no frozen
basis.** Under rule 2 that is legal only if the composition rule applied is the **lab's standing
one** and not a D4-specific rule chosen after the numbers were visible. **It is.** Twelve gates
`PASS`; **G5 — the bright line — `PASS`**; the two-row rule half-satisfied with `SHIPPED`
named `PENDING` rather than dropped. A rung that clears its bright line but cannot claim
toolchain independence is `GATE REACHED` by the standing vocabulary and by nothing bespoke.
**Accepted on that basis and on no other.**

**The gap is real and it is forward-looking, not retrofitted:** this family's pre-registration
template **does not register a composition rule**, so every item in it ends with a supervisor
composing after the fact. **That goes into `docs/dafoam/V_STANDARD_FD_VS_ADJOINT.md` as a
required field for the NEXT registration.** It is not read back into D4, D7R, D8 or D9.

## 3. `D4-DEF-7` — `g_completion()` NAMES THREE CLAUSES AND IMPLEMENTS ONE

**Found by reading the code, not by reading a report.** The docstring is byte-identical in
`d4_grade.py` and `d4_grade_SUPPLEMENT.py`:

> *"Rule 4's field list (`T U p_rgh alphat nut k omega`) is the THERMAL family's and does not
> apply to a compressible DAFoam optimisation. The clauses that DO apply are carried through
> unchanged: rc == 0, a terminal statement from the producer's own log FILE, and the AGE GUARD"*

**Three clauses named. One implemented.** The function's complete set of refusals is:
`age_datum_absent`, `age_reference_absent`, `age_reference_moved`, `arm_absent_from_ledger`,
and an arm-count mismatch. It then writes each arm's `rc` into its output —

```
out["arms"][arm] = {"rc": r["rc"], "core_min": r["core_min"],
                    "oomkilled": r["oomkilled"], "inspect_exit": r["inspect_exit"]}
```

— **and never compares `rc` to zero, anywhere.** There is no terminal-statement check either.
And the verdict line consumes the age half alone:

```
verdicts["G1_completion_and_age"] = ("PASS" if report["G1_age"]["pass"] else "NOT A RESULT")
```

**`report["G1_completion"]` is computed and is consumed by no verdict in either file.**

### 3.1 The consequence is not hypothetical — it is on the graded artifact

`ARMF3_d4_grade_verdict.json` at HEAD carries, simultaneously:

| | |
|---|---|
| `verdicts.G1_completion_and_age` | **`"PASS"`** |
| `report.G1_completion.arms.F.rc` | **`1`** |
| `report.G1_completion.arms.F.inspect_exit` | **`"1"`** |
| `report.G1_completion.arms_required` | `["P1","P2","O","F"]` |

**A gate named for completion returned `PASS` on a run where a REQUIRED arm exited non-zero,
because the clause that would have caught it is not in the code.** `rc: 1` sits in the report
gating nothing. That is worse than the "evidence annotated as non-binding" shape this lab
already knows: here the evidence is not even annotated.

### 3.2 Why the 29/29 selftest could not see it — and this is the durable part

The supplement's battery contains a unit asserting `gate_is("G1_completion_and_age",
"NOT A RESULT")`. **It drives that outcome through a STALE ARTIFACT — the age limb — and never
through a non-zero `rc`.** So the battery proves the age guard fires and is **silent on two
thirds of the gate**, and `29/29 PASS` was read as *"the gate works"*.

This family amended its own ruling on 2026-08-25 to say exactly this, and the amendment is now
turned on the instrument that motivated it:

> ***A guard is only shown to work by making the condition it guards actually occur.***

**Two of three clauses were never made to occur.** A selftest that never drives a clause cannot
distinguish a clause that passes from a clause that is absent.

## 4. WHY THE DISPOSITION IS `NOT ESTABLISHED` AND NOT `GATE FAIL`

The arm that produced the graded FD table is **F3**, ledgered `rc 0`, wall 709 s, 4 ranks,
delivered cores 3.9752, and its seven products were age-asserted **by hand** in `RESULTS.md`
§11.5 against a discriminating datum `1787695606` — 14,049 s later than the carried-over datum —
with **0 of 7 stale**. Arm F's `rc = 1` is the **known, diagnosed `D4-DEF-4` units crash**, a
superseded arm, and it did not contaminate a graded number.

**So the completion of the arm that matters is evidenced — but it is evidenced by a lane's hand
reading, not by the gate.** A gate may not keep a `PASS` it did not earn merely because the
answer would have been the same. **`NOT ESTABLISHED` records precisely that: the check was not
performed, and the record says so instead of implying it was.**

## 5. WHAT IS UNTOUCHED, STATED SO THE STRIKE IS NOT OVERREAD

**G5 — the bright line — stands entirely.** 5 of 5 registered components; aggregate vector-relative
error **0.1634451673004621 %** against band D's **5.0 %**; **zero sign flips**; zero components
without a plateau; zero near-zero. **G6** planted `1.234e-03` and all three consumed channels saw
it, source md5 unchanged either side. **G6b** refused a blind reader. **G7**'s four mutants each
raised their **named** refusal. **G13**'s pinned witness `patchV[0] = 100.0` was **discovered, not
told**, at rel residual exactly `0.0`. **ACC-1** `PASS` at rel `2.33873328108105e-04` inside a
`1.0e-3` band **frozen at `5ed02071` before the primal ran**.

**And the standing limitation is repeated rather than dropped: D4 bought PATCHED ONLY.** `SHIPPED`
is `PENDING` — not run, not failed. The shipped baseline on this case read **1.7138 %** aggregate
with **7 of 96 components beyond 15 %** and **idx18 at −360.75 %**. **D4 cannot claim a
toolchain-independent result and D5, D6 and D14 inherit that qualifier.**

## 6. BLAST RADIUS — measured at HEAD, and the two live graders are ordered to DEMONSTRATE, not count

Swept with `git ls-tree -r HEAD --name-only`, **never `git ls-files`** and never a bare
`git grep` — both read the shared index, which is measured **11.7 % blind** in `cases/dafoam`
(1,949 vs 2,207 files). Reads-`rc` against tests-`rc` across 28 dafoam graders and analysers:

| instrument | reads `rc` | tests `rc` |
|---|---|---|
| `d8_grade.py` | 4 | **0** |
| `d8_grade_entry.py` | 1 | **0** |
| `d9_grade.py`, `d9_grade_SUPPLEMENT.py` | 1 | **0** |
| `d12r_grade.py` (superseded) | 6 | **0** |
| `d12_grade.py` | 1 | **0** |
| `analyse_peak_rss.py` | 4 | **0** |
| `d4_grade.py` / `d4_grade_SUPPLEMENT.py` | 4 / 23 | 1 / 2 *(neither in `g_completion`)* |
| **`d7_grade.py`** | 20 | **2** |
| **`d12x_grade.py`** | 15 | **3** |

**A count is not a demonstration.** Both lanes grading tonight are ordered to **drive a required
arm's ledger `rc` to 1 on a sacrificial copy and show the verdict CHANGE**, under plain
`python3` **and** under `python3 -O` — because `assert`-based guards vanish under `-O`, and
**a selftest that passes under `-O` is the weak test; what matters is whether the REFUSALS FIRE.**

**`D8` is already closed at `GATE REACHED` on `d8_grade.py`, which reads `rc` four times and
tests it zero times. That is named here and is NOT reopened** — the chief's standing bound on the
`-O` and instrument-exposure findings is that settled verdicts are not reopened on this ground and
the remedy belongs in the next registrations. Reopening it would also be the meta-work Sanaa capped
at 20 %. **Naming an exposure and declining to re-audit on it are consistent, and the naming is the
part that must not be skipped.**

## 7. WHAT THIS RECORD DOES NOT CLAIM

- It does **not** claim D4's numbers are wrong. **They are not: the defect did not change the answer.**
- It does **not** claim the other zero-test instruments produced wrong verdicts. **That is NOT
  MEASURED** — only that they cannot say so themselves.
- It does **not** repair anything. **No frozen file was edited**, and any repair reaches this
  family's instruments only through a **next** registration, after I read the diff **as a diff**.
