#!/usr/bin/env python3
"""Shared Roache/GCI triple instrument for the 2D aero families.

WHAT THIS IS.  The lab's accepted grid-convergence standard was written inside
the thermal comparators and has never been available anywhere else.  This module
PORTS it -- it does not reinvent it -- so that a 2D aero ladder (cavity, cylinder,
step, airfoil) is graded by the same arithmetic and the same refusals as the
T-family.  The two parents are:

  * ``verification/runs/T-family/T1_runs/analyse_t1c.py`` -- the canonical
    ``gci()`` at line 321, ``FS = 1.25`` at line 44 and ``R_REFINE = 1.6`` at
    line 45.  EQUAL-ratio form.
  * ``verification/runs/T-family/T3_runs/analyse_t3.py`` -- ``gci_unequal()``
    (Celik et al. 2008 fixed point, line 337) and the planted-zero control
    (``PLANT = 1.234e-03`` line 81, ``plant_into_T()`` line 287, refusal at
    line 801).  UNEQUAL-ratio form.

``--selftest`` IMPORTS BOTH PARENTS AND CROSS-CHECKS AGAINST THEM.  The
provenance above is therefore an executable claim, not a comment: if this file
ever stops reproducing ``analyse_t1c.gci`` and ``analyse_t3.gci_unequal`` to
1e-12 the selftest fails.  (CLAUDE.md rule 6: a citation that sits inside an
executable check is the only kind that cannot rot quietly.)

THE ONE PLACE THIS PORT DELIBERATELY DIVERGES FROM ITS PARENTS.

  ``richardson`` here is ``f_fine - e21 / den``.  BOTH PARENTS RETURN
  ``f_fine + e21 / den`` (``analyse_t1c.py:337``, ``analyse_t3.py:384``), and
  that sign is wrong: with ``e21 = f_med - f_fine``, Roache's extrapolate
  ``f_exact = f_fine + (f_fine - f_med) / (r^p - 1)`` is ``f_fine - e21/den``.
  The ``+`` form reflects the extrapolate through the finest value onto the
  COARSE side -- the same distance from ``f_fine``, the wrong way.

  Worked control, which is also a regression test in ``--selftest``: a ladder
  1.16 / 1.04 / 1.01 at r = 2, dim = 2 recovers p = 2.0000 and its exact value
  is 1.0.  The corrected form returns 1.00; the parents' form returns 1.02.

  ``order``, ``GCI_pct`` and ``GCI_abs`` are UNAFFECTED -- they are built from
  ``|e21|``, so the blast radius is the extrapolated value alone.  The
  independent trace is commit ``2f1d6cb7`` (heat-transfer, 2026-08-24), which
  names both parent lines and gives the structural identity that settles it
  without appeal to authority:

      richardson + richardson_parent_convention == 2 * f_fine, exactly.

  That identity is asserted in ``--selftest`` too.

  THIS INSTRUMENT IS BOUND TO THE LAB'S STANDING RULE, NOT MERELY PARALLEL TO
  IT.  The heat-transfer team registered the value-control as **N-T8** at commit
  ``792acd8f``: "every comparator's --selftest must carry a VALUE-checking
  control against a synthetic power law whose limit is known by construction,
  asserted to 1e-12 relative -- not a check that the key exists".  Section
  (iii-b) of ``--selftest`` IS that control for this file: the ladder
  1.16/1.04/1.01 is a power law with limit 1.0 by construction, and the
  extrapolate is asserted against it at 1e-12.  N-T8 is satisfied here by
  conformance to the registered rule, so the lab lands ONE instrument class and
  not two.  The blast radius is also the same as the parents': ``band_verdict``
  grades the FINE VALUE, never the extrapolate, so no verdict this module can
  emit is a function of ``richardson`` -- display-only, exactly as the
  heat-transfer trace found lab-wide.

  THE PARENTS ARE NOT EDITED.  They are frozen under CLAUDE.md rule 6, another
  team owns them, and that team has already ruled its comparators unchanged and
  recorded corrected values as dated addenda.  This file is new, so writing it
  correct is not a departure from a freeze -- it is the first instance that gets
  to be right.  Both values are returned: ``richardson`` (correct) and
  ``richardson_parent_convention`` (the ``+`` form, under that explicit name),
  so a reader comparing this instrument against a PUBLISHED thermal number can
  see both and know which is which.  The parent cross-check in ``--selftest`` is
  therefore scoped to ``order``, ``GCI_pct`` and ``GCI_abs`` -- the quantities
  the parents get right and the only ones that decide a verdict.

  Ruled by cfd-supervisor on a check-1 diff read of this file before it was
  committed, 2026-08-24.  The selftest as first written cross-checked
  ``richardson`` against the parents and passed 45/45; that is precisely how a
  wrong number gets welded to a passing test, and it is why the diff read is not
  delegable.

THE FOUR THINGS THIS INSTRUMENT REFUSES TO DO, each paid for by a named failure.

1. IT WILL NOT GUESS A DIMENSIONALITY.  ``dim`` is a required argument on every
   entry point, asserted ``in (1, 2, 3)``, and PRINTED beside every order and
   every GCI it produces.  VERIFICATION_CHARTER.md section 3.1: changing the
   assumed dimensionality divides every observed order by exactly 1.5.  The 4G
   campaign found the lab's own helper hard-coding ``(1.0 / n) ** (1.0 / 3.0)``
   -- the 3D convention -- and applying it to a 2D ladder, where it "reports the
   observed order as 0.817 where the 2D calculation gives 0.545"
   (``verification/campaign/4G_tmr_mesh_aspect_ratio.md:695``).  That exact pair
   of numbers is a live regression test in ``--selftest``.

2. IT WILL NOT GRADE WITHOUT A PLANTED-ZERO CONTROL THAT PASSED.  CLAUDE.md rule
   3.  ``grade_ladder`` REFUSES (exit 2) when handed no control, or one that did
   not pass.  A zero from a reader not shown able to see a non-zero is not
   evidence, so the reader is shown a ``PLANT``-sized perturbation through the
   SAME code path a real read uses, and must report it.

3. IT WILL NOT SOFTEN A NUMBER RATHER THAN STOP.  Missing input, malformed
   series, a ladder that does not refine, unequal ratios handed to the
   equal-ratio path: every one of them exits non-zero with the reason.  CLAUDE.md
   rule 4's discipline -- comparators refuse rather than degrade.

4. IT WILL NOT QUOTE A GCI ON A NON-MONOTONE TRIPLE.  CLAUDE.md rule 5.  A GCI
   is emitted only in the CONVERGING state, and an assertion in ``grade_ladder``
   re-checks that no GCI escaped beside a non-monotone triple.

RULE 5, IN ORDER, AND ONLY IN THIS ORDER (CLAUDE.md rule 5; the wording is
``docs/campaigns/T-family/T1b_L4_AMENDMENT.md`` section 2):

  (a) any level not iteratively converged, or not plateaued  -> NOT A RESULT;
  (b) the triple DIVERGENT / STAGNANT / OSCILLATORY / EXACT   -> NOT A RESULT,
      with the value, EVERY triple and EVERY order printed beside it;
  (c) CONVERGING -> PASS inside the pre-registered band, else GATE FAIL, with
      the GCI printed at Fs = 1.25.

THE GATE IS ONE-WAY.  It may turn a PASS or a GATE FAIL INTO a NOT A RESULT and
may never do the reverse.  This is enforced structurally: the band verdict is
computed FIRST and unconditionally, is reported beside the final verdict, and an
assertion requires the final verdict to be either that band verdict or
NOT A RESULT.

WHAT THIS INSTRUMENT CANNOT SEE, stated because a check that overstates its
reach is worse than none:

  * whether the three values came from the same case setup.  It grades numbers.
    A ladder that changed a scheme, a model or a mesh RECIPE between levels will
    be graded as if it had not (VERIFICATION_CHARTER.md section 3.2, the second
    way an observed order lies -- a slope fitted across a change of experiment).
    The caller establishes similarity; this file cannot.
  * whether the dimensionality it was handed is the true one.  It can only
    refuse a missing one and print the one it used (section 3.1, rule 1).
  * whether the finest level is anywhere near the asymptotic range.  A CONVERGING
    triple means the last step fell to at most r^-0.5 of the previous one.  It
    does not mean a limit was reached.
  * anything about iterative convergence or plateau.  Those states are the
    CALLER's measurements, handed in; step (a) only acts on them.

EXIT CODES.  0 = PASS, 1 = GATE FAIL, 3 = NOT A RESULT, 2 = REFUSE.  NOT A RESULT
is given its own code deliberately: "checked and failed the band" and "cannot be
graded at all" are different facts and collapsing them is the L-45 error.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import shutil
import sys
import tempfile

# ---------------------------------------------------------------------------
# registered constants -- ported, not chosen
# ---------------------------------------------------------------------------
FS = 1.25                       # Roache safety factor, three levels (T1c:44)
PLANT = 1.234e-03               # planted-zero control perturbation (T3:81)
STAGNANT_FLOOR = 0.5            # 0 < p < STAGNANT_FLOOR is STAGNANT (T1c:321)
EQUAL_RATIO_TOL = 1.0e-9        # |r21 - r32| above this is NOT an equal ladder
PLANT_READBACK_TOL = 1.0e-12    # the plant must land to this (T3:302)

EXIT_OK, EXIT_FAIL, EXIT_REFUSE, EXIT_NOT_A_RESULT = 0, 1, 2, 3

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT",
            "BLOCKED", "PENDING")

NOT_A_RESULT_STATES = ("DIVERGENT", "STAGNANT", "OSCILLATORY", "EXACT",
                       "NO_ORDER")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T1C_PATH = os.path.join(_REPO, "verification", "runs", "T-family", "T1_runs",
                        "analyse_t1c.py")
T3_PATH = os.path.join(_REPO, "verification", "runs", "T-family", "T3_runs",
                       "analyse_t3.py")


class Refusal(Exception):
    """Raised where a library caller can catch it; the CLI turns it into exit 2."""


def refuse(msg):
    raise Refusal(msg)


# ---------------------------------------------------------------------------
# dimensionality -- required, asserted, and carried into every result
# ---------------------------------------------------------------------------
def require_dim(dim):
    """``dim`` is REQUIRED and asserted.  There is no default and there will not
    be one: VERIFICATION_CHARTER.md section 3.1 rule 1, "a ladder whose
    dimensionality is unstated is refused.  Not defaulted."
    """
    if isinstance(dim, bool) or not isinstance(dim, int):
        refuse(f"dimensionality must be the int 1, 2 or 3, got {dim!r}; "
               "an unstated dimensionality is refused, never defaulted "
               "(VERIFICATION_CHARTER.md 3.1 rule 1)")
    assert dim in (1, 2, 3), f"dim must be in (1, 2, 3), got {dim!r}"
    return dim


def representative_h(n_cells, dim, n_ref=1.0):
    """h = (N_ref / N) ** (1 / dim).

    N_ref only sets the scale; every ratio this module forms is invariant to it,
    so it defaults to 1.0 and dim does NOT default at all.
    """
    require_dim(dim)
    if n_cells is None or float(n_cells) <= 0.0:
        refuse(f"cell count must be positive, got {n_cells!r}")
    return (float(n_ref) / float(n_cells)) ** (1.0 / dim)


def refinement_ratio(n_coarser, n_finer, dim):
    """r = h_coarser / h_finer = (N_finer / N_coarser) ** (1 / dim), r > 1 when
    the ladder actually refines."""
    require_dim(dim)
    return representative_h(n_coarser, dim) / representative_h(n_finer, dim)


# ---------------------------------------------------------------------------
# the two GCI forms, ported
# ---------------------------------------------------------------------------
def gci_equal(f_coarse, f_med, f_fine, r, dim, fs=FS):
    """EQUAL-ratio Roache GCI.  Port of ``analyse_t1c.gci`` (T1c:321), which
    takes its ratio from the module constant ``R_REFINE``; here the ratio is an
    argument and ``dim`` travels with the answer.

    Refuses to invent an order.  States: EXACT, OSCILLATORY, DIVERGENT,
    STAGNANT, CONVERGING.

    Richardson sign: see the module docstring, "THE ONE PLACE THIS PORT
    DELIBERATELY DIVERGES FROM ITS PARENTS".
    """
    require_dim(dim)
    if r <= 1.0:
        refuse(f"the ladder does not refine: r = {r:.6f} (dim = {dim})")
    e21 = f_med - f_fine
    e32 = f_coarse - f_med
    common = dict(dim=dim, r21=r, r32=r, e21=e21, e32=e32, fs=fs,
                  values=(f_coarse, f_med, f_fine), form="equal")
    if e21 == 0.0:
        return dict(common, state="EXACT")
    if e32 / e21 < 0.0:
        return dict(common, state="OSCILLATORY", ratio=e32 / e21)
    p = math.log(abs(e32 / e21)) / math.log(r)
    if p <= 0.0:
        return dict(common, state="DIVERGENT", order=p)
    if p < STAGNANT_FLOOR:
        return dict(common, state="STAGNANT", order=p)
    den = r ** p - 1.0
    return dict(common, state="CONVERGING", order=p,
                GCI_pct=100.0 * fs * abs(e21 / f_fine) / den,
                GCI_abs=fs * abs(e21) / den,
                richardson=f_fine - e21 / den,
                richardson_parent_convention=f_fine + e21 / den)


def gci_unequal(f_coarse, f_med, f_fine, r21, r32, dim, fs=FS):
    """UNEQUAL-ratio Roache/Celik GCI.  Port of ``analyse_t3.gci_unequal``
    (T3:337), with ``dim`` carried.

        p = | ln|e32/e21| + q(p) | / ln r21,
        q(p) = ln( (r21^p - s) / (r32^p - s) ),   s = sign(e32/e21)

    ``s`` IS HARDCODED TO +1 IN THE CODE BELOW, AND THAT IS CORRECT RATHER THAN
    A SIMPLIFICATION: the ``ratio < 0`` branch returns OSCILLATORY before the
    fixed point is ever entered, so by construction s = +1 everywhere this
    iteration runs.  Stated here because the general formula above describes a
    case this function deliberately refuses instead of computing.

    When r21 == r32 the fixed point has q(p) = 0 and this reproduces
    ``gci_equal`` exactly (asserted in --selftest).

    Richardson sign: see the module docstring, "THE ONE PLACE THIS PORT
    DELIBERATELY DIVERGES FROM ITS PARENTS".
    """
    require_dim(dim)
    if r21 <= 1.0 or r32 <= 1.0:
        refuse(f"the ladder does not refine: r21 = {r21:.6f}, "
               f"r32 = {r32:.6f} (dim = {dim})")
    e21 = f_med - f_fine
    e32 = f_coarse - f_med
    common = dict(dim=dim, r21=r21, r32=r32, e21=e21, e32=e32, fs=fs,
                  values=(f_coarse, f_med, f_fine), form="unequal")
    if e21 == 0.0:
        return dict(common, state="EXACT")
    ratio = e32 / e21
    if ratio < 0.0:
        return dict(common, state="OSCILLATORY", ratio=ratio)
    p = math.log(abs(ratio)) / math.log(r21)
    if p <= 0.0:
        return dict(common, state="DIVERGENT", order=p)
    it = 0
    if r21 != r32:
        for it in range(1, 201):
            try:
                q = math.log((r21 ** p - 1.0) / (r32 ** p - 1.0))
            except ValueError:
                return dict(common, state="DIVERGENT", order=p, iterations=it)
            p_new = abs(math.log(abs(ratio)) + q) / math.log(r21)
            if abs(p_new - p) < 1e-13:
                p = p_new
                break
            p = 0.5 * (p + p_new)          # damped; the map is a contraction
        else:
            return dict(common, state="NO_ORDER", order=p, iterations=it,
                        why="order iteration did not converge in 200 steps")
    if p <= 0.0:
        return dict(common, state="DIVERGENT", order=p, iterations=it)
    if p < STAGNANT_FLOOR:
        return dict(common, state="STAGNANT", order=p, iterations=it)
    den = r21 ** p - 1.0
    return dict(common, state="CONVERGING", order=p, iterations=it,
                GCI_pct=100.0 * fs * abs(e21 / f_fine) / den,
                GCI_abs=fs * abs(e21) / den,
                richardson=f_fine - e21 / den,
                richardson_parent_convention=f_fine + e21 / den)


def triple_from_cells(f_coarse, f_med, f_fine, n_coarse, n_med, n_fine, dim,
                      fs=FS, form="auto", equal_tol=EQUAL_RATIO_TOL):
    """Form the refinement ratios from CELL COUNTS and ``dim``, then dispatch.

    ``form``:
      "auto"     -- equal path when |r21 - r32| <= equal_tol, else unequal;
      "equal"    -- REFUSES when |r21 - r32| > equal_tol.  The stated tolerance
                    is the argument, so a caller who declares an equal ladder
                    and did not build one is stopped rather than quietly graded
                    on the wrong formula;
      "unequal"  -- always the Celik fixed point.
    """
    require_dim(dim)
    r21 = refinement_ratio(n_med, n_fine, dim)      # h_med / h_fine
    r32 = refinement_ratio(n_coarse, n_med, dim)    # h_coarse / h_med
    gap = abs(r21 - r32)
    if form not in ("auto", "equal", "unequal"):
        refuse(f"unknown ratio form {form!r}")
    if form == "equal" and gap > equal_tol:
        refuse(f"equal-ratio path requested but the ladder is unequal: "
               f"r21 = {r21:.10f}, r32 = {r32:.10f}, |r21 - r32| = {gap:.3e} "
               f"> tol {equal_tol:.3e} (dim = {dim}); cells "
               f"{n_coarse}/{n_med}/{n_fine}.  Use form='unequal'.")
    use_equal = (form == "equal") or (form == "auto" and gap <= equal_tol)
    if use_equal:
        out = gci_equal(f_coarse, f_med, f_fine, r21, dim, fs=fs)
    else:
        out = gci_unequal(f_coarse, f_med, f_fine, r21, r32, dim, fs=fs)
    out["cells"] = (n_coarse, n_med, n_fine)
    out["ratio_gap"] = gap
    out["h"] = tuple(representative_h(n, dim) for n in (n_coarse, n_med, n_fine))
    return out


def monotone(tr):
    """The three values decrease or increase together and neither step is zero.
    This is the ONLY condition under which a GCI may be quoted (CLAUDE.md 5)."""
    e21, e32 = tr.get("e21"), tr.get("e32")
    if e21 is None or e32 is None or e21 == 0.0 or e32 == 0.0:
        return False
    return (e32 / e21) > 0.0


# ---------------------------------------------------------------------------
# the canonical read path, and the planted-zero control that proves it can see
# ---------------------------------------------------------------------------
def read_series(path):
    """Read a level series from disk.  THIS IS THE READ PATH THE CONTROL PLANTS
    INTO -- library callers grade through ``read_series``, and the control below
    replays exactly this function, so a zero it returns is a statement about the
    file rather than about the reader.

    Format (JSON):

        {"quantity": "u(0.5,0.5)", "dim": 2,
         "levels": [{"name": "c", "cells": 2500,  "value": -0.2041},
                    {"name": "m", "cells": 6400,  "value": -0.2053},
                    {"name": "f", "cells": 16384, "value": -0.2057}]}

    Levels are ordered COARSE FIRST.  Refuses on anything it cannot read.
    """
    if not os.path.isfile(path):
        refuse(f"no series file at {path}")
    try:
        with open(path) as fh:
            doc = json.load(fh)
    except Exception as exc:                                  # noqa: BLE001
        refuse(f"{path} does not parse as JSON: {exc}")
    levels = doc.get("levels")
    if not isinstance(levels, list) or len(levels) < 3:
        refuse(f"{path}: 'levels' must be a list of at least three entries, "
               f"coarse first; got {type(levels).__name__} "
               f"{len(levels) if isinstance(levels, list) else ''}")
    out = []
    for i, lv in enumerate(levels):
        for key in ("name", "cells", "value"):
            if key not in lv:
                refuse(f"{path}: level {i} has no {key!r}")
        try:
            out.append(dict(name=str(lv["name"]), cells=int(lv["cells"]),
                            value=float(lv["value"])))
        except (TypeError, ValueError) as exc:
            refuse(f"{path}: level {i} does not read as numbers: {exc}")
    cells = [lv["cells"] for lv in out]
    if any(b <= a for a, b in zip(cells, cells[1:])):
        refuse(f"{path}: cell counts must increase, coarse first; got {cells}")
    return dict(quantity=doc.get("quantity"), dim=doc.get("dim"), levels=out,
                path=path)


def plant_into_series(path, level_name, plant=PLANT):
    """Add ``plant`` to one level's value IN PLACE, then read the file back from
    disk and prove the plant landed.  Port of the discipline in
    ``analyse_t3.plant_into_T`` (T3:287): write, re-read, and raise if the
    re-read does not show the perturbation."""
    with open(path) as fh:
        doc = json.load(fh)
    hit = None
    for lv in doc["levels"]:
        if str(lv["name"]) == str(level_name):
            hit = lv
            break
    if hit is None:
        refuse(f"cannot locate level {level_name!r} in {path}")
    before = float(hit["value"])
    hit["value"] = before + plant
    with open(path, "w") as fh:
        json.dump(doc, fh)
    back = None
    for lv in read_series(path)["levels"]:
        if lv["name"] == str(level_name):
            back = lv["value"]
    if back is None or abs((back - before) - plant) > PLANT_READBACK_TOL:
        refuse(f"the plant did not land in {path}: {before} -> {back}")
    return before, back


def planted_zero_control(path, level_name=None, plant=PLANT):
    """Copy the series to a temp directory, plant ``plant`` into one level, read
    it back THROUGH ``read_series`` -- the same function a real grade uses -- and
    report whether the reader saw it.

    ``passed`` is False, never an exception, so the caller can print the failed
    control beside the refusal; ``grade_ladder`` then refuses on it.
    """
    base = read_series(path)
    if level_name is None:
        level_name = base["levels"][0]["name"]
    before_val = [lv["value"] for lv in base["levels"]
                  if lv["name"] == str(level_name)]
    if not before_val:
        refuse(f"cannot locate level {level_name!r} in {path}")
    tmp = tempfile.mkdtemp(prefix="roache_plant_")
    try:
        work = os.path.join(tmp, os.path.basename(path))
        shutil.copy(path, work)
        before, after = plant_into_series(work, level_name, plant=plant)
        seen = None
        for lv in read_series(work)["levels"]:
            if lv["name"] == str(level_name):
                seen = lv["value"]
        delta = None if seen is None else seen - before
        ok = delta is not None and abs(delta - plant) <= PLANT_READBACK_TOL
        return dict(passed=bool(ok), planted=plant, level=str(level_name),
                    read_back_delta=(after - before),
                    reader_delta=delta, reader="read_series",
                    artifact=os.path.abspath(path))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def external_plant_control(reader_name, before, after, plant=PLANT,
                           artifact=None, level=None):
    """Wrap a control a CASE comparator ran on its OWN raw artifact.

    The generic control above proves ``read_series`` can see a plant.  A case
    comparator whose real read path runs through an OpenFOAM sample file plants
    into THAT file and re-reads it with THAT parser, then hands the two values
    here.  ``grade_ladder`` accepts either -- what it will not accept is no
    control at all.
    """
    delta = float(after) - float(before)
    return dict(passed=abs(delta - plant) <= PLANT_READBACK_TOL, planted=plant,
                read_back_delta=delta, reader_delta=delta, reader=reader_name,
                artifact=artifact, level=level)


def assert_plant_control(pc):
    if not isinstance(pc, dict):
        refuse("no planted-zero control was supplied; a zero from a reader not "
               "shown able to see a non-zero is not evidence (CLAUDE.md rule 3)")
    if not pc.get("passed"):
        refuse("planted-zero control FAILED: reader "
               f"{pc.get('reader')!r} did not see the planted "
               f"{pc.get('planted')} on {pc.get('artifact')} "
               f"(saw {pc.get('reader_delta')}); its zeros mean nothing")
    return pc


# ---------------------------------------------------------------------------
# rule 5, in order
# ---------------------------------------------------------------------------
def band_verdict(value, band):
    """PASS inside the pre-registered band, else GATE FAIL.  Computed FIRST and
    UNCONDITIONALLY so that the one-way property of the gate is checkable rather
    than asserted: the final verdict must be this one or NOT A RESULT."""
    if band is None:
        refuse("no pre-registered band was supplied; this instrument grades "
               "against a band fixed before compute, and will not invent one")
    lo, hi = (band["lo"], band["hi"]) if isinstance(band, dict) else band
    lo, hi = float(lo), float(hi)
    if hi < lo:
        refuse(f"band is inverted: lo = {lo}, hi = {hi}")
    return ("PASS" if lo <= float(value) <= hi else "GATE FAIL"), (lo, hi)


def all_triples(levels, dim, fs=FS, form="auto", equal_tol=EQUAL_RATIO_TOL):
    """Every consecutive triple in the ladder, coarse first.

    A three-level ladder yields one; a four-level ladder yields two, which is
    what "both triples printed beside it" means in
    ``T1b_L4_AMENDMENT.md`` section 2 -- (c, m, f) and (m, f, x).  The instrument
    prints ALL of them and grades the FINEST.
    """
    require_dim(dim)
    if len(levels) < 3:
        refuse(f"a Roache triple needs at least three levels, got {len(levels)}")
    out = []
    for i in range(len(levels) - 2):
        a, b, c = levels[i], levels[i + 1], levels[i + 2]
        tr = triple_from_cells(a["value"], b["value"], c["value"],
                               a["cells"], b["cells"], c["cells"], dim,
                               fs=fs, form=form, equal_tol=equal_tol)
        tr["levels"] = (a["name"], b["name"], c["name"])
        out.append(tr)
    return out


def grade_ladder(quantity, levels, dim, band, plant_control,
                 iterative_states=None, plateau_states=None, fs=FS,
                 form="auto", equal_tol=EQUAL_RATIO_TOL, reference=None):
    """CLAUDE.md rule 5, in its order, and nothing else.

    ``levels``           list of dicts (name, cells, value), COARSE FIRST.
    ``dim``              required; printed beside every order and every GCI.
    ``band``             (lo, hi) or {"lo":, "hi":}, pre-registered.  No band,
                         no grade -- refusal, not a softer number.
    ``plant_control``    the result of ``planted_zero_control`` or of
                         ``external_plant_control``.  Missing or failed -> refuse.
    ``iterative_states`` {level name: state}; anything other than "CONVERGED"
                         triggers step (a).
    ``plateau_states``   {level name: state}; anything other than "PLATEAUED"
                         triggers step (a).  Pass None when the quantity has no
                         plateau to measure, and say so in the record -- an
                         absent measurement is reported as absent, never as a
                         pass (VERIFICATION_CHARTER.md section 9, ran_before_found).
    """
    require_dim(dim)
    assert_plant_control(plant_control)
    if len(levels) < 3:
        refuse(f"{quantity}: a Roache triple needs at least three levels")

    triples = all_triples(levels, dim, fs=fs, form=form, equal_tol=equal_tol)
    finest = triples[-1]
    fine_value = levels[-1]["value"]

    # the band verdict is computed FIRST, unconditionally, and reported beside
    # the final one.  The gate is one-way and this is how that is checked.
    bv, bounds = band_verdict(fine_value, band)

    row = dict(quantity=quantity, dim=dim, fs=fs,
               value=fine_value, reference=reference, band=bounds,
               band_verdict=bv,
               levels=[dict(lv) for lv in levels],
               triples=[_triple_public(t) for t in triples],
               orders=[t.get("order") for t in triples],
               states=[t["state"] for t in triples],
               monotone=monotone(finest),
               planted_zero=dict(plant_control),
               iterative_convergence=iterative_states,
               plateau=plateau_states)

    # ---- (a) iterative convergence and plateau, before ANY grid claim -------
    bad_it = sorted(k for k, v in (iterative_states or {}).items()
                    if v != "CONVERGED")
    bad_pl = sorted(k for k, v in (plateau_states or {}).items()
                    if v != "PLATEAUED")
    if iterative_states is None:
        refuse(f"{quantity}: no iterative-convergence states supplied; step (a) "
               "of rule 5 cannot be evaluated and an unevaluated step is not a "
               "passed one")
    if bad_it or bad_pl:
        row["verdict"] = "NOT A RESULT"
        row["why"] = ("levels " + ",".join(bad_it + bad_pl) +
                      " are not iteratively converged or not plateaued; no grid "
                      "claim can be made from this triple")
        return _seal(row, bv)

    # ---- (b) the triple itself ---------------------------------------------
    if finest["state"] in NOT_A_RESULT_STATES:
        row["verdict"] = "NOT A RESULT"
        row["why"] = (f"finest triple {finest['levels']} is "
                      f"{finest['state']} at dim = {dim}"
                      + (f", observed order {finest['order']:.4f}"
                         if "order" in finest else "")
                      + "; the value, every triple and every order are printed "
                        "beside it, and NO GCI is quoted because the three "
                        "values are not monotone")
        return _seal(row, bv)

    # ---- (c) CONVERGING: band, with the GCI printed -------------------------
    row["verdict"] = bv
    row["order"] = finest["order"]
    row["GCI_pct"] = finest["GCI_pct"]
    row["GCI_abs"] = finest["GCI_abs"]
    row["richardson"] = finest["richardson"]
    row["richardson_parent_convention"] = finest["richardson_parent_convention"]
    row["why"] = (f"finest triple {finest['levels']} CONVERGING at dim = {dim}, "
                  f"observed order {finest['order']:.4f}, "
                  f"GCI {finest['GCI_pct']:.4f} % = {finest['GCI_abs']:.6g} "
                  f"absolute at Fs = {fs}")
    return _seal(row, bv)


def _triple_public(t):
    keep = ("levels", "state", "order", "dim", "r21", "r32", "ratio_gap",
            "form", "values", "cells", "e21", "e32", "GCI_pct", "GCI_abs",
            "richardson", "richardson_parent_convention", "iterations", "why")
    return {k: t[k] for k in keep if k in t}


def _seal(row, bv):
    """The two structural assertions that make the printed row trustworthy."""
    # the gate is one-way: it may only turn PASS or GATE FAIL INTO NOT A RESULT.
    assert row["verdict"] in (bv, "NOT A RESULT"), (
        f"the gate moved {bv} to {row['verdict']}, which rule 5 forbids")
    assert row["verdict"] in VERDICTS, f"verdict {row['verdict']!r} is not in the "\
        "fixed vocabulary"
    # no GCI beside a non-monotone triple, ever.
    assert not ("GCI_pct" in row and not row["monotone"]), (
        "a GCI was produced beside a non-monotone triple")
    return row


# ---------------------------------------------------------------------------
# display -- dim printed beside every order and every GCI
# ---------------------------------------------------------------------------
def format_row(row):
    lines = []
    ref = "" if row.get("reference") is None else f"  ref {row['reference']:.6g}"
    lines.append(f"[{row['quantity']}]  value {row['value']:.6g}{ref}  "
                 f"band [{row['band'][0]:.6g}, {row['band'][1]:.6g}]  "
                 f"dim = {row['dim']}")
    for t in row["triples"]:
        order = ("n/a" if t.get("order") is None
                 else f"{t['order']:.4f} (dim = {t['dim']})")
        # GCI_pct divides by f_fine, so a functional near zero makes the
        # percentage meaningless.  GCI_abs is printed BESIDE it, always, so the
        # reader is never at the mercy of the denominator.
        gci = ("" if "GCI_pct" not in t
               else f"  GCI {t['GCI_pct']:.4f} % = {t['GCI_abs']:.6g} abs "
                    f"at Fs = {row['fs']}, dim = {t['dim']}"
                    f"  Richardson {t['richardson']:.8g} "
                    f"(parent-convention form {t['richardson_parent_convention']:.8g}"
                    f", sign-flipped, see module docstring)")
        lines.append(f"    triple {t['levels']} cells {t['cells']} "
                     f"r21 {t['r21']:.4f} r32 {t['r32']:.4f} ({t['form']})  "
                     f"values {tuple(round(v, 8) for v in t['values'])}  "
                     f"state {t['state']}  order {order}{gci}")
    pc = row["planted_zero"]
    lines.append(f"    planted-zero control: {'PASSED' if pc['passed'] else 'FAILED'}"
                 f"  planted {pc['planted']}  reader {pc['reader']}  "
                 f"saw {pc.get('reader_delta')}")
    if not row["monotone"]:
        lines.append("    GCI NOT QUOTED: the three values are not monotone "
                     "(CLAUDE.md rule 5).")
    lines.append(f"    band verdict (computed first, unconditionally): "
                 f"{row['band_verdict']}")
    lines.append(f"    VERDICT: {row['verdict']} -- {row['why']}")
    return "\n".join(lines)


def exit_code_for(verdict):
    return {"PASS": EXIT_OK, "GATE REACHED": EXIT_OK, "GATE FAIL": EXIT_FAIL,
            "NOT A RESULT": EXIT_NOT_A_RESULT}.get(verdict, EXIT_FAIL)


# ---------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------
_CHECKS = []


def check(name, ok, detail=""):
    _CHECKS.append((name, bool(ok), detail))
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


def _load(path, name):
    import importlib.util
    d = os.path.dirname(path)
    if d not in sys.path:
        sys.path.insert(0, d)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _synthetic(p_true, dim, n0=2500, ratio_cells=2.56, f_exact=1.0, amp=0.1):
    """A ladder built to a KNOWN order at a stated dim: f_i = f_exact + amp*h_i^p."""
    cells = [n0, n0 * ratio_cells, n0 * ratio_cells ** 2]
    hs = [representative_h(n, dim) for n in cells]
    vals = [f_exact + amp * h ** p_true for h in hs]
    return [dict(name=nm, cells=int(round(c)), value=v)
            for nm, c, v in zip(("c", "m", "f"), cells, vals)]


def selftest():
    print("roache_triple.py --selftest")
    ok_state = {"c": "CONVERGED", "m": "CONVERGED", "f": "CONVERGED"}

    # -- (i) THE 4G DEFECT, ENCODED AS A LIVE REGRESSION TEST ----------------
    # 4G_tmr_mesh_aspect_ratio.md:695 -- the helper hard-coded (1/n)**(1/3) and
    # on a 2D ladder "reports the observed order as 0.817 where the 2D
    # calculation gives 0.545".  Same measurements, ladder N -> 4N -> 16N.
    print("(i) dimensionality divides the observed order by exactly 1.5 "
          "(VERIFICATION_CHARTER 3.1; the 4G defect)")
    k = 2.0 ** 0.545                       # e32/e21 chosen to give p2D = 0.545
    e21, f_fine = 1.0e-3, 1.0
    vals = (f_fine + e21 * (1.0 + k), f_fine + e21, f_fine)
    cells = (1000, 4000, 16000)
    t2 = triple_from_cells(*vals, *cells, 2)
    t3 = triple_from_cells(*vals, *cells, 3)
    check("2D ladder read at dim=2 gives p = 0.545",
          abs(t2["order"] - 0.545) < 5e-4, f"p = {t2['order']:.6f}, dim = 2")
    check("the same ladder read at dim=3 gives p = 0.8175 (the 4G number)",
          abs(t3["order"] - 0.8175) < 5e-4, f"p = {t3['order']:.6f}, dim = 3")
    check("p(dim=3) / p(dim=2) == 1.5 exactly, equal-ratio path",
          abs(t3["order"] / t2["order"] - 1.5) < 1e-12,
          f"ratio = {t3['order'] / t2['order']:.16f}")

    # the same invariance on an UNEQUAL ladder, and on the derived quantities
    ucells = (2500, 6000, 16384)
    uvals = (1.0402, 1.0121, 1.0043)
    u2 = triple_from_cells(*uvals, *ucells, 2, form="unequal")
    u3 = triple_from_cells(*uvals, *ucells, 3, form="unequal")
    check("p(dim=3) / p(dim=2) == 1.5 on an UNEQUAL-ratio ladder too",
          abs(u3["order"] / u2["order"] - 1.5) < 1e-9,
          f"{u2['order']:.6f} -> {u3['order']:.6f}, "
          f"ratio = {u3['order'] / u2['order']:.12f}")
    check("Richardson value is INVARIANT under the dim assumption",
          abs(u3["richardson"] - u2["richardson"]) <= 1e-12 * abs(u2["richardson"]),
          f"{u2['richardson']:.12f} vs {u3['richardson']:.12f}")
    check("GCI is INVARIANT under the dim assumption",
          abs(u3["GCI_pct"] - u2["GCI_pct"]) <= 1e-12 * abs(u2["GCI_pct"]),
          f"{u2['GCI_pct']:.10f} % vs {u3['GCI_pct']:.10f} %")

    # -- (ii) dim is required and asserted -----------------------------------
    print("(ii) dimensionality is required, asserted, and printed")
    for bad in (None, 0, 4, 2.0, "2", True):
        try:
            representative_h(1000, bad)
            check(f"refuses dim = {bad!r}", False, "no refusal raised")
        except (Refusal, AssertionError):
            check(f"refuses dim = {bad!r}", True)
    check("every order carries its dim", t2.get("dim") == 2 and t3.get("dim") == 3)
    check("every GCI carries its dim", u2["dim"] == 2 and "GCI_pct" in u2)

    # -- (iii) provenance: the ports reproduce their parents -----------------
    print("(iii) the ports reproduce the thermal parents to 1e-12 on order, "
          "GCI_pct and GCI_abs (executable provenance)")
    print("      'richardson' is EXCLUDED FROM THIS CROSS-CHECK ON PURPOSE: "
          "both parents\n      carry a sign-flipped extrapolate "
          "(analyse_t1c.py:337, analyse_t3.py:384),\n      traced "
          "independently at commit 2f1d6cb7.  Matching them on it would weld "
          "the\n      defect to a passing test.  The parents are frozen "
          "(rule 6) and are NOT edited;\n      this file returns the correct "
          "value and the parent-convention value side by side.")
    t1c = _load(T1C_PATH, "t1c_parent")
    t3m = _load(T3_PATH, "t3_parent")
    check("parents import and carry the registered constants",
          t1c.FS == FS and t3m.FS == FS and t3m.PLANT == PLANT and
          abs(t1c.R_REFINE - 1.6) < 1e-15,
          f"FS = {t1c.FS}, PLANT = {t3m.PLANT}, R_REFINE = {t1c.R_REFINE}")
    r = t1c.R_REFINE
    worst_e = worst_u = 0.0
    for tr in ((1.10, 1.04, 1.01), (1.00, 1.02, 1.05), (1.0, 1.03375, 1.06375),
               (1.00, 1.10, 1.05), (2.0, 2.0, 2.0), (0.9, 0.95, 0.97)):
        a = t1c.gci(*tr)
        b = gci_equal(*tr, r, 2)
        c = t3m.gci_unequal(*tr, r, r)
        d = gci_unequal(*tr, r, r, 2)
        if a["state"] != b["state"] or c["state"] != d["state"]:
            check(f"state agrees with the parents on {tr}", False,
                  f"{a['state']}/{b['state']} {c['state']}/{d['state']}")
        for key in ("order", "GCI_pct", "GCI_abs"):
            if key in a and key in b:
                worst_e = max(worst_e, abs(a[key] - b[key]))
            if key in c and key in d:
                worst_u = max(worst_u, abs(c[key] - d[key]))
        # and the parent-convention value, which IS matched, proving the
        # divergence is exactly one sign and nothing else drifted.
        if "richardson" in a and "richardson_parent_convention" in b:
            worst_e = max(worst_e,
                          abs(a["richardson"] - b["richardson_parent_convention"]))
        if "richardson" in c and "richardson_parent_convention" in d:
            worst_u = max(worst_u,
                          abs(c["richardson"] - d["richardson_parent_convention"]))
    check("gci_equal reproduces analyse_t1c.gci on order, GCI and the "
          "parent-convention extrapolate", worst_e < 1e-12,
          f"worst |delta| = {worst_e:.3e}")
    check("gci_unequal reproduces analyse_t3.gci_unequal on order, GCI and the "
          "parent-convention extrapolate", worst_u < 1e-12,
          f"worst |delta| = {worst_u:.3e}")
    check("the port's own 'richardson' DIFFERS from the parents' "
          "(the deliberate correction is live)",
          abs(t1c.gci(1.16, 1.04, 1.01)["richardson"]
              - gci_equal(1.16, 1.04, 1.01, 2.0, 2)["richardson"]) > 1e-9,
          f"parent {t1c.gci(1.16, 1.04, 1.01)['richardson']:.10g} vs port "
          f"{gci_equal(1.16, 1.04, 1.01, 2.0, 2)['richardson']:.10g}")
    ge = gci_equal(1.10, 1.04, 1.01, 1.6, 2)
    gu = gci_unequal(1.10, 1.04, 1.01, 1.6, 1.6, 2)
    check("equal and unequal paths agree at equal ratios",
          abs(ge["order"] - gu["order"]) < 1e-12 and
          abs(ge["GCI_pct"] - gu["GCI_pct"]) < 1e-12,
          f"p {ge['order']:.12f} vs {gu['order']:.12f}")

    # -- (iii-b) THE RICHARDSON SIGN, WHICH THE PARENT CROSS-CHECK CANNOT SEE -
    # The test that would have caught the defect, and the structural identity
    # the heat-transfer team used to settle it (commit 2f1d6cb7).
    print("(iii-b) the Richardson extrapolate, on a ladder whose exact value "
          "is KNOWN")
    for label, g in (("equal", gci_equal(1.16, 1.04, 1.01, 2.0, 2)),
                     ("unequal", gci_unequal(1.16, 1.04, 1.01, 2.0, 2.0, 2))):
        check(f"[{label}] 1.16/1.04/1.01 at r = 2, dim = 2 recovers p = 2",
              abs(g["order"] - 2.0) < 1e-12, f"p = {g['order']:.12f}")
        check(f"[{label}] and extrapolates to the TRUE value 1.0",
              abs(g["richardson"] - 1.0) < 1e-12,
              f"richardson = {g['richardson']:.12f} "
              f"(parent-convention form = "
              f"{g['richardson_parent_convention']:.12f}, which is 1.02)")
        check(f"[{label}] identity: richardson + parent-convention "
              f"== 2 * f_fine, exactly",
              abs(g["richardson"] + g["richardson_parent_convention"]
                  - 2.0 * 1.01) < 1e-15,
              f"{g['richardson']:.12f} + "
              f"{g['richardson_parent_convention']:.12f} = "
              f"{g['richardson'] + g['richardson_parent_convention']:.12f}")
    # the same identity across a family, so it is a property and not one point
    bad_id = []
    for tr in ((1.10, 1.04, 1.01), (0.9, 0.95, 0.97), (2.0, 1.5, 1.4)):
        for g in (gci_equal(*tr, 1.6, 2), gci_unequal(*tr, 1.5, 1.7, 2),
                  gci_unequal(*tr, 1.6, 1.6, 3)):
            if g["state"] != "CONVERGING":
                continue
            if abs(g["richardson"] + g["richardson_parent_convention"]
                   - 2.0 * tr[2]) > 1e-12 * max(1.0, abs(tr[2])):
                bad_id.append((tr, g["form"], g["dim"]))
    check("the identity holds on every CONVERGING triple in a mixed family, "
          "both forms, both dims", not bad_id, f"violations: {bad_id}")

    # -- (iv) refuse rather than degrade -------------------------------------
    print("(iv) refuse rather than degrade")
    try:
        triple_from_cells(1.1, 1.04, 1.01, 2500, 6000, 16384, 2, form="equal")
        check("equal-ratio path refuses an unequal ladder", False, "no refusal")
    except Refusal as exc:
        check("equal-ratio path refuses an unequal ladder", True, str(exc)[:70])
    try:
        triple_from_cells(1.1, 1.04, 1.01, 16384, 6400, 2500, 2)
        check("refuses a ladder that does not refine", False, "no refusal")
    except Refusal:
        check("refuses a ladder that does not refine", True)
    try:
        read_series(os.path.join(tempfile.gettempdir(), "no_such_series_xyz.json"))
        check("refuses a missing series file", False, "no refusal")
    except Refusal:
        check("refuses a missing series file", True)
    tmpd = tempfile.mkdtemp(prefix="roache_selftest_")
    try:
        bad = os.path.join(tmpd, "bad.json")
        with open(bad, "w") as fh:
            json.dump({"levels": [{"name": "c", "cells": 100, "value": 1.0},
                                  {"name": "m", "cells": 50, "value": 1.0},
                                  {"name": "f", "cells": 25, "value": 1.0}]}, fh)
        try:
            read_series(bad)
            check("refuses a series whose cell counts do not increase", False, "")
        except Refusal:
            check("refuses a series whose cell counts do not increase", True)

        # -- (v) the planted-zero control, and a control ON the control -------
        print("(v) planted-zero control (CLAUDE.md rule 3)")
        good = os.path.join(tmpd, "series.json")
        lv = _synthetic(2.0, 2)
        with open(good, "w") as fh:
            json.dump({"quantity": "synthetic", "dim": 2, "levels": lv}, fh)
        pc = planted_zero_control(good)
        check("a working reader SEES the planted perturbation",
              pc["passed"] and abs(pc["reader_delta"] - PLANT) < 1e-12,
              f"planted {PLANT}, saw {pc['reader_delta']:.6e}")
        after = read_series(good)["levels"][0]["value"]
        check("the control does not disturb the graded file",
              abs(after - lv[0]["value"]) == 0.0, "planted into a temp copy only")
        blind = external_plant_control("blinded_reader", 1.0, 1.0)
        check("a BLIND reader fails the control", not blind["passed"])
        try:
            grade_ladder("synthetic", lv, 2, (0.9, 1.1), blind,
                         iterative_states=ok_state)
            check("grade_ladder REFUSES on a failed control", False, "graded anyway")
        except Refusal as exc:
            check("grade_ladder REFUSES on a failed control", True, str(exc)[:60])
        try:
            grade_ladder("synthetic", lv, 2, (0.9, 1.1), None,
                         iterative_states=ok_state)
            check("grade_ladder REFUSES with NO control at all", False, "graded")
        except Refusal:
            check("grade_ladder REFUSES with NO control at all", True)

        # -- (vi) rule 5, in order --------------------------------------------
        print("(vi) rule 5, in order, and the gate is one-way")
        band_wide = (0.0, 2.0)             # the fine value is INSIDE
        for label, tr in (("DIVERGENT", (1.00, 1.02, 1.05)),
                          ("STAGNANT", (1.0, 1.03375, 1.06375)),
                          ("OSCILLATORY", (1.00, 1.10, 1.05)),
                          ("EXACT", (1.10, 1.04, 1.04))):
            levels = [dict(name=n, cells=c, value=v) for n, c, v in
                      zip(("c", "m", "f"), (2500, 6400, 16384), tr)]
            row = grade_ladder(label, levels, 2, band_wide, pc,
                               iterative_states=ok_state)
            inside = band_wide[0] <= tr[2] <= band_wide[1]
            check(f"{label} triple with the fine value INSIDE the band "
                  f"-> NOT A RESULT",
                  inside and row["verdict"] == "NOT A RESULT" and
                  row["band_verdict"] == "PASS" and "GCI_pct" not in row,
                  f"band verdict {row['band_verdict']}, final {row['verdict']}")
            check(f"{label} row prints every triple and every order",
                  len(row["triples"]) == 1 and "state" in row["triples"][0])

        conv = _synthetic(2.0, 2)
        fine = conv[-1]["value"]
        row_pass = grade_ladder("converging", conv, 2,
                                (fine - 1e-6, fine + 1e-6), pc,
                                iterative_states=ok_state)
        check("CONVERGING inside the band -> PASS, with a GCI printed",
              row_pass["verdict"] == "PASS" and "GCI_pct" in row_pass and
              row_pass["dim"] == 2,
              f"p = {row_pass['order']:.4f}, dim = 2, "
              f"GCI = {row_pass['GCI_pct']:.4f} %")
        check("a synthetic second-order ladder recovers p = 2 at dim = 2",
              abs(row_pass["order"] - 2.0) < 1e-9,
              f"p = {row_pass['order']:.12f}")
        row_fail = grade_ladder("converging", conv, 2, (fine + 1.0, fine + 2.0),
                                pc, iterative_states=ok_state)
        check("the SAME triple outside the band -> GATE FAIL (mutation control)",
              row_fail["verdict"] == "GATE FAIL" and "GCI_pct" in row_fail)
        row_it = grade_ladder("converging", conv, 2,
                              (fine - 1e-6, fine + 1e-6), pc,
                              iterative_states={"c": "CONVERGED",
                                                "m": "NOT_CONVERGED",
                                                "f": "CONVERGED"})
        check("step (a) outranks a PASS: an unconverged level -> NOT A RESULT",
              row_it["verdict"] == "NOT A RESULT" and
              row_it["band_verdict"] == "PASS")
        row_pl = grade_ladder("converging", conv, 2, (fine + 1.0, fine + 2.0),
                              pc, iterative_states=ok_state,
                              plateau_states={"c": "PLATEAUED", "m": "PLATEAUED",
                                              "f": "NOT_PLATEAUED"})
        check("step (a) outranks a GATE FAIL too -> NOT A RESULT",
              row_pl["verdict"] == "NOT A RESULT" and
              row_pl["band_verdict"] == "GATE FAIL")
        try:
            grade_ladder("converging", conv, 2, (fine - 1e-6, fine + 1e-6), pc)
            check("refuses when step (a) cannot be evaluated at all", False, "")
        except Refusal:
            check("refuses when step (a) cannot be evaluated at all", True)
        try:
            grade_ladder("converging", conv, 2, None, pc,
                         iterative_states=ok_state)
            check("refuses with no pre-registered band", False, "graded anyway")
        except Refusal:
            check("refuses with no pre-registered band", True)

        # never a GCI on a non-monotone triple, checked over the whole family
        leaked = []
        for tr in ((1.00, 1.02, 1.05), (1.00, 1.10, 1.05), (1.10, 1.04, 1.04),
                   (1.0, 1.03375, 1.06375)):
            g = gci_equal(*tr, 1.6, 2)
            if "GCI_pct" in g:
                leaked.append(tr)
        check("no GCI is ever emitted on a non-monotone or non-converging triple",
              not leaked, f"leaked {leaked}")

        # -- (vii) four levels: BOTH triples reported -------------------------
        print("(vii) a four-level ladder reports BOTH triples "
              "(T1b_L4_AMENDMENT section 2)")
        four = [dict(name=n, cells=c, value=v) for n, c, v in
                zip(("c", "m", "f", "x"), (2500, 6400, 16384, 41943),
                    (1.0402, 1.0121, 1.0043, 1.0016))]
        row4 = grade_ladder("four", four, 2, (0.0, 2.0), pc,
                            iterative_states={k: "CONVERGED"
                                              for k in ("c", "m", "f", "x")})
        check("two triples and two orders are printed",
              len(row4["triples"]) == 2 and len(row4["orders"]) == 2,
              f"orders {[round(o, 4) for o in row4['orders']]}, "
              f"states {row4['states']}")
        check("the FINEST triple is the one graded",
              row4["triples"][-1]["levels"] == ("m", "f", "x"))
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    n_ok = sum(1 for _, ok, _ in _CHECKS if ok)
    print(f"\n{n_ok}/{len(_CHECKS)} checks passed")
    return EXIT_OK if n_ok == len(_CHECKS) else EXIT_FAIL


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--series", help="JSON level series, coarse first")
    ap.add_argument("--dim", type=int, default=None,
                    help="REQUIRED with --series; 1, 2 or 3.  No default.")
    ap.add_argument("--band", help="lo,hi -- the PRE-REGISTERED band")
    ap.add_argument("--quantity", default=None)
    ap.add_argument("--reference", type=float, default=None)
    ap.add_argument("--form", default="auto",
                    choices=("auto", "equal", "unequal"))
    ap.add_argument("--iterative", default=None,
                    help="name=STATE,name=STATE for every level")
    ap.add_argument("--plateau", default=None)
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.series:
        ap.error("--series is required (or --selftest)")
    try:
        if args.dim is None:
            refuse("--dim is REQUIRED and has no default "
                   "(VERIFICATION_CHARTER.md 3.1 rule 1)")
        if not args.band:
            refuse("--band is REQUIRED; the band is pre-registered, never "
                   "invented at grade time")
        doc = read_series(args.series)
        if doc.get("dim") is not None and int(doc["dim"]) != args.dim:
            refuse(f"the series file states dim = {doc['dim']} and --dim says "
                   f"{args.dim}; a ladder is graded at ONE stated dimensionality")
        lo, hi = (float(x) for x in args.band.split(","))
        pc = planted_zero_control(args.series)
        states = None
        if args.iterative:
            states = dict(kv.split("=") for kv in args.iterative.split(","))
        plateau = None
        if args.plateau:
            plateau = dict(kv.split("=") for kv in args.plateau.split(","))
        row = grade_ladder(args.quantity or doc.get("quantity") or "unnamed",
                           doc["levels"], args.dim, (lo, hi), pc,
                           iterative_states=states, plateau_states=plateau,
                           form=args.form, reference=args.reference)
    except Refusal as exc:
        print(f"REFUSE: {exc}")
        return EXIT_REFUSE
    print(format_row(row))
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(row, fh, indent=2, sort_keys=True)
        print(f"    written: {os.path.abspath(args.json_out)}")
    return exit_code_for(row["verdict"])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
