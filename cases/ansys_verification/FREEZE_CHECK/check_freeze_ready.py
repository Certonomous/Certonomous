#!/usr/bin/env python3
# =============================================================================
# check_freeze_ready.py -- a pre-freeze readiness instrument for Ansys VM cases.
#
# WHY THIS EXISTS
# ---------------
# The supervisor's undelegable CLAUDE.md-rule-2 / charter-s3 check --
# "pre-registration COMMITTED before compute" -- was discharged four times and
# wrong four times, in the SAME shape each time: the artifact was verified and
# its CONTRACT WITH THE MACHINERY was not. `bash -n` checks syntax, never path
# existence; a comparator selftest passes on synthetic arrays while its field
# names name zero code paths; a freeze can hold one instance of a registered
# triple; a document can contradict itself about its own triple. A fifth lesson
# saying "be more careful" is worthless. This is the instrument that would have
# caught THOSE FOUR -- and it is itself an instrument, so this lab's rules for
# instruments bind it: it REFUSES rather than degrades, it carries planted
# failures in --selftest (L-487), and it has no bare `assert` (it would vanish
# under python3 -O).
#
# READ "THOSE FOUR" STRICTLY. It is NOT a claim to catch the class, and two
# later members of that same class -- both VMFL046-R4 comparator defects -- pass
# every check here. See THE COVERAGE BOUNDARY below before relying on a pass.
#
# FILING QUESTION -- FLAGGED, NOT DECIDED (for the supervisor)
# -----------------------------------------------------------
# Lab convention (FILING_CHARTER, docs/LOCATIONS.md) puts scripts in scripts/.
# But scripts/ is OUTSIDE this team's folder scope, and the supervisor committed
# outside scope once already and recorded it as an error. This file therefore
# lives in TEAM TERRITORY, with cases/ansys_verification/DIGITIZER/ as the
# precedent for team-local tooling. Whether it should ultimately move to
# scripts/ (and be added to check_filing.py's allow-list) is the supervisor's
# call, not this lane's. The question is raised here so it is not silently
# decided by where the file happened to land.
#
# INTERFACE
# ---------
#   check_freeze_ready.py --case <case_dir> [--freeze <commit-ish>] [--selftest]
#     --freeze  defaults to the WORKING TREE (the point: it must be runnable
#               BEFORE the commit exists, via a pure-python git blob sha that
#               equals `git hash-object`). With a commit-ish, blobs are read
#               from that commit.
#   exit 0 = every check passed (PASS/WARN/deferred-only).
#   exit 2 = at least one REFUSAL, or a check that could not be evaluated
#            (blocking UNDETERMINED -- never read as a pass).
#   exit 3 = usage / internal error.
#
# THE SEVEN CHECKS (each maps to one of the four real failures)
#   C1 LAUNCHABILITY   -- an executable driver taking a run-root arg exists;
#                         REFUSE if the only executable is a tutorial Allrun.
#   C2 PATH EXISTENCE  -- every statically-resolvable in-repo path the driver /
#                         comparator name exists; runtime-only paths are listed
#                         UNDETERMINED, never silently passed. (What bash -n
#                         cannot do.)
#   C3 GRADING PIN     -- a 40-hex comparator blob pin is present and equals the
#                         comparator's actual blob; REFUSE on absent / deferred /
#                         wrong pin. C3 PINS THE COMPARATOR'S BYTES AND SAYS
#                         NOTHING WHATEVER ABOUT ITS BEHAVIOUR. See the coverage
#                         boundary below -- this narrowing is REQUIRED, not
#                         stylistic (VERIFICATION_CHARTER v1.68 s2aw.7).
#   C4 LEVEL COMPLETE  -- every declared level/instance is constructible from
#                         frozen material (dir | token-template+driver |
#                         committed generator). REFUSE if fewer than N of N.
#   C5 SELF-CONSISTENCY-- at most one refinement level-set family and one
#                         refinement ratio declared. REFUSE on contradiction.
#   C6 CONST AGREEMENT -- a comparator-hardcoded refinement ratio must agree
#                         with the registration's declared/implied ratio(s).
#   C7 RUN ROOT        -- report whether the implied run root exists / is empty;
#                         absence is a WARN (an ordering fix), never a refusal.
#
# THE COVERAGE BOUNDARY -- WHAT THESE SEVEN CHECKS DO **NOT** COVER
# ----------------------------------------------------------------
# RULED AGAINST THIS FILE, 2026-09-06, VERIFICATION_CHARTER v1.68 s2aw.7:
#
#     "check_freeze_ready.py's C3 DECLARES that it checks the comparator AND
#      DOES NOT CHECK THE COMPARATOR'S PRODUCTION ORDERING. A check whose
#      declaration is wider than its coverage is worse than an absent check,
#      because THE DECLARATION IS WHAT A READER RELIES ON."
#
# So, stated flatly, because an absent boundary is the defect:
#
#   * C3 compares BYTES. It cannot tell a correct comparator from a broken one.
#     A comparator that crashes on its own arguments, or refuses on its own
#     scratch files, passes C3 -- BOTH HAPPENED, in VMFL046-R4, on the same
#     file, in one day (L-495). C3 caught neither and was never able to.
#   * NOTHING HERE DRIVES grade() END-TO-END. A comparator's selftest may pass
#     every arm while exercising only the PARTS and never the PRODUCTION
#     SEQUENCE -- the argument shapes at its own call sites, the ordering of its
#     phases, the module-level state they share. That is the gap both VMFL046-R4
#     defects lived in, and it is NOT covered by C1-C7.
#   * s2aw.7 ENDORSED an end-to-end grade() drive AS PRACTICE and DECLINED TO
#     MINT IT as a freeze qualification (two defects in one file are one
#     population member, not two -- s2p.5; and s28.18's regress: a fourth layer
#     of guard is a fourth surface). It is therefore RECOMMENDED HERE AND NOT
#     ENFORCED, and this file must not be read as requiring it.
#   * WHAT WOULD MOVE THE REFEREE, PRE-STATED: the same class in a SECOND FILE,
#     or one instance where the missing end-to-end drive let a WRONG VERDICT
#     PUBLISH rather than merely blocking one. Either is owed upward at once.
#
# The three gaps declared since this file was written stand unchanged: it cannot
# catch wrong field names, cannot catch a missing runtime environment, and C3
# covers only the comparator -- not the driver and not the case inputs.
# =============================================================================

