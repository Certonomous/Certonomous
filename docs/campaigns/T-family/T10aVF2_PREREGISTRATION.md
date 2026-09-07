# T10a-VF2. Re-registration of the `viewFactorsGen` row-sum gate — repairing two named GATE-DESIGN defects

Predecessor: `T10a-VF` (explicit, for §2ay linkage). This registration is the
active, dated fix-successor to the **T10a-VF** rung `GATE FAIL` (5 PASS / 4 GATE
FAIL — `docs/campaigns/T-family/T10aVF_RESULTS.md` §7, AMENDMENT 1). All four
GATE FAILs are classed **GATE-DESIGN (5), not physics**
(`docs/campaigns/T-family/MATRIX_CONTRIBUTION.md` row 1156). Under
`VERIFICATION_CHARTER.md` §2ay.2(b) this registration makes T10a-VF a fail
**carrying an active fix-successor**; **T10a-VF keeps its verdict (§2an.2) and
stands closed** — this linkage moves no verdict, re-grades nothing in the
predecessor, and does not reopen the predecessor's frozen file.

> ## PARTIAL FREEZE 2026-09-07 by heat-transfer-supervisor — VF-4' + VF-7' FROZEN; VF-3' / VF-6' / the 0.20 admissibility rule DEFERRED. LAUNCH HELD.
> **Authorised by verification's V-121 gate-design ruling** (`7db1df83`): the VF-4'
> control-measured floor `B_ctrl` is ADMISSIBLE/GATED (D389/D393 precedent, NOT a
> widening) under three conditions, all met — independent control channel, frozen
> formula (read not chosen), and two floor-validity guards; VF-7' clean.
> **FROZEN NOW (this commit), grading path pinned (rule 2):** VF-4' Limb A and
> VF-7' and their controls, evaluated by the comparator
> `verification/runs/T-family/T10aVF_runs/analyse_t10avf2.py` git blob
> **`ebe19800f0a338664e74f40a89f9c2f35f0d2e05`** (imports nothing from the
> predecessor `analyse_t10avf.py` blob `6bb155521f8fce95e5fc571ed206e7cf3a297ab1`,
> which is UNTOUCHED; re-implements its readers verbatim as a self-contained unit).
> Pinned frozen constants: `B_ctrl(case) = max|E| over n_ev==0 control patches`;
> `LIMBA_COEFF = 0.30`; `ORDER_GUARD_MIN_P = 1.5`; the afix-bit-identity mechanism-
> leak guard; `VF7_MAX_MOVE_PP = 0.05`. Per V-121 condition (b) the comparator
> PLANTS BOTH floor-validity guards RED/GREEN and the §5 graded-value control;
> supervisor diff-read it AND ran `--selftest` (rc 0: both guards RED/GREEN, an
> INVALID floor forces NOT A RESULT never PASS, blind reader CAUGHT).
> **DEFERRED — NOT FROZEN (V-121):** VF-3', VF-6', and the §2
> signal-to-background **0.20 admissibility rule**. These freeze ONLY after a
> separate pre-registered DRIVEN sweep demonstrates the admissible-level set and
> the VF-3'/VF-6' verdicts are INVARIANT across `[0.05, 0.25]` (the D393
> non-load-bearing standard — an assertion of robustness is not enough). They land
> as a dated addendum and MUST be frozen before the single run computes. The frozen
> comparator above does NOT evaluate VF-3'/VF-6' and contains no 0.20 constant.
> **Cut at BUILD/launch (not at this freeze):** the builder `build_t10avf2.py`,
> the `T10aVF2_runs/` case dirs and their `CASE.json` contract — the cases do not
> yet exist (age guard, rule 4); the builder is diff-read and pinned before the run.
> **LAUNCH HELD** pending Sanaa's capacity decision. Amendments after first compute
> land only as struck/dated addenda that cannot alter a gate, threshold, cap or
> label (rule 2).

