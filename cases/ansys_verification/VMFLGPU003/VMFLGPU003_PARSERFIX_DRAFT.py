#!/usr/bin/env python3
"""VMFLGPU003 -- PARSER FIX, DRAFT ONLY.  NOT APPLIED.  NOT COMMITTED.  NOT A GRADER.

=====================================================================
  DRAFT.  This file grades NOTHING and is on NO grading path.
  It does not import, modify, wrap or monkey-patch grade_vmflgpu003.py.
  grade_vmflgpu003.py is UNTOUCHED by this draft; its blob is 3242084665d86baeff50fc59ab2b650e53cbb995.
=====================================================================

WHAT IS DEFECTIVE IN THE FROZEN GRADER
--------------------------------------
grade_vmflgpu003.py parses every `key = value` artifact with

    KV_RE = re.compile(r"(\w+)\s*=\s*(.*)")      # ONE pair per line
    m = KV_RE.match(line.strip())
    if m: out[m.group(1)] = m.group(2).strip()   # non-match SILENTLY DROPPED

Two measured failure modes, both present in this case's real
`LAUNCH_RECORD.txt` on disk:

  (a) TAIL SWALLOWED.  `status_smoke = smoke_rc=0 end=<utc> note=<text>`
      parses as ONE pair; `smoke_rc`, `end` and `note` are lost.
  (b) LINE SILENTLY SKIPPED.  `solve rc = 0  arm = gpu  level = L1  wall_s = 25
      cap_fired = 0  utc = <utc>` does not match at all (the leading bare word
      `solve` defeats `.match`), so `rc`, `arm`, `level`, `wall_s`, `cap_fired`
      and `utc` are unreadable from that file and NOTHING SAYS SO.

BLAST RADIUS ON THIS CASE: MEASURED **ZERO** (see the real-file regression
checks in selftest()).  Every key the frozen grader actually READS sits on a
single-pair, matching line, so no landed cost or verdict figure moves.  The
defect is a BLINDNESS, not a corruption: it makes a reader unable to see data,
which is the shape CLAUDE.md rule 3 exists for.

THE FIX
-------
  * parse ALL pairs on a line; a value runs to the start of the next key;
  * `=>` is NOT a key boundary (ldd output), so `libmpi.so.40 => /usr/...`
    does not manufacture a key `40`;
  * a line carrying no parseable pair is NEVER silently skipped -- it is
    returned in `unparsed` and every call site must dispose of it explicitly;
  * an EXPLICIT REFUSAL (never a bare `assert`; `python3 -O` strips those,
    L-332) runs a PLANTED CONTROL at EVERY call site before the reader's
    output is believed -- L-221/L-222: a lesson is not applied until every
    call site asserts it.  There are THREE call sites in grade_vmflgpu003.py:
        1. strict_completion()  -> RUN_RC.<level>.<arm> / RUN_RC.txt   (reads `rc`)
        2. cost_record()        -> COST.txt                            (whole dict lands)
        3. freeze_record()      -> LAUNCH_RECORD.txt                   (reads 7 keys)
  * proven by a MUTATION CONTROL: `--selftest --mutate` reverts the parser to
    the frozen single-pair behaviour and the suite must go RED.

DISCLOSURE -- WHAT THE FIX CHANGES THAT THE FROZEN READER PRODUCED
-----------------------------------------------------------------
Nothing any verdict depends on.  Measured, per real file, in selftest():
  * every key READ by grade_vmflgpu003.py keeps a BYTE-IDENTICAL value;
  * new keys appear in the LAUNCH_RECORD dict (`smoke_rc`, `end`, `note`,
    `arm`, `level`, `wall_s`, `cap_fired`, `utc`, `rc`) -- none of them is read
    by grade_vmflgpu003.py, and the grader lands only four named LAUNCH_RECORD keys
    (prereg_sha_head, comparator_sha_head, head, launched_utc);
  * ONE existing key changes value: `status_smoke` goes from the whole
    compound string to "" (its own segment is empty, the tail becomes
    smoke_rc/end/note).  `status_smoke` is read by nothing and landed nowhere.
  * COST.txt and every RUN_RC file are unchanged in every key and every value:
    they are single-pair throughout.
"""

