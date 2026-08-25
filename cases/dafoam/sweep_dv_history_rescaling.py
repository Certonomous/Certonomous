#!/usr/bin/env python3
"""D4-DEF-4 BLAST-RADIUS SWEEP -- commissioned by SUPERVISOR_D4DEF4_REPAIR_RULING.md §6.

THE QUESTION: which instruments in this lab READ DESIGN VARIABLES OUT OF A
pyOptSparse / OpenMDAO HISTORY and RE-APPLY THEM through `prob.set_val` (or
equivalent), and of those, which read a path where a registered OpenMDAO
`scaler` is NOT 1.0?

------------------------------------------------------------------------------
THE DISCRIMINATOR IS THE **SOURCE OF THE VECTOR**, NOT THE `set_val` CALL.
------------------------------------------------------------------------------
OpenMDAO's pyOptSparseDriver applies each design variable's `scaler` BEFORE
pyOptSparse sees the problem.  Therefore:

  * a vector read from `prob.get_val(...)` is the MODEL value and is PHYSICAL.
    Writing it to a file and later `set_val`-ing it back is a round trip in one
    unit system and CANNOT carry D4-DEF-4.
  * a vector read from `OptView.hst` through `History.getValues(...)` is
    DRIVER-SCALED, and `scale=False` is INERT because pyOptSparse's own scale is
    1.0.  Applying THAT through `set_val` is the defect.

**A sweep that keys on `set_val` is measuring the wrong thing.**  Recorded here
because THIS SWEEP'S FIRST PASS DID EXACTLY THAT and returned 87 hits, 72 of them
"FIRING" -- every optimisation runScript in the lab, because each declares
`prob.driver.hist_file = "OptView.hst"` (it WRITES the history) and each calls
`prob.set_val` during ordinary setup.  **Writing a history is not reading one.**
The first pass was discarded, not reported.

------------------------------------------------------------------------------
AND THE UNIT OF THE SWEEP IS THE **CHAIN**, NOT THE FILE.
------------------------------------------------------------------------------
**A per-file intersection MISSES D4 ITSELF.**  `d4_extract_endpoint.py` reads the
history and never calls `set_val`; `d4_fd_endpoint.py` calls `set_val` and never
touches the history; the JSON between them is where the units are lost.  Neither
file alone carries both halves of the pattern.  This sweep therefore groups by
DIRECTORY and asks whether the two halves are present in the same chain -- and
the D4 chain is a PLANT this sweep must return before any zero from it is
believed.

------------------------------------------------------------------------------
THE STATES REPORTED
------------------------------------------------------------------------------
  FIRING              chain reads a history AND re-applies, and some registered
                      scaler on that path is != 1.0
  EXPOSED_NOT_FIRING  chain reads a history AND re-applies, every registered
                      scaler == 1.0.  **REPORTED AS EXPOSED, NEVER AS CLEAN** --
                      D4 is only visible because one scaler happened to be 10.
  MITIGATED           chain reads a history, re-applies, AND already divides by
                      a scaler.  Sub-state records whether that divisor is
                      PARSED from the registration or TYPED (the drift risk the
                      ruling names).
  SAFE_BY_SOURCE      chain re-applies a DV vector from a FILE, but that file is
                      sourced from `prob.get_val` and is physical.  Reported as
                      a NEAR MISS, not as clean: nothing in such a chain ASSERTS
                      that its file is physical.
  CLEAN               everything else

------------------------------------------------------------------------------
L-325 IS APPLIED TO THIS SWEEP'S OWN INSTRUMENT
------------------------------------------------------------------------------
"Not found" is the return value of two different situations -- the record is
absent, and the instrument cannot express its name.  Every pattern is PLANTED
against a file KNOWN to contain it, and the sweep REFUSES if a plant does not
come back.  Measured live during construction: `git grep -lE 'History('`
returns ZERO with `fatal: Unmatched (` on stderr -- a regex error rendering as
an empty result set, which is the failure mode exactly.

NO PAGER, NO `head`, NO `tail` ANYWHERE IN THE ENUMERATION PATH.  `grep -r` on
this box is ugrep honouring ignore files, so gitignored archives are invisible
to it; this sweep uses `git ls-tree` and `os.walk`, and NEITHER is a grep.
"""
import json
import os
import re
import subprocess
import sys

