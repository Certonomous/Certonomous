"""D13 basin/restart comparator core: the frozen start set, the frozen
equivalence band, the readers, and the controls.

Frozen by the commit that carries
`cases/dafoam/ladder-a/A1/curriculum_D13/PREREGISTRATION.md`.
NOT EDITED AFTER THE FIRST LAUNCH.  An edit voids every start that ran before it.

Standard library ONLY, on purpose.  This module must be importable and runnable
on the HOST, outside any container, so that every control below can be dry-run
against D1 arm O's REAL endpoint JSON BEFORE the freeze, at zero compute.
That dry run is the point: a control that plants into its own synthetic fixture
proves the arithmetic and not the coupling, and the coupling is the half that
broke D1 arm C at 14 s on a `KeyError: 'CD_final'` (L-273).

THE L-302 REPAIR IS THE REASON THIS FILE EXISTS SEPARATELY FROM THE GRADER.
`curriculum_D3/d3_grade.py` returns PASS at 0.0000 % with zero sign flips over
an EMPTY COMPONENT SET: a present-but-unparseable FD block yields an empty list
under a key that IS present, the refusal tests key presence and never
non-emptiness, and the plateau loop iterates zero times.  A PARTIAL PLANT READS
ON THE PAGE EXACTLY LIKE A COMPLETE ONE.  `fd_table_gate` below therefore
refuses on an EMPTY or SHORT component set EXPLICITLY, BY COUNT, WITH THE COUNT
PRINTED, and `emptyset_control` / `shortset_control` prove that it does.

Nothing here selects a step.  Every step used by every start is selected inside
the container by the frozen D1 instrument `d1_fd_endpoint.py`
(md5 7e454d2f1830a40086465d9b5c57a941) from |J_adj| and the inherited eta alone.
This file only READS what the starts printed and COMPARES them.
"""

import copy
import hashlib
import itertools
import json
import os
import re

# ===========================================================================
# 1.  THE FROZEN START SET  (PREREGISTRATION.md section 6)
# ===========================================================================
# Generator, registered so the set is regenerable:
#     numpy 2.5.1, rng = numpy.random.default_rng(13)      # PCG64
#     dshape = rng.uniform(-1.0e-2, +1.0e-2, size=(5, 8))  # drawn FIRST
#     daoa   = rng.uniform(-1.0,    +1.0,    size=5)       # drawn SECOND
# The LITERAL TABLE BELOW IS THE AUTHORITY.  The seed is documentation of how
# the table was made; the table is what defines the experiment.  A start set
# that cannot be regenerated is not a registered experiment, and a start set
# whose identity depends on an RNG implementation detail is not one either.
SEED = 13
DELTA_SHAPE = 1.0e-2          # perturbation magnitude, shape modes (abs)
DELTA_AOA = 1.0               # perturbation magnitude, AoA (degrees)
NUMPY_GENERATOR = "numpy.random.default_rng(13) -> PCG64, numpy 2.5.1"

AOA0 = 5.13918623195176       # the case's own, runScript.py / d1_opt_runScript.py
U0 = 10.0                     # pinned, inert
CL_TARGET = 0.5

STARTS = {
    1: {"shape": [+7.295951740332e-03, +7.106050298641e-03, +6.220467975687e-03,
                  -4.771072771670e-03, -8.456010845632e-03, +8.929315608921e-03,
                  +2.275833820942e-03, -9.947384927474e-03],
        "daoa": +3.193426416986e-01},
    2: {"shape": [+8.208143561317e-03, +9.696069504751e-03, -4.274067916677e-03,
                  +6.273222460780e-03, -8.351841122374e-03, -1.234399053932e-03,
                  +6.354075494896e-03, -1.825333346205e-03],
        "daoa": -8.843407984147e-02},
    3: {"shape": [+3.549941437395e-04, -7.659202330499e-03, +6.280130385002e-03,
                  -4.265183334976e-05, -5.034416102267e-03, +5.533723120017e-03,
                  +9.584565783791e-03, +7.668646815258e-04],
        "daoa": +4.653029336944e-01},
    4: {"shape": [+4.743004452416e-03, +9.855213776967e-03, -9.397450072494e-03,
                  +1.979553047335e-03, +9.345905555832e-03, -7.653268523134e-03,
                  -5.537970100122e-03, +1.004567779667e-03],
        "daoa": -4.421993819611e-02},
    5: {"shape": [+4.446546214396e-03, +1.055048307897e-03, +9.540359128473e-04,
                  -8.969223410513e-03, +4.784594243895e-03, -3.585969801544e-03,
                  -8.520762524172e-03, +9.169366388253e-03],
        "daoa": -7.505573333882e-01},
}
START_IDS = [1, 2, 3, 4, 5]


