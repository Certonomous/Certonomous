#!/usr/bin/env python3
"""W3S ARM A (`GSCAN`) RECORD PRODUCER.  THE THING THAT FEEDS `w3s_grade.py`.

WHY THIS FILE EXISTS, IN ONE SENTENCE.
`w3s_grade.py` demands a manifest contract -- a per-row `leg` key, a per-row `W`, and a
per-leg `W_STEPS_<LEG>=` ledger line -- that NOTHING ON THIS BOX PRODUCES.  A gate fed by
nothing is worse than a missing gate, because it reports.  That is the defect that blocked
`A1WRT2`'s freeze: two HARD gates there read `MANIFEST.json`, whose only writer turned out
to be the selftest's own fixture builder.  This file is the producer, and `--producer-trace`
proves the binding MECHANICALLY -- by extracting the keys the frozen comparator actually
reads, out of the comparator's own AST, and refusing if any of them has no producer here.

WHAT IT IS NOT.  It runs no solver, starts no container and authorises no compute.  It
reads artefacts a stage left on disk and writes one manifest row; or it reads a manifest
back and asserts CLAUDE.md rule 4 over one leg; or it builds a SYNTHETIC fixture root in a
temporary directory so the producer/consumer binding can be driven end to end at zero cost.
Every fixture row carries `"fixture": true` and every fixture root carries a `FIXTURE`
marker file, so no fixture number can ever be mistaken for a measurement.

NOTHING IS RE-IMPLEMENTED THAT COULD BE CALLED OR READ.
  * The COMPLETION GATE is the frozen parent's own `g0_completion`, imported from
    `d12y_grade_w3.py` after its md5 is checked.  This launcher-side rule-4 assertion is
    therefore not a second opinion about completion -- it is the SAME gate, run earlier,
    so a launcher and its comparator cannot disagree about what a completed stage is.
  * The FATAL/SIGNAL token list and its single benign exclusion are LOADED OUT OF
    `d12y_w3_stage_and_run.sh` (md5-pinned) at runtime, not copied.  They live inside a
    shell heredoc there and cannot be imported, so they are extracted as source text and
    `ast.literal_eval`-ed.  A copy drifts; a read cannot.
  * The LEDGER and MANIFEST line shapes are validated against the CONSUMERS' OWN COMPILED
    REGEXES -- `w3s_grade.SPEND_LINE_RE`, `w3s_grade.CORE_MIN_RE`,
    `w3s_grade.CORE_MIN_VALUE_RE`, `w3s_grade._leg_ledger_re`, and
    `item_ceiling_guard._DECIMAL` -- never against a pattern typed here.

THE TWO LEG VOCABULARIES, WHICH ARE DIFFERENT AND ARE NAMED RATHER THAN CONFLATED.
  COST LEGS      SETUP, A0, A1, A2   -- what `LEG_CAP_CORE_MIN` prices and what the
                                        cumulative item-ceiling guard is asserted against.
  MANIFEST LEGS  A0, A1, A2          -- what `w3s_grade._w_from_record_gscan` enumerates.
The four setup stages run ONCE and are shared by all three windows.  They are filed under
manifest leg `A0` -- the leg whose window is the anchor -- because emitting them three
times would be three records of one execution, and filing them under a fifth leg name
would trip the comparator's N2 (unregistered leg).  Every row also carries `cost_leg`, so
the artefact states both vocabularies instead of leaving one in prose.

NO `assert` STATEMENT APPEARS IN THIS FILE.  `python3 -O` deletes assert statements, and a
guard that disappears under an optimisation flag is not a guard.  `--assert-audit` counts
them by AST -- whole file, and outside the selftest functions -- and both must be 0.

EVERY CONTROL PRINTS ITS OWN STATE.  `EXERCISED-PASS` / `EXERCISED-FAIL` / `NOT EXERCISED`,
and `NOT EXERCISED` is never counted as a pass and never inferred from the absence of a
failure (`DAFOAM_CHARTER.md` sec.18.5's proposed shape, adopted here voluntarily for this
instrument -- it is a proposal lab-wide and is NOT claimed as enacted law).

NOTHING HERE IS FILED, SENT, UPLOADED, REGISTERED, POSTED OR COMMENTED (CLAUDE.md rule 7).
SUBMISSIONS REMAIN PARKED.  The pre-registration this serves is UNFROZEN.
"""
import argparse
import ast
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

ITEM = "W3S"
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- pinned neighbours
PARENT_GRADER_NAME = "d12y_grade_w3.py"
PARENT_GRADER_MD5 = "3950d30fd09c9b56213a02f5e9864e20"
PARENT_LAUNCHER_NAME = "d12y_w3_stage_and_run.sh"
PARENT_LAUNCHER_MD5 = "8a92f3f84f72d6806a2e5c5df88d82ef"
GRADER_NAME = "w3s_grade.py"
GRADER_MD5 = "3a3ee623fa48cc1d81517638485f376b"
CEILING_GUARD_REL = os.path.join("..", "_common", "item_ceiling_guard.py")

# ---------------------------------------------------------------- registered legs
LEGS = (("A0", 2000), ("A1", 1400), ("A2", 2600))
LEG_NAMES = tuple(n for n, _ in LEGS)
LEG_W = dict(LEGS)

COST_LEGS = ("SETUP", "A0", "A1", "A2")
# The DECLARED stage graph.  DAFOAM_CHARTER sec.18.7 Requirement 4: an item reports BOTH
# its declared and its executed stage count, and a run whose executed count is below its
# declared count is never reported by a token that reads as success.
DECLARED_STAGES = {
    "SETUP": ("S0", "S1a", "S1b", "S2a"),
    "A0": ("S5",),
    "A1": ("S5",),
    "A2": ("S5",),
}
# cost leg -> the manifest leg its rows are filed under
MANIFEST_LEG_OF = {"SETUP": "A0", "A0": "A0", "A1": "A1", "A2": "A2"}
DECLARED_TOTAL = sum(len(v) for v in DECLARED_STAGES.values())      # 7

# AMENDED 2026-09-04 before first compute; see w3s_grade.py's note for the two arithmetic
# defects this repairs (a cap larger than its own timeout, and a window whose worst-case
# wall was OUTSIDE the bound).  These MIRROR w3s_grade.py and the launcher, and
# `cap_reachability` below is the check that stops the class recurring.
LEG_CAP_CORE_MIN = {"SETUP": 5.0, "A0": 100.0, "A1": 70.0, "A2": 115.0}
ITEM_CEILING_CORE_MIN = 290.0

MEMAVAIL_FLOOR_GIB = 14.0

FIXTURE_MARKER = "FIXTURE_NOT_A_MEASUREMENT"


class Refusal(Exception):
    pass


_CONTROL_LOG = []


def control(name, state, detail=""):
    """The only way a control reports.  `NOT EXERCISED` is a state, never a silence."""
    _CONTROL_LOG.append((name, state, detail))
    sys.stdout.write("EXERCISED-%-34s %-14s %s\n" % (name, state, detail))
    sys.stdout.flush()


def _md5(path):
    import hashlib
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _pinned(name, want, rel=None):
    """EXISTENCE FIRST AND SEPARATELY, THEN THE md5 (DAFOAM_CHARTER sec.18.3).  An
    md5-agreement control over a subset can read agreement on every pin it holds while a
    dependency the code executes is absent."""
    p = os.path.join(HERE, rel if rel else name)
    if not os.path.isfile(p):
        raise Refusal("PINNED DEPENDENCY ABSENT: %s is not on disk at %s. Existence is "
                      "asserted BEFORE any md5, because an md5 control cannot see a file "
                      "that is not there (DAFOAM_CHARTER sec.18.3)." % (name, p))
    if want is not None:
        got = _md5(p)
        if got != want:
            raise Refusal("PINNED DEPENDENCY DRIFTED: %s md5 %s, pinned %s. Refusing "
                          "rather than producing a record against an instrument that is "
                          "not the one this file was written against." % (name, got, want))
    return p


_MOD_CACHE = {}


