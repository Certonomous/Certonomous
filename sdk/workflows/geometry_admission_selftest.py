"""Drive :mod:`geometry_admission` RED and GREEN in ONE invocation.

Standing rule 3, applied to a gate rather than to a comparator: a checker that
has never been shown refusing anything is not a checker, and a checker that
refuses everything is not one either. Every run of this file does both, on the
real files the act actually receives and on surfaces built to be impossible.

Run:  python3 sdk/workflows/geometry_admission_selftest.py
Exit: 0 all arms as registered, 2 any arm wrong.
"""

from __future__ import annotations

import math
import struct
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from workflows.geometry_admission import (  # noqa: E402
    admit, agrees_with, sentences,
)

REPO = Path(__file__).resolve().parents[2]
REAL_UPLOAD = REPO / "sdk" / "geometry" / "naca0012_wing.stl"
REFERENCE_WING = REPO / "sdk" / "geometry" / "mach_tutorial_wing.stl"

# The axis roles sdk/workflows/_a2_shape.dimensions() assumes for every
# surface: x chordwise, y thickness, z span -> (chord, span, thickness).
ACT_CONVENTION = (0, 2, 1)


# --------------------------------------------------------------------------
# Surfaces built on purpose. Each names the real-world mistake it stands for.
# --------------------------------------------------------------------------

def _naca_half_thickness(x: float, t: float) -> float:
    return 5 * t * (0.2969 * math.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2
                    + 0.2843 * x ** 3 - 0.1015 * x ** 4)


def naca_wing(chord: float, span: float, t_over_c: float,
              axes: tuple[int, int, int] = (0, 1, 2), n: int = 40) -> list:
    """A closed NACA00xx wing. `axes` maps (chord, span, thickness) onto XYZ."""
    xs = [(1 - math.cos(math.pi * i / n)) / 2 for i in range(n + 1)]
    ribs = []
    for s in (-span / 2, span / 2):
        upper = [(x * chord, s, _naca_half_thickness(x, t_over_c) * chord)
                 for x in xs]
        lower = [(x * chord, s, -_naca_half_thickness(x, t_over_c) * chord)
                 for x in reversed(xs)]
        ribs.append(upper + lower[1:-1])
    tris = []
    m = len(ribs[0])
    for i in range(m):
        j = (i + 1) % m
        a, b, c, d = ribs[0][i], ribs[0][j], ribs[1][j], ribs[1][i]
        tris.append((a, b, c))
        tris.append((a, c, d))
    for rib in ribs:                       # cap each end so the body closes
        cx = (sum(p[0] for p in rib) / len(rib), rib[0][1],
              sum(p[2] for p in rib) / len(rib))
        for i in range(len(rib)):
            tris.append((rib[i], rib[(i + 1) % len(rib)], cx))
    # Explicit permutation: the value for world axis `axes[role]` is p[role],
    # where role 0 is chord, 1 is span, 2 is thickness.
    out = []
    for tri in tris:
        perm = []
        for p in tri:
            q = [0.0, 0.0, 0.0]
            for role in range(3):
                q[axes[role]] = p[role]
            perm.append(tuple(q))
        out.append(tuple(perm))
    return out


def scaled(tris: list, k: float) -> list:
    return [tuple(tuple(c * k for c in p) for p in t) for t in tris]


