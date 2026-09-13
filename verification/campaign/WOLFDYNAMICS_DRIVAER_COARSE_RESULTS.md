# Wolf Dynamics DrivAer, COARSE — GRADING RECORD

**VERDICT: `PASS` on G1, `PASS` on G2, `PASS` on G3. G4 (completion) holds in every
clause. This is a REPRODUCTION result. It is NOT a VALIDATION result.**

| item | value |
|---|---|
| Run | `/home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER/coarse_R1` |
| Pre-registration | `verification/campaign/WOLFDYNAMICS_DRIVAER_COARSE_PREREGISTRATION.md` |
| **Freeze commit** | **`f8a9c8a7f48a80e55be905c5caacd642c9d23796`**, 2026-09-13T18:46:37Z |
| **Freeze verified** | blob at freeze `970d40a8687bedf42f245110d37cf02a23ddd6b4`; **`git hash-object` of the live file returns the same sha.** The frozen file IS the file that graded this run |
| Launched | 2026-09-13T18:48:04Z (`LAUNCH_STAMP.txt`) — **1 min 27 s after the freeze, so the freeze precedes compute** |
| Container | Foundation OpenFOAM 9, `openfoam/openfoam9-paraview56`, container `e496573666bf…`; solver banner `Version: 9`, `Build: 9-b456138dc4bc` |
| Ranks | **4** — their `decomposeParDict numberOfSubdomains 4` and their `run_solver_fluent.sh procs=4`, unmodified |

---

## 🔴 1. THE DISCLOSURE THAT TRAVELS WITH EVERY NUMBER IN THIS DOCUMENT

**Our `postProcessing/all/0/forceCoeffs.dat` is BYTE-IDENTICAL to their shipped
`sol_logs/coarse/postProcessing/all/0/forceCoeffs.dat`.**

Verified by this lane, not relayed:

- both files **119,158 bytes**;
- `cmp` returns **rc = 0** — no differing byte;
- `diff` prints **0 lines**;
- sha256 of both: `285019ab1560ca8169d5b67ba5d7d043c28d2ae48eee0cbdc09b10753d2325b9`.

**The reader was given a planted control before that zero was believed** (rule 3). A
one-byte perturbation was written into a copy of their file at offset 119,000 and `cmp`
re-run against our output: it returned **rc = 1**, `differ: byte 119001, line 1009`. The
comparison instrument was **shown able to see a difference** before its "no difference"
was accepted as evidence.

**This is EXPECTED, and it is not an error and not a copy.** Route A ran **their binaries**
in the Foundation OpenFOAM 9 container, on **their mesh**, with **their `decomposeParDict`
at 4 ranks** and deterministic `scotch` decomposition. Identical operation order on
IEEE-754 doubles produces bit-identical output regardless of host CPU. Two independent
facts show our solver genuinely computed it rather than inheriting the file:

1. our file's mtime is **2026-09-13 19:24:37**, theirs **2022-04-20**; and
2. **our own `log.solver` prints `Cd = 0.291162651767` at `:42109`**, from the solver's own
   in-run `forceCoeffs` report — a channel that does not read their shipped file at all.

### 🔴 1.1 AND THE MEANING CHANGES BECAUSE OF IT — WRITTEN INTO THE RECORD AS REQUIRED

**Bit-identity proves the case was run VERBATIM; it CANNOT corroborate their number. We
reproduced their COMPUTATION, not independently confirmed their RESULT. Anyone citing
this run as independent agreement with Wolf Dynamics would be wrong.**

A bit-identical output carries exactly one bit of information — *nothing in our
transcription of their case diverged from theirs* — and zero bits of confirmation. An
independent confirmation would require a different mesh, a different decomposition, a
different code, or all three, and this run deliberately has none of those, because
"verbatim" was the instruction. **The strength of this result is its fidelity, and its
fidelity is precisely why it cannot corroborate.**

---

## 2. THE GATES, EACH VERIFIED FROM THE ARTIFACT BY THIS LANE

### 2.0 The column was resolved BY NAME, from the header

`postProcessing/all/0/forceCoeffs.dat` header line:

```
# Time              	Cm                  	Cd                  	Cl                  	Cl(f)               	Cl(r)
```

Parsed by name: `Cd` is at **header index 2 = column 3**. It is **not** column 2 (`Cm`)
and **not** column 5 (`Cl(f)`). **Reading a neighbouring coefficient as `Cd` cost this
lab a verdict earlier tonight**, so no column index is assumed anywhere in this grading —
the header is tokenised and `.index('Cd')` is taken.

### 2.1 G1 — endpoint reproduction: **PASS**

