# cfd — GRADING CHAIN

**Authority.** Sanaa's GRADING TRANSPARENCY ORDER, 2026-08-31, captured verbatim by the
chief at `4116024a` (`etc/sessions/2026-08-31T2055Z_sanaa_grading_transparency_order.md`),
read at that sha by `cfd-supervisor` before writing this. Her rule, verbatim: *"If any
link in your chain can't be named in one bullet, that's a finding, not a formatting
problem."* **Three of the eight bullets below are findings.** They are stated as findings,
not smoothed into prose.

Chain shape, used identically in every bullet:
**artifact → reader → frozen gate → planted-control citation (who proved the reader can
see) → where the verdict lands.**

---

1. **THE MATURE CHAIN — F17 / F17b / F17c / F18 / F23b. All five links nameable.**
   Solver-written field files under `verification/runs/<case>/<t>/` **→** `foam_io_*.py`
   readers with `grade_*.py` comparators and `exact_*.py` analytic referents **→** the
   frozen `*_PREREGISTRATION.md` in `verification/campaign/` **→** planted control
   `plant_into_vector_file(src, dst, comp, delta)` (`cases/F17c_kovasznay_floor/foam_io_f17c.py:107`),
   which **writes the perturbation into a FILE and reads it back**, with the comparator
   refusing (exit 2) if the reader cannot see it **→** `verification/campaign/<CASE>_RESULTS.md`
   (e.g. `F17c_KV40_FLOOR_RESULTS.md`). **This is the pattern the rest of the territory is
   measured against**, and it is the one Sanaa's control-birth directive describes.

2. **F28 §6.2 / §6.3 CONTROLS — ⚠ FINDING. The planted-control link CANNOT BE NAMED for
   any graded number.** `postProcessing/diskPlaneUp|Down/…/surfaceFieldValue.dat` and
   `postProcessing/forcesDuct/0/force.dat` **→** `analyse_f28.py:511 function_object_series`
   **→** frozen §6.2 C1–C4 and §6.3 **→** *(no control exists on this reader)* **→**
   `verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md`. The plant that
   does exist, `plant_into_p():411`, certifies `read_volScalarField` — whose **value
   reaches zero graded numbers**, its entire contribution being one array length. Two
   independent check-1 reads concur: `ea6f9992` (cfd) and `3fb0d0a3` (verification).
   **Cause class: INSTRUMENT. Under repair; Stage 1 gated until a re-read.**

3. **F28 STATIONARITY — ⚠ FINDING. The control does not travel the production path.**
   `force.dat` column `total_x` **→** `read_ptp_f28.py:53` **→** frozen §8, as floored by
   **Addendum 3** (`0a62c5c6`) to `ptp <= max(0.001*|T_mean|, T_floor)`,
   `T_floor = 5.934119457e-04 N` **in 5° sector newtons** **→** the plant at
   `read_ptp_f28.py:101-106` doubles the last sample **in a Python list**, never on disk
   **→** `verification/campaign/`. A control that never leaves memory does not test the
   reader that reads the file, which is exactly what Sanaa's control-birth directive
   forbids. **Cause class: INSTRUMENT.** Weaker than bullet 2's defect — the reader is at
   least the one that grades — but it is not a disk-borne control and must not be cited
   as one.

4. **F28 — WHERE THE VERDICT LANDS, and today it lands nowhere.** All twelve run
   directories under `verification/runs/F28_runs/` carry `LABEL=FEASIBILITY` or
   `LABEL=DIAGNOSTIC`. **Zero graded rows exist**; no verdict of the fixed vocabulary has
   been issued. The case is `PENDING`. Addendum 3's floored criterion is **registered and
   NOT WIRED** — nothing in `analyse_f28.py` implements it.

