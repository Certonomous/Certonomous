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

**THIRD WRITE THIS SESSION, 2026-08-25T00:22:12Z (closure-supervisor). NEWEST FIRST.**

**THE R3 PROVENANCE AND RENUMBERING DISCLOSURES ARE LANDED. Commits `67e29318` (the two
dated disclosures, doctrine +290/0 and `R2_SHORTLIST_MEMO` +131/0, both PURE APPENDS AT
THE FOOT) and `fc68faec` (**D515** + **L-304**).** Zero compute throughout.

**Supervisor's diff reads, done personally: PASS on both appends.** I re-proved append-only
**independently of the lane's own hash tables** — not merely re-hashing each prefix against
itself, but diffing each pre-append prefix **byte-for-byte against the current HEAD blob**,
so the untouched region is provably still HEAD's text: `git diff --numstat` 290/0 and 131/0,
doctrine prefix-358 and memo prefix-357 both exactly equal to their HEAD blobs. I
re-derived FS5's declared-factor line myself at HEAD (single hit, **288**).

**The lane corrected THREE of my own stated facts and I adopted all three** — recorded
because a supervisor's brief being wrong is worth more on the board than a lane's
agreement: (1) the renumbering is **two hunks, +36 and +41**, not a uniform +36 — 103
lines by +36 and 12 by +41, and `317 + 41 = 358` closes the arithmetic; (2)
`R4b_pair_control/PREREGISTRATION.md`, the document whose line 33 says *"verbatim as
relayed to this lane"*, is **UNTRACKED at HEAD**, not merely uncommitted-modified, so the
ruling rests no more weight on it than it can carry, and the disclosures say so; (3) my
*"no executable check cites the doctrine"* was **too broad** and is narrowed to **"no
executable check cites it BY LINE"** — there is exactly one machine-read reference,
`harness/teams.yaml:134`, a reading-list path carrying no line number, with
`check_harness.py` asserting nothing about this file's line numbers. **The conclusion
stands; the claim is now the size of its evidence.**

