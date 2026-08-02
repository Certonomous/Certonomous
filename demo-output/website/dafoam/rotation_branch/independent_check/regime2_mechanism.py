"""Is catastrophic cancellation THE cause of the second regime, or only present in it?

CONTEXT. `regime2_vs_angle.py` (2026-08-01) measured the shipped
`GETROTATIONMATRIX3D_B` against the true derivative as a function of tilt angle
and located the band at `vectorUtils_b.f90:133`,
`argb = -(angleb/SQRT(1.0-arg**2))`, attributing it to cancellation in
`1 - arg**2`. That is a LOCATION plus an ASSERTED mechanism: the line was
identified, the cancellation was never tested as the cause. ROOTCAUSE §6.4
states it as fact. This script tests it.

THE DISCRIMINATOR. `1 - arg**2` is mathematically `sin(angle)**2`, and
`sin(angle)` is available in the primal at full relative accuracy without any
subtraction:

    sin(angle) = |v1 x v2| / (|v1| |v2|)  =  axisMag / (magv1 * magv2)

and `axisMag` is ALREADY COMPUTED two lines earlier in the primal (it is what
normalises `axis`). So the substitution is free. Four variants of the reverse
routine, differing only in how the small quantities are formed:

  V0  shipped                 arg = v1.v2 ; angle = acos(arg) ; sqrt(1-arg^2)
  V1  sin from cross product  as V0, but sqrt(1-arg^2) -> axisMag/(magv1*magv2)
  V2  V1 + accurate angle     angle = atan2(axisMag, dot) as well
  V3  singularity-free form   §1.7's reparameterisation, reverse-differentiated

Reading:
  * V1 collapses the band  -> the cancellation in `1 - arg**2` IS the cause and
    the fix is one line, on a quantity the primal already has.
  * V1 does not, V2 does   -> the cause is the `acos` construction as a whole
    (the ANGLE is inaccurate, not just its derivative's denominator), and
    ROOTCAUSE §6.4's attribution to line 133 alone is too narrow.
  * neither                -> cancellation is ruled out as the cause.

PART B measures the cancellation directly, independent of any derivative:
`1 - arg**2` as computed against `sin(angle)**2` exactly.

No solver, no IDWarp, no DAFoam: numpy only, same as its siblings in this
directory.
"""
import numpy as np

TOL = 1.4901161193847656e-08   # vectorUtils.f90:44, = sqrt(eps)


def getmag(v):
    return np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2 + 1e-30)


def skew(w):
    return np.array([[0., -w[2], w[1]], [w[2], 0., -w[0]], [-w[1], w[0], 0.]])


def cross3(v1, v2):
    return np.array([v1[1] * v2[2] - v1[2] * v2[1],
                     v1[2] * v2[0] - v1[0] * v2[2],
                     v1[0] * v2[1] - v1[1] * v2[0]])


def getmag_b(v, vb, magb):
    s = v[0] ** 2 + v[1] ** 2 + v[2] ** 2 + 1e-30
    tempb = 0.0 if s == 0.0 else magb / (2.0 * np.sqrt(s))
    vb = vb.copy()
    vb += 2 * v * tempb
    return vb


def cross_b(v1, v1b, v2, v2b, crossb):
    v1b = v1b.copy(); v2b = v2b.copy(); cb = crossb.copy()
    v1b[0] += v2[1] * cb[2] - v2[2] * cb[1]
    v2b[1] += v1[0] * cb[2] - v1[2] * cb[0]
    v1b[1] += v2[2] * cb[0] - v2[0] * cb[2]
    v2b[0] += v1[2] * cb[1] - v1[1] * cb[2]
    cb[2] = 0.0
    v1b[2] += v2[0] * cb[1] - v2[1] * cb[0]
    v2b[2] += v1[1] * cb[0] - v1[0] * cb[1]
    return v1b, v2b


