#!/usr/bin/env python3
"""
check_exhaustion_evidence.py -- the STANDING INSTRUMENT for VERIFICATION_CHARTER
§2bc, Sanaa's EXHAUSTION-EVIDENCE ACCEPTANCE GATE, which strengthens §2ay.

WHY THIS EXISTS
---------------
§2ay governs the ACTIVE case: a rung that GATE FAILs or lands NOT A RESULT with a
live successor still climbing the ladder.  §2bc governs the TERMINAL case: a
GATE FAIL / NOT A RESULT that is being ACCEPTED AS FINAL, with no further rung to
run.  A terminal fail is the most consequential label the lab writes, because it
closes the question -- and a terminal fail that was declared before the obvious
alternatives were ruled out is exactly the confounded outcome D6RF9 was
(commits e3d9cd8f / 6c9f0f26): a timeout dressed as a measured floor-miss, a
crash dressed as a capability finding.  §2bc therefore requires that a terminal
fail carry, on record and by resolvable reference, the evidence that:

  * the NUMERICS LADDER was driven to exhaustion (it is not a solver artefact);
  * the MODEL SETUP / boundary conditions were ruled out (it is not a setup bug);
  * and, when the run did NOT complete, that a CAPABILITY RULE-OUT exists (an
    incomplete run cannot by itself measure a floor -- rule 4).

Two named exemptions are recognised, each of which still demands its own
resolvable evidence:
  * measured_capability_limit -- the fail IS the measured capability limit
    (a capability_rule_out or an exemption record must resolve);
  * closure_challenge_model_accuracy_miss -- an accepted model-accuracy miss on
    the closure-challenge benchmark (the numerics-ladder exhaustion or an
    exemption record must resolve).

WHAT IT ENFORCES
----------------
Usage:  check_exhaustion_evidence.py <record.json>

The record is a JSON object that either CARRIES an "exhaustion_evidence" block
under that top-level key, or IS the block (recognised by a top-level "verdict").
Schema of the block:

  "exhaustion_evidence": {
    "verdict": "GATE FAIL" | "NOT A RESULT",
    "terminal": true | false,
    "completes": true | false,          # false => a non-completing run => a
                                        #          capability rule-out is required
    "numerics_ladder_exhausted": "<path or git-sha ref>",
    "model_setup_ruled_out":     "<path or git-sha ref>",
    "capability_rule_out":       "<path or git-sha ref>",  # required iff completes==false
    "terminal_exemption": null | "measured_capability_limit"
                               | "closure_challenge_model_accuracy_miss",
    "exemption_ref": "<path or git-sha ref>"               # required iff terminal_exemption set
  }

APPLICABILITY (PASS, exit 0 -- the gate does not fire):
  * verdict not in {"GATE FAIL","NOT A RESULT"} -> PASS ("not a terminal fail,
    not applicable").
  * terminal is not true -> PASS ("not terminal; an active successor is §2ay's
    domain, out of §2bc scope").

REFUSAL RULES (exit 2, the message names the missing/failing component) for a
TERMINAL GATE FAIL / NOT A RESULT:
  * no exhaustion_evidence block at all -> REFUSE.
  * terminal_exemption set:
      - value not one of the two allowed strings -> REFUSE ("unknown
        terminal_exemption").
      - "measured_capability_limit": capability_rule_out OR exemption_ref must
        resolve -> else REFUSE.
      - "closure_challenge_model_accuracy_miss": numerics_ladder_exhausted OR
        exemption_ref must resolve -> else REFUSE.
  * no exemption -- every applicable component must be PRESENT and RESOLVE:
      - numerics_ladder_exhausted present and resolving -> else REFUSE.
      - model_setup_ruled_out present and resolving -> else REFUSE.
      - completes==false: capability_rule_out present and resolving -> else REFUSE.
  * otherwise PASS (exit 0): "PASS: terminal <verdict> carries valid exhaustion
    evidence (...)".

A REF RESOLVES when either:
  (a) it is an existing file/dir path, checked AS-GIVEN, relative to the record's
      own directory, and relative to cwd; OR
  (b) it is a 7-40 char lowercase-hex string that
      `git rev-parse --verify --quiet <ref>^{commit}` confirms exists (git is run
      in the repository root; all errors are swallowed).
Otherwise it does not resolve.

WHAT THIS CHECK CANNOT SEE  (stated because a check that overstates its reach is
worse than none -- mirrors check_ladder_preflight.py's honest-boundary note):
  * whether the referenced record's BYTES actually demonstrate what they claim.
    This gate verifies that each ref RESOLVES (the file/dir exists, or the commit
    exists) and that the block STRUCTURE is complete; it does NOT open the
    referenced numerics-ladder record and confirm the ladder was truly driven to
    exhaustion, nor read the capability rule-out to confirm the floor was
    measured rather than assumed.  A resolving ref that points at an empty or
    fabricated record is a deeper integrity fault that the supervisor's
    NON-DELEGABLE §3 backstops catch: crash-triage (a crash is a finding until
    triage says otherwise) and big-claim verification before belief.  The
    EXISTENCE of the evidence is proven here; a human reads its content.
  * whether a git-sha ref points at the commit that is actually IN FORCE for this
    verdict.  It confirms the commit exists, not that it is the right one.

This file is diff-read by the verification-supervisor before its output is
believed (SUPERVISION §3 check 1); it writes nothing outside its own scratch
fixture tree and it moves no verdict.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

EXIT_OK, EXIT_REFUSE, EXIT_VIOLATION = 0, 2, 3

TERMINAL_FAILS = ("GATE FAIL", "NOT A RESULT")
ALLOWED_EXEMPTIONS = ("measured_capability_limit",
                      "closure_challenge_model_accuracy_miss")
# the keys whose presence makes a whole-object record count as an actual
# exhaustion_evidence block (verdict/terminal/completes alone describe the run,
# not the exhaustion evidence).
EVIDENCE_KEYS = ("numerics_ladder_exhausted", "model_setup_ruled_out",
                 "capability_rule_out", "terminal_exemption", "exemption_ref")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def git(repo: str, *args: str) -> tuple[int, str, str]:
    """Run git in `repo`, swallowing failures into the return code."""
    try:
        r = subprocess.run(["git", "-C", repo, *args],
                           capture_output=True, text=True)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except OSError:
        return 1, "", "git unavailable"


def repo_root(start: str) -> str:
    """The git toplevel that contains `start`, else cwd (so git-sha resolution
    has a repository to ask; a non-repo start simply never resolves a sha)."""
    rc, out, _ = git(start, "rev-parse", "--show-toplevel")
    return out if rc == 0 and out else os.getcwd()


def ref_resolves(record_dir: str, repo: str, ref) -> bool:
    """A ref resolves iff it is an existing path (as-given / relative to the
    record's own directory / relative to cwd), OR a 7-40 char lowercase-hex
    string naming a commit that exists in `repo`."""
    if not ref or not isinstance(ref, str):
        return False
    cands = [ref, os.path.join(record_dir, ref), os.path.join(os.getcwd(), ref)]
    if any(os.path.exists(c) for c in cands):
        return True
    if SHA_RE.match(ref):
        rc, _, _ = git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
        if rc == 0:
            return True
    return False


def find_block(obj: dict) -> tuple[dict, bool]:
    """(block, has_evidence_block).  The block is the dict holding verdict /
    terminal / the evidence components: the nested "exhaustion_evidence" object
    if present, else the whole record when it carries a top-level "verdict".

    has_evidence_block is True when a nested "exhaustion_evidence" object exists,
    OR the whole-object block carries at least one EVIDENCE_KEY -- a record that
    states only verdict/terminal/completes has NO exhaustion evidence to grade."""
    ee = obj.get("exhaustion_evidence")
    if isinstance(ee, dict):
        return ee, True
    if "verdict" in obj:
        return obj, any(k in obj for k in EVIDENCE_KEYS)
    return obj, False


# --------------------------------------------------------------------------
# the check
# --------------------------------------------------------------------------
def check_record(path: str) -> tuple[int, str]:
    """Validate one exhaustion-evidence record.  Returns (exit_code, final_line)."""
    if not os.path.exists(path):
        return EXIT_REFUSE, f"REFUSE: {path} record does not exist on disk"
    try:
        with open(path, errors="replace") as f:
            obj = json.load(f)
    except (OSError, ValueError) as e:
        return EXIT_REFUSE, f"REFUSE: {path} record unparseable ({e})"
    if not isinstance(obj, dict):
        return EXIT_REFUSE, f"REFUSE: {path} record is not a JSON object"

    record_dir = os.path.dirname(os.path.abspath(path))
    repo = repo_root(record_dir)

    block, has_block = find_block(obj)
    verdict = block.get("verdict")
    terminal = block.get("terminal")

    # ---- APPLICABILITY -----------------------------------------------------
    if verdict not in TERMINAL_FAILS:
        return EXIT_OK, (f"PASS: verdict {verdict!r} is not a terminal fail; "
                         f"§2bc not applicable")
    if terminal is not True:
        return EXIT_OK, (f"PASS: {verdict} is not terminal; an active successor is "
                         f"§2ay's domain, out of §2bc scope")

    # ---- from here: a TERMINAL GATE FAIL / NOT A RESULT --------------------
    if not has_block:
        return EXIT_REFUSE, (f"REFUSE: terminal {verdict} carries no "
                             f"exhaustion_evidence block (§2bc requires one)")

    def resolves(ref) -> bool:
        return ref_resolves(record_dir, repo, ref)

    def require(key: str) -> tuple[int, str] | None:
        """REFUSE if `key` is absent/empty, or present but non-resolving."""
        val = block.get(key)
        if key not in block or not val:
            return EXIT_REFUSE, f"REFUSE: terminal {verdict} exhaustion evidence: {key} absent"
        if not resolves(val):
            return EXIT_REFUSE, (f"REFUSE: terminal {verdict} exhaustion evidence: "
                                 f"{key} does not resolve ({val!r})")
        return None

    exemption = block.get("terminal_exemption")

    # ---- EXEMPTION PATH ----------------------------------------------------
    if exemption is not None:
        if exemption not in ALLOWED_EXEMPTIONS:
            return EXIT_REFUSE, (f"REFUSE: terminal {verdict} unknown terminal_exemption "
                                 f"({exemption!r}); allowed: {ALLOWED_EXEMPTIONS}")
        if exemption == "measured_capability_limit":
            if not (resolves(block.get("capability_rule_out"))
                    or resolves(block.get("exemption_ref"))):
                return EXIT_REFUSE, (f"REFUSE: terminal {verdict} measured_capability_limit "
                                     f"exemption: neither capability_rule_out nor "
                                     f"exemption_ref resolves")
        else:  # closure_challenge_model_accuracy_miss
            if not (resolves(block.get("numerics_ladder_exhausted"))
                    or resolves(block.get("exemption_ref"))):
                return EXIT_REFUSE, (f"REFUSE: terminal {verdict} "
                                     f"closure_challenge_model_accuracy_miss exemption: "
                                     f"neither numerics_ladder_exhausted nor "
                                     f"exemption_ref resolves")
        return EXIT_OK, (f"PASS: terminal {verdict} carries valid exhaustion evidence "
                         f"(via {exemption} exemption)")

    # ---- NO EXEMPTION: every applicable component present AND resolving ----
    for key in ("numerics_ladder_exhausted", "model_setup_ruled_out"):
        bad = require(key)
        if bad is not None:
            return bad
    if block.get("completes") is False:
        bad = require("capability_rule_out")
        if bad is not None:
            return bad
        return EXIT_OK, (f"PASS: terminal {verdict} carries valid exhaustion evidence "
                         f"(non-completing run; numerics + model-setup + "
                         f"capability rule-out all resolve)")
    return EXIT_OK, (f"PASS: terminal {verdict} carries valid exhaustion evidence "
                     f"(numerics-ladder exhaustion + model-setup rule-out resolve)")


# --------------------------------------------------------------------------
# selftest -- the planted control, both directions
# --------------------------------------------------------------------------
def selftest() -> bool:
    """Drive the acceptance gate RED-then-GREEN through THIS FILE's entry point.
    Real temp files back the refs, so the resolve-check is genuinely exercised on
    disk.  Returns True iff every arm hit its expected exit code."""
    print("=" * 78)
    print("PLANTED CONTROL -- VERIFICATION_CHARTER §2bc / rule 3.  Both directions.")
    print("An acceptance gate whose refusal has not been shown able to become a")
    print("pass (and back) is worthless.")
    print("=" * 78)

    me = os.path.abspath(__file__)
    ok = True
    tmp = tempfile.mkdtemp(prefix="exhaustion_evidence_plant_")

    def run_entry(record: dict, fname: str) -> int:
        rp = os.path.join(tmp, fname)
        with open(rp, "w") as f:
            json.dump(record, f)
        r = subprocess.run([sys.executable, me, rp], capture_output=True, text=True)
        return r.returncode

    def arm(label: str, record: dict, want: int, fname: str):
        nonlocal ok
        got = run_entry(record, fname)
        good = (got == want)
        ok = ok and good
        print(f"  {label:56s} -> exit {got}  (want {want})  {'PASS' if good else 'FAIL'}")

    try:
        # REAL ref files on disk (basenames resolve against the record's own dir).
        num_ref = "numerics_ladder.md"
        mod_ref = "model_setup.md"
        cap_ref = "capability_ruleout.md"
        for r in (num_ref, mod_ref, cap_ref):
            with open(os.path.join(tmp, r), "w") as f:
                f.write("ladder driven to exhaustion; see rows.\n")

        # ---- GREEN ---------------------------------------------------------
        arm("GREEN-1 terminal completes=true, numerics+model resolve",
            {"exhaustion_evidence": {
                "verdict": "GATE FAIL", "terminal": True, "completes": True,
                "numerics_ladder_exhausted": num_ref,
                "model_setup_ruled_out": mod_ref}},
            EXIT_OK, "green1.json")

        arm("GREEN-2 terminal completes=false, all three resolve",
            {"exhaustion_evidence": {
                "verdict": "NOT A RESULT", "terminal": True, "completes": False,
                "numerics_ladder_exhausted": num_ref,
                "model_setup_ruled_out": mod_ref,
                "capability_rule_out": cap_ref}},
            EXIT_OK, "green2.json")

        arm("GREEN-3 measured_capability_limit + capability_rule_out",
            {"exhaustion_evidence": {
                "verdict": "GATE FAIL", "terminal": True, "completes": True,
                "terminal_exemption": "measured_capability_limit",
                "capability_rule_out": cap_ref}},
            EXIT_OK, "green3.json")

        arm("GREEN-4 closure_challenge_model_accuracy_miss + numerics",
            {"exhaustion_evidence": {
                "verdict": "NOT A RESULT", "terminal": True, "completes": True,
                "terminal_exemption": "closure_challenge_model_accuracy_miss",
                "numerics_ladder_exhausted": num_ref}},
            EXIT_OK, "green4.json")

        arm("GREEN-5 terminal=false (active successor, out of scope)",
            {"exhaustion_evidence": {"verdict": "GATE FAIL", "terminal": False}},
            EXIT_OK, "green5.json")

        arm("GREEN-6 verdict=PASS (not applicable)",
            {"exhaustion_evidence": {"verdict": "PASS", "terminal": True}},
            EXIT_OK, "green6.json")

        # ---- RED-1 no exhaustion_evidence block + control ------------------
        arm("RED-1 terminal fail, NO block",
            {"verdict": "GATE FAIL", "terminal": True, "completes": True},
            EXIT_REFUSE, "red1.json")
        arm("RED-1 control: a valid block added",
            {"verdict": "GATE FAIL", "terminal": True, "completes": True,
             "numerics_ladder_exhausted": num_ref,
             "model_setup_ruled_out": mod_ref},
            EXIT_OK, "red1_ctl.json")

        # ---- RED-2 numerics ref points nowhere + control ------------------
        missing = "numerics_MISSING.md"
        arm("RED-2 numerics ref non-existent path",
            {"exhaustion_evidence": {
                "verdict": "GATE FAIL", "terminal": True, "completes": True,
                "numerics_ladder_exhausted": missing,
                "model_setup_ruled_out": mod_ref}},
            EXIT_REFUSE, "red2.json")
        with open(os.path.join(tmp, missing), "w") as f:   # control: create it
            f.write("now exists\n")
        arm("RED-2 control: the numerics ref file now exists",
            {"exhaustion_evidence": {
                "verdict": "GATE FAIL", "terminal": True, "completes": True,
                "numerics_ladder_exhausted": missing,
                "model_setup_ruled_out": mod_ref}},
            EXIT_OK, "red2_ctl.json")

        # ---- RED-3 model_setup_ruled_out absent ----------------------------
        arm("RED-3 model_setup_ruled_out absent",
            {"exhaustion_evidence": {
                "verdict": "GATE FAIL", "terminal": True, "completes": True,
                "numerics_ladder_exhausted": num_ref}},
            EXIT_REFUSE, "red3.json")

        # ---- RED-4 completes=false, capability_rule_out absent + control ---
        arm("RED-4 completes=false, capability_rule_out absent",
            {"exhaustion_evidence": {
                "verdict": "NOT A RESULT", "terminal": True, "completes": False,
                "numerics_ladder_exhausted": num_ref,
                "model_setup_ruled_out": mod_ref}},
            EXIT_REFUSE, "red4.json")
        arm("RED-4 control: resolving capability_rule_out added",
            {"exhaustion_evidence": {
                "verdict": "NOT A RESULT", "terminal": True, "completes": False,
                "numerics_ladder_exhausted": num_ref,
                "model_setup_ruled_out": mod_ref,
                "capability_rule_out": cap_ref}},
            EXIT_OK, "red4_ctl.json")

        # ---- RED-5 unknown exemption ---------------------------------------
        arm("RED-5 terminal_exemption='something_else'",
            {"exhaustion_evidence": {
                "verdict": "GATE FAIL", "terminal": True, "completes": True,
                "terminal_exemption": "something_else"}},
            EXIT_REFUSE, "red5.json")

        # ---- RED-6 measured_capability_limit, both non-resolving -----------
        arm("RED-6 measured_capability_limit, cap+exemption non-resolving",
            {"exhaustion_evidence": {
                "verdict": "GATE FAIL", "terminal": True, "completes": True,
                "terminal_exemption": "measured_capability_limit",
                "capability_rule_out": "nope.md",
                "exemption_ref": "also_nope.md"}},
            EXIT_REFUSE, "red6.json")

        print("=" * 78)
        if ok:
            print("SELFTEST: PASS -- every arm hit its expected exit code; each RED arm")
            print("is paired with a control that flips it, proving the arm is load-bearing.")
        else:
            print("SELFTEST: FAIL -- at least one arm did NOT hit its expected exit code.")
            print("An acceptance gate whose plant does not fire prints no admissible pass (rule 3).")
        print("=" * 78)
        return ok
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("record", nargs="?",
                    help="path to a JSON record carrying an exhaustion_evidence block")
    ap.add_argument("--selftest", action="store_true",
                    help="drive the both-directions planted control; exit 3 if it does not fire")
    args = ap.parse_args(argv)

    if args.selftest:
        return EXIT_OK if selftest() else EXIT_VIOLATION

    if not args.record:
        ap.error("a record.json path is required (or --selftest)")

    code, line = check_record(args.record)
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
