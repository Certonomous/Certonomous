# CURRICULUM FADR — DAFoam's OWN shipped forward-AD regression, run UNMODIFIED, on BOTH toolchain rows — PRE-REGISTRATION

**Team:** dafoam. **Lane:** C, seventeenth session. **Written:** 2026-08-27, before any compute.
**Ladder position: OFF-LADDER.** FADR climbs neither A nor B. It verifies the **toolchain**, not a
case: it asks whether DAFoam's own shipped forward-AD regression passes inside the images DAFoam
ships in. **No A- or B-rung verdict moves on this item**, and no capability-grid cell is filled by it.

**Standards that bind this registration and are cited, not restated:**
`CLAUDE.md` standing rules 1–16; `docs/charters/VERIFICATION_CHARTER.md` §2, §2a–§2e, §7;
`docs/charters/DAFOAM_CHARTER.md` §6 (the two-row rule), §8 (vocabulary), §10 (`NOT FILED`);
`docs/standards/NONCONVERGENCE_STANDARD.md` @ `7ffd6c73` (the L0–L7 ladder and the **absolute**
anti-gaming clause); `docs/dafoam/ADJOINT_VERIFICATION_STANDARD.md` **v1.0b** (check (ii),
`BLOCKED — primal convergence under a forward seed`, band 1.0e-5 **untested, not falsified**);
`docs/dafoam/TOOLCHAIN_INVENTORY.md` (image digests).

---

## 1. WHAT IS ALREADY OBSERVED, AND IS THEREFORE EXCLUDED FROM THE PREDICTION SET

A prediction about something already measured is worth nothing. The following are **observations on
disk**, carried here so that no prediction below can be scored against them:

1. **The forward-AD channel is exposed and live.** On the A1 NACA0012 staged case (4,032 cells,
   np=1) the `ADF-Deriv` tangent for `CL` read **0.9983742395429173** against the reverse-mode total
   **1.037472696796837** — 3.8 % short and **rising monotonically** (0.98812 → 0.99343 → 0.99837).
   (`ADJOINT_VERIFICATION_STANDARD.md` v1.0b; AV-2 artefacts under
   `/home/ubuntu/certonomous-runs/CURRICULUM-AV2-a1-naca0012-duality/`.)
2. **The primal does not break under a forward seed; its convergence RATE collapses** from geometric
   to algebraic — 1.05e-03 / 2.78e-04 / 1.56e-04 / 1.07e-04 forward against
   6.52e-04 / 1.48e-05 / 5.36e-07 / 1.33e-08 reverse on the identical case, ~8,000× apart at
   iteration 400; reverse satisfies tolerance at iteration 435. The refusal is issued by
   `checkPrimalFailure()` (`DASolver.C:2721-2760`) — the **primal convergence gate**, not the API and
   not the forward channel.
3. **Two explanations are already eliminated at zero compute.** Tolerance configuration is not it
   (upstream's own regression runs an effective **1e-8**, 100× stricter than the lab's 1e-6 — see
   §4.1); invocation pattern is not it (`av2_xf.py` reproduces `tests/testFuncs.py:17-52` exactly).
   **What differs is THE CASE**: NACA0012 4,032 cells np=1 versus upstream's ConvergentChannel
   **343 cells np=4**. `primalMaxRes` is bit-identical across both images, so the IDWarp patch does
   not touch this channel.
4. **The fixture is absent from both images.** `tests/reg_test_files-main` does not exist on
   `dafoam/opt-packages:latest` or on `dafoam-idwarp-rot:v1`; `tests/Allrun:9-14` fetches it at run
   time. Read by this lane inside both images at freeze time, zero compute.

**One thing this lane measured at freeze time that was NOT previously on record, and which is stated
as an observation and not a prediction** (§4.2 turns it into a registered instrument property):
upstream's comparator `reg_file_comp` **rewrites the file it is comparing, in place**
(`testFuncs.py`, `f = open(comp_file, "w")` after reading it): where a value matched, the **reference**
line is written over the produced line. **A run graded by the shipped recipe destroys its own raw
output.** This registration therefore preserves the raw output *before* the comparator sees it.

---