import argparse
import hashlib
import math
import os
import re
import subprocess
import sys
import tempfile

# ---- status vocabulary for a single check -----------------------------------
PASS = "PASS"
REFUSE = "REFUSE"
WARN = "WARN"
UNDET = "UNDETERMINED"

# A check's status is blocking (forces exit != 0) iff it is REFUSE or UNDET.
BLOCKING = (REFUSE, UNDET)


class Check:
    def __init__(self, cid, status, evidence):
        self.cid = cid
        self.status = status
        # evidence: list of strings, printed one per line under the check line.
        self.evidence = evidence if isinstance(evidence, list) else [evidence]

    def is_blocking(self):
        return self.status in BLOCKING

    def emit(self):
        head = "%-4s %-13s" % (self.cid, self.status)
        print("%s : %s" % (head, self.evidence[0] if self.evidence else ""))
        for extra in self.evidence[1:]:
            print("       %s" % extra)


# =============================================================================
# git / blob helpers
# =============================================================================
def blob_sha_worktree(path):
    """git blob sha of a file on disk, computed WITHOUT a repo (works pre-freeze
    and inside a tmp fixture). Equals `git hash-object <path>` for a plain file."""
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError:
        return None
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def repo_root_for(path):
    d = path if os.path.isdir(path) else os.path.dirname(path)
    try:
        out = subprocess.run(
            ["git", "-C", d, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def blob_sha_committed(freeze, relpath, repo_root):
    """git blob sha of relpath as committed at <freeze>."""
    try:
        out = subprocess.run(
            ["git", "-C", repo_root, "rev-parse", "%s:%s" % (freeze, relpath)],
            capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def committed_text(freeze, relpath, repo_root):
    try:
        out = subprocess.run(
            ["git", "-C", repo_root, "show", "%s:%s" % (freeze, relpath)],
            capture_output=True, text=True, check=True)
        return out.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


# =============================================================================
# discovery
# =============================================================================
REG_NAMES = ("PREREGISTRATION.md",)
COMPARATOR_GLOBS = ("analyse_", "grade_", "compare_", "grader_")


def find_registration(case_dir):
    for n in REG_NAMES:
        p = os.path.join(case_dir, n)
        if os.path.isfile(p):
            return p
    # fall back to any *PREREGISTRATION*.md, preferring the shortest name
    cands = [os.path.join(case_dir, f) for f in sorted(os.listdir(case_dir))
             if f.endswith(".md") and "PREREGISTRATION" in f.upper()]
    return cands[0] if cands else None


def find_comparator(case_dir, reg_text):
    """Prefer a .py NAMED in the registration as Comparator/Reader/grading_freeze;
    else the single grader-like .py in the case dir."""
    pys = [f for f in os.listdir(case_dir) if f.endswith(".py")]
    named = None
    for m in re.finditer(r"(?:grading_freeze|Comparator|Reader|grader)[^\n`]*?"
                         r"([A-Za-z0-9_./-]+\.py)", reg_text):
        base = os.path.basename(m.group(1))
        if base in pys:
            named = base
            break
    if named:
        return os.path.join(case_dir, named)
    grader_like = [f for f in pys
                   if any(f.startswith(pre) for pre in COMPARATOR_GLOBS)]
    if len(grader_like) == 1:
        return os.path.join(case_dir, grader_like[0])
    if len(grader_like) > 1:
        # ambiguous -- return the list marker so the caller can UNDET honestly
        return ("AMBIGUOUS", grader_like)
    if len(pys) == 1:
        return os.path.join(case_dir, pys[0])
    return None


def find_drivers(case_dir):
    """Return (good_drivers, tutorial_allruns). A good driver is a shell script
    that is NOT a tutorial Allrun and accepts a run-root argument."""
    good, tutorial = [], []
    for f in sorted(os.listdir(case_dir)):
        p = os.path.join(case_dir, f)
        if not os.path.isfile(p):
            continue
        if not (f.endswith(".sh") or f in ("Allrun", "Allclean", "Allrun.pre")):
            continue
        try:
            with open(p, errors="replace") as fh:
                txt = fh.read()
        except OSError:
            continue
        is_tutorial = bool(re.search(r'cd\s+"?\$\{0%/\*\}"?', txt)) or f == "Allrun"
        takes_runroot = bool(re.search(r'\$\{1[:?]', txt)) or \
            bool(re.search(r'=\s*"?\$\{1[:?-]', txt)) or \
            bool(re.search(r'(RUN_ROOT|RUNS|DIR|OUT)\s*=\s*"?\$\{?1\b', txt))
        if is_tutorial and not takes_runroot:
            tutorial.append((f, p, txt))
        elif takes_runroot:
            good.append((f, p, txt))
        else:
            # a shell script that is neither a clean tutorial nor a run-root
            # driver -- keep it as a weak candidate, classified by its content
            tutorial.append((f, p, txt)) if is_tutorial else good.append((f, p, txt))
    return good, tutorial


# =============================================================================
# text extraction: level-sets and refinement ratios
# =============================================================================
def _line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def extract_slash_triples(text):
    """Return list of (a,b,c,line) for numeric A/B/C triples that are NOT part of
    a longer path/number. Dates/versions are filtered by the geometric test the
    caller applies; here we only reject zeros and 4-digit-year-looking leads."""
    out = []
    for m in re.finditer(r"(?<![\d./])(\d{1,4})\s*/\s*(\d{1,4})\s*/\s*(\d{1,4})(?![\d/])",
                         text):
        a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 0 in (a, b, c):
            continue
        # reject an obvious date lead (a year with a small month)
        if 1900 <= a <= 2100 and b <= 12 and c <= 31:
            continue
        out.append((a, b, c, _line_of(text, m.start())))
    return out


def geometric_levelsets(triples):
    """Keep triples that read as a refinement level-set: strictly monotone
    increasing with two successive ratios that roughly agree (>1.05, within 50%).
    Returns list of dicts {tuple, r1, r2, line}."""
    keep = []
    for a, b, c, ln in triples:
        if not (a < b < c):
            continue
        r1, r2 = b / a, c / b
        if r1 <= 1.05 or r2 <= 1.05:
            continue
        lo = min(r1, r2)
        if abs(r1 - r2) / lo > 0.5:
            continue
        keep.append({"tuple": (a, b, c), "r1": r1, "r2": r2, "line": ln})
    return keep


def extract_ratio_claims(text):
    """Explicit refinement-ratio claims. Returns list of (value, line, snippet).
    Lowercase `r = N` only (uppercase R is a physical constant here); the phrase
    'refinement ratio ... N'; and the N/2N/4N idiom (=> 2)."""
    claims = []
    for m in re.finditer(r"(?<![A-Za-z])r\s*=\s*(\d+(?:\.\d+)?)", text):
        claims.append((float(m.group(1)), _line_of(text, m.start()),
                       "r = %s" % m.group(1)))
    for m in re.finditer(r"refinement ratio[^\n\d]{0,20}(\d+(?:\.\d+)?)", text, re.I):
        claims.append((float(m.group(1)), _line_of(text, m.start()),
                       "refinement ratio %s" % m.group(1)))
    for m in re.finditer(r"N(?:_g)?\s*/\s*2\s*N(?:_g)?\s*/\s*4\s*N(?:_g)?", text):
        claims.append((2.0, _line_of(text, m.start()), "N/2N/4N (=> r=2)"))
    return claims


# =============================================================================
# path extraction for C2
# =============================================================================
def literal_shell_vars(txt):
    """VAR="literal" assignments whose value has no $ or backtick. Resolved
    transitively so ${REPO}/... can be reduced when REPO is literal."""
    vars_ = {}
    for m in re.finditer(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"?([^"\n]*)"?\s*$',
                         txt, re.M):
        name, val = m.group(1), m.group(2).strip().strip('"')
        vars_[name] = val
    # transitive resolution (a few passes)
    for _ in range(5):
        changed = False
        for k, v in list(vars_.items()):
            nv = resolve_vars(v, vars_)
            if nv != v:
                vars_[k] = nv
                changed = True
        if not changed:
            break
    return vars_


def resolve_vars(s, vars_):
    def repl(m):
        name = m.group(1) or m.group(2)
        return vars_.get(name, m.group(0))
    return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)",
                  repl, s)