Verdict vocabulary fixed by `CLAUDE.md` rule 1:
**PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.**

---

## 0. What is wrong, what is being corrected, and what is NOT

### 0.1 The two named GATE-DESIGN defects this registration repairs

Both are named verbatim in `T10aVF_RESULTS.md` §7 (lines 318, 321) and carried
into `MATRIX_CONTRIBUTION.md` row 1156:

- **Defect A — VF-4 carried no faceting allowance.** VF-4 graded *every* patch
  against `|E - n_ev·e(0.21)| <= 0.30·|E| + 0.002`. For a convex/flat patch
  `n_ev = 0`, so the predicted excess is ~0 and the test reduced to
  `|E| <= 0.002/0.70 ≈ 0.00286` **absolute**. The four failing rows
  (`S1_SPH_L1 inner`, `S1_SPH_L2 inner`, `S2_SHELL_c inner`, `S2_SHELL_c outer`)
  are all near-zero-prediction convex patches whose **converging background
  quadrature error** (T10a separately measured this at −0.538 % on the coarse
  sphere; §4 lines 188-189) is several times 0.00286 at coarse resolution. **The
  gate demanded that a different, already-known, converging error also be small,
  and had no term for it.**
- **Defect B — VF-7 registered the wrong knob.** VF-7 tested whether
  "`GaussQuadTol` and `intTol` cannot reach the coincident-edge term." But
  `intTol` is **not a quadrature tolerance**: `shootRays_CGAL.H:58,61` uses it as
  the fractional **shrink applied to each end of the visibility ray**, to stop a
  ray hitting its own endpoint faces. The `GaussQuadTol` limb passed at
  **0.0008 pp**; the `intTol` limb "failed" at **20.6 pp** — but the 20.6 pp is a
  *ray-visibility collapse* (648 of 1728 faces see nothing at `intTol=1e-4`), a
  **different fragility of the same utility**, not evidence that a quadrature
  tolerance can reach the coincident-edge term. **The gate conflated a quadrature
  knob with a ray-shrink epsilon.**

The predecessor's AMENDMENT 1 (lines 492-498) routed this rung under §2an with an
explicit instruction, which this registration follows to the letter:

> *"The successor's repair is to register better-posed tolerances BEFORE compute
> — separating the `alpha`-dependent term from the converging background — and
> NOT to relax these ones afterwards."*

### 0.2 THE REFERENCE DOES NOT MOVE. This is a correction of a mis-specified instrument, not a widening.

The graded observable is unchanged and needs no reference: for any CLOSED
enclosure of opaque surfaces, `sum_j F_ij = 1` **exactly**, for every emitting
face, at every resolution. `rowSum - 1` is compared to the exact value **1** and
to nothing else. **No band is widened to make a failing number pass.** Each
re-posed gate (§4) is graded against the *correct* quantity — the `alpha`-driven
mechanism separated from the converging quadrature background, and the quadrature
knob (`GaussQuadTol`) separated from the ray-shrink epsilon (`intTol`) — and each
retains a **real falsifier that a genuinely broken value would still trip** (§4a,
the honest-labelling audit). The predecessor's finding — a silent wrong-answer in
`viewFactorsGen`'s 2LI coincident-edge regularisation, closed-form in `alpha`,
`e(alpha) = -(2 ln alpha + 3)/(4π)`, exact at `alpha = exp(-3/2)` — **stands on
its own measurements and is not re-opened.**

### 0.3 What this arm does NOT do (registered in advance)

1. **It does not fix `viewFactorsGen`.** §8 of the predecessor documents a real
   upstream 2LI coincident-edge row-sum defect (max `|qr| = 13.95 W/m² = 3 %` of
   `σT⁴` on a uniform-300 K box, `T10aVF_RESULTS.md:352`). **The re-gate sits
   ATOP that defect; it measures the mechanism correctly, it does not repair the
   utility.** No patched binary is built. `alpha = exp(-3/2)` is applied only as a
   *dictionary value through the shipped code path* — evidence about the
   mechanism, not a verified patch (predecessor §11.4).
