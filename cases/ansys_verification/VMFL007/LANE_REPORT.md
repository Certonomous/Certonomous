# VMFL007 — LANE REPORT — pre-registration built and FROZEN, compute NOT started

**`ansys-lane-opus`, 2026-08-25.** Report of record to the
`ansys-verification` supervisor. The lane→supervisor message channel is one-way,
so this committed file is the primary channel.

> **STATE: `PENDING`. The pre-registration is FROZEN at
> `48f7a9bf930fbd06bf23ba4b6469754f879cb74e` (2026-08-25T16:51:56Z).
> `verification/runs/ansys_verification/VMFL007/` DOES NOT EXIST. No graded
> solver has run. THE FOUR §3 CHECKS AND THE COMPUTE UNLOCK ARE YOURS.**

---

## 1. WHAT I ACTUALLY DID

**Read first, in the charter's order:** `CLAUDE.md` in full; then
`ANSYS_VERIFICATION_CHARTER.md` — **at `HEAD`, not from the working tree, see
§4.5**; then the manual's VMFL007 page. Title-page verified per rule 15 (§4.2 of
the charter): the sidecar's head and the PDF's metadata (`Title: Fluid Dynamics
Verification Manual`, DocBook/XEP, **290 pages**, Release 2026 R1, March 2026)
agree with the charter's recorded fingerprint. Verified on the **title page**,
not on the filename or the hash.

**Archive.** Copied `VMFL007_WB.wbpz` to `/tmp/claude-1000/` and unpacked it
**there**. sha256 `2ba6f97b…` identical before and after; nothing under
`/home/ubuntu/ansys-vm2026r1/` was written, moved or deleted, and nothing was
unpacked inside the repository.

**Built and committed, in two acts so the ordering is evidentiary:**

| commit | UTC | contents |
|---|---|---|
| **`23091132c4971eb94dbcdf9243559b9c3e556304`** | **2026-08-25T16:46:36Z** | case tree (8 files), `grade_vmfl007.py`, `run_vmfl007.sh`, smoke evidence (6 logs) — **message declares no graded compute** |
| **`48f7a9bf930fbd06bf23ba4b6469754f879cb74e`** | **2026-08-25T16:51:56Z** | **`PREREGISTRATION.md` — THE FREEZE**, alone |

**Six peer commits landed between the two.** The private-index protocol handled
it: HEAD captured once per invocation, `diff-tree` asserted only my paths, CAS on
`update-ref`, and the post-commit `git diff HEAD~1 HEAD --stat` verified only my
files in both cases. No foreign rows were left uncommitted by this lane.

**Blob hashes at the freeze `48f7a9bf`:**

| artifact | blob |
|---|---|
| **`PREREGISTRATION.md`** | **`76adce6af94e18563d304d8d2578a39b6de3343d`** |
| **`grade_vmfl007.py`** | **`9a727216a73eedcdfbeff2b40c0f5a8f65db65e6`** |
| **`run_vmfl007.sh`** | **`71d26af229d24a6467de0b78e4a2e2da08bf259d`** |

`grade_vmfl007.py --verify-frozen 48f7a9bf` → **`frozen OK` (57 612 bytes)**.

---

## 2. WHAT I MEASURED

### 2.1 Your closed form — re-derived independently. **You are not wrong.**

| quantity | my value | yours | verdict |
|---|---|---|---|
| `τ_w` | **378.2623086489655 Pa** | 378.2623 Pa | **CONFIRMED** |
| `Δp` | **60521.96938383448 Pa** | 60521.969 Pa | **CONFIRMED** |
| vs printed 60.52 kPa | **+0.0032541042 %** | +0.0033 % | **CONFIRMED** |
| `Re` generalised | **84.59737930087186** | 84.60 | **CONFIRMED** |

`Re` was cross-checked by the Metzner–Reed form, which shares no algebra with
`8ρV²/τ_w` and agrees to **15 significant figures** (…087188 vs …087186).

### 2.2 The archive — three findings your brief did not carry

Read byte-exact from the configured case's HDF5 settings blob:
`(density (constant . 1000))`, `(viscosity (non-newtonian-power-law 10 0.4 0 0) …)`,
`(rp-axi? . #t)`, `(rp-3d? . #f)`. Your stated setup is **confirmed**. Beyond it:

1. **The inlet is NOT uniform 2 m/s.** The manual reads *"Fully developed velocity
   profile at inlet with an average velocity of 2 m/s"*, and the archive holds a
   20-point profile export whose velocity column my analytic
   `u(r) = 3.142857142857143 · (1 − (r/R)^3.5)` reproduces to **0.09–0.15 %**.
   A uniform inlet would need ~10 % of the pipe as entrance length and would not
   give the target. **The case imposes the analytic profile and asserts it.**
2. **Both Fluent viscosity limits are `0 0` — DISABLED.** OpenFOAM class A
   *requires* `nuMin`/`nuMax`, so the case must **prove** its clips never bind.
   It does (§2.4).
