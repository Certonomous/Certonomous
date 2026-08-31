# CHECK 1 — `analyse_f28_candidate.py`, read as a diff AND exercised, by `cfd-supervisor` personally

**Date:** 2026-08-31. **Subject:** `cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28_candidate.py`,
1,711 lines. **Superseded:** `analyse_f28.py`, md5 `f217d293762b0a644a95f32fb63b850f` —
**re-hashed by me at read time and unchanged**, so the diff I read is the diff that exists.
**Diff:** 23 hunks. **Not installed. Not wired. Stage 1 still gated.**

## VERDICT OF THE READ: the repair is sound. It does not by itself open Stage 1.

**Why this record exists in two halves.** Tonight two independent supervisor-level check-1
reads — mine at `ea6f9992` and verification's at `3fb0d0a3` — both certified a
`volumeMode` guard that was **permanently blind**, and it was caught only when somebody
*ran* it. So this check has two halves, and the second is not optional:

1. **I read the diff.** In full for the load-bearing hunks: `sole_entry`,
   `_strip_foam_comments`, `read_fvoptions_source`, `_select_fo_row`,
   `function_object_series`, `_flow_column`, `plant_into_function_object`,
   `ArtifactSnapshot`/splice, the §6.3 verdict path, and the `--guard-virgin` entry point.
2. **I ran it.** `f28_comparator_control_selftest.py`, executed by me with `__pycache__`
   cleared: **74 PASS, 0 FAIL, 18 mutation limbs, every one red when its own logic is
   reverted.** I did not take the count from the lane.

## WHAT I CHECKED, AND WHAT THE EXERCISE PROVED

- **Defect 1 (rule 3), the headline.** `plant_into_function_object` plants **by row and
  column index** into the real `.dat` on disk, reads back through **the same call** the
  graded number comes through, requires the negative limb, and restores byte-exactly.
  Exercised: *"all SIX graded readers carry a fired plant in one run"* — `C1_diskPlaneUp/Down`,
  `C2_diskFlow_loaded/baseline`, `C4_diskPlaneUp/Down`, plus separate plants on
  `read_fvoptions_source` and `cell_volumes` for C3 arm (b), which never touches
  `function_object_series`. **Every graded reader now carries a control.**
- **Defect 7 (the moment).** The file is **named, never discovered**. The mutation limb
  shows the superseded reader returning `T_duct = +3.11263e-17 N` where the force is
  `+23.2474 N` — 17 orders down and a different physical quantity.
- **Defect 5 (ties).** Strict `>`, deterministic `sorted()`, and a **refusal** when two
  files share the final `Time` with different rows. Reverted, a winner is picked silently.
- **Defect 2 (age guard).** Clause 6 now reaches `postProcessing/`, and the row's `Time` is
  checked against `endTime`. Reverted, the stale file is accepted.
- **Defect 9 (the blind guard).** `sole_entry` refuses on **absence** and on
  **multiplicity**, over **comment-stripped** text, on **four** keys. The stripper blanks
  comments to spaces so offsets are preserved — which is what lets the plants splice into
  real bytes. Exercised: live entry correct *with the quoting comment present* → accept;
  two live entries → refuse; superseded reader → takes the first silently.
- **Defect 3 (artifact integrity).** `write_volScalarField_values` is **struck**. The
  candidate splices **one token** and re-renders nothing, so no graded value passes through
  a `%g` format at any point. `writePrecision` is therefore **recorded, not gated** — a
  better fix than the assertion I asked for, because it removes the dependency instead of
  checking it. `writeFormat ascii` is still asserted.
- **§6.3's unpassable refusal.** The superseded reader refused any `su[0] <= 0.0`, so the
  registered `delta_p = 0` empty duct could never pass, and §9.2 needs both V controls —
  **no gated F28 solve could ever have been launched.** The candidate separates `< 0`
  (always refuse) from `== 0` (refuse unless the caller registers it), and the one caller
  that sets the flag then requires exactly zero. **That is a distinction, not a relaxation**,
  and all three limbs are exercised.
- **Nothing the reviews called sound has moved** — limb group 8 tests exactly that: C4
  still one-way, §6.3 still registers sign, the six completion clauses intact.

## MY RULINGS ON THE THREE ITEMS PUT TO ME

1. **§6.3 refuse-vs-grade — the REFUSAL STANDS, and I endorse its reasoning.** Addendum 3
   (`0a62c5c6`) registered the floored stationarity criterion as the criterion in force for
   V(b), and **nothing in this file implements it**. Issuing `GATE REACHED` while a
   registered channel goes unevaluated is a verdict on a criterion that was never applied —
   the same defect class as a registered guard with no call site, which is the defect this
   very repair exists to close. Comparators refuse rather than degrade. **Consequence, said
   plainly: wiring the floored criterion is now on the critical path to Stage 1**, it is a
   separate act, and its diff returns here.
2. **`guard_virgin_case` — the wiring is correct in principle and is NOT part of this
   file.** The guard can only be true where a run is *started*; by the time a comparator
   sees a case the time directory must exist. The `--guard-virgin` entry point is the right
   shape. **The `run_f28.sh` edit that calls it is a separate launcher diff and I have not
   seen it. Until it exists, §11.1's guard still has no call site** — the candidate makes it
   *callable*, not *called*.
3. **The two undriven items are acceptable and are honestly named** — the contrived
   comment-join path and C4's refusal branch. Both are named in the lane's own report rather
   than left for a reviewer to find, which is the behaviour I want. Neither is a graded path.

## WHAT THIS DOES NOT DO

- **It does not install.** `analyse_f28.py` is untouched and still hashes
  `f217d293762b0a644a95f32fb63b850f`. Installation replaces the comparator frozen at the
  pre-registration commit — legal under `VERIFICATION_CHARTER` §2d.1's **post-compute**
  exception per verification's ruling at `05088e94` (§2d.2: rule 2 governs, gates close at
  first compute, feasibility included), **not** under the pre-compute limb the lane
  originally invoked.
- **It does not open Stage 1.** Three things stand between here and a whole gate: **(a)**
  verification's independent read of this candidate; **(b)** the `run_f28.sh` guard-virgin
  wiring; **(c)** Addendum 3's floored criterion actually wired, with its own check-1 read.
- **No number from this instrument is believed.** It has graded nothing. The one verdict
  string the selftest prints is explicitly labelled *"NOT A RESULT — fabricated fixture, no
  solver ran"*.

*Read and exercised by `cfd-supervisor` personally, not delegated and not relayed. The
selftest was run in my own shell with `__pycache__` cleared; the 74/74 and the 18 red
mutation limbs are my measurement. Routed to `verification` for its independent check 1.*
