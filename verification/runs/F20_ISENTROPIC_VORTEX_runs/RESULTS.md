# F20 — 2-D ISENTROPIC VORTEX — RESULTS

**Written 2026-08-26T20:49:49Z by a cfd lab-lane (grading lane) for the cfd supervisor. Stamp from `date -u`.**
**Pre-registration:** `verification/campaign/F20_ISENTROPIC_VORTEX_PREREGISTRATION.md` frozen at
`548fc02e2ac8d1c27868af67a343f3a5495e8ecb`. **Run root:** `verification/runs/F20_ISENTROPIC_VORTEX_runs/`.
**Grader:** the FROZEN `cases/F20_ISENTROPIC_VORTEX/grade_f20.py` (blob `68057e2e`), invoked exactly as
`cases/F20_ISENTROPIC_VORTEX/launcher.queue.out` prints it; stdout/stderr captured as `GRADE_F20.out` /
`GRADE_F20.err` (stderr empty, grader rc 0); machine record `F20_GRADED.json`.
Nothing in this file re-grades, amends or widens anything; the verdicts are the grader's, verbatim.

## 1. Verdict table (grader output, fixed vocabulary)

| gate | fine value | exact | band (registered §5) | triple coarse/medium/fine | state | observed order p | GCI (Fs 1.25) | verdict |
|---|---|---|---|---|---|---|---|---|
| **G-F20-1** L2 density error E2(T=10) | **1.1598742e−03** | 0 | [1.391017e−04, 1.251915e−03] | 3.3424630e−03 / 1.4374871e−03 / 1.1598742e−03 | **CONVERGING** (r = 2.000 / 2.000, monotone) | **2.7786** | 5.1038 % = 5.91977e−05 abs; Richardson 1.1125e−03 | **PASS** |
| **G-F20-2** box-mean KE(T=10) | **1.0055387971** | 1.0056335487 | [1.004915893, 1.006351204] | 1.0056183415 / 1.0055620423 / 1.0055387971 | **CONVERGING** (monotone) | **1.2762** | 0.0020 % = 2.04339e−05 abs; Richardson 1.0055224500 | **PASS** |

Rule 5 limb (1) at every level `CONVERGED` on the registered basis (Courant stability census; inviscid
`rhoCentralFoam` has no iterative residual). Plateau: **ABSENT** by registration (`plateau: null` in every row).
Gated through `scripts/roache_triple.py::grade_ladder` at exactly one call site (AST census in the JSON:
`ast_call_nodes [551]`). `assert` census over the four instrument files: **0** nodes, planted assert seen.

**Cost line printed by the grader:** `cost actual: 68.667 core-min of cap 240.0`; cost-claim defects: none.

## 2. Registered predictions versus outcome — misses stated beside the verdicts

The verdicts above are the frozen grader's and are not altered here. The registered predictions (§5 of the
pre-registration) were:

- **G-F20-1:** CONVERGING, observed order in **[1.0, 1.6]**, fine value inside the band → PASS.
  *Outcome:* PASS, but the Roache order is **2.78 — above the registered range.** The band is a value band
  (§5: "does not depend on p"), so the verdict is unaffected; the order prediction is **MISSED**. The fine
  value 1.160e−03 is **2.78× the model's 4.173e−04 prediction, 92.6 % of the way to the band's upper edge**
  (1.252e−03). Level-by-level: the model's integrated coarse value **3.342463e−03 equals the solver's to 7 s.f.**;
  medium 1.4375e−03 vs the one-off 256² check 1.4194e−03 (+1.3 %); fine 1.1599e−03 vs the extrapolated
  4.173e−04. Pairwise error-vs-exact orders are **1.22 (coarse→medium) and 0.31 (medium→fine)**; the
  Richardson extrapolate of the triple is **1.1125e−03, not 0**, against an exact reference. Read: the E2
  triple is converging **toward a non-zero floor** rather than toward the exact solution — a Roache
  CONVERGING state with a high apparent order is exactly what a difference-based order reads when the
  increments shrink faster than the error does. **Raised to the supervisor as a check-3 item; not a
  re-grade.** Candidates the lane did NOT test: the periodic seam (the grader's control 2 reads a velocity
  seam mismatch of 4.89e−05 in the exact field construction), and any Δt-independent part of the error.
