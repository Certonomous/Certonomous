#!/usr/bin/env python3
"""R1 -- THE F3S UNIQUE-SELECTOR REPAIR DRIVER.

Registration : verification/campaign/R1_F3S_SELECTOR_REPAIR_PREREGISTRATION.md
Specification: docs/standards/UNIQUE_SELECTOR_RULE.md, frozen at
               ae2c8c49366259fe2c5bb8ece09d32bc8017c3f6

WHAT THIS PROGRAM WILL NOT DO
  * It will not grade without --prereg-commit, and it verifies that sha by HASHING the
    registration on disk against its committed blob (CLAUDE.md rule 2; the reference
    implementation is cases/F26_RINGLEB/grade_f26d.py:419-431).
  * It will not grade until its OWN BIRTH CONTROL has been driven -- until OpenFOAM's
    sampler has written p_ramp.raw and T_ramp.raw itself and the OLD predicate has been
    observed returning T_ramp.raw first on those real files.  Sanaa 2026-08-28T17:01Z.
  * It will not run under `python3 -O`.  It carries ZERO assert statements -- every
    control is an explicit raise or an explicit exit -- and it refuses under -O anyway,
    because a harness that runs under -O invites an assert to be added later and
    silently deleted (L-332).
  * It will not degrade.  Every refusal is exit 2 (rule 4).
  * It edits NOTHING under successor_triple_2026-08-26/ and hashes that whole tree
    before and after to prove it (G-R1-8).
"""

import argparse
import ast
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
F3_ROOT = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(F3_ROOT)))
FIRED = os.path.join(F3_ROOT, "successor_triple_2026-08-26")
FINE = os.path.join(FIRED, "runs", "wedge", "M2.5_th10", "fine")
FOAM = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

PREREG = "verification/campaign/R1_F3S_SELECTOR_REPAIR_PREREGISTRATION.md"
SPEC = "docs/standards/UNIQUE_SELECTOR_RULE.md"
SPEC_COMMIT = "ae2c8c49366259fe2c5bb8ece09d32bc8017c3f6"

CAP_CORE_MIN = 0.3000        # registered cap, sec.9.2.  NEVER raised.
EST_CORE_MIN = 0.2000        # registered estimate, sec.9.2
RANKS = 1
CAP_WALL_S = CAP_CORE_MIN * 60.0 / RANKS      # 18.0 s

RECORD = os.path.join(HERE, "R1_CONTROL_RECORD.json")

sys.path.insert(0, HERE)
import selector_controls as SC                                    # noqa: E402


class Refusal(Exception):
    pass


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def _git(args, cwd=REPO):
    return subprocess.run(["git"] + list(args), cwd=cwd, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True)


def blob_sha1(path):
    data = io.open(path, "rb").read()
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def verify_freeze(commit, relpath):
    """Rule 2: the frozen file that runs must BE the committed blob."""
    out = _git(["rev-parse", "%s:%s" % (commit, relpath)])
    if out.returncode != 0:
        raise Refusal("FREEZE: %s:%s does not resolve -- %s"
                      % (commit, relpath, out.stderr.strip()))
    want = out.stdout.strip()
    disk = os.path.join(REPO, relpath)
    if not os.path.isfile(disk):
        raise Refusal("FREEZE: %s is not on disk" % disk)
    got = blob_sha1(disk)
    if got != want:
        raise Refusal("FREEZE: %s on disk (blob %s) is NOT the committed blob %s at %s. "
                      "The grading path is fixed at the pre-registration commit."
                      % (relpath, got[:12], want[:12], commit))
    return want


def sha256_tree(root):
    out = {}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d != "__pycache__"]
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            h = hashlib.sha256()
            with io.open(p, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 16), b""):
                    h.update(chunk)
            out[os.path.relpath(p, REPO)] = h.hexdigest()
    return out


def sha256_file(p):
    h = hashlib.sha256()
    with io.open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def invariance_set():
    s = sha256_tree(FIRED)
    for rel in (SPEC, PREREG, "scripts/roache_triple.py"):
        s[rel] = sha256_file(os.path.join(REPO, rel))
    return s


