#!/usr/bin/env python3
"""
Derive T9a's reference constants instead of transcribing them.

The pre-registration (docs/campaigns/T-family/T9a_PREREGISTRATION.md) claims
this rung's references CANNOT be wrong because they are closed form.  That
claim is only worth something if the constants are reproduced here from the
governing equations, TWICE, by routes that share no code:

  T9a-1  composite wall, three layers in series, fixed face temperatures.
         Route A: the series-resistance closed form, q'' = dT / sum(L/k).
         Route B: a finite-volume solve of d/dx(k dT/dx) = 0 with harmonic
                  face conductances on a fine mesh, by the Thomas algorithm.
         For piecewise-constant k with interfaces on faces the FV solution is
         exact up to round-off, so the two must agree to ~1e-10.

  T9a-2  straight rectangular fin, adiabatic tip, Robin faces.
         Route A: eta = tanh(mL)/mL and theta(L)/theta_b = 1/cosh(mL) with
                  m = sqrt(2h/(k t)).
         Route B: a second-order finite-difference solve of theta'' = m^2
                  theta, theta(0)=1, theta'(L)=0, with eta formed from the
                  Simpson integral of theta (eta = mean(theta)/theta_b) and
                  cross-checked against the base-flux form.

Zero compute in the solver sense: no case, no mesh, no OpenFOAM.  The same
discipline as exact_laminar_pipe.py in T1c, cited by the pre-registration's
section 6, which also registers that the rung's comparator REFUSES TO RUN if
these derivations disagree.
"""
import math
import sys

# ---- the registered problem, transcribed from the pre-registration ---------
WALL_LAYERS = ((0.05, 0.8), (0.10, 0.04), (0.02, 16.0))   # (L [m], k [W/mK])
T_HOT, T_COLD = 350.0, 300.0

FIN_K, FIN_T, FIN_L, FIN_H = 200.0, 0.002, 0.05, 50.0

# the registered decimals, exactly as printed in the pre-registration
REGISTERED = dict(sum_R=2.563750, q=19.502682,
                  T_i1=348.781082, T_i2=300.024378,
                  m=15.811388, mL=0.790569,
                  eta=0.8332367, tip_ratio=0.7523781,
                  Bi=2.5e-4)


def thomas(a, b, c, d):
    """Solve the tridiagonal system a[i] x[i-1] + b[i] x[i] + c[i] x[i+1] = d[i]."""
    n = len(b)
    cp = [0.0] * n
    dp = [0.0] * n
    cp[0] = c[0] / b[0]
    dp[0] = d[0] / b[0]
    for i in range(1, n):
        den = b[i] - a[i] * cp[i - 1]
        cp[i] = c[i] / den
        dp[i] = (d[i] - a[i] * dp[i - 1]) / den
    x = [0.0] * n
    x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


# ---- T9a-1 composite wall ---------------------------------------------------
def wall_closed_form():
    sum_R = sum(L / k for L, k in WALL_LAYERS)
    q = (T_HOT - T_COLD) / sum_R
    T_i1 = T_HOT - q * (WALL_LAYERS[0][0] / WALL_LAYERS[0][1])
    T_i2 = T_COLD + q * (WALL_LAYERS[2][0] / WALL_LAYERS[2][1])
    return dict(sum_R=sum_R, q=q, T_i1=T_i1, T_i2=T_i2)


def wall_numeric(n_per_layer=(400, 800, 160)):
    """FV with harmonic face conductances; exact for piecewise-constant k."""
    dx, kc, xc = [], [], []
    x0 = 0.0
    for (L, k), n in zip(WALL_LAYERS, n_per_layer):
        h = L / n
        for i in range(n):
            dx.append(h)
            kc.append(k)
            xc.append(x0 + (i + 0.5) * h)
        x0 += L
    n = len(dx)
    # conductance between cell i and i+1 (series of two half-cells)
    g = [1.0 / (dx[i] / (2 * kc[i]) + dx[i + 1] / (2 * kc[i + 1]))
         for i in range(n - 1)]
    g_hot = 2.0 * kc[0] / dx[0]
    g_cold = 2.0 * kc[-1] / dx[-1]
    a = [0.0] * n
    b = [0.0] * n
    c = [0.0] * n
    d = [0.0] * n
    for i in range(n):
        gl = g_hot if i == 0 else g[i - 1]
        gr = g_cold if i == n - 1 else g[i]
        b[i] = -(gl + gr)
        if i > 0:
            a[i] = gl
        else:
            d[i] -= gl * T_HOT
        if i < n - 1:
            c[i] = gr
        else:
            d[i] -= gr * T_COLD
    T = thomas(a, b, c, d)
    q = g_hot * (T_HOT - T[0])
    q_cold = g_cold * (T[-1] - T_COLD)

    def iface_T(x_iface):
        iL = max(i for i in range(n) if xc[i] < x_iface)
        iR = iL + 1
        wL = kc[iL] / (x_iface - xc[iL])
        wR = kc[iR] / (xc[iR] - x_iface)
        return (wL * T[iL] + wR * T[iR]) / (wL + wR)

    return dict(sum_R=(T_HOT - T_COLD) / q, q=q, q_cold=q_cold,
                T_i1=iface_T(WALL_LAYERS[0][0]),
                T_i2=iface_T(WALL_LAYERS[0][0] + WALL_LAYERS[1][0]))


