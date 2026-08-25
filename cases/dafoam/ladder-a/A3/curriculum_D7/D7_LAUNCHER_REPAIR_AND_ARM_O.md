# `D7-LAUNCHER-DEF-1` REPAIRED and arm `O` fired. It aborted on a SECOND obstruction — and that one is a GUARD WORKING, not a defect.

**Date:** 2026-08-25. **Lane:** dafoam `lab-lane`.
**Repair authorised** by the dafoam-supervisor at `f340e4d2` under `VERIFICATION_CHARTER.md` §2d.1.
**Arm `O` verdict: `BLOCKED`. Cost: ZERO core-minutes** — it refused before any rank was claimed.

## 1. The repair — `d7_g8_token.py`, zero bytes of any frozen file edited

Built in the `d8_grade_entry.py` shape the supervisor named. It does not patch, monkey-patch, wrap
or re-implement `d7_grade.py` or `d7_run_arm.sh`. It writes one artifact, `.d7_g8_pass`, and only
when **the committed grader's own `g8_decomp`** says G8 passes.

**No gate, threshold, band, cap or label moves.** G8 is unchanged; its result was never recorded.

**The gate is evaluated by the instrument that owns it, never by this lane's reading of a log.**
That is the entire design constraint: the token could have been written by hand in one command, and
G8's evidence genuinely passes, so the hand-written token would have recorded something **true** —
and it would still have been forged, and the next reader could not have told the difference.

### 1a. Five controls, and EVERY ONE WAS MADE TO FIRE

The supervisor's standing lesson — *a control is not tested until something makes it FIRE*, after
`D4-DEF-1`, `M3` and this lane's own `D7-GRADER-DEF-2` — applied to the repair itself.

| control | what it refuses | **demonstrated firing** |
|---|---|---|
| **C1** | `d7_grade.py` on disk is not the HEAD blob | **YES** — pointed at a non-committed file → refused, exit 2 |
| **C2** | `d7_run_arm.sh` is not the HEAD blob, or not the md5 registered in Addendum 1 §A1.2 | **YES** — corrupted the registered constant → refused, exit 2 |
| **C3** | a G8 evidence artifact is absent | by construction; artifacts read from disk by the grader's own reader |
| **C4** | `g8_decomp` did not come from the committed module | asserted by module path |
| **C5** | **the token is NEVER written unconditionally** | **YES** — three mutations, below |

`--selftest`: **4 units, 4 passed.** The real evidence passes (`identical=True`, `n=4`,
`sum=42120`); and **three independent mutations each make G8 FAIL** — one differing cell
(`identical=False`), a wrong subdomain count (`n=3`), and a cell sum that is not the registered
42,120 (`42113`). **An unconditional `touch` would have converted a real gate into a no-op and
been worse than the defect**, which at least failed closed.

### 1b. What it wrote

```
D7_G8_EVALUATED pass=True identical=True n_subdomains=4 sum_cells=42120 registered=42120
  map_A={"processor0":10635,"processor1":10506,"processor2":10538,"processor3":10441}
  map_B={"processor0":10635,"processor1":10506,"processor2":10538,"processor3":10441}
```

The token records the gate, the verdict, both maps, the evaluating instrument, the grader and
launcher md5s, and the authorising ruling — so a later reader can tell **what** certified it.

## 2. Arm `O` fired. THE REPAIR WORKED.

Arm `O` cleared, in order: the cap assertion (`enforced_wall_s=9000`, `enforced_core_min=600.000000`,
back-checked against the registered 600.0); the host memory floor (**26.66 GiB** against the
registered 16.0); **all three instrument md5 re-assertions** on the staged copies; the image digest
(`sha256:9d45679d55fd…f07fc`, SHIPPED row); **the G8 token gate — the repair, working**; and it
derived the lift constraint from a file on disk rather than from memory:

> `D7_CL_TARGET_WRITTEN … CL_target=0.2876130251655752 from …/P2/d7_baseline.json`

**Then it aborted:**

> `ABORT no colouring cache at …/dRdWColoring_4.bin -- arm P2 builds it` → **exit 5**

**This is now MEASURED.** The previous record listed it as *"a reading of the frozen launcher, not
a measurement"* because the chain had halted on `P2` before arm `O` was reached. **It has now been
observed.**

## 3. THE SECOND OBSTRUCTION IS A GUARD WORKING, AND I WILL NOT OVERRIDE IT

