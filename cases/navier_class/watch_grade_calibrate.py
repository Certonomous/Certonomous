#!/usr/bin/env python3
# =====================================================================================
# DETACHED GRADE-AND-CALIBRATE WATCHER  --  cfd team, navier_class
#
# WHY THIS EXISTS.  Two graded cfd runs were launched detached on 2026-09-10 and both
# were, at launch, missing a piece of the chain that turns a finished solve into a
# LANDED VERDICT with a rule-12 calibration row:
#
#   * SUBOFF-R1-TRIPLE was launched WITHOUT `--grade`, so its launcher solves and then
#     prints the grading command for a human.  Nobody is there to type it.  With every
#     agent dead the triple finishes and NO verdict is ever produced.
#   * SUP_BOOSTER-E2 DOES autograde from inside its own detached launcher, but its
#     queue entry omitted `grading_freeze`, so the runner never pinned the comparator.
#     Standing rule 2 (frozen grading path) is therefore undischarged for E2, and the
#     by-hand hash check is the compensating control.
#   * NEITHER writes the CLAUDE.md rule-12 estimate-vs-actual row.  There is no cfd row
#     on docs/COST_CALIBRATION.md at all.
#
# This watcher supplies exactly those missing pieces and NOTHING ELSE.  It does not
# launch compute, does not signal any process, and removes nothing.
#
# -------------------------------------------------------------------------------------
# EVERY RULE BELOW EXISTS BECAUSE SOMETHING BROKE ON IT BEFORE.
# -------------------------------------------------------------------------------------
#
# (1) rc IS CAPTURED INSIDE THIS PROCESS, NEVER AROUND THE `setsid` LINE.
#     `setsid timeout cmd` returns 0 for EVERY outcome -- success, non-zero, SIGKILL,
#     timeout -- so an rc read by whoever launched this watcher is decoration.  The
#     grader's rc is read from subprocess.CompletedProcess.returncode on the line after
#     it returns, INSIDE run_grader_capture_rc(), and written to a named sidecar before
#     anything else is decided.  `--selftest-plant` drives that exact function with a
#     grader planted to exit non-zero and REFUSES unless the sidecar records it.
#
# (2) COMPLETION IS POLLED FROM ONE NAMED ARTIFACT.  NEVER A GLOB.
#     `grep` on this box is ugrep, multi-threaded, and interleaves multi-file output:
#     a glob-fed `tail -1` was measured 21/30 correct, and `-J1`/`--sort` make it
#     deterministically WRONG rather than merely unreliable.  Every read here names one
#     file: SUBOFF polls PROGRESS.R1_triple.txt for the launcher's own terminal line;
#     E2 polls graded_e2/LAUNCHER_DONE.  No `glob`, no `*`, no directory listing is used
#     to decide completion.
#
# (3) THE FROZEN GRADING PATH IS CHECKED BY THIS WATCHER, BEFORE IT GRADES.
#     The grader on disk is hashed as a GIT BLOB (sha1 over b"blob <len>\0" + bytes,
#     computed in-process -- it does not shell out to git and so cannot be fooled by a
#     dirty index) and compared against the sha pinned in the supervisor's brief and in
#     the run's freeze.  On ANY drift the watcher REFUSES to grade and records the
#     refusal.  It never grades anyway and never "notes a discrepancy" and proceeds --
#     a printed discrepancy labelled non-binding is worse than one never computed.
#     For E2, whose autograder fires on its own, the hash is re-checked at EVERY POLL
#     for the whole life of the run, so drift that happens BEFORE the autograde is
#     caught rather than discovered afterwards; a verdict produced while the hash was
#     wrong is QUARANTINED, not accepted.
#
# (4) NO GUARD IS AN `assert`.  Under `python3 -O` every assert is deleted, so a refusal
#     written as one is a refusal an interpreter flag can switch off.  There is no
#     `assert` statement anywhere in this file; every guard is `if ...: <refuse>`.
#
# (5) NOTHING BELONGING TO A RUN IS DELETED.  There is no shutil.rmtree, no os.remove
#     and no os.unlink in this file, and no `rm` that names anything under a run root.
#     The ONE deletion in this file is `rm -f "$GIT_INDEX_FILE"` inside LAND_SH, on the
#     watcher's OWN private scratch index under --scratch -- that line is required by the
#     rule-10 private-index protocol and touches no repository content.  Stated here
#     rather than left as a blanket 'there is no rm', which would have been false.
#     Unexpected state is a REFUSAL that is recorded, never something to clear.
#
# (6) IDEMPOTENT.  If the verdict sidecar for a run already exists, the watcher does not
#     re-grade and does not overwrite it.  It exits reporting the existing record.  Two
#     watchers racing on one run therefore produce one verdict, not two.
#
# (7) THE CALIBRATION ROW IS WRITTEN BY THIS WATCHER, NOT OWED TO A FUTURE AGENT.
#     Tier A, ALWAYS: a complete ready-to-append row is written to a named file beside
#     the run.  Tier B, ATTEMPTED: the row is landed on docs/COST_CALIBRATION.md through
#     the canonical scripts/append_record.py (which mints a collision-free id from a
#     clock reading and a hash, reading nothing the record contains) and committed under
#     the CLAUDE.md rule-10 private-index protocol with CAS and a post-commit verify.
#     If Tier B fails for any reason it is RECORDED as failed and Tier A stands.  An
#     honest half-measure beats a silent failure.
# =====================================================================================

import argparse
import ast
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import time

REPO = "/home/ubuntu/Certonomous"
LEDGER = "docs/COST_CALIBRATION.md"
RATE_USD_PER_CORE_H = 0.0513          # c7a.4xlarge, reported-by-owner, NOT measured

# The 3600-s stall rule of COMPUTE_BUDGET_CHARTER section 2: a row over 3600 wall s is a
# stall, and `cleaned` is gross minus the rows it matches.  Applied literally below.
STALL_WALL_S = 3600


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_blob_sha1(path: str) -> str:
    """The git blob sha of a file ON DISK, computed here.

    Deliberately NOT `git hash-object`: that reads repository state, and the shared
    index on this box is routinely stale under concurrency.  This is the plain object
    formula, so the answer depends on the bytes and nothing else.
    """
    with open(path, "rb") as fh:
        data = fh.read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


# -------------------------------------------------------------------------------------
# RULE (1): rc CAPTURED INSIDE THIS PROCESS.
# -------------------------------------------------------------------------------------
def run_grader_capture_rc(argv, stdout_path, rc_path):
    """Run the grader; read its rc INSIDE this process; write the rc sidecar FIRST.

    The sidecar is written before any verdict is interpreted, so a watcher killed
    between the grader returning and the verdict being read still leaves the rc on
    disk.  Returns the rc as an int.  This is the function `--selftest-plant` drives.
    """
    with open(stdout_path, "wb") as out:
        completed = subprocess.run(argv, stdout=out, stderr=subprocess.STDOUT)
    rc = completed.returncode                    # <-- INSIDE. The line after it returns.
    with open(rc_path, "w") as fh:
        fh.write("rc=%d\nrc_captured=inside_this_watcher_process\ncaptured_utc=%s\n"
                 % (rc, utc()))
    os.sync() if hasattr(os, "sync") else None
    return rc


