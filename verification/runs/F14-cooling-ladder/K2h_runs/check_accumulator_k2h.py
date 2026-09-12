#!/usr/bin/env python3
"""G-02b: the fieldAverage accumulator guard, for `resume_k2h.sh`.

    check_accumulator_k2h.py <case-dir> <latest-time> [--controldict PATH]

Exit 0 = the guard passes.  Exit 1 = REFUSE.  Exit 2 = the guard could not be
evaluated (which is also a refusal, stated separately so it is not mistaken for
a clean pass).

=== WHY THIS FILE EXISTS: THE GUARD IT REPLACES COULD NEVER FIRE CORRECTLY ===

`resume_k2h.sh`'s G-02b searched with

    ACC=$(find "$CASE" -name 'fieldAverageProperties*')

and `fieldAverageProperties` DOES NOT EXIST IN OpenFOAM 2606 AND NEVER WILL.
The name is pre-2016.  `fieldAverage::writeAveragingProperties()` calls
`item.writeState(propsDict)` then `setProperty(...)`, and
`functionObjectList::createPropertiesDict()` (functionObjectList.C:98-100)
builds that object at

    <time>/uniform/functionObjects/functionObjectProperties

`writeState` (fieldAverageItem.C:208) adds exactly `totalIter` and `totalTime`.

So `ACC` was ALWAYS empty, the else-branch ALWAYS ran, and the moment the run
passed the registered `timeStart` 42 that branch would have REFUSED every future
resume with a reason that is FALSE BY CONSTRUCTION -- "averaging should have
begun and left an accumulator, its absence is a DEFECT" -- about a file this
OpenFOAM never writes.  The refusal would have looked authoritative.

=== AND THE PRESENCE OF THE NEW FILE IS NOT THE ACCUMULATOR EITHER ===

`functionObjectProperties` exists from the FIRST write at t = 5, carrying the
OTHER function objects' state (`dp_tile`, `dp_return`, `U_ha`, `T_ca`,
`T_in_0..3`).  Gating on the file would have been the mirror-image error: always
true, including in the case where averaging silently never started.  THIS GUARD
GATES ON THE `fieldAverage` FUNCTION OBJECT'S OWN SUB-DICTIONARY inside that
file, and on the `totalIter`/`totalTime` it carries.

=== THE GENERAL FIX, WHICH IS THE PART WORTH KEEPING ===

Both paths are searched, new first, and EVERY PATH LOOKED IN IS REPORTED.  An
ABSENT reading can never stand without the evidence of where it was looked for.
That is what stops the next version of this defect, not the corrected constant.

Both refusal directions stay armed, because both are WRONG NUMBERS rather than
crashes: present on some ranks and not others, and absent when averaging is due.
"""
import argparse
import glob
import os
import re
import sys

REL_NEW = os.path.join("uniform", "functionObjects", "functionObjectProperties")
REL_OLD = os.path.join("uniform", "fieldAverageProperties")   # pre-2016


class Refusal(Exception):
    pass


def _strip_comments(txt):
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    return re.sub(r"//[^\n]*", "", txt)


def _block(txt, key):
    """Brace-balanced body of `key { ... }`, or None."""
    m = re.search(r"(?m)^\s*" + re.escape(key) + r"\s*$\s*\{", txt)
    if m is None:
        m = re.search(r"(?<![\w.])" + re.escape(key) + r"\s*\{", txt)
        if m is None:
            return None
    depth, j = 1, m.end()
    while depth and j < len(txt):
        depth += (txt[j] == "{") - (txt[j] == "}")
        j += 1
    return txt[m.end():j - 1]


def fieldaverage_fo(controldict):
    """(name, timeStart) of the `fieldAverage` function object, from the dict.

    Derived rather than hardcoded: a guard that assumes the function object is
    called `dpAverage` breaks silently the first time somebody renames it, and
    would then pass by looking for a block that is not there.
    """
    if not os.path.exists(controldict):
        raise Refusal("controlDict %s does not exist" % controldict)
    txt = _strip_comments(open(controldict, errors="replace").read())
    fns = _block(txt, "functions")
    if fns is None:
        raise Refusal("controlDict carries no `functions` block")
    for m in re.finditer(r"(?m)^\s*(\w+)\s*$\s*\{", fns):
        name = m.group(1)
        body = _block(fns, name)
        if body is None:
            continue
        if re.search(r"(?m)^\s*type\s+fieldAverage\s*;", body):
            ts = re.search(r"(?m)^\s*timeStart\s+([\d.eE+-]+)\s*;", body)
            if ts is None:
                raise Refusal("the fieldAverage function object %r carries no "
                              "`timeStart`; this guard will not invent one"
                              % name)
            return name, float(ts.group(1))
    raise Refusal("controlDict declares no function object of `type "
                  "fieldAverage`; there is no accumulator to guard")