import os
import re
import sys

CASE = "VMFLGPU003"
FROZEN_GRADER = "grade_vmflgpu003.py"
FROZEN_BLOB = "3242084665d86baeff50fc59ab2b650e53cbb995"
RUN_ROOT_DEFAULT = "/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFLGPU003"

# The FROZEN grader's regex, reproduced VERBATIM.  Kept for two reasons: the
# mutation control drives it, and the real-file regression checks diff against
# it.  It is never used to read anything this draft believes.
KV_RE_FROZEN = re.compile(r"(\w+)\s*=\s*(.*)")


# ---------------------------------------------------------------------------
# primitives, in the frozen grader's own form
# ---------------------------------------------------------------------------
def refuse(code, msg):
    """Exit 2.  Never an assert: `python3 -O` would delete an assert (L-332)."""
    sys.stderr.write("REFUSE (%s %s): %s\n" % (CASE, code, msg))
    sys.exit(2)


def warn_infra(msg):
    print("  WARNING(INFRASTRUCTURE): %s" % msg)
    return None


# ---------------------------------------------------------------------------
# THE FIX
# ---------------------------------------------------------------------------
# A key boundary is `word =` NOT followed by `=` or `>`.  The lookbehind keeps
# `so.40 =>` from becoming a key, and the lookahead keeps `==` and `=>` out.
KV_KEY_RE = re.compile(r"(\w+)[ \t]*=[ \t]*(?![=>])")


def kv_pairs(line):
    """EVERY `key = value` pair on one line, in order.

    A value runs from just after its own `=` to the start of the NEXT key on
    the same line (or end of line).  Returns [] for a line with no pair --
    the caller must dispose of that explicitly, never silently."""
    s = line.rstrip("\r\n")
    hits = [m for m in KV_KEY_RE.finditer(s) if not _is_arrow(s, m)]
    out = []
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(s)
        out.append((m.group(1), s[m.end():end].strip()))
    return out


def _is_arrow(s, m):
    """True when this `=` is really the `=>` of ldd output."""
    j = m.end() - 1
    while j >= 0 and s[j] in " \t":
        j -= 1
    return False if j < 0 else s[j] == ">"


def read_kv(path):
    """Returns (kv, unparsed).

    `unparsed` carries (lineno, text) for every NON-BLANK line that yielded no
    pair.  It is NEVER dropped: each call site disposes of it explicitly.
    An unreadable file returns ({}, [(0, '<OSError>')]) -- callers default to
    the REFUSING value, exactly as the frozen grader does."""
    kv, unparsed = {}, []
    try:
        for n, line in enumerate(open(path, errors="replace"), 1):
            pairs = kv_pairs(line)
            if not pairs:
                if line.strip():
                    unparsed.append((n, line.strip()))
                continue
            for k, v in pairs:
                kv[k] = v
    except OSError as e:
        return {}, [(0, "<OSError: %s>" % e)]
    return kv, unparsed


# ---------------------------------------------------------------------------
# THE PLANTED CONTROL, RUN AT EVERY CALL SITE (CLAUDE.md rule 3; L-221/L-222)
# ---------------------------------------------------------------------------
# A reader that cannot be SHOWN to see a multi-pair line has not been shown to
# see anything.  This plant carries both measured failure shapes.  It is an
# EXPLICIT REFUSAL, not a bare `assert`, so `python3 -O` cannot delete it.
_PLANT_LINES = [
    "status_smoke = smoke_rc=0 end=2026-01-01T00:00:00Z note=planted-note",
    "solve rc = 0  arm = gpu  level = LP  wall_s = 4321  cap_fired = 1  utc = 2026-01-01T00:00:01Z",
    "ldd_simpleFoam_libmpi = \tlibmpi.so.40 => /usr/lib/libmpi.so.40 (0x00007f00);",
    "plain_key = plain_value",
]
_PLANT_EXPECT = {
    "smoke_rc": "0", "end": "2026-01-01T00:00:00Z", "note": "planted-note",
    "rc": "0", "arm": "gpu", "level": "LP", "wall_s": "4321",
    "cap_fired": "1", "utc": "2026-01-01T00:00:01Z",
    "plain_key": "plain_value",
}


