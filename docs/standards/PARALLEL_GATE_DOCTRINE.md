# PARALLEL-GATE DOCTRINE

**Status:** standing record. Ratified by Sanaa, 2026-08-25.
**Territory:** cfd (`docs/standards/`). The audit scoped in §6 is **lab-wide** and is
**not cfd's to execute outside its own territory** — see §6.4.
**Built from:** the F6a/F12 findings, `verification/campaign/F6a_GREENBLATT_PREREGISTRATION.md`
Addendum 5 and the two F6a run trees named in §4.

---

## 1. Provenance

This doctrine originates in **Sanaa's own session turn of 2026-08-25**, relayed to the cfd
team by the chief. **Her words are the authority.** They are reproduced in §2 exactly as
she wrote them.

**Everything from §3 onward is cfd's reading of her words, and is marked as such.** The
operative clauses in §3 are this team's restatement of her text as checkable rules; they
are not her text, they do not extend it, and where a reader finds daylight between §2 and
§3, **§2 governs.**

**On the form of §2.** Her text is recorded in a fenced block rather than a `>` blockquote.
A markdown blockquote prefixes `> ` to every line, which alters every line's bytes — the
exact thing a verbatim record exists to prevent. The fenced block preserves her spelling,
punctuation, capitalisation, line breaks and the run-on between *"not the game"* and
*"F5b: APPROVED"* byte-for-byte and unnormalised. **This departure from the instructed
form is disclosed rather than taken silently.**

---

## 2. Sanaa's words, verbatim — 2026-08-25

```
II. CFD team instructions:PARALLEL-GATE DOCTRINE (from cfd's F6a/F12 findings):

Gate runs use deterministic decomposition. Identical input must produce identical partitions — pin the method and seed for any run feeding a verdict; non-deterministic partitioning is for throughput work only.
Per-channel residual tolerances must be justified or harmonized. A channel 5,000× tighter than its siblings, met by 0.6% on one partition and missed 4.6× on another, is measuring the partition, not convergence. Every gate's residual criteria get a one-line justification or get rationalized; the audit sweeps all standing cases.
Partition-robustness joins gate design: the graded quantities moved 2.2e-5 across partitions — the answers are stable; the gates aren't. Convergence verdicts should rest on graded-quantity stationarity plus reproducibility across a partition pair, not on the twitchiest residual channel alone.
Finding 3 is quietly excellent news: the physics your lab computes is reproducible to 2e-5 across different parallel layouts — the noise is in the referee, not the game F5b: APPROVED. The 72-core-min capped run fires as specced. The lane's refusal to route around my denial was correct; this is the answer.
F12 — new admissible mesh ladder, frozen gate untouched. The pre-registration's PASS rule and criteria stay exactly as frozen 2026-07-30. Build a fresh three-level mesh ladder that passes the admission gate at every level (birth certificates; deterministic decomposition per the new parallel-gate doctrine); record in the attempt ledger as the next attempt with reason "original ladder inadmissible at all levels, worsening under refinement — mesh instrument replaced, gate unchanged." Then run RAE 2822 / AGARD Case 9 against the unchanged criteria. This is the primary first-HOLDS path.
ONERA M6 — second HOLDS path, fresh pre-registration. Freeze a new prereg today (before any new solve): case, mesh ladder with admission checks, graded quantities vs AGARD 2308, PASS bands justified from the reference's stated accuracy, deterministic decomposition, iteration/convergence criteria per the harmonized-residual rule. The old favorable comparison is history and cannot score P; this one can. File the freeze commit hash to the docket, then run.
F4: re-present the event-choice as one paragraph — the two (or more) event definitions, what the headline finding says under each, and the team's recommended default with reasoning. Zero compute until my ruling.
Sequencing: 2 before 3 if compute contends; both ahead of new case selection. Every run under the parallel-gate doctrine just ratified.
```

---

## 3. The four operative clauses — cfd's reading, stated as checkable rules

**These are cfd's restatement, not Sanaa's words.** Each is written so that a reviewer can
answer *satisfied / not satisfied* without interpretation.

### C1 — Deterministic decomposition for any run feeding a verdict

**Rule.** Any run whose output reaches a gate, a graded row or a certificate must use a
decomposition that is **reproducible between invocations**: the method is pinned in
`system/decomposeParDict`, and where the method exposes a seed or ordering parameter, that
parameter is pinned too. **Identical input must produce identical partitions.**

**Check.** Decompose twice from a byte-identical case and compare the per-rank cell counts,
or compare `processor*/constant/polyMesh/cellProcAddressing`. Equal → satisfied.

**Scope limit.** Non-deterministic partitioning is **not banned** — it is confined to
**throughput work**: scaling probes, warm-ups, exploratory sweeps, anything whose number
never reaches a verdict.

