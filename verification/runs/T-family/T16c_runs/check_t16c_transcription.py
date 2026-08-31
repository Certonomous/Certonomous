#!/usr/bin/env python3
"""REFUSE unless every numeric constant `analyse_t16c.py` restates is the value
the FROZEN pre-registration registers -- located BY LINE, with the registered
text quoted, in

    docs/campaigns/T-family/T16c_PREREGISTRATION.md
    sha256 0b425c40974581484f9ce91c44ad7bb3d4956fb1e81dad0ce03e7ba7e01bcd3f
    frozen by the supervisor at commit 8ff2cf36

THIS CHECKER REFUSES; IT DOES NOT REPORT.  Any mismatch exits 2.  A printed
warning that lets a bad transcription stand certifies nothing.

WHY IT EXISTS -- the gap it closes, stated exactly.  `analyse_t16c.py:285-306`
restates eight floors and tolerances, and `_station_floor_identity_check()` at
:316-319 compares them ONLY TO EACH OTHER and to a hardcoded literal.  The
comparator's `_carried_over_identity()` (:2293) additionally compares them
against the PARENT `analyse_t16.py`.  Neither closes the remaining link:
NOTHING asserts that the parent's values are the values the FROZEN DOCUMENT
says the parent carries.  A constant could agree with the parent, agree with
itself, and still not be what was registered.  That is the link checked here.

THE CONSTANTS ARE LEGITIMATE, NOT INVENTED GATES.  They are TRANSCRIPTIONS of a
frozen registration.  This file adds NO threshold and MOVES NO gate: it sits off
the grading path entirely, is never imported by the comparator, and can only
refuse -- it can never let a run grade that would otherwise have refused.

TWO AUTHORITIES, AND THE DIFFERENCE IS RECORDED RATHER THAN SMOOTHED OVER.  The
frozen document does NOT register a literal for every constant, and pretending
otherwise would be the same error this file exists to catch:

  LITERAL       the frozen document states the number itself, on a named line.
                The comparator is checked against THAT NUMBER.  Fully closed:
                the document is pinned by sha256, so the authority cannot move.

  BY_REFERENCE  the frozen document names the constant and binds it with
                "carried over byte-identically" WITHOUT restating the number.
                The authority is then the parent `analyse_t16.py`, and the
                comparator is checked against the parent's own source literal.
                *** THE NAMES `CONV_FLOOR` AND `G_TOL` DO NOT OCCUR ANYWHERE IN
                THE FROZEN DOCUMENT AT ALL *** -- MEASURED, zero occurrences.
                They are carried only by section 6's clause-level list at
                :259 (`C_CONV`, `C_G`).  This is DISCLOSED, not resolved here.

RESIDUAL EXPOSURE, NAMED AND LEFT OPEN.  For every BY_REFERENCE constant the
authority chain runs through `analyse_t16.py`, which the frozen document does
NOT pin (section 5 registers exactly ONE pin, `T16_registered.json`).  Its
digest is therefore REPORTED as provenance and is NOT gated -- the same
disposition the supervisor ruled for `exact_t16.py`, and for the same reason: a
pin the frozen document does not register would be a NEW GATE, and section 9
forbids moving a gate.  Closing it needs a successor registration, not a patch.

NEVER IMPORTS, NEVER EXECUTES.  Both source files are read with `ast` only.  A
checker that imported the comparator would run the comparator's module-level
code -- including its path finder -- and could not then be trusted to be inert
with respect to the live tree.  It also means stale bytecode cannot invert this
checker's controls, which is the standing hazard `__pycache__` clearing exists
for.  The controls clear `__pycache__` anyway; the real defence is not importing.

BLINDNESS.  This file computes NO T16 graded value and reads NOTHING under
`verification/runs/T-family/T16_runs/` except `analyse_t16.py`'s SOURCE TEXT.
It never touches a case directory, a field, a log or a marker.

usage: check_t16c_transcription.py            # exits 0 or 2
       check_t16c_transcription.py --selftest # every planted control limb
"""
import argparse
import ast
import hashlib
import math
import os
import re
import shutil
import sys
import tempfile