def _unquote(tok):
    return tok.strip().strip('"').strip("'")


def extract_shell_paths(txt):
    """Candidate filesystem paths from a shell driver -- ONLY from genuine
    path-operation positions, never arbitrary quoted strings. Extracting paths
    from free-form shell by regex is not reliably possible (echo/error messages
    are full of '/'); restricting to path operators is what keeps C2 from
    false-refusing on message text. Positions read: cp/mv/rsync src&dst;
    source/`.`; cd; mkdir -p; and file-test operators [ -e|-f|-d PATH ]."""
    cands = set()
    # a "command position" is line start or right after a statement separator --
    # this stops the word 'source'/'cd' inside an echo MESSAGE from being read as
    # a path operation (a real false-positive source seen on VMFL046).
    CMD = r'(?:^|[;&|(){]|&&|\|\||\bthen\b|\bdo\b|\belse\b)\s*'
    UQ = r'''("[^"]+"|'[^']+'|[^\s;&|)"']+)'''   # unquoted stops at ; & | ) quote
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        m = re.match(r'(?:cp|mv|rsync)\s+(?:-\S+\s+)*' + UQ + r'\s+' + UQ, s)
        if m:
            cands.add(_unquote(m.group(1)))
            cands.add(_unquote(m.group(2)))
        for m in re.finditer(CMD + r'(?:source|\.)\s+' + UQ, s):
            cands.add(_unquote(m.group(1)))
        for m in re.finditer(CMD + r'cd\s+' + UQ, s):
            cands.add(_unquote(m.group(1)))
        for m in re.finditer(CMD + r'mkdir\s+(?:-\S+\s+)*' + UQ, s):
            cands.add(_unquote(m.group(1)))
        for m in re.finditer(r'\[\[?\s*!?\s*-[efdsr]\s+' + UQ, s):
            cands.add(_unquote(m.group(1)))
    return cands


def extract_python_literal_paths(txt):
    """Only LITERAL string-constant paths in python (os.path.join with a var is
    runtime -> not returned here)."""
    cands = set()
    for m in re.finditer(r'''["']([^"'\n]*/[^"'\n]*)["']''', txt):
        s = m.group(1)
        # keep things that look like real fs paths, not regexes/format frags
        if s.startswith(("/", "cases/", "verification/", "docs/", "models/",
                         "./", "../")):
            cands.add(s)
    return cands


# =============================================================================
# THE CHECKS
# =============================================================================
def C1_launchability(case_dir):
    good, tutorial = find_drivers(case_dir)
    if not good and not tutorial:
        return Check("C1", REFUSE, "no driver script found in the case dir "
                     "(no *.sh, no Allrun) -- nothing to launch.")
    if not good and tutorial:
        names = ", ".join(t[0] for t in tutorial)
        return Check("C1", REFUSE,
                     ["the only executable(s) are tutorial-style: %s" % names,
                      "a script that does `cd \"${0%%/*}\"` runs in its own dir "
                      "and writes outputs into cases/ -- the filing rule forbids it; "
                      "no script accepts a run-root argument."])
    ev = ["run-root driver(s): %s" % ", ".join(g[0] for g in good)]
    if tutorial:
        ev.append("WARN: a tutorial Allrun is also present (%s) -- a latent hazard, "
                  "but a real driver exists so C1 passes."
                  % ", ".join(t[0] for t in tutorial))
    return Check("C1", PASS, ev)


