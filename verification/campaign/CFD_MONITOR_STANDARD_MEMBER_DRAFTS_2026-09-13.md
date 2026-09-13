# MONITOR_STANDARD MEMBER DRAFTS FROM THE cfd RENDER/GRADING LANE — 2026-09-13

**DRAFT FOR ROUTING. NOT FILED.** This lane does not edit `docs/standards/MONITOR_STANDARD.md`
— that is the verification team's, and the M6 lane's amendment is the live one. These are
drafted at the cfd-supervisor's request, in this lane's words, **cited to commits rather than
to anyone's summary**, for the supervisor to route.

Five members. Every one was **measured**, not reasoned to, and each names the artifact that
would let a stranger reproduce it.

---

## M-1 — THE CONTROL WAS NOT A CONTROL

**Cite: `25caef4c6`.**

**MECHANISM.** A control compares the instrument against a reference that is secretly the
same thing. It cannot register a difference whatever the instrument does, so **its pass is
structurally uninformative** — it is not weak evidence, it is no evidence.

**THE CASE.** `render_openfoam_3d_paraview.py --field p` was declared a silent no-op because
its output was pixel-identical to "the plain mesh render". **Measured: immediately after
ParaView's `Show()` and BEFORE any `ColorBy` call, `d.ColorArrayName` already reads
`['POINTS', 'p']`** — ParaView auto-colours by the first array it finds. The two images were
identical **because they were the same field**, not because colouring was dead.

**NUMBERS.** `--field` works and always did: colouring by `T` instead of `p` moves 7.07 % of
frame pixels; `p` against a genuinely solid surface moves 6.47 %.

**COST.** Two failed fix attempts, one withdrawn guard, and a shipped defect record whose
conclusion was wrong — before anyone rendered a true solid-colour arm.

**THE TEST.** Before trusting a control, ask what the reference arm would show **if the
instrument were working perfectly AND if it were dead.** If the answer is the same picture,
it is not a control.

---

## M-2 — USABILITY IS PART OF RELIABILITY

**Cite: `c2c46be07`.**

**MECHANISM.** A guard that fires correctly, but whose message does not tell the reader what
to do next, is read as a tool defect — then worked around, then deleted. **A guard that is
worked around protects nothing. An instrument can fail by being IGNORED as easily as by being
WRONG.**

**THE CASE.** A new degenerate-range refusal correctly blocked `--field U` on a no-slip wall
patch: `U` there is exactly zero by boundary condition and a picture of it shows nothing. The
terse message read as a bug.

**THE REPAIR.** The message now names the case — the tool renders BOUNDARY PATCHES; on a
no-slip wall `U` is zero by construction and `nut`/`nuTilda`/`alphat`/`k`/`omega` are
wall-function zeros; **the volume field is not zero**; use `p`, `T` or `rho`, or render a
slice. The evidence sits in the code comment at the branch it explains:
`3000/U boundaryField[wing] = noSlip` against an internalField `|U|` of 1.11–360.13 m/s;
`3000/nuTilda = fixedValue uniform 0` against an internalField 5.24e-06–0.0431.

**THE TEST.** Read every refusal message as a stranger at 2 a.m. **If it does not say what to
do next, it will be worked around.**

---

## M-3 — A GUARD DOING ROUTINE WORK HAS ALREADY SPENT ITS MARGIN

**Cite: `481fd48b9`.**

**MECHANISM.** When a guard fires during **normal, correct** operation it is being used for
**CORRECTNESS** rather than for **VERIFICATION**. Its budget of surprise is consumed by
ordinary use, so when a genuine defect arrives there is nothing held in reserve — and
operators learn it "always complains" and route around it (which is M-2 arriving by a
different road).

**THE CASE.** `render_openfoam_3d_paraview.py` staged every render into a **fixed**
`<out>/_stage`. Two lanes rendering into one campaign's `RENDERS/` — which is what every team
does — staged into the **same path** and corrupted each other.

**MEASUREMENT.** Two of this lane's own checks sharing an `--out` produced
`per-patch identity failed for 43 of 44 patches`. The geometry guard caught it, **which is
the only reason it was a nuisance and not a wrong picture.**

**THE TEST.** If a guard can fire during correct concurrent or repeated use, it is
**load-bearing, not a check.** Remove the condition that makes it fire; keep the guard for the
defect it was written for. **REPAIR:** `_stage_<pid>`.

---

## M-4 — A FLOOR MUST BE EXCEEDED BY CONSTRUCTION, NOT MET BY ARITHMETIC IDENTITY

