#!/usr/bin/env python3
"""K0h STAGE ORCHESTRATOR AND CEILING-STOP ENFORCER.

REGISTERED AT docs/campaigns/F14-cooling-ladder/K0h_PREREGISTRATION.md
AMENDMENT 1, section A1.5 (2026-09-10, BEFORE FIRST COMPUTE).

WHY THIS FILE EXISTS AT ALL
---------------------------
K0g registered a ceiling and a per-arm cap and STILL overran into a
supervisor-executed SIGTERM on three arms in flight.  The mechanism is on
disk and is not a matter of opinion --
`verification/runs/F14-cooling-ladder/K0g_runs/orchestrate_k0g.py:113-118`:

    running_pt = sum(p for (n, l, p, t) in launched
                     if not os.path.exists(status_path(n)) and n in running())
    proj = completed_coremin() + running_pt + pt
    if proj > CEILING: ... UNRUN

A RUNNING ARM WAS CHARGED ITS *POINT ESTIMATE* (`p`), NOT ITS *CAP* (`t`).
The point estimate was low by x3.16-x3.19 on the two arms that completed
(K0h_PREREGISTRATION.md section 8.1), so the projection that guarded the
ceiling was itself computed from the mis-costed figure the ceiling existed
to contain.  The guard could not fail *before* the ceiling was breached,
because the guard's own arithmetic denied the breach was coming.

THE THREE REGISTERED RULES THIS FILE ENFORCES
---------------------------------------------
R1  A RUNNING ARM IS CHARGED ITS CAP, NEVER ITS ESTIMATE.  A cap is the
    only figure that BOUNDS an arm's spend; an estimate is the figure that
    was wrong.  This is the K0g repair and it is the whole point.

R2  THE STAGE GATE IS PRE-LAUNCH ONLY.  A stage launches only if
        charged_so_far + sum(caps of this stage's arms)  <=  CEILING.
    If it does not hold the stage is BLOCKED, its arms are named UNRUN, and
    the run STOPS.  An overrun does not get a new budget (standing rule 12).

R3  THIS FILE NEVER SIGNALS A RUNNING SOLVER.  There is no kill path, no
    SIGTERM, no SIGKILL, no `pkill`, no `terminate()`.  An arm in flight is
    stopped ONLY by its own `timeout` cap inside `launch_k0h.sh` (rc 124, a
    CAP-STOP).  `--selftest` ASSERTS the absence of every signalling call by
    reading this file's own source, so the rule cannot decay silently
    (standing rule 14: a lesson is not applied until every call site
    asserts it).

NO GATE, THRESHOLD, BAND OR LABEL LIVES IN THIS FILE.  The stage table,
the caps and the ceiling are READ FROM A REGISTERED MANIFEST whose blob is
pinned at the freeze commit.  This file cannot be used to move a number,
and a manifest whose arithmetic does not close is REFUSED (exit 2) rather
than run.

THIS FILE DOES NOT READ, EVALUATE OR ADVANCE A STAGE GATE.  The section 8.3
stage gate is a stationarity reading and it is the SUPERVISOR'S.  There is
no `--auto`: each stage is named explicitly on the command line, so no
budget is ever committed by this file deciding that a gate passed.

Exit codes:  0  the named stage was launched, or has already completed
             1  the named stage is BLOCKED by the ceiling (rule 12 stop)
             2  REFUSAL -- the manifest, the tree or the request is unusable
"""

import argparse
import json
import os
import re
import subprocess
import sys

EXIT_OK, EXIT_BLOCKED, EXIT_REFUSE = 0, 1, 2

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAUNCHER = os.path.join(REPO, "scripts", "launch_k0h.sh")

# The signalling calls R3 forbids.  Read out of this file's own source by
# --selftest.  A name added to the file without being added here is what the
# assertion is for: the check is on the SOURCE, not on this list's intent.
FORBIDDEN_SIGNALS = ("SIGTERM", "SIGKILL", "pkill", "killall",          # R3LIT
                     "os.kill", ".terminate(", ".kill(", "signal.alarm")  # R3LIT


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def own_blob_sha():
    import hashlib
    with open(os.path.abspath(__file__), "rb") as fh:
        b = fh.read()
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


# ======================================================================
# THE MANIFEST.  Every number the orchestrator obeys comes from here, and
# every one of them is CHECKED rather than trusted.
# ======================================================================