def C2_path_existence(case_dir, comparator, drivers_txt):
    repo = repo_root_for(case_dir)
    # "frozen material" lives under the repo root (or, absent a repo -- e.g. a
    # selftest fixture -- under the case dir's parent). A missing path there is a
    # freeze defect (REFUSE); a missing path OUTSIDE it is an environment
    # dependency (WARN).
    material_root = repo or os.path.dirname(os.path.normpath(case_dir))
    case_dir = os.path.normpath(case_dir)
    missing_static = []
    runtime = []
    checked = 0
    env_missing = []
    seen = set()

    def classify(raw, vars_):
        nonlocal checked
        resolved = resolve_vars(raw, vars_).strip().strip('"').strip("'")
        # strip a trailing "/." used by cp
        disp = resolved
        test = resolved[:-2] if resolved.endswith("/.") else resolved
        if not test or "$" in test:
            if test:
                runtime.append(disp)
            return
        # ignore option-y or glob tokens and non-paths
        if test.startswith("-") or any(ch in test for ch in "*?") or "/" not in test:
            return
        # a path under verification/runs/ is a RUN OUTPUT created at launch, not
        # frozen material -- its existence is C7's domain (a WARN, an ordering
        # fix), never a C2 freeze-defect. Skip it here.
        if "verification/runs/" in test.replace("\\", "/"):
            return
        if disp in seen:
            return
        seen.add(disp)
        checked += 1
        if os.path.isabs(test):
            abspath = os.path.normpath(test)
        else:
            abspath = os.path.normpath(os.path.join(material_root, test))
        inside = (abspath == material_root or
                  abspath.startswith(material_root + os.sep) or
                  abspath.startswith(case_dir + os.sep))
        if os.path.exists(abspath):
            return
        if inside:
            missing_static.append(disp)
        else:
            env_missing.append(disp)

    for txt in drivers_txt:
        vars_ = literal_shell_vars(txt)
        for raw in extract_shell_paths(txt):
            classify(raw, vars_)
    if comparator and isinstance(comparator, str) and os.path.isfile(comparator):
        with open(comparator, errors="replace") as fh:
            ctxt = fh.read()
        for raw in extract_python_literal_paths(ctxt):
            classify(raw, {})

    ev = ["%d static path(s) checked" % checked]
    if runtime:
        ev.append("UNDETERMINED (runtime-only, deferred to launch -- listed, "
                  "not passed): " + "; ".join(sorted(runtime)[:8]) +
                  (" ..." if len(runtime) > 8 else ""))
    if env_missing:
        ev.append("WARN missing environment path(s) outside the repo: " +
                  "; ".join(sorted(env_missing)))
    if missing_static:
        ev.append("MISSING in-repo path(s) the freeze depends on: " +
                  "; ".join(sorted(missing_static)))
        return Check("C2", REFUSE, ev)
    if env_missing:
        return Check("C2", WARN, ev)
    return Check("C2", PASS, ev)


DEFERRAL_MARKERS = ("to be pinned", "to be captured", "to be committed",
                    "will be pinned", "tbd", "todo",
                    "flagged for the supervisor", "unpinned")


def C3_grading_pin(case_dir, comparator, reg_text, freeze):
    if comparator is None:
        return Check("C3", UNDET, "no comparator .py could be identified -- the "
                     "pin cannot be evaluated (not read as a pass).")
    if isinstance(comparator, tuple) and comparator[0] == "AMBIGUOUS":
        return Check("C3", UNDET, "multiple grader-like .py files (%s) and none "
                     "named in the registration -- comparator ambiguous, pin "
                     "cannot be evaluated." % ", ".join(comparator[1]))
    repo = repo_root_for(case_dir)
    if freeze is None:
        expected = blob_sha_worktree(comparator)
        src = "git hash-object (working tree)"
    else:
        rel = os.path.relpath(comparator, repo) if repo else None
        expected = blob_sha_committed(freeze, rel, repo) if rel else None
        src = "committed blob at %s" % freeze
    if expected is None:
        return Check("C3", UNDET, "could not compute the comparator's blob (%s)."
                     % src)
    name = os.path.basename(comparator)
    if expected in reg_text:
        return Check("C3", PASS, "comparator %s pinned; registration carries its "
                     "blob %s (%s)." % (name, expected, src))
    # a matching pin is absent -- is there some OTHER comparator pin (=> wrong)?
    other = re.findall(r"\b[0-9a-f]{40}\b", reg_text)
    # only treat as a "comparator pin" one that sits near a grading marker
    comp_pins = []
    for m in re.finditer(r"\b([0-9a-f]{40})\b", reg_text):
        ctx = reg_text[max(0, m.start() - 200):m.start() + 40].lower()
        if any(w in ctx for w in ("grading_freeze", "comparator", "grader",
                                  "reader", "git blob", "hash-object",
                                  ".py")):
            comp_pins.append(m.group(1))
    if comp_pins:
        return Check("C3", REFUSE,
                     ["comparator %s: registration carries a comparator blob pin "
                      "%s that does NOT match the file's blob %s (%s)."
                      % (name, comp_pins[0], expected, src)])
    # no pin at all -- distinguish an explicit deferral from a plain omission
    marker_lines = []
    for i, line in enumerate(reg_text.splitlines(), 1):
        low = line.lower()
        if any(mk in low for mk in DEFERRAL_MARKERS) and \
           ("pin" in low or "comparator" in low or "grad" in low or "blob" in low):
            marker_lines.append("L%d: %s" % (i, line.strip()[:100]))
    ev = ["comparator %s: NO 40-hex blob pin for the comparator in the "
          "registration (expected %s, %s)." % (name, expected, src)]
    if marker_lines:
        ev.append("deferral marker(s) present -- the pin was left open: " +
                  " | ".join(marker_lines[:3]))
    return Check("C3", REFUSE, ev)


LEVEL_ID_RE = re.compile(r"\b([A-Z]\d{1,2})\b")


def levels_from_driver(driver_txt):
    """The authoritative level set is the DRIVER's own dispatch, not noisy prose.
    Read: a usage string <L1|L2|L3|B2|C1>; case arms `L1)`; declare-array keys
    `[L1]=`; and `for L in L1 L2 L3` lists."""
    ids = set()
    for m in re.finditer(r"<([A-Za-z0-9|]+)>", driver_txt):
        parts = m.group(1).split("|")
        if all(re.fullmatch(r"[A-Z]{1,3}\d{1,2}", p) for p in parts) and len(parts) >= 2:
            ids.update(parts)
    for m in re.finditer(r"(?m)^\s*([A-Z]{1,3}\d{1,2})\)", driver_txt):
        ids.add(m.group(1))
    for m in re.finditer(r"\[([A-Z]{1,3}\d{1,2})\]", driver_txt):
        ids.add(m.group(1))
    for m in re.finditer(r"for\s+\w+\s+in\s+([A-Z0-9 ]+?)(?:;|\bdo\b)", driver_txt):
        toks = m.group(1).split()
        if len(toks) >= 2 and all(re.fullmatch(r"[A-Z]{1,3}\d{1,2}", t) for t in toks):
            ids.update(toks)
    return ids