## 2. THE INBOUND FETCH — CONDITIONS, ALL MANDATORY, ALL RECORDED IN THE CASE DIRECTORY

The fixture `reg_test_files-main.tar.gz` is retrieved **once**, from upstream, onto this box.
**This is INBOUND ONLY.** Nothing of this lab's leaves the box in the act, and standing rule 7 is
untouched by it: **SUBMISSIONS REMAIN PARKED.** No account, no login, no token, no header carrying
lab data, no issue, no comment, no upload.

- **Source URL, exactly as `tests/Allrun:13` names it:**
  `https://github.com/DAFoam/reg_test_files/archive/refs/heads/main.tar.gz`
- **Recorded, all four, in `FIXTURE_PROVENANCE.md` beside this file:** the URL, the **sha256**, the
  **byte size**, and the **UTC timestamp** of the retrieval.
- **CONTENT VERIFICATION, per standing rule 15 — the sha256 is PROVENANCE, NOT IDENTIFICATION.**
  The archive is **opened** and the record states **what was seen inside it**: the presence of the
  `ConvergentChannel` case directory and the OpenFOAM case structure the test script requires
  (`0/`, `0.incompressible/`, `system/`, `system.incompressible/`, `constant/turbulenceProperties.sa`,
  `FFD/FFD.xyz`). **Never by filename. Never by file type. Never by hash alone.**
- **The digest is then a GATE, not a note.** `fadr_chain_driver.sh` recomputes the sha256 at launch
  and **refuses (exit 2)** if it does not equal the digest recorded in `FIXTURE_PROVENANCE.md`.
- **Storage:** the archive lives OUTSIDE git at `/home/ubuntu/certonomous-runs/FADR-fixture/`
  (binary, and `FILING_CHARTER` keeps bulk out of the tree). The provenance record is text and is in
  git beside this file.
- **If the retrieval does not succeed, the item is `BLOCKED` and says so** — see branch **P-C** in §8.

---

## 3. ARMS — TWO, ONE PER TOOLCHAIN ROW, ONE DETACHED CHAIN, np = 4 ON BOTH

The two-row rule (`DAFOAM_CHARTER.md` §6): **a DAFoam verdict is two rows or it is not a verdict
about DAFoam.** The identity is the image **digest**; the version string is not the identity.

| arm | image | digest | what it runs |
|---|---|---|---|
| **S** (SHIPPED) | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | the recipe of §4, unmodified |
| **P** (PATCHED) | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | the same recipe, unmodified |

**The two rows are graded independently on the same gate. A patched row never replaces a shipped
row. A row that does not return is `BLOCKED`, not a missing row.**

**Measured at freeze time and registered as a property of this item:** the three harness files are
**md5-identical on both images** — `runRegTests_DASimpleFoamForward.py` `e03630f44a016c3a8b23bcbc8b4b8128`,
`testFuncs.py` `fb11e90630aeba07c62c14afc5ed2ceb`,
`refs/DAFoam_Test_DASimpleFoamForwardRef.txt` `ac46aca2f10e68da43dbe74be0dd3c29`. **Any divergence
between the rows is therefore located in the toolchain, never in the test.**

---

## 4. THE GATE — UPSTREAM'S OWN COMPARATOR, AT UPSTREAM'S OWN TOLERANCES, UNMODIFIED

### 4.1 The recipe, taken verbatim from `tests/Allrun:20-37`

Per arm, inside the container, in a **writable copy** of the image's own `tests/` directory (copying
is not modifying; every file is md5-asserted against the in-image original before the run):

1. `mpirun --oversubscribe -np 4 python runRegTests_DASimpleFoamForward.py | tee DAFoam_Test_DASimpleFoamForward.txt`
   — rc read from `PIPESTATUS[0]`, exactly as `Allrun` reads it.
2. **`cp DAFoam_Test_DASimpleFoamForward.txt DAFoam_Test_DASimpleFoamForward.RAW.txt`** — this
   lane's ONE addition to the recipe, disclosed here, made **after** the produced output exists and
   **before** the comparator runs, because the comparator overwrites its input (§1). It cannot
   change any value and cannot change the gate.
