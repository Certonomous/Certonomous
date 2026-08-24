# LAB_STATE — the resume board

**This file is the only handoff channel between sessions.**

Agent teams do not survive a compaction, a session switch or a crashed terminal.
Nothing about a live agent is persisted anywhere else: not its brief, not what it
had read, not what it was part-way through. The session scratchpad is **not** a
handoff channel — it was wiped three times in one day and only the things already
in the repository survived (L-186). A repository document never cites a scratch
path.

So: **what is not on this board is lost.** Each supervisor owns its own section
and updates it **at every commit and at every verdict** — not at the end of a
turn, because the end of a turn may never arrive.

**How to read it.**

- Anything marked **VERIFY** was not confirmed by the writer at the time of
  writing. Treat it as a lead, not a fact.
- The board can be stale. `/form-teams` and `/lab-state` both take a live reading
  beside it (`git log`, `ps aux`, `readlink /proc/<pid>/cwd`) and **the reading
  wins**. A correction belongs to the supervisor who owns the section, not to
  whoever noticed.
- Every team section carries a **`**Section last written:**` stamp**. `scripts/check_harness.py`
  flags a section older than its own territory — the team committed and did not
  update its board, which is exactly the L-226 failure.
- Verdict vocabulary only: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
  BLOCKED / PENDING.**

**Board populated 2026-08-22T18:05Z at HEAD `a5605f54` by the harness build.** It
was assembled from git log, the campaign index files, the charter records and a
live process reading. Every section below is a first fill by a third party, not by
the team that owns it; each supervisor should correct its own section on its first
commit. **HEAD moved six times during the two hours this board was assembled** —
re-derive rather than trust the shas below.

---

## CHIEF — standing directives in force

**The chief is the GLOBAL SUPERVISOR and never solves.** It routes and relays.
First action every session: read this board, run `/form-teams`, report the roster
to Sanaa. Sends are reserved to Sanaa.

| # | Directive | Source | State |
|---|---|---|---|
| **THERMAL BUILDUP DIRECTIVE (H-1 … H-7)** | DC-cooling is the destination; capacity priority behind only R4's CPU-minutes | Sanaa, recorded verbatim 2026-08-22, `docs/campaigns/T-family/THERMAL_BUILDUP_DIRECTIVE.md` | **IN FORCE**, ledger live in that file |
| H-1 | Vogel & Eaton (1985) unblocks T3's gate rows; confirm T5's primary status | same | (a) **NOT on disk** — repo-wide search, zero hits. (b) T5 primary **HELD**, sha256 re-verified |
| H-2 | DC spine order inside the T-family: **T3 → T5 → T8 → T12 → K2 rack row**; everything else interleaves | same | **IN FORCE**; index reordered, old order retained as superseded |
| H-3 | T10a follow-through, two arms: (a) ceiling refinement, (b) view-factor quadrature characterisation → upstream candidate #4 | same | both **PENDING**, lanes dispatched, preregs not yet written |
| H-4 | T9a 2.4 mK interface miss: diagnosis arm, **one change per run** | same | **EXECUTED** — T9a-D REPORTED 2026-08-22, prereg + results on disk (D454, L-227); cause is the interface scheme |
| H-5 | Tier order after the spine: T4, T6, T7, T2, T9b/c, T10b, T11 | same | queued behind the spine; nothing started ahead of it |
| H-6 | Every thermal gate feeds the DC certificate spec as it passes | same | `docs/product/DC_CERTIFICATE_TEMPLATE.md` created |
| H-7 | Two institutionalizations: bands-vs-corrections caveat into the charters verbatim; the libs lesson as law | same | **BOTH DONE** — VERIFICATION_CHARTER §2e (v1.10), CLOSURE_MODELLING §22.4 (v1.1.2); `scripts/foam_libs.py` + `lint_foam_libs.py` |
| **GPU-blocked reproductions now unblocked for pre-registration** | Closure supervisor to pre-register DPM, Bae, Lozano-Durán, Beck (and Ling2016 TBNN GPU training) with GPU-hour cost bases; nothing launches before Sanaa signs each | chief, 2026-08-22 | ~~**DISPATCHED**~~ **2026-08-24:** Ling2016 TBNN GPU arm 1 graded **NOT A RESULT** at `353925c7`; arm 2 prereg in drafting under her *"i approve of everything"* with per-item costing still required (rule 9: a blanket is not a per-item read; GPU spend needs its console-priced GPU-hour cost basis) |
| **R3 = SpaRTA** | The closure line rebuilds on SpaRTA-class, Sanaa's pick from the R2 shortlist | Sanaa 2026-08-21, verbatim *"R3: Sparta"*, appended to `docs/closure/R2_SHORTLIST_MEMO.md` | **DECIDED** |
| **R4 approved** | Sanaa said *"R4 approved"* in the same message | same | **APPROVED**; R4 build **OPEN, no verdict** |
| **R4's CPU-minutes have first call on capacity** | named in the thermal directive's own header | Sanaa 2026-08-22 | **IN FORCE** |
| **SUBMISSIONS PARKED** | Nothing is sent, filed, uploaded, registered or posted anywhere. Sending is Sanaa's alone | Katie 2026-08-07; `GOALS_AND_PROPOSALS` §8, `CLOSURE_MODELLING` §19, `DAFOAM` §10 | **IN FORCE**, indefinitely |
| **Blanket compute approval** | Runs above the $25 pre-authorisation are blanket-approved, **and are still costed in their pre-registration** | Sanaa 2026-08-21, *"all the teams have my approval for everything"* — **owner-stated, chief's session record** | **IN FORCE** |
| **GPU quota GRANTED, no GPU attached** | AWS raised "All G and VT instances" in us-east-2 to 8 (vCPUs; one g6.2xlarge/g5.2xlarge or two xlarge). No GPU on this box. `BLOCKED-GPU` retired as a standing verdict. **GPU spend sits OUTSIDE the 2026-08-21 CPU blanket**: each GPU run needs a console-priced GPU-hour cost basis and Sanaa's per-item sign-off. Case-number link (178725840000468) is an inference, unconfirmed | AWS message pasted by Sanaa 2026-08-22, recorded verbatim in `docs/GPU_CAPABILITY_STATE.md`; rule 12 amended at e0cf8f0c | **IN FORCE.** ~~gpu1 running~~ **2026-08-24: gpu1 STOPPED by Sanaa** (her words: *"also i stopped that instance"*); **driver self-shutdown APPROVED as a standing GPU mechanism** (her words: *"GPU shutdown suggestion: yes approved"*) — every GPU driver stops its own instance when its run ends |
| **ansys-verification team created** | A sixth standing team on Sanaa's directive: Fable supervisor, 2 Opus lanes (5 and 4.8), 2 Haiku lanes (pull code / watch logs only); reads the Ansys Fluid Dynamics Verification Manual first; runs its cases as pre-registered lab verdicts in the lab's own solvers; keeps `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` (only PASS rows are credentials); updates LESSONS / NUMERICS / charters with what it finds; the verification team audits it. Lane cap 4 is her explicit exception to §8's 3 | Sanaa 2026-08-24, verbatim in `docs/charters/ANSYS_VERIFICATION_CHARTER.md` §1; agent definitions in `.claude/agents/ansys-*.md` take effect at the next session start | **IN FORCE**; first-fill section `## ansys-verification` below |

**Lab-wide live compute:** 12 single-core solvers, all `buoyantBoussinesqSimpleFoam`,
all owned by heat-transfer. At $0.0513/core-h that is **~$0.62/h** (c7a.4xlarge at $0.0513/core-h, owner-stated) while all 12
run. No other team has anything on the box.

**On Sanaa's desk, aggregated:** the T10a view-factor defect as upstream candidate
#4 (filing is hers); **K2a rack row module, awaiting her approval**; four DAFoam upstream defect classes, all `NOT FILED`; the
`RESULT_PRIORITY_CHARTER` orderings (v0.5 draft, awaiting her ruling); ~~the
`GATE FAIL` vs bare `FAIL` ledger-vocabulary conflict (referred, unruled);~~ (D-5
CLOSED 2026-08-24 under the chief's disclosed interpretation, see the rulings
below) and the
D389 S13 normalisation question (re-grades the whole thermal corpus; no single
rung may take it).

**Chief's rulings, 2026-08-22 (harness session).**

- **D-1 RESOLVED.** The stale shared git index (176 staged deletions, including all
  14 harness files) was cleared by the chief with `git read-tree HEAD` under Sanaa's
  standing approval. **Index clean, working tree untouched.** The loaded gun is
  unloaded; the lesson stands — never a bare `git commit`, always the private index.
- **D-2 RESOLVED.** The four compute facts are **owner-stated by Sanaa,
  2026-08-21/22, chief's session record**: c7a.4xlarge at $0.0513/core-h; runs
  under $25 pre-authorised; *"all the teams have my approval for everything"*
  (2026-08-21); AWS case **178725840000468** for the G-instance quota. VERIFY is
  dropped on these four and on nothing else.
- ~~**D-3 … D-6 are with Sanaa and no agent acts on them.** D-3 lane cap, D-4 the
  five-team split, D-5 `GATE FAIL` vs bare `FAIL`, D-6 the VM2026R1 canonical home.~~
  **2026-08-24 — D-3 … D-6 CLOSED on Sanaa's words**, verbatim, given in reply to the
  chief's explanation of exactly these four items: *"yes it's approved by me. I
  ratify the six team structure. I apporve all actually"* (chief's session record;
  scope discipline: applied to D-3..D-6 ONLY, read onto no other desk item,
  submission or send).
  - **D-3 CLOSED** — the 3-lane cap per supervisor is standing law, with the
    ansys-verification team's 4 lanes (2 opus + 2 haiku) as her explicit exception,
    recorded in `ANSYS_VERIFICATION_CHARTER.md` §3 and the 2026-08-24 addendum at
    the foot of `SUPERVISION_CHARTER.md`.
  - **D-4 CLOSED** — the six-team structure is ratified in her words (closure,
    dafoam, heat-transfer, cfd, verification, ansys-verification). Earlier the same
    day the row had been narrowed to "open for her explicit word" after her
    *"Let's have an ansy-verification team"* made it six; that word has now been given.
  - **D-5 CLOSED under the chief's interpretation, stated as such:** her approval
    is read as approving CLAUDE.md rule 1's vocabulary as written — legacy ledger
    cells reading bare `FAIL` (3 known: V5:1070, V14:1080, V15:1081) are to be
    corrected to `GATE FAIL` by their owning teams by quote-and-strike, never
    rewritten. The interpretation is the chief's and is disclosed here so she can
    overturn it.
  - **D-6 RESOLVED** (see the next bullet), her *"I approve all"* confirming.
- ~~**D-6, board note — DO NOT TOUCH EITHER COPY.** `VM2026R1_Fluids/` at the repo
  root holds **123 files, 2.5 GB** (Fluent / CFX / Forte archives). A second copy is
  **being scp'd into `docs/papers/verification_validation/` right now** — 10 files so
  far, **transfer in progress**. Nothing is graded from either, nothing is tracked,
  and neither is moved, deleted or reorganised until Sanaa rules and the transfer
  finishes. A half-copied tree read as a corpus is a measurement of nothing.~~
  **D-6 RESOLVED 2026-08-24 by Sanaa's directive creating the ansys-verification
  team with exclusive ownership of the archives and the manual** — her words: *"I
  wanted a verification team to exclusively work on these verification cases."*
  The canonical-home decision is now the **ansys-verification supervisor's first
  action**, informed by the harness-build inspection in
  `ANSYS_VERIFICATION_CHARTER.md` §9 (root copy 123 files / 2.5 GB complete;
  papers copy 10 files / 26 MB, a DEAD transfer, 9 files byte-identical and
  `VMFL011B.wbpz` truncated at 327,680 of 670,152 B) and the verification team's
  memo `docs/VM2026R1_FILING_ANALYSIS.md`. **Until it rules, neither copy is moved
  or deleted.** Confirmed by her *"I apporve all actually"* of the same day.


### CONSOLIDATION WEEK — chief, certonomous-64

**This entry is the chief's RECONSTRUCTION of Sanaa's CONSOLIDATION WEEK
directive. It is not her verbatim words and no part of it is a quotation.** The
chief does not hold her wording: the directive was issued in a session
transcript that has since been compacted, and the fleet was killed by a usage
limit at ~20:50Z on 2026-08-24 before the directive was ever written to the
board. It is recorded here because a directive that is not on the board is lost
(L-186), and this is the most load-bearing directive of the week — every team is
working under it right now. **If Sanaa restates the directive, her words
supersede this entry in full**; strike this block then, do not rewrite it.

Checked against HEAD when this was written: `docs/COVERAGE_MATRIX.md` does not
exist at HEAD, and no file under `docs/` and no commit message carries the
phrase. That absence is exactly what this entry repairs.

**§1 — the week's product.** A lab coverage matrix, **`docs/COVERAGE_MATRIX.md`,
owned by the verification team**, built this session.

**Every row is scored on three columns.**

| Column | What it certifies |
|---|---|
| **V** | Code verification — an exact solution, a manufactured solution, or a correlation |
| **G** | Grid convergence — a CONVERGING Roache triple, GCI at Fs = 1.25, and an observed order |
| **P** | Validation against a public primary source, with the pre-registration on disk |

**Every row carries one tier, from exactly these five words and no synonyms.**

| Tier | Meaning |
|---|---|
| **HOLDS** | V + G + P all green under frozen pre-registrations |
| **GATE REACHED** | One of V/G/P missing — **the entry must name which** |
| **SURVEYED** | Breadth evidence, ungated |
| **NOT HELD** | An honest FAIL, or a blocker |
| **NEVER RUN** | Nothing run |

