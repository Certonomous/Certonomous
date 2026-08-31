# R1_F3S_SELECTOR_REPAIR — RESULTS

**Verdict: `PASS`.** All eight gates `G-R1-1` … `G-R1-8` met; none of criteria §8.1–§8.3
applies.

- **Team:** cfd. **Rung id:** `R1_F3S_SELECTOR_REPAIR`.
- **Pre-registration:** `verification/campaign/R1_F3S_SELECTOR_REPAIR_PREREGISTRATION.md`,
  frozen at commit **`f7da1a24ca8c730d5c49a7ea429840c43378bf1e`**, blob
  `f6cd049e6fb10c2080d2c118e7505b4dad26d304`.
- **Spec:** `docs/standards/UNIQUE_SELECTOR_RULE.md` at commit
  **`ae2c8c49366259fe2c5bb8ece09d32bc8017c3f6`**, blob `805547d9d486…`.
- **Control record:**
  `verification/runs/F3_runs/successor_selector_2026-08-28/R1_CONTROL_RECORD.json`.
- **Ran:** 2026-08-30T23:55:42Z → 23:55:50Z, pid/sid 1609903, 1 rank, **7.9425 wall s**.
- **Verdict decided by:** `cfd-supervisor`, personally, 2026-08-31. The driver reports
  control outcomes and refuses rather than degrades; it does **not** award the verdict, and
  its own record says so.

---

## 1. WHY THIS VERDICT IS NOT A RELAY OF THE DRIVER'S SUMMARY

The control record stores each control as a **single truncated summary line** — `C1  FIRED
refused, 2 named: REFUSED: UNIQUE-SELECTOR: expected exactly 1 artifact for fi` — cut at
60 characters. **`G-R1-3` does not ask whether a control "fired". It asks whether the
refusal text contains `UNIQUE-SELECTOR`, the substring `matched   : 2`, and both
basenames.** Those substrings are **not in the record**. Neither is `G-R1-5`'s
`matched   : 0`.

Awarding `PASS` from the summary line would have been believing the instrument's own
report that it complied. **The gates were therefore read against the control source, as
code, by the supervisor** — `SUPERVISION_CHARTER.md` §3 check 1, and the reason it exists.

`selector_controls.py:145-166`, `_expect_refusal`, is what makes "FIRED" load-bearing:

- it requires `SystemExit` with `code == 2` and raises `ControlFailure` on any other code;
- it computes `missing = [s for s in err_substrings if s not in text]` and **raises if any
  required substring is absent**;
- **its final statement is `raise ControlFailure("expected SystemExit(2); the selector
  RETURNED instead")`** — a selector that silently returns a value **fails**, which is the
  precise fake repair §6 of the registration exists to forbid;
- any other exception type also fails.

So the substrings the record omits **are** asserted, in the code path, and their absence
would have raised. `FIRED` carries the gate. **The gap was in the record's display, not in
its evidence** — but that could only be established by reading the code, not by reading the
record.

---

## 2. THE EIGHT GATES, EACH AGAINST WHAT ACTUALLY ESTABLISHES IT

| Gate | Required | Established by | Verdict |
|---|---|---|---|
| **G-R1-1** — positive control fires on **unrepaired** code | old predicate returns `T_ramp.raw` **first**, in the same invocation `c3` (`:193-206`) raises `ControlFailure` unless `old[0] == "T_ramp.raw"`. Record: `old_predicate_first_element = T_ramp.raw`, `old_predicate_full = ['T_ramp.raw','p_ramp.raw','rho_ramp.raw']`, `len = 3` | **MET** |
| **G-R1-2** — defect stops firing on **repaired** code | `select_one(d,"p")` returns basename exactly `p_ramp.raw` | `c3` asserts the basename and raises otherwise. Record: `repaired->p_ramp.raw` | **MET** |
| **G-R1-3** — cardinality refuses | `SystemExit` code 2; stderr carries `UNIQUE-SELECTOR`, `matched   : 2`, **and both basenames** | `c1` (`:173-180`) passes exactly `["UNIQUE-SELECTOR", "matched   : 2", "p_wedgeSurface.raw", "p_rgh_wedgeSurface.raw", abspath(d)]` to `_expect_refusal` — **the gate's list plus the directory path** | **MET** |
| **G-R1-4** — the singleton still passes | returns `p_wedgeSurface.raw`, no exception | `c2` asserts the basename | **MET** |
| **G-R1-5** — negative control | **both** absence fixtures exit 2 with `matched   : 0` | `c4` (`:209-219`) requires `matched   : 0` on N1 (empty dir) **and** N2, and for N2 additionally names `T_ramp.raw` and `rho_ramp.raw` — the entries actually present | **MET** |
| **G-R1-6** — the mutation flips | with `if len(cands) != 1:` → `if False:`, **G-R1-3 and G-R1-5 both flip to failure** | `c5` + `_mutant_module`. Record: `C1 and C4 both flipped`. See §3 — this one was checked hardest | **MET** |
| **G-R1-7** — flag-proof | `python3 -O <driver> --selftest` returns rc **2**; **zero** `ast.Assert` nodes over every shipped file, **counted by AST, never by grep** | `ast_assert_census` walks `ast.parse` trees. Record: `0 ast.Assert over 5 shipped files; -O driver rc=2`. Five shipped `.py` files is the whole successor: `grade_f3s.py`, `run_f3s.py`, `instrument.py`, `selector_controls.py`, `selector_repair_driver.py` | **MET** |
| **G-R1-8** — invariance | §7's named set **bit-identical** before and after | **Re-derived by the supervisor from the disk, not read off the record** — see §4 | **MET** |

