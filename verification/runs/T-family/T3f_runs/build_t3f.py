#!/usr/bin/env python3
"""build_t3f.py -- build R_fy, the T3e continuation of R_fx.

REGISTERED BY docs/campaigns/T-family/T3f_PREREGISTRATION.md.

WHY THIS FILE EXISTS AT ALL -- DEFECT D-1.
T3d's build_t3d.py:89 wrote CASE.txt as SIX LINES OF PROSE with no key-value
pairs.  T3d's grader, analyse_t3.py:461-468, reads seven numeric keys from that
same file.  Both were sha-pinned in the SAME frozen registration and both were
byte-identical to their pins: nothing drifted, and the pair could never have
satisfied each other.  4,723.200 core-minutes were spent on a run no outcome of
which could have been graded.

THIS BUILDER'S CONTRACT (T3f_PREREGISTRATION.md section 7.2): R_fy/CASE.txt
carries the FULL STRUCTURED KEY-VALUE BLOCK.  Every inherited constant is COPIED
FROM R_ff/CASE.txt BY KEY and never retyped -- a retyped constant is a second
source of truth.  The prose header may be appended BELOW the block; it may not
replace it.

Standing rule 14: KEYS_INHERITED is asserted against a baseline at every call
site, never silently replaced.
Exit 0 built, 2 refusal.  Zero bare `assert` (L-332).
"""
import os
import shutil
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
T3 = os.path.normpath(os.path.join(HERE, "..", "T3_runs"))

SRC_CASE = "R_fy"          # the completed predecessor
SRC_TIME = "8000"         # its endTime, reconstructed
DST_CASE = "R_fz"
KEY_DONOR = "R_ff"         # carries the structured block; same mesh as R_fx

ADDITIONAL_ITERATIONS = 8000
WRITE_INTERVAL = 2000
PURGE_WRITE = 0            # D-3's repair: KEEP EVERY CHECKPOINT

# The seven keys analyse_t3.py:461-468 reads, plus the ones this rung's own
# grader reads.  THIS LIST IS THE CONTRACT WITH THE GRADER.
KEYS_INHERITED = ("H", "nu", "Pr", "Prt", "dTdn_wall", "T_in", "U_in")
KEYS_BASELINE = ("H", "nu", "Pr", "Prt", "dTdn_wall", "T_in", "U_in")

FIELDS = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega", "phi")


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(2)


def keys_intact_or_refuse():
    """STANDING RULE 14, AT EVERY CALL SITE.  KEYS_INHERITED is the grader's
    contract; if an entry is REMOVED rather than added, the builder would write
    a CASE.txt the grader cannot read -- which is D-1 exactly."""
    for k in KEYS_BASELINE:
        if k not in KEYS_INHERITED:
            refuse("standing rule 14: key %r was REMOVED from KEYS_INHERITED. "
                   "The grader reads it; a CASE.txt without it reproduces D-1. "
                   "Keys are INSERTED, never replaced." % k)


def read_keyed(path):
    """Parse a structured CASE.txt into {key: first_token}.  Blank lines,
    comment lines and prose lines without a second token are skipped."""
    if not os.path.isfile(path):
        refuse("no key donor at %s" % path)
    out = {}
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("="):
            continue
        parts = s.split()
        if len(parts) >= 2:
            out.setdefault(parts[0], parts[1])
    return out