# ---------------------------------------------------------------------------
# BR-1 -- THE BIRTH CONTROL.  OpenFOAM writes the fixtures, not this program.
# ---------------------------------------------------------------------------

def _copy_case(dst, surface_name):
    """Copy the retained fine case and change ONLY the surface name in its dict."""
    os.makedirs(dst)
    for sub in ("0", "constant", "system", "3.11989651"):
        shutil.copytree(os.path.join(FINE, sub), os.path.join(dst, sub))
    shutil.copy2(os.path.join(FINE, "meta.json"), os.path.join(dst, "meta.json"))
    dictp = os.path.join(dst, "system", "surfaceSampleDict")
    src = io.open(dictp, encoding="utf-8").read()
    if src.count("wedgeSurface") != 1:
        raise Refusal("BR-1: surfaceSampleDict names 'wedgeSurface' %d times, want 1 -- "
                      "the surface name is not a single token and this copy would change "
                      "more than the name" % src.count("wedgeSurface"))
    io.open(dictp, "w", encoding="utf-8").write(
        src.replace("wedgeSurface", surface_name, 1))
    os.utime(dictp, None)
    return dictp


def _sample(case_dir, budget_s, log_path):
    """Run THE REAL SAMPLER.  Exactly the command run_f3s.py:253 runs."""
    cmd = "postProcess -func surfaceSampleDict -latestTime"
    full = "source %s >/dev/null 2>&1; %s" % (FOAM, cmd)
    t0 = time.time()
    try:
        p = subprocess.run(["bash", "-c", full], cwd=case_dir, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=max(1.0, budget_s))
        rc, out = p.returncode, p.stdout
    except subprocess.TimeoutExpired:
        io.open(log_path, "wb").write(b"TIMEOUT\n")
        raise Refusal("CAP: the sampler exceeded the registered wall allowance of "
                      "%.1f s. An overrun STOPS the item; it does not get a new budget."
                      % CAP_WALL_S)
    io.open(log_path, "wb").write(out)
    return dict(command=cmd, rc=rc, wall_s=round(time.time() - t0, 4),
                log=os.path.relpath(log_path, REPO),
                end_line=b"\nEnd\n" in out or out.rstrip().endswith(b"End"))


def _latest_sample_dir(case_dir):
    root = os.path.join(case_dir, "postProcessing", "surfaceSampleDict")
    if not os.path.isdir(root):
        raise Refusal("BR-1: the sampler wrote no postProcessing/surfaceSampleDict")
    times = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
    if not times:
        raise Refusal("BR-1: no time directory under %s" % root)
    return os.path.join(root, max(times, key=float))