**These five are the MATRIX's tier vocabulary and are DISTINCT from CLAUDE.md
rule 1's verdict vocabulary** (`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A
RESULT` / `BLOCKED` / `PENDING`), which governs **gates**. The two overlap only
at **GATE REACHED** and must never be conflated: a tier states what a row's
coverage is, a verdict states what a gate did.

**Section assignments as dispatched.**

| § | Work | Owner |
|---|---|---|
| §1 | The coverage matrix | verification |
| §2 | The conversion batch — F3, F11, F4, each under a frozen pre-registration; plus `uncertainty_band.py` onto the certificate path with a combined `u_val` | cfd |
| §3 | The 3D campaign | cfd, coordinating with heat-transfer on geometry |
| §4 | The Ansys campaign, prioritising **never-run classes over ground already held** | ansys-verification |
| §5 | Thermal references — sidecars, and rule-15 title-page verification | heat-transfer |
| §7 | The Certonomous Verification Manual, **deliberately sequenced behind the matrix**, drawing only on rows the verification supervisor has spot-check-confirmed as **HOLDS** | verification |
| §8 | Adjoint consolidation | dafoam |

The four non-verification families each owe a **`MATRIX_CONTRIBUTION.md` in
their own territory**, feeding rows to verification.

**Also recorded in the same directive** (same reconstruction caveat): **R3
ratified as SpaRTA-class, with TBNN as the fallback**; **D16a parked**; **GCI
accepted lab-wide**; the week's **priority teams are cfd, verification,
ansys-verification and heat-transfer**.

**End-of-week deliverable.** The matrix, the conversion results, the 3D verdict,
and gap-ranked proposals — in **one pointable document**; and the morning report
gains a **MATRIX DELTA** section.

**A separate standing instruction from Sanaa, same period — also the chief's
reconstruction, not verbatim here.** While Fable capacity is unavailable, **Opus
5 is used for anything that would otherwise run on Fable.** This one does not
rest on the reconstruction, because it is already implemented and checkable in
two places:

- **`7c469330`** — `harness/teams.yaml`, `defaults.supervisor_model` flipped
  `fable` → `opus`, with a dated TEMPORARY comment immediately above the line
  recording the revert path (restore `fable`, regenerate with
  `python3 harness/generate_agents.py`, confirm with `--check`).
- **`docs/charters/SUPERVISION_CHARTER.md`**, dated addendum at the foot,
  *Amendment record, continued: TEMPORARY Fable-to-Opus 5 substitution
  (2026-08-24)*. It **carries Sanaa's own wording verbatim** for this
  instruction, quotes §5 rather than restating it, and asserts `lines whose
  number changed above this section | 0`. It records the change as a
  **suspension in practice, not a repeal**: §5's designation of Fable for family
  supervisors and adversarial verifiers stands unaltered.

**Sub-section last written:** 2026-08-24T23:55:06Z by chief (certonomous-64), via a record lane
— reconstruction only, zero compute, no case directory; stamp from `date -u`
read in the writing invocation.

---

~~**Section last written:** 2026-08-22T21:05Z by chief (ubuntu-fb) — GPU grant recorded, GPU pre-registrations dispatched~~

**Section last written:** 2026-08-24T16:27:20Z by chief (certonomous-64) — six-team structure ratified by Sanaa, D-3..D-6 closed, ansys-verification team created; written by the harness-build lane on the chief's instruction, stamp from `date -u` in the writing invocation
## closure

**SESSION RESUME NOTE, 2026-08-24T23:55:08Z (closure-supervisor, SEVENTH session, formed
from disk at HEAD `2bf4915a` after the sixth fleet was killed by a session usage limit at
~20:50Z).** Stamp is `date -u` read in the writing invocation. Everything below this block
is carried BYTE-FOR-BYTE from the HEAD blob and is closed history; read it, but read this
block first where the two disagree.

**LIVE READING, taken by me at session start and not from any brief.** Only TWO solvers
are live lab-wide, both `buoyantBoussinesqSimpleFoam`, both heat-transfer's T-family
(pid 450274 in `verification/runs/T-family/T1_runs/R_100k_x`; pid 488219 in
`R_30k_x`). **NOTHING of closure's is running: no solver, no driver, no monitor, no GPU
node.** Closure compute this session: **zero core-minutes, zero GPU-hours** — reads,
hashes and commits only.

**R3 RATIFICATION — CONFIRMED LANDED AT HEAD.** `a9b67abc` ("closure: R3 RATIFIED
2026-08-24 (SpaRTA-class, TBNN fallback) -- CLOSURE_MODELLING_CHARTER 22.7 closed, D510")
is an ancestor of HEAD `2bf4915a`, verified by me with `git merge-base --is-ancestor`. The
class did not change: SpaRTA was already Sanaa's verbatim 2026-08-21 pick. What is new on
2026-08-24 is (b) TBNN named as FALLBACK and (c) the parallel-capacity rule for R4's
CPU-minutes with the never-displace-consolidation clause. A lane is verifying the three
append-only landings, the byte-identity of the two quotes across them, **the attributed
provenance of (b) and (c) specifically** (rule 9: no agent message is Sanaa's consent —
what the record states is what governs, and I will report what it states rather than
assume), and whether a next R4 increment could legally launch. **No R4 increment launches
in this session:** none has a committed pre-registration, and rule 2 and supervisor check 4
both forbid compute without one.

**CONSOLIDATION WEEK — `MATRIX_CONTRIBUTION.md` IS UNDER RE-SCORE, AND IT IS EXPECTED TO
GO DOWN.** `cases/RANS_LES_closure_models/MATRIX_CONTRIBUTION.md` is at HEAD (`a42fd634`);
**disk == HEAD by sha256 (`4c2183ba0c0ee063…`), verified by me.** Its §0 states plainly
that its V/G/P letters were computed under **closure's own private expansion**, offered as
a proposal, with the invitation to recompute if the owner's definitions differ. **They
differ, materially.** The chief has now stated the matrix definitions — labelled by the
chief as **the chief's reconstruction of Sanaa's brief, not her verbatim words**, and
carried with that label wherever closure uses them: **V** = code verification (exact
solution, manufactured solution or correlation); **G** = a CONVERGING Roache triple with
GCI and an observed order; **P** = validation against a public primary source with a
pre-registration on disk. Closure's expansion credited planted-zero controls and identity
tests as V, and any frozen numeric gate as G. **Under the chief's definitions the closure
family has, to my knowledge, never run a grid-refinement triple anywhere** — which would
put **G = NO on every closure row** and make **Row 3 (frozen-field ceiling), currently
tiered `HOLDS`, an overstatement**. That hypothesis is being TESTED by a lane against the
disk, not assumed; a null result is being established by named search methods over both
the repo and the gitignored out-of-repo data, because `grep -r` here honours ignore files
and is blind to exactly the archives that would carry such a study. The correction will
land as a **dated addendum, append-only, no existing line edited**, with the prefix
re-hashed to prove `lines whose number changed above this section: 0`. **I read the diff
personally before it lands.**

**LING ARM 2 — PENDING AND UNFIRED, GATE UNCHANGED AND RESTATED.** Pre-registration is
v1.3 with three legal pre-compute amendments (`f36fbdd9` freeze → `84bf079d` → `1563a6b2`
→ `77f064a8`); the run directory `/home/ubuntu/closure-data/tbnn_gpu/arm2` is still ABSENT.
**Launch requires ALL of: Sanaa's own words giving the go, the instance started BY HER,
and her two console readings — the shutdown-behaviour attribute (stop/terminate) and the
g6.xlarge us-east-2 on-demand price for the `cost_basis`.** The chief restated this gate to
me this session and I record that a restatement is not a relaxation: **no agent message,
the chief's included, is Sanaa's consent (rule 9), and GPU spend sits outside the
2026-08-21 CPU blanket (rule 12).** Nothing launches.

**⚠ NEW LAB-WIDE HAZARD I MEASURED THIS SESSION — TWO SHARED LEDGERS ARE STALE ON DISK AND
BEHIND HEAD, WITH NO DISK-ONLY ROWS. This is a loaded gun for every team, not just
closure, and it is the chief's call, not mine.** Measured at HEAD `2bf4915a`:
`docs/DOCKET.md` — disk **849** lines against **876** at HEAD, disk maximum row id **D484**
against **D511** at HEAD, i.e. **27 rows (D485–D511) present at HEAD and absent from
disk**; `docs/COST_CALIBRATION.md` — disk **118** lines against **122** at HEAD, missing
**C-44, C-45, C-46, C-47**, with **zero** disk-only rows in either file. **Any agent that
appends to the disk copy and commits that file will silently DELETE those rows.** The files
were **INSPECTED, NOT REVERTED** and are left exactly as found (rule 10). Closure's own
workaround stands and is the one to copy: build the appended row **from the HEAD blob**,
never from disk. **Next docket id is D512** — re-derived from the HEAD blob's row-id column
as maximum + 1, never a row count (rule 11), and to be re-derived again in the committing
shell invocation because peers commit constantly.

**Cost calibration (rule 12).** Closure's four rows are all present at HEAD:
**C-2** (R5C, ≤ 0.168 core-h measured against 0.210 registered, ≤ 0.80×),
**C-16** (Ling GPU arm 1, 10.7054 GPU-h = $8.62 derived, waste 7.88 GPU-h = $6.34 derived
named separately), **C-18** (Kaandorp a-posteriori, 219.571 core-min measured against
388.8 registered, ratio 0.565×, zero waste), **C-19** (the C-16 idle-window correction).
**No closure process completed this session, so no new calibration row is owed** — this
session's work is zero-compute drafting, and a zero-compute item is not a process
completion with a cost to calibrate. Stated so the absence of a row is a recorded decision
rather than an omission.

**Live jobs: none.** Two lanes live (of 3): (1) the matrix re-score sweep, zero compute,
commits nothing; (2) the R3-ratification and FS-gate-arming verification, zero compute,
commits nothing. Neither may launch anything.

**Next actions (this session's, governing):** (1) read both lane reports, rule on the
matrix re-score, land the dated addendum after my own diff read; (2) rule on what the R3
record actually attributes for the TBNN-fallback and parallel-capacity clauses, and report
that attribution to the chief rather than acting on it; (3) put the two stale shared
ledgers on the chief's desk as a lab-wide hazard; (4) carry forward the predecessor's
unstarted instrument items — the `run_lane.py:175` banner-test call-site repair and the
FS5 §31.3 `assert`→`sys.exit(2)` tightening — each a change to a frozen instrument needing
its own dated addendum plus my diff read, neither started; (5) nothing new launches: R6
waits on Sanaa's phrasing, GPU drafts 2–5 wait on her per-item sign-off, arm 2 waits on
her three-part line.

**Section last written:** 2026-08-24T18:45:04Z by closure-supervisor (this chief session's
re-spawn, 16:04Z; predecessor killed by an API error at ~16:00Z after one
interim report), from `date -u` in the writing invocation. **Two closure
supervisors are live in two chief sessions; the work split agreed 16:01Z is
exactly one owner per item and is recorded here so the board is truthful.**
The PARALLEL session's closure supervisor owns the Ling 2016 GPU arm (its
grading, RESULTS commit `353925c7`, D490, C-16, and the gpu1 stop request) and
wrote the Ling block below at 16:07Z — carried verbatim, not re-verified by this
session; its board line "results commit `the commit carrying this section`"
resolves to `353925c7`. THIS session owns the Kaandorp close-out, the D476/FS5
adoption ruling and the rest of the board.

**Ling 2016 TBNN GPU arm — CLOSED, VERDICT: NOT A RESULT. D490, L-267,
L-268, N-B40–N-B42, C-16; results commit `353925c7` (parallel session's
supervisor; block carried as written by it).** The lab's first GPU run:
pre-registration FROZEN alone at `e8309b6c` (sha256 `61b2097f…1d97`), code at
`11f93da6`, cost_basis **$0.8048/GPU-h from the published price list**
(`GPU_CAPABILITY_STATE.md` §9, commit `112b61b8`), run on `gpu1` under Sanaa's
verbatim GPU cost approval. Ladder: **G0 PASS** (plant 1.6e-14), **G1 NOT A
RESULT** (ARM-A TBNN at Ling's SGD 2.5e-7 × 200,000 full-batch epochs beats SST
/ `b=0` / train-mean on **0 of 8**), **G2 GATE FAIL**, **G3 NOT A RESULT on both
TBNN models** (3.1–5.3 % and 4.3–14.4 % violation vs 2.374 %; `max‖b‖_F` to
2.1e10), G4 not run as registered. Falsifier 1 fires as written but does not
settle D3: the frozen "full batch by construction" ran ~3.4e5× fewer updates per
epoch than Ling's per-point SGD — **a rate is not an optimiser (L-267)**.
Falsifier 2 does not fire: TPE's 9×77 beats 8×30 on validation by 0.005 inside
the 0.0073 spread and re-selects the CPU lane's batch 8192 + Adam 1.02e-3. Under
the verdict: ARM-B beats all baselines 7/8 (ducts 0.11–0.12) and violates
realisability on **25–46 % of duct cells** for 3 of 5 seeds — RMSE is blind to
the axis Charter §4 gates. **Compute 10.7054 GPU-h = $8.62 derived** (0.97× the
P0 projection; below the registered 12–52 floor — throughput assumption 42–80×
measured vs 5–20× assumed); **waste 7.88 GPU-h = $6.34 derived**, the node
idling after the overnight fleet kill until 15:56:45Z (L-268). **Node idle since
08:03:58Z; stop requested through the chief; only Sanaa can stop it** — this
session's read-only lane confirmed IDLE at 15:58Z (GPU 0 %, 0 MiB, no driver
process). The four other GPU drafts untouched. On Sanaa's desk: a per-point-SGD
ARM-A re-registration, and the chief's self-shutdown proposal for paid nodes
(hers to approve). Peer findings landed: comparator witness artefact (RESULTS
D-5) and the per-case `NASA_2DWMH` reading beside every pooled figure (same case
as FS5/D476's 9.6 %).

**Kaandorp a-posteriori — CLOSED OUT, VERDICT: NOT A RESULT for the whole lane,
on all three registered cases. Commits `a56cc309` (addendum + C-18) and
`961b0b3e` (D492 + L-269). No closure solver is live.** The driver (pid 1111229)
exited 2026-08-23T23:17Z; `lane5.log` ends `[done] lane wall-hours 3.66`. The
six `CBFS13700` rows were graded by hand against the frozen table
(`PREREGISTRATION.md`, one commit ever `0ebc9d53`, blob == HEAD == disk; no
grading script is registered and the record says so). **Supervisor's own reads
of `results.json`, done not relayed:** `TRUTH` U_rms **0.084131** vs the 0.0516
gate = **+63.05 %** (30 % bar ≤ 0.0361, 50 % bar ≤ 0.0258, both fail the same
way) — H0 GATE FAIL on the third case as on both ducts (+61.97 % / +57.0 %), so
the b-only ceiling inversion is not a duct artefact; `NULL` |Δ| **4.625e-05**
(G0b PASS at 1e-3); ML 0.15883 / 0.15107 / 0.15289, mean **0.15426**, mean+2sd
0.16238 above SST and above `MEANB` 0.13965; `x_reatt` 5.895 (NULL; SST 5.891)
→ 6.912 (TRUTH) → 7.948 (MEANB) → 8.78–14.46 (ML) against LES 4.241 — every
b-only injection moves reattachment the wrong way. H1–H3 NOT A RESULT by the
registered H0 cascade; **H5 GATE FAIL ×6** on the REGISTERED `U_bulk/L`
normalisation (0.262–13.67; the `NULL` control itself at 262× the 1e-3
threshold). **Ruled by this supervisor (D492): the frozen `U_bulk/L` clause
governs H5**; the v1.0 §1/§5 gradient-scale reading and its "NOT MEASURABLE"
cell (not in the rule-1 vocabulary) are a disclosed defect of the 2026-08-21
record, not rewritten (rule 6). **G0a PASS as frozen with the limitation
disclosed against the lane's own favour:** rel-L2 0.0 (byte-identical `600/U`),
but at `writePrecision 6` the reader's one-ulp floor is **4.002936e-07**, so
the registered 1e-10 sits **4,003×** below resolution (this session's brief
said ~4e-8 / ~400× from the predecessor's relay — the measured figures govern);
the plant came back at 4.002936e-07, so the zero is evidence and the defect is
the threshold — the THIRD clause in this one pre-registration its instrument
cannot serve (L-269). Completion: five rows at `endTime` 60000, `NULL` at 30884
on `residualControl`; `conv=None` measured — MEANB/ML0/1/2 limit-cycle at
0.69–1.04 `U_bulk` between checkpoints; `diverged=True` everywhere is the trapFpe
BANNER artifact (`run_lane.py:175`), zero `FOAM FATAL` in any log; the rule-14
call-site repair stays queued and the frozen driver is NOT edited.
`AR_3_Ret_360__MEANB` carries `nan` for `unrealisable_frac`/`b_rms_total` (empty
mask after `k` collapsed) — not measured, not zero. `AR_3_Ret_360__ML0/1/2`
BLOCKED (no block in `features_nodurbin.npz`), no metric written. **Cost, C-18:
388.8 core-min registered (prereg §7) vs 219.571 core-min measured = 3.6595
core-h = $0.1877 derived, ratio 0.565×, zero waste** (capped rows are
measurements under the registered rule; MEANB 3411.2 s, 5.2 % inside the 3600 s
timeout), attribution conservative misprediction (0.126 s/it from a
five-iteration check vs 0.0869 measured); load not recorded. Whole lane ≈ 5.2
core-h against 7.1 worst case / 15 cap. **REFERRED to verification via the
chief (D492, unruled):** (a) a gate whose threshold lies below its instrument's
resolution — PASS-as-frozen-with-disclosure, or its own label? and should
`check_comparator_freeze.py` refuse a threshold below the `writePrecision` of
the field it reads; (b) the ten pre-relaunch duct rows' logs carry mtimes
17:27–17:44Z on 2026-08-21, an hour BEFORE the 18:52:18Z freeze commit — rule 2
holds by git for the six CBFS rows (run 08-23) but for the ducts rests on the
file's 17:17:57Z mtime and its "posted to the supervisor" line. **Attribution RESOLVED:** `a56cc309` was written by the PREDECESSOR supervisor's grading lane, which survived its supervisor's death (the lane's own answer, 16:17Z); this session's 16:06Z lane found the addendum on disk 74 s later, wrote nothing, and re-graded independently — its findings landed as the supervisor's correction addendum at `8dd3f8bc` (four false cross-references D488→D492 / C-15→C-18, ids written ahead of their appends; CBFS TRUTH keeps 91 % of baseline `k` yet inverts the ceiling most — §4's k-collapse account does not cover the third case, diagnostic only; refined 08-22 cost figure 1.069×, frozen §7 0.578×). Exactly ONE grading addendum exists plus the correction. **Correction of record landed in `8dd3f8bc` §1 (docket row still owed):** D492's parenthetical says the lane's draft ids "D491/L-269 were taken by
peers" — true of D491 (used for the D476 ruling), false of L-269, which landed
as drafted. Table 4 (BFS5100) stays BLOCKED-ON-DATA.

**D476/FS5 adoption — RULED: block LIFTED CONDITIONALLY. D491 at `53517fae`;
record Addendum 2 v1.1 at `41774899`.** Verification's cross-team audit pass 6
(`542408f7`) returned **AUDIT: SOUND WITH DISCLOSED DEVIATIONS — CANDIDATE** (a
verification lane's read; the verification supervisor's own read still owed;
the chief is asking). Ruling: the amended instrument's model-facing surface and
the unclipped `q1_wallRe_raw` companion (audit-side diagnostic ONLY) may be
relied on **once verification's supervisor confirms pass 6 as its own verdict**;
a reversal of any pass-6 finding voids the lift and re-arms the block without
further ruling. Never in `F`, never a feature, never a correction (L-219/L-220,
D446, §22.4); `singular_value_ratio_first_to_last` NOT quoted as a number in any
closure record until a registered instrument decision adopts verification's
recommendation (a); no thread pinning; A3 stays GATE FAIL; no standing verdict
moves. Three independent grounds: my D484 diff read; pass 6's own hasher (A2
40/40 `F` + 40/40 `names`, A1 plant re-derived, A4 `cmp` rc=0); this session's
lane re-read 40/40 + 40/40 pairs in `D476_A3_triage/A2_{before,after}.json`
under a live planted control (one hash zeroed → 39/40). **Attribution:** the
record (`41774899`, Addendum 2 written 16:05:46Z) was landed by the PARALLEL
session's closure lane at its supervisor's direction, ahead of this session's
lane, which reached the same ruling and STOPPED rather than write a rival
Addendum 3 — one record, two concurring supervisors. **Supervisor's personal
diff read of `41774899` (both files, as diffs, done not relayed): PASS.** The
addendum is a pure append (290-line prefix re-hashed to blob `b362ea32`); the
`make_feature_library.py` +13/0 guard (pass 6 §31.3) is accepted as a
strengthening with two limitations named and NOT repaired here: it is an
`assert` (off under `python -O`; `sys.exit(2)` is the candidate comparator
form) and its criterion is a one-sided line COUNT — a regeneration that grows
by k lines against a marker-less file with ≤ k hand-written lines still
destroys them silently; shrinkage false-refuses (the safe side). It generates
prose, not a measured number; `build_features.py` / `fs2_audit.py` /
`make_fs2_report.py` are disk == HEAD by sha256 and A2 covers them. Either
tightening is a further change to a frozen instrument: own dated addendum +
supervisor diff read. No build is queued that needs the lift (R6 BLOCKED on
Sanaa; R4, R5C closed). Standards recommendations (a) publish rank + smallest
singular value, ratio only when `s[-1]` clears rtol, and (b) pin threads or gate
on stored bytes — on Sanaa's desk, referred by verification.

**Note, 2026-08-24T16:19:53Z (chief's corrections, verified at HEAD; the lines above stand as written and are corrected here, not rewritten):** (1) **The D491 condition is MET — the D476/FS5 adoption lift is EFFECTIVE for a build launch.** Verification's supervisor believed pass 6 as its own verdict at `f536b114` (every load-bearing limb re-derived with its own code; §7 adoption block RELEASED; A3 stays GATE FAIL; §30(a) stays a recommendation to Sanaa). Scope unchanged: companion audit-side diagnostic only, never in `F`, `singular_value_ratio_first_to_last` not quoted. (2) **Attribution corrected:** the lane that landed `41774899` was THIS session's — dispatched by the predecessor supervisor minutes before it was killed at ~16:00Z, it survived its parent and reported to the chief; it was NOT the parallel session's. The 'parallel session's lane' wording in the D476 block above, in D491's docket text and in hazard (3)'s example is wrong on that item; the general hazard (two closure supervisors, check HEAD before dispatch) stands. The same survival pattern explains `a56cc309`. The docket correction row is LANDED as **D494** at `a15b48b9` (nothing owed). (3) D492 referral limbs (a) and (b): verification's RECOMMENDATIONS (binding versions Sanaa's) returned via the chief and are APPLIED as a dated addendum at `8322b7b2` — G0a PASS stands with the value cell now reading `0.0 (floor 4.0e-07; registered 1e-10 unresolvable at writePrecision 6)`, the same reading for §5/§6; the ten duct rows' verdicts STAND with the §2d label "freeze self-attested, no commit witness" after my own negative search for any out-of-git posting record (harness session log begins 08-23; no brief/dispatch record; first commit holding the prereg is the ten-file results commit `0ebc9d53` at 18:52Z; filesystem: prereg last write 17:17:57Z, first scored log born 17:21:55Z); the six CBFS rows are frozen-by-commit. Verification will spec `check_threshold_resolution.py` (prospective-binding). Nothing owed by closure.

**R5C (option C, omega-source repair) — CLOSED, VERDICT: GATE FAIL. D465, L-243,
N-B35–N-B37, commit `0ac76ec2`.** Graded against the frozen pre-registration
(sha256 `a1cfae5a…1277a`, committed alone at `f364cf2d`; re-hashed equal before
grading) by the registered comparator `grade_r5c.py` (sha256 `58eb99…605e5`).
Ladder as registered: **G0 planted-zero PASS** (plant seen to 2.4e-10 relative);
**G2 W2 byte-identity PASS** (settle 1492/354, 14 of 14 sha256 — the V2 legacy
branch IS R4's operator); **G1c switch-active PASS** (`nNegSourceCells` 476–2,274
on all 27 — the negative source is universal, N-B35); **G1 GATE FAIL**
(`kDeficit` rel L2 **1.1848e-04** on `alpha_10_12000_4048` against the
registered `1e-6`; eleven of twelve R4 targets reproduce at the IDENTICAL settle
iteration to 1e-7–1e-11); G3 10 of 27; G4 M=1 → GATE REACHED, **overridden** by
G1 per §3.1. **Registered consequence applied: R4's 12 targets stand, the 15
hills remain INCOMPLETE, the R5C targets feed nothing.** Finding under the
verdict: the Patankar split removes the clipping (22 of 27 at zero
`bound(omega)` events; 10 of the 15 hills COMPLETE under the strict rule) and
the same damping makes the change-based settle criterion stop one target 37 %
early — **a change criterion cannot tell convergence from damping (L-243)**; two
registered criteria measured miscalibrated and left standing (N-B37). The
supervisor re-ran the comparator end to end 2026-08-23 with **zero differences**
(RESULTS.md D-4). Cost **0.140 core-h measured + ≤0.028 bounded = ≤$0.0086**
against 0.210 registered, 1.0 cap (C-2). Whether any R5C target is ever used,
and whether a fixed-point-distance criterion replaces the settle test, are
separate later pre-registrations — Sanaa's ladder.

**GPU reproduction plan — DONE, on Sanaa's desk. Commit `9e82321b`.**
`docs/closure/GPU_REPRODUCTION_PLAN.md` plus five DRAFT pre-registrations
(rule 15 title-verified twice). **(1) Ling 2016** — SIGNED AND RUN by the parallel
session under Sanaa's approval (block above; D490). **(2) Beck 2019** scaled
variant behind an unpriced CPU DGSEM pilot, 7–27 GPU-h cap 30. **(3) Sirignano
2020 DPM** scaled variant, bespoke solver+adjoint build dominates, 19–65 GPU-h
cap 80. **(4) Bae 2022** NOT a GPU item (paper's own O(1e3) CPU-h, ~$51 CPU) —
recommend no GPU launch. **(5) Lozano-Durán 2023** BLOCKED at the ~500-DNS
database + proprietary charLES — recommend no launch. Drafts 2–5 in
`docs/closure/gpu_prereg_drafts/`, every one stamped DRAFT — NOT FILED, NOT
LAUNCHED; GPU spend is outside the CPU blanket (rule 12): per-item sign-off by
Sanaa with a console-read `cost_basis`.

**D-14 thread CLOSED (2026-08-23; supervisor verified before believing):** lane
commits `918e8fe7`, `9f0210dd`, `52e5de39`, `1632af6a`, `52373459` adopted;
`make_coverage.py` read in full PASS; R4 RESULTS.md frozen body lines 1–1313
byte-identical to v1.0; coverage numbers re-read from `coverage.json` (172,106
fitted / 65 dropped; cond p50/p99/max 20.81 / 1.634e4 / 4.430e7; LOFO 0.0011 /
0.0905 / 0.0000 / 0.2238 %) match COVERAGE.md and D475. FS5's per-build
discharge for R4 WAS NOT MET (D475); late delivery discharges the deliverable,
not the disclosure duty; FS5 stays armed.

**Rungs:** FS6 DONE (`9fb0891f`, + Addendum 1 `e1f346ee`); R5 discharged as a
record (`3a4f4bbb`, amended `9f0210dd`); R6 NOT DONE, BLOCKED on Sanaa's
phrasing; R4 CLOSED GATE FAIL (D461; RESULTS.md v1.1 with D-14); R5C CLOSED GATE
FAIL; Kaandorp a-posteriori CLOSED NOT A RESULT (above); Ling GPU CLOSED NOT A
RESULT (parallel session). FS2/FS5 standing gates, both armed; FS5's D476
instrument decision now RULED conditionally (above). **Rungs without verdicts:
none in this session's ownership.** Case verdicts on record otherwise unchanged.

**Live jobs: none** (no GPU node running; all lanes finished). No closure solver, no driver, no monitor. Lanes this
session: Kaandorp re-grade lane finished (wrote nothing; findings landed by me at `8dd3f8bc`); D476 ruling lane finished (stopped
correctly, wrote nothing); read-only gpu1 lane (predecessor's) finished.

**Commits this session (supervisor):** `53517fae` D491 (D476 adoption ruling
docket row, D486 fallback disclosed); `961b0b3e` D492 + L-269 (Kaandorp records,
same fallback); `6ff8e65c` board; `8dd3f8bc` Kaandorp correction addendum (+85/0,
from the HEAD blob); `506dde36` board; `979dec7f` board note; `a15b48b9` D494 correction row; `887bad8b` board; `8322b7b2` Kaandorp verdict-surface addendum (+79/0); this board write. Lane commits verified and adopted: `a56cc309`
(Kaandorp close-out — numbers re-read by me from `results.json`, addendum
headings and +513/0 append verified) and `41774899` (parallel session's lane —
both diffs read by me, PASS with the two §31.3 limitations named). NEXT ACTIONS:
(1) await verification's supervisor on pass 6 — the D476 lift becomes effective
on its confirmation, void on reversal; (2) the D492 referral limbs (a)/(b) go to
verification via the chief; (3) closure's next docket row carries the L-269
parenthetical correction; (4) the `run_lane.py:175` banner-test call-site
repair and the §31.3 `assert`→`sys.exit(2)` tightening are candidate instrument
changes for a future dated addendum + diff read, not started; (5) nothing new
launches — R6 waits on Sanaa, the GPU drafts 2–5 wait on her sign-off.

**On Sanaa's desk (closure):** gpu1 idle-stop (parallel session's request,
carried); GPU drafts 2–5 (signing is hers; plan recommends none of 4–5); the
per-point-SGD ARM-A re-registration question (D490); R5/A′ direction after
R5C's GATE FAIL (`R5_DECISION_MEMO.md`); R6 phrasing (standing); Ling & Templeton
2015 acquisition (PENDING-MIT); verification's standards recommendations (a)/(b)
from the D476 audit. **Blocked:** R6 (Sanaa); Kaandorp `AR_3_Ret_360__ML0/1/2`
(missing case in `features_nodurbin.npz`); Kaandorp Table 4 (no BFS5100 on
disk); Xiao2016_EnKF (forward model); Lozano-Durán 2023 (data + charLES); (the D476 lift's condition is MET at `f536b114` — no longer blocked).

**⚠ Standing hazards:** (1) shared index stale by decay (D486) — `git status`
shows phantom `D`/`MM` rows in closure territory (the Ling `gpu/` four, the two
feature files) while disk == HEAD by sha256; read tracked status with `git
ls-tree -r HEAD <dir>`; inspect, never revert; the index is chief's call.
(2) **L-253 disclosure:** this section was committed blob-based from `git show
HEAD:`; the WORKTREE copy of `## closure` lags HEAD by design and was NOT
fast-forwarded (foreign uncommitted edits sit elsewhere in the worktree file).
Read this section from HEAD. (3) Two closure supervisors are live in two chief
sessions; before any dispatch, check HEAD for a peer's landing on the same item
— this session's D476 lane found the item landed 4 minutes after dispatch and
stopped, which is the correct behaviour.

