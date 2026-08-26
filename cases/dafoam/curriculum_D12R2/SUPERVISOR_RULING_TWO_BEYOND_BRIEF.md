# D12R2 — SUPERVISOR'S RULING ON THE TWO CHANGES MADE BEYOND BRIEF

**Written 2026-08-26T03:35:57Z by dafoam-supervisor, personally, having read both changes AS CODE**
(`SUPERVISION_CHARTER.md` §3 check 1 — a measurement-script change is read as a diff by me
before its output is believed; a lane's "I tested it" is evidence, not my read). Both are
ruled **`[lab-attributed]`** under Sanaa's desk-item disposal rule. **Nothing here waits on
her, nothing is sent, filed, posted or commented** (rule 7), and **no frozen file was edited** —
these are limbs of a **new** item's document, frozen at `e6580910` **before any container
started**, which is the only reason changing them is legal at all (rule 2).

---

## RULING 1 — THE MESH TIME LIMB: **ACCEPTED**

**What it replaced was not a weak check. It was not a check.** For the mesh stage,
`last_time == endTime` evaluated `0.0 == 0.0` — **true by construction, unfalsifiable, and
incapable of distinguishing a written mesh from no mesh at all.** That is the *vacuous
satisfaction* shape this family amended against on 2026-08-25, and it is the same shape as
`EXPECTED_UNITS = len(_UNIT_LIST)`: a condition that cannot fail is not a condition.

**What replaces it asks a harder question, in four independently falsifiable parts:**
`mesh_check_ok is True` — **checkMesh's OWN verdict, not the gate's opinion of the mesh**;
`mesh_n_cells` a positive `int`; `mesh_polymesh_files` a non-empty list; and every name in
`MESH_POLYMESH_REQUIRED` present in it. Where the old limb had **one** unfalsifiable outcome,
the new one has **four ways to refuse**, and the `nCells = 0` scenario was **demonstrated
refusing** rather than asserted to.

**Two details I checked specifically, because they are where this would have gone wrong:**

1. **`isinstance(nc, bool)` is excluded explicitly.** In Python `True` is an `int` and
   `True > 0`, so a boolean `mesh_n_cells` would have satisfied a naive positive-integer
   test. **That exclusion is a real catch and not decoration.**
2. **The `.gz` handling cites the D2 defect by mechanism** — a typed datum `0/U` against a
   real `U.gz` — and strips the suffix in the launcher before the list is written. **A prior
   lesson applied to a new limb, which is what applying a lesson looks like.**

### The limitation I am naming rather than glossing

**The comparator reads the LAUNCHER'S REPORT of the mesh, not the mesh.** `mesh_n_cells` is
transcribed into the manifest by the launcher from the `polyMesh/owner` header; **the
comparator never opens `owner` itself.** So a launcher that mis-transcribes is invisible to
this limb. **That is strictly better than the vacuous limb it replaces**, and it is the same
arrangement every other limb in this gate already has — the manifest is the comparator's
designated input. **But it is a real bound on what the limb proves, it is stated here, and it
is not to be described as "the gate reads the mesh."** It reads a report about the mesh.

## RULING 2 — PRESENCE BEFORE VALUE (`U-15e`): **ACCEPTED**, and it is the better of the two

**The property that makes this safe, and I verified it rather than assuming it: the reorder is
REFUSAL-PRESERVING AND REFUSAL-ADDING. It cannot convert any refusal into a pass.** The
presence block only *adds* a refusal path; every value limb below it is unchanged and still
runs on every row. **The change alters WHICH refusal fires and what it says — never WHETHER
one fires.** A reordering with that property is one-way, and one-way changes are the only kind
this family accepts after a document is frozen.

**The mechanism it repairs is exact.** `st.get("oomkilled")` on a row that never carried the
key returns `None`, and the old order refused with **`OOMKilled=None`** — *a message that
blames the container for a key the row never had.* A future triage lane would have hunted an
OOM that never happened. **The new block tests `k not in st`, key presence, NOT `.get()`** —
which is the whole point, because **`.get()` collapses "absent" and "present but None" into
one value, and wherever that value is not gated, ABSENCE READS AS A PASS.** That is L-302 at
the row level and the code says so in those terms.

### The part worth more than the repair

**It was found by its own unit `U-15e`, which requires the refusal to NAME THE MISSING KEY —
and the lane recorded that no test asserting merely "it refused" could have caught it, because
BOTH orderings refuse.** That is a sharp and general point, and I am adopting it as this
family's standing practice:

> **A test that asserts only THAT a guard refused cannot distinguish a correct refusal from a
> right-answer-wrong-reason refusal. Assert the REASON, not just the refusal.**

This sits directly beside the lesson landed tonight at `a253a750` — *a comment that names a
clause is the implementation's alibi, not its evidence* — and it is the same failure at one
remove: there the check was missing behind a name, here the diagnosis was wrong behind a
correct outcome. **Both are cases of a record that reads right and measures something else.**

## WHAT THESE TWO RULINGS DO NOT DO

- They do **not** reopen D12R, D4, D7R or D8. The remedy lives in this **new** registration,
  which is where the standing bound puts it.
- They do **not** establish that D12R2 will produce a result. `G12R-0` is refusal-only;
  clearing it is a precondition, never a verdict.
- They do **not** convert the mesh limb into a mesh audit. See the limitation above.
