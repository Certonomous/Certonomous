# D11-O′ — THE OMEGA RE-BUY of the D11 MRF probe — ATTEMPT THREE AND LAST — PRE-REGISTRATION

**Form:** the 10-line mini-prereg. **Frozen at the commit that adds this file; no
container of D11-O′ has run.**
**Author:** dafoam `lab-lane`, 2026-08-25. Nothing filed, sent or posted (rule 7).

---

### 0. Why this exists, what it changes, and the hard stop on it

Attempt one (`../curriculum_D11_mrf_probe/`, frozen `c2913dcd`) → **`NOT A RESULT`**:
the frozen `MRFProperties` used the wrong dictionary layout and every stage died on
`Entry 'MRF' not found`.

Attempt two, D11-D′ (`../curriculum_D11_mrf_probe_Dprime/`, frozen `25c735ff`) →
**`NOT A RESULT`**, and it **half-succeeded in a way that is itself the finding**:

| stage | omega | task | rc |
|---|---|---|---|
| `omega0` | 0.0 | `compute_totals` (primal **and adjoint**) | **0** |
| `clean` | 0.0 | `run_model` | **0** |
| `omegaP` | 300.0 | `compute_totals` | 1 |
| `fdp`, `fdm` | 300.0 | `run_model` | 1, 2 |

**The corrected dictionary is right** — DAFoam parses it, builds the zone, and takes an
adjoint through to `rc = 0` — **and every failure is at omega = 300 rad/s and only
there.** Triage of the log: the steady SIMPLE primal **STALLS**, continuity plateauing
at `≈ 2.5e-4` and never reaching `primalMinResTol = 1e-10` inside 2000 iterations, so
DAFoam raises `openmdao.core.analysis_error.AnalysisError: Primal solution failed!` and
writes no JSON. **It stalls; it does not diverge, and it does not NaN.**

**That is the substrate refusing a 300 rad/s zone, not the capability being absent.** At
`r ≈ 0.02 m` a 300 rad/s zone drives ≈ 6 m/s of tangential motion against a 10 m/s
through-flow, at an abrupt zone boundary — a harsh steady problem, and my choice of
magnitude, not DAFoam's limitation.

**THE ONE CHANGE, and it is a registered quantity, so it is named plainly:** the plant
magnitude drops **once**, from `omega = 300.0` to **`omega = 30.0 rad/s`**. At
`r ≈ 0.01 m` that is ≈ 0.3 m/s, about 3 % of the through-flow — chosen in advance to sit
far above the unchanged `1.0e-6` plant floor (D10-P′ measured a 0.35 % boundary change
moving its objective by `2.06e-2`) and far below the momentum balance. **One value.
Not a ladder. Not selected after seeing an answer, because no run at 30 rad/s exists.**

**THE HARD STOP, registered before the run.** If the `omega = 30.0` primal also fails to
converge, the verdict is **`NOT A RESULT`** and **D11 goes to the supervisor UNPRICED
with a named blocker — "no substrate on this box has yet converged a steady MRF-active
DASimpleFoam primal". THERE IS NO FOURTH ATTEMPT.** Reducing omega again until something
converges would be tuning an instrument against an answer, and this clause exists so
that the temptation is refused in writing before it can be felt.

**Convergence is a PRE-GATE, and it is structural, not discretionary.** A non-converged
primal raises `AnalysisError`, writes no JSON, and the grader refuses on the missing
artifact. There is no code path by which a stalled primal produces a graded number.

### 1. Capability under probe
Unchanged from D11 §1, including the registered correction that **MRF is a CELL-ZONE
formulation in this build, not an interface**.

### 2. Image, by hash
`dafoam/opt-packages:latest`, digest
**`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`**. Unchanged.

### 3. What "reachable" means
**G11-1, G11-2a, G11-2b, G11-3, G11-4 and G11-5 carry over from D11 §3 with every
THRESHOLD unchanged to the digit** — plant floor `1.0e-6`, clean tolerance `1.0e-12`,
derivative floor `1.0e-12`, FD band `5.0e-2`, FD step `h = 1.0e-3 m/s` central on
`patchV[0]`. Substrate, driver, objective and mesh are byte-identical to D11-D′.
**The plant MAGNITUDE is the only registered quantity that moved, and §0 names it.**

### 4. What "unreachable" means, and the verdict it maps to
D11 §4 plus D11-D′ §4's added clause, both carried over: absent capability →
**`BLOCKED`**; NaN/inf → **`GATE FAIL`**; all-exactly-zero derivative → **`GATE FAIL`**;
bit-identical MRF-on/MRF-off derivatives → **`GATE FAIL`**; G11-5 outside band →
**`GATE FAIL`**; blind plant, noisy clean copy, **or a fatal originating in this lane's
own files or in a stalled primal** → **`NOT A RESULT`**, never `BLOCKED`, because
`BLOCKED` requires reaching the capability first. All six hold → **`GATE REACHED`**.

### 5. The planted control — on the MRF zone, magnitude per §0
`omega = 30.0 rad/s` versus an inert `0.0`, substituted from `OMEGA_PLACEHOLDER`,
asserted landed by the launcher before each container, read back off disk by
`d11o_grade.py:read_omega_from_disk()` which refuses unless the exact value is present.
Refusal text, discrimination control and the non-emptiness assertion are unchanged.
**Proven able to refuse:** `python3 d11o_grade.py --selftest` — 7/7 green before this
commit.

### 6. Cost
- **Predicted: 1.0 core-min.** Measured basis: D11-D′'s six containers cost 0.8334
  core-min with two of five stages dying early; D11-O′ runs all five to completion, and
  a completed primal+adjoint on this substrate measured 0.1667 core-min against 0.1167
  for a primal alone.
- **Registered cap: 5.0 core-min**, same guard, same 240 s per-stage timeout.
  **An overrun STOPS the probe.**
- `$0.00086` derived — **DERIVED, NOT MEASURED**.
- `cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED`.
- **D11's 0.7166 and D11-D′'s 0.8334 core-min are named separately as waste in
  `docs/COST_CALIBRATION.md` and are NOT absorbed into this row's ratio.**

### 7. np and decomposition
`np = 1`, `numberOfSubdomains 1`. **With np = 1 the parallel-determinism question does
not arise.**

### 8. What this probe does NOT establish
D11 §8 verbatim, plus one addition earned by §0: **it establishes nothing about MRF at
engineering rotational rates.** Whatever it returns is a statement about a 30 rad/s
zone. **The measured fact that a 300 rad/s zone stalls this steady substrate stands and
must be carried into D11's own pre-registration**, which will need either a rotating-
frame-appropriate case or an unsteady formulation.

### 9. Frozen instruments (md5 at this commit)
| file | md5 | note |
|---|---|---|
| `d11o_run_script.py` | `2975373099a6125a1c028a935b145e73` | **byte-identical to D11's and D11-D′'s** |
| `d11o_stage_and_run.sh` | `de2beb5e2472b4028fdccbdd28d7bfae` | `OMEGA_PLANT` and paths |
| `d11o_grade.py` | `2b88644c2c56c1b0f432b910867168b8` | `OMEGA_PLANT` constant, paths, labels |
| `d11o_case/constant/MRFProperties.template` | `e7d601ae02d9a3bc1c9f221b6792dea5` | **byte-identical to D11-D′'s corrected layout** |
