"""D2 optimizer-A/B comparator core: the reader, the controls, the statistics.

Frozen by the commit that carries
`cases/dafoam/ladder-a/A1/curriculum_D2/PREREGISTRATION.md`.
NOT EDITED AFTER THE FIRST LAUNCH.  An edit voids the arm that ran before it.

Standard library ONLY, on purpose.  This module must be importable and runnable
on the HOST, outside any container, so that its planted-zero control and its
A/B trivial baseline can be dry-run against D1 arm O's REAL log BEFORE the
freeze, at zero compute.  That dry run is the point: it is the L-273 repair
carried forward -- a control that plants into its own synthetic fixture proves
the arithmetic and not the coupling, and the coupling is the half that broke D1
arm C at 14 s on a KeyError.

Nothing here selects a step, a gate or a band.  Every step used by either arm is
selected inside the container by the frozen D1 instrument `d1_fd_endpoint.py`
(md5 7e454d2f1830a40086465d9b5c57a941) from |J_adj| and the inherited eta alone.
This file only READS what the arms printed and COMPARES the two arms.
"""

import copy
import hashlib
import json
import os
import re
import sys

# ---- frozen constants (PREREGISTRATION.md sections 4, 6, 7) ----------------

PLANT = 1.234e-03                       # CLAUDE.md rule 3
AB_TRIVIAL_SHIFT = 2.0e-02              # DAFOAM_CHARTER.md section 4, in the
                                        # A/B's own currency: a planted design
                                        # difference the comparison MUST see
                                        # AND must be failed by gate AB2
AB_RESOLUTION_SHIFT = 1.0e-02           # reported only: the smaller planted
                                        # difference, so the comparison's
                                        # measured resolution is on the record
AB2_BAND_L2_REL = 0.10                  # gate AB2, frozen band
AB2_BAND_LINF = 8.0e-03                 # gate AB2, frozen band
CL_TARGET = 0.5                         # runScript.py:34, the case's own
ETA_INHERITED = 1.957349804806996e-08   # D1 arm E run 2, MEASURED; sizes
                                        # nothing in this file

# D1 arm O, the frozen external reference (gate AB5).  Values from
# `cases/dafoam/ladder-a/A1/curriculum_D1/RESULTS.md` section 4.4 at commit
# b10260a0, and from the run-root log whose md5 is asserted below.
ARMO_LOG_MD5 = "64bee1631d28ab07973e56ec7e1f4bf3"
ARMO = {
    "CD_feasible": 0.020943920630946831,
    "CL_feasible": 0.49999943897261456,
    "AoA_feasible": 5.153023459675001,
    "CD_opt": 0.017527899854535338,
    "CL_opt": 0.49999981209363359,
    "AoA_opt": 1.128636497545056,
    "shape_opt": [0.02876504584608877, 0.047201042921213354,
                  0.016871666037627377, 0.036676713888073136,
                  0.0472289265360477, 0.022959816884178426,
                  0.008262623112944891, 0.036138219756860344],
    "majors": 11,
    "evals_reported": 12,
    "n_blocks": 13,
    "driver_wall_s": 278.04,
    "arm_wall_s": 361.0,
}

# The producer's ACTUAL key sets, read from the file D1 arm O really wrote.
# Asserted before any consumption, refused by name.  L-273.
DV_KEYS = ["dvs.patchV", "dvs.shape"]
CON_KEYS = ["geometry.rcon", "geometry.thickcon", "geometry.volcon",
            "scenario1.aero_post.functionals.CL"]
OBJ_KEYS = ["scenario1.aero_post.functionals.CD"]
ARRAY_LEN = {"dvs.patchV": 2, "dvs.shape": 8, "geometry.rcon": 2,
             "geometry.thickcon": 20, "geometry.volcon": 1,
             "scenario1.aero_post.functionals.CL": 1,
             "scenario1.aero_post.functionals.CD": 1}