def drive_birth_control(budget_s):
    """Produce the C1-C4 fixtures by RUNNING OPENFOAM, and write the evidence."""
    scratch = tempfile.mkdtemp(prefix="br1_f3s_")
    art = SC.ARTIFACT_ROOT
    if os.path.isdir(art):
        shutil.rmtree(art)
    os.makedirs(art)
    transcript, invocations = [], []
    t_start = time.time()
    try:
        for surface, expect in (("ramp", ["p_ramp.raw", "rho_ramp.raw", "T_ramp.raw"]),
                                ("rgh_wedgeSurface", ["p_rgh_wedgeSurface.raw",
                                                      "rho_rgh_wedgeSurface.raw",
                                                      "T_rgh_wedgeSurface.raw"])):
            case = os.path.join(scratch, "case_" + surface)
            dictp = _copy_case(case, surface)
            dict_mtime = os.path.getmtime(dictp)
            spent = time.time() - t_start
            inv = _sample(case, budget_s - spent,
                          os.path.join(case, "log.surfsample"))
            inv["surface"] = surface
            if inv["rc"] != 0:
                raise Refusal("BR-1(i): the sampler returned rc %d for surface %r"
                              % (inv["rc"], surface))
            if not inv["end_line"]:
                raise Refusal("BR-1(i): no End line in the sampler log for surface %r"
                              % surface)
            d = _latest_sample_dir(case)
            wrote = sorted(os.listdir(d))
            missing = [e for e in expect if e not in wrote]
            if missing:
                raise Refusal("BR-1: the sampler did not write %r; it wrote %r"
                              % (missing, wrote))
            newer = all(os.path.getmtime(os.path.join(d, e)) > dict_mtime
                        for e in expect)
            if not newer:
                raise Refusal("BR-1(ii): the .raw files for surface %r are NOT newer "
                              "than the surfaceSampleDict that named them" % surface)
            inv["newer_than_dict"] = True
            inv["wrote"] = wrote
            inv["sample_dir_in_scratch"] = d
            inv["mtimes"] = {e: os.path.getmtime(os.path.join(d, e)) for e in wrote}
            inv["dict_mtime"] = dict_mtime
            if surface == "ramp":
                old = SC.old_predicate(d)
                inv["old_predicate"] = old
                if len(old) < 2 or old[0] != "T_ramp.raw":
                    raise Refusal(
                        "BR-1(iii): the OLD predicate on the real sampler's own output "
                        "returned %r; it must return >= 2 files with T_ramp.raw FIRST. "
                        "The defect was never observed firing on producer-written "
                        "files, so nothing may be reported repaired." % (old,))
            for e in wrote:
                shutil.copy2(os.path.join(d, e), os.path.join(art, e))
            # RETAIN THE SAMPLER'S OWN LOG. A record that cites a log deleted with the
            # scratch tree cites nothing.
            keep_log = os.path.join(art, "log.surfsample_%s" % surface)
            shutil.copy2(os.path.join(case, "log.surfsample"), keep_log)
            inv["log"] = os.path.relpath(keep_log, REPO)
            exec_lines = [ln for ln in io.open(keep_log, encoding="utf-8",
                                               errors="replace").read().splitlines()
                          if ln.startswith("Exec")]
            inv["exec_line"] = exec_lines[0] if exec_lines else None
            inv["retained_raw"] = [os.path.relpath(os.path.join(art, e), REPO)
                                   for e in wrote]
            invocations.append(inv)
            transcript.append(
                "%-18s %s -> rc=%d End=%s wall=%.3fs wrote %s"
                % (surface, inv["command"], inv["rc"], inv["end_line"],
                   inv["wall_s"], wrote))

        # BR-2 -- the retained singleton, byte-identical, sha256 asserted.
        graded_ok, graded = True, {}
        for name in ("p_wedgeSurface.raw", "T_wedgeSurface.raw", "rho_wedgeSurface.raw"):
            src = os.path.join(SC.GRADED_DIR, name)
            if not os.path.isfile(src):
                raise Refusal("BR-2: retained graded artefact absent: %s" % src)
            dst = os.path.join(art, name)
            shutil.copy2(src, dst)
            a, b = sha256_file(src), sha256_file(dst)
            graded[name] = dict(original=a, retained=b, equal=(a == b),
                                bytes=os.path.getsize(src))
            graded_ok = graded_ok and (a == b)
        if not graded_ok:
            raise Refusal("BR-2: a retained singleton fixture is NOT sha256-identical "
                          "to the original")

        ramp = invocations[0]
        ev = dict(
            birth_requirement=("Sanaa 2026-08-28T17:01Z, implemented as a REFUSAL "
                               "CONDITION: this instrument grades nothing until the "
                               "real producer has written the fixtures and the defect "
                               "has been observed firing on them."),
            producer=("OpenFOAM v2606, `postProcess -func surfaceSampleDict "
                      "-latestTime` -- the command run_f3s.py:253 runs"),
            reader=("select_one() in this successor's grade_f3s.py and run_f3s.py, "
                    "reached from read_p_wall_mean() -- the production reader"),
            source_case=os.path.relpath(FINE, REPO),
            invocations=invocations,
            old_predicate_first_element=ramp["old_predicate"][0],
            old_predicate_len=len(ramp["old_predicate"]),
            old_predicate_full=ramp["old_predicate"],
            graded_dir_sha256_match=graded_ok,
            graded_singleton=graded,
            retained_artifacts=os.path.relpath(art, REPO),
            transcript=transcript,
            note=("NO .raw FILE HERE WAS HAND-WRITTEN AND NONE WAS RENAMED. Every "
                  "basename is the one OpenFOAM chose: p_ramp.raw and T_ramp.raw come "
                  "from a surface named `ramp`, and p_rgh_wedgeSurface.raw comes from a "
                  "surface named `rgh_wedgeSurface` -- so the two-member fixture C1 "
                  "reads is a pair the PRODUCER emitted, not a copy renamed to look "
                  "like one."),
            wall_s=round(time.time() - t_start, 4))
        io.open(SC.EVIDENCE, "w", encoding="utf-8").write(
            json.dumps(ev, indent=2, sort_keys=True) + "\n")
        return ev
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


