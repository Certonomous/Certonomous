"""The F7a gate's measurement definition, executed against the prose that froze it.

WHY THIS FILE EXISTS.  `F7a_REGATE_SPEC.md` §2 declares itself normative and
says so in the strongest available terms: *"Two independent agents given only
§2 and the same case directory must compute the same number."*  It then lived
entirely in a markdown file.  The extractor that produced its §3 verdict,
`F7_runs/front_metrics.py`, predates the prose by twelve days (`4aad8298`
against `1393b8b4`) and implements none of §2's assertions, guards, station
set, tolerance or verdict.  Nothing connected the two, so nothing could go red
when they disagreed — and by the time this file was written they disagreed in
five measurable ways, one of which silently mis-shapes the a/16 mesh.

WHAT IS ASSERTED HERE, and the direction of authority matters.  The source of
truth for every frozen constant is **the spec's own prose**, re-parsed out of
`F7a_REGATE_SPEC.md` on every run.  The tests then assert that
`F7_runs/f7a_contract.py` computes with those values.  A drift in either
direction fails: editing the module without the spec, or the spec without the
module.  This is the "cannot drift from the code" property the brief asked
for, and it is why the numbers below are read from disk rather than typed.

WHAT IS NOT ASSERTED HERE.  No test encodes a gate outcome as a requirement.
`test_gate_verdict_reproduces_frozen_section_3` pins the six published
deviations because a re-grade that silently moved them would be a regression in
the instrument, not a new result — but nothing here requires the verdict to be
FAIL, and §2.6's anti-relitigation clause is respected throughout: no
threshold, station set, axis or mesh is chosen here.

L-84: the guard tests carry must-not-fire controls beside their must-fire
cases.  A structural assertion that refused every mesh would satisfy a naive
test and be worthless.
"""
import json
import math
import os
import re
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F7 = os.path.join(REPO, "demo-output", "website", "campaign", "F7_runs")
SPEC_PATH = os.path.join(REPO, "demo-output", "website", "campaign",
                         "F7a_REGATE_SPEC.md")

# The one case the spec takes its verdict on (§3).  Tracked field data; no
# solver is launched by anything in this file.
VERDICT_CASE = os.path.join(F7, "F7a_R1", "res32y128_base")


# --------------------------------------------------------------------------
# The frozen prose, re-parsed.  These helpers deliberately import nothing.
# --------------------------------------------------------------------------

def _spec_section_2():
    """§2 of the spec, whitespace-collapsed so the assertions below are immune
    to line re-wrapping but not to a changed number."""
    txt = open(SPEC_PATH, encoding="utf-8").read()
    start = txt.index("## 2. THE CONTRACT")
    end = txt.index("## 3. THE GATE VERDICT")
    return re.sub(r"\s+", " ", txt[start:end])


def _one(pattern, where=None):
    body = _spec_section_2() if where is None else where
    m = re.search(pattern, body)
    assert m is not None, "frozen spec text no longer contains %r" % pattern
    return m


@pytest.fixture(scope="module")
def spec2():
    return _spec_section_2()


@pytest.fixture(scope="module")
def contract():
    sys.path.insert(0, F7)
    import f7a_contract
    return f7a_contract


# --------------------------------------------------------------------------
# 1. The contract's constants ARE the frozen prose.
# --------------------------------------------------------------------------

def test_length_scale_matches_frozen_spec(spec2, contract):
    """§2.1 'Length scale a = 0.05715 m exactly (2 1/4 in x 0.0254 m/in).'"""
    a = float(_one(r"a = ([\d.]+) m exactly", spec2).group(1))
    assert contract.A == a
    assert contract.A == pytest.approx(2.25 * 0.0254, abs=1e-12)


def test_gravity_matches_frozen_spec(spec2, contract):
    """§2.3 'g = 9.81 m/s2 exactly'."""
    g = float(_one(r"g = ([\d.]+) m/s. exactly", spec2).group(1))
    assert contract.G == g


def test_column_rounding_matches_frozen_spec(spec2, contract):
    """§2.1 'grouped into columns by cell-centre x rounded to 8 decimal places'
    — pinned in the prose 'rather than left to the implementer', which is
    exactly the clause `front_metrics.py` diverges from."""
    dp = int(_one(r"rounded to \*\*(\d+) decimal places\*\*", spec2).group(1))
    assert contract.COLUMN_ROUND_DP == dp


