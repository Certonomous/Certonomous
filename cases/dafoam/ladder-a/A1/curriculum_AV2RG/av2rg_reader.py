#!/usr/bin/env python3
"""AV2RG RECOVERY READER -- recovers the adjoint solve's `gmresRelTol` for ONE arm from the
THREE independent sources that carry it on disk, and REFUSES unless all three are present
and agree exactly.  ZERO SOLVER COMPUTE; every function here reads files and nothing else.

WHY THREE AND NOT ONE.  The three-source agreement rule is NOT invented here: it is the
frozen AV2R grader's own `g_toolchain` (`av2r_grade.py:466-479`), which identifies a row's
toolchain from the ledger DIGEST, the container's own `D4S_IDWARP_SO_MD5:` print and the
artefact's in-process md5, and reads `GATE FAIL` unless all three name the same library.
This module applies THAT rule, unchanged in shape, to the quantity the producer dropped --
the run-time record, the container's own print, and the frozen input:

  R  RUN-TIME   `<arm>/av2r_X.jsonl` or `<arm>/av2r_FAD.jsonl`, the single `{"kind":
                "identity"}` record's `gmresRelTol`.  This is the value the PRODUCER ITSELF
                held: `av2r_xf.py:152-156` emits it from the live `daOptions` in the same
                process, one statement before it writes the `identity` dict that omits it.
  C  CONTAINER  the arm's solver log, the DAOption echo `gmresRelTol <v>;`.  This is what
                DASimpleFoam actually PARSED -- the strongest source, because it is the
                solver's own statement of the tolerance the adjoint solve ran at, not
                anybody's record of what it was asked to be.
  F  FROZEN     `<arm>/av2r_runScript.py`, key path `daOptions["adjEqnOption"]
                ["gmresRelTol"]`, read by `ast` WITHOUT EXECUTING THE FILE.  The expected
                md5 is not written here: it is taken from the frozen producer's OWN
                `PRODUCER_MD5` constant, so this successor cannot quietly pin a different
                runScript -- the same discipline as AVWC deriving its candidate list from
                the frozen module's own `DATUM_REF`.

AGREEMENT IS EXACT, and deliberately so.  The frozen grader compares with `!=`
(`av2r_grade.py:511`) because "the band is 10 x the adjoint solve tolerance; a different
tolerance is a different band".  A reader that reconciled near-equal sources would be
choosing a band, which is the one thing a successor may not do.

A MISSING SOURCE IS A REFUSAL, NOT A VOTE.  There is no two-of-three majority and no
fallback ordering.  A repaired reader's whole risk is that it launders a genuine absence
into a pass, so absence refuses on the first source that cannot be read.

UNITS: `gmresRelTol` is DIMENSIONLESS -- a relative convergence tolerance on the Krylov
residual of the adjoint linear solve (PETSc KSP relative tolerance).  Frozen as
EXPECTED_UNITS_GMRES_REL_TOL below, before execution.

L-332: NO `assert` anywhere.
"""
import ast
import hashlib
import json
import os
import re

EXPECTED_UNITS_GMRES_REL_TOL = "dimensionless (relative Krylov residual tolerance)"
IDENTITY_KEY = "gmresRelTol"
RUNSCRIPT = "av2r_runScript.py"
RUNSCRIPT_KEY_PATH = ("daOptions", "adjEqnOption", "gmresRelTol")
JSONL = {"X": "av2r_X.jsonl", "FAD": "av2r_FAD.jsonl"}
ARTEFACT = {"X": "av2r_X.json", "FAD": "av2r_FAD.json"}
LOG_ECHO_RE = re.compile(r"^\s*gmresRelTol\s+(\S+?)\s*;\s*$", re.M)


def md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def arm_mode(arm):
    """X-S / X-P -> `X`; FAD-S / FAD-P -> `FAD`.  MESH has no producer artefact."""
    if arm.startswith("X-"):
        return "X"
    if arm.startswith("FAD-"):
        return "FAD"
    return None