def declared_level_ids(reg_text):
    """Fallback (no driver): level ids from prose that sit in a level context."""
    ids = {}
    lines = reg_text.splitlines()
    for m in re.finditer(r"\b([SLM]\d{1,2})\b", reg_text):
        lid = m.group(1)
        ln = _line_of(reg_text, m.start())
        line = lines[ln - 1] if ln - 1 < len(lines) else ""
        low = line.lower()
        if any(w in low for w in ("level", "mesh", "grid", "coarse", "medium",
                                  "fine", "triple", "cells", "refine", "group",
                                  "family", "instance")):
            ids.setdefault(lid, ln)
    return ids


def count_size_group_fields(case_dir):
    """Count f<i> size-group field files across 0 / 0.orig (population-balance)."""
    best = 0
    for sub in ("0.orig", "0"):
        d = os.path.join(case_dir, sub)
        if os.path.isdir(d):
            n = len([f for f in os.listdir(d) if re.match(r"^f\d+(\.|$)", f)])
            best = max(best, n)
    return best


def has_committed_generator(case_dir, comparator, drivers):
    """A committed/pinned script (not the driver, not the comparator) that emits
    grids/feeds/size groups."""
    comp_base = os.path.basename(comparator) if isinstance(comparator, str) else ""
    drv_bases = {os.path.basename(p) for _, p, _ in drivers}
    for f in os.listdir(case_dir):
        if not (f.endswith(".py") or f.endswith(".sh")):
            continue
        if f == comp_base or f in drv_bases:
            continue
        p = os.path.join(case_dir, f)
        try:
            with open(p, errors="replace") as fh:
                t = fh.read().lower()
        except OSError:
            continue
        if any(w in t for w in ("sizegroup", "quadrature", "kumar", "ramkrishna",
                                "generate grid", "feed", "abscissa", "def generate")):
            return f
    return None


def find_templates(case_dir):
    tmpls = []
    for root, _dirs, files in os.walk(case_dir):
        for f in files:
            if f.endswith(".template"):
                tmpls.append(os.path.join(root, f))
            else:
                # a file carrying @TOKEN@ placeholders is a template too
                p = os.path.join(root, f)
                try:
                    with open(p, errors="replace") as fh:
                        head = fh.read(4000)
                    if re.search(r"@[A-Z0-9_]{2,}@|__[A-Z0-9_]{2,}__", head):
                        tmpls.append(p)
                except OSError:
                    pass
    return tmpls


def C4_level_completeness(case_dir, reg_text, comparator, drivers):
    driver_txt = "\n".join(t for _, _, t in drivers)
    problems = []
    considered = False
    sym_levels = set()

    # -- (i) group-count triple (population-balance size groups) ---------------
    triples = geometric_levelsets(extract_slash_triples(reg_text))
    group_triples = []
    for ls in triples:
        ln = ls["line"]
        line = reg_text.splitlines()[ln - 1] if ln - 1 < len(reg_text.splitlines()) else ""
        window = " ".join(reg_text.splitlines()[max(0, ln - 3):ln + 2]).lower()
        if any(w in window for w in ("group", "class count", "n_g", "size class",
                                     "size group", "sectional")):
            group_triples.append(ls)
    present_groups = count_size_group_fields(case_dir)
    if group_triples and present_groups:
        considered = True
        gen = has_committed_generator(case_dir, comparator, drivers)
        # pick the gate triple: the one whose context mentions gate/section-7/ruling
        gate = group_triples[-1]
        counts = gate["tuple"]
        constructible = [g for g in counts
                         if g == present_groups or gen is not None]
        if len(constructible) < len(counts):
            missing = [g for g in counts if g not in constructible]
            problems.append(
                "group-count triple %s: only the %d-group instance is frozen "
                "(measured %d f<i> field files); no committed generator (%s); "
                "missing instance(s): %s"
                % ("/".join(map(str, counts)), present_groups, present_groups,
                   gen or "none found",
                   ", ".join("%d-group" % g for g in missing)))

    # -- (ii) symbolic spatial levels -- ONLY when a group-count triple does not
    #     already govern (a population-balance case's levels ARE the group
    #     counts; mechanism (i) is authoritative there). The level set is taken
    #     from the DRIVER's dispatch (authoritative); prose is the no-driver
    #     fallback only.
    if not group_triples:
        drv_levels = levels_from_driver(driver_txt)
        if drv_levels:
            considered = True
            sym_levels = drv_levels
            tmpls = find_templates(case_dir)
            gen = has_committed_generator(case_dir, comparator, drivers)
            existing_dirs = set()
            for _root, dnames, _f in os.walk(case_dir):
                existing_dirs.update(dnames)
            for lid in sorted(drv_levels):
                ok = False
                if lid in existing_dirs:
                    ok = True                      # (a) a per-level directory
                elif tmpls:
                    ok = True                      # (b) token-template the driver fills
                elif gen is not None:
                    ok = True                      # (c) a committed generator
                if not ok:
                    problems.append(
                        "level %s (driver-declared): no per-level dir, no token "
                        "template for the driver to fill, no committed generator "
                        "-- not constructible from frozen material." % lid)
        else:
            ids = declared_level_ids(reg_text)
            if ids:
                considered = True
                tmpls = find_templates(case_dir)
                gen = has_committed_generator(case_dir, comparator, drivers)
                existing_dirs = set()
                for _root, dnames, _f in os.walk(case_dir):
                    existing_dirs.update(dnames)
                sym_levels = set(ids)
                for lid, ln in sorted(ids.items()):
                    if lid in existing_dirs or tmpls or gen is not None:
                        continue
                    problems.append(
                        "level %s (registration L%d): no per-level dir, no token "
                        "template, no committed generator, and NO committed driver "
                        "at all -- not constructible from frozen material."
                        % (lid, ln))

    if not considered:
        return Check("C4", UNDET, "no level/instance identifiers could be "
                     "extracted from the registration -- completeness cannot be "
                     "evaluated (not read as a pass).")
    if problems:
        return Check("C4", REFUSE, problems)
    ev = []
    if group_triples:
        ev.append("group-count triple(s) %s: all instances constructible "
                  "(present %d f<i> fields / generator)."
                  % (", ".join("/".join(map(str, g["tuple"])) for g in group_triples),
                     present_groups))
    if sym_levels:
        ev.append("symbolic levels %s: all constructible."
                  % ", ".join(sorted(sym_levels)))
    return Check("C4", PASS, ev or ["all declared levels constructible."])


