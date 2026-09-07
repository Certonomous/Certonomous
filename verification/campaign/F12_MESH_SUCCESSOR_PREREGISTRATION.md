# F12-MESH SUCCESSOR — RAE 2822 Case 9 re-block — pre-registration (DRAFT)

> **DRAFT — NOT AUTHORISED — CHECK-4 NOT TAKEN.**
> A cfd `lab-lane` draft. Not frozen; no sha commits it; **no solver launched and no
> mesh built** in producing it. The rule-2 freeze (gate/threshold/cap/label by sha,
> grading path hashed against the committed blob) is the cfd supervisor's non-
> delegable check 4, which for this case must **also** decide the two matters §7 of
> the parent referred (the secondary-reference P question, and the plateau-clause /
> code-verification additions). Editable until frozen. Drafted 2026-09-07.

**§2ay classification of the parent.** Parent verdict: **F12 GATE FAIL** at all three
mesh levels on admission gate A (mesh) and on gate B (convergence) —
`verification/campaign/F12_RESULTS.md:22,112-114`. The census flagged it as a
standing violation: a landed GATE FAIL with **no active dated fix-successor** — even
though the parent record itself names the fix path at `:290` (a counterfactual
topology-repaired mesh) and `:592-597` ("F12 needs a fresh pre-registration
regardless … re-registers the ladder — block topology and wall-normal recipe both").
This draft is that successor. It is **not** a capability gap (state a): the failure
is a **mesh** our-side defect — a block topology whose non-orthogonality exceeds the
lab's 70° gate — and `rhoSimpleFoam` on an admissible RAE 2822 mesh is a routine,
demonstrated capability.

---

## 1. WHAT FAILED, MEASURED

**Gate A (mesh), all three levels FAIL — on non-orthogonality alone** (`:110-114`):

| level | cells | max non-orthogonality | faces > 70° | max skewness | gate A |
|---|---|---|---|---|---|
| coarse | 23,040 | **70.646°** | 892 | 0.827 (passes, 4.8× margin) | GATE FAIL |
| medium | 92,160 | **70.861°** | 3,598 | 0.827 | GATE FAIL |
| fine | 368,640 | **72.542°** | 14,399 | 0.827 | GATE FAIL |

The breach **worsens under refinement** (70.6 → 72.5°; offending faces ×4 per level):
the >70° faces are a fixed *fraction* of the mesh, a property of the **block topology
and the wall-normal grading recipe**, not curable by refinement (`:123-127`). The
finest mesh — the one gates 1–4 would be graded on — fails gate A by 2.54°, so
**F12 has no admissible mesh anywhere in its ladder** (`:129-133`).

**Gate B (convergence) FAIL** (`:158-183`): `rhoSimpleFoam` aborted at iteration 180
of 6,000 with `Negative initial temperature T0: -1.72234834` (`thermoI.H:57`). The
supervisor's own crash triage (`:280-293`) records this as **consistent-but-not-
demonstrated** with the gate-A breach: a negative temperature in a compressible
solver is the canonical symptom of corrupted gradient/diffusion terms, and 892 faces
above 70° is exactly the condition under which the non-orthogonal Laplacian
correction becomes unreliable. The incidence (α = 2.79°) and Mach (0.734) were
measured correct in `0/U`/`0/T` (`:244-261`) — the setup is not the cause.

---

## 2. THE SPECIFIC MESH CHANGE, AND WHY IT SHOULD RECOVER

**Changed:** the block topology and wall-normal grading recipe of the RAE 2822
C-grid, so that **max non-orthogonality ≤ 65°** (a design target below the 70° gate,
giving a warning-band margin per `MESH_STANDARD.md` §3.1), at **every level**, while
preserving geometric similarity of the ladder (the parent's repaired coarse-anchored
similar ladder, `:83-91`).

Concretely, the re-block targets the two regions that generate the >70° faces in a
naive RAE 2822 C-grid:
1. the **trailing-edge / wake junction**, where the C-grid's aft blocks meet at a
   sharp included angle — split the wake into blocks whose face normals stay closer
   to the cell-connection vectors (reduce the corner angle), or transition to a
   partial O-grid wrap around the aerofoil with a matched wake block;
2. the **wall-normal grading**, whose steep first-cell-to-far-field expansion
   (parent ratios 4.4e6–4.7e6, `:87-89`) combines with surface curvature at the
   leading edge to tilt near-wall faces — use a smoother, capped expansion and, where
   needed, `y`-line orthogonalisation near the wall.

**Why it should recover gate B too:** with the non-orthogonal faces below 65°, the
non-orthogonal Laplacian correction is reliable, removing the mechanism the
supervisor's triage identified as consistent with the negative-temperature crash.
This is the counterfactual mesh the parent (`:290-293`) said would be needed to
*demonstrate* causation — running it both fixes the gate and tests that hypothesis.

**Mesh admissibility is verified by `checkMesh` at each level BEFORE any solve** —
an explicit preflight gate. A level whose mesh fails gate A is not solved (this also
closes the parent's §9.2 refuse-never-degrade gap, where the code launched the solver
on a mesh already known to fail gate A).

**Design constraint carried from `:388-391`:** the surface polygon must be sized to
the **finest** level the ladder intends to build — at the parent's fine level the
mesh faceting margin over the polygon floor had fallen to 2.65× (perpendicular
metric) and one further refinement would breach it. The re-block sizes the polygon
sampling accordingly.

---

## 3. THE GATES, AND NO THRESHOLD IS WIDENED

**Admission gate A (mesh) — UNCHANGED:** max non-orthogonality ≤ **70°** and max
skewness ≤ **4**, boundary faces included (`MESH_STANDARD.md` §3.1). The re-block's
≤ 65° is a *design target*, not a relaxed gate — the gate stays at 70°.

**Admission gate B (convergence) — UNCHANGED:** the solver must print its own
convergence statement (`SIMPLE solution converged`); a small residual is not a
substitute (L-14/L-15).

**Grading gates 1–4 — UNCHANGED from the parent (`:216-220`):**

| gate | quantity | threshold (unchanged) |
|---|---|---|
| 1 | Cp RMS, upper / lower | ≤ 0.08 / ≤ 0.04 |
| 2 | shock location (sonic crossing) | ≤ 0.020 chord |
| 3 | CN vs 0.803 | ≤ 5 % |
| 4 | CD vs 0.0168 | ≤ 20 % |
| — | CM vs −0.099 | reported, not gated |

**Not one threshold is widened.** The fix is entirely in the *mesh*; the bars the
solution must clear are held exactly. The parent's frozen prediction 1 (the shock
sits 0.01–0.03 chord downstream of the measured position) **stands as written and is
tested as written** (`:230-234`) — it is not re-registered to fit.