SELF = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(SELF, "..", "..", "..", ".."))
COMPARATOR = os.path.join(SELF, "analyse_t16c.py")
PARENT = os.path.abspath(os.path.join(SELF, "..", "T16_runs", "analyse_t16.py"))
DOC = os.path.join(REPO, "docs", "campaigns", "T-family", "T16c_PREREGISTRATION.md")

# THE PIN IS ON THE FROZEN PREFIX, NOT ON THE WHOLE FILE, AND THAT IS RULE 6
# EXPRESSED AS ARITHMETIC.  Rule 6 permits exactly one kind of change to a
# frozen document: a DATED AMENDMENT APPENDED AT THE FOOT, asserting `lines
# whose number changed above this section: 0`.  Pinning the whole file would
# make that legal route indistinguishable from an illegal edit, and the check
# would have to be disabled every time the rule was obeyed -- a check that must
# be switched off to comply with the rule it enforces is worse than none.
#
# So the FIRST `DOC_FROZEN_BYTES` bytes -- the v1.0 blob frozen at 8ff2cf36 --
# must hash to `DOC_SHA256`, and anything after them is an appended amendment,
# which is allowed.  An edit ABOVE the foot changes the prefix and REFUSES.
#
# EVERY CITATION BELOW IS RESOLVED AGAINST THE FROZEN PREFIX ONLY.  A quoted
# registration must be found in the v1.0 text at the line it names -- appended
# text can never satisfy a citation, so nobody can discharge a mismatch by
# adding a line at the foot that happens to contain the missing quote.
DOC_SHA256 = "0b425c40974581484f9ce91c44ad7bb3d4956fb1e81dad0ce03e7ba7e01bcd3f"
DOC_FROZEN_BYTES = 19049       # `git cat-file -s 8ff2cf36:<doc>`, MEASURED
EXIT_REFUSE = 2

# ---------------------------------------------------------------------------
# THE REGISTRATIONS.  Each row: the constant, its authority, the frozen line it
# is registered on, and the EXACT registered text that must still be found at
# that line.  The quote is not decoration: other records cite this document by
# line, so a citation that has drifted is itself a finding, and this file
# refuses on drift rather than silently checking the wrong line.
#
#   (name, kind, doc_line, quoted_registered_text, registered_value_or_None)
# ---------------------------------------------------------------------------
REGISTRATIONS = [
    # ---- LITERAL: the frozen document states the number itself ----
    ("C_TRANSPOSE_TOL",     "LITERAL", 94,
     "**`C_TRANSPOSE` threshold: `0.5` (dimensionless).**", 0.5),
    ("C_PROFILE_TOL",       "LITERAL", 99,
     "**`C_PROFILE` threshold: `1.0e-06`, CARRIED OVER UNCHANGED**", 1.0e-06),
    ("W1_FLOOR_T",          "LITERAL", 103,
     "- **`W1_FLOOR_T` = `1.0e-06`**, carried over from `analyse_t16.py:116`.", 1.0e-06),
    ("W1_FLOOR_V",          "LITERAL", 104,
     "`W1_FLOOR_V` 2.0e-4", 2.0e-4),
    ("W1_FLOOR_G",          "LITERAL", 104,
     "`W1_FLOOR_G` 2.0e-5", 2.0e-5),
    ("REFINEMENT",          "LITERAL", 108,
     "`r = 2`", 2.0),
    ("TRANSPOSE_SIGNATURE", "LITERAL", 142,
     "the **recovered value is within `0.1` of `-1.0`**", -1.0),
    ("TRANSPOSE_SIG_TOL",   "LITERAL", 142,
     "the **recovered value is within `0.1` of `-1.0`**", 0.1),

    # ---- BY_REFERENCE: named and bound, but the number lives in the parent ----
    ("MASS_FLOOR",  "BY_REFERENCE", 104,
     "- Every other floor — `W1_FLOOR_V` 2.0e-4, `W1_FLOOR_G` 2.0e-5, `MASS_FLOOR`,", None),
    ("PLAT_FLOOR",  "BY_REFERENCE", 105,
     "`PLAT_FLOOR`, the Roache floors, `FS` — **carried over byte-identically. Not one", None),
    ("CONV_FLOOR",  "BY_REFERENCE", 259,
     "`C_CONV`, `C_PLAT`, `C_G`; the completion rule; the cost basis.", None),
    ("G_TOL",       "BY_REFERENCE", 259,
     "`C_CONV`, `C_PLAT`, `C_G`; the completion rule; the cost basis.", None),
    ("PLANT_REL",   "BY_REFERENCE", 256,
     "**CARRIED OVER, unexamined and byte-identical:** every other gate, threshold,", None),
    ("DIM",         "BY_REFERENCE", 256,
     "**CARRIED OVER, unexamined and byte-identical:** every other gate, threshold,", None),
]