def getrotationmatrix3d_b(v1, v2, mib, variant="V0"):
    """GETROTATIONMATRIX3D_B, vectorUtils_b.f90:7-154, with ONE line varied.

    variant V0 is the faithful transcription used by regime2_vs_angle.py; V1 and
    V2 differ only in the marked lines. Everything else is byte-for-byte the
    same code path, so any difference in the answer is attributable.
    """
    magv1 = getmag(v1); magv2 = getmag(v2)
    axis_raw = cross3(v1, v2); axismag = getmag(axis_raw)
    if axismag < TOL:
        angle = 0.0; axis_saved = axis_raw.copy()
        axis = np.array([1., 0., 0.]); branch = 0; minbranch = None; arg = None
    else:
        axis_saved = axis_raw.copy()
        axis = axis_raw / axismag
        vv1 = v1 / magv1; vv2 = v2 / magv2
        dot = vv1[0] * vv2[0] + vv1[1] * vv2[1] + vv1[2] * vv2[2]
        if 1.0 > dot: arg = dot; minbranch = 0
        else:         arg = 1.0; minbranch = 1
        if variant in ("V2", "V1b"):
            # <<< accurate angle: atan2(|v1 x v2|, v1.v2) on the unit vectors.
            angle = np.arctan2(axismag / (magv1 * magv2), arg)
        else:
            angle = np.arccos(arg)                                   # shipped
        branch = 1
    a = skew(axis); c = a @ a
    ab = np.sin(angle) * mib; cb = (1.0 - np.cos(angle)) * mib
    angleb = np.cos(angle) * np.sum(a * mib) + np.sin(angle) * np.sum(c * mib)
    ab[2, 0] += a[0, 2] * cb[2, 2] + a[0, 1] * cb[2, 1] + (a[0, 0] + a[2, 2]) * cb[2, 0] + a[1, 2] * cb[1, 0] + a[0, 2] * cb[0, 0]
    ab[0, 2] += a[2, 0] * cb[2, 2] + a[1, 0] * cb[1, 2] + (a[0, 0] + a[2, 2]) * cb[0, 2] + a[2, 1] * cb[0, 1] + a[2, 0] * cb[0, 0]
    ab[2, 1] += a[1, 2] * cb[2, 2] + (a[1, 1] + a[2, 2]) * cb[2, 1] + a[1, 0] * cb[2, 0] + a[1, 2] * cb[1, 1] + a[0, 2] * cb[0, 1]
    ab[1, 2] += a[2, 1] * cb[2, 2] + (a[1, 1] + a[2, 2]) * cb[1, 2] + a[2, 1] * cb[1, 1] + a[2, 0] * cb[1, 0] + a[0, 1] * cb[0, 2]
    ab[0, 1] += a[2, 0] * cb[2, 1] + a[1, 0] * cb[1, 1] + a[1, 2] * cb[0, 2] + (a[0, 0] + a[1, 1]) * cb[0, 1] + a[1, 0] * cb[0, 0]
    ab[0, 0] += a[2, 0] * cb[2, 0] + a[1, 0] * cb[1, 0] + a[0, 2] * cb[0, 2] + a[0, 1] * cb[0, 1] + 2 * a[0, 0] * cb[0, 0]
    ab[1, 0] += a[2, 1] * cb[2, 0] + a[0, 2] * cb[1, 2] + a[0, 1] * cb[1, 1] + (a[0, 0] + a[1, 1]) * cb[1, 0] + a[0, 1] * cb[0, 0]
    axisb = np.zeros(3)
    axisb[0] += ab[2, 1] - ab[1, 2]
    axisb[1] += ab[0, 2] - ab[2, 0]
    axisb[2] += ab[1, 0] - ab[0, 1]
    v2b = np.zeros(3)
    if branch == 0:
        magv2b = 0.0; axisb = np.zeros(3); axismagb = 0.0
    else:
        if arg == 1.0 or arg == -1.0:
            argb = 0.0
        elif variant in ("V1", "V2"):
            # <<< THE ONE LINE. sqrt(1-arg**2) is sin(angle), and sin(angle) is
            #     axisMag/(magv1*magv2) -- already computed, no subtraction.
            argb = -(angleb / (axismag / (magv1 * magv2)))
        else:
            argb = -(angleb / np.sqrt(1.0 - arg ** 2))               # line 133
        vv2b = np.zeros(3)
        if minbranch == 0:
            vv2b += (v1 / magv1) * argb
        v2b = v2b + vv2b / magv2
        magv2b = -(np.sum(v2 * vv2b) / magv2 ** 2)
        axismagb = -(np.sum(axis_saved * axisb) / axismag ** 2)
        axisb = axisb / axismag
    axisb = getmag_b(axis_saved, axisb, axismagb)
    v1b = np.zeros(3)
    v1b, v2b = cross_b(v1, v1b, v2, v2b, axisb)
    v2b = getmag_b(v2, v2b, magv2b)
    return v2b


def Msf(a, b):
    """§1.7's singularity-free form, R = I + [v]x + [v]x^2/(1+c)."""
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b)
    v = cross3(a, b); c = float(np.dot(a, b)); V = skew(v)
    return np.eye(3) + V + V @ V / (1.0 + c)


