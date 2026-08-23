# DPW8_V2 L4 divergence — diagnosis RESULTS

**Date:** 2026-08-23 (box clock)
**Team:** cfd
**Pre-registration:** `verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_PREREGISTRATION.md`,
frozen at commit **`99f939ee`** (full: `99f939ee21ac5debbe6981e8f958bad02db4b82b`).
Disk sha256 re-verified today: **`97938760db07b3a116da723df88b2440d528a79391d528bcc4a2a4ae9704d399`**.
Cited by commit sha as §10 of that document requires.
**Grading reader:** `verification/runs/DPW8_V2_runs/analyse_l4_diag.py`, committed **before launch** at
**`30d93a0c`** (full: `30d93a0cc8937051044a896539445e387ddda042`). Disk == committed blob, re-verified
today (both sha256 `c557f390d577fe9276a6ae5a5e6914cb3d9c23e3395d745340333317936524e2`). The
supervisor read the full reader diff as a diff (`SUPERVISION_CHARTER.md` §3, personal check) and
found it faithful to the freeze.
**Parent record:** `verification/campaign/DPW8_V2_joukowski.md` §3-CORRECTION, §3a, §3b.
**Grading transcript (in-tree):** `verification/runs/DPW8_V2_runs/L4_DIAG_GRADING_OUTPUT.txt`
(md5 `49ef5a3bcc8dede9909291931d8790dc`), regenerated deterministically for this record, exit 0,
byte-identical to the copy filed at each arm's `POSITIVE_CONTROL.txt` (§5 requirement).

**Status of the diagnosis question (§7 outcome map cell): `PENDING`.**
**Status of the L4 rung: `NOT GATED`, unchanged.**

---

## 0. Standing statement — what this document is not

Per §0 of the frozen pre-registration, and repeated here so no reader can extract more than was
registered:

- **The L4 rung of DPW8_V2 remains `NOT GATED`.** Nothing in this document creates a path to
  gating it.
- **No `PASS`, `GATE REACHED` or `GATE FAIL` is issued from this pre-registration.** There is no
  physics gate here to pass or fail. The rule-1 vocabulary appears below only for the diagnosis
  question (§7 of the freeze) and for run completion (§6 of the freeze).
- **No CL, Cd, Cp or grid-convergence claim is drawn from either arm.** Both arms ran 600
  iterations of a 3000-iteration case. Every coefficient quoted below is a **stability
  indicator**, not a physics measurement, and **nothing here may be cited as a DPW8_V2 result.**
- **`BOUNDED` / `NOT BOUNDED` are the pre-registration's stability-indicator outcome labels and
  are not gate verdicts.** They sit deliberately outside the rule-1 vocabulary.

---

## 1. Launch and provenance

Both arms were launched **2026-08-23T20:01Z** by the prior session's lane, from
`verification/runs/DPW8_V2_runs/launch_l4_diag.sh`, and both reached their terminal state before
that session ended.

| arm | LAUNCHED_AT | FINISHED_AT | wall s | ranks |
|---|---|---|---:|---:|
| `run_L4_diagA_relax` | 2026-08-23T20:01:34Z | 2026-08-23T20:03:38Z | 124.26 | 1 |
| `run_L4_diagB_scheme` | 2026-08-23T20:01:36Z | 2026-08-23T20:20:38Z | 1142.22 | 1 |

`run_L4_gate` was treated as evidence and is read-only throughout (§2, §9.5 of the freeze). It was
not written, moved, renamed or deleted at any point.

### 1.1 One change per arm — asserted, not asserted-about

Verified by the supervisor personally from both `PRELAUNCH_DIFF.txt` files. For each arm the
`0/` diff is empty, the `constant/` diff is empty, and the `system/` diff shows **exactly** the
declared lever plus the common `endTime 3000; → endTime 600;` edit, and nothing else.

**Arm A** (`run_L4_diagA_relax/PRELAUNCH_DIFF.txt`, md5 `0114e192ef0cebc71e6afa06eb92183a`):

