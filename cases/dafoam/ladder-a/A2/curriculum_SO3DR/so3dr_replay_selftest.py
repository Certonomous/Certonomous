#!/usr/bin/env python3
"""SELFTEST for `so3dr_replay.py` -- every guard, refusal, control and gate of the
SO-3D Stage-1 reader, driven IN BOTH DIRECTIONS on synthetic fixtures.

WHAT THIS IS NOT.  It is not a run of the item.  It never reads a registered
log, never creates the item's run root, and never writes `so3dr_replay.json`
or `so3dr_plant_report.json` anywhere the grading path would look.  It drives
the reader's own functions on fixture text so that a guard is shown able to
FIRE and able to REFUSE before the item is ever launched.

WHY IT IS A SEPARATE FILE.  The grading path is fixed at the pre-registration
commit (CLAUDE.md rule 2).  Giving `so3dr_replay.py` a fixture-root override
would make the reader steerable at anything; keeping the selftest outside it
leaves the reader's registered log paths hard-pinned.

NO `assert` STATEMENT ANYWHERE.  `assert` vanishes under `python3 -O`, so every
control here is an explicit comparison that raises or records a FAIL.  This file
is driven under BOTH `python3` and `python3 -O` and the counts must match.

Exit 0 iff every control passed.  Exit 1 otherwise.
"""

import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("so3d_replay",
                                               os.path.join(HERE, "so3dr_replay.py"))
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

RESULTS = []


def control(name, expectation, fn):
    """Run one control.  A control that raises an UNEXPECTED exception FAILS;
    it is never reported as a skip."""
    try:
        ok, detail = fn()
    except Exception as exc:  # noqa: BLE001 -- an unexpected raise is a failure
        RESULTS.append((name, "FAIL", "unexpected %s: %s" % (type(exc).__name__, exc),
                        expectation))
        return
    RESULTS.append((name, "PASS" if ok else "FAIL", detail, expectation))


def raises_refusal(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except R.Refusal as e:
        return True, str(e)[:110]
    except Exception as e:  # noqa: BLE001
        return False, "raised %s, not Refusal: %s" % (type(e).__name__, e)
    return False, "did NOT refuse"


# --------------------------------------------------------------------------
# FIXTURE BUILDER -- a synthetic multipoint log with the real grammar.
# --------------------------------------------------------------------------

def primal(aoa, n, fail, min_res="7.087799823e-05", tol="1e-08", cl="0.395"):
    out = [
        "DAInputPatchVelocity.",
        "Setting UMag = 100 AoA = %.10g degs at 1(inout)" % aoa,
        "Running Primal Solver %03d" % n,
        "Starting time loop",
        "",
        "Time = 1",
        "U0 initRes: 1 finalRes: 0.07246058778 nIters: 2",
        "p initRes: 1 finalRes: 0.08627240635 nIters: 3",
        "CD: 0.2755944628 final: 0.2755944628",
        "CL: -0.01342655597 final: -0.01342655597",
        "ExecutionTime = 3.29 s  ClockTime = 13 s",
        "",
        "Time = 1000",
        "U0 initRes: 1.018312114e-07 finalRes: 8.5861765e-09 nIters: 1",
        "p initRes: %s finalRes: 5.538984676e-06 nIters: 1" % min_res,
        "CD: 0.0241773412 final: 0.0241773412",
        "CL: %s final: %s" % (cl, cl),
        "ExecutionTime = 4162.9 s  ClockTime = 4199 s",
        "",
        "End",
        "",
        "Printing Primal Residual Statistics.",
        "p Residual Norm2: 279.7186365",
    ]
    if fail:
        out += [
            "********************************************",
            "Primal min residual %s" % min_res,
            "did not satisfy the prescribed tolerance %s" % tol,
            "Primal solution failed!",
            "********************************************",
        ]
    return out


def fixture(iters, fail_pattern, cutback_after=(), pad_head=0, pad_between=0):
    """`fail_pattern[k]` is a 3-tuple of booleans, one per scenario."""
    lines = ["/* fixture header */"] * pad_head
    lines += ["Finding a feasible design using the Newton method.",
              "Constraints:  ['cl04.aero_post.CL', 'cl05.aero_post.CL', 'cl06.aero_post.CL']",
              "Target:  [0.4, 0.5, 0.6]"]
    lines += primal(4.0, 1, False)          # PRETRIM record
    n = 2
    for k in range(iters):
        a = [0.5 + k * 0.01, 1.7 + k * 0.01, 3.0 + k * 0.01]
        lines += [
            "Driver debug print for iter coord: rank0:pyOptSparse_IPOPT|%d" % k,
            "-------------------------------------------------------------",
            "Design Vars",
            "{'dvs.patchV_cl04': array([100.        ,   %.8f]),"  % a[0],
            " 'dvs.patchV_cl05': array([100.        ,   %.8f]),"  % a[1],
            " 'dvs.patchV_cl06': array([100.        ,   %.8f]),"  % a[2],
            " 'dvs.shape': array([-0.01866365,  0.01008614])}",
        ]
        for si in range(3):
            lines += primal(a[si], n, fail_pattern[k][si])
            n += 1
            lines += [""] * pad_between
        lines += ["Nonlinear constraints",
                  "{'cl04.aero_post.functionals.CL': array([0.38985507])}",
                  "Objectives",
                  "{'obj.J': array([0.02811773])}"]
        if k in cutback_after:
            lines.append("Warning: Cutting back alpha due to evaluation error")
    return lines


# --------------------------------------------------------------------------
# CONTROLS
# --------------------------------------------------------------------------

def c_root_guard_absent():
    with tempfile.TemporaryDirectory() as d:
        old = R.RUN_ROOT
        R.RUN_ROOT = os.path.join(d, "does_not_exist")
        try:
            R.guard_run_root_absent()
            return True, "absent root accepted"
        finally:
            R.RUN_ROOT = old


def c_root_guard_present():
    with tempfile.TemporaryDirectory() as d:
        old = R.RUN_ROOT
        R.RUN_ROOT = d
        try:
            return raises_refusal(R.guard_run_root_absent)
        finally:
            R.RUN_ROOT = old


def _with_logs(mapping, fn):
    old = dict(R.LOGS)
    R.LOGS.clear()
    R.LOGS.update(mapping)
    try:
        return fn()
    finally:
        R.LOGS.clear()
        R.LOGS.update(old)


def c_logs_present_ok():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "a.log")
        open(p, "w").write("hello\n")
        out = _with_logs({"X": p}, R.verify_logs_present)
        ok = out["X"]["bytes"] == 6 and len(out["X"]["sha256"]) == 64
        return ok, "bytes=%d sha=%s..." % (out["X"]["bytes"], out["X"]["sha256"][:12])


