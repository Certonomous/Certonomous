#!/usr/bin/env python3
"""VR5 -- the SHARED-CWD STDOUT COLLISION DETECTOR.

Frozen gate: verification/campaign/VR5_PREREGISTRATION.md.

THE MECHANISM, and this file VERIFIES it rather than assuming it
-----------------------------------------------------------------
`scripts/queue_runner.py` `launch()` keys the STATUS file on the case
(`STATUS.{case_id}`) but keys the launched argv's stdout on the CWD ALONE --
a FIXED BASENAME with no case_id, no pid and no timestamp -- and redirects
into it with a TRUNCATING `>`.  There is no rotation, no backup and no
pre-move.  Two entries sharing a cwd therefore DESTROY each other's verdict
output, silently, and the STATUS file that survives says nothing about it.

This item is a DETECTOR, not a repair.  `scripts/queue_runner.py` is not this
team's file and a patch there is the chief's to route.

WHY THE MECHANISM IS RE-READ FROM SOURCE EVERY RUN
--------------------------------------------------
A detector that hardcodes a line number keeps reporting a hazard after the
hazard is fixed.  `mechanism()` locates the assignment and the redirect in the
runner's own text and classifies them PRESENT / REPAIRED / NOT LOCATED, so a
future repair RETIRES this item instead of being papered over by it.

THE CONTROLS (standing rule 3; VERIFICATION_CHARTER section 2j)
---------------------------------------------------------------
Section 2j.2 asks WHO WROTE THE BYTES THE CONTROL READS.  Every corpus limb
here plants JSON files and a LAUNCH_LOG on DISK and is read back through
`read_corpus()` and `read_launch_log()` -- the SAME readers the real scan
uses, entered at the same door.  Nothing is handed to the reducer as an
in-memory list; a control that supplies its own trigger downstream of the
reader tests the reducer and not the reader.

EXIT CODES
----------
    0   PASS      -- controls behaved; zero REALISED destroys (or the runner
                     mechanism is REPAIRED and the hazard is retired)
    1   GATE FAIL -- at least one REALISED destroy on the live corpus
    2   NOT A RESULT -- a control limb misbehaved, or the mechanism could not
                     be located in the runner source
"""
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
QUEUE_ROOT = REPO / "verification" / "queue"
LAUNCH_LOG = QUEUE_ROOT / "LAUNCH_LOG.tsv"
RUNNER_SRC = REPO / "scripts" / "queue_runner.py"

# The runner's OWN archived-record pattern (queue_runner.py:122), copied so this
# corpus reader excludes exactly what the runner's `is_current_record` excludes.
# An archived record is never relaunched, so it can never collide again.
ARCHIVED_RE = re.compile(r"\.\d{4}-\d{2}-\d{2}T\d{6}Z(\.\d+)?\.json$")


# --------------------------------------------------------------------------
# READERS -- the single door.  Both the live scan and every control limb enter
# through these two functions, from disk.
# --------------------------------------------------------------------------
def read_corpus(queue_root):
    """Every CURRENT queue record under `queue_root`, from disk.

    Returns a list of dicts: path, team, state, case_id, cwd.
    `state` is the queue lifecycle position taken from the path: an entry in
    `launched/` has been handed to the runner, one in `held/` has not, and one
    at a team's top level is what the runner's `d.glob("*.json")` will pick up
    next."""
    out = []
    for p in sorted(queue_root.rglob("*.json")):
        if ARCHIVED_RE.search(p.name):
            continue
        try:
            d = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        cwd = d.get("cwd")
        if not cwd:
            continue
        rel = p.relative_to(queue_root).parts
        team = rel[0] if len(rel) > 1 else "(root)"
        if "launched" in rel:
            state = "launched"
        elif "held" in rel:
            state = "held"
        else:
            state = "queued"
        out.append(dict(path=p, team=team, state=state,
                        case_id=d.get("case_id"), cwd=str(cwd)))
    return out