def v2b_singfree(v1, v2, mib):
    """V3: hand reverse of Msf w.r.t. v2, in double precision, no acos, no sqrt.

    d/dv2 of sum(mib * (I + V + V V /(1+c))) with V = skew(a x b), c = a.b,
    a = v1/|v1|, b = v2/|v2|.  Written as a forward-over-directional sweep in
    exact closed form is fiddly; the map is a rational function of b with no
    cancellation anywhere for c > -1, so a complex-step derivative is exact to
    machine precision and is used instead. Complex step has no subtraction and
    therefore no cancellation -- which is the point.
    """
    a = v1 / np.linalg.norm(v1)
    g = np.zeros(3)
    for k in range(3):
        e = np.zeros(3); e[k] = 1.0
        h = 1e-30
        z = (v2 + 1j * h * e).astype(complex)
        b = z / np.sqrt(np.sum(z * z))
        vv = np.array([a[1] * b[2] - a[2] * b[1],
                       a[2] * b[0] - a[0] * b[2],
                       a[0] * b[1] - a[1] * b[0]])
        c = np.sum(a * b)
        V = np.array([[0, -vv[2], vv[1]], [vv[2], 0, -vv[0]], [-vv[1], vv[0], 0]])
        M = np.eye(3) + V + V @ V / (1.0 + c)
        g[k] = np.imag(np.sum(mib * M)) / h
    return g


def truth_v2b(v1, v2, mib):
    """Richardson FD of the smooth map -- the same reference regime2_vs_angle used."""
    g = np.zeros(3)
    for k in range(3):
        e = np.zeros(3); e[k] = 1.0

        def J(t):
            return float(np.sum(mib * Msf(v1, v2 + t * e)))
        h = 1e-3
        g1 = (J(h) - J(-h)) / (2 * h); g2 = (J(h / 2) - J(-h / 2)) / h
        g[k] = (4 * g2 - g1) / 3.0
    return g


ANGLES = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 5e-8, 3e-8, 2e-8, 1e-8, 0.0]

np.random.seed(3)   # same seed and same mib as regime2_vs_angle.py
v1 = np.array([0., 0., 1.])
mib = np.random.randn(3, 3)

print("PART A -- which line carries the second regime?")
print("v1 = z, v2 tilted by theta about y, same fixed random mib as regime2_vs_angle.py.")
print("Relative error of ||v2b|| against the true derivative of the smooth map.")
print()
print("  V1  = denominator only   (sqrt(1-arg^2) -> axisMag/(magv1*magv2))")
print("  V1b = angle only         (acos(arg) -> atan2(axisMag/(magv1*magv2), arg))")
print("  V2  = both")
print()
print("  theta       branch     V0 shipped   V1 denom only  V1b angle only  V2 both        V3 singfree")
print("  " + "-" * 100)
rows = []
for th in ANGLES:
    v2 = np.array([np.sin(th), 0., np.cos(th)])
    tru = truth_v2b(v1, v2, mib)
    ntru = np.linalg.norm(tru)
    axismag = getmag(cross3(v1, v2))
    br = "guard(0)" if axismag < TOL else "live(1) "
    errs = []
    for var in ("V0", "V1", "V1b", "V2"):
        got = getrotationmatrix3d_b(v1, v2, mib.copy(), variant=var)
        errs.append(np.linalg.norm(got - tru) / max(ntru, 1e-300))
    got3 = v2b_singfree(v1, v2, mib)
    errs.append(np.linalg.norm(got3 - tru) / max(ntru, 1e-300))
    rows.append((th, br, errs))
    print(f"  {th:<11.0e} {br}  {errs[0]:<12.3e} {errs[1]:<14.3e} {errs[2]:<15.3e} {errs[3]:<14.3e} {errs[4]:.3e}")

print()
print("PART B -- the cancellation itself, measured without any derivative.")
print("1 - arg**2 as the shipped code forms it, against sin(theta)**2 exactly.")
print()
print("  theta       1-arg**2 computed      sin(theta)**2 exact     rel err     ulps in arg")
print("  " + "-" * 88)
for th in ANGLES:
    if th == 0.0:
        continue
    v2 = np.array([np.sin(th), 0., np.cos(th)])
    vv1 = v1 / getmag(v1); vv2 = v2 / getmag(v2)
    dot = float(np.dot(vv1, vv2))
    arg = min(1.0, dot)
    comp = 1.0 - arg ** 2
    exact = np.sin(th) ** 2
    rel = abs(comp - exact) / exact if exact > 0 else float("nan")
    # how many ulps of arg does the exact answer sit away from 1.0?
    ulp = np.spacing(1.0)
    n_ulp = (1.0 - np.cos(th)) / ulp
    print(f"  {th:<11.0e} {comp:<22.16e} {exact:<23.16e} {rel:<11.3e} {n_ulp:.2e}")

