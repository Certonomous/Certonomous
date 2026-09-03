# Curriculum D6RF2 — `F_mp` and `REF_off` at a producer whose anchor is unique, and the registration-time gate that would have caught `D6RF-BLOCKING-1` before a launch

**Item id:** `D6RF2` (dafoam curriculum successor to `D6RF`). **Team:** dafoam. **Date:** 2026-09-03.
**Version 1.0 — FROZEN by the commit that introduces this file.**
**Committed BEFORE any container starts** (`CLAUDE.md` rule 2).
Permission for detached launches: **`bc0e687e`**.
**Nothing here is sent, filed, uploaded, registered, posted or commented** (rule 7).
**No frozen file is edited** (rule 6). **This item has burned 0 core-min, started no container, and
IS NOT ENQUEUED.**

**Run root:** `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF2-a2-wing-multipoint-fd`, asserted
**ABSENT BY EXECUTION**:

    ROOT_ABSENCE_ASSERTED_BY_EXECUTION utc=2026-09-03T19:40:19Z
      /home/ubuntu/certonomous-runs/CURRICULUM-D6RF2-a2-wing-multipoint-fd=ABSENT

---

## 0. WHY A SUCCESSOR AND NOT AN AMENDMENT — and what is inherited unchanged

`D6RF` (`cases/dafoam/ladder-a/A2/curriculum_D6RF/`) registered `F_mp` and `REF_off`, the two arms
nobody in the D6 lineage had ever bought. It could not run them. **Ruled by the dafoam-supervisor
2026-09-03: successor, not amendment**, on three grounds — `D6RF` has had compute so
`VERIFICATION_CHARTER.md` §2d closes its gates; the fix touches a file frozen and md5-pinned in
`D6RF` §7b; and this family's precedent for an unrunnable registration is successor-not-amendment
(`D6`→`D6R`, `A1WR`→`A1WRT`).

