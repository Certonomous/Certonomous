#!/usr/bin/env python3
"""D6RG SUCCESSOR COMPARATOR -- re-grades D6R from its PRESERVED RUN ROOT through ONE
repaired reader.  ZERO SOLVER COMPUTE: nothing meshed, nothing solved, no container, no GPU.

WHY A SUCCESSOR AND NOT A RE-RUN.  D6R's `O_mp` arm SPENT 2,257.933 core-min and its
artefacts are INTACT (no file under the run root has an mtime later than 2026-08-29T02:01:00Z,
and the box went down 12 h 40 m later, so nothing was torn).  Re-running `O_mp` would spend
~2,500 core-min to reproduce the same numerical failure -- buying the same answer twice.  The
preserved artefacts are read instead.

HOW IT RE-GRADES, and this is the whole design: IT RE-IMPLEMENTS NO GATE.  It imports D6R's
OWN FROZEN COMPARATOR, verifies the file on disk is byte-identical to the committed blob,
REBINDS EXACTLY ONE NAME, and runs THE FROZEN `grade()`.  Every band, threshold, cap, label,
composition rule, prediction and refusal clause that decides a verdict is literally the frozen
code, unedited on disk.  The successor's contribution is one function body, and the rebind
audit below proves it is one.

  D6R   `d6r_grade.py:615-624`  rebind `read_ipopt`   (D6R-GRADER-DEF-2)

THE DEFECT.  `read_ipopt` requires BOTH an `Objective...............:` summary line AND an
`EXIT:` line, refusing at `:620-621` if either is missing.  IPOPT dying on `Eval_Error`
substitutes the exception text for the summary block, so a log that is otherwise complete
cannot be read.  Driven on this box 2026-08-30, the FROZEN grader unmodified against the
preserved root: exit code 2, `REFUSE G-D6R-OPT no_final_objective_or_exit n_obj=0 n_exit=1`,
NO verdict JSON written and ZERO of its ten registered gate readings printed.

WHAT THE REPAIR MAY NOT DO.  It may not invent an objective.  The final objective is
RECOVERED FROM THE ITERATION TABLE IN THE FILE, and its provenance is recorded as the
ITERATION ROW and NOT the summary line, because those are different claims -- see
`d6rg_reader.py`.  Seven registered gates stand between an unreadable log and a recovered
number and every one of them REFUSES through the FROZEN module's own `refuse()`.

PRESERVED ROOTS ARE NEVER WRITTEN.  Every regrade runs on a `cp -a` COPY.  An md5 manifest of
every regular file in BOTH preserved roots is taken before and after the whole execution and
the run REFUSES (`PRESERVED_ROOT_MUTATED`, naming the moved paths) if a single hash moves.  It
READS THE DISK, NOT GIT: a run root is not in git, so a git-based cleanliness check is blind to
exactly the thing being protected.

BIRTH REQUIREMENT, BOTH DIRECTIONS.  A repaired reader's entire risk is that it LAUNDERS A
GENUINE ABSENCE INTO A READING, so the MUST-FLAG direction is the point, not decoration.  Ten
plants travel the REAL frozen grader over the REAL preserved artefacts and every one must
still REFUSE; the MUST-NOT-FLAG direction is D4's real, complete log, which must be read by
the ORIGINAL summary-line path and not by the repaired one.

L-332: NO `assert` anywhere in either successor file; both are AST-counted before anything
runs and the counter is shown able to see a planted one.
"""
import argparse
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time

