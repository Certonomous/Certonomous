# T20_LC_P10 — `DEAD_LEVER_AUDIT.md` §26.6 conditions, MEASURED

**Status: THE ENTRY DID NOT LAND ON THIS PASS.** Condition **(iii) PASSED** by
measurement. Condition **(c)/(ii) FAILED** by measurement, on the bytes that would
have landed. §26.6 makes all four conditions binding, so the landing stops here.

**NO SOLVER RAN.** Zero core-minutes of solver compute. `T20_LC_P10` HAS NOT RUN.
No compute is authorised by §26 (§26.7 is explicit) nor by `4e5cd6c0`
(`VERIFICATION_CHARTER` §2d.3.5: *"I rule the REPAIR LEGAL. I do not authorise
COMPUTE."*). **T20 remains `NOT A RESULT` on its own registered terms**, because
`S12` verdict-map row **V5** (`T20_PREREGISTRATION.md:1062`, frozen at `7b93b2c8`)
makes a refusal on the planted arm a whole-rung `NOT A RESULT`, and V5's planted
arm has not executed.

Grant read at source: `docs/DEAD_LEVER_AUDIT.md` §26, committed at **`0d7dfd41`**.

---

## 1. CONDITION (iii) — THE DEAD-LEVER DEMONSTRATION: **THE TREES DIFFER. YES.**

> §26.6(iii): *"Build `T20_LC_P10` and `T20_LC_f` … and show the two trees **DIFFER**,
> with P10's `fvOptions` explicit source reading **5500** and `T20_LC_f`'s reading
> **5000**. If the built trees are byte-identical, the entry is a dead lever and
> MUST NOT LAND — however perfect its citations."*

Both trees were built **in scratch, outside the rung tree**, through
`build_t20c.py`. `LIVE_TREE_PLANTED_INTERLOCK` (`build_t20c.py:125`, enforced
`:338`) was **NOT lifted** and was not touched. `T20_registered.json` sha256 was
`e04c6a64c3920e3e…` before **and after** both builds — the registration was not
written. `__pycache__` was cleared before the builds.

- P10: `build_t20c.py --case T20_LC_P10 --root <scratch>/rootP10 --params <scratch>/p10_params.json --planted-source 5500`, rc 0.
  The params file is `queue_drafts/T20_LC_P10_CANDIDATE_ENTRY.json` → `entry`, copied verbatim.
- `T20_LC_f`: `build_t20c.py --case T20_LC_f --root <scratch>/rootF`, rc 0, no override.

### The byte comparison, every emitted file

| measurement | value |
|---|---|
| files emitted, P10 tree | **19** |
| files emitted, `T20_LC_f` tree | **19** |
| files **common** to both | **19** (only-in-P10 `[]`, only-in-f `[]`) |
| common files **byte-identical** | **16** |
| common files **DIFFERING** | **3** |

The three that differ, exhaustively:

| file | P10 | `T20_LC_f` | what the difference is |
|---|---:|---:|---|
| `constant/cellRegion/fvOptions` | 1122 B | 1122 B | **THE PLANT.** One line: `explicit    constant 5000;` → `explicit    constant 5500;` |
| `CASE.txt` | 1446 B | 870 B | provenance: `build_t20c.py`'s append-only override disclosure |
| `log.blockMesh` | 3182 B | 3166 B | **2 lines, both `PID    : <n>`** — process metadata, nothing else |

**The two `fvOptions` files are the SAME BYTE LENGTH, 1122 bytes on both sides** —
the delta is the value token and nothing structural.

- P10 `fvOptions` source token, quoted: **`explicit    constant 5500;`**
- `T20_LC_f` `fvOptions` source token, quoted: **`explicit    constant 5000;`**
- sha256 P10 `fvOptions`: `be26da2077e3da7c…` · sha256 f `fvOptions`: `4a3e3ef059411e29…`

The 16 byte-identical files are the whole of the physics apart from the source:
`constant/cellRegion/polyMesh/{points,faces,owner,neighbour,boundary}`,
`0.orig/cellRegion/{T,p}`, `constant/cellRegion/thermophysicalProperties`,
`constant/g`, `constant/regionProperties`,
`system/cellRegion/{blockMeshDict,fvSchemes,fvSolution}`,
`system/{controlDict,fvSchemes,fvSolution}`.

**That is `S7.2 :793-794`'s *"identical case … and nothing else changed"*
demonstrated over emitted bytes rather than asserted.**

> ### ANSWER TO §26.6(iii): **YES — THE TREES DIFFER.** The lever is LIVE.
> The byte-identity the stop record named as the dead lever is **absent**:
> `build_t20c.py` reaches the source token and moves it, and moves nothing else a
> solver reads.

---

## 2. CONDITION (c)/(ii) — **FAILED. THE CERTIFIER CANNOT SEE `T20_LC_P10` AT ALL.**

> §26.6(ii): *"(c) UNCHANGED. The comparator **REFUSES, not reports**, and the
> planted control is driven with **BOTH limbs** on the bytes that actually land:
> corrupt a value and prove it fires, restore it and prove it goes silent."*

Driven on a scratch copy of `T20_registered.json` **with the candidate P10 entry
installed** — i.e. on the bytes that would actually land — through
`check_t20_transcription.py`'s own `check()`:

| planted corruption in the installed **P10** entry | checker rc | verdict |
|---|---:|---|
| uncorrupted, P10 installed | 0 | silent |
| `P10.point_core_min` + 1e-09 | **0** | **SILENT** |
| `P10.timeout_s` + 1 s | **0** | **SILENT** |
| `P10.cost_source_section` removed | **0** | **SILENT** |
| `P10.cells` 240 → 999 | **0** | **SILENT** |

**Four planted mistranscriptions, four silences. The comparator certifies nothing
about P10.**

### The zero is NOT a blind zero — a live control was planted beside it (rule 3)

The **identical** mutation, in the **same file**, through the **same reader**, in the
**same invocation**:

| mutation | checker rc | messages |
|---|---:|---|
| `timeout_s` + 1 on **`T20_LC_f`** | **2 — FIRES** | `T20_LC_f.timeout_s MISTRANSCRIBED: registration has 109, prose has 108` **and** the `24.4(b)` single-rule limb |
| `timeout_s` + 1 on **`T20_LC_P10`** | **0 — SILENT** | none |

The reader was shown able to see a non-zero on the very same file. It is live, and
it simply cannot reach P10.

### The cause, located in code — not inferred

`check_t20_transcription.py:102` opens the loop that carries **every** substantive
limb — byte-equality against the frozen prose, condition **(a)** evidence-kind, and
condition **(b)** the single timeout rule:

    for case, pv in sorted(pcases.items()):

`pcases` is `T20_prose_cases_7b93b2c8.json` → `cases`, which holds exactly five
names: `T20_LC_D`, `T20_LC_Sc`, `T20_LC_Sf`, `T20_LC_f`, `T20_LC_m`. **`T20_LC_P10`
is not among them — it lives under that file's `_stopped` block**, where §24.4(a)
put it. The only limb that reaches P10 is (e), the ceiling and membership check at
`:94-100`, and that passes cleanly: P10 **is** one of `S11_2_ROWS` and seven is the
ceiling.

**So installing P10 into `T20_registered.json` alone would land a registered case
that the certifier is structurally blind to — an entry whose checker is connected to
nothing. That is the same failure class this audit file is named for, displaced one
level: not a dead lever in the builder, a dead limb in the comparator.** It is
precisely what §26.6(ii) exists to prevent, and it is why the landing stops.

---

## 3. WHAT WAS VERIFIED AND HOLDS — recorded so the next pass need not re-derive it

**Condition (b) — `timeout_s`, the one rule, unvaried.** `cap_core_min × 60 / ranks`
= **1.80 × 60 / 1 = 108 exactly**. The candidate carries `timeout_s: 108` and the
derivation string in the same fixed form the installed `T20_LC_f` entry uses
(`T20_registered.json:113`, cap 1.80 → 108; and `T20_LC_c`'s precedent at `:69`,
cap 0.80 → 48). The rule does not vary by case.

**Condition (a)/§24.5 — the five citations resolve at `7b93b2c8`, against P10's OWN
rows.** Read from the **committed blob** (`git cat-file blob
7b93b2c8:docs/campaigns/T-family/T20_PREREGISTRATION.md`), not the worktree:

| field | citation | resolves at `7b93b2c8` to |
|---|---|---|
| `mesh_source_section` | S9 `:873`, S11.2 `:1017`, S6.3 | `:873` `` `T20_LC_P10` \| base \| 240 \| 1.5 \| 4500 \| 3000 \| planted **+10 %** source \| **Q3 planted arm** ``; `:1017` `` `T20_LC_P10` \| 240 \| 3000 \| 0.1584 \| 1.80 ``; `:685` `` **base (`c`,`m`,`f`,`D`,`P10`)** \| **20 × 12** \| **240** \| **2.5** `` |
| `ladder_source_section` | S9 `:873`; S7.2 `:793-794` | `:873` deltaT 1.5 / endTime 4500; `:793-794` *"identical case with `fvOptions` explicit source `5500` (= 5000 × 1.10) and **nothing else changed**"* |
| `executiontime_source_section` | S9 `:873`; S11.2 `:1017` | 3000 steps both rows |
| `cost_source_section` | S11.2 `:1017` | 240 cells, 3000 steps, POINT 0.1584, CAP 1.80 |
| `graded_source_section` | S9 `:873` `graded` column | `**Q3 planted arm**` |

**None of the five points at `T20_LC_f`'s rows** (`:869`, `:1013`). A citation that
resolves at the sha but certifies another case's row is barred by §24.5, and that
trap is avoided.

---

## 4. WHY THIS LANE DID NOT CURE (c) ON ITS OWN AUTHORITY

Two cures exist and **both are above a lane**:

1. **Extend `check_t20_transcription.py` to cover a case absent from the prose
   file's `cases` block.** That is an instrument change, and **§26.6(iv) says
   "no second instrument pass"** — the cure would breach the condition it serves.
2. **Move `T20_LC_P10` from `T20_prose_cases_7b93b2c8.json` → `_stopped` into that
   file's `cases` block**, so the existing limbs reach it. This touches no code, and
   it is the same mechanical transcription §24 licensed for the other five. But it
   rewrites **the very file the certifier treats as authoritative**, and it was not
   in this lane's brief. Authoring both sides of a comparison is the shape that
   turns a check into a tautology unless the prose side is derived independently
   from the frozen blob — a judgement that belongs to the supervisor, and the
   referral to verification, not to the lane that benefits from it.

**A grant is not a licence to satisfy a condition by moving the condition.**
§26.7 rebuked precisely the widening of an approval past what was approved
(`CLAUDE.md` rule 9). (iii) passing does not carry (c).

---

## 5. INSTRUMENT HEALTH AFTER THE MEASUREMENT

Run against the **unchanged** registration (sha256 `e04c6a64c3920e3e…`, identical
before and after everything above):

| instrument | result | rc |
|---|---|---:|
| `build_t20c.py --selftest` | **30 limbs, 30 `ok`, 0 `FAIL`**, `SELFTEST PASS` | **0** |
| `mutation_controls_t20c.py` | **12 controls, 0 of 12 misbehaved** | **0** |
| `check_t20_transcription.py --selftest` | `SELFTEST PASS (0 failed)` — both planted limbs live | **0** |
| `check_t20_transcription.py` (live) | `CERTIFIED: **5** transcribed case(s)` | **0** |

That live line reads **five**, not six or seven. **The certifier states its own
coverage, and P10 is outside it.**

## 6. COST — ESTIMATE VERSUS ACTUAL (`CLAUDE.md` rule 12)

**Solver compute: 0 core-minutes. `T20_LC_P10` HAS NOT RUN and no run was queued.**

The only compute incurred was the §26.6(iii) build, which the grant itself
pre-estimates as *"approximately zero core-minutes"*. **Actual, measured:** one case
build = **0.25 wall s × 1 rank = 0.0042 core-min**; the demonstration is two builds
= **0.0083 core-min**. Ratio actual/predicted is not meaningful against a
predicted "approximately zero" and is **not fabricated here**; the honest statement
is that the actual sits in the same order the grant named. No waste, no contention,
no overrun. USD **DERIVED, NOT MEASURED**: **$0.0000071** at the owner-stated
$0.0513/core-h (REPORTED-BY-OWNER 2026-08-21/22 — the box cannot read its own
billing, `COMPUTE_BUDGET_CHARTER` §5).

P10's own registered cost is untouched and unspent: POINT **0.1584** core-min, CAP
**1.80** core-min (`S11.2 :1017`), inside the frozen rung TOTAL CAP **16.0** core-min
(`:1018`).

---

*Recorded by the heat-transfer lab-lane, 2026-08-31, on the heat-transfer
supervisor's brief. `T20_registered.json` WAS NOT WRITTEN. No frozen file was
edited. No interlock was lifted. No solver ran.*
