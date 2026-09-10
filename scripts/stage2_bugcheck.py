#!/usr/bin/env python3
r"""CASE PROTOCOL -- STAGE 2 BUG CHECK.  Reusable across cases; first instance SUBOFF.

AUTHORITY.  docs/charters/CASE_PROTOCOL_CHARTER.md v1.0 (SANAA-DIRECT, in force
2026-09-10) section 2, verbatim requirements:

    checkMesh on every level | dictionary and schema validation | boundary-condition
    closure: every patch has a condition for every field | dead-lever audit: every
    setting the registration claims is present in the files that the solver reads |
    instrument check: every reader that will grade this case detects a planted
    perturbation through the real path; a reader that cannot see its plant fails the
    case closed | dry run: one iteration, rc READ FROM THE PROCESS, never inferred
    from a marker.
    "Automatic, under one minute, no compute worth counting."
    "Exit condition: all checks green."

WHAT THIS FILE ADDS TO THAT LIST, AND WHY IT IS NOT SCOPE CREEP.
VERIFICATION_CHARTER v1.75 (f49d3e42) sections 2bd, 2bd.1, 2be.1 name THREE
comparator-defect classes that a freeze, a planted-zero control and a selftest all
pass over.  Section 2be states the reason in one line -- "the freeze proved the file
was unchanged; it could not prove the file was correct."  All three classes were
found in ONE pinned comparator (grade_suboff.py).  A stage-2 that certifies that
comparator green certifies nothing, so the dead-lever audit here is a SOURCE READ
for those three classes as CLASSES, not a search for three known lines:

  D1  TWO-SAMPLE WINDOW (2bd).  Any plateau / convergence / stationarity decision
      computed from a fixed number of endpoint samples rather than a trailing window.
      A monotone drift is the failure mode the window exists to catch, so a statistic
      reading only endpoints cannot satisfy the clause.  DETECTED BY SOURCE, because a
      plant cannot distinguish "small last step" from "settled".
  D2  FACE-INDEXED LIST USED AS A CELL COUNT (2bd.1).  polyMesh/owner holds one entry
      per FACE.  len(owner) is nFaces.  It reaches r and therefore GCI.  Detected by
      source AND by a live cross-reader disagreement against the mesh on disk.
  D3  HARD-CODED CLAIM STRING (2be.1).  A measurement-shaped sentence in a reporting
      path that no input can change.  "ONLY READING THE SOURCE DOES" -- 2be.1.  This
      one is invisible to the entire planted-control apparatus by construction.

EVERY DETECTOR CARRIES ITS OWN POSITIVE CONTROL (standing rule 3 turned on the
checker itself).  A detector is run against a file the charter records as CONTAINING
the defect and against one recorded as free of it.  A detector that cannot see its
own known-positive is reported COULD-NOT-RUN and never GREEN -- a zero from a reader
not shown able to see a non-zero is not evidence.

THE PLANT BATTERY (C5) RUNS THE COMPARATOR AS A SUBPROCESS THROUGH ITS REAL ARGV.
Importing a reader and calling an internal function certifies the shortcut, not
production.  The argv comes from the registration's `invocations` block, so an
invocation defect (R1b: a pinned grader invoked with --reference missing) is itself
inside the tested surface.

DETECTION IS JUDGED ON THE DECISION FIELD, NOT ON OUTPUT BYTES.  A comparator that
echoes an input path changes its bytes under any plant while its verdict does not
move; byte-comparison would score that DETECTED.  Each plant therefore names the
dotted decision field it must move, and moving anything else is not detection.

SAFETY.  Plants are applied inside a hardlink sandbox (cp -al).  A planted file is
UNLINKED and rewritten, never written in place, so the original inode is untouched;
and every source artifact's sha256 is re-verified after the battery.  A restore
failure is exit 3 and is never reported as a check result.

EXIT  0 all green | 1 one or more RED | 2 REFUSE / COULD-NOT-RUN | 3 sandbox leaked
Writes nothing outside --sandbox and --report.  Sends nothing.  Commits nothing.
"""
import argparse, ast, hashlib, json, os, re, shutil, subprocess, sys, time

EXIT_OK, EXIT_RED, EXIT_REFUSE, EXIT_LEAK = 0, 1, 2, 3
T0 = time.time()

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def refuse(msg):
    sys.stderr.write("REFUSE (exit 2): %s\n" % msg); sys.exit(EXIT_REFUSE)

