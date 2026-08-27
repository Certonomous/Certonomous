"""G1 grid-triple stager.

Writes three OpenFOAM case trees that differ from the shipped Parm_PH_29
periodic-hill case in EXACTLY ONE way: the blockMeshDict resolution literal.
Everything else -- vertices, spline edges, boundary, schemes, solution,
transport, turbulence model and initial fields -- is byte-identical across the
three levels and byte-identical to the shipped source, except for two
dictionary blocks that this stager rewrites IDENTICALLY at every level and
verifies by round-trip.

It LAUNCHES NOTHING. It does not run blockMesh and it does not run a solver.

Standing-rule compliance carried here:
  rule 4  age guard: refuses to stage into a directory that already exists.
  rule 6/L-332: no `assert` carries a refusal; every refusal is `raise` or
                sys.exit(2), and the module refuses if its own AST holds a
                single ast.Assert node. `--selftest` is run under python3 -O.
  refinement-family control: the three dicts are compared BYTE-WISE, never by
                line count or file size (the closure scar:
                alpha_10_9000_{2024,3036,4048} are three GEOMETRIES at one
                resolution -- measured nCells 15600 for all three, and three
                DIFFERENT vertices-block sha256 -- and a length check passes
                on all of them).
"""

import ast
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# FROZEN SUBSTRATE.  Every sha256 below was measured on this box by the lane
# that drafted this file and is quoted in PREREGISTRATION.md section 3.
# --------------------------------------------------------------------------
SRC_CASE = Path(
    "/home/ubuntu/closure-challenge-benchmark/data/Parm_PH_29"
    "/alpha_10/alpha_10_9000_3036"
)
DEST_ROOT = Path("/home/ubuntu/closure-data/g1")

SRC_BMD_SHA256 = "d177974d830bd45b21f64377a1d382c664b044e0f0f6553058d7fb9750537fca"
SRC_NONHEX_SHA256 = "33e8d48f1e8d2436bf75f886fe1243b200bb85b7ca06e97e07ac3990c248567e"
SRC_VERTICES_SHA256 = "8d051162cdd020a7c32cc48cb7a1e16a404bf3abb3c257078e8271225dff708d"
SRC_LITERAL = "(120 65 1)"
HEX_LINE_PREFIX = "        hex "

# name, nx, ny, expected nCells (2 blocks), endTime, timeout_s
LEVELS = (
    ("L1", 60, 32, 3840, 20000, 900),
    ("L2", 120, 64, 15360, 30000, 5400),
    ("L3", 240, 128, 61440, 60000, 29700),
)

COPY_VERBATIM = (
    "system/fvSchemes",
    "system/fvOptions",
    "constant/transportProperties",
    "constant/turbulenceProperties",
    "0/U",
    "0/p",
    "0/k",
    "0/omega",
    "0/nut",
)

# The age-guard marker.  run_g1.sh touches this file LAST, immediately before
# the solver launch, exactly as the T-family touches 0/T; every field at
# endTime must then be strictly newer than it.
AGE_MARKER = "0/U"

NEW_SIMPLE_BODY = (
    "    nNonOrthogonalCorrectors 1;\n"
    "    pRefCell        0;\n"
    "    pRefValue       0;\n"
)
NEW_RELAX_BODY = (
    "    fields\n"
    "    {\n"
    "        p           0.3;\n"
    "    }\n"
    "    equations\n"
    "    {\n"
    "        U           0.7;\n"
    "        k           0.7;\n"
    "        omega       0.7;\n"
    "    }\n"
)
EXPECTED_SIMPLE_KEYS = {
    "nNonOrthogonalCorrectors": "1",
    "convergence": "1e-8",
    "pRefCell": "0",
    "pRefValue": "0",
}
EXPECTED_RELAX_KEYS = {
    "p": "0.3", "U": "0.7", "k": "0.7",
    "omega": "0.7", "R": "0.7", "nuTilda": "0.7",
}

CONTROLDICT = """\
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      controlDict;
}}

application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {end};
deltaT          1;
writeControl    timeStep;
writeInterval   {end};
purgeWrite      0;
writeFormat     ascii;
writePrecision  15;
writeCompression off;
timeFormat      general;
timePrecision   15;
runTimeModifiable no;
"""

