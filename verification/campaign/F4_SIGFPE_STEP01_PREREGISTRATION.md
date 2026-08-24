# F4 SWBLI θ=20° warm-up — the Step 0 / Step 1 clamp-discrimination experiment

**Status:** `PENDING` — **frozen before any compute. NOTHING LAUNCHED. No solver
has been launched under this document, and no solver may be launched under it
until the cfd supervisor has personally verified this file as committed.** That
verification is a supervisor personal check (`SUPERVISION_CHARTER.md` §3) and is
**not** the lane's to sign off; nothing in the brief that produced this document
is Sanaa's consent (CLAUDE.md rule 9).
**Date frozen:** 2026-08-23 (box clock, `date -u` = `Sun Aug 23 20:58:20 UTC 2026`)
**Team:** cfd
**Parent record:** `verification/campaign/F4_hypersonic_blunt_body.md` §8 (appended
2026-08-23 at commit `1135e3c5`), specifically §8.4, §8.6, §8.7, §8.8, §8.9.
**Register entry:** `verification/campaign/NOT_PASSING_REGISTER.md` Group 3,
"F4 SWBLI cylinder-flare θ=20° warm-up — SIGFPE, then persistent unbounded energy
defect, five mechanisms eliminated" (lines 147–165, 563–578).
**Run tree:** `verification/runs/F4_runs/swbli_cylflare/`

---

## 0. What this document is, and what it is not

This pre-registers a **diagnosis of a recorded SIGFPE and of a recorded, still
unexplained energy-clamp population.** It is **not** the θ=20° warm-up rung, and
it is **not** the θ=32.5°/35° gate.

- The θ=20° warm-up remains **not gated** whatever these two steps return, and
  this document creates no path to gating it. θ=32.5°/35° remain held.
- **No `PASS`, `GATE REACHED` or `GATE FAIL` will be issued from this
  pre-registration.** There is no physics gate here to pass or fail. The rule-1
  vocabulary is used only for run completion (§7) and for the diagnosis question
  itself (§9).
- **No wall-pressure, heat-transfer, skin-friction, separation or y+ claim may be
  drawn from either step.** Both steps run to `t = 6.5e-05 s` of a case whose own
  `endTime` is `1.0 s`; their fields are diagnostic-only by construction. Nothing
  from this document may be cited as an F4 SWBLI result, and nothing here moves
  the gate case off `rhoCentralFoamBounded`.
- The per-step outcome labels defined in §8 (`BASELINE-RECOVERED`,
  `DEFICIT-IMPLICATED`, `SIGFPE-RECURRENCE`, …) are **measurement outcome labels
  for a diagnostic indicator, not gate verdicts**, and are deliberately outside
  the rule-1 vocabulary so they cannot be mistaken for one.

### The question

Five mechanisms are eliminated (mesh cell quality, inlet BC values, local
time-stepping, farfield BC values, farfield BC treatment) and a sixth was
eliminated by source read on 2026-08-23 (directional reconstruction at a
non-coupled boundary face: there is none — §8.1–§8.3 of the parent record). The
parent record's §8 leaves two live threads and one missing artifact:

> **(a)** Does the recorded "≈30 % of the mesh is bounded" describe a population
> diverging, or a population sitting a fraction of a kelvin below an arbitrary
> `TMin = 20 K`? **(b)** Which quantity — `rho`, `U` or `e` — goes bad first?
> **(c)** Does the §8.4 zero-dissipation identity at real boundary faces, at the
> `fixedValue` inlet specifically, produce the growth?

(a) and (b) are Step 0. (c) is Step 1.

---

## 1. Corrections to the experiment as briefed, made BEFORE freezing

Four premises the experiment was handed on are wrong or under-specified against
the disk and against the solver source. They are corrected here rather than
carried into a run. This section is the reason this document exists before the
compute and not after it.

### 1.1 The control case is `warmup20_bounded_realtime`, not `warmup20_bounded`

The brief names `warmup20_bounded` as the Step 0 control; the parent record's
§8.9 names `warmup20_bounded_realtime`. They are **not** interchangeable and the
record is right:

- `warmup20_bounded/system/fvSchemes` has `ddtSchemes { default localEuler; }` —
  LTS pseudo-time-stepping. `warmup20_bounded_realtime/system/fvSchemes` has
  `default Euler;` — real time-accurate. Read on disk today; that one entry is
  the whole difference between the two directories' `system/`.
- **Every number this experiment must reproduce or beat comes from the
  time-accurate case.** The `~12 %` bounded fraction at `t ≈ 1.9e-05 s` that
  §8.9's prediction is written against is the `zeroGradient` real-time case
  (parent record, "The farfield-shock-reflection hypothesis" section). The
  `≈30 %` end-state figure and the `ExecutionTime = 279.93 s` cost basis are the
  same run (parent record, "The invariant corner cell, and the LTS test", table).
- The parent record's own corrected verdict is that the LTS reading was an
  artifact for the corner cell's frozen *value*. Grading a discrimination
  experiment on the arm already known to carry an artifact would be a choice
  against the evidence.

**Step 0 and Step 1 therefore both use the `warmup20_bounded_realtime`
configuration** (`Euler`, corrected mesh grading, Table II inlet profile,
`farfield` `zeroGradient`).

### 1.2 Neither step may run in an existing case directory — both are fresh copies

`warmup20`, `warmup20_bounded`, `warmup20_bounded_realtime` and
`warmup20_bounded_farfield` are **evidence and are read-only for the whole of
this experiment.** Nothing in them is written, moved, renamed or deleted. Each
currently holds exactly one time directory, `0/`, verified on disk today; the
strict completion rule's age guard (§7) is meaningless in a directory that
already carries a result, and rule 4's guard refuses a case where a time
directory already exists.

### 1.3 `endTime 1.0` is unreachable and would make rule 4 unsatisfiable

The inherited `controlDict` carries `endTime 1.0;` with `deltaT 1e-9` and
`maxDeltaT 1e-6`. The reference run reached `t = 6.51e-05 s` in 279.93 wall-s;
`t = 1.0 s` is roughly four orders of magnitude further and is not reachable in
this or any budget. Every prior run of this case was therefore stopped by an
external `timeout` wrapper, which means **no run of this case has ever satisfied
rule 4's "last time == `endTime`" clause, and none ever could.** A diagnostic
that cannot complete cannot be graded.

`endTime` is therefore set to a **reachable** value, `6.5e-05`, chosen as the
largest round value at or below the `6.51e-05 s` the reference run actually
reached, so that the cost projection in §10 is bounded above by a wall time the
box has already demonstrated. This is a **shared diagnostic setting applied
identically to both steps**, not a variable between them.

### 1.4 `writeInterval 1e-3` would write no fields at all — and rule 4 needs them

With `writeControl adjustable; writeInterval 1e-3;` and `endTime 6.5e-05`, the
first write time (`1e-3`) lies past the end of the run. **No field would ever be
written**, so rule 4's "fields present at `endTime`" and its age guard would both
be unsatisfiable — this box's own recorded trap (`memory:
openfoam-restart-watcher-traps`, "non-`writeInterval` `endTime` writes no
fields"). `writeInterval` is set to `1.3e-05`, giving exactly five writes at
`1.3e-05, 2.6e-05, 3.9e-05, 5.2e-05, 6.5e-05` with `6.5e-05 = 5 × 1.3e-05`
landing exactly on `endTime`. `purgeWrite 3` is unchanged, so `3.9e-05`,
`5.2e-05` and `6.5e-05` survive — and `3.9e-05` is the pre-declared truncation
checkpoint of §7.2. Also a **shared** setting, identical in both steps.

### 1.5 Step 1 as briefed is a no-op or a physics violation on **every** patch of
this case, except the inlet — and it is re-specified to the inlet only

The brief and §8.9 specify Step 1 as: overwrite the **non-coupled boundary
patches** of the `_pos` fields with `patchInternalField()`, leaving `_neg` at the
patch value. Applied to all seven patches of this case, that is not a
single-variable numerics probe. Patch by patch, from the source read (line
numbers are `rhoCentralFoamBounded_src/rhoCentralFoamBounded.C`, which is
byte-identical to stock `rhoCentralFoam.C` in this region except for the two
`#include "boundE.H"` lines at `:267` and `:282`):

| patch | type | effect of the briefed overwrite | why |
|---|---|---|---|
| `farfield` (270 faces) | `patch`, `zeroGradient` on `U,T,p,k,omega` | **exact no-op** | `zeroGradient`'s patch value *is* `patchInternalField()`. Overwriting a value with itself changes nothing, bit for bit. |
| `outlet` (110 faces) | `patch`, `zeroGradient` | **exact no-op** | same |
| `axis` (0 faces) | `empty` | **no-op** | `nFaces 0` |
| `wall` (270 faces) | `wall`, no-slip `U=0`, isothermal `T=311 K`, `p` `zeroGradient` | **discrete mass leak through a solid wall — physics violation** | see algebra below |
| `frontWedge`/`backWedge` (29,700 faces each) | `wedge` | **axisymmetry violation touching all 29,700 cells** | see below |
| `inlet` (110 faces) | `patch`, `fixedValue` (Table II profile on `U`,`T`; uniform 576 Pa on `p`) | **the only live, legitimate lever** | see §5 |

**The wall leak, as algebra.** At a no-slip wall face `U_b = 0`, so
`phiv_b = U_b · Sf = 0` and (`:149–165`) `ap = c_b|Sf| > 0`,
`am = −c_b|Sf| < 0`, `a_pos = 1/2`, `aSf = −c_b|Sf|/2 ≠ 0`. With `pos == neg`
(the present behaviour) `:196` gives
`phi = (a_pos·0 − aSf)·rho_b + (a_neg·0 + aSf)·rho_b = 0` — **the exact
cancellation is what makes the discrete wall impermeable.** Set
`rho_pos = rho_internal ≠ rho_b` and the same line gives
`phi = aSf·(rho_b − rho_internal) ≠ 0`: mass crosses a solid wall every timestep.
The `pos == neg` identity at a wall is not a dissipation *deficit*; it is the
no-penetration boundary condition, discretely enforced. Restoring an "upwind
bias" there does not probe the numerics, it breaks the case.

**The wedge violation.** Every one of the 29,700 cells has two `wedge` faces. A
`wedge` patch value is the internal value transformed into the neighbouring
wedge plane; replacing it with the untransformed `patchInternalField()` on the
`_pos` side changes the flux on 59,400 faces — i.e. on **every cell in the
mesh**, not on the boundary-adjacent cells the hypothesis is about. That is a
global scheme change, and it would confound the very thing being isolated.

