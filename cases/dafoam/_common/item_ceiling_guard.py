#!/usr/bin/env python3
# =============================================================================
# item_ceiling_guard.py -- the PROSPECTIVE cumulative item-ceiling guard for the
# dafoam family.  One known-good implementation, so a new launcher copies or
# calls THIS instead of inheriting a guard that fails open.
#
# CLAUDE.md rule 12: "An overrun STOPS the run; it does not get a new budget."
# CLAUDE.md rule  3: "A zero from a reader not shown able to see a non-zero is
#                     not evidence."
#
# -----------------------------------------------------------------------------
# WHY THIS FILE EXISTS -- the three measured defects it is written against.
# -----------------------------------------------------------------------------
#
# (1) THE MISSING-LEDGER PLANTED ZERO.
#     `ladder-a/A2/curriculum_D6RF/d6rf_chain_driver.sh:130-146` reads prior
#     spend inside `try: ... except IOError: pass` and then prints the running
#     total.  A ledger that is absent, or unreadable, therefore returns the
#     string `0.000` -- INDISTINGUISHABLE from a ledger that exists and records
#     nothing spent.  That is a planted zero inside the guard's own input.
#     `ladder-a/A1/wall_resolved_alpha_tail/a1wrt_run_unit.sh:290-305` repairs
#     half of it -- a parse EXCEPTION yields the token `UNMEASURED` and the unit
#     refuses, and its own comment states the principle -- but its :285-286 limb
#     still reads
#         if not os.path.exists(p): print('0.0'); sys.exit()
#     so the ABSENT ledger is a `0.0` there too.  Measured, this file, 2026-09-04.
#     HERE: absent, unreadable, and unparseable are ONE state, `UNMEASURED`,
#     and `UNMEASURED` refuses.
#
# (2) THE PERMISSIVE NUMERIC REGEX -- TWO DIFFERENT FAILURES, NOT ONE.
#     d6rf uses `\bcore_min=([0-9.]+)`; a1wrt uses `\bcore_min=([0-9]+\.?[0-9]*)`.
#     These do NOT fail the same way, and the difference was found by DRIVING
#     them rather than reading them (selftest limbs CONTRAST-D6RF-REGEX and
#     CONTRAST-A1WRT-REGEX):
#       * `[0-9.]+` -- the `.` is inside a character class, so it is a LITERAL
#         dot.  On `core_min=1.2.3` this captures `1.2.3` WHOLE, and `float()`
#         then raises ValueError.  d6rf does not catch ValueError, so `$SPENT`
#         comes back EMPTY and defect (3) below fires.  It does NOT truncate.
#       * `[0-9]+\.?[0-9]*` -- at most one dot, so on the same input it captures
#         the PREFIX `1.2` and RAISES NOTHING.  a1wrt therefore SILENTLY
#         UNDER-COUNTS by an unknown amount and its own UNMEASURED limb never
#         fires, because there was no exception to catch.  On this input the
#         file with the better UNMEASURED discipline is the one that fails more
#         quietly, because it produces a plausible number instead of an empty
#         one.
#     Both are wrong in the permissive direction; only one of them is loud.
#     HERE: the token is captured WHOLE with `\S+` and validated WHOLE.  A token
#     that is not a finite non-negative decimal makes the whole read UNMEASURED.
#     It is NOT skipped and the remaining rows summed -- a partial sum is an
#     under-count, which is the same failure wearing a smaller number.
#
# (3) THE SHELL-ARITHMETIC FAIL-OPEN.
#     d6rf's ValueError path is uncaught, so `$SPENT` comes back EMPTY, and the
#     projection is then evaluated as `python3 -c "print(... ( $SPENT + $ACAP ) ...)"`
#     -- with SPENT empty that is Python's UNARY PLUS on the cap.  The projection
#     prints a clean `480.000` and the guard PASSES with the prior spend dropped.
#     `ladder-a/A1/curriculum_D19T/d19t_chain_driver.sh:65-66` has the same shape
#     from the other side: `awk` on an absent ledger prints `0.000`, and an empty
#     `$TOTAL` interpolated into `print('YES' if $TOTAL > ...)` is a SyntaxError,
#     `OVER` comes back empty, and `[ "$OVER" = "YES" ]` is false -- fail open.
#     HERE: NO NUMBER IS EVER HANDED BACK TO A SHELL ARITHMETIC CONTEXT.  The
#     guard does its own arithmetic in Python and answers on the EXIT CODE.  The
#     caller reads the exit status, never a token it must re-parse.  That is a
#     structural fix, not a validation one: there is no arithmetic context left
#     for a malformed token to reach.
#
# -----------------------------------------------------------------------------
# WHAT IS TAKEN FROM WHERE
# -----------------------------------------------------------------------------
#   * From `a1wrt_run_unit.sh:290-305` -- the PRIMARY limb: any read or parse
#     failure yields `UNMEASURED`, and `UNMEASURED` REFUSES.  Never `0.0`.
#   * From `d6rf_chain_driver.sh` -- ONLY the projection arithmetic:
#     PROJ = SPENT + THIS ARM'S CAP, tested BEFORE the arm launches.  Spend-to-date
#     compared AFTER an arm (d19t's `CHECKED AFTER EVERY ARM`) buys the overrun
#     first and reports it second.
#   * NOT taken from either: the per-arm runaway guard.  `d15_run_arm.sh:400-417`
#     and `d6rf_run_arm.sh:717-734` set `CEILING = 4 x CAP` / `3 x CAP` and label
#     it `D4S_RUNAWAY_GUARD arm=` / `D6RF_RUNAWAY_GUARD arm=`.  That is a
#     SINGLE-ARM runaway stop watching this arm's own core-min, it is correctly
#     named as one, and it is a DIFFERENT INSTRUMENT from a cumulative item
#     ceiling.  This file does not replace it and does not compete with it.
#
# -----------------------------------------------------------------------------
# SPEND IS READ FROM THE LEDGER ON DISK, NEVER FROM AN IN-PROCESS ACCUMULATOR.
# -----------------------------------------------------------------------------
#   Measured: A1ZE fired twice, 6 min 25 s apart, and fire 2 started its
#   accumulator at zero -- blind to fire 1's 0.7 core-min.  A process-local total
#   is a statement about one invocation, not about the item.  Every call here
#   re-reads the file.
#
# -----------------------------------------------------------------------------
# THE PLANTED-ZERO LIMB, WHICH IS THE ONE NEITHER ANCESTOR HAS
# -----------------------------------------------------------------------------
#   A reader that matches ZERO spend rows while the ledger CONTAINS lines
#   carrying the spend field is a reader that cannot see the non-zero that is
#   there -- a row-prefix drift, a renamed field, a ledger from another item.
#   That is precisely rule 3's case, and it returns `UNMEASURED`, not `0.000`.
#
# -----------------------------------------------------------------------------
# HOW A LAUNCHER CALLS IT -- the ONLY correct call form
# -----------------------------------------------------------------------------
#     GUARD="$REPO/cases/dafoam/_common/item_ceiling_guard.py"
#     python3 "$GUARD" --check \
#         --ledger "$BASE/ledger.txt" --cap "$CAP" --ceiling "$ITEM_CEILING" \
#         --row-prefix 'ARM=' --label "$ITEM"
#     rc=$?
#     [ "$rc" -eq 0 ] || { echo "chain=ABORT reason=item_ceiling rc=$rc"; exit "$rc"; }
#
#   The caller branches on `$rc` and NOTHING ELSE.  It must not capture stdout
#   into a variable and re-test it arithmetically -- doing so re-creates defect
#   (3) outside this file.  Exit codes: 0 = WITHIN_CEILING (proceed),
#   65 = REFUSED (UNMEASURED or OVER_CEILING), 64 = usage error (also refuses).
#
#   The three state tokens `WITHIN_CEILING` / `OVER_CEILING` / `UNMEASURED` are
#   GUARD STATES about a budget, not gate verdicts.  They are deliberately
#   disjoint from CLAUDE.md rule 1's verdict vocabulary so a reader can never
#   mistake a budget refusal for a graded result.
#
#   NO COMPUTE.  This file launches nothing and never has.
#
# Provenance: written 2026-09-04 for the dafoam family.  Drives, not asserts:
# `--selftest` exercises every limb against real files on disk and prints an
# `EXERCISED-*` line for each.  `ast.Assert` count in this file is 0, and the
# selftest re-derives that count from this file's own source rather than
# claiming it.
# =============================================================================