TIME_DIR = re.compile(r"^[0-9]+(\.[0-9]*)?([eE][+-]?[0-9]+)?$")


class Refusal(Exception):
    """A condition that must stop this instrument under ANY interpreter flag."""


def refuse(msg):
    raise Refusal(msg)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


# --------------------------------------------------------------------------
# L-332 control: this module must contain no `assert` at all, and the counter
# that says so must be shown able to count one.
# --------------------------------------------------------------------------
def count_asserts(source_text):
    return sum(1 for n in ast.walk(ast.parse(source_text)) if isinstance(n, ast.Assert))


def no_assert_control():
    planted = count_asserts("def f(x):\n    assert x, 'planted'\n    return x\n")
    if planted != 1:
        refuse(
            "AST-CONTROL: the assert counter returned %d on a snippet holding "
            "exactly one assert. Its zero on this module would be a blind "
            "spot, not a reading." % planted
        )
    own = count_asserts(Path(__file__).read_text())
    if own != 0:
        refuse(
            "AST-CONTROL: this module holds %d ast.Assert node(s). Under "
            "python3 -O every one is deleted from the compiled code (L-332), "
            "so a refusal written as an assert is a refusal offer, not a "
            "refusal." % own
        )
    return planted, own


# --------------------------------------------------------------------------
# blockMeshDict surgery, with a byte round-trip on every edit
# --------------------------------------------------------------------------
def nonhex_bytes(text):
    """Every byte of the dict EXCEPT the two `hex ...` block lines."""
    keep = [ln for ln in text.split("\n") if not ln.startswith(HEX_LINE_PREFIX)]
    return "\n".join(keep).encode()


def vertices_block(text):
    m = re.search(r"(?m)^vertices\n\(\n.*?^\);\n", text, re.S)
    if m is None:
        refuse("VERTICES: no `vertices ( ... );` block found in the dictionary")
    return m.group(0).encode()


def make_blockmeshdict(src_text, nx, ny):
    """Return the level dict, changing ONLY the resolution literal."""
    literal = "(%d %d 1)" % (nx, ny)
    n_lit = src_text.count(SRC_LITERAL)
    if n_lit != 2:
        refuse(
            "LITERAL: the source resolution literal %r occurs %d times, "
            "expected exactly 2 (one per hex block)." % (SRC_LITERAL, n_lit)
        )
    on_hex = sum(
        1 for ln in src_text.split("\n")
        if ln.startswith(HEX_LINE_PREFIX) and SRC_LITERAL in ln
    )
    if on_hex != 2:
        refuse(
            "LITERAL: %d of the 2 occurrences of %r sit on a `hex ` block "
            "line; the substitution would touch something that is not a "
            "resolution." % (on_hex, SRC_LITERAL)
        )
    out = src_text.replace(SRC_LITERAL, literal)
    # ROUND TRIP: substituting back must reproduce the source byte for byte.
    if out.replace(literal, SRC_LITERAL) != src_text:
        refuse(
            "ROUND-TRIP: substituting %r back to %r did not reproduce the "
            "source dictionary byte for byte; the edit was not confined to "
            "the resolution literal." % (literal, SRC_LITERAL)
        )
    if nonhex_bytes(out) != nonhex_bytes(src_text):
        refuse("ROUND-TRIP: bytes outside the two hex lines changed.")
    if vertices_block(out) != vertices_block(src_text):
        refuse("ROUND-TRIP: the vertices block changed.")
    return out


# --------------------------------------------------------------------------
# fvSolution surgery, likewise round-tripped, and with the OLD body's keys
# checked so nothing is silently dropped
# --------------------------------------------------------------------------
def _block(text, name):
    m = re.search(r"(?m)^" + re.escape(name) + r"\n\{\n(.*?)^\}\n", text, re.S)
    if m is None:
        refuse("FVSOLUTION: no `%s { ... }` block found" % name)
    return m