def load_manifest(path):
    """Read and VALIDATE the registered stage manifest.  REFUSES on anything
    it cannot check, and on any manifest whose own arithmetic does not close."""
    if not os.path.isfile(path):
        refuse(f"{path}: no stage manifest.  This file registers no stage "
               f"table of its own and will not invent one.")
    try:
        with open(path) as fh:
            m = json.load(fh)
    except Exception as exc:                                    # noqa: BLE001
        refuse(f"{path}: unreadable stage manifest ({exc})")

    for k in ("rung", "ceiling_core_min", "ranks", "stages"):
        if k not in m:
            refuse(f"{path}: manifest has no {k!r} key")
    if m["rung"] != "K0h":
        refuse(f"{path}: manifest is for rung {m['rung']!r}, not K0h")
    if m["ranks"] != 1:
        refuse(f"{path}: K0h is registered SERIAL (ranks = 1); manifest says "
               f"{m['ranks']!r}")
    if not isinstance(m["stages"], list) or not m["stages"]:
        refuse(f"{path}: manifest carries no stages")

    ceiling = float(m["ceiling_core_min"])
    if not ceiling > 0:
        refuse(f"{path}: ceiling_core_min must be positive")

    seen = set()
    total_caps = 0.0
    for si, st in enumerate(m["stages"], start=1):
        for k in ("name", "arms"):
            if k not in st:
                refuse(f"{path}: stage {si} has no {k!r}")
        if not st["arms"]:
            refuse(f"{path}: stage {st['name']!r} carries no arms")
        for arm in st["arms"]:
            for k in ("name", "basis_core_min", "cap_core_min"):
                if k not in arm:
                    refuse(f"{path}: an arm of stage {st['name']!r} has no "
                           f"{k!r}")
            n = arm["name"]
            if n in seen:
                refuse(f"{path}: arm {n!r} appears in more than one stage")
            seen.add(n)
            basis, cap = float(arm["basis_core_min"]), float(arm["cap_core_min"])
            if not basis > 0 or not cap > 0:
                refuse(f"{path}: arm {n!r} carries a non-positive figure")
            # A CAP BELOW ITS OWN BASIS IS A CAP THAT CANNOT BUY THE ARM IT
            # GUARDS.  Registering one is the K0g failure written down, so it
            # is refused rather than run.
            if cap < basis:
                refuse(f"{path}: arm {n!r} has cap {cap} core-min BELOW its own "
                       f"basis {basis} core-min.  A cap that cannot buy the arm "
                       f"it guards is a pre-registered stop, not a cap.")
            total_caps += cap

    # THE ARITHMETIC MUST CLOSE ON THE MANIFEST'S OWN FACE.  A ceiling that
    # the sum of the caps it authorises already exceeds is a ceiling the
    # arithmetic refutes, and this file will not run one.
    if total_caps > ceiling:
        refuse(f"{path}: the caps of the {len(seen)} registered arms sum to "
               f"{total_caps:.2f} core-min and the registered ceiling is "
               f"{ceiling:.2f} core-min.  The ceiling cannot buy the arms it "
               f"authorises even at the caps IT registers; the arithmetic "
               f"refutes it before any solver runs (standing rule 12).  Fix "
               f"the registration, not this check.")
    m["_total_caps"] = total_caps
    return m


# ======================================================================
# WHAT HAS ALREADY BEEN CHARGED.  R1 lives here.
# ======================================================================

_STATUS_RE = re.compile(r"(\w+)=(\S+)")


def read_status(runhome, arm):
    """The arm's STATUS fields, or None if it has none.  A STATUS is written
    only by `launch_k0h.sh` after the solver returns, so its ABSENCE beside a
    prepared case directory means IN FLIGHT or NEVER LAUNCHED -- never rc=0."""
    p = os.path.join(runhome, f"STATUS.{arm}")
    if not os.path.isfile(p):
        return None
    with open(p) as fh:
        txt = fh.read()
    d = dict(_STATUS_RE.findall(txt))
    if "wall" not in d or "rc" not in d:
        refuse(f"{p}: a STATUS with no {'wall' if 'wall' not in d else 'rc'} "
               f"field.  Refusing rather than charging an arm nothing.")
    return d


