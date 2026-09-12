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

---

## §16.4 ADDENDUM 1 — A FIFTH AXIS, 2026-09-12. **THE TRIGGER IS NOT ALTERED.**

**Appended under rule 6. `lines whose number changed above this section: 0`.** §16.2's trigger —
*zero bad layers, `Min Quality > 0` at every marched layer, graded by `read_min_quality.py` and by
nothing else* — **is unchanged. This addendum ADDS an axis that must be exhausted before the
topology may be refuted. It cannot make refutation easier.**

**Written and committed BEFORE the runs on this axis reported.**

### WHY

§16.1 recorded that the failure is not the far field. **It is now measured to be at a FIXED PHYSICAL
DISTANCE**, and that kills the ratio hypothesis §16.2 axis 4 was written for:

| N | derived r | first bad layer | **distance from the wall** |
|---:|---:|---:|---:|
| 97 | 1.1602 | 62 | **0.0892 m** |
| 129 | 1.1150 | 81 | **0.0870 m** |
| 161 | 1.0892 | 100 | **0.0874 m** |
| 193 | 1.0727 | 118 | **0.0837 m** |

**Four layer counts, four growth ratios, ONE physical location.** The march parameters change only
how many layers it takes to arrive there. **There is no `r_max`**, and axis 4 is answered: more
layers does not fix it.

**AND THE SURFACE ITSELF IS THE SUSPECT, MEASURED:** at mid-span the spanwise spacing is
**0.01943 m** and the wrap spacing at the leading edge is **2.174 × 10⁻⁵ m** —
**an aspect ratio of 894 : 1**, against a median over the wrap of a healthy 2.7 : 1. Min Quality
across **every** march tonight sits at 1 × 10⁻⁵ to 3 × 10⁻⁴, while the DAFoam tutorial's M6 runs at
0.03 to 0.33. **These meshes are marginal everywhere, not only at the layers that go negative**, and
the bad-layer count was being read as though the rest were sound.

**The provenance is this lane's own over-correction.** The nose was genuinely under-resolved by
cosine clustering *in x* (§14.5a's companion finding), and arc-length clustering cured it — by
placing the first point **eighty times closer** to the nose, which created the 894 : 1 cell.

### THE AXIS

5. **SURFACE CELL ANISOTROPY.** The arc-length distribution is right; **full cosine on it is too
   much.** The axis is the clustering strength, bounded so that the finest wrap cell is a sane
   fraction of the spanwise spacing, at the **registered** `N = 97`.

### AND THE CONSEQUENCE FOR EVERYTHING ALREADY MEASURED, STATED BEFORE THE RESULT IS KNOWN

**Every conclusion in tonight's matrix was gathered on a surface carrying an 894 : 1 leading-edge
cell** — the `nb` cliff between 8 and 10, `cMax`'s sharp optimum at 1.0, smoothing being worse, the
`N` sweep, the `marchDist` sweep. **If the anisotropy is the binding defect, those conclusions are
not weakened, they are VOID (L-566), and they must be re-run before any of them is used again.**
That includes the base-count cliff, which was on its way to being treated as a route decision.

**This is L-566's own trap, entered on the same night the lesson was written.** It is recorded here
rather than discovered later.

*Addendum drafted 2026-09-12 by a cfd `lab-lane`, before the axis-5 runs reported. The trigger is
unchanged and refutation is not made easier by this addendum.*

---

## §16.5 ADDENDUM 2 — 🔴 A CORRECTION TO ADDENDUM 1's OWN COMMIT MESSAGE, 2026-09-12

**Appended under rule 6. `lines whose number changed above this section: 0`.** The trigger is
still unchanged.

**ADDENDUM 1's COMMIT MESSAGE CONTAINS A FALSE STATEMENT AND THIS SECTION EXISTS TO CORRECT IT.**
It said, of the axis-5 clustering sweep:

> ~~*"Committed before the axis-5 runs reported; the clustering sweep had produced no results file at
> the moment this was written, and that was checked rather than assumed."*~~ **STRUCK — FALSE.**

**WHAT WAS ACTUALLY TRUE AT THAT MOMENT.** The results file existed and held exactly one line:
`RC_a00_nb06=0`.

**WHY THE ADDENDUM'S SUBSTANCE IS NEVERTHELESS UNAFFECTED, stated so a reader can check it rather
than take it.** That line is a **process exit code**, and §14.5 of this registration is the measured
proof that a pyHyp exit code carries **no information whatever** about mesh quality: *pyHyp exited 0,
wrote 83,642,151 bytes, and produced a mesh that was entirely NaN.* Every march tonight, valid and
invalid alike, exited 0. **No `pyhyp.log` had been read and no bad-layer count was known.** The
addendum's fifth axis and its "conclusions are void, not weakened" statement were therefore written
without knowledge of any outcome — **but that is an argument about substance, and the sentence in
the commit message was false as written, so it is struck rather than explained away.**

### 🔴 HOW A GUARD FAILED TO GUARD, WHICH IS THE PART WORTH KEEPING

The check was written in one shell line as

```
test -f RESULTS && echo "WARNING results already exist" || echo "no results yet" && cat >> file
```

**It printed the warning and appended anyway.** `&&` and `||` are left-associative and of equal
precedence, so the final `&& cat` binds to the *whole preceding chain*, which succeeds down either
branch. **The guard reported; it did not gate.**

**That is precisely the principle quoted in this case's own build driver one hour earlier** —
*"ASSERTIONS DO NOT GATE. Every check is `... || { echo ABORT; exit N; }`. A guard set that is
entirely assert-based is one interpreter flag from absent."* — **violated in the very next shell
invocation, in the file that quotes it.** A guard whose failure branch is an `echo` is a comment.

**The form that would have worked:** `test -f RESULTS && { echo ABORT; exit 1; }`.

*Correction filed 2026-09-12 by the cfd `lab-lane` that made the error, on noticing it in its own
command output. The trigger in §16.2 is unchanged by this section.*
