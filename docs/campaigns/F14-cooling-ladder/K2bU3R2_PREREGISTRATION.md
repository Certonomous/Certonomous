# K2b-U3-R2 — run the already-registered un-confounded Test D at the higher price. Pre-registration

Predecessor: **K2b**

*(The graded predecessor RECORD is K2b-U3, outcome P3 —
`K2bU3_RESULTS.md`; the parent rung id the §2ay completion-enforcement check
keys that flag by is `K2b`, verified against `[NOT A RESULT] K2b` in
`scripts/check_completion_enforcement.py`. The line-leading field above is the
lineage edge that discharges the flag; `CASE_ID_RE.search` on it returns `K2b`.)*

**FROZEN 2026-09-07 by heat-transfer-supervisor** — after a personal diff-read of
the comparator AND my own `--selftest` run (rc 0: planted control recovers PLANT,
blinded reader CAUGHT). **LAUNCH HELD** pending Sanaa's capacity decision — the
freeze fixes the grading path only; NO compute has run. **GRADING-PATH PINS (rule
2):** comparator `analyse_k2bU3R2.py` git blob
`120464450cecf8ed13816df5c9a3d640ab4b38d9` (imports the frozen predecessor
`analyse_k2bU3.py` blob `d1500a5f113c10c8547b47906474f318fbc93319` UNCHANGED and
adds only the §5.1 planted-zero control); this pre-registration frozen by sha at
this commit. The 60 mm case-dir pin (§5.3 item 2) is cut at BUILD/launch — the case
does not yet exist and the age guard requires it built fresh. Amendments after
first compute land only as struck/dated addenda that cannot alter a gate,
threshold, cap or label (rule 2). Nothing here has been sent, filed, submitted, uploaded, registered or
posted outside this box (`CLAUDE.md` rule 7). Verdict vocabulary is fixed by
`CLAUDE.md` rule 1; the new run's gate stands at **PENDING** (a queue/display
state, `REPORTING` §2 rule 5) until it runs.

---

## 0. What this document is, and what it is NOT

**IS.** An authorisation to spend the higher price (~42 core-minutes) named by the
frozen `K2b_3D_UNSTEADINESS_PREREGISTRATION.md` §4/§5, and to **run the
un-confounded Test D** that registration already defined: a 3D transient at the
spec's own **60 mm** coarse mesh, 80 s. It discharges the K2b-U3 §2ay flag
(currently `NOT A RESULT` — "UNDECIDABLE AT THIS PRICE, Test D never run — the
registered cost gate fired as designed") by putting the registered next attempt on
record with a committed cost.

**IS NOT.** A new gate, a new threshold, or a new outcome-to-meaning. Every gate,
threshold, aliasing/stationarity criterion and outcome consequence below is
**re-used unchanged and cited** from the frozen predecessor. Re-choosing the gate
to fit the answer is exactly what pre-registration forbids; this document chooses
nothing that the predecessor did not already fix before any 3D transient ran.

**It does NOT move, widen or retract any K2b-U3 verdict.** The P3 verdict, the
`DAMPS` reading of Control M, and K2b's pilot outcome O1 (PHYSICALLY UNSTEADY,
the 6.0 s ≈1.1 K limit cycle at 12.5 mm in 2D) all stand exactly as recorded.
This creates its OWN gate for the 60 mm run and nothing more.

---

## 1. Why the price is authorised now, not re-argued

The predecessor closed itself at the low price by design: Control M (2D, 100 mm)
read `DAMPS` (ratio 0.482 ≤ 0.5, aliasing guard passed at 34.4 steps / 29.9
samples per period — `K2bU3_RESULTS.md` §2), so a 3D run at 100 mm could not
separate three-dimensionality from mesh coarsening. The predecessor **named the
un-confounded experiment and its price before knowing any answer**:

> "*the cost of the un-confounded experiment is named: a 3D transient at the
> spec's own 60 mm coarse mesh, 80 s, is **≈42 core-minutes** at this rung's
> measured transient rate of 4.26e4 cell·steps/(core·s).*"
> — `K2b_3D_UNSTEADINESS_PREREGISTRATION.md` §4, lines 110-113