```
system/controlDict:  endTime 3000;  ->  endTime 600;
system/fvSolution:   fields    { p 0.25; }                    ->  fields    { p 0.15; }
                     equations { U 0.6; k 0.6; omega 0.6; }   ->  equations { U 0.3; k 0.3; omega 0.3; }
```

**Arm B** (`run_L4_diagB_scheme/PRELAUNCH_DIFF.txt`, md5 `7b4a757398674d376f354700e02c6098`):

```
system/controlDict:  endTime 3000;  ->  endTime 600;
system/fvSchemes:    div(phi,U)  bounded Gauss linearUpwind grad(U);  ->  div(phi,U)  bounded Gauss upwind;
```

Both diff files record the baseline as `run_L4_gate` and the prereg as `99f939ee`.

---

## 2. Positive control block — quoted verbatim (freeze §5, standing rule 3)

A zero from a reader not shown able to see a non-zero is not evidence. §5 requires this block's
full output to be quoted in the results record. It is reproduced verbatim from
`verification/runs/DPW8_V2_runs/L4_DIAG_GRADING_OUTPUT.txt` (and identically from each arm's
`POSITIVE_CONTROL.txt`).

```
==============================================================================
POSITIVE CONTROL BLOCK (pre-registration section 5) -- standing rule 3
A zero from a reader not shown able to see a non-zero is not evidence.
==============================================================================
C1  archived diverged L4 log  md5 OK
    bounding k events found: 2 -> [(262, 2448938.729), (264, 2432568.241)]
    C1 PASS -- reader demonstrably sees the known non-zero signature
C2  healthy L3 log  md5 OK
    bounding k events found: 0
    C2 PASS -- this zero is admissible ONLY because C1 above returned 2 from the same function in this same invocation
C3  archived diverged L4 coefficient.dat  md5 OK
    header-identified column indices: {'Time': 0, 'Cd': 1, 'Cl': 4}
    iter 201: Cd=-563.6550 Cl=-396.5607  (expected -563.6550 / -396.5607)
    iter 401: Cd=-332.8891 Cl=-8.8679  (expected -332.8891 / -8.8679)
    max|Cd| 100-600 = 779.795 at iter 105 (expected 779.795 at 105)
    max|Cd| 300-600 = 431.226 (expected 431.226)
    C3 PASS
C4  avg y+ at Time 600: diverged L4 = 122.159 (expected 122.159), healthy L3 = 3.32571 (expected 3.3257)
    C4 PASS
```

**C1–C4: `PASS`.** All four expectations of §5 reproduced exactly, in one invocation, on the
md5-asserted archive files.

**C5 — the plant into the arm's own file.** Quoted verbatim from the same transcript (the block
is emitted per graded arm; only Arm B reached grading, see §3):

```
C5  arm's own max|Cd| (17520.5) exceeds the nominal plant; plant raised to -175205 per section 5
C5  planted Cd = -175205 at iteration 350 (line index 362) into a scratch copy of run_L4_diagB_scheme's own file
    read back: max|Cd| (100, 600) = 175205, max|Cd| (300, 600) = 175205, expected 175205 for both
    C5 PASS -- reader demonstrably reads THIS arm's file
    arm's real file unmodified (md5 5478d26600e67ec73c8d6d0d58845657 before and after)
```

**C5 on Arm B: `PASS`.** The nominal plant of −9.8765e+02 was exceeded by the arm's own
max |Cd| = 17520.5, so the reader raised the plant to 10× the arm's own maximum
(−175205) exactly as §5 pre-declares, and read it back exactly. The arm's real
`postProcessing/forceCoeffs1/0/coefficient.dat` is byte-unchanged
(md5 `5478d26600e67ec73c8d6d0d58845657` before and after); the plant lived only in a scratch copy.

C5 was **not** run for Arm A: §5 places the plant "before that arm's verdict is computed", and Arm
A never reached grading because it failed §6 completion (§3 below). No verdict was computed for
Arm A, so no plant was owed.

---

## 3. Arm A — `run_L4_diagA_relax` (relaxation lever only): **`BLOCKED`**

**Verdict: `BLOCKED` under §6 of the freeze.** An arm that fails any completion clause is
`BLOCKED`, not NOT BOUNDED. The arm was **not graded** against B1–B4, and no BOUNDED/NOT BOUNDED
label attaches to it.

