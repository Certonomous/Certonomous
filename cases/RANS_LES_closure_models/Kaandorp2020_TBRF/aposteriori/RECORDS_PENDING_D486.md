# RECORDS DRAFTED AND NOT LANDED — Kaandorp a-posteriori close-out

**NOT LANDED. These two records are drafts.** They were composed at the
2026-08-24 close-out of this lane and `scripts/append_record.py` **REFUSED** to
land either. The refusal was not worked around, and `docs/DOCKET.md` and
`docs/LESSONS.md` were **not edited by hand**. They are filed here, under the
case directory they belong to, because the scratchpad is not a handoff channel
(`CLAUDE.md` rule 13, L-186).

Stamped 2026-08-24T16:09:33Z (`date -u`, same shell invocation as this write).
Composed against `HEAD` = `353925c7fc0a1f2eef77d8a60905c9e7b6182855`.

## The refusal, verbatim in substance

`scripts/append_record.py --path <record> --rows <row> --rev HEAD
--expect-first-id <id> --dry-run` refused all three of this close-out's records
with the same message shape:

> REFUSED: the worktree disagrees with the committed blob inside the committed
> blob's own bytes, first at byte N of M; the worktree is **SHORTER** than the
> blob, which is a **truncation, not an append**.

| record | HEAD blob | worktree | first divergence | id assert |
|---|---|---|---|---|
| `docs/COST_CALIBRATION.md` | 32,293 B | 23,712 B | byte 2,338 | **ok** — C-18 == max+1 |
| `docs/DOCKET.md` | 1,816,334 B | 1,803,389 B | byte 1,779,290 | **ok** — D491 == max+1 |
| `docs/LESSONS.md` | 658,105 B | 652,390 B | byte 652,390 | **ok** — L-269 == max+1 |

**In every case the id arithmetic PASSED and only the worktree-prefix test
failed.** This is D486 exactly — shared-index staleness is decay by construction,
not a rogue writer — and `scripts/check_docket_reconciliation.py` independently
reports the same thing for the docket (rows in HEAD and not in the worktree; the
rows are SAFE, they are in commits).

## What was landed anyway, and why only that one

**`docs/COST_CALIBRATION.md` row C-18 WAS landed**, by the route that file's own
committed header prescribes for exactly this condition — its
*"Divergence-by-design"* paragraph: *"Rows are built FROM `git show
HEAD:docs/COST_CALIBRATION.md`, re-derived at commit time in the commit's own
shell invocation, landed under rule 10's private-index protocol, and every
landing is asserted insertions-only post-commit."* That is a ruled procedure in
the record itself, and `CLAUDE.md` rule 12 makes the calibration row obligatory
at every process completion. Same fallback, same cause, as `df36bd3f` and
`b163c4a0`.

**`docs/DOCKET.md` and `docs/LESSONS.md` carry no such ruling, and their rows
here are discretionary rather than obligatory, so neither was landed by any
route.** They are below, ready to land unchanged once the worktree is
reconciled — **re-derive the ids at that commit** (`CLAUDE.md` rule 11: peers
commit constantly; D491 and L-269 were max+1 at 2026-08-24T16:09:33Z and will not stay so).

---

## DRAFT — docket row, id D491 at time of drafting

```
| D491 | **A FROZEN GATE THRESHOLD SET 4,003x BELOW ITS OWN INSTRUMENT'S RESOLUTION — Kaandorp a-posteriori G0a, and the third such defect in ONE pre-registration.** G0a (`Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md` §5, frozen `0ebc9d53`) requires rel-L2 of `U` between stock `kOmegaSST` and `kOmegaSSTCorrected(0,0)` **below 1e-10**. Measured **0.000000e+00** — the two `600/U` files are byte-identical (`md5 ff95ccb5c5b3f146ac4c364c006352b5`), so the gate reads PASS as frozen. **But the pair writes `writeFormat ascii` at `writePrecision 6`**, and the smallest non-zero this instrument can report, measured from the artifact itself, is **4.002936e-07** (one ulp of the 6-digit representation in the largest component, 108.209) with a half-ulp quantisation floor of **1.822069e-06**. The registered 1e-10 therefore sits **4,003x** below the single-ulp floor and **18,221x** below the quantisation floor: two solvers agreeing only to ~1e-8 relative would round to the same six digits, produce byte-identical files, and pass at "0.0". **What G0a establishes is agreement to < 4.0e-07, not < 1e-10.** The reader is not blind — a planted 1.234e-03 perturbation was written into a scratch copy of one component and the same rel-L2 expression (`run_lane.py:276`) returned 4.002936e-07, so the zero IS evidence — the defect is in the threshold, not in the reader. **This is the third registered clause in this one pre-registration that its own instrument cannot serve**: §5 H5's 1e-3 continuity threshold sits below the ~5e-3 estimator floor on the CBFS mesh, which the shipped SST baseline and the LES truth both exceed (RESULTS.md §5); §6's "sustained 100 iterations" is mutually unsatisfiable with a solver that stops at first satisfaction of its own `residualControl` (RESULTS.md §6); and now G0a. **Nothing was changed** — gates close after first compute (`CLAUDE.md` rule 2) and retiring or reinterpreting a threshold is not a lane's call. **A second, related conflict is referred with it:** §5 H5 registers the normalisation as `U_bulk / L` while RESULTS.md §1/§5 graded H5 on the field's own gradient scale, and §1's cell reads "NOT MEASURABLE", which is not in the fixed vocabulary of rule 1 / `VERIFICATION_CHARTER.md` §2. Both readings of one frozen clause now sit in one record. | Kaandorp a-posteriori close-out grading, 2026-08-24 (closure lane); measured in `/home/ubuntu/closure-data/aposteriori/kaandorp/AR_1_Ret_360__G0_{stock,corr}/600/U` and `system/controlDict`; recorded at `cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/RESULTS.md` §A.5, §A.7 of the 2026-08-24 addendum | **Verification's ruling on both limbs, with the closure supervisor.** (a) Whether a gate whose threshold lies below its instrument's resolution is PASS-as-frozen with the limitation disclosed (what this lane recorded) or must be labelled otherwise — and whether `check_comparator_freeze.py` should refuse a pre-registration whose threshold is below the `writePrecision` of the field it will read. (b) Which normalisation and which verdict word govern H5. **A lane may not choose the softer of two readings of a frozen clause, and did not** (L-269). |
```

---

## DRAFT — lesson, id L-269 at time of drafting

```
## L-269. A threshold is only as real as the instrument that will read it — dimension every registered number against its reader's resolution BEFORE the freeze, or the gate grades the instrument

