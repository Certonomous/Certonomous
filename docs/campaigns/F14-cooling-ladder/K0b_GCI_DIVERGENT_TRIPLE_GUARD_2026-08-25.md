# K0b — the GCI guard is SIGN-ONLY, and the family-wide self-blindness sweep

**Written 2026-08-25T18:12:03Z** (`date -u`, same shell invocation as the write).
**Owner:** heat-transfer. **Class:** dated diagnostic note. **HEAD at run:** `f6b72feb`.
**Scope:** the executable check `scripts/check_grader_self_blindness.py`
(sha256 `95d35ba6338f925b…`) run over every comparator in heat-transfer territory,
plus the two traces referred to this family by verification.

**NOTHING WAS FIXED. NO FROZEN FILE WAS EDITED.** This note is a diagnostic record.

---

## 1. What the check actually tests — and what a PASS from it does NOT mean

`check_grader_self_blindness.py` is **two cheap static AST smells**, not a
correctness proof, and it says so itself (`:29-31`).

* **Probe A (the FIFTH shape, L-322)** — flags two or more `dict(...)`/`{...}`
  literal assignments to the *same* subscript prefix whose **keyword-key sets
  differ**, escalating to ERROR when some key absent from one branch is read
  anywhere in the file. It hunts the `grade_f3.py` shape: a `PENDING` branch that
  omits `core_s` while the summary reads it.
* **Probe B (the FOURTH shape, L-321)** — flags a module-level UPPERCASE constant
  used **both** inside an `os.path.join(...)` in a function whose name matches a
  *fixture* hint (`synthetic`, `fixture`, `_make_`, `plant`, `_write_`) **and** in
  one whose name matches a *resolver* hint (`resolve`, `check_`, `grade`,
  `completion`, `verify`, `read`, `parse`). It hunts the `analyse_f5b_physics.py`
  shape: fixture and reader sharing one wrong assumption so their agreement
  carries no information.

`--selftest` passes here: each probe was shown able to **fire** on a planted
defect and to stay **quiet** on its clean counterpart — the rule-3 discipline,
applied to the probe itself.

**A PASS from this check means only:** no *literal* dict assignment in this file
has a divergent key set, and no *uppercase constant* is shared between an
`os.path.join` in a fixture-named function and one in a resolver-named function.

**A PASS does NOT mean:** the grader's arithmetic is right; its guards are
complete; its extrapolation has the right sign; its triple classification is
sound; its fixture is independent of its reader by any route other than a
shared UPPERCASE constant inside `os.path.join`. **Every defect this note goes on
to report was invisible to both probes.** The check is a smoke detector in one
room of the house.

## 2. The comparator list — enumerated with `find`, not `grep`

`find verification/runs/{T-family,F14-cooling-ladder,THERMAL_K0_runs} -name '*.py' -type f`
→ **111 files**. Each was tested against `git check-ignore`: **none is gitignored**,
so the L-`grep-honours-ignore-files` blind spot does not bite here. All 111 were
scanned. Result: **105 clean on both probes, 7 flags across 6 files.**

## 3. Every instance the check reported — and the triage

**All 7 flags are FALSE POSITIVES.** Two systematic over-read shapes in Probe A
account for all of them:

| # | file:line | probe / severity | triage |
|---|---|---|---|
| 1 | `T10a_runs/analyse_t10a.py:480,499,501` | A / ERROR | **Shape present, exposure NIL.** Three genuinely different branches (sphere / box / 2D-Hottel) write different key sets to `m["geometry"]`. But the only read outside a writing branch is `:839` `m["geometry"].get("facet_deficit_inner")` — a **guarded `.get()`** — and `:840` sits inside that guard. `:485-486` read keys the same branch wrote. The ERROR severity is spurious: the probe's read-map is keyed on the subscript **string alone**, so `REG["box"]["Lx"]` at `:492` counted as a read of `m["geometry"]["Lx"]`. |
| 2 | `T10a_runs/analyse_t10a.py:541,545` | A / ERROR | **False positive.** `:541` is `m["rowsum"] = {}`, a bare **container initializer**, not a branch. The consumer at `:832` is guarded by `if "rowsum" in m`. |
| 3 | `T1_runs/analyse_dts.py:922,928` | A / ERROR | **False positive**, same shape: `:922` is `out["per_case"] = {}`. One member constructor only. Script prints *"DIAGNOSTIC, NOT GRADED"*. |
| 4 | `T1_runs/analyse_dts_p.py:616,622` | A / ERROR | **False positive**, identical shape to #3. |
| 5 | `T10aR_runs/analyse_t10aR.py:629,642` | A / WARN | **False positive**: `:629` is `out["four_level"] = {}`. |
| 6 | `K0b_D406_repair/grade_d406.py:46,73` | A / WARN | **False positive**: `:46` is `out["legs"] = {}`. |
| 7 | `T9a_runs/analyse_t9aD.py:154,265` | B / ERROR | **False positive.** The shared constant is `HERE = os.path.dirname(os.path.abspath(__file__))` (`:69`) — the script's own directory. It carries **no assumption about artifact naming**, which is the whole content of the L-321 defect (a shared endTime *format*). Moreover `planted_zero` **copies the real case tree** (`shutil.copytree`) rather than constructing it — precisely the independence L-321 asks for. |