def read_launch_log(path):
    """Every launch row, from disk.

    The cwd is derived from the status_file column -- the runner writes it as
    `<cwd>/STATUS.<case_id>` (queue_runner.py:496), so the dirname IS the cwd
    the stdout was truncated in.  Joining on the status path rather than on
    case_id keeps the join independent of record renames."""
    rows = []
    if not path.exists():
        return rows
    for ln in path.read_text().splitlines():
        if not ln.strip():
            continue
        f = ln.split("\t")
        if len(f) < 9 or "/STATUS." not in f[8]:
            continue
        rows.append(dict(utc=f[0], team=f[1], case_id=f[2],
                         status_file=f[8], cwd=os.path.dirname(f[8])))
    return rows


# --------------------------------------------------------------------------
# REDUCER
# --------------------------------------------------------------------------
def collide(entries, rows):
    """Two INDEPENDENT populations, joined only for reporting.

    REALISED is a property of the LAUNCH LOG and of nothing else.  A destroy
    that already happened cannot be undone by the later disappearance of the
    record that caused it: an archived, renamed or consumed queue entry leaves
    the truncated stdout exactly as truncated.  Keying REALISED off the
    surviving CURRENT entries therefore UNDERCOUNTS -- measured 2026-08-30, it
    lost the ansys-verification and closure destroys entirely, because those
    cwds no longer carry two current records.  So: any cwd with two or more
    launch rows has already destroyed n-1 stdout records.

    EXPOSURE is a property of the CURRENT CORPUS: a cwd carrying more than one
    current record will collide on its next launch.  An exposure group whose
    cwd has fewer than two launch rows is LATENT -- the destroy is still ahead.

    Returns (realised, exposure), each a list of group dicts."""
    launches = {}
    for r in rows:
        launches.setdefault(r["cwd"], []).append(r)
    for v in launches.values():
        v.sort(key=lambda r: r["utc"])

    realised = []
    for cwd, lz in launches.items():
        if len(lz) < 2:
            continue
        destroyed, cross = [], 0
        for i in range(1, len(lz)):
            victim, killer = lz[i - 1], lz[i]
            destroyed.append(victim)
            if victim["case_id"] != killer["case_id"]:
                cross += 1
        realised.append(dict(cwd=cwd, launches=lz, destroyed=destroyed, cross=cross,
                             kind="REALISED"))
    realised.sort(key=lambda g: (-len(g["destroyed"]), g["cwd"]))

    by_cwd = {}
    for e in entries:
        by_cwd.setdefault(e["cwd"], []).append(e)
    exposure = []
    for cwd, es in by_cwd.items():
        if len(es) < 2:
            continue
        lz = launches.get(cwd, [])
        exposure.append(dict(cwd=cwd, entries=es, launches=lz,
                             kind="REALISED" if len(lz) >= 2 else "LATENT"))
    exposure.sort(key=lambda g: (-len(g["entries"]), g["cwd"]))
    return realised, exposure


# --------------------------------------------------------------------------
# MECHANISM -- read the runner's own source, never a remembered line number
# --------------------------------------------------------------------------
def mechanism(text):
    """Classify the runner source: PRESENT / REPAIRED / NOT LOCATED.

    PRESENT    the stdout path is built from the cwd with a basename carrying
               no case_id, pid or timestamp, AND the redirect truncates.
    REPAIRED   the basename is keyed (case_id/pid/stamp) or the redirect
               appends -- the hazard is gone and this item should be retired.
    NOT LOCATED  neither shape is in the file; the detector cannot verify its
               own premise and must refuse rather than report a stale hazard."""
    assign = redirect = None
    for i, ln in enumerate(text.splitlines(), 1):
        s = ln.strip()
        if re.match(r"^out\s*=\s*cwd\s*/", s):
            assign = (i, s)
        if "{out}" in s and ">" in s:
            redirect = (i, s)
    if assign is None or redirect is None:
        return "NOT LOCATED", assign, redirect, "no `out = cwd / ...` and/or no `{out}` redirect in the source"
    keyed = [t for t in ("case_id", "pid", "utc", "stamp", "time") if t in assign[1]]
    appends = ">> '{out}'" in redirect[1] or '>> "{out}"' in redirect[1]
    if keyed:
        return "REPAIRED", assign, redirect, "stdout basename now keyed on %s" % ", ".join(keyed)
    if appends:
        return "REPAIRED", assign, redirect, "redirect appends rather than truncates"
    return "PRESENT", assign, redirect, "fixed basename per cwd, truncating redirect"