2. **It does not re-grade T10a or T10a-VF.** T10a S0/S1 remain `NOT A RESULT`;
   T10a-VF's rung and rows keep their verdicts (§2an.2). This arm produces its own
   verdicts against its own frozen gates and discharges the §2ay flag by
   **lineage**, not by rewriting the predecessor.
3. **It measures no flux, temperature or HTC.** No solver runs. Mesh-side
   preprocessing only (`blockMesh` + `viewFactorsGen`), Charter §2d.
4. **It says nothing about `createViewFactors`** (separate code, no `alpha`,
   different 2AI), nor about `smoothing true` (row-renormalisation hides all of
   it), nor about the agglomeration question (predecessor §5.4 gap — carried
   forward as REPORTED ONLY, still not gated).
5. **SUBMISSIONS PARKED.** The upstream draft
   (`docs/upstream/T10a_viewFactorsGen_rowsum_NOT_FILED.md`) opens `NOT FILED`;
   novelty search still owed (predecessor §11.6). A rung verdict is not a
   clearance to send anything. Filing is Sanaa's call alone (rule 7).

---

## 1. Toolchain (unchanged from the predecessor, re-asserted)

OpenFOAM ESI **v2606**, `/usr/lib/openfoam/openfoam2606`,
`Build: _481094f-20260618`, `Arch: LSB;label=32;scalar=64`. Utility under study:
**`viewFactorsGen`** (source present, 1323 lines). Key facts from the source,
cited not re-derived:

| fact | source line (predecessor-verified) |
| --- | --- |
| a pair goes to 2LI when `dist <= distTol` | `viewFactorsGen.C:969` |
| the coincident-edge term is forced to quadrature order 0, *regardless of Gauss order* | `viewFactorsGen.C:1054-1058` |
| the log singularity is evaluated by `r -> alpha·\|s_i\|` | `viewFactorsGen.C:390-394` |
| 2LI branch normalisation `1/(4π A_i)` | `viewFactorsGen.C:1096-1097` |
| `GaussQuadTol` (default 0.01) is the 2LI Gauss-order acceptance tolerance | `viewFactorsGen.C:476-486` |
| **`intTol` (default 1e-2) is the ray-shrink epsilon, NOT a quadrature tolerance** | `shootRays_CGAL.H:58,61` |
| `writeViewFactorMatrix` writes the utility's own per-face row-sum field to `0/viewFactorField` | `viewFactorsGen.C:1200-1243` |

The closed-form defect size, on record and re-used here without re-derivation:

> **`e(alpha) = -(2 ln alpha + 3)/(4π)`**, added to `F_ij` once per
> mutually-visible edge-sharing neighbour. `e(0.21) = +0.0096524`,
> `e(exp(-3/2)) = 0`. A concave face sees all four edge neighbours
> (`n_ev = 4 → +3.86 %`); a convex/flat face sees none (`n_ev = 0`).

---

## 2. The physical basis of the faceting allowance — DERIVED, not calibrated

This is the load-bearing derivation for **Defect A**. It rests on facts the
predecessor already established and froze; it is **not** fitted to the four VF-4
failures.

**Step 1 — a closed FLAT-facet enclosure has an EXACT unit row sum.**
Predecessor PC-4 (`T10aVF_PREREGISTRATION.md:124-126`,
`T10aVF_RESULTS.md:342`): "A closed enclosure of *flat* facets still has exact
row sums of 1." Therefore the geometric faceting of a curved surface **does not
by itself break the row-sum identity** — the identity is exact on the discretised
(flat-facet) enclosure, *provided each pair integral is evaluated exactly.*

