#!/usr/bin/env python3
"""grade_d406.py -- every deviation of the D406 repair run from the published
rung, as a number.

Adds no arithmetic of its own to the physics: it reads the JSON the unmodified
`analyse_k0b_mesh.py` wrote in this tree and the JSON committed in
`K0b_mesh_sensitivity/`, and subtracts.  The thresholds are the ones fixed in
`docs/campaigns/F14-cooling-ladder/K0b_D406_REPAIR_PREREGISTRATION.md` section 5
BEFORE the first solve: < 0.1 % reproduced, > 1 % NOT REPRODUCED, and the band
between carries no verdict.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNG = os.path.abspath(os.path.join(HERE, "..", "K0b_mesh_sensitivity"))

NEW = json.load(open(os.path.join(HERE, "k0b_mesh_sensitivity.json")))
PUB = json.load(open(os.path.join(RUNG, "k0b_mesh_sensitivity.json")))

QUANTS = ["Nu_avg_hot", "Nu_avg_cold", "Nu_max_hot", "Nu_min_hot",
          "V_star_max", "V_star_min", "U_star_max", "U_star_min",
          "x_over_L_at_v_max", "stratification_S_leastsq_mid25pct",
          "energy_balance_pct", "Pr", "dT_K"]

out = {}
lines = []
def p(s=""):
    lines.append(s)
    print(s)

def dev(a, b):
    if a == b:
        return 0.0
    if b == 0:
        return float("inf")
    return 100.0 * (a - b) / b

p("=" * 78)
p("D406 REPAIR -- every deviation from the published rung, as a number")
p("=" * 78)
p("")
p("Threshold, pre-registered before the first solve: < 0.1 % reproduced,")
p("> 1 % NOT REPRODUCED; the band between carries no verdict.")
p("")

out["legs"] = {}
worst_overall = 0.0
for tag in ("32x32", "64x64", "128x128"):
    n, q = NEW["legs"][tag], PUB["legs"][tag]
    p(f"--- leg {tag}  (cells {n['cells']}, t = {n['time']}; published t = {q['time']}) ---")
    p(f"{'quantity':<38} {'re-run':>22} {'published':>22} {'deviation %':>14}")
    rec, exact, worst = {}, 0, 0.0
    for k in QUANTS:
        d = dev(n[k], q[k])
        if n[k] == q[k]:
            exact += 1
        worst = max(worst, abs(d))
        rec[k] = dict(rerun=n[k], published=q[k], deviation_pct=d,
                      bit_identical=(n[k] == q[k]))
        p(f"{k:<38} {n[k]!r:>22} {q[k]!r:>22} {d:>14.10f}")
    p(f"  time              re-run {n['time']!r}   published {q['time']!r}   "
      f"{'MATCH' if n['time'] == q['time'] else 'DIFFER'}")
    p(f"  Nu history writes re-run {len(n['Nu_history_by_time'])}   "
      f"published {len(q['Nu_history_by_time'])}   "
      f"{'MATCH' if len(n['Nu_history_by_time']) == len(q['Nu_history_by_time']) else 'DIFFER'}")
    hist_exact = sum(1 for kk in q["Nu_history_by_time"]
                     if kk in n["Nu_history_by_time"]
                     and n["Nu_history_by_time"][kk] == q["Nu_history_by_time"][kk])
    p(f"  Nu history values bit-identical: {hist_exact} of {len(q['Nu_history_by_time'])}")
    p(f"  {exact} of {len(QUANTS)} quantities BIT-IDENTICAL; largest |deviation| {worst:.10f} %")
    p("")
    worst_overall = max(worst_overall, worst)
    out["legs"][tag] = dict(quantities=rec, bit_identical=exact,
                            n_quantities=len(QUANTS), worst_abs_deviation_pct=worst,
                            time_rerun=n["time"], time_published=q["time"],
                            n_writes_rerun=len(n["Nu_history_by_time"]),
                            n_writes_published=len(q["Nu_history_by_time"]),
                            hist_bit_identical=hist_exact)

p("--- the ladder: Richardson block, leaf by leaf ---")
p(f"{'quantity':<38} {'leaf':<22} {'re-run':>22} {'published':>22}")
out["richardson"] = {}
rich_diff = 0
for k, pubv in PUB["richardson"].items():
    newv = NEW["richardson"][k]
    rec = {}
    for leaf, pv in pubv.items():
        nv = newv[leaf]
        same = (nv == pv)
        rec[leaf] = dict(rerun=nv, published=pv, bit_identical=same)
        if not same:
            rich_diff += 1
            p(f"{k:<38} {leaf:<22} {nv!r:>22} {pv!r:>22}   DIFFERS")
    out["richardson"][k] = rec
    p(f"{k:<38} {'p':<22} {newv['p']!r:>22} {pubv['p']!r:>22}")
    p(f"{'':<38} {'GCI_fine_pct':<22} {newv['GCI_fine_pct']!r:>22} {pubv['GCI_fine_pct']!r:>22}")
    p(f"{'':<38} {'change_64_to_128_pct':<22} {newv['change_64_to_128_pct']!r:>22} {pubv['change_64_to_128_pct']!r:>22}")
    p(f"{'':<38} {'extrapolated':<22} {newv['extrapolated']!r:>22} {pubv['extrapolated']!r:>22}")
p(f"  Richardson leaves differing: {rich_diff}")
p("")

# ---- whole-document leaf comparison -----------------------------------------
def flat(o, pre=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from flat(v, f"{pre}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from flat(v, f"{pre}[{i}]")
    else:
        yield pre, o

fn, fp = dict(flat(NEW)), dict(flat(PUB))
keys = sorted(set(fn) | set(fp))
diffs = []
for k in keys:
    a, b = fn.get(k, "<absent>"), fp.get(k, "<absent>")
    if a != b:
        diffs.append((k, a, b))
p(f"--- end-to-end: {len(fp)} leaves in the published document, "
  f"{len(fn)} in the re-run's; {len(diffs)} differ ---")

def classify(k):
    low = k.lower()
    if "wall_clock" in low or "core_minutes" in low or "core_seconds" in low:
        return "wall clock and derived cost"
    if k.endswith("/case"):
        return "case path string"
    return "OTHER -- inspect"

cls = {}
for k, a, b in diffs:
    c = classify(k)
    cls.setdefault(c, []).append((k, a, b))
for c in sorted(cls):
    p(f"  [{c}] {len(cls[c])}")
    for k, a, b in cls[c]:
        p(f"      {k}")
        p(f"          re-run   : {a!r}")
        p(f"          published: {b!r}")
out["end_to_end"] = dict(
    n_leaves_published=len(fp), n_leaves_rerun=len(fn), n_differing=len(diffs),
    classes={c: [d[0] for d in v] for c, v in cls.items()},
    physics_leaves_differing=len(cls.get("OTHER -- inspect", [])))
p("")
p(f"PHYSICS LEAVES DIFFERING: {len(cls.get('OTHER -- inspect', []))}")
p(f"WORST |deviation| over all graded quantities on all three legs: {worst_overall:.10f} %")

json.dump(out, open(os.path.join(HERE, "k0b_d406_regrade.json"), "w"), indent=1)
open(os.path.join(HERE, "grade_d406.txt"), "w").write("\n".join(lines) + "\n")
