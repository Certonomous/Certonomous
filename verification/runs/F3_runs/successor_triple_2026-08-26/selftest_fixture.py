#!/usr/bin/env python3
"""Synthetic run trees that drive the WHOLE grading path before any compute.

This exists so the grader is exercised END TO END pre-compute -- the F11 `C4`
lesson: six registered runs that would all have graded NOT A RESULT on an
instrument defect nobody drove first. Every artifact the real path reads is
written here in the real format, so a scenario that reaches a verdict here
reaches it for the same reasons on real output.
"""
import os
import json
import shutil
import numpy as np

LOG_HEAD = """/*---------------------------------------------------------------------------*\\
| Build  : synthetic-fixture                                                  |
\\*---------------------------------------------------------------------------*/
"""
STEP = """Mean and max Courant Numbers = 0.1 0.2
Time = %s

diagonal:  Solving for rho, Initial residual = 0, Final residual = 0, No Iterations 0
diagonal:  Solving for rhoUx, Initial residual = 0, Final residual = 0, No Iterations 0
diagonal:  Solving for rhoUy, Initial residual = 0, Final residual = 0, No Iterations 0
diagonal:  Solving for rhoE, Initial residual = 0, Final residual = 0, No Iterations 0
ExecutionTime = %s s  ClockTime = %s s

"""


def write_log(case_dir, n_steps, end_time, iterative_ok=True):
    body = [LOG_HEAD]
    for i in range(n_steps):
        t = end_time * (i + 1) / n_steps
        if iterative_ok:
            body.append(STEP % ("%.7g" % t, "%.2f" % (i * 0.02), "%d" % int(i * 0.02)))
        else:
            body.append(STEP.replace(
                "diagonal:  Solving for rho, Initial residual = 0, Final residual = 0, No Iterations 0",
                "smoothSolver:  Solving for rho, Initial residual = 1e-2, Final residual = 3.5e-2, No Iterations 4"
            ) % ("%.7g" % t, "%.2f" % (i * 0.02), "%d" % int(i * 0.02)))
    body.append("End\n")
    open(os.path.join(case_dir, "log.rhoCentralFoam"), "w").write("".join(body))


def write_series(case_dir, quantity, end_time, final, drift_frac=0.0, n=400):
    """A plateau series: `n` samples, the final 25% holding well over the floor."""
    t = np.linspace(0.0, end_time, n)
    v = np.full(n, float(final))
    if drift_frac:
        v = final * (1.0 + drift_frac * t / end_time)
        v = v - (v[-1] - final)          # keep the final value exactly `final`
    json.dump(dict(t=t.tolist(), v=v.tolist(), end_time=end_time),
              open(os.path.join(case_dir, "series_%s.json" % quantity), "w"))


def make_wedge_level(root, pair, level, p_target, beta_target, end_time=2.6,
                     drift=0.0, iterative_ok=True, Lramp=1.0):
    d = os.path.join(root, "wedge", pair, level)
    os.makedirs(os.path.join(d, "postProcessing", "surfaceSampleDict", "%g" % end_time),
                exist_ok=True)
    json.dump(dict(Lramp=Lramp, H=0.994, M=2.5, c=1.0), open(os.path.join(d, "meta.json"), "w"))
    # raw patch sample: x y z p -- the masked mean over 0.3..0.85 Lramp must be p_target
    xs = np.linspace(0.0, Lramp, 240)
    p = np.full_like(xs, p_target)
    p[(xs <= 0.3 * Lramp) | (xs >= 0.85 * Lramp)] = p_target * 0.5   # outside the mask
    raw = np.column_stack([xs, np.zeros_like(xs), np.zeros_like(xs), p])
    np.savetxt(os.path.join(d, "postProcessing", "surfaceSampleDict",
                            "%g" % end_time, "wedgeSurface_p.raw"),
               raw, header="x y z p")
    # shock locus whose 5-station fit gives beta_target
    m = np.tan(np.radians(beta_target))
    xk = np.linspace(0.1, 0.9, 6) * Lramp
    pts = np.column_stack([xk, m * xk])
    json.dump(dict(beta_computed_deg=beta_target, shock_pts=pts.tolist(),
                   endTime=end_time), open(os.path.join(d, "result.json"), "w"))
    write_log(d, 200, end_time, iterative_ok)
    write_series(d, "p_wall_mean", end_time, p_target, drift)
    write_series(d, "beta_deg", end_time, beta_target, drift)
    return d


def make_diamond_level(root, pair, level, cd_target, end_time=6.0, drift=0.0,
                       iterative_ok=True):
    d = os.path.join(root, "diamond", pair, level)
    os.makedirs(os.path.join(d, "postProcessing", "forces1", "0"), exist_ok=True)
    M, c, z = 2.5, 1.0, 0.01
    json.dump(dict(M=M, c=c), open(os.path.join(d, "meta.json"), "w"))
    q1 = 0.5 * 1.4 * 1.0 * M ** 2
    fx = cd_target * q1 * c * z / 2.0
    with open(os.path.join(d, "postProcessing", "forces1", "0", "force.dat"), "w") as f:
        f.write("# Force\n# Time total_x total_y total_z\n")
        for i in range(3):
            f.write("%.6f %.12e 0 0\n" % (end_time * (i + 1) / 3.0, fx))
    json.dump(dict(endTime=end_time), open(os.path.join(d, "result.json"), "w"))
    write_log(d, 200, end_time, iterative_ok)
    write_series(d, "cd", end_time, cd_target, drift)
    return d


def build(root, wedge_p, wedge_beta, diamond_cd, drift=0.0, iterative_ok=True):
    """wedge_p / wedge_beta / diamond_cd are (coarse, medium, fine) triples."""
    if os.path.exists(root):
        shutil.rmtree(root)
    for i, lvl in enumerate(("coarse", "medium", "fine")):
        make_wedge_level(root, "M2.5_th10", lvl, wedge_p[i], wedge_beta[i],
                         drift=drift, iterative_ok=iterative_ok)
        make_diamond_level(root, "M2.5_eps5", lvl, diamond_cd[i],
                           drift=drift, iterative_ok=iterative_ok)
    return root
