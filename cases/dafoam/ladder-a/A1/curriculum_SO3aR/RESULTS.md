# SO-3aR — RESULTS

**Status: NOT FILED ANYWHERE.** This record discusses a DAFoam failure mode and an
untested question about an upstream tutorial. Nothing here is filed, sent, posted,
uploaded, registered or commented upstream by any agent (`DAFOAM_CHARTER.md` §10;
`CLAUDE.md` rule 7). Filing is Sanaa's decision alone. This is **not** a defect
report and no defect report is prepared by this item — the cause found is a **lab
regression**, and the upstream question below is explicitly **OPEN and UNTESTED**.

**Item:** `SO3aR` — A1, NACA0012, alpha multipoint gradient.
**Written:** 2026-08-31, after the chain died. **Freeze:** `977f3d9b`
(`cases/dafoam/ladder-a/A1/curriculum_SO3aR/PREREGISTRATION.md`; addendum A-1 at
`fc9cdf0f`). The frozen document is **not edited by this record** — gates are
CLOSED and this file is a results record, not an amendment. Verified at write time:
the worktree `PREREGISTRATION.md` blob is `4461315446…`, byte-identical to
`HEAD:cases/dafoam/ladder-a/A1/curriculum_SO3aR/PREREGISTRATION.md`.

---

## 1. Item verdict

# NOT A RESULT

`NOT A RESULT` is the item verdict, from the fixed vocabulary of `CLAUDE.md` rule 1.

**The stop marker's `"verdict": "PENDING"` is NOT the item verdict and must not be
read as one.** `PENDING` is a **display/queue state** (`CLAUDE.md` rule 1;
`VERIFICATION_CHARTER.md` §9; `REPORTING_CHARTER.md` §2 rule 5 reserves
`PENDING: <path>`) — it is what the stop-marker writer emits when it cannot find a
readable comparator verdict at the registered address, and the marker says so
itself in the same object:

> `"verdict_source": "NO READABLE COMPARATOR VERDICT AT THIS ADDRESS"`
> — `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient/SO3aR_STOP_MARKER.json` [MEASURED]

The verdict is `NOT A RESULT` on two independent grounds, both on disk:

1. **The chain driver wrote it.** `STATUS.chain` line 5:
   `chain=NOT A RESULT declared=5 executed=1 chain_rc=1 stamp=20260831T202215Z`
   [MEASURED] — `…/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient/STATUS.chain`.
2. **The frozen comparator refused.** `grader_rc=2`, and the grade output reads
   `NOT A RESULT -- the comparator REFUSED`, `{"REFUSE": "G1", "detail":
   {"C3_artefact_absent": "…/X-S/so3ar_X.json", "arm": "X-S"}}` [MEASURED] —
   `…/SO3aR_grade_20260831T202215Z.out`. The registered per-arm artefact
   `X-S/so3ar_X.json` was never written because the arm died before its final
   write; the comparator refused rather than degrading, which is the required
   behaviour (`CLAUDE.md` rule 4).

**No gate was reached.** No row of the registered two-row verdict exists. See §5.

---

## 2. Chain state

| field | value | source |
|---|---|---|
| `chain_rc` | **1** [MEASURED] | `STATUS.chain`; `launcher.queue.out` final line |
| arms declared | **5** — `[MESH X-S F-S X-P F-P]` [REGISTERED] | `PREREGISTRATION.md` §4; echoed `STATUS.chain` line 1 |
| arms executed | **1** (plus MESH) | `STATUS.chain` |
| truncated | **true**, `stages_short: 4` [MEASURED] | `SO3aR_STOP_MARKER.json` |
| arm `MESH` | **rc = 0** [MEASURED] | `STATUS.MESH`; `ledger.txt` |
| arm `X-S` | **rc = 1** [MEASURED] | `STATUS.X-S`; `ledger.txt` |
| arms `F-S`, `X-P`, `F-P` | **NEVER LAUNCHED** — no container started | absent from `ledger.txt`; `chain=STOPPED_AT_FIRST_NONZERO arm=X-S` in `STATUS.chain` |

