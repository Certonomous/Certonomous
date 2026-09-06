# `w4_stage_root.sh` — DELTAS from `d6rf4_stage_root.sh`

`w4_stage_root.sh` is built on the D6RF4 run-root stager model
(`cases/dafoam/ladder-a/A2/curriculum_D6RF4/d6rf4_stage_root.sh`), as
`W4_REANCHOR_PREREGISTRATION.md` §18 fix step 1 directs. This note records where
the two files agree and, more importantly, where W4's structure forced a
deliberate departure, so the departures are reviewed rather than assumed. A raw
line diff would be noise — the two solve different launchers — so this is the
clause-by-clause account.

## What is CARRIED unchanged (the model's disciplines)

- **The staging list is DERIVED from the launcher's own bytes, never hand-written.**
  D6RF4's antidote to the two-drifting-lists defect. Carried in spirit and in
  fact: `w4_stage_root.sh` writes no instrument name of its own.
- **A parser that discovers nothing REFUSES (exit 40), never "nothing to stage"**
  — the planted-zero shape in a stager (CLAUDE.md rule 3).
- **Source side asserted BEFORE any create** — every instrument source must exist
  and hash to the registered md5 before `mkdir`, so a bad source never leaves a
  half-root behind.
- **Live-work guard before any write** — `sudo -n docker ps` for the arm's
  container prefix (`w4ra_`), reported `UNMEASURED` when docker cannot be read and
  refusing only on a POSITIVE sighting (a failed read and an empty read are the
  same empty string; reading the second from the first is the planted-zero shape).
- **No `rm -rf`, no `rm -r`, no `find -delete`, no `git`.** It creates and copies;
  it never removes.
- **`0/` touched LAST** so the age-guard datum (rule 4) dates the run allowed to
  produce the answer.
- **Disjoint exit codes** so a `launch_cmd`'s `launcher_rc` names which layer refused.
- **`set -uo pipefail` with every step gating explicitly** (`set -e` does not gate
  at a harness Bash top level).
- **It launches nothing.** The re-fire is the supervisor's decision.

## What DEPARTS, and why each departure is forced

1. **The md5 authority is a REGISTRY, not assertion lines in the launcher.**
   D6RF4's launcher (`d6rf4_run_arm.sh`) carries `echo "$MD5_X $BASE/f" | md5sum -c -`
   lines, and the stager parses *those* for both the file set and the md5s. **W4's
   drivers carry no md5-assertion lines at all** (`run_one.sh`/`run_plateau.sh` are
   minimal retargets of S1's). So the md5 authority is moved to the frozen
   comparator's `STAGED_INSTRUMENTS` registry (`analyse_w4_reanchor.py`, prereg
   4.1), parsed from its bytes. The staging *file set* is still discovered from the
   drivers; the derived set must EQUAL the registry key set or the stager refuses
   (`REFUSE-COVERAGE`, exit 40) — the same drift check by a different instrument.

2. **The parse ROOT is the launch target, discovered transitively.** D6RF4 parses
   one launcher. W4's launch path is two files: the launch target `run_plateau.sh`
   (what F9's `launch_cmd` runs — the one given) and the `run_one.sh` it calls.
   The stager parses `run_plateau.sh` to discover the sub-launcher, the case
   subdir, and the beta input it reads (a `-betafile` that is NOT an `np.save()`
   target — `beta_fd.npy` is written, so it is an output and is not staged), then
   parses the discovered `run_one.sh` for its `python <x>.py` entry and its
   `-w /mnt/<subdir>` container workdir. Placement is derived: `.sh` → run root;
   `.py` and beta `.npy` → the case subdir.

3. **An existing run root is REFUSED (exit 43), not re-asserted.** D6RF4 re-asserts
   an already-present root (`STAGED_NOW=no`, every assertion still runs) so it is
   safe in front of every fire. W4's §18 fix step 1 and §3 (run root registered
   ABSENT) direct the opposite: **refuse to clobber.** A re-fire archives the old
   root by an explicit operator `mv`, never this file's implicit act.

4. **No item-ceiling guard.** D6RF4's stager runs `item_ceiling_guard.py` before
   the fire because its launcher does not self-cap. **W4's `run_plateau.sh` carries
   its own `CAP=150.0` core-min rule-12 STOP** (remaining-budget-is-the-timeout),
   so the cap lives in the driver and the stager adds none. This keeps the stager
   purely additive — it touches no cap, threshold or budget.

5. **The case state is copied with a REGISTERED exclusion set, then two overlays.**
   D6RF4 copies its `base/` wholesale (`cp -a "$D4_BASE_SRC" "$BASE/base"`). W4's
   registered case source (`…/W4-adjoint-pc-unblock/cbfs_beta`, prereg §3) also
   holds §3's cited artefacts — `processor*/`, `fdlogs/`, `fd_beta_*.npy`,
   `cbfs_beta_grad.npy` (the REFUSED 1e-6 gradient) — and its own `runScript.py` is
   the **rejected 6,230-byte alternative** (prereg 4.1). So the copy excludes the
   §3 cited-artefact set (a *registered* refusal, cited, not a free-hand list) and
   the rejected script, then overlays the registered `runScript.py` (I1) and
   `fd_beta_ones.npy` (I4) from the instrument set. mtimes are preserved (§3
   read-only inputs); the source is never written.

## The drive

`w4_stage_root_control.py` drives the ACTUAL staging (prereg §18 fix step 2 — not a
BASE-redirected pre-populated sandbox, which §18 records as the defect): it runs
the stager into a sandbox root, reads that root back from disk to confirm it is
populated, then runs the frozen `run_plateau.sh` from the populated root (container
mocked via the §17 `drive_evidence/mock_sudo.sh` + `mock_solver.py`) and grades the
driver-produced tree with the frozen comparator. Both directions per rule 3: D1 is
the plant (populated root → 16 legs → comparator PASS); D2/D3/D4 are the refusals
(existing root → 43, md5 mismatch → 41, launch target absent → 40). The registered
run root is asserted untouched throughout. Evidence:
`drive_evidence/W4_STAGE_ROOT_DRIVE.txt`.
