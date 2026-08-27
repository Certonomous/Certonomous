#!/usr/bin/env python3
"""Curriculum AV1R COMPARATOR -- NACA0012 INCOMPRESSIBLE (DASimpleFoam) baseline gradient at
np = 1 / 2 / 4 (scotch), TWO ROWS (SHIPPED + PATCHED): the family's first np-INVARIANCE
rung, graded on the band ADJOINT_VERIFICATION_STANDARD.md section 3 derives.  FROZEN by
md5 in PREREGISTRATION.md section 7 before any container starts.  Computes nothing about
physics; renders verdicts from the FIXED vocabulary only (PASS / GATE REACHED / GATE FAIL /
NOT A RESULT / BLOCKED / PENDING).  DERIVED from curriculum_D15/d15_grade.py (8fc2bdeb,
md5 b429ec89e7a738647081783b8b755711): the ledger regex, L-342 field classes, arm-kind-
aware completion, inspect-record fallback, G9/G10/G12 and the selftest shape are D15's;
the bright line G5 (FD) is REPLACED by G-NP (np-invariance), av1r_grade_DELTAS_from_d15.diff.

WHAT IT GRADES (PREREGISTRATION.md section 3):
  G1   completion, ARM-KIND AWARE: every arm needs kernel rc == 0 (docker inspect, and the
       harness rc must agree), OOMKilled false, and the AGE GUARD on its registered artefact
       (strictly newer than the arm's own datum).  SOLVER arms (X*-*) also need the
       instrument's TERMINAL MARKER (AV1R_X_WRITTEN) and its planted-control line
       (AV1R_PLANTED_CONTROL_SEEN) in the arm log; the SCRIPT arm MESH needs `Mesh OK.`.
       Any clause fails -> REFUSE (NOT A RESULT).  An arm with no ledger row is read from
       the launcher's surviving `<ARM>_<stamp>.inspect.txt` (L-342).
  G-M2 mesh identity: cells == 4,032 (A1's mesh) -> PASS else GATE FAIL.
  G-NP per ROW, the bright line: with the np = 1 arm as the SERIAL REFERENCE and for each
       np in {2, 4}: (a) objective spread s_J = |J(np) - J(1)| / |J(1)| <= 2.2e-5 for CD
       and for CL; (b) gradient spread s_g = ||g(np) - g(1)|| / ||g(1)|| <= 1.0e-3 for the
       CD gradient (shape + patchV concatenated) and for the CL gradient; (c) per-component
       sign agreement, 0 flips, on components with |g_1,i| >= 1e-14 (smaller ones NAMED and
       skipped).  Any (a)/(b)/(c) outside -> the row is GATE FAIL with the np and the
       quantity named.  The np = 4 partition record (per-processor cell counts) must sum to
       the mesh's cell count and carry exactly np entries, else the arm is NOT A RESULT.
       Bands: ADJOINT_VERIFICATION_STANDARD.md section 3 (objective 2.2e-5 from
       PARALLEL_GATE_DOCTRINE.md:38,:194-198; gradient 1e-3 = 6x B3's measured 1.1-1.7e-4
       floor, 50x below band D; sign rule VERIFICATION_CHARTER.md:845).
  G9   toolchain per row: the ledger DIGEST, the container's `D4S_IDWARP_SO_MD5:` print
       and the artefact's in-process libidwarp.so md5 must all name the row's toolchain.
  G10  caps: every arm core_min <= its registered cap and the sum <= the ceiling (95.0).
  G12  placement: cpuset == the registered one PER ARM (0,1 at np <= 2; 0,1,12,15 at
       np = 4); delivered cores >= 0.75 x ranks where MEASURED, NOT_MEASURED otherwise.
  DIVERGENCE shipped-vs-patched on the np = 1 CD gradient is REPORTED per component.

PLANTED CONTROLS (rule 3): (i) the instrument's AV1R_PLANTED_CONTROL_SEEN line is required
in every X log (the instrument refused otherwise); (ii) this grader writes a copy of the
np = 2 SHIPPED artefact with PLANT added to every total into <root>/grader_controls/,
re-reads it through the same reader and REFUSES unless every value moved by exactly PLANT;
(iii) a copy of the np = 4 SHIPPED artefact with every total SIGN-FLIPPED is graded
through the same G-NP function and MUST read GATE FAIL with flips == n_components, else
REFUSE (a spread reader not shown able to see a wrong gradient is not a reader).

L-342 (Sanaa, d4d0c29d): FIELDS_PHYSICS absent -> REFUSE; FIELDS_INFRASTRUCTURE absent ->
NOT_MEASURED, disclosed beside the verdict, never composed to PASS; present-but-garbage ->
REFUSE.  L-332: NO `assert` anywhere; the module counts ast.Assert nodes in its own source
and refuses on any.  No unconditional success print.
"""
import ast
import glob
import json
import math
import os
import re
import sys
import time

# ---- REGISTERED CONSTANTS (PREREGISTRATION.md; the document governs) ----------------
ITEM = "AV1R"
BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-AV1R-a1-naca0012-npinv"
ARMS_REQUIRED = ["MESH", "X1-S", "X2-S", "X4-S", "X1-P", "X2-P", "X4-P"]
ARM_KIND = {"MESH": "SCRIPT", "X1-S": "SOLVER", "X2-S": "SOLVER", "X4-S": "SOLVER",
            "X1-P": "SOLVER", "X2-P": "SOLVER", "X4-P": "SOLVER"}
ARM_ROW = {"MESH": "SHIPPED", "X1-S": "SHIPPED", "X2-S": "SHIPPED", "X4-S": "SHIPPED",
           "X1-P": "PATCHED", "X2-P": "PATCHED", "X4-P": "PATCHED"}
ARM_RANKS = {"MESH": 1, "X1-S": 1, "X2-S": 2, "X4-S": 4, "X1-P": 1, "X2-P": 2, "X4-P": 4}
ARTEFACT = {a: ("checkMesh.log" if a == "MESH" else "av1r_X.json") for a in ARMS_REQUIRED}
TERMINAL = {a: "AV1R_X_WRITTEN" for a in ARMS_REQUIRED if a != "MESH"}
CONTROL_LINE = "AV1R_PLANTED_CONTROL_SEEN"
# --- SUCCESSOR DELTA (AV1R): the age-guard datum is resolved BY EXISTENCE, not by name ---
# AV-1 and AV-2 both REFUSED at G1 with `age_reference_absent` on "0/U".  The cause was not
# physics: the NACA0012 incompressible tutorial runs `writeCompression on`, so a SERIAL
# solver arm rewrites time 0 back to disk COMPRESSED and "0/U" becomes "0/U.gz".  Measured
# on both refused run roots, every affected arm's artefact was strictly NEWER than the
# recorded datum -- the age guard's SUBSTANCE held on every arm.  Only the PATH vanished.
# Parallel arms are untouched (they write under processor*/), which is why AV-1 refused at
# its first np=1 arm while its np=2 and np=4 arms carried "0/U" with mtime == datum.
# The successor therefore registers a candidate SET and resolves it BY EXISTENCE; a
# hard-coded second name would reproduce this defect at the next compression change.
DATUM_REF_CANDIDATES = {a: (("0.orig/U", "0.orig/U.gz") if a == "MESH" else ("0/U", "0/U.gz"))
                        for a in ARMS_REQUIRED}
