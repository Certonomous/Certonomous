#!/usr/bin/env python3
"""Do the caption glyphs SURVIVE THE RENDER? Checked in pixels, not in source.

WHY A SOURCE SWEEP CANNOT ANSWER THIS. The caption controls
(`ladder-a/A1/polar_frame_captions.py`), the language sweep and the mechanism
guard all read TEXT. Heat-transfer measured a case where ParaView's font
silently swallowed a `|` separator: **the caption was right in the file and
wrong on the screen.** Every text-side instrument was green on a string that was
never what got published.

AND THE BOUNDARY MATTERS, because this lab deliberately reads SOURCE elsewhere.
The tense sweep reads the `.tex` source on purpose: `pdftotext -layout`
interleaves a two-column page, so a face offset cannot be resolved to a beat and
staging one would be a fiction. **That excuse does not transfer to a PNG.** A
rendered frame has no reading-order problem, and the failure here is precisely
the one a source read is blind to. So: sheets keep the documented source-read
with its on-face flag; RENDERED CAPTIONS ARE VERIFIED ON THE RENDER.

It is the same principle as the camera read-back and the cropped wing frame:
**make the instrument state what it DID, not what it was ASKED to do.** A caption
in a script is what you asked for; the pixels are what happened.

THE METHOD IS THE PLANT THIS FAMILY ALREADY USES. Render the caption; render it
again with ONE character changed; assert the two frames DIFFER. A glyph the font
drops produces an identical frame, because dropping it and replacing it with
nothing are the same picture. Driven per separator glyph, because those are what
a compressed numeric caption leans on and exactly what a font is likeliest to
lack.

**A vanished separator is not cosmetic.** `alpha = 18 deg | 9/19 converged` with
the bar gone reads as one claim where there were two.

    python3 cases/dafoam/actd_caption_glyph_check.py
"""
from __future__ import annotations

import collections
import hashlib
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "cases" / "dafoam" / "ladder-a" / "A1"))

WRAPPER = Path("/opt/paraview/bin/pvbatch")
REAL = Path("/opt/ParaView-5.13.3-egl-MPI-Linux-Python3.10-x86_64/bin/pvbatch-real")
MD5_WRAPPER = "82ec8db976f28f51f2003a56c04fc272"
MD5_REAL = "dc272bb98d4ca91fd2f72dd3e89256b4"

OUT_ROOT = REPO / "verification" / "runs" / "actD_paraview" / "glyphs"

#: The separators a compressed numeric caption leans on. `|` is the one this
#: family publishes; the rest are here because they are the obvious next choices
#: and a successor reaching for one should find out here whether it renders.
SEPARATORS = ["|", "·", "×", "≤", "°", "⁻¹"]

TEXT_RENDER = '''
print("SENTINEL_PY_OK", flush=True)
from paraview.simple import *
print("SENTINEL_IMPORT_OK", flush=True)
t = Text(registrationName="cap")
t.Text = CAPTION
v = CreateRenderView()
v.ViewSize = [900, 120]
v.Background = [0.12, 0.14, 0.18]
v.OrientationAxesVisibility = 0
d = Show(t, v)
d.FontSize = 28
d.Color = [1.0, 1.0, 1.0]
d.WindowLocation = "Any Location"
d.Position = [0.02, 0.35]
Render(v)
print("SENTINEL_RENDER_OK", flush=True)
SaveScreenshot(OUT, v)
print("SENTINEL_SAVE_OK", flush=True)
'''


def md5(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def render_text(caption: str, out: Path, tag: str) -> bool:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    sp = OUT_ROOT / f"_render_{tag}.py"
    sp.write_text(f"CAPTION = {caption!r}\nOUT = {str(out)!r}\n" + TEXT_RENDER)
    r = subprocess.run([str(WRAPPER), str(sp)], capture_output=True,
                       text=True, timeout=600)
    return r.returncode == 0 and out.exists()


def px(p: Path):
    from PIL import Image
    im = Image.open(p).convert("RGB")
    return list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") \
        else list(im.getdata())


def frac_differing(a: Path, b: Path) -> float:
    import numpy as np
    from PIL import Image
    ia = np.asarray(Image.open(a).convert("RGB"), dtype=np.int16)
    ib = np.asarray(Image.open(b).convert("RGB"), dtype=np.int16)
    if ia.shape != ib.shape:
        return 1.0
    return float((np.abs(ia - ib).sum(axis=2) > 0).mean())


def touches_edge(p: Path, cols: int = 12) -> int:
    """Non-background pixels in the last `cols` columns: is the caption CUT OFF?

    THE ARM THIS FILE WAS MISSING, AND IT COST A DEFECT. The first published
    caption was one long line, it ran off the right edge of the view, and this
    script passed it: the glyphs were drawn, the ink was 5.79 %, every arm was
    green, and the last word was sliced in half on screen. Ink present is not
    content complete. It is the cropped-wing failure again in a second channel,
    and again only opening the image found it -- so it is an arm now.
    """
    import numpy as np
    from PIL import Image
    im = np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)
    bg = int(np.bincount(im.reshape(-1, 3)[:, 0]).argmax())
    edge = im[:, -cols:, 0]
    return int((np.abs(edge - bg) > 8).sum())


