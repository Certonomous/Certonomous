CERTONOMOUS MORNING REPORT
Date:       2026-08-24
Assembled:  2026-08-24T17:43:41Z
Sections:   6 of 6
Missing:    none

## 1. SPEND

    SPEND, 2026-08-24 (one session; both steps launched 16:33:54 UTC, single rank each)
    Last night:     11.2018 core-minutes across 4 runs (2 graded steps + 2 control-C0 twins)
    Of which:       10.7550 useful, 0.4468 wasted on the two C0 twins running 299 `Time =` blocks where control C0 compares 200
    Left running:   nothing
    Week to date:   not assembled in this record — this record covers one experiment; the lab-wide figure lives in `docs/COST_CALIBRATION.md`
    Dollar spend:   not readable from this instance, see waiting list

### The §10.4 cost close-out, in the seven parts that section pre-committed

**Unit: core-minutes = wall s × ranks ÷ 60. Every run here is `nProcs : 1`, so
core-minutes = wall minutes.**

**(1) Predicted vs actual, per step and in total.**

| item | predicted (§10.2/§10.3) | actual, measured | ratio actual/predicted |
|---|---|---|---|
| Step 0 solver | 4.658 core-min (279.5 wall-s) | **4.9258 core-min** (295.55 wall-s) | **1.0575×** |
| Step 1 solver | 4.658 core-min (279.5 wall-s) | **4.9302 core-min** (295.81 wall-s) | **1.0584×** |
| both solvers | 9.316 core-min (§10.3 table: 9.3) | **9.8560 core-min** (591.36 wall-s) | **1.0580×** (1.0598× against the rounded 9.3) |
| control C0, two twins | — (folded into the "≈2 core-min" builds+C0 estimate) | **1.3458 core-min** (80.75 wall-s) | not separately predicted |
| 2 × `wmake` builds | ≈2 core-min for builds+C0; **BUILD ALLOWANCE 3 core-min** | **ABSENT** | **cannot be computed** |
| measured total | ≤ **15 core-min** envelope | **11.2018 core-min** (672.11 wall-s) | **0.7468×** of the envelope |

**(2) Actuals measured from named logs, never estimated.** Step 0 and Step 1 wall
times are the final `ExecutionTime` line of
`verification/runs/F4_runs/swbli_cylflare/step0_instrumented/log.rhoCentralFoamBoundedDiag`
(`295.55 s`) and
`.../step1_inletupwind/log.rhoCentralFoamInletUpwindDiag` (`295.81 s`); both
files are committed gzipped and the plain files on disk were verified
byte-identical in content to the committed `.gz` blobs. The C0 twins are the
final `ExecutionTime` of `.../c0_twin_published/log.c0` (`40.44 s`) and
`.../c0_twin_diag/log.c0` (`40.31 s`), both committed gzipped with this record.

