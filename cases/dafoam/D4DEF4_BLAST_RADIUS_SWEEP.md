# D4-DEF-4 BLAST-RADIUS SWEEP — the answer is TWO, not one, and the second one was running while I swept

**Written 2026-08-25 by the D4-DEF-4 repair lane**, commissioned by
`cases/dafoam/ladder-a/A2/curriculum_D4/SUPERVISOR_D4DEF4_REPAIR_RULING.md` §6 (commit
`dbb88eb4`).

**Nothing here is sent, filed, uploaded, registered, posted or commented outside this box**
(`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **`D4-DEF-4` is a defect in THIS LAB'S OWN
INSTRUMENTS, not in DAFoam, OpenMDAO, IPOPT or pyOptSparse — no upstream report arises from this
sweep and none is drafted.**

Instrument: `cases/dafoam/sweep_dv_history_rescaling.py`. Every number below is reproducible by
running it.

---

## 0. THE ANSWER, FIRST

> **The blast radius is TWO items, not one. `curriculum_D4` (A2) and `curriculum_D7` (A3) both
> read the optimum's design point out of `OptView.hst` and re-apply it through `prob.set_val`,
> and both do it on a path where `shape`'s registered scaler is `10.0`.**

**The D8-DEF-2 precedent — that the honest answer might be "exactly one instance, close the
sweep" — does NOT hold here, and the ruling was right to commission this rather than assume it
either way.** D7's chain is byte-for-byte the same design as D4's with different constants:
`d7_extract_endpoint.py` calls `h.getValues(major=True, scale=False)` at its line 40, writes
`d7_endpoint_dvs.json`, and `d7_fd_endpoint.py:144` applies it with
`prob.set_val(key, np.array(dvs[key], dtype=float))`. **`scale=False` is inert there for exactly
the reason it is inert in D4.**

**D7's registration makes its pinned witness even sharper than D4's:** `U0 = 291.6`, and
`patchV` is pinned with `lower[0] == upper[0] == U0`. A driver-scaled extraction would read
**29.16** where the physical value is **291.6**.

**No D7 repair is authorised and none is taken here.** The supervisor ruled that D7 **inherits
this repair rather than authoring a parallel one**, and that `VERIFICATION_CHARTER.md` §2d.1
condition (1) — a **demonstrable** error, not a predicted one — is **not yet met for D7**,
because D7 has run no optimisation and no history exists to be mis-read. **I confirmed that
independently:** `find /home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin -name OptView.hst`
returns **nothing** at 2026-08-25T22:05Z. **D7's exposure is real and its error is not yet
demonstrable, and those are two different statements.**

---

## 1. THE FIRST PASS WAS WRONG AND IS RECORDED RATHER THAN TIDIED

**Pass 1 keyed on `set_val` and returned 87 hits, 72 of them "FIRING".** That would have been a
lab-wide alarm and it was an artifact of the instrument.

**The mechanism: writing a history is not reading one.** Every optimisation runScript in this lab
contains `prob.driver.hist_file = "OptView.hst"` — it **writes** the history — and every one
calls `prob.set_val` during ordinary model setup. A pattern that treats "mentions OptView" as
"reads OptView" flags all of them.

**Pass 1 also could not have seen D4 itself.** A per-FILE intersection of "reads a history" and
"re-applies" **misses the D4 chain entirely**: `d4_extract_endpoint.py` reads the history and
never calls `set_val`; `d4_fd_endpoint.py` calls `set_val` and never touches the history; the
JSON between them is where the units are lost. **A sweep that cannot see the defect it was built
for proves nothing about anything else.**

Both defects are fixed in the committed instrument, and the second is now a **refusing control**:
the sweep carries `CHAIN_PLANT = cases/dafoam/ladder-a/A2/curriculum_D4` and **exits 2 if the D4
chain does not come back**.

---

## 2. THE DISCRIMINATOR — the SOURCE of the vector, not the `set_val`

This is the sweep's actual finding about the defect class, and it is what made the second pass
sharp.

| the vector came from | unit system | exposed to D4-DEF-4? |
|---|---|---|
| `prob.get_val(...)` | **PHYSICAL** (the model value) | **No.** Writing it to a file and `set_val`-ing it back is a round trip in one unit system. |
| `History.getValues(...)` on `OptView.hst` | **DRIVER-SCALED** — OpenMDAO applies `scaler` before pyOptSparse sees the problem, so pyOptSparse's own scale is 1.0 and its `scale` flag is a no-op | **Yes. This is the defect.** |

**A sweep keyed on `set_val` is measuring the wrong thing.**

---

## 3. POPULATIONS — enumerated separately, because one is invisible to the other's instrument

| population | enumeration | files walked | `.py`/`.sh` examined | chains examined |
|---|---|---|---|---|
| **A — tracked blobs at HEAD** | `git ls-tree -r HEAD --name-only`; blobs via `git show HEAD:<path>` | 13,149 paths in tree | **1,115** | **214** |
| **B — run roots on disk** | `os.walk` of `/home/ubuntu/certonomous-runs`, OpenFOAM case sub-trees pruned | 42,471 | **2,141** | **667** |

**The worktree is deliberately NOT swept.** The shared index is heavily decayed and stages
deletions of files present at HEAD; other teams' uncommitted work would enter the population and
the sweep would be measuring the index rather than the lab.

**Population B is not optional.** `d4_stage_F.sh` lived in a run root **untracked**, and a
supervisor read a truncated listing as its absence. Files outside git are not invisible merely
because they are outside git.

**`grep -r` on this box is ugrep honouring ignore files, so gitignored archives are invisible to
it. Neither enumeration above is a grep**, and no `head`, `tail` or pager appears anywhere in the
enumeration path.

---

## 4. L-325 APPLIED TO THIS SWEEP'S OWN INSTRUMENT — every pattern planted before any zero is believed

"Not found" is the return value of two different situations: the record is absent, and the
instrument cannot express its name. The sweep **REFUSES (exit 2)** if a plant does not come back.

| plant | pattern | returned |
|---|---|---|
| `d4_extract_endpoint.py` | READS_HISTORY | **yes** |
| `d4_fd_endpoint.py` | REAPPLIES | **yes** |
| `d4_opt_runScript.py` | REGISTERS | **yes** |
| `d4_opt_runScript.py` | WRITES_HISTORY | **yes** |
| `sdk/scripts/build_a2_shape_frames.py` | READS_HISTORY | **yes** |
| `cases/dafoam/ladder-a/A2/curriculum_D4` | **CHAIN_GROUPING** | **yes** |

**Measured live while building this instrument, and it is the lesson in miniature:**
`git grep -lE 'History('` returns **zero results** with `fatal: Unmatched (` on stderr — **a
regex error rendering as an empty result set**. Read for presence, that zero is a false negative,
and nothing in the result distinguishes it from a true one.

---

## 5. THE RESULT

| state | count | meaning |
|---|---|---|
| **FIRING** | **8 chains, 2 distinct items** | reads a history, re-applies, and a registered scaler on that path is ≠ 1.0 |
| **MITIGATED** | 5 chains, 2 distinct instruments | reads a history, re-applies, and already divides by a scaler |
| **HIT_REGISTRATION_NOT_IN_CHAIN** | 2 | reads a history, re-applies, no `add_design_var` in the chain |
| **EXPOSED_NOT_FIRING** | **0** | — see §5a, this zero is the one that needs care |
| **SAFE_BY_SOURCE** | 52 | re-applies a DV vector from a file, but the file is sourced from `get_val` |
| clean chains | **208 of 214 (A) + 606 of 667 (B)** | |

### 5a. FIRING — 8 chains, and they collapse to TWO ITEMS

| item | chain | reader | `shape` scaler | pinned witness |
|---|---|---|---|---|
| **D4 (A2)** | `certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/{O,F,P1,P2}` | `d4_extract_endpoint.py` | **10.0** | `patchV[0] = U0 = 100.0`, read back as 10.0 — **MEASURED, this is the crash** |
| **D7 (A3)** | `cases/dafoam/ladder-a/A3/curriculum_D7` and `certonomous-runs/CURRICULUM-D7-a3-m6-cdmin/{.,P1,P2}` | `d7_extract_endpoint.py` | **10.0** | `patchV[0] = U0 = 291.6`, would read back as 29.16 — **PREDICTED, not measured: no history exists yet** |

The eight rows are four staged copies of the D4 tree and four of the D7 tree. **Two items.**

### 5b. MITIGATED — and one of them carries the drift risk the ruling names

| chain | what it does | divisor source |
|---|---|---|
| `cases/dafoam/ladder-a/A2/curriculum_D4` (+ its ACC/F2 staged copies) | this repair — `d4_endpoint_locus.py` / `d4_endpoint_physical.py` | **PARSED from `d4_opt_runScript.py` with `ast`** |
| `sdk/scripts/build_a2_shape_frames.py` | reads `OptView.hst` with `History(..., flag="r")` at line 149, `getValues(major=True)` at 150, then `dvgeo.setDesignVars({"shape": shape_rec[k] / SCALER_SHAPE, ...})` at 167 | **TYPED CONSTANT `SCALER_SHAPE`** |

**`build_a2_shape_frames.py` already knew about this defect** — its line 253 says the frames are
*"OptView.hst, de-scaled by the OpenMDAO driver scalers"*. **It is correct today and it is
correct by a constant that nothing checks against the registration.** That is precisely the
failure mode the ruling forbids for the repair — *"a typed constant can drift from the
registration and would reintroduce this defect somewhere new"* — sitting in an existing
instrument. **It produces figures, not gates**, so no verdict currently rests on it. Recorded as
a finding; **no change is made to it by this lane**, because it is outside D4's case directory
and repairing another item's instrument on my own authority is exactly what a lane may not do.

**A caveat on the automated classification, stated because it flatters the instrument:** the
sweep's `divisor_parsed_from_registration` flag is computed over the whole **directory**, and
`sdk/scripts` contains other files. It reports `parsed=True` for that chain. **The manual read
above is the authority and it says TYPED.** The automated flag is over-optimistic at directory
granularity and is not to be quoted alone.

### 5c. EXPOSED_NOT_FIRING is ZERO, and that zero is reported with its reason

**No chain reads a history, re-applies, and has every scaler at 1.0.** Both history-reading
chains in this lab carry `shape` at 10.0. The state exists in the instrument and was exercised
in its construction; it simply has no occupants. **Reported as a measured zero from a state the
instrument can express, not as an absence of the question.**

### 5d. SAFE_BY_SOURCE — 52 chains, and this is a NEAR MISS, not a clean bill

These re-apply a DV vector read from a **file**, but the file is written from `prob.get_val` and
is therefore physical. **The largest group is D9 (A5), whose `opt_dv.json` records
`shapexUpper` from `prob.get_val("shapexUpper")` at `d9_run_script.py:364` and re-applies it at
line 337.**

**D9's `shapexUpper` carries a registered scaler of 25.0** — two and a half times D4's. **Had
that file been sourced from `OptView.hst` instead of from `get_val`, D9 would be a worse
D4-DEF-4 than D4 is.** It is not, and **nothing in D9 asserts that its DV file is physical**:
there is no units declaration on the artifact, no pinned-variable witness, and no bounds check
on load. **D9 is safe by where its file happens to come from, not by anything that would stop
the source changing.** That is why the state is named `SAFE_BY_SOURCE` and not `CLEAN`.

The other groups (D3/A4, the W4 discriminator trees, the upstream DAFoam tutorials) are the same
shape with scalers of 1.0 or with `get_val` sources.

---

## 6. WHAT THIS ENUMERATION CANNOT SEE — named, not fixed

1. **Untracked files in the Certonomous worktree.** Deliberately excluded, reason in §3.
2. **`/home/ubuntu/closure-data`, `/home/ubuntu/closure-challenge-benchmark`** and any other
   out-of-git data area.
3. **Instruments inside container images.**
4. **A chain whose two halves live in DIFFERENT directories.** Grouping is by directory, so a
   reader in one tree feeding a re-applier in another is **invisible to this sweep**. This is the
   sweep's own version of the pass-1 defect, one level up, and it is not closed.
5. **A scaler passed as a variable rather than a numeric literal.** The parser records 1.0, which
   biases a chain toward `EXPOSED_NOT_FIRING` rather than toward `CLEAN` — the safe direction,
   but it is a bias and it is stated.
6. **A history read through a helper module imported from elsewhere.**

---

## 7. THE RECOMMENDATION

**Do NOT close this sweep, and do not run it again as a family-wide exercise either.** Both
occupants are now known by name. Concretely:

1. **D4 is repaired**, and the repair is proved by a solve (`D4_DEF4_REPAIR_PREREGISTRATION.md`,
   ACC-1 **PASS** at `rel_CD = 2.34e-04`).
2. **D7 inherits it.** The repair was written to be inheritable and **that was tested, not
   claimed** — see §8.
3. **`sdk/scripts/build_a2_shape_frames.py` should have its typed `SCALER_SHAPE` replaced by the
   parsed registration**, by whoever owns it. It gates nothing today; it is one edit away from
   being correct for a reason instead of by luck.
4. **D9's `opt_dv.json` should carry a units declaration and a pinned/bounds assertion on load.**
   Not because it is wrong — it is right — but because its rightness is currently unwitnessed.

**Items 3 and 4 are recommendations to their owners and are NOT taken by this lane.**

---

## 8. THE REPAIR IS INHERITABLE, AND THAT IS A MEASUREMENT

The supervisor asked for a repair D7 could adopt rather than a D4-specific one, and asked me not
to generalise past what I can test. **So I tested it.**

`d4_endpoint_locus.py` was pointed at **D7's own `d7_opt_runScript.py`, with no code change of
any kind**, and:

| | D4 | D7 |
|---|---|---|
| scalers parsed from the item's own runScript | `{patchV: 0.1, shape: 10.0, twist: 0.1}` | `{patchV: 0.1, shape: 10.0, twist: 0.1}` |
| `U0` read from the same source | **100.0** | **291.6** |
| pinned witnesses DISCOVERED (not told) | 1 — `patchV[0] = 100.0` | 1 — `patchV[0] = 291.6` |
| CONTROL P on a correct vector | PASS | PASS |
| **CONTROL P on the driver-scaled vector** | **REFUSED**, reconstructed 10.0 vs 100.0 | **REFUSED**, reconstructed 29.16 vs 291.6 |

**The instrument reproduced D7's own registered falsifiable prediction — 29.16 against 291.6 —
from D7's own source file, with zero D4-specific input.** Nothing about D4's three design-variable
families is hard-coded: the parser takes whatever `add_design_var` calls it finds and refuses if
it cannot read `lower`, `upper` and `scaler` for every one of them, and the pinned control
**discovers** `lower == upper` components rather than being told where to look.

**What is still D4-specific, stated plainly so a D7 adoption is not over-sold:**
`d4_endpoint_physical.py` hard-codes the two frozen md5s and the four filenames
(`d4_extract_endpoint.py`, `d4_opt_runScript.py`, `d4_endpoint_dvs.json`, and the two output
names). **A D7 adoption needs a sibling wrapper with D7's md5s and filenames; the controls and
the parser it calls need no change at all.** That is a fifteen-line file, and it is not written
here because **no D7 repair is authorised and D7's error is not yet demonstrable** (§0).

**And the thing this does NOT establish, named:** the test above shows what CONTROL P **would**
do to a driver-scaled D7 vector. It does **not** show that D7's history contains one, because
**D7 has no history**. The 29.16 figure is a prediction, exactly as D7's own record has it.
