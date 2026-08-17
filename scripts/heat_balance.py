#!/usr/bin/env python3
"""heat_balance.py -- watts in against watts out, for any OpenFOAM thermal solve.

    python3 scripts/heat_balance.py <case> [--time latestTime] [--tol 1.0]
                                   [--length 0.1] [--json out.json] [--quiet]

Exit 0 = balance closed within --tol percent.  Exit 1 = it did not.
Exit 2 = the auditor REFUSED to produce a number (see REFUSALS below).

WHY THIS EXISTS
---------------
Built at rung K0b of the thermal ladder and made a standing check from that
point on: no thermal number leaves this lab without its boundary heat balance
and its regime numbers attached.  A residual plot says the linear solver stopped
moving.  It does not say energy is conserved.  Those are different claims and
this lab has confused them before.

WHAT IT COMPUTES, AND HOW IT IS DERIVED
---------------------------------------
For a Boussinesq solve the temperature equation is

    div(phi, T) - laplacian(alphaEff, T) = 0,     alphaEff = nu/Pr + nut/Prt

which is a KINEMATIC equation: it never sees rho or cp.  To turn it into watts:

    q  = -rho.cp.alphaEff.grad(T)              [W/m^2]
    Q_into_domain_through_patch_p
       = -integral_p (q . n) dA                 (n = OUTWARD unit normal)
       = +rho.cp.alphaEff . integral_p (n . grad(T)) dA

The surface integral is obtained exactly, not by a finite-difference of my own:
`fvc::grad` overwrites the wall-normal component of its boundary field with the
scheme's own `snGrad` (OpenFOAM's `gaussGrad::correctBoundaryConditions`), so
`areaNormalIntegrate` of `grad(T)` over a patch IS `integral snGrad(T) dA`, in
the discretisation the solver actually used.  Nothing here re-implements the
solver's numerics, which is the whole point.

  TRAP, MEASURED, DO NOT REMOVE THE WORKAROUND.  `grad(T)` must be recomputed
  in the SAME postProcess pass as the surface integral.  If it is written to
  disk first and read back (`postProcess -func <sfv> -fields '(grad(T))'`), the
  wall boundary values come back WITHOUT the snGrad correction and the answer
  is silently wrong.  Measured on the K0a case at 2000 iterations:
      recomputed in-pass  : integral n.grad(T) dA = 0.595629494
      read back from disk : integral n.grad(T) dA = 0.377856775   (-36.6%)
  The in-pass value is the correct one: it reproduces a by-hand
  (T_wall - T_cell)/d summation over the raw T field to 7 significant figures.
  Hence the single `run_post` call with `grad(T)` first in the funcs list.

Note rho.cp.alpha = rho.cp.(nu/Pr) = k, the thermal conductivity, so the
laminar coefficient is just k and the script prints it for cross-checking
against a tabulated value.

At steady state with no volumetric source, sum over all boundary patches of
Q_into_domain must be zero.  The reported imbalance is

    imbalance% = 100 . |sum_p Q_p| / (sum over patches with Q_p > 0 of Q_p)

i.e. the net leak as a percentage of the total heat actually entering.

WHAT A PASSING CLOSURE NUMBER IS NOT -- READ THIS BEFORE QUOTING ONE
--------------------------------------------------------------------
On a SEALED, IMPERMEABLE, STEADY case this balance is very nearly an IDENTITY.
The discrete temperature equation is solved to a tight linear tolerance at every
outer iteration; `div(phi,T)` integrates to zero over the domain because `phi`
is conservative and no wall passes mass; so the boundary conduction terms are
forced to sum to zero AT EVERY ITERATION, CONVERGED OR NOT.  K0b pre-registered
"imbalance above 20 percent on an early, unconverged snapshot" and measured
0.0128 percent at iteration 10, never above 0.13 percent at any iteration.

So a number at or below `--tol` on a sealed case is NOT evidence that the
physics is right.  A quantity derivable by construction is an identity and per
W-2 cannot gate anything.  This script therefore STAMPS such a report:
`closure_is_identity_class` in the JSON and a line in the printed output.  The
stamp is not a warning about this script; it is a warning about the sentence a
reader is about to write.

What the check IS still worth, narrowly: wrong fluid properties, wrong patch
areas, a wrong sign convention, a patch omitted from the sum, any unaccounted
energy source or sink, and any domain with through-flow -- where the advective
enthalpy flux is a genuinely independent contribution and the balance is not an
identity at all.

THE ADVECTIVE PATH: WHAT IT WAS, AND THE DEFECT THAT MADE IT WORSE THAN MISSING
-------------------------------------------------------------------------------
Recorded here because the shape of this defect is more instructive than the
missing feature, and because the next person to add a flag needs to see it.

Until rung KV1 this script had a `--allow-advective` flag that read at EXACTLY
ONE place -- the exit-2 refusal guard -- and nowhere else.  The only per-patch
heat it ever computed was `Q = kcond * G`, pure conduction.  No advective key
reached the JSON and no advective line reached the printed report.  So the flag
did not "add an UNVALIDATED term"; it added NOTHING, and the docstring's claim
that it did was false in both halves.

THAT IS NOT THE WORST OF IT.  `sealed = not nonwall`, so an open case took the
`closure_is_identity_class is False` branch of the report and printed

    "NOT of the identity class, so the balance is a genuine constraint here
     rather than a restatement of the discretisation"

over a ledger whose advective term HAD NEVER BEEN COMPUTED.  The instrument made
a positive claim about the STRENGTH OF ITS OWN CHECK on exactly the case where
the quantity backing that claim did not exist.  A missing feature is a gap a
reader can see.  A missing feature under a printed assurance that the check is
strong here is a gap that reads as a result, and any figure quoted on top of it
inherits the assurance without the quantity.  That is the lesson (L-105) and it
is why the stamp was repaired BEFORE the term was implemented, in its own
commit, rather than after.

THE LEDGER IS NOW COMPLETE OR IT SAYS SO.  Every report carries
`advective.state` and `advective.ledger_complete`.  An incomplete ledger CANNOT
PASS -- `passed` is false whatever the imbalance reads -- and it cannot be
stamped as a genuine constraint either: `closure_is_identity_class` goes to
`null`/UNKNOWN, because a balance missing a term is neither an identity nor a
constraint, it is an unfinished sum.

WHAT IS COMPUTED NOW, AND AGAINST WHAT
--------------------------------------
On every active patch of a case that has a non-wall patch:

    Q_adv_into_domain_p = -rho.cp . integral_p (T - datum) (U.n) dA

summed into the SAME ledger as the conductive term, so `Q_in_W` on a patch is
conduction plus advection and `Q_net_W` is the whole boundary.

  * The integral is `integral_p T phi_f` read from `surfaceFieldValue` with
    `operation weightedSum`, `fields (phi)`, `weightField T`.  That is
    `gSum(T_f . phi_f)` over the patch faces against the SOLVER'S OWN
    conservative face flux, not a geometric `Sf & U_f` this script builds
    itself -- `div(phi,T)` is the term the solver assembled and reproducing it
    rather than inventing a second one is this file's standing rule.  For a
    volScalarField on a patch OpenFOAM's `filterField` returns the BOUNDARY
    field, so `T_f` is the same face value the convection term saw.  No `phi`
    on disk at the audited time is a REFUSAL, never a fallback to U.

  * THE DATUM IS THE CASE'S OWN `TRef`, NOT 0 K, AND THAT IS A GATE DECISION
    RATHER THAN A CONVENIENCE.  The NET is datum-free when mass balances, but
    the DENOMINATOR of the imbalance ratio is not: the datum decides how much
    of the through-flow's absolute enthalpy is counted as "heat entering".  A
    0 K datum adds `rho.cp.TRef.mdot` to that denominator -- on this lab's air
    at 300 K, hundreds of times the heat traffic actually being audited -- so
    the same 0.5 percent tolerance would become a vastly LOOSER gate wearing
    an unchanged number.  MEASURED at KV1 by mutation M4 on the KV1c duct: the
    denominator is 8.979442 W at a 0 K datum against 0.2079685 W at TRef, a
    factor of 43.2, so the 0.5 percent band is 4.49e-02 W of slack instead of
    1.04e-03 W.  M4 is also the one advective error the CLOSURE TEST CANNOT
    CATCH -- the datum cancels from the net when mass balances, so the case
    still passes -- which is exactly why the datum is fixed here in code and
    stated, rather than left to a caller to choose.

  * MASS IS CHECKED, NOT ASSUMED.  Shifting the datum by dT moves the ledger by
    `rho.cp.dT.(net volumetric flux)`, so the enthalpy number is only
    meaningful to the extent the boundary conserves mass.  The mass ledger is
    reported (`advective.mass_flux_*`, `mass_imbalance_pct`) and GATED against
    the same governed `--tol`: a case whose mass does not balance has
    `ledger_complete: false` and CANNOT PASS.  `datum_sensitivity_W_per_K`
    states what one kelvin of datum error is worth so a reader can compare it
    against the net directly.

  * THE SILENT-FALLBACK GUARD.  `surfaceFieldValue` returns the UNWEIGHTED sum,
    without a word on stderr, when `canWeight()` is false.  The advective term
    would then be ~`datum` times too small and nothing would say so.  So the
    invariant is checked: `integral T phi / integral phi` is a flux-weighted
    mean face temperature and must lie inside the field's own T range.  If the
    weight was dropped that ratio is exactly 1.0, and the auditor REFUSES.

WHAT THE OPEN-CASE CLOSURE IS WORTH -- CARRIED FROM K2a SECTION 8, NOT REDERIVED
-------------------------------------------------------------------------------
It DOES establish: an unconverged energy field, a mis-set temperature offset, a
flow-rate mismatch between a face pair, a patch omitted from the ledger.  Unlike
the sealed closure it is convergence-sensitive, because the advective term
depends on the SOLUTION -- on the outlet temperature and on `phi` -- and the
discretisation does not force it.  MEASURED at KV1 on the KV1c duct, the same
case audited at eleven iteration counts: 20.881 percent at iteration 20, 0.593
at 80, 0.0009 at 120, and 0.000000 percent (net +1.967e-11 W) at 201, tracking
the T equation's own initial residual from 8.01e-03 to 4.35e-12.  Set that
beside K0b's SEALED case, which read 0.0128 percent at iteration 10 and never
rose above 0.13 percent at any iteration: the open-case number crosses the 0.5
percent gate between iteration 80 and 100, and the sealed one never approaches
it.  One of the two is measuring the solution.

And it can FAIL, which was checked rather than hoped: `KV1_runs/
mutate_advective.py` puts four independent wrongnesses into the advective term
and re-audits the same field set.  Sign flipped -> 45.66 percent.  Scaled by
two -> 17.44 percent.  One open patch dropped from the sum -> 100 percent.  The
weight silently dropped -> REFUSED by the guard above.  All eleven sealed K0c
reports are byte-identical under every one of the four.

It does NOT establish CIRCULATION.  A solve with the flow structure entirely
wrong -- supply short-circuiting to the return, reversed aisle recirculation --
still closes perfectly once converged, because closure tests conservation and
not WHERE the energy travelled.  Closure is NECESSARY, NEVER SUFFICIENT, and no
K2b figure may cite it as validation evidence.

And the part that IS a measurement: the RECOVERY of a planted volumetric source
is convergence-sensitive, unlike the sealed-case closure.  Measured at K1c on
one case at eight iteration counts against a +5.000000000e-03 W plant, the
recovery error falls from -24.139 percent at iteration 100 to +2.3876e-09
percent at iteration 4000, tracking the T equation's own initial residual across
SEVEN decades.  Set that beside K0b's sealed no-source case, which read 0.0128
percent at iteration 10 and never rose above 0.13 percent at any iteration: one
of these two is measuring the solution and the other is measuring the
discretisation.  The full table is in docs/physics_rules.yaml, block `thermal`.

WHEN THE IMBALANCE RATIO IS UNDEFINED (proposal P1, closed 2026-08-17 at K1c)
-----------------------------------------------------------------------------
The denominator is the heat actually ENTERING.  On a case whose every patch
carries heat OUT -- which is exactly what a planted volumetric source produces
-- there is no such heat and the ratio has no denominator.  Two things follow,
and the second is the reason P1 was closed by REFUSING it rather than by
adopting it.

  1. The ratio is reported as UNDEFINED, with a named reason and with the watts
     stated, and the case FAILS.  It used to print a bare `nan`, which failed
     safe -- `nan` loses its own comparison -- but told the reader nothing about
     why.  A verdict nobody can act on is a verdict that gets ignored.

  2. P1 PROPOSED normalising by `max(sum(Q>0), |sum(Q<0)|)` to "give C3 a real
     percentage instead of nan".  That is REJECTED.  With no inward patch,
     `sum(Q<0)` IS the net, so the proposed ratio is |net|/|net| = 1 EXACTLY --
     100.0000 percent for every such case, whatever the source size, forever.
     It is another identity, and trading an honest refusal for a number that
     looks like a measurement is a straight loss.  This is not a prediction:
     the MIRROR case already does it.  Plant a SINK instead of a source, so that
     every patch carries heat IN and `Q_out` is zero, and the existing
     denominator prints exactly `100.0000 %` -- measured at K1c on
     KC2_sink_5mW.  The arithmetic is symmetric and so is the emptiness.

  A related failure the same measurement turned up, and the reason the test is
  on the RATIO and not merely on `Q_in == 0`: at intermediate iterations of the
  same planted case one adiabatic patch carried +1.63e-22 W of pure
  floating-point residue, so `Q_in > 0` was TRUE and the reported imbalance was
  3.07e+21 percent.  A denominator of residue is not a denominator.  The ratio
  is therefore declared undefined whenever `Q_in <= 0` OR `Q_in < |Q_net|`: if
  the leak is larger than all the heat entering, the quotient is not "a
  percentage of the heat entering" in any sense a reader can use.

  THIS IS NOT MORE PERMISSIVE, AND THAT IS PROVABLE RATHER THAN ASSERTED.  A
  case that passed before satisfies `100.|Q_net|/Q_in <= tol` with `tol` well
  under 100, hence `|Q_net| < Q_in`, hence the ratio is DEFINED and the verdict
  is byte-identical.  Every previously passing case still passes and every
  previously failing case still fails; only the words change on the cases that
  had no number to begin with.  Re-audited at K1c across all eleven committed
  K0c cases plus five controls; the diff on every pre-existing JSON key is
  empty.

REFUSALS -- what this script will NOT guess at
----------------------------------------------
It exits 2, loudly, rather than print a wrong number, when:

  * a non-wall, non-empty patch exists (inlet/outlet).  Those carry an
    ADVECTIVE enthalpy flux rho.cp.integral(T (U.n))dA, and a balance that
    silently omits it would be wrong by whatever the through-flow carries.
    `--allow-advective` suppresses this refusal and the term IS computed, from
    rung KV1 onward, and validated there against a planted source.  The refusal
    is KEPT rather than dropped because the flag is also where a reader is told
    what an open-case closure does and does not establish -- see "WHAT THE
    OPEN-CASE CLOSURE IS WORTH" below.  Removing the gate would make this
    checker more permissive, which is not a thing this rung is allowed to do.
    (Before KV1 the flag added NOTHING; the sentence that used to stand here --
    "`--allow-advective` adds the term but the report is then stamped
    UNVALIDATED" -- was false in both halves.  See "THE ADVECTIVE PATH".)
  * alphat is non-zero anywhere, i.e. a turbulence model is contributing
    turbulent thermal diffusivity.  Then alphaEff varies over the patch and
    `alphaEff . integral(n.grad T) dA` is NOT `integral(alphaEff n.grad T) dA`.
    `--allow-turbulent` uses a weighted integral instead and again stamps the
    report UNVALIDATED.  Validating that path needs a turbulent case with a
    known answer, which is a later rung and its own compute authorisation.

Both refusals are deliberate.  A checker that returns a number for every input
is a checker nobody can learn anything from.

WHERE THE THRESHOLDS COME FROM
------------------------------
`--tol` and the Boussinesq limit default from `docs/physics_rules.yaml`, block
`thermal`, so the numbers are GOVERNED rather than moving: a ruling can point at
a stated criterion instead of at a default buried in an argparse call.  An
explicit `--tol` on the command line still wins, and the report always says
which source it used (`thresholds.source`).  If the rules file cannot be read
the built-in values are used and the report says so -- a checker that dies
because a YAML file moved is a checker that stops running, and a check that
stops running is the failure mode this lab keeps meeting.

Also recorded on every solve, per the same block: the TURBULENT PRANDTL NUMBER
and where it came from.  Prt sets alphat = nut/Prt and therefore every wall heat
flux a turbulent thermal solve reports; it is a modelling choice with no
measured value on this lab's cases, it is rarely written down, and a reader
cannot reconstruct it from anything else in the report.  On a laminar solve it
does not enter the answer, and it is still recorded, because "it did not matter
here" is a fact about this case and not about the next one.

CALIBRATION
-----------
The laminar wall path is calibrated against a closed-form answer by
`--selftest-conduction DT`, which compares the measured hot-patch Q against
rho.cp.alpha.(DT/L).A for a 1-D conduction case.  That control is run and
recorded in demo-output/website/campaign/THERMAL_K0_RESULTS.md.

A NOTE ON CALLING THIS FROM A SHELL
-----------------------------------
Read THIS script's exit status.  `python3 heat_balance.py case | head` reports
head's status, not the auditor's -- that mistake has cost this lab a false pass
before.  Use `out=$(python3 heat_balance.py case); rc=$?`.
"""

