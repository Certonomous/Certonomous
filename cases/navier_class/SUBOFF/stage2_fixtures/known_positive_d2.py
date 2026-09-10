"""FIXTURE -- KNOWN POSITIVE for detector D2 (faces-as-cells, 2bd.1)."""
def parse_owner(case):
    return [0] * 10          # polyMesh/owner: ONE ENTRY PER FACE
def measure(case):
    ncells = len(parse_owner(case))            # the 2bd.1 defect shape: this is nFaces
    return ncells
