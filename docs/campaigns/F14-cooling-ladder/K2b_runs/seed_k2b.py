#!/usr/bin/env python3
"""seed_k2b.py -- seed a K2b control twin from its parent's converged field.

    python3 seed_k2b.py K2bP_C1_g0 K2bP_C2_dT13 K2bP_C3_plant
    python3 seed_k2b.py                      # every control in build_k2b.CASES

WHY A SEED AND NOT A FRESH START
--------------------------------
The three controls are the parent case perturbed in exactly one dictionary.
Started from `0.orig` each would cost a full 5,000-iteration solve and the
authorised 60 core-minutes does not hold four of those.  Started from the
parent's converged field they re-converge in a few hundred iterations, which is
what makes the control set affordable at all.

WHAT IS COPIED AND WHAT IS DELIBERATELY NOT
-------------------------------------------
The parent's **internalField** is copied.  The control's **own boundaryField**
is kept, taken from its own `0.orig`.  That distinction is the whole file: a
straight `cp -r` of the parent's time directory would also carry the parent's
BOUNDARY CONDITIONS, and `K2bP_C2_dT13` would then quietly run at the parent's
12.0 K offset while its dictionary, its CASE.txt and its write-up all said 13.2
-- a planted control that plants nothing, which is the failure this campaign
already met once at KV1b and is not going to meet again by a different route.

The seeded state is written to `0/`, and `system/controlDict` in the control
cases carries `startFrom latestTime`, so the run picks it up as time 0 and
counts its own iterations from there.
"""

import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_k2b  # noqa: E402

FIELDS = ("U", "T", "p_rgh", "k", "omega", "nut", "alphat")
RE_BF = re.compile(r"^boundaryField\s*$", re.M)


def latest_time(case):
    times = []
    for d in os.listdir(case):
        if os.path.isdir(os.path.join(case, d)) and re.fullmatch(r"[1-9]\d*", d):
            times.append(int(d))
    if not times:
        raise SystemExit(f"REFUSE: {case} has no written time directory to seed from")
    return str(max(times))


def split_at_boundaryField(text, what):
    m = RE_BF.search(text)
    if not m:
        raise SystemExit(f"REFUSE: no boundaryField block found in {what}")
    return text[:m.start()], text[m.start():]


def seed(control, parent):
    src = os.path.join(HERE, parent)
    dst = os.path.join(HERE, control)
    t = latest_time(src)
    out = os.path.join(dst, "0")
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    for f in FIELDS:
        sp = os.path.join(src, t, f)
        op = os.path.join(dst, "0.orig", f)
        if not os.path.exists(sp):
            raise SystemExit(f"REFUSE: {sp} does not exist")
        head, _ = split_at_boundaryField(open(sp).read(), sp)
        _, tail = split_at_boundaryField(open(op).read(), op)
        with open(os.path.join(out, f), "w") as fh:
            fh.write(head + tail)
    with open(os.path.join(dst, "SEED.txt"), "w") as fh:
        fh.write(f"control        {control}\n"
                 f"seeded_from    {parent}/{t}\n"
                 f"fields         {' '.join(FIELDS)}\n"
                 f"internalField  from the parent's converged solution\n"
                 f"boundaryField  from this control's OWN 0.orig -- see seed_k2b.py\n")
    print(f"seeded {control:16s} <- {parent}/{t}   "
          f"({len(FIELDS)} fields, boundaryField from its own 0.orig)")


def main(argv):
    controls = {n: v[6] for n, v in build_k2b.CASES.items() if v[6]}
    want = argv[1:] or sorted(controls)
    for c in want:
        if c not in controls:
            raise SystemExit(f"REFUSE: {c} is not a seeded control "
                             f"(seeded controls: {sorted(controls)})")
        seed(c, controls[c])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
