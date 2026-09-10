#!/usr/bin/env python3
"""M6 grid-(b) MEMORY PRE-FLIGHT GUARD.

WHY THIS EXISTS
---------------
The family-(II) `Lf` build is projected to peak near enough to this box's TOTAL RAM that a
build started on a loaded box does not fail fast -- it pages, thrashes, and either takes
hours or gets a peer solver OOM-killed.  This guard REFUSES to let the build start unless
MemAvailable, read from the kernel at the moment of the call, exceeds a threshold sized from
the MEASURED per-cell cost with a DERIVED margin.

TWO RULES THIS FILE OBEYS, DELIBERATELY
---------------------------------------
1. **`if ...: refuse(...)`, NEVER `assert`.**  `python3 -O` compiles `assert` out, which
   silently turns a guard into an offer (L-332).  Every refusal below is an explicit `if`
   raising `PreflightRefusal`.  `--selftest` PROVES the refusal fires under `-O`.
2. **Fail closed.**  A meminfo the guard cannot parse is a REFUSAL, not a pass.  A reader that
   cannot see a planted low MemAvailable is a REFUSAL (rule 3, planted-zero control): the
   selftest plants a synthetic meminfo and requires the guard to SEE it.

THE THRESHOLD IS DERIVED, NOT CHOSEN.  See `derive_requirement()`; every factor cites a
measured artifact and is printed by `--explain`.
"""
from __future__ import annotations

import argparse
import os
import sys

GiB = 1024 ** 3
REFUSE_EXIT = 2

# --------------------------------------------------------------------------------------
# MEASURED INPUTS.  Each constant names the artifact it came from.  None of these is a
# guess; changing one without changing its artifact is a defect.
# --------------------------------------------------------------------------------------

# verification/runs/M6_LE_RESOLVED_runs/Lc/work/MEM_plot3dToFoam_Lc.txt
LC_CELLS, LC_VMHWM_KB = 936_000, 781_832
LC_CGROUP_PEAK_BYTES = 782_483_456          # Lc/solve/MEM_cgroup_after_Lc.txt
# verification/runs/M6_LE_RESOLVED_runs/Lm/work/MEM_plot3dToFoam_Lm.txt
LM_CELLS, LM_VMHWM_KB = 7_488_000, 6_046_384
LM_CGROUP_PEAK_BYTES = 6_678_343_680        # Lm/solve/MEM_cgroup_after_Lm.txt

# Family (II) Lf, surface-only, fixed ~150 wall-normal layers.
# 228,544 surface faces (Lf_recluster/work/RECLUSTER_Lf.json: surface_faces_all9) x 150.
LF_II_SURFACE_FACES = 228_544
LF_II_LAYERS = 150
LF_II_CELLS = LF_II_SURFACE_FACES * LF_II_LAYERS          # 34,281,600

# Stage uplift: peak of the HEAVIEST MEASURED chain stage over the plot3dToFoam stage, at the
# same cell count.  Artifact: Lm/solve/MEM_STAGES_Lm.txt.  checkMesh was MEASURED at 645.11
# B/cell on the same 7,488,000-cell mesh = 0.780 x plot3dToFoam, so plot3dToFoam is the heavier
# of the two stages measured and the uplift is 1.000 ON A MEASURED BASIS.
# STILL UNMEASURED and disclosed, not waved: autoPatch, createPatch, renumberMesh.
STAGE_UPLIFT = 1.0
STAGE_UPLIFT_BASIS = "checkMesh measured 0.780x plot3dToFoam; 2 of 5 stages measured"

# The box's NON-DRAINING footprint, measured 2026-09-10 05:07Z by summing /proc/<pid>/status
# RssAnon over every process and subtracting the CFD solves that WOULD exit on a drain, plus the
# kernel's unreclaimable slab + kernel stacks + page tables.  This is what MemAvailable can
# never rise above being short of, so it fixes the CEILING a drained box can offer.
NONDRAINING_ANON_BYTES = int(1.19 * GiB)
KERNEL_UNRECLAIMABLE_BYTES = int(0.38 * GiB)


class PreflightRefusal(RuntimeError):
    """Raised INSTEAD OF proceeding.  Never caught inside this module."""


