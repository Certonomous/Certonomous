#!/usr/bin/env python3
"""SO-3D STAGE 1 READER -- log replay of the multipoint `Invalid number in NLP
function or derivative` pathology on the compressible A2 wing.

Grading path for `cases/dafoam/ladder-a/A2/curriculum_SO3D/PREREGISTRATION.md`
(FROZEN 2026-08-31, version 1.0). This file is the instrument that §12 of that
document registered as a binding pre-compute condition: Stage 1 may not run
until this file is committed and its md5 and line count are recorded in a dated
amendment at the foot of the pre-registration.

WHAT THIS PROGRAM IS ALLOWED TO DO
  * read four log files that already exist on disk, read-only;
  * create the item's own run root and write COPIES of one of them into it;
  * write `so3d_plant_report.json`, `so3d_replay.json` under the run root and
    a copy of each under the case directory.

WHAT IT NEVER DOES
  * launch a container, an MPI job or any OpenFOAM process (0 solver core-min,
    capped at 0 by the pre-registration);
  * write to anything under /home/ubuntu/certonomous-runs/CURRICULUM-D4-*,
    -D5-*, -D6-* or -D6R-*;
  * degrade a refusal to a warning.

NO `assert` STATEMENT CARRIES A REFUSAL, A GUARD, A CONTROL OR A GATE ANYWHERE
IN THIS FILE.  `assert` vanishes under `python3 -O`; every refusal below is an
explicit `raise` or `refuse()`.  There are no `assert` statements at all.

EXIT CODES
  0  every gate scored; verdicts are in `so3d_replay.json`
  2  REFUSAL / NOT A RESULT -- plant control failed, a log is missing or
     truncated, an attribution is ambiguous, or an original was modified
  3  BLOCKED on cost -- the registered 12 core-min cap was reached
"""

import hashlib
import json
import os
import re
import shutil
import sys
import time

# --------------------------------------------------------------------------
# FROZEN CONSTANTS -- every one of these is a value the pre-registration fixed.
# Changing any of them changes a gate, a threshold, a plant or a cap and is
# forbidden after first compute (CLAUDE.md rule 2).
# --------------------------------------------------------------------------

CASE_DIR = "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_SO3D"
RUN_ROOT = "/home/ubuntu/certonomous-runs/CURRICULUM-SO3D-a2-wing-multipoint-rootcause"
RUNS = "/home/ubuntu/certonomous-runs"

LOG_D6R = RUNS + "/CURRICULUM-D6R-a2-wing-multipoint/O_mp_20260828T162849Z_1898072.log"
LOG_D6 = RUNS + "/CURRICULUM-D6-a2-wing-multipoint/O_mp_20260827T140924Z_805560.log"
LOG_D4 = RUNS + "/CURRICULUM-D4-a2-wing-cdmin/O_20260825T181237Z_2359354.log"
LOG_D5 = RUNS + "/CURRICULUM-D5-a2-wing-ffd-density/O48_20260826T174911Z_325871.log"
LOGS = {"D6R": LOG_D6R, "D6": LOG_D6, "D4": LOG_D4, "D5": LOG_D5}

# §5 P1: the census window is lines 1 .. 264048 of the D6R log, i.e. strictly
# before the IPOPT summary block that begins at :264049.
D6R_CENSUS_LAST_LINE = 264048

# §5 registered predictions and §6 thresholds.
P1_EXPECTED_NONFINITE = 0        # G-SO3D-1
P3_MIN_SCENARIO_RATE = 0.1111    # G-SO3D-3, i.e. 11.11 %
P4_MIN_COUPLING = 0.90           # G-SO3D-4
D4_CONTROL_RATE_REGISTERED = 0.02222  # §5 P3 quotes 2.222 %
SCENARIOS = ("cl04", "cl05", "cl06")
CL_TARGETS = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}

# §7 plants -- content-addressed, never by absolute line number.
PLANT_A_FROM_LINE = 200000
PLANT_B_DELETE_FROM_LINE = 200000
PLANT_B_INSERT_AFTER_END_FROM_LINE = 100000
PLANT_C_FROM_LINE = 150000
PLANT_C_MULTIPLIER = 1e-4
PLANT_B_TOTAL_BANNERS_EXPECTED = 671   # §2 A7

# §11 cost.
RANKS = 1
CAP_CORE_MIN = 12.0
CAP_WALL_S = CAP_CORE_MIN * 60.0 / RANKS
SOLVER_CORE_MIN_CAP = 0.0
RATE_USD_PER_CORE_H = 0.0513  # owner-stated 2026-08-21/22; DERIVED, not measured

# Attribution tolerances (§ AMENDMENT 1 of the pre-registration; see the
# ATTRIBUTION RULE note below).  These are properties of the log's own print
# precision, not gate thresholds.
AOA_MATCH_ABS_TOL = 1e-5      # `Setting UMag` prints ~10 sig figs, Design Vars 8
# UNIQUENESS RULE, and the earlier form of it was WRONG.  A first draft required
# the second-nearest gap to exceed the nearest by a factor; on an EXACT match the
# nearest gap is 0.0, the factor test compares against a floor of 1e-12, and a
# rival 1e-7 away — comfortably inside AOA_MATCH_ABS_TOL — passed as unambiguous.
# The rule that can actually fire is a COUNT, not a ratio: an attribution is
# ambiguous when MORE THAN ONE candidate lies within AOA_MATCH_ABS_TOL.  The
# selftest control `ATTR-AMBIG` is what caught it.

