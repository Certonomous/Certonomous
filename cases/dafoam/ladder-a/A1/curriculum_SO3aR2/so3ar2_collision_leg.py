#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SO-3aR2 COLLISION LEG -- the RED-THEN-GREEN proof of the per-point run_directory
repair.  Host-only.  ZERO solver compute, no container, no OpenFOAM, no DAFoam.

===========================================================================
WHAT KILLED SO-3aR, AND WHY AN ASSERTION THAT IT IS FIXED IS NOT A PROOF
===========================================================================
SO-3aR ran two of five declared arms and died at `X-S` with, verbatim from its own
container log:

    pyDAFoam Error: /mnt/X-S/0.0001 already exists, moving failed!

raised at `.../dafoam/pyDAFoam.py:1543` in `renameSolution`, reached from
`.../dafoam/mphys/mphys_dafoam.py:483` in `solve_linear`, under
`prob.compute_totals(of=of, wrt=["shape"])`
[MEASURED, `curriculum_SO3aR/RESULTS.md` section 6; log lines 1827/1865/1868/1873].
`point0` renamed `443 -> 0.0001` and SUCCEEDED; `point1` tried `436 -> 0.0001` into
the destination `point0` had already taken.

`so3ar_runScript.py:245` built a SEPARATE `DAFoamBuilder` per point and passed NO
`run_directory` to any of them, so three `DASolver` instances -- each with its own
`solution_counter` -- addressed one case directory.  `grep -n run_directory
curriculum_SO3aR/so3ar_runScript.py` returns NOTHING [MEASURED].

THIS FILE EXISTS BECAUSE THE LAB HAS BEEN KILLED THREE TIMES RUNNING BY
INSTRUMENTS THAT READ GREEN ON THE STATE THAT KILLS THE ITEM.  SO-3a's
`so3a_xf_selftest` leg `A5` asserted that `PRODUCER_MD5` WAS a sentinel and went on
passing after the pin should have been set; SO-3a shipped 250 python legs and 0
failures on the morning it could not launch.  So this leg does not assert the fix.
IT DRIVES THE FAILURE FIRST, ON THE REAL UNFIXED BYTES, AND REFUSES TO REPORT
GREEN UNLESS IT HAS FIRST SEEN RED.

===========================================================================
THE FIVE LIMBS, AND WHAT EACH ONE IS EVIDENCE OF
===========================================================================
  L1  GREEN  -- the frozen `so3ar2_runScript.py`: three DISTINCT destinations,
                three real `os.rename` calls on a real temp filesystem, no raise.
  L2  RED    -- a BYTE-IDENTICAL COPY of the frozen runScript with ONE mutation
                (the `run_directory=` keyword deleted from the builder call),
                which reconstructs SO-3aR's state exactly.  MUST raise.
  L3  RED    -- SO-3aR's OWN FROZEN BYTES, read from `curriculum_SO3aR/` and never
                written.  This is the strongest limb available without a
                container: the leg reproduces the death on the exact file that
                produced it in production.  MUST raise, and the message MUST carry
                the literal bytes `already exists, moving failed!`.
  L4  RED    -- the LAUNCHER limb.  A `run_directory` the runScript names but the
                launcher never stages is a different failure with the same
                symptom.  Every value of `RUN_DIRS` must appear in
                `so3ar2_run_arm.sh`'s staging loop; a copy with one staging line
                deleted MUST be caught.
  L5  REFUSE -- the RULE-3 CONTROL ON THE LEG'S OWN READER.  A leg that extracts
                its subjects from the file under test cannot, on its own, tell
                "no collisions" from "no builders found".  L5 blinds the AST
                extractor and requires exit 2 -- the ABSENCE of a reading, which
                is neither green nor red.  Without L5 this whole file could ship
                reading GREEN on a source it could not parse at all.

`ONE MUTATION AT A TIME` is not fastidiousness: a compound mutant cannot attribute
a detection, because one limb's refusal masks another's silence.  L2 and L4 each
carry exactly one.