**Step 1 is therefore re-specified to the `inlet` patch only** (§5), which is
also the sharpest statement the parent record makes: §8.5's own conclusion is
*"a cell whose undissipated boundary faces include a `fixedValue` inlet."* The
scope this costs is declared in §9.3 and is not glossed: **this experiment does
not test the wedge-face or wall-face dissipation identity at all**, and a null
result eliminates only the inlet-face variant.

---

## 2. Evidence base — every number and threshold below is read from these

| Artifact | Path | md5 | On disk today |
|---|---|---|---|
| Original SIGFPE crash log (stock solver) | `demo-output/website/solve_registry/f4_swbli_warmup20_20260730T004453Z.log` | `b658b967377d574d8aacf00e3569cf9c` | yes, 2,174,951 bytes |
| Guard source (published solver) | `verification/runs/F4_runs/swbli_cylflare/rhoCentralFoamBounded_src/boundE.H` | `3c30480673b4b443ccc5ce7cceb53671` | yes |
| Solver source (published solver) | `.../rhoCentralFoamBounded_src/rhoCentralFoamBounded.C` | `b2d49a388a791da7830a03c7487b08db` | yes |
| Thermo-bound derivation | `.../rhoCentralFoamBounded_src/createFields.H` | `a7f08e8fa7c069a82f8b5e21f20c27b7` | yes |
| Control case `controlDict` | `.../warmup20_bounded_realtime/system/controlDict` | `d1a144790d89f4c5ebcf1a9a5691d87e` | yes |
| Control case `fvSchemes` | `.../warmup20_bounded_realtime/system/fvSchemes` | `c1d02c9c57813ad4d05fa48cf55f2382` | yes |
| Build procedure | `docs/OPENFOAM_SOLVER_BUILD.md` §4, §5 | — | yes |

### 2.1 The artifact that is NOT on disk, and what that costs this experiment

**Every `BOUND:` log from every bounded run of this case is gone** (parent record
§8.8; re-verified today — `grep -rl "BOUND: e" --include=*.log .` returns
nothing, and the surviving crash log contains **0** `BOUND:` lines, as expected
since it is the *stock* solver). Consequently:

- The `4 %`, `12 %`, `17 %`, `~22 %`, `~30 %`, `~32 %` bounded fractions, the
  worst-`e` values (`−199,551.388`, `−199,524.67…86`, `−211,681.775`), the
  clamped-region extents, **and the `ExecutionTime = 279.93 s` / `t = 6.51e-05 s`
  timing basis this document costs itself against** are all **record-quoted, not
  artifact-backed.** They are quoted from the parent record's prose.
- **`cost_basis` is therefore `record-quoted, artifact-missing`** — weaker than
  measured, and stated that way in §10 rather than dressed up.
- **Recreating that artifact is Step 0's first purpose.** Step 0 is not only a
  control; it is the run that puts the record's own headline number back on disk.

---

## 3. The shared configuration (identical in both steps — not a variable)

Both steps are **fresh directories**, built by copying the control case:

```
STEP0=verification/runs/F4_runs/swbli_cylflare/step0_instrumented
STEP1=verification/runs/F4_runs/swbli_cylflare/step1_inletupwind
SRC=verification/runs/F4_runs/swbli_cylflare/warmup20_bounded_realtime

mkdir -p $STEP0 $STEP1
for D in $STEP0 $STEP1; do
  cp -r $SRC/0 $SRC/constant $SRC/system $D/
done
```

Copying, not regenerating from `make_swbli_case.py`, is required for the steps to
be honest controls: the `0/U` and `0/T` inlet profiles are the
`build_inlet_profile.py`-derived Table II `nonuniform List`s mapped onto the
*actual* face order, and a regenerated case is not guaranteed to reproduce them
byte for byte. `constant/polyMesh` is 6.3 MB per step, 12.6 MB total.

**Common `system/controlDict` edits, applied identically to both steps** — these
are the shared diagnostic setting of §1.3/§1.4, not the variable:

```
endTime         6.5e-05;    // was: 1.0        (§1.3 — reachable, so rule 4 can hold)
writeInterval   1.3e-05;    // was: 1e-3       (§1.4 — so fields exist at endTime)
```

Everything else in `controlDict` is untouched: `startFrom startTime`,
`startTime 0`, `stopAt endTime`, `deltaT 1e-9`, `writeControl adjustable`,
`purgeWrite 3`, `writeFormat ascii`, `writePrecision 9`, `timeFormat general`,
`timePrecision 9`, `adjustTimeStep yes`, `maxCo 0.3`, `maxDeltaT 1e-6`,
`TMin 20.0`, `TMax 5000.0`, and both function objects (`wallShear`, `yPlus1`).
`0/`, `constant/` and `system/fvSchemes`/`system/fvSolution` are **untouched in
both steps.**

**`application` is the one line that differs between the steps**, and it is the
variable:

| step | `controlDict` `application` |
|---|---|
| Step 0 | `rhoCentralFoamBoundedDiag` |
| Step 1 | `rhoCentralFoamInletUpwindDiag` |

**One change per run, asserted, not asserted-about.** Before either launch:

```
diff -r $SRC/0        $D/0          # must be EMPTY
diff -r $SRC/constant $D/constant   # must be EMPTY
diff -r $SRC/system   $D/system     # must show EXACTLY the three lines above
                                    # (endTime, writeInterval, application) and nothing else
diff -r $STEP0/system $STEP1/system # must show EXACTLY the `application` line
```

A diff that is not exactly this **stops the step before launch** and is reported,
not adjusted around. Output is saved to `<STEP>/PRELAUNCH_DIFF.txt` and cited in
the results record. Both steps are single core (`nProcs : 1`), matching every
prior run of this case.

---

## 4. Step 0 — the instrument. Exactly which lines change, and why they cannot
alter the solution

### 4.1 The build

A **new** source tree,
`verification/runs/F4_runs/swbli_cylflare/rhoCentralFoamBoundedDiag_src/`, copied
from `rhoCentralFoamBounded_src/` (md5s in §2). **`rhoCentralFoamBounded_src/` is
not edited** — it is the published solver behind published results
(`docs/OPENFOAM_SOLVER_BUILD.md` §2, §6) and rule 6 applies. Changes in the new
tree, and only these:

1. `Make/files`: `EXE = $(FOAM_USER_APPBIN)/rhoCentralFoamBoundedDiag` (was
   `…/rhoCentralFoamBounded`). Target rename only, so the published binary is not
   overwritten.
2. `rhoCentralFoamBoundedDiag.C`: renamed from `rhoCentralFoamBounded.C`, with
   `Make/files` line 1 updated to match. **The file's contents are unchanged**,
   including both `#include "boundE.H"` sites at `:267` and `:282`.
3. `boundE.H`: instrumented as in §4.2.

Built per `docs/OPENFOAM_SOLVER_BUILD.md` §4 (copy into
`$WM_PROJECT_USER_DIR/applications/solvers/compressible/`, then
`openfoam2606 -c 'cd … && wmake'`). Because the target name differs, none of the
four published artifacts in that document's §6 table is overwritten, so its §5
`HOME`-redirection dance is not needed. **The build is recorded in the results
record with: the `wmake` exit code, the resulting binary's path, byte size and
md5, and `openfoam2606 -c 'rhoCentralFoamBoundedDiag -help' | head -2`.**

### 4.2 The instrument — every added statement, and the argument that it is inert

`boundE.H` today (52 lines, md5 `3c30480673b4b443ccc5ce7cceb53671`) opens a
block, takes `const scalarField& eIn = e.primitiveField();`, walks `forAll(eIn,
celli)` accumulating counts/worst/extent into local `label` and `scalar`
variables, emits at most two `Info<<` lines, and its **final and only
field-assigning statement** is `:51`:

```cpp
    e = min(max(e, eMin_bound), eMax_bound);
```

The instrumented version adds, and only adds:

```cpp
    // ADDED: read-only handles. rho and U are CURRENT at this point --
    // rho is advanced at :225 (continuity), U at :229-245 (momentum +
    // viscous correction), both before :265. T is NOT current: thermo.correct()
    // has not yet run for this step, so T lags by one correction. Reported
    // as T_prev and never as the clamped cell's temperature.
    const scalarField& rhoIn = rho.primitiveField();
    const vectorField& UIn   = U.primitiveField();
    const scalarField& TIn   = T.primitiveField();

    // ADDED: exact hConst inversion of the CURRENT e -- T = Tref + e/Cv,
    // with Cv_bound and Tref_bound the same constants createFields.H:110-123
    // already uses to build eMin_bound. This is the clamped cell's real
    // temperature; TIn is not.
    // ADDED: 12 fixed histogram bin edges on implied T, in K:
    //   (-inf,0] (0,1] (1,2] (2,5] (5,10] (10,15] (15,18] (18,19] (19,19.5]
    //   (19.5,19.9] (19.9,19.99] (19.99,20)
    // ADDED: per-clamped-cell min/max accumulators for rhoIn, mag(UIn), TIn,
    //   and the worst-low cell's rhoIn / mag(UIn) / TIn / implied T.

    // ADDED: two Info lines, tagged so a reader cannot confuse them with the
    // existing ones:
    //   "BOUNDDIAG: t=<time> nLow=<n> rhoLow=[<min>,<max>] magULow=[<min>,<max>]
    //    TprevLow=[<min>,<max>] worst: cell=<c> rho=<v> magU=<v> Tprev=<v> Timp=<v>"
    //   "BOUNDHIST: t=<time> nLow=<n> bins=<b0> <b1> ... <b11>"
```

**Why no added statement can alter the solution, clause by clause:**

1. Every added handle is a `const` reference obtained from `primitiveField()`.
   `primitiveField()` on a `volField` returns `const Field<Type>&`; there is no
   non-const path from any of them.
2. Every added write target is a function-local `label`, `scalar`,
   `Foam::FixedList<label,12>` or `Foam::vector` declared inside the same
   enclosing `{ … }` block. None outlives it. None is a field, a dimensioned
   quantity, a mesh object or a `runTime` entry.
3. The only field-assigning statement in the file remains `:51`'s clamp, and it
   remains the **last** statement in the block. Its right-hand side is
   `min(max(e, eMin_bound), eMax_bound)` — unchanged operands, unchanged bounds,
   both `eMin_bound` and `eMax_bound` still built in `createFields.H` from
   `TMin`/`TMax` read out of `controlDict`, both unchanged at `20.0` / `5000.0`.
