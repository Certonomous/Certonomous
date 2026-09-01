# AOA POLAR — RESULTS, both arms (FEASIBILITY READINGS, NOT VERDICTS)

**Items:** `AOAI` (incompressible), `AOAC` (compressible) · **Ladder:** A1
**Pre-registrations:** `AOAI_PREREGISTRATION.md` @ `ba8b501c`,
`AOAC_PREREGISTRATION.md` @ `338b539b`, amended pre-compute @ `c989b956`
**Ran:** 2026-09-01, 16:24:27Z (AOAI) and 16:27:41Z (AOAC), concurrently on cores 14 and 15

> **THESE ARE READINGS, NOT VERDICTS.** No grid triple exists for any point, so
> under Sanaa's convergence-prerequisite doctrine nothing here is a graded
> result. A band attaches only when the wing convergence ladder lands. Nothing
> is filed, sent or posted outside this box.

---

## 1. THE HEADLINE

**Both arms converged at α = 0…8° and failed at α = 9…18°. Nine points each,
ten failures each, and the two arms agree on the boundary to the degree —
across two different solvers and a tenfold difference in Reynolds number.**

| | AOAI (incompressible) | AOAC (compressible) |
|---|---|---|
| solver | `DASimpleFoam` | `DARhoSimpleFoam` |
| Re | ≈ 6.67e5 | ≈ 6.54e6 |
| declared points | 19 | 19 |
| segments present | **19** | **19** |
| **CONVERGED** | **9** (α = 0…8) | **9** (α = 0…8) |
| **NOT CONVERGED** | **10** (α = 9…18) | **10** (α = 9…18) |
| NOT MEASURED | 0 | 0 |
| reader | **11/11 controls PASS**, G-STALL PASS | **11/11 controls PASS**, G-STALL PASS |

Every non-converged point ran to the registered 1000-iteration cap and raised
`AnalysisError: … Primal solution failed!`. **No point was dropped, retried,
relaxed, re-tuned, or replaced by a transient.**

### The converged polar

| α° | AOAI CL | AOAI CD | AOAI it | AOAC CL | AOAC CD | AOAC it |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.000000 | 0.015252 | 314 | 0.000000 | 0.010919 | 338 |
| 1 | 0.100443 | 0.015446 | 425 | 0.108231 | 0.011136 | 496 |
| 2 | 0.200150 | 0.016050 | 415 | 0.215554 | 0.011808 | 489 |
| 3 | 0.298406 | 0.017062 | 404 | 0.320909 | 0.012936 | 474 |
| 4 | 0.394097 | 0.018557 | 389 | 0.422885 | 0.014600 | 449 |
| 5 | 0.486291 | 0.020581 | 373 | 0.520194 | 0.016863 | 428 |
| 6 | 0.573332 | 0.023245 | 363 | 0.610175 | 0.019878 | 397 |
| 7 | 0.653474 | 0.026710 | 353 | 0.689490 | 0.023911 | 363 |
| 8 | 0.723547 | 0.031217 | 378 | 0.751784 | 0.029541 | 516 |

CL = 0 exactly at α = 0 on a symmetric section, in both arms, is the sanity
check the geometry and the force directions had to pass and did.

---

## 2. ⚠ MY REGISTERED EXPECTATION WAS WRONG, AND IT WAS WRONG IN THE OPTIMISTIC DIRECTION

`AOAI_PREREGISTRATION.md` §4.3 and `AOAC_PREREGISTRATION.md` §4.3 registered:

> "I expect points above roughly 12–14° may not converge steady."

**The first failure is at α = 9° in both arms — three to five degrees below the
registered band. THE PREDICTION IS REFUTED, NOT CONFIRMED.**

This is recorded as a refutation rather than absorbed, because that is the whole
point of registering it. Had it not been written down first, "the solver stops
around 9°" would have read as an unremarkable observation instead of what it is:
**evidence that I understood the case less well than I claimed to.** The band was
argued from general knowledge of 2-D steady RANS past stall and not from anything
measured on this mesh, and the measurement disagrees with the argument.

---

## 3. ⚠⚠ WHAT THESE FAILURES ARE NOT

**NO STALL ANGLE IS REPORTED HERE, AND NONE MAY BE DERIVED FROM THIS DOCUMENT.**

