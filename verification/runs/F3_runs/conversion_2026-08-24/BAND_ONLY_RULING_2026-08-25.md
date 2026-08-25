# BAND-ONLY ROWS — MY RULING, AND I RESOLVE AN INCONSISTENCY THAT WAS MINE

**Ruled by the cfd supervisor personally, 2026-08-25.** `[lab-attributed]` under Sanaa's
desk-item disposal rule of this date; **overrulable**.

Evidence: `BAND_ONLY_ROW_FINDING.md` (commit `a60a8489`), which I accept in full and
have not asked a second lane to re-derive.

---

## 1. FIRST, THE INCONSISTENCY WAS MINE AND THE LANE WAS RIGHT TO STOP

I wrote the task with **two different gates**: Part 2 was gated on whether a band-only
row is **CITABLE**; my STOP condition was worded on whether it can become a
**CREDENTIAL**. **Those are different questions and here they give opposite answers.**
The lane found the disagreement, refused to resolve it in the direction that spends
compute, took the conservative limb and handed it back.

**That is exactly right and I am recording it as right.** A lane that resolves its
supervisor's ambiguity in favour of action is a lane that spends budget on a question
nobody actually settled. **The ambiguity was a defect in my instruction, not in its
execution.**

## 2. THE FINDING, ACCEPTED

**CITABLE — YES.** `grade_f3.py` (blob `6fea2e1d`) `:407-412` returns the band verdict
when `triple is None`. It does not refuse, does not exit 2, does not return
`NOT A RESULT`. `triple=None` is passed **deliberately**, from a per-pair `has_triple`
flag. **Standing rule 5 clause 2 is a test performed ON a triple; an absent triple has
nothing to turn.** Executed precedent is already on disk and was not hypothetical:
`wedge/M3.0_th15/fine` produced G-F3-1 `PASS` (+0.00733 %, band ±0.5 %) and G-F3-2
`PASS` (−0.9593 %, band ±2.0 %), both `triple: null`, both counted in the published
five-PASS tally.

**CREDENTIAL — NO.** F3 §9 `:399-400` keys credential status on *"PASS on a gate whose
triple CONVERGES"*, and §9's preamble fixes its meanings *"so no outcome can be re-read
afterwards"*. Credential status is a **label**, inside rule 2's frozen quartet, after
first compute.

**Correctly scoped by the lane and I repeat the scoping rather than quietly dropping
it: this restriction is F3's OWN §9. It is not lab-wide doctrine, and no charter
supplies the grant.** The finding establishes the F3 position only.

## 3. RULING (a) — I DECLINE TO WIDEN IT, AND ON THE MERITS, NOT MERELY ON PROCEDURE

The lane referred four options for granting band-only rows credential status in a
successor's own §9, and correctly said a label decision is above a lane. **I am not
referring it upward as an open question, because I am ruling against the widening, and
refusing to widen is always within my authority.**

> **No cfd successor registration will grant credential status to a single-mesh,
> band-only row. Not F3's successor, not any other.**

**The reason is substantive.** A band-only row has **no discretization-error estimate at
all** — no triple, no observed order, no GCI. What it establishes is that *this mesh*
produced a value inside a band. It cannot distinguish a converged answer from a value
that happens to land inside the band while the discretization error is larger than the
band itself. **A credential asserting more than that would be asserting something the
evidence does not contain, and it would degrade every credential beside it in the same
column.** F3's §9 got this right and a successor of mine will inherit it deliberately,
not merely by carry-over.

## 4. RULING (b) — THE SUCCESSOR **PROCEEDS**. My Part 2 gate was citability and it is MET.

Resolving my own inconsistency in the direction I actually specified: **Part 2's gate
was citability. Citability is established. The successor is authorised**, on four
conditions, and the first is not negotiable.

1. **EVERY ROW CARRIES ITS LIMIT ON ITS OWN FACE.** Each row prints
   **"band only — no grid triple — no discretization-error estimate — NOT a
   credential"** beside its verdict, in the results record and in any tally. **A row
   whose limitation is stated only in a companion document is a row that will be cited
   without it.** This lab has already ruled that evidence annotated as non-binding in
   the wrong place is worse than evidence never computed.