REPO = "/home/ubuntu/Certonomous"
RUNROOTS = "/home/ubuntu/certonomous-runs"

# --- STAGE 1: an actual READ of a pyOptSparse/OpenMDAO history -------------
READS_HISTORY = re.compile(
    r"History\s*\(|getValues\s*\(|readHistory|OptView\.hst[\"'][^)]*flag\s*=\s*[\"']r")
# --- STAGE 1b: merely DECLARES a history file (a WRITER, not a reader) -----
WRITES_HISTORY = re.compile(r"hist_file\s*=")
# --- STAGE 2: re-applies a design-variable vector --------------------------
REAPPLIES = re.compile(
    r"\.set_val\s*\(|setDesignVars\s*\(|\.set_design_vars\s*\(|prob\[[^\]]+\]\s*=")
# --- STAGE 2b: the vector came from a FILE ---------------------------------
FROM_FILE = re.compile(r"json\.load\s*\(|np\.load\s*\(|numpy\.load\s*\(|yaml\.safe_load")
# --- STAGE 2c: the vector came from prob.get_val -> PHYSICAL ---------------
FROM_GETVAL = re.compile(r"get_val\s*\(")
# --- registration and mitigation -------------------------------------------
REGISTERS = re.compile(r"add_design_var\s*\(")
SCALER_KW = re.compile(r"scaler\s*=\s*([-+0-9.eE]+)")
DIVIDES_BY_SCALER = re.compile(r"/\s*SCALER|/\s*_?scaler|/\s*[A-Za-z_]*SCALER[A-Za-z_]*|"
                               r"descale|de-?scal", re.I)
PARSES_REGISTRATION = re.compile(r"parse_registration|ast\.parse|add_design_var")

# --- L-325 plants: names KNOWN to exist that the patterns MUST return ------
PLANTS = [
    ("cases/dafoam/ladder-a/A2/curriculum_D4/d4_extract_endpoint.py", "READS_HISTORY"),
    ("cases/dafoam/ladder-a/A2/curriculum_D4/d4_fd_endpoint.py", "REAPPLIES"),
    ("cases/dafoam/ladder-a/A2/curriculum_D4/d4_opt_runScript.py", "REGISTERS"),
    ("cases/dafoam/ladder-a/A2/curriculum_D4/d4_opt_runScript.py", "WRITES_HISTORY"),
    ("sdk/scripts/build_a2_shape_frames.py", "READS_HISTORY"),
]
# the CHAIN plant: this directory MUST come back as a chain hit, or the
# chain-grouping logic cannot see the very defect it was built for.
CHAIN_PLANT = "cases/dafoam/ladder-a/A2/curriculum_D4"

PATS = {"READS_HISTORY": READS_HISTORY, "WRITES_HISTORY": WRITES_HISTORY,
        "REAPPLIES": REAPPLIES, "REGISTERS": REGISTERS}


def sh(args, cwd=REPO):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if p.returncode not in (0, 1):
        sys.stderr.write("SWEEP REFUSE rc=%d: %s\n%s\n"
                         % (p.returncode, " ".join(args), p.stderr[:400]))
        sys.exit(2)
    return p.stdout


def blob(path):
    p = subprocess.run(["git", "show", "HEAD:%s" % path], cwd=REPO,
                       capture_output=True, text=True, errors="replace")
    return p.stdout if p.returncode == 0 else ""


def tracked():
    out = sh(["git", "ls-tree", "-r", "HEAD", "--name-only"])
    names = [l for l in out.split("\n") if l]
    return [n for n in names if n.endswith((".py", ".sh"))], len(names)