**Probe A's two systematic over-reads, stated for the record:** (i) it treats a
bare `{}` container initializer as a schema branch — 5 of 7 flags; (ii) its
`reads` map ignores the container and matches on the key string alone — this is
what drove ERROR rather than WARN on #1 and #2. **On a clean family the check's
signal-to-noise is 0/7.** That is worth recording, because a check whose flags
are all false will be skimmed past on the day it is right.

## 4. Trace (a) — CONFIRMED: the K0b GCI guard is SIGN-ONLY, and quotes a NEGATIVE GCI

### 4.1 The defect, confirmed by planting on the frozen functions

`analyse_k0b_mesh.py`'s `richardson()` (`K0b_D403_rerun/:310-321`,
`K0b_D406_repair/:310-321` — **bit-identical**, md5 `d9983b8e…`;
`K0b_mesh_sensitivity/:391-402`, md5 `fb9a38b1…`) guards **only** on increment
sign change:

    if d21 == 0 or d32 == 0 or (d21 * d32) <= 0:   # refuses
    p = math.log(abs(d21 / d32)) / math.log(r)
    gci = 1.25 * abs(d32 / f3) / (r ** p - 1.0) * 100.0

**There is no `p <= 0` test.** A triple whose error *grows* under refinement has
same-sign increments and sails through. Planted live on all three frozen copies
(imported, not edited), with both controls:

| planted triple (coarse/med/fine) | what it is | p | `GCI_fine_pct` | `reason` |
|---|---|---:|---:|---|
| 1.00 / 1.02 / 1.05 | **DIVERGENT** | **−0.5850** | **−10.714 %** | **None** |
| 1.05 / 1.02 / 1.01 | CONVERGING (control) | +1.5850 | +0.619 % | None |
| 1.00 / 1.05 / 1.02 | sign change (control) | None | None | SET |

All three copies return **identical** values. The reader was shown able to fire,
to stay quiet, and to refuse — so the −10.714 % is a **measurement**, not an
absence. **The verification team's referred figure is CONFIRMED exactly.**

`p < 0` makes `r**p − 1 < 0`, so the GCI is negative: a band with a negative
width, offered with `reason = None` — i.e. offered as valid. Standing rule 5
requires such a row to be **NOT A RESULT**; this instrument cannot represent that
state at all, having no `state` field.

### 4.2 THE TRACE: has any published heat-transfer number been quoted from a divergent triple?

Every JSON artifact under the three territories was walked — **134 files, 112
nodes carrying an order and/or a GCI**. Published order range −4.8092 … +4.8789.

**Answer: NO for every graded number; YES for five numbers in one committed
display-only artifact.**

* **The gating comparators are CORRECT and gate correctly.** 22 `DIVERGENT` and 16
  `STAGNANT` triples exist across `gate_t1b.json`, `gate_t1b_L4.json`,
  `gate_t3.json`, `gate_t10a.json`, `gate_k0cg.json` and
  `K0cX_runs/grid_convergence.json`. **Every one carries `state=DIVERGENT` (or
  `STAGNANT`) and `GCI_pct = None`** — the band is withheld and the row reads
  `NOT A RESULT`. Rule 5 is working as written wherever a verdict is at stake.
