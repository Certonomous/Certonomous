#!/usr/bin/env python3
r"""
CASE PROTOCOL -- STAGE 1 EXIT GATE.  "Nothing below is run until the freeze
check passes."

THIS HOOK MAY REFUSE, AND IT IS THE ONLY THING IN THIS TEAM'S HAND THAT MAY.
D539 reserves the ADDING of a gate on lab process to Sanaa exactly as it
reserves retiring one.  That reservation is SATISFIED here and only here:
Sanaa ordered this gate herself, in her own words, as stage 1 of the CASE
PROTOCOL.  It is not a lab-invented refusal.  Nothing else this lane touches
acquired a right to refuse from this file.

docs/charters/CASE_PROTOCOL_CHARTER.md IS NOT AT HEAD AND NOT ON DISK AT THIS
WRITE.  This script is built to the spec in the dispatching brief; THE CHARTER
IS AUTHORITATIVE WHEN IT LANDS and this file must be re-read against it then.
No clause below is quoted from that charter -- none of it has been read.

--------------------------------------------------------------------------
WHAT IT DECIDES
--------------------------------------------------------------------------
Given a case directory and its registration, may stage 2 launch?  PASS (exit 0)
only when the freeze is PROVEN.  Everything else is REFUSE (exit 2).

The proof is delegated to the frozen instrument, scripts/check_comparator_freeze.py,
invoked as:

    check_comparator_freeze.py --repo <repo> --registration <abs reg> \
                               --restrict-to-registration

WHY THOSE FLAGS.  --registration adds the COVERAGE / IDENTITY / CURRENCY pin
limbs; without it the run judges a name-pattern population that is nobody's
registration.  --restrict-to-registration is NOT optional here and is not
leniency: that script's own docstring records the measurement -- TWELVE rows
belonging to other campaigns are UNFROZEN, so the unrestricted process exits 3
however clean the registered set is, and a gate phrased "the freeze check
exits 0" would be UNSATISFIABLE for every case in this repository.  A gate no
case can pass is not a gate, it is a stop.  Under restriction the exit code is
earned by the pinned set alone, and that script states in as many words that
the mode judges, re-judges, suppresses and changes NOTHING outside that set.

GATED ON THE EXIT CODE, NEVER ON A STDOUT SUBSTRING.  The frozen script argues
this at length against itself: a run that dies before printing its pass line
leaves no substring to fail on, and a grep for a pass phrase cannot tell
"printed and true" from "printed and then refused".  Stdout is read here for
ONE purpose only -- an inventory cross-check of which pins the instrument
actually printed a row for -- and never to decide PASS.

FAIL CLOSED.  Missing registration, missing case directory, not a git
repository, timeout, an exception, an unexpected exit code, or an inventory
that does not agree with itself: all REFUSE.  A check that did not reach its
subject has not passed; it has not run.

A REFUSAL CARRIES ITS REASON.  When this hook refuses AFTER the frozen
instrument has run, that instrument's captured stdout and stderr are printed
UNCONDITIONALLY.  --show-check-output is no longer needed to learn why a
refusal happened -- it was previously the only way, so the board's standing
mitigation was to make the flag mandatory in every documented invocation, and
that mandate is retired.  Passing the flag AND refusing prints the account
once, not twice.  On the PASS path the flag keeps exactly its old meaning.  The
argument for flushing at refuse() rather than at each refusal site, and the
statement that this can move no verdict, sit above refuse() itself.

--------------------------------------------------------------------------
WHY THIS HOOK IS NOT JUST A WRAPPER -- THE THREE KNOWN DEFECTS
--------------------------------------------------------------------------
check_comparator_freeze.py carries three defects this team recorded (D597,
D600).  They are ON SANAA'S DESK, UNREPAIRED, and that file is FROZEN: it is
NOT repaired here.  This hook reports AROUND it.

  (a) PIN_PATH at :261 is `\.(?:py|sh)` only.  A registration pinning a .json
      manifest, a .csv reference or a .md cross-pin has those paths SILENTLY
      INVISIBLE -- they never enter `pins`, so COVERAGE cannot report them
      missing and the instrument cannot fail on them.  A hook that merely
      relayed "freeze check passed" would certify a case whose DATA pins were
      never judged by anything.
  (b) the coverage figure prints "N of N pinned EXECUTABLE(s)" -- a count that
      cannot name its own exclusions.  N of N is true and uninformative when
      the excluded rows were removed before counting.
  (c) a pin written as a BARE FILENAME is read as repo-relative and reports
      PIN-ABSENT even when the file is present and clean elsewhere.

THE INDEPENDENT INVENTORY.  This hook parses the registration for pin rows
with a recogniser that differs from the frozen one in EXACTLY ONE DIMENSION --
the path suffix.  The strike-span handling and the 40-hex blob regex are
IMPORTED FROM THE FROZEN MODULE ITSELF rather than retyped, so a struck pin
cannot become a phantom finding and the blob rule cannot drift.  A pin row is
a table row carrying a 40-hex blob and a backticked path of ANY suffix.  The
difference between that set and the set the instrument actually judged is
printed explicitly:

    PINS NOT SEEN BY THE FROZEN CHECKER: 2 (verification/campaign/X.json, ...)

The set the instrument judged is taken from the frozen module's OWN
registered_pins(), not re-derived, and is cross-checked against the pin rows
it printed.  Disagreement is a REFUSAL: if the inventory cannot be established
the hook does not know what was judged.

UNSEEN PINS: WARN BY DEFAULT, REFUSE UNDER --refuse-unseen-pins.  See the flag
help.  Sanaa ordered a gate on THE FREEZE CHECK PASSING; refusing on a defect
the lab discovered afterwards is a SECOND gate with a lab-chosen threshold,
and D539 reserves that.  The count is therefore carried in the one-line status
so a stage-6 report cannot omit it, and the stricter reading is one flag away.

--------------------------------------------------------------------------
WHAT THIS HOOK CANNOT SEE
--------------------------------------------------------------------------
  * whether an unseen .json/.csv/.md pin is CLEAN.  It reports that NOTHING
    judged it.  Reporting a gap is not closing it.
  * anything the frozen instrument cannot see -- its own "CANNOT SEE" list
    passes straight through, unweakened and unimproved.
  * whether the registration was frozen before compute.  That is the freeze
    check's subject, and this hook only decides whether that check was allowed
    to reach it.

NO BARE `assert` ANYWHERE IN THIS FILE, selftest included: `python3 -O` strips
them, and this team docketed exactly that failure today (D594, L-332).  Every
check is `if not cond: sys.exit(...)` or an explicit counted comparison.

Exit: 0 stage 2 MAY launch; 2 REFUSED.
"""
import argparse
import importlib.util
import os
import re
import subprocess
import sys

