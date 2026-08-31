# heat-transfer — THE GRADING CHAIN

**Sanaa's GRADING TRANSPARENCY ORDER, 2026-08-31**, verbatim at
`etc/sessions/2026-08-31T2055Z_sanaa_grading_transparency_order.md` (`4116024a`), item 1.
Her rule governs this file: *"If any link in your chain can't be named in one bullet, that's a
finding, not a formatting problem."* **Section B is that finding list. It is not an appendix —
it is the honest half of this document.**

Territory: the T-family ladder and the F14 / K-rung DC-cooling spine.

---

## A. THE CHAIN — artifact → reader → frozen gate → planted control → verdict

1. **ARTIFACT GRADED.** `verification/runs/T-family/<RUNG>_runs/<CASE>/`: the case's own time
   directory at `endTime`, and its own `log.solve`. **Never `STATUS.<case>` for any physics
   quantity** — the queue runner clobbers it to a single `launcher_rc` key, so `rc`, `wall_s`,
   `core_min` and `capped` are destroyed. Cost is read from `log.solve`'s `ExecutionTime` at 1
   rank. Bookkeeping loss never voids physics (Sanaa's universal rule, 2026-08-26).

2. **COMPLETION READER.** `mark_done_<rung>.py`, frozen. Enforces `CLAUDE.md` rule 4's six
   conjuncts — `rc`, exactly one `End`, last time == `endTime`, registered fields present per
   region, `ExecutionTime` count == `endTime`/`deltaT`, and **the age guard**: every field at
   `endTime` newer than that case's OWN `0/T` (T24 uses `0/housing/T`), because `0/T` is touched
   last at launch and so dates the run allowed to produce the answer. **Refuses (exit 2) rather
   than degrades.** T24's is frozen at `3b053709`.

3. **VALUE READER.** `analyse_<rung>.py`, frozen **before it reads any case output**. T24's is
   frozen at `d9082bfb` (1,524 lines) and was authored **blind** — no `log.solve`, no time
   directory, no field, developed against forged trees only, with the `START` format learned
   from launcher source. Six of twelve cases had already landed when it was written; the freeze
   is what separates that from a gate fitted to its answer.

4. **FROZEN GATE.** `docs/campaigns/T-family/<RUNG>_PREREGISTRATION.md`, frozen by sha **before
   compute** (`CLAUDE.md` rule 2). T24: sha256 `2f3f7310bceac91f…`, 1,073 lines, frozen
   `b9057489` at 19:55:46Z against a 20:16:59Z launch — and `git diff b9057489 HEAD` on that path
   is empty, so not one line has moved since. The comparator names its own authority in-file
   (`FREEZE_SHA`, `FROZEN_DOC`) so a reader can check the binding without trusting this bullet.

5. **PLANTED CONTROL — who proved the reader can see.** `CLAUDE.md` rule 3. `PLANT = 1.234e-03`
   is **imported** from `scripts/roache_triple.py:169`, never redefined locally. The control
   plants a known perturbation, reads it back **from disk**, walks a magnitude ladder, and
   **REFUSES if no magnitude produces a non-zero read** — a blind reader is not entitled to
   certify a bound. Sizing uses the **relative** predicate `got >= PLANT*(1-1e-9)`;
   `analyse_t3.py:327`'s absolute form is expressly rejected. Precedents:
   `T3_runs/analyse_t3.py` (`plant_into_T()`, refusal ~:801), `T10a_runs/analyse_t10a.py:846`,
   `T24_runs/analyse_t24.py:506-526`. **A zero from a reader not shown able to see a non-zero is
   not evidence.**

6. **GATE APPLICATION, ONE-WAY.** A gate may only turn a `PASS` into `NOT A RESULT`, never the
   reverse. On gated rungs, Roache triple gating (rule 5): a non-`CONVERGING` triple is
   `NOT A RESULT` whatever the value; GCI at Fs = 1.25, never quoted on non-monotone triples.
   On **map** rungs (T23, T24) there is **no triple** — a single mesh level admits none — so no
   Roache class, GCI or observed order is computed or quotable; T24 §0.3 calls doing so a
   category error. Rule 5 is not weakened there; its object is absent.

7. **VERDICT LOCATION.** `verification/runs/T-family/<RUNG>_runs/gate_<rung>.json` — the machine
   record, carrying value, referent, triple, order, GCI where legal, and the verdict from the
   fixed vocabulary (`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` /
   `PENDING`). **Every non-`PASS` verdict now carries a CAUSE CLASS** from Sanaa's eight, assigned
   by the grading record and cited (§C).

8. **COST AND NARRATIVE.** Rule 12's estimate-versus-actual row lands in `docs/COST_CALIBRATION.md`
   at every process completion; the prose verdict lands in the commit message and in this team's
   `docs/LAB_STATE.md` block, which is the only handoff channel between sessions.

---

## B. WHERE MY CHAIN HAS AN UN-NAMEABLE LINK — the findings, per her rule

- **T21 — links 2 and 3 DO NOT EXIST.** `T21_PREREGISTRATION.md` (untracked, 1,245 lines,
  mtime 16:00Z) registers gate, threshold (±0.8600 mK about 0.0859974153 K), cap (20.0 core-min)
  and label, but **no comparator, builder or launcher exists**; §3/§5/§6 are a specification, not
  code. It is therefore **unfreezable**: `VERIFICATION_CHARTER` §2m.3 requires a freeze to be
  complete *including the grading path*, while its own four-hour clock (expired 20:00:48Z) orders
  me to freeze on the spot. **Referred to verification as a charter-internal conflict.** Nothing
  is at risk — T21 authorises nothing and `T21_runs/` does not exist.

- **T24 §3.7 — one registered limb has NO CODED READER, and its link is a human.** §3.7 registers
  both a mesh-identity hash *and* that every region of every case show `Mesh OK` with zero
  negative-volume cells "read as the DIRECT quantity… not as the absence of a warning." The
  comparator implements the hash only — no `checkMesh`, non-orthogonality, skewness or
  negative-volume handling in 1,524 lines. **I discharged it personally** (36/36 logs `Mesh OK`;
  min cell volumes 1.313e-09 / 6.739e-11 / 5.861e-10, strictly positive). **A supervisor's read is
  a weaker link than a coded reader with a planted control** — it has no refusal, no mutation
  test and no negative arm. Named here rather than left to look automatic.

- **T16c — link 7 is EMPTY, deliberately.** Comparator tracked at `46d090f6`; **no `gate_t16*.json`
  exists anywhere**. The blindness is intact and must stay intact: no T16 value may be computed
  before the comparator is frozen and read. Three mutation limbs (L19/L20/L34) remain untested —
  the harness's *measured* reach, not its selftest's claim.

- **T18 — link 3 is CONTAMINATED and the rung is quarantined.** `analyse_t18.py:509`'s
  `grade(HERE, …)` selftest limb produced a file **byte-identical to the real `gate_t18.json`**,
  so the selftest can overwrite the verdict it is meant to check. **`--selftest` must not be run**
  until an S8-carrying successor exists. The successor is owed.

- **T22 — links 4 and 7 ABSENT BY DESIGN.** Feasibility: no gate, no verdict, and **a feasibility
  output is never gradeable**. Recorded as an answered question with its cost, and nothing more.
  This is a declared absence, not a broken link.

---

## C. CAUSE CLASSES — the eight, and how this team assigns them

Sanaa's eight, no free text, **assigned by the grading record and cited like any claim**:
`PHYSICS-FAIL` · `MODEL-LIMIT` · `REFERENT-CEILING` · `GATE-DESIGN` · `INSTRUMENT` ·
`BOOKKEEPING` · `NAMING/PLUMBING` · `BUDGET/KILL`.

**Only the first two say anything about the lab's ability to do physics.** Every heat-transfer
report headline now carries the split **"N physics-adverse (list) / M non-physics (by class)"**,
and her standing definition governs the capability question: *"Can the lab run and post-process
X?"* is answered by **SURVEYED-or-better with cause classes excluding INSTRUMENT / BOOKKEEPING /
NAMING**. Everything else is referee trouble, and **referee trouble never again wears a physics
costume in any report.** A `PASS` carries no cause class. A rung with **no verdict** (T21, T22,
T16c) carries **no cause class either** — absence of a verdict is not a non-PASS verdict, and
backfilling one would be inventing a judgment the record does not contain.

---

*Bullets in §A: 8 (≤10, per the order). §B is the findings limb her rule requires, §C the
cause-class limb of item 2. Backfilled rows live in this team's `LAB_STATE` block and in the
grading records themselves, cited there.*