def start_vectors(k):
    """The (shape, patchV) a start is set to.  The ONLY place D13 sets a DV."""
    s = STARTS[k]
    if len(s["shape"]) != 8:
        _refuse("START_LEN", {"start": k, "n": len(s["shape"])})
    for v in s["shape"]:
        if abs(v) > DELTA_SHAPE * (1.0 + 1e-12):
            _refuse("START_MAGNITUDE", {"start": k, "v": v,
                                        "bound": DELTA_SHAPE})
    if abs(s["daoa"]) > DELTA_AOA * (1.0 + 1e-12):
        _refuse("START_AOA_MAGNITUDE", {"start": k, "v": s["daoa"],
                                        "bound": DELTA_AOA})
    return list(s["shape"]), [U0, AOA0 + s["daoa"]]


# ===========================================================================
# 2.  THE FROZEN EQUIVALENCE BAND  (PREREGISTRATION.md section 4)
# ===========================================================================
# THE WHOLE ITEM IS THIS BAND, AND IT IS SIZED FROM MEASURED ARTIFACTS.
#
# eps_* -- the SAME-OPTIMUM band.  Below it, two optima are not distinguishable
# by any instrument this case possesses.
#   eps_CD    = eta, A1's OWN measured CD plateau noise, peak-to-peak of the
#               last 5 samples at printInterval 10: 1.957349804806996e-08.
#               MEASURED, D1 arm E run 2, on this exact case and mesh.
#   eps_shape = SHAPE_FLOOR from the frozen d1_fd_endpoint.py, described there
#               as "A1's own measured roundoff branch": 1.0e-4.  A shape
#               displacement below it is not resolvable by this case's own
#               finite differences.
#   eps_aoa   = PATCHV_FLOOR from the same frozen file: 1.0e-3 deg.
# The first-order objective consequence of a DV difference at eps is bounded by
# D1's MEASURED endpoint dual infeasibility 4.0871293161759560e-07 times
# ||dx|| <= sqrt(8*(1e-4)^2 + (1e-3)^2) = 1.039e-3, i.e. 4.25e-10 -- 46x below
# eps_CD.  eps_CD is therefore dominated by the measured primal noise floor,
# which is the correct thing for it to be dominated by.
#
# dfd_* -- the FD-NOISE PROXY, the upper edge of the unresolvable window.
# The curriculum's named failure mode for D13 is "declaring one basin from
# optima that differ inside FD noise".  D1's MEASURED endpoint FD agreement was
# <= 0.2553 % relative on 4/4 named components with zero sign flips
# (curriculum_D1/RESULTS.md section 5.2, worst component patchV[1]).  That
# figure is an agreement between an ADJOINT and a FINITE DIFFERENCE on a
# GRADIENT COMPONENT.  Reusing it as a tolerance on a DESIGN VECTOR and on an
# OBJECTIVE IS A PROXY, NOT A MEASUREMENT OF EITHER, and this file says so
# here, the pre-registration says so in section 4, and the results record says
# so again.  It is used because it is the only endpoint-noise figure measured
# on this case, and because sizing the window from nothing would be worse.
ETA = 1.957349804806996e-08
EPS_CD = ETA
EPS_SHAPE = 1.0e-4
EPS_AOA = 1.0e-3

DFD_REL = 0.002553            # 0.2553 %, D1 RESULTS.md section 5.2, MEASURED