DATUM_REF = {a: DATUM_REF_CANDIDATES[a][0] for a in ARMS_REQUIRED}   # uncompressed name; the fixture's default
DATUM_SELF_TOL_S = 5         # the launcher writes the datum file one `stat` after the touch;
                             # measured delta on 10 of 10 arms across AV-1 and AV-2: 0 s
DATUM_RESOLVED = {}          # RECORDED per arm, never gated on the name
CAPS = {"MESH": 5.0, "X1-S": 10.0, "X2-S": 15.0, "X4-S": 20.0, "X1-P": 10.0, "X2-P": 15.0, "X4-P": 20.0}
ITEM_CEILING_CORE_MIN = 95.0
PREDICTED_CORE_MIN = {"MESH": 0.3, "X1-S": 2.5, "X2-S": 3.0, "X4-S": 4.0, "X1-P": 2.5, "X2-P": 3.0, "X4-P": 4.0}
CELLS_EXPECTED = 4032
OBJ_BAND = 2.2e-5            # objective spread across np, relative (PARALLEL_GATE_DOCTRINE.md:38)
GRAD_BAND = 1.0e-3           # gradient vector-relative spread vs the serial reference (standard sec.3)
SIGN_FLOOR = 1.0e-14
PLANT = 1.234e-03
IMG_DIGEST = {"SHIPPED": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc",
              "PATCHED": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"}
SO_MD5 = {"SHIPPED": "f0fcb488e0e98156575cd19548e91663", "PATCHED": "85f59e87253e0a71a813f64ca6e4c425"}
CPUSET_REGISTERED = {"MESH": "0,1", "X1-S": "0,1", "X2-S": "0,1", "X4-S": "0,1,12,15",
                     "X1-P": "0,1", "X2-P": "0,1", "X4-P": "0,1,12,15"}
DELIVERED_FRACTION = 0.75
PRED = {"P4_cost_ratio_band": (1.0, 3.0), "P5_core_min_band": (10.0, 50.0), "P6_mesh_wall_s_max": 120.0}
FIELDS_PHYSICS = ("rc", "inspect_exit", "oomkilled", "terminal_statement", "age_guard",
                  "core_min", "cap_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("memavail_pre_GiB", "memavail_post_GiB", "delivered", "siblings_pre",
                         "siblings_post", "log", "wall_s")
NOT_MEASURED = "NOT_MEASURED"
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
EXPECTED_UNITS = 31


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


# ================= LEDGER (physics vs infrastructure, L-342) -- D5/D15's regex ========
LEDGER_RE = re.compile(
    r"ARM=(?P<ARM>\S+)\s+ROW=(?P<ROW>\S+)\s+IMG=(?P<IMG>\S+)\s+"
    r"DIGEST=(?P<DIGEST>\S+)\s+rc=(?P<rc>-?\d+)\s+wall_s=(?P<wall_s>\d+)\s+"
    r"ranks=(?P<ranks>\d+)\s+core_min=(?P<core_min>[\d.]+)\s+"
    r"cap_core_min=(?P<cap>[\d.]+)\s+enforced_wall_s=(?P<ewall>\d+)\s+"
    r"enforced_core_min=(?P<ecore>[\d.]+)\s+memory=(?P<mem>\S+)\s+"
    r"inspect\(exit,oomkilled\)=\[(?P<inspect>[^\]]*)\]"
    r"(?:\s+memavail_pre_GiB=(?P<mempre>[\d.]+|NOT_MEASURED))?"
    r"(?:\s+memavail_post_GiB=(?P<mempost>[\d.]+|NOT_MEASURED))?"
    r"\s+cpuset=(?P<cpuset>\S+)"
    r"(?:\s+delivered_cores_mean=\[(?P<delivered>[^\]]*)\])?"
    r"(?:\s+siblings_pre=\[(?P<sibpre>[^\]]*)\])?"
    r"(?:\s+siblings_post=\[(?P<sibpost>[^\]]*)\])?"
    r"(?:\s+log=(?P<log>\S+))?")


def _infra_float(v):
    if v is None or v == NOT_MEASURED:
        return None
    return float(v)


def read_ledger(path):
    if not os.path.isfile(path):
        refuse("ledger", {"absent": path})
    rows = {}
    for line in open(path, errors="replace"):
        if not line.startswith("ARM="):
            continue
        m = LEDGER_RE.search(line)
        if not m:
            refuse("ledger", {"row_unparseable": line.strip()[:300],
                              "note": "PRESENT-BUT-GARBAGE row: refused, never skipped"})
        g = m.groupdict()
        parts = g["inspect"].split()
        infra_nm = [k for k, v in (("memavail_pre_GiB", g["mempre"]), ("memavail_post_GiB", g["mempost"]),
                                   ("delivered", g["delivered"]), ("siblings_pre", g["sibpre"]),
                                   ("siblings_post", g["sibpost"]), ("log", g["log"]))
                    if v is None or NOT_MEASURED in str(v)]
        row = {"ARM": g["ARM"], "ROW": g["ROW"], "IMG": g["IMG"], "DIGEST": g["DIGEST"],
               "rc": int(g["rc"]), "wall_s": int(g["wall_s"]), "ranks": int(g["ranks"]),
               "core_min": float(g["core_min"]), "cap_core_min": float(g["cap"]),
               "enforced_core_min": float(g["ecore"]), "memory": g["mem"],
               "inspect_exit": (parts[0] if parts else None),
               "oomkilled": (parts[1] if len(parts) > 1 else None),
               "memavail_pre_GiB": _infra_float(g["mempre"]), "memavail_post_GiB": _infra_float(g["mempost"]),
               "cpuset": g["cpuset"], "delivered": g["delivered"], "siblings_pre": g["sibpre"],
               "siblings_post": g["sibpost"], "log": g["log"], "source": "ledger_row",
               "field_sources": {"all": "ledger_row"}, "infra_not_measured": infra_nm}
        if row["ARM"] in rows:
            refuse("ledger", {"duplicate_arm_row": row["ARM"], "note": "two records for one run is the defect"})
        rows[row["ARM"]] = row
    return rows


def inspect_file_fallback(base, arm):
    cands = sorted(glob.glob(os.path.join(base, "%s_*.inspect.txt" % arm)))
    if len(cands) != 1:
        refuse("G1", {"arm_absent_from_ledger": arm, "inspect_record_candidates": cands,
                      "note": "exactly one surviving inspect record may stand in for a missing row"})
    parts = open(cands[0]).read().split()
    if len(parts) < 5:
        refuse("G1", {"inspect_record_unparseable": cands[0], "content": parts})
    logs = sorted(glob.glob(os.path.join(base, "%s_*.log" % arm)))
    try:
        rc = int(parts[0])
    except ValueError:
        refuse("G1", {"inspect_record_exit_unparseable": parts[0]})
    return {"ARM": arm, "ROW": ARM_ROW[arm], "IMG": None, "DIGEST": (parts[6] if len(parts) > 6 else None), "rc": rc, "wall_s": None,
            "ranks": ARM_RANKS[arm], "core_min": None, "cap_core_min": CAPS[arm],
            "enforced_core_min": CAPS[arm], "memory": parts[5] if len(parts) > 5 else None,
            "inspect_exit": parts[0], "oomkilled": parts[1].lower(), "memavail_pre_GiB": None,
            "memavail_post_GiB": None, "cpuset": parts[4], "delivered": NOT_MEASURED,
            "siblings_pre": NOT_MEASURED, "siblings_post": NOT_MEASURED,
            "log": (os.path.basename(logs[-1]) if logs else None), "source": "inspect_record",
            "field_sources": {"rc": "inspect.txt .State.ExitCode", "oomkilled": "inspect.txt .State.OOMKilled",
                              "cpuset": "inspect.txt HostConfig.CpusetCpus", "DIGEST": "inspect.txt 7th field (launcher's GOT_DIGEST)"},
            "infra_not_measured": list(FIELDS_INFRASTRUCTURE) + ["core_min"]}


# ================= G1: COMPLETION, ARM-KIND AWARE =====================================
def resolve_datum_ref(d, arm):
    """Resolve the age-guard reference BY EXISTENCE over the registered candidate set.

    Returns (path, name).  REFUSES when NO candidate exists -- that refusal is the driven
    control, and the selftest drives it -- and when MORE THAN ONE exists, because two files
    carry two mtimes and no registered rule says which one dates the run.
    """
    found = [(c, os.path.join(d, c)) for c in DATUM_REF_CANDIDATES[arm]
             if os.path.isfile(os.path.join(d, c))]
    if not found:
        refuse("G1", {"age_reference_absent": [os.path.join(d, c) for c in DATUM_REF_CANDIDATES[arm]],
                      "arm": arm,
                      "note": "no registered candidate exists; the guard fires (driven control)"})
    if len(found) > 1:
        refuse("G1", {"age_reference_ambiguous": [p for _c, p in found], "arm": arm,
                      "note": "two candidates, two mtimes, and no rule says which dates the run"})
    return found[0][1], found[0][0]


def read_write_compression(d):
    """Read `writeCompression` from the ARM'S OWN system/controlDict and RECORD it.

    Recorded, NEVER gated.  It is the setting that decides which candidate name the solver
    leaves behind, and a record that does not carry it cannot explain its own datum.
    Absent or unparseable -> NOT_MEASURED (an infrastructure field, L-342), never a refusal.
    """
    p = os.path.join(d, "system", "controlDict")
    if not os.path.isfile(p):
        return NOT_MEASURED
    try:
        for line in open(p, errors="replace"):
            s = line.strip()
            if s.startswith("writeCompression"):
                return s.rstrip(";").split()[-1]
    except OSError:
        return NOT_MEASURED
    return NOT_MEASURED


def arm_datum(base, arm):
    d = os.path.join(base, arm)
    p = os.path.join(d, ".av1r_age_datum")
    if not os.path.isfile(p):
        refuse("G1", {"age_datum_absent": p, "arm": arm})
    datum = int(open(p).read().strip())
    # The datum FILE is written by the launcher one `stat` after the touch and no solver in
    # this ladder writes it.  Its own mtime must therefore date its own recorded epoch: this
    # is what the old `mtime(0/U) == datum` clause was really protecting, moved onto a file
    # the solver cannot legitimately rewrite.
    self_mtime = int(os.path.getmtime(p))
    if abs(self_mtime - datum) > DATUM_SELF_TOL_S:
        refuse("G1", {"age_datum_self_inconsistent": p, "recorded": datum, "own_mtime": self_mtime,
                      "tol_s": DATUM_SELF_TOL_S,
                      "note": "the recorded epoch was not written by the launcher that staged this arm"})
    ref, refname = resolve_datum_ref(d, arm)
    ref_mtime = int(os.path.getmtime(ref))
    if ref_mtime < datum:
        refuse("G1", {"age_reference_older_than_datum": ref, "recorded": datum, "on_disk": ref_mtime,
                      "note": "a staged field cannot predate the stage that touched it"})
    DATUM_RESOLVED[arm] = {"datum_file": p, "recorded_epoch": datum, "datum_file_mtime": self_mtime,
                           "reference_name": refname, "reference_path": ref, "reference_mtime": ref_mtime,
                           "candidates": list(DATUM_REF_CANDIDATES[arm]),
                           "resolved_by": "EXISTENCE over the registered candidate set, never by name",
                           "writeCompression": read_write_compression(d)}
    return d, datum


def g_completion(base, rows):
    DATUM_RESOLVED.clear()
    out = {"arms": {}, "not_measured": {}}
    for arm in ARMS_REQUIRED:
        r = rows.get(arm)
        if r is None:
            r = inspect_file_fallback(base, arm)
            rows[arm] = r
        ke = r.get("inspect_exit")
        if ke is None:
            refuse("G1", {"kernel_exit_absent": arm, "note": "inspect(exit,oomkilled) is a PHYSICS field"})
        try:
            kernel_rc = int(ke)
        except (TypeError, ValueError):
            refuse("G1", {"kernel_exit_unparseable": arm, "value": ke})
        if kernel_rc != r["rc"]:
            refuse("G1", {"rc_disagreement": arm, "kernel": kernel_rc, "harness": r["rc"]})
        oom = str(r.get("oomkilled")).lower()
        if oom not in ("false", "true"):
            refuse("G1", {"oomkilled_unparseable": arm, "value": r.get("oomkilled")})
        if kernel_rc != 0 or oom != "false":
            refuse("G1", {"arm": arm, "kernel_rc": kernel_rc, "oomkilled": oom,
                          "note": "a run that fails any clause is not done (rule 4)"})
        adir, datum = arm_datum(base, arm)
        art = os.path.join(adir, ARTEFACT[arm])
        if not os.path.isfile(art):
            refuse("G1", {"artefact_absent": art, "arm": arm})
        if os.path.getmtime(art) <= datum:
            refuse("G1", {"artefact_not_newer_than_datum": art, "arm": arm, "datum": datum,
                          "artefact_mtime": os.path.getmtime(art), "note": "age guard, rule 4"})
        kind = ARM_KIND[arm]
        if kind == "SOLVER":
            logname = r.get("log")
            logpath = os.path.join(base, logname) if logname else None
            if not logpath or not os.path.isfile(logpath):
                refuse("G1", {"log_absent": logname, "arm": arm, "note": "a missing log is a FAILED clause"})
            text = open(logpath, errors="replace").read()
            if TERMINAL[arm] not in text:
                refuse("G1", {"terminal_marker_absent": TERMINAL[arm], "arm": arm, "log": logname})
            if CONTROL_LINE not in text:
                refuse("CONTROL", {"instrument_planted_control_line_absent": CONTROL_LINE, "arm": arm, "log": logname})
            r["log_text"] = text
        else:
            text = open(art, errors="replace").read()
            if not re.search(r"^Mesh OK\.$", text, re.M):
                refuse("G1", {"mesh_ok_absent": art, "arm": arm})
            r["log_text"] = open(os.path.join(base, r["log"]), errors="replace").read() if r.get("log") and os.path.isfile(os.path.join(base, r["log"])) else ""
        out["arms"][arm] = {"kind": kind, "kernel_rc": kernel_rc, "oomkilled": oom, "artefact": ARTEFACT[arm],
                            "source": r["source"], "field_sources": r["field_sources"]}
        if r.get("infra_not_measured"):
            out["not_measured"][arm] = r["infra_not_measured"]
    return out


# ================= readers with planted controls ======================================
def read_X(path):
    j = json.load(open(path))
    adj = {}
    for of in ("CD", "CL"):
        adj[of] = {dv: [float(v) for v in j["adjoint"][of][dv]] for dv in ("shape", "patchV")}
    return {"CD": float(j["CD_baseline"]), "CL": float(j["CL_baseline"]), "adjoint": adj,
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"), "nprocs": j.get("nprocs"),
            "partition": j.get("partition")}


def flat(X, of):
    return list(X["adjoint"][of]["shape"]) + list(X["adjoint"][of]["patchV"])


def grader_plant_control(base, xpath, tag):
    j = json.load(open(xpath))
    for of in ("CD", "CL"):
        for dv in ("shape", "patchV"):
            j["adjoint"][of][dv] = [repr(float(v) + PLANT) for v in j["adjoint"][of][dv]]
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "X_%s_planted.json" % tag)
    json.dump(j, open(cp, "w"), indent=1, sort_keys=True)
    a, b = read_X(xpath), read_X(cp)
    worst, n = 0.0, 0
    for of in ("CD", "CL"):
        for x, y in zip(flat(a, of), flat(b, of)):
            worst = max(worst, abs((y - x) - PLANT))
            n += 1
    if n == 0 or worst > 1e-12:
        refuse("CONTROL", {"grader_plant_not_seen": {"n_values": n, "worst_residual": worst, "plant": PLANT}})
    return {"grader_plant_seen": True, "n_values": n, "worst_residual": worst, "file": cp}