One pre-registration, three registered clauses, and **not one of them could be
served by the instrument that had to read it.** All three were found *after* the
compute, two of them at close-out, and none could be repaired because gates close
at first compute (`CLAUDE.md` rule 2).

`Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md`, frozen `0ebc9d53`:

1. **G0a: threshold 1e-10, instrument resolution 4.00e-07.** The solver-identity
   gate compares two `U` fields written `ascii` at `writePrecision 6`. One ulp of
   that representation in the largest component is a rel-L2 of **4.002936e-07**;
   the half-ulp quantisation floor is **1.822069e-06**. The registered 1e-10 is
   **4,003x** below the first. The gate read `0.0` and passed — correctly, the
   files are byte-identical — but two solvers agreeing only to 1e-8 would have
   passed identically. **The gate proves agreement to < 4e-07 and no more.**
2. **H5: threshold 1e-3, estimator floor ~5e-3.** The continuity gate is read by a
   curvilinear chain-rule gradient which, on the curved CBFS mesh, floors at
   ~5e-3 — a level the shipped converged SST baseline **and the LES truth itself**
   both exceed. The threshold could not be met by any field on that mesh.
3. **§6 convergence: "sustained for 100 iterations", against a solver that stops
   at first satisfaction.** `residualControl` terminates the run the first
   iteration its test passes, so a criterion phrased as a 100-iteration run is
   unsatisfiable by construction on exactly the rows that converge. Its
   stagnation fallback is phrased over "the last 500 iterations" and
   `writeInterval` wrote checkpoints every 5,000, so that limb could not be
   measured at its registered window either.

**The common failure is not carelessness about the physics. Every one of these
thresholds is defensible as a statement about the world;** each is indefensible as
a statement about a *measurement*, because nobody asked what the reader could
resolve. A pre-registration's evidentiary content is that the gate could not have
been chosen to fit the answer — but a gate the instrument cannot evaluate has a
foreordained answer too, and it is not the one the registration was reaching for.

**The rule.** Before the freeze, for every registered number, write down the
instrument that will read it and its resolution, and assert the threshold sits
**above** that floor with margin. The check is cheap and it is arithmetic:
`writePrecision` for a field comparison; the estimator's calibration on a field of
known answer for a derived quantity; the checkpoint interval for anything phrased
over a window; the solver's own termination logic for anything phrased as a run of
iterations. A pre-registration that names a threshold should name, in the same
sentence, what would be measurable if the claim were false.

**The tell at grading time is a zero, or a floor that the truth also fails.** A
comparator returning exactly `0.0` and a control row failing the same gate as the
treatment are both the same signal: the number is about the instrument. Rule 3's
planted control answers *"can the reader see anything?"* — it does **not** answer
*"can the reader see the thing the threshold names?"* Here the plant passed (the
reader reported 4.002936e-07 for a planted perturbation) while the threshold
remained 4,003x out of reach. **Plant the zero, and then also dimension the
threshold; they are two different checks and the first does not imply the second.**

**And when the defect is found after the compute, it is disclosed and referred,
never repaired.** Nothing in that pre-registration was changed; the three defects
are recorded in `RESULTS.md` §5, §6 and §A.5 and referred to verification as
D491. A lane facing two readings of one frozen clause may not take the softer one.
```
