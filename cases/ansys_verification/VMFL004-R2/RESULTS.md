# VMFL004-R2 — Plain Couette Flow with Pressure Gradient: `PASS`

## VERDICT: `PASS` (tier `HOLDS`)

VMFL004-R2 is the corrected re-run of VMFL004 (register row #25, `NOT A RESULT`) under
`ANSYS_VERIFICATION_CHARTER` §6. The gate quantity, reference, band and ceiling were carried
over **byte-identical** from VMFL004; the only change was the iterative-convergence channel,
argued on the physics of a 1-D fully-developed flow before the freeze (L-338). The physics
VMFL004 always supported is now earned honestly. Drafted by `ansys-lane-opus48` (Opus 4.8),
2026-08-26.

### The gate (carried over byte-identical from VMFL004)

`volAverage(U)_x` against the exact lab-evaluated section mean ⟨u⟩ = ∫₀¹(9y−6y²)dy = **2.5 m/s**:

| level | volAverage(U)_x | rel_dev (band 1e-3) | driven Ux_initial (floor 1e-7) |
|---|---|---|---|
| L1 (15×40) | 2.50125 | 5.000e-4 | 1.085e-15 |
| L2 (30×80) | 2.5003125 | 1.250e-4 | 1.386e-15 |
| L3 (60×160) | 2.50007812461 | **3.125e-5** | 3.220e-13 |

Triple **CONVERGING**, observed order **p = 1.99999760**, GCI_fine (Fs=1.25) **3.906e-5**,
Richardson extrapolate **2.499999999** (2.5 to 9 digits). Fine-grid rel_dev **3.125e-5** is
**~32× inside** the 0.1 % band → **PASS**. These values reproduce VMFL004 bit-for-bit (the run
is identical physics; L3's driven residual 3.22e-13 is exactly the figure L-338 recorded from
VMFL004), confirming this is the same run VMFL004 was — now correctly graded.

### The one change: iterative convergence gated on the driven channel

VMFL004 was `NOT A RESULT` because its inherited check required Uy and p residuals below 1e-7,
which are normalization noise for the degenerate transverse fields of a 1-D fully-developed flow
(L-338). VMFL004-R2 gates on the **driven** channel `Ux_initial` (all three levels ≪ 1e-7), and
**does not delete** the transverse channel — it tests it against a physics-based criterion:

| level | Uy_initial | p_initial | \|⟨U⟩_y\| | \|⟨U⟩_z\| | transverse degeneracy |
|---|---|---|---|---|---|
| L1 | 0.0947 | 0.0424 | 4.3e-17 | 0 | PASS |
| L2 | 0.0714 | 0.0471 | 6.6e-17 | 0 | PASS |
| L3 | 0.0492 | 0.0923 | 2.5e-17 | 0 | PASS |

The transverse normalized residuals are the expected O(1e-2) noise (all < the 1.0 divergence
ceiling), and the transverse **mean velocities are at machine level** (|⟨U⟩_y| ~ 1e-17 ≪ 1e-6
m/s), **confirming the fields ARE degenerate** — which is precisely what justifies exempting
their residual from the floor. The exemption's premise was tested, not assumed, and it held.

### Controls (all fired)

All four planted-zero controls PASSED with reader delta **= 0.001234** exactly (the plant, no
1/√N dilution — single-point plants into single-point readers, L-340): the gate reader
`volavg_ux_ms`, the transverse readers `volavg_uy_ms` / `volavg_uz_ms`, and the driven-
convergence reader `Ux_initial` in `solverInfo.dat` (this last closes a latent rule-3 gap in
VMFL004's grader). Strict completion (rule 4, all clauses incl. age guard) held at every level;
Roache triple `CONVERGING` (rule 5). The launcher verified detachment by SID==PID at every level.

### Why this is not gate-fitting

The known-PASS answer could not have shaped the gate because the gate quantity, reference, band
and ceiling were carried over **byte-identical** and the case files are a verified byte-identical
copy of VMFL004/case. The only change — the convergence channel — was justified on the flow's
structure (the degeneracy of Uy and p) independently of the answer, and it *adds* a real-failure
detector (transverse degeneracy) rather than removing one, so it can only make the instrument
stricter. Comparator `--selftest` 30/30 (identical under `python3`/`python3 -O`); mutation test
12/12 (three controls broken, each caught under both interpreters).

### Provenance

- **Prereg blob:** `3c78d0f52a86c99e42f3c1cbd3285550160f38ef` (freeze commit `bde20ff5`).
- **Comparator blob:** `417b4bbe60f49e67d0a33c2379fce20e38e72ee2` (`--verify-frozen HEAD` = FROZEN).
- **Grading:** `verification/runs/ansys_verification/VMFL004-R2/GRADING_VMFL004_R2.json`.
- **Run:** `verification/runs/ansys_verification/VMFL004-R2/{L1,L2,L3}/`; each `RUN_RC.txt` records
  the prereg and comparator shas the run verified at launch (`LAUNCH_RECORD.txt`).
- **Cites:** register row #25 (VMFL004, `NOT A RESULT`), which is NOT edited or removed.
- **Ceiling:** PASS/HOLDS — category-V closed form earning a rule-1 PASS per the VMFL019 precedent.

## COST (rule 12 calibration — actual vs pre-registered)

- **Measured actual:** **13.033 core-min** total (L1 0.467 + L2 2.133 + L3 10.433; ranks=1), from
  each level's `RUN_RC.txt` / `COST.txt`. Cap 30 (0.43 of cap; no overrun).
- **Pre-registered estimate:** ~11.4 core-min (VMFL004's measured actual for the identical run).
- **Ratio actual/predicted ≈ 1.14** — the +14 % is box contention (loadavg ~13 during the run),
  not misprediction of the work; the byte-identical-physics prediction was sound. **No waste**
  (rc=0 at every level).
- **$ derived (not measured):** 13.033 core-min × $0.0513/core-h ÷ 60 = **$0.01114**.

**Ledger follow-up owed to the supervisor (drafted in the lane report, NOT committed by this lane
because both the validation register and the calibration ledger are mid-rewrite on disk — disk ≠
HEAD — and adding rows now would collide):** the VMFL004-R2 register row (verdict PASS, citing
#25) and a COST_CALIBRATION row (actual 13.033 vs predicted 11.4, ratio 1.14, contention-
attributed). Numbers and text are in the lane report for the supervisor to land once the ledgers
settle.