def c_logs_missing():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "nope.log")
        return _with_logs({"X": p}, lambda: raises_refusal(R.verify_logs_present))


def c_logs_empty():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "empty.log")
        open(p, "w").close()
        return _with_logs({"X": p}, lambda: raises_refusal(R.verify_logs_present))


def c_census_sees_planted_nan():
    lines = ["CD: 0.024 final: 0.024", "CD: nan final: nan", "p initRes: 1 finalRes: 2 nIters: 1"]
    out = R.nonfinite_census(lines)
    return out["count"] == 2 and out["hits"][0]["line"] == 2, "count=%d" % out["count"]


def c_census_zero_on_clean():
    lines = ["CD: 0.024 final: 0.024", "p initRes: 1 finalRes: 2 nIters: 1",
             "ExecutionTime = 3.29 s  ClockTime = 13 s"]
    out = R.nonfinite_census(lines)
    return out["count"] == 0, "count=%d" % out["count"]


def c_census_does_not_match_info_words():
    lines = ["Info: nothing infinite here", "reading /path/to/info/nan_dir/file",
             "nanoseconds elapsed", "Infinity is not a token"]
    out = R.nonfinite_census(lines, restrict_to_numeric_prints=False)
    return out["count"] == 0, "unrestricted count=%d hits=%r" % (
        out["count"], [h["token"] for h in out["hits"]])


def c_census_window_respected():
    lines = ["CD: 0.1 final: 0.1", "CD: nan final: nan", "CD: nan final: nan"]
    inside = R.nonfinite_census(lines, 1)
    outside = R.nonfinite_census(lines, 3)
    return inside["count"] == 0 and outside["count"] == 4, (
        "windowed=%d full=%d" % (inside["count"], outside["count"]))


def c_attribute_exact():
    s, gap = R.attribute_aoa(0.5780466691, {"cl04": 0.57804667, "cl05": 1.77215221,
                                            "cl06": 3.03876289})
    return s == "cl04", "scenario=%r gap=%r" % (s, gap)


def c_attribute_out_of_tolerance():
    s, why = R.attribute_aoa(9.9, {"cl04": 0.578, "cl05": 1.772, "cl06": 3.038})
    return s is None and "exceeds tol" in str(why), "scenario=%r why=%r" % (s, why)


def c_attribute_ambiguous():
    """Two candidates inside the tolerance, one of them an EXACT match. A
    nearest-wins reader answers `cl04` here; the registered rule must not."""
    s, why = R.attribute_aoa(1.0000000, {"cl04": 1.0000000, "cl05": 1.0000001})
    return s is None and "ambiguous" in str(why), "scenario=%r why=%r" % (s, why)


def c_attribute_no_block():
    s, why = R.attribute_aoa(1.0, {})
    return s is None, "why=%r" % (why,)


def c_records_attributed():
    lines = fixture(2, [(False, False, True), (False, True, True)])
    ps = R.per_scenario_rates(R.parse_primal_records(lines))
    ok = (ps["starts"] == {"cl04": 2, "cl05": 2, "cl06": 2}
          and ps["banners"] == {"cl04": 0, "cl05": 1, "cl06": 2}
          and ps["pretrim"] == 1 and ps["unattributed"] == 0)
    return ok, "starts=%r banners=%r pretrim=%d unattr=%d" % (
        ps["starts"], ps["banners"], ps["pretrim"], ps["unattributed"])


def c_pretrim_named_not_dropped():
    lines = fixture(1, [(False, False, False)])
    ps = R.per_scenario_rates(R.parse_primal_records(lines))
    return ps["pretrim"] == 1 and any("PRETRIM" in k for k in ps["unattributed_reasons"]), \
        "pretrim=%d reasons=%r" % (ps["pretrim"], ps["unattributed_reasons"])