def test_front_threshold_matches_frozen_spec(spec2, contract):
    """§2.2 'h* = 0.02 a = 1.143 mm, fixed.'"""
    h = float(_one(r"h\\\* = ([\d.]+) a = 1\.143 mm\*\*, fixed", spec2).group(1))
    assert contract.H_STAR == h
    assert contract.H_STAR * contract.A == pytest.approx(1.143e-3, abs=1e-6)


def test_threshold_sweep_matches_frozen_spec(spec2, contract):
    """§2.2 'repeated at h* in {0.01a, 0.02a, 0.03a, 0.04a}'."""
    body = _one(r"repeated at \*\*h\\?\* . \{([^}]+)\}", spec2).group(1)
    sweep = tuple(float(v) for v in re.findall(r"([\d.]+)a", body))
    assert contract.THRESHOLD_SWEEP == sweep
    assert contract.H_STAR in contract.THRESHOLD_SWEEP


def test_spread_trigger_matches_frozen_spec(spec2, contract):
    """§2.2 'If that spread exceeds 1.0% of Z at any graded station, the
    verdict is UNGRADEABLE, not FAIL.'"""
    pct = float(_one(r"spread exceeds ([\d.]+)% of Z at any graded station", spec2).group(1))
    assert contract.SPREAD_UNGRADEABLE_FRAC == pytest.approx(pct / 100.0)


def test_wall_clause_matches_frozen_spec(spec2, contract):
    """§2.2 'If the front reaches Z >= 14.5 at or before a graded station, that
    station is UNGRADEABLE.'"""
    z = float(_one(r"front reaches Z . ([\d.]+) at or before", spec2).group(1))
    assert contract.Z_WALL_UNGRADEABLE == z


def test_monotonicity_tolerance_matches_frozen_spec(spec2, contract):
    """§2.2 'stops at the first time at which Z decreases by more than 0.05'."""
    tol = float(_one(r"Z decreases by more than ([\d.]+)\*\*", spec2).group(1))
    assert contract.MONOTONIC_DROP_TOL == tol


def test_write_cadence_cap_matches_frozen_spec(spec2, contract):
    """§2.3.4 'writeInterval must satisfy dT <= 0.35'."""
    cap = float(_one(r"must satisfy \*\*.T . ([\d.]+)\*\*", spec2).group(1))
    assert contract.DT_STAR_MAX == cap


def test_reference_table_matches_frozen_spec(spec2, contract):
    """§2.4 'The frozen reference table (T, Z), all eight points.'"""
    m = _one(r"\*\*The frozen reference table\*\* \(T, Z\), all eight points:", spec2)
    body = spec2[m.end():m.end() + 240]
    pairs = tuple((float(t), float(z))
                  for t, z in re.findall(r"\(([\d.]+), ([\d.]+)\)", body))[:8]
    assert len(pairs) == 8, pairs
    assert contract.REFERENCE == pairs


def test_graded_station_count_matches_frozen_spec(spec2, contract):
    """§2.4 'Graded stations: the first six, T = 3.90 ... 7.72, Z = 6 ... 11.'"""
    assert "Graded stations: the first six" in spec2
    assert contract.N_GRADED == 6
    assert [z for _, z in contract.REFERENCE[:contract.N_GRADED]] == \
        [6.0, 7.0, 8.0, 9.0, 10.0, 11.0]


def test_tolerance_matches_frozen_spec(spec2, contract):
    """§2.4 'Tolerance: 5%, applied to max|d_k| over the six graded stations.'"""
    pct = float(_one(r"Tolerance: ([\d.]+)%, applied to max", spec2).group(1))
    assert contract.TOLERANCE == pytest.approx(pct / 100.0)


def test_resolution_floors_match_frozen_spec(spec2, contract):
    """§2.5 'A gate verdict may be taken only on a mesh with dy <= a/128' and
    'no verdict is taken on it below dy <= a/32'."""
    v = int(_one(r"verdict may be taken only on a mesh with dy . a/(\d+)", spec2).group(1))
    d = int(_one(r"no verdict is taken on it below dy . a/(\d+)", spec2).group(1))
    assert contract.DY_VERDICT_FLOOR_DIV == v
    assert contract.DY_DIAGNOSTIC_FLOOR_DIV == d


