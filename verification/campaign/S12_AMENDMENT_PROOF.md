# PROOF FOR THE `CRM_WINGALONE` §12 AMENDMENT — `lines whose number changed above this section: 0`

Rule 6 requires the assertion. **This file proves it by construction instead of asserting it**, which
is what cfd-supervisor asked for. **The frozen file was NOT modified to produce this proof** — the
amended file was built in a scratch location and hashed; the registration on disk still hashes to
its frozen blob.

## The frozen facts

| quantity | value |
|---|---|
| frozen file | `verification/campaign/CRM_WINGALONE_PREREGISTRATION.md` |
| freeze commit | **`d2629d326`** |
| frozen blob | **`1fa5fb725e6298d99dc4ab2207f55f11e575b285`** |
| size / lines | **37,613 bytes / 595 lines**, terminated by `0x0a` |

## Proof 1 — byte-prefix hash

The amendment is **appended**, so the first 37,613 bytes of the amended file must be the frozen blob
**bit for bit**. Constructed and measured:

```
head -c 37613 <amended> | git hash-object --stdin
  -> 1fa5fb725e6298d99dc4ab2207f55f11e575b285
git rev-parse d2629d326:verification/campaign/CRM_WINGALONE_PREREGISTRATION.md
  -> 1fa5fb725e6298d99dc4ab2207f55f11e575b285
```

**IDENTICAL.** Not one byte before the amendment differs, so not one line above it can have changed
number.

## Proof 2 — independent, on line numbers directly

A hash proves bytes; it does not *read* as a statement about line numbers. So the section headings
were compared by line number as well:

```
diff <(grep -n '^#\{1,3\} ' <frozen>) <(head -595 <amended> | grep -n '^#\{1,3\} ')
  -> no differences
```

**Every §1–§12.2 heading sits on exactly the line it sat on before.** Two proofs, one of bytes and
one of line numbers, because other records cite this file **by line** and one citation sits inside an
executable check.

## The append operation, exactly

The append block is the region between the two `── TEXT TO APPEND ──` markers in
`CRM_WINGALONE_S12_AMENDMENT_DRAFT.md`: **86 lines, 4,766 bytes.** Amended file would be
**681 lines, 42,379 bytes.**

```bash
cd /home/ubuntu/Certonomous
F=verification/campaign/CRM_WINGALONE_PREREGISTRATION.md
D=verification/campaign/CRM_WINGALONE_S12_AMENDMENT_DRAFT.md
# 1. REFUSE unless the file is still exactly the frozen blob
[ "$(git hash-object $F)" = "1fa5fb725e6298d99dc4ab2207f55f11e575b285" ] || { echo "REFUSE: not the frozen blob"; exit 1; }
# 2. append only the marked region
awk '/^## ── TEXT TO APPEND BEGINS ──$/{f=1;next} /^## ── TEXT TO APPEND ENDS ──$/{f=0} f' $D >> $F
# 3. RE-PROVE after the append, never only before
head -c 37613 $F | git hash-object --stdin   # MUST print 1fa5fb725e6298d99dc4ab2207f55f11e575b285
```

🔴 **Step 3 is not optional and is not a repeat of step 1.** Step 1 proves the input; step 3 proves
the result. **A status artifact that outlives its run reads identically to a current result** — the
defect this rung met twice today — and a pre-append hash is exactly such an artifact once the append
has happened.

## What this proof does NOT establish

- **It does not sign the amendment.** The freeze block is the supervisor's personal signature and the
  draft's signature field is left **UNSIGNED**.
- **It does not establish that the amendment's CONTENT is correct** — only that appending it moves no
  line above it. The content is §13.1's heading correction and §13.2's probe-surface correction, each
  of which stands on its own evidence.
- **It says nothing about §10.** No gate, threshold, cap or label is touched by the append.