EXIT_PASS, EXIT_REFUSE = 0, 2
FROZEN_REL = os.path.join("scripts", "check_comparator_freeze.py")

# The WIDER recogniser -- see THE INDEPENDENT INVENTORY above.  Differs from
# the frozen PIN_PATH in the suffix alone.  The suffix must START WITH A LETTER
# so that a backticked number in a table cell (`0.5`) or a version (`v1.42`)
# cannot become a phantom pin, and the stem must be at least two characters.
WIDE_PIN_PATH = re.compile(
    r"`([A-Za-z0-9_][A-Za-z0-9_./+-]{1,200}\.[A-Za-z][A-Za-z0-9_+-]{0,11})`")
# a printed pin row: "  {status:16s} {path}   [{covered}]"
PRINTED_PIN_ROW = re.compile(r"^ {2}(PIN-[A-Z-]+)\s+(\S+)\s+\[", re.M)
PIN_BLOCK_HDR = "REGISTRATION PINS --"


def load_frozen(path):
    """Import the frozen checker as a module so its OWN recognisers can be
    reused rather than retyped.  Bytecode writing is disabled: a stale
    __pycache__ has inverted this lab's mutation tests before, and importing a
    repo script must not leave clutter beside it."""
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("_frozen_freeze_check", path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        return None
    return mod


def wide_pins(reg_text, strike_re, blob_re):
    """Every table row carrying a 40-hex blob and a backticked path of ANY
    suffix.  Struck spans are dropped FIRST, using the frozen module's own
    span regex, so a formally superseded pin cannot be reported as unseen."""
    src = strike_re.sub(lambda m: "\n" * m.group(0).count("\n"), reg_text)
    found = set()
    for line in src.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        if not blob_re.findall(line):
            continue
        for p in WIDE_PIN_PATH.findall(line):
            found.add(p)
    return found


def bare_filename_pins(repo, paths):
    """Defect (c): a pin with no directory component is read as repo-relative.
    Report the ones that are absent at the repo root but DO exist elsewhere in
    the tracked tree -- present and clean, reported PIN-ABSENT."""
    bare = sorted(p for p in paths if "/" not in p)
    if not bare:
        return []
    r = subprocess.run(["git", "-C", repo, "ls-files"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return []
    tracked = r.stdout.splitlines()
    out = []
    for b in bare:
        if os.path.isfile(os.path.join(repo, b)):
            continue
        hits = [t for t in tracked if os.path.basename(t) == b]
        if hits:
            out.append((b, hits[0]))
    return out


# --------------------------------------------------------------------------
# THE REFUSAL CARRIES ITS REASON -- the captured account of the frozen
# instrument, and why it is flushed HERE and not at each refusal site.
#
# This hook gates on the frozen instrument's EXIT CODE, but that instrument
# also PRINTS why it refused.  That text was captured and then discarded unless
# --show-check-output happened to be passed, so a REFUSAL showed the operator a
# one-line status and threw away the only account of its own cause.  The
# standing mitigation was to make --show-check-output mandatory in every
# documented invocation; this holder retires that mandate.
#
# WHY A MODULE-LEVEL HOLDER FLUSHED BY refuse(), AND NOT A PRINT PER SITE.
# Every refusal in this file leaves through refuse().  Flushing there reaches
# EVERY post-subprocess refusal path -- the two inventory-disagreement limbs,
# the rc limb, the strict-flag limb, the unreadable-registration limb -- AND
# every limb a later hand adds.  A per-site print covers only the sites that
# existed when it was written, and a future refusal that forgets to print its
# evidence is precisely the defect being repaired here; only the single choke
# point is immune to it.
#
# WHY IT CANNOT MOVE A VERDICT.  refuse() already ended in an unconditional
# sys.exit(EXIT_REFUSE).  This adds output strictly before that call.  It reads
# no predicate, compares no rc, and returns no value that anything branches on.
# The "printed" latch makes the flush idempotent, so --show-check-output plus a
# refusal prints the account ONCE, not twice.
#
# LIMIT, STATED PLAINLY.  The holder is filled only when the subprocess
# RETURNS.  The timeout and exception refusals above it never reach it and
# print only what they already printed; recovering TimeoutExpired's partial
# output is a different change and is deliberately NOT made here.
# --------------------------------------------------------------------------
_CAPTURED = {"out": None, "err": None, "printed": False}


def capture_check_output(out, err):
    """Hold the frozen instrument's own account, immediately after it returns."""
    _CAPTURED["out"] = out
    _CAPTURED["err"] = err
    _CAPTURED["printed"] = False


def emit_captured():
    """Print the held account AT MOST ONCE.  True if it printed here; False if
    nothing is held (the subprocess never returned) or it was already printed."""
    if _CAPTURED["printed"]:
        return False
    if _CAPTURED["out"] is None and _CAPTURED["err"] is None:
        return False
    _CAPTURED["printed"] = True
    print("STAGE1 the frozen instrument's own account follows "
          "(its stdout, then its stderr):")
    print(_CAPTURED["out"] or "")
    if _CAPTURED["err"]:
        print(_CAPTURED["err"])
    return True


def status_line(verdict, case_id, judged, unseen, rc, reason):
    print(f"STAGE1 FREEZE {verdict} case={case_id} pins_judged={judged} "
          f"pins_unseen={unseen} rc={rc} reason={reason}")


def refuse(case_id, judged, unseen, rc, reason):
    emit_captured()  # REFUSAL-REASON FLUSH -- selftest ARM B mutates this line
    status_line("REFUSE", case_id, judged, unseen, rc, reason)
    sys.exit(EXIT_REFUSE)


def run_gate(a):
    case_id = a.case_id or (os.path.basename(os.path.normpath(a.case))
                            if a.case else "-")

    # ---- fail-closed preconditions.  rc=n/a means THE CHECK NEVER RAN -------
    if not a.case or not os.path.isdir(a.case):
        refuse(case_id, 0, 0, "n/a", "case-directory-missing")
    repo = a.repo
    if not repo:
        r = subprocess.run(["git", "-C", a.case, "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            refuse(case_id, 0, 0, "n/a", "case-not-in-a-git-repo")
        repo = r.stdout.strip()
    repo = os.path.abspath(repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        refuse(case_id, 0, 0, "n/a", "repo-is-not-a-git-repository")

    reg = os.path.abspath(a.registration) if a.registration else ""
    if not reg or not os.path.isfile(reg):
        refuse(case_id, 0, 0, "n/a", "registration-missing")

    frozen = os.path.join(repo, FROZEN_REL)
    if not os.path.isfile(frozen):
        refuse(case_id, 0, 0, "n/a", "frozen-checker-missing")
    mod = load_frozen(frozen)
    if mod is None:
        refuse(case_id, 0, 0, "n/a", "frozen-checker-unimportable")
    for attr in ("registered_pins", "STRIKE_SPAN", "PIN_BLOB", "PIN_PATH"):
        if not hasattr(mod, attr):
            refuse(case_id, 0, 0, "n/a", f"frozen-checker-lacks-{attr}")

    # ---- LIMB 1: the frozen instrument, gated on its EXIT CODE --------------
    argv = [sys.executable, frozen, "--repo", repo,
            "--registration", reg, "--restrict-to-registration"]
    print("STAGE1 invoking the frozen instrument:")
    print("  " + " ".join(argv))
    try:
        r = subprocess.run(argv, capture_output=True, text=True,
                           timeout=a.timeout)
    except subprocess.TimeoutExpired:
        refuse(case_id, 0, 0, "timeout", "frozen-check-timed-out")
    except Exception as exc:                      # fail closed, never silent
        print(f"  the frozen check could not be run: {exc!r}")
        refuse(case_id, 0, 0, "n/a", "frozen-check-raised")
    rc = r.returncode
    out = r.stdout or ""
    capture_check_output(out, r.stderr)   # held for EVERY refusal below
    if a.show_check_output:
        emit_captured()                   # PASS path keeps its old meaning

    # ---- LIMB 2: the independent inventory ---------------------------------
    try:
        reg_text = open(reg, errors="replace").read()
    except OSError:
        refuse(case_id, 0, 0, rc, "registration-unreadable")
    seen = mod.registered_pins(reg)               # the FROZEN recogniser itself
    if seen is None:
        seen = {}
    seen_set = set(seen)
    wide_set = wide_pins(reg_text, mod.STRIKE_SPAN, mod.PIN_BLOB)
    unseen = sorted(wide_set - seen_set)
    judged = len(seen_set)

    # cross-check the frozen module's recogniser against the rows the process
    # actually PRINTED.  Not a verdict -- an inventory integrity test.  If the
    # two disagree, this hook does not know what was judged, so it refuses.
    if PIN_BLOCK_HDR in out:
        printed = {m.group(2) for m in PRINTED_PIN_ROW.finditer(out)}
        if printed != seen_set:
            print(f"  INVENTORY DISAGREEMENT: the frozen module's recogniser "
                  f"returns {sorted(seen_set)} but the process printed rows "
                  f"for {sorted(printed)}")
            refuse(case_id, judged, len(unseen), rc, "pin-inventory-disagreement")
    elif rc == 0 and seen_set:
        print("  INVENTORY DISAGREEMENT: the run exited 0 with a non-empty pin "
              "set and printed no REGISTRATION PINS block")
        refuse(case_id, judged, len(unseen), rc, "pin-block-absent")

    print("-" * 78)
    print(f"PINS JUDGED BY THE FROZEN CHECKER: {judged}"
          + (f" ({', '.join(sorted(seen_set))})" if seen_set else ""))
    if unseen:
        shown = unseen[:8]
        tail = ", ..." if len(unseen) > len(shown) else ""
        print(f"PINS NOT SEEN BY THE FROZEN CHECKER: {len(unseen)} "
              f"({', '.join(shown)}{tail})")
        print("  cause: PIN_PATH at check_comparator_freeze.py:261 matches "
              "\\.(?:py|sh) only (defect (a), D597/D600, unrepaired and "
              "Sanaa's to repair). These paths never entered `pins`, so "
              "COVERAGE could not report them missing and NOTHING judged them.")
        print("  the 'N of N pinned executable(s)' figure above is true and "
              "cannot name its own exclusions (defect (b)); these are they.")
    else:
        print("PINS NOT SEEN BY THE FROZEN CHECKER: 0")
    for b, where in bare_filename_pins(repo, wide_set):
        print(f"BARE-FILENAME PIN: `{b}` is absent at the repo root but is "
              f"tracked at {where} -- defect (c): the frozen checker reads a "
              f"bare filename as repo-relative and reports PIN-ABSENT.")

    # ---- the verdict -------------------------------------------------------
    if rc != 0:
        reason = {2: "frozen-check-REFUSED", 3: "frozen-check-VIOLATION"}.get(
            rc, "frozen-check-unexpected-rc")
        refuse(case_id, judged, len(unseen), rc, reason)
    if unseen and a.refuse_unseen_pins:
        refuse(case_id, judged, len(unseen), rc, "unseen-pins-under-strict-flag")
    if unseen:
        print("WARNING: stage 1 passed on the pins the frozen checker could "
              "see. The unseen pins above were judged by NOTHING. Re-run with "
              "--refuse-unseen-pins to make that a refusal.")
    status_line("PASS", case_id, judged, len(unseen), rc, "freeze-proven")
    return EXIT_PASS


# --------------------------------------------------------------------------
# selftest -- BOTH ARMS, or it is not evidence
# --------------------------------------------------------------------------
def _git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args),
                          capture_output=True, text=True)


def _mkrepo(root):
    os.makedirs(root, exist_ok=True)
    subprocess.run(["git", "init", "-q", root], check=True)
    _git(root, "config", "user.email", "selftest@local")
    _git(root, "config", "user.name", "selftest")
    return root


def _write(repo, rel, body):
    p = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as fh:
        fh.write(body)
    return p


def _blob(repo, rel):
    return _git(repo, "rev-parse", f"HEAD:{rel}").stdout.strip()


def _reg_body(rows):
    lines = ["# scratch registration", "",
             "| artifact | blob |", "|---|---|"]
    for path, blob in rows:
        lines.append(f"| `{path}` | {blob} |")
    return "\n".join(lines) + "\n"


def _pyargv():
    """sys.executable PLUS the optimisation flag this process is running under.
    Without this a `python3 -O --selftest` spawns children WITHOUT -O and the
    -O arm proves nothing about the children it is testing (D594, L-332)."""
    argv = [sys.executable]
    if sys.flags.optimize == 1:
        argv.append("-O")
    elif sys.flags.optimize >= 2:
        argv.append("-OO")
    return argv


def _hook_at(script, repo, case, reg, *extra):
    """Run an arbitrary BUILD of this hook.  ARM B needs this: the control that
    makes ARM A evidence is a copy of this file with the repair removed."""
    return subprocess.run(
        _pyargv() + [script, "--repo", repo,
                     "--case", case, "--registration", reg] + list(extra),
        capture_output=True, text=True)


def _hook(repo, case, reg, *extra):
    return _hook_at(os.path.abspath(__file__), repo, case, reg, *extra)


# ARM A/B/C plants.  These two strings are emitted by the stub below and by
# NOTHING ELSE in the pipeline -- not by the real frozen instrument, not by this
# hook, not by git.  A zero (the token absent) is therefore only evidence
# because ARM A first shows the same reader seeing a non-zero (CLAUDE.md rule 3).
_PLANT_OUT = "PLANTED-FROZEN-STDOUT-a7f3c19e5b2d4086"
_PLANT_ERR = "PLANTED-FROZEN-STDERR-a7f3c19e5b2d4086"

# A stand-in for the frozen instrument.  It exits 3, so the hook refuses on the
# rc limb -- a refusal that happens strictly AFTER the subprocess returned,
# which is the exact path the repair covers.  It carries the four attributes
# run_gate() requires of the imported module; registered_pins() returns an empty
# mapping so the inventory limbs are quiet and the rc limb is the one that fires.
_STUB_FROZEN = '''#!/usr/bin/env python3
"""Selftest stub for the frozen instrument.  Prints a planted marker on stdout
and another on stderr, then exits 3."""
import re
import sys

STRIKE_SPAN = re.compile(r"~~.*?~~", re.S)
PIN_BLOB = re.compile(r"\\b[0-9a-f]{40}\\b")
PIN_PATH = re.compile(r"`([^`]+\\.(?:py|sh))`")


def registered_pins(path):
    return {}


if __name__ == "__main__":
    print("%s")
    sys.stderr.write("%s\\n")
    sys.exit(3)
''' % (_PLANT_OUT, _PLANT_ERR)

# the line refuse() carries, and what ARM B replaces it with.  Both are matched
# by an explicit counted comparison, never by a bare assert (see :105).
_ANCHOR = "    emit_captured()  # REFUSAL-REASON FLUSH"
_ANCHOR_MUT = "    pass  # MUTATED: refusal-reason flush REMOVED\n"


def selftest():
    import tempfile
    import shutil
    tmp = tempfile.mkdtemp(prefix="cp_freeze_hook_")
    fails = []

    def _check(label, got, want):
        if got != want:
            fails.append(label)
            print(f"  SELFTEST FAIL: {label}: expected {want!r}, got {got!r}")
        else:
            print(f"  {label:56s} -> {want!r}  OK")

    try:
        repo = _mkrepo(os.path.join(tmp, "r"))
        # the frozen instrument has to exist INSIDE the scratch repo, because
        # the hook resolves it relative to the repo it is judging.
        here = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "check_comparator_freeze.py")
        os.makedirs(os.path.join(repo, "scripts"), exist_ok=True)
        shutil.copy2(here, os.path.join(repo, FROZEN_REL))

        case = os.path.join(repo, "cases", "SCRATCH")
        os.makedirs(case, exist_ok=True)
        _write(repo, "verification/t/analyse_x.py",
               "#!/usr/bin/env python3\nCASE = 'SCRATCH'\nprint(CASE)\n")
        _write(repo, "verification/campaign/K0h_STAGE_MANIFEST.json",
               '{"stage": 1}\n')
        _write(repo, "cases/SCRATCH/.keep", "")
        _git(repo, "add", "--", "verification/t/analyse_x.py",
             "verification/campaign/K0h_STAGE_MANIFEST.json",
             "cases/SCRATCH/.keep", FROZEN_REL)
        _git(repo, "commit", "-q", "-m", "scratch case")
        b_py = _blob(repo, "verification/t/analyse_x.py")
        b_js = _blob(repo, "verification/campaign/K0h_STAGE_MANIFEST.json")
        _check("scratch: the pinned .py has a blob", len(b_py), 40)

        reg = os.path.join(repo, "REG.md")

        # ---- ARM 1: POSITIVE.  Committed, clean, pinned at its HEAD blob ----
        _write(repo, "REG.md", _reg_body([("verification/t/analyse_x.py", b_py)]))
        r1 = _hook(repo, case, reg)
        _check("positive arm: a clean committed pin PASSES", r1.returncode,
               EXIT_PASS)
        _check("positive arm: says PASS on the status line",
               "STAGE1 FREEZE PASS" in r1.stdout, True)
        _check("positive arm: reports one judged pin",
               "pins_judged=1" in r1.stdout, True)
        _check("positive arm: reports no unseen pin",
               "pins_unseen=0" in r1.stdout, True)

        # ---- ARM 2: NEGATIVE.  The same case, pinned file MODIFIED ----------
        _write(repo, "verification/t/analyse_x.py",
               "#!/usr/bin/env python3\nCASE = 'SCRATCH'\nprint(CASE)\n# drift\n")
        r2 = _hook(repo, case, reg)
        _check("negative arm: pin drift on disk REFUSES", r2.returncode,
               EXIT_REFUSE)
        _check("negative arm: names the frozen check's violation",
               "reason=frozen-check-VIOLATION" in r2.stdout, True)
        _check("negative arm: carries the frozen rc", "rc=3" in r2.stdout, True)
        # restore, and PROVE the refusal was the drift and not the harness
        _write(repo, "verification/t/analyse_x.py",
               "#!/usr/bin/env python3\nCASE = 'SCRATCH'\nprint(CASE)\n")
        r2b = _hook(repo, case, reg)
        _check("negative arm control: clearing the drift PASSES again",
               r2b.returncode, EXIT_PASS)

        # ---- ARM 3: DEFECT (a).  A .json pin the frozen checker cannot see --
        _write(repo, "REG.md", _reg_body([
            ("verification/t/analyse_x.py", b_py),
            ("verification/campaign/K0h_STAGE_MANIFEST.json", b_js)]))
        raw = subprocess.run(
            _pyargv() + [os.path.join(repo, FROZEN_REL), "--repo", repo,
                         "--registration", reg, "--restrict-to-registration"],
            capture_output=True, text=True)
        _check("defect(a): the FROZEN checker is clean on this registration",
               raw.returncode, 0)
        _check("defect(a): and never mentions the .json at all",
               "K0h_STAGE_MANIFEST.json" in raw.stdout, False)
        _check("defect(a): its coverage figure reads 1 of 1",
               "PIN COVERAGE: 1 of 1" in raw.stdout, True)
        r3 = _hook(repo, case, reg)
        _check("defect(a): the hook counts the .json as UNSEEN",
               "pins_unseen=1" in r3.stdout, True)
        _check("defect(a): and names it explicitly",
               "PINS NOT SEEN BY THE FROZEN CHECKER: 1 "
               "(verification/campaign/K0h_STAGE_MANIFEST.json)" in r3.stdout,
               True)
        _check("defect(a): warn is the default, so exit is PASS",
               r3.returncode, EXIT_PASS)
        r3s = _hook(repo, case, reg, "--refuse-unseen-pins")
        _check("defect(a): --refuse-unseen-pins turns it into a REFUSAL",
               r3s.returncode, EXIT_REFUSE)
        _check("defect(a): and the reason names the flag",
               "reason=unseen-pins-under-strict-flag" in r3s.stdout, True)

        # ---- ARM 4: FAIL CLOSED --------------------------------------------
        gone = os.path.join(repo, "NO_SUCH_REGISTRATION.md")
        r4 = _hook(repo, case, gone)
        _check("fail-closed: a registration that does not exist REFUSES",
               r4.returncode, EXIT_REFUSE)
        _check("fail-closed: reason is registration-missing",
               "reason=registration-missing" in r4.stdout, True)
        _check("fail-closed: rc=n/a -- the check NEVER RAN",
               "rc=n/a" in r4.stdout, True)
        r4b = _hook(repo, os.path.join(repo, "cases", "NO_SUCH_CASE"), reg)
        _check("fail-closed: a case directory that does not exist REFUSES",
               r4b.returncode, EXIT_REFUSE)
        _check("fail-closed: reason is case-directory-missing",
               "reason=case-directory-missing" in r4b.stdout, True)

        # ---- ARM 5: a registration pinning ONLY unseeable paths -------------
        # the frozen checker refuses ("pins ZERO executables"); the hook must
        # relay the refusal AND name the pins nothing judged.
        _write(repo, "REG.md", _reg_body([
            ("verification/campaign/K0h_STAGE_MANIFEST.json", b_js)]))
        r5 = _hook(repo, case, reg)
        _check("data-only registration REFUSES", r5.returncode, EXIT_REFUSE)
        _check("data-only registration reports 0 judged, 1 unseen",
               "pins_judged=0 pins_unseen=1" in r5.stdout, True)

        # ---- ARM 6: THE REFUSAL CARRIES ITS REASON -------------------------
        # A refusal that happens AFTER the subprocess returned must show the
        # frozen instrument's own account WITHOUT --show-check-output (A);
        # a build with the flush removed must NOT show it, or (A) proves
        # nothing (B); and the flag plus a refusal must print it ONCE (C).
        repo6 = _mkrepo(os.path.join(tmp, "r6"))
        case6 = os.path.join(repo6, "cases", "SCRATCH6")
        os.makedirs(case6, exist_ok=True)
        os.makedirs(os.path.join(repo6, "scripts"), exist_ok=True)
        _write(repo6, FROZEN_REL, _STUB_FROZEN)
        _write(repo6, "verification/t/analyse_y.py", "print('y')\n")
        _write(repo6, "cases/SCRATCH6/.keep", "")
        _git(repo6, "add", "--", FROZEN_REL, "verification/t/analyse_y.py",
             "cases/SCRATCH6/.keep")
        _git(repo6, "commit", "-q", "-m", "stub instrument")
        b_y = _blob(repo6, "verification/t/analyse_y.py")
        reg6 = os.path.join(repo6, "REG6.md")
        _write(repo6, "REG6.md",
               _reg_body([("verification/t/analyse_y.py", b_y)]))
        _check("ARM6 scratch: the stub repo pins a real 40-hex blob",
               len(b_y), 40)

        # ARM A -- the repair, on the unflagged refusal path
        r6a = _hook_at(os.path.abspath(__file__), repo6, case6, reg6)
        _check("ARM A: the post-subprocess refusal still REFUSES",
               r6a.returncode, EXIT_REFUSE)
        _check("ARM A: and it is the rc limb, after the subprocess returned",
               "reason=frozen-check-VIOLATION" in r6a.stdout, True)
        _check("ARM A: WITHOUT the flag, the planted STDOUT is shown",
               _PLANT_OUT in r6a.stdout, True)
        _check("ARM A: WITHOUT the flag, the planted STDERR is shown",
               _PLANT_ERR in r6a.stdout, True)

        # ARM B -- the control.  A build with the flush line removed, so ARM A
        # is shown CAPABLE OF FAILING.  The mutation is counted, not asserted.
        src = open(os.path.abspath(__file__)).read().splitlines(True)
        hits = [i for i, ln in enumerate(src) if ln.startswith(_ANCHOR)]
        _check("ARM B: the refusal-reason flush line occurs exactly once",
               len(hits), 1)
        if len(hits) != 1:
            fails.append("ARM B: cannot build the control")
        else:
            src[hits[0]] = _ANCHOR_MUT
            mut = os.path.join(tmp, "unrepaired_hook.py")
            with open(mut, "w") as fh:
                fh.write("".join(src))
            r6b = _hook_at(mut, repo6, case6, reg6)
            _check("ARM B control: the unrepaired build still REFUSES",
                   r6b.returncode, EXIT_REFUSE)
            _check("ARM B control: unrepaired, the planted STDOUT is LOST",
                   _PLANT_OUT in r6b.stdout, False)
            _check("ARM B control: unrepaired, the planted STDERR is LOST",
                   _PLANT_ERR in r6b.stdout, False)
            # and prove the control is a faithful stand-in for the old code
            # rather than a build that simply captures nothing:
            r6b2 = _hook_at(mut, repo6, case6, reg6, "--show-check-output")
            _check("ARM B control: unrepaired, only the flag reveals it",
                   _PLANT_OUT in r6b2.stdout, True)

        # ARM C -- no double print
        r6c = _hook_at(os.path.abspath(__file__), repo6, case6, reg6,
                       "--show-check-output")
        _check("ARM C: flag AND refusal still REFUSES", r6c.returncode,
               EXIT_REFUSE)
        _check("ARM C: the planted STDOUT appears EXACTLY once",
               r6c.stdout.count(_PLANT_OUT), 1)
        _check("ARM C: the planted STDERR appears EXACTLY once",
               r6c.stdout.count(_PLANT_ERR), 1)

        # ARM D -- --show-check-output keeps its old meaning on the PASS path,
        # against the REAL frozen instrument, not the stub.
        _write(repo, "REG.md", _reg_body([("verification/t/analyse_x.py", b_py)]))
        r6d = _hook(repo, case, reg, "--show-check-output")
        _check("ARM D: a clean case still PASSES under the flag",
               r6d.returncode, EXIT_PASS)
        _check("ARM D: and the flag still echoes the check on the PASS path",
               r6d.stdout.count("PIN COVERAGE: 1 of 1"), 1)
        r6e = _hook(repo, case, reg)
        _check("ARM E: without the flag a PASS is still quiet",
               "PIN COVERAGE" in r6e.stdout, False)
        _check("ARM E: and still PASSES", r6e.returncode, EXIT_PASS)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        print(f"SELFTEST: {len(fails)} FAILED: {', '.join(fails)}")
        return False
    print("SELFTEST: all arms OK (positive, negative, defect(a), fail-closed, "
          "refusal-carries-its-reason A/B/C + flag-on-PASS D/E)")
    return True


def main():
    ap = argparse.ArgumentParser(
        description="CASE PROTOCOL stage-1 exit gate: may stage 2 launch?")
    ap.add_argument("--case", help="the case directory stage 2 would launch")
    ap.add_argument("--case-id", help="override the id printed on the status "
                                      "line (default: the case dir basename)")
    ap.add_argument("--registration", help="the case's pre-registration")
    ap.add_argument("--repo", help="repo root (default: discovered from --case)")
    ap.add_argument("--timeout", type=float, default=600.0,
                    help="seconds for the frozen check; a timeout is a REFUSAL")
    ap.add_argument("--refuse-unseen-pins", action="store_true",
                    help="REFUSE, not warn, when the registration pins paths "
                         "the frozen checker's PIN_PATH cannot see (defect "
                         "(a)). Default is warn: Sanaa's order gates stage 2 "
                         "on THE FREEZE CHECK PASSING, and making an unseen "
                         "pin refuse is a second, lab-chosen gate criterion "
                         "that D539 reserves to her. The count is on the "
                         "status line either way.")
    ap.add_argument("--show-check-output", action="store_true",
                    help="echo the frozen check's stdout on the PASS path. NOT "
                         "needed to see a REFUSAL's reason: a refusal after "
                         "the frozen check ran prints that check's stdout and "
                         "stderr unconditionally, and passing this flag as "
                         "well prints them once, not twice.")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(EXIT_PASS if selftest() else EXIT_REFUSE)
    sys.exit(run_gate(a))


if __name__ == "__main__":
    main()
