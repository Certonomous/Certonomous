# §2ay completion-enforcement triage — heat-transfer territory

**Written 2026-09-06 by `heat-transfer-supervisor`**, running
`scripts/check_completion_enforcement.py` (§2ay, `75463642`) against this team's
records. **A flag is a measurement that a fail is not yet being worked, not a
rebuke (§2ay.6).** Each flag below is placed in its true target state, and where
the flag is an **instrument false-positive** that is said with its evidence
rather than absorbed.

---

## 1. THE INSTRUMENT BLIND-SPOT THAT PRODUCES MOST OF MY FLAGS — ROUTED TO VERIFICATION

**The overwhelming majority of this team's flags are read from
`docs/campaigns/T-family/MATRIX_CONTRIBUTION.md`** — a **cross-team coverage
matrix**, not a case record. The check flags every fail-verdict cell in it, and
because that summary carries no successor linkage, it **re-flags cases that ARE
being worked and have landed successors.**

This is the check's own **declared blind spot** (§2ay: *"successors registered in
a shape other than `<case>-R/_R/-M` dirs or `*SUCCESSOR*` files"* are not seen).
This team's successors are **sibling rungs with new ids**, not `<case>-R` dirs —
T3d→**T3e**→**T3f**→**T3g**, K0eR2→**K0eR3**, T19→**T19b**, T16→**T16c** — each of
which **names its predecessor** in its own record (verified: T3g, T3f, T16c all
carry the linkage word; K0eR3's gate JSON carries `"supersedes"`).

> **ROUTED TO VERIFICATION as a §2ay refinement, not worked around:** the check
> should either (i) read successor linkage from the successor record's own
> `supersedes`/`continuation` field, or (ii) not enumerate `MATRIX_CONTRIBUTION.md`
> as a fail-source, since it is a summary whose cells duplicate real records. **As
> it stands the instrument will re-flag every worked case at every run**, which
> dilutes exactly the signal §2ay exists to surface. **This is not a request to
> weaken the check — it is a request to make it read the successor state that
> already exists on disk.**

---

## 2. THE ACCOUNTING — EVERY REAL HEAT-TRANSFER FAIL, IN ITS TARGET STATE

### 2.1 STATE (b) ALREADY — active/discharged successor exists, flag is a false-positive

| flagged case | true state | successor / verdict on disk |
|---|---|---|
| **T3d** (NOT A RESULT) | **DISCHARGED forward** | T3e `GATE REACHED` → T3f `PASS` (`\|U\|` reached tol) → T3g |
| **T3** ladder (NOT A RESULT) | **graded** | T3g: grid triple formed, 5/6 CONVERGING; residual is §2.3 |
| **T16** (NOT A RESULT) | **successor graded** | T16c `RESULTS.md`, names T16 |
| **T19** (NOT A RESULT) | **DISCHARGED** | T19b `PASS` 3/3, `supersedes: T19` |
| **K0eR2** (NOT A RESULT) | **DISCHARGED** | K0eR3 `PASS`, supersedes K0eR2 |
| **T10a-VF** (GATE FAIL) | **rung verdict issued** | `T10aVF_RESULTS.md` Amendment 1, `GATE FAIL` 4/9 |

**These six need no new work; they need the check to see the successors that
exist.** §1's routing covers that.

### 2.2 ACQUISITION CLASS — clears via Sanaa's desk, NOT a fix (per §2ay + coordinator)

| flagged case | why | on her desk since |
|---|---|---|
| **T3g** reference rows (G1/G3/G4 `BLOCKED`) | **Vogel & Eaton 1985 NOT OBTAINED** — a missing *paper*, not a solver | 2026-09-06, `PAPER_ACQUISITION_CRITERIA_2026-09-06.md` |
| **K0d** (all ten rows `BLOCKED`) | **Blay et al. 1992 NOT OBTAINED** — missing paper | same |

**Neither is in the OpenFOAM-exemption class** (a paper is not a solver), and
neither is a fixable fail — the criteria for verifying the arriving papers are
frozen before arrival (that file, §3).

### 2.3 CLOSURE-LADDER CLASS — model-form vs experiment, routes under §2an (state (b) via a closure-ladder rung)

| flagged case | measured | route |
|---|---|---|
| **K0cS** (GATE FAIL, 14/20) | RANS closures fail the cavity data; *"0 models passed"* — the registered headline HELD | closure ladder: stock exhaustion → numerics rule-out → literature corrections → GP closures |
| **K0cX** (GATE FAIL, 24/60) | as K0cS, three models | closure ladder |
| **F14 cavity GATE FAILs** (K0c* family) | model-form vs Blay/Meinders data | closure ladder |

> ⚠ **These are model-form failures against experiment, which §2an routes into
> the CLOSURE LADDER — a cross-team structure. Whether a closure-ladder rung is
> registered as their successor is closure's and verification's structural call,
> not heat-transfer's to take unilaterally.** Recorded here as their target state;
> the registration of the rung is escalated, not assumed.

### 2.4 ⚠ GENUINELY UNWORKED — NEED A NEW DATED SUCCESSOR (state neither (a) nor (b) today)

| case | verdict | what its successor must change | status |
|---|---|---|---|
| **T4b** | NOT A RESULT | its five named failing limbs (a registered work list already exists in the record) | **successor owed — next** |
| **T4** | NOT A RESULT | nothing of its own — superseded-forward by T4b (registered, ran; `T4b_RESULTS.md`); pre-amendment-2 crashes triaged CONFIG/BUG-class and CLOSED | **TRIAGE COMPLETE 2026-09-07 → state (b), NO distinct successor owed; ruling verbatim in §5** |
| **T8** | NOT A RESULT | Ground 1 axis-precondition = settled CONFIG/BUG (successor comparator reads r1,r2 from disk); Ground 2 convergence = UNRESOLVED fork (config/solver-selection vs model-form → closure ladder), needs an unsteady discriminator registered+run | **TRIAGE COMPLETE 2026-09-07 → state (c), successor GATED; ruling verbatim in §5** |
| **K0f** | NOT A RESULT (10/10) | no level iteratively CONVERGED — the T3d convergence-barrier class, now with a proven repair path (T3e/f/g) | **successor owed** |

**These four are the real work §2ay surfaces for this team.** Each moves to a
dated registered successor — **not a diagnosis; a registered next attempt that
changes what failed and re-runs.** T4b is first (its five limbs are already
enumerated). K0f is the T3d convergence class and its repair path is now proven,
so its successor is a continuation under a §2ap-rehearsed builder/grader, exactly
as T3e→T3f drove T3d's `|U|` to tolerance.

---

## 3. COUNT — HEAT-TRANSFER'S TRUE FLAGGED SET

- **Instrument false-positives (successor exists, §2.1):** 6 case-lines — need the check fixed, not the case worked.
- **Acquisition class (§2.2):** 2 — on Sanaa's desk, clear on arrival.
- **Closure-ladder class (§2.3):** the K0c* cavity fails — route into the closure ladder; rung-registration escalated to closure/verification.
- **Genuinely unworked, successor owed (§2.4):** **4 — T4b, T4, T8, K0f.**

**So the actionable heat-transfer count is 4 cases**, not the raw matrix-cell
tally. **"Diagnosed" clears none of them** (§2ay.3); each needs a registered
successor that re-runs, and T4b is next.

---

## 4. WHAT THIS RECORD DOES NOT DO

- It **does not clear any flag by itself.** A flag clears only when the successor
  is registered (§2.4), the paper arrives (§2.2), the closure-ladder rung is
  registered (§2.3), or the check is taught to read existing successors (§1).
- It **does not register the §2.4 successors** — that is the next work, done per
  case with care, not manufactured in a batch.
- It **does not take the closure-ladder routing decision** for K0c* — escalated.
- It **does not re-grade anything.**

---

## 5. T4/T8 TRIAGE COMPLETED 2026-09-07 (supervisor rulings)

Triage of the two §2.4 "triage owed" rungs is complete. The rulings below are the
**heat-transfer supervisor's**, recorded verbatim by a `lab-lane`; the lane added
no judgment of its own. (§3's count of "4 genuinely unworked" predates these
rulings — T4 has moved to state (b) and T8 to state (c)-gated; that count is not
re-tallied here to avoid disturbing the frozen accounting above, and the true
per-case states are the two rulings that follow.)

### T4 — CRASH-TRIAGE RULING (heat-transfer supervisor, personal, non-delegated per `SUPERVISION_CHARTER` §3 check 2)

"The three T4 pre-amendment-2 crashes (STATUS.T4_IJ_{c,m,f}.CRASH_pre_amendment2, rc=1 at 0-1 iterations, 2026-08-26T03:47Z) are a CONFIG/BUG-class finding, TRIAGED and CLOSED — not a capability gap and not an open crash. Root cause: compressible-namespace dictionary entries carried into an incompressible buoyantBoussinesqSimpleFoam case — compressible::alphatWallFunction ('Unknown patchField type') and the compressible spelling of div(((rho*nuEff)*dev2(T(grad(U))))) — both invisible to blockMesh/checkMesh. Repaired by Amendment 2 BEFORE first graded compute (arms exited at zero iterations, no time directory written, gates not yet closed -> a legal pre-compute amendment); the repair chose 'calculated' for alphat (low-Re-consistent, matching the running T1 convention) over the high-Re Jayatilleke wall function that would have run silently wrong. Does not recur: all three arms subsequently completed rc=0, strict completion rule met; named waste 0.034 core-min. The graded NOT A RESULT stands on gate (1) convergence, INDEPENDENT of the crashes. THEREFORE T4 = state (b): superseded-forward by T4b (registered, frozen, ran; T4b_RESULTS.md), whose own successor is the work item now being drafted. T4 owes NO distinct successor of its own. The only residual risk is the chain's forward tip stalling; the T4b-successor draft closes that."

### T8 — STATE RULING (heat-transfer supervisor)

"T8 = state (c), genuinely owed a successor, but the successor cannot be a like-for-like re-run and its shape is GATED. Two grounds (per T8_VERDICT_2026-08-26.md): Ground 1, the S3 axis-precondition r2=3*r1 is false on disk (measured 7/3) — a settled CONFIG/BUG fixed in the successor's frozen comparator by reading r1,r2 from disk and asserting only r2>r1>0. Ground 2, the steady formulation converges at no resolution (c stalled, m SIGFPE, f stalled) — an UNRESOLVED FORK between config/solver-selection (re-register unsteady/URANS) and model-form (closure unrealizable on these grids -> closure ladder, a cross-team call NOT taken here). The discriminator that separates them — one unsteady run at a single resolution with a registered stationarity criterion — has NOT been run. The existing T8_REREGISTRATION_DRAFT is a DRAFT (not frozen, no rung id) and under §2ay.3 clears NOTHING. T8's next step is to register and run that discriminator (ordinary re-registration route, no directive change), and the spine-placement referral must reach Sanaa with the supervisor recommendation entered (Item 2)."
