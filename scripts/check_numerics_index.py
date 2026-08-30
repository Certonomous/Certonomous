"""NUMERICS_KNOWLEDGE FAMILY INDEX: derive it from the tail, never maintain it by hand.

THE LOCATOR IS THE FILE'S OWN, quoted from docs/NUMERICS_KNOWLEDGE.md's index block:
    grep -nE '^(## |\\*\\*)N-AV[0-9]' docs/NUMERICS_KNOWLEDGE.md
Using a fresh regex instead of the file's own is how this supervisor first measured
41 entries against a true 124 -- the instrument answered a different question than
the one asked (MONITOR_STANDARD v1.13).
"""
import re, collections, sys

F = "docs/NUMERICS_KNOWLEDGE.md"
LOC = re.compile(r'^(?:## |\*\*)(N-([A-Z]+)([0-9]+))')

DESC = {
    "AV": "Ansys Fluid Dynamics Verification Manual — VMFL cases reproduced in the lab's own solvers as pre-registered verdicts",
    "B":  "Closure line (RANS/LES): β-field correction, feature-library, clip-repair and injection numerics",
    "C":  "General CFD meshing: snappyHexMesh / grid-family facts (a LEVEL step is not a grid refinement)",
    "D":  "DAFoam adjoint & optimisation: primal/adjoint solver behaviour, gradient verification, optimiser and cost numerics",
    "K":  "Data-driven closure benchmark numerics: Pope tensor-basis rank, TBNN / SpaRTA conditioning",
    "T":  "T-family heat-transfer ladder: GCI / Richardson, thermal grid-convergence numerics",
    "X":  "Cross-cutting V&V numerics: estimators and tolerances general to verification",
}


def tail_ids(path=F):
    """Distinct ids per family, from the tail, by the file's OWN locator."""
    seen = collections.OrderedDict()
    for ln in open(path, encoding="utf-8").read().splitlines():
        m = LOC.match(ln)
        if m:
            seen.setdefault(m.group(1), 0)
            seen[m.group(1)] += 1
    fam = collections.defaultdict(set)
    for i in seen:
        m = re.match(r'N-([A-Z]+)([0-9]+)$', i)
        fam[m.group(1)].add(int(m.group(2)))
    return dict(fam), seen


def index_ids(path=F):
    """Ids per family as listed by the NEWEST FAMILY INDEX block (it supersedes)."""
    txt = open(path, encoding="utf-8").read()
    starts = [m.start() for m in re.finditer(r'(?m)^## FAMILY INDEX', txt)]
    if not starts:
        return None
    newest = txt[starts[-1]:]
    fam = collections.defaultdict(set)
    for line in newest.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        m = re.match(r'^(N-[A-Z]+)$', cells[0])
        if not m:
            continue
        f = m.group(1)[2:]
        for n in re.findall(r'N-[A-Z]+([0-9]+)', cells[-1]):
            fam[f].add(int(n))
    return dict(fam)


def divergence(path=F):
    t, _ = tail_ids(path)
    i = index_ids(path)
    if i is None:
        return [("*", [], [], "no FAMILY INDEX block exists")]
    out = []
    for k in sorted(set(t) | set(i)):
        a, b = t.get(k, set()), i.get(k, set())
        if a != b:
            out.append((k, sorted(a - b), sorted(b - a), ""))
    return out


def render(path=F):
    t, _ = tail_ids(path)
    rows = []
    for k in sorted(t):
        ids = ", ".join("N-%s%d" % (k, n) for n in sorted(t[k]))
        rows.append("| N-%s | %s | %s |" % (k, DESC.get(k, "(description owed by the owning team)"), ids))
    total = sum(len(v) for v in t.values())
    return rows, len(t), total


# ---------------------------------------------------------------- selftest
def _selftest():
    """Planted controls. C3 is the one that matters and it is born from a real
    error: this supervisor's first parser returned ZERO families from the index
    and therefore reported EVERY family as diverging -- a dramatic result caused
    by a broken instrument, not a bad tree. A zero from a parser not shown able
    to see a non-zero is not evidence (standing rule 3), so the parser must
    REFUSE rather than report total divergence."""
    import tempfile, os
    bad = 0
    d = tempfile.mkdtemp(prefix="nkidx_")

    def write(name, body):
        p = os.path.join(d, name)
        open(p, "w", encoding="utf-8").write(body)
        return p

    TAIL = "## N-C1. one\n\ntext\n\n## N-C2. two\n\ntext\n\n## N-Q1. q\n\ntext\n"
    IDX_OK = ("\n## FAMILY INDEX — regenerated\n\n"
              "| fam | desc | ids |\n|---|---|---|\n"
              "| N-C | d | N-C1, N-C2 |\n| N-Q | d | N-Q1 |\n")
    IDX_STALE = ("\n## FAMILY INDEX — regenerated\n\n"
                 "| fam | desc | ids |\n|---|---|---|\n"
                 "| N-C | d | N-C1 |\n| N-Q | d | N-Q1 |\n")

    p = write("ok.md", TAIL + IDX_OK)
    if divergence(p):
        print("  FAIL  C2 (-) an index that AGREES was reported as diverging"); bad += 1
    else:
        print("  ok    C2 (-) index agrees with tail -> SILENT")

    p = write("stale.md", TAIL + IDX_STALE)
    dv = divergence(p)
    if [(k, m) for k, m, _, _ in dv] == [("C", [2])]:
        print("  ok    C1 (+) a missing id FIRES, and names exactly N-C2")
    else:
        print("  FAIL  C1 (+) wanted exactly N-C2 missing, got %r" % (dv,)); bad += 1

    p = write("noidx.md", TAIL)
    dv = divergence(p)
    if dv and dv[0][0] == "*":
        print("  ok    C3 (+) NO index block -> REFUSES, does not report total divergence")
    else:
        print("  FAIL  C3 (+) a missing index block must refuse, got %r" % (dv,)); bad += 1

    p = write("blindidx.md", TAIL + "\n## FAMILY INDEX — regenerated\n\n(no table at all)\n")
    ix = index_ids(p)
    if not ix:
        print("  ok    C4 (+) an index the parser cannot read yields NO families -- "
              "callers must treat this as PARSER BLINDNESS, never as divergence")
    else:
        print("  FAIL  C4 (+) expected an unreadable index to parse empty, got %r" % (ix,)); bad += 1

    import shutil; shutil.rmtree(d, ignore_errors=True)
    print("SELFTEST %s (%d failure(s))" % ("PASS" if not bad else "FAIL", bad))
    return bad


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(1 if _selftest() else 0)
    if "--gen" in sys.argv:
        rows, nf, tot = render()
        print("\n".join(rows))
        print("\nFAMILIES %d TOTAL %d" % (nf, tot))
    else:
        d = divergence()
        print("DIVERGENCE" if d else "INDEX AGREES WITH TAIL")
        for k, miss, extra, note in d:
            print("  N-%s: missing from index %s | in index not in tail %s %s"
                  % (k, ["N-%s%d" % (k, x) for x in miss],
                     ["N-%s%d" % (k, x) for x in extra], note))

