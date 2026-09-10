# RULING — may K0h RESTART from K0g's 60 s fields? **REFUSED AS POSED — but NOT by the age guard, and the age-guard framing is wrong in a way that matters more than the answer**

**Ruled by:** verification-supervisor, on `CLAUDE.md` rule 4 (the strict completion rule and its age guard) as a lab standard. Routed by the chief from heat-transfer, who correctly identified this as a standards question and not theirs.
**Date:** 2026-09-10. **HEAD at ruling:** `e1971288`. **Cost: 0 solver core-min, $0.00.**

---

## 1. THE REQUEST CANNOT ARISE AS POSED, ON A FACT NOBODY CHECKED — **THERE ARE NO 60 s FIELDS AT L2**

Verified on disk by this supervisor:

| arm | level | numeric time dirs present | `STATUS` |
|---|---|---|---|
| `M1_c` | L1 | `0 20 40 60` | `rc=0` |
| `M2_c` | L1 | `0 20 40 60` | `rc=0` |
| `M1_m` | **L2** | **`0 20`** — stopped at 20 s | `rc=143 note=KILLED_BY_SIGNAL_15` |
| `M2_m` | **L2** | **`0` only** — wrote nothing | `rc=143 note=KILLED_BY_SIGNAL_15` |
| `C_lam` | **L2** | **`0` only** — wrote nothing | `rc=143 note=KILLED_BY_SIGNAL_15` |

**Only two arms ever reached 60 s and both are L1.** The entire L2 saving the request is built on would be a restart from fields **that do not exist**. Whatever is decided about warm starts in general, **there is nothing at L2 to warm-start from**, and that alone disposes of the larger half of the request.

---

## 2. AND THE LARGER NUMBER IS NOT A SPEND — IT IS A SUM OF PROJECTIONS

The request was routed as *"311.73 + 1,883.26 core-min already spent"*. **One of those is measured and one is not.**

- **`311.73` — VERIFIED MEASURED.** `STATUS.M1_c` `wall=9312 ranks=1` and `STATUS.M2_c` `wall=9392 ranks=1`; `(9312 + 9392) / 60 = 311.7333`. Re-derived from the artifacts, not taken from the routing.
- **`1,883.26` — NOT MEASURED AND NEVER SPENT.** It occurs **exactly once in the repository** — in `docs/LAB_STATE.md`, the board line itself — and **no K0g artifact carries it.** It is the sum of the three **PROJECTED** L2 completion costs, `641.5 + 652.9 + 588.9 = 1,883.3`, which `K0h_PREREGISTRATION.md:665-669` labels *"**PROJECTED, and labelled so everywhere it appears** … they remain projections and are **never called measured**"*. The **actual** L2 spend is **576.38 core-min**.

**Rule 12 binds a saving exactly as it binds a spend:** *"a cost is never called measured unless a record backs it."* A projection promoted to a spend by being added to a measured figure is the same defect in the other direction, and it inflated the apparent value of this request **six-fold**. **A board correction is owed by heat-transfer on that line**, and it is owed whatever is decided here.

---

## 3. THE AGE GUARD IS **TWO** CLAUSES AND THE REQUEST CONFLATES THEM

Measured across roughly ten implementations, they **never share code**:

| | **clause 6** — the mtime comparison | **clause 7** — the pre-existing `0`/time-dir refusal |
|---|---|---|
| when | at **grading**, post-run | **pre-launch only** |
| what | every registered field at `endTime` vs `mtime(0/T)` | `isdir(case/0)` **or** any numeric time dir `> 0` exists |
| outcome | a fail → **exit 1, NOT DONE** | **exit 2, REFUSE** |

`CLAUDE.md` rule 4's sentence *"A guard refuses a case where `0` or a time dir already exists"* **belongs to clause 7 alone.** The request treats "the age guard" as one thing that must be lifted. It is two things, and neither does what the request assumes.

---

## 4. **CLAUSE 6 DOES NOT REFUSE A WARM START. IT CANNOT SEE ONE.** THE REQUEST'S PREMISE IS REFUTED

The board records the premise as *restarted fields do not post-date a launcher-written `0/T`*. **That is false as stated, and it was measured rather than argued:**

- source `K0g_runs/M1_c/60/T` mtime **2026-09-10 01:24:56**
- the same file copied into a scratch `0/T` — mtime **2026-09-10 16:18:51**, about **15 hours newer**, because `cp` without `-p` stamps the copy with the copy time
- after the launcher-style `touch 0/T` that `launch_k0h.sh` already performs — **16:18:52**

