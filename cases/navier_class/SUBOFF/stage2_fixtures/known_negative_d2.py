"""FIXTURE -- KNOWN NEGATIVE for D2.  The count comes from a source that counts CELLS and
the source is named, which is what 2bd.1 requires."""
def parse_owner(case):
    return [0] * 10
def measure(case):
    owner = parse_owner(case)
    ncells = max(owner) + 1                    # cells, from the owner index range
    n_cells_source = "polyMesh/owner: max(owner)+1"
    return ncells, n_cells_source