# The marker lines the frozen run script prints at full precision (%.17g).
# These, not the 8-digit debug_print blocks, are the graded endpoint values.
SCALAR_MARKERS = ["D1_OPT_ETA", "D1_FEASIBLE_CD", "D1_FEASIBLE_CL",
                  "D1_DRIVER_WALL_S", "D1_ENDPOINT_PATCHED_CD",
                  "D1_ENDPOINT_PATCHED_CL", "D1_OPT_MAXRSS_GiB"]
VECTOR_MARKERS = ["D1_FEASIBLE_PATCHV", "D1_FEASIBLE_SHAPE",
                  "D1_ENDPOINT_PATCHED_SHAPE", "D1_ENDPOINT_PATCHED_PATCHV"]

# Every channel this comparator CONSUMES.  The planted-zero control plants into
# ALL of them and refuses unless ALL of them read back moved by exactly PLANT.
# A consumed channel the control does not plant into is exactly the hole L-273
# names.
CONSUMED_CHANNELS = ["path_dv", "path_con", "path_obj",
                     "marker_scalar", "marker_vector"]

# Registered offset between the two independent evaluation counters, MEASURED
# on D1 arm O: 13 debug_print blocks against IPOPT's own 12 reported objective
# function evaluations (RESULTS.md section 4.2 and the log itself).
BLOCK_EVAL_OFFSET = 1

FLOAT = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")
ARRAY = re.compile(r"'(?P<key>[A-Za-z0-9_.]+)':\s*array\(\[(?P<body>[^\]]*)\]\)")
COORD = re.compile(r"^Driver debug print for iter coord: rank0:pyOptSparse_"
                   r"(?P<opt>[A-Za-z0-9_]+)\|(?P<idx>\d+)\s*$", re.M)


# ---- refusal ---------------------------------------------------------------

class Refuse(Exception):
    """Raised on any refusal.  Callers exit 2.  Never degrades to a warning."""


def _refuse(tag, payload):
    print("D2_REFUSE %s %s" % (tag, json.dumps(payload, sort_keys=True)),
          flush=True)
    raise Refuse(tag)


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---- the reader ------------------------------------------------------------
# Everything -- the real read, the plant read-back, the negative control and
# the A/B trivial baseline -- goes through read_text().  A control that reads
# back through a different path is not a control.

def read_text(path):
    """THE reader.  One function, one path."""
    with open(path, "r", errors="replace") as fh:
        return fh.read()


def _floats(body):
    return [float(m.group(0)) for m in FLOAT.finditer(body)]


def _blocks(text):
    """Split the log into per-function-evaluation debug_print blocks."""
    hits = list(COORD.finditer(text))
    out = []
    for k, m in enumerate(hits):
        end = hits[k + 1].start() if k + 1 < len(hits) else len(text)
        out.append({"opt": m.group("opt"), "idx": int(m.group("idx")),
                    "span": (m.start(), end), "text": text[m.start():end]})
    return out


def _section(block_text, header):
    """Brace-matched region following a standalone header line."""
    m = re.search(r"^%s\s*$" % re.escape(header), block_text, re.M)
    if m is None:
        return None
    i = block_text.find("{", m.end())
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(block_text)):
        if block_text[j] == "{":
            depth += 1
        elif block_text[j] == "}":
            depth -= 1
            if depth == 0:
                return (i, j + 1, block_text[i:j + 1])
    return None


def _arrays(section_text):
    out = {}
    for m in ARRAY.finditer(section_text):
        out[m.group("key")] = _floats(m.group("body"))
    return out


