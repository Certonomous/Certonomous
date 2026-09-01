"""The jet-flap screen's numbers, loaded from the one implementation.

THIS FILE HOLDS NO ARITHMETIC ON PURPOSE. The reader it exposes lives beside
the run tree it reads, at

    verification/runs/JF1_jet_flap/jf1_display_numbers.py

and the same file is called by the printed result sheet, by the lift panel
embedded in that sheet, by the standalone lift figure, and by the grid page.
Those four surfaces all report the same quantity, and two of them used to carry
their own copy of it as a hard-coded constant. The copies disagreed with the
measurement and with each other, and nobody noticed because a constant never
raises. One implementation is the whole point; a second one here would rebuild
exactly the failure that was just removed.

Loading by absolute path rather than importing a package adds no coupling this
module did not already have: the screen is hard-wired to that run tree, names
its cases explicitly, and is meaningless without it.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

#: The single implementation. Kept as a module-level constant so a moved tree
#: fails loudly here, once, rather than half-reporting from several places.
_SOURCE = Path("/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap"
               "/jf1_display_numbers.py")


def _load():
    """Import the reader by path, or say plainly why the screen cannot run.

    A missing reader is not something to degrade around. The screen exists to
    put measured numbers on camera, and without the reader there are none, so
    the failure is raised rather than absorbed into an empty result.
    """
    if not _SOURCE.is_file():
        raise ImportError(
            f"the jet-flap reader is not at {_SOURCE}; the screen has no "
            f"numbers to show and must not run")
    name = "jf1_display_numbers"
    existing = sys.modules.get(name)
    if existing is not None and getattr(existing, "__file__", None) == str(_SOURCE):
        return existing
    spec = importlib.util.spec_from_file_location(name, _SOURCE)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load the jet-flap reader from {_SOURCE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_impl = _load()

# Re-exported by name so a reader of the screen can see exactly what it uses.
ReaderRefused = _impl.ReaderRefused
#: The planted value every reader in the implementation must see before it is
#: allowed to report. Re-exported so the screen can NAME it on camera without
#: a second copy of the constant: a screen that states an instrument check
#: with its own literal would keep saying so after the reader changed it.
PLANT = _impl.PLANT
RUN_ROOT = _impl.RUN_ROOT
FLOW_CASE = _impl.FLOW_CASE
SWEEP_CASES = _impl.SWEEP_CASES
SWEEP_TIME = _impl.SWEEP_TIME
SETTLE_WINDOW = _impl.SETTLE_WINDOW
assert_one_grid = _impl.assert_one_grid
#: The whole one-grid rule, over every grid the screen DISPLAYS rather than
#: only the tabulated ones. ``assert_one_grid`` could not see the flow
#: picture's grid, which is how the gates line came to assert that the
#: tabulated grid carried the fields as well.
assert_display_grids = _impl.assert_display_grids
read_figure_provenance = _impl.read_figure_provenance
#: The frozen registration the UPFRONT forecast is read out of, and the
#: artifact that forecast cites. Named here so the act can cite it without a
#: second copy of the path.
PREREGISTRATION = _impl.PREREGISTRATION
registered_sweep_estimate = _impl.registered_sweep_estimate
display_citation = _impl.display_citation
flow_facts = _impl.flow_facts
movement_1sf = _impl.movement_1sf
reference_citation = _impl.reference_citation
settling = _impl.settling
sweep_facts = _impl.sweep_facts
sweep_rows = _impl.sweep_rows
wall_yplus = _impl.wall_yplus

__all__ = [
    "PLANT",
    "ReaderRefused", "RUN_ROOT", "FLOW_CASE", "SWEEP_CASES", "SWEEP_TIME",
    "SETTLE_WINDOW", "assert_one_grid", "assert_display_grids",
    "read_figure_provenance", "PREREGISTRATION", "registered_sweep_estimate",
    "display_citation", "flow_facts", "movement_1sf",
    "reference_citation", "settling", "sweep_facts", "sweep_rows",
    "wall_yplus",
]