def sign_flipped_copy(X):
    Y = json.loads(json.dumps(X))
    for of in ("CD", "CL"):
        for dv in ("shape", "patchV"):
            Y["adjoint"][of][dv] = [-v for v in Y["adjoint"][of][dv]]
    return Y


# ================= G-NP: the bright line, per row =====================================
def compare_np(Xref, Xnp, np_):
    out = {"np": np_, "objective": {}, "gradient": {}, "verdict": "PASS", "reasons": []}
    for of in ("CD", "CL"):
        jr, jn = Xref[of], Xnp[of]
        if abs(jr) < SIGN_FLOOR:
            refuse("G-NP", {"reference_objective_zero": of, "note": "no relative spread against zero"})
        sj = abs(jn - jr) / abs(jr)
        out["objective"][of] = {"J_ref": jr, "J_np": jn, "spread_rel": sj, "band": OBJ_BAND,
                                "verdict": "PASS" if sj <= OBJ_BAND else "GATE FAIL"}
        if sj > OBJ_BAND:
            out["verdict"] = "GATE FAIL"; out["reasons"].append("objective %s spread %.3e > %.1e" % (of, sj, OBJ_BAND))
        gr, gn = flat(Xref, of), flat(Xnp, of)
        if len(gr) != len(gn) or len(gr) == 0:
            refuse("G-NP", {"gradient_length_mismatch": of, "ref": len(gr), "np": len(gn)})
        num = math.sqrt(sum((a - b) ** 2 for a, b in zip(gr, gn)))
        den = math.sqrt(sum(a ** 2 for a in gr))
        if den < SIGN_FLOOR:
            refuse("G-NP", {"reference_gradient_norm_zero": of})
        sg = num / den
        flips, skipped = [], []
        for i, (a, b) in enumerate(zip(gr, gn)):
            if abs(a) < SIGN_FLOOR:
                skipped.append(i)
            elif a * b < 0.0:
                flips.append(i)
        out["gradient"][of] = {"spread_rel": sg, "band": GRAD_BAND, "n_components": len(gr),
                               "sign_flips": flips, "n_flips": len(flips), "skipped_near_zero": skipped,
                               "verdict": "PASS" if (sg <= GRAD_BAND and not flips) else "GATE FAIL"}
        if sg > GRAD_BAND:
            out["verdict"] = "GATE FAIL"; out["reasons"].append("gradient %s spread %.3e > %.1e" % (of, sg, GRAD_BAND))
        if flips:
            out["verdict"] = "GATE FAIL"; out["reasons"].append("gradient %s sign flips %s" % (of, flips))
    return out


