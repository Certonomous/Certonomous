# V16 — grade round 5 (independent, worktree-isolated)

**Grader:** an agent that wrote none of this code, in its own checkout under R-ISOLATE part 1.
**Subject:** repo HEAD `1393b8b4`. Board read from the benchmark README at `deb91557` —
Reissmann 1, Wu 2, Liu 3, Montoya 4.
**Suite:** `sdk/tests/test_rank_claim_surfaces.py` — **90 passed** at `1393b8b4`.
**Live guard verdict at `1393b8b4`:** WARN, 4 findings, all four the two known quotations in
`docs/DOCKET.md` and `docs/INSTRUMENT_INTEGRITY_LEDGER.md` (docket D3). 1388 tracked UTF-8
surfaces opened, 131 naming an entrant, 608 placement expressions, **0 skipped**.

Method, per R-ISOLATE part 3: **every claim was executed, none was read.** For each declared
item the probes were constructed here rather than re-run from the author's fixtures — the
author's tests passing proves the author's tests pass. All probes are committed executable at
`campaign/V16_GRADE_ROUND5_PROBES.py`, assembled at import so this file and that one contain
no placement the guard can match.

## Verdicts on the five declared items

| Item | Verdict |
|------|---------|
| **E1** skip-is-not-agreement | **CLOSED** |
| **E2** linear-algebra homonym discriminator | **NOT CLOSED** |
| **E3** rule B's recompute | **CLOSED** |
| **E4** sentence-boundary bind | **NOT CLOSED** |
| **L-76** absolute sweep over the rung's added lines | **CLOSED** |

### E1 — CLOSED

Executed against a corpus I controlled entirely (`_tracked_files` replaced with files I wrote;
the raise injected *inside* the guarded region by replacing `_placements`), driving each of the
four terminal branches and asserting the note reaches the **summary**, not only the frame:

| constructed state | branch reached | note in summary |
|---|---|---|
| travelling fault **+ a skip** | FAIL | yes |
| lab-record fault **+ a skip** | WARN (`internal`) | yes |
| travelling fault **+ an empty rule-A sweep** | FAIL | yes |
| lab-record fault **+ an empty rule-A sweep** | WARN (`internal`) | yes |
| a skip and nothing else | WARN (`notes`) | yes |
| an empty sweep and nothing else | WARN (`notes`) | yes |
| clean corpus (control) | **PASS** | n/a |

The middle four are the specific defect the author's comment describes as previously fixed —
another finding reaching its branch first. The note survives all of them, the skipped surface is
**named** in the detail (`raiser.md: … NOT counted as agreeing`), and the control still reaches
PASS, so the guard has not simply been wedged shut.

### E2 — NOT CLOSED

"Nearest wins, left-hand only" is a **proxy** for the grammatical subject, and the ordinary
genitive/prepositional construction inverts the proxy. In probe `E2 FP genitive after the noun`
— a Reynolds-stress-tensor sentence carrying an entrant's genitive between the noun and the
ordinal — the surname ends at offset 33 of the 80-character window and the nearest
linear-algebra noun at 26, so `_place_linalg_subject` returns `False` and the guard binds the
ordinal to that entrant, faulting a sentence whose grammatical subject is a tensor. Four such
sentences fault; two more, with the noun nearer, mute a *real* wrong placement. Three controls
behave correctly. (The sentences are assembled in the probe file and are not written out here,
under the convention docket D4 names.)

This lab's four entrants are turbulence authors, which is the guard's own stated reason for
rejecting the previous repair: *"a turbulence noun beside an entrant's name is the ordinary case
here, not the exotic one"*. The current repair does not merely keep the false negative it
declares — it adds the false positive the same comment calls **the worse trade**.

### E3 — CLOSED

Five-cell mutation matrix, `__pycache__` removed before **every** cell (docket D1), each cell a
fresh subprocess, the whole matrix printed by **one** driver invocation so an inversion cannot
hide across runs:

| cell | expected | observed |
|---|---|---|
| 1 clean control | PASS | PASS |
| 2 published figure `(5, 5,` → `(4, 5,` | FAIL | FAIL |
| 3 a committed rule-B sentence broken | FAIL | FAIL |
| 4 a second committed rule-B sentence broken | FAIL | FAIL |
| 5 restored control | PASS | PASS |

