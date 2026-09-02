#!/usr/bin/env python3
"""A1WR Stage-1 gate -- the Stage-2 launch decision, taken INSIDE the detached
chain, by this file, from bytes on disk. No agent takes it.

Registered rule (A1WR_PREREGISTRATION.md sections 3.3, 3.4, 5):
  * y+ is read from BOTH arms' probe outputs -- the field-exact
    `<solver> -postProcess -func yPlus -time 1500` line
    (`patch wing y+ : min = A, max = B, average = C`), cross-checked against
    the last DAFoam-printed `yPlus min: ... max: ... mean: ...` line in the
    probe's own solve log;
  * y+max >= 1.0 on EITHER arm  ->  GATE FAIL: Stage 2 DOES NOT LAUNCH and the
    wall-resolved claim is WITHDRAWN for the affected points (section 3.4).
    The mesh is NOT re-cut; a re-mesh-until-y+-passes loop is result-shopping
    and is forbidden on this item.
  * absent / empty / all-zero y+ for a probe that produced a flow field
    ->  REFUSE exit 2 (rule 3: a zero from a reader not shown able to see a
    non-zero is not evidence).

Exit codes: 0 = PASS (Stage 2 may launch); 3 = GATE FAIL (registered stop);
2 = REFUSED (controls failed, or an unreadable/blind channel).

Planted controls (section 10 discipline, every mutation ASSERTED to land):
  K1 [+] real bytes parse to a non-zero reading;
  K2 [-] y+max forced >= 1 in a mutated copy -> verdict flips to GATE FAIL;
  K3 [-] y+ values zeroed in a mutated copy -> REFUSED, never PASS;
  K4 [!] parser disabled -> K1 must flip (a control that passes against a
         broken reader is not a control).
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PP_LINE = re.compile(
    r"patch wing y\+ : min = ([0-9.eE+-]+), max = ([0-9.eE+-]+), average = ([0-9.eE+-]+)")
DA_LINE = re.compile(
    r"^yPlus min: ([0-9.eE+-]+) max: ([0-9.eE+-]+) mean: ([0-9.eE+-]+)", re.M)
THRESH = 1.0   # frozen, section 3.3 G-YPLUS


def parse_pp(text: str):
    m = None
    for m0 in PP_LINE.finditer(text):
        m = m0
    if m is None:
        return None
    return tuple(float(m.group(i)) for i in (1, 2, 3))


def parse_da(text: str):
    m = None
    for m0 in DA_LINE.finditer(text):
        m = m0
    if m is None:
        return None
    return tuple(float(m.group(i)) for i in (1, 2, 3))


def verdict_for(pp, flow_field_present: bool):
    """The gate rule on ONE arm's field-exact reading."""
    if pp is None:
        if flow_field_present:
            return "REFUSED", "no parseable `patch wing y+` line, with a flow field present"
        return "REFUSED", "no reading and no flow field"
    if all(v == 0.0 for v in pp):
        return "REFUSED", "y+ reads 0/0/0 -- a blind reader, not a fine mesh (rule 3)"
    if pp[1] >= THRESH:
        return "GATE FAIL", "measured y+max %.6g >= %.1f" % (pp[1], THRESH)
    return "PASS", "measured y+max %.6g < %.1f" % (pp[1], THRESH)