def C5_internal_consistency(reg_text):
    levelsets = geometric_levelsets(extract_slash_triples(reg_text))
    families = {}
    for ls in levelsets:
        families.setdefault(ls["tuple"], ls["line"])
    claims = extract_ratio_claims(reg_text)

    # distinct ratio values: from claims + from each level-set's mean ratio
    ratio_vals = {}
    for v, ln, snip in claims:
        ratio_vals.setdefault(round(v, 2), "L%d %s" % (ln, snip))
    for ls in levelsets:
        rmean = round(math.sqrt(ls["r1"] * ls["r2"]), 2)
        ratio_vals.setdefault(rmean, "L%d level-set %s (r=%.3f)"
                              % (ls["line"], "/".join(map(str, ls["tuple"])), rmean))

    problems = []
    if len(families) > 1:
        problems.append("MORE THAN ONE refinement level-set family declared: " +
                        "; ".join("%s (L%d)" % ("/".join(map(str, t)), families[t])
                                  for t in families))
    if len(ratio_vals) > 1:
        problems.append("MORE THAN ONE refinement ratio declared: " +
                        "; ".join("r=%s at %s" % (r, ratio_vals[r])
                                  for r in sorted(ratio_vals)))
    if problems:
        return Check("C5", REFUSE, problems)
    ev = []
    if families:
        t = list(families)[0]
        ev.append("one level-set family %s (L%d)"
                  % ("/".join(map(str, t)), families[t]))
    if ratio_vals:
        r = list(ratio_vals)[0]
        ev.append("one refinement ratio r=%s (%s)" % (r, ratio_vals[r]))
    if not ev:
        ev = ["no level-set / refinement-ratio declared -- nothing to contradict."]
    return Check("C5", PASS, ev)


def comparator_hardcoded_ratio(comparator):
    if not (isinstance(comparator, str) and os.path.isfile(comparator)):
        return None, []
    with open(comparator, errors="replace") as fh:
        txt = fh.read()
    vals, ev = [], []
    # named refinement-ratio parameters
    for pat in (r"\brref\s*=\s*(\d+(?:\.\d+)?)",
                r"\bR_REFINE\b[^\n=]*=\s*(\d+(?:\.\d+)?)",
                r"def\s+roache\s*\([^)]*\br\s*=\s*(\d+(?:\.\d+)?)",
                r"def\s+gci\s*\([^)]*\brref\s*=\s*(\d+(?:\.\d+)?)"):
        for m in re.finditer(pat, txt):
            v = float(m.group(1))
            vals.append(v)
            ev.append("L%d: %s" % (_line_of(txt, m.start()),
                                   m.group(0).strip()[:60]))
    # def roache(..., r=IDENT) with IDENT = number elsewhere
    for m in re.finditer(r"def\s+(?:roache|gci)\s*\([^)]*\br(?:ref)?\s*=\s*"
                         r"([A-Za-z_]\w*)", txt):
        ident = m.group(1)
        vm = re.search(r"\b%s\s*=\s*(\d+(?:\.\d+)?)" % re.escape(ident), txt)
        if vm:
            vals.append(float(vm.group(1)))
            ev.append("L%d: r=%s, %s=%s" % (_line_of(txt, m.start()), ident,
                                            ident, vm.group(1)))
    # math.log(2.0) used as an accuracy-order base in a gci/roache exponent
    for m in re.finditer(r"math\.log\([^)]*\)\s*/\s*math\.log\(\s*(\d+(?:\.\d+)?)\s*\)",
                         txt):
        # only count when it sits in a function that also computes p / GCI
        seg = txt[max(0, m.start() - 400):m.start()]
        if "def gci" in seg or "def roache" in seg or "rref" in seg or "p =" in txt[m.start()-30:m.start()+5]:
            vals.append(float(m.group(1)))
            ev.append("L%d: %s" % (_line_of(txt, m.start()), m.group(0).strip()[:60]))
    return (vals, ev)


def C6_const_agreement(reg_text, comparator):
    vals, cev = comparator_hardcoded_ratio(comparator)
    if not vals:
        return Check("C6", PASS, "comparator hardcodes no refinement ratio "
                     "(GCI ratio derived from the data) -- nothing to disagree.")
    cset = sorted(set(round(v, 3) for v in vals))
    # registration side: explicit claims + level-set successive ratios
    reg_ratios = []
    for v, ln, snip in extract_ratio_claims(reg_text):
        reg_ratios.append((round(v, 3), "L%d %s" % (ln, snip)))
    for ls in geometric_levelsets(extract_slash_triples(reg_text)):
        # only gate-relevant / group-context or the sole level-set
        reg_ratios.append((round(ls["r1"], 3),
                           "L%d %s (b/a)" % (ls["line"], "/".join(map(str, ls["tuple"])))))
        reg_ratios.append((round(ls["r2"], 3),
                           "L%d %s (c/b)" % (ls["line"], "/".join(map(str, ls["tuple"])))))

    tol = 0.05
    disagreements = []
    for rc in cset:
        for rr, where in reg_ratios:
            if rc <= 0 or rr <= 0:
                continue
            if abs(rc - rr) / rc > tol:
                disagreements.append(
                    "comparator r=%s disagrees with registration r=%s (%s)"
                    % (rc, rr, where))
    # a non-constant declared level-set makes any single hardcoded r wrong
    for ls in geometric_levelsets(extract_slash_triples(reg_text)):
        if abs(ls["r1"] - ls["r2"]) / min(ls["r1"], ls["r2"]) > 0.02:
            for rc in cset:
                disagreements.append(
                    "comparator assumes a CONSTANT r=%s but level-set %s has "
                    "NON-CONSTANT ratios %.4f then %.4f (L%d) -- any single r is wrong"
                    % (rc, "/".join(map(str, ls["tuple"])), ls["r1"], ls["r2"],
                       ls["line"]))
    if disagreements:
        ev = ["comparator hardcodes: " + "; ".join(cev)]
        ev.extend(sorted(set(disagreements))[:6])
        return Check("C6", REFUSE, ev)
    return Check("C6", PASS, ["comparator hardcodes r=%s; agrees with the "
                              "registration's declared ratio(s)."
                              % ",".join(map(str, cset))])


