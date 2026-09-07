# MP-A1V INSTRUMENT MD5 TABLE — FROZEN 2026-09-07

The grading + launch apparatus for `CURRICULUM-MP-A1V`. All md5s are the on-disk
bytes at authoring; the freeze (the dafoam-supervisor's act) hash-locks the grading
path (`mpa1v_grade.py`) and pins the apparatus. **ALL_PINS_MATCH = 1** (every pin
below equals its guarded file). **NOTHING FROZEN / COMMITTED / LAUNCHED.**

## Instrument md5s (on disk)

| file | md5 | provenance |
|---|---|---|
| `mpa1v_grade.py` | `0a41208ee834df2b413b944938587a67` | derived from `mpa1_grade.py` (DELTAS diff); THE GRADING PATH |
| `mpa1v_xf.py` | `ea53c04314f20c438de233101d5ce84d` | derived from `mpa1_xf.py` (DELTAS diff) |
| `mpa1v_runScript.py` | `bb3ba3a61b19dc8564e247cdb11e9147` | **byte-identical carry** of `mpa1_runScript.py` (the PRODUCER; staged AS `mpa1_runScript.py`, the name `mpa1v_xf.py`'s unchanged PRODUCER pin execs) |
| `mpa1v_run_arm.sh` | `eaf76e1b994f6209df784a82ed51c2cd` | derived from `mpa1_run_arm.sh` (DELTAS diff) — the launcher |
| `mpa1v_chain_driver.sh` | `96156dc58456eeece10ba3bee98c7454` | derived from `mpa1_chain_driver.sh` (DELTAS diff) — the stager/driver (UNGUARDED top of the pin chain; fixpoint terminates here) |
| `mpa1v_chain_driver.rc` | (contents `0`) | carry |
| `mpa1v_stall.py` | `5d112800fc34dc729c80c584d873eec7` | **byte-identical carry** of `mpa1_stall.py` (descriptive stall constants; no optimiser arm in MP-A1V) |
| `mpa1v_age_guard.py` | `7fe4352d36b7b48a5bb2885e225e455a` | **byte-identical carry** of `mpa1_age_guard.py` (parameterised; no arm-name deltas) |
| `mpa1v_stop_marker.sh` | `5063f90b227eb3a7341d18c6ca7b7824` | **byte-identical carry** of `mpa1_stop_marker.sh` (takes DECLARED/EXECUTED as args) |
| `mpa1v_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | **byte-identical carry** of `mpa1_aggregate_memory.py` |
| `mpa1v_decomposeParDict` | `e6f1b0060944bc86d6dff56480ad2bd4` | **byte-identical carry** of `mpa1_decomposeParDict` (np=1) |
| `reference/` | (carry) | REAL_SO1a MESH + arm logs the MESH arm/grader read |

Tutorial inputs are staged from `TUT_SRC=/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible`
by the driver, pinned by the six `MD5_TUT_*` (unchanged from MP-A1; verified present and matching).

## Pin fixpoint (ALL_PINS_MATCH = 1)

Every `MD5_*` pin in the driver and launcher equals its guarded file's on-disk md5,
verified after the last edit. The two DERIVED pins are cross-repinned last:
- `mpa1v_chain_driver.sh:MD5_LAUNCHER = c11db180…` → `mpa1v_run_arm.sh`
- `mpa1v_chain_driver.sh:MD5_GRADER   = 7c05866b…` → `mpa1v_grade.py`
- driver + launcher `MD5_RUNSCRIPT = bb3ba3a6…`, `MD5_XF = ea53c043…`, `MD5_DECOMP = e6f1b006…`;
  driver `MD5_AGG/STOP_MARKER/STALL/AGEGUARD` = the byte-identical-carry values above.

The **cpuset cascade**: pinning `CPUSET_REGISTERED = "12"` in the grader (from MP-A1's `"8"`)
changed the grader md5 to `7c05866b…`, which was cascaded into the driver's `MD5_GRADER`.
`mpa1v_run_arm.sh:CPUSET=12` and `mpa1v_grade.py:CPUSET_REGISTERED="12"` — G12 gates them equal.
**cpuset 12** chosen as a FREE core at authoring (only `d9succ`/15 live; 12 sits in one registered
sibling set, not 0, not 15, not T4d); re-confirm occupancy at launch.

## Sandbox dry-run of the pre-container integrity path (no run root, no container)

- Clean: the driver's existence + `md5sum -c` checks (against the case-dir sources) and the
  launcher's staged-name checks (runScript staged as `mpa1_runScript.py`, xf as `mpa1v_xf.py`,
  decomposeParDict) → **rc=0** (`DRYRUN_INTEGRITY_OK`).
- Planted: a one-byte corruption of the grader copy → its `MD5_GRADER` check **FAILS (caught)**,
  so the reader is not blind. Corrupted copy discarded; repo files never touched.

## Arm program / ride

- Arms: `MESH FV-S FV-P` (DECLARED=3), np=1, both rows. No O arm, no X arm.
- Ride: `mpa1v_run_arm.sh` sources `mpa1_xopt.json` from `MPA1_BASE` (MP-A1's frozen run root,
  read-only) per row (FV-S←O-S, FV-P←O-P), row-stamp checked; `mpa1v_grade.py` reads MP-A1's frozen
  adjoint (`MPA1_BASE/{XE-S,XE-P}/mpa1_X.json`) and carries G-OPT9 + J_baseline from MP-A1's grade.
- Cap authority: `mpa1v_grade.py:ITEM_CEILING_CORE_MIN = 33.0 == sum(CAPS)` asserted in `main()`;
  launcher per-arm caps MESH 5.0 / FV-S 14.0 / FV-P 14.0. No stale 183.5 anywhere.

**Freeze + launch are the dafoam-supervisor's acts, held for their final check-1.**
