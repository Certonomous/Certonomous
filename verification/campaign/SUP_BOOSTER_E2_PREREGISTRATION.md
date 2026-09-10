# SUP_BOOSTER — Case-3 EXACT-tier (E2) pre-registration — Taylor-Maccoll cone, §2bc successor to E1

**STATUS: DRAFT / UNFROZEN.** Prepared by a cfd lab-lane. **Not frozen**: the freeze
(commit + blob-sha pin) and the graded launch are the **cfd-supervisor's check-1 (new grader
diff) + check-4** and are not taken here.

**§2bc fix-until-runs successor to SUP_BOOSTER E1** (E1 RUN VERDICT `NOT A RESULT`, verdict
record `SUP_BOOSTER_E1_VERDICT.md`, frozen prereg `c8510ff7`). This is a **diagnosed,
pre-registered, costed** successor — not a blind retry, and not a silent edit to frozen E1
(rule 6). E1's physics was corroborated (shock at r=0.40 vs TM 0.401; cone-surface Cp within
0.13–0.21% of TM at coarse/medium); the two failures were **instrument/mesh robustness**, and
E2 fixes exactly those two, changing nothing else.

## 1. What E1 diagnosed, and the two E2 changes

- **Cause A (Gate C2 refuse):** E1's shock locator used max |Δρ/Δr|; the aggressive radial
  grading (`GR_RADIAL=12`) made near-wall cells so thin that small compression-region wiggles
  gave spurious large |Δρ/Δr| at r≈0.2–0.27, so the fitted shock line was not apex-anchored
  and the grader refused.
  **E2 change 1 — robust shock locator (freestream-density-boundary crossing).**
  `grade_sup_booster_e2.py::read_shock_angle` now scans each radial column **from the outside
  (undisturbed freestream) inward** and takes the shock as the outermost radius where density
  first exceeds the **per-station local freestream** (the outermost cell) by `SHOCK_EPS=0.03`.
  It never reaches the clustered near-wall region, so near-wall wiggles cannot be mistaken for
  the shock. **Proven on all three E1 graded solutions: β = 33.695° / 33.994° / 33.848°**
  (TM 33.9147°), all within ±0.30° and apex-anchored (intercepts 0.013–0.017 ≪ 5% L), with
  station radii growing linearly (0.25→0.58) like a true conical shock.
- **Cause B (Gate C1 DIVERGENT triple):** E1's fine-grid near-wall cell was so thin that
  shock-capture noise broke the cone-surface Cp Roache triple (p≈7.5, fine value diverged).
  **E2 change 2 — gentler radial grading (`GR_RADIAL 12 → 5`)** in `gen_cone_mesh_e2.py`. A
  more uniform near-wall distribution lets the owner-cell surface pressure converge
  monotonically (offset r_wall+Δy/2 → wall value as ~1/N) while still clustering enough to
  resolve the shock. E1 coarse/medium were already within 0.14% of TM, so a monotone triple
  is expected to CONVERGE.

**Everything else is byte-identical to the vetted E1 grader** (rule-3 planted-zero, rule-4
completion `p U T rho` + age guard, rule-5 Roache/Celik + iterative plateau, the cone-Cp
owner-cell plateau reader with spatial Cx-sort trim, refuse-not-degrade, exit vocabulary) and
to the E1 case (inviscid Euler, slip wall, M∞=2.0, θ_c=15°, wedge axisymmetry, BCs, farfield).

## 2. EXACT reference (unchanged from E1, sound)

Regenerated Taylor-Maccoll ODE reference, reused byte-identical:
`taylor_maccoll_reference.py` → `tm_reference_M2p0_tc15.json` (β=33.9147°, M_c=1.70687,
**Cp=0.202248**, pc/p∞=1.56629; ODE grid-independent to 1e-13). No external PDF.

## 3. Gates, thresholds, labels (E1 bands reused)

Both decided only through the Roache triple (Celik F_s=1.25); non-CONVERGING or not-plateaued
→ NOT A RESULT (rule 5). GCI printed.

- **Gate C1 — cone-surface Cp (PRIMARY).** PASS iff **|Cp_fine − 0.202248| ≤ 0.010** and the
  triple is CONVERGING; else GATE FAIL / NOT A RESULT.