def refuse(msg: str) -> "None":
    raise PreflightRefusal(msg)


# --------------------------------------------------------------------------------------
# READER
# --------------------------------------------------------------------------------------

def read_meminfo(path: str = "/proc/meminfo") -> "dict[str, int]":
    """Parse a meminfo into {key: bytes}.  Fails CLOSED on anything it cannot read."""
    try:
        with open(path, "r") as fh:
            text = fh.read()
    except OSError as exc:
        refuse(f"MEMORY PRE-FLIGHT REFUSED: cannot read meminfo at {path!r}: {exc}")
    out = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        parts = rest.split()
        if not parts:
            continue
        try:
            val = int(parts[0])
        except ValueError:
            continue
        unit = parts[1].lower() if len(parts) > 1 else "kb"
        if unit == "kb":
            val *= 1024
        elif unit not in ("b", ""):
            continue
        out[key.strip()] = val
    for need in ("MemTotal", "MemAvailable"):
        if need not in out:
            refuse(f"MEMORY PRE-FLIGHT REFUSED: {need} absent from {path!r} -- "
                   f"a reader that cannot see the field must not pass the build.")
    return out


# --------------------------------------------------------------------------------------
# DERIVATION
# --------------------------------------------------------------------------------------

def derive_requirement(cells: int = LF_II_CELLS) -> "dict":
    """Derive the required MemAvailable from the two MEASURED points.  All arithmetic here;
    no round numbers are chosen anywhere."""
    r_lc = LC_VMHWM_KB * 1024 / LC_CELLS
    r_lm = LM_VMHWM_KB * 1024 / LM_CELLS
    r_marginal = (LM_VMHWM_KB - LC_VMHWM_KB) * 1024 / (LM_CELLS - LC_CELLS)
    r_max = max(r_lc, r_lm)

    # (1) BASIS: the largest MEASURED per-cell rate, not the mean and not the marginal.
    #     The rate FALLS with size across the two measured points (855.34 -> 826.86 B/cell), so
    #     taking the SMALLER mesh's rate is deliberately conservative.  It is an uplift of
    #     r_max / r_marginal over the trend the two points actually establish.
    basis_bytes = r_max * cells
    f_basis = r_max / r_marginal

    # (2) EXTRAPOLATION ALLOWANCE.  The target sits 4.58x beyond the largest measured point.
    #     Nothing measures the rate there.  The allowance is the OBSERVED SCATTER between the
    #     two measured rates, r_lc / r_lm, applied once and one-sided.  It is a measured
    #     spread, not a chosen round number.
    f_extrap = r_lc / r_lm

    # (3) STAGE UPLIFT: heaviest MEASURED chain stage / plot3dToFoam at equal cells.
    f_stage = STAGE_UPLIFT

    # (4) PAGE CACHE IS OBSERVED AND DELIBERATELY *NOT* CHARGED AS A MULTIPLIER.  The cgroup
    #     peak exceeded VmHWM by this factor at Lm, but that excess is page cache, which the
    #     kernel already counts as reclaimable INSIDE MemAvailable.  Multiplying a MemAvailable
    #     requirement by it double-charges the same bytes; an earlier draft of this guard did
    #     exactly that and produced a 29.46 GiB requirement no drained box could ever meet.
    #     Reported, not charged.
    f_cgroup_observed = LM_CGROUP_PEAK_BYTES / (LM_VMHWM_KB * 1024)

    required = basis_bytes * f_extrap * f_stage

    # The CEILING a fully drained box can offer: MemTotal minus what never drains.
    drained_ceiling = None  # filled by preflight(), which has MemTotal in hand

    return {
        "cells": cells,
        "r_lc_B_per_cell": r_lc,
        "r_lm_B_per_cell": r_lm,
        "r_marginal_B_per_cell": r_marginal,
        "r_max_B_per_cell": r_max,
        "projected_vmhwm_bytes": r_lm * cells,      # the headline projection (Lm ratio)
        "basis_bytes": basis_bytes,
        "f_basis_vs_marginal": f_basis,
        "f_extrap": f_extrap,
        "f_cgroup_observed_not_charged": f_cgroup_observed,
        "f_stage": f_stage,
        "f_stage_basis": STAGE_UPLIFT_BASIS,
        "required_bytes": required,
        "extrapolation_factor_beyond_largest_measured": cells / LM_CELLS,
    }