The driver stopped at the first non-zero rc, as registered. Run root:
`/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient/`.

---

## 3. Cost

**Actual, MEASURED, from `ledger.txt` (`wall_s × ranks ÷ 60`, ranks = 1 on both arms):**

| arm | wall s | ranks | core-min | cap (core-min) | source |
|---|---|---|---|---|---|
| `MESH` | 16 | 1 | **0.267** [MEASURED] | 5.0 [REGISTERED] | `ledger.txt` `ARM=MESH` |
| `X-S` | 92 | 1 | **1.533** [MEASURED] | 15.0 [REGISTERED] | `ledger.txt` `ARM=X-S` |
| **total** | 108 | 1 | **1.800 core-min** [MEASURED] | ceiling 115.0 [REGISTERED] | |

**Dollars: $0.001539 — DERIVED, NOT MEASURED.** 1.800 core-min = 0.0300 core-h ×
$0.0513/core-h. `cost_basis`: c7a.4xlarge at $0.0513/core-h, **REPORTED-BY-OWNER,
NOT MEASURED** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5; `CLAUDE.md` rule 12). No dollar figure in this
lab is ever a measurement.

**No cap was breached and no `timeout` fired.** MESH used 5.3 % of its 5.0 cap;
X-S used 10.2 % of its 15.0 cap. Enforced in-container deadlines were 300 s and
900 s respectively [MEASURED, `ledger.txt`]; neither was reached. The chain died on
a solver error, not on an overrun.

**Waste, named separately and never absorbed** (`COMPUTE_BUDGET_CHARTER.md` §6):
the whole **1.800 core-min bought no gradeable artefact** and is carried as WASTE
on a failed attempt. It is not nothing — it bought three converged primals, one
completed adjoint, and the mechanism in §6 — but it bought no row and no gate, and
a total that silently counted it as useful would overstate this lab's efficiency.
**Separately again, and not this item's:** SO-3a's prior **0.334 core-min** is
carried as spent and named as waste by `PREREGISTRATION.md` §9 and is **never**
absorbed into SO-3aR's actual/predicted ratio.

**Nothing was left running.** Checked at write time: the run root's newest mtime is
`SO3aR_STOP_MARKER.json` at 20:22, and no `F-S`/`X-P`/`F-P` directory or log exists.

Estimate-versus-actual calibration is landed as a row in `docs/COST_CALIBRATION.md`
per `CLAUDE.md` rule 12; see §7.

---

## 4. Toolchain — both arms SHIPPED, and NO two-row verdict is possible

Both executed arms ran the **SHIPPED** row [MEASURED, `ledger.txt`]:

- image `dafoam/opt-packages:latest`
- digest `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`
- `libidwarp.so` md5 `f0fcb488e0e98156575cd19548e91663` — recorded per arm as
  `D4S_IDWARP_SO_MD5` in `ledger.txt`, echoed in the MESH log, and independently
  recorded by the producer itself in `X-S/so3ar_X.jsonl` line 1
  (`"libidwarp_so_md5": "f0fcb488e0e98156575cd19548e91663"`).
- staged tutorial source `/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible`
  at commit `d3b7e38b058aba2a98a74092e15c41ec455c570d` [MEASURED, `ledger.txt` `STAGED`].

**The PATCHED arms `X-P` and `F-P` NEVER RAN.** No container was started for either;
neither appears in `ledger.txt`. **Therefore NO two-row verdict is possible for this
item.** The registered SHIPPED-row / PATCHED-row comparison has exactly one side of
its evidence and one side of a comparison is not a comparison. Nothing in this
record may be read as a PATCHED result, and nothing may be inferred about the
patched toolchain from the SHIPPED arm's death.

---

## 5. What SUCCEEDED — the item's positive content

The X-S arm did not die early. It died **after** the multipoint primal block
completed and **after** the first scenario's adjoint completed. That is the
substantive content this item bought, and it is recorded as such.

