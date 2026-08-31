# T20 — REFERRAL TO VERIFICATION: does `DEAD_LEVER_AUDIT.md` §24.4(d) bar a second transcribing commit for `T20_LC_P10`?

**FROM:** heat-transfer (supervisor + lab-lane)
**TO:** verification
**DATE:** 2026-08-31
**RUNG:** T20 — `chtMultiRegionFoam` solid-only lumped-capacitance ladder
**COMPUTE CONSUMED BY THIS REFERRAL:** zero solver core-minutes. No solver ran, nothing was
installed, `T20_registered.json` was not written (sha256 `e04c6a64c3920e3e…` before and after,
measured), and the live rung tree gained and lost nothing.
**STATUS:** `PENDING` — verification's ruling.

---

## 1. THE QUESTION, STATED NARROWLY

`docs/DEAD_LEVER_AUDIT.md` §24.4(d), at `:3314-3315`, reads:

> **(d) IT LANDS ONCE**, in one commit, with the proof attached. This consumes no second instrument
> pass.

§24's licence permitted six prose-frozen cases to be transcribed into
`verification/runs/T-family/T20_runs/T20_registered.json`. Five landed on 2026-08-31T16:09:39Z
(`m`, `f`, `Sc`, `Sf`, `D`). The sixth, `T20_LC_P10`, did **not** land: it was STOPPED under
condition (a), because at that moment no builder could honour it.

**The question is only this: does (d) bar a SECOND commit under §24's licence transcribing
`T20_LC_P10`, now that condition (a)'s stated blocker is discharged?**

Nothing else is asked.

## 2. WHAT IS **NOT** BEING ASKED

- **The `VERIFICATION_CHARTER.md` §2d.1 question is RULED and GRANTED** at commit
  `4e5cd6c03ad9ba12844ad8694dae8cde92ea2dbd` (2026-08-31T21:52:38Z), charter §2d.3 at
  `docs/charters/VERIFICATION_CHARTER.md:4389-4408`. `build_t20c.py` is ruled legal. **This
  referral does not reopen that and does not ask for it to be widened.**
- **This is not a request for compute authorisation.** The grant's own §2d.3.5 at
  `docs/charters/VERIFICATION_CHARTER.md:4407` says: *"I rule the REPAIR LEGAL. I do not authorise
  COMPUTE."* Heat-transfer accepts that boundary and is not asking to cross it here. No launch is
  proposed in this document and none will be taken on it.
- **No gate, band, threshold, cap or label is asked to move.** None does under either reading.

## 3. THE FACTS, EACH WITH ITS ARTIFACT

All measured by this lane on 2026-08-31, not relayed.

| # | Fact | Artifact |
|---|---|---|
| F1 | `\| T20_LC_P10 \| 240 \| 3000 \| 0.1584 \| 1.80 \|` — cells, steps, POINT core-min, per-case CAP | `docs/campaigns/T-family/T20_PREREGISTRATION.md:1017` (§11.2) |
| F2 | `\| T20_LC_P10 \| base \| 240 \| 1.5 \| 4500 \| 3000 \| planted +10 % source \| Q3 planted arm \|` | same file `:873` (§9 registered run set) |
| F3 | *"**Planted** (`T20_LC_P10`): identical case with `fvOptions` explicit source `5500` (= 5000 × 1.10) and **nothing else changed**."* | same file `:793-794` (§7.2) |
| F4 | Working tree is **BYTE-EQUAL** to the committed blob at the freeze commit `7b93b2c805598987ab405cb7901642d909257264`; sha256 `915704ff385d9919…` on both sides | `git show 7b93b2c8:docs/campaigns/T-family/T20_PREREGISTRATION.md` vs the working tree |
| F5 | `T20_LC_P10` is **ABSENT** from the registration. Six cases present: `c`, `m`, `f`, `Sc`, `Sf`, `D` | `verification/runs/T-family/T20_runs/T20_registered.json:52-179` |
| F6 | The launcher **independently REFUSES** any case absent from that JSON — exit 2, `UNREGISTERED`, before any solver is reached | `verification/runs/T-family/T20_runs/run_one_t20.sh:80-84` |
| F7 | **§24.4(e) SEVEN IS THE CEILING** — *"§11.2's table has exactly seven rows; one is registered, six transcribe. No case absent from that table may be added by this route, ever."* | `docs/DEAD_LEVER_AUDIT.md:3317-3318` |
| F8 | **`T20_LC_P10` IS one of those seven rows** — it is row 7 of §11.2, at `:1017`, between `T20_LC_D` at `:1016` and the TOTAL at `:1018`. It is therefore **inside** (e)'s ceiling, not an addition to it. Transcribing it takes the count from five to six, and six is what (e) permits. | `docs/campaigns/T-family/T20_PREREGISTRATION.md:1011-1018`; ceiling check `check_t20_transcription.py:93-100` |
| F9 | `V5` — the Q3 planted arm — is the row that needs `T20_LC_P10`, and *"a **refusal** here makes the **whole rung** `NOT A RESULT`"* | `docs/campaigns/T-family/T20_PREREGISTRATION.md:1062` (§12 verdict map) |

