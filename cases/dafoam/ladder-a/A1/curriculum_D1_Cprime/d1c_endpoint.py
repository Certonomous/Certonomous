"""D1-C' comparator core: the reader, the planted-zero control and the FD kernel.

Frozen by the commit that carries
`cases/dafoam/ladder-a/A1/curriculum_D1_Cprime/PREREGISTRATION.md`.
NOT EDITED AFTER THE FIRST LAUNCH.  An edit voids the arm.

Standard library ONLY, on purpose.  This module must be importable and runnable
on the HOST, outside any container, so that its planted-zero control can be
dry-run against arm O's REAL endpoint artifact BEFORE the freeze, at zero
compute.  That dry run is the whole point of this file: it is the repair for
L-273, in which a control that planted into its own synthetic fixture proved the
arithmetic and not the coupling, and then killed D1 arm C at 14 s on a KeyError.

Nothing here selects a step.  Every step is INHERITED from arm O's frozen plan
and is additionally asserted against a literal frozen in this file, so a step
cannot move even if the file that is read is wrong.
"""

import copy
import hashlib
import json
import os
import shutil
import sys

# ---- frozen constants (PREREGISTRATION.md sections 4, 6) --------------------

PLANT = 1.234e-03                      # CLAUDE.md rule 3
TRIVIAL_STEP = 1e-8                    # DAFOAM_CHARTER.md section 4
PLATEAU_TOL = 0.10                     # inherited from D1 gate G3
CMIN = 5.0                             # inherited from D1 gate G3

# arm O's endpoint artifact, by md5.  A mismatch VOIDS the item (refuses).
ARMO_JSON_MD5 = "e63f57710cee6e2170f2e9cef39f8b2a"

# The four graded components, IN THIS ORDER.  The order is part of the
# instrument: each FD pair warm-starts from the previous component's last
# perturbed state, exactly as arm O's suite did.
NAMED = [("shape", 6), ("shape", 1), ("shape", 5), ("patchV", 1)]

# Steps INHERITED from arm O and frozen here as literals.  The file is read for
# them and the read value must equal the literal, or the comparator refuses.
FROZEN_STEPS = {
    "shape[6]": {"s_lo": 1e-4, "s_hi": 3e-4},
    "shape[1]": {"s_lo": 1e-4, "s_hi": 3e-4},
    "shape[5]": {"s_lo": 1e-4, "s_hi": 3e-4},
    "patchV[1]": {"s_lo": 1e-3, "s_hi": 3e-3},
}

# eta is INHERITED from D1 arm E run 2.  It sizes NOTHING here -- every step is
# inherited -- and is used only to print the clearance diagnostic C_measured on
# the same basis arm O printed it.
ETA_INHERITED = 1.957349804806996e-08

# The producer's ACTUAL top-level key set, read from the file arm O wrote.
# Asserted before any consumption.  L-273: the producer's key set is asserted
# against the consumer's in the invocation that freezes both.
PRODUCER_KEYS = ["CD", "CL", "J_adj", "cons", "eta", "fd", "feasible_note",
                 "maxrss_GiB", "patchV", "plan", "shape", "tag", "trivial"]

# Every channel this comparator actually CONSUMES from that file.  The planted
# zero control plants into ALL of them and refuses unless ALL of them read back
# moved.  A consumed channel the control does not plant into is exactly the hole
# L-273 names.
CONSUMED_KEYS = ["shape", "patchV", "plan", "eta", "J_adj", "fd"]


# ---- refusal ---------------------------------------------------------------

class Refuse(Exception):
    """Raised on any refusal.  Callers exit 2.  Never degrades to a warning."""


def _refuse(tag, payload):
    print("D1C_REFUSE %s %s" % (tag, json.dumps(payload, sort_keys=True)),
          flush=True)
    raise Refuse(tag)


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---- the reader ------------------------------------------------------------

def read_endpoint(path):
    """THE reader.  Everything -- the real read, the plant read-back and the
    negative control -- goes through this one function.  A control that reads
    back through a different path is not a control."""
    with open(path) as fh:
        return json.load(fh)