# -------------------------------------------------------------------------------------
# THE COST-CHANNEL READER, AND WHY IT LOOKS LIKE THIS.
#
# DEFECT REPAIRED 2026-09-10 (cfd).  The reader below used to iterate line by line and
# do `k, _, v = line.partition("=")`, taking the WHOLE remainder of the line as the
# value.  The SUP_BOOSTER launcher writes all four pairs on ONE line --
#     level=coarse rc_solve=0 wall_s=290 timeout_s=800
# -- so the dict was {"level": "coarse rc_solve=0 wall_s=290 timeout_s=800"}, carrying
# NO `wall_s` and NO `rc_solve` key.  `float(st.get("wall_s","0") or 0)` then produced a
# FALSE 0.0 and `st.get("rc_solve","absent")` produced "absent", which is not "0", so
# every level was ALSO mis-sorted into waste_levels.  A 34.23 core-min run was committed
# to docs/COST_CALIBRATION.md as 0.00 core-min, ratio 0.00x, "waste 0.00 (every level
# returned rc=0)" -- a claim this reader never made.  Row
# C-20260910T052907.204386Z-e9df493d, commit 4749ae1d.  It was an INSTRUMENT defect in
# the cost reader, not a real zero.
#
# THE PARSING RULE, stated once and defended against the formats ACTUALLY ON DISK
# (1,217 kv-shaped sidecars censused 2026-09-10; 9,061 lines classified):
#
#   A `key=` TOKEN is an identifier immediately followed by `=`, at line start or after
#   whitespace:  (?:(?<=\s)|^)([A-Za-z_][A-Za-z0-9_]*)=
#
#   (A) A line is a MULTI-PAIR record line if and only if it carries TWO OR MORE such
#       tokens AND THE FIRST ONE STARTS AT COLUMN 0 of the stripped line.  Each value
#       then runs from after its `=` to the START OF THE NEXT TOKEN -- NOT to the next
#       whitespace.  Whitespace INSIDE a value is therefore preserved.
#   (B) EVERY OTHER LINE keeps the legacy `partition("=")` parse, byte for byte.
#
# WHY THE COLUMN-0 ANCHOR, which is the whole safety of this change.  Without it, a
# single-pair line whose VALUE happens to contain `key=` substrings would be shredded and
# its real key LOST.  Those lines exist on disk and are machine-read:
#     caps_core_min = L1=300 L2=600 L3=1500  (PER LEVEL, not a shared drawdown ...)
#         -- verification/runs/ansys_verification/VMFL017/R2/LAUNCH_RECORD.txt
#     status_smoke = smoke_rc=0 end=2026-08-26T17:41:33Z note=build_gpu_solver.sh-exit-0
#         -- verification/runs/ansys_verification/VMFLGPU001/LAUNCH_RECORD.txt
#     level L1 : rc=0 wall_s=86 core_min=1.4333 cap=2 timeout_s=120 last_time=60000
#         -- verification/runs/ansys_verification/VMFL007-R3/LAUNCH_RECORD.txt
#     solver+mesh wall_s=2055 ranks=1 core_min=34 cap_core_min=60
#         -- verification/runs/navier_class/SUP_BOOSTER/graded_e2/COST.txt
# In all four the first token is NOT at column 0, so rule (B) applies and their parse is
# unchanged.  The last one is therefore NOT repaired either: `solver+mesh wall_s` stays a
# compound key.  Stated plainly rather than quietly widened -- COST.txt is not read by
# this watcher, and widening the rule to reach it is what would have eaten the other
# three.
#
# WHAT THE ANCHOR PRESERVES.  Values that legitimately contain spaces are the format's
# normal case, not an edge case, and they survive because a single-token line never takes
# branch (A):
#     cost_basis=owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); ...
#     note=rc captured INSIDE the run, not around a setsid line
#     cap_core_min=4000 (running total)
#     levels=L1:24:20:32:80 L2:48:40:64:160 L3:96:80:128:320
# 96 such lines were found on disk; the parse of every one is unchanged.  And a value
# that spans two tokens on a MULTI-PAIR line keeps its internal spaces too, because the
# value ends at the next token and not at the next space.
#
# MEASURED BLAST RADIUS.  Of 9,061 lines in 1,217 files: 2,820 carry no `=` and are
# ignored by both readers; 6,241 take branch (B) and are BYTE-IDENTICAL to the pre-repair
# parse; 589 take branch (A) and change -- and on every one of those 589 the pre-repair
# parse was already WRONG for every key but the first, because it had merged them into one
# compound key.  RESIDUAL AMBIGUITY after the anchor: ONE line in the whole repository,
# and it is prose in docs/ansys_verification/gpu/LAUNCH_RECORD_VMFLGPU001_2026-08-26.md
# quoting sidecar text inside backticks -- no machine-read sidecar is ambiguous.
#
# NOT WIDENED, deliberately: `open(path)` keeps its default strict decoding.  Adding
# errors="replace" would have turned a corrupt sidecar from a loud exception into a quiet
# partial read, i.e. weakened a failure.  No refusal in this file is removed or relaxed by
# this repair.
# -------------------------------------------------------------------------------------
_KV_TOKEN = re.compile(r'(?:(?<=\s)|^)([A-Za-z_][A-Za-z0-9_]*)=')


def read_kv(path):
    """Parse a `key=value` sidecar. ONE NAMED FILE, passed in by the caller.

    Handles BOTH on-disk shapes: one pair per line (SUBOFF `STATUS.R1_<lvl>`, T5-style
    `STATUS.<case>`) and all pairs on one line (SUP_BOOSTER `graded_e2/<lvl>/STATUS`).
    The rule and its defence are in the block comment above this function.
    """
    out = {}
    if not os.path.isfile(path):
        return out
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if "=" in line:
                toks = list(_KV_TOKEN.finditer(line))
                if len(toks) >= 2 and toks[0].start() == 0:
                    # (A) MULTI-PAIR LINE.  Value ends at the NEXT token, never at the
                    # next space, so a spaced value between two pairs survives.
                    for i, m in enumerate(toks):
                        end = toks[i + 1].start() if i + 1 < len(toks) else len(line)
                        out[m.group(1)] = line[m.end():end].strip()
                else:
                    # (B) LEGACY PATH -- byte-identical to the pre-repair reader.
                    k, _, v = line.partition("=")
                    out[k.strip()] = v.strip()
    return out


def _read_kv_prerepair_blinded(path):
    """THE PRE-REPAIR READER, VERBATIM.  Used ONLY by the negative arm of the cost
    planted control, which requires it to FAIL to see a planted wall_s.  It is the
    committed defect kept executable so the control can be shown able to say `false`.
    """
    out = {}
    if not os.path.isfile(path):
        return out
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if "=" in line:
                k, _, v = line.partition("=")
                out[k.strip()] = v.strip()
    return out


def _read_kv_constant_zero_blinded(path):
    """A reader hard-wired to the answer that was committed: wall_s 0, rc 0.  The second
    negative arm.  A control that cannot catch THIS is not a control, because this is
    exactly the shape of the row that had to be corrected.
    """
    if not os.path.isfile(path):
        return {}
    return {"wall_s": "0", "core_min": "0", "rc_solve": "0", "rc": "0", "ranks": "1"}


def named_file_contains(path: str, needle: str) -> bool:
    """Rule (2): completion read from ONE NAMED file. No glob, ever."""
    if not os.path.isfile(path):
        return False
    with open(path, errors="replace") as fh:
        return needle in fh.read()