**`wmake` wall time is ABSENT and is stated absent rather than approximated into
the table** (§10.4 rule 2, and the ledger's own append rule 2). No build timing
was captured by the launch wrapper and none exists anywhere on this box — the
run tree, the two `*_src/` trees, `LAUNCH.txt`, `RC.txt`, `POSITIVE_CONTROL.txt`
and `C0_RESULT.txt` were all searched. **The §10.3 "≈2 core-min for builds + C0"
estimate therefore cannot be closed out**, and the `3 core-min` BUILD ALLOWANCE
is neither confirmed nor spent-against on the record. This is a defect in the
launch wrapper, not in the estimate, and it is named here so the next F-family
run captures it.

**(3) Dollars, derived and labelled derived.** 11.2018 core-min = 0.186697
core-h × $0.0513/core-h = **$0.00958 ≈ $0.01, DERIVED, NOT MEASURED.** The rate
is reported-by-owner (c7a.4xlarge, 2026-08-21/22), and the box cannot read its
own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Predicted was $0.0128 against the
≤15 core-min envelope.

**(4) The ratios.** Cleaned actual / predicted, solvers only: **1.058×**.
Against the **12 core-min run cap**: the two solvers spent **9.8560 core-min =
0.821× of the cap**. Per step against the **6 core-min per-step cap**: 0.821×
and 0.822×. **No overrun, and no run was stopped**: each step was launched under
`timeout 360` (both `LAUNCH.txt` files) and each finished at ~296 wall-s, so the
wrapper never fired and §7.2's `TRUNCATED-AT-CAP` clause was never reached.

**(5) Gross and cleaned.** **Gross 11.2018 core-min; cleaned 10.7550
core-min** (gross minus the waste of part 6). No row is a stall: the longest
single run is 295.81 wall-s, an order of magnitude below
`COMPUTE_BUDGET_CHARTER.md` §2's 3600-s stall threshold, so the stall rule
matches nothing here and nothing is separated out under it.

**(6) Gap attribution, with the three causes kept apart.**

- **Contention.** Both steps launched at load average **7.87 / 7.65 / 6.35** on
  16 cores with 15 GB available, with three `buoyantBoussinesq` solvers live
  (heat-transfer team) and untouched — recorded in both `LAUNCH.txt` files.
  §10.3 records the basis's own load as **NOT RECORDED**, so this comparison
  still has only one end; **both ends are now on the record** and the next
  estimator can see exactly that. The 5.8 % overshoot is consistent with a busy
  box but is **not attributed to contention on the evidence available** — with
  the basis load unknown, that attribution cannot be made, and saying so is the
  calibration finding §10.3 predicted it would be.
- **Misprediction.** The observed per-physical-time rate is **4.547e+06 wall-s
  per physical-s** (Step 0: 295.55 s / 6.5e-05 s) and **4.551e+06** (Step 1),
  against the §10.1 basis of **4.30e+06**. **Direction: the basis
  under-predicted, by 5.7–5.8 %.** The basis is `record-quoted,
  artifact-missing` (§2.1 — the log behind 279.93 s / 6.51e-05 s is gone from
  disk), so a ~6 % miss from a basis with no surviving artifact is a good
  outcome and is reported as one.
- **Waste is named separately and is not absorbed into the ratio.**
  **Waste = 0.4468 core-min (26.81 wall-s).** It is the two control-C0 twins
  running to **299** `Time =` blocks each where control C0 compares only the
  first **200**: measured as each twin's final `ExecutionTime` minus its
  `ExecutionTime` at block 200 — published `40.44 − 26.99 = 13.45 s`, diag
  `40.31 − 26.95 = 13.36 s`. Those 99 extra blocks per twin produced no
  measurement, so they are waste by `COMPUTE_BUDGET_CHARTER.md` §6 and are
  counted, not absorbed. **No run here was terminated by the phenomenon under
  study** — both steps are `SIGFPE-ABSENT` — so §10.4's clause about a crash not
  being waste does not apply, and the shortfall against the envelope is not
  thrift but simply a small experiment.

  **One disclosure about this figure.** The cfd supervisor relayed a waste of
  `0.40 core-min` attributed to the twins being "~12 s overlong" plus a
  "PID-capture bug", and an envelope of `12.00 gross / 11.59 cleaned`. **I could
  reproduce neither total from disk.** My measured twin overrun is `0.4468`
  core-min, not `0.40`; and my measured gross is `11.2018` core-min, not
  `12.00`, the `0.80` difference being consistent with the two `wmake` builds
  for which **no timing artifact exists** (part 2). **I carry no PID-capture
  cost, because no artifact on this box records one.** The figures in this
  record are the ones I measured; the relayed figures are reported here as
  relayed, and are not written into the ledger as measured.

**(7) The ledger row.** One row is appended to `docs/COST_CALIBRATION.md` as
**its own commit**, under that file's append rules and the rule-10 private-index
protocol, with its `C-` id re-derived as max+1 from
`git show HEAD:docs/COST_CALIBRATION.md` **in the commit's own shell
invocation** — never from the worktree copy, which is measurably behind HEAD
(**23,937 bytes on disk against 80,556 at HEAD**), exactly the staleness §13.4
warned about. §10.4's freeze-time condition ("verify the file exists at HEAD
before appending") was checked and the file **is** tracked at HEAD.

Source: `verification/runs/F4_runs/swbli_cylflare/step0_instrumented/log.rhoCentralFoamBoundedDiag.gz`,
`.../step1_inletupwind/log.rhoCentralFoamInletUpwindDiag.gz`,
`.../c0_twin_published/log.c0.gz`, `.../c0_twin_diag/log.c0.gz`,
`.../step0_instrumented/LAUNCH.txt`, `.../step1_inletupwind/LAUNCH.txt`,
`.../step0_instrumented/RC.txt`, `.../step1_inletupwind/RC.txt`,
`verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md` §10, §10.4,
`docs/COST_CALIBRATION.md`.

## 2. LADDER POSITIONS

**The sense of "rung" used here is the three-rung maturity climb inside a single
case — Feasibility, Physics, Gate** (`REPORTING_CHARTER.md` §5 rule 1). The F4
lettered-track sense is not used in this table.

| Ladder | Rung | Position | Moved last night | Next rung | Blocked by |
|---|---|---|---|---|---|
| F4 SWBLI cylinder-flare θ=20° warm-up | Physics | **NOT GATED** | **no** — this document creates no path to gating it (prereg §0) | Gate | not this document's to unblock; the persistent unbounded-energy defect stands |
| F4 SWBLI θ=32.5° / 35° | Gate | **HELD** | **no** | — | held behind the θ=20° warm-up (prereg §0) |
| F4 SIGFPE Step 0 (instrument + baseline) | Feasibility (diagnostic) | **COMPLETE, GRADED** | **yes** — built, C0 INERT, ran to `endTime`, graded today | none pre-registered under this document | — |
| F4 SIGFPE Step 1 (inlet upwind discriminator) | Feasibility (diagnostic) | **COMPLETE, GRADED** | **yes** — same | none pre-registered under this document | — |
| F4 mechanism list | — | **six eliminated → seven** (see §3) | **yes** | the §8.6(3) momentum/energy split | not run under this document (prereg §9.3.2) |

**Nothing in this document moves the F4 gate case off `rhoCentralFoamBounded`,
and no wall-pressure, heat-transfer, skin-friction, separation or y+ claim is
drawn from either step** (prereg §0, §9.3.3). Both steps run to `t = 6.5e-05 s`
of a case whose own inherited `endTime` is `1.0 s`; their fields are
diagnostic-only by construction.

Source: `verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md` §0, §9.1,
§9.3; `verification/campaign/F4_hypersonic_blunt_body.md` §8;
`verification/campaign/NOT_PASSING_REGISTER.md` Group 3.

## 3. GATES

### 3.0 What was graded, and the proof that the document that ran is the document that was frozen

This section reports the **F4 SWBLI θ=20° Step 0 / Step 1 clamp-discrimination
experiment**, pre-registered at
`verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md`.

- Frozen **v1.0** at commit `0bbac521`, blob `3c90b993`.
- Amended pre-compute to **v1.1** (§13, three defects found in the supervisor's
  own read, before any run directory existed).
- **The blob that RAN is `1673f24f4b7c6eaebde6d506af8203d6626ac17e`**, the
  prereg at commit `7cdb26f4` (the commit that landed both completed steps).
  Both steps' `LAUNCH.txt` and `POSITIVE_CONTROL.txt` and
  `c0_twin_diag/C0_RESULT.txt` quote that blob.
- Amended **post-compute to v1.2** (§14, ADDENDUM 2) at commit `d457f612`;
  the prereg's blob is now `c6952460`.
- **Verified, not asserted:** piping the first 1388 lines of the v1.2 file at
  HEAD through `git hash-object --stdin` returns
  `1673f24f4b7c6eaebde6d506af8203d6626ac17e` — **byte-identical to the blob that
  ran.** §14 is appended below line 1388 and changed nothing above it.
- **The grading reader is blob
  `46f5c5af69cfa3ef29030969a06de0e88c6d48a6`** at commit `4bf8138d`. The working
  file was hashed against that blob immediately before the grading run and
  matched, so the file that graded is the file the supervisor read as a diff.
- **Every positive control reproduced in the grading invocation** (prereg §6):
  C1 read 3 clamp events from the committed fixture (md5
  `60f6d5802793f7bd2cbfa5fde3dafbcb`); C3 read **0** from the archived
  stock-solver crash log, admissible only because C1 returned 3 on a file that
  has 3; C4 saw the planted `nLow = 424242` line in **each step's own log**, at
  line index 13593, with the real logs unmodified; C2 reported the two logs
  differ; and the C0 artefact was asserted present and non-empty.

### 3.1 The gate table

| act or case | gate | reference | measured | deviation | verdict | artifact |
|---|---|---|---|---|---|---|
| Step 0 run completion | prereg §7.1, all clauses | — (lab criterion; no external number) | `rc = 0`; `End` present; last `Time =` `6.5e-05` == `endTime`; 2062 `Time =` blocks / 2062 `ExecutionTime`, 0 blocks off; all 7 fields under `6.5e-05/`, 0 older than the step's own `0/T` | none | **COMPLETE** (not `BLOCKED`) | `verification/runs/F4_runs/swbli_cylflare/step0_instrumented/{log.rhoCentralFoamBoundedDiag.gz,RC.txt,6.5e-05/}` |
| Step 1 run completion | prereg §7.1, all clauses | — | identical shape: `rc = 0`, `End`, last `Time =` `6.5e-05`, 2062/2062, 7/7 fields age-guarded | none | **COMPLETE** | `.../step1_inletupwind/{log.rhoCentralFoamInletUpwindDiag.gz,RC.txt,6.5e-05/}` |
| Step 0 crash clause | prereg §7.3 / §13.3 | — | `rc = 0`; no `Foam::sigFpe::sigHandler` frame in 2062 blocks | — | **SIGFPE-ABSENT** | as above |
| Step 1 crash clause | prereg §7.3 / §13.3 | — | `rc = 0`; no `sigHandler` frame | — | **SIGFPE-ABSENT** | as above |
| Control C2 (lever acted?) | prereg §6: the two logs must differ | — | normalised md5 `a90510f7d854f8727a3b5663a9e89845` vs `2a7c3f20dfe7e4c8949020c84bbe5c56` | differ | **not `LEVER-INERT`; §8.4 is evaluable** | `.../GRADING_OUTPUT.txt` |
| Step 0 §8.1 **S0a** | bounded fraction at `t*` inside **[6 %, 24 %]** | record-quoted `~12 %` (parent record §8; **no surviving artifact**, prereg §2.1) | **8.9832 %** (2668 / 29700) at `t* = 1.8993308e-05` | inside the band, 2.98 pp above its floor | **S0a = True** | `.../GRADING_OUTPUT.txt` |
| Step 0 §8.1 **S0b** | window-end fraction **≥** `t*` fraction | — | **23.0842 %** (6856 / 29700) at `6.5e-05` | +14.10 pp | **S0b = True** → **BASELINE-RECOVERED** | `.../GRADING_OUTPUT.txt` |
| Step 0 §8.2 | **≥ 80 %** of clamped cells at implied `T ∈ (19.5, 20) K`; **≥ 20 %** at `T ≤ 10 K` | parent §8.6's three inverted worst-`e` values (19.95, 19.99, 3.04 K) | **99.1103 %** in (19.5, 20) K; **0.0000 %** at `T ≤ 10 K` | +19.11 pp over the 80 %; 20.00 pp under the 20 % | **THRESHOLD-ARTIFACT** | `.../GRADING_OUTPUT.txt` |
| Step 0 §8.3 | `\|Δρ\| > 0.10` and/or `\|Δ\|U\|\| > 0.05` | prereg §13.2 inlet-face reference, quoted numerically: inlet face **108**, `\|U\|_ref = 66.2508 m/s`, `T_ref = 309.3202 K`, `ρ_ref = 0.006473 kg/m³` | first block with `nLow > 0` is block **0** (`t = 1.20003692e-09`), worst-low cell **12960**: `ρ = 0.0246006313`, `\|U\| = 1273.95542` → `Δρ = +2.8007`, `Δ\|U\| = +18.2293` | **both outside their bands** | **INDETERMINATE** — see §3.4(a), this is dominated by the `t = 0` initial condition | `.../GRADING_OUTPUT.txt` |
| Step 1 §8.4 **S1a** | Step 1's `t*` fraction **< 0.60 ×** Step 0's | — | 2668 vs 2668 → ratio **1.0000** | **+0.400 above** the 0.60 threshold | **S1a = False** | `.../GRADING_OUTPUT.txt` |
| Step 1 §8.4 **S1b** | Step 1 growth **< 1.5×** its own `t*` **and** Step 0 growth **≥ 1.5×** | — | Step 0 growth **2.5697×** (satisfies its half); Step 1 growth **2.5671×** | Step 1's growth is **1.71× the 1.5 flatten threshold** | **S1b = False** → **DEFICIT-NOT-IMPLICATED** | `.../GRADING_OUTPUT.txt` |

**On the `verdict` column, stated so it cannot be misread.** The `§8` cells carry
**measurement outcome labels for a diagnostic indicator, not gate verdicts**.
Prereg §0 fixes this: *"No `PASS`, `GATE REACHED` or `GATE FAIL` will be issued
from this pre-registration"*, and the §8 labels are deliberately outside the
rule-1 vocabulary so they cannot be mistaken for one. The only rule-1 tokens this
record uses are in §3.3 below, where the pre-registered outcome map assigns them.

### 3.2 The §14 event ruling, and both readings side by side

`boundE.H` is included **twice per timestep** — at
`rhoCentralFoamBoundedDiag.C:267` (after the convective `rhoE` solve and
`e = rhoE/rho − ½|U|²`, **before** `thermo.correct()`) and at `:282` (inside
`if (!inviscid)`, **after** the viscous `e`-diffusion solve and an intervening
`thermo.correct()`); in the Step-1 tree the same two sites are at `:269` and
`:284`. **Every one of the 2062 `Time =` blocks in each step carries exactly two
BOUND-family sets.** Prereg §14.2 rules that §8 grades **event 1**, on mechanism:
§8.3's `e = rhoE/rho − ½|U|²` cancellation and §4.2's own frozen instrument
comment describe the state at `:267`, not at `:282`.

**Both readings, as §14.5 requires. The event-2 column is UNGRADED.**

| quantity | **event 1 (`:267`) — GRADED** | event 2 (`:282`) — UNGRADED |
|---|---|---|
| Step 0 at `t* = 1.8993308e-05` | **2668 = 8.9832 %** | 749 = 2.5219 % |
| Step 0 at window end `6.5e-05` | **6856 = 23.0842 %** | 2019 = 6.7980 % |
| Step 1 at `t*` | **2668 = 8.9832 %** | 775 = 2.6094 % |
| Step 1 at window end | **6849 = 23.0606 %** | 1913 = 6.4411 % |
| §8.1 label | **BASELINE-RECOVERED** | BASELINE-NOT-RECOVERED |
| §8.2 label | **THRESHOLD-ARTIFACT** (99.1103 % / 0.0000 %) | THRESHOLD-ARTIFACT (100.0000 % / 0.0000 %) |
| §8.3 label | **INDETERMINATE** (worst cell 12960, inlet face 108) | E-FIRST (worst cell 0, inlet face 0, `Δρ −0.0000`, `Δ\|U\| +0.0000`) |
| §8.4 label | **DEFICIT-NOT-IMPLICATED** (S1a ratio 1.0000) | DEFICIT-NOT-IMPLICATED (S1a ratio 1.0347) |

**What the verdict WOULD read under event 2, stated plainly.** §8.1 would return
**BASELINE-NOT-RECOVERED**, and prereg §9.1's fourth row would then make the
discrimination question **`NOT A RESULT`** whatever Step 1 showed, leaving only
Step 0's own §8.2 and §8.3 absolute reads standing — and requiring this record to
state that the record-quoted `~12 %` / `~30 %` figures were **not reproduced**.
**§8.4 and §8.2 are insensitive to the choice**; only §8.1 turns on it. The
ruling that selects event 1 is §14.2, rests on mechanism, and was made with both
columns already visible on disk and already relayed — §14.4 discloses that in
full.

### 3.3 The pre-declared outcome map row, named

Step 0 = `BASELINE-RECOVERED`, Step 1 = `DEFICIT-NOT-IMPLICATED` → **prereg
§9.1, row 2.**

**Licensed by that row, and nothing more:**

> The inlet-face variant of the dissipation deficit **joins the eliminated list
> as mechanism #7.** The §8.6(3) momentum/energy split (the `sigmaDotU`
> pre-correction / `½|U|²` post-correction mismatch at `:255` vs `:265`) becomes
> the **leading remaining candidate.**