### 3.1 Completion clauses (freeze §6) — all false

| clause | required | measured |
|---|---|---|
| solver `rc = 0` | 0 | **136** (`solver.rc`: `Command terminated by signal 8` — SIGFPE) |
| `End` line in log | present | **absent** |
| last `Time =` == `endTime` (600) | 600 | **182** (`log.simpleFoam:5180`) |
| `ExecutionTime` line count == 600 | 600 | **false** |
| fields `U p k omega nut` under `600/` | present | **`600/` does not exist** (last written time dir `150/`) |
| age guard: every field under `600/` newer than `0/U` | holds | **not evaluable — no `600/`** |

The reader's own line, verbatim from the transcript:

```
    completion clauses: rc_zero=False, End_line=False, last_time_is_endTime=False, ExecutionTime_count=False, time_dir_present=False, fields_present=False, age_guard=False
  -> BLOCKED (pre-registration section 6: run did not complete). Not graded. A crash is a finding and goes to the supervisor for triage.
```

The §6 early-convergence exception did not fire: the log carries no
`SIMPLE solution converged in N iterations` line, consistent with §3b of the parent record.

### 3.2 Supervisor triage of the Arm A crash — TRIAGE, NOT A GRADE

*This subsection records the supervisor's personal crash triage (`SUPERVISION_CHARTER.md` §3
check 2: a crash is a finding until triage says otherwise). It is diagnostic narrative. It is
**not** a grade, it does not relabel the arm, and the `BLOCKED` label in §3 stands unaltered by
anything written here.*

**Toolchain ruled out.** The launcher is clean: `launcher.out` shows the OpenFOAM bashrc sourced
in-command, `simpleFoam` resolving to
`/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/simpleFoam`, `checkMesh` run
(`log.checkMesh` ends `Mesh OK.`), and the 4450 s wall cap **untouched** — the arm died at
124.26 wall s, 3.6 % of its cap. This is not the §9.1 PATH failure and not a budget stop.

**The crash is the divergence itself.** SIGFPE (signal 8, `rc = 136 = 128 + 8`) was raised inside
`Foam::symGaussSeidelSmoother::smooth` during the `U` momentum solve
(`log.simpleFoam:5184–5186`), with FPE trapping enabled at startup (`log.simpleFoam:18`,
`trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE)`). By the last written
coefficient row (iteration 181, `postProcessing/forceCoeffs1/0/coefficient.dat`) the
header-identified **Cd = 1.6026e+37** and **Cl = 8.0168e+37**. The arm was in unbounded
floating-point growth and the SIGFPE is that growth reaching overflow. **Supervisor's finding: a
case/method finding, not a toolchain artifact.**

*Recorded discrepancy, resolved to the header-identified column.* The relayed triage summary gave
the terminal force coefficients as "~1e35". The header-identified Cd/Cl columns of that same final
row read 1.6026e+37 / 8.0168e+37; the `CmRoll` / `CmYaw` / `Cs(f)` columns of the row read
∼1.6e+35. This record quotes the header-identified columns per §2.1 of the freeze, which forbids a
hardcoded index. The order of magnitude does not enter any clause, label or verdict — Arm A was
never graded — so nothing above or below turns on it.

**The failure-mode shift, recorded because it is the informative part.** The two divergences are
not the same divergence:

| | `run_L4_gate` (recorded divergence) | Arm A (deeper under-relaxation) |
|---|---|---|
| iterations survived | 3000 (relaunch reached 1137 before external kill) | **182**, then SIGFPE |
| `bounding k` events | **2** (iterations 262, 264; kmax 2,448,939 / 2,432,568) | **0** — zero lines matching `bounding k` in the whole log |
| late |Cd| behaviour | **pinned at ≈431** from iteration 300 through 600 | **unbounded growth to ~1.6e+37 by iteration 181** |

Deeper under-relaxation did not slow the failure — it converted a *bounded-but-wrong* pinned state
into an *overflowing* one, and it did so without the turbulence limiter ever firing. Whatever is
wrong is not being reached through `k` bounding in this arm. **This is a triage observation, not a
registered measurement, and it licenses no conclusion under §7.**