# D1 arm O, the frozen external reference and the 6th member of the comparison.
# Values from the artifact, not from prose:
#   /home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/armO/
#       endpoint_20260824T160552Z_1399954.json   md5 e63f57710cee6e2170f2e9cef39f8b2a
# cross-checked against curriculum_D1/RESULTS.md section 4.4.
D1_ENDPOINT_JSON = ("/home/ubuntu/certonomous-runs/"
                    "CURRICULUM-D1-a1-constrained-opt/armO/"
                    "endpoint_20260824T160552Z_1399954.json")
D1_ENDPOINT_MD5 = "e63f57710cee6e2170f2e9cef39f8b2a"
D1_REF = {
    "CD": 0.017527899854535338,
    "CL": 0.4999998120936336,
    "shape": [0.02876504584608877, 0.047201042921213354,
              0.016871666037627377, 0.036676713888073136,
              0.0472289265360477, 0.022959816884178426,
              0.008262623112944891, 0.036138219756860344],
    "patchV": [10.0, 1.128636497545056],
    "majors": 11,
    "nlp_error": 4.0871293161759560e-07,
    "constr_viol": 1.9421312102974042e-07,
}

# The proxy tolerances, DERIVED from the two measured inputs above, in this
# file, so that the arithmetic is auditable and no magic number is typed in.
DFD_CD = DFD_REL * D1_REF["CD"]                       # 4.474873e-05
DFD_SHAPE = DFD_REL * max(abs(v) for v in D1_REF["shape"])   # 1.205754e-04
DFD_AOA = DFD_REL * abs(D1_REF["patchV"][1])          # 2.881409e-03

# ===========================================================================
# 3.  THE FROZEN PER-START GATES  (PREREGISTRATION.md section 7)
# ===========================================================================
CL_TOL = 1.0e-5               # |CL - CL*|, D1's own registered tolerance
CONSTR_VIOL_TOL = 1.0e-5      # IPOPT's own reported constraint violation
THICKCON_LO, THICKCON_HI = 0.5 - 1e-6, 3.0 + 1e-6
VOLCON_LO = 1.0 - 1e-6
RCON_LO = 0.8 - 1e-6
FD_REL_TOL = 0.05             # 5 % per graded component, DAFOAM_CHARTER section 2
MIN_GRADED = 3                # >= 3 NAMED components, the brief's floor
NAMED = ["shape[6]", "shape[1]", "shape[5]", "patchV[1]"]
CMIN = 5.0                    # clearance, from the frozen d1_fd_endpoint.py
PLATEAU_TOL = 0.10            # two-step agreement, from the same frozen file
IPOPT_OK = "EXIT: Optimal Solution Found."
MAX_ITER_CAP = 40             # the run script's own registered cap

PLANT = 1.234e-03             # CLAUDE.md rule 3

# Every channel this comparator CONSUMES.  The planted-zero control plants into
# ALL of them and refuses unless ALL of them read back moved by exactly PLANT.
# A consumed channel the control does not plant into is exactly the hole L-273
# names and the hole L-302 names.
CONSUMED_CHANNELS = ["CD", "shape", "patchV", "fd_adj", "fd_value"]

# The producer's ACTUAL key set, asserted before any consumption, refused BY
# NAME.  D1 arm C died on `CD_final`; the key here is `CD`, and this list is
# what makes that impossible to repeat silently.
TOP_KEYS = ["CD", "CL", "cons", "eta", "fd", "J_adj", "patchV", "plan",
            "shape", "tag", "trivial"]
D13_KEYS = ["start_id", "start_shape", "start_patchV", "start_cons",
            "feasible_CD", "feasible_CL", "feasible_patchV",
            "driver_wall_s", "ipopt_exit", "ipopt_majors"]


# ===========================================================================
# 4.  refusal
# ===========================================================================
class Refuse(Exception):
    """Raised on any refusal.  Callers exit 2.  NEVER degrades to a warning."""


