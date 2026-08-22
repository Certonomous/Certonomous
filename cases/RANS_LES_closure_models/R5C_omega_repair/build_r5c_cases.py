#!/usr/bin/env python3
"""R5C step 1 - build the 27 repaired + 2 legacy frozen-extraction cases.

PREREGISTRATION.md sec. 2.4.  The 27 R5C cases are built by COPYING R4's own
`0/`, `constant/` and `system/` out of /home/ubuntu/closure-data/r4/frozen/,
NOT by rebuilding from the benchmark.  That is deliberate and is registered as
a strengthening of gate G1: the inputs are then bit-identical to R4's by
construction, so any difference G1 measures is the OPERATOR's and nothing else.
Every 0/ field's sha256 is recorded and asserted equal to the source.

The two G2 cases are copied out of verification/runs/W2_sparta_runs/{ph,cbfs}
_frozen and run with omegaSourceRepair FALSE - the legacy branch - so that
byte-identity against the W2 record proves the new build is not a new solver.

The ONLY edits made to a copied case (sec. 2.4):
  1. constant/turbulenceProperties: RASModel -> kOmegaSSTFrozenV2, and
     omegaSourceRepair <true|false> inside the RAS block.  Insert-or-replace,
     then ASSERTED back from disk (L-221/L-222: a silent no-op here returns
     R4's own model and R4's own answer, which is the exact L-221 shape).
  2. system/controlDict: libs merged through scripts/foam_libs.ensure_libs,
     then asserted from disk at this call site.
endTime, deltaT, writeInterval, writePrecision, writeFormat, purgeWrite,
startFrom and startTime are NOT touched.

Nothing is fitted here and no test or validation case is touched (asserted
through r4_lib.assert_no_test_case).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "cases", "RANS_LES_closure_models",
                                "R4_sparta_build"))
sys.path.insert(0, os.path.join(_REPO, "scripts"))

import r4_lib as R                                   # noqa: E402
from foam_libs import ensure_libs, assert_libs       # noqa: E402

R4_FROZEN = "/home/ubuntu/closure-data/r4/frozen"
W2 = os.path.join(_REPO, "verification", "runs", "W2_sparta_runs")
OUT = "/home/ubuntu/closure-data/r5c"
V2_LIB = "libspartaFrozenV2.so"
V2_MODEL = "kOmegaSSTFrozenV2"

TIME_RE = re.compile(r"^[0-9]+(\.[0-9]+)?$")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def refuse_if_dirty(dst):
    """Rule 4's guard: a run may not start in a directory that already holds
    a 0/ or a numeric time directory.  No run is resumed or restarted in place.
    """
    if not os.path.isdir(dst):
        return
    for d in os.listdir(dst):
        if d == "0" or TIME_RE.fullmatch(d):
            raise SystemExit(
                f"GUARD REFUSAL: {dst} already holds '{d}'.  A frozen "
                f"extraction is never resumed or restarted in place "
                f"(PREREGISTRATION sec. 4).")


def write_turbulence_properties(case_dir, repair):
    """RASModel -> kOmegaSSTFrozenV2 + the one switch.  Written, then ASSERTED
    back from disk.  A silent no-op here would select R4's own model."""
    path = os.path.join(case_dir, "constant", "turbulenceProperties")
    body = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      turbulenceProperties;
}}

simulationType RAS;