**Note on what is not yet established.** This clause does **not** assert that `scotch` is
non-deterministic as a general property. See §5.

### C2 — Per-channel residual tolerances are justified or harmonized

**Rule.** Every `residualControl` block that gates a verdict carries **either** a one-line
justification for each channel whose tolerance differs from its siblings, **or** it is
harmonized so that no such difference exists.

**Check.** For each gating case: read the block, compute `max(tolerance)/min(tolerance)`,
and confirm that a justification exists in the case's own frozen record for any channel
that sets the extremes. Missing justification and no harmonization → not satisfied.

**Why a bare number is not enough.** A tolerance is a claim that a channel has stopped
changing enough to trust. A tolerance that differs from its siblings by orders of magnitude
is an additional claim — that this channel needs more — and that claim has to be made
somewhere a reader can find it.

### C3 — Partition-robustness is part of gate design

**Rule.** A convergence verdict rests on **two** legs, not one:

1. **stationarity of the graded quantity** — the quantity the row reports has stopped
   moving, on its own frozen plateau criteria; **and**
2. **reproducibility across a partition pair** — the graded quantity agrees between two
   runs of the same case on **different** partitions, within a band stated in the
   pre-registration.

A verdict resting on **the tightest residual channel alone** is not a convergence verdict
under this doctrine.

**Check.** The pre-registration names both legs and the reproducibility band, before compute.

### C4 — The audit sweeps all standing cases

**Rule.** C2 is not applied only to new work. The existing stock of cases is swept, and
every gating `residualControl` block is brought into compliance with C2 or flagged.

**Scoped and costed in §6. NOT EXECUTED by this record.**

---

## 4. The measured evidence this doctrine was built from

Every figure below was **re-verified against the artifact named beside it** while writing
this record. Where a relayed figure did not reproduce exactly, the artifact's value is
printed and the correction is stated. **Three corrections were needed; they are marked
`CORRECTION`.**

**Artifacts:**
- `/home/ubuntu/Certonomous/verification/campaign/F6a_GREENBLATT_PREREGISTRATION.md` — Addendum 5, §A5.3 and §A5.4 (document lines 1671 onward)
- `/home/ubuntu/Certonomous/verification/runs/F6a_GREENBLATT_runs/attempt2_Re936k/result.json`
- `/home/ubuntu/Certonomous/verification/runs/F6a_GREENBLATT_runs/attempt3_Re936k/result.json`
- `/home/ubuntu/Certonomous/verification/runs/F6a_GREENBLATT_runs/attempt3_Re936k/system/fvSolution`
- `/home/ubuntu/Certonomous/verification/runs/F6a_GREENBLATT_runs/attempt{2,3}_Re936k/system/decomposeParDict`

### 4.1 The same case partitioned differently on two invocations

| run | partition, first three ranks | source |
|---|---|---|
| attempt 2 | **12777 / 12906 / 12965** | Addendum 5 §A5.3 table; `attempt3.../result.json` `THE_NEW_FINDING.evidence[0]` |
| attempt 3 | **12974 / 12870 / 12865** | same |

The mesh points, the `0/` directory and `system/controlDict` were **byte-identical**
between the two runs (`diff -rq` clean) — Addendum 5 §A5.3.

Both runs used `method scotch;` with `numberOfSubdomains 4;` — read directly from
`attempt2_Re936k/system/decomposeParDict` and `attempt3_Re936k/system/decomposeParDict`.

### 4.2 One residual channel 5,000× tighter than its siblings

Read from `attempt3_Re936k/system/fvSolution`:

```
residualControl
{
    "(U|p|k)"       5e-7;
    omega           1e-10;
}
```

`5e-7 / 1e-10 = 5000` exactly. **The 5,000× figure reproduces from the dictionary itself**,
not only from the prose about it.

### 4.3 The channel that measured the partition

| | attempt 2 | attempt 3 |
|---|---|---|
| omega initial residual at the deciding iteration | **9.94318e-11** | **4.63816e-10** |
| against control `1e-10` | **met, by 0.568 %** | **missed, by 4.638×** |
| iteration | converged at **1813** | **no convergence — hit the 2000 cap** |

> **`CORRECTION` — 0.6 % is a rounding; the artifact-backed figure is 0.568 %.**
> `(1e-10 − 9.94318e-11)/1e-10 = 0.5682 %`. Addendum 5's own §A5.3 table prints
> **0.568 %**; the prose field in `attempt3.../result.json` rounds it to *"A MARGIN OF
> 0.6 %"*. **0.568 % is used here.** Sanaa's text says 0.6%, which is that rounding and
> is not wrong — this note records the precise value, it does not contradict her.

