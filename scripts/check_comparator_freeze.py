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
POPULATION -- what is walked  (D471.2)
--------------------------------------------------------------------------
Both verification/ and cases/ are walked, and the grader name patterns are
analyse_*.py, grade_*.py and score_*.py.  Walking verification/ alone left
eleven graders under cases/ (R5C's grade_r5c.py, the TBNN/TBRF analysers, the
R4 scorers, the DAFoam case analysers) with zero freeze coverage.

A grader whose tree carries no completion marker is reported NO-MARKERS -- an
explicit, counted row, not an invisible skip.  Silence and "out of evidence
reach" look identical in a table that omits the row; only one of them is true.

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
POPULATION_ROOTS = ("verification", "cases")

# a substitution point in an f-string, %-format or str.format literal
HOLE = "\x00"
BRACE_HOLE = re.compile(r"\{[^{}]*\}")
PERCENT_HOLE = re.compile(r"%[-+ #0-9.*]*[sdifgeExXor]")
CASE_CHAR = "[A-Za-z0-9_.+-]+"

VIOLATING = ("UNCOMMITTED", "UNFROZEN", "MODIFIED_AFTER_COMMIT")
UNJUDGED = ("AMBIGUOUS-SCOPE", "NO-MARKERS", "UNDATED-MARKER")


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
def check_tree(repo, tree, strict_markers=False):
    rel = os.path.relpath(tree, repo)
    graders = sorted(f for f in os.listdir(tree)
                     if GRADER_RE.match(f)
                     and os.path.isfile(os.path.join(tree, f)))
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


def walk_population(repo, strict_markers=False, roots=POPULATION_ROOTS):
    """Every grader under every population root -- see POPULATION."""
    rows = []
    for root in roots:
        base = os.path.join(repo, root)
        if not os.path.isdir(base):
            continue
        for dp, dn, fn in os.walk(base):
            dn[:] = [d for d in dn if d not in (".git", "__pycache__")]
            r = check_tree(repo, dp, strict_markers=strict_markers)
            if r:
                rows.extend(r)
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
    a = ap.parse_args()
    if a.selftest:
        print("SELFTEST -- planted shapes that must fire, and ones that must not")
        sys.exit(EXIT_OK if selftest() else EXIT_VIOLATION)

    repo = os.path.abspath(a.repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        refuse(f"REFUSE: {repo} is not a git repository")

    rows = walk_population(repo, strict_markers=a.strict_markers)

    print("COMPARATOR FREEZE -- VERIFICATION_CHARTER.md 2d")
    print("scope: markers are matched PER COMPARATOR from the comparator's own "
          "source (D471.1)")
    print(f"population: {', '.join(POPULATION_ROOTS)}/  --  "
          "analyse_*.py, grade_*.py, score_*.py (D471.2)")
    print("=" * 100)
    if not rows:
        print("  no tree carries a grader.")
        print("ZERO VERDICT: NOT_A_MEASUREMENT -- nothing was in scope")
        sys.exit(EXIT_OK)
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
    if any(r["status"] == "UNDATED-MARKER" for r in rows):
        refuse("REFUSE: --strict-markers and at least one in-scope marker "
               "carries no finished_utc")
    if bad:
        print("VERDICT: FAIL")
        sys.exit(EXIT_VIOLATION)
    print("ZERO VERDICT: ZERO_IS_A_MEASUREMENT -- every grader in the "
          "population is either frozen against the cases it names or is "
          "reported as out of evidence reach")
    print("VERDICT: PASS")
    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