print()
print("PART C -- and the substitute is accurate: axisMag/(magv1*magv2) vs sin(theta).")
print()
print("  theta       axisMag/(|v1||v2|)      sin(theta) exact        rel err")
print("  " + "-" * 74)
for th in ANGLES:
    if th == 0.0:
        continue
    v2 = np.array([np.sin(th), 0., np.cos(th)])
    axismag = getmag(cross3(v1, v2))
    sub = axismag / (getmag(v1) * getmag(v2))
    exact = np.sin(th)
    print(f"  {th:<11.0e} {sub:<23.16e} {exact:<23.16e} {abs(sub - exact) / exact:.3e}")

print()
print("PART D -- does the substitution survive a general orientation, not just")
print("the one tilt plane above? 200 random (v1, mib, tilt axis) draws per angle;")
print("worst relative error over the draws.")
print()
print("  theta       n live   V0 shipped     V1 denom only   V2 both         V2 improvement")
print("  " + "-" * 88)
rng = np.random.default_rng(11)
for th in [1e-4, 1e-5, 1e-6, 1e-7, 5e-8, 3e-8, 2e-8]:
    w0 = w1 = w2 = 0.0
    nlive = 0
    for _ in range(200):
        a = rng.standard_normal(3); a /= np.linalg.norm(a)
        k = rng.standard_normal(3); k -= a * np.dot(a, k); k /= np.linalg.norm(k)
        b = np.cos(th) * a + np.sin(th) * k          # exactly theta from a
        m = rng.standard_normal((3, 3))
        if getmag(cross3(a, b)) < TOL:
            continue            # guard branch: regime 1, not what this measures
        nlive += 1
        tru = truth_v2b(a, b, m); nt = np.linalg.norm(tru)
        if nt < 1e-12:
            continue
        e0 = np.linalg.norm(getrotationmatrix3d_b(a, b, m.copy(), "V0") - tru) / nt
        e1 = np.linalg.norm(getrotationmatrix3d_b(a, b, m.copy(), "V1") - tru) / nt
        e2 = np.linalg.norm(getrotationmatrix3d_b(a, b, m.copy(), "V2") - tru) / nt
        w0 = max(w0, e0); w1 = max(w1, e1); w2 = max(w2, e2)
    print(f"  {th:<11.0e} {nlive:<8d} {w0:<14.3e} {w1:<15.3e} {w2:<15.3e} {w0 / max(w2, 1e-300):.3g}x")

print()
print("PART E -- what the angle change does to the PRIMAL.")
print("A fix that moves the forward warp is a different mesh, not a fix. Mi built")
print("with acos(arg) against Mi built with atan2(axisMag/(|v1||v2|), arg),")
print("max |difference| over the whole 3x3, 500 random pairs per angle.")
print()
print("  theta       max|Mi_acos - Mi_atan2|   as ulps of 1.0")
print("  " + "-" * 56)


def Mi(v1, v2, accurate_angle):
    magv1 = getmag(v1); magv2 = getmag(v2)
    ax = cross3(v1, v2); axismag = getmag(ax)
    if axismag < TOL:
        angle = 0.0; axis = np.array([1., 0., 0.])
    else:
        axis = ax / axismag
        arg = min(1.0, float(np.dot(v1 / magv1, v2 / magv2)))
        angle = (np.arctan2(axismag / (magv1 * magv2), arg) if accurate_angle
                 else np.arccos(arg))
    A = skew(axis); C = A @ A
    return np.eye(3) + np.sin(angle) * A + (1.0 - np.cos(angle)) * C


rng = np.random.default_rng(29)
for th in [1.0, 1e-1, 1e-2, 1e-4, 1e-6, 1e-7, 5e-8, 2e-8]:
    worst = 0.0
    for _ in range(500):
        a = rng.standard_normal(3); a /= np.linalg.norm(a)
        k = rng.standard_normal(3); k -= a * np.dot(a, k); k /= np.linalg.norm(k)
        b = np.cos(th) * a + np.sin(th) * k
        worst = max(worst, np.abs(Mi(a, b, False) - Mi(a, b, True)).max())
    print(f"  {th:<11.0e} {worst:<25.3e} {worst / np.spacing(1.0):.1f}")