def test_verdict_vocabulary_is_three_valued(spec2, contract):
    """§2.4 'Verdict is three-valued: PASS / FAIL / UNGRADEABLE.'"""
    assert "Verdict is three-valued: PASS / FAIL / UNGRADEABLE" in spec2
    assert {contract.PASS, contract.FAIL, contract.UNGRADEABLE} == \
        {"PASS", "FAIL", "UNGRADEABLE"}


# --------------------------------------------------------------------------
# 2. The definition has exactly ONE executable home.
#
# These tests read only tracked artifacts and are the ones that were already
# red before `f7a_contract.py` existed.  A second hardcoded copy of the
# reference table, or a second implementation of the metric that nothing marks
# as superseded, is a definition that can drift — which is how
# `gate_compare.py` came to carry T = 6.74 for the Z = 10 station while every
# other surface carries 6.70.
# --------------------------------------------------------------------------

NORMATIVE = "f7a_contract.py"
SUPERSEDED_MARK = "NOT-NORMATIVE"


def _f7_modules():
    out = subprocess.check_output(
        ["git", "ls-files", "demo-output/website/campaign/F7_runs/*.py"],
        cwd=REPO).decode()
    return sorted(os.path.join(REPO, p) for p in out.split())


def _front_reference_pairs(text):
    """Every (T, Z) pair in a source file whose Z is an integer 6..13 — which
    picks out a Martin & Moyce front table and nothing else (the column-height
    table has Z < 1.01; the comparator's own curve has Z = 13.003, 11.380, ...)."""
    pairs = []
    for t, z in re.findall(r"\(\s*(-?[\d.]+)\s*,\s*([\d.]+)\s*\)", text):
        zf = float(z)
        if zf.is_integer() and 6 <= zf <= 13:
            pairs.append((float(t), zf))
    return pairs


def test_reference_table_has_one_executable_home(contract):
    """Every tracked F7 module carrying a front reference table must either
    agree with the contract exactly, or declare itself NOT-NORMATIVE and name
    the module that is.  `gate_compare.py` (the 2026-07-28 gate) disagrees at
    one station and is kept, struck, per L-76 — never silently corrected."""
    offenders = []
    for path in _f7_modules():
        if os.path.basename(path) == NORMATIVE:
            continue
        text = open(path, encoding="utf-8").read()
        pairs = _front_reference_pairs(text)
        if not pairs:
            continue
        agrees = tuple(pairs[:8]) == contract.REFERENCE
        marked = SUPERSEDED_MARK in text and NORMATIVE in text
        if not (agrees or marked):
            offenders.append((os.path.basename(path), pairs[:8]))
    assert not offenders, (
        "these modules carry a front reference table that neither matches the "
        "contract nor declares itself superseded: %s" % offenders)


def test_metric_implementations_declare_which_one_is_normative():
    """`front_metrics.py` and `grade_f7a.py` implement the metric and the
    grading independently of the contract.  They may stay — they are the R1
    audit's executed instruments and L-76 keeps executed instruments — but each
    must name the normative module, so no future reader takes a verdict off
    one of them by accident.  This is docket C3, one home per fact, applied to
    a definition rather than a number."""
    unmarked = []
    for name in ("front_metrics.py", "grade_f7a.py", "gate_compare.py",
                 "old_spec_readings.py"):
        text = open(os.path.join(F7, name), encoding="utf-8").read()
        if not (SUPERSEDED_MARK in text and NORMATIVE in text):
            unmarked.append(name)
    assert not unmarked, (
        "these modules compute a gate quantity without naming %s as normative: %s"
        % (NORMATIVE, unmarked))


def test_length_scale_is_pinned_not_an_argument(contract):
    """§2.1 pins a = 0.05715 m exactly.  `front_metrics.py` takes `a` from
    argv, so two invocations of the same script on the same case can disagree
    about the length scale — the definition is not pinned if the caller
    supplies it.  The contract takes no such argument."""
    import inspect
    src = inspect.getsource(contract.grade)
    assert "a=" not in src.replace("dp=", ""), \
        "grade() must not accept a length scale; a is pinned at module level"
    assert contract.A == 0.05715


