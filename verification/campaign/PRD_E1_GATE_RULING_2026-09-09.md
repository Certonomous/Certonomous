# PRD-E1 — PRE-COMPUTE GATE RULING (verification)

**Author:** verification-supervisor. **Date:** 2026-09-09. **Authority:** V&V
pre-compute gate audit (VERIFICATION_CHARTER §2, §2b, §2e, §2bb, §2bc; rule 5;
GCI/Roache; the reference-tier standard V-140). **Scope self-test (§2am /
ESCALATION):** this is an APPLICATION of standing law to a NEW EXACT-tier gate —
it sets no *new* standard, retires/widens no *existing* threshold, and performs
no cross-family arbitration → **NO Sanaa escalation**; the chief relays to
heat-transfer, whose freeze this authorises. Precedent: V-121 (T10aVF2), V-131
(T4f), V-135 (D6RF10). **Cost of this ruling: 0 solver core-min, $0.00** (read +
reasoning; no compute).

Target of the ruling: `docs/campaigns/T-family/PRD_E1_PREREGISTRATION_DRAFT.md`
(heat-transfer lane draft, 2026-09-09), Navier-spine **Case 3** EXACT rung.

---

## 0 — PHYSICS INDEPENDENTLY RE-DERIVED (my §3 big-claim check)

Every frozen physical figure in the draft was re-derived by me from ε=0.40,
d_p=0.003 m, ρ=1.2, μ=1.8e-5, L_core=0.10 m and **reproduces exactly**:

- Ergun viscous/inertial per-length: A = 150·μ(1−ε)²/(ε³d_p²) = **1687.5**;
  B = 1.75·ρ(1−ε)/(ε³d_p) = **6562.5**.
