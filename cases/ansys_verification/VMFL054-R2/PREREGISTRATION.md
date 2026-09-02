# VMFL054-R2 — Laminar Flow in a Trapezoidal Driven Cavity — PRE-REGISTRATION **FROZEN**

**FROZEN — THIS IS THE FREEZE COMMIT.** Frozen by `ansys-verification-supervisor` at **2026-09-02T21:53:01Z**
after a personal §3 check-4 diff re-read. Drafted by `ansys-lane-opus48` (`claude-opus-4-8[1m]`)
2026-09-02. A minimal re-registration of VMFL054: **exactly ONE file changes from R1 — the driver —
and only to source the OpenFOAM environment.** This is the VMFL064→VMFL064-R2 pattern.

**WHY THIS IS A NEW REGISTRATION AND NOT AN AMENDMENT.** First compute has occurred on R1 (the daemon
launched it), so under `CLAUDE.md` rule 2 **R1's gates are CLOSED and cannot be reopened** — an amendment
could not lawfully touch them, and none is attempted. R2 is a fresh registration citing R1, exactly as
§6 requires of a re-run after a repair. **No gate is re-chosen here**, and that is provable rather than
asserted: see the blob identity below.

**THE GRADING PATH IS PINNED BY SHA AT THIS COMMIT (rule 2):**

- comparator `grade_vmfl054_r2.py` — blob **`0e9f3fe14fb7f8713bed0a68ad34454697350a60`**
- driver `run_vmfl054_r2.sh` — blob **`d72ad7a9fcde7795c45de74767614e0d4013f741`**

**SUPERVISOR'S §3 CHECK-4 RECORD — THE GATE PROVABLY DID NOT MOVE.** The R2 comparator is
**BYTE-IDENTICAL** to R1's frozen comparator: both hash to `0e9f3fe14fb7f8713bed0a68ad34454697350a60`, the blob frozen at `05ec949e`. A gate
cannot have been re-chosen in a file that did not change by one byte — this is a stronger guarantee than
any reading of the constants, and it is why a renamed comparator was checked by CONTENT and not by name.
All **nine** case inputs likewise verified byte-identical to their blobs at `05ec949e` (`0/U`, `0/p`,
`transportProperties`, `momentumTransport`, `turbulenceProperties`, `fvSchemes`, `fvSolution`,
`blockMeshDict.template`, `controlDict.template`). The driver diff was read line by line and is confined
to: the three env lines (`source .../etc/bashrc` plus `command -v` asserts on `blockMesh` and
`simpleFoam`), the `VMFL054`→`VMFL054-R2` relative path in the integrity check, the script name and echo
strings, and comments. **The cap logic, the `touch 0/U 0/p` age-guard reference, the level definitions
`NX/NY = 40/80/160`, the `ENDTIME` substitution and the freeze-check mechanism are all unchanged.**

**THE PREDICTION STANDS UNCHANGED FROM R1 AND IS NOT RE-DERIVED:** `GATE FAIL` on the order limb at a
GCI of ~0.011 %, with the standing caveat that a 3-point triple cannot distinguish genuine
super-2nd-order convergence from a pre-asymptotic artefact — so the failure is **not** to be narrated as
vindicated superconvergence. Gates are CLOSED from this commit.

## 1. Why R2 exists — R1's infrastructure abort (not a physics result)
R1 (frozen `05ec949eb4bd12d88a559f30e0f74ad5bd4f5e98`) was filed, committed (`5c536341`)
and launched by the daemon at 2026-09-02T21:43:57Z. **Its driver did not source the
OpenFOAM environment.** The daemon runs the driver in a plain shell where `FOAM_APPBIN`
is not on PATH, so `blockMesh` was `command not found` (rc 127); the driver aborted at L1
at **zero physics compute** (`launcher_rc=10`). The frozen comparator, run on the aborted
tree, correctly **REFUSED (exit 2)**: "RUN_RC absent … cannot confirm solver rc==0
(rule 4)" — the strict-completion guard doing its job.
- **Cause class:** infrastructure / launcher defect (NOT physics) — the same class as
  VMFL064 attempt-1. The team's reference drivers VMFL063:177-178 and VMFL064-R2:158-159
  both source the bashrc and assert the solver on PATH; **R1 dropped exactly those lines.**
  R1's drafting lane (this lane) owns the miss; the smoke tests masked it because they
  sourced the environment manually in the test harness.
- **R1's disposition is the supervisor's** — a `NOT A RESULT` on infrastructure grounds,
  recorded honestly. R1's run root and `05ec949e` freeze stand as the evidence.

## 2. The ONE change in R2 (and proof it works)
`run_vmfl054_r2.sh` adds, unconditionally near the top:
```
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source ..."; exit 2; }
command -v blockMesh  >/dev/null || { echo "ABORT: blockMesh not on PATH ..."; exit 2; }
command -v simpleFoam >/dev/null || { echo "ABORT: simpleFoam not on PATH ..."; exit 2; }
```
(plus the HEAD-blob rel path updated to `.../VMFL054-R2/case/`). **Proven under a
BARE shell** (no manual sourcing, replicating the daemon): with `blockMesh` NOT on PATH
beforehand, the driver self-sourced and ran L1 clean — rc 0, wrote time dir 741, RUN_RC 0,
probe file present.

## 3. Byte-identity to R1's frozen package (verified 2026-09-02)
- Comparator `grade_vmfl054_r2.py` == R1 frozen `grade_vmfl054.py`: both
  `0e9f3fe14fb7f8713bed0a68ad34454697350a60`.
- All 9 `case/` inputs hash-identical to `05ec949e:cases/ansys_verification/VMFL054/case/*`.
- Comparator selftest: 12 arms, **ALL PASS** (dual plant, known-bad refusal, 4 completion
  BAD arms refusing exit 2, Roache classifier).

## 4. Everything else — UNCHANGED from R1 (see R1 PREREGISTRATION.md, frozen 05ec949e)
Geometry, mesh, grid triple (L1/L2/L3 = 40/80/160, r=2), solver (simpleFoam laminar
SIMPLEC, Re=400), gate quantity (u_x at the cavity centre, `cellPoint` interpolation),
cost (≤3 core-min; scratch triple measured 1.07), guards, and cost_basis are as R1.

## 5. Rulings carried forward VERBATIM (in the frozen bytes, §11.2)
- **Ruling 1 (BC direction):** both base walls +x co-directional, disclosed as our
  reading; case **capped at `GATE REACHED`**; deferred D&V validation may need a further
  R with corrected BCs, not merely figure digitization.
- **Ruling 2 (observed-order band):** `P_OBS_LO=1.0`, `P_OBS_HI=3.0`, `GCI_FINE_MAX=0.05`
  freeze VERBATIM; a `GATE FAIL` at GCI ≈ 0.011 % is **predicted**, recorded unsoftened;
  the GCI-primary lesson is banked FORWARD (a future registration may adopt it a-priori,
  citing the graded row). Caveat: p ≈ 3.4 is a 3-point estimate with a small second
  difference — genuine >2 order vs pre-asymptotic is unresolved without an L4; the register
  row must not assert "superconvergence."

## 6. Grading path (to be pinned by sha at the R2 freeze commit)
Comparator `grade_vmfl054_r2.py`; driver `run_vmfl054_r2.sh`; case `case/`. **This FROZEN registration
awaits the supervisor's §3 check-4 diff re-read (the driver is the only diff) and the
freeze commit.** Then a fresh run root `verification/runs/ansys_verification/VMFL054-R2/`
and a top-level queue entry. **I froze nothing, graded nothing.**
