# MESH_STANDARD §15 — APPEND DRAFT, PREPARED BY VERIFICATION, **TO BE LANDED BY cfd**

> **STATUS: DRAFT. NOT ADOPTED. THIS FILE IS NOT THE MESH STANDARD AND NOTHING IN
> IT IS IN FORCE.** The standard is `docs/standards/MESH_STANDARD.md`; this is
> prepared amendment text awaiting its owner's own read and landing.
>
> **OWNER: cfd-supervisor** — `docs/standards/MESH_STANDARD.md` is cfd's territory
> under `CLAUDE.md`'s roster. **Verification drafted this text and deliberately did
> NOT land it**, holding the same line as `VERIFICATION_CHARTER` §2q: *"I SPEC; I
> DO NOT AMEND"* — a routing that offers the choice does not widen a scope
> (`CLAUDE.md` rule 9). The binding half of this work is committed separately as
> `VERIFICATION_CHARTER` v1.43 **§2r**, which is verification's own file.
>
> **WHY THIS FILE EXISTS AT ALL:** the draft previously lived only in the
> scratchpad, and **`L-186` forbids the scratchpad as a handoff channel** — it is
> shared fleet-wide and has been wiped three times in one day. A draft another
> agent must read lives in the repository. This commit is that durability and
> nothing more.
>
> **⚠ RE-DERIVE BEFORE LANDING, DO NOT TRUST THE FIGURES BELOW.** The line number,
> line count and md5 in the draft header were taken at an earlier HEAD and peers
> commit constantly. The landing agent re-derives the target's line count and
> digest **in the same shell invocation as the commit**, and proves the append
> pure by `md5` of `head -N` against the true parent blob rather than asserting it.
>
> **Verification claims no authorship credit and no veto over edits.** If cfd's own
> read disagrees with any clause here, cfd's judgement governs its own file — with
> the single exception that the text quoting **Sanaa's ruling** must stay verbatim,
> because that is hers and not either team's.

---

DRAFT — NOT COMMITTED. Append VERBATIM at the foot of
/home/ubuntu/Certonomous/docs/standards/MESH_STANDARD.md, after its current
line 1571. Everything below the marker line is the append text.

⚠ ROUTING, UPDATED 2026-09-03 AFTER `fb2d0d39` LANDED. The charter half of this
work is DONE and COMMITTED by the verification-supervisor as VERIFICATION_CHARTER
v1.43 §2r. In that commit the supervisor held, in their own words: "`sdk/` and
`docs/standards/` are OUTSIDE this team's folder scope. I SPEC; I DO NOT AMEND."
So THIS block is NOT verification's to land. It goes to cfd (whose territory
docs/standards/MESH_STANDARD.md is per CLAUDE.md's roster) or to Sanaa.