def assert_keys(obj, where):
    have = sorted(obj.keys())
    if have != sorted(PRODUCER_KEYS):
        _refuse("KEYSET", {"where": where, "expected": sorted(PRODUCER_KEYS),
                           "found": have,
                           "missing": sorted(set(PRODUCER_KEYS) - set(have)),
                           "extra": sorted(set(have) - set(PRODUCER_KEYS))})
    for k in CONSUMED_KEYS:
        if k not in obj:
            _refuse("CONSUMED_KEY_ABSENT", {"where": where, "key": k})
    return True


def assert_steps(obj, where):
    """Steps are inherited AND frozen.  The read value must equal the literal."""
    plan = obj["plan"]
    for key, want in FROZEN_STEPS.items():
        if key not in plan:
            _refuse("PLAN_KEY_ABSENT", {"where": where, "key": key})
        for tag in ("s_lo", "s_hi"):
            got = plan[key].get(tag)
            if got is None or abs(float(got) - want[tag]) > 1e-18:
                _refuse("STEP_MOVED", {"where": where, "component": key,
                                       "which": tag, "frozen": want[tag],
                                       "read": got})
    return True


# ---- gate G5-C': the planted-zero control, against the REAL artifact --------

def _plant_into(base):
    """Perturb EVERY consumed channel by exactly PLANT."""
    p = copy.deepcopy(base)
    p["shape"] = [v + PLANT for v in base["shape"]]
    p["patchV"] = [v + PLANT for v in base["patchV"]]
    p["eta"] = base["eta"] + PLANT
    p["J_adj"] = copy.deepcopy(base["J_adj"])
    p["J_adj"]["shape"] = [v + PLANT for v in base["J_adj"]["shape"]]
    p["J_adj"]["patchV"] = [v + PLANT for v in base["J_adj"]["patchV"]]
    p["plan"] = copy.deepcopy(base["plan"])
    for k in p["plan"]:
        p["plan"][k]["s_lo"] = base["plan"][k]["s_lo"] + PLANT
        p["plan"][k]["s_hi"] = base["plan"][k]["s_hi"] + PLANT
    p["fd"] = copy.deepcopy(base["fd"])
    for k in p["fd"]:
        p["fd"][k]["J_adj"] = base["fd"][k]["J_adj"] + PLANT
        for st in p["fd"][k]["steps"]:
            p["fd"][k]["steps"][st]["fd"] = base["fd"][k]["steps"][st]["fd"] + PLANT
    return p


def _deltas(base, back):
    """Read-back deltas, per consumed channel, as max |delta - PLANT|."""
    out = {}
    out["shape"] = max(abs((b - a) - PLANT)
                       for a, b in zip(base["shape"], back["shape"]))
    out["patchV"] = max(abs((b - a) - PLANT)
                        for a, b in zip(base["patchV"], back["patchV"]))
    out["eta"] = abs((back["eta"] - base["eta"]) - PLANT)
    out["J_adj"] = max(
        [abs((b - a) - PLANT) for a, b in zip(base["J_adj"]["shape"],
                                              back["J_adj"]["shape"])]
        + [abs((b - a) - PLANT) for a, b in zip(base["J_adj"]["patchV"],
                                                back["J_adj"]["patchV"])])
    out["plan"] = max(
        max(abs((back["plan"][k][t] - base["plan"][k][t]) - PLANT)
            for t in ("s_lo", "s_hi"))
        for k in base["plan"])
    out["fd"] = max(
        max([abs((back["fd"][k]["J_adj"] - base["fd"][k]["J_adj"]) - PLANT)]
            + [abs((back["fd"][k]["steps"][s]["fd"]
                    - base["fd"][k]["steps"][s]["fd"]) - PLANT)
               for s in base["fd"][k]["steps"]])
        for k in base["fd"])
    return out