> **`CORRECTION` — 4.6× is a rounding; the precise figure is 4.638×.**
> `4.63816e-10 / 1e-10 = 4.6382`. Addendum 5 prints **4.638×**.

At attempt 3's cap **every other channel was comfortably inside its 5e-7 control** —
Ux 2.88977e-08, Uz 5.92457e-08, p 5.77611e-08, k 8.31752e-08
(`attempt3.../result.json`, `WHY_IT_IS_NOT_A_RESULT.binding_channel`). **omega alone was
binding.**

### 4.4 Two of three runs tripped the criterion

| run | converged at |
|---|---|
| C-45 | **1772** |
| attempt 2 | **1813** |
| attempt 3 | **not by 2000** |

Source: `attempt3.../result.json` `THE_NEW_FINDING.evidence[5]`; Addendum 5 §A5.3 table.
**Two of three.** The C-45 partition was not recorded.

### 4.5 The graded quantities were stable across the partitions

| quantity | attempt 2 | attempt 3 | spread |
|---|---|---|---|
| separation `x_s/c` | 0.6544112034434796 | 0.6544109177598695 | **2.857e-07** |
| reattachment `x_r/c` | 1.2534333536987177 | 1.2534550444895884 | **2.169e-05** |

Values read from `result.json` — `gates.P1_separation.value` / `gates.P2_reattachment.value`
on attempt 2, and `gates_REPORTED_NOT_CERTIFIED.*` on attempt 3.

> **`CORRECTION` — "the graded quantities moved 2.2e-5" is the WORST channel, not both.**
> **2.2e-5 is the reattachment spread alone** (2.169e-05). **Separation moved 2.857e-07 —
> roughly two orders of magnitude less.** 2.2e-5 is therefore correct **as the upper bound
> across the two graded quantities**, and this record states it that way. Addendum 5 §A5.4
> already separates them (3e-7 and 2.17e-5); the single figure 2.2e-5 collapses that.

Addendum 5 §A5.4 also records the scale: **2.17e-5 in x/c is 0.0017 % of the value and
3.95e-4 of Gate P2's half-width.**

### 4.6 What the evidence supports

**The answer was reproducible across partitions to 2.2e-5 in x/c. Whether the convergence
criterion tripped inside the iteration cap was not reproducible at all.** That asymmetry —
stable physics, unstable referee — is the whole of this doctrine's empirical ground.

---

## 5. HONEST LIMITS — what this record does NOT establish

**A record that overstates its ground invites a correct rebuttal that then looks like it
overturns the conclusion.** The following are stated so that no such rebuttal is available.

1. **The non-determinism is OBSERVED, on `scotch`, over three runs of ONE case.**
   Three observations (C-45, attempt 2, attempt 3) of the F6a Greenblatt hump at
   Re 936k, 4 subdomains. That is the entire observational base.

2. **It is NOT established as a `scotch` bug.** No upstream defect is claimed, none is
   filed, and none should be inferred from this record. The observation is consistent with
   a `scotch` non-determinism; it is equally consistent with an input to the partitioner
   varying between invocations for a reason not yet identified. **The two have not been
   separated.**

3. **It is NOT characterised across other decomposition methods.** `simple`, `hierarchical`,
   `metis`, `kahip` and `manual` were **not tested**. Nothing here says they are
   deterministic and nothing here says they are not. C1 requires the method be *shown*
   reproducible, precisely because this record cannot say which methods already are.

4. **It is NOT characterised across other cases, cell counts or rank counts.** One case,
   one mesh, one `numberOfSubdomains 4`.

5. **The MECHANISM IS CONSISTENT WITH THE OBSERVATION AND IS NOT DEMONSTRATED.** The chain
   *partition → parallel summation order → round-off → residual trajectory* is a plausible
   and physically ordinary explanation. **No step of it was measured.** No summation order
   was captured, no round-off difference was isolated, and no controlled experiment
   attributed the residual divergence to that chain rather than to anything else. It is
   stated in this record as a **hypothesis**, and Addendum 5 states it the same way.

### 5.1 What WOULD demonstrate each claim

