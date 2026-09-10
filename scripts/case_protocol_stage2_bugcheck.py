#!/usr/bin/env python3
"""THE CASE PROTOCOL -- STAGE 2: BUG CHECK.

EXIT CONDITION
    Every check below is GREEN, and the whole stage completed in under a minute
    per level.  A green here does not say the answer will be right; it says the
    case can be run at all and that the instruments which will later report a zero
    have been shown able to report a non-zero.

FAILURE ACTION -- FIXED, NOT DISCRETIONARY
    On red: apply the repair the lessons ledger already carries for that red.  If
    the ledger carries nothing, apply the SMALLEST change that clears it and write
    a NEW lesson.  NEVER WAIT.  Every repair is recorded with the red that caused
    it, so a repair applied twice for the same red is visible as a repeat.

THE CHECKS
    1. checkMesh on every level.
    2. Dictionary and schema validation -- every dictionary the solver will read.
    3. BC closure on EVERY PATCH and EVERY FIELD -- the full matrix, not a spot check.
    4. Dead-lever audit -- a registered lever that cannot take effect.
    5. Instrument check with a planted perturbation driven through the REAL path.
    6. One-iteration dry run, with rc read FROM THE PROCESS.

WHY 4 EXISTS, IN ONE MEASURED SENTENCE
    On this protocol's first case a diagnostic registered to test `transonic yes`
    aborted at Time = 1 on `Entry 'div(phid,p)' not found in divSchemes`, so the
    lever was recorded as tried and was never once exercised.  A lever that cannot
    move is worse than a lever nobody pulled, because the record says it was pulled.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import case_protocol_lib as L  # noqa: E402

STAGE = "STAGE2"

# Fields OpenFOAM requires a boundary entry for, by solver family.  A field with a
# patch missing from its boundaryField is not a default -- it is a FatalIOError at
# construction, and it is the single most common way a 3D case dies after the queue
# has already spent the wall time getting to it.
REQUIRED_FIELDS = {
    "rhoPimpleFoam": ["U", "p", "T", "nut", "alphat", "k", "omega"],
    "rhoSimpleFoam": ["U", "p", "T", "nut", "alphat", "k", "omega"],
}

# Levers whose effect depends on something else being present.  {lever: (where it is
# read, what it needs, where THAT is read)}.  This table is the audit; adding a row
# is how a new lever becomes auditable.
DEAD_LEVER_RULES = [
    {
        "lever": "transonic yes",
        "declared_in": "system/fvSolution",
        "pattern": r"^\s*transonic\s+yes\s*;",
        "requires": "div(phid,p) scheme",
        "required_in": "system/fvSchemes",
        "required_pattern": r"div\(phid,p\)",
        "why": ("with transonic on, the pressure equation gains a div(phid,p) convective term. "
                "With `default none;` in divSchemes an unruled term is a HARD ABORT at the first "
                "pressure solve, so the run dies in dictionary lookup having exercised nothing."),
    },
    {
        "lever": "LTS (ddtSchemes localEuler)",
        "declared_in": "system/fvSchemes",
        "pattern": r"^\s*default\s+localEuler\s*;",
        "requires": "maxCo in the PIMPLE dict",
        "required_in": "system/fvSolution",
        "required_pattern": r"^\s*maxCo\s",
        "why": ("localEuler builds its local time step from maxCo. Without it the pseudo-time "
                "field is not controlled by anything the registration named."),
    },
    {
        "lever": "pressureControl (pMinFactor/pMaxFactor)",
        "declared_in": "system/fvSolution",
        "pattern": r"^\s*pM(in|ax)Factor\s",
        "requires": "a solver that constructs pressureControl",
        "required_in": "__solver_binary__",
        "required_pattern": r"pressureControl",
        "why": ("the factors are read by the pressureControl helper; a solver that never "
                "constructs it ignores them silently and the registration records a bound that "
                "was never applied."),
    },
    {
        "lever": "residualControl",
        "declared_in": "system/fvSolution",
        "pattern": r"^\s*residualControl\b",
        "requires": "NON-ZERO entries to have any effect",
        "required_in": "system/fvSolution",
        "required_pattern": r"residualControl[^}]*[1-9]",
        "why": ("residualControl with every entry 0 never fires. That is often DELIBERATE -- it "
                "keeps the run going to endTime so rule 4's last-time clause holds -- so this is "
                "reported as INERT-BY-DESIGN when the registration says so, and as a dead lever "
                "when it does not."),
    },
    {
        "lever": "limitTemperature fvOption",
        "declared_in": "system/fvOptions",
        "pattern": r"limitTemperature",
        "requires": "fvOptions to be listed as an active constraint the solver reads",
        "required_in": "system/fvOptions",
        "required_pattern": r"(selectionMode|type\s+limitTemperature)",
        "why": ("a clamp that is ACTIVE at the plateau is not a stabiliser, it is a boundary "
                "condition on the answer, and it biases any gate downstream of it. Stage 2 can "
                "only see that it is wired; stage 3 and 4 must check whether it is FIRING."),
    },
]


# ---------------------------------------------------------------------------

def run(argv: List[str], cwd: Optional[str] = None, timeout: float = 300.0) -> Tuple[int, str, float]:
    """Run a command and return (rc FROM THE PROCESS, combined output, wall seconds).

    `Popen.returncode` and nothing else.  `setsid timeout cmd` returns 0 for every
    outcome including a SIGFPE, which is how a crash gets recorded as a pass; no
    wrapper's exit status is consulted here.
    """
    t0 = time.time()
    p = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        out, _ = p.communicate()
        return 124, out, time.time() - t0
    return p.returncode, out, time.time() - t0


def check_mesh(level: str, case: Path, results: List[Dict[str, Any]]) -> Dict[str, Any]:
    rc, out, wall = run(L.foam_cmd(["checkMesh", "-case", str(case)], case), timeout=900)
    stars = [ln.strip() for ln in out.splitlines() if ln.lstrip().startswith("***")]
    ok = ("Mesh OK." in out) and rc == 0
    ncells = None
    m = re.search(r"^\s*cells:\s*(\d+)\s*$", out, re.M)
    if m:
        ncells = int(m.group(1))
    r = {"check": "checkMesh", "level": level, "rc": rc, "rc_source": "Popen.returncode",
         "wall_s": round(wall, 2), "mesh_ok": ok, "n_cells": ncells,
         "n_cells_source": f"checkMesh stdout: cells: {ncells}" if ncells else None,
         "failures": stars, "green": ok,
         "output_tail": ([] if ok else out.strip().splitlines()[-8:])}
    results.append(r)
    return r


def check_dictionaries(level: str, case: Path, solver: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Every dictionary the solver will read must PARSE, via OpenFOAM's own parser.

    Parsed by `foamDictionary` rather than by a regex, because a regex that is happy
    with a file OpenFOAM rejects is worse than no check.
    """
    need = ["system/controlDict", "system/fvSchemes", "system/fvSolution",
            "constant/thermophysicalProperties", "constant/turbulenceProperties"]
    bad, missing = [], []
    for rel in need:
        f = case / rel
        if not f.is_file():
            missing.append(rel)
            continue
        rc, out, _ = run(L.foam_cmd(["foamDictionary", "-case", str(case), rel], case), timeout=60)
        if rc != 0:
            bad.append({"file": rel, "rc": rc, "error": out.strip().splitlines()[-3:]})
    r = {"check": "dictionaries", "level": level, "required": need, "missing": missing,
         "unparseable": bad, "green": not missing and not bad}
    results.append(r)
    return r