**Step 2 — the convex-patch residual is therefore PURE NON-SINGULAR QUADRATURE
error, carrying NO `alpha` term.** Since Step 1 removes the geometry as a source,
the entire convex-patch residual `E_convex(h)` is the numerical error of the
2AI/2LI branches evaluating *well-separated, smooth* pairs (a convex face's edge
neighbours are not self-visible, `n_ev = 0`; the faces it does see are across the
cavity, all far). It contains no coincident-edge term. **This is independently
proven on record:** every failing convex row in VF-4 is *bit-identical between
the `alpha=0.21` case and its `alpha=exp(-3/2)` twin* (`T10aVF_RESULTS.md:191`).
So `E_convex` is provably `alpha`-independent — the mechanism does not touch it.

**Step 3 — the non-singular quadrature error scales as `O(h²)`.** The 2AI
one-point double-area rule and the 2LI Gauss-order loop are, for well-separated
smooth pairs, midpoint/low-order-Gauss quadratures of a smooth kernel. The
per-pair leading error is `O(h²)` in the facet size; summed into a row sum, the
leading near-neighbour errors cancel by the local symmetry of a convex patch,
leaving a residual `B(h) = O(h²)`, where

> **`h` ≡ the characteristic facet angular size** on the patch, taken as
> `h = 1/sqrt(N_patch)` (mean facet linear size ÷ enclosure/curvature scale),
> `N_patch` = the patch face count.

The **order** `p = 2` is read from the quadrature rule, **not** from any measured
convergence. (For the record — not used to set the floor — the predecessor's
convex control fell as `O(h^1.6..1.9)`, `T10aVF_RESULTS.md:94`, consistent with
`p ≈ 2` under near-neighbour cancellation on a non-doubling mesh family.)

**Step 4 — the operative floor is a same-case, same-resolution CONVEX CONTROL,
armed in advance and convergence-gated.** The absolute magnitude of `B(h)`
depends on an `O(1)` geometric constant `C_q` set by the kernel curvature, which
cannot be pinned to a number **without either an independent analytic bound
(geometry-specific and heavy) or a fit to the data (forbidden, `CLAUDE.md`
rule 2 / §2at).** Rather than pick `C_q` by hand, the floor is **measured by the
utility itself on the convex/flat (`n_ev = 0`) patches of the SAME case at the
SAME resolution** — the utility's own quadrature-error channel, matched in
geometry and `h`, and *provably mechanism-free by Step 2*:

> **`B_ctrl(case) ≡ max |E|` over that case's `n_ev = 0` (convex/flat) patches.**

This is a **control channel armed before compute**, not a calibration to the VF-4
failure: it reads a *different* set of patches (the controls), it is fixed by the
registration before any successor case exists, and it is *guarded* so it cannot
become an unbounded escape hatch — a convex control is admissible as a floor only
if **(i)** it converges at order `p ≥ 1.5` across the mesh family (falls by
`≥ 2^1.5 = 2.83×` per `h`-halving equivalent — the `O(h²)` prediction of Step 3
with margin) **and (ii)** it is bit-identical between the `alpha` case and its
`afix` twin (Step 2). **A convex control that fails either guard is INVALID; any
gate that depends on it is then `NOT A RESULT`, never `PASS`** — the instrument
may not certify a floor it cannot show converging and mechanism-free.

**Honest label (the derivation's own limit).** The floor's *scaling and order*
are derived from the quadrature rule (Steps 1–3); the floor's *absolute size* is
**measured** by an advance-armed, mechanism-free control (Step 4), not
analytically pinned. This is stated so the supervisor judges it as what it is: a
principled control-derived allowance, not a hand-tuned constant and not a fit to
the observed failure. **§4a self-audits each re-posed gate against the
pass-fitting line.**

**Signal-to-background admissibility (used by VF-3', VF-6').** A mesh level can
measure the `alpha`-mechanism's `h`-independence only where the mechanism signal
dominates the background. Register, before compute:

> **A mesh level is ADMISSIBLE for a mechanism gate iff
> `B_ctrl(case) <= 0.20 · |n_ev · e(0.21)|` on that case** (signal ≥ 5× background).

`0.20` is a round order-of-magnitude signal-to-background floor, **not** chosen to
exclude a specific level: any value in `[0.05, 0.25]` gives the same partition of
the predecessor's family (the `N=8` `L1` level sat at background/signal `≈ 0.31`;
`L2–L4` sat at `≈ 0.02–0.05`). The criterion is a measurement-design rule decided
in advance and applied to the successor's *own* fresh controls at grade time.

