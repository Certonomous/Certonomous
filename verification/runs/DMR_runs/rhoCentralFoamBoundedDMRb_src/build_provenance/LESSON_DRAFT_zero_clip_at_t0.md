# LESSON DRAFT — hand to the cfd supervisor (NOT committed to docs/LESSONS.md)

Numbering is assigned AT COMMIT from the tail (rule 11): re-derive with
`grep -oE '^## L-[0-9]+' docs/LESSONS.md | grep -oE '[0-9]+' | sort -n | tail -1`
and use max+1. At authoring (2026-09-08) the max existing was **505**, so the next
number is expected to be **L-506** — but RE-DERIVE at commit, do not trust this.

This draft is NOT committed to `docs/LESSONS.md` (numbering at commit; the supervisor
places it). It is kept here as a durable draft under the case directory (rule 13:
never the scratchpad as a handoff channel).

---

## L-<NEXT> A positivity-clip floor validated against a hand e-formula, not the solver's ACTUAL initial field, sits above the field and corrupts the run — enforce a t=0 zero-clip assertion

**Class.** A positivity-preserving solver that floors internal energy `e` (hence T)
with `e = min(max(e, eMin_bound), eMax_bound)` must derive `eMin_bound` from the
SOLVER'S OWN initial `e` field, not from a hand-assumed thermodynamic reference. If
the floor is calibrated against an assumed `Tref`/`eref` hand-formula
(`e = Cv·(T − Tref)`) instead of the energy representation the thermo actually uses,
the floor can sit ABOVE the entire physical field; the clip then fires on 100 % of
cells from the first timestep and energy-pumps the field — the run measures the
instrument defect, not the model (NOT A RESULT, no capability inference — L-501).

**Measured occurrence (DMR-R3 L5).** `rhoCentralFoamBoundedDMR` set
`eMin_bound = -532.410` from `e = Cv·(T − 298.15)` (assumed `Tref = 298.15`,
`eref = 0`), predicting ambient `e(T=1.0) = -530.626`. But OpenFOAM's ACTUAL `hConst
sensibleInternalEnergy` assigns ambient `e ≈ -743.589 J/kg`
(`e_actual(T) = Cv·T − Cp·Tref`, so at T=1.0: `1.785717 − 2.5·298.15 = -743.589`).
The floor sat ~211 J/kg ABOVE the field; the run reported a byte-identical
`worst e = -743.58928` at its first step across ALL THREE grids (a per-grid-invariant
worst-`e` is a thermo-reference constant, not a flow feature — the smoking gun) and
clipped 14400/57600/230400 = 100 % of cells. Verdict NOT A RESULT
(`DMR_R3_L5_BOUNDED_T_RESULTS.md`). Cost of the miss: the full 100-core-min L5 family
cap, spent on a corrupted field.

**The durable, enforced fix (two parts).**
1. **Anchor the floor on the ACTUAL initial field.** For a linear (hConst) inversion,
   `eMin_bound = e_min_initial − Cv·(T_min_initial − TMin)` with `e_min_initial`,
   `T_min_initial` the MEASURED global minima (`gMin`) of the initial `e`/`T` fields —
   no assumed reference. The floor then sits `Cv·(T_min_initial − TMin)` BELOW the
   coldest physical cell BY CONSTRUCTION.
2. **A t=0 zero-clip STARTUP ASSERTION** (plant-the-zero, in the solver): on the
   physical initial field, count cells with `e < eMin_bound` (reduced across ranks);
   if `> 0`, `FatalError` + non-zero exit. A correctly-calibrated positivity floor is
   INERT at t=0 by construction; the assertion catches ANY miscalibration — including a
   hand-formula floor above the field — before a core-minute is spent. It would have
   caught L5 at t=0.

**Corrected rung (DMR-R3 L5b).** `rhoCentralFoamBoundedDMRb`
(`verification/runs/DMR_runs/rhoCentralFoamBoundedDMRb_src/`) implements both. VERIFIED
against the ACTUAL R3 (N=240) field: `eMin_bound = -745.35714` (anchored on measured
`e_min = -743.58928`), STARTUP ASSERT PASS — 0 cells clip at t=0
(`build_provenance/t0_assertion_probe_R3.txt`).

**Enforcement instrument.** `scripts/check_zero_clip_at_t0.py` (planted-control
`--selftest`) — a static pre-freeze check that REFUSES (exit 3) when a solver defines
and uses a low positivity clip bound but carries NO t=0 zero-clip startup assertion.
Confirmed: REFUSES the original L5 `createFields.H`+`boundE.H`, PASSES the corrected
L5b source. Run it on any positivity-clip solver's source before freeze.

**Wider applicability.** The same trap exists wherever a bound is calibrated against a
recalled/assumed reference rather than the field the solver actually holds — e.g. the
F4 SWBLI `rhoCentralFoamBounded` bakes `Cv = 717.30` (dimensional), which is wrong for
the DMR nondimensional thermo by ~400×. Anchor bounds on measured field state; make
the calibration self-verifying with a t=0 assertion.