**All three multipoint primals CONVERGED** — three tolerance-satisfaction lines and
three `End` lines in `X-S_20260831T202041Z_376689.log` [MEASURED]:

| scenario | line | minimal residual | prescribed tol | `End` at line |
|---|---|---|---|---|
| 1st | 1514 | 9.671227459413947e-09 | 1e-08 | 1518 |
| 2nd | 1644 | 9.66548074377354e-09 | 1e-08 | 1648 |
| 3rd | 1774 | 9.907086431972576e-09 | 1e-08 | 1778 |

Counts verified over the whole log: `satisfied the prescribed tolerance` = **3**,
`^End$` = **3**.

**Functionals at baseline** — source `X-S/so3ar_X.jsonl` **line 4**
(`"kind": "primal", "tag": "baseline", "wall_s": 20.033`) [MEASURED]:

- `CD = [0.01723938072177922, 0.020910510045267394, 0.027268054119716875]`
- `CL = [0.31189588769251864, 0.49876526085592926, 0.6639763551107052]`
- `J = 0.02180598162892116` (`"J_source": "obj.J"`, objective
  `J = SUM_i w_i * CD_i`, equal weights 1/3, jsonl line 3)
- `"non_finite": []`

Alphas were read back and matched the registered values to the recorded digits
(`3.13918623195176 / 5.13918623195176 / 7.13918623195176`, jsonl line 3:
`alphas_registered == alphas_from_dvs == alphas_read_back`) [MEASURED].

**The multipoint ADJOINT for scenario `point0` COMPLETED.** The linear solve
converged — `Main iteration 157 KSP Residual norm 1.007293914605e-08`,
`**Completed**! Total iterations: 157. PetscConvergedReason: 2`, `Residual
tolerance satisfied, solution finished!` — the five `d[…]/d[…]^T * psi` products
were computed, and the solution was renamed successfully:
**`Moving time 443 to 0.0001`, log line 1827** [MEASURED].

These figures are recorded as **what the run measured**, not as a graded result.
They carry **no verdict**: the item is `NOT A RESULT`, the registered gates were
never evaluated, and no number above may be quoted as a PASS or a GATE REACHED.

---

## 6. Cause of death

**Verbatim, log line 1868:**

```
| pyDAFoam Error: /mnt/X-S/0.0001 already exists, moving failed!             |
```

**Raised by** `'point1.coupling.solver'` (log line 1873:
`pyDAFoam Error: 'point1.coupling.solver' <class DAFoamSolver>: Error calling
solve_linear()`), at
`…/site-packages/dafoam/pyDAFoam.py`, **line 1543**, in `renameSolution`
(`raise Error("%s already exists, moving failed!" % dst)`), reached from
`…/site-packages/dafoam/mphys/mphys_dafoam.py`, **line 483**, in `solve_linear`
(`solutionTime, renamed = DASolver.renameSolution(self.solution_counter)`),
under `prob.compute_totals(of=of, wrt=["shape"])` at
`/mnt/X-S/so3ar_xf.py`, **line 643**, in `main`. All four frames [MEASURED],
`X-S_20260831T202041Z_376689.log` lines 1882–1894 and the tail. Process exit 1;
`mpirun` aborted the job.

**The collision, line by line** [MEASURED]:

- line **1827** `Moving time 443 to 0.0001` — `point0`'s adjoint, **succeeded**.
- line **1865** `Moving time 436 to 0.0001` — `point1`'s adjoint, **collided**.
- line **1868** the `pyDAFoam Error` above.
- line **1873** the failing component named: `'point1.coupling.solver'`.