---

## 4. Arm B — `run_L4_diagB_scheme` (momentum convection lever only): **NOT BOUNDED**

**Run completed.** All §6 clauses hold, verbatim from the transcript:

```
    completion clauses: rc_zero=True, End_line=True, last_time_is_endTime=True, ExecutionTime_count=True, time_dir_present=True, fields_present=True, age_guard=True
    age-guard margins vs 0/U (s): {'U': 1142.6, 'p': 1142.7, 'k': 1142.6, 'omega': 1142.7, 'nut': 1142.6}
```

`solver.rc` = 0; `End` at `log.simpleFoam:16943`; last `Time = 600`; `ExecutionTime` count 600;
`U p k omega nut` all present under `600/`; every one of them newer than the arm's own `0/U` by
≈1142.6 s — i.e. by the whole duration of the run, which is what the age guard exists to
establish.

**Grading against the four pre-registered clauses of §4. All four fail.**

| clause | threshold (frozen §4) | measured | outcome |
|---|---|---:|---|
| **B1** no `bounding k` at `Time > 50` | 0 events | **1 event**, iteration **136**, kmax **40,040,962.66** | FAIL |
| **B2** max \|Cd\|, iterations 100–600 | < 30 | **17,520.5** at iteration **105** | FAIL |
| **B3** max \|Cd\|, iterations 300–600 | < 5 | **5,359.82** at iteration **303** | FAIL |
| **B4** avg y+ on `airfoil` at Time 600 | < 20 | **189.906** | FAIL |

**Arm B outcome label: `NOT BOUNDED`** (B1=False B2=False B3=False B4=False). Per §4, any one
clause failing makes the arm NOT BOUNDED; all four failed, so no clause-combination caveat of the
kind §4's B4 paragraph anticipates is in play.

**Context, explicitly not a physics result:** Cd(600) = −2107.33, Cl(600) = −1439.23. These are
stability-indicator readings of a diverged 600-iteration truncation of a 3000-iteration case and
are recorded only so the terminal state is on the record. **They are not a DPW8_V2 coefficient and
may not be cited as one.**

*Also on record, unregistered and drawn no conclusion from:* Arm B's single k-bounding event is
**16× larger in kmax** than either of the gate run's two (40.0e6 vs 2.45e6/2.43e6), and comes at
iteration 136 rather than 262/264. Under-relaxation was untouched in this arm
(`p 0.25 / U,k,omega 0.6`, §3 of the freeze), so the comparison against the gate run is
lever-clean. Recorded as an observation; it is not a §4 clause and licenses nothing.

---

## 5. Diagnosis — §7 outcome map: **`PENDING`**

The frozen outcome map's applicable row is *"any | `BLOCKED` → Diagnosis is `PENDING` on the
blocked arm."* One arm `BLOCKED`, one arm NOT BOUNDED. The reader's own emission:

```
  Arm A (relaxation only)      : BLOCKED
  Arm B (momentum scheme only) : NOT BOUNDED
  -> PENDING on the BLOCKED arm. A single BOUNDED arm plus a BLOCKED arm
     licenses only that that one lever is sufficient; nothing about the other.
OUTCOME_MAP_CELL: PENDING
```

**Outcome map cell: `PENDING`.** The registered diagnosis question — *is the L4 divergence a
startup/relaxation robustness failure, or something at the L4 discretisation level?* — is **not
answered**.

### 5.1 What IS established — stated exactly, and no wider

Two narrower facts, and they are the whole of what this experiment licenses:

1. **The momentum-convection lever is eliminated as a sufficient rescue.** Established
   **formally**, by Arm B: a completed run, graded against the four frozen clauses, NOT BOUNDED on
   all four. Dropping `div(phi,U)` from `bounded Gauss linearUpwind grad(U)` to first-order
   `bounded Gauss upwind` does not restore boundedness at L4.
2. **The relaxation lever produced a harder divergence.** Established as a **triage finding
   beside a formal `BLOCKED`** (§3.2), not as a graded measurement. Arm A carries the label
   `BLOCKED` and nothing else.

