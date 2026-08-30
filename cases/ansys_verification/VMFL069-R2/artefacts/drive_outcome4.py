#!/usr/bin/env python3
"""OUTCOME-4 DETECTOR DRIVE -- prove check_alpha_stationary and check_x_invariance
are STRUCTURALLY CAPABLE OF REFUSING, against R1's REAL diverged data.

Nothing here writes into cases/ or verification/runs/. R1's bytes are COPIED, never
touched. Every perturbation is planted ON DISK and read back through the PRODUCTION
readers (CLAUDE.md rule 3). The functions driven are imported from the frozen
comparator itself -- not reimplemented.
"""
import contextlib
import io
import importlib.util
import os
import shutil
import sys
import tempfile

CASE = "/home/ubuntu/Certonomous/cases/ansys_verification/VMFL069-R2"
R1_ALPHA = ("/home/ubuntu/Certonomous/verification/runs/ansys_verification/"
            "VMFL069/L1/0/alpha.fluid1")

spec = importlib.util.spec_from_file_location("g", os.path.join(CASE, "grade_vmfl069_r2.py"))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

WORK = tempfile.mkdtemp(prefix="outcome4_")
results = []


def arm(name, expect_refuse, fn):
    """Run one arm. `fn` returns (value_or_None, refusal_text_or_None)."""
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            val = fn()
        got, text = False, None
    except SystemExit:                            # the comparator's SystemExit2
        val, got, text = None, True, err.getvalue().strip()
    ok = (got == expect_refuse)
    results.append((name, expect_refuse, got, ok, text, val))
    print("[%s] %-58s expect_refuse=%-5s got=%-5s" % ("OK " if ok else "BAD", name,
                                                      expect_refuse, got))
    if text:
        print("        REFUSAL TEXT: %s" % text.replace("\n", " "))
    elif val is not None:
        print("        returned: %r" % (val,))
    return ok


# ---------------------------------------------------------------- geometry ----
cx, cy = g._centres("L1")
print("registered L1 centres: %d cells, %d distinct y-rows, %d distinct x-cols"
      % (len(cy), len(set(round(v, 12) for v in cy)), len(set(round(v, 12) for v in cx))))
print("R1 real alpha source : %s" % R1_ALPHA)
print("            sha256   : %s" % __import__("hashlib").sha256(
    open(R1_ALPHA, "rb").read()).hexdigest())
print("frozen thresholds    : ALPHA_TOL=%g  XINVAR_TOL=%g  REF_WHOLE=%.12g"
      % (g.ALPHA_TOL, g.XINVAR_TOL, g.REF_WHOLE))
print()


def alpha_arm(delta, writer=None):
    """Copy R1's REAL bytes, plant `delta` on disk with the production planter,
    read back with the production reader, drive the production detector."""
    p = os.path.join(WORK, "alpha_%s" % abs(hash((delta, writer is not None))))
    shutil.copyfile(R1_ALPHA, p)
    (writer or g._plant_internal_scalar)(p, delta)
    a = g.read_internal_scalar(p, "R1 real alpha, planted %g" % delta)
    return g.check_alpha_stationary(cy, a)


def blind_scalar(path, delta):
    """NEGATIVE ARM: a writer that writes NOTHING. If the detector still refuses,
    the refusal did not come from the disk bytes."""
    return None


def x_arm(col_delta, writer=True):
    """Build the exact x-invariant solution on the registered L1 mesh, write it to
    disk in the production format, perturb ONE x-column on disk, read it back with
    the production reader, drive the production detector."""
    p = os.path.join(WORK, "U_%s" % abs(hash((col_delta, writer))))
    ux = [g.exact_u(y) for y in cy]
    g._write_vector_x(p, "U", ux)
    if writer:                                    # plant on disk, in place
        txt = open(p).read()
        xs = sorted(set(round(v, 12) for v in cx))
        target = xs[0]
        vals = [u + (col_delta if round(x, 12) == target else 0.0)
                for x, u in zip(cx, ux)]
        g._write_vector_x(p, "U", vals)
    back = g.read_internal_vector_x(p, "U planted %g" % col_delta)
    return g.check_x_invariance(cx, cy, back)


X_ABS = g.XINVAR_TOL * abs(g.REF_WHOLE)           # spread in m/s at the threshold
# R1's logged extremes, read from verification/runs/.../VMFL069/L1/log.interFoam
R1_ALPHA_MIN = -2.36630181882e+23                 # Min(alpha.fluid1) at t=68
R1_COURANT_MAX = 2869282454.01                    # convective Courant max at t=68
R1_UX = R1_COURANT_MAX * 0.25 / 1.0               # dx=0.25 m, deltaT=1 s -> m/s

print("=== ALPHA CHANNEL -- R1's REAL 256-value setFields bytes ===")
ok = True
ok &= arm("A0 CONTROL   unperturbed R1 bytes", False, lambda: alpha_arm(0.0))
ok &= arm("A1 NEAR-MISS below 1e-9 (9.0e-10)", False, lambda: alpha_arm(9.0e-10))
ok &= arm("A2 NEAR-MISS above 1e-9 (1.1e-9)", True, lambda: alpha_arm(1.1e-9))
ok &= arm("A3 R1 REAL   Min(alpha) = -2.3663e+23", True, lambda: alpha_arm(R1_ALPHA_MIN))
ok &= arm("A4 BLIND     writer writes nothing", False,
          lambda: alpha_arm(R1_ALPHA_MIN, writer=blind_scalar))

print()
print("=== X-INVARIANCE CHANNEL -- exact solution on the registered L1 mesh, "
      "perturbed at R1's LOGGED magnitude ===")
print("    threshold in m/s = XINVAR_TOL * REF_WHOLE = %.12g" % X_ABS)
print("    R1 logged Courant max %.6g at deltaT 1 s, dx 0.25 m -> |u_x| = %.6g m/s"
      % (R1_COURANT_MAX, R1_UX))
ok &= arm("X0 CONTROL   pure exact solution", False, lambda: x_arm(0.0, writer=False))
ok &= arm("X1 NEAR-MISS below threshold (0.9x)", False, lambda: x_arm(0.9 * X_ABS))
ok &= arm("X2 NEAR-MISS above threshold (1.1x)", True, lambda: x_arm(1.1 * X_ABS))
ok &= arm("X3 R1 REAL   u_x = 7.173e+08 m/s", True, lambda: x_arm(R1_UX))
ok &= arm("X4 BLIND     no perturbation written", False, lambda: x_arm(R1_UX, writer=False))

print()
texts = [t for n, _e, gt, _o, t, _v in results if gt and t]
distinct = len(set(t.split(":")[1].split(".")[0] for t in texts))
print("=== REFUSAL-TEXT DIFFERENCE ===")
print("    %d refusals fired, %d distinct refusal headings" % (len(texts), distinct))
for t in sorted(set(t for t in texts)):
    print("      - %s" % t[:110])
ok &= (distinct >= 2)

print()
bad = [n for n, _e, _g, o, _t, _v in results if not o]
print("ARMS: %d run, %d as registered, %d WRONG %s"
      % (len(results), len(results) - len(bad), len(bad), bad or ""))
shutil.rmtree(WORK, ignore_errors=True)
sys.exit(0 if ok and not bad else 1)