def C7_run_root(case_dir, runs_base=None):
    case = os.path.basename(os.path.normpath(case_dir))
    repo = repo_root_for(case_dir) or os.path.dirname(os.path.dirname(
        os.path.dirname(case_dir)))
    base = runs_base or os.path.join(repo, "verification", "runs",
                                     "ansys_verification")
    run_root = os.path.join(base, case)
    if not os.path.isdir(run_root):
        return Check("C7", WARN,
                     ["run root %s does NOT exist." % run_root,
                      "queue_runner.py chdirs into cwd and Popen(cwd=) raises "
                      "FileNotFoundError, so the entry is recorded LAUNCHED and "
                      "dies. The fix is ordering (create the run root before the "
                      "queue row), NOT a change to the freeze."])
    entries = [e for e in os.listdir(run_root) if not e.startswith(".")]
    if entries:
        return Check("C7", PASS, "run root %s exists and is NON-EMPTY (%d "
                     "entries) -- a run may be present; do not disturb."
                     % (run_root, len(entries)))
    return Check("C7", PASS, "run root %s exists and is empty -- ready." % run_root)


# =============================================================================
# driver
# =============================================================================
def run_all(case_dir, freeze=None, runs_base=None):
    if not os.path.isdir(case_dir):
        print("C0   %-13s : case dir does not exist: %s" % (UNDET, case_dir))
        return 3
    reg_path = find_registration(case_dir)
    if reg_path is None:
        print("C0   %-13s : no PREREGISTRATION.md in %s" % (UNDET, case_dir))
        return 2
    if freeze is None:
        with open(reg_path, errors="replace") as fh:
            reg_text = fh.read()
    else:
        repo = repo_root_for(case_dir)
        rel = os.path.relpath(reg_path, repo) if repo else None
        reg_text = committed_text(freeze, rel, repo) if rel else None
        if reg_text is None:
            print("C0   %-13s : could not read registration at freeze %s"
                  % (UNDET, freeze))
            return 2

    comparator = find_comparator(case_dir, reg_text)
    good, tutorial = find_drivers(case_dir)
    all_drivers = good + tutorial
    drivers_txt = [t for _, _, t in all_drivers]

    print("# check_freeze_ready.py  case=%s  freeze=%s"
          % (os.path.basename(os.path.normpath(case_dir)),
             freeze or "WORKING-TREE"))
    print("# registration: %s" % os.path.relpath(reg_path, os.getcwd()))
    if isinstance(comparator, str):
        print("# comparator  : %s" % os.path.basename(comparator))
    print("")

    checks = [
        C1_launchability(case_dir),
        C2_path_existence(case_dir, comparator, drivers_txt),
        C3_grading_pin(case_dir, comparator, reg_text, freeze),
        C4_level_completeness(case_dir, reg_text, comparator, all_drivers),
        C5_internal_consistency(reg_text),
        C6_const_agreement(reg_text, comparator),
        C7_run_root(case_dir, runs_base),
    ]
    for c in checks:
        c.emit()

    blocking = [c for c in checks if c.is_blocking()]
    print("")
    if blocking:
        print("VERDICT: NOT FREEZE-READY -- %d blocking check(s): %s"
              % (len(blocking), ", ".join("%s(%s)" % (c.cid, c.status)
                                          for c in blocking)))
        return 2
    print("VERDICT: freeze-ready -- all checks PASS/WARN.")
    return 0


# =============================================================================
# SELFTEST -- one planted failure + one positive control per check (L-487).
# No bare assert (would vanish under -O); explicit raise via _expect.
# =============================================================================
def _expect(label, got, want):
    ok = (got == want)
    print("  [%s] %-40s got=%-13s want=%-13s" %
          ("ok " if ok else "XX ", label, got, want))
    return ok


