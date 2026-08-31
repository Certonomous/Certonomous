#!/usr/bin/env python3
"""VR10 -- PAPER SIDECAR FIDELITY.

Gate question: does every PDF in `docs/papers/` carry a `.txt` sidecar that is
present, non-trivial, AND ACTUALLY THE TEXT OF THAT PDF?

WHY IT IS NOT MERELY A TIDINESS ITEM. CLAUDE.md's filing table requires each
paper to be "`docs/papers/<topic>/author_year_identifier.pdf` **plus a matching
`.txt` sidecar**". The sidecar is not decoration: IT IS THE ONLY THING A TEXT
SWEEP CAN SEE. A team asking "do we already hold a reference for X" greps the
sidecars. A PDF with no sidecar is INVISIBLE to that question, and a "no" over it
is a FALSE NEGATIVE, not an answer.

STANDING RULE 15 IS THE SHARPER HALF: "Title-page verification of every retrieved
paper (L-144). Never by file type, filename or hash -- a manifest can be
internally consistent and externally false." A sidecar that EXISTS but belongs to
a different document passes every presence check and satisfies rule 15 not at
all. So this item checks AGREEMENT, not existence.

WHAT IS MINE: the measurement. The papers belong to six teams' topic folders and
EXTRACTING A MISSING SIDECAR IS EACH OWNER'S ACT. This item extracts nothing into
the repository and edits nothing.

-------------------------------------------------------------------------------
WHAT THIS ITEM DOES NOT DO -- AND IT MATTERS, BECAUSE THE TOPIC IS ON THE DESK
-------------------------------------------------------------------------------
The "34 % sidecar gap" is ALREADY ON SANAA'S DESK as a referred item. THIS ITEM
DOES NOT RULE ON IT, does not propose a remedy and does not re-open the referral.
It MEASURES, and it exists because the board's own record and the disk DISAGREE:
the 2026-08-30 entry records the gap as "closed by extracting", and the disk on
2026-08-31 still shows 48 PDFs with no sidecar. A discrepancy between the record
and the disk is verification's own business whatever else is referred.

-------------------------------------------------------------------------------
SS2j -- WHO WROTE THE BYTES
-------------------------------------------------------------------------------
  * the PDFs -- written by their PUBLISHERS and retrieved by the lab. The one
    referent in this repository nobody here authored.
  * the sidecars -- written by the lab's own extraction passes.
  * the page-1 text this item compares against -- produced by `pdftotext`,
    THE REAL PRODUCTION EXTRACTOR, invoked exactly as an extraction pass invokes
    it. Not a re-implementation, not a fixture.

BOTH ANSWERS ALREADY EXIST IN THE REAL CORPUS, so nothing is planted: there are
real PDFs with faithful sidecars, a real 77-byte stub sidecar, and real PDFs with
none. The one thing the selftest constructs is limb X3's CROSS-PAIRING -- one
real PDF's page-1 text against a DIFFERENT real paper's sidecar -- which uses
only real bytes and exists to prove the comparator can say NO.
"""

import argparse
import os
import re
import subprocess
import sys

REPO = "/home/ubuntu/Certonomous"
PAPERS = os.path.join(REPO, "docs/papers")

# A sidecar below this is a stub, not an extraction. The real corpus contains a
# 77-byte specimen, which is what makes the threshold demonstrable rather than
# arbitrary.
MIN_SIDECAR_BYTES = 200

# Fraction of page-1 VERBATIM n-word phrases that must appear in the sidecar's
# opening. See agreement() for why this is a structural test and not a tuned
# number, and limb X3 for the assertion that it separates on real bytes.
SHINGLE_WORDS = 8
AGREE_THRESHOLD = 0.30
OPENING_CHARS = 4000

STOP = {"the", "and", "for", "with", "that", "this", "from", "are", "was", "not",
        "但", "of", "in", "to", "a", "is", "on", "by", "as", "at", "an", "be",
        "we", "it", "its", "or", "which", "have", "has", "can", "all"}


class Refusal(Exception):
    """The instrument cannot honestly grade. Exit 2, never a degraded answer."""


# ---------------------------------------------------------------- helpers -----

def require_pdftotext():
    try:
        p = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True,
                           timeout=20)
    except (OSError, subprocess.SubprocessError) as exc:
        raise Refusal("pdftotext unavailable (%s) -- WITHOUT THE REAL EXTRACTOR "
                      "every sidecar would read 'cannot verify', which is "
                      "PARSER BLINDNESS and not a finding" % exc)
    if p.returncode not in (0, 99):
        raise Refusal("pdftotext returned rc=%s" % p.returncode)
    return (p.stderr or p.stdout).splitlines()[0] if (p.stderr or p.stdout) else "pdftotext"


