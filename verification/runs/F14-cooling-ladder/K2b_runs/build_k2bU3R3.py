#!/usr/bin/env python3
"""build_k2bU3R3.py -- stage AND launch the K2b-U3-R3 run: the un-confounded
Test D at the nearest builder-feasible 59 mm UNIFORM mesh (137 000 cells), 80 s.

    python3 build_k2bU3R3.py stage
        # Stage the case dir K2bU3R3_D59 by running the FROZEN builder
        # build_k2bU3.build_3d() body VERBATIM (which calls mesh3d(H_CELL)),
        # with only the module CELL SIZE (0.059) and the write target redirected.
        # Writes system/, constant/, 0.orig/ and CASE.txt. Writes NO 0/ and NO
        # numeric time dir, so the rule-4 age guard is satisfiable. Refuses if
        # the case dir already exists. (Freeze-time step; run by the supervisor.)
    python3 build_k2bU3R3.py run --case K2bU3R3_D59 --cap-core-min 66 --ranks 1 [--no-detach]
        # THE LAUNCH. Age guard (rule 4 / prereg §5.2): REFUSE if 0/ or a numeric
        # time dir already exists. Arm 0/ from 0.orig AT LAUNCH (so 0/T is touched
        # last and dates the run). blockMesh, checkMesh, then the transient solver
        # under a HARD cap of 66 core-min that argv CANNOT widen. Writes COST.txt
        # in core-minutes FIRST and unconditionally. Reaching the cap without
        # completion -> BLOCKED over-cap (rule 12), not a graded outcome.

FROZEN, UNCHANGED, imported NOT edited (rule 6):
  build_k2bU3.py  git blob efc5f22d...  (mesh3d, build_3d, control_dict, TRANS_FVSOL)
  build_k2b.py    git blob 16e38080...  (geometry constants + field/write helpers)
Only the CELL SIZE (H = 0.059 m) and the CASE NAME (K2bU3R3_D59) differ from the
frozen 100 mm build_3d(); every field / BC / controlDict / 70%-provisioning step
is the frozen build_3d() body run verbatim (K2bU3R3_PREREGISTRATION.md §2.4, §3, §6).

WHY THIS IS A NEW FILE, NOT A DIFF OF AN R2 RUNNER: K2bU3R2 was build-infeasible
(60 mm fails the frozen divs() 2% guard) and its named run_k2bU3R2.sh was never
written; the predecessor runner run_k2b.sh drives the STEADY solver with NO cap.
So the run() logic MIRRORS run_k2b.sh's structure (source the OpenFOAM bashrc
before any solver call; arm 0/ from 0.orig; blockMesh / checkMesh / 'Mesh OK';
time the solve; COST.txt first and unconditional -- run_k2b.sh:48-56 lesson) and
adds only (a) the transient solver, (b) the hard cap, (c) refuse-if-0/-or-time-dir
in place of run_k2b.sh's rm -rf 0, per the rule-4 age guard.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = "K2bU3R3_D59"
H    = 0.059                       # nearest-to-60 mm size passing the FROZEN
                                   # build_k2bU3.divs() 2% guard on ALL 5
                                   # intervals (prereg §2.2) -> 137 000 cells.
CAP_CEIL_CORE_MIN = 66             # HARD ceiling (prereg §6). argv CANNOT widen it.
RANKS = 1                          # serial (prereg §6; no decomposeParDict).
SOLVER = "buoyantBoussinesqPimpleFoam"
LOGNAME = f"log.{SOLVER}"
OF_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

NUM = re.compile(r'^-?[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?$')


def _numeric_time_dirs(case):
    """Numeric OpenFOAM time dirs present in `case` (0.orig is the template, not
    a time dir; 0/ is checked separately)."""
    out = []
    for d in sorted(os.listdir(case)):
        if d in ("0", "0.orig"):
            continue
        if os.path.isdir(os.path.join(case, d)) and NUM.match(d):
            out.append(d)
    return out


# ---------------------------------------------------------------------------
def stage():
    """Stage K2bU3R3_D59 by running the FROZEN build_k2bU3.build_3d() body
    verbatim, with only the module cell size and the target dir redirected.
    build_3d() hard-codes name='K2bU3_D' and reads the module globals H_CELL
    (=0.1) and HERE; we import the frozen module, set its H_CELL to 0.059 and
    redirect its HERE to a private staging dir (holding a symlink to the frozen
    K2b3D_probe template it copies from), call build_3d() UNCHANGED, then move
    the built tree to K2bU3R3_D59. NOTHING in build_k2bU3.py or build_k2b.py is
    edited (rule 6); only two module globals are reassigned IN THIS PROCESS, and
    restored in the finally. No 0/ and no numeric time dir are written (rule 4)."""
    dst = os.path.join(HERE, CASE)
    if os.path.exists(dst):
        sys.exit(f"REFUSE (exit 2): {dst} already exists; the age guard (rule 4) "
                 f"requires a fresh tree with no 0/ and no time dir.")
    sys.path.insert(0, HERE)
    import build_k2bU3 as B3                       # FROZEN, imported not edited
    probe = os.path.join(HERE, "K2b3D_probe")
    assert os.path.isdir(probe), f"frozen template {probe} missing"
    staging = tempfile.mkdtemp(prefix="k2bU3R3stage_", dir=HERE)
    saved_here, saved_h = B3.HERE, B3.H_CELL
    try:
        os.symlink(probe, os.path.join(staging, "K2b3D_probe"))
        B3.HERE, B3.H_CELL = staging, H            # redirect + resolution ONLY
        name, n = B3.build_3d()                    # FROZEN build_3d body, verbatim
        built = os.path.join(staging, name)        # staging/K2bU3_D
        # re-point the case IDENTIFIER in CASE.txt (K2bU3_D -> K2bU3R3_D59), the
        # analogue of the analyse re-point; the rest is the frozen build's output.
        cp = os.path.join(built, "CASE.txt")
        open(cp, "w").write(open(cp).read().replace("K2bU3_D", CASE, 1))
        shutil.move(built, dst)
    finally:
        B3.HERE, B3.H_CELL = saved_here, saved_h
        shutil.rmtree(staging, ignore_errors=True)
    assert not os.path.isdir(os.path.join(dst, "0")), "staged tree must have no 0/"
    assert not _numeric_time_dirs(dst), "staged tree must have no numeric time dir"
    assert os.path.isdir(os.path.join(dst, "0.orig")), "staged tree needs 0.orig/"
    print(f"staged {CASE}: {n} cells at h={H} m (frozen build_3d body run verbatim); "
          f"0.orig present, no 0/ and no numeric time dir -> age guard satisfiable.")
    return 0


# ---------------------------------------------------------------------------
def _sh(cmd, cwd=None):
    """Run one shell command with the OpenFOAM environment sourced BEFORE it --
    run_k2b.sh:11-15 measured that sourcing under `set -e` aborts silently, so we
    source, then run the command, in a fresh non-`-e` shell each call."""
    return subprocess.run(["bash", "-c", f". {OF_BASHRC} >/dev/null 2>&1; {cmd}"],
                          cwd=cwd)


def _grep_cells(path):
    try:
        for ln in open(path, errors="replace"):
            s = ln.strip()
            if s.startswith("nCells:"):
                return s.split()[1]
    except FileNotFoundError:
        pass
    return "NA"


def _count(path, pat):
    rx = re.compile(pat)
    try:
        return sum(1 for ln in open(path, errors="replace") if rx.search(ln))
    except FileNotFoundError:
        return 0


def run(args):
    # ---- cap: hardcoded ceiling, argv CANNOT widen it (rule 12) --------------
    cap = CAP_CEIL_CORE_MIN if args.cap_core_min is None else args.cap_core_min
    if cap > CAP_CEIL_CORE_MIN:
        sys.exit(f"REFUSE (exit 2): requested cap {cap:g} core-min exceeds the "
                 f"registered hard ceiling {CAP_CEIL_CORE_MIN} core-min "
                 f"(K2bU3R3_PREREGISTRATION.md §6). The cap is NOT argv-widenable.")
    if args.ranks != RANKS:
        sys.exit(f"REFUSE (exit 2): ranks={args.ranks} but this run is serial "
                 f"(ranks={RANKS}; prereg §6, no decomposeParDict).")
    case = os.path.join(HERE, args.case)
    if not os.path.isdir(case):
        sys.exit(f"REFUSE (exit 2): case dir {case} does not exist; stage it first "
                 f"(`python3 build_k2bU3R3.py stage`, freeze-time, by the supervisor).")
    # ---- age guard (rule 4 / prereg §5.2): refuse a pre-existing 0/ or time dir
    if os.path.isdir(os.path.join(case, "0")):
        sys.exit(f"REFUSE (exit 2): {case}/0 already exists -- the age guard refuses "
                 f"a case that already carries a 0/ (rule 4).")
    tds = _numeric_time_dirs(case)
    if tds:
        sys.exit(f"REFUSE (exit 2): numeric time dir(s) {tds} already present in "
                 f"{case} -- the age guard refuses an already-run case (rule 4).")
    if os.path.isfile(os.path.join(case, LOGNAME)) or \
       os.path.isfile(os.path.join(case, "COST.txt")):
        sys.exit(f"REFUSE (exit 2): a prior {LOGNAME}/COST.txt is present in {case}; "
                 f"refusing to overwrite an existing run's record.")
    if not os.path.isdir(os.path.join(case, "0.orig")):
        sys.exit(f"REFUSE (exit 2): {case} has no 0.orig/ to arm from; stage first.")
    # ---- arm 0/ from 0.orig AT LAUNCH (0/T touched last -> dates the run) -----
    shutil.rmtree(os.path.join(case, "constant", "polyMesh"), ignore_errors=True)
    shutil.copytree(os.path.join(case, "0.orig"), os.path.join(case, "0"))
    # ---- mesh (run_k2b.sh:58-60) ---------------------------------------------
    if _sh("blockMesh > log.blockMesh 2>&1", cwd=case).returncode != 0:
        sys.exit("BLOCKED: blockMesh failed; see log.blockMesh.")
    _sh("checkMesh > log.checkMesh 2>&1", cwd=case)
    if _sh("grep -q '^Mesh OK' log.checkMesh", cwd=case).returncode != 0:
        sys.exit("BLOCKED: checkMesh not OK; see log.checkMesh.")
    # ---- solve under the HARD cap (ranks=1 -> core-min == wall-min) ----------
    wall_cap_s = int(round(cap * 60 / RANKS))
    t0 = time.time()
    rc = _sh(f"timeout {wall_cap_s}s {SOLVER} > {LOGNAME} 2>&1", cwd=case).returncode
    wall = time.time() - t0
    core_min = wall * RANKS / 60.0
    # ---- COST.txt FIRST and unconditionally (run_k2b.sh:48-56 lesson) --------
    ncells = _grep_cells(os.path.join(case, "log.blockMesh"))
    niters = _count(os.path.join(case, LOGNAME), r'^Time = ')
    with open(os.path.join(case, "COST.txt"), "w") as fh:
        fh.write(f"case {args.case}\ncells {ncells}\niterations {niters}\n"
                 f"wall_clock_s {wall:.3f}\ncores {RANKS}\n"
                 f"core_minutes {core_min:.4f}\ncap_core_min {cap:g}\n")
    if rc == 124:
        sys.exit(f"BLOCKED (over-cap): {SOLVER} reached the {cap:g} core-min cap "
                 f"({wall_cap_s}s) without finishing; the run STOPS, no new budget "
                 f"(rule 12). Not a graded outcome.")
    if rc != 0:
        sys.exit(f"BLOCKED: {SOLVER} exited {rc}; see {LOGNAME}.")
    print(f"{args.case}: {ncells} cells, {niters} steps, {wall:.1f}s = "
          f"{core_min:.2f} core-min (cap {cap:g}). Grade with analyse_k2bU3R3.py.")
    return 0


# ---------------------------------------------------------------------------
def main(argv):
    ap = argparse.ArgumentParser(description="stage/launch K2b-U3-R3 (59 mm Test D)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("stage", help="stage the case dir via the frozen build_3d body")
    r = sub.add_parser("run", help="arm 0/, mesh, solve under the hard cap")
    r.add_argument("--case", default=CASE)
    r.add_argument("--cap-core-min", type=float, default=None)
    r.add_argument("--ranks", type=int, default=RANKS)
    r.add_argument("--no-detach", action="store_true",
                   help="run the solver in the foreground (queue default)")
    a = ap.parse_args(argv)
    return stage() if a.cmd == "stage" else run(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
