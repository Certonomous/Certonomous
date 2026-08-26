# VMFL011 — Laminar Flow in a Triangular Cavity: `NOT A RESULT` (comparator refused)

## VERDICT: `NOT A RESULT` — the frozen comparator REFUSED (exit 2)

The frozen comparator refused on its planted-zero control (rule 3) and produced no
graded number. Per the supervisor's directive, that refusal IS the result and the
frozen instrument is not edited (rule 2). Drafted by `ansys-lane-opus48`, 2026-08-26,
for the supervisor's audit. Manual p.41; reference the Jyotsna-Vanka 1995 numerical
benchmark (code-to-code, digitised from Figure .11.2); ceiling GATE REACHED.

### The refusal, exactly

`grade_vmfl011.py --run-root …VMFL011` → **exit 2**:
> REFUSING (exit 2): planted-zero control FAILED for rms_vs_benchmark. planted 0.001234
> into …/L1/postProcessing/bisector/20000/bisect_U.xy, reader moved by only 3.67709e-07.

### Diagnosis — a mis-calibrated control, NOT a blind reader (a FINDING)

The reader is **responsive**, not blind: the plant moved the RMS by 3.68e-7 ≠ 0. But
`rms_vs_benchmark` is an RMS over the **401** bisector sample points, so a single-point
plant of 1.234e-3 is diluted by ~1/√N to O(1e-7) — far below the control's threshold
`delta > 0.1·plant = 1.234e-4`. The planted-zero threshold `0.1·plant` is calibrated
for a **point reader** (the `u_min` channel, where plant→read is ~1:1) and is
**unreachable for an averaging reader** (an RMS over many points). This is an inherited
frozen-grader defect I did not catch when freezing. **A corrected re-run — plant sized
to the averaging reader's sensitivity, or a per-channel threshold — is a NEW row
(charter §6).** Candidate LESSON L-339 (flagged for the supervisor).

### The physics beside the verdict (would NOT have been a clean pass either)

| level | rms_vs_benchmark (band 0.030) | u_min_norm (bench −0.318062) |
|---|---|---|
| L1 (800 c) | 0.0403 | −0.264494 |
| L2 (3200 c) | 0.0348 | −0.319438 |
| L3 (12800 c) | **0.0341** | −0.337560 |

- **rms exceeds the 3 % band at every level** — even absent the control refusal, L3
  (0.0341 > 0.030) would grade `GATE FAIL`.
- **u_min triple is CONVERGING** (steps −0.05494, −0.01812; ratio 0.330; observed order
  **p = 1.60**; Richardson-extrapolated **−0.3465**) — but the lab's converged
  recirculation minimum sits **8.9 % from the digitised benchmark −0.318**, larger than
  the ~1–3 % digitisation noise assumed in the prereg band. Whether that gap is the
  digitisation, the collapsed-hex apex resolution, or an under-resolved corner vortex
  (p=1.60 < the formal 2.0) is OPEN and not resolved here.

So VMFL011 is genuinely not a clean credential: the honest verdict is `NOT A RESULT`
(comparator refused), and the physics points to `GATE FAIL` + a real benchmark
discrepancy underneath.

### Provenance
- **Prereg sha:** `4bd8c4285e379e93e1ad4e6c2b9967604d042523`.
  **Comparator sha:** `e369496bf2e28ccb7145756e1c2442eb11e8e3f7` (blob-verified == HEAD).
- **Comparator `--selftest`:** 16/16 exit 0 under `python3` and `python3 -O`;
  `mutation_test_vmfl011.py` 6/6 exit 0 under both.
- **Detachment:** launched with the supervisor's setsid fix; verified live
  (wrapper SID==PID); all three levels completed rc=0 detached from the launching lane.

## COST (rule 12 calibration)
- **Measured actual:** 8.2 core-min (L1 0.25 + L2 0.967 + L3 7.0; ranks=1). Cap 50.
- **Pre-registered estimate:** ~39.3 core-min (prereg §7, from an L3 smoke at 118 ms/iter
  measured under contention). **Ratio actual/predicted = 0.21** — the smoke rate was
  taken under load and badly over-predicted; the actual ran uncontended (ET/CT L1 0.991
  / L2 1.000 / L3 1.000). No waste (rc=0 throughout, comparator refusal is not a re-run).
- **$ derived:** 8.2 core-min × $0.0513/core-h ÷ 60 = **$0.0070**.

**Ledger follow-up:** register row and COST_CALIBRATION row landed with this record;
LESSON L-339 (planted-zero threshold must scale to the reader's sensitivity) flagged.

---
**Correction (2026-08-26, appended not rewritten):** the planted-zero-threshold lesson
predicted above as "candidate L-339" landed as **L-340** — a peer appended L-339 between
this file's drafting and the lesson's commit, and the number was re-derived from the HEAD
blob tail at commit (CLAUDE.md rule 11: an id written in prose before its append is a
prediction, not an identifier). The correct reference is **L-340**.