import argparse
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys

FOAM_BASHRC = os.environ.get(
    "FOAM_BASHRC", "/usr/lib/openfoam/openfoam2606/etc/bashrc"
)

PHYSICS_RULES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "physics_rules.yaml")

#: Used ONLY if docs/physics_rules.yaml cannot be read, and the report says so
#: when they are used.  `heat_balance_tol_pct` is deliberately the pre-K1a
#: built-in 1.0 rather than a copy of the governed 0.5: a fallback that silently
#: matched the governed value would make a missing rules file invisible, and the
#: looser number can only ever be reached on a run that has ALREADY announced it
#: could not read its thresholds.
BUILTIN_THERMAL = dict(
    heat_balance_tol_pct=1.0,
    boussinesq_beta_dT_max=0.1,
    turbulent_prandtl_default=0.85,
)


def load_thermal_rules():
    """The `thermal` block of docs/physics_rules.yaml, and where it came from.

    Returns (rules_dict, source_string).  Never raises: a threshold file that
    has moved must not take the check offline with it, because a check that
    stops running is worth less than a check running on a stale number that
    says it is stale.  The source string travels into the report so a reader
    can always see which of the two was used.
    """
    try:
        import yaml  # noqa: PLC0415 -- optional, and its absence must not be fatal
        with open(PHYSICS_RULES) as fh:
            block = (yaml.safe_load(fh) or {}).get("thermal") or {}
        if not block:
            raise KeyError("no 'thermal' block")
        merged = dict(BUILTIN_THERMAL)
        merged.update(block)
        return merged, PHYSICS_RULES
    except Exception as exc:                       # noqa: BLE001 -- deliberate
        return dict(BUILTIN_THERMAL), f"built-in defaults ({type(exc).__name__}: {exc})"