def _load(name, want, rel=None, modname=None):
    p = _pinned(name, want, rel)
    key = modname or name
    if key in _MOD_CACHE:
        return _MOD_CACHE[key]
    import importlib.util
    spec = importlib.util.spec_from_file_location("_w3s_dep_" + key.replace(".", "_"), p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _MOD_CACHE[key] = mod
    return mod


def parent_grader():
    return _load(PARENT_GRADER_NAME, PARENT_GRADER_MD5, modname="parent")


def grader():
    return _load(GRADER_NAME, GRADER_MD5, modname="grader")


def ceiling_guard_mod():
    return _load("item_ceiling_guard.py", None, rel=CEILING_GUARD_REL, modname="ceiling")


# ==================================================================================
# THE FATAL-TOKEN SCAN, READ OUT OF THE PINNED PARENT LAUNCHER RATHER THAN COPIED
# ==================================================================================
def _extract_list_literal(text, varname):
    """Pull `varname = [ ... ]` out of shell-embedded python source and literal_eval it.
    Full-line `#` comments inside the list are dropped; nothing else is touched."""
    m = re.search(r"^\s*%s\s*=\s*\[" % re.escape(varname), text, re.M)
    if not m:
        raise Refusal("could not locate `%s = [` in the pinned parent launcher; its "
                      "fatal-token block moved and this reader will not guess at it"
                      % varname)
    start = text.index("[", m.start())
    depth = 0
    end = None
    for i in range(start, len(text)):
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise Refusal("unbalanced brackets while extracting `%s`" % varname)
    body = text[start:end]
    kept = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        kept.append(line)
    try:
        return ast.literal_eval("\n".join(kept))
    except (SyntaxError, ValueError) as exc:
        raise Refusal("could not literal_eval `%s` out of the parent launcher: %r"
                      % (varname, exc))


_SCAN_CACHE = {}


def fatal_scan_patterns():
    """(_FATAL, _BENIGN) READ from `d12y_w3_stage_and_run.sh` after its md5 is checked.

    They live inside a shell heredoc and cannot be imported, so they are extracted as
    source text.  This is deliberately NOT a copy: a copy of a nine-token list drifts
    silently, and this family has already paid for a fatal scan that matched OpenFOAM's
    own `trapFpe:` ENABLEMENT BANNER (W3-LAUNCHER-DEF-2)."""
    if "scan" in _SCAN_CACHE:
        return _SCAN_CACHE["scan"]
    p = _pinned(PARENT_LAUNCHER_NAME, PARENT_LAUNCHER_MD5)
    with open(p, errors="replace") as f:
        txt = f.read()
    fatal = _extract_list_literal(txt, "_FATAL")
    benign = _extract_list_literal(txt, "_BENIGN")
    if not fatal:
        raise Refusal("the parent launcher's _FATAL list extracted EMPTY -- an empty "
                      "fatal scan can never refuse and would launder a crash")
    _SCAN_CACHE["scan"] = (list(fatal), [tuple(b) for b in benign])
    return _SCAN_CACHE["scan"]


def scan_log_for_fatals(text):
    """Per line, with the per-line benign exclusion.  A banner on line 89 can NEVER
    suppress a crash on line 400.  Returns (hits_in__FATAL_order, benign_records)."""
    fatal, benign = fatal_scan_patterns()
    hitset = set()
    excluded = []
    for i, line in enumerate(text.splitlines(), 1):
        lh = [p for p in fatal if re.search(p, line)]
        if not lh:
            continue
        why = None
        for bp, bw in benign:
            if re.search(bp, line):
                why = bw
                break
        if why:
            excluded.append({"line": i, "tokens": lh, "why": why,
                             "text": line.strip()[:200]})
        else:
            hitset.update(lh)
    return [p for p in fatal if p in hitset], excluded


# ==================================================================================
# THE MANIFEST ROW.  ONE PRODUCER, AND EVERY FIELD READ OFF DISK.
# ==================================================================================
def read_stage_log(logpath):
    """rule-4's log-side limbs, plus the CD structural witness, read off disk."""
    out = {"end_line_present": False, "last_time": None, "time_line_count": 0,
           "execution_time_count": 0, "obj_from_log": None, "fatal_tokens": None,
           "fatal_benign_excluded": [], "n_cd_lines": 0, "n_cl_lines": 0,
           "n_cd_negative": None, "cd_min": None, "cd_max": None}
    if not (logpath and os.path.isfile(logpath)):
        # `fatal_tokens` stays None: NO LOG WAS READ.  The frozen gate distinguishes
        # None (scan NOT MEASURED) from [] (scan RAN, clean) and this producer will not
        # collapse the two.
        return out
    with open(logpath, errors="replace") as f:
        txt = f.read()
    out["end_line_present"] = bool(re.search(r"^End\b", txt, re.M))
    times = re.findall(r"^Time = ([0-9.eE+-]+)", txt, re.M)
    out["time_line_count"] = len(times)
    if times:
        try:
            out["last_time"] = float(times[-1])
        except ValueError:
            out["last_time"] = None
    out["execution_time_count"] = len(re.findall(r"ExecutionTime", txt))
    hits, excluded = scan_log_for_fatals(txt)
    out["fatal_tokens"] = hits
    out["fatal_benign_excluded"] = excluded
    # ANCHORED on `^CD:`.  The solver prints `average:` on BOTH the CD and the CL line,
    # so an unanchored reader takes CL's (d12y_w3_stage_and_run.sh:631-647, [D3]).
    cd_avgs = re.findall(r"^CD:\s*\S+\s+average:\s*(\S+)\s*$", txt, re.M)
    cl_avgs = re.findall(r"^CL:\s*\S+\s+average:\s*(\S+)\s*$", txt, re.M)
    out["n_cd_lines"] = len(cd_avgs)
    out["n_cl_lines"] = len(cl_avgs)
    if cd_avgs:
        try:
            out["obj_from_log"] = float(cd_avgs[-1])
        except ValueError:
            out["obj_from_log"] = None
    cd_vals = re.findall(r"^CD:\s*(\S+)\s+average:", txt, re.M)
    try:
        vals = [float(v) for v in cd_vals]
        out["n_cd_negative"] = sum(1 for v in vals if v < 0.0)
        out["cd_min"] = min(vals) if vals else None
        out["cd_max"] = max(vals) if vals else None
    except ValueError:
        out["n_cd_negative"] = None
    return out


def _endtime_dir(stage_dir, endtime):
    if endtime is None:
        return None
    for nm in (repr(endtime), "%g" % endtime, str(endtime)):
        p = os.path.join(stage_dir, nm)
        if os.path.isdir(p):
            return p
    return None


def age_guard(stage_dir, endtime, datum, sentinel, kind):
    """CLAUDE.md rule 4's AGE GUARD, and THE MTIME QUESTION ANSWERED IN THE CODE.

    THIS ITEM STAGES WITH `cp -a`, WHICH PRESERVES mtimes.  A copied file therefore
    carries the SOURCE's mtime and can pre-date -- or, from a tampered or restored
    source, post-date -- the launch.  A datum taken from a copied file is exactly what a
    preserved mtime defeats.

    SO THE DATUM IS NOT A COPIED FILE.  It is a DEDICATED RUN-ROOT SENTINEL created and
    touched LAST, after every copy and after every cold-start assertion, immediately
    before the container starts -- the form `a1wrt2_stage.py:587-596` measured to be safe.
    Two positive assertions come with it, and both are recorded in the row rather than
    assumed:
      (i)  NOTHING STAGED POST-DATES THE DATUM.  A staged file newer than the sentinel is
           the preserved-mtime hazard actually occurring, and it REFUSES.
      (ii) THE SENTINEL DID NOT MOVE.  Its mtime after the stage must equal the datum; a
           datum that shifted under the run cannot date it.
    """
    detail = {"age_guard_ok": None, "age_guard_detail": "",
              "age_datum": None, "age_sentinel": sentinel,
              "age_sentinel_unmoved": None, "age_staged_postdating": None}
    if datum is None:
        detail["age_guard_detail"] = "no age datum was recorded; the guard could not arm"
        detail["age_guard_ok"] = False
        return detail
    datum = int(datum)
    detail["age_datum"] = datum
    if sentinel and os.path.exists(sentinel):
        detail["age_sentinel_unmoved"] = (int(os.path.getmtime(sentinel)) == datum)
        if not detail["age_sentinel_unmoved"]:
            detail["age_guard_ok"] = False
            detail["age_guard_detail"] = (
                "THE AGE SENTINEL MOVED: %s now reads mtime %d against the recorded datum "
                "%d. A datum that shifted under the run cannot date the run."
                % (sentinel, int(os.path.getmtime(sentinel)), datum))
            return detail
    elif sentinel:
        detail["age_guard_ok"] = False
        detail["age_guard_detail"] = ("the age sentinel %s is GONE; the datum has no "
                                      "artefact behind it" % sentinel)
        return detail
    if kind == "mesh":
        pm = os.path.join(stage_dir, "constant", "polyMesh")
        if not os.path.isdir(pm):
            detail["age_guard_ok"] = False
            detail["age_guard_detail"] = "polyMesh absent, so the age guard has nothing to date"
            return detail
        names = sorted(os.listdir(pm))
        stale = [n for n in names
                 if int(os.path.getmtime(os.path.join(pm, n))) < datum]
        detail["age_guard_ok"] = (len(stale) == 0 and len(names) > 0)
        detail["age_guard_detail"] = (
            "all %d polyMesh files newer than the run-root sentinel datum %d"
            % (len(names), datum)) if detail["age_guard_ok"] else \
            ("STALE against the sentinel datum %d: %s" % (datum, ",".join(stale))
             if stale else "polyMesh present but empty")
        return detail
    d0 = _endtime_dir(stage_dir, endtime)
    if d0 is None:
        detail["age_guard_ok"] = False
        detail["age_guard_detail"] = "no endTime directory on disk"
        return detail
    fields = [os.path.join(d0, x) for x in sorted(os.listdir(d0))
              if os.path.isfile(os.path.join(d0, x))]
    if not fields:
        detail["age_guard_ok"] = False
        detail["age_guard_detail"] = "endTime dir present but holds no field files"
        return detail
    older = [os.path.basename(p) for p in fields if int(os.path.getmtime(p)) < datum]
    detail["age_guard_ok"] = (len(older) == 0)
    detail["age_guard_detail"] = (
        "all %d fields at endTime newer than the run-root sentinel datum %d "
        "(staging preserves mtimes; the datum is deliberately NOT a copied file)"
        % (len(fields), datum)) if not older else ("STALE: " + ",".join(sorted(older)))
    return detail


def staged_files_postdating(stage_dir, datum):
    """(i) above.  Returns the list of staged paths whose mtime POST-DATES the datum."""
    bad = []
    if not (stage_dir and os.path.isdir(stage_dir) and datum is not None):
        return bad
    datum = int(datum)
    for root, _dirs, files in os.walk(stage_dir):
        for fn in files:
            p = os.path.join(root, fn)
            try:
                if int(os.path.getmtime(p)) > datum:
                    bad.append(os.path.relpath(p, stage_dir))
            except OSError:
                bad.append(os.path.relpath(p, stage_dir) + " (unstattable)")
    return sorted(bad)


ROW_ORDER_NOTE = ("every key below is either read off disk or is a REGISTERED constant "
                  "this producer was invoked with; none is echoed back from the shell's "
                  "own intent")


def build_row(stage, cost_leg, task, stage_kind, expected_steps, rc, wall_s, core_min,
              memavail_gib, endtime, stage_dir, logpath, age_datum, age_sentinel,
              docker_inspect, dv_index, dv_delta, dv_units, coldstart_ok,
              field_b_md5_ok=True, fixture=False):
    """THE ONE PRODUCER OF A W3S MANIFEST ROW."""
    if cost_leg not in COST_LEGS:
        raise Refusal("unregistered cost leg %r; the registered cost legs are %s"
                      % (cost_leg, list(COST_LEGS)))
    mleg = MANIFEST_LEG_OF[cost_leg]
    row = {
        "name": stage,
        "leg": mleg,                       # W3S-A1: the manifest leg -- w3s_grade N1/N2
        "cost_leg": cost_leg,              # the OTHER vocabulary, stated not implied
        "W": int(LEG_W[mleg]),             # W3-A2 / W3S-A1 N3: the window that ran
        "task": task,
        "stage_kind": stage_kind,
        "rc": int(rc),
        "wall_s": int(wall_s),
        "core_min": float(core_min),
        "memavail_GiB": float(memavail_gib),
        "expected_steps": (int(expected_steps) if expected_steps not in (None, "", "None")
                           else None),
        "endTime": (float(endtime) if endtime not in (None, "", "None") else None),
        "registered_dvIndex": int(dv_index),
        "registered_dvDelta": float(dv_delta),
        "dv_units": dv_units,
        "coldstart_ok": bool(coldstart_ok),
        "field_b_md5_ok": bool(field_b_md5_ok),
    }
    if fixture:
        row["fixture"] = True
    ec, _, oom = str(docker_inspect).partition("|")
    row["docker_exit"] = ec
    row["oomkilled"] = oom if oom else "false"

    # ---- the stage's own JSON, read off disk (never echoed from the caller) --------
    jf = os.path.join(stage_dir, "d12y_%s.json" % stage) if stage_dir else None
    if jf and os.path.isfile(jf):
        with open(jf) as f:
            j = json.load(f)
        row["status"] = j.get("status")
        row["obj"] = j.get("obj")
        row["nShapes"] = j.get("nShapes")
        row["dobj_dshape"] = j.get("dobj_dshape")
        row["maxrss_GiB_after_primal"] = j.get("maxrss_GiB_after_primal")
        row["maxrss_GiB_after_adjoint"] = j.get("maxrss_GiB_after_adjoint")
        sv = j.get("shape")
        row["applied_shape_vector"] = sv
        if isinstance(sv, list):
            nz = [(i, v) for i, v in enumerate(sv) if v != 0.0]
            if len(nz) == 0:
                row["applied_index"] = None
                row["applied_sign"] = "zero"
                row["applied_magnitude"] = 0.0
            elif len(nz) == 1:
                i, v = nz[0]
                row["applied_index"] = i
                row["applied_sign"] = "plus" if v > 0 else "minus"
                row["applied_magnitude"] = abs(v)
            else:
                row["applied_index"] = [i for i, _ in nz]
                row["applied_sign"] = "multiple"
                row["applied_magnitude"] = None
        row["applied_dvIndex_reported"] = j.get("dvIndex")
        row["applied_dvDelta_reported"] = j.get("dvDelta")
    else:
        row["status"] = None

    row.update(read_stage_log(logpath))

    if stage_kind == "mesh":
        pm = os.path.join(stage_dir, "constant", "polyMesh") if stage_dir else None
        present, ncells = [], None
        if pm and os.path.isdir(pm):
            for fn in os.listdir(pm):
                present.append(re.sub(r"\.gz$", "", fn))
            for cand in ("owner", "owner.gz"):
                fp = os.path.join(pm, cand)
                if os.path.isfile(fp):
                    try:
                        import gzip
                        op = gzip.open if cand.endswith(".gz") else open
                        with op(fp, "rt", errors="replace") as f:
                            head = f.read(4096)
                        m = re.search(r"nCells:\s*(\d+)", head)
                        if m:
                            ncells = int(m.group(1))
                    except (OSError, ValueError, EOFError) as exc:
                        row["mesh_n_cells_detail"] = "could not read %s: %r" % (cand, exc)
                    break
        row["mesh_polymesh_files"] = sorted(set(present))
        row["mesh_n_cells"] = ncells
        logtxt = ""
        if logpath and os.path.isfile(logpath):
            with open(logpath, errors="replace") as f:
                logtxt = f.read()
        row["mesh_check_ok"] = (("Mesh OK." in logtxt)
                                and not re.search(r"Failed\s+\d+\s+mesh checks", logtxt))
        # A mesh stage has NO time.  None rather than 0.0, so no reader can mistake an
        # absent quantity for a measured zero.
        row["last_time"] = None
        row["endTime"] = None
        row["expected_steps"] = None

    row.update(age_guard(stage_dir, row.get("endTime"), age_datum, age_sentinel,
                         stage_kind))
    row["age_staged_postdating"] = staged_files_postdating(stage_dir, age_datum)
    return row


def append_row(manifest, row):
    with open(manifest, "a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    return row


def blocked_row(stage, cost_leg, blocked_by, memavail_gib):
    """A GUARD THAT REFUSES MUST LEAVE THE SAME TRACE IN BOTH ARTIFACTS (W2R-DEF-1).
    The comparator FILTERS blocked rows out of the graded set, so a blocked leg cannot
    become a partial result -- it refuses at N4 instead, which is the correct outcome for
    an arm whose whole question is a three-point comparison."""
    mleg = MANIFEST_LEG_OF[cost_leg]
    return {"name": stage, "leg": mleg, "cost_leg": cost_leg, "W": int(LEG_W[mleg]),
            "blocked": True, "blocked_by": blocked_by,
            "memavail_GiB": float(memavail_gib)}


# ==================================================================================
# LEDGER LINE PRODUCERS, VALIDATED AGAINST THE CONSUMERS' OWN REGEXES
# ==================================================================================
def w_steps_line(manifest_leg, deltat):
    if manifest_leg not in LEG_NAMES:
        raise Refusal("W_STEPS_ line requested for unregistered manifest leg %r"
                      % manifest_leg)
    line = "W_STEPS_%s=%d deltaT=%s" % (manifest_leg, LEG_W[manifest_leg], deltat)
    g = grader()
    if not g._leg_ledger_re(manifest_leg).match(line):
        raise Refusal("the producer emitted a W_STEPS line the CONSUMER'S OWN regex does "
                      "not match: %r" % line)
    return line


def leg_spend_line(cost_leg, rc, wall_s, core_min, declared, executed, blocked):
    """The item's ONLY spend row shape.  Two independent consumers read it and BOTH are
    checked here, with THEIR regexes:
      w3s_grade.spend_from_root  -- `^(?:STAGE|ARM|LEG)=` + `\\bcore_min=` validated WHOLE
      item_ceiling_guard         -- `--row-prefix LEG=` + `(?:^|\\s)core_min=(\\S+)`
    Exactly one such row per cost leg, so no reader can double-count.  Per-stage detail
    goes on `SDETAIL=` lines carrying `stage_core_min=`, which BOTH readers are blind to
    BY CONSTRUCTION -- and the selftest drives that blindness rather than asserting it."""
    line = ("LEG=%s rc=%d wall_s=%d ranks=1 core_min=%s declared=%d executed=%d "
            "blocked=%d" % (cost_leg, int(rc), int(wall_s), repr(float(core_min)),
                            int(declared), int(executed), int(blocked)))
    g = grader()
    if not g.SPEND_LINE_RE.match(line):
        raise Refusal("the producer emitted a spend row w3s_grade.SPEND_LINE_RE does not "
                      "match: %r" % line)
    m = g.CORE_MIN_RE.search(line)
    if not m or not g.CORE_MIN_VALUE_RE.match(m.group(1)):
        raise Refusal("the producer emitted a core_min token w3s_grade would call "
                      "UNMEASURED: %r" % line)
    c = ceiling_guard_mod()
    m2 = re.compile(r"(?:^|\s)core_min=(\S+)").search(line)
    if not m2 or c.parse_decimal(m2.group(1)) is None:
        raise Refusal("the producer emitted a core_min token item_ceiling_guard would "
                      "call UNMEASURED: %r" % line)
    return line


def stage_detail_line(stage, cost_leg, rc, wall_s, core_min, memavail_gib, logname):
    """Per-stage detail.  DELIBERATELY NOT SPEND-SHAPED: `SDETAIL=` is not one of
    `STAGE|ARM|LEG` and `stage_core_min=` carries no word boundary before `core_min`, so
    neither spend reader can see it.  The alternative -- a `STAGE=` row carrying
    `core_min=` beside a `LEG=` row carrying the leg total -- would be DOUBLE-COUNTED by
    `w3s_grade.spend_from_root`, which sums every `^(STAGE|ARM|LEG)=` line it finds."""
    line = ("SDETAIL=%s cost_leg=%s rc=%d wall_s=%d ranks=1 stage_core_min=%s "
            "memavail_GiB=%s log=%s" % (stage, cost_leg, int(rc), int(wall_s),
                                        repr(float(core_min)), memavail_gib, logname))
    g = grader()
    if g.SPEND_LINE_RE.match(line):
        raise Refusal("a stage-detail line matched the SPEND row regex and would be "
                      "DOUBLE-COUNTED against the leg row: %r" % line)
    if g.CORE_MIN_RE.search(line):
        raise Refusal("a stage-detail line carries a bare `core_min=` token: %r" % line)
    return line


# ==================================================================================
# CAP REACHABILITY -- A REGISTERED CAP THAT EXCEEDS ITS OWN TIMEOUT REFUSES TO FREEZE
# ==================================================================================
# THE RULE, in the supervisor's own words: `cap x 60 / ranks < wall_bound` FOR EVERY LEG.
#
# WHY IT IS A CHECK AND NOT A NOTE.  A cap larger than the timeout that guards the same
# work CAN NEVER BIND -- the timeout fires first, always -- so it is a registered number no
# execution path can reach.  W3S's own A2 leg was registered at 155.0 core-min = 9300 s
# against a 7200 s stage wall bound: 29.2 % larger than anything reachable.  This family
# has now found the same DEAD-LEVER class in `SO3aF2`'s CEILING, in `W_CONTINGENCY = 900`
# and in eleven more.  Documenting that this item did it stops nothing; a check that
# refuses the freeze stops the next one.
#
# `ranks` is carried per leg rather than assumed, because the conversion from core-minutes
# to wall seconds is the whole content of the rule and it is wrong at any other rank count.
LEG_RANKS = {"SETUP": 1, "A0": 1, "A1": 1, "A2": 1}
# The wall bound available to a leg is the SUM of its declared stages' registered bounds.
STAGE_WALL_BOUND_S = {"S0": 900, "S1a": 7200, "S1b": 7200, "S2a": 7200, "S5": 7200}


def cap_reachability():
    """Returns (rc, body).  rc=0 only when EVERY registered cap is reachable.
    rc=64 names every dead lever it found."""
    rows = []
    dead = []
    for leg in COST_LEGS:
        cap = LEG_CAP_CORE_MIN[leg]
        ranks = LEG_RANKS[leg]
        cap_s = cap * 60.0 / float(ranks)
        bound = sum(STAGE_WALL_BOUND_S[s] for s in DECLARED_STAGES[leg])
        ok = cap_s < bound
        row = {"leg": leg, "cap_core_min": cap, "ranks": ranks,
               "cap_wall_s": cap_s, "leg_wall_bound_s": bound,
               "declared_stages": list(DECLARED_STAGES[leg]),
               "reachable": ok,
               "headroom_pct": 100.0 * (bound / cap_s - 1.0) if cap_s > 0 else None}
        rows.append(row)
        if not ok:
            dead.append(row)
    total = sum(LEG_CAP_CORE_MIN.values())
    sums_exactly = abs(total - ITEM_CEILING_CORE_MIN) < 1e-9
    body = {"rule": "cap x 60 / ranks < wall_bound, for every leg",
            "legs": rows, "caps_sum_core_min": total,
            "item_ceiling_core_min": ITEM_CEILING_CORE_MIN,
            "caps_sum_equals_ceiling": sums_exactly,
            "dead_levers": dead}
    if dead:
        body["verdict"] = "BLOCKED"
        body["reason"] = (
            "DEAD LEVER: %s. A cap that exceeds its own timeout can never bind -- the "
            "timeout binds first, always -- so it is a registered number no execution path "
            "can reach. THE ITEM DOES NOT FREEZE."
            % "; ".join("leg %s caps at %.1f core-min = %.0f s against a %d s wall bound"
                        % (d["leg"], d["cap_core_min"], d["cap_wall_s"],
                           d["leg_wall_bound_s"]) for d in dead))
        return 64, body
    if not sums_exactly:
        body["verdict"] = "BLOCKED"
        body["reason"] = ("REGISTRATION INCONSISTENT: the caps sum to %.3f, the registered "
                          "ceiling is %.3f. A registration whose parts do not equal its "
                          "whole is a defect found here or not at all."
                          % (total, ITEM_CEILING_CORE_MIN))
        return 64, body
    body["verdict"] = "PASS"
    body["reason"] = ("every registered cap is reachable inside its own wall bound, and "
                      "the %d caps sum to %.1f == the registered ceiling"
                      % (len(rows), total))
    return 0, body


# ==================================================================================
# THE IN-LEG BUDGET, AND THE ONE THING THAT MAKES A CAP EXECUTABLE
# ==================================================================================
SDETAIL_RE = re.compile(r"^SDETAIL=(\S+)\s+cost_leg=(\S+)\b")
STAGE_CORE_MIN_RE = re.compile(r"\bstage_core_min=(\S+)")


def leg_spent_from_disk(root, cost_leg):
    """Sum THIS leg's stage detail rows, RE-READ FROM DISK on every call.

    A1ZE fired twice, 6 min 25 s apart, and fire 2 started its accumulator at zero --
    blind to fire 1's 0.7 core-min.  A process-local total is a statement about one
    invocation, not about the leg.  Returns (core_min, note); core_min is None meaning
    UNMEASURED and NEVER 0.0 for a read or parse failure."""
    led = os.path.join(root, "ledger.txt")
    if not os.path.isfile(led):
        if os.path.isdir(root) and any(p.endswith(".log") for p in os.listdir(root)):
            return None, ("UNMEASURED: %s carries stage logs and no ledger" % root)
        return 0.0, "FRESH: no ledger yet, no stage has run"
    c = ceiling_guard_mod()
    tot = 0.0
    n = 0
    try:
        with open(led, errors="replace") as f:
            for line in f:
                m = SDETAIL_RE.match(line.strip())
                if not m or m.group(2) != cost_leg:
                    continue
                v = STAGE_CORE_MIN_RE.search(line)
                if not v:
                    return None, "UNMEASURED: a SDETAIL row for %s carries no " \
                                 "stage_core_min=" % cost_leg
                # the SAME whole-token validator the ceiling guard uses on its own field
                parsed = c.parse_decimal(v.group(1))
                if parsed is None:
                    return None, ("UNMEASURED: stage_core_min=%r is not a finite "
                                  "non-negative decimal" % v.group(1))
                tot += parsed
                n += 1
    except OSError:
        return None, "UNMEASURED: the ledger could not be read"
    return tot, "MEASURED from %d SDETAIL row(s)" % n


def stage_timeout(root, cost_leg, bound_s):
    """THE REGISTERED LEG CAP, TURNED INTO A PROCESS THAT CAN EXECUTE IT.

    The cumulative item-ceiling guard is PROSPECTIVE -- it refuses BEFORE a leg and can
    see nothing that happens inside one.  DAFOAM_CHARTER sec.13's 2026-08-22 PROPOSAL is
    exactly this shape one layer out: A3 rung 2 registered an 8 GiB floor and armed a
    RECORD-ONLY watcher, with nothing connecting them, and the floor was breached for
    52.6 %% of the graded arm with no stop firing.  So this leg's remaining budget is
    converted into the ONE quantity the operating system will enforce for free: the
    stage's `timeout` in seconds.

    Returns (seconds, note) or (None, why).  The caller validates the token WHOLE before
    it reaches any command line; no number returned here ever enters a shell arithmetic
    context (`item_ceiling_guard.py` defect (3))."""
    if cost_leg not in LEG_CAP_CORE_MIN:
        return None, "unregistered cost leg %r" % cost_leg
    spent, note = leg_spent_from_disk(root, cost_leg)
    if spent is None:
        return None, ("REFUSED: %s. An unknown in-leg spend cannot be shown to fit under "
                      "the %.1f core-min leg cap." % (note, LEG_CAP_CORE_MIN[cost_leg]))
    remaining = LEG_CAP_CORE_MIN[cost_leg] - spent
    if remaining <= 0.0:
        return None, ("REFUSED: leg %s has spent %.4f of its registered %.1f core-min "
                      "cap; there is no budget left for another stage. An overrun STOPS "
                      "the run; it does not get a new budget (CLAUDE.md rule 12)."
                      % (cost_leg, spent, LEG_CAP_CORE_MIN[cost_leg]))
    budget_s = int(math.floor(remaining * 60.0))
    if budget_s < 1:
        return None, ("REFUSED: leg %s has %.4f core-min left, under one second of wall "
                      "at ranks=1" % (cost_leg, remaining))
    chosen = min(int(bound_s), budget_s)
    return chosen, ("leg %s: spent %.4f of cap %.1f (%s), remaining %.4f core-min = %d s; "
                    "registered stage wall bound %d s; timeout = min(bound, budget) = %d s"
                    % (cost_leg, spent, LEG_CAP_CORE_MIN[cost_leg], note, remaining,
                       budget_s, int(bound_s), chosen))


# ==================================================================================
# THE PER-LEG RULE-4 ASSERTION.  THE FROZEN PARENT'S OWN GATE, RUN EARLY.
# ==================================================================================
def verify_leg(root, cost_leg):
    """Returns (rc, body).
      0  the leg's declared stages all ran and all pass the frozen completion gate
      6  DECLARED > EXECUTED -- a truncated program, NEVER a success-reading token
      2  a declared stage ran and FAILED the frozen rule-4 gate
      3  the manifest is unreadable or the leg is unregistered
    """
    if cost_leg not in DECLARED_STAGES:
        return 3, {"leg": cost_leg, "verdict": "BLOCKED",
                   "reason": "unregistered cost leg %r" % cost_leg}
    manifest = os.path.join(root, "manifest.jsonl")
    if not os.path.isfile(manifest):
        return 3, {"leg": cost_leg, "verdict": "BLOCKED",
                   "reason": "no manifest at %s" % manifest}
    rows = []
    with open(manifest) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    declared = list(DECLARED_STAGES[cost_leg])
    mine = [r for r in rows if r.get("cost_leg") == cost_leg]
    executed = [r for r in mine if not r.get("blocked")]
    blocked = [r for r in mine if r.get("blocked")]
    names_exec = [r.get("name") for r in executed]
    missing = [s for s in declared if s not in names_exec]
    body = {"leg": cost_leg, "declared_stages": declared,
            "declared_count": len(declared), "executed_count": len(executed),
            "blocked_count": len(blocked),
            "executed_stages": names_exec,
            "blocked_stages": [r.get("name") for r in blocked],
            "missing_stages": missing,
            "item_declared_total": DECLARED_TOTAL}
    # DAFOAM_CHARTER sec.18.7 Requirement 4: the shortfall is READ BY A GATE, not merely
    # recorded.  W3 recorded its 20 blocked stages perfectly in TWO artefacts and nothing
    # read them; the one gate that fired reached the right verdict by the wrong mechanism.
    if missing or len(executed) != len(declared):
        body["verdict"] = "NOT A RESULT"
        body["reason"] = (
            "TRUNCATED PROGRAM: leg %s DECLARED %d stage(s) %s and EXECUTED %d %s "
            "(%d blocked). A run whose executed count is below its declared count is "
            "never reported by a token that reads as success "
            "(DAFOAM_CHARTER sec.18.7 Requirement 4)."
            % (cost_leg, len(declared), declared, len(executed), names_exec,
               len(blocked)))
        return 6, body
    p = parent_grader()
    try:
        g0 = p.g0_completion(executed)
    except p.Refusal as exc:
        body["verdict"] = "NOT A RESULT"
        body["gate"] = "G12R-0 (the FROZEN parent's own completion gate, called not copied)"
        body["reason"] = "RULE 4 REFUSAL: %s" % exc
        return 2, body
    body["verdict"] = "PASS"
    body["gate"] = "G12R-0 (the FROZEN parent's own completion gate, called not copied)"
    body["g0"] = g0
    body["reason"] = ("all %d declared stage(s) executed and passed the frozen rule-4 "
                      "gate; %d infrastructure defect(s) reported beside it"
                      % (len(executed), g0.get("n_infrastructure_defects", 0)))
    return 0, body


# ==================================================================================
# THE PRODUCER TRACE.  EXTRACTED FROM THE CONSUMER'S AST, NOT TYPED HERE.
# ==================================================================================
# (function name -> extraction mode).
#   "both"     `.get('k')` AND `x['k']` are both row-key reads.
#   "get-only" ONLY `.get('k')` is a row-key read, because the function BUILDS AND INDEXES
#              ITS OWN output dict and those subscripts are not manifest keys.  This
#              narrowing is stated rather than silent: `plan_gscan` writes `out["gates"]`,
#              `out["arm_a_verdict"]` and so on, and counting those as consumed row keys
#              would manufacture findings against keys no row was ever meant to carry --
#              a checker that reports noise is a checker nobody reads.
CONSUMER_FUNCTIONS = {
    PARENT_GRADER_NAME: (("g0_completion", "both"),),
    GRADER_NAME: (("_w_from_record_gscan", "both"), ("read_g", "both"),
                  ("looks_like_gscan", "both"), ("ga_1_magnitudes", "both"),
                  ("plan_gscan", "get-only")),
}

# Keys the consumers read that are NOT manifest-row keys and are therefore excluded from
# the row census by NAME, each with the reason it is excluded.  Anything not on this list
# and not produced is a FINDING.
NON_ROW_KEYS = {
    "STAGE_KIND": "an environment variable in the parent launcher, not a manifest key",
    "DV_UNITS": "an environment variable in the parent launcher, not a manifest key",
}


def _keys_read_by(path, spec):
    """Every constant string key a function reads off a row: `x.get('k')`, `x.get('k',d)`
    and `x['k']`.  Statement-level and mechanical -- a list written from memory always has
    the failure mode DAFOAM_CHARTER sec.18.3 legislates against; an extraction cannot."""
    with open(path) as f:
        tree = ast.parse(f.read(), filename=path)
    modes = dict(spec)
    keys = {}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name in modes):
            continue
        mode = modes[node.name]
        for sub in ast.walk(node):
            if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute)
                    and sub.func.attr == "get" and sub.args
                    and isinstance(sub.args[0], ast.Constant)
                    and isinstance(sub.args[0].value, str)):
                keys.setdefault(sub.args[0].value, set()).add(node.name)
            if (mode == "both" and isinstance(sub, ast.Subscript)
                    and isinstance(sub.slice, ast.Constant)
                    and isinstance(sub.slice.value, str)):
                keys.setdefault(sub.slice.value, set()).add(node.name)
    return keys