3. **The archive's own stored result disagrees with the manual's printed one.**
   `VMFL007_validate_table_pressure2.srp` reads **60498.203 Pa (−0.0360 %)**; the
   manual tabulates Fluent at **60.41 kPa (−0.1818 %)**. The archive is **5×
   closer** to the target than the manual says it is. **Recorded, not resolved**;
   drafted as `N-AV14`.

### 2.3 The `powerLaw` trap — closed, and it is worse than described

Read from the v2606 sources, not from memory. **Class B has NO `k` key at all**
— it multiplies `nu0` taken from the transport model:

| | **A (chosen)** | **B (the trap)** |
|---|---|---|
| keys | `k`, `n`, `nuMin`, `nuMax` | `n`, `nuMin`, `nuMax` — **no `k`** |
| ν | `clamp(k·γ̇^(n−1))`, `k` is `dimViscosity` | `clamp(ν₀·γ̇^(n−1))` |

`powerLawCoeffs_` is read with `optionalSubDict` and only `n`/`nuMin`/`nuMax` are
`readEntry`-ed, so **a stray `k` is silently ignored**. And the archive's own
material blob carries a leftover `(constant . 9.999999699999999e-06)` — **so the
specific stray constant an incorrect port would pick up makes the error EXACTLY
1000**, and Δp would read **3818.7 Pa** instead of 60522 Pa.

**Class A is selected via `laminar { model Stokes; }`, and the choice is asserted
on four independent channels** (log transport model; log laminar model +
`generalizedNewtonian` absent; the dictionary's `k == 0.01` before any solver
starts; and **`min(nu)` on disk at `endTime` in `[2e−05, 8e−05]`** against the
continuum wall value `4.298435325556426e−05` — class B would read `~4.30e−08`,
**a factor of 1000 away**).

**The kinematic conversion, shown:** Fluent's `μ = k γ̇^(n−1)` is **dynamic**;
OpenFOAM class A's `k_` carries `dimViscosity` = m²/s, **kinematic**. So
`k_OF = 10/1000 = 0.01`. **The conversion IS needed.** Using the manual's `k` raw
inflates Δp by `1000^0.4 = 15.848931924611133` → **959 208.6 Pa**. A **second**
factor of 1000 runs the other way: `simpleFoam`'s `p` is kinematic, so
`Δp_Pa = ρ·Δp_foam`. Both asserted, neither a comment.

### 2.4 Measured in the smoke test, before the freeze

| quantity | measured | predicted | agreement |
|---|---|---|---|
| inlet patch area | `1.363469252911e-08 m²` | `½R²sin(t) = 1.363469252912774e-08` | **12 sig. figs.** |
| `sum(phi)/(V·A)` | **1.000600** | 1 + O(h²) | +0.060 % at L1 |
| `max(Ux)` at inlet | **3.142847411860** | `u_max = 3.142857142857143` | shape confirmed |
| `min(nu)`, `max(nu)` | 1.71e−05, 0.1919 | class A order, both clips inert | class A |
| `checkMesh`, all 3 levels | non-orth **0**, skew **0.3332**, AR **160.0** | — | Mesh OK |

### 2.5 The wedge bias — **`sec(t/2) − 1`, and the lane who corrected you was right**

Derived independently from the force balance `Δp·A = τ_w·P·L`: the true sector has
`P/A = 2/R`, the flat wedge `P/A = 2/(R cos(t/2))`, ratio **`sec(t/2)`**.

**I departed from team precedent: `t = 1°`, not 5°.** The criterion, stated
before the choice: **the bias — which no refinement removes — must sit BELOW the
reference's own rounding half-width (± 5 Pa = ± 0.00826 %)**, so a bias the triple
cannot see is also one the reference cannot resolve.

| | Δp bias | vs ± 0.00826 % | |
|---|---|---|---|
| 5° | +0.09526851633199218 % | **11.5× larger** | fails |
| **1°** | **+0.003807838573699485 %** | 0.46× | **meets** |

**Sign: HIGH**, as the clause requires. This is `N-AV9`'s own named mitigation.
**Cost disclosed:** the campaign's wedge angle is no longer uniform and must be
read per case.

---

## 3. THE VERDICT I AM ENTITLED TO

**`PENDING`** — and that is the whole of it. `verification/runs/ansys_verification/VMFL007/`
does not exist; no graded solver has run; **no verdict, tier or column is claimed.**

**Cost so far: the pre-flight smoke test only.** One `simpleFoam` iteration on 625
cells plus `blockMesh`/`checkMesh` at three levels — **ExecutionTime 0.03 s**,
under **0.01 core-minutes**, in `/tmp`, outside the runs tree. **The 60 core-minute
cap is untouched.**

**Pre-registered for the graded run:** point estimate **15 core-min**, cap **60
core-min** (`timeout 3600` per level), **$0.0513 derived** at the cap — 487× under
the $25 pre-authorisation. `cost_basis` is **derived from a measured lab record and
scaled**: VMFL001's 104 wall s for 16 384 cells × 3000 serial iterations = 2.115e−6
core-s per cell-iteration, ×4 for the power-law update and a pressure solve the
smoke test showed needing 429 GAMG sweeps on iteration 1. **Not measured, and the
document says so.**