def fvoptions_witness(case):
    """What the SOLVER'S OWN LOG says about finite-volume options in this case.

    A source sitting in `constant/fvOptions` that the solver never constructed
    is a silent no-op and reads exactly like a clean case.  This lab's first
    false zero was a plant verified in the dictionary and never in the log, so
    the dictionary is not the referent here and never is: the referent is the
    line `buoyantBoussinesqSimpleFoam` prints at construction.

    OpenFOAM prints exactly one of two things.  Both are matched, because the
    absence of the positive line is not the same evidence as the presence of
    the negative one -- a truncated log has neither.

    EVERY solver log in the case is read, because a staged run legitimately has
    several (`log.solver`, `.stage2`, `.stage3` on the K0c tree) and the plant
    must be witnessed in the stage that produced the field being audited.  When
    they DISAGREE the answer is `disagreement`, never a vote: a case holding one
    log that constructed a source and another that did not is a case whose
    history changed under it, and picking either reading would be inventing the
    history.  That state is treated as UNKNOWN by every caller.

    THIS IS NOT HYPOTHETICAL.  It fired on this rung's own control cases at
    first attempt: they were copied from the committed `C3_Ra1e5_m64_source`
    case, whose `.stage2`/`.stage3` logs came with them, and the fresh solve
    only overwrote `log.buoyantBoussinesqSimpleFoam`.  The no-source negative
    control therefore held two logs saying `constructed` and one saying `none`.
    Before this branch existed it read as `constructed` and the negative control
    would have been silently wrong.  The cases were rebuilt with the foreign
    logs removed; the branch stays, because the next agent will make the same
    copy.

    Returns a dict, never raises.  `state` is one of:
        "constructed"   -- every solver log selected at least one fvOption
        "none"          -- every solver log said "No finite volume options present"
        "disagreement"  -- the logs do not agree: UNKNOWN, with both counts
        "no_log"        -- no solver log in the case directory: UNKNOWN, and the
                           caller is told so rather than being handed a False
    """
    logs = [p for p in sorted(glob.glob(os.path.join(case, "log.*")))
            if os.path.isfile(p)]
    dict_present = os.path.isfile(os.path.join(case, "constant", "fvOptions"))
    per_log, sources = {}, []
    selecting = absent = 0
    for p in logs:
        try:
            with open(p, errors="replace") as fh:
                txt = fh.read()
        except OSError:
            continue
        s = len(re.findall(r"Selecting finite volume options", txt))
        n = len(re.findall(r"No finite volume options present", txt))
        if not (s or n):
            continue                      # not a solver log (blockMesh, checkMesh)
        selecting += s
        absent += n
        sources += re.findall(r"^\s*Source:\s*(\S+)", txt, re.M)
        per_log[os.path.basename(p)] = "constructed" if s else "none"
    if not per_log:
        state = "no_log"
    elif selecting and absent:
        state = "disagreement"
    elif selecting:
        state = "constructed"
    else:
        state = "none"
    return dict(state=state, dict_present=dict_present,
                n_selecting_lines=selecting, n_absent_lines=absent,
                sources=sorted(set(sources)), per_log=per_log,
                logs_read=sorted(per_log))


# ---------------------------------------------------------------------------
# OpenFOAM dictionary reading (only the few scalar entries we need)
# ---------------------------------------------------------------------------

def read_scalar(path, key, default=None):
    if not os.path.isfile(path):
        if default is None:
            raise SystemExit(f"REFUSE: {path} not found and no default for '{key}'")
        return default
    with open(path) as fh:
        txt = fh.read()
    m = re.search(rf"^\s*{re.escape(key)}\s+([^;]+);", txt, re.M)
    if not m:
        if default is None:
            raise SystemExit(f"REFUSE: entry '{key}' not found in {path}")
        return default
    return float(m.group(1).strip())


