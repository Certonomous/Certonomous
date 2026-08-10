# Instrument integrity — 2026-08-11, Katie's dispatch section C

Executed by the Infrastructure and Standards family supervisor.

**Model-rule override, stated not silent (SUPERVISION_CHARTER §5).** This pass ran
on **Opus** because the family's designated tier is credit-exhausted. Recorded on the
work's face so a later reader knows which tier produced it.

**Standing rules this pass was held to.** `LESSONS.md` L-40 (the switch you set is
not the switch that ran), L-43 and its two corollaries (an audit's null is a claim
about its REACH first; a found-dead verdict is a claim about IMPLEMENTATION and
implementation hides in `.H` includes), L-45 (a gate may fail open, never false),
L-46 (a change that creates an artifact is audited from both ends), L-48 (record a
gap as a gap, never as a constraint), L-49 and L-51 (a search has a method **and** a
frame). `VERIFICATION_CHARTER.md` §9. Infra family supervision guidelines v1.13.

**Compute: zero core-minutes.** No solve was run, priced, or requested.

---

## 0. What this pass found, in one place

| item | headline |
|---|---|
| **C1** | **6 FOUND-DEAD across the fleet-wide remainder. Five are in the monitoring and credential standards; one is in the DAFoam echo. The hump-adjoint attempts — the target Katie named — are CLEAN: zero found-dead in 13 lever/conclusion pairs.** |
| **C2** | **100 instruments in frame; 67 never ask "did the check run?"; 9 have a third state; 20 are false-positive channels and 12 of those have a named archived conclusion through them.** The worst is not a parser at all — it is a corpus glob that fed six adopted monitor rules a quarter of the archive. |
| **C5** | The check exists and fires. **The dispatch's 29 is a subtree count; repo-wide the frame is 238 shebang-bearing tracked files of which 3 had an exec bit.** One of the 29 turned out to be load-bearing for a safety gate and is fixed; 28 remain, split by owner below. |

**The single most important finding of the night sits across C2 and C5 at once**, and
it is section 3.1: `launch_solve.sh` gated its preflight on `[ -x "$PF" ]` while
`case_preflight.sh` was tracked non-executable, so **every fresh clone of this
repository launched solves with the preflight silently skipped** — the exact
silence-read-as-success shape C2 was dispatched to hunt, inside the launcher the lab
moved its discipline into.

---

## 1. C1 — DEAD-LEVER AUDIT, FLEET-WIDE

### 1.0 The frame, and why it is three frames

Two prior audits exist and were not redone:

- `DEAD_LEVER_AUDIT_2026-08-08.md` — its own method line scopes it to conclusion-bearing
  records under `demo-output/website/` limited to `campaign/`, `dafoam/`, and three
  family status files. **Everything else in the repository was outside its frame**, which
  is a fact about that audit's reach and not about the world (L-43).
- `DEAD_LEVER_AUDIT_BATCH_2026-08-10.md` — the batch / `mega_batch` / model-form family.

Fleet-wide coverage of the remainder was therefore split three ways, each with its own
stated frame:

| sweep | frame | what the frame structurally cannot contain |
|---|---|---|
| **C1-A** | every hump-adjoint attempt, anywhere under `/home/ubuntu` | runs that left no log; the in-container DAFoam build; levers OpenFOAM never echoes; two 906 MB tarballs left unopened |
| **C1-B** | records added since 2026-08-08 under `campaign/` + `dafoam/` (213 paths, 41 `.md`), plus 38 pre-existing records materially amended after it, plus the 08-08 audit's four declared truncations | a stale conclusion nobody edited is invisible to a git-diff frame; the C++ build; gitignored ledger rows |
| **C1-C** | the surfaces neither prior audit touched: `docs/**`, `models/`, `mission-output/`, `chief-engineer-runs/`, root `.md`, and every `demo-output/website/` subtree outside `campaign/`+`dafoam/` | see 1.4 |

**Lower-bound declaration (L-49).** C1-B and C1-C drew part of their lever vocabulary
from the records they were reading. Their counts are **lower bounds, not censuses**, and
are labelled so wherever they appear.

### 1.1 C1-A — every hump-adjoint attempt. The named target. **CLEAN.**

Katie named this explicitly: a lever may have been off on the hump exactly as
`transonicPCOption` was for M6. It was not.

**Frame.** Three independent instruments over `/home/ubuntu` (17 GB `Certonomous`
+ 66 GB `certonomous-runs`): a filename `find` (355 paths), a content fingerprint
(`Find 622 reference points`, the hump objective), and a universal DAFoam-adjoint
marker (`transonicPCOption`) which establishes the archive's **total population of
DAFoam adjoint logs at 651**. The hump members were isolated from that population
rather than searched for by name — so the frame is defined by what a DAFoam adjoint
run always prints, not by what the auditor thought to spell.

**Positive controls: 8 run, 6 passed, 2 failed and were discarded.** Both failures
were caught by the control rather than by the finding:

- one instrument used a flag GNU `grep` does not have, so its null carried exit 2 — **VOID, not an absence**;
- one 79 GB-class sweep hit exit 124 — **a timeout null, discarded**, its ground re-covered by three other passing controls.

**Inventory: 9 hump-adjoint artifacts.** 7 substantive runtime logs, 2 memory
companions. 6 reached the adjoint linear solve; 1 was killed before a reason code; 1
never reached the adjoint at all. **Plus one attempt outside every prior audit's
frame** — `certonomous-runs/adjwall/HUMP51k/log.run`, a hump-geometry `DASimpleFoam`
adjoint staging from 2026-07-30 that **no archived record cites**. It reopens nothing
because nothing rests on it, but it belongs in the frame and is now in it.

**Two attempts left no log** (aborted stagings ledgered at ~40 s in
`W4_ADJOINT_PC_UNBLOCK.md:300`). Reported as findings, not absences: no conclusion
rests on them.

**Result: 13 lever/conclusion pairs — 9 VERIFIED, 3 UNVERIFIABLE-FROM-LOGS, 1 LATENT,
0 FOUND-DEAD.**

**The M6-analogue question, answered explicitly.** `transonicPCOption` **is** echoed in
all seven substantive hump adjoint logs — value `-1`, solver `DASimpleFoam`
(`hump_adjoint_run1.log:409 solverName DASimpleFoam;`, `:514` for the echo). It is
**LATENT, not FOUND-DEAD**, for two independent reasons either of which suffices:

1. **No conclusion leans on it.** Every `transonicPCOption` mention in the repository
   is M6/A3-family, and the only two that name the hump place it explicitly outside
   hump scope — `W4_ADJOINT_PC_UNBLOCK.md:288` reads *"Lead 1.5 (`transonicPCOption`
   for M6): out of this item's gate (compressible…)"*.
2. **The deadness claim is declined on its merits**, per L-43's second corollary. The
   relevant residual class would be `DAResidualSimpleFoam.C`, which is **not on this
   host** — verified, with a positive control proving the same `find` locates
   `runScript_hump.py`. The verdict is therefore recorded as *"not found in the files
   searched, which were: the seven hump runtime logs, every `.md`/`.json`/`.html`
   under `Certonomous`, and a whole-filesystem `find` for `DAResidual*.C`,
   `pyDAFoam.py`, `DALinearEqn.C`."* **A negative claim without its search space is
   not a finding.**

**A strengthening, not just a confirmation.** The 08-08 audit verified S1 rung 4
(`jacMatReOrdering natural` stops the NaN) from the **dictionary echo**. This sweep
found the **PC runtime banner** — `hump_nat_run1.log:2238 Mat ReOrdering: natural`
against baseline `hump_adjoint_run1.log:2273 Mat ReOrdering: rcm`. The row moves from
configured-and-echoed to configured-and-observed-in-the-preconditioner.

**One caveat the sweep adds to a verified row.** `S1_FIML_FIELD_INVERSION.md:351`
says the `limitVelocity` fvOption was *"inert at the solution, max abs U 44.54"*. The
inertness is VERIFIED (all 721 `Limited` lines read `0 (0%) of cells`, and those lines
are **not** `printInterval`-gated). **The number 44.54 appears in no archived hump
log** — it was evidently computed offline from a field file. UNVERIFIABLE-FROM-LOGS,
non-load-bearing, owed a face caveat.

### 1.2 C1-B — records created after the 08-08 audit, plus that audit's four truncations

**30 lever/conclusion pairs — 25 VERIFIED, 4 UNVERIFIABLE-FROM-LOGS, 1 FOUND-DEAD.**

**Three of the 08-08 audit's four declared truncations are now CLOSED**, all verifying:

| truncation | outcome |
|---|---|
| `rotation_branch` D2–D6 | **CLOSED, all VERIFIED.** The 08-08 audit *inferred* these from the D1a/D1b pair's echo format. The inference was correct: every log carries the runtime dict at `:509-519` plus a `REPRO` line — `D3 evalMode: 'exact'` vs `'fast'`, `D6 useRotations: True/False`, `D5a jacMatReOrdering rcm` vs `natural` |
| `PROOF.md` §23 capstone | **VERIFIED to every quoted digit** — `D6_predeform_on.log:838 ‖dXs‖=1.566420804338303e+03`; sign flips at `D1a` idx 8 (2.0704) gone in D6, worst residual 0.0822, exactly the record's "207.0% → 8.22%" |
| `W4-a4-du0check` | **CLOSED, VERIFIED from its own log** — `du0_np4scotch.log:11708`, `scotch [4]` at `:48`, ledger 12.20 core-min matching the record |
| `PROOF.md` §1–24 interior | **STILL OPEN.** ~2,400 lines. Its lever conclusions surface in rows audited elsewhere, but that is inference, not measurement. Carried forward. |

The 08-08 audit's section-7 claim (25 narrative files "swept, nothing load-bearing")
was **spot-checked on 5 rather than inherited**. It holds on 4. The exception:
`CHALLENGE_SLATE_2026-08.md:91` asserts *"initialisation trap named — potentialFoam
baked the frame sweep into the zone"* on its own face — a lever-citing conclusion
restating F8, not the bare pointer section 7 classes it as.

**FOUND-DEAD FD-1 — DAFoam's `printInfo` echo is a REQUESTED-value print, not an
EFFECTIVE-value print.** In one file, unambiguously:

```
A3-gateB-restoration/gateB.log:861   Solver Type: gmres
A3-gateB-restoration/gateB.log:862   GMRES Restart: 200
A3-gateB-restoration/gateB.log:884       type: fgmres        <- -ksp_view, same run
A3-gateB-restoration/gateB.log:885       restart=30
```

Same pattern in `A3-stage2-lgmres/stage2_lgmres.log:862` vs `:879`, and
`A3-stage2-gamg/stage2_gamg.log:862` vs `:884`.

**Conclusions it reopens: NONE — and that is a finding about foresight, not luck.**
`A3_STAGE2_UNREACHABLE_CLASS_PREREGISTRATION.md:50-52` pre-registered, *before the
runs*, that the `Solver Type:` line would still print the requested value and that
`-ksp_view` must be read back and quoted. It was. Both stage-2 arms are verified on
`-ksp_view`. This is the pre-registration machinery doing exactly the job it exists
for, and it deserves to be said.

**The residual gap the chief should see.** FD-1's blast radius is bounded by the
argument that *on the shipped image the `PETSC_OPTIONS` override is discarded, so
requested ≡ effective*. That argument carries the entire pre-2026-08-10 DAFoam corpus
and it is an **argument, not an artifact**: `PETSC_OPTIONS` is recorded nowhere in
`A3-onera-m6-sweep-n15_21840/` or `W4-a4-discriminators/`, and a positive control
confirms the token *is* greppable where it exists. The 08-10 runs closed this by
putting `PETSC_OPTIONS=[…]` into `lever_echo.txt`.
`DEFECT_CANDIDATE_ksp_options_override.md:160-163` already recommends an
effective-value echo; this audit endorses that from the archive.

**The strongest lever proof in the new corpus**, worth naming because it shows the
echo working as designed: `F5C_STAGE_A_RESULTS.md:84-88` claims `consistent yes;` is
literally readable inside the gzipped archived log. It is —
`F5c_runs/stage_a_A1/log.simpleFoam.gz:70`, against `consistent no;` at `:70` in A3
and A4, with each echo's `fvSolution` sha256 matching `sha256sum` of the archived
dictionary. **A structurally-unecho-able lever became log-provable.** That is the
answer to the 08-08 audit's four-echo-less-classes finding.

