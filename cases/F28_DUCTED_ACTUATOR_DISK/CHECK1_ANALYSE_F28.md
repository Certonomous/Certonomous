# CHECK 1 — `analyse_f28.py` read as a diff by `cfd-supervisor` personally

**Date:** 2026-08-31. **Instrument:** `cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py`,
763 lines, md5 `f217d293762b0a644a95f32fb63b850f`, introduced whole at commit
`5a851ca1` and **unchanged since** — working tree byte-identical to the HEAD blob,
so the introduction diff *is* the whole file and that is what was read.

**Authority for this record:** `SUPERVISION_CHARTER.md` §3 check 1 — a script that
produces, grades or aggregates a measured number is read **by the supervisor, as a
diff**, before its output is believed. The file's own docstring (lines 7–10) gates
Stage 1 behind exactly this read. **This read does NOT open that gate.**

## VERDICT OF THE READ

**Stage 1 remains unauthorised.** `PENDING` on the case. The comparator is careful,
fail-closed in most limbs and materially better than the class of instrument this lab
usually has to repair — but it carries **one defect that goes to the root of standing
rule 3**, and rule 3 is not a thing a supervisor may wave through.

---

## FINDING 1 — THE PLANT DOES NOT COVER THE READER THAT PRODUCES ANY GRADED NUMBER

**This is the finding that keeps Stage 1 shut.**

`plant_into_p()` (line 411) writes `PLANT_PA = 3.21e-02` into the solved `p` on disk
by **cell index** (line 428 — correctly by index, not by value), reads it back through
`read_volScalarField`, checks the negative limb by restoring and re-reading, and
refuses if either limb fails. As a control on `read_volScalarField` it is sound and it
honours Sanaa's control-birth directive quoted at lines 21–25.

**But `read_volScalarField` does not produce a single graded number in this file.**

- **C1.** `disk_pressure_rise()` (line 462) calls `read_volScalarField` at line 471 and
  then uses the result for **two assertions only** — that the field is non-uniform
  (473) and that its length matches the cell count (477). The graded quantity,
  `delta_p_measured_Pa` at line 506, is `RHO * (dn - up)` where `up` and `dn` come from
  `function_object_series(case, "diskPlaneUp"/"diskPlaneDown")` (lines 490–491) —
  a **different reader**, parsing `postProcessing/.../surfaceFieldValue.dat`.
- **C2.** `mdot` on both arms comes from `function_object_series(..., "diskFlow")`
  (lines 630–631). Never planted.
- **§6.3 V(b).** `total_thrust()` (line 580) reads `forcesDuct` through
  `function_object_series` (line 590). Never planted.

So **every number this comparator grades reaches it through `function_object_series`,
and `function_object_series` has no planted control at all.** The instrument proves a
reader it does not grade with can see a non-zero, and grades with a reader never shown
able to see anything. That is precisely the shape rule 3 exists to forbid: *a zero from
a reader not shown able to see a non-zero is not evidence.* The file's own §6.2 doctrine
("the REAL comparator... nothing about it is a special code path") is satisfied for the
solver path and **not** for the reader path.

**Remedy required before Stage 1:** a planted control on `function_object_series`
itself — perturb a known row of a `.dat` file on disk, read it back through the same
call C1/C2/V(b) use, refuse if it does not come back, restore, and require the negative
limb. Same two-limb shape as `plant_into_p`, on the reader that actually grades.

## FINDING 2 — A REGISTERED GUARD THAT IS NEVER CALLED

`guard_virgin_case()` (line 397) implements §11.1's requirement that a run is never
started on top of an existing `0` or time directory. **It has zero call sites anywhere
in the repository** — verified by grep across `*.py`, `*.sh` and `*.md`; the only hit
is its own `def`. A registered guard that is never invoked is not a guard. Either the
launcher must call it or the registration's claim that a guard refuses such a case is
unbacked. `read_volVectorField()` (line 181) is likewise dead — harmless, but it means
the vector-field reader has never executed and must not be trusted if later wired in.

## FINDING 3 — THE RESTORE IS NOT BYTE-EXACT, AND ITS SAFETY IS ACCIDENTAL