def partition_check(X, np_, cells):
    part = X.get("partition")
    if np_ == 1:
        if part not in ([], None):
            refuse("G-NP", {"np1_partition_record_not_empty": part})
        return {"np": 1, "record": [], "ok": True}
    if not isinstance(part, list) or len(part) != np_:
        refuse("G-NP", {"partition_record_count": (len(part) if isinstance(part, list) else None), "np": np_,
                        "note": "a parallel gradient names its decomposition (DAFOAM_CHARTER sec.5)"})
    ns = [p.get("nCells") for p in part]
    if any(n is None for n in ns) or sum(ns) != cells:
        refuse("G-NP", {"partition_cells": ns, "sum": (sum(n for n in ns if n is not None)), "mesh_cells": cells})
    return {"np": np_, "record": ns, "sum": sum(ns), "ok": True}


# ================= G9 / G10 / G12 ======================================================
def g_toolchain(rows):
    out = {"per_arm": {}, "verdict": "PASS"}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        row = ARM_ROW[arm]
        m = re.search(r"D4S_IDWARP_SO_MD5:\s*([0-9a-f]{32})", r.get("log_text", ""))
        printed = m.group(1) if m else None
        ok = (r.get("DIGEST") == IMG_DIGEST[row]) and (printed == SO_MD5[row])
        art_md5 = r.get("artefact_so_md5")
        if arm != "MESH":
            ok = ok and (art_md5 == SO_MD5[row])
        out["per_arm"][arm] = {"row": row, "digest": r.get("DIGEST"), "printed_so_md5": printed,
                               "artefact_so_md5": art_md5, "ok": bool(ok)}
        if not ok:
            out["verdict"] = "GATE FAIL"
    return out