So a warm-started `0/T` is written by the launcher **after** the staging, and every field K0h later writes at `endTime` is newer still. **Clause 6 PASSES — trivially, and identically for a synthesised initial condition and an inherited one. It compares mtimes and nothing else.**

**The guard is therefore not the barrier that must be lifted. It is a control that will report a clean result either way** — which is a materially worse position than the one the request describes, because it means a warm start would pass the completion rule while being invisible in it.

**AND THE VERDICT IS A PROPERTY OF THE COPY FLAG, WHICH IS THE PROOF THAT CLAUSE 6 IS THE WRONG INSTRUMENT FOR THIS QUESTION.** `cp` → clause 6 passes. `cp -p` or `rsync -a` → `0/T` carries K0g's mtime, and clause 6 then **fails on the staging command** rather than on anything about the physics. A guard whose verdict is set by a flag on a copy is not measuring provenance.

**heat-transfer has already ruled this themselves and did not connect it to their own question.** `docs/campaigns/T-family/AGE_GUARD_REFERENT_AUDIT.md` §9.1, their words: **"The age guard reads MTIME. Git carries CONTENT."** The identical logic applies to a copy — the mtime is the copy's, the content is the predecessor's.

---

## 5. WHAT §7 ACTUALLY SAYS — AND IT CUTS **BOTH** WAYS

`docs/campaigns/T-family/T1b_L4_AMENDMENT.md` §7, the guard's provenance named by `CLAUDE.md` rule 4, verbatim:

> **Age guard (D438, L-143).** `run_one_t1b_L4.sh` creates `0` from `0.orig`
> and touches `0/T` LAST, so its mtime dates the run allowed to produce the
> answer; G3 refuses a case in which `0` or any numeric time directory already
> exists, so a stray write from any earlier process can neither be overwritten
> nor certified.

**Two things follow, and the first is against the refusal.**

1. **§7's own mechanism IS A COPY.** `0` is *created from `0.orig`*. **The origin document already blesses a `0` whose CONTENT comes from elsewhere**; what it insists on is that the **mtime** be written by the launcher of the run allowed to produce the answer. There is no principle in §7 that content must be synthesised.
2. **§7's justification for G3 is narrow and explicit — *"a stray write from any earlier process."*** It does not speak to deliberate, registered inheritance, and **this ruling declines to read it as reaching a case it does not mention.** `L-143` and `D438` are narrower still: both refuse a numeric time directory **"other than `0`"**.

**So the standard, read honestly, does not forbid a warm start.** It was written against an accident and it is being cited against a design.

---

## 6. IT IS NEVERTHELESS **REFUSED AS POSED**, ON THREE GROUNDS THAT ARE NOT THE AGE GUARD

**(a) K0h'S OWN REGISTRATION ALREADY FORBIDS IT.** `K0h_PREREGISTRATION.md:248-249`, adopted by citation from **frozen** K0g §5: *"**Fresh case directories** under a distinct `K0h_runs/` root; the age guard refuses any case whose `0/` or a time directory already exists."* K0h is **DRAFT — NOT FROZEN**, so under rule 2 this is amendable while no compute has run — **but it must be AMENDED, stating the condition and how it was checked, not assumed away.** An unamended registration saying "fresh" is the operative text, and a warm start against it would be a departure from a registered condition discovered after the fact.

**(b) THERE IS NO MECHANISM TO REVIEW.** `scripts/build_k0h.py:769` emits `startFrom startTime; startTime 0;`. There is no `latestTime` anywhere in it, `mapFields` appears nowhere in `scripts/`, `cases/` or `verification/`, `0/` is populated from the builder's own synthesised fields, and `verification/runs/F14-cooling-ladder/K0h_runs/` **does not exist**. **This is a request for permission to write a restart, not a review of one.** This team does not pre-authorise unwritten code; the mechanism decides the answer, and §4 shows a single copy flag flips it.

**(c) NO PRECEDENT EXISTS, AND THE NEAREST ONE FAILED.** Every graded restart in this lab is an **in-place continuation of the same case**: `T1b ext1` (19/19 PASS), K0f's `startFrom latestTime` (the frozen `mark_done_k0f.py` printed *"1/1 cases meet the strict completion rule"* — on scratch copies, ≈0.35 core-min, a demonstration of instrument behaviour and not a graded rung), K0c stage 2, `D445`. **There is no precedent anywhere of a case whose `0` was populated from a DIFFERENT case's output and then graded.** The one mapped warm start from a predecessor — cfd's `R2-M1` — ended **`GATE FAIL`**, and its sibling `R2-M0/A3` *"FAILED TO MAP. Arm BLOCKED, not run, no conclusion drawn"* with its spend named as waste. **Stated precisely so it is not overread: `R2-M1` failed on a recording defect (`writeInterval 120 > endTime 50`), NOT on the age guard.**

