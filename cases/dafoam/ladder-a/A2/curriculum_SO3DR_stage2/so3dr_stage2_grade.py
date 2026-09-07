#!/usr/bin/env python3
"""SO-3D-R STAGE 2 -- the grader for the cl04-standalone discrimination experiment.

Reads each of the 36 registered standalone legs' logs, counts the standalone
failure banner per leg, computes r_sa, and applies G-SA-DISCRIM:

    r_sa >= 50 %  (>= 18/36) -> HIGH -> "cl04's OWN primal is the pathology"
                                        (coupling-primary REFUTED; a RESULT)
    r_sa <= 10 %  (<=  3/36) -> LOW  -> "the MULTIPOINT ABORTED-TRIAL COUPLING
                                        is the cause" (routes to the om.ExecComp
                                        code-read; a RESULT)
    10 % < r_sa < 50 %       -> NOT A RESULT (indeterminate)

Controls and falsifiers, all registered in PREREGISTRATION.md sections 3-4:
  * planted-zero banner-reader control (rule 3): a reader that cannot see a
    planted banner REFUSES; a decoy line containing "failed" must NOT be counted.
  * strict-completion + age-guard per leg (rule 4): a leg is a completed primal
    only with End, last time == endTime, fields present and every field newer
    than its own 0/. A leg failing this is NOT A RESULT for that leg, excluded
    from r_sa, never a silent success and never a banner.
  * F1 banner-blind reader; F2 over-count; F3 rig-confound (SUCCEEDED-stratum
    instability downgrades a HIGH reading to NOT A RESULT); F4 echo-check
    (injected AoA + shape/twist md5 vs the D6R block); F5 indeterminate-band
    honesty; F6 sample-tampering (recompute the sample from the pinned log/seed).

freeze_check() extracts the instrument list from THIS FILE's own source (ast),
never from memory.

RULING 2's bar is PRESERVED: the 39.7x is a DATUM, never a verdict; this grader
never computes, quotes or emits it.

Verdict vocabulary is the fixed six: PASS / GATE REACHED / GATE FAIL /
NOT A RESULT / BLOCKED / PENDING. No `assert` statement carries anything.
SUBMISSIONS PARKED.
"""
import os
import re
import ast
import sys
import json
import glob
import hashlib
import argparse

# --------------------------------------------------------------------------
# REGISTERED CONSTANTS (frozen in PREREGISTRATION.md)
# --------------------------------------------------------------------------
D6R_LOG = "/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/O_mp_20260828T162849Z_1898072.log"
D6R_LOG_SHA256 = "394d9f5d8c59ea79602e678cec7a75915bef53a048b61e153d835fce57fc675d"
SAMPLE_MD5 = "55bf8e2dcc07fbe3197f2c53421ad019"
SEED = 20260907
N_TOTAL = 36
N_FAIL = 24
N_SUCC = 12
HIGH_THRESH = 0.50            # r_sa >= 0.50 -> HIGH
LOW_THRESH = 0.10             # r_sa <= 0.10 -> LOW
F3_SUCC_CONFOUND = 0.10       # SUCCEEDED-stratum standalone rate above this confounds a HIGH
AOA_ECHO_TOL = 1.0e-6
ENDTIME = 1000                # the A2-wing primal endTime (D6R / D6RF4, controlDict endTime 1000)
# The A2-wing solver is COMPRESSIBLE DARhoSimpleFoam, run DECOMPOSED (np=4) with
# GZIPPED fields. Field sets VERIFIED on disk against a real endTime directory:
#   endTime: /home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-convergence-probe/P_conv/mp04/processor0/1000/
#            -> {T,U,alphat,nuTilda,nut,p,phi,rho, betaFINuTilda,fvSource,fvSourceEnergy,meshPhi} (all .gz)
#   0/     : .../P_conv/mp04/processor0/0/  -> {T,U,alphat,nuTilda,nut,p} (all .gz)
# FIELDS_ENDTIME are the primal STATE fields the solver writes at endTime (phi
# added on Sanaa's 2026-09-06 approval, rule 4). FIELDS_ZERO are those also
# present in 0/ (phi is NOT in 0/), used for the age-guard reference mtime.
FIELDS_ENDTIME = ("U", "p", "T", "nut", "alphat", "nuTilda", "phi")
FIELDS_ZERO = ("U", "p", "T", "nut", "alphat", "nuTilda")