def _mk(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(content)


def selftest():
    tmp = tempfile.mkdtemp(prefix="fchk_selftest_")
    results = []

    # ---- C1 -----------------------------------------------------------------
    neg = os.path.join(tmp, "c1_neg")
    os.makedirs(neg)
    _mk(os.path.join(neg, "Allrun"),
        '#!/bin/sh\ncd "${0%/*}" || exit\nblockMesh\n')
    _mk(os.path.join(neg, "PREREGISTRATION.md"), "x\n")
    results.append(_expect("C1 neg (tutorial-only)",
                           C1_launchability(neg).status, REFUSE))
    pos = os.path.join(tmp, "c1_pos")
    os.makedirs(pos)
    _mk(os.path.join(pos, "run_x.sh"),
        '#!/bin/bash\nRUN_ROOT="${1:?usage}"\nmkdir -p "$RUN_ROOT"\n')
    results.append(_expect("C1 pos (run-root driver)",
                           C1_launchability(pos).status, PASS))

    # ---- C2 -----------------------------------------------------------------
    neg = os.path.join(tmp, "c2_neg")
    os.makedirs(neg)
    drv = ('#!/bin/bash\nREPO="%s"\nCASE_ID="c2_neg"\n'
           'cp -r "${REPO}/%s/base/." "$OUT/"\n'
           'RUN_ROOT="${1:?}"\n' % (os.path.dirname(neg), "c2_neg"))
    # base/ deliberately absent under the case dir -> static in-repo miss
    res = C2_path_existence(neg, None, [drv])
    results.append(_expect("C2 neg (missing base/)", res.status, REFUSE))
    pos = os.path.join(tmp, "c2_pos")
    os.makedirs(os.path.join(pos, "base"))
    drv2 = ('#!/bin/bash\nREPO="%s"\nCASE_ID="c2_pos"\n'
            'cp -r "${REPO}/%s/base/." "$OUT/"\n'
            'cp -r "$RUN_ROOT/$LEVEL/x" "$dst"\n'  # runtime -> UNDET, not fail
            % (os.path.dirname(pos), "c2_pos"))
    res = C2_path_existence(pos, None, [drv2])
    results.append(_expect("C2 pos (base exists, runtime listed)",
                           res.status, PASS))

    # ---- C3 -----------------------------------------------------------------
    neg = os.path.join(tmp, "c3_neg")
    os.makedirs(neg)
    _mk(os.path.join(neg, "grade_x.py"), "# comparator\nprint('hi')\n")
    reg_neg = ("Comparator: grade_x.py -- to be pinned by blob before grading.\n")
    results.append(_expect("C3 neg (deferred pin)",
                           C3_grading_pin(neg,
                                          os.path.join(neg, "grade_x.py"),
                                          reg_neg, None).status, REFUSE))
    pos = os.path.join(tmp, "c3_pos")
    os.makedirs(pos)
    comp = os.path.join(pos, "grade_x.py")
    _mk(comp, "# comparator\nprint('hi')\n")
    good_pin = blob_sha_worktree(comp)
    reg_pos = "grading_freeze grade_x.py\ngit blob %s\n" % good_pin
    results.append(_expect("C3 pos (correct pin)",
                           C3_grading_pin(pos, comp, reg_pos, None).status, PASS))
    # extra planted: a WRONG pin must also REFUSE (a restrictive guard's teeth)
    reg_wrong = "grading_freeze grade_x.py\ngit blob %s\n" % ("0" * 40)
    results.append(_expect("C3 neg (wrong pin)",
                           C3_grading_pin(pos, comp, reg_wrong, None).status,
                           REFUSE))

    # ---- C4 -----------------------------------------------------------------
    # neg: group triple 2/4/8 with only a 4-field instance and no generator
    neg = os.path.join(tmp, "c4_neg")
    os.makedirs(os.path.join(neg, "0.orig"))
    for i in range(4):
        _mk(os.path.join(neg, "0.orig", "f%d.air" % i), "0\n")
    reg_neg = ("The size-group triple over class count 2/4/8 (three levels).\n"
               "S1 coarse, S2 medium, S3 fine group instance.\n")
    results.append(_expect("C4 neg (2 of 3 group instances absent)",
                           C4_level_completeness(neg, reg_neg, None, []).status,
                           REFUSE))
    # pos: L1 L2 L3 with a token template + a driver that dispatches each
    pos = os.path.join(tmp, "c4_pos")
    os.makedirs(os.path.join(pos, "system"))
    _mk(os.path.join(pos, "system", "blockMeshDict.template"),
        "hex (0 1 2 3) (__NX__ __NY__ 1)\n")
    drv = ('#!/bin/bash\nRUN_ROOT="${1:?}"\n'
           'declare -A NX=( [L1]=16 [L2]=32 [L3]=64 )\n'
           'for L in L1 L2 L3; do echo "level $L mesh"; done\n')
    _mk(os.path.join(pos, "run_x.sh"), drv)
    reg_pos = ("Grid family: L1 32^2 cells (coarse), L2 64^2 (medium mesh), "
               "L3 128^2 (fine mesh). Three-level r = 2 triple.\n")
    dpos = find_drivers(pos)[0]
    results.append(_expect("C4 pos (template+dispatch L1/L2/L3)",
                           C4_level_completeness(pos, reg_pos, None, dpos).status,
                           PASS))

    # ---- C5 -----------------------------------------------------------------
    reg_neg = ("The concrete N_g (10/20/40 is the intended family) ... "
               "refinement ratio r = 2 on class count.\n"
               "The section-7 triple over group count 25 / 35 / 50.\n")
    results.append(_expect("C5 neg (two level-sets/ratios)",
                           C5_internal_consistency(reg_neg).status, REFUSE))
    reg_pos = ("Grid family 40/80/160 cells, three-level r = 2 triple, "
               "refinement ratio 2 throughout.\n")
    results.append(_expect("C5 pos (one level-set, one ratio)",
                           C5_internal_consistency(reg_pos).status, PASS))

    # ---- C6 -----------------------------------------------------------------
    neg = os.path.join(tmp, "c6_neg")
    os.makedirs(neg)
    _mk(os.path.join(neg, "analyse_x.py"),
        "import math\n"
        "def gci(coarse, medium, fine, Fs=1.25, rref=2.0):\n"
        "    p = math.log(2.0)/math.log(rref)\n    return p\n")
    reg_neg = "The section-7 triple over group count 25 / 35 / 50 (gate).\n"
    results.append(_expect("C6 neg (rref=2 vs 25/35/50)",
                           C6_const_agreement(reg_neg,
                                              os.path.join(neg, "analyse_x.py")).status,
                           REFUSE))
    pos = os.path.join(tmp, "c6_pos")
    os.makedirs(pos)
    _mk(os.path.join(pos, "analyse_x.py"),
        "import math\n"
        "def gci(coarse, medium, fine, Fs=1.25, rref=2.0):\n"
        "    return rref\n")
    reg_pos = "Grid family 40/80/160 cells, r = 2 triple.\n"
    results.append(_expect("C6 pos (rref=2 vs 40/80/160)",
                           C6_const_agreement(reg_pos,
                                              os.path.join(pos, "analyse_x.py")).status,
                           PASS))

    # ---- C7 -----------------------------------------------------------------
    case7 = os.path.join(tmp, "VMFLX")
    os.makedirs(case7)
    empty_base = os.path.join(tmp, "runs_empty")
    os.makedirs(os.path.join(empty_base, "VMFLX"))
    results.append(_expect("C7 pos (run root exists empty)",
                           C7_run_root(case7, runs_base=empty_base).status, PASS))
    absent_base = os.path.join(tmp, "runs_absent")
    os.makedirs(absent_base)
    results.append(_expect("C7 warn (run root absent -> WARN, not refuse)",
                           C7_run_root(case7, runs_base=absent_base).status, WARN))

    print("")
    n_ok = sum(1 for r in results if r)
    print("SELFTEST: %d/%d fixtures behaved as designed." % (n_ok, len(results)))
    return 0 if n_ok == len(results) else 2


def main():
    ap = argparse.ArgumentParser(description="Pre-freeze readiness check for "
                                 "an Ansys VM case.")
    ap.add_argument("--case", help="path to the case directory")
    ap.add_argument("--freeze", default=None,
                    help="commit-ish to read frozen blobs from "
                         "(default: WORKING TREE)")
    ap.add_argument("--selftest", action="store_true",
                    help="run planted-failure self-tests and exit")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.case:
        ap.print_usage()
        print("error: --case is required (or use --selftest)", file=sys.stderr)
        return 3
    try:
        return run_all(os.path.abspath(args.case), freeze=args.freeze)
    except Exception as exc:  # never let an internal error read as a pass
        print("INTERNAL ERROR (not a pass): %r" % exc, file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