def _refuse(tag, payload):
    print("D13_REFUSE %s %s" % (tag, json.dumps(payload, sort_keys=True)),
          flush=True)
    raise Refuse(tag)


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ===========================================================================
# 5.  the reader
# ===========================================================================
def read_endpoint(path, require_d13=True, where="?"):
    """Read one endpoint JSON and REFUSE BY NAME on any missing or malformed
    channel.  Nothing downstream is allowed to touch a dict this did not clear.
    """
    if not os.path.isfile(path):
        _refuse("NO_SUCH_ENDPOINT", {"path": path, "where": where})
    with open(path) as fh:
        try:
            d = json.load(fh)
        except Exception as exc:
            _refuse("ENDPOINT_UNPARSEABLE", {"path": path, "err": str(exc)})
    missing = [k for k in TOP_KEYS if k not in d]
    if missing:
        _refuse("ENDPOINT_KEYSET", {"path": path, "missing": missing,
                                    "found": sorted(d.keys())})
    if require_d13:
        m2 = [k for k in D13_KEYS if k not in d]
        if m2:
            _refuse("ENDPOINT_D13_KEYSET", {"path": path, "missing": m2})
    for k in ("CD", "CL", "eta"):
        if not isinstance(d[k], float):
            _refuse("ENDPOINT_NOT_FLOAT", {"path": path, "key": k,
                                           "type": type(d[k]).__name__})
    if not isinstance(d["shape"], list) or len(d["shape"]) != 8:
        _refuse("ENDPOINT_SHAPE_LEN",
                {"path": path,
                 "n": (len(d["shape"]) if isinstance(d["shape"], list) else -1)})
    if not isinstance(d["patchV"], list) or len(d["patchV"]) != 2:
        _refuse("ENDPOINT_PATCHV_LEN", {"path": path})
    if not isinstance(d["fd"], dict) or len(d["fd"]) == 0:
        _refuse("ENDPOINT_FD_EMPTY",
                {"path": path,
                 "n_fd": (len(d["fd"]) if isinstance(d["fd"], dict) else -1)})
    return d


IPOPT_ITERS = re.compile(r"^Number of Iterations\.*:\s*(\d+)\s*$", re.M)
IPOPT_NLP = re.compile(r"^Overall NLP error\.*:\s*([-+0-9.eE]+)\s*$", re.M)
IPOPT_CV = re.compile(r"^Constraint violation\.*:\s*([-+0-9.eE]+)\s*$", re.M)
IPOPT_EXIT = re.compile(r"^(EXIT:.*)$", re.M)


def read_ipopt(path, where="?"):
    """Read IPOPT's own file.  This is the SECOND, INDEPENDENT channel for the
    termination statement; the producer also embeds it in the JSON, and the
    grader refuses if the two disagree."""
    if not os.path.isfile(path):
        _refuse("NO_SUCH_IPOPT", {"path": path, "where": where})
    with open(path) as fh:
        txt = fh.read()
    ex = IPOPT_EXIT.findall(txt)
    it = IPOPT_ITERS.findall(txt)
    nl = IPOPT_NLP.findall(txt)
    cv = IPOPT_CV.findall(txt)
    if not ex:
        _refuse("IPOPT_NO_EXIT_LINE", {"path": path, "bytes": len(txt)})
    if not it:
        _refuse("IPOPT_NO_ITER_LINE", {"path": path, "bytes": len(txt)})
    return {"exit": ex[-1].strip(), "majors": int(it[-1]),
            "nlp_error": (float(nl[-1]) if nl else None),
            "constr_viol": (float(cv[-1]) if cv else None)}