def kv_selfproof(site):
    """Refuse unless the reader demonstrably sees BOTH failure shapes.

    Called at EVERY call site before that site's output is believed."""
    got = {}
    misses = []
    for line in _PLANT_LINES:
        pairs = kv_pairs(line)
        if not pairs:
            misses.append("a planted line yielded NO pair: %r" % line[:60])
        for k, v in pairs:
            got[k] = v
    for k, want in sorted(_PLANT_EXPECT.items()):
        if got.get(k) != want:
            misses.append("planted key %r read as %r, expected %r"
                          % (k, got.get(k), want))
    if "40" in got:
        misses.append("the ldd `=>` manufactured a bogus key '40'")
    if misses:
        refuse("KV-PROOF/%s" % site,
               "the key/value reader could not see its own planted control, so "
               "nothing it reads may be believed at this call site. %s"
               % ("; ".join(misses)))
    return True


# ---------------------------------------------------------------------------
# the three call sites, in the frozen grader's own shape
# ---------------------------------------------------------------------------
RC_REQUIRED = ("rc",)
FREEZE_PHYSICS_KEYS = ("prereg_sha_head", "prereg_sha_disk",
                       "comparator_sha_head", "comparator_sha_disk")
FREEZE_LANDED_KEYS = ("prereg_sha_head", "comparator_sha_head",
                      "head", "launched_utc")


def read_rc(rc_path):
    """CALL SITE 1 -- strict_completion().  PHYSICS-CRITICAL."""
    kv_selfproof("strict_completion")                      # <-- ASSERT, site 1
    kv, unparsed = read_kv(rc_path)
    if unparsed:
        warn_infra("%s: %d line(s) carried no key/value pair and were NOT "
                   "silently dropped: %s"
                   % (rc_path, len(unparsed),
                      "; ".join("L%d %r" % (n, t[:60]) for n, t in unparsed[:4])))
    raw = kv.get("rc", "1")            # FAIL-SAFE default: the refusing value
    return kv, raw, unparsed


def read_cost(cost_path):
    """CALL SITE 2 -- cost_record().  INFRASTRUCTURE; never refuses (L-342)."""
    kv_selfproof("cost_record")                            # <-- ASSERT, site 2
    kv, unparsed = read_kv(cost_path)
    if unparsed:
        warn_infra("COST.txt: %d unparsed line(s), reported not dropped: %s"
                   % (len(unparsed),
                      "; ".join("L%d %r" % (n, t[:60]) for n, t in unparsed[:4])))
    return kv, unparsed


def read_freeze(launch_path):
    """CALL SITE 3 -- freeze_record().  The sha keys are PHYSICS-CRITICAL."""
    kv_selfproof("freeze_record")                          # <-- ASSERT, site 3
    kv, unparsed = read_kv(launch_path)
    if unparsed:
        warn_infra("LAUNCH_RECORD.txt: %d line(s) carried no key/value pair "
                   "and were NOT silently dropped: %s"
                   % (len(unparsed),
                      "; ".join("L%d %r" % (n, t[:60]) for n, t in unparsed[:4])))
    return kv, unparsed


CALL_SITES = ("strict_completion", "cost_record", "freeze_record")


# ---------------------------------------------------------------------------
# selftest, with the mutation control
# ---------------------------------------------------------------------------
def _mutate():
    """REVERT the fix to the frozen single-pair behaviour.  The suite MUST go
    RED under this; a fix asserted without a mutation control is not proven."""
    def frozen_pairs(line):
        m = KV_RE_FROZEN.match(line.strip())
        return [(m.group(1), m.group(2).strip())] if m else []
    globals()["kv_pairs"] = frozen_pairs