- OpenFOAM-fed: d = 150(1−ε)²/(ε³d_p²) = **9.375e7 1/m²**;
  f = 3.5·(1−ε)/(ε³d_p) = **10937.5 1/m**; and **½ρf = 0.5·1.2·10937.5 = 6562.5 =
  B** ✓. The **3.5 = 2×1.75** exactly undoes OpenFOAM's internal `forchCoeff =
  0.5*fXYZ` (½ρ) factor — LOAD-BEARING and correct.
- Δp(U_s) = 168.75·U_s + 656.25·U_s²: **83.20 / 248.44 / 825.00 / 2962.50 /
  11175.00 Pa** at U_s = 0.25 / 0.50 / 1.00 / 2.00 / 4.00 — all five match; viscous
  fraction 50.7 % → 6.0 % (both terms genuinely exercised).

**CAVEAT (deferred to the freeze):** the OpenFOAM-source ½ρ derivation
(§2.3, v2606) is cited by the lane as verified but the comparator/coefficient
scripts are **not yet authored**. The ½ρ factor and the kinematic→Pa conversion
(×ρ) baked into those scripts get my §3 **check-1 diff-read before any graded
number is believed**. This ruling authorises the gate DESIGN, not un-read code.

---

## 1 — THE BAND (Q1) — RULED

### 1.1 Per-U_s band at the finest level: **±3 % relative on Δp — ADMISSIBLE.**
This is an EXACT self-consistency gate (the CFD must reproduce the analytic law
fed into its own sink), so the band is tied to discretization + modeling error,
not to a free reference value. The draft's error budget (L3 discretization
≲1–2 % via GCI@Fs=1.25; core-face velocity non-uniformity ≲1 %; plane averaging
≲0.5 %; quadrature ≈2–2.5 %) supports ±3 % as **tight with modest margin**. It is
in the **anti-gaming-safe direction** (tight, not loose): there is no free answer
to fit — the target is the analytic law — and a looser band is the only gameable
direction, which this is not. **APPROVED.**

### 1.2 The `band > GCI` constraint (rule 5) — CONFIRMED and STRENGTHENED.
Rule 5 requires the band to exceed the reported GCI. GCI captures **only
discretization error**; the ±3 % band must also cover the non-grid budget
(velocity non-uniformity, plane placement). Therefore I add a pre-asymptotic
guard so the gate cannot silently degrade into a mere grid-convergence check:

> **If the reported L3 GCI (Fs=1.25) for any U_s is ≥ 2.0 %** (i.e.
> discretization alone consumes ≥ two-thirds of the ±3 % band, leaving < ~1.5 %
> quadrature headroom for the non-grid budget), **that U_s is treated as
> PRE-ASYMPTOTIC**: run the already-budgeted **L4** and re-form the triple at
> (L2, L3, L4) before issuing PASS / GATE FAIL. Do not grade a band dominated by
> discretization.

### 1.3 The ±1.5 % asymptotic sub-check — ENDORSED and ELEVATED to a BINDING gate `G-ASYMP`.
For an EXACT-tier gate the grid-independent limit is precisely what "reproduces
the law" means, so the Richardson-extrapolated Δp vs Ergun is the **primary
self-consistency discriminator**, not a decoration. **±1.5 % ADMISSIBLE** (tighter
than the per-level band → anti-gaming-safe). Quote the extrapolated value + GCI
**only on a MONOTONE CONVERGING triple** (rule 5); never off a non-monotone one.

**Meaning of a G-ASYMP miss (recorded so the label is honest):** a clean
CONVERGING triple whose extrapolated Δp lands in ±3 % per-level but OUTSIDE
±1.5 % asymptotic is a **real modeling-consistency signal** (core-face velocity
non-uniformity, or the ρ / superficial-velocity handling in
`explicitPorositySource`), **not by itself a numerics bug**. Its verdict is
**GATE FAIL naming the mechanism**, and under §2bc that is a fixable-model/setup
question → **NEEDS-SUCCESSOR (non-terminal)** unless the model/setup ladder is
exhausted; it is NOT an admissible terminal fail on first sight.

### 1.4 Gate hierarchy (frozen ordering).
Per rule 5: (1) any level not iteratively converged / not plateaued → NOT A
RESULT; (2) triple not CONVERGING (DIVERGENT/STAGNANT/OSCILLATORY/EXACT) → NOT A
RESULT, both triples + orders printed; (3) CONVERGING → **G-ERGUN** (per-level Δp
in ±3 %, band > GCI, §1.2 guard) **and G-ASYMP** (extrapolated in ±1.5 %) → PASS
only if both hold, else GATE FAIL with the failing gate + mechanism named. GCI
always printed. A PASS at all five U_s is the credential.

---

## 2 — CELIK/ROACHE Fs = 1.25 (Q2) — CONFIRMED (standing standard, not a choice).
Rule 5 fixes GCI at **Fs = 1.25**. The draft uses it throughout. Fs = 1.25 is the
correct factor for a **≥3-grid study with an OBSERVED order p** (which this is: a
genuine 3-level triple at r = 2, uniform in all directions). Conditions I pin:
constant refinement ratio r = 2 (satisfied); observed order p reported and, for
GCI to be quoted, the triple **monotone**; P-GRID's expected p ∈ [~1.5, 2.5] for a
2nd-order scheme is reasonable — **p outside [1, ~2.5] or a non-monotone triple →
NOT A RESULT and run L4**, never a GCI quoted off it. No deviation from the
standard is requested or granted.

---

## 3 — LADDER SIZE (Q3) — RULED: **FULL 15-solve (5 U_s × 3 levels). Lean 7 REJECTED.**
Rule 5 requires a **CONVERGING Roache triple per gated quantity**; the gated
quantity is **Δp at each of the 5 registered U_s**. The lean-7 design
(anchor triple at one U_s + L3-only curve) yields a triple at ONE U_s only; the
other four points are single-grid values with **no triple → NOT A RESULT** for a
grid-gated quantity — they cannot earn PASS / GATE FAIL. Worse, the lean design
leaves the **inertial-dominated end (U_s = 2, 4; viscous fraction 11 %, 6 %)**
ungraded — exactly the regime where the **½ρ Forchheimer factor** (§2.3, and
loss-mode (a): "the single most likely silent error") dominates. The lean design
under-tests the load-bearing physics. The cost delta is negligible: full ≈ 4160
core-min ≈ $3.6 (DERIVED) vs lean ~half; **both far under the $25
pre-authorisation** — this is a V&V-sufficiency call, not a spend ruling. **Run
the full ladder.**

---

## 4 — CONDITIONS ATTACHED (the freeze may not proceed until all hold)

1. **§2bb pre-flight PASS** (`check_ladder_preflight.py`-class): deadline sizing
   (L3 ~40 min projected ≤ frozen deadline / 1.25) + each DISTINCT solver path run
   past decompose+first-solve; `fvOptions` parses and the DarcyForchheimer
   coefficients **read back == the §2.3 frozen values**; the sink is exercised
   ACTIVE (D,f set → Δp>0) and INERT (D=f=0 → ~0). **The incompressible-
   `explicitPorositySource` ρ handling + kinematic→Pa conversion (§2.1/§2.4) MUST
   be MEASURED against the written fields and resolved BEFORE freeze** — the Pa
   conversion is load-bearing to every graded number.
2. **Planted-zero controls (§6, rule 3):** all three fire — the D=f=0 / D,f-set
   visibility pair AND the `PLANT_DP = 3.210 Pa` read-back-and-refuse. I
   drive/confirm the plant at freeze; a perfect zero from any reader is REFUSED.
3. **§3 check-1 diff-read (mine, non-delegable):** every measurement script — the
   coefficient generator (the ½ρ / 3.5 factor), the Δp reader (×ρ Pa conversion,
   plane placement x=0.200/0.300 m), the y+ reader, the triple/GCI grader —
   read as a diff before any graded number is believed. This is where I
   re-verify the v2606 ½ρ source claim against the actual authored code.
4. **§2ba dual-mechanism run:** a live monitor AND a detached (PPID=1) grader
   pinned to the FROZEN comparator (rule 2 disk==pin re-hash), survives fleet
   death; neither substitutes.
5. **Completion (rule 4 + clause-5 + age guard):** field set **{U, p, k, omega,
   nut, phi}** (incompressible isothermal — NOT the thermal {T, p_rgh, alphat});
   `phi` included per the 2026-09-06 addition; every field NEWER than the case's
   own `0/`; last time == endTime; **clause-5 `ExecutionTime == round(endTime/
   deltaT)` — this is FIXED-deltaT (steady simpleFoam, deltaT=1 → == endTime),
   IN clause-5 scope (V-136), NOT the adaptive-dt path.** The `mark_done`-class
   instrument must be given this field list explicitly (answers §11 Q6).
6. **y+ gate (Q4):** continuous/Menter treatment with **y+ ≤ 200 upper bound,
   consistent recipe across levels** — ADMISSIBLE (not y+≤1) BECAUSE the gated Δp
   is dominated by the volumetric D/f sink, not wall shear; report max y+ per
   patch per level; the cross-check reader plants→reads-back→refuses (rule 3).
7. **Deliberate exclusions — CONFIRMED CORRECT (endorsed):** NO Spalart–Rumsey
   farfield and NO Barlow–Rae–Pope blockage — this is INTERNAL duct flow with an
   explicit inlet/outlet and a full-section core; all refs are per-frontal-area /
   superficial. Consistent with the V-140 Navier-spine ruling (cases 2/3/6
   internal → neither applies).
8. **§2bc:** OpenFOAM CAN do this (DarcyForchheimer is a shipped model; the §2bb
   active/inert exercise IS the capability proof). No `BLOCKED` verdict is
   admissible without measured exhaustion evidence. A terminal GATE FAIL / NOT A
   RESULT needs the §2bc exhaustion ladder (`check_exhaustion_evidence.py`).

---

## 5 — FILING / RUNG-ID (Q2 of the draft) — RULED against the chief's navier_class structure

- **Canonical home:** the draft currently sits at `docs/campaigns/T-family/`. The
  chief-ruled Navier structure is **`docs/campaigns/navier_class/<CASE>/`**, so on
  freeze this record moves to **`docs/campaigns/navier_class/PRD/`** (with
  `cases/navier_class/PRD/`, `verification/runs/navier_class/PRD/`, and the frozen
  prereg in `verification/campaign/`). The draft's suggested
  `docs/campaigns/porous-radiator-duct/` home is SUPERSEDED by the chief's ruling.
- **Rung id:** stays **`PRD-E1`** (Case = `PRD`, rung suffix `E1` = EXACT-tier
  rung 1). The draft's alternative `N3E1` is SUPERSEDED — the chief ruled the
  case-id vocabulary (SUBOFF / MRF_PUMP / PRD / SUP_BOOSTER / ORBITER_HB2 /
  SCRUBBER / DRIVAER + E1/M1).
- **check_filing registration:** R7 (`docs/campaigns/<FAMILY>/<FILE>`, depth 4)
  is being extended to also govern `docs/campaigns/navier_class/<CASE>/<FILE>`
  (depth 5), SCOPED to `navier_class` so the ~30 existing ungoverned depth-5
  demo/figures files are untouched. `PRD_E1_PREREGISTRATION.md` matches
  `CAMPAIGN_RECORD_MD`; helper code stays lower_snake. `verification/campaign/`
  prereg naming remains ungoverned by check_filing (unchanged — not widened).

---

## 6 — WHAT THIS RULING DOES NOT DO
It does not freeze anything, author any script, or move any verdict. The freeze,
the scripts, the §2bb pre-flight run, the final mesh decision and the launch are
heat-transfer's, subject to the §4 conditions and my §3 check-1 diff-read of the
measurement scripts when they land.

*— verification-supervisor, 2026-09-09.*
