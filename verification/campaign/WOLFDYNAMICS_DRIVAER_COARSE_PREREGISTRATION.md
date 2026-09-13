# PRE-REGISTRATION — Wolf Dynamics DrivAer, COARSE, verbatim reproduction

- Campaign: `WOLFDYNAMICS_DRIVAER`  Rung: `coarse_R1`
- Team: cfd    Lane: lab-lane    Supervisor: cfd-supervisor
- Status at freeze: **NO COMPUTE HAS RUN.** Run directory
  `/home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER/coarse_R1` contains the staged
  case only: no `0/`, no `processor*/`, no `log.*`, no time directory.
- Governing rule, Sanaa's: **VERBATIM.** Dictionaries copied, never re-typed; nothing
  improved, tidied, modernised or adapted.

---

## 0. THE ONE LINE, VERBATIM AS SANAA GAVE IT

> occDrivAerStaticMesh mesh tarball unreachable (Zenodo 403) — Wolf Dynamics case used verbatim instead.

---

## 1. THE CASE, ITS SOURCE, AND ITS HASHES

Published source, already on disk, **not re-downloaded** for this registration:

- Archive root: `/home/ubuntu/upstream/published-openfoam-setups/wolfdynamics-drivaer/`
- Per-file manifest: `/home/ubuntu/upstream/published-openfoam-setups/SHA256SUMS.wolfdynamics-drivaer.txt`
- In-repo pointer: `docs/PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md`, committed at `799c88e78`
- **Manifest verified against disk at freeze time: 101 of 101 files `OK`, 0 failures.**

Staged run directory: `/home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER/coarse_R1`
(outside git; the case is multi-GB — `mesh_coarse.msh` alone is 128,008,411 bytes).

**"Verbatim" is a fact with a sha256, not an intention.** Two independent proofs, both
taken at freeze time:

1. All 16 dictionaries and initial-condition files (`system/*`, `constant/transportProperties`,
   `constant/turbulenceProperties`, `0_org/*`) hashed in the published source and again in
   the staged copy. `diff` of the two sha256 lists: **identical, 0 differing hashes.**
   Lists retained at `dicts_SOURCE.sha256` / `dicts_STAGED.sha256` and reproduced in §10.
2. The staged copy re-checked against the **published manifest** with paths rebased:
   **48 of 48 `OK`, 0 failures.**

