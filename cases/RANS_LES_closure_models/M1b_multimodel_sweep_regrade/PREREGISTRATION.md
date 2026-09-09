# M1b — REGRADE OF THE M1 MULTI-MODEL SWEEP WITH A CONTROL-ROBUSTNESS-REPAIRED COMPARATOR

## PRE-REGISTRATION — zero-compute regrade of the 78 M1 runs already on disk

**Status at this commit: FROZEN.** Comparator pinned by sha256 below. No gate,
threshold, ceiling, count, band or label is invented here or widened here — all
are **inherited verbatim** from the frozen M1 pre-registration
(`../M1_multimodel_sweep/PREREGISTRATION.md`, freeze commit `73cd5ac5`,
grade_m1.py sha256 `b3decc88aca147c9a975bfa21f9ce71ffeac2c34dd34a6943935e20114b78e6e`).
This document exists for ONE reason: the frozen `grade_m1.py` cannot be executed
to a verdict because its C1 planted-zero control **false-refuses on real
velocity data** (proven below), and a frozen file is never edited (standing
rule 6). The repair lives in a **successor comparator**, `grade_m1b.py`, and this
pre-registration freezes that successor against the same thresholds.

---

## 1. WHY A REGRADE EXISTS AT ALL — THE C1 FALSE-POSITIVE, PROVEN

The M1 sweep was graded on 2026-09-09 with the frozen `grade_m1.py`. The
comparator **refused (exit 2) at its C1 planted-zero control, before computing
any gate**. The refusal is a FALSE POSITIVE, independently reproduced by the
supervisor from the frozen source:

* C1 copies a real staged `20000/U`, adds `PLANT = 1.234e-3` to the first
  component of the first internal cell **on disk**, re-reads through the graded
  reader, and takes `seen = max|planted - clean|` over all cells.
* The frozen predicate was `passed = (seen >= PLANT - 1e-15)` — an **absolute**
  1e-15 tolerance (`grade_m1.py:215`).
* The sort-first COMPLETE donor is `kOmega/AR_10_Ret_180/20000/U`, whose first
  cell is `47.0666702943016` m/s. Reading `47.0666702943016 + 1.234e-3` back and
  differencing carries **~3.37e-15** of double round-off (≈ half a ULP at
  magnitude 47) — larger than the absolute `1e-15` slack. The predicate returned
  `False` on a reader that **plainly sees the plant**, and C1 refused.

The reader is **sighted**; the control is what broke, not the instrument's
sight. A control that fires on any O(1)+ velocity donor destroys a legitimate
comparator. Full record: `../M1_multimodel_sweep/M1_GRADE_RESULT_2026-09-09.md`;
lesson **L-508**.

### 1.1 The repair is a control-robustness fix, NOT a threshold change

The frozen M1 **§C1 specification** already reads: *"computes the relative L2
change between the planted and unplanted copies … refuses if the reader does not
see a change **consistent with `PLANT`**."* The frozen *code* discharged that
intent with a one-sided absolute-1e-15 test that does not scale with donor
magnitude. `grade_m1b.py:364` replaces it with a two-sided, magnitude-
independent, PLANT-relative test:

    frozen:  passed = (seen >= PLANT - 1e-15)
    M1b:     passed = (abs(seen - PLANT) <= PLANT * 1e-9)

`PLANT * 1e-9 = 1.234e-12` sits **~360×** above the measured 3.37e-15 round-off
and **~9 orders below** PLANT, so:

* a **blind** reader (`seen = 0`) still refuses — `abs(0 - PLANT) = 1.234e-3 ≫
  1.234e-12` → `passed=False` (control still bites; selftest arm asserts it);
* a **wrong-magnitude** reader refuses;
* a **sighted** reader on the real O(47) donor now passes.

This changes **only the C1 control's read-back tolerance**. It touches **no**
gate value, band, ceiling, count, label, `PLANT`, or reader. It is a repair that
brings the implementation into conformance with the frozen §C1 intent — the same
class as the four-condition repair exception of `VERIFICATION_CHARTER.md` §2d.1
(a control that refuses valid data is an instrument defect, disclosed with its
condition and how it was checked; the condition is stated above and the check is
the selftest fixture below and the independent supervisor reproduction).

---

## 2. THE THING BEING GRADED — SAME DATA, ZERO NEW COMPUTE

The 78 M1 runs (2 arms × 39 cases) already exist on disk at
`/home/ubuntu/closure-data/multimodel_sweep/{kOmega,kOmegaSST_null}/`, staged and
solved under the frozen M1 pre-registration and its `stage_m1.py`/`run_m1.sh`.
**No solver runs for M1b. No staging runs. No queue entry is created.** M1b reads
the fields already on disk and grades them. The regrade is legitimate precisely
because it inherits M1's PRE-REGISTERED thresholds rather than choosing new ones
against fields it can already see (the anti-gaming hazard M1 §7 G5 guards).

---

## 3. THE GATES — INHERITED VERBATIM FROM FROZEN M1 §7

The comparator constants below are **byte-for-byte identical** in
`grade_m1.py` and `grade_m1b.py` (supervisor-verified by direct grep of both
files, 2026-09-09):

| constant | value | M1 §7 origin |
|---|---|---|
| `CAP_ITER` | 20000 | §3 |
| `CONV_K_TOL` / `CONV_OMEGA_TOL` | 5.0e-6 | §4.1 |
| `G2_BAND` | 1.0e-3 | G2 |
| `G2_MIN_IN_BAND` | 37 | G2 |
| `G2_MATCHED_PREFIX` | `"alpha_"` (the 29 iteration-matched hills) | G2 supervisor ruling |
| `G2_UNMATCHED_MAX_OUT` | 2 | G2 supervisor ruling |
| `G2_CEILING` | 1.0e-2 | G2 |
| `G2_REFUSE_ABOVE` | 1.0e-1 | G2 |
| `G3_SEPARATION` | 1.0e-2 | G3 |
| `G3_MIN_CASES` | 30 | G3 |
| `G4_MAX_CAPBOUND` | 8 | G4 |

