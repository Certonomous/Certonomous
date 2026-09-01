#!/usr/bin/env python3
"""Every number the jet-flap display screen puts on camera, read from the
landed run tree at present time.

Nothing here starts a solver, writes into a case, or derives a value from
anything but files already on disk. It is a reader, and the whole point of a
reader is that it can be wrong in the one way that looks like good news: it
can return a clean, plausible, empty answer because it was looking in the
wrong place.

That happened while this module was being written. A first draft read the
aerofoil wall values out of the y+ field by the patch name ``aerofoil``. The
patch in the run tree is spelled ``airfoil``. The reader found no patch,
returned an empty list, and reported y+ max as 0.0 for both meshes: a number
that would have gone on camera as proof of an exquisitely resolved wall, and
which meant only that the reader was blind.

So every reader below is paired with a PLANT (CLAUDE.md rule 3): a known
perturbation written into a copy of the real file, read back through the same
code path, and asserted. A reader that cannot see the plant REFUSES. It does
not fall back, does not warn, and does not return a zero.
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Where the landed runs are. One constant, so a moved tree fails loudly in one
# place rather than half-reporting from several.
# ---------------------------------------------------------------------------

RUN_ROOT = Path("/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap")

#: The finer grid the flow picture and the wall resolution come from. Its
#: reference area is the full unit span.
FLOW_CASE = RUN_ROOT / "JF1_P1_L1_CMESH_PHYSICS"
FLOW_TIME = "20000"

#: The grid the five force calculations ran on. Its reference area is the
#: one-cell slab thickness, and mixing the two reports lift 100x wrong.
SWEEP_CASES: tuple[tuple[float, str], ...] = (
    (0.00, "JF1_L1_UNBLOWN_A0"),
    (0.05, "JF1_L1_BLOWN_CMU005_A0"),
    (0.10, "JF1_L1_BLOWN_CMU010_A0"),
    (0.20, "JF1_L1_BLOWN_CMU020_A0"),
    (0.40, "JF1_L1_BLOWN_CMU040_A0"),
)
SWEEP_TIME = "8000"

#: The wall the boundary layer is resolved on, spelled as the run tree spells
#: it. The comment is the whole reason this constant exists rather than being
#: written inline at the call site.
WALL_PATCH = "airfoil"
SLOT_PATCH = "jetSlot"

#: Jet deflection, radians. 30 degrees below the chord line at the trailing
#: edge, as registered.
TAU_RAD = 0.5235987755982988

#: The settling window the screen quotes. Deliberately the full final fifth of
#: the force calculations rather than the last thousand iterations: a shorter
#: window always reports less movement and is the flattering choice.
SETTLE_WINDOW = 4000

#: The plant. Chosen so it cannot be confused with a physical value in any
#: field this module reads, and so it survives a float round trip exactly.
PLANT = 1.234e-03


class ReaderRefused(RuntimeError):
    """A reader could not see a value planted where it was told to look."""


# ---------------------------------------------------------------------------
# 1. OpenFOAM scalar field, one boundary patch
# ---------------------------------------------------------------------------

def _patch_block(text: str, patch: str) -> str:
    """The body of one named boundaryField entry.

    Raises rather than returning "" for a patch that is not there: an absent
    patch is the failure this module exists to catch, and a caller that gets
    an empty string back will compute a clean zero from it.
    """
    marker = re.search(rf"^\s*{re.escape(patch)}\s*$", text, re.M)
    if marker is None:
        raise ReaderRefused(
            f"no boundary patch named {patch!r} in this field; the reader was "
            f"looking in the wrong place and any value it returned would be "
            f"an artefact of that")
    tail = text[marker.end():]
    opening = tail.index("{")
    depth = 0
    for index, char in enumerate(tail[opening:], start=opening):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return tail[opening + 1:index]
    raise ReaderRefused(f"unterminated boundaryField block for {patch!r}")


def _values(block: str) -> list[float]:
    """The scalar values of one patch entry, uniform or nonuniform."""
    listed = re.search(r"nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\(", block)
    if listed:
        count = int(listed.group(1))
        rest = block[listed.end():]
        body = rest[:rest.index(")")]
        values = [float(token) for token in body.split()]
        if len(values) != count:
            raise ReaderRefused(
                f"patch declares {count} values and {len(values)} were parsed")
        return values
    uniform = re.search(r"value\s+uniform\s+([-\d.eE+]+)\s*;", block)
    if uniform:
        return [float(uniform.group(1))]
    raise ReaderRefused("patch entry carries no readable value")


def read_patch(field_path: Path, patch: str) -> list[float]:
    """Scalar values on one patch of one written field."""
    field_path = Path(field_path)
    if not field_path.is_file():
        raise ReaderRefused(f"no field written at {field_path}")
    return _values(_patch_block(
        field_path.read_text(encoding="utf-8", errors="replace"), patch))


def _plant_patch(field_path: Path, patch: str) -> None:
    """Prove read_patch can see a value it did not expect.

    A copy of the real field has its first patch value replaced by PLANT and
    is read back through read_patch. This is the control for a wall-resolution
    number: it establishes that the reader is looking at THIS patch of THIS
    file, and not silently at nothing.
    """
    with tempfile.TemporaryDirectory(prefix="jf1_plant_") as work:
        copy = Path(work) / Path(field_path).name
        shutil.copy2(field_path, copy)
        text = copy.read_text(encoding="utf-8", errors="replace")
        block = _patch_block(text, patch)
        before = _values(block)
        if not before:
            raise ReaderRefused(f"nothing to plant into on patch {patch!r}")
        first = f"{before[0]!r}"
        # Replace the first value token inside this patch's block only, so the
        # plant cannot land in a different patch and be read back from there.
        planted_block = block.replace(
            re.search(r"[-\d][-\d.eE+]*", block[block.index("("):]).group(0)
            if "(" in block else first,
            f"{PLANT!r}", 1)
        copy.write_text(text.replace(block, planted_block, 1),
                        encoding="utf-8")
        seen = read_patch(copy, patch)
        if not any(abs(value - PLANT) < 1e-12 for value in seen):
            raise ReaderRefused(
                f"planted {PLANT} into patch {patch!r} of {field_path} and the "
                f"reader did not see it; every value this reader reports about "
                f"that patch is unevidenced")


def wall_yplus(case_dir: Path, time_dir: str) -> dict[str, float]:
    """Wall y+ on the aerofoil surface: the resolution claim, with its plant."""
    field = Path(case_dir) / time_dir / "yPlus"
    _plant_patch(field, WALL_PATCH)
    values = read_patch(field, WALL_PATCH)
    return {"n": len(values), "min": min(values), "max": max(values),
            "mean": sum(values) / len(values), "path": str(field)}


def slot_faces(case_dir: Path) -> dict[str, object]:
    """How many cells span the slot mouth, and whether the slot is open.

    The open/closed reading is the one fact on this screen that a plausible
    sentence has already got wrong once: the unblown calculation is a
    slot-CLOSED reference, not the blown case with the jet turned down.
    """
    boundary = Path(case_dir) / "constant" / "polyMesh" / "boundary"
    if not boundary.is_file():
        raise ReaderRefused(f"no mesh boundary file at {boundary}")
    block = _patch_block(
        boundary.read_text(encoding="utf-8", errors="replace"), SLOT_PATCH)
    kind = re.search(r"\btype\s+(\w+)\s*;", block)
    faces = re.search(r"\bnFaces\s+(\d+)\s*;", block)
    if kind is None or faces is None:
        raise ReaderRefused(f"slot entry in {boundary} carries no type/nFaces")
    return {"type": kind.group(1), "faces": int(faces.group(1)),
            "open": kind.group(1) != "wall", "path": str(boundary)}


# ---------------------------------------------------------------------------
# 2. Force history
# ---------------------------------------------------------------------------

def _coefficient_file(case_dir: Path) -> Path:
    path = Path(case_dir) / "postProcessing" / "forceCoeffs" / "0" / "coefficient.dat"
    if path.is_file():
        return path
    raise ReaderRefused(f"no force history at {path}")


def read_lift_history(case_dir: Path) -> list[float]:
    """Lift coefficient at every iteration, in order."""
    path = _coefficient_file(case_dir)
    column = None
    values: list[float] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("#"):
            names = line.lstrip("#").split()
            if "Cl" in names:
                column = names.index("Cl")
            continue
        if column is None:
            raise ReaderRefused(f"{path} has data before any header naming Cl")
        fields = line.split()
        if len(fields) > column:
            values.append(float(fields[column]))
    if not values:
        raise ReaderRefused(f"{path} carries no rows")
    return values


def _plant_history(case_dir: Path) -> None:
    """Prove the lift reader reads the Cl column and not a neighbour.

    The plant is written into the LAST row's Cl field of a copy, which is the
    row the settling window is most sensitive to. A reader picking up Cd or
    Cl(f) instead will not see it.
    """
    path = _coefficient_file(case_dir)
    with tempfile.TemporaryDirectory(prefix="jf1_plant_") as work:
        copy_dir = Path(work) / "postProcessing" / "forceCoeffs" / "0"
        copy_dir.mkdir(parents=True)
        copy = copy_dir / "coefficient.dat"
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        column = None
        last = None
        for index, line in enumerate(lines):
            if line.startswith("#"):
                names = line.lstrip("#").split()
                if "Cl" in names:
                    column = names.index("Cl")
                continue
            last = index
        if column is None or last is None:
            raise ReaderRefused(f"{path} has no Cl column to plant into")
        fields = lines[last].split()
        fields[column] = repr(PLANT)
        lines[last] = " ".join(fields)
        copy.write_text("\n".join(lines) + "\n", encoding="utf-8")
        seen = read_lift_history(copy.parent.parent.parent.parent)
        if abs(seen[-1] - PLANT) > 1e-12:
            raise ReaderRefused(
                f"planted {PLANT} into the last lift value of {path} and the "
                f"reader read {seen[-1]} instead; it is not reading that column")


def movement_1sf(value: float) -> float:
    """One movement figure, rounded UP to one significant figure.

    The rounding lives here, beside the number, because the printed pages
    promise it in words. The caption on the result sheet reads "rounded up to
    one significant figure", and the constants it replaced did not satisfy
    that under EITHER settling window: rounding 6.901e-07 up to one
    significant figure gives 7e-07, and the sheet printed 5e-07. Four of the
    five printed values failed the rounding rule the caption states, which is
    what condemns them independently of any argument about the window.

    So the operation the caption names is performed here, once, and both the
    table and the figure that carries the same quantity call it. A generator
    that rounds to NEAREST while its caption says UP is the same defect in a
    quieter form.

    A NEGATIVE INPUT REFUSES. A half range is max minus min over a window and
    cannot be negative, so a negative value here means the reader that
    produced it is broken. Rounding it to 0.0 would answer an impossible input
    with the most flattering number available, and that zero would print on
    the sheet as a calculation that had stopped moving entirely. Every other
    reader in this file raises rather than degrading; this one does too.

    Exactly 0.0 is allowed through, because a window in which the lift never
    moved at all is physically possible and has already been observed on the
    lowest-blowing row over a shorter window.
    """
    if value < 0.0:
        raise ReaderRefused(
            f"movement cannot be negative and this one is {value!r}; a half "
            f"range is a maximum minus a minimum, so the reader that produced "
            f"it is wrong and its zero would print as a perfectly settled "
            f"calculation")
    if value == 0.0:
        return 0.0
    import math

    exponent = math.floor(math.log10(value))
    return math.ceil(value / 10 ** exponent) * 10 ** exponent


def settling(case_dir: Path, window: int = SETTLE_WINDOW) -> dict[str, float]:
    """How much the lift still moved over the final ``window`` iterations.

    Half the range, not the standard deviation and not the end-to-end drift:
    the range is the only one of the three that cannot hide an excursion
    inside the window.

    This is the number the screen quotes INSTEAD of a convergence claim. No
    calculation in this family met its convergence criterion, so a settling
    figure is what there is, and it is reported as movement rather than as
    evidence of convergence.
    """
    _plant_history(case_dir)
    history = read_lift_history(case_dir)
    if len(history) < window:
        raise ReaderRefused(
            f"asked for the final {window} iterations and only "
            f"{len(history)} exist; a shorter window would report less "
            f"movement than the screen claims to be showing")
    tail = history[-window:]
    return {"window": window, "half_range": 0.5 * (max(tail) - min(tail)),
            "final": history[-1], "mean": sum(tail) / len(tail),
            "iterations": len(history)}


# ---------------------------------------------------------------------------
# 3. Mesh size and the last turbulence residual
# ---------------------------------------------------------------------------

def cell_count(case_dir: Path) -> dict[str, object]:
    log = Path(case_dir) / "log.checkMesh"
    if not log.is_file():
        raise ReaderRefused(f"no mesh check log at {log}")
    found = re.search(r"^\s*cells:\s*(\d+)\s*$",
                      log.read_text(encoding="utf-8", errors="replace"), re.M)
    if found is None:
        raise ReaderRefused(f"{log} states no cell count")
    return {"cells": int(found.group(1)), "path": str(log)}


def measured_core_minutes(case_dir: Path) -> dict[str, object]:
    """What a case actually cost, read off its own log rather than typed.

    Core-minutes are wall seconds times ranks over sixty, and BOTH factors are
    read: the wall time from the last ExecutionTime line, the rank count from
    the decomposition dictionary, cross-checked against the processor
    directories that actually exist. A rank count taken from one of those two
    alone is a number nobody measured; taken from neither, it is a literal, and
    a literal cost is how a sheet came to quote a run as "still running" for
    hours after it finished.

    REFUSES A RUN THAT DID NOT FINISH. A cost quoted as final for an
    incomplete run is worse than no cost, because it reads as the whole bill.
    The End line is the cheapest honest test of that and it is checked here so
    no caller can forget to.
    """
    log = Path(case_dir) / "log.simpleFoam"
    if not log.is_file():
        raise ReaderRefused(f"no solver log at {log}")
    text = log.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"^End\s*$", text, re.M):
        raise ReaderRefused(
            f"{log} carries no End line, so this run did not finish and its "
            f"cost is not a final cost")
    times = re.findall(r"^ExecutionTime = ([\d.]+) s", text, re.M)
    if not times:
        raise ReaderRefused(f"{log} states no ExecutionTime")
    wall = float(times[-1])

    ranks = 1
    control = Path(case_dir) / "system" / "decomposeParDict"
    if control.is_file():
        stripped = re.sub(r"//[^\n]*", "",
                          control.read_text(encoding="utf-8", errors="replace"))
        found = re.search(r"^\s*numberOfSubdomains\s+(\d+)\s*;", stripped, re.M)
        if found:
            ranks = int(found.group(1))
    # The cross-check. A dictionary states an intention; the processor
    # directories are what the run actually decomposed into.
    procs = len([p for p in Path(case_dir).glob("processor[0-9]*") if p.is_dir()])
    if procs and procs != ranks:
        raise ReaderRefused(
            f"{control} asks for {ranks} ranks and {case_dir} holds {procs} "
            f"processor directories; the core-minute figure would be wrong by "
            f"the ratio between them")

    # TWO BASES, NAMED, BECAUSE THEY ARE NOT THE SAME NUMBER and mixing them
    # across a table is how a cost line stops being comparable with itself.
    #
    #   solver_core_min : the solver's own ExecutionTime x ranks. Excludes
    #                     start-up, decomposition and teardown.
    #   core_min        : the run record's core_min_MEASURED, wall clock x
    #                     ranks. GROSS, and larger.
    #
    # The result sheet quotes the gross basis for all five completed rows, so
    # `core_min` is what a sixth row must be quoted in. Reporting the solver
    # figure beside five gross ones would understate the sixth by roughly the
    # start-up cost and look like an efficiency that is not there. Rule 12 of
    # the constitution asks a spend figure to say which basis it is on; this
    # returns both so a caller cannot quietly pick the flattering one.
    result = {"wall_s": wall, "ranks": ranks,
              "solver_core_min": wall * ranks / 60.0, "path": str(log)}
    for status in sorted(Path(case_dir).rglob("RUN_STATUS*")):
        found = re.search(r"^\s*core_min_MEASURED\s+([\d.]+)",
                          status.read_text(encoding="utf-8", errors="replace"),
                          re.M)
        if found:
            result["core_min"] = float(found.group(1))
            result["core_min_basis"] = "gross wall clock x ranks"
            result["core_min_path"] = str(status)
            break
    else:
        raise ReaderRefused(
            f"no run record under {case_dir} states core_min_MEASURED; the "
            f"gross cost the sheet quotes for every other row is not "
            f"available for this one and must not be substituted with the "
            f"smaller solver-only figure")
    return result


def last_k_residual(case_dir: Path) -> dict[str, object]:
    """Turbulent kinetic energy equation imbalance at the final iteration.

    Reported because it is the channel that fails: not one calculation in this
    family reached the 1e-06 criterion set before running, and the screen says
    so rather than quoting a residual that did converge.

    WHY TAKING THE LAST MATCH IS SAFE HERE, AND WOULD NOT BE FOR p. This
    function keeps the last "Solving for k" line of the run. That is correct
    for k and for omega and it is WRONG for p, because these cases run with
    nNonOrthogonalCorrectors 1: pressure is solved twice per iteration and the
    last match is the second corrector pass, not the iteration's residual.
    Measured on JF1_L1_BLOWN_CMU020_A0/log.simpleFoam: 8000 time steps, 8000
    k solves, 8000 omega solves, and 16000 p solves.

    So the immunity is real but it is a property of WHICH FIELD is read, not
    of this code. Do not generalise this function to p by parameterising the
    field name: that would silently return a corrector-pass residual. A
    pressure reader has to select by iteration, not by last match.
    """
    log = Path(case_dir) / "log.simpleFoam"
    if not log.is_file():
        raise ReaderRefused(f"no solver log at {log}")
    last = None
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        found = re.search(
            r"Solving for k,\s*Initial residual = ([-\d.eE+]+)", line)
        if found:
            last = float(found.group(1))
    if last is None:
        raise ReaderRefused(f"{log} carries no turbulence residual lines")
    return {"k_initial_residual": last, "path": str(log)}


# ---------------------------------------------------------------------------
# 4. Published reference: Williams, Butler and Wood, 1961, equation (2)
# ---------------------------------------------------------------------------

def _theory_json() -> dict:
    import json

    path = RUN_ROOT / "artefacts_actB" / "jf1_theory_actB_numbers.json"
    if not path.is_file():
        raise ReaderRefused(f"no reference curve at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def reference_curve() -> dict[float, dict]:
    """Published total lift against blowing, keyed by jet momentum.

    Read from the committed reference file rather than recomputed here, so the
    screen and the printed sheet cannot drift apart. The citation travels with
    it: the interpolation formula is printed by Williams, Butler and Wood, and
    attributing it to the 1956 paper it builds on is wrong.
    """
    data = _theory_json()
    return {row["C_mu"]: row for row in data["theory"]}


def reference_citation() -> str:
    """The full citation, with the page and equation locators, for the record."""
    return _theory_json()["source"]["citation"]


#: What the screen says out loud. The full citation carries printed-page and
#: section locators, and "section 2" read aloud on camera is indistinguishable
#: from an internal rule number, which the output rules forbid. The locators
#: stay in reference_citation() for the record and off the screen.
DISPLAY_CITATION = ("Williams, Butler and Wood, The Aerodynamics of Jet "
                    "Flaps, Aeronautical Research Council Reports and "
                    "Memoranda No. 3304, 1961, equation (2)")


def display_citation() -> str:
    """The citation as the screen says it, checked against the full one.

    The check is the point: a short form that drifted off the paper it claims
    would be a false attribution in the one place a viewer would never verify
    it. The authors and the report number must both appear in the full
    citation this file reads, or the short form is refused.
    """
    full = reference_citation()
    for token in ("Williams", "Butler", "Wood", "3304", "1961"):
        if token not in full:
            raise ReaderRefused(
                f"the short citation claims {token!r} and the reference file "
                f"does not carry it; the screen would be attributing the "
                f"curve to a paper this lab has not checked")
    return DISPLAY_CITATION


# ---------------------------------------------------------------------------
# 5. The two grids, kept apart
# ---------------------------------------------------------------------------

def reference_area(case_dir: Path) -> float:
    """The reference area this case's coefficients were divided by.

    Read per case, never assumed. The force sweep ran on a slab 0.01 m thick
    and the flow picture on a slab 1.0 m thick; a table that mixed the two
    would report lift a hundredfold wrong, and has to be impossible to build
    rather than merely discouraged.
    """
    control = Path(case_dir) / "system" / "controlDict"
    if not control.is_file():
        raise ReaderRefused(f"no run dictionary at {control}")
    text = control.read_text(encoding="utf-8", errors="replace")
    stripped = re.sub(r"//[^\n]*", "", text)
    found = re.search(r"\bAref\s+([-\d.eE+]+)\s*;", stripped)
    if found is None:
        raise ReaderRefused(f"{control} states no reference area")
    return float(found.group(1))


def assert_one_grid(case_dirs) -> float:
    """Refuse to build a table spanning both grids.

    This is the guard, not a comment: every table the screen emits passes its
    own cases through here first, and a mixed table raises instead of
    rendering.
    """
    areas = {round(reference_area(case), 12) for case in case_dirs}
    if len(areas) != 1:
        raise ReaderRefused(
            f"these cases do not share one reference area ({sorted(areas)}); "
            f"putting them on one axis reports lift wrong by the ratio between "
            f"them")
    return areas.pop()


# ---------------------------------------------------------------------------
# 6. The whole screen's numbers, in one call
# ---------------------------------------------------------------------------

def sweep_rows() -> list[dict]:
    """One row per force calculation: what was solved, and how settled it is."""
    import math

    cases = [RUN_ROOT / name for _, name in SWEEP_CASES]
    area = assert_one_grid(cases)
    theory = reference_curve()
    rows = []
    for (c_mu, name), case in zip(SWEEP_CASES, cases):
        slot = slot_faces(case)
        settle = settling(case)
        reaction = c_mu * math.sin(TAU_RAD)
        rows.append({
            "C_mu": c_mu,
            "slot_open": slot["open"],
            "slot_faces": slot["faces"],
            "CL_aero": settle["final"],
            "jet_reaction": reaction,
            "CL_total": settle["final"] + reaction,
            "CL_published": theory[c_mu]["CL_total"],
            "movement": settle["half_range"],
            "window": settle["window"],
            "iterations": settle["iterations"],
            "k_residual": last_k_residual(case)["k_initial_residual"],
            "cells": cell_count(case)["cells"],
            "Aref": area,
            "case_dir": str(case),
        })
    return rows


def flow_facts() -> dict:
    """The finer grid: what it resolves, and how long it ran."""
    case = FLOW_CASE
    return {
        "cells": cell_count(case)["cells"],
        "yplus": wall_yplus(case, FLOW_TIME),
        "slot": slot_faces(case),
        "Aref": reference_area(case),
        "iterations": int(FLOW_TIME),
        "case_dir": str(case),
    }


def sweep_facts() -> dict:
    """The force grid: what it resolves. Reported beside the finer grid and
    never on the same axis as it."""
    case = RUN_ROOT / SWEEP_CASES[3][1]
    return {
        "cells": cell_count(case)["cells"],
        "yplus": wall_yplus(case, SWEEP_TIME),
        "slot": slot_faces(case),
        "Aref": reference_area(case),
        "iterations": int(SWEEP_TIME),
        "case_dir": str(case),
    }


def main() -> int:
    """Read everything and print it, so the screen's numbers can be checked
    without the screen. Exit 2 if any reader refused."""
    try:
        flow = flow_facts()
        sweep = sweep_facts()
        rows = sweep_rows()
    except ReaderRefused as exc:
        print(f"READER REFUSED: {exc}")
        return 2
    print(f"reference: {reference_citation()}")
    print(f"\nfiner grid   cells={flow['cells']} iters={flow['iterations']} "
          f"Aref={flow['Aref']} yplus_max={flow['yplus']['max']:.4g} "
          f"n={flow['yplus']['n']} slot={flow['slot']['type']}/"
          f"{flow['slot']['faces']}")
    print(f"force grid   cells={sweep['cells']} iters={sweep['iterations']} "
          f"Aref={sweep['Aref']} yplus_max={sweep['yplus']['max']:.4g} "
          f"n={sweep['yplus']['n']} slot={sweep['slot']['type']}/"
          f"{sweep['slot']['faces']}")
    print(f"\n{'C_mu':>5} {'open':>5} {'CL_aero':>12} {'react':>9} "
          f"{'CL_total':>10} {'published':>10} {'move/4000':>11} {'k_res':>10}")
    for row in rows:
        print(f"{row['C_mu']:5.2f} {str(row['slot_open']):>5} "
              f"{row['CL_aero']:12.6f} {row['jet_reaction']:9.4f} "
              f"{row['CL_total']:10.6f} {row['CL_published']:10.6f} "
              f"{row['movement']:11.3e} {row['k_residual']:10.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