**Two matters the supervisor must rule at the freeze (referred by the parent, and
legal as pre-compute choices in a fresh registration):**
- **P (validation source):** F12's reference is the AFOSR-HTTM/Stanford secondary
  digitisation (flow case 8621); the AGARD AR-138 primary is **not held on this box**
  and cannot be title-page-verified (rule 15) — `:441-458`. Whether a secondary
  transcription can support a P is a `VERIFICATION_CHARTER.md` ruling and must be
  settled before this ladder is graded, not after.
- **Plateau clause + code-verification element:** the parent (`:576-597,405-430`)
  ruled these belong in the *next* pre-registration as pre-compute choices. A
  code-verification (MMS/exact) element is what a future F12 would need to reach the
  HOLDS tier; adding it is the supervisor's scope decision.

---

## 4. GRADING PATH — FIXED AT THE FREEZE, PLANTED-ZERO CONTROL

The grading path (`sdk/workflows/rae2822_case9.py`, `tmr_verification.py`,
`scripts/roache_triple.py`) is fixed at the fresh registration commit and hashed at
check 4. **Two parent defects must be repaired in the grading path before it is
frozen** (both reported-not-repaired in the parent, `:472-560`):
- the frozen document must cite the live grading file by **symbol and blob, never by
  line** (the parent's line citations all went stale when the pre-launch repair moved
  them, `:472-507`);
- `parse_check_mesh` must read `Max aspect ratio` from the **separate v2606 line**
  (the combined-line branch never fires on v2606, `:527-541`) — advisory, but it
  should not silently return `None`.

A **planted-zero control (rule 3)** is mandated on every graded quantity: for the Cp
RMS and force integrals, plant a known perturbation into the read field, read it back
through the same reader, and refuse (exit 2) if unseen — a zero deviation is evidence
only from a reader shown able to see a non-zero. The mesh-quality gate is already
fail-closed (`:523-525`, a `None` counts as a breach) and stays so.

