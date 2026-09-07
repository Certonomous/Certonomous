# F12 P-reference fidelity cross-check — DATED, GATE-NEUTRAL ADDENDUM

**Filed 2026-09-07 by a `lab-lane` worker for the cfd team.** Executes ruling
`verification/campaign/F12_P_REFERENCE_PROVENANCE_RULING_2026-09-07.md`
(ruling id **d1a55db1**, Branch A) against the pre-registered spot tap set
`verification/campaign/F12_P_REFERENCE_CROSSCHECK_TAP_PREREG_2026-09-07.md`
(committed **`3a3edef1`**, frozen BEFORE this tabulation). **Cost: 0 solver
core-min, $0.00** — a read-and-compare task; no solver, no mesh, no case directory.

## GATE-NEUTRALITY — asserted explicitly

This addendum records a **reference-provenance cross-check only**. It alters
**NO gate, NO threshold, NO cap, NO label and NO verdict** of F12. Specifically it
does not touch: admission gates A/B; Gate 1 (upper RMS ≤ 0.08, lower ≤ 0.04),
Gate 2 (≤ 0.020 c), Gate 3 (≤ 5%), Gate 4 (≤ 20%); the CM-reported clause; the
overall PASS rule; any cap; the three cell counts; either condition; the four
predictions. F12's frozen Gate-1 band is **not re-opened** (rule 2) — the
cross-check establishes reference **fidelity**, not a new band, and the read
error is folded into the reported **digitisation-uncertainty channel** as the
ruling's Branch A directs. F12's own row stands unchanged as **`GATE FAIL` /
`NOT HELD`** (`verification/campaign/F12_RESULTS.md`): its mesh failed admission
gate A at all three levels, so no Gate-1 value was ever computed and no P column
opened for that run. This addendum discharges the ruling's rule-15 condition on
the secondary reference **of record**; it does not, and cannot, resurrect a
Gate-1 number that F12's run never produced.

## The two sources (per L-144)

- **Secondary — F12's reference of record.**
  `verification/runs/F12_runs/reference/rae2822_case9_cp_upper.dat`, HEAD blob
  `44f6f0c8dfc845174202ea9df5e3134cdda5c50c`, the AFOSR-HTTM/Stanford flow-case-8621
  transcription (evaluator R. E. Melnik, 1981), consumed by the F12 grader
  `load_experiment_cp()` (`sdk/workflows/rae2822_case9.py:173`). Frozen 2026-07-30.
- **Primary — read from the PAGE IMAGE, not OCR/sidecar/filename.**
  `docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf`
  (17,588,425 B, 612 pp). **Title-page-verified this session (L-144):** PDF p1
  "AGARD-AR-138 / EXPERIMENTAL DATA BASE FOR COMPUTER PROGRAM ASSESSMENT / AGARD
  Advisory Report No.138 / Report of the Fluid Dynamics Panel Working Group 04";
  PDF p2 "Published May 1979 / Copyright © AGARD 1979 / ISBN 92-835-1323-1". RAE
  2822 contribution (Cook, McDonald, Firmin, RAE Farnborough) opens PDF p182
  (A6-1). Test-case conditions: Table 6.2, PDF p191 (A6-10) — Case 9 M∞=0.730,
  α=3.19°, Re=6.5e6, CN=0.803, Cm=−0.099, CD=0.0168 (matches the secondary).
  **Cp table read: Table 6.7, PDF p201 (A6-20), header "CASE 9 M=0.730
  ALPHA=3.19 RE=6500000", UPPER SURFACE column.** The primary Cp values were read
  by a human off the rendered p201 image (the numeric table bodies are absent from
  the OCR text layer, so a text-grep would falsely return zero — rule 3's
  principle applied to a document).

## Fidelity metric and tolerance (from the pre-reg / ruling)

