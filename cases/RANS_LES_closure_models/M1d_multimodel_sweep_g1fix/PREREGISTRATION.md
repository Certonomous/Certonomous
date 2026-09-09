# M1d — REGRADE OF THE M1 MULTI-MODEL SWEEP WITH THE G1 ARM-APPLICATION READER REPAIRED

## PRE-REGISTRATION — zero-compute regrade of the 78 M1 runs already on disk

**Status at this commit: FROZEN.** Comparator pinned by sha256 below. No gate,
threshold, ceiling, count, band or label is invented or widened here — all are
**inherited verbatim** from the frozen M1 pre-registration
(`../M1_multimodel_sweep/PREREGISTRATION.md`, freeze `73cd5ac5`) through the M1b
successor (`../M1b_multimodel_sweep_regrade/PREREGISTRATION.md`, freeze
`7dca38f6`). This document exists for ONE reason, of the same class as M1b: the
frozen `grade_m1b.py` cannot reach a believable verdict because its **G1
arm-application log-reader false-fails on every real OpenFOAM log** (proven
below, L-509), and a frozen file is never edited (standing rule 6). The repair
lives in this successor, `grade_m1d.py`, frozen against the same thresholds.

---

## 1. WHY THIS REGRADE EXISTS — THE G1 FALSE-FAIL, PROVEN

The frozen M1b comparator (`grade_m1b.py`, freeze `7dca38f6`) was graded on
2026-09-09. Its C1 repair (L-508) worked — the planted-zero control returned
`passed=True` on the real O(47) donor — but **G1 (arm application) returned NOT A
RESULT on all 78 rows**, every failure tuple `(arm, case, 'log', 'type')`.
Independently triaged by the supervisor from source:

* `MODEL_RE = re.compile(r"Selecting\s+(?:RAS\s+)?turbulence model\s+(\w+)")`
  (`grade_m1b.py:394`, **byte-identical to the frozen `grade_m1.py:224`**),
  applied with `.search()` — first match wins.
* Every real OpenFOAM log in this corpus prints TWO lines, in this order:

      Selecting turbulence model type RAS      <- MODEL_RE matches FIRST, captures "type"
      Selecting RAS turbulence model kOmega    <- the model-specific line, never reached

  so `model_from_log = "type"` on all 78 rows, and G1 flagged a mismatch against
  the (correct) dict model.
* The arm **was applied correctly**: `read_ras_model_from_dict` returns
  `kOmega`/`kOmegaSST` correctly, and the log's own second line names the right
  model. The reader captured a keyword.
* Invisible until now because the M1b synthetic selftest fixture
  (`grade_m1b.py:1105`) wrote ONLY the model-specific line and omitted the
  generic line every real log prints first — the fixture was cleaner than any
  real log — and because frozen `grade_m1.py` always refused at C1 before ever
  reaching G1. Full record: `../M1b_multimodel_sweep_regrade/M1b_GRADE_RESULT_2026-09-09.md`;
  lesson **L-509**.

### 1.1 The repair is a control-robustness fix, NOT a threshold change

The frozen M1 **§7 G1 specification** reads: the arm-application control compares
`RASModel` from the dictionary against *"the model `simpleFoam` reports selecting
in `log.run`."* The intent is the model the solver announces — which is the
model-specific line, not the generic `... model type RAS` line. `grade_m1d.py`
makes the `RAS ` token **mandatory**:

    frozen/M1b:  MODEL_RE = re.compile(r"Selecting\s+(?:RAS\s+)?turbulence model\s+(\w+)")
    M1d:         MODEL_RE = re.compile(r"Selecting RAS turbulence model\s+(\w+)")