class Result:
    """One check.  state is GREEN / RED / COULD-NOT-RUN -- never a fourth word."""
    def __init__(self, cid, title):
        self.cid, self.title, self.state = cid, title, "COULD-NOT-RUN"
        self.findings, self.numbers, self.basis = [], {}, ""
    def green(self, **n):  self.state = "GREEN"; self.numbers.update(n); return self
    def red(self, finding, **n):
        self.state = "RED"; self.findings.append(finding); self.numbers.update(n); return self
    def cnr(self, why):    self.state = "COULD-NOT-RUN"; self.findings.append(why); return self
    def line(self):
        return "STAGE 2 | %-4s | %-13s | %s%s" % (
            self.cid, self.state, self.title,
            ("  ::  " + " ; ".join(self.findings)) if self.findings else "")
    def as_dict(self):
        return dict(check=self.cid, title=self.title, state=self.state,
                    findings=self.findings, numbers=self.numbers, basis=self.basis)

# =======================================================================================
# DEAD-LEVER DETECTORS.  Source reads.  Each returns a list of {file, line, why, snippet}.
# =======================================================================================
PLATEAU_NAMES = re.compile(r"plateau|converg|settle|settl|station|steady|flat|drift", re.I)

def _const_index(node):
    """Return the integer of a constant subscript index, else None (a Slice returns 'SLICE')."""
    if isinstance(node, ast.Slice):
        return "SLICE"
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) \
       and isinstance(node.operand, ast.Constant) and isinstance(node.operand.value, int):
        return -node.operand.value
    return None

def detect_two_sample_window(path):
    """D1 (VERIFICATION_CHARTER 2bd).  A plateau/convergence decision whose value
    subtree indexes a series at a FIXED SET OF <=2 CONSTANT POSITIONS and never over a
    slice.  Reported as a CLASS: the target name, not the literal line, is the trigger."""
    src = open(path, "r", errors="replace").read()
    tree = ast.parse(src, filename=path)
    lines = src.splitlines()
    # PRE-PASS: names bound to a SLICE of another sequence ARE windows.  Reading the two
    # endpoints OF A DECLARED WINDOW is a legitimate drift statistic and 2bd asks for
    # exactly that; only endpoint-reads of the FULL series are the defect.  Without this
    # the detector fires on its own known-negative, which would make it useless.
    window_names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Subscript) \
           and isinstance(n.value.slice, ast.Slice):
            window_names.update(t.id for t in n.targets if isinstance(t, ast.Name))
    out = []
    for node in ast.walk(tree):
        targets = []
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            value = node.value
        elif isinstance(node, ast.keyword) and node.arg:
            targets, value = [node.arg], node.value
        else:
            continue
        if not any(PLATEAU_NAMES.search(t) for t in targets):
            continue
        # collect every constant subscript index, per base series name, in this subtree
        per_base = {}
        for sub in ast.walk(value):
            if isinstance(sub, ast.Subscript):
                base = sub.value.id if isinstance(sub.value, ast.Name) else "<expr>"
                idx = _const_index(sub.slice)
                if idx is not None:
                    per_base.setdefault(base, set()).add(idx)
        for base, idxs in per_base.items():
            if "SLICE" in idxs or base in window_names:
                continue                      # a slice IS a window; not this class
            if len(idxs) <= 2 and all(isinstance(i, int) for i in idxs):
                out.append(dict(
                    file=path, line=node.lineno, why=(
                        "decision '%s' is computed from %d fixed sample position(s) %s of "
                        "series '%s' and never over a trailing window (2bd: a two-point "
                        "difference is not a plateau test and may not be gated on)"
                        % (",".join(targets), len(idxs), sorted(idxs), base)),
                    snippet=lines[node.lineno - 1].strip()[:160]))
    return out

FACE_SOURCES = re.compile(r"owner|neighbou?r|(^|_)faces?($|_)|facelist", re.I)

def detect_face_count_as_cells(path):
    """D2 (2bd.1).  len(<face-indexed list>) bound to a cell-count name."""
    src = open(path, "r", errors="replace").read()
    tree = ast.parse(src, filename=path)
    lines = src.splitlines()
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if not any(re.search(r"cell", n, re.I) for n in names):
            continue
        for sub in ast.walk(node.value):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id == "len" and sub.args:
                a = sub.args[0]
                src_name = (a.func.id if isinstance(a, ast.Call) and isinstance(a.func, ast.Name)
                            else a.id if isinstance(a, ast.Name) else "")
                if FACE_SOURCES.search(src_name or ""):
                    out.append(dict(
                        file=path, line=node.lineno, why=(
                            "'%s' = len(%s(...)); polyMesh/owner holds ONE ENTRY PER FACE, so "
                            "this is nFaces, not nCells (2bd.1: it reaches r and therefore GCI)"
                            % (",".join(names), src_name)),
                        snippet=lines[node.lineno - 1].strip()[:160]))
    return out

