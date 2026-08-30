# VMFL063 — RESULTS

**LANDED 2026-08-30.** Drafted by `ansys-lane-opus`; the freeze identity, the strict-completion
ruling, the comparator invocation and every headline number below were **verified personally by
`ansys-verification-supervisor`** before this file was committed, not accepted on report.
Filed under this family's convention `cases/ansys_verification/<CASE>/RESULTS.md`, which is the
form every `RESULTS path` cell in the register uses.

Separated Laminar Flow Over a Blunt Plate, Ansys Fluid Dynamics Verification Manual
**Release 2026 R1, March 2026, p. 193** (Test Case, geometry) and **p. 194**
Table .63.1 / Table .63.2 (Results Comparison). **FIRST registration of this case** —
`grep -c VMFL063` on the register returned **0** at freeze and returns **0** now.

Graded by the frozen comparator `cases/ansys_verification/VMFL063/grade_vmfl063.py`,
blob **`fc339a79d1b0b1a5a5c6beba455e8e3f0e518d45`**, against the pre-registration
`cases/ansys_verification/VMFL063/PREREGISTRATION.md`, blob
**`efdb2a8abb788c5f55bac60f10fb09816af50a30`**, frozen at commit **`2df23798`**
(v1.0) and amended at **`3602cbf3`** (v1.1, Amendment 1, launcher only) — the commit
the queue entry names as `prereg_commit`.
Raw grading record: `verification/runs/ansys_verification/VMFL063/GRADING_RECORD_VMFL063.json`
(sha256 `e83502f74e8314f547cd8d4a3d97472a946c2e61156d438b342853821f942155`).

---

## VERDICT — `GATE FAIL`

**`LR/(2t) = 5.600237`** at the finest level **L3** against the manual's experimental
**Target 4.0** — **40.0059 %** deviation against the frozen **10 %** band, on a
**`CONVERGING`** triple. This is registered outcome **#2** of pre-registration §10:
*"ROW `GATE FAIL` (physics) — triple `CONVERGING`, L3 outside the 10 % band. A finding,
recorded with its numbers, never softened and never deleted."*

| limb | class | verdict | registered ceiling |
|---|---|---|---|
| **A** | CONTINUUM (`VERIFICATION_CHARTER` §2f.3) | **`GATE FAIL`** | `GATE REACHED` — **`PASS` unavailable** |
| **B** | SAME-DISCRETE-PROBLEM IDENTITY | **`PASS`** | `PASS` |
| **ROW** | worst limb | **`GATE FAIL`** | `GATE REACHED` (row ceiling, by construction) |

**The row verdict is the WORST limb and limb B's `PASS` does not carry it.** Limb A's
ceiling was declared `GATE REACHED` before compute because the reference is
**EXPERIMENTAL** (Lane & Loehrke 1980), so this registration could never have produced
a credential (`ANSYS_VERIFICATION_CHARTER` §6: *"Only `PASS` rows are credentials"*).
**The ceiling did not bind on this outcome** — `GATE FAIL` sits below it either way —
and that is stated so nobody reads the ceiling as having done work it did not do.

---

## 1. THE MEASUREMENT

Reattachment length on `plateTop`, located as the **last** reversed-to-attached crossing
of the physical wall shear inside the frozen window **(0.0, 1.2] m**, linearly
interpolated between bracketing face centres.

| level | cells | iterations | LR (m) | **LR/(2t)** | plateTop faces | local Δx at the crossing |
|---|---|---|---|---|---|---|
| **L1** | 5 760 | 1 004 | 0.610931435 | **6.788127** | 80 | 25.95 mm |
| **L2** | 23 040 | 1 944 | 0.554823232 | **6.164703** | 160 | 11.81 mm |
| **L3** | 92 160 | 4 177 | 0.504021299 | **5.600237** | 320 | 5.477 mm |
| L1D (twin) | 5 760 | 1 004 | 0.610931435 | 6.788127 | 80 | — |