# --------------------------------------------------------------------------
# CONTROLS -- planted on disk, read back through the real readers
# --------------------------------------------------------------------------
def _plant(root, team, state, case_id, cwd):
    d = root / team / state if state != "queued" else root / team
    d.mkdir(parents=True, exist_ok=True)
    (d / (case_id + ".json")).write_text(json.dumps(
        dict(case_id=case_id, cwd=cwd, team=team)) + "\n")


def _plant_log(path, triples):
    path.write_text("".join(
        "\t".join([utc, team, cid, "1", "1", "1", "1.0", "0" * 40,
                   os.path.join(cwd, "STATUS." + cid)]) + "\n"
        for utc, team, cid, cwd in triples))


def controls():
    """Five limbs.  Three must FIRE, one must stay SILENT on BOTH populations,
    one exercises the mechanism reader.  Every corpus limb is written to DISK
    and re-read through `read_corpus` / `read_launch_log` -- the same door the
    live scan uses (charter 2j.2: ask who wrote the bytes the control reads)."""
    ok = True
    t = Path(tempfile.mkdtemp(prefix="vr5_ctl_"))
    try:
        return _controls(t)
    finally:
        # A monitor that litters the temp filesystem every tick is its own defect.
        shutil.rmtree(t, ignore_errors=True)


