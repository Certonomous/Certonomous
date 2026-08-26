# VMFL002 — Laminar Flow Through a Pipe with Uniform Heat Flux: `GATE REACHED`

## VERDICT: `GATE REACHED`

Both frozen gate channels lie inside their 2 % bands at the finest level, on a
grid triple whose dP and rise channels are both `CONVERGING`. Ceiling GATE REACHED
per supervisor Ruling 1 (the gate is the manual's PRINTED Target, not a
lab-evaluated closed form). Drafted by `ansys-lane-opus48` (Opus 4.8), 2026-08-26,
for the supervisor's audit.

- **Manual reference (frozen gate):** pressure drop = 1.000 Pa; centreline outlet
  temperature = 341.00 K (VM2026R1 p.17 Table .02.1 "Target"). Category V; ceiling
  GATE REACHED (Ruling 1) — the lab compares to Ansys's published Target, not to its
  own closed-form re-derivation (0.99724 Pa / 341.0638 K, prereg Corroboration, used
  only to corroborate the archive-sourced inlet).
- **Archive-sourced setup input (Ruling 1, disclosed):** inlet velocity from
  `VMFL002_WB.wbpz → .../Fluent/VMFL002_laminar-pipe-hotflow.set.prof` (20 radial
  points, least-squares fit u=umax(1−(r/R)²), umax=1.0231091246e-02 m/s). Confirmed
  at runtime: codedFixedValue compiled via wmake; inlet U parabolic (near-axis 0.01021).
- **Grid triple:** L1 60×15 (900), L2 120×30 (3600), L3 240×60 (14400), r=2, wedge.
- **Controls:** planted-zero fired on both channels; strict completion (rc=0, End
  line, last time==5000, U/p/T present, ExecutionTime count==5000, age guard) held on
  all three levels; both triples CONVERGING.
- **Prereg sha:** `bda4c9a083184335afa2b921fa6311cdf5d8ff4b`.
  **Comparator sha:** `027bcbf72eba2177f8b76eec0136f13b6bb75db8`.
  **Grading artifact:** `verification/runs/ansys_verification/VMFL002/GRADING_VMFL002.json`.
- **Comparator `--selftest`:** 16/16 exit 0, IDENTICAL under `python3` and `python3
  -O`. No `assert` carries any control.

## COST (rule 12 calibration — actual vs pre-registered)

- **Measured actual:** 5.2 core-min total (L1 0.3 + L2 0.817 + L3 4.083; ranks=1, so
  core-min = wall-min), from each level's `RUN_RC.txt` and `COST.txt`. Cap 40.
- **Pre-registered estimate:** 11.4 core-min (prereg §12, measured-basis pre-flight at
  load ~9).
- **Ratio actual/predicted = 0.46** — came in UNDER. Attribution: misprediction on
  the conservative side (the pre-flight rate was taken under higher contention than
  the actual run saw); no waste (nothing re-run, all levels rc=0); contention not
  separately isolated (no uncontended control bought).
- **$ derived (not measured):** 5.2 core-min × $0.0513/core-h ÷ 60 = **$0.0044**, at
  the owner-stated c7a.4xlarge rate; the box cannot read its own billing.

**Ledger follow-up (for the supervisor):** register row and a `docs/COST_CALIBRATION.md`
row (C-108 at draft time; re-derive number at commit, rule 11) are owed; the numbers
above are the content.