4. `Info<<` writes to `stdout` only. It is not a reduction, not a synchronisation
   point, and both runs are serial (`nProcs : 1`) so no `reduce()` is introduced
   or needed.
5. No `#include` site moves: `rhoCentralFoamBoundedDiag.C` still includes
   `boundE.H` at exactly `:267` and `:282` and nothing else about that file
   changes.
6. No `Make/options` entry changes, so the same libraries link in the same order.

**This is an argument, not a measurement, and it is labelled as one.** It is
converted into a measurement by control **C0** in §6.

### 4.3 What Step 0 is for

1. **Recreate the missing artifact.** A `BOUND:` log on disk, at a known commit,
   for a run whose configuration is fully specified here.
2. **Settle the `TMin = 20 K` threshold-artifact question (§8.6(1) of the parent
   record).** The `BOUNDHIST:` histogram answers it directly and costs nothing
   beyond the run.
3. **Identify which quantity goes bad first.** `rho`, `|U|` and implied `T` are
   reported for every clamp event, so a `rho` collapse or a `|U|` overshoot can
   be distinguished from a genuine energy defect — the gap §8.7 names.
4. **Be the matched control for Step 1.**

---

## 5. Step 1 — the discriminator. The exact source diff, before the run

### 5.1 What is changed

A second new source tree,
`verification/runs/F4_runs/swbli_cylflare/rhoCentralFoamInletUpwindDiag_src/`,
copied from `rhoCentralFoamBoundedDiag_src/` (Step 0's tree, so **the instrument
is bit-identical between the two steps and is not a second variable**), with
`Make/files` retargeted to `rhoCentralFoamInletUpwindDiag`, the `.C` renamed to
match, and exactly one functional change: a new header
`inletUpwindPos.H`, included by exactly one added line placed immediately after
the `cSf_neg` construction (after `:147` of the Step-0 `.C`, i.e. after every
`_pos`/`_neg` surface field this loop iteration uses has been formed and before
`ap` is built at `:149`):

```cpp
        surfaceScalarField cSf_neg
        (
            "cSf_neg",
            interpolate(c, neg, T.name())*mesh.magSf()
        );

+       #include "inletUpwindPos.H"    // <-- THE ONLY FUNCTIONAL CHANGE
+
        surfaceScalarField ap
```

`inletUpwindPos.H`, in full:

```cpp
// STEP 1 DISCRIMINATOR (F4_SIGFPE_STEP01_PREREGISTRATION.md §5).
// Restore an upwind bias at the fixedValue supersonic INLET patch only, by
// replacing the _pos face states there with the owner cell's own values while
// leaving the _neg states at the patch value. Everywhere else -- every internal
// face, and every other patch -- nothing is touched.
//
// Scope, and why it is the inlet ONLY: at a no-slip wall the pos==neg identity
// is what makes phi vanish, so breaking it leaks mass through a solid wall; on
// the zeroGradient farfield/outlet patchInternalField() IS the patch value, so
// the overwrite is an exact no-op; on the two wedge patches it would change the
// flux on every one of the 29,700 cells. See the prereg's §1.5 table.
{
    const label inletPatchi = mesh.boundaryMesh().findPatchID("inlet");

    // Refuse rather than silently do nothing: a missing or empty inlet patch
    // would make this arm a null-by-construction, which is exactly the failure
    // mode control C2 exists to catch.
    if (inletPatchi < 0 || mesh.boundary()[inletPatchi].size() == 0)
    {
        FatalErrorInFunction
            << "STEP1: inlet patch not found or empty -- refusing to run a "
            << "discriminator whose lever cannot act." << exit(FatalError);
    }

    rho_pos.boundaryFieldRef()[inletPatchi] =
        rho.boundaryField()[inletPatchi].patchInternalField()();

    rhoU_pos.boundaryFieldRef()[inletPatchi] =
        rhoU.boundaryField()[inletPatchi].patchInternalField()();

    rPsi_pos.boundaryFieldRef()[inletPatchi] =
        rPsi.boundaryField()[inletPatchi].patchInternalField()();

    e_pos.boundaryFieldRef()[inletPatchi] =
        e.boundaryField()[inletPatchi].patchInternalField()();

    // Derived _pos states must be rebuilt from the overwritten primitives,
    // or U_pos and p_pos would still carry the patch state.
    U_pos.boundaryFieldRef()[inletPatchi] =
        rhoU_pos.boundaryField()[inletPatchi]
      / rho_pos.boundaryField()[inletPatchi];

    p_pos.boundaryFieldRef()[inletPatchi] =
        rho_pos.boundaryField()[inletPatchi]
      * rPsi_pos.boundaryField()[inletPatchi];

    // Wave speed must follow the state it belongs to, or ap/am are inconsistent.
    cSf_pos.boundaryFieldRef()[inletPatchi] =
        c.boundaryField()[inletPatchi].patchInternalField()()
      * mesh.magSf().boundaryField()[inletPatchi];

    // phiv_pos was formed from U_pos at :121-123 and must be re-formed.
    phiv_pos.boundaryFieldRef()[inletPatchi] =
        U_pos.boundaryField()[inletPatchi]
      & mesh.Sf().boundaryField()[inletPatchi];
}
```

**Nothing else in the solver changes.** `_neg` is untouched on every patch.
Internal faces are untouched on every field. `boundE.H` is bit-identical to Step
0's. The `#include "boundE.H"` sites do not move.

**The exact diff to be produced and quoted in the results record before the run
is believed:**

```
diff -u rhoCentralFoamBoundedDiag_src/rhoCentralFoamBoundedDiag.C \
        rhoCentralFoamInletUpwindDiag_src/rhoCentralFoamInletUpwindDiag.C
diff -u rhoCentralFoamBoundedDiag_src/boundE.H \
        rhoCentralFoamInletUpwindDiag_src/boundE.H          # must be EMPTY
diff -u rhoCentralFoamBoundedDiag_src/Make/files \
        rhoCentralFoamInletUpwindDiag_src/Make/files
diff -u rhoCentralFoamBoundedDiag_src/Make/options \
        rhoCentralFoamInletUpwindDiag_src/Make/options      # must be EMPTY
```

The first diff must show **exactly** the one added `#include` line (plus the
blank line) and nothing else. Anything more stops the step.

### 5.2 The pre-declared prediction that the lever is inert in the supersonic core

This is not a caveat found afterwards; it is arithmetic from `:149–165` and it is
frozen here.

At an inlet face, `Sf` points out of the domain (upstream), so for freestream
inflow `phiv = U·Sf < 0`. With `Cp = 1005`, `molWeight = 28.9`:
`R = 8314.47/28.9 = 287.699`, `Cv = 717.302`, `γ = 1005/717.302 = 1.40109`. At
`T∞ = 81.2 K`, `c∞ = √(1.40109 × 287.699 × 81.2) = 180.9 m/s`, so
`M∞ = 1274/180.9 = 7.04` — the Table I value, recovered.

Where **both** the patch state and the interior state are supersonic relative to
`Sf` (i.e. `phiv + cSf < 0` for both), `ap = max(max(·,·), 0) = 0`, hence
`a_pos = ap/(ap − am) = 0` **exactly**, hence `aSf = am·a_pos = 0` **exactly**,
hence `aphiv_pos = a_pos·phiv_pos − aSf = 0`. **The `_pos` state drops out of
every flux.** So over the supersonic core of the inlet — the great majority of
its 110 faces — Step 1 is a *bit-exact no-op*, and that is correct behaviour, not
a defect: a supersonic inflow has no outgoing characteristic to bias.

The lever becomes live only where the Table II profile is subsonic — the
near-wall faces, where `phiv_pos + cSf_pos > 0` gives `ap > 0`, `a_pos > 0`,
`aSf ≠ 0`. **Those are exactly the cells the parent record names**: all four
persistently-clamped cells (`0`, `3960`, `6360`, `13080`) are multiples of 120,
i.e. in the inlet-adjacent column (§8.5), and `13080` is the inlet∩wall corner.

**Consequence, frozen:** a Step 1 whose log is bit-identical to Step 0's is
**not** evidence about the mechanism — it is evidence the lever never acted.
Control **C2** (§6) makes that distinction mandatory rather than optional.

---

## 6. Positive controls — required, and passing BEFORE anything is graded
(standing rule 3)

**A zero from a reader not shown able to see a non-zero is not evidence**, and
this experiment's headline reads are counts. The grading reader
`verification/runs/F4_runs/swbli_cylflare/analyse_f4_sigfpe_step01.py`
**refuses to grade any step (exit 2) unless every control below reproduces in the
same invocation.** No control is advisory.

**C0 — the instrument is inert, measured rather than argued (§4.2).** Before
Step 0 is graded, build the Step-0 solver **and** the unmodified published
`rhoCentralFoamBounded` and run both from the same fresh `0/` for the first
**200 timesteps** into two throwaway directories. Assert: the `Time = `,
`Courant Number mean/max`, and `ExecutionTime`-adjacent residual lines agree, and
the existing `BOUND: e below eMin in N cell(s)` lines agree **exactly** in `N`,
in worst-`e` to all printed digits, and in worst cell index, at every step where
either fires. **If they disagree anywhere, the instrument is not inert and Step 0
does not run.** Cost is inside the §10 build allowance (200 steps of a `dt≈1e-8`
run is a few seconds each). This converts §4.2's argument into evidence.

**C1 — the clamp reader sees a known non-zero, from a committed fixture.** No
`BOUND:` log exists anywhere on this box (§2.1), so the non-zero cannot come from
the archive. It comes from a hand-written fixture committed with the reader:
`verification/runs/F4_runs/swbli_cylflare/fixtures/bound_log_fixture.txt`,
containing a known set of `BOUND:`, `BOUNDDIAG:` and `BOUNDHIST:` lines
interleaved with `Time = `/`ExecutionTime` lines. Expected, exactly, and asserted
by the reader against values written into the fixture *and* into the reader's
`EXPECTED` table: **3 clamp events, at `t = 1e-08, 2e-08, 3e-08`, with
`nLow = 7, 55, 411`, worst-`e` `−199600.5, −201234.75, −211681.775`, worst cells
`0, 3960, 13080`, and histogram row sums equal to `nLow` at every event.** The
fixture is **committed before compute** and its md5 is quoted in the results
record.