# =====================================================================================
# THE TWO RUNS.
# =====================================================================================
RUNS = {
    "suboff": {
        "label": "SUBOFF-R1-TRIPLE",
        "team": "cfd",
        "prereg_commit": "94d7afb7",
        "grader": REPO + "/cases/navier_class/SUBOFF/grade_suboff.py",
        "grader_pinned_blob": "9ab71b156d395d1e040851c524f0b81bb0e82ae1",
        "run_root": REPO + "/verification/runs/navier_class/SUBOFF",
        # RULE (2): ONE named artifact, and it is the launcher's own terminal line.
        "done_file": REPO + "/verification/runs/navier_class/SUBOFF/PROGRESS.R1_triple.txt",
        "done_needle": "TRIPLE FINISHED with launcher status",
        "levels": ["coarse", "medium", "fine"],
        "predicted_core_min": 80.38,
        "cap_core_min": 150.0,
        "grades_itself": False,          # launched WITHOUT --grade: WE must grade it
        "watch_pid_of": REPO + "/cases/navier_class/SUBOFF/run_suboff_r1_triple.sh",
    },
    "e2": {
        "label": "SUP_BOOSTER-E2",
        "team": "cfd",
        "prereg_commit": "34797ce9",
        "grader": REPO + "/verification/runs/navier_class/SUP_BOOSTER/grade_sup_booster_e2.py",
        "grader_pinned_blob": "d18f0867ea7d1fd6f86347c00ca1a5b8e3ddb663",
        "run_root": REPO + "/verification/runs/navier_class/SUP_BOOSTER/graded_e2",
        "done_file": REPO + "/verification/runs/navier_class/SUP_BOOSTER/graded_e2/LAUNCHER_DONE",
        "done_needle": "done ",
        "levels": ["coarse", "medium", "fine"],
        "predicted_core_min": 31.0,
        "cap_core_min": 60.0,
        "grades_itself": True,           # autograde_sup_booster_e2.sh fires from the launcher
        "watch_pid_of": REPO + "/verification/runs/navier_class/SUP_BOOSTER/run_graded_triple_e2.sh",
    },
}


# -------------------------------------------------------------------------------------
# COST -- read from the runs' OWN sidecars, never from memory (ledger append rule 2).
# -------------------------------------------------------------------------------------
def collect_cost(key, cfg):
    """Per-level wall_s / ranks / rc, from ONE NAMED sidecar per level."""
    rows = []
    if key == "suboff":
        for lvl in cfg["levels"]:
            case = os.path.join(cfg["run_root"], "reg_" + lvl)
            st = read_kv(os.path.join(case, "STATUS.R1_" + lvl))
            if not st:
                rows.append({"level": lvl, "present": False})
                continue
            rows.append({
                "level": lvl, "present": True,
                # ADDED with the 2026-09-10 repair: whether the key was actually THERE.
                # `.get(k,"0")` cannot tell an absent key from a measured zero, and that
                # indistinguishability is what landed a false 0.00x ratio.  Nothing
                # existing reads these two fields; cost_channel_guard() does.
                "wall_s_key_present": "wall_s" in st,
                "rc_key_present": "rc" in st,
                "rc": st.get("rc", "absent"),
                "wall_s": float(st.get("wall_s", "0") or 0),
                "ranks": int(st.get("ranks", "1") or 1),
                "core_min": float(st.get("core_min", "0") or 0),
                "source": os.path.join(case, "STATUS.R1_" + lvl),
            })
    else:
        for lvl in cfg["levels"]:
            d = os.path.join(cfg["run_root"], lvl)
            st = read_kv(os.path.join(d, "STATUS"))
            if not st:
                rows.append({"level": lvl, "present": False})
                continue
            wall = float(st.get("wall_s", "0") or 0)
            rows.append({
                "level": lvl, "present": True,
                "wall_s_key_present": "wall_s" in st,
                "rc_key_present": "rc_solve" in st,
                "rc": st.get("rc_solve", "absent"),
                "wall_s": wall, "ranks": 1,
                "core_min": wall / 60.0,
                "source": os.path.join(d, "STATUS"),
            })
    return rows


def summarise_cost(rows):
    """gross / cleaned / waste, with waste NAMED SEPARATELY (charter section 6).

    cleaned = gross minus every level the 3600-s stall rule matches.
    waste    = core-minutes spent on levels that returned non-zero, i.e. spend that
               bought no gradeable answer.  It is reported beside the ratio and is
               NEVER folded into either column or into the ratio's explanation.
    """
    present = [r for r in rows if r.get("present")]
    gross = sum(r["core_min"] for r in present)
    stalled = [r for r in present if r["wall_s"] > STALL_WALL_S]
    cleaned = gross - sum(r["core_min"] for r in stalled)
    waste = sum(r["core_min"] for r in present if str(r.get("rc")) != "0")
    return {
        "gross_core_min": gross,
        "cleaned_core_min": cleaned,
        "stalled_levels": [r["level"] for r in stalled],
        "waste_core_min": waste,
        "waste_levels": [r["level"] for r in present if str(r.get("rc")) != "0"],
        "levels_present": [r["level"] for r in present],
        "levels_absent": [r["level"] for r in rows if not r.get("present")],
    }


# =====================================================================================
# STANDING RULE 3, ARMED ON THE COST CHANNEL.
#
# The physics channel has planted-zero controls (analyse_t3.py plants PLANT=1.234e-03
# into T and REFUSES if the reader cannot see it).  The COST channel had NONE, and that
# is precisely why a 34.23 core-min run could be committed as 0.00 core-min with nothing
# in the pipeline objecting: a zero from a reader never shown able to see a NON-zero is
# not evidence, and until this control existed nobody had shown this reader able to see
# one.
#
# WHAT THIS CONTROL DOES.  It plants a KNOWN NON-ZERO wall_s and a KNOWN rc into REAL
# on-disk sidecars -- the actual bytes of graded_e2/coarse/STATUS (all pairs on one line)
# and of SUBOFF/reg_coarse/STATUS.R1_coarse (one pair per line), not a synthetic string --
# writes them to a fixture tree, and reads them back THROUGH THE PRODUCTION PATH:
# collect_cost() then summarise_cost(), the same two functions whose output becomes the
# ledger row.  It does not re-implement the reader; if it did, it would be testing itself.
#
# IT HAS BOTH WORDS.  A control that can only say "passed" has not been shown to work:
#   POSITIVE arms  -- the repaired reader MUST see the plant, to the exact value.
#   NEGATIVE arms  -- a deliberately blinded reader MUST be CAUGHT (passed: false):
#                     (N1) the PRE-REPAIR reader, kept executable verbatim, and
#                     (N2) a reader hard-wired to wall_s=0 / rc=0, which is the exact
#                          shape of the answer that got committed, and
#                     (N3) a real sidecar with the wall_s key REMOVED, where the value
#                          the caller would report is the reader's `.get(...,"0")`
#                          DEFAULT rather than a measured zero.
#   FAIL-CLOSED arm -- if its fixture source is missing the control REFUSES.  It does
#                     not skip, does not warn, does not pass by default.  A control that
#                     goes quiet when its inputs vanish is the same failure one level up.
#
# IT REFUSES, IT DOES NOT WARN.  Failure is exit 2 from main() and, inside watch(), a
# recorded refusal that STOPS the calibration row from being written or landed.  A
# printed discrepancy labelled non-binding is worse than one never computed.
#
# NO GUARD HERE IS AN `assert`.  `python3 -O` deletes every assert statement, so a
# refusal written as one is a refusal an interpreter flag switches off.
# no_bare_assert_proof() PARSES THIS FILE'S OWN AST and refuses if a single ast.Assert
# node exists anywhere in it -- an AST parse, not a grep, because a grep cannot tell an
# `assert` statement from the word "assert" in a comment or a string, in either direction.
# =====================================================================================

# The plant.  4321 is chosen to be non-zero, exact in float, and equal to NO wall_s on
# disk (real values are 243/290/501/584/900/1107/1174/1180/2513/6707), so a fixture read
# that returns a real file's value instead of the plant is caught rather than confused.
COST_PLANT_WALL_S = 4321
COST_PLANT_CORE_MIN = 72.017          # the SUBOFF family carries its own core_min key
COST_PLANT_RC_OK = "0"
COST_PLANT_RC_NONZERO = "137"

