# DOCKET_DRAFT — proposed docket rows from D460 phase 1

> **DRAFT. NOT APPENDED.** This lane does not write `docs/DOCKET.md`,
> `demo-output/website/agenda/docket.json`, `docs/NUMERICS_KNOWLEDGE.md` or `docs/LAB_STATE.md`.
> Every real append goes through `python3 scripts/append_record.py`, with
> `python3 scripts/check_record_reconciliation.py` run **before** — and, for the docket specifically,
> `python3 scripts/check_docket_reconciliation.py`, because the docket diverges from HEAD by design
> under the private-index protocol (`CLAUDE.md` rule 11). That is the supervisor's job.
>
> Numbers are assigned **at commit, from the tail — the maximum existing number, never a count**,
> and re-derived **in the same shell invocation as the append** because peers commit constantly.
> Re-derived 2026-08-23 for context only: max `D` **474**, max `N-D` **21**. **Do not hard-code
> 475.**

---

## Proposed row 1 — D460 blocker 1 CLOSED, and the novelty claim it closes on is NOT the one the candidate makes

**Status: closed. Zero compute.**

The full-protocol novelty sweep D460 named as blocker 1 is complete: **101 recorded searches across
13 venues, 2026-08-23**, against the house protocol's 63 across 10. Record:
`cases/dafoam/LIAISON_NOVELTY_SWEEP_adf_primal_nonreproduction.md`. Controls per L-234 on all three
search surfaces, in both directions.

**Outcome: PRIOR ART OF THE SAME DEFECT FAMILY WAS FOUND.** `DAFoam/OpenFOAM-AD` **#2**, open since
2026-01-25, author `friedenhe` (DAFoam lead maintainer), 0 comments, **[verbatim, REST]**:
*"If PBiCGStab/DILU are used in fvSolution, both ADR and ADF flow solvers generate wrong results
(flow variables blow up rapidly). … If you comment out PBiCGStab/DILU and use GAMG/GaussSeidel in
fvSolution, the flow solution is correct."*

- **No prior report of D460's specific measurement exists** — nobody has reported the ADF build
  failing to reproduce the plain build's primal, and nobody has located an AD-versus-plain
  divergence at the 8th significant figure of the energy equation.
- **D460 §8's `-1e10` false-convergence finding remains cleanly novel** — `primalMaxRes`,
  `primalMinIters` and `-10000000000` are clean zeros in issues, Discussions and GitHub-global
  search alike.
- **But D460 §9.4's sentence *"No prior art was found for either finding"* is not sustainable for
  the primal finding**, and the candidate must not be filed while it stands.

**Action for the dafoam-supervisor** (D460 is frozen and is not edited by a lane, `CLAUDE.md`
rule 6 — this needs a dated addendum, which is a supervisor call): narrow §9.4's novelty sentence;
strike §9.4's "not covered" list (mdolab mailing lists **do not exist**; CFD-Online, the OpenFOAM
forums, Google Scholar, `OpenFOAM-v1812-AD` and MeDiPack are all now covered and negative; and
`DAFoam/OpenFOAM-AD`, the venue that mattered, **was not on the list at all**); and rewrite §11's
filing tone from *"here is a new defect"* to *"here is a second instance of your open
`OpenFOAM-AD` #2, at the opposite solver polarity, on a compressible transonic case, with the
divergence located to the 8th significant figure."* **That is a better report, not a weaker one** —
it attaches to an issue the maintainer already owns and supplies the digit-level entry point #2
lacks. **SUBMISSIONS REMAIN PARKED; filing is Sanaa's alone.**

## Proposed row 2 — D460 sweep 1 pre-registered and redesigned; PENDING the supervisor's go

**Status: `PENDING`. Pre-registration committed, nothing launched, 0.000 core-min spent.**

`cases/dafoam/d460_sweep1_solver_family/PREREGISTRATION.md`, with the frozen comparator
`analyse_sweep1.py` (sha256 `239c1764c6b2ff8db5736c45f0f5f00f0debba0a4a93e745b080e1e641be7e94`).