def producer_trace(drop_key=None):
    """Returns (rc, body).  rc=0 only when EVERY key the frozen consumers read has a
    producer in the registered set.

    `drop_key` is the PLANTED CONTROL (CLAUDE.md rule 3 applied to the checker rather than
    to a comparator): a trace that reports zero findings must first be shown able to
    report a non-zero.  With a key removed from the produced set the trace MUST flag it.
    """
    p = parent_grader()
    g = grader()
    consumed = {}
    for fname, spec in CONSUMER_FUNCTIONS.items():
        want = PARENT_GRADER_MD5 if fname == PARENT_GRADER_NAME else GRADER_MD5
        path = _pinned(fname, want)
        for k, where in _keys_read_by(path, spec).items():
            consumed.setdefault(k, set()).update("%s::%s" % (fname, w) for w in where)
    # the frozen gate's own required-key tuples, READ from the parent, never typed
    for k in tuple(p.REQUIRED_ROW_KEYS) + tuple(p.REQUIRED_ROW_KEYS_MESH):
        consumed.setdefault(k, set()).add("%s::REQUIRED_ROW_KEYS" % PARENT_GRADER_NAME)

    # The produced set is the UNION over both row producers, because `blocked` is written
    # by `blocked_row` and never by `build_row` -- and a trace that only ever built clean
    # fixtures would report `blocked` as unproduced, which is the false-finding direction.
    produced = set()
    for kwargs in ({}, {"blocked_stage": ("S5", "A2")}):
        d = tempfile.mkdtemp(prefix="w3s_trace_")
        try:
            fx = build_fixture(d, fs0="hit", fs1="miss", **kwargs)
            with open(os.path.join(fx["root"], "manifest.jsonl")) as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        produced.update(json.loads(line).keys())
        finally:
            shutil.rmtree(d, ignore_errors=True)
    if drop_key is not None:
        produced.discard(drop_key)

    findings = []
    for k in sorted(consumed):
        if k in produced:
            continue
        if k in NON_ROW_KEYS:
            continue
        findings.append({"key": k, "read_by": sorted(consumed[k]),
                         "finding": "NO PRODUCER: no row this launcher writes carries it"})

    # ---- the LEDGER side of the contract, driven through the consumers' own regexes.
    ledger_checks = []
    for leg in LEG_NAMES:
        ln = w_steps_line(leg, "1e-2")
        ledger_checks.append({"line": ln, "consumer": "w3s_grade._leg_ledger_re(%r)" % leg,
                              "matched": True})
    sl = leg_spend_line("A0", 0, 4073, 67.8833, 1, 1, 0)
    ledger_checks.append({"line": sl,
                          "consumer": "w3s_grade.SPEND_LINE_RE + CORE_MIN_VALUE_RE and "
                                      "item_ceiling_guard.parse_decimal",
                          "matched": True})
    sd = stage_detail_line("S5", "A0", 0, 4073, 67.8833, 20.5, "S5_x.log")
    ledger_checks.append({"line": sd,
                          "consumer": "NEITHER spend reader -- checked blind by "
                                      "construction so the leg row is not double-counted",
                          "matched": False})

    body = {"item": ITEM,
            "consumed_keys": {k: sorted(v) for k, v in sorted(consumed.items())},
            "n_consumed_keys": len(consumed),
            "produced_keys": sorted(produced),
            "n_produced_keys": len(produced),
            "excluded_by_name": NON_ROW_KEYS,
            "ledger_line_checks": ledger_checks,
            "findings": findings,
            "n_findings": len(findings),
            "registered_producers": [
                "w3s_stage_record.py::build_row      -> every manifest row key",
                "w3s_stage_record.py::blocked_row    -> the blocked-row shape",
                "w3s_stage_record.py::w_steps_line   -> W_STEPS_<LEG>= per leg",
                "w3s_stage_record.py::leg_spend_line -> LEG=<leg> ... core_min= per leg",
                "w3s_stage_and_run.sh                -> calls all four, one leg per "
                "invocation",
            ]}
    body["verdict"] = "PASS" if not findings else "GATE FAIL"
    return (0 if not findings else 2), body