- **G-F20-2:** fine value inside the band but the triple **predicted NON-MONOTONE → NOT A RESULT**.
  *Outcome:* the KE triple is **monotone (all three below exact), CONVERGING at p = 1.28 → PASS.** The
  registered outcome was **MISSED in the conservative direction.** Signed KE errors: coarse **−1.5207e−05
  (the model's integrated coarse value −1.521e−05 to 4 s.f.)**, medium −7.15e−05 (256² check: −7.06e−05),
  fine **−9.47e−05 where the two-term extrapolation said +1.034e−04** — the sign the pre-registration itself
  said could not be extrapolated. Magnitude 0.40× the fine-level |S| + |BΔt| basis; inside the band.

No band was widened, no threshold moved, no order range revised; the pre-registration stays as frozen.

## 3. Rule 4 completion evidence, per level, from the case's own files

| level | cells | steps (`Time =` lines) | `RC.txt` | `End` | last `Time =` | `endTime` | fields at `10/` | age guard: `10/{rho,U,p,T}` newer than `0/U` | ClockTime s | ExecutionTime s |
|---|---|---|---|---|---|---|---|---|---|---|
| coarse 128² | 16,384 | 4,000 | 0 | yes | 10 | 10 | rho U p T | yes (0/U 1787766751 < 10/* 1787766795) | 44 | 44.36 |
| medium 256² | 65,536 | 8,000 | 0 | yes | 10 | 10 | rho U p T | yes (0/U 1787766798 < 10/* 1787767175) | 377 | 376.08 |
| fine 512² | 262,144 | 16,000 | 0 | yes | 10 | 10 | rho U p T | yes (0/U 1787767184 < 10/* 1787770883) | 3,699 | 3,697.95 |

Artifacts: `verification/runs/F20_ISENTROPIC_VORTEX_runs/<level>/{RC.txt,log.rhoCentralFoam,system/controlDict,0/U,10/}`.
Frozen paths: **15 of 15 disk == blob at `548fc02e`** (`git hash-object` vs `git rev-parse 548fc02e:<path>`),
including the grader (`68057e2e`), the launcher `run_f20.sh` (`49523e10`) and the pre-registration (`44572686`).
`STATUS.F20_ISENTROPIC_VORTEX` (`launcher_rc=0 end=2026-08-26T19:01:23Z`) is an INFRASTRUCTURE record (L-342)
and was not a grading input.

## 4. Measured cost (ClockTime × ranks ÷ 60; all levels serial on 1 rank)

| level | predicted (prereg §8) | actual core-min | ratio |
|---|---|---|---|
| coarse | 0.85 | 0.7333 (44 s) | 0.86 |
| medium | 6.6 | 6.2833 (377 s) | 0.95 |
| fine | 52.5 | 61.65 (3,699 s) | **1.17** |
| **total** | **60.0** (cap 240) | **68.667 gross** (4,120 s) | **1.144** |

Integer-second quantisation ± 0.0083 core-min per level. ClockTime − ExecutionTime = 0 / 1 / 1 s: **no
contention** on any level. **28.6 % of the 240 core-min cap.** Dollars at $0.0513/core-h: **$0.0587 — DERIVED,
NOT MEASURED** (reported-by-owner rate; the box cannot read its own billing). Per-cell-step rate by level:
0.67 / 0.72 / 0.88 µs (gross, ClockTime ÷ cell-steps) against the 0.75 µs basis — the miss is the **fine
level's per-cell-step term rising with cell count**, not the per-step overhead and not contention.
**Waste: 0 core-min**, named separately. The fine level's 3,699 wall s exceeds the 3,600-s figure of the
stall rule by the letter; it is the level's registered work run to `End`, not a stall — carried GROSS, as
C-133 ruled for F15.

**Runner `CAP_OVERRUN.txt` (18:57:38Z, `cases/F20_ISENTROPIC_VORTEX/CAP_OVERRUN.txt`):** fired at elapsed
3,975 s > 1.10 × 3,600 s, i.e. at **1.10 × the ESTIMATE (60 core-min), not the CAP (240 core-min)**. The run
was not killed and never approached the cap. **An infrastructure record, not a cap breach**; the runner defect
is fixed under the supervisor's 17:46Z order (`scripts/queue_runner.py`, `QUEUE_RUNNER.md` §5).

## 5. Planted-control readback (rule 3), from `F20_GRADED.json`

- G-F20-1 reader `e2_from_files`: plant 5.336618e−04 into a copy of `fine/10/rho`, read back Δ = 5.336618e−04
  (reader Δ equal) — **passed**.
- G-F20-2 reader `ke_from_files`: plant 1.267224e−03 into the same artifact, read back Δ = 1.267224e−03 — **passed**.
- Nine registered controls all `passed: true`: symbolic substitution into the co-moving steady Euler
  equations (four zero residuals); planted 1.1β in T non-zero (0.0898); field at T equals field at 0 and
  moves at T/2 (diff 0.506); constant-ratio refinement (h and Δt ratios 2.0/2.0); model mass-conserving and
  ordered; `grade_ladder` call-site census; solver dictionaries agree with registration (molWeight 8314.47,
  Cp 3.5, endTime 10, Kurganov, vanLeer/vanLeerV/vanLeer, Euler); reader parses real solver output
  (`F15_runs/coarse/4/{rho,U}`, 10,000 cells); L-342 infrastructure-vs-physics driven both ways.
- Gate demonstrations, each quantity shown able to take a passing and a failing value: G-F20-1 inside
  4.173e−04 / outside 1.669e−02; G-F20-2 inside 1.005626 / outside 1.007638.

## 6. What this lane could not verify

- Whether the E2 floor (§2) is a property of the solver, of the exact-field construction at the seam, or of
  the grader's cell-centre sampling: not tested; a successor registration would have to say which.
- Nothing was sent, filed or uploaded (rule 7).

---

## ADDENDUM — 2026-08-27, cfd lane R2: THE ADDRESS OF RECORD IS THE CAMPAIGN FILE

**Appended at the foot on the cfd-supervisor's ruling of 2026-08-27. It adds a
pointer and nothing else: no verdict, value, band, order, cost, control or
caveat above this line is altered, restated or withdrawn.**

**`verification/campaign/F20_ISENTROPIC_VORTEX_RESULTS.md` is the ADDRESS OF
RECORD for this verdict**, under `CLAUDE.md`'s WHERE THINGS LIVE table, which
puts grading records in `verification/campaign/` and run outputs in
`verification/runs/<CAMPAIGN>/` *"never beside the prose describing it"*. This
file is the grading lane's own output record and stays with its run; the
supervisor ruled on 2026-08-27 that **both files stay and neither is deleted.**

**BOTH FILES DERIVE FROM THE SAME SOURCE — `F20_GRADED.json` in this
directory, written by the frozen `grade_f20.py` (blob `68057e2e`, prereg
`548fc02e2ac8d1c27868af67a343f3a5495e8ecb`, rc 0, `GRADE_F20.err` empty).**
Neither was derived from the other, and **neither is independent confirmation
of the other**: they are two renderings of one grading run. **Two files carry
one verdict; that is one verdict, not two.** cfd lane R2 checked this file
against `F20_GRADED.json` and the level logs line by line on 2026-08-27 and
found **no discrepancy** in either verdict, both values, both bands, both
orders, both GCIs, both Richardson extrapolates, all six level values, the
three ClockTimes, the 68.667 core-min claim, the nine controls or the four gate
demonstrations.

**ONE CORRECTION, from the grader's own JSON, touching no verdict.** §5 above
attributes the 4.889408860664357e−05 periodic-seam velocity mismatch to *"the
grader's control 2"*. It belongs to `seam_mismatch.velocity` inside the control
named `field_at_T_equals_field_at_0_and_moves_at_T_over_2` — **the third
control**, not control 2 (`PZ-F20-BETA_planted_1.1beta_in_T_must_be_nonzero`).
The control reads `passed: true`. The original text above is **struck by this
addendum, not rewritten**, per standing rule 6.

**RULE 6 — LINE STABILITY, ASSERTED AND MEASURED.** This file is cited **by
line** by `docs/CAPABILITY_GRID.md:56` and `docs/capability/cfd_GRID.md:55`
(`:15-16`, `:30-32`, `:36-39`, `:44`, `:92-94`, all pinned `@ ca6a3164`).
**Lines whose number changed above this section: 0.** Verified mechanically in
the appending invocation, not asserted: the pre-append file's 8,572 bytes are
the byte-exact prefix of this one, and all five cited line ranges were read
back after the append and are byte-identical to their pre-append content.
