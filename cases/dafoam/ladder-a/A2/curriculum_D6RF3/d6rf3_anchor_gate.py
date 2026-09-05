#!/usr/bin/env python3
"""Curriculum D6RF3 -- `G-ANCHOR`, THE REGISTERED PRE-COMPUTE GATE.

THE RULE IT ENFORCES, registered by the dafoam-supervisor 2026-09-03 and stated
in his words:

    Any reader that splits a file on a sentinel must have that sentinel's
    UNIQUENESS ASSERTED AT REGISTRATION, on the bytes it will actually read --
    not merely refused at run time.

`D6RF-BLOCKING-1` is what that rule is for.  Both of D6R's anchor-scoped
consumers DID refuse honestly on `count != 1`.  **What was never checked is
whether the producer could satisfy them** -- and it could not, because the
docstring sentence explaining the anchor reproduced it.  A run-time refusal
turns an unrunnable registration into a wasted launch; a registration-time
assertion turns it into a defect found before compute.

WHAT THIS GATE ASSERTS, per (reader, producer) pair, on the REAL bytes:

  A1  the reader declares a sentinel and a producer, both parsed OUT OF THE
      READER'S OWN SOURCE -- never typed here, so a reader whose anchor changes
      cannot drift past this gate.
  A2  the producer the reader NAMES is the producer this item stages, and the
      md5 the reader PINS is that file's actual md5.  (This is the clause that
      would have caught the fact that a one-character reword makes a pinned
      consumer refuse one step EARLIER than the anchor.)
  A3  the sentinel occurs EXACTLY ONCE in that producer.
  A4  the header `split(SENTINEL)[0]` is at least MIN_HEADER_CHARS long -- a
      count of 1 AT THE WRONG SITE would still be wrong, and the predecessor's
      truncated header was 1,396 characters of a 12,861-character file.
  A5  the header carries every symbol the consumers read out of the exec'd
      namespace.  MEASURED on the predecessor: the truncated header carried
      `daOptions` (the docstring mentions it) but NOT `class Top`, `POINTS` or
      `U0` -- so a `daOptions`-only check would have passed it.

REFUSES (exit 3) rather than degrading.  `--selftest` drives it in BOTH
directions on real bytes: the repaired producer must PASS, and the ORIGINAL --
still on disk, unedited -- must REFUSE at A3.
"""
import argparse
import ast
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
D6R = os.path.abspath(os.path.join(HERE, os.pardir, "curriculum_D6R"))

RC_ANCHOR_REFUSAL = 3
MIN_HEADER_CHARS = 9000            # the correct split yields 10,536; the broken one 1,396
REQUIRED_SYMBOLS = ("class Top", "POINTS", "U0 =", "daOptions", "CL_TARGETS", "WEIGHTS")
READERS = ("d6rf3_fd_endpoint.py", "d6rf3_ref_off.py")
STAGED_PRODUCER = "d6rf3_opt_runScript.py"


def refuse(check, detail):
    sys.stderr.write("D6RF3_ANCHOR REFUSE %s %s\n" % (check, detail))
    sys.exit(RC_ANCHOR_REFUSAL)


def md5_of(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def read_constants(path):
    """Parse PRODUCER / PRODUCER_MD5 / ANCHOR out of the reader's OWN source."""
    tree = ast.parse(open(path).read(), filename=path)
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) \
                and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            out[node.targets[0].id] = node.value.value
    return out