_COST_PLANT_FAMILIES = {
    # family -> real source sidecar whose BYTES are the fixture template
    "e2_oneline": {
        "source": REPO + "/verification/runs/navier_class/SUP_BOOSTER/graded_e2/coarse/STATUS",
        "collect_key": "e2",
        "rc_key": "rc_solve",
        "shape": "all pairs on ONE line (the shape that produced the false zero)",
    },
    "suboff_multiline": {
        "source": REPO + "/verification/runs/navier_class/SUBOFF/reg_coarse/STATUS.R1_coarse",
        "collect_key": "suboff",
        "rc_key": "rc",
        "shape": "one pair per line, 14 pairs, incl. a filesystem-path value",
    },
}


def _plant_kv_token(text, key, value):
    """Rewrite `key=<value>` IN THE FILE'S OWN SHAPE.  Returns (text, n_replaced)."""
    pat = re.compile(r'((?:(?<=\s)|^)%s=)\S*' % re.escape(key), re.M)
    return pat.subn(lambda m: m.group(1) + str(value), text)


def _strip_kv_token(text, key):
    """Delete `key=<value>` entirely -- the N3 arm's blinding, done to a REAL sidecar."""
    pat = re.compile(r'(?:(?<=\s)|^)%s=\S*[ \t]?' % re.escape(key), re.M)
    return pat.subn("", text)


def _build_cost_fixture(family, dest_root, wall_s, rc, drop_wall_key=False,
                        source_override=None):
    """Write the fixture from a REAL sidecar's bytes.  FAILS CLOSED: returns a refusal
    string instead of a root if the real source is missing, or if a key the plant needs
    is not in it.  Never fabricates a template.
    """
    fam = _COST_PLANT_FAMILIES[family]
    src = source_override if source_override is not None else fam["source"]
    if not os.path.isfile(src):
        return None, ("FIXTURE MISSING: %s does not exist. The cost planted control "
                      "REFUSES rather than skipping -- a control that goes quiet when "
                      "its input vanishes is the failure it exists to catch." % src)
    try:
        with open(src) as fh:
            template = fh.read()
    except OSError as exc:
        return None, "FIXTURE UNREADABLE: %s (%s)" % (src, exc)

    for lvl in ("coarse", "medium", "fine"):
        text = template
        n_wall = n_rc = 1
        if drop_wall_key:
            text, n_wall = _strip_kv_token(text, "wall_s")
        else:
            text, n_wall = _plant_kv_token(text, "wall_s", wall_s)
        text, n_rc = _plant_kv_token(text, fam["rc_key"], rc)
        if "core_min" in template:
            text, _ = _plant_kv_token(text, "core_min", "%.3f" % COST_PLANT_CORE_MIN)
        text, _ = _plant_kv_token(text, "level", lvl)
        text, _ = _plant_kv_token(text, "case", lvl)
        if n_wall < 1 or n_rc < 1:
            return None, ("FIXTURE REFUSAL: the real template %s carries no %s= or no %s= "
                          "token, so the plant could not be placed. Not worked around."
                          % (src, "wall_s", fam["rc_key"]))
        if family == "e2_oneline":
            d = os.path.join(dest_root, lvl)
            name = "STATUS"
        else:
            d = os.path.join(dest_root, "reg_" + lvl)
            name = "STATUS.R1_" + lvl
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, name), "w") as fh:
            fh.write(text)
    return dest_root, None


def cost_channel_guard(rows):
    """Refusals for the COST channel, in the caller's own terms.

    A 0.0 that came from an ABSENT key is the reader's `.get(key,"0")` DEFAULT, not a
    measured zero, and the two must never be reported as the same thing -- that
    indistinguishability is what let the false 0.00x ratio land.  Returns a list of
    refusal strings; empty means the channel may be reported.
    """
    refusals = []
    for r in rows:
        if not r.get("present"):
            continue
        if not r.get("wall_s_key_present"):
            refusals.append(
                "%s: sidecar %s carries NO wall_s key, so the %.3f core-min reported for "
                "this level is the reader's DEFAULT and not a measured value"
                % (r["level"], r["source"], r.get("core_min", 0.0)))
        if not r.get("rc_key_present"):
            refusals.append(
                "%s: sidecar %s carries NO rc key, so %r is a parse outcome and not a "
                "process status -- it cannot be used to sort waste"
                % (r["level"], r["source"], r.get("rc")))
    return refusals


def _read_plant_back(family, fixture_root, expect_wall, expect_rc, expect_core_min):
    """Read the fixture back through collect_cost()+summarise_cost() -- THE PRODUCTION
    PATH -- and return (ok, findings).  Nothing here re-implements the reader.
    """
    fam = _COST_PLANT_FAMILIES[family]
    cfg = {"run_root": fixture_root, "levels": ["coarse", "medium", "fine"]}
    rows = collect_cost(fam["collect_key"], cfg)
    cost = summarise_cost(rows)
    findings = []
    ok = True

    present = [r for r in rows if r.get("present")]
    if len(present) != 3:
        ok = False
        findings.append("only %d of 3 planted levels were read at all" % len(present))
    for r in present:
        if abs(r.get("wall_s", 0.0) - float(expect_wall)) > 1e-9:
            ok = False
            findings.append("%s: wall_s read %r, plant was %s -- THE READER CANNOT SEE "
                            "THE PLANT" % (r["level"], r.get("wall_s"), expect_wall))
        if str(r.get("rc")) != str(expect_rc):
            ok = False
            findings.append("%s: rc read %r, plant was %r"
                            % (r["level"], r.get("rc"), expect_rc))
        if abs(r.get("core_min", 0.0) - expect_core_min) > 1e-6:
            ok = False
            findings.append("%s: core_min read %r, plant implies %.6f"
                            % (r["level"], r.get("core_min"), expect_core_min))
    if abs(cost["gross_core_min"] - 3.0 * expect_core_min) > 1e-6:
        ok = False
        findings.append("gross read %.6f core-min, plant implies %.6f"
                        % (cost["gross_core_min"], 3.0 * expect_core_min))
    # The waste channel is part of the same defect: `rc` reading "absent" mis-sorted
    # every level into waste_levels while waste_core_min stayed 0.00.
    if str(expect_rc) == "0":
        if cost["waste_levels"]:
            ok = False
            findings.append("rc=0 was planted at every level yet %s were sorted into "
                            "waste_levels" % ", ".join(cost["waste_levels"]))
        if cost["waste_core_min"] != 0.0:
            ok = False
            findings.append("rc=0 planted yet waste_core_min is %.6f"
                            % cost["waste_core_min"])
    else:
        if sorted(cost["waste_levels"]) != ["coarse", "fine", "medium"]:
            ok = False
            findings.append("rc=%s planted at every level yet waste_levels is %s"
                            % (expect_rc, cost["waste_levels"]))
        if abs(cost["waste_core_min"] - cost["gross_core_min"]) > 1e-6:
            ok = False
            findings.append("rc=%s planted at every level yet waste %.6f != gross %.6f"
                            % (expect_rc, cost["waste_core_min"], cost["gross_core_min"]))
    guard = cost_channel_guard(rows)
    if guard:
        ok = False
        findings.append("cost_channel_guard REFUSED: " + "; ".join(guard))
    return ok, findings, cost


def _with_reader(reader, fn):
    """Run fn() with the module-level read_kv temporarily replaced.  collect_cost()
    resolves read_kv as a module global, so this blinds THE PRODUCTION PATH itself and
    not a copy of it.  Restored in a finally, so a failing arm cannot leave the watcher
    holding a blinded reader.
    """
    g = globals()
    saved = g["read_kv"]
    g["read_kv"] = reader
    try:
        return fn()
    finally:
        g["read_kv"] = saved