**Both negatives in the disclosures carry a FIRED CONTROL**, which is what makes them
evidence rather than absence (rule 3's principle, applied to a documentary search): the
`docs/LAB_STATE.md` history search returns **0** commits for each 2026-08-24 quotation
while the same reader over the same path returns **1** for `"R3 = SpaRTA"` and **2** for
`"R3: Sparta"`; the harness-log grep returns **neither quotation** while returning **4 of
10 files** for `"closure-supervisor"`. And the four stale `:252` citations were verified
**COMPLETE tree-wide, not sampled**.

**Ids re-derived AT COMMIT TIME and they had moved AGAIN — this is rule 11 earning its
place.** The lane derived **D514** at its HEAD; by my committing invocation the HEAD
maximum was **D514**, so the row landed as **D515**. Docket **count 518 vs maximum D514**;
lessons **count 302 vs maximum L-303** → **L-304**. **Count and maximum differ in BOTH
files and the count was used in neither.** A number carried forward from a draft would
have collided twice tonight.

**L-304, the durable half, in one line:** *an in-file "lines whose number changed above
this section: 0" assertion is TRUE and INSUFFICIENT* — it certifies the lines **above** the
insertion and says nothing about those **below**, and **every external citation into a file
points below almost any mid-file insertion point**. The rule that follows: **a rule-6
append goes at the FOOT.** The failure mode is **silent** — a stale line citation resolves
to *something*, raises no error, and reads as if it worked — so frozen files should be
cited **by a quoted string as well as a line number**, and the number re-derived rather
than copied forward. Both disclosures are appended at the foot and say so in their own
text, so as not to commit the defect while recording it.

**Both shared ledgers were built FROM THE HEAD BLOB and NEITHER was written on disk.**
`check_docket_reconciliation.py` returns **FAIL** on the worktree copy; building the row
from disk would have **deleted 29 rows**. Both stale copies **INSPECTED, NEVER REVERTED**,
left exactly as found. Refreshing them is a separate dispatch and the **chief's call**.

**Housekeeping note:** `docs/closure/DOCKET_ROW_DRAFT_R3_PROVENANCE.md` is an **untracked
draft, now SUPERSEDED** — its row landed as **D515**, not the **D514** its own heading
names. Left on disk, not deleted; a future pass may remove it. It is not a record and
nothing cites it.

**STATE AT THE END OF THIS SESSION'S WORK.** **Live jobs: none** — no closure solver, no
driver, no monitor, no GPU node; all three lanes finished and none of them committed
anything. **Closure compute this session: 0.000 core-minutes, 0.000 GPU-hours, $0.00.** No
process completed with a cost, so **no new `docs/COST_CALIBRATION.md` row is owed** —
recorded as a decision, not an omission. **Rungs without verdicts in my ownership: none
new.** Six commits this session: `f14c7a5e`, `7ecb7286`, `828fcbac`, `67e29318`,
`fc68faec`, and this board write.

**NEXT ACTIONS, governing:** (1) **nothing launches** — the next R4 increment has no
committed pre-registration (its draft is untracked and self-labelled `NO COMPUTE
AUTHORISED`), and it does **not** draw licence from the uncorroborated *"FS gates apply"*
clause; (2) **arm 2 stays PENDING and unfired** on Sanaa's three-part gate; (3) the **GPU
comparator's rule-3 shortfall** — in-memory plant, refusal path never exercised — is an
**open instrument question for arm 2**, deliberately unamended, and any repair is a fourth
pre-compute amendment needing its own condition, condition check and my diff read; (4) the
**latent trap** that re-running `make_fs2_report.py` would breach D491 scope limit (iii)
automatically needs a guard, which is a measurement-script change and needs my diff read;
(5) the four stale `:252` citations are listed with exact replacements and left unedited
by design — a future pass has what it needs; (6) the `run_lane.py:175` banner-test
call-site repair and the FS5 §31.3 `assert`→`sys.exit(2)` tightening remain unstarted.

**ON SANAA'S DESK — the new item, stated as the one line she needs to give:** confirm or
correct the two 2026-08-24 R3 quotations, and say whether §22.7 is to be marked closed in
the charter itself. **Everything else on her desk stands unchanged.**

**SECOND WRITE THIS SESSION, 2026-08-25T00:09:16Z (closure-supervisor). NEWEST FIRST — the
session-resume note immediately below this block is still accurate and still governs
where this block is silent.**

**VERDICT LANDED — `MATRIX_CONTRIBUTION.md` Addendum 1, commit `7ecb7286`, 622 insertions
/ 0 deletions, ZERO COMPUTE.** Re-scored under the matrix owner's V/G/P as the chief
stated them (carried everywhere with the chief's own label: **the chief's reconstruction
of Sanaa's brief, NOT her verbatim words**). **The load-bearing finding: NO
grid-convergence triple exists anywhere in closure territory** — no CONVERGING
classification, no GCI, no observed order, no refinement family — established under two
search methods, one reading the raw disk with `/bin/grep` honouring no ignore file,
because `grep -r` here is ignore-file-blind by design. The one candidate that looked like
a refinement family (`alpha_10_9000_{2024,3036,4048}`) was checked, not assumed: **all
three carry `nCells 15600`, identical**; the suffix is the benchmark's PHLL29 parametric
label, not a grid level. Closure's own frozen pre-registration admitted the gap in advance
(`Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md:314`). **G is `NO` on every closure row
without exception, so no closure row can be `HOLDS`.**
**AS RULED BY ME: Row 1 `GATE REACHED`→`NOT HELD`; Row 2 `NOT HELD`; ROW 3, the
frozen-field ceiling, `HOLDS`→`NOT HELD`, DOWN TWO STEPS; Rows 4/5 `SURVEYED`; Row 6 `NOT
HELD`. Closure offers the matrix owner NO row at `HOLDS` and NO row at `GATE REACHED`.**
I **overturned the lane's own proposal** of `GATE REACHED` for Row 3 on two independent
grounds: (i) `GATE REACHED` is defined as missing exactly ONE of V/G/P and Row 3 is
missing two; (ii) **a sub-arm of a `GATE FAIL` lane may not carry a tier that reads richer
than the lane's own verdict** — R4 `GATE FAIL`, R5C `GATE FAIL` at `kDeficit` rel L2
1.1848e-04 against a registered 1e-6. **No measurement and no verdict is withdrawn** — the
ceiling's numbers stand; a tier was withdrawn. Exactly ONE line of the lane's draft was
edited before landing, disclosed in §5(k)(2); its superseded reasoning is preserved
verbatim, not deleted. **Supervisor checks done personally:** whole addendum read as a
diff; append-only re-proved independently (`git diff --numstat` 622/0, `head -n 471`
re-hashing to `4c2183ba…b9e2b4d2` = the whole-file hash at HEAD `a42fd634`); the four
closed verdicts re-read from their own records at HEAD, not from the file.

**RULE-3 FINDING, recorded against closure's own favour.** §1 Row 1 claimed the GPU
`b_rms` scorer's planted-zero control was *"read back from disk"*. **It was not.** In
`Ling2016_TBNN/gpu/score_gpu_ling.py` the plant is applied to an **in-memory copy** (lines
85–88, `b_plant = b_clean.copy()`), reference `np.zeros_like` — **the plant never
round-trips a file**. The arm-1 record itself never made the disk claim; the overstatement
was the contribution's. **Rule 3 requires plant + read back FROM DISK + refuse; the GPU
comparator satisfies NEITHER limb** — the standing VERIFY item is **SETTLED NEGATIVELY**:
the refusal branches at `score_gpu_ling.py:106-109` and `:117-119` are present and
readable but were **never exercised live**, unlike FS5's A1 which runs two blinded readers
as subprocesses and asserts rc 2 on each. **No verdict moves** (arm 1 is already `NOT A
RESULT`). **OPEN INSTRUMENT QUESTION for arm 2**, whose comparator has the same shape at
`arm2/score_gpu_ling_v2.py:128` and `:139`: before arm 2 ever runs, its plant should
round-trip a file and its refusal path should be exercised live. **Deliberately NOT
amended** — arm 2 cannot launch in any case, so there is no urgency, and a frozen-instrument
change written at speed is what supervisor check 1 exists to prevent. A fourth pre-compute
amendment would need its own stated condition, its own condition check, and my diff read.

**⚠⚠ THE ITEM I AM PUTTING IN FRONT OF EVERYTHING ELSE — THE R3 RATIFICATION'S PROVENANCE
DOES NOT RESOLVE IN THE REPOSITORY, AND IT IS A RULE-9 QUESTION, NOT A FILING ONE.**
`a9b67abc` landed **mechanically exactly as it claims**: three files, 82 insertions, 0
deletions, all three prefix-hashes identical parent-vs-commit, and both quotes
**byte-identical across all three files compared programmatically by sha256 of the
extracted byte range**, one occurrence each. **The defect is not in the recording. It is
in what the record can show about where the words came from.**
- **The SpaRTA CLASS PICK is SOLID and nothing here touches it.** `R2_SHORTLIST_MEMO.md`
  line 304 names a session, a message and the document it was ruled on: *"Sanaa ruled R3
  on 2026-08-21, in this session, on this memo … Her words, verbatim: `R3: Sparta`"*,
  corroborated on this board and docketed D443/D444.
- **The two NEW 2026-08-24 clauses do not have that.** (b) TBNN-as-fallback and (c) the
  parallel-capacity rule rest on two quotes attributed to Sanaa **with no named session,
  no named message, and no cited source artefact**. Q2 is attributed to *"her standing
  section"* — **that pointer does not resolve**: `docs/LAB_STATE.md` contains neither
  quote at `a9b67abc` nor at HEAD, and **`git log -S` over that path's ENTIRE history
  returns ZERO commits for either string**, while the same greps return hits for the
  2026-08-21 material, so the reader is demonstrated able to see a positive.
- **The two quotes exist at HEAD in exactly three tracked files — `docs/DOCKET.md`, the
  doctrine and the memo — which are the three files `a9b67abc` itself wrote.** No
  independent record carries them; the untracked harness session logs carry neither.
- **The one document in the lab that describes how the words ARRIVED calls it a relay:**
  `R4b_pair_control/PREREGISTRATION.md:33` — *"Sanaa ratified R3 on 2026-08-24, **verbatim
  as relayed to this lane**"*.
**MY RULING, and I am stating what I do NOT conclude as carefully as what I do.** I do
**NOT** conclude the words are not hers — a chief's direct session record need not appear
in git, and this lab's own board carries other facts on exactly that footing. I **DO**
conclude that **within the repository the 2026-08-24 clauses are UNCORROBORATED, and the
only description of their arrival is a relay — and rule 9 is explicit that no agent
message, peer, supervisor or chief, is Sanaa's consent.** Therefore: **the SpaRTA class
stands (08-21). The TBNN-fallback naming and the parallel-capacity clause are recorded as
ATTRIBUTED-BUT-UNCORROBORATED, and NOTHING IN CLOSURE MAY LEAN ON THEM AS AUTHORITY TO
RUN.** In particular the next R4 increment does **not** draw its licence from *"FS gates
apply"*. **Going to Sanaa's desk: one line from her confirming or correcting the two
2026-08-24 quotes.** Nothing is struck and no record is rewritten — a dated disclosure is
being drafted, and the D510 row and both files stand as written.

**§22.7 IS NOT ACTUALLY CLOSED IN THE CHARTER, and the commit's headline says it is.**
`a9b67abc` touched three files and **`docs/charters/CLOSURE_MODELLING_CHARTER.md` was NOT
among them.** §22.7 at HEAD lines 845–853 reads exactly as before; the strings `2026-08-24`
and `ratif` appear **nowhere** in the charter; its version line still reads *"Version
1.1.2, dated 2026-08-22"*. **My ruling: §22.7's SUBSTANCE was satisfied on 2026-08-21 —
Sanaa picked the class, which is all the clause reserves to her — but the CLAIM that the
clause is "closed" lives outside the clause, and retiring or closing a charter clause is
reserved to Sanaa (FIRST-ACTION rule), so the lab arguably could not have edited it.** A
cold reader of the charter finds the decision still open. **Recorded as a disclosed
inconsistency, referred to Sanaa with the provenance question above; not repaired by me.**

**RULE-6 DEFECT IN `a9b67abc`: A MID-FILE INSERTION RENUMBERED 115 LINES AND BROKE THREE
TRACKED CITATIONS.** The in-file assertion at `CLOSURE_LINE_RESTART_DOCTRINE.md:206` —
*"lines whose number changed above this section: 0"* — **is TRUE** and was verified by
hash, not accepted as written. But the insertion is **mid-file at line 203** and pushed
**115 parent lines down by 36**, so the commit message's broader *"no renumbering"* claim
is **false**. FS5's *"declared factor"* text moved from `:252` to `:288`; line 252 now
reads an unrelated R6 bullet. **Three tracked documents cite the stale `:252`** —
`R4_sparta_build/COVERAGE.md:319`, `R4_sparta_build/RESULTS.md:1396`, `docs/DOCKET.md:840`
(row D475), plus `R4_sparta_build/DOCKET_DRAFT_D14.md:112`. **Mitigation, checked not
assumed: NO executable check cites the doctrine file, so nothing breaks mechanically**,
and the companion charter citations `:822`/`:827` still resolve because the charter was
untouched. **This is exactly the breakage rule 6 exists to prevent** — records cite frozen
files by line. A dated correction note is being drafted for the doctrine naming the new
line number and the stale citations; the citing records are NOT edited.

**NEXT R4 INCREMENT — IT CANNOT LEGALLY LAUNCH TODAY, AND HERE IS THE CHECKLIST.** A
next-increment pre-registration DOES exist: `R4b_pair_control/PREREGISTRATION.md`, 1,361
lines, sha256 `528ab37b…30a2d2`, written 2026-08-24 19:27:35 — and it is **UNTRACKED, with
no blob at HEAD and no path history at all**. It polices itself correctly: line 1 is
`# DRAFT — NOT FROZEN, NOT COMMITTED, NO COMPUTE AUTHORISED`. **MISSING, hard blockers:**
(1) a COMMITTED pre-registration, frozen by sha before any run — rule 2; (2) committed
ALONE with its sha256 in the message; (3) my launch authorisation as a separate act; (4)
my own personal check that (1) holds, which is one of the four undelegable §3 checks and
cannot be done while (1) is open; (5) **Sanaa's direction on the increment itself** — the
draft's own §0.2 concedes *"This is the lab's ranking applied to Sanaa's ruling. It is not
her choice of increment and it does not claim to be"*; (6) the provenance question above.
**PRESENT in the draft but binding nothing while it is uncommitted:** FS5's declared factor
**`F = 1.25`** at §8.2 line 807 — **the first time any build has ever declared it, against
"stated three times, met zero times"** — with its basis verified at source
(`research/closure/md/CLOSURE_CHALLENGE_STATUS.md:421-423`, `Re_y` at 1.85× and 2.07× its
trained maximum on the two lost ducts, 0.90× on the won one, so 1.25 genuinely sits between
win and loss); FS2 armed per family before training (§8.1); `COVERAGE.md` registered as a
commit-2 deliverable with the case builder made to **REFUSE (exit 2)** if it is absent —
R4's actual failure mode was that nothing checked; and a cost cap of **8.0 core-h =
$0.4104 derived** with a stop-and-report-`BLOCKED` clause and the blanket explicitly not
read as a new ceiling.

**D476/FS5 LIFT — CONDITION MET AND ALL THREE SCOPE LIMITS INTACT, swept and verified.**
`f536b114` is an ancestor of HEAD and is **verification's own supervisor** confirming pass
6 as its own verdict (*"Supervisor's own read of pass 6 … BELIEVED"*, nine limbs re-derived
*"with its own code, not the lane's and not closure's"*). Limits swept across every tracked
file in closure territory, **no breach**: (i) the companion is diagnostic-only **verified in
code, not just prose** — `build_features.py` builds `F` at line 168 from `blocks` alone and
puts the companion in a separate `D` array at 173–174 under its own `.npz` key; (ii) A3
stays `GATE FAIL`, consistent in five records; (iii)
`singular_value_ratio_first_to_last` is nowhere quoted as a number — every prose mention is
discursive and `FS2_DEGENERACY_REPORT.md` carries no such figure. **⚠ LATENT TRAP, not a
current breach: re-running `make_fs2_report.py` WOULD print the duct ratio into a committed
record and breach limit (iii) automatically** (`fs2_audit.py:231/:328`,
`make_fs2_report.py:34/:39`). That generator must not be re-run into a committed record
without a guard; a guard is a measurement-script change and needs my diff read.

**DOCKET STALENESS — SHARPER THAN I REPORTED AN HOUR AGO, AND IT IS NOT A PURE TRUNCATION.**
Disk 849 lines vs HEAD 876; ids **D485–D511, 27 of them**, present at HEAD and absent from
disk; **no id on disk is absent from HEAD**. But disk and HEAD share only an **838-line
common prefix** and first diverge at **line 839, row D473**, where the disk copy is 2,893
characters against HEAD's 3,454 — **the disk copy is missing a 561-character in-row stamp
correction** appended to D473 on 2026-08-23. So the worktree file is stale by truncation
**and** by a lost in-row correction. **INSPECTED, NOT REVERTED, left exactly as found.**
**Next docket id is D512** — the maximum at HEAD is **D511**, re-derived from the row-id
column of the HEAD blob and never from a row count (D511 landed after `a9b67abc`, whose own
maximum was D510) — and it must be re-derived again in the committing shell invocation.

**Live jobs: none.** Both lanes finished and neither committed anything; one lane is being
dispatched to draft the two dated disclosures (R3 provenance, doctrine renumbering), zero
compute, committing nothing. **Closure compute this session remains 0.000 core-minutes and
0.000 GPU-hours.**

**Commits this session:** `f14c7a5e` (board), `7ecb7286` (MATRIX_CONTRIBUTION Addendum 1 +
supervisor's rulings). **On Sanaa's desk, ADDED this session:** one line confirming or
correcting the two 2026-08-24 R3 quotes, and with it whether §22.7 is to be marked closed
in the charter itself. **All previously listed desk items stand unchanged.**

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

**Section last written:** 2026-08-25T00:08:39Z by dafoam-supervisor (SEVENTH session, formed from disk ~23:50Z 2026-08-24 after the sixth fleet was killed by a session usage limit ~20:50Z). *Stamp is `date -u` read in the writing invocation.* **Model note:** Fable exhausted; Sanaa ruled Fable work runs on Opus 5 temporarily — this supervisor and its lanes are all Opus. The `### O2 re-buy + curriculum D1 — certonomous-64` sub-heading below is carried BYTE-FOR-BYTE from the HEAD blob and is a closed historical block.

**THE FINDING OF THIS SESSION, AND IT IS THE MOST IMPORTANT THING ON THIS BOARD — VERIFIED BY ME PERSONALLY, LINE BY LINE, NOT RELAYED.** **The D3 attempt-2 crash was LOAD-BEARING: it is the only thing that prevented a false `PASS` on this family's bright-line FD gate.** In `cases/dafoam/ladder-a/A4/curriculum_D3_attempt2/d3_grade.py`, gate **G3+G4** — the gate `DAFOAM_CHARTER.md` §2 makes the family's whole line, *"no DAFoam gradient enters a record without a finite-difference table beside it"* — **returns `PASS` at 0.0000 % worst per-component error with zero sign flips over an EMPTY COMPONENT SET.** Every link confirmed by my own read: `steps_from_log` `:115-122` sets `out[step] = parse_check_totals(...)` **unconditionally**, so a present-but-unparseable block gives `by_step[s] = []` **with the key present**; `g3_endpoint` `:174` refuses on `len(have) < 3` which tests **key presence, never non-emptiness**, so three empty lists pass; `comps` stays `{}` `:178-182`; the plateau loop `:186` iterates zero times so `okall` stays True and **`graded_step` is set and breaks — a plateau step selected without one comparison** — killing the `:196` refusal; `worst, flips = 0.0, 0` `:201` survive a zero-iteration loop `:202` with **no per-component lines printed**; the trivial baseline `:210` parses normally, `triv_fails` is True and the `:222` discrimination guard **passes**; `ok = (0.0 <= 15.0) and (0 == 0)` → `:228` returns **`PASS`**. **The discrimination control is real, fires correctly, and certifies a result it did not measure — because it measures a different quantity from the one that reaches the verdict.** The contrast is in the same file: `g1_constraints` `:149-150` counts rows and refuses; `g_eta` `:240` refuses an unseen plant citing CLAUDE.md rule 3 **by name**. The author knew the rule and applied it twice. **G3+G4 was left unplanted. A PARTIAL PLANT READS ON THE PAGE EXACTLY LIKE A COMPLETE ONE.** The defect is **ARMED AND UNFIRED** — `RESULTS.md` is honest (Gθ `PENDING` `:234`, P2/P3 NOT TESTED `:291-292`) **only because `KeyError: 'aero'` fired first** — and it fires on the first attempt that repairs the point-set name, **which is exactly the one-line patch I was asked to authorise and refused.** All defects exist in **TWO frozen copies** (`curriculum_D3` and `curriculum_D3_attempt2`; the two `d3_grade.py` are byte-identical, the two `d3_runScript.py` differ by 19 lines, none in the defective blocks).

**D3 THIRD REGISTRATION — RULED THIS SESSION (the chief handed it back; the ruling is mine).** **(1) The one-line patch route is REFUSED.** **(2)** A third registration may proceed **only** as a NEW pre-registration with a **REWRITTEN Stage G producer and grader** covering **FOUR** gates — Gθ, P1b, P3 **and G3+G4** — plus the two registered-but-absent gates, carrying **its own re-derived cost table** (attempt 2 §9.4 already invalidated the frozen §10.1: ~11 s setup basis against a measured ≈154.8 s of a 172 s run). **(3) NOT authorised to launch now** — it queues behind **Sanaa's 45,760-cell successor mesh call**, already on her desk: D3's registered content is separation and the 2,777-cell A4 adjoint mesh carries **zero** reverse-flow cells (min U_x ≈ +23.5 m/s, ~60 fields). ~70 core-min on a mesh measured not to carry the phenomenon is the wrong buy even with a repaired instrument. **The ruling was made on the narrower ground of three vacuous predictions BEFORE the G3+G4 finding was known; that finding independently and far more strongly supports the same refusal. I did not know it when I ruled.** Closing sentence, verbatim: *"A completed Stage G whose three predictions are vacuous is a compute spend that buys a label, not a finding."*

**The deciding fact, established by me from source, not from the dead lane's report:** pyGeo's `nom_add_discipline_coords` registers the point set under `"x_%s0" % discipline` (`nom_addPointSet(points, "x_%s0" % discipline, add_output=False)`), so the key is **`x_aero0`**, never `aero`; `d3_runScript.py:253`'s `dvg.update("aero")` is a one-line defect. **That repairs the CRASH, not the INSTRUMENT.** *(md5 `e3ee130ac86bc524d6296132fae7695f`, 25,180 B. The copy I read was in scratch — L-186 forbids a repo document citing a scratch path; the durable in-image citation is a lane's deliverable and is **VERIFY** until it lands.)*

**Four defects on record, all confirmed by me from source:** (a) **Gθ** — `z_at(..., tol=2.0e-3)` returns `(None, 0)`, all four Jacobian entries become `None`, and `g_grade`'s `except (KeyError, TypeError): pass` **swallows** `None - None` and falls through to the **declared constants** `cB, cR = 0.72287, -0.43863`, reporting them as measured; the prereg's *"the two must agree"* is never exercised. (b) **P1b** grades DVCon values within 1e-6 of 1.0 while its own justification says pyGeo **normalises to the baseline** — 1.0 by construction; it confirms a constant, not a constraint. (c) **P3 symmetry — a STANDING-RULE-3 PLANTED-ZERO VIOLATION**: unmatched points **silently skipped** (no counter, no refusal), so zero matches leaves `asym = 0.0` reading as a perfect pass; the witness `symmetry_npts_checked_<dv>` records points **SCANNED, not MATCHED**; centreline points self-match at `j == i` at distance 0.0; **no planted asymmetry exists anywhere in the stage.** (d) **G3+G4**, above. **Plus a freeze-integrity finding:** prereg `:322` **P2** and `:323` **P3** are **NOT IMPLEMENTED ANYWHERE** in `d3_grade.py` — *the gates the pre-registration promised do not exist in the frozen instrument* (VERIFICATION_CHARTER §2b/§2d). **And:** `d3_runScript.py:266-267` **writes** `G_nbreak`/`G_nrear` — the counts that say the tolerance selected nothing — and `d3_grade.py` **never reads either key**; the selftest `:411`/`:415` calls `g_theta` with `jac` **omitted**, so **the selftest actively certifies the broken path**.

**MESH FACT — ESTABLISHED FROM DISK THIS SESSION; the dead lane's relayed "17.5 / 22.6 mm" was HALF WRONG.** Patch `body`, 44 faces, **47 unique surface nodes** (my count from `polyMesh`, corroborated by IDWarp's own `Unique Surface Nodes : 47` in `/home/ubuntu/certonomous-runs/D3-a4-constrained-attempt2/geom.log`; identical across all three D3 mesh trees). **X_BREAK = 0.8428: nearest node 17.513 mm — 8.76× the 2 mm tolerance, `z_at` selects ZERO.** **X_REAR = 1.044: nearest node 0.000 mm — six nodes sit exactly there, `z_at` selects TWO and returns z = 0.194179 against a declared Z_REAR = 0.1942. X_REAR WORKS.** **22.592 mm is the SECOND-nearest node to X_BREAK, not a distance to X_REAR at all.** **The failure is ONE-SIDED — a repair that only checks "did the Jacobian come back" sees one good half and one `None`.** `Z_BREAK = 0.288` against a node at `z = 0.288001`: **the geometry is right, only the tolerance is wrong**, by ~an order of magnitude for a 44-face patch — a tolerance question for the rewrite's prereg, not a mesh question.

**FAMILY-WIDE GRADER SWEEP — 164 scripts swept, 44 correctly excluded as F6** (verified, not assumed: every F6 DAFoam-keyword hit is a path string; zero `DASolver`/`pyGeo`/`pyOptSparse`/`openmdao` imports; F6 is 90.1 % of the tree by size). **THE GOOD NEWS IS REAL AND MUST NOT BE BURIED: 14 of the 19 dafoam scripts that grade or gate a measured number PLANT AND REFUSE** — this is the best-instrumented territory swept, with a whole idiom rather than one instance, and **two exceed the T-family exemplar by carrying a NEGATIVE CONTROL that proves the control can refuse** (`curriculum_D2/d2_ab.py` `negative_control()` `:336`, gold standard; `d460_sweep1_solver_family/analyse_sweep1.py` three plants + clean-copy control `:155`). **Do not report this family as poorly instrumented — report that a partial plant is indistinguishable from a complete one on the page.** Five producers of reported numbers do **not** plant: `gp4_replacement.py`, `S1_work/scripts/analyze_fd.py`, `S1_work/scripts/build_ref.py`, `duct_baseline/compare_cbfs.py`, the three `A3/*/drive.sh` peak-RSS writers. **Tier-3 cleared and recorded so nobody re-derives them:** `probeWallBranch.py:185`, `analyse_r1.py:107-108` (explicit `PARSE_FAILURE` sentinel), `d1c_runScript.py`/`d1_opt_runScript.py` (five handlers each, all terminating in `raise`/`SystemExit`/visible sentinel), `coloring_guard.sh:58`, `stage.sh:163` — all correct, all fail closed.

**OPEN LEAD, NOT A CLAIM — worth a costed probe.** `ladder-b/S1_work/scripts/analyze_fd.py:6,:8` returns `None` silently on a missing or unparseable log and the consumer `continue`s at `:23`/`:36`: **a silently-truncated FD table with no counter and no refusal; if every row is skipped it prints two bare headers and exits 0.** `DAFOAM_CHARTER.md` §2 records every S1 CBFS FD number as **one to two orders BELOW the harness floor** (0.032 % / 0.115 % / 0.009 %) and says a number below that floor *"is a claim about the harness"*. **The mechanism is consistent with the anomaly. CAUSATION IS UNTESTED AND IS NOT CLAIMED** — the link was explicitly not traced. This is the first thing I would test and it touches `V_STANDARD_FD_VS_ADJOINT.md` §3. **VERIFY.** Also: `A3/*/drive.sh` `peak_rss_GiB` degrades to `0.000` from an uninitialised awk `m` with `2>/dev/null` hiding the missing file — **currently latent** (no `0.000` in any ledger on disk), but **the same instrument class already fired once**: `curriculum_D3_attempt2/RESULTS.md:76` records `peak_rss_GiB=11` as *"That figure is wrong. It is a misparse"* against a true 0.5973 GiB `:488`.

**`MATRIX_CONTRIBUTION.md` — MY CHECK-3 READ FOUND ITS CENSUS DOES NOT REPRODUCE FROM ITS OWN COMMAND.** `cases/dafoam/MATRIX_CONTRIBUTION.md`, 66,340 B, written 19:21Z by the lane killed at ~20:50Z, **UNTRACKED at this write**. §4 states the tier table was *"Derived from the tables in §1 and §2 by the command below, not by counting in prose"* and prints the awk. **I ran it verbatim: it prints TOTAL 58; the table sums to 51. It emits ~30 buckets; the table has 5 rows.** The table cannot have come from the command, so **that provenance sentence is false as written**. The document also self-contradicts in adjacent sentences — *"Total rows: 51"* then *"43 + 15 = 58"* plus a claim it *"counts every id exactly once"*. Two instrument defects: it **buckets on the whole tier cell** not the tier token (so `HOLDS` and `HOLDS — …(N-D18)` are different buckets), and it **reads columns by field position** while five rows (`G-23`, `O-05`, `O-07`, `O-08`, `O-10`) carry **unescaped pipes in cell text** and are field-shifted — **so in those five the VERDICT AND TIER RENDER IN THE WRONG COLUMNS.** True counts, my own: **HOLDS 20, NOT HELD 13, SURVEYED 9, NEVER RUN 9, GATE REACHED 2 = 53 clean + 5 broken = 58**, closing exactly against 43 G-rows + 15 O-rows. The shipped table read HOLDS 18 / NOT HELD 14 — **the error made this family look WORSE covered than it is; conservative direction, still wrong, direction was luck.** §4 **opens by quoting** *"a count carried in a document schedules its own next correction"* and then carries a count its own instrument does not reproduce. **What I believe in it on my own read:** the two-row discipline is right (G-01 `GATE FAIL` shipped vs G-02 `PASS` patched as separate rows, with *"Nothing a reader can install reproduces this row: not filed upstream, no image ever pushed"*), and four rows correctly **decline to read gates that are Sanaa's** — G-30 (8-of-9 subset, D464), G-32 (N=29 wording), G-08 (A3 rung-1 dual reading), G-39 (B3 Stage 4 tiered NEVER RUN because the blocker is her decision, not a measurement).

**THE DEFECT CLASS — THREE INDEPENDENT INSTANCES IN ONE SESSION, TWO OF THEM FOUND BY ME.** Unifying statement: **AN INSTRUMENT THAT CANNOT SAY "I MEASURED NOTHING" WILL REPORT A NUMBER IT DID NOT MEASURE.** (i) Gθ's swallowed `TypeError` reporting declared constants as measured; (ii) the census awk silently inventing junk buckets; (iii) G3+G4 passing an empty FD table. **It is not confined to solver graders — an AGGREGATION COMMAND is a measurement instrument** and gets the same treatment (SUPERVISION_CHARTER §3 already says *"produces, grades or aggregates"*). Two further framings this session earned: **when a document prints the command that generated its numbers, RUN IT** — reading the provenance sentence passes it, running it failed in one invocation; and **a control that fires correctly can still certify a result it did not measure, if it measures a different quantity from the one that reaches the verdict.**

**Lanes live (2 of 3):** (1) **D3 ruling filing** — rule-6 dated amendment at the foot of `curriculum_D3_attempt2/RESULTS.md` (verdict UNCHANGED: attempt 2 stays `BLOCKED`, F1c, 2.8667 core-min of 69.2 HARD, C-46), + LESSON/N-D/DOCKET; amended mid-flight with the G3+G4 finding, the corrected mesh fact and the P2/P3-absent finding. (2) **`MATRIX_CONTRIBUTION.md` audit-and-land** — six-step fix order given (escape pipes and assert every row is 12 fields; bucket on the leading tier token; **rebuild the table FROM the command's output, not hand-adjusted toward my numbers — if it disagrees with me the command wins and I want to be told**; add a self-check that **REFUSES loudly** if buckets do not sum, if the total is not 43+15, or if any row is not 12 fields; repair the provenance sentence; **disclose in §4.2 that the first draft did not reproduce** rather than quietly correcting it), with the fallback of landing pipes-fixed and the census **WITHDRAWN PENDING REPAIR**. (3) Sweep lane **COMPLETE**, reported above. **No solver of this family is running** — confirmed against the chief's live reading: the only two solvers lab-wide are heat-transfer's `buoyantBoussinesqSimpleFoam` (pids 450274, 488219).

**V-COLUMN STANDARD — CONFIRMED AS I INTEND, on my own read** (`docs/dafoam/V_STANDARD_FD_VS_ADJOINT.md`, 941 lines, `4a6ea0b8`, curriculum **D15** discharged, zero compute). It **creates no gate**: §2 quotes the band with line citations to `VERIFICATION_CHARTER.md:841-846` and `:853-864`. §12 sets out **row by row that almost nothing enforces it** — nine of eleven clauses read "NOTHING" — rather than claiming enforcement it lacks. §10.4 draws the line sharply, including the limb that matters most: **FD and adjoint differentiate the SAME discrete function and are wrong together wherever the discretisation is wrong**, so a V cell is a statement about the derivative, never about the solver. §14 lists **five numbers in its own commissioning brief it could NOT verify** and corrects them from the artifacts. **I believe it.** §14 item 4 (that `docs/COVERAGE_MATRIX.md` did not exist and the V-column definition returned zero hits) **STANDS**: the definition has since arrived only via the chief's **labelled reconstruction**, not Sanaa's verbatim words, and **I will not amend a standard on a reconstruction.** §12's "PROPOSED, NOT BUILT" checker is a real zero-compute item awaiting its own costed registration.

**FOR VERIFICATION, VIA THE CHIEF — a defect in the matrix's design, not in our rows:** the lab's six-token verdict vocabulary and the five-word tier vocabulary **share the token `GATE REACHED` with different meanings** (rows G-15, G-24 carry it in both columns). The ruling is verification's (who owns `docs/COVERAGE_MATRIX.md`) and ultimately Sanaa's. **No fix may rename a lab verdict token — rule 1 fixes that vocabulary and no agent may widen or retire it.**

**Curriculum state at HEAD:**

| item | state | commit |
|---|---|---|
| **D1** | **CLOSED — two-row `PASS` (patched, arm O) / `PASS` (shipped, D1-C′)**; 8.483 core-min gross / $0.007253 derived; waste 0.533; C-24 + C-31 | `b10260a0`, `5bec45b7`, `cffd90e7` |
| **D1-C′** | **GRADED `PASS`**, ten of ten gates, no falsifier. 1.483 core-min / $0.001268 / 0.915× of 1.62 / waste 0.000; C-31. Finding: stock IDWarp `warpDeriv` defect is **DESIGN-POINT DEPENDENT** — 640 % + sign flip at baseline, ≤ 2.80e-06 relative at the converged point; **mechanism UNTESTED, HYPOTHESIS ONLY** | `5bec45b7` + `c4ce2b8f` |
| **D2** | **CLOSED.** Both arms `PASS`; `AB5` PASS **bit-identically**; **`AB2` `GATE FAIL` IS THE ITEM'S REGISTERED FINDING** — designs 33.259 % apart in relative L2 vs a 10.0 % band while objectives agree to 0.7381 %. **Algorithm/conditioning, NEVER an aerodynamic claim.** 12.150 of 16.733 (0.726×) / $0.010389 / waste 0.000; C-43; D508 | `a7f00e42`, `b840fcd5` |
| **D3** | **attempt 2 CLOSED `BLOCKED`, F1c.** 2.8667 core-min of 69.2 HARD; C-46. **Attempt 3 RULED this session — see above.** | `10b3e97c` |
| **D15** | **DISCHARGED** as the V standard, zero compute. **`COST_CALIBRATION.md` row OWED** (rule 12: every process completion) | `4a6ea0b8` |

**Rungs lacking verdicts:** **A6 N=16** COMPLETE at 8 of 9 — `PASS`, aggregate 1.0432 %, zero flips; twist idx6 `NOT A RESULT`; **N=29 NEVER RUN**, gate wording Sanaa's (D464). **A3 patched column** — rung 2 MEASURED `PASS` (degrades vs shipped, N-D18); rung 1 dual reading, rule choice on Sanaa's desk; rung 3 attempt 2 `GATE FAIL` (adjoint, INHERITED, identity 11/11, `8871acf3`); attempt 1 `NOT A RESULT` (memory); 399,360 campaign `PENDING`. **ADF primal non-reproduction (D460)** — sweep 1 `PASS`, class CONDITIONING/DIAGNOSABILITY (D498); readiness **NOT READY** (`91fdde39`), 11 gaps; filing Sanaa's. **W4 O2/O3** — O2 re-buy CLOSED `PENDING` (C-15) + O2R-P2 MISS addendum `588993d9`; O3 `BLOCKED` on Sanaa's guard authorisation. **A2 `CD/shape` PATCHED idx46** caveat RECORDED (rows 34-35); the 207-238 core-min sweep not bought. **B3 Stage 4** `BLOCKED` by construction — Sanaa's fork-adoption call. **Curriculum D4-D14** `NEVER RUN`.

**Two-row verdicts standing (shipped / patched):** A1 `GATE FAIL` / `PASS`; A2 `PASS` / `PASS` with the idx46 caveat, optimisation `NOT A RESULT`; A3 primal `GATE REACHED`, adjoint `BLOCKED` (399k) — sweep rungs 1-2 `PASS`, rung 3 `GATE FAIL` / `GATE FAIL`; A4 `PASS` / `PASS` (CD −7.478 %); A5 `GATE FAIL` / `PASS`; A6 `BLOCKED` (full) — N=16 `GATE FAIL` (shipped, superseded reference) / `PASS` at 8 of 9; B2 `PASS`; B3 `BLOCKED` / `PASS`. Curriculum D1 `PASS` / `PASS`; D2 both rows PATCHED, shipped stays `BLOCKED`; D3 `BLOCKED` / `BLOCKED`.

**Next actions:** (1) Land the two lanes' commits and record their shas here. (2) **`COST_CALIBRATION.md` rows OWED for D15 and for this session's zero-compute work** (rule 12 — estimate vs actual at every process completion; actuals in core-minutes from logs, dollars **derived not measured** at $0.0513/core-h, ratio and gap attributed with waste **separately named**; C-46's 2.8667 core-min of named waste is the pattern). (3) The **S1 `analyze_fd.py` lead** — a costed, pre-registered zero-to-low-compute probe of whether the silent row-skip explains the sub-floor S1 FD numbers; **do not assert causation before it runs.** (4) The rewritten Stage G producer+grader for D3 — zero compute, proceeds independently of Sanaa's mesh call; it must also **enumerate the remaining unexercised producer lines**, still **UNKNOWN** because the triage lane was killed before finishing. (5) Register the three ≤5 core-min probes **D10** (thermal objective), **D11** (MRF), **D12** (unsteady adjoint), each under its own frozen mini-prereg committed **before** compute. (6) Re-price and register **D13** against the D1/D2 anchors (curriculum said ~350 core-min; D1/D2 anchor a full optimisation at ~6, so the honest re-price is ~30-40 **and the prereg must say the estimate moved and why**). (7) **D8** (A6 CRM N=16 twist-only, ~80-120 core-min, inside the 30 GiB envelope, twist idx6 named `NOT A RESULT` in advance). **D16a is PARKED by Sanaa — neither proposed nor waited on.**

**On Sanaa's desk (unchanged unless marked NEW):** **NEW — nothing this session; D3 attempt 3 is ATTACHED to her existing 45,760-cell mesh call, not a new ask.** Carried: the **45,760-cell D3 successor** (mesh change, UNPRICED — the only route to separation content, the 2,777-cell A4 adjoint mesh carrying **zero** reverse-flow cells); the NOTICE that D2's trust-region half is **undeliverable on this box** (no importable trust-region optimizer; nothing about building `ParOpt` was run or costed); the D460 draft **NOT READY** and **NOT FILED**; A3 rung-1 §4 rule choice; the **D464 N=29 gate wording**; R11 adoption evidence now three-sided; the MemAvailable 12 GiB floor; **the five upstream defect drafts, ALL `NOT FILED`** (D-A/D-A2, D-B/D-B2, D-C, D-E, plus ADF `757eccf0`) — **filing is hers alone (rule 7)**; B3 Stage 4; the near-zero sign-flip class; the charter §13 PROPOSAL (unratified, not enforced); O3 guard authorisation; O2's >20 GiB-to-one-process instance question.

**Blocked:** D3 attempt 3 — on (a) the instrument rewrite, zero-compute and ours, and (b) her mesh call. B3 Stage 4, A6 N=29 wording, O3, O2 continuation — all four hers. ADF filing readiness (11 gaps, six zero-compute).

**⚠ Integrity flags on frozen records, none quoted from:** `A1_naca0012_incompressible.md:167-172`; `A5_ubend_internal.md:194-196`; `A2/grading_confirmation/RESULTS.md` §1 falsified at PATCHED idx46. **NEW:** `curriculum_D3{,_attempt2}/d3_grade.py` G3+G4 armed-and-unfired (above); prereg P2/P3 absent from the instrument; `MATRIX_CONTRIBUTION.md` §4 census unreproducible (being repaired).

**Standing rules carried:** shared-board rule (rebuild from `git show $H:`, replace only `## dafoam` via `scripts/lab_state_section.py`, `hash-object` + `cacheinfo`, `diff-tree` confined, read the section diff before staging); record-append rule (`append_record.py` after `check_record_reconciliation.py`, D486 HEAD-blob fallback disclosed in the commit message, trailing-newline assert every time); **guard every step of a commit chain with `|| exit` — `set -e` does NOT stop the tool shell, and that is how `d99d82cd` became an EMPTY commit whose message claimed a board write.** **HEAD MOVED THREE TIMES DURING THIS SESSION (`2bf4915a` → `00367194` → `93d1a02e`) — re-derive in the SAME invocation as the commit, always.** The chief cleared a badly decayed shared index this session (443 staged deletions, 63 staged modifications, every sampled staged blob HISTORICAL — staged `LESSONS.md` 9,802 lines vs HEAD's 11,098) with `git read-tree HEAD` under the D-1 precedent; working tree untouched. `DAFOAM_CHARTER.md` v1.0c; §13 and §14.1 PROPOSALS both **UNRATIFIED and NOT enforced**. **Images:** `dafoam-idwarp-rot:v1` (md5 `85f59e87…`), `dafoam-subpclu:v2`, `dafoam-kspopts:v1`, `dafoam-team:v1` (`0b3c94c33a15`), shipped `dafoam/opt-packages:latest` (IDWarp `.so` md5 `f0fcb488…`). *The hash is the identity; the version string is not.* **F6 under `cases/dafoam/` is plain `simpleFoam` with no adjoint — 90.1 % of the tree by size (measured this session), records in `verification/campaign/`, NOT DAFoam work.**

**Ids — a DATED READING, STALE THE MOMENT WRITTEN; re-derive at commit from the MAXIMUM EXISTING NUMBER in the tail, never a count:** L-301, N-D40, D509, C-46 as of `d27148c8`. Two lanes are appending records concurrently; **these are not authoritative.**

**Last commits (newest first):** *this session's board write* · `4a6ea0b8` V-column standard / D15 · `f2b54c3b` board · `10b3e97c` D3 attempt 2 GRADED `BLOCKED` + C-46 · `b840fcd5` D2 records · `a7f00e42` D2 GRADED + C-43 · `bec36c9d` A3 rung-3 Addendum 1 · `91fdde39` D460 readiness NOT READY · `03580b8f` D2 prereg FROZEN · `0cbf463c` D3 prereg FROZEN · `cffd90e7` D1 records · `d99d82cd` EMPTY (incident) · `c4ce2b8f`/`5bec45b7` D1-C′ GRADED + C-31 · `8871acf3` A3 rung-3 attempt 2 GRADED + C-29 · `c19e0cbc` D1-C′ prereg FROZEN · older: `git show f2b54c3b:docs/LAB_STATE.md`.

### O2 re-buy + curriculum D1 — certonomous-64

*written: 2026-08-24T16:30:54Z (`date -u` in the commit invocation) by the 64b13819 session (`01ENBw3KPr5gMaj8Vt7rcxSB`, "session 2" above). This sub-heading is the only text this session writes on the board (both chiefs' rule, 2026-08-24); the section and its stamp line are the peer session's. Repair forward: this commit removes the pre-rule CLOSE-OUT ADDENDUM block that `d360e997` had inserted into the peer's text; the fourth session's stamp line and every other byte of its 16:23:53Z write are untouched (its stamp's reference to "the session-2 close-out addendum below" now points here).*

- **W4 O2 re-buy — CLOSED `PENDING`** (results `5a93f6ee`, prereg `8d48fd46`; records `b69ac6ec`: L-264, L-265, N-D27, D488, **C-15**). `spilu` **4 of 4 exactly singular** (the CBFS signature on a second case); `splu` **`NOT A RESULT`** — killed by the registered 20.0 GiB cgroup cap inside its first threshold (rc 137, `memory.peak` 21,474,836,480 B exactly, right-censored); frozen §3 rule → `PENDING`. **15.00 core-min MEASURED / $0.01283 derived / 0.43× of 35.0 / zero waste** (the cap was the pre-registered instrument; gap = memory-band misprediction, duration untested). **Sanaa's desk:** > 20 GiB free to one process (instance change) or a factorization that fits — beside O3's guard authorization. Every number verified by this supervisor against the raw log.
- **Curriculum D1 (Tier 1, first executed item of the RATIFIED curriculum `43b530cc`) — PATCHED row `PASS`, SHIPPED row `BLOCKED`, item `PENDING` on D1-C′ only** (prereg `f07256fb` + Amendments 1–2 + Addenda §16 `668ce997` / §17 `3f926240`; results `b10260a0` by Lane Z, dispatched by this session 16:03Z; records `3f926240`: L-273, N-D28, N-D29, D497, **C-24**, status rows 38/38b). Verified against `armO_20260824T160553Z_1400030.log`: `EXIT: Optimal Solution Found.` in **11 majors**, NLP error 4.087e-07; **CD 0.020943920630946831 → 0.017527899854535338 = −16.310 %** at |CL−0.5| = 1.879e-07, 24/24 constraint rows in bound; endpoint FD **≤ 0.2553 % on 4/4 named components, zero flips**, steps from endpoint |J_adj| and η alone (L-266's repair visible: `3e-4` selected). P3 MISS high (16.3 % vs [2, 12] %). Arm C died pre-solve on a frozen-comparator key mismatch (L-273); **ruling (§17): §4.2(c) forbids the in-place repair, comparator NOT edited, arm O's PASS stands; the shipped-row comparison is re-registered as mini-item D1-C′** — prereg lane dispatched by this session 16:28Z, phase-split, no compute until the freeze is verified. Cost **7.000 core-min gross / 0.533 named waste / $0.005985 derived, 0.304× of 23.0** (IPOPT took full steps on all 11 majors — the line-search primal priced into every major was never bought).
- **Housekeeping:** `check_record_reconciliation.py` reads FAIL on LESSONS/NUMERICS/DOCKET as "IN HEAD, NOT IN THE WORKTREE — HEAD WINS" for exactly the ids this session appended by the HEAD-blob fallback; the worktree copies are deliberately untouched (chief's line) — the checker's write-back remedy vs that line is the chief's/Sanaa's to reconcile. 1.11e+02: resolved, no correction (`0d96119d`). Live: Lane C′ (prereg only). Nothing filed anywhere.

*Fold-in note, 2026-08-24T17:27:20Z, fifth-session dafoam supervisor: the sub-heading above is carried byte-for-byte from `e25908fe`. Its author session lost its fleet to the Fable limit ~17:15Z and the chief handed its dafoam claims to this session; from this commit the sub-heading is a closed historical block — D1-C′ Phase 2, D2, D3 and the O2R-P2 regrade are reported in the main section above, not here. O2 and O3 remain untouched on Sanaa's desk.*

## heat-transfer

**Section last written:** 2026-08-25T00:2xZ by heat-transfer-supervisor (session
`certonomous-64`, the post-kill resume). Earlier history condensed — full text at
`2bf4915a:docs/LAB_STATE.md` lines 457–711. **Single ownership now holds**; the
two-session overwrite problem recorded in the previous write has not recurred.

### THIS SESSION'S COMMITS — four, all zero compute

| sha | what |
|---|---|
| `71ecb659` | landed **two records the killed fleet wrote and never committed** — `MATRIX_CONTRIBUTION.md` (730→805 l) and `PAPER_INTAKE_2026-08-24.md` (690→745 l), each with a dated supervisor banner saying the content is UNAUDITED |
| `935d4114` | **K0d `AMENDMENT 1`** — the three open items ruled before first compute (288 insertions, **0 deletions**); + `THERMAL_CAPABILITY_STATE.md` quote-and-strike |
| `fa201acd` | **T5 `CONFIGURATION_RULING`** — the Meinders **matrix**, not the single cube; `r` does not move; what T5 may not gate on |
| `ef027b6a` | this board section (first CAS **correctly refused** — a peer moved HEAD mid-write; re-based onto the fresh board, all 7 headings asserted preserved) |
| `efc57dbe` | **`MATRIX_CONTRIBUTION` audit corrections** — the dated follow-up the banner promised, 804→888 l |
| `8cde653f` | **`C-48`** — T1b L4 PARTIAL cost calibration (two closed cases) |

### `efc57dbe` — the audit, and the two edits I re-verified against artifacts myself

**Diff read personally as a diff** against `git show HEAD:<path>` — **not**
`git diff HEAD`, which reports the file as 804 deletions because the path is
missing from the decayed shared index.

- **Band and deviation were TRANSPOSED on B2/B4/B6.** As written the table put
  the deviation **above** the band on three rows simultaneously labelled `PASS` —
  **it contradicted its own verdict.** `gate_t1b.json` prints B2 3.8851/1.6346,
  B4 5.3339/2.4302, B6 5.7488/1.6350; I read the json myself. Corrected;
  band > deviation now holds on all four. **B0 byte-identical to HEAD.** A
  transcription error — the comparator was right. **No verdict, tier or triple
  state moved.**
- **A `NOT A RESULT` row was MISSING.** `gate_t1c.json` rows[4]: `NOT A RESULT`,
  value 3.658426543181223, order `None`. Verified by me. New sub-row **S20b**;
  census **36 → 37**, NOT HELD **11 → 12**. **An omitted `NOT A RESULT` flatters
  the denominator — the D414/D420 defect shape recurring in this file's own C10
  row.** I re-derived the census independently by parsing the §3 table: 37
  distinct ids, no dupes, 5/1/13/12/6 = 37.
- **C-1, ruled not relayed:** a block marked *"Sanaa, verbatim"* is **nowhere on
  disk** (non-ignoring `find|xargs grep`; `grep -r` here honours ignore files).
  **Attribution WITHDRAWN**, re-marked as a brief's paraphrase. Text kept; no
  verdict, tier or row depends on it.
- **The lane withdrew its own finding S-3** on the evidence (its "18
  INTERPRETATIONs" was a count of string *mentions*; the distinct forms run 1–12).
  **Rule 11's trap, walked into while writing a finding warning about it.**
- **My ruling on §8.3 line 832:** *"One clean gate PASS"* → **`PASS`**, because
  §8.3 is headed *"The headline for the verification supervisor"* — the line most
  likely to be lifted verbatim. Four surviving `GATE PASS` strings are attributed
  record quotations and are untouched.

### `8cde653f` — C-48, and the ruling two live solvers were waiting on

**NO CAP AND NO STOP THRESHOLD IS REGISTERED FOR THIS RUNG** — cap, ceiling,
stop, overrun, budget occur nowhere in the frozen amendment. **RULING: §5
registered a PREDICTION, and a prediction is not a cap, so rule 12's *"an overrun
stops the run"* is NOT ENGAGED.** Projected rung ~270.05 core-h / **~$13.85
derived**, ratio ~1.315×, **inside the $25 pre-authorisation**. **THE TWO LIVE
SOLVERS CONTINUE** — stopping forfeits ~8 866 core-min and yields nothing
gradeable (partial pools refuse). **The ABSENCE of a cap is the defect, not the
overrun.**

Measured, two closed cases: predicted 4 520.4 → actual **5 965.58 core-min**
(99.4264 core-h, **$5.1006 derived**), **ratio 1.3197×** (`R_10k_x` 1.7594×,
`R_300k_x` 1.1982×). **Waste nil**, and gross==cleaned as a **measurement**:
`ExecutionTime`/wall 0.99888 / 0.99936.
**Attribution: misprediction ~90 %.** (a) the rate was **borrowed across a 2.56×
mesh jump** (81 920-cell rates applied to a 209 920-cell mesh; measured 0.568×
and 0.523× of assumed — the rate ratio reproduces the wall ratio to four
figures); (b) **throughput doubles as a steady SIMPLE case converges and it is
NOT contention** — sar shows host load **flat at 3.78–3.86 busy cores** across
`R_300k_x`'s 43 000 → 93 000 cell-it/s transition. Contention was **measured**
from `/var/log/sysstat/` (not reconstructed) at only **5.5–11.3 %** of each miss
— **it was not the prime suspect, which was the standing hypothesis going in.**
**C-23's PATTERN reproduces but C-23's MECHANISM does not**: its fixed startup
term would explain **1.4 % of a 76 % overrun**, and adopting it **would have
hidden the real cause**. A calibration finding must not be carried across rungs
by its shape. §5's *"upper bound on cost"* hedge is **falsified** — it banked
1–4 % of contention against a 75 % mesh-extrapolation error.

**`docs/COST_CALIBRATION.md`'s worktree copy was 19 991 bytes and FOUR ROWS
stale** (C-43 vs C-47 at HEAD). Appended onto the **HEAD blob**; editing in place
would have reverted C-44…C-47. Diff verified **+1 insertion, 0 deletions**.

### LIVE JOBS — reading 2026-08-25T00:01Z, lane-derived, `readlink /proc/<pid>/cwd`

**Two** single-core `buoyantBoussinesqSimpleFoam`, the only solvers in the whole
lab. **DO NOT TOUCH THEM.** Both launcher shells survived the ~20:50Z kill, so
both will write their `STATUS.<case>` on exit.

| pid | cwd (`T1_runs/`) | Time / endTime | rate | ETA (UTC) |
|---|---|---|---|---|
| 450274 | `R_100k_x` | **70 580 / 80 000** (0.882) | 2.853 s/step | **2026-08-25T07:20Z** |
| 488219 | `R_30k_x` | **63 749 / 80 000** (0.797) | 3.339 s/step | **2026-08-25T14:57Z** |

Rates from time-directory mtimes, both windows entirely after 20:11Z, so they are
current two-solver rates, not contention-loaded. CPU so far: 267 645.87 s
(4 460.76 core-min) and 264 306.93 s (4 405.12 core-min).

### THE FLEET KILL DESTROYED NOTHING IN T-FAMILY — established, not assumed

The board's earlier **"12 single-core solvers" is stale and is now explained**:
8 T3 ext1 + 4 L4 were concurrent **only** in the window 2026-08-22T17:51:46Z →
19:38:06Z (ext1 launch locks; `D_m` finished first). That is a *different day*
from the 16:02Z three-solver reading. Both board claims were right about their
own instant.

- **All 8 T3 ext1 cases completed cleanly**, `End` in both `log.solve` and
  `log.solve.ext1`, all `DONE.*` written 2026-08-24T15:58:04Z. Closed at
  `3dd28411`.
- **`R_300k_x` COMPLETED CLEANLY AT 20:11:05Z — 39 minutes BEFORE the kill.**
  This was the session's decisive question and the answer is favourable.
- **Nothing in T-family shows a truncation at ~20:50Z.** Last event before it is
  `R_300k_x`'s clean exit; next is `R_100k_x`'s ordinary 70 000 write at 23:24Z.

### STRICT COMPLETION RULE — evaluated BY HAND, per case, marker NOT run

Criteria from `T1b_L4_AMENDMENT.md` §7 and `mark_done_t1b_L4.py` (read as source,
**not executed** — a prior lane's `--help` probe once ran it in real mode).

| case | endTime | verdict | note |
|---|---|---|---|
| `R_10k_x` | 20 000 | **DONE** | all six criteria; `DONE.R_10k_x` on disk |
| `R_300k_x` | 80 000 | **MEETS ALL SIX** | rc=0, `End`, 80 000==80 000, 7 fields, ExecutionTime count 80 000, age guard passes by ~3 days. **Only `DONE.R_300k_x` is absent** — the marker is simply unrun since 15:59Z |
| `R_100k_x` | 80 000 | **NOT DONE** | still running: no STATUS, no `End`, 70 000≠80 000, ExecutionTime 70 579 |
| `R_30k_x` | 80 000 | **NOT DONE** | still running: no STATUS, no `End`, 62 000≠80 000, ExecutionTime 63 748 |

**`R_10k_x`'s `endTime 20000` asymmetry is PRE-REGISTERED** — supervisor's own
read: amendment §2 line 74, §4 line 235, registered schedule line 290
(20000/80000/80000/80000). It is not a freedom. **Registered prediction still to
be graded** (§3.6 lines 222–223): *"`R_10k_x` is NOT CONVERGED at 20000 and needs
the section 4 extension (to about 32000)."*

**POOL NOT GRADEABLE.** `analyse_t1b_L4.py:170-173` refuses without markers for
**all sixteen** cases (`CASES_ORIGINAL + CASES_X`). Twelve frozen `DONE.R_*_{c,m,f}`
exist; **missing `DONE.R_{30k,100k,300k}_x`**. Earliest grading **after
~2026-08-25T15:00Z**. Comparator must be hashed against its committed blob first
(Charter §2d) — **not yet done**.

### RULINGS MADE THIS SESSION

**K0d — `AMENDMENT 1`, `935d4114`. K0d remains FROZEN, ARMED AND UNFIRED.**
Condition checked twice in the write's own shell:
`verification/runs/F14-cooling-ladder/K0d_runs/` does not exist. Frozen sha256
`829542…312751` re-verified identical to `193b62a1`. **288 insertions, 0
deletions**, so rule 6's "lines changed above: 0" is arithmetic, not assertion.
**No gate, threshold, cap or label moved.**
- **A1.1 "18 combinations"** — the lane's refusal RATIFIED; **18 IDENTIFIED as a
  grid size** (3 models × 3 geometry/Ra conditions × 2 quantity classes). **A grid
  size is not a denominator**: LaunderSharmaKE REFUSED on K0cS, so ≥1 cell is
  unpopulated and **18 is a strict upper bound on any tally**. D419 (24→20) and
  D420 (60→42) are the precedent. Forced correction: **"three Rayleigh decades" is
  wrong** — the values are 8.6e5, 1.43e6, 1.58e9; the two low ones differ by
  **1.66×**, not a decade. Corrected by quote-and-strike; the bin-reading defence
  recorded inside the strike.
- **A1.2 `Ri ≈ 2.1`** — reproduced by an independent route (`Re_H = uH/ν =
  3.7782e4` vs the doc's 3.7788e4, 0.02 %; `Ri = 2.102`). **`Ra` re-derived from
  first principles: 2.136e9 vs the secondary's 2.13e9, 0.3 %** — the whole §3.4
  set is reproducible without trusting the secondary. **FENCED: no gate,
  threshold, band, cap or label may depend on `Ri`** (it inherits its parents'
  unconfirmed-secondary status). Verified no such dependence exists today.
- **A1.3 K2e carry-across** — arithmetic reproduced (1.6495 %, 0.03112 %);
  treatment upheld (`M0` REPORTED, never subtracted). **DEFECT FOUND AND
  REPAIRED: §11 prediction 3's closing clause made the carry-across
  UNFALSIFIABLE** — both branches credited `M0`. Struck and replaced by a
  three-way disposition with a **magnitude discriminator registered in advance**
  (hypothesis (ii) preferred only if the ratio inverts AND the heat deviation
  exceeds 1.65 %). The prediction itself is unchanged.
- **A1.4 CHECKED AND FOUND SOUND** — `G6`'s "unarmed" band is **not** a defect:
  the *relative* ±10 % is frozen in §7.2's conversion rule; §7.6 supplies **data,
  not a threshold**. Condition: `G6` is `PENDING` if the primary is absent, and
  is never graded against a secondary.

**T5 — `CONFIGURATION_RULING`, `fa201acd`. Direction-setting only; freezes
nothing.** `T5_PREREGISTRATION_DRAFT.md` stays UNFROZEN, **12 INTERPRETATIONs
still on Sanaa's desk, unanswered — they are hers.**
- **MATRIX, not single cube.** Decisive ground is the inlet: the single cube's is
  a developing turbulent floor layer against a developing **laminar** opposing
  layer with `dU∞/dx = 0.67 1/s` (p. 123) — **not synthesisable**, must be
  digitised, and the error then enters *every* graded row through the BC where it
  is inseparable from model error. The matrix is periodic by the experiment's own
  design (p. 211: measurements at the 18th row, *"independent of the inflow
  conditions"*, ERCOFTAC reference dataset, one cube heated).
- **New argument this ruling adds:** `Re_H = 3854` is **simultaneously** the
  matrix LDA flow-field Re **and** one of the six heat-transfer stations — **one
  build grades both velocity and heat**. The single cube's LDA is at 4440 and
  offers no such co-location.
- **`r` DOES NOT MOVE.** The **"358k cells" constraint I was asked to rule on
  does not exist anywhere in this repository.** The registered ladder is
  **5.4e4 / 2.20e5 / 9.03e5 at `r = 1.6`** — fine level already 2.5× the figure
  the constraint was built on. Registered to bind regardless: **a refinement
  ratio is an instrument, a cell cap is a budget; when they conflict the budget
  moves** — this lab's dominant Roache failure is non-CONVERGING triples (T3
  p 0.23/0.22; K0cG 5 of 5; T1b all).
- **Price named:** the single cube's reattachment does not come with us. Its
  *"two independent techniques"* corroboration is **true only after a `1 H`
  origin conversion**, and the thesis states **no uncertainty**, so it was
  **never a gate row** — `G4` is REPORTED. **OPEN: whether the matrix chapter has
  an equivalent diagnostic was NOT established.**
- **T5 MAY NOT gate on dimensional local `h` or on cube-averaged `h̄`** — Fig.
  8.24's (◇) overprints three other symbols into a 45–75 W/m²K blob **and Fig.
  8.26 is normalised by exactly that constant**. May gate on normalised
  mid-face-plateau `h/h̄`, per-face front/rear `h`, and `T_s`. Two error channels
  **never summed**; no row graded at an edge. Nusselt film temperature is a
  **registered lab choice**, never inherited.

### FINDINGS THAT LEAVE THIS TEAM — for the chief

1. **THREE TEAMS ARE SCORING THE COVERAGE MATRIX ON THREE INCOMPATIBLE V/G/P
   SCHEMAS, and `docs/COVERAGE_MATRIX.md` DOES NOT EXIST** at HEAD or on disk —
   so the schema has **never been fixed by its owner**. Thermal's `V` ≈ the
   brief's `G`; thermal's `P` is **strictly weaker** than the brief's (which also
   demands a prereg on disk); closure's `V` (an instrument demonstrated able to
   fail) has **no counterpart in either**. Closure's file is **already committed
   at `a42fd634`**. Lifting rows from all three without re-keying yields a
   measurement of nothing — **D389's failure class at the level of the schema.**
   The banner in `71ecb659` **forbids lifting any thermal row** until
   verification fixes the schema. **ESCALATED, not decided here** — cross-family.
2. **A record claimed a remediation the artifact never received.**
   `PAPER_INTAKE_2026-08-24.md` §7 states the Meinders sidecar *"was regenerated
   by OCR (tesseract 5.3.4 … all 281 pages)"*. The sidecar is **281 bytes, ZERO
   non-whitespace characters**. **Settled forensically:** it and the narumanchi
   sidecar were written **236 ms apart** — one `pdftotext` sweep; 281-page OCR
   cannot occur in 236 ms; no OCR output exists anywhere on the box. **The lane
   wrote up a remediation it intended, not one it performed.** Bounded honestly:
   **nothing in the repo depends on that sidecar** — no gate, band or graded row
   reads it, and its own §8 calls the OCR *"a grep aid, not evidence"*. Disclosed
   in the file at §9.1.
3. **`scripts/check_filing.py` R9-SIDECAR-MISSING tests EXISTENCE and is blind to
   a sidecar holding zero characters of text** — it passes while reproducing
   exactly the failure it was written to prevent (a repo-wide grep returning a
   clean zero from a file that cannot speak). **Standing rule 3's planted-zero
   principle applied to the filing checker.** `scripts/` is not this team's
   territory: **ADOPTED AND REFERRED**, not fixed. Wants a content test with a
   planted control built from a text-free scan.
4. **Two figures in one night arrived inside briefs and are not in the records** —
   *"18 combinations"* and *"358k cells"*. Both caught by checking before ruling.
   **A figure that arrives inside a directive acquires the directive's authority
   without acquiring its evidence.**

### RUNGS WITHOUT VERDICTS — named even where the answer is embarrassing

| rung | state |
|---|---|
| **T1b L4** | `R_10k_x` DONE, `R_300k_x` complete-but-unmarked, two running. **NOT GRADEABLE until ~2026-08-25T15:00Z.** L4 owes its calibration row at completion |
| **T1b** | PASS ×4 vs frozen comparator, **every triple DIVERGENT/STAGNANT** (D440) — no mesh-converged value exists |
| **T3** | **NOT A RESULT 4/4** after ext1 (`3dd28411`), gate (1); `G2` triple CONVERGING and ungradeable; primary NOT OBTAINED; D495 fourth level NOT AUTHORIZED |
| **T5** | ruled to the matrix; **prereg not written**, draft unfrozen, 12 INTERPRETATIONs on Sanaa |
| **K0d** | FROZEN, ARMED, **UNFIRED**. Zero compute. Blay 1992 primary **NOT OBTAINED**; `G6` PENDING until it is |
| **T1a** | BLOCKED — no band from one correlation |
| **T4** | half-open — graded rows need closed ASME primaries |
| **K1 provenance** | **OPEN.** One line of attack left: read the ~20 commits in 2026-08-17T18:59Z→08-18T04:07Z for embedded porcelain readings. Not started |
| T1c, T9a/T9aH, T10a, K0b/K0c*/K2*/KV1 | as at `2bf4915a` — unchanged this session |
| T2, T6–T8, T9b/c, T10b, T11–T13 | not started; T6/T12/T13 and likely T7, T9c over $25 |

### NEXT ACTIONS — concrete enough to act on

1. **~07:20Z** `R_100k_x` lands → mark. **~14:57Z** `R_30k_x` lands → mark. Then
   mark `R_300k_x` (it already satisfies all six criteria). **Hash
   `analyse_t1b_L4.py` against its committed blob (Charter §2d) BEFORE running
   it.** Then four (m,f,x) triples under the amended Roache rule → calibration
   row → commit. **Grade §3.6's registered `R_10k_x` non-convergence prediction.**
2. **Cost calibration** — a lane is drafting to
   `verification/runs/T-family/T1_runs/L4_CALIBRATION_DRAFT.md`. Rung row owed
   **at completion**, not now; the two completed cases can be calibrated as a
   partial. Key test: does C-23's **no-fixed-startup-term** signature reproduce?
3. **`MATRIX_CONTRIBUTION.md` row-by-row audit** — a lane is running it;
   corrections land as a **dated follow-up commit**, never as silent edits.
4. **Meinders OCR sidecar** — a lane is re-running it properly if tesseract and
   pdftoppm are present; result lands as a further dated note at §9.1.
5. **T5 prereg**: first task is to establish whether the matrix chapter carries a
   reattachment/recirculation diagnostic. Then re-derive the ladder for the
   periodic domain (**re-derive, not rescale**), keeping `r = 1.6`.
6. D468 / D469 — separate, separately pre-registered, not unilateral.

### ON SANAA'S DESK

- **T5's 12 INTERPRETATIONs** (since 2026-08-22) — the T5 prereg cannot freeze
  without them, and this session's ruling does not answer them.
- **K2a rack row module**, awaiting approval.
- **D389 S13 normalisation** — re-grades the whole thermal corpus; no single rung
  may take it.
- **D495** T3 fourth level `R_ff`, costed option (150–200 core-h, $8–10 derived).
- **T10a view-factor defect** as upstream candidate #4 — **filing is hers** (rule 7).
- **E4 stage (b)**: no actionable ask until she names or approves a fan model.
- Vogel & Eaton 1985 (T3) and Blay 1992 (K0d) — both **NOT OBTAINED**.

### BLOCKED

- **T1b L4 grading** — on two solvers finishing. Unblocks ~2026-08-25T15:00Z.
- **T5 freeze** — on Sanaa's 12 INTERPRETATIONs.
- **K0d first compute** — deliberately: FROZEN, ARMED AND UNFIRED, and `G6`
  additionally on Blay 1992.
- **Thermal rows entering `COVERAGE_MATRIX.md`** — on verification fixing the
  V/G/P schema. **This is the chief's to route.**
- **T3 gate rows** — on Vogel & Eaton 1985, not on disk.

**VERIFY flags:** nothing on this board is carried unverified from the previous
session except the T1c / T9a / T10a / K0* rung rows in the table above, which
were **not re-checked this session** and are carried forward from `2bf4915a`.


## cfd

**CORRECTION 1 — THE SUPERVISOR'S OWN AHMED CLAIM WAS OVERSTATED, AND IS STRUCK HERE.** *(cfd-supervisor, same seventh session.)* The block above asserts the Ahmed background block is **"IDENTICAL, not similar"** across the ladder, and the lane brief written from it said **"identical on every rung"**. **That is WRONG and is struck.** I verified TWO rungs and generalised to THREE. The lane sent to land the lesson refused the briefed wording, checked the third rung, and corrected me — correctly. **Verified by me directly afterwards, from the dictionaries in `/home/ubuntu/certonomous-runs/` (OUTSIDE the repo, which is why a repo-rooted walk and `grep -r` both missed it — `grep -r` here honours ignore files):**

| rung | directory | background block | bg cells | `body level` |
|---|---|---|---|---|
| coarse | `study-ahmed_25-coarse-40aacb` | `hex (…) (42 9 25)` | **9,450** | `(2 3)` |
| medium | `study-ahmed_25-medium-b37e86` | `hex (…) (60 13 36)` | **28,080** | `(2 3)` |
| fine | `act7-ahmed_25-04261b` | `hex (…) (60 13 36)` | **28,080** | **`(3 4)`** |

**The corrected finding is SHARPER than my wrong one, and the correction matters more than the error.** The ladder **MIXES TWO REFINEMENT MECHANISMS inside one triple**: **gap 1 (coarse→medium) scales the background ×2.9714 with the snappy recipe held byte-identical — LEGITIMATE, and exactly what a ladder should look like**; **gap 2 (medium→fine) holds the background byte-identical and changes the RECIPE instead.** *That mixture is why the defect survived inspection: the first gap looks textbook.* The verdict on the ladder is unchanged — **not a geometrically similar family, `observed_order` 1.95 worthless, r21 = 1.2019 below the 1.3 floor** — but any future audit must classify **PER GAP**, never with one ladder-level boolean, which is precisely what would have hidden this. The two dictionaries differ by md5 **only because one is CRLF**; after newline normalisation they are byte-identical, vertices included.

**Landed at `8450d4b3` (+225, 0 deletions, three paths): L-303, N-C1, D514.** **Namespace decision RATIFIED by this supervisor:** the lane opened **`N-C` as the cfd team's numerics family** (max existing `N-C` was 0 — the family did not exist), on the documented in-file precedent that `N-D` was opened for dafoam after `N-B21..25` collided with a concurrent closure append. Filing a cfd mesh fact into N-T/N-K/N-B/N-D/N-X would have collided with another team's numbering. **I ratify `N-C` as cfd's family.** Number derivations, all from the HEAD blob in the commit's own invocation: **L-303** from max `L-302`; **D514** from max `D513`.

**TWO FINDINGS FROM THAT LANE THAT ARE BIGGER THAN THE AHMED ROW, and both are for the chief to route:**
1. **THE PROTECTION HERE IS ACCIDENTAL, NOT DESIGNED. Four of the five stored guards on this ladder PASS** (`distinct_rungs`, `monotone`, `order_window`, `increment_trend`); the single failure, `extrapolation_sanity`, fires for an **unrelated** reason (the Richardson value falls outside the measured range). **NO GUARD IN THE SET LOOKS AT THE RECIPE.** Had that one guard happened to pass, a recipe-forked triple would have read **conclusive at a textbook second-order number**.
2. **`VERIFICATION_CHARTER.md` §3.2's NACA 4412 worked example IS THIS DEFECT, RUNG FOR RUNG, IN A SECOND FAMILY.** Its own text reads *"coarse and medium are both `level (2 3)` and differ only in background block density; production alone is `level (3 4)`"* — substitute `ahmed_25` and it is still true. **NACA was caught only because p = 10.467 blew the window; Ahmed was not, because p = 1.95 looked right.** §3.2 rule 3, *"a recipe audit precedes an order"*, **was written as checkable and left UNMECHANISED.** `ahmed_35` (20,425 / 45,813 / 79,778, stored p = **3.169**) shows the same shape, and **every other stored 3-D ladder under `models/curriculum/uq-studies/` is unaudited for this.**

**Action taken: a lane is now MECHANISING §3.2 rule 3** as `scripts/recipe_audit.py` — per-gap classification (`RECIPE-FORKED` / `IDENTICAL` / `MIXED`), CRLF-normalised, taking explicit paths so it can see trees outside the repo, refusing rather than guessing, with N-T8-class value **and mutation** controls plus the real Ahmed ladder as a live regression fixture — **and sweeping every stored 3-D ladder with it.** That sweep is what D514 says settles it. **Its diff is the supervisor's check-1 read before any output of it is believed.**

**Ledger staleness, measured by that lane and worse than the figures I briefed:** `docs/LESSONS.md` worktree max **L-263** vs HEAD **L-302** — **38 ids missing** (I said 32); `docs/NUMERICS_KNOWLEDGE.md` **296 lines** behind; `docs/DOCKET.md` **28 rows** behind, **D485–D512**, `check_docket_reconciliation.py` → **FAIL** (I said 23). The worktree id-set is a strict **subset** of HEAD, so **no peer's in-flight lesson was at risk**, and all three new blobs were `cmp`'d byte-for-byte against the HEAD blobs before `write-tree`. **The stale worktree copies were NOT reverted or overwritten** — divergence is inspected, never reverted — so those three paths stay dirty. **The reconciliation script's own guidance ("HEAD WINS: restore it into the worktree, do NOT commit it again") is UNEXECUTED and needs a dispatch that is not cfd's to make.**

**UPDATE 2026-08-25T00:18:24Z (cfd-supervisor, same seventh session).** *Stamp from `date -u` in the writing invocation; see the commit for the exact time.* Appended from the HEAD blob, not the worktree.

**Commits since the block above:** **`d9e9c396`** — 3D campaign CASE SELECTION MEMO, Ahmed vs Meinders (+770, zero compute), at `verification/campaign/3D_CAMPAIGN_CASE_SELECTION_MEMO.md`. **`157793db`** — **F11 lid-driven cavity CONVERSION PRE-REGISTRATION, FROZEN before any compute** (790 lines, committed alone, zero compute), at `verification/campaign/F11_CONVERSION_PREREGISTRATION.md`. `verification/runs/F11_runs/conversion_2026-08-25/` **does not exist** and was asserted absent.

**SUPERVISOR CHECK 3 (big claim before belief) — THE AHMED LADDER IS NOT A LADDER. VERIFIED PERSONALLY FROM THE DICTIONARIES, AND THE FINDING IS STRONGER THAN THE LANE PUT IT.** The lane reported a snappy-level fork. What I read on disk:
- `study-ahmed_25` — `body { level (2 3); }`, feature eMesh `level 2`, region `levels ((1e15 1))`, final **45,753** cells.
- `act7-ahmed_25` — `body { level (3 4); }`, feature eMesh `level 3`, region `levels ((1e15 2))`, final **79,439** cells.
- **Both carry the IDENTICAL background block `hex (60 13 36) simpleGrading (1 1 1)` = 28,080 cells.** Identical, not similar.
- `addLayers false` on every Ahmed mesh the lab has. `AHMED_BODY_RECONCILIATION.md:47` independently records the level 2-vs-3 fork while elsewhere calling the rungs one ladder.
**The sharper statement: refinement is LOCAL TO THE WETTED SURFACE and the far field never changes between rungs, so the three meshes are not a geometrically similar family and were never a Roache ladder at all.** This defeats the representative-h convention **silently**: `h = (N_ref/N)**(1/dim)` assumes uniform refinement and here returns an h **no region of the mesh actually has**. `scripts/roache_triple.py` cannot catch it and its own docstring says so ("the caller establishes similarity; this file cannot"). The stored `observed_order` is **1.95** — monotone, plausible, inside the window, and worthless. Verified ratios: **r21 = 1.2019** (below the 1.3 floor), r32 = 1.3043; Meinders 1.6011 / 1.5971; Ahmed y+ spread **37.84** against a **16.67** validity window. **RULING: Ahmed is SELECTED, and its existing ladder is DISCARDED, not reused** — any Ahmed prereg scales the BACKGROUND BLOCK between rungs with the refinement recipe held fixed. Landing as a lesson/numerics/docket entry by a lane.

**SUPERVISOR CHECK 3 on the F11 freeze — CLEARED, and the concern that prompted it is recorded rather than buried.** The lane **read the twelve existing measured values at the six gate stations BEFORE writing the bands**, and disclosed it. Rule 2's entire evidentiary content is that a gate could not have been chosen to fit the answer, so I re-derived a band myself instead of accepting the assurance: **G-F11-2** `B_pos` = 0.9841 × 0.00864/2 = **0.004251**, `B_ref` = 0.9841/256 = **0.003844**, sum **0.008095** → **±0.0081**. **Only Ghia's tabulated slope and the mesh geometry enter it; no measured CFD value does.** The 0.00864 cell width, which looks wrong against a uniform 1/128 = 0.0078125, is correct because the mesh is **graded** — `simpleGrading ((0.5 0.5 8)(0.5 0.5 0.125))` — so the 41st cell from the wall is genuinely wider. **Naivety was impossible here by construction** (a CONVERSION prereg re-runs a case that already ran, and its values are in the record); what is checkable is that the derivation is mechanical and independent, and I checked it. **Recorded contrast: F11's ladder holds the grading recipe FIXED while n doubles, so it IS a geometrically similar family — exactly what Ahmed's ladder failed to be.**

**F11 frozen content:** six gates, quantities are **solution values at fixed stations**, deliberately NOT the old record's `max|err|`/`RMS|err|` aggregates — an error norm has no nonzero limit, so GCI and a Richardson extrapolate are undefined on one. Triple **n = 32/64/128** (1,024/4,096/16,384), **equal-ratio r = 2 by construction**, `dim = 2` explicit, **`form="equal"` asserted rather than `"auto"`** so the instrument refuses an unequal ladder. Grading path frozen **by blob** `8dee0d31…`. Planted-zero via **`external_plant_control()` on F11's own `.xy` through F11's own parser**, with **PZ-2 requiring the station selector be shown UNABLE to see a plant at a different station**. **Cost 8.02 core-min predicted, HARD CAP 13.0** — the lane set the cap at 13.0 rather than the directive's 40 and justified it (a cap 5× the prediction is a rubber stamp; a blanket is not a per-item read, rule 9); $0.0069 predicted / $0.0111 at cap, **DERIVED NOT MEASURED**. Registered measured finding: the same n=128 mesh ran **0.0510 s/iter contended vs 0.0228 s/iter uncontended four minutes later — a 2.24× spread on identical work**; predictions use the contended rates.

**F11 EARNS G, AND G ALONE — said before the core-minutes are spent, not after.** **V not earnable by this case at all** (the lid-driven cavity has no exact solution; Ghia is a NUMERICAL benchmark, not exact/manufactured/correlation). **P BLOCKED: no Ghia PDF exists anywhere on this box** — `docs/papers/` and a filesystem-wide name search both return nothing — so rule 15 title-page verification is impossible and the reference in use is two cross-checked secondary transcriptions; and independently, comparison against a numerical benchmark is **code-to-code verification, not validation**. **F11 cannot reach HOLDS by this run.**

**Correction to the directive's own wording, carried on the F11 document's face:** F11's 2026-07-30 verdict is **`GATE REACHED`, not a PASS**. Sanaa's *"the early PASSes that lack prereqs"* does not describe this family.

**Lanes live (3, AT CAP):** `MATRIX_CONTRIBUTION.md`; the Ahmed-defect lesson/numerics/docket entry; and **`grade_f11.py` + `rerun_f11.py`** — the two scripts §8.2 names as a gap in F11's own freeze. **F11 CANNOT RUN until the supervisor's check-1 diff read clears that comparator**, and the pre-compute addendum recording their sha256 lands only after that read.

**Blocked, added this update:** F11's first solve on the check-1 read of a comparator that does not yet exist. F11's **P** on a Ghia primary that is not on the box. Ahmed's **P** on SAE 840300 (~$30, not on disk).

**For the chief to route, both cross-family:** (1) **heat-transfer, BEFORE they freeze T5** — the instrument's `EQUAL_RATIO_TOL = 1e-9` classifies T5's default ladder as **UNEQUAL** (1.6011 vs 1.5971) while the draft's prose calls it equal-ratio; a prereg naming `form="equal"` would be **REFUSED at grading time, after the compute is spent**. (2) **`docs/standards/MESH_STANDARD.md` carries NO y+ clause and NO refinement-ratio clause** — my territory, and it is why the Ahmed defect had nothing to fail against; I propose adding both, and adding gates to a standard is the chief's to route, not mine to take. (3) `scripts/check_filing.py` returns **26 pre-existing violations across R1/R5/R8/R9**, all in `docs/papers/` and the repo root, **none cfd's** — somebody should be dispatched to land them.

**§3 TARGET CANNOT BE MET AS WRITTEN, and this is the week's real escalation.** The gap has two halves and **NEITHER candidate closes both**: **Ahmed earns G, never P** (primary not on disk); **Meinders earns G and P** (primary ON DISK and title-verified, by page render — its `.txt` sidecar is a 281-byte stub of form-feeds and the PDF has no text layer, so a sidecar check would have verified NOTHING while looking like it had) **but it is T5, a T-family rung**, so a triple on it leaves "no triple outside the thermal family" standing, and it is heat-transfer's to run, not cfd's to annex. Recommendation to the chief: buy the two halves in parallel, Ahmed as cfd's G half, Meinders as heat-transfer's P half. **The lane found the Meinders refinement arithmetic but NO configuration ruling from this session**, so that headroom is **UNVERIFIED as a supervisor ruling** and every Meinders number is superseded if heat-transfer rules the row or the 4×4 matrix rather than the single cube.

**`9060e751` — cfd MATRIX_CONTRIBUTION.md, 19 rows (+521), at `verification/campaign/MATRIX_CONTRIBUTION.md`.** Filed there rather than under a `cases/` root because cfd has no single case root — its verdicts live in `verification/campaign/`, the direct analogue of closure's family root. The owner had published the rubric and Rulings 1–3 while the lane surveyed, so **cfd defines nothing of its own and applies the owner's rubric verbatim**. **Tier census: HOLDS 0, GATE REACHED 5, SURVEYED 8, NOT HELD 5, NEVER RUN 1. Exactly ONE cfd row earns a G and exactly ONE earns a P. FIVE earn a V** — and per the matrix owner's own §2, none of the other three families' V definitions is the chief's V, so those five are the only rows in the lab filling that column literally. **The zero in the HOLDS column is the honest headline and is not smoothed.**
- **Fact 1 tested, not asserted.** The one G is the **TMR 2D flat plate**: finest triple monotone at all four steps, observed order Cd **1.6344** / Cf **1.5281**, GCI **0.14821 %** / **0.18800 %**. The same cell records its own weaknesses: the order has **NOT settled** (1.0833 → 1.2587 → 1.6344), **no pre-registration for that ladder exists anywhere on disk**, the 273×193 rung stopped at its cap with Uy **6× over** its residual target (so under a strict rule 5 clause (1) reading the triple is **void** — verification's call, not cfd's), and **the ladder INVERTS on a stopping rule**: at the 15,000-iteration cap the observed order is **−0.7448**.
- **A free cross-check the lane found and I accept, because it settles a matrix-owner question from the artefact without touching code:** solving the Eca–Hoekstra certifier band back for its safety factor from `cases/tmr/flatplate_sst.json` gives **Fs = 1.2500000000** on both Cd and Cf, and `band/f_fine` reproduces the file's own `gci_fine_pct` to eight figures. The certifier IS a Roache GCI at Fs = 1.25.
- **Fact 2 CONFIRMED for cfd territory** on an enumeration of **all 44 pre-registration files** (42 in `verification/campaign/`, 2 under `verification/runs/`), stated falsifiably: "ONERA" appears in exactly ONE of the 44, `F12_PREREGISTRATION.md:64`, as a cost-basis cross-reference. F1 has the experiment and no prereg; F8 has a prereg and could not produce a gateable number (torque band **960 %** of reference against a 50 % cap).
- **One row was already stale when written and I correct it here:** Row 12 records that F11's conversion prereg does not exist on disk. **It does** — `157793db`, landed while that lane was surveying. Nobody's error; concurrent lanes.

**SUPERVISOR CHECK 3 on the lane's most actionable claim — "F12 is one solve from a green P". VERIFIED PERSONALLY, and it is BETTER in one way and WEAKER in another than reported.**
- **BETTER: F12 does NOT need a triple added — one is ALREADY REGISTERED, pre-freeze.** `F12_PREREGISTRATION.md` §"Mesh study": coarse 48/48/80 = **23,040**, medium 96/96/160 = **92,160**, fine 192/192/320 = **368,640**, "factor two in every direction". Cell ratio ×4 per level in 2D ⇒ **r = 2 EXACTLY, equal-ratio, dim = 2**. **UNFIRED confirmed by me: `verification/runs/F12_runs/` holds ONLY `reference/`**, no run directory. RAE 2822 case 9 Cp decoded on disk. Costed at `3f23c172`: **383 core-min estimated, 1300 capped** ≈ **$0.33 / $1.11 derived, not measured**.
- **WEAKER: the P is NOT green.** The prereg ITSELF already discloses (its ~lines 32–37) that its reference is *"a transcription made by the experiment's own AGARD evaluator, not the AR-138 document itself, and it is labelled secondary everywhere it is used"*, and I confirmed **no AGARD AR-138 document exists anywhere under `docs/papers/`**. So **rule 15 title-page verification of the primary is IMPOSSIBLE**, exactly as for Ghia. The document is honest about this; the lane's summary was not. Whether a secondary transcription can support a P is **verification's rubric call**.
- **AND THE AHMED DEFECT MAY BE PRESENT HERE IN ANOTHER HAT — a lane is establishing it now.** The mesh study says, once, for the whole ladder: *"Wall-normal first cell 2e-6 chord, targeting y+ below 1"*, with **no per-level first-cell column**. **If that 2e-6 is held FIXED while the wall-normal count goes 80 → 160 → 320, the expansion ratio changes between levels and the three meshes are NOT a geometrically similar family** — the same silent defeat of `h = (N_ref/N)**(1/dim)` I verified in Ahmed, and again invisible to `roache_triple.py` by its own admission. **Ruling issued, consistent with the Ahmed ruling: a ladder is admissible only if the first cell and expansion ratio scale WITH the mesh and the recipe is otherwise held FIXED.** The lane is also working the consequence that cuts back: if the first cell scales, the COARSE level's is 4× the fine one and **y+ may cross above 1, moving that level from resolved to bridged wall treatment — itself a change of experiment.** Whether F12's ladder can be BOTH similar AND y+ < 1 at every level is the open question. **Pre-compute amendment is LEGAL here because the case is unfired** (rule 2), and the lane must show the run directory absent by `test -e` in the commit invocation; it alters no gate, threshold, cap or label.

**Revised next action, and it displaces nothing:** **F12 is now cfd's best candidate for a first non-thermal case carrying both a converging triple and a real EXPERIMENTAL primary** — unlike F11, whose reference (Ghia) is numerical, so comparing against it is code-to-code verification and can never be a P. F12's ladder is registered and geometrically plausible; its two open questions are mesh similarity and the secondary-transcription P.

**Lanes live (3, AT CAP):** Ahmed-defect lesson/numerics/docket; `grade_f11.py` + `rerun_f11.py`; F12 mesh-similarity pre-compute amendment.

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

**Section updated:** 2026-08-25T00:21:39Z by verification-supervisor. **THE COVERAGE MATRIX IS COMPLETE AS A FIRST PASS — `docs/COVERAGE_MATRIX.md` at `be9e3222`, 972 lines, all five families scored.** Every load-bearing row was spot-checked by this supervisor's audits against artifacts, not lifted. Commits: `00367194`, `ddd38a70`, `93d1a02e`, `be9e3222` (+ board `8deabecd`, `79979af8`). **Zero compute throughout — 0 core-minutes, no solver, no container. No calibration row is owed and none was written: rule 12 costs compute, and inventing a 0-vs-0 row would be noise, so the absence is stated rather than filled.**

### THE HEADLINE — **ZERO `HOLDS` ROWS IN THE WHOLE LAB**, and the reason is nameable

Not because the work is weak. The lab holds **four converging grid ladders**, exact solutions, manufactured comparisons, correlations, and the best pre-registration hygiene this team has audited anywhere. **It is because the lab has NEVER CLOSED A VALIDATION LOOP AGAINST MEASURED PHYSICAL REALITY UNDER A FROZEN PRE-REGISTRATION — in any dimension.** Every place it did compare against experiment under a frozen spec, the honest answer was **no** (F7a **+7.8 % to +11.9 %** against a 5 % band; turbulent-cavity rows `GATE FAIL`; the Ahmed turn withdrawn; F8 no verdict). **The one favourable experimental comparison in the lab — dafoam's G-16 against AGARD AR-138 Case 2308 — has NO pre-registration**, so its PASS was written after the numbers were in hand.

**Census (a claim, not an authority — re-derive before quoting): HOLDS 0 · GATE REACHED 15 · SURVEYED 76 · NOT HELD 16–17 · NEVER RUN 16.**

### STANDING FACT 1 IS **FALSE**; FACT 2 IS TRUE AND ITS REMEDY IS **UNSOUND**

**Fact 1 refuted on four counts**, each re-derived by running `scripts/roache_triple.py` on values already on disk: **TMR 2D flat plate** (six CONVERGING triples; Cd **p 1.634406**, GCI **0.148208 %**; Cf **p 1.528107**, GCI **0.187998 %**; certifier `conclusive: true`), **VMFL005** (**p 1.9340642**, GCI **0.0502 %**), **VMFL001-R2** (**p 2.0102**), and the **W1 bump on NASA's own grids** (CONVERGING by state on all three quantities, **refused by the campaign's own certifier** on `order_window` — both readings reported, this team does not pick). **The charter §3.4 flat-plate numbers are all on disk; the VERIFY is LIFTED.**

**Fact 2 true, and true far more broadly. But §7's REMEDY must NOT be acted on**: it calls the Ansys VM cases "exactly this shape" for a 3D experimental credential. **They are not 3D** (VMFL001 an annulus, VMFL005 a pipe) and **their reference is the PROPRIETARY Ansys manual**, while VMFL005's value **is the Hagen-Poiseuille exact solution** — a V reference. **The Ansys cases are the lab's cleanest G; they are not a route to P.** **The genuine nearest candidate is 2D and already written: F12** (RAE 2822 / AGARD AR-138 Case 9, prereg frozen 2026-07-30 **before any solver**, overall PASS rule already fixed, **NEVER RUN**) — the shortest path to the lab's first HOLDS that needs no new pre-registration, and its gate could genuinely fail.

### THE ONE MATERIAL ERROR FOUND — and it was on the row the matrix would have rested on

**K0c was tiered HOLDS on a grid triple it does not have.** K0c was designed as **mesh PAIRS** (all 20 gate rows carry exactly `coarse_mesh` and `fine_mesh`), and the quoted *"p 1.94–2.33 on the Richardson ladder"* belongs to **K0b's** 32/64/128 capability ladder, **whose own record says at line 335 that "the de Vahl Davis values do not apply to these cases and are not used"**. The quoted range is not even that table's range (its orders span 1.75–2.98). **G is empty; K0c is GATE REACHED on this alone.** Everything else about K0c holds up (prereg `7c606b74` 15:43:21Z vs first artifact 16:04:01Z — **19 minutes**; bands parsed from the frozen spec at run time; 0-of-20 confirmed from `gate_k0c.json`, largest deviation **1.1388340512100987 %** on a 3 % band). **One rule-2 defect reported, not waved through:** `analyse_k0c.py` was first committed at `32d4ae0d`, **after every solve finished** — the claim must read *"the specification was frozen before compute; the comparator was not"*.

### FOUR RULINGS, all disclosed as overrulable (§2.2)

**Ruling 1 reached its FINAL FORM at a second amendment; both earlier forms are STRUCK IN PLACE.** Each broke on a real row: the original would have tiered dafoam's 24 zero-coverage rows GATE REACHED; the first amendment would have tiered **VMFL005** — the lab's cleanest G, prereg frozen 194 s before compute — as SURVEYED. **The defect in both was counting ABSENCES.** The tier now counts **GREEN** columns: 3 → HOLDS; 1–2 under a frozen prereg → GATE REACHED naming the missing letters; 0 → SURVEYED; a green column's gate FAILing → NOT HELD; no solve → NEVER RUN.

**Ruling 4 — `P` requires validation against MEASURED PHYSICAL REALITY.** Resolved a genuine collision between two of this team's own audits reading the same clause opposite ways on VMFL005. An exact solution, analytic benchmark, manufactured solution, correlation, another code's result or a numerical benchmark scores **V** if it qualifies and scores **P never**. Reading P to cover exact solutions would let one comparison score two columns and make HOLDS reachable without the lab comparing anything to the world. **Severe, and its cost is stated not buried: it empties P across most of the lab — and that IS the finding.**

### RICHARDSON: RULED. ONE INSTRUMENT, ONE CONVENTION

**18 distinct implementations across 22 files. All 18 agree on the observed order and on GCI to the last bit; they split exactly two ways on the extrapolate, and the split is the sign.** On one shared triple with a known analytic answer every implementation returned **p = 1.9999999999999973** and **GCI = 1.2376237623762418 %**; the extrapolate came back **1.0** from thirteen and **1.02** from five — **2 % of the value and 100 % of the correction**, invisible on a printout because 1.02 sits plausibly between the levels. **RULING: the lab standardises on `scripts/roache_triple.py` with N-T8's convention verbatim.** **Adopting one instrument is NOT retiring five and nothing was retired** — the T-family parents are byte-frozen with hash identities other code refuses on, and **retiring a standard is Sanaa's**.

**CHECK 1 DISCHARGED PERSONALLY, NOT DELEGATED.** This supervisor read that instrument's arithmetic **as a diff**: `richardson = f_fine − e21/den` with `e21 = f_med − f_fine` **is** N-T8's form algebraically; the defective form is returned beside it as `richardson_parent_convention`, named wrong, so the frozen T-family records stay reconcilable **without editing them**; **both** ratio paths return EXACT/OSCILLATORY/DIVERGENT/STAGNANT **before any GCI key is created**, so a non-monotone triple physically cannot carry a GCI; a second assertion forces the verdict to be the band verdict or NOT A RESULT — **rule 5's one-way door enforced in code**; it **refuses** on `r <= 1.0`; `dim` is required with no default. Selftest **53/53**, and it imports both parents and cross-checks them **live**, so its provenance is executable rather than a comment.

**"Display-only" is CORRECT at every defective site and FALSE as a lab-wide sentence.** Re-derived, not relayed: no comparison outside a selftest reads an extrapolate at a defective site, and the trace's two un-adjudicated residues both carry the correct form — **no verdict moved and none could have**. But **N-T8's registered sentence has two counterexamples**: `sdk/chief_engineer/uq.py`'s `_asymptotic_guard`, whose boolean sets `conclusive` across **eight call sites and selects the band formula itself**, and the **ansys V-column tiers, which EXCHANGE PLACES under the defect**. Both carry the correct form, so nothing moved. **Referred to heat-transfer as a narrowing — that fact is theirs.**

### ⚠ A WORSE DEFECT, and in this team's judgement more urgent than the sign

**THREE implementations quote a GCI on a DIVERGENT triple.** Planted 1.00 / 1.02 / 1.05 (error **growing** under refinement, increments same-sign so a sign-only guard misses it): the three **K0b** copies and **`4G_runs/.../ladder.py`** return **`GCI_fine_pct = −10.714 %`** — a **NEGATIVE GCI**, `reason = None` — and **`sdk/workflows/tmr_verification.py`** returns an order of **−0.5850** rather than `None`. All three guard **only** on increment sign change, never on `p <= 0`. **A wrong extrapolate is display-only where it lives; a negative GCI printed beside a PASS is a quoted uncertainty on a row rule 5 says is NOT A RESULT.** `tmr_verification.py` is **the flat-plate ladder's own instrument**, so this is not hypothetical for the matrix's strongest G row. **Whether any published number rests on a divergent triple has NOT been traced and it should be. REFERRED TO CFD AND HEAT-TRANSFER.**

### ⚠ FOUR-FILE STALENESS PATTERN, measured (three independently)

Worktree copies stale against HEAD: `docs/LAB_STATE.md` (**303 lines short**), `docs/COST_CALIBRATION.md` (**C-43** vs HEAD's **C-47**), **`docs/NUMERICS_KNOWLEDGE.md` DOES NOT CONTAIN N-T8** (HEAD carries it at line 3849), and the ansys register (**1 row / "0 PASS of 1 run"** vs HEAD's **3 rows / "2 PASS of 3 run"**). **A lane opening NUMERICS_KNOWLEDGE.md to check the Richardson convention WILL NOT FIND IT.** These files are **HEAD-only**. *(The stale shared-index hazard recorded in the block below stands and remains the chief's to clear.)*

### ansys-verification audited — **VMFL005's PASS is SOUND**

Prereg blob **byte-identical** to the frozen sha and frozen **194 s** before the first solver artifact; the comparator blob on disk identical to the sha frozen in the prereg's §10 table, so **the frozen file IS the file that ran**; the gate **discriminates** — **Ansys's own CFX value of 10.49 Pa GATE FAILs it**, as the prereg said in advance it would; planted-zero fired with a negative arm; **dP = 10.2909853852 Pa reproduces from the raw monitor files by subtraction**. Register **2 PASS of 3** recomputed, every PASS artifact verified present, **no non-PASS row carried as a credential, no softening anywhere**. Tier **GATE REACHED — missing V and P**, and the ansys team reached the same tier **independently and unprompted** (N-AV7). **Trap recorded: a literal search for `10.24` in the manual sidecar returns NOTHING** — the PDF text layer renders it `10. 24`, with a space inside the number.

**Next actions:** §7, the Certonomous Verification Manual, **remains SEQUENCED BEHIND this matrix by the chief's deliberate hold — and with ZERO HOLDS rows it currently has NOTHING to draw on; that is the honest state, not a blocker.** Then: the `check_threshold_resolution.py` spec (drafted, this supervisor's to read before any implementation); the divergent-triple trace; exhaustive cfd rows.

**On Sanaa's desk, via the chief:** (1) **FD-vs-adjoint as a fourth `V` instrument** — a rubric widening, **23 dafoam rows move**. (2) The four §2.2 rulings, disclosed as overrulable. (3) Standing: `RESULT_PRIORITY_CHARTER` v0.5; and **the matrix rubric is the chief's reconstruction of her directive, still unruled by her**.

**Blocked:** nothing in this team's territory.

---

**Section updated:** 2026-08-25T00:09:30Z by verification-supervisor (stamp from `date -u` in the committing invocation), at its fourth commit of this session.

### ⚠⚠ URGENT, LAB-WIDE, AND IT IS THE CHIEF'S CALL — THE SHARED GIT INDEX IS STALE AND LOADED AGAIN (D-1's shape, recurring)

**Measured by this supervisor personally, not relayed.** At HEAD `fa201acd` the shared index carried **4 staged DELETIONS and 3 staged modifications**, and **every one of the four "deleted" files EXISTS ON DISK AND EXISTS AT HEAD**: `docs/COVERAGE_MATRIX.md` (**this week's headline deliverable**), `docs/campaigns/T-family/MATRIX_CONTRIBUTION.md`, `docs/campaigns/T-family/T5_CONFIGURATION_RULING.md`, `docs/papers/forced_convection_heat_transfer/PAPER_INTAKE_2026-08-24.md`. **A bare `git commit` by any lane right now deletes all four from HEAD.**

**The mechanism, which matters more than the list.** The index was `read-tree`d from an older HEAD. **Ten commits landed in this session window alone.** Every file a peer lands at HEAD that the stale index does not carry appears as a staged deletion — **so the loaded set GROWS with every peer commit and the file list is stale the moment it is written.** An audit lane reported a DIFFERENT and larger set an hour earlier (the closure GPU record set and closure's own `MATRIX_CONTRIBUTION.md`); **that set was true at its moment and is not the current set.** Do not act on either list — act on the mechanism. **Per rule 10 nothing was reverted and the index was not touched: the index is the chief's call.** The fix is the same one that resolved D-1: `git read-tree HEAD`, chief only, under Sanaa's standing approval.

### Coverage matrix — dafoam and closure AUDITED AND ENTERED

`docs/COVERAGE_MATRIX.md` at **`93d1a02e`** (476 lines). Commits this session: `00367194` front matter, `ddd38a70` §2.2 rulings, `93d1a02e` §3 rows. **All work read-only; 0 core-minutes; no solver or container started.**

**THE HEADLINE — 64 rows audited, ZERO HOLDS, and the G column is empty on every one.** Neither dafoam (58 rows) nor closure (6) has EVER computed a grid convergence index: `GCI` and `Roache` appear in **zero** files under `cases/dafoam/`, `docs/dafoam/` and `cases/RANS_LES_closure_models/`; no observed order `p` anywhere; neither contribution contains `CONVERGING`. **This CONFIRMS the inventory's standing fact for these two families, and confirms it harder than the fact claims** — the absence is not of a *converging* triple but of *any* triple. Two category errors named in advance: every `Richardson` hit in the dafoam tree is FD-step-size extrapolation or a Richardson PRECONDITIONER sweep, not grid Richardson; and dafoam's only three-level family (A3, 21,840/42,120/79,560) **GATE FAILed at its finest level** (reason −3, 1.31× reduction), so under rule 5 it could not be graded even if someone tried.

**dafoam: 0 HOLDS, 0 GATE REACHED.** All 24 rows it tiers HOLDS are **SURVEYED**, each missing all three letters. **ESCALATED TO THE CHIEF, NOT DECIDED:** whether **FD-vs-adjoint** (now a landed family standard, `docs/dafoam/V_STANDARD_FD_VS_ADJOINT.md`, `4a6ea0b8`) is admitted as a **fourth V instrument** — a rubric widening, **23 of 24 rows change tier**. This team's input only: if admitted, SHIPPED rows only, because code verification whose instrument cannot be re-run outside this box is a self-consistency check; **only 6 of 24 survive that test**. Both outward-facing rows fail **P on the PRE-REGISTRATION clause, not the source clause** — **G-16 holds the strongest external artifact in either family** (AGARD AR-138 Case 2308, `cases/dafoam/ladder-a/logs_A3/case_2308.dat`, 22,695 B, **tracked**, title-verified from its own content as Schmitt & Charpin 1979) and **no prereg registers a Cp band against it**; G-33's "published floor" is a lab regeneration, and its own record disclaims the published framing. **G-16 is the one dafoam row worth promoting — on a RE-RUN under a frozen prereg, never on the run that exists.**

**dafoam census defect (§3.2a) — an instrument defect, DEFLATED not inflated.** §4.1's table says 51 rows; the document's own command returns **58**, and §4.2 says the command wins — so **the prose was right all along and the table was the error, wrong in every cell** (HOLDS 24 not 18; PATCHED 35 not 27; SHIPPED 21 not 23; OTHER 2 not 1). **Three defects in the command itself, so nobody re-runs it as printed:** it reads the tier from `$9` while five rows carry literal `|` in their statistic cells (`|CL − 0.5|`, `max|FD_stock − FD_patched|`, `|ΔAoA|`), shifting every later field — **`$(NF-3)` is field-shift-immune**; the ternary tests `/SHIPPED/` before `/PATCHED/` so G-07's *"SHIPPED-equivalent"* string defeats the document's own bucketing rule; and **G-32 is an undisclosed second OTHER row**. §4.3's conclusion survives, its arithmetic does not — the PATCHED-over-SHIPPED imbalance it warns of is **35 to 21**, worse than claimed.

**closure: 0 HOLDS.** Row 3, the frozen-field ceiling, drops **HOLDS → SURVEYED** (missing V and G) and **nothing about it is weak** — byte-identical W2 reproduction, independent re-derivation to worst `3.969e-12`, planted controls registered to refuse `exit 2`, and all four headline ratios reproduce exactly from its artefact. **Closure's prereg hygiene is the best in the lab and was VERIFIED, not trusted:** six preregs, disk sha256 == HEAD blob on every one, commit histories exactly as claimed, FS5's second commit a **legal dated Addendum 1** carrying *"lines whose number changed above this section: 0"*.

**RULING 1 AMENDED, original STRUCK IN PLACE, before any row was entered under it.** The audit returned 24 rows missing ALL THREE letters; the original ruling would have tiered them GATE REACHED alongside rows missing one — flattering, and in the direction of the lab's own interests. **GATE REACHED restored to the chief's wording (exactly one); missing two or three → SURVEYED, naming every missing letter; SURVEYED's gloss sharpened to "ungated ON THE V/G/P AXES"** because such a row may well have passed a frozen lab gate. **A tier says what KIND of evidence a row is, not how well it was done.**

**Owed back to other families as dated corrections, theirs to make, none verdict-moving:** dafoam's §0.6 staleness marker (says `V_STANDARD_FD_VS_ADJOINT.md` is NOT at HEAD; **it is**, `4a6ea0b8`); dafoam's G-16 citation path (`RESULTS.md:44` points at `cases/dafoam/logs_A3/`, **a directory that does not exist** — the file is one level up); closure's *"all eleven cases where it converged"* (the headline CBFS13700 ceiling case ran to a designed fixed `endTime` 30,000 with `converged_by_residual_control = False`; clean continuity `2.6e-13`, **not a falsification**, but the phrase mis-reads).

**Lanes live: 2 of 3.** (thermal + K0c + both standing facts + cfd rows) and (Richardson-sign instrument unification + VMFL005 audit + `check_threshold_resolution.py` spec). Lane 1 returned and is landed.

**Next actions:** land thermal, cfd and ansys rows; rule on K0c's tier under Ruling 3; make the one-instrument-one-convention call on Richardson; then the calibration row and — only then — §7, which stays **SEQUENCED BEHIND** the matrix.

**On Sanaa's desk (new, via the chief):** the **FD-vs-adjoint-as-fourth-V-instrument** question, because it is a rubric widening and moves 23 rows. Standing: the `RESULT_PRIORITY_CHARTER` orderings (v0.5 draft), and the fact that **the matrix rubric is the chief's reconstruction of her directive, unruled by her**.

**Blocked:** nothing in this team's territory. **The stale shared index blocks nobody but endangers everybody, and it is the chief's to clear.**

---

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

**Section last written:** 2026-08-25T00:11:19Z by `ansys-verification-supervisor` personally
(stamp from `date -u` in the writing invocation; staged via `scripts/lab_state_section.py`
+ `hash-object -w` + `update-index --cacheinfo`, never the shared worktree copy).

**Last commits (this session):** `ea10aa07` COVERAGE_ROWS.md (the team's three rows, a
FEED to verification, not their file); `c774cecd` CASE_MAP.md GAP-CLOSING PRIORITY table;
`a89da095` RECORDS_DRAFTS.md. Prior: `c6994175` VMFL005 VERDICT PASS, `90ee8d80` artifacts,
`2d54a629` prereg frozen.

**D-6 RULED AND EXECUTED — the chief may stop asking.** Canonical archive home is
`/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/{FLUENT,CFX,FORTE}_ARCHIVES/`, 123 files
sha256-verified against `docs/ansys_verification/VM2026R1_SHA256_MANIFEST.txt`. The dead
partial copy under `docs/papers/verification_validation/` was deleted 2026-08-24T17:39:17Z
AFTER re-verifying the survivor (manifest 123 OK, exit 0). Commits `e9737c5f` / `17527f40`;
write-up `docs/ansys_verification/ARCHIVE_HOME_RULING.md`. **CASE_MAP LANDED** (`546a036b`):
95 cases, 54 2D / 22 axi / 19 3D, 26 analytical / 50 experimental / 19 benchmark, 11 with no
solver here. Both first-action items are CLOSED.

**Register: 3 rows at HEAD, credential count 2 PASS of 3 run.** #1 VMFL001 run 1
`NOT A RESULT` (1.9833 core-min, $0.0017 derived, C-37); #2 VMFL001-R2 `PASS` (3.2833
core-min, $0.002807, C-45); #3 VMFL005 `PASS` (4.0000 core-min, $0.003420, C-47).

**THE TEAM'S SHARPEST FINDING, and the one worth carrying lab-wide — `N-AV7`.** Two cases,
both `PASS`, both `CONVERGING`, both p ~ 2, and Richardson extrapolation behaves in
**opposite** directions. VMFL001-R2 lands on White's closed form to **3.7 ppm** without
ever seeing the formula (`N-AV6`). VMFL005 converges cleanly at second order to
**10.295119 Pa, not to the exact 10.24 Pa** — its deviation from exact is **0.4979 %**
against **GCI_fine 0.0502 %**, a ratio of **9.92**, and the extrapolate sits **0.5383 %**
from exact, FURTHER OUT than the finest grid. Roughly 90 % of the residual is not
discretisation error. **A small GCI is a statement about grid convergence only; it does not
license the claim that the remaining deviation from a reference is numerical.** Any team
scoring a V column off a small GCI would have scored VMFL005 HOLDS and been wrong. Verified
by this supervisor personally from the HEAD blob of `cases/ansys_verification/VMFL005/RESULTS.md`
§5.2, not relayed.

**Coverage rows fed to verification** (`docs/ansys_verification/COVERAGE_ROWS.md`, `ea10aa07`):
VMFL001 run 1 **NOT HELD**; **VMFL001-R2 HOLDS** (V exact — White §3-2.3; G CONVERGING
p = 2.0102, GCI 0.0563 %; P frozen prereg on disk) — a candidate for the lab's first HOLDS
with a non-empty G column; **VMFL005 GATE REACHED**, not HOLDS, the tier set by this
supervisor's ruling on the 9.92 ratio. VMFL005's own triple: `CONVERGING`, r = 2.0 exactly,
p = 1.9340642225610707, GCI_fine 5.021172780104668e-04, planted-zero fired — it earns **G**
outright; the tier is held down solely by the exact-solution limb, so **no grid spend is
recommended**. Verification has not yet ingested these rows.

**IN FLIGHT — VMFL051, the team's first compressible/supersonic case** (manual pp. 165-166),
chosen to close the lab's biggest declared gap. Isentropic Prandtl-Meyer expansion over a
convex corner: inlet M = 2.5, 15 deg turn, **exact closed-form target M = 3.2370** (Anderson).
Picked over the oblique-shock cases deliberately — cfd's F3 suite already covers wedge/cone/
diamond COMPRESSIONS, and an expansion fan is both the complement and, being smooth and
shock-free, a case where an observed order means something instead of being smeared to first
order by shock capturing. Lane is deriving the reference itself to full double precision
rather than leaning on the manual's four printed decimals, and derives gamma from the manual's
own Cp and molecular weight. **ZERO COMPUTE until this supervisor verifies the prereg commit**
(SUPERVISION §3 check 4). Cap 30 core-min. Toolchain present: `rhoCentralFoam`, `sonicFoam`,
`rhoSimpleFoam`, `rhoPimpleFoam` in v2606. **Manual defect found and to be recorded:** VMFL051's
"Analysis Assumptions" calls the flow **incompressible** while its own Physics/Models line says
"Compressible, inviscid" and the case is a M 2.5 -> 3.24 expansion.

**Next case after VMFL051: VMFL045** (oblique shock over an inclined ramp, p. 153) — accepted
on the lane's recommendation: closes two declared gaps at once, exact analytical target, same
solver and class so the tooling transfers, trivial cost. NOT started; VMFL051 clears its freeze
first.

**TWO RECORD DEFECTS OF THIS TEAM'S OWN, found this session and under repair:**
1. **`N-AV7` and `N-AV8` are forward-cited from a credentials file and DO NOT EXIST.**
   `docs/NUMERICS_KNOWLEDGE.md` carries N-AV1..N-AV6 and stops. Both ids are cited in
   `VMFL005/RESULTS.md` and inside **register row #3**, which is append-only. This is exactly
   L-292 ("an id in prose before its append is a prediction, not an identifier") committed by
   this team on a credential row. Repair lane live; landing both plus a new wedge-bias entry.
2. **Docket-id collision:** register row #3 cites `D510` for VMFL005's open mechanism; `D510`
   at HEAD is **closure's R3 SpaRTA ratification** (`docs/DOCKET.md:875`). Repair is a fresh id
   for the question plus a dated correction note at the FOOT of the register striking the wrong
   citation — the row itself is never edited.

**Open mechanism, honestly unresolved:** VMFL005's ~90 % non-discretisation deviation. Leading
candidate is the planar-wedge area deficit — an OpenFOAM wedge sector is a flat-sided triangle,
so at 5 deg the modelled area is short by sin(t)/t = 0.9987312439537492, i.e. **0.1268756 %**,
worth **+0.2542 %** of dP under a fixed-Q R^-4 reading (**51.06 %** of the 0.4979 %) or
**+0.1270 %** under fixed-V_avg R^-2 (**25.5 %**). A quarter to a half, reported as a quarter to
a half — **NOT claimed as the resolution.** It is a modelling bias that axial and radial
refinement cannot remove, because the error lives in the azimuthal direction the wedge holds at
one cell; every future axisymmetric case here carries it in its error budget.

**Live jobs:** **no solver compute owned by this team; zero core-minutes spent this session.**
Lanes: VMFL051 pre-registration (opus, no compute); records repair (opus 4.8).

**Rungs lacking verdicts:** none. Every case run is graded and in the register.

**Corrections to this section's previous text:** L-300 and L-301 were carried as "drafted and
not landed" — **both are at HEAD** and need no re-drafting. A future lane must not be dispatched
to re-land them.

**On Sanaa's desk (new, via the chief):** the **P-column definition question** — whether a case
whose ONLY reference is the manual's own printed number can score the P column, given the manual
is proprietary vendor documentation rather than open literature. VMFL001 and VMFL005 are firm
(White and Hagen-Poiseuille, public textbook, re-derived independently here), but the distinction
governs most of the remaining 92 cases and it defines what a credential IS lab-wide, so it is not
this team's to settle. **SUBMISSIONS PARKED** — nothing from this team's VM2026R1 work is filed,
sent or registered outside this box, and the manual is proprietary Ansys documentation.

**For the chief to route, not this team's files to fix:** the shared-ledger truncation has reached
a credentials file — `ANSYS_VALIDATION_REGISTER.md` worktree **3,305 B vs 13,899 B at HEAD**,
showing **1 row where HEAD has 3**; `COST_CALIBRATION.md` 143,555 vs 163,546; `LAB_STATE.md`
109,257 vs 126,208. A lane reading the worktree copy reports this team has run one case, and one
of mine did exactly that today. Inspected, never reverted (rule 10). The shared index also holds
staged **deletions** of this team's own `cases/ansys_verification/` files.

**Blocked:** none.