# --------------------------------------------------------------------------
# LOG GRAMMAR -- the marker strings §9 of the pre-registration names as
# solver-independent DAFoam / mphys / pyOptSparse prints.
# --------------------------------------------------------------------------

RE_PRIMAL_START = re.compile(r"^Time = 1$")
RE_UMAG = re.compile(r"^Setting UMag = \S+ AoA = (\S+) degs")
RE_FAIL_BANNER = re.compile(r"^Primal solution failed!$")
RE_MIN_RES = re.compile(r"^Primal min residual\s+(\S+)\s*$")
RE_TOL_LINE = re.compile(r"^did not satisfy the prescribed tolerance\s+(\S+)\s*$")
RE_DRIVER_DEBUG = re.compile(r"^Driver debug print for iter coord:")
RE_CUTBACK = re.compile(r"Cutting back alpha due to evaluation error")
RE_DV_PATCHV = re.compile(r"'dvs\.patchV_(cl\d\d)':\s*array\(\[([^\]]*)\]")
RE_CD = re.compile(r"^CD: (\S+)")
RE_CL = re.compile(r"^CL: (\S+)")
RE_END = re.compile(r"^End$")
RE_NEWTON_TRIM = re.compile(r"^Finding a feasible design using the Newton method")

# G-SO3D-1 in-scope lines.  §6's cell for this gate says the census covers
# "a numeric field of a DAFoam or OpenMDAO print".  The whitelist below is
# derived mechanically from the log's own grammar and is fixed here BEFORE any
# census is scored.  The UNRESTRICTED count over every line in the window is
# reported BESIDE it and never instead of it, so nothing is hidden by the
# restriction (VERIFICATION_CHARTER §7's "reported beside it" duty).
NUMERIC_PRINT_PATTERNS = [
    re.compile(r"^(?:U\d|he|p|nuTilda|k|omega|epsilon|T)\s+initRes:"),
    re.compile(r"^C[DLM]\w*: "),
    re.compile(r"^yPlus "),
    re.compile(r"^Time step continuity errors"),
    re.compile(r"^\s+(?:global|cumulative) = "),
    re.compile(r"^ExecutionTime = "),
    re.compile(r"^Primal min residual"),
    re.compile(r"^did not satisfy the prescribed tolerance"),
    re.compile(r"^Setting UMag = "),
    re.compile(r"^\w+ Residual (?:Norm2|Mean|Max):"),
    re.compile(r"array\(\["),
    re.compile(r"^\s+[-+0-9.eE, ]+\]?\)?,?\s*$"),
    re.compile(r"^\s*\{?'(?:dvs|obj|con)\."),
    re.compile(r"^Target:\s*\["),
]

# A non-finite numeric token.  Bounded on both sides so that `info`, `Info`,
# `infinity`, `nanoseconds` and a path component are not matches.
RE_NONFINITE = re.compile(
    r"(?<![A-Za-z0-9_.])[+-]?(?:nan|inf)(?![A-Za-z0-9_])", re.IGNORECASE
)


class Refusal(Exception):
    """A registered refusal.  Never downgraded to a warning."""


class CostCap(Exception):
    """The registered 12 core-min cap was reached."""


# --------------------------------------------------------------------------
# COST CLOCK
# --------------------------------------------------------------------------

class Clock:
    def __init__(self, cap_wall_s=CAP_WALL_S):
        self.t0 = time.monotonic()
        self.cap = cap_wall_s

    def wall_s(self):
        return time.monotonic() - self.t0

    def core_min(self):
        return self.wall_s() * RANKS / 60.0

    def check(self, where):
        if self.wall_s() >= self.cap:
            raise CostCap(
                "BLOCKED on cost at %s: %.3f core-min of a registered cap of "
                "%.1f core-min. The run stops; it does not receive a new "
                "budget (CLAUDE.md rule 12). No gate below this point is "
                "scored." % (where, self.core_min(), CAP_CORE_MIN)
            )


# --------------------------------------------------------------------------
# PURE HELPERS -- these are what the selftest drives on synthetic text.
# --------------------------------------------------------------------------

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def line_in_numeric_print(line):
    for pat in NUMERIC_PRINT_PATTERNS:
        if pat.search(line):
            return True
    return False


def nonfinite_census(lines, last_line=None, restrict_to_numeric_prints=True):
    """Census of non-finite numeric tokens.

    `lines` is 0-indexed; reported line numbers are 1-indexed.  Returns a dict
    with the in-scope hits, the unrestricted hits, and both counts.  This
    function NEVER raises on a hit: a hit is a measurement, and G-SO3D-1 is
    what turns it into a verdict.
    """
    stop = len(lines) if last_line is None else min(last_line, len(lines))
    hits = []
    hits_all = []
    for idx in range(stop):
        line = lines[idx]
        found = RE_NONFINITE.findall(line)
        if not found:
            continue
        in_scope = line_in_numeric_print(line)
        for tok in found:
            rec = {"line": idx + 1, "token": tok, "text": line.rstrip()[:200]}
            hits_all.append(rec)
            if in_scope or not restrict_to_numeric_prints:
                hits.append(dict(rec))
    return {
        "count": len(hits),
        "count_unrestricted": len(hits_all),
        "hits": hits[:200],
        "hits_unrestricted": hits_all[:200],
        "window_last_line": stop,
    }