**C2 — the reader can tell Step 1's log apart from Step 0's, and refuses if it
cannot.** Given §5.2, a bit-identical pair is a live possibility and must not be
allowed to read as "no effect on the clamp population". The reader computes an
`md5` of each step's log with `ExecutionTime` and wall-clock lines stripped, and:
- identical ⇒ the reader emits label **`LEVER-INERT`** and **refuses to grade the
  discrimination question** (exit 3). The step is reported, the mechanism is not.
- different ⇒ grading proceeds, and the results record quotes the first differing
  `Time = ` block.

**C3 — the counter returns zero on a log known to have no clamp lines.** Run the
identical counting function on
`demo-output/website/solve_registry/f4_swbli_warmup20_20260730T004453Z.log`
(md5 `b658b967377d574d8aacf00e3569cf9c`, asserted before reading). Expected:
**0** `BOUND:` lines. That log is the *stock* solver's, so zero is the correct
answer — and it is admissible **only** because C1 in the same invocation returned
3 on a file that has 3.

**C4 — the plant, into each step's OWN log (rule 3, and `memory:
a-zero-needs-a-live-planted-control`).** C1–C3 prove the reader works on files it
did not just produce. They do not prove it is reading *this step's* file. So, per
step, before that step's numbers are computed:
- copy `<STEP>/log.<solver>` to a scratch path (unique to the invocation);
- insert, **by line index** (immediately after the `Time = ` line of the 5th
  timestep block), one line:
  `BOUND: e below eMin in 424242 cell(s) at Time = <that block's time>, worst e = -299999.125 J/kg at cell 12345 C = (9.9 9.9 9.9) | low-e cell extent: x=[9.9,9.9] r=[9.9,9.9]`
  and one line
  `BOUNDHIST: t=<that block's time> nLow=424242 bins=424242 0 0 0 0 0 0 0 0 0 0 0`;
- run the reader on the copy and assert it reports `nLow_max = 424242`,
  `worst_e = -299999.125`, `worst_cell = 12345`, and bin 0 = 424242.
- **The step's real log is never modified**; the plant lives only in the scratch
  copy. **If the reader cannot see the plant in that step's own file, that step is
  not graded.**

The full control output is written to `<STEP>/POSITIVE_CONTROL.txt` and quoted in
the results record. **A results record that does not quote it is incomplete.**

**The reader is committed before compute, and its diff is the supervisor's to
read.** The reader is a measurement script; `SUPERVISION_CHARTER.md` §3 makes
reading its diff *as a diff* a supervisor personal check that may not be
delegated. Nothing it outputs is believed before that read.

### 6.1 The controls that could be run at freeze WERE run, and were mutated

C1 and C3 need no solver, so they were exercised at freeze (zero solver compute,
pure file reads):

- `analyse_f4_sigfpe_step01.py --selftest` → **exit 0**. C1 read
  **3 clamp events** from the fixture with `nLow = 7, 55, 411`, worst-`e`
  `−199600.5 / −201234.75 / −211681.775`, worst cells `0 / 3960 / 13080`, lowest
  occupied histogram bins `9 / 6 / 3`, and every histogram row summing to its own
  `nLow`. C3 read **0** clamp events from the archived stock-solver crash log
  after asserting its md5 `b658b967377d574d8aacf00e3569cf9c`.
  Fixture md5 at freeze: **`60f6d5802793f7bd2cbfa5fde3dafbcb`**.
- **A passing control is not evidence that the control can fail.** Six
  mutations were injected into scratch copies of the fixture — a broken histogram
  sum, a changed `nLow`, a changed worst cell, a changed worst `e`, a bin
  ordering inconsistent with the worst implied `T`, and a deleted `BOUND:` line.
  **All six were caught; zero survived**, and the unmutated fixture still passed
  afterwards (`__pycache__` cleared first — `memory:
  stale-pycache-inverts-mutation-tests`). The mutations lived only in a scratch
  directory, which was removed; the committed fixture is untouched.

C0, C2 and C4 need run logs and are therefore **`PENDING`** at freeze — stated as
`PENDING`, not implied to have passed.

---

## 7. Completion — a step is graded only if its run finished (standing rule 4)

### 7.1 `COMPLETE`

Per step, all of:

- solver `rc = 0`;
- an `End` line in the log;
- **last `Time = ` in the log == `endTime` == `6.5e-05`**;
- `ExecutionTime` line count == the number of timesteps the log reports (this
  case is `adjustTimeStep yes`, so the count is not a fixed number known in
  advance; the clause is that every `Time = ` block carries exactly one
  `ExecutionTime` line, checked pairwise, and that the counts are equal);
- fields `T U p alphat k nut omega` present under `6.5e-05/`;
- **every field under `6.5e-05/` newer than that step's own `0/T`** — the age
  guard. `0/` is copied at step construction and `0/T` is touched last before
  launch, so it dates the run allowed to produce the answer.

A guard refuses to launch into a directory where any numeric time directory other
than `0` already exists.

### 7.2 `TRUNCATED-AT-CAP` — pre-declared now, so it is not a post-hoc rescue

The §10 cap is only 1.29× the projection, and the box is shared. If a step is
stopped **at the cap** (rule 12: an overrun stops the run; it does not get a new
budget) then:

- **if** its log's last `Time = ` is `≥ 3.9e-05` **and** `3.9e-05/` exists with
  all seven fields present and every one newer than that step's own `0/T`, the
  step is **`TRUNCATED-AT-CAP`** and is graded on the window `[0, 3.9e-05]`, with
  every §8 clause evaluated at `3.9e-05` instead of `6.5e-05`. Its label carries
  the suffix `(TRUNCATED)` everywhere it appears.
- **otherwise** the step is **`BLOCKED`**.

`3.9e-05` is fixed here, before compute, as the third write time (§1.4) and as
2.05× the `t ≈ 1.9e-05 s` comparison point the prediction is written against. It
is not chosen after seeing a log, and it may not be moved.

**Both steps must carry the same status** for the discrimination question to be
answered: a `COMPLETE` step compared against a `TRUNCATED-AT-CAP` step is not a
matched comparison, and in that case **both** are re-read on the `[0, 3.9e-05]`
window and both labels carry `(TRUNCATED)`.

### 7.3 `SIGFPE-RECURRENCE` — a crash is a measured outcome here, not a hole (L-255)

**This is the clause L-255 was written to demand.** The subject of this
experiment is a SIGFPE and a clamp population; a step may itself die. A generic
crash → `BLOCKED` rule would route the most informative outcome into an empty
cell, which is exactly what it cost the DPW8_V2 L4 diagnosis.

A step is labelled **`SIGFPE-RECURRENCE`** — a *measured outcome*, distinct from
`BLOCKED` — if its solver terminates on a floating-point exception (log carries a
`Foam::sigFpe` / `Floating point exception` backtrace, or `rc` is 136/`SIGFPE`),
**and** the pre-crash log satisfies:

- at least **200** `Time = ` blocks before the crash (so the clamp population has
  a trend, not a single point), and
- at least one field write (`1.3e-05/`) present and newer than that step's `0/T`.

Its clauses are then evaluated on the **truncated pre-crash window**, and the
results record states the crash time, the last `BOUND:`/`BOUNDDIAG:` line before
it, and which of `rho`, `|U|`, `e` was extreme there. A step that crashes with
fewer than 200 blocks or with no field write is **`BLOCKED`**, and goes to the
supervisor for triage (a crash is a finding until triage says otherwise —
`SUPERVISION_CHARTER.md` §3).

A step that does **not** take a floating-point exception is labelled
**`SIGFPE-ABSENT`**. Both steps carry one of these two labels unconditionally, so
neither absence nor presence of a crash can go unrecorded.

### 7.4 `BLOCKED`