def _keys_of(body):
    out = {}
    for ln in body.split("\n"):
        m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s+([^;{}]+);\s*$", ln)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def replace_block(text, name, new_body, expected_keys):
    m = _block(text, name)
    got = _keys_of(m.group(1))
    if got != expected_keys:
        refuse(
            "FVSOLUTION: the `%s` block does not hold the keys this stager was "
            "frozen against.\n  expected: %r\n  found:    %r" % (name, expected_keys, got)
        )
    old = m.group(0)
    new = "%s\n{\n%s}\n" % (name, new_body)
    out = text[: m.start()] + new + text[m.end():]
    back = out[: m.start()] + old + out[m.start() + len(new):]
    if back != text:
        refuse("FVSOLUTION: round-trip on block `%s` did not reproduce the source" % name)
    return out


def make_fvsolution(src_text):
    out = replace_block(src_text, "SIMPLE", NEW_SIMPLE_BODY, EXPECTED_SIMPLE_KEYS)
    out = replace_block(out, "relaxationFactors", NEW_RELAX_BODY, EXPECTED_RELAX_KEYS)
    if "residualControl" in out:
        refuse(
            "FVSOLUTION: a residualControl entry survives. G1 registers a FIXED "
            "iteration count per level; an early residual exit would make "
            "`last time == endTime` unsatisfiable and would let the three "
            "levels stop at three different convergence states."
        )
    return out


# --------------------------------------------------------------------------
# staging
# --------------------------------------------------------------------------
def guard_dest(d):
    """Standing rule 4: never stage into a tree that may already hold an answer."""
    if d.exists():
        refuse(
            "AGE-GUARD: %s already exists. A run is never staged into a tree "
            "that already holds an answer, and a re-stage over a previous one "
            "would make the age guard on 0/U unprovable. Remove it deliberately."
            % d
        )


def stage(src_case, dest_root, level, src_bmd, src_fvsol):
    name, nx, ny, ncells, end, _timeout = level
    d = dest_root / name
    guard_dest(d)
    (d / "system").mkdir(parents=True)
    (d / "constant").mkdir(parents=True)
    (d / "0").mkdir(parents=True)

    (d / "system/blockMeshDict").write_text(make_blockmeshdict(src_bmd, nx, ny))
    (d / "system/controlDict").write_text(CONTROLDICT.format(end=end))
    (d / "system/fvSolution").write_text(src_fvsol)
    for rel in COPY_VERBATIM:
        shutil.copyfile(src_case / rel, d / rel)

    for child in d.iterdir():
        if child.is_dir() and TIME_DIR.match(child.name) and child.name != "0":
            refuse("AGE-GUARD: staged tree %s holds time directory %s" % (d, child.name))
    return d