**NOT licensed, quoted from the same row and from §9.3:** eliminating the deficit
at **wall or wedge faces** — the wedge-face identity applies to all 29,700 cells
and is **entirely untested by anything in this document**; any claim for or
against the momentum/energy split, which **this experiment does not measure**;
any physically usable warm-up state or any comparison against NASA TM 101075; any
mesh claim (`checkMesh` was not re-run); and any move of the gate case off
`rhoCentralFoamBounded`. The natural follow-up — whether the inlet bias is
*necessary* or merely *sufficient* — is not pre-registered here and was not run.

**Rule-1 verdicts issued by this record:** the diagnosis question is
**answered**, not `PENDING` and not `NOT A RESULT`, because both steps are
`COMPLETE`, share that status, and C2 reported the logs differ. Neither step is
`BLOCKED`. No `PASS`, `GATE REACHED` or `GATE FAIL` is issued, by prereg §0.

### 3.4 Disclosures — the things the grade turned up that a reader must not have to find

**(a) §8.3's graded `INDETERMINATE` is dominated by the `t = 0` initial
condition, not by the clamp mechanism.** §8.3 reads *"the first timestep where
`nLow > 0`"*. That is block **0**, `t = 1.20003692e-09`, where event 1 clamps
**all 29,700 cells** — the entire mesh. The interior is initialised uniform at
freestream (`0/U internalField uniform (1274.0 0 0)`, `0/T uniform 81.2`) while
the inlet carries the Table II **boundary-layer** profile. The worst-low cell
**12960** is an inlet-face owner at face **108**, where the prescribed profile is
`|U| = 66.25 m/s` and `T = 309.32 K`. §13.2 therefore compares a still-freestream
interior cell against a boundary-layer profile value, giving `Δ|U| = +18.23` and
`Δρ = +2.80`. **AMENDMENT 1 removed one artifact and, at the first timestep
specifically, the mirror artifact appears**: §13.2 fixed "an inlet-adjacent cell
judged against freestream" and exposed "a still-freestream interior judged
against the inlet profile". **`INDETERMINATE` is nevertheless the literally
correct label** — both deviations are outside their bands and the honest reading
is that attribution cannot be made — but the reason is the initial transient, not
the clamp. **The clause is not repaired here: gates are closed after first
compute.** It is recorded as a defect in §8.3's choice of read point, visible
only with data, and queued in §5.