The ten failures per arm are evidence that **the steady solver stopped
converging**. They are **not** evidence of stall. The reader enforces this
structurally: no function computes a stall angle, and **G-STALL** refuses at
exit 2 on any output binding a stall word to a numeric angle. It **PASSED** on
both arms — i.e. neither reading contains such a claim. Controls C7/C7b prove
the guard fires on a planted claim and does not fire on the honest caveat.

**And the mirror, which is the half usually left out:** the nine points that
**did** converge are not thereby trustworthy at the top of their range either.
This is a 4,032-cell wall-function mesh (y+ 16.7–92.4). It cannot resolve a
separated boundary layer at any angle. **Convergence and correctness are
independent here.**

**The lift-slope indicator, reported as an indicator only:** AOAI falls from
91.6 % of thin-airfoil (0→1°) to 63.9 % (7→8°); AOAC from 98.7 % to 56.8 %. A
falling slope is consistent with the lift going nonlinear. **It is not a
separation measurement** — that needs wall shear, which this rung does not buy,
on a mesh that could resolve it, which this one is not.

---

## 4. THE COLD CONTROLS — THE INSTRUMENT IS LIVE, AND THE FAILURE IS NOT THE PATH'S FAULT

| α | branch | AOAI | AOAC |
|---|---|---|---|
| 4 | continued | CONVERGED, CL 0.394097, **389 it** | CONVERGED, CL 0.422885, **449 it** |
| 4 | **cold** | CONVERGED, CL 0.394097, **441 it** | CONVERGED, CL 0.422885, **502 it** |
| 14 | continued / cold | NOT CONVERGED / **NOT CONVERGED** | NOT CONVERGED / **NOT CONVERGED** |
| 17 | continued / cold | NOT CONVERGED / **NOT CONVERGED** | NOT CONVERGED / **NOT CONVERGED** |

**(1) THE CONTINUATION INSTRUMENT IS LIVE.** At α = 4 the continued point reached
tolerance in **389 iterations against the cold point's 441** (AOAI, −11.8 %) and
**449 against 502** (AOAC, −10.6 %). Equal counts would have meant the warm start
was not being inherited and the "continued" label on this polar was false. It is
not false.

**(2) THE POLAR IS PATH-INDEPENDENT WHERE IT CONVERGES.** At α = 4 the continued
and cold results agree to **|ΔCL|/CL = 5.4e-8** (AOAI) and **4.1e-9** (AOAC).

**(3) THE HIGH-α FAILURE IS A PROPERTY OF THE OPERATING POINT, NOT OF THE
CONTINUATION PATH.** This is the result the controls were bought for. Both cold
controls at α = 14 and α = 17 — started from freestream, inheriting nothing —
**failed exactly as the continued points did, in both arms.** Had the continued
branch failed while the cold branch converged, the failures would have been an
artefact of the chain. They are not.

**Registered caveat, unchanged:** a single upward sweep still does not test
hysteresis, and none is claimed. What §3 of each pre-registration said
disagreement would mean did not arise — the branches agree.

**Continuation provenance:** α = 10…18 each continued from a predecessor that had
not converged, and the readings flag them. They are not comparable with points
continued from a converged predecessor. **The cold controls at 14 and 17 are what
make the high-α failures interpretable at all**, precisely because they carry no
such inheritance.

---

## 5. ⚠ A POST-COMPUTE REPAIR TO THE READER, DISCLOSED UNDER §2d.1

**The reader REFUSED at exit 2 on AOAI's first grading pass. It was right to.**

Three of the eleven controls — **C3, C4 and C6** — were written against the
`WRITER_BUILT` fixture's **literal values** (`Time = 412`; a literal CL). On real
run bytes the mutations **silently no-opped**: C3's `replace("Time = 412", …)`
matched nothing, so the "ran to cap" control never reached the cap and read
NOT MEASURED; C4's split matched nothing, so the "truncated" control read
CONVERGED; C6's CL replacement matched nothing, so the channel cross-check
reported no mismatch. **They passed on the fixture and were dead on the artefact
they had to police.**

**C3 is the zero-passing control** — the one that proves the non-convergence
channel can fire. Without it a polar reading "all CONVERGED" would have proved
nothing. **The reader refused to publish rather than publish with three dead
controls, which is the behaviour rule 3 exists to produce.**