def planted_zero_control(src_json, workdir, reader=read_endpoint):
    """CLAUDE.md rule 3, repaired for L-273.

    Plants into a COPY OF THE REAL ARTIFACT arm O wrote -- never a synthetic
    fixture -- reads it back through the SAME reader, and REFUSES (exit 2)
    unless every consumed channel moved by exactly the plant.  Asserts the
    source file's md5 before and after, so the control cannot damage the
    evidence it reads.
    """
    got = md5_of(src_json)
    if got != ARMO_JSON_MD5:
        _refuse("ARMO_MD5", {"path": src_json, "expected": ARMO_JSON_MD5,
                             "found": got})
    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    frozen = os.path.join(workdir, "armO_endpoint_frozen.json")
    if os.path.abspath(frozen) != os.path.abspath(src_json):
        shutil.copyfile(src_json, frozen)
    if md5_of(frozen) != ARMO_JSON_MD5:
        _refuse("COPY_MD5", {"path": frozen, "expected": ARMO_JSON_MD5,
                             "found": md5_of(frozen)})

    base = reader(frozen)
    assert_keys(base, "armO_endpoint_frozen.json")
    assert_steps(base, "armO_endpoint_frozen.json")

    plant_path = frozen + ".plant"
    with open(plant_path, "w") as fh:
        json.dump(_plant_into(base), fh, indent=1)
    back = reader(plant_path)
    assert_keys(back, "armO_endpoint_frozen.json.plant")
    d = _deltas(base, back)
    os.remove(plant_path)

    seen = {k: bool(v < 1e-12) for k, v in d.items()}
    after = md5_of(src_json)
    out = {"plant": PLANT, "channels_planted": CONSUMED_KEYS,
           "max_residual_vs_plant": d, "channel_seen": seen,
           "src_md5_before": got, "src_md5_after": after,
           "src_unchanged": bool(got == after),
           "pass": bool(all(seen.values()) and got == after)}
    if not out["pass"]:
        _refuse("PLANTED_ZERO", out)
    print("D1C_G5_PLANTED_ZERO OK %s" % json.dumps(out, sort_keys=True),
          flush=True)
    return out


def keyset_control(src_json, workdir):
    """L-273's own defect, replayed as a live control.

    Rename the producer's `"CD"` to `"CD_final"` -- the exact key D1 arm C's
    consumer reached for -- and require the comparator to REFUSE with a named
    message.  The failure mode this rules out is a `KeyError` raised deep inside
    a consumer at 14 s of container time, which is what actually happened.
    """
    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    obj = read_endpoint(src_json)
    obj["CD_final"] = obj.pop("CD")
    broken = os.path.join(workdir, "keyset_control_renamed.json")
    with open(broken, "w") as fh:
        json.dump(obj, fh, indent=1)
    try:
        assert_keys(read_endpoint(broken), "keyset_control_renamed.json")
    except Refuse as exc:
        os.remove(broken)
        print("D1C_G5_KEYSET_CONTROL OK refused=%s" % exc, flush=True)
        return {"pass": True, "refused_with": str(exc)}
    os.remove(broken)
    print("D1C_G5_KEYSET_CONTROL FAILED renamed key was accepted", flush=True)
    return {"pass": False, "refused_with": None}


def negative_control(src_json, workdir):
    """The control must be able to FAIL.  A deliberately blind reader -- one
    that returns the unperturbed file whatever path it is handed -- must be
    REFUSED.  A planted-zero control that cannot refuse is not a control."""
    frozen = os.path.join(workdir, "armO_endpoint_frozen.json")
    if not os.path.exists(frozen):
        shutil.copyfile(src_json, frozen)

    def blind(_path, _f=frozen):
        with open(_f) as fh:
            return json.load(fh)

    try:
        planted_zero_control(src_json, workdir, reader=blind)
    except Refuse as exc:
        print("D1C_G5_NEGATIVE_CONTROL OK refused=%s" % exc, flush=True)
        return {"pass": True, "refused_with": str(exc)}
    print("D1C_G5_NEGATIVE_CONTROL FAILED blind reader was accepted",
          flush=True)
    return {"pass": False, "refused_with": None}


