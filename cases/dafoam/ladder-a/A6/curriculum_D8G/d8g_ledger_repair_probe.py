#!/usr/bin/env python3
"""D8G LEDGER-REPAIR PROBE -- IT GRADES NOTHING AND IT IS NOT PART OF THE FROZEN SET.

WHAT IT IS FOR.  The supervisor's ruling on d8g_LEDGER_REFUSED_ROW_DEFECT.diff turns on
questions of the form "does repair X actually dissolve blocker Y".  Those are measurable,
and this file measures them so nobody has to reason about them.  It is the instrument
behind every number in D8G_2D1_REPAIR_EVIDENCE.md.

WHAT IT DOES NOT DO, AND THE LIST IS THE POINT:
  * it NEVER writes inside the run root.  Every copy it makes lives in a tempdir it
    creates and removes itself.
  * it NEVER modifies d8g_grade.py, d8g_run_arm.sh, ledger.txt or any other frozen file.
    It reads them, copies the bytes, and patches THE COPIES in memory.
  * it RETURNS NO VERDICT.  It prints, for each (reader variant, ledger variant) pair,
    what read_ledger() did -- parsed, or refused and on which branch.  It cannot know
    which direction a verdict wants, because it never reaches one.
  * it APPLIES NOTHING.  Running it changes no instrument and unblocks nothing.

THE READER VARIANTS.
  baseline  the frozen d8g_grade.py, byte-for-byte.
  A         the frozen reader, unchanged -- driven against a ledger written AS IF
            repair A (`REFUSED_ARM=` prefix, d8g_run_arm.sh:922) had been in force at
            write time.  Repair A is a PRODUCER-side change, so on the reader side there
            is nothing to patch: that is the whole finding about A.
  B         repair B of the diff, transcribed: REFUSED_LAUNCH_RE, the `continue`, the
            refused-launch-and-no-completed-row refusal, the `__refused_launches__` key.
  SKIP      the NAIVE repair nobody drafted -- skip any `ARM=` line carrying no `rc=`.
            It is here because it FAILS the planted control below, and a repair that
            fails a control is worth more on the record than one that is merely absent.
  ADMIT     a repair that READS the refused row as an arm row.  It is here because the
            diff's "second, independent blocker" claim is TRUE of this shape and of no
            other, and that distinction is the answer to the duplicate question.

THE PLANTED CONTROL (CLAUDE.md rule 3), AND IT IS WHY THIS FILE EXISTS RATHER THAN A
PARAGRAPH.  A reader that returns "no refusal" proves nothing until it is shown able to
refuse.  Every reader variant is therefore ALSO driven against a ledger whose WELL-FORMED
row has been corrupted by one token (`rc=` -> `rcX=`).  A variant that stays silent on
that ledger is a reader that cannot see a non-zero, and the probe says so by name.

USAGE:  python3 d8g_ledger_repair_probe.py [--ledger <path>] [--grader <path>]
        defaults: the D8G run root's ledger.txt and this directory's d8g_grade.py.
"""
import argparse
import importlib.util
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_GRADER = os.path.join(HERE, "d8g_grade.py")
DEFAULT_LEDGER = "/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple/ledger.txt"

ANCHOR = '''    rows = {}
    for line in open(path, errors="replace"):
        if not line.startswith("ARM="):
            continue
        m = LEDGER_RE.search(line)'''

B_PREAMBLE = '''REFUSED_LAUNCH_RE = re.compile(r"^ARM=(?P<ARM>\\S+)\\s+ROW=\\S+\\s+IMG=\\S+\\s+DIGEST=\\S+\\s+"
                               r"launched:\\s+false\\s+reason=\\[.*\\]\\s+launch_rc=(?P<launch_rc>-?\\d+)\\s")


def read_ledger'''

B_BODY = '''    rows = {}
    refused_launches = []
    for line in open(path, errors="replace"):
        if not line.startswith("ARM="):
            continue
        rl = REFUSED_LAUNCH_RE.match(line)
        if rl:
            refused_launches.append({"ARM": rl.group("ARM"),
                                     "launch_rc": int(rl.group("launch_rc")),
                                     "raw": line.strip()[:300]})
            continue
        m = LEDGER_RE.search(line)'''