def parse_design_vars_blocks(lines):
    """Every `Driver debug print for iter coord` block and the per-scenario AoA
    it declares.  Returns a list of {line, aoa: {scenario: value}}."""
    blocks = []
    for idx, line in enumerate(lines):
        if not RE_DRIVER_DEBUG.search(line):
            continue
        aoa = {}
        for j in range(idx, min(idx + 60, len(lines))):
            m = RE_DV_PATCHV.search(lines[j])
            if m:
                nums = [t for t in re.split(r"[,\s]+", m.group(2).strip()) if t]
                if len(nums) < 2:
                    raise Refusal(
                        "REFUSE: `dvs.patchV_%s` at line %d carries %d numbers; "
                        "the AoA is the second element and cannot be read. "
                        "UNMEASURED, not assumed." % (m.group(1), j + 1, len(nums))
                    )
                try:
                    aoa[m.group(1)] = float(nums[1])
                except ValueError:
                    raise Refusal(
                        "REFUSE: `dvs.patchV_%s` AoA token %r at line %d is not "
                        "a number. UNMEASURED, not assumed."
                        % (m.group(1), nums[1], j + 1)
                    )
            if len(aoa) == len(SCENARIOS):
                break
        if aoa:
            blocks.append({"line": idx + 1, "aoa": aoa})
    return blocks


def attribute_aoa(aoa_value, aoa_map):
    """Nearest-AoA attribution with a uniqueness margin.

    Returns (scenario, gap) or (None, reason).  An ambiguous or unmatched AoA is
    UNATTRIBUTED and is reported by name and count -- never silently dropped and
    never folded into a neighbouring scenario.
    """
    if not aoa_map:
        return None, "no design-vector block in scope"
    gaps = sorted(((abs(aoa_value - v), s) for s, v in aoa_map.items()))
    best_gap, best = gaps[0]
    if best_gap > AOA_MATCH_ABS_TOL:
        return None, "nearest gap %.3e exceeds tol %.3e" % (best_gap, AOA_MATCH_ABS_TOL)
    within = [(g, s) for g, s in gaps if g <= AOA_MATCH_ABS_TOL]
    if len(within) > 1:
        return None, (
            "ambiguous: %d candidates within tol %.3e -- %r"
            % (len(within), AOA_MATCH_ABS_TOL, [(s, "%.3e" % g) for g, s in within])
        )
    return best, best_gap


def parse_primal_records(lines):
    """Split a log into primal records and attribute each to a scenario.

    A record starts at `^Time = 1$` (the counter §2 A7-A10 used) and runs to the
    line before the next such start.  Its AoA is the LAST `Setting UMag` line
    strictly before the start -- §2 A14 records 985 UMag lines against 977
    starts, so the mapping is last-before-start, never one-to-one by position.

    A record carries:
      failures     -- number of `Primal solution failed!` BANNERS inside it.
                      Banners, not records: PLANT-B's registered expectation is
                      a movement of exactly -1 / +1 against a total of 671, and
                      671 is the banner count (§2 A7).
      min_res      -- the `Primal min residual` value if the log printed one
      tol          -- the tolerance the log itself printed beside it
      residual_converged -- min_res < tol, or None where no residual was printed
    """
    starts = [i for i, ln in enumerate(lines) if RE_PRIMAL_START.match(ln)]
    umags = []
    for i, ln in enumerate(lines):
        m = RE_UMAG.match(ln)
        if m:
            try:
                umags.append((i, float(m.group(1))))
            except ValueError:
                raise Refusal(
                    "REFUSE: `Setting UMag` at line %d carries a non-numeric "
                    "AoA %r. UNMEASURED, not assumed." % (i + 1, m.group(1))
                )
    blocks = parse_design_vars_blocks(lines)

    records = []
    for k, s in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else len(lines)
        aoa = None
        for i, v in reversed(umags):
            if i < s:
                aoa = v
                break
        block = None
        for b in blocks:
            if b["line"] - 1 < s:
                block = b
            else:
                break
        span = lines[s:end]
        n_banner = sum(1 for ln in span if RE_FAIL_BANNER.match(ln))
        min_res = None
        tol = None
        for j, ln in enumerate(span):
            m = RE_MIN_RES.match(ln)
            if m:
                try:
                    min_res = float(m.group(1))
                except ValueError:
                    raise Refusal(
                        "REFUSE: `Primal min residual` at line %d carries a "
                        "non-numeric value %r. UNMEASURED, not assumed."
                        % (s + j + 1, m.group(1))
                    )
                for jj in range(j + 1, min(j + 4, len(span))):
                    mt = RE_TOL_LINE.match(span[jj])
                    if mt:
                        try:
                            tol = float(mt.group(1))
                        except ValueError:
                            raise Refusal(
                                "REFUSE: prescribed tolerance token %r at line "
                                "%d is not a number. UNMEASURED, not assumed."
                                % (mt.group(1), s + jj + 1)
                            )
                        break
                break
        if block is None:
            scen, why = None, "PRETRIM: record precedes the first design-vector block"
        elif aoa is None:
            scen, why = None, "no `Setting UMag` line precedes this record"
        else:
            scen, why = attribute_aoa(aoa, block["aoa"])
            if scen is not None:
                why = None
        residual_converged = None
        if min_res is not None and tol is not None:
            residual_converged = min_res < tol
        records.append({
            "start_line": s + 1,
            "end_line": end,
            "aoa": aoa,
            "scenario": scen,
            "unattributed_reason": why if scen is None else None,
            "banners": n_banner,
            "min_res": min_res,
            "tol": tol,
            "residual_converged": residual_converged,
        })
    return records