# the ONLY banner that counts -- byte-identical to Stage-1's RE_FAIL_BANNER
RE_FAIL_BANNER = re.compile(r"^Primal solution failed!$")
RE_END = re.compile(r"^End$")
RE_UMAG = re.compile(r"^Setting UMag = \S+ AoA = (\S+) degs")
RE_TIME = re.compile(r"^Time = (\S+)$")


class Refusal(Exception):
    pass


# --------------------------------------------------------------------------
# the banner reader -- the one statistic everything else guards
# --------------------------------------------------------------------------
def count_banners(lines):
    """Count `Primal solution failed!` banners. Anchored: a decoy line merely
    containing 'failed' is NOT counted (guards F2)."""
    return sum(1 for ln in lines if RE_FAIL_BANNER.match(ln))


def _blinded_count_banners(lines):
    """A DELIBERATELY-WRONG reader used ONLY by the plant control: it looks for a
    string the banner does not carry, so it can never see a real banner. The
    plant control must catch it."""
    return sum(1 for ln in lines if ln == "PRIMAL_OK_SENTINEL_NEVER_PRESENT")


# --------------------------------------------------------------------------
# planted-zero control (rule 3)
# --------------------------------------------------------------------------
def control_planted_zero():
    """PLANT-SA-BANNER + PLANT-SA-DECOY. Returns a dict of outcomes; raises
    Refusal if the honest reader cannot see a planted banner."""
    clean = ["Time = 1", "Running Primal Solver 001", "SIMPLE solution converged", "End"]
    if count_banners(clean) != 0:
        raise Refusal("PLANT-SA control: the clean fixture already reads a banner. UNMEASURED.")

    planted = clean[:3] + ["Primal solution failed!"] + clean[3:]
    honest = count_banners(planted)
    if honest - count_banners(clean) != 1:
        raise Refusal("PLANT-SA-BANNER: honest reader did not see the planted banner move +1. REFUSE.")

    # the blinded reader must FAIL to see it -- proving the control has teeth
    blind = _blinded_count_banners(planted) - _blinded_count_banners(clean)
    blind_caught = (blind != 1)
    if not blind_caught:
        raise Refusal("PLANT-SA-BANNER: a reader that cannot see the banner was NOT caught. REFUSE.")

    decoy = clean[:3] + ["  the primal solution failed to satisfy something"] + clean[3:]
    decoy_count = count_banners(decoy) - count_banners(clean)
    if decoy_count != 0:
        raise Refusal("PLANT-SA-DECOY: a non-banner 'failed' line was counted (over-count). REFUSE.")

    return {
        "PLANT-SA-BANNER": "PASS",
        "planted_delta_honest": honest - count_banners(clean),
        "blinded_reader_caught": blind_caught,
        "PLANT-SA-DECOY": "PASS",
        "decoy_delta": decoy_count,
    }


# --------------------------------------------------------------------------
# design-vector parse -- pure python, identical to the rig's parse, no dafoam
# --------------------------------------------------------------------------
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _floats_between(text, start_key):
    i = text.find(start_key)
    if i < 0:
        return None
    j = text.find("array([", i)
    if j < 0:
        return None
    k = text.find("])", j)
    if k < 0:
        return None
    body = text[j + len("array(["):k]
    return [float(t) for t in re.findall(r"[-+]?\d+\.?\d*(?:[eE][-+]?\d+)?", body)]


def _md5_floats(vals):
    """md5 of a float64 buffer -- matches the rig's
    hashlib.md5(np.ascontiguousarray(arr).tobytes()) for arrays parsed from the
    same log (identical float list -> identical little-endian float64 bytes)."""
    import struct
    return hashlib.md5(b"".join(struct.pack("<d", v) for v in vals)).hexdigest()


def d6r_block_reference(log_lines, dv_block_line):
    window = "\n".join(log_lines[dv_block_line - 1: dv_block_line - 1 + 120])
    patchv = _floats_between(window, "'dvs.patchV_cl04':")
    shape = _floats_between(window, "'dvs.shape':")
    twist = _floats_between(window, "'dvs.twist':")
    if patchv is None or shape is None or twist is None:
        raise Refusal("F4: could not parse the D6R block at line %d" % dv_block_line)
    return {
        "aoa": patchv[1],
        "shape_md5": _md5_floats(shape),
        "twist_md5": _md5_floats(twist),
    }


