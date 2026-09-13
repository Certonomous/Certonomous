#!/usr/bin/env python3
# ===========================================================================
# d6r2c_grade.py -- THE PRODUCTION GRADER FOR CURRICULUM ITEM D6R2C, ARM O_mp
# ===========================================================================
#
# WHAT THIS FILE IS, AND THE HAZARD IT CARRIES, DISCLOSED FIRST.
#
# PREREGISTRATION.md section 4 (frozen 2026-09-12, version 1.0, unaltered by
# ADDENDUM 1 and ADDENDUM 2) opens:
#
#     "Graded by `d6r2c_grade.py`'s inputs -- the arm's own log, `opt_IPOPT.txt`,
#      `OptView.hst`, `d6r2c_evals.jsonl` and the arm directory -- all read
#      **after** the container exits."
#
# THAT FILE WAS NEVER WRITTEN.  It is absent from the section 11 frozen-instrument
# table, absent from the working tree and absent from every commit in this
# repository's history.  THIS FILE IS THAT INSTRUMENT, WRITTEN LATE -- after the
# run it grades had already produced data.  That is precisely the hazard
# CLAUDE.md rule 2 exists to prevent, and it is named here rather than hidden.
#
# THE MITIGATION, AND IT IS THE ONLY ONE AVAILABLE.  EVERY threshold, literal,
# comparison direction and label in this file is COPIED VERBATIM out of the
# frozen document, and each constant carries the sentence it was copied from.
# NOTHING was chosen by the author.  Where section 4's prose is ambiguous, this
# file DOES NOT RESOLVE THE AMBIGUITY in its own favour: it computes the strict
# reading, REPORTS the alternative reading beside it, and REFUSES (exit 2)
# rather than pick when two registered inputs disagree about the same quantity.
# The ambiguities are enumerated in AMBIGUITIES below.
#
# REFUSE, NEVER DEGRADE.  A missing or unreadable input is a refusal (exit 2) or
# a gate failure per section 4.  There is no default value anywhere in this file
# and no silent skip.
#
# RULE 3, THE PLANTED CONTROL.  `--selftest` builds complete synthetic arm trees
# in a temporary directory, plants a known defect for EACH of G1-G5 and the cap,
# and REQUIRES the label to flip.  A negative control (an unmutated copy) must
# reproduce the unmutated label.  The selftest exits non-zero if any control
# fails.  It NEVER touches a real run directory.
#
# ===========================================================================
# AMBIGUITIES IN SECTION 4 THAT THIS FILE DOES NOT RESOLVE
# ===========================================================================
#
# A-1.  "the FIRST `obj.J` printed by THIS run".  The arm's log carries `obj.J`
#       in TWO distinct printed forms: the per-evaluation dictionary
#       `{'obj.J': array([<value>])}`, and pyOptSparse's own optimisation-summary
#       table row `<index>  obj.J  <value>` (which is printed once before the
#       solve, carrying 0.000000E+00, and once after it).  Section 4 does not say
#       which form it means.  THIS FILE GRADES ON THE DICTIONARY FORM
#       (J_DICT_RE) and PRINTS the table-form reading beside it, with its own J0,
#       Jf, ratio and G2 outcome, in `g2_alternative_reading` of the JSON and in
#       the stdout table.  The supervisor rules; the grader does not.
#
# A-2.  "at the FINAL DESIGN" (G3).  Section 4 does not name the record that
#       holds the final design.  This file uses the LAST `kind == "F"` row of
#       `d6r2c_evals.jsonl` -- the last real function evaluation -- and then
#       CROSS-CHECKS its `obj.J` against `Jf` read from the log at the log's own
#       printed precision.  If they disagree, "the final design" is genuinely
#       ambiguous between two registered artefacts and THIS FILE REFUSES
#       (exit 2), printing G3 under both candidate rows.  It does not choose.
#
# A-3.  "field data at time `1000`" (G4).  Section 4 does not enumerate the
#       fields.  This file requires, for each of mp04/mp05/mp06: at least one
#       `processor*` directory; a `1000` directory inside EVERY one of them; at
#       least one regular file inside each such `1000`; and EVERY filesystem
#       entry under each `1000` strictly newer than the age datum.  It does not
#       enumerate field names and it does not widen `1000` to "the latest time
#       directory" -- `1000` is the literal in the frozen text.
#
# A-4.  THE LOG'S PRINTED PRECISION IS A HARD FLOOR ON G2.  The dictionary form
#       prints J at numpy's default 8 significant decimals.  A G2 margin smaller
#       than that print's last digit is NOT RESOLVABLE from the log, whatever
#       `d6r2c_evals.jsonl` holds at full precision.  Section 4 registers the log
#       as the source of J0 and Jf, so this file reads the log; the resolvable
#       floor is computed from the printed string itself and REPORTED as
#       `j_print_ulp` so no reader mistakes a rounding for a measurement.
#
# ===========================================================================
# WHAT THE AGE DATUM RESOLVES TO
# ===========================================================================
# Section 4 G4 says "strictly newer than the age datum `0/U`".  The launcher
# `d6r2c_run_arm.sh:227-231` does:
#       test -f "$WORK/0/U" || ABORT
#       touch "$WORK/0"/*
#       AGE_DATUM=$(stat -c '%Y' "$WORK/0/U")     # INTEGER seconds, truncated
#       echo "$AGE_DATUM" > "$WORK/.d6r2c_age_datum"
# and its own ownership instrument (line 368) then uses
#       find "$WORK" -newermt "@$AGE_DATUM" ...
# THIS FILE USES THE RECORDED INTEGER in `.d6r2c_age_datum`, because that is the
# datum the launcher's own G5 instrument compared against, and because `find
# -newermt "@N"` resolves N to N.000000000 -- the exact semantics reproduced by
# `st_mtime > float(datum)` here.  It CROSS-CHECKS that integer against
# `int(stat("0/U").st_mtime)` and REFUSES (exit 2) if they differ: a disagreement
# means `0/U` was touched after launch and the datum is no longer the launch
# instant.  Both values are reported.
# ===========================================================================

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

# ---------------------------------------------------------------------------
# THE FROZEN LITERALS.  Each carries the sentence it was copied from.
# Nothing below was chosen by the author of this file.
# ---------------------------------------------------------------------------

ITEM = "D6R2C"
REGISTERED_BASE = ("/home/ubuntu/certonomous-runs/"
                   "CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable")
DEFAULT_ARM = "O_mp"

# section 4, G1: "`rc = 0`"
G1_REQUIRED_RC = 0
# section 4, G1: "carrying `Number of Iterations....: 25`"
G1_REQUIRED_ITER_LINE = "Number of Iterations....: 25"
# section 4, G1: "and `EXIT: Maximum Number of Iterations Exceeded.`"
G1_REQUIRED_EXIT_LINE = "EXIT: Maximum Number of Iterations Exceeded."
# section 4, G1: "Any other `EXIT:` line -- in particular `Invalid number in NLP
# function or derivative detected` ... **FAILS G1**."
G1_EXIT_PREFIX = "EXIT:"

# section 4, G2: "**PASS requires `Jf <= 0.90 x J0`**"
G2_FACTOR = 0.90

# section 4, G3: "`max_i |CL_i - target_i| <= 1.0e-3` over `cl04 / cl05 / cl06`."
G3_TOL = 1.0e-3
# section 1: "`cl04` -> CL = 0.4, `cl05` -> CL = 0.5, `cl06` -> CL = 0.6"
# and the HEADER row of d6r2c_evals.jsonl, which is cross-checked against this.
CL_TARGETS = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}
POINTS = ("cl04", "cl05", "cl06")
CL_KEY_FMT = "%s.aero_post.functionals.CL"

# section 4, G4: "`OptView.hst`, `opt_IPOPT.txt`, `d6r2c_evals.jsonl`,
# `d6r2c_x0.json` and field data at time `1000` under `mp04/`, `mp05/`, `mp06/`
# `processor*`, all present and **strictly newer than the age datum `0/U`**."
G4_REQUIRED_ARTIFACTS = ("OptView.hst", "opt_IPOPT.txt",
                         "d6r2c_evals.jsonl", "d6r2c_x0.json")
G4_MP_DIRS = ("mp04", "mp05", "mp06")
G4_TIME_DIR = "1000"

# section 4, G5: "**Zero** files under the arm directory newer than the age datum
# are owned by uid 0 or gid 0."
G5_FORBIDDEN_UID = 0
G5_FORBIDDEN_GID = 0