===========================================================================
WHAT THIS LEG DOES **NOT** ESTABLISH -- stated plainly, not in a footnote
===========================================================================
`pyDAFoam.py` IS NOT ON THIS HOST (`find / -name pyDAFoam.py` returns nothing
[MEASURED]); it lives inside the container image.  So the destination NAME this
model computes -- `"%g" % (DELTA_T * solution_counter)` with `DELTA_T = 1e-4` and
the counter starting at 1 -- is RECONSTRUCTED FROM THE MEASURED LOG STRINGS of
SO-3aR's own death (`Moving time 443 to 0.0001`, `Moving time 436 to 0.0001`,
`/mnt/X-S/0.0001`), NOT read from upstream source.  It is a MODEL of the naming
rule and is labelled one.

WHAT IS **NOT** MODELLED IS THE LOAD-BEARING PART: the collision itself is a REAL
one.  This leg makes real directories on a real filesystem and calls the real
`os.path.exists` and `os.rename`, and the structural claim it proves does not
depend on the naming rule at all -- three solvers whose counters start at the same
value and whose deltaT is the same produce the SAME basename whatever that
basename is, so they collide if and only if they share a parent directory.  The
leg asserts the destinations are distinct AS PATHS, which is the property the
repair actually establishes.

It establishes NOTHING about whether three `DASimpleFoam` `DASolver` instances
co-exist correctly in one process once isolated -- that is a runtime question only
the X-S arm can answer, and section 6's `P-EVAL` is registered against it.  It
establishes NOTHING about upstream: upstream's own multipoint tutorial shares one
directory too, but passes ONE shared `dafoam_builder` to both scenarios where this
item constructs THREE, so the collision plausibly cannot arise there.  That
reading is recorded OPEN/UNTESTED in `curriculum_SO3aR/RESULTS.md` and nothing
here is a defect report.  NOT FILED ANYWHERE.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

# The producer this leg reads.  Filled at the freeze, driven in BOTH directions by
# `so3ar2_groot5_selftest.sh` legs (c5)/(c5b).  SO-3aR's own producer pin was never
# driven at all -- it was read for the first time inside a container, on the item's
# second arm, and it was UNSET.
PRODUCER_MD5 = "d9ac0faf5b5e49d686db74db4cdbc1aa"

# The launcher whose staging loop must create what the producer names.
LAUNCHER_MD5 = "ebc127f7039acc7b8422ee23442a8360"

# The parent's frozen producer -- the REAL bytes that really died.  READ-ONLY.  A
# closed item's file is never written by a successor (CLAUDE.md rule 6).
PARENT_RUNSCRIPT = os.path.join(HERE, os.pardir, "curriculum_SO3aR", "so3ar_runScript.py")
PARENT_RUNSCRIPT_MD5 = "53ba67c95461f86a585cb7ec7cdc2b39"

# The MODEL of pyDAFoam's rename destination.  See the docstring: reconstructed
# from measured log strings, not from upstream source.
DELTA_T = 1.0e-4
COUNTER0 = 1

# The literal bytes the real failure carries.  L3 requires them.
FAIL_BYTES = "already exists, moving failed!"

EXIT_GREEN, EXIT_RED, EXIT_REFUSE = 0, 1, 2


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