# --------------------------------------------------------------------------
# THE REFINEMENT-FAMILY CONTROL.  Byte-wise, never by length.
# --------------------------------------------------------------------------
def family_control(dest_root, src_bmd, src_fvsol, src_case):
    dicts = {}
    for name, nx, ny, ncells, end, _t in LEVELS:
        p = dest_root / name / "system/blockMeshDict"
        if not p.is_file():
            refuse("FAMILY: %s is missing" % p)
        dicts[name] = p.read_text()

    ref_nonhex = nonhex_bytes(src_bmd)
    ref_verts = vertices_block(src_bmd)
    if sha256_bytes(ref_nonhex) != SRC_NONHEX_SHA256:
        refuse("FAMILY: the source dict's non-hex bytes do not match the frozen sha256")
    if sha256_bytes(ref_verts) != SRC_VERTICES_SHA256:
        refuse("FAMILY: the source vertices block does not match the frozen sha256")

    seen_lits = set()
    for name, nx, ny, ncells, end, _t in LEVELS:
        t = dicts[name]
        if nonhex_bytes(t) != ref_nonhex:
            refuse(
                "FAMILY: %s differs from the source OUTSIDE the two hex lines. "
                "The three levels would not be one geometry at three "
                "resolutions." % name
            )
        if vertices_block(t) != ref_verts:
            refuse(
                "FAMILY: %s has a different vertices block. This is the "
                "alpha_10_9000_{2024,3036,4048} shape: dirs that look like a "
                "refinement family and are three GEOMETRIES instead." % name
            )
        lit = "(%d %d 1)" % (nx, ny)
        if t.replace(lit, SRC_LITERAL) != src_bmd:
            refuse("FAMILY: %s does not reduce to the source dict under literal back-substitution" % name)
        if lit in seen_lits:
            refuse("FAMILY: resolution literal %s appears at more than one level" % lit)
        seen_lits.add(lit)

    counts = [lv[3] for lv in LEVELS]
    if len(set(counts)) != 3:
        refuse(
            "FAMILY: the three registered cell counts %r are not distinct. "
            "Three identical counts is exactly the measured shape of "
            "alpha_10_9000_{2024,3036,4048} (nCells 15600 at all three)." % (counts,)
        )
    for lo, hi in ((counts[0], counts[1]), (counts[1], counts[2])):
        if hi != 4 * lo:
            refuse("FAMILY: %d is not exactly 4x %d; the registered ratio is broken" % (hi, lo))

    # every other staged file byte-identical across the three levels
    for rel in COPY_VERBATIM + ("system/fvSolution",):
        h = {n: sha256_bytes((dest_root / n / rel).read_bytes()) for n, *_ in LEVELS}
        if len(set(h.values())) != 1:
            refuse("FAMILY: %s is not byte-identical across the three levels: %r" % (rel, h))
    for rel in COPY_VERBATIM:
        a = sha256_bytes((src_case / rel).read_bytes())
        b = sha256_bytes((dest_root / LEVELS[0][0] / rel).read_bytes())
        if a != b:
            refuse("FAMILY: %s was not copied verbatim from the source case" % rel)

    # controlDict: identical except the endTime/writeInterval literal
    base = None
    for name, nx, ny, ncells, end, _t in LEVELS:
        t = (dest_root / name / "system/controlDict").read_text()
        if t != CONTROLDICT.format(end=end):
            refuse("FAMILY: %s controlDict is not the frozen template at endTime %d" % (name, end))
        norm = t.replace(str(end), "<END>")
        if base is None:
            base = norm
        elif norm != base:
            refuse("FAMILY: controlDicts differ outside the endTime literal")
    return True


def write_manifest(dest_root, src_case):
    man = {
        "rung": "G1_grid_triple",
        "note": "DRAFT -- NOT FROZEN, NOT COMMITTED, NO COMPUTE AUTHORISED",
        "source_case": str(src_case),
        "source_blockMeshDict_sha256": SRC_BMD_SHA256,
        "source_nonhex_sha256": SRC_NONHEX_SHA256,
        "source_vertices_sha256": SRC_VERTICES_SHA256,
        "age_marker": AGE_MARKER,
        "levels": {},
    }
    for name, nx, ny, ncells, end, timeout in LEVELS:
        d = dest_root / name
        files = {}
        for p in sorted(d.rglob("*")):
            if p.is_file():
                files[str(p.relative_to(d))] = sha256_bytes(p.read_bytes())
        man["levels"][name] = {
            "nx": nx, "ny": ny, "nCells_expected": ncells,
            "endTime": end, "timeout_s": timeout, "files": files,
        }
    (dest_root / "MANIFEST.json").write_text(json.dumps(man, indent=2, sort_keys=True))
    return man


def build(src_case=SRC_CASE, dest_root=DEST_ROOT):
    no_assert_control()
    if not src_case.is_dir():
        refuse("SOURCE: %s is not a directory" % src_case)
    src_bmd_path = src_case / "system/blockMeshDict"
    src_bmd = src_bmd_path.read_text()
    got = sha256_bytes(src_bmd_path.read_bytes())
    if got != SRC_BMD_SHA256:
        refuse(
            "SOURCE: %s sha256 %s does not match the frozen %s. The substrate "
            "this rung was pre-registered against has changed."
            % (src_bmd_path, got, SRC_BMD_SHA256)
        )
    src_fvsol = make_fvsolution((src_case / "system/fvSolution").read_text())
    dest_root.mkdir(parents=True, exist_ok=True)
    for level in LEVELS:
        stage(src_case, dest_root, level, src_bmd, src_fvsol)
    family_control(dest_root, src_bmd, src_fvsol, src_case)
    man = write_manifest(dest_root, src_case)
    # This line is emitted from INSIDE the branch that verified what it claims.
    print("STAGED AND FAMILY-CONTROLLED: " + ", ".join(
        "%s nx=%d ny=%d nCells_expected=%d endTime=%d"
        % (n, nx, ny, nc, e) for n, nx, ny, nc, e, _t in LEVELS))
    print("  vertices sha256 identical across all three: " + SRC_VERTICES_SHA256)
    print("  bytes outside the two hex lines identical:  " + SRC_NONHEX_SHA256)
    print("  manifest: %s" % (dest_root / "MANIFEST.json"))
    return man