| claim | what would demonstrate it |
|---|---|
| `scotch` is non-deterministic between invocations | Run `decomposePar` **N ≥ 10** times on one byte-identical case, capturing `cellProcAddressing` each time, and report the number of distinct partitions. **One distinct partition over 10 invocations refutes it; more than one establishes it for that case.** Repeat on ≥ 3 cases of different size to establish it as a property of the method rather than of one mesh. |
| the effect is method-specific | The same N-invocation protocol on `simple`, `hierarchical` and `metis`. A method returning one distinct partition over N is a deterministic alternative and can be named in C1. |
| the mechanism is summation order | Hold the partition **fixed** (`method manual` from a saved `cellProcAddressing`) and re-run twice: identical residual trajectories are expected. Then vary **only** the partition and confirm the trajectory changes. That isolates partition from every other source. A stronger form pins reduction order (deterministic reduction) and shows the divergence disappears. |
| the criterion, not the physics, is what varies | Already measured for this one case (§4.5 vs §4.3) and it is the strongest result here. Generalising it needs the same partition-pair comparison on other cases — which is what C3 makes routine. |

**Until those are run, C1 stands on the sound conservative ground that a verdict should not
depend on an input the lab has not shown to be reproducible — NOT on a demonstrated defect
in any named tool.**

---

## 6. THE RESIDUAL-CRITERIA AUDIT — scope and cost

Clause C4 (Sanaa: *"the audit sweeps all standing cases"*) is **lab-wide, not cfd-only**.
This section scopes and costs it. **It has NOT been executed.**

### 6.1 How many standing cases carry per-channel residual criteria — counted from disk

Counted 2026-08-25 with `/usr/bin/find` + `/usr/bin/grep` (**never bare `grep`**, which in
this environment is a `ugrep --ignore-files` wrapper and is blind to gitignored archives).
`processor*/` copies excluded. Control: 465 files matched `residualControl` and 219 did not,
summing to the 684 found — **the reader was shown able to return both a hit and a miss.**

**In the repository — `cases/`, `models/`, `verification/runs/`:**

| | fvSolution files | of which carry `residualControl` |
|---|---|---|
| total | **684** | **465** |

**Split by kind:**

| kind | with `residualControl` |
|---|---|
| case **definitions** (`cases/`, `models/`) | **193** |
| **run trees** (`verification/runs/`) | **272** |

### 6.2 By team territory

| territory | case definitions | run trees | repo total |
|---|---|---|---|
| **dafoam** (`cases/dafoam/`) | **149** | 0 | **149** |
| **cfd** (`cases/` outside closure/dafoam/ansys; `verification/runs/` outside T-family, F14, THERMAL_K0, ansys) | **40** | **75** | **115** |
| **heat-transfer** (`verification/runs/{T-family,F14-cooling-ladder,THERMAL_K0_runs}/`) | 0 | **182** | **182** |
| **ansys-verification** (`cases/ansys_verification/`, `verification/runs/ansys_verification/`) | **4** | **15** | **19** |
| **closure** (`cases/RANS_LES_closure_models/`) | **0** | 0 | **0** |
| | | | **465** |

**closure holds ZERO OpenFOAM `fvSolution` files inside the repository.** Its solver cases
live outside git, and the sweep must reach them or it is not lab-wide:

| out-of-git store | fvSolution (non-`processor*`) | with `residualControl` |
|---|---|---|
| `/home/ubuntu/closure-data` | 226 | **171** |
| `/home/ubuntu/closure-challenge-benchmark` | 40 | **11** |
| `/home/ubuntu/certonomous-runs` (the general run store — chiefly cfd and dafoam work) | 944 | **652** |

**Total blocks in scope if the sweep is taken at its widest: 465 + 171 + 11 + 652 = 1,299.**

**This total is an upper bound on FILES, not on GATING CASES.** Most run-tree blocks are
copies of a definition's block carried into an output directory, and most archived runs
gate nothing. **The number that matters to C2 is the count of blocks that gate a verdict**,
and that cannot be read off `find` — it requires matching each block to a pre-registration.
**That matching is the substance of the sweep and is why it is scoped here rather than
guessed at.**

### 6.3 The sweep must CLASSIFY before it computes any ratio

**This subsection exists because of a measurement by the F5b lane, relayed 2026-08-25, and
it changes the instrument's design.** Credited to that lane.

**The finding.** On the F5b case the tightest/loosest tolerance ratio is **10,000×**, and
**a sweep that flagged on that raw ratio would be WRONG.** Three reasons, each of which the
instrument has to survive:

1. **The direction is inverted from F6a.** F6a's pathology is a channel *tighter* than its
   siblings — that channel is met last, becomes the sole binding criterion, and is what
   measures the partition. On F5b the outlier is the *loosest* channel, which is met
   **first** and therefore **never binds**. A loose outlier cannot produce the F6a pathology.
2. **That run is SERIAL.** With no partition, the F6a mechanism — partition → summation
   order → round-off → residual trajectory — **cannot operate at all.**
3. **`pcorr` is not a convergence channel of the physics.** It is the flux correction for
   mesh motion, a different equation. **Among the primary solved channels the ratio is a
   benign 10×.**