def c_unattributed_counted_not_folded():
    lines = fixture(1, [(False, False, False)])
    # Corrupt one primal's AoA so it matches no design variable.
    for i, ln in enumerate(lines):
        if ln.startswith("Setting UMag = 100 AoA = 1.7"):
            lines[i] = "Setting UMag = 100 AoA = 88.5 degs at 1(inout)"
            break
    ps = R.per_scenario_rates(R.parse_primal_records(lines))
    ok = ps["unattributed"] == 1 and ps["starts"]["cl05"] == 0
    return ok, "unattr=%d starts=%r" % (ps["unattributed"], ps["starts"])


def c_design_vars_malformed_refuses():
    lines = ["Driver debug print for iter coord: rank0:pyOptSparse_IPOPT|0",
             "Design Vars",
             "{'dvs.patchV_cl04': array([100.]),"]
    return raises_refusal(R.parse_design_vars_blocks, lines)


def c_umag_nonnumeric_refuses():
    lines = ["Setting UMag = 100 AoA = ABC degs at 1(inout)", "Time = 1"]
    return raises_refusal(R.parse_primal_records, lines)


def c_minres_nonnumeric_refuses():
    lines = ["Time = 1", "End", "Primal min residual NOTANUMBER"]
    return raises_refusal(R.parse_primal_records, lines)


def c_residual_classification():
    lines = fixture(1, [(True, False, False)])
    recs = R.parse_primal_records(lines)
    failed = [r for r in recs if r["residual_converged"] is False]
    none_ = [r for r in recs if r["residual_converged"] is None]
    return len(failed) == 1 and len(none_) == 3, "failed=%d none=%d" % (
        len(failed), len(none_))


def c_plant_a_applies():
    lines = fixture(2, [(False, False, True), (False, True, True)])
    old = R.PLANT_A_FROM_LINE
    R.PLANT_A_FROM_LINE = 1
    try:
        out, meta = R.apply_plant_a(lines)
        return "CD: nan" in out[meta["line"] - 1], "line=%d" % meta["line"]
    finally:
        R.PLANT_A_FROM_LINE = old


def c_plant_a_refuses_when_absent():
    old = R.PLANT_A_FROM_LINE
    R.PLANT_A_FROM_LINE = 1
    try:
        return raises_refusal(R.apply_plant_a, ["no cd lines here", "Time = 1"])
    finally:
        R.PLANT_A_FROM_LINE = old


def c_plant_b_applies():
    lines = fixture(2, [(False, False, True), (False, True, True)])
    olds = (R.PLANT_B_DELETE_FROM_LINE, R.PLANT_B_INSERT_AFTER_END_FROM_LINE)
    # delete the LAST banner, insert after an early End
    R.PLANT_B_DELETE_FROM_LINE = max(i for i, l in enumerate(lines, 1)
                                     if l == "Primal solution failed!")
    R.PLANT_B_INSERT_AFTER_END_FROM_LINE = 1
    try:
        out, meta = R.apply_plant_b(lines)
        n0 = sum(1 for l in lines if l == "Primal solution failed!")
        n1 = sum(1 for l in out if l == "Primal solution failed!")
        return n0 == n1 and len(out) == len(lines), "banners %d->%d meta=%r" % (n0, n1, meta)
    finally:
        (R.PLANT_B_DELETE_FROM_LINE, R.PLANT_B_INSERT_AFTER_END_FROM_LINE) = olds


def c_plant_b_refuses_when_no_banner():
    olds = (R.PLANT_B_DELETE_FROM_LINE, R.PLANT_B_INSERT_AFTER_END_FROM_LINE)
    R.PLANT_B_DELETE_FROM_LINE = 1
    R.PLANT_B_INSERT_AFTER_END_FROM_LINE = 1
    try:
        return raises_refusal(R.apply_plant_b, ["Time = 1", "End"])
    finally:
        (R.PLANT_B_DELETE_FROM_LINE, R.PLANT_B_INSERT_AFTER_END_FROM_LINE) = olds


def c_plant_b_refuses_when_anchors_inverted():
    lines = ["End", "Primal solution failed!"]
    olds = (R.PLANT_B_DELETE_FROM_LINE, R.PLANT_B_INSERT_AFTER_END_FROM_LINE)
    R.PLANT_B_DELETE_FROM_LINE = 1
    R.PLANT_B_INSERT_AFTER_END_FROM_LINE = 1
    try:
        # deletion anchor lands at line 2, insertion anchor at line 1 -> legal;
        # invert by forcing the insertion search to start after the deletion.
        R.PLANT_B_INSERT_AFTER_END_FROM_LINE = 3
        return raises_refusal(R.apply_plant_b, lines + ["End"])
    finally:
        (R.PLANT_B_DELETE_FROM_LINE, R.PLANT_B_INSERT_AFTER_END_FROM_LINE) = olds


def c_plant_c_scales():
    lines = fixture(1, [(True, False, False)])
    old = R.PLANT_C_FROM_LINE
    R.PLANT_C_FROM_LINE = 1
    try:
        out, meta = R.apply_plant_c(lines)
        return abs(meta["R_scaled"] - meta["R"] * 1e-4) < 1e-30 and \
            out[meta["line"] - 1].startswith("Primal min residual"), \
            "R=%g -> %g" % (meta["R"], meta["R_scaled"])
    finally:
        R.PLANT_C_FROM_LINE = old


def c_plant_c_refuses_when_absent():
    old = R.PLANT_C_FROM_LINE
    R.PLANT_C_FROM_LINE = 1
    try:
        return raises_refusal(R.apply_plant_c, ["Time = 1", "End"])
    finally:
        R.PLANT_C_FROM_LINE = old