5. **JF1 — ⚠⚠ THE WORST FINDING IN MY TERRITORY: TWO LINKS OF THE CHAIN DO NOT EXIST.**
   `postProcessing` forces/coefficients and `READOUT.txt` **→** *(NO READER — the only
   Python in `cases/JF1_JET_FLAP/` is `build_jf1.py`, a mesh generator; there is no
   comparator)* **→** frozen `JF1_PREREGISTRATION.md` gates **→** *(NO PLANTED CONTROL —
   none exists anywhere in the case)* **→** *(no results record)*. **JF1 has no comparator,
   so STAGE G CANNOT BE GRADED WHEN IT ARRIVES.** Cause class: **INSTRUMENT**, and it is
   prior to every other JF1 question — a gate cannot fail or pass through a comparator that
   was never written.

   **⚠ CORRECTION, 2026-08-31, to my own first version of this bullet — made within the hour,
   by the lane I asked to check it, and verified at the line by me before accepting.** I
   first wrote *"five L1 rows have been run and there is nothing in this lab that can grade
   them"*, which reads as retrospective waste. **That is wrong and I withdraw it.** Those
   rows are registered **feasibility** and score nothing by design: every `RUN_STATUS`
   carries `label feasibility` and `gate NONE -- this run scores nothing`, and frozen §6 at
   `:1233` answers stage F's "Gated?" with *"**No.** Nothing here is a result."* **They are
   ungraded BY REGISTRATION, not by instrument failure**, and a missing comparator is not
   why. The forward-looking sentence above is the true one, and it is still serious.
   **Two things that make the position better than my first version implied, both verified:**
   (a) the comparator's **specification is frozen and unusually complete** — §8.1's six
   completion clauses with the `controlDict`/`fvSolution` pin, §8.2's three named plants
   **plus ten mutation limbs M1–M10 tabulated at `:1714-1725` with the required outcome for
   each**, §8.3's verdict emission, and §8.4's registered refusal list at `:1744-1758`. The
   hard, rule-2-critical part — deciding **pre-compute** what the instrument must refuse —
   **is done and frozen.** What is absent is **transcription of a frozen spec, not design.**
   (b) §8.1's clauses and §8.4's refusal list contain **no `checkMesh` clause**, so bullet
   6's §4.5 `Mesh OK` contradiction does **not** block writing the comparator. It stays open
   on Sanaa's desk; it is not a blocker on the instrument track.

6. **JF1 GATES — two defects in the frozen document itself, both mine to escalate and
   neither mine to fix.** (a) §4.5's hard-gate table at `:763` requires `checkMesh` to
   print `Mesh OK`; no C-mesh level does, and **the sole failing check is the aspect-ratio
   one the same table declares admissible two rows above at `:762`** — the table
   contradicts itself. (b) Frozen gate line 6 registers a comparand its own BC and
   geometry cannot produce, short by exactly `cos(30°)`. Both are post-first-compute, so
   rule 2 closes them to every agent. **Cause class: GATE-DESIGN (both). On Sanaa's desk.**

7. **CAUSE-CLASS BACKFILL — cfd's non-PASS rows, from existing records, no re-runs.**
   Assigned by the grading record and cited, per her rule.

   | Item | Record | Class |
   |---|---|---|
   | F28 no-floor stationarity criterion (degenerate on its own control) | Addendum 3 §2, `0a62c5c6` | **GATE-DESIGN** *(Sanaa's own anchor — verified against the record before transcribing)* |
   | F28 comparator: 6 defects across two check-1 reads | `ea6f9992`, `3fb0d0a3` | **INSTRUMENT** |
   | F28 stationarity plant is in-memory | `read_ptp_f28.py:101` | **INSTRUMENT** |
   | F28 mesh-generator `n == 1` degradation | `55c4db56`, `db04e95a` | **INSTRUMENT** |
   | JF1 has no comparator and no planted control | this document, bullet 5 | **INSTRUMENT** |
   | JF1 §4.5 `Mesh OK` self-contradiction | `JF1_PREREGISTRATION.md:762-763` | **GATE-DESIGN** |
   | JF1 frozen line 6 `cos(30°)` comparand | board, JF1 §6 | **GATE-DESIGN** |
   | JF1 budget shortfall (257.6 core-min over slack) | board 20:41Z | **BUDGET/KILL — DISSOLVED** by Sanaa at `1dcdb677` |
   | JF1 five L1 rows stopped at iteration limit 8000, not converged | board; `READOUT.txt` per row | **BUDGET/KILL — DISSOLVED**; now runnable to §5.5's 20,000 |

8. **THE HEADLINE SPLIT, AND IT IS THE POINT OF HER ORDER: cfd is 0 physics-adverse /
   9 non-physics (5 INSTRUMENT, 3 GATE-DESIGN, 2 BUDGET/KILL both dissolved — 10 rows, one
   item double-counted across the two dissolved).** **Not one cfd row currently says
   anything about whether this lab can do physics.** Every blocked thing in my territory
   is referee trouble: instruments that cannot see, gates that contradict themselves, and a
   budget she has since removed. Under her standing definition — *"Can the lab run and
   post-process X?"* is answered by SURVEYED-or-better with classes **excluding**
   INSTRUMENT/BOOKKEEPING/NAMING — **F28 and JF1 do not currently qualify**, and the honest
   reason is my instruments, not the physics.

*Written by `cfd-supervisor` personally. Every line number and citation was opened and
checked at the time of writing rather than recalled; the two Sanaa anchors she supplied
(F28's no-floor criterion → GATE-DESIGN, JF1's budget item → BUDGET/KILL) were verified
against their records before transcription, per her instruction that her examples are
anchors to check. Bullets 2, 3 and 5 are findings under her rule and are counted as such.*
