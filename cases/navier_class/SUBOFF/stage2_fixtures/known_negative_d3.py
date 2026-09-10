"""FIXTURE -- KNOWN NEGATIVE for D3 (hard-coded claim string, 2be.1).  Every measurement
in the reporting path is a placeholder filled from a read value, so an input can change it."""
def report(waste_core_min, levels):
    return "waste named separately: %.2f core-min on level(s) %s" % (waste_core_min, levels)