3. The two `sed -i` normalisations of `Allrun:30-31`, verbatim.
4. `python testFuncs.py refs/DAFoam_Test_DASimpleFoamForwardRef.txt DAFoam_Test_DASimpleFoamForward.txt`
   — **its exit code is the gate.**

**Two further disclosures, both of which change no numerical setting and neither of which touches a
value, a tolerance or the command line's arguments.** (a) The containers run as **uid 0** — that is
the images' own default user, measured, not a choice — and OpenMPI refuses to launch as root without
`OMPI_ALLOW_RUN_AS_ROOT=1` and `OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1`. Those two are **exported into the
environment**, so `mpirun --oversubscribe -np 4 python runRegTests_DASimpleFoamForward.py` stands
exactly as `Allrun` writes it. (b) The invocation is wrapped in `timeout -k 60 1800`, the registered
per-arm deadline of §6: a deadline can **stop** a run, it cannot alter a value it produced, and cap
enforcement is standing rule 12.

The test's own settings, unmodified and stated so the gate is legible: `primalMinResTol` **1.0e-12**
with `primalMinResTolDiff` **1e4**, so the **forward-mode primal is accepted at an effective 1e-8**;
`adjEqnOption.gmresRelTol` **1.0e-12**; `nCells` **343**; `DASimpleFoam`, SA, `U0 = 10 m/s`;
design variables `shape[0]`, `beta[0,200]`, `fv_source[100,300]`, `u_in[0]`; functions `CD`, `HFX`.

### 4.2 THE THRESHOLD, AND AN HONEST STATEMENT OF ITS DISCRIMINATING POWER

Upstream writes every value with `reg_write_dict(derivDict, 1e-8, 1e-12)` and compares each against
its stored reference with **`rel_err < 1e-8` OR `abs_err < 1e-12`** — a **disjunction**, so the
looser of the two governs. **24 `@value` lines**: 2 functions × 6 DV entries × {Adjoint, ForwardAD}.

**Counted at freeze time from the reference file itself, and registered as a limitation of the
instrument, not of the run:** `abs_tol` governs wherever `|value| < 1e-4`. **16 of the 24 values are
below that** (`beta0`, `beta200`, `fv_source100`, `fv_source300` on both functions), where `1e-12`
absolute is as loose as **8e-4 relative** on the smallest (`beta200 = 1.25e-9`). **Only 8 values —
`shape0` and `u_in0` on `CD` and on `HFX` — are genuinely governed by the 1e-8 relative tolerance.**
This is stated **before** the run so that a `PASS` is not read as 24 tight agreements when it is 8.

### 4.3 VERDICT MAPPING — the fixed vocabulary, per row, then for the item

- **`PASS`** — the comparator returns 0 (`REG_FILES_MATCH`), the raw output carries **exactly 24**
  `@value` lines, `mpirun` rc = 0, the age datum holds (§6), and **every planted control was seen**.
- **`GATE FAIL`** — the comparator returns 1 (`REG_FILES_DO_NOT_MATCH`) on a run that otherwise
  completed. The failing keys and their values are named. **Never re-banded, never re-run for a
  better number** (anti-gaming, absolute).
- **`NOT A RESULT`** — the comparator returns `-1` (`REG_ERROR`, a file it could not read); or the
  `@value` count is not 24; or a planted control was not seen; or the age datum fails; or the raw
  output was destroyed before capture.
- **`BLOCKED`** — the arm cannot run at all: the image does not start, the fixture is unobtainable
  (§8 P-C), an import fails, or `checkPrimalFailure()` refuses the forward-seeded primal so that no
  `@value` line is ever produced. **A forward primal that does not reach 1e-8 and aborts the run is
  `BLOCKED`, and it is a finding about the toolchain, not about this registration.**
- **`GATE REACHED`** — never applicable here; it is the optimiser's cap token.
- **`PENDING`** — registered and unrun.
- **Item verdict:** `PASS` **only if both rows are `PASS`**. Otherwise the item takes the weakest
  row's label, both rows printed.

### 4.4 THE PLANTED CONTROLS (standing rule 3) — the grader refuses if any is not seen

`fadr_grade.py` reimplements the comparison independently of `testFuncs.py` and carries
`--selftest`, whose evidence is committed at this freeze:

