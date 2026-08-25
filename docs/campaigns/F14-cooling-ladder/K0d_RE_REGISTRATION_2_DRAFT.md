# K0d — RE-REGISTRATION DRAFT. **NOT FROZEN. NOT REGISTERED. NO RUNG ID ASSIGNED.**

> **THIS IS A DRAFT AND IT REGISTERS NOTHING.** It carries **no rung id**, it is
> **not frozen**, no sha is claimed for it, and **nothing in it may be cited as a
> registered gate, threshold, cap or label.** It authorises **no solve**.
> **Landing a re-registration is Sanaa's and the chief's** — a lane drafts, a
> supervisor recommends, and neither registers. **It supersedes nothing until
> somebody with the authority to supersede says so.**
>
> **`K0d_REREGISTRATION.md` (v1.3) remains the operative document until then**,
> and it stays on disk byte-unchanged (standing rule 6).

**Drafted:** 2026-08-25, by a heat-transfer lane, on the heat-transfer
supervisor's ruling of the same day.
**Compute consumed by this draft: zero core-minutes.**

---

## 0. WHY ONE DOCUMENT AND NOT THREE AMENDMENTS

**Three independent findings closed all three columns of the same rung.** They
are not three defects in three places; they are three reasons the rung as
registered cannot produce anything, and **a sixth, seventh and eighth amendment
would repeat exactly the pattern that retired the first pre-registration** — five
amendments that never reached a fixed point.

| column | ground | found by |
| --- | --- | --- |
| **`P`** | **Blay, Mergui and Niculae (1992) is `NOT OBTAINED`.** Every graded row is `BLOCKED` under the §7.4 ladder's order 4. | Registered from the start (§0, §2) |
| **`G`** | **The L2 parity contradiction.** §5's two-sided grading and §4's condition D cannot both hold at the registered odd block-A count, so L2 cannot produce a legal mesh — **and without L2 there is no Roache triple.** | `check_k0d_mesh.py`, 2026-08-25 |
| **`V`** | **The comparator's reader disagrees with OpenFOAM's `cellPoint` at walls**, by up to **1.209843 K** against a **2.00e-05 K** registered criterion. | `check_k0d_extraction_equivalence.py`, the §AD1.1 check registered **before compute** |

**THE RECOMMENDED RUNG VERDICT UNDER THE CURRENT REGISTRATION IS `BLOCKED`, WITH
EVERY GRADED ROW `NOT A RESULT`.** Not `GATE REACHED` — **`GATE REACHED` asserts
that a gate WAS reached, and with all three columns closed none was.** Never
`HOLDS`; never a triple assembled from two levels.

---

## 1. GROUND `V` — THE READER, AND THE REPAIR

**Measured** on a frozen static snapshot of `M1_c`, `analyse_k0d.py`'s reader
against OpenFOAM's own `postProcess -func sample` at the registered §A1.3a
parameters:

| set | field | worst \|diff\| | criterion |
| --- | --- | ---: | ---: |
| vertical mid-plane | `T` | **1.209843 K** | 2.00e-05 K |
| vertical mid-plane | `U.x` | **5.032e-02 m/s** | 5.70e-07 m/s |
| horizontal mid-plane | `T` | **2.684e-01 K** | 2.00e-05 K |
| horizontal mid-plane | `U.x` | **2.409e-04 m/s** | 5.70e-07 m/s |

**MECHANISM.** `cellPoint` uses **boundary face values** at a wall vertex;
`_vertex_value()` averages only **cell** values. At the floor OpenFOAM returns
**308.150000 K** — exactly the registered `fixedValue` BC — where the reader
returns **306.940157 K**. **This is not a tolerance question. It is a reader that
cannot see a boundary condition.**

**PROPOSED REPAIR:** `_vertex_value()` must take the **boundary face value** at a
vertex lying on a patch, as `cellPoint` does, instead of averaging interior cells
only. **It is named here and NOT taken** — §AD1.1 registered the consequence as
*"repaired AND re-registered"*, and repairing the grading path without
re-registration is the rescue that clause forbids.