def explain(d: "dict") -> str:
    L = []
    A = L.append
    A("M6 GRID-(b) MEMORY PRE-FLIGHT -- THRESHOLD DERIVATION (every factor from an artifact)")
    A(f"  target cells                        : {d['cells']:,}"
      f"  (= {LF_II_SURFACE_FACES:,} faces x {LF_II_LAYERS} layers, family II)")
    A(f"  measured Lc rate                    : {d['r_lc_B_per_cell']:.2f} B/cell"
      f"  ({LC_VMHWM_KB:,} kB / {LC_CELLS:,} cells)")
    A(f"  measured Lm rate                    : {d['r_lm_B_per_cell']:.2f} B/cell"
      f"  ({LM_VMHWM_KB:,} kB / {LM_CELLS:,} cells)")
    A(f"  2-point marginal rate               : {d['r_marginal_B_per_cell']:.2f} B/cell")
    A(f"  HEADLINE projection (Lm rate)       : {d['projected_vmhwm_bytes']/GiB:.2f} GiB")
    A(f"  basis = max measured rate x cells   : {d['basis_bytes']/GiB:.2f} GiB"
      f"   (f_basis vs marginal = {d['f_basis_vs_marginal']:.4f})")
    A(f"  x f_extrap (measured rate scatter)  : {d['f_extrap']:.4f}")
    A(f"  x f_stage  ({d['f_stage_basis']})   : {d['f_stage']:.4f}")
    A(f"  ==> REQUIRED MemAvailable           : {d['required_bytes']/GiB:.2f} GiB")
    A(f"  OBSERVED but NOT CHARGED: cgroup/VmHWM = {d['f_cgroup_observed_not_charged']:.4f}"
      " (page cache; already inside MemAvailable)")
    ceiling = (32_132_596 * 1024) - NONDRAINING_ANON_BYTES - KERNEL_UNRECLAIMABLE_BYTES
    A(f"  measured DRAINED-BOX CEILING        : {ceiling/GiB:.2f} GiB"
      f"   (MemTotal 30.64 - non-draining 1.19 - kernel unreclaimable 0.38)")
    A(f"  MARGIN when drained                 : {(ceiling - d['required_bytes'])/GiB:+.2f} GiB")
    A(f"  INFERRED, NOT MEASURED: the target is {d['extrapolation_factor_beyond_largest_measured']:.2f}x")
    A( "    beyond the largest measured point; the per-cell rate is assumed to keep its")
    A( "    measured trend out to that size.  It has not been measured there.")
    return "\n".join(L)


# --------------------------------------------------------------------------------------
# THE GUARD
# --------------------------------------------------------------------------------------

