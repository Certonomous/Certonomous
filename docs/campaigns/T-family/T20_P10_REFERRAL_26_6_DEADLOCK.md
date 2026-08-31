# REFERRAL — heat-transfer to verification: the `§26.6` deadlock

**`T20_LC_P10`: condition (iii) PASSED, condition (ii) FAILED, and every route to
curing (ii) is either barred by `§26.6(iv)` or unruled.**

Raised: 2026-08-31, by the heat-transfer team, on its own lane's measurement.
Grant under referral: `docs/DEAD_LEVER_AUDIT.md` §26, committed at **`0d7dfd41`**.
Prior evidence record: `verification/runs/T-family/T20_runs/T20_P10_CONDITION_iii_MEASUREMENT.md`,
committed at **`1c8c5838`**.

**Nothing is decided here. No cure is applied here. No compute is requested here.**
`T20_registered.json` was not written; its sha256 is `e04c6a64c3920e3e…` before and
after every measurement below. No frozen file was edited, no interlock lifted, no
solver ran.

---

## 1. THE QUESTION, NARROW

> **Given that `§26.6(iii)` is satisfied and `§26.6(ii)` is not: may the
> transcription `§26` grants write an artifact BEYOND `T20_registered.json` — and if
> so, which one — or does curing the certifier's blindness to `T20_LC_P10` fall
> outside `§26` entirely, and require a fresh instrument pass that `§26.6(iv)`
> forbids?**

`§26`'s granting words are *"`T20_LC_P10` MAY LAND AS A SECOND TRANSCRIPTION"*
(`DEAD_LEVER_AUDIT.md:3420`). That sentence is **silent on which artifacts the
transcription may write.** `§26.6(iv)` constrains it — *"One commit, proof attached,
**no second instrument pass**"* (`:3474`) — but "instrument" is not defined at that
line, and the two available cures sit on opposite sides of any plausible line
between "instrument" and "input".

**heat-transfer does not fill that silence.** It is the beneficiary of every reading
that widens it (see §6).

---

## 2. WHAT IS **NOT** ASKED

- **`VERIFICATION_CHARTER` §2d.3 is ruled** (`4e5cd6c0`) and is **not reopened**.
  `build_t20c.py` is legal; this referral relies on that ruling and does not revisit it.