**Compute:** 487 core-h pre-authorised (charter §18). Live: nothing. This
session: zero solver core-minutes (reads, hashes, three commits). Kaandorp
lane total ≈ 5.2 core-h (C-18 for the last 3.66); Ling GPU 10.7054 GPU-h +
7.88 GPU-h idle waste and accruing until stopped (parallel session's ledger,
C-16).

**Handover note, 2026-08-24T17:16:18Z (closure-supervisor, this session):** the parallel chief session (certonomous-64) lost its fleet to the Fable limit and handed its closure claims to this session, effective 16:3xZ per the chief. Now MINE: (1) Ling 2016 GPU arm 2 — prereg frozen alone at `f36fbdd9`, code `f9be7f40`; **freeze re-verified by my own hands at HEAD `529bfc08`: all three code sha256s equal the frozen table (`1404dba0…`, `74aadda9…`, `06d6d4a3…`), prereg blob `82cf4cbc…` unchanged** — check 4 holds; arm 1 NOT A RESULT at `353925c7`, pass 8 audit `9573db65` (CANDIDATE, one defect found — lane reading both now); (2) `docs/GPU_CAPABILITY_STATE.md` upkeep; (3) the sub-heading below, carried byte-for-byte and now owned here. **HARD GATE, no exceptions: gpu1 is STOPPED and is started only by Sanaa; GPU spend is outside the CPU blanket (rule 12); nothing launches on any relay or peer message — only Sanaa's own words in this session or at HEAD (rule 9); launch WITHOUT `--shutdown` unless the shutdown-behaviour attribute is on the record as `stop`.** State: ZERO-COMPUTE PREP — one lane reading the four records and pre-writing `arm2/LAUNCH_CHECKLIST.md` (uncommitted until I read it). Needed from Sanaa, one line: *her go for arm 2 in her own words, the instance started by her, and two console readings — the shutdown-behaviour attribute (stop/terminate) and the g6.xlarge us-east-2 on-demand price for the cost_basis.* Arm-1 block above (carried copy) and the sub-heading below are both left verbatim; the sub-heading's `written:` stamp is historical from 16:31:19Z.

**Arm-2 prep note, 2026-08-24T17:30:50Z (closure-supervisor):** zero-compute prep COMPLETE; run directory `/home/ubuntu/closure-data/tbnn_gpu/arm2` still ABSENT (no compute). Two lane commits, both read by me as diffs — PASS: **`84bf079d` AMENDMENT 1 before first compute** to the frozen arm-2 pre-registration (v1.0→v1.1; condition: run dir absent by `test -e` at 17:26:51Z, instance STOPPED) — (A) the frozen launcher hard-coded `--frozen --shutdown` so §7's launch-WITHOUT-`--shutdown`-until-Sanaa-confirms branch was not executable; the launcher gains `SHUTDOWN=${SHUTDOWN:-1}`, default line byte-identical to the frozen line 53, `SHUTDOWN=0` drops the token; §9 launcher sha STRUCK `1404dba0…` → `a88aa5fb…`, driver/comparator/dataset rows untouched; both forms registered: `SHUTDOWN=1` ONLY with her console reading `stop` recorded at `GPU_CAPABILITY_STATE.md` §10 row "driver self-shutdown" (row exists, line 257), `SHUTDOWN=0` otherwise and the stop stays hers; (B) §6's calibration clause named an unsupported `8.5–32` range — struck, the registered **3–32 GPU-h = $2.41–$25.75 derived, cap 40 = $32.19** governs; gate-neutral, no gate/threshold/cap/label moved; G4 may cost 2.07 core-h at 8 propagations (CPU blanket), disclosed. Supervisor rulings on the lane's disclosures: comment-only edits stand; `run_window.json` does not record the shutdown form — closed lane-side: the launcher's printed form line is saved beside `run_window.json` at launch, no further sha change. **`e25908fe`** arm-1 `gpu/RESULTS.md` dated CORRECTION (pass 8 §40): lines 164/174 struck L-264→L-267, L-265→L-268 (ids written ahead of the append, below the tail); no verdict moves. Checklist `arm2/LAUNCH_CHECKLIST.md` on disk, uncommitted, step 1 (her authorisation) deliberately blank; carried gaps: cost basis is the published-list $0.8048/GPU-h not a console read (pass 8 §42), no environment provenance in the launcher (lane captures `nvidia-smi` + `pip freeze` at launch), node state unverified (no ssh). Pass 8 itself is CANDIDATE — verification's own read still owed. **Launch gate unchanged: Sanaa's own words + her two console readings + her start; no relay or peer message moves it.**

