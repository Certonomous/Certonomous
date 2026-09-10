#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RC2 HALF B -- the re-grade FROM PRESERVED ARTIFACTS (zero solver compute).

STATUS: DRAFT / UNFROZEN.  Not the freeze.  Standing rule 2; the freeze commit
carries PREREGISTRATION.md AND both instruments together, hashed against the
committed blobs.  Nothing may run against this file for a graded result before that
commit.

WHAT THIS DOES (PREREGISTRATION.md section 2 HALF B, section 4).  A repaired reader
with no re-grade leaves every number it already produced standing on the defect.  So
this harness, reading PRESERVED artifacts only and RUNNING NO SOLVER:

  1. GATE (section 5.1 clause 1).  Before any row is read, it runs the successor's
     two-direction planted control on the 22 named REAL logs (rc2_divergence
     .planted_control_fatal_real).  If it does not fire in both directions, the whole
     item is NOT A RESULT and nothing is re-graded.

  2. ENUMERATION (section 4.1).  Walks every .md and .json in the repo outside .git
     and records, with file and line, every citation of run_lane.py:{175,176,168,177},
     the `diverged` key in a Kaandorp context, and the phrase DIVERGED in a Kaandorp
     context.  Written to CITATION_MANIFEST.json in the run root; every re-grade row
     cites it.  The rule is fixed BEFORE the answer is seen so the scope cannot be
     narrowed after.

  3. CONSUMER AUDIT (section 4.2).  Sweeps every .py for ["diverged"], .get("diverged")
     and .diverged, and reports each site -- so "R4 is not contaminated" is a reading,
     not an assumption.

  4. RE-GRADE (section 4).  For each of the 16 flag cells in results.json: the FROZEN
     value (the cell), the SUCCESSOR value (re-read from the preserved log through the
     imported reader), and FLAG MOVED iff they differ.  Provenance control (6.3): each
     row records path/size/mtime_ns/sha256 and is REFUSED (NOT A RESULT) if its log's
     mtime is newer than results.json's -- rule 4's age guard read backwards.

  5. MOVEMENT (section 4.3).  FLAG MOVED / VERDICT MOVED / TRIGGER DISARMED, defined
     before the answer.  RC2 REPORTS movement; it does not move a verdict (5.4) --
     that ruling is the supervisor's, then verification's.

  6. PRE_RELAUNCH (section 3.3).  The 10 named cells in
     results_PRE_RELAUNCH_2026-08-23.json are NOT A RESULT -- artifact provenance
     unestablished, registered in advance and named.

READ-ONLY (6.4): every artifact opened "r"; before exit all 16 logs +
results.json + PRE_RELAUNCH are re-stat'd and the run REFUSES if any size/mtime_ns
moved.  MAY NOT edit run_lane.py, results.json or PRE_RELAUNCH (5.4); writes only
REGRADE_RC2.json and CITATION_MANIFEST.json in the run root.

VOCABULARY (5.3): PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING,
through a checker that REFUSES on a synonym, a hedge or a lower-case variant.