### 5.2 What is NOT established

- **No cause is asserted.** The relaxation hypothesis is **not** eliminated in the formal sense
  Arm B eliminates the convection hypothesis — Arm A was `BLOCKED`, and a blocked arm licenses
  nothing about its lever. The §7 row for NOT BOUNDED / NOT BOUNDED (which would have read
  `NOT A RESULT` and eliminated both cheap hypotheses) **does not apply here** and is not borrowed.
- **No relabelling of Arm A.** §6 is frozen; a crash is `BLOCKED`. The triage in §3.2 is
  informative and changes no label. There is no post-hoc route by which an overflowing arm becomes
  a graded NOT BOUNDED.
- **L4 stays `NOT GATED`, and nothing in this document is a physics result.** No CL, no Cd, no
  Cp, no grid-convergence claim, from either arm, in any window.

---

## 6. Cost (standing rule 12)

**Unit: core-minutes = wall s × ranks ÷ 60.** Both arms single-rank, so core-minutes = wall
minutes.

| item | figure | source |
|---|---:|---|
| Arm A solver wall | 124.26 s | `run_L4_diagA_relax/solver.time` |
| Arm B solver wall | 1142.22 s | `run_L4_diagB_scheme/solver.time` |
| Arm A core-minutes | **2.07** | 124.26 × 1 ÷ 60 |
| Arm B core-minutes | **19.04** | 1142.22 × 1 ÷ 60 |
| solver subtotal | **21.1 core-min** | sum |
| `checkMesh` + preflight, both arms | ≈ 0.4 core-min | `log.checkMesh` per arm |
| **total spend** | **≈ 21.5 core-min** | |
| dollar figure | 21.5/60 × $0.0513 = **$0.018** | derived |
| registered cap (freeze §8) | 150 core-min total, **75 per arm** | prereg §8 |
| against cap | **21.5 of 150 total; 2.07 and 19.04 against 75 each** — under, both ways | |
| against projection | projected ≈ 61 core-min; actual ≈ 21.5 (Arm A stopped early by its crash) | |

**`cost_basis`: reported-by-owner rate.** $0.0513/core-h, c7a.4xlarge, **owner-stated
2026-08-21/22**. The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so the
dollar figure is **derived, not measured**. The **wall seconds are measured**, from each arm's
`solver.time` file. The figure is gross; no row exceeded 3600 wall s, so there is no stall to
separate out. No overrun occurred and no budget was re-issued.

Under the 2026-08-21 blanket this is far under $25 and pre-authorised; it is costed here anyway,
because a blanket is not a per-item read (rule 9).

---

## 7. Successor decision and docket referral

**Supervisor's decision: no further L4 diagnosis compute now.**

Both cheap single-lever hypotheses have been spent: relaxation produced a harder divergence
(`BLOCKED` by crash, triage on record), momentum upwinding returned NOT BOUNDED on all four
clauses. The remaining suspects — the `omega` wall boundary condition at L4's first-cell spacing,
the near-wall treatment / wall functions, and the linear-solver stall documented at §3b of the
parent record — are a **third-lever question** and are **not** authorised by this
pre-registration, whose gates closed at first compute.

That question is **referred to the docket as an open item needing its own costed
pre-registration**, or an explicit decision to record the DPW8_V2 family as stopping at L3. No
compute is bought here for it.

**Family standing after this diagnosis:**

| rung | status |
|---|---|
| L1 (feasibility) | `PASS` |
| L3 (physics) | `PASS` |
| **L4 (fine)** | **`NOT GATED`** — with this diagnosis on record; the diagnosis question itself `PENDING` |

**Explicit closing statement, per §0 and §7 of the freeze: L4 remains `NOT GATED`, and nothing in
this document is a physics result.**

---

## 8. Artifact inventory — committed vs disk-only

Every number above cites a file that is still on disk. This table declares which of those files
are **in git** and which are **disk-only**, so no reader mistakes an uncommitted artifact for a
tracked one.

### Committed with this record