# The frozen document, section 4 THRESHOLD (:187-188), registers the station
# floor as "the registered `W1_FLOOR_T` ... **Not a new number.**"  The only way
# source text can carry "not a new number" is to BIND THE NAME rather than
# restate a literal.  A literal here would be a second number that merely
# happens to agree today.
NAME_BINDINGS = [
    ("STATION_FLOOR_T", "W1_FLOOR_T", 187,
     "**THRESHOLD.** `W1_T(j) <= 1.0e-06`, the registered `W1_FLOOR_T`"),
]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def module_constants(path):
    """Module-level `NAME = <literal>` assignments, by AST.  NEVER imported."""
    tree = ast.parse(open(path).read())
    out = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 \
                and isinstance(n.targets[0], ast.Name):
            try:
                out[n.targets[0].id] = ast.literal_eval(n.value)
            except Exception:
                pass
    return out


def module_name_bindings(path):
    """Module-level `NAME = OTHER_NAME` assignments, by AST."""
    tree = ast.parse(open(path).read())
    out = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 \
                and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Name):
            out[n.targets[0].id] = n.value.id
    return out


def frozen_prefix(doc, nbytes=DOC_FROZEN_BYTES):
    """The v1.0 bytes: the file truncated to the size of the blob at 8ff2cf36.
    Returns (sha256_of_prefix, prefix_lines, total_bytes)."""
    raw = open(doc, "rb").read()
    pre = raw[:nbytes]
    return (hashlib.sha256(pre).hexdigest(),
            pre.decode("utf-8").split("\n"),
            len(raw))