# ==================================================================================
# THE FIXTURE.  SYNTHETIC, LABELLED, AND NEVER WRITTEN INTO A REAL RUN ROOT.
# ==================================================================================
FIXTURE_G = {
    # FS-0 HIT reproduces the registered anchor exactly; MISS is +2 %, outside the
    # registered +/-1 % band.
    "hit": 0.48835975139977306,
    "miss": 0.48835975139977306 * 1.02,
}
# FS-1: the registration's own PREDICTED points miss the 2048.61 bar; the `hit` variant
# plants a |g(3000)| large enough to clear it, so the gate is driven in BOTH directions.
FIXTURE_G_A1 = {"miss": 0.713, "hit": 0.713}
FIXTURE_G_A2 = {"miss": 0.318, "hit": 0.80}   # 0.80*2600 = 2080 > the 2048.61 bar


def _write(path, text):
    with open(path, "w") as f:
        f.write(text)


def _fake_log(nsteps, endtime, cd=0.6377885661084924, mesh=False):
    if mesh:
        return ("FIXTURE -- synthetic checkMesh output, no solver ran\n"
                "Mesh OK.\nEnd\n")
    lines = ["FIXTURE -- synthetic solver log, no solver ran",
             "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE)."]
    dt = endtime / float(nsteps) if nsteps else 0.0
    for i in range(1, nsteps + 1):
        lines.append("Time = %s" % repr(round(i * dt, 10)))
        lines.append("CD: %r average: %r" % (cd, cd))
        lines.append("CL: %r average: %r" % (0.05, 0.03))
        lines.append("ExecutionTime = %.2f s  ClockTime = %d s" % (i * 0.1, i))
    lines.append("End")
    return "\n".join(lines) + "\n"