def check_pair(reader_path, work_dir, verbose=True):
    name = os.path.basename(reader_path)
    c = read_constants(reader_path)
    # ---- A1 --------------------------------------------------------------
    for k in ("PRODUCER", "PRODUCER_MD5", "ANCHOR"):
        if k not in c:
            refuse("A1", "%s declares no module-level %s" % (name, k))
    producer, pinned, anchor = c["PRODUCER"], c["PRODUCER_MD5"], c["ANCHOR"]
    # ---- A2 --------------------------------------------------------------
    if producer != STAGED_PRODUCER:
        refuse("A2", "%s names producer %r; this item stages %r"
               % (name, producer, STAGED_PRODUCER))
    ppath = os.path.join(work_dir, producer)
    if not os.path.isfile(ppath):
        refuse("A2", "%s names producer %r, absent from %s" % (name, producer, work_dir))
    actual = md5_of(ppath)
    if actual != pinned:
        refuse("A2", "%s pins producer md5 %s; the file on disk is %s. A pinned "
                     "consumer refuses at the md5 check BEFORE it ever counts "
                     "the anchor." % (name, pinned, actual))
    src = open(ppath).read()
    # ---- A3 --------------------------------------------------------------
    n = src.count(anchor)
    if n != 1:
        refuse("A3", "sentinel %r occurs %d times in %s (need exactly 1). %s "
                     "splits on it, so a second occurrence truncates the header "
                     "at the FIRST one. THIS IS D6RF-BLOCKING-1."
               % (anchor, n, producer, name))
    # ---- A4 --------------------------------------------------------------
    head = src.split(anchor)[0]
    if len(head) < MIN_HEADER_CHARS:
        refuse("A4", "the header %s would exec is %d chars, below the registered "
                     "floor %d -- the sentinel is unique but at the WRONG SITE"
               % (name, len(head), MIN_HEADER_CHARS))
    # ---- A5 --------------------------------------------------------------
    missing = [s for s in REQUIRED_SYMBOLS if s not in head]
    if missing:
        refuse("A5", "the header %s would exec is missing %s -- the consumers "
                     "read these out of the exec'd namespace" % (name, missing))
    if verbose:
        print("  %-26s producer=%s md5=%s anchor=%r count=1 header=%d chars, all "
              "%d symbols present" % (name, producer, actual[:12] + "...", anchor,
                                      len(head), len(REQUIRED_SYMBOLS)))
    return {"reader": name, "producer": producer, "md5": actual,
            "anchor": anchor, "count": n, "header_chars": len(head)}


def gate(work_dir):
    print("D6RF3 G-ANCHOR -- %d anchor-scoped readers, on the bytes they will "
          "actually read" % len(READERS))
    res = [check_pair(os.path.join(work_dir, r), work_dir) for r in READERS]
    print("D6RF3_ANCHOR_PASS readers=%d producer=%s" % (len(res), STAGED_PRODUCER))
    return res