def _plant_env(lines):
    """Scale every frozen plant anchor down to the fixture and return the olds."""
    olds = (R.PLANT_A_FROM_LINE, R.PLANT_B_DELETE_FROM_LINE,
            R.PLANT_B_INSERT_AFTER_END_FROM_LINE, R.PLANT_C_FROM_LINE,
            R.D6R_CENSUS_LAST_LINE, R.PLANT_B_TOTAL_BANNERS_EXPECTED)
    R.PLANT_A_FROM_LINE = 1
    R.PLANT_B_DELETE_FROM_LINE = max(i for i, l in enumerate(lines, 1)
                                     if l == "Primal solution failed!")
    R.PLANT_B_INSERT_AFTER_END_FROM_LINE = 1
    R.PLANT_C_FROM_LINE = 1
    R.D6R_CENSUS_LAST_LINE = len(lines)
    R.PLANT_B_TOTAL_BANNERS_EXPECTED = sum(1 for l in lines
                                           if l == "Primal solution failed!")
    return olds


def _plant_restore(olds):
    (R.PLANT_A_FROM_LINE, R.PLANT_B_DELETE_FROM_LINE,
     R.PLANT_B_INSERT_AFTER_END_FROM_LINE, R.PLANT_C_FROM_LINE,
     R.D6R_CENSUS_LAST_LINE, R.PLANT_B_TOTAL_BANNERS_EXPECTED) = olds



def _blind_attribution():
    """Replace attribution with a reader that names NO scenario -- the honest
    way to simulate blindness. Squeezing AOA_MATCH_ABS_TOL does NOT do it: the
    fixture prints the same AoA on both sides, so the gap is exactly 0.0 and no
    tolerance can exclude it. That mistake made an earlier version of the
    GATE-P-ATTRIB control pass for the WRONG REASON -- it was refusing because
    its insertion anchor landed in the PRETRIM record, not because attribution
    was broken. Found by this file's own PLANT-INCREMENTAL control."""
    old = R.attribute_aoa
    R.attribute_aoa = lambda v, m: (None, "blinded by the control")
    return old


def _unblind(old):
    R.attribute_aoa = old

def _same_scenario_fixture():
    """A fixture in which BOTH plant anchors land in the SAME scenario -- the
    configuration the real D6R log deterministically produces, and the one the
    predecessor's per-scenario predicate cannot score. cl04 is the first primal
    of every iteration, so iteration 0's cl04 owns the insertion `End` and
    iteration 2's cl04 owns the last banner."""
    lines = fixture(3, [(True, False, False), (False, True, False),
                        (True, False, False)])
    olds = _plant_env(lines)
    # delete anchor: the LAST banner, which belongs to iteration 2's cl04
    R.PLANT_B_DELETE_FROM_LINE = max(i for i, l in enumerate(lines, 1)
                                     if l == "Primal solution failed!")
    # insert anchor: the first `End` at or after iteration 0's cl04 primal
    first_dv = next(i for i, l in enumerate(lines, 1)
                    if l.startswith("Driver debug print"))
    R.PLANT_B_INSERT_AFTER_END_FROM_LINE = first_dv
    return lines, olds


def c_plant_control_passes_on_sound_reader():
    lines, olds = _same_scenario_fixture()
    try:
        rep = R.score_plant_control(lines)
        pb = rep["plants"]["PLANT-B"]
        owners = set(pb["owning_scenarios"].values())
        ok = (rep["status"] == "PASS" and len(pb["record_moves_by_ordinal"]) == 2
              and owners == {"cl04"})
        return ok, "status=%s moves=%r owners=%r per_scenario=%r" % (
            rep["status"], pb["record_moves_by_ordinal"], pb["owning_scenarios"],
            pb["per_scenario_moves_REPORTED_BESIDE_NOT_INSTEAD"])
    finally:
        _plant_restore(olds)


def c_plantB_passes_with_both_anchors_in_one_scenario():
    """THE CONTROL THIS SUCCESSOR EXISTS FOR. Both anchors owned by one scenario
    is exactly where the predecessor refused; the record-level predicate must
    PASS here, and the per-scenario vector it reports beside must be all zeros --
    proving the vector is carried as disclosure and is NOT what is scored."""
    lines, olds = _same_scenario_fixture()
    try:
        rep = R.score_plant_control(lines)
        pb = rep["plants"]["PLANT-B"]
        scen = pb["per_scenario_moves_REPORTED_BESIDE_NOT_INSTEAD"]
        ok = (pb["status"] == "PASS"
              and all(v == 0 for v in scen.values())
              and sorted(pb["record_moves_by_ordinal"].values()) == [-1, 1])
        return ok, "record moves=%r  per-scenario (reported, not scored)=%r" % (
            pb["record_moves_by_ordinal"], scen)
    finally:
        _plant_restore(olds)