**Cite: `e08a102cd`.**

**MECHANISM.** A pre-registration that states a minimum sample and a run length whose
arithmetic yields **exactly** that minimum has no margin on either side. **A quantity that
equals its own threshold carries no evidence about which side of it the truth is on**, and
any single lost sample converts a sound measurement into `NOT A RESULT` — with the failure
sitting in the registration, not in the run.

**THE CASE.** `DRIVAER-RATE-PROBE-96C` registered `endTime` 150, a 50-iteration ramp discard,
and a floor of **≥ 99** usable successive differences. 150 − 50 − 1 = **exactly 99**. The run
was clean and the measurement sound; **one missing `ExecutionTime` line would have voided it
on its own §5.**

**THE TEST.** Compute the margin at registration time, not at grading time. Size the run so
the floor is **comfortably** cleared — this probe should have registered `endTime` 160.

---

## M-5 — 🔴 TWO CORRECT RULES CAN BE JOINTLY UNSATISFIABLE, AND THE COLLISION IS SILENT UNTIL A LAUNCH REPORTS IT

**Cite: `e08a102cd`. THIS ONE IS NOT A DEFECT IN A TOOL. IT IS A COLLISION BETWEEN TWO
CONTROLS, BOTH OF WHICH ARE RIGHT, AND IT IS ABOVE THIS LANE AND ABOVE cfd.**

**THE TWO RULES.**
1. **`CLAUDE.md` rule 2 / rule 6:** a departure from a frozen document is disclosed as a
   **dated addendum appended at the foot**. Originals are struck, never rewritten.
2. **The runner's `grading_freeze` pin:** a document named there is compared **byte-for-byte**
   against the blob committed at `prereg_commit`, and any difference is reported as
   `MISMATCH`.

**APPEND A LEGAL ADDENDUM TO A PINNED DOCUMENT AND YOU BREAK THE PIN WHILE OBEYING THE
CONSTITUTION.** Nothing in either rule says which yields. Every team on this box uses both.

**THE CASE, WITH THE LAUNCH LINE VERBATIM.**

> `2026-09-13T00:30:26Z GRADER-FREEZE DRIVAER-RATE-PROBE-96C: MISMATCH -- 1 of 3
> comparator(s) named by 'grading_freeze' do NOT match freeze ab52c0a0.`

The probe's own registration was named in `grading_freeze` and then carried a dated addendum
recording its enqueue provenance, appended between the freeze commit and the launch.

**THE DEMONSTRATION, REPEATABLE BY ANYONE WITHOUT THIS LANE'S WORD:**

```
git show ab52c0a03:verification/campaign/DRIVAER_RATE_PROBE_PREREGISTRATION_2026-09-13.md > frozen.md
head -c $(wc -c < frozen.md) verification/campaign/DRIVAER_RATE_PROBE_PREREGISTRATION_2026-09-13.md | cmp - frozen.md
```

→ **the frozen bytes are a BYTE-EXACT PREFIX of the disk file.** The added content is the
addendum alone; the other two pinned comparators **MATCH**; and **no threshold, band or cap
line differs** between the two versions.

**THE RULING THIS LANE RECORDS, AND IT IS A PAIR, NOT A CHOICE.** The **result stands** — a
median of 0.3700 against a band frozen at a commit that provably contains that band is a
sound measurement. The **mismatch also stands, unretired** — the pin's claim is *"the frozen
file IS the file that ran"*, and strictly it was not. **A demonstration by the lane whose work
it concerns does not retire a pin; the pin exists precisely so the claim is not taken on that
lane's word.** Carrying both is more honest than carrying either.

**THE CONCRETE RULE, ADOPTED FOR THE DrivAer FAMILY 2026-09-13 BY THE cfd-supervisor:**
**a document named in `grading_freeze` is APPEND-FROZEN FOR THE LIFE OF THE PIN.** Anything
that must be recorded in that window goes in a **separate file**.

**AND THE IRONY IS RECORDED RATHER THAN SUPPRESSED, BECAUSE IT IS THE CLEAREST STATEMENT OF
THE COLLISION:** *the addendum that broke the pin was the one recording this lane's refusal of
its supervisor's dispatch.* **A document written to strengthen the procedural record broke a
procedural control.** That is not an argument against writing it — it is the reason the
collision needs a ruling from above rather than a habit from below.

---

*Drafted by a cfd `lab-lane`, 2026-09-13, for the cfd-supervisor to route. **NOT FILED.**
This lane amends no standard and no charter. No agent's message is Sanaa's consent.
Submissions parked.*
