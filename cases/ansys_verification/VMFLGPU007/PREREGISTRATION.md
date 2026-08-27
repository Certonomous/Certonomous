# VMFLGPU007 — PRE-REGISTRATION (frozen before compute)

**Case:** the lab's GPU solver path on **turbulent flow with heat transfer in a
backward-facing step**, Ansys Fluid Dynamics Verification Manual, Release 2026 R1,
**p. 243**. CPU parent VMFL013.
**Drafted by `ansys-lane-opus` (lane R2), 2026-08-27, for the supervisor to freeze.**
Prediction-first, frozen by sha before any solver runs (CLAUDE.md rule 2).

| artifact | blob |
|---|---|
| comparator `grade_vmflgpu007.py` | **`71d05b259e2446aeec04abbe22db1b93d167c39b`** |
| launcher `run_vmflgpu007.sh` | **`8747b42cc882167d56b0f316d583b31841ad7426`** |
| field-completeness guard `field_completeness.py` | **`195fcc0009e46d092dd836a6cbe189927f3268e7`** |
| mesh generator `resolve_blockmesh.py` | **`76ee0d3ac1c4c18529492155192f052f045ab7de`** |
| **reference (the gate's source)** `reference/vmfl013_vogel_eaton_nu.csv` | **`03d48a28644c637060d0abaf5fe74db86d5c6c16`** |
| context only, never the gate `reference/vmfl013_fluent_wall4_nu.csv` | `1a4fcc819d9e3f60bc5bc77b44a45c3c2163d4d1` |
| inlet profile `reference/VMFL013_step_ve.set.prof` | `7a1f24ed8ce70249255582821960f236423d5a9d` |
| pre-freeze mesh record `MESH_PREFREEZE_RECORD.md` | `f0f56f95c05a7adb3ac0689d99a0045fa01a82e9` |

**All five executable/registered paths are freeze-checked by the launcher at launch**
(HEAD blob == on-disk hash), including **the launcher itself**: a launcher that verifies
everything except itself and its own instruments is the same hole one level up.

**Zero compute at the time of writing.** No `VMFLGPU007` run root exists on the lab box or on
the GPU instance — `verification/runs/ansys_verification/VMFLGPU007` **does not exist**, which
is how this lab proves a pre-compute condition. (`VMFL007` and `VMFL007_R2` under that tree are
the CPU case VMFL007, a different case.)

---

## 1. THE MANUAL IS DEFECTIVE ON THIS CASE, and this section says exactly how

**The manual's "Test Case" paragraph for VMFLGPU007 is NOT the source of this setup, because it
is not about this case.** It is **byte-identical** to VMFLGPU006's paragraph on p.239 — 493
bytes, sha256 `97e3b556…`, sidecar lines 6229–6233 against 6168–6172, confirmed with `cmp` by
this lane — and it describes *"airflow over a Goldman stator blade at the mid-span … typical of
turbomachinery applications."* **This case is a backward-facing step.** A third instance of the
same paragraph, at sidecar line 5453, belongs to **VMFL071 (Mid-Span Flow Over a Goldman Stator
Blade)**, where it is legitimate; the defect is specifically that **007 carries 006's paragraph
verbatim**.

**What on that page IS sound and IS used as a source** — the defect is one paragraph, not the
page, and pretending otherwise would throw away real setup:

- **Reference** (intact): *J.C. Vogel, J.K. Eaton, "Combined Heat Transfer and Fluid Dynamic
  Measurements Downstream of a Backward-Facing Step", Journal of Heat Transfer, Vol. 107,
  pp. 922–929, 1985* — **experimental**.
- **Physics/Models**: *"Incompressible, turbulent flow with heat convection and reattachment."*
- **Material Properties** (complete): ρ = 1 kg/m³, μ = 1e-4 kg/m-s, k = 1.408 W/m-K,
  Cp = 10 000 J/kg-K. **Consistency check passed by this lane:** μ·Cp/k = **0.7102272727**, and
  the case's `thermophysicalProperties` carries `Pr 0.7102272727272728`.
- **Analysis Assumptions and Modeling Notes** (entirely correct and case-specific, and the
  source for the model and operating point): *"The flow is steady and incompressible. Fluid
  properties are considered constant. Pressure based solver is used. The inlet boundary
  conditions are specified using the fully developed profiles for the velocity, k, and epsilon.
  The incoming boundary layer thickness is 1.1 H. Under the given pressure conditions, the
  Reynolds number, ReH is about 28,000 The standard k-ε model with standard wall functions is
  used for accounting turbulence."*
- **Boundary Conditions**: *"Wall heat transfer, Q̇ = 1,000 W/m²"* (the column also carries a
  stray bare `I`).

**The Geometry column IS truncated** — it gives `H = 1 m` and nothing else: no expansion ratio,
no channel width, no upstream or downstream length. **Geometry therefore comes from the
`VMFL013_WB.wbpz` archive** at `/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/VM2026R1_FLUENT_ARCHIVES/`,
read **for setup and reference numbers only** (ANSYS_VERIFICATION_CHARTER §2). **The band comes
from the digitised Vogel & Eaton data**, not from the manual's figure and not from Ansys's curve.

**A case whose setup silently came from a paragraph about a different geometry is not
verifiable. That is why this is section 1.**

## 2. Geometry and the inlet — every number verified against the archive data

Verified by this lane by parsing the archive files directly, not by trusting the template's
comments (`INHERITED_SKELETON_AUDIT.md`):

| quantity | value | how it is known |
|---|---|---|
| step height H | 1 m | manual p.244 — the only dimension it gives |
| inlet plane | x = −3.8 H | `VMFL013_step_ve.set.prof`: `x` is −3.8 at **all 101 points** |
| inlet duct height | 4 H (y = 1..5) | the same file's `y` block, min 1.000000 max 5.000000 |
| downstream length | 30 H | `vmfl013_fluent_wall4_nu.csv`: 101 positions spanning exactly 0..30 |
| **expansion ratio** | **1.25** | downstream channel 5 H over inlet duct 4 H = 5/4 — Vogel & Eaton's rig |
| dimensionality | 2-D | `z` ≡ 0 and `v-velocity` ≡ 0 at every point |

**THE REGISTERED VELOCITY SCALE — `Re_H = 28 000` on `u_max = 2.8 m/s`.** The manual says only
*"ReH is about 28,000"* and never names the scale. Measured from the archive's own profile with
the manual's own properties (Re = U × 10⁴): **u_max = 2.800000 gives Re_H = 28 000 exactly**,
while the bulk mean 2.570882 gives **25 709**, missing by 8.2 %. The exactness is the evidence.
**`u_max` is the registered scale and 25 709 is recorded here so that nobody later "corrects"
the Reynolds number and silently moves the operating point.** `0/U` applies the profile with
`setAverage false`, so the identity survives into the run.

**A discrepancy in an inherited file, recorded rather than tidied away:**
`constant/boundaryData/inlet/points` says *"101 points"* in its own header and **contains 202** —
101 distinct y values duplicated across exactly 2 z planes (0.0 and 0.1). **The data is correct
and the duplication is necessary**: `timeVaryingMappedFixedValue` interpolates to patch face
centres, this mesh is one cell thick with centres at z = 0.05, and a single sample plane would
leave them outside the cloud. **Only the comment is wrong**, and the next reader will hit it too.

## 3. Solver, model and modelling choices, each registered

`buoyantSimpleFoam` (OpenFOAM v2606) + petsc4Foam + PETSc-CUDA; `heRhoThermo`, `pureMixture`,
`rhoConst ρ = 1`, `hConst Cp = 10 000`, `const` transport `μ = 1e-4`, `Pr = 0.7102272727272728`;
**standard k-ε with standard wall functions** (`kqRWallFunction`, `epsilonWallFunction`,
`nutkWallFunction`, `compressible::alphatJayatillekeWallFunction` `Prt 0.85`); `g = (0 0 0)`.

- **Why a buoyant solver for a case the manual calls incompressible:** it provides the energy
  equation and a temperature field with constant density. With `g = (0 0 0)`, `p_rgh ≡ p` and no
  buoyancy is introduced. **Registered as a modelling choice, not a physical claim.**
- **`stepFace`, `ductBottom` and `topWall` are ADIABATIC.** The manual states one heat-flux value
  and does not say the step face carries it, and the archive's Nu curve starts at x = 0 — at the
  step foot, not on the vertical face. **This is a real degree of freedom and is registered as a
  choice**; Vogel & Eaton heated the downstream wall.
- **`0/p` carries explicit BC entries** where `buoyantSimpleFoam` normally leaves `p` as
  `calculated`. With `g = 0` the two fields are identical, so it cannot move a number; noted so
  nobody later reads it as significant.

## 4. THE GATE — three limbs, and what each may earn

**Gate quantity:** the **peak surface Nusselt number and its location** on the heated wall,
with `Nu(x) = q''·H / (κ·(T_w(x) − T_inlet))` **derived by the comparator from the frozen
constants** `q'' = 1000 W/m²`, `κ = 1.408 W/m-K`, `H = 1 m`, `T_inlet = 300 K`. A solver-side
Nusselt number is never trusted.

**Gate reader, named before the run and the only one:** the `wallT` `surfaces` function object
writing raw face-centre `(x y z T)` on `heatedWall` at the directory named exactly `endTime`.

| limb | test | may earn |
|---|---|---|
| **A — GPU execution** | binary, physics-critical: on the GPU arm PETSc's own `-log_view` per-event accounting must show **GPU %F ≥ 99.0** and a non-zero host-to-device transfer count; **the forced-CPU arm must show 0 and 0**. A leaking control **REFUSES**. An **ABSENT** `-log_view` table **REFUSES** and is never read as a zero. | — |
| **B — GPU ≡ forced-CPU** | `\|q_GPU − q_CPU\| / \|q_CPU\| ≤ 1e-4` at **every** level | **PASS-CAPABLE** |
| **C — physics band** | `\|Nu_peak − 64.8530\| / 64.8530 ≤ 0.20` **and** `\|x_peak/H − 5.8209\| ≤ 1.5` | **`GATE REACHED` AT MOST — never `PASS`** |

**Why limb B is PASS-capable and limb C is not.** Limb B compares the two arms at an **identical
mesh with an identical scheme**, so discretisation error cancels on both sides and no grid triple
is needed to make the claim; it is the object under verification. Limb C is a physics comparison,
and **without systematic refinement this case cannot claim a discretisation-converged physics
result and will not pretend to.** `TIER_CEILING_C = "GATE REACHED"` is hard-coded in the
comparator and executed by `--selftest`, so the ceiling is a property of the instrument, not a
sentence in this document.

**A LIMB C MISS WITH LIMB B HOLDING IS A *MODEL* MISS, NOT A GPU-PATH FAILURE**, and the
comparator reports it in those words. Standard k-ε under-predicting backward-facing-step
reattachment is the best-documented deficiency of this exact model on this exact flow. It cannot
move limb B, which is unaffected by turbulence-model bias. **This is written down before the run
so that such an outcome reads as the gate working, not as an excuse.**

**Reference:** peak Nu = **64.8530** at **x/H = 5.8209**, parsed by this lane from
`reference/vmfl013_vogel_eaton_nu.csv` (19 two-column rows, x/H spanning 0.8206–15.8999).
**Why the extension changed:** `.gitignore` line 68 is `*.xy`, so the archive's `VMFL013_htc.xy`
was **invisible to git**. A pre-registration cannot cite a sha git does not carry, and a gate
whose reference is untracked is not frozen. Following VMFLGPU003, the data was copied
**byte-for-byte** (`cmp`-verified) into the tracked `.csv` above. The `.xy` original stays on
disk untracked as the extraction artifact; it was **not** force-added and `.gitignore` was **not**
edited.

**Band justification, fixed before any run** (`BAND_DECISION_ORDER.md`, written before the mesh
existed): (i) heat-transfer measurements of this class carry roughly ±5–8 % scatter;
(ii) standard k-ε with wall functions is documented to mis-predict peak Nu on this flow by
10–20 %. A band tighter than the model's own documented bias would fail the case for using the
model the manual specifies. The location band of 1.5 H is about a quarter of the measured
reattachment-scale distance. **Both must hold**: C1 alone could be met by a curve of the wrong
shape peaking in the wrong place; C2 alone says nothing about magnitude.

## 5. Ansys's own result is NOT the gate

`reference/vmfl013_fluent_wall4_nu.csv` is Fluent's own wall-4 Nusselt curve (101 rows). It is
quoted for **context only** and is never the gate (ANSYS_VERIFICATION_CHARTER §5.1). **A verdict
here is a statement about this lab's solver against Vogel & Eaton; it is never a statement about
Ansys.**

## 6. THIS IS A MESH-SENSITIVITY FAMILY, NOT A ROACHE TRIPLE — and no GCI is ever quoted

**Registered levels, with the MEASURED cell counts as birth-certificate targets** (built and
`checkMesh`'d before this freeze, on the lab box, in scratch — `MESH_PREFREEZE_RECORD.md`):

| level | NXI/NXD/NYU/NYL | endTime | **measured cells** | checkMesh | max non-orth | max skew |
|---|---|---|---|---|---|---|
| L1 | 16/96/24/10 | 1200 | **3 648** | Mesh OK | 0 | 1.14e-13 |
| L2 | 24/144/36/12 | 1800 | **7 776** | Mesh OK | 0 | 1.36e-13 |
| L3 | 36/216/52/14 | 3000 | **16 128** | Mesh OK | 0 | 2.52e-13 |

**`H1 = 0.07 m`, the wall-normal first-cell height, is IDENTICAL at every level**, solved for by
`resolve_blockmesh.py` so that `d1 == H1` exactly (to 1e-9) whatever the cell count.

**Why there is no Roache triple, and the reason is ARITHMETIC rather than methodological.** The
manual specifies standard wall functions, which are valid only in the log layer, so H1 must stay
fixed. Holding it fixed while refining means the wall cell approaches and then exceeds the
uniform spacing: **at L3 the solved gradings are already `GU = 1.2039` and `GC = 1.0411`,
essentially uniform**, so **a fourth level is arithmetically impossible** without reducing H1 —
which drops y+ out of the log layer and **changes the case**. Refinement is therefore not
systematic: the near-wall contribution does not scale with h while the rest of the mesh does. An
observed order across such a family is not a discretisation order, and a GCI from it would be a
number wearing the shape of a rigour it does not have.

**The alternative was considered and rejected, and why is registered:** forcing a genuine r = 2
triple would mean abandoning wall functions for a low-Re model at y+ ≈ 1. **That is a different
case from the manual's**, and this lab will not misrepresent a case to make a statistic
available.

1. **The three levels are a mesh-sensitivity / limb-B robustness family**: to show limb B holds
   across mesh sizes, and to bound how much limb C's comparison moves with mesh.
2. **NO GCI. NO observed order.** Not printed, not quoted, not "for information". Enforced **in
   code**: `no_gci_selfcheck()` scans the comparator's own emitted output and refuses if any such
   token ever reaches a reader. *(It fired during development on the author's own disclaimer
   text, which is how it is known not to be decorative.)*
3. **Rule 5's triple gating does not fire because NO TRIPLE IS REGISTERED. THIS IS A LIMITATION
   AND NOT AN EXEMPTION.** Nobody may read the absence of a triple as a route around CLAUDE.md
   rule 5. The rule-5 wording question — whether a no-triple registration needs its own charter
   clause — is with the verification team through the chief; the ceiling registered here can only
   be tightened by that answer, never loosened.
4. **What replaces the GCI:** the **mesh-sensitivity spread** of peak Nu across the three levels,
   printed beside limb C's value as an explicit uncertainty channel. That spread is the honest
   substitute for a number this family is not entitled to.

**The y+ band is registered on the ATTACHED REGION ONLY**: `11.0 ≤ y+ ≤ 300.0` on the
upper-quartile representative of the y+ distribution. **y+ → 0 at separation and reattachment
because the wall shear vanishes there by definition**, so a floor demanded everywhere would
refuse every correct backward-facing-step mesh; the minimum is **reported, never gated**.
**Design y+ ≈ 37.3** (first-cell centre 0.035 m, u_τ = 0.106434 m/s from Dean's correlation) —
an **estimate, not a measurement**; `yPlusFO` records the realised value and the comparator
refuses outside the band. *An earlier design at H1 = 0.03 gave y+ ≈ 16 — the buffer layer — and
passed `checkMesh` on all three levels; it was corrected before this freeze.*

## 7. Strict completion (rule 4) and the field classes (L-342)

**PHYSICS-CRITICAL, and the comparator REFUSES (exit 2) rather than grading a partial run:**
solver `rc`; an `End` line; last time == `endTime`; **`Time =` line count == `endTime`**; the
fields `T U p_rgh alphat nut k epsilon` present at `endTime`; and the **age guard** — every field
at `endTime` newer than the case's own `0/T`, which the launcher touches last at launch.

**INFRASTRUCTURE, reported and never refusing:** the **`ExecutionTime` line count**. petsc4Foam
prints `endTime + 2` — two initialisation timing lines inside `Time = 1`, before the first solve.
VMFLGPU001 froze that count as physics-critical, all six of its arms finished `rc = 0`, and it
has **no verdict** as a result. Also infrastructure: `COST.txt`, every GPU-hour and core-minute
figure, `LAUNCH_RECORD.txt`'s non-sha bookkeeping, pids and mtimes.

**R-RC as an explicit conjunction:** an absent `rc` record gives `rc = NOT MEASURED` **only when**
the other four clauses all hold; if any of those is also missing, completion **REFUSES**. A
missing rc never becomes a blanket pass.

**There is NO `residualControl`, so the run always reaches `endTime` and "it ran to endTime" is
NOT convergence.** Convergence is established separately by the **plateau channel**: `wallTmin`,
`min(T)` on the heated wall written **once per SIMPLE iteration**. Peak Nu occurs where
`T_w − T_inlet` is **minimum**, so `wallTmin` is a **monotone map of the graded number, not a
proxy for it**. Registered: window 200 iterations, peak-to-peak ≤ 1e-4 K, minimum 200 samples,
**and a LIVENESS FLOOR** — a null window is accepted only if the same channel moved by more than
1e-2 K over its full history. A dead channel and a perfectly converged one look identical to a
peak-to-peak test; VMFLGPU001-R2 was re-registered over exactly that, and this clause is strictly
**more** discriminating, not a relaxation.

## 8. PLANTED-ZERO CONTROL (rule 3) — at the row the reader actually selects

`PLANT = 1.234e-3 K` is applied to an **in-memory copy** of the wall-temperature reader **at the
argmax row — the row a `max()` reader selects** — not at an arbitrary first row, which was the
VMFL011 L-347 failure. The expected Nu move is computed from the frozen constants and the plant
must move the graded value by more than 10 % of it, or the comparator **refuses PLANT-BLIND**. A
**negative arm** (an unplanted copy must see exactly zero move) runs alongside. **The run tree is
never modified.**

## 9. COST (CLAUDE.md rule 12)

- **Estimate: 0.70 GPU-h** for the whole case (six solves). Basis, from this family's own measured
  numbers rather than a guess: VMFLGPU002's per-outer-iteration model `t = 0.0945 + 5.99e-6·cells`
  s on the GPU arm with the forced-CPU arm at 1.31×, applied to this case's cell counts and
  endTimes (3 648 × 1200, 7 776 × 1800, 16 128 × 3000). **CPU: 55 core-min** at `ranks = 1`,
  counting the GPU arm's host rank rather than treating it as free.
- **Cap: 1.5 GPU-h** (2.1× the estimate) and **90 core-min** on the CPU arm, both **enforced in
  the executable path by `timeout` with the rc captured inside the launcher**. An overrun
  **stops the run** and does not get a new budget. The headroom is a runaway guard, not a target:
  VMFLGPU002 came within 10.3 % of its cap on a healthy run and a cap that kills a healthy run
  manufactures a loss.
- **$ derived:** 0.70 GPU-h × $0.8048/GPU-h = **$0.56**; at the cap, $1.21. CPU 55 core-min ×
  $0.0513/core-h = **$0.047**. **DERIVED, NOT MEASURED** — this box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER.md` §5); the published-list GPU rate is not a console reading and the
  console figure is still owed and supersedes. GPU spend is **outside** the 2026-08-21 blanket.
- The one-time toolchain build is a **family** line amortised across the ten VMFLGPU cases and is
  **not** charged to this case.

## 10. EVERY GUARD DRIVEN, not read (Sanaa §1 / L-314 / L-357)

**L-357 is applied throughout: every planted failure asserts THE EXPECTED REFUSAL TEXT, never
merely a non-zero exit.** That lesson came from this lane — two arms of an earlier instrument
returned `rc = 1` and looked like clean refusals while actually being a `NameError` crash.

`grade_vmflgpu007.py --selftest` is **26/26**, byte-identical under `python3` and `python3 -O`,
**zero `ast.Assert` nodes** (`-O` strips `assert`, so a guard built on one evaporates exactly
when the code is run for speed). Arms: completion C1–C6 (rc, End, last time, `Time =` count,
fields, age guard); plateau I2–I4 including the liveness floor; limb A A1–A4 (absent `-log_view`
table, **control leak**, GPU %F floor, zero host-to-device); the y+ band; ambiguous reader;
missing `endtime`; arms disagreeing on `endTime`; a singular Nu; limb B miss → `GATE FAIL`;
limb C miss with limb B holding → `GATE FAIL` reported as a **model** miss; the ceiling; the
vocabulary; the no-GCI self-check both firing and staying silent on a clean grade; and the
zero-`assert` check.

`field_completeness.py --selftest` is **17/17** under both interpreters, zero `ast.Assert` nodes,
and returns `required={T, U, epsilon, k, p_rgh}` on this case's real inputs — **the first
non-empty required set this family has had.** Three defects were repaired and each is shown to
**flip** on the same fixture: the newline-clearing parser; the `{p, U}` base set that could not
see `p_rgh`; and a line-anchored closure lookup that missed the **inline** `RAS { RASModel
kEpsilon; … }` form this case actually carries — under which the ancestor **aborted this case at
launch for a false reason**. An empty required set now **refuses** instead of certifying.

`resolve_blockmesh.py` ships a control plus three driven refusals (inadmissible level, odd NYU,
unresolved placeholder), and its placeholder guard **failed on its first drive** — the regex
class excluded the underscore — and was repaired and re-driven.

## 11. Verdict vocabulary

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and only these
(rule 1). **This rung is `PENDING` until the comparator has graded a completed run against the
gate above.** Limb C cannot earn `PASS`; limb B can.

## 12. What this case will NOT claim

Nothing about **Ansys** — this box has no Fluent, and the archive was read for geometry and
reference numbers only. Nothing about **GPU performance**: no speed-up is claimed, sought or
gated, and **a GPU arm slower than the CPU arm passes every limb.** No **discretisation-converged**
physics result. No **GCI** and no **observed order**. No claim that the turbulence model is
correct — limb C is a comparison against experiment under a model the manual chose.

**Enqueueing is not authorisation** (`QUEUE_ENTRY_STANDARD.md` §1). `SUPERVISION_CHARTER` §3
check 4 — the pre-registration **committed** before compute — is the supervisor's own and is not
discharged by this document.

---

## PRE-COMPUTE AMENDMENT 1 — 2026-08-27 — a GRADING-PATH READER repair, found by a smoke before any GPU compute

**Version 1.1.** Appended at the foot. **Nothing above this section is rewritten, edited or
struck.** **Lines whose number changed above this section: 0**, verified by hashing the frozen
blob `2992b343624e3f3c73a73bb69d847265e03c9013` as an exact byte prefix of this file, not
merely asserted. Drafted by `ansys-lane-opus` (lane R2) on the supervisor's ruling to take the
smoke before the drop.

**THIS AMENDMENT MOVES NO LIMB, NO BAND, NO THRESHOLD, NO CAP AND NO LABEL.** The y+ band is
still `11.0 ≤ y+ ≤ 300.0`, character for character. Limb A's `GPU_PCTF_MIN = 99.0`, limb B's
`1e-4`, limb C's `0.20` and `1.5`, the reference `64.8530` at `5.8209`, the ceiling
`GATE REACHED`, the caps `1.5 GPU-h` / `90 core-min`, the mesh family, the endTimes and the
verdict vocabulary are all untouched. **One reader is repaired.**

| file | blob BEFORE | blob AFTER |
|---|---|---|
| `grade_vmflgpu007.py` | `71d05b259e2446aeec04abbe22db1b93d167c39b` | **`a4632b7ac2ef88fd98d14015b614ab4772ae71df`** |
| `run_vmflgpu007.sh` | `8747b42cc882167d56b0f316d583b31841ad7426` | **UNCHANGED** |
| `field_completeness.py` | `195fcc0009e46d092dd836a6cbe189927f3268e7` | **UNCHANGED** |
| `resolve_blockmesh.py` | `76ee0d3ac1c4c18529492155192f052f045ab7de` | **UNCHANGED** |

### 1. THE CONDITION: no compute, and how it was checked

**No solver of VMFLGPU007 has run.** On the **lab box**,
`verification/runs/ansys_verification/VMFLGPU007` **does not exist** — `ls` returns *"No such
file or directory"*. On the **GPU instance** the directory **exists and is EMPTY**:
`find <run root> -mindepth 1` returns **0 entries**. It was created, after the freeze commit,
**solely** so that `scripts/queue_entry_check.py`'s EXEC clause is satisfiable — that clause
refuses an entry whose `cwd` does not exist, because `queue_runner.py` chdirs into it.
**Creating an empty directory is not compute**, and the pre-compute condition was established
and recorded at the freeze commit `84a4d83a`, when the directory did not exist on either box.
**Zero GPU-seconds have been spent on this case.**

### 2. What the smoke was, and that nothing from it is a result

A **5-iteration, CPU-only** run of this case's L1 mesh, on the **lab box**, in a **scratch**
directory —
`/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/ansys-lane-r2/smoke`
— **never the run root**, which is what rule 4's age guard requires. Its **only** purpose was to
confirm the **actual on-disk names and shapes** the function objects write on this build. It
used `PCG`/`PBiCGStab` rather than the frozen `petsc` solver blocks, because **the lab box
has no petsc4Foam** and the linear algebra is not what a reader-path check tests.

**It produces NO graded quantity and NOTHING from it is ever cited as a result.** The peak Nu it
happens to yield (131.35 at x/H 0.156, after five iterations of an unconverged field) is not a
number about this case and appears here only to be disowned.

### 3. What the smoke CONFIRMED — the reader paths are real

```
postProcessing/wallT/5/T_heatedWall.raw          header "# x y z  T", 96 rows
postProcessing/wallTmin/0/surfaceFieldValue.dat  header "# Region type : patch heatedWall"
postProcessing/yPlusFO/0/yPlus.dat               header "# Time patch min max average"
postProcessing/wallFlux/0/wallHeatFlux.dat
postProcessing/resid/0/solverInfo.dat
log.buoyantSimpleFoam                            End line present, rc = 0
```

Every one matches the frozen comparator's globs. **Driven, not eyeballed** — the frozen readers
were executed against this real output: `read_wall_T` returned **96 rows** (= NXD, the heated
wall's face count) with the correct `x y z T` column order; the **planted-zero control FIRED ON
REAL SOLVER OUTPUT**, expected Nu move `0.02997040931279571` against observed
`0.029970409313051505`; `plateau` refused for the **right reason** (5 samples < the registered
200), which proves it found and parsed the file; and `logview_gpu` refused with *"no PETSc
-log_view table"*, correct on a box with no PETSc and a live demonstration that an absent table
is never read as a zero.

### 4. THE DEFECT the smoke found, which would have cost the entire run

The frozen `yplus_band()` ingested **every numeric token of every row** — `min`, `max` **and**
`average`, for **every patch** — and took the 75th percentile of the pool, calling it *"the
attached-region y+"*. **Measured on the real output:** the pool was **12 numbers from 4 patch
rows**, and its 75th percentile was **626.3 — which is `stepFace`'s AVERAGE.**

| patch | min | max | average |
|---|---|---|---|
| **`heatedWall` (the gate patch)** | **20.31** | **106.48** | **33.44** |
| `stepFace` | 106.5 | 1089.8 | 626.3 |
| `ductBottom` | 37.08 | 705.9 | 193.9 |
| `topWall` | 28.83 | 48.44 | 33.45 |

`stepFace` is the vertical step face — a 1H wall inside the recirculation zone, **neither the
gate patch nor the attached region** — and its y+ spans 106–1090 **by the physics of the flow,
not by any mesh defect**. **The frozen comparator would therefore have REFUSED A HEALTHY RUN at
clause Y3 after 0.70 GPU-h had been spent, and produced no verdict** — the identical loss this
family has already taken four times. **Three errors compounded:** it pooled four patches instead
of selecting the gate patch; it pooled three different *statistics* as though they were samples
of one distribution; and the percentile presupposed **per-face** data that the `yPlus` function
object never writes.

### 5. THE REPAIR — which number is read, and nothing else

Select the **gate patch** `heatedWall` — the wall Vogel & Eaton measured and the wall limb C is
computed on — and read its **`average`**, a statistic the file actually contains. Its `min`
and `max` are **reported and never gated**, because y+ → 0 at separation and reattachment where
the wall shear vanishes by definition. **The other patches are reported and never gated**: the
band is a statement about the gate patch. A y+ record with **no row for the gate patch** now
**refuses** (clause Y4) rather than substituting another wall. `YPLUS_QUANTILE = 0.75` is
retired because it presupposed data that does not exist; **the band it was applied to is
unchanged.**

**Measured on the same real output, the repaired reader PASSES**: gate patch average **33.4397**,
inside the frozen band **[11.0, 300.0]**, min 20.31 / max 106.48 reported. **That figure is
close to the 37.3 estimated pre-freeze from Dean's correlation — the independent check that the
MESH was right all along and only the READER was wrong.** No mesh, no band and no constant
needed to change.

### 6. The fixture was wrong too, and that is why the selftest had passed

The comparator's y+ fixture wrote a **single-column, single-patch** file that OpenFOAM does not
produce. **A selftest that only ever sees a shape the author invented cannot discover that the
real shape differs** — which is exactly the limit named in §12 of the freeze as the largest
residual risk. The fixture now writes the **real** multi-patch, five-column shape **carrying the
real out-of-band values the smoke measured**, so the trap is reproduced in the selftest. A new
arm, `y_nongate_patches_do_not_gate`, asserts that a clean run **still passes** with
`stepFace` at 626.3 — the regression this amendment fixes. Selftest is now **28/28** under
`python3` **and** `python3 -O`, still **zero `ast.Assert` nodes**.

### 7. What this amendment does NOT do

- It does not touch the launcher, the field-completeness guard or the mesh generator.
- It does not add any new gated quantity. `wallHeatFlux` is written by the case and is
  available on disk, but it is **not** part of the frozen grading path and is **not** wired in
  here: adding a new refusal path after the freeze is not a reader repair, and it is not done.
- It does not re-open any gate, and it does not authorise a launch.
  `SUPERVISION_CHARTER` §3 check 4 remains the supervisor's own.

---

## PRE-COMPUTE AMENDMENT 2 — 2026-08-27 — a LAUNCHER SEQUENCING repair: the case directory is completed before any OpenFOAM utility runs

**Version 1.2.** Appended at the foot, below Amendment 1, which it does not touch. **Nothing
above this section is rewritten, edited or struck.** **Lines whose number changed above this
section: 0**, verified by hashing the Amendment-1 blob
`bfbfd1a070d9c3747d2908734a5827300df2a5eb` as an exact byte prefix of this file, not merely
asserted. Drafted by `ansys-lane-opus` (lane R2) after the supervisor's personal triage.

**THIS AMENDMENT MOVES NO LIMB, BAND, THRESHOLD, CAP, LABEL, MESH COUNT, ENDTIME OR CONSTANT.**
Verified by comparing every registered constant on disk against its blob at HEAD, character for
character: `BAND_B = 1.0e-4`, `BAND_C1 = 0.20`, `BAND_C2 = 1.5`, `REF_PEAK_NU = 64.8530`,
`REF_PEAK_XH = 5.8209`, `YPLUS_MIN_ATTACHED = 11.0`, `YPLUS_MAX_ATTACHED = 300.0`,
`GPU_PCTF_MIN = 99.0`, `TIER_CEILING_C = "GATE REACHED"`, `PLANT = 1.234e-3`,
`LEVELS = (("L1", 3648), ("L2", 7776), ("L3", 16128))`, `H1_WALL = 0.07`, and in the launcher
`CAP_GPU_H=1.5`, `CAP_CPU_ARM_CORE_MIN=90` and the `LEVELS` line with its endTimes and
measured cell counts — **all IDENTICAL**.

| file | blob BEFORE | blob AFTER |
|---|---|---|
| `run_vmflgpu007.sh` | `8747b42cc882167d56b0f316d583b31841ad7426` | **`9174e648d7c571414cebe3911bb7e411b4646f56`** |
| `grade_vmflgpu007.py` | `a4632b7ac2ef88fd98d14015b614ab4772ae71df` | **UNCHANGED** |
| `field_completeness.py` | `195fcc0009e46d092dd836a6cbe189927f3268e7` | **UNCHANGED** |
| `resolve_blockmesh.py` | `76ee0d3ac1c4c18529492155192f052f045ab7de` | **UNCHANGED** |

### 1. THE CONDITION: still zero compute, and the failure itself is the evidence

The case was dropped at **20:20:34Z** and aborted at **20:21:35Z**. **Not one cell was meshed
and no solver ran** — `blockMesh` died in its own constructor, before generating any geometry,
with this in `gpu/L1/log.blockMesh`:

> `--> FOAM FATAL ERROR: (openfoam-2606)`
> `cannot find file ".../VMFLGPU007/gpu/L1/system/controlDict"`

**A utility that cannot construct its `Time` object has not computed anything**, so gates
remain open and this amendment is legal under rule 2. The failed attempt is **preserved, not
deleted**: the supervisor renamed the run root to `VMFLGPU007.attempt1_blockmesh_fail/` on the
instance and recreated an empty run root, so `log.blockMesh` — the evidence quoted above —
survives and the operation is reversible. **Nothing was deleted.**

### 2. THE DEFECT

**Every OpenFOAM utility constructs a `Time` object before it does anything else, and `Time`
reads `system/controlDict`. `blockMesh` is no exception.** The frozen launcher staged the case
and then, in this order:

```
199  cp -a "/." "/"            copies controlDict.TEMPLATE, not controlDict
202  python3 resolve_blockmesh.py ...     blockMeshDict resolved
205  rm -f .../blockMeshDict.template
206  ( cd "" && blockMesh ... )          <-- DIES HERE, no controlDict exists yet
...
233  sed ... controlDict.template > controlDict    <-- 27 LINES TOO LATE
```

**The contrast that proves it:** the VMFLGPU001-R2 launcher, which ran to completion, templates
`blockMeshDict`, `controlDict` **and** `fvSolution` and only then calls `blockMesh`. **This
launcher inherited that structure and then moved the mesh generation ahead of the templating
when `resolve_blockmesh.py` was introduced.** That is the whole defect: a reordering, not a
missing step.

### 3. THE REPAIR

The `fvSolution` and `controlDict` materialisation (and the `rm -f` of their templates) moves
to **before** the mesh generation, so the case directory is **complete before the first utility
is invoked**. The new order is: `mkdir` → `cp` → `fvSolution` → `controlDict` →
`blockMeshDict` → `blockMesh` → `checkMesh` → `Mesh OK` → birth certificate → field
completeness → `touch 0/T` → solve. **Nothing else changes**; no clause is added, removed or
re-worded, and the field-completeness call stays where it was.

### 4. THE FIX IS DRIVEN, and the flip is exact (L-357)

The per-arm staging block was **extracted from the launcher's own bytes** — once from the blob at
HEAD, once from the repaired file on disk — and both were run against the real frozen case inputs
with OpenFOAM v2606 on the lab box, in scratch.

| arm | rc | `blockMesh` said | `system/` afterwards |
|---|---|---|---|
| **HEAD bytes (the defect)** | **1** | `--> FOAM FATAL ERROR: (openfoam-2606)` / `cannot find file ".../system/controlDict"` | `blockMeshDict  controlDict.template  fvSchemes  fvSolution.template` |
| **repaired bytes** | **0** | `End` | `blockMeshDict  controlDict  fvSchemes  fvSolution` |

The repaired arm continues through `checkMesh` to
**`BIRTH CERTIFICATE OK: 3648 cells == registered 3648`**, and `field_completeness.py` on the
resulting directory returns `required={T, U, epsilon, k, p_rgh}`. **The instance's exact error
message was reproduced on the lab box from the frozen bytes**, which is what makes this a
demonstrated cause rather than a plausible one.

### 5. Why the smoke did not catch this, stated plainly

Amendment 1's 5-iteration smoke **validated the reader paths, not the launcher's case-assembly
sequence.** It ran in a scratch directory that had been **staged by hand** — templates
materialised manually before `blockMesh` was called — so it never exercised the launcher's own
ordering. **That is the boundary of what a smoke of the READER can prove**, and it is recorded
here so nobody later reads "the smoke passed" as covering the launcher. The lesson generalises:
a smoke proves the step it actually performs, and hand-staging a fixture silently replaces the
step under test.

### 6. What this amendment does NOT do

- **The comparator does not move.** `a4632b7ac2ef88fd98d14015b614ab4772ae71df` before and after.
- It adds no clause, no guard and no refusal path; it reorders four lines of staging.
- It does not touch the preserved failed attempt, and it does not authorise a launch.
  `SUPERVISION_CHARTER` §3 check 4 remains the supervisor's own.