2. **The frozen bands carry over UNCHANGED and nothing is re-derived** — ±0.5 %, ±2.0 %,
   ±1.0 %, §3.1 reference values verbatim at full double precision. §9 carries over too,
   deliberately, per ruling (a).
3. **F3's tally, rows and verdicts are not altered**, and F3's three rows stay `BLOCKED`
   as a launch request and `PENDING` as graded cells.
4. **Costed, capped and committed before compute**, using F3's measured 1.1290 ratio
   rather than a guessed margin.

**Why proceeding is right at this price.** Three graded rows against **exact analytic**
references, at roughly **6.4 core-min — about $0.0055 DERIVED, never measured.** Sanaa's
binding rebalance measures this lab in gates fired and cases run, and declining a
three-row gate at half a cent because the rows are honest about their own limits would
be the wrong lesson to draw from an honest finding. **The finding does not say the rows
are worthless. It says precisely what they are worth, which is the useful outcome.**

## 5. THE INFERENCE THE LANE CAUGHT AGAINST ITSELF — carried forward, because it will recur

AMENDMENT 1's *"a single fine cone M3.0 run converts nothing"* **does not transfer** to
the wedge and diamond M2.5 pairs. It holds for the cone because that pair's §1 defect
**is** refinement-absence. The 2026-07-28 record shows wedge M2.5 already had medium and
fine, and diamond M2.5 had coarse, medium and fine. **Their §1 defect is the missing
pre-registration alone, which a fine run under a frozen band DOES cure — and they would
still not yield a §9 credential, because §9 keys on the TRIPLE, not on the defect.**

**The general shape, and it is the reusable part: §1's defect axis and §9's credential
axis come apart.** Curing why a row was inadmissible is not the same as making it a
credential, and a reader who conflates them will over-claim in one direction and
under-run in the other.

## 6. WHAT THE BAND-ONLY WAVES HAVE ACTUALLY BEEN BUYING

**184.83 of F3's 2,005.06 launched core-seconds — 9.2 % — went to the one band-only run
that fitted the cap, and bought two PASS rows that count in the tally and are not
credentials.** **Verdict breadth, not credential breadth.** That is a fair trade at that
price, and it is the first time this team has been able to say which of the two it was
buying.

## 7. ESCALATED, BECAUSE IT IS CROSS-FAMILY AND NOT MINE TO SWEEP

The lane could not establish **whether any OTHER campaign leans on band-only rows as
credentials**, and said so rather than guessing. **That sweep is cross-family and goes to
the chief and to verification, not to cfd.** If another family's credential column
contains single-mesh rows, that is a matrix-cell question of exactly the kind Sanaa now
measures in, and it is bigger than F3.

## 8. THE §8 DOCUMENTATION GAP — a dated addendum is owed, and its scope is narrow

§8 lists `grade_f3.py` at sha256 `fe9fe6df…`; the grader that ran is `e7602996…` (blob
`6fea2e1d`), repaired by AMENDMENT 2 under §2d.1.

**The grade IS defensible and I am not letting this be reported as a freeze breach.**
§8's operative mechanism is a **blob check against the commit passed as
`--prereg-commit`**, and both the graded JSON (`prereg_commit 48b7812a`,
`frozen_match true`) and `RESULTS.md` disclose the re-freeze **on their face**.

**What is genuinely missing is a pointer, and only that.** AMENDMENT 2 records no
post-repair sha256, so a reader hashing against §8's literal value finds a mismatch with
nothing in the document telling them where to look — and AMENDMENT 1 `:557` asserts the
§8 pair stands as frozen, **which the repair overtakes**. A dated post-compute addendum
records the post-repair sha256 and supersedes that sentence. **It alters no gate, no
threshold, no cap and no label, and it regrades nothing.** A record that makes a
defensible grade *look* undefendable to the next reader is a records defect worth half
an hour, and no more than that.
