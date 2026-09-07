#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
map_carrier.py -- VMFL034-R3 Stage-1 -> Stage-2 carrier freeze.

Injects the CONVERGED single-phase carrier internal field (Stage-1 simpleFoam:
U, k, epsilon, nut on the same mesh) into the two-phase Stage-2 fields the
frozen-flow solver holds fixed, PRESERVING each target's own boundaryField (the
two-phase BC structure: pressureInletOutletVelocity outlet keyed to phi.air, per-
phase wall functions, empty frontAndBack).  Only the internalField block is
replaced; the same mesh guarantees the list length matches.  Because the Stage-2
solver never solves momentum/pressure/energy (frozen flow), the carrier so injected
stays frozen for the whole moment transport.

Carrier -> two-phase targets (dilute, no-slip: both phases move with the carrier;
mixtureKEpsilon mixture fields = carrier turbulence):
    U       -> U.air, U.water
    k       -> km, k.air, k.water
    epsilon -> epsilonm, epsilon.air, epsilon.water
    nut     -> nut.air, nut.water
phi.air/phi.water are NOT written -- the solver computes the (frozen) flux from the
frozen U at createFields time.

Usage:  map_carrier.py --carrier <stage1_time_dir> --target <stage2_0_dir>
REFUSES (exit 2) if a carrier source or a target file is missing, or if a carrier
internalField cannot be parsed (never silently maps a partial carrier).
"""
import sys, os, re, argparse

MAP = {
    "U":       ["U.air", "U.water"],
    "k":       ["km", "k.air", "k.water"],
    "epsilon": ["epsilonm", "epsilon.air", "epsilon.water"],
    "nut":     ["nut.air", "nut.water"],
}

# internalField: 'uniform <val>;' or 'nonuniform List<...> N (....);'
_IF = re.compile(
    r"internalField\s+(?:uniform\s+[^;]+|nonuniform\s+List<[^>]+>\s*\d+\s*\(.*?\))\s*;",
    re.S,
)

def read_internalfield(path):
    with open(path) as fh:
        t = fh.read()
    m = _IF.search(t)
    if not m:
        sys.stderr.write("map_carrier REFUSAL: cannot parse internalField in %s (exit 2)\n" % path)
        raise SystemExit(2)
    return m.group(0)

_UNIF = re.compile(r"internalField\s+uniform\s+([^;]+);")

def inject(target_path, if_block):
    with open(target_path) as fh:
        t = fh.read()
    m = _IF.search(t)
    if not m:
        sys.stderr.write("map_carrier REFUSAL: no internalField to replace in %s (exit 2)\n" % target_path)
        raise SystemExit(2)
    # The two-phase 0-fields reference the (uniform) internalField from computed
    # boundary patches via the `$internalField` macro (value/inletValue).  Once the
    # internalField becomes the carrier's NONUNIFORM list, that macro would expand to
    # a volume-sized list on a patch -> IO error.  So FIRST neutralize every
    # `$internalField` macro to the field's ORIGINAL uniform value (semantically
    # identical placeholder; computed patches recompute it at startup), THEN swap the
    # internalField block for the carrier's.
    if "$internalField" in t:
        mu = _UNIF.search(t)
        if not mu:
            sys.stderr.write("map_carrier REFUSAL: %s uses $internalField but its "
                             "internalField is not uniform -- cannot neutralize safely (exit 2)\n" % target_path)
            raise SystemExit(2)
        t = t.replace("$internalField", "uniform " + mu.group(1).strip())
    t2 = _IF.sub(lambda _m: if_block, t, count=1)
    with open(target_path, "w") as fh:
        fh.write(t2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--carrier", required=True, help="Stage-1 converged time dir (holds U,k,epsilon,nut)")
    ap.add_argument("--target", required=True, help="Stage-2 0/ dir (holds U.air,U.water,km,...)")
    a = ap.parse_args()
    n = 0
    for src, tgts in MAP.items():
        sp = os.path.join(a.carrier, src)
        if not os.path.exists(sp):
            sys.stderr.write("map_carrier REFUSAL: carrier field %s missing (exit 2)\n" % sp)
            raise SystemExit(2)
        ifb = read_internalfield(sp)
        for tg in tgts:
            tp = os.path.join(a.target, tg)
            if not os.path.exists(tp):
                sys.stderr.write("map_carrier REFUSAL: target field %s missing (exit 2)\n" % tp)
                raise SystemExit(2)
            inject(tp, ifb)
            n += 1
    print("map_carrier: injected carrier internalField into %d two-phase fields (BCs preserved)" % n)
    return 0

if __name__ == "__main__":
    sys.exit(main())