- **C1 — the reader can see a MISMATCH.** A synthetic comp file with one `@value` perturbed beyond
  both tolerances must be reported MISMATCH. A reader that has never been shown a non-match cannot
  report a match.
- **C2 — the reader can see a MATCH.** The reference compared against itself must report MATCH.
- **C3 — the operator mutation flips the control.** With the comparison predicate inverted, C1 and
  C2 must both flip. A guard never shown able to fail is not known to work.
- **C4 — the silent-empty refusal.** A comp file with **zero** `@value` lines must **refuse**, never
  return MATCH. This is the AV-2 hazard in its FADR form: `mphys` forward hooks are a **silent
  no-op** that warn and fall through (`ADJOINT_VERIFICATION_STANDARD.md` v1.0a), so an instrument
  reading nothing must never read it as agreement.
- **C5 — the count guard.** A comp file with 23 `@value` lines must refuse, not pad.
- **C6 — the tolerance disjunction is exercised in BOTH directions**: a value passing only on
  `abs_tol` and a value passing only on `rel_tol` are each shown accepted, and each shown rejected
  when its own tolerance is tightened.

`--selftest` additionally parses its own AST and **refuses if a single `ast.Assert` node exists**
(L-332: `python3 -O` deletes asserts, and a refusal written as one is a refusal the runner declines
by an interpreter flag they did not know they were choosing). Every refusal is `sys.exit(2)`.

---

## 5. COST — DERIVED FROM NAMED ANCHORS, NOT MEASURED

**Anchors, all named:** **AV-2's own measured ledger** — `FAD-S` **8.267 core-min** for one reverse
primal plus five forward-mode primals, 4,032 cells, np=1; `X-S` **1.017 core-min** (anchor C-31, one
primal plus one adjoint); `MESH` **0.167 core-min** (anchor C-135, container start plus setup) —
`cases/dafoam/ladder-a/A1/curriculum_AV2R/PREREGISTRATION.md` §4 @ `44b9c0c3`.

**Derivation, stated so it can be graded (P6):** per forward primal at 4,032 cells np=1 ≈
8.267 / 6 ≈ **1.38 core-min**. Solver work scales with cells: 343 / 4,032 = **1/11.75** →
**0.12 core-min** at np=1. At **86 cells per rank** no parallel speedup is assumed, so np=4 costs
**4×** the core-minutes → **0.47**. The 1e-8 effective tolerance against the lab's usual 1e-6 is
taken at **3×** → **1.4 core-min** per primal. **Seven** full OpenMDAO problem constructions (one
reverse plus six forward), each carrying a mesh/IDWarp/FFD setup at 4 × 0.167 ≈ **0.67** → **4.7**.
Adjoint `compute_totals` over two functions ≈ **1.0**.

| arm | derivation | point (core-min) | cap (core-min) | in-container wall | mem |
|---|---|---|---|---|---|
| **S** | 7 setups (4.7) + 7 primals (9.8) + adjoint (1.0), rounded | **17.0** | 120.0 | 1,800 s | 8g |
| **P** | identical | **17.0** | 120.0 | 1,800 s | 8g |
| grader | zero compute, host | 0 | — | — | — |
| **total** | | **34.0 point**, band **[10, 120]** | **ceiling 240.0 = Σ caps** | | |

**`cost_basis`: c7a.4xlarge at $0.0513/core-h — REPORTED-BY-OWNER, NOT MEASURED**; the box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Dollars DERIVED, not measured:** point
34.0 core-min = 0.5667 core-h = **$0.0291**; ceiling 240.0 core-min = 4.0 core-h = **$0.2052**.
Under the $25/run pre-authorisation, and **still costed** — a blanket is not a per-item read
(rule 9). **An overrun stops the run; it does not get a new budget.** **A calibration row is owed at
completion** (rule 12) against the 34.0 point, in `docs/COST_CALIBRATION.md`.
**Spent on this item before this freeze: 0.000 core-min of solver time.** The freeze-time image
reads (`md5sum`, `cat`, `ls`) are instrument time and are named here rather than absorbed.

---

## 6. PLACEMENT, MEMORY, CPUSET, THE DETACHED FORM, AND THE AGE DATUM