def no_bare_assert_proof(path=None):
    """PARSE this file's AST and refuse if ANY `assert` statement exists in it.

    Not a grep: a grep cannot distinguish an `assert` statement from the word assert in
    a comment or a docstring, and gets it wrong in both directions.  ast.Assert nodes are
    the statements `python3 -O` deletes, and they are what is counted here.
    """
    src_path = path or os.path.abspath(__file__)
    try:
        with open(src_path) as fh:
            src = fh.read()
    except OSError as exc:
        return False, "cannot read own source %s (%s)" % (src_path, exc)
    try:
        tree = ast.parse(src, filename=src_path)
    except SyntaxError as exc:
        return False, "own source does not parse: %s" % exc
    bad = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    if bad:
        return False, ("%d bare assert statement(s) at line(s) %s -- these VANISH under "
                       "python3 -O" % (len(bad), ", ".join(str(b) for b in bad)))
    return True, "0 ast.Assert nodes in %d AST nodes" % sum(1 for _ in ast.walk(tree))


def cost_plant_control(scratch, verbose=True, blind_production_reader=False):
    """The rule-3 planted control for the COST channel.  Returns a dict with `passed`.

    `blind_production_reader` installs the PRE-REPAIR reader for the positive arms, which
    must make the control REFUSE.  It exists so the refusal can be driven under both
    `python3` and `python3 -O` and shown to fire in both -- a guard never driven into its
    refusal is a guard nobody has seen work.
    """
    root = os.path.join(scratch, "cost_plant")
    os.makedirs(root, exist_ok=True)
    arms = []

    def note(name, kind, passed, detail):
        arms.append({"arm": name, "kind": kind, "passed": passed, "detail": detail})
        if verbose:
            print("  %-34s %-9s %-8s %s" % (name, kind, "OK" if passed else "FAILED",
                                            detail))

    ok_ast, ast_detail = no_bare_assert_proof()
    note("A0 no-bare-assert (AST parse)", "structure", ok_ast, ast_detail)

    # ---- FAIL-CLOSED ARM: the fixture source is gone. --------------------------------
    bogus = os.path.join(root, "no_such_source_STATUS")
    if os.path.exists(bogus):
        os.remove(bogus)
    _, refusal = _build_cost_fixture("e2_oneline", os.path.join(root, "failclosed"),
                                     COST_PLANT_WALL_S, COST_PLANT_RC_OK,
                                     source_override=bogus)
    note("F1 fixture-missing fails CLOSED", "failclosed", refusal is not None,
         (refusal or "NO REFUSAL -- the control would have skipped")[:120])

    # ---- POSITIVE ARMS ----------------------------------------------------------------
    reader = _read_kv_prerepair_blinded if blind_production_reader else read_kv
    positives = [
        ("P1 one-line fmt, rc=0", "e2_oneline", COST_PLANT_RC_OK,
         COST_PLANT_WALL_S / 60.0),
        ("P2 one-line fmt, rc=137", "e2_oneline", COST_PLANT_RC_NONZERO,
         COST_PLANT_WALL_S / 60.0),
        ("P3 multi-line fmt, rc=0", "suboff_multiline", COST_PLANT_RC_OK,
         COST_PLANT_CORE_MIN),
    ]
    for name, family, rc, expect_cm in positives:
        dest = os.path.join(root, name.split()[0])
        got, refusal = _build_cost_fixture(family, dest, COST_PLANT_WALL_S, rc)
        if refusal:
            note(name, "positive", False, refusal[:120])
            continue
        ok, findings, cost = _with_reader(
            reader, lambda: _read_plant_back(family, got, COST_PLANT_WALL_S, rc,
                                             expect_cm))
        note(name, "positive", ok,
             ("saw wall_s=%d rc=%s at 3 levels, gross %.3f core-min (%s)"
              % (COST_PLANT_WALL_S, rc, cost["gross_core_min"],
                 _COST_PLANT_FAMILIES[family]["shape"]))
             if ok else "; ".join(findings)[:200])

    # ---- NEGATIVE ARMS: a blinded reader MUST be caught. ------------------------------
    dest = os.path.join(root, "N")
    got, refusal = _build_cost_fixture("e2_oneline", dest, COST_PLANT_WALL_S,
                                       COST_PLANT_RC_OK)
    if refusal:
        note("N1/N2 negative arms", "negative", False, refusal[:120])
    else:
        for nname, blind in (("N1 pre-repair reader blinded", _read_kv_prerepair_blinded),
                             ("N2 reader hard-wired to zero", _read_kv_constant_zero_blinded)):
            ok, findings, _ = _with_reader(
                blind, lambda: _read_plant_back("e2_oneline", got, COST_PLANT_WALL_S,
                                                COST_PLANT_RC_OK,
                                                COST_PLANT_WALL_S / 60.0))
            note(nname, "negative", (not ok),
                 ("CAUGHT: " + "; ".join(findings)[:150]) if not ok
                 else "NOT CAUGHT -- the control cannot say `false` and is worthless")

    # N3: a REAL sidecar with the wall_s key removed.  The repaired reader parses it
    # fine; the value the caller would report is a DEFAULT, and the guard must refuse.
    dest3 = os.path.join(root, "N3")
    got3, refusal = _build_cost_fixture("e2_oneline", dest3, COST_PLANT_WALL_S,
                                        COST_PLANT_RC_OK, drop_wall_key=True)
    if refusal:
        note("N3 wall_s key removed", "negative", False, refusal[:120])
    else:
        cfg = {"run_root": got3, "levels": ["coarse", "medium", "fine"]}
        rows3 = collect_cost("e2", cfg)
        g3 = cost_channel_guard(rows3)
        note("N3 wall_s key removed", "negative", bool(g3),
             ("CAUGHT: " + g3[0][:150]) if g3
             else "NOT CAUGHT -- an absent key was reported as a measured 0.0")

    passed = all(a["passed"] for a in arms)
    result = {
        "control": "rule-3 planted control, COST channel",
        "plant_wall_s": COST_PLANT_WALL_S,
        "plant_rc_ok": COST_PLANT_RC_OK,
        "plant_rc_nonzero": COST_PLANT_RC_NONZERO,
        "fixture_sources": {k: v["source"] for k, v in _COST_PLANT_FAMILIES.items()},
        "read_back_through": "collect_cost() + summarise_cost() -- the production path",
        "production_reader_blinded": blind_production_reader,
        "arms": arms,
        "passed": passed,
        "utc": utc(),
    }
    if verbose:
        if passed:
            print("COST PLANTED CONTROL PASSED: the reader was shown able to see a "
                  "planted wall_s=%d and rc, in BOTH real on-disk sidecar formats, and "
                  "three blinded readers were CAUGHT." % COST_PLANT_WALL_S)
        else:
            print("REFUSED (exit 2): the cost channel is NOT trusted. Failing arms: %s"
                  % ", ".join(a["arm"] for a in arms if not a["passed"]),
                  file=sys.stderr)
    return result


def usd(core_min):
    return core_min / 60.0 * RATE_USD_PER_CORE_H