# ===========================================================================
# THE EXTRACTOR.  Reads, from the SOURCE, what `run_directory` each builder gets.
# ===========================================================================
def extract_builders(src_text, path, blind=False):
    """Return [(scenario_expr_repr, run_directory_or_None), ...] for every
    `DAFoamBuilder(...)` constructed in the file, in source order.

    `blind=True` is L5's mutation: the extractor returns nothing.  It exists so
    the leg can be shown unable to launder "I could not read the file" into "I
    found no collisions".
    """
    if blind:
        return []
    tree = ast.parse(src_text, filename=path)

    # module-level literal bindings, so `RUN_DIRS[sc]` can be resolved without
    # importing DAFoam.  Only dict/list/str/comprehension-over-a-literal-list
    # forms are evaluated, and anything else stays UNRESOLVED rather than guessed.
    consts = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        t = node.targets[0]
        if not isinstance(t, ast.Name):
            continue
        try:
            consts[t.id] = ast.literal_eval(node.value)
            continue
        except (ValueError, SyntaxError):
            pass
        # `{sc: "mp%d" % i for i, sc in enumerate(SCENARIOS)}` and
        # `["point%d" % i for i in range(len(ALPHAS))]` -- evaluated against the
        # literals already bound, never against the interpreter's globals.
        try:
            consts[t.id] = eval(  # noqa: S307 - literal-only namespace, see below
                compile(ast.Expression(node.value), path, "eval"),
                {"__builtins__": {"range": range, "len": len, "enumerate": enumerate}},
                dict(consts))
        except Exception:
            pass

    # ---- ONE CALL SITE IN A LOOP IS NOT ONE BUILDER, AND THE DISTINCTION IS THE
    # ---- ONE THIS WHOLE ITEM TURNS ON.  This lane's first draft counted
    # ---- `DAFoamBuilder(` call SITES and read "1" for a construction inside
    # ---- `for i, sc in enumerate(SCENARIOS):`, then labelled the result
    # ---- ONE_SHARED_BUILDER.  It reached the right destinations by luck and the
    # ---- label was a lie: three builders were being built.  It matters because
    # ---- the difference between "one call site executed three times" (three
    # ---- DASolvers, three solution_counters, collision) and "one builder object
    # ---- passed to three scenarios" (one DASolver, no collision) is EXACTLY the
    # ---- structural difference between this item and upstream's own multipoint
    # ---- tutorial, and it is the reason this record does not call upstream
    # ---- broken.  So the loop is detected instead of assumed.
    loop_iters = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.AsyncFor)):
            names = {n.id for n in ast.walk(node.iter) if isinstance(n, ast.Name)}
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    loop_iters.append((sub, names))

    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", None)
        if name != "DAFoamBuilder":
            continue
        rd = None
        for kw in node.keywords:
            if kw.arg != "run_directory":
                continue
            try:
                rd = ast.literal_eval(kw.value)
            except (ValueError, SyntaxError):
                # `RUN_DIRS[sc]` -- resolve the MAP, and report it as a map so the
                # caller expands it over the scenarios rather than over one key.
                rd = ("MAP", ast.unparse(kw.value)) if hasattr(ast, "unparse") else ("MAP", "?")
        looped = any(c is node and ("SCENARIOS" in nm or "POINTS" in nm or "ALPHAS" in nm)
                     for c, nm in loop_iters)
        out.append((rd, consts, looped, node.lineno))
    return out


def resolve_run_dirs(src_text, path, blind=False):
    """The per-scenario destination PARENT each DASolver will rename into.

    Returns (scenarios, [abs-relative parent per scenario], how) or refuses.
    `how` names which rule resolved it, so a reader can tell a real
    `run_directory` from the cwd fallback.
    """
    builders = extract_builders(src_text, path, blind=blind)
    if not builders:
        return None, None, "NO_BUILDERS_FOUND"
    consts = builders[0][1]
    scen = consts.get("SCENARIOS")
    if not isinstance(scen, (list, tuple)) or not scen:
        return None, None, "NO_SCENARIOS_FOUND"
    scen = list(scen)

    # HOW MANY `DASolver`s WILL EXIST, which is the only question that matters:
    # a call site inside a loop over the scenarios builds ONE PER SCENARIO; a
    # single call site outside any such loop builds ONE, SHARED.
    n_solvers = sum(len(scen) if looped else 1 for _, _, looped, _ in builders)
    per_scenario = [b for b in builders if b[2]]
    if n_solvers == 1:
        return scen, ["." for _ in scen], (
            "ONE_SHARED_BUILDER -- a single DAFoamBuilder constructed OUTSIDE any "
            "loop over the scenarios, so ONE DASolver and ONE solution_counter "
            "serve every scenario and no rename can collide with itself.  This is "
            "upstream's tutorial shape, NOT this item's")
    if n_solvers != len(scen):
        return None, None, "BUILDER_COUNT_%d_SOLVERS_VS_%d_SCENARIOS" % (n_solvers, len(scen))

    rd_map = consts.get("RUN_DIRS")
    parents, how = [], []
    for i, sc in enumerate(scen):
        b = per_scenario[0] if per_scenario else builders[i]
        rd = b[0]
        if rd is None:
            parents.append(".")
            how.append("CWD_FALLBACK -- no run_directory keyword")
        elif isinstance(rd, tuple) and rd[0] == "MAP":
            if not isinstance(rd_map, dict) or sc not in rd_map:
                return None, None, "RUN_DIRS_MAP_UNRESOLVED_FOR_%s" % sc
            parents.append(str(rd_map[sc]))
            how.append("RUN_DIRS[%s]" % sc)
        else:
            parents.append(str(rd))
            how.append("literal")
    return scen, parents, ("PER_SCENARIO (%d DASolvers): " % n_solvers) + "; ".join(how)