**A check that cries wolf on a healthy case teaches the next agent to ignore it** — L-315's
failure mode in a second costume. The classification below is how the instrument avoids that
**mechanically, without a human reading each case.**

#### 6.3.1 Two corrections to the relayed F5b example — both verified against artifacts

> **`CORRECTION` — F5b's `fvSolution` carries NO `residualControl` BLOCK AT ALL.**
> The 1e-09 / 1e-08 figures are **linear-solver `tolerance` entries inside `solvers{}`** — a
> **different dictionary key measuring a different quantity**: the drop tolerance of one
> linear solve *within* an iteration, not a convergence criterion for the outer loop.
> Verified on `/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/f5b_re1000_3d_pilot_stage/system/fvSolution`
> — `p` 1e-08, `pFinal` 1e-08, `"(U|k|omega)"` 1e-09, `"(U|k|omega)Final"` 1e-09 — and a
> `residualControl` extraction returns **empty on all six staged `f5a-cylinder-ladder` cases.**
> **This strengthens the F5b lane's point rather than weakening it:** the instrument must
> classify by **dictionary key** before it ever classifies by channel.

> **`CORRECTION` — the `pcorr` 1e-05 value, and therefore the 10,000× ratio, is RELAYED, NOT
> VERIFIED.** **No `fvSolution` under `/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/`
> contains the string `pcorr`** — 0 of the non-`processor*` files. The `pcorr` block is
> restored into the live case **at run time**: `verification/runs/F5b_runs/launch_f5b_physics.sh:218`
> greps the running case's `fvSolution` for `pcorr` as its own lever check. **The approved
> 72-core-min run has not yet fired, so the dictionary carrying `pcorr` does not exist on
> disk.** The 10,000× is recorded here as **relayed and not reproducible from any artifact
> this record could find.** **The three design requirements above do not depend on it** and
> stand on their own.

> **`CONFIRMED`** — `pcorr`/`pcorrFinal` **are** declared **`unverifiable-from-logs`** in the
> case's own frozen registration: `verification/campaign/F5b_PHYSICS_PREREGISTRATION.md:635`,
> *"no log line echoes which `fvSolution` entry the moving-mesh flux correction used"*.

#### 6.3.2 The three classification axes, each mechanical

**A1 — DICTIONARY KEY. Never pool two keys into one ratio.**

| key | what it is | in scope for C2? |
|---|---|---|
| `residualControl { … }` | **convergence criterion** for the outer loop — when the run stops | **YES** |
| `solvers { <ch> { tolerance … } }` | **linear-solver drop tolerance** inside one iteration | **NO** — reported in a separate column, never ratioed against the above |

**A2 — CHANNEL ROLE. Primary field of the physics, or auxiliary equation.**

Mechanical rule, no human read required:

- Collapse `<name>Final` onto `<name>` — the same equation at a different corrector stage.
- Expand regex channel patterns (`"(U|p|k)"`) into their member names.
- A channel is **PRIMARY** if its name is a field present in the case's **`0/` directory**.
- A channel is **AUXILIARY** otherwise.

`pcorr` **never appears in `0/`** — it is an internal flux-correction variable — so this rule
classifies it as auxiliary **mechanically**. The same rule catches `Phi`,
`cellDisplacement` and `pointDisplacement` without any of them being named in advance.
**24 repo `fvSolution` files mention `pcorr`, so this is not a one-case special case.**

**A3 — PARALLELISM.** Read `numberOfSubdomains` from `system/decomposeParDict` and confirm
against `processor*` directories. **A serial run cannot exhibit the F6a mechanism**, so C1
and the partition-sensitivity concern do not apply to it. **C2's justification requirement
still does** — a criterion nobody can explain is a defect in serial too.

#### 6.3.3 The statistic is DIRECTIONAL, not a bare ratio

**`bind_ratio` = (loosest PRIMARY tolerance) / (tightest PRIMARY tolerance)**, computed over
**PRIMARY channels under `residualControl` only.** This is the F6a statistic, and **it is the
only statistic the §6.4 thresholds apply to.**

Loose outliers and auxiliary channels are reported under **separate headings** and **never
trip the binding flag.** Under this rule **F5b's primary channels give `bind_ratio` = 10 →
`OK`, no flag** — which is the correct answer, reached mechanically.

#### 6.3.4 A second detector, from the F5b lane's sharper observation

The F5b lane's more valuable finding is **not the ratio**:

> **`pcorr` is simultaneously the LOOSEST channel and the one the case's own registration
> declares `unverifiable-from-logs`. THE LOOSEST LEVER IS THE UNOBSERVABLE ONE.**

That is **a real defect class, and it is not the class the raw ratio finds.** It gets its own
detector, orthogonal to `bind_ratio`:

**`LOOSEST-AND-UNOBSERVABLE`** — flag any channel that is **simultaneously** (a) the loosest
in its block and (b) named in its case's registration as unverifiable, unobservable, or not
echoed to logs. Mechanical test: intersect the loosest-channel name with the set of channels
the pre-registration marks `unverifiable-from-logs` or equivalent.

**Why it matters:** the loosest tolerance is the one doing the most to permit a result, and a
channel nobody can observe is one nobody can check. **The combination is worse than either
alone,** and the raw ratio would have reported it as a binding-tightness problem — the wrong
diagnosis on the right case.

### 6.3a What the sweep would output

One row per `residualControl` block:

| column | content |
|---|---|
| `path` | absolute path to the `fvSolution` |
| `territory` | closure / dafoam / heat-transfer / cfd / ansys-verification, by the §6.2 rule |
| `gating` | does a pre-registration on disk grade a row from this case? yes / no / undetermined |
| `parallel` | `numberOfSubdomains`, and whether `processor*` dirs exist (axis A3) |
| `channels_primary` | primary channels after `Final`-collapse and regex expansion (axis A2) |
| `channels_auxiliary` | auxiliary channels, listed but excluded from `bind_ratio` |
| `tol_primary_min/max` | loosest and tightest **primary** tolerance |
| `bind_ratio` | `tol_primary_max / tol_primary_min` — **§6.3.3** |
| `flag` | `OK` / `FLAG` / `HARD FLAG` per §6.4 |
| `loose_unobservable` | the §6.3.4 detector: yes / no |
| `solver_tolerances` | the `solvers{}` values, **reported, never ratioed against the above** (axis A1) |
| `justification` | does the case's own frozen record justify the extreme primary channels? |

Plus a planted-zero control on every run: **a synthetic block with a known `bind_ratio`, a
known auxiliary channel and a known loose-unobservable pair is planted and read back, and the
sweep refuses to report if it cannot see all three** (standing rule 3). **A classifier is
exactly the kind of reader that returns a confident zero when its rule silently matches
nothing.**

### 6.3b What §6.1's count does and does not cover

§6.1 counted the **`residualControl`** key, which axis A1 now confirms is the right key. It
follows that **the 219 repo files WITHOUT `residualControl` are not thereby uncontrolled**:
**181 of them carry `solvers{}` tolerances** and are transient PIMPLE-type cases whose
stopping behaviour is set by corrector counts and solver tolerances instead — F5b is one of
them. **38 carry neither.**

**Those 181 are outside C2 as written and are NOT counted in the 465.** Whether a transient
case's stopping behaviour needs an equivalent of C2 is **a real question this record does not
answer** and does not quietly fold into the sweep.

### 6.4 The proposed flag threshold, and why — derived from principle

**Proposed: `FLAG` at `bind_ratio` ≥ 100 (two decades). `HARD FLAG` at `bind_ratio` ≥ 1000
(three decades).** Applied **only** to the directional primary-channel statistic of §6.3.3 —
never to a raw min/max over every tolerance in the file.

**The derivation does not use F6a's number and does not look at it.** It rests on two
properties of what a residual control actually is:

1. **The normalisation noise floor is about one decade.** OpenFOAM normalises each
   equation's residual by that equation's own field scale, so channels are already
   dimensionless and are meant to be comparable. The normalisation is imperfect — a channel
   whose normalising factor is weak or near-zero can legitimately sit a decade away from its
   siblings for reasons that are numerical rather than physical. **One decade is therefore
   the honest floor of channel comparability, and a difference inside it means nothing.**

2. **A stiffer equation legitimately earns roughly one more decade.** A `residualControl`
   block is a **conjunction**: the run stops when *every* channel is met, so the stopping
   iteration is set by whichever channel is met **last**. Source-term-dominated transport
   equations — `omega`, `epsilon` — genuinely settle later than the momentum and pressure
   channels, and giving them a tolerance about a decade apart is a defensible engineering
   choice rather than an error.

**One decade of normalisation noise plus one decade of legitimate stiffness gives two
decades.** Beyond 100×, a tolerance difference can no longer be explained by either, and
**must instead be explained in writing** — which is exactly what C2 asks. Beyond 1000×, the
tight channel is not merely the last to be met: under comparable decay rates it is met
*decades* after its siblings, the other channels stop carrying any information about the
stopping decision, and **the block is a single-channel gate written as though it were five.**
That is the `HARD FLAG`.

#### 6.4.1 Two honesty tests on this threshold, stated so a reader can apply them

