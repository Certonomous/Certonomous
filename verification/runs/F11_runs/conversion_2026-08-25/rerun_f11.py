#!/usr/bin/env python3
"""
F11 CONVERSION -- the launcher, frozen with the pre-registration.

Drives the six solves of section 6 of
``verification/campaign/F11_CONVERSION_PREREGISTRATION.md`` (committed
157793db5ff6bbdda7ab22299abe5725d96e9b37) into FRESH case directories under
``conversion_2026-08-25/runs/<rung>/<level>/``.

``verification/runs/F11_runs/cavity_ladder.py`` is used BYTE-UNCHANGED as the
case generator (section 6), and this file verifies that before it builds
anything.  It adds only the three artifacts the completion rule needs and that
module does not write -- ``meta.json``, ``run_rc.txt`` and
``launch_timing.json`` -- plus the ONE registered change to the case
dictionaries in section 6.1, applied with an assert and never blind.

BUDGET (CLAUDE.md rule 12; section 7).  The cap is HARD: **13.0 core-minutes =
780 core-seconds**.  AN OVERRUN STOPS THE RUN; IT DOES NOT GET A NEW BUDGET.
Three enforcement points, all here:

  1. a per-run wall cap of ``max(60 s, 2.5 x predicted)`` -- 60 / 60 / 442 for
     the Re 1000 ladder and 60 / 60 / 674 for Re 100.  A run past its cap is
     SIGTERMed and recorded ``KILLED``, which fails C1/C2 and therefore grades
     its ladders NOT A RESULT -- never a softened number;
  2. a pre-wave budget check -- a wave whose predicted cost does not fit the
     remaining budget with 20 % headroom is NOT LAUNCHED and its ladders grade
     PENDING;
  3. a GLOBAL WATCHDOG polling every 5 s that terminates every live run the
     moment cumulative core-seconds reach 780.  **This is the binding
     enforcement**: the per-run caps sum ABOVE the budget, so the per-run caps
     alone do not enforce it.

     A DEFECT IN THE FROZEN DOCUMENT, recorded here and NOT repaired: section 7
     states that sum as "1,296 s (21.6 core-min)".  The six caps that same
     paragraph registers -- 60, 60, 442, 60, 60, 674 -- sum to 1,355.575 s
     (22.59 core-min).  The arithmetic is wrong by 59.575 s.  It is IMMATERIAL
     to the clause's conclusion, which is that the caps sum above the 780 s
     budget so the watchdog binds; that holds a fortiori at the larger figure.
     The caps implemented below are the six the document registers, unchanged.
     Surfaced by grade_f11.py --selftest, which carries it as a live check.

THE GUARD (CLAUDE.md rule 4).  A child REFUSES (rc = 3) any case directory that
already exists, and separately refuses one carrying a ``0/`` or a time
directory.  No run in this conversion can inherit a ``0/``, a time directory or
a ``postProcessing/`` tree from the 2026-07-30 campaign or from a retry.

WHAT THIS FILE NEVER TOUCHES.  It signals only processes it started itself.
Other teams' solvers on this box are never inspected for a kill and never
signalled, and this launcher writes nothing outside
``verification/runs/F11_runs/conversion_2026-08-25/``.

Per-run wall seconds and rank count are written to ``launch_timing.json`` in
every case directory so that core-minutes are computable FROM LOGS afterwards
for the mandatory ``docs/COST_CALIBRATION.md`` row (section 7).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
F11_ROOT = os.path.dirname(HERE)                  # verification/runs/F11_runs
REPO = os.path.dirname(os.path.dirname(os.path.dirname(F11_ROOT)))
RUNS = os.path.join(HERE, "runs")
sys.path.insert(0, F11_ROOT)

FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

# ---------------------------------------------------------------------------
# FROZEN -- transcribed from the pre-registration, not chosen here
# ---------------------------------------------------------------------------

# section 6: the run matrix.  (level name, n, cells, endTime)
LEVELS = (
    ("coarse", 32, 1024, 4000),
    ("medium", 64, 4096, 4000),
    ("fine", 128, 16384, 9000),
)
RUNGS = ("re1000", "re100")
RE_OF = {"re100": 100.0, "re1000": 1000.0}
GRADING_RATIO = 8.0            # section 4.1: held at 8.0 on EVERY level, so
                               # the mesh family is geometrically self-similar

# section 7: predicted core-seconds, per run.  cost_basis is in the
# pre-registration; the n = 32 rows are labelled ESTIMATE there and the rest
# are measured from named logs.
PRED = {
    ("re1000", "coarse"): 4.0,       # ESTIMATE, labelled (no n = 32 exists)
    ("re1000", "medium"): 14.39,     # measured
    ("re1000", "fine"): 176.73,      # measured
    ("re100", "coarse"): 4.0,        # ESTIMATE, labelled
    ("re100", "medium"): 12.58,      # measured
    ("re100", "fine"): 269.50,       # measured rate x measured iteration count
}
COST_BASIS = {
    ("re1000", "coarse"): "ESTIMATE, labelled -- no n = 32 measurement exists",
    ("re1000", "medium"): "measured, f11_re1000_n64_20260730T041833Z.log",
    ("re1000", "fine"): "measured, f11_re1000_n128_20260730T041833Z.log",
    ("re100", "coarse"): "ESTIMATE, labelled -- no n = 32 measurement exists",
    ("re100", "medium"): "measured, f11_re100_n64_20260730T041833Z.log",
    ("re100", "fine"): "measured rate x measured iteration count, "
                       "f11_re100_n128_20260730T041833Z.log",
}

# section 7: the cap and its enforcement
CAP_CORE_MIN = 13.0
CAP_CORE_S = 780.0
WATCHDOG_POLL_S = 5.0
WAVE_HEADROOM = 1.20           # "with 20 % headroom"
MAX_CONCURRENT = 2             # "At most 2 live runs, deliberately below the
                               # box's core count"

# section 7: launch order, FROZEN.  If the budget stops the line, wave 4 is
# lost first and the three Re 100 ladders grade PENDING -- a triple is never
# left half-built: losing a wave loses a whole rung, never one level.
WAVES = (
    (("re1000", "coarse"), ("re1000", "medium")),
    (("re1000", "fine"),),
    (("re100", "coarse"), ("re100", "medium")),
    (("re100", "fine"),),
)

# section 6: the generator is used BYTE-UNCHANGED.
CAVITY_LADDER_REL = "verification/runs/F11_runs/cavity_ladder.py"
CAVITY_LADDER_BLOB = "e9381a6e140c2e182c1f32c6c350b38d9f3db597"

RANKS = 1                      # section 7: "All runs are serial, 1 rank"

RC_OK, RC_FAIL, RC_REFUSE_EXISTS, RC_KILLED = 0, 1, 3, 143


def wall_cap(key):
    """Section 7 enforcement point 1: max(60 s, 2.5 x predicted).  Reproduces
    the frozen 60 / 60 / 442 / 60 / 60 / 674 -- asserted in
    grade_f11.py --selftest, not merely claimed here."""
    return max(60.0, 2.5 * PRED[key])


def case_dir(key):
    return os.path.join(RUNS, key[0], key[1])


def level_spec(level):
    for name, n, cells, cap in LEVELS:
        if name == level:
            return n, cells, cap
    raise KeyError(level)


# ---------------------------------------------------------------------------
# the generator freeze
# ---------------------------------------------------------------------------

def verify_generator():
    path = os.path.join(REPO, CAVITY_LADDER_REL)
    with open(path, "rb") as fh:
        data = fh.read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    got = h.hexdigest()
    if got != CAVITY_LADDER_BLOB:
        sys.stderr.write(
            "REFUSED: section 6 uses %s BYTE-UNCHANGED as the case generator, "
            "and it is not byte-unchanged.\n  frozen  %s\n  on disk %s\n"
            % (CAVITY_LADDER_REL, CAVITY_LADDER_BLOB, got))
        return None
    return got


# ---------------------------------------------------------------------------
# section 6.1 -- the ONE registered change to the case dictionaries
# ---------------------------------------------------------------------------

def apply_section_6_1(case, end_time):
    """The ``centerlineProfiles`` function object carries
    ``executeControl onEnd; writeControl onEnd;``, which writes ONE sample set
    per run -- from which no plateau can be measured.  Section 6.1 changes it
    to ``executeControl timeStep; executeInterval 250; writeControl timeStep;
    writeInterval 250``.

    FIELD WRITES ARE UNTOUCHED: ``controlDict``'s top-level ``writeControl
    timeStep; writeInterval <endTime>; purgeWrite 1`` is asserted intact
    afterwards, so this adds no field I/O.  It changes WHEN a sample is
    written, never WHAT the converged field is.

    Inserted with an assert, never blind (CLAUDE.md rule 14's discipline):
    exactly one occurrence of each line must be found, or this refuses.
    """
    path = os.path.join(case, "system", "controlDict")
    txt = open(path).read()

    txt, n_exec = re.subn(
        r"^(\s*)executeControl(\s+)onEnd;[ \t]*$",
        lambda m: ("%sexecuteControl%stimeStep;\n%sexecuteInterval%s250;"
                   % (m.group(1), m.group(2), m.group(1), m.group(2))),
        txt, flags=re.M)
    if n_exec != 1:
        raise RuntimeError(
            "section 6.1: expected exactly ONE 'executeControl onEnd;' in %s, "
            "found %d -- refusing to edit a dictionary that is not the one "
            "the pre-registration describes" % (path, n_exec))

    txt, n_write = re.subn(
        r"^(\s*)writeControl(\s+)onEnd;[ \t]*$",
        lambda m: ("%swriteControl%stimeStep;\n%swriteInterval%s250;"
                   % (m.group(1), m.group(2), m.group(1), m.group(2))),
        txt, flags=re.M)
    if n_write != 1:
        raise RuntimeError(
            "section 6.1: expected exactly ONE 'writeControl onEnd;' in %s, "
            "found %d" % (path, n_write))

    # FIELD WRITES UNTOUCHED -- asserted, not assumed.
    if len(re.findall(r"^\s*writeInterval\s+%d;\s*$" % end_time, txt,
                      re.M)) != 1:
        raise RuntimeError(
            "section 6.1 must leave the top-level 'writeInterval %d;' intact "
            "in %s and it did not" % (end_time, path))
    if len(re.findall(r"^\s*writeInterval\s+250;\s*$", txt, re.M)) != 1:
        raise RuntimeError("section 6.1: the sampling writeInterval 250 was "
                           "not inserted exactly once in %s" % path)
    if len(re.findall(r"^\s*executeInterval\s+250;\s*$", txt, re.M)) != 1:
        raise RuntimeError("section 6.1: the executeInterval 250 was not "
                           "inserted exactly once in %s" % path)
    if len(re.findall(r"^\s*purgeWrite\s+1;\s*$", txt, re.M)) != 1:
        raise RuntimeError("section 6.1 must leave 'purgeWrite 1;' intact in "
                           "%s" % path)
    if len(re.findall(r"^\s*endTime\s+%d;\s*$" % end_time, txt, re.M)) != 1:
        raise RuntimeError("the endTime in %s is not the section 6 value %d"
                           % (path, end_time))
    if "onEnd" in txt:
        raise RuntimeError("an 'onEnd' control survived the section 6.1 edit "
                           "in %s" % path)
    open(path, "w").write(txt)
    return dict(section="6.1", executeControl="timeStep", executeInterval=250,
                writeControl="timeStep", writeInterval=250,
                field_writes_untouched=True, endTime=end_time)


# ---------------------------------------------------------------------------
# child: one run
# ---------------------------------------------------------------------------

_LIVE = {"proc": None, "case": None, "t0": None}


def _sigterm(signum, frame):
    """SIGTERMed by the watchdog or by a per-run wall cap.  Kill the solver,
    record a NON-ZERO rc so the run fails C1, record the timing so the wall
    seconds spent are still costed, and exit.  A killed run is never softened
    into a number."""
    p = _LIVE.get("proc")
    if p is not None and p.poll() is None:
        try:
            p.send_signal(signal.SIGTERM)
            p.wait(timeout=20)
        except Exception:                                      # noqa: BLE001
            try:
                p.kill()
            except Exception:                                  # noqa: BLE001
                pass
    case = _LIVE.get("case")
    if case and os.path.isdir(case):
        open(os.path.join(case, "run_rc.txt"), "w").write("%d\n" % RC_KILLED)
        json.dump(dict(wall_s=time.time() - (_LIVE.get("t0") or time.time()),
                       ranks=RANKS, killed=True,
                       killed_reason="SIGTERM -- budget cap or per-run wall "
                                     "cap; an overrun stops the run and does "
                                     "not get a new budget"),
                  open(os.path.join(case, "launch_timing.json"), "w"),
                  indent=2)
    sys.exit(RC_KILLED)


def sh(cmd, cwd, logfile):
    """Run one OpenFOAM utility, keeping its log.  Registered as its own
    subprocess so the SIGTERM handler can reach it."""
    full = "source %s >/dev/null 2>&1; %s" % (FOAM_BASHRC, cmd)
    p = subprocess.Popen(["bash", "-c", full], cwd=cwd,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    _LIVE["proc"] = p
    out, _ = p.communicate()
    _LIVE["proc"] = None
    with open(logfile, "wb") as fh:
        fh.write(out)
    return p.returncode


def run_one_child(rung, level):
    key = (rung, level)
    cd = case_dir(key)
    _LIVE["case"], _LIVE["t0"] = cd, time.time()

    # ---- THE GUARD (CLAUDE.md rule 4; section 5) --------------------------
    if os.path.exists(cd):
        sys.stderr.write(
            "REFUSED: %s already exists. The completion rule's guard refuses a "
            "case where 0/ or a time directory already exists, and this "
            "conversion always runs into a FRESH directory -- it never "
            "inherits a 0/, a time directory or a postProcessing/ tree from "
            "the 2026-07-30 campaign or from a retry.\n" % cd)
        return RC_REFUSE_EXISTS
    for parent in (os.path.join(RUNS, rung),):
        stale = os.path.join(parent, level)
        if os.path.exists(stale):
            sys.stderr.write("REFUSED: %s already exists\n" % stale)
            return RC_REFUSE_EXISTS

    if verify_generator() is None:
        return RC_FAIL

    n, cells, end_time = level_spec(level)
    os.makedirs(cd)
    signal.signal(signal.SIGTERM, _sigterm)
    rc = RC_FAIL
    try:
        import cavity_ladder
        meta = cavity_ladder.build_case(cd, RE_OF[rung], n,
                                        max_iter=end_time,
                                        grading_ratio=GRADING_RATIO)
        if meta["cells"] != cells:
            raise RuntimeError("the generator built %d cells at n = %d; "
                               "section 6 registers %d"
                               % (meta["cells"], n, cells))
        meta["rung"], meta["level"] = rung, level
        meta["section_6_1"] = apply_section_6_1(cd, end_time)
        meta["generator_blob"] = CAVITY_LADDER_BLOB
        meta["predicted_core_s"] = PRED[key]
        meta["cost_basis"] = COST_BASIS[key]
        meta["wall_cap_s"] = wall_cap(key)
        meta["ranks"] = RANKS
        json.dump(meta, open(os.path.join(cd, "meta.json"), "w"), indent=2)

        if sh("blockMesh", cd, os.path.join(cd, "log.blockMesh")) != 0:
            raise RuntimeError("blockMesh failed; see log.blockMesh")
        # Mesh birth certificate (section 4.4, VERIFICATION section 9 v1.5):
        # every level runs checkMesh at creation and RETAINS log.checkMesh. A
        # level whose checkMesh is not clean does not enter the ladder --
        # grade_f11.py reads this log and grades that row NOT A RESULT.
        sh("checkMesh", cd, os.path.join(cd, "log.checkMesh"))

        # THE AGE GUARD'S ANCHOR (CLAUDE.md rule 4): 0/ is touched LAST before
        # the solver starts, so it dates the run that was allowed to produce
        # the answer. Every field and every sampled .xy must be strictly newer.
        now = time.time()
        for f in os.listdir(os.path.join(cd, "0")):
            os.utime(os.path.join(cd, "0", f), (now, now))
        time.sleep(0.01)

        rc_solve = sh("simpleFoam", cd, os.path.join(cd, "log.simpleFoam"))
        rc = RC_OK if rc_solve == 0 else RC_FAIL
        if rc != RC_OK:
            sys.stderr.write("simpleFoam rc=%d in %s\n" % (rc_solve, cd))
    except Exception as exc:                                   # noqa: BLE001
        sys.stderr.write("FAILED %s/%s: %r\n" % (rung, level, exc))
        rc = RC_FAIL
    open(os.path.join(cd, "run_rc.txt"), "w").write("%d\n" % rc)
    json.dump(dict(wall_s=time.time() - _LIVE["t0"], ranks=RANKS,
                   killed=False, predicted_core_s=PRED[key],
                   cost_basis=COST_BASIS[key]),
              open(os.path.join(cd, "launch_timing.json"), "w"), indent=2)
    return rc


# ---------------------------------------------------------------------------
# parent: waves, pre-wave budget check, global watchdog
# ---------------------------------------------------------------------------

def load_reading():
    """Section 7: load is checked before each wave.  RECORDED, not gated -- no
    load threshold is registered in the pre-registration and inventing one here
    would be inventing a clause.  Other teams' solvers are observed and never
    touched."""
    try:
        la1, la5, la15 = os.getloadavg()
    except OSError:
        la1 = la5 = la15 = None
    return dict(loadavg_1min=la1, loadavg_5min=la5, loadavg_15min=la15,
                cpu_count=os.cpu_count(),
                note="recorded, NOT gated; this launcher signals only "
                     "processes it started itself")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--dry-run", action="store_true",
                    help="print the frozen matrix, caps and budget arithmetic "
                         "and launch NOTHING")
    a = ap.parse_args()

    total_pred = sum(PRED.values())
    if a.dry_run:
        print("F11 CONVERSION -- launcher, DRY RUN. Nothing is launched.")
        print("  cap %.1f core-min = %.0f core-s (HARD; an overrun stops the "
              "run)" % (CAP_CORE_MIN, CAP_CORE_S))
        print("  predicted total %.2f core-s = %.4f core-min"
              % (total_pred, total_pred / 60.0))
        print("  per-run wall caps sum to %.1f s, ABOVE the budget -- the "
              "watchdog is the binding enforcement"
              % sum(wall_cap(k) for k in PRED))
        cum = 0.0
        for i, wave in enumerate(WAVES, 1):
            cum += sum(PRED[k] for k in wave)
            print("  wave %d: %-34s pred %7.2f core-s  cum %.2f core-min"
                  % (i, ", ".join("/".join(k) for k in wave),
                     sum(PRED[k] for k in wave), cum / 60.0))
        for k in PRED:
            print("    %-16s n=%-4d endTime %-5d wall cap %6.1f s  pred "
                  "%7.2f core-s  [%s]"
                  % ("/".join(k), level_spec(k[1])[0], level_spec(k[1])[2],
                     wall_cap(k), PRED[k], COST_BASIS[k]))
        print("  generator %s blob %s: %s"
              % (CAVITY_LADDER_REL, CAVITY_LADDER_BLOB,
                 "VERIFIED byte-unchanged" if verify_generator()
                 else "MISMATCH -- would refuse"))
        return RC_OK

    if verify_generator() is None:
        return RC_FAIL
    os.makedirs(RUNS, exist_ok=True)
    ledger = dict(cap_core_min=CAP_CORE_MIN, cap_core_s=CAP_CORE_S,
                  predicted_total_core_s=total_pred, ranks=RANKS,
                  runs={}, waves={}, stopped_by=None,
                  cost_basis_note="core-minutes = wall s x ranks / 60 and are "
                                  "the MEASURED unit. Dollars are DERIVED at "
                                  "the owner-stated $0.0513/core-h; this box "
                                  "cannot read its own billing "
                                  "(COMPUTE_BUDGET_CHARTER section 5). A "
                                  "docs/COST_CALIBRATION.md row is MANDATORY "
                                  "at completion.")
    ledger_path = os.path.join(HERE, "F11_CONVERSION_RUN_LEDGER.json")

    def flush():
        ledger["spent_core_min"] = round(spent_s / 60.0, 4)
        ledger["cap_respected"] = spent_s <= CAP_CORE_S
        json.dump(ledger, open(ledger_path, "w"), indent=2)

    spent_s = 0.0
    stopped = False
    for wi, wave in enumerate(WAVES, 1):
        ledger["waves"][str(wi)] = dict(runs=["/".join(k) for k in wave],
                                        load_before=load_reading(),
                                        predicted_core_s=sum(PRED[k]
                                                             for k in wave))
        if stopped:
            for k in wave:
                ledger["runs"]["/".join(k)] = dict(
                    status="PENDING",
                    reason="the budget stopped the line before wave %d; a "
                           "triple is never left half-built, so a whole rung "
                           "is lost, never one level" % wi)
            continue

        # ---- enforcement point 2: the pre-wave budget check ---------------
        pred_wave = sum(PRED[k] for k in wave)
        if spent_s + pred_wave * WAVE_HEADROOM > CAP_CORE_S:
            for k in wave:
                ledger["runs"]["/".join(k)] = dict(
                    status="PENDING",
                    reason="wave %d not launched: %.2f spent + %.2f predicted "
                           "x %.2f headroom exceeds the %.0f core-s cap"
                           % (wi, spent_s, pred_wave, WAVE_HEADROOM,
                              CAP_CORE_S))
            ledger["stopped_by"] = ("pre-wave budget check before wave %d"
                                    % wi)
            stopped = True
            flush()
            continue

        procs = {}
        for k in wave[:MAX_CONCURRENT]:
            cmd = [sys.executable, os.path.abspath(__file__), "--one",
                   k[0], k[1]]
            procs[k] = dict(p=subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                               stderr=subprocess.PIPE),
                            t0=time.time())
            print("[wave %d] launched %s (cap %.0f s, pred %.2f core-s)"
                  % (wi, "/".join(k), wall_cap(k), PRED[k]), flush=True)

        # ---- enforcement points 1 and 3: wall caps and the global watchdog -
        while any(v["p"].poll() is None for v in procs.values()):
            time.sleep(WATCHDOG_POLL_S)
            for v in procs.values():
                if v["p"].poll() is not None and "wall" not in v:
                    v["wall"] = time.time() - v["t0"]
            live_s = sum(time.time() - v["t0"] for v in procs.values()
                         if v["p"].poll() is None)
            done_s = sum(v["wall"] for v in procs.values() if "wall" in v)
            if (spent_s + live_s + done_s) * RANKS >= CAP_CORE_S:
                for k, v in procs.items():
                    if v["p"].poll() is None:
                        v["p"].send_signal(signal.SIGTERM)
                        v["killed"] = ("global watchdog: cumulative core-s "
                                       "reached the %.0f s cap" % CAP_CORE_S)
                ledger["stopped_by"] = ("global watchdog reached the %.1f "
                                        "core-min cap" % CAP_CORE_MIN)
                stopped = True
                break
            for k, v in procs.items():
                if v["p"].poll() is None and \
                        (time.time() - v["t0"]) > wall_cap(k):
                    v["p"].send_signal(signal.SIGTERM)
                    v["killed"] = "per-run wall cap %.0f s" % wall_cap(k)

        for k, v in procs.items():
            v["p"].wait()
            v.setdefault("wall", time.time() - v["t0"])
            spent_s += v["wall"] * RANKS
            name = "/".join(k)
            status = ("KILLED" if "killed" in v else
                      ("OK" if v["p"].returncode == 0 else
                       ("REFUSED_EXISTS"
                        if v["p"].returncode == RC_REFUSE_EXISTS
                        else "FAILED")))
            ledger["runs"][name] = dict(
                status=status, killed_reason=v.get("killed"),
                rc=v["p"].returncode, predicted_core_s=PRED[k],
                actual_core_s=round(v["wall"] * RANKS, 2),
                ratio_actual_over_predicted=round(v["wall"] * RANKS
                                                  / PRED[k], 3),
                cost_basis=COST_BASIS[k], ranks=RANKS,
                wall_cap_s=wall_cap(k), case_dir=case_dir(k),
                stderr_tail=(v["p"].stderr.read().decode()[-1200:]
                             if v["p"].stderr else ""))
            print("[wave %d] %-16s %-14s %7.1f core-s (pred %6.2f)  "
                  "cum %.3f core-min"
                  % (wi, name, status, v["wall"] * RANKS, PRED[k],
                     spent_s / 60.0), flush=True)
        flush()
        if stopped:
            for later in WAVES[wi:]:
                for k in later:
                    ledger["runs"].setdefault("/".join(k), dict(
                        status="PENDING",
                        reason="the budget stopped the line at wave %d" % wi))
            break

    flush()
    print("\nTOTAL %.4f core-min against a %.1f core-min cap (respected: %s)"
          % (spent_s / 60.0, CAP_CORE_MIN, ledger["cap_respected"]))
    print("predicted %.4f core-min; ratio actual/predicted = %.3f"
          % (total_pred / 60.0,
             (spent_s / total_pred) if total_pred else float("nan")))
    print("ledger: %s" % ledger_path)
    print("A docs/COST_CALIBRATION.md row is MANDATORY at completion "
          "(CLAUDE.md rule 12, section 7): actual core-minutes from the logs, "
          "the ratio actual/predicted, and the gap attributed between "
          "contention, waste and misprediction -- waste named separately and "
          "never absorbed into the ratio.")
    return RC_OK if ledger["cap_respected"] else RC_FAIL


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--one":
        sys.exit(run_one_child(sys.argv[2], sys.argv[3]))
    sys.exit(main())