**Echo coverage, measured:** B-52 turn-closure draws **5 of 8** carry an echo; Ahmed
c3 **3 of 4**; F5c **4 of 4**; FPE diag **5 of 5**. Every post-`199e9d17` launch
carries it; every pre-`199e9d17` parallel launch does not. Lower bound.

**And a structural gap now quantified rather than asserted:** the token `consistent`
appears in **zero of the 297 files in `solve_registry/`**, with a positive control
proving the directory readable. The 08-08 audit said stock OpenFOAM never echoes
`consistent`; that is now a measurement.

### 1.3 C1-C — the surfaces neither prior audit touched

*(Consolidated detail pending from the sweep; the FOUND-DEAD count and the two
highest-impact rows are established and are reported in 1.4.)*

**Corrected split: 145 files swept, 106 lever-bearing, 39 not.** The sweep published
a first-pass split of 103/78/25 and then **corrected its own count on its own face**
when a delegated surface returned, because the first version had absorbed 42
undelivered files into the "not lever-bearing" column. That is the right handling and
it is noted rather than smoothed over.

### 1.4 FOUND-DEAD list, ranked by reopening impact

**Six across the fleet-wide remainder. None in the batch family; none on the hump.**
Katie's rule applies: each names the conclusion it reopens, and **no conclusion is
rewritten here.**

| rank | found-dead | reopens | why it ranks here |
|---|---|---|---|
| **1** | **D1 — monitor rules S6/S8 are unreachable in production.** The standard's per-rule Status lines are honest ("when constructed with `residual_target`"); **nobody ever checked whether anything constructs it that way.** **Re-verified firsthand by this supervisor:** `residual_target` is passed at exactly two kinds of site — `sdk/tests/test_head_engineer.py:109,131,178` (tests) and `sdk/scripts/replay_monitor_rules.py:134,231` (the replay harness). **Zero production paths.** `head_engineer.py:592` `if self.residual_target is None … return` is the gate that never opens | `MONITOR_STANDARD.md`'s S6/S8 status; **unrecorded anywhere in the lab's own records** | A rule that cannot fire is a rule the lab believes it has and does not. Highest impact and, uniquely on this list, **not previously written down anywhere** |
| **2** | **D4 — `MONITOR_STANDARD.md:64-67`'s universal is false.** It states *"every OpenFOAM log prints a trapping banner (`trapFpe: …`)… Evidence: motorcycle benchmark logs, knowledge base fact 7."* **Re-verified firsthand:** `solve_registry/b3_diag_frozen{4,5}_*.log` carry **0** `trapFpe` hits while being unambiguously genuine solver logs (11,914 lines, **11,088 `Initial residual` lines**, `Selecting incompressible transport model Newtonian`), against a **positive control confirming the token is findable where it exists** (`F5c_runs/…/log.blockMesh`, 1 hit). Its cited evidence, `NUMERICS_KNOWLEDGE.md:34-41`, describes a **superseded motorBike mesh** (353,578 cells / skew 8.94, replaced by 353,688 / skew 3.99 per `MOTORBIKE.md:45`) | **two** conclusions: `NUMERICS_KNOWLEDGE.md:39-41` and `MONITOR_STANDARD.md:64-67` | **The rule itself survives and is still correct** — keying `sigFpe::sigHandler` is strictly safer than keying the banner either way. Only the *warrant* is defective, and it is defective twice over |
| **3** | **D2 — `LogMonitor.check_wall_time` has no callers outside its own test.** | `MONITOR_STANDARD.md:342-356` and `VERIFICATION_CHARTER.md:816-827`, which both record a five-day defect in which *"every caller that took the monitor default was judging on a threshold nobody approved"* | The correction has landed (`head_engineer.py:641` now reads `flag_multiple: float = FLAG_MULTIPLE`). But **"every caller" was the test suite** — the recorded defect had empty production blast radius. Good news about the defect, bad news about the rule: it is the same fact that makes D1 true |
| **4** | **FD-1 — DAFoam `printInfo` prints requested, not effective, KSP settings** (section 1.2) | nothing — pre-registered around before the runs | Zero reopening. Listed because the *reason* it reopens nothing is a repeatable practice worth citing |
| **5–6** | **D3 and D5** | *(detail pending consolidation; see 1.3)* | |

**Two leads escalated but NOT log-verified — flagged as leads, not findings:**