def check(comparator=COMPARATOR, parent=PARENT, doc=DOC, doc_sha=DOC_SHA256,
          nbytes=DOC_FROZEN_BYTES):
    """Returns (rc, messages).  rc 0 = certified, 2 = refused."""
    bad = []

    # ---- (0) EVERY INPUT IS PRESENT.  A checker that tracebacks on a missing
    # file has not refused; it has crashed, and a crash is not a verdict.
    for what, p in (("the frozen pre-registration", doc),
                    ("the comparator", comparator),
                    ("the parent instrument", parent)):
        if not os.path.isfile(p):
            bad.append("%s is absent at %s -- nothing can be certified against a "
                       "file that is not there" % (what, p))
    if bad:
        return EXIT_REFUSE, bad

    # ---- (1) THE FROZEN PREFIX HAS NOT MOVED ----------------------------
    if os.path.getsize(doc) < nbytes:
        bad.append("the pre-registration at %s is %d bytes, SHORTER than the %d-byte "
                   "blob frozen at 8ff2cf36 -- frozen text has been DELETED"
                   % (doc, os.path.getsize(doc), nbytes))
        return EXIT_REFUSE, bad
    got, lines, total = frozen_prefix(doc, nbytes)
    if got != doc_sha:
        bad.append("the first %d bytes of %s hash %s, NOT the frozen %s -- text AT OR "
                   "ABOVE the amendment foot has been edited, which rule 6 forbids "
                   "outright. The authority for every constant below has moved and "
                   "nothing here can be certified against it. (A dated amendment "
                   "APPENDED BELOW byte %d is the legal route and does NOT trip this.)"
                   % (nbytes, doc, got, doc_sha, nbytes))
        # Every later limb quotes lines out of this prefix, so refuse now rather
        # than quote lines from a document that is not the registered one.
        return EXIT_REFUSE, bad
    cvals = module_constants(comparator)
    pvals = module_constants(parent)

    # ---- (1) EVERY CITATION STILL POINTS WHERE IT CLAIMS -----------------
    for name, kind, ln, quote, _v in REGISTRATIONS:
        if ln < 1 or ln > len(lines):
            bad.append("%s cites %s:%d, which is outside the document (%d lines)"
                       % (name, os.path.basename(doc), ln, len(lines)))
        elif quote not in lines[ln - 1]:
            bad.append("%s cites %s:%d for the text %r, which is NOT on that line -- "
                       "the citation has drifted and the constant is being checked "
                       "against the wrong registration"
                       % (name, os.path.basename(doc), ln, quote))
    for name, target, ln, quote in NAME_BINDINGS:
        if ln > len(lines) or quote not in lines[ln - 1]:
            bad.append("%s cites %s:%d for %r, which is NOT on that line"
                       % (name, os.path.basename(doc), ln, quote))

    # ---- (2) EVERY CONSTANT EQUALS ITS REGISTERED VALUE ------------------
    for name, kind, ln, quote, want in REGISTRATIONS:
        if name not in cvals:
            bad.append("%s is not a module-level literal constant of %s -- the "
                       "transcription cannot be checked because it is not there"
                       % (name, os.path.basename(comparator)))
            continue
        got_v = cvals[name]
        if kind == "LITERAL":
            if got_v != want:
                bad.append("%s MISTRANSCRIBED: %s has %r, the frozen document "
                           "registers %r at %s:%d (%r)"
                           % (name, os.path.basename(comparator), got_v, want,
                              os.path.basename(doc), ln, quote))
        else:
            if name not in pvals:
                bad.append("%s is registered BY REFERENCE at %s:%d but is not a "
                           "module-level literal of the parent %s, so the value it "
                           "is carried over FROM does not exist"
                           % (name, os.path.basename(doc), ln, os.path.basename(parent)))
                continue
            if got_v != pvals[name]:
                bad.append("%s NOT CARRIED OVER BYTE-IDENTICALLY: %s has %r, the "
                           "parent %s has %r; the frozen document binds it at %s:%d "
                           "(%r) and section 6 says 'Not one is touched'"
                           % (name, os.path.basename(comparator), got_v,
                              os.path.basename(parent), pvals[name],
                              os.path.basename(doc), ln, quote))

    # ---- (3) "NOT A NEW NUMBER" MEANS A NAME, NOT A LITERAL --------------
    cbind = module_name_bindings(comparator)
    for name, target, ln, quote in NAME_BINDINGS:
        if cbind.get(name) != target:
            bad.append("%s must BIND THE NAME %s, not restate a literal: %s:%d "
                       "registers it as 'the registered %s ... Not a new number', and "
                       "a literal there is a SECOND number that merely agrees today. "
                       "Found: %s"
                       % (name, target, os.path.basename(doc), ln, target,
                          ("%s = %s" % (name, cbind[name])) if name in cbind
                          else ("%s = %r (a literal)" % (name, cvals.get(name)))))
    return (EXIT_REFUSE if bad else 0), bad