Anything else — non-zero `rc` without SIGFPE, no `End` line, missing fields, a
field older than the step's own `0/T`, a failed pre-launch diff (§3), a failed
control (§6), or a cap stop below `3.9e-05`. **`BLOCKED` is a statement about the
run, never about the physics** (L-255's corollary).

---

## 8. Pre-declared measurement clauses and labels

All fractions are `nLow / 29700`, read from the `BOUND:`/`BOUNDDIAG:` lines, at
the `Time = ` block whose time is nearest `1.9e-05` from below (call it `t*`) and
at the window end (`6.5e-05`, or `3.9e-05` under §7.2).

### 8.1 Step 0 — `BASELINE-RECOVERED` / `BASELINE-NOT-RECOVERED`

Step 0 is **`BASELINE-RECOVERED`** iff **both**:

- **S0a** — bounded fraction at `t*` is within **[6 %, 24 %]**, i.e. the
  record-quoted `~12 %` within a factor of two either way;
- **S0b** — bounded fraction at the window end is **≥ S0a's value**, i.e. the
  population is not shrinking over the window.

*Justification for the band.* The `~12 %` and `~30 %` figures are
record-quoted with **no surviving artifact** (§2.1), and the window end here
(`6.5e-05`) differs from the figure's origin. A tight band would be asserting
precision the evidence does not have. A factor of two is wide enough that
reproducing the record's own order of magnitude passes and a qualitatively
different run fails. **Set now, before the run, and not movable after.**

Otherwise **`BASELINE-NOT-RECOVERED`**, and §9 says what that licenses.

### 8.2 The free read — `THRESHOLD-ARTIFACT` / `GENUINE-DIVERGENCE` / `MIXED`

From Step 0's `BOUNDHIST:` line at the window end, over the clamped population:

- **`THRESHOLD-ARTIFACT`** if **≥ 80 %** of clamped cells have implied
  `T ∈ (19.5, 20) K`;
- **`GENUINE-DIVERGENCE`** if **≥ 20 %** have implied `T ≤ 10 K`;
- **`MIXED`** otherwise.

*Justification.* The parent record §8.6 already inverts three quoted worst-`e`
values to `19.95 K`, `19.99 K` and `3.04 K` — the population straddles both
regimes at its extremes, so the question is genuinely about the *bulk*. 80 % and
20 % are set far enough apart that both labels cannot fire, and the residual is
named `MIXED` rather than forced. This read costs **zero additional compute**.

### 8.3 The attribution read — `RHO-FIRST` / `U-FIRST` / `E-FIRST` / `INDETERMINATE`

From Step 0's `BOUNDDIAG:` lines, at the **first** timestep where `nLow > 0`, for
the worst-low cell, relative to the freestream reference state
(`rho∞ = 0.0252 kg/m³`, `|U|∞ = 1274 m/s`, `T∞ = 81.2 K`; NASA TM 101075 Table I,
quoted in the parent record §7a):

- **`RHO-FIRST`** if `|rho/rho∞ − 1| > 0.10` while `||U|/|U|∞ − 1| ≤ 0.05`;
- **`U-FIRST`** if `||U|/|U|∞ − 1| > 0.05` while `|rho/rho∞ − 1| ≤ 0.10`;
- **`E-FIRST`** if both are within their bands — i.e. `rho` and `U` are both
  near-freestream and the energy is nonetheless out of range;
- **`INDETERMINATE`** if both are outside their bands.

*Justification for `5 %` on `|U|`.* Parent record §8.6(3): reaching `T = 19.95 K`
needs `|U|` high by **2.71 %**, and `T = 3.04 K` by **3.45 %**. A 5 % threshold
therefore sits **above** the velocity error that alone suffices to produce the
observed clamps, so `U-FIRST` firing means the velocity error is larger than the
whole explanation requires — a strong, not a marginal, reading. The 10 % on `rho`
is the corresponding round figure on the density side of the same
`e = rhoE/rho − ½|U|²` cancellation (§8.6(3): a 6.70 % deficit in `rhoE/rho`
reaches 19.95 K). **These bands cannot be renegotiated after the run.**

### 8.4 Step 1 — `DEFICIT-IMPLICATED` / `DEFICIT-NOT-IMPLICATED`

Evaluated **only** if C2 (§6) reports the logs differ, and only against a Step 0
of the same completion status (§7.2).

Step 1 is **`DEFICIT-IMPLICATED`** iff **both**:

- **S1a** — Step 1's bounded fraction at `t*` is **below 0.60 ×** Step 0's
  bounded fraction at the same `t*`;
- **S1b** — the growth flattens: Step 1's bounded fraction at the window end is
  **< 1.5 ×** its own value at `t*`, whereas Step 0's window-end value is
  **≥ 1.5 ×** its own `t*` value.

Otherwise **`DEFICIT-NOT-IMPLICATED`**.

*Justification.* §8.9's frozen prediction is "**materially** below the ~12 %
baseline **and** the growth flattens". `0.60 ×` is the operationalisation of
"materially" and is set as a **ratio against Step 0's own measured value**, not
against the record-quoted 12 %, precisely because §2.1 shows that 12 % has no
surviving artifact. `1.5 ×` operationalises "flattens" and is required of **both**
steps in opposite directions, so a run in which neither grows cannot read as a
flattening. Both numbers are frozen here.

---

## 9. Pre-declared outcome map — what each result licenses, and what it does not

### 9.1 The main map

| Step 0 | Step 1 | Diagnosis conclusion, and its limit |
|---|---|---|
| `BASELINE-RECOVERED` | `DEFICIT-IMPLICATED` | The **inlet-face zero-dissipation identity (§8.4 of the parent record) is implicated** as a contributing mechanism. Licensed: "restoring an upwind bias at the `fixedValue` inlet materially reduces and flattens the clamp population." **Not licensed:** that it is *the* root cause, that the case is now physical, that the wall or wedge faces behave the same way, or any move of the gate case off `rhoCentralFoamBounded`. The natural follow-up — is the bias *necessary*, or merely sufficient — is not pre-registered here and is not run under this document. |
| `BASELINE-RECOVERED` | `DEFICIT-NOT-IMPLICATED` | The inlet-face variant of the dissipation deficit **joins the eliminated list as mechanism #7.** Licensed: that elimination, and the §8.6(3) momentum/energy split (the `sigmaDotU` pre-correction / `½\|U\|²` post-correction mismatch at `:255` vs `:265`) becomes the leading remaining candidate. **Not licensed:** eliminating the deficit at wall or wedge faces (§9.3), nor any claim about the split, which is **not measured by this experiment**. |
| `BASELINE-RECOVERED` | `LEVER-INERT` (C2) | **`NOT A RESULT`** for the discrimination question. What is established is that the lever did not act — which, per §5.2, is the *expected* outcome if the inlet is supersonic on every face that matters, and is itself a finding worth recording. Mechanism #7 is **not** eliminated. |
| `BASELINE-NOT-RECOVERED` | any | **`NOT A RESULT`** for the discrimination question, whatever Step 1 shows: an unmatched control cannot ground a ratio. What survives is Step 0's own reads (§8.2, §8.3) **if and only if** Step 0 is `COMPLETE` or `TRUNCATED-AT-CAP` — those are absolute reads of a real run, not comparisons. The record must then state plainly that the record-quoted `~12 %`/`~30 %` figures were **not reproduced**, which is itself a finding about the parent record. |
| any | `BLOCKED` | Diagnosis is **`PENDING`** on the blocked step. Step 0's §8.2/§8.3 reads still stand if Step 0 completed. |
| `BLOCKED` | any | Diagnosis is **`PENDING`**. Nothing is licensed. |

### 9.2 The crash rows (L-255) — a SIGFPE is a measurement here

| where | label | what it licenses |
|---|---|---|
| Step 0 takes a SIGFPE | `SIGFPE-RECURRENCE` on the control | **A new finding, not a hole.** `rhoCentralFoamBounded` has never SIGFPE'd on this case; a recurrence under a bit-identical clamp means the clamp on `e` alone does **not** prevent the exception, which directly supports §8.7's claim that `rho` or `U` — not `e` — is the defective quantity. The `BOUNDDIAG:` line immediately before the crash names which. Licensed: "the `e`-only clamp is insufficient, and `<quantity>` was extreme at the crash." **Not licensed:** any comparison with Step 1 (the control is gone), so the discrimination question reads **`PENDING`**. Goes to the supervisor for triage. |
| Step 1 takes a SIGFPE, Step 0 does not | `SIGFPE-RECURRENCE` on the discriminator | The inlet upwind bias **destabilised** the case. This is a real, directional result and is reported as one: licensed is "restoring an upwind bias at the inlet makes this case worse, not better," which is evidence **against** the §8.4 deficit being protective. It is **not** `DEFICIT-IMPLICATED` (the fraction clauses are unevaluable) and it is **not** `BLOCKED`. Mechanism #7 is recorded as **contra-indicated**, not eliminated. |
| Both steps take a SIGFPE | `SIGFPE-RECURRENCE` on both | The clamp does not prevent the exception under either scheme. Licensed: the §8.7 gap is real and the guard must be extended to `rho` and `U` before any further discrimination is attempted. The discrimination question is **`NOT A RESULT`**. |
| Neither step takes a SIGFPE | `SIGFPE-ABSENT` on both | The expected case. Recorded explicitly so that "no crash" is a stated measurement rather than a silence. |

### 9.3 The scope this experiment does not cover — stated before it runs

1. **Wall-face and wedge-face dissipation are not tested.** §1.5 shows the
   briefed lever cannot be applied there without breaking no-penetration or
   axisymmetry. A `DEFICIT-NOT-IMPLICATED` therefore eliminates the **inlet-face
   variant only**. The wedge-face identity — which applies to all 29,700 cells —
   remains entirely untested by anything in this document.
2. **The §8.6(3) momentum/energy split is not measured.** It is named as the
   leading remaining candidate in one row of §9.1 and nowhere else, and no number
   from either step may be offered as evidence for or against it.
3. **Neither step produces a physically usable warm-up state.** `t = 6.5e-05 s`
   is ~1/15,000 of the case's own `endTime` and the flow has convected roughly
   `0.083 m` of a `0.2 m` domain. No comparison against TM 101075 is possible or
   permitted.
4. **`checkMesh` is not re-run and no mesh claim is made.** The mesh is copied
   byte-for-byte from a case whose mesh is already characterised.

---

## 10. Cost (standing rule 12)

**Unit: core-minutes = wall s × ranks ÷ 60. Both steps are single-rank, so
core-minutes = wall minutes.**

### 10.1 The basis, and the honest name for it

The parent record, §"The invariant corner cell, and the LTS test" (table at lines
304–309 and the paragraph at line 302), reports for the time-accurate control
run: **`ExecutionTime = 279.93 s`**, single core, **physical time reached
`6.51e-05 s`**, ended by a `timeout 280` wrapper.

**A per-*iteration* rate cannot be derived from it** — the record does not report
an iteration count for that run, and `adjustTimeStep yes` means the count is not
recoverable from the endpoints. What the record does support is a
per-*physical-time* rate:

```
rate = 279.93 wall-s / 6.51e-05 physical-s = 4.30e+06 wall-s per physical-s
```

(check: `6.51e-05 × 4.30e+06 = 279.93` ✓)

### 10.2 The arithmetic

```
per step:   6.5e-05 physical-s × 4.30e+06 wall-s/physical-s = 279.5 wall-s
            279.5 s × 1 rank ÷ 60                            = 4.658 core-min  -> 4.66
two steps:  2 × 4.658                                        = 9.32 core-min   -> 9.3
```

This independently reproduces §8.9's `4.67` and `≈9.4` figures (the small
difference is only that §8.9 costed the full `6.51e-05 s` where this document
runs to `6.5e-05 s`).

### 10.3 The table

| item | figure |
|---|---|
| rate basis | 279.93 wall-s to `t = 6.51e-05 s`, single core, 2026-07-30 |
| **load average the basis was measured at** | **NOT RECORDED.** The parent record gives no load figure for the time-accurate control run. The nearest same-day figure is **load 9.4** at the launch of the *original* `f4_swbli_warmup20` (parent record line 249: "26.6 GB available, load 9.4, swap 0") — **a different run**, quoted here only so the next estimator knows what the box looked like that day, never as this basis's own load. The farfield run's own resource check (line 329) records memory but no load. **This gap is itself the calibration finding**: an unrecorded basis load is exactly the defect the L4 diagnosis measured (0.64× misprediction from a basis taken at load ~19.5 and applied at load ~5.03; ledger row `DPW8_V2 L4`, `b8fe7eea`). |
| **load average this basis is being re-applied at** | **6.96 / 10.67 / 11.44** (1 / 5 / 15 min), 16 GB available, 16 cores, at freeze on 2026-08-23 20:58 UTC. **Re-read at launch time** — this figure dates the freeze, not the run. |
| derived rate | **4.30e+06 wall-s per physical-s** |
| projected per step (`endTime 6.5e-05`) | 279.5 wall-s = **4.66 core-min** |
| projected, both steps | **9.3 core-min** |
| **RUN CAP** | **12 core-min total; 6 core-min per step** |
| headroom on the run cap | **1.29×** — thin, and §7.2 exists because of it |
| solver builds (2 × `wmake`) + control **C0** (2 × 200 steps) | **estimated ≈ 2 core-min** — *no `wmake` timing for this solver is recorded anywhere on this box; this figure is an estimate and is labelled as one, never as a measurement* |
| **BUILD ALLOWANCE** | **3 core-min** — stated **separately and as an addition** to §8.9's `≤12`, because §8.9 counted solver runs only and a `wmake` is real compute that must not be smuggled in as free. **The supervisor may trim this; the lane does not assume it.** |
| **TOTAL ENVELOPE** | **≤ 15 core-min** = 0.25 core-h |
| dollar figure | 0.25 core-h × $0.0513/core-h = **$0.0128 ≈ $0.01** |
| `cost_basis` | **rate: record-quoted, artifact-missing.** The 279.93 s / 6.51e-05 s figures come from the parent record's prose; the log behind them is **gone from disk** (§2.1, parent §8.8). **Price: reported-by-owner, not measured** — $0.0513/core-h, c7a.4xlarge, owner-stated 2026-08-21/22, corroborated at `Xiao2016_EnKF/PREREGISTRATION.md:197`. The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so the dollar figure is derived, not measured. |

