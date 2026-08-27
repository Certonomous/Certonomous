# VMFLGPU007 — RESULTS

**Case.** Turbulent flow with heat transfer over a backward-facing step, GPU solver path.
VM2026R1 **p. 243**; CPU parent VMFL013.

**Verdict: `NOT A RESULT`.** The frozen comparator **REFUSED (exit 2)** at its plateau clause
`IG3`. Graded 2026-08-27 by `ansys-verification-supervisor` on lane R's pull, against the
comparator frozen at `7126b0a5`.

---

## 1. The refusal, verbatim

```
REFUSE (VMFLGPU007 IG3): the plateau window peak-to-peak is 0.0237893 K, above the
registered 0.0001 K: the channel has not settled
```

`GRADING.txt` / `GRADING_EXIT_CODE.txt` (`COMPARATOR_EXIT_CODE=2`) in the run root.

## 2. Why this is a PHYSICS finding and not an instrument fault

The plateau clause reads `wallTmin` over the last `PLATEAU_WINDOW = 200` SIMPLE iterations and
requires peak-to-peak `<= PLATEAU_PTP_TOL = 1.0e-4` K. **All six arms miss it, and the miss is
large and orderly:**

| arm | window peak-to-peak (K) | multiple of tolerance |
|---|---|---|
| gpu/L1 | 0.0237893 | 238x |
| cpu/L1 | 0.0238644 | 239x |
| gpu/L2 | 0.0120540 | 121x |
| cpu/L2 | 0.0120592 | 121x |
| gpu/L3 | 0.00358665 | 36x |
| cpu/L3 | 0.00358716 | 36x |

The wall-temperature channel is **still travelling at `endTime` on every arm**, and the
peak-to-peak falls monotonically as the registered `endTime` rises (1200 / 1800 / 3000). The
runs were not carried far enough for the registered convergence criterion.

**The pre-registration predicted this shape before the run.** §7, verbatim: *"There is NO
`residualControl`, so the run always reaches `endTime` and 'it ran to endTime' is NOT
convergence."* The clause did the job it was frozen to do.

## 3. Strict completion (CLAUDE.md rule 4) HOLDS on all six arms

`rc = 0`; an `End` line; last time == `endTime`; `Time =` count == `endTime`
(1200/1800/3000); fields `T U p_rgh alphat nut k epsilon` present at `endTime`; **age guard
met**. The **`ExecutionTime` count is `endTime + 2` on all six** — petsc4Foam prints two
initialisation timing lines inside `Time = 1` — and the frozen comparator **already classifies
this as INFRASTRUCTURE under L-342 and does not refuse on it**, as §7 registered after
VMFLGPU001. The physics-critical count is the `Time =` count, which matches `endTime` exactly
on every arm.

**So the solver did not fail. The run completed cleanly and the gate refused it anyway** —
which is the distinction this register exists to keep.

## 4. No gate number was produced, and none is quoted

The comparator refused at `IG3` **before** limb A, limb B, limb C, the y+ report, the plant
line or the mesh-sensitivity spread were reached. **No peak Nusselt number, no GPU-vs-CPU
deviation and no deviation from Vogel & Eaton appears in this record**, and none was computed
by hand. Producing them outside the instrument would manufacture exactly the numbers the frozen
comparator declined to produce.

**No GCI, no observed order, no refinement ratio** — this case registers **no Roache triple**
(§6: `H1 = 0.07 m` is held identical at every level for the wall functions, so refinement is
not systematic and an observed order from it would be a number wearing a rigour it does not
have). Enforced in code by `no_gci_selfcheck()`. **This is a LIMITATION, NOT AN EXEMPTION from
rule 5.**

## 5. Instrument health, measured

- Freeze intact: comparator `a4632b7a`, launcher `9174e648`, prereg `1979b7a4` — each verified
  byte-equal to its HEAD blob **before and after** grading. `LAUNCH_RECORD.txt` independently
  records the launcher's own freeze check at launch against `head = 7126b0a5`, all five blobs
  matching, **so the file that ran is the file that is frozen.**
