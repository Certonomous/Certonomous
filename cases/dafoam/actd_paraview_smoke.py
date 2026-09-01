#!/usr/bin/env python3
"""STAGE 0 of the Act D ParaView render pass: can the registered engine render?

Registered in `cases/dafoam/ACTD_PARAVIEW_RENDER_PASS_PREREGISTRATION.md`
(v1.1, amendment A1.3) as ONE FRAME, before any script iteration, graded on
G-PV1a, G-PV1b and G-PV7a only.

WHY THIS RUNS FIRST. `CLAUDE.md` rule 12: no GPU is attached to this box, and
EGL normally wants a GPU or a software EGL. The registered engine may be unable
to run here at all. The honest majority of this item's 45 core-min is script
iteration, so finding an unusable engine afterwards buys a BLOCKED at full price
and finding it in one frame buys the same BLOCKED for nearly nothing.

WHAT IT DOES NOT DO. It does not fall back. If EGL cannot initialise, the verdict
is BLOCKED and the 5.11.2 + xvfb path is registered properly as its own
amendment, with the blank-image hazard gated by G-PV7 rather than argued about.
A fallback here would change the toolchain without changing the record.

    python3 cases/dafoam/actd_paraview_smoke.py
"""
from __future__ import annotations

import collections
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN_ROOT = REPO / "verification" / "runs" / "actD_paraview" / "stage0"

# ---- the registered engine, BY ABSOLUTE PATH (prereg §2, amendment A1.1) ----
# Both halves of the pair. The wrapper is what we invoke; the real binary is
# what it execs. Gating only one leaves the other free to be swapped.
WRAPPER = Path("/opt/paraview/bin/pvbatch")
REAL = Path("/opt/ParaView-5.13.3-egl-MPI-Linux-Python3.10-x86_64/bin/pvbatch-real")
MD5_WRAPPER = "82ec8db976f28f51f2003a56c04fc272"   # G-PV1a
MD5_REAL = "dc272bb98d4ca91fd2f72dd3e89256b4"      # G-PV1b

# ---- G-PV7a thresholds, registered scale-free (amendment A1.2) -------------
MODAL_SHARE_MAX = 0.99   # a blank frame is ~100% one colour, whatever the palette
DISTINCT_COLOURS_MIN = 64

# THE SENTINELS ARE THE POINT, NOT DECORATION. The first run of this test
# reported BLOCKED -- an ENGINE verdict -- on what was actually a typo in this
# very script (`ColorBy(d, None)`, invalid in 5.13.3). The engine had loaded
# fine. A red with an innocent explanation is the easiest failure to act on
# wrongly, and acting on that one would have sent us to register a whole
# fallback toolchain we do not need. So the script now says HOW FAR IT GOT and
# the driver triages on that rather than on a bare non-zero rc.
RENDER_SCRIPT = '''# Stage 0 smoke frame. Deliberately trivial: this tests the
# ENGINE, not the case. A case-coupled render is G-PV7b's job, later.
print("SENTINEL_PY_OK", flush=True)
from paraview.simple import *
print("SENTINEL_IMPORT_OK", flush=True)
s = Sphere(ThetaResolution=64, PhiResolution=64)
d = Show(s)
d.Representation = "Surface With Edges"
v = GetActiveView()
v.ViewSize = [480, 360]
v.Background = [0.12, 0.14, 0.18]
ResetCamera()
Render()
print("SENTINEL_RENDER_OK", flush=True)
SaveScreenshot(OUT, v)
print("SENTINEL_SAVE_OK", flush=True)
'''


