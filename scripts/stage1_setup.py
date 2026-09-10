#!/usr/bin/env python3
r"""CASE PROTOCOL -- STAGE 1 SETUP.  Emits the two registration artifacts and gates on
the freeze check.  Reusable; first instance SUBOFF.

AUTHORITY.  CASE_PROTOCOL_CHARTER v1.0 section 1:
    "The setup script produces a complete case from the registration and the knowledge
     base, WITH NO FREE CHOICES LEFT TO AN AGENT ... three similar levels from one script
     at ratio 1.5 to 2; BIRTH CERTIFICATE WITH HASH ON EACH LEVEL ... Solver tolerance
     strictly tighter than any gate that reads its output (the T23G2Rn2 rule: a tolerance
     equal to a gate voids the rung) ... blockage stated ... comparator pinned by hash.
     NOTHING BELOW IS RUN UNTIL THE FREEZE CHECK PASSES."
    "if the knowledge base has no entry for this flow class, the supervisor registers the
     class default with its provenance marked 'class default, first use' and proceeds.
     A MISSING ITEM NEVER WAITS."

SCHEMA.  Fixed by VERIFICATION_CHARTER v1.75 and relayed as binding; emitted verbatim,
never a variant.  Two fields exist because of the SUBOFF defects:

  n_cells_source   MANDATORY.  A path plus HOW the number was read -- "checkMesh stdout:
                   cells: N" -- and NEVER len(owner), which is nFaces (2bd.1).  null when
                   no cell-counting source can be named: a visible null beats an
                   invisible face count.
  invocations      argv as a LIST, verbatim, so a MISSING FLAG IS A DIFF AND NOT A PARSE.
                   R1b is the case: a correctly pinned grader invoked with --reference
                   absent (run_suboff_r1b_triple.sh:369).  A pinned comparator invoked
                   wrongly is an unpinned grading path (2be section 1).
  guards           armed "unconditional" | "by_data"; a by_data guard carries the source
                   condition VERBATIM, armed_by_pin, and -- because a pin proves a file
                   unchanged but not a check awake -- arming_datum_present and
                   arming_value READ FROM THE PINNED BLOB.

FREEZE CHECK.  Invoked with --restrict-to-registration, which is MANDATORY and is not
leniency: unrestricted, the frozen checker exits 3 however clean the registered set is,
because rows from other campaigns are unfrozen.  A gate no case can pass is not a gate.
The flag is carried in `invocations` verbatim like any other argv -- pinned, not
remembered, which is the lesson R1b taught.

A WARNING IS NOT A PASS.  Unseen pins WARN, so the checker can exit 0 while pins it could
not judge exist.  pins_unseen is read from the status line and carried into the state
line; a non-zero pins_unseen holds the exit condition at COULD-NOT-RUN, never GREEN.
This script COMPUTES NO ANCESTRY: it emits freeze_commit and pin blobs and the hook
derives it.

Writes only the two artifacts and an optional report.  Sends nothing, commits nothing.
"""
import argparse, hashlib, json, os, re, subprocess, sys, time
from datetime import datetime, timezone