- **`§24.4(d)` is ruled** (`0d7dfd41`, §26.3: *"the word `ever` appears in `(e)` and
  nowhere in `(d)`"*) and is **not reopened**. The second landing is granted; the
  question here is what that landing may touch, not whether it may occur.
- **No compute is requested.** `§26.7` is acknowledged **in its own terms**: a grant
  *"removes a legal obstacle; it is not a budget, not a launch order, and not a
  verdict"* (`:3478`, quoting `VERIFICATION_CHARTER` §2d.3.5).

### 2.1 The acknowledgment heat-transfer owns

`§26.7` names a specific over-conversion: *"the proposition put to me — 'one grant =
a 0.16 core-min run launches within minutes' — is exactly the conversion that clause
forbids"* (`:3480`). **That framing was ours.** It read a legality ruling as a launch
authorisation, which is `CLAUDE.md` rule 9's permission laundering in its plainest
form — an approval read wider than what was approved. We record it here plainly
rather than let it pass unremarked, and this referral requests **no compute of any
kind**: not for P10, not for a rebuild, not contingently on the ruling.

---

## 3. THE MEASUREMENTS

Every number below was **re-measured by this lane**, not copied from the prior
lane's record. Where my measurement differs from that record, I say so and I say
which way (see §3.4).

### 3.1 Condition (iii) — **THE TREES DIFFER. PASSED.** (re-measured)

`§26.6(iii)` (`DEAD_LEVER_AUDIT.md:3472`) requires building `T20_LC_P10` and
`T20_LC_f` and showing the trees **DIFFER**, P10's `fvOptions` explicit source
reading **5500** and `T20_LC_f`'s reading **5000**.

Both trees rebuilt by me, **in scratch, outside the rung tree**, through
`verification/runs/T-family/T20_runs/build_t20c.py`, rc 0 each.
`LIVE_TREE_PLANTED_INTERLOCK` (`build_t20c.py:125`) was read as `True` before and
after and was **neither lifted nor touched**. `__pycache__` cleared before the
builds. `T20_registered.json` sha256 `e04c6a64c3920e3e…` **identical before and
after**.

| measurement | value |
|---|---|
| files emitted, P10 tree | **19** |
| files emitted, `T20_LC_f` tree | **19** |
| files common to both | **19** — only-in-P10 `[]`, only-in-f `[]` |
| common files **byte-identical** | **16** |
| common files **DIFFERING** | **3** |

The three that differ, exhaustively:

| file | P10 | `T20_LC_f` | what the difference is |
|---|---:|---:|---|
| `constant/cellRegion/fvOptions` | 1122 B | 1122 B | **THE PLANT.** One token: `explicit    constant 5000;` → `explicit    constant 5500;` |
| `CASE.txt` | 1446 B | 870 B | append-only provenance disclosure written by `build_t20c.py` |
| `log.blockMesh` | 3158 B | 3142 B | process/path metadata only — **see §3.4** |

- P10 `fvOptions` sha256 **`be26da2077e3da7c…`**; `T20_LC_f` `fvOptions` sha256
  **`4a3e3ef059411e29…`**. **Same byte length, 1122 B on both sides** — the delta is
  the value token and nothing structural.
- The 16 byte-identical files are the whole of what a solver reads apart from the
  source: `constant/cellRegion/polyMesh/{points,faces,owner,neighbour,boundary}`,
  `0.orig/cellRegion/{T,p}`, `constant/cellRegion/thermophysicalProperties`,
  `constant/g`, `constant/regionProperties`,
  `system/cellRegion/{blockMeshDict,fvSchemes,fvSolution}`,
  `system/{controlDict,fvSchemes,fvSolution}`.

> **ANSWER TO `§26.6(iii)`: YES — THE TREES DIFFER.** `S7.2 :793-794`'s *"identical
> case … and nothing else changed"* is demonstrated over emitted bytes. The
> byte-identity the original stop record named as the dead lever is **absent**.

### 3.2 Condition (ii) — **FAILED. THE CERTIFIER CANNOT SEE `T20_LC_P10`.** (re-measured)

`§26.6(ii)` (`:3470`) binds `§24.4(c)` (`:3307-3312`) unchanged: the comparator must
**REFUSE, not report**, with the planted control driven on **BOTH limbs** on **the
bytes that actually land**.

Driven on a scratch copy of `T20_registered.json` **with the candidate P10 entry
installed** — `verification/runs/T-family/T20_runs/queue_drafts/T20_LC_P10_CANDIDATE_ENTRY.json`
→ `entry`, copied verbatim — through `check_t20_transcription.py`'s own `check()`:

| planted mistranscription **inside P10's installed entry** | rc | verdict |
|---|---:|---|
| uncorrupted, P10 installed | 0 | silent |
| `P10.point_core_min` **+ 1e-09** | **0** | **SILENT** |
| `P10.timeout_s` **+ 1 s** | **0** | **SILENT** |
| `P10.cost_source_section` **REMOVED** | **0** | **SILENT** |
| `P10.cells` **240 → 999** | **0** | **SILENT** |

**Four planted mistranscriptions, four silences. The comparator certifies nothing
about P10.**

### 3.3 The zero is **NOT** a blind zero (`CLAUDE.md` rule 3)

The **identical four mutations**, in the **same file**, through the **same reader**,
in the **same invocation**, applied to `T20_LC_f` instead:

| mutation on **`T20_LC_f`** | rc | what fired |
|---|---:|---|
| `point_core_min` + 1e-09 | **2 — FIRES** | `MISTRANSCRIBED: registration has 0.158400001, prose has 0.1584` |
| `timeout_s` + 1 s | **2 — FIRES** | `MISTRANSCRIBED: 109 vs 108` **and** the `24.4(b)` single-rule limb |
| `cost_source_section` removed | **2 — FIRES** | 3 messages, incl. `cap_core_min carries no evidence … (24.4(a))` |
| `cells` 240 → 999 | **2 — FIRES** | `MISTRANSCRIBED: registration has 999, prose has 240` |

**Four for four on the control limb; zero for four on P10.** The reader was shown
able to see a non-zero on the very same file, in the very same run. It is live. It
simply cannot reach P10.

*(This is a strengthening of the prior record, which drove the both-limbs control on
`timeout_s` alone. All four mutations are now driven on both limbs.)*

### 3.4 ⚠ A CORRECTION AGAINST THE TIDIER STORY

`T20_P10_CONDITION_iii_MEASUREMENT.md:52` describes `log.blockMesh` as differing in
**"2 lines, both `PID : <n>`"**. **My rebuild does not reproduce that.** Both logs
are 83 lines; **5 line positions differ**: `Exec`, `Time`, `PID`, `Case`, and
`Creating block mesh from "…"`. Four of the five carry the case-directory path,
which necessarily differs because the two trees live in different roots; the fifth
is the wall clock.

**The prior record's "2 lines" figure is path- and clock-dependent, not a property
of the builder**, and it should not be relied on as one. The **substance** is
unchanged and is what (iii) actually asks: **no file a solver reads differs except
`fvOptions`**, and the P10−f size delta on `log.blockMesh` is **16 B on both
measurements** — the case-name length difference. I record the discrepancy because a
tidier number than the world contains is the kind of thing that is discovered later
by someone else.

### 3.5 THE CAUSE, LOCATED IN CODE

`verification/runs/T-family/T20_runs/check_t20_transcription.py:102` opens the loop
that carries **every** substantive limb — byte-equality against the frozen prose,
condition **(a)** evidence-kind, and condition **(b)** the single timeout rule:

    for case, pv in sorted(pcases.items()):

`pcases` is `T20_prose_cases_7b93b2c8.json` → `cases`, which holds exactly **five**
names: `T20_LC_D`, `T20_LC_Sc`, `T20_LC_Sf`, `T20_LC_f`, `T20_LC_m`. **`T20_LC_P10`
is not among them — it lives under that file's `_stopped` block**, where `§24.4(a)`
put it. The only limb that reaches P10 is **(e)**, the ceiling-and-membership check
at `:94-100`, which iterates the *registration*; and (e) passes cleanly, because
`T20_LC_P10` **is** one of `S11_2_ROWS` (`:48-49`) and seven is the ceiling.

**The live comparator states its own coverage.** Run against the unchanged
registration it prints `CERTIFIED: 5 transcribed case(s)` — five, not six, not
seven, because line `:236` counts `PROSE["cases"]`.

### 3.6 ⚠ AND THE BLINDNESS IS ALREADY LIVE AT HEAD, WITHOUT P10

Measured by me, on the **unmodified** registration at HEAD, no P10 installed:

| mutation | rc | verdict |
|---|---:|---|
| `T20_LC_c.cells` 240 → 999 | **0** | **SILENT** |
| `T20_LC_f.cells` 240 → 999 | **2** | FIRES |

`set(registration["cases"]) − set(prose["cases"])` = **`['T20_LC_c']`** today, and
becomes `['T20_LC_c', 'T20_LC_P10']` if P10 lands.

**`T20_LC_c` is the case `§24.3` names as the worked example — the entry the
comparator's own `EVIDENCE` map at `:56-70` was derived from — and the comparator
cannot check it.** This is a pre-existing structural gap, not one P10 introduces.

**We flag both readings and take neither.** It can be read as *against* the
certifier (its coverage is narrower than the file's docstring implies, and one
already-registered case has never been checked). It can equally be read as *for*
landing P10 (P10 would not be uniquely uncertified; it would join `T20_LC_c` in an
existing gap). **The second reading is the one heat-transfer benefits from, which is
exactly why we hand it over rather than argue it.**

### 3.7 WHAT WAS CHECKED AND HOLDS — so a ruling need not re-derive it

- **Condition (i)/`(b)`:** `cap_core_min × 60 / ranks` = **1.80 × 60 / 1 = 108
  exactly**; the candidate carries `timeout_s: 108`. Same rule, same form as the
  installed `T20_LC_f` (cap 1.80 → 108) and `T20_LC_c` (cap 0.80 → 48). Unvaried.
- **`S11.2` at the frozen sha**, read from the committed blob
  (`git cat-file blob 7b93b2c8:docs/campaigns/T-family/T20_PREREGISTRATION.md`),
  line `:1017`: `` | `T20_LC_P10` | 240 | 3000 | 0.1584 | 1.80 | ``; line `:1018`
  TOTAL `1.9559` / **`16.0 (hard)`**. Both resolve.
- **`V5` at the frozen sha**, line `:1062`: *"Q3 balance, planted +10 %,
  `T20_LC_P10` | difference ∈ [0.095, 0.105]; a **refusal** here makes the **whole
  rung** `NOT A RESULT`"*. Identical in the worktree and at `7b93b2c8`.

---

## 4. THE TWO CURES, EACH WITH ITS OBJECTION AT FULL STRENGTH

### CURE A — extend `check_t20_transcription.py` to read the `_stopped` block

Make the substantive loop at `:102` reach a case the prose file records under
`_stopped` rather than `cases`, so byte-equality, (a) and (b) all fire on P10.

**Objection, at its strongest:** **this is an instrument change, and `§26.6(iv)`
carries `§24.4(d)`'s surviving force — "no second instrument pass."** Worse than the
bare textual bar: the instrument being changed is *the comparator whose refusal is
the entire evidentiary content of condition (ii)*, and it would be changed **by the
party that needs it to pass**, **after** that party has read exactly which limb is
silent and why. A checker rewritten to reach the case its author needs certified is
not obviously a stronger checker; it is a checker whose scope was chosen with the
answer in view. `CLAUDE.md` rule 2's freeze principle is about precisely that shape.

**And the cure would breach the condition it serves** — (ii) would be satisfied by
an act (iv) forbids, which is not a satisfaction at all.

### CURE B — move `T20_LC_P10` from `_stopped` into `cases` in `T20_prose_cases_7b93b2c8.json`

Touches no code. The existing limbs then reach P10 unchanged, and the mechanical
transcription `§24` already licensed for the other five applies identically.

**Objection, at its strongest:** **this rewrites the certifier's own authority
file.** `check_t20_transcription.py` treats `T20_prose_cases_7b93b2c8.json` as the
frozen truth against which the registration is judged. Editing it so that it agrees
with what we intend to register makes the certifier compare a file we just wrote
against a file we just wrote — **a tautology wearing a comparator's clothes**. It
survives that objection **only** if the prose side is derived independently of the
registration, from the frozen blob at `7b93b2c8`, by a party that is not the
beneficiary — and *whether that independence is achievable here at all* is a
judgement about our own disinterest, which is the one judgement we are least
entitled to make about ourselves (`CLAUDE.md` rule 9).

**A second objection, which cuts the other way and we state anyway because it favours
us:** the `_stopped` block is not itself a frozen artifact of the pre-registration —
it is a *record of a decision this team made on 2026-08-31*, written after the
freeze at `7b93b2c8`, and `§26` has since ruled the ground of that decision removed
(`:3454-3464`). On that reading, moving the entry is updating a stale decision
record, not editing frozen evidence. **We do not assert that reading. We name it
because a reader who spotted it and thought we had hidden it would be right to
distrust everything else here.**

### The deadlock

**Cure A is barred by `(iv)`. Cure B is unruled, and is unruled precisely on the
axis where our interest lies.** `§26`'s grant does not say which artifacts the
transcription may write, and heat-transfer will not decide that for itself.

---

## 5. A THIRD OPTION, NAMED BY US AND ARGUED AGAINST BY US

**Option C: land P10 with the certifier's blindness merely DISCLOSED** — install the
entry, attach §3's measurements, and write in the record that the comparator does
not reach P10.

**heat-transfer argues this is wrong, and argues it against our own interest, because
Option C is the only one of the three that we could execute today without a ruling.**

1. **It is "evidence annotated as non-binding."** A printed discrepancy labelled
   *diagnostic only* is worse than one never computed: it converts a live defect into
   a documented feature and buys the appearance of candour at the price of the
   control. The disclosure would sit in a record; the silent `rc 0` would sit in
   every future run of the comparator, and it is the `rc 0` that gets read.
2. **`§24.4(c)`'s entire content forbids it.** Verbatim (`:3310`): *"A transcription
   checker not shown able to detect a mistranscription certifies nothing."* Option C
   proposes to land a case the checker has been **shown unable** to detect a
   mistranscription in — four times, in §3.2. That is not a weaker version of (c);
   it is (c)'s stated failure condition, met exactly.
3. **It repeats the dead lever one level up.** `§26.5` lifted the stop because
   `build_t20c.py` is fail-closed: the lever now moves something. Option C would
   register a case whose **checker** is connected to nothing — a dead limb in the
   comparator where there was a dead lever in the builder. `DEAD_LEVER_AUDIT.md` is
   named for that failure class; landing it in the file's own campaign would be a
   poor place to make an exception.

**We name Option C so that verification can rule on it now, rather than have it
arrive later as a convenience** — which is how this option would otherwise reach the
record: not argued, but done.

---

## 6. DISCLOSURE — WHOSE INTEREST THIS SERVES

**heat-transfer is the beneficiary of every reading that lets `T20_LC_P10` land.**

- **T20 is presently `NOT A RESULT` on its own registered terms.** `V5` at
  `T20_PREREGISTRATION.md:1062`, frozen at `7b93b2c8` and verified by me at the
  committed blob, makes a refusal on the planted arm a **whole-rung `NOT A RESULT`**.
  The planted arm cannot run without P10.
- **This route is the only path to a graded T20 at all.** `§26.8` says so in the
  grant itself (`:3484`): *"this route is the only thing that lets T20 reach a graded
  result… That is a legitimate motive and it is precisely why `(a)` exists."*
- **Therefore heat-transfer takes no reading and applies no cure.** Not A, not B, not
  C. Not the `_stopped`-is-not-frozen argument in §4 that favours us; not the
  join-the-existing-gap argument in §3.6 that favours us. We measured, we corrected
  our own prior record where it was tidier than the world (§3.4), and we hand the
  question over.

**The direction the answer wants is knowable in advance, which is the reason we are
not the ones to give it.**

---

## 7. COST (`CLAUDE.md` rule 12)

**Zero solver compute. `T20_LC_P10` HAS NOT RUN. No run is queued and none is
requested.**

| item | value |
|---|---|
| (iii) demonstration, this lane, **measured** | 2 builds, **0.514 wall s × 1 rank = 0.00857 core-min** |
| (iii) demonstration, prior lane (`1c8c5838`), measured | **0.0083 core-min** |
| USD, **DERIVED NOT MEASURED** | **$0.0000073** at the owner-stated **$0.0513/core-h** |
| condition (ii) re-measurement | JSON reads and comparator calls; **< 0.001 core-min**, not separately resolvable |
| solver core-minutes | **0** |

The rate is **REPORTED-BY-OWNER** (2026-08-21/22) and is not measured: the box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER` §5). The grant pre-estimated (iii) as
*"approximately zero core-minutes"* (`:3472`); actual sits in that order, and **no
actual/predicted ratio is fabricated against a non-numeric prediction.** No waste, no
contention, no overrun.

**Whatever is ruled, nothing about T20's costed envelope moves:** P10's registered
POINT stays **0.1584** core-min and CAP **1.80** core-min (`S11.2 :1017` at
`7b93b2c8`), inside the frozen rung TOTAL CAP **16.0 core-min (hard)** (`:1018`).
Any launch of P10 remains heat-transfer's own separate act under rule 2, rule 12 and
the strict completion rule — **not something this referral asks for or a ruling would
grant** (`§26.7`).

---

*Raised by the heat-transfer team, 2026-08-31. `T20_registered.json` was not written
(sha256 `e04c6a64c3920e3e…` unchanged). No frozen file was edited. No interlock was
lifted. No solver ran. Nothing was sent outside this box (`CLAUDE.md` rule 7).*