Corroborated on disk: `X-S/` holds `0.0001/` (point0's renamed solution) alongside
un-renamed `436/` and `424/` — `point1`'s and `point2`'s converged times, which
`point0` had already taken the destination for [MEASURED, directory listing].

### ROOT CAUSE — THIS IS A LAB REGRESSION, NOT AN UPSTREAM DEFECT

`so3ar_runScript.py` builds `point0` / `point1` / `point2`
(`SCENARIOS = ["point%d" % i for i in range(len(ALPHAS))]`, **line 171**) and gives
each its own `DAFoamBuilder` (**line 245**) and its own mesh coordinate subsystem,
then adds each as a scenario (**line 262**) — **with NO per-point
`run_directory`.** `grep -n run_directory
cases/dafoam/ladder-a/A1/curriculum_SO3aR/so3ar_runScript.py` returns **nothing**
[MEASURED]. Three independent `DASolver`s therefore share one case directory
(`/mnt/X-S`), each carries its own `solution_counter`, and each renames its solution
to the same `0.0001`. The second one to arrive collides by construction. The script's
own docstring (line 44) says *"Each scenario keeps its own `DAFoamBuilder` and its
own mesh coordinate subsystem"* — own builder, own mesh, **shared directory**. That
is the gap.

**A2's D6R had already solved exactly this.** In
`/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R/d6r_opt_runScript.py`:

- **line 59:** `RUN_DIRS = {"cl04": "mp04", "cl05": "mp05", "cl06": "mp06"}`
- **line 120:** `"gridFile": os.path.join(os.getcwd(), RUN_DIRS[point])`
- **line 138:** `run_directory=RUN_DIRS[pt]` passed to the per-point builder

and its own docstring, **lines 6–8**, states the design in as many words:

> *"three ScenarioAerodynamic scenarios cl04 / cl05 / cl06 (CL targets 0.4 / 0.5 /
> 0.6), each with its OWN DAFoamBuilder in its OWN run_directory mp04/ mp05/ mp06/
> (a full copy of the case, staged by the launcher)…"*

Both source facts verified directly against the two files at write time.

**The A1 multipoint script did not carry forward A2's per-point directory
isolation.** The lab knew this, wrote it down in a docstring, and lost it crossing
from A2 to A1. That is a regression inside this repository, and calling it anything
else — an upstream bug, an environment problem, a surprise — would be false. The
repair is A2's, already written: give each point its own staged `run_directory`.

### OPEN and UNTESTED — the upstream question

Upstream's own multipoint tutorial,
`/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/multipoint/runScript.py`, adds two
scenarios at **lines 118–119** —
`self.mphys_add_scenario("scenario1", ScenarioAerodynamic(aero_builder=dafoam_builder))`
and the same for `"scenario2"` — sharing one directory, with **no `run_directory`**
anywhere in the file (`grep` returns nothing) [MEASURED].

**Whether upstream is ALSO latently broken is UNTESTED and OPEN.** It is NOT this
item's finding, it is NOT a defect report, and it is NOT filed anywhere. One
verified structural difference argues for genuine caution before assuming the two
cases are the same: **upstream passes ONE shared `dafoam_builder` to both
scenarios**, where SO-3aR constructs **three separate builders**. A single builder
may mean a single `DASolver` and a single `solution_counter`, in which case the
collision this item hit cannot arise there. That is a reading of the source, **not
a test** — nobody has run upstream's tutorial to find out, and this record does not
claim to know. Recorded as **OPEN**.

---

## 7. Calibration (`CLAUDE.md` rule 12)

- **Predicted: 22.0 core-min** point, band `[14.0, 60.0]`, ceiling `115.0`
  [REGISTERED, `PREREGISTRATION.md` §9 and §4, frozen at `977f3d9b` before compute].
  Registered dollars $0.01881 point — DERIVED there too, never measured.
- **Actual: 1.800 core-min** [MEASURED, `ledger.txt`, §3 above].
- **Ratio actual/predicted = 0.082.**
- **Attribution: TRUNCATION at arm 2 of 5 — not misprediction.** The per-arm rates
  were fine and are the evidence for it: `MESH` came in at 0.267 against a 5.0 cap
  and `X-S` at 1.533 against a 15.0 cap, both well inside their registered
  envelopes, so nothing suggests the estimate for the arms that *ran* was wrong. The
  ratio is small because **three of five arms (`F-S`, `X-P`, `F-P`) never started**,
  not because the lab priced the work badly. Calling this an over-prediction would
  be laundering a crash into an estimating success.