**An overrun stops the run; it does not get a new budget** (rule 12). A step that
passes 6 core-min is stopped, and §7.2 decides whether what it reached is
gradeable on the pre-declared truncated window or is `BLOCKED`.

Under the 2026-08-21 blanket this is far under $25 and pre-authorised. **It is
costed here anyway, because a blanket is not a per-item read (rule 9), and being
inside a pre-authorised band is not an authorisation to launch (§12).**

### 10.4 Cost close-out — pre-committed here, frozen with everything else

Sanaa's directive, verbatim (2026-08-23): *"for all teams involved once a process
is completed, the estimated costs must be compared with the actual incurred costs
so we can improve the lab's estimates."* Relayed by the cfd supervisor before
this document was committed, so it is **part of the freeze, not an amendment**.

On completion of this experiment — whatever the outcome, including a `BLOCKED`,
`SIGFPE-RECURRENCE` or `NOT A RESULT` result — the results record
(`F4_SIGFPE_STEP01_RESULTS.md`) **must** carry a cost close-out section stating:

1. **Predicted vs actual core-minutes**, per step and in total. Predicted:
   4.66 core-min per step, 9.3 core-min total solver, ≤ 2 core-min build (§10.3).
2. **Actuals measured from named logs, not estimated.** The source for each
   figure is stated: solver wall time from each step's own
   `<STEP>/log.<solver>` final `ExecutionTime` line **and** from the launch
   wrapper's own timing file if one is written; `wmake` wall time captured by
   timing the build command itself and recorded per solver. **A figure not
   measured is stated as absent, never approximated into the table** (ledger
   append rule 2).
3. **Dollars derived at the recorded rate** ($0.0513/core-h, reported-by-owner)
   and **labelled derived**, never measured.
4. **The ratio** (cleaned actual / predicted), and the ratio against the cap
   (actual / 12 core-min run cap).
5. **Gross and cleaned** per `COMPUTE_BUDGET_CHARTER.md` §2 (a row over 3600 wall
   s is a stall). At the projected 280 wall-s per step no stall row is expected;
   if one appears it is separated out and named.