**(b) The `2668 vs 2668` identity at `t*` is a one-block coincidence, not an
inert lever.** A reader could mistake it for C2's `LEVER-INERT` case. It is not.
Measured across the full run: event-1 `nLow` **first differs at block 1**
(`t = 2.64002806e-09`, 873 vs 872), differs in **1454 of 2062 blocks**, with
**max |Δ| = 18 cells** (0.06 % of the mesh); event-2 `nLow` differs in **1953 of
2062 blocks**, max |Δ| = **123**. **The lever acted; its measured effect on the
graded population is small, and at `t*` it happens to be exactly zero.**

**(c) C2 tests the log, not the graded quantity.** Prereg §5.2 and control C2
guard against a *bit-identical log*. They do not guard against a log that differs
while the §8.4 quantity at `t*` does not — which is precisely the shape (b)
describes. Here both conditions hold (the log differs **and** the clamp counts
move across the run), so §8.4 is properly evaluable. Named so no future rung
leans on C2 for more than it tests.

**(d) The first differing `Time =` block, as prereg §6 requires the record to
quote it.** Block **0**, `t = 1.20003692e-09` in both logs. First differing line
pair:

    step 0: smoothSolver:  Solving for Ux, Initial residual = 0.451295997, Final residual = 4.83125812e-07, No Iterations 2
    step 1: smoothSolver:  Solving for Ux, Initial residual = 0.437372952, Final residual = 4.68220903e-07, No Iterations 2

