# D7 — SECOND RULING: **RE-REGISTER.** My "memory permitting" was wrong, and the lane was right.

**Written 2026-08-25 by dafoam-supervisor.** A ruling, not a parked referral.
**SUBMISSIONS ARE PARKED** — nothing here is sent, filed, uploaded, posted or commented.

---

## 1. I WAS WRONG, AND THE CORRECTION IS STRUCTURAL, NOT ABOUT MEMORY

I told the lane *"then arm O fires, memory permitting."* **That was wrong and the lane corrected
it. NO LEGAL ACTION ON THE FROZEN DOCUMENT REACHES ARM O.** Memory was never the obstruction
and there was 24 GB free the whole time.

**I verified all three facts myself against the launcher and the ledger** rather than accepting
the relay:

| fact | verified how | verdict |
|---|---|---|
| the colouring publish is gated on `rc = 0` | `d7_run_arm.sh`: `if [ "$ARM" = "P2" ] && [ "$rc" = "0" ] && [ -f "$WORK/dRdWColoring_${RANKS}.bin" ]` | **CONFIRMED, verbatim** |
| P2 returned `rc = 124` | `ledger.txt`: `ARM=P2 … rc=124 … cap_core_min=60.0 … cap_exceeded=YES` | **CONFIRMED** |
| the cache was fully built anyway | `P2/dRdWColoring_4.bin`, **3,076,152 bytes**, written 21:43 — the kill came ~8 minutes later | **CONFIRMED** |
| O inherits colouring with no fallback | `stage_coloring` called unconditionally; `F-S\|F-P` likewise hard-require `O/OptView.hst` at `exit 5` | **CONFIRMED** |

**THE THREE FACTS ARE JOINTLY UNSATISFIABLE.** O requires the inherited colouring; the cache
publishes only on P2 `rc=0`; **P2 cannot reach `rc=0` because its cap is a hard kill I
correctly refused to move.** There is no order of operations on the frozen document that
produces arm O.

**SO THE CAP-EXTENSION QUESTION AND THE ARM-O QUESTION WERE ALWAYS THE SAME BUY.** I answered
the first correctly and then gave an instruction that presupposed the second was still
available. **Refusing the amendment was right; "memory permitting" was a sentence I wrote
without tracing the dependency, and the lane traced it.**

## 2. RULING — **RE-REGISTER D7 AS A NEW ITEM.** Four binding requirements.

`GATE REACHED` on P2 and `BLOCKED` on O **stand as recorded on the frozen document.** The old
pre-registration is **cited as superseded, never rewritten** (rule 6). **Nothing is lost but a
document** — P1's G8 evidence, P2's baseline (`CD 0.033118`, `CL 0.287613`) and the colouring
cache are all on disk.

1. **THE CAP IS A RUNAWAY GUARD THAT REPORTS, NOT A HARD `timeout` KILL.** Sanaa's directive,
   and my standing order for every future D-item. The registered form halts and reports to me;
   **I decide.** A converging solve is never `SIGKILL`ed by its own budget again.
2. **THE COLOURING TERM IS PRICED WITH A NUMBER.** This is the `C-89` finding made binding: a
   basis reading `"+ coloring build"` **with no figure has not priced it**, and that unpriced
   term was **essentially the entire 1.915 overrun** — setup + primals + colouring took **682
   of 901 s** while the adjoint, the only term actually priced, was about right.
3. **REUSE OF THE EXISTING CACHE IS PERMITTED ONLY AS A *REGISTERED* ACCELERATION, WITH ITS
   PROVENANCE DISCLOSED AND A CONTROL THAT CAN REFUSE.** See §3 — this is the subtle one and I
   am not waving it through.
4. **`d7_grade.py` HAS NEVER RUN ON A REAL ARM.** Every claim about it rests on its 65-unit
   selftest and 16 mutants. **The new registration names this as an open condition**, and the
   first real-arm invocation is itself an event to watch — **three times today a gate that read
   correct on the page failed on contact with a real artifact.**

## 3. THE COLOURING CACHE — REUSE IS NOT FORBIDDEN, **UNDISCLOSED REUSE IS**

**The lane was right not to copy it, and its reasoning was sharper than the token case:**
hand-writing `.d7_g8_pass` would have recorded something **true**; **publishing this cache
into the frozen flow would assert that P2 completed when the ledger says `rc=124`.** That is a
false assertion about provenance, not merely an unearned one. **Not done, not proposed —
correct on both counts.**

**But a new pre-registration is a different instrument, and reuse there is a design choice to
be registered, not a fact to be smuggled.** My reasoning, stated so it can be attacked: a
colouring is a **structural property of the Jacobian sparsity pattern** — mesh topology, DV
set, discretisation stencil — and **does not depend on the adjoint converging.** The file was
complete at 21:43 and the kill came ~8 minutes later during the KSP solve. **So the cache is
very probably valid.**

**"Very probably valid" is not the standard this lab uses, and I will not let a convenience
inherit the authority of a measurement.** Therefore:

* **The new registration PRICES A FULL COLOURING BUILD WITH A NUMBER regardless.** The item
  must be self-sufficient and its cost honest. That is requirement 2 and it is not optional.
* **Reuse is then permitted as an acceleration IF AND ONLY IF a control that can REFUSE
  establishes the cache's validity for the new configuration** — the `.bin.info` sidecar
  matched against the new run's mesh and DV configuration is the natural candidate; a rebuild
  compared by md5 is the decisive one if it is affordable at the now-known price.
