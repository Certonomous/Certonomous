# VMFL011-R3 — Laminar Flow in a Triangular Cavity: `GATE FAIL`

## VERDICT: `GATE FAIL` — the frozen gate `rms_vs_benchmark ≤ 0.030` is missed at L3 (0.034088), on a `CONVERGING` triple

VMFL011-R3 is the third attempt at the triangular-cavity case (VM2026R1 p. 41/42). Rows **#26**
(VMFL011) and **#31** (VMFL011-R2) both landed `NOT A RESULT` because the frozen comparator
**refused (exit 2)** at its planted-zero control — the readers could not see the plant on those
runs. R3 carries the gate section **byte-identical** (the prereg documents an EMPTY 77-line diff
over every gate constant, the verdict path, `roache()` and both gate readers) so that no gate
constant, band, reader or verdict path could have been chosen to fit the R2 answer already on
disk (rule 2). The prereg states in terms: **"THE PREDICTED OUTCOME OF THIS RUN IS `GATE FAIL`"**
— and it is. Graded independently by `ansys-lane-opus48` (lane B), 2026-08-27.

### The numbers, exactly (frozen comparator `grade_vmfl011_r3.py`, blob `3975d9ee`)

- **Gate: `rms_vs_benchmark ≤ 0.030` at L3 (the finest level).**
- **L3 `rms_vs_benchmark = 0.034087720284112416`** — deviation exceeds the 0.030 band by 13.6 %
  ⇒ **`GATE FAIL`**.
- rms sequence L1 / L2 / L3 = **0.040264214986269156 / 0.0347751352338498 / 0.034087720284112416**
  — monotone decreasing (converging toward the benchmark, but the finest level does not enter the
  band).
- **Roache triple (computed on `u_min_norm`): `CONVERGING`, GCI_fine = 0.033030412676502835
  (3.303 %)**, state above/below the p-floor `CONVERGING`/`DEGENERATE`. Because the triple is
  `CONVERGING`, rule 5 does **not** convert the row to `NOT A RESULT`; the gate verdict
  `GATE FAIL` stands.
- **Tier: `NOT HELD`** — the tier ceiling is `GATE REACHED` (the reference is code-to-code
  numerical; the comparator cannot print `PASS`), and the gate is missed, so the row earns no
  coverage tier.

### R-RC handling — the load-bearing part (first live application of R-RC, approved 2026-08-27)

**This run lands on R-RC-1, and neither R-RC-2 nor its R-RC-4 fence is engaged.**

R-RC (approved by Sanaa 2026-08-27; ruling `docs/L342_GRADER_AUDIT.md` §2, cross-cited in
`VERIFICATION_CHARTER` §1's desk-rulings block) sorts the `RUN_RC.<level>` boundary:

- **R-RC-1** — the rc **value** is physics-critical (rule 4 unchanged); the rc **record** is
  infrastructure.
- **R-RC-2** — record **ABSENT** ⇒ grader marks rc `NOT MEASURED` and proceeds, **only if** the
  four other rule-4 physics conditions hold.
- **R-RC-3** — record **PRESENT and non-zero** ⇒ refuse.
- **R-RC-4** — the fence on R-RC-2's permissive widening: a grader *inferring* rc must also refuse
  on a `FOAM FATAL` / signal token.

For VMFL011-R3, **`RUN_RC.L1/.L2/.L3` are all PRESENT with `rc = 0`**, captured **inside the
detached subshell** (the note in each record says so). The comparator's own JSON records
`rc_measured = True`, `rc = 0`, `rc_path = …/RUN_RC.L<n>`, `state = COMPLETE` at every level.
**rc is therefore directly MEASURED from a present zero record — R-RC-1.** R-RC-2's permissive
widening (which fires only on an ABSENT record) is not invoked, so its R-RC-4 FOAM-FATAL fence is
not the operative path — nothing was inferred. (The L3 solver log ends on a clean `End` line with
final p residual 5.10e-13 and continuity 1.40e-13; no fatal or signal token exists to catch.)
This is the clean top-of-ladder case R-RC-1 describes.

### Controls fired (CLAUDE.md rule 3)

All planted-zero off-path probes fired (exit 2 each): the L-340 parent-pair plant (reader moved
3.68e-07 < 1.234e-04 threshold — refuses), the all-row unsized plant (1.06e-04 < threshold —
refuses), the adversarial fixed plant (1.39e-17 < 0.04 — refuses), and the L-347 placement
probe. The **on-path** reader passed its sized-plant sensitivity (0.322 → delta 0.1186 inside
band). `--verify-frozen` rc = 0 (disk == committed blob), `--selftest` 50/50. Strict completion
(rule 4) holds at all three levels (rc 0, End line, last == endTime 20000, fields present, age
guard).

### Cost

Total **9.5667 core-min** measured (L1 0.2667 + L2 1.0667 + L3 8.2333, wall 16 + 64 + 494 s × 1
rank ÷ 60), against the pre-registered **9.1 core-min** estimate — ratio **1.051×**. Running-total
cap 50 core-min — never bit (19.1 %). **$0.00818 derived** at $0.0513/core-h, derived not
measured. No stall, no waste.

### Provenance

- Prereg freeze: **`45c3e8a4ec3a805f98e7e2464cbbe770102c3f38`** (2026-08-26T22:39:13Z; blob
  `c169f992544b83c7f2082efdf4e38d7ac3773e64`, disk == HEAD).
- Comparator: **`3975d9ee3a60bde8b2c1537c27abb1431662d65b`** (`grade_vmfl011_r3.py`; disk == HEAD,
  `--verify-frozen` rc = 0, `--selftest` 50/50).
- Run artifacts: `verification/runs/ansys_verification/VMFL011-R3/` (L1, L2, L3; `RUN_RC.L1/.L2/.L3`
  rc = 0 each; `COST.txt`; grade JSON reproduced in the scratchpad, not a repository artifact).
- Reference: Jyotsna & Vanka, *J. Comp. Phys.* **122**, 107–117 (1995), via manual p. 41; the
  curve is Ansys's own digitisation (VMFL011_xvel.xy, "Benchmark x-norm", 46 rows). Manual p. 42
  prints only a FIGURE, no discrete target table. **Reference kind: NUM (code-to-code, doubly
  indirect) — buys neither V nor P; tier ceiling `GATE REACHED`.**
- Cites the superseded rows #26 (R1) and #31 (R2), both `NOT A RESULT`; their trees, preregs and
  comparators are preserved (VERIFICATION_CHARTER §6).

**`GATE FAIL` is a finding, not a credential and not a deletion** (charter §6). It is recorded
honestly with its numbers and is not softened.

### Charter / doc update line (Amendment 1.4 Clause C)

**NONE** — the outcome matches the prereg's named prediction (`GATE FAIL`) and R-RC-1 is the
already-documented clean rung; no new numerics fact, lesson or charter change is established.
