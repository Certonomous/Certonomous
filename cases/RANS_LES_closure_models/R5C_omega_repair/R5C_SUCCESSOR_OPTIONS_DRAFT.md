# R5C successor options — decision analysis after the omega-repair GATE FAIL

> **STATUS: DRAFT — NOT FROZEN — NOTHING MAY RUN AGAINST IT.**
> Prepared for closure-supervisor review under `SUPERVISION_CHARTER.md` §3
> check-4. This file registers nothing: no gate, threshold, cap or label below
> is closed, no sha256 here binds anything, and no solver, fit, selection,
> propagation, run directory or queue entry is authorised by it. It is a
> **proposal to the supervisor**, not a pre-registration. Nothing here has been
> sent, filed, uploaded, registered, posted or commented (CLAUDE.md rules 2, 7).
>
> **Zero compute produced this file.** Every number is quoted from a record
> already on disk, with its artefact path. The lab **ranks and argues; it does
> not choose** — the successor decision, and any re-baselining or direction
> call, is the supervisor's or Sanaa's per §4 below.

**Lane:** closure. **Predecessors:** `../R4_sparta_build/` (GATE FAIL),
`R5C_omega_repair/` (GATE FAIL). **Date drafted:** 2026-09-09.
**Follows the structure and honesty discipline of** `docs/closure/R5_DECISION_MEMO.md`.

---

## 0. Why this file exists

The §2bc exhaustion re-audit
(`docs/closure/CLOSURE_2BC_EXHAUSTION_REAUDIT.md`, Row 8) classified
`R5C_omega_repair` as **NEEDS-SUCCESSOR**: "a live numerics/convergence
question, not an exhausted finding — premature as terminal." An owed successor
must register the path that drives the **3 non-converged** and the **15
still-INCOMPLETE hill** rows to a defensible state before R5C's GATE FAIL is
treated as terminal (exhaustion-proven) and the line stops. The GATE FAIL
verdict itself stands as written; a successor addresses only its terminality.
R5C was itself `R5_DECISION_MEMO.md` option **C** run to a verdict; the
memo pre-dates R5C's result, so the successor question is genuinely re-opened by
what C actually returned. This file grounds the options in the R5C artefacts so
the supervisor can freeze one (a within-R3 §3 check-4 act) or route the big move
to Sanaa.

---

## 1. The precise breach — from the R5C artefacts, not from prose

R5C's verdict is **GATE FAIL**, governed by **G1** (identity on R4's frozen 12
targets). G1 carried two clauses (RESULTS.md §3.1, line 17): (i) `max` rel-L2 of
`kDeficit`/`bijDelta` ≤ **1e-6**; and (ii) all 12 R4-COMPLETE targets still
COMPLETE **and** CONVERGED under G3. Both clauses fired. **The two clauses do not
fire on the same set of cases**, and that distinction is the whole of the
analysis below.

**The G3 convergence criterion that all three breaches fail is criterion (d):**
`initRes(1) / initRes(convergedAt) ≥ 1e6` (the residual-fall ratio;
`grade_r5c.py:53` `G3_RES_FALL = 1e6`, computed at `:188` `d["d_res_fall"]`).

### The exact 3 of R4's 12 targets that are non-CONVERGED under the R5C operator

Every number below is from
`R5C_omega_repair/artefacts/r5c_grading.json`, field paths named.