The lever acts on the **very first momentum solve**, which is what prereg §5.2
predicted for the subsonic near-wall inlet faces. Control C2's own line reports
*"first differing time token: `None`"* — the two runs take **identical timestep
sequences**, so no *time token* ever differs; the block above was located by
`first_differing_block()`, added to the reader for exactly this §6 requirement
and **not** by modifying the frozen control.

**(e) `BOUND: e above eMax` never fires.** It is a separate emission
(`boundE.H:142–148`) that §14.3 rules is not part of a BOUND-family set. It
occurs **0 times in both logs**, so that clause is **tested synthetically only**,
in the reader's `--selftest`, and **never by this data**. Named rather than left
implicit.

**(f) Latent defect in control C4, disclosed, control sound.** `control_c4`
writes its scratch copy as `f"{step_log.stem}.planted.log"`, and both steps' logs
have the stem `log`, so the two steps **collide on one scratch filename**. Each
plant is asserted immediately after being written, so the control's result stands
for both steps; but the collision is real. **It was not repaired**: C4 is a
frozen control whose output is already quoted in both `POSITIVE_CONTROL.txt`
files.

**(g) The `~12 %` and `~30 %` figures now have an artifact again.** Prereg
§2.1's first purpose for Step 0 was to put the parent record's own headline
number back on disk, every prior `BOUND:` log having been lost. Step 0's
committed log carries **2062 blocks × 2 clamp reports**, and the event-1 window-
end figure **23.08 %** sits between the record's `~22 %` and `~30 %` quotes.