# section 8 table, and d6r2c_run_arm.sh cap_core_min(): "O_mp) echo 2359.5"
CAP_CORE_MIN = 2359.5
# d6r2c_run_arm.sh:352 -- the crossing test the launcher itself applies:
#   [ "$(python3 -c "print(1 if $CM > $CAP else 0)")" = "1" ]
# STRICTLY GREATER.  core_min == cap is NOT a crossing.
# section 8: "A crossing writes `D6R2C_CAP_CROSSED` to the ledger, the row is
# graded **`NOT A RESULT`**, and **the cap is never raised**."
CAP_CROSSED_LEDGER_TOKEN = "D6R2C_CAP_CROSSED"

# section 4 LABELS: "`PASS` = G1^G2^G3^G4^G5.  `GATE FAIL` = G1^G4^G5 hold and G2
# or G3 misses ...  `NOT A RESULT` = G1, G4 or G5 fails, or the registered cap of
# section 8 is crossed.  No other label, no synonyms (rule 1)."
V_PASS = "PASS"
V_GATE_FAIL = "GATE FAIL"
V_NOT_A_RESULT = "NOT A RESULT"

# The two printed forms of obj.J in the arm's log.  See AMBIGUITY A-1.
J_DICT_RE = re.compile(r"\{'obj\.J':\s*array\(\[\s*([^\]\s,]+)\s*\]\)\}")
J_TABLE_RE = re.compile(r"^\s*\d+\s+obj\.J\s+([-+0-9.eE]+)\s*$")

# The ledger row this grader reads rc, core_min, the cap and the log name from.
# d6r2c_run_arm.sh:372.
LEDGER_ROW_RE = re.compile(r"^ARM=(\S+)\s")


class Refusal(Exception):
    """Refuse (exit 2) rather than degrade.  Never a default, never a skip."""


# ---------------------------------------------------------------------------
# small readers
# ---------------------------------------------------------------------------

def _md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_newer(path, datum):
    """`find -newermt "@N"` semantics: mtime strictly greater than N.000000000."""
    return os.lstat(path).st_mtime > float(datum)


def read_age_datum(armdir):
    """Returns (datum_int, detail dict).  Refuses on disagreement.  See header."""
    rec_path = os.path.join(armdir, ".d6r2c_age_datum")
    u_path = os.path.join(armdir, "0", "U")
    if not os.path.isfile(rec_path):
        raise Refusal("no age datum recorded at %s -- d6r2c_run_arm.sh:230 writes "
                      "it at launch; without it G4 and G5 have no datum." % rec_path)
    if not os.path.isfile(u_path):
        raise Refusal("no %s -- section 4 names `0/U` as the age datum and "
                      "d6r2c_run_arm.sh:227 refuses to launch without it." % u_path)
    raw = open(rec_path).read().strip()
    try:
        recorded = int(raw)
    except ValueError:
        raise Refusal("age datum file %s does not hold an integer epoch: %r"
                      % (rec_path, raw))
    u_mtime = os.lstat(u_path).st_mtime
    u_int = int(u_mtime)
    if u_int != recorded:
        raise Refusal(
            "AGE DATUM DISAGREEMENT -- refusing rather than choosing.\n"
            "  .d6r2c_age_datum : %d\n"
            "  int(mtime 0/U)   : %d  (%.9f)\n"
            "  d6r2c_run_arm.sh:229 sets the recorded value FROM 0/U at launch, so a "
            "difference means 0/U was touched afterwards and the datum no longer dates "
            "the run allowed to produce the answer." % (recorded, u_int, u_mtime))
    return recorded, {"age_datum_epoch": recorded,
                      "age_datum_source": ".d6r2c_age_datum (== int(mtime of 0/U))",
                      "age_datum_0U_mtime": u_mtime,
                      "age_datum_agree": True}


