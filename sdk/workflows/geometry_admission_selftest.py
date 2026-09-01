"""Drive :mod:`geometry_admission` RED and GREEN in ONE invocation.

Standing rule 3, applied to a gate rather than to a comparator: a checker that
has never been shown refusing anything is not a checker, and a checker that
refuses everything is not one either. Every run of this file does both, on the
real files the act actually receives and on surfaces built to be impossible.

Run:  python3 sdk/workflows/geometry_admission_selftest.py
Exit: 0 all arms as registered, 2 any arm wrong.
"""

from __future__ import annotations

import itertools
import math
import struct
import subprocess
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


def read_stl_tris(path) -> list:
    """The triangles of a binary STL, so a tracked file can be permuted.

    The value-invariance arm has to permute the axes of the REAL uploaded
    surface, not of a look-alike this file generates: a generated body would
    only prove the generator and the reader agree with each other.
    """
    raw = Path(path).read_bytes()
    n = struct.unpack_from("<I", raw, 80)[0]
    if 84 + 50 * n != len(raw):
        raise ValueError(f"{path} is not a binary STL")
    out = []
    for i in range(n):
        v = struct.unpack_from("<12f", raw, 84 + 50 * i)
        out.append((v[3:6], v[6:9], v[9:12]))
    return out


def permute(tris: list, order: tuple) -> list:
    """The same body with its coordinate axes reordered. Nothing else moves."""
    return [tuple(tuple(p[k] for k in order) for p in t) for t in tris]


# --------------------------------------------------------------------------

FAILURES: list[str] = []
# The arm count is COUNTED, never asserted. The published figure for this file
# was once given as 34 from a commit message while the file ran 33, and a
# re-count then said 34 again because a grep counted lines containing the
# phrase and took the summary line for an arm. A number that describes this
# file is derived from this file.
ARMS = 0