### The four §2d.1 conditions, each discharged

1. **A demonstrable error, not a preference.** The reader printed the proof:
   `C3 … last_time 314 >= cap 1000; got NOT MEASURED` — the mutation had not
   landed.
2. **Established by an instrument independent of the hypothesis.** **By the
   controls themselves, which grade nothing.** They cannot have been selected to
   move a verdict, because they do not know which direction a verdict would go.
3. **Disclosed, instrument named, and what moved quantified.** Named above.
   **What moved: nothing that was published.** The reader had **refused**, so
   there were no pre-repair AOAI numbers. `classify()` — the registered
   convergence criterion — is **byte-untouched**; only the control-construction
   changed. No gate, threshold, cap or label moved.
4. **Pre-repair values recorded beside the published ones.** The refusing output
   is retained at
   `…/CURRICULUM-AOAI-…/AOA_AOAI_read_20260901T162427Z.txt`, beside the repaired
   reading `AOA_AOAI_read_REPAIRED_20260901T163038Z.txt`. AOAC's compute began
   16:27:41Z and its grading ran at 16:31:13Z with the repaired reader, so the
   same disclosure covers it.

### The md5s, so the pin evidence is not erased

`AOAI_MD5.txt` and `AOAC_MD5.txt` are **left as frozen** — they record the pin as
it stood at each pre-registration commit, and rewriting them would destroy the
evidence of what was pinned. The repaired reader's md5 is disclosed here instead:

| `aoa_read.py` | md5 |
|---|---|
| as pinned at `ba8b501c` / `c989b956` (pre-repair) | `0a3bf0bb5a21c8fe3345ae2887ce3bb0` |
| **after the §2d.1 repair** | **`1ce50161c7c59efd16f30449a7640fd7`** |

`classify()`, the registered convergence criterion, is byte-identical between the
two. The diff is confined to control construction.

### The repair, and the general rule it earned

Each mutation is now **artefact-general** — it locates what to change *in the
text* (last `Time =` line, the `AOA_POINT_VALUES` CL field) instead of assuming a
value the fixture happened to carry. And a `mutate()` wrapper now **refuses any
control whose mutation did not change the text**:

> **A CONTROL THAT CANNOT PROVE IT CHANGED ANYTHING IS NOT A CONTROL.**

**This is the second instance of one failure mode in this item, and that is the
finding worth keeping.** The first was `G-PHYS`, whose marker-count limb was
never driven while its md5 limb was — reported PASS, and would have refused the
producer (it did, at the first launch). Both are the same error:

> **A GUARD OR CONTROL VALIDATED ONLY AGAINST A WRITER-BUILT FIXTURE, OR ONLY ON
> SOME OF ITS LIMBS, IS NOT VALIDATED. A PARTIAL SELFTEST REPORTING PASS IS WORSE
> THAN NO SELFTEST, BECAUSE IT BUYS CONFIDENCE IT HAS NOT EARNED.**

Both were caught by the guards themselves, before either could contaminate a
number — which is the system working, but only because the guards refused rather
than degraded.

---

## 6. COST — ACTUAL VERSUS PREDICTED (rule 12)

| | AOAI | AOAC | item |
|---|---:|---:|---:|
| registered estimate | 3.2 core-min | 3.4 core-min | 6.6 |
| **actual** | **3.1000** | **3.5333** | **6.6333** |
| **ratio actual/predicted** | **0.969** | **1.039** | **1.005** |
| band [2.0, 12.0] | inside | inside | — |
| per-arm cap 20.0 | 15.5 % used | 17.7 % used | — |
| item ceiling 40.0 | — | — | **16.6 % used** |

**No overrun. No arm approached its cap.** Core-minutes are **MEASURED** from the
arm's own wall clock. Dollars **DERIVED** at the owner-reported $0.0513/core-h:
**$0.00567** for the item — **NOT MEASURED**, the box cannot read its own billing.
**GPU: 0 GPU-h.**

### ⚠ THE ITEM RATIO OF 1.005 IS TWO OFFSETTING ERRORS, NOT A GOOD PREDICTION

Attribution, because a ratio near 1.0 that hides two ~20 % errors is worse than
an honest miss:

| | AOAI | AOAC |
|---|---:|---:|
| iterations predicted | 13,090 | 13,300 |
| **iterations actual** | **15,855** | **16,452** |
| ratio | **1.211** | **1.237** |
| per-iteration rate, anchor | 0.011024 s | 0.011500 s |
| **per-iteration rate, actual** | **0.009642 s** | **0.011370 s** |
| ratio | **0.875** | **0.989** |

- **I under-predicted iterations by 21–24 % in both arms**, because I priced
  continued points at 350 iterations from D19M's FD-sweep mean, and a 1° α step
  costs more than that — the converged points ran 314–516. That is the
  extrapolation §7.2 explicitly labelled as not a measurement of a 1° step, and
  it was optimistic.
- **The compressible per-iteration anchor was accurate to 1.1 %** — 0.011370
  actual against 0.011500 registered. It came from 30,622 iterations of D19M
  FE-S, a large sample, and it held.
- **The incompressible per-iteration anchor was 12.5 % conservative** — 0.009642
  actual against 0.011024. It came from **three** SO3aF primals, and a three-point
  anchor is what a 12 % miss looks like.
- **The two errors ran in opposite directions and nearly cancelled.** The item
  ratio of 1.005 is therefore **not** evidence that the estimate was good.

**Waste: none identified.** No stall, no row over 3600 s, no re-run of a
completed solve. The two arms ran concurrently on separate cores, so wall-clock
elapsed for both was ~4 minutes.

**Recommended anchor updates for successors** (not applied here — this item does
not own those files): incompressible per-iteration **0.009642 s** [MEASURED,
15,855 iterations, this item]; compressible **0.011370 s** [MEASURED, 16,452
iterations, this item]. Both are now large-sample and supersede the three-primal
incompressible figure.

---

## 7. COMPLETION STATUS — HONEST

**Both arms report `AOA_ARM_INCOMPLETE` (`rc=97`, `cold_executed=1/3`).**

This is **correct behaviour, not a defect**, and it is not being talked away: the
arm refuses to emit a completion token when fewer points executed than were
declared, and two cold controls did not execute — **because their primals failed,
which is itself the finding of §4(3).** The distinction the record must keep:

- **The physics is complete.** All 19 declared sweep points and all 3 declared
  cold controls **ran**, produced logs, and were read. Nothing is missing.
- **The success token is withheld**, because "executed" counts `rc=0` and a
  failed primal is not `rc=0`.

Per Sanaa's universal rule of 2026-08-26, **bookkeeping never voids physics**. The
counts are reported as they are; the readings stand on the artefacts.

---

## 8. ARTEFACTS

| what | where |
|---|---|
| AOAI run root | `/home/ubuntu/certonomous-runs/CURRICULUM-AOAI-a1-naca0012-alpha-polar-incompressible` |
| AOAC run root | `/home/ubuntu/certonomous-runs/CURRICULUM-AOAC-a1-naca0012-alpha-polar-compressible` |
| per-point ledgers | `<root>/out/LEDGER.tsv` |
| sweep logs | `<root>/out/sweep.log`, `<root>/out/cold_alpha_*.log` |
| machine readings | `<root>/AOA_POINTS.json` |
| AOAI reading (repaired) | `<root>/AOA_AOAI_read_REPAIRED_20260901T163038Z.txt` |
| AOAI reading (**pre-repair, REFUSED** — retained per §2d.1) | `<root>/AOA_AOAI_read_20260901T162427Z.txt` |
| AOAC reading | `<root>/AOA_AOAC_read_20260901T162741Z.txt` |
| status | `<root>/STATUS.AOAI`, `<root>/STATUS.AOAC` |

---

## 9. WHAT IS STILL OPEN

1. **Why the primal fails at α = 9°** is not diagnosed here, and this item does
   not diagnose it. It is a failure of the steady solver at that operating point
   on this mesh; whether it is the mesh, the wall functions, the SA model or the
   steady formulation is **unmeasured**.
2. **No band exists on any number above.** The wing convergence ladder is the
   prerequisite (§1 of both pre-registrations).
3. **The 9° boundary is a property of this 4,032-cell wall-function mesh** and
   must not be carried to another grid without re-measurement.
4. **α = 9…18 carry no CL or CD at all** — the primal produced none. They are
   blank in the polar, not zero, and not interpolated.