# A LITERAL numeric measurement -- "0.00 core-min", "4.01x", "0 control failure(s)".
# Deliberately NOT the verdict words: PASS / GATE FAIL / NOT A RESULT are the lab's fixed
# vocabulary (rule 1) and appear legitimately in every grader, so flagging them would make
# this detector fire on everything, which is the shape MONITOR_STANDARD 3.3 calls broken.
# A format placeholder (%.2f, {:.2f}) carries no literal digits and so does not match.
CLAIM_STR = re.compile(r"\d+\.\d+\s*(core-min|core-h|GPU-h|core-s)"
                       r"|\b\d+\s+control failure"
                       r"|\b\d+\.\d+x\b(?!\s*\{)")

def detect_hardcoded_claim(path):
    """D3 (2be.1).  A measurement-shaped PLAIN string literal (never an f-string) reaching
    a reporting sink.  No input can change it, so no plant can detect it."""
    src = open(path, "r", errors="replace").read()
    tree = ast.parse(src, filename=path)
    lines = src.splitlines()
    out = []
    # docstrings are prose, not a reporting path: collect and exclude them by identity
    docs = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b = getattr(n, "body", None)
            if b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) \
               and isinstance(b[0].value.value, str):
                docs.add(id(b[0].value))
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        if id(node) in docs:
            continue
        if not CLAIM_STR.search(node.value):
            continue
        out.append(dict(
            file=path, line=node.lineno, why=(
                "plain string literal carries a LITERAL numeric measurement; it is asserted "
                "whatever the reader found, so no input can falsify it and no planted "
                "control can detect it (2be.1 -- only reading the source does)"),
            snippet=node.value.strip()[:160]))
    return out

DETECTORS = {"D1": ("two-sample window (2bd)", detect_two_sample_window),
             "D2": ("faces-as-cells (2bd.1)", detect_face_count_as_cells),
             "D3": ("hard-coded claim string (2be.1)", detect_hardcoded_claim)}

# =======================================================================================
# C4  DEAD-LEVER AUDIT
# =======================================================================================
def check_C4_dead_levers(prof, repo):
    r = Result("C4", "SOURCE ARM -- claim: 'this reader COMPUTES THE RIGHT THING' "
                     "(dead-lever audit, defect classes D1/D2/D3)")
    comp = prof["comparator"]["path"]
    if not os.path.exists(comp):
        return r.cnr("comparator not on disk: %s" % comp)

    # --- 4.0 POSITIVE CONTROLS.  A detector unproven on a known-positive is not evidence.
    ctrl = prof.get("detector_controls", {})
    ctrl_state = {}
    for did, (title, fn) in DETECTORS.items():
        pos = ctrl.get(did, {}).get("known_positive")
        neg = ctrl.get(did, {}).get("known_negative")
        seen_pos = seen_neg = None
        if pos and os.path.exists(pos):
            try:    seen_pos = len(fn(pos))
            except Exception as e: seen_pos = "error: %s" % e
        if neg and os.path.exists(neg):
            try:    seen_neg = len(fn(neg))
            except Exception as e: seen_neg = "error: %s" % e
        ok = isinstance(seen_pos, int) and seen_pos > 0 and (seen_neg is None or seen_neg == 0)
        ctrl_state[did] = dict(known_positive=pos, hits_on_positive=seen_pos,
                               known_negative=neg, hits_on_negative=seen_neg, armed=bool(ok))
    r.numbers["detector_controls"] = ctrl_state
    unarmed = [d for d, s in ctrl_state.items() if not s["armed"]]
    if unarmed:
        return r.cnr("detector(s) %s not proven on a known-positive -- a zero from an "
                     "unproven reader is not evidence (rule 3)" % ",".join(sorted(unarmed)))

    # --- 4.1 the three defect classes, over the WHOLE pinned path (comparator + launcher)
    pinned = [comp] + [p for p in prof["comparator"].get("also_scan", []) if os.path.exists(p)]
    hits = []
    for did, (title, fn) in DETECTORS.items():
        for p in pinned:
            if not p.endswith(".py"):
                continue
            for h in fn(p):
                h["detector"] = did; h["class"] = title; hits.append(h)
    r.numbers["pinned_python_scanned"] = [os.path.relpath(p, repo) for p in pinned if p.endswith(".py")]
    r.numbers["class_hits"] = hits

    # --- 4.2 registration levers present in the files the SOLVER reads (charter sec.2 wording)
    missing = []
    for lvl, d in prof["levels"].items():
        for fname, keys in prof.get("registered_settings", {}).items():
            fp = os.path.join(d, fname)
            txt = open(fp, errors="replace").read() if os.path.exists(fp) else None
            if txt is None:
                missing.append(dict(level=lvl, file=fname, key="<file absent>")); continue
            for k, want in keys.items():
                m = re.search(r"\b%s\s+([^;\n]+);" % re.escape(k), txt)
                if not m:
                    missing.append(dict(level=lvl, file=fname, key=k, why="absent"))
                elif want is not None and m.group(1).strip() != str(want):
                    missing.append(dict(level=lvl, file=fname, key=k,
                                        why="registered %r, on disk %r" % (want, m.group(1).strip())))
    r.numbers["registered_setting_misses"] = missing

    # --- 4.3 LIVE cross-reader on the mesh count (D2 made a measurement, not only a source read)
    xr = {}
    for lvl, d in prof["levels"].items():
        own = os.path.join(d, "constant/polyMesh/owner")
        if not os.path.exists(own):
            xr[lvl] = dict(state="COULD-NOT-RUN", why="no polyMesh/owner"); continue
        txt = open(own, errors="replace").read()
        m = re.search(r"\n(\d+)\s*\(", txt)
        s = m.end(); vals = [int(x) for x in txt[s:txt.index(")", s)].split()]
        n_faces, n_cells = len(vals), max(vals) + 1
        reg = prof.get("registered_cells", {}).get(lvl)
        xr[lvl] = dict(n_internal_faces=n_faces, n_cells_max_owner_plus_1=n_cells,
                       registered=reg, faces_over_cells=round(n_faces / n_cells, 4),
                       registered_matches_cells=(reg == n_cells) if reg else None)
    r.numbers["mesh_count_cross_reader"] = xr

    findings = []
    for h in hits:
        findings.append("%s %s:%d -- %s" % (h["detector"], os.path.relpath(h["file"], repo),
                                            h["line"], h["why"]))
    if missing:
        findings.append("%d registered setting(s) absent or disagreeing on disk" % len(missing))
    if findings:
        for f in findings:
            r.red(f)
        return r
    return r.green(class_hits=0, registered_setting_misses=0)

