# VMFL003-M2 — LANE REPORT OF RECORD (ansys-lane-opus48, Opus 4.8, 2026-08-25)

**NOT FILED ANYWHERE.** Nothing here leaves this box (CLAUDE.md rules 7, 8). This is the
one-way lane→supervisor channel of record; the scratchpad is not a handoff channel (L-186).

## 1. What this lane did (in order)
1. Read the frozen run-1 inputs, both M2 comparators and the M2 draft at HEAD.
2. Built the four-arm case tree: a model-agnostic **base** (`case/`, byte-faithful copies
   of run-1's frozen inputs minus the model) and four **arm overlays** (`arms/`):
   - **A `kEpsilon`** — identical to run 1 (control, converge-only).
   - **B `realizableKE`** — RASModel keyword only; coeffs A0 4.0 / C2 1.9 / sigmak 1.0 /
     sigmaEps 1.2, read from `…/RAS/realizableKE/realizableKE.C` (not recalled).
   - **C `RNGkEpsilon`** — RASModel keyword only; coeffs Cmu 0.0845 / C1 1.42 / C2 1.68 /
     C3 0 / sigmak 0.71942 / sigmaEps 0.71942 / eta0 4.38 / beta 0.012, from
     `…/RAS/RNGkEpsilon/RNGkEpsilon.C`.
   - **D `kOmegaSST`** — DECLARED coupled change: `0/omega` replaces `0/epsilon`
     (omega_in = epsilon_in/(Cmu·k_in) = 19964.892656248117 1/s, returns epsilon_in
     exactly), and `system/fvSchemes`/`fvSolution` swap div(phi,epsilon)→div(phi,omega)
     and the `(U|k|epsilon)`→`(U|k|omega)` solved-variable class + relaxation. nut/k wall
     treatment held identical to run 1 (nutkWallFunction, kqRWallFunction); omega uses
     omegaWallFunction.
3. Wrote the launcher `run_vmfl003_m2.sh` (four arms × six meshes; freeze guard; both
   comparators verify-frozen; pre-existing-dir guard; per-arm 40 + slate 160 core-min caps;
   age-guard datum; birth-certificate step in `mesh_case`). **It declares no graded compute
   and the graded run is LOCKED for the supervisor.**
4. **Authorised pre-freeze compute (own 5-core-min cap, scratch OUTSIDE
   `verification/runs/`):** blockMesh/checkMesh/topoSet on the six meshes + a one-iteration
   per-arm smoke test. Measured total **2 wall-s = 0.033 core-min** at RANKS=1.
5. Ruled the reference kind into §2 (V), updated §13 boundary, produced the frozen
   `PREREGISTRATION.md` from the draft (draft retained as history).

## 2. What this lane measured

### Mesh quality vs `docs/standards/MESH_STANDARD.md` (all six meshes born **clean**)
| mesh | cells | max non-ortho (gate 70) | max skew (gate 4) | max aspect (adv. 1000) | verdict |
|---|---|---|---|---|---|
| L1_250x5 | 1250 | 0.0 | 0.330796465395 | 40.0381 | clean |
| L2_500x5 | 2500 | 0.0 | 0.330796465395 | 20.0191 | clean |
| L3_1000x5 | 5000 | 0.0 | 0.330796465395 | 10.0095 | clean |
| D_500x3 | 1500 | 0.0 | 0.330796465394 | 12.0114 | clean |
| D_500x4 | 2000 | 0.0 | 0.330796465394 | 16.0152 | clean |
| D_500x6 | 3000 | 0.0 | 0.330796465395 | 24.0229 | clean |

All non-orthogonality 0 and skewness ~0.33 — far inside the hard gates. Aspect ratio
(10–40) is wall-normal boundary-layer anisotropy on orthogonal cells — the aligned,
legitimate case (MESH_STANDARD §3.3), and two orders of magnitude below the 1000 advisory.
`checkMesh -allGeometry` prints "Mesh OK." for every mesh. Birth certificates (§6 of the
standard) written and admitted (`certificate_admits` True) for all six, kept under
`mesh_certificates/<mesh>/birth_certificate.json` with the three mesh logs beside each.
**This closes the "checked but uncertified" gap the standards read flagged (23 mesh-check
logs, 0 certificates): these are six certified meshes, not a 24th uncertified one.**

**Certificate ↔ graded-mesh binding is MEASURED, not assumed:** blockMesh is deterministic
here — an independent regeneration of L1 reproduced the certificate's `points_sha256`
(`8e10d678…8547`) byte-for-byte. The graded run regenerates each mesh from these frozen
templates and re-certifies at launch; the pre-freeze certificate therefore certifies the
mesh the graded run will use.

### Smoke test (1 iteration, coarsest 250x5, per arm) — ALL FOUR PASSED
Each arm: rc=0, an `End` line, and its second turbulence field assembled and solved
(A/B/C: `Solving for epsilon`; D: `Solving for omega`; `k` for all). This is the check a
comparator `--selftest` cannot make — it proves the CASE and LAUNCHER, not the grader
(VMFL045 passed 45/45 selftest and died on timestep 1; run-1's launcher passed 60/60 while
unrunnable). Full smoke logs under `smoke/<arm>/log.simpleFoam`. **No gate quantity was
produced (a one-iteration run holds no converged Δp), so nothing here can bias the gate.**

### Cost (rule 12)
Pre-freeze mesh+smoke: measured 0.033 core-min against the task's 5 core-min cap (ratio
0.007). Graded-run estimate stands at ~113 core-min / 160 cap, $0.137 derived at
$0.0513/core-h — **derived, not measured** (the box cannot read its own billing). The
estimate-vs-actual calibration row for the graded run is owed at graded completion, not now.