Validation document (Sanaa's ruling — it carries the band):

- Filed at `docs/papers/benchmark_test_cases/guerrero_2022_drivaer_validation_wolfdynamics.pdf`
  with sidecar `.txt`, per FILING_CHARTER.
- sha256 `510569660b16416423300d85e8fd173879731863ee71de88a91a8a744bcbc734`, byte-identical
  to the archive copy.
- **Title-page verified per CLAUDE.md rule 15** — not by filename, not by hash. Page 1 reads
  "Drivaer validation case"; document properties give Author `joegi`, 25 pages, created
  2022-04-27. The author string `joegi` is corroborated inside the case itself: the shipped
  solver log records `Case : /home/joegi/OF_training/UNISA/COURSE/session2/Xdrivaer`.

---

## 2. ROUTE DECISION — ROUTE A, AND THE TRANSLATION TABLE IS EMPTY

Their case is OpenFOAM **9, Foundation** (openfoam.org). This box's native install is
**v2606, ESI** (openfoam.com) — a different fork.

**ROUTE A TAKEN: run their case unmodified inside a Foundation OpenFOAM 9 container.**

- Image `openfoam/openfoam9-paraview56:latest`, digest
  `sha256:eb76be2b208872e960ad8e30097721e40d94473347c6f87a5157452538286024`, 3.98 GB, pulled
  to this box. Verified in-container: `WM_PROJECT_VERSION=9`, build `9-b456138dc4bc`.
- Every utility their scripts invoke is present in the container: `fluent3DMeshToFoam`,
  `simpleFoam`, `potentialFoam`, `renumberMesh`, `decomposePar`, `checkMesh`, `blockMesh`,
  `snappyHexMesh`, `foamCleanTutorials`, `foamDictionary`, `surfaceFeatures`, `mpirun`.

**TRANSLATION TABLE (their keyword | ours): EMPTY. Zero keywords translated.**
That is the entire point of Route A and it is why it was taken.

**Route B was costed and rejected, and the reasons are recorded because they are findings
about this box, not merely about the route not taken.** Had the case been forced onto v2606:

- `surfaceFeatures` **does not exist** in v2606 (ESI ships `surfaceFeatureExtract`). Their
  `run_mesh_shm.sh` would fail on its first meshing command.
- `fvConstraints` is **not read by v2606 at all** — zero occurrences in the entire v2606
  source tree, and `simpleFoam.C` includes only `fvOptions.H`. Their `system/fvConstraints`
  would have been **silently ignored**, not refused. This is the exact silent-swallow trap
  the supervisor warned of, and it is load-bearing in their method: their own validation
  document, page 15, describes this limiter as "recommended to follow this practice to avoid
  reaching unrealistic values and eventually divergence". Losing it silently would have been
  an undisclosed change to their physics.
- Correction recorded against my own earlier reading: I first reported `skewCorrected`
  (their `interpolationSchemes` default) as absent from v2606. **That was wrong** — my search
  was depth-limited. It is present at
  `src/finiteVolume/interpolation/surfaceInterpolation/schemes/skewCorrected`. Recorded
  because a false blocker in a frozen document is worse than no document.

---

## 3. MESH — THEIRS, SHIPPED, NOT GENERATED HERE

Sanaa's ruling: if a mesh ships, theirs wins, and say so. **It ships. We use theirs.**

- `drivaer_coarse/mesh/mesh_coarse.msh`, 128,008,411 bytes, dated 2022-04-20, in the
  verified manifest.
- Cell count read from the Fluent header declaration `(12 (0 1 a36e8 0 0))`:
  **669,416 cells**; points `(10 (0 1 b42a6 0 3))` = 737,958; faces `(13 (0 1 1fa29f 0 0))`
  = 2,073,247.
- The parse method is corroborated on the fine mesh: its header gives `0x3dc663` =
  **4,048,483** cells, against the validation document's stated "approximately 4048000
  cells" (p.20). The same method gives coarse 669,416 against their stated "approximately
  660000 cells" (p.20). Both agree.
- The count will be confirmed independently by `fluent3DMeshToFoam` and `checkMesh` in-run;
  if the run disagrees with 669,416, the run is the authority and this line is struck by addendum.

**We therefore execute their `run_all_fluent.sh` path** (`run_mesh_fluent.sh` +
`run_solver_fluent.sh`), which is the path their own README and their validation document
p.20 nominate: "If you do not want to generate the mesh from scratch, you can use the
pre-generated meshes." **No `blockMesh` and no `snappyHexMesh` are run.** Their SHM path
remains registered but unexecuted, and this removes the whole geometry-and-meshing class of
deviation: the mesh is theirs, byte-for-byte.

---

## 4. THE FOUR CONDITIONS, CARRIED FORWARD AND REGISTERED

**Condition 1 — their STLs are not watertight.** `body2.stl` carries **1,101 illegal
triangles and 550,895 unmatched edges**, measured with `surfaceCheck` by a sibling lane and
carried here unmodified. **This is a property of the published case and is registered as
one. It is not repaired.** Note its operative scope: because we take their shipped mesh
(§3), the STLs are not consumed by this run at all. The condition is registered because it
is true of the case, and it becomes operative the moment anyone runs their SHM path.

**Condition 2 — version disagreement, settled by their own shipped log.** Their web page
says OpenFOAM 9; their `snappyHexMeshDict`, `controlDict`, `decomposeParDict`,
`transportProperties` and `turbulenceProperties` headers say `Version: 7`; their
`blockMeshDict`, `fvSchemes`, `fvSolution`, `meshQualityDict`, `surfaceFeaturesDict` and
`fvConstraints` headers say `Version: 9`. **The shipped log is the authority** and it reads
`Build : 9-6adb71a2e61d`. **Why the log wins:** a dictionary header is an inert comment that
OpenFOAM never reads and that survives copy-paste between case generations — the `Version: 7`
headers sit on files whose *content* is demonstrably post-7 — whereas the build string is
emitted by the binary that actually executed and cannot be stale with respect to that
execution. Corroborating: `system/fvConstraints` exists at all, and `fvConstraints` is a
Foundation 8/9 construct absent from 7.
**Named deviation:** we run OpenFOAM 9 build `9-b456138dc4bc`; they ran 9 `6adb71a2e61d`.
Same fork, same major version, different patch commit. Not zero, and named.

**Condition 3 — the six farfield patches typed `wall`. VERIFIED MYSELF; RESOLVES.**
`system/blockMeshDict` does type all six `ff*` patches `type wall`. I verified in
**both** of their mesh scripts that this never reaches the solver. `run_mesh_fluent.sh` —
**the script this run actually executes** — re-types them after meshing:
`ffminx`→`patch`, `ffmaxx`→`patch`, `ffminy`→`symmetry`, `ffmaxy`→`patch`,
`ffminz`→`wall`, `ffmaxz`→`patch`, then removes `inGroups` from all six.
`run_mesh_shm.sh` carries the identical block. Only `ffminz`, the ground, remains `wall`,
which is correct for it. **Resolves, does not block.** Note the further detail that the
`wall` typing is doubly inert on our path: we never run `blockMesh`, so their
`blockMeshDict` patch types are not even created — the patch types come from the Fluent
mesh and are then re-typed by the same `foamDictionary` block.

**Condition 4 — 0.2912 is not a converged reference, and it may not be used as one.**
Registered as prohibited. Confirmed here from their own shipped artifact
`sol_logs/coarse/postProcessing/all/0/forceCoeffs.dat`:
- Cd at iteration 1000 = **0.291163** (0.2912 as reported).
- Single-iteration change at 1000: |0.291163 − 0.292027| = **8.64e-04**, matching the
  8.6e-04 carried in.
- Mean slope over the last 100 iterations: **5.52e-05 per iteration**. Both figures are true
  and both are stated so neither is mistaken for the other.
- Cl is still crossing zero at iteration 1000 (+1.87e-03 at 999, −4.44e-03 at 1000).
- **Independent corroboration from their own setup:** their `fvSolution` sets
  `residualControl` at 1e-3 on p, U, k and omega. Their log ran the full 1000 iterations to
  `End` — so **their own convergence criterion never fired.** Their configuration agrees
  with us that it had not converged.

---

## 5. THE CONDITION THAT MUST BE STATED SO NOBODY MISREADS IT LATER

**This is the original TUM DrivAer: a HALF model, 30 m/s, nu = 1.5881327800829875e-05,
reference area 1.073476 m². It is a DIFFERENT experiment from the full-scale 38.889 m/s
configuration this lab's other DrivAer gates are anchored on. Reproducing them exactly
reproduces THEIR experiment. That is the point of this exercise and it is legitimate — but
no Cd produced by this run may be compared against this lab's other DrivAer band.**

Half-model confirmed structurally, not assumed: the domain is y ∈ [0, 4] with `ffminy`
carrying `type symmetry` in both `0_org/U` and the post-mesh `foamDictionary` re-typing.

---

## 6. WHAT THIS RUN IS EXPECTED TO REPRODUCE — THE COMPARANDS

Sanaa's ruling is that their published Cd against TUM data is the band. That ruling is
honoured, **and it requires one distinction stated plainly, because their published band is
not a coarse-mesh number.**

**6a. Their published validation table** (filed PDF, p.18 and p.19), "Mean drag coefficient
(OpenFOAM)":

| Case | Description | Cd |
|---|---|---|
| Setup 1 | No rotating wheels – Moving ground | 0.2660 |
| Setup 2 | Rotating wheels – Moving ground | 0.2426 |
| Setup 3 | Rotating wheels – No moving ground | 0.2569 |
| Setup 4 | No rotating wheels – No moving ground | 0.2630 |

**Their reported reference data** (p.19), against which they validate:

| Reference | Reported mean Cd |
|---|---|
| Ref.[1] – EXP PVT UC | 0.243 |
| Ref.[1] – EXP PVT | 0.228 |
| Ref.[1] – EXP TUM ASME | 0.247 |
| Ref.[1] – EXP TUM SA | 0.243 |
| Ref.[1] – NUM US:200M | 0.235 |
| Ref.[1] – NUM (EWT) | 0.214 |
| Ref.[2] | 0.258 |

Ref.[1] = R. Yazdani, *Steady and Unsteady Numerical Analysis of the DrivAer Model*,
Chalmers University of Technology, MSc thesis, 2015. Ref.[2] = *Experimental Comparison of
the Aerodynamic Behavior of Fastback and Notchback DrivAer Models*, SAE 2014-01-0613.
Their note, p.18/19: all reported results are the fastback, smooth-underbody model.

**6b. Which number is which — measured, not inferred.**

The shipped case configuration is **rotating wheels** (`ruotaant`, `ruotapost`:
`rotatingWallVelocity`, omega −94 rad/s) and **moving ground** (`ffminz`: `fixedValue
(30 0 0)`). By the table's own labels that is **Setup 2 = 0.2426**.

Measured from their shipped FINE artifacts, over their own `fieldAverage` window
(`timeStart 200`, run to 10000): **mean Cd = 0.256412**, stable across sub-windows
(0.2542 to 0.2564). That is **0.19% from Setup 3 (0.2569)** and **5.7% from Setup 2
(0.2426)**, while the shipped fine case has the Setup 2 boundary conditions.

**This is a discrepancy in the published material and it is registered as an open
discrepancy, not resolved in our favour and not quietly assigned to whichever row is
convenient.** Either the shipped solutions correspond to a different row than their boundary
conditions imply, or the table's rows were generated from runs other than the shipped ones.
**We do not know which, we did not change anything to make it agree, and a reproduction that
lands near 0.2569 must not be written up as reproducing 0.2426.**

**6c. The coarse mesh has no published converged comparand, and the 0.2912 caveat belongs
to the shipped log, not to their published result.** Their validation document nominates the
coarse mesh "to obtain fast outcomes" (p.20) and says only the fine mesh is "good enough to
obtain an accurate and stable solution". The published table is a fine-mesh-grade result.
**So the 0.2912 prohibition of §4 applies to the shipped coarse log; it does not touch the
p.18/19 band, which is a separate and converged claim about a different mesh.**

**6d. THE COMPARANDS THIS RUN IS GATED ON are therefore their own shipped COARSE artifacts
— a reproduction target, explicitly not a validation target:**

| Quantity | Their shipped coarse value | Source |
|---|---|---|
| Cd at iteration 1000 | **0.291163** | `sol_logs/coarse/postProcessing/all/0/forceCoeffs.dat` |
| Mean Cd over their own window (200→1000) | **0.283631** | same file, their `fieldAverage` `timeStart 200` |
| Iterations completed | 1000, terminating at `End` | `sol_logs/coarse/log.solver` |
| Ranks | 4 | same log, `nProcs : 4` |

The p.18/19 band is carried in this registration as the **fine-mesh comparand for the next
rung** and as disclosure context for this one. It is not a gate on the coarse run.

---

## 7. THEIR AVERAGING IS REGISTERED AS THEIRS

Their averaging is a **fixed window, not a detection rule**: `controlDict` `fieldAverage`
with `timeStart 200`, no `timeEnd`, running to `endTime 1000`. **That window is registered
verbatim and is used unchanged.** This lab's stationarity gate is **not** substituted into
their case.

**Our gate is reported separately, as a disclosure, and alters nothing.** After the run we
will additionally report, beside their number and never in place of it, whether their
converged result would pass this lab's stationarity bar. On their own shipped coarse data it
would not (§4) — that disclosure is already owed and is already made.

---

## 8. THE GATE

Frozen before compute. Let `Cd_ours` be from our run's
`postProcessing/all/0/forceCoeffs.dat`, computed by their unmodified `all` forceCoeffs
function object.

- **G1 (endpoint reproduction).** `|Cd_ours(1000) − 0.291163| / 0.291163 ≤ 2.0%`
  → **PASS**, else **GATE FAIL**.
- **G2 (their-window mean reproduction).** `|mean(Cd_ours, 200→1000) − 0.283631| / 0.283631 ≤ 2.0%`
  → **PASS**, else **GATE FAIL**.
- **G3 (mesh identity).** `fluent3DMeshToFoam` + `checkMesh` report **669,416 cells**
  → **PASS**, else **GATE FAIL** (their mesh is not the mesh we ran).
- **G4 (completion).** rc = 0; an `End` line; last time == `endTime` = 1000; the full field
  set present at 1000; every field at 1000 newer than the case's own `0/T`-equivalent launch
  stamp. Any clause failing → **NOT A RESULT**.

Band rationale, stated before the answer is known: with their mesh, their dictionaries,
their rank count and the same OpenFOAM major version, agreement should be well inside 0.5%.
2.0% is set to absorb the one named deviation — their build `6adb71a2e61d` against ours
`b456138dc4bc` — plus CPU-dependent floating-point summation order. **A result inside 0.5%
will be reported as such; the gate does not get widened after the fact, and it does not get
narrowed either.**

**Reporting condition, binding:** any Cd from this run is reported with the §5 line attached.
It is never compared to this lab's other DrivAer band.

---

## 9. RANKS, COST AND CAP

**Ranks: 4.** Their `run_solver_fluent.sh` and `run_mesh_fluent.sh` set `procs=4` and their
`decomposeParDict` sets `numberOfSubdomains 4`. Their own shipped log confirms they ran at
`nProcs : 4`. **Taking 4 is the verbatim choice, not a concession** — it is strictly more
faithful than the 24 ranks offered, because changing the decomposition changes the scotch
partitioning and the GAMG agglomeration built on it. Choosing 24 would have been a
deviation; choosing 4 is zero deviation, and it also adds nothing to a box at 84/96.

**Cost, pre-registered as rule 12 requires.** Their published coarse run: `ExecutionTime =
3905.83 s` at 4 ranks = **260.4 core-minutes** on their 2022 hardware. Adding
`fluent3DMeshToFoam` (serial), `decomposePar`, `checkMesh`, `renumberMesh` and
`potentialFoam` (10 non-orthogonal correctors):

- **Predicted: 300 core-minutes.**
- Derived dollars at the recorded c7a.4xlarge rate of $0.0513/core-h:
  300/60 × 0.0513 = **$0.257 — DERIVED, NOT MEASURED.** This box cannot read its own
  billing (COMPUTE_BUDGET_CHARTER §5); the rate is owner-stated.
- Actual core-minutes will be taken from the run's own `ExecutionTime` and compared against
  this 300 in `docs/COST_CALIBRATION.md` at completion, with the ratio actual/predicted and
  the gap attributed — rule 12's calibration clause. Contention is expected and will be
  named separately from misprediction, never absorbed into the ratio.

**Cap: none.** Sanaa's ruling of 2026-09-12, directive #17: no run is stopped by a time or
budget cap. The cost above is stated because rule 12 requires every run to be costed; it is
not a stop condition.

---

## 10. THE SINGLE LINE ON DEVIATION

**Every deviation from their files is either ZERO or NAMED below. There is no third category.**

**ZERO — proven by sha256, §1:** all 16 dictionaries and initial fields
(`system/blockMeshDict`, `controlDict`, `decomposeParDict`, `fvConstraints`, `fvSchemes`,
`fvSolution`, `meshQualityDict`, `snappyHexMeshDict`, `surfaceFeaturesDict`;
`constant/transportProperties`, `constant/turbulenceProperties`; `0_org/U`, `k`, `nut`,
`omega`, `p`). Their mesh, byte-identical. Their run scripts, executed as written. Their
rank count. Their averaging window. Their `residualControl`. **Keyword translations: zero.**

**NAMED — the complete list, and it has two entries:**

1. **OpenFOAM 9 build `9-b456138dc4bc` (ours) against `9-6adb71a2e61d` (theirs).** Same
   fork, same major version, different patch commit. No Foundation 9 build at their exact
   commit is available to this box.
2. **Execution inside a container** (`openfoam/openfoam9-paraview56`) rather than on a bare
   host, and on c7a.4xlarge hardware rather than theirs. Affects timing and
   floating-point summation order; affects no dictionary value.

Nothing else differs. If anything else is found to differ, it is disclosed by dated addendum
under CLAUDE.md rule 2 and it is never silently absorbed.

**A value that looked wrong to me and was NOT changed**, per the standing instruction to
record rather than correct: `snappyHexMeshDict` `addLayersControls` contains both
`minMedialAxisAngle 90` and `minMedianAxisAngle 90` — the second is a misspelling of the
first and OpenFOAM will silently ignore the unrecognised key. **Recorded, not repaired.**
It is inert on this run (no `snappyHexMesh` is executed) and becomes operative on their SHM
path.

---

## 11. EXECUTION PLAN, FROZEN

Working directory `/home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER/coarse_R1`, bind-mounted
into `openfoam/openfoam9-paraview56:latest`, running **their scripts unmodified**:

    sh run_mesh_fluent.sh     # foamCleanTutorials; 0_org -> 0; fluent3DMeshToFoam; 12x foamDictionary
    sh run_solver_fluent.sh   # 0_org -> 0; decomposePar; checkMesh; renumberMesh; potentialFoam -writep; simpleFoam

equivalently their `run_all_fluent.sh`, which is exactly those two in order.

**Nothing in their scripts is skipped, reordered, or adapted.** Reviewed against this lab's
rules before freezing: their `foamCleanTutorials` acts only inside the staged copy; the
pristine archive at `/home/ubuntu/upstream/` is never written to and its integrity is
re-verified after the run. Liveness will be read from rank pids and log mtime, never from a
recorded pid or a log's contents.

---

## 12. SIGN-OFF

Drafted by lab-lane. **Frozen by cfd-supervisor before compute — this is the supervisor's
personal check under SUPERVISION_CHARTER §3 and it is not delegable.**

Launch is authorised only after this file is committed and its committed blob hash matches
the file on disk.

---

## APPENDIX A — THE 16 FROZEN HASHES (identical in source and staged copy)

```
040e4ee42ee3807ad64ef77c2af21fa8004aae317b14777f653c2f76917f1cc4  0_org/U
7912c5e28fcc9c706c39e56e9dc089367a7b73779e98ca635c84911a724bd4b4  0_org/k
85dd3aec372f67340c6b5421755c4f08f97646ebe6a91754a302de09cb200c46  0_org/nut
20f32d1ad7617a17f426dd938efa24024419535336406a9557848cf90c20c273  0_org/omega
d43c0b0f061dfe680fa3d516a80e6d674b45ab098072d4495d85c0e65148a06b  0_org/p
917ba87a40e207c785ab06471c59d51060533d472208799d5e61d92bb352c86a  constant/transportProperties
716ca7e0533b61dcc9df1b274a46e0ffdf923951ff4030091c8cd40bfcd379a7  constant/turbulenceProperties
6226fc88b6cdac40789574edbd2684eb8652395364057a71a27422616bac5080  system/blockMeshDict
fdd80e811c935cf11efadcce0b9571968723eed2ebd05326c01d1cf0de0aed46  system/controlDict
46f7b439c2a5c0d1c744769c236070365aafa2a2529a2703c40967d827d8eb7c  system/decomposeParDict
96cce6dc5a83ecb95a77f11b3ad7705c081683794b718e6f4fe74725c6006b38  system/fvConstraints
a7be7c65deccb38426e24ff9fa046ba2ed0efa1dba83dbc20e63bb02b2491e17  system/fvSchemes
10d8b6fa1dc07d9a0892759743940cca7c7b96db647bd648369ed60ab61a7178  system/fvSolution
2a3a5de816e36ed715b774516e36bb5eda677bd911acdd4e427fd16140cc4664  system/meshQualityDict
15c95efb0633bdb2df49c16a8f54fcbf53d745bb7bc44d816cfd15de17134593  system/snappyHexMeshDict
8f819a3edaf44c9ed673986f1f0485974f48fbe53e107b6762a9abf9aa22f544  system/surfaceFeaturesDict
```

Taken at freeze time in the staged run directory. Byte-identical to the same 16 files
in `/home/ubuntu/upstream/published-openfoam-setups/wolfdynamics-drivaer/drivaer_coarse/`.
These will be re-hashed after the run; any change is a rule-6 violation and voids the result.

## APPENDIX B — FREEZE-HEADER PROOF: NO COMPUTE HAS RUN

```
staged dir: /home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER/coarse_R1
time dirs (0/ or numeric): 0
processor* dirs:           0
log.* files:               0
constant/polyMesh:         ABSENT
```