def g_caps(rows):
    out = {"per_arm": {}, "verdict": "PASS", "total_core_min": 0.0, "ceiling": ITEM_CEILING_CORE_MIN, "not_measured": []}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        cm = r.get("core_min")
        if cm is None:
            out["not_measured"].append(arm)
            out["per_arm"][arm] = {"core_min": NOT_MEASURED, "cap": CAPS[arm]}
            continue
        out["total_core_min"] += cm
        crossed = cm > CAPS[arm]
        out["per_arm"][arm] = {"core_min": cm, "cap": CAPS[arm], "crossed": crossed,
                               "ratio_actual_over_predicted": round(cm / PREDICTED_CORE_MIN[arm], 4)}
        if crossed:
            out["verdict"] = "GATE FAIL"
    if out["total_core_min"] > ITEM_CEILING_CORE_MIN:
        out["verdict"] = "GATE FAIL"
    return out


def g_placement(rows):
    out = {"per_arm": {}, "verdict": "PASS", "not_measured": []}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        cs_ok = r.get("cpuset") == CPUSET_REGISTERED[arm]
        d = r.get("delivered")
        dl = None
        m = re.match(r"\s*([\d.]+)\s+n=(\d+)", d or "")
        if m:
            dl = float(m.group(1))
        if dl is None:
            out["not_measured"].append(arm)
        dl_ok = True if (dl is None or ARM_RANKS[arm] == 1) else dl >= DELIVERED_FRACTION * ARM_RANKS[arm]
        out["per_arm"][arm] = {"cpuset": r.get("cpuset"), "registered": CPUSET_REGISTERED[arm],
                               "delivered_cores_mean": (dl if dl is not None else NOT_MEASURED)}
        if not (cs_ok and dl_ok):
            out["verdict"] = "GATE FAIL"
    return out


# ================= the grade ==========================================================
def grade(root):
    rows = read_ledger(os.path.join(root, "ledger.txt"))
    g1 = g_completion(root, rows)
    cm_txt = open(os.path.join(root, "MESH", "checkMesh.log"), errors="replace").read()
    m = re.search(r"^\s*cells:\s+(\d+)", cm_txt, re.M)
    if not m:
        refuse("G-M2", {"cells_absent_in_checkMesh": True})
    cells = int(m.group(1))
    gm2 = "PASS" if cells == CELLS_EXPECTED else "GATE FAIL"
    X = {}
    for arm in ARMS_REQUIRED:
        if arm == "MESH":
            continue
        X[arm] = read_X(os.path.join(root, arm, "av1r_X.json"))
        rows[arm]["artefact_so_md5"] = X[arm]["so_md5"]
        if X[arm]["nprocs"] != ARM_RANKS[arm]:
            refuse("G-NP", {"artefact_nprocs": X[arm]["nprocs"], "registered_ranks": ARM_RANKS[arm], "arm": arm})
    controls = {"grader_plant_X2S": grader_plant_control(root, os.path.join(root, "X2-S", "av1r_X.json"), "X2S")}
    wrong = compare_np(X["X1-S"], sign_flipped_copy(X["X4-S"]), 4)
    nflip = wrong["gradient"]["CD"]["n_flips"] + wrong["gradient"]["CL"]["n_flips"]
    nexp = (wrong["gradient"]["CD"]["n_components"] - len(wrong["gradient"]["CD"]["skipped_near_zero"])
            + wrong["gradient"]["CL"]["n_components"] - len(wrong["gradient"]["CL"]["skipped_near_zero"]))
    if wrong["verdict"] != "GATE FAIL" or nflip != nexp:
        refuse("CONTROL", {"sign_flipped_copy_not_read_as_wrong": {"verdict": wrong["verdict"], "flips": nflip, "expected": nexp}})
    controls["sign_flipped_X4S_read_as_GATE_FAIL"] = {"seen": True, "flips": nflip, "expected": nexp}
    gnp = {}
    for rk, ref, arms in (("S", "X1-S", (("X2-S", 2), ("X4-S", 4))), ("P", "X1-P", (("X2-P", 2), ("X4-P", 4)))):
        per = {}
        parts = {"1": partition_check(X[ref], 1, cells)}
        for arm, np_ in arms:
            parts[str(np_)] = partition_check(X[arm], np_, cells)
            per[str(np_)] = compare_np(X[ref], X[arm], np_)
        rowv = "GATE FAIL" if any(v["verdict"] == "GATE FAIL" for v in per.values()) else "PASS"
        gnp[rk] = {"reference_arm": ref, "per_np": per, "partitions": parts, "row_verdict": rowv,
                   "CD_serial": X[ref]["CD"], "CL_serial": X[ref]["CL"]}
    div = []
    a, b = X["X1-S"], X["X1-P"]
    for dv in ("shape", "patchV"):
        for i, (u, v) in enumerate(zip(a["adjoint"]["CD"][dv], b["adjoint"]["CD"][dv])):
            den = max(abs(u), abs(v), 1e-300)
            div.append({"dv": dv, "idx": i, "J_shipped": u, "J_patched": v, "divergence_pct": abs(u - v) / den * 100.0})
    g9, g10, g12 = g_toolchain(rows), g_caps(rows), g_placement(rows)
    # ---- predictions, scored never adjusted
    preds = {"P1_patched_row_np_invariance_PASS": "HIT" if gnp["P"]["row_verdict"] == "PASS" else "MISS",
             "P2_shipped_row_np_invariance_PASS": "HIT" if gnp["S"]["row_verdict"] == "PASS" else "MISS"}
    spreads = [gnp[rk]["per_np"][k]["objective"][of]["spread_rel"] for rk in ("S", "P") for k in ("2", "4") for of in ("CD", "CL")]
    mx = max(spreads)
    preds["P3_objective_not_bit_identical_but_inside_band"] = "HIT" if (0.0 < mx <= OBJ_BAND) else "MISS"
    preds["P3_max_objective_spread_rel"] = mx
    c1, c4 = rows["X1-S"].get("core_min"), rows["X4-S"].get("core_min")
    if c1 is None or c4 is None or c1 <= 0:
        preds["P4_cost_ratio_np4_over_np1_shipped"] = NOT_MEASURED
    else:
        ratio = c4 / c1
        preds["P4_cost_ratio_np4_over_np1_shipped"] = "HIT" if PRED["P4_cost_ratio_band"][0] <= ratio <= PRED["P4_cost_ratio_band"][1] else "MISS"
        preds["P4_ratio_value"] = ratio
    tot = g10["total_core_min"]
    preds["P5_total_core_min_band"] = NOT_MEASURED if g10["not_measured"] else ("HIT" if PRED["P5_core_min_band"][0] <= tot <= PRED["P5_core_min_band"][1] else "MISS")
    mw = rows["MESH"].get("wall_s")
    preds["P6_mesh_wall_le_120s"] = NOT_MEASURED if mw is None else ("HIT" if mw <= PRED["P6_mesh_wall_s_max"] else "MISS")
    preds["P7_cells_4032"] = "HIT" if gm2 == "PASS" else "MISS"
    if "GATE FAIL" in (gnp["S"]["row_verdict"], gnp["P"]["row_verdict"], gm2, g9["verdict"], g10["verdict"], g12["verdict"]):
        verdict = "GATE FAIL"
    else:
        verdict = "PASS"
    if verdict not in VOCAB:
        refuse("VOCAB", {"verdict": verdict})
    return {"item": "CURRICULUM-%s" % ITEM, "verdict": verdict,
            "rows": {"SHIPPED": gnp["S"]["row_verdict"], "PATCHED": gnp["P"]["row_verdict"]},
            "gates": {"G1_completion": "PASS", "G-M2_mesh_identity": gm2, "G-NP_SHIPPED": gnp["S"], "G-NP_PATCHED": gnp["P"],
                      "G9_toolchain": g9, "G10_caps": g10, "G12_placement": g12},
            "bands": {"objective_spread_rel": OBJ_BAND, "gradient_spread_rel": GRAD_BAND, "sign_flips": 0,
                      "provenance": "ADJOINT_VERIFICATION_STANDARD.md sec.3; PARALLEL_GATE_DOCTRINE.md:38; B3 bb5088c4:16-25; VERIFICATION_CHARTER.md:845"},
            "mesh_cells": cells, "divergence_shipped_vs_patched_np1_CD": div, "predictions": preds,
            "controls": controls, "completion": g1,
            "not_measured": {"G1": g1["not_measured"], "G10": g10["not_measured"], "G12": g12["not_measured"]},
            "datum_resolution": dict(DATUM_RESOLVED),
            "field_classes": {"physics": list(FIELDS_PHYSICS), "infrastructure": list(FIELDS_INFRASTRUCTURE),
                              "rule": "absent infrastructure -> NOT_MEASURED beside the verdict; absent physics -> REFUSE (L-342)"},
            "no_gci": "no grid family; standing rule 5 has no row; NO GCI IS QUOTED",
            "no_fd": "this rung carries no FD table; it is an np-invariance check of the adjoint against itself (standard sec.3), and moves no capability-grid verdict on its own",
            "capability_grid_cell": "2D . steady . incompressible -- np-invariance evidence for the gradient column's 'what was checked'"}