**Declared ceiling: `GATE REACHED`** — a closed-form reference buys **V** and never
**P**. `HOLDS` is not claimable. **I did not resolve `COVERAGE_ROWS.md` §202's open
question about what P asks for**; the ceiling is declared under your reading, and
changing it is yours, before compute.

---

## 4. WHAT I COULD NOT VERIFY — plainly

1. **That the run converges at all.** `endTime = 10000` and `p 0.3 / U 0.7` come
   from precedent, not from a converged run — a converged run before the freeze is
   exactly the information rule 2 forbids. **If a level misses the §8.2 clauses the
   row is `NOT A RESULT`**, honestly, for ≈ 15 core-minutes.
2. **The observed order.** Declared band `[1.0, 2.5]`, formal 2, with the axis
   viscosity singularity `ν ~ r^−1.5` named in advance as why it may fall below 2.
   **Above 2.5 is declared SUSPICIOUS, not good** — VMFL045-R2's `p = 3.3862` is the
   precedent. It is a prediction and may be wrong.
3. **Whether the `V` column is earned.** Measured at grading per `N-AV7`, not now.
4. **Ansys's internal discrepancy (§2.2 item 3)** is unexplained by me.
5. **A STALE WORKTREE CHARTER — inspected, NOT reverted, REFERRED TO YOU.**
   `docs/charters/ANSYS_VERIFICATION_CHARTER.md` measures **289 lines in the
   working tree** against **662 at `HEAD`** (blob `f5d5c8a7…`, identical at `HEAD`
   and at `75030b12`). The worktree copy is **missing the dated note, Amendment 1.3
   and Amendment 1.4** — the amendment that binds this registration. `git status`
   reports it `MM`. **I read and wrote against the `HEAD` blob.** Rule 10: an
   unexpected change is inspected, never reverted, and the index is the chief's
   call. **I reverted nothing. This is yours or the chief's.**
6. **`birth_certificate.json`** is not minted for these three meshes — the same
   **CHECKED-BUT-UNCERTIFIED** gap charter v1.4 records for the team's other 23.
   Named, not silently passed.

### 4.1 Three faults the smoke test found that a `--selftest` could not

Recorded because they are the warrant for Clause B, from this case's own work:

1. **`volFieldValue` takes `operation`, not `operations`.** The solver exited
   `FOAM FATAL IO ERROR`. **A selftest proves the GRADER, never the CASE.**
2. **The launcher handed its smoke directory back through `$(smoke | tail -1)`** —
   a command substitution, i.e. a **subshell**, where every `exit 1` inside would
   have killed only the subshell and left the script running with an empty value.
   **The same silent-non-gating class as `( set -e; … )`.** Fixed to a file handoff
   with the status gated in the parent.
3. **The `generalizedNewtonian` guard fired on the dictionary's own warning
   comment.** Fixed to strip comments and match a *selecting* line; both arms tested.

### 4.2 The comparator class fix — stated at its **measured** size

Seven comparators exist here. **Three derive no root at all.** Of the four that do:
`grade_vmfl045.py:59`, `grade_vmfl045_r2.py:59`, `grade_vmfl051.py:62` hardcode
`REPO = "/home/ubuntu/Certonomous"`; `grade_vmfl003.py:937` uses three `dirname`s,
which evaluates to `<repo>/cases` — **one level short**.

**BOTH FLAVOURS ARE LATENT AND NO VERDICT IS AFFECTED.** The hardcoded path is
correct on this box. VMFL003's short value is used **only as the `cwd` of a git
subprocess**, where git walks up and the wrongness cannot show — **the defect is in
what the idiom would do if reused as a path root, not in what it does.** I am
saying no more than that, because this team was corrected today for overstating a
defect.

**What is common, and what is fixed:** neither form is ever *checked*, so neither
can fail loudly. Here the root is asked for (`git rev-parse --show-toplevel` from
the file's own directory) and then **checked by inode**. **Demonstrated, not
asserted:** it refuses with `REFUSE:` and exit 2 — no traceback — when the file is
moved to another depth and when it is outside a repository at all.

### 4.3 On `scripts/append_record.py`

Acknowledged and complied with: I used it **nowhere**. All `N-AV` ids in
`PREREGISTRATION.md` §13 are **drafts for you**, and the document says they must be
re-derived by hand from the tail at the committing invocation.

---

## 5. WHAT IS OWED TO YOU

1. **The four §3 checks**, personally: the comparator diff read **as a diff**; the
   smoke-test findings triaged; the closed form and the `sec(t/2)` correction
   verified before belief; **the freeze confirmed committed before compute** —
   `48f7a9bf`, and `verification/runs/ansys_verification/VMFL007/` still absent.
2. **The compute unlock.** Then, and only then:
   `bash cases/ansys_verification/VMFL007/run_vmfl007.sh --prereg-sha 48f7a9bf930fbd06bf23ba4b6469754f879cb74e`
   The launcher refuses without it; all four refusal arms were exercised and each
   returns non-zero.
3. **A ruling on the stale worktree charter (§4.5)** — or its referral to the chief.
4. **A ruling on the `P`-column reading** if §202's open question should change the
   declared ceiling. It must be made **before** compute; after first compute the
   label is closed.