## 3. Decisions carried / confirmed
- **Reference kind: V, RULED** (Sanaa 2026-08-25 limb a — a correlation scores V, never P;
  a correlation carried by a public primary source is still a correlation). Open-question
  framing deleted from §2; §13 open-call (a) closed.
- **Falsification arm preserved verbatim (§7 Arm 5):** if all four models' L3 Δp lie within
  ≤1.0 % of each other AND all four GATE FAIL in −4.0…−5.0 %, model selection is FALSIFIED
  and the miss is not the wall treatment — recorded as a GATE FAIL slate, not softened.
- **GATE REACHED ceiling — two reasons kept visibly separate (§6):** Reason 1 grid-structural
  (N-AV10, R⁺=408 radial channel unrefinable → no trustworthy radial order; operative and
  independent of Sanaa) vs Reason 2 Sanaa's success condition. Not conflated.
- **Grid family: keep run-1's** (my recommendation, ACCEPTED). Coarsening L1 recovers only
  an axial order and does not lift the ceiling.
- **Ladder uniform across all four arms** (my own correction, ACCEPTED): the ceiling, y+
  minimum and endTime bump apply to all four, so all four share one comparator per family.

## 4. Record-update DRAFTS (§7 duty; supervisor to land, NOT this lane)
Per the supervisor's tooling prohibition, **`scripts/append_record.py` was NOT used** and
any id must be **hand-derived inside the committing shell, reading the tail with eyes** (the
tool is blind to em-dash headings and mis-assigns). Candidates for the supervisor's read:
- **NUMERICS (next id `N-AV12`, derived by hand: all 32 `N-*` are period-style, N-AV strict
  and permissive maxima agree at 11):** *"With a standard log-law wall function the wall
  shear is imposed by the log law from the first-cell k, not computed by the interior
  two-equation closure; kEpsilon / realizableKE / RNGkEpsilon sharing nutkWallFunction are
  therefore expected to share their developed-pipe friction. Confirmed pre-registered as
  §7 Arm 4; to be measured by the graded slate."* — LAND ONLY after the graded slate
  measures it, not on prediction.
- **LESSON (id hand-derived at land time, `max+1` from the tail):** the certificate↔mesh
  determinism method (a pre-freeze scratch mesh can be certified and the certificate is
  valid for the graded mesh iff blockMesh determinism is measured, not assumed). Draft only.

## 5. Commits (this lane; private-index protocol, per-item, post-commit verified)
- **Commit 1 (inputs, NO GRADED COMPUTE):** `case/`, `arms/`, `run_vmfl003_m2.sh`,
  `mesh_certificates/`, `smoke/`, this `LANE_REPORT.md`.
- **Commit 2 (FREEZE, separate & later):** `PREREGISTRATION.md` alone.
- Blob hashes (git hash-object == committed blob):
  - `PREREGISTRATION.md` = **cdbf2659b6eec2599fc3eda7a149aaca391461b0**
  - `run_vmfl003_m2.sh` = **29a53e035a1bb595d7dde69b0e2e6b77bcd561b4**
  - `grade_vmfl003_m2.py` (already frozen at HEAD) = **6dcc99940154ea204a598ba2118042bf972a786d**
  - `grade_vmfl003_m2_omega.py` (already frozen at HEAD) = **b595c86a4b8580d5928b4d4dd1458698f6de8ac2**
- Commit shas + timestamps: recorded in the dated addendum below after the freeze lands.

## 6. What this lane could NOT verify / boundary
- **The GRADED verdicts are not measured** — the graded run is LOCKED and is the
  supervisor's after the four §3 checks. No arm value against the gate exists.
- The graded-run cost is an ESTIMATE; its calibration is owed at completion.
- **A supervisor's message is not Sanaa's consent (rule 9).** This lane acted only within
  its own task's authorisation (mesh + 5-core-min smoke); the predecessor lane's refusal to
  widen scope on a message alone was correct and stands.

---
## Addendum, 2026-08-25 — the two commits, as landed
- **Commit 1 (inputs, NO GRADED COMPUTE):** `fd6427917238f031f59e767de350d5581054744c`
  at **2026-08-25T16:38:22+00:00** — 54 files (case tree, arm overlays, launcher, six mesh
  certificates + logs, four smoke logs, this report). No PREREGISTRATION.md.
- **Commit 2 (FREEZE, separate & later):** `c5fdcad402fe8be99e344580b7a5f08d54434a5a`
  at **2026-08-25T16:38:51+00:00** — `PREREGISTRATION.md` alone, blob
  `cdbf2659b6eec2599fc3eda7a149aaca391461b0`, on-disk == HEAD (freeze verified).
- Ordering holds: grading path (both comparators at HEAD, blobs
  `6dcc9994…` / `b595c86a…`) and inputs+launcher (commit 1) exist **before** the freeze
  (commit 2); all before any graded solver. The graded run remains LOCKED for the supervisor.
- This addendum itself is a post-freeze, non-gating edit to this report; it alters no gate,
  threshold, band, cap, label, or the frozen `PREREGISTRATION.md`.