# Set BEFORE any local import: importing a comparator must never drop a __pycache__ beside a
# frozen case's files, and no stale bytecode may invert a unit (L-332 / the stale-pycache trap).
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
A2 = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(A2, "..", "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import d6rg_reader as R                                                       # noqa: E402

VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
EXPECTED_UNITS = 27

# ---- REGISTERED, frozen with PREREGISTRATION.md ---------------------------------------
FROZEN_GRADER_REL = "cases/dafoam/ladder-a/A2/curriculum_D6R/d6r_grade.py"
FROZEN_PREREG_REL = "cases/dafoam/ladder-a/A2/curriculum_D6R/PREREGISTRATION.md"
# d6r_grade.py AFTER D6R's AMENDMENT 1, the value D6R_chain_wait.json carries as
# `grader_md5_post_amendment`.  L-370: the pins at PREREGISTRATION.md section 7:414 and
# section 8:478 are PRE-amendment and a check that stops there reports a false drift.
FROZEN_GRADER_MD5 = "bc8e9fec48b3f58ce7a96f4b9549590b"
FROZEN_PREREG_MD5 = "e525084daac50c82738170925894fbe1"
REBIND_REGISTERED = ("read_ipopt",)
PRESERVED_D6R = "/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint"
PRESERVED_D4_O = "/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O"
OPT_LOG_REL = os.path.join("O_mp", "opt_IPOPT.txt")
# The measured endpoint, carried so a unit can prove the reader reads the FILE.
D6R_FINAL_MAJOR = 73
D6R_FINAL_OBJ_TEXT = "2.2238800e-02"
D4_FINAL_OBJ = 2.1125978108239574e-02
# The three carried-forward findings, registered here as EXPECTATIONS the units check.
CARRIED_S1_CUTBACKS = 673
CARRIED_G10_FRAME_GAP_S = 75
CARRIED_G10_ALLOWANCE_S = 30            # FRAME_ALLOWANCE_S(90) - KILL_GRACE_S(60)

_ORIGINALS = []                          # keeps rebound originals alive; id() must not recycle


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


def md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def manifest(root):
    """md5 of every regular file under `root`, keyed by relative path.  A run root is not in
    git, so `git status` is blind to it; the DISK is read."""
    out = {}
    for dp, _dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            if os.path.isfile(p) and not os.path.islink(p):
                out[os.path.relpath(p, root)] = md5_file(p)
    return out


GIT_ALLOWED = {"cat-file", "rev-parse", "ls-tree"}


def git(*args):
    if args[0] not in GIT_ALLOWED:
        refuse("GIT_SUBCOMMAND_NOT_ALLOWED", {"asked": args[0], "allowed": sorted(GIT_ALLOWED)})
    r = subprocess.run(["git", "-C", REPO] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    return r.returncode, r.stdout


def committed_blob_md5(rel, rev="HEAD"):
    """rule 2: verify the frozen file IS the file that ran, by hashing it against the
    COMMITTED BLOB -- not against a value typed into a document."""
    rc, out = git("cat-file", "blob", "%s:%s" % (rev, rel))
    if rc != 0:
        refuse("COMMITTED_BLOB_ABSENT", {"rev": rev, "path": rel})
    return hashlib.md5(out).hexdigest()


def check_frozen_files():
    """Both directions of rule 2 on BOTH frozen files: disk == registered md5, AND
    disk == the committed blob at HEAD."""
    rec = {}
    for rel, reg in ((FROZEN_GRADER_REL, FROZEN_GRADER_MD5), (FROZEN_PREREG_REL, FROZEN_PREREG_MD5)):
        p = os.path.join(REPO, rel)
        if not os.path.isfile(p):
            refuse("FROZEN_FILE_ABSENT", {"path": p})
        disk = md5_file(p)
        blob = committed_blob_md5(rel)
        if disk != reg:
            refuse("FROZEN_MD5_NOT_REGISTERED", {"path": rel, "registered": reg, "on_disk": disk})
        if disk != blob:
            refuse("FROZEN_DISK_NOT_COMMITTED_BLOB", {"path": rel, "on_disk": disk,
                                                      "committed_blob_HEAD": blob})
        rec[rel] = {"registered_md5": reg, "on_disk_md5": disk, "committed_blob_md5_HEAD": blob,
                    "disk_equals_registered": True, "disk_equals_committed_blob": True}
    rc, out = git("rev-parse", "HEAD")
    rec["HEAD"] = out.decode().strip() if rc == 0 else None
    return rec


def load_frozen():
    """Import D6R's frozen comparator AFTER proving the file on disk is the file that was
    frozen.  Bytecode writing is disabled so importing a frozen case's comparator cannot drop
    a __pycache__ into its directory, and no stale bytecode can invert a unit."""
    sys.dont_write_bytecode = True
    rec = check_frozen_files()
    path = os.path.join(REPO, FROZEN_GRADER_REL)
    name = "d6rg_frozen_D6R_%d" % len(_ORIGINALS)
    sp = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(sp)
    sys.modules[name] = mod
    sp.loader.exec_module(mod)
    return mod, rec


def _fingerprint(mod):
    return {k: id(v) for k, v in vars(mod).items() if callable(v)}


# =======================================================================================
# THE ONE REPAIR.  Same signature and same return shape as the frozen `read_ipopt`, and it
# raises THE FROZEN MODULE'S OWN `refuse`, so a refusal from here is shaped exactly like the
# refusal that instrument would have raised.  Every regex it matches with is the FROZEN
# module's own.  When the summary line IS present it DELEGATES TO THE FROZEN FUNCTION
# VERBATIM -- the must-NOT-flag direction is structural, not a promise.
# =======================================================================================
def make_repaired_read_ipopt(mod, audit):
    original = mod.read_ipopt
    _ORIGINALS.append(original)

    def read_ipopt(path, where="read_ipopt"):
        if not os.path.isfile(path):
            mod.refuse(where, {"absent": path})
        txt = open(path, errors="replace").read()
        objs, exits = mod.OBJ_RE.findall(txt), mod.EXIT_RE.findall(txt)
        if objs and exits:
            r = dict(original(path, where))
            r.update({"summary_line_present": True, "objective_provenance": "SUMMARY_LINE",
                      "repair_branch_taken": False})
            audit[path] = {"branch": "ORIGINAL", "n_obj": len(objs), "n_exit": len(exits),
                           "objective": r["objective"], "provenance": "SUMMARY_LINE"}
            return r
        r = R.recover_nonfinite_exit(path, txt, where, mod.refuse,
                                     mod.EXIT_RE, mod.NIT_RE, mod.MAJOR_ROW_RE)
        audit[path] = {"branch": "REPAIRED", "n_obj": len(objs), "n_exit": len(exits),
                       "objective": r["objective"], "provenance": r["objective_provenance"],
                       "row_major": r["objective_row_major"],
                       "printed_significant_digits": r["objective_printed_significant_digits"]}
        return r
    return read_ipopt


# ================= plants.  They mutate the COPY's log, never the preserved root ========
def _is_major_row(line, MAJOR_ROW_RE):
    return bool(MAJOR_ROW_RE.match(line))


def _major_of(line, MAJOR_ROW_RE):
    m = MAJOR_ROW_RE.match(line)
    return (int(m.group("n")) if m else None)


def _edit(copy_root, fn):
    p = os.path.join(copy_root, OPT_LOG_REL)
    txt = open(p, errors="replace").read()
    open(p, "w").write(fn(txt))


def plant_no_table(mod):
    def f(root):
        _edit(root, lambda t: "\n".join(l for l in t.splitlines()
                                        if not _is_major_row(l, mod.MAJOR_ROW_RE)) + "\n")
    return f


def plant_truncate_after_major(mod, n):
    """Cut the file the way a torn write cuts it: the table stops and the whole tail --
    `Number of Iterations`, the exception block and `EXIT:` -- is gone."""
    def f(root):
        def g(t):
            out = []
            for l in t.splitlines():
                out.append(l)
                if _major_of(l, mod.MAJOR_ROW_RE) == n:
                    break
            return "\n".join(out) + "\n"
        _edit(root, g)
    return f


def plant_torn_table(mod, keep_upto):
    """The DANGEROUS shape: the tail is intact and still reports 73 majors, but the table
    stops at `keep_upto`.  A reader that trusted the last readable row would publish an
    intermediate objective as the endpoint."""
    def f(root):
        def g(t):
            out = []
            for l in t.splitlines():
                mj = _major_of(l, mod.MAJOR_ROW_RE)
                if mj is not None and mj > keep_upto:
                    continue
                out.append(l)
            return "\n".join(out) + "\n"
        _edit(root, g)
    return f


def plant_hole(mod, lo, hi):
    def f(root):
        def g(t):
            out = []
            for l in t.splitlines():
                mj = _major_of(l, mod.MAJOR_ROW_RE)
                if mj is not None and lo <= mj <= hi:
                    continue
                out.append(l)
            return "\n".join(out) + "\n"
        _edit(root, g)
    return f


def plant_last_objective(mod, new_text):
    """Rewrite the objective token of the LAST major row, in place, inside the real file."""
    def f(root):
        def g(t):
            lines = t.splitlines()
            idx = [i for i, l in enumerate(lines) if _is_major_row(l, mod.MAJOR_ROW_RE)]
            i = idx[-1]
            m = mod.MAJOR_ROW_RE.match(lines[i])
            s, e = m.span("obj")
            lines[i] = lines[i][:s] + new_text + lines[i][e:]
            return "\n".join(lines) + "\n"
        _edit(root, g)
    return f


def plant_scaling(new):
    def f(root):
        _edit(root, lambda t: R.SCALING_LINE_RE.sub(
            lambda m: m.group(0).replace(m.group("v"), new, 1), t, count=1))
    return f


def plant_exit_line(mod, new_line):
    def f(root):
        _edit(root, lambda t: "\n".join((new_line if mod.EXIT_RE.match(l) else l)
                                        for l in t.splitlines()) + "\n")
    return f


def plant_drop_exit_line(mod):
    def f(root):
        _edit(root, lambda t: "\n".join(l for l in t.splitlines()
                                        if not mod.EXIT_RE.match(l)) + "\n")
    return f


def plant_drop_nit_line(mod):
    def f(root):
        _edit(root, lambda t: "\n".join(l for l in t.splitlines()
                                        if not mod.NIT_RE.match(l)) + "\n")
    return f


# ================= the regrade ==========================================================
class Bench(object):
    """ONE `cp -a` copy of the 1.07 GB preserved root, re-used across plants.  Between
    plants the SINGLE file under test is restored from a pristine byte copy and its md5 is
    RE-VERIFIED against the preserved original, so every plant starts from the real file.
    Taking a fresh 14,546-file copy per plant would read ~30 GB to prove the same property."""

    def __init__(self, workdir):
        self.work = workdir
        self.copy_root = os.path.join(workdir, "root_D6R")
        if not os.path.isdir(PRESERVED_D6R):
            refuse("PRESERVED_ROOT_ABSENT", {"root": PRESERVED_D6R})
        if os.path.isdir(self.copy_root):
            shutil.rmtree(self.copy_root)
        rc = subprocess.run(["cp", "-a", PRESERVED_D6R, self.copy_root]).returncode
        if rc != 0:
            refuse("COPY_FAILED", {"src": PRESERVED_D6R, "dst": self.copy_root, "rc": rc})
        self.log_copy = os.path.join(self.copy_root, OPT_LOG_REL)
        self.pristine_md5 = md5_file(os.path.join(PRESERVED_D6R, OPT_LOG_REL))
        self.pristine = os.path.join(workdir, "pristine_opt_IPOPT.txt")
        shutil.copyfile(os.path.join(PRESERVED_D6R, OPT_LOG_REL), self.pristine)
        if md5_file(self.pristine) != self.pristine_md5:
            refuse("PRISTINE_COPY_MOVED", {"expected": self.pristine_md5})

    def restore(self):
        shutil.copyfile(self.pristine, self.log_copy)
        got = md5_file(self.log_copy)
        if got != self.pristine_md5:
            refuse("RESTORE_FAILED", {"expected": self.pristine_md5, "got": got})


def regrade(bench, plant=None, label="production"):
    """Run the FROZEN `grade()` over the copy with the ONE registered name rebound."""
    bench.restore()
    if plant:
        plant(bench.copy_root)
    mod, frozen_rec = load_frozen()
    fp0 = _fingerprint(mod)
    audit = {}
    mod.read_ipopt = make_repaired_read_ipopt(mod, audit)
    fp1 = _fingerprint(mod)
    rebound = sorted(k for k in set(fp0) | set(fp1) if fp0.get(k) != fp1.get(k))
    if tuple(rebound) != REBIND_REGISTERED:
        refuse("REBIND_AUDIT", {"expected": list(REBIND_REGISTERED), "actual": rebound,
                                "note": "the successor replaces exactly the registered names and "
                                        "no others; everything else that decides the verdict is "
                                        "the frozen code"})
    out = {"label": label, "frozen": frozen_rec, "names_rebound": rebound}
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            r = mod.grade(bench.copy_root)
        out.update({"verdict": r.get("verdict"), "refusal": None, "grade": r})
    except mod.Refuse as ex:
        out.update({"verdict": "NOT A RESULT", "refusal": str(ex), "grade": None})
    out["frozen_stderr_tail"] = err.getvalue().strip().splitlines()[-1:]
    out["reader_audit"] = audit
    if out["verdict"] not in VOCAB:
        refuse("VOCAB", {"verdict": out["verdict"], "label": label})
    return out


def refusal_clause(out):
    """The refusal's own key, so a control checks WHICH clause fired, not merely that
    something did.  A control that only checks 'it refused' passes on the wrong refusal."""
    if not out.get("refusal"):
        return None
    txt = out["refusal"]
    i = txt.find("{")
    try:
        d = json.loads(txt[i:]) if i >= 0 else {}
    except ValueError:
        return "UNPARSEABLE"
    det = d.get("detail")
    keys = sorted(det.keys()) if isinstance(det, dict) else []
    return "%s:%s" % (d.get("REFUSE"), ",".join(keys))


def _refused_on(out, key):
    return out["verdict"] == "NOT A RESULT" and key in (out.get("refusal") or "")


# ================= selftest =============================================================
def selftest(work):
    n, fails, lines = 0, [], []

    def unit(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name.split(" ")[0])
        lines.append("  [%s] %s" % ("OK " if cond else "BAD", name))

    mod, frozen_rec = load_frozen()
    d6r_log = os.path.join(PRESERVED_D6R, OPT_LOG_REL)
    d4_log = os.path.join(PRESERVED_D4_O, "opt_IPOPT.txt")

    # ---- READER LEVEL, on the REAL preserved files ------------------------------------
    frozen_err = None
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            mod.read_ipopt(d6r_log, "U1")
    except mod.Refuse as ex:
        frozen_err = str(ex)
    unit("U1 THE DEFECT, reproduced through the FROZEN code: `read_ipopt` on D6R's preserved "
         "opt_IPOPT.txt REFUSES on `no_final_objective_or_exit` with n_obj=0 and n_exit=1 -- "
         "the EXIT line IS there and only the summary Objective line is missing",
         frozen_err is not None and "no_final_objective_or_exit" in frozen_err
         and '"n_obj": 0' in frozen_err and '"n_exit": 1' in frozen_err)

    with contextlib.redirect_stderr(io.StringIO()):
        d4_frozen = mod.read_ipopt(d4_log, "U2")
    unit("U2 PLANT THE ZERO -- the CONTROL that makes U1's absence evidence: the SAME frozen "
         "reader on D4's real complete log RETURNS objective %.16e, exit %r, n_iter %s.  A zero "
         "from a reader not shown able to see a non-zero is not evidence (rule 3)"
         % (d4_frozen["objective"], d4_frozen["exit"], d4_frozen["n_iter"]),
         abs(d4_frozen["objective"] - D4_FINAL_OBJ) < 1e-18 and d4_frozen["optimal"] is True
         and d4_frozen["n_iter"] == 80)

    s6, s4 = (R.read_scaling_method(open(d6r_log, errors="replace").read()),
              R.read_scaling_method(open(d4_log, errors="replace").read()))
    unit("U3 `nlp_scaling_method` is READ FROM BOTH LOGS as %r / %r, so the iteration table's "
         "single objective column equals the summary's UNSCALED column BY THE SETTING IN THE "
         "FILE and not by assumption" % (s6, s4),
         s6 == R.REQUIRED_SCALING and s4 == R.REQUIRED_SCALING)

    audit = {}
    rep = make_repaired_read_ipopt(mod, audit)
    with contextlib.redirect_stderr(io.StringIO()):
        d4_rep = rep(d4_log, "U4")
    unit("U4 MUST-NOT-FLAG: the REPAIRED reader on D4's real complete log takes the ORIGINAL "
         "path -- every key the frozen module consumes is EQUAL to the frozen reader's own "
         "return and the provenance is SUMMARY_LINE.  The repair is unreachable when the "
         "summary line is present",
         d4_rep["objective_provenance"] == "SUMMARY_LINE" and d4_rep["repair_branch_taken"] is False
         and all(d4_rep[k] == d4_frozen[k] for k in ("objective", "objective_scaled", "exit",
                                                     "n_iter", "optimal", "path")))

    with contextlib.redirect_stderr(io.StringIO()):
        d6_rep = rep(d6r_log, "U5")
    unit("U5 MUST-NOT-FLAG: the REPAIRED reader on D6R's real log recovers objective %r from "
         "major %s with provenance ITERATION_TABLE_ROW, summary_line_present False, optimal "
         "False, n_iter %s and %s printed significant figures -- NOT the summary's 17"
         % (d6_rep["objective_row_text"], d6_rep["objective_row_major"], d6_rep["n_iter"],
            d6_rep["objective_printed_significant_digits"]),
         d6_rep["objective_provenance"] == "ITERATION_TABLE_ROW"
         and d6_rep["objective_row_text"] == D6R_FINAL_OBJ_TEXT
         and d6_rep["objective_row_major"] == D6R_FINAL_MAJOR
         and d6_rep["summary_line_present"] is False and d6_rep["optimal"] is False
         and d6_rep["n_iter"] == D6R_FINAL_MAJOR
         and d6_rep["objective_printed_significant_digits"] == 8)

    raw = [l for l in open(d6r_log, errors="replace").read().splitlines()
           if _major_of(l, mod.MAJOR_ROW_RE) == D6R_FINAL_MAJOR]
    unit("U6 THE READER READS THE FILE, NOT A CONSTANT: an INDEPENDENT path -- scanning the "
         "preserved log's own lines for major %d -- yields the same objective token %r"
         % (D6R_FINAL_MAJOR, D6R_FINAL_OBJ_TEXT),
         len(raw) == 1 and D6R_FINAL_OBJ_TEXT in raw[0]
         and abs(float(D6R_FINAL_OBJ_TEXT) - d6_rep["objective"]) == 0.0)

    ctrl_dir = os.path.join(work, "planted_control")
    with contextlib.redirect_stderr(io.StringIO()):
        ctrl = mod.planted_zero_control(d4_log, ctrl_dir, reader=rep)
    unit("U7 THE REPAIRED READER PASSES THE FROZEN PLANTED-ZERO CONTROL on D4's reference: a "
         "planted %.3e is SEEN (delta %.3e) and the unperturbed negative control does not move "
         "(delta %.1e).  Note the FROZEN grader never drove this control on D6R's data -- "
         "`g_price` short-circuits when F_mp did not run -- so rule 3 is driven HERE"
         % (mod.PLANT, ctrl["seen_delta"], ctrl["negative_control_delta"]),
         ctrl["pass"] is True and abs(ctrl["seen_delta"] - mod.PLANT) < 1e-12
         and ctrl["negative_control_delta"] == 0.0)

    mod.read_ipopt = rep                 # the real rebind, so U8 measures the real thing
    unit("U8 THE FROZEN `planted_zero_control`'s DEFAULT reader is NOT changed by the rebind -- "
         "it is bound in `__defaults__` at def time, so D4's reference control still travels the "
         "ORIGINAL frozen code AFTER `read_ipopt` has been rebound.  Registered, and measured "
         "rather than assumed",
         mod.read_ipopt is rep and mod.planted_zero_control.__defaults__ is not None
         and any(f is _ORIGINALS[0] for f in mod.planted_zero_control.__defaults__)
         and not any(f is rep for f in mod.planted_zero_control.__defaults__))

    # ---- GRADER LEVEL: the ten plants, every one on the REAL frozen grader --------------
    bench = Bench(work)

    b = regrade(bench, plant_no_table(mod), "MUST-FLAG no table")
    unit("U9 BIRTH must-FLAG: EVERY major row removed, tail intact -> still REFUSED on "
         "`repair_declined_no_iteration_table`.  There is no objective in that file and the "
         "reader does not produce one (clause %r)" % refusal_clause(b),
         _refused_on(b, "repair_declined_no_iteration_table"))

    b = regrade(bench, plant_truncate_after_major(mod, 40), "MUST-FLAG truncated")
    unit("U10 BIRTH must-FLAG: the file TRUNCATED after major 40 the way a torn write cuts it "
         "-- table stops, whole tail gone -> REFUSED on `repair_declined_no_exit_line`.  An "
         "absent record is not a recognised non-finite exit (clause %r)" % refusal_clause(b),
         _refused_on(b, "repair_declined_no_exit_line"))

    b = regrade(bench, plant_torn_table(mod, 67), "MUST-FLAG torn table")
    unit("U11 BIRTH must-FLAG, THE DANGEROUS SHAPE: majors 68-73 deleted but the tail STILL "
         "reports 73 iterations -> REFUSED on `repair_declined_iteration_table_torn`.  A reader "
         "that trusted the last readable row would have published major 67's intermediate "
         "objective as the endpoint (clause %r)" % refusal_clause(b),
         _refused_on(b, "repair_declined_iteration_table_torn"))

    b = regrade(bench, plant_last_objective(mod, "nan"), "MUST-FLAG nan")
    unit("U12 BIRTH must-FLAG: the last objective rewritten to `nan` -> REFUSED, never coerced. "
         "HONEST CLAUSE NAMING: the FROZEN `MAJOR_ROW_RE` objective class `[-+0-9.eE]+` CANNOT "
         "EXPRESS `nan`, so the row stops matching and the refusal lands on the TORN clause, not "
         "on the non-finite one.  The requirement holds; the clause is named, not assumed "
         "(clause %r)" % refusal_clause(b),
         _refused_on(b, "repair_declined_iteration_table_torn"))

    b = regrade(bench, plant_last_objective(mod, "1e999"), "MUST-FLAG inf")
    unit("U13 BIRTH must-FLAG, THE LIMB THAT PROVES NO SILENT COERCION: the last objective "
         "rewritten to `1e999` -- expressible in the frozen regex's own class, floats to inf -> "
         "REFUSED on `repair_declined_recovered_objective_not_finite`.  The failure under repair "
         "IS a non-finite evaluation, so returning one would be exactly the laundering this "
         "reader exists to prevent (clause %r)" % refusal_clause(b),
         _refused_on(b, "repair_declined_recovered_objective_not_finite"))

    b = regrade(bench, plant_scaling("gradient-based"), "MUST-FLAG scaling")
    unit("U14 BIRTH must-FLAG: `nlp_scaling_method` flipped none -> gradient-based -> REFUSED on "
         "`repair_declined_nlp_scaling_method`.  With scaling on, the table's single column is "
         "the SCALED objective and the unscaled number the frozen reader returns IS NOT IN THE "
         "FILE (clause %r)" % refusal_clause(b),
         _refused_on(b, "repair_declined_nlp_scaling_method"))

    b = regrade(bench, plant_exit_line(mod, "EXIT: Restoration Failed."), "MUST-FLAG other exit")
    unit("U15 BIRTH must-FLAG: the EXIT line replaced with an UNREGISTERED non-optimal exit -> "
         "REFUSED on `repair_declined_exit_not_registered`.  The repair covers exactly the "
         "registered Eval_Error exit; widening it is a registration change, not a reader change "
         "(clause %r)" % refusal_clause(b),
         _refused_on(b, "repair_declined_exit_not_registered"))

    b = regrade(bench, plant_drop_exit_line(mod), "MUST-FLAG no exit")
    unit("U16 BIRTH must-FLAG: the EXIT line surgically deleted with the table intact -> REFUSED "
         "on `repair_declined_no_exit_line` (the same clause U10 reaches by truncation, from a "
         "different shape) (clause %r)" % refusal_clause(b),
         _refused_on(b, "repair_declined_no_exit_line"))

    b = regrade(bench, plant_drop_nit_line(mod), "MUST-FLAG no nit")
    unit("U17 BIRTH must-FLAG: `Number of Iterations` deleted -> REFUSED on "
         "`repair_declined_number_of_iterations_absent`.  Without the tail's own count there is "
         "nothing to corroborate the table against, so a truncated table cannot be distinguished "
         "from a complete one (clause %r)" % refusal_clause(b),
         _refused_on(b, "repair_declined_number_of_iterations_absent"))

    b = regrade(bench, plant_hole(mod, 30, 35), "MUST-FLAG hole")
    unit("U18 BIRTH must-FLAG: a HOLE punched at majors 30-35 with both ends intact -> REFUSED on "
         "`repair_declined_iteration_table_not_contiguous`.  A last row that agrees with the tail "
         "is not by itself proof the table is whole (clause %r)" % refusal_clause(b),
         _refused_on(b, "repair_declined_iteration_table_not_contiguous"))

    # ---- GRADER LEVEL: the production regrade ------------------------------------------
    p = regrade(bench, None, "production")
    g = p.get("grade") or {}
    gopt = g.get("G-D6R-OPT", {})
    g10 = g.get("G10", {})
    om = (g10.get("per_arm") or {}).get("O_mp", {})
    preds = g.get("predictions", {})
    unit("U19 MUST-NOT-FLAG, THE WHOLE POINT: the unplanted copy runs the FROZEN `grade()` to a "
         "verdict and the original `G-D6R-OPT no_final_objective_or_exit` REFUSAL IS GONE -- the "
         "frozen instrument produced ELEVEN gate readings where it previously produced none",
         p["refusal"] is None and p["verdict"] in VOCAB and len(g.get("gates") or {}) == 11)
    unit("U20 REBIND AUDIT: exactly %r rebound and nothing else.  Every band, threshold, cap, "
         "label, composition rule and prediction that decides the verdict is the frozen code"
         % (list(REBIND_REGISTERED),), p["names_rebound"] == list(REBIND_REGISTERED))
    unit("U21 CARRIED FORWARD 1 -- G-D6R-OPT is UNCLASSIFIED, not STALLED: S1 TRUE (%s cutbacks "
         "over %s majors = %.4f/major against a registered 1.0) but S2 FALSE (dual infeasibility "
         "FELL %.2e at major %s -> %.2e at %s).  The registered ladder needs BOTH"
         % (gopt.get("cutbacks"), gopt.get("n_major"), gopt.get("cutbacks_per_major") or -1,
            gopt.get("inf_du_at_tail_start") or -1, gopt.get("tail_start_major"),
            gopt.get("inf_du_last") or -1, gopt.get("n_major")),
         gopt.get("outcome") == "UNCLASSIFIED" and gopt.get("S1_line_search_failing") is True
         and gopt.get("S2_dual_infeasibility_not_decreasing") is False
         and gopt.get("cutbacks") == CARRIED_S1_CUTBACKS and gopt.get("n_major") == D6R_FINAL_MAJOR)
    unit("U22 CARRIED FORWARD 2 -- P1 scores MISS on POINT and BAND (registered set "
         "{ITERATION_CAP, STALLED}, point STALLED; observed UNCLASSIFIED) and P8 (`the chain "
         "COMPLETES -- all four arms run`) is a clean MISS.  Both are the FROZEN scorer's own",
         preds.get("P1", {}).get("score") == "MISS" and preds.get("P8", {}).get("score") == "MISS")
    unit("U23 CARRIED FORWARD 3 -- G10 GATE FAIL, and the failing limb is O_mp's FRAME GAP: host "
         "%s s minus container %s s = %s s against an allowance of FRAME_ALLOWANCE_S 90 minus "
         "KILL_GRACE_S 60 = %d s.  The arm was INSIDE its cap at %.3f of 2900.0 core-min; the "
         "frame allowance is under-registered for a 12.7 MB log"
         % (om.get("host_wall_s"), om.get("container_wall_s"), om.get("frame_gap_s"),
            CARRIED_G10_ALLOWANCE_S, om.get("core_min") or -1),
         g10.get("verdict") == "GATE FAIL" and om.get("frame_gap_s") == CARRIED_G10_FRAME_GAP_S
         and om.get("frame_gap_within_allowance") is False and om.get("within_cap") is True)
    unit("U24 THE REPAIR DID NOT LAUNDER A REFUSAL INTO A PASS: the item verdict is %r, and it "
         "is neither PASS nor GATE REACHED" % p["verdict"],
         p["verdict"] == "NOT A RESULT" and p["verdict"] not in ("PASS", "GATE REACHED"))
    unit("U25 every one of the %d gate values the frozen composer returned is in the fixed "
         "vocabulary" % len(g.get("gates") or {}),
         bool(g.get("gates")) and all(v in VOCAB for v in (g.get("gates") or {}).values()))

    planted = sum(1 for x in ast.walk(ast.parse("x = 1\nassert x == 1\n")) if isinstance(x, ast.Assert))
    own = [count_asserts(os.path.abspath(__file__)), count_asserts(os.path.join(HERE, "d6rg_reader.py"))]
    unit("U26 L-332: both successor files carry ZERO `assert` statements (%s), and the counter is "
         "shown able to see a planted one (%d) -- so `python3 -O` cannot strip a check" % (own, planted),
         own == [0, 0] and planted == 1)

    return n, fails, lines, p


# ================= main =================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--evidence", default=None)
    a = ap.parse_args()
    for p in (os.path.abspath(__file__), os.path.join(HERE, "d6rg_reader.py")):
        if count_asserts(p) != 0:
            sys.stdout.write("REFUSAL: %s carries an assert statement (L-332)\n" % p)
            return 2
    os.makedirs(a.workdir, exist_ok=True)
    t0 = time.time()
    before = {r: manifest(r) for r in (PRESERVED_D6R, PRESERVED_D4_O)}
    try:
        n, fails, lines, prod = selftest(a.workdir)
    except Refusal as ex:
        sys.stdout.write("D6RG SUCCESSOR REFUSED %s\n" % ex)
        return 2
    after = {r: manifest(r) for r in (PRESERVED_D6R, PRESERVED_D4_O)}
    moved = {r: sorted(k for k in set(before[r]) | set(after[r]) if before[r].get(k) != after[r].get(k))
             for r in before}
    identical = all(not v for v in moved.values())
    n += 1
    lines.append("  [%s] U27 PRESERVED ROOTS BYTE-IDENTICAL after the whole execution: %d files "
                 "under the D6R root and %d under D4's O/, md5 manifest before == after.  READ "
                 "FROM THE DISK, not from git -- a run root is not in git"
                 % ("OK " if identical else "BAD", len(before[PRESERVED_D6R]), len(before[PRESERVED_D4_O])))
    if not identical:
        fails.append("U27")
    wall = time.time() - t0
    body = "\n".join(lines)
    tail = ("D6RG SELFTEST units=%d expected=%d failures=%d python_O=%s wall_s=%.1f core_min=%.3f\n"
            % (n, EXPECTED_UNITS, len(fails), not __debug__, wall, wall / 60.0))
    if n != EXPECTED_UNITS or fails:
        tail += "SELFTEST FAIL: %s\n" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS))
    else:
        tail += "D6RG SELFTEST PASS %d/%d (counted against the frozen EXPECTED_UNITS)\n" % (n, EXPECTED_UNITS)
    sys.stdout.write(body + "\n" + tail)
    if a.evidence:
        open(a.evidence, "a").write(body + "\n" + tail)
    if a.out:
        rec = {"item": "D6RG", "predecessor": "D6R", "verdict": prod["verdict"],
               "frozen": prod["frozen"], "names_rebound": prod["names_rebound"],
               "reader_audit": prod["reader_audit"], "grade": prod["grade"],
               "selftest": {"units": n, "expected": EXPECTED_UNITS, "failures": fails,
                            "python_O": not __debug__},
               "preserved_roots_identical": identical,
               "preserved_root_files": {r: len(before[r]) for r in before},
               "cost_core_min_this_execution": round(wall / 60.0, 3),
               "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        json.dump(rec, open(a.out, "w"), indent=1, sort_keys=True, default=str)
    if a.selftest:
        return 0 if (n == EXPECTED_UNITS and not fails) else 2
    return 0 if (n == EXPECTED_UNITS and not fails) else 2


if __name__ == "__main__":
    sys.exit(main())