**Run root:** `/home/ubuntu/certonomous-runs/CURRICULUM-FADR-forward-ad-regression/` — asserted
**ABSENT** at this freeze, before and after the driver's own selftest. **This directory does not
exist at the time this pre-registration is committed**, which is the condition rule 2 requires an
amendment to name and check; it is named and checked here.

**cpuset `5,6,7` — THREE cores, registered, and the choice is disclosed.** Every other core on this
16-core box is reserved by a **pending** queue entry (0,1 AV1R/AV2R; 8,10,11,13 D5_r4; 9 SO1a;
12,15 D18) or held by the **running** D6 container (2,3,4,14). `np = 4` is **upstream's own and is
not changed**; `mpirun --oversubscribe` is **already in the shipped command**, so four ranks on three
cores is the shipped invocation meeting the box's real capacity. **This affects wall time only and
cannot move a derivative.** Core-minutes are declared at `ranks = 4` per
`COMPUTE_BUDGET_CHARTER`'s formula, which therefore **over**-states true occupancy — the conservative
direction.

`--memory=8g` with `--memory-swap` equal and `--oom-score-adj=500`; one detached chain driver runs
S then P; per-arm in-container `timeout -k 60 1800`; **rc read from `docker inspect .State.ExitCode`,
never from the `setsid` parent** (a `setsid timeout cmd` parent exits 0 for every outcome).

**THE AGE DATUM, in the form this item's artefact takes.** The graded artefact is a text file, not a
field, so the age guard is stated in its own terms and **resolved BY EXISTENCE, never by name**: the
arm's `tests/runRegTests_DASimpleFoamForward.py`, written at staging, **is** the datum, and
`DAFoam_Test_DASimpleFoamForward.RAW.txt` must be **strictly newer** than it. A raw output older
than the harness that produced it is `NOT A RESULT`. The driver refuses if the arm directory, or
the run root, already exists.

---

## 7. PREDICTIONS — scored HIT / MISS by the grader, never adjusted after the fact

| # | prediction | scored by |
|---|---|---|
| **P1** | The comparator's exit code is identical on both rows (S and P agree on PASS-or-FAIL). | comparator rc per arm |
| **P2** | The raw output of each arm carries **exactly 24** `@value` lines. | grader count |
| **P3** | The forward-seeded primal **reaches acceptance** on ConvergentChannel — i.e. no `checkPrimalFailure()` refusal appears in either arm's log. This is the discriminator the item exists to buy, and it is registered as a HIT/MISS **before** the run. | log scan for the refusal banner |
| **P4** | Where both rows produce values, `shape0-Adjoint` and `shape0-ForwardAD` agree with each other to better than **1e-8 relative** on `CD` — the duality agreement upstream's own reference exhibits (1.7436786358470828 vs 1.7436786358487191, 9.4e-13 relative). | grader, computed from the raw outputs |
| **P5** | The 3.8 % NACA0012 gap is **not** reproduced here: the worst Adjoint-vs-ForwardAD relative disagreement over the 8 rel-governed values is below **1e-5** — the band `ADJOINT_VERIFICATION_STANDARD.md` §2 registered and which v1.0b records as **untested**. | grader |
| **P6** | Measured chain cost lands inside the registered band **[10, 120] core-min**. | ledger |
| **P7** | S and P produce **bit-identical** `@value` lines on every one of the 24 — the IDWarp patch does not touch this channel (`primalMaxRes` is already known bit-identical across the images). A **MISS here is a larger finding than a HIT** and is reported as one. | grader, byte comparison |

**P4 and P5 are diagnostic readings, not gates.** The gate is §4.3 and nothing else. A prediction
MISS never changes a verdict.

---

## 8. THE THREE BRANCHES, NAMED IN ADVANCE — THIS IS WHAT MAKES THE ITEM HONEST

**Both substantive outcomes are written here, before anything runs, with their consequences. Neither
is preferred, and the record will say which one landed.**

- **P-A — the regression PASSES (item `PASS`, both rows).** Then DAFoam's forward-AD channel is
  demonstrably correct to upstream's own reference in the image it ships in, and **the AV-2
  observation is confirmed as CASE-DEPENDENCE**. The discriminator is then **problem size and
  conditioning** — 343 cells at np=4 against 4,032 at np=1 — and the successor question is which of
  the two (size, partitioning, conditioning, or the SA field state) carries it. Check (ii)'s status
  in `ADJOINT_VERIFICATION_STANDARD.md` stays `BLOCKED — primal convergence under a forward seed`
  **for the A1 case**, and gains a positive control on a case where it is not blocked.