# ===========================================================================
# 6.  THE FD-TABLE GATE  --  the L-302 repair, and the reason for this module
# ===========================================================================
def fd_table_gate(ep, where="?"):
    """Gate G3.  DAFOAM_CHARTER.md section 2: a DAFoam gradient is not a result
    until a finite-difference table stands beside it AT A STEP PROVED TO LIE IN
    THE PLATEAU.

    THIS GATE COUNTS.  It refuses, by count, with the count printed, on:
      * an fd block that is not a dict, or is empty;
      * a NAMED component absent from the fd block;
      * a component whose `steps` lacks either rung, or whose rungs carry no
        numeric `fd`;
      * FEWER THAN MIN_GRADED components surviving the plateau + clearance
        tests.
    `graded` is RE-DERIVED here from the raw fd/step/C numbers.  The producer's
    own `graded` boolean is read only to cross-check and a disagreement
    REFUSES: an instrument that trusts its producer's verdict is not an
    instrument.

    L-302: an instrument that cannot say "I measured nothing" will report a
    number it did not measure.
    """
    fd = ep.get("fd")
    if not isinstance(fd, dict):
        _refuse("FD_NOT_A_DICT", {"where": where,
                                  "type": type(fd).__name__})
    n_present = len(fd)
    if n_present == 0:
        _refuse("FD_BLOCK_EMPTY", {"where": where, "n_components_present": 0,
                                   "min_required": MIN_GRADED})
    missing = [k for k in NAMED if k not in fd]
    if missing:
        _refuse("FD_NAMED_MISSING", {"where": where, "missing": missing,
                                     "n_components_present": n_present,
                                     "present": sorted(fd.keys())})

    rows = []
    for key in NAMED:
        c = fd[key]
        if not isinstance(c, dict) or "steps" not in c \
                or not isinstance(c["steps"], dict):
            _refuse("FD_COMPONENT_MALFORMED",
                    {"where": where, "component": key,
                     "n_components_present": n_present})
        st = c["steps"]
        for rung in ("s_lo", "s_hi"):
            if rung not in st or not isinstance(st[rung], dict):
                _refuse("FD_RUNG_MISSING",
                        {"where": where, "component": key, "rung": rung,
                         "n_components_present": n_present})
        lo, hi = st["s_lo"], st["s_hi"]
        for rung, blk in (("s_lo", lo), ("s_hi", hi)):
            if not isinstance(blk.get("fd"), float) \
                    or not isinstance(blk.get("step"), float):
                _refuse("FD_RUNG_NOT_NUMERIC",
                        {"where": where, "component": key, "rung": rung,
                         "fd": repr(blk.get("fd")),
                         "step": repr(blk.get("step")),
                         "n_components_present": n_present})
        adj = float(c["J_adj"])
        fdhi = float(hi["fd"])
        fdlo = float(lo["fd"])
        if fdhi == 0.0:
            _refuse("FD_ZERO_REFERENCE",
                    {"where": where, "component": key,
                     "n_components_present": n_present})
        # re-derived, never inherited
        plateau = abs(fdhi - fdlo) / abs(fdhi)
        c_meas = abs(fdhi) * 2.0 * float(hi["step"]) / float(ep["eta"])
        rel = abs(adj - fdhi) / abs(fdhi)
        flip = (adj * fdhi) < 0.0
        graded = bool(plateau <= PLATEAU_TOL and c_meas >= CMIN)
        claimed = bool(c.get("graded", None))
        if claimed != graded:
            _refuse("FD_GRADED_DISAGREES",
                    {"where": where, "component": key,
                     "producer_said": claimed, "gate_derived": graded,
                     "plateau": plateau, "C_measured": c_meas})
        rows.append({"component": key, "J_adj": adj, "fd_lo": fdlo,
                     "fd_hi": fdhi, "step_hi": float(hi["step"]),
                     "plateau": plateau, "C_measured": c_meas,
                     "rel_err": rel, "sign_flip": bool(flip),
                     "graded": graded})

    graded_rows = [r for r in rows if r["graded"]]
    n_graded = len(graded_rows)
    # THE COUNT REFUSAL.  This is the clause d3_grade.py does not have.
    print("D13_G3_COMPONENT_COUNT where=%s n_named=%d n_present=%d "
          "n_graded=%d min_required=%d"
          % (where, len(NAMED), n_present, n_graded, MIN_GRADED), flush=True)
    if n_graded < MIN_GRADED:
        _refuse("FD_TOO_FEW_GRADED",
                {"where": where, "n_graded": n_graded,
                 "min_required": MIN_GRADED, "n_components_present": n_present,
                 "rows": [{"component": r["component"],
                           "plateau": r["plateau"],
                           "C_measured": r["C_measured"]} for r in rows]})

    worst = max(r["rel_err"] for r in graded_rows)
    flips = [r["component"] for r in graded_rows if r["sign_flip"]]
    verdict = "PASS" if (worst <= FD_REL_TOL and not flips) else "GATE FAIL"
    return {"rows": rows, "n_present": n_present, "n_graded": n_graded,
            "worst_rel_err": worst, "sign_flips": flips, "verdict": verdict}