def preflight(cells: int = LF_II_CELLS,
              meminfo_path: str = "/proc/meminfo",
              require_bytes: "float | None" = None,
              quiet: bool = False) -> "dict":
    """REFUSE unless MemAvailable exceeds the derived requirement.

    Returns the reading on success.  Raises PreflightRefusal otherwise.  There is no
    'proceed anyway' path in this function and there must never be one."""
    d = derive_requirement(cells)
    need = d["required_bytes"] if require_bytes is None else float(require_bytes)
    mem = read_meminfo(meminfo_path)
    avail = mem["MemAvailable"]
    total = mem["MemTotal"]
    swap_total = mem.get("SwapTotal", 0)

    # -- explicit ifs.  NEVER assert: `python3 -O` deletes asserts (L-332). --
    if need <= 0:
        refuse("MEMORY PRE-FLIGHT REFUSED: requirement derived as non-positive "
               f"({need} B) -- a zero requirement is a broken derivation, not a green light.")
    if total < need:
        refuse(
            "MEMORY PRE-FLIGHT REFUSED: NOT BUILDABLE ON THIS MACHINE.\n"
            f"  required peak : {need/GiB:.2f} GiB  ({cells:,} cells)\n"
            f"  MemTotal      : {total/GiB:.2f} GiB\n"
            f"  SwapTotal     : {swap_total/GiB:.2f} GiB (NOT counted: a {need/GiB:.0f} GiB "
            "working set paging to swap thrashes; swap is not headroom)\n"
            "  This is a CAPACITY finding, not a scheduling one.  Draining the box cannot fix it.")
    ceiling = total - NONDRAINING_ANON_BYTES - KERNEL_UNRECLAIMABLE_BYTES
    if need > ceiling:
        refuse(
            "MEMORY PRE-FLIGHT REFUSED: NOT REACHABLE EVEN ON A FULLY DRAINED BOX.\n"
            f"  required peak          : {need/GiB:.2f} GiB  ({cells:,} cells)\n"
            f"  MemTotal               : {total/GiB:.2f} GiB\n"
            f"  never-draining anon    : {NONDRAINING_ANON_BYTES/GiB:.2f} GiB (measured "
            "2026-09-10 05:07Z, /proc RssAnon less the CFD solves)\n"
            f"  kernel unreclaimable   : {KERNEL_UNRECLAIMABLE_BYTES/GiB:.2f} GiB\n"
            f"  DRAINED-BOX CEILING    : {ceiling/GiB:.2f} GiB\n"
            f"  SHORT BY               : {(need-ceiling)/GiB:.2f} GiB\n"
            "  Killing every peer solver would still not free enough.  This is a CAPACITY "
            "finding; do not wait for a drain that cannot help.")

    if avail < need:
        refuse(
            "MEMORY PRE-FLIGHT REFUSED: BOX NOT DRAINED.\n"
            f"  MEASURED  MemAvailable : {avail/GiB:.2f} GiB   (read from {meminfo_path})\n"
            f"  REQUIRED  MemAvailable : {need/GiB:.2f} GiB\n"
            f"  SHORT BY               : {(need-avail)/GiB:.2f} GiB\n"
            f"  MemTotal               : {total/GiB:.2f} GiB -- the build FITS this machine "
            "when drained; it does not fit it right now.\n"
            "  Starting anyway would page against peer solvers.  Wait for the box to drain; "
            "do NOT lower the requirement to make this pass.")

    if not quiet:
        print(f"MEMORY PRE-FLIGHT PASS: MemAvailable {avail/GiB:.2f} GiB "
              f">= required {need/GiB:.2f} GiB (MemTotal {total/GiB:.2f} GiB, "
              f"{cells:,} cells); headroom {(avail-need)/GiB:+.2f} GiB, "
              f"drained-box ceiling {ceiling/GiB:.2f} GiB")
    return {"MemAvailable_bytes": avail, "MemTotal_bytes": total,
            "required_bytes": need, "derivation": d}


# --------------------------------------------------------------------------------------
# PLANTED-FAILURE SELFTEST -- both arms, and it must fire under `python3 -O` too.
# --------------------------------------------------------------------------------------

_SYNTH = ("MemTotal:       {total} kB\n"
          "MemFree:          123456 kB\n"
          "MemAvailable:   {avail} kB\n"
          "SwapTotal:      16777212 kB\n"
          "SwapFree:       16691952 kB\n")


def _write_synth(path: str, total_kb: int, avail_kb: int) -> str:
    with open(path, "w") as fh:
        fh.write(_SYNTH.format(total=total_kb, avail=avail_kb))
    return path