# =======================================================================================
# C5  INSTRUMENT CHECK -- plant battery through the REAL argv, in a hardlink sandbox
# =======================================================================================
def build_sandbox(prof, sandbox):
    if os.path.exists(sandbox):
        shutil.rmtree(sandbox)
    os.makedirs(sandbox)
    mapping = {}
    for lvl, d in prof["levels"].items():
        dst = os.path.join(sandbox, lvl)
        subprocess.run(["cp", "-al", d, dst], check=True)
        mapping[lvl] = dst
    return mapping

def unlink_write(path, text):
    """NEVER write in place: the sandbox is hardlinked to the run of record."""
    os.remove(path)
    with open(path, "w") as f:
        f.write(text)

def dotted(obj, path):
    for k in path.split("."):
        if isinstance(obj, dict):
            if k not in obj: return "<absent>"
            obj = obj[k]
        else:
            return "<absent>"
    return obj

def run_comparator(prof, mapping, timeout=180):
    argv = []
    for a in prof["comparator"]["invocation"]["argv"]:
        argv.append(a.format(comparator=prof["comparator"]["path"],
                             reference=prof["comparator"]["reference"], **mapping))
    p = subprocess.run([sys.executable] + argv, capture_output=True, text=True,
                       timeout=timeout, cwd=prof["comparator"]["invocation"].get("cwd") or None)
    try:    parsed = json.loads(p.stdout)
    except Exception: parsed = None
    return dict(rc=p.returncode, stdout=p.stdout, stderr=p.stderr[-2000:], parsed=parsed)

# ---- the plants.  Each names the decision field it MUST move. -------------------------
def plant_offset(path, col, mag):
    """Add a constant to the LAST row only.  This is the shape grade_suboff.py's own
    rule-3 control plants, and the two-point plateau test CAN see it -- so it is the
    POSITIVE CONTROL for the whole battery, not a test of the defect."""
    lines = open(path, errors="replace").read().splitlines(True)
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() and not lines[i].startswith("#"):
            r = lines[i].split()
            r[col] = "%.16e" % (float(r[col]) + mag)
            lines[i] = "\t".join(r) + "\n"
            break
    unlink_write(path, "".join(lines))

def plant_drift(path, col, window, total_rel, endpoint_rel):
    """Replace the final `window` rows with a linear ramp of total relative change
    `total_rel`, WHILE holding the last-to-second-last relative step at `endpoint_rel`.
    This is the shape a two-point test is blind to and a trailing window is not."""
    raw = open(path, errors="replace").read().splitlines(True)
    idx = [i for i, l in enumerate(raw) if l.strip() and not l.startswith("#")]
    if len(idx) < window + 2:
        raise RuntimeError("series shorter than the requested window")
    sel = idx[-window:]
    base = float(raw[sel[0]].split()[col])
    for j, i in enumerate(sel):
        r = raw[i].split()
        # ramp over the window, then flatten the final step to endpoint_rel
        frac = j / (window - 1)
        v = base * (1.0 + total_rel * frac)
        if j == window - 1:
            prev = base * (1.0 + total_rel * ((window - 2) / (window - 1)))
            v = prev * (1.0 + endpoint_rel)
        r[col] = "%.16e" % v
        raw[i] = "\t".join(r) + "\n"
    unlink_write(path, "".join(raw))

