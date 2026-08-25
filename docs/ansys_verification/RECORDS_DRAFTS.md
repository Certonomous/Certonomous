# RECORDS DRAFTS — ansys-verification team's pending LESSONS / NUMERICS entries

**NOT FILED ANYWHERE. Nothing here leaves this box** (CLAUDE.md rules 7, 8).

**This is a DRAFT staging file in this team's own territory.** Nothing in it has been
committed to `docs/LESSONS.md` or `docs/NUMERICS_KNOWLEDGE.md` by the drafting lane.
Per this task's instruction, the opus lane **drafts**; the supervisor **reads before
anything lands** — that is the supervisor's check, not the lane's. Numbers below are
re-derived from HEAD **max + 1** at landing time, in the same shell invocation as the
commit (CLAUDE.md rule 11), never from a count and never from these draft placeholders.

Drafted by `ansys-lane-opus48` (`claude-opus-4-8[1m]`), 2026-08-25.

---

## FINDING FIRST — the two "never landed" lesson candidates are ALREADY LANDED

The brief named two lesson candidates as *"DRAFTED AND NEVER LANDED by an earlier
lane"* (this team's LAB_STATE section). **Read from the HEAD blob this session, both
are in fact already committed** — the LAB_STATE note is stale, and re-drafting them
would create duplicate lesson numbers. Verified against `git show HEAD:docs/LESSONS.md`:

- **Lesson (a) — sub-linear continuation — is `L-301`.**
  Title at HEAD: *"Extending a converging steady SIMPLE run is SUB-LINEAR in cost —
  price a continuation at ≈ 0.88 × linear, and say which case measured it."* The
  numbers check out against the logs this session:
  - Run 1 L3 (3000 iters): `ExecutionTime = 103.99 s` → **34.66 ms/iter**.
  - R2 L3 (6000 iters): `ExecutionTime = 182.31 s` → **30.39 ms/iter**.
  - Linear extrapolation of the first-3000 rate to 6000 iters = 207.9 s; actual
    182.31 s; **ratio 0.877 ≈ 0.88×**. L-301 is correct as landed.
- **Lesson (b) — a gate value from a gitignored artifact — is `L-300`.**
  Title at HEAD: *"A gate value whose source artifact is gitignored is a number with
  no artifact — the sampled files are named in the pre-registration and landed by
  EXPLICIT path."* It cites `.gitignore:67` (`**/postProcessing/`) and the six
  VMFL001/R2 `.xy` blobs landed via `git update-index --add`, exactly as the brief
  describes. L-300 is correct as landed.

**No re-draft of L-300 / L-301 is proposed.** The records duty for both is discharged.
The action for the supervisor is to **correct this team's LAB_STATE section** so a
future lane is not sent to re-land them.

---

## PENDING NUMERICS — a records BACKLOG the supervisor should know about

`docs/NUMERICS_KNOWLEDGE.md` at HEAD carries the AV family only to **N-AV6** (verified:
headers N-AV1…N-AV6, nothing higher). But the **VMFL005 record and register row #3
forward-cite `N-AV7` and `N-AV8`** as if they exist:

- `N-AV7` — cited as *"a small GCI is a statement about grid convergence only; it does
  not license the claim that the remaining deviation from a reference is numerical"*
  (VMFL005 RESULTS §5 / the supervisor's course-correction). **Not present as an entry
  in `docs/NUMERICS_KNOWLEDGE.md`.**
- `N-AV8` — cited as the wedge's `Uz` out-of-plane null channel, excluded from the
  gate and printed rather than dropped (VMFL005 RESULTS §2.3, register row #3). **Not
  present as an entry.**

This is exactly the loss §7 of the ANSYS charter warns against: *"A finding noted only
in a lane's report and not in one of these files is lost at the next compaction."* Two
numerics facts are promised by the credential record and are not yet in the numerics
file. **Recommend the supervisor land N-AV7 and N-AV8 (their content already exists in
the VMFL005 record) before or alongside the candidate below**, so the next free AV
number is settled. This lane does not land them (they are not this task's product), but
flags the gap.

---

## DRAFT NUMERICS CANDIDATE — the OpenFOAM wedge area deficit (proposed `N-AV9`, re-derive at landing)

*Proposed number `N-AV9` assumes N-AV7 and N-AV8 are landed first; re-derive max+1 at
commit.*

**Draft entry text:**

> ## N-AV9. An OpenFOAM axisymmetric **wedge** under-represents the true circular
> cross-section by the factor `sin(t)/t` (0.127 % at t = 5°), a MODELLING bias that
> grid refinement does not remove — carry it in the error budget of every axisymmetric
> case run against an exact target
>
> **The fact.** An OpenFOAM wedge cell is a flat-sided triangle, not a circular
> sector. For total included angle `t`, the modelled cross-section area is
> `½ R² sin(t)` against the true sector `½ R² t`, short by the factor **`sin(t)/t`**.
> At `t = 5°` (`= 0.08726646259971647` rad): `sin(t)/t = 0.9987312439537492`, an area
> deficit of **0.1268756 %**. This is a property of the mesh, not an approximation of
> the reader: for VMFL005 the modelled L3 inlet-patch area `½ R² sin(t) =
> 6.809042402160794e-08 m²` matches the solver's own monitor-header area
> `6.809042402188e-08 m²` to eleven significant figures.
>
> **Why it matters.** For VMFL005 (Hagen–Poiseuille, exact 10.24 Pa) the fine-grid dP
> deviates 0.4979 % from exact while GCI_fine is only 0.0502 % — 90 % of the deviation
> is not discretisation error (N-AV7). Under a fixed-volumetric-flow reading
> (dP ∝ R⁻⁴, effective-radius deficit `√(sin t/t)`), the wedge deficit inflates dP by
> `(sin t/t)⁻² = +0.2542 %` — **51 % of the deviation**; under a fixed-mean-velocity
> reading (dP ∝ R⁻², as the imposed inlet profile suggests) it inflates dP by
> `(sin t/t)⁻¹ = +0.1270 %` — **26 %**. Either way the wedge geometry is a
> **substantial but partial** contributor of order a quarter-to-half, and it does
> **not** close the gap (the remaining candidates in VMFL005 RESULTS §5.3 stay open;
> docket keeps the question).
>
> **The consequence, which is why this is recorded.** The deficit is **independent of
> radial and axial refinement** — the 5° azimuthal wedge is fixed while the triple
> refines r and x — so it is a MODELLING error that a converging Roache triple carries
> to its extrapolate rather than removes. Every axisymmetric case run against an
> **exact** target (VMFL002, VMFL007, VMFL028, VMFL036, VMFL044, VMFL058, VMFL073,
> VMFL076) inherits it. Mitigation: use a **smaller wedge angle** (the deficit is
> `O(t²)` — `1 − sin(t)/t ≈ t²/6`, so 1° cuts it 25×) or **carry `1 − sin(t)/t` as an
> explicit line in the pre-registration's error budget** so a converging-triple PASS
> is not mistaken for convergence to the exact value.
>
> *Artifacts:* `cases/ansys_verification/VMFL005/RESULTS.md` §5.3;
> `verification/runs/ansys_verification/VMFL005/L3_400x40/postProcessing/pInletMonitor/0/surfaceFieldValue.dat`
> (monitor-header area); the arithmetic in
> `docs/ansys_verification/COVERAGE_ROWS.md`.

**Provenance of the arithmetic** (re-derivable, no solve): `t = 5° = 0.08726646259971647`
rad; `sin(t) = 0.08715574274765817`; `sin(t)/t = 0.9987312439537492`; `(sin t/t)⁻² =
1.0025423495…` (+0.2542 %); `(sin t/t)⁻¹ = 1.0012703678…` (+0.1270 %); VMFL005
deviation 0.49790415 %; fractions 51.06 % and 25.51 %. Wedge half-angle 2.5° / total
5° read from `cases/ansys_verification/VMFL005/case/system/blockMeshDict.template` and
`constant/polyMesh/boundary` (`wedge1`/`wedge2`, `type wedge`).

---

## FLAG — a docket-id collision to check (not resolved here)

Register row #3 and the VMFL005 RESULTS §5 state the open mechanism question is
**docket `D510`**. But `git show HEAD:docs/DOCKET.md` shows **`D510` is the closure
team's "R3 ratified" row**, not a VMFL005 row. The two cite the same id for different
questions. This lane does **not** edit the docket (outside this task and outside the
private-index paths this task commits). **Flagged for the supervisor** to reconcile
with `scripts/check_docket_reconciliation.py` and assign VMFL005's open question a
free id (the supervisor's own note gives max D = 511, so D511+ is free). Recorded here
so the finding is not lost (§7).

---

## Charter entries — none proposed this session

No finding this session changes how the lab **grades** (a tolerance class, a
completion clause, a control), so no dated charter amendment is drafted. The wedge
deficit is an **error-budget** fact (numerics), not a grading-rule change. If the
supervisor judges that axisymmetric cases should be *required* to carry `1 − sin(t)/t`
in their pre-registration error budget, that would be a grading-convention change and
belongs as a dated amendment to `ANSYS_VERIFICATION_CHARTER.md` §5 routed through the
chief — flagged, not drafted, because widening or setting a grading rule is not this
lane's call.
