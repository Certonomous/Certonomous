"""D1 endpoint finite-difference driver.

Frozen algorithm, per
cases/dafoam/ladder-a/A1/curriculum_D1/PREREGISTRATION.md sections 4.2 and 6/G3.

NOT EDITED AFTER THE FIRST LAUNCH.  An edit voids every arm that ran before it.

The step for a component is a function of |J_adj| and eta ONLY.  No finite
difference value ever enters the choice of a step.
"""
import copy
import json
import os

import numpy as np

# ---- frozen constants (PREREGISTRATION.md section 6, gate G3) ---------------
SHAPE_LADDER = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2]
PATCHV_LADDER = [1e-3, 3e-3, 1e-2, 3e-2, 1e-1]
SHAPE_FLOOR = 1e-4     # A1's own measured roundoff branch
PATCHV_FLOOR = 1e-3
CMIN = 5.0             # clearance requirement
RATIO = 3.0            # s_hi >= 3 * s_lo
PLATEAU_TOL = 0.10     # two-step agreement tolerance
TRIVIAL_STEP = 1e-8    # gate G4, charter section 4
PLANT = 1.234e-03      # gate G5, CLAUDE.md rule 3

NAMED = [("shape", 6), ("shape", 1), ("shape", 5), ("patchV", 1)]


def clearance(J, s, eta):
    """C(s) = |J| * 2s / eta."""
    return abs(float(J)) * 2.0 * float(s) / float(eta)


def pick_steps(J, eta, dv):
    """Return (s_lo, s_hi, C_lo, C_hi) by the frozen mechanical rule."""
    ladder = SHAPE_LADDER if dv == "shape" else PATCHV_LADDER
    floor = SHAPE_FLOOR if dv == "shape" else PATCHV_FLOOR
    s_lo = None
    for s in ladder:
        if s >= floor and clearance(J, s, eta) >= CMIN:
            s_lo = s
            break
    if s_lo is None:
        return None, None, None, None
    # The registered rule is exact arithmetic: s_hi := smallest rung with
    # s_hi >= 3*s_lo, and 3e-4 >= 3*1e-4 EXACTLY.  In binary floating point
    # 3*1e-4 = 3.0000000000000004e-04 > the 3e-4 literal, which would skip the
    # rung the rule selects.  The relative tolerance below implements the
    # registered mathematics; it does not change the rule.
    s_hi = None
    for s in ladder:
        if s >= RATIO * s_lo * (1.0 - 1e-9):
            s_hi = s
            break
    if s_hi is None:
        return s_lo, None, clearance(J, s_lo, eta), None
    return s_lo, s_hi, clearance(J, s_lo, eta), clearance(J, s_hi, eta)


def central_fd(f, x, i, s, restore=None):
    """(f(x + s e_i) - f(x - s e_i)) / (2 s).

    Exactly two evaluations, which is the registered budget (18 perturbed
    primals for 4 components x 2 steps x 2 signs plus the trivial baseline).
    The design vector is put back by `restore`, which SETS values and does not
    solve; the following solve warm-starts from the last perturbed state, which
    is exactly what `check_totals` itself does across its 20 perturbations.
    """
    x = np.array(x, dtype=float)
    xp = x.copy()
    xp[i] = xp[i] + s
    fp = f(xp)
    xm = x.copy()
    xm[i] = xm[i] - s
    fm = f(xm)
    if restore is not None:
        restore(x)
    return (fp - fm) / (2.0 * s), fp, fm


# ---- zero-compute instrument controls, run before any container starts ------
def selftest_cubic():
    """The difference kernel must differentiate a cubic."""
    f = lambda v: float(v[0]) ** 3
    x = np.array([2.0])
    calls = {"n": 0}

    def g(v):
        calls["n"] += 1
        return f(v)

    d, fp, fm = central_fd(g, x, 0, 1e-4)
    rel = abs(d - 12.0) / 12.0
    return {"derivative": d, "expected": 12.0, "rel_err": rel,
            "pass": bool(rel < 1e-8), "calls": calls["n"]}


def read_endpoint(path):
    with open(path) as fh:
        return json.load(fh)


def planted_zero_control(path, plant=PLANT):
    """CLAUDE.md rule 3.  A zero from a reader not shown able to see a
    non-zero is not evidence.  Refuses (exit 2) if the plant is invisible."""
    base = read_endpoint(path)
    pert = copy.deepcopy(base)
    pert["CD_final"] = base["CD_final"] + plant
    pert["shape"] = [v + plant for v in base["shape"]]
    tmp = path + ".plant"
    with open(tmp, "w") as fh:
        json.dump(pert, fh)
    back = read_endpoint(tmp)
    d_cd = back["CD_final"] - base["CD_final"]
    d_sh = max(abs((b - a) - plant) for a, b in zip(base["shape"], back["shape"]))
    os.remove(tmp)
    seen = (abs(d_cd - plant) < 1e-12) and (d_sh < 1e-12)
    out = {"plant": plant, "read_back_delta_CD": d_cd,
           "max_shape_residual": d_sh, "pass": bool(seen)}
    if not seen:
        print("D1_G5_PLANTED_ZERO REFUSE", json.dumps(out), flush=True)
        raise SystemExit(2)
    print("D1_G5_PLANTED_ZERO OK", json.dumps(out), flush=True)
    return out


def eta_from_series(cd_series, n_last):
    """Peak-to-peak of the last n_last samples."""
    tail = cd_series[-n_last:]
    if len(tail) < 2:
        return None
    return max(tail) - min(tail)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        r = selftest_cubic()
        print("D1_SELFTEST_CUBIC", json.dumps(r), flush=True)
        raise SystemExit(0 if r["pass"] else 2)
    if len(sys.argv) > 2 and sys.argv[1] == "plantcheck":
        planted_zero_control(sys.argv[2])
        raise SystemExit(0)
