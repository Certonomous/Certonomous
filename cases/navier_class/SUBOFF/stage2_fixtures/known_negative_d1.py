"""FIXTURE -- KNOWN NEGATIVE for D1.  Same decision, measured over a declared trailing
window with a drift statistic, which is what 2bd requires."""
TOL, WINDOW = 0.005, 100
def decide(series):
    w = series[-WINDOW:]                       # a SLICE is a window; D1 must not fire
    drift = abs(w[-1] - w[0]) / max(abs(w[-1]), 1e-300)
    plateaued = drift <= TOL
    return plateaued