# --------------------------------------------------------------------------
# strict completion + age guard (rule 4), per leg
# --------------------------------------------------------------------------
def _field_path(time_dir, fld):
    """Return the path to a field written either plain or gzipped, else None.
    The A2-wing solver writes gzipped fields (<fld>.gz)."""
    for cand in (os.path.join(time_dir, fld), os.path.join(time_dir, fld + ".gz")):
        if os.path.exists(cand):
            return cand
    return None


def _time_dirs_for(leg_dir):
    """Resolve the 0 and endTime directories, handling the DECOMPOSED layout
    (processor0/0, processor0/1000) the solver actually writes at np=4, and a
    reconstructed root layout (0, 1000) as a fallback."""
    proc0 = os.path.join(leg_dir, "processor0")
    if os.path.isdir(proc0):
        return os.path.join(proc0, "0"), os.path.join(proc0, str(ENDTIME))
    return os.path.join(leg_dir, "0"), os.path.join(leg_dir, str(ENDTIME))


def leg_completed(leg_dir, log_lines):
    """Returns (True, note) if the leg is a completed primal; (False, reason)
    otherwise. A DAFoam post-End acceptance refusal (the banner) is STILL a
    completed primal -- completion is about whether the solve ran, not whether
    acceptance passed."""
    if not any(RE_END.match(ln) for ln in log_lines):
        return False, "no End line -- incomplete or infra-killed leg"
    times = [m.group(1) for ln in log_lines for m in [RE_TIME.match(ln)] if m]
    if not times:
        return False, "no Time lines"
    try:
        last_t = max(float(t) for t in times)
    except ValueError:
        return False, "non-numeric Time token"
    if last_t < ENDTIME:
        return False, "last time %s < endTime %d" % (last_t, ENDTIME)
    zerot, endt = _time_dirs_for(leg_dir)
    if not os.path.isdir(endt) or not os.path.isdir(zerot):
        return False, "missing 0/ or %d/ time dir (looked in %s)" % (ENDTIME, os.path.dirname(endt))
    # age-guard reference: newest mtime among the 0/ state fields
    z_paths = [p for f in FIELDS_ZERO for p in [_field_path(zerot, f)] if p]
    if not z_paths:
        return False, "no state fields found in 0/ (%s)" % zerot
    z_mtime = max(os.path.getmtime(p) for p in z_paths)
    for fld in FIELDS_ENDTIME:
        ef = _field_path(endt, fld)
        if ef is None:
            return False, "field %s (or %s.gz) absent at endTime" % (fld, fld)
        if os.path.getmtime(ef) <= z_mtime:
            return False, "age guard: field %s at endTime not newer than 0/" % fld
    return True, "completed"


# --------------------------------------------------------------------------
# F4 echo-check per leg
# --------------------------------------------------------------------------
def falsifier_f4_echo(leg_dir, log_lines, dv_block_line, ref):
    sidecar_path = os.path.join(leg_dir, "injected_dv.json")
    if not os.path.isfile(sidecar_path):
        raise Refusal("F4: leg %s has no injected_dv.json sidecar" % leg_dir)
    with open(sidecar_path) as fh:
        sc = json.load(fh)
    if sc.get("shape_md5") != ref["shape_md5"] or sc.get("twist_md5") != ref["twist_md5"]:
        raise Refusal("F4: injected shape/twist md5 != D6R block %d -- wrong design injected" % dv_block_line)
    if abs(float(sc.get("aoa_injected", 1e9)) - ref["aoa"]) > AOA_ECHO_TOL:
        raise Refusal("F4: injected AoA != D6R block AoA (block %d)" % dv_block_line)
    # the leg's own log must echo the AoA it actually ran
    log_aoas = [float(m.group(1)) for ln in log_lines for m in [RE_UMAG.match(ln)] if m]
    if not log_aoas or min(abs(a - ref["aoa"]) for a in log_aoas) > AOA_ECHO_TOL:
        raise Refusal("F4: leg log AoA does not echo the registered AoA (block %d)" % dv_block_line)
    return True