# ---------------- source R: the producer's own run-time record ------------------------
def source_runtime(arm_dir, mode, refuse):
    p = os.path.join(arm_dir, JSONL[mode])
    if not os.path.isfile(p):
        refuse("G-DP", {"gmresRelTol_source_absent": "RUNTIME", "path": p})
    recs = []
    for line in open(p, errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            recs.append(json.loads(line))
        except ValueError:
            continue
    ids = [r for r in recs if r.get("kind") == "identity"]
    if len(ids) != 1:
        refuse("G-DP", {"gmresRelTol_runtime_identity_records": len(ids), "expected": 1, "path": p})
    v = ids[0].get(IDENTITY_KEY)
    if v is None:
        refuse("G-DP", {"gmresRelTol_source_absent": "RUNTIME",
                        "note": "the identity record carries no %s" % IDENTITY_KEY, "path": p})
    return float(v), p


# ---------------- source C: the container's own DAOption echo -------------------------
def source_container(log_path, refuse):
    if not log_path or not os.path.isfile(log_path):
        refuse("G-DP", {"gmresRelTol_source_absent": "CONTAINER", "path": log_path})
    hits = LOG_ECHO_RE.findall(open(log_path, errors="replace").read())
    if not hits:
        refuse("G-DP", {"gmresRelTol_source_absent": "CONTAINER",
                        "note": "no `gmresRelTol <v>;` line in the solver's own DAOption echo",
                        "path": log_path})
    vals = sorted(set(float(h) for h in hits))
    if len(vals) != 1:
        refuse("G-DP", {"gmresRelTol_container_echo_inconsistent": vals, "n_echoes": len(hits),
                        "path": log_path})
    return vals[0], log_path


# ---------------- source F: the frozen runScript, parsed, never executed ---------------
def _dict_lookup(node, key, where, refuse):
    if not isinstance(node, ast.Dict):
        refuse("G-DP", {"gmresRelTol_runscript_not_a_dict": where})
    for k, v in zip(node.keys, node.values):
        if isinstance(k, ast.Constant) and k.value == key:
            return v
    refuse("G-DP", {"gmresRelTol_runscript_key_absent": key, "at": where})
    return None


def source_frozen(arm_dir, expect_md5, refuse):
    p = os.path.join(arm_dir, RUNSCRIPT)
    if not os.path.isfile(p):
        refuse("G-DP", {"gmresRelTol_source_absent": "FROZEN", "path": p})
    got = md5_file(p)
    if got != expect_md5:
        refuse("G-DP", {"gmresRelTol_runscript_md5_moved": {"path": p, "on_disk": got,
                                                            "expected_from_frozen_producer": expect_md5}})
    tree = ast.parse(open(p, errors="replace").read(), p)
    target = None
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == RUNSCRIPT_KEY_PATH[0]:
                    target = n.value
    if target is None:
        refuse("G-DP", {"gmresRelTol_runscript_assignment_absent": RUNSCRIPT_KEY_PATH[0], "path": p})
    node = target
    for key in RUNSCRIPT_KEY_PATH[1:-1]:
        node = _dict_lookup(node, key, key, refuse)
    leaf = _dict_lookup(node, RUNSCRIPT_KEY_PATH[-1], RUNSCRIPT_KEY_PATH[-2], refuse)
    try:
        v = ast.literal_eval(leaf)
    except (ValueError, SyntaxError):
        refuse("G-DP", {"gmresRelTol_runscript_value_not_literal": ast.dump(leaf)[:200], "path": p})
        v = None
    return float(v), p


# ---------------- the agreement rule --------------------------------------------------
def recover_gmres_rel_tol(arm_dir, mode, log_path, expect_runscript_md5, refuse):
    """All three sources, or a refusal.  Exact agreement, or a refusal.  There is no
    majority vote and no ordering preference: the three are peers and a disagreement means
    the tolerance the adjoint solve ran at is UNKNOWN, which is not a band."""
    r, rp = source_runtime(arm_dir, mode, refuse)
    c, cp = source_container(log_path, refuse)
    f, fp = source_frozen(arm_dir, expect_runscript_md5, refuse)
    srcs = {"RUNTIME": {"value": r, "path": rp},
            "CONTAINER": {"value": c, "path": cp},
            "FROZEN": {"value": f, "path": fp}}
    if not (r == c == f):
        refuse("G-DP", {"gmresRelTol_sources_disagree": {k: repr(v["value"]) for k, v in srcs.items()},
                        "note": "a different tolerance is a different band; three sources that do "
                                "not agree do not name one tolerance"})
    return r, {"value": r, "units": EXPECTED_UNITS_GMRES_REL_TOL, "sources": srcs, "agreement": "EXACT"}


def repair_identity_in_copy(artefact_path, value, refuse):
    """Write the recovered value into `identity.gmresRelTol` of a COPY of the artefact --
    the field `av2r_xf.py:56-63` should have written and did not.  The FROZEN grader then
    reads it from exactly where its own pre-registration says it reads it
    (`av2r_grade.py:321`, `PREREGISTRATION.md:72`): the registered SOURCE is not changed,
    the producer's OMISSION is undone.  Read back from disk and refuse if the write is not
    visible to the reader -- a repair not proved visible is not a repair."""
    j = json.load(open(artefact_path))
    ident = j.get("identity")
    if not isinstance(ident, dict):
        refuse("G-DP", {"artefact_identity_absent": artefact_path})
    before = ident.get(IDENTITY_KEY)
    ident[IDENTITY_KEY] = value
    json.dump(j, open(artefact_path, "w"), indent=1, sort_keys=True)
    back = (json.load(open(artefact_path)).get("identity") or {}).get(IDENTITY_KEY)
    if back != value:
        refuse("G-DP", {"identity_repair_not_visible_on_readback":
                        {"path": artefact_path, "wrote": repr(value), "read_back": repr(back)}})
    return {"path": artefact_path, "before": before, "after": back}
