# PETITION — repair the box-wide kill scope in `run_r2_m0.sh` (§2d.1 / §2av forced repair)

**This is a PETITION artifact, not a repair. NOT FILED, NOT SENT — it stays in the box.**
It petitions **verification** to rule the repair lawful under `§2d.1` (the post-compute
grading-path repair exception) on the `§2av` **forced-repair** test. **The frozen file
`cases/committee-grids/run_r2_m0.sh` is UNTOUCHED and remains untouched pending
verification's ruling.** Under `§2d.1`'s process the change lands only after that ruling,
as a dated rule-6 amendment appended at the foot of the frozen file.

- **Drafted by:** `lab-lane` for `cfd-supervisor`, 2026-09-06.
- **Owner approval of the REPAIR CHOICE (option 1: scope the kill, do not retire the
  driver):** Sanaa, captured at commit `476f2f27` — *"chief SESSION CAPTURE addendum:
  Sanaa chose option 1 for the m0 box-wide kill — repair the pkill scope (not retire the
  driver), routed to cfd+verification as a forced-repair §2d.1 post-compute amendment."*
  Per CLAUDE.md rule 9, a captured owner choice of *what to fix* is not verification's
  ruling of *whether the fix is lawful under §2d.1*; that ruling is what this petition seeks.
- **Frozen baseline this petition is written against:** `run_r2_m0.sh`, git blob
  `4d8081afecf6c5f2d5beea44fbe6be7b15349675`, sha256
  `cb810bb5fa79e9aeef382a12e3cd8e7a4fe77499e660c1fd6f938487418c3885`
  (working tree == `HEAD`, verified). The sha256 is re-derived inside the commit
  invocation that lands this petition, so the baseline it cites is provably current.

---

## 1. The defect, verified at source

`run_r2_m0.sh:82-88`:

```
sweep() {
    pkill -TERM -f "rhoSimpleFoam -parallel" 2>/dev/null
    sleep 2
    pkill -KILL -f "rhoSimpleFoam -parallel" 2>/dev/null
    return 0
}
trap 'sweep' EXIT
```

The pattern `rhoSimpleFoam -parallel` is not scoped to this run. It is armed on
`trap 'sweep' EXIT`, so it fires on **every** exit path of the driver — normal completion,
`die()`, cap exit, crash. The safe sibling `run_r2_m1.sh` documents this exact defect at
its `:72-81` and scopes its own sweep to `$ROOT` (`run_r2_m1.sh:82-88`) with a guard.

**This is a genuine POST-compute case.** The driver ran unattended (queue daemon) and
graded a verdict. Verified at source:

- `verification/runs/RUNG2_CRM_runs/M0_compressible_admission/RUN_ROOT_CREATED_EPOCH`
  → epoch `1788685768` = **2026-09-06T09:09:28Z**.
- `STATUS.R2_M0`: `grade_rc=0`, `selftest_rc=0`, `comparator_matches_committed_blob=1`,
  `spent_core_s=114` (1.90 core-min), `cap_hit=0`, `a3_warmstart_mapped=0`.
- `log.grade`: `R2-G0: PASS`, `R2-G1: GATE FAIL`, **`R2-M0 VERDICT: GATE FAIL`**.

So first compute occurred; `§2ax` (no-compute) does **not** apply, and the full
four-condition `§2d.1` burden is in force.