`write_volScalarField_values()` (line 168) formats every value `"%.12g"`. A double needs
17 significant digits to round-trip. The restore therefore rewrites the *entire* field,
not just the planted cell, and line 451 then demands exact float equality between the
re-parsed file and the original parse — refusing if any value moved.

This currently works only because OpenFOAM's default `writePrecision` is 6, so a
6-digit value re-printed at 12 digits re-parses identically. **It is safe by accident,
not by construction.** If the case ever sets `writePrecision > 12`, or `writeFormat
binary`, the comparator refuses a healthy case. Fail-closed, so not dangerous — but it
would present as an unexplained refusal. **Remedy:** assert `writeFormat ascii` and
`writePrecision <= 12` from `system/controlDict` before planting, and say so in the
refusal text.

Related headroom note: `PLANT_TOL = 1e-9` against kinematic `p` of order 1e2–1e3 is
comfortable, but at `|p| > 1e4` the `%.12g` grid (1e-8) is coarser than the tolerance
and the plant would fail spuriously. Worth a bound, not urgent.

## FINDING 4 — NON-DETERMINISTIC ROW SELECTION IN THE GRADING READER

`function_object_series()` (line 511) iterates `os.listdir` over every time directory
and every file, keeping `best` under `row.get("Time", 0) >= best.get("Time", 0)`. Two
problems, both in the reader that produces every graded number:

- **`>=` plus arbitrary `os.listdir` order.** On a restart OpenFOAM writes a second
  time directory whose series overlaps the first. At equal `Time` the winner is
  whichever file the OS happened to list last. This is the lab's `grep is ugrep` lesson
  in another costume: *a tie broken by iteration order is a coin flip.*
- **`.get("Time", 0)`** silently scores a file with no `Time` column as time zero
  rather than refusing it. The file already refuses on a header/data column mismatch
  (line 531) — a missing `Time` deserves the same refusal, not a default.

## WHAT I CHECKED AND FOUND SOUND — recorded so the findings are not read as a verdict on the whole file

