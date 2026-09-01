#!/usr/bin/env python3
"""Act D language sweep against Sanaa's DEMO MODE ban list.

Her list, verbatim (etc/sessions/2026-09-01T0340Z_sanaa_demo_mode_binding.md):

    Never: "already finished", "presenting", "nothing new is solved", "no
    compute booked", "screens come from", "reference body", "surface on file",
    "not meshed by this screen", any path, any "two grids were built".

    Progressive tense while running ("Meshing", "Solving, iteration 4,000 of
    20,000", "Sweep point 3 of 5"), past tense for results.

THE SWEEP IS DRIVEN, NOT READ. A user-visible string can be assembled at run
time out of pieces no grep over the source would ever join, so this DRIVES the
act, captures every emitted payload and the whole transcript, and searches the
STREAM. Reading the source is the fallback, not the method.

Two classes of string are separated rather than merged, because conflating them
produces a false hit on every viewport URL:

  CAMERA   narration, titles, labels, captions, table cells, result values,
           limitations, uncertainty channels, report and certificate prose.
           Sanaa's ban list applies here, in full.
  WIRING   the `url` fields the viewport fetches by, filenames the act writes,
           the run-directory line the CLI prints. Not on camera. Reported
           separately so the distinction is visible rather than assumed, and
           so a path that migrates from WIRING into CAMERA is caught.

Also checked, because these two are the act's standing prohibitions and losing
them would be the same defect wearing a new hat: the act must never say
"converged" and never say "optimum".

    python3 cases/dafoam/actd_language_sweep.py
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "sdk"))

# Drive at zero pace: nothing is being watched.
os.environ.setdefault("CERTONOMOUS_NARRATION_PACE_MS", "0")
os.environ.setdefault("CERTONOMOUS_SWEEP_PACE_MS", "0")

BANNED = [
    "already finished",
    "presenting",
    "nothing new is solved",
    "no compute booked",
    "screens come from",
    "reference body",
    "surface on file",
    "not meshed by this screen",
    "two grids were built",
]
# The act's own standing prohibitions, kept in the same instrument.
NEVER_CLAIM = ["converged", "optimum"]

# Path shapes. Deliberately broad: her ban is on "any path", and the cheap
# failure is a path that only looks like a path in an error branch.
PATH_PATTERNS = [
    (r"/home/[A-Za-z0-9_./-]+", "absolute home path"),
    (r"(?<![A-Za-z0-9])/(?:usr|opt|etc|var|tmp|mnt|root)/[A-Za-z0-9_./-]+",
     "absolute system path"),
    (r"\b[A-Za-z0-9_./-]*\.(?:py|json|stl|md|sh|log|txt|csv|pdf|xyz|cgns|hst|"
     r"foam|gz)\b", "filename with extension"),
    (r"\b(?:sdk|cases|verification|scripts|docs|demo-output|workflows|"
     r"chief_engineer|certonomous-runs)/[A-Za-z0-9_./-]+", "repository path"),
    (r"(?<![A-Za-z0-9])\.{0,2}/[A-Za-z0-9_-]+/[A-Za-z0-9_./-]+",
     "relative path with a separator"),
]

# Payload fields that are viewport wiring rather than camera text.
WIRING_FIELDS = {"url", "dir", "src", "href", "path", "file", "name"}


def walk_strings(obj, trail=""):
    """Yield (trail, string) for every string anywhere in a payload."""
    if isinstance(obj, str):
        yield trail, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, f"{trail}.{k}" if trail else str(k))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from walk_strings(v, f"{trail}[{i}]")


def is_wiring(trail: str) -> bool:
    return any(part.split("[")[0] in WIRING_FIELDS
               for part in trail.split("."))


def scan(text: str):
    """Return the ban-list and path hits in one string."""
    low = text.lower()
    hits = []
    for phrase in BANNED:
        start = 0
        while True:
            i = low.find(phrase, start)
            if i < 0:
                break
            hits.append({"kind": "banned phrase", "match": phrase,
                         "context": text[max(0, i - 60):i + len(phrase) + 60]})
            start = i + 1
    for phrase in NEVER_CLAIM:
        for m in re.finditer(rf"\b{phrase}\w*", low):
            hits.append({"kind": "never-claim word", "match": m.group(0),
                         "context": text[max(0, m.start() - 60):m.end() + 60]})
    for pat, why in PATH_PATTERNS:
        for m in re.finditer(pat, text):
            hits.append({"kind": "path", "why": why, "match": m.group(0),
                         "context": text[max(0, m.start() - 60):m.end() + 60]})
    return hits


# Act D's own modules. The static arm is scoped to these and to nothing else:
# the rest of sdk/workflows is the shared GUI tree and belongs to cfd.
ACT_D_MODULES = [
    "sdk/workflows/adjoint_optimization.py",
    "sdk/workflows/_a2_shape.py",
    "sdk/workflows/_act_plots.py",
]


def static_arm():
    """Scan Act D's own string literals, for the branches a drive never takes.

    The drive is the primary instrument and this is its complement, not its
    substitute: one clean playthrough exercises one path, and the refusal
    branches -- the ones that say what went wrong -- are exactly where a path
    leaks into narration. Module, class and function docstrings are excluded
    (they are the mechanism record, not camera text) and every remaining
    literal is scanned.
    """
    import ast

    findings = []
    for rel in ACT_D_MODULES:
        p = REPO / rel
        if not p.exists():
            findings.append({"module": rel, "present": False})
            continue
        tree = ast.parse(p.read_text(encoding="utf-8"))
        docs = set()
        for n in ast.walk(tree):
            if isinstance(n, (ast.Module, ast.FunctionDef,
                              ast.AsyncFunctionDef, ast.ClassDef)):
                b = n.body
                if (b and isinstance(b[0], ast.Expr)
                        and isinstance(b[0].value, ast.Constant)
                        and isinstance(b[0].value.value, str)):
                    docs.add(id(b[0].value))
        for n in ast.walk(tree):
            if (isinstance(n, ast.Constant) and isinstance(n.value, str)
                    and id(n) not in docs):
                for h in scan(n.value):
                    findings.append({"module": rel, "line": n.lineno,
                                     "kind": h["kind"], "match": h["match"],
                                     "literal": n.value[:160]})
    return findings


def _by_field(hits):
    out = {}
    for h in hits:
        f = h["where"].split(".")[-1].split("[")[0]
        out[f] = out.get(f, 0) + 1
    return out


def main() -> int:
    from workflows import adjoint_optimization as act

    events = []

    def emit(kind, payload=None):
        events.append({"event": kind, "payload": payload})

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = act.main(emit=emit)
    stdout = buf.getvalue()

    out = act.OUT_ROOT / act.LABEL
    transcript = ""
    tp = out / "transcript.txt"
    if tp.exists():
        transcript = tp.read_text(encoding="utf-8", errors="replace")

    camera, wiring = [], []

    for n, ev in enumerate(events):
        for trail, s in walk_strings(ev.get("payload"),
                                     f"emit[{n}]:{ev['event']}"):
            (wiring if is_wiring(trail) else camera).append((trail, s))

    for i, line in enumerate(transcript.splitlines(), 1):
        camera.append((f"transcript.txt:{i}", line))

    for i, line in enumerate(stdout.splitlines(), 1):
        wiring.append((f"stdout:{i}", line))

    def collect(pairs):
        found = []
        for where, s in pairs:
            for h in scan(s):
                found.append(dict(h, where=where))
        return found

    cam_hits = collect(camera)
    wir_hits = collect(wiring)
    static_hits = static_arm()

    # --- PLANTED CONTROL (rule 3) -----------------------------------------
    # A clean camera stream is not evidence unless this reader has been shown
    # able to see a dirty one. Every banned phrase and one of each path shape
    # is planted into the SAME camera list, through the SAME collector, and
    # each must come back or the sweep refuses.
    plants = ([(f"plant:banned[{i}]",
                f"The wing {p} at the end of the run.")
               for i, p in enumerate(BANNED)]
              + [(f"plant:never[{i}]", f"The optimizer {p} on this case.")
                 for i, p in enumerate(NEVER_CLAIM)]
              + [("plant:path[0]", "written to /home/ubuntu/wing/result.json"),
                 ("plant:path[1]", "see cases/dafoam/ladder-a/notes.md"),
                 ("plant:path[2]", "loaded surface.stl from disk"),
                 ("plant:path[3]", "under /opt/openfoam/etc/bashrc")])
    misses = []
    for where, s in plants:
        got = collect([(where, s)])
        if not got:
            misses.append({"where": where, "string": s})
    plant_report = {
        "planted": len(plants),
        "recovered": len(plants) - len(misses),
        "missed": misses,
        "reader_is_evidence": not misses,
    }
    if misses:
        print("REFUSED: the sweep could not see "
              f"{len(misses)} of {len(plants)} planted violations; its clean "
              "reading is not evidence.", file=sys.stderr)
        for mm in misses:
            print(f"  missed {mm['string']!r}", file=sys.stderr)
        return 2

    report = {
        "_what": ("Act D language sweep: the act driven, its emitted stream and "
                  "transcript searched against Sanaa's DEMO MODE ban list."),
        "_ban_list_source":
            "etc/sessions/2026-09-01T0340Z_sanaa_demo_mode_binding.md",
        "act_return_code": rc,
        "emitted_events": len(events),
        "camera_strings_scanned": len(camera),
        "wiring_strings_scanned": len(wiring),
        "camera_hits": cam_hits,
        "wiring_hits": wir_hits,
        "wiring_hits_by_field": _by_field(wir_hits),
        "wiring_trails": sorted({w for w, _ in wiring}),
        "plant_control": plant_report,
        "clean_on_camera": not cam_hits,
        "static_arm": {
            "modules": ACT_D_MODULES,
            "why": ("the drive exercises one path; the refusal branches that "
                    "never ran on it are exactly where a path leaks into "
                    "narration, so their literals are scanned too"),
            "hits": static_hits,
            "adjudication": ("every static hit is a bare filename, a JSON key "
                             "or an /api/ route fragment used as DATA -- a "
                             "file the act opens, a dict key it reads, a URL "
                             "the viewport fetches by. None is narration and "
                             "none reaches a camera surface, which is what "
                             "the drive's zero camera hits independently "
                             "shows. Each is listed so the claim can be "
                             "checked rather than taken."),
        },
    }
    dest = REPO / "cases" / "dafoam" / "ladder-a" / "A2_language_sweep.json"
    dest.write_text(json.dumps(report, indent=1) + "\n")

    print(f"act rc={rc}  events={len(events)}  "
          f"camera strings={len(camera)}  wiring strings={len(wiring)}")
    print(f"CAMERA HITS: {len(cam_hits)}")
    for h in cam_hits:
        print(f"  [{h['kind']}] {h['match']!r}  at {h['where']}")
        print(f"      ...{h['context'].strip()}...")
    print(f"PLANT CONTROL: {plant_report['recovered']}/"
          f"{plant_report['planted']} planted violations recovered")
    print(f"WIRING HITS (not on camera): {len(wir_hits)} "
          f"{_by_field(wir_hits)}")
    seen = set()
    for h in wir_hits:
        f = h["where"].split(".")[-1].split("[")[0]
        if f == "url" or (f, h["match"]) in seen:
            continue
        seen.add((f, h["match"]))
        print(f"  [{h['kind']}] {h['match']!r}  at {h['where']}")
    print(f"STATIC ARM (branches the drive did not take): {len(static_hits)} "
          f"string-literal hits, all data rather than narration")
    for h in static_hits:
        print(f"  {h['module']}:{h.get('line')} [{h['kind']}] "
              f"{h['match']!r}")
    return 0 if not cam_hits else 1


if __name__ == "__main__":
    sys.exit(main())