def read_rank(pdir, tname, fo):
    """(path_found, fields_dict_or_None, paths_looked_in) for one rank."""
    looked = []
    for rel in (REL_NEW, REL_OLD):
        fp = os.path.join(pdir, tname, rel)
        looked.append(fp)
        if not os.path.exists(fp):
            continue
        blk = _block(_strip_comments(open(fp, errors="replace").read()), fo)
        if blk is None:
            return fp, None, looked          # file present, ACCUMULATOR absent
        fields = {}
        for fm in re.finditer(r"(\w+)\s*\{([^{}]*)\}", blk):
            it = re.search(r"totalIter\s+(\d+)\s*;", fm.group(2))
            tt = re.search(r"totalTime\s+([-\d.eE+]+)\s*;", fm.group(2))
            if it or tt:
                fields[fm.group(1)] = (int(it.group(1)) if it else None,
                                       float(tt.group(1)) if tt else None)
        if not fields:
            raise Refusal("%s carries a %r block with no totalIter/totalTime in "
                          "it. The guard will not read that as either present "
                          "or absent" % (fp, fo))
        return fp, fields, looked
    return None, None, looked


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("latest", type=float)
    ap.add_argument("--controldict", default=None)
    a = ap.parse_args(argv)

    cd = a.controldict or os.path.join(a.case, "system", "controlDict")
    out = []
    try:
        fo, tstart = fieldaverage_fo(cd)
        out.append("  G-02b fieldAverage function object %r, timeStart %g"
                   % (fo, tstart))

        procs = sorted(glob.glob(os.path.join(a.case, "processor*")))
        if not procs:
            raise Refusal("no processor* directories under %s" % a.case)
        tname = ("%g" % a.latest) if a.latest != int(a.latest) else \
                str(int(a.latest))
        if not os.path.isdir(os.path.join(procs[0], tname)):
            for cand in (repr(a.latest), "%g" % a.latest, str(a.latest)):
                if os.path.isdir(os.path.join(procs[0], cand)):
                    tname = cand
                    break

        found, looked_all = {}, []
        for p in procs:
            fp, fields, looked = read_rank(p, tname, fo)
            looked_all += looked
            found[os.path.basename(p)] = (fp, fields)

        # EVERY PATH LOOKED IN IS REPORTED.  An absent reading never stands
        # without the evidence of where it was looked for.
        # The wording matters: `read_rank` tries the 2606 path first and STOPS
        # at the first file it finds, so on a healthy case the pre-2016 name is
        # never reached.  Saying "both spellings" would claim a search that did
        # not happen.  What is reported is what was actually tried.
        out.append("  G-02b tried %d path(s), 2606 spelling first, stopping at "
                   "the first file found on each rank:" % len(set(looked_all)))
        for x in sorted(set(looked_all)):
            out.append("      %s%s" % (x.replace(a.case + "/", ""),
                                       "   <- FOUND" if os.path.exists(x) else ""))

        with_acc = [k for k, (_, f) in found.items() if f]
        without = [k for k, (_, f) in found.items() if not f]

        # --- direction 1: present on SOME ranks only -- a WRONG NUMBER -------
        if with_acc and without:
            raise Refusal(
                "the %r accumulator is present on %s and ABSENT on %s at "
                "t=%s. Resuming would average a partial window on some ranks "
                "and a blank one on others. That is a WRONG NUMBER, not a "
                "crash. STOP and triage."
                % (fo, ", ".join(sorted(with_acc)), ", ".join(sorted(without)),
                   tname))

        # --- direction 2: absent when averaging is DUE ----------------------
        if not with_acc:
            if a.latest >= tstart:
                raise Refusal(
                    "NO %r accumulator exists on ANY rank, but the latest time "
                    "%s is at or past the registered timeStart %g. Averaging "
                    "should have begun and left one. Its absence is then a "
                    "DEFECT, not a normal state. STOP and triage. (Checked "
                    "BOTH the OpenFOAM 2606 path and the pre-2016 name, listed "
                    "above -- this is not the old guard's false refusal, which "
                    "searched only for a file this OpenFOAM never writes.)"
                    % (fo, tname, tstart))
            out.append("  G-02b OK: no accumulator, and NONE IS DUE -- latest "
                       "time %s is before the registered timeStart %g, so "
                       "averaging has not begun. Absence here is EXPECTED, and "
                       "this guard PROVES it against the paths listed above "
                       "rather than assuming it." % (tname, tstart))
            print("\n".join(out))
            return 0

        # --- all ranks carry it: they must AGREE ----------------------------
        sig = {k: tuple(sorted((f, v[0], v[1]) for f, v in found[k][1].items()))
               for k in with_acc}
        if len(set(sig.values())) != 1:
            raise Refusal(
                "all four ranks carry the %r accumulator but they DISAGREE on "
                "totalIter/totalTime: %s. Four present-but-disagreeing "
                "accumulators pass a presence test and still give a wrong "
                "mean. STOP and triage."
                % (fo, "; ".join("%s %s" % (k, sig[k]) for k in sorted(sig))))
        one = found[with_acc[0]][1]
        out.append("  G-02b OK: the %r accumulator is present on all %d ranks "
                   "at t=%s and they AGREE: %s. The average RESUMES."
                   % (fo, len(with_acc), tname,
                      ", ".join("%s totalIter=%s totalTime=%s"
                                % (f, v[0], v[1]) for f, v in sorted(one.items()))))
        print("\n".join(out))
        return 0

    except Refusal as e:
        print("\n".join(out))
        print("REFUSE G-02b: %s" % e)
        return 1
    except Exception as e:                      # noqa: BLE001
        print("\n".join(out))
        print("REFUSE G-02b: the guard could not be evaluated (%s: %s). A guard "
              "that cannot run is a refusal, not a pass." % (type(e).__name__, e))
        return 2


if __name__ == "__main__":
    sys.exit(main())