- **Waste kept separately named:** the full 1.800 core-min is waste on a failed
  attempt (§3) and is not folded into the ratio's explanation; SO-3a's prior 0.334
  core-min is excluded entirely, as `PREREGISTRATION.md` §9 requires.

The ledger row is at `docs/COST_CALIBRATION.md`, id **`C-20260831T204530.092810Z-e03cf43f`**.

---

## 8. What this record could NOT verify

- **Nothing about the PATCHED toolchain.** `X-P` and `F-P` never ran (§4).
- **Nothing about F-arm behaviour.** `F-S` never ran.
- **No registered gate value.** The comparator refused at G1 before evaluating any
  gate; `SO3aR_grade_20260831T202215Z.json` does not exist, and the stop marker
  records `rows` and `G5J` as `"NOT PRESENT IN THE ARTEFACT"`.
- **Whether upstream's multipoint tutorial is latently broken** — UNTESTED (§6).
- **The `delivered_cores_mean` for MESH** is `[NOT_MEASURED]` in `ledger.txt`; the
  X-S arm recorded `0.7577 (n=5, max_nr_throttled=8)`, i.e. the arm was CPU-throttled
  below one full core. That does not change the core-minute figure, which is
  `wall_s × ranks ÷ 60` by the lab's definition, but it is stated rather than hidden.

---

## 9. Artifacts

### 9.1 The two runner artifacts are NOT tracked, and why

`STATUS.queue.SO3aR_chain` and `launcher.queue.out` sit on disk in this case
directory, **untracked, and they stay untracked.** They were staged into a first
version of this commit and `scripts/check_filing.py` **refused them**, twice, under
rule **`R6-RUNARTIFACT`**:

> *"a queue-runner artifact is a RUN OUTPUT and belongs under
> `verification/runs/<CAMPAIGN>/`, not in the case's input directory
> (`FILING_CHARTER`; `CLAUDE.md` WHERE THINGS LIVE; Sanaa 2026-08-27: logs and
> attempt dirs stay out of git)."*

The rule is not a shape-match that got lucky: `check_filing.py` carries planted
controls for both limbs — `cases/X/launcher.queue.out` must flag,
`verification/runs/CAMP/L1/launcher.queue.out` must not, and `cases/X/STATUS.md`
must not. The sibling pair at
`cases/dafoam/ladder-a/A1/feasibility_SO3a_alpha/{STATUS.SO3AF,launcher.queue.out}`
**is tracked and is itself flagged by the same rule** — it is a standing violation,
not a precedent, and it was the reasoning that led this lane astray. A tracked
violation is not a licence to add two more.

**Preservation is served instead by quoting them verbatim in §9.2 below.** A results
record is a legitimate case document; the bytes are in git, inside a document that
is allowed to hold them, and the runner artifacts stay out of `cases/` as the rule
requires. Their absolute paths on this box:
`/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3aR/STATUS.queue.SO3aR_chain`
and `…/launcher.queue.out`.

### 9.2 The two runner artifacts, verbatim

`STATUS.queue.SO3aR_chain` (1 line, 93 bytes):

```
launcher_rc=1 end=2026-08-31T20:22:15Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc
```

Note the artifact's own caveat: `launcher_rc` is **the exit status of the launch
argv, NOT the solver rc**. The solver rc is `X-S rc=1` in `ledger.txt` and
`STATUS.X-S`, and that is what §2 cites.

`launcher.queue.out` (33 lines, 3,634 bytes):