# ===========================================================================
# 7.  THE CONTROLS  (CLAUDE.md rule 3)
# ===========================================================================
def _plant(d, plant=PLANT):
    """Plant into EVERY consumed channel.  A consumed channel not planted into
    is a hole that reads on the page exactly like a complete plant."""
    p = copy.deepcopy(d)
    p["CD"] = d["CD"] + plant
    p["shape"] = [v + plant for v in d["shape"]]
    p["patchV"] = [d["patchV"][0], d["patchV"][1] + plant]
    for key, c in p["fd"].items():
        c["J_adj"] = d["fd"][key]["J_adj"] + plant
        for rung in ("s_lo", "s_hi"):
            if rung in c["steps"] and isinstance(c["steps"][rung], dict) \
                    and isinstance(c["steps"][rung].get("fd"), float):
                c["steps"][rung]["fd"] = \
                    d["fd"][key]["steps"][rung]["fd"] + plant
    return p


def _deltas(base, back, plant=PLANT):
    out = {}
    out["CD"] = abs((back["CD"] - base["CD"]) - plant)
    out["shape"] = max(abs((b - a) - plant)
                       for a, b in zip(base["shape"], back["shape"]))
    out["patchV"] = abs((back["patchV"][1] - base["patchV"][1]) - plant)
    w = 0.0
    for key in base["fd"]:
        w = max(w, abs((back["fd"][key]["J_adj"]
                        - base["fd"][key]["J_adj"]) - plant))
    out["fd_adj"] = w
    w = 0.0
    for key in base["fd"]:
        for rung in ("s_lo", "s_hi"):
            a = base["fd"][key]["steps"][rung].get("fd")
            b = back["fd"][key]["steps"][rung].get("fd")
            if isinstance(a, float) and isinstance(b, float):
                w = max(w, abs((b - a) - plant))
    out["fd_value"] = w
    return out


def planted_zero_control(src_json, workdir, src_md5=None,
                         reader=read_endpoint, require_d13=True):
    """CLAUDE.md rule 3, with L-273's coupling half.

    Plants into a COPY OF A REAL ENDPOINT JSON -- never a synthetic fixture --
    reads it back through the SAME reader, and REFUSES (exit 2) unless EVERY
    consumed channel moved by exactly the plant.  Asserts the source md5 before
    and after, so the control cannot damage the evidence it reads.
    """
    got = md5_of(src_json)
    if src_md5 is not None and got != src_md5:
        _refuse("SRC_MD5", {"path": src_json, "expected": src_md5,
                            "found": got})
    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    planted = os.path.join(workdir, "planted_control.json")
    base = reader(src_json, require_d13=require_d13, where="src")
    with open(planted, "w") as fh:
        json.dump(_plant(base), fh)
    back = reader(planted, require_d13=require_d13, where="planted")
    d = _deltas(base, back)
    os.remove(planted)
    seen = {k: bool(d[k] < 1e-12) for k in CONSUMED_CHANNELS}
    after = md5_of(src_json)
    out = {"plant": PLANT, "channels_planted": CONSUMED_CHANNELS,
           "max_residual_vs_plant": d, "channel_seen": seen,
           "src_md5_before": got, "src_md5_after": after,
           "src_unchanged": bool(got == after),
           "pass": bool(all(seen.values()) and got == after)}
    if not out["pass"]:
        _refuse("PLANTED_ZERO", out)
    print("D13_G5_PLANTED_ZERO OK %s" % json.dumps(out, sort_keys=True),
          flush=True)
    return out


def negative_control(src_json, workdir, require_d13=True):
    """The control must be able to FAIL.  A deliberately blind reader -- one
    that returns the unperturbed parse whatever path it is handed -- must be
    REFUSED.  A planted-zero control that cannot refuse is not a control."""
    def blind(_p, require_d13=True, where=None, _s=src_json):
        return read_endpoint(_s, require_d13=require_d13, where=where)

    try:
        planted_zero_control(src_json, workdir, reader=blind,
                             require_d13=require_d13)
    except Refuse as exc:
        print("D13_G5_NEGATIVE_CONTROL OK refused=%s" % exc, flush=True)
        return {"pass": True, "refused_with": str(exc)}
    print("D13_G5_NEGATIVE_CONTROL FAILED blind reader was accepted",
          flush=True)
    return {"pass": False, "refused_with": None}