# ---------------------------------------------------------------------------
# PLANTED CONTROLS.  Standing rule 3: a limb with no planted control that
# reddens it is not verified.  Every limb below perturbs a SCRATCH COPY of the
# bytes the real producer wrote -- the control never authors a comparator, a
# parent or a registration -- and asserts the checker REFUSES.  The negative
# arm (unperturbed -> exit 0, silent) runs first AND last.
#
# No limb reads a case directory, a field, a log or a marker.  Nothing under
# T16_runs is written at any point: the parent-drift limb copies analyse_t16.py
# into scratch and perturbs the COPY.
# ---------------------------------------------------------------------------
ASSIGN_RE_TMPL = r"(?m)^(%s\s*=\s*)(-?[0-9][0-9eE.+\-]*)"


def _perturb_one_ulp(src, name):
    """Rewrite `NAME = <literal>` to the NEXT REPRESENTABLE DOUBLE.  One ULP is
    the smallest change a float can carry: a checker that survives it is
    comparing something other than the number."""
    m = re.search(ASSIGN_RE_TMPL % re.escape(name), src)
    if not m:
        return None, None
    v = float(m.group(2))
    nxt = math.nextafter(v, math.inf)
    if nxt == v:
        return None, None
    return src[:m.start()] + m.group(1) + repr(nxt) + src[m.end():], nxt


def _clear_pycache(d):
    for dirpath, dirnames, _ in os.walk(d):
        for n in list(dirnames):
            if n == "__pycache__":
                shutil.rmtree(os.path.join(dirpath, n), ignore_errors=True)