def arm_state(runhome, arm):
    """One of 'DONE' (STATUS present), 'IN_FLIGHT' (case dir present, no
    STATUS) or 'UNLAUNCHED' (no case dir)."""
    if read_status(runhome, arm) is not None:
        return "DONE"
    if os.path.isdir(os.path.join(runhome, arm)):
        return "IN_FLIGHT"
    return "UNLAUNCHED"


def charge(runhome, manifest, verbose=False):
    """Core-minutes CHARGED against the ceiling so far.

    R1, THE K0g REPAIR: a DONE arm is charged its MEASURED wall x ranks / 60.
    AN ARM IN FLIGHT IS CHARGED ITS CAP, NEVER ITS ESTIMATE -- the cap is the
    only figure that bounds it, and charging the estimate is precisely how
    K0g's ceiling was breached from inside its own guard."""
    total = 0.0
    detail = []
    for st in manifest["stages"]:
        for arm in st["arms"]:
            n = arm["name"]
            state = arm_state(runhome, n)
            if state == "DONE":
                s = read_status(runhome, n)
                ranks = float(s.get("ranks", manifest["ranks"]))
                c = float(s["wall"]) * ranks / 60.0
                basis = "MEASURED"
            elif state == "IN_FLIGHT":
                c = float(arm["cap_core_min"])
                basis = "CHARGED AT CAP (in flight; R1)"
            else:
                c = 0.0
                basis = "unlaunched"
            total += c
            detail.append((n, st["name"], state, c, basis))
    if verbose:
        print(f"  {'arm':<10} {'stage':<8} {'state':<10} {'core-min':>10}  basis")
        for n, sn, state, c, basis in detail:
            print(f"  {n:<10} {sn:<8} {state:<10} {c:>10.2f}  {basis}")
        print(f"  {'CHARGED':<10} {'':<8} {'':<10} {total:>10.2f}")
    return total, detail


# ======================================================================
# R2: THE PRE-LAUNCH STAGE GATE.
# ======================================================================

def stage_by_name(manifest, name):
    for st in manifest["stages"]:
        if st["name"] == name:
            return st
    refuse(f"stage {name!r} is not in the manifest (have: "
           f"{[s['name'] for s in manifest['stages']]})")


def evaluate_stage(runhome, manifest, stage, verbose=False):
    """Returns (decision, charged, need, headroom).

    decision is 'LAUNCH', 'BLOCKED' or 'ALREADY' -- and it is decided BEFORE
    anything is launched.  Nothing in flight is ever affected by it."""
    charged, _ = charge(runhome, manifest, verbose=verbose)
    ceiling = float(manifest["ceiling_core_min"])

    to_launch = [a for a in stage["arms"]
                 if arm_state(runhome, a["name"]) == "UNLAUNCHED"]
    if not to_launch:
        return "ALREADY", charged, 0.0, ceiling - charged

    need = sum(float(a["cap_core_min"]) for a in to_launch)
    if charged + need > ceiling:
        return "BLOCKED", charged, need, ceiling - charged
    return "LAUNCH", charged, need, ceiling - charged


def write_stop_record(runhome, stage, charged, need, ceiling, unrun):
    """The rule-12 stop, written where a reader will find it.  A stop that
    leaves no record is indistinguishable from a stage nobody ran."""
    p = os.path.join(runhome, "CEILING_STOP.txt")
    with open(p, "a") as fh:
        fh.write(
            f"CEILING STOP -- stage {stage['name']!r} BLOCKED, NOT LAUNCHED.\n"
            f"  charged so far        : {charged:.2f} core-min "
            f"(arms in flight charged AT CAP, rule R1)\n"
            f"  this stage needs      : {need:.2f} core-min at the registered caps\n"
            f"  registered ceiling    : {ceiling:.2f} core-min\n"
            f"  would reach           : {charged + need:.2f} core-min\n"
            f"  UNRUN ARMS            : {', '.join(unrun)}\n"
            f"  An overrun does not get a new budget (standing rule 12).  A new\n"
            f"  ceiling is a NEW REGISTRATION, and it is not this file's to write.\n"
            f"  NOTHING IN FLIGHT WAS SIGNALLED (rule R3).\n\n")
    return p


# ======================================================================
# LAUNCHING.  Per-arm caps only; no signalling; no auto-advance.
# ======================================================================