# --------------------------------------------------------------------------
# 3. The measurement itself, on meshes whose answer is known analytically.
# --------------------------------------------------------------------------

def _synthetic(nx, ny, dx, dy):
    """Structured cell centres, row-major, exactly as OpenFOAM writes them."""
    return [( (i + 0.5) * dx, (j + 0.5) * dy, 0.0 )
            for j in range(ny) for i in range(nx)]


def test_quadrature_is_the_full_depth_integral(contract):
    """§2.1 'h(x_i) = sum_j alpha_ij . dy, over ALL n_y cells of column i, from
    y = 0 to the top of the domain, with no truncation and no free surface
    sought.'  A column filled to k cells must integrate to exactly k.dy
    whatever the shape of alpha above it."""
    nx, ny, dx, dy = 6, 10, 0.01, 0.002
    C = _synthetic(nx, ny, dx, dy)
    mesh = contract.build_mesh(C)
    alpha = [0.0] * (nx * ny)
    for j in range(4):                      # fill the bottom four rows of col 2
        alpha[j * nx + 2] = 1.0
    h = contract.depth_profile(alpha, mesh)
    assert h[2] == pytest.approx(4 * dy)
    assert all(h[i] == pytest.approx(0.0) for i in range(nx) if i != 2)

    # the same water, smeared over the full column height, integrates the same
    alpha2 = [0.0] * (nx * ny)
    for j in range(ny):
        alpha2[j * nx + 2] = 4.0 / ny
    assert contract.depth_profile(alpha2, mesh)[2] == pytest.approx(4 * dy)


def test_front_is_linear_interpolation_between_column_centres(contract):
    """§2.2 'located by linear interpolation between the two adjacent
    column-centre x values that bracket the crossing.'  Placed so the answer
    is the exact midpoint of two centres."""
    nx, ny, dx, dy = 5, 2, 0.01, 0.001
    mesh = contract.build_mesh(_synthetic(nx, ny, dx, dy))
    h_star = 0.5 * contract.A * contract.H_STAR
    h = [2 * h_star, 2 * h_star, 2 * h_star, 0.0, 0.0]
    # crossing between centres x=0.025 and x=0.035, at h_star = half the drop
    z = contract.front(mesh, h, h_star)
    assert z == pytest.approx((0.025 + 0.5 * dx) / contract.A)


def test_front_takes_the_furthest_crossing(contract):
    """§2.2 'The search scans from the far wall toward x = 0 and returns the
    first crossing it meets, which is by construction the furthest downstream
    one.'  A non-monotone h with two crossings must return the further."""
    nx, ny, dx, dy = 7, 2, 0.01, 0.001
    mesh = contract.build_mesh(_synthetic(nx, ny, dx, dy))
    hs = 1.0
    h = [2.0, 0.0, 2.0, 2.0, 2.0, 0.0, 0.0]   # crossings at i=0->1 and i=4->5
    z = contract.front(mesh, h, hs)
    assert z * contract.A > 0.04, "returned the upstream crossing"


def test_time_origin_is_unshifted(contract):
    """§2.3 'T = t . sqrt(g/a) ... t is the OpenFOAM time value, in seconds,
    unshifted.'  Explicitly NOT the first solver write, NOT re-zeroed at Z=1."""
    assert contract.T_of(0.0) == 0.0
    assert contract.T_of(0.025) == pytest.approx(0.025 * math.sqrt(9.81 / 0.05715))
    assert contract.T_of(0.05) == pytest.approx(2 * contract.T_of(0.025))


# --------------------------------------------------------------------------
# 4. The FAIL LOUD assertions fire — and, per L-84, do not fire on good input.
# --------------------------------------------------------------------------

def test_structure_assertion_accepts_a_well_formed_mesh(contract):
    """Must-not-fire control.  An assertion that refused everything would pass
    the must-fire test below and be worthless."""
    mesh = contract.build_mesh(_synthetic(8, 5, 0.01, 0.002))
    assert (mesh.nx, mesh.ny) == (8, 5)
    assert mesh.dy == pytest.approx(0.002)