# ================= selftest: planted fixtures, counted against a FROZEN unit count ======
ROWFMT = ("ARM={arm} ROW={row} IMG={img} DIGEST={dig} rc={rc} wall_s={wall} ranks={ranks} core_min={cm} "
          "cap_core_min={cap} enforced_wall_s=600 enforced_core_min={cap} memory=4g inspect(exit,oomkilled)=[{ke} {oom}] "
          "memavail_pre_GiB=20.00 memavail_post_GiB={mpost} cpuset={cs} delivered_cores_mean=[{dl}] "
          "siblings_pre=[] siblings_post=[] log={log} stamp=x\n")
J0 = {"shape": [-0.011, 0.02, -0.03, 0.041, 0.05, -0.06, 0.007, -0.008], "patchV": [0.0, 0.0123]}


def _fix(tmp, tweak=None):
    k = {"rc": {a: 0 for a in ARMS_REQUIRED}, "ke": {}, "oom": {a: "false" for a in ARMS_REQUIRED},
         "cm": dict(PREDICTED_CORE_MIN), "cs": dict(CPUSET_REGISTERED),
         "so": {a: SO_MD5[ARM_ROW[a]] for a in ARMS_REQUIRED}, "cells": CELLS_EXPECTED,
         "gpert": {a: 1.0e-4 for a in ARMS_REQUIRED}, "jpert": {a: 1.0e-7 for a in ARMS_REQUIRED},
         "flip": {a: set() for a in ARMS_REQUIRED}, "terminal": {a: True for a in ARMS_REQUIRED},
         "ctrl_line": {a: True for a in ARMS_REQUIRED}, "stale": set(), "mpost": "20.00",
         "drop_row": set(), "inspect_file": set(), "dl": {a: "%.2f n=10 max_nr_throttled=0" % (0.99 * ARM_RANKS[a]) for a in ARMS_REQUIRED},
         "nprocs": dict(ARM_RANKS), "part_cells": {}, "wall": {a: 60 for a in ARMS_REQUIRED}}
    k["gpert"]["X1-S"] = 0.0; k["gpert"]["X1-P"] = 0.0; k["jpert"]["X1-S"] = 0.0; k["jpert"]["X1-P"] = 0.0
    k.update({"datum_gz": set(), "datum_none": set(), "datum_both": set(), "datum_skew": 0,
              "ref_backdate": set(), "gz_skew": 50, "wc": "on"})
    if tweak:
        tweak(k)
    root = os.path.join(tmp, "root_%d" % int(time.time() * 1e6))
    os.makedirs(root)
    led = ["ITEM=AV1R\n", "STAGED stamp=x\n"]
    for arm in ARMS_REQUIRED:
        d = os.path.join(root, arm)
        os.makedirs(os.path.join(d, "0.orig" if arm == "MESH" else "0"))
        os.makedirs(os.path.join(d, "system"), exist_ok=True)
        open(os.path.join(d, "system", "controlDict"), "w").write(
            "writeControl    timeStep;\nwriteCompression %s;\n" % k["wc"])
        ref = os.path.join(d, DATUM_REF[arm])
        open(ref, "w").write("U\n")
        t0 = int(os.path.getmtime(ref))
        gz = ref + ".gz"
        if arm in k["datum_gz"] or arm in k["datum_both"]:
            open(gz, "w").write("U.gz\n")
            os.utime(gz, (t0 + k["gz_skew"], t0 + k["gz_skew"]))
        if arm in k["datum_gz"] or arm in k["datum_none"]:
            os.remove(ref)
        if arm in k["ref_backdate"]:
            for cand in (ref, gz):
                if os.path.isfile(cand):
                    os.utime(cand, (t0 - 60, t0 - 60))
        datfile = os.path.join(d, ".av1r_age_datum")
        open(datfile, "w").write("%d\n" % (t0 - k["datum_skew"]))
        os.utime(datfile, (t0, t0))
        log = "%s_x.log" % arm
        so = k["so"][arm]
        text = "D4S_CONTAINER_UID: 0\nD4S_IDWARP_SO_MD5: %s\nD4S_DEADLINE_IN_CONTAINER_S: 600\n" % so
        if arm == "MESH":
            art = os.path.join(d, "checkMesh.log")
            open(art, "w").write("Mesh stats\n    cells:            %d\n\nMesh OK.\n" % k["cells"])
        else:
            art = os.path.join(d, "av1r_X.json")
            ident = {"libidwarp_so_md5": so, "idwarp_file": "/x/idwarp/__init__.py"}
            gp = k["gpert"][arm]
            adj = {}
            for of, scale in (("CD", 1.0), ("CL", 10.0)):
                adj[of] = {}
                for dv in ("shape", "patchV"):
                    vals = []
                    for i, v in enumerate(J0[dv]):
                        x = v * scale * (1.0 + gp)
                        if (dv, i) in k["flip"][arm]:
                            x = -x
                        vals.append(repr(x))
                    adj[of][dv] = vals
            np_ = k["nprocs"][arm]
            if np_ == 1:
                part = []
            else:
                pc = k["part_cells"].get(arm)
                if pc is None:
                    base_n = k["cells"] // np_
                    pc = [base_n] * np_
                    pc[-1] += k["cells"] - sum(pc)
                part = [{"dir": "processor%d" % i, "nCells": n} for i, n in enumerate(pc)]
            json.dump({"item": "AV1R", "mode": "X", "identity": ident, "nprocs": np_,
                       "CD_baseline": repr(0.02 * (1.0 + k["jpert"][arm])), "CL_baseline": repr(0.5 * (1.0 + k["jpert"][arm])),
                       "adjoint": adj, "partition": part, "plant": PLANT}, open(art, "w"))
            if k["ctrl_line"][arm]:
                text += CONTROL_LINE + " n=20 worst_residual=0.0 plant=0.001234\n"
            if k["terminal"][arm]:
                text += TERMINAL[arm] + " ok\n"
        os.utime(art, (t0 - 5, t0 - 5) if arm in k["stale"] else (t0 + 5, t0 + 5))
        open(os.path.join(root, log), "w").write(text)
        ke = k["ke"].get(arm, k["rc"][arm])
        if arm in k["inspect_file"]:
            open(os.path.join(root, "%s_x.inspect.txt" % arm), "w").write("%d %s 2026-08-26T00:00:00Z 2026-08-26T00:01:00Z %s 4294967296 %s\n" % (ke, k["oom"][arm], k["cs"][arm], IMG_DIGEST[ARM_ROW[arm]]))
        if arm in k["drop_row"]:
            continue
        led.append(ROWFMT.format(arm=arm, row=ARM_ROW[arm], img="img", dig=IMG_DIGEST[ARM_ROW[arm]], rc=k["rc"][arm],
                                 wall=k["wall"][arm], ranks=ARM_RANKS[arm], cm=k["cm"][arm], cap=CAPS[arm], ke=ke, oom=k["oom"][arm],
                                 mpost=k["mpost"], cs=k["cs"][arm], dl=k["dl"][arm], log=log))
    open(os.path.join(root, "ledger.txt"), "w").write("".join(led))
    return root