def selftest():
    fails = []

    def ok(cond, label):
        print("  [%s] %s" % ("ok " if cond else "FAIL", label))
        if not cond:
            fails.append(label)

    tmp = tempfile.mkdtemp(prefix="t16c_transcheck_")
    if os.path.realpath(tmp).startswith(os.path.realpath(SELF) + os.sep):
        sys.exit("REFUSE: selftest scratch resolves inside the rung tree")
    try:
        live_c = os.path.join(tmp, "analyse_t16c.py")
        live_p = os.path.join(tmp, "analyse_t16.py")
        live_d = os.path.join(tmp, "T16c_PREREGISTRATION.md")
        shutil.copyfile(COMPARATOR, live_c)   # bytes written by the real producer
        shutil.copyfile(PARENT, live_p)
        shutil.copyfile(DOC, live_d)
        _clear_pycache(tmp)

        # ---- NEGATIVE ARM, FIRST: the real files must go SILENT (rc 0) -----
        rc0, m0 = check(live_c, live_p, live_d)
        ok(rc0 == 0, "N1 UNPERTURBED real comparator/parent/document -> rc 0, silent "
                     "(%d msgs%s)" % (len(m0), (": " + m0[0]) if m0 else ""))

        # ---- POSITIVE ARM: ONE ULP on each constant, one at a time --------
        src_c = open(live_c).read()
        for name, kind, ln, quote, want in REGISTRATIONS:
            p = os.path.join(tmp, "mut_%s.py" % name)
            mutated, nxt = _perturb_one_ulp(src_c, name)
            if mutated is None:
                ok(False, "P:%s could not be perturbed -- no `%s = <literal>` "
                          "assignment found, so this limb tests NOTHING" % (name, name))
                continue
            open(p, "w").write(mutated)
            _clear_pycache(tmp)
            rc, msgs = check(p, live_p, live_d)
            hit = any(name in x and ("MISTRANSCRIBED" in x or "BYTE-IDENTICALLY" in x)
                      for x in msgs)
            ok(rc == EXIT_REFUSE and hit,
               "P:%-19s +1 ULP (%s -> %r) -> REFUSES on its own %s limb"
               % (name, kind, nxt, "LITERAL" if kind == "LITERAL" else "carry-over"))

        # ---- POSITIVE ARM: ONE BYTE EDITED INSIDE THE FROZEN PREFIX -------
        # The thing rule 6 forbids outright.  One byte, in the middle of the
        # frozen text, changing no number and no meaning -- it must still refuse.
        p = os.path.join(tmp, "doc_edited.md")
        raw = open(live_d, "rb").read()
        cut = DOC_FROZEN_BYTES // 2
        open(p, "wb").write(raw[:cut] + (b"." if raw[cut:cut + 1] != b"." else b",")
                            + raw[cut + 1:])
        _clear_pycache(tmp)
        rc, msgs = check(live_c, live_p, p)
        ok(rc == EXIT_REFUSE and any("has been edited" in x for x in msgs),
           "P:PREFIX  ONE byte edited at offset %d, INSIDE the frozen prefix -> "
           "REFUSES (rule 6: frozen files are never edited)" % cut)

        # ---- POSITIVE ARM: frozen text DELETED ---------------------------
        p = os.path.join(tmp, "doc_truncated.md")
        open(p, "wb").write(raw[:DOC_FROZEN_BYTES - 1])
        _clear_pycache(tmp)
        rc, msgs = check(live_c, live_p, p)
        ok(rc == EXIT_REFUSE and any("DELETED" in x for x in msgs),
           "P:TRUNC   the document shortened by one byte -> REFUSES rather than "
           "hashing a prefix it does not have")

        # ---- NEGATIVE ARM: an APPENDED amendment is LEGAL and stays SILENT -
        # The pin must not punish the one change rule 6 permits, or it would have
        # to be switched off to comply with the rule it enforces.
        p = os.path.join(tmp, "doc_amended.md")
        open(p, "wb").write(raw + b"\n\n---\n\n## AMENDMENT 99 -- a foot append\n\n"
                                  b"lines whose number changed above this section: 0\n")
        _clear_pycache(tmp)
        rc, msgs = check(live_c, live_p, p)
        ok(rc == 0, "N3 a DATED AMENDMENT APPENDED AT THE FOOT -> rc 0, silent: the "
                    "legal rule-6 route is not punished (%d msgs%s)"
                    % (len(msgs), (": " + msgs[0]) if msgs else ""))

        # ---- POSITIVE ARM: a quote satisfied only by APPENDED text --------
        # Nobody may discharge a mismatch by appending a line at the foot that
        # contains the missing registration.  Citations resolve in the PREFIX only.
        p = os.path.join(tmp, "doc_append_quote.md")
        open(p, "wb").write(raw + b"\n- **`W1_FLOOR_T` = `9.9e-99`**\n")
        pc = os.path.join(tmp, "mut_append.py")
        m2, _ = _perturb_one_ulp(src_c, "W1_FLOOR_T")
        open(pc, "w").write(m2)
        _clear_pycache(tmp)
        rc, msgs = check(pc, live_p, p)
        ok(rc == EXIT_REFUSE and any("W1_FLOOR_T" in x and "MISTRANSCRIBED" in x
                                     for x in msgs),
           "P:APPEND  a registration appended at the FOOT cannot satisfy a citation "
           "-> still REFUSES on the perturbed W1_FLOOR_T")

        # ---- POSITIVE ARM: a citation that has DRIFTED off its line -------
        # Driven with the mutated document's OWN digest so the sha limb passes
        # and THIS limb is the one exercised -- otherwise the sha limb would
        # mask it and the drift limb would never be shown able to fire.
        p = os.path.join(tmp, "doc_drift.md")
        dl = open(live_d, encoding="utf-8").read().split("\n")
        dl.insert(0, "<!-- MUTANT: one line inserted, every citation below drifts -->")
        open(p, "w", encoding="utf-8").write("\n".join(dl))
        _clear_pycache(tmp)
        rc, msgs = check(live_c, live_p, p, doc_sha=sha256_of(p),
                         nbytes=os.path.getsize(p))
        ok(rc == EXIT_REFUSE and any("drifted" in x for x in msgs),
           "P:CITATION one line inserted at the top -> REFUSES on the drift limb "
           "(%d citations detected as drifted)"
           % sum(1 for x in msgs if "drifted" in x))

        # ---- POSITIVE ARM: the parent drifts under a BY_REFERENCE constant -
        p = os.path.join(tmp, "parent_drift.py")
        src_p = open(live_p).read()
        mutated, nxt = _perturb_one_ulp(src_p, "MASS_FLOOR")
        open(p, "w").write(mutated)
        _clear_pycache(tmp)
        rc, msgs = check(live_c, p, live_d)
        ok(rc == EXIT_REFUSE and any("MASS_FLOOR" in x and "BYTE-IDENTICALLY" in x
                                     for x in msgs),
           "P:PARENT MASS_FLOOR +1 ULP in the PARENT (%r) -> REFUSES: the "
           "BY_REFERENCE authority is genuinely read, not assumed" % nxt)

        # ---- POSITIVE ARM: "not a new number" replaced by a number --------
        p = os.path.join(tmp, "mut_station.py")
        s2 = src_c.replace("STATION_FLOOR_T = W1_FLOOR_T",
                           "STATION_FLOOR_T = 1.0e-6")
        ok(s2 != src_c, "P:STATION the `STATION_FLOOR_T = W1_FLOOR_T` binding was "
                        "found and replaced (the mutation is real, not a no-op)")
        open(p, "w").write(s2)
        _clear_pycache(tmp)
        rc, msgs = check(p, live_p, live_d)
        ok(rc == EXIT_REFUSE and any("BIND THE NAME" in x for x in msgs),
           "P:STATION STATION_FLOOR_T rebound to a LITERAL that agrees numerically "
           "-> REFUSES anyway: section 4 registers a name, not a second number")

        # ---- POSITIVE ARM: the constant deleted outright ------------------
        p = os.path.join(tmp, "mut_gone.py")
        open(p, "w").write(re.sub(r"(?m)^W1_FLOOR_T\s*=.*$", "", src_c))
        _clear_pycache(tmp)
        rc, msgs = check(p, live_p, live_d)
        ok(rc == EXIT_REFUSE and any("W1_FLOOR_T" in x for x in msgs),
           "P:ABSENT  W1_FLOOR_T's assignment deleted -> REFUSES rather than "
           "skipping a constant it cannot find")

        # ---- NEGATIVE ARM, LAST: restored bytes go silent AGAIN -----------
        _clear_pycache(tmp)
        rc9, m9 = check(live_c, live_p, live_d)
        ok(rc9 == 0, "N2 RESTORED to the real bytes -> rc 0, silent again (%d msgs)"
                     % len(m9))

        # ---- THE PLANTED-ASSERT COUNTER (L-332) ---------------------------
        # An `assert` vanishes under `python3 -O` and the refusal it carried
        # vanishes with it.  The counter is itself shown able to see one.
        src = open(os.path.abspath(__file__)).read()
        n = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(src)))
        planted = sum(isinstance(x, ast.Assert)
                      for x in ast.walk(ast.parse(src + "\nassert True\n")))
        ok(n == 0 and planted == 1,
           "A1 AST assert count in this file = %d (counter sees a planted assert: %d)"
           % (n, planted))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    rc, msgs = check()
    if rc:
        for m in msgs:
            sys.stderr.write("REFUSE: %s\n" % m)
        sys.stderr.write("REFUSE (exit %d): the transcription is NOT certified.\n"
                         % EXIT_REFUSE)
        return EXIT_REFUSE
    nl = sum(1 for r in REGISTRATIONS if r[1] == "LITERAL")
    nr = len(REGISTRATIONS) - nl
    print("CERTIFIED: %d constant(s) equal their registration in the document frozen "
          "at 8ff2cf36 (%d against a LITERAL the document states, %d BY_REFERENCE "
          "against the parent it binds them to), %d name-binding(s) still bind a name."
          % (len(REGISTRATIONS), nl, nr, len(NAME_BINDINGS)))
    print("PROVENANCE, REPORTED AND NOT GATED: %s sha256 %s -- the frozen document "
          "registers exactly ONE pin (section 5) and a pin it does not register would "
          "be a new gate, so the BY_REFERENCE authority chain remains an OPEN exposure."
          % (os.path.basename(PARENT), sha256_of(PARENT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