6. **Gap attribution**, with the three causes kept apart and **waste separately
   named** (charter §6, never laundered into the ratio's explanation):
   - **contention** — the load average at launch, quoted against §10.3's
     "basis was measured at: NOT RECORDED" row, so the next estimator sees both
     ends of the comparison;
   - **misprediction** — the per-physical-time rate actually observed
     (wall-s ÷ physical-s reached) against the 4.30e+06 basis, with its direction
     stated;
   - **waste** — any core-minutes that produced no measurement (a failed
     pre-launch diff, a discarded build, a re-run after a staging fault), named
     as waste and counted, not absorbed. A run terminated by the phenomenon under
     study (§7.3's `SIGFPE-RECURRENCE`) is **not waste** — the crash is the
     measurement — and the close-out must say so explicitly rather than let the
     shortfall read as thrift.
7. **One appended row in `docs/COST_CALIBRATION.md`**, at the foot of the table,
   per that file's own append rules (append-only; figures from committed records;
   units stated; gross/cleaned per charter §2; waste separately named;
   **re-derive the table's current tail at commit time in the same shell
   invocation as the commit, and land it by the private-index protocol of rule
   10** — that file is written by multiple teams concurrently).

**One condition on that ledger row, checked at freeze and stated so the next
agent does not assume it:** `docs/COST_CALIBRATION.md` **exists on disk today
(7,189 bytes) but is NOT tracked at HEAD** — `git ls-files docs/COST_CALIBRATION.md`
returns nothing, so a parallel session's commit of it is still pending. At
close-out time, **verify the file exists at HEAD before appending**; if it does
not, the row is held and the fact reported to the supervisor rather than the file
created a second time from this side.

---

## 11. Operational notes — the traps this case and this box have already sprung

1. **The Bash tool runs non-login shells and OpenFOAM is NOT on `PATH`.** Source
   the bashrc **in the same command as the launch**, never in a preceding call:
   `source /usr/lib/openfoam/openfoam2606/etc/bashrc "" && setsid … rhoCentralFoamBoundedDiag …`.
   Path confirmed at `docs/OPENFOAM_SOLVER_BUILD.md:78`. `docs/OPENFOAM.md:118`'s
   `wsl -d Ubuntu` prefix is a **Windows/WSL host** instruction and does not
   apply to this box.
2. **Launch with `setsid`** so the solver outlives the agent; a foreground Bash
   solver is SIGTERMed when the agent's shell goes away.
3. **`pgrep`/wait-loop completion checks lie on this case specifically** — the
   parent record's own LTS section documents a `while pgrep -x
   rhoCentralFoamBounded` loop reporting a finished run that was still advancing.
   Completion is decided by §7, cross-checked with `ps -p <pid>`, never by a wait
   loop and never by a `.done` filename (check `.done` **bodies**, not existence).
4. **Fleet agents are invisible to `pgrep`.** At freeze time: load average 6.96 on
   16 cores, 16 GB available, one `simpleFoam` live (pid 1161379, closure team,
   54 min elapsed) and two long-lived `python3` processes (pids 1439, 1446). **Do
   not touch them.** Two additional single-core steps are within free capacity,
   but this sweep is a floor on what is running, not a ceiling — re-run the L-41
   sequence (`git log --since`, run-dir mtimes, docket, then processes) at launch
   time, not from this note.
5. **The four existing `warmup20*` directories are evidence and are read-only**
   for the whole of this experiment (§1.2).
6. **`purgeWrite 3` with `writeInterval 1.3e-05` at `endTime 6.5e-05` keeps
   `3.9e-05/`, `5.2e-05/` and `6.5e-05/`.** That is intended: §7.1's age guard is
   checked against `6.5e-05/` and §7.2's against `3.9e-05/`.
7. **The published `rhoCentralFoamBounded` binary must not be overwritten.** Both
   new solvers carry distinct `EXE` targets (§4.1, §5.1), so
   `docs/OPENFOAM_SOLVER_BUILD.md` §6's four md5s stay valid. Verify after each
   build that `…/platforms/linux64GccDPInt32Opt/bin/rhoCentralFoamBounded` still
   has md5 `ee83ca590752bd34265d306faf3ad660`.

---

## 12. Freeze

The corrections (§1), the shared configuration (§3), the instrument (§4.2), the
Step 1 source diff and its inertness prediction (§5), the positive controls (§6),
the completion rule including the truncation and SIGFPE clauses (§7), the
measurement clauses, thresholds and labels (§8), the outcome map (§9) and the
cost cap and close-out commitment (§10, including §10.4) are **fixed at the
commit of this file.**

**Nothing may launch before that commit exists and the cfd supervisor has
personally verified it.** Pre-registration-committed-before-compute is a
supervisor personal check and is not the lane's to sign off
(`SUPERVISION_CHARTER.md` §3; CLAUDE.md rule 9). The brief that produced this
document is an agent message and is **not** Sanaa's consent.

**The condition, checked at freeze on 2026-08-23 and quoted verbatim from the
box:**

```
$ ls -d verification/runs/F4_runs/swbli_cylflare/step0* \
        verification/runs/F4_runs/swbli_cylflare/step1* \
        verification/runs/F4_runs/swbli_cylflare/rhoCentralFoamBoundedDiag_src \
        verification/runs/F4_runs/swbli_cylflare/rhoCentralFoamInletUpwindDiag_src
ls: cannot access 'verification/runs/F4_runs/swbli_cylflare/step0*': No such file or directory
ls: cannot access 'verification/runs/F4_runs/swbli_cylflare/step1*': No such file or directory
ls: cannot access 'verification/runs/F4_runs/swbli_cylflare/rhoCentralFoamBoundedDiag_src': No such file or directory
ls: cannot access 'verification/runs/F4_runs/swbli_cylflare/rhoCentralFoamInletUpwindDiag_src': No such file or directory
```

(the fourth path was probed at freeze under its working name
`rhoCentralFoamBndUpwind_src` and was likewise absent; the target name settled in
§5.1 is `rhoCentralFoamInletUpwindDiag_src`, which does not exist either.)

**No run directory, no solver source tree and no compiled binary exists for
either step. No compute has been spent under this document.** The four existing
`warmup20*` directories each hold exactly one time directory, `0/`, and are
untouched.

Amendments before first compute are legal and must state the condition and how it
was checked. **After first compute the gates are closed** and changes land only
as dated addenda that cannot alter a gate, threshold, cap or label; originals are
struck, never rewritten (rule 2, rule 6).

Results will be recorded in
`verification/campaign/F4_SIGFPE_STEP01_RESULTS.md`, citing this file by its
commit sha and hashing the frozen file against the committed blob to prove the
document that ran is the document that was frozen.

---

## 13. AMENDMENT 1 (pre-compute, 2026-08-24) — three defects found in the supervisor's read of the frozen file

**Version:** v1.1 — was v1.0, the freeze at commit `0bbac521`
(`0bbac521712258b1def4c6119710fe6fcc10ba7c`, 2026-08-23T21:13:11Z). The frozen
blob of v1.0 is `3c90b9931e6f996ed59db4ee0c7a125bf8fc60b5` and was verified byte-
identical to the working copy before this amendment was appended
(`git hash-object` == `git rev-parse 0bbac521:<this file>`).

**Why this is legal.** Rule 2: *"Before first compute, amendments are legal and
must state the condition and how it was checked (name the run directory that does
not exist)."* Rule 6: frozen files are never edited — this is appended at the
foot, nothing above is touched. §12 of this document repeats both.

**What produced it.** The cfd supervisor's personal read of the frozen file
(`SUPERVISION_CHARTER.md` §3 — pre-registration verified before compute, and the
measurement-script diff read as a diff). Three defects were found. Each is stated
below with the original clause quoted verbatim and struck, the replacement, and
the on-disk evidence that the defect is real. **A supervisor brief is not Sanaa's
consent (rule 9); this amendment authorises nothing to launch.**

---

### 13.0 The condition, and how it was checked

Checked at 2026-08-24T16:18:47Z (box clock, `date -u`, read in the same shell invocation as
the write), at HEAD `506dde3608e3f2625a96862129449ddca8d461b3`.

**(a) Neither step's run directory nor either solver source tree exists.** Verbatim
from the box, the same probe §12 froze:

```
$ ls -d verification/runs/F4_runs/swbli_cylflare/step0* \
        verification/runs/F4_runs/swbli_cylflare/step1* \
        verification/runs/F4_runs/swbli_cylflare/rhoCentralFoamBoundedDiag_src \
        verification/runs/F4_runs/swbli_cylflare/rhoCentralFoamInletUpwindDiag_src
ls: cannot access 'verification/runs/F4_runs/swbli_cylflare/step0*': No such file or directory
ls: cannot access 'verification/runs/F4_runs/swbli_cylflare/step1*': No such file or directory
ls: cannot access 'verification/runs/F4_runs/swbli_cylflare/rhoCentralFoamBoundedDiag_src': No such file or directory
ls: cannot access 'verification/runs/F4_runs/swbli_cylflare/rhoCentralFoamInletUpwindDiag_src': No such file or directory
```

**(b) No numeric time directory other than `0/` exists anywhere in the run tree** —
so no solver has written a field under this document, in either step or in any of
the four pre-existing `warmup20*` cases:

```
$ find verification/runs/F4_runs/swbli_cylflare -maxdepth 2 -type d -regex '.*/[0-9.e-]+$'
verification/runs/F4_runs/swbli_cylflare/warmup20/0
verification/runs/F4_runs/swbli_cylflare/warmup20_bounded/0
verification/runs/F4_runs/swbli_cylflare/warmup20_bounded_farfield/0
verification/runs/F4_runs/swbli_cylflare/warmup20_bounded_realtime/0
```

Four directories, four `0/` dirs, nothing else. §12's assertion still holds
verbatim: **no run directory, no solver source tree, no compiled binary, and no
compute spent under this document.**

**(c) The whole run tree, for completeness** — `analyse_f4_sigfpe_step01.py`,
`fixtures/`, `rhoCentralFoamBounded_src/` (the *published* solver, §11.7, not
either new one) and the four `warmup20*` cases. No `step0`, no `step1`, no
`*Diag_src`.

**Gates are therefore open.** This amendment changes one completion clause
(§7.3), one reference state (§8.3) and one reader regex. It changes **no
threshold, no band, no cap and no label**; §8.3's `10 %` and `5 %` bands and
§10's `12 core-min` cap are carried through untouched.

---

### 13.1 Defect 1 — §7.3's `1.3e-05/` field-write clause is unsatisfiable under `purgeWrite 3`

**STRUCK — original, line 677, verbatim:**

> ~~- at least one field write (`1.3e-05/`) present and newer than that step's `0/T`.~~

**REPLACEMENT:**

> - **at least one numeric time directory other than `0` present under the step,
>   carrying all seven fields (`T U p alphat k nut omega`), every one of them
>   newer than that step's own `0/T`** (the age guard, standing rule 4). The
>   results record states which time directory was used.

**Why the original cannot hold.** The step `controlDict` (§3, lines 235–241) sets
`writeInterval 1.3e-05`, `endTime 6.5e-05`, `purgeWrite 3`, giving five writes at
`1.3e-05, 2.6e-05, 3.9e-05, 5.2e-05, 6.5e-05`. `purgeWrite 3` keeps the three
most recent: the moment `5.2e-05/` is written, **`1.3e-05/` is deleted by
OpenFOAM.** A step that crashes after `5.2e-05` therefore has no `1.3e-05/` and
would be forced to **`BLOCKED`** by §7.3's second bullet — routing the *late*
crash, which carries the most pre-crash trend data, into the empty cell that
L-255 was written to prevent. The clause inverts its own purpose.

**On-disk evidence, and an internal contradiction this document already carried.**
`purgeWrite 3;` is confirmed at line 16 of
`verification/runs/F4_runs/swbli_cylflare/warmup20_bounded_realtime/system/controlDict`
(md5 `d1a144790d89f4c5ebcf1a9a5691d87e`), the inherited file §3 modifies, and §3
line 241 carries `purgeWrite 3` forward unchanged. **This document already knew
the consequence**: §11 note 6, lines 969–971, states *"`purgeWrite 3` with
`writeInterval 1.3e-05` at `endTime 6.5e-05` keeps `3.9e-05/`, `5.2e-05/` and
`6.5e-05/`"* — a list that does not contain `1.3e-05/`. §7.3 and §11.6
contradicted each other at the freeze. §11.6 is right; §7.3 was wrong, and is
corrected here.

**What is NOT changed.** The 200-`Time = `-block minimum stands. The
`SIGFPE-RECURRENCE` / `SIGFPE-ABSENT` labels stand. The `BLOCKED` fallback for a
crash with fewer than 200 blocks **or with no surviving field write at all**
stands. This widens no gate: a step that writes nothing still fails.

---

### 13.2 Defect 2 — §8.3's freestream reference state is wrong for exactly the cells that clamp

**STRUCK — original, lines 740–743, verbatim:**

> ~~From Step 0's `BOUNDDIAG:` lines, at the **first** timestep where `nLow > 0`, for
> the worst-low cell, relative to the freestream reference state
> (`rho∞ = 0.0252 kg/m³`, `|U|∞ = 1274 m/s`, `T∞ = 81.2 K`; NASA TM 101075 Table I,
> quoted in the parent record §7a):~~

**REPLACEMENT:**

> From Step 0's `BOUNDDIAG:` lines, at the **first** timestep where `nLow > 0`,
> for the worst-low cell, relative to a reference state chosen as follows and
> **stated in the results record**:
>
> - **If the worst-low cell is the owner of an inlet-patch face** — determined by
>   the exact map `constant/polyMesh/owner` over the inlet face range
>   `[startFace, startFace + nFaces)` read from `constant/polyMesh/boundary`, whose
>   ordering is the **same** ordering as the `nonuniform List` entries of the
>   `inlet` patch in `0/U` and `0/T` — the reference is **that face's own Table II
>   inlet-profile values**: `|U|_ref` = the magnitude of that face's `0/U` entry,
>   `T_ref` = that face's `0/T` entry, and `rho_ref = p / (R · T_ref)` with
>   `p = 576 Pa` (`0/p`, `internalField uniform 576.0`) and
>   `R = 8314.47 / 28.9 = 287.6979 J/(kg K)` (`constant/thermophysicalProperties`,
>   `molWeight 28.9`, `perfectGas`; the same `R` already used by `CV_BOUND`).
> - **Otherwise** the freestream values `rho∞ = 0.0252 kg/m³`, `|U|∞ = 1274 m/s`,
>   `T∞ = 81.2 K` (NASA TM 101075 Table I, parent record §7a).
> - The results record **states which reference was used** and either the cell's
>   **inlet face index** or the words **`not inlet-adjacent`**. A row that does not
>   state this is not graded.

**The bands are UNCHANGED.** `RHO_BAND = 0.10` and `U_BAND = 0.05` and the four
labels `RHO-FIRST` / `U-FIRST` / `E-FIRST` / `INDETERMINATE` (lines 745–749) are
carried through **verbatim and untouched**, as is their justification at lines
751–758. **This amendment changes what the deviation is measured *from*, not how
large a deviation has to be to fire a label.** The 5 % figure still sits above the
2.71 % / 3.45 % velocity errors of parent record §8.6(3); that argument is
unaffected, because it was always an argument about a *deviation from the local
state*, and the local state at an inlet-adjacent cell is the inlet profile.

**On-disk evidence — the map, read read-only from the control case
`warmup20_bounded_realtime`.** `constant/polyMesh/boundary` gives the `inlet`
patch as `nFaces 110`, `startFace 59020`; the mesh header records
`nCells:29700  nFaces:119180  nInternalFaces:59020`, so `inlet` is the first
boundary patch and its faces are `59020 … 59129`. Reading
`constant/polyMesh/owner` over that range gives 110 distinct owner cells running
`0, 120, 240, …, 13080` — **a single constant stride of 120**, which is the
origin of the parent record's "`≡ 0 mod 120`" observation. All four persistently
clamped cells are inlet-face owners:

| clamped cell | inlet face index | global face |
|---|---|---|
| 0 | 0 | 59020 |
| 3960 | 33 | 59053 |
| 6360 | 53 | 59073 |
| 13080 | **109** — the last inlet face, the inlet∩wall corner | 59129 |

**On-disk evidence — the profile at those faces**, read from the `inlet` patch's
`nonuniform List<vector>` in `0/U` (110 entries, `type fixedValue`) and
`nonuniform List<scalar>` in `0/T` (110 entries, `type fixedValue`), with
`rho = p/(R T)`, `p = 576 Pa`, `R = 287.699`:

(pipes avoided in the header below so the table renders: `magU` is `|U|`.)

| cell | face | magU (m/s) | `T` (K) | `rho` (kg/m³) | magU/magU∞ − 1 | rho/rho∞ − 1 | label §8.3 **would** fire |
|---|---|---|---|---|---|---|---|
| 0 | 0 | 1274.0000 | 81.200 | 0.024656 | +0.000 | −0.0216 | `E-FIRST` |
| 3960 | 33 | 1274.0000 | 81.200 | 0.024656 | +0.000 | −0.0216 | `E-FIRST` |
| 6360 | 53 | 1224.8712 | 106.169 | 0.018858 | −0.0386 | −0.2517 | `RHO-FIRST` |
| 13080 | 109 | **21.7811** | 303.959 | 0.006587 | **−0.9829** | **−0.7386** | `INDETERMINATE` |

**The defect is confirmed, and it is not marginal.** The brief's check was
whether `|U|` at the corner face is within 5 % of 1274 m/s. It is **21.78 m/s —
98.29 % below freestream**, because the inlet profile is a boundary-layer profile
and face 109 sits in it. Across the whole inlet, **54 of 110 faces** exceed the
5 % `|U|` band and **65 of 110** exceed the 10 % `rho` band **on the prescribed
boundary condition alone, at `t = 0`, before the solver has taken a single step**
(inlet `|U|` range 21.78 … 1274.00 m/s; inlet `T` range 81.200 … 368.823 K; inlet
`rho` range 0.005428 … 0.024656 kg/m³). Against the freestream reference, §8.3
would have returned three *different* labels for four cells that are the same
phenomenon — and for the corner cell it would have read `INDETERMINATE` (both
deviations outside their bands) purely from the inlet BC. The attribution read
would have been measuring the inlet profile, not the clamp mechanism.

**One honest disclosure about the replacement's own arithmetic.** At the
freestream face (`T = 81.2 K`), `rho = p/(R T) = 0.024656 kg/m³`, which is
**2.16 % below** the Table I `rho∞ = 0.0252 kg/m³`. The case's own `p` and `T`
and the tabulated `rho` are not exactly consistent. 2.16 % is inside the 10 %
band, so it flips no label at the freestream face, but the results record must
quote the reference it used numerically rather than by name, so this offset is
visible to the reader rather than hidden inside a symbol.

---

### 13.3 Defect 3 — the reader's `RE_SIGFPE` matches the OpenFOAM startup banner, so it reports a SIGFPE on **every** OpenFOAM run

**STRUCK — original, `analyse_f4_sigfpe_step01.py` line 119, verbatim:**

> ~~`RE_SIGFPE = re.compile(r"Foam::sigFpe|Floating point exception|SIGFPE")`~~

**REPLACEMENT (landed in the reader in the same commit as this amendment):**

> `RE_SIGFPE = re.compile(r"Foam::sigFpe::sigHandler|^Floating point exception\b")`
>
> and a new module constant `SIGFPE_RC = 136`.

**The rule, pre-declared here.** For §7.3's *"terminates on a floating-point
exception"* test:

1. **`rc == SIGFPE_RC` (136 = 128 + `SIGFPE`(8)) is the PRIMARY signal.** It is
   the kernel's own report and cannot be produced by log text.
2. **The backtrace frame `Foam::sigFpe::sigHandler` in the log is SECONDARY** —
   sufficient on its own when `rc` was not captured, but it is a log artefact and
   is named as such.
3. **The startup banner is EXPLICITLY EXCLUDED.** It is not evidence of anything
   except that trapping was enabled.

**On-disk evidence — the banner is universal and the old pattern matches it.** The
banner line is, verbatim from the archived F4 crash log
`demo-output/website/solve_registry/f4_swbli_warmup20_20260730T004453Z.log`
(md5 `b658b967377d574d8aacf00e3569cf9c`, asserted before reading), **line 18**:

```
trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).
```

The same line appears in every OpenFOAM solver log sampled on this box, including
runs that completed cleanly and never crashed —
`verification/runs/F5_runs/re3900/log.pimpleFoam` (line 18),
`verification/runs/F5_runs/re3900_corrected/log.pimpleFoam`,
`verification/runs/F5_runs/re1000/log.pimpleFoam`,
`verification/runs/F7_runs/damBreak_MM_a2p25in_medium/log.interFoam` (line 29),
and two further F7 `interFoam` logs. It is emitted by `Foam::sigFpe` at startup
whenever `FOAM_SIGFPE` is set, which is the default in the environment this box
sources.

**Measured false-positive rate of the struck pattern: 100 %.** Applied line by
line:

| log | struck pattern matches | first match | replacement matches | first match |
|---|---|---|---|---|
| F4 archived crash log (a **real** SIGFPE) | 2 | line 18, the banner | 1 | line 27602, the backtrace frame |
| `F5_runs/re3900/log.pimpleFoam` (clean, no crash) | **1** | line 18, the banner | **0** | — |
| `F7_runs/damBreak_MM_a2p25in_medium/log.interFoam` (clean, no crash) | **1** | line 29, the banner | **0** | — |

The struck pattern would have set `parse_log()["sigfpe"] = True` on a clean run,
and §7.3 would have labelled a perfectly completed step `SIGFPE-RECURRENCE`. The
replacement returns `True` on the real crash and `False` on both clean runs.

**How the archived crash actually signals**, quoted verbatim from line 27602 of
that log (the first frame of the `[stack trace]` block that ends the file at line
27611):

```
#1  Foam::sigFpe::sigHandler(int) in <platforms>/linux64GccDPInt32Opt/lib/libOpenFOAM.so
```

with frames `#4`/`#5` in `libfluidThermophysicalModels.so` and `#6`/`#9` in
`rhoCentralFoam` — the thermo inversion, which is the mechanism this experiment
is about. **The crash log contains no bare `Floating point exception` line at the
crash at all**: the only occurrence of that string in the whole 27,611-line file
is inside the startup banner. The backtrace frame is the only in-log signal there
is, which is exactly why the replacement pattern targets it.