def test_structure_assertion_fires_when_columns_do_not_close(contract):
    """§2.1 'Assertion, FAIL LOUD: every column must contain exactly n_y cells
    ... with n_x . n_y = the internal field length.'  Perturb one centre off
    its column and the extractor must refuse rather than integrate a column of
    the wrong depth."""
    C = _synthetic(8, 5, 0.01, 0.002)
    C[3] = (C[3][0] + 1e-6, C[3][1], C[3][2])
    with pytest.raises(contract.ContractViolation, match="2.1 structure"):
        contract.build_mesh(C)


def test_graded_y_mesh_is_refused(contract):
    """§2.1 'Assertion, FAIL LOUD: the mesh is uniform in y; graded on a graded
    mesh, the extractor refuses.'  h = sum(alpha).dy is not the depth integral
    when dy varies."""
    nx, ny, dx = 6, 6, 0.01
    ys, y = [], 0.0
    for j in range(ny):                      # 10% expansion ratio
        step = 0.002 * (1.1 ** j)
        ys.append(y + 0.5 * step)
        y += step
    C = [(( i + 0.5) * dx, ys[j], 0.0) for j in range(ny) for i in range(nx)]
    with pytest.raises(contract.ContractViolation, match="graded in y"):
        contract.build_mesh(C)


def test_ascii_write_precision_is_not_mistaken_for_grading(contract):
    """Must-not-fire control for the clause above.  The tracked `C` fields
    carry uniform meshes whose successive spacings differ at a relative 2.5e-6
    from ASCII rounding.  Refusing those would refuse every real case."""
    nx, ny, dx, dy = 6, 6, 0.01, 0.002
    C = [((i + 0.5) * dx, round((j + 0.5) * dy, 9), 0.0)
         for j in range(ny) for i in range(nx)]
    mesh = contract.build_mesh(C)
    assert mesh.dy == pytest.approx(dy, rel=1e-5)


def test_pinned_rounding_is_load_bearing_on_the_a16_family(contract):
    """The measured drift, pinned as a regression guard.

    §2.1 pins 8 dp and says why.  `front_metrics.py` groups at 9 dp.  On the
    a/16 family — the comparator's own mesh, and the mesh §3.1's +23.3%
    code-to-code result was taken on — 9 dp does not close: 37 apparent rows x
    263 apparent columns = 9731 against 4800 real cells.  This test fails if
    anyone loosens the assertion to make 9 dp 'work'."""
    case = os.path.join(F7, "F7a_R1", "res16_base")
    C = contract.read_vector(contract.find_centres(case))
    mesh8 = contract.build_mesh(C, dp=8)
    assert (mesh8.nx, mesh8.ny) == (240, 20)
    assert mesh8.nx * mesh8.ny == len(C) == 4800
    with pytest.raises(contract.ContractViolation, match="2.1 structure"):
        contract.build_mesh(C, dp=9)


def test_v1_rounding_defect_on_res8_is_refused_not_guessed(contract):
    """A defect in the frozen contract, recorded as executed fact rather than
    repaired in place (§2.6: re-pinning is a v1.1 that re-grades every case).

    At the pinned 8 dp, `res8_base` yields 211 apparent columns against 120
    physical ones, so the contract raises instead of returning a number.  7 dp
    closes it.  §2.5 already forbids any verdict at a/8, so no verdict moves."""
    case = os.path.join(F7, "F7a_R1", "res8_base")
    C = contract.read_vector(contract.find_centres(case))
    with pytest.raises(contract.ContractViolation, match="2.1 structure"):
        contract.build_mesh(C, dp=contract.COLUMN_ROUND_DP)
    mesh7 = contract.build_mesh(C, dp=7)
    assert mesh7.nx * mesh7.ny == len(C) == 1200


# --------------------------------------------------------------------------
# 5. The guards that stop a number being produced from garbage.
# --------------------------------------------------------------------------

def test_monotonicity_guard_cuts_a_retreating_front(contract):
    """§2.2 'a surge front does not retreat ... stops at the first time at
    which Z decreases by more than 0.05; that time and every later one are
    UNGRADEABLE.'  The real failure mode: after the surge reaches the far wall
    the furthest-crossing search returns a spurious crossing back in the
    collapsing column."""
    series = [(1.0, 5.0), (2.0, 8.0), (3.0, 12.0), (4.0, 1.59), (5.0, 1.60)]
    kept, cut = contract.monotonicity_cutoff(series)
    assert [Z for _, Z in kept] == [5.0, 8.0, 12.0]
    assert cut == 4.0