RAS
{{
    RASModel        {V2_MODEL};
    turbulence      on;
    printCoeffs     on;
    omegaSourceRepair {'true' if repair else 'false'};
}}
"""
    with open(path, "w") as fh:
        fh.write(body)
    back = open(path).read()
    assert re.search(rf"^\s*RASModel\s+{V2_MODEL};\s*$", back, re.M), (
        f"RASModel did not land in {path}")
    want = "true" if repair else "false"
    assert re.search(rf"^\s*omegaSourceRepair\s+{want};\s*$", back, re.M), (
        f"omegaSourceRepair {want} did not land in {path}")
    return path


def install_libs(case_dir):
    """L-221/L-222/rule 14: merge (never blind-append, never blind-replace)
    through the shared depth-aware helper, then assert from disk here."""
    cd = os.path.join(case_dir, "system", "controlDict")
    ensure_libs(cd, V2_LIB)
    assert_libs(cd, V2_LIB)                       # assert AT the call site
    s = open(cd).read()
    assert V2_LIB in s, f"libs insert failed: {cd}"
    return cd


def build_one(name, src, dst, repair):
    refuse_if_dirty(dst)
    os.makedirs(dst, exist_ok=True)
    for sub in ("constant", "system"):
        d = os.path.join(dst, sub)
        if os.path.isdir(d):
            shutil.rmtree(d)
        shutil.copytree(os.path.join(src, sub), d)
    # Case-root regular files that the dictionaries #include.  The DUCT family
    # ships `caseDef` and every case ships `fieldDef`; `0/U` on the ducts opens
    # `#include "../caseDef"` and the solver dies on FOAM FATAL IO ERROR
    # before iteration 1 if it is absent.  Run artefacts are never copied.
    SKIP = ("rc", "wall_seconds", "omegaHistory.csv")
    for f in sorted(os.listdir(src)):
        sp = os.path.join(src, f)
        if not os.path.isfile(sp) or f in SKIP or f.startswith("log."):
            continue
        shutil.copyfile(sp, os.path.join(dst, f))

    # 0/ is copied LAST and its mtimes are fresh, so the age guard dates the
    # run allowed to produce the answer.
    shutil.copytree(os.path.join(src, "0"), os.path.join(dst, "0"))

    inputs = {}
    for f in sorted(os.listdir(os.path.join(src, "0"))):
        sp = os.path.join(src, "0", f)
        dp = os.path.join(dst, "0", f)
        if os.path.isfile(sp):
            a, b = sha256(sp), sha256(dp)
            assert a == b, f"0/{f} copy is not bit-identical for {name}"
            inputs[f] = a

    write_turbulence_properties(dst, repair)
    install_libs(dst)
    # touch 0/ last, so every written field is strictly newer (rule 4)
    for root, _, files in os.walk(os.path.join(dst, "0")):
        for f in files:
            os.utime(os.path.join(root, f), None)
    os.utime(os.path.join(dst, "0"), None)

    return {"case": name, "src": src, "dir": dst,
            "omegaSourceRepair": bool(repair), "inputs_sha256": inputs}


def main():
    # `--only <case> [<case> ...]` builds a named subset.  A case whose
    # destination already holds a time directory is REFUSED by the guard, so
    # this can never silently re-open a run that produced an answer.
    only = None
    if len(sys.argv) > 1 and sys.argv[1] == "--only":
        only = set(sys.argv[2:])
        assert only, "--only needs at least one case name"

    cases = R.training_cases()
    R.assert_no_test_case([c for c, _, _ in cases])

    rec = []
    for case, _bench, family in cases:
        if only is not None and case not in only:
            continue
        src = os.path.join(R4_FROZEN, case)
        assert os.path.isdir(src), f"R4 frozen case missing: {src}"
        dst = os.path.join(OUT, "frozen", case)
        r = build_one(case, src, dst, repair=True)
        r["family"] = family
        rec.append(r)
        print(f"[built repaired] {case:22s} {family}", flush=True)

    w2 = []
    for tag, srcname in (("ph", "ph_frozen"), ("cbfs", "cbfs_frozen")):
        if only is not None and tag not in only:
            continue
        src = os.path.join(W2, srcname)
        assert os.path.isdir(src), f"W2 record missing: {src}"
        dst = os.path.join(OUT, "w2_legacy", tag)
        r = build_one(tag, src, dst, repair=False)
        r["w2_record"] = src
        w2.append(r)
        print(f"[built legacy  ] {tag:22s} (gate G2)", flush=True)

    man = {"n_repaired": len(rec), "n_legacy": len(w2),
           "out": OUT, "model": V2_MODEL, "lib": V2_LIB,
           "only": sorted(only) if only else None,
           "repaired": rec, "legacy": w2}
    os.makedirs(OUT, exist_ok=True)
    mpath = os.path.join(
        OUT, "build_manifest.json" if only is None
        else "build_manifest_" + "_".join(sorted(only)) + ".json")
    with open(mpath, "w") as fh:
        json.dump(man, fh, indent=1)
    print(f"\n{len(rec)} repaired + {len(w2)} legacy cases -> {OUT}")


if __name__ == "__main__":
    main()
