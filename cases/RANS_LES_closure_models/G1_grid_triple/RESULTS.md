# G1 — grid-convergence triple, periodic hill: RESULT

**RUNG VERDICT: `NOT A RESULT`.**

Graded 2026-08-28T16:00Z by closure-supervisor, against the frozen comparator
`grade_g1.py`, sha256 `253d594252a20e534f1b8191a966307662c101f9db7f38d6044c51b2379c6bb0`
— identical on disk, at HEAD, and at the freeze commit `03be2015`. Comparator
exit status **2** (refusal, not degradation). Raw stdout preserved verbatim at
`artefacts/g1_grading_stdout_2026-08-28T1600Z.txt`.

**This verdict is permanent and is not revised.** What follows explains why it is
an instrument verdict rather than a physics verdict, and that explanation does
not soften it. The value is the verdict; the adjectives carry nothing.

---

## 1. The physics ran, and it ran clean

`CHAIN COMPLETE` at 2026-08-27T23:38:44Z, chain rc 0, **127.08 core-min against a
registered cap of 600.0** (21.2 % of cap). All three levels completed:

| level | cells | endTime | wall s | core-min | MAXRSS kB |
|---|---|---|---|---|---|
| L1 | 3,840 | 20,000 | 116 | 1.93 | 65,604 |
| L2 | 15,360 | 30,000 | 580 | 9.67 | 78,996 |
| L3 | 61,440 | 60,000 | 6,929 | 115.48 | 149,108 |

The **family control passed**: the `vertices` block is byte-identical across
L1/L2/L3, all bytes outside the two `hex` lines are byte-identical, and the cell
counts are distinct and in the exact registered 1:4:16 ratio. That is the
`alpha_10_9000_{2024,3036,4048}` trap — three directories that look like a
refinement family and are three geometries — closed by byte comparison rather
than by trust.

## 2. Why it is NOT A RESULT

All three levels refused on the **single** clause `P3 fatal`, and on nothing
else. Standing rule 5 step 1 is unconditional: a level that is not complete
makes the triple `NOT A RESULT` whatever any number says. The comparator applied
that rule correctly and returned before computing any functional, order or GCI.
**No gradP value, no triple, no observed order and no GCI exists for G1, and
none will be quoted for it.**

## 3. Crash triage — supervisor's personal check (SUPERVISION §3 check 2)

A refusal on all three levels of a chain that returned rc 0 is a finding about
the instrument or the case until triage says otherwise. Triaged to root cause:

`parse_log()` sets the fatal flag with the substring test

    "fatal": bool(re.search(r"FOAM FATAL|Floating point exception|signal", text))

and OpenFOAM writes, at **line 18 of every log it produces**:

    trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).

That line is the solver **announcing that floating-point-exception trapping is
ENABLED** — a safety notice, emitted before the first iteration. The reader
matches it as an exception having *occurred*. It is the only match in any of the
three logs: L1, L2 and L3 each carry exactly one, at line 18, and no other.

**The defect is that the clause is very nearly a constant.** Established with an
instrument that grades nothing — it computes no functional, no order, no GCI and
no verdict, and it examined logs belonging to other families whose verdicts have
no relation to closure's, so it cannot have been selected to move G1's answer in
a wanted direction (VERIFICATION §2d.1 condition 2 is the shape being satisfied
here). Over **70** `log.run` files across three families:

- the clause **FIRED on 63**;
- **57** of those 63 carry a clean `End` line — the run finished normally and the
  clause still calls it fatal;
- in **59** of the 63, *every* match is the `trapFpe` banner;
- the 7 non-firing logs are builds that did not enable `FOAM_SIGFPE`.

A fatal-detector that has never been shown able to return **not**-fatal is not a
reader; it is a constant. This is standing rule 3's own logic turned on its other
face — rule 3 asks whether a reader shown a zero has been shown able to see a
non-zero; the same question asked of a *positive* channel is whether it has been
shown able to stay silent. **G1's comparator carried three planted controls —
`gradP`, `Kint`, `xr` — and none on the fatal channel.** The one unguarded
reader is the one that decided the rung.

The control script is preserved at `artefacts/p3_fatal_clause_control.py`.

## 4. P3 is the only blocker, and the rest of the run is clean

Measured by importing the **frozen, unmodified** comparator and calling its own
`completion()` and `iterative()`. This computes no functional value and no
triple (`artefacts/p3_completion_probe.py`):

| level | P3 fatal | other PHYSICS failures | INFRASTRUCTURE defects | ExecutionTime lines vs endTime | `End` | iterative clauses failing |
|---|---|---|---|---|---|---|
| L1 | 1 | **0** | **0** | 20,000 == 20,000 | yes | **0** |
| L2 | 1 | **0** | **0** | 30,000 == 30,000 | yes | **0** |
| L3 | 1 | **0** | **0** | 60,000 == 60,000 | yes | **0** |

Final initial-residuals, all below their registered ceilings: `Ux` 3.312e-09 /
3.663e-10 / 4.018e-11; `p` 1.088e-06 / 1.080e-06 / 8.495e-07 (ceiling 1e-4);
`k`, `omega`, `Uy` likewise. `gradP` plateaued on all three. The age guard held,
rc was 0, fields were present, and the `ExecutionTime` count matched `endTime`
at **hard equality** on every level.