def _stage_dir_with_field(base, name, endtime, datum, mesh=False):
    d = os.path.join(base, name)
    os.makedirs(d, exist_ok=True)
    if mesh:
        pm = os.path.join(d, "constant", "polyMesh")
        os.makedirs(pm, exist_ok=True)
        _write(os.path.join(pm, "owner"), "nCells: 2450\n")
        for fn in ("points", "faces", "neighbour", "boundary"):
            _write(os.path.join(pm, fn), "FIXTURE\n")
        for fn in os.listdir(pm):
            os.utime(os.path.join(pm, fn), (datum + 5, datum + 5))
        return d
    td = os.path.join(d, repr(endtime))
    os.makedirs(td, exist_ok=True)
    for fn in ("U", "p", "nut", "nuTilda", "phi"):
        _write(os.path.join(td, fn), "FIXTURE\n")
        os.utime(os.path.join(td, fn), (datum + 5, datum + 5))
    return d


def build_fixture(basedir, fs0="hit", fs1="miss", omit_stage=None, mislabel_leg=False,
                  drop_ledger_leg=None, blocked_stage=None):
    """Build a SYNTHETIC three-leg Arm A run root.  NO SOLVER, NO CONTAINER, NO COMPUTE.

    Its only purpose is to drive the producer/consumer binding end to end.  The root
    carries a `FIXTURE_NOT_A_MEASUREMENT` marker, every row carries `"fixture": true`,
    and the gradient values are the registration's OWN PREDICTED points -- so nothing here
    can be mistaken for, or quoted as, a measurement.
    """
    root = os.path.join(basedir, "CURRICULUM-D12R2W3S-GSCAN-FIXTURE")
    os.makedirs(root, exist_ok=True)
    _write(os.path.join(root, FIXTURE_MARKER),
           "This tree was written by w3s_stage_record.py --fixture.\n"
           "NO SOLVER RAN.  NO CONTAINER STARTED.  NO NUMBER HERE IS A MEASUREMENT.\n")
    manifest = os.path.join(root, "manifest.jsonl")
    ledger = os.path.join(root, "ledger.txt")
    _write(manifest, "")
    _write(ledger, "ITEM=W3S ARM=GSCAN FIXTURE=true\n")
    datum = 1_700_000_000

    def sentinel(tag):
        p = os.path.join(root, ".w3s_age_ref.%s" % tag)
        _write(p, "age sentinel\n")
        os.utime(p, (datum, datum))
        return p

    def emit(stage, cost_leg, task, kind, nsteps, endtime, core_min, dobj=None,
             mesh=False):
        tag = "%s_%s" % (cost_leg, stage)
        sen = sentinel(tag)
        sd = _stage_dir_with_field(root, stage, endtime if endtime else 0.0, datum,
                                   mesh=mesh)
        log = os.path.join(root, "%s_FIXTURE.log" % stage)
        _write(log, _fake_log(nsteps or 0, endtime or 0.0, mesh=mesh))
        os.utime(log, (datum + 5, datum + 5))
        if task in ("run_model", "compute_totals"):
            j = {"status": "COMPLETE", "obj": 0.6377885661084924, "nShapes": 4,
                 "shape": [0.0, 0.0, 0.0, 0.0], "dvIndex": 0, "dvDelta": 0.0}
            if dobj is not None:
                j["dobj_dshape"] = dobj
            _write(os.path.join(sd, "d12y_%s.json" % stage), json.dumps(j))
            os.utime(os.path.join(sd, "d12y_%s.json" % stage), (datum + 5, datum + 5))
        row = build_row(stage=stage, cost_leg=cost_leg, task=task, stage_kind=kind,
                        expected_steps=nsteps, rc=0, wall_s=int((core_min or 0) * 60),
                        core_min=core_min, memavail_gib=20.5, endtime=endtime,
                        stage_dir=sd, logpath=log, age_datum=datum, age_sentinel=sen,
                        docker_inspect="0|false", dv_index=0, dv_delta=0.0,
                        dv_units="FFD shape-function DV, dimensionless driver units",
                        coldstart_ok=True, fixture=True)
        if mislabel_leg and stage == "S5" and cost_leg == "A1":
            row["leg"] = "A0"          # the W2R-GRADER-DEF-1 shape, wearing a leg name
        append_row(manifest, row)
        with open(ledger, "a") as f:
            f.write(stage_detail_line(stage, cost_leg, 0, int((core_min or 0) * 60),
                                      core_min, 20.5, os.path.basename(log)) + "\n")
        return row

    plan = [
        ("S0", "SETUP", "mesh", "mesh", None, None, 0.0667, None, True),
        ("S1a", "SETUP", "shell", "steady", 500, 500.0, 0.25, None, False),
        ("S1b", "SETUP", "run_model", "unsteady", 200, 10.0, 0.5333, None, False),
        ("S2a", "SETUP", "run_model", "unsteady", 300, 3.0, 0.9, None, False),
    ]
    gvals = {"A0": FIXTURE_G[fs0], "A1": FIXTURE_G_A1[fs1], "A2": FIXTURE_G_A2[fs1]}
    for leg in LEG_NAMES:
        w = LEG_W[leg]
        plan.append(("S5", leg, "compute_totals", "unsteady", w, round(w * 1e-2, 8),
                     round(w * 2.0438 / 60.0, 4),
                     [gvals[leg], 0.42401, 0.23027, -1.14264], False))
    executed = {}
    for stage, cleg, task, kind, nsteps, endt, cm, dobj, mesh in plan:
        if omit_stage is not None and (stage, cleg) == omit_stage:
            continue
        if blocked_stage is not None and (stage, cleg) == blocked_stage:
            # THE ONLY SHAPE IN WHICH A BLOCKED ROW OCCURS IN THIS ITEM.  The memory
            # guard WAITS and then TERMINATES; it never blocks-and-continues.  But a
            # guard that refuses must leave the same trace in BOTH artefacts
            # (W2R-DEF-1), so the terminal refusal writes a blocked row before it exits
            # non-zero.  The comparator then FILTERS it out and refuses at N4 -- which is
            # correct: Arm A's question is a three-point comparison and there is no
            # partial answer to it.
            append_row(manifest, blocked_row(stage, cleg, "memavail_floor_bound", 13.5))
            continue
        emit(stage, cleg, task, kind, nsteps, endt, cm, dobj=dobj, mesh=mesh)
        executed[cleg] = executed.get(cleg, 0) + 1
    for leg in LEG_NAMES:
        if drop_ledger_leg == leg:
            continue
        with open(ledger, "a") as f:
            f.write(w_steps_line(leg, "1e-2") + "\n")
    for cleg in COST_LEGS:
        n = executed.get(cleg, 0)
        tot = round(sum(p[6] for p in plan if p[1] == cleg
                        and not (omit_stage is not None and (p[0], p[1]) == omit_stage)), 4)
        with open(ledger, "a") as f:
            f.write(leg_spend_line(cleg, 0, int(tot * 60), tot,
                                   len(DECLARED_STAGES[cleg]), n, 0) + "\n")
    return {"root": root, "manifest": manifest, "ledger": ledger, "datum": datum}