**Test 1 — it must not be reverse-engineered from F6a.** A threshold chosen to flag F6a by
construction would sit just under F6a's ratio. **F6a's ratio is 5,000.** This threshold is
**100** — F6a exceeds the soft flag by **50×** and the hard flag by **5×**, and both bounds
sit on round decade boundaries that came from the argument above. More to the point:
**100× will flag many blocks besides F6a, and that is the test.** A threshold that flags
exactly one case is a description of that case, not a rule. **If the executed sweep returns
F6a and nothing else, the threshold should be treated as suspect, not as confirmed.**

**Test 2 — it must not fire on a healthy case (the F5b test).** F5b is the standing negative
control. Under §6.3.3 its primary channels give **`bind_ratio` = 10 → `OK`**, while its raw
whole-file ratio — relayed as 10,000× — would have produced a **`HARD FLAG`**. **A sweep
design that cannot show `OK` on F5b is not ready to run**, because it would open its
production life with a false positive on a case Sanaa has just approved, and **a check that
cries wolf on a healthy case teaches the next agent to ignore it.**

**A flag is not a defect.** It marks a block whose primary-channel spread requires the
one-line justification C2 asks for. **A flagged block with a written justification is
compliant.**

### 6.5 Cost

**ZERO COMPUTE. No solver, no mesh, no MPI rank.**

The sweep is a read of dictionaries and a match against pre-registration text.

- **Solver core-minutes: 0.** Nothing is run.
- **Parse cost:** reading and parsing ~1,300 dictionaries is a single-rank operation
  measured in **CPU-seconds**. Under the lab's unit — wall s × ranks ÷ 60 — that is
  **well under 1 core-minute**, and it is stated here as **estimated, not measured**,
  because the parser does not exist yet.
- **The real cost is agent time**, in four parts: writing the parser, the §6.3.2 classifier
  and their planted-zero controls; the `gating` column, which requires matching blocks to
  pre-registrations; the `loose_unobservable` column, which requires reading each case's
  registration for its unverifiability declarations; and reading the flagged blocks to decide
  justify-or-harmonize. **The `gating` and `loose_unobservable` columns are the two that do
  not automate.**

**The §6.3 classification adds work and removes more than it adds.** Three extra axes and a
second detector cost parser effort once; the false flags they prevent would have cost a human
read **per flagged case, on every future run of the sweep.**

**That review cost scales with the FLAG COUNT, not the file count**, and the flag count is
unknown until the sweep runs. **This record therefore does not put a number on agent time.**
An estimate offered before the flag count is known would be a guess wearing a figure's
clothes.

### 6.6 Routing — cfd does not sweep another team's cases

**cfd's own scope is 115 blocks** (§6.2), plus whatever share of `/home/ubuntu/certonomous-runs`
is cfd's — a boundary that must itself be drawn before that store is swept.

**The other 350 repo blocks — dafoam 149, heat-transfer 182, ansys-verification 19 — and
closure's 182 out-of-git blocks belong to their own teams.** cfd does not sweep them without
the chief routing it. **This section is offered to the chief as the routing basis; it is not
a claim on anyone else's territory.**

---

## 7. What this record does and does not do

**It does:** record Sanaa's ratification verbatim; state cfd's four operative clauses;
cite the measured evidence with artifact paths and correct three relayed roundings; bound
the claim honestly; and scope and cost the C4 audit.

**It does not:** authorise any run; alter any frozen gate, threshold, cap or label; file
anything upstream; or execute the §6 sweep.

---

## 8. AMENDMENT — 2026-08-25: **THE SOFT `FLAG ≥ 100` TIER IS RETIRED. THE DISCRIMINATOR IS THE LONE-OUTLIER COLUMN.**

**Insertions-only, appended at the foot. Nothing above this line is edited; §6.4's proposal stands
in the record exactly as it was written, because the reason a threshold was retired is worth more
than the threshold was.**

### 8.1 The ruling

> **A `residualControl` block is FLAGGED when its TIGHTEST tolerance is held by EXACTLY ONE
> CHANNEL — a LONE TIGHT OUTLIER.**
> **`bind_ratio` is a SEVERITY MEASURE ON A FLAGGED BLOCK. IT IS NOT A DETECTOR.**
> **`HARD FLAG` at `bind_ratio ≥ 1000` is VALIDATED AND STANDS.**
> **The bare-ratio soft `FLAG ≥ 100` tier is RETIRED.**

Ruled by the cfd supervisor, 2026-08-25, on this lane's measurement of the tier's own population.

### 8.2 The ground — and it is a measurement, not an argument

§6.4 derived `FLAG ≥ 100` **from principle**, and said so honestly, and added the right test:
*"100× will flag many blocks besides F6a, and that is the test."* **The test was run. The tier
failed it, and it failed in the most complete way a threshold can.**