- **P-B — the regression FAILS or is REFUSED (item `GATE FAIL` or `BLOCKED`).** Then **DAFoam's own
  shipped forward-AD regression does not pass in the image DAFoam ships in.** This is the
  **materially larger finding**: it is not a statement about this lab's cases at all, and it makes
  the AV-2 result a symptom rather than a peculiarity. It is an **upstream defect candidate**.
  **If P-B lands, the artefact is a DRAFT carrying `NOT FILED` in its OPENING LINES at the top of the
  file** (`DAFOAM_CHARTER.md` §10). **It is not filed, sent, posted, commented or registered
  anywhere, by this lane or by anyone, ever.** Sending is Sanaa's decision alone (standing rule 7).

- **P-C — the fixture cannot be retrieved (item `BLOCKED`).** No network route, an upstream 404, or
  a content check that fails §2. Then **nothing is concluded about DAFoam**: the item is `BLOCKED`
  on the fixture, the reason is recorded with its UTC, and no compute is spent. This branch is named
  so that a failed download cannot later be narrated as a finding.

---

## 9. WHAT THIS REGISTRATION DOES **NOT** AUTHORISE

- **No convergence ladder.** If a forward primal does not converge, `NONCONVERGENCE_STANDARD` §2.1
  **L0 is MANDATORY and is a reading, not a run**: the record names which of the three shapes
  (oscillation / growth under flat neighbours / plateau), which channel, the balance state, and where
  in the domain. **No L1–L7 arm is registered here.** Any such arm is a **new registration** with its
  own freeze and its own cap. A parameter hunt under this freeze is forbidden by the anti-gaming
  clause, which is **absolute**.
- **No modification of the test, the reference, the fixture or the tolerances**, for any reason,
  including to make it pass. The one disclosed addition to the recipe is §4.1 step 2, which copies a
  file.
- **No re-run for a better number.** If a row fails, it fails, with its keys named.
- **No verdict about the A-ladder, the B-ladder, or any capability-grid cell.**
- **No send, of anything, to anywhere.** §8 P-B's draft carries `NOT FILED` at its head.

---

## 10. INSTRUMENTS, FROZEN BY md5 AT THIS COMMIT

| file | role |
|---|---|
| `PREREGISTRATION.md` | this file — the freeze |
| `fadr_fetch_fixture.sh` | the §2 inbound retrieval and the provenance record it writes |
| `fadr_chain_driver.sh` | the detached two-arm chain, its guards and its refusals |
| `fadr_grade.py` | the independent grader, its planted controls, `--selftest` |
| `fadr_grade_selftest_evidence.txt` | the selftest's committed output |

The md5 of each is recorded in `INSTRUMENT_MD5.txt` at this commit and re-asserted by the driver
before the first container starts. **The grading path is fixed at this commit** (standing rule 2):
the driver hashes each instrument against the committed blob and **refuses** on any difference.

---

## 11. FREEZE AND QUEUE

This file is frozen by the sha of the commit that **adds** it, re-derived with
`git log --oneline --diff-filter=A -- <path>` and **never from a commit subject line** — two commits
in this lab shared a subject 52 s apart and the wrong one resolved to a real commit, failing only at
the path check (`VERIFICATION_CHARTER` v1.12).

**After first compute this document is closed.** Departures land only as dated addenda that cannot
alter a gate, threshold, cap or label; originals are struck, never rewritten.

The queue entry is `verification/queue/dafoam/FADR_chain.json`, validated by
`scripts/queue_entry_check.py`. **ENQUEUEING IS NOT AUTHORISATION**: `SUPERVISION_CHARTER.md` §3
check 4 is the supervisor's own and is not discharged by this lane filing the entry. **Nothing is
launched by hand.** The daemon runner launches from the drop path with no agent alive; the box is
above the runner's 85 % ceiling and the entry will **hold**. **That is correct behaviour, not a
stall.**