# --------------------------------------------------------------------------
# F6 sample tamper check
# --------------------------------------------------------------------------
def falsifier_f6_sample(sample_path):
    if not os.path.isfile(sample_path):
        raise Refusal("F6: registered sample %s absent" % sample_path)
    if hashlib.md5(open(sample_path, "rb").read()).hexdigest() != SAMPLE_MD5:
        raise Refusal("F6: registered sample md5 != frozen %s -- sample tampered" % SAMPLE_MD5)
    with open(sample_path) as fh:
        s = json.load(fh)
    if s.get("N") != N_TOTAL or s.get("n_fail") != N_FAIL or s.get("n_succ") != N_SUCC:
        raise Refusal("F6: sample strata changed from the registered 24+12")
    if s.get("log_sha256") != D6R_LOG_SHA256:
        raise Refusal("F6: sample's D6R log sha256 != registered")
    return s


# --------------------------------------------------------------------------
# G-SA-DISCRIM
# --------------------------------------------------------------------------
def g_sa_discrim(n_failed, n_completed, r_succ):
    """Apply the gate. r_sa over completed legs.

    Returns (verdict, discrimination, finding, r_sa, basis).

    `verdict` is ALWAYS one of the fixed six tokens (CLAUDE.md rule 1;
    DAFOAM_CHARTER.md §8) -- never a descriptive string. Registered mapping
    (PREREGISTRATION.md §2):
      * a CLEAR discrimination (HIGH or LOW) -> **GATE REACHED**: the item
        reached its registered informative endpoint. The direction and the fix
        it routes are carried in `discrimination` / `finding`, NOT in `verdict`.
      * indeterminate (10-50%) -> **NOT A RESULT**.
      * a HIGH reading with the SUCCEEDED stratum itself unstable (F3 rig
        confound) -> **NOT A RESULT**.
      * no completed legs -> **NOT A RESULT**.
    RULING 2's bar: no ratio here is a verdict; the 39.7x is never computed."""
    if n_completed <= 0:
        return "NOT A RESULT", None, "no completed legs", None, "no completed legs"
    r_sa = n_failed / n_completed
    if r_sa >= HIGH_THRESH:
        if r_succ is not None and r_succ > F3_SUCC_CONFOUND:
            return ("NOT A RESULT", "HIGH-CONFOUNDED",
                    "F3 rig-confound: SUCCEEDED-stratum standalone rate %.4f > %.2f; a HIGH reading "
                    "cannot be attributed to intrinsic pathology" % (r_succ, F3_SUCC_CONFOUND),
                    r_sa, "F3 rig confound")
        return ("GATE REACHED", "HIGH",
                "cl04's own primal is the pathology; route to D6RF5-class fix",
                r_sa, "r_sa >= 0.50")
    if r_sa <= LOW_THRESH:
        return ("GATE REACHED", "LOW",
                "multipoint aborted-trial coupling; route to the om.ExecComp code-read",
                r_sa, "r_sa <= 0.10")
    return ("NOT A RESULT", "INDETERMINATE",
            "indeterminate: 0.10 < r_sa < 0.50, the sample did not discriminate",
            r_sa, "indeterminate band")


# --------------------------------------------------------------------------
# freeze_check -- instrument list from THIS FILE's source, not memory
# --------------------------------------------------------------------------
def freeze_check(self_path=None):
    self_path = self_path or os.path.abspath(__file__)
    with open(self_path) as fh:
        tree = ast.parse(fh.read())
    instruments = sorted(
        n.name for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef)
        and (n.name.startswith(("control_", "falsifier_")) or n.name in ("count_banners", "leg_completed", "g_sa_discrim"))
    )
    n_asserts = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert))
    return {"instruments_from_code": instruments, "assert_nodes": n_asserts}