1. **L-47 relaxation is the only explicitly-open, never-tested lever with live verdicts
   stacked on it.** `F6b_ERCOFTAC_RESULTS.md:171` names its own gap (*"a 62,400-cell
   mesh may simply need tighter under-relaxation… should be tested first"*) while its
   reattachment claim sits +63–66% against reference; the R4 Ahmed ladder rests a
   non-monotone Cd verdict on differences comparable to settle noise at identical
   `U 0.9`; and the 36 model-form records share one untested relaxation setting *by
   design*. **Three standing verdicts, one untested switch.** L-47 says two solves
   differing only in relaxation must agree at convergence — this is exactly its case,
   and it costs one extra solve per arm. **Priced, not spent: routed to the chief.**
2. **S10a — `printInterval` gates whether the evidence is written at all.**
   `MONITOR_STANDARD.md:804-831` records *"689 clip events where the archive recorded
   3."* That is L-40 in the **observability** dimension: the switch governing whether a
   lever's activity can ever be seen. **Every archived clip rate in this lab is a
   floor.**

### 1.5 UNVERIFIABLE-FROM-LOGS added by this pass

| entry | reason class |
|---|---|
| `consistent` binding for the A1 SIMPLEC pair (435 vs 490 iterations are VERIFIED; the *binding* is not) | structural — DAFoam never prints the fvSolution SIMPLE sub-dict; 0 of 297 `solve_registry` files contain the token |
| `fvSchemes`/relaxation sameness for the 3 pre-echo B-52 turn-closure draws | pre-`199e9d17` parallel launch, no echo |
| dictionary sameness of the published Ahmed c3 to its 3 new sibling draws | same; the 3 new draws echo `fvSchemes b277ad5c…`, the published c3 has 0 echo lines |
| `pcFillLevel` under sub-LU on the hump | needs the build's view, which this host does not have. **No conclusion leans on it** |
| "max abs U 44.54" on the hump | computed offline; in no archived log |
| `PROOF.md:2421` ‖dXs‖ "1.566e+03 versus 1.495e+03" | verbatim correct, but the `off` arm is **bit-identical to the undeformed D1b** on all 27 FD/AN pairs — only one arm of the "versus" moved. Two readings survive and **cannot be discriminated without IDWarp source**, which is not on this host. A §9 caveat, explicitly **not** a dead lever |

### 1.6 Secondary defects surfaced (not corrected — read-only, per the negative-verdict process)

1. `R4_AHMED_C3_LEG2_RESULTS.md:21` gives the `residualControl` range as "181–210
   iterations". The published c3 met it at **220** (`R4_runs/c3/log.simpleFoam:6659`).
   The claim is true; the range is wrong, and ranges get quoted onward.
2. `A3_RUNG3_N52_RESULT.md:11-12` says both solves collapse to *"exactly 0.0"*. CL is
   exactly `0.000000000000e+00`; **CD is `9.490658670647e-154`**. Same verdict, but
   "exactly 0.0" is true of one solve, not both — the same false-precision class that
   record already corrected once at `:43-48`.
3. `PROOF.md:2423` cites `rotation_branch/D6_predeform_{on,off}.txt`; the archive holds
   `.log`.

---

## 2. C2 — FAIL-FALSE SWEEP: every parser and gate in the lab

### 2.1 Frame

Instruments were enumerated three ways, deliberately overlapping: an **AST detector**
flagging any function that both reads something external *and* emits a verdict;
**idiom greps** for the seven named fail-false shapes plus shell-specific ones
(`grep -c`, missing `pipefail`, `|| true`, `2>/dev/null`); and a **deep read** of
every candidate against the fixed `parse_check_log` as the template.

**100 candidate instruments in production code** (80 in `sdk/**` + `scripts/**`, 20
under `demo-output/**`), across 56 files. 211 of 226 `demo-output` `.py` files emit
no verdict and are out of frame.

**What the frame structurally cannot contain:** gates that are human procedure in
Markdown; solver-side gates inside OpenFOAM dictionaries; CI/git-hook gates (**there
are none** — no `.github/workflows`, no non-sample hooks); `.ps1` files; and any
function whose verdict travels through a variable name the detector's token lists do
not contain — an unquantified residual false-negative rate, stated because it is
real.

### 2.2 Positive control, with its success condition stated first

**Condition, fixed before running:** pointed at `git show 06f747e8^:…/mesh_certificate.py`,
the detector must flag `parse_check_log` with **both** `third_state` and `asks_ran`
absent; pointed at the fixed file, it must flag the same function with both present.
A detector that cannot separate those two cannot report an absence.

**PASS.** Pre-fix → `succ=['clean'], unknown=[], asks_ran=[]`. Post-fix →
`unknown=['unverified'], asks_ran=['completed','_FATAL','End\b','did not run','terminated']`.
**The first widened detector FAILED this control** (it read module constants as
absent) and was rejected and rebuilt before any sweep ran.

**One instrument failure caught mid-audit and disclosed.** `timeout 100 command grep …`
silently fails — `timeout` cannot invoke a shell builtin — and returns a clean exit
through `head`. It was initially read as "zero archived records carry `unsettled`".
**VOID, not an absence**; the correct answer is 52. Every count was re-derived without
that construction.

### 2.3 Counts, with their frame

Frame: the 100 in-frame production instruments.

| measure | count |
|---|---|
| carry any "did the check run?" marker | **33** |
| carry **none** | **67** |
| have a **named third state** for unknown | **9** |
| contain a swallowing `except` in a verdict path | **17** |
| ranked MEDIUM or above | 26 |
| **false-positive channels** (say verified when it is not) | **20** |
| …of which have a **named archived conclusion** through them | **12** |

### 2.4 Per-instrument table — everything ranked MEDIUM or above

**FP** = false-positive channel. **FO** = fails open. Per L-45, false-positive
channels are ranked above every false-negative, including larger ones.

| # | instrument | what it gates | asks "did it run?" | third state | could a recorded conclusion have passed through it? |
|---|---|---|---|---|---|
| FP-1 | `sdk/scripts/replay_monitor_rules.py:157` | adoption of monitor rules S1–S6 | **N** | **lacks** | **YES** — `MONITOR_STANDARD.md` §3.5 + `monitor/replay_s1_s6.json`; **S6's conclusion is refuted** |
| FP-2 | `scripts/case_preflight.sh:105,217,226,231,248` | every long solve's launch | **N** | **lacks** (2 exits) | **YES** — 146 `.done` records; `F11_lid_driven_cavity_ladder.md:174` "run clean on every case" |
| FP-3 | `sdk/scripts/replay_s12_unsettled_stop.py:127` | S12 corpus characterization | partial | partial | **YES** — `monitor/replay_s12.json`; **48 of 162 labels unsupported** |
| FP-4 | `sdk/workflows/crm_wingbody.py:73` (+`onera_m6.py:40`) | "Converged at iteration", VALIDATED tier | **N** | lacks | **YES** — `mission-output/crm-wingbody/transcript.txt:29 Verdict: validated` |
| FP-5 | `crm_wingbody.py:341` / `onera_m6.py:654` | the monitor's fatal-scan claim | **N — no scan at all** | N/A | **YES** — both archived transcripts |
| FP-6 | `geometry_study.py:mesh_gates_pass:556` + `head_engineer.py:collect_mesh_stats:1352` | `in_validated_regime` for 9 workflows; every non-certificate mesh verdict | **N** (returncode never read) | lacks | **YES** — `mission-output/nasa-hump/`, `ahmed-body/`; 14 archived `report.md` |
| FP-7 | `head_engineer.py:report_markdown:1450` | archived mission report | **N** | lacks | **YES — 8 of 9 print `Geometry \| n/a, no issues found`** |
| FP-8 | `sdk/scripts/closure_baseline_error_gate.py:466` | whether the C1 decline gate works | N/A | lacks | **YES** — cited by the round-3 gated submission |
| FP-9 | `sdk/scripts/is_idle.sh:73` | auto-stop; **powers off the box** | **N** (`pgrep` exit never read) | lacks | **YES** — `OTHER_WORK_STATUS.md:50`; realized 2026-07-30 10:40 |
| FP-10 | `head_engineer.py:stage_case:917` | **arbitrary-code-execution admission** | **N** — the only `_wsl` call in the class without a sentinel | lacks | wired; no archived record of the scan's own result |
| FP-11 | `sdk/scripts/model_form_batch.py:721` | S12 clause of the model-form gate | **N** | lacks | **YES** — 11 records; **0 verdicts flipped** |
| FP-12/13 | `verify_warm_replay.sh:124,149,240`; `audit_transcripts.sh:62` | pre-filming replay + discretion proofs | **N** | lacks | wired; no archived verdict |
| FP-14 | `scripts/contention_audit.py:215` | whether a wall clock may be priced | **N** | lacks | **YES** — `CALIBRATION_SCORECARD_2026-08.md` §3 |
| FP-15 | `validate_closure_mesh_recon.py:119` | trust in reconstructed training fields | N/A | lacks | **YES** — 3 PASS strings hand-transcribed into `…round2.json:65` |
| FP-16 | `closure_divergence_audit.py:272` | regenerated-vs-shipped CSV match | **N** | lacks (`.get(k, 0.0)`) | **YES** — divergence audit + submission draft |
| FP-17 | `scripts/check_convergence_sweep.py:100` | L-14 closure | **N** | N/A | **YES** — `NOT_PASSING_REGISTER.md`, `IMPROVEMENT_DASHBOARD:93` |
| FP-18 | `scripts/ledger_backup.py:193,199` | L-2 closure ("verified backup") | **N** | lacks | **YES** — 2 `.METADATA` files assert facts nothing checked |
| FP-19 | `sdk/chief_engineer/lab.py:trust:203` + 15 workflow call sites | **the fidelity tier itself** | **N** | `grid_conclusive` has one; `converged` does not | latent — **0 of 16 archived tiers are UNCONVERGED** |
| FP-20 | `geometry_study.py:2414` / `ahmed_body.py:788` | settling falsifier narration | **N** | lacks (None→pass) | **YES** — 1 instance, `plots/submarine_sail/events.jsonl:203` |
| FP-21/22/23 | `credibility.py:394`; `agenda.py:1097`; `debrief.py:67` | robustness score; the cost rail; lesson entry | **N** | lacks | wired; the single archived lesson passed **vacuously** |
| FO→FP | `log_signatures.py` — 6 detectors | every S-rule fire | **N** | **only `grade_bounding_episode` has one** | consumers read bare `None` as clean |

**Instruments that already do it right, and should be cited when fixing the above:**
`mesh_certificate.parse_check_log`; `lever_echo.levers_verified_active`;
`uncertainty_band.compose`; `uq.reportable_band`;
`log_signatures.grade_bounding_episode` (`{"graded": False}`);
`check_convergence.py`'s `CANNOT_TELL` + exit 2; `morning_report.py`'s `PENDING:`;
`mint_retrospective_certificates.py` (every refusal a named class);
`model_form_batch.apply_mesh_gate` (unreadable = breach, refuses the exemption);
`rae2822_case9.mesh_gate:746`; `dow_2011_table42_check.py` (carries a negative
control); and `launch_solve.sh`'s new `PREFLIGHT NOT RUN` (section 3.1).

### 2.5 The four findings that matter most

**FP-1. A published standard's conclusions rest on a corpus glob that omits three
quarters of the archive. Verified firsthand by this supervisor.**

`sdk/scripts/replay_monitor_rules.py:157` reads `logs = sorted(ARCHIVE_ROOT.rglob("*.log"))`.
**OpenFOAM's own naming convention is `log.<app>`, which that glob cannot match.**
Measured now, frame `demo-output/**`:

| pattern | files |
|---|---|
| `*.log` (what the glob sees) | **590** |
| `log.*` plain (invisible to it) | **950** |
| `log.*.gz` (invisible to it) | **78** |
| **total** | **1,618** |

The archived `replay_s1_s6.json` records `corpus.all = 449`, `with_residuals = 144`.
**Every fire rate in `MONITOR_STANDARD.md` §3.5 — S1's `14 of 449`, S3's `158 of 449`
— has a denominator built from roughly a quarter of the residual-carrying archive.**

And one published conclusion is **refuted by the omitted files**.
`MONITOR_STANDARD.md:785` states: *"What S6 needs is not a cleverer sweep, it is one
archived case outside this family that declares a target it actually reaches."*
Replaying `case_targets` over the 950 excluded logs found **53 such cases across 10
families** — 17 in `mega-batch/work/ahmed-viscous`, 11 in `mega-batch/work/cylinder`,
6 in `campaign/R4_runs`, 5 each in `dafoam/rans_model_comparison`, `campaign/F8_runs`
and `campaign/W3_runs`. **The thing the standard says the archive does not contain is
in the archive, filtered out by a glob.**

This outranks everything else by L-45's asymmetry: it is not one bad record, it is a
*measurement instrument* whose output is the evidence base for six adopted rules, and
its cleanup is the whole corpus it touched.

**FP-3. The S12 replay affirms "ran-to-end" from a regex that did not match** —
`return "residual-converged" if STOP_CONVERGED.search(text) else "ran-to-end"`. The
docstring reasons carefully about returning `"unknown"` for a *missing* log
(*"the archive not keeping it is a fact about the archive, not about the run"*) and
then makes an affirmative claim about a run's ending from a **non-match**. That is
tonight's specimen verbatim, inside the harness that certifies monitor rules. Of 162
`ran-to-end` labels: **35 are gzipped** (binary read, neither regex can match, so a
genuinely converged run is *pushed into* `ran-to-end`), **13 carry no completion
marker at all**, 114 genuinely completed. **48 of 162 unsupported.** The 36 fire
counts are unaffected — histories come from `coefficient.dat`, which is not gzipped —
so only the attribution and corpus characterization move.

**FP-4/5. A VALIDATED verdict and a "none seen" fatal scan, both manufactured.**
`crm_wingbody.py:73` returns the last `Time = N` line as **`converged_iteration`** —
nothing measures convergence. `crm_wingbody.py:341` sets
`monitor_note = "• Watched the solver log for the fatal patterns … none seen."` as an
**unconditional string constant**, with no scan preceding it. Both are in
`mission-output/crm-wingbody/transcript.txt` backing `Verdict: validated`. And line
17 of that transcript reads `Time none this pass … replayed from the run that solved
it` — **the VALIDATED tier was minted from a cached log on a warm replay**, admitted
on a `DONE` file containing a directory name, with no exit status and no completion
marker.

**FP-6. The mesh gate reads a missing measurement as a perfect one.**
`geometry_study.py:556` is
`return ((non_ortho or 0) <= MAX_NON_ORTHOGONALITY and (skew or 0) <= MAX_SKEWNESS)`.
Executed: `mesh_gates_pass(None, None) → True`; `mesh_gates_pass(85.0, 9.0) → False`.
**An unmeasured mesh scores identically to a perfect one.** Its feeder never inspects
`check.returncode`, and it computes a genuine positive marker
(`mesh_ok = "Mesh OK" in text`) **that every consumer ignores**.
`ahmed_body.py:474/489` prints the contradiction on one row:
`Max non-orthogonality | n/a | 70° | Inside the gate`. Meanwhile
`rae2822_case9.mesh_gate:746` does the same job **correctly**. Two contradictory
conventions for one gate.

**Vacuous 0-of-0 passes, executed and confirmed:** `verify_warm_replay.sh not-a-real-act`
→ `identical: 0 clocks-only: 0 differing or failed: 0`, **exit 0**;
`contention_audit.py --window 2030-…` → **exit 0** via
`return 1 if state.get("below_usable_ratio") else 0` on a key that does not exist,
with the docstring telling callers to gate on that exit code;
`audit_transcripts.sh:62` prints `clean: no banned vocabulary in any act transcript`
with nothing counting files (its sibling `audit_camera_discretion.sh:187` **does**
print `$files camera surface(s) scanned`).

**Open but never fired, and measured rather than assumed:** `check_convergence.py`
returns CONVERGED at lines 314 and 366 **before** `crash = _find_crash(text)` at line
317 is consulted. Exposure measured at **zero** — all 11 archived CONVERGED records
carry `crashmarkers=0`, and no registry log holds both a converged statement and a
fatal marker.

### 2.6 C4 — proposed fixes, each with its WHOLE-CORPUS calibration plan and that plan's cost

**No detector or pattern was changed by this sweep.** C4 binds: any change re-runs its
calibration over the **whole corpus, never the sample under test**, because the last
widening misread all 105 real logs when a term was added after calibration and before
re-validation. Each cost below is **recorded beside the pattern** so that cannot
recur.

| # | proposed change | whole corpus it must be recalibrated against | cost of that recalibration | what it will move |
|---|---|---|---|---|
| **P1** | `replay_monitor_rules.py:157` — widen to `log.*` and `.gz`, add a `corpus_incomplete` guard | **1,618 log files** under `demo-output` (590 + 950 + 78), ≥511 carrying residual lines | **< 2 min wall, 0 core-min** (pure file reads; the comparable S12 harness timed at 8.17 s) | every fire rate in `MONITOR_STANDARD.md` §3.5; **S6's line 785 must be withdrawn or amended** — 53 counter-examples already exist |
| **P2** | `replay_s12_unsettled_stop.py:127` — read gzip; split `ran-to-end` into `ran-to-end` (positive marker present) and `stopped-without-marker` | **477 coefficient files / 942 histories / 473 cases** across repo + `certonomous-runs` | **8.17 s, 0 core-min** (measured by running it to scratch) | ~35 labels move on the gzip fix alone, ~13 into the new third state |
| **P3** | `mesh_gates_pass` + `collect_mesh_stats` — make `None` a **breach**, not a zero; check `returncode`; adopt `rae2822_case9.mesh_gate:746`'s convention | **338 archived `log.checkMesh`** (repo + `certonomous-runs`) | **~2 s, 0 core-min — and it has already been run**: 0 of 338 fail to yield both readings, so **zero archived runs flip** | nothing retroactively; the fix is provably free of retro-impugnment. *This is what running the corpus rather than the sample buys.* |
| **P4** | `settle_verdict_s12:721` — return `"unjudgeable"` + reason instead of `unsettled: False` when `detect_unsettled_stop` declines on a length/scale ground (it returns `None` for **five** distinct reasons, only one of which means settled) | the 942 histories of P2, plus the 70-row `MODEL_FORM_runs/ledger.jsonl` and 32 `settle_s12` blocks | seconds | **11 archived records** gain `"unjudgeable"`; **no verdict flips** (all 11 already excluded on other grounds). An evidence-quality amendment, not a revocation |
| **P5** | `head_engineer.py:917` — give the **code-execution scan** a sentinel (`; echo __SCAN_DONE__`) and refuse when it is absent, matching the eight sibling `_wsl` calls | none — the gate has no calibrated pattern | one test | **Highest consequence-per-line on this list** |
| **P6** | `case_preflight.sh` — print `n of m checks executed`; drop the unconditional `ok: solver field headers parsed`; make `(0 patches)` a **skip** not an `ok`; narrow the `"\".*\""` escape hatch; close `launch_solve.sh`'s `[ -d "$CASE" ]` with an else branch | the **146 archived `.done` records** — replay preflight over each recorded `case:` path | file reads, minutes | **This corpus replay was NOT run and should be run before the change lands** |
| **P7** | exit codes on `validate_closure_mesh_recon.py`, `validate_pressure_fields.py`, `validate_motorbike_pressure.py`, `check_convergence_sweep.py` — all `return 0` regardless of findings | each over its own inputs | seconds each | which archived PASS strings were transcribed from a harness that **could not fail** |
| **P8** | `trust()` / `validate_against_reference()` — drop the `= True` defaults on `converged`, `in_validated_regime`, `calibrated`, `solver_backed`; make them required | the **16 archived credential tiers** and 15 literal call sites | seconds | **0 tiers change today** — which is exactly why it is cheap now and expensive after the first record without an `ok` key |

**L-46 enumeration for P1 and P2, since both touch artifacts the lab reads.** P1 must
**amend `replay_s1_s6.json` in place with a dated note (L-44)** and must NOT write to
a new path — `MONITOR_STANDARD.md:542` cites the artifact, and any consumer
discovering monitor artifacts by pattern would otherwise pick up two. P2's new
`stopped-without-marker` value must be added to every consumer of
`fired_by_stop_reason`; `MESH_CERT_RULINGS_2026-08-10/RULINGS.md:217` cites
`ran-to-end` **by name**.

---

## 3. C5 — FRESH-CLONE PREFLIGHT

### 3.1 The finding: C5 and C2 are the same defect

`scripts/launch_solve.sh:158-164`, before tonight:

```bash
PF=/home/ubuntu/Certonomous/scripts/case_preflight.sh
if [ -x "$PF" ] && [ -d "$CASE" ]; then
    if ! "$PF" "$CASE" --quiet; then
        echo "REFUSING TO LAUNCH: $CASE failed preflight. Fix it, do not override."
        exit 1
    fi
fi
```

`scripts/case_preflight.sh` was tracked **100644**. So on a fresh clone `[ -x "$PF" ]`
is false, **the entire preflight gate is skipped, and the launcher launches** — with
no line in the output saying the case was never checked. `LESSONS.md` D12 line 329
promises the launcher *"runs `case_preflight.sh` and refuses to launch if it fails"*,
as one of four things *"the caller cannot forget"*. **On a clone, the harness forgot
too.**

**This box masked it completely.** The working copy carried the bit locally while the
committed tree did not: `stat` read `775`, `git ls-tree HEAD` read `100644`, and only
the commit travels.

**Demonstrated rather than argued** (L-46's third instance rule), with a preflight
that always fails:

| preflight mode | what the gate did |
|---|---|
| `755` (positive control) | `PREFLIGHT RAN AND FAILED` → **`REFUSING TO LAUNCH`** |
| `664` — exactly what `git checkout-index` writes | **`==> LAUNCHED`** |

Same script, same case, same failing preflight.

### 3.2 What landed

**`cb686975`** — the gate no longer reads a missing mode bit as a clean bill. A
present-but-non-executable preflight is now **run through `bash`**; an **absent** one
gets its own third verdict:

```
PREFLIGHT NOT RUN: <path> is missing. The case was NOT checked; this is not a pass.
```

distinct from `REFUSING TO LAUNCH`, because *checked-and-bad* and *never-checked* are
different facts and printing neither of them is the fail-false. **All four branches
exercised** (executable+fails, 644+fails, absent, 644+passes).

*Deliberately not decided here:* whether an absent preflight should **refuse** rather
than warn. That is a chief's call, and three Ladder V agents hold live work in this
tree.

*L-46, what reads this change:* the only consumer of `launch_solve.sh`'s stdout is
`sdk/tests/test_lever_echo.py:800`, which asserts `REFUSING TO LAUNCH` is **absent**
for a clean fixture. Unaffected and verified green (69 passed).

**`0462b45b`** — the exec bit for `case_preflight.sh`, **split into its own commit
because the first one silently dropped it**. `core.filemode` is `false` in this repo,
so `git commit -- <path>` takes the working tree's content with **HEAD's mode**, and a
`git update-index --chmod=+x` sitting in the index is discarded. The index read
`100755` while the new tree read `100644` — the same index-versus-tree gap that hid
the original defect, one level up. Recorded rather than quietly re-committed.

**`73bb3836`** — the check itself: `sdk/chief_engineer/exec_bits.py` +
`sdk/tests/test_exec_bits.py`.

### 3.3 The check

Reads **`git ls-tree -r HEAD`** — not `os.access`, and **not the index either**. The
first draft read `git ls-files -s` and went green on a mode that was staged and never
committed; that near-miss is now its own regression test. *A clone materializes the
commit and nobody's index.*

Three findings, kept apart because they are three different facts:

| verdict | fires when |
|---|---|
| `missing_required` | a fresh clone cannot run something it must |
| `unregistered` | a **new** shebang-bearing tracked file with no bit and no waiver — **the ratchet** |
| `stale_waivers` | a waived path that has since gained its bit or been deleted — so the register can never quietly stop describing the tree |

**Every verdict is seen to FIRE before it is trusted**: 6 planted specimens in
throwaway repositories, plus **2 planted against the real tree with no git mutation at
all** — `scripts/self_audit.py` (100644 in HEAD) is reported by both the required
check and the ratchet when declared to them, and the audit returns to all-empty when
restored.

**Suite: 1,284 passed, 0 failed, 174 subtests**, of which 15 are this module's.

### 3.4 The frame, and why the number is not 29

**The dispatch's 29 is a subtree count.** Stated frames:

| frame | shebang-bearing tracked files | with an exec bit | without |
|---|---|---|---|
| `scripts/**` (the dispatch's frame) | 29 | 0 → **1 fixed tonight** | **29 → 28** |
| **whole repository** | **238** | **3** (all committed at `59b7e7ac`) → **4** | **235 → 234** |

**Until tonight, 3 of 238 shebang-bearing tracked files in this repository carried an
exec bit.** The exec bit is not *mostly* set here with 29 exceptions; it is
essentially never set, and `scripts/**` is where somebody looked. Both numbers are
stated because a count without its frame is not a count.

### 3.5 The 28 remaining under `scripts/**`, split by owner

**Not mass-changed.** Changing another family's files across a family boundary is
forbidden, and a 234-file mode sweep would land in a tree where three Ladder V agents
hold live work. The register carries an owner per path so a supervisor can route it
without re-deriving it.

| owner / function | n | files |
|---|---|---|
| **Infra — ops, keepalive, filming** | 7 | `session_keepalive.sh`, `filming_keepalive.sh`, `filming_mode.sh`, `auto-stop.sh.proposed`, `kill_worker.sh`, `demo_servers.sh`, `package_caches.sh` |
| **Infra — audit and report rails** | 7 | `self_audit.py`, `morning_report.py`, `contention_audit.py`, `cost_calibration.py`, `dispatch_queue.py`, `ledger_backup.py`, `add_proposals_r5.py` |
| **Demo / filming — shoot and bundle** | 6 | `audit_camera_discretion.sh`, `audit_transcripts.sh`, `verify_warm_replay.sh`, `build_laptop_bundle.py`, `laptop_bundle/replay_console.py`, `laptop_bundle/run-demo.sh` |
| **Cases — mesh and UQ tooling** | 5 | `ugrid_to_foam.py`, `coefficient_uq_plate.py`, `coefficient_uq_plate_analysis.py`, `memwatch.py`, `gate_table.py` |
| **Cases — convergence gates** | 3 | `check_convergence.py`, `check_convergence_sweep.py`, `check_convergence_validate.py` |
| **Infra — launcher chain** | ~~1~~ | ~~`case_preflight.sh`~~ — **FIXED at `0462b45b`**; it was load-bearing for a safety gate, not for convenience |

Repo-wide the 234 split: **DAFoam 107, Cases 59, Demo/website 26, Infra/Standards 42.**

### 3.6 A gap recorded as a gap, not as a constraint (L-48)

An attempt was made to **narrow** the rule from "every shebang script" to "the ones
actually invoked as a bare path", so the register would name only files that matter.
**That measurement is unreliable and is recorded as unreliable rather than as a
result.** Invocation goes through indirection — `"$PF" "$CASE"` in `launch_solve.sh`
and `[str(self.LAUNCHER), ...]` in `test_lever_echo.py:790` — so a literal-path search
**structurally cannot see the two call sites already known to exist**. Its null was
void.

`REQUIRED_EXECUTABLE` therefore stays conservative at four entries rather than
encoding a limit nobody measured. Recording what is missing is right; recording what
is impossible without measuring the impossibility is not.

---

## 4. For the chief — what is routed, and to whom

**Not fixed here, by design: no conclusion was rewritten, and nothing was fixed across
a family boundary.**

| # | item | owner | why it cannot wait |
|---|---|---|---|
| 1 | **FP-1** — `replay_monitor_rules.py`'s corpus glob. Amend `replay_s1_s6.json` **in place with a dated note**, re-run over 1,618 logs, and **withdraw or amend `MONITOR_STANDARD.md:785`** | Infra (this family) — **but the standard's conclusions are the chief's to withdraw** | It is a measurement instrument under six adopted rules; L-45 puts it above every other item |
| 2 | **D1** — monitor rules **S6/S8 unreachable in production**, unrecorded anywhere | Infra + chief | A rule that cannot fire is a rule the lab believes it has and does not |
| 3 | **D4** — `MONITOR_STANDARD.md:64-67`'s false universal, sourced to a superseded mesh | Infra + chief | Two conclusions. **The rule survives; only its warrant is defective** — the fix is a citation, not a retraction |
| 4 | **P5** — the arbitrary-code-execution scan opens when it fails | Infra (this family) | Highest consequence-per-line; one test |
| 5 | **FP-4/5** — the CRM-wingbody `VALIDATED` tier is minted from a last-`Time` line, an unconditional "none seen" string, and a **warm replay** | DAFoam / Cases — **routed, not touched** | A published tier with no measurement behind it |
| 6 | **L-47 relaxation** — three standing verdicts on one untested switch (F6b hills, R4 Ahmed ladder, 36 model-form records) | Cases + chief | **Costs one extra solve per arm. Priced, not spent — asking rather than spending** |
| 7 | **S10a `printInterval`** — every archived clip rate in this lab is a **floor** | Infra + Cases | L-40 in the observability dimension |
| 8 | **The 28 remaining exec bits**, by the split in 3.5 | four owners | Each owner's call; the ratchet stops the gap growing meanwhile |
| 9 | **FD-1** — DAFoam `printInfo` prints requested, not effective, KSP settings; the "requested ≡ effective on the shipped image" argument carrying the pre-08-10 corpus is an **argument, not an artifact** | DAFoam | Endorses that record's own recommendation |
| 10 | Three secondary record defects (1.6) and the face caveats in 1.5 | record owners | One-line corrections |

---

## 5. Explicitly skipped — stated, not silently truncated

1. **`PROOF.md` §1–24 hypothesis-ladder interior.** The 08-08 audit's own truncation;
   its other three are now closed, this one is not. ~2,400 lines.
2. **`S1_CBFS_WEIGHTED_ARM_RESULT.md`'s run tree** (`certonomous-runs/S1-cbfs-weighted-arm/`)
   was not opened. Its gate ledger is **unverified**. At 229–267 core-min of spend,
   **this is the single largest unaudited new record.**
3. **`DRAW_SCATTER_RETROFIT/` and `CUBE_SAIL_DRAW_SCATTER_PREREGISTRATION.md`** were
   screened as not lever-bearing on vocabulary count alone, **not read line by line**.
4. **The 08-08 audit's section-7 list**: 5 of ~25 files spot-checked; the other ~20 are
   inherited, not re-tested.
5. **Two 906 MB tarballs at `/home/ubuntu`** (`certonomous-cache.tar.gz`,
   `certonomous-git-backup-*.tar.gz`) were **not opened**. They could contain hump
   adjoint logs. A real gap in C1-A's reach.
6. **No whole-archive `.gz` sweep** — gz logs were read where records pointed at them.
   A gzipped log nobody cited is invisible.
7. **C2: 12 candidate instruments in `sdk/tests`** were read for contract, not audited
   as gates; `control_room.html`'s 28 verdict strings were judged display-only without
   tracing each to its producer; the `closure_eval_battery/` subtree beyond
   `build_master_table.py` was not swept.
8. **P6's 146-record `.done` corpus replay was NOT run**, and is named as the
   prerequisite for that change landing.
9. **The C2 sweep distinguishes firsthand from relayed findings.** Relayed without
   firsthand verification: `is_idle.sh`'s executable list, the `closure_*` gate
   internals, `self_audit.py`, `ledger_backup.py`'s metadata claims,
   `dispatch_queue.py`, `memwatch.py`, `demo_servers.sh`, `filming_keepalive.sh`, and
   `sensitivity.py`/`credibility.py`'s slack arithmetic. Each is quoted with a file and
   line and **should be re-checked before any of them is acted on.** FP-1 was
   re-verified firsthand by this supervisor before publication.
10. **C1-C's consolidated detail for FOUND-DEAD D3 and D5** is pending at the time of
    writing; the count of 6 and the ranking of D1/D4/D2 are established.

---

## 6. Commits from this pass

| hash | what |
|---|---|
| `cb686975` | the preflight gate stops reading a missing exec bit as a pass; adds the `PREFLIGHT NOT RUN` third verdict |
| `0462b45b` | the exec bit for `case_preflight.sh`, which `core.filemode=false` dropped from the commit that described it |
| `73bb3836` | `exec_bits.py` + `test_exec_bits.py` — the fresh-clone check, its ratchet, and the 234-path owner-routed register |

All single-step pathspec commits. **No bare `git commit` was issued**: three Ladder V
agents held live work in this tree throughout, and their commits (`92562841`,
`bbe0e4db`) interleave with these.