def read_path(path, expect_opt=None, where=None):
    """The function-evaluation path: one record per debug_print block.

    Refuses by name on a wrong optimizer tag, a wrong key set, a wrong array
    length, or a missing section.  Every refusal exits 2; none degrades.
    """
    where = where or os.path.basename(path)
    text = read_text(path)
    blocks = _blocks(text)
    if not blocks:
        _refuse("NO_PATH_BLOCKS", {"where": where})
    recs = []
    for b in blocks:
        if expect_opt is not None and b["opt"] != expect_opt:
            _refuse("OPTIMIZER_TAG", {"where": where, "block": b["idx"],
                                      "expected": expect_opt,
                                      "found": b["opt"]})
        rec = {"idx": b["idx"], "opt": b["opt"]}
        for header, keys, tag in (("Design Vars", DV_KEYS, "dv"),
                                  ("Nonlinear constraints", CON_KEYS, "con"),
                                  ("Objectives", OBJ_KEYS, "obj")):
            sec = _section(b["text"], header)
            if sec is None:
                _refuse("SECTION_ABSENT", {"where": where, "block": b["idx"],
                                           "header": header})
            arr = _arrays(sec[2])
            have = sorted(arr.keys())
            if have != sorted(keys):
                _refuse("KEYSET", {"where": where, "block": b["idx"],
                                   "header": header, "expected": sorted(keys),
                                   "found": have,
                                   "missing": sorted(set(keys) - set(have)),
                                   "extra": sorted(set(have) - set(keys))})
            for k in keys:
                if len(arr[k]) != ARRAY_LEN[k]:
                    _refuse("ARRAY_LEN", {"where": where, "block": b["idx"],
                                          "key": k, "expected": ARRAY_LEN[k],
                                          "found": len(arr[k])})
            rec[tag] = arr
        recs.append(rec)
    return recs


def read_markers(path, where=None):
    """The full-precision marker lines the frozen run script prints."""
    where = where or os.path.basename(path)
    text = read_text(path)
    out = {}
    for name in SCALAR_MARKERS:
        m = re.search(r"^%s\s+(%s)\s*$" % (re.escape(name), FLOAT.pattern),
                      text, re.M)
        out[name] = None if m is None else float(m.group(1))
    for name in VECTOR_MARKERS:
        m = re.search(r"^%s\s+(\[[^\]]*\])\s*$" % re.escape(name), text, re.M)
        out[name] = None if m is None else json.loads(m.group(1))
    return out


def assert_markers_present(mk, needed, where):
    missing = [k for k in needed if mk.get(k) is None]
    if missing:
        _refuse("MARKER_ABSENT", {"where": where, "missing": missing})
    return True


# ---- gate G5: the planted-zero control, against the REAL artifact -----------

def _plant_text(text):
    """Perturb EVERY consumed channel by exactly PLANT, in the log's own
    syntax, so the plant is read back through the same reader."""
    def _arr(m):
        vals = [v + PLANT for v in _floats(m.group("body"))]
        return "'%s': array([%s])" % (m.group("key"),
                                      ", ".join("%.17g" % v for v in vals))
    out = ARRAY.sub(_arr, text)

    def _scal(m):
        return "%s %.17g" % (m.group(1), float(m.group(2)) + PLANT)
    out = re.sub(r"^(%s)\s+(%s)\s*$" % ("|".join(SCALAR_MARKERS),
                                        FLOAT.pattern),
                 _scal, out, flags=re.M)

    def _vec(m):
        vals = [v + PLANT for v in json.loads(m.group(2))]
        return "%s %s" % (m.group(1), json.dumps(vals))
    out = re.sub(r"^(%s)\s+(\[[^\]]*\])\s*$" % "|".join(VECTOR_MARKERS),
                 _vec, out, flags=re.M)
    return out


def _channel_deltas(base_recs, back_recs, base_mk, back_mk):
    """Read-back deltas per consumed channel, as max |delta - PLANT|."""
    out = {}
    for tag, keys, name in (("dv", DV_KEYS, "path_dv"),
                            ("con", CON_KEYS, "path_con"),
                            ("obj", OBJ_KEYS, "path_obj")):
        worst = 0.0
        for a, b in zip(base_recs, back_recs):
            for k in keys:
                for x, y in zip(a[tag][k], b[tag][k]):
                    worst = max(worst, abs((y - x) - PLANT))
        out[name] = worst
    worst = 0.0
    for k in SCALAR_MARKERS:
        if base_mk.get(k) is None:
            continue
        worst = max(worst, abs((back_mk[k] - base_mk[k]) - PLANT))
    out["marker_scalar"] = worst
    worst = 0.0
    for k in VECTOR_MARKERS:
        if base_mk.get(k) is None:
            continue
        for x, y in zip(base_mk[k], back_mk[k]):
            worst = max(worst, abs((y - x) - PLANT))
    out["marker_vector"] = worst
    return out