- **Gate C2 — conical shock angle β (SECONDARY).** PASS iff **|β_fine − 33.9147°| ≤ 1.0°** and
  the triple is CONVERGING; else GATE FAIL / NOT A RESULT.
  **SUPERVISOR RULING — 2026-09-10 — cfd-supervisor — FRAMING (i) RULED. THE GRADER IS NOT
  CHANGED.** *(This supersedes the OPEN DESIGN QUESTION previously flagged at this point. It is
  a legal pre-first-compute amendment under standing rule 2: it is taken BEFORE any E2 graded
  compute, and it moves no gate, threshold, band, cap or label — it fixes the gating METHOD that
  the already-committed grader already implements. **Condition and how it was checked:** the E2
  graded run root `verification/runs/navier_class/SUP_BOOSTER/graded_e2/` DOES NOT EXIST —
  checked at 2026-09-10T04:04:39Z by `os.path.exists`/`lexists`/`isdir`, all False, with the
  reader PLANT-VERIFIED able to see a non-absence in the same invocation (the directory was
  created, seen True, and removed) per standing rule 3. The sibling root `graded/` that DOES
  exist holds **E1's** compute only, under E1's separate freeze `c8510ff7` and E1's pinned
  grader `3c8d418a`; no byte of E2 graded compute has been bought.)*

  **The question ruled on, with BOTH options preserved so a reader can see what was decided
  against.** A captured shock's located radius wiggles at the sub-cell level across grids, so
  the β Roache triple may be OSCILLATORY even with a correct locator (on the E1 solutions the
  three β were 33.70/33.99/33.85 — all within ±0.30° of TM and inside the ±1.0° band, but not
  monotone). Two admissible framings were before the supervisor —
  **(i)** keep C2 as a Roache-gated gate (OSCILLATORY → NOT A RESULT), which is what
  `grade_sup_booster_e2.py` implements today; or
  **(ii)** the DMR precedent (`DMR_PREREGISTRATION.md` §3/§4): **report β_fine with its locator
  increment as a measurement** and gate only its rung-to-rung consistency (e.g. spread ≤ 1.0°),
  reserving the band as a PASS check on the fine value.
  **RULED: (i). NOT (ii).**

  **The four reasons, recorded as the supervisor stated them:**

  1. **GATE-FITTING IS THE DECIDING ARGUMENT.** E1's three beta values (33.70 / 33.99 / 33.85)
     are ALREADY KNOWN to be non-monotone while sitting inside the +/-1.0 deg band. Choosing
     framing (ii) now, with that outcome in hand, would convert a likely NOT A RESULT into a
     likely PASS. That is choosing the gate to fit the answer, and defeating exactly that is the
     entire evidentiary content of standing rule 2. The fact that (ii) has a respectable physics
     argument does not rescue it, because the argument arrives AFTER the number.
  2. **(i) is the status quo**, so the freeze requires no instrument edit at all — the
     lowest-risk path to a real verdict.
  3. **I ACCEPT the likely cost of my own ruling and it must be stated on the face of the
     record:** if beta wiggles again the triple is OSCILLATORY, C2 is NOT A RESULT under rule 5,
     and since the rung PASSes only if both gates PASS, the RUNG is NOT A RESULT even though
     C1's physics may be corroborated to 0.13-0.21%. That is an honest outcome, not a failure,
     and I would rather buy it for 31 core-min than buy a PASS I chose.
  4. **SEPARATELY, AND NOT AS PART OF THIS FREEZE**, the general question is referred to the
     verification team as a STANDARDS question, to be answered on the standard and not on this
     case: is a discretisation-QUANTISED locator output (a captured shock's located radius,
     whose value is quantised by the cell size) an admissible input to Richardson extrapolation
     at all, or does the DMR precedent govern that whole class? Roache's theory assumes a smooth
     functional of the solution. If verification rules the DMR precedent governs, that ruling
     applies lab-wide and arrives without anyone having chosen it to rescue a known number.
     Nothing in this freeze pre-empts that.

  **⚠ CONFLICTING RULING OF RECORD — DISCLOSED, NOT RESOLVED HERE (recorded by the preparing
  lane, 2026-09-10).** A ruling on this exact question already exists in the repository and
  rules the OTHER WAY: `verification/campaign/SUP_BOOSTER_E2_C2_SHOCK_ANGLE_GATING_RULING_2026-09-09.md`,
  authored by the **verification-supervisor**, dated 2026-09-09, committed as `0e9c1bcb`, titled
  *"framing (ii) GRANTED"*, and describing itself as *"gates cfd's SUP_BOOSTER E2 freeze"*. It
  grants framing (ii) on the DMR/F19/F4S precedent, holds that Rule 5 *"does not mandate that
  every quantity be Roache-gated"*, and attaches eight binding conditions (its §1), including a
  localized grader change decoupling C2 from the Roache coupling plus a re-run of check-1. Its
  own §3 records that *"On a 'keep Roache-gated' reading cfd could instead freeze as-is and
  accept an OSCILLATORY → NOT A RESULT on C2"* — i.e. it acknowledges (i) as an available
  reading while recommending against it. **This document does not decide which ruling prevails.**
  Reconciling a cfd ruling with a verification ruling is cross-family arbitration, which
  `CLAUDE.md`'s FIRST-ACTION RULE reserves to Sanaa and to no agent at any level. The conflict
  is recorded here so that it cannot be frozen over silently; **the freeze should not be taken
  until it is reconciled.** Note also that reason 4 above refers the general question to
  verification as still-open; verification's 2026-09-09 ruling is that team's answer for THIS
  case, though it expressly declines to codify a charter clause and flags the general
  codification for Sanaa's desk (its §2).
- **Labels:** fixed vocabulary. Rung PASS iff both gates PASS.

## 4. Grid triple for Celik F_s=1.25 (E2 gentler grading)

`gen_cone_mesh_e2.py`, r=1.5 uniform (2.25× cells/level). All three meshed clean at pre-flight:

| level | cells | max non-orth | max skew | neg-vol | h (rel) |
|---|---|---|---|---|---|
| coarse | 6,000 | 14.94° | 0.667 | 0 | 2.25 |
| medium | 13,500 | 14.95° | 0.668 | 0 | 1.50 |
| fine | 30,375 | 14.96° | 0.668 | 0 | 1.00 |

Hard gates PASS (≤70° non-orth, ≤4.0 skew, 0 neg-vol). Graded endTime = 15000 LTS
pseudo-iterations (deltaT=1, writeInterval 1000); iterative plateau enforced by the grader
(rule 5 clause 1). The grader asserts the actual 2.25× cell-count family (refuse otherwise).

## 5. Compute cap and cost basis

Point estimate from the E1 measured actual (same solver/endTime, near-identical cell counts):
**~31 core-min**; **CAP = 60 core-min** (≈2× margin). cost_basis: c7a.4xlarge at
**$0.0513/core-h** (owner-stated; box cannot read its own billing → **derived, not measured**,
COMPUTE_BUDGET_CHARTER §5). Derived cost at the cap: 60/60 × $0.0513 = **$0.0513 (derived)** —
under the $25 pre-auth. Overrun stops the run (rule 12). Serial (1 rank), sequential
coarse→medium→fine (good citizen). Estimate-vs-actual calibration filed to
`docs/COST_CALIBRATION.md` at completion.

## 6. Planted-zero (rule 3), completion (rule 4), refuse-not-degrade — unchanged from E1

Byte-identical to the vetted E1 grader: PLANT=1000.0 Pa into a cone owner-cell of a copy of the
finest `p`, read back through the same reader, refuse unless seen; rule-4 completion (rc 0,
End, last==endTime, `p U T rho` present and newer than 0/T); refuse (exit 2) not degrade;
exit 70 only for an internal defect. Verified live: planted-zero PASSED on the smoke case
(reader delta 10.6383 = 1000/94 exact); all three Roache verdict branches classify correctly.

## 7. Cross-cuts (unchanged from E1)

Celik F_s=1.25 (§4); Menter y+ N/A for the inviscid slip-wall rung (binds the MEASURED-tier
successor, PENDING-data); Spalart–Rumsey farfield (R_top 1.2 > L·tanβ 0.673, shock exits the
outlet); curvature LE-check geometrically inapplicable to a sharp cone (controls behave);
blockage N/A (unbounded external cone).

## 8. Amendment provision

Before first graded compute, amendments legal with a stated condition. After first graded
compute the gate/threshold/cap/label are closed (rule 2). The grading path (grader +
generator) is pinned by blob sha at the freeze commit and hashed against the committed blob
(scripts/check_comparator_freeze.py).

## 9. §2bb pre-flight — verdict at draft

| screen | result |
|---|---|
| E2 robust locator recovers the shock angle | β 33.70/33.99/33.85° on the three E1 solutions, all within ±0.30° of TM, apex-anchored — PASS |
| 3 E2 meshes admissible | non-orth ≤14.96°, skew ≤0.668, 0 neg-vol — PASS |
| Solver stability (E2 smoke, gentler mesh) | rc 0, End, last time == endTime 300, wall 10 s — PASS |
| Planted-zero control fires | reader sees 1000 Pa exactly — PASS |
| Roache verdict branches | CONVERGING→PASS, OSCILLATORY→NOT A RESULT, CONVERGING-outside-band→GATE FAIL — PASS |
| Reference regenerable, grid-independent | reused E1 frozen JSON (1e-13) — PASS |

**§2bb pre-flight verdict: ADMISSIBLE** — awaiting supervisor check-1 (new grader diff) + freeze (check-4).

## 10. Frozen grading path (pinned by git blob sha) — TO BE COMPLETED AT FREEZE

*(The supervisor pins these at the freeze commit; left as a placeholder table so the freeze
edit only fills the shas — the checker parses only `|`-table rows.)*

| file (pinned grading path) | git blob sha |
| --- | --- |
| `verification/runs/navier_class/SUP_BOOSTER/grade_sup_booster_e2.py` | TO BE PINNED AT FREEZE |
| `cases/navier_class/SUP_BOOSTER/gen_cone_mesh_e2.py` | TO BE PINNED AT FREEZE |

Provenance (non-.py): reused frozen reference tm_reference_M2p0_tc15.json git blob
c442a94bfd3166e443124e92248c5d96a929d8a5 (unchanged from E1).

---

*Artifacts:* new grader `verification/runs/navier_class/SUP_BOOSTER/grade_sup_booster_e2.py`;
gentler generator `cases/navier_class/SUP_BOOSTER/gen_cone_mesh_e2.py`; E2 mesh checks
`verification/runs/navier_class/SUP_BOOSTER/e2_meshcheck_{coarse,medium,fine}/`; E2 smoke
`.../e2_smoke_medium/`; E1 verdict `verification/campaign/SUP_BOOSTER_E1_VERDICT.md`.
*DRAFT / UNFROZEN — new-grader diff (check-1) + freeze + launch are the cfd-supervisor's.*