B_TAIL_OLD = '''        rows[row["ARM"]] = row
    return rows'''

B_TAIL_NEW = '''        rows[row["ARM"]] = row
    for rl in refused_launches:
        if rl["ARM"] not in rows:
            refuse("ledger", {"refused_launch_and_no_completed_row": rl["ARM"],
                              "launch_rc": rl["launch_rc"], "raw": rl["raw"],
                              "note": "the solver's first artifact never appeared"})
    if refused_launches:
        rows["__refused_launches__"] = refused_launches
    return rows'''

SKIP_BODY = '''    rows = {}
    for line in open(path, errors="replace"):
        if not line.startswith("ARM="):
            continue
        if re.search(r"\\src=-?\\d+\\s", line) is None:
            continue
        m = LEDGER_RE.search(line)'''

ADMIT_BODY = '''    rows = {}
    for line in open(path, errors="replace"):
        if not line.startswith("ARM="):
            continue
        if " launched: false " in line:
            mm = re.match(r"ARM=(?P<ARM>\\S+)\\s", line)
            arm = mm.group("ARM")
            if arm in rows:
                refuse("ledger", {"duplicate_arm_row": arm, "note": "two records for one run is the defect"})
            rows[arm] = {"ARM": arm, "rc": 88, "source": "refused_launch_row"}
            continue
        m = LEDGER_RE.search(line)'''


def fail(msg):
    print("PROBE REFUSES: %s" % msg)
    sys.exit(2)


def reader_variants(src):
    if src.count(ANCHOR) != 1:
        fail("the frozen read_ledger() head is not where this probe expects it; the probe is "
             "stale against d8g_grade.py and MUST NOT be trusted until re-anchored")
    out = {"baseline": src, "A": src}
    b = src.replace("def read_ledger", B_PREAMBLE, 1).replace(ANCHOR, B_BODY, 1)
    if B_TAIL_OLD not in b:
        fail("read_ledger()'s tail is not where this probe expects it")
    out["B"] = b.replace(B_TAIL_OLD, B_TAIL_NEW, 1)
    out["SKIP"] = src.replace(ANCHOR, SKIP_BODY, 1)
    out["ADMIT"] = src.replace(ANCHOR, ADMIT_BODY, 1)
    for k, v in out.items():
        if k != "baseline" and k != "A" and v == src:
            fail("reader variant %s is byte-identical to the frozen reader: the patch did not apply" % k)
    return out