import argparse
import ast
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

STATE_WITHIN = "WITHIN_CEILING"
STATE_OVER = "OVER_CEILING"
STATE_UNMEASURED = "UNMEASURED"

RC_OK = 0
RC_REFUSED = 65
RC_USAGE = 64

# A finite, non-negative decimal, ANCHORED, with an optional exponent.
# re.ASCII so `\d` cannot match a non-ASCII digit.
# Accepts:  0  12  1.5  .5  3.  1.5e2  1E-3  +2.0e+1
# Rejects:  1.2.3  ''  nan  inf  0x10  1_000  1,5  -1  12abc  1e  1e+
_DECIMAL = re.compile(r"^\+?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$", re.ASCII)


def parse_decimal(token):
    """Whole-token validation.  Returns a float, or None if the token is not a
    finite non-negative decimal.  The token is never partially consumed."""
    if token is None:
        return None
    if not isinstance(token, str):
        return None
    if _DECIMAL.match(token) is None:
        return None
    try:
        value = float(token)
    except ValueError:
        return None
    if not math.isfinite(value):
        return None
    if value < 0.0:
        return None
    return value


def read_spend(ledger_path, row_prefix="ARM=", field="core_min"):
    """Read cumulative spend FROM DISK.

    Returns (state, spent, rows_counted, lines_with_field_not_counted, why).
      state is STATE_UNMEASURED, or None meaning 'measured, spent is a float'.

    Every failure mode collapses to UNMEASURED.  There is no path here that
    returns 0.0 because something could not be read."""
    # Field token captured WHOLE.  `\S+` runs to the next whitespace, so a
    # malformed `1.2.3` arrives entire and is rejected entire.
    pattern = re.compile(
        r"(?:^|\s)" + re.escape(field) + r"=(\S+)", re.ASCII)

    if not os.path.exists(ledger_path):
        return (STATE_UNMEASURED, None, 0, 0,
                "ledger does not exist: %s" % ledger_path)
    try:
        handle = open(ledger_path, "r", errors="replace")
    except OSError as exc:
        return (STATE_UNMEASURED, None, 0, 0,
                "ledger could not be opened (%s): %s"
                % (exc.__class__.__name__, ledger_path))

    total = 0.0
    rows = 0
    field_lines_uncounted = 0
    try:
        with handle:
            for lineno, line in enumerate(handle, 1):
                match = pattern.search(line)
                if match is None:
                    continue
                if not line.startswith(row_prefix):
                    # The field is present on a line this reader does not count.
                    # Tracked, because rows == 0 with this non-zero is rule 3's
                    # blind reader.
                    field_lines_uncounted += 1
                    continue
                value = parse_decimal(match.group(1))
                if value is None:
                    return (STATE_UNMEASURED, None, rows, field_lines_uncounted,
                            "line %d carries a %s token that is not a finite "
                            "non-negative decimal: %r -- the whole read is "
                            "UNMEASURED, because summing the remaining rows "
                            "would under-count by an unknown amount"
                            % (lineno, field, match.group(1)))
                total += value
                rows += 1
    except OSError as exc:
        return (STATE_UNMEASURED, None, rows, field_lines_uncounted,
                "ledger became unreadable while being read (%s)"
                % exc.__class__.__name__)

    if rows == 0 and field_lines_uncounted > 0:
        return (STATE_UNMEASURED, None, rows, field_lines_uncounted,
                "0 rows matched prefix %r, but %d line(s) carry a %s= token. "
                "A reader that cannot see the non-zero that is present reports "
                "UNMEASURED, never 0.000 (CLAUDE.md rule 3)"
                % (row_prefix, field_lines_uncounted, field))

    return (None, total, rows, field_lines_uncounted, "")