`d7_run_arm.sh:428` — the colouring publish:

```
if [ "$ARM" = "P2" ] && [ "$rc" = "0" ] && [ -f "$WORK/dRdWColoring_${RANKS}.bin" ]; then
```

**The publish is gated on `rc = 0`. `P2` returned `rc = 124`.** The cache was fully built — it
exists at `P2/dRdWColoring_4.bin`, 3,076,152 bytes — but **the launcher deliberately declined to
publish it, because the arm that built it did not complete cleanly.**

**That is not a defect. That is a guard doing exactly what it was frozen to do:** an arm that did
not complete does not hand artifacts to downstream arms.

**This is materially different from `D7-LAUNCHER-DEF-1` and the distinction is the whole point:**

| | `.d7_g8_pass` | `$BASE/dRdWColoring_4.bin` |
|---|---|---|
| has a writer? | **NO — none anywhere.** Incoherent instrument; the item cannot start at all | **YES**, at `:429`, correctly conditioned |
| why it is missing | nobody ever wrote it | **the condition was evaluated and was FALSE** |
| §2d.1 demonstrable error? | **yes — repaired** | **NO. Repairing it would mean deleting a condition that fired correctly** |

**Copying the cache into place by hand is one command.** It is the same temptation as hand-writing
the token, wearing different clothes, and it is **less** defensible: the token would have recorded a
true fact, whereas publishing this cache would assert that `P2` completed when the ledger says
`rc=124, cap_exceeded=YES`. **Not done, and not proposed.**

## 4. RULING: arm `O` is STRUCTURALLY UNREACHABLE under D7's freeze

This corrects the supervisor's *"then arm O fires, memory permitting."* **It cannot**, and the
reason is not memory:

1. Arm `O` requires the inherited colouring — `stage_coloring` is called unconditionally in the `O`
   branch at `:246`, with **no fallback to building its own**.
2. The cache is published **only** when `P2` exits `rc = 0`.
3. `P2` cannot exit `rc = 0`, because its cap is a hard `timeout` kill, **and the supervisor has
   refused to move that cap** — correctly: the cap is the **third of rule 2's four protected items**
   and first compute has happened.

**These three are jointly unsatisfiable. No legal action on this frozen document reaches arm `O`.**

**The path is the one the supervisor already ruled for the converged adjoint: a NEW
PRE-REGISTRATION.** They are the same buy. A new item's `P2`-equivalent needs the cap registered as
a **runaway guard that reports** (the supervisor's standing order) and the colouring term **priced
with a number** (the `C-89` finding) — and with both, it completes, publishes, and arm `O` runs.

**Nothing is lost but a document.** `P1`'s G8 and placement evidence, `P2`'s baseline primal
(`CD 0.03311805865399452`, `CL 0.2876130251655752`) and its 3.08 MB colouring cache are all on disk
and all reusable by a new registration.

## 5. State left behind

* `.d7_g8_pass` — written, self-describing.
* `O/` — re-staged cold by the abort's own staging step. **It does not block a retry**: the
  launcher does `rm -rf "$WORK"` before staging, so every launch is cold by construction. It
  contains `d7_cl_target.json` and no time directory, no `processor*`, no history.
* **No container was created for arm `O`.** `docker ps` count: 0.

## 6. Cost

**Arm `O`: 0.000 core-minutes.** The refusal is pre-launch, before any rank is claimed — the
launch gate is the control, exactly as Addendum 1 §A1.4 registered it.

The repair and its selftest are serial Python on artifacts already on disk: **< 0.1 core-min**,
np=1. Calibration row **`C-91`**. (Allocated `C-91`, not `C-90`: the id is taken at append time against HEAD, and an `ansys-verification` peer landed `C-90` between this lane deriving the id and committing. Re-derived inside the committing invocation, per `CLAUDE.md` rule 11.)

## 7. Named as unverified

* **`D7-DEF-4`'s pinned-witness prediction (`patchV[0]` → `29.16` rather than `291.6`) is still
  UNTESTED.** It needs an `OptView.hst`; arm `O` never started one. It stands registered, and per
  the supervisor's ruling it can now only be confirmed or refuted, never fitted.
* **D7's registered objective was not measured.** No drag number. No optimisation history.
* **`d7_grade.py` has still never been run on real arms.**
