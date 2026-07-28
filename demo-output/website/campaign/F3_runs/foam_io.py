"""Minimal parsers for OpenFOAM ASCII field files (no external deps)."""
import re
import numpy as np


def read_patch_scalar(time_dir, field, patch):
    """Read the boundaryField values for `patch` from a scalar field file."""
    path = f"{time_dir}/{field}"
    txt = open(path).read()
    # isolate the patch block
    m = re.search(rf"\b{re.escape(patch)}\b\s*\{{(.*?)\n\}}", txt, re.S)
    if m is None:
        raise ValueError(f"patch {patch} not found in {path}")
    block = m.group(1)
    mm = re.search(r"nonuniform\s+List<scalar>\s*\n(\d+)\s*\((.*?)\)\s*;", block, re.S)
    if mm:
        vals = np.array([float(x) for x in mm.group(2).split()])
        return vals
    mm2 = re.search(r"uniform\s+([\-0-9.eE]+)\s*;", block)
    if mm2:
        return float(mm2.group(1))
    raise ValueError(f"could not parse patch {patch} field values in {path}")