| | |
|---|---|
| Gate (frozen) | `\|Cd_ours(1000) − 0.291163\| / 0.291163 ≤ 2.0 %` |
| Their shipped coarse endpoint | **0.291163** |
| **Ours at `Time = 1000`** | **0.291162651767** |
| Absolute difference | 3.48233 × 10⁻⁷ |
| **Relative difference** | **1.196 × 10⁻⁶ = 0.000120 %** |
| Margin to the 2.0 % threshold | **16,700×** |
| **VERDICT** | **`PASS`** |

The registration said in advance that *"a result inside 0.5 % will be reported as such"*.
It is inside 0.5 % by four orders of magnitude — for the reason in §1, and only for that
reason.

### 2.2 G2 — their-window mean reproduction: **PASS**

| | |
|---|---|
| Gate (frozen) | `\|mean(Cd_ours, 200→1000) − 0.283631\| / 0.283631 ≤ 2.0 %` |
| Window | their own `fieldAverage timeStart 200`, no `timeEnd`, to `endTime 1000` — **registered verbatim as theirs and used unchanged** |
| Rows in the window | **801** (t = 200 … 1000 inclusive, `deltaT 1`) |
| Their shipped coarse window mean | **0.283631** |
| **Ours** | **0.283631445567** |
| Absolute difference | 4.45567 × 10⁻⁷ |
| **Relative difference** | **1.571 × 10⁻⁶ = 0.000157 %** |
| **VERDICT** | **`PASS`** |

**The averaging reader was itself controlled** (rule 3): adding +1.0 to a single row of the
window moved the computed mean from 0.283631 to 0.284880 — a shift of 1.248 × 10⁻³,
exactly 1/801. The mean is being computed over the rows it claims, by a reader that
responds to the data.

### 2.3 G3 — mesh identity: **PASS**, and it was a PREDICTION MADE BEFORE THE RUN

| | |
|---|---|
| Gate (frozen) | `fluent3DMeshToFoam` + `checkMesh` report **669,416 cells** |
| **Measured** | **669,416** — `log.checkmesh:45`, from `mpirun -np 4 checkMesh -parallel` |
| **VERDICT** | **`PASS`** |

This is the strongest of the three gates and the only one §1 does not weaken. **The number
669,416 was written into the registration at `f8a9c8a7` before any mesh was converted on
this box**, derived by counting their shipped `.msh` rather than by trusting their prose —
the same method gave their fine mesh 4,048,483 against a published *"approximately
4048000"* and the coarse 669,416 against *"approximately 660000"*. **A pre-registered
integer landing exactly is a real prediction discharged**, and unlike G1 and G2 it is
independent of floating-point determinism: a different mesh would have produced a
different integer no matter how faithfully the solver ran.

### 2.4 G4 — completion: every clause holds

| clause (frozen) | measured |
|---|---|
| `rc = 0` | **`RC=0`** — `RUN_RC.txt`, written by the wrapper from the script's own exit status |
| an `End` line | **1 occurrence** in `log.solver`, followed by `Finalising parallel run` |
| last time == `endTime` | last `Time = 1000`; `controlDict endTime 1000` |
| `ExecutionTime` count == `round(endTime/deltaT)` | **1000 == round(1000/1)** — `deltaT 1`, the unit-step case |
| field set present at 1000 | `U p k omega nut phi` **present**, plus `Q wallShearStress yPlus` and their `*Mean`/`*Prime2Mean` averages — `processor*/1000/` |
| **age guard** — every field newer than the case's launch stamp | `LAUNCH_STAMP.txt` **18:48:04.955**; `U/p/k/omega/nut` at 1000 all **19:24:37.78–.79** — every field **36 min 33 s newer** |
| No early termination | **`SIMPLE solution converged` appears ZERO times** — see §4 |

**All four gates are discharged. Nothing in this run is `NOT A RESULT`.**

---

## 3. AGAINST EXPERIMENT — STATED, AND STATED AS NOT A VALIDATION FAILURE

Their own validation document's reference table (p.19), the two TUM entries:

| reference | reported mean Cd | our endpoint 0.291163 | our window mean 0.283631 |
|---|---|---|---|
| **EXP TUM ASME** | **0.247** | **+17.88 %** | +14.83 % |
| **EXP TUM SA** | **0.243** | **+19.82 %** | +16.72 % |

**0.291163 is 17.9 % and 19.8 % above the two TUM experiments. That is stated here in the
verdict document, plainly, and not in a footnote.**

**IT IS NOT A VALIDATION FAILURE, FOR THREE REASONS THAT ARE THEIR OWN AND NOT OURS:**

1. **Their document nominates the coarse mesh for speed, not accuracy.** It selects the
   coarse mesh *"to obtain fast outcomes"* (p.20) and says only the **fine** mesh is
   *"good enough to obtain an accurate and stable solution"*. **The p.18/19 published band
   is a fine-mesh-grade claim.** Grading a coarse-mesh number against it compares two
   different things.
