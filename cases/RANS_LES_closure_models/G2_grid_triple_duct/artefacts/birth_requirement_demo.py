# BIRTH-REQUIREMENT DEMONSTRATION (Sanaa's directive 2026-08-28T1701Z).
# Reads the FROZEN comparator's OWN parse_log -- unmodified, imported, not
# reimplemented -- over REAL OpenFOAM logs written by the REAL producer, and
# reports whether it has been shown to return a non-zero the way reality
# delivers one. It GRADES NOTHING: no functional, no order, no GCI, no verdict.
# It EDITS NOTHING: the frozen comparator is imported read-only.
import importlib.util, re, sys
from pathlib import Path
BANNER = "trapFpe: Floating point exception trapping enabled"
def load(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def demo(mod, logs):
    pos, neg, refused, nb, nbe = [], 0, 0, 0, 0
    for p in logs:
        try:
            o = mod.parse_log(p)
        except Exception:
            refused += 1; continue
        t = p.read_text(errors="replace")
        if o["fatal"]:
            pos.append((p, mod.FATAL_RE.search(t).group(0).strip(),
                        bool(re.search(r"(?m)^End\s*$", t))))
        else:
            neg += 1
            if BANNER in t:
                nb += 1
                if re.search(r"(?m)^End\s*$", t): nbe += 1
    return pos, neg, refused, nb, nbe
if __name__ == "__main__":
    logs = [Path(l.strip()) for l in open(sys.argv[2]) if Path(l.strip()).is_file()]
    mod = load("frozen", sys.argv[1])
    pos, neg, refused, nb, nbe = demo(mod, logs)
    print("comparator      : %s" % sys.argv[1])
    print("real logs read  : %d   fatal=True %d   fatal=False %d   refused %d"
          % (len(logs), len(pos), neg, refused))
    print("NEGATIVE DIRECTION on real artifacts: %d carry the trapFpe banner and read "
          "NOT-fatal (%d of them with a clean End)" % (nb, nbe))
    print("POSITIVE DIRECTION, signatures that fired:")
    from collections import Counter
    c = Counter(s for _p, s, _e in pos)
    for s, n in c.most_common(): print("   %-34s %d" % (s[:34], n))
    print("of the positives, %d of %d lack a clean End (they really died)"
          % (sum(1 for _p, _s, e in pos if not e), len(pos)))