def _controls(t):
    ok = True

    # C1 (+, REALISED): two entries share a cwd AND both launched.
    q1 = t / "q1"
    _plant(q1, "planted", "launched", "PLANT_A", "/planted/shared")
    _plant(q1, "planted", "launched", "PLANT_B", "/planted/shared")
    lg1 = t / "log1.tsv"
    _plant_log(lg1, [("2026-01-01T00:00:00Z", "planted", "PLANT_A", "/planted/shared"),
                     ("2026-01-01T01:00:00Z", "planted", "PLANT_B", "/planted/shared")])
    r1, x1 = collide(read_corpus(q1), read_launch_log(lg1))
    hit = [g for g in r1 if g["cwd"] == "/planted/shared"]
    if hit and len(hit[0]["destroyed"]) == 1 and hit[0]["cross"] == 1 and len(x1) == 1:
        print("  control C1 +: planted shared cwd with 2 launches -> REALISED, "
              "1 destroyed, 1 cross-case, 1 exposure group  (FIRED)")
    else:
        print("  CONTROL C1 FAIL: planted shared+launched pair not reported REALISED")
        ok = False

    # C2 (-, SILENT): two entries with DISTINCT cwds, both launched.
    q2 = t / "q2"
    _plant(q2, "planted", "launched", "PLANT_C", "/planted/alpha")
    _plant(q2, "planted", "launched", "PLANT_D", "/planted/beta")
    lg2 = t / "log2.tsv"
    _plant_log(lg2, [("2026-01-01T00:00:00Z", "planted", "PLANT_C", "/planted/alpha"),
                     ("2026-01-01T01:00:00Z", "planted", "PLANT_D", "/planted/beta")])
    r2, x2 = collide(read_corpus(q2), read_launch_log(lg2))
    if r2 or x2:
        print("  CONTROL C2 FAIL: distinct cwds reported as a collision -> %s"
              % [g["cwd"] for g in r2 + x2])
        ok = False
    else:
        print("  control C2 -: planted distinct cwds correctly SILENT on BOTH "
              "populations (0 realised, 0 exposure)")

    # C3 (+, LATENT): shared cwd, only ONE launch -- exposure LATENT, NOT realised.
    q3 = t / "q3"
    _plant(q3, "planted", "launched", "PLANT_E", "/planted/latent")
    _plant(q3, "planted", "held", "PLANT_F", "/planted/latent")
    lg3 = t / "log3.tsv"
    _plant_log(lg3, [("2026-01-01T00:00:00Z", "planted", "PLANT_E", "/planted/latent")])
    r3, x3 = collide(read_corpus(q3), read_launch_log(lg3))
    if not r3 and len(x3) == 1 and x3[0]["kind"] == "LATENT":
        print("  control C3 +: planted shared cwd with 1 launch -> LATENT exposure, "
              "0 realised  (FIRED, correctly not REALISED)")
    else:
        print("  CONTROL C3 FAIL: single-launch shared cwd not classified LATENT")
        ok = False

    # C5 (+, REALISED WITHOUT A SURVIVING RECORD): the destroy is a property of
    # the LOG.  Two launches into a cwd whose queue records are all gone must
    # still be REALISED -- this is the exact limb whose absence made an earlier
    # draft of this detector lose the ansys-verification and closure destroys.
    q5 = t / "q5"
    (q5 / "planted").mkdir(parents=True, exist_ok=True)
    lg5 = t / "log5.tsv"
    _plant_log(lg5, [("2026-01-01T00:00:00Z", "planted", "PLANT_G", "/planted/gone"),
                     ("2026-01-01T01:00:00Z", "planted", "PLANT_H", "/planted/gone")])
    r5, x5 = collide(read_corpus(q5), read_launch_log(lg5))
    if len(r5) == 1 and len(r5[0]["destroyed"]) == 1 and not x5:
        print("  control C5 +: 2 launches into a cwd with ZERO surviving records "
              "-> still REALISED, 0 exposure  (FIRED)")
    else:
        print("  CONTROL C5 FAIL: a destroy vanished when its queue records did "
              "(realised=%d exposure=%d)" % (len(r5), len(x5)))
        ok = False

    # C4: the MECHANISM reader must return all three answers, not just one.
    real = mechanism(RUNNER_SRC.read_text())[0]
    rep = mechanism('        out = cwd / f"launcher.{case_id}.out"\n'
                    '        inner = ("x > \'{out}\' 2>&1")\n')[0]
    app = mechanism('        out = cwd / "launcher.queue.out"\n'
                    '        inner = ("x >> \'{out}\' 2>&1")\n')[0]
    nil = mechanism("def launch():\n    return 0\n")[0]
    if (rep, app, nil) == ("REPAIRED", "REPAIRED", "NOT LOCATED"):
        print("  control C4 +: mechanism reader returns REPAIRED (keyed), "
              "REPAIRED (append) and NOT LOCATED on planted sources; "
              "live runner reads %s" % real)
    else:
        print("  CONTROL C4 FAIL: mechanism reader gave (%s, %s, %s), "
              "expected (REPAIRED, REPAIRED, NOT LOCATED)" % (rep, app, nil))
        ok = False
    return ok


