# T1b L4 extension: pre-registration (template form)

Registered 2026-08-25, before any extension solver was launched. This is a
**standard continuation under an already-registered protocol**, not a novel or
contested case, so it takes the 10-line template form Sanaa registered on
2026-08-25 ("standard verification/validation cases use the 10-line prereg
form"), plus the cost registration that rule 12 makes non-optional.

**It creates no gate, no threshold, no band and no label.** Every one of those
is already frozen in `docs/campaigns/T-family/T1b_L4_AMENDMENT.md` (sections 2,
3 and 4) and in `T1b_band.json`. Nothing here may alter them, and nothing here
is read by the comparator.

---

1. **Case.** `R_10k_x`, `R_100k_x`, `R_300k_x` at
   `verification/runs/T-family/T1_runs/` — the three fourth-level (x, 209 920
   cell) T1b cases that failed iterative convergence at their registered
   `endTime` in today's grading (relative change between the last two
   checkpoints: 4.832e-02, 1.954e-05, 1.269e-04 against a 1e-6 tolerance).
   `R_30k_x` converged exactly and is **NOT extended**.

2. **Reference.** `T1b_L4_AMENDMENT.md` section 4, the extension protocol
   registered 2026-08-21 before any x case solved, and anticipated for these
   three cases specifically in section 3.6 (lines 222-223). Raised `endTime` =
   the smallest multiple of 2000 at or above 1.6x the fine level's converged
   count, which section 4 enumerates: **32000 / 94000 / 110000**. This
   pre-registration adopts those three numbers unchanged; it does not choose
   them.

3. **Quantities.** None graded here. The extension produces only the two
   further checkpoints (30000/32000, 92000/94000, 108000/110000) that
   `iterative_convergence()` and `analyse_t1b_L4.py` will read later.

4. **Bands.** Unchanged and untouched: `T1b_band.json`, and the amended gating
   rule of section 2. No band is set, widened or reinterpreted by this document.

5. **Ladder.** T-family, tier 1, rung T1b, fourth grid level (x). Position in
   the ladder is unchanged; this is a continuation of the same rung.

6. **Decomposition seed.** **Serial, 1 rank, no decomposition** —
   `nProcs = 1`, no `decomposeParDict` is used, no `decomposePar` is run, and
   the solver is invoked directly rather than through `mpirun`. There is no
   seed to record because there is no partitioner. *This field is recorded
   because the form requires it, not because the value is in doubt.*

7. **Criteria.** No verdict is assigned by this document and none may be
   assigned by the lane that runs it. On completion the sequence is the one
   section 7 of the amendment already fixes: `mark_done_t1b_L4.py` (which
   applies its `check_ext` branch once `log.solve.ext1` exists) ->
   `analyse_t1b_L4.py` -> `gate_t1b_L4.json`. A case that does not meet the
   strict completion rule across BOTH segments gets no marker and is
   `NOT A RESULT`. The comparator is hashed against its committed blob before
   analysis (Charter 2d).

8. **Restart mechanism, and what is preserved.** `startFrom latestTime` (already
   set), `endTime` raised in `system/controlDict`, solver appending to
   `log.solve.ext1`, `checkMesh` to `log.checkMesh.ext1`, `STATUS_ext1.<case>`
   beside `STATUS.<case>` — exactly the `run_one_ext1.sh` form section 4
   registers, with the `STATUS_ext1` name that the frozen
   `mark_done_t1b_L4.py` reads (`STATUS_EXT = "STATUS_ext1"`). `log.solve`,
   `log.checkMesh`, `STATUS.<case>` and `0/T` are never written. Because
   `purgeWrite 2` will unlink the graded checkpoints as new ones appear, the
   two graded time directories of each extended case are **hardlink-preserved**
   under `verification/runs/T-family/T1_runs/PRESERVED_L4_graded/<case>/`
   before launch, so today's graded numbers keep their artifact on disk.

9. **Cost, derived from THIS rung's own measured rates.** The frozen section 5
   estimate is NOT used: it borrowed a throughput across a 2.56x mesh jump and
   missed by 31.4 %. Basis here is each case's **own `ClockTime` over its own
   last 10 000 iterations** on this same 209 920-cell mesh (throughput rises as
   a steady SIMPLE case converges, so the late segment is the right basis for
   the segment being added). Ceiling basis is the **slowest sustained segment
   measured anywhere on this mesh** — 5.4338 s/iteration, `R_10k_x` last 5 000
   iterations under full 19-case contention — applied to every case, so the
   ceiling bounds contention rather than guessing at it.

   | case | added its | POINT s/it | POINT wall s | POINT core-min | CEIL s/it | CEIL wall s | CEIL core-min |
   | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
   | `R_10k_x` | 12 000 | 5.3681 | 64 417 | 1 073.6 | 5.4338 | 65 206 | 1 086.8 |
   | `R_100k_x` | 14 000 | 2.8756 | 40 258 | 671.0 | 5.4338 | 76 073 | 1 267.9 |
   | `R_300k_x` | 30 000 | 2.2425 | 67 275 | 1 121.2 | 5.4338 | 163 014 | 2 716.9 |
   | **total** | 56 000 | | **171 950** | **2 865.8** | | **304 293** | **5 071.5** |

   **POINT 2 865.8 core-minutes = 47.76 core-hours = $2.45.
   CEILING 5 071.5 core-minutes = 84.53 core-hours = $4.34.**
   Priced at $0.0513 per core-hour, c7a.4xlarge, **reported-by-owner
   (2026-08-21/22), not measured** — the box cannot read its own billing
   (`COMPUTE_BUDGET_CHARTER.md` §5). **Every dollar figure above and below is
   DERIVED, NOT MEASURED.** Under Sanaa's standing under-$25 pre-authorisation.

10. **Cap, and its enforcement.** The registered cap is the ceiling rounded up:

    | case | cap (core-min) | ranks | enforced timeout (s) = cap x 60 / ranks | derived $ |
    | --- | ---: | ---: | ---: | ---: |
    | `R_10k_x` | 1 100 | 1 | 66 000 | 0.94 |
    | `R_100k_x` | 1 300 | 1 | 78 000 | 1.11 |
    | `R_300k_x` | 2 750 | 1 | 165 000 | 2.35 |
    | **total** | **5 150** | | | **4.40** |

    The identity is written as `timeout = cap_core_min * 60 / ranks` and is
    coded that way in the runner, so a later parallel case cannot inherit a
    silent factor-of-ranks overrun; with `ranks = 1` the two coincide here.
    Enforcement is GNU `timeout`: at the cap the solver is killed, `rc` is 124,
    `STATUS_ext1` records it, and `mark_done_t1b_L4.py` refuses the case. **An
    overrun stops the run; it does not get a new budget.** A capped case is
    reported as `NOT A RESULT`, not re-launched with a larger cap.

**Estimate-versus-actual calibration (rule 12) is owed at completion** and is
the supervisor's row in `docs/COST_CALIBRATION.md`: actual core-minutes from
`STATUS_ext1.<case>` wall seconds against the POINT above, with the gap
attributed.
