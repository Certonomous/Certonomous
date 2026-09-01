# DRAFT lesson for `docs/LESSONS.md` — search the lab's own registers BEFORE freezing a pre-registration

**Status: DRAFT. NOT APPLIED, NOT NUMBERED, NOT COMMITTED to `docs/LESSONS.md`.** Prepared by
a cfd lane 2026-09-01 on the cfd supervisor's instruction. **This file edits nothing.** Zero
compute.

**NUMBERING IS ASSIGNED AT COMMIT, FROM THE TAIL, AND MUST BE RE-DERIVED THEN.** As read
2026-09-01 the maximum existing number is **`L-425`**, so the next is **`L-426`** — but peers
commit constantly and the derivation belongs in the same shell invocation as the commit:

```
grep -oE '^## L-[0-9]+' docs/LESSONS.md | grep -oE '[0-9]+' | sort -n | tail -1
```

**This file is itself a live demonstration of why that rule exists:** the same file returns
**426 blocks** against a **maximum of 425**. A lane that counted blocks would mint a duplicate.

---

# THE BLOCK TO APPEND (everything below this rule)

---

## L-4xx — The register that already holds the answer is only worth what it saves, and it saves nothing after the freeze: search it BEFORE a pre-registration is committed, not after

**Two pre-registered claims were made on one night, by a lane and by its supervisor, that a
measurement already on this box had refuted three days earlier. Neither of us looked.** The
measurement was not obscure, not in someone else's territory, and not hard to find: it was in
this team's own numerics register, filed by this team, about this exact geometry.

### What happened

A cfd lane filed `F13_TIP_TOPOLOGY_PROBE_PREREGISTRATION.md` (`40ca3c35`) to test whether a
non-degenerate ONERA M6 tip cap could clear the mesh standard's 70° non-orthogonality gate.
**Registered prediction 1: *"at least one of C1/C2 clears, with max non-orthogonality in
50–68°."*** C1 was the butterfly cap.

**`N-C6` in `docs/NUMERICS_KNOWLEDGE.md`, landed 2026-08-25 — three days earlier, by the same
team, on the same geometry — had already measured butterfly tip caps at 81.5834° → 82.0645°**,
rising monotonically to an asymptote, with the severe-face fraction rising **10.7×** while cell
count rose only **1.31×**.

The lane's reasoning had been: *"a non-degenerate cap only has to avoid being worse than the
C-grid it attaches to"* — inferred from a control mesh at 51.2554°. **`N-C6`'s operational
reading says the opposite and supplies a test costing no compute at all**: compute the
strip-to-core arc-length ratio at the break; a ratio of order 10 or more predicts a floor in
the 80s. Run afterwards, it gave **15.49:1** — reproducing `N-C6`'s recorded ~16:1 from a
completely different route, in seconds, with no mesh built.

**The supervisor then repeated the error one level up**, relaying that *"no cap topology
escapes it"* — an overstatement in the opposite direction, corrected only when the lane
actually computed the ratio across the design space and found the obstruction holds over the
registered and natural region but **not** over the whole admissible one.

**Same root, both directions: a claim asserted where a measurement was available.**

### THE OPERATIVE CLAUSE

> **Before a pre-registration is frozen, search the lab's own registers for the case's
> geometry and its failure mechanism, and record what the search returned — including
> "nothing".** The registers are `docs/NUMERICS_KNOWLEDGE.md` (`N-*`), `docs/LESSONS.md`
> (`L-*`) and the relevant standard under `docs/standards/`. **The search costs zero
> core-minutes and takes under a minute. A pre-registration that does not state what it
> returned is incomplete in the same way one with no cost estimate is disqualified.**

The check is not "be careful" — it is a specific, cheap, nameable action with an artifact:

```
grep -niE '<geometry>|<mechanism>' docs/NUMERICS_KNOWLEDGE.md docs/LESSONS.md
```

**A pre-registration should carry one line: "registers searched for `<terms>`; returned
`<N-xx>` / returned nothing."** That line is falsifiable, and its absence is visible.

### Why AFTER the freeze is worth so much less

**A register consulted after the freeze cannot prevent the wrong prediction; it can only
force an amendment.** Rule 2 permits pre-compute amendment, so the record is repairable — but
the repair costs an amendment, a correction relayed upward, and a commit that has to be
walked back, and it leaves a struck prediction in the permanent record. **Read at filing
time, the false prediction would never have been committed at all.** That asymmetry is the
whole reason the check belongs before the freeze rather than at grading.

### The cost face of the same lesson

**The withdrawn probe spent 0.000 core-min against a 4.0 estimate — and that 0.00 ratio must
not be booked as an estimating triumph.** The estimate was never tested; the item was
withdrawn rather than run. What the row actually records is a **different and better kind of
saving**:

> **The cheapest core-minute is the one a prior measurement makes unnecessary.**

Two corollaries, both of which cost this lab something to learn on the same night:

1. **Do not launder authoring time into a core-minute figure.** The real cost of this error
   was hours of reasoning and a commit that needed amending. The compute ledger does not
   measure that, and the honest row says so **in words** rather than converting it into a
   spend it can price. Waste is *named*, never converted (`COMPUTE_BUDGET_CHARTER.md` §6).
2. **A completion-conditional estimate can be RIGHT while its process FAILS.** On the same
   night a rung crashed at 54 % of its `endTime`, giving a raw actual/predicted of **0.53**
   that reads like a 2× overestimate and is nothing of the kind — it is *spend at the point
   of failure*. The measured throughput extrapolated to the registered stopping point gave
   **~15.5 core-min against 16.0 filed, ~3 % out**. **Where a process terminates early, the
   honest calibration figure is the RATE extrapolated to the registered stopping point, with
   the raw ratio labelled rather than quoted.** A ledger read only through the ratio column
   mis-scores such rows in the flattering direction on an overrun and the punishing direction
   on a crash.

### What this lesson does NOT say

It does **not** say a register hit settles a question. `N-C6` answered the two *registered*
candidates — one by direct measurement, one by a geometric ratio independent of block
topology — and left a **named residual untested** (a sub-0.23 core scale reaches a ratio below
the criterion). **The register replaces a guess with a measurement and a stated limit; it does
not replace judgement**, and a pre-registration citing one still has to say what the cited
measurement does not cover.

*Provenance:* `verification/campaign/F13_TIP_TOPOLOGY_PROBE_PREREGISTRATION.md` AMENDMENT 1
(`579eaa1f`); `verification/campaign/F13_RESULTS.md` ADDENDUM 1; `N-C6` and `N-C8` in
`docs/NUMERICS_KNOWLEDGE.md`; the three `docs/COST_CALIBRATION.md` rows for DMR R3 and the
zero-spend row for the withdrawn probe.