def planted_zero_control(src_log, workdir, expect_opt, src_md5=None,
                         reader=read_path, marker_reader=read_markers):
    """CLAUDE.md rule 3, with L-273's coupling half.

    Plants into a COPY OF A REAL ARM LOG -- never a synthetic fixture -- reads
    it back through the SAME readers, and REFUSES (exit 2) unless every
    consumed channel moved by exactly the plant.  Asserts the source md5 before
    and after, so the control cannot damage the evidence it reads.
    """
    got = md5_of(src_log)
    if src_md5 is not None and got != src_md5:
        _refuse("SRC_MD5", {"path": src_log, "expected": src_md5,
                            "found": got})
    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    planted = os.path.join(workdir, "planted_control.log")
    with open(planted, "w") as fh:
        fh.write(_plant_text(read_text(src_log)))

    base_recs = reader(src_log, expect_opt=expect_opt, where="src")
    back_recs = reader(planted, expect_opt=expect_opt, where="planted")
    base_mk = marker_reader(src_log, where="src")
    back_mk = marker_reader(planted, where="planted")
    if len(base_recs) != len(back_recs):
        _refuse("PLANT_BLOCK_COUNT", {"base": len(base_recs),
                                      "planted": len(back_recs)})
    d = _channel_deltas(base_recs, back_recs, base_mk, back_mk)
    os.remove(planted)

    seen = {k: bool(d[k] < 1e-12) for k in CONSUMED_CHANNELS}
    after = md5_of(src_log)
    out = {"plant": PLANT, "channels_planted": CONSUMED_CHANNELS,
           "max_residual_vs_plant": d, "channel_seen": seen,
           "n_blocks": len(base_recs),
           "src_md5_before": got, "src_md5_after": after,
           "src_unchanged": bool(got == after),
           "pass": bool(all(seen.values()) and got == after)}
    if not out["pass"]:
        _refuse("PLANTED_ZERO", out)
    print("D2_G5_PLANTED_ZERO OK %s" % json.dumps(out, sort_keys=True),
          flush=True)
    return out


def negative_control(src_log, workdir, expect_opt):
    """The control must be able to FAIL.  A deliberately blind reader -- one
    that returns the unperturbed parse whatever path it is handed -- must be
    REFUSED.  A planted-zero control that cannot refuse is not a control."""
    def blind_path(_p, expect_opt=None, where=None, _s=src_log):
        return read_path(_s, expect_opt=expect_opt, where=where)

    def blind_mk(_p, where=None, _s=src_log):
        return read_markers(_s, where=where)

    try:
        planted_zero_control(src_log, workdir, expect_opt,
                             reader=blind_path, marker_reader=blind_mk)
    except Refuse as exc:
        print("D2_G5_NEGATIVE_CONTROL OK refused=%s" % exc, flush=True)
        return {"pass": True, "refused_with": str(exc)}
    print("D2_G5_NEGATIVE_CONTROL FAILED blind reader was accepted",
          flush=True)
    return {"pass": False, "refused_with": None}


def keyset_control(src_log, workdir, expect_opt):
    """L-273's own defect, replayed as a live control on THIS producer.

    Rename the producer's objective key to `...CD_final` -- the exact shape of
    the mismatch that killed D1 arm C at 14 s of container time -- and require
    a NAMED refusal rather than a KeyError deep inside a consumer.
    """
    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    broken = os.path.join(workdir, "keyset_control_renamed.log")
    with open(broken, "w") as fh:
        fh.write(read_text(src_log).replace(
            "'scenario1.aero_post.functionals.CD'",
            "'scenario1.aero_post.functionals.CD_final'"))
    try:
        read_path(broken, expect_opt=expect_opt, where="keyset_control")
    except Refuse as exc:
        os.remove(broken)
        print("D2_G5_KEYSET_CONTROL OK refused=%s" % exc, flush=True)
        return {"pass": True, "refused_with": str(exc)}
    os.remove(broken)
    print("D2_G5_KEYSET_CONTROL FAILED renamed key was accepted", flush=True)
    return {"pass": False, "refused_with": None}