def classify(ledger_path, cap, ceiling, row_prefix="ARM=", field="core_min"):
    """The whole guard.  Returns (state, detail_dict).  Arithmetic happens HERE,
    in Python, on values already validated whole.  Nothing numeric is returned
    for a caller to evaluate."""
    detail = {
        "ledger": ledger_path,
        "cap": cap,
        "ceiling": ceiling,
        "row_prefix": row_prefix,
        "field": field,
        "spent": None,
        "proj": None,
        "rows": 0,
        "uncounted": 0,
        "why": "",
    }
    state, spent, rows, uncounted, why = read_spend(ledger_path, row_prefix, field)
    detail["rows"] = rows
    detail["uncounted"] = uncounted
    if state == STATE_UNMEASURED:
        detail["why"] = why
        return STATE_UNMEASURED, detail

    detail["spent"] = spent
    proj = spent + cap
    detail["proj"] = proj
    if proj > ceiling:
        detail["why"] = (
            "%.3f core-min already spent + this arm's %.3f cap = %.3f core-min "
            "projected, over the registered %.3f ceiling. The overrun is "
            "refused BEFORE the arm; it does not get a new budget "
            "(CLAUDE.md rule 12)." % (spent, cap, proj, ceiling))
        return STATE_OVER, detail
    detail["why"] = (
        "%.3f spent + %.3f cap = %.3f <= ceiling %.3f, over %d ledger row(s)."
        % (spent, cap, proj, ceiling, rows))
    return STATE_WITHIN, detail