| target | fails G1 identity? (`≤1e-6`) | fails G3? which criterion | settle it. R4→R5C | numbers + json field |
|---|---|---|---|---|
| **`alpha_10_12000_4048`** | **YES** — rel-L2 `kDeficit` = **1.1848e-04** (`bijDelta` 1.1737e-08) | **YES**, G3(d): `d_res_fall` = **4.7252e+04** < 1e6 | 1362→**853** (**−37.4 %**) | `G1.rows[..].rel_l2_kDeficit`; `table[..].g3.d_res_fall`, `.g3.pass.d=false` |
| **`alpha_15_10929_4048`** | **no** — rel-L2 `kDeficit` = **4.385e-09**, `bijDelta` = **9.087e-08** (both `≤1e-6`) | **YES**, G3(d): `d_res_fall` = **7.5106e+05** < 1e6 | 1382→1382 (0.0 %) | same fields |
| **`PHLL10595`** | **no** — rel-L2 `kDeficit` = **5.950e-10**, `bijDelta` = **3.624e-09** (both `≤1e-6`) | **YES**, G3(d): `d_res_fall` = **9.1673e+05** < 1e6 (**8.3 % short**) | 1243→1243 (0.0 %) | same fields |

All three pass G3 criteria (a) zero bound events, (b) `min(omega)>0` from disk,
(c) `convergedAt≥100`, (e) no pre-window flat-domega — only (d) fails
(`table[..].g3.pass = {a:T,b:T,c:T,d:F,e:T}` on each).

### The crux, stated exactly

Only **one** of the three breached targets — `alpha_10_12000_4048` — actually
voids identity (rel-L2 1.18e-04, 118× the 1e-6 bar). The other **two**
(`alpha_15_10929_4048`, `PHLL10595`) reproduce R4's frozen targets to **1e-9 and
1e-10** and fail only the ratio criterion (d). R5C's own record diagnoses (d) as
**miscalibrated** (RESULTS.md §6.2): it is a ratio where an absolute bar was
needed, the absolute bar already lives in the settle criterion, and as
registered it **rejects R4's own W2-validated reference case** `PHLL10595` at
8.3 % short of the bar. So of the "3 of 12 not CONVERGED," **two are
identity-clean and fail a gate-design artifact**; **one is a genuine
field-space drift**.

Note the verdict does not hinge on criterion (d): G1 clause (i) fails on
`alpha_10_12000_4048`'s 1.18e-04 identity drift regardless of (d), so
recalibrating (d) would not have changed R5C's GATE FAIL. The (d) finding is a
successor-gate-design lesson (see LESSONS L-515), not a re-grade of R5C, whose
grader is frozen.

**Why the one genuine breach happened** (RESULTS.md §5.1–5.2, confirmed against
the settle-iteration column): the Patankar-split sink damps the outer iteration
more strongly — that is exactly what stops `omega` going negative — so the
**change-based** settle criterion (`omega initRes < 1e-8` **and**
`max|Δomega|/max|omega| < 1e-9`) is reached **509 iterations sooner**, at a point
further from the shared fixed point. Where the two operators stop at the **same**
iteration (11 of 12 cases) they agree to **1e-11** (§5.1). **The fixed point is
confirmed shared, not falsified; only the stopping distance moved on one case.**

---

## 2. Is an identity-preserving repair mechanically possible?

**One-line answer: PLAUSIBLE in mechanism, but the magnitude is UNMEASURED (a
run is needed to confirm ≤1e-6 on the one drifted case).** The tension is **not**
between hill-completion and the extraction operator — it is between
hill-completion and the **change-based convergence criterion**.

The reasoning, from evidence already on disk:

1. **The operator preserves the fixed point.** RESULTS.md §5.1: 11 of 12 targets
   settle at the identical iteration under the repaired operator and agree with
   R4 to 1e-7–1e-11; all four ducts and both W2 cases match to 1e-11. R5C §2.2's
   registered fixed-point identity was **confirmed, not falsified** (§5.3 says
   this explicitly). The Patankar split changes the *iteration path*, not the
   *answer the path converges to*.

2. **The single breach is a stopping-distance artifact, not an operator drift.**
   On `alpha_10_12000_4048` the error is broad and small (largest cell carries
   0.08 % of the squared error; `k` differs by exactly 0 — it is frozen data),
   the run simply stopped 509 iterations early (§5.2). A convergence criterion
   that bounds **distance to the fixed point** (rather than change per
   iteration) would iterate that case further, toward the shared fixed point
   R4's target sits on.

