# VMFL007-R3 — Non-Newtonian (power-law) Flow in a Pipe — RESULTS (`PASS`, recovered from `BLOCKED`)

**Case.** VM2026R1 §.07 (p. 29): fully-developed laminar flow of a power-law
(shear-thinning) fluid in a pipe; the gated quantity is the pressure drop Δp.
OpenFOAM v2606 `simpleFoam`, SIMPLEC arm, three-level r-family L1/L2/L3 to
`endTime 60000`. Reference: closed-form Rabinowitsch-Mooney solution
**60521.969 Pa** (Hughes & Brighton, *Schaum's Outline of Fluid Dynamics*), the
manual's printed target **60.52 kPa** (Table .07.1); Ansys Fluent 60.41 / CFX
61.52 kPa are context-only.

**Verdict: `PASS`** (register row #67) — the lab's **11th** ansys credential
(recovers the VMFL007 case; not the lab's first credential). **Recovered from
`BLOCKED` (row #64) via a VERIFICATION_CHARTER §2d.1 value-invariant repair of the
frozen grading instrument, verification-audited as V-129.** The SAME complete,
valid run is graded — **ZERO re-solve.**

## What was blocked, and what the §2d.1 repair changed

Row #64 landed `BLOCKED`: the frozen comparator (v1.0, blob `03518d00`) REFUSED
(exit 2) inside the OFF-GATE `nuMinAll`/`nuMaxAll` viscosity-clip precondition —
its `_monitor_path` (frozen lines 152-155) globbed `surfaceFieldValue.dat` for
every monitor, but the driver's `controlDict` declares those two nu monitors as
`type volFieldValue`, so OpenFOAM wrote `volFieldValue.dat`. The glob matched zero
paths and `one_or_refuse` raised exit 2 from `viscosity_class`, **before** the
gate and before the pInlet planted control. The run itself is complete and valid
(strict completion passed on all three levels); the block was a defect in our
grading instrument.

The in-place amendment (v1.0 → v1.1, blob **`da081105`**) is a **pure insertion**
at the file foot (frozen lines 1-898 byte-identical; verified by blob diff — 0
content deletions, 1 hunk at line 896). It appends `_visc_monitor_path` (resolves
whichever single file OpenFOAM wrote — `volFieldValue.dat` in a real run,
`surfaceFieldValue.dat` in the frozen selftest fixtures — under the SAME
`one_or_refuse` discipline), `_visc_read_scalar_series` (identical parse), a
`viscosity_class` that **overrides** the frozen off-gate reader using the frozen
clip thresholds (0.999·NUMAX, 1.001·NUMIN) byte-for-byte, and a selftest
regression arm that builds a `volFieldValue.dat` fixture and proves the repaired
reader resolves it while the frozen `surfaceFieldValue`-only glob refuses it. It
lets the comparator REACH the frozen gate; it references and alters no gate
quantity, band, threshold, label, verdict-cascade node or planted control.

## The §2d.1 four conditions (VERIFICATION_CHARTER §2d.1), with evidence

1. **Demonstrable error, not a preference.** Proven by file existence: the
   `surfaceFieldValue` path does not exist for the nu monitors; `volFieldValue.dat`
   does (all six across L1/L2/L3). The frozen glob matched 0 paths → exit 2 on a
   valid run.
2. **[Load-bearing] Established by an instrument that grades nothing.** The
   appended `volFieldValue` selftest regression arm grades nothing — it plants a
   fixture and requires the repaired reader to resolve it while the frozen glob
   refuses. Independently, the repair is **value-invariant**: the entire
   verdict/gate path is byte-identical (blob diff), so the change could not have
   been selected to move the verdict. Verification confirmed byte-for-byte
   value-invariance as **V-129** (signed off, commit `ac004773`).
3. **Disclosed, instrument named, what-moved quantified.** The dated amendment
   header discloses the change, names V-129 and the selftest arm, and states what
   moved: the comparator now REACHES the gate; **no gate quantity moved**
   (value-invariant).
4. **Pre-repair values recorded beside the published ones.** The pre-repair state
   was **no Δp graded — the comparator refused at the off-gate precondition**
   (row #64, `BLOCKED`, preserved unedited). This row records that absence,
   measured and named, beside the now-published triple — the §2d.3 pattern for a
   repair whose predecessor published no value.

## The graded result (re-grade of the SAME run, ZERO re-solve)

Re-run first-hand through the amended frozen comparator (this lane's grade
execution was **not** auto-mode-blocked; it produced the verdict and rewrote
`GRADING_VMFL007_R3.json`, reproducing the draft run):

| level | Δp (Pa) | plateau | residuals |
|---|---|---|---|
| L1 | 60432.6281 | ptp 7.65e-06 Pa (PLATEAUED) | SETTLED |
| L2 | 60498.9821 | ptp 1.65e-05 Pa (PLATEAUED) | SETTLED |
| L3 | 60517.0713 | ptp 0.001535 Pa (PLATEAUED) | SETTLED |

- **Gate:** `|Δp − 60520| / 60520 ≤ 0.005` (band [60217.40, 60822.60] Pa) AND a
  CONVERGING triple. Finest **Δp = 60517.0713 Pa**, rel dev **0.00484 %** — inside
  the band.
- **Roache triple** (r = 2.0): 60432.6281 / 60498.9821 / 60517.0713 →
  **CONVERGING**, observed order **p = 1.8751**, **GCI_fine 0.0140 %** (Fs 1.25).
- **VERDICT: `PASS`** — ceiling `PASS` (§12.2 ruled SAME/PASS-capable, the
  reference is the closed-form solution of the same continuum model).
- **Controls FIRED:** planted-zero on L3 passed (planted 0.001234 kinematic →
  reader Δp shift 1.2340000000040163 Pa vs expected 1.234; file
  `pInlet/surfaceFieldValue.dat` — the gate reader, unchanged by the repair);
  p-floor planted control OK (P_MIN 0.05). Selftest **all checks passed under
  `python3` AND `python3 -O`** (frozen v1.0 arms + the new v1.1 volFieldValue arm);
  `ast.Assert` count **0**.

## Freeze / verification chain

- **Frozen comparator (v1.1)** `cases/ansys_verification/VMFL007-R3/grade_vmfl007_r3.py`,
  blob **`da0811058965cb34de24ff70af4427991554f431`** — verified on disk; the frozen
  v1.0 (blob `03518d00`) is byte-identical on lines 1-898. **Grading path re-pinned
  to commit `b955b605`** (the commit carrying v1.1); the original freeze `529f1665`
  (blob `03518d00`) is superseded **for grading**, not rewritten (rule 6).
- **Pre-registration** blob `3242a99f`, with a dated re-pin addendum at its foot
  (rule 6, no frozen line rewritten). V-129 value-invariance confirmed.

## Cost (rule 12) — ZERO re-solve

**35.45 core-min** (the row #64 compute, unchanged; L1 1.4333 + L2 4.8667 + L3
29.15, serial ranks=1) = **$0.03 DERIVED, NOT measured** at $0.0513/core-h
(`COMPUTE_BUDGET_CHARTER.md` §5). The §2d.1 repair added **no solver time** — it
re-grades the already-complete run.

## Provenance

- **Run root:** `verification/runs/ansys_verification/VMFL007-R3/{L1,L2,L3}` +
  `GRADING_VMFL007_R3.json` (re-grade PASS). Gate series
  `pInlet`/`pOutlet` `surfaceFieldValue.dat`; nu monitors
  `nuMinAll`/`nuMaxAll` `volFieldValue.dat`.
- **Cites/supersedes** row #64 (BLOCKED); cites rows #8 (VMFL007 run 1) and #37
  (VMFL007-R2), both preserved unedited.
- **Calibration:** `docs/COST_CALIBRATION.md` row `C-20260909T021050.027609Z-049e6ae7`.
