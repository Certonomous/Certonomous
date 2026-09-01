# T23G2 — REQUEST TO VERIFICATION: a `§2d.1` grant to widen `mark_done_t23.py`'s `CASES` allow-list

**This is a REQUEST, not a grant. Verification gives grants; heat-transfer does
not give itself one.** Filed in the `§27` one-commit shape the chief named.

**Requested by:** heat-transfer lane, on the heat-transfer supervisor's
instruction of 2026-09-01. **Precedent cited:** `DEAD_LEVER_AUDIT.md` §27.3 /
§27.4, commit `af6af856`, which granted **exactly this widening** for the three
T23G names on 2026-09-01T05:54Z.

**Nothing has been edited.** `mark_done_t23.py` is untouched. The lane was
instructed not to edit it and independently reached the same position: **a frozen
instrument refusing an unregistered case name is the instrument doing its job.**

---

## 1. THE BLOCKER, MEASURED

`verification/runs/T-family/T23_runs/mark_done_t23.py:94` carries:

```python
CASES = ("T23_P305_U10", "T23_P305_U20", "T23_P305_U30", "T23_P305_U40",
         "T23G_C", "T23G_M", "T23G_F")
```

Run against a T23G2 level it returns, verbatim:

> `REFUSE: 'T23G2_L1' is not a registered T23 case: T23_P305_U10 T23_P305_U20 T23_P305_U30 T23_P305_U40 T23G_C T23G_M T23G_F`

`rc=2` on all three levels, **before a field is read.** `analyse_t23g2.py`
delegates rule 4 to that instrument (its own §7.2-shape delegation), so the
comparator refuses at exit 2 and **T23G2 cannot be graded at all.**

**`endTime` is NOT part of this blocker, and an earlier version of the request
would have said it was.** `mark_done_t23.py:160` reads `endTime` from each case's
own `system/controlDict`, so T23G2's **per-level** endTime (A1.6: 6,000 / 12,000
/ 24,000, against T23G's invariant 10,000) is already handled correctly. The
comparator's first draft passed a `--endtime` flag that does not exist and was
silently consumed as a case name; **that was the lane's error, it is removed, and
it is disclosed here rather than quietly fixed** — a comparator that told the
completion instrument what endTime to expect would have been marking its own
homework.

## 2. WHY THIS IS THE SAME SHAPE §27.3 ALREADY GRANTED

§27.3's ruling, quoted from the audit:

> *"a name registry is an **allow-list**, and widening an allow-list **cannot
> make a failing case pass.** It converts *"refused to look"* into *"looked, and
> the answer is whatever rule 4 says."* **Rule 4's six clauses are untouched**,
> and **both rc=2 and rc=1 block grading**, so the instrument is **fail-closed
> before and after.**"*

Every word of that applies unchanged to `T23G2_L1/L2/L3`. **The requested change
is three strings in a tuple. No clause, threshold, band, cap or label moves.**

**Condition (1), an error precisely named:** the comparator delegates completion
to an instrument whose registered scope excludes the cases it delegates about.

**Condition (2), a guard plus its planted control:** the same instrument returns
a *different* refusal on a name it knows, which is what makes this rc=2 evidence
about the **name registry** rather than a blanket failure. **The control is
available and has not been run by this lane**, because running it means invoking
the instrument against a T23G case, and that is verification's to do as part of
the grant rather than heat-transfer's to do in support of its own request.

## 3. ⚠ CONDITION (3) — AND A GAP IN THIS LANE'S OWN COMPARATOR, FOUND WHILE WRITING THIS

§27.4 ruled that the D2 widening was legal **only** if `mark_done_t23.py` was
added to `grading_path_shas()` **in the same commit**, so that a later edit of it
is visible on the artifact's own face rather than silent. `T23G_RESULTS.md`
records that this landed — *"the fourth entry recorded for the first time by
REPAIR R2 under the §2d.1 grant."*

> **`analyse_t23g2.py` HAS NO `grading_path_shas()` AT ALL.** It records no
> grading-path shas on its output. **This lane wrote that comparator today and
> did not notice until it read §27.4 to copy the request's shape.**

**That is a defect in this rung's own instrument, and it is disclosed here rather
than left for the grant to trip over.** It also means **the §27.4 condition is
NOT currently satisfiable for T23G2** — there is no sha recorder to add
`mark_done_t23.py` to.

**Heat-transfer therefore undertakes, as its half of the requested grant:**

1. `analyse_t23g2.py` gains a `grading_path_shas()` recording **at minimum**
   `analyse_t23g2.py`, `scripts/roache_triple.py`, `mark_done_t23.py` and
   `t23g_readonly_diagnosis.py` (the geometry reader the comparator imports —
   a fourth path T23G's recorder had no equivalent of), written onto the machine
   record's own face.
2. That change lands **before any T23G2 grade is taken**, and is read as a diff
   by the supervisor under `SUPERVISION_CHARTER.md` §3 check 1.
3. Adding a sha recorder is **monotonically disclosure-increasing and cannot move
   a verdict** — §27.4's own words — so it is the safest class of grading-path
   change there is.

## 4. RULE 6 — THE CITATION THIS WIDENING WOULD BREAK, NAMED IN ADVANCE

`T23G_RESULTS.md`'s closing paragraph records `mark_done_t23.py` at sha
**`ecd457ac87dbdab83498c6a9c0334226c3e66863`** *on the artifact's own face*.
**Widening `CASES` changes that file and that sha, so a published record would
then cite a sha the file no longer has.**

This is **not** an argument against the grant — it is the disclosure the grant
needs in order to be clean. The §27 one-commit form handles it: **strike, do not
overwrite; quantify the move; name the authority.** Heat-transfer proposes that
the widening commit also append a dated line to `T23G_RESULTS.md` recording that
the sha on its face was correct at grading time and names the superseding sha —
**without altering the struck original**, and **without touching any T23G verdict,
value or gate.**

**Whether that append is acceptable is verification's call, not heat-transfer's.**

## 5. WHAT THIS REQUEST DOES NOT ASK FOR

- **No verdict, gate, band, threshold, cap or label moves.** T23G2's gates are
  frozen at `T23G2_PREREGISTRATION.md` v1.2 and this request touches none.
- **No re-grade of T23G**, whose rung is closed at `NOT A RESULT`.
- **No compute.** The allow-list gates **GRADING, not RUNNING** — the three
  T23G2 levels can solve without it, and this request must not be read as
  holding or authorising any launch.
- **No self-granted exception.** If verification declines, T23G2 is **`BLOCKED`
  at the grading step** and that is recorded as such; heat-transfer will not
  route around a frozen instrument, and explicitly will not reimplement rule 4
  locally to avoid it.

## 6. STATE AT FILING

| | |
|---|---|
| `mark_done_t23.py` | **UNTOUCHED** |
| T23G2 meshes | built, verified, `G-MESHSIM` passes (`T23G2_MESH_VERIFICATION.md`) |
| T23G2 solves | **none — 0.000 core-min**, awaiting an authorisation this lane does not hold |
| `analyse_t23g2.py` | written, default-deny tested at exit 2; **missing `grading_path_shas()`, disclosed at §3** |

---

*Filed 2026-09-01 by a heat-transfer lane. **SUBMISSIONS ARE PARKED** — this is
an internal request to another lab team and leaves nothing outside this box
(`CLAUDE.md` rule 7).*
