# VMFLGPU003 — GPU Solver Path on the Lid-Driven Triangular Cavity: `GATE FAIL`

## VERDICT: `GATE FAIL` — limb C (physics vs the digitised benchmark) missed at L3; limbs A and B both HELD, on a `CONVERGING` triple

VMFLGPU003 reproduces the triangular-cavity case (VM2026R1 p. 229; CPU parent VMFL011) on the
**GPU solver path**: OpenFOAM v2606 `simpleFoam` with the **petsc4Foam** GPU linear-algebra path
(`mat_type aijcusparse`, `vec_type cuda`) on a **g6.xlarge** GPU instance, a three-level r = 2
ladder (800 / 3 200 / 12 800 cells at endTime 1000 / 1500 / 3500), RANKS = 1, run **twice per
level** (a GPU arm and a forced-CPU control arm). Graded by `ansys-lane-opus48` (lane B),
2026-08-27; the 351 MB run root was synced **read-only** from the GPU instance (3.15.199.152)
and graded on the box against the frozen comparator — no running solve on the instance was
disturbed.

### The three-limb gate, exactly (frozen comparator `grade_vmflgpu003.py`, blob `32420846`)

- **LIMB A — GPU EXECUTION (binary, physics-critical): HELD at all three levels.** Three GPU
  tells fired on the GPU arm and the forced-CPU control showed GPU-ABSENT at L1/L2/L3. A miss on
  limb A would be `NOT A RESULT` whatever the value; it did not miss.
- **LIMB B — GPU ≡ CPU (≤ 1e-4, both channels, every level): HELD.** Worst
  `|q_GPU − q_CPU|/|q_CPU| = 4.607e-12` (at L1, rms channel) against tol 1e-4 — the GPU path
  reproduced the lab's own CPU answer to **twelve digits**. (u_min channel: 0.0 at L2/L3.)
- **LIMB C — physics vs the digitised benchmark (rms ≤ 0.03 at L3): MISSED.**
  `rms_vs_benchmark = 0.034087720283630406` at L3 against band 0.03 — **OUTSIDE** (exceeds by
  13.6 %). GPU rms L1/L2/L3 = 0.0402642 / 0.0347751 / 0.0340877, monotone decreasing.
- **Roache triple on `u_min_norm` (a solution functional, not the error norm — the benchmark
  passes through near-zero in the quiescent lower half, so the error norm cannot converge to
  zero): `CONVERGING`.** Values -0.264494 / -0.319438 / -0.337560, **R = 0.329844, p = 1.60014,
  GCI_fine = 0.033030 (3.303 %)**. Because the triple is `CONVERGING`, rule 5 does **not** convert
  the row to `NOT A RESULT`; the gate outcome `GATE FAIL` (limb C missed) stands.
- **Tier: `NOT HELD`** — limb C missed; the tier ceiling is `GATE REACHED` (code-to-code
  reference), and the case cannot earn `PASS`.

### What this result means

**The GPU solver path is validated here and proven CPU-equivalent to twelve digits** (limbs A and
B both HELD on a `CONVERGING` triple — the first VMFLGPU case to clear both on a convergent
triple; GPU001 refused on a plateau clause, GPU002 was `NOT A RESULT` on an OSCILLATORY triple).
**The benchmark miss is not a GPU defect and not a discrepancy between the arms** — it MIRRORS the
CPU parent **VMFL011-R3 (register row #36, `GATE FAIL` at the identical rms 0.034088)**. The GPU
path reproduces the CPU physics exactly; both miss the digitised Jyotsna & Vanka benchmark by the
same margin. The miss is against the reference.

### Controls fired (CLAUDE.md rule 3, rule 5)

All planted-zero controls SEEN on both gate channels, each placed where its reader looks (L-347)
and sized to its reader (L-340): `u_min_norm` base −0.33756 → −0.46096 (delta 0.1234 > threshold
0.01234), `rms_vs_benchmark` base 0.034088 → 0.261936 (delta 0.227848), plateau plant SEEN at L3.
The negative (blind) arm is silent on both. `--selftest` **61/61 PASS**. Comparator disk blob ==
committed `32420846`. All six solves: `rc = 0`, `cap_fired = 0` (RUN_RC.{L1,L2,L3}.{cpu,gpu}).

### Cost

**0.856944 GPU-h** measured (total wall 3085 s; the CPU control arm adds 14.7333 core-min on the
same billed instance), of a **1.5 GPU-h cap** — cap never fired (57.1 %). Against the registered
**0.70 GPU-h** estimate, **ratio 1.224×**. **$0.6897 derived** at the published-list
**$0.8048/GPU-h** (g6.xlarge us-east-2), **derived not measured** — the console figure is owed and
supersedes (`COMPUTE_BUDGET_CHARTER.md` §5).

**WASTE, named separately and NOT absorbed into the 1.224 ratio:** the GPU idled **46.15 minutes**
between VMFLGPU003 finishing (18:08:43Z) and VMFLGPU001-R2 starting (18:55:33Z) = **0.7692 GPU-h,
$0.6190 derived** (idle window measured by the supervisor). This is an **infrastructure defect** —
a launcher freeze check bound to the wrong tree — not compute for this rung, and it is not part
of 003's ratio.

### Provenance

- Prereg freeze: **`fc8bef5135aabe4cd608ce8899ca72e125814eb3`** (2026-08-27T17:07:45Z; prereg blob
  `b0a5e8b97d8f6c8b6073f501382ccbaaff48e781`, matching RUN_RC).
- Comparator: **`3242084665d86baeff50fc59ab2b650e53cbb995`** (`grade_vmflgpu003.py`; disk == HEAD,
  `--selftest` 61/61).
- Run artifacts: `verification/runs/ansys_verification/VMFLGPU003/` (gpu/ + cpu/ each with L1/L2/L3;
  RUN_RC.{L1_20x40,L2_40x80,L3_80x160}.{cpu,gpu} rc = 0 each; COST.txt; STATUS.VMFLGPU003;
  TOOLCHAIN_MANIFEST.txt) — synced read-only from GPU instance 3.15.199.152.
- Reference: Jyotsna & Vanka, *J. Comp. Phys.* **122**, 107–117 (1995), via manual p. 229; the
  curve is Ansys's own digitisation (`reference/vmfl011_benchmark_xnorm.csv`, committed with
  VMFL011-R3). Manual gives no number (figure only). **Reference kind: code-to-code numerical —
  buys neither V nor P; tier ceiling `GATE REACHED`.**