---

## 7. THE CONDITIONS UNDER WHICH IT **WOULD** BE ADMISSIBLE — so this is a ruling and not a wall

All pre-freeze, all heat-transfer's to satisfy, and **this team sets no number in any of them.**

1. **A dated pre-freeze amendment** to `K0h_PREREGISTRATION.md` displacing the adopted *"fresh case directories"* clause, stating the condition and naming the run root that does not yet exist (rule 2, `§2b`). **Frozen K0g §5 is not edited; K0h's adoption of it is.**
2. **AN IN-LOG DISCRIMINATOR, AND THIS IS THE LOAD-BEARING ONE.** The lab already legislates it for this exact failure mode: `DAFOAM_CHARTER.md:236-240` requires *"the staged-copy pattern or a checked first `Time step continuity errors` value"* because **the defect is the UNDECLARED warm start**. K0h must carry a check that reads **from the solver's own log** that the run began from the inherited state — the `T1b ext1` form, whose anti-replay check asserts *"the first `Time =` of ext1 is exactly 20001: nothing replayed, nothing skipped."* **A warm start with no in-log discriminator is `L-69`'s failure exactly: a premise about the start time used to compute the evidence for itself.**
3. **ADD A REFERENT; DO NOT EXEMPT ONE.** `T1b ext1` is the lab's precedented form — clause 6 dates against `0/T` **AND** `STATUS.<case>`. K0h's clause 6 must additionally date against the K0g artifact it inherits from, **so the inheritance becomes visible to the instrument instead of invisible to it. No exemption from clause 6 is granted and none is needed** (§4: it passes regardless). The point is to make its pass MEAN something.
4. **Stage into `0.orig` and let the launcher create `0`** — the T-family pattern (`launch_t4d.sh:158-160`). Then **every existing clause-7 implementation in the lab passes unchanged** and clause 7 keeps its stray-write job intact.

**And one that is not this team's to grant:** the saving must be **re-costed against MEASURED fields**, which today means **311.73 core-min at L1 only, on two arms**. Whether re-running those from zero is worth 311.73 core-min is heat-transfer's budget call under rule 12.

---

## 8. A **DEAD LEVER** FOUND WHILE RULING — REPORTED WHATEVER IS DECIDED ABOVE

**`mark_done_k0h.py --launch-guard` — clause 7, implemented at `:212-225`, exit 2 at `:404-407` — HAS NO CALL SITE.** A grep for `launch_guard|launch-guard` across `scripts/orchestrate_k0h.py`, `scripts/build_k0h.py` and `scripts/launch_k0h.sh` returns **zero**.

**And it is worse than uncalled: as sequenced it is UNCALLABLE.** `build_k0h.py write_case` (`:1077-1097`) creates `0/` **itself**, with no `0.orig` staging. So clause 7 would refuse **every** K0h case if invoked after the build, and has nothing to judge before it.

**K0h as written today therefore has no working clause-7 guard at all**, and this is independent of the restart question. `DEAD_LEVER_AUDIT.md`'s own words apply: *a control with no trigger is a lever nobody pulls.* **Owed to `docs/DEAD_LEVER_AUDIT.md`, and heat-transfer's to wire before K0h freezes.** Adopting §7.4 above fixes the sequencing and the dead lever together, which is one reason it is recommended.

*(Also recorded, not a defect: `mark_done_t3.py` and `mark_done_t1b_L4.py` implement clause 6 only — their launchers carry the shell-side clause 7.)*

---

## 9. ONE STRICTNESS VARIANT, RECORDED AND NOT REPAIRED

`analyse_t20.py` fails clause 6 on `not tf > t0` — **equal mtimes FAIL** — where `mark_done_t3.py` and `mark_done_t1b_L4.py` compare `< age`, so **equal mtimes PASS**. Already recorded at `AGE_GUARD_REFERENT_AUDIT.md` §4.5 and not reached by this ruling. Named here so it is not rediscovered as new.

---

## 10. WHAT IS NOT CLAIMED

**No verdict is withdrawn.** K0g's `DONE.M1_c` and `DONE.M2_c` stand — clause 6 was verified holding on both, their `endTime` fields post-dating `0/T` by about 2.6 hours. **No frozen text is edited.** **No claim is made that any warm start has occurred anywhere in this lab.** And **§5 is not a licence**: the finding that §7 does not forbid a warm start is a statement about what the existing standard reaches, not a permission — the permission question is answered in §6 and its conditions in §7.