**INHERITED BY CITATION FROM `D6RF`, UNCHANGED, AND NOT RESTATED HERE:** §1's three repairs
(`D6RF-DEF-1` the driver-scaled endpoint, `D6RF-DEF-2` the in-place `F_mp` staging, `D6RF-DEF-3`
`REF_off`'s 3.16×-short cap); §2's two arms and five FD components; §2a's staging contract S1–S8 and
its no-`rm -rf`, refuse-on-stale-directory rule; §3's gates, thresholds, bands and labels **in full**;
§4's anchors, caps `F_mp` **480.0** / `REF_off` **190.0**, ceiling **670.0**, `TMO` **7,110** /
**2,760** at `FRAME_ALLOWANCE_S = 90`, and the cost basis; §5's predictions; §6's two rows.
**NO GATE, THRESHOLD, BAND, CAP, LABEL, PREDICTION OR COST MOVES IN THIS ITEM.** What moves is the
producer's docstring, the pins that follow from it, and one new **pre-compute** gate.

---

## 1. `D6RF-BLOCKING-1` — the sentence explaining the anchor contained the anchor

`d6r_opt_runScript.py` carries the sentinel `# OpenMDAO setup` **twice**: at **`:230`**, the real
anchor, and at **`:21`**, inside the module docstring, in the sentence
*"The ANCHOR line `# OpenMDAO setup` is kept so that `d6r_fd_endpoint.py` and `d6r_ref_off.py` exec
the header exactly as D4's FD instrument does."* **The sentence explaining why the anchor exists
reproduces it, and thereby breaks it.**

Both consumers refuse on a count other than one — `d6r_fd_endpoint.py:67`, `d6r_ref_off.py:53` — so
**both arms were unrunnable, and so were `D6R`'s own.** `d4_opt_runScript.py` carries it **once**,
which is why D4's arm F3 ran.

**THE GUARDS WERE PROTECTING THE ITEM, AND THE MEASUREMENT SHOWS IT.** `split(ANCHOR)[0]` returns
**1,396 characters of a 12,861-character file**, truncated inside the docstring, where the correct
header is **10,275**. The truncated header carries **`daOptions`** — the docstring mentions it — but
**not `class Top`, not `POINTS`, not `U0`, not `CL_TARGETS`, not `WEIGHTS`**, every one of which the
consumers read out of the exec'd namespace. **A `daOptions`-only check would have passed it.**
Nothing about the detectors needs changing: a count-must-be-1 refusal is exactly what should happen.
**What was never checked is whether the producer could satisfy them.**

**HOW IT WAS FOUND, AND IT IS NOT TO THE LANE'S CREDIT.** `D6RF`'s own guard self-test started a
container by accident (`D6RF` ADDENDUM 3 §A3.3) and that container refused on this. **Without the
accident `D6RF` would have been re-enqueued after its `.gz` repair and spent `F_mp`'s registered
155.7 core-min reaching a guaranteed refusal.** That does not make the accidental launch acceptable;
it makes the disclosure valuable. `D6RF`'s `P2` — *"the chain COMPLETES"* — **MISSED, for a reason
established before the compute rather than after it.**

---

## 2. THE REPAIR — a docstring reword, and the pins that follow from it

### 2a. ⚠ A CORRECTION TO THE RULING THAT COMMISSIONED THIS ITEM

The ruling says the fix *"is a DOCSTRING REWORD and changes no executable byte"* and that the
successor *"stages its OWN copy of the producer with a new pin"*. **Both are true of the producer and
neither is sufficient**, because **both consumers hardcode
`PRODUCER_MD5 = "93edb4a231e13a7af065368f61a468ef"`** (`d6r_fd_endpoint.py:31`, `d6r_ref_off.py:30`)
and check it **before** they ever count the anchor. **A one-character reword therefore makes them
refuse one step EARLIER, at the md5.** So this item must derive the consumers too. It does — by
substitution of exactly two constants each, the producer's **name** and its **md5**, and nothing
else. `D6RF`'s `d6rf_endpoint_physical.py` pins the same md5 and is derived on the same terms.

**`D6R`'s originals are not edited, not moved and not re-pinned.** `D6R`'s record and its pins stand
intact, and this item reads them read-only.

### 2b. The derivation — enumerated, and every substitution asserted present-then-absent

`d6rf2_derive.py` derives four files from frozen bytes. **Anything not in the substitution set is the
source's bytes.** Each substitution must occur **exactly once** before and be **gone** after; a
substitution that matched nothing is a silent no-op and aborts.

| derived | from | substitutions |
|---|---|---|
| `d6rf2_opt_runScript.py` | `curriculum_D6R/d6r_opt_runScript.py` | **1 — the docstring sentence.** Prose only; **no executable byte changes** |
| `d6rf2_fd_endpoint.py` | `curriculum_D6R/d6r_fd_endpoint.py` | 2 — `PRODUCER`, `PRODUCER_MD5` |
| `d6rf2_ref_off.py` | `curriculum_D6R/d6r_ref_off.py` | 2 — `PRODUCER`, `PRODUCER_MD5` |
| `d6rf2_endpoint_physical.py` | `curriculum_D6RF/d6rf_endpoint_physical.py` | 3 — `RUNSCRIPT`, `MD5_RUNSCRIPT`, the locus module name |

`d6r_extract_endpoint.py` **does not use the anchor** (measured: zero occurrences) and is staged
**unchanged** under `D6R`'s own md5.

**The replacement names the anchor without reproducing it**, and the deriver **asserts the
replacement does not contain the sentinel**. Its closing line is registered here:
*"Name the anchor; never quote it."*

**THE REPAIR IS ASSERTED, NOT ASSUMED, and the assertions are stronger than a count:**

* the **original** must still carry the sentinel **twice** — otherwise the premise of this item has
  changed and the deriver aborts;
* the **repaired** producer must carry it **exactly once** — measured **2 → 1**;
* the header must be **≥ 10,000 characters** — measured **10,536**, against the broken **1,396**;
* the header must carry `class Top`, `POINTS`, `U0 =`, `daOptions`, `CL_TARGETS`, `WEIGHTS`;
* and the strongest form: **the repaired header is byte-for-byte the original's CORRECT header with
  the registered substitution applied.**
* every derived consumer must **name the repaired producer and pin its md5**, with the old md5
  **absent** from the file.

---

## 3. `G-ANCHOR` — THE NEW GATE, AND IT IS PRE-COMPUTE

**The rule, registered by the dafoam-supervisor 2026-09-03, in his words:**

> Any reader that splits a file on a sentinel must have that sentinel's **uniqueness asserted AT
> REGISTRATION**, on the bytes it will actually read — not merely refused at run time.

`d6rf2_anchor_gate.py` (md5 in §5) enforces it over **every anchor-scoped reader in this item**, and
it runs **before any container**, not as a grading gate. It **REFUSES (exit 3)** rather than
degrading. Its five clauses, each on the real bytes:

| clause | assertion |
|---|---|
| **A1** | the reader declares `PRODUCER`, `PRODUCER_MD5` and `ANCHOR`, **parsed out of the reader's own source by `ast`** — never typed into the gate, so a reader whose anchor changes cannot drift past it |
| **A2** | the producer it names is the one this item stages, it exists, and **the md5 it pins is that file's actual md5** — the clause the ruling did not anticipate |
| **A3** | the sentinel occurs **exactly once** in that producer |
| **A4** | the header `split(SENTINEL)[0]` is **≥ 9,000 characters** — *a count of 1 at the wrong site is still wrong* |
| **A5** | the header carries every symbol the consumers read out of the exec'd namespace |

**DRIVEN IN BOTH DIRECTIONS, ON REAL BYTES — 6/6, under `python3` AND `python3 -O`:**

* **positive:** the repaired producer passes for **both** readers — count 1, header **10,536**, all
  six symbols;
* **negative:** the **ORIGINAL producer, still on disk unedited**, **REFUSES at A3**, and the
  evidence prints the header it prevented — **1,396 chars, missing `class Top`, `POINTS`, `U0 =`,
  `CL_TARGETS`, `WEIGHTS`**, with a plant asserting that shape exactly;
* **A4:** a producer whose sentinel is **unique but moved to the top** — count still 1 — **REFUSES**;
* **A2:** a producer that **drifts by one comment** refuses **at the md5, before the anchor is ever
  counted**; a producer **absent** from the work directory refuses.

**This gate does not alter any inherited gate, threshold, band, cap or label.** It is a
registration-time admissibility check and it can only turn a launch into a refusal.

---

## 4. WHAT `D6RF`'s RUN ROOT COST, AND WHERE IT WENT

**Archived, never deleted**, on the supervisor's ruling, with the preservation asserted by count:

| | |
|---|---|
| from | `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF-a2-wing-multipoint-fd` |
| to | `…/CURRICULUM-D6RF-a2-wing-multipoint-fd_partial_20260903T193723Z` |
| paths | **617 → 617** |
| top-level entries | **25 → 25** |
| bytes | **68,393,914 → 68,393,914** |

**Total spend on that root: 0.800 core-min = $0.0007 DERIVED**, and **it is WASTE, named as waste
and never absorbed into any ratio** (`COMPUTE_BUDGET_CHARTER.md` §6). `F_mp`'s staging abort produced
**no `ARM=` row** and `spent_before_arm=0.000`.

**The stray `ARM=REF_off rc=2` row is ANNOTATED, NOT EDITED.** A line appended to that ledger names
it a **guard-self-test artefact, not an arm attempt** — no chain requested it; `STATUS.chain` had
closed `STOPPED_AT_FIRST_NONZERO arm=F_mp rc=5 not_run=[REF_off]` five minutes earlier. **No grader
may read it as this item's or `D6RF`'s `REF_off` arm.** Its `rc=2` is nonetheless a real physics
finding and is the origin of `D6RF-BLOCKING-1`.

> **A CORRECTION TO A FIGURE, RECORDED BECAUSE IT WAS CAUGHT BEFORE IT TRAVELLED.** The supervisor's
> first reading of that total was **380.8** core-min, from a regex that matched `cap_core_min=380.0`
> as well as `core_min=`. He caught it himself before it left his hands. **A sum is only as good as
> its word boundary** — the same defect this item's own driver was driven against.

**`verification/queue/dafoam/launched/D6RF_chain.json` IS LEFT EXACTLY AS IT IS.** It carries
pre-ADDENDUM-2 pins. **It is the historical record of what the daemon actually launched, and
rewriting a launched row falsifies history.** Registered here so a reader meeting those stale pins
knows why they are stale.

---

## 5. INSTRUMENTS — the md5 table

| file | md5 | role |
|---|---|---|
| `d6rf2_opt_runScript.py` | **`137539e0a99be27f27fdb69e063b2a87`** | the repaired producer — **1 prose substitution, no executable byte** |
| `d6rf2_fd_endpoint.py` | **`0ce81a0b038abe12728b5b062e4420df`** | the FD instrument, re-pinned |
| `d6rf2_ref_off.py` | **`25f532e01156d8bd93458b23e1471d0a`** | the off-design instrument, re-pinned |
| `d6rf2_endpoint_physical.py` | **`6e5fa9f9c2048b0665593282f62ba3dc`** | the endpoint repair wrapper, re-pinned |
| `d6rf2_anchor_gate.py` | **`e34c0cb62df30e7a1565b896d07a32e6`** | **`G-ANCHOR`**, the new pre-compute gate |
| `d6rf2_units_assert.py` | **`34f8b79b96cc17d28d42ffd9ebc1874f`** | the units gate, `D6RF`'s, with the §5a repair |
| `d6rf2_endpoint_locus.py` | `341189ca866f302a7e1bba8eefad3a57` | **byte-identical to `D6RF`'s** |
| `d6rf2_derive.py` | **`bb6ea17332ec39d7479b200e28edba4f`** | the deriver |
| `d6rf2_selftest_evidence.txt` | **`c1fc50112f5b8199149209734cb7f098`** | seven drives |

Staged unchanged under `D6R`'s / D4's own md5s: `d6r_extract_endpoint.py` `1743dd42…`,
`d4_extract_endpoint.py` `ee7d3c99…`, `d4_opt_runScript.py` `2906d52a…`, `d4_endpoint_locus.py`
`e63df184…`, `d4_endpoint_physical.py` `74c35c80…`.

**SEVEN DRIVES, ZERO CONTAINERS:** `G-ANCHOR` **6/6**, units **25/25**, locus **30/30** — each under
`python3` **and** `python3 -O` — plus the deriver re-driven, re-asserting every substitution.

### 5a. ⚠ A DEFECT IN THIS ITEM'S OWN SELF-TEST, FOUND BY DRIVING IT AND FIXED BEFORE THE FREEZE

On its first drive `d6rf2_units_assert.py --selftest` reported **`0/25 PASS`**. Not one leg was
wrong: the self-test **spawned a hard-coded filename**, `d6rf_units_assert.py`, which stopped
existing at the rename into this item, so every subprocess errored. **A self-test that cannot find
itself reports total failure for a reason that has nothing to do with the thing it tests.**
Repaired by resolving the path from `__file__`, which cannot drift on a rename; re-driven **25/25**
under both interpreters. **It is recorded rather than quietly fixed, because a `0/25` that a lane
explains away instead of reading is how a broken instrument gets a clean bill.**

---

## 6. WHAT IS OUTSTANDING BEFORE THIS ITEM MAY BE ENQUEUED

**`d6rf2_run_arm.sh`, `d6rf2_chain_driver.sh` and `d6rf2_grade.py` ARE NOT WRITTEN.** They are
derived from `D6RF`'s — which now carry the ADDENDUM 2 vacuous-zero repair, the ADDENDUM 3
compressed-field repair and the self-test safety gate — by an enumerated substitution set on the
instrument names and pins, plus **one addition: `G-ANCHOR` is invoked by the launcher at staging,
before any container.** They land as a **dated pre-compute addendum**, and the condition is stated
and checked by execution: **the run root does not exist** (asserted above, and to be re-asserted).

**No queue row may be filed and no container may start until that addendum lands** carrying their
md5s, a **driven** `d6rf2_guard_selftest.py` with a container census before == after and zero
containers created, and the every-guard-precedes-every-destructive-step assertion with line numbers
recomputed from the file. **Nothing in §0–§5 changes when it lands.**

---

## 7. WHAT THIS ITEM MAY NOT CONCLUDE

* **Nothing that repairs `D6RF`'s or `D6R`'s verdicts.** `D6RF`'s `P2` MISSED and stays missed.
* **No claim that the anchor repair makes the arms run.** It removes one refusal, measured. **No
  container has ever run `F_mp` or `REF_off` at any point in this lineage**, and `L-316` binds: a
  self-test proves the **instrument**, never the **case**. **The first real container is still the
  first evidence about the case.**
* **No claim about the SHIPPED toolchain** — PATCHED-only, `D6RF` §6 inherited.
* **No GCI**; no grid family exists here.
* **A `GATE FAIL` or a `NOT A RESULT` here is a result and is reported as one.**

**`CLAUDE.md` check-1 and check-4 are the SUPERVISOR'S and this lane claims neither.** Enqueueing is
not authorisation.