def md5(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def frame_content(png: Path) -> dict:
    """G-PV7a: is this a picture, or a uniform rectangle?

    Scale-free by design. A pixel-variance floor needs a scale nobody can
    register honestly before seeing the first frame, and a floor guessed in
    advance is a number chosen to be passed.
    """
    from PIL import Image
    im = Image.open(png).convert("RGB")
    px = list(im.getdata())
    counts = collections.Counter(px)
    modal_colour, modal_n = counts.most_common(1)[0]
    return {
        "pixels": len(px),
        "distinct_colours": len(counts),
        "modal_colour": list(modal_colour),
        "modal_share": modal_n / len(px),
        "size": list(im.size),
    }


# --------------------------------------------------------------- triage ----
EGL_MARKERS = ("egl", "opengl", "glx", "display", "render window",
               "vtkxopenglrenderwindow", "failed to create")


def triage(rc: int, stdout: str, stderr: str, frame_exists: bool) -> tuple[str, str]:
    """(verdict, why) for a render attempt. THREE STATES, NOT TWO.

    A non-zero rc means "this run failed", NOT "the engine cannot render", and
    only one of those is BLOCKED. Getting this wrong is expensive in both
    directions: a false BLOCKED buys a whole registration cycle for a fallback
    toolchain we do not need, and a false NOT A RESULT hides a real toolchain
    problem behind "my script was buggy".

    THIS FUNCTION EXISTS SO IT CAN BE PLANTED. The first version of this test
    reported BLOCKED on a typo in its own render script (`ColorBy(d, None)`,
    invalid in 5.13.3); the engine had loaded perfectly. That is a red with an
    innocent explanation, and acting on it would have sent us to register a
    fallback we do not need.
    """
    if rc == 0 and frame_exists:
        return "PASS", "the engine rendered a frame"
    got = set(stdout.split())
    py_up = "SENTINEL_PY_OK" in got
    engine_up = "SENTINEL_IMPORT_OK" in got
    egl = any(k in (stderr or "").lower() for k in EGL_MARKERS)
    if not py_up:
        return ("NOT A RESULT",
                "the smoke script did not execute its first line, so nothing "
                "here is a statement about the engine")
    if engine_up and not egl:
        return ("NOT A RESULT",
                "the smoke SCRIPT failed after the engine loaded, with no "
                "EGL/OpenGL signature in stderr, so this run says nothing "
                "about the engine; it is a defect in this test")
    return ("BLOCKED",
            "the registered EGL engine could not initialise or could not make "
            "a render context on this box; per prereg A1.3 nothing falls back "
            "and the 5.11.2 + xvfb path is registered separately")


def is_blank(content: dict) -> bool:
    """G-PV7a. Scale-free: a blank frame is ~100% one colour, any palette."""
    return (content["modal_share"] >= MODAL_SHARE_MAX
            or content["distinct_colours"] < DISTINCT_COLOURS_MIN)


#: The render script's own body, mutated, for the triage plants. Each must
#: produce ONE named verdict and no other.
SELFTEST_CASES = [
    ("syntax error before anything runs",
     "def (\n", "NOT A RESULT"),
    ("runtime error after the engine loaded, no graphics signature",
     'print("SENTINEL_PY_OK", flush=True)\n'
     "from paraview.simple import *\n"
     'print("SENTINEL_IMPORT_OK", flush=True)\n'
     "raise ValueError('a defect in this test, not the engine')\n",
     "NOT A RESULT"),
    ("engine never imports and stderr carries a graphics signature",
     'print("SENTINEL_PY_OK", flush=True)\n'
     "import sys; sys.stderr.write('libEGL: failed to create display\\n')\n"
     "sys.exit(1)\n",
     "BLOCKED"),
]


def selftest() -> int:
    """Plant every arm, in every direction. Both gates, not just one.

    A gate never shown able to fire is not a gate (CLAUDE.md rule 3), and that
    applies to a TRIAGE as much as to a comparator: a triage that answers
    NOT A RESULT to everything is exactly as useless as one that answers
    BLOCKED to everything, and only a two-sided plant separates them.
    """
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    blind = []
    n = 0

    # ---- the triage, driven through the REAL binary where it can be --------
    for name, body, want in SELFTEST_CASES:
        n += 1
        sp = RUN_ROOT / "selftest_render.py"
        sp.write_text(body)
        r = subprocess.run([str(WRAPPER), str(sp)], capture_output=True,
                           text=True, timeout=600)
        got, _why = triage(r.returncode, r.stdout, r.stderr, False)
        print(f"  [{got:>12}] want {want:>12}  {name}")
        if got != want:
            blind.append(f"triage: {name}: got {got}, want {want}")

    # ---- G-PV7a, driven through the REAL pipeline, BOTH directions ---------
    # THE BLANK ARM IS A GENUINE RENDER, not a synthetic image. A blank-frame
    # gate tested on a PNG this script wrote itself would prove nothing about
    # what the ENGINE emits when it draws nothing.
    for name, body, want_blank in (
            # A view with NOTHING SHOWN IN IT. This is the exact shape of the
            # failure G-PV7 exists for: the engine initialises, the process
            # exits zero, a PNG appears, and it is a uniform rectangle. The
            # view is created explicitly because an empty scene has no active
            # one -- and the first version of this plant failed to render at
            # all for that reason, which the control caught rather than
            # scoring as a pass.
            ("an empty scene must read as blank",
             'print("SENTINEL_PY_OK", flush=True)\n'
             "from paraview.simple import *\n"
             "v = CreateRenderView()\n"
             "v.ViewSize = [480, 360]\n"
             "v.Background = [0.12, 0.14, 0.18]\n"
             "Render(v); SaveScreenshot(OUT, v)\n", True),
            ("a drawn sphere must NOT read as blank",
             RENDER_SCRIPT, False)):
        n += 1
        out = RUN_ROOT / "selftest_frame.png"
        if out.exists():
            out.unlink()
        sp = RUN_ROOT / "selftest_render.py"
        sp.write_text(f"OUT = {str(out)!r}\n" + body)
        r = subprocess.run([str(WRAPPER), str(sp)], capture_output=True,
                           text=True, timeout=600)
        if r.returncode != 0 or not out.exists():
            blind.append(f"G-PV7a: {name}: the plant did not render at all")
            print(f"  [   NO RENDER] {name}")
            continue
        c = frame_content(out)
        got_blank = is_blank(c)
        print(f"  [blank={str(got_blank):>5}] want {str(want_blank):>5}  {name}"
              f"   (modal {c['modal_share']:.4f}, {c['distinct_colours']} colours)")
        if got_blank != want_blank:
            blind.append(f"G-PV7a: {name}: got blank={got_blank}")

    print(f"\nPLANT CONTROL: {n - len(blind)}/{n} arms behaved")
    if blind:
        for b in blind:
            print(f"  REFUSE: {b}")
        return 2
    print("ok  the triage and the blank-frame gate both fire, in both directions")
    return 0


def main() -> int:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    record: dict = {"_what": "Stage 0 EGL smoke test, one frame",
                    "_preregistration": "cases/dafoam/"
                                        "ACTD_PARAVIEW_RENDER_PASS_PREREGISTRATION.md v1.1",
                    "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    fail: list[str] = []

    # ---------------------------------------------- G-PV1a / G-PV1b --------
    for gate, path, want in (("G-PV1a", WRAPPER, MD5_WRAPPER),
                             ("G-PV1b", REAL, MD5_REAL)):
        if not path.exists():
            record[gate] = {"path": str(path), "verdict": "NOT A RESULT",
                            "why": "the registered binary is not on this box"}
            fail.append(f"{gate}: {path} absent")
            continue
        got = md5(path)
        ok = got == want
        record[gate] = {"path": str(path), "md5_measured": got,
                        "md5_registered": want,
                        "verdict": "PASS" if ok else "NOT A RESULT"}
        if not ok:
            fail.append(f"{gate}: md5 {got} != registered {want}")

    if fail:
        record["VERDICT"] = "NOT A RESULT"
        record["_why"] = ("the engine could not be identified, so nothing it "
                          "produced could be attributed; no render attempted")
        (RUN_ROOT / "stage0.json").write_text(json.dumps(record, indent=1))
        for f in fail:
            print(f"REFUSE: {f}")
        return 2
    print(f"G-PV1a PASS  wrapper md5 {MD5_WRAPPER}")
    print(f"G-PV1b PASS  real    md5 {MD5_REAL}")

    # ------------------------------------------------- the one frame -------
    out = RUN_ROOT / "smoke.png"
    if out.exists():
        out.unlink()
    script = RUN_ROOT / "smoke_render.py"
    script.write_text(f"OUT = {str(out)!r}\n" + RENDER_SCRIPT)

    t0 = time.time()
    r = subprocess.run([str(WRAPPER), str(script)],
                       capture_output=True, text=True, timeout=600)
    wall = time.time() - t0
    record["render"] = {"rc": r.returncode, "wall_s": round(wall, 3),
                        "ranks": 1,
                        "core_min": round(wall / 60.0, 4),
                        "stdout_tail": r.stdout.strip().splitlines()[-3:],
                        "stderr_tail": r.stderr.strip().splitlines()[-6:]}

    got = set(r.stdout.split())
    record["render"]["sentinels"] = sorted(
        x for x in got if x.startswith("SENTINEL_"))
    if r.returncode != 0 or not out.exists():
        verdict, why = triage(r.returncode, r.stdout, r.stderr, out.exists())
        record["VERDICT"], record["_why"] = verdict, why
        (RUN_ROOT / "stage0.json").write_text(json.dumps(record, indent=1))
        print(f"\n{verdict}: {why}")
        print(f"  sentinels reached: {record['render']['sentinels'] or 'none'}")
        for line in record["render"]["stderr_tail"]:
            print(f"  {line}")
        if verdict == "BLOCKED":
            print("\nNo fallback is taken. Per A1.3 this returns to the "
                  "supervisor and the 5.11.2 + xvfb path is registered as its "
                  "own amendment.")
            return 3
        return 1

    # ------------------------------------------------------- G-PV7a --------
    content = frame_content(out)
    record["G-PV7a"] = dict(content)
    blank = is_blank(content)
    record["G-PV7a"]["modal_share_max"] = MODAL_SHARE_MAX
    record["G-PV7a"]["distinct_colours_min"] = DISTINCT_COLOURS_MIN
    record["G-PV7a"]["verdict"] = "NOT A RESULT" if blank else "PASS"

    print(f"\nFRAME: {content['size'][0]}x{content['size'][1]}, "
          f"{content['distinct_colours']} distinct colours, "
          f"modal colour {content['modal_colour']} at "
          f"{content['modal_share']:.4f} of pixels")
    print(f"G-PV7a threshold: modal share < {MODAL_SHARE_MAX}, "
          f"distinct >= {DISTINCT_COLOURS_MIN}")

    if blank:
        record["VERDICT"] = "NOT A RESULT"
        record["_why"] = ("the engine ran and exited zero and produced a "
                          "UNIFORM frame; an md5-clean blank rectangle is "
                          "exactly the failure G-PV7 exists to catch")
        (RUN_ROOT / "stage0.json").write_text(json.dumps(record, indent=1))
        print("\nNOT A RESULT: the frame is uniform. The engine ran; it drew "
              "nothing. This is the failure the blank-frame gate exists for.")
        return 1

    record["VERDICT"] = "PASS"
    record["_scope"] = ("Stage 0 proves the ENGINE renders a non-blank frame on "
                        "this box. It proves NOTHING about case coupling, which "
                        "is G-PV7b/G-PV7c, nor about any physics.")
    (RUN_ROOT / "stage0.json").write_text(json.dumps(record, indent=1))
    print(f"\nPASS  Stage 0: the registered EGL engine renders here. "
          f"{record['render']['core_min']} core-min.")
    print(f"      record: {RUN_ROOT / 'stage0.json'}")
    print("      SCOPE: the engine renders. Case coupling is G-PV7b/c, not this.")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