2. **Their own convergence criterion never fired.** `system/fvSolution` carries
   `residualControl { p 1.0e-3; U 1.0e-3; k 1.0e-3; omega 1.0e-3; }`, and
   **`SIMPLE solution converged` appears zero times in 1000 iterations of `log.solver`.**
   The run stopped because it hit `endTime`, not because it converged. **A number taken
   from a solve that did not meet its own stopping criterion is not a validation datum**,
   and this was registered as a disclosure *before* the run (§7 of the registration), not
   discovered afterwards.
3. **There is no published converged coarse comparand to fail against.** §6c of the
   registration establishes it: the gate for this rung is their **shipped coarse
   artifacts**, explicitly *"a reproduction target, explicitly not a validation target"*.

**THE CORRECT READING, IN ONE LINE: this run reproduces, to the last byte, a solve its own
authors published as a fast-and-inaccurate one. Its agreement with them is total; its
agreement with the wind tunnel is 18–20 % off, and both facts are properties of their
coarse case, not findings of ours.**

**The §5 reporting condition of the registration is attached here, as it is binding on
every Cd from this run:** this is the original TUM DrivAer — a **half model**, 30 m/s,
nu = 1.5881327800829875e-05, reference area 1.073476 m², half-model confirmed structurally
(`ffminy type symmetry` in both `0_org/U` and the post-mesh re-typing). **It is a DIFFERENT
experiment from the full-scale 38.889 m/s configuration this lab's other DrivAer gates are
anchored on, and no Cd from this run may be compared against this lab's other DrivAer band.**

**One open discrepancy in their published material is carried forward, unresolved and not
resolved in our favour** (registration §6b): the shipped case has Setup 2 boundary
conditions (rotating wheels + moving ground) whose published Cd is 0.2426, while their
shipped **fine** solution averages 0.256412 — 0.19 % from Setup 3 and 5.7 % from Setup 2.
Either the shipped solutions correspond to a different table row than their boundary
conditions imply, or the table was generated from runs other than the shipped ones. **We do
not know which, and we changed nothing to make it agree.**

---

## 4. RENDERS — SANAA'S STANDING PARAVIEW RULE, DISCHARGED ON COMPLETION

Rendered by `scripts/render_openfoam_3d_paraview.py` under `xvfb-run pvbatch`, from the
case's own `constant/polyMesh` and its own `1000/` time directory. Vehicle patches
`body2`, `ruotaant`, `ruotapost`; `--up z` (automotive convention — a generic camera
renders this car upside down).