- `--selftest` **28/28 under `python3` and 28/28 under `python3 -O`**, outputs differing only in
  tmpdir and the `__debug__` marker. **Zero `ast.Assert` nodes**, so the `-O` run is a real
  check.
- **Planted-zero control (rule 3) FIRES.** Driven on the frozen bytes; refusal text verbatim:
  `REFUSE (VMFLGPU007 P1): PLANT-BLIND at the argmax row (index 14, x/H = 4.5312): a plant of
  0.001234 K should have moved peak Nu by about 0.00732393 but it moved by 0. The reader cannot
  see a known non-zero, so a zero from it is not evidence (CLAUDE.md rule 3).`
- **y+ band held** on the gate patch `heatedWall`: average 36.502 / 36.284 / 36.158 at L1/L2/L3
  inside the registered `[11.0, 300.0]`, close to the pre-freeze estimate 37.3 from Dean's
  correlation. Minimum **reported, never gated** (2.853 / 1.751 / 2.642) — y+ goes to zero at
  separation and reattachment because wall shear vanishes there by definition.

## 6. TWO DEFECTS IN THE FROZEN COMPARATOR — recorded, NOT repaired

Gates are closed post-compute (rule 2). **Neither defect moves this verdict**, because `IG3`
refuses first and independently; a repair could only have changed which refusal fired, never
turned this run into a result. Repairing an instrument post-compute on a case that has already
refused, when the only possible effect is a more favourable verdict, is the line this family
refused to cross on VMFLGPU001's `I5` and does not cross here. **The repairs go forward into
the successor.**

**DEFECT 1 — limb A's reader is wrong in both channels.** Read personally by the supervisor out
of the frozen file at `grade_vmflgpu007.py:457`:

- `gpu_pctf` is `max()` of the **last four numeric tokens** of a `MatMult`/`KSPSolve` row. The
  real trailing columns are `GPU Mflop/s | CpuToGpu Count | CpuToGpu Size | GpuToCpu Count |
  GpuToCpu Size | GPU %F`, so that `max()` returns the **CpuToGpu size in Mbytes** whenever it
  exceeds 100 — measured **210.0 / 672.0 / 2320.0** at L1/L2/L3, values that scale with mesh and
  exceed 100, **which a percentage cannot**. The true GPU %F is **100**. **Clause A3's floor of
  99.0 was therefore cleared by a megabyte count — a pass reached for the wrong reason, and a
  SILENT FALSE PASS.** That is the dangerous half.
- `h2d` is **never read at all**. The regex `CpuToGpu (?:Count|- CopyTo)\s*[:=]?\s*(\d+)` needs
  digits immediately after the optional colon; the only matching line is the **legend**, whose
  colon is followed by descriptive text. So `h2d` is always `None`, returned as `0`, and
  **clause A4 (`h2d <= 0` refuses) is UNPASSABLE ON ANY RUN, by construction** — the instrument
  was frozen guaranteed to refuse there. True values: **CpuToGpu Count = 7200 on `MatMult`,
  3601 on `KSPSolve`** (gpu/L1).
- The forced-CPU control reads `0.0 / 0` **correctly but by coincidence**: its trailing four
  tokens happen to all be zero, so the broken `max()` returns 0 and A2's leak check passes.

**Independent evidence the GPU path genuinely ran** (from the artifacts, not from the broken
parser): the gpu arm built `arch-cuda-opt`, CUDA architecture 89, PETSc types
`aijcusparse`/`cuda`; the cpu arm `aij`/`standard` with the `GPU Mflop/s` column identically 0
and `GPU %F` = 0 on every event. **Limb A's physics looks satisfied and limb A's reader is
broken.** This is recorded as context and is **not** a claim of limb A holding — the frozen
instrument never graded it.

**DEFECT 2 — a documentation defect.** The module docstring advertises `--drive-refusal <arm>`;
`main()`'s argparse defines only `--run-root` and `--selftest`. The option does not exist.