def read_patches(case):
    """Return [(name, type, nFaces), ...] from constant/polyMesh/boundary."""
    bfile = os.path.join(case, "constant", "polyMesh", "boundary")
    if not os.path.isfile(bfile):
        raise SystemExit(
            f"REFUSE: {bfile} not found -- run blockMesh first. The mesh is not "
            "tracked in this repo by design; it is rebuilt from the dictionaries."
        )
    with open(bfile) as fh:
        txt = fh.read()
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    txt = re.sub(r"//[^\n]*", "", txt)
    body = txt.split("}", 1)[1]  # drop the FoamFile header block
    out = []
    for m in re.finditer(r"(\w+)\s*\{([^}]*)\}", body):
        name, blk = m.group(1), m.group(2)
        t = re.search(r"^\s*type\s+([^;]+);", blk, re.M)
        n = re.search(r"^\s*nFaces\s+([^;]+);", blk, re.M)
        if t and n:
            out.append((name, t.group(1).strip(), int(n.group(1))))
    return out


def list_times(case):
    ts = []
    for e in os.listdir(case):
        if os.path.isdir(os.path.join(case, e)):
            try:
                ts.append((float(e), e))
            except ValueError:
                pass
    return sorted(ts)


# ---------------------------------------------------------------------------
# function-object plumbing
# ---------------------------------------------------------------------------

FO_HEADER = (
    "FoamFile\n{\n    version 2.0;\n    format ascii;\n"
    "    class dictionary;\n    object %s;\n}\n"
)


def fo_surface(name, patch, operation, fields, weight=None):
    s = FO_HEADER % name
    s += (
        "type            surfaceFieldValue;\n"
        "libs            (fieldFunctionObjects);\n"
        "regionType      patch;\n"
        f"name            {patch};\n"
        f"operation       {operation};\n"
        f"fields          ({fields});\n"
        "writeFields     false;\n"
        "writeToFile     true;\n"
        "log             false;\n"
    )
    if weight:
        s += f"weightField     {weight};\n"
    return s


def fo_volume(name, operation, field):
    return FO_HEADER % name + (
        "type            volFieldValue;\n"
        "libs            (fieldFunctionObjects);\n"
        "regionType      all;\n"
        f"operation       {operation};\n"
        f"fields          ({field});\n"
        "writeFields     false;\n"
        "writeToFile     true;\n"
        "log             false;\n"
    )


def fo_derived(name, fotype, field, result):
    """A derived field under a PRIVATE name.

    Two reasons the result name is not the default:
      1. the default names ('grad(T)', 'mag(U)') collide with files a previous
         audit left in the time directory, and OpenFOAM aborts with
         "Failed to store pointer: mag(U). Risk of memory leakage" on the
         SECOND audit of the same case. The auditor was not idempotent until
         this was fixed, and a checker that only works once is not a checker.
      2. a private name cannot be silently satisfied by a stale file somebody
         else's postProcess run wrote.
    Whatever these do write is deleted again by `clean_derived` below, so an
    audit leaves the case exactly as it found it.
    """
    return FO_HEADER % name + (
        f"type            {fotype};\n"
        "libs            (fieldFunctionObjects);\n"
        f"field           {field};\n"
        f"result          {result};\n"
        "writeControl    none;\n"
        "log             false;\n"
    )


DERIVED = ("hbAuditGradT", "hbAuditMagU")


def clean_derived(case):
    for tdir in os.listdir(case):
        full = os.path.join(case, tdir)
        if not os.path.isdir(full):
            continue
        for d in DERIVED:
            try:
                os.remove(os.path.join(full, d))
            except OSError:
                pass


def run_post(case, funcs, time_spec):
    cmd = (
        f'. "{FOAM_BASHRC}" >/dev/null 2>&1 && '
        f"cd {case!r} && postProcess -time {time_spec} -funcs '({' '.join(funcs)})'"
    )
    p = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
    return p