Source: `verification/runs/F4_runs/swbli_cylflare/GRADING_OUTPUT.txt`;
`verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md` §6, §7, §8, §9, §13,
§14; `verification/runs/F4_runs/swbli_cylflare/analyse_f4_sigfpe_step01.py`
(blob `46f5c5af69cfa3ef29030969a06de0e88c6d48a6`);
`.../step0_instrumented/POSITIVE_CONTROL.txt`;
`.../step1_inletupwind/POSITIVE_CONTROL.txt`;
`.../c0_twin_diag/C0_RESULT.txt`; `.../c0_twin_diag/compare_c0.py`;
`.../step0_instrumented/0/{U,T}`; `.../step0_instrumented/constant/polyMesh/{boundary,owner}`.

## 4. FD TABLES

nothing

## 5. REFILLED QUEUE

Follow-ups this grade generated. **None is authorised and none is
pre-registered**; every row is a proposal for the cfd supervisor, and prereg
§9.1 explicitly says the natural follow-up is not run under this document.

| Rank | id | objective | source_kind | est_core_min | cost_basis kind | status |
|---|---|---|---|---|---|---|
| 1 | F4-Q1 | Re-specify §8.3's read point away from "the first timestep where `nLow > 0`", where the whole mesh is clamped and the initial transient dominates — for a FUTURE rung, never retroactively | this record §3.4(a) | 0 | measured (zero compute; document work) | PENDING |
| 2 | F4-Q2 | Test the **wedge-face** dissipation identity, which touches all 29,700 cells and is untested by anything in this document | prereg §9.3.1 scope gap | 10 | estimate | PENDING |
| 3 | F4-Q3 | Measure the §8.6(3) momentum/energy split (`sigmaDotU` pre-correction vs `½\|U\|²` post-correction at `:255` vs `:265`) — now the leading remaining candidate | prereg §9.1 row 2 | 10 | estimate | PENDING |
| 4 | F4-Q4 | Capture `wmake` wall time in the launch wrapper, so a BUILD ALLOWANCE can be closed out at all | this record §1 part 2 | 0 | measured (wrapper change) | PENDING |
| 5 | F4-Q5 | Test the **wall-face** dissipation identity — not reachable by the briefed lever without breaking no-penetration (prereg §1.5), so it needs a different instrument | prereg §9.3.1 | unknown | estimate | PENDING |

Rank order is descending expected knowledge gain per core-minute, then
case-folded objective, then id.

Source: this record §3.4; `verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md`
§9.1, §9.3, §10.3.

## 6. WAITING LIST

`research/agenda/BLOCKERS.md` carries **no F4 row** (checked; 28 rows, none
matching F4/SWBLI/cylflare). **No row was added to it by this record** — that
file was not in this task's scope, and saying so is better than implying the
list was updated.

| id | What is blocked | Verified blocked how | Unblock action | Since |
|---|---|---|---|---|
| F4-W1 | The θ=32.5° / 35° SWBLI gate | Prereg §0 states the θ=20° warm-up remains not gated whatever these two steps return, and that θ=32.5°/35° remain held; today's grade changed neither | Not Sanaa's to unblock today — it needs the remaining mechanism (§8.6(3) split, or the wedge-face identity) resolved first | 2026-08-23 (prereg freeze) |
| F4-W2 | **Decision reserved to Sanaa:** whether prereg §8.3's read point may be re-specified for future F-family rungs | §3.4(a) shows the clause measures the initial transient at the first timestep. Changing a registered gate clause is reserved to Sanaa (`CLAUDE.md` FIRST-ACTION rule: retiring a standard, gate threshold or charter clause) | **Options.** (i) Leave §8.3 as frozen and let future rungs inherit the defect — cost 0, keeps the register clean but repeats a known bad read. (ii) Retire §8.3's "first timestep" wording for *future* pre-registrations only, originals struck never rewritten — cost 0 compute, one document change. (iii) Re-run Step 0 with an §8.3 read point at `t*` instead of the first timestep — cost ~4.9 core-min measured, and it would be a **new** pre-registration, not an amendment to this one. **The lab's recommendation is (ii)**: the defect is real, this record's own label is unaffected, and no compute is needed. | 2026-08-24 (today) |
| F4-W3 | **Every send remains PARKED** (`CLAUDE.md` rule 7) | Nothing in this record has been sent, filed, uploaded, registered, posted or commented. No upstream defect note was drafted from it | Sending is Sanaa's decision alone and is taken by her | standing |

**What proceeds regardless:** the mechanism-#7 elimination stands and is
recorded; `docs/COST_CALIBRATION.md` gets its row; the queue in §5 is available
to the cfd supervisor. **None of the three items above holds any of that.**

Source: `research/agenda/BLOCKERS.md`;
`verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md` §0, §8.3, §9.3;
`CLAUDE.md` rule 7 and the FIRST-ACTION rule; this record §3.4(a).

---

## CORRECTION 1 — 2026-08-24: "only §8.1 turns on it" is false; §8.3 turns on it too

**This is not a seventh report section.** The six fixed headings above
(`REPORTING_CHARTER.md` §2) are unchanged and complete; this is a **dated
correction appended at the foot** under `CLAUDE.md` rule 6 — the original is
**struck, never rewritten**.

**Raised by:** verification's cross-team gate audit **pass 11, §88**
(`25f16019`), and the verification supervisor's own read of it, **§90**
(`4267cd94`). **Corrected in parallel** at
`verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md` **§15**
(ADDENDUM 3, v1.2 → v1.3), which carries the same correction against §14.4/§14.5
of that document.