def on_disk():
    hits, n_all = [], 0
    prune = {"0", "0.orig", "constant", "system", "postProcessing", "reports",
             "FFD", ".git", "__pycache__"}
    for root, dirs, files in os.walk(RUNROOTS):
        dirs[:] = [d for d in dirs if not d.startswith("processor") and d not in prune]
        for f in files:
            n_all += 1
            if f.endswith((".py", ".sh")):
                hits.append(os.path.join(root, f))
    return hits, n_all


def scalers_in(text):
    out = []
    for m in REGISTERS.finditer(text):
        seg = text[m.start():m.start() + 400]
        sm = SCALER_KW.search(seg)
        nm = re.search(r'add_design_var\s*\(\s*["\']([^"\']+)', seg)
        out.append({"dv": nm.group(1) if nm else None,
                    "scaler": float(sm.group(1)) if sm else 1.0,
                    "scaler_declared": bool(sm)})
    return out


def sweep(texts, label):
    """Group by directory and classify each CHAIN."""
    dirs = {}
    for p, t in texts:
        dirs.setdefault(os.path.dirname(p), []).append((p, t))

    rows = []
    for d, members in sorted(dirs.items()):
        readers = [p for p, t in members if READS_HISTORY.search(t)]
        reappliers = [p for p, t in members if REAPPLIES.search(t)]
        if not (readers and reappliers):
            # a chain with no history READ is not exposed to D4-DEF-4 at all.
            # But a chain that re-applies a DV vector FROM A FILE is a near miss
            # worth naming, so record it separately.
            fromfile = [p for p, t in members
                        if REAPPLIES.search(t) and FROM_FILE.search(t)]
            if fromfile:
                joined = "\n".join(t for _, t in members)
                regs = scalers_in(joined)
                nonunit = [r for r in regs if r["scaler"] != 1.0]
                rows.append({
                    "chain_dir": d, "population": label,
                    "state": "SAFE_BY_SOURCE",
                    "reapplies_from_file": sorted(fromfile),
                    "history_readers": [],
                    "dv_source_is_get_val": bool(FROM_GETVAL.search(joined)),
                    "scalers_registered": {r["dv"]: r["scaler"] for r in regs},
                    "scalers_not_1": {r["dv"]: r["scaler"] for r in nonunit},
                    "note": "re-applies a DV vector read from a FILE, but the "
                            "file is not sourced from a pyOptSparse history. "
                            "NEAR MISS, not clean: nothing in the chain ASSERTS "
                            "that its file is physical.",
                })
            continue

        joined = "\n".join(t for _, t in members)
        regs = scalers_in(joined)
        reg_here = bool(regs)
        nonunit = [r for r in regs if r["scaler"] != 1.0]
        mitigated = bool(DIVIDES_BY_SCALER.search(joined))
        parses = bool(re.search(r"parse_registration|ast\.parse", joined))

        if mitigated:
            state = "MITIGATED"
        elif not reg_here:
            state = "HIT_REGISTRATION_NOT_IN_CHAIN"
        elif nonunit:
            state = "FIRING"
        else:
            state = "EXPOSED_NOT_FIRING"

        rows.append({
            "chain_dir": d, "population": label, "state": state,
            "history_readers": sorted(readers),
            "reappliers": sorted(reappliers),
            "registration_in_chain": reg_here,
            "scalers_registered": {r["dv"]: r["scaler"] for r in regs},
            "scalers_not_1": {r["dv"]: r["scaler"] for r in nonunit},
            "already_divides_by_a_scaler": mitigated,
            "divisor_parsed_from_registration": parses if mitigated else None,
        })
    return rows, len(dirs)