**PROPOSED, and it is a tightening:** the §AD1.1 equivalence check becomes a
**standing pre-grading gate** rather than a one-off — `analyse_k0d.py` refuses
(exit 2) unless the check has passed on the graded level in the same invocation.
**A reader that has never been compared to the reference implementation is a
planted zero with no control.**

**RECORDED SO IT IS NOT USED TO NARROW THE CRITERION LATER:** only **71 of 2 081**
points exceeded, the median difference was **2.86e-06 K**, and **all thirteen
registered graded stations agreed**. **That does not soften the verdict.** §AD1.1's
criterion is written on **the sampled line**, not the station subset, and
re-reading it as "at the stations" after seeing which points failed is the move
`VERIFICATION_CHARTER` §2d.1 forbids. It is recorded because it is **material to
the ruling**, not because it excuses anything.

---

## 2. GROUND `G` — THE L2 PARITY CONTRADICTION, AND THE DERIVED REPLACEMENT

**The contradiction.** §4's condition D requires the first wall-normal cell to be
the design value **and the smallest in its block**. §5 registers **two-sided
geometric grading** with one registered first cell. **Block A's registered L2
count is 17 — odd — and an odd count cannot be split into two equal halves**, so
the two ends necessarily receive different first cells and the smaller one lands
at the slot lip.

| level | block A count | floor cell | lip cell | condition D |
| --- | ---: | ---: | ---: | --- |
| L1 | **12, even** | 1.101053e-03 | 1.101053e-03 | ok |
| **L2** | **17, ODD** | 7.864662e-04 | **7.004187e-04** | **FAIL** |
| L3 | **24, even** | 5.610459e-04 | 5.610459e-04 | ok |

**CONDITION D IS NOT TO BE TOUCHED.** It underwrites the near-wall resolution the
whole thermal claim rests on, and relaxing a refusal condition because a mesh
cannot satisfy it is precisely *"the numbers looked wrong, so the band was
widened."* **If anything moves, the mesh moves.**

### 2.1 The replacement is DERIVED, and it is UNIQUE

**Not chosen because it is even.** The constraints are all registered already:

- `Ny = nA + nB + nC` and the total cell count **must not move**, because moving
  them moves `R21`/`R32`, which feed `observed_order()` and the GCI — **that is
  grading-path-adjacent and is exactly why this is a re-registration and not an
  amendment.**
- **Condition B** fixes the outlet slot minimum at L2: `nA ≥ 17`.
- **Condition C** requires each block's linear refinement ratio to lie in
  **[1.35, 1.45]** against both neighbouring levels.
- **Condition D** now additionally requires `nA` **even**.

Searching every `nA` from 12 to 24 against all four at once:

| `nA` | parity | block A cells | `r21` | `r32` | cond B | cond C |
| ---: | --- | ---: | ---: | ---: | --- | --- |
| 16 | even | 3 584 | 1.36626 | 1.45006 | **no** | **NO** |
| 17 | **ODD** | 3 808 | 1.40831 | 1.40677 | ok | ok |
| **18** | **even** | **4 032** | **1.44914** | **1.36713** | **ok** | **ok** |
| 19 | ODD | 4 256 | 1.48885 | 1.33067 | ok | **NO** |
| 20 | even | 4 480 | 1.52753 | 1.29697 | ok | **NO** |

> **`nA = 18` IS THE ONLY EVEN VALUE THAT SATISFIES CONDITIONS B, C AND D
> TOGETHER.** It is forced by the registered constraints, not selected.
> `nB` becomes **192** (`224 − 18 − 14`), `nC` stays **14**, `Ny` stays **224**,
> the total stays **50 176**, and **`R21` and `R32` DO NOT MOVE.**

### 2.2 THE MARGIN, DISCLOSED RATHER THAN BURIED