def selftest(tmp):
    n = 0; fails = []

    def unit(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)
        print("  [%s] %s" % ("OK " if cond else "BAD", name))

    def refused(root):
        try:
            grade(root); return False
        except Refusal:
            return True

    def refused_at(root, key):
        try:
            grade(root)
        except Refusal as e:
            return key in str(e)
        return False

    def tw(**kw):
        def f(k):
            for key, val in kw.items():
                if isinstance(val, dict) and isinstance(k.get(key), dict):
                    k[key].update(val)
                else:
                    k[key] = val
        return f
    r = grade(_fix(tmp))
    unit("U1 clean fixture (spreads 1e-4 / 1e-7) -> item PASS, both rows PASS, G-M2/G9/G10/G12 PASS",
         r["verdict"] == "PASS" and r["rows"] == {"SHIPPED": "PASS", "PATCHED": "PASS"} and r["gates"]["G-M2_mesh_identity"] == "PASS"
         and r["gates"]["G9_toolchain"]["verdict"] == "PASS" and r["gates"]["G10_caps"]["verdict"] == "PASS" and r["gates"]["G12_placement"]["verdict"] == "PASS")
    unit("U2 clean fixture -> P1, P2, P3 (0 < spread <= 2.2e-5), P4 (ratio 1.6), P5, P6, P7 HIT",
         all(r["predictions"][x] == "HIT" for x in ("P1_patched_row_np_invariance_PASS", "P2_shipped_row_np_invariance_PASS",
                                                    "P3_objective_not_bit_identical_but_inside_band", "P4_cost_ratio_np4_over_np1_shipped",
                                                    "P5_total_core_min_band", "P6_mesh_wall_le_120s", "P7_cells_4032")))
    unit("U3 grader-level plant SEEN on X2-S; sign-flipped X4-S copy read as GATE FAIL with every component flipped (rule 3)",
         r["controls"]["grader_plant_X2S"]["grader_plant_seen"] and r["controls"]["sign_flipped_X4S_read_as_GATE_FAIL"]["seen"]
         and r["controls"]["sign_flipped_X4S_read_as_GATE_FAIL"]["flips"] == 18)
    r = grade(_fix(tmp, tw(gpert={"X4-S": 2.0e-3})))
    unit("U4 PLANTED gradient spread 2e-3 at np=4 SHIPPED -> G-NP SHIPPED GATE FAIL (np 4 named), PATCHED PASS, item GATE FAIL, P2 MISS",
         r["rows"]["SHIPPED"] == "GATE FAIL" and r["rows"]["PATCHED"] == "PASS" and r["verdict"] == "GATE FAIL"
         and r["gates"]["G-NP_SHIPPED"]["per_np"]["4"]["verdict"] == "GATE FAIL" and r["predictions"]["P2_shipped_row_np_invariance_PASS"] == "MISS")
    r = grade(_fix(tmp, tw(gpert={"X2-P": 9.0e-4})))
    unit("U5 gradient spread 9e-4 at np=2 PATCHED (inside 1e-3) -> PASS", r["rows"]["PATCHED"] == "PASS" and r["verdict"] == "PASS")
    r = grade(_fix(tmp, tw(jpert={"X2-P": 5.0e-5})))
    unit("U6 PLANTED objective spread 5e-5 at np=2 PATCHED -> objective GATE FAIL, row GATE FAIL, P1 MISS",
         r["gates"]["G-NP_PATCHED"]["per_np"]["2"]["objective"]["CD"]["verdict"] == "GATE FAIL" and r["rows"]["PATCHED"] == "GATE FAIL"
         and r["predictions"]["P1_patched_row_np_invariance_PASS"] == "MISS")
    r = grade(_fix(tmp, tw(flip={"X4-P": {("shape", 6)}})))
    unit("U7 PLANTED sign flip on shape[6] at np=4 PATCHED -> flip counted, row GATE FAIL",
         r["gates"]["G-NP_PATCHED"]["per_np"]["4"]["gradient"]["CD"]["n_flips"] == 1 and r["rows"]["PATCHED"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(jpert={"X2-S": 0.0, "X4-S": 0.0, "X2-P": 0.0, "X4-P": 0.0})))
    unit("U8 objectives BIT-IDENTICAL across np -> P3 MISS (the B3 G4 finding not reproduced), verdict still PASS",
         r["predictions"]["P3_objective_not_bit_identical_but_inside_band"] == "MISS" and r["verdict"] == "PASS")
    unit("U9 rc=1 on X4-P -> REFUSAL", refused(_fix(tmp, tw(rc={"X4-P": 1}, ke={"X4-P": 1}))))
    unit("U10 OOMKilled=true on X2-S -> REFUSAL", refused(_fix(tmp, tw(oom={"X2-S": "true"}))))
    unit("U11 terminal marker absent in X1-P log -> REFUSAL", refused(_fix(tmp, tw(terminal={"X1-P": False}))))
    unit("U12 instrument planted-control line absent in X4-S log -> REFUSAL", refused(_fix(tmp, tw(ctrl_line={"X4-S": False}))))
    unit("U13 artefact OLDER than the age datum (X1-S) -> REFUSAL (rule 4)", refused(_fix(tmp, tw(stale={"X1-S"}))))
    unit("U14 np=4 partition record with 3 entries -> REFUSAL", refused(_fix(tmp, tw(part_cells={"X4-S": [1344, 1344, 1344]}))))
    unit("U15 np=4 partition cells summing to 4033 -> REFUSAL", refused(_fix(tmp, tw(part_cells={"X4-P": [1008, 1008, 1008, 1009]}))))
    unit("U16 artefact nprocs 2 on the np=4 arm -> REFUSAL", refused(_fix(tmp, tw(nprocs={"X4-S": 2}))))
    r = grade(_fix(tmp, tw(so={"X2-P": SO_MD5["SHIPPED"]})))
    unit("U17 X2-P carrying the SHIPPED .so md5 -> G9 GATE FAIL, item GATE FAIL", r["gates"]["G9_toolchain"]["verdict"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(cm={"X4-S": 21.0})))
    unit("U18 X4-S core_min 21.0 > cap 20.0 -> G10 GATE FAIL", r["gates"]["G10_caps"]["verdict"] == "GATE FAIL" and r["gates"]["G10_caps"]["per_arm"]["X4-S"]["crossed"])
    r = grade(_fix(tmp, tw(cs={"X4-S": "0,1"})))
    unit("U19 X4-S on cpuset 0,1 (registered 0,1,12,15) -> G12 GATE FAIL", r["gates"]["G12_placement"]["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(cells=4033)))
    unit("U20 cells 4033 -> G-M2 GATE FAIL, P7 MISS (partition sums follow the fixture's cells)", r["gates"]["G-M2_mesh_identity"] == "GATE FAIL" and r["predictions"]["P7_cells_4032"] == "MISS")
    r = grade(_fix(tmp, tw(mpost="NOT_MEASURED", dl={a: "NOT_MEASURED" for a in ARMS_REQUIRED})))
    unit("U21 absent infrastructure fields -> verdict unchanged PASS, NOT_MEASURED named beside it (L-342)",
         r["verdict"] == "PASS" and r["not_measured"]["G1"].get("X1-S") and "X4-S" in r["not_measured"]["G12"])
    unit("U22 harness rc 0 vs kernel exit 1 disagreement -> REFUSAL", refused(_fix(tmp, tw(ke={"X2-P": 1}))))
    r = grade(_fix(tmp, tw(drop_row={"X4-P"}, inspect_file={"X4-P"})))
    unit("U23 ledger row absent, ONE inspect record -> read from it, source named, core_min NOT_MEASURED, verdict PASS",
         r["verdict"] == "PASS" and r["completion"]["arms"]["X4-P"]["source"] == "inspect_record" and "X4-P" in r["not_measured"]["G10"])
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(tmp, "planted_assert.py")
    open(p, "w").write("x = 1\nassert x == 1\n")
    unit("U24 ast.Assert count = 0 in av1r_grade.py and av1r_x.py, and the counter sees a planted assert (=1)",
         count_asserts(os.path.abspath(__file__)) == 0 and count_asserts(os.path.join(here, "av1r_x.py")) == 0 and count_asserts(p) == 1)
    # ---- SUCCESSOR DELTA: the datum resolved BY EXISTENCE, and the guard STILL ABLE TO FIRE
    solver_arms = [a for a in ARMS_REQUIRED if ARM_KIND[a] == "SOLVER"]
    r_gz = _fix(tmp, tw(datum_gz=set(solver_arms)))
    try:
        g_gz = grade(r_gz)
    except Refusal:
        g_gz = None
    unit("UD1 datum resolved BY EXISTENCE: every solver arm carrying ONLY 0/U.gz still grades "
         "(the exact shape that refused AV-1 and AV-2 is repaired)", g_gz is not None)
    unit("UD2 the resolution is RECORDED and names 0/U.gz on every solver arm, with its candidate set",
         g_gz is not None
         and all(g_gz["datum_resolution"][a]["reference_name"] == "0/U.gz" for a in solver_arms)
         and all(list(g_gz["datum_resolution"][a]["candidates"]) == ["0/U", "0/U.gz"] for a in solver_arms))
    unit("UD3 writeCompression is READ from the arm's own system/controlDict and recorded ('on'), never gated",
         g_gz is not None and all(g_gz["datum_resolution"][a]["writeCompression"] == "on" for a in ARMS_REQUIRED))
    unit("UD4 DRIVEN CONTROL -- with NEITHER candidate on disk the guard STILL REFUSES; a guard "
         "relaxed without a control showing it can fire is a guard retired, not repaired",
         refused_at(_fix(tmp, tw(datum_none=set(solver_arms))), "age_reference_absent"))
    unit("UD5 ambiguity REFUSES: 0/U and 0/U.gz both present is two mtimes and no registered rule",
         refused_at(_fix(tmp, tw(datum_both=set(solver_arms))), "age_reference_ambiguous"))
    unit("UD6 the datum file must date its own epoch: content back-dated 60 s against its own mtime REFUSES",
         refused_at(_fix(tmp, tw(datum_skew=60)), "age_datum_self_inconsistent"))
    unit("UD7 a resolved reference OLDER than the datum REFUSES (a staged field cannot predate its stage)",
         refused_at(_fix(tmp, tw(ref_backdate=set(solver_arms))), "age_reference_older_than_datum"))
    print("AV1R GRADER SELFTEST units=%d expected=%d failures=%d python_O=%s" % (n, EXPECTED_UNITS, len(fails), not __debug__))
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 2
    print("AV1R GRADER SELFTEST PASS %d/%d (counted against the frozen EXPECTED_UNITS)" % (n, EXPECTED_UNITS))
    return 0


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmpdir", default="/tmp")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if count_asserts(os.path.abspath(__file__)) != 0:
        print("REFUSAL: this comparator carries an assert statement (L-332)"); return 2
    if a.selftest:
        d = os.path.join(a.tmpdir, "av1r_selftest_%d" % os.getpid()); os.makedirs(d, exist_ok=True)
        return selftest(d)
    if not a.root:
        print("usage: av1r_grade.py --root <run root> [--out FILE] | --selftest"); return 64
    try:
        r = grade(a.root)
    except Refusal as e:
        print("REFUSAL: %s -> NOT A RESULT" % e)
        if a.out:
            json.dump({"item": "CURRICULUM-%s" % ITEM, "verdict": "NOT A RESULT", "refusal": str(e)}, open(a.out, "w"), indent=1)
        return 2
    print(json.dumps(r, indent=1, default=str))
    if a.out:
        json.dump(r, open(a.out, "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
