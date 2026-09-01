#!/usr/bin/env python3
"""A2-B2R pin census -- pins_exist == pins_driven, by ROLE.

WHY THIS EXISTS.  SO-2MR lost its first arm to md5 pins that were STALE THE
INSTANT a mechanical rename ran, because the rename rewrote the very bytes the
pins pinned.  A pin table is not evidence unless something reads it back off
disk and refuses.  This does that, and it separates two roles that are secured
by two different mechanisms rather than pretending one census covers both:

  role `instrument`   -- the files the SOLVER consumes: the frozen A2 driver,
                         this rung's row spec, the surface-geometry tarball.
                         These are secured AT RUN TIME: run_a2b2r.sh asserts
                         each one's hash before it stages anything.  For this
                         role the census demands pins_exist == pins_driven:
                         every pinned instrument must have its hash asserted by
                         a literal inside the launcher, and every hash literal
                         in the launcher must belong to a pinned instrument.
  role `grading-path` -- the files that decide the VERDICT: the age guard, the
                         comparator, the launcher, this census.  Nothing asserts
                         these at run time and nothing could without circularity;
                         they are secured by the FREEZE COMMIT.  For this role
                         the census compares the document's pin against the
                         file on disk AND against the committed git blob.

Refusals are named, and exit 2:
    REFUSE_PIN_FILE_MISSING     a pinned path is not on disk
    REFUSE_PIN_STALE            document pin != file on disk
    REFUSE_PIN_NOT_DRIVEN       an `instrument` pin no code asserts
    REFUSE_LITERAL_UNPINNED     a hash literal in the launcher pins nothing
    REFUSE_PIN_NOT_COMMITTED    a `grading-path` file differs from its git blob
    REFUSE_NO_PINS              the pin table could not be read at all
"""
import hashlib
import os
import re
import subprocess
import sys

REPO = "/home/ubuntu/Certonomous"
DOC = os.path.join(REPO, "cases/dafoam/A2_B2R_INDEPENDENT_TRIM_PREREGISTRATION.md")
LAUNCHER = os.path.join(REPO, "cases/dafoam/run_a2b2r.sh")

ROW = re.compile(r"^\|\s*`?(instrument|grading-path)`?\s*\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{32})`"
                 r"\s*\|\s*`([0-9a-f]{64})`\s*\|")
HEX32 = re.compile(r"\b[0-9a-f]{32}\b")
HEX64 = re.compile(r"\b[0-9a-f]{64}\b")


def _h(path, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def refuse(tok, det):
    print("%s %s" % (tok, det))
    sys.exit(2)


def read_pins(doc=DOC):
    pins = []
    for line in open(doc, encoding="utf-8"):
        m = ROW.match(line.strip())
        if m:
            pins.append(dict(role=m.group(1), path=m.group(2), md5=m.group(3), sha256=m.group(4)))
    if not pins:
        refuse("REFUSE_NO_PINS", doc)
    return pins


def main(check_git=True):
    pins = read_pins()
    launcher_src = open(LAUNCHER, encoding="utf-8").read()
    lits = set(HEX32.findall(launcher_src)) | set(HEX64.findall(launcher_src))

    print("A2-B2R PIN CENSUS")
    print("%-13s %-46s %-8s %-8s %s" % ("role", "path", "md5", "sha256", "driven/committed"))
    by_role = {}
    driven = set()
    for p in pins:
        ap = p["path"] if os.path.isabs(p["path"]) else os.path.join(REPO, p["path"])
        if not os.path.isfile(ap):
            refuse("REFUSE_PIN_FILE_MISSING", p["path"])
        got5, got256 = _h(ap, "md5"), _h(ap, "sha256")
        if got5 != p["md5"]:
            refuse("REFUSE_PIN_STALE", "%s md5 %s != %s" % (p["path"], p["md5"], got5))
        if got256 != p["sha256"]:
            refuse("REFUSE_PIN_STALE", "%s sha256 %s != %s" % (p["path"], p["sha256"], got256))
        note = ""
        if p["role"] == "instrument":
            hit = (p["md5"] in lits) or (p["sha256"] in lits)
            if not hit:
                refuse("REFUSE_PIN_NOT_DRIVEN",
                       "%s: no hash literal in run_a2b2r.sh asserts it" % p["path"])
            driven.add(p["sha256"] if p["sha256"] in lits else p["md5"])
            note = "asserted in run_a2b2r.sh"
        else:
            if check_git:
                blob = subprocess.run(["git", "-C", REPO, "hash-object", ap],
                                      capture_output=True, text=True).stdout.strip()
                head = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD:" + p["path"]],
                                      capture_output=True, text=True)
                if head.returncode != 0:
                    note = "NOT YET COMMITTED (pre-freeze)"
                elif head.stdout.strip() != blob:
                    refuse("REFUSE_PIN_NOT_COMMITTED",
                           "%s disk blob %s != HEAD blob %s"
                           % (p["path"], blob[:12], head.stdout.strip()[:12]))
                else:
                    note = "blob %s == HEAD" % blob[:12]
            else:
                note = "git leg skipped"
        by_role.setdefault(p["role"], []).append(p["path"])
        print("%-13s %-46s %-8s %-8s %s" % (p["role"], p["path"], got5[:8], got256[:8], note))

    # every hash literal in the launcher must belong to a pin: a literal that
    # pins nothing is exactly the SO-3aR shape -- a citation with no referent.
    pinned_hashes = {p["md5"] for p in pins} | {p["sha256"] for p in pins}
    orphan = sorted(l for l in lits if l not in pinned_hashes)
    if orphan:
        refuse("REFUSE_LITERAL_UNPINNED", ",".join(x[:12] for x in orphan))

    n_inst = len(by_role.get("instrument", []))
    print("\nBY-ROLE CENSUS")
    print("  instrument     pins_exist=%d  pins_driven=%d  -> %s"
          % (n_inst, len(driven), "EQUAL" if n_inst == len(driven) else "NOT EQUAL"))
    print("  grading-path   pins_exist=%d  (secured by the freeze commit, not by a runtime assert)"
          % len(by_role.get("grading-path", [])))
    print("  launcher hash literals=%d, all of them pinned" % len(lits))
    if n_inst != len(driven):
        refuse("REFUSE_PIN_NOT_DRIVEN", "instrument census not equal")
    print("\nPIN_CENSUS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(check_git="--no-git" not in sys.argv))
