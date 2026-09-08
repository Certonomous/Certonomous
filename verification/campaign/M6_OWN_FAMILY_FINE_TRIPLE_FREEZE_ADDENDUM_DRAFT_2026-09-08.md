# DRAFT — FREEZE ADDENDUM to M6_OWN_FAMILY_FINE_TRIPLE_PREREGISTRATION.md (grading-path re-pin)

> **THIS IS A DRAFT FOR THE cfd-SUPERVISOR TO REVIEW AND APPLY. IT IS NOT APPLIED.**
> Authored by a cfd `lab-lane` 2026-09-08 (rule 16). This file is a SEPARATE draft; the frozen
> prereg body is **not edited** by the authoring lane (rule 6). No message from this lane, or
> from any agent, is Sanaa's consent (rule 9). **SUBMISSIONS ARE PARKED (rule 7).**
>
> **OWED before this addendum is applied (the supervisor's, undelegated — SUPERVISION §3):**
> - **check-1** — the own-family grader `analyse_m6_own_family.py` read AS A DIFF vs the pinned
>   `analyse_m6sr.py` (MEASUREMENT LOGIC): confirm the Cp comparison and the Roache/GCI math are
>   REUSED UNCHANGED (imported) and only the level-discovery / paths / counts / endTimes /
>   patch-names / Gate-G framing were adapted.
> - **check-4** — the personal read of the re-pin: it moves no gate, threshold, band, cap or label.
> - Applying this addendum at the re-pin commit, so the pinned grader blob equals the committed blob.

---

## HOW THE SUPERVISOR APPLIES THIS (rule 6, the T23G2R re-pin precedent)

Append the block below **at the foot of the frozen prereg as a new §13**, after §12. Do **not**
edit §1–§12 (the frozen gate content). The append satisfies rule 6: a departure is disclosed in
a dated amendment at the foot, with a version bump and the assertion that no line number above it
changed. It re-pins **only** the grading-path blob; it changes **no** gate/threshold/band/cap/label.

---

## BLOCK TO APPEND — begins below this line

## 13. FREEZE ADDENDUM — 2026-09-08 (grading-path RE-PIN; §1–§12 gate content byte-unchanged)

**Version: v1.0 (freeze, §12) → v1.1 (grading-path re-pin addendum, this §13).**

**lines whose number changed above this section: 0.** This addendum is appended at the foot; it
edits no line of §1–§12. It re-pins the grading-path blob **only** and **alters no gate,
threshold, band, cap or label byte** — §5 (Gate P literals `ΔCp = ±0.02`, `x/c ≤ 0.90`, the seven
`y/b` stations, Gate G's rule-5 ordering), §6 (the honest-labelling law), §7.3 (the one registered
hard cap 2,136 core-min) and §10 (the byte-identity proof) are untouched.

### 13.1 WHY THIS RE-PIN EXISTS
§12.3's HONEST NOTE recorded that the pinned comparator `cases/M6SR/analyse_m6sr.py` (blob
`8007b23da5bb3173dacb6eda1d67ca5d90ce9139`) carries the **check-1'd MEASUREMENT FUNCTIONS** for
the M6 Cp-vs-AGARD comparison and the Roache/GCI math, but its **level-discovery / registration
layer is M6SR-specific** — `main()` / `_discover_levels()` hardwire the level ids `L3/L2/L1`, the
M6SR mesh paths, the M6SR cell triple `A4_CELLS = (99840, 399360, 1597440)`, the endTimes
`(3000, 4000, 5000)` and the patch-name set `{wing, inout, sym}` — so it **cannot grade this
own-family {L2, L1, L0} triple as invoked**. §12.3 ruled that an own-family grading harness must
be authored, pass the cfd-supervisor's **check-1**, and be pinned by a **dated FREEZE ADDENDUM**.
This §13 is that addendum.

### 13.2 GRADING-PATH RE-PIN TABLE — pinned by git blob at this addendum's commit (rule 2)
The grading path is re-pinned from `analyse_m6sr.py` (M6SR-hardwired discovery) to the own-family
grader. The own-family grader **IMPORTS** `analyse_m6sr.py` and calls its pinned measurement
functions **UNCHANGED** (`read_case_2308`, `d1_discriminator`, `cfd_sections_for_case`,
`gate_p_figure_data`, `set_to_set_assignment`, `gate_p`, `roache_triple`, `gci_fine_from_gate_g`,
`cd_series`, `residual_series`, `gate_g2`, `completion_clauses`, `controls`, `read_checkmesh`,
`points_stream_sha`, `read_boundary`, `section7_condition_1`, `section7_conditions_2_3_4`), so the
M6SR core stays pinned as its instrument.