3. **Two of the three "non-converged" targets already preserve identity to
   1e-9.** They fail only criterion (d), which the record itself flags as
   redundant/miscalibrated (§6.2) and which rejects R4's own reference case.

**Therefore:** a repair that (a) completes the hills under the Patankar-split
operator **and** (b) holds R4's frozen-12 identity to ≤1e-6 is **plausible**,
because it does not require a different operator — it requires the *same*
operator paired with a convergence criterion that bounds distance-to-fixed-point.
Completing the hills does **not** necessarily void identity.

**What this claim cannot see (honest limit — VERIFY by run).** Whether a
distance-bounding criterion actually pulls `alpha_10_12000_4048` back inside
1e-6 is **not measured** — R5C never ran that criterion, and §5.2/§6.2 both note
that *nothing in R5C measures distance to the fixed point*. It is proven only
where the settle iteration already coincided. If, on running, the drift proves to
be a real operator-level difference on that one case (not merely an early stop),
then hill-completion and frozen-12 identity **are** in genuine structural
tension and the answer routes to C2 (§3). This is the honest fork the successor
must be pre-registered to resolve either way.

---

## 3. The successor options

Costs are from R4's measured rate card (`R5_DECISION_MEMO.md` §2; rate
$0.0513/core-h, owner-stated, **reported-by-owner not measured**, CLAUDE.md rule
12). Every dollar figure is **derived, not measured**.

### Summary

| # | option | compute | cost (derived) | crosses §18's 487 core-h? |
|---|---|---|---|---|
| **R5D** | identity-preserving completion (Patankar operator + distance-to-fixed-point criterion + re-registered identity gate) | ~**0.184** core-h re-extract (R5C measured **0.140**) | ~**$0.009** | no |
| **C2** | accept R5C operator as new baseline; rebuild R4 fit+propagation on 27 cases under one operator | **19.148** core-h | **$0.982** | no |
| **A′ (R4b)** | uniform amplitude/realisability control on the pair (`b^Δ` and `R`) on R4's frozen 12 | **0.576–5.365** core-h | **$0.030–$0.275** | no |
| **D** | bank the harness result, stop discovery | **0.000** | **$0.000** | no |

---

### R5D — identity-preserving completion *(the new option R5C's result creates; offered only because §2 finds it plausible)*

**What it would establish.** Whether the Patankar-split operator — which already
removed clipping on 22 of 27 cases and completed 10 of 15 hills — can complete
the hills **while** preserving R4's frozen-12 identity to ≤1e-6, once the
change-based settle criterion (which §5.2 shows exploits the extra damping) is
replaced by one that bounds distance to the fixed point. It is the direct
discharge of the re-audit's owed successor: it drives the 3 non-converged rows
(by iterating them to a distance bar) and re-attempts the 15 hills under an
operator not in tension with identity.

**What it would cost.** A 27-case frozen re-extraction, as R5C: registered
0.184 core-h / $0.009 (memo §3 C); R5C actually spent **0.140 core-h measured**
on 29 runs (RESULTS.md §9). Identity re-validation on the frozen 12 (byte / rel-L2
against R4) ~0. Modest upward risk if the distance criterion forces longer
iteration on a few cases; bounded well under R5C's own 1.0-core-h cap.

**What it would pre-register (before any run).**
1. The **Patankar-split operator in full**, and that it *is* the R5C operator
   (its `libspartaFrozenV2.so` / `kCorrectiveFrozenFoamV2` already exist under
   `sdk/openfoam/sparta/`; RESULTS.md §10).
2. A **distance-to-fixed-point convergence criterion** replacing the change-based
   settle **and** the miscalibrated G3(d) ratio — the quantity §5.2/§6.2 show
   nothing in R5C measures. This is a *new* criterion registered up front, not an
   edit to R5C's frozen file (rule 2/6).