**The sweep was redesigned before compute, because the novelty sweep invalidated D460 §7's
version of it.** §7 said: switch `p` from `GAMG` to `PBiCGStab`/`DIC` and read *NaN persists* as
**AD correctness**. `OpenFOAM-AD` #2 reports PBiCGStab/DILU as independently breaking AD builds, so
that arm is **confounded** and its headline reading would have been wrong; `DIC` is additionally a
symmetric preconditioner facing an asymmetric transonic pressure equation. The registered
discriminator is instead **`smoothSolver`/`GaussSeidel`** — non-multigrid, not the pair upstream
reports as broken, already this case's setting for every other equation, and the fix the maintainer
himself named for a GAMG-in-an-AD-build failure in `OpenFOAM-v1812-AD` #2 (2020).

**A control arm was added and is not optional.** D460 §7 sketches one arm; one arm cannot answer the
question, because a trajectory change from the solver swap is indistinguishable from a change in the
AD amplification. Registered: **ARM F-SM** (forward AD) against **ARM P-SM** (plain), identical in
every other respect.

| | |
|---|---|
| predicted cost | **5.0 core-min** (= **$0.0043**) |
| **hard ceiling** | **20.0 core-min** (= **$0.0171**) — **an overrun stops the run** |
| cost_basis | c7a.4xlarge $0.0513/core-h, **owner-stated, reported-by-owner, NOT measured** |
| launch gate | MemAvailable ≥ 12 GiB — read **25.96 GiB** at 2026-08-23T19:59:55Z, satisfied, **nothing launched** |
| run root | `/home/ubuntu/certonomous-runs/D460-sweep1-solver-family/` — **asserted ABSENT at the pre-registration commit** |
| decision | `PASS`/`GATE REACHED` → **conditioning / diagnosability**; `GATE FAIL` → **AD correctness** |

**Phase 2 is not authorised by the pre-registration itself.** It runs only after the
dafoam-supervisor personally verifies the commit (`SUPERVISION_CHARTER.md` §3 — a check that may
not be delegated).

## Proposed row 3 — D460 remains NOT FILING-READY, and the reason has changed

Blocker 1 is closed; **blocker 2, sweep 1, is now pre-registered but unrun**, so the defect class is
still **UNDETERMINED** and the candidate still says so correctly. What has changed is that a
**third** item now stands between D460 and filing-readiness, and it did not exist yesterday: the
§9.4 novelty claim and the §11 filing posture must be revised against `OpenFOAM-AD` #2 (row 1).

## Proposed row 4 — a standing-protocol defect, for whoever owns `PROBLEM_RESEARCH_PROTOCOL.md`

Two statements in §1a were measured stale on 2026-08-23: `curl` to `github.com` HTML **does not**
hang from this host any more (22/22 fetches under a second, and it is the *better* instrument
because it yields deterministic, auditable counts), and the "error while loading" retry test fires
on **every** fetch because the literal string sits in the page template. Detail in
`LESSONS_DRAFT.md`. **Editing a standards document is not a lane's call.**

---

## Proposed numerics rows (`docs/NUMERICS_KNOWLEDGE.md`, `N-D` family) — **conditional, do not append yet**

Both of these are **claims about what a run would show**, and **neither is a measurement.** They are
recorded here only so that the supervisor can append them **after** sweep 1 grades, with the arm
that supports each. **A number whose artifact does not yet exist is not a numerics fact.**

- **Candidate N-D (pending sweep 1):** on A6 N=16, `DARhoSimpleCFoam`, np = 1, the iteration-1
  cumulative-continuity amplification between the forward-AD and plain builds under `GAMG` is
  **`r = 10.029307311562496`** (`-0.05058272456310364` / `-0.00504349133910657`). **This one IS
  measured**, from `s1b.log` and `patched.log`, both on disk — it is listed here because it is the
  registered reference value for sweep 1's band, and it may be worth a numerics row on its own
  regardless of how sweep 1 grades.
- **Candidate N-D (pending sweep 1):** the value of `r` under `smoothSolver`/`GaussSeidel`.
  **Unmeasured. `PENDING`.**