---

## 3. What is built and run (successor run tree)

Run tree: **`verification/runs/T-family/T10aVF2_runs/`**. Mesh-side preprocessing
only. **No case in this tree exists at freeze; every case is built after the
freeze commit** (age guard, `CLAUDE.md` rule 4). Nothing in
`T10aVF_runs/` or `T10a_runs/` is written to — both are read-only input.

Same clean-room geometry family as the predecessor (`blockMesh` only, no
`snappyHexMesh`), so every case is reproducible from small text files:

| sweep | cases | purpose |
| --- | --- | --- |
| **S1 — SPH mesh family** | `SPH` at 768/1728/3072/4800 faces + `_afix` twin of each (8) | VF-1 (carried), VF-2 (carried), **VF-3'**, **VF-4'**, **VF-6'** |
| **S2 — geometry/convexity** | `BOX`, `SHELL`, `BALL`, `CYL` at 2 res + `_afix` at the finer (12) | **VF-4'** convexity law, **VF-6'** |
| **S3 — generator knobs** (fixed `SPH` 1728) | `alpha ∈ {0.10,0.15,0.20,0.21,0.22,exp(-3/2),0.25,0.30}` (8); `GaussQuadTol ∈ {0.01,0.001,1e-6}` (3); `distTol ∈ {1,4,8,100}` (4); `intTol ∈ {0.01,1e-4}` (2); agglom off/on | VF-5 (carried), **VF-7'**, VF-8 (carried), VF-9 (report), **VF-11** (report) |

`L1` (`N=8`, 768 faces) is run and reported but is **inadmissible in advance**
for the mechanism gates by the §2 signal-to-background rule; it is retained
because VF-1 (non-convergence over the full 6.25× face-count range) is scored on
the whole family.

---

## 4. Registered predictions and gates

Symbols as the predecessor: `E` = patch-mean `rowSum - 1`; `n_ev` = patch-mean
mutually-visible edge-sharing neighbour count; `e(a) = -(2 ln a + 3)/(4π)`;
`B_ctrl` and admissibility per §2. **Gates carried UNCHANGED** from the
predecessor (they passed; a passing gate is never touched — §2at): **VF-1, VF-2,
VF-5, VF-8, VF-10.** Their thresholds are re-asserted verbatim from
`T10aVF_PREREGISTRATION.md` §4 and are not restated here. **Re-posed gates:**

