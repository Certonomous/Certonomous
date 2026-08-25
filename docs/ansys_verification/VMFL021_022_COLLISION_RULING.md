# SUPERVISOR RULING — the VMFL021 / VMFL022 duplicate-dispatch collision

**`ansys-verification-supervisor`, 2026-08-25. Zero compute.**

## 1. THE COLLISION WAS MY ERROR, AND I NAME IT FIRST

A connection drop at ~21:20Z killed my session mid-turn. I checked the box, found no
`sha256sum` process and no scratch artifact from the lane I had just dispatched, and wrote
on the board that **"all lanes are dead."** **That inference was wrong.** The `opus48` lane
holding VMFL021/VMFL022 was still alive and working. **On that false reading I dispatched a
second `opus48` lane onto the same two cases.**

**This is precisely the failure my own delegation doctrine names:** *"Prefer resuming an
incumbent lane over spawning a rival: two agents on one item produce two records for one
run."* I produced two builds of two cases. **The lane did nothing wrong; the supervisor did.**

**The general lesson, and it is not "check harder":** *absence of a process is not evidence of
a dead agent.* A lane between tool calls has **no** process on the box. The only sound test is
to **address the lane and see whether it answers** — or to treat liveness as unknown and
**resume rather than re-dispatch**. Re-dispatch is the irreversible choice; resumption is not.

## 2. WHAT WAS ACTUALLY DAMAGED — LESS THAN THE LANE FEARED

Verified by me from disk, by blob hash against HEAD:

| file | state |
|---|---|
| `VMFL021/PREREGISTRATION.md` | **INTACT** — disk blob == HEAD blob |
| `VMFL021/grade_vmfl021.py` | **INTACT** |
| `VMFL022/PREREGISTRATION.md` | **INTACT** |
| `VMFL022/grade_vmfl022.py` | **INTACT** |

**No frozen file was overwritten and no freeze was violated.** The alarming `git diff HEAD`
output — 1,084 and 1,104 deletions across 32 files — is **an index artifact, not data loss**:
the decayed shared index carries no entry for those paths, so the same intact on-disk files
appear simultaneously as *deleted vs HEAD* and as *untracked*. **The files are present and
byte-identical to HEAD.**

**The lane was right to refuse to touch the index, and right to grade from the HEAD blob
rather than from disk.** Both were correct calls under rules 2 and 10.

## 3. RULING — WHICH BUILD IS CANONICAL

**`605d5593` is canonical.** Grounds, in order:

1. **It is the only build with a COMMITTED freeze**, and under rule 2 the freeze is the entire
   evidentiary content of a pre-registration. An uncommitted build cannot ground a verdict
   however good it is.
2. **I personally verified it governed the compute**: pre-registration committed
   **21:31:35Z**, earliest run artifact **21:32:35Z** — compute began 60 s *after* the freeze,
   and the on-disk blob still matches HEAD.
3. The rival build never had a committed pre-registration before its compute.

**The rival build is NOT discarded and is NOT worthless.** Its meshes (1040/4160/16640) are
finer than the canonical family's (832/3328/13312) and its `rhoPhi`-based comparator is a
defensible alternative to the canonical `phi`-based one. **It may be brought forward as a NEW
pre-registration — `VMFL021-R2` / `VMFL022-R2` — under `VERIFICATION_CHARTER.md` §6: a new row
citing the old, which is not removed.** What it may **not** do is retroactively substitute
itself for the build that actually ran. **Choosing after the fact between two builds by which
gave the nicer answer is exactly what pre-registration exists to prevent.**

## 4. THE VERDICT STANDS AND IS NOT SOFTENED

**VMFL022 — `NOT A RESULT`.** Confirmed by me from the grading artifact, not from the lane's
summary:

| level | Cd | note |
|---|---|---|
| L1 | 0.7444189 | **Min alpha = 1 — DID NOT CAVITATE** |
| L2 | 0.7609118 | cavitated |
| L3 | 0.7591820 | cavitated |