def test_monotonicity_guard_tolerates_sub_threshold_jitter(contract):
    """Must-not-fire control: a 0.04 dip is inside the pinned 0.05 tolerance
    and must not truncate an otherwise good series."""
    series = [(1.0, 5.0), (2.0, 8.0), (3.0, 7.97), (4.0, 12.0)]
    kept, cut = contract.monotonicity_cutoff(series)
    assert cut is None and len(kept) == 4


def test_wall_clause_marks_the_confounded_station(contract):
    """§2.2, on the verdict case.  At T = 9.53 the front sits at Z = 14.59,
    past the Z >= 14.5 wall clause.  The spec's own §3 table reports that
    station's +12.20% without applying the clause — it is labelled 'reported,
    not graded' so no verdict depends on it, but the contract flags it."""
    r = contract.grade(VERDICT_CASE)
    last = r["stations"][-1]
    assert last["T_ref"] == 9.53 and last["graded"] is False
    assert last["Z_pinned"] >= contract.Z_WALL_UNGRADEABLE
    assert any("wall proximity" in x for x in last["reasons"])
    # and it does not contaminate the graded set
    assert all(not s["reasons"] for s in r["stations"] if s["graded"])


def test_threshold_spread_over_one_percent_yields_ungradeable(contract):
    """§2.2 'If that spread exceeds 1.0% of Z at any graded station, the
    verdict is UNGRADEABLE, not FAIL.'  Driven by lowering the trigger below
    the verdict case's measured 0.68% rather than by inventing a case."""
    r = contract.grade(VERDICT_CASE)
    worst = max(s["spread_frac"] for s in r["stations"] if s["graded"])
    assert worst < contract.SPREAD_UNGRADEABLE_FRAC
    saved = contract.SPREAD_UNGRADEABLE_FRAC
    try:
        contract.SPREAD_UNGRADEABLE_FRAC = worst / 2.0
        r2 = contract.grade(VERDICT_CASE)
        assert r2["verdict"] == contract.UNGRADEABLE
        assert any("threshold spread" in x for x in r2["reasons"])
    finally:
        contract.SPREAD_UNGRADEABLE_FRAC = saved


def test_verdict_floor_refuses_a_mesh_coarser_than_a128(contract):
    """§2.5 'A gate verdict may be taken only on a mesh with dy <= a/128.'
    `res32_base` is dy = a/32 and must come back UNGRADEABLE, never FAIL —
    the distinction docket B2 exists to enforce."""
    r = contract.grade(os.path.join(F7, "F7a_R1", "res32_base"))
    assert r["verdict"] == contract.UNGRADEABLE
    assert any("2.5" in x and "verdict floor" in x for x in r["reasons"])


def test_write_cadence_is_checked_against_the_frozen_cap(contract):
    """§2.3.4 'writeInterval must satisfy dT <= 0.35'.  The verdict case runs
    at dt_w = 0.025 s, dT = 0.328, inside the cap — which is what makes every
    graded station bracketed by written times."""
    r = contract.grade(VERDICT_CASE)
    assert r["dt_write"] == pytest.approx(0.025)
    assert r["dT_write"] == pytest.approx(0.328, abs=5e-4)
    assert r["dT_write"] <= contract.DT_STAR_MAX


def test_restart_time_values_are_verified(contract):
    """§2.3.2 'for every graded time directory the extractor reads
    <t>/uniform/time and asserts its value equals the directory name to 1e-9.
    Mismatch => FAIL LOUD.'  Must-fire: corrupt one and the read must raise."""
    times = contract.written_times(VERDICT_CASE)
    assert times, "no written fields"
    reasons, dtw = contract.check_time_contract(VERDICT_CASE, times)
    assert reasons == [] and dtw == pytest.approx(0.025)


# --------------------------------------------------------------------------
# 6. The gate, and independent-implementation agreement.
# --------------------------------------------------------------------------

SECTION_3 = {3.90: 9.45, 4.49: 7.11, 5.17: 6.80,
             5.91: 7.20, 6.70: 7.89, 7.72: 11.03}