def controls(real_bytes: str) -> list[str]:
    global PP_LINE
    fails = []
    # K1 [+]
    r = parse_pp(real_bytes)
    if r is None or all(v == 0.0 for v in r):
        fails.append("K1: real probe bytes do not parse to a non-zero reading")
        return fails  # nothing further is meaningful
    # K2 [-]  plant y+max = 2.5; assert the mutation landed
    mut = PP_LINE.sub("patch wing y+ : min = 0.01, max = 2.5, average = 0.2", real_bytes)
    if mut == real_bytes:
        fails.append("K2: MUTATION DID NOT LAND -- control is inert")
    else:
        v, _ = verdict_for(parse_pp(mut), True)
        if v != "GATE FAIL":
            fails.append("K2: planted y+max 2.5 did not flip the verdict (got %s)" % v)
    # K3 [-]  zero the reading; assert landed
    mut = PP_LINE.sub("patch wing y+ : min = 0, max = 0, average = 0", real_bytes)
    if mut == real_bytes:
        fails.append("K3: MUTATION DID NOT LAND -- control is inert")
    else:
        v, _ = verdict_for(parse_pp(mut), True)
        if v != "REFUSED":
            fails.append("K3: an all-zero y+ was not REFUSED (got %s)" % v)
    # K4 [!]  disable the parser; K1 must flip
    keep = PP_LINE
    PP_LINE = re.compile(r"(?!x)x_matches_nothing (\d) (\d) (\d)")
    try:
        broken = parse_pp(real_bytes)
    finally:
        PP_LINE = keep
    if broken is not None:
        fails.append("K4: disabling the parser did not blind it -- the control proves nothing")
    return fails


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("usage: a1wr_stage1_gate.py <probe_I_dir> <probe_C_dir>\n")
        return 2
    out = {"utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "threshold_yplus_max": THRESH, "arms": {}, "controls": None,
           "verdict": None, "rule": "PASS only if BOTH arms measure y+max < 1.0; "
           "GATE FAIL stops Stage 2 (section 3.4, mesh NOT re-cut); REFUSED stops "
           "Stage 2 as unmeasured, never as passed"}
    arm_verdicts = []
    ctrl_fails_all = []
    for arm, d in (("I", argv[1]), ("C", argv[2])):
        d = Path(d)
        pp_p = d / "out" / "probe_yplus.log"
        log_p = d / "out" / "sweep.log"
        pp_text = pp_p.read_text(errors="replace") if pp_p.is_file() else ""
        log_text = log_p.read_text(errors="replace") if log_p.is_file() else ""
        flow = bool(re.search(r"^Time = \d+", log_text, re.M))
        cf = controls(pp_text) if pp_text else ["K1: probe_yplus.log absent or empty"]
        ctrl_fails_all += ["%s:%s" % (arm, f) for f in cf]
        pp = parse_pp(pp_text)
        da = parse_da(log_text)
        v, why = verdict_for(pp, flow) if not cf else ("REFUSED", "; ".join(cf))
        cross = None
        if pp and da:
            cross = abs(pp[1] - da[1]) / max(pp[1], da[1], 1e-30)
        out["arms"][arm] = {
            "probe_dir": str(d), "flow_field_seen_in_log": flow,
            "yplus_field_exact_min_max_avg": pp,
            "yplus_dafoam_log_last_min_max_mean": da,
            "cross_channel_rel_diff_on_max": cross,
            "cross_channel_note": ("the DAFoam log line is computed during the solve "
                                   "at print cadence; the field-exact postProcess read "
                                   "is the BINDING channel; a large disagreement is "
                                   "REPORTED, never silently resolved"),
            "verdict": v, "why": why}
        arm_verdicts.append(v)
    if ctrl_fails_all:
        out["controls"] = {"status": "FAILED", "failures": ctrl_fails_all}
        out["verdict"] = "REFUSED"
    else:
        out["controls"] = {"status": "PASS", "list": ["K1", "K2", "K3", "K4"],
                           "note": "every mutation asserted to land; parser-disable flip proven"}
        if any(v == "REFUSED" for v in arm_verdicts):
            out["verdict"] = "REFUSED"
        elif any(v == "GATE FAIL" for v in arm_verdicts):
            out["verdict"] = "GATE FAIL"
        else:
            out["verdict"] = "PASS"
    gate_path = Path(argv[1]).parent / "stage1_gate.json"
    gate_path.write_text(json.dumps(out, indent=2) + "\n")
    sys.stdout.write(json.dumps(out, indent=2) + "\n")
    return {"PASS": 0, "GATE FAIL": 3, "REFUSED": 2}[out["verdict"]]


if __name__ == "__main__":
    sys.exit(main(sys.argv))