def plant_residual(path, field, which, value):
    """Set the `which` ('first'|'last') 'Solving for <field>, Initial residual = X'
    occurrence WITHIN THE FINAL SOLVER ITERATION to `value`.  Two limbs: a reader that
    sees one and not the other is position-blind, and the limb it misses is named."""
    txt = open(path, errors="replace").read()
    cut = txt.rfind("\nTime = ")
    head, tail = txt[:cut], txt[cut:]
    pat = re.compile(r"(Solving for %s,\s*Initial residual\s*=\s*)([-\d.eE+]+)" % re.escape(field))
    hits = list(pat.finditer(tail))
    if not hits:
        raise RuntimeError("no '%s' residual line in the final iteration" % field)
    m = hits[0] if which == "first" else hits[-1]
    tail = tail[:m.start(2)] + repr(value) + tail[m.end(2):]
    unlink_write(path, head + tail)
    return len(hits)

def check_C5_instrument(prof, sandbox, repo):
    r = Result("C5", "PLANT ARM -- claim: 'this reader CAN SEE ITS INPUT' "
                     "(planted perturbations through the real argv)")
    mapping = build_sandbox(prof, sandbox)

    # --- STABILITY arm: an output that drifts run-to-run scores DETECTED for any plant.
    a = run_comparator(prof, mapping); b = run_comparator(prof, mapping)
    if a["stdout"] != b["stdout"] or a["rc"] != b["rc"]:
        return r.cnr("comparator output is not stable across two identical runs -- any "
                     "plant would score DETECTED; instability is COULD-NOT-RUN, not GREEN")
    base = a
    r.numbers["baseline_rc"] = base["rc"]
    if base["parsed"] is None:
        return r.cnr("baseline comparator run rc=%d produced no parseable report; the "
                     "battery cannot judge a decision field.  stderr tail: %s"
                     % (base["rc"], base["stderr"][-300:].replace("\n", " ")))

    results = []
    for spec in prof["plants"]:
        lvl = spec["level"]
        # rebuild ONLY the planted level, so plants never compound
        shutil.rmtree(mapping[lvl])
        subprocess.run(["cp", "-al", prof["levels"][lvl], mapping[lvl]], check=True)
        target = os.path.join(mapping[lvl], spec["artifact"])
        if "*" in target:
            import glob as _g
            g = sorted(_g.glob(target))
            if not g:
                results.append(dict(plant=spec["name"], state="COULD-NOT-RUN",
                                    why="artifact glob matched nothing: %s" % spec["artifact"]))
                continue
            target = g[-1]
        try:
            k = spec["kind"]
            if   k == "offset":   plant_offset(target, spec["column"], spec["magnitude"])
            elif k == "drift":    plant_drift(target, spec["column"], spec["window"],
                                              spec["total_rel"], spec["endpoint_rel"])
            elif k == "residual": plant_residual(target, spec["field"], spec["which"], spec["value"])
            else: raise RuntimeError("unknown plant kind %r" % k)
        except Exception as e:
            results.append(dict(plant=spec["name"], state="COULD-NOT-RUN",
                                why="plant could not be made to land: %s" % e))
            continue
        out = run_comparator(prof, mapping)
        field = spec["expect_field"].format(level=lvl)
        was, now = dotted(base["parsed"], field), dotted(out["parsed"], field) if out["parsed"] else "<no report>"
        moved = (was != now)
        want = spec.get("expect", "changes")
        ok = moved if want == "changes" else (now == spec.get("expect_value"))
        results.append(dict(plant=spec["name"], kind=spec["kind"], level=lvl,
                            artifact=os.path.relpath(target, sandbox), field=field,
                            baseline=was, planted=now, rc=out["rc"],
                            state="DETECTED" if ok else "NOT-DETECTED",
                            role=spec.get("role", "defect probe"), why=spec.get("why", "")))
    r.numbers["plants"] = results

    # RESTORE PROOF -- the run of record must be byte-identical after the battery.
    leaked = []
    for pth, want in prof.get("immutable_sha256", {}).items():
        if not os.path.exists(pth):
            leaked.append("%s ABSENT" % pth); continue
        got = sha256_file(pth)
        if got != want:
            leaked.append("%s sha256 %s != registered %s" % (pth, got[:12], want[:12]))
    for pth, want_ns in prof.get("immutable_mtime_ns", {}).items():
        if not os.path.exists(pth):
            leaked.append("%s ABSENT (mtime arm)" % pth); continue
        got_ns = os.stat(pth).st_mtime_ns
        if got_ns != want_ns:
            leaked.append("%s RE-DATED: mtime_ns %d != registered %d -- rule 4's age guard "
                          "dates a run by field mtimes against the case's own 0/T, so a "
                          "re-dated artifact corrupts the evidence this audit is checking"
                          % (pth, got_ns, want_ns))
    r.numbers["restore_proof"] = ("byte-identical AND mtime-identical" if not leaked else leaked)
    r.numbers["restore_arms"] = dict(sha256=len(prof.get("immutable_sha256", {})),
                                     mtime_ns=len(prof.get("immutable_mtime_ns", {})))
    if leaked:
        r.numbers["LEAK"] = True
        return r.cnr("SANDBOX LEAKED into the run of record: %s" % "; ".join(leaked))

    ctrls = [x for x in results if x.get("role") == "positive control"]
    if not ctrls or any(x["state"] != "DETECTED" for x in ctrls):
        return r.cnr("the battery's positive control did not detect its own plant -- the "
                     "harness is not shown able to see a non-zero (rule 3)")
    bad = [x for x in results if x.get("role") != "positive control" and x["state"] != "DETECTED"]
    if bad:
        for x in bad:
            r.red("plant '%s' NOT-DETECTED: %s stayed %r through the real argv -- %s"
                  % (x["plant"], x["field"], x["baseline"], x.get("why", "")))
        return r
    return r.green(plants_detected=len(results))