def per_scenario_rates(records):
    starts = {s: 0 for s in SCENARIOS}
    banners = {s: 0 for s in SCENARIOS}
    unattributed = 0
    pretrim = 0
    unattributed_reasons = {}
    for r in records:
        s = r["scenario"]
        if s is None:
            why = r["unattributed_reason"] or "unknown"
            if why.startswith("PRETRIM"):
                pretrim += 1
            else:
                unattributed += 1
            unattributed_reasons[why] = unattributed_reasons.get(why, 0) + 1
            continue
        starts[s] += 1
        banners[s] += r["banners"]
    rates = {}
    for s in SCENARIOS:
        rates[s] = (banners[s] / starts[s]) if starts[s] else None
    return {
        "starts": starts,
        "banners": banners,
        "rates": rates,
        "unattributed": unattributed,
        "pretrim": pretrim,
        "unattributed_reasons": unattributed_reasons,
        "cl_targets": CL_TARGETS,
    }


def cutback_coupling(lines):
    """G-SO3D-4 / P4.  For each cutback line, scan backward to the nearest
    preceding driver-debug line and report whether a failure banner lies
    strictly between them, plus the banner-count distribution (H5)."""
    cutbacks = [i for i, ln in enumerate(lines) if RE_CUTBACK.search(ln)]
    driver = [i for i, ln in enumerate(lines) if RE_DRIVER_DEBUG.search(ln)]
    banners = [i for i, ln in enumerate(lines) if RE_FAIL_BANNER.match(ln)]
    coupled = 0
    dist = {}
    no_preceding_driver = 0
    import bisect
    for c in cutbacks:
        di = bisect.bisect_left(driver, c) - 1
        if di < 0:
            no_preceding_driver += 1
            dist["no_preceding_driver_block"] = dist.get("no_preceding_driver_block", 0) + 1
            continue
        lo = driver[di]
        a = bisect.bisect_right(banners, lo)
        b = bisect.bisect_left(banners, c)
        n = max(0, b - a)
        dist[str(n)] = dist.get(str(n), 0) + 1
        if n >= 1:
            coupled += 1
    total = len(cutbacks)
    return {
        "cutbacks": total,
        "coupled": coupled,
        "fraction": (coupled / total) if total else None,
        "banner_count_distribution": dist,
        "cutbacks_with_no_preceding_driver_block": no_preceding_driver,
    }


def control_rate(lines):
    """A single-point control's failure rate: banners over `^Time = 1$` starts.
    The same two counters §2 A9/A10 used, so the numbers are comparable."""
    starts = sum(1 for ln in lines if RE_PRIMAL_START.match(ln))
    banners = sum(1 for ln in lines if RE_FAIL_BANNER.match(ln))
    reached_1000 = sum(1 for ln in lines if ln.strip() == "Time = 1000")
    return {
        "starts": starts,
        "banners": banners,
        "reached_time_1000": reached_1000,
        "rate": (banners / starts) if starts else None,
    }


# --------------------------------------------------------------------------
# THE PLANTS (§7).  Each returns the mutated line list plus what it targeted.
# --------------------------------------------------------------------------

def apply_plant_a(lines):
    for idx in range(PLANT_A_FROM_LINE - 1, len(lines)):
        if RE_CD.match(lines[idx]):
            out = list(lines)
            out[idx] = re.sub(r"^CD: \S+", "CD: nan", lines[idx])
            return out, {"line": idx + 1, "before": lines[idx].rstrip()[:120],
                         "after": out[idx].rstrip()[:120]}
    raise Refusal(
        "REFUSE (PLANT-A): no line matching `^CD: ` at or after line %d. The "
        "plant could not be applied, so the control could not be run. "
        "NOT A RESULT, never a clean sheet." % PLANT_A_FROM_LINE
    )


def apply_plant_b(lines):
    del_idx = None
    for idx in range(PLANT_B_DELETE_FROM_LINE - 1, len(lines)):
        if RE_FAIL_BANNER.match(lines[idx]):
            del_idx = idx
            break
    if del_idx is None:
        raise Refusal(
            "REFUSE (PLANT-B): no `Primal solution failed!` at or after line %d."
            % PLANT_B_DELETE_FROM_LINE
        )
    ins_idx = None
    for idx in range(PLANT_B_INSERT_AFTER_END_FROM_LINE - 1, len(lines)):
        if RE_END.match(lines[idx]):
            ins_idx = idx
            break
    if ins_idx is None:
        raise Refusal(
            "REFUSE (PLANT-B): no `End` line at or after line %d."
            % PLANT_B_INSERT_AFTER_END_FROM_LINE
        )
    if ins_idx >= del_idx:
        raise Refusal(
            "REFUSE (PLANT-B): the insertion anchor (line %d) is not strictly "
            "before the deletion anchor (line %d); the plant as registered "
            "assumes two distinct sites." % (ins_idx + 1, del_idx + 1)
        )
    out = []
    for idx, ln in enumerate(lines):
        if idx == del_idx:
            continue
        out.append(ln)
        if idx == ins_idx:
            out.append("Primal solution failed!")
    return out, {"deleted_line": del_idx + 1, "inserted_after_line": ins_idx + 1}