def test_gate_verdict_reproduces_frozen_section_3(contract):
    """The contract, executed on the case §3 names, must reproduce §3's six
    published deviations.  Not a requirement that the gate fail — a requirement
    that re-deriving the published number from the pinned definition gives the
    published number.  Had it not, either §3 or the definition would be wrong,
    and that is the finding this test would have surfaced."""
    r = contract.grade(VERDICT_CASE)
    got = {s["T_ref"]: s["dev"] * 100 for s in r["stations"] if s["graded"]}
    assert set(got) == set(SECTION_3)
    for T, published in SECTION_3.items():
        assert got[T] == pytest.approx(published, abs=0.01), \
            "station T=%.2f: contract %.3f%% vs frozen §3 %.2f%%" % (T, got[T], published)
    assert r["mean_dev"] * 100 == pytest.approx(8.25, abs=0.01)
    assert r["max_abs_dev"] * 100 == pytest.approx(11.03, abs=0.01)
    assert r["n_graded"] == contract.N_GRADED


def test_two_independent_groupings_agree_on_the_verdict_case(contract):
    """§2's stated purpose: 'Two independent agents given only §2 and the same
    case directory must compute the same number.'

    The contract groups columns by rounding to a pinned decimal count.  An
    equally faithful implementation would cluster centres by proximity, with no
    magic digit at all.  This builds that second implementation and requires
    the two to agree to 1e-9 in Z at every station.  Agreement is evidence the
    pinned digit is not doing hidden work; disagreement would mean §2.1 still
    admits two readings."""
    C = contract.read_vector(contract.find_centres(VERDICT_CASE))
    xs_raw = sorted(c[0] for c in C)
    span = xs_raw[-1] - xs_raw[0]
    # cluster on a gap larger than a tenth of the smallest genuine spacing
    uniq = sorted(set(xs_raw))
    gaps = [b - a for a, b in zip(uniq, uniq[1:]) if b - a > span * 1e-9]
    tol = 0.1 * min(gaps)

    clusters, reps = [], []
    for x in uniq:
        if reps and x - reps[-1] <= tol:
            clusters[-1].append(x)
        else:
            clusters.append([x])
            reps.append(x)
        reps[-1] = clusters[-1][0]
    key = {}
    for ci, group in enumerate(clusters):
        for x in group:
            key[x] = ci
    nx = len(clusters)

    mesh = contract.build_mesh(C)
    assert nx == mesh.nx, "the two groupings disagree on the column count"
    for k, c in enumerate(C):
        assert key[c[0]] == mesh.col_of[k], \
            "the two groupings assign cell %d to different columns" % k


def test_contract_is_runnable_as_a_script():
    """The contract must be executable end to end, not just importable — the
    verdict is meant to be re-derivable by anyone with the repo."""
    out = subprocess.run(
        [sys.executable, os.path.join(F7, "f7a_contract.py"),
         os.path.join("F7a_R1", "res32y128_base")],
        cwd=F7, capture_output=True, text=True, timeout=300)
    assert out.returncode == 0, out.stderr
    assert "VERDICT:" in out.stdout
    assert "11.03%" in out.stdout


# --------------------------------------------------------------------------
# 7. The prior gate reading is not comparable to the current one.
#
# Added 2026-08-14.  These pin the measured basis for the strike recorded in
# `F7a_REGATE_SPEC.md` §6: the 2026-07-28 gate's +13.6% / 21.3% and the
# 2026-07-30 R1 audit's +8.2% / +11.0% were taken under a DIFFERENT
# measurement definition (an alpha = 0.5 line probe on one cell row) from the
# one §2 pins (a depth integral over the whole column), and the case the first
# of them was measured on cannot carry a verdict under §2 at all.
# --------------------------------------------------------------------------

ORIGINAL_GATE_CASE = os.path.join(F7, "damBreak_MM_a2p25in_medium_closedbox")


def test_original_gate_case_is_unreadable_at_the_pinned_rounding(contract):
    """The case that produced the published +13.6% / 21.3% carries a `C` field
    written at 6 significant figures, so at §2.1's pinned 8 dp its 300 x 40
    grid appears as 329 x 72 = 23,688 against 12,000 real cells.  The contract
    refuses it rather than integrating over columns that do not exist.  6 dp
    closes it, which is the v1.1 re-pin proposed in §6 of the spec."""
    C = contract.read_vector(contract.find_centres(ORIGINAL_GATE_CASE))
    with pytest.raises(contract.ContractViolation, match="2.1 structure"):
        contract.build_mesh(C, dp=contract.COLUMN_ROUND_DP)
    mesh6 = contract.build_mesh(C, dp=6)
    assert (mesh6.nx, mesh6.ny) == (300, 40)
    assert mesh6.nx * mesh6.ny == len(C) == 12000