**`GATE FAIL` is a finding, not a credential and not a deletion** (charter §6). Recorded honestly
with its numbers, unsoftened.

### Charter / doc update line (Amendment 1.4 Clause C)

Names `docs/NUMERICS_KNOWLEDGE.md` (the `N-AV` GPU-path-equivalence observation, landed
separately) and this record's dated addendum on the launcher's vacuous field-completeness guard.

---

## Dated addendum — 2026-08-27 — the launcher's FIELD-COMPLETENESS guard passed VACUOUSLY and is NOT evidence for VMFLGPU003

**Appended at the foot in rule-6 form by `ansys-lane-opus48` (lane B) on the supervisor's
dispatch of 2026-08-27. Nothing above is edited, struck, widened or renumbered; no gate,
threshold, cap, label or verdict changes.**

The launcher's `field_completeness()` guard (in `run_vmflgpu003.sh` and its VMFLGPU siblings)
was intended to refuse launch unless the case's `system/fvSolution` solver block declares
solvers for the required fields (`p`, `U`, plus the closure's fields). **On this case it passed
VACUOUSLY: `required = {}` — the guard checked NO fields.**

**Mechanism, measured — and NOT the "nested petsc blocks" story the board carried.** The guard's
embedded key-extraction parser contains the line `if ch in ";\n" and depth == 0: tok = ""`, which
clears the accumulated key token at **every depth-0 newline**. OpenFOAM's standard `fvSolution`
style puts the solver key (`p`, `U`) on its **own line**, with the opening `{` on the **next**
line — so the newline between the key and its brace clears the token, and when the `{` is reached
`tok` is empty, no key is captured, `keys = []`, `cand = {}`, and `required = cand ∩ {p, U} = {}`.

**A/B discriminator, independently reproduced in this lane** (not taken on report): with the key
and brace on **one line** (`p {`), `required = {U, p}` and the guard is active; with the key on
its **own line** (OpenFOAM standard), `required = {}` and the guard still fails. **Confirmed
`required = {}` on VMFLGPU003's frozen `system/fvSolution.template`, on its `gpu/L3_80x160`
actual `fvSolution`, and on VMFLGPU001-R2's frozen template** (the R2 run executing at the time
of writing printed the same empty set).

**Consequence:** the launcher's green field-completeness check is **NOT evidence** that the
required fields were declared for VMFLGPU003. It is a vacuous pass.

**What DOES stand, and why the verdict is untouched:** the verdict `GATE FAIL` rests on limb A (GPU-execution tells), limb B (GPU ≡ CPU, 4.607e-12), limb C (rms vs benchmark, 0.034088 > 0.030) and the CONVERGING Roache triple on `u_min_norm` — all read by the **frozen
COMPARATOR** from disk, which carries its own planted-zero controls and its own strict-completion
field-presence checks (CLAUDE.md rule 4). Those are the real evidence; the launcher's guard is a
redundant belt-and-braces check that happened to be vacuous. **The frozen launcher is NOT edited**
(a departure is disclosed, never reverted); this is a records addendum so no future reader cites
the launcher's field-completeness pass as evidence of field completeness for this case.

**Lines whose number changed above this section: 0.**