def apply_plant_c(lines):
    for idx in range(PLANT_C_FROM_LINE - 1, len(lines)):
        m = RE_MIN_RES.match(lines[idx])
        if m:
            try:
                r = float(m.group(1))
            except ValueError:
                raise Refusal(
                    "REFUSE (PLANT-C): `Primal min residual` value %r at line "
                    "%d is not a number." % (m.group(1), idx + 1)
                )
            out = list(lines)
            new = r * PLANT_C_MULTIPLIER
            out[idx] = "Primal min residual %.10g" % new
            return out, {"line": idx + 1, "R": r, "R_scaled": new,
                         "multiplier": PLANT_C_MULTIPLIER}
    raise Refusal(
        "REFUSE (PLANT-C): no `Primal min residual` line at or after line %d."
        % PLANT_C_FROM_LINE
    )


# --------------------------------------------------------------------------
# THE PLANT CONTROL (G-SO3D-P).  Scored FIRST.  §6 ordering rule 1: if it does
# not PASS the reader exits 2 and every other gate is NOT A RESULT.
# --------------------------------------------------------------------------

def score_plant_control(clean_lines, clock=None):
    report = {"gate": "G-SO3D-P", "plants": {}}

    # ---- PLANT-A : value channel -----------------------------------------
    if clock:
        clock.check("PLANT-A")
    base_census = nonfinite_census(clean_lines, D6R_CENSUS_LAST_LINE)
    a_lines, a_meta = apply_plant_a(clean_lines)
    a_census = nonfinite_census(a_lines, D6R_CENSUS_LAST_LINE)
    delta = a_census["count"] - base_census["count"]
    a_hit_at_target = any(h["line"] == a_meta["line"] and h["token"].lower() == "nan"
                          for h in a_census["hits"])
    a_ok = (delta == 1) and a_hit_at_target
    report["plants"]["PLANT-A"] = {
        "channel": "value",
        "target_line": a_meta["line"],
        "census_unplanted": base_census["count"],
        "census_planted": a_census["count"],
        "delta": delta,
        "detected_at_target_line": a_hit_at_target,
        "expected": "delta == 1 and the hit is at the target line, field CD",
        "status": "PASS" if a_ok else "REFUSE",
    }
    if not a_ok:
        raise Refusal(
            "REFUSE (PLANT-A): planted `nan` into `CD:` at line %d. Expected the "
            "census to move by exactly +1 with the hit AT that line. Measured: "
            "unplanted %d, planted %d, delta %d, hit_at_target %s. A reader that "
            "cannot see a planted non-finite cannot be believed when it reports "
            "none (CLAUDE.md rule 3)."
            % (a_meta["line"], base_census["count"], a_census["count"], delta,
               a_hit_at_target)
        )

    # ---- PLANT-B : flag channel ------------------------------------------
    if clock:
        clock.check("PLANT-B")
    base_records = parse_primal_records(clean_lines)
    base_ps = per_scenario_rates(base_records)
    b_lines, b_meta = apply_plant_b(clean_lines)
    b_records = parse_primal_records(b_lines)
    b_ps = per_scenario_rates(b_records)

    base_total = sum(base_ps["banners"].values())
    b_total = sum(b_ps["banners"].values())
    moves = {s: b_ps["banners"][s] - base_ps["banners"][s] for s in SCENARIOS}
    minus = [s for s, d in moves.items() if d == -1]
    plus = [s for s, d in moves.items() if d == +1]
    zero = [s for s, d in moves.items() if d == 0]
    b_ok = (
        len(minus) == 1 and len(plus) == 1 and len(zero) == len(SCENARIOS) - 2
        and b_total == base_total
        and base_total == PLANT_B_TOTAL_BANNERS_EXPECTED
    )
    report["plants"]["PLANT-B"] = {
        "channel": "flag",
        "deleted_line": b_meta["deleted_line"],
        "inserted_after_line": b_meta["inserted_after_line"],
        "banners_unplanted": base_ps["banners"],
        "banners_planted": b_ps["banners"],
        "moves": moves,
        "total_unplanted": base_total,
        "total_planted": b_total,
        "expected": ("exactly one scenario -1, exactly one +1, the rest 0, total "
                     "unchanged at %d" % PLANT_B_TOTAL_BANNERS_EXPECTED),
        "status": "PASS" if b_ok else "REFUSE",
    }
    if not b_ok:
        raise Refusal(
            "REFUSE (PLANT-B): moved one `Primal solution failed!` banner from "
            "line %d to just after line %d. Expected exactly one scenario at -1, "
            "exactly one at +1, the rest at 0, and the total unchanged at %d. "
            "Measured moves %r, total %d -> %d. Any other movement means the "
            "reader is not attributing banners to the scenario that owns them."
            % (b_meta["deleted_line"], b_meta["inserted_after_line"],
               PLANT_B_TOTAL_BANNERS_EXPECTED, moves, base_total, b_total)
        )

    # ---- PLANT-C : dose / classification channel --------------------------
    if clock:
        clock.check("PLANT-C")
    c_lines, c_meta = apply_plant_c(clean_lines)
    c_records = parse_primal_records(c_lines)
    base_class = {r["start_line"]: r["residual_converged"] for r in base_records}
    c_class = {r["start_line"]: r["residual_converged"] for r in c_records}
    changed = [k for k in base_class
               if k in c_class and base_class[k] != c_class[k]]
    target_owner = None
    for r in base_records:
        if r["start_line"] <= c_meta["line"] <= r["end_line"]:
            target_owner = r["start_line"]
            break
    c_ok = (
        len(changed) == 1
        and target_owner is not None
        and changed[0] == target_owner
        and base_class.get(target_owner) is False
        and c_class.get(target_owner) is True
    )
    report["plants"]["PLANT-C"] = {
        "channel": "dose/classification (RELATIVE plant)",
        "target_line": c_meta["line"],
        "R": c_meta["R"],
        "R_scaled": c_meta["R_scaled"],
        "multiplier": c_meta["multiplier"],
        "records_whose_classification_moved": changed[:10],
        "n_records_moved": len(changed),
        "target_record_start_line": target_owner,
        "classification_before": base_class.get(target_owner),
        "classification_after": c_class.get(target_owner),
        "expected": "exactly one record moves, and it is the target, failed -> converged",
        "status": "PASS" if c_ok else "REFUSE",
    }
    if not c_ok:
        raise Refusal(
            "REFUSE (PLANT-C): scaled `Primal min residual` at line %d from %r to "
            "%r (x%g). Expected EXACTLY ONE record to flip its residual "
            "classification from failed to converged, and for it to be the record "
            "owning that line. Measured: %d records moved %r, target record %r, "
            "before %r after %r. A plant that does not flip the classification "
            "means the reader is not classifying on the residual at all."
            % (c_meta["line"], c_meta["R"], c_meta["R_scaled"],
               c_meta["multiplier"], len(changed), changed[:10], target_owner,
               base_class.get(target_owner), c_class.get(target_owner))
        )

    report["status"] = "PASS"
    return report


