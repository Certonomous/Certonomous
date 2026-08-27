# VMFLGPU002 — GPU solver path, laminar tee-junction flow split: `NOT A RESULT` (grid triple OSCILLATORY)

## VERDICT: `NOT A RESULT` — the amended frozen comparator GRADED the run and the GPU grid triple is OSCILLATORY

After two grading-path reader repairs (Post-compute Amendment 5, committed at `51e7b54e`
BEFORE this re-grade), the frozen comparator `grade_vmflgpu002.py` (blob `92a82426`)
graded the completed run to a verdict: **`NOT A RESULT`**, because the GPU grid triple is
**OSCILLATORY** (non-monotone) — rule 5 step 2 gates it to `NOT A RESULT` before any band
is read, and no GCI is quotable. Drafted by `ansys-lane-opus48` (lane H) for the
supervisor's audit. Manual **p. 227**, CPU parent VMFL010; reference the **numerical
benchmark** flow split **0.887** (Hayes, Nandkumar & Nasr-El-Din, *Computers and Fluids*
17, 537–553, 1989 — code-to-code, buys NEITHER V nor P); **tier ceiling `GATE REACHED`**,
so `PASS` was unreachable in any case.

### Both gradings, as the §2d.1 repair requires

**Pre-repair (frozen comparator `8172a0d3`, as launched):** refused at clause C7 —
> REFUSE (VMFLGPU002 C7): L1_N20: 1202 ExecutionTime lines, the registered endTime is 1200 (clause 5)

and, with C7 alone repaired, then refused at limb A —
> REFUSE (VMFLGPU002 A2): L1_N20: the FORCED-CPU CONTROL (mat_type aij, vec_type standard) REPORTED GPU WORK (tell1=True tell3=False). The tells cannot discriminate GPU from CPU on this build, so this row certifies NOTHING.

**Post-repair (amended comparator `92a82426`, blob-verified == HEAD, re-grade rc = 0),
verbatim verdict block:**
> LIMB A HELD at L1_N20 / L2_N40 / L3_N80: the GPU arm shows GPU %F > 0 on -log_view event rows and holds device memory (tell2), and the forced-CPU control showed GPU-ABSENT (Post-compute Amendment 5)
> PLANT SEEN ON ALL 2 GATE CHANNELS (L-340): 0.001234 planted into each of ['qInlet', 'qMain'] moved the SPLIT by ['0.00164058', '0.00185086'] -- gain ['1.329', '1.5'] x the plant, floor 0.1
> split(GPU) L1/L2/L3 = ['0.8859508974', '0.8844553076', '0.8847505466']
> split(CPU) L1/L2/L3 = ['0.8859508973', '0.8844553077', '0.8847505463']
> mass balance |q_in+q_main+q_branch|/|q_in| (GPU, L3_N80) = 6.18e-12 (tol 1e-06)
> limb B worst |GPU-CPU|/|CPU| = 4.07e-10 at L3_N80 (tol 0.0001)
> reference split = 0.887 (code-to-code / numerical benchmark -- buys NEITHER V nor P)
> limb C |GPU-ref|/|ref| at L3_N80 = 0.002536 (tol 0.02)
> triple split = ['0.8859508974', '0.8844553076', '0.8847505466'] ; state=OSCILLATORY R=-0.197406 p=None
> the grid triple is OSCILLATORY -- rule 5 step 2.
> NO GCI IS QUOTED off a non-CONVERGING triple.
> VERDICT: NOT A RESULT

### Why it is `NOT A RESULT` and not a band verdict

The GPU split triple 0.8859509 / 0.8844553 / 0.8847505 is **non-monotone** — it falls from
L1 to L2 and rises from L2 to L3 — so `d21/d32 = R = −0.197406 < 0`, which the Roache
classifier calls **OSCILLATORY**. Rule 5 step 2: a triple that is not `CONVERGING` is
`NOT A RESULT`, whatever its value, and no GCI may be quoted. **This gate can only turn a
result INTO `NOT A RESULT`, never the reverse** — so although limb B (GPU vs CPU) and
limb C (vs the benchmark) both held, they are not the verdict.

### The physics beside the verdict — CONTEXT, explicitly NOT THE VERDICT

- **Limb B** (GPU arm vs forced-CPU arm): worst `abs(GPU−CPU)/abs(CPU) = 4.07e-10` at L3,
  far inside the frozen `1e-4` band. **The GPU linear-algebra path reproduced the lab's own
  CPU answer to ten digits.**
- **Limb C** (finest GPU vs the 0.887 benchmark): `abs(GPU−ref)/abs(ref) = 0.2536 %`, well
  inside the frozen `2 %` band.
- **Mass balance** at L3: `6.18e-12` of the inlet flux (tol `1e-6`) — the discrete tee
  balance closes.
- Both limbs holding while the triple oscillates is the honest signature of a converged,
  correct flow split whose grid-convergence path is **non-monotone** on this three-level
  family — a real finding about the case, not a defect in the solve.

