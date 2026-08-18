#!/usr/bin/env python3
"""mutate_advective.py -- can the repaired advective term FAIL?

    python3 mutate_advective.py [--json out.json]

WHY THIS EXISTS
---------------
KV1a shows the advective term recovers a planted source.  That is not enough.
A quantity that is computed, is quoted, and CANNOT COME OUT WRONG is exactly
the defect this rung was opened to repair, wearing a different name: the
sealed-case heat balance closes whether the physics is right or not (K0b, W-2),
and a new term that closes whatever it is set to would be the same failure
again.  So the question here is not "does it close" but "can it fail".

WHAT IT DOES
------------
Each mutation is a single textual substitution applied to a COPY of
`scripts/heat_balance.py`.  The copy is placed at `<tmp>/scripts/heat_balance.py`
with `<tmp>/docs/physics_rules.yaml` symlinked to the real one, because the
auditor resolves its governed thresholds relative to its own `__file__` and a
mutant that silently fell back to the built-in 1.0 percent tolerance would be
testing two changes at once.

Every mutant is asserted to have actually changed the file.  A substitution that
matched nothing would run the UNMUTATED auditor and report a clean pass, which
is a false negative of exactly the kind this harness exists to prevent.

THE CASES, AND WHY THERE ARE THREE KINDS
----------------------------------------
  KV1c_duct_heated     the mutations MUST fire.  Conduction in through the hot
                       wall and advection out through the outlet are two
                       independent non-zero terms that must cancel; a wrong
                       advective term breaks the cancellation.
  KV1b_duct_nosource   the mutations must NOT fire, and that is not a defect.
                       Its advective sum is identically zero (inlet +0.146 W,
                       outlet -0.146 W), so scaling or flipping it changes
                       nothing.  This is the NEGATIVE control: it shows the
                       sensitivity measured on KV1c belongs to the case and not
                       to the harness, and it is the reason KV1c had to be built
                       at all.
  the sealed K0c set   the mutations must not fire AND the JSON must be
                       BYTE-IDENTICAL. No advective function object is written
                       on a sealed case, so no mutation of that code path can
                       reach one. This is the "not more permissive" evidence.

M4 IS NOT LIKE THE OTHERS AND THE HARNESS SAYS SO RATHER THAN HIDING IT
------------------------------------------------------------------------
M4 moves the enthalpy datum from the case's TRef to 0 K.  Because the datum
cancels exactly when mass balances, the NET is unchanged -- so M4 does NOT
break closure and the case still passes.  What it changes is the DENOMINATOR:
the imbalance ratio is then taken against the through-flow's absolute enthalpy
instead of against the heat traffic, and the same 0.5 percent band becomes a far
looser gate at an unchanged number.  M4 is therefore reported as the mutation
the closure test CANNOT catch, which is precisely why the datum is fixed in code
and stated in the docstring rather than left to a caller.
"""

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_repo(start):
    """Walk up until `scripts/heat_balance.py` is found, and REFUSE otherwise.

    Not a counted chain of `dirname` calls: this file sits four levels down and
    a hand-counted chain was wrong on the first run, resolving the auditor to
    `docs/scripts/heat_balance.py`. It failed loudly, which was luck -- a chain
    that lands on a DIFFERENT readable file would have mutated the wrong script
    and reported a clean sweep.
    """
    d = start
    while True:
        if os.path.isfile(os.path.join(d, "scripts", "heat_balance.py")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise SystemExit(
                f"REFUSE: no scripts/heat_balance.py in any parent of {start}")
        d = parent


REPO = _find_repo(HERE)
AUDITOR = os.path.join(REPO, "scripts", "heat_balance.py")
RULES = os.path.join(REPO, "docs", "physics_rules.yaml")

BASE = "                Q_adv = -rho * cp * (int_T_phi - TRef * Vdot)"

MUTATIONS = [
    ("M0_unmutated", None,
     "the repaired auditor, unaltered. The control's control: if this does not "
     "pass, nothing below means anything."),
    ("M1_sign_flipped", (BASE, BASE.replace("= -rho", "= +rho")),
     "the advective enthalpy flux enters the ledger with the wrong sign."),
    ("M2_scaled_by_two", (BASE, BASE.replace("= -rho", "= -2.0 * rho")),
     "the advective term is twice what it should be: a wrong rho.cp, a wrong "
     "unit conversion, a double-counted face."),
    ("M3_outlet_dropped",
     (BASE, "                Q_adv = 0.0 if name == 'outlet' else "
            "-rho * cp * (int_T_phi - TRef * Vdot)"),
     "one open patch is silently missing from the advective sum."),
    ("M4_datum_zero", (BASE, BASE.replace("TRef * Vdot", "0.0 * Vdot")),
     "the enthalpy datum is moved from the case's TRef to 0 K."),
    ("M5_weight_dropped",
     ("                int_T_phi = read_dat(case, fa)[1][0]",
      "                int_T_phi = read_dat(case, fv)[1][0]"),
     "surfaceFieldValue silently returns the UNWEIGHTED sum(phi), which is what "
     "it really does when canWeight() is false. This one is aimed at the GUARD, "
     "not at the balance: the auditor must REFUSE, not report a wrong number."),
]

OPEN_CASES = [
    os.path.join(HERE, "KV1c_duct_heated"),
    os.path.join(HERE, "KV1b_duct_nosource"),
]
#: The sealed half of the corpus. Selected on the presence of a MESH, because
#: an auditor cannot audit a case whose `constant/polyMesh/boundary` is absent.
#:
#: THE ARCHIVE IS ASKED FOR BY NAME, NOT SPELLED OUT.  R25 moves
#: `docs/campaigns/<campaign>/*_{runs,sensitivity}/**` to
#: `verification/runs/<campaign>/`, and this path was assembled from SEGMENTS --
#: `os.path.join(REPO, "docs", "campaigns", ...)` -- so a scan for the literal
#: `docs/campaigns` could not see it, which is the same blindness that hid the
#: depth class (L-127).  `lab_paths.run_archive` probes every spelling the map
#: knows and prefers the successor, so this is correct on both sides of the move
#: and of the next one.  A miss REFUSES instead of yielding an empty corpus --
#: the rule `SEALED_EXPECTED` below already states.
sys.path.insert(0, os.path.join(REPO, "scripts"))
import lab_paths as _lab_paths  # noqa: E402

_K0C_RUNS = _lab_paths.run_archive("K0c_runs", "F14-cooling-ladder")
if _K0C_RUNS is None:
    raise SystemExit(
        "REFUSE: no `K0c_runs` archive under any spelling `lab_paths` knows. "
        "The sealed half would compare an EMPTY corpus and report True for "
        "every mutation, which is the vacuous pass this harness exists to stop.")
SEALED_CASES = sorted(
    d for d in glob.glob(os.path.join(str(_K0C_RUNS), "*"))
    if os.path.isfile(os.path.join(d, "constant", "polyMesh", "boundary")))

#: How many sealed cases MUST be found. `constant/polyMesh/` is not tracked
#: (.gitignore:60) and is rebuilt from the dictionaries, so in a FRESH CLONE
#: this list is EMPTY -- and `all(...)` over an empty corpus returns True.
#: The harness would then print `sealed_identical_to_unmutated: True` for every
#: mutation having compared nothing at all. That is exactly the vacuous pass
#: L-98 is about, and it was found by running this file's own reproduction
#: recipe in a fresh clone rather than by reading it. An empty corpus is a
#: BROKEN INSTRUMENT and a broken instrument yields a refusal, never a PASS.
SEALED_EXPECTED = 11


def build_mutant(tmp, name, sub):
    root = os.path.join(tmp, name)
    os.makedirs(os.path.join(root, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(root, "docs"), exist_ok=True)
    dst = os.path.join(root, "scripts", "heat_balance.py")
    src = open(AUDITOR).read()
    if sub is not None:
        old, new = sub
        if src.count(old) != 1:
            raise SystemExit(
                f"REFUSE: mutation {name} anchor matched {src.count(old)} times, "
                "expected exactly 1. An unmatched mutation runs the UNMUTATED "
                "auditor and reports a clean pass, which is the false negative "
                "this harness exists to prevent.")
        src = src.replace(old, new)
    open(dst, "w").write(src)
    rules = os.path.join(root, "docs", "physics_rules.yaml")
    if not os.path.exists(rules):
        os.symlink(RULES, rules)
    return dst


def audit(auditor, case, jsonpath):
    cmd = [sys.executable, auditor, case, "--allow-advective", "--quiet",
           "--json", jsonpath]
    p = subprocess.run(cmd, capture_output=True, text=True)
    rec = dict(exit=p.returncode, stderr=p.stderr.strip()[-400:])
    if os.path.exists(jsonpath):
        r = json.load(open(jsonpath))
        rec.update(passed=r["passed"], Q_net_W=r["Q_net_W"], Q_in_W=r["Q_in_W"],
                   imbalance_pct=r["imbalance_pct"],
                   imbalance_defined=r["imbalance_defined"])
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(HERE, "mutation_results.json"))
    a = ap.parse_args()
    if len(SEALED_CASES) != SEALED_EXPECTED:
        raise SystemExit(
            f"REFUSE: found {len(SEALED_CASES)} meshed sealed K0c cases, "
            f"expected {SEALED_EXPECTED}. `constant/polyMesh/` is not tracked "
            "(.gitignore:60), so a fresh clone has none and the sealed half of "
            "this harness would compare an EMPTY corpus and report True for "
            "every mutation.\n        Rebuild the K0c meshes first:\n"
            f"        for c in {os.path.relpath(_K0C_RUNS, REPO)}/*/; do\n"
            "          [ -f \"$c/system/blockMeshDict\" ] && (cd \"$c\" && blockMesh > log.blockMesh 2>&1)\n"
            "        done\n"
            "        The open half (KV1b, KV1c) is unaffected: their meshes are "
            "rebuilt by run_kv1.sh.")
    for c in OPEN_CASES:
        if not os.path.isfile(os.path.join(c, "constant", "polyMesh", "boundary")):
            raise SystemExit(
                f"REFUSE: {c} has no mesh. Run KV1_runs/run_kv1.sh first.")
    tmp = tempfile.mkdtemp(prefix="kv1mut_")
    out = {}
    try:
        for name, sub, why in MUTATIONS:
            aud = build_mutant(tmp, name, sub)
            out[name] = dict(why=why, cases={})
            for case in OPEN_CASES:
                cn = os.path.basename(case)
                out[name]["cases"][cn] = audit(
                    aud, case, os.path.join(tmp, f"{name}_{cn}.json"))
            # The sealed half: only M0 and one mutation are needed to make the
            # point, but every one is run, because "no advective function object
            # is written" is a claim about the code path and cheap to check for
            # real on all of them.
            sealed = {}
            for case in SEALED_CASES:
                cn = os.path.basename(case)
                sealed[cn] = audit(
                    aud, case, os.path.join(tmp, f"{name}_{cn}.json"))
            out[name]["sealed"] = sealed
        # sealed byte-identity against M0
        ref = out["M0_unmutated"]["sealed"]
        for name, _s, _w in MUTATIONS[1:]:
            same = all(out[name]["sealed"][k] == ref[k] for k in ref)
            out[name]["sealed_identical_to_unmutated"] = bool(same)
    finally:
        pass
    with open(a.json, "w") as fh:
        json.dump(out, fh, indent=2)

    w = print
    w("=" * 78)
    w("KV1 MUTATION HARNESS -- can the advective term FAIL?")
    w("=" * 78)
    w(f"{'mutation':<20}{'KV1c heated':>26}{'KV1b degenerate':>26}")
    w("-" * 78)
    for name, _s, _w2 in MUTATIONS:
        row = out[name]["cases"]

        def cell(c):
            r = row[c]
            if "passed" not in r:
                return f"REFUSED (exit {r['exit']})"
            v = "PASS" if r["passed"] else "FAIL"
            if r["imbalance_defined"]:
                return f"{v} {r['imbalance_pct']:.4f}% exit {r['exit']}"
            return f"{v} UNDEFINED exit {r['exit']}"
        w(f"{name:<20}{cell('KV1c_duct_heated'):>26}"
          f"{cell('KV1b_duct_nosource'):>26}")
    w("-" * 78)
    w(f"sealed K0c set ({len(SEALED_CASES)} cases found, {SEALED_EXPECTED} required), "
      "JSON identical to the unmutated auditor:")
    for name, _s, _w2 in MUTATIONS[1:]:
        w(f"    {name:<20} {out[name]['sealed_identical_to_unmutated']}")
    w("=" * 78)
    for name, _s, why in MUTATIONS:
        w(f"  {name}: {why}")
    w(f"\nwritten to {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