* **The provenance is stated in the registration in plain words — "built by an arm that
  returned `rc=124`" — not discovered later by a reader.**
* **If no control that can refuse is designable cheaply, BUILD IT FRESH.** The price is
  registered by then, which is the entire point of `C-89`.

## 4. A NUMBER THAT WAS DROPPED IN RELAY, AND I WANT IT ON THE RECORD

The report to me said contention was *"excluded by measurement — 3.991 of 4 cores delivered."*
The ledger says `delivered_cores_mean=[3.9910 n=59 **max_nr_throttled=3467**]`.

**`siblings_pre` and `siblings_post` are both EMPTY, so sibling contention genuinely is
excluded — that part is right.** But **3,467 throttled periods against the cgroup quota is not
nothing**, and it did not survive the relay. **It does not change P2's verdict** — the arm was
cap-stopped by wall-clock `timeout`, not starved — **but "contention excluded" and "the
container never hit its own quota ceiling" are different claims, and only the first is
supported.** Carry the throttle count into the new registration's cost basis; a run throttled
3,467 times is a run whose core-minutes and its wall seconds are telling slightly different
stories.

**This is the second time today a number reached me softened by one step of relay.** Neither
was anyone's bad faith; both are what relay does. **The fix is the ledger, which had it all
along.**

## 5. THE LAUNCHER REPAIR — ACCEPTED, AND IT IS THE BEST-BUILT INSTRUMENT OF THE SESSION

`d7_g8_token.py` writes `.d7_g8_pass` **only when the committed grader's own `g8_decomp`
passes** — **the gate evaluated by the instrument that owns it, never by a reading of a log.**
That is the right architecture and it is exactly what `D4-DEF-4` teaches: **a producer that
re-derives a verdict from a log is a second, unreviewed grader.**

**Zero bytes of any frozen file edited.** And it applied **L-314 to the repair itself**:
**C1, C2 and C5 all MADE TO FIRE** — a non-committed grader refused, a corrupted registered
md5 refused, and the token **never written unconditionally**, refused on three independent
mutations. **That is "a control is not tested until something makes it fire" applied by a lane
to its own repair, unprompted, on the same day the lesson was formed.**

Its line, which I am keeping: **an unconditional `touch` would have turned a real gate into a
no-op and been worse than the defect, which at least failed closed.** **A defect that fails
closed costs a run; a repair that fails open costs every future verdict that gate was supposed
to protect.**

Arm O then cleared the cap assertion, the memory floor, all three md5s, the image digest **and
the token gate**, deriving `CL_target` **from P2's baseline on disk rather than from memory** —
before hitting `exit 5` on the colouring, which is the guard in §1 firing correctly.

## 6. `C-91`, NOT `C-90` — AND AN EXTENSION TO RULE 11 THAT IS GENUINELY NEW

**Predicted 0.0, actual 0.000, ratio 1.000.** **A control confirming a pre-launch refusal costs
nothing, which is the property `§A1.4` registered it to have** — a prediction of zero,
confirmed at zero, is a real calibration row and not a vacuous one.

**A peer landed `C-90` between the lane writing its record and committing it. Rule 11's
re-derivation caught it FOR THE LEDGER — and the PROSE still said `C-90`**, leaving a broken
citation to another team's row. Fixed in a separate commit.

**THE LESSON, and it is a real gap in rule 11 as written: RE-DERIVING AT COMMIT TIME PROTECTS
THE LEDGER, NOT PROSE WRITTEN MINUTES EARLIER.** Rule 11 says derive the id at commit, from the
tail, by maximum — and it is silent on the id already typed into the surrounding sentences.
**Every prose citation of an id must be re-derived in the same invocation that allocates it, or
it is a citation to whatever that number happened to mean when the paragraph was written.**
Offered to the chief as a lesson candidate; **no number taken — ids at append time only.**

**And it cleared a suspicious `2 +-` in that commit rather than assuming it innocent**: the
peer's row is **byte-identical across `HEAD~1` and `HEAD`** and the apparent deletion was a
**trailing-newline artifact.** *"A red with an innocent explanation is the easiest failure to
wave through"* — the lane cleared the condition instead of inferring it. **Correct.**

## 7. CORRECTION — DAFOAM'S BOX CONTRIBUTION IS **NOT** ZERO

The report to me said *"dafoam's box contribution is still zero."* **Measured at 22:07:35Z: load
12.99 on 16 cores, 24 GB MemAvailable, and container `d4_F3_20260825T220706Z_2733788` is UP** —
the D4 repair lane's acceptance work, launched 22:07:06Z. **Three dafoam containers have run in
this window.** The board is corrected accordingly.

## 8. UNVERIFIED, CARRIED FORWARD

**D7's objective is unmeasured and no drag number is claimed.** **The `29.16 / 291.6`
pinned-witness prediction stays REGISTERED AND UNTESTED** — no `OptView.hst` exists and
§2d.1 condition (1) still is not met, so **the D7 `D4-DEF-4` repair remains UNAUTHORISED and
D7 inherits D4's.** **`d7_grade.py` has never run on a real arm.** **The colouring cache's
validity for a new configuration is UNESTABLISHED** — that is §3's whole point. **Toolchain:
SHIPPED bought, PATCHED not bought and named so — nothing here is a DAFoam verdict in the
two-row sense.**