def main():
    # ---------------- L-325 plants ---------------------------------------
    plants = []
    for path, which in PLANTS:
        text = blob(path)
        seen = bool(text) and bool(PATS[which].search(text))
        plants.append({"planted_file": path, "pattern": which,
                       "blob_bytes": len(text), "returned": seen})
        if not seen:
            sys.stderr.write("SWEEP REFUSE plant %s did not return %s -- the "
                             "instrument cannot express the name it is asked "
                             "about; no zero from it is evidence (L-325)\n"
                             % (path, which))
            sys.exit(2)

    files_a, n_tree = tracked()
    texts_a = [(p, blob(p)) for p in files_a]
    files_b, n_files_b = on_disk()
    texts_b = []
    for p in files_b:
        try:
            with open(p, errors="replace") as fh:
                texts_b.append((p, fh.read()))
        except OSError:
            texts_b.append((p, ""))

    rows_a, ndir_a = sweep(texts_a, "A_tracked_HEAD")
    rows_b, ndir_b = sweep(texts_b, "B_runroots_disk")
    rows = rows_a + rows_b

    # ---- the CHAIN plant: the D4 chain MUST come back --------------------
    chain_seen = any(r["chain_dir"] == CHAIN_PLANT and
                     r["state"] in ("FIRING", "MITIGATED") for r in rows_a)
    plants.append({"planted_chain": CHAIN_PLANT, "pattern": "CHAIN_GROUPING",
                   "returned": chain_seen})
    if not chain_seen:
        sys.stderr.write("SWEEP REFUSE the chain plant %s did not come back -- "
                         "a sweep that cannot see the defect it was built for "
                         "proves nothing about anything else\n" % CHAIN_PLANT)
        sys.exit(2)

    counted = {}
    for r in rows:
        counted[r["state"]] = counted.get(r["state"], 0) + 1

    report = {
        "sweep": "D4-DEF-4 blast radius: DV vectors sourced from a pyOptSparse "
                 "HISTORY and re-applied, where a registered scaler != 1.0",
        "discriminator": "the SOURCE of the vector -- prob.get_val is PHYSICAL, "
                         "History.getValues is DRIVER-SCALED. A sweep keyed on "
                         "set_val measures the wrong thing.",
        "unit_of_sweep": "the CHAIN (directory), not the file -- D4's two halves "
                         "live in two files and a per-file intersection misses it.",
        "plants_L325": plants,
        "population_A_tracked_at_HEAD": {
            "paths_in_tree": n_tree, "py_sh_examined": len(files_a),
            "chains_examined": ndir_a,
            "enumeration": "git ls-tree -r HEAD --name-only; blobs via git show "
                           "HEAD:<path>. THE WORKTREE IS NOT USED -- the shared "
                           "index is decayed and stages deletions of files "
                           "present at HEAD."},
        "population_B_runroots_on_disk": {
            "files_walked": n_files_b, "py_sh_examined": len(files_b),
            "chains_examined": ndir_b,
            "enumeration": "os.walk of /home/ubuntu/certonomous-runs, OpenFOAM "
                           "case sub-trees pruned. OUTSIDE git and invisible to "
                           "population A -- d4_stage_F.sh lived here untracked."},
        "tally": counted,
        "chains_clean_A": ndir_a - len(rows_a),
        "chains_clean_B": ndir_b - len(rows_b),
        "rows": rows,
        "what_this_enumeration_cannot_see": [
            "UNTRACKED files in the Certonomous worktree -- deliberately not "
            "swept, because the shared index is decayed and other teams' "
            "uncommitted work would enter the population.",
            "/home/ubuntu/closure-data, /home/ubuntu/closure-challenge-benchmark "
            "and any other out-of-git data area.",
            "Instruments inside container images.",
            "A chain whose two halves live in DIFFERENT directories -- grouping "
            "is by directory, so a reader in one tree feeding a re-applier in "
            "another is invisible to this sweep. NAMED, not fixed.",
            "A scaler passed as a variable rather than a literal: recorded as "
            "1.0 by the parser, which biases toward EXPOSED_NOT_FIRING rather "
            "than toward CLEAN.",
            "A history read through a helper module imported from elsewhere.",
        ],
    }
    print(json.dumps(report, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