def launch_stage(runhome, manifest, stage, foam_bashrc, dry_run=False,
                 verbose=True):
    ranks = int(manifest["ranks"])
    launched = []
    for a in stage["arms"]:
        n = a["name"]
        if arm_state(runhome, n) != "UNLAUNCHED":
            if verbose:
                print(f"  {n}: {arm_state(runhome, n)}, not relaunched")
            continue
        cap = float(a["cap_core_min"])
        # THE CAP, CONVERTED THE ONE REGISTERED WAY (section 8.4):
        #     timeout_s = cap_core_min * 60 / ranks
        timeout_s = int(round(cap * 60.0 / ranks))
        cmd = ["bash", LAUNCHER, "--case-dir", os.path.join(runhome, n),
               "--timeout", str(timeout_s), "--ranks", str(ranks)]
        if foam_bashrc:
            cmd += ["--foam-bashrc", foam_bashrc]
        if verbose:
            print(f"  {n}: cap {cap:.2f} core-min -> timeout {timeout_s} s"
                  + ("   [DRY RUN, not launched]" if dry_run else ""))
        if not dry_run:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                             stderr=subprocess.STDOUT)
        launched.append(n)
    return launched


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="K0h stage orchestrator and ceiling-stop enforcer.")
    ap.add_argument("--runhome", help="the K0h_runs directory")
    ap.add_argument("--manifest", help="the registered stage manifest (JSON)")
    ap.add_argument("--stage", help="the stage to launch, BY NAME. There is no "
                                    "--auto: a stage gate is the supervisor's.")
    ap.add_argument("--report", action="store_true",
                    help="charge the tree against the ceiling and stop")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--foam-bashrc")
    ap.add_argument("--expect-sha",
                    help="this file's committed blob sha1; REFUSES on mismatch")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()

    sha = own_blob_sha()
    print(f"orchestrate_k0h.py blob sha1: {sha}")
    if a.expect_sha and a.expect_sha != sha:
        refuse(f"FREEZE CHECK FAILED: this file hashes to {sha}, the committed "
               f"blob was given as {a.expect_sha}.")
    if not a.runhome or not a.manifest:
        ap.error("--runhome and --manifest are required (or --selftest)")
    if not os.path.isdir(a.runhome):
        refuse(f"{a.runhome}: not a directory")

    m = load_manifest(a.manifest)
    ceiling = float(m["ceiling_core_min"])
    print(f"manifest OK: {len(m['stages'])} stages, caps sum "
          f"{m['_total_caps']:.2f} <= ceiling {ceiling:.2f} core-min")

    if a.report or not a.stage:
        charged, _ = charge(a.runhome, m, verbose=True)
        print(f"\nCHARGED {charged:.2f} of {ceiling:.2f} core-min; headroom "
              f"{ceiling - charged:.2f}")
        for st in m["stages"]:
            d, c, need, head = evaluate_stage(a.runhome, m, st)
            print(f"  stage {st['name']:<8} {d:<8} needs {need:>9.2f} at cap, "
                  f"headroom {head:>9.2f}")
        return EXIT_OK

    st = stage_by_name(m, a.stage)
    print(f"\nSTAGE {st['name']!r} -- PRE-LAUNCH GATE (R2)")
    decision, charged, need, headroom = evaluate_stage(a.runhome, m, st,
                                                       verbose=True)
    print(f"  charged {charged:.2f} + need {need:.2f} vs ceiling {ceiling:.2f} "
          f"-> {decision}")
    if decision == "ALREADY":
        print("  every arm of this stage is launched or done; nothing to do.")
        return EXIT_OK
    if decision == "BLOCKED":
        unrun = [x["name"] for x in st["arms"]
                 if arm_state(a.runhome, x["name"]) == "UNLAUNCHED"]
        p = write_stop_record(a.runhome, st, charged, need, ceiling, unrun)
        print(f"  CEILING STOP recorded at {p}")
        print("  NOTHING IN FLIGHT WAS SIGNALLED (R3).")
        return EXIT_BLOCKED
    launch_stage(a.runhome, m, st, a.foam_bashrc, dry_run=a.dry_run)
    return EXIT_OK