Reference **4.0** (manual Table .63.1 *Target*). Context only, never the gate:
**Ansys Fluent 4.16** (Ratio 1.04), **Ansys CFX 4.05** (Ratio 1.01).

**Deviation at L3: 40.0059 % against a frozen 10 % band.** The lab's `simpleFoam`
over-predicts the reattachment length by **40 %** on the finest mesh run. It is not a
near miss and it is not presented as one.

**The sign convention was fixed from the data, not assumed.** At `X_SIGN_REF = 1.35 m`
— outside the search window, 0.15 m short of the outlet — the reported
`wallShearStress` x-component is **negative** in attached flow at every level
(τ_ref = −1.440e-5 / −1.429e-5 / −1.401e-5 Pa·m³/kg at x ≈ 1.3577 / 1.3448 / 1.3518 m),
so the orientation is **−1** at all three levels and the comparator multiplied through.
Had this been assumed rather than measured, the reader would have had the sign backwards.

**Crossing census (diagnostic, gates nothing).** Exactly **one** reversed-to-attached
crossing in the window at every level (`neg_to_pos: 1`, `pos_to_neg: 1`,
`starts_attached: true`, 74 / 149 / 298 samples in window). **The secondary corner eddy
that voided VMFL064 attempt 1 is NOT resolved at any level here**, so the registered
last-crossing reader and the off-path first-crossing reader would return the same
number on this data. The last-crossing choice was made in advance and cost nothing;
it also earned nothing here, and that is worth recording honestly.

**Cross-instrument agreement, and it gates.** An independent instrument — the sign
change of streamwise `u_x` in the first cell row above the plate, a different field with
a different discretisation — located the same event to:

| level | gap (m) | tolerance (3 local cell widths, m) | margin |
|---|---|---|---|
| L1 | 1.996e-07 | 7.786e-02 | **390 000×** inside |
| L2 | 4.286e-08 | 3.542e-02 | **826 000×** inside |
| L3 | 9.981e-09 | 1.643e-02 | **1 646 000×** inside |

Two independent instruments agree to 8–10 significant figures. **The 40 % deviation is
not a reader artefact.**

---

## 2. THE TRIPLE, ITS GCI, AND AN HONEST LIMIT ON BOTH

```
f_L1 = 6.788127   f_L2 = 6.164703   f_L3 = 5.600237
d21  = -0.6234245   d32 = -0.5644659   R = d32/d21 = 0.905428
state = CONVERGING      (0 < R < 1, monotone)
p     = 0.143328        (>= frozen floor P_MIN = 0.05)
GCI_fine (Fs = 1.25) = 1.206236  ->  120.62 %
f_extrapolated = 0.196072
```

**The triple is `CONVERGING` on the registered criteria and rule 5 applies one-way.**
`R = 0.905` lies in (0, 1) so the sequence is monotone and not `DIVERGENT`,
`OSCILLATORY`, `STAGNANT` or `EXACT`; `p = 0.1433` clears the frozen floor
`P_MIN = 0.05` (`docs/ansys_verification/FINDING_p_floor.md` §4). **Rule 5 can only turn
a verdict INTO `NOT A RESULT`, never the reverse**, and no such turn applies here. The
row stands at `GATE FAIL`.

**AND THE TRIPLE IS ONLY BARELY CONVERGING, WHICH IS DISCLOSED, NOT USED TO MOVE THE
VERDICT.** Three facts belong in the record and none of them is a gate:

1. **`R = 0.905` is close to 1.** Successive differences are shrinking by less than 10 %
   per halving. That is the arithmetic edge of `DIVERGENT`, not the middle of
   `CONVERGING`.
2. **`p = 0.143` is far below the formal second order of the scheme.** The solution is
   **not in the asymptotic range** on these three meshes.