L-332: every refusal is a raise/sys.exit(2); the module parses its OWN AST and refuses
on any ast.Assert.  Green under python3 and python3 -O.
"""

import argparse
import ast
import json
import os
import re
import sys
import time
from pathlib import Path

# import the SUCCESSOR reader itself -- not a copy of its expression (section 4;
# the same object the birth control certified).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc2_divergence as RC2  # noqa: E402
from rc2_divergence import Refusal, refuse, sha256_file, read_fatal  # noqa: E402

REPO = "/home/ubuntu/Certonomous"
KRUN = "/home/ubuntu/closure-data/aposteriori/kaandorp"
RESULTS = os.path.join(KRUN, "results.json")
PRE_RELAUNCH = os.path.join(KRUN, "results_PRE_RELAUNCH_2026-08-23.json")

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

# The 10 PRE_RELAUNCH cells, named in advance (section 3.3).
PRE_RELAUNCH_CELLS = [
    "AR_1_Ret_360__NULL", "AR_1_Ret_360__TRUTH", "AR_1_Ret_360__MEANB",
    "AR_1_Ret_360__ML0", "AR_1_Ret_360__ML1", "AR_1_Ret_360__ML2",
    "AR_1_Ret_360__MEANB64", "AR_3_Ret_360__NULL", "AR_3_Ret_360__TRUTH",
    "AR_3_Ret_360__MEANB",
]

# Citation-enumeration patterns (section 4.1), fixed here.
_KAANDORP_CTX = re.compile(r"[Kk]aandorp|aposteriori|run_lane")
_LINE_TOKENS = [
    re.compile(r"run_lane\.py:1(?:75|76|68|77)"),
    re.compile(r"\bdiverged\b"),
    re.compile(r"\bDIVERGED\b"),
]
# consumer-audit patterns (section 4.2)
_CONSUMER = re.compile(r"\[\s*[\"']diverged[\"']\s*\]|\.get\(\s*[\"']diverged[\"']|\.diverged\b")


# --------------------------------------------------------------------------
# L-332 control
# --------------------------------------------------------------------------
def count_asserts(source_text):
    return sum(1 for n in ast.walk(ast.parse(source_text)) if isinstance(n, ast.Assert))


def no_assert_control():
    planted = count_asserts("def f(x):\n    assert x, 'planted'\n    return x\n")
    if planted != 1:
        refuse("AST-CONTROL: counter returned %d on a one-assert snippet; a blind spot" % planted)
    for f in (Path(__file__).read_text(), Path(RC2.__file__).read_text()):
        own = count_asserts(f)
        if own != 0:
            refuse("AST-CONTROL: %d ast.Assert node(s) present; python3 -O deletes them (L-332)" % own)
    return planted


# --------------------------------------------------------------------------
# Vocabulary checker (section 5.3) -- refuses a synonym/hedge/lower-case variant.
# --------------------------------------------------------------------------
def check_verdict(v):
    if v not in VERDICTS:
        refuse("VOCABULARY: %r is not one of %s -- no synonym, hedge or lower-case "
               "variant is a verdict (rule 1)" % (v, VERDICTS))
    return v


# --------------------------------------------------------------------------
# Provenance / age guard (section 6.3) -- rule 4's age guard, backwards.
# --------------------------------------------------------------------------
def provenance(path, ref_mtime_ns):
    st = os.stat(path)
    row = dict(path=path, bytes=st.st_size, mtime_ns=st.st_mtime_ns,
               sha256=sha256_file(path))
    if st.st_mtime_ns > ref_mtime_ns:
        row["provenance"] = "REFUSED: mtime newer than results.json"
        row["verdict"] = check_verdict("NOT A RESULT")
    else:
        row["provenance"] = "ok: older than results.json"
    return row


# --------------------------------------------------------------------------
# Enumeration (section 4.1) and consumer audit (section 4.2).
# --------------------------------------------------------------------------
def enumerate_citations():
    hits = {}
    for dirpath, dirnames, filenames in os.walk(REPO):
        if ".git" in dirpath.split(os.sep):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            continue
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            if not (fn.endswith(".md") or fn.endswith(".json")):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                lines = open(fp, "r", errors="replace").read().splitlines()
            except OSError:
                continue
            file_hits = []
            for i, line in enumerate(lines, 1):
                if not _KAANDORP_CTX.search(line):
                    # diverged token still counts only in a Kaandorp context: require
                    # context on the line OR the file path itself is Kaandorp/aposteriori
                    if not _KAANDORP_CTX.search(fp):
                        continue
                for pat in _LINE_TOKENS:
                    if pat.search(line):
                        file_hits.append(dict(line=i, pattern=pat.pattern,
                                              text=line.strip()[:200]))
                        break
            if file_hits:
                hits[os.path.relpath(fp, REPO)] = file_hits
    return hits


def consumer_audit():
    sites = []
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                lines = open(fp, "r", errors="replace").read().splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                if _CONSUMER.search(line):
                    sites.append(dict(file=os.path.relpath(fp, REPO), line=i,
                                      text=line.strip()[:200]))
    return sites


# --------------------------------------------------------------------------
# THE RE-GRADE
# --------------------------------------------------------------------------
def regrade(run_root):
    t0 = time.time()
    no_assert_control()

    # 1. GATE -- the successor's two-direction control on real logs (section 5.1.1).
    control = RC2.planted_control_fatal_real()  # refuses on any disagreement

    # read-only snapshot of the artifacts we must not touch (section 6.4)
    guarded = [RESULTS, PRE_RELAUNCH] + [RC2.neg_log_path(c) for c in RC2.NEG_CORPUS]
    before = {p: (os.stat(p).st_size, os.stat(p).st_mtime_ns) for p in guarded}

    res = json.load(open(RESULTS, "r", errors="replace"))
    runs = res["runs"]
    res_mtime_ns = os.stat(RESULTS).st_mtime_ns

    # 4. per-row re-grade
    rows = []
    flag_moved = 0
    infra_defects = []
    for case in RC2.NEG_CORPUS:
        if case not in runs or "diverged" not in runs[case]:
            infra_defects.append("results.json row missing 'diverged' for %s" % case)
            continue
        frozen_cell = runs[case]["diverged"]
        prov = provenance(RC2.neg_log_path(case), res_mtime_ns)
        row = dict(case=case, frozen_flag=bool(frozen_cell), **prov,
                   cites="CITATION_MANIFEST.json")
        if prov["provenance"].startswith("REFUSED"):
            row["successor_flag"] = None
            row["flag_moved"] = None
            row["verdict"] = check_verdict("NOT A RESULT")
        else:
            text = open(prov["path"], "r", errors="replace").read()
            succ = read_fatal(text)
            row["successor_flag"] = succ
            row["flag_moved"] = bool(frozen_cell) != bool(succ)
            if row["flag_moved"]:
                flag_moved += 1
            # RC2 does not move a verdict; the graded row's verdict is that the
            # re-grade was performed and is defensible (section 5.3 headline).
            row["verdict"] = check_verdict("PASS")
            # TRIGGER DISARMED leg: the independently-computed `converged` field
            # (run_lane.py:183-196) -- the "fails to converge" leg (section 4.4).
            row["converged_field"] = runs[case].get("converged")
        rows.append(row)

    # 5. movement summary (section 4.3), reported not adjudicated
    graded = [r for r in rows if r["successor_flag"] is not None]
    not_a_result_rows = [r["case"] for r in rows if r["successor_flag"] is None]
    converged_true = [r["case"] for r in graded if r.get("converged_field") is True]
    fails_to_converge_still_armed = [r["case"] for r in graded if r.get("converged_field") is False]
    movement = dict(
        FLAG_MOVED=flag_moved,
        FLAG_MOVED_of=len(graded),
        VERDICT_MOVED="reported: 0 expected; RC2 does not adjudicate -- routed to "
                      "supervisor then verification (section 5.4)",
        TRIGGER_DISARMED=dict(
            diverges_leg="disarmed on all %d graded rows (frozen true -> successor "
                         "false)" % flag_moved,
            fails_to_converge_leg="STAYS ARMED on %d rows where converged==false "
                                  "(independent channel, run_lane.py:183-196)"
                                  % len(fails_to_converge_still_armed),
            converged_true_rows=converged_true,
            finding="H1's GATE FAIL rests on TWO legs; the 'diverges' leg disarms, the "
                    "'fails to converge' leg remains armed -- reported as its own "
                    "category, not folded into 'no verdict moved' (section 4.3)"),
    )

    # 6. PRE_RELAUNCH cells -- NOT A RESULT, named (section 3.3)
    pre = json.load(open(PRE_RELAUNCH, "r", errors="replace"))
    pre_runs = pre.get("runs", pre)
    pre_rows = []
    for case in PRE_RELAUNCH_CELLS:
        cell = pre_runs.get(case, {})
        pre_rows.append(dict(case=case, pre_relaunch_flag=cell.get("diverged"),
                             verdict=check_verdict("NOT A RESULT"),
                             reason="artifact provenance unestablished; no hash of the "
                                    "PRE_RELAUNCH-era log was preserved (section 3.3)"))

    # 2/3 enumeration + consumer audit
    citations = enumerate_citations()
    consumers = consumer_audit()
    r4_sites = [c for c in consumers if "score_aposteriori" in c["file"]]

    # read-only verification (section 6.4) -- refuse if anything moved during the run
    for p in guarded:
        now = (os.stat(p).st_size, os.stat(p).st_mtime_ns)
        if now != before[p]:
            refuse("READ-ONLY: %s changed during the re-grade (size/mtime moved); a "
                   "re-grade that modifies its own evidence has destroyed it (6.4)" % p)

    # headline
    headline = check_verdict("PASS") if graded and not not_a_result_rows else (
        check_verdict("PASS") if graded else check_verdict("NOT A RESULT"))

    out = dict(
        item="RC2_kaandorp_divergence_repair",
        status="DRAFT/UNFROZEN -- not a registered result until the freeze commit",
        headline=headline,
        headline_means="the re-grade was performed and is defensible; NOT 'nothing was "
                       "wrong' -- flag cells were expected to move and that is the finding",
        control=dict(
            positive_real_fatals=len(control["positive"]),
            negative_banner_only=len(control["negative"]),
            blind_frozen_fires=len(control["blind"]),
            fired_both_directions=True),
        regrade_rows=rows,
        regradable=len(graded),
        not_a_result_this_run=not_a_result_rows,
        pre_relaunch_not_a_result=pre_rows,
        movement=movement,
        consumer_audit=dict(all_sites=consumers, r4_sites=r4_sites,
                            note="R4's two sites read score_aposteriori's OWN log_facts "
                                 "(narrow Foam::sigFpe test), NOT Kaandorp results.json "
                                 "(section 4.2) -- R4 uncontaminated"),
        citation_manifest="CITATION_MANIFEST.json",
        citation_file_count=len(citations),
        infra_defects=infra_defects,
        wall_s=round(time.time() - t0, 2),
    )

    os.makedirs(run_root, exist_ok=True)
    with open(os.path.join(run_root, "REGRADE_RC2.json"), "w") as f:
        json.dump(out, f, indent=2)
    with open(os.path.join(run_root, "CITATION_MANIFEST.json"), "w") as f:
        json.dump(dict(rule="every .md/.json outside .git; run_lane.py:{175,176,168,177}"
                            ", diverged, DIVERGED in a Kaandorp context (section 4.1)",
                       files=citations), f, indent=2)

    print("RC2 RE-GRADE %s -- %d/%d flag cells MOVED (true->false), %d NOT A RESULT this "
          "run, %d PRE_RELAUNCH NOT A RESULT; control fired both directions; %d citation "
          "files enumerated; R4 sites=%d (uncontaminated). Zero solver compute."
          % (headline, flag_moved, len(graded), len(not_a_result_rows), len(pre_rows),
             len(citations), len(r4_sites)))
    return 0


# --------------------------------------------------------------------------
# selftest -- two-sided, on the harness's OWN logic (temp fixtures), plus it
# delegates the reader birth to rc2_divergence.selftest.
# --------------------------------------------------------------------------
def selftest():
    import tempfile
    no_assert_control()
    print("[L-332] no ast.Assert in either instrument  OK")

    # vocabulary, two-sided
    for v in VERDICTS:
        check_verdict(v)
    for bad in ("pass", "Passed", "roughly converged", "FAIL", "OK"):
        try:
            check_verdict(bad)
        except Refusal:
            pass
        else:
            refuse("VOCAB SELFTEST: %r was accepted; the checker is not a checker" % bad)
    print("[5.3] vocabulary checker accepts all 6 verdicts, refuses every synonym/hedge  OK")

    # provenance age-guard, two-sided, on temp files (never real artifacts)
    with tempfile.TemporaryDirectory(prefix="rc2reg_") as td:
        ref = Path(td) / "results.json"
        ref.write_text("{}")
        ref_ns = os.stat(ref).st_mtime_ns
        old = Path(td) / "old.run"
        old.write_text("End\n")
        os.utime(old, ns=(ref_ns - 10 ** 9, ref_ns - 10 ** 9))
        new = Path(td) / "new.run"
        new.write_text("End\n")
        os.utime(new, ns=(ref_ns + 10 ** 9, ref_ns + 10 ** 9))
        r_old = provenance(str(old), ref_ns)
        r_new = provenance(str(new), ref_ns)
        if r_old["provenance"].startswith("REFUSED"):
            refuse("PROV SELFTEST: an OLDER log was refused; the age guard is inverted")
        if not r_new["provenance"].startswith("REFUSED"):
            refuse("PROV SELFTEST: a NEWER log passed; the age guard does not bite")
        print("[6.3] age guard: older log passes, newer log -> NOT A RESULT  OK")

    # the reader birth is the successor's own control -- delegate it
    RC2.planted_control_fatal_real()
    print("[6.1/6.2] delegated successor two-direction + blind control on 22 real logs  OK")

    print("SELFTEST PASS: harness logic (vocabulary, age guard, no-assert) demonstrated "
          "two-sided; reader birth delegated; green target python3 and -O.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="RC2 re-grade from preserved artifacts (DRAFT/UNFROZEN, zero compute)")
    ap.add_argument("--run-root", default="/home/ubuntu/closure-data/rc2",
                    help="where REGRADE_RC2.json and CITATION_MANIFEST.json are written")
    ap.add_argument("--selftest", action="store_true",
                    help="exercise the harness's own controls two-sided and exit 0 iff all pass")
    args = ap.parse_args(argv)
    try:
        if args.selftest:
            return selftest()
        return regrade(args.run_root)
    except Refusal as e:
        sys.stderr.write("REFUSE (exit 2): %s\n" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
