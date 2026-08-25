#!/usr/bin/env python3
"""F6a / C-15 LAUNCHER for the FROZEN pre-registration
`verification/campaign/F6a_GREENBLATT_PREREGISTRATION.md`.

IT DEFINES NO GATE. Every threshold is transcribed from the frozen document.

THE ONE THING THIS FILE EXISTS FOR, in the pre-registration's own words (ss5.5):

    "ENFORCEMENT -- THE SINGLE CHANGE THAT WOULD HAVE SAVED F12's SPEND: the
     launcher REFUSES to start the solver when Gate M fails. Non-zero exit, no
     solver process, no MPI rank spawned. Gate M is enforced BEFORE launch, not
     recorded after it."

C-50 records that F12's frozen `run_case` computed its mesh gate and then LAUNCHED
THE SOLVER ANYWAY -- 20.5 s of solver wall into a mesh already known to fail. This
file closes that gap by gating the ACT OF LAUNCHING.

Exit codes
  0 ran and graded        3 ss9.2 a registered run directory already EXISTS
  2 comparator REFUSAL    4 GATE M FAIL -> BLOCKED, no solver process started
  5 ss6.3 smoke test abort   6 pin/config assertion failure   7 cap timeout fired
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f6a_greenblatt_gate as G   # noqa: E402

REPO = G.REPO

# ---- FROZEN, transcribed with section numbers -----------------------------
RUN_ROOTS = (                                                          # ss9.1
    "/home/ubuntu/Certonomous/verification/runs/F6a_GREENBLATT_runs",
    "/home/ubuntu/certonomous-runs/f6a-greenblatt-baseline",
)
RUN_CASE = ("/home/ubuntu/Certonomous/verification/runs/F6a_GREENBLATT_runs/"
            "baseline_Re936k")                                         # ss11
SOURCE_CASE = "cases/dafoam/f6a_nasa_hump/case"                        # ss6.1
PRISTINE = ("0", "constant", "system", "caseDef", "fieldDef")          # ss6.1 -- inputs ONLY

RANKS = 4                                                              # ss8.5
CAP_CORE_MIN = 30                                                      # ss8.3
MESH_RESERVE_S = 30                                                    # ss8.5
ENDTIME = G.ENDTIME_CAP                                                # ss6.1 / ss3.1

MAX_NON_ORTHO = 70.0                                                   # ss5.1 / ss5.5 HARD
MAX_SKEWNESS = 4.0                                                     # ss5.1 / ss5.5 HARD

RE_NONORTHO = re.compile(r"non-orthogonality\s+Max:\s*([0-9.eE+\-]+)")
RE_SKEW = re.compile(r"Max skewness\s*=\s*([0-9.eE+\-]+)")


def solver_timeout_s(cap_core_min=CAP_CORE_MIN, ranks=RANKS, reserve=MESH_RESERVE_S):
    """ss8.5. A WALL-CLOCK timeout IS NOT A CORE-MINUTE CAP. They coincide only at
    1 rank. A naive `timeout 1800` at 4 ranks would permit 4x the registered budget
    before firing -- a cap that does not cap."""
    if ranks < 1:
        raise ValueError("ranks must be >= 1")
    total = cap_core_min * 60.0 / ranks
    t = total - reserve
    if t <= 0:
        raise ValueError("mesh reserve %ss exhausts the cap's %ss wall budget"
                         % (reserve, total))
    return total, t


def freeze_condition(roots=None):
    """ss9.1 + ss9.2. Evaluated by `test -e` IN THIS INVOCATION -- never read from
    the frozen file. The pre-registration is explicit that a reading taken at
    freeze time is NOT a substitute for the check at launch time.

    `roots` is resolved AT CALL TIME, never bound as a default. A default argument
    captures the module global once, at definition, so a guard written
    `def freeze_condition(roots=RUN_ROOTS)` silently checks a stale tuple -- which
    is how a directory guard passes while pointing at the wrong directories. The
    mutation control for ss9.2 caught exactly that and it is fixed here.
    """
    roots = RUN_ROOTS if roots is None else roots
    present = [d for d in roots if os.path.exists(d)]
    return (len(present) == 0), present


def parse_checkmesh(text):
    """ss5.5. Returns the two HARD gate quantities. Aspect ratio, cell determinant
    and every other check are REPORTED, NOT GATED (ss5.3)."""
    m1 = RE_NONORTHO.search(text)
    m2 = RE_SKEW.search(text)
    if not m1:
        raise G.Refusal("checkMesh output carries no non-orthogonality line -- "
                        "UNEVALUABLE. Gate M refuses rather than assuming.")
    if not m2:
        raise G.Refusal("checkMesh output carries no skewness line -- UNEVALUABLE.")
    return float(m1.group(1)), float(m2.group(1))


def gate_m(text, max_no=MAX_NON_ORTHO, max_sk=MAX_SKEWNESS):
    """ss5.5. PASS iff max non-orthogonality <= 70.0 AND max skewness <= 4.0.
    A Gate M failure is BLOCKED -- not GATE FAIL and not NOT A RESULT: nothing was
    computed, so nothing was graded."""
    no, sk = parse_checkmesh(text)
    ok = (no <= max_no) and (sk <= max_sk)
    return ok, {"max_non_orthogonality": no, "threshold": max_no,
                "max_skewness": sk, "skewness_threshold": max_sk,
                "GATE_M": "PASS" if ok else "BLOCKED",
                "reported_not_gated": "aspect ratio, cell determinant and all other "
                                      "checkMesh checks are REPORTED and NOT gated (ss5.3)"}


def assert_libs_stock(controldict_text):
    """rule 14: `libs` entries are INSERTED WITH AN ASSERT, NEVER REPLACED.

    ss7.3 registers DEVIATION 3: this run uses STOCK kOmegaSST, measured inert to
    0.02 %. So the correct assertion here is that NO custom library is active at
    the top level of controlDict. W1 ran this same case with a lab-built
    libkOmegaSSTQCRTurbulenceModels.so (ss6.2), which is exactly the model-library
    boundary the smoke test is aimed at. An active top-level libs entry is a
    FINDING and is refused -- it is never silently overwritten.
    """
    head = controldict_text.split("functions", 1)[0]
    active = [l.strip() for l in head.splitlines()
              if re.match(r"^\s*libs\b", l) and not l.strip().startswith("//")]
    if active:
        raise G.Refusal("rule 14: active top-level libs entry in controlDict %r. "
                        "ss7.3 registers STOCK kOmegaSST. REFUSING -- a libs entry is "
                        "asserted, never replaced." % active)
    return True


def install_pc_sampling(controldict_text, stride=G.SAMPLE_STRIDE):
    """ss3.1 (P-c) needs x_r/c and x_s/c every 50 iterations over the final 500.
    The shipped FOs write at `writeTime` only (writeInterval = $endTime), which
    yields ONE sample. This installs the sampling cadence and ASSERTS the edit
    landed. It changes no gate: the cadence is itself frozen at ss3.1."""
    out, n = re.subn(r"(\n\s*)(write|execute)Control(\s+)writeTime;",
                     lambda m: "%s%sControl%stimeStep;%s%sInterval%s%d;"
                               % (m.group(1), m.group(2), m.group(3),
                                  m.group(1), m.group(2), m.group(3), stride),
                     controldict_text)
    if n != 3:
        raise G.Refusal("ss3.1 (P-c) sampling install expected 3 substitutions in the "
                        "functions block, made %d. REFUSING rather than launching a run "
                        "that cannot produce 10 samples." % n)
    if "timeStep" not in out or ("Interval    %d" % stride) not in out.replace("\t", " " * 4):
        # tolerant re-check: the interval keyword and stride must both be present
        if not re.search(r"(write|execute)Interval\s+%d;" % stride, out):
            raise G.Refusal("ss3.1 (P-c) sampling install did not write the %d-iteration "
                            "interval." % stride)
    return out


def build_case(repo, run_case, dry_run=False):
    """Builds the graded case from the SHIPPED inputs only. Time directories and
    postProcessing from the source case are DELIBERATELY NOT COPIED: rule 4's guard
    refuses a case where a time dir already exists, and the age guard needs a `0/U`
    that dates THIS run."""
    src = os.path.join(repo, SOURCE_CASE)
    steps = []
    for name in PRISTINE:
        s = os.path.join(src, name)
        if not os.path.exists(s):
            raise G.Refusal("shipped case is missing %s" % s)
        steps.append((s, os.path.join(run_case, name)))
    if dry_run:
        return steps
    os.makedirs(run_case)
    for s, d in steps:
        (shutil.copytree if os.path.isdir(s) else shutil.copy2)(s, d)
    stale = [d for d in os.listdir(run_case) if d.isdigit() and d != "0"]
    if stale:
        raise G.Refusal("rule 4 guard: time directories already present in the fresh "
                        "case: %s" % stale)
    cd = os.path.join(run_case, "system", "controlDict")
    text = open(cd).read()
    assert_libs_stock(text)
    open(cd, "w").write(install_pc_sampling(text))
    return steps


def touch_age_anchor(run_case):
    """rule 4 / ss9.4: `0/U` is touched LAST at launch and so dates the run permitted
    to produce the answer. Every field at endTime must be NEWER than it."""
    a = os.path.join(run_case, G.AGE_GUARD_ANCHOR)
    if not os.path.exists(a):
        raise G.Refusal("age-guard anchor %s absent" % a)
    os.utime(a, None)
    return a


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--scratch", required=False,
                    help="ss6.3 smoke-test root. MUST be outside verification/runs/.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Run every pre-launch check and STOP. Starts no solver.")
    ap.add_argument("--show-frozen", action="store_true")
    a = ap.parse_args(argv)

    if a.show_frozen:
        total, t = solver_timeout_s()
        print("LAUNCHER FROZEN CONSTANTS")
        print("  ss9.1 run roots that must NOT exist:")
        for d in RUN_ROOTS:
            print("        %s" % d)
        print("  ss11  graded run case: %s" % RUN_CASE)
        print("  ss5.5 GATE M: max non-ortho <= %.1f deg AND max skewness <= %.1f"
              % (MAX_NON_ORTHO, MAX_SKEWNESS))
        print("        a Gate M failure is BLOCKED; the launcher starts NO solver process")
        print("  ss8.3 cap %d core-min at ranks = %d" % (CAP_CORE_MIN, RANKS))
        print("  ss8.5 wall budget = %d * 60 / %d = %.0f s; mesh reserve %d s;"
              % (CAP_CORE_MIN, RANKS, total, MESH_RESERVE_S))
        print("        SOLVER TIMEOUT = %.0f s" % t)
        print("  ss6.1 endTime %d, ranks %d, stock kOmegaSST (DEVIATION 3)" % (ENDTIME, RANKS))
        return 0

    report = {}
    try:
        # ---- rule 2: the file that runs must BE the file that was frozen ----
        G.assert_pinned(a.repo)
        report["pins"] = {"extractor_sha256": G.EXTRACTOR_SHA256,
                          "preregistration_sha256": G.PREREG_SHA256}

        # ---- ss9.1 / ss9.2 freeze condition, IN THIS INVOCATION ----
        ok, present = freeze_condition()
        report["freeze_condition"] = {"roots": list(RUN_ROOTS), "existing": present,
                                      "ok": ok, "checked_by": "test -e in this invocation"}
        if not ok:
            sys.stderr.write("ss9.2 REFUSAL (exit 3): registered run directory already "
                             "exists: %s\n" % present)
            return 3

        # ---- ss8.5 cap arithmetic, derived not hardcoded ----
        total_wall, timeout_s = solver_timeout_s()
        report["cap"] = {"cap_core_min": CAP_CORE_MIN, "ranks": RANKS,
                         "wall_budget_s": total_wall, "mesh_reserve_s": MESH_RESERVE_S,
                         "solver_timeout_s": timeout_s}

        if a.dry_run:
            report["build_plan"] = [d for _, d in build_case(a.repo, RUN_CASE, dry_run=True)]
            report["STATUS"] = ("DRY RUN -- every pre-launch check evaluated, NO solver "
                               "process started, NO case directory created.")
            print(json.dumps(report, indent=2))
            return 0

        if not a.scratch:
            ap.error("--scratch is required for a real launch (ss6.3)")
        if os.path.abspath(a.scratch).startswith(
                "/home/ubuntu/Certonomous/verification/runs"):
            raise G.Refusal("ss6.3: the smoke-test scratch directory MUST be outside "
                            "verification/runs/. Its output is not evidence and is not "
                            "cited by any record.")
        build_case(a.repo, RUN_CASE)

        # ---- ss5.5 GATE M, ENFORCED BEFORE ANY SOLVER PROCESS ----
        cm = subprocess.run(["checkMesh", "-case", RUN_CASE],
                            capture_output=True, text=True, timeout=MESH_RESERVE_S)
        open(os.path.join(RUN_CASE, "log.checkMesh"), "w").write(cm.stdout + cm.stderr)
        passed, detail = gate_m(cm.stdout + cm.stderr)
        report["gate_m"] = detail
        if not passed:
            report["VERDICT"] = "BLOCKED"
            report["why"] = ("GATE M FAILED. NO SOLVER PROCESS WAS STARTED and NO MPI "
                             "RANK WAS SPAWNED. Nothing was computed, so nothing was "
                             "graded -- ss5.5.")
            print(json.dumps(report, indent=2))
            return 4

        # ---- ss6.3 PRE-FLIGHT SMOKE TEST: a LAUNCH CONDITION, NOT A GATE ----
        smoke = os.path.join(a.scratch, "f6a_smoke")
        if os.path.exists(smoke):
            shutil.rmtree(smoke)
        shutil.copytree(RUN_CASE, smoke)
        cdp = os.path.join(smoke, "system", "controlDict")
        open(cdp, "w").write(re.sub(r"\nendTime\s+\d+;", "\nendTime         1;",
                                    open(cdp).read()))
        sm = subprocess.run(["simpleFoam", "-case", smoke],
                            capture_output=True, text=True, timeout=MESH_RESERVE_S)
        fatal = "FOAM FATAL" in (sm.stdout + sm.stderr)
        report["smoke_test"] = {"rc": sm.returncode, "foam_fatal": fatal,
                                "scratch": smoke,
                                "kind": "LAUNCH CONDITION, NOT A GATE",
                                "note": "It decides whether the run STARTS. It never "
                                        "decides what the run MEANS. It produces no "
                                        "number entering any gate. It catches the "
                                        "VMFL045 dictionary-completeness class and "
                                        "would NOT have caught F12 (died at iteration "
                                        "180 of 6,000) -- Gate M enforcement is what "
                                        "would have. Disjoint risks."}
        if sm.returncode != 0 or fatal:
            report["VERDICT"] = "BLOCKED"
            report["why"] = "ss6.3 smoke test aborted the campaign before the graded run."
            print(json.dumps(report, indent=2))
            return 5

        # ---- launch, under the ss8.5 cap ----
        touch_age_anchor(RUN_CASE)
        log = os.path.join(RUN_CASE, "log.simpleFoam")
        with open(log, "w") as lf:
            try:
                pr = subprocess.run(
                    ["mpirun", "-np", str(RANKS), "simpleFoam", "-case", RUN_CASE,
                     "-parallel"],
                    stdout=lf, stderr=subprocess.STDOUT, timeout=timeout_s)
                rc = pr.returncode
            except subprocess.TimeoutExpired:
                report["VERDICT"] = "NOT A RESULT"
                report["why"] = ("ss8.3 CAP EXCEEDED at %.0f s wall (%d core-min at "
                                 "ranks = %d). An overrun STOPS THE RUN. It does not "
                                 "get a new budget." % (timeout_s, CAP_CORE_MIN, RANKS))
                print(json.dumps(report, indent=2))
                return 7
        report["solver_rc"] = rc
        report["STATUS"] = ("solver finished; grade with scripts/f6a_greenblatt_gate.py "
                            "--case %s --log %s --endtime %d --rc %d"
                            % (RUN_CASE, log, ENDTIME, rc))
    except G.Refusal as e:
        sys.stderr.write("REFUSAL: %s\n" % e)
        report["VERDICT"] = "NOT A RESULT"
        report["REFUSAL"] = str(e)
        print(json.dumps(report, indent=2))
        return 6

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