def check_bc_closure(level: str, case: Path, solver: str, mesh_dir: Path,
                     results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """EVERY PATCH x EVERY FIELD.  The full matrix.

    A spot check on the wall passes a case whose farfield is missing an entry on
    `alphat`, and that case dies at field construction after the queue has already
    paid for everything upstream of it.
    """
    bnd = L.read_boundary(mesh_dir / "boundary")
    patches = sorted(bnd)
    fields = REQUIRED_FIELDS.get(solver)
    if fields is None:
        L.refuse("SOLVER_FIELDS_UNKNOWN", f"no required-field list registered for {solver!r}")
    matrix: Dict[str, Dict[str, str]] = {}
    holes: List[str] = []
    for fl in fields:
        f = case / "0" / fl
        if not f.is_file():
            f = case / "0" / (fl + ".gz")
        if not f.is_file():
            matrix[fl] = {p: "FIELD ABSENT" for p in patches}
            holes.append(f"0/{fl} absent")
            continue
        txt = f.read_text(errors="replace")
        body = txt[txt.find("boundaryField"):]
        matrix[fl] = {}
        for p in patches:
            # an entry may be named literally or matched by a quoted regex group
            lit = re.search(rf'(^|\s|"|\(){re.escape(p)}("|\)|\s|$)', body, re.M)
            typ = None
            if lit:
                after = body[lit.end():]
                tm = re.search(r"type\s+([\w:]+)\s*;", after)
                typ = tm.group(1) if tm else "MATCHED, TYPE UNREAD"
            if typ is None:
                matrix[fl][p] = "NO ENTRY"
                holes.append(f"0/{fl}: patch {p!r} has no boundary entry")
            else:
                matrix[fl][p] = typ
    r = {"check": "bc_closure", "level": level, "patches": patches, "fields": fields,
         "matrix": matrix, "holes": holes, "green": not holes}
    results.append(r)
    return r


def check_dead_levers(level: str, case: Path, solver: str, registration_notes: Dict[str, Any],
                      results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """A registered lever that cannot take effect is a dead lever.

    This does not ask whether a lever is a good idea.  It asks the narrower and
    entirely checkable question: if the registration says this lever is set, is
    the thing it depends on actually there?
    """
    findings = []
    for rule in DEAD_LEVER_RULES:
        src = case / rule["declared_in"]
        if not src.is_file():
            continue
        txt = src.read_text(errors="replace")
        # a commented-out line is not a declaration
        live = "\n".join(ln for ln in txt.splitlines() if not ln.lstrip().startswith("//"))
        if not re.search(rule["pattern"], live, re.M):
            continue
        where = rule["required_in"]
        if where == "__solver_binary__":
            rc, out, _ = run(["bash", "-lc",
                              f"source {L.FOAM_BASHRC} '' >/dev/null 2>&1 && "
                              f"nm -D $(which {solver}) 2>/dev/null | grep -c {rule['required_pattern']} "
                              f"|| strings $(which {solver}) | grep -c {rule['required_pattern']}"], timeout=120)
            present = rc == 0 and out.strip().isdigit() and int(out.strip()) > 0
            detail = f"symbol scan of the {solver} binary: {out.strip()[:40]}"
        else:
            dep = case / where
            dtxt = dep.read_text(errors="replace") if dep.is_file() else ""
            dlive = "\n".join(ln for ln in dtxt.splitlines() if not ln.lstrip().startswith("//"))
            present = bool(re.search(rule["required_pattern"], dlive, re.M | re.S))
            detail = f"{where} {'has' if present else 'LACKS'} {rule['requires']}"
        note = registration_notes.get(rule["lever"])
        findings.append({
            "lever": rule["lever"], "declared_in": rule["declared_in"],
            "requires": rule["requires"], "dependency_present": present,
            "detail": detail, "why": rule["why"],
            "registration_says": note,
            "status": ("LIVE" if present else
                       ("INERT-BY-DESIGN" if note == "inert by design" else "DEAD LEVER")),
        })
    dead = [f for f in findings if f["status"] == "DEAD LEVER"]
    r = {"check": "dead_levers", "level": level, "findings": findings,
         "dead": [f["lever"] for f in dead], "green": not dead}
    results.append(r)
    return r


SOURCE_DEFECT_RULES = [
    {
        "id": "TWO_POINT_PLATEAU",
        "authority": "VERIFICATION_CHARTER 2bd",
        "pattern": r"\[-1\]\s*-\s*\w+\[-2\]|\[-2\]\s*-\s*\w+\[-1\]",
        "what": ("a plateau or convergence test taken over the LAST TWO SAMPLES. A steady drift "
                 "with small per-write steps passes it. A false PLATEAUED is a false green on a "
                 "rule-5 clause-1 gate, and rule 5 lets a gate turn a PASS into NOT A RESULT but "
                 "never the reverse -- so it does not merely mis-report, it MANUFACTURES "
                 "admissibility. The window, the statistic over that window, and the tolerance "
                 "must all be declared before the run."),
    },
    {
        "id": "CELL_COUNT_FROM_OWNER",
        "authority": "VERIFICATION_CHARTER 2bd.1",
        "pattern": r"len\s*\(\s*[\w.]*(owner|parse_owner)[^)]*\)",
        "what": ("a cell count taken from polyMesh/owner, which holds one entry per FACE. "
                 "Measured 4.01x wrong in the instance that earned the clause, and it feeds the "
                 "refinement ratio, the observed order and every GCI derived from it. A cell "
                 "count comes from checkMesh stdout or the polyMesh header, and the registration "
                 "names the source."),
    },
    {
        "id": "LITERAL_CLAIM_STRING",
        "authority": "VERIFICATION_CHARTER 2be.1",
        "pattern": r"(print|write|append)\s*\([^)]*['\"](PASS|CONVERGING|PLATEAUED|Mesh OK|GREEN)['\"]",
        "what": ("a verdict word emitted as a literal rather than derived from a measurement. "
                 "No input can falsify it: the reader reads faithfully and reports a constant."),
    },
    {
        "id": "SILENT_DEFAULT_AS_MEASUREMENT",
        "authority": "lab practice, measured 2026-09-10",
        "pattern": r"\.get\s*\([^,)]+,\s*['\"]?0(\.0)?['\"]?\s*\)",
        "what": ("a dictionary default of zero flowing into a reported number. A key that was "
                 "never written and a value that was measured as zero then look identical, and "
                 "only one of them is evidence."),
    },
]


def check_instrument_source(level: str, comparator: Optional[str],
                            results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """ARM 2 of the instrument check: does the reader COMPUTE THE RIGHT THING.

    This arm exists because arm 1 cannot answer the question.  A planted
    perturbation asks only *can this reader see its input*.  A reader that opens the
    right file, reads it faithfully, and then computes the wrong quantity -- a
    plateau from the last two samples, a cell count from the face list, a verdict
    emitted as a string literal -- answers YES to arm 1 and is wrong anyway.  Those
    defects are not falsifiable by any input, so they are detected by reading the
    code and by nothing else.

    Reported SEPARATELY and labelled.  One clean line covering both arms certifies
    the weaker claim while appearing to certify the stronger one.
    """
    if comparator is None or not Path(comparator).is_file():
        r = {"check": "instrument_source_arm", "level": level, "green": False,
             "claim": "this reader computes the right thing",
             "detail": f"comparator {comparator!r} absent; nothing to read"}
        results.append(r)
        return r
    src = Path(comparator).read_text(errors="replace")
    live = "\n".join(ln for ln in src.splitlines() if not ln.lstrip().startswith("#"))
    hits = []
    for rule in SOURCE_DEFECT_RULES:
        for m in re.finditer(rule["pattern"], live):
            ln = live[:m.start()].count("\n") + 1
            hits.append({"id": rule["id"], "authority": rule["authority"],
                         "line_in_comment_stripped_source": ln,
                         "text": m.group(0)[:120], "what": rule["what"]})
    r = {"check": "instrument_source_arm", "level": level,
         "claim": "this reader computes the right thing",
         "comparator": comparator, "comparator_sha256": L.sha256_file(comparator),
         "rules_applied": [x["id"] for x in SOURCE_DEFECT_RULES],
         "hits": hits, "green": not hits,
         "detail": ("source-level detection only. A clean result here means none of the "
                    "REGISTERED defect shapes are present; it is not a proof of correctness, "
                    "and it must never be merged with the perturbation arm's result.")}
    results.append(r)
    return r


def check_instrument_planted(level: str, case: Path, comparator: Optional[str],
                             results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """ARM 1 of the instrument check: CAN THIS READER SEE ITS INPUT.

    A known perturbation goes into the field file on disk that the comparator will
    actually open -- not a copy, not a mock, not an in-memory array -- because the
    failure this guards against is a reader whose glob, patch filter or time
    selection silently misses the data it claims to read.

    THE RESTORE IS BYTE-FOR-BYTE AND MTIME-FOR-MTIME, AND A FAILED RESTORE DOMINATES
    EVERY OTHER OUTCOME.  Rule 4's age guard dates a run by comparing field mtimes
    against the case's own 0/T.  An audit that silently re-dates the artifact it is
    auditing corrupts the evidence it exists to check -- it can fail a sound run or
    pass an unsound one.  So the restore is verified by hash AND by mtime, and if
    that verification fails this returns a RESTORE FAILURE and nothing else: a
    corrupted-evidence result is not reported alongside a verdict, it replaces it.
    """
    claim = "this reader can see its input"
    if comparator is None or not Path(comparator).is_file():
        r = {"check": "instrument_perturbation_arm", "level": level, "green": False, "claim": claim,
             "detail": f"comparator {comparator!r} absent; a zero it reports would not be evidence"}
        results.append(r)
        return r

    target = None
    for t in sorted((d for d in case.iterdir() if d.is_dir() and re.fullmatch(r"\d+(\.\d+)?", d.name)),
                    key=lambda d: float(d.name), reverse=True):
        if (t / "p").is_file():
            target = t / "p"
            break
    if target is None:
        r = {"check": "instrument_perturbation_arm", "level": level, "green": False, "claim": claim,
             "detail": ("no written time directory carrying p; nothing to plant into. The "
                        "perturbation arm CANNOT be discharged before a first write, and this "
                        "stage says so rather than passing it by default.")}
        results.append(r)
        return r

    PLANT = 1.234e-03
    sha_before = L.sha256_file(target)
    st_before = target.stat()
    backup = target.with_suffix(target.suffix + ".preplant")
    shutil.copy2(target, backup)
    rc, out, seen = None, "", False
    try:
        txt = target.read_text()
        i = txt.find("internalField")
        j = txt.find("(", i)
        k = txt.find("\n", j)
        target.write_text(txt[:k + 1] + f"{PLANT:.6e}\n" + txt[k + 1:])
        rc, out, _ = run([sys.executable, comparator, "--selftest"], timeout=120)
        seen = (f"{PLANT:.3e}"[:5] in out) or ("PLANT" in out.upper())
    finally:
        shutil.copyfile(str(backup), str(target))
        os.utime(target, ns=(st_before.st_atime_ns, st_before.st_mtime_ns))
        Path(backup).unlink(missing_ok=True)

    sha_after = L.sha256_file(target)
    st_after = target.stat()
    restored = (sha_after == sha_before and st_after.st_mtime_ns == st_before.st_mtime_ns)
    if not restored:
        r = {"check": "instrument_perturbation_arm", "level": level, "green": False,
             "claim": claim, "RESTORE_FAILURE": True,
             "sha_before": sha_before, "sha_after": sha_after,
             "mtime_ns_before": st_before.st_mtime_ns, "mtime_ns_after": st_after.st_mtime_ns,
             "detail": ("THE AUDIT MUTATED THE ARTIFACT IT WAS AUDITING. Rule 4's age guard reads "
                        "these mtimes. No verdict is reported from this run and the case's "
                        "completion evidence must be treated as compromised until restored from "
                        "a known-good copy.")}
        results.append(r)
        return r

    r = {"check": "instrument_perturbation_arm", "level": level, "claim": claim,
         "plant_value": PLANT, "planted_into": str(target), "comparator_rc": rc,
         "comparator_saw_plant": bool(seen), "restored_byte_and_mtime": True,
         "green": bool(seen),
         "detail": ("the comparator was run against a field carrying a known perturbation; if it "
                    "did not see it, its zeros are not evidence (standing rule 3). THIS ARM SAYS "
                    "NOTHING ABOUT WHETHER THE COMPARATOR COMPUTES THE RIGHT THING -- see the "
                    "source arm.")}
    results.append(r)
    return r


def check_one_iteration(level: str, case: Path, solver: str, results: List[Dict[str, Any]],
                        scratch: Path) -> Dict[str, Any]:
    """One iteration, on a COPY, with rc read from the process.

    On a copy because a dry run that writes into the graded case makes the graded
    case's own age guard unreadable afterwards.
    """
    dry = scratch / f"dryrun_{level}"
    if dry.exists():
        shutil.rmtree(dry)
    dry.mkdir(parents=True, exist_ok=True)
    for rel in ("system", "constant", "0"):
        src = case / rel
        if src.is_dir():
            shutil.copytree(src, dry / rel, symlinks=True)
    cd = dry / "system" / "controlDict"
    txt = cd.read_text()
    txt = re.sub(r"^\s*endTime\s+[0-9.eE+\-]+\s*;", "endTime 1;", txt, flags=re.M)
    txt = re.sub(r"^\s*writeInterval\s+[0-9.eE+\-]+\s*;", "writeInterval 1;", txt, flags=re.M)
    cd.write_text(txt)

    rc, out, wall = run(L.foam_cmd([solver, "-case", str(dry)], dry), timeout=1800)
    sig = None
    if rc < 0:
        sig = -rc
    elif rc > 128:
        sig = rc - 128
    n_time = len(re.findall(r"^Time = ", out, re.M))
    n_exec = len(re.findall(r"^ExecutionTime = ", out, re.M))
    fatal = [ln.strip() for ln in out.splitlines() if "FOAM FATAL" in ln or "Entry '" in ln]
    r = {"check": "one_iteration", "level": level, "solver": solver,
         "rc": rc, "rc_source": "Popen.returncode (NOT a wrapper exit status)",
         "signal": sig, "wall_s": round(wall, 2),
         "time_lines": n_time, "executiontime_lines": n_exec,
         "fatal": fatal[:6], "green": rc == 0 and n_exec >= 1,
         "case_copy": str(dry),
         "interpretation": (
             "rc 136 is 128+8 = SIGFPE: the process took a floating-point exception. "
             "Zero ExecutionTime lines with one Time line means it died inside the first "
             "iteration, before any iteration completed." if sig == 8 else
             ("a FOAM FATAL with an Entry '...' not found is a DICTIONARY defect, not a "
              "physics one: the lever under test was never exercised." if fatal else ""))}
    results.append(r)
    return r


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--case-root", required=True,
                    help="where stage 1 wrote the runnable cases, one subdir per level")
    ap.add_argument("--solver", required=True)
    ap.add_argument("--comparator", default=None)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--skip", default="", help="comma-separated check names to skip, RECORDED as skipped")
    a = ap.parse_args(argv)

    spec = json.loads(Path(a.spec).read_text())
    out = Path(a.out)
    scratch = Path(a.scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    skip = {s.strip() for s in a.skip.split(",") if s.strip()}
    notes = spec.get("registration_lever_notes", {})

    results: List[Dict[str, Any]] = []
    per_level_wall: Dict[str, float] = {}
    t_all = time.time()

    for lv in spec["levels"]:
        name = lv["name"]
        case = Path(a.case_root) / name / "case"
        if not case.is_dir():
            case = Path(a.case_root) / name
        mesh_dir = Path(lv["mesh_dir"])
        t0 = time.time()
        for fn, args in (("checkMesh", (name, case, results)),):
            pass
        if "checkMesh" not in skip:
            check_mesh(name, case, results)
        if "dictionaries" not in skip:
            check_dictionaries(name, case, a.solver, results)
        if "bc_closure" not in skip:
            check_bc_closure(name, case, a.solver, mesh_dir, results)
        if "dead_levers" not in skip:
            check_dead_levers(name, case, a.solver, notes, results)
        if "instrument_planted" not in skip:
            ip = check_instrument_planted(name, case, a.comparator, results)
            if ip.get("RESTORE_FAILURE"):
                print(L.state_line(STAGE, "RESTORE FAILURE", "ABORT", detail=ip["detail"]))
                return 6
        if "instrument_source" not in skip:
            check_instrument_source(name, a.comparator, results)
        if "one_iteration" not in skip:
            check_one_iteration(name, case, a.solver, results, scratch)
        per_level_wall[name] = round(time.time() - t0, 2)

    for r in results:
        print(L.state_line(STAGE, f"{r['check']} {r.get('level','')}",
                           "GREEN" if r.get("green") else "RED",
                           **{k: v for k, v in r.items()
                              if k in ("rc", "signal", "wall_s", "n_cells", "time_lines",
                                       "executiontime_lines", "comparator_saw_plant")
                              and v is not None}))
        for h in (r.get("holes") or [])[:8]:
            print(L.state_line(STAGE, f"{r['check']} {r.get('level','')} hole", h))
        for d in (r.get("dead") or []):
            print(L.state_line(STAGE, f"{r['check']} {r.get('level','')} DEAD LEVER", d))
        for f in (r.get("fatal") or [])[:3]:
            print(L.state_line(STAGE, f"{r['check']} {r.get('level','')} fatal", f))

    for lvl, w in per_level_wall.items():
        print(L.state_line(STAGE, f"budget {lvl}", "UNDER A MINUTE" if w < 60 else "OVER A MINUTE",
                           wall_s=w))

    record = {"stage": 2, "case": spec["case"], "solver": a.solver,
              "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "skipped": sorted(skip), "results": results,
              "per_level_wall_s": per_level_wall,
              "wall_clock_s": round(time.time() - t_all, 2)}
    out.mkdir(parents=True, exist_ok=True)
    (out / "STAGE2_RECORD.json").write_text(json.dumps(record, indent=2, default=str) + "\n")

    reds = [r for r in results if not r.get("green")]
    print(L.state_line(STAGE, "EXIT", "GREEN" if not reds else "RED",
                       reds=len(reds), checks=len(results),
                       wall_s=record["wall_clock_s"]))
    return 0 if not reds else 5


if __name__ == "__main__":
    try:
        sys.exit(main())
    except L.Refusal as e:
        print(L.state_line(STAGE, "REFUSAL", e.code, detail=e.detail))
        sys.exit(2)