# -------------------------------------------------------------------------------------
# THE ROW.
# -------------------------------------------------------------------------------------
def build_row(cfg, cost, verdict_text, refs):
    pred = cfg["predicted_core_min"]
    ratio = (cost["cleaned_core_min"] / pred) if pred > 0 else 0.0
    if cost["stalled_levels"]:
        cleaned_note = ("%.2f core-min = $%.4f derived (gross minus the 3600-s stall "
                        "rule matches: %s)" % (cost["cleaned_core_min"],
                                               usd(cost["cleaned_core_min"]),
                                               ", ".join(cost["stalled_levels"])))
    else:
        cleaned_note = ("%.2f core-min = $%.4f derived (= gross; no level exceeds the "
                        "3600-s stall rule)" % (cost["cleaned_core_min"],
                                                usd(cost["cleaned_core_min"])))

    if cost["waste_core_min"] > 0:
        waste_txt = ("**waste named separately: %.2f core-min** on level(s) %s, which "
                     "returned non-zero and bought no gradeable answer -- NOT absorbed "
                     "into the ratio" % (cost["waste_core_min"],
                                         ", ".join(cost["waste_levels"]) or "none"))
    else:
        waste_txt = ("**waste named separately: 0.00 core-min** -- no level was sorted "
                     "into waste. This row is only reachable with every level's rc key "
                     "actually READ and equal to 0: cost_channel_guard() REFUSES the cost "
                     "channel when an rc key is absent, so `absent` can no longer be "
                     "reported as rc=0 (the 2026-09-10 false-zero repair)")

    if ratio > 1.0:
        direction = ("over the estimate; the per-level wall timeouts, not the estimate, "
                     "bounded the spend")
    else:
        direction = "under the estimate"

    gap = ("%s. %s. Levels absent from the record: %s. Attribution: solver iteration "
           "rate under box contention (multiple OpenFOAM and DAFoam solvers live at "
           "launch) against a single-tenant per-iteration basis in the pre-registration"
           % (direction, waste_txt, ", ".join(cost["levels_absent"]) or "none"))

    cells = [
        "{{ALLOCATE_ID}}",
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
        cfg["team"],
        "**%s** (graded triple; prereg frozen at `%s`; %s)"
        % (cfg["label"], cfg["prereg_commit"], verdict_text),
        "%.2f core-min registered (cap %.0f core-min)" % (cfg["predicted_core_min"],
                                                          cfg["cap_core_min"]),
        "%.2f core-min = $%.4f derived (solver wall x ranks / 60, from the run's own "
        "per-level sidecars)" % (cost["gross_core_min"], usd(cost["gross_core_min"])),
        cleaned_note,
        "%.2fx" % ratio,
        gap,
        refs,
    ]
    return "| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |\n"


# -------------------------------------------------------------------------------------
# TIER B: land the row.  Canonical tool + rule-10 private index, in ONE invocation.
# -------------------------------------------------------------------------------------
LAND_SH = r'''
set -u
cd /home/ubuntu/Certonomous || exit 90
ROWS="$1"; IDX="$2"; MSG="$3"
export GIT_INDEX_FILE="$IDX"; rm -f "$GIT_INDEX_FILE"
H=$(git rev-parse HEAD) || exit 91
case "$H" in *[!0-9a-f]*|"") echo "BAD HEAD sha: $H" >&2; exit 92;; esac
# The tool rebuilds the ledger as HEAD's blob + our row and mints a collision-free id.
python3 scripts/append_record.py --path docs/COST_CALIBRATION.md --rows "$ROWS" \
        --rev "$H" --allocate-id || exit 93
git read-tree "$H" || exit 94
git update-index --add -- docs/COST_CALIBRATION.md || exit 95
T=$(git write-tree) || exit 96
case "$T" in *[!0-9a-f]*|"") echo "BAD tree sha: $T" >&2; exit 97;; esac
if [ "$T" = "$(git rev-parse ${H}^{tree})" ]; then
  echo "REFUSE: write-tree equals HEAD's tree -- the append changed nothing" >&2; exit 98
fi
N=$(git diff-tree --no-commit-id --name-only -r "$H" "$T" | wc -l)
if [ "$N" != "1" ]; then
  echo "REFUSE: $N paths in the tree, expected exactly 1" >&2
  git diff-tree --no-commit-id --name-only -r "$H" "$T" >&2; exit 99
fi
P=$(git diff-tree --no-commit-id --name-only -r "$H" "$T")
if [ "$P" != "docs/COST_CALIBRATION.md" ]; then
  echo "REFUSE: foreign path in tree: $P" >&2; exit 100
fi
C=$(git commit-tree "$T" -p "$H" -F "$MSG") || exit 101
case "$C" in *[!0-9a-f]*|"") echo "BAD commit sha: $C" >&2; exit 102;; esac
if [ ${#C} -ne 40 ]; then echo "BAD commit sha length: $C" >&2; exit 103; fi
git update-ref refs/heads/main "$C" "$H" || exit 104     # CAS: parent must still be HEAD
NOW=$(git rev-parse HEAD)
if [ "$NOW" != "$C" ]; then echo "REFUSE: HEAD did not move to $C (is $NOW)" >&2; exit 105; fi
V=$(git diff HEAD~1 HEAD --name-only)
if [ "$V" != "docs/COST_CALIBRATION.md" ]; then
  echo "REFUSE post-commit verify: commit carries [$V]" >&2; exit 106
fi
echo "LANDED $C"
'''