def page1_text(pdf, timeout=60):
    """Page 1 of `pdf` via the REAL extractor. None if it cannot be read."""
    try:
        p = subprocess.run(["pdftotext", "-f", "1", "-l", "1", pdf, "-"],
                           capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0:
        return None
    return p.stdout


def tokens(text):
    if not text:
        return set()
    out = set()
    for w in re.findall(r"[A-Za-z][A-Za-z\-']{3,}", text.lower()):
        if w not in STOP:
            out.add(w)
    return out


def shingles(text, n=SHINGLE_WORDS):
    """Normalised n-word phrases. Whitespace and case are collapsed so that a
    re-flowed extraction still matches; nothing else is altered."""
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    if len(words) < n:
        return []
    return [" ".join(words[i:i + n]) for i in range(len(words) - n + 1)]


def agreement(page1, sidecar_opening):
    """Fraction of page-1 SHINGLES appearing verbatim in the sidecar opening.

    WHY SHINGLES AND NOT VOCABULARY OVERLAP -- and this is the whole reason the
    comparator has the shape it has. A first cut scored the fraction of page-1
    CONTENT TOKENS present in the sidecar. Driven on real bytes it scored 0.985
    for a faithful pairing and 0.481 FOR A DELIBERATELY WRONG ONE: two unrelated
    CFD papers share half their vocabulary, because that is what a shared field
    IS. A comparator that cannot separate 0.985 from 0.481 cannot verify a title
    page, and standing rule 15 is not met by a number that high for a document
    the sidecar does not belong to.

    A faithful sidecar is an EXTRACTION of the PDF, so its opening reproduces
    page 1 NEARLY VERBATIM. An %d-word verbatim phrase is a structural property
    of that relationship, not a tuned quantity: unrelated papers in the same
    field share vocabulary but essentially never share long exact phrases. The
    threshold is therefore not fitted to this corpus -- limb X3 asserts the
    separation rather than assuming it.
    """
    a = shingles(page1)
    if not a:
        return None            # cannot judge; never silently a pass
    b = set(shingles(sidecar_opening))
    return len([s for s in a if s in b]) / float(len(a))


def find_pdfs():
    if not os.path.isdir(PAPERS):
        raise Refusal("docs/papers absent at %s" % PAPERS)
    out = []
    for dp, dn, fn in os.walk(PAPERS):
        dn[:] = [d for d in dn if d != ".git"]
        for f in fn:
            if f.lower().endswith(".pdf"):
                out.append(os.path.join(dp, f))
    if not out:
        raise Refusal("ZERO PDFs under docs/papers -- a reader that finds no "
                      "papers reports a vacuous PASS")
    return sorted(out)


def classify(pdf, extract=True):
    """MISSING / STUB / MISMATCH / UNREADABLE / OK, with the number behind it."""
    side = pdf[:-4] + ".txt"
    if not os.path.exists(side):
        return "MISSING", None
    size = os.path.getsize(side)
    if size < MIN_SIDECAR_BYTES:
        return "STUB", size
    if not extract:
        return "OK", size
    p1 = page1_text(pdf)
    if p1 is None:
        return "UNREADABLE", size
    opening = open(side, encoding="utf-8", errors="replace").read(OPENING_CHARS)
    frac = agreement(p1, opening)
    if frac is None:
        return "UNREADABLE", size
    if frac < AGREE_THRESHOLD:
        return "MISMATCH", round(frac, 3)
    return "OK", round(frac, 3)


# ------------------------------------------------------------- selftest -------

def selftest():
    results = []

    def ok(n, d):
        results.append((n, True, d))

    def bad(n, d):
        results.append((n, False, d))

    try:
        ver = require_pdftotext()
        pdfs = find_pdfs()
    except Refusal as exc:
        print("SELFTEST REFUSED: %s" % exc)
        return 2

    print("  extractor: %s (THE REAL PRODUCTION EXTRACTOR)" % ver)
    print("  corpus: %d PDFs under docs/papers (producers: their publishers)"
          % len(pdfs))

    # Cheap partition first -- no extraction, so the selftest stays inside a
    # small cap while the census pays for the full pass.
    missing = [p for p in pdfs if not os.path.exists(p[:-4] + ".txt")]
    stubs = [p for p in pdfs
             if os.path.exists(p[:-4] + ".txt")
             and os.path.getsize(p[:-4] + ".txt") < MIN_SIDECAR_BYTES]
    sized = [p for p in pdfs
             if os.path.exists(p[:-4] + ".txt")
             and os.path.getsize(p[:-4] + ".txt") >= MIN_SIDECAR_BYTES]
    print("  partition: %d MISSING / %d STUB / %d sized"
          % (len(missing), len(stubs), len(sized)))

    # -- P1 the reader must SEE a real MISSING sidecar.
    if missing:
        ok("P1 positive (a real MISSING sidecar is seen)",
           "%d missing; specimen %s"
           % (len(missing), os.path.relpath(missing[0], PAPERS)))
    else:
        bad("P1 positive (a real MISSING sidecar is seen)",
            "none missing -- reader never shown able to return MISSING")

    # -- P2 the reader must SEE a real STUB. The corpus holds a 77-byte one.
    if stubs:
        ok("P2 positive (a real STUB sidecar is seen)",
           "%d stub(s); specimen %s at %d bytes"
           % (len(stubs), os.path.relpath(stubs[0], PAPERS),
              os.path.getsize(stubs[0][:-4] + ".txt")))
    else:
        bad("P2 positive (a real STUB sidecar is seen)",
            "no stub in the corpus, so MIN_SIDECAR_BYTES is an untested "
            "threshold and its value is unjustified here")

    # -- P3 NEGATIVE: a real faithful sidecar must read OK through the REAL
    #    extractor. Without this the item is a detector that fires on everything.
    good = None
    for p in sized[:6]:
        verdict, val = classify(p)
        if verdict == "OK":
            good = (p, val)
            break
    if good:
        ok("P3 negative (a real faithful sidecar reads OK)",
           "%s agreement=%s" % (os.path.relpath(good[0], PAPERS), good[1]))
    else:
        bad("P3 negative (a real faithful sidecar reads OK)",
            "no sized sidecar in the first 6 read OK -- the comparator may be "
            "rejecting good extractions, and every MISMATCH would be suspect")

    # -- X3 THE DISCRIMINATION LIMB, and the one that makes rule 15 real:
    #    a real PDF's page 1 against a DIFFERENT real paper's sidecar must
    #    DISAGREE. If it agrees, the comparator cannot tell documents apart and
    #    a corpus-wide OK means nothing.
    if good and len(sized) > 1:
        other = next((q for q in sized if q != good[0]), None)
        p1 = page1_text(good[0])
        wrong = open(other[:-4] + ".txt", encoding="utf-8",
                     errors="replace").read(OPENING_CHARS)
        frac = agreement(p1, wrong)
        faithful = good[1]
        if frac is None:
            bad("X3 cross-paired sidecar DISAGREES",
                "page-1 text unreadable for the specimen; limb void")
        elif frac >= AGREE_THRESHOLD:
            bad("X3 cross-paired sidecar DISAGREES",
                "agreement=%.3f >= %.2f on a DELIBERATELY WRONG pairing -- the "
                "comparator cannot tell two documents apart, so it cannot "
                "verify a title page and rule 15 is not met"
                % (frac, AGREE_THRESHOLD))
        elif not isinstance(faithful, float) or faithful < AGREE_THRESHOLD:
            bad("X3 cross-paired sidecar DISAGREES",
                "the wrong pairing scored %.3f but the FAITHFUL pairing scored "
                "%s -- without a passing positive the low score proves only "
                "that the comparator rejects everything" % (frac, faithful))
        elif (faithful - frac) < 0.5:
            bad("X3 cross-paired sidecar DISAGREES",
                "faithful %.3f vs wrong %.3f -- separation %.3f is too narrow "
                "to call the threshold structural rather than fitted"
                % (faithful, frac, faithful - frac))
        else:
            ok("X3 cross-paired sidecar DISAGREES WITH CLEAR SEPARATION",
               "%s page1: faithful sidecar %.3f vs %s sidecar %.3f "
               "-> separation %.3f across the %.2f threshold"
               % (os.path.relpath(good[0], PAPERS), faithful,
                  os.path.relpath(other, PAPERS), frac, faithful - frac,
                  AGREE_THRESHOLD))
    else:
        bad("X3 cross-paired sidecar DISAGREES",
            "not enough sized sidecars to cross-pair; limb cannot be driven")

    # -- N1 REFUSAL: no extractor must REFUSE, not mark everything unverifiable.
    saved = globals()["subprocess"]

    class _Boom(object):
        SubprocessError = subprocess.SubprocessError

        @staticmethod
        def run(*a, **k):
            raise OSError("planted: pdftotext unavailable")

    try:
        globals()["subprocess"] = _Boom
        require_pdftotext()
        bad("N1 refusal when the extractor is absent", "did not refuse")
    except Refusal:
        ok("N1 refusal when the extractor is absent", "refused (exit 2 path)")
    except OSError:
        bad("N1 refusal when the extractor is absent", "raised OSError not Refusal")
    finally:
        globals()["subprocess"] = saved

    # -- N2 REFUSAL: no papers must REFUSE.
    saved_p = globals()["PAPERS"]
    try:
        globals()["PAPERS"] = "/nonexistent/vr10/papers"
        find_pdfs()
        bad("N2 refusal when docs/papers is unreadable", "did not refuse")
    except Refusal:
        ok("N2 refusal when docs/papers is unreadable", "refused (exit 2 path)")
    finally:
        globals()["PAPERS"] = saved_p

    # -- N3 the agreement function must REFUSE to judge empty page-1 text
    #    rather than scoring it 0 and calling it a mismatch.
    if agreement("", "anything at all here") is None:
        ok("N3 empty page-1 text is unjudgeable, not a mismatch",
           "agreement() returns None, so UNREADABLE is distinct from MISMATCH")
    else:
        bad("N3 empty page-1 text is unjudgeable, not a mismatch",
            "an unreadable PDF would be scored as a content mismatch")

    print()
    for n, g, d in results:
        print("  [%s] %s -- %s" % ("ok" if g else "FAIL", n, d))
    nbad = sum(1 for _, g, _ in results if not g)
    print("\nSELFTEST: %d case(s), %d failure(s)" % (len(results), nbad))
    return 0 if nbad == 0 else 2


# ---------------------------------------------------------------- census ------

def run_census():
    ver = require_pdftotext()
    pdfs = find_pdfs()
    buckets = {}
    for p in pdfs:
        verdict, val = classify(p)
        buckets.setdefault(verdict, []).append((p, val))

    print("VR10 -- paper sidecar fidelity "
          "(frozen: verification/campaign/VR10_PREREGISTRATION.md)")
    print("  repo=%s" % REPO)
    print("  extractor: %s" % ver)
    print("  PDFs: %d" % len(pdfs))
    for k in ("OK", "MISSING", "STUB", "MISMATCH", "UNREADABLE"):
        print("    %-11s %d" % (k, len(buckets.get(k, []))))

    for k in ("MISSING", "STUB", "MISMATCH", "UNREADABLE"):
        rows = buckets.get(k, [])
        if not rows:
            continue
        print("\n  %s roll call:" % k)
        for p, val in rows:
            print("    %-70s %s" % (os.path.relpath(p, PAPERS), val))

    bad = sum(len(buckets.get(k, [])) for k in ("MISSING", "STUB", "MISMATCH"))
    unreadable = len(buckets.get("UNREADABLE", []))
    if unreadable:
        print("\n  NOTE: %d PDF(s) UNREADABLE by the extractor are REPORTED AND "
              "NOT GATED -- 'I cannot read it' is not 'it is wrong'."
              % unreadable)
    if bad:
        print("\nVERDICT: GATE FAIL -- %d of %d papers lack a usable sidecar "
              "(%d missing, %d stub, %d mismatched). A PDF with no usable "
              "sidecar is INVISIBLE to every text sweep, so a 'we do not hold "
              "this reference' answer over it is a FALSE NEGATIVE (rule 15, "
              "L-144). This is a finding about the LIBRARY, not about any run: "
              "NO VERDICT IS WITHDRAWN, and EXTRACTING A SIDECAR IS THE OWNING "
              "TEAM'S ACT -- this item extracts none."
              % (bad, len(pdfs), len(buckets.get("MISSING", [])),
                 len(buckets.get("STUB", [])), len(buckets.get("MISMATCH", []))))
        return 1
    print("\nVERDICT: PASS -- every paper carries a sidecar that agrees with its "
          "own first page.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="VR10 paper sidecar fidelity")
    ap.add_argument("--selftest", action="store_true",
                    help="drive both control limbs on the real corpus; exit 2 on "
                         "any failure or refusal")
    args = ap.parse_args()
    try:
        if args.selftest:
            print("VR10 SELFTEST -- controls read real PDFs, real sidecars and "
                  "the real pdftotext extractor (SS2j.2)")
            return selftest()
        return run_census()
    except Refusal as exc:
        print("REFUSED: %s" % exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