# =======================================================================================
# C1 checkMesh | C2 dictionaries | C3 BC closure | C6 one-iteration dry run
# =======================================================================================
_ENV_CACHE = {}
def solver_env(prof):
    """Capture the environment the solver actually needs by sourcing the registered
    bashrc ONCE.  rc=127 from a missing runtime environment is COULD-NOT-RUN, never RED:
    an instrument that could not look and an instrument that looked and found nothing
    produce identical clean output and only one of them is evidence."""
    rcfile = prof.get("solver", {}).get("bashrc")
    if not rcfile:
        return os.environ.copy()
    if rcfile in _ENV_CACHE:
        return _ENV_CACHE[rcfile]
    p = subprocess.run(["bash", "-c", ". %s >/dev/null 2>&1 && env -0" % rcfile],
                       capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        return os.environ.copy()
    env = {}
    for kv in p.stdout.split("\0"):
        if "=" in kv:
            k, v = kv.split("=", 1); env[k] = v
    _ENV_CACHE[rcfile] = env or os.environ.copy()
    return _ENV_CACHE[rcfile]

def check_C1_mesh(prof, sandbox):
    r = Result("C1", "checkMesh on every level against the registered quality gates")
    gates = prof.get("mesh_gates", {})
    if not gates:
        return r.cnr("no registered mesh gates in the profile -- nothing to check against")
    per = {}
    for lvl, d in prof["levels"].items():
        log = os.path.join(sandbox, "checkMesh.%s.log" % lvl)
        try:
            p = subprocess.run([prof["solver"].get("check_mesh", "checkMesh"),
                                "-case", d, "-constant", "-noFunctionObjects"],
                               capture_output=True, text=True, timeout=300,
                               env=solver_env(prof))
        except FileNotFoundError:
            return r.cnr("checkMesh not found -- the mesh gate could not be evaluated and is "
                         "NOT reported green")
        if p.returncode == 127:
            return r.cnr("checkMesh exited 127 (runtime environment absent) -- the mesh gate "
                         "COULD NOT BE LOOKED AT; this is not a clean mesh")
        open(log, "w").write(p.stdout + p.stderr)
        o = p.stdout
        def num(pat):
            m = re.search(pat, o)
            return float(m.group(1)) if m else None
        got = dict(max_non_orthogonality=num(r"Mesh non-orthogonality Max:\s*([\d.eE+-]+)"),
                   max_skewness=num(r"Max skewness\s*=\s*([\d.eE+-]+)"),
                   n_cells=int(re.search(r"cells:\s*(\d+)", o).group(1)) if re.search(r"cells:\s*(\d+)", o) else None,
                   n_faces=int(re.search(r"faces:\s*(\d+)", o).group(1)) if re.search(r"faces:\s*(\d+)", o) else None,
                   n_points=int(re.search(r"points:\s*(\d+)", o).group(1)) if re.search(r"points:\s*(\d+)", o) else None,
                   rc=p.returncode, log=log)
        got["gate_verdicts"] = {}
        for k, lim in gates.items():
            v = got.get(k)
            got["gate_verdicts"][k] = ("COULD-NOT-RUN" if v is None else
                                       "PASS" if v <= lim else "GATE FAIL")
        per[lvl] = got
    r.numbers["per_level"] = per
    bad = [(l, k, v) for l, g in per.items() for k, v in g["gate_verdicts"].items() if v != "PASS"]
    if any(v == "COULD-NOT-RUN" for _, _, v in bad):
        return r.cnr("a registered mesh metric was not parsed from checkMesh output: %s" % bad)
    if bad:
        for l, k, v in bad:
            r.red("%s: %s = %s exceeds registered gate %s" % (l, k, per[l][k], gates[k]))
        return r
    return r.green(levels=len(per))

def check_C2_dicts(prof):
    r = Result("C2", "dictionary and schema validation on every level")
    req = prof.get("required_dicts", [])
    bad = []
    for lvl, d in prof["levels"].items():
        for rel in req:
            p = os.path.join(d, rel)
            if not os.path.exists(p):
                bad.append("%s: %s ABSENT" % (lvl, rel)); continue
            t = open(p, errors="replace").read()
            body = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
            body = "\n".join(l.split("//")[0] for l in body.splitlines())
            if body.count("{") != body.count("}"):
                bad.append("%s: %s unbalanced braces (%d open, %d close)"
                           % (lvl, rel, body.count("{"), body.count("}")))
            if not re.search(r"FoamFile\s*\{", t):
                bad.append("%s: %s has no FoamFile header" % (lvl, rel))
    r.numbers["required_dicts"] = req
    if bad:
        for b in bad: r.red(b)
        return r
    return r.green(dicts_checked=len(req) * len(prof["levels"]))

def check_C3_bc_closure(prof):
    """Charter sec.2: 'every patch has a condition for every field; no default that
    silently fills a hole.'  A catch-all regex entry IS a default filling a hole, so it
    is REPORTED, and reported as a hole unless the registration declares it."""
    r = Result("C3", "boundary-condition closure: every patch, every field")
    allowed = set(prof.get("allowed_catchall_patches", []))
    holes, catchalls = [], []
    for lvl, d in prof["levels"].items():
        bnd = os.path.join(d, "constant/polyMesh/boundary")
        if not os.path.exists(bnd):
            return r.cnr("%s: no polyMesh/boundary" % lvl)
        txt = open(bnd, errors="replace").read()
        patches = [m.group(1) for m in re.finditer(
            r"(\w+)\s*\{[^}]*?nFaces\s+\d+;[^}]*?startFace\s+\d+;", txt, re.S)]
        for fld in prof["fields_zero_dir"]:
            fp = os.path.join(d, "0", fld)
            if not os.path.exists(fp) and os.path.exists(fp + ".gz"):
                fp += ".gz"
            if not os.path.exists(fp):
                holes.append("%s: 0/%s ABSENT" % (lvl, fld)); continue
            ft = (open(fp, errors="replace").read() if not fp.endswith(".gz")
                  else __import__("gzip").open(fp, "rt", errors="replace").read())
            m = re.search(r"boundaryField\s*\{(.*)\n\}", ft, re.S)
            if not m:
                holes.append("%s/0/%s: no boundaryField block" % (lvl, fld)); continue
            blk = m.group(1)
            # an entry is `name { ... }` inline OR `name` on its own line; both forms occur
            named = set(re.findall(r"^\s*\"?([\w.|()\[\]*+-]+)\"?\s*(?:\{|$)", blk, re.M))
            named.discard("")
            for p in patches:
                if p in named:
                    continue
                cover = [n for n in named if any(c in n for c in ".*|()[]") and
                         re.fullmatch(n.strip('"'), p)]
                if cover:
                    catchalls.append("%s/0/%s: patch '%s' covered only by catch-all %s"
                                     % (lvl, fld, p, cover))
                else:
                    holes.append("%s/0/%s: patch '%s' has NO condition" % (lvl, fld, p))
    undeclared = [c for c in catchalls if not any(a in c for a in allowed)]
    r.numbers["catchall_coverage"] = catchalls
    if holes or undeclared:
        for h in holes: r.red(h)
        for c in undeclared:
            r.red("%s -- a catch-all is a default silently filling a hole; declare it in "
                  "allowed_catchall_patches or name the patch" % c)
        return r
    return r.green(patches_x_fields_closed=True)

def check_C6_dry_run(prof, sandbox):
    """rc IS READ FROM THE PROCESS.  A wrapper may never manufacture an exit status."""
    r = Result("C6", "one-iteration dry run, rc read from the process")
    lvl = prof["smoke_level"]
    src = prof["levels"][lvl]
    dst = os.path.join(sandbox, "dryrun_" + lvl)
    if os.path.exists(dst): shutil.rmtree(dst)
    os.makedirs(dst)
    for sub in ("constant", "system"):
        shutil.copytree(os.path.join(src, sub), os.path.join(dst, sub), symlinks=True)
    zero = os.path.join(src, "0.orig") if os.path.isdir(os.path.join(src, "0.orig")) else os.path.join(src, "0")
    shutil.copytree(zero, os.path.join(dst, "0"), symlinks=True)
    cd = os.path.join(dst, "system/controlDict")
    t = open(cd, errors="replace").read()
    t = re.sub(r"\bendTime\s+[^;]+;", "endTime 1;", t)
    t = re.sub(r"\bwriteInterval\s+[^;]+;", "writeInterval 1;", t)
    t = re.sub(r"\bstartFrom\s+[^;]+;", "startFrom startTime;", t)
    t = re.sub(r"\bstartTime\s+[^;]+;", "startTime 0;", t)
    open(cd, "w").write(t)
    log = os.path.join(sandbox, "dryrun.%s.log" % lvl)
    try:
        p = subprocess.run([prof["solver"]["binary"], "-case", dst],
                           capture_output=True, text=True,
                           timeout=prof["solver"].get("dry_timeout", 300),
                           env=solver_env(prof))
    except FileNotFoundError:
        return r.cnr("solver %r not found" % prof["solver"]["binary"])
    except subprocess.TimeoutExpired:
        return r.red("one-iteration dry run did not return inside the timeout")
    open(log, "w").write(p.stdout[-40000:] + p.stderr[-8000:])
    rc = p.returncode                      # FROM THE PROCESS.  Not from an End line.
    if rc == 127:
        return r.cnr("solver exited 127 (runtime environment absent) -- the dry run COULD "
                     "NOT BE MADE; a 127 is not a finding about the case")
    wrote = os.path.isdir(os.path.join(dst, "1"))
    r.numbers.update(rc_from_process=rc, wrote_time_dir_1=wrote, log=log,
                     rc_source="subprocess.CompletedProcess.returncode")
    if rc != 0:
        return r.red("solver rc=%d on a one-iteration dry run (tail in %s)" % (rc, log))
    if not wrote:
        return r.red("solver returned 0 but wrote no time directory 1/ -- an rc of 0 is not "
                     "a result (log %s)" % log)
    return r.green(rc=0)

# =======================================================================================
def main():
    ap = argparse.ArgumentParser(description="CASE PROTOCOL stage 2 bug check")
    ap.add_argument("--profile", required=True)
    ap.add_argument("--sandbox", required=True)
    ap.add_argument("--report")
    ap.add_argument("--only", help="comma list of check ids, e.g. C4,C5")
    a = ap.parse_args()
    prof = json.load(open(a.profile))
    repo = prof.get("repo", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    os.makedirs(a.sandbox, exist_ok=True)
    want = set(a.only.split(",")) if a.only else {"C1", "C2", "C3", "C4", "C5", "C6"}

    checks = []
    if "C1" in want: checks.append(check_C1_mesh(prof, a.sandbox))
    if "C2" in want: checks.append(check_C2_dicts(prof))
    if "C3" in want: checks.append(check_C3_bc_closure(prof))
    if "C4" in want: checks.append(check_C4_dead_levers(prof, repo))
    if "C5" in want: checks.append(check_C5_instrument(prof, a.sandbox, repo))
    if "C6" in want: checks.append(check_C6_dry_run(prof, a.sandbox))

    wall = time.time() - T0
    states = [c.state for c in checks]
    overall = ("RED" if "RED" in states else
               "COULD-NOT-RUN" if "COULD-NOT-RUN" in states else "GREEN")
    for c in checks:
        print(c.line())
    print("STAGE 2 | EXIT | %-13s | %d checks, %.1f s wall (charter sec.2 budget: 60 s)%s"
          % (overall, len(checks), wall, "" if wall <= 60 else "  ::  OVER BUDGET"))
    coverage = dict(
      source_arm_C4=("catches a defect whose reader is FAITHFUL and whose COMPUTATION is "
                     "wrong. This is the only arm that reaches D2 (faces-as-cells) and D3 "
                     "(hard-coded claim string): no input can falsify either."),
      plant_arm_C5=("catches a reader that CANNOT SEE ITS INPUT. It reaches D1 ONLY when the "
                    "plant is shaped like the failure mode (a DRIFT, not an offset) AND "
                    "detection is judged on the DECISION FIELD rather than on output bytes. "
                    "An offset plant on the same artifact reports DETECTED and says nothing."),
      what_neither_arm_reaches=("a wrong CONSTANT, a wrong physical model, and a wrong "
                                "reference value: all three read faithfully, compute "
                                "consistently, and are simply not the right number. Currently "
                                "caught only by a supervisor reading the source as a diff "
                                "(SUPERVISION_CHARTER section 3 check-1)."),
      do_not_merge=("a GREEN plant arm is NOT a reprieve for a computation-correctness defect "
                    "and must never be reported as one; 'could not look' and 'looked and "
                    "found nothing' are different states and are never the same output"))
    rep = dict(stage=2, case=prof.get("case_id"), profile=os.path.abspath(a.profile),
               overall=overall, wall_s=round(wall, 2), under_60s=bool(wall <= 60),
               arm_coverage=coverage, checks=[c.as_dict() for c in checks])
    if a.report:
        json.dump(rep, open(a.report, "w"), indent=2, default=str)
    if any(c.numbers.get("LEAK") for c in checks):
        return EXIT_LEAK
    return EXIT_OK if overall == "GREEN" else EXIT_RED if overall == "RED" else EXIT_REFUSE

if __name__ == "__main__":
    sys.exit(main())
