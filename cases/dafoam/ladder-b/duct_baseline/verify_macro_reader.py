#!/usr/bin/env python3
"""
Round-trip verification for macro_field_reader.py.

Method: take CBFS's 0/U -- a field Ofpp CAN parse directly (no #include, no
$ macros) -- and use its own real inlet-boundary numeric data (150 vectors,
already parsed once by plain Ofpp) to synthesize a macro'd field file that
mimics the exact #include + $name structure used by 0/U_LES. Then parse the
synthetic file two ways:

  (a) directly with plain Ofpp (ground truth -- these are literally the
      same numbers already sitting in 0/U, so this is not a new parse of
      new data, it's a re-statement of numbers we already trust)
  (b) with our macro-expanding reader, going through #include splicing and
      $ substitution

and assert the two arrays are byte-identical (np.array_equal, exact, no
tolerance). This is the strongest test available: it exercises the actual
macro machinery (#include + $var) end to end against numbers whose
Ofpp-parsed value is independently known, rather than testing on a file
that never invokes the macro path at all.
"""
import os
import shutil
import sys

sys.path.insert(0, "/home/ubuntu/closure-challenge-pkg/src")
import numpy as np
from Ofpp import parse_boundary_field

sys.path.insert(0, os.path.dirname(__file__))
from macro_field_reader import parse_internal_field_macro

CBFS = "/home/ubuntu/Certonomous/demo-output/website/dafoam/ladder-b/duct_baseline/CBFS"
TMP = "/tmp/claude-1000/-home-ubuntu-Certonomous/982d6244-5800-47f3-a450-80ce0b0a24b7/scratchpad/macro_roundtrip"

# 1. Ground truth: parse 0/U's inlet boundary field with plain Ofpp (no macros
#    involved in 0/U at all -- this file has neither #include nor $ syntax).
bd = parse_boundary_field(os.path.join(CBFS, "0", "U"))
assert bd is not None, "sanity check failed: plain Ofpp could not parse 0/U at all"
inlet_ground_truth = bd[b"inlet"][b"value"]
print("Ground truth (plain Ofpp on 0/U boundaryField[inlet]):",
      "shape", inlet_ground_truth.shape, "dtype", inlet_ground_truth.dtype)

# 2. Re-serialize those exact numbers as an OpenFOAM nonuniform List<vector>
#    entry, in the same textual form CBFS's own interpolatedFields/* use.
n = inlet_ground_truth.shape[0]
lines = ["U_inlet_roundtrip nonuniform List<vector>", str(n), "("]
for row in inlet_ground_truth:
    lines.append("({:.10g} {:.10g} {:.10g})".format(*row))
lines.append(");")
include_body = "\n".join(lines) + "\n"

os.makedirs(os.path.join(TMP, "interpolatedFields"), exist_ok=True)
with open(os.path.join(TMP, "interpolatedFields", "U_inlet_roundtrip"), "w") as f:
    f.write(include_body)

# 3. Build a main field file with the exact #include + $name macro structure
#    used by CBFS/0/U_LES, but pointing at our synthesized include and using
#    it as the *internalField* (so parse_internal_field_macro exercises it).
main_text = """/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U_roundtrip;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

#include "interpolatedFields/U_inlet_roundtrip"

internalField   $U_inlet_roundtrip;

boundaryField
{
    allBoundary
    {
        type            fixedValue;
        value           $U_inlet_roundtrip;
    }
}

// ************************************************************************* //
"""
main_path = os.path.join(TMP, "U_roundtrip_macro")
with open(main_path, "w") as f:
    f.write(main_text)

# 4. Parse it through the macro-expanding reader.
macro_result = parse_internal_field_macro(main_path)
if macro_result is None:
    print("FAIL: macro reader returned None on a file it should resolve")
    sys.exit(1)

print("Macro reader result: shape", macro_result.shape, "dtype", macro_result.dtype)

identical = np.array_equal(inlet_ground_truth, macro_result)
print("Byte-identical to ground truth (np.array_equal, exact):", identical)
if not identical:
    diff = np.abs(inlet_ground_truth - macro_result)
    print("FAIL: max abs diff =", diff.max())
    sys.exit(1)

# 5. Also confirm the macro reader is NOT silently returning None the way
#    Ofpp does on the real macro'd file (negative control): plain Ofpp on the
#    same synthetic macro'd file should fail (return None), proving the test
#    file genuinely exercises the macro path and isn't accidentally
#    macro-free.
from Ofpp import parse_internal_field as plain_ofpp_parse
plain_result = plain_ofpp_parse(main_path)
print("Negative control -- plain Ofpp on the SAME macro'd file returns:", plain_result)
assert plain_result is None, (
    "unexpected: plain Ofpp parsed the macro'd file directly -- "
    "the synthetic test file does not actually exercise the macro bug"
)

# 6. Duplicate-key regression test, modeled directly on the real bug found
#    in CBFS's own 0/p_LES: a placeholder `internalField uniform 0;` BEFORE
#    the #include block, legitimately shadowed by the real macro'd value
#    AFTER it (OpenFOAM dictionaries are last-entry-wins). Confirm the
#    reader returns the REAL (post-#include) value, not the placeholder --
#    this is a second, more dangerous failure mode than a silent None
#    because it looks like a valid answer.
dup_text = """FoamFile
{
    version 2.0;
    format ascii;
    class volScalarField;
    object p_dup_roundtrip;
}

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

#include "interpolatedFields/U_inlet_roundtrip"

internalField   $U_inlet_roundtrip;
"""
# reuse the same synthesized include from step 2/3 (still on disk at this point)
dup_path = os.path.join(TMP, "p_dup_roundtrip")
with open(dup_path, "w") as f:
    f.write(dup_text)

from macro_field_reader import parse_internal_field_macro as _reparse
dup_result = _reparse(dup_path)
print()
print("Duplicate-key test (placeholder `uniform 0` shadowed by real #include'd value):")
print("  result:", None if dup_result is None else (dup_result.shape, dup_result.dtype))
if dup_result is None:
    print("FAIL: returned None instead of the shadowing (real) value")
    sys.exit(1)
if np.isscalar(dup_result) or dup_result.shape == ():
    print("FAIL: returned the placeholder `uniform 0` value instead of resolving "
          "the later, real entry -- this is the p_LES bug reproduced")
    sys.exit(1)
dup_identical = np.array_equal(inlet_ground_truth, dup_result)
print("  matches real (post-#include) data, not placeholder:", dup_identical)
if not dup_identical:
    print("FAIL: duplicate-key resolution did not pick the correct (last) entry")
    sys.exit(1)

print()
print("ROUND-TRIP VERIFICATION: PASS")
print(" - macro reader correctly resolved #include + $name substitution")
print(" - resulting values are byte-identical (exact) to the independently")
print("   Ofpp-parsed ground truth for the same underlying numbers")
print(" - plain Ofpp on the identical macro'd file returns None (confirms")
print("   the test genuinely exercises the silent-failure mode from B2)")

shutil.rmtree(TMP, ignore_errors=True)