def tag_control(src_log, workdir, expect_opt):
    """An A/B consumes two logs.  A comparator that cannot tell which arm it is
    reading can silently compare an arm with itself.  Rename the optimizer tag
    and require a NAMED refusal."""
    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    broken = os.path.join(workdir, "tag_control_renamed.log")
    with open(broken, "w") as fh:
        fh.write(read_text(src_log).replace("pyOptSparse_%s|" % expect_opt,
                                            "pyOptSparse_WRONGOPT|"))
    try:
        read_path(broken, expect_opt=expect_opt, where="tag_control")
    except Refuse as exc:
        os.remove(broken)
        print("D2_G5_TAG_CONTROL OK refused=%s" % exc, flush=True)
        return {"pass": True, "refused_with": str(exc)}
    os.remove(broken)
    print("D2_G5_TAG_CONTROL FAILED wrong optimizer tag was accepted",
          flush=True)
    return {"pass": False, "refused_with": None}


# ---- the statistics --------------------------------------------------------

def path_cl(recs):
    return [r["con"]["scenario1.aero_post.functionals.CL"][0] for r in recs]


def path_cd(recs):
    return [r["obj"]["scenario1.aero_post.functionals.CD"][0] for r in recs]


def path_max_cl_violation(recs):
    """Gate AB4: max |CL - CL_TARGET| over the whole evaluation path.

    This is a statement about the OPTIMISER'S PATH and never about the flow.
    """
    cl = path_cl(recs)
    v = [abs(c - CL_TARGET) for c in cl]
    i = max(range(len(v)), key=lambda k: v[k])
    return {"max": v[i], "at_block": recs[i]["idx"], "n": len(v),
            "first": v[0], "last": v[-1]}


def l2(v):
    return sum(x * x for x in v) ** 0.5


def linf(v):
    return max(abs(x) for x in v)


def compare(a_mk, b_mk, a_recs, b_recs):
    """The A/B comparison statistics, all of them, in one place."""
    sa = a_mk["D1_ENDPOINT_PATCHED_SHAPE"]
    sb = b_mk["D1_ENDPOINT_PATCHED_SHAPE"]
    d_shape = [y - x for x, y in zip(sa, sb)]
    cda = a_mk["D1_ENDPOINT_PATCHED_CD"]
    cdb = b_mk["D1_ENDPOINT_PATCHED_CD"]
    aoa_a = a_mk["D1_ENDPOINT_PATCHED_PATCHV"][1]
    aoa_b = b_mk["D1_ENDPOINT_PATCHED_PATCHV"][1]
    va = path_max_cl_violation(a_recs)
    vb = path_max_cl_violation(b_recs)
    return {
        "AB1_dCD_abs": cdb - cda,
        "AB1_dCD_rel": abs(cdb - cda) / abs(cda),
        "AB2_dshape_l2_rel": l2(d_shape) / l2(sa),
        "AB2_dshape_linf": linf(d_shape),
        "AB2_dAoA_deg": abs(aoa_b - aoa_a),
        "AB3_blocks_A": len(a_recs), "AB3_blocks_B": len(b_recs),
        "AB4_Vmax_A": va, "AB4_Vmax_B": vb,
        "AB4_ratio_B_over_A": (vb["max"] / va["max"]) if va["max"] > 0 else None,
        "CD_A": cda, "CD_B": cdb,
        "CL_A": a_mk["D1_ENDPOINT_PATCHED_CL"],
        "CL_B": b_mk["D1_ENDPOINT_PATCHED_CL"],
        "AoA_A": aoa_a, "AoA_B": aoa_b,
        "driver_wall_s_A": a_mk["D1_DRIVER_WALL_S"],
        "driver_wall_s_B": b_mk["D1_DRIVER_WALL_S"],
    }