# ==================================================================================
# SELFTEST
# ==================================================================================
def _run_grader_gscan(fx, tmpdir):
    g = _pinned(GRADER_NAME, GRADER_MD5)
    pr = subprocess.run([sys.executable, g, "--gscan", "--manifest", fx["manifest"],
                         "--root", fx["root"], "--tmpdir", tmpdir],
                        capture_output=True, text=True)
    return pr.returncode, pr.stdout, pr.stderr


def selftest(tmpdir):
    os.makedirs(tmpdir, exist_ok=True)
    sys.stdout.write("%s_STAGE_RECORD SELFTEST  python_O=%s  workdir=%s\n"
                     % (ITEM, not __debug__, tmpdir))
    sys.stdout.write("-" * 78 + "\n")

    def drive(name, fn, expect):
        """Every control reports EXERCISED-PASS / EXERCISED-FAIL / NOT EXERCISED.  A
        control that could not run is NEVER counted as a pass."""
        try:
            got = fn()
        except Exception as exc:                                    # noqa: BLE001
            control(name, "NOT EXERCISED", "the control itself raised %s: %s"
                    % (exc.__class__.__name__, exc))
            return
        state = "EXERCISED-PASS" if got == expect else "EXERCISED-FAIL"
        control(name, state, "observed=%r expected=%r" % (got, expect))

    # ---- 1. pinned dependencies: EXISTENCE FIRST, THEN md5 (sec.18.3)
    drive("PIN-parent-grader-exists",
          lambda: os.path.isfile(_pinned(PARENT_GRADER_NAME, None)), True)
    drive("PIN-parent-grader-md5",
          lambda: _md5(_pinned(PARENT_GRADER_NAME, None)) == PARENT_GRADER_MD5, True)
    drive("PIN-grader-md5", lambda: _md5(_pinned(GRADER_NAME, None)) == GRADER_MD5, True)
    drive("PIN-parent-launcher-md5",
          lambda: _md5(_pinned(PARENT_LAUNCHER_NAME, None)) == PARENT_LAUNCHER_MD5, True)
    drive("PIN-ceiling-guard-exists",
          lambda: os.path.isfile(os.path.join(HERE, CEILING_GUARD_REL)), True)
    drive("PIN-absent-dependency-refuses",
          lambda: _refuses(lambda: _pinned("no_such_instrument.py", None)), True)

    # ---- 2. the fatal scan is READ from the pinned launcher, not copied
    fatal, benign = fatal_scan_patterns()
    drive("SCAN-read-from-parent-nonempty", lambda: len(fatal) >= 9, True)
    drive("SCAN-benign-exclusion-present", lambda: len(benign) == 1, True)
    drive("SCAN-trapFpe-banner-EXCLUDED", lambda: scan_log_for_fatals(
        "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).\n")[0], [])
    drive("SCAN-real-SIGFPE-CAUGHT", lambda: len(scan_log_for_fatals(
        "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).\n"
        "process rank 2 exited on signal 8 (Floating point exception).\n")[0]) > 0, True)
    drive("SCAN-FOAM-FATAL-CAUGHT", lambda: len(scan_log_for_fatals(
        "--> FOAM FATAL ERROR:\n")[0]) > 0, True)
    drive("SCAN-clean-log-is-EMPTY-not-None",
          lambda: read_stage_log(_tmpfile(tmpdir, "clean.log",
                                          "Time = 0.01\nEnd\n"))["fatal_tokens"], [])
    drive("SCAN-absent-log-is-None-not-EMPTY",
          lambda: read_stage_log(os.path.join(tmpdir, "nope.log"))["fatal_tokens"], None)

    # ---- 3. the ledger line producers, against the CONSUMERS' OWN regexes
    g = grader()
    drive("LEDGER-W_STEPS-matches-consumer",
          lambda: bool(g._leg_ledger_re("A1").match(w_steps_line("A1", "1e-2"))), True)
    drive("LEDGER-W_STEPS-unregistered-leg-refuses",
          lambda: _refuses(lambda: w_steps_line("A9", "1e-2")), True)
    drive("LEDGER-LEG-row-is-spend-shaped",
          lambda: bool(g.SPEND_LINE_RE.match(leg_spend_line("A0", 0, 60, 1.0, 1, 1, 0))),
          True)
    drive("LEDGER-LEG-row-core_min-parses-WHOLE",
          lambda: bool(g.CORE_MIN_VALUE_RE.match(
              g.CORE_MIN_RE.search(leg_spend_line("A0", 0, 60, 66.78, 1, 1, 0)).group(1))),
          True)
    drive("LEDGER-SDETAIL-invisible-to-w3s_grade",
          lambda: bool(g.SPEND_LINE_RE.match(
              stage_detail_line("S5", "A0", 0, 60, 1.0, 20.0, "x.log"))), False)
    drive("LEDGER-SDETAIL-invisible-to-ceiling-guard",
          lambda: bool(re.compile(r"(?:^|\s)core_min=(\S+)").search(
              stage_detail_line("S5", "A0", 0, 60, 1.0, 20.0, "x.log"))), False)

    # ---- 4. the ceiling guard reads THIS ledger.  Both directions, over a real file.
    def _ceiling(rc_ledger_lines, cap, ceiling):
        d = tempfile.mkdtemp(dir=tmpdir)
        lp = os.path.join(d, "ledger.txt")
        _write(lp, "".join(l + "\n" for l in rc_ledger_lines))
        pr = subprocess.run([sys.executable, os.path.join(HERE, CEILING_GUARD_REL),
                             "--check", "--ledger", lp, "--cap", cap,
                             "--ceiling", ceiling, "--row-prefix", "LEG=",
                             "--label", ITEM], capture_output=True, text=True)
        return pr.returncode
    drive("CEILING-empty-ledger-is-a-real-zero",
          lambda: _ceiling(["ITEM=W3S ARM=GSCAN"], "5.0", "330.0"), 0)
    drive("CEILING-reads-our-LEG-rows",
          lambda: _ceiling(["ITEM=W3S", leg_spend_line("SETUP", 0, 105, 1.75, 4, 4, 0),
                            leg_spend_line("A0", 0, 4073, 67.8833, 1, 1, 0)],
                           "70.0", "330.0"), 0)
    drive("CEILING-refuses-over-the-ceiling",
          lambda: _ceiling(["ITEM=W3S", leg_spend_line("A0", 0, 12000, 200.0, 1, 1, 0)],
                           "155.0", "330.0"), 65)
    drive("CEILING-refuses-a-malformed-token",
          lambda: _ceiling(["LEG=A0 rc=0 core_min=1.2.3"], "5.0", "330.0"), 65)
    drive("CEILING-refuses-an-ABSENT-ledger",
          lambda: subprocess.run(
              [sys.executable, os.path.join(HERE, CEILING_GUARD_REL), "--check",
               "--ledger", os.path.join(tmpdir, "never_written.txt"), "--cap", "5.0",
               "--ceiling", "330.0", "--row-prefix", "LEG=", "--label", ITEM],
              capture_output=True, text=True).returncode, 65)
    drive("CEILING-caps-sum-EXACTLY-to-the-ceiling",
          lambda: abs(sum(LEG_CAP_CORE_MIN.values()) - ITEM_CEILING_CORE_MIN) < 1e-9, True)

    # ---- 4a. CAP REACHABILITY.  `cap x 60 / ranks < wall_bound`, every leg.
    drive("CAPREACH-the-registered-caps-are-all-reachable",
          lambda: cap_reachability()[0], 0)
    drive("CAPREACH-and-they-sum-EXACTLY-to-the-ceiling",
          lambda: cap_reachability()[1]["caps_sum_equals_ceiling"], True)
    drive("CAPREACH-A2-at-W=2600-clears-its-own-timeout",
          lambda: [r for r in cap_reachability()[1]["legs"] if r["leg"] == "A2"][0]["reachable"],
          True)
    # THE PLANTED CONTROL, AND IT IS THIS ITEM'S OWN SUPERSEDED REGISTRATION.  A checker
    # reporting zero dead levers must first be shown able to report one -- and the one it
    # is shown is the very cap this item registered and had to withdraw: 155.0 core-min at
    # ranks=1 is 9300 s against a 7200 s bound.
    def _plant_dead_lever():
        saved = dict(LEG_CAP_CORE_MIN)
        saved_ceiling = ITEM_CEILING_CORE_MIN
        try:
            LEG_CAP_CORE_MIN["A2"] = 155.0
            globals()["ITEM_CEILING_CORE_MIN"] = 330.0
            rc, body = cap_reachability()
            return (rc, [d["leg"] for d in body["dead_levers"]])
        finally:
            LEG_CAP_CORE_MIN.clear()
            LEG_CAP_CORE_MIN.update(saved)
            globals()["ITEM_CEILING_CORE_MIN"] = saved_ceiling
    drive("CAPREACH-PLANT-the-WITHDRAWN-A2-cap-155.0-IS-a-dead-lever",
          _plant_dead_lever, (64, ["A2"]))
    drive("CAPREACH-the-plant-did-not-leak-into-the-live-registration",
          lambda: LEG_CAP_CORE_MIN["A2"], 115.0)

    # ---- 4b. THE IN-LEG BUDGET -> `timeout` CONVERTER, both directions
    def _budgetroot(lines):
        d = tempfile.mkdtemp(dir=tmpdir)
        _write(os.path.join(d, "ledger.txt"), "".join(l + "\n" for l in lines))
        return d
    fresh_root = tempfile.mkdtemp(dir=tmpdir, prefix="budget_fresh_")
    # A CONSEQUENCE OF RULING 3 WORTH STATING RATHER THAN LEAVING AS A DEAD BRANCH: once
    # every cap is REACHABLE (`cap x 60 / ranks < wall_bound`), the CAP always binds first
    # on a fresh leg and the stage wall bound becomes a BACKSTOP that cannot fire before
    # it.  A2's 115.0 core-min cap is 6900 s against a 7200 s bound, so `min(bound,
    # budget)` returns 6900.  This control expected 7200 while the cap was the withdrawn
    # 155.0 (9300 s), where the bound won -- the expectation was stale, not the code.
    drive("BUDGET-a-fresh-A2-leg-is-CAP-bound-at-6900s-not-bound-bound",
          lambda: stage_timeout(fresh_root, "A2", 7200)[0], 6900)
    drive("BUDGET-the-wall-bound-STILL-wins-when-it-is-the-smaller-of-the-two",
          lambda: stage_timeout(fresh_root, "A2", 1000)[0], 1000)
    drive("BUDGET-min-is-taken-over-BOTH-so-neither-limb-is-dead",
          lambda: (stage_timeout(fresh_root, "A0", 7200)[0],
                   stage_timeout(fresh_root, "A0", 500)[0]), (6000, 500))
    drive("BUDGET-a-thin-remainder-SHORTENS-the-timeout",
          lambda: stage_timeout(_budgetroot(
              ["ITEM=W3S",
               stage_detail_line("S5", "A2", 0, 6600, 110.0, 20.0, "x.log")]),
              "A2", 7200)[0], 300)
    drive("BUDGET-an-exhausted-leg-REFUSES-no-new-budget",
          lambda: stage_timeout(_budgetroot(
              ["ITEM=W3S",
               stage_detail_line("S5", "A2", 0, 6900, 115.0, 20.0, "x.log")]),
              "A2", 7200)[0], None)
    drive("BUDGET-a-malformed-stage_core_min-is-UNMEASURED-not-zero",
          lambda: leg_spent_from_disk(_budgetroot(
              ["SDETAIL=S5 cost_leg=A2 rc=0 stage_core_min=1.2.3"]), "A2")[0], None)
    drive("BUDGET-a-root-with-logs-and-no-ledger-is-UNMEASURED",
          lambda: leg_spent_from_disk(
              os.path.dirname(_tmpfile(tempfile.mkdtemp(dir=tmpdir), "S5_x.log", "x")),
              "A2")[0], None)
    drive("BUDGET-another-leg's-spend-is-NOT-charged-to-this-one",
          lambda: leg_spent_from_disk(_budgetroot(
              ["ITEM=W3S",
               stage_detail_line("S5", "A0", 0, 4073, 67.8833, 20.0, "x.log")]),
              "A2")[0], 0.0)

    # ---- 5. THE END-TO-END BINDING.  The fixture this file writes must GRADE.
    d1 = tempfile.mkdtemp(dir=tmpdir, prefix="fx_hit_miss_")
    fx1 = build_fixture(d1, fs0="hit", fs1="miss")
    rc1, out1, err1 = _run_grader_gscan(fx1, tmpdir)
    drive("E2E-frozen-comparator-GRADES-our-manifest", lambda: rc1, 0)
    j1 = json.loads(out1) if rc1 == 0 else {}
    drive("E2E-verdict-is-in-the-fixed-vocabulary",
          lambda: j1.get("arm_a_verdict") in ("PASS", "GATE REACHED", "GATE FAIL",
                                              "NOT A RESULT", "BLOCKED", "PENDING"), True)
    drive("E2E-FS0-HIT-on-the-anchor-fixture",
          lambda: [x for x in j1.get("gates", []) if x.get("gate") == "GA-2"][0]["outcome"],
          "HIT")
    drive("E2E-FS1-MISS-on-the-registration's-own-points",
          lambda: [x for x in j1.get("gates", []) if x.get("gate") == "GA-3"][0]["outcome"],
          "MISS")
    drive("E2E-no-step-plan-reached-the-artefact",
          lambda: j1.get("step_plan") == g.BAR_REFUSAL_STRING, True)
    drive("E2E-window-binding-returned-all-three-legs",
          lambda: [x for x in j1.get("gates", []) if x.get("gate") == "GA-W"][0]["legs"],
          dict(LEG_W))

    d2 = tempfile.mkdtemp(dir=tmpdir, prefix="fx_hit_hit_")
    fx2 = build_fixture(d2, fs0="hit", fs1="hit")
    rc2, out2, _ = _run_grader_gscan(fx2, tmpdir)
    j2 = json.loads(out2) if rc2 == 0 else {}
    drive("E2E-FS1-HIT-is-reachable-the-gate-goes-both-ways",
          lambda: [x for x in j2.get("gates", []) if x.get("gate") == "GA-3"][0]["outcome"],
          "HIT")

    # ---- 6. THE NEGATIVE DIRECTION.  A producer never shown able to make the comparator
    # ---- REFUSE has not been shown to be feeding the gate at all.
    d3 = tempfile.mkdtemp(dir=tmpdir, prefix="fx_mislabel_")
    fx3 = build_fixture(d3, fs0="hit", fs1="miss", mislabel_leg=True)
    drive("NEG-leg-mislabel-REFUSED-by-the-comparator",
          lambda: _run_grader_gscan(fx3, tmpdir)[0], 2)
    d4 = tempfile.mkdtemp(dir=tmpdir, prefix="fx_noledgerleg_")
    fx4 = build_fixture(d4, fs0="hit", fs1="miss", drop_ledger_leg="A2")
    drive("NEG-missing-per-leg-W_STEPS-REFUSED",
          lambda: _run_grader_gscan(fx4, tmpdir)[0], 2)
    d5 = tempfile.mkdtemp(dir=tmpdir, prefix="fx_omit_")
    fx5 = build_fixture(d5, fs0="hit", fs1="miss", omit_stage=("S5", "A2"))
    drive("NEG-a-missing-leg-REFUSED-not-graded-as-two-points",
          lambda: _run_grader_gscan(fx5, tmpdir)[0], 2)
    d5b = tempfile.mkdtemp(dir=tmpdir, prefix="fx_blocked_")
    fx5b = build_fixture(d5b, fs0="hit", fs1="miss", blocked_stage=("S5", "A2"))
    drive("NEG-a-BLOCKED-leg-REFUSED-a-blocked-row-is-not-a-third-point",
          lambda: _run_grader_gscan(fx5b, tmpdir)[0], 2)
    drive("NEG-the-blocked-row-IS-in-the-manifest-same-trace-both-artefacts",
          lambda: sum(1 for l in open(fx5b["manifest"])
                      if l.strip() and json.loads(l).get("blocked")), 1)
    drive("RULE4-a-blocked-leg-is-rc6-and-COUNTS-the-blocked-row-IN",
          lambda: (verify_leg(fx5b["root"], "A2")[0],
                   verify_leg(fx5b["root"], "A2")[1]["blocked_count"]), (6, 1))

    # ---- 7. THE PER-LEG RULE-4 ASSERTION, which is the FROZEN PARENT'S OWN GATE
    drive("RULE4-SETUP-leg-passes-on-a-complete-fixture",
          lambda: verify_leg(fx1["root"], "SETUP")[0], 0)
    drive("RULE4-A2-leg-passes-on-a-complete-fixture",
          lambda: verify_leg(fx1["root"], "A2")[0], 0)
    drive("RULE4-truncated-leg-is-rc6-NOT-A-RESULT",
          lambda: verify_leg(fx5["root"], "A2")[0], 6)
    drive("RULE4-truncated-leg-reports-BOTH-counts",
          lambda: (verify_leg(fx5["root"], "A2")[1]["declared_count"],
                   verify_leg(fx5["root"], "A2")[1]["executed_count"]), (1, 0))
    drive("RULE4-truncated-leg-never-says-PASS",
          lambda: verify_leg(fx5["root"], "A2")[1]["verdict"], "NOT A RESULT")
    drive("RULE4-unregistered-leg-refuses",
          lambda: verify_leg(fx1["root"], "A9")[0], 3)

    # a stage that FAILED rule 4 must be caught by the frozen gate, not waved through
    d6 = tempfile.mkdtemp(dir=tmpdir, prefix="fx_stale_")
    fx6 = build_fixture(d6, fs0="hit", fs1="miss")
    _corrupt_row(fx6["manifest"], "S5", "A2", {"age_guard_ok": False})
    drive("RULE4-stale-age-guard-REFUSED-by-the-frozen-gate",
          lambda: verify_leg(fx6["root"], "A2")[0], 2)
    d7 = tempfile.mkdtemp(dir=tmpdir, prefix="fx_rc_")
    fx7 = build_fixture(d7, fs0="hit", fs1="miss")
    _corrupt_row(fx7["manifest"], "S5", "A1", {"rc": 3})
    drive("RULE4-nonzero-rc-REFUSED-by-the-frozen-gate",
          lambda: verify_leg(fx7["root"], "A1")[0], 2)
    d8 = tempfile.mkdtemp(dir=tmpdir, prefix="fx_steps_")
    fx8 = build_fixture(d8, fs0="hit", fs1="miss")
    _corrupt_row(fx8["manifest"], "S5", "A0", {"time_line_count": 1999})
    drive("RULE4-step-count-shortfall-REFUSED-by-the-frozen-gate",
          lambda: verify_leg(fx8["root"], "A0")[0], 2)
    d9 = tempfile.mkdtemp(dir=tmpdir, prefix="fx_memfloor_")
    fx9 = build_fixture(d9, fs0="hit", fs1="miss")
    _corrupt_row(fx9["manifest"], "S5", "A0", {"memavail_GiB": 13.5154})
    drive("RULE4-MemAvailable-below-the-14.0-floor-REFUSED",
          lambda: verify_leg(fx9["root"], "A0")[0], 2)

    # ---- 8. THE AGE GUARD AND THE MTIME QUESTION, driven on real files
    ad = tempfile.mkdtemp(dir=tmpdir, prefix="age_")
    datum = 1_700_000_000
    sen = os.path.join(ad, ".w3s_age_ref.T")
    _write(sen, "x\n")
    os.utime(sen, (datum, datum))
    sd = _stage_dir_with_field(ad, "SX", 20.0, datum)
    drive("AGE-fields-newer-than-the-sentinel-PASS",
          lambda: age_guard(sd, 20.0, datum, sen, "unsteady")["age_guard_ok"], True)
    for fn in os.listdir(os.path.join(sd, repr(20.0))):
        os.utime(os.path.join(sd, repr(20.0), fn), (datum - 60, datum - 60))
    drive("AGE-a-field-OLDER-than-the-sentinel-REFUSES",
          lambda: age_guard(sd, 20.0, datum, sen, "unsteady")["age_guard_ok"], False)
    os.utime(sen, (datum + 99, datum + 99))
    drive("AGE-a-MOVED-sentinel-REFUSES-the-datum-cannot-date-the-run",
          lambda: age_guard(sd, 20.0, datum, sen, "unsteady")["age_guard_ok"], False)
    os.utime(sen, (datum, datum))
    sd2 = _stage_dir_with_field(ad, "SY", 20.0, datum)
    for fn in os.listdir(os.path.join(sd2, repr(20.0))):
        os.utime(os.path.join(sd2, repr(20.0), fn), (datum + 500, datum + 500))
    drive("AGE-a-STAGED-file-post-dating-the-datum-is-REPORTED",
          lambda: len(staged_files_postdating(sd2, datum)) > 0, True)
    drive("AGE-a-clean-stage-tree-post-dates-NOTHING",
          lambda: staged_files_postdating(
              _stage_dir_with_field(ad, "SZ", 20.0, datum + 10_000), datum + 20_000), [])
    drive("AGE-missing-sentinel-REFUSES",
          lambda: age_guard(sd, 20.0, datum, os.path.join(ad, "gone"),
                            "unsteady")["age_guard_ok"], False)

    # ---- 9. THE PRODUCER TRACE, AND ITS PLANTED CONTROL IN BOTH DIRECTIONS
    rc_t, body_t = producer_trace()
    drive("TRACE-every-consumed-key-has-a-producer", lambda: rc_t, 0)
    drive("TRACE-it-actually-looked-at-something",
          lambda: body_t["n_consumed_keys"] >= 20, True)
    rc_p, body_p = producer_trace(drop_key="age_guard_ok")
    drive("TRACE-PLANT-a-dropped-key-IS-FLAGGED", lambda: rc_p, 2)
    drive("TRACE-PLANT-names-the-dropped-key",
          lambda: [f["key"] for f in body_p["findings"]], ["age_guard_ok"])

    # ---- 10. THE AST AUDIT.  A guard that vanishes under `-O` is not a guard.
    drive("AST-assert-statements-in-this-file",
          lambda: _count_asserts(os.path.abspath(__file__)), 0)
    drive("AST-assert-statements-outside-the-selftest",
          lambda: _count_asserts_outside_selftest(os.path.abspath(__file__)), 0)

    sys.stdout.write("-" * 78 + "\n")
    n_pass = len([c for c in _CONTROL_LOG if c[1] == "EXERCISED-PASS"])
    n_fail = len([c for c in _CONTROL_LOG if c[1] == "EXERCISED-FAIL"])
    n_not = len([c for c in _CONTROL_LOG if c[1] == "NOT EXERCISED"])
    sys.stdout.write("%s_STAGE_RECORD SELFTEST controls=%d EXERCISED-PASS=%d "
                     "EXERCISED-FAIL=%d NOT-EXERCISED=%d python_O=%s\n"
                     % (ITEM, len(_CONTROL_LOG), n_pass, n_fail, n_not, not __debug__))
    if n_fail or n_not or not _CONTROL_LOG:
        sys.stdout.write("%s_STAGE_RECORD SELFTEST REFUSED -- NOT EXERCISED is never a "
                         "pass and is never inferred from the absence of a failure\n"
                         % ITEM)
        return 1
    sys.stdout.write("%s_STAGE_RECORD SELFTEST PASS %d/%d\n"
                     % (ITEM, n_pass, len(_CONTROL_LOG)))
    return 0