* **K0b's own published ladder is CLEAN.** `published_protocol_L32_L64_L128b`
  (the ladder behind the K0b record) gives **p ∈ [1.7529, 2.9824]** on all six
  quantities — every one positive and near second order — with positive GCIs
  0.0631 … 0.7840 %. **No K0b published number rests on a divergent triple.**
* **The five live negative GCIs.**
  `K0b_D403_rerun/k0b_d403_regrade.json` → `richardson/script_alone_L32_L64_L128a`
  and `grade_d403.txt:78-84`:

  | quantity | p | `GCI_fine_pct` |
  |---|---:|---:|
  | `Nu_avg_hot` | −1.2517 | **−11.3760 %** |
  | `Nu_max_hot` | −0.5425 | **−30.9020 %** |
  | `Nu_min_hot` | −3.2759 | **−14.1965 %** |
  | `U_star_max` | −1.5200 | **−6.9652 %** |
  | `stratification_S_leastsq_mid25pct` | −3.1749 | **−19.2018 %** |
  | `V_star_max` | None | None *(refused — the one triple that changed sign)* |

  This is the **`script_alone` arm**: the deliberately defective control leg
  (L128a at `endTime` 4000, the under-converged fine mesh D403 was investigating).
  Divergence is the *expected* signature of that arm — the defect is not that the
  triple diverges, it is that **the instrument quoted a band on it instead of
  refusing**.

**Exposure — established by reading the verdict operands, not the prose:**
`grade_d403.py:105-118` builds `out["richardson"][label]`, dumps it and
**prints** it. The `verdict` column in `grade_d403.txt` is
`out["deviations"][tag][k]["verdict"]` (REPRODUCED / NOT-REPRODUCED), computed at
`:88-96` from per-leg deviations — **no verdict operand anywhere reads
`out["richardson"]`.** A search of every tracked `.md` under `docs/`,
`verification/` and `cases/` for `script_alone` or for any of the five negative
values returns **nothing**. (The one apparent hit, `docs/NUMERICS_KNOWLEDGE.md:10`,
is an unescaped-`.` regex artefact matching the date `2026-07-19/20`.)

> **VERDICT on trace (a): the defect is REAL and CONFIRMED on all three K0b
> copies. Published-number exposure is NIL — no graded value, band or verdict in
> the heat-transfer family rests on a divergent triple. Five negative GCIs stand
> in one committed display-only artifact and its printed report, unlabelled.**

### 4.3 This is a DIFFERENT defect from the one already recorded