# ===========================================================================
# THE MODEL.  Real directories, real os.rename, real collision.
# ===========================================================================
class RenameCollision(Exception):
    pass


def drive_rename(arm_dir, scen, parents, converged_times):
    """One `DASolver` per scenario, each with its OWN `solution_counter` starting at
    COUNTER0, each renaming its converged time directory into its own
    `run_directory`.  Faithful to the MEASURED sequence: point0 renamed 443, point1
    renamed 436, point2 would have renamed 424.

    Raises RenameCollision carrying the REAL pyDAFoam message shape when a
    destination already exists.  Nothing here is simulated -- `os.path.exists` and
    `os.rename` are the real ones, on a real filesystem.
    """
    dsts = []
    for i, sc in enumerate(scen):
        rundir = os.path.normpath(os.path.join(arm_dir, parents[i]))
        os.makedirs(rundir, exist_ok=True)
        src = os.path.join(rundir, str(converged_times[i]))
        os.makedirs(src, exist_ok=True)
        with open(os.path.join(src, "U"), "w") as fh:
            fh.write("scenario %s\n" % sc)
        # pyDAFoam.renameSolution: dst = <run_directory>/<counter * deltaT>
        dst = os.path.join(rundir, "%g" % (DELTA_T * COUNTER0))
        if os.path.exists(dst):
            raise RenameCollision("pyDAFoam Error: %s %s" % (dst, FAIL_BYTES))
        os.rename(src, dst)
        dsts.append(dst)
    return dsts


def run_case(label, src_path, tmp, blind=False, src_text=None):
    """Drive one source file end to end.  Returns a dict; never raises for a
    finding -- the caller decides what a finding means for that limb."""
    text = src_text if src_text is not None else open(src_path).read()
    scen, parents, how = resolve_run_dirs(text, src_path, blind=blind)
    if scen is None:
        return {"label": label, "resolved": False, "why": how}
    arm = os.path.join(tmp, label.replace(" ", "_"))
    os.makedirs(arm, exist_ok=True)
    abs_parents = [os.path.normpath(os.path.join(arm, p)) for p in parents]
    distinct = len(set(abs_parents)) == len(abs_parents)
    times = [443, 436, 424][:len(scen)] or [443]
    try:
        dsts = drive_rename(arm, scen, parents, times)
    except RenameCollision as e:
        return {"label": label, "resolved": True, "how": how, "scenarios": scen,
                "run_directories": parents, "distinct_parents": distinct,
                "collided": True, "message": str(e)}
    return {"label": label, "resolved": True, "how": how, "scenarios": scen,
            "run_directories": parents, "distinct_parents": distinct,
            "collided": False, "destinations": [os.path.relpath(d, arm) for d in dsts]}


# ===========================================================================
# L4: the launcher must STAGE what the producer NAMES.
# ===========================================================================
STAGE_TOKEN = 'cp -a "$BASE/MESH" "$WORK/$mp"'


def check_staging(launcher_text, run_dirs):
    """Every value of RUN_DIRS must be staged by the launcher.  A `run_directory`
    DAFoam is told to use but nobody creates is a different failure wearing the
    same symptom, and it would be invisible to L1-L3, which make the directories
    themselves.

    THE CHECK IS SCOPED TO THE STAGING LOOP, NOT TO THE WHOLE FILE, and that is a
    correction this lane had to make by driving it.  The first draft asked whether
    the string `mp1` appeared ANYWHERE in the launcher.  It does -- the launcher
    also iterates `mp0 mp1 mp2` in the G-IC0 block -- so deleting mp1 from the
    STAGING loop left the check GREEN.  A check that green on the mutation it
    exists to catch is worth less than no check, which is the whole subject of
    this file.  The staging loop is identified by the copy it performs, not by
    its position.
    """
    import re as _re
    blocks = []
    for m in _re.finditer(r"for\s+mp\s+in\s+([^;]+);\s*do", launcher_text):
        end = launcher_text.find("\n  done", m.end())
        body = launcher_text[m.end():end if end > 0 else len(launcher_text)]
        if STAGE_TOKEN in body:
            blocks.append(m.group(1).split())
    if not blocks:
        return {"run_dirs": list(run_dirs), "missing_from_launcher": list(run_dirs),
                "ok": False, "why": "no staging loop found -- no `for mp in ...` block "
                                    "performs %r" % STAGE_TOKEN}
    staged = set()
    for b in blocks:
        staged.update(b)
    missing = [d for d in run_dirs if d not in staged]
    return {"run_dirs": list(run_dirs), "staged_by_launcher": sorted(staged),
            "missing_from_launcher": missing, "ok": not missing}