> "*100 mm is coarser than the spec's 60 mm 3D coarse mesh. Even P1 or P2 is a
> statement about a 100 mm 3D module, and Control M is what stops that being a
> statement about nothing.*"
> — same file, §5, lines 117-119

The second citation is the frozen basis for running at **60 mm without a Control
M**: at the spec's own coarse resolution the answer is a statement about the
spec's 3D module (the operative object), not "about nothing", so the 100 mm
confound the Control M existed to break does not arise. This is the predecessor's
own prescription, executed — not a new gate.

---

## 2. The run, and the numbers fixed before it starts

One case only: the un-confounded Test D at 60 mm. **No new Control M is run** (see
§1). The 100 mm `K2bU3_D` tree is **not** touched — `K2bU3_RESULTS.md` §3 records
it "must not be run at this resolution"; this run gets its **own new case
directory** at 60 mm, built fresh with the age guard satisfied (§5.3).

| | Test D at 60 mm (this run) | source of the fixed value |
|---|---|---|
| solver | `buoyantBoussinesqPimpleFoam`, Euler ddt, PIMPLE 2 outer / 2 inner | predecessor §3, line 45 |
| provisioning | 70 % tile provisioning, BCs of `K2bP_under`, uniform start at T_sup | predecessor §3, lines 46-47 |
| geometry | full module, **N = 4 racks, open row ends 0.60 m each** (the 3D-only path) | predecessor §3, line 51/53 |
| mesh | full module, **h = 0.060 m** (spec's own coarse 3D mesh) | predecessor §4 line 112, §5 line 117 |
| endTime | **80 s** | predecessor §3 line 54; §4 line 112 |
| maxCo | **2.0** | predecessor §3 line 56 |
| monitor interval | 0.2 s, `weightedAverage(rack{0..3}_in) of T`, mass-flow-weighted mean over the four rack front faces, per-rack reported alongside | predecessor §3 lines 58, §3.3 lines 79-81 |

The graded quantity is unchanged from the predecessor's Test D: the mass-flow-
weighted mean of T_in over all four rack front faces, per-rack values reported
alongside (predecessor §3.3, lines 79-81).

### 2.1 The aliasing guard — REUSED UNCHANGED (predecessor §3.1, lines 62-69)

A period sampled too coarsely aliases into apparent decay. **Required and reported
as measured whatever happens: ≥ 20 time steps per period AND ≥ 10 monitor samples
per period**, against the 2D limit cycle's 6.000 s period. **If the achieved Δt
delivers fewer than 10 samples per period the run is REFUSED as unable to
distinguish decay from aliasing — outcome P3 — never graded into a soft answer.**
This is the arm that made the predecessor's null a reading rather than a
non-detection, and it is unchanged here. (Note: at 60 mm, maxCo 2.0 gives a
smaller Δt than at 100 mm, so the guard is expected to pass with more margin, not
less; the achieved figures are reported as measured regardless.)

### 2.2 Windows / stationarity — REUSED UNCHANGED (predecessor §3.2, lines 72-76)

The 3D room turnover at 70 % provisioning is ≈35 s (same flow, same provisioning,
same N = 4 as the predecessor's 3D case), so **the first 40 s are discarded as
development**. Graded on the **final 20 s (60–80 s) against the preceding 20 s
(40–60 s)** — each ≈3.3 periods of the 6.000 s cycle.

### 2.3 The thresholds — REUSED UNCHANGED (predecessor §3.3, lines 83-87)

| reading | verdict |
|---|---|
| final-window p2p **≥ 0.30 K** AND ratio final/preceding **≥ 0.8** | **SURVIVES** |
| final-window p2p **≤ 0.10 K**, OR ratio **≤ 0.5** | **DAMPS** |
| anything else | **UNDECIDABLE** |

These are read straight from the frozen comparator constants
(`analyse_k2bU3.py:15`: `P_SURV, P_DAMP, R_SURV, R_DAMP = 0.30, 0.10, 0.8, 0.5`;
`:16` floors 20 / 10). Nothing is added or moved.

---

## 3. THE OUTCOMES AND THEIR MEANING — CITED, NOT RE-AUTHORED

The SURVIVES→P1 / DAMPS→P2 / UNDECIDABLE-or-guard-fail→P3 mapping and each
outcome's consequence are re-used verbatim from the frozen predecessor §4
(lines 89-113). They are reproduced here so this document is self-contained; the
binding text is the predecessor's, and this document changes none of it.

**P1 — IT SURVIVES IN 3D.** Test D reads SURVIVES. → "*The limit cycle is not an
artefact of two-dimensionality. O1's consequence carries to the 3D module: it
needs a transient formulation, the §9 steady estimate stays void, and K2a §9 must
be re-specified for transient-with-averaging at this provisioning.*"
(predecessor §4, lines 91-95, adapted only in that at 60 mm the statement is about
the spec's own coarse 3D module rather than a 100 mm one — see §4 below.)

**P2 — IT DAMPS IN 3D.** Test D reads DAMPS. → "*Three-dimensionality damps the
mode. The 2D finding stands as true of the 2D slice — it is not retracted and it
was not wrong … What changes is only its extrapolation: the 3D module may be
steady-solvable, the §9 estimate becomes revivable but not revived — it was built
on iteration counts taken from an unsteady 2D case and must be re-derived before
it is quoted.*"  (predecessor §4, lines 97-105.)

**P3 — UNDECIDABLE AT THIS PRICE.** The aliasing guard of §2.1 fails, OR Test D
reads UNDECIDABLE. → "*Stated as the answer, not resolved by preference.*" The 3D
module stays held, the §9 estimate stays void. (predecessor §4, lines 107-113;
the "Control M fails" P3 trigger of the original does not apply here, since no
Control M is run — §1.)

The gate can only turn a SURVIVES or DAMPS **into** P3 (via a guard failure),
never the reverse (`CLAUDE.md` rule 5 order; predecessor §4).

---

## 4. What this run CAN and CANNOT reach (honest labels)

- **P1 or P2 here is a statement about the spec's own 60 mm 3D module** — the
  operative resolution, so unlike the 100 mm run it is not "about nothing"
  (predecessor §5, lines 117-119, is discharged: we are AT the 60 mm mesh that
  bullet named). It is still NOT a statement about the 12.5 mm resolution where
  the 2D cycle was found; 60 mm remains 4.8× coarser than 12.5 mm.
- **NON-GATING note for the supervisor, deliberately NOT made a gate:** the
  predecessor's strongest possible un-confounding parity would pair this with a
  2D companion at 60 mm (a Control-M analogue). The frozen registration did NOT
  require one — it named the 60 mm 3D transient as "the un-confounded experiment"
  standing alone — so adding one here would be re-choosing the gate and is
  **excluded**. If the supervisor judges a 60 mm 2D companion worth having, that
  is a separate registration, not a modification of this one.
- **One provisioning, one geometry** (70 % under-provisioning, N = 4); **80 s
  cannot see a mode slower than ≈25 s** (predecessor §5, lines 121-123).

---

## 5. Controls this run MUST carry (standing rules, not optional)

### 5.1 Planted-zero control — REQUIRED, and a gap to close before freeze (rule 3)

A `DAMPS` verdict is a **near-zero p2p** reading, and a zero from a reader not
shown able to see a non-zero is not evidence (`CLAUDE.md` rule 3;
`a-zero-needs-a-live-planted-control`). **The frozen predecessor comparator
`analyse_k2bU3.py` (sha 91a26fc9…) carries NO planted-zero control** — this is a
pre-existing gap, flagged here, that the successor's comparator MUST close before
freeze. The frozen grading script for this run shall:

1. plant a known non-zero perturbation (e.g. a fixed p2p offset `PLANT`) into the
   T monitor series **after reading it from disk**, re-read it back through the
   same p2p reader, and **refuse (exit 2)** if the reader cannot recover `PLANT`;
2. only then grade the true series — so a reported `≤ 0.10 K` p2p is a measured
   near-zero, not a blind reader returning zero.

This control is a precondition of believing any DAMPS reading; the supervisor
diff-reads the comparator before belief.

### 5.2 Strict completion rule — REQUIRED (rule 4)

The run is `done` only if ALL hold: `rc = 0`; an `End` line; **last time ==
endTime (80.0)**; fields present (`T U p_rgh alphat nut k omega phi` — thermal
family); `ExecutionTime` count == `endTime`; and **every field at endTime NEWER
than the case's own `0/T`** (the age guard). The guard **refuses** a case where
`0` or a time dir already exists. A run failing any clause is `NOT A RESULT`, not
"roughly done" (`CLAUDE.md` rule 4). The completion-guard instrument is a
freeze-time pin (§5.3): either `mark_done_t3.py` reused or an F14 equivalent that
enforces the identical clause set.

### 5.3 Grading-path freeze plan — pins to be cut AT freeze (rules 2, 6)

At freeze the supervisor cuts and records, and verifies each frozen file **is**
the file that ran by hashing it against its committed blob (rule 2):

1. **This pre-registration** — frozen by sha at commit; grading path fixed at that
   commit; amendments after first compute land only as struck/dated addenda that
   cannot alter a gate, threshold, cap or label.
2. **The 60 mm case directory** — a NEW tree, e.g.
   `verification/runs/F14-cooling-ladder/K2b_runs/K2bU3R2_D60/` (NOT the 100 mm
   `K2bU3_D`, which must not run). Pin: sha256 of `system/`, `constant/` and
   `0.orig/` of the built case at freeze, built with `0`/time dirs absent so the
   age guard is satisfiable.
3. **The comparator** — a frozen script (a parameterisation of `analyse_k2bU3.py`
   to the 60 mm case dir, or a sibling `analyse_k2bU3R2.py`) carrying the §5.1
   plant; pin its sha256 at freeze. It reuses the §2.1–§2.3 constants unchanged.

No comparator or case has been written or modified by this draft (see the report).

---

## 6. Cost — costed before the run (rule 12)

**Pre-registered estimate: ≈ 42 core-minutes**, taken directly from the frozen
predecessor §4 (line 112: "≈42 core-minutes") for exactly this experiment — a 3D
transient at the spec's own 60 mm coarse mesh, 80 s, at the rung's measured
transient rate **4.26e4 cell·steps/(core·s)**. The rate is measured (predecessor
§4, line 113); the cell-count and achieved step-count that multiply out to ~42
core-min are **pins measured at freeze** from the built 60 mm mesh and the
achieved Δt (§5.3), reported estimate-vs-actual at completion per rule 12.

**Cap: 63 core-minutes (1.5× the estimate).** An overrun **stops the run**; it
does not get a new budget (`CLAUDE.md` rule 12). If the run reaches the cap
without satisfying §5.2, the result is `BLOCKED` (over-cap), not a graded outcome.

**cost_basis:** REPORTED-BY-OWNER at **$0.0513/core-h** (owner-stated 2026-08-21/22;
the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5). DERIVED
dollars (NOT measured):
- estimate 42 core-min = 0.700 core-h → **$0.036** (derived)
- cap 63 core-min = 1.050 core-h → **$0.054** (derived)

Both are far under the $25/run pre-authorisation; a larger CPU run would still be
costed here regardless (rule 9: a blanket is not a per-item read). A
`docs/COST_CALIBRATION.md` row is owed at completion (estimate 42 core-min vs
actual from the log) and is the supervisor's to land.

---

## 7. Lineage and scope (what this discharges)

- **Discharges** the K2b §2ay flag `NOT A RESULT` ("UNDECIDABLE AT THIS PRICE,
  Test D never run") by registering the active next attempt via the line-leading
  `Predecessor: **K2b**` edge at the top of this file (recognised by
  `scripts/check_completion_enforcement.py` `_find_lineage_successor`).
- **Does not** alter the K2b-U3 P3 verdict, the Control M `DAMPS` reading, or O1.
- **Creates** one new gate (the 60 mm Test D), currently **PENDING** — it grades
  only after the run satisfies §5.2 and the frozen comparator (with the §5.1
  plant) returns rc 0.

**FROZEN 2026-09-07 (grading path pinned — see the freeze stamp at the top).
LAUNCH HELD pending Sanaa's capacity decision.**