def selftest(tmpdir: str) -> int:
    """Prove the guard REFUSES and PASSES against PLANTED readings.  A guard only ever shown
    passing is not shown to work."""
    opt = "ON (-O: asserts deleted)" if not __debug__ else "off (plain python3)"
    print(f"--- mem_preflight_guard selftest, optimisation {opt} ---")
    d = derive_requirement()
    need_gib = d["required_bytes"] / GiB
    fails = 0

    # ARM 1 -- PLANTED LOADED BOX.  MemAvailable planted 1 GiB BELOW the requirement.
    lo = _write_synth(os.path.join(tmpdir, "meminfo_loaded"),
                      total_kb=32_132_596,
                      avail_kb=int((d["required_bytes"] - GiB) / 1024))
    try:
        preflight(meminfo_path=lo, quiet=True)
        print("  ARM 1 (planted loaded box)      : FAIL -- guard PASSED a reading it must refuse")
        fails += 1
    except PreflightRefusal as exc:
        first = str(exc).splitlines()[0]
        print(f"  ARM 1 (planted loaded box)      : REFUSED as required -- {first}")

    # ARM 2 -- PLANTED DRAINED BOX.  MemAvailable planted 1 GiB ABOVE the requirement.
    hi = _write_synth(os.path.join(tmpdir, "meminfo_drained"),
                      total_kb=32_132_596,
                      avail_kb=int((d["required_bytes"] + GiB) / 1024))
    try:
        preflight(meminfo_path=hi, quiet=True)
        print(f"  ARM 2 (planted drained box)     : PASSED as required "
              f"(planted {need_gib + 1:.2f} GiB vs required {need_gib:.2f} GiB)")
    except PreflightRefusal as exc:
        print(f"  ARM 2 (planted drained box)     : FAIL -- guard refused a reading it must "
              f"pass -- {str(exc).splitlines()[0]}")
        fails += 1

    # ARM 3 -- PLANTED SMALL MACHINE.  MemTotal below the requirement: capacity, not drain.
    sm = _write_synth(os.path.join(tmpdir, "meminfo_small"),
                      total_kb=int((d["required_bytes"] - GiB) / 1024),
                      avail_kb=int((d["required_bytes"] - 2 * GiB) / 1024))
    try:
        preflight(meminfo_path=sm, quiet=True)
        print("  ARM 3 (planted small machine)   : FAIL -- guard PASSED a machine too small")
        fails += 1
    except PreflightRefusal as exc:
        if "NOT BUILDABLE ON THIS MACHINE" in str(exc):
            print("  ARM 3 (planted small machine)   : REFUSED as required (capacity branch)")
        else:
            print("  ARM 3 (planted small machine)   : FAIL -- refused via the WRONG branch")
            fails += 1

    # ARM 4 -- BLIND READER.  MemAvailable REMOVED.  A reader that cannot see the field must
    # refuse, never pass by default (rule 3 in guard form).
    blind = os.path.join(tmpdir, "meminfo_blind")
    with open(blind, "w") as fh:
        fh.write("MemTotal:       32132596 kB\nMemFree:          123456 kB\n")
    try:
        preflight(meminfo_path=blind, quiet=True)
        print("  ARM 4 (blind reader, no field)  : FAIL -- guard PASSED with no MemAvailable")
        fails += 1
    except PreflightRefusal:
        print("  ARM 4 (blind reader, no field)  : REFUSED as required (fails closed)")

    # ARM 5 -- family (I) Lf, 137,126,400 cells: must refuse on CAPACITY against real /proc.
    try:
        preflight(cells=137_126_400, quiet=True)
        print("  ARM 5 (family I Lf, real /proc) : FAIL -- guard PASSED 137.1M cells")
        fails += 1
    except PreflightRefusal as exc:
        if "NOT BUILDABLE ON THIS MACHINE" in str(exc):
            print("  ARM 5 (family I Lf, real /proc) : REFUSED as required (capacity branch)")
        else:
            print("  ARM 5 (family I Lf, real /proc) : refused, but via the drain branch "
                  "-- report: " + str(exc).splitlines()[0])
    print(f"--- selftest {'PASS' if fails == 0 else 'FAIL'}: {fails} arm(s) wrong ---")
    return 0 if fails == 0 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cells", type=int, default=LF_II_CELLS,
                    help="cell count of the build about to start (default: family II Lf)")
    ap.add_argument("--meminfo", default="/proc/meminfo")
    ap.add_argument("--require-gib", type=float, default=None,
                    help="OVERRIDE the derived requirement (selftest/planted use only)")
    ap.add_argument("--explain", action="store_true", help="print the threshold derivation")
    ap.add_argument("--selftest", metavar="TMPDIR", default=None,
                    help="run the planted-failure selftest in TMPDIR")
    a = ap.parse_args(argv)

    if a.selftest:
        os.makedirs(a.selftest, exist_ok=True)
        return selftest(a.selftest)
    if a.explain:
        print(explain(derive_requirement(a.cells)))
    try:
        preflight(cells=a.cells, meminfo_path=a.meminfo,
                  require_bytes=None if a.require_gib is None else a.require_gib * GiB)
    except PreflightRefusal as exc:
        sys.stderr.write(str(exc) + "\n")
        return REFUSE_EXIT
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
