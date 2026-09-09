# M1d multimodel sweep -- G1 MODEL_RE fix (successor to M1b)

    UNFROZEN -- NOT A RESULT -- NO SUPERVISION_CHARTER sec.3 check-1 YET.
    DO NOT GRADE TO A VERDICT.  DO NOT FREEZE.
    Nothing this comparator produces is a result until the closure-supervisor
    performs the sec.3 check-1 diff-read and freezes it by sha in a DELIBERATE
    session with a pre-registration (CLAUDE.md rule 2).

## What this is

`grade_m1d.py` is the **UNFROZEN successor to M1b** (`grade_m1b.py`), built to fix
the single defect **L-509** in the arm-application gate G1. It is a copy of
`grade_m1b.py` with **only** the model-name reader, its synthetic fixture, and
its §2j birth demonstration changed. It is **not** a repair of the frozen
`grade_m1b.py` or `grade_m1.py` (CLAUDE.md rule 6 forbids editing either) -- it is
a new file, per the family's standing successor precedent.

## The defect it fixes (L-509)

`grade_m1b.py:394` (byte-identical to the frozen `grade_m1.py:224`) read:

    MODEL_RE = re.compile(r"Selecting\s+(?:RAS\s+)?turbulence model\s+(\w+)")

applied in `parse_log` with `.search()`, first-match-wins. Every real OpenFOAM log
prints two lines, in this order:

    Selecting turbulence model type RAS      <- MODEL_RE matched this FIRST -> "type"
    Selecting RAS turbulence model kOmega    <- the model-specific line, never reached

So `model_from_log` was the literal `"type"` on all 78 M1 rows, and G1 flagged a
mismatch against the (correct) dict model -> **NOT A RESULT on all 78 rows**. The
arm was applied correctly; the reader captured a keyword. M1b's synthetic fixture
(`grade_m1b.py:1105`) wrote only the second line and omitted the first, so a green
selftest never saw the defect -- the "fixture cleaner than a real log" failure of
L-402 / the G2 precedent.

## What changed vs `grade_m1b.py`

1. **MODEL_RE** now makes the `RAS ` token before `turbulence model` **mandatory**:

       MODEL_RE = re.compile(r"Selecting RAS turbulence model\s+(\w+)")

   It matches `Selecting RAS turbulence model kOmega` (captures the model) and does
   **not** match `Selecting turbulence model type RAS`, so first-match-wins now
   lands on the model-specific line. `MODEL_RE2` (the inherited fallback, unused in
   `parse_log`) is line-anchored and verified not to reintroduce the `"type"`
   capture on the generic line.

2. **The synthetic fixture** (`_fake_log`) now prepends the real generic line
   `Selecting turbulence model type RAS` before the model-specific line, so the
   fixture reproduces the real two-line banner and can **exhibit** the defect.

3. **L-314 planted-failure proof (model channel)** added to `--selftest`: (a) the
   fixed `MODEL_RE` extracts `kOmega` from the two-line banner; (b) the retained
   defective predecessor pattern would have captured `type` from the same bytes.

4. **§2j birth demonstration** extended with a **MODEL limb on REAL producer bytes**:
   on the same real M1 clean logs the fixed reader extracts the true model
   (`kOmega`/`kOmegaSST`) while the defective pattern reads `type`. The birth record
   is a **separate** path (`/home/ubuntu/closure-data/m1d_birth/`) so it does not
   clobber M1b's, and `verify_birth_record` now refuses (BIRTH-MODEL) if that limb
   is absent or unsatisfied.

**Everything else is inherited from M1b verbatim**: all 12 gate constants
(`CAP_ITER`, `CONV_K_TOL`, `CONV_OMEGA_TOL`, `G2_BAND`, `G2_MIN_IN_BAND`,
`G2_MATCHED_PREFIX`, `G2_UNMATCHED_MAX_OUT`, `G2_CEILING`, `G2_REFUSE_ABOVE`,
`G3_SEPARATION`, `G3_MIN_CASES`, `G4_MAX_CAPBOUND`), the C1 planted-zero predicate
(the L-508 repair), the fatal channel, and the non-finite/anti-windowing channel.

## Verification done (ZERO COMPUTE -- regex + selftest + read-only)

- `python3 grade_m1d.py --selftest`  -> **66 ok, 0 FAIL, SELFTEST PASS** (rc 0)
- `python3 -O grade_m1d.py --selftest` -> **66 ok, 0 FAIL, SELFTEST PASS** (rc 0)
  (L-332: refusals via `raise`/`sys.exit(2)`, zero `ast.Assert` nodes)
- `python3 grade_m1d.py --birth` -> all three limbs SATISFIED on real producer
  bytes (fatal positive 3/3, fatal negative 4/4, MODEL 4/4).
- **DRY RUN ONLY, NOT A VERDICT (unfrozen)**, real corpus, output to scratch:
  **G1 = PASS** (n_bad 0 -- the fix works), G0 = GATE FAIL (n_complete 72, the same
  6 incomplete arms), G2/G3 = GATE FAIL (missing rows), G4 = GATE REACHED. No result
  record committed.

## What it awaits

The closure-supervisor's **SUPERVISION_CHARTER sec.3 check-1** (the measurement-
script diff read, done personally, never delegated), then a **deliberate freeze
session** with a pre-registration committed before any graded verdict (CLAUDE.md
rule 2). Until then this file grades nothing.
