# SO-3D STAGE 1 — RESULT: **NOT A RESULT**

**Dated 2026-09-03.** Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`
(checks 1 and 4 discharged personally before the launch; first compute authorised
by him, `agent adf48149dd270d738`).

**Pre-registration:** `PREREGISTRATION.md`, frozen v1.0 2026-08-31, AMENDMENT 1
(v1.1) 2026-09-03. **Grading path:** `so3d_replay.py`, blob
`4ebd9b2f17a824b49470f32d685bbb05cba61f09`, md5
`60af48e4e3debb536141eb3f5c66409b` — **hashed against its committed blob in the
launching invocation, before the reader was invoked, and the two matched**
(`STATUS.SO3D`, `G1 OK`).

**SUBMISSIONS PARKED.** Nothing here is filed, sent, uploaded, registered, posted
or commented outside this box (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

---

## 1. THE VERDICT, AS THE READER EMITTED IT

> ## **NOT A RESULT**

**G-SO3D-P — the plant control — REFUSED**, exit 2, and by §6 ordering rule 1
**every other gate is `NOT A RESULT`, whatever number it would have computed.**
No gate below the plant control was scored: `G-SO3D-1`, `G-SO3D-2`, `G-SO3D-3` and
`G-SO3D-4` were never reached, and this document quotes no census count, no
per-scenario rate and no coupling fraction, because none was produced.

**This outcome is REGISTERED, not improvised.** §8's second null path, frozen
2026-08-31 before the reader existed:

> *"If the plant control fails (G-SO3D-P), the rung is `NOT A RESULT` in its
> entirety and **the reader itself is the finding**."*

The reader is the finding. The refusal, verbatim from
`SO3D_replay_2026-09-03T205808Z.out`:

> `NOT A RESULT: REFUSE (PLANT-B): moved one `Primal solution failed!` banner from
> line 200205 to just after line 100261. Expected exactly one scenario at −1,
> exactly one at +1, the rest at 0, and the total unchanged at 671. Measured moves
> {'cl04': 0, 'cl05': 0, 'cl06': 0}, total 671 → 671.`

| gate | verdict |
|---|---|
| **G-SO3D-P** | **REFUSE** → the rung is `NOT A RESULT` in its entirety |
| G-SO3D-1 | **NOT A RESULT** — not reached, not scored |
| G-SO3D-2 | **NOT A RESULT** — not reached, not scored |
| G-SO3D-3 | **NOT A RESULT** — not reached, not scored |
| G-SO3D-4 | **NOT A RESULT** — not reached, not scored |

**No mechanism finding is claimed.** H1–H7 stand exactly where §4 left them. **No
remedy is proposed** (§8, §10).

---

## 2. TRIAGE — WHAT ACTUALLY HAPPENED, AND IT IS THE LANE'S OWN DEFECT

**The total was right and the movement was zero.** `671 → 671` is correct: the
plant moves a banner, it does not create or destroy one. What refused is the
*distribution*: no scenario moved at all.

**MEASURED, in a triage invocation that computed no gate quantity** — it reports
the attribution of the two plant sites and nothing else:

| plant site | line | owning record | AoA | scenario |
|---|---|---|---|---|
| PLANT-B **delete** | 200205 | 200024 – 200292 | 0.9304417657 | **`cl04`** |
| PLANT-B **insert** | 100261 | 100085 – 100355 | 0.5780466691 | **`cl04`** |

**Both content-addressed anchors land in `cl04` records.** The registered plant
therefore removes one banner from `cl04` and adds one to `cl04`; the two cancel,
and the per-scenario vector is `{cl04: 0, cl05: 0, cl06: 0}`.

**THE DEFECT IS IN MY ACCEPTANCE PREDICATE, NOT IN THE FREEZE.** §7 registers the
expectation as a movement *"of exactly −1 in the scenario owning the deleted banner
and exactly +1 in the scenario owning the inserted one"*. **It nowhere requires
those two scenarios to be different.** My predicate demanded
`len(minus) == 1 and len(plus) == 1` — two *distinct* scenarios — which is a
condition the registered plant does not state and which this log cannot satisfy.

**AND IT WAS UNSATISFIABLE BY CONSTRUCTION.** The anchors are content-addressed and
deterministic — *first* banner at or after line 200000, *first* `End` at or after
line 100000 — so they select the same two records on every invocation, forever.
**There was no possible run of this reader in which PLANT-B could have passed.**
That is the eighth unsatisfiable-by-construction condition this family has met, and
the second one this lane authored. It cost **0.0392 core-min** to find, and the
control that found it is the one whose entire purpose is to be untrusted until it
fires.

**What is NOT wrong.** The plant's *substance* — that a moved banner must be seen
to move, by name, in the scenario that owns it — was never in doubt and is not
weakened by anything here. Nor is the freeze at fault: §7's text is satisfiable as
written.

---

## 3. WHAT PASSED, AND THE HONEST LIMIT ON SAYING SO

**PLANT-A passed. That statement is an INFERENCE FROM CONTROL FLOW, not an
artifact,** and the distinction is stated rather than glossed. `score_plant_control`
scores PLANT-A first and raises on failure, so execution reaching PLANT-B proves
PLANT-A's acceptance was true — the value channel census moved by exactly +1, at
the planted line, on the field `CD`. **But `so3d_plant_report.json` is written only
after all three plants pass, so no artifact records it.** A pass that exists only
as a deduction from source ordering is weaker than a pass on disk, and it is
reported at that strength.

**PLANT-C was never reached.** It is **NOT RUN**, and NOT RUN is not PASS.

---

## 4. TWO INSTRUMENT DEFECTS DISCLOSED FOR THE SUCCESSOR

1. **The refusal path writes no artifact into the run root.** `so3d_replay.json`
   carrying the refusal landed in this case directory; the run root
   `/home/ubuntu/certonomous-runs/CURRICULUM-SO3D-a2-wing-multipoint-rootcause`
   was created and left **empty**. A reader arriving at the run root finds nothing
   and cannot tell a refusal from a run that never started.
2. **The plant report is all-or-nothing.** Defect 1 above and the PLANT-A
   inference in §3 are the same defect seen twice: the instrument records only
   complete success, so a partial pass leaves no evidence.

Neither is repaired here. **`so3d_replay.py` is the frozen grading path and first
compute has occurred**, so its gates are closed (`CLAUDE.md` rule 2) and this lane
does not edit it.

---

## 5. THE SUCCESSOR, PROPOSED AND NOT TAKEN

**This family's precedent is SUCCESSOR, NOT AMENDMENT** — D6 → D6R → D6RF → D6RF2,
A1WR → A1WRT. A successor stages its **own** copy of the reader with a new pin; the
frozen `so3d_replay.py` stays intact as the instrument that produced this
`NOT A RESULT`.

**Proposed as `SO3D-R`, for the supervisor's ruling — NOT begun:**

- PLANT-B scored at the **record** level: the deleted banner's record moves −1, the
  inserted banner's record moves +1, both records' owning scenarios are named, and
  the total stays 671. **This is strictly MORE discriminating than the
  per-scenario predicate, not less** — per-scenario movement is a coarsening of
  per-record movement — so it cannot be a weakening dressed as a repair, and the
  per-scenario vector is reported beside it.
- The refusal path writes its artifact into the run root as well as the case
  directory, and the plant report is written incrementally so a partial pass leaves
  evidence.
- Everything else — the five gates, the four predictions, the three plants, the
  12 core-min cap and every threshold — carried across **unchanged**.

**The lane does not rule on whether that successor is lawful, does not write it,
and does not arm it.** That is `SUPERVISION_CHARTER.md` §3 check 4.

---

## 6. COST — RULE 12, MEASURED AGAINST THE REGISTERED ESTIMATE

| field | value |
|---|---|
| unit | core-minutes = wall s × ranks ÷ 60 |
| ranks | **1** (host post-processing; no container, no MPI job, no OpenFOAM process) |
| **wall** | **2.350 s** [MEASURED, captured **inside** the detached wrapper — `setsid` returns 0 for every outcome of what it wraps] |
| **actual** | **0.0392 core-min** [MEASURED] |
| registered point estimate | **6.0 core-min** (bracket 3–10) |
| **ratio actual/predicted** | **0.0065** |
| cap | **12.0 core-min registered — not approached** (0.33 % of it) |
| solver core-min | **0.000**, cap 0.000 — **honoured**: no container, no MPI job, no OpenFOAM process was started |
| dollars | actual **$0.000033**, predicted $0.00513 — **DERIVED at the owner-stated $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5) |
| waste | **0.0392 core-min, named in full and not absorbed** (`COMPUTE_BUDGET_CHARTER.md` §6): the invocation produced no gate reading, so all of it is waste attributable to the PLANT-B predicate defect of §2 |

**Gap attribution: MISPREDICTION, and of a specific kind.** The registration
predicted 6 core-min for *"four logs totalling ≈ 0.9 M lines, three full passes
each"*. It over-predicted by **~153×** because it costed the work as I/O-bound line
counting; the measured pass rate is **0.49 s per 222,223-line log** including
sha256. **Not contention** — the box was ~95 % busy and this run took 2.35 s of it.
**The 0.0065 ratio is real but is a floor, not a calibration of the full
pipeline**, because the run aborted at PLANT-B and never reached the four gates,
the controls or the JSON writes. **A successor that runs to completion will
produce the honest ratio; this row must not be read as one.**

---

## 7. WHAT THIS ITEM DOES NOT CLAIM

**It establishes nothing about the multipoint pathology.** No hypothesis in §4 was
tested. The `Invalid number in NLP function or derivative` mechanism is exactly as
uncharacterised as it was before this invocation, and the 4,258.466 core-min of D6
and D6R evidence remains unreplayed.

**No gradient, no FD table, no adjoint, no GCI** — this rung computes none and
quotes none. **Stage 2 and Stage 3 remain unfrozen** (§10). **No remedy is
proposed.**
