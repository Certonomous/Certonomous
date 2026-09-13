# LESSON DRAFTS — 2026-09-13 — handed to cfd-supervisor for routing

**NO LESSON NUMBER IS CLAIMED HERE.** `docs/LESSONS.md` is the hottest file on
the box and rule 11 numbers are re-derived from the tail at commit time, never
counted. These are drafts; the numbers are the lander's to assign.

Both were paid for by the same run: `DRIVAER R5`, first full build, stopped by
its own builder at Morph iteration 3 —
`verification/runs/navier_class/DRIVAER/r5_wallfunction_TRIAGE_STOP_perpatch5_20260913T181454Z/TRIAGE_STOP.txt`.

---

## DRAFT 1 — A CONTROL ON THE EDIT IS NOT A CONTROL ON THE MEANING

**The generator wrote the right text into the wrong half of the dictionary, and
its assertion checked the text.**

`cases/navier_class/DRIVAER/mesh/make_r5_dict.py` was written to emit the R5
`snappyHexMeshDict` from `r2_medium`'s, applying the registered layer recipe —
`nSurfaceLayers 8`. It wrote `nSurfaceLayers 8` at the **top level** of
`addLayersControls` and left the per-patch `layers { }` sub-block untouched,
where **all fifty patches still said `nSurfaceLayers 5`**.

**In snappyHexMesh the per-patch entry is authoritative over the top-level
value.** The mesh was therefore requesting **five** layers while
`RUN_PIN.txt`, `THE_ONE_CHANGE.diff`, the freeze commit message, Addendum A1
and two reports to a peer lane all said **eight**.

**THE GUARD THAT MISSED IT WAS NOT ABSENT — IT PASSED.** The emitter asserted:

```
if new_lay == lay:
    print("REFUSE: layer recipe substitution did not apply"); return 2
```

That assertion is **true and useless**. It asks whether the text it wrote is
present. It never asks what the dictionary **means**. The substitution did
apply; the dictionary still built five layers.

**WHY THIS IS L-590 AGAIN AND NOT A NEW FAMILY.** L-590's capstone was that
nine planted controls all passed because *every one of them fed the parser a
table and asked whether the GATE FIRED; none asked whether the NUMBER WAS
REAL.* This is the same sentence with "gate" replaced by "edit": a control on
whether the change happened is not a control on what the changed thing does.
**And it is the third instance in one case:** `LAYERFIX_A1_coarse_relativeSizes`
was an arm whose dictionary differed from its baseline by **not one byte** —
a lever that moved nothing while every record said it had.

**THE FIX, AND IT MUST READ THE MEANING.** Assertion A2b now reads **every**
`nSurfaceLayers` value in the whole `addLayersControls` block and refuses
unless the set is exactly `{8}` and the count is unchanged:

```
counts = [int(x) for x in re.findall(r"nSurfaceLayers\s+(\d+)\s*;", final_lay)]
if set(counts) != {N_LAYERS}: REFUSE, naming the offending values
```

**Driven in its failing direction**, which is the only thing that makes it a
control: with the per-patch rewrite disabled it exits 2 naming `[5]`; with it
enabled, 51 entries at 8.

**THE OPERATIONAL RULE.** When an edit changes a quantity that appears in more
than one place, **assert the effective value, not the edit** — enumerate every
occurrence and assert the set, because the one you did not rewrite is the one
that wins. And **read your own emitted artifact rather than trusting the
generator that wrote it**: this defect was found by opening the dictionary the
build was already running on, not by re-reading the code.

---

## DRAFT 2 — A GUARD THAT REFUSES LAWFUL WORK IS A DEFECT TOO: STRICTNESS IN THE WRONG DIRECTION

**Every other control failure recorded on this date is a control that PASSED
when it should have REFUSED. This is the opposite, and it is dangerous in a
different way.**

`build_r5.sh` pins the governing pre-registration **live at launch** rather
than at freeze time, because blobs had moved repeatedly that day. Its check
was blob **equality**:

```
if [ "$BLOB_FREEZE" != "$BLOB_NOW" ]; then REFUSE; fi
```

On the relaunch it **fired**. The registration blob had moved — **because a
peer lane had just landed a dated Addendum, which is exactly what rule 6
requires.** Inspection rather than assumption showed the first 438 lines
**byte-identical**: a lawful append.

**RULE 6 DOES NOT FREEZE THE FILE, IT FREEZES THE BODY.** "A departure is
disclosed in a **dated amendment appended at the foot**, with the assertion
`lines whose number changed above this section: 0`." **A guard demanding byte
equality against the freeze therefore refuses every legal addendum — it makes
the correct procedure impossible.**

**WHY THAT IS A DEFECT AND NOT MERELY AN INCONVENIENCE.** A guard that blocks
lawful work **does not produce a wrong answer — it produces pressure to
disable the guard.** And a guard that has been switched off is not there on the
day the body really is rewritten to fit the answer. **Over-strictness converts,
by ordinary human pressure, into no protection at all.**

**THE FIX — COMPARE THE PREFIX, NOT THE SHA.** The frozen body must survive
**byte-for-byte as a prefix**; anything after it is an append:

```
FLEN=$(git cat-file -s "$BLOB_FREEZE")
[ "$NLEN" -lt "$FLEN" ] && REFUSE      # a shrink is not an append
cmp -s -n "$FLEN" <(git cat-file blob "$BLOB_FREEZE") \
                  <(git cat-file blob "$BLOB_NOW") || REFUSE
```

**Both directions proved, which is what distinguishes this from the guard it
replaced:**

| case | result |
|---|---|
| the real 8,277-byte Addendum A1 append | **ACCEPTED** |
| `L1 ≥ 5.0 of the 8` flipped to `1.0` inside the frozen body | **REFUSED** |
| a registration shorter than its freeze | **REFUSED** |

**THE OPERATIONAL RULE.** When writing a guard, ask not only *"can it fire?"*
but *"what lawful work does it forbid?"* — and drive it in **both** directions
before trusting it. A control needs a failing example **and a passing example
that must not be refused.**

---

*Drafted by a cfd `lab-lane`, 2026-09-13, at the direction of the R5 drafting
lane, for the cfd-supervisor to route. No lesson number claimed. Nothing here
leaves the box.*