EXIT_OK, EXIT_RED, EXIT_REFUSE = 0, 1, 2

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def git(repo, *a):
    p = subprocess.run(["git", "-C", repo] + list(a), capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else None

def blob_of(repo, relpath):
    """The blob sha git holds for this path at HEAD.  None when untracked -- and an
    untracked pin is reported as null, never as clean."""
    return git(repo, "rev-parse", "HEAD:%s" % relpath)

def run_checkmesh(prof, case):
    """The ONLY cell-count source this script will name.  If it cannot run, n_cells and
    n_cells_source are null -- the count is NEVER back-filled from len(owner)."""
    env = os.environ.copy()
    rc = prof.get("solver", {}).get("bashrc")
    if rc:
        p = subprocess.run(["bash", "-c", ". %s >/dev/null 2>&1 && env -0" % rc],
                           capture_output=True, text=True, timeout=120)
        if p.returncode == 0:
            env = {k: v for k, v in (kv.split("=", 1) for kv in p.stdout.split("\0") if "=" in kv)}
    try:
        p = subprocess.run([prof["solver"].get("check_mesh", "checkMesh"),
                            "-case", case, "-constant", "-noFunctionObjects"],
                           capture_output=True, text=True, timeout=600, env=env)
    except Exception as e:
        return None, "checkMesh could not be run: %s" % e
    if p.returncode == 127:
        return None, "checkMesh exited 127 (runtime environment absent)"
    return p.stdout, None

def parse_checkmesh(out):
    def i(pat):
        m = re.search(pat, out); return int(m.group(1)) if m else None
    def f(pat):
        # NUM matches a well-formed float and stops before sentence punctuation: checkMesh
        # prints "Total volume = 4.31...9." and a greedy [\d.eE+-]+ swallows the full stop.
        m = re.search(pat.replace("NUM", r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?"), out)
        return float(m.group(1)) if m else None
    bbox = None
    m = re.search(r"Overall domain bounding box\s*\(([^)]*)\)\s*\(([^)]*)\)", out)
    if m:
        bbox = dict(min=[float(x) for x in m.group(1).split()],
                    max=[float(x) for x in m.group(2).split()])
    return dict(n_cells=i(r"cells:\s*(\d+)"), n_faces=i(r"faces:\s*(\d+)"),
                n_points=i(r"points:\s*(\d+)"), bbox=bbox,
                total_volume=f(r"Total volume\s*=\s*(NUM)"),
                max_non_orthogonality=f(r"Mesh non-orthogonality Max:\s*(NUM)"),
                max_skewness=f(r"Max skewness\s*=\s*(NUM)"))

def mesh_manifest(case):
    d = os.path.join(case, "constant/polyMesh")
    man = {}
    for root, _, files in os.walk(d):
        for fn in sorted(files):
            p = os.path.join(root, fn)
            man[os.path.relpath(p, case)] = sha256_file(p)
    digest = hashlib.sha256(json.dumps(man, sort_keys=True).encode()).hexdigest()
    return man, digest

def birth_certificate(prof, level, case, coarser_cells, repo):
    out, why = run_checkmesh(prof, case)
    cm = parse_checkmesh(out) if out else {}
    n_cells = cm.get("n_cells")
    n_cells_source = ("%s/constant/polyMesh -- checkMesh stdout: 'cells: %d'"
                      % (os.path.relpath(case, repo), n_cells)) if n_cells is not None else None
    dim = prof.get("dim", 3)
    h_ref = None
    if n_cells and cm.get("total_volume"):
        h_ref = (cm["total_volume"] / n_cells) ** (1.0 / 3.0)
    ratio = None
    if n_cells and coarser_cells:
        ratio = (n_cells / coarser_cells) ** (1.0 / dim)
    geo = prof.get("geometry", {})
    gsrc = geo.get("source_file")
    man, digest = mesh_manifest(case)
    gen = prof.get("generator", {})
    return dict(
        case=prof["case_id"], level=level, created_utc=utc(),
        mesh=dict(n_cells=n_cells, n_cells_source=n_cells_source,
                  n_cells_source_note=("null means no cell-counting source could be named; "
                                       "len(polyMesh/owner) is nFaces and is NEVER used here "
                                       "(VERIFICATION_CHARTER 2bd.1)"),
                  n_cells_unavailable_because=why,
                  n_faces=cm.get("n_faces"), n_points=cm.get("n_points"), bbox=cm.get("bbox"),
                  h_ref=h_ref,
                  h_ref_convention="(total_volume / n_cells)**(1/3) from checkMesh",
                  refinement_ratio_vs_next_coarser=ratio,
                  refinement_ratio_convention="(N_this / N_coarser)**(1/dim), dim=%d" % dim),
        geometry=dict(source_file=gsrc,
                      sha256=sha256_file(gsrc) if gsrc and os.path.exists(gsrc) else None,
                      geometry_gate=geo.get("geometry_gate")),
        generator=dict(script=gen.get("script"),
                       blob_sha=blob_of(repo, os.path.relpath(gen["script"], repo))
                                if gen.get("script") else None,
                       argv=gen.get("argv"), rc=gen.get("rc")),
        mesh_manifest_sha256=digest, mesh_manifest=man)

def read_arming(pin_path, expr_key):
    """Evaluate a by_data guard's arming datum AGAINST THE PINNED BLOB.  A pin proves the
    file unchanged; only reading the datum proves the check awake."""
    if not pin_path or not os.path.exists(pin_path):
        return False, None
    try:
        doc = json.load(open(pin_path))
    except Exception:
        return False, None
    node = doc
    for k in expr_key.split("."):
        if isinstance(node, dict) and k in node:
            node = node[k]
        else:
            return False, None
    return (node is not None and node != 0 and node != ""), node

def _tighter_verdict(tol_cmp, tightest):
    """None when the graded-units figure was not supplied -- COULD-NOT-RUN, not True.
    An instrument that could not look and one that looked and found nothing are
    different states and only one of them is evidence."""
    g = tol_cmp.get("in_graded_units")
    if not g or g.get("iterative_drift_rel") is None:
        return None
    return bool(g["iterative_drift_rel"] <= tightest / g.get("required_factor", 10.0))

def freeze_manifest(prof, repo, freeze_commit):
    pins = []
    for p in prof["pins"]:
        rel = os.path.relpath(p["path"], repo) if os.path.isabs(p["path"]) else p["path"]
        pins.append(dict(path=rel, blob=blob_of(repo, rel), role=p["role"],
                         blob_null_means="untracked at HEAD -- reported, never treated as clean"))
    guards = []
    for g in prof.get("guards", []):
        present, value = (False, None)
        if g.get("armed") == "by_data":
            present, value = read_arming(g.get("armed_by_pin_abs"), g.get("arming_key", ""))
        guards.append(dict(name=g["name"], armed=g["armed"], condition=g["condition"],
                           armed_by_pin=(os.path.relpath(g["armed_by_pin_abs"], repo)
                                         if g.get("armed_by_pin_abs") else None),
                           arming_datum_present=present if g.get("armed") == "by_data" else None,
                           arming_value=value if g.get("armed") == "by_data" else None))
    tol = prof["solver"]["tolerance"]
    gates = prof["gates"]
    tightest = min(g["band"] for g in gates if g.get("band") is not None)
    # THE T23G2Rn2 RULE IS NOT A NUMERIC COMPARISON OF TWO DIFFERENT QUANTITIES.
    # A solver residual is a normalised equation imbalance; a gate band is a relative
    # error on the graded quantity.  1.0e-4 < 0.10 is arithmetically true and physically
    # meaningless -- it compares nothing to nothing.  R1b is the demonstration: it clears
    # the naive test and its fine level was still moving 5.71% per 100 writes against a
    # +/-10% band.  The meaningful test is CASE_PROTOCOL section 5's own rule -- iterative
    # error at least TEN TIMES smaller than what the gate must resolve -- expressed in the
    # GRADED QUANTITY's units.  Both are emitted; only the second is gated on.
    tol_cmp = dict(
        naive_numeric=dict(solver_tolerance=tol, tightest_gate=tightest,
                           passes=bool(tol < tightest),
                           admissible=False,
                           why="compares a residual to a relative band: different quantities, "
                               "not comparable; recorded to show it is NOT the test"),
        in_graded_units=prof["solver"].get("iterative_error_in_graded_units"))
    return dict(
        case=prof["case_id"],
        registration_path=os.path.relpath(prof["registration_path"], repo),
        registration_blob=blob_of(repo, os.path.relpath(prof["registration_path"], repo)),
        freeze_commit=freeze_commit,
        ancestry_note="NOT computed here; freeze_commit and pin blobs are emitted and the hook derives it",
        pins=pins,
        invocations=[dict(name=i["name"], argv=i["argv"], cwd=i.get("cwd"),
                          env_keys=i.get("env_keys", []))
                     for i in prof["invocations"]],
        guards=guards, gates=gates,
        solver_tolerance=tol, tightest_gate=tightest,
        tolerance_strictly_tighter=_tighter_verdict(tol_cmp, tightest),
        tolerance_comparison=tol_cmp,
        tolerance_rule=("T23G2Rn2: a tolerance EQUAL to a gate voids the rung. Judged in the "
                        "GRADED QUANTITY's units against CASE_PROTOCOL section 5's factor of "
                        "ten, never as a bare numeric comparison of a residual to a band"),
        cost=prof["cost"], blockage=prof["blockage"])

def main():
    ap = argparse.ArgumentParser(description="CASE PROTOCOL stage 1 setup")
    ap.add_argument("--profile", required=True)
    ap.add_argument("--emit-dir", required=True, help="case root the artifacts are written under")
    ap.add_argument("--freeze-hook", help="path to the stage-1 exit-gate hook")
    ap.add_argument("--report")
    a = ap.parse_args()
    t0 = time.time()
    prof = json.load(open(a.profile))
    repo = prof["repo"]
    freeze_commit = git(repo, "rev-parse", "HEAD")

    lines, certs = [], {}
    order = prof["level_order"]
    prev = None
    for lvl in order:
        case = prof["levels"][lvl]
        bc = birth_certificate(prof, lvl, case, prev, repo)
        prev = bc["mesh"]["n_cells"]
        dst = os.path.join(a.emit_dir, lvl, "BIRTH_CERTIFICATE.json")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        json.dump(bc, open(dst, "w"), indent=2)
        certs[lvl] = dst
        lines.append("STAGE 1 | BIRTH | %-7s | n_cells=%-8s source=%s | r_vs_coarser=%s | %s"
                     % (lvl, bc["mesh"]["n_cells"],
                        "NAMED" if bc["mesh"]["n_cells_source"] else "NULL",
                        ("%.5f" % bc["mesh"]["refinement_ratio_vs_next_coarser"])
                        if bc["mesh"]["refinement_ratio_vs_next_coarser"] else "n/a", dst))

    fm = freeze_manifest(prof, repo, freeze_commit)
    fmp = os.path.join(a.emit_dir, "FREEZE_MANIFEST.json")
    json.dump(fm, open(fmp, "w"), indent=2)

    ratios = [certs and json.load(open(certs[l]))["mesh"]["refinement_ratio_vs_next_coarser"]
              for l in order[1:]]
    ratio_ok = all(r is not None and 1.5 <= r <= 2.0 for r in ratios)
    tol_ok = fm["tolerance_strictly_tighter"]
    null_src = [l for l in order if json.load(open(certs[l]))["mesh"]["n_cells_source"] is None]
    null_blob = [p["path"] for p in fm["pins"] if p["blob"] is None]
    sleeping = [g["name"] for g in fm["guards"]
                if g["armed"] == "by_data" and not g["arming_datum_present"]]

    # --- freeze check: the exit condition.  --restrict-to-registration is MANDATORY.
    fz = dict(state="COULD-NOT-RUN", why="freeze hook not invoked", pins_unseen=None)
    if a.freeze_hook and os.path.exists(a.freeze_hook):
        # ARGV FROM THE REGISTRATION, NOT FROM MEMORY.  The hook owns whether
        # --restrict-to-registration is its own flag or one it passes downstream; hard-coding
        # a flag the hook does not take is the same class of error as omitting one it needs.
        argv = [sys.executable, a.freeze_hook] + [
            t.format(repo=repo, registration=prof["registration_path"], case_id=prof["case_id"])
            for t in prof.get("freeze_hook_argv",
                              ["--repo", "{repo}", "--registration", "{registration}"])]
        try:
            p = subprocess.run(argv, capture_output=True, text=True, timeout=600)
            m = re.search(r"pins?[_ ]unseen\D{0,4}(\d+)|PINS NOT SEEN:\s*(\d+)", p.stdout, re.I)
            unseen = int(m.group(1) or m.group(2)) if m else None
            fz = dict(state=("GREEN" if p.returncode == 0 and unseen == 0 else
                             "COULD-NOT-RUN" if p.returncode == 0 else "RED"),
                      rc=p.returncode, pins_unseen=unseen, argv=argv,
                      why=("a WARNING IS NOT A PASS: rc=0 with pins_unseen=%s means pins the "
                           "instrument could not judge exist" % unseen)
                          if p.returncode == 0 and unseen != 0 else "")
        except Exception as e:
            fz = dict(state="COULD-NOT-RUN", why="freeze hook failed to run: %s" % e, pins_unseen=None)

    reds = []
    if not ratio_ok:  reds.append("refinement ratios %s outside the charter's 1.5-2.0" % ratios)
    if tol_ok is None:
        reds.append("tolerance_strictly_tighter COULD NOT BE JUDGED: no iterative error in the "
                    "graded quantity's units was supplied; the naive residual-vs-band "
                    "comparison is not the test and is not accepted in its place")
    elif not tol_ok:
        g = fm["tolerance_comparison"]["in_graded_units"]
        reds.append("T23G2Rn2 FAIL: iterative drift in the graded quantity is %.4g of the "
                    "quantity against a gate band of %.4g -- %.2gx the band, and section 5 "
                    "requires it %gx SMALLER (naive residual-vs-band test passes and is "
                    "meaningless)" % (g["iterative_drift_rel"], fm["tightest_gate"],
                                      g["iterative_drift_rel"] / fm["tightest_gate"],
                                      g.get("required_factor", 10.0)))
    if null_src:      reds.append("n_cells_source NULL on %s" % ",".join(null_src))
    if null_blob:     reds.append("pin(s) untracked at HEAD (blob null): %s" % ",".join(null_blob))
    if sleeping:      reds.append("SLEEPING GUARD(S) %s -- by_data and the arming datum is "
                                  "absent/null in the pinned blob" % ",".join(sleeping))
    overall = "RED" if reds else ("GREEN" if fz["state"] == "GREEN" else "COULD-NOT-RUN")

    for l in lines: print(l)
    print("STAGE 1 | FREEZE| %-13s | rc=%s pins_unseen=%s | %s"
          % (fz["state"], fz.get("rc"), fz.get("pins_unseen"), fz.get("why", "")))
    print("STAGE 1 | EXIT  | %-13s | ratios=%s tol_strictly_tighter=%s | %s | %.1f s"
          % (overall, ["%.5f" % r if r else None for r in ratios], tol_ok,
             ("; ".join(reds) if reds else "no red"), time.time() - t0))
    rep = dict(stage=1, case=prof["case_id"], overall=overall, birth_certificates=certs,
               freeze_manifest=fmp, freeze_check=fz, reds=reds,
               ratios=ratios, tolerance_strictly_tighter=tol_ok,
               sleeping_guards=sleeping, untracked_pins=null_blob)
    if a.report:
        json.dump(rep, open(a.report, "w"), indent=2)
    return EXIT_OK if overall == "GREEN" else EXIT_RED if overall == "RED" else EXIT_REFUSE

if __name__ == "__main__":
    sys.exit(main())
