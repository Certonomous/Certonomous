# JF1R-QB4 — rule-4 completion grading of the quiet-box 4-rank parallel rerun

**Label: FEASIBILITY / TIMING RERUN. NO GATE, NO THRESHOLD, NO VERDICT of the
fixed vocabulary attaches to any run graded here** (registration:
`verification/campaign/JF1R_QB4_QUIET_BOX_RERUN_NOTE.md`, frozen at commit
`4778bf75572dffc3dcd8779433ea5b585c5c390b`, blob
`c05afbf6a37deea2575d8cd1f7b3785942848acf`; the launcher verified commit,
in-commit blob and working-tree copy before solving — `prereg_check
VERIFIED` in `cases/JF1_JET_FLAP/RUN_STATUS.JF1R_QB4_SWEEP.guard.txt`).
This record grades **completion only**, per CLAUDE.md rule 4, as §2 of the
frozen note requires before any timing number is used.

Graded 2026-09-02 by the cfd demo lane, from the artifacts on disk under
`verification/runs/JF1_jet_flap/JF1R_QB4_<TAG>/`. Every figure below is read
from a named artifact, none is retyped from memory.

## 1. Rule-4 clauses, per case — ALL FIVE CASES COMPLETE

Clauses, as applied to this family (steady incompressible `simpleFoam`,
`endTime 8000`; field set `U p p k omega nut` per the case's own `0/`;
the launcher touches `0/*` and `processor*/0/*` last before the solver, so
the age guard dates against the case's own `0/`):

| Case | rc | `End` lines | last `Time =` | `Time` count | `ExecutionTime` count | fields at `8000/` (reconstructed) | `processor*/8000` present | age guard (recon + per-processor) | wall_s | core-min (×4 ranks) |
|---|---|---|---|---|---|---|---|---|---|---|
| JF1R_QB4_UNBLOWN | 0 | 1 | 8000 | 8000 | 8000 | U p k omega nut all present | 4 of 4 | every `8000` field newer than `0/` max | 468 | 31.2000 |
| JF1R_QB4_CMU005 | 0 | 1 | 8000 | 8000 | 8000 | U p k omega nut all present | 4 of 4 | every `8000` field newer than `0/` max | 344 | 22.9333 |
| JF1R_QB4_CMU010 | 0 | 1 | 8000 | 8000 | 8000 | U p k omega nut all present | 4 of 4 | every `8000` field newer than `0/` max | 350 | 23.3333 |
| JF1R_QB4_CMU020 | 0 | 1 | 8000 | 8000 | 8000 | U p k omega nut all present | 4 of 4 | every `8000` field newer than `0/` max | 417 | 27.8000 |
| JF1R_QB4_CMU040 | 0 | 1 | 8000 | 8000 | 8000 | U p k omega nut all present | 4 of 4 | every `8000` field newer than `0/` max | 397 | 26.4667 |

Sources per case: `SOLVER_RC.txt` (rc), `log.simpleFoam` (`End`, `Time =`,
`ExecutionTime` counts), the reconstructed `8000/` directory and the four
`processor*/8000` directories (fields), filesystem mtimes of `8000/*` against
the max mtime of the same case's `0/*` (age guard),
`RUN_STATUS.JF1R_QB4_<TAG>.txt` (wall_s, core_min_MEASURED). Launcher exit:
`rc 0`, `stage_at_exit done` (sweep guard status file above).

**Every clause holds on every case. All five runs are COMPLETE under rule 4
and their timing numbers are usable** in the sense of the frozen note §2 —
which, per Sanaa's 2026-09-02 ~09:30Z ruling (§4 below), no screen now takes.

## 2. The measured timing record (MEASURED, from the runs' own logs)

- Per-case walls and core-minutes: table above; sum **131.7333 core-min**
  (also in `JF1R_QB4_READOUT.txt`).
- Waves as launched: wave 1 = CMU040, UNBLOWN, CMU010 (03:11:54Z start,
  slowest member UNBLOWN at 468 s); wave 2 = CMU005, CMU020 (03:19:42Z
  start, slowest member CMU020 at 417 s). Sweep span first start to last
  end **893 s ≈ 14.9 min** (guard status file), consistent with the two
  waves' slowest members (468 + 417 = 885 s) plus handover.
- Slowest member overall by measured wall: **UNBLOWN, 468 s = 7.8 min** —
  NOT the strongest-blowing case this time (the landed serial sweep's
  slowest was CMU040 at 1,512 s).

## 3. The registered physics cross-check (a consistency check, not a gate)

Note §2 registers: each blown case's settled lift against the landed serial
sweep's value for the same `C_mu_jet`, expected within 1%. Measured from the
tail rows of each case's own `coefficient.dat` at `Time = 8000` (surface
`Cl`; the jet-reaction term is the same frozen constant per `C_mu` on both
executions, so the surface coefficient carries the entire difference):

| `C_mu_jet` | QB4 `Cl` | landed serial `Cl` | gap |
|---|---|---|---|
| 0.05 | 0.405711 | 0.405733 | −0.0054% |
| 0.10 | 0.548834 | 0.548846 | −0.0023% |
| 0.20 | 0.743987 | 0.743999 | −0.0017% |
| 0.40 | 1.009966 | 1.009994 | −0.0028% |

All four blown rows agree within 0.006%, far inside the registered 1%.
UNBLOWN (not part of the registered check): `Cl` 0.000054 vs 0.000055 — an
absolute difference of 1e-6 on a symmetric section at zero incidence, where
a relative figure is meaningless; reported as a finding, grades nothing.

## 4. Screens: Sanaa's 2026-09-02 ~09:30Z ruling — the rewiring question is CLOSED

Captured at `etc/sessions/2026-09-02T0930Z_sanaa_jf1_65_and_no_tessellation.md`:
**JF1's screens keep her interim set — 4 workers | 19 core-min per run |
95 total | 6.5 min wall, predicted wall 4.9 min — permanently; no rewiring
to this rerun's measured numbers, now or later, absent a new ruling.** The
frozen note's §2/§5 expectation that the screens would take these numbers is
superseded by that ruling. This record and the measured figures above stay
internal, per rule 12 and the note's own words that the real record is never
altered by what the screens carry.

## 5. Estimate versus actual (rule 12)

Registered estimate **170 core-min** (frozen note §3, derived basis); cap
400 core-min structural. Measured actual **131.73 core-min** (sum of the
five `core_min_MEASURED` cells, wall × 4 ranks ÷ 60), gross = cleaned (no
case over 3600 wall s; max 468 s). **Ratio actual/predicted 0.77.** Gap
attribution: MISPREDICTION on the conservative side, two named causes.
(1) The estimate assumed 4-rank parallel efficiency 0.55–0.85 against the
serial baseline; the apparent per-case ratio serial-core-s / parallel-core-s
realised 0.76–1.07 (UNBLOWN 1,426/1,872 = 0.76; CMU005 1,466/1,376 = 1.07;
CMU010 0.93; CMU020 0.80; CMU040 1,512/1,588 = 0.95). (2) A ratio above 1 is
not superlinear speedup: the serial baseline was itself measured on a SHARED
box with no load record (frozen note §3 basis; compute note §4), so its
walls carry unquantified contention inflation and the derived estimate
inherited it. No contention on this run (queue-daemon busy-ceiling hold is
the quiet-box mechanism) and no waste (zero timeouts, zero failed cases, no
row near the 3600 s stall line). Dollars derived, not
measured, at the owner-stated $0.0513/core-h: ≈ $0.11 against ≈ $0.15
estimated. The calibration row lands in `docs/COST_CALIBRATION.md` per that
file's append rules; this section is its cited source.