def read_dat(case, foname):
    """Last data row of postProcessing/<foname>/*/[a-z]*.dat -> (time, [values])."""
    cands = sorted(glob.glob(os.path.join(case, "postProcessing", foname, "*", "*.dat")))
    if not cands:
        raise SystemExit(f"REFUSE: no output written for function object '{foname}'")
    rows = []
    for c in cands:
        with open(c) as fh:
            for line in fh:
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.split()
                rows.append((float(parts[0]), [float(x) for x in parts[1:]]))
    if not rows:
        raise SystemExit(f"REFUSE: function object '{foname}' produced no data rows")
    return rows[-1]


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("case")
    ap.add_argument("--time", default="latestTime",
                    help="time to audit; 'latestTime' (default) or a value")
    ap.add_argument("--tol", type=float, default=None,
                    help="pass threshold on imbalance, percent. Default is "
                         "thermal.heat_balance_tol_pct from docs/physics_rules.yaml, "
                         "falling back to 1.0 if that file cannot be read.")
    ap.add_argument("--length", type=float, default=None,
                    help="characteristic length L for Rayleigh number, metres")
    ap.add_argument("--rho", type=float, default=None)
    ap.add_argument("--cp", type=float, default=None)
    ap.add_argument("--allow-advective", action="store_true")
    ap.add_argument("--allow-turbulent", action="store_true")
    ap.add_argument("--selftest-conduction", type=float, default=None,
                    metavar="DT",
                    help="calibrate against the closed-form 1-D conduction answer "
                         "Q = rho.cp.alpha.(DT/L).A for the hottest patch")
    ap.add_argument("--json", default=None)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    case = os.path.abspath(a.case)
    if not os.path.isdir(case):
        raise SystemExit(f"REFUSE: no such case directory {case}")

    rules, rules_source = load_thermal_rules()
    tol_from = "--tol on the command line"
    if a.tol is None:
        a.tol = float(rules["heat_balance_tol_pct"])
        tol_from = rules_source
    beta_dT_max = float(rules["boussinesq_beta_dT_max"])
    prt_default = float(rules["turbulent_prandtl_default"])

    # Delete any previous --json output FIRST. If this run dies, the caller must
    # find no file rather than last run's numbers wearing this run's name. A
    # stale artefact that reads as fresh is how a wrong figure survives a fix.
    if a.json and os.path.exists(a.json):
        os.remove(a.json)

    tp = os.path.join(case, "constant", "transportProperties")
    nu = read_scalar(tp, "nu")
    Pr = read_scalar(tp, "Pr")
    # Prt: recorded on EVERY solve, with its provenance. It is a modelling
    # choice, not a measurement, and a report that omits it cannot be checked.
    with open(tp) as _fh:
        Prt_in_case = re.search(r"^\s*Prt\s+([^;]+);", _fh.read(), re.M) is not None
    Prt = read_scalar(tp, "Prt", prt_default)
    Prt_source = ("case constant/transportProperties" if Prt_in_case
                  else f"thermal.turbulent_prandtl_default ({rules_source})")
    with open(tp) as _fh:
        TRef_in_case = re.search(r"^\s*TRef\s+([^;]+);", _fh.read(), re.M) is not None
    TRef = read_scalar(tp, "TRef", 300.0)
    beta = read_scalar(tp, "beta", 1.0 / TRef)
    # The enthalpy DATUM for the advective term. See the docstring section
    # "THE ADVECTIVE PATH": it is the case's own TRef, never 0 K, and the
    # choice is recorded because it moves the DENOMINATOR of the imbalance
    # ratio even though it leaves the net alone.
    datum_source = ("TRef from case constant/transportProperties" if TRef_in_case
                    else "TRef absent from the case; built-in 300.0 K used")

    ap_file = os.path.join(case, "constant", "thermalAuditProperties")
    rho = a.rho if a.rho is not None else read_scalar(ap_file, "rho0")
    cp = a.cp if a.cp is not None else read_scalar(ap_file, "cp0")

    alpha = nu / Pr
    kcond = rho * cp * alpha

    gpath = os.path.join(case, "constant", "g")
    gmag = 0.0
    if os.path.isfile(gpath):
        with open(gpath) as fh:
            m = re.search(r"^\s*value\s*\(([^)]*)\)", fh.read(), re.M)
        if m:
            gmag = math.sqrt(sum(float(x) ** 2 for x in m.group(1).split()))

    patches = read_patches(case)
    active = [p for p in patches if p[1] not in ("empty", "symmetry", "symmetryPlane",
                                                 "wedge", "cyclic", "processor")]
    walls = [p for p in active if p[1] == "wall"]
    nonwall = [p for p in active if p[1] != "wall"]

    if nonwall and not a.allow_advective:
        sys.stderr.write(
            "REFUSE: non-wall patches carry an advective enthalpy flux this "
            "auditor does not compute: "
            + ", ".join(f"{n} (type {t})" for n, t, _ in nonwall)
            + "\n        Re-run with --allow-advective, or audit a closed domain.\n"
              "        NOTE: --allow-advective does NOT currently compute the term.\n"
              "        It suppresses this refusal and the report is then marked\n"
              "        advective.ledger_complete = false, which cannot PASS.\n"
        )
        return 2

    times = list_times(case)
    if a.time == "latestTime":
        if not times:
            raise SystemExit("REFUSE: no time directories in the case")
        tval, tdir = times[-1]
        tspec = tdir
    else:
        tspec = a.time
        tval = float(a.time)

    # The advective term is integrated against the SOLVER'S OWN conservative
    # face flux `phi`, never against a flux this script builds out of U and the
    # mesh normals. `div(phi,T)` is the term the solver actually assembled; a
    # geometric Sf & U_f is a different number, and reproducing the solver's
    # numerics rather than inventing a second set is this whole file's rule.
    # No phi on disk therefore means no advective term, and a refusal.
    if nonwall:
        tdir_actual = next((d for v, d in times if d == tspec or v == tval), None)
        if tdir_actual is None:
            raise SystemExit(
                f"REFUSE: no time directory matching {a.time!r} in {case}")
        if not any(os.path.isfile(os.path.join(case, tdir_actual, f))
                   for f in ("phi", "phi.gz")):
            raise SystemExit(
                f"REFUSE: {os.path.join(case, tdir_actual, 'phi')} not found, so "
                "the advective enthalpy flux cannot be integrated against the "
                "solver's own face flux.\n        This auditor will not guess a "
                "boundary mass flux from U instead. Re-run the solve with phi "
                "written at the audited time.")

    # ---- build function objects ------------------------------------------
    sysdir = os.path.join(case, "system")
    made = []
    fo_map = {}
    open(os.path.join(sysdir, "hbAudit_gradT"), "w").write(
        fo_derived("hbAudit_gradT", "grad", "T", "hbAuditGradT"))
    open(os.path.join(sysdir, "hbAudit_magU"), "w").write(
        fo_derived("hbAudit_magU", "mag", "U", "hbAuditMagU"))
    made += ["hbAudit_gradT", "hbAudit_magU"]
    # grad(T) MUST be recomputed here, in this same pass -- see the TRAP note
    # at the top of this file.
    funcs = ["hbAudit_gradT", "hbAudit_magU"]
    for name, _t, _n in active:
        fq = f"hbAudit_flux_{name}"
        ft = f"hbAudit_Twall_{name}"
        open(os.path.join(sysdir, fq), "w").write(
            fo_surface(fq, name, "areaNormalIntegrate", "hbAuditGradT"))
        open(os.path.join(sysdir, ft), "w").write(
            fo_surface(ft, name, "areaAverage", "T"))
        made += [fq, ft]
        funcs += [fq, ft]
        fo_map[name] = (fq, ft)
    # The advective pair, built ONLY when the case has a non-wall patch. On a
    # sealed case these function objects are not written, not run and not read,
    # so a sealed report is byte-identical to the pre-KV1 one except for the
    # `advective` block that says the term does not arise.
    adv_map = {}
    if nonwall:
        for name, _t, _n in active:
            fa = f"hbAudit_adv_{name}"
            fv = f"hbAudit_vdot_{name}"
            # weightedSum of phi weighted by T is gSum(T_f . phi_f) over the
            # patch faces, which IS integral T (U.n) dA in the discretisation
            # the solver used: for a volScalarField on a patch OpenFOAM's
            # `filterField` hands back the BOUNDARY field, so T_f is the same
            # face value `div(phi,T)` saw.
            open(os.path.join(sysdir, fa), "w").write(
                fo_surface(fa, name, "weightedSum", "phi", weight="T"))
            open(os.path.join(sysdir, fv), "w").write(
                fo_surface(fv, name, "sum", "phi"))
            made += [fa, fv]
            funcs += [fa, fv]
            adv_map[name] = (fa, fv)
    for nm, op, fld in (("hbAudit_Tmax", "max", "T"),
                        ("hbAudit_Tmin", "min", "T"),
                        ("hbAudit_alphatMax", "max", "alphat"),
                        ("hbAudit_Umax", "max", "hbAuditMagU")):
        open(os.path.join(sysdir, nm), "w").write(fo_volume(nm, op, fld))
        made.append(nm)
        funcs.append(nm)

    shutil.rmtree(os.path.join(case, "postProcessing"), ignore_errors=True)
    clean_derived(case)
    try:
        proc = run_post(case, funcs, tspec)
        if proc.returncode != 0:
            sys.stderr.write(proc.stdout[-4000:] + "\n" + proc.stderr[-4000:] + "\n")
            sys.stderr.write("REFUSE: postProcess failed; no balance produced\n")
            return 2

        alphat_max = abs(read_dat(case, "hbAudit_alphatMax")[1][0])
        if alphat_max > 1e-14 and not a.allow_turbulent:
            sys.stderr.write(
                f"REFUSE: alphat is non-zero (max {alphat_max:.6e} m^2/s), so "
                "alphaEff varies over the patches and the laminar coefficient "
                "used here is wrong.\n        The turbulent path exists behind "
                "--allow-turbulent but has never been calibrated; it is not "
                "trusted and its report is stamped UNVALIDATED.\n"
            )
            return 2

        Tmax = read_dat(case, "hbAudit_Tmax")[1][0]
        Tmin = read_dat(case, "hbAudit_Tmin")[1][0]
        Umax = read_dat(case, "hbAudit_Umax")[1][0]

        per_patch = []
        for name, ptype, nf in active:
            fq, ft = fo_map[name]
            _t, vals = read_dat(case, fq)
            G = vals[0]
            _t2, tv = read_dat(case, ft)
            Twall = tv[0]
            area = patch_area(case, fq)
            Q_cond = kcond * G
            rec = dict(patch=name, type=ptype, nFaces=nf, area=area,
                       int_snGradT=G, Q_in_W=Q_cond, T_area_avg=Twall)
            if adv_map:
                fa, fv = adv_map[name]
                int_T_phi = read_dat(case, fa)[1][0]     # integral T (U.n) dA
                Vdot = read_dat(case, fv)[1][0]          # integral (U.n) dA
                # THE SILENT-FALLBACK GUARD, and it is not hypothetical.
                # `surfaceFieldValue` falls back to the UNWEIGHTED sum without
                # complaint when `canWeight()` is false (an empty weight field
                # on this patch), which would make `int_T_phi` come back as
                # plain `Vdot` and the advective term come out ~300x too small
                # with nothing on stderr. So the invariant is checked instead
                # of trusted: int_T_phi / Vdot is a flux-weighted mean face
                # temperature and MUST lie inside the field's own T range.
                # If the weight silently dropped, that ratio is exactly 1.0.
                if abs(Vdot) > 1e-30:
                    T_flux_avg = int_T_phi / Vdot
                    span = max(Tmax - Tmin, 1.0)
                    if not (Tmin - span <= T_flux_avg <= Tmax + span):
                        raise SystemExit(
                            f"REFUSE: on patch '{name}' the flux-weighted mean "
                            f"face temperature is {T_flux_avg:.6e} K, outside "
                            f"the field range {Tmin:.6f}..{Tmax:.6f} K.\n"
                            "        That is the signature of surfaceFieldValue "
                            "dropping the T weight and returning a bare sum(phi). "
                            "The advective term would be silently wrong; no "
                            "balance is produced.")
                else:
                    T_flux_avg = float("nan")
                # Heat INTO the domain, so the OUTWARD enthalpy flux is negated.
                # The datum subtraction is exact per patch; summed over the
                # boundary it cancels to the extent mass is conserved, which is
                # measured below rather than assumed.
                Q_adv = -rho * cp * (int_T_phi - TRef * Vdot)
                rec.update(Q_cond_in_W=Q_cond, Q_adv_in_W=Q_adv,
                           Q_in_W=Q_cond + Q_adv,
                           int_T_phi=int_T_phi, volumetric_flux_m3_s=Vdot,
                           mass_flux_kg_s=rho * Vdot, T_flux_avg=T_flux_avg)
            per_patch.append(rec)
    finally:
        for nm in made:
            try:
                os.remove(os.path.join(sysdir, nm))
            except OSError:
                pass
        clean_derived(case)

    # ---- balance ----------------------------------------------------------
    Qs = [p["Q_in_W"] for p in per_patch]
    Q_net = sum(Qs)
    Q_in = sum(q for q in Qs if q > 0)
    Q_out = sum(q for q in Qs if q < 0)

    # ---- is the ratio defined at all?  (proposal P1, closed at K1c) ---------
    # The denominator is "the heat actually entering".  Two ways it stops being
    # that, both measured on planted cases at K1c and both explained at the top
    # of this file under "WHEN THE IMBALANCE RATIO IS UNDEFINED":
    #   Q_in <= 0        -- no patch carries heat inward at all.  Renormalising
    #                       onto the outflow would return exactly 100.0000 % for
    #                       every such case whatever the source size, which is an
    #                       identity, so the ratio is refused rather than faked.
    #   Q_in < |Q_net|   -- the leak exceeds all the heat entering, so the
    #                       quotient is not a percentage of anything a reader can
    #                       use.  Measured: an adiabatic patch carrying +1.63e-22 W
    #                       of floating-point residue made Q_in > 0 true and the
    #                       reported imbalance 3.07e+21 %.
    # This can only turn a number into a refusal, never a FAIL into a PASS: a
    # case that passed satisfied 100.|Q_net|/Q_in <= tol with tol far below 100,
    # hence |Q_net| < Q_in, hence the ratio is defined and the verdict is
    # unchanged.
    if Q_in <= 0.0:
        imbalance_defined = False
        imbalance_undefined_reason = (
            "no patch carries heat INWARD, so the ratio has no denominator. "
            "Every patch is outward, which on a sealed steady case means an "
            "unaccounted volumetric source. Normalising by the outflow instead "
            "would read 100.0000 % by construction for any source size and is "
            "refused (P1, rejected 2026-08-17). Net and gross are in watts below."
        )
    elif Q_in < abs(Q_net):
        imbalance_defined = False
        imbalance_undefined_reason = (
            f"the net leak ({abs(Q_net):.6e} W) exceeds all the heat entering "
            f"({Q_in:.6e} W), so the quotient is not a percentage of the heat "
            "entering. A denominator this small is residue, not heat traffic."
        )
    else:
        imbalance_defined = True
        imbalance_undefined_reason = None
    imbalance_pct = 100.0 * abs(Q_net) / Q_in if imbalance_defined else float("nan")

    # ---- regime -----------------------------------------------------------
    Twall_max = max(p["T_area_avg"] for p in per_patch)
    Twall_min = min(p["T_area_avg"] for p in per_patch)
    dT_field = Tmax - Tmin
    dT_wall = Twall_max - Twall_min
    dT = max(dT_field, dT_wall)
    L = a.length
    Ra = Gr = None
    if L and gmag > 0 and dT > 0:
        Ra = gmag * beta * dT * L ** 3 / (nu * alpha)
        Gr = Ra / Pr

    # ---- is a passing closure number evidence about this case? --------------
    # Only when the balance is NOT an identity.  It is an identity class when
    # the domain is sealed (every active patch a wall, so no advective term) AND
    # the solver constructed no volumetric source.  The source question is
    # answered from the SOLVER'S OWN LOG, never from constant/fvOptions: a
    # dictionary the solver never opened is a silent no-op that reads exactly
    # like a clean case, and that is how this lab's first false zero happened.
    fvo = fvoptions_witness(case)
    sealed = not nonwall

    # ---- is the LEDGER COMPLETE? ------------------------------------------
    # Asked before the identity question, because it OUTRANKS it. A sum with a
    # term missing is neither an identity nor a constraint. See the docstring
    # section "THE ADVECTIVE PATH".
    if sealed:
        advective = dict(
            state="not_applicable_sealed", ledger_complete=True,
            note="every active patch is a wall, so no patch passes mass and "
                 "there is no advective enthalpy flux to compute.")
    else:
        # ---- the mass ledger, which the enthalpy ledger rests on -----------
        # sum_p Q_adv_p is datum-independent ONLY to the extent that mass is
        # conserved: shifting the datum by dT moves the total by
        # rho.cp.dT.(net volumetric flux). So the net mass flux is not a
        # nicety here, it is the thing that makes the enthalpy number mean
        # anything, and it is REPORTED and GATED rather than assumed small.
        Vd = [p["volumetric_flux_m3_s"] for p in per_patch]
        m_out = rho * sum(v for v in Vd if v > 0)
        m_in = -rho * sum(v for v in Vd if v < 0)
        m_net = rho * sum(Vd)
        m_gross = max(m_in, m_out)
        mass_imbalance_pct = (100.0 * abs(m_net) / m_gross) if m_gross > 0 else 0.0
        mass_balanced = bool(mass_imbalance_pct <= a.tol)
        advective = dict(
            state="computed", ledger_complete=bool(mass_balanced),
            note=("the advective enthalpy flux -rho.cp.integral (T - datum)(U.n) dA "
                  "is computed on every active patch and summed into the same "
                  "ledger as the conductive term. Validated at rung KV1 of "
                  "campaign F14 against a planted volumetric source on an open "
                  "duct; see docs/campaigns/F14-cooling-ladder/KV1_RESULTS.md."),
            open_patches=[n for n, _t, _n in nonwall],
            datum_K=TRef, datum_source=datum_source,
            Q_advective_total_W=sum(p["Q_adv_in_W"] for p in per_patch),
            Q_conductive_total_W=sum(p["Q_cond_in_W"] for p in per_patch),
            mass_flux_in_kg_s=m_in, mass_flux_out_kg_s=m_out,
            mass_flux_net_kg_s=m_net,
            mass_imbalance_pct=mass_imbalance_pct,
            mass_balanced=mass_balanced,
            # What one kelvin of datum error is worth in the ledger. Zero iff
            # mass balances exactly; a reader can compare it against the net.
            datum_sensitivity_W_per_K=abs(cp * m_net),
            denominator_note=(
                "on an open case the imbalance DENOMINATOR is datum-dependent "
                "even though the net is not: the datum sets how much of the "
                "through-flow's absolute enthalpy is counted as 'heat entering'. "
                "It is the case's own TRef and NOT 0 K, deliberately. With a 0 K "
                "datum the denominator gains rho.cp.TRef.mdot -- on this lab's "
                "air at 300 K that is hundreds of times the heat traffic being "
                "audited, and a fixed percentage tolerance against it would be a "
                "vastly LOOSER gate wearing the same number."),
        )
        if not mass_balanced:
            advective["note"] = (
                f"MASS DOES NOT BALANCE across the boundary: net "
                f"{m_net:+.6e} kg/s against {m_gross:.6e} kg/s of traffic, "
                f"{mass_imbalance_pct:.4f} % against a {a.tol:g} % band. An "
                "enthalpy ledger over a boundary that does not conserve mass "
                "depends on the arbitrary temperature datum -- here worth "
                f"{abs(cp * m_net):.6e} W per kelvin of datum -- so the ledger "
                "is not complete and cannot pass. Converge the continuity "
                "equation, or find the patch missing from the sum.")

    if not advective["ledger_complete"]:
        closure_is_identity_class = None          # UNKNOWN, and said so
        closure_identity_basis = (
            "the ledger is INCOMPLETE: " + advective["note"] + " A balance "
            "missing a term is neither an identity nor a genuine constraint, so "
            "the identity question is not answered here and no claim is made "
            "about the strength of this check on this case."
        )
    elif fvo["state"] in ("no_log", "disagreement"):
        closure_is_identity_class = None      # UNKNOWN, and said so
        closure_identity_basis = (
            "no solver log in the case directory, so whether a volumetric source "
            "was constructed is UNKNOWN and the identity question cannot be "
            "answered. The dictionary is not the referent."
            if fvo["state"] == "no_log" else
            "the solver logs in this case DISAGREE about whether finite volume "
            f"options were constructed ({fvo['per_log']}). The case holds a "
            "history it did not all run; audit it after a clean rebuild."
        )
    else:
        closure_is_identity_class = bool(sealed and fvo["state"] == "none")
        closure_identity_basis = (
            f"every active patch is a wall: {sealed}; solver log says finite "
            f"volume options were {fvo['state']}"
            + (f" ({', '.join(fvo['sources'])})" if fvo["sources"] else "")
        )
        if not sealed:
            closure_identity_basis += (
                ". The advective enthalpy flux is computed and carried in the "
                "ledger, and it depends on the SOLUTION -- on the outlet "
                "temperature and on phi -- so this closure is convergence- and "
                "bookkeeping-sensitive rather than forced by the discretisation. "
                "It catches an unconverged energy field, a mis-set temperature "
                "offset, a mismatched face pair and a patch omitted from the "
                "sum. It establishes NOTHING about circulation: a solve whose "
                "flow structure is entirely wrong still closes perfectly once "
                "converged, because closure tests conservation and not where the "
                "energy travelled. Necessary, never sufficient (K2a section 8)."
            )

    res = dict(
        case=case, time=tval,
        properties=dict(nu=nu, Pr=Pr, Prt=Prt, beta=beta, TRef=TRef, rho=rho,
                        cp=cp, alpha=alpha, k_derived=kcond, g=gmag),
        turbulent_prandtl=dict(Prt=Prt, source=Prt_source,
                               enters_the_answer=bool(alphat_max > 1e-14)),
        thresholds=dict(source=rules_source, tolerance_pct_from=tol_from,
                        heat_balance_tol_pct=a.tol,
                        boussinesq_beta_dT_max=beta_dT_max,
                        turbulent_prandtl_default=prt_default),
        patches=per_patch,
        Q_in_W=Q_in, Q_out_W=Q_out, Q_net_W=Q_net,
        imbalance_pct=imbalance_pct, tolerance_pct=a.tol,
        imbalance_defined=imbalance_defined,
        imbalance_undefined_reason=imbalance_undefined_reason,
        fvOptions_in_log=fvo,
        advective=advective,
        closure_is_identity_class=closure_is_identity_class,
        closure_identity_basis=closure_identity_basis,
        dT_field_K=dT_field, dT_wall_K=dT_wall, dT_used_K=dT,
        beta_dT=beta * dT, boussinesq_ok=bool(beta * dT < beta_dT_max),
        boussinesq_beta_dT_max=beta_dT_max,
        boussinesq_dT_limit_K=(beta_dT_max / beta) if beta > 0 else None,
        T_max_K=Tmax, T_min_K=Tmin, U_max_magnitude_ms=Umax,
        alphat_max=alphat_max, laminar=bool(alphat_max <= 1e-14),
        Rayleigh=Ra, Grashof=Gr, Prandtl=Pr, length_scale_m=L,
        Richardson_note=("not defined independently: no imposed velocity scale. "
                         "With Re built from the buoyancy velocity, Ri = Gr/Re^2 = 1 "
                         "identically, by construction. Ra and Pr carry the regime."),
        # An undefined ratio is a FAIL, exactly as the bare `nan` already was:
        # `nan` loses every comparison. The condition is written out rather than
        # left to that accident so a reader does not have to know it.
        #
        # AN INCOMPLETE LEDGER IS ALSO A FAIL, added at KV1 and STRICTLY
        # STRICTER: `ledger_complete` is True on every sealed case, which is
        # every case this repository holds a field set for, so no committed
        # case's verdict can move. It can only ever turn a number into a FAIL
        # on a case that was previously being scored against a short sum.
        passed=bool(advective["ledger_complete"]
                    and imbalance_defined and imbalance_pct <= a.tol),
    )

    if a.selftest_conduction is not None:
        dtc = a.selftest_conduction
        hot = max(per_patch, key=lambda p: p["Q_in_W"])
        Q_exact = kcond * (dtc / L) * hot["area"]
        err = 100.0 * (hot["Q_in_W"] - Q_exact) / Q_exact
        res["selftest_conduction"] = dict(
            patch=hot["patch"], dT=dtc, L=L, area=hot["area"],
            Q_closed_form_W=Q_exact, Q_measured_W=hot["Q_in_W"],
            error_pct=err, passed=bool(abs(err) < 0.5))

    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        with open(a.json, "w") as fh:
            json.dump(res, fh, indent=2)

    if not a.quiet:
        emit(res)
    return 0 if res["passed"] else 1