def c_degeneracy_is_real_literal_frozen_predicate():
    """PROVES THE FINDING RATHER THAN ASSERTING IT. Evaluates the PREDECESSOR's
    LITERALLY-FROZEN per-scenario expectation -- `-1 in the scenario owning the
    deleted banner, +1 in the scenario owning the inserted one, total unchanged`
    -- for a CORRECT reader and for a TOTALLY BLIND one on the same bytes. If
    the two are indistinguishable, the frozen control tests nothing."""
    lines, olds = _same_scenario_fixture()
    try:
        b_lines, _ = R.apply_plant_b(lines)
        rb = R.parse_primal_records(lines)
        ra = R.parse_primal_records(b_lines)

        def scen_vector(recs, blind):
            v = {sc: 0 for sc in R.SCENARIOS}
            tot = 0
            for rec in recs:
                tot += rec["banners"]
                sc = None if blind else rec["scenario"]
                if sc is not None:
                    v[sc] += rec["banners"]
            return v, tot

        sigs = {}
        for blind in (False, True):
            v0, t0 = scen_vector(rb, blind)
            v1, t1 = scen_vector(ra, blind)
            sigs[blind] = ({sc: v1[sc] - v0[sc] for sc in R.SCENARIOS}, t0, t1)
        correct, blind = sigs[False], sigs[True]
        degenerate = (correct == blind)
        return degenerate, ("correct=%r blind=%r -- IDENTICAL, so the frozen "
                            "per-scenario predicate cannot separate them"
                            % (correct, blind))
    finally:
        _plant_restore(olds)


def c_plantB_refuses_a_blind_reader():
    """And the successor's predicate DOES separate them: a reader that can name
    no owning scenario must refuse, even though it still sees both record
    deltas -- ordinals need no attribution."""
    lines, olds = _same_scenario_fixture()
    old = _blind_attribution()
    try:
        return raises_refusal(R.score_plant_control, lines)
    finally:
        _unblind(old)
        _plant_restore(olds)


def c_plantB_refuses_record_count_change():
    lines, olds = _same_scenario_fixture()
    real = R.apply_plant_b
    def bad(ls):
        out, meta = real(ls)
        return out + ["Time = 1", "End"], meta      # invents a record
    R.apply_plant_b = bad
    try:
        return raises_refusal(R.score_plant_control, lines)
    finally:
        R.apply_plant_b = real
        _plant_restore(olds)


def c_plantB_refuses_rps_label_drift():
    lines, olds = _same_scenario_fixture()
    real = R.apply_plant_b
    def bad(ls):
        out, meta = real(ls)
        out = list(out)
        for i, l in enumerate(out):
            if l.startswith("Running Primal Solver"):
                out[i] = "Running Primal Solver 999"   # relabels every record
        return out, meta
    R.apply_plant_b = bad
    try:
        return raises_refusal(R.score_plant_control, lines)
    finally:
        R.apply_plant_b = real
        _plant_restore(olds)


def c_plant_report_is_incremental():
    """PLANT-A's PASS must be a FACT ON DISK even when PLANT-B refuses. The
    predecessor wrote its report only on full success, so a refusal at PLANT-B
    left PLANT-A's pass inferable only from source ordering."""
    lines, olds = _same_scenario_fixture()
    old = _blind_attribution()           # force a PLANT-B refusal
    seen = []
    try:
        try:
            R.score_plant_control(lines, None, lambda partial: seen.append(partial))
        except R.Refusal:
            pass
        if not seen:
            return False, "no snapshot was emitted before the refusal"
        last = seen[-1]
        a = last["plants"]["PLANT-A"]["status"]
        b = last["plants"]["PLANT-B"]["status"]
        c = last["plants"]["PLANT-C"]["status"]
        ok = (a == "PASS" and b == "REFUSE" and c == "NOT RUN")
        return ok, "snapshots=%d  A=%s B=%s C=%s" % (len(seen), a, b, c)
    finally:
        _unblind(old)
        _plant_restore(olds)


def c_not_run_is_not_pass():
    """An unreached plant is NOT RUN in the artifact -- never absent, never PASS."""
    lines, olds = _same_scenario_fixture()
    old = _blind_attribution()
    seen = []
    try:
        try:
            R.score_plant_control(lines, None, lambda partial: seen.append(partial))
        except R.Refusal:
            pass
        c = seen[-1]["plants"]["PLANT-C"]
        return c["status"] == "NOT RUN" and "NOT RUN is not PASS" in c["note"], \
            "PLANT-C=%r" % c
    finally:
        _unblind(old)
        _plant_restore(olds)


def c_record_ordinal_is_shift_invariant():
    """The key PLANT-B is scored on must survive the plant's own line shift --
    which is precisely what `start_line` does NOT do."""
    lines, olds = _same_scenario_fixture()
    try:
        b_lines, meta = R.apply_plant_b(lines)
        rb = R.parse_primal_records(lines)
        ra = R.parse_primal_records(b_lines)
        ords_ok = [r["ordinal"] for r in rb] == [r["ordinal"] for r in ra]
        ids_ok = [r["rps_id"] for r in rb] == [r["rps_id"] for r in ra]
        starts_moved = sum(1 for x, y in zip(rb, ra)
                           if x["start_line"] != y["start_line"])
        return ords_ok and ids_ok and starts_moved > 0, (
            "ordinals stable=%s rps labels stable=%s  start_line MOVED for %d "
            "records, which is why start_line cannot be the key"
            % (ords_ok, ids_ok, starts_moved))
    finally:
        _plant_restore(olds)


def c_plant_control_refuses_a_blinded_census():
    """A reader that cannot see the planted `nan` because the CD line is out of
    its own in-scope whitelist MUST refuse.  This is the direction that matters:
    the control exists to make a clean sheet unbelievable."""
    lines = fixture(3, [(False, False, True), (False, True, True),
                        (True, False, True)])
    olds = _plant_env(lines)
    old_pats = list(R.NUMERIC_PRINT_PATTERNS)
    del R.NUMERIC_PRINT_PATTERNS[:]      # blind the census
    try:
        return raises_refusal(R.score_plant_control, lines)
    finally:
        R.NUMERIC_PRINT_PATTERNS.extend(old_pats)
        _plant_restore(olds)


