"""FIXTURE -- KNOWN POSITIVE for detector D1 (two-sample window, VERIFICATION_CHARTER 2bd).
NOT A GRADER.  Nothing imports this; it exists so D1 is proven able to see a non-zero
before its silence on a real comparator is read as evidence (standing rule 3)."""
TOL = 0.005
def decide(series):
    value = series[-1]
    plateaued = abs(series[-1] - series[-2]) <= TOL * abs(value)   # the 2bd defect shape
    return plateaued