def eta_observed(cd_series, n_last=5):
    """Peak-to-peak of the last n_last printed CD samples.

    D1 Amendment 2 A2.2's registered definition, reused at GRADING time only,
    as an OBSERVATION.  It sizes NOTHING -- every step either arm uses is
    selected inside the container from |J_adj| and the INHERITED eta.
    """
    tail = list(cd_series)[-int(n_last):]
    if len(tail) < 2:
        return None
    return max(tail) - min(tail)


def selftest_stats():
    """A statistic that cannot find a planted maximum is not permitted to
    compare two optimisers."""
    recs = []
    for k, cl in enumerate([0.5, 0.5 + 3.0e-3, 0.5 - 7.0e-3, 0.5 + 1.0e-6]):
        recs.append({"idx": k, "opt": "T",
                     "con": {"scenario1.aero_post.functionals.CL": [cl]},
                     "obj": {"scenario1.aero_post.functionals.CD": [0.02]}})
    r = path_max_cl_violation(recs)
    ok_max = abs(r["max"] - 7.0e-3) < 1e-15 and r["at_block"] == 2
    ok_l2 = abs(l2([3.0, 4.0]) - 5.0) < 1e-15
    ok_inf = abs(linf([-9.0, 2.0]) - 9.0) < 1e-15
    ok_eta = abs(eta_observed([1.0, 2.0, 3.0, 4.0, 4.5, 4.25], 5) - 2.5) < 1e-15
    return {"path_max": r, "pass": bool(ok_max and ok_l2 and ok_inf and ok_eta),
            "l2_ok": ok_l2, "linf_ok": ok_inf, "eta_ok": ok_eta}


def ab_trivial_baseline(src_log, workdir, expect_opt):
    """DAFOAM_CHARTER.md section 4, in the A/B's own currency.

    (a) The comparator run on one arm against ITSELF must return EXACTLY zero
        on every comparison statistic.  (b) The same comparator, run against a
        copy of that log whose FIRST shape mode has been moved by
        AB_TRIVIAL_SHIFT, must SEE that planted difference at its planted size
        and must FAIL BOTH of gate AB2's frozen bands.  A comparison that
        cannot fail is not a comparison.  (c) The smaller AB_RESOLUTION_SHIFT
        is run and REPORTED so the comparison's measured resolution is on the
        record; it does not gate.
    """
    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    mk = read_markers(src_log, where="src")
    recs = read_path(src_log, expect_opt=expect_opt, where="src")

    same = compare(mk, mk, recs, recs)
    zeros = {k: same[k] for k in ("AB1_dCD_abs", "AB1_dCD_rel",
                                  "AB2_dshape_l2_rel", "AB2_dshape_linf",
                                  "AB2_dAoA_deg")}
    self_zero = all(v == 0.0 for v in zeros.values())

    text = read_text(src_log)
    base_sh = list(mk["D1_ENDPOINT_PATCHED_SHAPE"])
    old = "D1_ENDPOINT_PATCHED_SHAPE %s" % json.dumps(base_sh)
    if old not in text:
        _refuse("AB_TRIVIAL_MARKER", {"where": "ab_trivial", "line": old[:80]})

    def _probe(shift):
        sh = list(base_sh)
        sh[0] = sh[0] + shift
        new = "D1_ENDPOINT_PATCHED_SHAPE %s" % json.dumps(sh)
        p = os.path.join(workdir, "ab_probe_%g.log" % shift)
        with open(p, "w") as fh:
            fh.write(text.replace(old, new))
        m2 = read_markers(p, where="probe")
        r2 = read_path(p, expect_opt=expect_opt, where="probe")
        mv = compare(mk, m2, recs, r2)
        os.remove(p)
        return {"shift": shift,
                "seen": bool(abs(mv["AB2_dshape_linf"] - shift) < 1e-12),
                "dshape_linf": mv["AB2_dshape_linf"],
                "dshape_l2_rel": mv["AB2_dshape_l2_rel"],
                "fails_AB2_l2": bool(mv["AB2_dshape_l2_rel"] > AB2_BAND_L2_REL),
                "fails_AB2_linf": bool(mv["AB2_dshape_linf"] > AB2_BAND_LINF)}

    prim = _probe(AB_TRIVIAL_SHIFT)
    reso = _probe(AB_RESOLUTION_SHIFT)
    out = {"self_comparison_all_zero": bool(self_zero),
           "self_comparison": zeros,
           "AB2_bands": {"l2_rel": AB2_BAND_L2_REL, "linf": AB2_BAND_LINF},
           "trivial_baseline": prim,
           "resolution_probe_REPORTED_ONLY": reso,
           "pass": bool(self_zero and prim["seen"] and prim["fails_AB2_l2"]
                        and prim["fails_AB2_linf"])}
    if not out["pass"]:
        _refuse("AB_TRIVIAL", out)
    print("D2_G5_AB_TRIVIAL OK %s" % json.dumps(out, sort_keys=True),
          flush=True)
    return out