def ledger_variants(lines):
    refused = [i for i, l in enumerate(lines) if l.startswith("ARM=") and " launched: false " in l]
    good = [i for i, l in enumerate(lines) if l.startswith("ARM=") and " rc=" in l]
    if len(refused) != 1 or len(good) != 1:
        fail("this probe is written for the ledger that carries EXACTLY one refused-launch row and "
             "one completed row; found %d and %d" % (len(refused), len(good)))
    r, g = refused[0], good[0]
    out = {}
    out["real"] = list(lines)
    a = list(lines); a[r] = "REFUSED_" + a[r]
    out["A_applied"] = a
    p = list(lines); p[g] = p[g].replace(" rc=", " rcX=", 1)
    out["PLANT"] = p                                  # the rule-3 control
    ap = list(a); ap[g] = ap[g].replace(" rc=", " rcX=", 1)
    out["A_applied+PLANT"] = ap
    out["refused_only"] = [l for i, l in enumerate(lines) if i != g]
    out["A_applied+refused_only"] = [l for i, l in enumerate(a) if i != g]
    # ---- THE "FOURTH PATH": repair A, then a CLEAN re-run of the same arm --------------
    # A synthetic rc=0 row for the same arm, appended as a re-run into the SAME run root
    # would append it.  Two shapes, because they answer different questions:
    #   rerun_same_ledger   -- A landed TODAY, so line 3 still carries its `ARM=` prefix
    #   A_from_start+rerun  -- the BEST CASE: A had been in force when line 3 was written
    clean = (lines[g].replace(" rc=1 ", " rc=0 ", 1)
                     .replace("inspect(exit,oomkilled)=[1 false]", "inspect(exit,oomkilled)=[0 false]", 1)
                     .replace("stamp=", "rerun_stamp=", 1))
    if clean == lines[g]:
        fail("could not synthesise a clean re-run row from the completed row")
    out["rerun_same_ledger"] = list(lines) + [clean]
    out["A_from_start+rerun"] = list(a) + [clean]
    return out


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grader", default=DEFAULT_GRADER)
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    a = ap.parse_args()
    for p in (a.grader, a.ledger):
        if not os.path.isfile(p):
            fail("absent: %s" % p)
    src = open(a.grader).read()
    lines = open(a.ledger, errors="replace").read().split("\n")
    tmp = tempfile.mkdtemp(prefix="d8g_probe_")
    try:
        readers, ledgers = reader_variants(src), ledger_variants(lines)
        mods = {}
        for k, v in readers.items():
            fp = os.path.join(tmp, "r_%s.py" % k)
            open(fp, "w").write(v)
            mods[k] = load(fp, "d8g_probe_%s" % k)
        lpaths = {}
        for k, v in ledgers.items():
            fp = os.path.join(tmp, "l_%s.txt" % k.replace("+", "_"))
            open(fp, "w").write("\n".join(v))
            lpaths[k] = fp
        print("D8G LEDGER-REPAIR PROBE -- grades nothing, applies nothing, writes nothing outside %s" % tmp)
        print("grader: %s" % a.grader)
        print("ledger: %s" % a.ledger)
        print()
        print("%-9s %-26s %s" % ("READER", "LEDGER", "read_ledger() OUTCOME"))
        blind = []
        for rk in ("baseline", "A", "B", "SKIP", "ADMIT"):
            for lk in ("real", "A_applied", "PLANT", "A_applied+PLANT",
                       "refused_only", "A_applied+refused_only",
                       "rerun_same_ledger", "A_from_start+rerun"):
                # variant A IS the frozen reader; it is meaningful only on an A-written ledger
                if rk == "A" and not lk.startswith("A_"):
                    continue
                try:
                    rows = mods[rk].read_ledger(lpaths[lk])
                    det = "PARSED keys=%s" % sorted(rows.keys())
                    r1 = rows.get("L1-P")
                    if isinstance(r1, dict):
                        det += " L1-P.rc=%s" % r1.get("rc")
                    if lk.endswith("PLANT"):
                        blind.append((rk, lk))
                except mods[rk].Refusal as e:
                    d = json.loads(str(e))
                    det = "REFUSE %s :: %s" % (d["REFUSE"], ",".join(sorted(d["detail"].keys())))
                print("%-9s %-26s %s" % (rk, lk, det))
        # ---- WHAT THE GRADER DOES *NEXT*, once the ledger stops being the blocker ------
        # This is the load-bearing measurement and it is why the probe reaches past
        # read_ledger().  g_completion() only READS the run root (open/getmtime); it writes
        # nothing.  If it refuses, the ledger repair bought a different refusal, not a grade.
        root = os.path.dirname(os.path.abspath(a.ledger))
        print("%-9s %-26s %s" % ("READER", "LEDGER", "NEXT STOP -- g_completion() on the real run root"))
        for rk, lk in (("baseline", "A_applied"), ("B", "real"), ("B", "A_applied")):
            try:
                rows = mods[rk].read_ledger(lpaths[lk])
            except mods[rk].Refusal:
                print("%-9s %-26s (never reached: the ledger itself refused)" % (rk, lk))
                continue
            try:
                mods[rk].g_completion(root, rows)
                print("%-9s %-26s g_completion PASSED -- grading proceeds" % (rk, lk))
            except mods[rk].Refusal as e:
                d = json.loads(str(e))
                print("%-9s %-26s REFUSE %s :: %s" % (rk, lk, d["REFUSE"], json.dumps(d["detail"], sort_keys=True)[:160]))
        print()
        if blind:
            print("RULE-3 CONTROL FAILED for: %s" % ", ".join("%s on %s" % b for b in blind))
            print("  Those readers stayed silent on a ledger whose WELL-FORMED row was corrupted by one")
            print("  token.  A reader not shown able to see a non-zero is not evidence.")
        else:
            print("RULE-3 CONTROL PASSED for every reader variant driven against it: each refused the")
            print("  one-token-corrupted well-formed row, so none of their silences elsewhere is a")
            print("  reader that accepts anything.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