Per tap, `d = Cp_secondary − Cp_primary`. Read tolerance **±0.0001** (one print
unit of the primary's 4-decimal table; its own rounding half-width is ±0.00005).
Experiment's quoted tap uncertainty **Cp ±0.0026** (AR-138 tape item 10, Re=6.5e6).
MEETS if every tap agrees within the read tolerance and thus far within ±0.0026.

## THE CROSS-CHECK — 12 upper-surface taps (7 shock-region dominators)

Primary Cp read from PDF p201 (A6-20). Secondary Cp read on-disk from the .dat.

| # | x/c (sec) | x/c (pri, p201) | Cp secondary | Cp primary | d = sec − pri | \|d\|/read-tol | shock region |
|---|---|---|---|---|---|---|---|
| 1  | 0.049974 | 0.0500 | −1.197257 | −1.1973 | +0.000043 | 0.43 | — |
| 2  | 0.100047 | 0.1000 | −1.112293 | −1.1123 | +0.000007 | 0.07 | — |
| 3  | 0.300038 | 0.3000 | −1.153426 | −1.1535 | +0.000074 | 0.74 | — |
| 4  | 0.500030 | 0.5000 | −1.285256 | −1.2853 | +0.000044 | 0.44 | **YES** (pre-shock) |
| 5  | 0.524967 | 0.5250 | −1.309700 | −1.3097 | +0.000000 | 0.00 | **YES** (peak suction) |
| 6  | 0.550003 | 0.5500 | −1.124936 | −1.1249 | −0.000036 | 0.36 | **YES** (shock onset) |
| 7  | 0.575039 | 0.5750 | −0.755240 | −0.7552 | −0.000040 | 0.40 | **YES** (steepest recompression) |
| 8  | 0.599976 | 0.6000 | −0.633863 | −0.6338 | −0.000063 | 0.63 | **YES** (post-shock) |
| 9  | 0.619647 | 0.6196 | −0.568117 | −0.5681 | −0.000017 | 0.17 | **YES** (post-shock) |
| 10 | 0.650048 | 0.6500 | −0.494953 | −0.4949 | −0.000053 | 0.53 | **YES** (recovery) |
| 11 | 0.749994 | 0.7500 | −0.298220 | −0.2983 | +0.000080 | 0.80 | — |
| 12 | 0.900013 | 0.9000 | −0.032538 | −0.0325 | −0.000038 | 0.38 | — |

- **max|d| = 0.000080** at x/c(sec) 0.749994.
- **max|d| as a fraction of the tap uncertainty (0.0026) = 0.0308** (3.08 %).
- Every tap is within the ±0.0001 read tolerance; the seven shock-region
  dominators agree to ≤ 0.000063 (tap 5, the peak-suction shoulder, is exact to
  six decimals). The residuals are at the 5th–6th decimal — the expected
  print/rounding difference between a 4-dp printed table and a 6-digit tape decode,
  with no systematic offset.

## DECISION — MEETS

**The secondary reference of record is a faithful transcription of the AR-138
primary Case 9 upper-surface pressure distribution.** Every pre-registered tap,
shock-foot dominators included, agrees within the read tolerance and far within
the experiment's own ±0.0026 tap uncertainty. The cross-check **MEETS** the
ruling's fidelity tolerance. This discharges the rule-15 / L-144 fidelity
obligation the ruling separated from rule 2's freeze.

**This addendum does NOT declare F12 P `PASS`.** Two reasons, both recorded:
(1) the P disposition is owed the cfd supervisor's personal **check-3** (big-claim
verification of these tap numbers and of gate-neutrality) and **check-1** of the
comparison script read as a diff, after which **verification audits this
addendum** (ruling's closing clause); and (2) F12's own run has no admissible
mesh, so there is no Gate-1 P value on this row to grade — the fidelity finding
attaches to the reference of record and to any **next** F12, not to a P column
this GATE-FAIL row never opened.

## Planted-zero control (rule 3) — flagged for supervisor check-1

The comparison was produced by
`verification/runs/F12_runs/p_reference_crosscheck_2026-09-07/crosscheck_p_reference.py`,
which carries a planted-zero control that fails closed (exit 2): before the real
comparison, it writes a known perturbation (+0.037000) into a disk copy of the
secondary at the steepest-recompression tap (x/c 0.575039), reads it back through
the same on-disk loader, and requires the diff detector to see +0.037000 there
and 0 elsewhere; it refuses rather than emit a possibly-blind zero. On this run
the control **passed** (reader saw +0.037000 at the planted tap, 0.00e+00
elsewhere). **A measurement script's output does not count until the supervisor
reads the diff (check-1);** this addendum's numbers are provisional on that read.

## Provenance and read order (rule 9, honestly)

The pre-registered tap set (`3a3edef1`) was committed **before** this tabulation;
the git history shows pre-reg → addendum, which is what proves the taps were not
chosen to fit. The tap-selection criterion is **primary-independent** (shock-foot
dominators of the unweighted Gate-1 RMS plus a chordwise spread), pinned to
F12's frozen prediction 4 and the shock location visible in the already-frozen
secondary. As disclosed in the pre-reg, PDF p201 was viewed as a whole page
during title-page verification, so the primary column had been seen before the
pre-reg commit; this does not compromise the freeze because the taps reference no
primary value and no primary-minus-secondary difference. No agent message
authorized anything here.

*Filed 2026-09-07 by a `lab-lane` worker for the cfd team. No solver was launched,
no mesh was built and no case directory was created in producing it. Every primary
Cp above was read from the PDF p201 page image per L-144; every secondary Cp was
read on-disk from the frozen `.dat`.*
