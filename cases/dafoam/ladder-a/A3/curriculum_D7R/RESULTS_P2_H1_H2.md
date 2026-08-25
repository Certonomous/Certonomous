# D7R — `P2` COMPLETED `rc=0`, the thing D7 could never do. `H1` and `H2` both TESTED. Arm `O` running.

**Date:** 2026-08-25. **Lane:** dafoam `lab-lane`. Pre-registration frozen `88690717`.

## 1. `P2` — rc=0, and the re-priced basis was ACCURATE

| | |
|---|---|
| rc | **0** — D7's `P2` returned `rc=124` |
| wall | **941 s** |
| cost | **62.733 core-min** |
| CAP / CEILING | 120.0 / 480.0 |
| runaway guard | **`cap_exceeded=no cap_reported=no ceiling_hit=no`** — it finished *inside* the cap |
| **predicted** | **60.1** → **ratio 1.044** |

**R1 and R2 are both vindicated by this row, and they are separable claims:**

* **R1 (runaway guard).** The cap was never crossed, so the report path did not fire — **but the
  hard `timeout` that killed D7's `P2` at 901 s is gone, and this arm ran 941 s.** Under D7's
  launcher this run would have been `SIGKILL`ed 40 s before it finished.
* **R2 (price the colouring).** **60.1 predicted against 62.733 measured is a 4.4 % error**, on an
  arm whose predecessor missed by **2.002×**. The difference is one number: the colouring, priced
  at **24.43 core-min** from D7's own log instead of appearing as the words *"+ coloring build"*.
  **`C-89` paid for itself on the first arm that used it.**

## 2. GATE `H2` — PASS, at exactly zero

The re-measured baseline against D7's inherited value:

| | D7R (re-measured) | D7 (inherited) | rel. diff | `H2` (≤ 1e-6) |
|---|---|---|---|---|
| `CD` | `0.033118058653994517` | `0.033118058653994517` | **0.000e+00** | **PASS** |
| `CL` | `0.28761302516557519` | `0.28761302516557519` | **0.000e+00** | **PASS** |

**Bit-for-bit identical on an independent run, in a fresh container, from a cold stage.** D7's
`P2` baseline is reproducible, and the primal path is deterministic at np=4 `scotch` on this mesh.
**The inherited number is no longer inherited — it has been re-derived**, which is what `H2` was
registered to force.

## 3. THE CROSS-CHECK I DID NOT HAVE TO RUN, AND WHAT IT SETTLES

The fresh colouring against the one this item **declined** to reuse:

| | md5 | size |
|---|---|---|
| D7's cache — built by the **`rc=124`** arm | `a2e5f3172f3b889656e51b67ca4e55a6` | 3,076,152 |
| D7R's fresh build — **`rc=0`** arm of this item | `a2e5f3172f3b889656e51b67ca4e55a6` | 3,076,152 |

**BYTE-IDENTICAL.** This is the **md5-rebuild control** the ruling called *"the decisive one"* — and
it has now been performed. **The declined cache was valid.** The supervisor's structural reasoning
was correct: a colouring is a property of the Jacobian sparsity and does not depend on the adjoint
converging.

**And the conclusion runs the other way from the obvious one.** The rebuild is **the only reason
anyone knows** it was valid. Reusing it would have been right *and unjustified*, and the record
would have shown a validity check that no instrument could perform — the `.bin.info` sidecar being
22 bytes of PETSc option string that cannot tell one mesh from another.

> **The 24.43 core-min did not buy a colouring. It bought the knowledge that the colouring was
> valid — which is the thing no cheap control could have supplied. Being right for an unavailable
> reason is not the same as being right.**

## 4. GATE `H1` — TESTED THREE WAYS, ALL THREE FIRE

Earlier this gate was **unreachable** for testing: the CL-target guard sits ahead of
`stage_coloring`, so `H1` could not be exercised until `P2` produced a baseline. **`P2` has, so it
was tested — with distinct named refusals, not a generic one.**

| case | planted state | result |
|---|---|---|
| **A** | provenance record **absent** | **exit 5** — `no provenance record; the cache was not built by an rc=0 arm of THIS item` |
| **B** | provenance from **another item** (`item=D7`) | **exit 5** — `provenance record is not this item's` |
| **C** | this item, **`rc=124`** — *exactly the D7 situation* | **exit 5** — `the arm that built the cache did not return rc=0` |

**Case C is the one that matters**: it is the precise state D7 was left in, and `H1` refuses it by
name. **Zero containers were created by any of the three.** The provenance record was restored and
verified **byte-identical** to the original.

Then, on the real run, `H1` passed **legitimately**:
`D7R_H1_PASS item=D7R arm=P2 rc=0 stamp=20260825T222104Z_2765730 md5=a2e5f3172f3b889656e51b67ca4e55a6`

## 5. Arm `O` — RUNNING. The first D7-family optimisation driver to start.

Container `d7r_O_20260825T223806Z_2844774`, fired 22:38:06Z at MemAvailable 26.81 GiB.
`D7R_RUNAWAY_GUARD arm=O cap_core_min=900.0 ceiling_core_min=3600.0 mode=report_then_stop_at_ceiling`.
CL target derived **from disk**: `0.2876130251655752`.

**The `D7-DEF-4` witness test is armed and will fire the moment `OptView.hst` is stable.** It
measures three things, not one: whether `getValues(scale=True)` and `(scale=False)` are identical —
**the mechanism claim this lane cited from D4's ruling and has never measured on this box** — what
the frozen extractor returns for the pinned `patchV[0]`, and the same for `twist[1]` and
`shape[115]`. **The prediction (`29.16`, not `291.6`) was registered before the artifact existed and
cannot now be fitted.**

## 6. A DEFECT IN MY OWN LAUNCHER — `D7R-LAUNCHER-NOTE-1`

The R1 transformation replaced D7's `timeout … > "$LOG"` with a detached container, and the log is
now written by `docker logs` **only after the container exits**. **A running arm therefore has no
log file**, and `ls $R/P2_*.log` returns nothing mid-run.

**This is a monitoring regression, not a correctness one** — the log is complete and correct at
exit, and the ledger, cost accounting and gates are unaffected. **It is recorded rather than
repaired**: the launcher is frozen at `88690717` and first compute has happened. **Workaround:
`sudo -n docker logs <container>` streams live.** The next registration should tee the container's
output to the log file as it runs.

## 7. Standing

* `P1` **PASS** · `P2` **rc=0, gates `H1`/`H2` PASS** · `O` **RUNNING** · `F-S`/`F-P` **BLOCKED** on
  `D4-DEF-4`, whose repair this item does not author.
* **`d7_grade.py` has still never run on a real arm** — registration **R4**, open. `P1` and `P2`
  artifacts now exist for it to be run against, and per R4 its first real-arm invocation is an event
  to watch, not a formality.
* **Toolchain: SHIPPED bought for `P1`, `P2`, `O`. PATCHED NOT BOUGHT** — registered to `F-P` only,
  which is gated. **Not a two-row DAFoam verdict, and it does not claim to be.**