def main():
    keys_intact_or_refuse()                      # RULE 14 -- CALL SITE 1 of 2
    src = os.path.join(T3, SRC_CASE)
    dst = os.path.join(T3, DST_CASE)
    donor = os.path.join(T3, KEY_DONOR, "CASE.txt")

    if not os.path.isdir(src):
        refuse("%s does not exist; nothing to continue from" % src)
    seed = os.path.join(src, SRC_TIME)
    if not os.path.isdir(seed):
        refuse("%s does not exist; the predecessor's endTime fields are the "
               "seed and they are not on disk" % seed)

    # THE AGE-GUARD PRECONDITION (rule 4): refuse a case that already holds an
    # answer.  A rebuilt case over an old one is L-143's contamination.
    if os.path.isdir(dst):
        for name in os.listdir(dst):
            if name == "0" or (name.replace(".", "", 1).isdigit() and name != "0.orig"):
                refuse("%s already holds %r -- a time directory or 0/. A run is "
                       "never built into a tree that already carries an answer."
                       % (dst, name))

    kv = read_keyed(donor)
    missing = [k for k in KEYS_INHERITED if k not in kv]
    if missing:
        refuse("key donor %s carries no %s -- the inherited constants cannot be "
               "copied BY KEY and this builder will not retype them"
               % (donor, ", ".join(missing)))

    os.makedirs(dst, exist_ok=True)
    for sub in ("constant", "system"):
        s = os.path.join(src, sub)
        if not os.path.isdir(s):
            refuse("%s missing from the predecessor" % s)
        d = os.path.join(dst, sub)
        if os.path.isdir(d):
            shutil.rmtree(d)
        shutil.copytree(s, d)

    # seed 0.orig/ -- NOT 0/. The registered launcher creates 0 from 0.orig and
    # touches 0/T LAST, so that mtime dates the run allowed to produce the answer
    # (rule 4 clause 6, L-143). A builder that writes 0/ directly hands the age
    # guard a COPIED mtime and defeats it. Found by the section 2ap rehearsal.
    zero = os.path.join(dst, "0.orig")
    os.makedirs(zero, exist_ok=True)
    seeded = []
    for f in FIELDS:
        p = os.path.join(seed, f)
        if os.path.isfile(p):
            shutil.copy2(p, os.path.join(zero, f))
            seeded.append(f)
    if "T" not in seeded:
        refuse("no T in %s; 0.orig/T seeds 0/T, the age-guard datum" % seed)

    # controlDict: endTime, writeInterval AND purgeWrite, each rewrite VERIFIED
    cdp = os.path.join(dst, "system", "controlDict")
    cd = open(cdp).read()
    import re
    for key, val in (("endTime", ADDITIONAL_ITERATIONS),
                     ("writeInterval", WRITE_INTERVAL),
                     ("purgeWrite", PURGE_WRITE)):
        cd2 = re.sub(r"(?m)^%s\s+\S+\s*;\s*$" % key, "%-15s %d;" % (key, val), cd)
        if not re.search(r"(?m)^%s\s+%d\s*;\s*$" % (key, val), cd2):
            refuse("controlDict rewrite of %s to %d did not take; refusing "
                   "rather than running under the predecessor's setting"
                   % (key, val))
        cd = cd2
    open(cdp, "w").write(cd)

    keys_intact_or_refuse()                      # RULE 14 -- CALL SITE 2 of 2

    # THE STRUCTURED BLOCK.  This is D-1's repair and it is the whole point.
    lines = ["case              %s" % DST_CASE,
             "rung              T3f (heated backward-facing step, continuation of %s)" % SRC_CASE,
             "level             fy",
             "arm               continuation"]
    for k in KEYS_INHERITED:
        lines.append("%-17s %s" % (k, kv[k]))
    lines += ["endTime           %d" % ADDITIONAL_ITERATIONS,
              "writeInterval     %d" % WRITE_INTERVAL,
              "purgeWrite        %d" % PURGE_WRITE,
              "seeded_from       %s/%s" % (SRC_CASE, SRC_TIME),
              "key_donor         %s/CASE.txt" % KEY_DONOR,
              "registration      docs/campaigns/T-family/T3f_PREREGISTRATION.md",
              "",
              "# --- prose, APPENDED BELOW the block and not replacing it (D-1) ---",
              "# mesh IDENTICAL to R_ff and R_fx; this is NOT a new ladder level.",
              "# endTime is ADDITIONAL iterations; the counter restarts at 0.",
              "# purgeWrite 0 keeps every checkpoint: three consecutive pairs, D-3.",
              ""]
    open(os.path.join(dst, "CASE.txt"), "w").write("\n".join(lines))

    print("built %s" % dst)
    print("  seeded 0.orig/ from %s/%s: %s" % (SRC_CASE, SRC_TIME, " ".join(seeded)))
    print("  CASE.txt carries %d inherited keys copied BY KEY from %s"
          % (len(KEYS_INHERITED), KEY_DONOR))
    print("  endTime %d, writeInterval %d, purgeWrite %d (all three verified)"
          % (ADDITIONAL_ITERATIONS, WRITE_INTERVAL, PURGE_WRITE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