Cells 3 and 4 are the direction that actually proves the recompute is live: the published figure
is untouched and must still go stale. `git status` was clean after the run, so the restores were
exact.

### E4 — NOT CLOSED

The repair is symmetric and the symmetry is not the invariant that matters. Each side appends one
character of what follows the gap — true, as claimed — but `_PLACE_SENTENCE` closes a boundary
only on `[.!?] … \s … [A-Z("'*`]`, so an appended character closes it **only when it is an
uppercase letter**, and neither side's appended character reliably is:

- **left** appends the ordinal token's first character, which is a **digit** in every `Nth place`
  form: in probe `E4 FP left, digit-form ordinal opens the sentence` the probe string is
  `' ran the duct case. ' + '<digit>'` and the boundary is **not** detected. It is likewise
  lowercase for a sentence-initial rank token, and for a lowercased word-form ordinal — the form
  a markdown bullet, a log line or a lowercased heading produces;
- **right** appends the matched name's first character, and surnames match case-insensitively,
  so probe `E4 FP right, lowercase citation form of the surname` binds across the stop.

Six shapes bind across a full stop; the author's own two cases — a capitalised rank token and a
capitalised surname — hold, as do both over-fix controls: the guard still binds normally with no
boundary, and in the sentence after a stop. The failure axis is the **character class**, not the
side. One entry of this round's probe file was written as a control and its own regression check
reclassified it as a fifth false positive, which is the argument for committing probes rather
than prose.

### The L-76 absolute sweep — CLOSED

Surface list derived, not enumerated: the V16 commit set is `git log --format=%H 862d2cff^..HEAD
-- sdk/tests/test_rank_claim_surfaces.py campaign/V16_*` → **12 commits**, touching **5
surfaces**, contributing **3323** distinct added lines, of which the lines still standing at HEAD
carry **84** absolutes. Nearly all are in the *safe* direction — declaring a limit ("cannot fire
where nobody is named", "cannot be recomputed", "cannot tell use from mention"), which is what
L-76 asks for. The overclaim-direction absolutes were read individually. The strongest, and the
direct successor to L-76's own third instance, is `_published_board`'s **"THIS FUNCTION CANNOT
RAISE AN `Exception`"** — and it is now structural rather than a promise: the whole read-and-parse
is `try: return _parse_published_board() except Exception`, with `BaseException` propagation
declared in the same paragraph. The absolute is backed by the structure it names. No absolute in
the rung's added lines was found asserting a safety the code does not have.

## R-VALUE

Both open findings are **material**, and both are **latent**:

- Swept mechanically over `git ls-files` at HEAD (20571 paths, 1224 opened, files read in Python,
  UTF-8, ≤ 4 MB — the shell's `grep` is `ugrep --ignore-files` and was not used), the tracked
  corpus contains **0** instances of the E2 false-positive shape and **0** of the E4
  false-positive shape. The only two E4 candidates are the guard's own comment quoting the
  already-fixed capitalised case, and the guard is correctly silent on both. **No published
  figure moves and today's WARN is unchanged.**
- They are material anyway, because each falsifies a **specific written claim** about the guard,
  in the direction that produces a false FAULT — and on a travelling surface a rule-A fault is
  FAIL severity. E4's *"Both sides now carry the next character"* reads as "the boundary defect is
  fixed"; it is fixed only for uppercase-initial probes. E2's stated discriminator is *what is
  being said to be rank N*; the implementation decides by token proximity and inverts on the
  ordinary genitive.

So this round did **not** return only findings that would leave an external reader's belief
unchanged, and the R-VALUE counter does not reach two. **V16 does not close on this round.**

Both findings are **inside the declared scope** (E2 and E4 are two of the five), so under
R-CONVERGE they belong to the rung and are not docket items — this is not scope creep, it is the
declared criteria failing when executed. Two findings that fell *outside* the five are filed as
**docket D5** (a worktree cut behind the subject commit — a second fail-open shape in R-ISOLATE,
not covered by its gitignore caveat) and **docket D6** (the guard publishes four recall figures
and no precision figure, and both findings above are precision defects).

**What would close E2 and E4 next round:** for E4, a boundary test that does not depend on the
case of the character it appends. For E2, a discriminator anchored to the clause rather than to
token distance — or, if nearest-wins is kept, an honest precision figure beside the four recall
figures (D6) and the genitive construction added to the blind-spot list, so the frame stops
claiming a discriminator it does not implement.
