# M1b MULTI-MODEL SWEEP REGRADE — GRADE RESULT, 2026-09-09

## VERDICT: NOT A RESULT (G1 arm-application control cannot verify the log channel)

The C1 repair that motivated M1b **WORKS**: the planted-zero control now returns
`passed=True` on the real O(47) donor (`read_back_delta = 0.0012339999999966267`
on `kOmega/AR_10_Ret_180/20000/U`). L-508 is validated on real data. But running
the comparator to the gates for the first time exposed a **second inherited
comparator defect**, in the G1 arm-application log-reader, that the frozen
`grade_m1.py`'s C1 refusal had been masking all along. Under the frozen G1 rule
(§7: *"otherwise the whole sweep is NOT A RESULT — not GATE FAIL"*), the sweep is
**NOT A RESULT** — but the cause is the instrument, not the physics, and this
record discloses that in full.

## BIRTH RECORD (rule 2 / prereg §6, supervisor-verified)

* **Instrument sha256 executed:** `70ada1b742659ab94799de6e99cba43f8e16d4b736d3283927da67f5dd07ca33`
  — re-hashed at run time, **byte-identical** to the freeze pin
  (`PREREGISTRATION.md` §7, freeze commit `7dca38f6`). Grade is of the frozen file.
* **Section 2j birth demonstration: VERIFIED.** Positive limb 3/3 real crashed
  solver logs read `fatal=True`; negative limb 4/4 real clean logs read
  `fatal=False` while all 4 carry the trapFpe banner (a reading, not an empty
  population). Record at `/home/ubuntu/closure-data/m1b_birth/`.
* **Data snapshot graded:** `/home/ubuntu/closure-data/multimodel_sweep/`
  (`STAGING_MANIFEST_M1.json` present), 78 fields, mtimes predate this commit.
* **No solver, no staging ran.** Zero-compute regrade.

## GATE-BY-GATE

| gate | verdict | key numbers |
|---|---|---|
| **C1** planted zero | **PASS** (repaired) | `passed=True`, read-back delta 0.0012339999999966267 on the O(47) donor |
| **G0** completion + age guard | **GATE FAIL** | 72/78 complete; 6 incomplete named below |
| **G1** arm application | **NOT A RESULT** | n_bad=78, every one `(arm, case, 'log', 'type')` — an instrument defect (below) |
| **G2** null-arm identity | GATE FAIL | 30/37 in band; `all_rows_max=0.02419` > ceiling 0.01; 2 missing (incomplete) |
| **G3** arm separation | GATE FAIL | GATE FAILs on principle because 4 cases are missing (incomplete arm pair); of the 35 evaluable, all 35 separate (>1e-2), max spread 0.101 |
| **G4** cap-bound census | GATE REACHED | 0 cap-bound (≤ 8) |

Standing rule 5 (Roache triple gating) **does not apply** — one mesh per case, no
triple; the comparator prints that sentence in its own output.

### G0 — the 6 incomplete arms, exactly as pre-stated (§5)

    kOmega/AR_14_Ret_180, kOmega/AR_1_Ret_180, kOmega/AR_7_Ret_180,
    kOmega/PH_Breuer, kOmegaSST_null/AR_1_Ret_180, kOmegaSST_null/PH_Breuer

Each holds only `0/` and `0.orig/` (rc=124 wall-timeout). G0 GATE FAIL was the
pre-registered expectation and is confirmed.

## THE G1 DEFECT — TRIAGE (SUPERVISION §3 check-2, done personally)

**G1 NOT A RESULT is a comparator parsing defect, NOT a physical arm
mis-application.** Proof:

* `MODEL_RE = re.compile(r"Selecting\s+(?:RAS\s+)?turbulence model\s+(\w+)")`
  (`grade_m1b.py:394`, **byte-identical to frozen `grade_m1.py:224`** — inherited).
* Every real OpenFOAM log in this corpus prints TWO lines, in this order:

      Selecting turbulence model type RAS      <- MODEL_RE.search() matches FIRST, captures "type"
      Selecting RAS turbulence model kOmega    <- the model-specific line, never reached

  `.search()` returns the first match, so `model_from_log = "type"` on all 78.
* The arm WAS applied correctly: `read_ras_model_from_dict` returns `kOmega` /
  `kOmegaSST` correctly (`grade_m1b.py:525`, regex sound), and the real log's own
  second line literally names the correct model. G1 compares dict-model (correct)
  vs log-model ("type") and flags a mismatch that does not physically exist.
* **Why it was invisible until now:** the synthetic selftest fixture
  (`grade_m1b.py:1105`) writes only `Selecting RAS turbulence model {model}` and
  omits the `... model type RAS` line that precedes it in every real log — the
  fixture is cleaner than any log a solver produces. The comparator's own comment
  at line 1100 diagnoses exactly this class of hazard for the *fatal* channel
  (which now carries a §2j real-bytes birth demonstration) but the **arm-
  application model-name reader was never given a real-bytes birth demonstration**.
* The frozen `grade_m1.py` never reached G1 (it refused at C1), so this defect has
  been latent since the M1 freeze and is surfaced only now that C1 is repaired.

**Consequence.** A comparator whose arm-application log channel is broken must not
certify the sweep — NOT A RESULT is the correct label. But it is an **instrument**
NOT A RESULT: the multimodel-sweep data is intact and the arms were correctly
applied. G2/G3/G4 numbers were computed and are printed for the record, but are
not believable while G1 is NOT A RESULT.

## COST — CALIBRATION (rule 12)

* **Grade + birth demonstration:** < 0.01 core-min (0.05 s wall). MEASURED.
* **Solve phase (the 78 runs, from STATUS):** **781.4 core-min** MEASURED, 0 rows
  NOT MEASURED. Registered estimate **1298.1 core-min**, cap 1900.0.
  **actual/predicted = 0.602** — the estimate over-predicted because the 72
  complete arms converged well before the 20000 cap (most CONVERGED@2000–5000),
  so wall times fell short of a cap-budgeted estimate. Gap attributed to
  misprediction (cap-conservative estimate), not contention.
* **Waste, separately named (rule 12 §6), included within the 781.4:** the 6
  timeout arms = **133.03 core-min** = **$0.114 DERIVED** at $0.0513/core-h.
* Dollars: 781.4 core-min = 13.023 core-h → **$0.668 DERIVED** (box cannot read
  its own billing; derived, not measured).
* **$0.00 send.** SUBMISSIONS PARKED.

## NEXT INCREMENT

A successor comparator (M1c-class) that repairs MODEL_RE to bind the model name
from the specific `Selecting RAS turbulence model <name>` line (or take the LAST
match, not the first), inherits ALL gate thresholds VERBATIM again, and carries a
**real-bytes birth demonstration of the arm-application model-name channel** so
the fixture can no longer be cleaner than the logs. Zero-compute (data on disk).
This is a verdict-asserting freeze; a heads-up goes to Sanaa's desk first.

*Recorded by the closure supervisor, 2026-09-09. Frozen `grade_m1b.py` is NOT
edited (rule 6); the repair lives in the successor.*