# --------------------------------------------------------------------------
# GATES
# --------------------------------------------------------------------------

def score_gates(census, ps, coupling, controls):
    gates = {}

    # G-SO3D-1 -- channel: value or flag?
    n = census["count"]
    gates["G-SO3D-1"] = {
        "question": "channel: value or flag?",
        "measured": {"nonfinite_in_scope": n,
                     "nonfinite_unrestricted": census["count_unrestricted"],
                     "window_last_line": census["window_last_line"]},
        "threshold": "P1: count == %d" % P1_EXPECTED_NONFINITE,
        "verdict": "PASS" if n == P1_EXPECTED_NONFINITE else "GATE FAIL",
        "reading": ("H1 stands as the only surviving reading of the exception"
                    if n == P1_EXPECTED_NONFINITE
                    else "H1 refuted, H6 revived; the census names file, line and token"),
        "hits": census["hits"][:50],
        "hits_unrestricted": census["hits_unrestricted"][:50],
    }

    # G-SO3D-2 -- dose-response in CL target
    r = ps["rates"]
    if any(r[s] is None for s in SCENARIOS):
        gates["G-SO3D-2"] = {
            "question": "dose-response in CL target",
            "measured": r,
            "threshold": "P2: r(cl04) < r(cl05) < r(cl06), strict",
            "verdict": "NOT A RESULT",
            "reading": ("a scenario has zero attributed primal starts, so its "
                        "rate is undefined; a rate that does not exist is not a "
                        "rate that passes"),
        }
    else:
        mono = r["cl04"] < r["cl05"] < r["cl06"]
        gates["G-SO3D-2"] = {
            "question": "dose-response in CL target",
            "measured": r,
            "threshold": "P2: r(cl04) < r(cl05) < r(cl06), strict",
            "verdict": "PASS" if mono else "GATE FAIL",
            "reading": "H2 stands" if mono else "H2 refuted",
        }

    # G-SO3D-3 -- multipoint-specific vs case-specific
    if any(r[s] is None for s in SCENARIOS):
        gates["G-SO3D-3"] = {
            "question": "multipoint-specific vs case-specific",
            "measured": {"rates": r, "controls": controls},
            "threshold": "P3: min(r) >= %.4f" % P3_MIN_SCENARIO_RATE,
            "verdict": "NOT A RESULT",
            "reading": "a scenario rate is undefined",
        }
    else:
        mn = min(r[s] for s in SCENARIOS)
        gates["G-SO3D-3"] = {
            "question": "multipoint-specific vs case-specific",
            "measured": {"min_rate": mn, "rates": r, "controls": controls,
                         "d4_control_rate_registered": D4_CONTROL_RATE_REGISTERED},
            "threshold": "P3: min(r) >= %.4f" % P3_MIN_SCENARIO_RATE,
            "verdict": "PASS" if mn >= P3_MIN_SCENARIO_RATE else "GATE FAIL",
            "reading": ("H3 stands: the lowest multipoint scenario is at least 5x "
                        "the single-point control" if mn >= P3_MIN_SCENARIO_RATE
                        else "H3 not supported at the registered margin"),
        }

    # G-SO3D-4 -- single-scenario poisoning of the sum
    f = coupling["fraction"]
    if f is None:
        gates["G-SO3D-4"] = {
            "question": "single-scenario poisoning of the sum",
            "measured": coupling,
            "threshold": "P4: fraction >= %.2f" % P4_MIN_COUPLING,
            "verdict": "NOT A RESULT",
            "reading": "zero cutback lines: the denominator does not exist",
        }
    else:
        gates["G-SO3D-4"] = {
            "question": "single-scenario poisoning of the sum",
            "measured": coupling,
            "threshold": "P4: fraction >= %.2f" % P4_MIN_COUPLING,
            "verdict": "PASS" if f >= P4_MIN_COUPLING else "GATE FAIL",
            "reading": ("cutbacks follow DAFoam's own boolean failure signal"
                        if f >= P4_MIN_COUPLING else "P4 refuted"),
        }
    return gates