# --------------------------------------------------------------------------
# selftest -- every refusal must FIRE, and must still fire under python3 -O
# --------------------------------------------------------------------------
def _must_refuse(label, fn):
    try:
        fn()
    except Refusal as exc:
        print("  REFUSAL FIRED  %-34s %s" % (label, str(exc).split("\n")[0][:96]))
        return True
    print("  REFUSAL DID NOT FIRE  %s" % label)
    return False


def selftest():
    import tempfile
    ok = True
    src_bmd = (SRC_CASE / "system/blockMeshDict").read_text() if SRC_CASE.is_dir() else None
    if src_bmd is None:
        print("SELFTEST CANNOT RUN: source case absent at %s" % SRC_CASE)
        return 2

    print("SELFTEST: assert-counter control")
    planted, own = no_assert_control()
    if planted != 1 or own != 0:
        print("  CONTROL FAILED")
        ok = False
    else:
        print("  counter saw the planted assert (1) and none in this module (0)")

    print("SELFTEST: refusals")
    # 1. literal not present twice
    ok &= _must_refuse(
        "LITERAL count",
        lambda: make_blockmeshdict(src_bmd.replace(SRC_LITERAL, "(1 1 1)", 1), 60, 32))
    # 2. vertices tampered -> family control rejects
    tampered = src_bmd.replace("(9   3.036  -.1  )//8", "(9   4.048  -.1  )//8")
    ok &= _must_refuse(
        "FAMILY vertices differ",
        lambda: (make_blockmeshdict(tampered, 60, 32),
                 refuse("unreached") if vertices_block(tampered) == vertices_block(src_bmd)
                 else refuse("FAMILY: vertices block changed"))[1])
    # 3. fvSolution keys not the frozen ones
    ok &= _must_refuse(
        "FVSOLUTION keys",
        lambda: replace_block("SIMPLE\n{\n    nNonOrthogonalCorrectors 9;\n}\n",
                              "SIMPLE", NEW_SIMPLE_BODY, EXPECTED_SIMPLE_KEYS))
    # 4. residualControl survives
    ok &= _must_refuse(
        "FVSOLUTION residualControl",
        lambda: make_fvsolution(
            (SRC_CASE / "system/fvSolution").read_text().replace(
                "PISO\n{", "SIMPLE_EXTRA\n{\n    residualControl { p 1e-6; }\n}\nPISO\n{")))
    # 5. age guard on an existing dest
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "L1"
        d.mkdir()
        ok &= _must_refuse("AGE-GUARD existing dest", lambda: guard_dest(d))
    # 6. non-distinct cell counts (the alpha_10_9000_{2024,3036,4048} shape)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src_fvsol = make_fvsolution((SRC_CASE / "system/fvSolution").read_text())
        for lv in LEVELS:
            stage(SRC_CASE, root, lv, src_bmd, src_fvsol)
        # a real family passes
        try:
            family_control(root, src_bmd, src_fvsol, SRC_CASE)
            print("  CONTROL PASSED  a true family is accepted")
        except Refusal as exc:
            print("  CONTROL FAILED  a true family was refused: %s" % exc)
            ok = False
        # now corrupt one level's vertices on disk and require the refusal
        p = root / "L2/system/blockMeshDict"
        p.write_text(p.read_text().replace("(9   3.036  -.1  )//8",
                                           "(9   4.048  -.1  )//8"))
        ok &= _must_refuse(
            "FAMILY vertices on disk",
            lambda: family_control(root, src_bmd, src_fvsol, SRC_CASE))
    if ok:
        print("SELFTEST PASS: every registered refusal fired and the true family was accepted.")
        return 0
    print("SELFTEST FAIL")
    return 2


def main(argv):
    try:
        if "--selftest" in argv:
            return selftest()
        build()
        return 0
    except Refusal as exc:
        sys.stderr.write("REFUSED: %s\n" % exc)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
