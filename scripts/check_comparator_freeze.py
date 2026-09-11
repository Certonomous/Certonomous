#!/usr/bin/env python3
"""
Enforce VERIFICATION_CHARTER.md 2d: the comparator is frozen before its cases
can answer it.

The rule is enforceable because both sides of the comparison are on disk and
neither is written by the party being audited:

  * when the comparator was last committed   -- git
  * when the run tree's first case finished  -- the completion markers

A comparator whose last commit PRECEDES the earliest completion marker OF THE
CASES IT ACTUALLY GRADES was frozen by construction.  One committed after is
not, and the charter requires a dated disclosure naming what was added, when,
what was readable at that moment, and which findings rest on it.

--------------------------------------------------------------------------
UNIT OF ANALYSIS -- which markers a comparator is judged against  (D471.1)
--------------------------------------------------------------------------
Markers are scoped PER COMPARATOR.  Pooling every marker in a directory
against every comparator in it is a false-positive generator: a directory such
as verification/runs/T-family/T1_runs holds 41 markers from four or more
sub-campaigns, and the earliest of them dates a campaign a given comparator
never reads.

The association is derived from the comparator's OWN SOURCE, parsed as Python,
because the comparator is the only artifact that states which cases it opens
and it cannot be edited to widen its scope without that edit showing up in the
freeze test itself.  A marker file DONE.<CASE> is IN SCOPE for a comparator
when <CASE> is derivable from that comparator's source by either:

  (a) LITERAL -- <CASE> occurs in the source as a complete string constant; or
  (b) TEMPLATE -- <CASE> fully matches a name template found in the source.
      Templates come from f-strings, %-format and str.format literals; each
      substitution point becomes the wildcard [A-Za-z0-9_.+-]+ .  A template is
      used only if it carries at least one substitution point AND at least one
      literal anchor run of two or more characters, because a bare "{}" matches
      every case name and would silently restore the pooling defect.

Strings that are the whole of an expression statement -- module, class and
function docstrings -- are EXCLUDED.  Prose naming a case in order to disclaim
it ("those rows are the frozen rung's, not this one's") is not evidence that
the comparator reads it.  Comments never enter the AST at all.

If a comparator's source names NO marker in its tree while markers exist, the
row is reported AMBIGUOUS-SCOPE and is given NO freeze verdict.  The pooled
figure is printed beside it, explicitly labelled unscoped, so nothing is
hidden; it is never silently used as the verdict.  A comparator whose source
does not parse is likewise AMBIGUOUS-SCOPE.

Every scoped row also prints the pooled first marker and pooled margin as a
diagnostic, so a reader can see exactly what the scoping changed.

--------------------------------------------------------------------------
POPULATION -- what is walked  (D471.2, widened by VERIFICATION_CHARTER 2q)
--------------------------------------------------------------------------
verification/, cases/ and docs/campaigns/ are walked, and the grader name
patterns are analyse_*.py, grade_*.py and score_*.py.  Walking verification/
alone left eleven graders under cases/ (R5C's grade_r5c.py, the TBNN/TBRF
analysers, the R4 scorers, the DAFoam case analysers) with zero freeze
coverage.

docs/campaigns/ was added under VERIFICATION_CHARTER.md 2q (v1.42).  T23G2's
comparator lives at docs/campaigns/T-family/analyse_t23g2.py and 2d.9.2 ruled
PERMANENTLY that it does not move -- relocating it would make the record false
rather than the registration true.  That ruling guarantees the file stays
outside the two original roots, so the coverage hole could not be closed from
the campaign side; it had to be closed here, in the instrument.

SOLVER OUTPUT TREES ARE PRUNED FROM THE WALK -- see PRUNE_RE.  processor*/,
VTK/, postProcessing/ and numeric time directories are solver output, not
source, and the walk descended into all of them: 95,889 of the 109,686
directories under the three roots, 87 per cent of the walk, for a check whose
own charter clause 2cf.1 exists to schedule IO of that size.  The prune is
verdict-neutral BY MEASUREMENT, not by assumption: the number of files matching
GRADER_RE anywhere below one of those names is ZERO -- 0 of 266 tracked (git
ls-files) and 0 of 272 on disk (a full unpruned walk) -- and read_markers()
reads only the directory a grader sits IN, so no marker below a pruned name was
ever reachable either.  The population is identical either way, 272 files; only
the IO is removed.  A pinned path inside a pruned tree is still judged, by the
`extras` fallback at the foot of walk_population, which visits any pinned
directory the walk did not reach.

A grader whose tree carries no completion marker is reported NO-MARKERS -- an
explicit, counted row, not an invisible skip.  Silence and "out of evidence
reach" look identical in a table that omits the row; only one of them is true.

EMPTY POPULATION IS A REFUSAL, NOT A CLEAN BILL  (charter 2p.2)
A walk that finds ZERO graders says nothing about freeze and must not report
success.  It is the exact shape 2q names: point this check at a repository
whose every comparator lives outside its walk roots and the old code answered
exit 0.  A population of zero is now a refusal (exit 2); the reach of a check
is not evidence of the state of what it cannot reach.

PARTIAL POPULATION IS ALSO NOT A CLEAN BILL  (M6SR item 40)
The clause above understood the hazard for the EMPTY case and was SILENT on the
PARTIAL one, so "I checked 1 of 10" returned exactly what "I checked 10 of 10"
returned.  Measured, on this repository: the M6SR ladder runs TEN pinned
executables and the name patterns above matched exactly ONE of them -- three
live under scripts/, which is outside every walk root, and six are .sh drivers
and control suites, which no analyse_/grade_/score_ pattern can match.  The
sole producer of SOLVER_RC.txt, which the strict completion rule reads, was
among the nine outside.

THE FIX IS NOT MORE GLOBS.  A longer pattern list reproduces the defect with a
longer list: it still decides the population from FILE NAMES, which is a
property of nobody's registration.  Instead --registration <path> makes the
check read the set the REGISTRATION ITSELF PINS, and judge exactly that.  Three
limbs, each of which can fail on its own:

  COVERAGE  every pinned path must be judged.  A pinned path that the walk does
            not reach is INJECTED into the population by explicit path,
            whatever it is called and wherever it lives.  One that cannot be
            judged at all -- gone from disk, unreadable tree -- makes the run
            REFUSE (exit 2), because a coverage figure short of the pinned set
            is the partial-population shape this clause exists to stop.
  IDENTITY  for every pinned path, the worktree bytes must equal the HEAD blob.
            This is marker-independent and scope-independent ON PURPOSE: it is
            the "is the file that ran the file that was frozen" question, and
            it must not be silently skipped for a row that happens to be
            NO-MARKERS or AMBIGUOUS-SCOPE, which is where the per-row identity
            test above lives.  Failure is PIN-DRIFT, a violation (exit 3).
  CURRENCY  the HEAD blob of a pinned path must be one of the blob shas the
            registration actually records for it in an unstruck row.  A file
            that moved and whose new blob NOBODY wrote down is unpinned in
            fact however many pin tables the document carries.  Failure is
            PIN-STALE, a violation (exit 3).

WHAT THE PIN LIMBS DELIBERATELY DO NOT DECIDE.  A registration may record
several blob shas for one path across successive amendments, some superseded
and not all of them struck.  Which one is IN FORCE is a reading of the strike
record, not of the file system, and this check does not take it: CURRENCY asks
only the unambiguous question -- is the current blob recorded ANYWHERE unstruck
-- and says so.  Text inside a ~~strike span~~ is dropped before parsing, so a
pin the document has formally superseded cannot satisfy CURRENCY.

--registration is OPT-IN and additive.  With no --registration the walk, the
rows, the counts and the exit code are exactly what they were; the pin limbs
are the only thing the flag adds, and they judge only paths that a named
registration pins.  This matters because the tool is shared, cross-team
instrumentation and other campaigns' rows are not this flag's business.

REGISTRATION-RESTRICTED MODE -- AN EXIT CODE A REGISTRATION CAN EARN
                                                        (M6SR item 42)
The repo-wide exit code is not any one campaign's to earn.  Measured, on this
repository: TWELVE rows belonging to other campaigns are UNFROZEN, so the
process exits 3 no matter how clean the registered set is -- and it was
perfectly clean, 10 of 10 covered, 10 PIN-OK, 0 violating, at the same run.  A
grading criterion phrased "the freeze check exits 0" is therefore UNSATISFIABLE
for such a campaign however correct it is, and no amount of work on its own
files can make it satisfiable.

The available readings were both bad.  Reading the criterion off a substring of
stdout ("PIN COVERAGE: 10 of 10") is weaker than an exit code: a run that dies
before printing that line leaves no substring to fail on, and a grep for a pass
phrase cannot distinguish "printed and true" from "printed and then refused".
Ignoring the exit code is worse still.

--restrict-to-registration answers it at the population instead.  It judges
ONLY the executables the named registration(s) pin, and the exit code is then
earned by that set alone:

  * the population IS the pinned set.  The name patterns never run, so no file
    the registration does not pin can enter it, and no directory is walked for
    anything other than the basenames pinned in it.
  * NOTHING OUTSIDE THE PINNED SET IS JUDGED, RE-JUDGED, SUPPRESSED OR CHANGED.
    A foreign row is not silenced by this mode -- it was never in it.  The
    unrestricted run continues to report every one of those rows exactly as it
    did, at the same status, and continues to exit 3 on them.  That is the
    point: this mode narrows what THIS invocation speaks about, and takes away
    nothing that any other invocation says.
  * IT IS NOT LENIENT.  Every refusal and every violation that could fire in
    the unrestricted run still fires here on a pinned path: an uncovered pin
    REFUSES (exit 2), PIN-DRIFT and PIN-STALE are violations (exit 3), an empty
    restricted population REFUSES, and a pinned comparator that is itself
    UNFROZEN, UNCOMMITTED or MODIFIED_AFTER_COMMIT still exits 3.  Restricting
    the population is not the same as lowering the bar for what is in it.
  * it REQUIRES --registration.  A restriction with no registered set is not a
    narrower population, it is an empty one, and 2p.2 already rules on that.

WHAT A GREEN FROM THIS MODE DOES NOT MEAN -- carried in the output, not only
here, because a caveat a grader has to remember is enforced by prose (M6SR
item 41).  A restricted row that is NO-MARKERS was tested for IDENTITY and
CURRENCY and NOT for freeze margin, because the freeze-margin limb dates a
freeze from completion markers in the comparator's own tree and a campaign
whose chain writes none can never reach it -- before or after a launch.  When
any restricted row is NO-MARKERS the run prints that caveat beside the verdict.
A PASS here is not, and must not be read as, a marker-dated freeze margin.

--------------------------------------------------------------------------
SHA-WITNESS FREEZE  (D471.3)
--------------------------------------------------------------------------
A rung can freeze its comparator by recording the comparator's sha256 in a
record that is itself committed before any case finished.  The comparator file
may then be committed later without the freeze being in doubt: the bytes are
witnessed.

This is recognised as FROZEN-SHA-WITNESS when ALL of:
  * the comparator's ON-DISK bytes hash to <sha>;
  * some other file, still present at HEAD, contains BOTH <sha> and the
    comparator's file name (a bare sha attests to nothing in particular);
  * the commit that introduced <sha> into that file PRECEDES the earliest
    in-scope marker.

The plain commit test is still computed and is printed beside the status on
every such row (`commit test: ...`).  The commit test is not weakened, relaxed
or skipped; a second, independent freeze proof is reported when it exists.

--------------------------------------------------------------------------
MARKER DATING  (D471.4)
--------------------------------------------------------------------------
A marker's own finished_utc= line is a property of the run.  An mtime is a
property of the filesystem, and in this repository 87 of 156 markers carry no
finished_utc while sharing bulk mtimes to the second -- evidence of a copy, not
of a run.  Behaviour, stated so it matches this docstring:

  * default -- an undated marker is still used, its time basis is recorded as
    `mtime`, the row is FLAGGED and counted, and the flag is printed on the
    row.  A margin derived from mtime is never presented as a run-time margin.
  * --strict-markers -- a comparator whose earliest in-scope marker carries no
    finished_utc is given status UNDATED-MARKER, NO freeze verdict, and the
    run refuses with exit 2.

WHAT THIS CHECK CANNOT SEE, stated because a check that overstates its reach is
worse than none:
  * whether a post-marker edit touched the grading path or was purely additive.
    2d permits the second WITH a disclosure and forbids the first outright.
    This check finds the timestamp; a human reads the diff.
  * whether a disclosure exists.  It reports the fact and leaves the reading.
  * a comparator that reads a case its source cannot be shown to name -- the
    scope rule is sound only to the precision of the comparator's own source.
    It errs toward the wider scope: every case name the source can produce is
    in scope, including ones it merely reads for context.
  * a sha witness recorded in a file that no longer exists at HEAD.
  * a comparator that was never committed at all -- reported separately as
    UNCOMMITTED, which is a different and worse condition than late.
  * whether the comparator was ever EXECUTED on the run whose verdict cites
    it.  A freeze verifies BYTES; it never verifies that anything CALLS them.
    A file can be frozen by sha, selftest-green and clean on every row this
    check prints, and still have been run by nobody.  L-544 (commit 4f6384125)
    measured three such instruments in three campaigns -- K2d's
    analyse_k2d.py, whose main() is a stub; T4e's trajectory_t4e.py, which was
    never scheduled; D629's check_instrument_detects_plant.py, which has zero
    call sites -- and this check would report all three PERFECTLY FROZEN.  A
    green here is a statement about the FILE, not about the verdict that cites
    it; the executable call site is read by a human, elsewhere.

Exit: 0 clean, 3 at least one LATE or UNCOMMITTED or MODIFIED, 2 refusal
(including --strict-markers meeting an undated marker).
"""
import argparse
import ast
import datetime as dt
import hashlib
import os
import re
import subprocess
import sys