**Criteria §8, in order:** §8.1 `BLOCKED` — does not apply; the successor directory and
driver exist and the driver resolved the frozen spec at `ae2c8c49`. §8.2 `NOT A RESULT` —
does not apply; BR-1/BR-2 did **not** refuse (`graded_dir_sha256_match = True`, and the old
predicate was observed firing on producer-written files). §8.3 `NOT A RESULT` — does not
apply; `rc = 0` on **both** shipped modules and **6 of 6** controls `FIRED`, none `NOT RUN`.
§8.4 `GATE FAIL` — does not apply; no gate unmet. **§8.5 `PASS`.**

---

## 3. G-R1-6 WAS CHECKED HARDEST, BECAUSE A MUTATION CONTROL IS THE EASIEST ONE TO FAKE

A mutation test that "flips" for the wrong reason certifies nothing. Three specific ways it
could have been hollow, each closed in the code:

1. **Ambiguous anchor.** `_mutant_module` (`:222-237`) counts the needle
   `"    if len(cands) != 1:"` and **raises unless the count is exactly 1**. A mutation that
   hit some other line, or several, cannot be reported as this mutation.
2. **A flip manufactured by import failure.** The mutant is written **into the successor
   directory** under a pid-bearing name, not into `/tmp`, and the docstring says why: *"A
   mutant imported from /tmp would fail on import and be mistaken for a flip."* The import
   happens **before** the per-control loop, so an `ImportError` propagates out of `c5` as an
   error rather than being counted as a flip.
3. **Stale bytecode inverting the result** — the known trap in which the clean control fails
   and the mutated case passes. The `finally` block removes the mutant `.py` **and** deletes
   its `__pycache__` entries **by name prefix**. `PYTHONDONTWRITEBYTECODE` would not have
   fixed this; removing the files does.

And the flip is required in the right direction: if a mutated control still **passes**, `c5`
raises *"C5 DID NOT FLIP … A guard whose deletion changes nothing was never being
exercised."*

---

## 4. G-R1-8 — THE HASHED SET IS §7's SET, RE-DERIVED ON DISK

The record asserts `n_hashed = 8545`, `changed = []`, `bit_identical = True`. **A count is
not a set**, so the count was reproduced independently:

```
find verification/runs/F3_runs/successor_triple_2026-08-26/ -type f | wc -l   ->  8542
+ docs/standards/UNIQUE_SELECTOR_RULE.md
+ verification/campaign/R1_F3S_SELECTOR_REPAIR_PREREGISTRATION.md
+ scripts/roache_triple.py
                                                              TOTAL   ->  8545
```

**8542 + 3 = 8545, matching exactly**, and `invariance_set()` (`selector_repair_driver.py:117-119`)
composes precisely those four items — the whole fired rung plus the three named singles.
`roache_triple.py` is in the set **because this item must be shown not to have touched the
lab's shared comparator**, not because it is called; §3 of the registration records that it
is not.

The invariance reader itself carries a planted control (`:480-484`, *"the invariance reader,
shown able to see a single changed byte"*), so the zero in `changed` comes from a reader
shown able to report a non-zero — `CLAUDE.md` rule 3.

---

## 5. WHAT THIS PASS DOES AND DOES NOT ESTABLISH

**It establishes** that the `select_one` unique-selector repair, in **both** shipped modules
`grade_f3s.py` and `run_f3s.py`, refuses ambiguity and absence with exit 2 and a message
naming what it saw; that the defect it replaces was **observed firing on files the real
OpenFOAM sampler wrote**, not on hand-made fixtures; and that the fired rung under
`successor_triple_2026-08-26/` was **not touched** — 8,545 files bit-identical.

**It does not establish any physics.** `R1` is an **instrument repair**. It grades no flow,
reproduces no reference, and counts toward no result column. `postProcess -latestTime` is
not time-marching, so three clauses of the strict completion rule (last time == `endTime`,
`ExecutionTime` count == `endTime`, and the age guard in its literal form) **have no
referent here**. They are recorded as having none rather than marked satisfied — a clause
with no referent is not a clause passed.

**BR-1 is the part worth carrying forward.** The birth requirement was implemented as a
*refusal condition*: the instrument grades nothing until the real producer has written the
fixtures **and the defect has been observed firing on them**. The two-member fixture `c1`
reads is a pair the producer emitted — `p_wedgeSurface.raw` and `p_rgh_wedgeSurface.raw`
come from surfaces OpenFOAM named — **not a copy renamed to look like one**. A repair
demonstrated on a fixture where the defect does not fire is a zero from a reader never shown
able to see a non-zero.

---

## 6. COST — ESTIMATE VERSUS ACTUAL (`CLAUDE.md` rule 12)

| | value |
|---|---|
| Predicted | **0.200 core-min** |
| **Actual** | **0.132375 core-min** (7.9425 wall s × 1 rank ÷ 60) |
| **Ratio actual/predicted** | **0.662** |
| Registered cap | 0.300 core-min — **not breached** (44% consumed); no `CAP_OVERRUN.txt` or `ESTIMATE_OVERRUN.txt` exists |
| Dollars | **$0.000113 — DERIVED, NOT MEASURED**, at $0.0513/core-h, c7a.4xlarge, reported-by-owner |
| Waste | **none.** Every artifact the record cites is on disk and re-readable |

**Attribution of the 0.662 gap: misprediction, on the conservative side.** The cost basis
allowed 5.0 s for two scratch case copies and 3.0 s for ~12 python invocations; both came in
under. No contention, no waste. Calibration row filed as **`C-216`** in
`docs/COST_CALIBRATION.md`.

**The box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5), so the dollar
figure is derived at a rate stated by the owner and is never called measured.