def null_result_criterion(gates):
    """§8, registered before the run so a null cannot be dressed up after it."""
    g1 = gates["G-SO3D-1"]["verdict"]
    g2 = gates["G-SO3D-2"]["verdict"]
    g4 = gates["G-SO3D-4"]["verdict"]
    if g1 == "PASS" and g2 == "GATE FAIL" and g4 == "GATE FAIL":
        return {
            "triggered": True,
            "mechanism_finding": "NOT A RESULT",
            "text": ("G-SO3D-1 PASSed while G-SO3D-2 and G-SO3D-4 both GATE FAILed. "
                     "The failure population is NOT ATTRIBUTABLE BY LOG REPLAY. "
                     "G-SO3D-1 and G-SO3D-3 stand as independent measured verdicts. "
                     "The instrument that would be required is Stage 2: a "
                     "per-trial-point trace inside the runScript carrying, for "
                     "each scenario and each evaluation, the design vector, the "
                     "warped-mesh quality metrics, the primal's residual history, "
                     "DASolver.primalFail, the functional values, and the boolean "
                     "actually returned to pyOptSparse. NO REMEDY IS PROPOSED."),
        }
    return {"triggered": False, "mechanism_finding": None}


# --------------------------------------------------------------------------
# I/O AND THE GUARDS AROUND IT
# --------------------------------------------------------------------------

def verify_logs_present():
    """§6 ordering rule 2: a missing or truncated log is NOT A RESULT, never a
    zero.  Existence, non-emptiness, byte length and sha256 are all recorded."""
    integrity = {}
    for name, path in LOGS.items():
        if not os.path.isfile(path):
            raise Refusal(
                "REFUSE: registered log %s is ABSENT at %s. A missing log is "
                "NOT A RESULT, never a zero (pre-registration §6 rule 2)."
                % (name, path)
            )
        size = os.path.getsize(path)
        if size == 0:
            raise Refusal(
                "REFUSE: registered log %s at %s is EMPTY (0 bytes). NOT A "
                "RESULT, never a zero." % (name, path)
            )
        integrity[name] = {"path": path, "bytes": size, "sha256": sha256_of(path),
                           "lines": None}
    return integrity


def guard_run_root_absent():
    """CLAUDE.md rule 4: a guard refuses a case whose run root already exists."""
    if os.path.exists(RUN_ROOT):
        raise Refusal(
            "REFUSE: the run root %s ALREADY EXISTS. This item's freeze records "
            "it as absent (§12); an existing root means either a previous run or "
            "a name collision, and either way this invocation is not the run "
            "allowed to produce the answer. Archive by `mv`, never delete."
            % RUN_ROOT
        )


def read_lines(path):
    with open(path, errors="replace") as fh:
        return fh.read().split("\n")