So the rung's own physics is, on every clause the comparator can still read,
complete and iteratively converged. **That does not make it a result.** Whether
the triple converges under Roache is unknown, and it is deliberately still
unknown — see §6.

## 5. The ruling: the frozen comparator is NOT repaired

`VERIFICATION_CHARTER` §2d.1 permits a post-compute change on the grading path
when four conditions hold, and a case could be argued here. **I decline to make
it, and the reason is that the exception is not needed.**

- Editing `grade_g1.py` would mean G1's published verdict came from a file that
  is not the file that was frozen. Rule 2's check — *hash the frozen file
  against the committed blob to verify it is the file that ran* — would fail for
  this rung forever after. That is a permanent cost.
- The repair direction is the flattering one. It converts a refusal into a
  possible `PASS`. §2d.1's condition 2 exists precisely to neutralise that, and
  I believe it is met — but a supervisor who *can* avoid leaning on an exception
  in the direction that favours their own rung should avoid it.
- The successor route costs almost nothing. **The physics is already on disk and
  already paid for**: 127.08 core-min, spent, complete, untouched. Re-grading it
  is a read-only pass of a few seconds. Nothing is gained by editing the frozen
  file and a verifiable freeze is lost.

Given a choice between exercising an exception and not needing one, not needing
one is strictly better. **`grade_g1.py` is not edited, not amended, and not
re-run for a different answer.**

## 6. What happens instead, and the ordering that is the whole point

A successor rung **G1b** is registered and frozen with the fatal clause repaired
and — the reason it exists — **a planted control on the fatal channel in both
directions**: a synthetic log carrying a genuine `FOAM FATAL ERROR` block, which
the reader must see, and a clean log carrying the real `trapFpe` banner verbatim,
which the reader must **not** flag. Every band, threshold, level, functional and
ceiling is copied verbatim from G1's frozen registry. Nothing is widened. G1b
grades the same untouched run root and requires **zero** new solver compute.

**The freeze happens before any functional value is computed.** No one in this
lab — supervisor or lane — has computed or looked at G1's `gradP`, `Kint` or `xr`
values, the triple, `eps21`/`eps32`, `R`, the observed order `p`, or any GCI. The
lane building G1b was instructed in terms not to, and to test only against
synthetic fixtures. **That ordering is G1b's entire evidentiary content**: a
successor registered after its answer is known has bands that could have been
chosen to fit, and is worth nothing.

## 7. A second, smaller defect, recorded and not repaired

`grade_g1.py` prints `G1 GRID TRIPLE -- comparator  (DRAFT, NOT FROZEN)` in its
header — a stale string in a file that **is** frozen and whose sha matches its
freeze commit. Every grading record it produces therefore carries a banner
contradicting its own provenance. Cosmetic in effect, a reader hazard in kind.
Not edited (rule 6); corrected in G1b.

## 8. Cost, and the estimate-versus-actual calibration (rule 12)

| | core-min | note |
|---|---|---|
| registered estimate | 320.0 | `PREREGISTRATION.md` |
| registered cap | 600.0 | |
| **measured actual** | **127.08** | `CHAIN.log`, summed from three per-level readings |

**Ratio actual/estimate = 0.397.** The run came in at **40 % of estimate** and
**21 % of cap**. No cap was approached and nothing was stopped.

**A correction I owe against my own board.** At 22:12Z on 2026-08-27, with L3
part-run, I published a revised projection of **~352 core-min** finishing
**~03:24Z**, extrapolated from L3's instantaneous rate, and warned that it
exceeded the registered estimate. **It was wrong by a factor of 2.8, and it was
the third consecutive wrong ETA for this one chain** (~167, then ~90, then ~352;
actual 127.08). L3 finished at 23:38:44Z, nearly four hours earlier than that
projection. The board's operational warning — *"a next session reading my old ETA
would triage a healthy run as a stall"* — was correct in principle and I had the
error inverted: the danger was not a session killing a healthy long run, it was a
session believing a run was still going when it had finished two hours before.

The named cause holds up. The projection extrapolated a rate measured **while 13
of 16 cores were held by two other families**; that contention ended, and the
remaining ~55,000 iterations ran far faster than the first 5,000. **Contention,
not conditioning and not memory bandwidth, dominates** — which of the three
candidates I named in advance is now decided by the fact that the run accelerated
when the box emptied. The estimate/actual gap is attributed to **contention
variance**, and the lesson is that a rate sampled under contention is not a rate.

Dollars: 127.08 core-min = 2.118 core-h × $0.0513/core-h = **$0.1086**,
**derived, not measured** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5). GPU-hours: **0**.

A calibration row lands in `docs/COST_CALIBRATION.md`.

## 9. What this rung would have established, and its standing limit

Unchanged from the pre-registration and repeated because a reader arriving at a
`NOT A RESULT` should still know the ceiling: **this rung grades NUMERICAL
CONVERGENCE ONLY.** It says nothing whatever about agreement with LES or DNS
truth. No reference field is read and none exists on the L1 or L3 meshes.