def emptyset_control(src_json, require_d13=True):
    """L-302 REPLAYED AS A LIVE CONTROL ON THIS GATE.

    d3_grade.py's G3+G4 returns PASS at 0.0000 % with zero sign flips over an
    EMPTY component set.  Hand `fd_table_gate` exactly that -- a present but
    EMPTY fd dict -- and require a NAMED refusal, not a number."""
    ep = read_endpoint(src_json, require_d13=require_d13, where="emptyset_src")
    broken = copy.deepcopy(ep)
    broken["fd"] = {}
    try:
        fd_table_gate(broken, where="emptyset_control")
    except Refuse as exc:
        print("D13_G5_EMPTYSET_CONTROL OK refused=%s" % exc, flush=True)
        return {"pass": True, "refused_with": str(exc)}
    print("D13_G5_EMPTYSET_CONTROL FAILED empty component set was graded",
          flush=True)
    return {"pass": False, "refused_with": None}


def shortset_control(src_json, require_d13=True):
    """The half-empty case, which reads on the page exactly like the full one.
    Degrade three of the four NAMED components so only ONE can grade, and
    require a NAMED refusal citing the COUNT."""
    ep = read_endpoint(src_json, require_d13=require_d13, where="shortset_src")
    broken = copy.deepcopy(ep)
    for key in NAMED[1:]:
        # break the plateau so the component cannot grade, without removing it
        broken["fd"][key]["steps"]["s_lo"]["fd"] = \
            broken["fd"][key]["steps"]["s_hi"]["fd"] * 5.0
        broken["fd"][key]["graded"] = False
    try:
        fd_table_gate(broken, where="shortset_control")
    except Refuse as exc:
        print("D13_G5_SHORTSET_CONTROL OK refused=%s" % exc, flush=True)
        return {"pass": True, "refused_with": str(exc)}
    print("D13_G5_SHORTSET_CONTROL FAILED short component set was graded",
          flush=True)
    return {"pass": False, "refused_with": None}


def keyset_control(src_json, workdir, require_d13=True):
    """L-273's own defect, replayed live: rename the producer's objective key
    to `CD_final` -- the exact mismatch that killed D1 arm C at 14 s of
    container time -- and require a NAMED refusal, not a KeyError."""
    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    ep = read_endpoint(src_json, require_d13=require_d13, where="keyset_src")
    broken = copy.deepcopy(ep)
    broken["CD_final"] = broken.pop("CD")
    p = os.path.join(workdir, "keyset_control.json")
    with open(p, "w") as fh:
        json.dump(broken, fh)
    try:
        read_endpoint(p, require_d13=require_d13, where="keyset_control")
    except Refuse as exc:
        os.remove(p)
        print("D13_G5_KEYSET_CONTROL OK refused=%s" % exc, flush=True)
        return {"pass": True, "refused_with": str(exc)}
    os.remove(p)
    print("D13_G5_KEYSET_CONTROL FAILED renamed key was accepted", flush=True)
    return {"pass": False, "refused_with": None}


# ===========================================================================
# 8.  THE BASIN COMPARISON  (PREREGISTRATION.md section 4)
# ===========================================================================
CELL_ORDER = {"SAME": 0, "UNRESOLVED": 1, "DIFFERENT": 2}


def _cell(d, eps, dfd):
    if d <= eps:
        return "SAME"
    if d <= dfd:
        return "UNRESOLVED"
    return "DIFFERENT"


def compare_pair(a, b):
    """One pair, three channels, the frozen band.  Pair cell = WORST channel."""
    d_cd = abs(a["CD"] - b["CD"])
    d_sh = max(abs(x - y) for x, y in zip(a["shape"], b["shape"]))
    d_ao = abs(a["patchV"][1] - b["patchV"][1])
    ch = {"CD": {"delta": d_cd, "eps": EPS_CD, "dfd": DFD_CD,
                 "cell": _cell(d_cd, EPS_CD, DFD_CD)},
          "shape_Linf": {"delta": d_sh, "eps": EPS_SHAPE, "dfd": DFD_SHAPE,
                         "cell": _cell(d_sh, EPS_SHAPE, DFD_SHAPE)},
          "aoa_deg": {"delta": d_ao, "eps": EPS_AOA, "dfd": DFD_AOA,
                      "cell": _cell(d_ao, EPS_AOA, DFD_AOA)}}
    worst = max((v["cell"] for v in ch.values()), key=lambda c: CELL_ORDER[c])
    return {"channels": ch, "cell": worst}