# ---- the FD kernel ---------------------------------------------------------

def central_fd(f, x, i, s, restore=None):
    """(f(x + s e_i) - f(x - s e_i)) / (2 s).

    Deliberately identical in behaviour to arm O's kernel
    (`d1_fd_endpoint.py:62-80`, md5 7e454d2f1830a40086465d9b5c57a941): plus
    first, minus second, then a SET-only restore that does not solve, so the
    next component's first solve warm-starts from the last perturbed state.
    The comparison to arm O is like-for-like only if the perturbation history
    is the same, so it is reproduced rather than improved.
    """
    x = [float(v) for v in x]
    xp = list(x)
    xp[i] = xp[i] + s
    fp = f(xp)
    xm = list(x)
    xm[i] = xm[i] - s
    fm = f(xm)
    if restore is not None:
        restore(x)
    return (fp - fm) / (2.0 * s), fp, fm


def selftest_cubic():
    """A kernel that cannot differentiate a cubic is not permitted to
    differentiate a solver."""
    calls = {"n": 0}

    def g(v):
        calls["n"] += 1
        return float(v[0]) ** 3

    d, _fp, _fm = central_fd(g, [2.0], 0, 1e-4)
    rel = abs(d - 12.0) / 12.0
    return {"derivative": d, "expected": 12.0, "rel_err": rel,
            "pass": bool(rel < 1e-8), "calls": calls["n"]}


def clearance_from_fd(fp, fm, eta=ETA_INHERITED):
    """C_measured := |f(x+s) - f(x-s)| / eta.

    Computed from the MEASURED primal difference, never from the analytic under
    test.  Algebraically identical to arm O's |J_fd| * 2s / eta and free of the
    circularity of clearing a gradient against itself.
    """
    return abs(fp - fm) / float(eta)


def eta_from_series(cd_series, n_last=5):
    """Peak-to-peak of the last `n_last` printed samples.

    D1 Amendment 2 A2.2's registered definition, reused here at GRADING time
    only, on the CD samples this arm's own log prints at `printInterval 10`.
    It sizes NOTHING -- every step in this item is inherited -- and exists so
    that the endpoint's own noise floor, which D1 section 5.3 recorded it could
    not measure, is at least OBSERVED and reported beside the inherited eta.
    """
    tail = list(cd_series)[-int(n_last):]
    if len(tail) < 2:
        return None
    return max(tail) - min(tail)


def grade(rel_err, sign_flip):
    """DAFOAM_CHARTER.md section 2 band, per component."""
    if sign_flip:
        return "GATE FAIL"
    if rel_err <= 0.05:
        return "PASS"
    if rel_err <= 0.15:
        return "CONDITIONAL"
    return "GATE FAIL"


# ---- CLI: the zero-compute controls, runnable on the HOST -------------------

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        r = selftest_cubic()
        print("D1C_SELFTEST_CUBIC %s" % json.dumps(r, sort_keys=True),
              flush=True)
        raise SystemExit(0 if r["pass"] else 2)
    if len(sys.argv) > 3 and sys.argv[1] == "plantcheck":
        try:
            planted_zero_control(sys.argv[2], sys.argv[3])
        except Refuse:
            raise SystemExit(2)
        raise SystemExit(0)
    if len(sys.argv) > 3 and sys.argv[1] == "negcheck":
        r = negative_control(sys.argv[2], sys.argv[3])
        raise SystemExit(0 if r["pass"] else 2)
    if len(sys.argv) > 3 and sys.argv[1] == "keycheck":
        r = keyset_control(sys.argv[2], sys.argv[3])
        raise SystemExit(0 if r["pass"] else 2)
    print("usage: d1c_endpoint.py selftest | plantcheck SRC WORKDIR | "
          "negcheck SRC WORKDIR | keycheck SRC WORKDIR")
    raise SystemExit(2)