# ---- CLI: the zero-compute controls, runnable on the HOST -------------------

def _usage():
    print("usage: d2_ab.py selftest | plantcheck LOG WORKDIR OPT [MD5] | "
          "negcheck LOG WORKDIR OPT | keycheck LOG WORKDIR OPT | "
          "tagcheck LOG WORKDIR OPT | abtrivial LOG WORKDIR OPT | "
          "path LOG OPT")
    raise SystemExit(2)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        _usage()
    cmd = a[0]
    try:
        if cmd == "selftest":
            r = selftest_stats()
            print("D2_SELFTEST_STATS %s" % json.dumps(r, sort_keys=True),
                  flush=True)
            raise SystemExit(0 if r["pass"] else 2)
        if cmd == "plantcheck" and len(a) >= 4:
            planted_zero_control(a[1], a[2], a[3],
                                 src_md5=(a[4] if len(a) > 4 else None))
            raise SystemExit(0)
        if cmd == "negcheck" and len(a) >= 4:
            r = negative_control(a[1], a[2], a[3])
            raise SystemExit(0 if r["pass"] else 2)
        if cmd == "keycheck" and len(a) >= 4:
            r = keyset_control(a[1], a[2], a[3])
            raise SystemExit(0 if r["pass"] else 2)
        if cmd == "tagcheck" and len(a) >= 4:
            r = tag_control(a[1], a[2], a[3])
            raise SystemExit(0 if r["pass"] else 2)
        if cmd == "abtrivial" and len(a) >= 4:
            r = ab_trivial_baseline(a[1], a[2], a[3])
            raise SystemExit(0 if r["pass"] else 2)
        if cmd == "path" and len(a) >= 3:
            recs = read_path(a[1], expect_opt=a[2], where="path")
            mk = read_markers(a[1], where="path")
            v = path_max_cl_violation(recs)
            print("D2_PATH_BLOCKS %d" % len(recs), flush=True)
            print("D2_PATH_CL_VIOLATION %s" % json.dumps(v, sort_keys=True),
                  flush=True)
            print("D2_PATH_CL %s" % json.dumps(
                ["%.8g" % c for c in path_cl(recs)]), flush=True)
            print("D2_PATH_CD %s" % json.dumps(
                ["%.8g" % c for c in path_cd(recs)]), flush=True)
            print("D2_MARKERS %s" % json.dumps(mk, sort_keys=True), flush=True)
            print("D2_SHAPE_L2 %.17g"
                  % l2(mk["D1_ENDPOINT_PATCHED_SHAPE"]), flush=True)
            raise SystemExit(0)
    except Refuse:
        raise SystemExit(2)
    _usage()