`analyse_t1c.ADDENDUM_2026-08-24_richardson_sign.md` §6 examined these same three
K0b files and cleared them — correctly — on the **extrapolate sign**
(`ext = f3 + d32/(r^p − 1)` with `f3` fine and `d32 = f_fine − f_med` **is** the
right Roache form; K0b's published extrapolate 4.52001514525647 stands). That
trace did **not** examine the **guard**. The sign is right and the guard is
incomplete; they are independent faults in one function.

## 5. Trace (b) — T1c extrapolate exposure: ESTABLISHED, and it is NO

`analyse_t1c.py:337` `richardson = f_fine + e21 / den` with `e21 = f_med − f_fine`
— **CONFIRMED**, sign inverted against Roache/Celik (`f_fine − e21/den`).
Identical at `analyse_t3.py:384`.

The question referred as *unknown* — **does any verdict, band decision or
published value in the T1c chain read the extrapolate?** — resolves to **NO**,
on three independent readings:

1. **The key is written once and never read.** `grep -n 'richardson'
   analyse_t1c.py` returns **exactly one line: 337, the write.** There is no
   consumer inside the module.
2. **It never reaches the gate artifact.** `grep -c 'richardson'
   verification/runs/T-family/T1_runs/gate_t1c.json` → **0**.
3. **The verdict operands are `dev` and `band`.** `analyse_t1c.py:462-472`:
   `fband = fconv.get("GCI_pct")`, `verdict = "NOT A RESULT" if fband is None`
   else the `dev ≤ band` test. `GCI_pct` uses `abs(e21)` and `p` uses
   `abs(e32/e21)` — **both sign-independent.** The `richardson` value is not an
   operand of any verdict.

This independently confirms §3 of the 2026-08-24 sidecar, which had already
traced this and reached the same conclusion; the trace was **not** in fact
outstanding, though it was referred as such.

**One live caveat, carried forward rather than absorbed.** The sidecar names it
and this sweep confirms it: `analyse_dts_p.py:374` computes
`L["h0_excess_pct"] = 100.0 * (conv["richardson"] − NU_TS) / NU_TS` **from the
sign-defective extrapolate**, and that quantity feeds the **P1/P2/P3
prediction-consistency flags** written to `dts_p.json` at `:540, :562, :581`.
Those flags **do move with the sign.** They are a registered **non-verdict**
channel — the comparator prints *"DIAGNOSTIC, NOT GRADED: no band, no pass/fail,
no T1c verdict moves"* — so the NO above stands for verdicts, bands and published
values. It does not extend to the P-flags, and no reader should take it as doing so.

## 6. One real L-321 instance the check is blind to

`analyse_t3.py:1088-1100` — selftest control (iv), *"gci_unequal with equal ratios
reproduces T1C.gci to 1e-12"* — asserts agreement across `("order", "GCI_pct",
"richardson")` between `gci_unequal` and the imported `T1C.gci`. **Both carry the
identical sign defect**, so the control passes on the `richardson` key *because
both are wrong the same way*: two implementations sharing one assumption, their
agreement carrying no information. That is the FOURTH shape exactly, and **Probe B
cannot see it** — Probe B only inspects UPPERCASE constants inside `os.path.join`.

Stated at its true severity: **as a reduction check it is sound** (its claim is
that the unequal-ratio form reduces to the equal-ratio form, and it does). It is
only misleading if read as *validation* of `richardson`. The lab already holds the
correct control — `T10aR_runs/analyse_t10aR.py:383-406`, *"the shared gci's own
richardson carries the registered SIGN DEFECT"* — which is the form that carries
information. Note the planted triple at `analyse_t3.py:1091` is `(1.0, 1.02, 1.05)`:
the very divergent triple of trace (a), already in this family's own selftest.

## 7. Un-fixable under the freeze — what a dated amendment would have to assert

The K0b guard defect (§4) **cannot be repaired in place.** All three
`analyse_k0b_mesh.py` copies are frozen graded instruments; `K0b_D403_rerun` and
`K0b_D406_repair` are byte-identical to each other and were the instruments of
two committed regrades. This is the same freeze-citation class that forced the
2026-08-24 T1c finding into a **sidecar** rather than an in-file amendment.

**No fix is proposed and none may be applied.** A dated amendment — which is the
supervisor's call and not this lane's — would have to assert, at minimum:

1. The exact defect: the `richardson()` guard tests **only** `d21 * d32 <= 0`, never
   `p <= 0`, so a divergent triple yields `p < 0`, `r**p − 1 < 0` and a **negative
   GCI with `reason = None`**; the instrument has no `state` field and therefore
   **cannot represent** the `NOT A RESULT` outcome rule 5 mandates for such a row —
   the FIFTH shape (L-322) in its exact form, in a frozen file, found by hand and
   **not** by the new check.
2. The measured blast radius: five negative GCIs in
   `k0b_d403_regrade.json` `/richardson/script_alone_L32_L64_L128a` and
   `grade_d403.txt:78-84`, enumerated in §4.2 with values.
3. That **no verdict, band or published number moves** — with the operand reading
   that establishes it (`grade_d403.py:88-96` vs `:105-118`), not an assertion.
4. That K0b's **published** ladder is untouched: p ∈ [1.7529, 2.9824], all GCIs
   positive.
5. `lines whose number changed above this section: 0`, plus the sha256 of each of
   the three copies, since a sidecar leaves the frozen bytes intact.
6. That the correct instrument already exists in the lab and should be preferred
   by any future K0b work: `analyse_t1c.gci` / `analyse_t3.gci_unequal` classify
   `DIVERGENT` at `p <= 0` and `STAGNANT` at `p < 0.5` and withhold the band —
   which is exactly why the 22 divergent rows elsewhere in this family are
   correctly `NOT A RESULT`.

## 8. Docket

Landed as **D528** (the K0b sign-only guard), **D529** (the check's own
signal-to-noise on a clean family), **D530** (the L-321 shape the check cannot
see). Ids derived by hand from the HEAD blob's row-opener form
`^\|\s*(\*\*|~~)*\s*D[0-9]+` → max 527; the bare-token sweep over-reads to 901
(the D901 fixture constant inside D349's prose) and was not used.