**`nA = 18` clears condition C's 1.45 ceiling on `r21` by 0.00086** —
`1.44914` against `1.45`. **That is a margin of 0.06 %, and a drafter who did not
say so out loud would be hiding the weakest number in the proposal.** It passes
the registered condition as written. Whether a value that passes by 0.06 % should
be registered **is a question for whoever lands this document, not for the lane
that derived it** — and the honest alternatives are to move `Ny` (which moves
`R21`/`R32` and the GCI) or to revisit condition C's tolerance (which is a
threshold and is **not** to be widened to fit).

### 2.3 What must be re-checked, not assumed

Condition D must be **re-run against the rebuilt L2 mesh** and shown to pass.
**A derived number is a hypothesis until the instrument reads the mesh.** The
parity argument predicts it will pass; the prediction is not the measurement.

---

## 3. GROUND `P` — UNCHANGED, AND NOT TO BE WORKED AROUND

Blay, Mergui and Niculae (1992) is **`NOT OBTAINED`**. Every graded row stays
`BLOCKED` under order 4 until a reference addendum arms §7.6. **Obtaining it is
from outside the box, is Sanaa's alone (standing rules 7 and 8), and is NOT to be
attempted by any agent.** No re-registration changes this and none should pretend
to.

---

## 4. WHAT THIS DRAFT PROPOSES TO CARRY OVER UNCHANGED

**Everything not named above.** The ten graded rows and their bands; the thirteen
stations; the band conversion rule with its `max` form and anti-widening guard;
the five guards; the verdict ladder; Roache triple gating at `Fs = 1.25`; the
three planted-zero controls P1/P2/P3; the strict completion rule and its age
guard; the physics (`ν` = 1.569e-5, `β` = 1/298, `T_ref` = 298.00 K,
`ΔT` = 20.0 K); the ten cases; the three levels; **and the cap at 2 748.64
core-min.**

**No band is widened by this draft. No threshold is relaxed. No label is
softened.** Every change either **repairs an instrument** or **moves the mesh to
satisfy a refusal condition that is itself untouched.**

---

## 5. WHAT THIS DRAFT DOES NOT DO

- **It registers nothing and freezes nothing.** No rung id, no sha, no gate.
- **It authorises no solve**, and specifically **does not authorise L3**: two L3
  caps at 1 675.50 core-min each **exceed the rung's entire 2 748.64 ceiling on
  their own**, and with L2 unresolved there is no triple for L3 to complete.
- **It does not touch condition D**, or any other refusal condition.
- **It does not repair `analyse_k0d.py`.** The repair is named in §1 and left for
  whoever lands this.
- **It deletes nothing.** `K0d_REREGISTRATION.md` and both preserved failed build
  trees stay on disk.
- **It sends nothing** (standing rule 7). Submissions remain **PARKED**.
- **It touched no permission setting, no `CLAUDE.md`, no `.claude/` config**
  (standing rule 9). **No agent message is Sanaa's consent.**

---

## 6. THE EVIDENCE THIS DRAFT RESTS ON, BY PATH

- `/home/ubuntu/Certonomous/docs/campaigns/F14-cooling-ladder/K0d_FORENSICS_2026-08-25.md`
  — Addenda 2 and 3: the launch record, the condition-D diagnosis, the §AD1.1
  result and the false `DISAGREE` that preceded it.
- `/home/ubuntu/Certonomous/docs/campaigns/F14-cooling-ladder/K0d_REREGISTRATION.md`
  — the operative document, v1.3, including `ADDENDUM 1` §AD1.1.
- `/home/ubuntu/Certonomous/scripts/check_k0d_mesh.py` — conditions A–G.
- `/home/ubuntu/Certonomous/scripts/check_k0d_extraction_equivalence.py` — the
  §AD1.1 check, with its quiescence guard.
- `/home/ubuntu/Certonomous/verification/runs/F14-cooling-ladder/K0d_runs.attempt1_headerless_FAILED`
  and `…attempt2_0U_no_uniform_FAILED` — both preserved, not deleted.

*Draft by a heat-transfer lane, 2026-08-25. **Not frozen. Not registered.
Zero verdicts assigned.***