EXIT_OK, EXIT_REFUSE, EXIT_VIOLATION = 0, 2, 3
MARKER_UTC = re.compile(r"^finished_utc=(.+)$", re.M)

# grader name patterns -- see POPULATION above
GRADER_RE = re.compile(r"^(analyse_|grade_|score_).*\.py$")
# docs/campaigns added under VERIFICATION_CHARTER.md 2q; 2d.9.2 forbids moving
# the comparator that lives there, so the root has to come to the file.
POPULATION_ROOTS = ("verification", "cases", "docs/campaigns")

# Directory names pruned from the population walk -- see POPULATION above.
# These are SOLVER OUTPUT trees: decomposed-case copies, the VTK and
# postProcessing writers, and numeric time directories.  Measured before the
# prune was added, on this repository: files matching GRADER_RE below one of
# these names -- ZERO, both tracked (0 of 266, git ls-files) and on disk (0 of
# 272, full unpruned walk); that zero is plant-controlled, the same census run
# on a tree carrying planted graders under processor0/, VTK/, postProcessing/
# and two numeric time dirs counts 5.  The prune therefore drops no candidate
# and can move no verdict.  "0.orig" and "constant" do not match and are walked.
PRUNE_DIRS = (".git", "__pycache__")
PRUNE_RE = re.compile(
    r"^(processors?[0-9]+(_[0-9]+-[0-9]+)?"   # processor0, processors16_0-15
    r"|VTK|postProcessing"
    r"|[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?)$")  # numeric time directories

# a substitution point in an f-string, %-format or str.format literal
HOLE = "\x00"
BRACE_HOLE = re.compile(r"\{[^{}]*\}")
PERCENT_HOLE = re.compile(r"%[-+ #0-9.*]*[sdifgeExXor]")
CASE_CHAR = "[A-Za-z0-9_.+-]+"

VIOLATING = ("UNCOMMITTED", "UNFROZEN", "MODIFIED_AFTER_COMMIT")
UNJUDGED = ("AMBIGUOUS-SCOPE", "NO-MARKERS", "UNDATED-MARKER")