The gate semantics — **G0** strict completion + age guard (§C4); **G1**
arm-application `NOT A RESULT` on mismatch (§C3); **G2** null-arm identity with
the structural matched/unmatched partition and the `>1e-1` sweep-condemnation;
**G3** arm-separation spread (a spread and only a spread, never an uncertainty,
§8); **G4** cap-bound census — are inherited without alteration. **Standing rule 5
(Roache triple gating) DOES NOT APPLY** (one mesh per case, no triple; §8), and
the comparator prints that sentence in its own output.

---

## 4. CONTROLS — INHERITED, WITH C1 REPAIRED PER §1.1

C1 (planted zero, repaired tolerance), C2 (the null arm), C3 (arm application
read from two independent places), C4 (strict completion + age guard), C5
(physics-critical vs infrastructure fields), C6 (`0/nut` uniform-0) are all
carried from M1 §6. Every control refuses via `raise`/`sys.exit(2)`, never an
`assert` (L-332), and each ships its L-314 planted-failure proof. The selftest
runs under `python3` **and** `python3 -O`; both are green (supervisor-run
2026-09-09).

The C1 selftest fixture is extended per L-508 to cover the exact gap that hid the
bug: it exercises (a) a BLIND reader (must report `passed=False`), (b) a SIGHTED
reader on an **O(47)** donor with first cell `47.0666702943016` (must report
`passed=True`), and (c) the live control on the real O(47) donor when present.

---

## 5. THE EXPECTED VERDICT, STATED BEFORE THE GRADE READS (rule 2)

The supervisor's completion census (corroborating, from the six arms' own time
directories) found **6 of 78 arms INCOMPLETE**: each holds only `0/` and
`0.orig/`, no `20000/` — `rc=124` wall-timeout:

    kOmega/AR_1_Ret_180, kOmega/AR_7_Ret_180, kOmega/AR_14_Ret_180,
    kOmega/PH_Breuer, kOmegaSST_null/AR_1_Ret_180, kOmegaSST_null/PH_Breuer

Therefore the pre-stated expectation is:

* **G0 = GATE FAIL** — the 6 incomplete arms are named individually and excluded
  from every other gate (they are printed beside each gate they are excluded
  from, never dropped silently).
* **G2, G3, G4 compute on the complete rows** (72 arms; G2 on the complete
  `kOmegaSST_null` subset, G3 on cases where both arms completed, G4 census over
  all complete rows).

This expectation is recorded so the grade cannot be read as chosen to fit. The
grade's actual verdict is whatever `grade_m1b.py` prints.

---

## 6. BIRTH RECORD — PROVENANCE FIXED AT THIS COMMIT

The graded result record must state, and the supervisor must verify at grade
time:

1. The **grade script sha256** actually executed, re-hashed at run time and
   asserted byte-identical to the pin in §7 below.
2. The **data snapshot** graded: `/home/ubuntu/closure-data/multimodel_sweep/`,
   with its `STAGING_MANIFEST_M1.json` present.
3. The **frozen-comparator lineage**: grade_m1b.py inherits grade_m1.py's gates
   verbatim; the only functional divergence is the C1 predicate of §1.1.
4. That **no solver and no staging ran** for M1b (zero-compute, confirmed by the
   fields' mtimes predating this commit).

---

## 7. FREEZE — THE COMPARATOR IS PINNED HERE

* **Comparator:** `grade_m1b.py`
* **sha256 (pinned):** `70ada1b742659ab94799de6e99cba43f8e16d4b736d3283927da67f5dd07ca33`
* The grading path is fixed at this pre-registration commit. Before the grade is
  believed, the supervisor re-hashes the file that ran and asserts it equals this
  pin (rule 2). If they differ, the grade is `NOT A RESULT`.
* After this commit the gates are closed. Any departure lands only as a dated
  addendum that cannot alter a gate, threshold, cap or label; originals are
  struck, never rewritten; the addendum asserts `lines whose number changed
  above this section: 0` (rule 6).

---

## 8. COST

* **Solver / staging compute: 0 core-min** — the 78 runs predate this rung; M1b
  reads them.
* **Grading compute:** a sub-core-minute read of populated fields (measured at
  grade time, stated in the result record).
* **Waste carried from M1 (rule 12 §6, MEASURED, not absorbed):** the 6 timeout
  arms cost **133.03 core-min** = **$0.114 DERIVED** at $0.0513/core-h (the box
  cannot read its own billing; derived, not measured). This waste is attributed
  to the M1 solve phase, reconciled at this regrade when G0 grades those 6 arms.
* **$0.00 send.** SUBMISSIONS PARKED (standing rule 7).

---

## 9. WHAT M1b STILL CANNOT SEE

Everything M1 §11 could not see, unchanged: the spread is not an error and M1b is
not a validation; no ranking of the two models; no model-form uncertainty from
the spread; no truth comparison (that is M2, separately frozen). M1b changes the
C1 control's arithmetic robustness and nothing about what the sweep can conclude.

---

*Pre-registration authored and frozen by the closure supervisor, 2026-09-09,
under the chief's dispatch of the M1b increment and Sanaa's standing
"all teams continue per our standards". The M1b-freeze heads-up remains on
Sanaa's desk as awareness (this is an internal verdict, not a send).*