# ---- T9a-2 fin --------------------------------------------------------------
def fin_closed_form():
    m = math.sqrt(2.0 * FIN_H / (FIN_K * FIN_T))
    mL = m * FIN_L
    return dict(m=m, mL=mL, eta=math.tanh(mL) / mL,
                tip_ratio=1.0 / math.cosh(mL),
                Bi=FIN_H * (FIN_T / 2.0) / FIN_K)


def fin_numeric(n=20000):
    """theta'' = m^2 theta, theta(0)=1, theta'(L)=0, second-order FD."""
    m2 = 2.0 * FIN_H / (FIN_K * FIN_T)
    h = FIN_L / n
    # unknowns theta_1..theta_n (theta_0 = 1 known)
    N = n
    a = [0.0] * N
    b = [0.0] * N
    c = [0.0] * N
    d = [0.0] * N
    for j in range(N):
        b[j] = -2.0 - m2 * h * h
        a[j] = 1.0
        c[j] = 1.0
    # first row couples to the known theta_0 = 1
    a[0] = 0.0
    d[0] = -1.0
    # tip: ghost node theta_{n+1} = theta_{n-1}  ->  2 theta_{n-1} - (2+m2h2) theta_n = 0
    a[-1] = 2.0
    c[-1] = 0.0
    th = thomas(a, b, c, d)
    theta = [1.0] + th
    # eta from the surface integral: eta = (1/L) int theta dx   (Simpson)
    s = theta[0] + theta[-1]
    for j in range(1, n):
        s += (4.0 if j % 2 else 2.0) * theta[j]
    eta_int = (h / 3.0) * s / FIN_L
    # cross-check: eta from the base flux, one-sided second-order gradient
    dth0 = (-3.0 * theta[0] + 4.0 * theta[1] - theta[2]) / (2.0 * h)
    eta_flux = -FIN_K * FIN_T * dth0 / (2.0 * FIN_H * FIN_L)
    return dict(eta=eta_int, eta_flux=eta_flux, tip_ratio=theta[-1],
                m=math.sqrt(m2), mL=math.sqrt(m2) * FIN_L)


def main():
    ok = True

    def check(name, va, vb, tol, note=""):
        nonlocal ok
        rel = abs(va - vb) / max(abs(va), 1e-300)
        good = rel <= tol
        ok = ok and good
        print(f"  {name:12s} {va:.10f}  vs  {vb:.10f}   rel {rel:.2e}  "
              f"{'agree' if good else 'DISAGREE'} {note}")
        return good

    wa, wb = wall_closed_form(), wall_numeric()
    print("T9a-1 composite wall: closed form vs harmonic-FV solve")
    check("sum_R", wa["sum_R"], wb["sum_R"], 1e-9)
    check("q''", wa["q"], wb["q"], 1e-9)
    check("T_i1", wa["T_i1"], wb["T_i1"], 1e-11)
    check("T_i2", wa["T_i2"], wb["T_i2"], 1e-11)
    check("q'' balance", wb["q"], wb["q_cold"], 1e-9, "(numeric hot vs cold face)")

    fa, fb = fin_closed_form(), fin_numeric()
    print("T9a-2 fin: closed form vs finite-difference solve")
    check("eta", fa["eta"], fb["eta"], 1e-7)
    check("eta (flux)", fa["eta"], fb["eta_flux"], 1e-5, "(one-sided gradient)")
    check("tip ratio", fa["tip_ratio"], fb["tip_ratio"], 1e-7)

    print("registered decimals vs derivation")
    check("sum_R", REGISTERED["sum_R"], wa["sum_R"], 1e-6)
    check("q''", REGISTERED["q"], wa["q"], 1e-6)
    check("T_i1", REGISTERED["T_i1"], wa["T_i1"], 1e-8)
    check("T_i2", REGISTERED["T_i2"], wa["T_i2"], 1e-8)
    check("m", REGISTERED["m"], fa["m"], 1e-7)
    check("mL", REGISTERED["mL"], fa["mL"], 1e-6)
    check("eta", REGISTERED["eta"], fa["eta"], 1e-6)
    check("tip_ratio", REGISTERED["tip_ratio"], fa["tip_ratio"], 1e-6)
    check("Bi", REGISTERED["Bi"], fa["Bi"], 1e-9)

    print("AGREE: every constant reproduced two ways." if ok else
          "DISAGREE: the derivations do not agree; nothing downstream may run.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