def selftest():
    import shutil, tempfile
    ok, fail = [], []

    def check(label, fn, want_refusal):
        try:
            fn()
            got, det = "no-refusal", ""
        except SystemExit as e:
            got, det = ("REFUSED" if e.code == RC_ANCHOR_REFUSAL else
                        "EXIT:%s" % e.code), ""
        except Exception as e:                                   # noqa: BLE001
            got, det = "EXCEPTION:%s" % type(e).__name__, repr(e)[:120]
        want = "REFUSED" if want_refusal else "no-refusal"
        print("  %-64s want=%-11s got=%-11s %s"
              % (label, want, got, "PASS" if got == want else "FAIL"))
        if det:
            print("        %s" % det)
        (ok if got == want else fail).append(label)

    print("D6RF3 G-ANCHOR SELFTEST -- both directions, on REAL bytes\n")
    print("A. THE POSITIVE LEG, on this item's own derived files")
    check("the repaired producer PASSES the gate for both readers",
          lambda: gate(HERE), False)

    print("\nB. THE NEGATIVE LEG, on the ORIGINAL producer, still on disk unedited")
    td = tempfile.mkdtemp(prefix="d6rf3_anchor_")
    # a reader re-pointed at the ORIGINAL bytes under this item's staged name
    shutil.copy2(os.path.join(D6R, "d6r_opt_runScript.py"),
                 os.path.join(td, STAGED_PRODUCER))
    orig_md5 = md5_of(os.path.join(td, STAGED_PRODUCER))
    r = open(os.path.join(HERE, "d6rf3_fd_endpoint.py")).read()
    r = re.sub(r'PRODUCER_MD5 = "[0-9a-f]{32}"',
               'PRODUCER_MD5 = "%s"' % orig_md5, r)
    open(os.path.join(td, "d6rf3_fd_endpoint.py"), "w").write(r)
    check("the ORIGINAL producer (sentinel twice) REFUSES at A3",
          lambda: check_pair(os.path.join(td, "d6rf3_fd_endpoint.py"), td), True)
    # and prove WHY: the truncated header is short and missing the symbols
    orig = open(os.path.join(D6R, "d6r_opt_runScript.py")).read()
    anchor = read_constants(os.path.join(HERE, "d6rf3_fd_endpoint.py"))["ANCHOR"]
    broken = orig.split(anchor)[0]
    print("        the header A3 prevented: %d chars, missing %s"
          % (len(broken), [s for s in REQUIRED_SYMBOLS if s not in broken]))
    okb = len(broken) == 1396 and "class Top" not in broken and "daOptions" in broken
    print("  %-64s %s" % ("PLANT: it is 1396 chars, carries daOptions and NOT "
                          "class Top", "PASS" if okb else "FAIL"))
    (ok if okb else fail).append("plant/truncated-header-shape")

    print("\nC. A4 AND A5 -- a unique sentinel AT THE WRONG SITE still refuses")
    td2 = tempfile.mkdtemp(prefix="d6rf3_anchor2_")
    prod = open(os.path.join(HERE, STAGED_PRODUCER)).read()
    # move the (unique) anchor to the very top: count stays 1, header goes short
    moved = anchor + "\n" + prod.replace(anchor, "# model section", 1)
    open(os.path.join(td2, STAGED_PRODUCER), "w").write(moved)
    r2 = re.sub(r'PRODUCER_MD5 = "[0-9a-f]{32}"',
                'PRODUCER_MD5 = "%s"' % hashlib.md5(moved.encode()).hexdigest(),
                open(os.path.join(HERE, "d6rf3_fd_endpoint.py")).read())
    open(os.path.join(td2, "d6rf3_fd_endpoint.py"), "w").write(r2)
    check("count == 1 but the anchor is at the TOP -> REFUSES at A4",
          lambda: check_pair(os.path.join(td2, "d6rf3_fd_endpoint.py"), td2), True)

    print("\nD. A2 -- the pin, which is the clause the ruling did not anticipate")
    td3 = tempfile.mkdtemp(prefix="d6rf3_anchor3_")
    shutil.copy2(os.path.join(HERE, STAGED_PRODUCER), os.path.join(td3, STAGED_PRODUCER))
    shutil.copy2(os.path.join(HERE, "d6rf3_fd_endpoint.py"),
                 os.path.join(td3, "d6rf3_fd_endpoint.py"))
    with open(os.path.join(td3, STAGED_PRODUCER), "a") as fh:
        fh.write("\n# one byte of drift\n")
    check("the producer drifts by one comment -> REFUSES at A2 (the md5), "
          "BEFORE the anchor is ever counted",
          lambda: check_pair(os.path.join(td3, "d6rf3_fd_endpoint.py"), td3), True)
    td4 = tempfile.mkdtemp(prefix="d6rf3_anchor4_")
    shutil.copy2(os.path.join(HERE, "d6rf3_fd_endpoint.py"),
                 os.path.join(td4, "d6rf3_fd_endpoint.py"))
    check("the producer is ABSENT from the work dir -> REFUSES at A2",
          lambda: check_pair(os.path.join(td4, "d6rf3_fd_endpoint.py"), td4), True)

    print("\nD6RF3_ANCHOR_SELFTEST %d/%d PASS" % (len(ok), len(ok) + len(fail)))
    if fail:
        print("FAILED: %s" % ", ".join(fail))
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--work-dir", default=HERE)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    gate(a.work_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