| gate | what it now tests | PASS threshold | falsifier (GATE FAIL) |
| --- | --- | --- | --- |
| **VF-3'** per-pair constant | `E/n_ev` is a constant of `alpha`, not of `h`, **measured only where the signal dominates** | (a) `E/n_ev ∈ [0.0080, 0.0130]` on every concave patch of S1–S2 at `alpha=0.21`; **and** (b) spread of `E/n_ev` across the **ADMISSIBLE** `SPH` levels `<= 15 %` | (a) outside the interval on any patch; **or** (b) admissible-level spread `> 15 %` |
| **VF-4'** convexity law, correctly posed | the law `E = n_ev·e(alpha) + B(h)` holds patch by patch, with the background separated | **Limb A (concave patches):** `\|E - n_ev·e(0.21)\| <= 0.30·\|n_ev·e(0.21)\| + B_ctrl(case)` for every concave patch of S1–S2. **Limb B (convex/flat patches):** every `n_ev=0` patch is (i) **bit-identical** between its `alpha=0.21` case and `_afix` twin, and (ii) its `E` participates in a mesh-family convergence at order `p >= 1.5` | Limb A: any concave patch outside. Limb B: any convex patch **not** `afix`-bit-identical (mechanism leaked onto a convex patch), or the convex background **not** converging at `p >= 1.5` |
| **VF-6'** `alpha`-fix leaves exactly the background | setting `alpha = exp(-3/2)` removes **exactly** the mechanism, leaving the converging background | on every **ADMISSIBLE, UN-AGGLOMERATED** case: all patch means `\|E_afix - B_ctrl(case)\| <= max(0.30·B_ctrl(case), 0.003)` | any admissible un-agglomerated patch mean outside |
| **VF-7'** quadrature tolerance inert | the **quadrature** tolerance `GaussQuadTol` cannot reach the order-0-forced coincident-edge term | `GaussQuadTol` 0.01→0.001→1e-6 moves the `SPH` outer `E` by `<= 0.05 pp` | `> 0.05 pp` |
| **VF-9** agglomeration | (carried) — **REPORTED ONLY, no gate** (predecessor §5.4 gap: a non-degenerate level, `nFacesInCoarsestLevel` in the hundreds, is run and reported; no verdict) | — | — |
| **VF-11** ray-shrink fragility | **NEW, REPORTED ONLY, no gate.** `intTol` is a ray-shrink epsilon; at `intTol=1e-4` rays are too short to escape their own endpoint faces and faces come back seeing nothing. Recorded, with the count of blind faces and the collapsed inner-patch mean. **Explicitly NOT a quadrature-tolerance test.** | — | — |

**Quantitative predictions written down now (carried from the predecessor,
re-asserted, to be scored later):** `SPH outer / BALL outer` `n_ev=4 → E ≈ +3.86 %`;
`CYL side` `n_ev≈2 → E ≈ +1.93 %`; convex/flat patches `E → B(h)`, converging
`O(h²)` with patch max pinned at `1..2·e(0.21)` on box-edge faces.

### 4a. Principled-vs-pass-fitting self-audit (the honest-labelling test)

For each re-posed gate: does the previously-failing number now pass **because it
is graded against the correct quantity**, and would a **genuinely broken value
still trip the falsifier**?

| gate | why the old fail now passes | the falsifier that still bites |
| --- | --- | --- |
| **VF-3'** | L1 (`N=8`) is excluded **in advance** by a signal-to-background rule (background 31 % of signal), not post-hoc; the mechanism's `h`-independence is measured only where it is measurable | if `E/n_ev` genuinely drifted with `h` on the admissible levels (mechanism not `h`-independent), spread `> 15 %` → GATE FAIL |
| **VF-4'** | convex near-zero patches are graded against the **converging background** (their own mechanism-free control), not against a 0.002 absolute floor that had no term for it | Limb B trips if the mechanism ever leaks onto a convex patch (afix non-identity) or the background fails to converge; Limb A trips if a concave patch departs from `n_ev·e(alpha)` by more than 30 % + background |
| **VF-6'** | the residual after the fix is graded against the background it should leave (`B_ctrl`), not against 0 — the fix removes the mechanism, it cannot remove the converging quadrature error | trips if the fix leaves **more** than the background behind (fix incomplete) on any admissible un-agglomerated case |
| **VF-7'** | the **correct** knob (`GaussQuadTol`) is tested; `intTol`'s ray collapse is moved to REPORTED-ONLY VF-11 where it belongs | trips if `GaussQuadTol` moves `E` by `> 0.05 pp` — i.e. if the term is **not** in fact order-0-forced |