def emit(state, detail, label):
    def num(x):
        return "UNMEASURED" if x is None else "%.3f" % x
    sys.stdout.write(
        "ITEM_CEILING label=%s state=%s spent_core_min=%s cap_core_min=%.3f "
        "proj_core_min=%s ceiling_core_min=%.3f rows=%d uncounted_field_lines=%d\n"
        % (label, state, num(detail["spent"]), detail["cap"],
           num(detail["proj"]), detail["ceiling"], detail["rows"],
           detail["uncounted"]))
    if state != STATE_WITHIN:
        sys.stdout.write("ITEM_CEILING REFUSED: %s\n" % detail["why"])
    else:
        sys.stdout.write("ITEM_CEILING OK: %s\n" % detail["why"])
    sys.stdout.flush()


# =============================================================================
# SELFTEST -- every limb DRIVEN against real files on disk.
# No `assert`.  Each check compares an observed state against an expected one
# and records a failure explicitly.
# =============================================================================

class Driver(object):
    def __init__(self):
        self.failures = []
        self.exercised = []

    def check(self, name, observed, expected):
        ok = (observed == expected)
        self.exercised.append(name)
        sys.stdout.write("EXERCISED-%-26s observed=%-14s expected=%-14s %s\n"
                         % (name, observed, expected, "OK" if ok else "MISMATCH"))
        if not ok:
            self.failures.append("%s: observed %s, expected %s"
                                 % (name, observed, expected))
        return ok

    def note(self, name, text):
        self.exercised.append(name)
        sys.stdout.write("EXERCISED-%-26s %s\n" % (name, text))


def write_ledger(path, lines):
    with open(path, "w") as fh:
        for line in lines:
            fh.write(line + "\n")