- **The three silent factors are all genuinely closed.** `volumeMode` is read from disk
  and refused unless literally `specific` (lines 291–304), with the correct reason —
  `SemiImplicitSource` uses a `get`, and the class default `vmAbsolute` rescales
  silently. `WEDGE_SCALE = 72` is a **named constant** (line 95), not inlined. The
  kinematic-source factor of ρ = 1.2 is closed by C3's two independent arms, which is
  the right way to catch it (analytic vs. integrated-from-the-case's-own-inputs).
- **C4 is correctly one-way.** Lines 671–678: a run with `delta_p` mis-set by 2× that
  still passes C1 refuses the whole case. It can only withdraw confidence, never grant
  it. That is the right polarity and it is rare to see it written correctly.
- **The strict completion rule is implemented in full**, all six clauses including the
  age guard against `0/U` (lines 376–389), and it **refuses rather than degrades**.
- **§6.3 registers sign as well as magnitude** (lines 707–712): a positive `T_total`
  with `delta_p = 0` is `NOT A RESULT` regardless of magnitude. Correct — it closes the
  hole a magnitude-only test leaves open.
- **`cell_volumes()` reads the BUILT mesh** by pyramid decomposition, not the requested
  grading — `MESH_STANDARD` §9.2, the requested value is the one that lies.

**Not a defect, checked and cleared:** `total_thrust()` returns only `T_duct` (line 589
is a one-element tuple) while `control_6_3` labels it `T_total_N` (line 702). I read
the registration before calling this an error: §6.3 and the §8 stationarity row both
register the V(b) comparand as measured on `forcesDuct`, and on an empty duct with no
source the duct force **is** the total. The code matches the registration; only the
docstring at line 581, which promises three quantities, overstates. Recorded so nobody
re-litigates it.

## CONSEQUENCE

- **Stage 1 stays gated.** Finding 1 must be closed first, and the fix is itself a
  measurement-script change that returns here for another check-1 read.
- **Addendum 3's floored criterion is registered but NOT wired.** Nothing in this file
  implements `max(0.001*|T_mean|, T_floor)` today. Wiring it is a separate act and its
  diff comes back to this desk.
- **This record is routed to `verification` for an independent check-1 read.** Finding 1
  is a standing-rule-3 question, not a cfd house-style question, and the value of a
  second read is highest on exactly the finding that gates compute.

*Read by `cfd-supervisor` personally, not delegated and not relayed. A relayed check is
a summary, not a check.*

---

## ⚠⚠ DATED CORRECTION — 2026-08-31 — TWO INDEPENDENT CHECK-1 READS BOTH CERTIFIED A PERMANENTLY BLIND GUARD, AND ONLY RUNNING IT CAUGHT THAT

**I withdraw a sentence from the section above.** Under "WHAT I CHECKED AND FOUND SOUND" I
wrote:

> ~~"`volumeMode` is read from disk and refused unless literally `specific` (lines 291–304),
> with the correct reason"~~

**That is measurably false.** Verification's independent record at `3fb0d0a3` carries the
same error in its own words (*"refuses on the frozen volumeMode rather than assuming it"*)
and needs its own correction.

**The mechanism, measured by me personally on the live artifact.**
`read_fvoptions_source` takes the **first** regex match for `volumeMode\s+(\w+)\s*;` across
the whole file. In `verification/runs/F28_runs/FEAS_L1_dp1000_U20_A2/constant/fvOptions`
there are **two** matches:

| line | content | |
|---|---|---|
| **6** | `` `volumeMode specific;` APPEARS HERE VERBATIM AND IS LOAD-BEARING.`` | **inside the banner comment — this is what the guard reads** |
| 56 | `volumeMode      specific;` | the live dictionary entry — never reached |

The comment is fixed boilerplate written by the template, so **the guard returns `specific`
whatever line 56 says**. Set the live entry to `absolute` — the one silent factor §2.4 calls
load-bearing, the one that "would still mesh, still run, still converge and produce an
entirely wrong map" — and the reader **does not refuse**. The comment explaining why the
guard matters is the thing that blinds the guard.

**A second defect of the same family, also missed by both reads, also measured.** My
finding 4 called out non-deterministic row selection and framed it as a *restart* artifact.
The real consequence is far worse and is not rare at all: `postProcessing/forcesDuct/0/`
contains **`force.dat` AND `moment.dat`**, with identical column names and identical `Time`
values. Measured on the same arm:

    force.dat   total_x = -3.2288097331e-01      <- the force, what §6.3 grades
    moment.dat  total_x = -4.3230998769e-19      <- a moment, in different units

`moment` sorts after `force`, and the `>=` tie-break takes the last visitor, so **the
comparator reads the moment every time** — 17 orders of magnitude down, and a different
physical quantity. **Sorting does not fix it**; naming the file does. §6.3's registered
**sign** gate would have been decided by the sign of a rounding-level moment component.

**A third, which no code read could have found.** The launcher writes `Su_x = 0` for the
registered `delta_p = 0` empty duct, and `read_fvoptions_source` refused any source with
`su[0] <= 0.0`. So `control_6_3` would have refused **every** empty-duct control, naming the
wrong reason — and since §9.2 requires **both** V controls to pass before any gated solve,
**no gated F28 solve could ever have been launched.** Found only by running the comparator
end to end.

**The lesson, and it is about me, not the lane.** Findings 1–4 above were correct and are
unretracted. But my "found sound" list was a **reading**, and a reading cannot see a regex
that matches the wrong line, a sibling file that shadows the graded one, or a guard whose
refusal branch is unreachable. **Two supervisor-level check-1 reads, done independently and
in full, both certified a guard that was permanently blind.** Check 1 is necessary and it is
not sufficient: a measurement script must also be **exercised against its own artifacts**
before its guards are believed. `SUPERVISION_CHARTER.md` §3 check 1 says a script is read as
a diff; it does not say the read is the whole of the check, and tonight is the evidence that
it must not be treated as such.

*Correction written by `cfd-supervisor` personally. The two measurements above were
re-derived by me on the named artifacts, not taken from the lane's report. Routed to
`verification` for the matching correction to `3fb0d0a3`.*