def land_row(row_text, cfg, key, scratch, logf):
    """Attempt Tier B.  Every failure is RECORDED and returns False; Tier A stands."""
    rows_file = os.path.join(scratch, "row_%s.md" % key)
    msg_file = os.path.join(scratch, "msg_%s.txt" % key)
    sh_file = os.path.join(scratch, "land_%s.sh" % key)
    for attempt in range(1, 6):
        with open(rows_file, "w") as fh:
            fh.write(row_text)
        with open(msg_file, "w") as fh:
            fh.write("cfd COST_CALIBRATION: %s rule-12 estimate-vs-actual row\n\n"
                     "Written by the detached grade-and-calibrate watcher\n"
                     "cases/navier_class/watch_grade_calibrate.py at run completion,\n"
                     "not owed to a future agent (CLAUDE.md rule 12). Predicted %.2f\n"
                     "core-min; actuals read from the run's own per-level sidecars.\n"
                     % (cfg["label"], cfg["predicted_core_min"]))
        with open(sh_file, "w") as fh:
            fh.write(LAND_SH)
        idx = os.path.join(scratch, "idx_%s_%d" % (key, attempt))
        env = dict(os.environ)
        env.pop("GIT_INDEX_FILE", None)
        p = subprocess.run(["bash", sh_file, rows_file, idx, msg_file],
                           cwd=REPO, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.stdout.decode(errors="replace")
        logf.write("[%s] land attempt %d rc=%d\n%s\n" % (utc(), attempt, p.returncode, out))
        logf.flush()
        if p.returncode == 0:
            return True, out.strip().splitlines()[-1] if out.strip() else "LANDED"
        # 104 = CAS lost to a peer commit: re-derive against the new HEAD and retry.
        if p.returncode in (93, 104, 105, 99, 100):
            time.sleep(7 + attempt * 3)
            continue
        return False, "rc=%d (not retried): %s" % (p.returncode, out.strip()[-400:])
    return False, "exhausted 5 attempts under concurrency"


# -------------------------------------------------------------------------------------
# THE WATCH.
# -------------------------------------------------------------------------------------
def watch(key, deadline_s, poll_s, scratch):
    cfg = RUNS[key]
    root = cfg["run_root"]
    verdict_sidecar = os.path.join(root, "WATCHER_VERDICT.%s.json" % key)
    logpath = os.path.join(root, "watcher.%s.log" % key)
    rowfile = os.path.join(root, "CALIBRATION_ROW.%s.pending.md" % key)

    logf = open(logpath, "a", buffering=1)

    def log(msg):
        logf.write("[%s] %s\n" % (utc(), msg))
        logf.flush()

    log("=" * 78)
    log("watcher start pid=%d ppid=%d run=%s" % (os.getpid(), os.getppid(), cfg["label"]))
    log("ppid observed from this process: %d (1 == reparented to init == survives fleet death)"
        % os.getppid())

    # RULE (6): IDEMPOTENT.  An existing verdict record is never overwritten.
    if os.path.exists(verdict_sidecar):
        log("IDEMPOTENT STOP: %s already exists. Not re-grading, not overwriting." % verdict_sidecar)
        return 0

    pinned = cfg["grader_pinned_blob"]
    hash_timeline = []
    drift_seen = None
    t0 = time.time()
    done = False

    while time.time() - t0 < deadline_s:
        # RULE (3): the freeze is re-checked EVERY poll, so drift before an autograde is
        # caught rather than discovered after it.
        if os.path.isfile(cfg["grader"]):
            h = git_blob_sha1(cfg["grader"])
            if not hash_timeline or hash_timeline[-1][1] != h:
                hash_timeline.append((utc(), h))
                log("grader blob %s (pinned %s) %s" %
                    (h, pinned, "MATCH" if h == pinned else "*** DRIFT ***"))
            if h != pinned and drift_seen is None:
                drift_seen = (utc(), h)
                log("FREEZE DRIFT DETECTED -- standing rule 2. This watcher will REFUSE "
                    "to grade and will quarantine any verdict produced from here on.")
        else:
            if drift_seen is None:
                drift_seen = (utc(), "MISSING")
                log("FREEZE DRIFT: pinned grader MISSING at %s" % cfg["grader"])

        # RULE (2): ONE NAMED ARTIFACT.
        if named_file_contains(cfg["done_file"], cfg["done_needle"]):
            done = True
            log("completion seen in ONE NAMED artifact %s" % cfg["done_file"])
            break
        time.sleep(poll_s)

    if not done:
        log("DEADLINE REACHED after %.0f s with no completion marker in %s. "
            "Recording BLOCKED; nothing graded, nothing deleted."
            % (time.time() - t0, cfg["done_file"]))
        rec = {"run": cfg["label"], "state": "BLOCKED",
               "reason": "watcher deadline reached with no completion marker",
               "done_file": cfg["done_file"], "watcher_ppid": os.getppid(),
               "hash_timeline": hash_timeline, "utc": utc()}
        with open(verdict_sidecar, "w") as fh:
            json.dump(rec, fh, indent=2)
        return 3

    # ---- FREEZE GATE.  Refuse rather than grade.  Not a note; a refusal. ----------
    h_now = git_blob_sha1(cfg["grader"]) if os.path.isfile(cfg["grader"]) else "MISSING"
    if h_now != pinned or drift_seen is not None:
        log("REFUSING TO GRADE: grading path is not the frozen one. on-disk=%s pinned=%s "
            "first_drift=%s" % (h_now, pinned, drift_seen))
        rec = {"run": cfg["label"], "state": "NOT A RESULT",
               "reason": "frozen grading path drifted (CLAUDE.md rule 2); this watcher "
                         "refused to grade and graded nothing",
               "grader": cfg["grader"], "grader_on_disk_blob": h_now,
               "grader_pinned_blob": pinned, "first_drift": drift_seen,
               "hash_timeline": hash_timeline, "watcher_ppid": os.getppid(),
               "self_graded_by_launcher": cfg["grades_itself"], "utc": utc()}
        with open(verdict_sidecar, "w") as fh:
            json.dump(rec, fh, indent=2)
        return 2

    log("FREEZE OK: grader blob %s == pinned %s. Rule 2 discharged by this watcher." % (h_now, pinned))

    # ---- GRADE (SUBOFF) or VALIDATE THE LAUNCHER'S OWN GRADE (E2) -----------------
    grade_rc = None
    grade_note = ""
    if cfg["grades_itself"]:
        rc_auto = read_kv(os.path.join(root, "rc.autograde"))
        raw = ""
        p_rc = os.path.join(root, "rc.autograde")
        if os.path.isfile(p_rc):
            with open(p_rc) as fh:
                raw = fh.read().strip()
        verdict_json = os.path.join(root, "VERDICT.json")
        if os.path.isfile(verdict_json):
            grade_rc = int(raw) if raw.isdigit() else None
            grade_note = ("graded by the launcher's own detached autograder; this watcher "
                          "verified the frozen grading path across the whole run and did "
                          "not re-grade (rule 6, idempotent)")
            log("E2 verdict present at %s, autograde rc=%s. Not re-grading." % (verdict_json, raw))
        else:
            log("E2 LAUNCHER_DONE present but VERDICT.json ABSENT -- the autograder did "
                "not produce a verdict. Grading here with the frozen grader.")
            grade_rc = run_grader_capture_rc(
                [sys.executable, cfg["grader"],
                 "--coarse", os.path.join(root, "coarse"),
                 "--medium", os.path.join(root, "medium"),
                 "--fine", os.path.join(root, "fine"),
                 "--reference", REPO + "/verification/runs/navier_class/SUP_BOOSTER/"
                                       "tm_reference_M2p0_tc15.json",
                 "--report", verdict_json],
                os.path.join(root, "watcher_verdict_stdout.txt"),
                os.path.join(root, "rc.grade.watcher"))
            grade_note = "autograder produced no verdict; this watcher graded, rc captured inside"
    else:
        grade_rc = run_grader_capture_rc(
            [sys.executable, cfg["grader"],
             "--coarse", os.path.join(root, "reg_coarse"),
             "--medium", os.path.join(root, "reg_medium"),
             "--fine", os.path.join(root, "reg_fine"),
             "--reference", os.path.join(root, "suboff_reference_ReL1p2e7.json"),
             "--report", os.path.join(root, "VERDICT.R1_triple.json")],
            os.path.join(root, "watcher_verdict_stdout.txt"),
            os.path.join(root, "rc.grade.watcher"))
        grade_note = ("graded by this watcher because the launcher was started WITHOUT "
                      "--grade; rc captured inside this process")
        log("grade_suboff.py rc=%s (2 = the grader's own REFUSE, e.g. rule-4 incompleteness)"
            % grade_rc)

    # ---- COST, then TIER A, then TIER B ------------------------------------------
    rows = collect_cost(key, cfg)
    cost = summarise_cost(rows)
    log("cost gross=%.2f cleaned=%.2f waste=%.2f core-min (levels present: %s)"
        % (cost["gross_core_min"], cost["cleaned_core_min"], cost["waste_core_min"],
           ", ".join(cost["levels_present"]) or "none"))

    # ---- RULE 3, ARMED ON THE COST CHANNEL. ---------------------------------------
    # The reader that produced the figures above is shown able to see a PLANTED non-zero
    # wall_s and rc, in both real on-disk sidecar formats, BEFORE any cost row is written
    # or landed.  BOOKKEEPING NEVER VOIDS PHYSICS (Sanaa, universal rule 2026-08-26): a
    # refusal here suppresses the CALIBRATION ROW only.  The verdict sidecar is still
    # written, carrying the refusal, and the grade above is untouched.
    cost_plant = cost_plant_control(scratch, verbose=False)
    cost_guard = cost_channel_guard(rows)
    cost_trusted = bool(cost_plant["passed"]) and not cost_guard
    if not cost_trusted:
        log("COST CHANNEL REFUSED (standing rule 3): planted control passed=%s; guard=%s. "
            "NO calibration row will be written and none will be landed. The grade and the "
            "verdict record are unaffected -- bookkeeping never voids physics."
            % (cost_plant["passed"], cost_guard or "clean"))
        for a in cost_plant["arms"]:
            if not a["passed"]:
                log("  failing arm %s (%s): %s" % (a["arm"], a["kind"], a["detail"]))

    if grade_rc == 0:
        vtxt = "graded; verdict in the run's own VERDICT json"
    elif grade_rc == 2:
        vtxt = ("grader REFUSED (exit 2) -- a level is not rule-4 complete, so the triple "
                "is **NOT A RESULT** by incompleteness")
    elif grade_rc is None:
        vtxt = "verdict produced by the launcher's own autograder"
    else:
        vtxt = "grader exited %d -- a crash is a FINDING until the supervisor's check-3 triage" % grade_rc

    refs = ("`%s`; per-level sidecars `%s`; watcher log `%s`"
            % (verdict_sidecar.replace(REPO + "/", ""),
               ", ".join(r["source"].replace(REPO + "/", "") for r in rows if r.get("present"))
               or "none present",
               logpath.replace(REPO + "/", "")))
    row_text = build_row(cfg, cost, vtxt, refs)

    # TIER A -- written unless the COST PLANTED CONTROL REFUSED.  "Always" was the old
    # promise and it is exactly how a false zero reached the ledger: a row is worse than
    # no row when the reader behind it has not been shown able to see a non-zero.
    if not cost_trusted:
        rec = {
            "run": cfg["label"],
            "grade_rc": grade_rc,
            "grade_note": grade_note,
            "cost_channel": "NOT A RESULT",
            "cost_channel_reason": "standing rule 3: the cost planted control did not "
                                   "pass, or cost_channel_guard refused. No calibration "
                                   "row was written and none was landed.",
            "cost_plant_control": cost_plant,
            "cost_channel_guard": cost_guard,
            "cost_rows": rows,
            "cost_unreported": cost,
            "physics_unaffected": "the grade above stands; bookkeeping never voids "
                                  "physics (Sanaa, universal rule 2026-08-26)",
            "grader_pinned_blob": pinned,
            "grader_on_disk_blob": h_now,
            "hash_timeline": hash_timeline,
            "watcher_pid": os.getpid(),
            "watcher_ppid": os.getppid(),
            "utc": utc(),
        }
        with open(verdict_sidecar, "w") as fh:
            json.dump(rec, fh, indent=2)
        log("verdict sidecar written with the cost channel marked NOT A RESULT: %s"
            % verdict_sidecar)
        return 2

    with open(rowfile, "w") as fh:
        fh.write("<!-- Ready-to-append docs/COST_CALIBRATION.md row, written by\n"
                 "     cases/navier_class/watch_grade_calibrate.py at %s.\n"
                 "     The id cell is the tool's {{ALLOCATE_ID}} placeholder: land with\n"
                 "       python3 scripts/append_record.py --path docs/COST_CALIBRATION.md \\\n"
                 "              --rows <this file> --allocate-id\n"
                 "     then commit under the CLAUDE.md rule-10 private-index protocol. -->\n"
                 % utc())
        fh.write(row_text)
    log("TIER A written: %s" % rowfile)

    landed, land_msg = land_row(row_text, cfg, key, scratch, logf)
    log("TIER B %s: %s" % ("LANDED" if landed else "NOT LANDED", land_msg))

    rec = {
        "run": cfg["label"],
        "prereg_commit": cfg["prereg_commit"],
        "grader": cfg["grader"],
        "grader_pinned_blob": pinned,
        "grader_on_disk_blob": h_now,
        "freeze_check": "PASS -- discharged by this watcher, every poll",
        "hash_timeline": hash_timeline,
        "grade_rc": grade_rc,
        "grade_note": grade_note,
        "cost": cost,
        "cost_rows": rows,
        "cost_plant_control": cost_plant,
        "cost_channel_guard": cost_guard or "clean",
        "cost_basis": "core-minutes from the run's own per-level sidecars; dollars at "
                      "$0.0513/core-h are DERIVED, not measured (the box cannot read its "
                      "own billing, COMPUTE_BUDGET_CHARTER section 5)",
        "predicted_core_min": cfg["predicted_core_min"],
        "cap_core_min": cfg["cap_core_min"],
        "calibration_row_file": rowfile,
        "calibration_landed": landed,
        "calibration_land_message": land_msg,
        "watcher_pid": os.getpid(),
        "watcher_ppid": os.getppid(),
        "utc": utc(),
    }
    with open(verdict_sidecar, "w") as fh:
        json.dump(rec, fh, indent=2)
    log("verdict sidecar written: %s" % verdict_sidecar)
    log("watcher done.")
    return 0


# -------------------------------------------------------------------------------------
# THE PLANTED-FAILURE PROOF (rule (1)).
# -------------------------------------------------------------------------------------
def selftest_plant(dirpath):
    """Drive run_grader_capture_rc() -- THE PRODUCTION FUNCTION -- with a grader
    planted to exit non-zero, and REFUSE unless the sidecar records that rc.

    A guard never driven into its refusal is a guard nobody has seen work.  Both limbs
    run: a planted failure that must be recorded, and a planted success that must be
    recorded as 0, so a sidecar hard-wired to any constant fails one limb or the other.
    """
    os.makedirs(dirpath, exist_ok=True)
    failures = []
    for want in (7, 124, 2, 0):
        g = os.path.join(dirpath, "planted_grader_%d.py" % want)
        with open(g, "w") as fh:
            fh.write("import sys\nsys.stdout.write('planted grader, exiting %d\\n')\n"
                     "sys.exit(%d)\n" % (want, want))
        rc_path = os.path.join(dirpath, "rc.planted_%d" % want)
        out_path = os.path.join(dirpath, "out.planted_%d" % want)
        got = run_grader_capture_rc([sys.executable, g], out_path, rc_path)
        side = read_kv(rc_path)
        recorded = side.get("rc")
        ok = (got == want) and (recorded == str(want))
        print("  planted rc=%-4d -> returned %-4s sidecar rc=%-4s  %s"
              % (want, got, recorded, "OK" if ok else "FAILED"))
        if not ok:
            failures.append(want)
    if failures:
        print("REFUSED: rc capture did not record planted rc(s) %s. The watcher is NOT "
              "trusted." % failures, file=sys.stderr)
        return 1
    print("PLANTED-FAILURE PROOF PASSED: run_grader_capture_rc records a non-zero rc "
          "(7, 124, 2) and a zero rc (0) faithfully, INSIDE the watcher process.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", choices=sorted(RUNS))
    ap.add_argument("--deadline-s", type=float, default=36000.0)
    ap.add_argument("--poll-s", type=float, default=20.0)
    ap.add_argument("--scratch", default="/tmp/claude-1000/watcher")
    ap.add_argument("--selftest-plant")
    ap.add_argument("--selftest-cost-plant",
                    help="RULE 3 ON THE COST CHANNEL: plant a known non-zero wall_s and "
                         "rc into REAL on-disk sidecars, read them back through the "
                         "production path, and REFUSE (exit 2) if the reader cannot see "
                         "the plant or if a blinded reader is not caught.")
    ap.add_argument("--force-blind-cost-reader", action="store_true",
                    help="Install the PRE-REPAIR reader for the control's positive arms "
                         "so the refusal must fire. Only legal with "
                         "--selftest-cost-plant; it exists to drive the refusal under "
                         "both python3 and python3 -O.")
    args = ap.parse_args()
    if args.force_blind_cost_reader and not args.selftest_cost_plant:
        sys.stderr.write("REFUSED: --force-blind-cost-reader is only legal with "
                         "--selftest-cost-plant; it must never blind a real run.\n")
        return 2
    if args.selftest_cost_plant:
        res = cost_plant_control(args.selftest_cost_plant, verbose=True,
                                 blind_production_reader=args.force_blind_cost_reader)
        out = os.path.join(args.selftest_cost_plant, "COST_PLANT_CONTROL.json")
        os.makedirs(args.selftest_cost_plant, exist_ok=True)
        with open(out, "w") as fh:
            json.dump(res, fh, indent=2)
        print("control record: %s" % out)
        return 0 if res["passed"] else 2
    if args.selftest_plant:
        return selftest_plant(args.selftest_plant)
    if not args.run:
        ap.error("--run is required unless --selftest-plant")
    os.makedirs(args.scratch, exist_ok=True)
    return watch(args.run, args.deadline_s, args.poll_s, args.scratch)


if __name__ == "__main__":
    sys.exit(main())