def c_plant_control_refuses_broken_attribution():
    """A reader whose AoA tolerance is so tight that nothing attributes must
    refuse at PLANT-B rather than report three empty scenarios."""
    lines, olds = _same_scenario_fixture()
    old = _blind_attribution()
    try:
        return raises_refusal(R.score_plant_control, lines)
    finally:
        _unblind(old)
        _plant_restore(olds)


def c_plant_control_refuses_wrong_total():
    lines = fixture(3, [(False, False, True), (False, True, True),
                        (True, False, True)])
    olds = _plant_env(lines)
    first_dv = next(i for i, l in enumerate(lines, 1)
                    if l.startswith("Driver debug print"))
    R.PLANT_B_INSERT_AFTER_END_FROM_LINE = first_dv
    R.PLANT_B_TOTAL_BANNERS_EXPECTED = 999999
    try:
        return raises_refusal(R.score_plant_control, lines)
    finally:
        _plant_restore(olds)


def c_plant_control_refuses_blinded_residual_classifier():
    """A reader that never reads the prescribed tolerance classifies every record
    as None, so PLANT-C's registered flip cannot happen. It must REFUSE rather
    than report `no record moved` as a clean sheet."""
    import re as _re
    lines = fixture(3, [(False, False, True), (False, True, True),
                        (True, False, True)])
    olds = _plant_env(lines)
    first_dv = next(i for i, l in enumerate(lines, 1)
                    if l.startswith("Driver debug print"))
    R.PLANT_B_INSERT_AFTER_END_FROM_LINE = first_dv
    old_re = R.RE_TOL_LINE
    R.RE_TOL_LINE = _re.compile(r"^THIS STRING NEVER APPEARS$")
    try:
        return raises_refusal(R.score_plant_control, lines)
    finally:
        R.RE_TOL_LINE = old_re
        _plant_restore(olds)


def c_coupling_detects_coupled():
    lines = fixture(2, [(False, False, True), (False, True, True)],
                    cutback_after=(0, 1))
    out = R.cutback_coupling(lines)
    return out["cutbacks"] == 2 and out["fraction"] == 1.0, "%r" % out["fraction"]


def c_coupling_detects_uncoupled():
    lines = fixture(2, [(False, False, False), (False, False, False)],
                    cutback_after=(0, 1))
    out = R.cutback_coupling(lines)
    return out["cutbacks"] == 2 and out["fraction"] == 0.0, "%r" % out["fraction"]


def c_coupling_zero_cutbacks_is_none():
    lines = fixture(1, [(False, False, False)])
    out = R.cutback_coupling(lines)
    return out["cutbacks"] == 0 and out["fraction"] is None, "%r" % out


def c_control_rate():
    lines = fixture(2, [(False, False, True), (False, True, True)])
    out = R.control_rate(lines)
    return out["starts"] == 7 and out["banners"] == 3, "%r" % out


def c_clock_cap_fires():
    clk = R.Clock(cap_wall_s=0.0)
    try:
        clk.check("selftest")
    except R.CostCap as e:
        return "BLOCKED on cost" in str(e), str(e)[:80]
    return False, "cap did not fire"


def c_clock_cap_does_not_fire_early():
    clk = R.Clock(cap_wall_s=10000.0)
    clk.check("selftest")
    return True, "no premature stop"


def _gate_inputs(rates, nonfinite, coupling_fraction):
    census = {"count": nonfinite, "count_unrestricted": nonfinite, "hits": [],
              "hits_unrestricted": [], "window_last_line": 100}
    ps = {"starts": {s: 10 for s in R.SCENARIOS},
          "banners": {s: 0 for s in R.SCENARIOS}, "rates": rates,
          "unattributed": 0, "pretrim": 0, "unattributed_reasons": {},
          "cl_targets": R.CL_TARGETS}
    coup = {"cutbacks": 100 if coupling_fraction is not None else 0,
            "coupled": 0, "fraction": coupling_fraction,
            "banner_count_distribution": {},
            "cutbacks_with_no_preceding_driver_block": 0}
    return census, ps, coup, {}


def c_gate1_can_pass_and_fail():
    a = R.score_gates(*_gate_inputs({"cl04": .1, "cl05": .2, "cl06": .3}, 0, 1.0))
    b = R.score_gates(*_gate_inputs({"cl04": .1, "cl05": .2, "cl06": .3}, 7, 1.0))
    return (a["G-SO3D-1"]["verdict"] == "PASS"
            and b["G-SO3D-1"]["verdict"] == "GATE FAIL"), \
        "%s / %s" % (a["G-SO3D-1"]["verdict"], b["G-SO3D-1"]["verdict"])


def c_gate2_can_pass_fail_and_not_a_result():
    a = R.score_gates(*_gate_inputs({"cl04": .1, "cl05": .2, "cl06": .3}, 0, 1.0))
    b = R.score_gates(*_gate_inputs({"cl04": .3, "cl05": .2, "cl06": .1}, 0, 1.0))
    c = R.score_gates(*_gate_inputs({"cl04": None, "cl05": .2, "cl06": .3}, 0, 1.0))
    return (a["G-SO3D-2"]["verdict"] == "PASS"
            and b["G-SO3D-2"]["verdict"] == "GATE FAIL"
            and c["G-SO3D-2"]["verdict"] == "NOT A RESULT"), \
        "%s / %s / %s" % (a["G-SO3D-2"]["verdict"], b["G-SO3D-2"]["verdict"],
                          c["G-SO3D-2"]["verdict"])