def mutate_delete_run_directory(text):
    """L2's SINGLE mutation: delete the `run_directory=` keyword ARGUMENT from the
    builder call, and nothing else.  The result is SO-3aR's state.

    THE ARGUMENT IS DELETED, NOT THE LINE.  This lane's first draft dropped the
    whole source LINE, which in this file also carried the call's closing paren,
    so the mutant did not PARSE -- and a mutant that does not parse tests the
    reader's error handling, not the repair.  It was caught by driving the leg
    rather than by reading it.  The regex takes the comma too, so the remaining
    argument list is well formed."""
    import re as _re
    out, n = _re.subn(r",\s*run_directory=RUN_DIRS\[sc\]", "", text, count=1)
    return out, n


def mutate_drop_one_staged_dir(text, target):
    """L4b's SINGLE mutation: remove the ONE token naming a staged run directory
    FROM THE STAGING LOOP's iteration list, leaving the rest of the launcher --
    including the G-IC0 loop that names the same directories -- untouched.  That
    is the mutation a careless edit would actually make."""
    import re as _re
    out, n = text, 0
    for m in _re.finditer(r"for\s+mp\s+in\s+([^;]+);\s*do", text):
        end = text.find("\n  done", m.end())
        body = text[m.end():end if end > 0 else len(text)]
        if STAGE_TOKEN not in body or target not in m.group(1).split():
            continue
        newlist = " ".join(x for x in m.group(1).split() if x != target)
        out = text[:m.start(1)] + newlist + text[m.end(1):]
        n = 1
        break
    return out, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    say = sys.stdout.write

    producer = os.path.join(root, "so3ar2_runScript.py")
    launcher = os.path.join(root, "so3ar2_run_arm.sh")
    for p in (producer, launcher, PARENT_RUNSCRIPT):
        if not os.path.isfile(p):
            say("SO3AR2_COLLISION REFUSE missing input %s\n" % p)
            return EXIT_REFUSE

    # ---- pins, fail-closed.  A leg that reads an unverified producer is reading
    # ---- some other file's behaviour and calling it this item's.
    #
    # EACH COMPARISON NAMES ITS CONSTANT DIRECTLY, and that is not style.  This
    # lane's first draft looped over `(path, pin, name)` triples, so every
    # comparison read `got != pin` -- a LOCAL variable.  `so3ar2_pin_census.py`'s
    # A4 correctly calls a pin with no consumer site DEAD, and a hash compared
    # against a local is a runtime-to-runtime comparison, not a pin site.  All
    # three pins would have been dead to the census while looking consumed to a
    # reader.  The loop was the bug; the three lines are the fix.
    got_p = md5_of(producer)
    if got_p != PRODUCER_MD5:
        say("SO3AR2_COLLISION REFUSE producer md5 %s != frozen %s\n" % (got_p, PRODUCER_MD5))
        return EXIT_REFUSE
    got_l = md5_of(launcher)
    if got_l != LAUNCHER_MD5:
        say("SO3AR2_COLLISION REFUSE launcher md5 %s != frozen %s\n" % (got_l, LAUNCHER_MD5))
        return EXIT_REFUSE
    got_q = md5_of(PARENT_RUNSCRIPT)
    if got_q != PARENT_RUNSCRIPT_MD5:
        say("SO3AR2_COLLISION REFUSE parent producer md5 %s != frozen %s\n"
            % (got_q, PARENT_RUNSCRIPT_MD5))
        return EXIT_REFUSE

    tmp = tempfile.mkdtemp(prefix="so3ar2_collision_")
    findings = []
    try:
        ptext = open(producer).read()
        ltext = open(launcher).read()

        # ---- L1 GREEN ---------------------------------------------------------
        r1 = run_case("L1_frozen_fixed", producer, tmp)
        say("L1 %r\n" % r1)
        if not r1.get("resolved"):
            findings.append("L1 could not resolve run directories: %s" % r1.get("why"))
        elif r1["collided"]:
            findings.append("L1 THE FIX DID NOT HOLD -- the frozen producer collided: %s"
                            % r1["message"])
        elif not r1["distinct_parents"]:
            findings.append("L1 run directories are not distinct: %r" % r1["run_directories"])
        elif len(set(r1["run_directories"])) != len(r1["scenarios"]):
            findings.append("L1 RUN_DIRS is not injective over SCENARIOS: %r"
                            % r1["run_directories"])

        # ---- L2 RED, one mutation --------------------------------------------
        mtext, nmut = mutate_delete_run_directory(ptext)
        if nmut != 1:
            findings.append("L2 expected EXACTLY ONE run_directory keyword to delete, "
                            "deleted %d -- the mutation is not attributable" % nmut)
        else:
            r2 = run_case("L2_mutant_no_run_directory", producer, tmp, src_text=mtext)
            say("L2 %r\n" % r2)
            if not (r2.get("resolved") and r2.get("collided")):
                findings.append("L2 DID NOT GO RED.  With the isolation removed the leg "
                                "must reproduce the collision; it reported %r.  A fix "
                                "without a leg that fails on the unfixed state is not "
                                "proved." % r2)
            elif FAIL_BYTES not in r2["message"]:
                findings.append("L2 went red on the wrong thing: %r" % r2["message"])

        # ---- L3 RED, on SO-3aR's REAL FROZEN BYTES ---------------------------
        r3 = run_case("L3_parent_real_bytes", PARENT_RUNSCRIPT, tmp)
        say("L3 %r\n" % r3)
        if not (r3.get("resolved") and r3.get("collided")):
            findings.append("L3 DID NOT GO RED on SO-3aR's own frozen bytes (%s, md5 %s), "
                            "which DID die in production.  The leg is not measuring the "
                            "thing that killed the parent; it reported %r"
                            % (PARENT_RUNSCRIPT, PARENT_RUNSCRIPT_MD5, r3))
        elif FAIL_BYTES not in r3["message"]:
            findings.append("L3 went red on the wrong thing: %r" % r3["message"])

        # ---- L4 the launcher stages what the producer names -------------------
        rd = sorted(set(r1.get("run_directories") or []))
        s_ok = check_staging(ltext, rd)
        say("L4 %r\n" % s_ok)
        if not rd:
            findings.append("L4 no run directories to check -- L1 resolved none")
        elif not s_ok["ok"]:
            findings.append("L4 the launcher does not stage %r" % s_ok["missing_from_launcher"])
        else:
            bad, ntok = mutate_drop_one_staged_dir(ltext, rd[0])
            if ntok == 0:
                findings.append("L4 control could not plant: %r absent from the launcher" % rd[0])
            else:
                s_bad = check_staging(bad, rd)
                say("L4b (must be NOT ok) %r\n" % s_bad)
                if s_bad["ok"]:
                    findings.append("L4b DID NOT GO RED -- the staging check passes on a "
                                    "launcher that no longer stages %r, so its green on the "
                                    "real launcher is not evidence" % rd[0])

        # ---- L5 RULE-3: the reader proved not blind ---------------------------
        r5 = run_case("L5_blinded_extractor", producer, tmp, blind=True)
        say("L5 %r\n" % r5)
        if r5.get("resolved"):
            findings.append("L5 the blinded extractor still resolved builders -- the "
                            "blinding control is not blinding anything")
        elif r5.get("why") != "NO_BUILDERS_FOUND":
            findings.append("L5 blinded extractor refused for the wrong reason: %r"
                            % r5.get("why"))
        else:
            say("L5 OK -- a reader that finds no builders REFUSES; it does not report "
                "'no collisions'.  Exit 2 is the ABSENCE of a reading, neither green "
                "nor red.\n")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if findings:
        for f in findings:
            say("SO3AR2_COLLISION FINDING: %s\n" % f)
        say("SO3AR2_COLLISION rc=1 findings=%d\n" % len(findings))
        return EXIT_RED
    say("SO3AR2_COLLISION rc=0 -- L1 GREEN on the frozen producer; L2 RED on the same "
        "bytes with ONE mutation; L3 RED on SO-3aR's own frozen bytes; L4 the launcher "
        "stages every named run directory and L4b proves that check able to fail; L5 the "
        "extractor REFUSES when blinded.\n")
    return EXIT_GREEN


if __name__ == "__main__":
    sys.exit(main())
