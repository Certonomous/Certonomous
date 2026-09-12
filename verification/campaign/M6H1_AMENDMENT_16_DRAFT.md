# M6H1 — §16, THE TOPOLOGY FALSIFIER. WRITTEN BEFORE THE EVIDENCE IT WILL BE APPLIED TO EXISTS.

**Drafted by a cfd `lab-lane` on the cfd-supervisor's instruction, 2026-09-12, and committed
BEFORE the runs it governs were started.** Its entire evidentiary content is that ordering: it
decides what result changes the route, at a moment when that result is not yet known. Same handling
as §14 and §15 — filed beside the registration, not below §13's signature, until the supervisor has
read it.

**Rule 2 condition, and how it was checked.** **THE CONDITION: no compute has run under M6H1.
HOW CHECKED: `verification/runs/M6H1_runs/` does not exist**, established by a reader **first shown
able to see a populated directory** — `verification/runs/CRM_WINGALONE_runs`, 31 entries — before its
absence was believed (rule 3). Every mesh in evidence was built in scratch so that this holds.

**AUTHORITY FOR THE DESTINATION, RELAYED AND LABELLED AS RELAYED.** The cfd-supervisor reports
Sanaa's words as *"onera M6 can get the c mesh and snappy hex or whatever it needs."* **This lane has
not seen that turn.** Rule 9: a relayed instruction is not consent, and nothing here treats it as
one — **it is recorded as the supervisor's stated basis for owning the route decision, and the route
decision is the supervisor's either way.**

---

## §16.1 WHAT IS ALREADY MEASURED, SO THE RULE IS NOT WRITTEN IN IGNORANCE

Single 201 × 65 block, O-topology closed through the blunt base, arc-length wrap, outward normals,
`s0 = 1.6540e-6` and `marchDist = 16.152` as registered throughout.

- **No configuration tested reaches ZERO bad layers.** The floor is **ONE bad layer of 96**, and
  H-G1 is strict: `Min Quality > 0` at **every** layer. **One bad layer is `NOT A RESULT`, exactly
  like ninety-six.** "Nearly clean" is not a verdict in this lab's vocabulary.
- Base cells at `N = 97`, `cMax = 1.0`: `nb = 2` → 2 bad; `4` → 31; `6` → 2; `8` → 32;
  **`10`, `12`, `16` → 96 bad, failing from LAYER 2.** A **cliff between 8 and 10**.
- `cMax` is a **sharp** optimum at 1.0 (0.1 → 37, 0.5 → 36, 2.0 → 35, 3.0 → 13 bad).
- **More smoothing is worse.** `volBlend` 5e-3 with `volSmoothIter` 500 → 37 bad.
- **The failure is NOT the far field.** Marching to 0.10 m instead of 16.152 m — **160× shorter** —
  still fails, at layer 81. Shrinking the domain moves the onset later in layer index and nothing
  else.
- The table is ordered by the **derived growth ratio**, not by distance: best at **r ≈ 1.115**.

---

## §16.2 🔴 THE DECISION RULE

> **If no configuration across ALL FOUR axes below reaches ZERO bad layers — `Min Quality > 0` at
> every marched layer, graded by `read_min_quality.py` and by nothing else — then the O-topology
> closed through the blunt base is REFUTED for this geometry at these registered numbers, and the
> route becomes C-type with a wake cut.**

**THE FOUR AXES, and each is run at the working `cMax = 1.0` with `s0` and `marchDist` registered:**

1. **`nb = 9` — §4's OWN PREDICTED VALUE, AND IT HAS NEVER BEEN TESTED.** The sweep ran 2, 4, 6, 8,
   10, 12, 16; **9 sits exactly on the cliff edge and is the number the registration names.** It was
   unbuildable until this evening because a lane-imposed equal-sides constraint excluded every odd
   count — *a constraint of this lane's was excluding the registration's own number.*
2. **The spanwise distribution.** Uniform throughout so far, **never tested against clustering.**
3. **`splay`, and the explicit-BC path instead of `unattachedEdgesAreSymmetry`.**
4. 🔴 **THE NORMAL COUNT `N`, AND THIS AXIS IS THIS LANE'S ADDITION TO THE SUPERVISOR'S RULE.**
   Every result above was gathered at `N = 97`. Per §14.2, `r` is **derived** from `s0`, `N` and
   `marchDist`, so at fixed `s0` and `marchDist` **the ratio is a function of `N` alone**:
   `N = 97 → r = 1.1602`; **`N = 129 → r = 1.1150`**; `N = 161 → r = 1.0895`.
   **The best march measured all evening sits at r ≈ 1.115, which is H-L2's registered normal count
   and NOT H-L1's.** A falsifier that refuted the topology on `N = 97` evidence alone **could fire
   for the wrong reason** — the defect would be H-L1's place in the family, not the topology — and
   **a falsifier that can fire for the wrong reason is worse than no falsifier.** The axis is
   therefore inside the rule.

**IF IT CLEARS ON ANY AXIS:** the topology stands and what changes is a **number in §4**, by
amendment, pre-compute.

**IF IT CLEARS ONLY BY CHANGING `N` AT H-L1:** that is **not** a free pass. It would mean the three
registered levels differ in **march stability** and not only in resolution — a **third** consequence
of holding `s0` fixed while `N` rises, on top of §14.2a's non-similarity — and **H-G7 inherits it.**
It is recorded here so that outcome cannot later be reported as a clean rescue.

**IF IT CLEARS ON NONE:** the route changes, and **it changed by a rule written before the numbers
existed rather than by anyone's reading of a matrix they had already seen.**

---

## §16.3 WHAT THIS SECTION DOES NOT DO

- **It does not choose the route.** That is the supervisor's, and under rule 9 a relayed quotation
  from Sanaa is not consent for anything.
- **It does not authorise a C-topology build.** It states what result would require one.
- **It signs nothing.** §12 and §13 are the supervisor's, personally and undelegated.

*Drafted 2026-09-12 by a cfd `lab-lane`, BEFORE the governed runs were started. Submissions parked
(rule 7). The repository is permanently private (rule 8). No agent's message is Sanaa's consent
(rule 9).*