ALIGNED TO THE COMMITTED §2r. Two rulings in the earlier version of this draft
were STRUCK by the supervisor at fb2d0d39 and are corrected here:
  - a Tier-2 limb failure does NOT make the run `NOT A RESULT`; it refuses the
    CERTIFICATE and reverts the run to Tier-1 treatment (§2r.2 — "bookkeeping
    never voids physics"). Fixed at §15.3 and §15.4.
  - the §2n cause-class referral is DISSOLVED, not answered, and is removed
    from the flag list (there is no `NOT A RESULT` to classify).
Derived at HEAD 6319743d48f3c8830bde6cb37fe8dfc66344ae92:
  file lines before append          = 1571
  md5 of HEAD blob                  = 72cb037d3e2e0224694e102f7a9c0cc8
  md5 of worktree copy              = 72cb037d3e2e0224694e102f7a9c0cc8  (EQUAL — file clean at HEAD)
  max existing section ORDINAL      = 14   -> this block is §15
  max existing section VERSION      = v1.9 -> this block is v1.10
  (§14.x warns explicitly that the ordinal is not the version. Both were
   derived separately, from the file, by grep. RE-DERIVE BOTH IN THE SAME
   SHELL INVOCATION AS THE COMMIT — peers commit constantly.)
========================= APPEND BEGINS ON NEXT LINE =========================

---

## 15. TWO-TIER MESH ADMISSIBILITY — THE 70° GATE IS THE GENERATION STANDARD AND IS UNCHANGED; A WORKSHOP COMMITTEE GRID IS A DIFFERENT OBJECT AND IS ADMISSIBLE FOR VALIDATION-AGAINST-WORKSHOP-DATA WITHOUT MEETING IT (v1.10, 2026-09-03) [SANAA-RULED]

**Lines whose number changed above this section: 0.** Nothing above is edited, reordered,
inserted or deleted — §3.1's 70° hard gate and its 65–70 warning band are not touched in
either direction, and §3.2, §3.3, §6, §7, §8, §9, §10, §11, §12, §13 and §14 are untouched.
Verified by digest, not by assertion — see the closing table.

**This section is [SANAA-RULED] and not this lab's own reading.** Retiring, widening or
narrowing a gate threshold is reserved to Sanaa (CLAUDE.md, FIRST-ACTION RULE). **She does
not widen the 70° gate here and neither does this section.** What she rules is that a
committee grid is a *different object* from a mesh the lab builds, and that the gate which
governs the second does not govern the first.

### 15.1 THE RULING, IN HER OWN WORDS

Sanaa, 2026-09-03 ~17:30Z, verbatim, from
`etc/sessions/2026-09-03T1730Z_sanaa_mesh_standard_and_freeze_enforcement.md:5-20`:

> **Two-tier mesh standard — this resolves the R12 question. The 70° gate
> is our generation standard: every mesh the lab builds must meet it,
> unchanged. Committee grids are a different object: they exist for
> comparability with the workshop's own results, where every participant
> used the same grids. Ruling: committee grids are admissible for
> validation-against-workshop-data cases without meeting the 70° gate,
> under these conditions: (a) their measured quality (max
> non-orthogonality, skewness, the works) is reported on the certificate,
> not gated; (b) solver-side mitigations (non-orthogonal corrector counts,
> relaxation) are registered before running; (c) the numerical-uncertainty
> band still comes from the grid family; (d) the certificate names the
> grid as "workshop committee family, quality as published" in the
> what-was-checked section. A full certificate IS reachable this way — a
> certificate's honesty is disclosure and verification, not our internal
> birth standard. What committee grids can never do is certify our meshing
> capability — that stays on in-house grids under 70°.**

Everything below is mechanics for that text. **Where any sentence below and her text
disagree, her text governs and the sentence below is the defect.**

### 15.2 TIER 1 — THE GENERATION STANDARD. UNCHANGED, AND IT IS THE DEFAULT

> **§3.1's 70° hard gate is the GENERATION standard. Every mesh the lab builds must meet
> it, unchanged.** *(Her words: "The 70° gate is our generation standard: every mesh the
> lab builds must meet it, unchanged.")*

- "The lab builds" means the mesh was produced on this box, or by this lab's invocation of
  any generator — `blockMesh`, `snappyHexMesh`, `pyHyp`, a hand-written `blockMeshDict`, or
  a public generator driven from a namelist **this lab wrote or modified**.
- **Tier 1 is the default.** A mesh is Tier 2 only if it is *declared* Tier 2 at
  pre-registration under §15.3 and meets every condition there. **There is no implicit
  Tier 2, and no mesh becomes Tier 2 after its quality is measured.** A grid promoted to
  Tier 2 after a Tier-1 reading came back over 70° is the shape rule 2 exists to forbid.
- **A modified namelist does not make a committee grid.** This is the point on which M6I
  already failed R12, measured and on record: M6I was produced by invoking the public
  generator once with `target_y_plus` moved 1.0 → 0.25 and three counts doubled
  (`docs/LAB_STATE.md:21964`). Under §15.3(0) it is Tier 1 and its L1/L2/L3 readings of
  **87.7462° / 86.4646° / 87.6620°** (`verification/runs/M6I_runs/{L1,L2,L3}/log.checkMesh:91`)
  are **breaches of §3.1**, not disclosures under §15.3.

### 15.3 TIER 2 — WORKSHOP COMMITTEE GRIDS. A DIFFERENT OBJECT, WITH ITS OWN ADMISSION TEST

> **A workshop committee grid is admissible for a validation-against-workshop-data case
> without meeting the 70° gate**, when **all five** of (0) and (a)–(d) hold.

**WHAT HAPPENS WHEN A LIMB FAILS — governed by `VERIFICATION_CHARTER` §2r.2, not by this
section, and quoted here so the two documents cannot drift:**

> **A TIER-2 LIMB FAILURE REFUSES THE CERTIFICATE. IT DOES NOT VOID THE PHYSICS.** The run
> does not become `NOT A RESULT`; it **reverts to Tier-1 treatment** — a generation-standard
> breach, the numerical channel carrying it, the fidelity chip capped, and no validated
> force claimed from that mesh. **A disclosure this lab failed to make is a statement about
> our record, not about what the solver computed.**

That is Sanaa's universal rule *bookkeeping never voids physics* (2026-08-26) applied where
it points. **A missing registration heading, an absent substring, a sha never recorded —
these are bookkeeping.** No §2n cause class arises, because no `NOT A RESULT` arises.

**(0) THE OBJECT TEST — what actually is a committee grid.** *(Her ground: "they exist for
comparability with the workshop's own results, where every participant used the same
grids.")* All four:

1. The grid was **published and distributed by the workshop committee itself** — named
   body, named workshop, named grid family, named level, with the URL or the archive it
   came from.
2. It is **byte-unmodified from what was distributed**, apart from format conversion. The
   pre-registration records the sha-256 of the distributed file and of the converted
   `polyMesh`, and states the converter and its version.
3. **Other participants ran this same grid** — that is the comparability the exemption
   buys. A grid nobody else used buys nothing and is Tier 1.
4. The **case is a validation against that workshop's own data.** *(Her scope:
   "admissible for validation-against-workshop-data cases".)* This exemption does not
   travel to any other case type — and note it is a **narrower** grant than R12's on this
   axis and a **wider** one on the certificate axis; see §15.8.

**(a) MEASURED QUALITY REPORTED, NOT GATED.** *(Her words: "their measured quality (max
non-orthogonality, skewness, the works) is reported on the certificate, not gated".)*
The certificate carries, as measured numbers with the artifact each is read from:
max non-orthogonality; the **count of severely non-orthogonal (>70°) faces** and that count
as a fraction of total faces (§14's clause — the maximum alone hides the propagation);
max skewness and its highly-skew face count; max aspect ratio; cell count; face count; and
every other quantity `checkMesh` reported. Read per §14.4: **off the reported maxima,
never off `Non-orthogonality check OK.` and never off `Mesh OK.` / `Failed N mesh checks.`**
**"Not gated" means the row carries no pass/fail verdict and no gate comparison** — not
that a comparison is made and hidden, and not that the gate is moved to make it pass. A
certificate that prints `89.71° vs 70° gate — pass` has laundered the exemption into a
false measurement and is worse than one that fails.

**(b) SOLVER-SIDE MITIGATIONS REGISTERED BEFORE RUNNING.** *(Her words: "solver-side
mitigations (non-orthogonal corrector counts, relaxation) are registered before running".)*
Operational form in §15.4 — that subsection is what a grader checks.

**(c) THE NUMERICAL-UNCERTAINTY BAND STILL COMES FROM THE GRID FAMILY.** *(Her words: "the
numerical-uncertainty band still comes from the grid family".)* Operationally:

- The band is a **Roache triple over three levels of the SAME committee family**, graded
  under CLAUDE.md rule 5 in full. **Rule 5 is not relaxed by one word here:** a triple that
  is not `CONVERGING` is `NOT A RESULT`, whatever the value; no GCI is quoted on
  non-monotone values; GCI at Fs = 1.25. §9.1's three-level requirement stands.
- **The band may NOT be imported from the workshop's published scatter, from another
  family, or from a single level.** A published scatter is other people's result, not this
  lab's measurement, and substituting it is exactly the "reference caps the tier" confusion
  §2n class 6 names.
- **A committee family that does not publish three levels cannot satisfy (c) and therefore
  cannot reach a full certificate.** That is a real and expected outcome, and it is stated
  here so nobody discovers it after the compute is spent.

**(d) THE CERTIFICATE NAMES THE GRID.** *(Her words: 'the certificate names the grid as
"workshop committee family, quality as published" in the what-was-checked section'.)*
Operational form, including the literal string, in §15.5.

### 15.4 CONDITION (b), MADE OPERATIONAL — WHERE THE REGISTRATION LIVES AND WHAT IT NAMES

> **THE HOME.** The registration lives in **the case's own pre-registration**, the one
> named by `prereg_path` in the queue entry and frozen at `prereg_commit`, under a section
> whose heading is **exactly**:
>
> ```
> ## SOLVER-SIDE MITIGATIONS REGISTERED FOR A COMMITTEE GRID (MESH_STANDARD §15.4)
> ```
>
> It lives **nowhere else**. Not in the queue entry's free-text annotations, not in a
> RESULTS file, not in a lane report, not in `docs/LAB_STATE.md`, and **never in the
> scratchpad** (CLAUDE.md rule 13). Rule 2 governs it in full: it is written **before the
> solver starts**, frozen by sha, and after first compute it can be corrected only by a
> dated addendum that alters no gate, threshold, cap or label.

**WHAT IT MUST NAME — one row per mitigation, all six columns, no blanks:**

| # | column | what it must carry |
|---|---|---|
| 1 | **dictionary file** | path relative to the case root, e.g. `system/fvSolution` |
| 2 | **keyword** | the exact keyword, e.g. `nNonOrthogonalCorrectors` |
| 3 | **registered value** | the exact value that will run |
| 4 | **counterfactual** | the value this lab would use on a §3.1-compliant grid — so the SIZE of the mitigation is on the record, not just its existence |
| 5 | **what it mitigates** | which measured quality number (from (a)) it answers, by value |
| 6 | **blob sha at freeze** | `git rev-parse <prereg_commit>:<path>` for the file in column 1 |

**THE MINIMUM SET, because "registered" must not mean "whatever we happened to write
down".** A Tier-2 registration is incomplete unless it carries a row — a row stating the
default and *why no change was needed* is a legitimate row — for **each** of:

- `nNonOrthogonalCorrectors` (or the solver's equivalent corrector count);
- the surface-normal-gradient scheme in `system/fvSchemes` (`corrected` /
  `limited <c>` / `uncorrected`) **and its coefficient**;
- the Laplacian scheme and its non-orthogonal treatment;
- every entry under `relaxationFactors` that differs from the case's own compliant-grid
  baseline;
- any wall-treatment or limiter switched on because of this grid.

**WHY (b) IS THE CONDITION THAT WILL ACTUALLY BITE, and it is not a hypothetical.** This
lab has already measured what a committee grid does to a solver: on the HLPW6 coarse grid,
**twenty second-order configurations all diverged inside 29 iterations** and only first
order completed (`docs/DOCKET.md:618`, D253; corroborated at
`docs/inventory/2026-08-24/LAB_INVENTORY.md:57`, *"second-order diverges at iteration 16,
only first order completes"*). That record's own conclusion is the point: it hardened
*"a numerics problem"* into **a discretisation problem**. **Solver-side mitigation is not a
formality on these grids — it is the whole of what makes them solvable, which is exactly
why Sanaa requires it registered BEFORE the run rather than described after it.**

**AND IT MUST BE PROVEN ACTIVE, NOT MERELY PRESENT.** Charter §9's lever-activity clause
(v1.5, L-40) applies with full force and is the half that makes this checkable: **each
registered mitigation must be shown ACTIVE in the runtime log of the run being graded**,
not merely present in the input dictionary. A registered corrector count that the solver
never exercised is not a mitigation; it is a sentence.

**HOW A GRADER CHECKS IT — five mechanical steps, no judgement:**

1. `git show <prereg_commit>:<prereg_path>` contains the §15.4 heading **verbatim**.
2. The table under it has **≥ 1 row** and **no blank cell**, and covers the minimum set.
3. For every row, `git rev-parse <prereg_commit>:<column-1 path>` **equals column 6**.
4. For every row, the dictionary file **as it ran** carries column 2 = column 3.
5. For every row, the runtime log shows the lever **active** (§9 lever-activity).

**Any step failing → the grid was not admitted → the CERTIFICATE is refused and the run
reverts to Tier-1 treatment** (`VERIFICATION_CHARTER` §2r.2, quoted at §15.3). **The
physics is not voided and no §2n cause class arises.**

**PLANTED CONTROL.** The §15.4 check is a reader and CLAUDE.md rule 3 binds it: it must be
shown, in the same run, able to see a **non**-compliant registration — plant a row with a
wrong blob sha, or a lever the log does not show active, and prove the check refuses.
**A check that has only ever returned "registered" is not evidence that anything was.**

### 15.5 CONDITION (d), MADE OPERATIONAL — THE LITERAL STRING, AND WHERE IT GOES

> **THE LITERAL STRING, to be carried verbatim, case-sensitive, as a contiguous substring:**
>
> ```
> workshop committee family, quality as published
> ```
>
> **THE FIELD.** It goes in the certificate's **what-was-checked section**. In the lab's
> current generator that is the **`scope` field** — `sdk/chief_engineer/certificate.py`,
> the `scope` parameter of `build_certificate_v2` (documented at :1032 as *"a labelled
> field, not fine print: it states what was actually [checked]"*, rendered as the **Scope**
> row at :1188-1189 and sealed with the run at :603-604). If a future certificate form
> renames that field, the string moves with the *function*, never off the page.

**THE FULL SENTENCE THE STRING SITS IN — the required form:**

```
Grid: workshop committee family, quality as published — <BODY> <WORKSHOP> <FAMILY>
level <LEVEL>, distributed <URL-or-archive>, sha-256 <DIGEST>. Measured quality is
reported, not gated, under MESH_STANDARD §15.3(a); this grid was not built by this lab
and is not evidence of this lab's meshing capability (§15.7).
```

**A grader checks (d) by substring.** The literal string is present in the certificate's
scope field, or condition (d) fails and the certificate does not issue. **It is a
substring test, not a paraphrase test**, precisely so that no lane has to decide whether
its own wording was close enough.

**"Quality as published" is a claim and it is checkable.** The pre-registration cites the
committee's own published quality figures for that grid, and the certificate reports this
lab's measured figures beside them. **Where they disagree, both are printed and the
disagreement is named.** A grid whose measured quality does not match its published
quality is a **finding**, not a rounding note — and it is the one thing that could show the
distributed file and the converted mesh are not the same object.

### 15.6 A FULL CERTIFICATE IS REACHABLE THIS WAY — AND THIS IS THE PART THAT CHANGES

> **Her ruling, verbatim: "A full certificate IS reachable this way — a certificate's
> honesty is disclosure and verification, not our internal birth standard."**

That sentence is the operative change and it is stated plainly rather than buried:
**a Tier-2 grid meeting (0) and (a)–(d) is not capped, not chipped down, and not confined
to a model-form band.** It can carry a `PASS`, a full certificate, and the lab's ordinary
verdict vocabulary, on the same terms as any other admissible mesh.

**And the reason matters more than the permission**, because it is what stops the next
lane reading this as a loophole: *a certificate's honesty is disclosure and verification,
not our internal birth standard.* Tier 2 does not lower the evidence bar — it **relocates**
it. Where Tier 1 buys confidence by controlling how the mesh was born, Tier 2 buys it by
**disclosing exactly what the mesh is** (condition a), **registering in advance what was
done about it** (condition b), **measuring the numerical band on that same family**
(condition c), and **naming the object on the certificate's face** (condition d). Four
disclosures replace one birth standard. **A Tier-2 certificate that is missing any of the
four is not a weaker certificate; it is not a certificate.**

### 15.7 THE HARD LIMIT — A COMMITTEE GRID CAN NEVER CERTIFY THIS LAB'S MESHING CAPABILITY

> **Her words, verbatim: "What committee grids can never do is certify our meshing
> capability — that stays on in-house grids under 70°."**

> **CLAUSE. No Tier-2 grid, and no result obtained on one, may be cited as evidence of this
> lab's meshing capability** — not in `docs/CAPABILITY_GRID.md`, not in a credentials-wall
> entry, not in the capability register, not in a certificate's capability claim, and not
> in a report upward. **Meshing capability is certified on in-house grids meeting §3.1,
> and on nothing else.** *"Never" is her word and it takes no exception.*

The distinction is exact and is worth stating in one line: **a Tier-2 certificate certifies
the PHYSICS this lab computed; it certifies nothing about the MESH this lab did not
build.** Importing a grid faithfully is an import capability (that is what the mesh-import
register row certifies — fidelity), and it is not a meshing capability.

### 15.8 SUPERSESSION — THIS RESOLVES THE R12 QUESTION AS PUT, AND THE QUESTION IS QUOTED

> **Her words, verbatim: "Two-tier mesh standard — this resolves the R12 question."**

**THE QUESTION AS PUT.** It was put by the cfd-supervisor in board 47 of
`docs/LAB_STATE.md`, section heading at **:21961**, under a heading that is itself the
claim:

> **`### 🔴 R12 DOES NOT REACH A CERTIFICATE, AND M6I DOES NOT EVEN QUALIFY FOR R12`**

and, verbatim, at **`docs/LAB_STATE.md:21963-21966`**:

> - `MESH_STANDARD.md:73-82` and ruling R12: *"physics gates and credential verdicts still
>   require compliant meshes -- this exemption never travels to them."* Rung 1's deliverable
>   is pressures against tunnel data = a physics gate. **R12 buys a MODEL-FORM BAND ONLY.
>   Sanaa's "full certificate" is NOT reachable on an R12-exempted grid.**
> - **M6I does not qualify:** R12 covers *"the reference community's OWN CANONICAL
>   verification grid"*. M6I was produced by invoking the public generator ONCE with a
>   namelist **this lab modified** (`target_y_plus` 1.0 -> 0.25, three counts doubled).
>   Reaching R12 needs an actually-distributed canonical family — **a NEW import, gated by
>   Rung 0.**
> - **A band costs MORE, not less, and inverts the shape:** [...] **Three models on one
>   grid, not one model on three grids.**
> - **This is verification's call to confirm or overturn, not cfd's.**

It stands on that board's own measured exhibit at **`docs/LAB_STATE.md:21918-21932`** —
*"FIVE OF FIVE COMMITTEE GRIDS EVER IMPORTED ON THIS BOX BREACH SECTION 3.1 BY 17-20
DEGREES"* — and it was carried to Sanaa's desk as item 3, **`docs/LAB_STATE.md:22006`**:
*"**The committee-grid admissibility wall** — governs Rungs 1, 2 and 3 together."*

**HOW IT IS RESOLVED — and it is resolved by SUPERSESSION, not by an answer.** cfd asked
whether R12 reaches a certificate. **Sanaa did not answer that question; she replaced the
instrument.** R12 is a *narrow exemption to a gate*; §15 is a *two-tier standard* in which
the gate never applied to the object in the first place. The consequences, stated so nobody
has to infer them:

| the question as put | how §15 disposes of it |
|---|---|
| *"R12 buys a MODEL-FORM BAND ONLY"* | **CORRECT ABOUT R12, and R12 is no longer the governing instrument.** §15.6 makes a full certificate reachable on a Tier-2 grid. cfd's reading of R12 is not overturned — it is superseded. |
| *"Sanaa's 'full certificate' is NOT reachable on an R12-exempted grid"* | **True of an R12 exemption; false of a §15 Tier-2 grid.** The two are different objects with different conditions. |
| *"M6I does not qualify"* | **UPHELD, and on stronger ground.** §15.3(0)(2) requires byte-unmodified distribution; M6I's namelist was modified by this lab. M6I is **Tier 1** and its 87.7462° L1 reading is a §3.1 breach. |
| *"a band costs MORE ... three models on one grid, not one model on three grids"* | **MOOT under §15, and inverted.** §15.3(c) requires the numerical band from **the grid family** — three levels of one family. The band-of-models route was R12's shape; it is not §15's. |
| *"This is verification's call to confirm or overturn, not cfd's"* | **Neither. Sanaa ruled it.** It was above both teams, and §15 records it as hers. |

**R12 IS NOT RETIRED BY THIS SECTION AND ITS TEXT IS NOT EDITED.** Retiring a standard or a
ruling is reserved to Sanaa (CLAUDE.md, FIRST-ACTION RULE) and she did not retire it. R12
continues to govern the object it names — *model-form banding on a reference community's own
canonical verification grid* — and its three mandatory conditions are unchanged.
**§3.1's R12 pointer at lines 73–82 is likewise NOT edited**, because editing it would move
every line number below and this section asserts that none moved. **A reader arriving at
§3.1:73-82 must read §15 with it**, and every future citation of R12 in a
validation-against-workshop-data context is **non-conforming** and must cite §15 instead.
⚠ Where R12 and §15 could both be read to reach the same grid, **the overlap is flagged in
§15.9 item 1 and not resolved here.**

### 15.9 WHAT THIS SECTION DOES NOT DO — AND FOUR COLLISIONS FLAGGED, NOT DECIDED

- It **changes no gate value**. §3.1's 70°, its 65–70 band and its action clause are
  untouched; §3.2's skewness 4 and §3.3's aspect-ratio advisory are untouched. Nothing is
  written to `docs/physics_rules.yaml` and §5's change control is not invoked, **because no
  gate value changes.**
- It **retires nothing** and **re-grades nothing**. No existing verdict moves.
- It creates **no** general exemption. Tier 2 reaches **validation-against-workshop-data
  cases on distributed committee grids** and nothing else.
- It does **not** make any grid currently on this box Tier 2. **No grid has been declared
  Tier 2, because a declaration is made at pre-registration and none exists.**

**⚠ FOUR COLLISIONS, NAMED AND REFERRED — this section decides none of them.** *(A fifth, the §2n cause class for a limb failure, was DISSOLVED rather than answered by `VERIFICATION_CHARTER` §2r.2: there is no `NOT A RESULT` to classify.)*

1. **R12's scope overlaps §15's.** A distributed canonical committee grid used for
   model-form banding satisfies R12; the same grid used for validation-against-workshop-data
   satisfies §15. **Which instrument governs a case that is both is not ruled here.**
2. **The birth-certificate machinery does not implement §3.1 at all, and it will
   quarantine Tier-2 grids on SKEWNESS.** Measured, not asserted:
   `sdk/chief_engineer/mesh_certificate.py:44` sets `ACCEPTED_VERDICTS = ("clean",
   "flagged")` and `:47-57`'s `_HARD_ERRORS` fires on the literal `***Max skewness`. Every
   DPW5 committee grid prints it —
   `cases/committee-grids/logs/DPW5_hex_checkMesh.log:109` (`***Max skewness = 14.0594`),
   `DPW5_prism_checkMesh.log:107` and `DPW5_hybrid_checkMesh.log:107` (both
   `***Max skewness = 6.31513`) — so all three are born **`broken`** and
   `certificate_admits()` (:249-274) refuses them entry to a case. **Sanaa's (a) says
   quality is reported "not gated"** and names skewness in her own parenthesis, **but she
   did not name this machinery**, and reading her ruling onto a code path she did not
   mention is the permission laundering rule 9 forbids. **Referred.**
   *(The same measurement shows the converse hazard: these logs print
   `Non-orthogonality check OK.` at 89.71°, 89.94° and 89.9985° — §14.4's finding, live on
   the exact grids this section governs.)*
3. **`_mesh_rows()` has no "reported, not gated" mode.**
   `sdk/chief_engineer/certificate.py:936-999` renders max non-orthogonality as
   `"{v}° vs {gate}° gate"` with a `pass`/`caveat` verdict and no way to suppress it. The
   only lever is the `non_orthogonality_gate` key, and **raising it to force a `pass` would
   print a false measurement** — worse than the breach. **Condition (a) is not satisfiable
   by the current generator without a code change in `sdk/`, which is outside this team's
   folder scope.** Specced, not written. **Referred.**
4. **THE CAPABILITY GRID CARRIES A `CAN NOT DO` WHOSE STATED CAUSE IS THIS GATE, AND IT IS
   A GENERATED FILE.** `docs/CAPABILITY_GRID.md:75` and `docs/capability/cfd_GRID.md:74`
   and `:200` record **3D · steady · transonic** as *"**CAN NOT DO** — attempted 2 cases,
   both `GATE FAIL` at mesh admission on the 70° non-orthogonality gate"*, and the same
   cell names the CRM committee grids (DPW5 / HLPW6) among its evidence. **The verdict
   itself appears to survive §15 on its own facts** — F13 and F1 are in-house Tier-1 builds
   (84.64 / 86.02 / 86.78° and 81.94 / 83.88 / 83.64°, genuine §3.1 breaches) and the
   committee grids in that cell were *"conversion and feasibility probes only, no solve
   graded"* — **but its stated CAUSE is now partly superseded**, since a committee grid is
   no longer barred from that cell by the 70° gate alone. **Two reasons this section does
   not touch it:** the file is **GENERATED** (`scripts/assemble_capability_grid.py`; a hand
   edit is overwritten — `VERIFICATION_CHARTER` §2n.12), and **§15.7 makes the capability
   surface the one place a Tier-2 grid may NEVER be cited**, so an edit there is exactly
   the move that needs a ruler rather than a lane. **Referred.**
   *(Found in the same sweep and NOT a collision, recorded because it is the waiting
   customer: `verification/campaign/NEXT_CASES_SLATE.md:62` slates
   `w1-dpw5-hex-three-level-ladder` at 400 core-min, and `:263` states its mesh source as
   **"committee grids, not ours — which is the whole point"**. A three-level ladder on one
   committee family is §15.3(c)'s exact shape. **No grid is declared Tier 2 by this
   section, that one included.**)*

| assertion | value |
|---|---|
| ruling authority | **[SANAA-RULED]**, 2026-09-03 ~17:30Z, quoted verbatim at §15.1 |
| gate values changed by this section | **0** |
| gates · thresholds · bands · caps · labels created, moved or retired | **0 · 0 · 0 · 0 · 0** |
| rulings retired | **0** (R12 is superseded in scope, not retired; its text is not edited) |
| results re-graded | **0** |
| grids declared Tier 2 by this section | **0** |
| solver compute | **0 core-min, $0.00** |
| collisions flagged and NOT decided | **4** (§15.9); a fifth DISSOLVED by `VERIFICATION_CHARTER` §2r.2 |
| **lines whose number changed above this section** | **0** |
| md5 of this file's HEAD blob before the append | `72cb037d3e2e0224694e102f7a9c0cc8` |
| md5 of this file's first 1,571 lines after the append | *(RE-DERIVE AT COMMIT)* |
| the two digests | *(assert EQUAL — MEASURED, in the commit's own shell invocation)* |