def check(label: str, got, want, detail: str = "") -> None:
    global ARMS
    ARMS += 1
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

    print("\nVALUE-INVARIANCE ARM -- the load-bearing one, and it was missing")
    print("-" * 74)
    # WHY THIS ARM EXISTS (verification audit, FAIL_OPEN_GATE_AUDIT section 20,
    # 2026-09-01). Every arm above this point asks whether the VERDICT held or
    # whether the ROLES were recovered. None of them asked whether the NUMBERS
    # the customer is told are right. Verification proved the gap by mutating
    # ONE LINE of the reader -- inverting the chord/span role assignment -- and
    # watching it tell the customer "3 m chord, 1 m span, 4.0% of chord"
    # against the true "1 m chord, 3 m span, 12.0%", the original defect's
    # exact signature, WHILE ALL EIGHT AXIS-ORDER ARMS RETURNED AS REGISTERED.
    #
    # Their fair caveat, kept here so nobody overstates it: the suite did still
    # exit 2 under that mutation, but it was killed by the defect arm on the
    # reference wing, not by any axis-order arm. It caught it for the wrong
    # reason. An overlap is not coverage.
    #
    # So this arm asserts the REPORTED VALUES against ground truth, to full
    # precision, and then asserts they do not move under any permutation of
    # the input. That one arm covers both failure modes: a reader whose role
    # assignment is inverted moves the values with the input untouched, and a
    # future permutation regression moves them with the reader untouched.
    #
    # THE REGISTERED VALUES ARE THE FILE'S OWN BYTES, and getting that right
    # took a correction. They were first pinned at thickness_m = 0.12002,
    # which is what the reader returned in the environment this selftest runs
    # in -- and the reader returned 0.12001006305217743 in an environment with
    # the SDK off sys.path, on identical bytes (md5 3d41177e...). Pinning
    # "whatever this environment reports" to full precision is not ground
    # truth; it is a pin that passes or fails on how it was invoked.
    #
    # The divergence is now explained and closed at the source: _read prefers
    # the raw file reader, because 0.12002 was the viewport's 5-decimal
    # transport rounding leaking into a measurement. 0.12001006305217743 is
    # the float32 the binary STL actually stores, so it is what the file
    # measures and what the customer is told about. The arm below asserts the
    # two readings' relationship rather than trusting either.
    REGISTERED = {"chord_m": 1.0, "span_m": 3.0,
                  "thickness_m": 0.12001006305217743}
    REGISTERED_RATIO = "12.0%"

    def reported(path) -> dict:
        d = admit(path)
        return {k: d["axes"][k] for k in REGISTERED} if d.get("axes") else {}

    def ratio_of(vals: dict) -> str:
        return f"{100.0 * vals['thickness_m'] / vals['chord_m']:.1f}%"

    base_vals = reported(REAL_UPLOAD)
    check("uploaded wing: reported chord/span/thickness are the true ones",
          base_vals, REGISTERED,
          f"chord {base_vals.get('chord_m')} m, span {base_vals.get('span_m')} "
          f"m, thickness {base_vals.get('thickness_m')} m")
    check("uploaded wing: the thickness the CUSTOMER is told",
          ratio_of(base_vals) if base_vals else None, REGISTERED_RATIO,
          f"says {ratio_of(base_vals) if base_vals else '-'}; 4.0% here would "
          f"be the original defect's signature")

    up_tris = read_stl_tris(REAL_UPLOAD)
    for order in itertools.permutations((0, 1, 2)):
        p = write_stl(permute(up_tris, order), tmp / f"inv_{''.join(map(str, order))}.stl")
        vals = reported(p)
        check(f"same values with the input axes permuted {order}",
              vals, REGISTERED,
              f"convention now {admit(p)['axes']['convention']}"
              if admit(p).get("axes") else "")

    # THE RED LEG. An arm that has never been driven red is not evidence, so
    # this is verification's own mutation rather than an easier one of my
    # choosing: the chord/span role assignment is inverted, and the arm must
    # catch it BY NAME. The inversion is applied at discover_axes' output
    # boundary, which is where its one-line effect is observable; it is not a
    # fork of the function and it is put back immediately.
    from workflows import geometry_admission as GA

    real_discover = GA.discover_axes

    def inverted(surf):
        d = dict(real_discover(surf))
        d["chord_axis"], d["span_axis"] = d["span_axis"], d["chord_axis"]
        d["chord_m"], d["span_m"] = d["span_m"], d["chord_m"]
        return d

    # The red leg's own comparisons are made HERE rather than through check(),
    # so a deliberate failure is not printed as a WRONG arm and not counted as
    # one. What is registered is the CATCH, and that is what check() records.
    GA.discover_axes = inverted
    bent = reported(REAL_UPLOAD)
    bent_ratio = ratio_of(bent) if bent else None
    GA.discover_axes = real_discover
    moved = sorted(k for k in REGISTERED if bent.get(k) != REGISTERED[k])
    check("RED LEG: the arm CATCHES verification's inverted role assignment",
          (moved, bent_ratio != REGISTERED_RATIO), (["chord_m", "span_m"], True),
          f"with the input untouched the reader said {bent_ratio} against the "
          f"registered {REGISTERED_RATIO}, moving {', '.join(moved) or 'nothing'}")
    check("and green again once the reader is put back",
          reported(REAL_UPLOAD), REGISTERED)

    # THE ONE BODY THE THINNEST-EXTENT ASSUMPTION GETS WRONG, and what happens
    # to it (verification finding 1, 2026-09-01: discover_axes takes the
    # thinnest extent to BE the thickness, which is a prior and not a
    # discovery). A stub whose SPAN is shorter than its own thickness would be
    # described with span and thickness exchanged. It never reaches a customer
    # that way, because it is refused first by a gate computed on the sorted
    # extents, which no axis order can move. The assumption's blast radius is
    # therefore a body this reader already will not run -- and that is now
    # armed rather than argued.
    # TWO READERS, AND THE ARM SAYS SO OUT LOUD. _read can reach the surface
    # two ways, and they do NOT agree: the SDK's transport loader rounds every
    # coordinate to 5 decimals for the viewport. That is a fact about the two
    # readers, so it is asserted as one rather than left to be rediscovered by
    # whoever next sees a number move without the data moving.
    #
    # The assertion is the RELATIONSHIP, not a loosened tolerance. Loosening
    # is what let the 4.0% through, and it is refused here: the registered
    # claim is that the transport reading equals the raw reading with each
    # coordinate rounded to 5 decimals, exactly, and that _read returns the
    # raw one. A transport loader that started doing anything else -- welding
    # vertices, dropping faces, rescaling -- breaks this arm immediately,
    # while the known 9.94e-06 m rounding does not.
    print("\nTWO-READER ARM -- a reader with two answers must say so")
    print("-" * 74)
    raw_v, raw_f = GA._read_stl_fallback(Path(REAL_UPLOAD))
    raw_surf = GA.Surface(REAL_UPLOAD, raw_v, raw_f)
    try:
        from chief_engineer.geometry import load_surface
        payload = load_surface(str(REAL_UPLOAD), max_faces=10 ** 9)
        tr_surf = GA.Surface(REAL_UPLOAD, payload["vertices"], payload["faces"])
    except Exception as exc:                              # pragma: no cover
        tr_surf = None
        print(f"  (transport loader not importable here: {exc})")
    check("_read takes the RAW file reader on an STL",
          GA._read(REAL_UPLOAD).read_by, "raw file bytes",
          "so the reported measurement cannot depend on sys.path")
    check("the raw reader reports the float32 the file stores",
          raw_surf.extents[raw_surf.by_size[0]], REGISTERED["thickness_m"])
    if tr_surf is not None:
        rounded = GA.Surface(
            REAL_UPLOAD, [[round(c, 5) for c in v] for v in raw_v], raw_f)
        check("the two readers DISAGREE, and by exactly the transport rounding",
              tr_surf.extents == rounded.extents, True,
              f"transport {tr_surf.extents[tr_surf.by_size[0]]!r} against raw "
              f"{raw_surf.extents[raw_surf.by_size[0]]!r}: "
              f"{abs(tr_surf.extents[tr_surf.by_size[0]] - raw_surf.extents[raw_surf.by_size[0]]):.2e} m, "
              f"and it lands on the SMALLEST extent")
        check("the disagreement does not reach the customer's percentage",
              (f"{100.0 * tr_surf.extents[tr_surf.by_size[0]] / tr_surf.extents[tr_surf.by_size[1]]:.1f}%",
               f"{100.0 * raw_surf.extents[raw_surf.by_size[0]] / raw_surf.extents[raw_surf.by_size[1]]:.1f}%"),
              (REGISTERED_RATIO, REGISTERED_RATIO),
              "both render 12.0%; nothing on screen was ever wrong")

    # AND THE PROOF, IN A SEPARATE PROCESS. Everything above runs in one
    # interpreter with the SDK already imported, so it cannot demonstrate what
    # happens when the SDK is NOT importable -- which is the environment the
    # bug was found in. This arm re-reads the same file in a fresh process
    # with only the workflows directory on sys.path, exactly the shell that
    # reported 0.12001006305217743, and requires the same answer. It is the
    # one arm here that would have gone red before this fix.
    # sys.path is FILTERED, never replaced: replacing it removes the standard
    # library too, and the probe then fails on `import __future__` and proves
    # nothing about the reader. (It did exactly that once, here.) What is
    # removed is every Certonomous entry, so `chief_engineer` is unimportable
    # while Python still works.
    probe = (
        "import sys;"
        "sys.path[:]=[p for p in sys.path if 'Certonomous' not in p];"
        f"sys.path.insert(0, r'{Path(__file__).resolve().parent}');"
        "import geometry_admission as G;"
        "assert G._read.__module__=='geometry_admission';"
        "\ntry:\n import chief_engineer\n raise SystemExit('SDK still importable')\nexcept ImportError:\n pass\n"
        f"s=G._read(r'{REAL_UPLOAD}');"
        "print(repr(s.extents[s.by_size[0]]), s.read_by, sep='|')")
    out = subprocess.run([sys.executable, "-c", probe],
                         capture_output=True, text=True)
    got = out.stdout.strip().split("|") if out.returncode == 0 else [out.stderr]
    check("same answer in a process where the SDK is NOT importable",
          (got[0] if got else None, got[1] if len(got) > 1 else None),
          (repr(REGISTERED["thickness_m"]), "raw file bytes"),
          "the environment that first reported the disagreement")

    stub = write_stl(naca_wing(1.0, 0.08, 0.12), tmp / "stub.stl")
    stub_d = admit(stub)
    check("a stub thicker than its own span is refused, not mislabelled",
          (stub_d["code"], stub_d["admitted"]),
          ("NOT_A_LIFTING_SURFACE", False),
          "the one class the thinnest-extent assumption gets wrong never "
          "reaches a customer")

    # THE IDENTITY CHECK IS A SECOND CONSUMER OF THIS READER, and it used to
    # bypass it -- calling the viewport's transport loader directly under a
    # comment claiming the surface was "read exactly as it arrived". It is
    # routed through _read now, and these arms hold it there.
    print("\nIDENTITY-CHECK ARMS -- the act's other consumer of this reader")
    print("-" * 74)
    from workflows import _a2_shape as SH

    doc = SH.load()
    ident = SH.identify(doc, REFERENCE_WING.name, directory=REFERENCE_WING.parent)
    check("the reference wing identifies as itself",
          (ident["match"], ident["at_resolution_floor"]), (True, True),
          f"worst {ident['worst_pct']:.3g}% against a float32 floor of "
          f"{ident['resolution_pct']:.3g}%, so the screen says 'below "
          f"{ident['resolution_pct']:.1g}%' rather than a made-up five figures")
    other = SH.identify(doc, REAL_UPLOAD.name, directory=REAL_UPLOAD.parent)
    check("the uploaded NACA0012 is still a different wing",
          (other["match"], other["at_resolution_floor"]), (False, False),
          f"worst {other['worst_pct']:.4g}%")
    # THE PLANTED CONTROL on the floor branch. "Below the resolution floor" is
    # only evidence if a real disagreement is shown escaping it: a branch that
    # says "agrees" can hide a defect, and this one is on screen.
    bent = bytearray(REFERENCE_WING.read_bytes())
    n_bent = struct.unpack_from("<I", bent, 80)[0]
    for i in range(n_bent):
        off = 84 + 50 * i
        v = list(struct.unpack_from("<12f", bent, off))
        for k in (5, 8, 11):                       # the span coordinate
            if v[k] > 14.0:
                v[k] += 0.001                      # 1 mm on a 14 m span
        struct.pack_into("<12f", bent, off, *v)
    (tmp / "bent_ref.stl").write_bytes(bytes(bent))
    planted = SH.identify(doc, "bent_ref.stl", directory=tmp)
    check("a 1 mm stretch does NOT hide under the resolution floor",
          planted["at_resolution_floor"], False,
          f"it reads {planted['worst_pct']:.3g}% and gets a number on screen; "
          f"through the rounded copy a perfect match already read 3.3e-04%, so "
          f"a defect this size was indistinguishable from the rounding")

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
    print(f"Every arm as registered, {ARMS} of them. The checker refuses "
          f"surfaces it cannot run and\nadmits ones it can; its refusals do "
          f"not move when the axes are permuted; and the\nchord, span and "
          f"thickness it reports do not move either, under any permutation "
          f"of\nthe input or under an inverted role assignment inside the "
          f"reader.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