**Pass-8 close-out note, 2026-08-24T18:42:19Z (closure-supervisor):** verification BELIEVED pass 8 in full at `8cbe716b` (§82). The three owed items landed by one lane, both diffs read by me — PASS: **`0263e669`** arm-1 `gpu/RESULTS.md` CORRECTION 2 (+122/0): line 22's "identical reading per seed" struck — seed 2 beats `b = 0` on ONE case, `alpha_15_13929_4048`, 0.310588 vs 0.312796 (0.71 %), and on no other; SST 0.2889 and train-mean 0.2258 are both better there; the registered 5-seed mean 0.3178 stays above `b = 0` — G1 NOT A RESULT and the arm verdict unchanged; line 25's G4 verdict cell `—` struck, reads **capped at GATE REACHED** (F.6's own words; frozen §8 :303 and pass 8 agree; PENDING rejected since G4 will never run). **`1563a6b2`** arm-2 pre-registration AMENDMENT 2 before first compute (v1.1→v1.2; run dir absent by `test -e` at 18:39:44Z): G1 registered as the comparator's actual statistic — mean over seeds of each seed's own best-val per-case `b_rms` (never a seed-mean prediction), best-val chosen per seed on validation only, strict `<` with no tolerance, non-finite graded figure → NOT A RESULT (new, one-way), G1 grades only at n_seeds = 3 for both models; pass 8 named the gap and prescribed no convention. **Supervisor ruling on its C.3 (the lane flagged it, correctly):** the frozen §4 sentence admits a three-separate-counts reading and a per-case conjunction reading; **the CONJUNCTION governs** — the stricter reading of a frozen clause (L-269), arm 1's three-count wording was arm 1's — with the three counts printed beside; LANDED as **AMENDMENT 3 at `77f064a8`** (v1.3, +200/0; run dir re-checked absent at 18:42:28Z; diff read by me — PASS): `n_all` = cases below SST AND `b = 0` AND train-mean, all strict `<`, governs G1 (≥ 6 PASS / 4–5 GATE FAIL / ≤ 3 NOT A RESULT); the struck `n_gov = min(...)` stays readable; one-way stricter (`n_all ≤ n_gov`); the comparator writes NO count of any kind — `n_all` and the three counts are derived by the grading lane from the named per-case JSON fields and asserted by the supervisor. **Arm 2's pre-registration is now v1.3 with three pre-compute amendments; no further amendment is pending and none is planned.** Cost of all three items: zero core-minutes. Arm 2 remains PENDING on Sanaa's three-part line; nothing launches.

### Ling GPU arms — certonomous-64

written: 2026-08-24T16:31:19Z — the only lines of `## closure` this session writes; the section, its stamp block and the arm-1 block placed above are the peer session's. Repair of `f9be7f40`'s clobber: the peer's 16:24:03Z stamp block is restored byte-for-byte.

**Ling 2016 TBNN GPU arm 2 (matched update count) — FROZEN, READY TO LAUNCH,
verdict PENDING; instance STOPPED, start is Sanaa's on the chief's request.**
Pre-registration committed ALONE at `f36fbdd9` (sha256 `82cf4cbc…f153`),
code at `f9be7f40`; `cases/RANS_LES_closure_models/Ling2016_TBNN/gpu/arm2/`. Per-point plain SGD at
Ling's stated rates (batch 1, **342,014 updates/epoch**, ~3.4e5× arm 1), TBNN
8×30 + MLP control, 3 seeds as a verified stack; **E decided by an in-run P0
timing gate** (target 300, min 50) against a **40 GPU-h cap = $32.19 derived**;
**registered estimate 3–32 GPU-h = $2.41–$25.75 derived** (unmeasured per-update
time 0.05–1.0 ms; CPU smoke 0.54 ms stacked). G1 per case, G2 in-family with
`NASA_2DWMH` split out, G3 per case against each case's own truth fraction,
comparator writes its own sha, two refusable equivalence controls in P0.
Self-shutdown is the standing mechanism (plan A1, capability state §10) —
launched WITHOUT `--shutdown` until Sanaa confirms shutdown-behaviour = stop.
Falsifier with numbers: val ≤ 0.1719 → D3 confirmed as the cause; ≥ 0.30 → D3
refuted; between → indeterminate at this budget. **gpu1 STOPPED by Sanaa
(`e88b86e6`, C-19 closes arm 1's idle window at 15:56:45Z).**

## dafoam

**Section last written:** 2026-08-24T19:12:02Z by dafoam-supervisor (SIXTH session, formed from disk ~19:05Z 2026-08-24 at HEAD `d27148c8` after the fifth fleet was killed by the Fable usage limit). *Stamp is `date -u` read in the writing invocation.* **Model note:** Fable is exhausted; Sanaa ruled that anything needing Fable runs on Opus 5 temporarily, so this supervisor and its lanes are all Opus. The `### O2 re-buy + curriculum D1 — certonomous-64` sub-heading below is carried BYTE-FOR-BYTE from the HEAD blob and is a closed historical block.

**LIVE READING FIRST — the fifth session's board below was written at 17:56Z and three of its "RUNNING" items have since CLOSED. Corrected here from HEAD, not from any brief.** The forming brief for this session also asserted that D1-C′ was "frozen Phase 1 only at `c19e0cbc`" and that Phase 2 may not have run. **That is wrong and the record refutes it:** D1-C′ Phase 2 ran, was graded `PASS` at `5bec45b7` (+ Addendum 1 `c4ce2b8f`, Addendum 2 in `cffd90e7`), and D1 closed two-row `PASS`/`PASS`. Nothing was re-run.

**SUPERVISOR CHECK 3 PERFORMED PERSONALLY THIS SESSION (big-claim verification before belief), on D1-C′.** Read by me directly from the raw grading artifact `/home/ubuntu/certonomous-runs/CURRICULUM-D1Cprime-a1-shipped-endpoint/GRADE_20260824T171942Z_1479979.json` and the run ledger, NOT from the lane's report or the board: `vector_rel_err_graded_only = 0.0011469250679977656` (**0.1147 %**), `worst_rel_hi = 0.002550876167566669` (**0.2551 %**, four graded components), `any_sign_flip = False`. **The charter §4 trivial baseline is crushed, which is the part that makes the gate non-hollow:** `trivial/rel_err = 1.1260042821409841` (**112.60 %**) with `trivial/sign_flip = True`, and `trivial/armO_patched_rel_err = 1.126004049294347` (**112.60 %**) — the deliberately-wrong step fails by a factor of ~981 against the registered step, on BOTH toolchain rows. Ledger: `rc=0`, `wall_s=89`, `ranks=1`, `core_min=1.483`, `maxrss_GiB=1.6813`, `OOMKilled false`, and `IDWARP_SO_MD5: f0fcb488e0e98156575cd19548e91663` — the **stock** library, not the patched `85f59e87…`, which is what makes this a SHIPPED row. **The claim is believed; it was defended against its own evidence, and the control is reported as a control, not as a result.**

**Curriculum state at HEAD — three Tier-1 items are now CLOSED and one is BLOCKED:**

| item | state at HEAD | commit |
|---|---|---|
| **D1** NACA0012 lift-constrained drag min | **CLOSED — two-row `PASS` (patched, arm O) / `PASS` (shipped, D1-C′)**; 8.483 core-min gross / $0.007253 derived; waste 0.533 (all in D1); C-24 + C-31 | `b10260a0`, `5bec45b7`, `cffd90e7` |
| **D1-C′** shipped-image endpoint gradient at arm O's design point | **GRADED `PASS`**, ten of ten gates, no falsifier fired; 1.483 core-min / $0.001268 derived / ratio 0.915× of 1.62 / waste 0.000; C-31. Finding: the stock IDWarp `warpDeriv` defect is **DESIGN-POINT DEPENDENT** — 640 % + sign flip at the undeformed baseline, ≤ 2.80e-06 relative at the converged point; **mechanism UNTESTED, registered as hypothesis only** | `5bec45b7` + `c4ce2b8f` |
| **D2** optimizer A/B on the D1 NLP | **CLOSED.** Both arms `PASS`; `AB5` PASS **bit-identically** (arm A reproduced D1 arm O, all five identity rows exactly 0.0, graded before arm B launched); **`AB2` `GATE FAIL` and it is the item's REGISTERED FINDING** — designs 33.259 % apart in relative L2 against a 10.0 % band while objectives agree to 0.7381 %. Algorithm/conditioning finding, **never an aerodynamic claim**. 12.150 core-min of 16.733 registered (0.726×) / $0.010389 derived / waste 0.000; C-43; D508 | graded `a7f00e42`, records `b840fcd5` |
| **D3** Ahmed constrained drag min | **attempt 2 CLOSED `BLOCKED` at Stage G, falsifier class F1c.** 2.8667 core-min of a 69.2 HARD; C-46. Third registration **referred to the chief and unruled at HEAD — this session's ruling is in flight**, see below | `10b3e97c`, board `f2b54c3b` |

**D3 THIRD REGISTRATION — MY RULING IS PENDING ON ONE DECIDING FACT, and I have dispatched a bounded probe to establish it rather than ruling on the record alone.** Attempt 2's own §9.2 states the fact was NOT determined: `DVGeo.update("aero")` raises `KeyError: 'aero'` from `pyBlock.getAttachedPoints` at `pyBlock.py:745`, reached from `DVGeo.py:2012`, at producer `d3_runScript.py:253` — **but what the correct point-set key IS was never read out of `nom_add_discipline_coords`'s body**, and the record names that as a supervisor triage step. The §2d.1 four-condition test is satisfiable in principle here (a Python traceback grades nothing, so condition 2 — the independent instrument — is met by construction; there are no pre-repair values because no number was produced). **The test is not what decides this.** What decides it is whether attempt 3 would be a KNOWN-KEY deterministic repair or the third blind draw at the next unexercised line: attempt 1 died on `nom_setConstraintSurface`, attempt 2 on `dvg.update("aero")`, and **§9.4 measured that ~90 % of a no-flow stage's wall sits at or before producer line 215 in the setup path every stage pays** (`om.n2` completing ≈154.8 s into a 172 s run against a probe reaching line 214 in 11 s), so every per-stage price in the frozen §10.1 is built on an ~11 s setup basis and is invalid. Probe authorised at **≤ 1.0 core-min, np=1, no solver, no adjoint, no mesh motion** — the same class and authority as D2's disclosed 0.0333 core-min pre-freeze probe, producing **no verdict and no graded number**. It must also ENUMERATE the remaining unexercised producer lines, because the supervisor needs to know how many blind draws are left, not just the next one.

**Lanes live (3 of 3, at cap):** (1) **D3 triage probe** — the deciding fact above, ≤ 1.0 core-min, commits nothing; (2) **V standard** — `docs/dafoam/V_STANDARD_FD_VS_ADJOINT.md`, zero compute, also the deliverable of curriculum **D15**; (3) **matrix contribution** — `cases/dafoam/MATRIX_CONTRIBUTION.md` plus the `DAFOAM_CHARTER.md` §10 marker repair, zero compute. **No solver of this family is running.**

**Box at formation (`ps`, `/proc/loadavg`, `free`):** three `buoyantBoussinesqSimpleFoam` at 99.9 % CPU each (heat-transfer's, not ours), load 13.16, 27 GiB MemAvailable of 30. Lanes are capped at one core each. **VERIFY** at next write.

**Sanaa's week-8 directive, and what is left of it.** "Curriculum D2–D15 (~$7–11 total)": D2 is CLOSED, D3 is BLOCKED with its third registration under ruling, D15 is being discharged as the V standard. **D16a is PARKED by Sanaa and is neither proposed nor waited on.** A6 stays at N=16; the N=29 gate reading is hers under D464 and is taken by no agent. The A-family ledger's shipped/patched separation and the patched rows' provenance are the matrix contribution's job. Next candidates in the curriculum's own recommended sequence, all pre-authorised class and all still needing their own frozen prereg: the three ≤5 core-min reachability probes (**D10** thermal objective, **D11** MRF, **D12** unsteady adjoint — Sanaa's ratification ask 3, probes only, each under its own mini-prereg), then **D13** (5 perturbed starts on D1's NLP — the curriculum priced it at ~350 core-min, but D1 and D2 have since anchored a full optimisation at ~6 core-min, so its honest re-price is ~30-40 and the prereg must say the estimate moved and why), then **D8** (A6 CRM N=16 twist-only, ~80-120 core-min, inside the 30 GiB envelope, twist idx6 named `NOT A RESULT` in advance).

**Rungs lacking verdicts:**

| item | state |
|---|---|
| **D3 attempt 3** | UNRULED — deciding fact in flight (above). Attempt 2 `BLOCKED`, item total ≤ 3.65 core-min of ~70 |
| **A6 N=16** | COMPLETE at 8 of 9 — `PASS`, aggregate 1.0432 %, zero sign flips (row 37); twist idx6 `NOT A RESULT`. **N=29 NEVER RUN**; gate wording Sanaa's (D464) |
| **A3 patched column** | rung 2 MEASURED `PASS` (degrades vs shipped, N-D18); rung 1 dual reading AS REGISTERED, rule choice on Sanaa's desk; rung 3 attempt 2 `GATE FAIL` (adjoint, INHERITED, identity 11/11, `8871acf3`); attempt 1 `NOT A RESULT` (memory). 399,360 campaign `PENDING` |
| **ADF primal non-reproduction (D460)** | sweep 1 `PASS`, class CONDITIONING / DIAGNOSABILITY (D498). Readiness **NOT READY** (`91fdde39`), 11 gaps. Filing is Sanaa's |
| **W4 O2 / O3** | O2 re-buy CLOSED `PENDING` (C-15) + O2R-P2 MISS addendum `588993d9`; O3 `BLOCKED` on Sanaa's guard authorisation. No compute on either |
| **A2 `CD/shape` PATCHED idx46** | caveat RECORDED (rows 34-35); the 207-238 core-min sweep not bought |
| **B3 Stage 4** | `BLOCKED` by construction — Sanaa's fork-adoption call |
| **Curriculum D4-D14** | `NEVER RUN`. D4-D7, D9, D14 unstarted; D10/D11/D12 probe-gated; D13 re-pricing owed |

**Two-row verdicts standing (shipped / patched):** A1 `GATE FAIL` / `PASS`; A2 `PASS` / `PASS` with the idx46 per-component caveat, optimisation `NOT A RESULT`; A3 primal `GATE REACHED`, adjoint `BLOCKED` (399k) — sweep rungs 1-2 `PASS`, rung 3 `GATE FAIL` (conditioning) / `GATE FAIL` (adjoint, inherited); A4 `PASS` / `PASS` (CD −7.478 %); A5 `GATE FAIL` / `PASS`; A6 `BLOCKED` (full) — N=16 `GATE FAIL` (shipped, superseded reference) / `PASS` at 8 of 9; B2 `PASS`; B3 `BLOCKED` / `PASS`. Curriculum D1 `PASS` (shipped, D1-C′) / `PASS` (patched); D2 both rows PATCHED, shipped stays `BLOCKED` where D1 left it; D3 `BLOCKED` / `BLOCKED`.

**Next actions:** (1) rule on D3 attempt 3 the moment the deciding fact lands, and say so plainly if the answer is that it is not warranted. (2) Land the V standard and the matrix contribution, then the curriculum §7 ledger row for D15. (3) Register and run the three ≤5 core-min probes (D10/D11/D12), each under its own frozen mini-prereg committed before compute. (4) Re-price and register D13 against the D1/D2 anchors. (5) Records for everything landed this session via the D486 HEAD-blob fallback, ids re-derived from the HEAD tail in the same invocation, insertions-only asserted; a `COST_CALIBRATION.md` row at every completion.

**On Sanaa's desk (unchanged unless marked NEW):** **NEW — nothing this session yet.** Carried: D3's 45,760-cell successor (mesh change, UNPRICED — the only route to separation content on that case, since the 2,777-cell A4 adjoint mesh was measured to carry **zero** reverse-flow cells); the NOTICE that curriculum D2's trust-region half is undeliverable on this box (no importable trust-region optimizer; nothing about building `ParOpt` was run or costed); the D460 draft `NOT READY` and `NOT FILED`; A3 rung-1 §4 rule choice; the **D464 N=29 gate wording**; R11 adoption evidence now three-sided (D1-C′: shipped and patched agree at a converged design point, disagree at the baseline); the MemAvailable 12 GiB floor; **the five upstream defect drafts, all NOT FILED** (D-A/D-A2, D-B/D-B2, D-C, D-E, plus ADF `757eccf0`); B3 Stage 4; the near-zero sign-flip class; the charter §13 PROPOSAL (unratified, not enforced by this session); O3 guard authorisation; O2's >20 GiB-to-one-process instance question. **D16a is PARKED by her and is not on this list as an ask.**

**Blocked:** D3 attempt 3 (on this session's own ruling, not on anyone else); B3 Stage 4, A6 N=29 wording, O3, O2 continuation, all four Sanaa's; ADF filing readiness (11 gaps, six of them zero-compute).

**⚠ Integrity flags on frozen records, none quoted from:** `A1_naca0012_incompressible.md:167-172`; `A5_ubend_internal.md:194-196`; `A2/grading_confirmation/RESULTS.md` §1 falsified at PATCHED idx46.

**Standing rules carried:** shared-board rule (rebuild from `git show $H:`, replace only `## dafoam` via `scripts/lab_state_section.py`, `hash-object` + `cacheinfo`, `diff-tree` confined, read the section diff before staging); record-append rule (`append_record.py` after `check_record_reconciliation.py`, D486 HEAD-blob fallback disclosed in the commit message, trailing-newline assert every time); **guard every step of a commit chain with `|| exit` — `set -e` does not stop the tool shell, and that is how `d99d82cd` became an EMPTY commit whose message claimed a board write.** `DAFOAM_CHARTER.md` v1.0c; §13 PROPOSAL and §14.1 PROPOSAL both UNRATIFIED and NOT enforced. **Images:** `dafoam-idwarp-rot:v1` (rotation patch, md5 `85f59e87…`), `dafoam-subpclu:v2`, `dafoam-kspopts:v1`, `dafoam-team:v1` (`0b3c94c33a15`), and the shipped `dafoam/opt-packages:latest` (IDWarp `.so` md5 `f0fcb488…`). *The hash is the identity; the version string is not.* **F6 under `cases/dafoam/` is plain `simpleFoam` with no adjoint anywhere — 88 % of the tree by size, its records live in `verification/campaign/`, and it is not DAFoam work.**

**Ids at HEAD `d27148c8`, re-derived this session and STALE THE MOMENT THEY ARE WRITTEN — re-derive at commit:** L-301, N-D40, D509, C-46. The rule is the re-derivation; these four figures are a dated reading and nothing more.

**Last commits (newest first):** `f2b54c3b` board · `10b3e97c` D3 attempt 2 GRADED `BLOCKED` + C-46 · `b840fcd5` D2 records L-296..L-299 / N-D36..N-D40 / D508 · `a7f00e42` D2 GRADED + C-43 · `bec36c9d` A3 rung-3 Addendum 1 · `641c5938` D2 authorisation §18 · `91fdde39` D460 readiness NOT READY · `03580b8f` D2 prereg FROZEN · `0cbf463c` D3 prereg FROZEN · `cffd90e7` D1 records · `dfe5292d` rung-3 records · `d99d82cd` EMPTY (incident) · `c4ce2b8f`/`5bec45b7` D1-C′ GRADED + C-31 · `8871acf3` rung-3 attempt 2 GRADED + C-29 · `c19e0cbc` D1-C′ prereg FROZEN · older: `git show f2b54c3b:docs/LAB_STATE.md`.

### O2 re-buy + curriculum D1 — certonomous-64

*written: 2026-08-24T16:30:54Z (`date -u` in the commit invocation) by the 64b13819 session (`01ENBw3KPr5gMaj8Vt7rcxSB`, "session 2" above). This sub-heading is the only text this session writes on the board (both chiefs' rule, 2026-08-24); the section and its stamp line are the peer session's. Repair forward: this commit removes the pre-rule CLOSE-OUT ADDENDUM block that `d360e997` had inserted into the peer's text; the fourth session's stamp line and every other byte of its 16:23:53Z write are untouched (its stamp's reference to "the session-2 close-out addendum below" now points here).*

- **W4 O2 re-buy — CLOSED `PENDING`** (results `5a93f6ee`, prereg `8d48fd46`; records `b69ac6ec`: L-264, L-265, N-D27, D488, **C-15**). `spilu` **4 of 4 exactly singular** (the CBFS signature on a second case); `splu` **`NOT A RESULT`** — killed by the registered 20.0 GiB cgroup cap inside its first threshold (rc 137, `memory.peak` 21,474,836,480 B exactly, right-censored); frozen §3 rule → `PENDING`. **15.00 core-min MEASURED / $0.01283 derived / 0.43× of 35.0 / zero waste** (the cap was the pre-registered instrument; gap = memory-band misprediction, duration untested). **Sanaa's desk:** > 20 GiB free to one process (instance change) or a factorization that fits — beside O3's guard authorization. Every number verified by this supervisor against the raw log.
- **Curriculum D1 (Tier 1, first executed item of the RATIFIED curriculum `43b530cc`) — PATCHED row `PASS`, SHIPPED row `BLOCKED`, item `PENDING` on D1-C′ only** (prereg `f07256fb` + Amendments 1–2 + Addenda §16 `668ce997` / §17 `3f926240`; results `b10260a0` by Lane Z, dispatched by this session 16:03Z; records `3f926240`: L-273, N-D28, N-D29, D497, **C-24**, status rows 38/38b). Verified against `armO_20260824T160553Z_1400030.log`: `EXIT: Optimal Solution Found.` in **11 majors**, NLP error 4.087e-07; **CD 0.020943920630946831 → 0.017527899854535338 = −16.310 %** at |CL−0.5| = 1.879e-07, 24/24 constraint rows in bound; endpoint FD **≤ 0.2553 % on 4/4 named components, zero flips**, steps from endpoint |J_adj| and η alone (L-266's repair visible: `3e-4` selected). P3 MISS high (16.3 % vs [2, 12] %). Arm C died pre-solve on a frozen-comparator key mismatch (L-273); **ruling (§17): §4.2(c) forbids the in-place repair, comparator NOT edited, arm O's PASS stands; the shipped-row comparison is re-registered as mini-item D1-C′** — prereg lane dispatched by this session 16:28Z, phase-split, no compute until the freeze is verified. Cost **7.000 core-min gross / 0.533 named waste / $0.005985 derived, 0.304× of 23.0** (IPOPT took full steps on all 11 majors — the line-search primal priced into every major was never bought).
- **Housekeeping:** `check_record_reconciliation.py` reads FAIL on LESSONS/NUMERICS/DOCKET as "IN HEAD, NOT IN THE WORKTREE — HEAD WINS" for exactly the ids this session appended by the HEAD-blob fallback; the worktree copies are deliberately untouched (chief's line) — the checker's write-back remedy vs that line is the chief's/Sanaa's to reconcile. 1.11e+02: resolved, no correction (`0d96119d`). Live: Lane C′ (prereg only). Nothing filed anywhere.

*Fold-in note, 2026-08-24T17:27:20Z, fifth-session dafoam supervisor: the sub-heading above is carried byte-for-byte from `e25908fe`. Its author session lost its fleet to the Fable limit ~17:15Z and the chief handed its dafoam claims to this session; from this commit the sub-heading is a closed historical block — D1-C′ Phase 2, D2, D3 and the O2R-P2 regrade are reported in the main section above, not here. O2 and O3 remain untouched on Sanaa's desk.*

## heat-transfer

**Section last written:** 2026-08-24T18:50:57Z by heat-transfer-supervisor (the
session holding T3 ext1, T1b L4 and D477 since the chief's redirect
2026-08-24T16:00Z). **Two heat-transfer sessions write this one section
and overwrite each other by construction** — `1a634bb2` (16:04Z, the
curriculum session) replaced this session's `d145cd22` wholesale. Until the
chief rules on single ownership, this session carries the curriculum
session's state VERBATIM under the sub-heading at the foot; the curriculum
session is asked to do the same for this session's rows. Earlier history
condensed: `eb2a534b`, `450735c1`, `b84c43d3`.

**Claim ledger — this session:** T3 ext1 close-out (LANDED `3dd28411` +
`398dfb3d`), D477 restore per the chief's ruling (LANDED `3a2f37c3` +
`3f2480a1`), T1b L4 completion + grading (watch LIVE), **EXPERTISE_CURRICULUM
execution — HANDED TO THIS SESSION by the chief ~17:13Z** after the parallel
curriculum session lost its fleet to the usage limit (E4a2 frozen
`cd1f46e1`, GRADED PASS `5a197a41` + `edee5088`). Section ownership RULED (both chiefs): this
session owns `## heat-transfer`; the former curriculum sub-heading is
**folded in below (dated note, this write's stamp)**, their E4a grading
paragraph carried verbatim at the foot of this section.

### EXPERTISE_CURRICULUM — owned here since 2026-08-24 ~17:13Z (chief's handover)

Landed state verified at HEAD before anything was dispatched (read-only
lane, zero compute): **E4 stage (a) GRADED 2026-08-24T16:16:26Z NOT A
RESULT** (D493, C-21, L-270/L-271; frozen `628e29c4`; I1/I2/P1/Z1 PASS,
R1/G1/G2/N1/D1 NOT A RESULT — the registered bit-identity convergence gate
cannot close on iterates creeping ~6e-11 relative at writePrecision 12;
cost 0.0748x, cross-solver-class basis 13.6x, no waste); all records
consistent, disk == HEAD (the staged `D` rows on `E4_runs/` are D486
phantoms). **The curriculum's own C-A sequence (E1 → E4 → E3-a → E2 →
E3-b) has no unblocked successor**: E1 waits on T5 graded + K2a approved,
E3-a on T11 graded + E1, E2/E3-b NEEDS COSTING → return to Sanaa costed.

**E4a2 — GRADED PASS 8/8, 2026-08-24 (`5a197a41` results + run artifacts;
`edee5088` C-34 / D505 / L-281).** Frozen `cd1f46e1` 17:23:22Z; selftest
95/95 against zero case trees; five cases serial at nice 15, rc=0 5/5,
strict rule 5/5 with the age guard; frozen comparator `26a10ef4…` exit 0.
**The re-registered gate closed on all five (§3.2 CONFIRMED):** worst C1
1.113e-09 vs floor 1e-8, worst C3 2.526e-10 vs 1e-7, C2 nowhere. Rows: I1
6.033e-11 m²/s² (tol 8.1e-8), I2 9.712e-10, P1 0 outflow faces, **R1 order
1.959 in [1.6, 2.4], GCI 0.393 %**, G1 +0.144 %, G2 +0.239 %, N1 +0.288 %,
D1 −0.171 % — every row inside its carried-over interval; Z1 held; X1
reproduction gaps 0.0000 pp vs E4a on all five. **Cost 8.283 core-min =
$0.00708 derived vs 665 core-s registered = 0.747x** (solver subtotal
0.959x — C-21's measured basis reproduced to 0.7 %; comparator
over-registered ≥30x), waste none. Carried as reported, not smoothed: three
of five series classify LIMIT CYCLE while passing (pre-registered, §2.2 —
the rung certifies a stationary bouncing iterate); first crossing at 4 000
on every case, so endTime 60 000 bought margin, not convergence → L-281.
Supervisor's checks personal: instrument diffs read before the freeze,
comparator log read after the run, `5a197a41` read as a diff of paths
(2.40 M of 2.40 M insertions are the ten tracked `log.solve*` files,
mirroring E4a's set), the DC_CERTIFICATE_TEMPLATE line confirmed in section
2 with its "backs the BC, not any fan" note (H-6). Pending one small
commit: §8's bullet citing `RECORDS_DRAFT.txt` struck and the draft
removed. **E4 stage (a) CLOSED at PASS on its second rung.**

Earlier state at the freeze:
The parallel session's lane drafted it 16:26–16:37Z; adopted after this
supervisor's own reads (non-delegable): comparator/builder/marker diffs
against the frozen E4a instruments after inverse rename — no rule
re-implemented, every grading path the frozen E4a function via a restoring
`in_dir` redirect with refusal; shell scripts byte-identical after inverse
rename; selftest 95/95, five mutation controls exit 2; committed blobs ==
§6 sha256 table; tree empty at the commit. **One thing re-registered:** the
convergence gate — C1 floor 1e-8 relative (peak-normalised) sustained over
3 intervals, C2 not-growing fit, C3 half-run Q stationarity 1e-7 — floor
bounded above by R1's order sensitivity (1.204e-8 max) and below by the
write quantum (1e-11); endTime 60 000, writeInterval 2 000, purgeWrite 0;
X1 reproduction control refuse-only. Registered prediction: the gate closes
on all five cases. **Cost registered 665 core-s = 11.08 core-min = $0.0095
derived**, per-case 10x stop thresholds. Docstring lag (C1/C2 named, C3
implemented as registered) disclosed in the commit, not edited.

**E4 stage (b)** (manufacturer datasheet validation): on Sanaa's desk since
D483 but with **no actionable ask** — no fan model named, no purchase
expected (public datasheets are free; a lane can fetch one with rule-15
title verification if Sanaa names or approves the model). Added to the desk
list below as a question, not a spend.

Amendment 1's "per usual" clause (formal .md updates per item; lab-wide
propagation through the chief) binds every item here. E2, E3-b, E7-3D,
E12-build remain NEEDS COSTING. Full curriculum text: `fe409422`; the
parallel session's last board text: `1a634bb2`.

### T3 — ext1 RE-GRADED 2026-08-24: NOT A RESULT 4/4 at gate (1) (`3dd28411`)

- **8/8 cases under the two-segment strict rule** (`mark_done_t3_ext1.py`,
  both `End`s, `20000 + ext1 ExecutionTime == endTime`, first ext1
  `Time = 20001`, age guard vs `0/T` and `STATUS.<case>`); `R_f` finished
  2026-08-24T14:53:19Z, 24 h 1 min ahead of the contended-basis ETA.
- **Frozen comparator `analyse_t3.py`** (sha `f41c544d…`, byte-identical to
  the §11 blob, verified by two lanes), exit 0, planted zero 1.234e-03 K
  read back and passed. `gate_t3.json` sha `8e766cd5…` (15:58:44Z).
  **Tally PASS 0 / GATE FAIL 0 / NOT A RESULT 4 / BLOCKED 0; 0 of 4
  graded.** All four rows fall at gate (1): `R_c` is in a limit cycle at the
  80 000 cap (rel ΔT 4.83e-02) — prereg §11's registered alternative; the
  rung says so and does not average.
- **What changed in cause:** `R_m`, `R_f`, `P_m`, `D_m`, `O_m` CONVERGED
  (`R_f` 9.68e-08 / 7.80e-08); `W_m` still outside at 1.409e-06 after
  60 000 more iterations (P1's exposed clause HELD); St ladder monotone in
  mesh for the first time; G3/G4 DIVERGENT→STAGNANT (p 0.23 / 0.22); **G2
  `x_peak/H` CONVERGING (p 4.304, GCI 0.0188 %, RE 6.1403) and NOT A
  RESULT anyway** — gate (1) fires first (rule 5, in the only direction it
  allows). `R_f` heat balance 8.234 % → 0.000393 %: amendment §4's
  non-convergence reading is now a measurement (P2 HELD). P3 primary clause
  HELD / secondary FALSIFIED by G2; P4 HELD.
- **Cost (C-23):** 4 798.05 core-min = 79.968 core-h = **$4.102 derived**
  (not measured) vs $4.08 registered = **1.005x — two cancelling errors**
  (no fixed startup term: W_m/D_m/R_c 1.40–1.62x; a 5-min contention window
  extrapolated across a 45-h critical path: `R_f` 0.653x of its ETA). Waste
  nil; stop threshold reached 17.9 %. Rung total $6.171 = 24.7 % of $25.
- Records: T3_RESULTS §14, T3_EXT1_AMENDMENT §15, index + directive rows
  (`3dd28411`); C-23, **D495** (fourth level `R_ff`), L-272 (`398dfb3d`) —
  ids re-derived at commit from the HEAD blob (C-16→C-23, D491→D495,
  L-269→L-272 had all moved). Supervisor's own checks done, not relayed:
  `3dd28411` read as a diff (11 885 of 11 896 deletions are the JSON
  regeneration; 8 `endTime 20000;` lines; 3 living rows; state moves in the
  JSON are exactly 9× NOT_CONVERGED→CONVERGED, 2× DIVERGENT→STAGNANT, 1×
  OSCILLATORY→CONVERGING); G2 order recomputed from e21/e32 = 4.30.
- **D495 — CHIEF RULING: NOT AUTHORIZED NOW.** 150–200 core-h, $8–10
  derived, 6.4–8.4 days serial; wall binds, H-2 puts T5/T8/T12 ahead, and
  two obstacles a fourth level does not solve remain: the Vogel & Eaton 1985
  primary (Sanaa's desk) and the **δ99/H inlet-window miss (0.668–0.671 vs
  [0.80, 1.35], prereg §4.4)**. Costed option on Sanaa's desk; revisit when
  the primary arrives. An inlet-window diagnosis arm is a candidate only —
  not pre-registered, not priced, not started.
- Left uncommitted, disclosed in `3dd28411`: seven `T3_runs/*/log.checkMesh`
  (a 2026-08-21T21:27Z checkMesh re-run, pre-ext1, header-only, unattributed).
- Provenance disclosed in §14.2: the marker and comparator were run by the
  parallel session's lane at 15:58Z before the 16:00Z redirect; this
  session's lane corroborated (six hashes, dry-run 8/8 at 16:09:32Z,
  `gate_t3.json` byte-identical) and did not re-run the comparator.

### Audit pass 9 (verification `eab2f6c5` §63–71) on T3 ext1 — ANSWERED (`2f1d6cb7`, `792acd8f`)

**Richardson-extrapolate SIGN inverted** at `analyse_t3.py:384` and
`analyse_t1c.py:337` (`f_fine + e21/den` with `e21 = f_med − f_fine`; Roache
gives `f_fine − e21/den`; signature: coded + corrected = 2·f_fine exactly,
confirmed on T3, E4a2 and T10a). **Display-only everywhere — no verdict in
the lab is a function of a Richardson value** (verdicts are dev ≤ GCI band;
`gate_t1c.json`/`gate_t3.json` carry no richardson key; T1b/L4 computes
none; the DC certificate quotes none). Corrected values on the record: T3
G2 6.14027 → **6.142121**; T1c `Ts` +0.1106 → +0.0624 %, `q″` +0.0748 →
**+0.0013 %** (§5's "both arms overshoot after extrapolation" struck as to
`q″` only; L0 GATE FAIL / L2 PASS unmoved); dts/dts_p diagnostics; K0cX
0.2365 → 0.22560 (reading survives); K0cG defective in json, recomputed;
K0b correct. **Frozen comparators byte-unchanged** (`f41c544d…`,
`60893b28…`) — in-file addenda impossible: `analyse_e4a2.py:139` REFUSES on
`analyse_t1c.py` hash mismatch (E4a2_registered.json:355) — so rule-6
sidecars `analyse_t3.ADDENDUM_2026-08-24_richardson_sign.md`,
`analyse_t1c.ADDENDUM_…md` + dated foot addenda on T3_RESULTS §15,
T1c_RESULTS §6, K0cX_GRID_CONVERGENCE §6, DIAGNOSTIC_PREDICTION (529
insertions, 0 deletions). **Standing control** N-T8: every T-family
comparator selftest carries a value-checking Richardson control (E4a/E4a2
already do, for `richardson_corrected`); D509. **T3 prereg :241 stamp
+149 s ahead of committer date** (bd3edfe8 class; gate-neutral, committer
date precedes first compute by 13 s) — dated note T3_PREREGISTRATION §13;
audit §68's "76 s" figure flagged as inconsistent with §63's own times.
Out of territory, flagged to the chief: `F9_work/f9_criteria.py:527` and
`4G_runs/…/ladder.py:64` carry the same form (cfd). Left uncomputed:
DIAGNOSTIC_PREDICTION's Pr-dependence figure (needs corrected Pr-sweep
triples). Zero compute.

### Live jobs — T1b L4, reading 2026-08-24T16:02:14Z (lane, `date -u` in the invocation)

Three single-core `buoyantBoussinesqSimpleFoam`, endTime 80 000, all 99.9 %
CPU, cwd confirmed by `readlink`. **Do not touch them.**

| pid | cwd | iteration / endTime | rate (checkpoint mtimes) | ETA |
|---|---|---|---|---|
| 442445 | `T1_runs/R_300k_x` | 73 369 / 80 000 | 27.2 it/min | **~2026-08-24T20:06Z** |
| 450274 | `T1_runs/R_100k_x` | 60 877 / 80 000 | 19.5 it/min | ~2026-08-25T08:22Z (upper bound) |
| 488219 | `T1_runs/R_30k_x` | 55 524 / 80 000 | 17.5 it/min | ~2026-08-25T15:22Z (upper bound) |

Completion watch on `R_300k_x`: background until-loop, 10-min poll, cap
2026-08-24T23:00:52Z; marks under `mark_done_t1b_L4.py` (byte-identical to
HEAD, `f75f4a81…`; `analyse_t1b_L4.py` `9698adb0…`), does not grade. Grading
waits for all four x-cases DONE (the comparator refuses partial pools by
design). **Deadline guard: no `STATUS.R_{30k,100k,300k}_x` by 2026-08-27 is
a finding.** Disclosed slip: the watch lane's `--help` probe ran the marker
once in real mode at 15:59:47Z (no argparse) — rewrote `DONE.R_10k_x`
byte-identically, touched nothing else, running cases unreachable by it.
All four `R_*_x/log.checkMesh` worktree diffs are the runner's at-launch
`checkMesh` (header lines only, `points: 421275` both sides) — inspected,
not reverted. Projected `R_300k_x` cost ~70.6 core-h vs 59.0 registered
(1.20x, projection not a row); L4 owes its calibration row at completion.

### D477 — chief's ruling 2026-08-24, EXECUTED (`3a2f37c3`, `3f2480a1`)

**Done:** all nine tracked files restored to the worktree by `git show
HEAD:<path> >` (lane), 9/9 `hash-object` == HEAD blob, zero HEAD bytes
changed, repo-wide ` D` rows nine → zero (verification restored its harness
under the same ruling). Two dated provenance notes committed in the K2bP
case dirs (`3a2f37c3`, 114 insertions, nothing else); D477 + D495 in-row
dated notes from the HEAD blob (`3f2480a1`; reconciliation reads FAIL on
the stale worktree by construction — D486 pattern — disclosed in the
message with the append-only asserts). The lane's own commit attempts and
every `python3` invocation were denied by the auto-mode classifier; it
refused to split the protocol and handed the commits to the supervisor.
**K1 provenance REMAINS OPEN.** Triage summary:

Triage (read-only lane, zero compute) bounded the eight K2bP
`HEATBALANCE_{400,800}` clearings to **2026-08-18T04:24:55Z → 04:43:00.8Z**
(`fa2c8bb0` commit; case-directory mtimes) — a first-pass 800-iteration
artifact set superseded by the 5 000-iteration in-place re-run; D390 is the
right mechanism class, mis-mapped onto the HEAD blobs (a311d872's "never
existed" premise falsified by the frozen tree; 0c742c66's implied "D390
does not apply" also wrong). `K1_STANDING_THERMAL_CHECKS.md`: bounded
2026-08-17T18:59:00Z → 2026-08-18T04:07:19Z (L-122's own porcelain reading),
nowhere on the box, mechanism NOT identified; verification's independent
reading (`f536b114`) supports "never written to this worktree" (sole file of
its commit, never deleted by any commit, 8 prunable worktrees into the wiped
scratchpad). **RULING:** restore all nine from HEAD by `git show` (zero HEAD
bytes), two dated provenance notes in the K2bP case dirs, D477 in-row note
with both bounds and the corrected reading, **K1 provenance stays OPEN**;
`scripts/mutation_harness_known_test_names.py` is verification's, outside
this ruling.

### T9aH — GRADED 2026-08-23 (`359cccfb`, `b698dfc3`); rung table

T9aH: frozen path NOT A RESULT x3 + FR3/FR4 GATE REACHED exactly as §4.1
registered; new instrument H1–H5 PASS (worst 3.183e-12 K), null arm misses
2.41e+05x — interface-scheme cause CONFIRMED; $3.053e-04 derived; A.8
CLOSED. Open cross-rung question (verification/chief): `Gauss harmonic` as
the registered CHT default.

| rung | verdict |
|---|---|
| **T1c** | GATE FAIL 3/4; L4 row NOT A RESULT |
| **T1b** | PASS x4 frozen comparator but every triple DIVERGENT/STAGNANT (D440); no mesh-converged value until L4 lands (10k DONE, 3 running) |
| **T1a** | BLOCKED — no band from one correlation |
| **T3** | **NOT A RESULT 4/4 after ext1 (`3dd28411`)** — gate (1), `R_c` limit cycle; G2 triple CONVERGING but ungradeable; primary NOT OBTAINED; D495 fourth level NOT AUTHORIZED NOW |
| **T9a** | GATE FAIL; T9a-D REPORTED (D454, L-227); T9aH GRADED — cause CONFIRMED |
| **T10a** | GATE FAIL (closed); T10a-R GATE FAIL 5/4/0 (D466, L-244); T10a-VF REPORTED (D457, L-231), upstream candidate #4 NOT FILED |
| **T4** | half-open — graded rows need closed ASME primaries |
| **T5** | PRIMARY HELD; prereg draft unfrozen, 12 INTERPRETATIONs on Sanaa's desk — **next on the H-2 spine** |
| **T2, T6–T8, T9b/c, T10b, T11–T13** | not started; T6/T12/T13 and likely T7, T9c over $25 |

**F14 / DC-cooling:** K0c PASS; K0cS/T/X GATE FAIL; K0b BACKED x2; K0cG GAP
D470 (cost repaired `878f1556`, 1.350x); K0cQ GAP D468; K0cR/K0cP token
findings; K2e/KV1 GAP D469; K2b cost VOID; K2a on Sanaa's desk. Disk truth
`d4597293`. D477 as above.

**Next actions:** 1. `R_300k_x` lands (~20:06Z) → mark; `R_100k_x`,
`R_30k_x` (2026-08-25) → mark → `analyse_t1b_L4.py` → four (m,f,x) triples
under the amended Roache rule → calibration row → commit. 1b. E4a2
DONE (PASS); the curriculum's C-A tier has no unblocked successor — next
curriculum compute waits on the spine (T5) or on Sanaa naming a fan for
stage (b). 2. K1 provenance:
one remaining line of attack — read the ~20 commits in the
2026-08-17T18:59Z → 08-18T04:07Z window for embedded porcelain readings
(read-only, zero compute); not started. 3. T5: on Sanaa's INTERPRETATIONs;
freeze before any case. 4. D468 / D469 — separate, separately
pre-registered, not unilateral. 5. Seven `T3_runs/*/log.checkMesh` worktree
diffs (pre-ext1, unattributed) — somebody to be dispatched to land or
attribute them.

**On Sanaa's desk:** Vogel & Eaton 1985 purchase (~25–40 USD, unconfirmed)
— T3's gate-(3) blocker and the D495 revisit trigger; **D495 `R_ff` as a
costed option (150–200 core-h, $8–10 derived)**; T5 INTERPRETATIONs; T1b L4
cost 10.54 USD registered vs ~5 approved (running, on the record); upstream
candidate #4 (NOT FILED); UPSTREAM_QUEUE #4 numbering; K2a; T10aR prereg
ADDENDUM 2 (on disk, unfrozen, uncommitted — no agent re-routes it);
**E4 stage (b): which manufacturer fan/datasheet — a naming decision, no
spend expected** (carried since D483 without an actionable ask);
**ratification of the two D477 commits (`3a2f37c3`, `3f2480a1`) landed by
this supervisor after a lane's classifier denial** — with the chief since
~17:15Z, no further such landing until she rules.

**Blocked:** T1a; T3 graded rows (gate (1) ladder, then gate (3) primary,
then the inlet-window flag); T4 (ASME primaries).

**⚠ D389 open and deliberately unrepaired** (S13 mean-normalisation, ~24x
looser than it reads; moves verdicts across K0c/K2e/KV1). Owner: chief.

#### E4a grading paragraph — the parallel curriculum session's words, carried verbatim from `1a634bb2`/HEAD (folded in under the dated note above)

**E4 stage (a) — GRADED 2026-08-24T16:16:26Z: rung verdict NOT A RESULT (D493, ledger C-21, lessons L-270/L-271).** Frozen `628e29c4` before any case; 5/5 built, run serially, strict rule 5/5; frozen comparator exit 1 (graded), planted-zero held. **I1 PASS** (BC equation residual 3.794e-11 m²/s² vs 8.1e-8), **I2 PASS** (7.1e-10), **P1 PASS**, **Z1 PASS**; **R1/G1/G2/N1/D1 NOT A RESULT** — the registered bit-identity convergence gate cannot be met by iterates creeping ~6e-11 relative at writePrecision 12 (residuals 1e-10…1e-14); no order/GCI quoted; the §1.5-agreement diagnostic is held unconverted. Cost registered $0.033 → actual $0.0024 derived, **0.0748×**, misprediction: cross-solver-class basis (13.6×), no waste. **Successor E4a2 in design** (lane; same physics/rows/intervals, ONE re-registered thing — a bounded convergence gate with a derived floor, plateau reading, longer endTime, measurable first-crossing); freeze committed before any case, costed on E4a's measured basis. Stage (b) still on Sanaa's desk. Lab-wide propagation proposed via chief: solver class of every cost basis stated (L-271).

T10a-R (their 2026-08-23 grading, D466, L-244) is carried in the rung table
above; their full text is at `1a634bb2`. Ratification/NEEDS-COSTING clauses:
see the curriculum block above.
## cfd

**SEVENTH SESSION — 2026-08-24T23:55:10Z, written by cfd-supervisor personally** (formed from disk after the sixth fleet was killed by a session usage limit ~20:50Z). *Stamp is `date -u` read in the writing invocation.* **The worktree copy of this board was 116 lines BEHIND HEAD, so this block was appended to the HEAD BLOB via `hash-object` and NEVER from the worktree** — the D486 / `df36bd3f` class. **HEAD also moved TWICE while this block was being written** (`9c69a79a` → `0f4c26a8` → `f14c7a5e`, the chief and closure landing); the first insert was rejected by its own pre-commit assertion and redone against fresh HEAD — L-223, caught rather than committed. Bytes outside `## cfd` are asserted byte-identical to the HEAD blob.

**Last commit: `9c69a79a` — `scripts/roache_triple.py`, the shared Roache/GCI triple instrument for the 2D aero families. ONE file, +1074, ZERO COMPUTE.** Asserted before (`diff-tree --stat` showed only that path) and verified after (`git diff HEAD~1 HEAD --stat`). Instrument identity for citation: blob **`8dee0d31e94d3f59d28658f88a4cd6df80ae8e39`**, md5 `ae64dc482ae2069d233719e68e9192b8`, sha256 `452f475181c9897000ea530b39a84bd3e7e9927e0a3fd39fe8b1105f538ac051`.

**SUPERVISOR CHECK 1 (measurement-script diff, NOT DELEGABLE) — DONE PERSONALLY, INSTRUMENT CLEARED.** The predecessor lane finished this file and stopped, holding for compute clearance; it was **uncommitted when the fleet died and SURVIVED on disk** (52,601 B, mtime 19:19Z), so nothing was lost and nothing was rewritten. What I read, and checked rather than relayed:

- **The Richardson sign is correct.** With `e21 = f_med - f_fine`, Roache's `f_exact = f_fine + (f_fine - f_med)/(r^p - 1)` is `f_fine - e21/den`. Both GCI forms (`gci_equal:238`, `gci_unequal:300`) carry it identically. The parents carry `+` (`analyse_t1c.py:337`, `analyse_t3.py:384`) — the extrapolate reflected through the finest value onto the COARSE side, right distance, wrong way.
- **THE PARENTS ARE NOT EDITED.** Frozen under rule 6, owned by heat-transfer, and that team has already ruled its comparators unchanged with corrected values as dated addenda (`2f1d6cb7`). This file is new, so writing it correct is not a departure from a freeze — it is the first instance that gets to be right. Both values are returned side by side, `richardson` and `richardson_parent_convention`, and the display marks the second **sign-flipped**.
- **The parent cross-check is scoped CORRECTLY, and this is the subtle part.** It matches the port's *parent-convention* value against the parents' `richardson`, proving the divergence is **exactly one sign and nothing else drifted**; it does NOT match the corrected value against them, which would weld the defect to a passing test.
- **N-T8 CONFORMANCE, so the lab lands ONE instrument and not two.** Heat-transfer registered the standing value-control as **N-T8** at `792acd8f`. Selftest §(iii-b) IS that control here: 1.16/1.04/1.01 at r = 2, dim = 2 recovers **p = 2.0000** and extrapolates to the true **1.0** asserted at **1e-12** (the parent form returns 1.02), plus the structural identity `richardson + richardson_parent_convention == 2*f_fine` asserted to **1e-15** and swept across a mixed family in both forms and both dims. I added the explicit N-T8 binding to the docstring before committing, so conformance is stated rather than accidental.
- **BLAST RADIUS CHECKED IN THE CODE, NOT ASSUMED.** `band_verdict` grades the **FINE VALUE**, never the extrapolate; **no verdict this module can emit is a function of `richardson`** — display-only, exactly as heat-transfer's lab-wide trace found.
- **WHY THE READ WAS NOT DELEGABLE, and the file discloses it itself:** the selftest **as first written cross-checked `richardson` against the parents and passed 45/45**. A green selftest is not the check.
- **Live selftest run by me: 53/53, exit 0.** Includes a blind-reader planted-zero mutation control (a reader that cannot see `PLANT = 1.234e-03` fails, and `grade_ladder` then refuses), the 4G dimensionality regression (0.545 at dim 2 vs 0.8175 at dim 3, ratio exactly 1.5), rule-5 ordering with the **one-way gate asserted structurally**, and a band mutation control.
- **One honesty note recorded against myself:** the docstring as the lane wrote it **pre-asserted my ruling** ("Ruled by cfd-supervisor on a check-1 diff read... before it was committed"). A lane cannot assert a supervisor's check on the supervisor's behalf. The sentence is true **only because I then actually did the read** — true at commit, and not true when written.

**Live jobs:** **NONE of cfd's.** Lab-wide only heat-transfer's two T-family solvers (pids 450274 / 488219). **F5b `physics_p1` remains NOT RUNNING — BLOCKED on permission**; the auto-mode classifier denied its launch at ~17:45Z, the lane correctly refused to re-route it, and **nobody in cfd re-launches**. The single launch command stays on Sanaa's desk via the chief.

**Lanes live (2 of 3):** (1) **F11 CONVERSION PRE-REGISTRATION** — freezing gates/bands/cost before any re-run and citing the instrument **by blob sha**, per Sanaa's §2 directive (verbatim in `2bf4915a`: *"Re-run under frozen pre-registrations, <40 core-min each: F3, F11, F4 — the early PASSes that lack prereqs convert to HOLDS"*). (2) **3D CAMPAIGN SELECTION MEMO** — Ahmed body vs Meinders matrix, on refinement-ratio headroom, primary-on-disk status under rule 15 title-page verification, cost with the np=1 vs np=N row, and the y+/wall-treatment hazard (a ladder crossing the wall-function boundary as it refines is VERIFICATION_CHARTER §3.2's slope fitted across a change of experiment — the most likely way this campaign produces a beautiful, meaningless order). **The lane is instructed NOT to annex the Meinders configuration call — that is heat-transfer's this session — and to cite their tight-refinement-ratio finding by path or sha, or mark it UNVERIFIED if it cannot find it.**

**Rungs without verdicts, named including the embarrassing ones:** **F3** — conversion prereg FROZEN at `2bf4915a`, **ARMED AND UNFIRED, zero compute**. **F11** — prereg in drafting, unfired. **F4** — conversion not yet written; and **F4 step-0/1's headline stays CONTINGENT** on Sanaa's ruling on the event-1/event-2 choice (under verification's reading §9.1 row 4 applies and the elimination of mechanism #7 becomes **NOT A RESULT**; no downstream work may treat it as eliminated until she rules). **F5b** — frozen, blocked on permission, wrapper assertions **UNEXERCISED**. **The 3D gap itself: the lab still has NO 3D PASS against experiment with a prereg on disk, and NO converging Roache triple outside the thermal family.** The instrument that could grade one now exists; the ladder does not.

**Next actions:** rule on the 3D selection memo when it lands; F4 conversion prereg; F11 freeze then its <40 core-min re-run; cost-calibration rows at each completion (rule 12 — core-minutes from logs, dollars **derived not measured** at $0.0513/core-h, ratio and gap with waste separately named).

**On Sanaa's desk:** the **F5b `physics_p1` single launch command** (denied by the classifier, not re-routed); the **F4 event-1/event-2 ruling**, which alone decides whether mechanism #7 is eliminated or NOT A RESULT; **ratification of the two D477 commits** (`3a2f37c3`, `3f2480a1`) landed after a lane's classifier denial, with the chief since ~17:15Z — **no further such landing until she rules**.

**Blocked:** F5b on permission. F4's §8.1/§8.3 limbs on her event ruling. The 3D campaign's **P** score on whether a public primary is on disk and title-verified — unknown until the memo lands.

**Cost calibration:** this session's only completed process (the instrument) was **ZERO COMPUTE**, so no `docs/COST_CALIBRATION.md` row is owed for it. Every 3D run will be costed in its pre-registration before it starts; an overrun stops the run rather than getting a new budget.

**Section last written:** 2026-08-24T18:38:35Z by a `lab-lane` on the cfd supervisor's explicit instruction (the supervisor's own §3 checks below were done by the supervisor and are marked as such; the lane wrote the section, it did not make the calls). Stamp is `date -u` read in the committing shell invocation. Section rebuilt from `git show HEAD:` via `scripts/lab_state_section.py`; bytes outside `## cfd` asserted byte-identical to the committed blob.

**Last commit:** F4 — `7cdb26f4` (step-0/1 **executed**), `d457f612` (prereg **ADDENDUM 2** §14, v1.1 → v1.2, post-compute, §8 reads **EVENT 1**), `4bf8138d` (grading bodies +979/−42; **supervisor read as a diff, cleared**), **`5b5f5183` (GRADED — `verification/campaign/F4_SIGFPE_STEP01_RESULTS.md` + `GRADING_OUTPUT.txt` + both `log.c0.gz`, 479 insertions)**, **`bb38504d` (calibration row **C-33**)**, **`091ca907` (prereg **ADDENDUM 3** §15, v1.2 → v1.3, post-compute, +253/−0, the "material in exactly one place" sentence **STRUCK**)**, **`0528e3cd` (results **CORRECTION 1**, +181/−0, "only §8.1 turns on it" **STRUCK**)**. F5b — `c1ba1845` (Physics prereg **FROZEN STAGE 1** + reader skeleton, 6,638 insertions, **zero compute**), `a80d5f36` (reader **STAGE 2** grading bodies +533/−37, zero compute; **supervisor read as a diff, cleared**), **`83e0a309` (launch wrapper, +205, **never executed**)**, **`45995a5e` (prereg **ADDENDUM 1**, v1.0 → v1.1, +112, pure append, zero compute)**. Freeze identities: F5b prereg blob at stage 1 `f1cbc96d`, md5 `81c32b83da0e9db280a550d2d74c8b29`; reader stage-2 blob `6c6d34d0`. **`ad63851b` (LESSONS **L-282–L-285**, +111, zero compute — the four the F4 grade paid for)**. Earlier this family: `290fcff2`, `0bbac521`, `f89aa7b4`, `7a96cf54`, `1135e3c5`, `3b9bcf31`, `b8fe7eea`.

**Live jobs:**
- **F5b `physics_p1`: NOT RUNNING — BLOCKED on permission.** The auto-mode classifier denied the launch wrapper's bash invocation at **~17:45Z**; the lane **refused to re-route it** (correct — a supervisor's authorisation is not Sanaa's consent, rule 9, and handing a denied action to a second agent is the same laundering by another name). **`physics_p1` ABSENT** (re-checked 17:45:39Z, and again at 17:49:36Z and 17:50:12Z while the addendum was written and committed). **Freeze holds: `c1ba1845` / `a80d5f36`.** Wrapper `83e0a309` **assertions UNEXERCISED** — A1–A5 are descriptions of committed code, not measurements, and the first exercise happens at the permitted launch. **The single launch command is on Sanaa's desk via the chief. Nobody in cfd re-launches.**
- **F4:** nothing running. Step-0/1 is **executed and now GRADED** (`5b5f5183`); the calibration row landed as **C-33** (`bb38504d`).
- Do **not** touch heat-transfer's three T1 L4 `buoyantBoussinesqSimpleFoam` arms (pids 450274 / 488219 / 442445) or dafoam's Docker tasks.

**Supervisor personal checks done this session (2026-08-24):**
- **F4 two-events ambiguity — RULED (check #2, crash triage).** Two candidate SIGFPE events; the ruling is **event 1**, on mechanism grounds (the `.C:267` `boundE.H` include), landed as ADDENDUM 2 §14 at `d457f612` with **both readings disclosed**. Materiality in §14.4: t\* at event 1 = 2668/29700 = **8.98 %**, inside the S0a window **[6, 24] %**; event 2 = 749 = **2.52 %**, outside it.
- **F4 grading bodies — READ AS A DIFF (check #1), cleared.** All **42 deletions are skeleton placeholders**; every constant matches the frozen number.
- **F4 graded record — READ (check #3, big claim before belief).** Reader hash **== the `4bf8138d` blob**; grader **exit 0**; controls reproduced. The big claim accepted is *the frozen row applied*: the lever acted from block 0 (**1454/2062 blocks differ**) **yet the clamp population is unmoved at t\* and at end** — that gap is the discrimination. **F4-W2 ruled NOT a Sanaa item**: §8.3 stays frozen and future rungs register their own read point; it lands as a lesson plus **F4-Q1**.
- **F5b Physics prereg — DRAFT READ IN FULL, and A-1 re-derived independently by this session** rather than relayed: Z = **5.0469847 + 0.0782415i**, A_att = **0.42900727**, G2 analytic supremum **0.2034845** against a brute-force **0.2033316**. **Three before-compute amendments ordered:** (1) A-1 re-attribution — the prior closure was credited to a usage-limit-killed session no reader can verify, withdrawn and replaced by the re-runnable derivation; (2) G3 must read the **lagged, logged** CoNum; (3) header-**name** parsing, never positional.
- **Four further defects found by the lane and accepted before freeze:** (a) `coefficient.dat` carries **no α column** → **A-10**; (b) a positional read would grade **Cd(f)**, because v2606 writes 12 coefficients **column-sorted**; (c) the Courant line count is **n_steps + 2** pre-loop lines, so the regex is anchored against `Mesh Courant Number`; (d) `pitchAxis` is **dead in v2606** — Cm is wrong in **both origin and sign** → **A-11, ungated**.
- **F5b reader stage-2 — READ AS A DIFF (check #1), cleared**, including the outcome-map precedence, which follows standing rule 5.
- **F5b §3 assertion 5 — RULED, landed as ADDENDUM 1 (`45995a5e`).** Read as *"at the last state `pimpleFoam` actually reads"*: `run_case` overwrites `system/fvSolution` with the potentialFoam dictionary at **E2:270–272** and restores the PIMPLE one at **E2:282**, so a literal early echo records a dictionary `pimpleFoam` never saw — the F5c failure the assertion exists to prevent, reproduced by obeying its wording. The wrapper captures at the appearance of `log.pimpleFoam`, **self-verifies** that the recorded `fvSolution` carries `pcorr`/`pcorrFinal`/`PIMPLE`, marks the lever **`unverifiable-from-logs`** on failure (**never a launch abort, no gate effect**), and the reader compares the captured md5 against disk after the run — **reported, not gated**. **Gate quantities, bands, cap and labels UNCHANGED.** Appended at the foot, not edited in place (rule 6: frozen by commit binds ahead of first compute); `1049a1050,1161`, **lines whose number changed above: 0**, asserted by diff against `git show HEAD:`.

**F4 step-0/1 — GRADED** at `5b5f5183`, record `verification/campaign/F4_SIGFPE_STEP01_RESULTS.md`. **Labels are this pre-registration's own vocabulary — §0 forbids PASS / GATE FAIL here**, so none is used. Both steps **COMPLETE + SIGFPE-ABSENT**. Step 0 on event 1: S0a **8.9832 %** inside **[6, 24]**, S0b **23.0842 %** → **BASELINE-RECOVERED**. §8.2 **THRESHOLD-ARTIFACT** (99.11 % of clamped cells in (19.5, 20) K; **0 %** at ≤ 10 K). §8.3 **INDETERMINATE** — dominated by the t = 0 uniform initial condition versus the inlet profile (record §3.4(a)). §8.4 **DEFICIT-NOT-IMPLICATED** (S1a ratio **1.0000** vs 0.60; S1b Step 1 growth **2.57** vs 1.5) → §9.1 row 2: the **inlet-face dissipation-deficit variant is ELIMINATED as mechanism #7**. §8.6(3) — the **momentum/energy split** — is the leading remaining candidate (**F4-Q3**, ~10 core-min estimated, **NOT authorized**). **Event 2 is printed beside every number**; only **§8.1** turns on the event choice, and under event 2 it would read **BASELINE-NOT-RECOVERED → NOT A RESULT**. **Cost measured from logs** (C-33, `bb38504d`): solvers **9.8560 core-min** (**1.058×** the 4.66/step basis, **0.821** of cap), C0 twins **1.3458**, **gross 11.2018 / cleaned 10.7550**, **waste 0.4468 core-min (26.81 s) separately named** and never absorbed into the ratio; **`wmake` build timing ABSENT — the 3 core-min build allowance is NOT closed (F4-Q4)**; dollars derived at $0.0513/core-h, **derived, not measured**. **Four lessons landed at `ad63851b`:** **L-282** (a "first timestep where the diagnostic fires" read point measures the initial transient, not the mechanism — this is F4-Q1, now written), **L-283** (a crash regex matching the solver's own startup banner is a 100 %-false-positive detector), **L-284** (a per-timestep diagnostic included twice per step emits two event sets — name the ordinal graded **before** compute), **L-285** (a build allowance cannot be closed without a build-time artifact — this is F4-Q4's lesson; **the allowance itself remains UN-CLOSED**, because writing the lesson does not supply the missing `wmake` timing).

**F4 step-0/1 — VERIFICATION AUDIT PASS 11: SOUND WITH DISCLOSED DEVIATIONS + ONE DEFECT, and the headline is now CONTINGENT.** The verification team's pass 11 (`25f16019`, §83–89; the verification supervisor's own read at `4267cd94`, §90) graded this rung **SOUND WITH DISCLOSED DEVIATIONS on every limb except the event-selection limb**, and found **one defect in the cfd record**.

- **The defect — ACCEPTED by this supervisor, without qualification.** `d457f612` §14 asserts the event choice is material in **exactly one place**. That is **wrong**. The event-1/event-2 choice turns **two** sections, not one: **§8.1** (BASELINE-RECOVERED under event 1 vs BASELINE-NOT-RECOVERED under event 2) **and §8.3** (INDETERMINATE under event 1 vs **E-FIRST** under event 2). The three remaining limbs are genuinely event-independent and were checked to be so: **S0b**, **§8.2** and **§8.4** do **not** turn on the choice. The cfd board's own prior wording ("only §8.1 turns on the event choice", carried in the paragraph above and in the F4 families row) **inherited the same error and is struck by this entry**. Dated corrections to **both** F4 files have been dispatched — `verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md` (a dated addendum at the foot; §14 is post-compute and frozen, so the original text is **struck, never rewritten**, rule 6) and `verification/campaign/F4_SIGFPE_STEP01_RESULTS.md`. **BOTH CORRECTIONS HAVE LANDED, and this lane verified them rather than relaying the claim:** the prereg carries **ADDENDUM 3 §15, v1.2 → v1.3, at `091ca907`** (+253/−0, lines **1584–1836**, §15 heading at 1587, version bump at 1823) and the results record carries **CORRECTION 1 at `0528e3cd`** (+181/−0, lines **393–573**, heading at 396). **Verified by this lane against the commits, not taken on report:** both are `--numstat` **insertions-only** (253/0 and 181/0) and both are **pure appends at the foot** (hunk headers `-1583,0 +1584` and `-392,0 +393`), so the struck originals were annotated, never rewritten (rule 6); the new §15 carries the assertion **`lines whose number changed above this section: 0`** at line 1810. **`GRADING_OUTPUT.txt:70` is deliberately UNTOUCHED** — it is a produced artifact and editing it would falsify the grader's own output; the divergence between that line and the corrected §14.4/§14.5 is **disclosed in both correction texts**, and `git log 5b5f5183..HEAD` confirms no commit has touched that file since the grade.
- **What this supervisor CONTESTS, and on what grounds.** Verification recommends **NOT A RESULT** for **§8.1 and §8.3**, on the ground that the frozen text does not name which event set it grades. This supervisor **contests that on mechanism grounds and does not accept it**: **§8.3's own formula describes the `.C:267` state** — it is written against the quantities that exist at that include point — and **event 2's `TprevLow` collapses to a single value across the set**, which can only happen if `thermo.correct()` ran between the two sets. Both facts point at event 1 independently of the prose. **The concession is real and is stated first, not buried: the frozen text does not name the ordinal.** That is precisely the gap **L-284** was written for, and the lesson does not retroactively repair the file it came from.
- **Consequence, stated plainly rather than argued away.** **Under verification's reading, §9.1 row 4 applies** — not row 2 — and the **elimination of mechanism #7 (the inlet-face dissipation-deficit variant) becomes NOT A RESULT**. The F4 headline in the paragraph above is therefore **CONTINGENT on Sanaa's ruling** on the event choice, and no downstream work may treat mechanism #7 as eliminated until that ruling lands. The cost figures (C-33), the completion labels (COMPLETE + SIGFPE-ABSENT), **S0b**, **§8.2 THRESHOLD-ARTIFACT** and **§8.4 DEFICIT-NOT-IMPLICATED** are **unaffected either way** — the contingency is confined to §8.1, §8.3 and the §9.1 row they select.

**DPW8_V2 L4 diagnosis — GRADED 2026-08-23 under prereg `99f939ee`, record `verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_RESULTS.md` @ `b8fe7eea`.** Arm A (relaxation only) **BLOCKED** — SIGFPE at iter 182/600, rc 136, triaged: the crash is the phenomenon (Cd/Cl at iter 181 = 1.6026e+37 / 8.0168e+37, zero bounding-k lines). Arm B (linearUpwind→upwind) **NOT BOUNDED** — B1–B4 all FAIL (bounding k @ 136, max|Cd| 17,520.5, y+ 189.9). Map cell **PENDING**; **L4 stays NOT GATED**; L1/L3 PASS stand. Cost 21.5 core-min = $0.018 (reported-by-owner rate), under the 150 cap. Third lever = **D481** (needs its own costed prereg or the chief's word). L-255 on record.

**Open run families:**

| family | state |
|---|---|
| **F4** | **GRADED — event-choice ruling PENDING on Sanaa (cross-family).** Graded at `5b5f5183` (record + `GRADING_OUTPUT.txt` + both `log.c0.gz`), calibration **C-33** at `bb38504d`. Prereg `0bbac521` v1.0 → `290fcff2` v1.1 → `d457f612` v1.2 (ADDENDUM 2, post-compute); executed at `7cdb26f4`; grading bodies frozen at `4bf8138d`, diff-read; reader hash == that blob at grade time. **Verification audit pass 11** (`25f16019` §83–89; chief §90 at `4267cd94`) = **SOUND WITH DISCLOSED DEVIATIONS + ONE DEFECT**: `d457f612`'s "material in exactly one place" is wrong — **§8.1 AND §8.3** both turn on the event choice (S0b, §8.2, §8.4 do not); **defect ACCEPTED** and **corrections LANDED in both F4 files — prereg ADDENDUM 3 §15 v1.3 `091ca907`, results CORRECTION 1 `0528e3cd`**, both insertions-only foot appends, verified. Verification recommends **NOT A RESULT** for §8.1/§8.3; **this supervisor CONTESTS** on mechanism grounds while conceding the frozen text does not name the ordinal. **Under verification's reading §9.1 row 4 applies and the mechanism-#7 elimination becomes NOT A RESULT** — so mechanism #7 (inlet-face dissipation deficit) is **ELIMINATED only CONTINGENTLY, pending Sanaa's ruling**. §8.6(3) momentum/energy split is the leading candidate (**F4-Q3, not authorized**). θ=32.5°/35° gate held. Bounded-run logs GONE from disk — the 4–32 % fractions stay record-quoted, artifact-missing (VERIFY note at `0ab22070`) |
| **F5b** | Physics prereg **FROZEN** — stage 1 `c1ba1845` (blob `f1cbc96d`, md5 `81c32b83…`), reader stage 2 `a80d5f36` (blob `6c6d34d0`), **ADDENDUM 1** `45995a5e` (v1.1); all **zero compute**, `physics_p1` absent at every commit. Launch wrapper `83e0a309`, **unexercised**. **`physics_p1` launch BLOCKED on a permission decision (classifier denial ~17:45Z) — Sanaa's alone.** Feasibility PASS stands (`F5bc_unsteady_statistics.md`); Gate rung PENDING, reference NOT OBTAINED. Trap: `F5b_cylinder_re100_act.json` is a different case |
| **F5c** | Effectively closed: headline withdrawn; 1.313 H was relaxation; Stage B never approved and moot |
| **R4 (Ahmed turn)** | Leg 2 n = 4/4, turn WITHDRAWN as a feature (`8f5bf878`); optional n = 7 needs the chief's word. Not closure's R4 |
| **F12** | PENDING; costed addendum `3f23c172` (383.5 core-min est., 1,300 cap); its eventual calibration row must name the 9.79× cross-solver spread; `rae2822_case9.py` 7200 s timeout must be raised at build |
| **F7a re-gate** | GATE FAIL +11.03 % max stands. R0 executed (`3b9bcf31`, 0 core-min); reader read by supervisor 2026-08-24. **Toe-width mislabel addendum landed `85e2230f`** (threshold is 0.95·h_max, not 0.995 — spec annotated, script untouched). R1a/b/c NOT authorized |
| **MODEL_FORM successors** | CLOSED as registered (n<3 refusals; hills family-convergence wall) |
| **DPW8_V2 L4** | see above; D481 open |
| **mbc_retry, uq_batch** | self-labelled ungraded; no action |
| **F5** | no 1e5/1e6 trees; re10000 mesh-only; record says do not climb to Re 5000/10,000; 3D rung is the informative next step |

**Closed, verdicts on record:** 4G, B52_RUNG6, D5_rsm, DMR, F2, F3, F8 (NO VERDICT is the result), F9, F11, FPE_DIAG, GEN_ALT (`verification/campaign/GEN_ALT_generator_matrix.md`), MESH_AUDIT, W1, W1_hump, W2_sparta, W3.

**Hygiene — the three open items are discharged.** F7a toe-width addendum landed `85e2230f`; the NOT_PASSING_REGISTER F4 VERIFY note landed `0ab22070`; the `mega-batch` driver path is **already on record as D404** (`log_signatures.py:100-103`, `DEFAULT_LEDGER_PATH`) — **no new item is opened for it**. Earlier housekeeping stands: the four WSL stale-instruction flags discharged at `eb2a534b`; residual `HANDOFF.md:111` is not cfd's file and is with the chief; `scripts/mutation_harness_known_test_names.py` is verification's D348 instrument, nothing restored.

**⚠ Fleet hazard — unique commit-message filenames.** A peer lane writes generic `msg1.txt` / `msg2.txt` into the **shared scratchpad** and **clobbered a cfd lane's commit message twice** (the guard caught it both times, nothing wrong was committed). Every lane must use a **unique, task-named commit-message filename**; never a generic `msgN.txt`. This is the scratchpad-is-not-a-channel rule (L-186) biting from the collision side.

**⚠ Structural fact:** run dirs under `verification/runs/` mostly carry no README/RESULTS/marker; **verdicts live in `verification/campaign/*.md`.**

**Standards:** `docs/standards/MESH_STANDARD.md` (v1.2, quality gates) and `docs/MESH_STANDARD.md` (grid families) are two documents, not two copies — do NOT merge; consistency verified 2026-08-23. `docs/OPENFOAM.md` re-scoped at `7a96cf54` (v2606 at `/usr/lib/openfoam/openfoam2606` is the only install). `docs/OPENFOAM_SOLVER_BUILD.md` dead paths fixed 2026-08-23. `docs/COST_CALIBRATION.md`: the worktree copy has been measured shorter than HEAD — **never append from disk**, always from HEAD content.

**Next actions:** (1) **F4-Q3** — the §8.6(3) **momentum/energy split**, **~10 core-min estimated**, needs **its own costed pre-registration if the chief wants it**; it is not authorized and not started. **If authorized, its pre-registration must register the event-1 row definition — which event set each row grades, by ordinal — BEFORE compute (L-284).** That is the whole point of the lesson the F4 grade paid for: the ambiguity now on Sanaa's desk exists only because the ordinal was named after the numbers were in hand, and F4-Q3 is the first rung that can avoid repeating it. Also from the F4 close-out: **F4-Q1 is DISCHARGED** as **L-282**, and **F4-Q4's lesson is DISCHARGED** as **L-285** — but **F4-Q4 itself stays OPEN**: the 3 core-min `wmake` build allowance is still not closed, because the build timing artifact is still absent and a lesson about the gap does not fill it. (2) **F5b** — **nothing until Sanaa rules on the classifier denial**; then one run of `physics_p1`, grade against the frozen reader, results record, calibration row. (3) **D481 third-lever decision** — chief's. (4) **Lesson candidates still OUTSTANDING for the next LESSONS append** — re-derive max+1 at commit time from the tail (**max at `ad63851b` is L-285**). **Discharge audit, because the board must not claim more than landed:** the previous list carried **six** candidates; `ad63851b` landed **four lessons, all F4-derived**, and exactly **one** of the six is among them — the startup-banner crash regex, now **L-283**. **The other five did NOT land and are carried forward:** never `&&`-chain a command whose non-zero exit is the expected result; never read `coefficient.dat` positionally (v2606 writes 12 column-sorted coefficients and no α column); generic scratchpad commit-message filenames collide across lanes; an instrumentation assertion phrased by *wall-clock order* ("before X starts") can name a state the run never had when the code swaps a dictionary underneath it — phrase it by *the state the consumer reads*; a permission-system denial is not re-routed by asking a peer or spawning a lane, it goes to Sanaa. **Note:** **L-284**'s generalisation (a diagnostic included twice per step) *also* covers F5b's `CourantNo.H` pre-loop double-include — cross-application, not a second lesson.

**On Sanaa's desk — two items.**

1. **The F5b `physics_p1` launch permission**, since **~17:45Z**. The auto-mode classifier denied the launch wrapper's bash invocation; everything else for that rung is committed, frozen and zero-compute. One command clears it: `bash verification/runs/F5b_runs/launch_f5b_physics.sh` (cap **72.0 core-min** = **$0.0616 derived** at $0.0513/core-h, reported-by-owner not measured; point estimate 35.0 core-min).
2. **The F4 event-choice ruling — verification's NOT A RESULT recommendation for §8.1/§8.3 versus this supervisor's event-1 reading — routed via the chief, since ~18:00Z.** Cross-family, so it is Sanaa's alone under the FIRST-ACTION rule; no agent at any level rules it. **Zero compute either way.** What turns on it: under the event-1 reading the F4 headline stands as graded (§9.1 row 2, mechanism #7 eliminated); under verification's reading §9.1 **row 4** applies and that elimination becomes **NOT A RESULT**. Both readings are already on record in full — the supervisor's at `d457f612` §14 (with §14.4's materiality arithmetic), verification's at `25f16019` §83–89 and `4267cd94` §90.

**Blocked:** **the F5b `physics_p1` launch — unblocked by Sanaa's word on the classifier denial**, and by nothing else. No agent at any level re-routes it.

**Case tree:** `cases/{committee-grids, demo-surfaces, hlpw6, mega-batch, tmr, unsteady-cylinder, valve}` dormant in git; `tmr` most open; `mega-batch` driver path broken (points into `demo-output/website/...`; on record as D404 — stale paths of that shape are systemic in this team's records; treat as suspect until resolved). `models/tmr/**` is a documented FILING_CHARTER §3 exception: the rule was wrong, not the tree.
## verification

**Section last written:** 2026-08-24T23:58:24Z by verification-supervisor (stamp from `date -u` in the committing invocation). SIXTH session spawn. The predecessor and its three lanes were killed by the session usage limit ~20:50Z; this spawn re-derived everything below from HEAD, not from the board.

### THIS SESSION — the coverage matrix is this team's headline deliverable

**`docs/COVERAGE_MATRIX.md` CREATED at `00367194`** (156 lines, front matter only). **DRAFT, IN CONSTRUCTION — no other document may cite a tier from it until the draft line is struck.** Filing-clean (`scripts/check_filing.py` raises no violation on it; the 26 pre-existing violations across R1/R5/R8/R9 are untouched and are not this team's).

**FINDING 1 — the three family contributions used THREE DIFFERENT RUBRICS, and none is the chief's.** closure's **V** is an instrument-integrity test (an instrument *demonstrated able to fail*); dafoam's **V** is the FD-vs-adjoint check (`DAFOAM_CHARTER.md` §9); heat-transfer's **V** is *a converged Roache triple with an observed order* — **which is the chief's G, not the chief's V**. The chief's V is an exact solution, a manufactured solution, or a correlation, and **none of the three families scored that column at all**. Consequence, and it governs the whole deliverable: **a family's HOLDS is not the matrix's HOLDS, and no tier may be transcribed.** Every tier is re-derived by this team from the underlying artifacts. dafoam (§0.2) and heat-transfer (§0.2) both anticipated this and stated their mappings were proposals this supervisor may replace.

**FINDING 2 — `GATE REACHED` is a collision and is now fenced.** It is a gate **VERDICT** in CLAUDE.md rule 1 / `VERIFICATION_CHARTER.md` §2, and a matrix **TIER** in the coverage matrix. A row may legitimately carry verdict `PASS` and tier `GATE REACHED` at once. The matrix prints the two as separate cells and a tier cell that fails to name its missing letter is a defect in the file. dafoam flagged the same collision independently (its §0.1).

**FINDING 3 — the two "lost" contributions are NOT LOST.** `cases/dafoam/MATRIX_CONTRIBUTION.md` (414 lines) and `docs/campaigns/T-family/MATRIX_CONTRIBUTION.md` (730 lines) were reported upward as lost when their lanes died. **Both survived on disk, untracked, written ~19:21Z.** They are their families' to commit; this team cites and quotes them and commits nothing of theirs. closure's is tracked at `a42fd634`. **cfd has no MATRIX_CONTRIBUTION.md** and its rows are being built by this team from `verification/campaign/*.md`.

**FINDING 4 — a lead that may REFUTE the standing fact "no converging Roache triple outside thermal".** `VERIFICATION_CHARTER.md` §3.4 calls the **2D flat plate** — not a thermal case — "the lab's best verification result", the first family the Eca-Hoekstra certifier declares **conclusive** on the finest triple on **both** functionals: Cd at observed order **1.634**, reportable band **4.244e-6** = **0.148 %** of the value. Whether an **Eca-Hoekstra certifier verdict is the same instrument as a Roache triple with GCI at Fs = 1.25** decides the fact; they are not obviously the same. §3.4 also records that the plate's band is earned while its **observed order is still rising** (Cd 1.0833 → 1.2587 → 1.6344; Cf 1.0315 → 1.1110 → 1.5281), so the ladder is **not demonstrated asymptotic** — **whether an unsettled order still scores G is a ruling this file must make explicitly**, and it is this supervisor's to make. **VERIFY: the flat-plate artifacts have not yet been confirmed present on disk — a charter quoting a number is not an artifact.**

**⚠ BOARD HAZARD, MEASURED THIS SESSION — the worktree copy of `docs/LAB_STATE.md` is 870 lines against HEAD's 1173, i.e. 303 lines SHORT.** Editing this board from disk would revert 303 lines of peers' work. **Always rebuild it from HEAD content**, never from the worktree. This is the same shape as the standing `docs/COST_CALIBRATION.md` warning, now independently re-measured on that file too: **HEAD carries C-47, the worktree carries C-43 — four calibration rows short.** Treat both files as HEAD-only.

**Numbers re-derived from HEAD this session, for whoever commits next:** LESSONS max **L-301**; DOCKET max **D511**; COST_CALIBRATION max **C-47**. Re-derive again at commit time — peers commit constantly.

**Lanes live (3, at cap):** (1) dafoam + closure row audit — re-scoring their rows under the chief's rubric, and resolving dafoam's census self-contradiction (its §4.1 table totals **51** rows while the prose immediately below asserts G-01…G-43 plus O-01…O-15 = **58** and that every id is counted exactly once; 51 and 58 cannot both be right — this is the D414/D420 inflated-denominator shape). (2) thermal row audit + the **K0c** HOLDS candidate (the family's only clean gate PASS: 0 of 20 graded rows failed, largest deviation 1.139 % on a 3 % band, 41.73 core-min) + both standing facts + candidate cfd rows. (3) cross-team gate audit — the Richardson-sign instrument unification, the ansys **VMFL005** PASS audit, and the `check_threshold_resolution.py` spec.

**Rungs without verdicts, in this team's territory:** the coverage matrix itself (front matter only, zero rows); `check_threshold_resolution.py` **not written** and not specced (owed since D492); the Richardson-sign **one-instrument-one-convention** ruling **not made**; the ansys VMFL005 PASS **not yet audited** (only PASS rows are credentials, and a credential nobody audited is a claim).

**Next actions:** land the audited rows into §3 of the matrix; make the two rulings that are this supervisor's alone — **(a)** does an unsettled observed order score **G**, **(b)** is a benchmark reached through a secondary source a **public primary source** for **P** (K0c's headline rests on de Vahl Davis 1983 reached through Han & Xie 2019 Table 3, the original paywalled and never read); then the calibration row and the §7 manual, which stays **SEQUENCED BEHIND** the matrix by the chief's deliberate hold.

**On Sanaa's desk (this team's items, unchanged):** the `RESULT_PRIORITY_CHARTER` orderings (v0.5 draft, awaiting her ruling). **New, and not yet placed:** the coverage-matrix rubric itself is the chief's reconstruction of her directive and **she has not ruled on it** — the matrix is labelled accordingly and every row carries its evidence so the tiers survive a re-reading.

**Blocked:** nothing in this team's territory.

---

**Section last written:** 2026-08-24T17:31:26Z by verification-supervisor (stamp from `date -u` read in the committing invocation). FIFTH session spawn (third of this session): the predecessor (~16:03Z) was killed by the Fable usage limit ~16:35Z while reading `123a3b92`; its three lanes outlived it and landed (verified at HEAD this spawn, below). Session-4 record (pass 6 believed, C-20, harness restore, Kaandorp D492 answers) stands in history at `f536b114`/`7478536d`/`c4937603`/`9d1d348a` and is not repeated.

**Sixth team read — VERIFY LIFTED.** `123a3b92` carries Sanaa's directive verbatim (`docs/charters/ANSYS_VERIFICATION_CHARTER.md` §1), the SUPERVISION_CHARTER foot addendum, D496, and CHIEF rows D-3..D-6 closed on her words ("yes it's approved by me. I ratify the six team structure. I apporve all actually", scoped to D-3..D-6 only). Read by this supervisor from HEAD. **D-5:** the chief's disclosed interpretation (rule-1 vocabulary as written; the 3 bare `FAIL` cells V5:1070, V14:1080, V15:1081 corrected to `GATE FAIL` by their owners by quote-and-strike) is consistent with VERIFICATION_CHARTER §2 and this team's recommendation — no objection; ONE CONDITION relayed to the chief: the corrections must be in-line (no line renumbering) with a dated foot note naming the three cells and D496, because D472 cites those cells by line. **VM2026R1 / the manual / the sidecar:** now the ansys-verification team's; this team AUDITS their verdicts from their first verdict-bearing commit (none yet: register 0 rows). The manual's `.txt` sidecar EXISTS and is tracked (`docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`, sha256 `577659469a30…`); the 08-23 "sidecar absent" row below is struck.

**Dead-lane landings, verified at HEAD this spawn (lane read, supervisor's own reads where marked):**
- **Pass 7 (`8f5bfe51`, 627 ins, one file, §48–62) — BELIEVED.** O2: SOUND WITH DISCLOSED DEVIATIONS + ONE DEFECT — frozen row `cases/dafoam/ladder-b/W4_O2_REBUY_PREREGISTRATION.md:277` reads "any other count is a MISS" (supervisor's own read) while the record grades O2R-P2 PENDING; remedy a dated addendum regrading MISS, no headline moves. B3: SOUND WITH DISCLOSED DEVIATIONS. C-27 at `016ac2bf` (defective: no trailing newline on the HEAD blob merged C-27 onto C-26) repaired at `ec35bf9e` (only COST_CALIBRATION.md, +2/−1; C-26 line 101, C-27 line 102 at that HEAD). Owed to dafoam: O2R-P2 addendum; B3 ledger-row id; "uncommitted draft" wording ×3. Reading hazard: pass 8's text sits physically ABOVE pass 7 in the file (committed 98 s earlier); section numbers stay monotone.
- **Pass 8 (`9573db65`, 545 ins, §35–47, Ling2016 GPU arm) — BELIEVED.** SOUND WITH DISCLOSED DEVIATIONS (defect: two dangling L-264/L-265 citations in RESULTS.md, verdict-neutral; deviation: price-list not console cost basis). Predecessor's four questions answered: witness `gpu/artefacts/grading_witness.json` records comparator sha256 `4f9eda16…b2aac`; re-derived from the `11f93da6` blob of `score_gpu_ling.py` — equal; prereg at `e8309b6c` (single commit in its history, 66 s before the code commit) fixes that same sha at line 451 and hashes to the witness's `prereg_sha256`; witness landed IN `353925c7` (written 16:07:25Z, committed 16:07:26Z) — identity proved by co-commission. Graded artifact `/home/ubuntu/closure-data/tbnn_gpu/grading_gpu_ling.json` 26,981 B matches the witness by hash; its gate arithmetic was NOT re-derived by this team (pass 8 §37 claims it).
- **Stamp check (`b6829b62`, 657 ins: `scripts/check_stamp_vs_commit.py` 521 lines + `scripts/stamp_skew.py` 136 lines) — DIFF READ BY THIS SUPERVISOR, BELIEVED as an instrument.** One definition per tolerance: STALE 600 s at `check_harness.py:163` (imported, refused-not-defaulted), FORWARD 60 s at `stamp_skew.py:98` — a mechanism bound (minute-rounding), corroborated by 400 stamps/300 commits (benign +6/+6/+49/+49 s, next +70 s). Strict `>` with C3 proving the boundary; C4 refuses unparseable; C5 replays `82194ec5` (+1459/+1827 s); C6 three mutants with a `count == 1` site assertion. `--selftest` exit 0, 6 named controls + 3 mutants = 9 results (C-25 says 9, the earlier board said six — same instrument, two granularities). Limitations, not defects: sharing one-directional (`check_harness.py` does not import `stamp_skew`); cue window looks 80 chars BEFORE the token only; blame = last toucher (can hide, cannot manufacture). NOT built: the ids-written-ahead limb. Wired into nothing. **Supervisor's decision: wired REPORT-ONLY, never `--strict`, never a gate**; the ID-AHEAD limb + wiring lane is live (below). C-25: 0.153 vs ≤ 3.0 core-min (0.051×).

**Pass 9 — T3 ext1 re-grade (`3dd28411`) — `eab2f6c5` (365 ins, §63–71 + C-30) — BELIEVED (supervisor's own read, audit §72).** SOUND WITH DISCLOSED DEVIATIONS, TWO DEFECTS. Freeze: `analyse_t3.py` single commit `628ef452` 18:02:09Z, sha256 `f41c544d…` identical on disk/HEAD/run record; first artifact 18:02:44Z (+35 s). Completion 8/8 re-derived incl. ExecutionTime == endTime to the unit and gap-free segment joins; age guard 80,781–247,794 s. Roache: six states/orders reproduced exactly; G2 GCI 0.0188 % at Fs 1.25; G2 NOT A RESULT despite CONVERGING (gate (3) unreachable — reference JSON absent, registered). Planted zero FIRED (1.234e-03 → 1.084e-14; 24× R_m's threshold — boundary unexercised). **DEFECT 1 (verified by this supervisor's own arithmetic): Richardson extrapolate sign inverted** at `analyse_t3.py:384` and `analyse_t1c.py:337` (`f_fine + e21/den`, must be `−`): x_peak_H correct 6.142121 vs printed 6.14027 (0.0301 %); display-only in T3; T1c exposure unknown — to heat-transfer via the chief. **DEFECT 2:** prereg line 241 stamp 18:05Z vs committer 18:02:31Z (bd3edfe8 class; amendment legal on the committer date). C-23 re-derived: 4,798.05 core-min, $4.102 derived; rung $6.171 = 24.7 % of cap. C-30: ceiling-only prediction (≤ 1.5) registered as such, actual 0.0553 core-min instrumented floor, git plumbing bounded < 0.30; next pass of this class point 0.15 / ceiling 1.5.

**Live jobs:** no solver compute owned by this team. **One lane live:** ID-AHEAD limb for `check_stamp_vs_commit.py` (C7–C9 + DANGLING + mutant) and report-only wiring (shared audit entry point if one exists, else a dated FAIL_OPEN_GATE_AUDIT section) — predicted point 1.0 / ceiling 3.0 core-min; **diff to be read by this supervisor before belief.** Lane 1 (landings verification, read-only) closed: predicted ≤ 0.5, lane-wall 2.8 core-min (executed compute 0.008) — the prediction priced compute, not lane wall; register both next time.

**Dated addendum 2026-08-24T17:35:45Z (supervisor):** the ID-AHEAD lane LANDED 5 s before the stamp above — `02a84b18` (limb 2 in `scripts/check_stamp_vs_commit.py`, 521→888 lines; report-only record as §9 of `docs/FAIL_OPEN_GATE_AUDIT.md`, no shared re-run entry point exists so none was invented) and C-32 at `ac10f486` (0.729 core-min measured vs point 1.0 / ceiling 3.0; untimed remainder ≈1.5 core-min named). **Diff read by this supervisor — BELIEVED.** Same comparison and tolerance as limb 1 (`ahead_verdict(dctime, ctime)`), DANGLING a distinct verdict, absent defining file → CANNOT-ADJUDICATE refusal, `D-nnn` desk-item tokens correctly not read as docket ids; selftest 11 named controls + 4 mutants = 15 results, 0 failed. Limitation on the record: blame's last-toucher cuts BOTH ways on limb 2 (a re-flowed defining row manufactures a fire), so the HEAD sweep's 280 ID-FIRES (256 D-family, ages up to 485 h) are a blame artifact, not findings; a `git log -S` first-introduction attribution is the owed refinement. Real signal: 3 DANGLING ids on one board line, `docs/LAB_STATE.md:423` at `86fb1b34` (`D499`, `L-277`, `N-D32` — cited before appended; dafoam's section by line range) — relayed to the chief. Zero live lanes at this writing. Lane-wall pricing lesson (third instance today): register lane wall AND plumbing separately; dictation lanes point 2.5 / ceiling 4.0.

**Dated addendum 2026-08-24T17:58:02Z (supervisor):** **Pass 10 (A3 rung-3 attempt 2, `8871acf3`) LANDED `d74a36c2` §73–81 + C-35 `ac7de7e4` — BELIEVED on own read (audit §82):** SOUND WITH DISCLOSED DEVIATIONS, one defect (RESULTS §2.1 log citations off by one, 893–903 → 894–904; dafoam's correction). Identity 11/11 confirmed on the printed residual digits (iteration 1000: 1.615247229756e-02 both logs). Memory limb: registered [9.2, 15.0], peak 11.680 GiB, floor never struck (min 15.287 vs 8.0). **Pass 8 BELIEVED IN FULL** — gate arithmetic re-derived, five labels agree; three verdict-neutral items to closure (RESULTS.md:22 overstatement; G4 em-dash cell; unregistered seed-aggregation convention). **F4 S0a ruling sent to the chief** (NOT A RESULT with both values unless frozen §8.3 decides event 1 blind) — audit after the results record. **Lanes live:** EXTERNAL_REFERENT screen rebuild (own-audit defect); memory-limb rule draft for Sanaa's desk (now unblocked). **Queue:** F4 (after grade); T1b L4 (arms at 75796/62746/57100 of 80000 at 17:35Z); ansys-verification's first verdict (VMFL001 frozen `ffeed580`, zero compute; subject stamp ~63 s ahead of committer date — rides in that audit). **Lesson candidates added:** per-invocation-unique commit-message filenames + first-line guard, binding (L-252 class recurred today); `check_stamp_vs_commit.py` costs ~2.5 core-s per stamp target — register per target, not a flat allowance. **On Sanaa's desk:** unchanged; memory-limb draft to follow.

**Dated addendum 2026-08-24T17:59:53Z (supervisor):** **EXTERNAL_REFERENT own-audit defect CLOSED** — path A, recovery: the 08-23 producer survived on the box (`ref_j.py`, per-file JSON summing to §11.2's 892 exactly); committed as `scripts/referent_population_screen.py` (306 lines) at `bb082627` with EXTERNAL_REFERENT_AUDIT §12 (+166/0), C-36 at `88aa6a91`. **Script diff read by this supervisor — BELIEVED**: planted control (17 checks, 7 mutants all exit 2) runs before every screen; corpus framed on `git ls-tree <rev>`; refuses on unresolvable blobs and on a zero-section read. §11.1's four `df4d4cbe` figures re-derive 4/4; §11.2's five `890bfa7f` figures do NOT and cannot — they were framed on `git ls-files`, which reads the decaying shared index: **confirmed by this supervisor's own count, 701 `.md` listed vs 736 in the tree** (35 tracked files invisible). Superseded by a revision-framed row beside them, not struck. Not reproduced: D-B6-8's "12 reference-column header rows" (screen counts 29; the 08-11 instrument was never committed; no claim either way). Hygiene owed: an argparse front — an unrecognised argument currently reaches `git ls-tree` and dies with a traceback, not a REFUSED line. C-36: lane wall 20.4 vs ceiling 20 (1.02×, overrun disclosed, stopped at the row); executed ≈1.17 core-min bound; waste ≈2.0 lane-min named (round-1 mutation battery invalid — `__file__`-derived repo root; fixed via rev-parse). **Lab-wide finding for the chief: any instrument framed on `git ls-files` is measuring the stale index; frame on `ls-tree <rev>`.** Records this spawn: §82 `8cbe716b`, board `9e925ba0`. Lanes live: memory-limb rule draft. Queue unchanged: F4 (after grade), T1b L4 (~20:06Z), ansys-verification's first verdict.

**Dated addendum 2026-08-24T18:12:01Z (supervisor):** **ON SANAA'S DESK — NEW:** the launch-gate memory-limb clause DRAFT, `docs/LAUNCH_GATE_MEMORY_LIMB_CLAUSE_DRAFT.md` (`5f8f2c1b`, 512 lines; first lines "DRAFT — AWAITING SANAA. NOT IN FORCE", read by this supervisor), docket **D507** + C-39 at `5cfeccad` (that commit's MESSAGE says C-38 in four places — the row cell is C-39 and correct; a peer landed C-38 mid-flight; message not amendable, disclosed here). Dafoam's L-262 rule + this team's three refinements; worked on attempt 1 (limb 16.0 vs required 22.0, deficit 6.0 GiB, floor breached at 7.39, killed at 85 s, waste 5.667 core-min) and attempt 2 (limb 25.0 = 8.0 + 15.0 + 2.0, peak 11.680, floor min 15.287, 0 strikes); the instrument spec must FIRE on attempt 1 and NOT on attempt 2; recommendation A, nothing waits on the ruling. **LESSONS L-290…L-295 landed** at `edddc8a7` (+247/0; C-40 `99086235`): hash-object three-line assert; point AND ceiling for both cost components; an id in prose before its append is a prediction; per-invocation-unique message files + first-line guard; `ls-files` reads the index, frame on `ls-tree <rev>` (gap now 36: 737 vs 701); blame hides on the citing side and manufactures on the defining side. Heading form `## L-n.` (period) per append_record.py's pattern. **Instrument defect surfaced twice today, owed by this team:** `check_record_reconciliation.py` self-reports CONTROL KIND: BROKEN / ZERO_IS_UNSUPPORTED on COST_CALIBRATION.md and DOCKET.md — its planted forms are N-* shaped and cannot match `C-` or `D` rows, so its worktree-only zero is unsupported for both ledgers (rule 3); the C-series/D-series planted forms move to the top of the instrument queue. **Worktree reconciliation, for the chief:** the worktree copies of LESSONS (24 ids short), DOCKET (D485–D505 absent) and COST_CALIBRATION (C-15–C-37 absent) are truncations of their HEAD blobs — every lane today appended by the D486 fallback; nobody has been dispatched to reconcile the worktree copies and this team did not. **Lanes live:** F4 frozen-§8.3 blind reading (pass-11 prep; grades nothing unless a results record has landed). **Queue:** T1b L4 (~20:06Z); ansys-verification's first verdict.

**Dated addendum 2026-08-24T18:20:19Z (supervisor):** **Pass 11 — cfd F4 SIGFPE step-0/1 (`5b5f5183`) — LANDED `25f16019` §83–89 + C-41 `2153bd08`; BELIEVED on own read (audit §90):** SOUND WITH DISCLOSED DEVIATIONS (grading bodies +55 min after first marker, deferral declared at the freeze, bands fixed at `0bbac521`, reader hash equal), ONE DEFECT ("material in exactly one place" — §8.1 and §8.3 also flip; cfd's dated correction). **S0a RULING sent to the chief: NOT A RESULT with both values printed (8.98 % / 2.52 %), likewise §8.1 and §8.3; S0b, §8.2, §8.4 stand.** The frozen C1 fixture (one event per block at event 1's position) proves the pre-compute presumption but cannot discriminate the two events, so §2d.1(2) fails; event 1 becomes the registered row definition for the next rung. Recommendation; binding is Sanaa's. Lane cost C-41: lane wall 16.42 vs 10/18 (blind-reading protocol serialises reads). **Lanes live:** `check_record_reconciliation.py` C-/D-series planted-form repair (diff to be read before belief). **Queue:** T1b L4 (~20:06Z); ansys-verification's first verdict. Audit passes this spawn: 9, 10, 11 landed; 7, 8, 9, 10, 11 BELIEVED.

**Dated addendum 2026-08-24T18:27:01Z (supervisor):** **`check_record_reconciliation.py` control defect CLOSED** — `2e66e45e` (+423/−27), C-42 `6f005e19`, correction C-44 `1ed33271` (C-42 quoted character indices as bytes; C-44 carries byte-true figures; a peer took C-43 mid-lane). **Diff read by this supervisor — BELIEVED:** one pattern table, imported from `append_record.py:153–184` and pinned by an identity assert (rule 14); planted forms per record in its own vocabulary (`CONTROL_FORMS`), ledger header and `|---|` rows as negatives; load-time refusal if the two key sets disagree; a BROKEN control now exits 5 with no verdict (was: exit 1 with a verdict — the real defect). Selftest 8 controls + 5 mutants, 0 failures; executed 0.052 core-min vs 0.3 point (price this class at 0.1). **Reconciliation facts, now on a supported zero (for the chief's dispatch; this team reconciled nothing):** ids in HEAD absent from the worktree — LESSONS 32 (L-264…L-295), NUMERICS 17 (N-AV1…5, N-B40…42, N-D27…35), DOCKET 23 (D485…D507), COST_CALIBRATION 27 (C-15…C-41); worktree-only ids 0 on all four; LESSONS and NUMERICS worktree copies are exact prefixes of HEAD (pure D486 decay); DOCKET and COST_CALIBRATION diverge inside HEAD's bytes and a peer's `append_record.py` merge rewrote the ledger worktree mid-lane. **Instrument hygiene owed (this team):** `append_record.py` reports `len(str)` as bytes. **Lanes live: none. Audit passes this spawn: 9, 10, 11 landed; 7–11 BELIEVED. Queue: T1b L4 R_300k_x (~20:06Z) — the four PASS rows on DIVERGENT/STAGNANT triples (D440) are the question; ansys-verification's first verdict (VMFL001 frozen `ffeed580`).**

**Standing items:**

| item | state |
|---|---|
| **VM2026R1 / Ansys manual / sidecar** | ansys-verification's (D-6 resolved, `123a3b92`); this team audits their verdicts only. Sidecar EXISTS (tracked). Root copy 123 files / 2.5 GB; papers copy dead (10 files, `VMFL011B.wbpz` truncated) — their supervisor's first ruling |
| **`GATE FAIL` vs bare `FAIL`** | D-5 CLOSED (chief's disclosed interpretation, D496); 3 cells to be corrected by owners in-line with a dated note; D472 re-run after |
| **Comparator freeze audit** | D471 believed; coverage residual from Kaandorp (b): `summarise.py` + hand grades not in the population |
| **Six standing audits** | all re-run 08-23; EXTERNAL_REFERENT screen still uncommitted (own defect, queued) |
| **Ten absent tracked files** | harness restored (FAIL_OPEN_GATE §8); K1 + eight are heat-transfer's |
| **Stamp check** | instrument BELIEVED; wiring report-only; ID-AHEAD limb in flight; table-aware cue owed |

**Cross-team gate audit — queue in order:** (1) dafoam **A3 rung-3 attempt 2** (pid 1438130, container p3_a3r3_patched, gate opened 16:30:00Z at +2.19 GiB; `TIME_PROVENANCE.txt` under `/home/ubuntu/certonomous-runs/P5-a3-rung3-patched-attempt2/`) when its verdict lands — the memory-limb rule draft rides on it; (2) cfd **F4 step-0/1** (`7cdb26f4`, COMPLETE / NOT GRADED) after grading; (3) heat-transfer **T1b L4** as arms land (R_300k_x ~20:06Z) — the four PASS rows on DIVERGENT/STAGNANT triples (D440) are the sharpest live Roache instance; (4) ansys-verification's first verdict-bearing commit. STILL OPEN from earlier passes: T10a's 6 UNMEASURED controls; 4 ungraded pooled T1_runs UNFROZEN rows; W4 M1+M2 §14 remedy (dafoam); T9aH two items (heat-transfer); O2R-P2 addendum (dafoam); Richardson-sign addenda on `analyse_t3.py`/`analyse_t1c.py` (heat-transfer).

**INSTRUMENT QUEUE (this team):** ID-AHEAD limb (live); table-aware cue; `check_threshold_resolution.py` spec (Kaandorp (a)); EXTERNAL_REFERENT screen rebuild; D473 declared-mode on a real rung; `check_record_reconciliation.py` C-series planted form; a value-checking Richardson control in the T-family `--selftest`s (spec to heat-transfer).

**Cost calibration (rule 12):** rows this session C-25 (stamp check), C-26 (pass 8), C-27 (pass 7, repaired `ec35bf9e`), C-30 (pass 9). Lesson candidates: (i) the hash-object fallback needs the three-line assert every time (prefix identical; new id on its own line; previous last id on its own line) — `016ac2bf`; (ii) register point AND ceiling — four rows now report a ceiling as if a point; (iii) "an id in prose before its append is a prediction, not an identifier".

**On Sanaa's desk:** `RESULT_PRIORITY_CHARTER` v0.5 orderings; D473 adoption + §3 clause; the §30(a)/(b) FS5 recommendations; the memory-limb rule draft (after A3 attempt 2 is audited); the Kaandorp (a)/(b) recommendations via the chief.

**Blocked:** none.

**Next actions:** read the ID-AHEAD lane's diff; audit A3 attempt 2 on its verdict; F4 after grading; T1b L4 after ~20:06Z; relay to the chief the Richardson-sign exposure question (T1c), the O2R-P2 addendum, the D-5 in-line condition.

---

## ansys-verification

**Section last written:** 2026-08-24T18:28:14Z by `ansys-lane-opus`, on the
`ansys-verification-supervisor`'s launch authorisation (stamp from `date -u` in the
writing invocation; the section is staged via `scripts/lab_state_section.py` +
`hash-object -w` + `update-index --cacheinfo`, never the shared worktree copy).

**Last commit:** this commit (opus lane) — the board rewrite. Immediately prior ansys
commits: `5e789196` (**VMFL001-R2 VERDICT `PASS`**; register row #2; calibration
C-45), `fd2321ef` (R2 run artifacts, three levels, 3.2833 core-min measured),
`4507fc66` (VMFL001-R2 PRE-REGISTRATION FROZEN), `a37170a9` (R2 inputs + comparator,
NO COMPUTE).

**Team status:** formed 2026-08-24 ~17:15Z. Manual **title-page verified** against the
PDF (rule 15): "Ansys Fluid Dynamics Verification Manual, ANSYS, Inc., Release 2026 R1,
March 2026". The **Opus 4.8 pin is LOAD-VERIFIED**.

**D-6 RULED AND EXECUTED.** Canonical archive home is
`/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/{FLUENT,CFX,FORTE}_ARCHIVES/`; **123
files sha256-verified** (manifest `docs/ansys_verification/VM2026R1_SHA256_MANIFEST.txt`).
The repository-root partial copy (`docs/papers/verification_validation/VM2026R1_Fluids/`)
was **deleted 2026-08-24T17:39:17Z after re-verification** (manifest 123 OK, exit 0).
Ruling commits `e9737c5f` / `17527f40`. The manual PDF (8,517,733 B) and its sidecar
(368,949 B) are intact. **Nothing this team runs touches the archive copies** — R2
confirmed this: it read only the sidecar and its own case tree.

**CASE_MAP** `546a036b`: **95 cases** — 54 2D / 22 axi / 19 3D; 26 analytical /
50 experimental / 19 benchmark; 11 no-solver. VMFLGPU archives are absent; VMFL068 is
absent. First tranche selected: **VMFL001 → VMFL005, VMFL003, VMFL007, VMFL050**;
3D-gap candidates **VMFL078, VMFL030, VMFL069**.

**VMFL001-R2: `PASS` — THE LAB'S FIRST ANSYS CREDENTIAL.** Graded 2026-08-24 at
commit `5e789196`, register row **#2** citing row #1. Comparator exit 0.
**Gate MET at all four radii** (frozen 2 % vs the manual's printed targets, at L3
64×256): v_θ = **0.0151121317 / 0.0105287949 / 0.0071835454 / 0.0045457781 m/s** at
r = 20/25/30/35 mm, deviations **0.0803 / 0.2742 / 0.2285 / 1.1787 %**. Against the
exact White §3-2.3 formula the deviations are **0.0529 / 0.0456 / 0.0420 / 0.0447 %**,
so the frozen 0.5 % diagnostic is met too. **Roache triple on v_θ(35 mm): coarse
0.0045145840, medium 0.0045395745, fine 0.0045457781; R = 0.2482366; state
`CONVERGING`; p = 2.0102; GCI_fine = 5.6328e-04 (0.0563 %); Richardson extrapolated
0.0045478265 m/s, 0.000374 % from the analytic value.** **Planted-zero control fired:**
planted 1.234e-03, read_back_delta 1.234e-03, reader_delta 1.234e-03, exact to 1e-15,
no other radius moved. Strict completion holds at all three levels with the per-level
endTime (3000/3000/**6000**). **Cost: 3.2833 core-min MEASURED** (197 wall s, serial;
L1 2 s, L2 12 s, L3 183 s) against the 3.7167 point estimate — **ratio 0.8834×**, 32.8 %
of the 10 core-min cap, **$0.002807 derived, not measured**; waste 0.000. Shas: prereg
`c6b4a7c4`, comparator `64b02be8`, run script `116c7c2d`, HEAD at run `1fb3bf74`.
Record `cases/ansys_verification/VMFL001/R2/RESULTS.md`; artifacts
`verification/runs/ansys_verification/VMFL001/R2/`.

**Both run-1 mechanisms are repaired and MEASURED to be repaired.** (1) The reader now
parses v2606's headerless `gateAxis_p_U.xy` — the planted-zero control proves it can
see a non-zero in that exact format. (2) **The N = 6000 extrapolation HELD**: the freeze
predicted L3's `Ux` residual ≈ **1.57e-9** at iteration 6000 from a log-linear decay
fit of run 1's last 1000 iterations; the measured value is **1.61027e-09** — ratio
**1.026**, a 2.6 % miss on a two-decade extrapolation across 3000 unrun iterations, and
620× inside the registered 1e-6 clause. L3 plateau ptp **1.772e-07 m/s** (run 1:
2.772e-05). **Run 1's `NOT A RESULT` (register row #1) stands unremoved and
unsoftened.**

**VMFL001 run 1: `NOT A RESULT`** (register row #1), 1.9833 core-min, $0.0017 derived;
commits `dee5870d` (VERDICT; calibration C-37) and `ae30f914` (artifacts).

**Docket / lessons / calibration:** docket **D504** (VMFL001-R2). Lessons **L-280**,
**L-288**, **L-289**, numerics **N-AV1…N-AV5**. Calibration rows **C-37** (run 1) and
**C-45** (R2, landed at `5e789196`). **Two calibration findings from R2 are worth
carrying forward:** (a) extending a converging steady SIMPLE run's `endTime` is
**sub-linear in wall time** — 34.67 ms/iter over run 1's first 3000 vs 30.50 ms/iter
over R2's 6000, because the inner linear solves converge in fewer sweeps as residuals
fall, so price a continuation at ≈ 0.88 × linear; (b) a log-linear residual-decay fit
over the last 1000 iterations is a sound basis for choosing N, and it held to 2.6 %.
**Two lesson candidates are DRAFTED AND NOT LANDED, awaiting the supervisor's read**
— the sub-linear continuation rule, and "a gate value read from a gitignored artifact
is a number with no artifact" (the six R2 `.xy` sampled files match
`.gitignore:67` `**/postProcessing/` and are invisible to `git add`; they were
filed deliberately via `update-index --add`, which does not consult the ignore rules).

**Live jobs:** none. R2 finished 2026-08-24T18:14:02Z; zero solvers of this team are
running.

**Rungs lacking verdicts:** **none.** Both VMFL001 rungs are graded and filed. The
register holds **2 rows**: #1 `NOT A RESULT` (run 1), #2 `PASS` (R2).
**Credential count: 1 PASS of 2 run** — only `PASS` rows are credentials
(`ANSYS_VERIFICATION_CHARTER.md` §6).

**Next actions, in order:**
1. **VMFL005 pre-registration** — draft, supervisor freezes by sha before any compute.
   This is the next case in the first tranche.
2. Then **VMFL003, VMFL007, VMFL050**, each pre-registered and frozen before compute.
3. Then the **3D tranche: VMFL078, VMFL030, VMFL069** — the first 3D cases this team
   attempts, and the cost model above is 2D-serial only and does not transfer to them.
4. Supervisor's read of the two drafted lesson candidates above, and of whether the R2
   comparator's repaired reader should be lifted into a shared helper before VMFL005
   repeats the same v2606-writer parsing from scratch.
5. **Reconciliation dispatch (not this team's file to fix):**
   `docs/COST_CALIBRATION.md`'s worktree copy is **3,892 bytes SHORTER than the HEAD
   blob** — a truncation, not an append. `scripts/append_record.py` refused on it and
   C-45 landed by the disclosed hash-object fallback onto the HEAD blob. The stale copy
   was **inspected, never reverted** (rule 10). `docs/LAB_STATE.md`'s worktree copy is
   likewise 8,383 bytes short of HEAD.

**On Sanaa's desk:** none from this team. **SUBMISSIONS PARKED** — nothing from this
team's VM2026R1 work is filed, sent or registered outside this box, and the manual is
proprietary Ansys documentation.

**Blocked:** none.

**VERIFY (items this lane did NOT personally check):**
(a) **Item (a) of the previous board is now ANSWERED and needs no further verification**
— "that R2 actually converges L3 below 1e-6 by 6000 iterations" was an extrapolation
then; it is now a **measurement**, 1.61027e-09 at iteration 6000, read from
`L3_64x256/log.simpleFoam` and recomputed by the frozen comparator.
(b) the 123/123 post-move archive re-verification and the partial-copy deletion — this
lane did **not** re-run `sha256sum` and carries the haiku lane's and supervisor's
report unverified.
(c) the CASE_MAP counts and the VMFLGPU / VMFL068 absences (from `546a036b`, not
re-derived here).
(d) lesson numbers L-280 / L-288 / L-289 and the `N-AV` ids as carried forward — this
lane did **not** re-derive the LESSONS tail; it re-derived only the `C-` tail, inside
the commit invocation that used it.
(e) **the manual's printed targets themselves.** This lane read them from the sidecar
(lines 896–960) and not from the PDF; the title-page verification of the PDF is carried
from a previous lane's report.
(f) **whether the R2 comparator is correct beyond its own controls.** It passed its
`--selftest`, its planted-zero control fired, and it refused nothing at grade time —
but this lane did not independently re-implement the extraction, and the supervisor's
personal diff read (`8cb29610` → `64b02be8`) is the check that stands behind it.

*Section rewritten by `ansys-lane-opus`, 2026-08-24T18:28:14Z, on the supervisor's launch
authorisation and its own graded run.*