**Known stale artifact, NOT repaired by this petition:** the frozen header
(`run_r2_m0.sh:3, 14, 21`) still asserts *"THIS DRIVER HAS NEVER BEEN EXECUTED"*. It ran at
09:09:28Z; the header is stale because it is frozen and could not be updated at run time.
It is named here for verification's awareness only. This petition touches **only the kill
scope**. If verification wants the header corrected too, folding it into this same grant
avoids a second intrusion into the frozen file (cf. `§2av.5`'s second-touch note); this
lane does not fold it in unilaterally.

---

## 2. Is the fix FORCED (§2av — no degrees of freedom)? — YES, and doubly so

**`§2av` (VERIFICATION_CHARTER v1.67, :8104-8111):** *for a repair, the anti-gaming
question is not only who found the error but how many ways it could be fixed; a repair
whose correct form is forced has no degrees of freedom pointing at the answer and cannot be
aimed.*

**(i) m0 has a `$ROOT`-equivalent that uniquely identifies its own run root — quoted by line.**

- `run_r2_m0.sh:57`: `ROOT="$REPO/verification/runs/RUNG2_CRM_runs/M0_compressible_admission"`
  — absolute, unique to this run, set **once** as a literal and **never reassigned**
  anywhere in the file (unlike the sibling, which reassigns `ROOT` for `--dry-go`; m0 has no
  such mode).
- `run_r2_m0.sh:334-335`: `for arm in $ARMS; do  d="$ROOT/$arm"` — the per-arm directory.
- `run_r2_m0.sh:352-353`: `run_step "$arm" "$RANKS" "$d/log.solve"  mpirun -np "$RANKS"
  rhoSimpleFoam -case "$d" -parallel` — **every** rhoSimpleFoam child is launched with
  `-case "$ROOT/$arm"`. There is no other `rhoSimpleFoam` invocation in the file.

Therefore `rhoSimpleFoam -case $ROOT` is the common prefix of every arm's command line, and
matches nothing else on the box (the two `reconstructPar`/`decomposePar` calls at `:300`,
`:317`, `:361` are different binaries; the driver's own shell is `bash run_r2_m0.sh`). This
is **exactly the sibling's proven idiom** (`run_r2_m1.sh:84,86`), already committed and run.

**(ii) There is one right scope string, not a choice among several.** The forced answer is
"make m0's sweep identical to the sibling's blessed sweep." A per-arm loop or a
trailing-slash variant would *deviate* from the proven sibling with no benefit; nothing in
m0's structure offers a second correct-looking scope that would behave differently.

**(iii) The stronger ground — the repaired code path emits no value at all.** `§2av`'s
forced-ness matters because a *comparator reads data*. Here the object repaired is a
`pkill` inside a `trap ... EXIT` cleanup: it **reads no field, computes no quantity, and
contributes nothing to any field, gate, threshold or verdict**, and it runs *after* grading
on the way out. No conceivable choice of kill pattern could tilt the R2-M0 reading in any
direction, because the sweep produces no reading. The `§2av` anti-gaming hazard has **no
object** here — a fact about the case, not a gap in the evidence (cf. `§2av.3`/`§2av.4` on
vacuously-satisfied conditions being sound when the hazard does not exist).

**Verdict on §2av: FORCED holds.** This is not a choice dressed as a forced fix.

---

## 3. The exact diff — nothing but the kill scope

**BEFORE** (`run_r2_m0.sh:82-88`, verbatim):

```
sweep() {
    pkill -TERM -f "rhoSimpleFoam -parallel" 2>/dev/null
    sleep 2
    pkill -KILL -f "rhoSimpleFoam -parallel" 2>/dev/null
    return 0
}
```

**AFTER** (adopting the sibling's proven idiom, `run_r2_m1.sh:82-88`):

```
sweep() {
    [ -n "${ROOT:-}" ] || return 0
    pkill -TERM -f "rhoSimpleFoam -case $ROOT" 2>/dev/null
    sleep 2
    pkill -KILL -f "rhoSimpleFoam -case $ROOT" 2>/dev/null
    return 0
}
```

Three changes, and only these:

- `:83` — `-f "rhoSimpleFoam -parallel"` → `-f "rhoSimpleFoam -case $ROOT"`
- `:85` — `-f "rhoSimpleFoam -parallel"` → `-f "rhoSimpleFoam -case $ROOT"`
- one guard line inserted before `:83` — `[ -n "${ROOT:-}" ] || return 0`

The guard is the sibling's, verbatim. In m0 `ROOT` is always non-empty (set once, never
reassigned), so the guard is inert in m0's control flow; it is included to make the sweep
**byte-idiomatically identical** to the blessed sibling and to defend against the exact
box-wide misfire (`pkill -f "rhoSimpleFoam -case "` with an empty `$ROOT`) if a future edit
ever unset `ROOT`. The `trap 'sweep' EXIT` line (`:88`), the comment block (`:80-81`) and
everything else are unchanged. **No gate, threshold, cap, label, field or verdict is
touched.**

---

## 4. The four §2d.1 conditions, discharged

`§2d.1` (VERIFICATION_CHARTER :1936-1942): a post-compute grading-path change is permitted
iff all four hold.

**(1) A DEMONSTRABLE ERROR, not a preference — MET.** `pkill -f "rhoSimpleFoam -parallel"`
in an `EXIT` trap is a box-wide kill that can signal another team's solver mid-campaign,
directly against CLAUDE.md's standing *DO NOT TOUCH RUNNING SOLVERS*. The correct form is
established by the lab's own standard — the sibling already scopes it — so this repairs an
error, not a taste. Demonstrated empirically in §5, not asserted.

**(2) AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS — MET, at the limiting case.** The driven
control in §5 is `pgrep`/`pkill` **pattern matching on stand-in processes**: it grades
nothing, knows nothing of R2-M0's verdict, and cannot represent it. Stronger still, per (iii)
above: the repaired code path (an EXIT-trap sweep) feeds nothing into the grading path, so
there is no verdict it could be selected to move. This is the purest form of the
independence `§2d.1`(2) requires (cf. `§2av.3`: a matcher that grades nothing "cannot even
represent the verdict").

**(3) THE RECORD DISCLOSES IT, NAMES THE INSTRUMENT, QUANTIFIES WHAT MOVED — MET.** This
petition discloses the defect (§1), names the instrument (§5's `pgrep`/`pkill` rehearsal),
and quantifies what moved on the landed verdict: **nothing**. The GATE FAIL that landed at
09:09:28Z is unchanged; the amendment does not re-run and does not re-grade. Quantified
movement: 0 gates, 0 thresholds, 0 caps, 0 labels, 0 field values. Like `§2av.3`, this
condition is satisfied because its hazard — undisclosed movement of published values — has
no object: the sweep publishes no value. Verified byte-wise by the diff in §3, which is
confined to the two patterns plus one guard line; the grading path (`grade_r2_m0.py`,
separately frozen) is not touched.

**(4) PRE-REPAIR VALUES BESIDE THE PUBLISHED ONES — MET.** Pre-repair landed verdict:
**R2-M0 = GATE FAIL** (R2-G0 PASS, R2-G1 GATE FAIL), spend 1.90 core-min, recorded in
`STATUS.R2_M0` and `log.grade`. Post-repair state: **identical** — the amendment neither
re-runs nor re-grades, so the post value equals the pre value. Both are recorded here, beside
each other, per the condition.

**Checkable no-move assertion:** the only lines the amendment changes are the two `pkill`
patterns (`:83`, `:85`) and one inserted guard line; everything above the appended amendment
is unchanged, and the amendment block will carry rule 6's assertion
**"lines whose number changed above this section: 0"** with the unchanged-prefix sha256
(`cb810bb5…`, re-derived at apply time) proving the prefix is byte-identical.

**Honest note for verification — the frame.** `§2av` was cut for a *crash in a comparator*
(the grading path). This is neither a crash nor the comparator: the driver ran to
completion and the sweep is an EXIT-trap cleanup, not on the grading path in the value
sense. Per `§2av.2`'s "easy exit," verification may hold that `§2d`/`§2d.1` is not even
engaged and that the change may land as an ordinary dated rule-6 addendum to a frozen
instrument. This petition discharges the full four-condition burden regardless (the
belt-and-braces conduct commended in the F28 ruling, :4228), so the repair is lawful on
either route. Which route to take is verification's to rule.

---

## 5. The driven control the petition rides on — rehearsed BOTH WAYS on stand-ins

Rehearsal: `cases/committee-grids/M0_KILL_SCOPE_PETITION.md` was produced with the script
`scratchpad/rehearse_m0_killscope.sh` (temp; not a handoff channel — its result is
transcribed here per L-186). It signals ONLY two `sleep` stand-ins it starts itself; no
real solver was running (verified via `/proc/*/exe` and `pgrep` immediately before).

Stand-ins (argv[0] set via `exec -a`, so the process cmdline is realistic):

- **ALPHA** (this run's own arm): cmdline `rhoSimpleFoam -case <TESTROOT>/A0 -parallel 600`
- **BRAVO** (a foreign solver): cmdline `rhoSimpleFoam -parallel 600` (no TESTROOT)

Result (measured):

- **(a) scoped repair.** `pkill -TERM/-KILL -f "rhoSimpleFoam -case <TESTROOT>"` →
  **ALPHA = DEAD, BRAVO = ALIVE.** The scoped kill takes this run's own arm and spares the
  foreign one.
- **(b) old box-wide pattern.** Demonstrated by MATCH SET via `pgrep -f "rhoSimpleFoam
  -parallel"` (identical `-f` matcher to `pkill`), **never signalled** — running the
  box-wide `pkill` is exactly the prohibited act. Match set = `{BRAVO}`; **BRAVO is in it,
  so the old box-wide `pkill` WOULD HAVE KILLED the foreign stand-in.** The new scoped
  pattern does **not** match BRAVO (why it survived in (a)).
- Both stand-ins reaped by exact PID; nothing else signalled.

**Bonus finding, measured.** The old pattern's match set was `{BRAVO}` only — it did **not**
match ALPHA, whose tokens `rhoSimpleFoam … -parallel` are non-adjacent (`-case <root>` sits
between them). So the frozen idiom is not merely over-broad toward foreign solvers; it can
also **under-match this run's own arms** depending on argument order. The scoped `-case
$ROOT` pattern matches its own arms reliably (ALPHA died) — a correctness gain beyond the
safety gain.

> **DISCRIMINATES: the scoped pattern KILLS the own-arm stand-in and SPARES the foreign one;
> the old box-wide pattern MATCHES the foreign one. The repair narrows the kill exactly as
> intended.**

This is the whole petition: the old idiom would signal a foreign solver; the new one, keyed
on this run's unique `$ROOT`, does not.

---

## 6. What might make verification refuse or re-frame

1. **Frame.** `§2av` is a *crash/comparator* precedent; this is a driver EXIT-trap sweep not
   on the grading path (see §4's honest note). Verification may rule `§2d.1` not engaged and
   accept the change as a plain rule-6 addendum. Either way the four conditions are met.
2. **Scope of the petition.** The guard line is a second change beyond the two patterns.
   It is inert in m0's flow (ROOT never empty) and matches the sibling verbatim; verification
   should rule whether the grant covers the guard as well as the patterns. This lane includes
   it as "adopt the sibling's proven idiom."
3. **The stale header** (`:3,14,21`, "NEVER BEEN EXECUTED") is now false. Not repaired here;
   flagged for a possible single-touch fold-in (`§2av.5`).
4. **Second-touch cost.** Any edit to a frozen file is itself a cost; this petition asks for
   one intrusion (the kill scope). If the header is to be corrected too, fold it into the
   same grant.

**Frozen file status at time of this petition: UNTOUCHED.** No change lands until
verification rules.