def c_gate3_can_pass_and_fail():
    a = R.score_gates(*_gate_inputs({"cl04": .12, "cl05": .2, "cl06": .3}, 0, 1.0))
    b = R.score_gates(*_gate_inputs({"cl04": .05, "cl05": .2, "cl06": .3}, 0, 1.0))
    return (a["G-SO3D-3"]["verdict"] == "PASS"
            and b["G-SO3D-3"]["verdict"] == "GATE FAIL"), \
        "%s / %s" % (a["G-SO3D-3"]["verdict"], b["G-SO3D-3"]["verdict"])


def c_gate4_can_pass_fail_and_not_a_result():
    a = R.score_gates(*_gate_inputs({"cl04": .1, "cl05": .2, "cl06": .3}, 0, 0.95))
    b = R.score_gates(*_gate_inputs({"cl04": .1, "cl05": .2, "cl06": .3}, 0, 0.50))
    c = R.score_gates(*_gate_inputs({"cl04": .1, "cl05": .2, "cl06": .3}, 0, None))
    return (a["G-SO3D-4"]["verdict"] == "PASS"
            and b["G-SO3D-4"]["verdict"] == "GATE FAIL"
            and c["G-SO3D-4"]["verdict"] == "NOT A RESULT"), \
        "%s / %s / %s" % (a["G-SO3D-4"]["verdict"], b["G-SO3D-4"]["verdict"],
                          c["G-SO3D-4"]["verdict"])


def c_null_criterion_triggers():
    g = R.score_gates(*_gate_inputs({"cl04": .3, "cl05": .2, "cl06": .1}, 0, 0.5))
    n = R.null_result_criterion(g)
    return n["triggered"] and n["mechanism_finding"] == "NOT A RESULT", "%r" % n["triggered"]


def c_null_criterion_does_not_trigger():
    g = R.score_gates(*_gate_inputs({"cl04": .12, "cl05": .2, "cl06": .3}, 0, 0.95))
    n = R.null_result_criterion(g)
    return not n["triggered"], "%r" % n["triggered"]


def c_no_assert_statements_in_reader():
    """CLAUDE.md: no `assert` may carry a refusal, guard, control or gate --
    they vanish under `python3 -O`.  This control proves there are none at all,
    in EITHER file, by parsing the source rather than grepping it."""
    import ast
    bad = []
    for fn in ("so3dr_replay.py", "so3dr_replay_selftest.py"):
        tree = ast.parse(open(os.path.join(HERE, fn)).read())
        n = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Assert))
        if n:
            bad.append("%s:%d" % (fn, n))
    return not bad, "assert statements found: %r" % (bad or "none")


def c_optimize_flag_reported():
    """Report which interpreter mode this invocation is in, so the two runs are
    distinguishable in the evidence file rather than assumed different."""
    return True, "__debug__=%s (python3 -O sets it False)" % __debug__