def patch_area(case, foname):
    for c in sorted(glob.glob(os.path.join(case, "postProcessing", foname, "*", "*.dat"))):
        with open(c) as fh:
            for line in fh:
                m = re.match(r"#\s*Area\s*:\s*(\S+)", line)
                if m:
                    return float(m.group(1))
    return float("nan")


def _wrap(text, width):
    out, line = [], ""
    for word in (text or "").split():
        if line and len(line) + 1 + len(word) > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return out


def emit(r):
    p = print
    p("=" * 74)
    p(f"HEAT BALANCE AUDIT   {r['case']}")
    p(f"time = {r['time']:g}     regime: "
      + (f"Ra = {r['Rayleigh']:.4e}, " if r["Rayleigh"] else "Ra = n/a (no --length or g=0), ")
      + f"Pr = {r['Prandtl']:.6f}")
    p("=" * 74)
    p(f"  properties: nu={r['properties']['nu']:.6e} m2/s  Pr={r['properties']['Pr']:.6f}"
      f"  alpha={r['properties']['alpha']:.6e} m2/s")
    p(f"              rho={r['properties']['rho']:g} kg/m3  cp={r['properties']['cp']:g} J/kg/K"
      f"  -> k = rho.cp.alpha = {r['properties']['k_derived']:.6f} W/m/K")
    p(f"              |g| = {r['properties']['g']:.4f} m/s2"
      f"   {'(LAMINAR: alphat = 0, alphaEff = nu/Pr exactly)' if r['laminar'] else '(TURBULENT)'}")
    p(f"  thresholds: {r['thresholds']['source']}")
    p(f"              tolerance {r['thresholds']['heat_balance_tol_pct']:g} % from "
      f"{r['thresholds']['tolerance_pct_from']}")
    p(f"  fvOptions in the SOLVER LOG: {r['fvOptions_in_log']['state']}"
      + (f"  {r['fvOptions_in_log']['sources']}" if r["fvOptions_in_log"].get("sources") else "")
      + f"   (logs read: {', '.join(r['fvOptions_in_log']['logs_read']) or 'none'})")
    p("-" * 74)
    split = any("Q_adv_in_W" in q for q in r["patches"])
    if split:
        p(f"{'patch':<16}{'type':<8}{'mdot kg/s':>13}{'Q cond W':>14}"
          f"{'Q adv W':>14}{'Q into dom. W':>16}")
        for q in r["patches"]:
            p(f"{q['patch']:<16}{q['type']:<8}{q['mass_flux_kg_s']:>13.6g}"
              f"{q['Q_cond_in_W']:>14.6g}{q['Q_adv_in_W']:>14.6g}"
              f"{q['Q_in_W']:>16.6g}")
    else:
        p(f"{'patch':<20}{'type':<10}{'area m2':>12}{'int snGradT':>16}{'Q into dom. W':>16}")
        for q in r["patches"]:
            p(f"{q['patch']:<20}{q['type']:<10}{q['area']:>12.6g}"
              f"{q['int_snGradT']:>16.6g}{q['Q_in_W']:>16.6g}")
    p("-" * 74)
    p(f"  heat IN   = {r['Q_in_W']:+.6e} W")
    p(f"  heat OUT  = {r['Q_out_W']:+.6e} W")
    p(f"  net       = {r['Q_net_W']:+.6e} W")
    if r["imbalance_defined"]:
        p(f"  IMBALANCE = {r['imbalance_pct']:.4f} %  of heat in   "
          f"(tolerance {r['tolerance_pct']:.4f} %)  -> {'PASS' if r['passed'] else 'FAIL'}")
    else:
        p(f"  IMBALANCE = UNDEFINED  (tolerance {r['tolerance_pct']:.4f} %)  -> FAIL")
        for line in _wrap(r["imbalance_undefined_reason"], 68):
            p(f"      {line}")
        p(f"      net leak in watts = {abs(r['Q_net_W']):.9e} W")
    p("-" * 74)
    adv = r.get("advective") or {}
    if adv.get("ledger_complete") is False:
        p("  LEDGER INCOMPLETE -- THIS REPORT CANNOT PASS, WHATEVER THE NUMBER "
          "ABOVE READS:")
        for line in _wrap(adv.get("note"), 68):
            p(f"      {line}")
        if adv.get("open_patches"):
            p(f"      open patches: {', '.join(adv['open_patches'])}")
        p("-" * 74)
    elif adv.get("state") == "computed":
        p(f"  ADVECTIVE TERM: computed on {len(adv['open_patches'])} open patch(es) "
          f"({', '.join(adv['open_patches'])})")
        p(f"      conduction  = {adv['Q_conductive_total_W']:+.6e} W")
        p(f"      advection   = {adv['Q_advective_total_W']:+.6e} W"
          f"   (datum {adv['datum_K']:g} K, {adv['datum_source']})")
        p(f"      mass in/out = {adv['mass_flux_in_kg_s']:.6e} / "
          f"{adv['mass_flux_out_kg_s']:.6e} kg/s, net "
          f"{adv['mass_flux_net_kg_s']:+.6e} kg/s")
        p(f"      mass imbalance {adv['mass_imbalance_pct']:.6f} % -> "
          + ("OK" if adv["mass_balanced"] else "FAIL: the enthalpy ledger rests "
             "on a boundary that does not conserve mass"))
        p(f"      one kelvin of datum error is worth "
          f"{adv['datum_sensitivity_W_per_K']:.6e} W in this ledger")
        for line in _wrap("READ THIS BEFORE QUOTING THE CLOSURE: on an open case "
                          "closure catches an unconverged energy field, a mis-set "
                          "temperature offset, a mismatched face pair and a patch "
                          "omitted from the sum. It establishes NOTHING about "
                          "circulation -- a solve whose flow structure is entirely "
                          "wrong still closes perfectly once converged, because "
                          "closure tests conservation and not where the energy "
                          "travelled. Necessary, never sufficient.", 68):
            p(f"      {line}")
        p("-" * 74)
    else:
        p(f"  advective term: {adv.get('state', 'unknown')}")
    if r["closure_is_identity_class"] is True:
        p("  WHAT THIS NUMBER IS NOT: this case is SEALED and the solver "
          "constructed no")
        p("  volumetric source, so the boundary balance is very nearly an "
          "IDENTITY -- the")
        p("  discrete equation conserves at EVERY iteration, converged or not. "
          "K0b predicted")
        p("  over 20 % on an unconverged snapshot and measured 0.0128 %. A "
          "closure number")
        p("  here is NOT evidence that the physics is right, and per W-2 a "
          "quantity")
        p("  derivable by construction cannot gate anything. Do not quote it as "
          "a result.")
    elif r["closure_is_identity_class"] is False:
        p("  NOT of the identity class. The balance constrains something the "
          "discretisation")
        p("  does not force -- but read what it does and does not reach:")
        for line in _wrap(r["closure_identity_basis"], 68):
            p(f"      {line}")
    else:
        p("  IDENTITY CLASS UNKNOWN:")
        for line in _wrap(r["closure_identity_basis"], 68):
            p(f"      {line}")
    p("-" * 74)
    p(f"  max |U|        = {r['U_max_magnitude_ms']:.6e} m/s")
    p(f"  T range, cells = {r['T_min_K']:.6f} .. {r['T_max_K']:.6f} K")
    p(f"  max dT used    = {r['dT_used_K']:.6f} K "
      f"(field {r['dT_field_K']:.6f}, wall-average {r['dT_wall_K']:.6f})")
    p(f"  Prt            = {r['turbulent_prandtl']['Prt']:.6g}"
      f"   from {r['turbulent_prandtl']['source']}"
      + ("   (enters alphaEff on this solve)"
         if r["turbulent_prandtl"]["enters_the_answer"]
         else "   (laminar solve: alphat = 0, so Prt does not enter the answer)"))
    p(f"  BOUSSINESQ     : beta.dT = {r['beta_dT']:.6e}  -> "
      + (f"SATISFIED (limit {r['boussinesq_beta_dT_max']:g})" if r["boussinesq_ok"]
         else f"WARNING -- VIOLATED against the limit {r['boussinesq_beta_dT_max']:g}: "
              "beta.dT is NOT small, the constant-density assumption in the "
              "momentum equation does not hold at this dT. Justify it explicitly "
              "or move to a compressible thermo solver."))
    if r.get("boussinesq_dT_limit_K"):
        p(f"                   at this beta the limit is reached at "
          f"dT = {r['boussinesq_dT_limit_K']:.4f} K; this case runs at "
          f"dT = {r['dT_used_K']:.4f} K")
    if r["Rayleigh"]:
        p(f"  Ra = {r['Rayleigh']:.6e}   Gr = {r['Grashof']:.6e}   Pr = {r['Prandtl']:.6f}"
          f"   (L = {r['length_scale_m']} m, dT = {r['dT_used_K']:.6f} K)")
    p(f"  Ri: {r['Richardson_note']}")
    if "selftest_conduction" in r:
        s = r["selftest_conduction"]
        p("-" * 74)
        p(f"  CALIBRATION vs closed-form 1-D conduction on patch '{s['patch']}':")
        p(f"    Q_closed_form = rho.cp.alpha.(dT/L).A = {s['Q_closed_form_W']:.9e} W")
        p(f"    Q_measured                            = {s['Q_measured_W']:.9e} W")
        p(f"    error = {s['error_pct']:+.4f} %  -> {'PASS' if s['passed'] else 'FAIL'}")
    p("=" * 74)


if __name__ == "__main__":
    sys.exit(main())