**DEFECT 3 — a gap, not a false claim.** **None of the 28 selftest arms drives the planted-zero
control.** The control is live on every graded run, but its refusal path was undriven until it
was driven by hand tonight. §10 of the freeze does not claim a plant arm, so this is a gap
rather than a broken claim. It is closed in the successor.

**THE PATTERN, now three occurrences in this family: a fixture-shaped parser meeting real
output.** VMFLGPU007 Amendment 1 (the y+ reader, caught by a smoke *before* compute);
VMFLGPU002 Amendment 5 (the limb-A tell, frozen guaranteed to refuse); and now this. The
reason this one escaped the pre-drop smokes is stated plainly: **no smoke of this family ever
produced a real PETSc `-log_view` table**, so `logview_gpu` was only ever exercised on its
absent-table path, never on its parse path.

## 7. Cost (CLAUDE.md rule 12)

- **0.306944 GPU-h** measured; total wall **1105 s**; per-arm wall 90 / 20 / 187 / 68 / 449 /
  286 s (gpu-L1, cpu-L1, gpu-L2, cpu-L2, gpu-L3, cpu-L3).
- **CPU arm 6.2333 core-min** at `ranks = 1`.
- **Caps: 1.5 GPU-h (20.5 % used) and 90 core-min (6.9 % used). NEITHER FIRED**, on any arm.
- **$0.2470 GPU + $0.0053 CPU = $0.2523 derived** at the published-list **$0.8048/GPU-h**
  (g6.xlarge us-east-2) and $0.0513/core-h. **DERIVED, NOT MEASURED** — the box cannot read its
  own billing (`COMPUTE_BUDGET_CHARTER.md` §5); **the console figure is still owed and
  supersedes.**
- **WASTE 0.000 for the run itself** — no truncation, no re-run, no cap fire. GPU idle after
  the run is named separately on the board and is **not** folded into this rung's ratio
  (`COMPUTE_BUDGET_CHARTER.md` §6).
- **The CPU arms ran FASTER than the GPU arms at every level** (20 vs 90, 68 vs 187, 286 vs
  449 s). At these mesh sizes the GPU path is a **correctness vehicle, not a speedup** — the
  same finding row #39 recorded. No speed-up is gated and none is claimed.

## 8. Artifacts, and an honest filing limitation

`verification/runs/ansys_verification/VMFLGPU007/` — 288 files, 39 MB, pulled by `rsync -a`
from the GPU instance with **mtimes preserved to the nanosecond** (286 rows compared each side,
0 differing; rolled content hash identical). Mtime preservation is load-bearing: the age guard
compares field mtimes against the case's own `0/T`.

**`.gitignore:67` is `**/postProcessing/`, so 60 of the 288 files — the entire postProcessing
tree, including the gate reader's own output and the `wallTmin` series this verdict rests on —
are GITIGNORED and exist ON DISK ONLY.** They were **not** force-added and `.gitignore` was
**not** edited. This follows the family's precedent (zero files are tracked under the
VMFLGPU003 and VMFLGPU001-R2 run trees either), but it is a real evidentiary limitation and is
named rather than glossed: *gitignored is not filed*. The small evidence files that this
verdict cites directly are committed.

## 9. What this row does NOT claim

It does not claim limb A, limb B or limb C held or missed — **the instrument refused before
reaching any of them.** It does not claim the GPU path was verified on this case. It does not
claim the plateau tolerance was wrong. It makes **no** statement about Ansys.

## 10. Forward

**VMFLGPU007-R2**, a fresh registration citing this row and re-grading nothing: a longer
`endTime` chosen from tonight's measured settling behaviour, limb A's reader repaired **by
column position against the table's own header** and driven on tonight's real bytes, a guard
that refuses a GPU %F above 100, and a `p1_*` selftest arm that drives the plant.

**The `endTime` may be chosen from tonight's data. The plateau tolerance may NOT be.** Loosening
`PLATEAU_PTP_TOL` because 1.0e-4 K refused tonight would be choosing the gate to fit the answer
in the favourable direction. The remedy is a longer run, not a wider band.