def selftest():
    drv = Driver()
    tmp = tempfile.mkdtemp(prefix="item_ceiling_guard_selftest_")
    sys.stdout.write("SELFTEST item_ceiling_guard.py  workdir=%s\n" % tmp)
    sys.stdout.write("SELFTEST euid=%d (mode-000 limb needs a non-root euid)\n"
                     % os.geteuid())
    sys.stdout.write("-" * 78 + "\n")
    try:
        # -- 0. THE PLANTED CONTROL.  The reader is shown able to see a NON-ZERO
        #       before any zero or any refusal in this file is believed.
        plant = os.path.join(tmp, "plant.txt")
        write_ledger(plant, ["ARM=F_mp rc=0 core_min=12.345 note=planted"])
        state, det = classify(plant, cap=1.0, ceiling=1000.0)
        seen = ("%.3f" % det["spent"]) if det["spent"] is not None else "NONE"
        drv.check("PLANT-NONZERO-VISIBLE", seen, "12.345")

        # -- 1. LEDGER ABSENT.  d6rf and d19t return 0.000 here; a1wrt returns
        #       0.0 here.  This must be UNMEASURED.
        absent = os.path.join(tmp, "no_such_ledger.txt")
        state, det = classify(absent, cap=100.0, ceiling=480.0)
        drv.check("LEDGER-ABSENT", state, STATE_UNMEASURED)

        # -- 2. LEDGER UNREADABLE (mode 000).
        locked = os.path.join(tmp, "locked.txt")
        write_ledger(locked, ["ARM=F_mp rc=0 core_min=100.0"])
        os.chmod(locked, 0o000)
        really_unreadable = not os.access(locked, os.R_OK)
        if really_unreadable:
            state, det = classify(locked, cap=100.0, ceiling=480.0)
            drv.check("LEDGER-UNREADABLE-000", state, STATE_UNMEASURED)
        else:
            drv.note("LEDGER-UNREADABLE-000",
                     "NOT EXERCISED: this euid can still read a mode-000 file, "
                     "so the limb was not driven and is not claimed.")
        os.chmod(locked, 0o600)

        # -- 3. MALFORMED TOKEN BESIDE A REAL VALUE.
        mixed = os.path.join(tmp, "mixed.txt")
        write_ledger(mixed, [
            "ARM=REF_off rc=0 core_min=100.0 wall_s=600 ranks=10",
            "ARM=F_mp rc=0 core_min=1.2.3 wall_s=700 ranks=10",
        ])
        state, det = classify(mixed, cap=100.0, ceiling=480.0)
        drv.check("MALFORMED-TOKEN-REFUSES", state, STATE_UNMEASURED)

        #    ...and the CONTRAST, so the repair is measured and not asserted.
        #    These two ancestors fail DIFFERENTLY on the same input, which is
        #    only visible by running them:
        #      d6rf's `[0-9.]+` has a LITERAL dot in the class -> captures
        #      `1.2.3` whole -> float() raises -> $SPENT empty -> fail open.
        #      a1wrt's `[0-9]+\.?[0-9]*` allows at most one dot -> captures
        #      `1.2` -> NO exception -> silent under-count, UNMEASURED never fires.
        row = "ARM=F_mp rc=0 core_min=1.2.3 wall_s=700"
        permissive_d6rf = re.search(r"\bcore_min=([0-9.]+)", row)
        permissive_a1wrt = re.search(r"\bcore_min=([0-9]+\.?[0-9]*)", row)
        drv.check("CONTRAST-D6RF-REGEX", permissive_d6rf.group(1), "1.2.3")
        d6rf_throws = "no"
        try:
            float(permissive_d6rf.group(1))
        except ValueError:
            d6rf_throws = "yes"
        drv.check("CONTRAST-D6RF-FLOAT-THROWS", d6rf_throws, "yes")
        drv.check("CONTRAST-A1WRT-REGEX", permissive_a1wrt.group(1), "1.2")
        a1wrt_throws = "no"
        try:
            float(permissive_a1wrt.group(1))
        except ValueError:
            a1wrt_throws = "yes"
        drv.check("CONTRAST-A1WRT-FLOAT-THROWS", a1wrt_throws, "no")
        drv.check("WHOLE-TOKEN-CAPTURED",
                  re.search(r"(?:^|\s)core_min=(\S+)",
                            "ARM=F_mp rc=0 core_min=1.2.3 wall_s=700").group(1),
                  "1.2.3")

        # -- 4. SCIENTIFIC NOTATION IS A LEGITIMATE VALUE AND IS ACCEPTED.
        #       A validator that refuses everything is not a validator.
        sci = os.path.join(tmp, "sci.txt")
        write_ledger(sci, [
            "ARM=A rc=0 core_min=1.5e2",     # 150.0
            "ARM=B rc=0 core_min=2.5E-1",    #   0.25
            "ARM=C rc=0 core_min=.5",        #   0.5
            "ARM=D rc=0 core_min=3.",        #   3.0
        ])
        state, det = classify(sci, cap=1.0, ceiling=1000.0)
        drv.check("SCIENTIFIC-ACCEPTED", state, STATE_WITHIN)
        drv.check("SCIENTIFIC-SUMMED", "%.3f" % det["spent"], "153.750")

        # -- 5. PROJECTION OVER THE CEILING, REFUSED BEFORE THE ARM.
        over = os.path.join(tmp, "over.txt")
        write_ledger(over, [
            "ARM=REF_off rc=0 core_min=190.0",
            "ARM=F_mp rc=0 core_min=200.0",
        ])
        state, det = classify(over, cap=100.0, ceiling=480.0)
        drv.check("PROJECTION-OVER-CEILING", state, STATE_OVER)
        drv.check("PROJECTION-ARITHMETIC", "%.3f" % det["proj"], "490.000")

        # -- 6. EXACTLY AT THE CEILING IS WITHIN IT (refusal is on `>`).
        exact = os.path.join(tmp, "exact.txt")
        write_ledger(exact, [
            "ARM=REF_off rc=0 core_min=190.0",
            "ARM=F_mp rc=0 core_min=190.0",
        ])
        state, det = classify(exact, cap=100.0, ceiling=480.0)
        drv.check("EXACTLY-AT-CEILING", state, STATE_WITHIN)
        drv.check("EXACTLY-AT-CEILING-PROJ", "%.3f" % det["proj"], "480.000")

        # -- 7. THE BLIND READER.  Field present, prefix never matches.
        #       A reader that cannot see the non-zero that is there says so.
        blind = os.path.join(tmp, "blind.txt")
        write_ledger(blind, [
            "UNIT=A1WRT rc=0 core_min=300.0",
            "UNIT=A1WRT rc=0 core_min=150.0",
        ])
        state, det = classify(blind, cap=100.0, ceiling=480.0, row_prefix="ARM=")
        drv.check("BLIND-READER-REFUSES", state, STATE_UNMEASURED)
        drv.check("BLIND-READER-SAW-LINES", str(det["uncounted"]), "2")
        #       ...and with the prefix the ledger actually uses, it measures.
        state, det = classify(blind, cap=100.0, ceiling=600.0, row_prefix="UNIT=")
        drv.check("BLIND-READER-PREFIX-FIX", "%.3f" % det["spent"], "450.000")

        # -- 8. EMPTY BUT PRESENT LEDGER IS A REAL ZERO, AND IS MEASURED.
        #       This is the case the UNMEASURED limb must NOT swallow: a ledger
        #       that exists, is readable, and records nothing spent.
        empty = os.path.join(tmp, "empty.txt")
        write_ledger(empty, [])
        state, det = classify(empty, cap=100.0, ceiling=480.0)
        drv.check("EMPTY-LEDGER-IS-ZERO", state, STATE_WITHIN)
        drv.check("EMPTY-LEDGER-SPENT", "%.3f" % det["spent"], "0.000")

        # -- 9. TOKEN VALIDATION TABLE, driven whole-token.
        accept = ["0", "12", "1.5", ".5", "3.", "1.5e2", "1E-3", "+2.0e+1"]
        reject = ["1.2.3", "", "nan", "inf", "Infinity", "0x10", "1_000",
                  "1,5", "-1", "12abc", "1e", "1e+", "None", "  "]
        bad_accept = [t for t in accept if parse_decimal(t) is None]
        bad_reject = [t for t in reject if parse_decimal(t) is not None]
        drv.check("VALIDATOR-ACCEPTS-LEGIT", str(bad_accept), "[]")
        drv.check("VALIDATOR-REJECTS-JUNK", str(bad_reject), "[]")

        # -- 10. THE FAIL-OPEN THAT DEFEATED THE ANCESTOR, DRIVEN SIDE BY SIDE.
        #        d6rf's uncaught ValueError leaves $SPENT empty, and
        #        `( $SPENT + $ACAP )` is then Python's UNARY PLUS on the cap.
        legacy_proj = subprocess.run(
            [sys.executable, "-c", "print('%.3f' % ( + 480.0 ))"],
            capture_output=True, text=True)
        drv.check("LEGACY-UNARY-PLUS-PASSES",
                  legacy_proj.stdout.strip(), "480.000")
        #        The same ledger through THIS guard:
        trap = os.path.join(tmp, "trap.txt")
        write_ledger(trap, [
            "ARM=REF_off rc=0 core_min=100.0",
            "ARM=F_mp rc=0 core_min=1.2.3",
        ])
        state, det = classify(trap, cap=480.0, ceiling=480.0)
        drv.check("GUARD-REFUSES-SAME-LEDGER", state, STATE_UNMEASURED)

        # -- 11. THE CLI CONTRACT: the caller reads an EXIT CODE, not a token.
        here = os.path.abspath(__file__)
        run_ok = subprocess.run(
            [sys.executable, here, "--check", "--ledger", exact,
             "--cap", "100.0", "--ceiling", "480.0", "--label", "SELFTEST"],
            capture_output=True, text=True)
        drv.check("CLI-RC-WITHIN", str(run_ok.returncode), str(RC_OK))
        run_over = subprocess.run(
            [sys.executable, here, "--check", "--ledger", over,
             "--cap", "100.0", "--ceiling", "480.0", "--label", "SELFTEST"],
            capture_output=True, text=True)
        drv.check("CLI-RC-OVER", str(run_over.returncode), str(RC_REFUSED))
        run_unmeas = subprocess.run(
            [sys.executable, here, "--check", "--ledger", absent,
             "--cap", "100.0", "--ceiling", "480.0", "--label", "SELFTEST"],
            capture_output=True, text=True)
        drv.check("CLI-RC-UNMEASURED", str(run_unmeas.returncode),
                  str(RC_REFUSED))
        #        A malformed CAP or CEILING from the caller refuses too -- the
        #        guard's own inputs get the same whole-token validation.
        run_badcap = subprocess.run(
            [sys.executable, here, "--check", "--ledger", exact,
             "--cap", "1.2.3", "--ceiling", "480.0", "--label", "SELFTEST"],
            capture_output=True, text=True)
        drv.check("CLI-RC-BAD-CAP", str(run_badcap.returncode), str(RC_USAGE))

        # -- 12. SPEND IS RE-READ FROM DISK ON EVERY CALL, not accumulated
        #        in-process.  A1ZE fire 2 started at zero, blind to fire 1's
        #        0.7 core-min.  Two calls, one process, ledger grows between.
        refire = os.path.join(tmp, "refire.txt")
        write_ledger(refire, ["ARM=A rc=0 core_min=0.700"])
        _, det_fire1 = classify(refire, cap=1.0, ceiling=1000.0)
        with open(refire, "a") as fh:
            fh.write("ARM=B rc=0 core_min=0.300\n")
        _, det_fire2 = classify(refire, cap=1.0, ceiling=1000.0)
        drv.check("REFIRE-SEES-FIRE1", "%.3f" % det_fire1["spent"], "0.700")
        drv.check("REFIRE-SEES-BOTH", "%.3f" % det_fire2["spent"], "1.000")

        # -- 13. ast.Assert count RE-DERIVED from this file's own source.
        with open(here, "r") as fh:
            tree = ast.parse(fh.read(), filename=here)
        n_assert = sum(1 for node in ast.walk(tree)
                       if isinstance(node, ast.Assert))
        drv.check("AST-ASSERT-COUNT", str(n_assert), "0")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    sys.stdout.write("-" * 78 + "\n")
    sys.stdout.write("SELFTEST limbs exercised: %d\n" % len(drv.exercised))
    if drv.failures:
        sys.stdout.write("SELFTEST RESULT: GATE FAIL -- %d mismatch(es)\n"
                         % len(drv.failures))
        for f in drv.failures:
            sys.stdout.write("  %s\n" % f)
        return 1
    sys.stdout.write("SELFTEST RESULT: PASS -- every limb driven, "
                     "no mismatches, ast.Assert 0\n")
    return 0