| grading-path member | role | pinned git blob | source |
|---|---|---|---|
| `verification/runs/M6_OWN_FAMILY_runs/analyse_m6_own_family.py` | own-family Gate P + Gate G grader (measurement core reused UNCHANGED; only the own-family adaptation layer is new) | `da0df95c81ded5833821cfd8a1f711d7f849f93c` | on-disk `git hash-object`; enters the tree at this re-pin commit |
| `cases/M6SR/analyse_m6sr.py` | the imported MEASUREMENT CORE (Cp comparison + Roache/GCI math + planted controls), reused verbatim | `8007b23da5bb3173dacb6eda1d67ca5d90ce9139` | committed HEAD blob (unchanged from §12.3) |
| `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/case_2308.dat` | reference — 271 AR-138 tapped values | sha256 `020c5fcc58060737024eb87d9404f56bc563f3f6f15e337675c47477fa91f0d0` | unchanged from §12.3 (hash-refused inside the imported reader) |
| `verification/runs/M6_OWN_FAMILY_runs/L{2,1,0}/case/system/createPatchDict` | own-family patch-name source (`{wing, symmetry, farfield}`) | sha256 `3e235b4d1324f4eb3f3986dc6e136ca621e39feb6b091aa2c9bf23cc892b368f` | re-hashed by the grader's Section-7 name screen at run time |

The solve driver `verification/runs/M6_OWN_FAMILY_runs/run_m6_own_family_triple.sh` (git blob
`63ce12b927c74eb8b64b719a2bae86b5a2965247`, on-disk at this commit) is the queue row's launch
target (§8); it hashes the grader against its committed blob (above) and refuses on drift before
spending a core-minute (rule 2), and rehearses the planted controls under `python3` and
`python3 -O` before the solve (rule 3, §9.2 parity).

### 13.3 WHAT THE OWN-FAMILY GRADER DIFFERS IN (the check-1 surface, MEASUREMENT LOGIC)
The DIFF vs `analyse_m6sr.py` is the own-family adaptation layer **only**:
- level ids `L2/L1/L0` (coarse→fine), run roots `.../L{2,1,0}/solve`, cells `71760/574080/4592640`
  (cell ratio **8.00**, not M6SR's 4.00), endTimes `(6000, 6000, 6000)` (§7.2's cost basis; a
  DRAFT the supervisor confirms), patch names `{wing, symmetry, farfield}`.
- Gate G FRAMING: this triple refines **all three** directions (surface ×4 = 2² **and** wall-normal
  layers ×2 = 2¹ per level; cells = surface_faces × layers, cell ratio 8 = 2³), so its Roache ratio
  `r = 2.000` is the genuine isotropic 3-D refinement ratio, **DERIVED** from the frozen §1 counts,
  and `roache_triple`'s `p` is a **CREDENTIAL-GRADE OBSERVED ORDER** — **not** M6SR's
  surface-refinement lower bound (clause L-HONEST is **not** carried over; it is false for this
  family). The GCI math (`roache_triple`, `gci_fine_from_gate_g`) and the GCI's r-invariance are
  reused unchanged; only the derived `r` and the interpretation differ.
- The rule-5 ordering, the case_2308.dat hash-refusal, the planted-zero controls, the rule-4 strict
  completion + age guard, the exit-2 refusals and the fixed verdict vocabulary are the imported
  pinned functions, unchanged.

### 13.4 CONDITION CHECKED AT THIS ADDENDUM (rule 2)
- The solve run roots `verification/runs/M6_OWN_FAMILY_runs/{L2,L1,L0}/solve` are **ABSENT** (the
  age guard and the no-pre-existing-time-dir refusal hold at launch, rule 4) — nothing has run.
- The re-pin moves no gate/threshold/band/cap/label byte (§13 opening assertion).
- The grader on disk hashes `da0df95c81ded5833821cfd8a1f711d7f849f93c`; the re-pin commit makes
  that the committed blob (verified after commit).

## BLOCK TO APPEND — ends above this line