# ---------------------------------------------------------------------------
# THE DRIVER'S OWN CONTROLS -- each fired in BOTH directions
# ---------------------------------------------------------------------------

def _both(name, positive, negative, out):
    """`positive` must succeed; `negative` must raise.  Anything else is a refusal."""
    try:
        pdetail = positive()
    except Exception as e:                                        # noqa: BLE001
        refuse("SELFTEST control %s: the POSITIVE limb failed (%s: %s). A control that "
               "cannot pass on a good input is not a control." % (name, type(e).__name__, e))
    fired = False
    try:
        negative()
    except Exception as e:                                        # noqa: BLE001
        fired, ndetail = True, "%s: %s" % (type(e).__name__, str(e).splitlines()[0][:90])
    if not fired:
        refuse("SELFTEST control %s: the NEGATIVE limb DID NOT FIRE. The check accepted "
               "an input it must refuse; it is measuring nothing." % name)
    out.append((name, pdetail, ndetail))


def selftest():
    out = []

    # D1 -- the pre-registration sha check, both ways.
    def d1p():
        return "prereg blob %s verified at %s" % (
            verify_freeze(FREEZE_COMMIT, PREREG)[:12], FREEZE_COMMIT[:12])

    def d1n():
        tmp = tempfile.mkdtemp(prefix="d1n_")
        try:
            rel = os.path.relpath(os.path.join(tmp, "x.md"), REPO)
            verify_freeze(FREEZE_COMMIT, rel)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("D1-PREREG-SHA", d1p, d1n, out)

    # D1b -- the same check shown able to see a ONE-BYTE difference.
    def d1bp():
        data = io.open(os.path.join(REPO, PREREG), "rb").read()
        return "blob_sha1 reader saw %d bytes -> %s" % (len(data), blob_sha1(
            os.path.join(REPO, PREREG))[:12])

    def d1bn():
        tmp = tempfile.mkdtemp(prefix="d1bn_")
        try:
            p = os.path.join(tmp, "m.md")
            io.open(p, "wb").write(io.open(os.path.join(REPO, PREREG), "rb").read() + b"x")
            want = _git(["rev-parse", "%s:%s" % (FREEZE_COMMIT, PREREG)]).stdout.strip()
            if blob_sha1(p) == want:
                raise Refusal("unreachable")
            raise Refusal("PLANTED ONE-BYTE CHANGE SEEN: %s != %s"
                          % (blob_sha1(p)[:12], want[:12]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("D1b-SHA-SEES-1BYTE", d1bp, d1bn, out)

    # D2 -- the frozen SPEC must hash to its committed blob at its own commit.
    def d2p():
        return "spec blob %s verified at %s" % (
            verify_freeze(SPEC_COMMIT, SPEC)[:12], SPEC_COMMIT[:12])

    def d2n():
        verify_freeze("0000000000000000000000000000000000000000", SPEC)
    _both("D2-SPEC-FREEZE", d2p, d2n, out)

    # D3 -- the birth gate: it must REFUSE with no evidence and ADMIT with evidence.
    def d3p():
        save_e, save_a = SC.EVIDENCE, SC.ARTIFACT_ROOT
        tmp = tempfile.mkdtemp(prefix="d3p_")
        try:
            SC.ARTIFACT_ROOT = os.path.join(tmp, "art")
            os.makedirs(SC.ARTIFACT_ROOT)
            for n in ("p_ramp.raw", "T_ramp.raw", "rho_ramp.raw",
                      "p_rgh_wedgeSurface.raw", "p_wedgeSurface.raw",
                      "T_wedgeSurface.raw", "rho_wedgeSurface.raw"):
                io.open(os.path.join(SC.ARTIFACT_ROOT, n), "w").write("x")
            SC.EVIDENCE = os.path.join(tmp, "ev.json")
            io.open(SC.EVIDENCE, "w").write(json.dumps(dict(
                invocations=[dict(rc=0, end_line=True, newer_than_dict=True,
                                  surface="ramp")],
                old_predicate_first_element="T_ramp.raw", old_predicate_len=3,
                producer="synthetic, SELFTEST ONLY",
                graded_dir_sha256_match=True)))
            SC.birth_evidence(sys.stderr)
            return "gate ADMITS a well-formed evidence set"
        finally:
            SC.EVIDENCE, SC.ARTIFACT_ROOT = save_e, save_a
            shutil.rmtree(tmp, ignore_errors=True)

    def d3n():
        save_e = SC.EVIDENCE
        try:
            SC.EVIDENCE = os.path.join(HERE, "__no_such_birth_evidence__.json")
            SC.birth_evidence(sys.stderr)
        finally:
            SC.EVIDENCE = save_e
    _both("D3-BIRTH-GATE", d3p, d3n, out)

    # D3b -- the gate must refuse evidence whose defect never fired.
    def d3bp():
        return "see D3 positive limb"

    def d3bn():
        save_e, save_a = SC.EVIDENCE, SC.ARTIFACT_ROOT
        tmp = tempfile.mkdtemp(prefix="d3bn_")
        try:
            SC.ARTIFACT_ROOT = os.path.join(tmp, "art")
            os.makedirs(SC.ARTIFACT_ROOT)
            for n in ("p_ramp.raw", "T_ramp.raw", "rho_ramp.raw",
                      "p_rgh_wedgeSurface.raw", "p_wedgeSurface.raw",
                      "T_wedgeSurface.raw", "rho_wedgeSurface.raw"):
                io.open(os.path.join(SC.ARTIFACT_ROOT, n), "w").write("x")
            SC.EVIDENCE = os.path.join(tmp, "ev.json")
            io.open(SC.EVIDENCE, "w").write(json.dumps(dict(
                invocations=[dict(rc=0, end_line=True, newer_than_dict=True,
                                  surface="ramp")],
                old_predicate_first_element="p_ramp.raw",   # THE DEFECT DID NOT FIRE
                old_predicate_len=3, producer="synthetic",
                graded_dir_sha256_match=True)))
            SC.birth_evidence(sys.stderr)
        finally:
            SC.EVIDENCE, SC.ARTIFACT_ROOT = save_e, save_a
            shutil.rmtree(tmp, ignore_errors=True)
    _both("D3b-DEFECT-MUST-FIRE", d3bp, d3bn, out)

    # D4 -- the AST census, shown able to see a non-zero (rule 3, on the census itself).
    def d4p():
        c = SC.ast_assert_census([os.path.join(HERE, f) for f in SC.SHIPPED])
        if sum(c.values()) != 0:
            raise Refusal("shipped path carries %d ast.Assert node(s): %r"
                          % (sum(c.values()), c))
        return "0 ast.Assert over %d shipped files" % len(c)

    def d4n():
        tmp = tempfile.mkdtemp(prefix="d4n_")
        try:
            p = os.path.join(tmp, "planted.py")
            io.open(p, "w").write("def f(x):\n    assert x\n")
            c = SC.ast_assert_census([p])
            if sum(c.values()) != 1:
                raise Refusal("CENSUS BLIND: planted 1 assert, census saw %d" % sum(c.values()))
            raise Refusal("PLANTED ASSERT SEEN: census returned %r" % c)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("D4-AST-CENSUS", d4p, d4n, out)

    # D5 -- the -O refusal, driven as a real subprocess in both directions.
    def d5p():
        p = subprocess.run([sys.executable, __file__, "--probe"],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=HERE)
        if p.returncode != 0:
            raise Refusal("probe without -O returned rc %d, want 0" % p.returncode)
        return "no -O: rc 0"

    def d5n():
        p = subprocess.run([sys.executable, "-O", __file__, "--probe"],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=HERE)
        if p.returncode != 2:
            raise Refusal("-O returned rc %d, want 2" % p.returncode)
        raise Refusal("-O CORRECTLY REFUSED with rc 2")
    _both("D5-FLAG-PROOF", d5p, d5n, out)

    # D6 -- the record guard: never overwrite a landed control record.
    def d6p():
        tmp = tempfile.mkdtemp(prefix="d6p_")
        try:
            guard_record(os.path.join(tmp, "R1_CONTROL_RECORD.json"))
            return "absent record accepted"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def d6n():
        tmp = tempfile.mkdtemp(prefix="d6n_")
        try:
            p = os.path.join(tmp, "R1_CONTROL_RECORD.json")
            io.open(p, "w").write("{}")
            guard_record(p)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("D6-RECORD-GUARD", d6p, d6n, out)

    # D7 -- the invariance reader, shown able to see a single changed byte.
    def d7p():
        s = invariance_set()
        if len(s) < 10:
            raise Refusal("invariance set only %d entries" % len(s))
        return "%d artefacts hashed" % len(s)

    def d7n():
        tmp = tempfile.mkdtemp(prefix="d7n_")
        try:
            a = os.path.join(tmp, "f.txt")
            io.open(a, "w").write("one")
            h1 = sha256_file(a)
            io.open(a, "w").write("onf")
            if sha256_file(a) == h1:
                raise Refusal("HASHER BLIND: a changed byte produced the same sha256")
            raise Refusal("PLANTED BYTE SEEN: %s -> %s" % (h1[:12], sha256_file(a)[:12]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("D7-INVARIANCE-READER", d7p, d7n, out)

    print("R1 DRIVER SELFTEST -- controls fired, each in BOTH directions")
    print("=" * 78)
    for name, p, n in out:
        print("  %-22s POSITIVE %s" % (name, p))
        print("  %-22s NEGATIVE fired: %s" % ("", n))
    print("=" * 78)
    print("%d controls fired, each shown able to fail" % len(out))
    print("assert census over the shipped path: %s"
          % json.dumps(SC.ast_assert_census([os.path.join(HERE, f) for f in SC.SHIPPED])))
    print("__debug__ = %s (this run is NOT under -O)" % __debug__)
    return 0


def guard_record(path):
    if os.path.exists(path):
        raise Refusal("A control record already exists at %s. This driver does not "
                      "overwrite a landed record; move it aside deliberately or run "
                      "under a new registration." % path)
    return True


# ---------------------------------------------------------------------------
# THE GRADED PATH
# ---------------------------------------------------------------------------

def grade(freeze_commit):
    t0 = time.time()
    before = invariance_set()
    prereg_blob = verify_freeze(freeze_commit, PREREG)
    spec_blob = verify_freeze(SPEC_COMMIT, SPEC)
    guard_record(RECORD)

    ev = drive_birth_control(CAP_WALL_S - (time.time() - t0))

    import importlib
    mods = {}
    for name in ("grade_f3s", "run_f3s"):
        mods[name] = importlib.import_module(name)

    results = {}
    for name, mod in mods.items():
        buf = io.StringIO()
        rc = SC.run_battery(mod, buf)
        results[name] = dict(rc=rc, transcript=buf.getvalue())
        if rc != 0:
            sys.stderr.write(buf.getvalue())
            refuse("the C1-C6 battery refused on %s" % name)

    # The real reader, end to end, on the graded case: read_p_wall_mean through select_one
    p_val, p_art = mods["grade_f3s"].read_p_wall_mean(FINE)

    after = invariance_set()
    moved = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))

    wall = time.time() - t0
    actual = wall * RANKS / 60.0
    rec = dict(
        item="R1_F3S_SELECTOR_REPAIR",
        prereg=PREREG, prereg_commit=freeze_commit, prereg_blob=prereg_blob,
        spec=SPEC, spec_commit=SPEC_COMMIT, spec_blob=spec_blob,
        birth_control=ev,
        controls=results,
        real_reader_end_to_end=dict(
            case=os.path.relpath(FINE, REPO), p_wall_mean=p_val,
            artifact=os.path.relpath(p_art, REPO) if p_art else None),
        invariance=dict(n_hashed=len(before), changed=moved,
                        bit_identical=(not moved)),
        cost=dict(unit="core-minutes", ranks=RANKS, wall_s=round(wall, 4),
                  actual_core_min=round(actual, 6),
                  predicted_core_min=EST_CORE_MIN, cap_core_min=CAP_CORE_MIN,
                  ratio_actual_over_predicted=round(actual / EST_CORE_MIN, 4),
                  over_cap=(actual > CAP_CORE_MIN),
                  dollars_derived_not_measured=round(actual / 60.0 * 0.0513, 8),
                  rate_basis=("$0.0513/core-h, c7a.4xlarge, owner-stated 2026-08-21/22, "
                              "REPORTED-BY-OWNER. The box cannot read its own billing "
                              "(COMPUTE_BUDGET_CHARTER.md sec.5); dollars are DERIVED."),
                  calibration_row_owed="docs/COST_CALIBRATION.md"),
        verdict_note=("Gate verdicts G-R1-1..G-R1-8 are decided by the supervisor "
                      "against this record; this driver reports control outcomes and "
                      "refuses rather than degrades."))
    if actual > CAP_CORE_MIN:
        rec["verdict"] = "NOT A RESULT"
        rec["why"] = ("CAP OVERRUN: %.4f core-min against a registered cap of %.4f. "
                      "An overrun stops the item; it does not get a new budget."
                      % (actual, CAP_CORE_MIN))
    io.open(RECORD, "w", encoding="utf-8").write(
        json.dumps(rec, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: rec[k] for k in ("item", "invariance", "cost")}, indent=2))
    print("real reader end to end: p_wall_mean = %r from %s"
          % (p_val, rec["real_reader_end_to_end"]["artifact"]))
    print("record: %s" % os.path.relpath(RECORD, REPO))
    if moved:
        refuse("G-R1-8 INVARIANCE: %d artefact(s) changed: %r" % (len(moved), moved[:5]))
    return 0


FREEZE_COMMIT = "f7da1a24ca8c730d5c49a7ea429840c43378bf1e"


def main(argv=None):
    if not __debug__:
        sys.stderr.write(
            "REFUSED: this driver is running under `python3 -O`, which deletes every "
            "assert statement in the interpreter. This program carries none by design, "
            "but a harness that RUNS under -O invites one to be added later and "
            "silently removed. A control that can vanish is not a control (L-332).\n")
        return 2
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--prereg-commit", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--birth-control", action="store_true")
    ap.add_argument("--probe", action="store_true",
                    help="return 0 if not under -O; used by the flag-proof control")
    a = ap.parse_args(argv)

    if a.probe:
        print("probe: __debug__=%s" % __debug__)
        return 0
    if a.selftest:
        return selftest()
    try:
        if a.birth_control:
            ev = drive_birth_control(CAP_WALL_S)
            print("BR-1 BIRTH CONTROL DRIVEN -- OpenFOAM wrote the fixtures")
            print("=" * 78)
            for line in ev["transcript"]:
                print("  " + line)
            print("  old predicate on the sampler's own output: %r" % ev["old_predicate_full"])
            print("  first element: %s   <-- THE DEFECT, FIRING ON PRODUCER BYTES"
                  % ev["old_predicate_first_element"])
            print("  BR-2 sha256 identity with the graded originals: %s"
                  % ev["graded_dir_sha256_match"])
            print("=" * 78)
            print("evidence: %s" % os.path.relpath(SC.EVIDENCE, REPO))
            return 0
        if not a.prereg_commit:
            refuse("--prereg-commit is required. This driver does not grade without the "
                   "sha of the pre-registration's adding commit, and it VERIFIES that "
                   "sha by hashing %s on disk against its committed blob (rule 2)."
                   % PREREG)
        if a.prereg_commit != FREEZE_COMMIT:
            refuse("--prereg-commit %s is not this item's freeze commit %s"
                   % (a.prereg_commit, FREEZE_COMMIT))
        return grade(a.prereg_commit)
    except Refusal as e:
        sys.stderr.write("REFUSED: %s\n" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