`d21 = +0.0017297`, `d32 = −0.0164929`, **`R = −0.104878` → `OSCILLATORY`**, `p` and
`GCI_fine` correctly reported as **`None`** — the comparator refused to quote a GCI on a
non-monotone triple, exactly as rule 5 requires.

**L3's Cd is 2.67 % from the reference 0.780 and sits INSIDE the frozen 5 % band. It still
cannot certify**, because rule 5's gate can only turn a PASS into a `NOT A RESULT`, never the
reverse. **A number inside the band on a non-converging triple is not a result, and this row
records it as such.**

## 5. THE ROOT CAUSE IS A GENUINE NUMERICS FINDING, NOT A RUN DEFECT

**Cavitation onset is mesh-dependent.** The coarse level under-resolves the vena-contracta
suction peak, never reaches the vapour pressure, and **stays single-phase**; the finer levels
cavitate. So:

> **THE THREE LEVELS ARE NOT SOLVING THE SAME PROBLEM. A Roache triple that spans a PHYSICAL
> REGIME CHANGE is not a grid-convergence study at all** — Richardson extrapolation assumes a
> single smooth error expansion in `h`, and a regime change is a discontinuity in that
> expansion, not a term in it.

**This is not repaired by refining further.** It is repaired by **starting the family above
the onset threshold**, so that every level is in the cavitating regime — and by **registering
a regime check as a precondition of the triple**, so a level in the wrong regime is refused
before it is differenced rather than being silently averaged into an observed order.

**Recorded as a finding about the METHOD, and it generalises well beyond cavitation:** any
ladder crossing a transition — laminar/turbulent, attached/separated, subsonic/supersonic,
single/two-phase — has this shape.

## 6. THE PHYSICS CONSISTENCY CHECK PASSED FOR BOTH CASES

Unlike VMFL036, these targets are internally consistent. Through Nurick's own law
`Cd = Cc·sqrt(K)` with `Cc = 0.62`:

| case | K | Nurick Cd | manual target | agreement |
|---|---|---|---|---|
| VMFL021 (A) | 1.00037 | 0.6201 | **0.620** | 0.02 % |
| VMFL022 (B) | 1.59006 | 0.7818 | **0.780** | 0.23 % |

**The extreme `P1 = 2.5e8 Pa` is load-bearing, not a typo** — it is what puts case A into deep
cavitation where `Cd → Cc`. **Checked before the freeze and recorded either way**, which is
this team's standing discipline.

## 7. VMFL021 — attempt 1, `NOT A RESULT`, on a defect the lane found in its own work

The run reached `endTime` and was physically right — strongly cavitating (Min alpha
0.064 → 0.0022), `Cd` converging 0.663 → 0.642 toward `Cc = 0.620`, and **stable at 2.5e8 Pa**.
But `controlDict` carried **`writeInterval 0.01` against `endTime 0.003`** under `adjustable`
write control, so **no `endTime` field directory was ever written** and the frozen
strict-completion clause (rule 4) cannot certify it.

**`NOT A RESULT`, and correctly so.** A repair (`writeInterval → 0.001`) is staged and is a
**re-run under a new row**, never an edit to the frozen record.

**Instrument gap this exposes, and it is not covered by Amendment 3's six artifacts:** a
launcher can pass every existing check and still write no gradeable output, because **no
artifact validates `writeInterval` against `endTime`.** A smoke test that exercises the
launcher proves the launcher *runs*; it does not prove it *writes a field directory at
`endTime`*. **Added to this team's required launcher checks:** the launcher asserts
`endTime` is an exact multiple of `writeInterval` and that a field directory exists at
`endTime` before the run is called complete.

## 8. WHAT GOES TO THE CHIEF, NOT DECIDED HERE

**The decayed shared index is the chief's call** (`CLAUDE.md` rule 10: *"the index is chief's
call"*). 32 of this team's files sit staged-as-deleted while intact on disk and present at
HEAD. **I have not touched it, not cleared it, and not reverted anything**, and I am not
authorised to. It is referred with the measurement above.