# --------------------------------------------------------------------------
# grading driver
# --------------------------------------------------------------------------
def grade(runs_root, sample_path, out_path):
    report = {"item": "SO3DR-STAGE2", "gate": "G-SA-DISCRIM",
              "ruling2_bar": "the 39.7x is a DATUM, never a verdict; not computed here",
              "status": "PENDING"}
    report["freeze_check"] = freeze_check()
    report["plant_control"] = control_planted_zero()      # raises Refusal if blind
    falsifier_f6_sample(sample_path)                       # F6: raises Refusal on tamper
    report["sample"] = "verified"
    if sha256_of(D6R_LOG) != D6R_LOG_SHA256:
        raise Refusal("D6R log sha256 != registered -- UNMEASURED")
    d6r_lines = open(D6R_LOG, encoding="utf-8", errors="replace").read().splitlines()
    sample = json.load(open(sample_path))["sample"]

    legs = []
    n_failed = n_completed = 0
    succ_failed = succ_completed = 0
    incomplete = []
    for row in sample:
        bl = row["dv_block_line"]
        leg_dir = os.path.join(runs_root, "leg_%d" % bl, "mp04")
        log_glob = sorted(glob.glob(os.path.join(runs_root, "leg_%d" % bl, "*.log")))
        if not log_glob:
            incomplete.append((bl, "no log"))
            continue
        lines = open(log_glob[-1], encoding="utf-8", errors="replace").read().splitlines()
        ref = d6r_block_reference(d6r_lines, bl)
        falsifier_f4_echo(leg_dir, lines, bl, ref)          # raises on wrong design
        ok, note = leg_completed(leg_dir, lines)
        if not ok:
            incomplete.append((bl, note))
            continue
        nb = count_banners(lines)
        if nb not in (0, 1):
            raise Refusal("F2: leg %d has %d banners; expected 0 or 1" % (bl, nb))
        failed = nb == 1
        n_completed += 1
        n_failed += int(failed)
        if row["multipoint_outcome"] == "SUCCEEDED":
            succ_completed += 1
            succ_failed += int(failed)
        legs.append({"dv_block_line": bl, "multipoint_outcome": row["multipoint_outcome"],
                     "banners": nb, "standalone_failed": failed})

    r_succ = (succ_failed / succ_completed) if succ_completed else None
    report["legs_completed"] = n_completed
    report["legs_incomplete"] = incomplete
    report["r_succ_stratum"] = r_succ
    if incomplete:
        report["status"] = "PENDING"
        report["verdict"] = "PENDING"          # six-token: not yet run -- re-run the incomplete legs
        report["note"] = ("%d of %d legs not completed (rule 4) -- re-run before a final verdict; "
                          "no G-SA-DISCRIM verdict is emitted on a partial run" % (len(incomplete), N_TOTAL))
    else:
        verdict, discrimination, finding, r_sa, why = g_sa_discrim(n_failed, n_completed, r_succ)
        report["status"] = "GRADED"
        report["r_sa"] = r_sa
        report["n_failed"] = n_failed
        report["verdict"] = verdict            # six-token: GATE REACHED / NOT A RESULT
        report["discrimination"] = discrimination   # HIGH / LOW / INDETERMINATE / HIGH-CONFOUNDED
        report["finding"] = finding            # the routing, NEVER the verdict token
        report["verdict_basis"] = why
    report["legs"] = legs
    if out_path:
        with open(out_path, "w") as fh:
            json.dump(report, fh, indent=1)
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--runs-root", help="root holding leg_<dv_block_line>/ directories")
    p.add_argument("--sample", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                    "so3dr_stage2_registered_sample.json"))
    p.add_argument("--out", default=None)
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    try:
        if args.selftest:
            fc = freeze_check()
            pc = control_planted_zero()
            print("freeze_check instruments (from code):", fc["instruments_from_code"])
            print("assert nodes in grader:", fc["assert_nodes"])
            print("plant control:", pc)
            # F5 band arithmetic -- six-token verdict + discrimination (no compute)
            for nf in (3, 4, 17, 18):
                v, disc, finding, r, why = g_sa_discrim(nf, 36, 0.0)
                print("  F5 band: %2d/36 = %.3f -> verdict=%s discrimination=%s" % (nf, r, v, disc))
            # F3: a HIGH reading downgraded to NOT A RESULT when SUCCEEDED stratum unstable
            v, disc, finding, r, why = g_sa_discrim(20, 36, 0.25)
            print("  F3 confound: 20/36 with r_succ=0.25 -> verdict=%s discrimination=%s" % (v, disc))
            print("  verdict tokens used:", sorted({g_sa_discrim(n, 36, 0.0)[0] for n in (3, 10, 18)} | {"PENDING"}))
            print("SELFTEST OK")
            return 0
        if not args.runs_root:
            sys.stderr.write("grade mode needs --runs-root (leg directories). None given.\n")
            return 2
        rep = grade(args.runs_root, args.sample, args.out)
        print(json.dumps({k: rep[k] for k in ("status", "verdict", "discrimination", "finding", "r_sa") if k in rep}, indent=1))
        return 0
    except Refusal as e:
        sys.stderr.write("STAGE2 GRADER REFUSE (exit 2): %s\n" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