def write_json(path, obj):
    tmp = path + ".partial"
    with open(tmp, "w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def main(argv):
    clock = Clock()
    started = time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())
    result = {
        "item": "SO-3D",
        "stage": 1,
        "started_utc": started,
        "prereg": os.path.join(CASE_DIR, "PREREGISTRATION.md"),
        "reader": os.path.abspath(__file__),
        "toolchain_row": "PATCHED (dafoam-idwarp-rot:v1) -- every log replayed "
                         "here was produced on that row; there is no shipped row "
                         "for the multipoint pathology and this rung does not "
                         "manufacture one (DAFOAM_CHARTER.md §6)",
        "solver_core_min": 0.0,
        "solver_core_min_cap": SOLVER_CORE_MIN_CAP,
    }

    try:
        guard_run_root_absent()
        integrity = verify_logs_present()
        os.makedirs(RUN_ROOT, exist_ok=False)

        clock.check("after run-root creation")

        # Read every log ONCE.
        text = {}
        for name, path in LOGS.items():
            text[name] = read_lines(path)
            integrity[name]["lines"] = len(text[name])
        result["log_integrity_before"] = integrity
        clock.check("after reading logs")

        # ---- G-SO3D-P, scored FIRST (§6 ordering rule 1) -----------------
        plant_report = score_plant_control(text["D6R"], clock)
        plant_report["started_utc"] = started
        plant_report["log_sha256_D6R"] = integrity["D6R"]["sha256"]
        write_json(os.path.join(RUN_ROOT, "so3d_plant_report.json"), plant_report)
        write_json(os.path.join(CASE_DIR, "so3d_plant_report.json"), plant_report)
        result["plant_control"] = plant_report
        clock.check("after the plant control")

        # ---- The originals must be untouched by the plant pass ------------
        after = {}
        for name, path in LOGS.items():
            after[name] = sha256_of(path)
            if after[name] != integrity[name]["sha256"]:
                raise Refusal(
                    "REFUSE: the ORIGINAL log %s at %s CHANGED during this "
                    "invocation (sha256 %s -> %s). Plants are applied to copies "
                    "only; an original that moved invalidates every number "
                    "above it. NOT A RESULT."
                    % (name, path, integrity[name]["sha256"], after[name])
                )
        result["log_sha256_after"] = after

        # ---- The gates, scored on the UNPLANTED originals -----------------
        census = nonfinite_census(text["D6R"], D6R_CENSUS_LAST_LINE)
        clock.check("after the non-finite census")
        records = parse_primal_records(text["D6R"])
        ps = per_scenario_rates(records)
        clock.check("after per-scenario attribution")
        coupling = cutback_coupling(text["D6R"])
        clock.check("after cutback coupling")

        controls = {
            "D4": control_rate(text["D4"]),
            "D5": control_rate(text["D5"]),
            "D6": control_rate(text["D6"]),
        }
        controls["D6R_whole_log"] = control_rate(text["D6R"])
        clock.check("after the controls")

        newton = {n: sum(1 for ln in text[n] if RE_NEWTON_TRIM.match(ln))
                  for n in ("D6R", "D6")}

        result["nonfinite_census"] = census
        result["per_scenario"] = ps
        result["cutback_coupling"] = coupling
        result["controls"] = controls
        result["newton_trim_invocations"] = newton
        result["attribution_rule"] = (
            "A primal record runs from `^Time = 1$` to the line before the next "
            "one. Its AoA is the LAST `Setting UMag ... AoA = a degs` strictly "
            "before the start. It is attributed to the scenario whose "
            "`dvs.patchV_clNN` AoA in the most recent `Driver debug print for "
            "iter coord` block is nearest to a, with |gap| <= %g AND with "
            "EXACTLY ONE candidate inside that tolerance. Anything else is "
            "UNATTRIBUTED and is reported by count and reason, never dropped "
            "and never folded into a neighbour. Records preceding the first "
            "design-vector block are PRETRIM and are excluded by name."
            % (AOA_MATCH_ABS_TOL,)
        )

        gates = score_gates(census, ps, coupling, controls)
        result["gates"] = gates
        result["null_result"] = null_result_criterion(gates)

        if ps["unattributed"] > 0:
            result["attribution_warning"] = (
                "%d primal records could not be attributed to a scenario and are "
                "excluded from every per-scenario rate BY NAME. Reasons: %r"
                % (ps["unattributed"], ps["unattributed_reasons"])
            )

        wall = clock.wall_s()
        result["cost"] = {
            "unit": "core-minutes = wall seconds x ranks / 60",
            "ranks": RANKS,
            "wall_s": round(wall, 3),
            "cost_core_min_measured": round(wall * RANKS / 60.0, 4),
            "cap_core_min_registered": CAP_CORE_MIN,
            "predicted_core_min_point": 6.0,
            "predicted_core_min_bracket": [3.0, 10.0],
            "solver_core_min": 0.0,
            "usd_derived": round(wall * RANKS / 3600.0 * RATE_USD_PER_CORE_H, 6),
            "cost_basis": ("core-minutes MEASURED from this process's own wall "
                           "clock x 1 rank / 60. Dollars are DERIVED at the "
                           "owner-stated rate $%.4f/core-h and are "
                           "REPORTED-BY-OWNER, NOT MEASURED -- the box cannot "
                           "read its own billing (COMPUTE_BUDGET_CHARTER §5)."
                           % RATE_USD_PER_CORE_H),
        }
        result["verdict_summary"] = {k: v["verdict"] for k, v in gates.items()}
        result["verdict_summary"]["G-SO3D-P"] = plant_report["status"]
        result["status"] = "SCORED"
        write_json(os.path.join(RUN_ROOT, "so3d_replay.json"), result)
        write_json(os.path.join(CASE_DIR, "so3d_replay.json"), result)
        print("SO3D STAGE 1 SCORED  %.4f core-min of a %.1f cap"
              % (result["cost"]["cost_core_min_measured"], CAP_CORE_MIN))
        for k in sorted(result["verdict_summary"]):
            print("  %-10s %s" % (k, result["verdict_summary"][k]))
        if result["null_result"]["triggered"]:
            print("  NULL-RESULT CRITERION TRIGGERED: mechanism finding is "
                  "NOT A RESULT (pre-registration §8)")
        return 0

    except CostCap as e:
        result["status"] = "BLOCKED"
        result["blocked_reason"] = str(e)
        result["cost"] = {"wall_s": round(clock.wall_s(), 3),
                          "cost_core_min_measured": round(clock.core_min(), 4),
                          "cap_core_min_registered": CAP_CORE_MIN}
        try:
            write_json(os.path.join(CASE_DIR, "so3d_replay.json"), result)
        except OSError:
            pass
        sys.stderr.write("BLOCKED: %s\n" % e)
        return 3

    except Refusal as e:
        result["status"] = "NOT A RESULT"
        result["refusal"] = str(e)
        result["cost"] = {"wall_s": round(clock.wall_s(), 3),
                          "cost_core_min_measured": round(clock.core_min(), 4),
                          "cap_core_min_registered": CAP_CORE_MIN}
        try:
            write_json(os.path.join(CASE_DIR, "so3d_replay.json"), result)
        except OSError:
            pass
        sys.stderr.write("NOT A RESULT: %s\n" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
