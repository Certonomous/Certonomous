# The docket — findings that are real but are not this rung's

Created 2026-08-11 by the chief supervisor, as the queue **R-CONVERGE** requires.

A rung that absorbs every new finding never closes. A rung that DROPS them is worse.
This file is the third option: a finding made outside a rung's declared scope is written
down here, with the rung it surfaced in and what would settle it, and the rung closes.

**This is a queue, not an archive.** An item leaves it by being executed or by Katie
ruling it out — never by ageing.

Rules that govern entries here:

- Every item names **where it was found**, **what it would take to settle**, and **who
  owns it** (fleet / chief / Katie).
- Items filed under **R-DEPTH** (depth-3 meta-work) stay filed unless a depth-2 finding
  falsified something published. They are marked `[R-DEPTH — filed, not executed]`.
- Items filed under **R-VALUE** are the residuals of a rung that closed as PASS WITH
  RESIDUALS. They are marked with the rung.
- No item here is a claim about the world. Where an item asserts something, it carries
  its evidence or it says it has none yet.

---

## A. Katie's — decisions the fleet cannot make

| # | Item | Where found | What settles it |
|---|------|-------------|-----------------|
| A1 | **8 transcript hits before filming.** Three acts narrate the cache, one names the solver binary, four carry internal doc paths. | Transcript sweep, 2026-08-11 | Katie's call on each: cut, reword, or accept on camera. |
| A2 | **40 core-min hump authorisation** — M1 offline + M2 negative control. Drawn from a 365 core-min list I recommend against buying as a block. | C1 lever audit | Katie authorises compute, or does not. Nothing runs meanwhile. |
| A3 | **`LAPTOP_SHOOT.md` still carries the withdrawn board claim.** It is Katie's file; the fleet does not edit it. | V15 round 5 reconciliation | Katie edits, or rules the claim stands. |
| A4 | **The auto-stop causal question.** A real code defect plus a real symptom is not a cause. Katie/Sanaa own the box's power control. | `auto-stop-ignores-control-room` | The fleet exhibits wiring, or the claim stays a candidate. |

## B. Machinery — each defect class becomes an executable check

A lesson without a check is a lesson that will recur. Owner: fleet.

> **CLAIM AN ITEM BEFORE YOU DISPATCH IT — write your session into the Status column first.**
> Added 2026-08-11 after two chief sessions independently dispatched the *same four briefs*
> off the same directive block. The B1 collision is the proof: two agents ran the identical
> sweep brief, and one's `Write` landed on the other's already-committed
> `docs/SWEEP_REFRAME_AUDIT.md`, replacing a 335-line document with a 281-line one and
> dropping two sections. It survived only because that agent went looking, compared both,
> judged the other strictly more complete, and restored it with `git checkout --`.
>
> **That is L-77 with commits instead of a scratchpad, and the failure is the dispatcher's,
> not the agent's.** This file is the one surface both sessions already read. One edit before
> dispatch makes the collision visible while it is still cheap — the agents do not exist yet.