```
SO3AR_DEPS_EXIST n=7 checked_before_any_md5=yes
/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3aR/so3ar_run_arm.sh: OK
/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3aR/so3ar_grade.py: OK
/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3aR/so3ar_aggregate_memory.py: OK
/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3aR/so3ar_stop_marker.sh: OK
/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/runScript.py: OK
/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/genAirFoilMesh.py: OK
/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/preProcessing.sh: OK
/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/profiles/NACA0012PS.profile: OK
/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/profiles/NACA0012SS.profile: OK
/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/FFD/wingFFD.xyz: OK
SO3AR_ROOT_STAGED base=/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient stamp=20260831T201813Z mode=777 permission=bc0e687e
/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient/so3ar_runScript.py: OK
/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient/so3ar_xf.py: OK
/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient/base/system/decomposeParDict: OK
/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient/base/genAirFoilMesh.py: OK
/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient/base/preProcessing.sh: OK
/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient/base/profiles/NACA0012PS.profile: OK
/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient/base/profiles/NACA0012SS.profile: OK
/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient/base/FFD/wingFFD.xyz: OK
SO3AR_DRIVER start=20260831T201813Z pid=374044 ppid=374043 sid=374043 cwd=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3aR arms=[MESH X-S F-S X-P F-P] declared=5 permission=bc0e687e
/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3aR/so3ar_run_arm.sh: OK
SO3AR_H5_WINDOW arm=MESH n=45 window_s=60 floor_GiB=16.0 min_GiB=27.23 max_GiB=27.5 samples_below_floor=0 waited_s=0 file=MESH_h5_window_20260831T201813Z.txt
SO3AR_AGGREGATE arm=MESH waited=0 {"live_caps_GiB": 0.0, "live": [], "this_cap_GiB": 12.0, "host_noncontainer_rss_GiB": 3.37, "aggregate_GiB": 15.37, "ceiling_GiB": 30.6, "ok": true}
SO3AR_DRIVER arm=MESH image=dafoam/opt-packages:latest begin=20260831T201919Z ppid_now=374043 permission=bc0e687e
SO3AR_DRIVER arm=MESH end=20260831T201936Z rc=0
/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3aR/so3ar_run_arm.sh: OK
SO3AR_H5_WINDOW arm=X-S n=45 window_s=60 floor_GiB=16.0 min_GiB=26.98 max_GiB=27.45 samples_below_floor=0 waited_s=0 file=X-S_h5_window_20260831T201936Z.txt
SO3AR_AGGREGATE arm=X-S waited=0 {"live_caps_GiB": 0.0, "live": [], "this_cap_GiB": 12.0, "host_noncontainer_rss_GiB": 3.43, "aggregate_GiB": 15.43, "ceiling_GiB": 30.6, "ok": true}
SO3AR_DRIVER arm=X-S image=dafoam/opt-packages:latest begin=20260831T202041Z ppid_now=374043 permission=bc0e687e
SO3AR_DRIVER arm=X-S end=20260831T202215Z rc=1
SO3AR_STOP_MARKER written=/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient/SO3aR_STOP_MARKER.json verdict=PENDING chain_rc=1 declared=5 executed=1 truncated=True
SO3AR_DRIVER end=20260831T202215Z chain_rc=1 declared=5 executed=1
```

The `verdict=PENDING` on the second-to-last line is the same display/queue state
§1 disposes of, echoed by the driver from the stop marker it had just written. It
is not the item verdict.

### 9.3 Run-root artifacts

Outside git, in the run root
`/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient/`
(cited by absolute path; run outputs are not filed into `cases/`):

- `SO3aR_STOP_MARKER.json`, `SO3aR_grade_20260831T202215Z.out`
- `STATUS.chain`, `STATUS.MESH`, `STATUS.X-S`, `ledger.txt`
- `X-S_20260831T202041Z_376689.log` (the death), `MESH_20260831T201919Z_375030.log`
- `X-S/so3ar_X.jsonl` (4 lines; line 4 carries the functionals)
- `X-S/0.0001/`, `X-S/436/`, `X-S/424/` — the collision, on disk

**A number whose artifact is gone is not a result.** Every figure above cites one
that was present and read at write time, 2026-08-31.