Measured by `scripts/sweep_residual_criteria.py` over **1,990 non-`processor*` `fvSolution` files,
1,282 carrying a `residualControl` block**, 1,035 with a computable `bind_ratio`
(2026-08-25T17:4xZ). **The sweep was run TWICE, twelve minutes apart, while other teams were
writing into the same corpus: it grew by 2 files and the `OK`→`OK` cell moved 767 → 769, while
EVERY FLAG POPULATION — 90, 151 and 25 — WAS IDENTICAL IN BOTH RUNS.** The counts below are the
second run's.

| what the retired tier caught | count | `bind_ratio` | channels sharing the tightest value |
|---|---|---|---|
| soft `FLAG` population | **90** | **EXACTLY 100.000 — all ninety** | **3 — all ninety**, and the same three every time: `U, k, omega` |

**All ninety sat precisely on the boundary.** `>= 100` catches all ninety; `> 100` catches none.
**A threshold whose entire population sits exactly on its own boundary is not measuring anything —
it is re-describing the convention it was set at.** That convention is the ubiquitous two-tier
`p 1e-6` with `U, k, omega 1e-8`, in which **three channels share the tightest tolerance, so no
single channel can become the sole binding criterion and the F6a mechanism cannot arise.**

And the discriminating column was already visible in the same sweep:

| tier | count | lone tight outlier? |
|---|---|---|
| `HARD FLAG` (≥ 1000) | **151** | **151 of 151 — every one** |
| soft `FLAG` (= 100) | **90** | **0 of 90 — not one** |

**The signal was never the ratio. It was whether ONE channel holds the tightest tolerance alone** —
which is precisely the F6a mechanism §4.2 and §4.3 recorded: one channel 5,000× tighter than its
siblings became the sole binding criterion and measured the partition rather than the convergence.

### 8.3 The corrected counts, re-measured under the new rule

| | retired rule (`ratio ≥ 100 / ≥ 1000`) | **lone-outlier rule** | movement |
|---|---|---|---|
| `HARD FLAG` | 151 | **151** | **unchanged — every one is a lone tight outlier** |
| `FLAG` | 90 | **25** | 90 retired, **25 NEW** |
| `OK` | 794 | **859** | |
| **total flagged** | **241** | **176** | **−65** |

Transition matrix, every cell measured:

| retired → new | count |
|---|---|
| `FLAG` → `OK` | **90** (all at ratio 100.000, all with 3 channels tied) |
| `HARD FLAG` → `HARD FLAG` | **151** (all lone outliers — the tier is confirmed, not merely kept) |
| `OK` → `FLAG` | **25** |
| `OK` → `OK` | **769** |

**THE 25 NEW FLAGS ARE THE POINT.** Every one is a **lone tight outlier at `bind_ratio` 10.0**, with
**`U` as the lone tightest channel in all 25** — 18 in cfd territory, 7 in the out-of-git run store.
**The retired tier could never have seen them**, because 10 is a decade below its boundary. So the
retirement did not merely remove 90 false positives; **it revealed 25 blocks carrying the real F6a
pattern that a ratio threshold was structurally blind to.**

### 8.4 The instrument

`scripts/sweep_residual_criteria.py`. The retirement and its ground are recorded **in the
instrument's own docstring**, beside the code that implements it, so a reader who never finds this
file still finds the reason.

**Two new planted controls were added, and `--selftest` passes all six:**

| control | plant | required |
|---|---|---|
| **P4** positive | lone tight outlier at `bind_ratio` **10** (below the retired boundary) | **must `FLAG`** — measured `FLAG`, `n_at_tightest = 1`, ratio 10.0 |
| **N2** negative | the exact two-tier convention: `p 1e-6`, `(U\|k\|omega) 1e-8`, ratio **exactly 100** | **must stay `OK`** — measured `OK`, `n_at_tightest = 3`, ratio 100.0 |

together with the four already standing (P1 hard-flag 5000×, P2 auxiliary exclusion, P3
loosest-and-unobservable, N1 harmonized-negative). **N2 is the important one: it is the negative
control for the retirement itself**, and without it a later reader could not tell a rule that
correctly ignores the two-tier convention from a rule that has gone blind.

### 8.5 What this amendment does NOT do

It does not touch `HARD FLAG ≥ 1000`, which stands **validated by its own population**. It does not
re-verdict any case: a `FLAG` is a **request for the one-line C2 justification**, never a verdict,
and nothing here converts one into a finding. It does not sweep another team's cases — §6.6's
routing is unchanged. It authorises no run and alters no frozen gate, threshold, cap or label.

**ZERO SOLVER COMPUTE.** This is a dictionary parse over files already on disk.