def _real_files(run_root):
    """(kind, path) for every real artifact of this case that is on disk."""
    import glob
    out = []
    p = os.path.join(run_root, "LAUNCH_RECORD.txt")
    if os.path.isfile(p):
        out.append(("LAUNCH_RECORD", p))
    p = os.path.join(run_root, "COST.txt")
    if os.path.isfile(p):
        out.append(("COST", p))
    for p in sorted(glob.glob(os.path.join(run_root, "RUN_RC.*"))
                    + glob.glob(os.path.join(run_root, "*", "*", "RUN_RC.txt"))):
        out.append(("RUN_RC", p))
    return out


def _frozen_read(path):
    """Exactly what the FROZEN grader's _read_kv() produces."""
    out = {}
    try:
        for line in open(path, errors="replace"):
            m = KV_RE_FROZEN.match(line.strip())
            if m:
                out[m.group(1)] = m.group(2).strip()
    except OSError:
        return {}
    return out


READ_BY_KIND = {
    "LAUNCH_RECORD": FREEZE_PHYSICS_KEYS + ("host",) + FREEZE_LANDED_KEYS,
    "RUN_RC": RC_REQUIRED,
    "COST": None,          # the whole dict lands in rec['infrastructure']['cost']
}


def selftest(run_root):
    checks = []

    def chk(name, ok):
        checks.append((name, bool(ok)))

    # --- 1. the fix parses all pairs on a line ------------------------------
    p = dict(kv_pairs("status_smoke = smoke_rc=0 end=E note=N"))
    chk("multi-pair: smoke_rc recovered", p.get("smoke_rc") == "0")
    chk("multi-pair: end recovered", p.get("end") == "E")
    chk("multi-pair: note recovered", p.get("note") == "N")
    chk("multi-pair: status_smoke own segment is empty", p.get("status_smoke") == "")

    # --- 2. the fix parses a line the frozen regex SKIPS --------------------
    line = "solve rc = 0  arm = gpu  level = L3  wall_s = 879  cap_fired = 0  utc = U"
    p = dict(kv_pairs(line))
    chk("skipped line: now matches at all", bool(p))
    chk("skipped line: rc", p.get("rc") == "0")
    chk("skipped line: arm", p.get("arm") == "gpu")
    chk("skipped line: level", p.get("level") == "L3")
    chk("skipped line: wall_s", p.get("wall_s") == "879")
    chk("skipped line: cap_fired", p.get("cap_fired") == "0")
    chk("skipped line: utc", p.get("utc") == "U")
    chk("FROZEN regex demonstrably FAILS this line",
        KV_RE_FROZEN.match(line.strip()) is None)

    # --- 3. `=>` does not manufacture a key --------------------------------
    p = dict(kv_pairs("ldd_x = \tlibmpi.so.40 => /usr/lib/libmpi.so.40 (0x7f);"))
    chk("ldd: no bogus key '40'", "40" not in p)
    chk("ldd: the real key survives", "ldd_x" in p)

    # --- 4. single-pair lines are untouched --------------------------------
    for s, k, v in (("rc = 0", "rc", "0"), ("rc=0", "rc", "0"),
                    ("host = ip-10-0-0-1", "host", "ip-10-0-0-1"),
                    ("cost_basis = reported-by-owner, not measured",
                     "cost_basis", "reported-by-owner, not measured")):
        chk("single-pair untouched: %s" % s, dict(kv_pairs(s)).get(k) == v)

    # --- 5. a non-matching line is NEVER silently dropped -------------------
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        f = os.path.join(td, "x.txt")
        open(f, "w").write("rc = 0\nthis line has no pairs at all\n\n")
        kv, un = read_kv(f)
        chk("unparsed line is REPORTED, not dropped", len(un) == 1)
        chk("unparsed line carries its line number", un and un[0][0] == 2)
        chk("blank line is not reported as unparsed", len(un) == 1)
        chk("the good key still parses", kv.get("rc") == "0")
        f2 = os.path.join(td, "missing.txt")
        kv, un = read_kv(f2)
        chk("unreadable file -> empty dict", kv == {})
        chk("unreadable file -> reported, not silent", len(un) == 1)

    # --- 6. the planted control is live AT EVERY CALL SITE ------------------
    def _proof_ok(site):
        """The proof REFUSES (exit 2) on a blind reader.  Under the mutation
        control that refusal is the correct behaviour, so it is caught here and
        recorded as a FAILED check rather than aborting the suite -- otherwise
        the mutant run could not report its counts."""
        try:
            return bool(kv_selfproof(site))
        except SystemExit:
            return False
    for site in CALL_SITES:
        chk("planted control passes at call site %s" % site, _proof_ok(site))
    chk("there are exactly 3 call sites, each asserted", len(CALL_SITES) == 3)
    # the control must be SHOWN able to refuse (its own control)
    saved = globals()["kv_pairs"]
    try:
        globals()["kv_pairs"] = lambda line: []
        red = False
        try:
            kv_selfproof("negative-control")
        except SystemExit as e:
            red = (e.code == 2)
        chk("planted control REFUSES (exit 2) on a blind reader", red)
    finally:
        globals()["kv_pairs"] = saved
    bare = [i for i, L in enumerate(open(__file__).read().splitlines(), 1)
            if L.strip().startswith("assert ")]
    chk("no bare `assert` statement anywhere -- survives python3 -O (L-332)",
        not bare)

    # --- 7. REAL-FILE REGRESSION: no key the grader READS may move ----------
    files = _real_files(run_root)
    chk("real artifacts found on disk for %s" % CASE, len(files) > 0)
    moved = []
    for kind, path in files:
        old = _frozen_read(path)
        new, _un = read_kv(path)
        keys = READ_BY_KIND[kind]
        if keys is None:                   # COST: whole dict lands
            for k, v in old.items():
                if new.get(k) != v:
                    moved.append("%s:%s old=%r new=%r" % (path, k, v, new.get(k)))
        else:
            for k in keys:
                if old.get(k) != new.get(k):
                    moved.append("%s:%s old=%r new=%r"
                                 % (path, k, old.get(k), new.get(k)))
    chk("BLAST RADIUS ZERO: no key read by the frozen grader moves (%d files)"
        % len(files), not moved)
    if moved:
        for m in moved:
            print("    MOVED: %s" % m)

    # --- 8. the fix RECOVERS keys the frozen reader lost --------------------
    lr = [p for k, p in files if k == "LAUNCH_RECORD"]
    if lr:
        old = _frozen_read(lr[0])
        new, un = read_kv(lr[0])
        gained = sorted(set(new) - set(old))
        chk("LAUNCH_RECORD: the fix recovers previously-lost keys (%s)"
            % ", ".join(gained[:8]), len(gained) >= 5)
        chk("LAUNCH_RECORD: wall_s is now readable", "wall_s" in new)
        chk("LAUNCH_RECORD: cap_fired is now readable", "cap_fired" in new)
        chk("LAUNCH_RECORD: no line silently skipped", not un)

    failed = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print("  %s  %s" % ("ok  " if ok else "FAIL", n))
    print("SELFTEST: %d ok / %d FAILED  (of %d)"
          % (len(checks) - len(failed), len(failed), len(checks)))
    return 0 if not failed else 1


if __name__ == "__main__":
    rr = RUN_ROOT_DEFAULT
    args = sys.argv[1:]
    if "--run-root" in args:
        rr = args[args.index("--run-root") + 1]
    if "--mutate" in args:
        print("MUTATION CONTROL ACTIVE: the fix is REVERTED to the frozen "
              "single-pair KV_RE.  This suite MUST go RED.")
        _mutate()
    sys.exit(selftest(rr))