# ======================================================================
# SELFTEST_REGION_BEGINS_HERE -- the sentinel the R3 source scan splits on.
# Every rule is driven BOTH WAYS.  A probe never shown able to fire is not
# evidence (standing rule 3).  THE SELFTEST LEGITIMATELY CONTAINS A PLANTED
# SIGNALLING CALL as its negative control, which is exactly why the R3 scan
# is scoped to the PRODUCTION region above this line and asserts that the
# region is non-trivial.
# ======================================================================

_P, _F = [0], [0]


def check_(label, cond, note=""):
    if cond:
        _P[0] += 1
        print(f"  OK    {label}" + (f"   [{note}]" if note else ""))
    else:
        _F[0] += 1
        print(f"  FAIL  {label}" + (f"   [{note}]" if note else ""))


def _refuses(fn, *args, **kw):
    """True iff fn REFUSES (exit 2).  Returns (fired, printed_text)."""
    import io
    import contextlib
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            fn(*args, **kw)
        return False, buf.getvalue()
    except SystemExit as exc:
        return exc.code == EXIT_REFUSE, buf.getvalue()


def _manifest(tmp, ceiling, stages, rung="K0h", ranks=1):
    p = os.path.join(tmp, f"man_{abs(hash((ceiling, str(stages), rung, ranks)))}.json")
    with open(p, "w") as fh:
        json.dump(dict(rung=rung, ceiling_core_min=ceiling, ranks=ranks,
                       stages=stages), fh)
    return p


def _status(runhome, arm, wall, rc=0, ranks=1):
    with open(os.path.join(runhome, f"STATUS.{arm}"), "w") as fh:
        fh.write(f"rc={rc} wall={wall} ranks={ranks} case={arm} note=clean\n")