def main():
    print("VR5 -- shared-cwd stdout collision detector "
          "(frozen: verification/campaign/VR5_PREREGISTRATION.md)")
    print("  repo=%s" % REPO)

    print("CONTROLS (rule 3; charter 2j.2 -- planted on disk, read back "
          "through the real corpus reader):")
    if not controls():
        print("VERDICT: NOT A RESULT -- a control limb misbehaved")
        return 2

    state, assign, redirect, why = mechanism(RUNNER_SRC.read_text())
    print("MECHANISM (read from %s, not from a remembered line number):"
          % RUNNER_SRC.relative_to(REPO))
    print("    state=%s -- %s" % (state, why))
    if assign:
        print("    :%d  %s" % assign)
    if redirect:
        print("    :%d  %s" % redirect)
    if state == "NOT LOCATED":
        print("VERDICT: NOT A RESULT -- the runner no longer has the shape this "
              "detector reads; VR5 must be re-read against the new source rather "
              "than keep reporting a hazard it can no longer verify")
        return 2

    entries = read_corpus(QUEUE_ROOT)
    rows = read_launch_log(LAUNCH_LOG)
    realised, exposure = collide(entries, rows)
    latent = [g for g in exposure if g["kind"] == "LATENT"]
    n_dest = sum(len(g["destroyed"]) for g in realised)
    n_cross = sum(g["cross"] for g in realised)

    print("CORPUS: %d current queue records under %s, %d launch rows in %s"
          % (len(entries), QUEUE_ROOT.relative_to(REPO), len(rows),
             LAUNCH_LOG.relative_to(REPO)))
    print("  A. REALISED -- from the LAUNCH LOG, a destroy that ALREADY HAPPENED:")
    print("        cwds launched into more than once = %d" % len(realised))
    print("        launches into them                = %d"
          % sum(len(g["launches"]) for g in realised))
    print("        stdout records DESTROYED          = %d  (CROSS-CASE = %d)"
          % (n_dest, n_cross))
    per = {}
    for g in realised:
        for v in g["destroyed"]:
            per[v["team"]] = per.get(v["team"], 0) + 1
    print("        by the team that owned the LOST stdout:")
    for tm, n in sorted(per.items(), key=lambda kv: (-kv[1], kv[0])):
        print("            %-22s %d" % (tm, n))
    if realised:
        b = realised[0]
        print("        LARGEST: %s -- %d launches, %d destroyed"
              % (b["cwd"], len(b["launches"]), len(b["destroyed"])))

    print("  B. EXPOSURE -- from the CURRENT CORPUS, a cwd that will collide next launch:")
    print("        distinct cwds                     = %d"
          % len({e["cwd"] for e in entries}))
    print("        cwds carrying >1 current entry    = %d" % len(exposure))
    print("        entries sitting in a shared cwd   = %d"
          % sum(len(g["entries"]) for g in exposure))
    print("        of those groups, LATENT (<2 launches, destroy still ahead) = %d"
          % len(latent))
    print("        entries not yet launched in a LATENT group = %d"
          % sum(len([e for e in g["entries"] if e["state"] != "launched"])
                for g in latent))
    ent_per = {}
    for g in exposure:
        for e in g["entries"]:
            ent_per[e["team"]] = ent_per.get(e["team"], 0) + 1
    print("        by owning team:")
    for tm, n in sorted(ent_per.items(), key=lambda kv: (-kv[1], kv[0])):
        print("            %-22s %d" % (tm, n))
    if exposure:
        b = exposure[0]
        print("        LARGEST: %s -- %d entries, %d launches"
              % (b["cwd"], len(b["entries"]), len(b["launches"])))

    print("  C. EVERY REALISED CWD, with the records whose stdout is gone:")
    for g in realised:
        print("    [REALISED] %s  (launches=%d destroyed=%d cross-case=%d)"
              % (g["cwd"], len(g["launches"]), len(g["destroyed"]), g["cross"]))
        for v in g["destroyed"]:
            print("        DESTROYED %s  %s  (%s)" % (v["utc"], v["case_id"], v["team"]))
    print("  D. EVERY EXPOSED CWD in the current corpus:")
    for g in exposure:
        print("    [%s] %s  entries=%d (%s)  launches=%d"
              % (g["kind"], g["cwd"], len(g["entries"]),
                 ", ".join(sorted({"%s/%s" % (e["team"], e["state"]) for e in g["entries"]})),
                 len(g["launches"])))

    if state == "REPAIRED":
        print("VERDICT: PASS -- MECHANISM REPAIRED in the runner (%s). The %d "
              "historic destroyed record(s) above are HISTORY, not a live hazard; "
              "VR5 is retired and should be struck from the queue." % (why, n_dest))
        return 0
    if realised:
        print("VERDICT: GATE FAIL -- %d stdout record(s) already destroyed across %d "
              "cwd(s) launched into more than once. This is a FINDING ABOUT "
              "scripts/queue_runner.py, not a failure of this item; the repair is the "
              "chief's to route and is NOT made here. EXPOSURE and LATENT are "
              "REPORTED, NEVER GATED." % (n_dest, len(realised)))
        return 1
    print("VERDICT: PASS -- zero REALISED destroys on today's launch log; %d LATENT "
          "group(s) reported, never gated" % len(latent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