3. **`GCI_fine = 120.62 %` is larger than the value it qualifies**, and
   `f_extrapolated = 0.196` is **physically meaningless** — Richardson extrapolation
   with `r^p − 1 = 0.1043` divides the last difference by a very small number. The GCI is
   printed because the registration says a GCI is quoted on a `CONVERGING` triple and on
   no other; **it is quoted, and it is quoted with this caveat rather than presented as
   a discretisation uncertainty a reader could use.**

**The physical reading, stated as a reading and not as a result.** The sequence
6.788 → 6.165 → 5.600 is marching monotonically **toward** the reference 4.0 and had not
stopped by L3. Grid convergence on this quantity has **not** been demonstrated, and this
row establishes nothing about meshes finer than L3 (pre-registration §12). Whether a
finer family would land inside the band is **unknown and is not claimed here.** No
finer level is invented after the fact to rescue the number.

---

## 3. STRICT COMPLETION — CLAUDE.md RULE 4, AS REGISTERED, AT ALL FOUR LEVELS

**HOLDS at L1, L1D, L2 and L3.** The comparator's `completion()` refuses (exit 2) on any
failed clause; it refused nothing and returned `state = COMPLETE` four times.

**The clause that needs explaining is the endTime clause, and it was registered before
compute, not improvised.** The four levels stopped at **four different iteration counts**
(1004 / 1004 / 1944 / 4177) against a common **`endTime = 30000`**. That is the signature
of residual-convergence termination, and **pre-registration §6 clause 4 (lines 324–331)
declared exactly that adaptation in advance**, verbatim:

> **last `Time` < `endTime`.** **This is the declared adaptation of rule 4's "last time
> == endTime" clause for a `residualControl`-terminated STEADY solve, and it is declared
> HERE, before compute, not improvised in the comparator.** For a steady solve
> `last == endTime` means the solver **ran out of clock without converging**, which is
> the opposite of completion; the honest completion condition is that it stopped on its
> own residual criterion strictly before the ceiling.

The comparator implements that and only that, at `grade_vmfl063.py:585-587`:

```python
if not (out["last_time"] < out["endTime"]):
    raise SystemExit2("%s reached endTime %g -- it ran out of clock and did NOT converge"
                      % (level_dir, out["endTime"]))
```

**So a run that DID reach 30000 would have been refused as incomplete.** Under this
registration `last == endTime` is the failure and `last < endTime` is the pass, and that
inversion is registered, not chosen after the numbers were seen. Pre-registration §10
outcome 5 names the opposite result — *"`NOT A RESULT` — the solve never converged … last
`Time` == `endTime` (ran out of clock)"* — as the largest scientific risk in the
registration. **It did not materialise.**

| clause | comparator line | L1 | L1D | L2 | L3 |
|---|---|---|---|---|---|
| solver `rc = 0` (captured **inside** the detached subshell, `.solver_rc`) | :551-554 | 0 | 0 | 0 | 0 |
| exactly one `End` line, exact filename via `one_match` | :562-564 | 1 | 1 | 1 | 1 |
| `SIMPLE solution converged` present | :565-569 | yes (1004) | yes (1004) | yes (1944) | yes (4177) |
| **last `Time` < `endTime` 30000** (registered adaptation) | :581-587 | 1004 | 1004 | 1944 | 4177 |
| `ExecutionTime` count == iteration count | :574-577 | 1004 | 1004 | 1944 | 4177 |
| fields present at that time (`U p wallShearStress Cx Cy`) | :598-599 | 5/5 | 5/5 | 5/5 | 5/5 |
| numerically-latest time dir (`key=float`) == log's last `Time` | :591-597 | 1004 | 1004 | 1944 | 4177 |
| **AGE GUARD** — every field strictly newer than `0/U` | :600-608 | **+9 s** | **+8/9 s** | **+74 s** | **+739 s** |

**THE AGE GUARD, VERIFIED INDEPENDENTLY OF THE COMPARATOR.** The datum `0/U` is
`touch`ed last by the launcher, immediately before the solver, so it dates the run
allowed to produce the answer. Read directly from the filesystem:

| level | `0/U` mtime (UTC) | field mtimes at the converged time | strictly newer? |
|---|---|---|---|
| L1 | 17:41:41 | 17:41:50 (all five) | **yes, +9 s** |
| L1D | 17:41:50 | 17:41:58 (U, p, wallShearStress), 17:41:59 (Cx, Cy) | **yes, +8/+9 s** |
| L2 | 17:41:59 | 17:43:13 (all five) | **yes, +74 s** |
| L3 | 17:43:15 | 17:55:34 (all five) | **yes, +739 s** |

Each level's datum also post-dates the previous level's fields, so the four solves are
serialised in the order the launcher ran them. No pre-existing `0/` or numeric time
directory was inherited: the run root was created **empty** at enqueue and each level
holds exactly two time directories, `0` and its own converged time.

**ITERATIVE CONVERGENCE (rule 5 step 1) HOLDS AT EVERY LEVEL.** Final-iteration initial
residuals against the registered `residualControl` (`p 1e-08`, `U 1e-09`):

| level | Ux | Uy | p |
|---|---|---|---|
| L1 / L1D | 3.66523e-10 | 9.88509e-10 | 5.22361e-10 |
| L2 | 3.76193e-10 | 9.98921e-10 | 5.25229e-10 |
| L3 | 4.12737e-10 | 9.97905e-10 | 5.25543e-10 |

Every level is one to two orders inside its own criterion. **L1 and L1D agree to every
printed digit on all three residuals** — an independent corroboration of limb B.

**Mesh, from each level's own `checkMesh` birth certificate** (`MESH_STANDARD` §6):
cells **5 760 / 5 760 / 23 040 / 92 160**, exactly the registered counts;
`Mesh OK`, `failed_checks: 0`, max non-orthogonality **0.0** (pure Cartesian), max
skewness ≤ 1.34e-13, max aspect ratio 62.9 / 62.9 / 62.4 / 62.8 at L1 / L1D / L2 / L3.

---

## 4. THE CONTROLS

### 4.1 Planted zero (CLAUDE.md rule 3) — **FIRED, THROUGH A REAL DISK ROUND TRIP**

**It is a real-path control, and that was checked by reading the code, not by trusting
the label.** `planted_zero_tau()` (:400-467) takes the **real solver-written file** via
`one_match`, `shutil.copy`s it to a temp dir, plants **on disk** through
`_plant_patch_vector_x()` (:239-259, which `open(p, "w")` and rewrites the file), then
reads it **back off disk** through the same `read_patch_vector_x()` the grading path
uses. **It does not plant into an already-parsed in-memory list** — which is exactly the
defect this team found in `grade_vmflgpu005.py:609` and `grade_vmflgpu007_r2.py:413` and
repaired at commit `87a624ea`. The middle clause of rule 3, *"reads it back from disk"*,
is genuinely present here.

| stage | channel | planted | result |
|---|---|---|---|
| **P1a** reader sensitivity | wall shear, **every one of 80** `plateTop` faces of `L1/1004/wallShearStress` | 6.7766e-06 physical (−6.7766e-06 reported; `K_PLANT = 0.05 × max\|τ\|` in-window) | worst read-back error **4.9999e-16** — every face moved by exactly the plant |
| **P1b** gate-functional sensitivity | same planted file, **full gate functional** | — | crossing moved **upstream by 0.0883645 m** (0.610931 → 0.522567 m) |
| **P1a** reader sensitivity | near-wall `u_x`, every internal cell of `L1/1004/U` | 2.5850e-03 m/s (`K_PLANT_U = 0.05 × U_inf`) | worst read-back error **5.0000e-14** |
| **P1b** gate-functional sensitivity | same planted `U` | — | **plant pushed the `u_x` crossing OUT of the window** |

Both stages on both channels returned `passed: true`. The comparator's only way to
return from these functions is to have seen the plant on both stages; either failure
raises `SystemExit2` (exit 2). The `--selftest` additionally monkeypatches the *writer*
so the plant never reaches disk and requires the control to **refuse** — the control is
shown able to fail, not only to pass.