def basin_verdict(members):
    """members: ordered list of (label, endpoint-dict).  Returns every pair and
    the item verdict from the FIXED vocabulary.

    Registered precedence, frozen before any start ran:
      any pair DIFFERENT   -> GATE FAIL   (measurably distinct optima; the
                                           same-optimum claim is falsified,
                                           and a falsification is a result)
      else any UNRESOLVED  -> NOT A RESULT (the difference sits inside the FD
                                           noise proxy; the instruments cannot
                                           tell "two optima" from "one optimum
                                           measured twice" -- the curriculum's
                                           OWN named failure mode for D13)
      else all SAME        -> PASS        (one optimum, to below this case's
                                           own measured noise floor)
    DIFFERENT dominates UNRESOLVED because a DIFFERENT pair is RESOLVED by the
    instrument, and a falsified claim is not made unfalsified by a second pair
    the instrument cannot see.
    """
    pairs = []
    for (la, a), (lb, b) in itertools.combinations(members, 2):
        r = compare_pair(a, b)
        r["a"], r["b"] = la, lb
        pairs.append(r)
    cells = [p["cell"] for p in pairs]
    if "DIFFERENT" in cells:
        v = "GATE FAIL"
    elif "UNRESOLVED" in cells:
        v = "NOT A RESULT"
    else:
        v = "PASS"
    return {"pairs": pairs, "n_pairs": len(pairs), "verdict": v,
            "n_same": cells.count("SAME"),
            "n_unresolved": cells.count("UNRESOLVED"),
            "n_different": cells.count("DIFFERENT")}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "bands":
        print(json.dumps({"EPS_CD": EPS_CD, "EPS_SHAPE": EPS_SHAPE,
                          "EPS_AOA": EPS_AOA, "DFD_REL": DFD_REL,
                          "DFD_CD": DFD_CD, "DFD_SHAPE": DFD_SHAPE,
                          "DFD_AOA": DFD_AOA}, indent=1))
        raise SystemExit(0)
    if len(sys.argv) > 2 and sys.argv[1] == "controls":
        # Dry-run every control against D1 arm O's REAL endpoint JSON, on the
        # HOST, at zero compute, BEFORE the freeze.
        wd = sys.argv[2]
        ok = True
        r = planted_zero_control(D1_ENDPOINT_JSON, wd,
                                 src_md5=D1_ENDPOINT_MD5, require_d13=False)
        ok = ok and r["pass"]
        for fn in (negative_control,):
            ok = ok and fn(D1_ENDPOINT_JSON, wd, require_d13=False)["pass"]
        for fn in (emptyset_control, shortset_control):
            ok = ok and fn(D1_ENDPOINT_JSON, require_d13=False)["pass"]
        ok = ok and keyset_control(D1_ENDPOINT_JSON, wd,
                                   require_d13=False)["pass"]
        g = fd_table_gate(read_endpoint(D1_ENDPOINT_JSON, require_d13=False,
                                        where="D1_armO"), where="D1_armO")
        print("D13_G3_DRYRUN_D1_ARMO %s"
              % json.dumps({"n_graded": g["n_graded"],
                            "worst_rel_err": g["worst_rel_err"],
                            "sign_flips": g["sign_flips"],
                            "verdict": g["verdict"]}, sort_keys=True))
        ok = ok and g["verdict"] == "PASS" and g["n_graded"] == 4
        print("D13_CONTROLS %s" % ("ALL PASS" if ok else "FAILED"))
        raise SystemExit(0 if ok else 2)
    if len(sys.argv) > 1 and sys.argv[1] == "starts":
        for k in START_IDS:
            sh, pv = start_vectors(k)
            print("S%d shape=%s patchV=%s"
                  % (k, json.dumps(sh), json.dumps(pv)))
        raise SystemExit(0)
    print("usage: d13_basin.py {bands|starts|controls <workdir>}")
    raise SystemExit(1)