def read_ledger(base, arm):
    """The LAST `ARM=<arm>` row of ledger.txt, plus any cap-crossed rows for it."""
    path = os.path.join(base, "ledger.txt")
    if not os.path.isfile(path):
        raise Refusal("no ledger at %s -- d6r2c_run_arm.sh:372 writes the "
                      "ARM=%s row carrying rc, core_min, the cap and the log "
                      "name at container exit." % (path, arm))
    rows, crossed = [], []
    with open(path, errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            m = LEDGER_ROW_RE.match(line)
            if m and m.group(1) == arm:
                fields = {}
                for tok in line.split():
                    if "=" in tok:
                        k, v = tok.split("=", 1)
                        fields[k] = v
                fields["_raw"] = line
                rows.append(fields)
            elif line.startswith(CAP_CROSSED_LEDGER_TOKEN) and ("arm=%s" % arm) in line:
                crossed.append(line)
    if not rows:
        raise Refusal(
            "NO `ARM=%s` ROW IN %s.\n"
            "  The run has not recorded its exit.  Section 4 reads every input "
            "**after the container exits**; grading before that is not a strict "
            "reading of the frozen document and this file will not do it."
            % (arm, path))
    return rows[-1], crossed, len(rows), path


def parse_ipopt(path, datum):
    """G1's evidence.  Every `EXIT:` line found, and whether the iteration line is there."""
    out = {"path": path, "present": os.path.isfile(path)}
    if not out["present"]:
        out.update({"newer_than_datum": False, "exit_lines": [],
                    "iteration_line_found": False, "mtime": None})
        return out
    out["mtime"] = os.lstat(path).st_mtime
    out["newer_than_datum"] = _is_newer(path, datum)
    exits, iter_found = [], False
    with open(path, errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if s.startswith(G1_EXIT_PREFIX):
                exits.append(s)
            if G1_REQUIRED_ITER_LINE in line:
                iter_found = True
    out["exit_lines"] = exits
    out["iteration_line_found"] = iter_found
    return out


def _printed_ulp(text):
    """The resolvable floor of a printed float, from its own string (A-4)."""
    t = text.strip()
    exp = 0
    if "e" in t.lower():
        mant, _, e = t.lower().partition("e")
        exp = int(e)
        t = mant
    if "." in t:
        decimals = len(t.split(".", 1)[1])
    else:
        decimals = 0
    return 10.0 ** (exp - decimals)


def parse_log_J(path):
    """J0/Jf under BOTH printed readings (A-1).  Refuses if the reader sees nothing."""
    if not os.path.isfile(path):
        raise Refusal("the arm's own log is not at %s -- section 4 names it as an "
                      "input and d6r2c_run_arm.sh:359 writes it at exit." % path)
    dict_vals, table_vals = [], []
    with open(path, errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            m = J_DICT_RE.search(line)
            if m:
                dict_vals.append((lineno, m.group(1), float(m.group(1))))
            m2 = J_TABLE_RE.match(line)
            if m2:
                table_vals.append((lineno, m2.group(1), float(m2.group(1))))
    if not dict_vals:
        raise Refusal(
            "REFUSING: no `{'obj.J': array([...])}` line anywhere in %s.\n"
            "  A reader that cannot see the quantity it is asked to grade has no "
            "zero to report (rule 3).  %d pyOptSparse summary-table `obj.J` rows "
            "were seen, which is a different printed form (AMBIGUITY A-1)."
            % (path, len(table_vals)))
    return dict_vals, table_vals


def parse_evals(path, datum):
    """HEADER + the F/G records.  Refuses on a missing or malformed registered field."""
    if not os.path.isfile(path):
        raise Refusal("no %s -- section 4 names it as an input." % path)
    header, F, G = None, [], []
    with open(path, errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError as exc:
                raise Refusal("%s line %d is not JSON (%s) -- refusing rather than "
                              "skipping a record." % (path, lineno, exc))
            kind = row.get("kind")
            if kind == "HEADER":
                header = row
            elif kind == "F":
                F.append(row)
            elif kind == "G":
                G.append(row)
    if header is None:
        raise Refusal("%s carries no HEADER row; the registered CL targets cannot "
                      "be cross-checked." % path)
    if not F:
        raise Refusal("%s carries no `kind == \"F\"` row; there is no evaluated "
                      "design in it, so G3 has no final design to read." % path)
    got = header.get("cl_targets")
    if got != CL_TARGETS:
        raise Refusal(
            "CL TARGET DISAGREEMENT -- refusing rather than choosing.\n"
            "  PREREGISTRATION section 1 : %r\n"
            "  %s HEADER                 : %r" % (CL_TARGETS, path, got))
    return header, F, G


# ---------------------------------------------------------------------------
# the gates
# ---------------------------------------------------------------------------

def gate_g1(rc, ipopt):
    """section 4 G1, verbatim conditions."""
    other_exits = [e for e in ipopt["exit_lines"] if e != G1_REQUIRED_EXIT_LINE]
    detail = {
        "rc": rc,
        "rc_is_zero": rc == G1_REQUIRED_RC,
        "opt_IPOPT_present": ipopt["present"],
        "opt_IPOPT_newer_than_datum": ipopt["newer_than_datum"],
        "iteration_line_required": G1_REQUIRED_ITER_LINE,
        "iteration_line_found": ipopt["iteration_line_found"],
        "exit_line_required": G1_REQUIRED_EXIT_LINE,
        "exit_lines_found": ipopt["exit_lines"],
        "other_exit_lines": other_exits,
        "required_exit_line_found": G1_REQUIRED_EXIT_LINE in ipopt["exit_lines"],
    }
    ok = (detail["rc_is_zero"]
          and detail["opt_IPOPT_present"]
          and detail["opt_IPOPT_newer_than_datum"]
          and detail["iteration_line_found"]
          and detail["required_exit_line_found"]
          and not other_exits)
    return ok, detail


def gate_g2(dict_vals, table_vals):
    """section 4 G2.  Strict reading on the dictionary form; table form reported."""
    j0_txt, j0 = dict_vals[0][1], dict_vals[0][2]
    jf_txt, jf = dict_vals[-1][1], dict_vals[-1][2]
    threshold = G2_FACTOR * j0
    ok = jf <= threshold
    detail = {
        "J0": j0, "J0_printed": j0_txt, "J0_log_line": dict_vals[0][0],
        "Jf": jf, "Jf_printed": jf_txt, "Jf_log_line": dict_vals[-1][0],
        "n_obj_J_prints": len(dict_vals),
        "ratio_Jf_over_J0": (jf / j0) if j0 != 0.0 else None,
        "reduction_percent": ((1.0 - jf / j0) * 100.0) if j0 != 0.0 else None,
        "threshold_0p90_J0": threshold,
        "margin_Jf_minus_threshold": jf - threshold,
        "j_print_ulp": _printed_ulp(jf_txt),
        "source": "log, {'obj.J': array([...])} form (AMBIGUITY A-1)",
    }
    alt = {"note": "pyOptSparse summary-table `obj.J` rows -- the OTHER printed "
                   "form section 4 could mean (AMBIGUITY A-1).  REPORTED, NOT GRADED.",
           "n_rows": len(table_vals),
           "rows": [{"log_line": ln, "printed": txt, "value": val}
                    for ln, txt, val in table_vals]}
    if table_vals:
        a0, af = table_vals[0][2], table_vals[-1][2]
        alt["J0"] = a0
        alt["Jf"] = af
        alt["ratio_Jf_over_J0"] = (af / a0) if a0 != 0.0 else None
        alt["G2_under_this_reading"] = bool(af <= G2_FACTOR * a0)
    return ok, detail, alt


def _record_is_measurable(row):
    """True only if the record is an actual measurement: `fail == 0`, and `obj.J`
    and all three CLs finite.  Used ONLY to NAME a record in a refusal message --
    this file never falls back to it (A-2a)."""
    try:
        if float(row.get("fail")) != 0.0:
            return False
    except (TypeError, ValueError):
        return False
    funcs = row.get("funcs", {})
    vals = [funcs.get("obj.J")] + [funcs.get(CL_KEY_FMT % p) for p in POINTS]
    for v in vals:
        if isinstance(v, list):
            if len(v) != 1:
                return False
            v = v[0]
        try:
            if not math.isfinite(float(v)):
                return False
        except (TypeError, ValueError):
            return False
    return True


def gate_g3(F, jf, jf_ulp):
    """section 4 G3 at the FINAL DESIGN.  Refuses if the two artefacts disagree (A-2)."""
    def cls_of(row):
        out = {}
        for pt in POINTS:
            key = CL_KEY_FMT % pt
            if key not in row.get("funcs", {}):
                raise Refusal("the final-design record has no %r -- G3 cannot be "
                              "read and this file will not substitute a value." % key)
            v = row["funcs"][key]
            if isinstance(v, list):
                if len(v) != 1:
                    raise Refusal("%r is a list of %d values; G3 expects one CL per "
                                  "condition." % (key, len(v)))
                v = v[0]
            out[pt] = float(v)
        return out

    last = F[-1]
    if "obj.J" not in last.get("funcs", {}):
        raise Refusal("the last `kind == \"F\"` record has no `obj.J`, so it cannot "
                      "be cross-checked against the log's Jf (AMBIGUITY A-2).")
    jlast = last["funcs"]["obj.J"]
    if isinstance(jlast, list):
        jlast = jlast[0]
    jlast = float(jlast)

    # -----------------------------------------------------------------------
    # A-2a -- THE NON-MEASUREMENT GUARD.  THIS RUNS BEFORE THE CROSS-CHECK, AND
    # THE ORDER IS LOAD-BEARING.
    #
    # A failed evaluation writes NaN into `obj.J` and into the three CLs.  Every
    # comparison against NaN is False in Python, so the A-2 cross-check below
    # (`abs(jlast - jf) > jf_ulp`) would NOT fire on a NaN record: execution
    # would fall through, `misses` would be NaN, `max(..., key=...)` over NaN has
    # undefined ordering, and `ok = nan <= 1.0e-3` would evaluate False -- the
    # grader would report a GATE FAIL MANUFACTURED OUT OF NaN ARITHMETIC.  That
    # is a verdict built from a non-measurement, and the rule is refuse rather
    # than degrade.  A failed or non-finite final-design record is therefore a
    # REFUSAL.  The last record that does satisfy the conditions is PRINTED so
    # the supervisor can rule; THIS FILE DOES NOT FALL BACK TO IT.
    # -----------------------------------------------------------------------
    fail_flag = last.get("fail")
    complaints = []
    if fail_flag is None:
        complaints.append("the registered `fail` field is ABSENT from the record")
    else:
        try:
            if float(fail_flag) != 0.0:
                complaints.append("`fail` flag is %r -- the evaluation FAILED"
                                  % (fail_flag,))
        except (TypeError, ValueError):
            complaints.append("`fail` flag %r is not a number" % (fail_flag,))
    if not math.isfinite(jlast):
        complaints.append("`obj.J` is %r -- not a finite number" % (jlast,))
    try:
        _cls_probe = cls_of(last)
    except Refusal as exc:
        complaints.append("CL unreadable: %s" % str(exc).splitlines()[0])
        _cls_probe = {}
    for _pt, _v in _cls_probe.items():
        if not math.isfinite(_v):
            complaints.append("CL for %s is %r -- not a finite number" % (_pt, _v))
    if complaints:
        lines = ["THE FINAL-DESIGN RECORD IS NOT A MEASUREMENT -- REFUSING RATHER "
                 "THAN GRADING IT (AMBIGUITY A-2).",
                 "  last kind==F record: n=%s utc=%s fail=%r"
                 % (last.get("n"), last.get("utc"), fail_flag)]
        for c in complaints:
            lines.append("    - %s" % c)
        good = None
        for i in range(len(F) - 1, -1, -1):
            if _record_is_measurable(F[i]):
                good = F[i]
                break
        if good is None:
            lines.append("  NO kind==F record in this file satisfies fail == 0 with "
                         "finite obj.J and finite CLs.")
        else:
            gj, gcls = good["funcs"]["obj.J"], cls_of(good)
            if isinstance(gj, list):
                gj = gj[0]
            lines.append("  The LAST record that IS a measurement: n=%s utc=%s "
                         "fail=%r obj.J=%.17g"
                         % (good.get("n"), good.get("utc"), good.get("fail"),
                            float(gj)))
            lines.append("    its CL misses: %s"
                         % {p: "%.6e" % abs(gcls[p] - CL_TARGETS[p])
                            for p in POINTS})
            lines.append("    its |obj.J - log Jf| = %.6g against the print ulp %.3g"
                         % (abs(float(gj) - jf), jf_ulp))
        lines.append("  Section 4 does not name the record that holds the final "
                     "design and does not legislate a failed one.  THIS FILE DOES "
                     "NOT FALL BACK.  The supervisor rules.")
        raise Refusal("\n".join(lines))

    # A-2: the cross-check.  The log prints J truncated; compare at the log's own
    # resolvable floor, never tighter than the print can carry.
    if abs(jlast - jf) > jf_ulp:
        matches = [(i, r) for i, r in enumerate(F)
                   if abs(float(r.get("funcs", {}).get("obj.J", [float("nan")])[0]
                                if isinstance(r.get("funcs", {}).get("obj.J"), list)
                                else r.get("funcs", {}).get("obj.J", float("nan")))
                          - jf) <= jf_ulp]
        lines = ["THE FINAL DESIGN IS AMBIGUOUS -- REFUSING RATHER THAN CHOOSING "
                 "(AMBIGUITY A-2).",
                 "  Jf from the log                 : %.17g (printed %s, ulp %.3g)"
                 % (jf, "n/a", jf_ulp),
                 "  obj.J of the LAST F record (n=%s): %.17g" % (last.get("n"), jlast),
                 "  |difference|                    : %.3g  EXCEEDS the log's own "
                 "printed resolution" % abs(jlast - jf),
                 "  F records whose obj.J matches Jf: %s"
                 % ([F[i].get("n") for i, _ in matches] or "NONE")]
        for i, r in matches:
            try:
                lines.append("    n=%s CL miss would be %.6e"
                             % (r.get("n"),
                                max(abs(cls_of(r)[pt] - CL_TARGETS[pt]) for pt in POINTS)))
            except Refusal:
                lines.append("    n=%s CL unreadable" % r.get("n"))
        lines.append("  Section 4 does not name the record that holds the final "
                     "design.  The supervisor rules; this file does not.")
        raise Refusal("\n".join(lines))

    cls = cls_of(last)
    misses = {pt: abs(cls[pt] - CL_TARGETS[pt]) for pt in POINTS}
    worst_pt = max(POINTS, key=lambda p: misses[p])
    ok = misses[worst_pt] <= G3_TOL
    detail = {
        "final_design_record": "last kind==F row of d6r2c_evals.jsonl (AMBIGUITY A-2)",
        "final_design_n": last.get("n"),
        "final_design_utc": last.get("utc"),
        "final_design_fail_flag": last.get("fail"),
        "final_design_objJ": jlast,
        "objJ_vs_log_Jf_abs_diff": abs(jlast - jf),
        "objJ_vs_log_Jf_tolerance": jf_ulp,
        "CL": cls,
        "targets": dict(CL_TARGETS),
        "misses": misses,
        "worst_point": worst_pt,
        "worst_miss": misses[worst_pt],
        "tolerance": G3_TOL,
    }
    return ok, detail


def gate_g4(armdir, datum):
    """section 4 G4, exactly as stated.  `1000` is the literal; no fallback (A-3)."""
    detail = {"artifacts": {}, "fields": {}, "missing": [], "not_newer": []}
    ok = True
    for name in G4_REQUIRED_ARTIFACTS:
        p = os.path.join(armdir, name)
        present = os.path.isfile(p)
        newer = _is_newer(p, datum) if present else False
        detail["artifacts"][name] = {
            "present": present, "newer_than_datum": newer,
            "mtime": os.lstat(p).st_mtime if present else None,
            "bytes": os.path.getsize(p) if present else None}
        if not present:
            detail["missing"].append(name)
            ok = False
        elif not newer:
            detail["not_newer"].append(name)
            ok = False

    for mp in G4_MP_DIRS:
        mpdir = os.path.join(armdir, mp)
        procs = sorted(d for d in (os.listdir(mpdir) if os.path.isdir(mpdir) else [])
                       if d.startswith("processor")
                       and os.path.isdir(os.path.join(mpdir, d)))
        entry = {"processor_dirs": procs, "n_processor_dirs": len(procs),
                 "time_dir_required": G4_TIME_DIR, "per_processor": {}}
        if not procs:
            entry["ok"] = False
            entry["why"] = "no processor* directory under %s" % mpdir
            detail["fields"][mp] = entry
            ok = False
            continue
        mp_ok = True
        for pd in procs:
            tdir = os.path.join(mpdir, pd, G4_TIME_DIR)
            rec = {"path": tdir, "present": os.path.isdir(tdir),
                   "n_files": 0, "n_entries_not_newer": 0, "oldest_entry": None}
            if not rec["present"]:
                rec["ok"] = False
                mp_ok = False
            else:
                stale, nfiles, oldest = [], 0, None
                for root, dirs, files in os.walk(tdir):
                    for nm in dirs + files:
                        p = os.path.join(root, nm)
                        st = os.lstat(p)
                        if os.path.isfile(p) and not os.path.islink(p):
                            nfiles += 1
                        if not (st.st_mtime > float(datum)):
                            stale.append(p)
                        if oldest is None or st.st_mtime < oldest[1]:
                            oldest = (p, st.st_mtime)
                if not (os.lstat(tdir).st_mtime > float(datum)):
                    stale.append(tdir)
                rec["n_files"] = nfiles
                rec["n_entries_not_newer"] = len(stale)
                rec["stale_examples"] = stale[:5]
                rec["oldest_entry"] = oldest
                rec["ok"] = bool(nfiles > 0 and not stale)
                if not rec["ok"]:
                    mp_ok = False
            entry["per_processor"][pd] = rec
        entry["ok"] = mp_ok
        detail["fields"][mp] = entry
        ok = ok and mp_ok
    return ok, detail


def gate_g5(armdir, datum):
    """section 4 G5.  Reproduces d6r2c_run_arm.sh:368's own find: every entry."""
    offenders, n_scanned = [], 0
    for root, dirs, files in os.walk(armdir):
        for nm in dirs + files:
            p = os.path.join(root, nm)
            try:
                st = os.lstat(p)
            except OSError as exc:
                raise Refusal("cannot stat %s (%s) -- G5 counts every entry under "
                              "the arm directory and will not skip one." % (p, exc))
            n_scanned += 1
            if st.st_mtime > float(datum) and (st.st_uid == G5_FORBIDDEN_UID
                                               or st.st_gid == G5_FORBIDDEN_GID):
                offenders.append({"path": p, "uid": st.st_uid, "gid": st.st_gid,
                                  "mtime": st.st_mtime})
    detail = {"n_entries_scanned": n_scanned,
              "n_root_owned_newer_than_datum": len(offenders),
              "offenders": offenders[:20],
              "instrument": "os.walk + lstat, == d6r2c_run_arm.sh:368 "
                            "`find $WORK -newermt @DATUM \\( -uid 0 -o -gid 0 \\)`"}
    return len(offenders) == 0, detail


# ---------------------------------------------------------------------------
# the grader
# ---------------------------------------------------------------------------

def grade(armdir, check_live=True):
    armdir = os.path.abspath(armdir)
    if not os.path.isdir(armdir):
        raise Refusal("no arm directory at %s" % armdir)
    base = os.path.dirname(armdir)
    arm = os.path.basename(armdir)

    # Protective guard, NOT a gate: section 4 reads every input AFTER the
    # container exits.  Applies only to the registered run root, so synthetic
    # copies in a temporary directory are never blocked.
    live_note = "not checked"
    if check_live and os.path.realpath(base) == os.path.realpath(REGISTERED_BASE):
        try:
            out = subprocess.run(["sudo", "-n", "docker", "ps", "--format",
                                  "{{.Names}}"], capture_output=True, text=True,
                                 timeout=30)
            names = [n for n in out.stdout.split() if n.startswith("d6r2c_%s_" % arm)]
            live_note = "queried; live=%s" % (names or "none")
            if names:
                raise Refusal(
                    "THE CONTAINER IS STILL UP: %s\n"
                    "  Section 4: every input is read **after** the container exits. "
                    "Refusing to grade a live arm." % ", ".join(names))
        except (OSError, subprocess.SubprocessError) as exc:
            live_note = "could not query docker (%s); proceeding" % exc

    datum, datum_detail = read_age_datum(armdir)
    row, crossed_rows, n_rows, ledger_path = read_ledger(base, arm)

    for key in ("rc", "core_min", "cap_core_min", "log"):
        if key not in row:
            raise Refusal("the ledger row for %s has no `%s=` field:\n  %s"
                          % (arm, key, row["_raw"]))
    try:
        rc = int(row["rc"])
        core_min = float(row["core_min"])
        ledger_cap = float(row["cap_core_min"])
    except ValueError as exc:
        raise Refusal("unparseable ledger row for %s (%s):\n  %s"
                      % (arm, exc, row["_raw"]))
    if ledger_cap != CAP_CORE_MIN:
        raise Refusal(
            "CAP DISAGREEMENT -- refusing rather than choosing.\n"
            "  PREREGISTRATION section 8 / d6r2c_run_arm.sh cap_core_min(): %.6g\n"
            "  ledger row                                                 : %.6g\n  %s"
            % (CAP_CORE_MIN, ledger_cap, row["_raw"]))

    logpath = os.path.join(base, row["log"])
    if not os.path.isfile(logpath):
        raise Refusal("the ledger names log=%s but %s is not there."
                      % (row["log"], logpath))
    # staleness guard, NOT a gate: the log is written at exit (run_arm.sh:359),
    # therefore after the datum.  An older log means this ledger row belongs to an
    # earlier attempt than the arm directory now on disk.
    if not _is_newer(logpath, datum):
        raise Refusal(
            "STALE LEDGER ROW -- refusing rather than grading one run's directory "
            "against another run's exit.\n  log %s mtime %.3f is NOT newer than the "
            "age datum %d.  d6r2c_run_arm.sh:359 writes the log at container exit, "
            "after the datum is set.  %d `ARM=%s` rows are in %s."
            % (logpath, os.lstat(logpath).st_mtime, datum, n_rows, arm, ledger_path))

    ipopt = parse_ipopt(os.path.join(armdir, "opt_IPOPT.txt"), datum)
    dict_vals, table_vals = parse_log_J(logpath)

    # G4 and G5 are evaluated BEFORE G3's inputs are parsed.  Section 4 names
    # `d6r2c_evals.jsonl` in G4's own artifact list, so its ABSENCE is a
    # registered G4 failure -- `NOT A RESULT` -- and must not be converted into a
    # refusal by this file reading it early.  A file that is PRESENT but
    # unreadable is still a refusal: that is not a case section 4 legislates.
    g4, g4d = gate_g4(armdir, datum)
    g5, g5d = gate_g5(armdir, datum)
    g1, g1d = gate_g1(rc, ipopt)
    g2, g2d, g2alt = gate_g2(dict_vals, table_vals)

    evals_path = os.path.join(armdir, "d6r2c_evals.jsonl")
    if not os.path.isfile(evals_path):
        if g4:
            raise Refusal("internal inconsistency: G4 passed without %s"
                          % evals_path)
        header, F, G = None, [], []
        g3 = None
        g3d = {"not_read": "d6r2c_evals.jsonl is absent; section 4 makes that a G4 "
                           "failure and the verdict is NOT A RESULT on G4. G3 is "
                           "NOT GRADED and is reported as null, never as a pass.",
               "CL": None, "misses": None, "targets": dict(CL_TARGETS),
               "tolerance": G3_TOL}
    else:
        header, F, G = parse_evals(evals_path, datum)
        g3, g3d = gate_g3(F, g2d["Jf"], g2d["j_print_ulp"])

    cap_crossed_by_value = core_min > CAP_CORE_MIN
    cap_crossed = bool(cap_crossed_by_value or crossed_rows)
    capd = {"core_min": core_min, "cap_core_min": CAP_CORE_MIN,
            "crossed_by_value": cap_crossed_by_value,
            "comparison": "core_min > cap (d6r2c_run_arm.sh:352, strict)",
            "margin_core_min_minus_cap": core_min - CAP_CORE_MIN,
            "ledger_cap_crossed_rows": crossed_rows,
            "crossed": cap_crossed}

    # section 4 LABELS, verbatim, in their registered precedence.
    if (not g1) or (not g4) or (not g5) or cap_crossed:
        verdict = V_NOT_A_RESULT
    elif g1 and g2 and g3 and g4 and g5:
        verdict = V_PASS
    else:
        verdict = V_GATE_FAIL

    result = {
        "item": ITEM,
        "arm": arm,
        "arm_dir": armdir,
        "run_base": base,
        "verdict": verdict,
        "label_rule": "section 4: PASS = G1^G2^G3^G4^G5; GATE FAIL = G1^G4^G5 hold "
                      "and G2 or G3 misses; NOT A RESULT = G1, G4 or G5 fails, or "
                      "the section 8 cap is crossed.",
        # Sanaa's universal rule 2026-08-26 -- bookkeeping never voids physics, and
        # graders split physics from infrastructure fields.  THIS SPLIT IS REPORTING
        # ONLY.  The single `verdict` above is computed by section 4's labelling rule
        # over all five gates unchanged, and this split does not alter it.
        "gates_physics": {"G2": {"pass": g2, **g2d}, "G3": {"pass": g3, **g3d}},
        "gates_infrastructure": {"G1": {"pass": g1, **g1d},
                                 "G4": {"pass": g4, **g4d},
                                 "G5": {"pass": g5, **g5d},
                                 "cap": capd},
        "split_note": "gates_physics/gates_infrastructure is REPORTING, not grading; "
                      "the verdict is section 4's rule over all five gates unchanged.",
        "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5,
        "cap_crossed": cap_crossed,
        "rc": rc,
        "exit_lines_found": ipopt["exit_lines"],
        "J0": g2d["J0"], "Jf": g2d["Jf"],
        "ratio_Jf_over_J0": g2d["ratio_Jf_over_J0"],
        "CL": g3d.get("CL"), "CL_misses": g3d.get("misses"),
        "core_min": core_min, "cap_core_min": CAP_CORE_MIN,
        "g2_alternative_reading": g2alt,
        "ledger_row": row["_raw"],
        "ledger_path": ledger_path,
        "ledger_rows_for_arm": n_rows,
        "log_path": logpath,
        "n_evals_F": len(F), "n_evals_G": len(G),
        "evals_header": header,
        "live_container_check": live_note,
        "grader_path": os.path.abspath(__file__),
        "grader_md5": _md5_of(os.path.abspath(__file__)),
        "ambiguities_not_resolved": ["A-1 which printed obj.J form G2 means",
                                     "A-2 which record is the final design for G3",
                                     "A-3 what 'field data' enumerates for G4",
                                     "A-4 the log's printed precision floors G2"],
    }
    result.update(datum_detail)
    return result


def render(r):
    W = 78
    out = []
    add = out.append
    add("=" * W)
    add("D6R2C PRODUCTION GRADE -- item %s, arm %s" % (r["item"], r["arm"]))
    add("=" * W)
    add("arm dir      : %s" % r["arm_dir"])
    add("age datum    : %d  (%s)" % (r["age_datum_epoch"], r["age_datum_source"]))
    add("ledger row   : %s" % r["ledger_row"])
    add("log          : %s" % r["log_path"])
    add("grader md5   : %s" % r["grader_md5"])
    add("-" * W)
    add("INFRASTRUCTURE GATES (bookkeeping -- reported separately from physics)")
    g1 = r["gates_infrastructure"]["G1"]
    add("  G1 optimiser terminated at its budget .......... %s"
        % ("PASS" if g1["pass"] else "MISS"))
    add("     rc=%s (need %d)   iteration line %s   exit lines: %s"
        % (g1["rc"], G1_REQUIRED_RC,
           "FOUND" if g1["iteration_line_found"] else "ABSENT",
           g1["exit_lines_found"] or "NONE"))
    if g1["other_exit_lines"]:
        add("     OTHER EXIT LINES (each fails G1): %s" % g1["other_exit_lines"])
    g4 = r["gates_infrastructure"]["G4"]
    add("  G4 results saved and newer than the datum ...... %s"
        % ("PASS" if g4["pass"] else "MISS"))
    for name, a in g4["artifacts"].items():
        add("     %-20s present=%-5s newer=%-5s bytes=%s"
            % (name, a["present"], a["newer_than_datum"], a["bytes"]))
    for mp, e in g4["fields"].items():
        bits = ["%s:%s" % (pd, "ok" if rec.get("ok") else
                           ("no %s" % G4_TIME_DIR if not rec["present"] else "stale"))
                for pd, rec in e.get("per_processor", {}).items()]
        add("     %s/ time %s -> %s" % (mp, G4_TIME_DIR, ", ".join(bits) or e.get("why")))
    g5 = r["gates_infrastructure"]["G5"]
    add("  G5 ran as ubuntu (zero uid0/gid0 files) ........ %s"
        % ("PASS" if g5["pass"] else "MISS"))
    add("     %d entries scanned, %d owned by uid 0 or gid 0 and newer than the datum"
        % (g5["n_entries_scanned"], g5["n_root_owned_newer_than_datum"]))
    for o in g5["offenders"]:
        add("     ROOT-OWNED: %s (uid %s gid %s)" % (o["path"], o["uid"], o["gid"]))
    cap = r["gates_infrastructure"]["cap"]
    add("  cap (section 8) ................................ %s"
        % ("CROSSED" if cap["crossed"] else "not crossed"))
    add("     %.3f core-min against %.1f  (margin %+.3f)"
        % (cap["core_min"], cap["cap_core_min"], cap["margin_core_min_minus_cap"]))
    add("-" * W)
    add("PHYSICS GATES")
    g2 = r["gates_physics"]["G2"]
    add("  G2 Jf <= 0.90 x J0 ............................. %s"
        % ("PASS" if g2["pass"] else "MISS"))
    add("     J0 = %.10g (log line %d, printed %s)"
        % (g2["J0"], g2["J0_log_line"], g2["J0_printed"]))
    add("     Jf = %.10g (log line %d, printed %s)"
        % (g2["Jf"], g2["Jf_log_line"], g2["Jf_printed"]))
    if g2["ratio_Jf_over_J0"] is not None:
        add("     Jf/J0 = %.6f   reduction = %.3f %%   threshold 0.90xJ0 = %.10g"
            % (g2["ratio_Jf_over_J0"], g2["reduction_percent"],
               g2["threshold_0p90_J0"]))
    add("     margin Jf-0.90xJ0 = %+.6g   log print resolution = %.3g"
        % (g2["margin_Jf_minus_threshold"], g2["j_print_ulp"]))
    alt = r["g2_alternative_reading"]
    add("     A-1 ALTERNATIVE READING (reported, not graded): %d summary-table rows%s"
        % (alt["n_rows"],
           ("; J0=%.10g Jf=%.10g G2=%s" % (alt["J0"], alt["Jf"],
                                           alt["G2_under_this_reading"]))
           if alt["n_rows"] else ""))
    g3 = r["gates_physics"]["G3"]
    add("  G3 max|CL_i - target_i| <= 1.0e-3 .............. %s"
        % ("NOT GRADED" if g3["pass"] is None
           else ("PASS" if g3["pass"] else "MISS")))
    if g3["pass"] is None:
        add("     %s" % g3.get("not_read"))
    else:
        for pt in POINTS:
            add("     %-5s CL = %.10f   target %.1f   miss %.3e"
                % (pt, g3["CL"][pt], g3["targets"][pt], g3["misses"][pt]))
        add("     worst %s at %.3e against %.1e   (final design: F record n=%s, "
            "fail=%s)" % (g3["worst_point"], g3["worst_miss"], g3["tolerance"],
                          g3["final_design_n"], g3["final_design_fail_flag"]))
    add("-" * W)
    add("VERDICT: %s" % r["verdict"])
    add("  %s" % r["label_rule"])
    add("=" * W)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# RULE 3 -- THE PLANTED CONTROLS.  Synthetic trees only; no run directory.
# ---------------------------------------------------------------------------

_CLEAN_J0 = 3.0          # synthetic; chosen so 1e-7 relative is visible at the
_CLEAN_JF = 2.4          # log's 8-decimal print (see AMBIGUITY A-4)
_SMALL_J0 = 0.03         # a second, realistic-magnitude pair
_SMALL_JF = 0.024


def _cl_band_edges(pt):
    """The two ATTAINABLE CL values that straddle G3's band edge, one ulp apart.

    There is no double `v` with `abs(v - target) == 1.0e-3` for target in
    {0.4, 0.5, 0.6}, so the equality boundary the brief asks for cannot be built.
    This returns the offsets that land immediately inside and immediately outside
    the band, and ASSERTS both properties after the round trip the fixture
    performs (`target + offset`), so the control cannot silently drift.
    """
    t = CL_TARGETS[pt]
    outside = t + G3_TOL                      # what a naive fixture writes
    inside = math.nextafter(outside, t)       # one ulp back toward the target
    off_out, off_in = outside - t, inside - t
    miss_out, miss_in = abs((t + off_out) - t), abs((t + off_in) - t)
    assert miss_out > G3_TOL, ("fixture: target+1.0e-3 was expected to land "
                               "OUTSIDE the band, got %.17g" % miss_out)
    assert miss_in <= G3_TOL, ("fixture: one ulp inside was expected to land "
                               "INSIDE the band, got %.17g" % miss_in)
    return off_in, off_out, miss_in, miss_out


def _write_log(path, j_values, table_values=(0.0, None)):
    lines = ["D6R2C_MODE: COLD  max_iter=25", "Optimization Problem"]
    for v in j_values[:1]:
        lines.append("{'obj.J': array([%s])}" % v)
    lines.append("   Objectives")
    lines.append("      Index  Name             Value")
    lines.append("          0  obj.J     %.6E" % table_values[0])
    for v in j_values[1:]:
        lines.append("{'obj.J': array([%s])}" % v)
    if table_values[1] is not None:
        lines.append("          0  obj.J     %.6E" % table_values[1])
    open(path, "w").write("\n".join(lines) + "\n")


def _build_clean(root, j0=_CLEAN_J0, jf=_CLEAN_JF, cl_offsets=None,
                 rc=0, core_min=780.0, iters=25,
                 exit_line=G1_REQUIRED_EXIT_LINE, arm=DEFAULT_ARM,
                 final_fail=0, final_nan=False):
    """A complete synthetic arm that must grade PASS."""
    base = os.path.join(root, "base")
    armdir = os.path.join(base, arm)
    os.makedirs(os.path.join(armdir, "0"))
    open(os.path.join(armdir, "0", "U"), "w").write("U\n")
    datum = int(os.lstat(os.path.join(armdir, "0", "U")).st_mtime)
    open(os.path.join(armdir, ".d6r2c_age_datum"), "w").write("%d\n" % datum)
    newer = datum + 10

    def touch(p, t=newer):
        os.utime(p, (t, t))

    j0_txt = "%.8f" % j0
    jf_txt = "%.8f" % jf
    for name in G4_REQUIRED_ARTIFACTS:
        p = os.path.join(armdir, name)
        open(p, "w").write("x\n")
        touch(p)
    open(os.path.join(armdir, "opt_IPOPT.txt"), "w").write(
        "Number of Iterations....: %d\n"
        "Total CPU secs in IPOPT                               =      1.0\n"
        "%s\n" % (iters, exit_line))
    touch(os.path.join(armdir, "opt_IPOPT.txt"))

    cl_offsets = cl_offsets or {p: 0.0 for p in POINTS}
    rows = [{"kind": "HEADER", "cl_targets": dict(CL_TARGETS), "max_iter": 25,
             "mode": "COLD", "points": list(POINTS), "ranks": 4, "uid": 1000,
             "gid": 1000, "weights": {"cl04": 0.25, "cl05": 0.5, "cl06": 0.25},
             "utc": "2026-01-01T00:00:00Z", "wall_since_start_s": 0.0,
             "hotstart_file": ""}]
    for n, jv in ((1, j0), (2, jf)):
        funcs = {CL_KEY_FMT % p: [CL_TARGETS[p] + (cl_offsets[p] if n == 2 else 0.0)]
                 for p in POINTS}
        # the log truncates J to 8 decimals; the record holds full precision
        funcs["obj.J"] = [float("%.8f" % jv) + 3.0e-12]
        if n == 2 and final_nan:
            nan = float("nan")
            funcs["obj.J"] = [nan]
            for p in POINTS:
                funcs[CL_KEY_FMT % p] = [nan]
        rows.append({"kind": "F", "n": n,
                     "fail": (final_fail if n == 2 else 0), "eval_wall_s": 1.0,
                     "utc": "2026-01-01T00:%02d:00Z" % n,
                     "wall_since_start_s": float(n), "dv": {"dvs.twist": [0.0]},
                     "funcs": funcs})
    with open(os.path.join(armdir, "d6r2c_evals.jsonl"), "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    touch(os.path.join(armdir, "d6r2c_evals.jsonl"))

    for mp in G4_MP_DIRS:
        for pd in ("processor0", "processor1"):
            t = os.path.join(armdir, mp, pd, G4_TIME_DIR)
            os.makedirs(t)
            for f in ("U.gz", "p.gz", "T.gz"):
                open(os.path.join(t, f), "w").write("f\n")
                touch(os.path.join(t, f))
            touch(t)
            touch(os.path.join(armdir, mp, pd))
        touch(os.path.join(armdir, mp))

    stamp = "20260101T000000Z_1"
    logname = "%s_%s.log" % (arm, stamp)
    _write_log(os.path.join(base, logname), [j0_txt, jf_txt],
               table_values=(0.0, jf))
    touch(os.path.join(base, logname))

    with open(os.path.join(base, "ledger.txt"), "w") as fh:
        fh.write("ITEM=%s\n" % ITEM)
        fh.write("ARM=%s rc=%d oom=false wall_s=11700 ranks=4 core_min=%s "
                 "cost_ranks=4 cap_core_min=%s max_iter=25 hotstart=none "
                 "uid=1000:1000 root_owned_new_files=0 memavail_pre_GiB=600 "
                 "load1_pre=1.0 swap_pre_kB=0 log=%s stamp=%s\n"
                 % (arm, rc, core_min, CAP_CORE_MIN, logname, stamp))
    return base, armdir, datum


def _verdict_of(armdir):
    try:
        return grade(armdir, check_live=False)["verdict"]
    except Refusal as exc:
        return "REFUSE: %s" % str(exc).splitlines()[0]


def selftest():
    controls, failures = [], []
    tmp = tempfile.mkdtemp(prefix="d6r2c_grade_selftest_")
    root_planted_real = None

    def control(name, expect, mutate=None, build=None):
        d = tempfile.mkdtemp(dir=tmp)
        base, armdir, datum = (build or _build_clean)(d)
        note = mutate(base, armdir, datum) if mutate else ""
        got = _verdict_of(armdir)
        ok = (got == expect) if expect != "REFUSE" else got.startswith("REFUSE")
        controls.append((name, expect, got, ok, note))
        if not ok:
            failures.append(name)
        return armdir

    def edit(path, old, new):
        t = open(path).read()
        assert old in t, "selftest fixture: %r not in %s" % (old, path)
        open(path, "w").write(t.replace(old, new))

    def keep_mtime(path, fn):
        st = os.lstat(path)
        fn()
        os.utime(path, (st.st_mtime, st.st_mtime))

    # ---- NEGATIVE CONTROLS -------------------------------------------------
    control("N1 clean synthetic arm", V_PASS)
    control("N3 clean arm at realistic J magnitude", V_PASS,
            build=lambda r: _build_clean(r, j0=_SMALL_J0, jf=_SMALL_JF))

    # N2 -- the negative control proper: an UNMUTATED COPY must reproduce the
    # unmutated original's label.  A real copy on disk, not an assertion.
    _d = tempfile.mkdtemp(dir=tmp)
    _base, _arm, _ = _build_clean(_d)
    _orig = _verdict_of(_arm)
    _copy_base = os.path.join(_d, "copy")
    shutil.copytree(_base, _copy_base, symlinks=True)
    for _r, _ds, _fs in os.walk(_base):
        for _n in _ds + _fs:
            _p = os.path.join(_r, _n)
            _q = os.path.join(_copy_base, os.path.relpath(_p, _base))
            _st = os.lstat(_p)
            os.utime(_q, (_st.st_mtime, _st.st_mtime))
    _got = _verdict_of(os.path.join(_copy_base, DEFAULT_ARM))
    _ok = (_got == _orig)
    controls.append(("N2 an UNMUTATED COPY reproduces the original's label",
                     _orig, _got, _ok, "real copytree, mtimes preserved"))
    if not _ok:
        failures.append("N2 unmutated copy")

    # ---- G1 ----------------------------------------------------------------
    control("G1a EXIT line -> 'Invalid number in NLP function or derivative "
            "detected'", V_NOT_A_RESULT,
            build=lambda r: _build_clean(
                r, exit_line="EXIT: Invalid number in NLP function or "
                             "derivative detected"))
    control("G1b rc = 137 (OOM)", V_NOT_A_RESULT,
            build=lambda r: _build_clean(r, rc=137))
    control("G1c rc = 255", V_NOT_A_RESULT, build=lambda r: _build_clean(r, rc=255))
    control("G1d Number of Iterations 24, not 25", V_NOT_A_RESULT,
            build=lambda r: _build_clean(r, iters=24))
    control("G1e a SECOND EXIT: line beside the registered one", V_NOT_A_RESULT,
            mutate=lambda b, a, d: keep_mtime(
                os.path.join(a, "opt_IPOPT.txt"),
                lambda: open(os.path.join(a, "opt_IPOPT.txt"), "a").write(
                    "EXIT: Restoration Failed!\n")) or "appended a second EXIT:")

    # ---- G2 ----------------------------------------------------------------
    control("G2a Jf EXACTLY 0.90 x J0 (boundary -- must hold)", V_PASS,
            build=lambda r: _build_clean(r, j0=_CLEAN_J0,
                                         jf=G2_FACTOR * _CLEAN_J0))
    control("G2b Jf = 0.9000001 x J0", V_GATE_FAIL,
            build=lambda r: _build_clean(r, j0=_CLEAN_J0,
                                         jf=0.9000001 * _CLEAN_J0))
    control("G2c Jf just over the band at realistic magnitude "
            "(0.90 x J0 + 1e-7)", V_GATE_FAIL,
            build=lambda r: _build_clean(r, j0=_SMALL_J0,
                                         jf=G2_FACTOR * _SMALL_J0 + 1.0e-7))

    # ---- G3 ----------------------------------------------------------------
    # THE G3 BAND EDGE IS NOT REPRESENTABLE, AND THAT IS A FINDING, NOT A BUG.
    # For every registered target (0.4, 0.5, 0.6) there is NO double `v` with
    # abs(v - target) == 1.0e-3 exactly: the attainable misses step by one ulp of
    # `v` (~1.1e-16) and straddle the frozen literal without landing on it.  The
    # naive fixture `target + 1.0e-3` evaluates to a miss of 1.0000000000000009e-3,
    # which is ABOVE the band and GATE FAILs under section 4's `<=` -- correctly.
    # The boundary is therefore driven from BOTH SIDES, one ulp apart, which is a
    # stronger control than the unattainable equality.  NOTHING in the gate is
    # widened, rounded or given a tolerance to accommodate this.
    _off_in, _off_out, _miss_in, _miss_out = _cl_band_edges("cl05")
    control("G3a largest ATTAINABLE CL miss inside the band (%.17g <= 1.0e-3)"
            % _miss_in, V_PASS,
            build=lambda r: _build_clean(
                r, cl_offsets={"cl04": 0.0, "cl05": _off_in, "cl06": 0.0}))
    control("G3a2 smallest ATTAINABLE CL miss outside it (%.17g > 1.0e-3 -- this is "
            "what `target + 1.0e-3` actually evaluates to)" % _miss_out,
            V_GATE_FAIL,
            build=lambda r: _build_clean(
                r, cl_offsets={"cl04": 0.0, "cl05": _off_out, "cl06": 0.0}))
    control("G3b CL miss 1.0001e-3", V_GATE_FAIL,
            build=lambda r: _build_clean(
                r, cl_offsets={"cl04": 0.0, "cl05": 1.0001e-3, "cl06": 0.0}))
    control("G3c CL miss 1.0001e-3 on cl06", V_GATE_FAIL,
            build=lambda r: _build_clean(
                r, cl_offsets={"cl04": 0.0, "cl05": 0.0, "cl06": -1.0001e-3}))

    # ---- G4 ----------------------------------------------------------------
    for art in G4_REQUIRED_ARTIFACTS:
        control("G4 remove %s" % art, V_NOT_A_RESULT,
                mutate=(lambda art_: lambda b, a, d: (
                    os.remove(os.path.join(a, art_)), "removed")[1])(art))
    control("G4 backdate OptView.hst to 1 s OLDER than the datum", V_NOT_A_RESULT,
            mutate=lambda b, a, d: (os.utime(os.path.join(a, "OptView.hst"),
                                             (d - 1, d - 1)), "backdated")[1])
    control("G4 artifact mtime EXACTLY the datum (not STRICTLY newer)",
            V_NOT_A_RESULT,
            mutate=lambda b, a, d: (os.utime(os.path.join(a, "d6r2c_x0.json"),
                                             (d, d)), "mtime == datum")[1])
    control("G4 remove mp05/processor1/1000", V_NOT_A_RESULT,
            mutate=lambda b, a, d: (shutil.rmtree(
                os.path.join(a, "mp05", "processor1", G4_TIME_DIR)), "removed")[1])
    control("G4 backdate one field file under mp06/.../1000", V_NOT_A_RESULT,
            mutate=lambda b, a, d: (os.utime(
                os.path.join(a, "mp06", "processor0", G4_TIME_DIR, "U.gz"),
                (d - 5, d - 5)), "backdated")[1])
    control("G4 rename 1000 -> 0.0026 (the LATEST time dir is NOT a substitute)",
            V_NOT_A_RESULT,
            mutate=lambda b, a, d: (os.rename(
                os.path.join(a, "mp04", "processor0", G4_TIME_DIR),
                os.path.join(a, "mp04", "processor0", "0.0026")), "renamed")[1])
    control("G4 empty 1000 directory (present but no field file)", V_NOT_A_RESULT,
            mutate=lambda b, a, d: ([os.remove(os.path.join(
                a, "mp04", "processor0", G4_TIME_DIR, f))
                for f in os.listdir(os.path.join(a, "mp04", "processor0",
                                                 G4_TIME_DIR))], "emptied")[1])

    # ---- G5 ----------------------------------------------------------------
    def plant_root(b, a, d):
        nonlocal root_planted_real
        p = os.path.join(a, "root_written_file")
        r = subprocess.run(["sudo", "-n", "touch", p], capture_output=True)
        if r.returncode == 0 and os.path.exists(p) and os.lstat(p).st_uid == 0:
            root_planted_real = p
            return "REAL root-owned file planted via sudo -n touch (uid 0)"
        raise AssertionError("could not plant a real root-owned file")

    try:
        control("G5 a REAL uid-0 file newer than the datum", V_NOT_A_RESULT,
                mutate=plant_root)
        g5_mode = "REAL root-owned file (sudo -n touch), uid 0 verified by lstat"
    except AssertionError:
        # Simulated at the stat-reading boundary, and SAID so.
        real_lstat = os.lstat
        target = {}

        def fake_lstat(path, *a, **k):
            st = real_lstat(path, *a, **k)
            if target.get("p") and os.path.abspath(str(path)) == target["p"]:
                class S:
                    pass
                s = S()
                for f in dir(st):
                    if f.startswith("st_"):
                        setattr(s, f, getattr(st, f))
                s.st_uid = 0
                s.st_gid = 0
                return s
            return st

        def plant_sim(b, a, d):
            p = os.path.join(a, "root_written_file")
            open(p, "w").write("x\n")
            target["p"] = os.path.abspath(p)
            return "SIMULATED at the stat-reading boundary (os.lstat patched)"

        os.lstat = fake_lstat
        try:
            control("G5 a uid-0 file newer than the datum (SIMULATED)",
                    V_NOT_A_RESULT, mutate=plant_sim)
        finally:
            os.lstat = real_lstat
            target.clear()
        g5_mode = ("SIMULATED at the stat-reading boundary -- no root-owned file "
                   "could be created without root")

    # ---- the cap -----------------------------------------------------------
    control("CAP core_min 2359.6 (over 2359.5)", V_NOT_A_RESULT,
            build=lambda r: _build_clean(r, core_min=2359.6))
    control("CAP core_min EXACTLY 2359.5 (not crossed -- strict >)", V_PASS,
            build=lambda r: _build_clean(r, core_min=CAP_CORE_MIN))
    control("CAP a D6R2C_CAP_CROSSED ledger row while core_min is under the cap",
            V_NOT_A_RESULT,
            mutate=lambda b, a, d: (open(os.path.join(b, "ledger.txt"), "a").write(
                "D6R2C_CAP_CROSSED arm=O_mp core_min=2400.0 cap=2359.5 "
                "action=REPORTED_RUN_CONTINUES_NOT_A_RESULT_AND_CAP_NEVER_RAISED\n"),
                "row appended")[1])

    # ---- PRECEDENCE --------------------------------------------------------
    control("PREC G2 misses AND rc=137 -> NOT A RESULT, never GATE FAIL",
            V_NOT_A_RESULT,
            build=lambda r: _build_clean(r, rc=137, j0=_CLEAN_J0,
                                         jf=0.99 * _CLEAN_J0))
    control("PREC G3 misses AND a root-owned file is absent but 1000 is gone "
            "-> NOT A RESULT", V_NOT_A_RESULT,
            build=lambda r: _build_clean(
                r, cl_offsets={"cl04": 1.0e-2, "cl05": 0.0, "cl06": 0.0}),
            mutate=lambda b, a, d: (shutil.rmtree(
                os.path.join(a, "mp04", "processor0", G4_TIME_DIR)), "removed")[1])

    # ---- REFUSALS ----------------------------------------------------------
    control("REFUSE no ARM= row in the ledger", "REFUSE",
            mutate=lambda b, a, d: (open(os.path.join(b, "ledger.txt"), "w").write(
                "ITEM=%s\n" % ITEM), "ledger row removed")[1])
    control("REFUSE the log the ledger names is absent", "REFUSE",
            mutate=lambda b, a, d: ([os.remove(os.path.join(b, f))
                                     for f in os.listdir(b) if f.endswith(".log")],
                                    "log removed")[1])
    control("REFUSE no obj.J printed in the log (a blind reader)", "REFUSE",
            mutate=lambda b, a, d: [keep_mtime(
                os.path.join(b, f),
                (lambda fp: lambda: open(fp, "w").write("no objective here\n"))(
                    os.path.join(b, f)))
                for f in os.listdir(b) if f.endswith(".log")] and "log blanked")
    control("REFUSE the age datum disagrees with 0/U", "REFUSE",
            mutate=lambda b, a, d: (open(os.path.join(a, ".d6r2c_age_datum"),
                                         "w").write("%d\n" % (d - 100)),
                                    "datum rewritten")[1])
    control("REFUSE the ledger cap is not the registered 2359.5", "REFUSE",
            mutate=lambda b, a, d: (edit(os.path.join(b, "ledger.txt"),
                                         "cap_core_min=2359.5",
                                         "cap_core_min=3000.0"),
                                    "cap rewritten")[1])
    control("REFUSE the HEADER CL targets are not the registered ones", "REFUSE",
            mutate=lambda b, a, d: (edit(os.path.join(a, "d6r2c_evals.jsonl"),
                                         '"cl06": 0.6', '"cl06": 0.7'),
                                    "target rewritten")[1])
    control("REFUSE the final-design record disagrees with the log's Jf (A-2)",
            "REFUSE",
            mutate=lambda b, a, d: (edit(os.path.join(a, "d6r2c_evals.jsonl"),
                                         '"obj.J": [2.40000000000',
                                         '"obj.J": [2.77700000000'),
                                    "last F record's J moved")[1])
    control("REFUSE the ledger row is older than the arm directory (stale row)",
            "REFUSE",
            mutate=lambda b, a, d: ([os.utime(os.path.join(b, f), (d - 60, d - 60))
                                     for f in os.listdir(b) if f.endswith(".log")],
                                    "log backdated before the datum")[1])
    # A-2a -- the NaN/failed final-design record.  WITHOUT the guard added for
    # this control the grader reports GATE FAIL built out of NaN arithmetic,
    # because every comparison against NaN is False and the A-2 cross-check
    # therefore does not fire.  The label MUST be a refusal, never GATE FAIL.
    control("REFUSE the final-design record carries fail=1", "REFUSE",
            build=lambda r: _build_clean(r, final_fail=1))
    control("REFUSE the final-design record is NaN in obj.J and all three CLs "
            "(would otherwise manufacture GATE FAIL out of NaN arithmetic)",
            "REFUSE", build=lambda r: _build_clean(r, final_fail=1, final_nan=True))
    control("REFUSE the final-design record is NaN with fail=0 (NaN alone is "
            "enough; the fail flag is not the only guard)", "REFUSE",
            build=lambda r: _build_clean(r, final_fail=0, final_nan=True))
    control("REFUSE d6r2c_evals.jsonl has no F record", "REFUSE",
            mutate=lambda b, a, d: (keep_mtime(
                os.path.join(a, "d6r2c_evals.jsonl"),
                lambda: open(os.path.join(a, "d6r2c_evals.jsonl"), "w").write(
                    json.dumps({"kind": "HEADER", "cl_targets": dict(CL_TARGETS)})
                    + "\n")), "F records removed")[1])

    if root_planted_real:
        subprocess.run(["sudo", "-n", "rm", "-f", root_planted_real],
                       capture_output=True)
    shutil.rmtree(tmp, ignore_errors=True)

    W = 78
    print("=" * W)
    print("D6R2C_GRADE SELFTEST -- planted controls, synthetic trees only")
    print("=" * W)
    for name, expect, got, ok, note in controls:
        print("%-4s %-62s" % ("ok" if ok else "FAIL", name))
        print("       expected %-14s got %-14s %s"
              % (expect, got, ("[%s]" % note) if note else ""))
    print("-" * W)
    print("G5 control mode: %s" % g5_mode)
    print("-" * W)
    if failures:
        print("D6R2C_GRADE SELFTEST FAIL n_failed=%d of %d: %s"
              % (len(failures), len(controls), ", ".join(failures)))
        return 1
    print("D6R2C_GRADE SELFTEST PASS n=%d" % len(controls))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Grade curriculum item D6R2C arm O_mp against the FROZEN "
                    "production gates G1-G5 of PREREGISTRATION.md section 4.")
    ap.add_argument("armdir", nargs="?",
                    default=os.path.join(REGISTERED_BASE, DEFAULT_ARM),
                    help="the arm directory (default: the registered O_mp)")
    ap.add_argument("--selftest", action="store_true",
                    help="drive the planted controls and exit")
    ap.add_argument("--no-json", action="store_true",
                    help="print the table but write no <ARM>_GRADE.json")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    try:
        r = grade(args.armdir)
    except Refusal as exc:
        print("D6R2C_GRADE REFUSE (exit 2)")
        print(str(exc))
        return 2

    print(render(r))
    if not args.no_json:
        out = os.path.join(r["run_base"], "%s_GRADE.json" % r["arm"])
        with open(out, "w") as fh:
            json.dump(r, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        print("written: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