**Flag for the supervisor's judgment (not hidden).** The one element that is a
registered *judgment call* rather than a derivation is the **signal-to-background
constant `0.20`** in the §2 admissibility rule (VF-3', VF-6'). I argue it is
principled (a round 5×-signal floor, robust across `[0.05, 0.25]`, not
knife-edged to L1's 0.31). **If the supervisor judges it pass-fitting, the
correct action is to leave VF-3'/VF-6' FLAGGED and NOT widened** — the derivation
above (§2 Step 4, the convex-control floor and its convergence guard) stands
independently and is the load-bearing repair for VF-4'; VF-3'/VF-6' can be
deferred without re-opening VF-4'.

---

## 5. Planted-zero control (rule 3) — NEW; the predecessor comparator had none

The predecessor's `analyse_t10avf.py` is a read-only streamer with **no plant**:
it was never shown able to see a non-unit row sum before it reported an in-band
one. This registration **requires a plant** in the successor comparator, because
every gate here turns on a small residual `E` and a reader that cannot see a
*non-zero* residual is not evidence (rule 3; `a-zero-needs-a-live-planted-control`).

Registered plant, to be implemented in the successor comparator (§6) and driven
in **every grading run**, refusing (**exit 2**) if the reader cannot see it:

- **PLANT_ROWSUM = 3.21e-2.** The comparator copies `constant/F` to a scratch
  path under the case (never the real matrix), injects `+PLANT_ROWSUM` into one
  designated face's first `F` entry, streams the perturbed copy through the
  **same** row-sum path used for grading, and asserts the designated face's
  reported `rowSum` rose by `PLANT_ROWSUM` to within `1e-9`. **If the perturbed
  row sum is not seen, the comparator refuses and grades nothing** — a zero
  residual from a reader not shown able to see `3.21e-2` is not evidence.
- **Non-vacuity twin (matches §2ay.5's own two-limb discipline):** the same run
  reads the *un*-perturbed copy and asserts the designated row is **at its
  measured value** (the plant left the real matrix untouched). RED (perturbed
  seen) then GREEN (unperturbed clean), in one run, before any `E` is believed.

The plant is **read back from disk** (the scratch copy), never from an in-memory
value, so it exercises the full parse path the grade uses.

---

## 6. Comparator and grading-path freeze plan (pins cut at freeze)

Frozen together with this file at the pre-registration commit, **before any
successor case is built**; the grading path is fixed at that commit and the
frozen file is verified to be the file that ran by hashing it against the
committed blob (rule 2; `scripts/check_comparator_freeze.py`):

| path | role | status at draft |
| --- | --- | --- |
| `docs/campaigns/T-family/T10aVF2_PREREGISTRATION.md` | this file | drafted (hashed by the commit) |
| `verification/runs/T-family/T10aVF2_runs/build_t10avf2.py` | case builder (may reuse predecessor `build_t10avf.py` logic verbatim) | **TO BE WRITTEN before freeze** |
| `verification/runs/T-family/T10aVF2_runs/run_t10avf2.sh` | `blockMesh` + `viewFactorsGen` driver (non-fatal bashrc source, no `maxDynListLength` — predecessor's two disclosed plumbing fixes folded in from the start) | **TO BE WRITTEN before freeze** |
| `verification/runs/T-family/T10aVF2_runs/analyse_t10avf2.py` | **NEW comparator**: predecessor `analyse_t10avf.py` streaming logic **plus** the §5 plant, `B_ctrl`, the §2 admissibility flag, and the re-posed VF-3'/VF-4'/VF-6'/VF-7' gate evaluations | **TO BE WRITTEN before freeze** |
| `verification/runs/T-family/T10aVF2_runs/grade_t10avf2.py` | gate scorer emitting a rung verdict from §4 rows and §4a's falsifiers | **TO BE WRITTEN before freeze** |

**Pins cut at freeze:** (1) the gate set, thresholds, `e(alpha)` law, the §2
floor construction, the §2 admissibility constant `0.20`, the §5 plant value, and
the labels — all committed before compute; after first compute they close and
change only as dated struck-through addenda that cannot alter a gate, threshold,
cap or label (§2b/§2d). (2) The grading path is the committed blobs of the two
scoring scripts; the comparator hashes itself against its committed blob at run
time and refuses on mismatch. **This lane writes none of the scripts in this
zero-compute draft; it registers their contract so the supervisor can diff-read
them against this file before freeze.**

---

## 7. Cost — core-minutes, and the honest cost basis

`viewFactorsGen` scales `O(n²)` in radiative faces. Anchor, from the predecessor
actuals (`T10aVF_RESULTS.md` §9): the 34-case predecessor sweep spent **4.20
core-min** of `blockMesh`+`viewFactorsGen` (measured, sum of per-case
`STATUS wall_s`) over `sum n² ≈ 1.48e8`, i.e. **≈ 2.84e-8 core-min per `n²`**
(the predecessor's pre-registration used 2.35e-8 from T10a; the successor uses the
predecessor's *measured* rate, which is the better estimate — this is the rule-12
estimate-vs-actual calibration feeding forward).

| item | `sum n²` | core-min |
| --- | ---: | ---: |
| S1 (8 cases) | 7.2e7 | ~2.0 |
| S2 (12 cases) | 3.4e7 | ~1.0 |
| S3 (~19 cases incl. agglom + intTol report) | ~4.5e7 | ~1.3 |
| `blockMesh` + `checkMesh`, ~39 cases | — | ~2.3 |
| analysis Python (comparator + plant + grade over ~39 cases) | — | ~11.0 |
| **registered total** | ~1.5e8 | **~17.6 core-min** |
| **registered ceiling incl. 3× contingency and reruns** | | **~53 core-min** |

**Arm cap: 1.00 USD** (as the predecessor). Registered estimate **~17.6
core-min**; derived cost **≈ $0.015** at **$0.0513/core-h**.

> **cost_basis: rate $0.0513/core-h is OWNER-STATED (`CLAUDE.md` rule 12;
> `Xiao2016_EnKF/PREREGISTRATION.md:197`); the box cannot read its own billing
> (`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar figure here is DERIVED at that
> rate, REPORTED-BY-OWNER, NEVER measured. Core-minutes are the measured unit and
> come from per-case `STATUS wall_s` at grade time.** An overrun **stops the run**
> (rule 12); the cut order is the predecessor's — drop `S1_SPH_L4` and its twin
> first (the single most expensive pair), then `S2_SHELL_f` and its twin, then the
> `distTol=100`/`intTol` cases. No cut touches a flow result: **no solver runs in
> this arm.** Under $25 pre-authorised (2026-08-18 standing authorization); this
> is ~0.06 % of that per-run ceiling.

At every process completion (rung graded), rule 12's estimate-vs-actual
calibration row lands in `docs/COST_CALIBRATION.md` (actual/predicted ratio, gap
attribution, waste named separately) — the completion report is incomplete
without it.

---

## 8. Concurrency and safety

At most 2 cores, serial utilities, `MAXJOBS=2` — the box is shared; check
before launch (`git log --since`, run-dir mtimes, docket, then a process sweep;
fleet agents are invisible to `pgrep`). No case in this tree is touched by any
other lane; the predecessor tree and the T10a tree are read-only input.

---

## 9. Deliverables

1. `docs/campaigns/T-family/T10aVF2_RESULTS.md` — the re-posed gate table scored,
   the rung verdict, actual-vs-registered cost, and a `Predecessor: T10a-VF` line
   for §2ay lineage; **it discharges the T10a-VF §2ay flag by lineage iff it
   lands PASS on the re-posed gates** (§2ay.2(b) terminal form).
2. The four frozen scripts under `verification/runs/T-family/T10aVF2_runs/`.
3. A `docs/COST_CALIBRATION.md` row at completion (rule 12).

---

*Pre-registration DRAFT written by a heat-transfer `lab-lane`, 2026-09-07,
zero-compute, before any successor case was built, meshed or run. NOT FROZEN, NOT
LAUNCHED, NOT COMMITTED — the supervisor freezes after a personal diff-read of
this file and every comparator it names.*