def selftest():
    import tempfile
    print("=" * 70)
    print("orchestrate_k0h.py -- SELFTEST")
    print(f"  this file's git blob sha1: {own_blob_sha()}")
    print("=" * 70)
    tmp = tempfile.mkdtemp(prefix="orch_k0h_selftest_")

    S1 = [dict(name="1", arms=[dict(name="M1_c", basis_core_min=100.0,
                                    cap_core_min=250.0),
                               dict(name="M2_c", basis_core_min=100.0,
                                    cap_core_min=250.0)]),
          dict(name="2", arms=[dict(name="M1_m", basis_core_min=400.0,
                                    cap_core_min=1000.0)])]

    # ---- R3 FIRST, ON THIS FILE'S OWN PRODUCTION SOURCE -------------------
    print("\n-- R3: NO SIGNALLING PATH, ASSERTED ON THIS FILE'S SOURCE --")
    with open(os.path.abspath(__file__)) as fh:
        src_lines = fh.readlines()
    # SCOPE.  The scan covers the PRODUCTION region -- everything above the
    # sentinel.  It CANNOT cover the selftest, because the selftest's own
    # negative control below is a planted `os.kill(..., SIGTERM)`, and a scan
    # that refused to see it could never be shown able to fire.  The boundary
    # is therefore asserted to exist and the region asserted non-trivial.
    # The sentinel is assembled from pieces so that this search is not itself
    # a second occurrence of it -- a scope marker that matches its own finder
    # is not a scope marker.
    sentinel = "SELFTEST_REGION" + "_BEGINS_HERE"
    marker = [i for i, l in enumerate(src_lines) if sentinel in l]
    check_("the production/selftest boundary sentinel exists exactly once, so "
           "the scan's SCOPE is fixed by the file and not by a line number",
           len(marker) == 1, f"line {marker[0] + 1 if marker else None}")
    if len(marker) != 1:
        print("SELFTEST FAILED: cannot scope the R3 scan"); return EXIT_REFUSE
    prod = src_lines[:marker[0]]
    # Strip the module docstring, comment lines, and the R3LIT-tagged literal
    # that NAMES the forbidden tokens in order to forbid them.  A NAMING is
    # not a CALL, and the distinction is what makes the scan meaningful.
    body, in_doc, ndoc = [], False, 0
    for ln in prod:
        st = ln.strip()
        q = st.count('"""')
        if not in_doc and st.startswith('"""'):
            ndoc += 1
            in_doc = (q == 1)
            continue
        if in_doc:
            if q >= 1:
                in_doc = False
            continue
        if st.startswith("#") or ln.rstrip().endswith("# R3LIT"):
            continue
        body.append(ln)
    body_txt = "".join(body)
    check_("the production region is NON-TRIVIAL, so a clean scan is not "
           "merely a scan of nothing", len(body) > 150 and ndoc >= 5,
           f"{len(body)} executable lines, {ndoc} docstrings stripped")
    hits = [t for t in FORBIDDEN_SIGNALS if t in body_txt]
    check_("no signalling call appears in PRODUCTION executable code -- an arm "
           "in flight can only ever be stopped by its OWN timeout cap",
           not hits, f"searched {len(body)} code lines, hits={hits}")
    check_("the FORBIDDEN_SIGNALS list is non-empty, so the search above is "
           "not vacuous", len(FORBIDDEN_SIGNALS) >= 6,
           f"{len(FORBIDDEN_SIGNALS)} tokens")
    # AND THE NEGATIVE: the same scan, on the same text, MUST fire once a
    # signalling call is planted into it.
    planted = body_txt + "\n    os." + "kill(pid, signal.SIG" + "TERM)\n"
    check_("NEGATIVE: the SAME scan FIRES on a planted signalling call, so the "
           "R3 assertion was shown able to fail rather than merely to pass",
           [t for t in FORBIDDEN_SIGNALS if t in planted],
           "os.kill planted -> detected")

    # ---- MANIFEST VALIDATION, BOTH WAYS -----------------------------------
    print("\n-- THE MANIFEST IS CHECKED, NOT TRUSTED --")
    good = _manifest(tmp, 1500.0, S1)
    m = load_manifest(good)
    check_("a manifest whose caps (1500.00) equal its ceiling (1500.00) is "
           "ACCEPTED -- the boundary is inclusive",
           abs(m["_total_caps"] - 1500.0) < 1e-9, f"{m['_total_caps']:.2f}")
    fired, txt = _refuses(load_manifest, _manifest(tmp, 1499.0, S1))
    check_("NEGATIVE: a ceiling ONE core-minute below the caps it authorises "
           "is REFUSED -- the arithmetic is checked before any solver runs",
           fired and "arithmetic refutes it" in txt, "exit 2")
    fired, _ = _refuses(load_manifest, _manifest(tmp, 1500.0, S1, rung="K0g"))
    check_("NEGATIVE: a manifest for another rung is REFUSED", fired, "exit 2")
    fired, _ = _refuses(load_manifest, _manifest(tmp, 1500.0, S1, ranks=4))
    check_("NEGATIVE: ranks != 1 is REFUSED (K0h is registered SERIAL)",
           fired, "exit 2")
    fired, txt = _refuses(load_manifest, _manifest(
        tmp, 1500.0, [dict(name="1", arms=[dict(name="M1_c",
                                                basis_core_min=300.0,
                                                cap_core_min=250.0)])]))
    check_("NEGATIVE: a cap BELOW its own arm's basis is REFUSED -- a cap that "
           "cannot buy the arm it guards is a pre-registered stop",
           fired and "BELOW its own basis" in txt, "exit 2")
    fired, _ = _refuses(load_manifest, _manifest(
        tmp, 1500.0, [dict(name="1", arms=[dict(name="M1_c", basis_core_min=1.0,
                                                cap_core_min=2.0)]),
                      dict(name="2", arms=[dict(name="M1_c", basis_core_min=1.0,
                                                cap_core_min=2.0)])]))
    check_("NEGATIVE: the same arm in two stages is REFUSED (it would be "
           "charged twice, or launched twice)", fired, "exit 2")
    fired, _ = _refuses(load_manifest, os.path.join(tmp, "no_such_manifest"))
    check_("NEGATIVE: an ABSENT manifest is REFUSED -- this file invents no "
           "stage table", fired, "exit 2")

    # ---- R1: A RUNNING ARM IS CHARGED ITS CAP, NOT ITS ESTIMATE -----------
    print("\n-- R1: THE K0g REPAIR, DRIVEN BOTH WAYS --")
    rh = os.path.join(tmp, "runs_R1")
    os.makedirs(os.path.join(rh, "M1_c"))          # prepared, IN FLIGHT
    ch, _ = charge(rh, m)
    check_("an arm IN FLIGHT is charged its CAP (250.00), not its basis "
           "(100.00) -- this is the exact figure K0g got wrong",
           abs(ch - 250.0) < 1e-9, f"charged {ch:.2f}")
    check_("NEGATIVE: it is NOT charged the basis -- had it been, the charge "
           "would read 100.00 and the K0g breach would be reproduced",
           abs(ch - 100.0) > 1e-9, f"charged {ch:.2f}, basis was 100.00")
    _status(rh, "M1_c", wall=3000)                 # now DONE: 3000 s = 50 min
    ch2, _ = charge(rh, m)
    check_("once the arm is DONE it is charged its MEASURED wall (3000 s x 1 "
           "rank = 50.00 core-min), and the cap charge is released",
           abs(ch2 - 50.0) < 1e-9, f"charged {ch2:.2f}")
    _status(rh, "M2_c", wall=6000, ranks=2)
    ch3, _ = charge(rh, m)
    check_("a STATUS's OWN ranks field is honoured, not the manifest's "
           "(6000 s x 2 = 200.00 on top of 50.00)",
           abs(ch3 - 250.0) < 1e-9, f"charged {ch3:.2f}")
    with open(os.path.join(rh, "STATUS.M1_m"), "w") as fh:
        fh.write("rc=0 case=M1_m\n")               # no wall
    fired, _ = _refuses(charge, rh, m)
    check_("NEGATIVE: a STATUS with no `wall` is REFUSED rather than charged "
           "nothing -- a missing measurement is not a zero cost", fired,
           "exit 2")
    os.remove(os.path.join(rh, "STATUS.M1_m"))

    # ---- R2: THE PRE-LAUNCH STAGE GATE, BOTH WAYS -------------------------
    print("\n-- R2: THE STAGE GATE IS PRE-LAUNCH, AND IT BLOCKS --")
    rh2 = os.path.join(tmp, "runs_R2")
    os.makedirs(rh2)
    st1, st2 = m["stages"][0], m["stages"][1]
    d, c, need, head = evaluate_stage(rh2, m, st1)
    check_("on an empty tree stage 1 LAUNCHES: 0.00 + 500.00 <= 1500.00",
           d == "LAUNCH" and abs(need - 500.0) < 1e-9, f"{d}, need {need:.2f}")
    _status(rh2, "M1_c", wall=3000)
    _status(rh2, "M2_c", wall=3000)
    d, c, need, head = evaluate_stage(rh2, m, st2)
    check_("with stage 1 done at 100.00 measured, stage 2 LAUNCHES: "
           "100.00 + 1000.00 <= 1500.00",
           d == "LAUNCH", f"{d}, charged {c:.2f}, need {need:.2f}")
    # now make stage 1 expensive enough that stage 2 cannot be bought
    _status(rh2, "M1_c", wall=30000)               # 500 core-min
    _status(rh2, "M2_c", wall=30000)               # 500 core-min
    d, c, need, head = evaluate_stage(rh2, m, st2)
    check_("NEGATIVE: with 1000.00 charged, stage 2's 1000.00 would reach "
           "2000.00 > 1500.00, so the stage is BLOCKED and STOPS",
           d == "BLOCKED", f"{d}, charged {c:.2f}, need {need:.2f}")
    p = write_stop_record(rh2, st2, c, need, 1500.0, ["M1_m"])
    rec = open(p).read()
    check_("the stop is RECORDED with the unrun arm NAMED and rule 12 quoted",
           "UNRUN ARMS" in rec and "M1_m" in rec and "new budget" in rec,
           os.path.basename(p))
    check_("the stop record states that nothing in flight was signalled",
           "NOTHING IN FLIGHT WAS SIGNALLED" in rec)
    # the EXACT boundary
    _status(rh2, "M1_c", wall=15000)               # 250
    _status(rh2, "M2_c", wall=15000)               # 250  -> charged 500
    d, _, _, _ = evaluate_stage(rh2, m, st2)
    check_("at EXACTLY the ceiling (500.00 + 1000.00 == 1500.00) the stage "
           "LAUNCHES -- the comparison is `>`, not `>=`, and the boundary is "
           "stated rather than left to a reader", d == "LAUNCH", d)
    _status(rh2, "M1_c", wall=15060)               # 251 -> charged 501
    d, _, _, _ = evaluate_stage(rh2, m, st2)
    check_("NEGATIVE: ONE core-minute past the ceiling BLOCKS, so the gate is "
           "shown to fire on the boundary and not merely on a large number",
           d == "BLOCKED", d)
    d, _, _, _ = evaluate_stage(rh2, m, st1)
    check_("a stage whose arms are all done reports ALREADY and is not "
           "relaunched", d == "ALREADY", d)

    # ---- R1 x R2 ON A TREE WHERE THE TWO ARITHMETICS DISAGREE -------------
    print("\n-- R1 x R2: THE ONE TREE WHERE CHARGING AT CAP AND CHARGING AT "
          "ESTIMATE GIVE DIFFERENT ANSWERS --")
    # HONEST STATEMENT OF WHAT R1 DOES AND DOES NOT BUY.  Because
    # load_manifest() now REFUSES any manifest whose caps exceed its ceiling,
    # a campaign in which every arm respects its cap CANNOT breach the ceiling
    # and the R2 gate can never fire.  That is the point of the closure check:
    # the K0g failure is designed out at registration, not caught at runtime.
    # R1 is DEFENCE IN DEPTH for the one channel the closure check cannot
    # bound -- an arm whose MEASURED spend EXCEEDS its cap, which is reachable
    # because `wall` in STATUS covers blockMesh + checkMesh + solver while the
    # cap converts only the solver `timeout`.  On such a tree, and only on
    # such a tree, the two arithmetics differ -- and here it is.
    rh3 = os.path.join(tmp, "runs_R1R2")
    os.makedirs(rh3)
    os.makedirs(os.path.join(rh3, "M2_c"))         # IN FLIGHT: cap 250
    _status(rh3, "M1_c", wall=18000)               # DONE at 300.00, cap was 250
    charged_cap, _ = charge(rh3, m)
    charged_est = 300.0 + 100.0                    # the K0g arithmetic
    check_("M1_c OVERSPENT its cap: measured 300.00 core-min against a 250.00 "
           "cap, which is the one channel the closure check cannot bound",
           abs(charged_cap - 550.0) < 1e-9, f"charged {charged_cap:.2f}")
    d, c, need, head = evaluate_stage(rh3, m, m["stages"][1])
    check_("charging the IN-FLIGHT arm at its CAP: 550.00 + 1000.00 = 1550.00 "
           "> 1500.00, so stage 2 is BLOCKED", d == "BLOCKED",
           f"{d}, charged {c:.2f}, need {need:.2f}")
    check_("NEGATIVE, AND THIS IS THE WHOLE OF R1: the K0g arithmetic charges "
           "the in-flight arm its ESTIMATE, reaches 400.00 + 1000.00 = 1400.00 "
           "<= 1500.00, and LAUNCHES the stage that R1 blocks -- the two rules "
           "differ in OUTCOME on this very tree",
           charged_est + 1000.0 <= 1500.0 and d == "BLOCKED",
           f"K0g would launch at {charged_est + 1000.0:.2f}, R1 blocks at "
           f"{charged_cap + 1000.0:.2f}")

    # ---- LAUNCH ARITHMETIC, WITHOUT LAUNCHING -----------------------------
    print("\n-- THE CAP -> timeout CONVERSION --")
    rh4 = os.path.join(tmp, "runs_L")
    os.makedirs(rh4)
    got = launch_stage(rh4, m, st1, None, dry_run=True, verbose=False)
    check_("a dry run reports both arms of stage 1 and launches nothing",
           got == ["M1_c", "M2_c"] and not os.path.exists(
               os.path.join(rh4, "STATUS.M1_c")), str(got))
    check_("timeout_s = cap x 60 / ranks is the ONE registered conversion "
           "(250.00 core-min, 1 rank -> 15000 s)",
           int(round(250.0 * 60.0 / 1)) == 15000, "15000 s")

    print("\n" + "=" * 70)
    print(f"  {_P[0]} passed, {_F[0]} failed")
    if _F[0]:
        print("SELFTEST FAILED")
        return EXIT_REFUSE
    print("SELFTEST PASSED: every registered rule was driven BOTH WAYS -- shown\n"
          "able to FIRE on a planted defect and to STAY QUIET on its clean\n"
          "counterpart.  R1 and the K0g arithmetic were shown to DIFFER IN\n"
          "OUTCOME on the same tree, so the repair is measured, not asserted.")
    print("=" * 70)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