CONTROLS = [
    ("RUNROOT-ABSENT", "an absent run root is accepted", c_root_guard_absent),
    ("RUNROOT-PRESENT", "an existing run root REFUSES", c_root_guard_present),
    ("LOGS-OK", "a present non-empty log is accepted with sha256", c_logs_present_ok),
    ("LOGS-MISSING", "a missing log REFUSES (NOT A RESULT, never a zero)", c_logs_missing),
    ("LOGS-EMPTY", "a 0-byte log REFUSES", c_logs_empty),
    ("CENSUS-SEES", "the census sees planted non-finites", c_census_sees_planted_nan),
    ("CENSUS-ZERO", "the census returns 0 on clean text", c_census_zero_on_clean),
    ("CENSUS-WORDS", "`info`/`nanoseconds`/`Infinity` are NOT matches",
     c_census_does_not_match_info_words),
    ("CENSUS-WINDOW", "the P1 line window is honoured", c_census_window_respected),
    ("ATTR-EXACT", "an exact AoA attributes to its scenario", c_attribute_exact),
    ("ATTR-FAR", "an out-of-tolerance AoA is UNATTRIBUTED", c_attribute_out_of_tolerance),
    ("ATTR-AMBIG", "an ambiguous AoA is UNATTRIBUTED, not nearest-wins",
     c_attribute_ambiguous),
    ("ATTR-NOBLOCK", "no design-vector block gives UNATTRIBUTED", c_attribute_no_block),
    ("REC-ATTRIB", "records attribute to the right scenarios", c_records_attributed),
    ("REC-PRETRIM", "pre-trim records are named, not dropped", c_pretrim_named_not_dropped),
    ("REC-UNATTR", "an unattributable record is counted, never folded into a neighbour",
     c_unattributed_counted_not_folded),
    ("DV-MALFORMED", "a malformed design-vector array REFUSES", c_design_vars_malformed_refuses),
    ("UMAG-NONNUM", "a non-numeric AoA REFUSES", c_umag_nonnumeric_refuses),
    ("MINRES-NONNUM", "a non-numeric residual REFUSES", c_minres_nonnumeric_refuses),
    ("RESID-CLASS", "residual classification is failed/None as the log allows",
     c_residual_classification),
    ("PLANT-A-APPLY", "PLANT-A writes `nan` into a CD field", c_plant_a_applies),
    ("PLANT-A-REFUSE", "PLANT-A REFUSES when it cannot be applied",
     c_plant_a_refuses_when_absent),
    ("PLANT-B-APPLY", "PLANT-B moves one banner, total unchanged", c_plant_b_applies),
    ("PLANT-B-REFUSE", "PLANT-B REFUSES with no banner to move",
     c_plant_b_refuses_when_no_banner),
    ("PLANT-B-ANCHOR", "PLANT-B REFUSES on inverted anchors",
     c_plant_b_refuses_when_anchors_inverted),
    ("PLANT-C-APPLY", "PLANT-C scales the residual by 1e-4", c_plant_c_scales),
    ("PLANT-C-REFUSE", "PLANT-C REFUSES when it cannot be applied",
     c_plant_c_refuses_when_absent),
    ("GATE-P-PASS", "the plant control PASSes on a sound reader",
     c_plant_control_passes_on_sound_reader),
    ("PLANTB-SAMESCEN", "PLANT-B PASSes with BOTH anchors in one scenario -- where the predecessor refused",
     c_plantB_passes_with_both_anchors_in_one_scenario),
    ("DEGENERACY-PROOF", "the frozen per-scenario predicate CANNOT separate a correct reader from a blind one",
     c_degeneracy_is_real_literal_frozen_predicate),
    ("PLANTB-BLIND", "the record-level predicate DOES refuse a blind reader",
     c_plantB_refuses_a_blind_reader),
    ("PLANTB-COUNT", "PLANT-B REFUSES if the record count changes across the plant",
     c_plantB_refuses_record_count_change),
    ("PLANTB-RPSDRIFT", "PLANT-B REFUSES if record labels drift across the plant",
     c_plantB_refuses_rps_label_drift),
    ("PLANT-INCREMENTAL", "PLANT-A's PASS is on disk even when PLANT-B refuses",
     c_plant_report_is_incremental),
    ("NOTRUN-NOT-PASS", "an unreached plant is NOT RUN in the artifact, never PASS",
     c_not_run_is_not_pass),
    ("ORDINAL-INVARIANT", "the record ordinal survives the plant's line shift; start_line does not",
     c_record_ordinal_is_shift_invariant),
    ("GATE-P-BLIND", "the plant control REFUSES a blinded census",
     c_plant_control_refuses_a_blinded_census),
    ("GATE-P-ATTRIB", "the plant control REFUSES broken attribution",
     c_plant_control_refuses_broken_attribution),
    ("GATE-P-TOTAL", "the plant control REFUSES a wrong banner total",
     c_plant_control_refuses_wrong_total),
    ("GATE-P-RESID", "the plant control REFUSES a blinded residual classifier",
     c_plant_control_refuses_blinded_residual_classifier),
    ("COUPLE-YES", "coupling detects a banner before a cutback", c_coupling_detects_coupled),
    ("COUPLE-NO", "coupling reports 0.0 when no banner precedes", c_coupling_detects_uncoupled),
    ("COUPLE-NONE", "zero cutbacks gives a None fraction, not a 1.0",
     c_coupling_zero_cutbacks_is_none),
    ("CONTROL-RATE", "a single-point control rate counts starts and banners",
     c_control_rate),
    ("COST-CAP-FIRES", "the 12 core-min cap can BLOCK", c_clock_cap_fires),
    ("COST-CAP-QUIET", "the cap does not fire early", c_clock_cap_does_not_fire_early),
    ("G1-BOTH", "G-SO3D-1 can PASS and can GATE FAIL", c_gate1_can_pass_and_fail),
    ("G2-ALL", "G-SO3D-2 can PASS, GATE FAIL and be NOT A RESULT",
     c_gate2_can_pass_fail_and_not_a_result),
    ("G3-BOTH", "G-SO3D-3 can PASS and can GATE FAIL", c_gate3_can_pass_and_fail),
    ("G4-ALL", "G-SO3D-4 can PASS, GATE FAIL and be NOT A RESULT",
     c_gate4_can_pass_fail_and_not_a_result),
    ("NULL-YES", "the §8 null criterion triggers on P1-clean/P2-fail/P4-fail",
     c_null_criterion_triggers),
    ("NULL-NO", "the §8 null criterion does not trigger otherwise",
     c_null_criterion_does_not_trigger),
    ("NO-ASSERTS", "neither file contains a single `assert` statement",
     c_no_assert_statements_in_reader),
    ("INTERPRETER", "the interpreter mode is reported, not assumed",
     c_optimize_flag_reported),
]


def main():
    for name, expectation, fn in CONTROLS:
        control(name, expectation, fn)
    n_pass = sum(1 for r in RESULTS if r[1] == "PASS")
    n_fail = sum(1 for r in RESULTS if r[1] == "FAIL")
    print("SO3DR READER SELFTEST -- __debug__=%s (python3 -O sets it False)" % __debug__)
    for name, status, detail, expectation in RESULTS:
        print("  %-16s %-4s  %s" % (name, status, expectation))
        if status == "FAIL":
            print("        detail: %s" % detail)
    print("CONTROLS %d  PASS %d  FAIL %d  NOT RUN 0" % (len(RESULTS), n_pass, n_fail))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