| artifact | what it shows | measured |
|---|---|---|
| `RENDERS/wd_coarse_R1_mesh_surface.png` + `.json` | the coarse surface mesh, solid colour, **not** coloured by any field | 32,913 faces rendered, ink 0.1096 |
| `RENDERS/wd_coarse_R1_field_p_surface.png` + `.json` | surface pressure at `Time = 1000` | range **−1142.265 … +472.490 m²/s²** (**KINEMATIC**, from the field file's own `dimensions` header — *not* Pa; the solve is incompressible) |
| `RENDERS/wd_coarse_R1_field_yPlus_surface.png` + `.json` | wall-function y⁺ at `Time = 1000` | range **1.625 … 1976.064**, ink 0.1141 |

All paths are under
`/home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER/coarse_R1/RENDERS/`.

**Three controls, all measured, none assumed:**

1. **Face-count guard.** Rendered surface cells **32,913** == Σ`nFaces` over the three
   rendered patches, **32,913**. Equality measured, not assumed — a render that silently
   decimated or triangulated would stop.
2. **Planted colour control** (rule 3). The colour transfer function was collapsed to a
   single value and the **saved PNG read back off disk**: **90.12 %** of the 236,251 body
   pixels changed, against a 0.1 floor. A renderer that was not actually colouring by the
   field could not have produced that.
3. **The graded tree was proven untouched.** The script censuses the case before and after
   each render; `graded_tree_census_before == graded_tree_census_after` in all three
   sidecars. **Independently re-verified by this lane after every render was finished:**
   `postProcessing/all/0/forceCoeffs.dat` still hashes to
   `285019ab1560ca8169d5b67ba5d7d043c28d2ae48eee0cbdc09b10753d2325b9` and still `cmp`s
   rc = 0 against their shipped file.

🔴 **TWO HONEST DISCLOSURES ON THE RENDERS.**

- **`reconstructPar -time 1000` was run to produce them.** The solve is decomposed and the
  render script has no decomposed-case reader. It was run **in the same container, with the
  same invocation and the same uid** as the graded run, writing only a new `1000/`
  directory. **It is post-processing of a completed solve and it altered no graded
  artifact** — the `postProcessing` census is identical before and after, and it is the
  same operation their own `run_postprocess.sh` performs by unpacking
  `solutions/coarse_1000.tar.gz`. Its log is deliberately named
  **`log.reconstructPar_render`** — not `log.reconstructPar` — so that no later reader can
  mistake it for a stage of the graded pipeline. Their `run_all_fluent.sh` calls
  `fluent3DMeshToFoam`, `decomposePar`, `checkMesh`, `renumberMesh`, `potentialFoam` and
  `simpleFoam`, and nothing else; **the graded pipeline is exactly those six.**
- **`pvbatch` exits rc = 1 on this box even when the render succeeds.** The failure is
  `X Error … GLXBadContext` at GLX teardown, printed **after** the PNG is written. Each
  render's own log line reads `WROTE … (32913 faces, ink …, guard PASS, graded tree
  untouched)` and the sidecar JSON is complete. **The rc is disclosed rather than
  suppressed**; the evidence that the renders are good is the guard output and the
  sidecars, not the exit status. Related to L-545 (this ParaView build is X11/GLX-only).

**One reading corrected while making them, because it would otherwise have looked like a
contradiction in this record.** `log.solver` prints `max() of p = 1142.26542419` and
`min() of p = 3.82094215419e-06`, while the render measures the field's range as
**−1142.265 … +472.490**. Both are right: their `minmaxdomain_scalar` function object sets
`writeLocation true`, under which OpenFOAM reports **magnitude** extrema so a location can
be named — so their `max` is `max|p|` and their `min` is `min|p|`. The **signed** range was
measured directly by two independent ParaView reads, of the internal mesh and of the body
patches, and both return `(−1142.265380859375, 472.4900207519531)`. The 1142.265 is a
**suction** peak, Cp ≈ −2.54 against q = ½U² = 450 m²/s².

---

## 5. COST — MEASURED IN CORE-MINUTES, DOLLARS DERIVED

| stage | ranks | measured | core-minutes |
|---|---|---|---|
| `simpleFoam` | 4 | `ExecutionTime = 2167.01 s` (`ClockTime = 2167 s`) | **144.467** |
| `potentialFoam` | 4 | `ExecutionTime = 5.07 s` | 0.338 |
| mesh convert + `decomposePar` + `checkMesh` + `renumberMesh` | 1–4 | 20.76 s of pipeline wall, not separately instrumented — **bounded, not measured** | ≤ 1.38 |
| **total, gross, at the 4 ranks held for the whole pipeline** | | 2,192.83 s wall (18:48:04.955 → 19:24:37.79) | **146.189** |

- **Predicted in the frozen registration §9: 300 core-minutes.**
- **Actual gross: 146.189 core-minutes. Ratio actual/predicted = 0.487.**
- **Cleaned = gross.** No stage approaches the 3600-s stall rule; nothing was discarded;
  **no waste to name.**
- **Dollars: 146.189 / 60 × $0.0513 = $0.125 — DERIVED, NOT MEASURED** (predicted $0.257,
  also derived). Rate owner-stated for c7a.4xlarge; this box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER.md` §5).

**Gap attribution — misprediction, and the cause is named rather than absorbed.** The
estimate anchored on **their published 2022 `ExecutionTime = 3905.83 s` at 4 ranks =
260.4 core-minutes** and treated a wall time from someone else's silicon as transferable.
Our solver did the **bit-identical arithmetic in 2167.01 s — 1.802× faster** on
c7a.4xlarge. **This is not contention and not waste:** `ExecutionTime = 2167.01 s` against
`ClockTime = 2167 s` shows essentially zero stall despite a busy box, because the 4 ranks
were reserved. **The lesson for the next estimate is specific: a published wall time is a
hardware-bound figure, and porting it to this box without a measured scale factor costs
roughly 2× in the conservative direction. The fine rung now has one — 1.802×.**

---

## 6. WHAT THIS LANE COULD NOT VERIFY

- **Nothing here corroborates Wolf Dynamics' number.** §1.1 is the load-bearing limitation
  of this entire document and it is not softened anywhere in it.
- **The Setup 2 / Setup 3 discrepancy in their published table (§3) is not resolved**, and
  this run does not bear on it: it is a coarse reproduction and the discrepancy lives in
  their fine-mesh results.
- **The mesh-conversion, decompose, checkMesh and renumber stages carry no `ExecutionTime`
  line in their logs**, so their 20.76 s share of the cost is **bounded from the pipeline
  wall clock, not measured.** The bound is stated as a bound in §5.
- **The 18–20 % gap to TUM is not attributed to any specific mechanism here.** §3 says why
  it is not a validation failure; it does **not** claim to know how much of it is mesh
  resolution, how much is the unconverged residual, and how much is the k-omega closure.
  Separating those needs the fine rung, which is registered next.

---

*Graded by a cfd `lab-lane`, 2026-09-13, against the pre-registration frozen at
`f8a9c8a7` and verified by hash to be the file that ran. Contains no submission and no
external communication. Nothing leaves the box.*