3. The **identity gate re-registered on R4's frozen 12** at ≤1e-6, with the
   fixed-point-identity and byte-identical W2 reproduction as gates *before* the
   run (as R5C did; G2 passed 14/14).
4. The **planted-zero control** (R5C's G0 pattern, PLANT 1.234e-03) and the
   strict six-condition completion rule (rule 4), up front.
5. A **registered rule for the partial outcome** — what stands if the criterion
   completes some hills and not others.

**The NOT-A-RESULT branch.** If, under the distance-bounding criterion,
`alpha_10_12000_4048` (or any frozen-12 target) still exceeds 1e-6 identity, then
the drift is operator-level, not stopping-distance — hill-completion and
frozen-12 identity are in genuine tension, R5D is **GATE FAIL**, and the question
routes to C2. A subtler failure to guard: a criterion that "converges" by a new
flat mode — the L-235/L-243 shape (a criterion that cannot tell convergence from
clipping/damping), which R5C already caught once. The distance criterion must
itself carry a planted control that a flat field cannot pass.

**Freezability:** **within R3** (SpaRTA operator unchanged; a numerics/criterion
finding-repair — exactly the FREEZE-AHEAD repair-registration class). Supervisor
§3 check-4, doc + instrument in one commit.

---

### C2 — accept the R5C operator as the new baseline, rebuild on 27 cases *(memo §3 C2)*

**What it would establish.** The SpaRTA fit and propagation rebuilt on the
enlarged, less-biased 27-case set under **one** operator, removing R4's
known selection bias (its 12 targets are the cases whose frozen `omega` happened
not to go negative — a non-random sample; memo §5, R4 RESULTS §7/§11.3c).

**What it would cost (memo §3 C2).** C (0.184) + FS3 selection (0.262) + three
27-case configuration sweeps (3 × 6.234 = 18.702) = **19.148 core-h / $0.982**.

**What it would pre-register.** A **new operator-identity gate** (the R5C
operator's own defining identity, registered as a gate), the full 27-case
completion rule, the FS2/FS5/realisability discharges, and — critically — the
explicit statement that **R4's frozen 12 targets and the R5C targets are
different quantities**: no number crosses between them without saying so.

**What it VOIDS, stated plainly.** Every cross-comparison to R4's frozen numbers.
R4's `MODEL.md` coefficients, its a-priori bars, its ceiling numbers are all
extracted under the old operator; C2 abandons them as the reference frame. This
is not a case-level change — it re-founds the line's evidentiary baseline.

**The NOT-A-RESULT branch.** The rebuilt operator completes the hills but no
longer reproduces the W2 record byte-identically → the enlarged dataset carries
an unmeasured operator error rather than 15 honest hills (memo §3 C failure
mode). And the sharper one: a rebuild that converges by clipping flat (L-221
shape).

**Freezability:** **Sanaa's call.** See §4 — C2 re-founds the reference frame the
whole closure line is calibrated against and voids standing frozen numbers.

---

### A′ (R4b) — uniform amplitude/realisability control on the pair *(memo §3 A′; drafted at `../R4b_pair_control/`)*

**Read of the drafted files.** `../R4b_pair_control/PREREGISTRATION.md` (DRAFT,
2026-08-24) and `INSTRUMENT_BUILD_PREREGISTRATION.md` (`R4b-I`,
PENDING_SUPERVISOR_FREEZE, 2026-08-28). It is **option A′**: one uniformly-applied
control on the pair `b^Δ` and `R`, with Charter §4's realisability clause in the
verdict ladder, on **R4's standing 12 targets**.

**Does it depend on R5C data? NO.** The prereg states verbatim (line 1277):
*"This build uses no R5C target."* It fits and propagates on R4's frozen 12; it
is fully decoupled from the R5C successor question. It can proceed on its own
schedule regardless of which R5C successor is chosen.

**Cost (memo §3 A′).** 5.365 core-h / $0.275 planning; **0.576 core-h / $0.030**
floor if it diverges early.

**Freeze-readiness — a real wrinkle.** The four instruments **exist as files**
(`select_control.py`, `build_r4b_cases.py`, `run_r4b.sh`, `grade_r4b.py`, all
2026-08-28; a birth record ran PASS). **But** the instrument-build registration
`R4b-I` had its gates **CLOSED by inadvertent first compute** (the `_dev/` run
under `/home/ubuntu/closure-data/r4b_instruments/`, ruled first compute by the
supervisor), so `grade_r4b.py` may no longer be edited. The route is a
**successor instrument `R4b-Ib`** (`R4b_Ib/grade_r4b_ib.py` +
`INSTRUMENT_BUILD_PREREGISTRATION_R4b_Ib.md`, both DRAFT, 2026-08-31), which must
land **doc + grader in one commit** as the supervisor's act. So: **instrument
exists (y)**, but the freeze must resolve the R4b-I→R4b-Ib successor-instrument
path first.

**Freezability:** **within R3** — Sanaa ratified "SpaRTA-class, TBNN fallback"
(2026-08-24) and A′ is an amplitude/realisability control on the SpaRTA pair.

**The NOT-A-RESULT branch (memo §3 A′).** The control strength is tuned per
family to buy convergence → there is no one model, there are two. Or a scaling
chosen after seeing a propagation outcome (calibration on the graded quantity).

---

### D — bank the harness result, stop discovery *(memo §3 D)*

**What it would establish.** Nothing new — it is a documentation act. The
harness result is already real and banked in `R4_sparta_build/RESULTS.md` §11 and
in R5C's record: a reproducible frozen-field ceiling and a proven negative
result. D adds only the decision to **stop** discovery on the line.

**Cost.** 0.000 core-h / $0.000.

**The NOT-A-RESULT branch.** Presenting the extracted-from-truth ceiling as a
model prediction (memo §3 D). And: banking closes nothing else — the 15 hills
stay unextracted, R6 stays NOT DONE.

**Freezability:** **Sanaa's call** — stopping discovery is a direction decision
on the line (memo §5; Charter §22.7/§22.8 frame line-closure and release as
hers).

---

## 4. Freezability map — who owns each call

**Strictly applied.** R3 = the model *class* pick, ratified by Sanaa 2026-08-24
("SpaRTA-class, TBNN fallback"), hers under `CLOSURE_MODELLING_CHARTER.md` §22.7.
A successor is supervisor-freezable (§3 check-4) only if it stays inside that
ratified class **and** does not re-found the line's evidentiary baseline.

| option | within-R3, supervisor-freezable? | owner of the call | why |
|---|---|---|---|
| **R5D** identity-preserving completion | **YES** | closure-supervisor (§3 check-4) | Same SpaRTA operator; a numerics/criterion finding-repair, exactly the FREEZE-AHEAD repair-registration class. Preserves R4's frozen numbers by design. |
| **A′ (R4b)** | **YES** | closure-supervisor (§3 check-4) | Amplitude/realisability control on the ratified SpaRTA pair, on R4's frozen 12; no re-baselining. (Must first resolve the R4b-I→R4b-Ib instrument path.) |
| **C2** re-baseline on the R5C operator | **NO** | **Sanaa** | Big move: it **voids every cross-comparison to R4's frozen numbers**, abandons R4's `MODEL.md` reference frame, and re-founds the line's baseline under a new operator-identity gate. Model class stays SpaRTA, but re-founding the reference frame and retiring standing frozen numbers is beyond a case-level freeze — it is a line-direction decision. |
| **D** stop discovery | **NO** | **Sanaa** | Closing the discovery line is a direction call (memo §5). |

**Note on the R5D→C2 fork.** R5D is the cheap within-R3 test of §2's plausibility
claim. If R5D returns GATE FAIL (identity genuinely un-preservable while
completing hills), the successor question **escalates** to C2 — a Sanaa call —
because at that point the only path to the enlarged data set is re-baselining.
The supervisor can freeze R5D alone; the supervisor **cannot** pre-commit C2 on
R5D's behalf.

---

## 5. Cross-reference — the other drafted closure successors, so the map is complete

Two further closure repair-registrations are drafted and PENDING_SUPERVISOR_FREEZE.
Both are **separate** from the R5C successor (neither drives the R5C
non-converged/incomplete rows); they are listed so the supervisor's freeze
picture is whole. **Their own headers state the freeze rule: the freeze commit
must carry the document AND its instrument together** (rule 2).

| item | status | instrument exists? | freeze-ready? | scope |
|---|---|---|---|---|
| **RC1** `../RC1_birth_requirement_control/` | PENDING_SUPERVISOR_FREEZE (2026-08-28) | **NO** — dir holds only `PREREGISTRATION.md` + `QUEUE_ENTRY_DRAFT.json`; header: "this item's instrument does not exist yet" | **NO** | Birth-requirement control for every closure log reader (a standing-instrument control) |
| **RC2** `../RC2_kaandorp_divergence_repair/` | PENDING_SUPERVISOR_FREEZE (2026-08-28) | **NO** — same; header says the freeze needs "this document and both instruments" | **NO** | Kaandorp divergence-flag reader repair + re-grade from preserved artifacts (the re-audit's Row 4 owed successor) |

Neither can be frozen until its instrument is built and lands in the same commit
as its doc. Both are within-R3 finding-repairs when their instruments exist.

---

## 6. RECOMMENDATION — marked as a recommendation; the lab ranks, it does not choose

**Recommended order: R5D first. Then A′ (R4b), which is independent and can run in
parallel. C2 only if R5D returns GATE FAIL. D holds regardless.**

**R5D first, because §1 shows the breach is mostly a criterion artifact, not an
operator failure.** Two of the three "non-converged" targets reproduce R4 to
1e-9 and fail only a ratio criterion the R5C record itself calls miscalibrated
(§6.2); the one genuine drift is a 509-iteration early stop on a **confirmed
shared fixed point** (§5.1). The cheapest, most conservative move is to re-run
the working Patankar operator under a convergence criterion that bounds distance
to the fixed point, with the identity gate re-registered — ~$0.009, within R3,
and it preserves R4's frozen numbers by construction. It is the direct discharge
of the re-audit's owed successor.

**A′ (R4b) can proceed independently** — it uses no R5C target (§3), so it does
not wait on the R5C fork. The supervisor should resolve its R4b-I→R4b-Ib
instrument-successor path when freezing it.

**C2 is a Sanaa call and should not be reached for first.** It costs 100× R5D and
voids the line's frozen reference frame. It becomes the right move only if R5D
demonstrates that hill-completion and frozen-12 identity are genuinely
incompatible — which §2 says is **not** the current evidence.

**D holds regardless** — the harness result is already banked; D adds only the
decision to stop, which is Sanaa's.

**Band-caveat discipline (Charter §22.4).** No model-form band is quoted anywhere
above; every number is a training-family measurement or a projected cost from
R4's rate card. **None is presented as bounding an error it cannot see.** The
eigenspace family's blind spot remains `k`-magnitude — the axis `R` corrects —
and no band is applied as a correction here.

---

## 7. What this file cannot see (honest limits)

- **It has measured no successor outcome.** §2's plausibility claim is a
  mechanism argument from R5C's confirmed shared fixed point; whether R5D
  actually holds `alpha_10_12000_4048` to ≤1e-6 is **UNMEASURED** and needs the
  run.
- **It prices R5D and C2 from R4's rate card**, not from a run of those exact
  configurations; the distance-criterion iteration cost is an estimate.
- **It reads the R4b/RC1/RC2 drafts as they stand on disk today**; a freeze
  action by the supervisor would change their state and this file does not track
  that.
- **It opens no test or validation case and prepares no submission.** Every R5C
  number is a training-family number; nothing here generalises beyond the
  training set, and re-opening R3 or the line's direction remains Sanaa's.