**THE HONEST LIMITATION, STATED PLAINLY: THE PLANT FIRES AT ONE LEVEL, NOT AT EVERY
LEVEL.** `main()` calls both controls on **L1 only** (`grade_vmfl063.py:1156-1158`):

```python
l1 = R["levels"]["L1"]
R["planted_zero"] = [planted_zero_tau(l1["level_dir"], l1["time_dir"]),
                     planted_zero_u(l1["level_dir"], l1["time_dir"])]
```

**L2, L3 and L1D are read by the same reader functions but no plant is driven through
their bytes.** This is consistent with the frozen pre-registration, which promises *"two
stages on two channels"* and per-**face** coverage (§8) and nowhere promises per-level
coverage — so it is **not** a departure from the freeze. It is nonetheless **weaker than
rows #42 and #43**, whose re-grade record states *"Plant fired at all three levels in
each."* Recorded here as a known limitation of this instrument for the supervisor's
read, not repaired after the fact and not written into the gate.

### 4.2 The other registered controls

| control | outcome |
|---|---|
| **Cardinality guard** (`one_match`, refuses on ≠ 1 match) | every file opened through it; no refusal. `sorted(glob(...))[-1]` appears **nowhere** in the file |
| **Numeric time-dir cross-check** (`key=float`, checked against the log's last `Time`) | agreed at all four levels |
| **AST guard** (`ast.Assert` count must be 0, run **on the grading path**, not only in selftest) | **0**, recorded in the grading record |
| **Orientation refusal** (\|τ\| < `TAU_EPS = 1e-14` at `X_SIGN_REF`) | reference face carried \|τ\| ≈ 1.4e-05, four orders above the floor |
| **Cross-instrument gate** (3 local cell widths) | held by 5–6 orders of magnitude at every level |
| **Tier-ceiling refusal** (`verdict_for_limb_a` refuses if it ever emits `PASS`) | never triggered; limb A emitted `GATE FAIL` |
| **`--selftest`** | **62 checks, 0 failures, rc 0**, `__pycache__` cleared beforehand |
| **`--verify-frozen`** | rc **0** — both blobs equal their HEAD blobs at grade time |

---

## 5. LIMB B — SERIAL DETERMINISM, `PASS`, AND WHAT IT IS WORTH

L1 and L1D are the **same discrete problem solved twice** in separate directories.
`VERIFICATION_CHARTER` §2f.3 makes this a SAME-DISCRETE-PROBLEM IDENTITY claim, where
both sides carry the same discretisation error on the same mesh, it cancels exactly, a
grid triple is irrelevant, and **`PASS` is available**.

| test | result |
|---|---|
| same converged iteration count | **yes** — 1004 and 1004 |
| sha256 `<t>/wallShearStress` identical | **yes** — `dbf1b556e489bd2c…` |
| sha256 `<t>/U` identical | **yes** — `73d37da053a7ea9d…` |
| sha256 `<t>/p` identical | **yes** — `a5ba2ad7a0c025da…` |
| `LR` bitwise equal | **yes** — both 0.610931435369616 m |

**Band: EXACT IDENTITY. No tolerance was registered and none was used.** The selftest
shows this limb **can** fail: a one-part-in-3.6e6 difference between the twins is
detected.

**This is the first time this lab has measured the premise it has been relying on.**
Every re-grade, every "byte-identical to attempt 1" and every GPU-vs-CPU comparison this
team has made rests on serial `simpleFoam` being deterministic, and until this row it
had never been measured. It cost **0.1333 core-min**. **It does not rescue the row** —
the row takes the worse limb and reads `GATE FAIL`.

---

## 6. COST — ESTIMATE VERSUS ACTUAL (CLAUDE.md rule 12)

| | predicted | actual | ratio |
|---|---|---|---|
| **total core-min** | **16** (registered §7; built table 15.4) | **13.8333** | **0.8646** (0.8983 vs 15.4) |
| L1 | 0.17 | 0.15 | 0.8824 |
| L1D | 0.17 | 0.1333 | 0.7841 |
| L2 | 1.50 | 1.2333 | 0.8222 |
| L3 | 13.55 | 12.3167 | 0.9090 |
| **$ (DERIVED, NOT MEASURED)** | **$0.013680** | **$0.011827** | — |

Cap **90 core-min**: actual is **15.37 %** of cap, **76.17 core-min** unspent. No
`CAP_OVERRUN.txt`, no `CAP_EXCEEDED`, no `ESTIMATE_OVERRUN.txt` anywhere under the run
root — swept and confirmed. The launcher's own `timeout` drew down correctly
(5400 → 5391 → 5383 → 5309 s) and never fired.

**THE AGGREGATE RATIO FLATTERS A MODEL THAT WAS WRONG IN BOTH COMPONENTS, AND THE
COMPONENTS ARE REPORTED SEPARATELY RATHER THAN LET THE 0.86 STAND AS ACCURACY.**

- **Iteration count: UNDER-predicted at every level**, by 1.34× to 1.64×
  (613→1004, 613→1004, 1381→1944, 3110→4177). Measured exponent on cells,
  L1→L2 **0.477** and L2→L3 **0.552**, against the model's 0.586 — the *exponent* was
  close; the **prefactor** was low.
- **Throughput rate: OVER-predicted.** Registered 2.837e-6 s/cell/iteration (from row
  #30's L3); measured **1.881e-6** aggregate over 441 308 160 cell-iterations and 830
  wall s — **0.663× the model**. Per level: 1.556e-6 / 1.383e-6 / 1.652e-6 / 1.920e-6.
- **The two errors have OPPOSITE SIGN and largely cancelled** (≈1.40 × 0.663 ≈ 0.93).
  A reader who saw only 0.8646 would conclude the model was good to 14 %. **It was not.**

**Waste: 0 core-min, named separately and never absorbed into the ratio.** No failed
solve, no re-run, no crash, no stall — the longest solve was 739 wall s against the
3 600 s stall convention. **Contention is named as a separate inflation, not as waste:**
`CONTENTION.txt` records load average **13.94 on 16 cores** and 3 other `python3`
processes at launch, which inflates `wall_s`; **13.8333 core-min is therefore an upper
bound** on what this family costs on a quiet box.

`cost_basis`: c7a.4xlarge at **$0.0513/core-h**, owner-stated 2026-08-21/22 —
**REPORTED-BY-OWNER, NOT MEASURED.** The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar figure above is **DERIVED**.

---

## 7. INFRASTRUCTURE NOTES (L-342 — each voids bookkeeping, none voids the physics)

- **`STATUS.VMFL063` reads `launcher_rc=0` and says so about itself:**
  `note=exit-status-of-the-launch-argv-NOT-the-solver-rc`. **That field is not evidence
  about the solver and is not used as such here.** The solver rc is the one captured
  **inside** the detached subshell — `.solver_rc` = 0 at all four levels, mirrored into
  `RUN_RC.<level>` (`rc = 0`, `state = FINISHED`, `wait_rc = 0`) — and that is what the
  comparator read at :551-554.
- **The run was orphaned for 2 days.** It completed 2026-08-28T17:55:34Z; the box shut
  down 2026-08-29T14:40Z (18 h 44 m later) and rebooted 2026-08-30T22:33:32Z. **Nobody
  graded it.** No `FAMILY_DONE.flag` exists anywhere under the run root — this is a
  bookkeeping gap in the queue-completion path, reported beside the verdict and **voiding
  nothing**: every physics-critical artefact is on disk, dated, and reproduced the grade.
- **The runner's cap check reports and does not enforce** (docketed **D559**). It did not
  matter here — the actual came in at 15 % of cap — but the real guard remains the
  launcher's own `timeout`, and that is what it was on this run.

---

## 8. WHAT THIS ROW DOES NOT CLAIM

- **It is not a statement about Ansys.** This box has no Ansys solver. Fluent's 4.16 and
  CFX's 4.05 are context and were never the gate. **That Ansys reproduced the target to
  1–4 % and this lab missed it by 40 % is a statement about this lab's case setup**, not
  about the manual.
- **It does not claim Ansys's domain.** `VMFL063_WB.wbpz` was **not opened** (sha256
  `8b037b7b79cf13b9…`). The domain is this lab's own choice — `Lu = 0.9 m`, `Ld = 1.5 m`,
  `H = 1.8 m` — disclosed with its 2.50 % blockage and **+2.564 %** free-stream
  acceleration, **whose sign of effect on LR/(2t) is not asserted** (pre-registration
  §9). **A 40 % miss is far larger than a 2.5 % blockage explains, and no attempt is made
  here to attribute it.** Why the deviation is this large is **not established by this
  row** and is not guessed at.
- **It establishes nothing about meshes finer than L3**, and the triple's `p = 0.143`
  says the asymptotic range was not reached on the three that were run.
- **It is not a credential**, and could not have been: the row ceiling is
  `GATE REACHED` by construction.
- **Nothing here is sent anywhere.** Submissions are parked; the manual is proprietary
  Ansys documentation held for this lab's private use (`CLAUDE.md` rules 7 and 8).

---

## PROVENANCE

| item | value |
|---|---|
| manual | Ansys Fluid Dynamics Verification Manual, **Release 2026 R1, March 2026**, p. 193–194 |
| title-page verification (rule 15) | **PDF read directly**, not by filename or hash: page 1 reads *"Ansys Fluid Dynamics Verification Manual / ANSYS, Inc. / Southpointe / 2600 Ansys Drive / Canonsburg, PA 15317 / Release 2026 R1 / March 2026"*; `pdfinfo` `Title: Fluid Dynamics Verification Manual`, `Pages: 290`, `Creator: DocBook XSL Stylesheets V1.76.1`, `Producer: XEP 4.22`. VMFL063 is **PDF page 207 = printed page 193**; Tables .63.1/.63.2 are **PDF page 208 = printed page 194**. Sidecar text matches the PDF verbatim on the reference, the Target 4.0 and the material/geometry table |
| pre-registration | `cases/ansys_verification/VMFL063/PREREGISTRATION.md`, blob `efdb2a8abb788c5f55bac60f10fb09816af50a30` |
| freeze commits | **`2df23798`** (v1.0) → **`3602cbf3`** (v1.1, Amendment 1 — **launcher only**) |
| comparator | `cases/ansys_verification/VMFL063/grade_vmfl063.py`, blob `fc339a79d1b0b1a5a5c6beba455e8e3f0e518d45` — **identical at `2df23798` and at `3602cbf3`**; Amendment 1 did not touch one byte of the grading instrument |
| launcher | `cases/ansys_verification/VMFL063/run_vmfl063.sh`, blob `8c3d9ec7daf76c8c0ae8a2d8c015e9050267b33e` |
| freeze re-verified at grade time | on-disk `git hash-object` == blob at `3602cbf3` for **all three** files; `--verify-frozen` rc **0** against HEAD `6d4e0d18` |
| launched / finished | **2026-08-28T17:41:41Z** / **2026-08-28T17:55:34Z**, `LAUNCH_RECORD.txt` |
| graded | **2026-08-30T22:46Z**, by `ansys-lane-opus`, no edits of any kind to the frozen files |
| run root | `verification/runs/ansys_verification/VMFL063/` (L1, L1D, L2, L3) |
| grading record | `verification/runs/ansys_verification/VMFL063/GRADING_RECORD_VMFL063.json`, sha256 `e83502f74e8314f547cd8d4a3d97472a946c2e61156d438b342853821f942155` |
| comparator exit code | **0** |