**One thing this lane could NOT verify, stated plainly.** The archived crash's
`rc` is **not recoverable from disk**. Its sidecar
`demo-output/website/solve_registry/f4_swbli_warmup20_20260730T004453Z.done`
records `job`, `pid` (296218), `started`, `finished`, `case`,
`expected_artifact` and the last 25 log lines — **no `rc` field**. So rule 1
above (`rc == 136` primary) is a forward commitment binding the step-0/step-1
launch wrapper, which must capture and record `rc`; it is **not** a claim about
the 2026-07-30 archived run, whose `rc` nobody can now read. The archived run is
classified a SIGFPE here on the secondary signal alone, and this amendment says
so rather than implying a measurement that does not exist.

**Also corrected in passing:** the supervisor's brief predicted the banner text
as `SigFpe : Enabling floating point exception trapping (FOAM_SIGFPE).` The
actual text on this box is `trapFpe: Floating point exception trapping enabled
(FOAM_SIGFPE).` Both are excluded by the replacement pattern, and the reader's
`--selftest` asserts non-match against **both** strings so the guard does not
depend on which wording a future OpenFOAM build emits.

**Reader changes landed in the same commit** (and nothing else in that file):
`RE_SIGFPE` replaced at line 119; `SIGFPE_RC = 136` added to the frozen-constants
block with a comment citing this §13.3; `INLET_P_PA = 576.0` and
`R_GAS = 8314.47 / 28.9` added with a comment citing §13.2; three assertions
added to `--selftest`. All grading bodies remain `NotImplementedError` by design.
The C1 fixture `fixtures/bound_log_fixture.txt` is **untouched** — md5
`60f6d5802793f7bd2cbfa5fde3dafbcb` before and after.

---

### 13.4 Note — §10.4's freeze-time condition on `docs/COST_CALIBRATION.md` is stale, and was already stale when it was frozen

§10.4 lines 935–941 state, as a condition checked at freeze:

> ~~`docs/COST_CALIBRATION.md` **exists on disk today (7,189 bytes) but is NOT
> tracked at HEAD** — `git ls-files docs/COST_CALIBRATION.md` returns nothing, so a
> parallel session's commit of it is still pending.~~

**This is no longer true, and on inspection it was not true at the freeze
either.** The file was first committed at `ef6a9082` (*"Cost calibration law:
estimate-vs-actual at every process completion (Sanaa 2026-08-23)"*,
2026-08-23T21:04:25Z), which `git merge-base --is-ancestor` confirms is an
ancestor of the freeze commit `0bbac521` (2026-08-23T21:13:11Z) — **nine minutes
earlier**. `git ls-tree 0bbac521^ -- docs/COST_CALIBRATION.md` returns a blob, so
the file was tracked at the very HEAD the freeze was taken against. The condition
as written appears to have been read from a stale worktree rather than from HEAD.
Today it is tracked and has been appended to repeatedly, most recently at
`e88b86e6`; the cfd team's own two rows landed at `f89aa7b4`.

**The operative clause of §10.4 stands UNCHANGED**, and this note makes it more
important, not less: *"At close-out time, verify the file exists at HEAD before
appending; if it does not, the row is held and the fact reported to the
supervisor rather than the file created a second time from this side."* Verifying
**at HEAD** is precisely the check that would have caught the stale reading. The
worktree is measurably behind HEAD on this file right now — `23,937` bytes on
disk against `38,661` bytes at HEAD — so an agent appending from the disk copy
would silently revert a peer's rows. §10.4's seven close-out requirements are
otherwise unaltered, including the private-index protocol of rule 10 for that
append.

**Nothing in `docs/COST_CALIBRATION.md` was touched by this amendment.**

---

### 13.5 Assertions

- **lines whose number changed above this section: 0** — this section is appended
  at the foot of the file; §§0–12 are byte-identical to the frozen blob
  `3c90b9931e6f996ed59db4ee0c7a125bf8fc60b5` (commit `0bbac521`), which was
  verified against the working copy before the append and is verified again after
  it by diffing `0bbac521..HEAD` on this path and confirming additions only, all
  at the foot.
- **No gate, threshold, band, cap or label is altered.** §8.3's `10 %` / `5 %`
  bands, §8.1's `[6 %, 24 %]`, §8.2's `80 %` / `20 %`, §8.4's `0.60 ×` / `1.5 ×`,
  §7.3's 200-block minimum and §10's `12 core-min` cap are all carried through
  unchanged. §13.1 corrects an unsatisfiable completion clause; §13.2 corrects the
  reference state a threshold is applied *to*; §13.3 corrects a reader regex.
- **Version bumped:** v1.0 → **v1.1**. The status in the header remains `PENDING`.
- **Nothing launched. No build.** No run directory, no solver source tree and no
  compiled binary exists for either step; no compute has been spent under this
  document, before or after this amendment. Condition re-verified at
  2026-08-24T16:18:47Z and quoted verbatim in §13.0.
- **The supervisor's read of this amendment's diff is required before launch.**
  This is a change to a frozen pre-registration and to a measurement script; both
  are supervisor personal checks under `SUPERVISION_CHARTER.md` §3 and neither is
  the lane's to sign off. A lane's assurance that the amendment is sound is a
  summary, not a check. **No agent message — including the brief that produced
  this amendment — is Sanaa's consent (CLAUDE.md rule 9).**