# --- registration pin parsing -- see PARTIAL POPULATION above ---------------
# A pin is a MARKDOWN TABLE ROW that carries both a backticked repo-relative
# executable path and a full 40-hex git blob sha.  Both conditions are load
# bearing: prose naming a file is not a pin, and a movement chain that carries
# only ABBREVIATED shas is history rather than a pin claim -- the registration
# that drove this says so of its own chain table in as many words.
STRIKE_SPAN = re.compile(r"~~.*?~~", re.S)
PIN_PATH = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./+-]*\.(?:py|sh))`")
PIN_BLOB = re.compile(r"\b[0-9a-f]{40}\b")
PIN_VIOLATING = ("PIN-DRIFT", "PIN-STALE", "PIN-UNCOMMITTED")


def refuse(msg):
    print(msg)
    sys.exit(EXIT_REFUSE)


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo] + list(args),
                       capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def parse_utc(s):
    s = s.strip().replace("Z", "+00:00")
    try:
        d = dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


# --------------------------------------------------------------------------
# markers
# --------------------------------------------------------------------------
def read_markers(tree):
    """[{case, name, time, basis}] for every DONE.* in tree.

    basis is 'finished_utc' when the marker dates itself and 'mtime' when it
    does not.  The distinction is carried all the way to the printed row: see
    MARKER DATING in the module docstring."""
    out = []
    for f in sorted(os.listdir(tree)):
        if not f.startswith("DONE."):
            continue
        p = os.path.join(tree, f)
        t, basis = None, "mtime"
        try:
            m = MARKER_UTC.search(open(p, errors="replace").read())
            if m:
                t = parse_utc(m.group(1))
                if t is not None:
                    basis = "finished_utc"
        except OSError:
            pass
        if t is None:
            t = dt.datetime.fromtimestamp(os.path.getmtime(p), dt.timezone.utc)
        out.append(dict(case=f[len("DONE."):], name=f, time=t, basis=basis))
    return out


def earliest(markers):
    return min(markers, key=lambda m: m["time"]) if markers else None


# --------------------------------------------------------------------------
# scope -- which markers belong to which comparator
# --------------------------------------------------------------------------
def _normalise_holes(s):
    return PERCENT_HOLE.sub(HOLE, BRACE_HOLE.sub(HOLE, s))


def source_name_evidence(path):
    """(literals, template_regexes) or (None, None) if the source will not parse.

    Docstrings are excluded on purpose: a comparator that names a case only to
    DISCLAIM it must not be scoped to that case.  See UNIT OF ANALYSIS."""
    try:
        src = open(path, errors="replace").read()
        mod = ast.parse(src)
    except (OSError, SyntaxError, ValueError):
        return None, None
    doc_ids = set()
    for node in ast.walk(mod):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            doc_ids.add(id(node.value))
    lits, tmpls = set(), set()
    for node in ast.walk(mod):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in doc_ids:
                continue
            lits.add(node.value)
            tmpls.add(_normalise_holes(node.value))
        elif isinstance(node, ast.JoinedStr):
            parts = []
            for v in node.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    parts.append(_normalise_holes(v.value))
                else:
                    parts.append(HOLE)
            tmpls.add("".join(parts))
    regexes = []
    for t in tmpls:
        if HOLE not in t:
            continue
        segs = t.split(HOLE)
        # a template with no literal anchor of 2+ chars matches every case name
        # and would silently reinstate the pooling defect.
        if not any(len(s) >= 2 for s in segs):
            continue
        regexes.append(re.compile("^" + CASE_CHAR.join(re.escape(s) for s in segs) + "$"))
    return lits, regexes


def scope_markers(path, markers):
    """(subset, rule) -- the markers this comparator's own source can name."""
    lits, regexes = source_name_evidence(path)
    if lits is None:
        return [], "source did not parse"
    hit = []
    for m in markers:
        if m["case"] in lits or any(r.match(m["case"]) for r in regexes):
            hit.append(m)
    return hit, "named by the comparator's own source"


# --------------------------------------------------------------------------
# registration pins
# --------------------------------------------------------------------------
def registered_pins(reg_path):
    """{repo-relative path: [blob sha, ...]} for every UNSTRUCK pin row.

    Struck spans are removed FIRST, and are replaced by the newline count they
    contained so that nothing above them changes line, because a superseded pin
    the document has formally struck must not be able to satisfy CURRENCY.
    Returns None if the registration cannot be read at all."""
    try:
        src = open(reg_path, errors="replace").read()
    except OSError:
        return None
    src = STRIKE_SPAN.sub(lambda m: "\n" * m.group(0).count("\n"), src)
    pins = {}
    for line in src.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        blobs = PIN_BLOB.findall(line)
        if not blobs:
            continue
        for p in PIN_PATH.findall(line):
            pins.setdefault(p, [])
            for b in blobs:
                if b not in pins[p]:
                    pins[p].append(b)
    return pins


def pin_rows(repo, pins, judged_keys):
    """One row per pinned path: coverage, worktree identity, pin currency."""
    out = []
    for rel in sorted(pins):
        row = dict(path=rel, recorded=pins[rel])
        full = os.path.join(repo, rel)
        row["exists_on_disk"] = os.path.isfile(full)
        row["covered"] = (os.path.dirname(rel), os.path.basename(rel)) in judged_keys
        rc_h, head_blob, _ = git(repo, "rev-parse", f"HEAD:{rel}")
        row["head_blob"] = head_blob if rc_h == 0 and head_blob else None
        rc_d, disk_blob, _ = git(repo, "hash-object", "--", full) \
            if row["exists_on_disk"] else (1, "", "")
        row["disk_blob"] = disk_blob if rc_d == 0 and disk_blob else None

        if not row["exists_on_disk"]:
            row["status"] = "PIN-ABSENT"
        elif row["head_blob"] is None:
            row["status"] = "PIN-UNCOMMITTED"
        elif row["disk_blob"] != row["head_blob"]:
            row["status"] = "PIN-DRIFT"
        elif row["head_blob"] not in pins[rel]:
            row["status"] = "PIN-STALE"
        else:
            row["status"] = "PIN-OK"
        out.append(row)
    return out


# --------------------------------------------------------------------------
# sha witness
# --------------------------------------------------------------------------
def sha_witness(repo, relc, disk_sha):
    """(iso, witness_path) for the EARLIEST commit that recorded disk_sha in a
    file which also names this comparator, or (None, None).  See SHA-WITNESS."""
    name = os.path.basename(relc)
    rc, out, _ = git(repo, "grep", "-l", disk_sha, "HEAD")
    if rc != 0 or not out:
        return None, None
    best = None
    for line in out.splitlines():
        if ":" not in line:
            continue
        path = line.split(":", 1)[1]
        if path == relc:
            continue
        rc2, blob, _ = git(repo, "show", f"HEAD:{path}")
        if rc2 != 0 or name not in blob:
            continue
        _, hist, _ = git(repo, "log", "-S", disk_sha, "--format=%cI",
                         "--reverse", "--", path)
        if not hist.strip():
            continue
        t = parse_utc(hist.splitlines()[0])
        if t is not None and (best is None or t < best[0]):
            best = (t, path)
    return (best[0].isoformat(), best[1]) if best else (None, None)


# --------------------------------------------------------------------------
# the check
# --------------------------------------------------------------------------
def check_tree(repo, tree, strict_markers=False, extra=(), restrict=None):
    """`extra` are basenames a REGISTRATION pins in this tree.  They join the
    population by explicit path, whatever they are called: that is the whole
    point of the pin limbs, since a name pattern is a property of nobody's
    registration.  Everything downstream judges them identically.

    `restrict`, when given, limits this tree to those basenames and suppresses
    the name patterns entirely.  It is used for a pinned directory OUTSIDE the
    walk roots, so that following one registration's pin into, say, scripts/
    judges THAT registration's files and does not quietly conscript four other
    campaigns' graders that happen to share the directory."""
    rel = os.path.relpath(tree, repo)
    try:
        present = os.listdir(tree)
    except OSError:
        return None
    if restrict is not None:
        names = [f for f in restrict if os.path.isfile(os.path.join(tree, f))]
    else:
        names = [f for f in present
                 if GRADER_RE.match(f) and os.path.isfile(os.path.join(tree, f))] \
            + [f for f in extra if os.path.isfile(os.path.join(tree, f))]
    graders = sorted(set(names))
    if not graders:
        return None
    markers = read_markers(tree)
    pooled = earliest(markers)
    out = []
    for c in graders:
        relc = os.path.join(rel, c)
        row = dict(tree=rel, comparator=c, n_markers_in_tree=len(markers))
        if pooled is not None:
            row["pooled_first_marker"] = pooled["name"]
            row["pooled_first_marker_utc"] = pooled["time"].isoformat()

        # ---- unit of analysis, before anything is compared -----------------
        if not markers:
            row.update(status="NO-MARKERS", scope_rule="no completion marker "
                       "in this tree", note="out of this check's evidence reach")
            out.append(row)
            continue
        mine, rule = scope_markers(os.path.join(tree, c), markers)
        row["scope_rule"] = rule
        row["scope_n"] = len(mine)
        row["scope_sample"] = ", ".join(m["case"] for m in sorted(
            mine, key=lambda m: m["case"])[:4]) + ("..." if len(mine) > 4 else "")
        if not mine:
            row.update(status="AMBIGUOUS-SCOPE",
                       note="no marker in this tree is named by this "
                            "comparator's source; pooled figure shown "
                            "UNSCOPED and NOT used as a verdict")
            out.append(row)
            continue

        mk = earliest(mine)
        row["first_marker"] = mk["name"]
        row["first_marker_utc"] = mk["time"].isoformat()
        row["marker_time_basis"] = mk["basis"]
        if pooled is not None:
            row["pooled_margin_seconds"] = None  # filled once we have a commit

        if mk["basis"] == "mtime" and strict_markers:
            row.update(status="UNDATED-MARKER",
                       note="earliest in-scope marker carries no finished_utc; "
                            "--strict-markers refuses rather than date a "
                            "freeze from the filesystem")
            out.append(row)
            continue

        # ---- git side -------------------------------------------------------
        rc, iso, _ = git(repo, "log", "-1", "--format=%cI", "--", relc)
        # FIRST commit as well as last, because "did not exist in any commit
        # when the first case finished" and "existed, then was amended" are
        # different conditions and only the first is 2d's core violation.
        # --follow so a rename does not read as a birth.
        _, hist, _ = git(repo, "log", "--follow", "--format=%cI", "--", relc)
        first_iso = hist.splitlines()[-1] if hist.strip() else ""
        rc2, blob, _ = git(repo, "rev-parse", f"HEAD:{relc}")

        disk_sha = None
        try:
            disk_sha = hashlib.sha256(
                open(os.path.join(tree, c), "rb").read()).hexdigest()
        except OSError:
            pass
        row["disk_sha256"] = disk_sha

        if rc != 0 or not iso:
            row.update(status="UNCOMMITTED", committed_utc=None,
                       commit_test="UNCOMMITTED",
                       note="the comparator is in no commit")
        else:
            ct = parse_utc(iso)
            row["committed_utc"] = ct.isoformat()
            row["margin_seconds"] = (mk["time"] - ct).total_seconds()
            if pooled is not None:
                row["pooled_margin_seconds"] = (pooled["time"] - ct).total_seconds()
            # is the file that ran the file that was frozen?
            modified = None
            if rc2 == 0 and disk_sha is not None:
                # INDEX-INDEPENDENT ON PURPOSE.  `git status` and `git diff HEAD`
                # both consult the index, and this repository's shared index has
                # been observed stale enough to report tracked files as deleted
                # while they sit on disk.  Comparing the worktree bytes against the
                # HEAD BLOB asks git only for content, which no index can distort.
                r = subprocess.run(["git", "-C", repo, "cat-file", "blob", blob],
                                   capture_output=True)
                if r.returncode == 0:
                    modified = hashlib.sha256(r.stdout).hexdigest() != disk_sha
                    row["worktree_differs_from_HEAD"] = modified
            ft = parse_utc(first_iso) if first_iso else None
            row["first_committed_utc"] = ft.isoformat() if ft else None
            if ct < mk["time"]:
                row["commit_test"] = "MODIFIED_AFTER_COMMIT" if modified else "FROZEN"
            elif ft is not None and ft < mk["time"]:
                # existed in a commit before the run finished its first case, and
                # was touched again afterwards.  W-4 corrections to a published
                # rung live here and 2d's boundary clause exempts them, so this is
                # reported as its own state rather than folded into a violation.
                row["commit_test"] = "AMENDED_AFTER"
            else:
                row["commit_test"] = "UNFROZEN"
            row["status"] = row["commit_test"]

        # ---- second, independent freeze proof: the sha witness --------------
        # The commit test above is already decided and is kept, printed, in
        # row["commit_test"].  A witness can only ADD a proof, never remove one.
        if row["status"] in ("UNFROZEN", "UNCOMMITTED") and disk_sha:
            w_iso, w_path = sha_witness(repo, relc, disk_sha)
            if w_iso is not None:
                row["sha_witness_utc"] = w_iso
                row["sha_witness_path"] = w_path
                if parse_utc(w_iso) < mk["time"]:
                    row["status"] = "FROZEN-SHA-WITNESS"
        out.append(row)
    return out


def walk_population(repo, strict_markers=False, roots=POPULATION_ROOTS,
                    extras=None):
    """Every grader under every population root -- see POPULATION.

    `extras` is {repo-relative dir: [basename, ...]} of paths a registration
    PINS.  A pinned directory the roots already reach gets its names ADDED to
    that tree's population; one the roots never reach is visited afterwards
    RESTRICTED to the pinned names.  With extras empty this function is exactly
    what it was, which is the property the --registration flag rests on."""
    rows, seen = [], set()

    def take(r):
        for x in r or ():
            k = (x["tree"], x["comparator"])
            if k not in seen:
                seen.add(k)
                rows.append(x)

    pending = {d: list(n) for d, n in (extras or {}).items()}
    for root in roots:
        base = os.path.join(repo, root)
        if not os.path.isdir(base):
            continue
        for dp, dn, fn in os.walk(base):
            dn[:] = [d for d in dn
                     if d not in PRUNE_DIRS and not PRUNE_RE.match(d)]
            rel = os.path.relpath(dp, repo)
            take(check_tree(repo, dp, strict_markers=strict_markers,
                            extra=pending.pop(rel, ())))
    for rel in sorted(pending):
        d = os.path.join(repo, rel)
        if not os.path.isdir(d):
            continue
        take(check_tree(repo, d, strict_markers=strict_markers,
                        restrict=pending[rel]))
    return rows


def walk_registered(repo, pins, strict_markers=False):
    """The RESTRICTED population -- exactly the executables `pins` names.

    See REGISTRATION-RESTRICTED MODE.  Every pinned directory is visited once,
    RESTRICTED to the basenames pinned in it, so GRADER_RE never runs and no
    file the registration does not pin can enter the population.  Nothing
    outside the pinned set is opened, judged or reported here -- which is the
    property that makes the exit code the registration's own to earn, and the
    property that keeps this mode from touching another campaign's row.

    Rows are produced by the SAME check_tree as the unrestricted walk, so a
    pinned path is judged identically in both; the only difference is which
    paths are in the population."""
    by_dir = {}
    for path in pins:
        by_dir.setdefault(os.path.dirname(path) or ".", []).append(
            os.path.basename(path))
    rows, seen = [], set()
    for rel in sorted(by_dir):
        d = repo if rel == "." else os.path.join(repo, rel)
        if not os.path.isdir(d):
            continue
        for x in check_tree(repo, d, strict_markers=strict_markers,
                            restrict=by_dir[rel]) or ():
            k = (x["tree"], x["comparator"])
            if k not in seen:
                seen.add(k)
                rows.append(x)
    return rows


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------
def selftest():
    """Planted shapes that must fire, and shapes that must survive."""
    import tempfile, shutil
    ok = True
    tmp = tempfile.mkdtemp()

    def check(label, got, want):
        nonlocal ok
        if got != want:
            print(f"  SELFTEST FAIL: {label}: expected {want!r}, got {got!r}")
            ok = False
        else:
            print(f"  {label:44s} -> {want}  OK")

    try:
        repo = os.path.join(tmp, "r")
        os.makedirs(os.path.join(repo, "verification", "t"))
        subprocess.run(["git", "init", "-q", repo], check=True)
        subprocess.run(["git", "-C", repo, "config", "user.email", "t@t"], check=True)
        subprocess.run(["git", "-C", repo, "config", "user.name", "t"], check=True)
        tree = os.path.join(repo, "verification", "t")

        def commit(msg, when):
            env = dict(os.environ, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
            # throwaway repository in a tempdir -- not the shared worktree
            subprocess.run(["git", "-C", repo, "add", "-A"], check=True, env=env)
            subprocess.run(["git", "-C", repo, "commit", "-q", "-m", msg],
                           check=True, env=env)

        def marker(d, case, when=None):
            body = f"finished_utc={when}\n" if when else "strict rule met\n"
            open(os.path.join(d, f"DONE.{case}"), "w").write(body)

        # ---- FROZEN: comparator committed before the marker it grades -------
        open(os.path.join(tree, "analyse_x.py"), "w").write(
            'def m(t):\n    return f"AX_{t}_c"\n')
        commit("c", "2026-01-01T00:00:00+00:00")
        marker(tree, "AX_1_c", "2026-01-02T00:00:00Z")
        r = check_tree(repo, tree)
        check("planted FROZEN", r and r[0]["status"], "FROZEN")

        # ---- AMENDED_AFTER: existed before the marker, touched again after --
        # W-4 territory; 2d's boundary clause exempts it, so it must NOT be a
        # violation.
        open(os.path.join(tree, "analyse_x.py"), "w").write(
            'def m(t):\n    return f"AX_{t}_c"  # v2\n')
        commit("c2", "2026-01-03T00:00:00+00:00")
        r = check_tree(repo, tree)
        check("planted AMENDED", r and r[0]["status"], "AMENDED_AFTER")

        # ---- UNFROZEN: the comparator is in NO commit until after the first
        # case it grades finished.  2d's core violation.
        t3 = os.path.join(repo, "verification", "t3")
        os.makedirs(t3)
        marker(t3, "ZC_1", "2026-02-01T00:00:00Z")
        commit("marker only", "2026-02-01T00:00:00+00:00")
        open(os.path.join(t3, "analyse_z.py"), "w").write(
            'def m(t):\n    return f"ZC_{t}"  # born late\n')
        commit("comparator after the fact", "2026-02-02T00:00:00+00:00")
        r = check_tree(repo, t3)
        check("planted UNFROZEN", r and r[0]["status"], "UNFROZEN")

        # ---- MODIFIED: frozen commit but the worktree file has drifted ------
        marker(tree, "AX_1_c", "2026-01-04T00:00:00Z")
        open(os.path.join(tree, "analyse_x.py"), "a").write("# drift\n")
        r = check_tree(repo, tree)
        check("planted MODIFIED", r and r[0]["status"], "MODIFIED_AFTER_COMMIT")
        open(os.path.join(tree, "analyse_x.py"), "w").write(
            'def m(t):\n    return f"AX_{t}_c"  # v2\n')

        # ================================================================
        # D471.1 -- UNIT OF ANALYSIS.  A pooled layout the OLD code would have
        # condemned falsely: comparator analyse_p.py grades only the PB_* cases,
        # which finish LATE; a foreign sub-campaign PA_* in the same directory
        # finishes EARLY.  Pooling dates analyse_p.py from PA_1 and calls it
        # UNFROZEN; scoped to the cases its own source names it is FROZEN.
        # ================================================================
        tp = os.path.join(repo, "verification", "pool")
        os.makedirs(tp)
        open(os.path.join(tp, "analyse_a.py"), "w").write(
            'def m(t):\n    return f"PA_{t}"\n')
        commit("foreign comparator, frozen first", "2026-02-25T00:00:00+00:00")
        marker(tp, "PA_1", "2026-03-01T00:00:00Z")      # foreign, early
        marker(tp, "PA_2", "2026-03-01T01:00:00Z")
        commit("foreign sub-campaign finishes", "2026-03-02T00:00:00+00:00")
        open(os.path.join(tp, "analyse_p.py"), "w").write(
            'LEVELS = ("c", "f")\n'
            'def m(t, l):\n    return f"PB_{t}_{l}"\n')
        commit("the comparator under test", "2026-03-03T00:00:00+00:00")
        marker(tp, "PB_1_c", "2026-03-04T00:00:00Z")    # its own cases, late
        marker(tp, "PB_1_f", "2026-03-04T01:00:00Z")
        r = check_tree(repo, tp)
        byname = {x["comparator"]: x for x in r}
        pooled_would_have = (parse_utc("2026-03-01T00:00:00Z")
                             < parse_utc("2026-03-03T00:00:00+00:00"))
        if not pooled_would_have:
            print("  SELFTEST FAIL: pooled control is not actually adverse"); ok = False
        check("D471.1 pooled layout, own cases scoped",
              byname["analyse_p.py"]["status"], "FROZEN")
        check("D471.1 scope excludes the foreign campaign",
              byname["analyse_p.py"]["scope_n"], 2)
        check("D471.1 foreign comparator still judged on its own",
              byname["analyse_a.py"]["status"], "FROZEN")
        # the pooled figure must still be VISIBLE, never silently used
        check("D471.1 pooled figure still printed",
              byname["analyse_p.py"]["pooled_first_marker"], "DONE.PA_1")
        # PLANTED NEGATIVE: prose and bare string statements must NOT widen the
        # scope.  Prose is excluded by whole-string equality (a sentence is
        # never equal to a case name); a bare string statement whose whole
        # content IS a case name is excluded only by the docstring rule, which
        # is why both are planted.
        open(os.path.join(tp, "analyse_d.py"), "w").write(
            '"""This comparator does NOT grade PA_1; those rows are elsewhere."""\n'
            '"PA_2"  # legacy note: graded elsewhere, left as a bare string\n'
            'def m(t, l):\n    return f"PB_{t}_{l}"\n')
        commit("docstring disclaimer", "2026-03-03T00:00:00+00:00")
        r = check_tree(repo, tp)
        byname = {x["comparator"]: x for x in r}
        check("D471.1 prose/bare-string mention does not widen scope",
              byname["analyse_d.py"]["scope_n"], 2)
        # AMBIGUOUS-SCOPE: names nothing in its tree -> no verdict, no pooling
        open(os.path.join(tp, "analyse_q.py"), "w").write(
            'def m(x):\n    return x\n')
        commit("scopeless comparator", "2026-03-05T00:00:00+00:00")
        r = check_tree(repo, tp)
        byname = {x["comparator"]: x for x in r}
        check("D471.1 unscopable comparator",
              byname["analyse_q.py"]["status"], "AMBIGUOUS-SCOPE")
        check("D471.1 unscopable row carries no margin",
              byname["analyse_q.py"].get("margin_seconds"), None)

        # ================================================================
        # D471.2 -- POPULATION.  A grader planted under cases/ must be FOUND.
        # ================================================================
        tc = os.path.join(repo, "cases", "synthetic_rung")
        os.makedirs(tc)
        open(os.path.join(tc, "grade_syn.py"), "w").write(
            'def m(t):\n    return f"SY_{t}"\n')
        commit("grader under cases/", "2026-04-01T00:00:00+00:00")
        marker(tc, "SY_1", "2026-04-02T00:00:00Z")
        rows = walk_population(repo)
        found = [x for x in rows if x["tree"].startswith("cases/")]
        check("D471.2 grader under cases/ is in the population", len(found), 1)
        check("D471.2 grader under cases/ is judged",
              found and found[0]["status"], "FROZEN")
        v_only = walk_population(repo, roots=("verification",))
        if any(x["tree"].startswith("cases/") for x in v_only):
            print("  SELFTEST FAIL: cases/ control is not adverse -- the old "
                  "verification-only walk would already have found it"); ok = False
        else:
            print("  D471.2 control is adverse (old walk missed it)  OK")
        # a grader with no marker anywhere is REPORTED, not skipped
        tn = os.path.join(repo, "cases", "no_marker_rung")
        os.makedirs(tn)
        open(os.path.join(tn, "score_none.py"), "w").write("x = 1\n")
        commit("marker-less grader", "2026-04-03T00:00:00+00:00")
        rows = walk_population(repo)
        nm = [x for x in rows if x["comparator"] == "score_none.py"]
        check("D471.2 marker-less grader reported, not skipped",
              nm and nm[0]["status"], "NO-MARKERS")

        # ================================================================
        # 2q -- POPULATION WIDENED TO docs/campaigns.  Deliberately the same
        # three-part shape as D471.2 eleven lines above: the new root's grader
        # must be FOUND and JUDGED through the PRODUCTION roots, and the OLD
        # roots must be shown to have MISSED it.  A control the old code would
        # also have passed is not a control.
        # ================================================================
        old_roots = ("verification", "cases")
        tdc = os.path.join(repo, "docs", "campaigns", "T_synthetic")
        os.makedirs(tdc)
        open(os.path.join(tdc, "analyse_dc.py"), "w").write(
            'def m(t):\n    return f"DC_{t}"\n')
        commit("grader under docs/campaigns/", "2026-08-01T00:00:00+00:00")
        marker(tdc, "DC_1", "2026-08-02T00:00:00Z")
        # PRODUCTION PATH ON PURPOSE: no roots= argument, so this reads the same
        # POPULATION_ROOTS the command line reads.  A test that passed its own
        # roots tuple would be exercising a copy of the widening, and a test of
        # a copy tests nothing (charter 2p.3(d)).
        rows = walk_population(repo)
        dcf = [x for x in rows if x["tree"].startswith("docs/campaigns/")]
        check("2q grader under docs/campaigns/ is in the population", len(dcf), 1)
        # 2p.3(e) POSITIVE CONTROL, limb 1 -- the widening must not refuse
        # everything it newly sees.  A repair that condemns its whole new
        # population is "restrictive" only in the trivial sense.
        check("2q(e) newly-seen grader still judged FROZEN",
              dcf and dcf[0]["status"], "FROZEN")
        # ADVERSE CONTROL, the D471.2 shape -- re-walk with the OLD roots and
        # fail the selftest if they would have found it too.
        old_walk = walk_population(repo, roots=old_roots)
        if any(x["tree"].startswith("docs/campaigns/") for x in old_walk):
            print("  SELFTEST FAIL: docs/campaigns control is not adverse -- the "
                  "old two-root walk would already have found it"); ok = False
        else:
            print("  2q control is adverse (old roots missed it)  OK")
        # 2p.3(e) POSITIVE CONTROL, limb 2 -- the widening is ADDITIVE: it loses
        # no grader it already walked and re-judges none of them.  A widening
        # that quietly moved an existing verdict would be caught here.
        was = {(x["tree"], x["comparator"]): x["status"] for x in old_walk}
        now = {(x["tree"], x["comparator"]): x["status"] for x in rows}
        check("2q(e) widening loses no previously-walked grader",
              sorted(k for k in was if k not in now), [])
        check("2q(e) widening changes no previously-returned verdict",
              sorted(k for k, v in was.items() if now.get(k) != v), [])
        check("2q(e) widening is purely additive",
              len(rows) - len(old_walk), len(dcf))

        # ================================================================
        # 2p.2 -- THE EMPTY-INPUT ARM.  A walk that finds ZERO comparators has
        # checked nothing and must REFUSE.  Both arms below run THIS FILE as a
        # subprocess, so what is exercised is the code the command line runs and
        # not a re-implementation of it (2p.3(d)).
        # ================================================================
        me = os.path.abspath(__file__)

        def scratch_repo(name):
            rp = os.path.join(tmp, name)
            os.makedirs(rp)
            subprocess.run(["git", "init", "-q", rp], check=True)
            subprocess.run(["git", "-C", rp, "config", "user.email", "t@t"],
                           check=True)
            subprocess.run(["git", "-C", rp, "config", "user.name", "t"],
                           check=True)
            return rp

        def commit_in(rp, msg, when):
            env = dict(os.environ, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
            # throwaway repository in a tempdir -- not the shared worktree
            subprocess.run(["git", "-C", rp, "add", "-A"], check=True, env=env)
            subprocess.run(["git", "-C", rp, "commit", "-q", "-m", msg],
                           check=True, env=env)

        def entry_point_rc(rp):
            return subprocess.run([sys.executable, me, "--repo", rp],
                                  capture_output=True, text=True).returncode

        # RESTRICTIVE ARM, in 2q's own words: a repository whose every
        # comparator lives OUTSIDE the walk roots.  The old code answered
        # exit 0 -- ALL CLEAN -- on exactly this tree.
        rz = scratch_repo("empty_population")
        os.makedirs(os.path.join(rz, "elsewhere"))
        open(os.path.join(rz, "elsewhere", "analyse_hidden.py"), "w").write(
            'def m(t):\n    return f"HID_{t}"\n')
        marker(os.path.join(rz, "elsewhere"), "HID_1", "2026-08-10T00:00:00Z")
        commit_in(rz, "comparator outside every walk root",
                  "2026-08-09T00:00:00+00:00")
        check("2p.2 zero-comparator population REFUSES",
              entry_point_rc(rz), EXIT_REFUSE)
        check("2p.2 the refused population really was empty",
              len(walk_population(rz)), 0)
        # PLANTED CONTROL ON THAT ZERO -- the walker that returned 0 above is
        # shown able to return non-zero on the same tree when a root reaches it.
        # A zero from a reader never shown able to see a non-zero is not
        # evidence (CLAUDE.md rule 3).
        check("2p.2 the hidden grader IS found once a root reaches it",
              len(walk_population(rz, roots=("elsewhere",))), 1)

        # POSITIVE CONTROL for that refusal (2p.3(e)) -- it restricted, it did
        # not disable.  A non-empty, correctly-frozen population under the NEW
        # root still exits 0 through the same entry point.
        rp2 = scratch_repo("positive_control")
        pdc = os.path.join(rp2, "docs", "campaigns", "P_rung")
        os.makedirs(pdc)
        open(os.path.join(pdc, "analyse_pc.py"), "w").write(
            'def m(t):\n    return f"PC_{t}"\n')
        commit_in(rp2, "frozen comparator under docs/campaigns",
                  "2026-08-11T00:00:00+00:00")
        marker(pdc, "PC_1", "2026-08-12T00:00:00Z")
        check("2p.3(e) non-empty frozen population still PASSES",
              entry_point_rc(rp2), EXIT_OK)

        # ================================================================
        # D471.3 -- SHA WITNESS.  Comparator committed AFTER its marker, but a
        # record committed BEFORE the marker carries the comparator's sha and
        # names it.  Must read FROZEN-SHA-WITNESS with the commit test still
        # visible and still UNFROZEN.
        # ================================================================
        tw = os.path.join(repo, "verification", "witness")
        os.makedirs(tw)
        body = 'def m(t):\n    return f"WT_{t}"\n'
        wsha = hashlib.sha256(body.encode()).hexdigest()
        open(os.path.join(tw, "RECORD.md"), "w").write(
            f"sha256 of `analyse_w.py`, recorded before any case existed:\n{wsha}\n")
        commit("record with the sha witness", "2026-05-01T00:00:00+00:00")
        marker(tw, "WT_1", "2026-05-02T00:00:00Z")
        open(os.path.join(tw, "analyse_w.py"), "w").write(body)
        commit("comparator committed late", "2026-05-03T00:00:00+00:00")
        r = check_tree(repo, tw)
        wrow = [x for x in r if x["comparator"] == "analyse_w.py"][0]
        check("D471.3 sha-witness freeze recognised",
              wrow["status"], "FROZEN-SHA-WITNESS")
        check("D471.3 commit test still visible and unweakened",
              wrow["commit_test"], "UNFROZEN")
        # PLANTED NEGATIVE 1: a witness recorded AFTER the marker proves nothing
        tw2 = os.path.join(repo, "verification", "witness_late")
        os.makedirs(tw2)
        body2 = 'def m(t):\n    return f"WL_{t}"\n'
        w2 = hashlib.sha256(body2.encode()).hexdigest()
        marker(tw2, "WL_1", "2026-05-02T00:00:00Z")
        commit("marker first", "2026-05-02T00:00:00+00:00")
        open(os.path.join(tw2, "RECORD.md"), "w").write(
            f"sha256 of `analyse_wl.py`: {w2}\n")
        open(os.path.join(tw2, "analyse_wl.py"), "w").write(body2)
        commit("witness and comparator both late", "2026-05-03T00:00:00+00:00")
        r = check_tree(repo, tw2)
        wrow2 = [x for x in r if x["comparator"] == "analyse_wl.py"][0]
        check("D471.3 late witness does NOT rescue", wrow2["status"], "UNFROZEN")
        # PLANTED NEGATIVE 2: a witness whose sha does not match the disk bytes
        tw3 = os.path.join(repo, "verification", "witness_stale")
        os.makedirs(tw3)
        body3 = 'def m(t):\n    return f"WS_{t}"\n'
        open(os.path.join(tw3, "RECORD.md"), "w").write(
            "sha256 of `analyse_ws.py`: " + "0" * 64 + "\n")
        commit("stale witness", "2026-06-01T00:00:00+00:00")
        marker(tw3, "WS_1", "2026-06-02T00:00:00Z")
        open(os.path.join(tw3, "analyse_ws.py"), "w").write(body3)
        commit("comparator late", "2026-06-03T00:00:00+00:00")
        r = check_tree(repo, tw3)
        wrow3 = [x for x in r if x["comparator"] == "analyse_ws.py"][0]
        check("D471.3 non-matching witness does NOT rescue",
              wrow3["status"], "UNFROZEN")

        # ================================================================
        # D471.4 -- MARKER DATING.  A marker with no finished_utc is FLAGGED,
        # and under --strict-markers it is refused, never mtime-graded silently.
        # ================================================================
        tu = os.path.join(repo, "verification", "undated")
        os.makedirs(tu)
        open(os.path.join(tu, "analyse_u.py"), "w").write(
            'def m(t):\n    return f"UD_{t}"\n')
        commit("comparator", "2026-07-01T00:00:00+00:00")
        marker(tu, "UD_1")                     # deliberately no finished_utc
        r = check_tree(repo, tu)
        check("D471.4 undated marker flagged as mtime-basis",
              r[0]["marker_time_basis"], "mtime")
        r = check_tree(repo, tu, strict_markers=True)
        check("D471.4 --strict-markers refuses to date from mtime",
              r[0]["status"], "UNDATED-MARKER")
        check("D471.4 refused row carries no freeze margin",
              r[0].get("margin_seconds"), None)
        # a DATED marker in the same shape must survive both modes
        marker(tu, "UD_2", "2026-07-02T00:00:00Z")
        os.remove(os.path.join(tu, "DONE.UD_1"))
        r = check_tree(repo, tu, strict_markers=True)
        check("D471.4 dated marker survives strict mode",
              r[0]["status"], "FROZEN")
        check("D471.4 dated marker basis", r[0]["marker_time_basis"], "finished_utc")

        # ================================================================
        # ITEM 40 -- PARTIAL POPULATION.  The shape measured on the real
        # repository: a registration pins TEN executables and the name patterns
        # match ONE, because three live outside every walk root and six are .sh.
        # Reproduced in miniature, with the adverse control the D471.2 and 2q
        # arms above insist on -- the OLD walk must be shown to MISS them.
        # ================================================================
        rpn = scratch_repo("pinned_population")

        def wr(rp, rel, body, ex=False):
            f = os.path.join(rp, rel)
            os.makedirs(os.path.dirname(f), exist_ok=True)
            open(f, "w").write(body)
            if ex:
                os.chmod(f, 0o755)
            return f

        def blob_of(rp, rel):
            return git(rp, "rev-parse", f"HEAD:{rel}")[1]

        def run_ep(rp, *args):
            return subprocess.run([sys.executable, me, "--repo", rp] + list(args),
                                  capture_output=True, text=True)

        # one grader the patterns DO match, one .sh inside a walk root they
        # cannot match, one file outside every walk root, and -- the trap -- a
        # FOREIGN grader sharing that outside directory.
        wr(rpn, "cases/PIN/analyse_pin.py", 'def m(t):\n    return f"PN_{t}"\n')
        wr(rpn, "cases/PIN/run_pin.sh", '#!/bin/sh\necho pin\n', ex=True)
        wr(rpn, "tools/helper_pin.py", "X = 1\n")
        wr(rpn, "tools/analyse_foreign.py", "Y = 2\n")   # another campaign's
        commit_in(rpn, "the pinned set and one foreign grader",
                  "2026-09-01T00:00:00+00:00")

        pinned3 = ["cases/PIN/analyse_pin.py", "cases/PIN/run_pin.sh",
                   "tools/helper_pin.py"]
        b = {p: blob_of(rpn, p) for p in pinned3}

        def reg_body(rows, extra_text=""):
            out = ["# registration\n\n| path | git blob sha |\n|---|---|\n"]
            for p, sha in rows:
                out.append(f"| **`{p}`** (pinned) | **`{sha}`** |\n")
            out.append(extra_text)
            return "".join(out)

        reg = "verification/campaign/REG.md"
        wr(rpn, reg, reg_body([(p, b[p]) for p in pinned3]))
        commit_in(rpn, "registration pinning three", "2026-09-01T01:00:00+00:00")

        # ---- ADVERSE CONTROL: the OLD walk misses two of the three ----------
        old = walk_population(rpn)
        old_names = {(x["tree"], x["comparator"]) for x in old}
        check("item40 old walk finds the glob-matching grader",
              ("cases/PIN", "analyse_pin.py") in old_names, True)
        check("item40 old walk MISSES the .sh in a walk root",
              ("cases/PIN", "run_pin.sh") in old_names, False)
        check("item40 old walk MISSES the file outside every root",
              ("tools", "helper_pin.py") in old_names, False)

        # ---- COVERAGE: the pinned set is judged, whatever it is called ------
        p3 = registered_pins(os.path.join(rpn, reg))
        check("item40 registration parses to its pinned set",
              sorted(p3), sorted(pinned3))
        ext = {}
        for pth in p3:
            ext.setdefault(os.path.dirname(pth) or ".", []).append(
                os.path.basename(pth))
        neu = walk_population(rpn, extras=ext)
        new_names = {(x["tree"], x["comparator"]) for x in neu}
        check("item40 the .sh is now IN the population",
              ("cases/PIN", "run_pin.sh") in new_names, True)
        check("item40 the out-of-root file is now IN the population",
              ("tools", "helper_pin.py") in new_names, True)
        # THE RESTRICT CONTROL.  Following a pin into tools/ must judge the
        # pinned file and must NOT conscript the other campaign's grader that
        # happens to share the directory -- this tool is shared instrumentation.
        check("item40 following a pin does NOT conscript a foreign grader",
              ("tools", "analyse_foreign.py") in new_names, False)
        # ADDITIVE, the 2q(e) shape: nothing previously walked is lost or moved
        was2 = {(x["tree"], x["comparator"]): x["status"] for x in old}
        now2 = {(x["tree"], x["comparator"]): x["status"] for x in neu}
        check("item40 widening loses no previously-walked grader",
              sorted(k for k in was2 if k not in now2), [])
        check("item40 widening changes no previously-returned verdict",
              sorted(k for k, v in was2.items() if now2.get(k) != v), [])

        # ---- the flag is OPT-IN: without it, nothing at all changes ---------
        check("item40 no --registration leaves the population untouched",
              len(walk_population(rpn)), len(old))

        # ---- PARTIAL POPULATION REFUSES (the item 40 ruling) ----------------
        # A registration pinning a path that cannot be judged must refuse, the
        # way an empty population already did.  Planted by pinning a path that
        # is not on disk.
        wr(rpn, reg, reg_body([(p, b[p]) for p in pinned3]
                              + [("cases/PIN/vanished.sh", "0" * 40)]))
        commit_in(rpn, "registration pins a path that is not there",
                  "2026-09-01T02:00:00+00:00")
        r_part = run_ep(rpn, "--registration", reg)
        check("item40 a pinned path with no row REFUSES", r_part.returncode,
              EXIT_REFUSE)
        check("item40 the refusal names the uncovered path",
              "vanished.sh" in r_part.stdout, True)
        # POSITIVE CONTROL ON THAT REFUSAL (2p.3(e)) -- it restricted, it did
        # not disable.  The same entry point on the COMPLETE pin set must NOT
        # refuse.  A refusal that fires on everything proves nothing.
        wr(rpn, reg, reg_body([(p, b[p]) for p in pinned3]))
        commit_in(rpn, "back to the complete pin set",
                  "2026-09-01T03:00:00+00:00")
        r_full = run_ep(rpn, "--registration", reg)
        check("item40 the COMPLETE pin set does not refuse",
              r_full.returncode != EXIT_REFUSE, True)
        check("item40 coverage is reported as N of N",
              "PIN COVERAGE: 3 of 3" in r_full.stdout, True)
        check("item40 a complete, current pin set is clean",
              r_full.returncode, EXIT_OK)

        # ---- STRIKE SPANS ARE DROPPED --------------------------------------
        # A pin the document has formally struck must not be resurrected as a
        # coverage obligation.  Planted with a struck row naming a path that
        # does not exist: if the strike is honoured the run is unchanged; if it
        # is not, the run refuses on a path nobody pins any more.
        wr(rpn, reg, reg_body([(p, b[p]) for p in pinned3],
                              "\n> STRUCK BY QUOTE: ~~| **`cases/PIN/struck.sh`**"
                              " | **`" + "1" * 40 + "`** |~~\n"))
        commit_in(rpn, "a struck row", "2026-09-01T04:00:00+00:00")
        check("item40 a STRUCK pin row is not a live pin",
              sorted(registered_pins(os.path.join(rpn, reg))), sorted(pinned3))
        check("item40 a struck row does not make the run refuse",
              run_ep(rpn, "--registration", reg).returncode, EXIT_OK)

        # ---- PIN-DRIFT: worktree bytes are not the committed bytes ----------
        open(os.path.join(rpn, "tools/helper_pin.py"), "a").write("# drift\n")
        r_dr = run_ep(rpn, "--registration", reg)
        check("item40 uncommitted drift on a pinned file is PIN-DRIFT",
              "PIN-DRIFT" in r_dr.stdout, True)
        check("item40 PIN-DRIFT is a violation", r_dr.returncode, EXIT_VIOLATION)

        # ---- PIN-STALE: the file moved and the pin did not ------------------
        commit_in(rpn, "the pinned file moves, the registration does not",
                  "2026-09-01T05:00:00+00:00")
        r_st = run_ep(rpn, "--registration", reg)
        check("item40 a moved file whose new blob is recorded nowhere is "
              "PIN-STALE", "PIN-STALE" in r_st.stdout, True)
        check("item40 PIN-STALE is a violation", r_st.returncode, EXIT_VIOLATION)
        # ADVERSE PAIR -- re-pin the moved file and the same run goes green, so
        # PIN-STALE is shown to track the pin and not merely the edit.
        b["tools/helper_pin.py"] = blob_of(rpn, "tools/helper_pin.py")
        wr(rpn, reg, reg_body([(p, b[p]) for p in pinned3]))
        commit_in(rpn, "re-pinned", "2026-09-01T06:00:00+00:00")
        check("item40 re-pinning clears PIN-STALE",
              run_ep(rpn, "--registration", reg).returncode, EXIT_OK)

        # ---- a registration that pins NOTHING is a refusal, not a pass ------
        # The 2p.2 principle one level up: a parser that read a document and
        # found no pin has failed to reach a pin set, not verified an empty one.
        wr(rpn, "verification/campaign/NOPINS.md",
           "# registration\n\nThis one names `cases/PIN/run_pin.sh` in prose "
           "only, with no blob sha anywhere.\n")
        commit_in(rpn, "a registration with no pins",
                  "2026-09-01T07:00:00+00:00")
        check("item40 a registration pinning nothing REFUSES",
              run_ep(rpn, "--registration",
                     "verification/campaign/NOPINS.md").returncode, EXIT_REFUSE)

        # ================================================================
        # M6SR ITEM 42 -- AN EXIT CODE A REGISTRATION CAN EARN.
        #
        # The planted repository reproduces the measured defect exactly: a
        # registered set that is PERFECTLY CLEAN, and foreign rows that hold
        # the process exit at 3 regardless.  Every arm below runs THIS FILE as
        # a subprocess, so what is exercised is the command line a grading
        # criterion would be written against.
        # ================================================================
        r42 = scratch_repo("item42")

        # -- the registered set: one grader with a marker, one file outside
        #    every walk root with none (the M6SR shape).
        wr(r42, "cases/M/analyse_m.py", 'def m(t):\n    return f"MM_{t}"\n')
        wr(r42, "tools/help_m.py", "X = 1\n")
        commit_in(r42, "the registered set", "2026-09-02T00:00:00+00:00")
        marker(os.path.join(r42, "cases", "M"), "MM_1", "2026-09-03T00:00:00Z")

        # -- FOREIGN ROW 1: another campaign's grader, in a tree this
        #    registration has nothing to do with, born AFTER its own case
        #    finished.  This is the twelve-row shape.
        os.makedirs(os.path.join(r42, "verification", "foreign"))
        marker(os.path.join(r42, "verification", "foreign"), "FF_1",
               "2026-09-03T12:00:00Z")
        commit_in(r42, "a foreign case finishes", "2026-09-03T12:00:00+00:00")
        wr(r42, "verification/foreign/analyse_f.py",
           'def m(t):\n    return f"FF_{t}"  # born late\n')
        # -- FOREIGN ROW 2: the near-miss.  A grader the NAME PATTERNS match,
        #    sitting INSIDE a directory this registration pins a file in.
        #    Restricting must exclude it BY REGISTRATION, not by directory.
        wr(r42, "cases/M/analyse_other.py",
           'def m(t):\n    return f"MM_{t}"  # another campaign, born late\n')
        commit_in(r42, "two foreign graders, both late",
                  "2026-09-04T00:00:00+00:00")

        b42 = {p: blob_of(r42, p) for p in ("cases/M/analyse_m.py",
                                            "tools/help_m.py")}
        reg42 = "verification/campaign/REG42.md"
        wr(r42, reg42, reg_body(sorted(b42.items())))
        commit_in(r42, "registration pinning two", "2026-09-05T00:00:00+00:00")

        # ---- IS THE PLANT ACTUALLY ADVERSE?  A control that fires on a tree
        # that was never guilty proves nothing, so the guilt is measured
        # first, at source, rather than assumed from the way it was built.
        st42 = {(x["tree"] + "/" + x["comparator"]): x["status"]
                for x in walk_population(r42)}
        check("item42 plant is adverse: foreign grader is UNFROZEN",
              st42.get("verification/foreign/analyse_f.py"), "UNFROZEN")
        check("item42 plant is adverse: same-directory grader is UNFROZEN",
              st42.get("cases/M/analyse_other.py"), "UNFROZEN")
        check("item42 plant is adverse: the REGISTERED grader is clean",
              st42.get("cases/M/analyse_m.py"), "FROZEN")

        # ---- THE DEFECT, REPRODUCED.  Registered set clean; exit 3 anyway. --
        u1 = run_ep(r42, "--registration", reg42)
        check("item42 unrestricted: the pinned set is completely covered",
              "PIN COVERAGE: 2 of 2" in u1.stdout, True)
        check("item42 unrestricted: the pinned set has ZERO violations",
              "2 PIN-OK, 0 violating" in u1.stdout, True)
        check("item42 unrestricted: and the exit code is 3 REGARDLESS",
              u1.returncode, EXIT_VIOLATION)

        # ---- THE FIX.  Same repo, same registration, one added flag. --------
        r1 = run_ep(r42, "--registration", reg42, "--restrict-to-registration")
        check("item42 RESTRICTED: the registered set earns exit 0",
              r1.returncode, EXIT_OK)
        check("item42 RESTRICTED: population is 2 graders, not the walk",
              "2 grader(s) in the population, 0 violating" in r1.stdout, True)

        # ---- SILENCE, NOT SUPPRESSION.  The foreign rows are not hidden by
        # this mode; they were never in it.  Both must be absent from the
        # restricted output and present in the unrestricted one -- the second
        # half is what makes the first half mean something.
        for nm in ("analyse_f.py", "analyse_other.py"):
            check(f"item42 RESTRICTED does not judge foreign {nm}",
                  nm in r1.stdout, False)
            check(f"item42 unrestricted still reports foreign {nm}",
                  nm in u1.stdout, True)

        # ---- NON-INTERFERENCE, BYTE FOR BYTE.  The unrestricted invocation
        # must be untouched by the existence of the restricted one.  PLANTED:
        # the same comparison is run against the restricted output, and MUST
        # report a difference -- a byte comparison that cannot see one is not
        # evidence of sameness.
        u2 = run_ep(r42, "--registration", reg42)
        check("item42 unrestricted output is byte-identical across runs",
              u1.stdout == u2.stdout, True)
        check("item42 unrestricted exit code is unchanged",
              u1.returncode == u2.returncode, True)
        check("item42 PLANT: that comparison CAN see a difference",
              u1.stdout == r1.stdout, False)

        # ---- ITEM 41's CAVEAT IS PRINTED WHERE THE GRADER MEETS IT ---------
        # tools/help_m.py has no marker in its tree, so its freeze-margin limb
        # cannot fire.  The verdict must say so.
        check("item41 caveat is printed beside a restricted verdict",
              "CAVEAT ON THIS VERDICT" in r1.stdout, True)
        check("item41 caveat counts the unreachable rows",
              "1 of 2 restricted row(s) are NO-MARKERS" in r1.stdout, True)
        # NEGATIVE CONTROL -- the caveat is CONDITIONAL, not boilerplate.  A
        # registration whose every pinned row IS margin-judged must not get it.
        reg41 = "verification/campaign/REG41.md"
        wr(r42, reg41, reg_body([("cases/M/analyse_m.py",
                                  b42["cases/M/analyse_m.py"])]))
        commit_in(r42, "a registration with no NO-MARKERS row",
                  "2026-09-05T01:00:00+00:00")
        r_nc = run_ep(r42, "--registration", reg41, "--restrict-to-registration")
        check("item41 caveat is ABSENT when every row is margin-judged",
              "CAVEAT ON THIS VERDICT" in r_nc.stdout, False)
        check("item41 that negative control still PASSES",
              r_nc.returncode, EXIT_OK)

        # ---- RESTRICTED IS NOT LENIENT.  Every arm below is the SAME entry
        # point and the SAME flag as the passing arm above, so a failure here
        # is the plant and not the mode.
        # (a) a pinned path that cannot be judged still REFUSES
        wr(r42, reg42, reg_body(sorted(b42.items())
                                + [("cases/M/gone.sh", "0" * 40)]))
        commit_in(r42, "a pin nobody can judge", "2026-09-05T02:00:00+00:00")
        r_mp = run_ep(r42, "--registration", reg42, "--restrict-to-registration")
        check("item42 RESTRICTED still REFUSES on an uncovered pin",
              r_mp.returncode, EXIT_REFUSE)
        check("item42 that refusal names the uncovered path",
              "gone.sh" in r_mp.stdout, True)
        wr(r42, reg42, reg_body(sorted(b42.items())))
        commit_in(r42, "back to the complete pin set",
                  "2026-09-05T03:00:00+00:00")
        # (b) PIN-DRIFT is still a violation under restriction
        open(os.path.join(r42, "tools/help_m.py"), "a").write("# drift\n")
        r_dr2 = run_ep(r42, "--registration", reg42, "--restrict-to-registration")
        check("item42 RESTRICTED still fails on PIN-DRIFT",
              r_dr2.returncode, EXIT_VIOLATION)
        check("item42 and names it PIN-DRIFT", "PIN-DRIFT" in r_dr2.stdout, True)
        # (c) PIN-STALE is still a violation under restriction
        commit_in(r42, "the drift lands, the pin does not move",
                  "2026-09-05T04:00:00+00:00")
        r_st2 = run_ep(r42, "--registration", reg42, "--restrict-to-registration")
        check("item42 RESTRICTED still fails on PIN-STALE",
              r_st2.returncode, EXIT_VIOLATION)
        check("item42 and names it PIN-STALE", "PIN-STALE" in r_st2.stdout, True)
        # ADVERSE PAIR -- re-pinning clears it, so the failure tracked the pin
        # and not merely the edit.
        b42["tools/help_m.py"] = blob_of(r42, "tools/help_m.py")
        wr(r42, reg42, reg_body(sorted(b42.items())))
        commit_in(r42, "re-pinned", "2026-09-05T05:00:00+00:00")
        check("item42 re-pinning clears it and RESTRICTED passes again",
              run_ep(r42, "--registration", reg42,
                     "--restrict-to-registration").returncode, EXIT_OK)

        # (d) THE ARM THAT MATTERS MOST: a violation INSIDE the registered set.
        # Restricting the population must not restrict the standard applied to
        # what is in it.  Planted so the PIN limbs are clean and the ROW is
        # not, which isolates the row limb from the pin limbs entirely.
        r42b = scratch_repo("item42_own_set_violates")
        os.makedirs(os.path.join(r42b, "cases", "N"))
        marker(os.path.join(r42b, "cases", "N"), "NN_1", "2026-09-06T00:00:00Z")
        commit_in(r42b, "the case finishes first", "2026-09-06T00:00:00+00:00")
        wr(r42b, "cases/N/analyse_n.py",
           'def m(t):\n    return f"NN_{t}"  # born after its own case\n')
        commit_in(r42b, "the comparator is born late",
                  "2026-09-07T00:00:00+00:00")
        regb = "verification/campaign/REGB.md"
        wr(r42b, regb, reg_body([("cases/N/analyse_n.py",
                                  blob_of(r42b, "cases/N/analyse_n.py"))]))
        commit_in(r42b, "pinned at its current blob",
                  "2026-09-07T01:00:00+00:00")
        r_own = run_ep(r42b, "--registration", regb, "--restrict-to-registration")
        check("item42 RESTRICTED fails on an UNFROZEN row in its OWN set",
              r_own.returncode, EXIT_VIOLATION)
        check("item42 and the PIN limbs were clean, so the ROW earned it",
              "1 PIN-OK, 0 violating" in r_own.stdout, True)
        check("item42 the failing row is reported UNFROZEN",
              "UNFROZEN" in r_own.stdout, True)

        # (e) the flag REQUIRES a registration.  Restricting to nothing is an
        # empty population, and that has never been a clean population.
        check("item42 --restrict-to-registration alone REFUSES",
              run_ep(r42, "--restrict-to-registration").returncode, EXIT_REFUSE)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return ok


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--strict-markers", action="store_true",
                    help="refuse (exit 2) rather than date a freeze from a "
                         "marker that carries no finished_utc")
    ap.add_argument("--registration", action="append", default=[], metavar="PATH",
                    help="a pre-registration whose PINNED executables must all "
                         "be in the population.  Repeatable.  Adds the COVERAGE, "
                         "IDENTITY and CURRENCY limbs; changes nothing about the "
                         "walk when it is not given")
    ap.add_argument("--restrict-to-registration", action="store_true",
                    help="judge ONLY the executables the given registration(s) "
                         "pin, so the EXIT CODE is earned by that set alone. "
                         "Requires --registration. Judges, re-judges, "
                         "suppresses and changes NOTHING outside the pinned "
                         "set -- the unrestricted run still reports every "
                         "other row exactly as before. Not lenient: every "
                         "refusal and violation still fires on a pinned path")
    a = ap.parse_args()
    if a.selftest:
        print("SELFTEST -- planted shapes that must fire, and ones that must not")
        sys.exit(EXIT_OK if selftest() else EXIT_VIOLATION)

    repo = os.path.abspath(a.repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        refuse(f"REFUSE: {repo} is not a git repository")

    if a.restrict_to_registration and not a.registration:
        # 2p.2 one level up.  "Restrict to the registered set" with no
        # registration names an EMPTY set, and an empty population has never
        # been a clean population.  Refusing here also stops the flag from
        # being a silent no-op that a criterion could be written against.
        refuse("REFUSE: --restrict-to-registration requires at least one "
               "--registration. A restriction with no registered set is not a "
               "narrower population, it is an empty one (charter 2p.2).")

    # ---- registration pins, read BEFORE the walk so they can widen it -------
    pins, extras = {}, {}
    for reg in a.registration:
        p = registered_pins(reg if os.path.isabs(reg) else os.path.join(repo, reg))
        if p is None:
            refuse(f"REFUSE: registration {reg} could not be read")
        if not p:
            # the 2p.2 shape, one level up: a parser that read a registration
            # and found no pin at all has not verified a pin set, it has failed
            # to reach one.  Reporting that as coverage would be the exact
            # defect this flag exists to close.
            refuse(f"REFUSE: {reg} pins ZERO executables by blob sha. A "
                   f"registration from which no pin is readable is a parser "
                   f"that did not reach its subject, not a clean pin set.")
        for path, blobs in p.items():
            pins.setdefault(path, [])
            for b in blobs:
                if b not in pins[path]:
                    pins[path].append(b)
    for path in pins:
        extras.setdefault(os.path.dirname(path) or ".", []).append(
            os.path.basename(path))

    if a.restrict_to_registration:
        rows = walk_registered(repo, pins, strict_markers=a.strict_markers)
    else:
        rows = walk_population(repo, strict_markers=a.strict_markers,
                               extras=extras)

    print("COMPARATOR FREEZE -- VERIFICATION_CHARTER.md 2d")
    print("scope: markers are matched PER COMPARATOR from the comparator's own "
          "source (D471.1)")
    if a.restrict_to_registration:
        print(f"population: RESTRICTED to the {len(pins)} executable(s) pinned "
              f"by {', '.join(a.registration)} -- the analyse_/grade_/score_ "
              f"name patterns are NOT applied")
        print("THE EXIT CODE BELOW IS EARNED BY THAT SET ALONE. This mode is "
              "SILENT about every row outside it: it judges none of them, "
              "re-judges none of them, suppresses none of them and changes "
              "none of them. The unrestricted invocation still reports them "
              "unaltered, at the same statuses and the same exit code.")
    else:
        print(f"population: {', '.join(POPULATION_ROOTS)}/  --  "
              "analyse_*.py, grade_*.py, score_*.py (D471.2; docs/campaigns added "
              "under charter 2q)")
    print("=" * 100)
    if not rows:
        # charter 2p.2, the empty-input test.  A walk that found nothing has not
        # checked anything, and the old exit 0 here was indistinguishable, from
        # the exit code alone, from "every comparator is frozen".  2q names this
        # exact shape: a repository whose comparators all sit outside the walk
        # roots used to report ALL CLEAN.  Refuse instead; a check's reach is not
        # evidence about what lies beyond it.
        print("  no tree carries a grader.")
        print("ZERO VERDICT: NOT_A_MEASUREMENT -- nothing was in scope")
        if a.restrict_to_registration:
            # the same clause, restricted: a mode whose whole population is the
            # pinned set and which reached NONE of it has not judged that set
            # clean, it has failed to reach it.
            refuse("REFUSE: the RESTRICTED population is EMPTY -- not one of "
                   "the " + str(len(pins)) + " pinned executable(s) could be "
                   "reached: " + ", ".join(sorted(pins)) + ". An empty "
                   "population is not a clean population (charter 2p.2).")
        refuse(f"REFUSE: the walk of {', '.join(POPULATION_ROOTS)}/ found ZERO "
               f"comparators. An empty population is not a clean population -- "
               f"it is a check that did not reach its subject (charter 2p.2).")
    bad = 0
    order = {"UNCOMMITTED": 0, "UNFROZEN": 1, "MODIFIED_AFTER_COMMIT": 2,
             "AMBIGUOUS-SCOPE": 3, "UNDATED-MARKER": 4, "AMENDED_AFTER": 5,
             "FROZEN-SHA-WITNESS": 6, "FROZEN": 7, "NO-MARKERS": 8}
    for r in sorted(rows, key=lambda x: (order.get(x["status"], 9), x["tree"])):
        marg = r.get("margin_seconds")
        m = f"{marg:+.0f}s" if marg is not None else "-"
        flag = "   <-- " if r["status"] in VIOLATING else ""
        print(f"  {r['status']:22s} {r['tree']}/{r['comparator']}")
        if r["status"] == "NO-MARKERS":
            print(f"      no completion marker in this tree -- out of evidence "
                  f"reach, reported so the gap is countable")
            continue
        print(f"      scope: {r.get('scope_n')} of {r.get('n_markers_in_tree')} "
              f"marker(s) in the tree [{r.get('scope_sample') or '-'}] "
              f"({r.get('scope_rule')})")
        if r["status"] == "AMBIGUOUS-SCOPE":
            print(f"      UNSCOPED pooled first marker "
                  f"{r.get('pooled_first_marker_utc')} "
                  f"({r.get('pooled_first_marker')}) -- shown, NOT used")
            continue
        print(f"      first commit {r.get('first_committed_utc')}   last commit "
              f"{r.get('committed_utc')}")
        print(f"      first marker {r['first_marker_utc']} ({r['first_marker']})"
              f"   margin(last) {m}{flag}")
        if r.get("marker_time_basis") == "mtime":
            print(f"      MARKER-UNDATED: no finished_utc; the time above is an "
                  f"mtime, a filesystem property, not a run property")
        if r["status"] == "UNDATED-MARKER":
            continue
        pm = r.get("pooled_margin_seconds")
        if pm is not None and r.get("pooled_first_marker") != r.get("first_marker"):
            print(f"      pooled (unscoped) first marker "
                  f"{r.get('pooled_first_marker_utc')} "
                  f"({r.get('pooled_first_marker')})   pooled margin {pm:+.0f}s "
                  f"-- diagnostic only")
        if r["status"] == "FROZEN-SHA-WITNESS":
            print(f"      sha witness {r.get('sha_witness_utc')} in "
                  f"{r.get('sha_witness_path')}   commit test: "
                  f"{r.get('commit_test')} (unweakened, shown beside)")
        if r["status"] in VIOLATING:
            bad += 1
    print("-" * 100)
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    n_mtime = sum(1 for r in rows if r.get("marker_time_basis") == "mtime")
    print("  " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    print(f"  {len(rows)} grader(s) in the population, {bad} violating, "
          f"{n_mtime} dated from an mtime rather than a finished_utc")
    print("CANNOT SEE: whether a late edit touched the grading path or was "
          "purely additive; whether a disclosure exists; a case a comparator "
          "reads but its source cannot be shown to name; a sha witness in a "
          "file no longer at HEAD.")
    # ---- the pin limbs -- COVERAGE, IDENTITY, CURRENCY ----------------------
    pin_bad, uncovered = 0, []
    if pins:
        judged = {(r["tree"], r["comparator"]) for r in rows}
        prows = pin_rows(repo, pins, judged)
        print("-" * 100)
        print(f"REGISTRATION PINS -- {', '.join(a.registration)}")
        for pr in sorted(prows, key=lambda x: (x["status"] == "PIN-OK", x["path"])):
            cov = "covered" if pr["covered"] else "NOT IN THE POPULATION"
            print(f"  {pr['status']:16s} {pr['path']}   [{cov}]")
            print(f"      HEAD blob {pr['head_blob'] or '-'}   worktree blob "
                  f"{pr['disk_blob'] or '-'}   {len(pr['recorded'])} sha(s) "
                  f"recorded unstruck")
            if pr["status"] == "PIN-STALE":
                print(f"      the HEAD blob is recorded NOWHERE unstruck in this "
                      f"registration -- the file moved and the pin did not")
            if pr["status"] == "PIN-DRIFT":
                print(f"      the worktree file is NOT the committed file; a pin "
                      f"names bytes that are not the bytes that would run")
            if not pr["covered"]:
                uncovered.append(pr["path"])
            if pr["status"] in PIN_VIOLATING:
                pin_bad += 1
        n_ok = sum(1 for pr in prows if pr["status"] == "PIN-OK")
        print(f"  PIN COVERAGE: {len(prows) - len(uncovered)} of {len(prows)} "
              f"pinned executable(s) judged in the population; {n_ok} PIN-OK, "
              f"{pin_bad} violating")
        print("PIN LIMBS CANNOT SEE: which of several recorded shas is the one "
              "IN FORCE when a registration carries superseded, unstruck pin "
              "rows -- that is a reading of the strike record, not of the file "
              "system.")

    if any(r["status"] == "UNDATED-MARKER" for r in rows):
        refuse("REFUSE: --strict-markers and at least one in-scope marker "
               "carries no finished_utc")
    if uncovered:
        # the PARTIAL-POPULATION arm.  Exactly the reason the empty arm above
        # refuses: a coverage figure short of the pinned set is a check that did
        # not reach its subject, and "I checked 1 of 10" must not return what
        # "I checked 10 of 10" returns.
        print("ZERO VERDICT: NOT_A_MEASUREMENT -- part of the pinned set was "
              "never in scope")
        refuse("REFUSE: " + str(len(uncovered)) + " pinned executable(s) got no "
               "row: " + ", ".join(uncovered) + ". A partial population is not "
               "a clean population -- it is a check that did not reach its "
               "subject (charter 2p.2, extended to the partial case).")
    if a.restrict_to_registration:
        # M6SR item 41, carried WHERE A GRADER MEETS IT.  The freeze-margin limb
        # dates a freeze from completion markers in the comparator's own tree.
        # A campaign whose chain writes no marker cannot reach that limb, before
        # or after a launch, and a NO-MARKERS row is therefore tested for
        # IDENTITY and CURRENCY and NOT for margin.  Printing this only beside a
        # restricted verdict is deliberate: this is the invocation a grading
        # criterion is written against, so this is where the caveat has to be.
        n_nm = sum(1 for r in rows if r["status"] == "NO-MARKERS")
        if n_nm:
            print("-" * 100)
            print(f"CAVEAT ON THIS VERDICT -- {n_nm} of {len(rows)} restricted "
                  f"row(s) are NO-MARKERS. The FREEZE-MARGIN limb DID NOT FIRE "
                  f"for them and cannot fire while their tree carries no "
                  f"completion marker. What was tested for those rows is "
                  f"IDENTITY and CURRENCY. A PASS from this mode is NOT a "
                  f"marker-dated "
                  f"freeze margin and must not be read as one; a campaign in "
                  f"this position proves its freeze by commit ordering, not by "
                  f"this limb.")
    if bad or pin_bad:
        print("VERDICT: FAIL")
        sys.exit(EXIT_VIOLATION)
    if a.restrict_to_registration:
        print("ZERO VERDICT: ZERO_IS_A_MEASUREMENT -- every executable the "
              "named registration PINS is in the population, is the file that "
              "was committed, is pinned at a sha the registration records "
              "unstruck, and is either frozen against the cases it names or "
              "reported as out of evidence reach. This says NOTHING about any "
              "row outside the pinned set.")
        print("VERDICT: PASS")
        sys.exit(EXIT_OK)
    print("ZERO VERDICT: ZERO_IS_A_MEASUREMENT -- every grader in the "
          "population is either frozen against the cases it names or is "
          "reported as out of evidence reach")
    print("VERDICT: PASS")
    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