def _refuses(fn):
    try:
        fn()
    except Refusal:
        return True
    return False


def _tmpfile(d, name, text):
    p = os.path.join(d, name)
    _write(p, text)
    return p


def _corrupt_row(manifest, stage, cost_leg, updates):
    """Rewrite one fixture row so a REFUSAL direction can be driven.  Fixtures only."""
    rows = []
    with open(manifest) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("name") == stage and r.get("cost_leg") == cost_leg:
                r.update(updates)
            rows.append(r)
    with open(manifest, "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")


def _count_asserts(path):
    with open(path) as f:
        tree = ast.parse(f.read(), filename=path)
    return sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert))


def _count_asserts_outside_selftest(path):
    with open(path) as f:
        tree = ast.parse(f.read(), filename=path)
    inside = 0
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name in ("selftest",):
            inside += sum(1 for x in ast.walk(n) if isinstance(x, ast.Assert))
    return _count_asserts(path) - inside


# ==================================================================================
def main(argv):
    ap = argparse.ArgumentParser(prog="w3s_stage_record.py")
    ap.add_argument("--emit-row", action="store_true")
    ap.add_argument("--emit-blocked-row", action="store_true")
    ap.add_argument("--verify-leg", action="store_true")
    ap.add_argument("--producer-trace", action="store_true")
    ap.add_argument("--fixture", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--assert-audit", action="store_true")
    ap.add_argument("--w-steps-line", action="store_true")
    ap.add_argument("--leg-spend-line", action="store_true")
    ap.add_argument("--stage-detail-line", action="store_true")
    ap.add_argument("--stage-timeout", action="store_true")
    ap.add_argument("--cap-reachability", dest="cap_reach", action="store_true")
    ap.add_argument("--bound-s", default="7200")

    ap.add_argument("--root")
    ap.add_argument("--dir")
    ap.add_argument("--cost-leg")
    ap.add_argument("--stage")
    ap.add_argument("--task")
    ap.add_argument("--stage-kind")
    ap.add_argument("--expected-steps")
    ap.add_argument("--rc", default="0")
    ap.add_argument("--wall-s", default="0")
    ap.add_argument("--core-min", default="0.0")
    ap.add_argument("--memavail", default="0.0")
    ap.add_argument("--endtime")
    ap.add_argument("--stage-dir")
    ap.add_argument("--log")
    ap.add_argument("--age-datum")
    ap.add_argument("--age-sentinel")
    ap.add_argument("--docker-inspect", default="0|false")
    ap.add_argument("--dv-index", default="0")
    ap.add_argument("--dv-delta", default="0.0")
    ap.add_argument("--dv-units", default="unregistered")
    ap.add_argument("--coldstart-ok", default="1")
    ap.add_argument("--blocked-by", default="unspecified")
    ap.add_argument("--declared", default="0")
    ap.add_argument("--executed", default="0")
    ap.add_argument("--blocked", default="0")
    ap.add_argument("--deltat", default="1e-2")
    ap.add_argument("--fs0", default="hit")
    ap.add_argument("--fs1", default="miss")
    ap.add_argument("--tmpdir", default="/tmp")
    a = ap.parse_args(argv)

    try:
        if a.assert_audit:
            here = os.path.abspath(__file__)
            n = _count_asserts(here)
            out = _count_asserts_outside_selftest(here)
            print("assert statements in this file: %d (must be 0)" % n)
            print("assert statements OUTSIDE the selftest functions: %d (must be 0)" % out)
            return 0 if (n == 0 and out == 0) else 1
        if a.selftest:
            return selftest(os.path.join(a.tmpdir, "w3s_stage_record_selftest"))
        if a.cap_reach:
            rc, body = cap_reachability()
            print(json.dumps(body, indent=2, sort_keys=True, default=str))
            return rc
        if a.producer_trace:
            rc, body = producer_trace()
            print(json.dumps(body, indent=2, sort_keys=True, default=str))
            return rc
        if a.fixture:
            if not a.dir:
                print("REFUSAL: --fixture needs --dir", file=sys.stderr)
                return 3
            fx = build_fixture(a.dir, fs0=a.fs0, fs1=a.fs1)
            print(json.dumps(fx, indent=2, sort_keys=True))
            return 0
        if a.verify_leg:
            if not (a.root and a.cost_leg):
                print("REFUSAL: --verify-leg needs --root and --cost-leg", file=sys.stderr)
                return 3
            rc, body = verify_leg(a.root, a.cost_leg)
            print(json.dumps(body, indent=2, sort_keys=True, default=str))
            return rc
        if a.stage_timeout:
            if not (a.root and a.cost_leg):
                print("REFUSAL: --stage-timeout needs --root and --cost-leg",
                      file=sys.stderr)
                return 3
            secs, note = stage_timeout(a.root, a.cost_leg, a.bound_s)
            if secs is None:
                print("REFUSED", file=sys.stdout)
                print("W3S_STAGE_TIMEOUT %s" % note, file=sys.stderr)
                return 6
            print("%d" % secs)
            print("W3S_STAGE_TIMEOUT %s" % note, file=sys.stderr)
            return 0
        if a.w_steps_line:
            print(w_steps_line(a.cost_leg and MANIFEST_LEG_OF.get(a.cost_leg, a.cost_leg),
                               a.deltat))
            return 0
        if a.leg_spend_line:
            print(leg_spend_line(a.cost_leg, int(a.rc), int(float(a.wall_s)),
                                 float(a.core_min), int(a.declared), int(a.executed),
                                 int(a.blocked)))
            return 0
        if a.stage_detail_line:
            print(stage_detail_line(a.stage, a.cost_leg, int(a.rc), int(float(a.wall_s)),
                                    float(a.core_min), a.memavail,
                                    os.path.basename(a.log or "-")))
            return 0
        if a.emit_blocked_row:
            if not (a.root and a.cost_leg and a.stage):
                print("REFUSAL: --emit-blocked-row needs --root --cost-leg --stage",
                      file=sys.stderr)
                return 3
            row = blocked_row(a.stage, a.cost_leg, a.blocked_by, float(a.memavail))
            append_row(os.path.join(a.root, "manifest.jsonl"), row)
            print(json.dumps(row, sort_keys=True))
            return 0
        if a.emit_row:
            if not (a.root and a.cost_leg and a.stage and a.task and a.stage_kind):
                print("REFUSAL: --emit-row needs --root --cost-leg --stage --task "
                      "--stage-kind", file=sys.stderr)
                return 3
            row = build_row(
                stage=a.stage, cost_leg=a.cost_leg, task=a.task,
                stage_kind=a.stage_kind, expected_steps=a.expected_steps, rc=int(a.rc),
                wall_s=int(float(a.wall_s)), core_min=float(a.core_min),
                memavail_gib=float(a.memavail), endtime=a.endtime,
                stage_dir=a.stage_dir, logpath=a.log, age_datum=a.age_datum,
                age_sentinel=a.age_sentinel, docker_inspect=a.docker_inspect,
                dv_index=a.dv_index, dv_delta=a.dv_delta, dv_units=a.dv_units,
                coldstart_ok=(a.coldstart_ok == "1"))
            append_row(os.path.join(a.root, "manifest.jsonl"), row)
            print("W3S_ROW stage=%s cost_leg=%s leg=%s W=%d rc=%s age_guard=%r "
                  "fatal_tokens=%r postdating=%d"
                  % (row["name"], row["cost_leg"], row["leg"], row["W"], row.get("rc"),
                     row.get("age_guard_ok"), row.get("fatal_tokens"),
                     len(row.get("age_staged_postdating") or [])))
            return 0
    except Refusal as exc:
        print("REFUSAL: %s" % exc, file=sys.stderr)
        return 2
    print("REFUSAL: no mode selected. Try --selftest, --producer-trace, --assert-audit, "
          "--fixture, --verify-leg, --emit-row, --emit-blocked-row, --w-steps-line, "
          "--leg-spend-line or --stage-detail-line.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