**LANE REPAIR NOTE — grading-path defects (2026-09-07, cfd `lab-lane`; additive,
alters no gate/threshold/cap/label/prediction; subject to the supervisor's
check-1 diff read before any output counts).** Both §4 defects were repaired in
the grading path ahead of the freeze:
- **Aspect-ratio parse bug — FIXED.** `parse_check_mesh` (in
  `sdk/workflows/rae2822_case9.py`, cited **by symbol**) matched the aspect ratio
  only on a *combined* line (`startswith("Max cell openness")` **and**
  `"aspect ratio" in s`), which never fires on v2606 — v2606 prints
  `Max aspect ratio = 805.199 OK.` on its **own** line (real disk evidence in the
  `mesh_audit_2026-08-25` checkMesh logs). The repair widens the branch condition
  to also match a standalone `Max aspect ratio` line; the existing body
  (`split("=")[-1]`) already reads both forms. It is a **single-line condition
  change (zero net lines added)**, so it shifts no downstream line numbers.
  Verified by a planted-value control at
  `verification/runs/F12_runs/mesh_parse_selftest_2026-09-07/selftest_parse_check_mesh.py`
  (repaired reader SEES a planted 805.199; the pre-repair combined-line reader is
  shown BLIND; `mesh_gate` stays fail-closed on the gated quantities).
- **Stale line citation — DIAGNOSED; repaired by content-anchoring here (L-492).**
  The frozen parent `F12_PREREGISTRATION.md` cites this live grading file **by
  line**, and all three resolved lines are now **stale** (verified 2026-09-07):
  `:229`→`rae2822_case9.py:577` (cited as the `rhoSimpleFoam` solver line; line 577
  is a docstring terminator `"""`); `:330`→`:903` (cited as the mesh-stretch
  `build_case`; line 903 is a boundary-condition entry); `:366`→`:930` (cited as
  `timeout: float = 7200.0`; line 930 is `for line in text.splitlines():` inside
  `parse_check_mesh`). The parent is frozen (rule 6) and is **not edited**. This
  successor therefore cites the grading path **by symbol** — `build_case`,
  `run_case`, `parse_check_mesh`, `mesh_gate`, `solver_converged` in
  `sdk/workflows/rae2822_case9.py`; `gci`/`gci_unequal`/`grade_ladder` in
  `scripts/roache_triple.py`; the TMR reference reader in
  `sdk/workflows/tmr_verification.py` — and its **blob sha is pinned at the
  check-4 freeze**, never by line (L-492: a quote fails loudly, a line number
  fails silently).

---

## 5. COST — rule 12 (anchored to the parent's frozen estimates and the C-50 rate)

The parent measured a **rate** on its rung 1 before the crash: **4.8301e−6 s per
cell-iteration** at 1 rank (`:614`, calibration row C-50), which confirmed the
parent's Basis A to +2.7 %. Using that measured rate for a *completing* 6,000-
iteration run at each admissible level:

| level | cells | iters | basis | core-min |
|---|---|---|---|---|
| coarse | ~23,000 | 6,000 | 4.83e−6 s/cell-iter × 1 rank | ~11.1 |
| medium | ~92,000 | 6,000 | same | ~44.4 |
| fine | ~369,000 | 6,000 | same | ~178 |
| meshing (3 × blockMesh+checkMesh) | | | parent 0.191 core-min, ×~1.5 | ~0.3 |
| **estimate total** | | | | **≈ 234 core-min** |
| **HARD CAP** | | | | **360 core-min** (120 per level, the parent's per-rung cap, unchanged) |

The 4.83e−6 rate is **measured** (C-50); the iteration counts assume convergence at
the registered 6,000 (the point of the fix), and ranks may be raised to 4 to cut wall
time with little change in core-min. An overrun of the 360 cap **stops the run**
(rule 12). Dollars: 360 core-min = 6.0 core-h × $0.0513 = **$0.308 — DERIVED, NOT
MEASURED** (reported-by-owner, `COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 ceiling.
Calibration row owed at completion.

---

## 6. WHAT THIS SUCCESSOR CAN AND CANNOT SETTLE

- **Can:** whether an admissible RAE 2822 mesh (≤ 65° non-orthogonality, all levels)
  lets `rhoSimpleFoam` converge and clear gates 1–4; and — as the counterfactual the
  parent lacked — whether the gate-A breach *caused* the negative-temperature crash.
- **Cannot without the supervisor's P and V rulings (§3):** reach the HOLDS tier — a
  passing gate ladder without a code-verification element reaches at most GATE REACHED
  (`:426-430`), and the P source must be ruled admissible before grading.

**Nothing is sent, filed, uploaded, registered or posted (rule 7). Draft handed to
the cfd supervisor for the check-4 freeze and the two referred rulings.**