def main(argv):
    parser = argparse.ArgumentParser(
        prog="item_ceiling_guard.py",
        description="Prospective cumulative item-ceiling guard. Refuses BEFORE "
                    "the arm. Any unreadable or unparseable ledger is "
                    "UNMEASURED and refuses; it is never 0.")
    parser.add_argument("--check", action="store_true",
                        help="run the guard and answer on the exit code")
    parser.add_argument("--selftest", action="store_true",
                        help="drive every limb against real files on disk")
    parser.add_argument("--ledger", help="path to the item's ledger.txt")
    parser.add_argument("--cap", help="THIS arm's registered cap, core-min")
    parser.add_argument("--ceiling", help="the item's registered ceiling, core-min")
    parser.add_argument("--row-prefix", default="ARM=",
                        help="only lines starting with this are spend rows "
                             "(default 'ARM=')")
    parser.add_argument("--field", default="core_min",
                        help="the spend field name (default 'core_min')")
    parser.add_argument("--label", default="UNLABELLED",
                        help="item label, echoed into the guard line")
    args = parser.parse_args(argv)

    if args.selftest and args.check:
        sys.stderr.write("ITEM_CEILING USAGE: --selftest and --check are "
                         "separate invocations.\n")
        return RC_USAGE
    if args.selftest:
        return selftest()
    if not args.check:
        sys.stderr.write("ITEM_CEILING USAGE: pass --check or --selftest.\n")
        return RC_USAGE

    missing = [n for n, v in (("--ledger", args.ledger), ("--cap", args.cap),
                              ("--ceiling", args.ceiling)) if v is None]
    if missing:
        sys.stderr.write("ITEM_CEILING USAGE: --check requires %s.\n"
                         % ", ".join(missing))
        return RC_USAGE

    # The guard's OWN inputs get the same whole-token validation as the ledger.
    # A cap or ceiling that arrived malformed from a shell would otherwise be
    # the fail-open reintroduced at the front door.
    cap = parse_decimal(args.cap)
    ceiling = parse_decimal(args.ceiling)
    if cap is None or ceiling is None:
        sys.stderr.write(
            "ITEM_CEILING USAGE: --cap %r and --ceiling %r must each be a "
            "finite non-negative decimal, validated WHOLE. REFUSED.\n"
            % (args.cap, args.ceiling))
        return RC_USAGE

    state, detail = classify(args.ledger, cap, ceiling,
                             row_prefix=args.row_prefix, field=args.field)
    emit(state, detail, args.label)
    return RC_OK if state == STATE_WITHIN else RC_REFUSED


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