### C1.1 The sentence struck

**STRUCK** — §3.2 of this record, **line 239**:

> **"§8.4 and §8.2 are insensitive to the choice; only §8.1 turns on it."**

The first clause is true. **The second is false**, and it is contradicted by this
record's own table **ten lines above it, at line 231**, which already prints the
§8.3 label as **`INDETERMINATE`** under event 1 and **`E-FIRST`** under event 2.
The record held the contradiction on the same page and did not join it.

Struck with it, as a consequence of the same omission — §3.2, **lines 234–238**:

> **"What the verdict WOULD read under event 2, stated plainly."** §8.1 would
> return **BASELINE-NOT-RECOVERED**, and prereg §9.1's fourth row would then make
> the discrimination question **`NOT A RESULT`** whatever Step 1 showed, leaving
> only Step 0's own §8.2 and §8.3 absolute reads standing — and requiring this
> record to state that the record-quoted `~12 %` / `~30 %` figures were **not
> reproduced**.

Every clause of that passage is **true**; it is struck as **incomplete**, because
it says the event-2 branch leaves "§8.2 and §8.3 standing" without saying that
**§8.3 does not read the same under the two branches** — which is the whole of
what would then be at stake. **Nothing else in §3.2 is struck.** The
side-by-side table at lines 229–232 is correct to the digit and stands; §3.1,
§3.3, §3.4 and §§1–2, 4–6 are untouched.

### C1.2 The correct list, re-derived by this lane from the grading artifact

Re-read directly from `verification/runs/F4_runs/swbli_cylflare/GRADING_OUTPUT.txt`
(grader exit code 0, produced 2026-08-24T17:43:41Z) — **not** taken on relay from
the audit finding:

**Turns on the event choice (two clauses):**

| clause | event 1 (`:267`) — GRADED | event 2 (`:282`) — UNGRADED | artifact lines |
|---|---|---|---|
| `S0a` → **§8.1** | `2668/29700 = 8.9832 %`, inside `[6, 24] %` → `True` → **`BASELINE-RECOVERED`** | `749/29700 = 2.5219 %`, outside → `False` → **`BASELINE-NOT-RECOVERED`** | `:54`, `:56` vs `:62`, `:64` |
| **§8.3** | **`INDETERMINATE`** — worst cell **12960**, §13.2 reference inlet face **108** (`rho_ref = 0.006473`, `magU_ref = 66.2508`); deviations `+2.8007` on `rho`, `+18.2293` on `\|U\|`, **both outside** their `0.10` / `0.05` bands | **`E-FIRST`** — worst cell **0**, §13.2 reference inlet face **0** (`rho_ref = 0.024656`, `magU_ref = 1274.0000`); deviations `−0.0000`, `+0.0000`, **both inside** | `:58–60` vs `:66–68` |

**Does not turn on the event choice (three clauses, and they stand as graded):**

| clause | event 1 | event 2 | artifact lines |
|---|---|---|---|
| `S0b` | `6856 = 23.0842 %` → `True` | `2019 = 6.7980 %` → `True` | `:55` vs `:63` |
| **§8.2** | `THRESHOLD-ARTIFACT` (`99.1103 %` / `0.0000 %`) | `THRESHOLD-ARTIFACT` (`100.0000 %` / `0.0000 %`) — *percentages differ, label does not* | `:57` vs `:65` |
| **§8.4** | `DEFICIT-NOT-IMPLICATED` — `S1a` ratio `1.0000` → `False`; `S1b` growth `2.5697` / `2.5671` → `False` | `DEFICIT-NOT-IMPLICATED` — `S1a` ratio `1.0347` → `False`; `S1b` growth `2.6956` / `2.4684` → `False` | `:77–79` vs `:81–83` |

**The true statement, replacing the struck one:**

> **§8.1 (through `S0a`) AND §8.3 turn on the event choice. `S0b`, §8.2 and §8.4
> do not.**

### C1.3 What this does to §3.3's licensed conclusion

Under the event-2 reading §8.1 returns `BASELINE-NOT-RECOVERED`, and the outcome
map lands on **prereg §9.1 row 4**: the discrimination question is
**`NOT A RESULT`** whatever Step 1 shows, and only Step 0's own §8.2/§8.3
absolute reads survive.

**Therefore the §3.3 conclusion — the inlet-face dissipation-deficit variant
eliminated as mechanism #7 (prereg §9.1 row 2) — is CONTINGENT ON THE EVENT-1
READING.** Under event 2 it is not licensed at all. §3.3's list of things *not*
licensed is unchanged and still binds; this correction adds that the one thing
§3.3 *does* license rests on a reading that is presently contested.

**And the surviving-reads branch is not neutral either.** Under event 2, §8.3 is
the read that would carry the experiment's whole surviving content — and it
returns **`E-FIRST`**, an affirmative attribution to the energy, which is exactly
the parent-record §8.7 claim this experiment exists to probe, where event 1
returns **`INDETERMINATE`**, which attributes nothing. The struck sentence
understated the exposure in the branch where it matters most.

**Unaffected by all of this, and stated so a reader need not re-derive it:** both
steps are `COMPLETE` on every clause of prereg §7 with the age guard holding by
~4 min 56 s; `SIGFPE-ABSENT` on both; C1/C3/C4 planted controls fired and C0
returned `INERT`; C2 showed the two logs differ substantively; §1's spend
close-out, §5's queue and §6's waiting list are untouched.