| path | md5 |
|---|---|
| `verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_RESULTS.md` | this file |
| `verification/runs/DPW8_V2_runs/L4_DIAG_GRADING_OUTPUT.txt` | `49ef5a3bcc8dede9909291931d8790dc` |
| `run_L4_diagA_relax/POSITIVE_CONTROL.txt` | `49ef5a3bcc8dede9909291931d8790dc` |
| `run_L4_diagA_relax/PRELAUNCH_DIFF.txt` | `0114e192ef0cebc71e6afa06eb92183a` |
| `run_L4_diagA_relax/LAUNCHED_AT`, `FINISHED_AT`, `solver.rc`, `solver.time`, `launcher.out` | — |
| `run_L4_diagA_relax/log.checkMesh` | `d5a87994685ce98b08d5967bca7f2933` |
| `run_L4_diagA_relax/log.simpleFoam` | `b66a9829b426329e60bdf74f57621114` |
| `run_L4_diagA_relax/postProcessing/forceCoeffs1/0/coefficient.dat` | `6c79ddddcb7686255d1d6e75898c3d8d` |
| `run_L4_diagA_relax/postProcessing/yPlus1/0/yPlus.dat` | `2bd878160e0f763438fd9394a78105b0` |
| `run_L4_diagB_scheme/POSITIVE_CONTROL.txt` | `49ef5a3bcc8dede9909291931d8790dc` |
| `run_L4_diagB_scheme/PRELAUNCH_DIFF.txt` | `7b4a757398674d376f354700e02c6098` |
| `run_L4_diagB_scheme/LAUNCHED_AT`, `FINISHED_AT`, `solver.rc`, `solver.time`, `launcher.out` | — |
| `run_L4_diagB_scheme/log.checkMesh` | `aeb560b054815329ffaf049c683bbb18` |
| `run_L4_diagB_scheme/log.simpleFoam` | `edbd86f1ec9c39bb0e9e0e302344a012` |
| `run_L4_diagB_scheme/postProcessing/forceCoeffs1/0/coefficient.dat` | `5478d26600e67ec73c8d6d0d58845657` |
| `run_L4_diagB_scheme/postProcessing/yPlus1/0/yPlus.dat` | `1799d21ebd1e297013e85e7c9139b24e` |

(Arm paths are relative to `verification/runs/DPW8_V2_runs/`.)

Already in git, cited above and not re-committed: the frozen pre-registration (`99f939ee`), the
grading reader (`30d93a0c`), `launch_l4_diag.sh`, and the whole of `run_L4_gate` and
`run_L3_physics`/`run_L1_feasibility` that the positive control reads.

### Disk-only, deliberately not committed

| path | why, and what attests it |
|---|---|
| `<ARM>/constant/` (incl. `polyMesh`) | 12 MB per arm, 24 MB total, **byte-identical to the tracked `run_L4_gate/constant/`** — each arm's `PRELAUNCH_DIFF.txt` records `diff -r constant/` as `(empty: identical)`. Committing it would duplicate a tracked mesh. |
| `<ARM>/0/` | Byte-identical to tracked `run_L4_gate/0/`; each `PRELAUNCH_DIFF.txt` records `diff -r 0/` as `(empty: identical)`. |
| `<ARM>/system/` | Differs from tracked `run_L4_gate/system/` by exactly the lines transcribed in §1.1 and reproduced in full inside the committed `PRELAUNCH_DIFF.txt`. The diff file, not the directory, is the record. |
| `<ARM>/<numeric time dirs>/` — Arm A `50/ 100/ 150/`, Arm B `50/ … 600/` | Solver field output. Bulky and reproducible; the **completion evidence they carry is attested by the committed grading transcript**, which records the §6 clause results and the per-field age-guard margins (`U 1142.6 s`, `p 1142.7 s`, `k 1142.6 s`, `omega 1142.7 s`, `nut 1142.6 s` for Arm B) read from those directories at grading time. |

**Honest limit:** the age-guard margins and the `600/` field presence are, in this record, attested
by the committed transcript rather than by committed field files. Re-deriving them independently
requires the disk-only time directories, which are present on this box now but are not preserved
in git. Stated so a later reader knows exactly which of these numbers is reproducible from the
repository alone and which is not.