### The GPU path genuinely ran (recorded, per the supervisor)

From PETSc's own `-log_view` accounting (which grades nothing): on the **GPU arm**,
`MatMult` and `KSPSolve` run at **GPU %F = 100** with **6000 CpuToGpu transfers (173 MB)**
and GPU Mflop/s 2834; on the **forced-CPU arm**, the same events show **GPU %F = 0** and
**zero transfers**. `tell2` (a solver PID holding device memory) fires on the GPU arm only.
The GPU arm was also faster at L3 (967 s vs 1636 s) — recorded as-is; **no speed-up was
gated**. This is the independent instrument that established the limb-A reader defect
(Amendment 5): the frozen `tell1` matched the arm-independent `-log_view` legend and so
fired on the CPU arm too, and `tell3` expected a ksp_view `type: aijcusparse` line this
build echoes only in the options block.

### Strict completion (rule 4) — HELD at all six solves (verified by the lane)

`rc = 0` at all six (`RUN_RC.*`), an `End` line each, `Time =`-line count == the registered
endTime (1200/1600/2200) exactly, `U` and `p` present at endTime, the **age guard met** on
all 12 field checks (every endTime field newer than its `0/U` marker). The `ExecutionTime`
count is endTime + 2 on every log — two petsc4Foam init timing lines inside `Time = 1` —
**INFRASTRUCTURE** under L-342 (Amendment 5 item 1), a warning that never refuses. The
instrument graded; the solver did not fail.

### Provenance
- **Freeze commit:** `eca61c2d` ("VMFLGPU002 FREEZE", zero compute); prereg blob at launch
  and now **`790a3bbd`** (frozen §1–§13 unchanged; Amendment 5 appended at the foot, 0 lines
  changed above).
- **Comparator:** launch blob **`8172a0d3`**; amended blob **`92a82426`** (Post-compute
  Amendment 5, commit `51e7b54e`, committed BEFORE this re-grade), blob-verified == HEAD.
- **Freeze proven at launch:** `LAUNCH_RECORD.txt` records prereg_sha_head == prereg_sha_disk
  == `790a3bbd` and comparator_sha_head == comparator_sha_disk == `8172a0d3`, written before
  any solver ran (host `ip-172-31-44-162`).
- **Selftest:** 47 checks GREEN, byte-identical under `python3` and `python3 -O`, zero
  `ast.Assert` nodes; the repaired reader verified on the six real logs (True on all GPU
  arms, False on all CPU arms) and driven on a forged GPU-arm log with GPU %F = 0 (refuses).

## COST (rule 12 calibration)
- **Measured actual:** **0.896944 GPU-h** (total wall 3229 s), of a **1.0 GPU-h cap** — the
  cap did **NOT fire**, but the run came within **10.3 %** of it. CPU arm **30.567 core-min**
  of its 60 core-min cap. `COST.txt`.
- **Pre-registered estimate:** **30.4 core-min** (the supervisor's brief). Restated in the
  measured unit: the GPU run consumed **0.896944 GPU-h**; the CPU arm's **30.567 core-min**
  matches the 30.4 estimate to **ratio 1.005**. The GPU-hour figure had no separate
  pre-registered GPU-h estimate; it is recorded as the first VMFLGPU002 GPU-h measurement.
- **$ derived:** 0.896944 GPU-h × $0.8048/GPU-h = **$0.7219**, **DERIVED not measured**
  (published-list rate, g6.xlarge us-east-2; `COMPUTE_BUDGET_CHARTER.md` §5). **Console figure
  still owed.**
- **Idle waste, named separately (not absorbed into any ratio):** the run finished
  2026-08-26T23:40:01Z and the instance sat idle until grading began ~2026-08-27T16:20Z —
  **~16 h 40 m ≈ $13.41 derived** at the published-list rate. This is waste, not compute for
  this rung.

**Ledger follow-up:** register **row 34** and **calibration C-168** land with this record.
**No R2 is warranted:** a re-run on the same three grids reproduces the same OSCILLATORY
triple and the same `NOT A RESULT`, so it buys nothing (supervisor, 2026-08-27).

---

## Dated addendum — 2026-08-27 — the launcher's FIELD-COMPLETENESS guard passed VACUOUSLY and is NOT evidence for VMFLGPU002

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
required fields were declared for VMFLGPU002. It is a vacuous pass.

**What DOES stand, and why the verdict is untouched:** the verdict `NOT A RESULT` rests on the OSCILLATORY GPU grid triple (rule 5 step 2, R = −0.197406) and the amended comparator's own field reads — all read by the **frozen
COMPARATOR** from disk, which carries its own planted-zero controls and its own strict-completion
field-presence checks (CLAUDE.md rule 4). Those are the real evidence; the launcher's guard is a
redundant belt-and-braces check that happened to be vacuous. **The frozen launcher is NOT edited**
(a departure is disclosed, never reverted); this is a records addendum so no future reader cites
the launcher's field-completeness pass as evidence of field completeness for this case.

**Lines whose number changed above this section: 0.**