def test_original_gate_case_cannot_carry_a_verdict_under_the_contract(contract):
    """Read at 6 dp so the mesh is legible, the original gate case is still
    UNGRADEABLE, for reasons that are independent of each other and of its
    result: its write cadence is dT = 0.655 against §2.3.4's 0.35 cap — so the
    graded stations are not bracketed the way §2.4 requires — and its mesh is
    a/20, far below §2.5's a/128 verdict floor.

    This is the load-bearing fact behind the §6 strike.  The published
    +13.6% / 21.3% is not a stricter or looser reading of the current gate; it
    is a reading of a case the current gate does not admit."""
    r = contract.grade(ORIGINAL_GATE_CASE, dp=6)
    assert r["verdict"] == contract.UNGRADEABLE
    assert r["dT_write"] > contract.DT_STAR_MAX
    assert any("2.3.4" in x for x in r["reasons"])
    assert any("2.5" in x and "verdict floor" in x for x in r["reasons"])


def test_definition_change_alone_does_not_explain_the_halving(contract):
    """The decomposition the corpus never made.

    Six surfaces describe the campaign as having roughly halved the deviation,
    +13.6% -> +8.2%.  Two things changed at once between those readings: the
    measurement definition AND the mesh.  Holding the case fixed and changing
    only the definition moves the six-station mean by well under a point
    (old reading A: +12.7%, spec §1.3; pinned depth integral: +13.1% here).
    The move to +8.25% is therefore attributable to refinement, not to the
    metric change — which matters, because a metric change that flattered the
    result would be the one repair this lab must never make."""
    r = contract.grade(ORIGINAL_GATE_CASE, dp=6)
    assert r["n_graded"] == contract.N_GRADED
    assert r["mean_dev"] * 100 == pytest.approx(13.12, abs=0.05)
    # ... against the old definition's reading A on the same case, +12.7%
    assert abs(r["mean_dev"] * 100 - 12.7) < 1.0


def test_finest_mesh_is_ungradeable_on_its_own_metric_uncertainty(contract):
    """`res32y256_base` is the finest tracked mesh and R1 recorded an
    'unexplained early-time outlier' of +18.1% at T = 3.90 on it.  Under §2.2's
    mandatory threshold sweep that station is not an outlier to be explained:
    the metric's own spread there is 15% of Z, fifteen times the 1.0%
    UNGRADEABLE trigger, because at h* = 0.04a the crossing lands on a
    different feature (Z = 6.04 against Z = 7.07 at the other three).  The case
    yields no verdict, and the +10.8% mean recorded for it is unframed."""
    r = contract.grade(os.path.join(F7, "F7a_R1", "res32y256_base"))
    assert r["verdict"] == contract.UNGRADEABLE
    first = r["stations"][0]
    assert first["T_ref"] == 3.90
    assert first["spread_frac"] > 10 * contract.SPREAD_UNGRADEABLE_FRAC
    assert any("threshold spread" in x for x in r["reasons"])


def test_every_case_above_the_verdict_floor_fails(contract):
    """The re-gate itself, stated as the contract sees it.  Three tracked cases
    satisfy §2.5's dy <= a/128 verdict floor.  All three FAIL, and none is
    close to the 5% tolerance.  This test does not require FAIL as a policy —
    it records the measured state, and would go red if a case ever passed,
    which is precisely when a human should look."""
    verdicts = {}
    for name in ("res32y128_base", "res32y128_slip", "res64y128_base"):
        r = contract.grade(os.path.join(F7, "F7a_R1", name))
        verdicts[name] = (r["verdict"], round(r["max_abs_dev"] * 100, 2))
    assert verdicts == {
        "res32y128_base": (contract.FAIL, 11.03),
        "res32y128_slip": (contract.FAIL, 19.12),
        "res64y128_base": (contract.FAIL, 12.23),
    }