| # | Item | Lesson | Status / owning session |
|---|------|--------|--------|
| B1 | **Sanctioned `sweep()` helper** — names its frame, filter and commit in its own output; cannot silently exclude; test asserts it sees a planted file inside an ignored path. Plus: re-run every standing sweep whose conclusion mattered; mark any that cannot be re-derived as **UNFRAMED**. | L-75 | **LANDED** — `85cc1078` + `fc8e1812` (helper, 4 named frames, 3 verdicts, `FrameMismatch` on cross-frame comparison; 24 tests). Part (c) at `8ebe2b8e`/`8623b8ca`: **16 published sweeps re-run, 4 moved, 3 UNFRAMED.** *Ran twice — see the claim rule above.* |
| B2 | **Fail-false gates.** Every gate and parser answers "did the check run?" before "what did it find?", with a third verdict for unknown. Sweep all gates. | The V16 skip-is-not-agreement defect | `be42e5d4` landed; **re-running its CLEARED sites** under the cache guard — injection is a mutation plus a re-import, so a stale cache silently skips the injection and the site reads as safe (see D1a). Reporting three groups, not two. |
| B3 | **Absolutes.** No absolute claim ("never", "always", "cannot") ships in a docstring, comment, report or camera surface without an executed test named beside it. Surface list derived mechanically, never enumerated. | L-76 | **MEASURED, AND NOT USABLE AS A GATE YET — see B3a/B3b.** The FP rate was published as required, and it is the reason this row does not close. |
| B3a | **74%.** A checker was built (`scripts/check_absolutes.py`, `8a8b5392`) and its author measured its own false-positive rate against a 75-record hand-labelled sample: **37 of 50 flagged records were legitimate**, false-negative rate 8%. Not a usable gate — and publishing the number rather than a clean-looking output is the deliverable working as designed. Sweep as it stands: **7,040 unbacked absolutes across 685 files**, from 18,145 absolutes in 44,206 prose units, 1,077 of 1,078 in-frame files read (1 binary skipped, 0 unreadable). Frame: `git ls-files` filtered to `.py .md .html .tex .sh .js .txt`, 4 MB cap. The seven false-positive classes are labelled per-record in the committed fixture: past-tense reports with evidence cited, counterfactual premises, bounded quantifiers enumerated a few words past the gate's window, table rows and headings, stated blind spots, claims inside a `test_*` docstring where the enclosing test **is** the check, and third-party text. | B3, 2026-08-11 | Round-2 gates are drafted and were **deliberately not shipped unmeasured**. Each must be checked against a positive-control set of the six real specimens pulled from git history (`c05a03e0`, `db096bb7`, `fd855017`, `V15_ROUND5_NUMBER_RECONCILIATION.md:96/168`) before it is trusted — otherwise gating tunes to a pretty number. | fleet |
| B3b | **The keyword premise has a measured floor, and it is this rule's problem rather than the checker's.** **Two of the six real specimens carry no keyword from B3's list at all** — *"stops being able to go stale"* and *"the three `BaseException`s propagate exactly as documented"* contain no never/always/cannot/every/all/none. So **any keyword-family checker has a ~33% structural miss on the known specimen set**, before tuning. Related: `must` must NOT be treated as normative and exempted — a deontic modal on an *inanimate* subject (*"one surface must never be able to end the audit"*, repaired at `fd855017`) is a claim wearing a modal; exempt only on an imperative opening, an agentive subject, or a rules surface. | B3, 2026-08-11 | Either the rule widens past a word list, or the audit document **states the ~33% miss as a declared blind spot**. A checker that silently misses a third of its own founding examples while reporting 7,040 hits is the fail-open shape in a new costume. | fleet |
| B3c | **A committed checker cites tests that do not exist.** `scripts/check_absolutes.py` shipped at `8a8b5392` without `sdk/tests/test_absolute_claims.py`, and its own docstring names those tests. **By the checker's own rule that is `CITES_MISSING_CHECK`** — its author's stated reason being that a name resolving to nothing reads as backing to every human who sees it. The instrument fails itself on its first surface. | B3 stand-down, 2026-08-11 | Write the tests or strike the citations. Do not leave it citing air. | fleet |
| B4 | **Quoted generated numbers.** A generated figure quoted into prose carries its commit and the moment it was taken, or it is regenerated at read time. Prefer regeneration; forbid bare copies. | L-79 | Open |
| B5 | **Frames.** Every count carries frame + filter + commit. A number whose frame nobody can state is worse than no number. | L-75 | Open |
| B6 | **Shipped-helper blindness.** A check written with the same helpers as the thing it checks proves only transcription fidelity. Any load-bearing verification names its EXTERNAL referent, or declares it has none. | L-74 | Open |
| B7 | **Lever activity.** Configured is not active. Log-verified or it is not evidence. | L-40 class | **CLAIMED 2026-08-11 by session `64b13819`** (Katie's §4 item 4, the C1 dead-lever audit incl. every hump-adjoint conclusion). L-40 is the lab's most-cited lesson — **104 citations** across the corpus, measured, well clear of the next at 58 — so this is the discipline the most conclusions lean on and the least mechanised. The naval line already produced one instance at capability scale: **zero tracked files reference any wave machinery**, against 1,825 mentioning `alpha.water` by the identical pipeline. Configured, shipped, linked into three solvers — and never once run. |

## C. Memory as an audited system

| # | Item | Owner |
|---|------|-------|
| C1 | **Cold-start test, monthly.** A fresh agent with no context reaches correct current state from the durable files alone. Everything it gets wrong is a memory defect fixed **in the files**, never by explaining. **First run IN FLIGHT 2026-08-11** — dispatched with exactly the one instruction §6.3 specifies. | fleet |
| C2 | ~~`docs/MEMORY_ARCHITECTURE.md`~~ — **ALREADY EXISTS**, v1.0 dated 2026-08-10, and it carries all four required parts plus the test spec in its §6. *I filed this as open without opening the docs directory; the check took one `ls`. Left visible rather than deleted, because a docket whose first entry was a thing already done is exactly the defect the docket exists to catch.* | — |
| C2a | **The §6.4 answer key is itself a set of quoted generated numbers** (B4's defect class): it fixes the lesson corpus at L-53 when `LESSONS.md` now runs to L-79, and the fleet-death count at eight. Scoring a fresh agent against a stale key marks correct answers wrong. The key needs regeneration-at-read-time or a stamp on every row. | chief |
| C3 | **One home per fact.** Cross-reference; never copy. Copies drift (L-79). Supersession in place, dated — never a silent edit. | standing |

## D. Rung residuals

Filled as rungs close under R-VALUE. A rung closing here does not mean these are small;
it means they are not what that rung declared it would settle.

| # | Item | Where found | What settles it | Owner |
|---|------|-------------|-----------------|-------|
| D1 | **A mutation test can report the exact opposite of the truth, via stale bytecode.** Verifying V16's E3 recompute, an equal-length source mutation (`(5, 5,` → `(4, 5,`) plus a restore left a stale `scripts/__pycache__/self_audit.cpython-312.pyc`: Python's source-based invalidation compares `(mtime, size)`, and `cp` back gave the same size. For three consecutive runs `sa._PLACE_REACH_B` was `(4, 5)` at run time while the file on disk read `(5, 5)`. The clean control **failed** and the mutated case **passed** — a perfectly inverted mutation matrix, which a less suspicious reading would have written up as "the recompute is dead". Re-run with the cache cleared before every step, the matrix is correct in all four cells. | V16 grade-four close-out, 2026-08-11 | A mutation-test harness that **clears `__pycache__` between every cell** — **NOT `PYTHONDONTWRITEBYTECODE=1`, see the correction below** — and that asserts the clean control and the mutated case in the *same* run so an inversion cannot look like a pass. Until it exists, every mutation result in this lab is only as good as whether its author happened to clear the cache. |
| **D1a** | **[CORRECTION 2026-08-11, chief — the fix D1 first recommended DOES NOT WORK, and I propagated it to three agents before testing it.]** `PYTHONDONTWRITEBYTECODE=1` stops Python **writing** a `.pyc`; it does nothing about **reading** a stale one that already exists — and one always exists, because the module was imported before the mutation. Reproduced minimally: with a stale pyc present and an equal-length mutation, the mutated cell returns the **clean** value while the file on disk holds the mutation. **A wrong fix is worse than no fix: it converts an unverified result into a falsely verified one.** Executed mitigation table — deleting `__pycache__` before every cell: **WORKS**; `PYTHONPYCACHEPREFIX` to a fresh dir per cell: **WORKS**; a mutation that changes byte length: works, but that is a property of the edit, not a guard; `sleep` **between the prime and the write**: works; `sleep` between the write and the run: **FAILS**, the mtime was already stamped; `PYTHONDONTWRITEBYTECODE=1`: **FAILS**. **Mechanism:** Python's timestamp invalidation compares `int(st_mtime)` — *whole seconds* — plus size, so a prime-mutate-run-restore-run cycle completing inside one second with a length-preserving edit matches both halves of the key. This is why the defect surfaces for scripted agents and essentially never for someone editing by hand. | Chief, on D1, 2026-08-11 | Nothing further — executed. The harness in D1 must be built against cache **clearing**; a harness built on the flag would certify the same false passes. | fleet | fleet |
| D2 | **Two published surfaces carry an underived count: "four" digit-form linear-algebra ranks.** `campaign/V16_GRADE.md` says *"swept over every tracked UTF-8 surface … four genuine linear-algebra ranks written as digits"*; `docs/PRODUCT_LIST.md:3765` repeats *"It is not — four are digits"*. Re-run mechanically (`git ls-files` piped to `/usr/bin/grep`, **not** this shell's `grep`, which is `ugrep --ignore-files`) the number is not four — it moves with whether the guard's own source, its tests, and the audit records that quote them are inside the filter. Neither surface states a filter or a commit, so neither can be reproduced. The count is not load-bearing — the exclusion was rewritten on the *shape* of the two senses, not on how many instances exist — which is why V16 dropped the figure from `self_audit.py` rather than restating it. The two published copies still carry it. | V16 grade-four close-out, 2026-08-11 | Either re-derive both figures with frame + filter + commit (B5/L-75/L-72), or replace them with the named paths, which do not drift. | fleet |
| D3 | **`docs/INSTRUMENT_INTEGRITY_LEDGER.md` holds the guard's two standing faults, and one of them is structurally unclearable.** Every run of `check_board_placement_words` reports WARN with exactly these two: a rule-A `rank-3` bound to Wu (a *quotation* of defect A, which the adjudication clause does not clear because the correcting sentence is too far away) and a rule-B `"Our margin over the runner-up"` (a quotation of defect C — and **rule B has no adjudication clause and cannot be given one**, since there is no correct form of a position word to sit beside a wrong one). This is the check's permanent non-green floor: no future round can reach PASS while these stand, so a reader cannot tell this WARN from a new one. | V16 rounds 1–4; measured again at close-out, 2026-08-11 | Assemble the ledger's two quotations from split tokens the way `sdk/tests/test_rank_claim_surfaces.py` and `V16_AUTHOR_HELDOUT_SET.py` already assemble theirs — the convention exists and this surface predates it — **or** record an explicit dated accepted-exception so the WARN is legible as "the two known quotations, nothing new". | fleet |
| D4 | **The fixture-assembly convention is enforced by review alone, and review failed twice in one night.** `test_rank_claim_surfaces.py` states in its own header that a tracked file must not spell a wrong placement in full. The killed agent's inherited diff broke it, and so did my first draft of the repair: between us we put **eight** new real rule-A faults about a live entrant into the guard's own test file (measured: WARN 2 → WARN 10, all eight new ones in that one file). The live guard *did* catch it — but only because I ran the audit by hand mid-round. | V16 grade-four close-out, 2026-08-11 | `check_board_placement_words` (or a thin wrapper) run as part of `sdk/tests/`, so adding a literal fault to a tracked file reddens the suite rather than waiting for someone to run the audit. **[R-DEPTH — borderline: this is the guard checking the guard's own test file. Filed, not executed.]** | fleet |
| D5 | **`sdk/workflows/adjoint_optimization.py` swallows the same certificate `unlink` B2 fixed in ten places, but publishes no withdrawal claim** — so by B2's own test (does the swallow reach a *published* verdict?) it is out of that rung, and it was left alone rather than swept in. The stale-page risk is nonetheless real: if the unlink fails and the build then fails, an earlier mission's certificate stays on disk and the act says nothing about it either way. | B2 fail-open sweep, 2026-08-11 | Either route it through `workflows.withdraw_certificate` like its nine siblings, or record the deliberate decision that an act which makes no claim needs none. One line of code; the reason it is filed rather than done is R-CONVERGE, not difficulty. | fleet |
| D6 | **Five acts take the OPPOSITE failure on the same line, and it contradicts a rule those same files state.** `cylinder_vortex_shedding.py`, `diamond_airfoil.py`, `hypersonic_cylinder.py`, `supersonic_cone.py` and `supersonic_wedge.py` withdraw the previous certificate with a bare `if cert_path.exists(): cert_path.unlink()` **outside** the try that wraps certificate building. A `PermissionError` there raises straight out of `main()` — taking down a mission whose result was already computed, in files that state "a certificate must never take down a good mission". Not fail-open, so not B2's defect class; it is the same line failing the other way. These five also still carry the unconditional withdrawal sentence, and they are **the same five** — the set that takes the bare `unlink` is exactly the set that still states the claim. (Frame: `git ls-files 'sdk/workflows/*.py'`, matched on the two source substrings, at `36c533f3`.) | B2 fail-open sweep, 2026-08-11 | Route them through `workflows.withdraw_certificate` too — it returns rather than raising and states which of three outcomes happened, which fixes both directions at once. Then assert in `sdk/tests/` that no act in the package calls `unlink` on a certificate outside that helper. | fleet |
| D7 | **An absolute with no executed test beside it, and this rung produced the counterexample.** **Two** acts — `sdk/workflows/aircraft_optimization.py:2671` and `sdk/workflows/geometry_study.py:2914` — carry the comment *"the previous run's page is withdrawn FIRST and the new page lands by atomic replacement, so a page from an earlier mission **can never** be served after this one completes"*. (Frame: `git ls-files '*.py'` piped to `/usr/bin/grep -ln "from an earlier mission"`, at `36c533f3`, excluding this rung's own test file which quotes the phrase to describe it. My first draft of this entry said **six**, from reading rather than counting, and the count was wrong — recorded here because an underived number in a docket entry about underived numbers is worth leaving visible.) B2's injection exhibits exactly that: refuse the unlink, fail the build, and the earlier mission's page is still there. The code is now fixed to *say so*, but the comment still states the absolute. This is B3's class (no absolute ships without an executed test named beside it), found in B2. | B2 fail-open sweep, 2026-08-11 | Reword to what the code can support — the page is withdrawn *unless the withdrawal is reported as failed* — or name `sdk/tests/test_certificate_withdrawal.py::TheActPublishesWhatHappenedTests` beside it, which is the executed test that bounds the claim. Mechanical sweep, not an enumerated list: B3 owns the derivation. | fleet |
| D8 | **B2's seven CANDIDATES — flagged, plausible, and NOT made to fire.** Each is a swallowing `except` inside a function that publishes something, where the swallow cannot move the status; none was shown to produce a wrong published verdict, so none is a defect and none was fixed. (1) `chief_engineer/head_engineer.py:1084`, an all-failing `line_hook` empties a published live chart with no marker — the step verdict comes from the process exit status, which is why it is only a candidate. (2) `workflows/aircraft_optimization.py:2034`, a malformed finalist result silently leaves a published table with no expected-count beside it. (3–5) `workflows/ahmed_body.py:697`, `geometry_study.py:2262`, `nasa_hump.py:833` — the painted-field copy is swallowed and `announce_field` then publishes `/api/field/<act>/<name>` while the file stayed in the case directory, a URL the acts' own comments say cannot resolve. (6) `workflows/backstep_case.py:925`, an all-unparsed pressure profile publishes as `[]`, indistinguishable from a file of comments; weak, a `len(parts) < 4` guard absorbs realistic truncation. (7) `workflows/tmr_verification.py:438`, `parse_yplus_dat` keeps the last **parseable** row — reproduced: a garbled final row returns the 200-iteration row, published downstream as `max y+`, "the converged state" per its own docstring, with nothing saying a row was dropped. | B2 fail-open sweep, 2026-08-11 | 1–5 need a live solve or a live hook to inject into, which B2 may not launch; 7 needs an owner's ruling on whether the last *complete* row is the right answer, which is a semantics call and not a bug an agent may assert. Full reasoning and injections in `docs/FAIL_OPEN_GATE_AUDIT.md` section 4. | fleet |
| D8b | *[ID CORRECTED 2026-08-11 by the chief. This row was filed as a second **D8** by a concurrent session while B2's candidates already held that number — two writers, one ID, neither aware. Renumbered rather than merged, and the collision is recorded rather than tidied away: it is the L-43/L-63 duplicate-number shape one level up, in the very file built to stop findings being lost. **D9 below refutes this row**, and cites it as "the D8 row above" — read that as D8b.]* **A published plateau-balance triple does not reconcile with the field it describes, by 1.684x.** `dafoam/ladder-b/S1_CBFS_INVERSION_RESULT.md` §4(2) reports the corrupted run's stationary point as `\|g_penalty\|/\|g_QoI\| = 0.998` with `cos(g_QoI, −g_penalty) = 0.9995`, and its own trajectory table gives `‖g‖₂ = 9.011e-06` at eval 16 — which the driver writes as `np.linalg.norm(g)` of the **total** gradient (`S1-cbfs-inversion/invert_lbfgsb.py:117`, read). Those three over-determine `\|g_penalty\|` and imply **2.841e-04**. Computed exactly from the archived field, `\|g_penalty\| = 2·λ_L2·‖β−1‖₂ = 2·1e-4·2.392652 =` **4.785304e-04**. Solving back, `‖g‖₂ = 9.011e-06` at ratio 0.998 needs `cos = 0.999826`, which does not round to 0.9995. **The finding is unaffected** — the plateau *is* a penalty/likelihood cancellation, confirmed independently by the 53x cancellation itself and by rms\|β−1\| = 0.016511 reproducing the published 0.0165 exactly. What is in doubt is the published cosine, and it matters because `s1-regularization-chosen-by-prior-theory-with-a-posterior-on-beta` named that balance as the control a posterior must reproduce. (Frame: `S1-cbfs-inversion/fields_beta.npy`, 21,000 cells, λ_L2 = 1e-4 read from that run's own driver line 25; host-side arithmetic, zero solver compute; repo commit `7d9e4c51`.) | S1-with-priors pre-registration, 2026-08-11 | Either re-derive the cosine and the ratio with their frame stated, or replace both with the exact analytic `\|g_penalty\|`, which is reproducible from a file on disk. The dependent gate has **already been re-based** onto the analytic quantity (`S1_PRIORS_PREREGISTRATION.md` §4 G-P4, §8), so nothing is blocked on this — it is the published sentence that still carries the unreconciled pair. Belongs to that document's owner, per C3. | fleet |
| D9 | **The plateau-balance triple reconciles exactly, to three published figures; the D8 row above mixes two evaluations.** The second D8 row reports the corrupted S1 run's published `\|g_penalty\|/\|g_QoI\| = 0.998` and `cos(g_QoI, −g_penalty) = 0.9995` as unreconcilable with the archived field by **1.684x**, and `S1_PRIORS_PREREGISTRATION.md` §8 re-bases that document's control gate G-P4 onto `\|g_penalty\|` alone on the strength of it. **Executed check: all three published numbers reproduce from disk.** That run archived a *matched* (β, ∇) pair at the plateau — `beta_eval010.npy` with `grad_eval010.npy`, both DV order, written by the same `run_eval` call (`invert_lbfgsb.py:56,64`) — and evals 11–17 agree in J to seven digits, so eval 10 **is** the plateau. Composing the driver's own convention `g_total = λ_QoI·g_raw + 2·λ_L2·(β−1)` (line 114) gives ratio **0.998441**, cos **0.999542**, rms\|β−1\| **0.016502** against the published 0.998 / 0.9995 / 0.0165 — three for three. The identity `‖g_total‖ = \|g_QoI\|·√(1+r²−2rc)` closes to **six digits** (1.450369e-05 measured directly and via the identity), so the triple is internally self-consistent. **The 1.684 factor is produced by combining the plateau-state ratio and cosine with `‖g‖₂ = 9.011e-06`, which the trajectory table reports at eval 16 — a different state.** Near-cancellation is what makes the mix bite: `‖g_total‖` moves 1.45e-05 → 9.01e-06 (1.6x) between eval 10 and eval 16 while r and c move only in the fourth decimal. No gradient was ever needed to be re-derived — one was on disk. (Frame: two `.npy` files under `/home/ubuntu/certonomous-runs/S1-cbfs-inversion/cbfs_inv/`, **outside the repo, invisible to any repo-scoped grep**; 21,000 cells, DV order both, λ_QoI/λ_L2 from that run's pre-registration §2; host-side arithmetic, zero solver compute.) | `S1_WITH_PRIORS_PREREGISTRATION.md` §3 and its dated reconciliation section, 2026-08-11 | The plateau-balance D8 row and `S1_PRIORS_PREREGISTRATION.md` §8 want withdrawing by their author, and G-P4 restoring to the ratio-and-cosine form. `\|g_penalty\| = 2·λ_L2·‖β−1‖` alone is an **identity** that any treatment knowing λ_L2 and β reproduces exactly, so re-basing onto it removes the only part of the control that tests the *balance* — the cosine is the part that carries information about whether the prior pull actually opposed the likelihood gradient. Not edited in place: the entry belongs to its author, per C3. **[CHIEF, 2026-08-11 — the author session has since ended, so "belongs to its author" no longer assigns this to anyone. C3's supersession-by-the-author rule has no owner to name here, and an unowned withdrawal is how a refuted claim stays published. Reassigned: whoever next picks up the S1 line withdraws D8b and `S1_PRIORS_PREREGISTRATION.md` §8, and restores G-P4 to the ratio-and-cosine form. Until that happens, a refuted correction and its dependent gate re-basing are both live in the record — which is the state this docket exists to prevent.]** | fleet — **unowned, see the chief's note** |

### D-follow-on — the two published results D1 puts in doubt

Filed by the chief, 2026-08-11, on the back of D1. **D1 says the instrument can lie. This
entry asks whether it already did, in something we published.**

A sweep of every commit in this tree since 00:00 today for mutation-proved claims returns
three hits, one spurious:

| Commit | Time | Claim | Why it carries D1's signature |
|---|---|---|---|
| `717d7e7a` | 06:19 | *"mutating `_PLACE_REACH` from 24 to 99 moves…"* | `24` → `99` is an **equal-length** edit — the size half of `(mtime, size)` is preserved by construction. |
| `6b37866a` | 07:14 | *"the recompute moves when I mutate my own sentences"* (V16 fourth grade) | Its own body states the file was **"restored byte-for-byte"**, which reproduces both halves of the invalidation key. |
| `d4509368` | 01:36 | *"the solves did not mutate their own inputs"* | **Not a mutation test** — a different sense of the word. Discarded, and recorded so the next sweep does not re-flag it. |

**Both live ones are POSITIVE results, and that is the dangerous polarity.** Each concluded
that a recompute is alive. Under the inversion D1 demonstrated, the module can hold the
mutated value at run time while the file on disk reads the original — so a test that appeared
to redden on mutation may have been reading stale mutated bytecode throughout, and the
recompute it certified as live may not be. That is a **false pass in a published claim**, not
merely an unverified one.

**What settles it:** re-run those two with `__pycache__` **cleared between every cell**
(NOT `PYTHONDONTWRITEBYTECODE=1` — see D1a; the flag does not stop a stale pyc being read),
asserting all cells **in the same run** so an inversion cannot present as a pass. Routed to
the V16 agent with an explicit instruction not to re-open the rung for it.

**SETTLED 2026-08-11, V16 close-out — both hold, neither was a false pass.** Re-run in a
detached worktree at each claim's own commit, with `__pycache__` deleted before every cell,
each cell a fresh subprocess, and every cell reporting the value seen AT RUNTIME beside the
value ON DISK so an inversion would be visible rather than inferred. Both mutations were kept
**equal-length**, so both sat squarely in the vulnerable class rather than dodging it.

`717d7e7a`, `_PLACE_REACH` 24 → 99 (equal length), harness at `scripts/self_audit.py`:

| cell | expect | runtime | disk | verdict |
|---|---|---|---|---|
| A clean | 24 | 24 | 24 | OK |
| B mutated 24→99 | 99 | 99 | 99 | OK |
| C restored byte-for-byte | 24 | 24 | 24 | OK |

The generated verdict line carried `24 of 45` in A and C and `99 of 45` in B. Claim holds.

`6b37866a`, one sentence in `V16_AUTHOR_HELDOUT_SET.py` mutated `Wu and Zhang` →
`Xu and Zhung` (equal length, one occurrence), test
`test_every_published_reach_figure_recomputes_from_its_sentences`:

| cell | expect | got | runtime has mutant | disk has mutant | verdict |
|---|---|---|---|---|---|
| A clean control | GREEN | GREEN | False | False | OK |
| B one sentence mutated | RED | RED | True | True | OK |
| C restored byte-for-byte | GREEN | GREEN | False | False | OK |

Byte-for-byte restore verified by SHA-256. Runtime matched disk in every cell of both
matrices — no inversion. **D1 says the instrument can lie; these two say it did not lie
here.** D1 itself stays open: the finding is real and the harness it asks for is still not
part of `sdk/tests/`.

**The cheap answer that would settle it for free:** if either mutation was reverted with
`git checkout` rather than a copy, the mtime changes and the stale cache is defeated. One line
of evidence closes it.

**The general form, worth more than the two instances:** every mutation-proved result this lab
has produced is only as good as whether its author happened to clear the cache — and mutation
testing is the main way both live sessions have been proving that recomputes are live. Until
the harness in D1 exists, treat any mutation result produced without the guard as **unproven
rather than merely unverified.**

## E. Standing task-list items not yet executed

| # | Item |
|---|------|
| E1 | Print the 30 unprinted self-audit blind spots. |
| E2 | Fix the completion-record collector writing zero-byte `.done` files. |

## F. Repo professionalization — Katie's §7, 2026-08-11. **BLOCKED BY DESIGN.**

**The block is Katie's own sequencing and it is not a delay to be worked around:** *"after
Ladder V converges — not during"*, because path moves under active worktrees create merge
chaos and moves during an open verification poison the ladder's paths. It sits here, in the
queue, rather than in flight.

**Release conditions, all four:**

1. Ladder V converged (the fixed point, not a clean sweep — see the ladder's termination rule).
2. Every family drained or checkpointed. No agent holding open work in the tree.
3. One dedicated agent, one branch `chore/repo-structure`, one quiet window.
4. A written `MOVE_MAP` (old → new, **every** file) committed **first**, before any move.

**Mechanics that bind that agent:** `git mv` only, history preserved; imports, launchers,
cron and systemd paths updated **in the same commits** as the moves; full test suite green
after **every batch**; the sanctioned `sweep()` helper re-pointed (it is B1's deliverable, so
B1 lands first); no history rewrite; nothing load-bearing deleted without a docket entry.

**Pointers that will dangle when `scripts/` moves under `ops/`** — a running list, because
each is a live cross-file dependency and G3 requires them updated *in the same commit as the
move*, not afterwards. Add to it as they are created; this is cheaper to maintain now than to
discover during the window:

- `scripts/corpus_figures.py` — `docs/MEMORY_ARCHITECTURE.md` §5 points at it by path, having
  replaced its hardcoded corpus counts with a call to it. If it moves and the pointer does
  not, the map's central section instructs the reader to run a command that does not exist.
  *(Raised by peer session `certonomous-3b`, whose agent holds the other half of that repair.)*
- `scripts/sweep.py` — B1's sanctioned helper, named by G3 explicitly.
- `scripts/self_audit.py` — invoked by name from the test suite and from several campaign
  records.
- `scripts/fail_open_scan.py` and `sdk/tests/test_fail_open_scan.py` — the scanner hardcodes a
  path to `scripts/self_audit.py` **and pins a historical commit for its positive control**. So
  a move breaks **the control rather than the scan**, which is the quieter and worse failure: a
  positive control that silently stops working is how a scan starts reporting confident
  negatives. *(Raised by the peer session; reasoning kept as they put it, because the reason is
  sharper than the fact.)*
- `demo-output/website/campaign/F7_runs/old_spec_readings.py` — reads tracked field files by
  relative path.

**Target shape** (proposed, then executed): product source under `certonomous/` or a retained
`sdk/`, with `workflows/`, `agents/`, `kernel/` beneath it; `ops/` for launchers, auto-stop and
preflight; `docs/` as the **only** documentation home, with `charters/`, `standards/`,
`research/`, `architecture/`; `cases/` for configs and birth certificates, **never results**;
`evidence/` gitignored with a README explaining what lives there and why it is untracked;
`web/` for site-bound artifacts. Root reduced to README, the LICENSE decision, top-level
configs, and directories. **Nothing loose at root.**

**READMEs:** root README = what Certonomous is in three sentences, a 30-second architecture
sketch, how to run one mission, a repo map at one line per directory, and a pointer to
`docs/`. Every top-level directory gets its own short README naming purpose and entry points.
The qg-closure Q2 standard applies — goals and structure, professional register, no stale
claims — and **every number quoted obeys L-79: regenerate it, or carry its provenance.**

**Acceptance is a test, not an opinion — the cold-visitor test.** An agent with no context
clones the branch and must answer, within one screen per level: what is this, how do I run a
mission, where are the charters, where is the evidence for claim X. **Every question it has to
dig for is a defect.** Then Sanaa walks the tree herself before merge. That second gate is a
**taste gate and taste is hers** — it is not delegable to a checklist.

**One finding already, made while filing this and worth landing before the move window opens:**
G5 asks that tracked generated artifacts move to a gitignored `evidence/` or leave tracking.
They exist in quantity **today** — `demo-output/website/campaign/F7_runs/F7a_R1/` alone tracks
OpenFOAM time directories (`0.025/U`, `alpha.water`, `phi`, `uniform/functionObjects/…`) as
version-controlled files. That is solver output in git. **Scoping it is zero-compute and can
be done now**; the moves themselves wait for the window with everything else.

## G. Naval campaign — Katie's §8, 2026-08-11. Executing the zero-compute half now.

| # | Item | Compute? | State |
|---|------|----------|-------|
| G1 | **H1 F7a re-gate.** Pin the measurement definition **contractually** in the gate spec — probe row, front criterion, time origin: the exact ambiguity that produced the false FAIL. Then re-run and take the verdict either way. | Spec: **no**. Re-run: **yes** | **DONE, and the re-run turned out not to be needed for the verdict.** `campaign/F7a_REGATE_SPEC.md` §2 pins all four definitions; §1 exhibits the old ambiguity as measured fact (+13.4% vs −16.1% on the same solve); §3 takes the verdict **FAIL, max +11.03%**, from already-tracked fields at **zero compute**. Compute request re-scoped and its expensive half recommended against — see G1a |
| G2 | **H2 Wigley hull.** Wave-making resistance vs published data at 2–3 Froude numbers; free-surface mesh discipline written into a new marine section of `MESH_STANDARD`; birth certificates as everywhere. | Yes | Mesh section and pre-registration can precede it |
| G3 | **H3 DTMB 5415.** Resistance vs open workshop data — the credibility case naval people recognise on sight. Staged per doctrine: feasibility → physics (wave pattern qualitatively right) → gate rung. | Yes, staged | Staging plan is zero-compute |
| G4 | **H4 extensions, filed as COSTED PROPOSALS and not auto-run:** KCS container ship; propeller open-water curve vs workshop data ~~(reuses F8's MRF machinery — the naval turbine)~~ **— see the amendment below, the reuse premise does not survive**; seakeeping / added resistance, which needs wave BCs we may not have, so **the deliverable is the capability-gap map, honest about what is missing.** | Filing: **no** | Filing now |
| G5 | **H5** Every naval gate lands on the credentials wall with regime metadata like everything else, and **Naval becomes a wall category.** Katie's GTM list already touches marine engineers, so these wall entries are sales artifacts the day they exist. | No | Follows each gate |

**State after the 2026-08-11 zero-compute pass.** G1 done (above). G2 mesh
section done — `docs/standards/MESH_STANDARD.md` §7, with §7.0 stating why it
landed there rather than in `docs/MESH_STANDARD.md`, and the Wigley comparison
stations pinned in `campaign/NAVAL_CAPABILITY_GAP_MAP.md` §6.2a. G3 staging plan
done — `campaign/F7c_DTMB5415_STAGING_PLAN.md`, now carrying a **Stage 0** it was
missing (see G3a). G4 done — three proposals filed, and the gap map delivered.

| # | Amendment | Owner |
|---|---|---|
| **G1a** | **The F7a compute request, re-scoped.** The re-gate needs no compute to produce a verdict, so the request is now: **buy the zero-core-min comparison-basis item (R0)**; **do not buy** the a/512 rung (R1a, **760–1,520 core-min**, 2–4× the entire R1 campaign) to settle the shape of a convergence sequence. Reason, measured: `res16_papermodel` — comparator physics, mesh and domain all matched — sits **+23.3% ahead of the comparator's own published curve**, an offset larger than the +8.2% residual the campaign has been chasing. Refining the mesh explores a direction already shown to be small. Priced in `campaign/F7a_REGATE_PREREGISTRATION.md` §5. | Katie |
| **G1b** | **The compressed version of the D-12 story is wrong, and D-12 names six files that carry it.** "The F7a FAIL was a measurement artifact" is false: the ambiguity is worth ~20 points of the *originally reported* number and **essentially none of the current one** — at dy ≤ a/32 every reading of even the old definition lands +7.8% to +11.9%, all failing 5%. The six files are not individually wrong; the summary that circulates is. Not edited here: six near-verbatim copies is exactly the amendment hazard D-12 exists to flag, and C3 gives the case record the home. | fleet |
| **G3a** | **DTMB 5415 has no verified open geometry route** — ITTC-cited navy host **DNS-dead**, `simman2014` **registration-walled**, `simman2008` **TLS cert mismatch**. Its reference *data* is the best of the four (ITTC 27th Resistance Committee: CT, sinkage, trim at Fr 0.1/0.28/0.41 across **eleven** tanks), which is what makes it look fundable until someone tries to mesh it. **Registration is an external interaction — PARKED and reserved to Katie.** Filed as Stage 0 of the staging plan. | Katie |
| **G3b** | **The naval ordering docket §8 implies is inverted by the evidence.** By blockedness: propeller open-water (**not blocked by the ladder rule at all**, 900 core-min) → wave-capability step (135) → KCS (3,000; data open and tabulated, geometry verified) → **DTMB 5415, the most blocked of the four**. Recommendation only; §8's sequencing was written before this evidence existed. | Katie |
| **G4a** | **`grade_f7a.py` averages spurious post-wall crossings into its reported mean** — it prints "mean −0.8%" for `res16_base` and "mean −6.7%" for `res16_papermodel`, both arithmetic over ≈ −87% artifacts produced when the front passes the far wall and the furthest-crossing search picks up a crossing back in the collapsing column. Fixed **by contract** in `F7a_REGATE_SPEC.md` §2.2 (monotonicity guard); **not fixed in the script**. B2's class. Any number taken from that script's unrestricted mean line is unframed until re-derived. | fleet |

**The honest note about H4's third item:** "needs wave BCs we may not have" is a claim about
our capability, and the deliverable Katie asked for is the **gap map**, not a workaround. An
agent that discovers we lack the boundary conditions and quietly substitutes something else
has destroyed the deliverable. The map is the product.

> **[AMENDED 2026-08-11 — G4's propeller premise did not survive checking. Original text
> retained above rather than edited, per the supersession rule; the claim is Katie's and she
> is entitled to see it challenged rather than quietly reinterpreted.]**
>
> G4 describes the propeller open-water case as *"reuses F8's MRF machinery — the naval
> turbine"*. That phrasing is Katie's, from §8 H4, and I transcribed it here. **An evidence
> audit of the F8 case files contradicts it on four points**, and pricing the proposal on the
> reuse premise would understate it badly:
>
> - **F8 is a WIND turbine in AIR** — `simpleFoam`, steady, incompressible (`nu 1.4805e-05`,
>   kinematic `p`, no thermophysical model), single-phase, Spalart-Allmaras.
> - Its MRF **is genuine** (a real `constant/MRFProperties`, `omega 7.5398`, zone actually
>   built by `topoSetDict` — not SRF, not AMI, not `rotatingWallVelocity`) — **but the rotating
>   zone is the entire domain**, which is the one thing a propeller case must not copy.
> - **F8's steady-MRF branch is closed on evidence three ways, with ZERO gated CFD numbers.**
>   Reuse would inherit a branch that never produced a gated result.
> - The geometry is a fixed 68 MB / 330,950-triangle STL with **no generator anywhere in the
>   repo**, so a propeller blade is **100% new work**, not a parameter change. And **the sign
>   convention is inverted** — F8 extracts power, a propeller absorbs torque — which is
>   precisely the error class that cost F8 three riders.
>
> **Status: routed to the naval agent to confirm or contradict against the case files
> itself**, because the audit reached me second-hand and this lab's rule is that a grader
> executes rather than relays. Not treated as settled here.
>
> **Calibration datum from the same audit, and it is load-bearing for every H4 price:** F8's
> own proposal carried `est_core_min: 6` against **47.7 core-min actual — an 8× overrun**,
> at a measured 0.54–0.60 core-s/iteration for 230k cells. That is the house's demonstrated
> optimism factor on a rotating case. *(A "0.145 core-s/iteration" figure in F8 §5 contradicts
> every other number in its own record and is not to be used.)*

> **[AMENDED 2026-08-11 — the F8 reuse premise in G4 does not survive checking, and the
> premise was mine to check.]** Katie's §8 describes the propeller item as reusing F8's MRF
> machinery, *"the naval version of the turbine"*. I transcribed that into G4 without opening
> F8. An agent sent to price the reuse found **both halves wrong**:
>
> - **F8 is a WIND turbine in AIR** — `simpleFoam`, steady, incompressible, single-phase,
>   Spalart–Allmaras — not a naval one. And its steady-MRF branch is **closed on evidence
>   three ways** with **zero gated CFD numbers**, so there is no validated result to inherit.
> - **The geometry does not transfer at all.** `blade.stl` is a fixed 68 MB, 330,950-triangle
>   S809 wind blade with **no generator anywhere in the repo**. A propeller blade is **100%
>   new work**.
> - **The sign convention is INVERTED** for a propeller, which absorbs torque rather than
>   producing it — and that is precisely the error class that cost F8 three riders.
> - What genuinely transfers is **dictionaries and process discipline**, which is real but is
>   not what "reuses the MRF machinery" prices at.
>
> One more thing found while pricing it, and it is a calibration fact about the whole proposal
> system rather than about F8: **F8 cost 47.7 core-min against an `est_core_min` of 6 in its
> own proposal — an 8× overrun.** Any naval estimate built by analogy to F8's *estimate*
> inherits that error; build them against its *measured* 0.54–0.60 core-s/iteration at 230k
> cells instead. (F8's own record also carries a "0.145 core-s/iteration" figure in its §5
> that is inconsistent with every other number in the same document; do not use it.)
>
> **And the thing not to copy:** F8's MRF cellZone is **the entire domain** — 230,135 of
> 230,135 cells. It ran, and it is not what an MRF zone is for.
>
> This is Katie's text, so the correction goes to her rather than being applied silently. The
> proposal is not withdrawn — a propeller open-water gate against PPTC/VP1304 is still worth
> filing — it is **repriced from scratch rather than by analogy**, and the report to Katie
> says the analogy was the thing that failed.