def blob(size: float) -> list:
    """A cube: the same extent in all three directions. Cannot be a wing."""
    s = size
    v = [(x * s, y * s, z * s) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
    q = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
         (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    tris = []
    for a, b, c, d in q:
        tris.append((v[a], v[b], v[c]))
        tris.append((v[a], v[c], v[d]))
    return tris


def flat_sheet(chord: float, span: float) -> list:
    """A mid-surface: a wing planform with literally zero thickness."""
    v = [(0, 0, 0), (chord, 0, 0), (chord, span, 0), (0, span, 0)]
    return [(v[0], v[1], v[2]), (v[0], v[2], v[3])]


def write_stl(tris: list, path: Path) -> Path:
    with open(path, "wb") as fh:
        fh.write(b"selftest surface".ljust(80, b"\0"))
        fh.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            fh.write(struct.pack("<12fH", 0, 0, 0, *a, *b, *c, 0))
    return path


# --------------------------------------------------------------------------

FAILURES: list[str] = []


def check(label: str, got, want, detail: str = "") -> None:
    ok = got == want
    if not ok:
        FAILURES.append(f"{label}: got {got!r}, registered {want!r}")
    mark = "as registered" if ok else "WRONG"
    print(f"  [{mark:>13s}] {label}"
          + (f"\n{' ' * 18}{detail}" if detail else ""))


def arm_green(label: str, path, note: str) -> None:
    d = admit(path)
    check(label, d["code"], "ADMITTED",
          note + (f" -> {d['axes']['convention']}" if d["admitted"]
                  else f" -> REFUSED: {d['reason']}"))


def arm_red(label: str, path, code: str) -> None:
    d = admit(path)
    check(label, d["code"], code, f"says: {d['reason']}")
    if d["code"] == code:
        # A refusal must also be a refusal to proceed, not a note beside a run.
        check(label + " -> stops", d["admitted"], False)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="geom_admit_"))
    print(f"Working surfaces in {tmp}\n")

    print("GREEN ARMS -- these must be admitted, or the checker is useless")
    print("-" * 74)
    arm_green("the file the customer actually uploaded", REAL_UPLOAD,
              "naca0012_wing.stl, the file reported as impossible")
    arm_green("the act's own reference wing", REFERENCE_WING,
              "mach_tutorial_wing.stl")
    arm_green("high-aspect glider wing (chord 0.5 m, span 20 m)",
              write_stl(naca_wing(0.5, 20.0, 0.12), tmp / "glider.stl"),
              "unusual proportions, entirely legal")
    arm_green("thick 24% root section (chord 2 m, span 6 m)",
              write_stl(naca_wing(2.0, 6.0, 0.24), tmp / "thick.stl"),
              "thicker than most wings, still a wing")
    arm_green("low-aspect delta-ish wing (chord 3 m, span 2 m)",
              write_stl(naca_wing(3.0, 2.0, 0.10), tmp / "delta.stl"),
              "span SHORTER than chord -- must not be refused for it")

    print("\nRED ARMS -- these must be refused, each for its own reason")
    print("-" * 74)
    arm_red("millimetre export read as metres (x1000)",
            write_stl(scaled(naca_wing(1.0, 3.0, 0.12), 1000.0),
                      tmp / "mm.stl"), "TOO_LARGE")
    arm_red("scale error the other way (/1000)",
            write_stl(scaled(naca_wing(1.0, 3.0, 0.12), 0.001),
                      tmp / "tiny.stl"), "TOO_SMALL")
    arm_red("a solid block, not a lifting surface",
            write_stl(blob(1.0), tmp / "blob.stl"), "NOT_A_LIFTING_SURFACE")
    arm_red("a zero-thickness mid-surface",
            write_stl(flat_sheet(1.0, 3.0), tmp / "sheet.stl"), "NO_THICKNESS")
    not_a_surface = tmp / "notes.txt"
    not_a_surface.write_text("this is a text file, not a geometry export")
    arm_red("a file that is not a surface at all", not_a_surface, "UNREADABLE")

    print("\nAXIS-ORDER ARMS -- a refusal must not depend on the axis order")
    print("-" * 74)
    # The whole point: permuting axes must change NOTHING about admission.
    for name, axes in (("chord X, span Y, thickness Z", (0, 1, 2)),
                       ("chord X, thickness Y, span Z", (0, 2, 1)),
                       ("thickness X, chord Y, span Z", (1, 2, 0)),
                       ("span X, chord Y, thickness Z", (2, 0, 1))):
        p = write_stl(naca_wing(1.0, 3.0, 0.12, axes=axes),
                      tmp / f"perm_{axes}.stl")
        d = admit(p)
        check(f"good wing, {name}", d["code"], "ADMITTED",
              f"discovered: {d['axes']['convention']}" if d["admitted"] else "")
        pb = write_stl(scaled(naca_wing(1.0, 3.0, 0.12, axes=axes), 1000.0),
                       tmp / f"permbad_{axes}.stl")
        check(f"mm export, {name}", admit(pb)["code"], "TOO_LARGE")

    print("\nTHE DEFECT ARM -- the question the original reading never asked")
    print("-" * 74)
    r = agrees_with(REAL_UPLOAD, ACT_CONVENTION)
    check("uploaded wing does NOT use the act's axis convention",
          r["agrees"], False,
          f"file uses {r['found_convention']}; "
          f"the act assumed {r['expected_convention']}")
    r2 = agrees_with(REFERENCE_WING, ACT_CONVENTION)
    check("reference wing DOES use the act's axis convention",
          r2["agrees"], True, f"file uses {r2['found_convention']}")

    print("\nMUTATION ARMS -- each refusal must come FROM its own threshold")
    print("-" * 74)
    # A refusal that survives its own threshold being disabled was never
    # produced by that threshold, and the arm above proved nothing. Each
    # mutation is applied to the live module and then put back.
    from workflows import geometry_admission as GA
    for attr, broken, path, was in (
            ("MAX_THICKNESS_TO_CHORD", 2.0, tmp / "blob.stl",
             "NOT_A_LIFTING_SURFACE"),
            ("MAX_PLAUSIBLE_EXTENT_M", 1e9, tmp / "mm.stl", "TOO_LARGE"),
            ("MIN_PLAUSIBLE_EXTENT_M", 0.0, tmp / "tiny.stl", "TOO_SMALL"),
            ("MIN_THICKNESS_FRACTION", 0.0, tmp / "sheet.stl", "NO_THICKNESS")):
        keep = getattr(GA, attr)
        setattr(GA, attr, broken)
        after = admit(path)["code"]
        setattr(GA, attr, keep)
        check(f"{was} disappears when {attr} is disabled",
              after != was, True,
              f"with the threshold off the same file returns {after}")
        check(f"{was} returns when {attr} is restored",
              admit(path)["code"], was)

    print("\nWHAT THE CUSTOMER WOULD HEAR")
    print("-" * 74)
    for label, path in (("uploaded wing", REAL_UPLOAD),
                        ("millimetre export", tmp / "mm.stl"),
                        ("solid block", tmp / "blob.stl")):
        print(f"  on the {label}:")
        for line in sentences(admit(path)):
            print(f"    \"{line}\"")

    print("\n" + "=" * 74)
    if FAILURES:
        print(f"{len(FAILURES)} ARM(S) WRONG")
        for f in FAILURES:
            print("  " + f)
        return 2
    print("Every arm as registered: the checker refused five surfaces, "
          "admitted nine,\nand its refusals did not move when the axes were "
          "permuted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