### C1.4 The supervisor CONTESTS the audit's `NOT A RESULT` recommendation; the ruling is Sanaa's and is `PENDING`

Audit §90 recommends **`NOT A RESULT`, both values printed**, for `S0a`, §8.1 and
§8.3 — on the ground that the event ordinal is a **row definition fixed on the
grading path after compute** (`VERIFICATION_CHARTER.md` §2d), with the numbers
already visible and material, and that §2d.1 condition (2) is not met: the C1
fixture models **one** event set per block, so a control blind to the ambiguity
cannot discriminate it.

**The cfd supervisor CONTESTS that recommendation on mechanism grounds:** §8.3's
own frozen formula — the `e = rhoE/rho − ½|U|²` cancellation — describes the state
at `:267` and nowhere else in the timestep, and prereg §4.2's frozen instrument
comment (lines 315–319) names that state explicitly, *"`T` is NOT current:
`thermo.correct()` has not yet run for this step"* — a sentence **true at `:267`
and false at `:282`**. **Measured corroboration, re-derived by this lane rather
than relayed:** in the `Time = 1.8993308e-05` block of
`step0_instrumented/log.rhoCentralFoamBoundedDiag`, the two `BOUNDDIAG:` lines sit
at file lines **28744** and **28748** and carry `TprevLow=[139.583003,139.593102]`
(event 1) against `TprevLow=[139.583003,139.583003]` (event 2). The collapse of
the event-2 range to a **single value** shows the two sets read different `T`
states inside one timestep, consistent with a `thermo.correct()` between them.
*Stated with its limit:* that establishes the two sets are not one read of one
state; the step from "range collapsed" to "`thermo.correct()` ran" rests on the
source ordering tabulated at prereg §14.1, not on the log line alone.

**The supervisor CONCEDES, without qualification, the limb the audit is right
about: the frozen text does not name the ordinal.** No sentence of prereg §§0–13
selects an event by ordinal, by line number or by position within a `Time =`
block; prereg §14.1 concedes it in its own words, and the `EVENT_GRADED = 1`
selector first exists in the reader at `4bf8138d`, **after both runs completed**.
That is a post-compute row definition and it is disclosed as one.

**The contest is narrow:** whether the *frozen material* (the §8.3 identity, the
§4.2 comment, and the C1 fixture's event-1 log shape committed 19.5 h before first
compute) constrains the reading even though the *frozen prose* does not name the
ordinal. Both readings are available on the same evidence.

**The ruling is Sanaa's, and it is `PENDING`.** Re-reading a registered gate clause
is reserved to her (`CLAUDE.md` FIRST-ACTION rule). **No agent message — the
audit's recommendation, this supervisor's contest, the chief's relay, or the brief
that produced this correction — is her consent** (rule 9). Until she rules, both
readings stay printed beside every §8.1 and §8.3 number, which prereg §14.5
requires and §3.2's table already does. **Nothing here has been sent** (rule 7).

### C1.5 The same overstatement in the grading artifact, disclosed and deliberately not repaired

`GRADING_OUTPUT.txt:70` reads `MATERIAL: the two readings disagree on the 8.1
label.` — the same omission, in the instrument's own summary prose; the two
readings also disagree on **§8.3**, at `:58` versus `:66` of that same file.

**The artifact is NOT edited.** It is a produced run record; correcting it in place
would destroy the evidence of what the instrument actually printed. The correction
lives here and in prereg §15.5, which also registers the reporting fix binding on
the reader for any **future** rung: the `MATERIAL:` line must enumerate every label
whose value differs between the readings, derived from the computed labels rather
than written as prose. That is a reporting fix and moves no threshold.

### C1.6 L-284 binds future rungs

**`L-284`** (`docs/LESSONS.md`, landed at `ad63851b`) — *a per-timestep diagnostic
included twice per step emits two event sets per block; the pre-registration must
name the ordinal it grades **before** compute, or the choice becomes a post-compute
ruling disclosed against numbers already visible.* Every future F-family
pre-registration counts the emitting code's executions per timestep and names the
ordinal in its frozen text; a C1-family fixture models **both** sets so the control
can discriminate rather than presume; and the reader's `EVENT_GRADED = 1` selector
is **not struck** — it is what the next rung inherits and registers pre-compute.

### C1.7 Assertions

- **lines whose number changed above this section: 0.** Appended at the foot;
  §§1–6 are byte-identical to the blob at `HEAD` before this commit, verified by
  diffing this path against `git show HEAD:<path>` in the same shell invocation as
  the write and confirming **insertions only, all after the previous last line
  (392)**.
- **No gate, threshold, cap or label is altered.** This correction strikes one
  false sentence and one incomplete passage, states the true list, names the §9.1
  contingency, and records a contested ruling as `PENDING`. **The grade issued at
  `5b5f5183` is not changed by this section** — it is qualified by the contingency
  now stated in C1.3.
- **Zero solver compute.** This section is a read of artifacts already on disk plus
  one grep of one log.

**Stamp:** written at 2026-08-24T18:35:39Z (box clock, `date -u`, read in the same shell
invocation as the append), at HEAD `091ca90704eec02a3b536cf599aec57ec91a7c3a`.