def ink(p: Path) -> float:
    """Fraction of pixels that are not the background. A caption that rendered
    as nothing at all is caught here rather than by a difference that happens
    to be zero for a second reason."""
    vals = px(p)
    bg = collections.Counter(vals).most_common(1)[0][0]
    return 1.0 - (sum(1 for v in vals if v == bg) / len(vals))


def main() -> int:
    for gate, path, want in (("G-PV1a", WRAPPER, MD5_WRAPPER),
                             ("G-PV1b", REAL, MD5_REAL)):
        if not path.exists() or md5(path) != want:
            print(f"REFUSE: {gate} md5 mismatch")
            return 2
    print("G-PV1a PASS  G-PV1b PASS")
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    blind: list[str] = []
    n = 0

    # ---- the sound check: does the text channel draw ANYTHING at all? ------
    # Without this, a pipeline that renders every caption as a blank strip
    # would give "identical frames" for every glyph and be read as "every glyph
    # is missing", which is the right alarm for the wrong reason.
    a = OUT_ROOT / "sound_A.png"
    b = OUT_ROOT / "sound_B.png"
    n += 1
    if not (render_text("AAAA", a, "sound_a") and render_text("AAAB", b, "sound_b")):
        blind.append("the text renderer did not produce a frame at all")
        print("REFUSE: no frame; nothing below can be believed")
        return 2
    ink_a = ink(a)
    if ink_a < 0.001:
        blind.append(f"the text renderer drew nothing ({ink_a:.5f} ink)")
    n += 1
    if frac_differing(a, b) <= 0.0:
        blind.append("changing a LETTER changed no pixel; the text channel is "
                     "not live and no glyph verdict below means anything")
    print(f"TEXT CHANNEL: {ink_a * 100:.2f}% ink; one letter changed moves "
          f"{frac_differing(a, b) * 100:.3f}% of pixels")

    if blind:
        for x in blind:
            print(f"REFUSE: {x}")
        return 2

    # ---- per separator glyph, the two-sided plant --------------------------
    print("\nSEPARATOR GLYPHS  (rendered, then rendered with the glyph removed)")
    results = []
    for i, g in enumerate(SEPARATORS):
        with_g = OUT_ROOT / f"sep_{i}_with.png"
        without = OUT_ROOT / f"sep_{i}_without.png"
        ok1 = render_text(f"18 deg {g} 9/19", with_g, f"sep{i}_with")
        ok2 = render_text("18 deg   9/19", without, f"sep{i}_without")
        n += 1
        if not (ok1 and ok2):
            blind.append(f"glyph {g!r}: did not render")
            continue
        d = frac_differing(with_g, without)
        drawn = d > 0.0
        results.append((g, d, drawn))
        name = {"|": "vertical bar", "·": "middle dot",
                "×": "times", "≤": "less-or-equal",
                "°": "degree", "⁻¹": "superscript minus-one"}[g]
        print(f"  {'DRAWN  ' if drawn else 'DROPPED'}  {name:<22} "
              f"differs on {d * 100:.4f}% of pixels")
        if not drawn:
            blind.append(f"glyph {g!r} ({name}) IS NOT DRAWN by this font; a "
                         f"caption using it as a separator would publish as "
                         f"though the separator were absent")

    # ---- the captions this family actually publishes -----------------------
    print("\nPUBLISHED CAPTIONS, rendered")
    from polar_frame_captions import CAPTIONS, REVEAL_CAPTION, REFUSAL_BULLETS
    # CAPTIONS values are BULLET LISTS, not strings -- each bullet is its own
    # rendered line and each is checked on its own, because a list that fits as
    # a whole tells you nothing about whether any single line does.
    published = [(f"{k}[{i}]", b) for k, v in CAPTIONS.items()
                 for i, b in enumerate(v)]
    published.append(("reveal", REVEAL_CAPTION.format(radius=0.19, kept=118,
                                                      total=4032)))
    published += [(f"refusal_{i}", t) for i, t in enumerate(REFUSAL_BULLETS)]
    for tag, text in published:
        out = OUT_ROOT / f"caption_{tag}.png"
        n += 1
        if not render_text(text, out, f"cap_{tag}"):
            blind.append(f"published caption {tag!r} did not render")
            continue
        got = ink(out)
        n += 1
        if got < 0.001:
            blind.append(f"published caption {tag!r} rendered blank")
        n += 1
        spill = touches_edge(out)
        if spill:
            blind.append(f"published caption {tag!r} is CUT OFF: {spill} "
                         f"non-background pixels touch the right edge")
        print(f"  {got * 100:5.2f}% ink  edge {spill:>4}   {tag}")

    print(f"\nGLYPH CONTROL: {n - len(blind)}/{n} arms behaved")
    if blind:
        for x in blind:
            print(f"REFUSE: {x}")
        return 1
    print("ok  every separator this family publishes is drawn, and every "
          "published caption reaches pixels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