This binds `MODEL_RE` to ONLY the model-specific line: it matches
`Selecting RAS turbulence model kOmega` (captures `kOmega`) and does NOT match
`Selecting turbulence model type RAS`, so first-match-wins now lands on the right
line. This changes **only the arm-application log-reader**. It touches **no** gate
value, band, ceiling, count, label, `PLANT`, the C1 predicate (the L-508 repair,
verified byte-identical), or any other channel. It is a repair bringing the
implementation into conformance with the frozen §7 G1 intent — the same
control-robustness class as M1b's C1 fix (`VERIFICATION_CHARTER.md` §2d.1; the
condition is stated above, the check is §4 below and the supervisor's independent
triage).

---

## 2. THE THING BEING GRADED — SAME DATA, ZERO NEW COMPUTE

The 78 M1 runs already exist at
`/home/ubuntu/closure-data/multimodel_sweep/{kOmega,kOmegaSST_null}/`. **No solver
runs. No staging runs. No queue entry.** M1d reads the fields already on disk and
grades them. Legitimate because it inherits M1's pre-registered thresholds rather
than choosing new ones against fields it can already see.

---

## 3. THE GATES — INHERITED VERBATIM FROM FROZEN M1 §7

Supervisor-verified byte-for-byte between `grade_m1b.py` and `grade_m1d.py` on
2026-09-09 (`diff` of the constant block returned no difference):

| constant | value | | constant | value |
|---|---|---|---|---|
| `CAP_ITER` | 20000 | | `G2_CEILING` | 1.0e-2 |
| `CONV_K_TOL`/`CONV_OMEGA_TOL` | 5.0e-6 | | `G2_REFUSE_ABOVE` | 1.0e-1 |
| `G2_BAND` | 1.0e-3 | | `G3_SEPARATION` | 1.0e-2 |
| `G2_MIN_IN_BAND` | 37 | | `G3_MIN_CASES` | 30 |
| `G2_MATCHED_PREFIX` | `"alpha_"` | | `G4_MAX_CAPBOUND` | 8 |
| `G2_UNMATCHED_MAX_OUT` | 2 | | | |

Gate semantics (G0 completion + age guard; G1 arm-application `NOT A RESULT` on
mismatch; G2 null-arm identity with the matched/unmatched partition and the
`>1e-1` sweep-condemnation; G3 arm-separation spread — a spread and only a spread;
G4 cap-bound census) are inherited without alteration. **Standing rule 5 does not
apply** (one mesh per case; the comparator prints that sentence). The C1
planted-zero predicate (L-508 repair) is inherited **byte-identical**
(supervisor-verified).

---

## 4. CONTROLS — INHERITED, WITH THE G1 READER REPAIRED PER §1.1, AND A NEW MODEL-CHANNEL BIRTH LIMB

C1–C6 carried from M1 §6 (C1 with the L-508 tolerance, byte-identical). Every
control refuses via `raise`/`sys.exit(2)`, never `assert` (L-332; the AST check
confirms zero `ast.Assert` nodes). Selftest **66/66** green under `python3` AND
`python3 -O` (supervisor-run 2026-09-09).

Two additions defend the G1 fix (L-314 / §2j on real bytes):

1. **A model-channel planted-failure proof** in the selftest: it confirms the
   FIXED `MODEL_RE` extracts `kOmega` from the real two-line banner, that the
   retained (evidence-only, never-gating) defective predecessor pattern captures
   `type` from the same bytes, and that the fixed pattern does not match the
   generic line. The synthetic fixture now carries the real TWO-line banner, so
   it can exhibit the defect the fix removes.
2. **A §2j birth MODEL limb on REAL producer bytes**: the birth demonstration
   (a precondition of grading, own `m1d_birth` directory since the instrument
   sha256 differs from M1b's) reads the real M1 logs and shows the fixed reader
   extracts a genuine model name where the defective pattern read `type`.
   `verify_birth_record` **refuses (BIRTH-MODEL)** if the model limb is not
   satisfied — a green synthetic selftest is not a demonstration on real bytes.

---

## 5. THE EXPECTED VERDICT, STATED BEFORE THE GRADE READS (rule 2)

From the supervisor's completion census and the M1d dry run (which is NOT a
verdict), the pre-stated expectation is:

* **G1 = PASS** — the arm was applied correctly on every complete row (dict and
  the solver's own model-specific banner line agree); the M1b NOT A RESULT was
  the reader defect, now repaired.
* **G0 = GATE FAIL** — the same 6 incomplete arms (kOmega/{AR_1,AR_7,AR_14}_Ret_180,
  kOmega/PH_Breuer, kOmegaSST_null/{AR_1_Ret_180,PH_Breuer}), named individually
  and excluded from every other gate.
* **G2, G3 = GATE FAIL** because the incomplete arms leave rows missing (a gate
  that cannot see all its rows fails rather than passes); **G4 = GATE REACHED**
  (0 cap-bound).
* **Overall the sweep is GATE FAIL, governed by G0** — a full PASS is not
  reachable until the 6 incomplete arms are re-run (the compute-gated completion
  rung), and this regrade does not pretend otherwise.

Recorded so the grade cannot be read as chosen to fit. The grade's actual verdict
is whatever `grade_m1d.py` prints.

---

## 6. BIRTH RECORD — PROVENANCE FIXED AT THIS COMMIT

The graded result record must state, and the supervisor must verify at grade time:
the grade-script sha256 actually executed (re-hashed, asserted equal to §7's pin);
the data snapshot (`/home/ubuntu/closure-data/multimodel_sweep/`); that no solver
or staging ran; and the §2j birth demonstration (all three limbs — fatal positive,
fatal negative, MODEL) VERIFIED on real bytes from its own `m1d_birth` record.

---

## 7. FREEZE — THE COMPARATOR IS PINNED HERE

* **Comparator:** `grade_m1d.py`
* **sha256 (pinned):** `a1ee190550e94be13fb2fc678379e1c23275b9fd4f002905073776d263628790`
* The grading path is fixed at this pre-registration commit. Before the grade is
  believed, the supervisor re-hashes the file that ran and asserts it equals this
  pin (rule 2); if they differ, the grade is `NOT A RESULT`.
* After this commit the gates are closed. Any departure lands only as a dated
  addendum that cannot alter a gate, threshold, cap or label; originals are
  struck, never rewritten; the addendum asserts `lines whose number changed above
  this section: 0` (rule 6).
* **Supervisor §3 check-1 (the measurement-script diff-read) was performed
  personally on 2026-09-09** before this freeze: MODEL_RE fix correct (RAS
  mandatory, binds only the model-specific line); all 12 gate constants and the C1
  predicate byte-identical to frozen M1b; fixture and §2j birth demonstration
  soundly extended; selftest green under both `-O` modes; zero `ast.Assert`.

---

## 8. COST

* **Solver / staging compute: 0 core-min** — the 78 runs predate this rung.
* **Grading + birth demonstration:** a sub-core-minute read (measured at grade
  time, stated in the result record).
* **Waste carried from M1 (rule 12 §6, MEASURED):** the 6 timeout arms =
  **133.03 core-min** = **$0.114 DERIVED** at $0.0513/core-h (box cannot read its
  own billing; derived, not measured). Reconciled when G0 grades those 6.
* **$0.00 send.** SUBMISSIONS PARKED (standing rule 7).

---

## 9. WHAT M1d STILL CANNOT SEE

Everything M1 §11 could not see, unchanged: the spread is not an error and M1d is
not a validation; no ranking of the two models; no model-form uncertainty from the
spread; no truth comparison (that is M2, separately frozen). M1d repairs the
arm-application reader's robustness on real logs and nothing about what the sweep
can conclude.

---

*Pre-registration authored and frozen by the closure supervisor, 2026-09-09,
after a personal §3 check-1 diff-read of `grade_m1d.py`. The M1d-freeze remains a
heads-up on Sanaa's desk (an internal verdict, not a send).*