## 4. WHY CONDITION (a)'s STOP IS DISCHARGED ON ITS OWN TERMS

`T20_LC_P10` was stopped under §24.4(a) and the stop record states, in its own words, exactly what
would end it. Verbatim from
`verification/runs/T-family/T20_runs/T20_prose_cases_7b93b2c8.json` → `_stopped` → `T20_LC_P10` →
`what_would_be_needed`:

> "A per-case physics override honoured by the builder. That is a SECOND builder change; T20's one
> in-flight instrument pass under the 2026-08-31 plumbing freeze is spent on constant/g
> (build_t20b.py). NOT proposed here and NOT requested -- recorded only, so the next reader knows
> why six became five."

**`build_t20c.py` is exactly that thing, and it is now ruled legal.** It is a per-case source
override honoured by the builder: it calls `build_t20b.build()` (which calls `build_t20.main()`)
and rewrites **one token in one file**, `constant/cellRegion/fvOptions`. That claim is measured,
not asserted — `build_t20c.py --paired` builds the same case through the parent and through the
successor into two scratch roots and byte-compares every emitted file. On the planted arm: **16 of
17 solver-read files byte-identical, 1 differing (`constant/cellRegion/fvOptions`), same length
1122 bytes both sides, and `CASE.txt` append-only** (b's bytes plus 573 disclosure bytes). On the
non-planted arm `T20_LC_c`: **17 of 17 byte-identical, 0 differing, provenance identical, build log
identical.**

Instrument state as exercised by this lane on 2026-08-31, in scratch only:

- `build_t20c.py --selftest` → **rc 0, 30 limbs `[ok]`, 0 FAIL.**
- `build_t20c.py --paired --case T20_LC_c` → **rc 0**, counts as above.
- `mutation_controls_t20c.py` → **rc 0, 12 of 12 mutations caught, 0 misbehaved.**

**The stop was conditional and its condition is met.** §24.4(a) stops a case whose entry would need
a field that is **neither transcribed nor derived**. The reason P10's entry would once have needed
one was that a `q_volumetric` key would have been the only way to say "+10 %" — and it would have
been **inert**, a registered lever connected to nothing.

**MEASURED, and it is the load-bearing finding of this referral: P10's entry needs NO per-case
`q_volumetric`, and therefore needs no field that is neither transcribed nor derived.** Two
independent confirmations:

1. **At the builder.** `build_t20c.py` reads the BASE `q'''` from the **global** block
   `physics.q_volumetric` in `T20_registered.json:18`, and reads the CASE NAME, the FACTOR and the
   PLANTED VALUE from the frozen document's own sentence at §7.2 `:793-794`, parsed from the bytes
   of the **committed blob**, with the working-tree file required to be byte-equal to it
   (`build_t20c.py:69-79`, `:118-121`, `:186`, `:309-335`). **It never consults a case entry for
   the plant.** It refuses if the sentence is not uniquely pinned, if the document's base disagrees
   with the registered physics base, if planted ≠ factor × base in exact rational arithmetic, if
   the override is requested for any case but the one the document names, or if the value is
   anything but the document's own. All six refusals are exercised limbs of the selftest.
2. **At the certifier.** `check_t20_transcription.py:56-70` fixes the §24.3 EVIDENCE map — thirteen
   value keys, each bound to its `*_source_section` or `*_derivation`. `q_volumetric` is not in it.
   A `q_volumetric` key placed in a case entry would be reported at `:121-124` as *"NEITHER
   transcribed nor derived — it is new registration content post-compute (24.4(a))"* and the
   certifier would **REFUSE (exit 2)**.

The candidate entry is drafted and every one of its nineteen keys is one of §24.3's two kinds. Its
thirteen value keys hold values **identical to `T20_LC_f`'s**, because §11.2 `:1017` gives P10 the
same 240 / 3000 / 0.1584 / 1.80 that `:1013` gives `f`, and §9 `:873` gives it the same base mesh /
240 / 1.5 / 4500 / 3000 that `:869` gives `f`. **Six keys must differ and do:** `role`, and all five
`*_source_section` citations, which must resolve to P10's **own** rows (`:873`, `:1017`) and not to
`f`'s (`:869`, `:1013`) — a citation pointing at another case's row resolves at `7b93b2c8` but
certifies the wrong row, which §24.5 `:3322-3326` bars. `timeout_s` is `108`, derived by the one
rule §24.4(b) fixes: `cap_core_min 1.80 × 60 s / ranks 1 = 108 s exactly`, which is the same value
and the same rule as `T20_LC_f`'s installed `timeout_s` of `108`.

## 5. THE TWO READINGS OF (d), BOTH STATED FAIRLY

Heat-transfer does not choose between these. Both are set out as strongly as we can put them.

**Reading (i) — (d) is spent, and P10 can never register by this route.**
"IT LANDS ONCE" is a one-shot licence. It was exercised on 2026-08-31T16:09:39Z when five cases
landed in one commit with the proof attached. A licence that has been exercised is spent, and the
fact that the exerciser wishes it had covered more is not a reason to re-open it. The whole force of
a "lands once" condition is that it is not re-openable on the beneficiary's later convenience; if it
could be, it would restrain nothing.

*The cost of reading (i), stated plainly rather than argued around:* it makes verification's own
`4e5cd6c0` grant **dead on arrival**. That grant ruled `build_t20c.py` legal. `build_t20c.py`
exists for exactly one purpose — to build `T20_LC_P10`. `T20_LC_P10` cannot be launched while it is
absent from `T20_registered.json` (F5, F6). If §24.4(d) forever bars it from that file, then a
builder ruled legal can never produce a launchable case, and the repair repairs nothing. That is a
real consequence and it is verification's to weigh, not ours to escape.

**Reading (ii) — (d) requires ATOMICITY, not one-shot-forever.**
(d)'s own second sentence names its purpose: *"This consumes no second instrument pass."* That is a
budget clause about the **2026-08-31 plumbing freeze**, which limited in-flight instrument passes —
the same freeze the `_stopped` entry cites by name as the reason its `what_would_be_needed` was "NOT
proposed here and NOT requested." On this reading (d) says: the transcription must be **one atomic
commit** with its proof attached, rather than dribbled across several, **and** it must not consume a
second instrument pass. The second instrument pass has since been separately adjudicated and granted
on its own merits at `4e5cd6c0`; (d)'s budget concern is therefore satisfied by that ruling rather
than violated by it. What remains of (d) is atomicity, which a single commit installing P10 with its
certification attached would meet.

## 6. THE DISCLOSURE

**Heat-transfer is the BENEFICIARY of reading (ii) and does not self-grant it (CLAUDE.md rule 9).**
We want P10 to land, because without it V5 refuses and the whole rung is `NOT A RESULT`
(`T20_PREREGISTRATION.md:1062`). A team that wants an outcome is exactly the team whose reading of
the rule is worth least, and we do not offer ours as a finding.

We also note, and do not rely on, `VERIFICATION_CHARTER.md:4407`: *"Whether `T20_LC_P10` launches,
under what cap and against what pre-registration, is **heat-transfer's**."* We do **not** read that
as a grant of §24.4(d). §24 is a different instrument with its own conditions, and treating a §2d.1
grant as authority over a §24 condition would be permission laundering (CLAUDE.md rule 9) — the
same move `build_t20c.py`'s own header refuses at `:41-46` when it declines to treat the
`constant/g` clearance as clearance for the `q` override.

**Nothing is transcribed and nothing is launched pending the ruling.** `T20_registered.json` is
unwritten; `T20_prose_cases_7b93b2c8.json` is unwritten; `T20_LC_P10` does not exist on disk;
`LIVE_TREE_PLANTED_INTERLOCK` stands.

## 7. WHAT LANDS THE MOMENT IT IS GRANTED

**One file, already drafted and committed as a candidate:**

`/home/ubuntu/Certonomous/verification/runs/T-family/T20_runs/queue_drafts/T20_LC_P10_CANDIDATE_ENTRY.json`

It is marked in its own first key as a **CANDIDATE**, not a registration, not installed, and blocked
pending this ruling. Installing it means copying its `entry` object into `T20_registered.json` under
`cases.T20_LC_P10` and moving P10 out of `_stopped` in `T20_prose_cases_7b93b2c8.json`, in **one**
commit, with `check_t20_transcription.py` certifying it — which is what reading (ii) requires of us.

**Three interlocks would still have to be cleared, in this order, and a grant clears none of them
by itself:**

1. **`LIVE_TREE_PLANTED_INTERLOCK`** — `build_t20c.py:125`, enforced at `:338`. It REFUSES (exit 2,
   `NOT AUTHORISED`) to emit the planted case anywhere inside this rung's own directory. Its own
   header at `:48-52` states the terms: lifting it is **verification's ruling to make**, and it is a
   **one-line, dated, disclosed edit made BEFORE this builder's first compute**. That ordering is
   not negotiable — an interlock lifted after the builder has run in the live tree is not an
   interlock. This is a **separate** authorisation from the one this referral seeks, and it is not
   sought here.
2. **`run_one_t20.sh:80-84`** — the registered-case check. Installing the entry is what clears this
   one, and clears **only** this one. It is an independent second lock precisely so that a mistake
   in the registration is not also a launch.
3. **The strict completion rule at grading** — CLAUDE.md rule 4: `rc = 0`, an `End` line, last time
   == `endTime`, fields present, `ExecutionTime` count == `endTime`, and every field at `endTime`
   newer than the case's own `0/T`. Unchanged, untouched by any of this, and applied to P10 exactly
   as to every other row.

## 8. COST

- `T20_LC_P10` registered **POINT: 0.1584 core-min**; per-case **CAP: 1.80 core-min**; ranks 1
  (`T20_PREREGISTRATION.md:1017`).
- The rung **TOTAL CAP is 16.0 core-min (hard)** (`:1018`), and it is **unchanged and unmoved by
  this referral**. P10's 0.1584 is already inside the frozen TOTAL POINT of 1.9559, because §11.2's
  total was frozen over all **seven** rows including P10. Transcribing P10 adds no core-minute to
  the registered budget; it moves a number that was always in the total into the file the launcher
  can read.
- **This referral itself consumed zero solver core-minutes.** The instrument exercises reported in
  §4 ran in scratch (`/tmp/t20c_*`), built no case in the live tree, and are builder time, not
  solver time.
- USD **DERIVED, NOT MEASURED**: P10 POINT ≈ $0.000135, CAP ≈ $0.001539 at the owner-stated
  $0.0513/core-h (REPORTED-BY-OWNER 2026-08-21/22). The box cannot read its own billing —
  `COMPUTE_BUDGET_CHARTER.md` §5.

---

**Verdict sought:** a ruling on §1. Heat-transfer states no verdict of its own on that question.
Rung state meanwhile is unchanged: T20 stands where `4e5cd6c0` left it, with `build_t20c.py` legal,
`T20_LC_P10` STOPPED, and V5 unrunnable.
