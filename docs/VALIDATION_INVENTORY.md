# What this lab can validate, and against what

**Read this before anything else in `docs/`.** It answers one question that no
other document in the repository answers whole: **which of this lab's numbers
are checked against the world, and which are only checked against the lab.**

It holds no result of its own. Every row points at the campaign record that owns
it, and every verdict below is quoted from that record with the commit that
carries it. Nothing here upgrades anything. Where a record says TREND-ONLY, this
page says TREND-ONLY however good the solve looks; where a reference was never
obtained, the row says so in the reference column and not in a footnote.

**Frame.** Every count on this page was taken at commit `fa2c8bb0`, over
`git ls-tree -r HEAD`. The counts move several times an hour and the paths move
with them (section 1.3). Re-derive rather than quote.

---

## The headline, stated before the method so it cannot hide behind it

1. **Almost nothing in this lab is validated against the world.** Over **135
   distinct gates and rungs**, **three cases** carry a VALIDATED chip, and all
   three are qualified. The largest reference class in the lab, at 43 percent of
   rows, is **the lab's own earlier run, its own text or its own code**. The rest
   is solver-backed, capability-only, withdrawn, or blocked. Section 4 counts it.
2. **The reference is the ceiling, not the solve.** A rung's tier is set by what
   it was compared against, not by how well it converged. The best-instrumented
   rung in the lab (F14 K0c, 24 of 24 rows inside band, five controls, one of
   them a planted 10 percent Rayleigh error that the same comparator fails at
   3.19 percent) is capped at TREND ONLY, because its reference is a numerical
   benchmark and not an experiment. That is correct and it is the single most
   useful thing a newcomer can learn from this page.
3. **The lab's own convention for a missing reference is used in one campaign.**
   The token `NOT OBTAINED` appears in campaign F14 and essentially nowhere else
   (section 6). Elsewhere a missing reference is recorded in other words, or
   in the case of the most visible gate table in the repository, not recorded at
   the gate at all.
4. **Twenty-seven gates and checks in this lab cannot fail**, fourteen of them
   demonstrated as such by the lab itself and thirteen structural but never
   exercised. They share one mechanism: **the gate's quantity is derived from,
   or fixed by, the thing it is supposed to test.** Section 7 is the census, and
   it separates the ones whose inability to fail was demonstrated from the ones
   where it was only argued.
5. **What good looks like here is section 7.4**, and a newcomer should read it
   before the census above it. The strongest gate in the lab grades continuity
   against exact theory, on an instrument validated first at r = 0.9997 to
   1.0000, finds 58x and 123x degradation with the sign against the lab's own
   entry, and does it on a referent the benchmark's scoring metric structurally
   cannot see.

---

## 1. How the population was derived

Hand enumeration has failed repeatedly on this tree, and a list of campaigns an
author happened to think of certifies memory rather than coverage (L-104). The
population below was swept, not remembered.

### 1.1 The commands, with their readings at `fa2c8bb0`

| Step | Command | Reading |
|---|---|---|
| Corpus | `git ls-tree -r HEAD --name-only \| grep -cE '\.md$'` | 478 tracked markdown files |
| Screen A, fixed verdict tokens | `git grep -lE '\b(GATE REACHED\|GATE FAIL\|GATE PASS\|GATE NOT REACHED\|NOT A RESULT\|VALIDATED\|SOLVER-BACKED\|RESEARCH MODEL\|UNCONVERGED\|TREND[ -]ONLY)\b' HEAD -- '*.md'` | 82 files |
| Screen B, gate or rung declared | `git grep -lE '(^\|[^a-zA-Z])[Gg]ate[ _-]?(table\|row\|spec\|metric\|criterion\|criteria\|reached\|fail)\|\b[Rr]ung\b' HEAD -- '*.md'` | 309 files |
| Union, the candidate population | both screens | **327 files** |
| Campaign tags, derived from filenames | `git ls-tree -r HEAD --name-only \| grep -E '\.md$' \| xargs -n1 basename \| grep -oE '^(F[0-9]+[a-z]*\|W[0-9]+\|R[0-9]+\|B[0-9]+\|A[0-9]+\|S[0-9]+\|K[0-9]+[a-z]*\|V[0-9]+\|LADDER_V\|DMR\|DPW8\|4G\|THERMAL_K0\|MODEL_FORM)' \| sort -u` | the family list in section 3 |

Screen A alone is not sufficient: a pre-registration that fixes a gate before
any compute carries no verdict token at all, and F12 is exactly that file. Screen
B alone is not sufficient either: it matches every mention of the word rung,
including the charters. The union was then adjudicated file by file, and files
that turned out to be status reports, move records, or instrument audits rather
than campaign gates were classified out and are named in section 1.4.

### 1.2 The unit, and why capability rungs are shown but not counted as results

The unit is **one gate or one ladder rung**, not one document and not one
verdict line. A single record can carry twenty four graded rows against one
reference (F14 K0c) and that is one rung; a single rung can carry four grade
documents and five re-grades (Ladder V V10) and that is still one rung, taken at
its latest verdict.

**Capability rungs appear in the table and never as results.** F14's K0a and K0b
are labelled capability rungs by standing rule, in their own record's own words
at `32d4ae0d`:

> **CAPABILITY RUNGS. NOT RESULTS ABOUT THE WORLD.** K0a and K0b establish that
> this lab can drive a buoyancy-coupled solver and that the watts coming out of
> it balance. They are validated against **no published reference datum**.

The entry rule is `docs/charters/CASE_SELECTION_CHARTER.md` section 8: a
capability rung "is labelled a capability rung at launch the same way section 3
labels a regression test: before it produces a number, never after."

### 1.3 What this sweep cannot see

Stated before the results, because a reach limit found afterwards is a defence.

| Not seen | Size at `fa2c8bb0` | Why it matters here |
|---|---|---|
| The run tree outside the repository, `/home/ubuntu/certonomous-runs/` | 477 run directories, 31 markdown files | Almost every gate's raw solver evidence lives here. I read the records, not the logs. No number below was re-derived from a solve |
| The gitignored arm inside the tree | 37,243 files at the `8cefb4e9` reading in `docs/LOCATIONS.md` section 3 | Includes `mission-output/`, which holds the evidence artifacts for all nine acts of the lab's most visible gate table (section 3.1) |
| The 68 tracked PDFs | 68 | This corpus uses strike-and-keep, and a struck figure sits in a PDF text layer exactly as a live one does. A PDF cannot be graded from its text extract |
| Machine-readable siblings | every `*.json` beside a record | At least one known md/json disagreement exists (ladder-a A4's JSON reads PASS where its prose read CONDITIONAL). A gate that exists only as a JSON key is not in this table |
| Rendered HTML and 955 PNGs | | A page can carry a claim its bytes do not contain |
| **No solver was run for this audit** | n/a | Every number is quoted from the record that owns it. Nothing was re-derived from a solve, and a row can be reference-obtained, in band, failable and still wrong |
| Several long records were **sampled, not read whole** | `K2a_RACK_ROW_MODULE_SPEC.md` 500 lines, `KV1_RESULTS.md` 531, `LADDER_V_TRIPLE_VERIFICATION.md` and 50 sibling grade documents | A gate stated only in a section I did not open is not in this table |
| JSON siblings were not read against their markdown | every `*.json` beside a record | At least one known disagreement exists: ladder-a A4's JSON reads PASS where its prose read CONDITIONAL |
| Independence of any non-author grade | | Every commit on this box carries one identity. Independence rests on untracked per-machine dispatch records (D130), and `scripts/check_rung_attribution.py` must not be cited for it (D173) |

**And the tree moved under this sweep, twice, which is itself the finding.**
At `fa2c8bb0`, `git status --porcelain` showed **2,699 tracked paths deleted
from the working tree** and present in HEAD: `demo-output/website/dafoam/`,
`demo-output/website/tmr/`, `demo-output/website/mega-batch/` and others have
been moved to `cases/` by an uncommitted `git mv` batch. Separately, three F14
rung records existed in the working tree and in **no commit at all** when this
sweep opened, and one of them, `K2e_RESULTS.md`, landed at `b845b603` while it
was running. **Every path cited on this page is a HEAD path.** If a path here
does not exist on disk, look for it under `cases/`, and re-derive rather than
assume the record is gone.

### 1.4 What was classified out, and where it lives instead

These carry gates, and they are not validation gates against a physical
reference. They are named so a reader does not think the sweep missed them.

| Class | Where | Why out of scope |
|---|---|---|
| Instrument fail-open sites | `docs/FAIL_OPEN_GATE_POPULATION.md`, `docs/FAIL_OPEN_GATE_AUDIT.md` | 419 `except` sites and 44 `check_*` functions in tracked Python. A population of code shapes, not of physical claims |
| Standing monitor signatures S1 to S16 | `docs/standards/MONITOR_STANDARD.md` | Gate instruments, not physical quantities |
| Standing physics rules | `docs/physics_rules.yaml`, four blocks (`womersley`, `mesh_quality`, `sobol`, `thermal`) | Thresholds inherited by solves, not gates on a case |
| Mesh and convergence admission gates | `docs/standards/MESH_STANDARD.md`, `scripts/check_convergence.py` | Upstream of every physics gate. Where one blocked a physics gate, the physics row says so |
| Governance and budget gates | HLPW6 submission gate, TMR C4 affordability gate | Correctly gates, gates nothing physical |
| Referent classification of checks | `docs/EXTERNAL_REFERENT_AUDIT.md` | Classifies verifications as EXTERNAL, SELF-REFERENTIAL or NONE. This page holds the join of that axis with tier, verdict and failability; it does not repeat it |

---

## 2. The tiers, read from source

Two axes, and confusing them is the commonest error on this tree. Both are
quoted here rather than recalled.

**Gate verdicts.** `docs/charters/VERIFICATION_CHARTER.md:95`: *"The verdict
vocabulary is fixed. Gate verdicts: PASS, GATE REACHED, GATE FAIL, NOT A RESULT,
BLOCKED."*

**Fidelity chips**, a different axis, defined in `sdk/chief_engineer/lab.py:182`
to `:200` and restated at `VERIFICATION_CHARTER.md:97`:

| Chip | Definition, verbatim from `lab.py` | The path that grants it |
|---|---|---|
| `VALIDATED` | "graded against a published experiment and inside its band" | `validate_against_reference()` only. `lab.py:224`: "VALIDATED is earned only against a published experiment. A tight envelope alone stays SOLVER-BACKED" |
| `SOLVER-BACKED` | "a real solve produced it; no experimental comparison (or the comparison is not like-for-like)" | every other branch of `trust()` |
| `RESEARCH MODEL` | "a sizing/reduced-order model, honestly labeled" | `solver_backed=False` |
| `UNCONVERGED` | "the solve did not settle; the number is not evidence yet" | `converged=False` |
| `TREND ONLY` | **retired.** `lab.py:194` maps it, with `REFERENCE REGIME MISMATCH`, onto `SOLVER-BACKED`; `NEEDS WORK` onto `UNCONVERGED` | historical records only |

Three consequences a newcomer should carry:

- **A code-to-code comparison never grants VALIDATED.** `lab.py:456`: "this path
  never grants VALIDATED; a positive comparison is stated on the record and the
  tier stays SOLVER-BACKED." Section 3.1 row 9 is a live violation of this on the
  lab's most visible surface.
- **TREND-ONLY in a record means SOLVER-BACKED under the current code.** It is
  kept verbatim in the tables below because the records say it, and because
  demoting a label the record chose is an edit, not a reading.
- **A gate must be able to fail.** `VERIFICATION_CHARTER.md` section 2a: *"A gate
  whose quantity is derivable by construction from its own inputs is an IDENTITY,
  not a control. It may be reported. It may never be gated on."* Section 6 is the
  population of places this bites.

---

## 3. The inventory

Columns are the same in every table. **Ref class** is one of: experiment,
numerical benchmark, exact theory, another solver, own earlier run, none.
**Obtained** is the column that matters most. **Tier** is the record's own word,
never mine. **Can fail** is DEMONSTRATED (a control, a planted defect or a real
failure is cited), ARGUED (a failing condition is stated and was never
exercised), or NO (with the mechanism).

### 3.1 The nine-act gate table, the lab's most visible surface

`demo-output/website/campaign/NINE_ACT_GATE_TABLE.md`, generated by
`scripts/gate_table.py`, last touched `b14356b0`. This is the table that reaches
the camera and the website, so its defects travel further than any other.

| # | Act and gate | Ref class | Obtained? | Tier of record | Verdict, anchor | Can fail |
|---|---|---|---|---|---|---|
| 1 | Cylinder Re 100, Strouhal | published correlation | **NOT OBTAINED as cited.** The gate uses `St=0.198(1-19.7/Re)`, whose constants the repo traces to a prior lab gate and a task prompt. `sdk/workflows/cylinder_vortex_shedding.py:22` cites Roshko 1954 NACA 1191 for a *different* form, `0.212(1-21.2/Re)`, which the same run misses at **5.54 percent**. Acquisition: read NACA 1191 and settle which form governs Re 100 (filed, D-B6-1) | PASS, 0.77 percent | `b14356b0` | ARGUED. It passes against the unattributed form and fails against the cited one |
| 2 | Wedge M 2.0 15 deg, oblique shock angle | exact theory | OBTAINED, theta-beta-M, own solver checked to 6 figures against NASA GRC `oblshk.f` | PASS, 1.44 percent | `b14356b0` | ARGUED |
| 3 | Cone M 2.35 10 deg, conical shock angle | exact theory | OBTAINED, Taylor-Maccoll, own shooting solver | PASS, 2.14 percent | `b14356b0` | ARGUED |
| 4 | Diamond M 2.0, wave drag | exact theory | OBTAINED, shock-expansion, cross-checked against Ackeret | PASS, 0.26 percent | `b14356b0` | ARGUED |
| 5 | Hypersonic cylinder M 8, shock standoff | published correlation | OBTAINED, Billig 1967 via Anderson Eq. 5.37, PDF fetched and OCR'd; a web-sourced coefficient 4.76 was rejected for the printed 4.67 | PASS, 0.70 percent | `b14356b0` | ARGUED |
| 6 | Ahmed 25 deg slant, drag | published experiment | **PARTIAL.** SAE 840300 is a real, uniquely identified paper, but **no record states which table, figure or page `cd: 0.285` came from, or how**. `git log --follow` on `models/curriculum/ahmed_25/reference.yaml` returns one commit, the initial import `5336dd57`. A sibling file from the same batch was caught being a hand-set estimate wearing a citation | "see record". The cell was corrected from `SOLVER-BACKED` at `13b965dd` because the cited transcript states no tier. The act's own verdict is "inconclusive refinement study, not enough to call it validated" | `b14356b0`, correction `13b965dd` | DEMONSTRATED at family level (the 35 deg sibling lands outside its band) |
| 7 | NASA wall-mounted hump, separation and reattachment x/c | published experiment | OBTAINED, `noflow_cp.exp.dat` / `noflow_cf.exp.dat` fetched live from the NASA TMR and retained | **VALIDATED** | `b14356b0` | **NO, as posed.** Reattachment misses by **+13.9 percent** and the row still reads VALIDATED. No band is printed in the table and no threshold exists that a larger miss would have crossed |
| 8 | ONERA M6, primal residual against its own tolerance | **self-referential, and it says so** | n/a. The intended external gate, Cp at 7 spanwise stations against AGARD AR-138, is **named in the cell and declared NOT evaluated** | UNCONVERGED | `b14356b0` | DEMONSTRATED. This row is the gate that failed |
| 9 | CRM wing-body, drag | **another solver** (DAFoam's own CRM_Wing tutorial, Cd 0.02090 +/-2 percent) | OBTAINED, tutorial page fetched | **VALIDATED** | `b14356b0` | **NO.** Same code, same downloaded mesh, same unmodified `daOptions`, agreeing to 0.007 percent. It can catch a broken pipeline, not a modelling error |

**Three things about this table a newcomer must not miss.**

**Row 8 is the best row in the lab.** It is a verification that correctly declares
it has no external referent, names the external gate it did not reach, and
refuses to substitute the nearer gate it did compute. `docs/EXTERNAL_REFERENT_AUDIT.md:619`
calls it exactly that, and it is built programmatically at
`scripts/gate_table.py:224`.

**Row 9 is a live tier violation.** `lab.py:456` states that a code-to-code
comparison never grants VALIDATED. The correct declaration exists, in
`demo-output/website/dafoam/ladder-a/A6_crm_wingbody.md:154`, which calls the act
"essentially an exact reproduction of the tutorial's own stated result" and
explicitly not evidence about drag prediction accuracy. **That declaration does
not travel to this table**, and this table is the one that was filmed. The
external-referent audit calls this the lab's real defect class: transmission
loss, four of its seven live findings, not self-referential checking.

**None of the nine artifacts is in the repository.** All nine `artifact` cells
point into `mission-output/...` paths under `mission-output/`, which is
gitignored. The charter's bright line is *"Done means a gate has a verdict, the
verdict cites an artifact, and the artifact is still on disk."* It is on disk on
this machine. **A fresh clone of this repository can verify none of these nine
gates.**

### 3.2 Campaign F14, the cooling ladder

`docs/campaigns/F14-cooling-ladder/`. The youngest campaign and the only one that
uses the lab's NOT OBTAINED convention. Read its `README.md` next after this
page: it is the model for what a campaign record should look like.

| Rung | What it gates | Ref class | Obtained? | Tier of record | Verdict, anchor | Can fail |
|---|---|---|---|---|---|---|
| K0a | Heated box 400 cells: solver runs, Nu(g on)/Nu(g off) > 1.5, g-off velocity zero, heat imbalance < 2 percent | **none, declared** | n/a. "validated against **no published reference datum**" | **CAPABILITY RUNG. NOT A RESULT ABOUT THE WORLD** | all four gates PASS, `32d4ae0d` | ARGUED. A2's failing branch is written down: "Nu = 1.0 within noise means the solver is transporting nothing. That is a failed rung" |
| K0b | Differentially heated square cavity Ra 1e5, 4096 cells: residuals, boundary-layer scaling, core stratification S > 0.3, Nu 3 to 7 | **none, declared** | n/a. B5's Nu point estimate 4.98 "is my own scaling estimate. It is not a reference value and cannot grade anything" | **CAPABILITY RUNG** | all six gates PASS, `32d4ae0d` | ARGUED. S is a real discriminator: pure conduction gives S = 0 exactly |
| K0b mesh triple | Nu_avg mesh convergence at 32/64/128, observed order and Roache GCI | own earlier run | OBTAINED (the committed 64 leg at `183c91c0`) | **capability rung, graded against no published datum** | order 1.94, GCI 0.24 percent after the 128 leg was continued to 16000 iterations, `77c53e13` | DEMONSTRATED. At the original 4000 iterations the triple read **divergent**, order -1.25. Iteration error wearing a mesh study's clothes, caught and named |
| K0a/K0b A4, B4 heat balance | Boundary heat balance closure on a closed wall-bounded domain | none | n/a | PASS at 0.000563 and 0.000309 percent, then **declared non-gating after the fact** | `32d4ae0d` | **NO. Near-identity by construction, and the record says so.** Control C3 predicted over 20 percent imbalance on an unconverged snapshot and measured 0.0128 percent, never above 0.13 percent at any iteration. C3 was replaced by C3b, a planted 5 mW source: 35.94 percent imbalance, exit 1 |
| K0c laminar | Nu_avg, Nu_max, Nu_min, u1max, u2max at Ra 1e3/1e4/1e5/1e6, de Vahl Davis square cavity, mandatory two-mesh pair each | **published numerical benchmark, tier SECONDARY** | **PARTIAL.** de Vahl Davis 1983 (`10.1002/fld.1650030305`) is paywalled, Unpaywall `is_oa: false`, and **was not read**. Values carried from Han and Xie 2019 Table 3, corroborated against Gjesdal 2003 Table 1 and INL/EXT-09-15333 Table 3 where they overlap | **TREND ONLY, and not lifted by this result.** The spec's section 2.5: passing the laminar rung alone "supports verification claims only and caps at TREND ONLY" | **GATE PASS, 0 of 24 graded rows failed**, worst deviation 1.139 percent against a 3.0 percent band, `4afefe54` | **DEMONSTRATED, at the gate's own scale.** C2 plants a 10 percent Rayleigh error and the same comparator fails it at 3.19 percent against the 1.0 percent band. C4 perturbs each of the 24 rows in turn by 1.5x its own band and requires that row and only that row to flip: `every_row_reachable = True`. **No row on this gate is decorative** |
| K0c energy balance rows (4 of the 24) | Boundary heat balance, sealed cavity | none | n/a, "a defect, not a target" | reported, **not counted as evidence for the rung** | all four read 0.000 percent, `4afefe54` | **NO.** "On a sealed, impermeable, steady cavity with no source the boundary heat balance is very nearly an identity: the discrete temperature equation conserves at every iteration, converged or not. Every energy-balance row reads 0.000 percent, and **that is not evidence that the physics is right, it is what a sealed box does.**" C3 (planted 5 mW source, 341.73 percent FAIL, exit 1) shows the FAIL branch is reachable and nothing more |
| K0c core stratification | Core temperature gradient S at four Rayleigh numbers | published numerical benchmark | **NOT OBTAINED.** No read source tabulates it; both candidate primaries (de Vahl Davis 1983, Le Quere 1991 `10.1016/0045-7930(91)90025-D`) are paywalled, Unpaywall `is_oa: false` checked 2026-08-17 | **UNGRADED, measured and reported only** | four values printed, status UNGRADED, `4afefe54` | n/a. "A rung must never pass against a number the executing agent produced itself" |
| K0c turbulent | Mid-height velocity peaks and core stratification, Betts and Bokhari tall cavity, ERCOFTAC Case 079 | **published experiment** | **OBTAINED.** 22 primary data files byte-identical from the ERCOFTAC archive, full-archive SHA-256 recorded in `reference-data/MANIFEST.md` | **the only rung in this campaign eligible for VALIDATED** | **NOT RUN, not authorized**, `208fef5c` | n/a, unrun |
| K0c turbulent, Nusselt row | Measured Nusselt number, same case | published experiment | **NOT OBTAINED.** The ERCOFTAC database provides no Nusselt files; Betts and Bokhari 2000 (`10.1016/S0142-727X(00)00033-3`) is paywalled, `is_oa: false` | row cannot be graded | `208fef5c` | n/a |
| K0d | Turbulent mixed convection: velocity and temperature profiles, Blay heated-floor ventilated cavity | **published experiment** | **NOT OBTAINED.** Blay, Mergui and Niculae 1992, ASME HTD Vol. 213 pp. 65-72. **No DOI exists** (CrossRef query on the full title, 2026-08-17, no matching record; ASME HTD volumes of that era are unregistered), no OA copy. Venue corroborated by CiNii CRID 1573105974176827520. Profiles exist today only as figures in secondary papers | **TREND-ONLY, filed, gate rows fixed and reference numbers awaiting the primary** | `208fef5c` | n/a, unrun. The gate is written to be armed by addendum on receipt |
| K1a / K1c | Four thermal checks made standing (`docs/physics_rules.yaml` block `thermal`, monitor signatures S13 to S15) and run against planted defects | own planted defects | OBTAINED | verification of instruments, not a physics rung | 5 planted controls, 1 identity probe, 13 paired audits, **0 of 13 verdicts moved by any change**, `4afefe54` | **DEMONSTRATED, both directions.** KC2 (sign-reversed source) and KC3a/KC3b (magnitudes straddling the threshold) are recognition controls; KC0 is the negative control; KC-S15 caught a defect nobody planted. **This rung also closed proposal P1 by refusing it**: the proposed imbalance normaliser would print 100.0000 percent for every sourceless case whatever the source size, "a second identity, and by this campaign's own W-2 finding an identity cannot gate anything" |
| KV1 | The advective enthalpy-flux path of `scripts/heat_balance.py`, on an open duct | own planted source, plus a mutation harness | OBTAINED | instrument validation | advective term implemented and validated at +2.40e-08 percent on a planted source, `65684e7c` | **DEMONSTRATED, and the demonstration is the point.** See section 6 row 3: KV1b, the no-source negative twin, **cannot fail** because the uniform 305 K field makes the advective sum identically zero, and the fix was KV1c, a heated-wall duct with two independent non-zero terms that must cancel. Mutations then bit: sign flipped 45.66 percent, scaled by two 17.44 percent, one open patch dropped 100 percent |
| K2a | Rack-row module specification: geometry, parameter ranges, boundary condition on every surface, Boussinesq admissibility against the lab's 30.0 K limit | n/a, a specification | n/a | **Awaiting owner approval, no solve authorized** | `151bd7ea` | n/a |
| K2b pilot | Rack-row module as a 2D vertical slice: case runs, recirculation appears, per-rack inlet temperature extraction works, heat balance closes | **none** | n/a. "No number here is compared against a measurement of a real facility, because no such comparison is in scope" | **"it is a capability case in the K0a/K0b sense, never a result"** | four establishing measurements, `fa2c8bb0` | ARGUED, and the rung's own headline is a split: **the case that shows recirculation is the one that fails the S13 convergence signature, and the case that passes S13 never closes its heat balance.** C1 gravity-off twin, C3 planted source. The heat-balance leg is the sealed-case near-identity again. Four defects filed against this rung alone: D378 (every closure number produced through an uncalibrated code path, because the KV1 prerequisite K2a named was a laminar rung and every K2b case is turbulent) and D379 (y+ below the wall-function band on every wall, visible only because the spec required it measured) |
| K2c-A | Rack-front temperature and velocity profiles, hard-floor 10-rack module, Wibron et al. 2018 | **published experiment** | **OBTAINED, and armed.** CC-BY PDF in `docs/papers/`, SHA-256 recorded; reference column armed by vector-path digitization of Figures 6 and 7, seven controls, increments plus or minus 0.03 K on temperature, 0.007 m/s on velocity | **TREND-ONLY until the addendum landed; now VALIDATED-ELIGIBLE on two rows, VALIDATED on none.** Armed for **8 of 10 racks**: R5 and R6 are NOT ARMABLE because the paper plots no experimental bar for them | `f57ea386` | n/a, unrun. Three of the seven digitization controls are identity checks (the same datum plotted twice), recovering to 1.2e-5 m/s, 0.0060 m/s and 6.5e-5 deg C |
| K2c-B, raised floor | Rack-inlet temperature and perforated-tile flow, raised-floor facility | published experiment | **NOT OBTAINED IN ITS ENTIRETY. Eight papers with DOIs, every Unpaywall check dated 2026-08-17, every one `is_oa: false`**: Karki 2003 `10.1080/10789669.2003.10391062`; Schmidt and Cruz 2002 `10.1109/itherm.2002.1012507`; Schmidt 2004 `10.1109/itherm.2004.1319226`; VanGilder and Schmidt `10.1115/ipack2005-73375` and `10.1016/j.buildenv.2005.03.005`; Abdelmaksoud 2010 `10.1109/itherm.2010.5501413`; Arghode 2014 `10.1115/1.4028835`; Athavale 2018 `10.1115/1.4039025` | **NOT OBTAINED. No gate rows exist and none were written.** Any tile-supply solve is TREND-ONLY however well it converges | `f57ea386` | **n/a. There is no gate here at all**, and that is the honest state rather than a gap |
| K2e | Where the Boussinesq model stops being right: peak horizontal velocity, Nusselt number, centro-symmetry defect and centre temperature, Boussinesq against variable-density on identical geometry at fixed Ra 1e5 | **another solver / another model**, no experiment | n/a, and stated: "No experimental reference exists here" | **SOLVER-BACKED.** "under `sdk/chief_engineer/lab.py` it cannot reach VALIDATED. Nothing below may be quoted as validation" | velocity separates in eps (0.0333, 0.0500], Nu_h only 0.063 percent apart at eps = 0.1 and not reaching 1 percent until eps (0.30, 0.40]; first order against second order, `b845b603` | DEMONSTRATED on four of five controls. **C-3, the K0c anchor, is flagged by the record itself as "recognition, it reads a published number back and cannot fail informatively about K2e's own physics."** The heat-balance section is again declared non-evidence: `heat_balance_closure_is_evidence_on_sealed_case: false`, imbalance 0.0000 percent on all 15 Boussinesq cases |

**F14's own NOT OBTAINED table is in its `README.md` at `32d4ae0d`**, extended by
`K2c_RACK_ROW_VALIDATION_SEARCH.md` section 4 at `f57ea386`. It carries five
rows. This page reproduces them in section 7 with a price against each.

**A gate whose evidence its own tooling deletes.** K2e's pass docketed three
defects in `scripts/heat_balance.py`, and one bears directly on the failability
column above. At `scripts/heat_balance.py:770` the auditor runs
`shutil.rmtree(os.path.join(case, "postProcessing"), ignore_errors=True)` before
its own postProcess pass. That directory is the in-pass function-object history,
and **auditing a case therefore destroys it, silently and after the fact**.
Twelve K2e Boussinesq cases lost `hotFlux`, `coldFlux`, `Umax` and `Tcentre` the
moment they were audited. Filed as **D375** at `e4a977ef`. Re-derived here rather than taken second-hand:
`git ls-tree -r HEAD` returns **zero** tracked `postProcessing` paths anywhere
under `docs/campaigns/F14-cooling-ladder/`, so the committed archive of the
lab's best-instrumented rung contains none of that arm at all.

**What saves K0c, and it is luck rather than design.** K0c's convergence
criterion is graded on Nu_avg "as printed by the running solver's own in-pass
function object every 50 iterations", and those writes also went to the solver
logs, which **are** committed: `Ra1e5_m128/log.buoyantBoussinesqSimpleFoam`
carries 120 `areaNormalIntegrate(hotWall)` writes and its stage-2 log 33 more.
`scripts/check_convergence.py --monitor-regex` reads logs, not
`postProcessing/`, so the gate still runs. The two other docketed defects are
**D376**, that the auditor has no path for a compressible `rhoThermo` case, which
is exactly the solver class the Boussinesq limit points a later rung at, and
**D377**, that six of its refusal paths exit 1 rather than the documented 2, so a
caller cannot distinguish a refusal from a finding.

### 3.3 The F-series physics campaigns, F1 to F12

The lab's main physics validation line. Records live under
`demo-output/website/campaign/` (moved to `cases/` in the working tree at the
frame of this page, section 1.3).

| Rung | What it gates | Ref class | Obtained? | Tier of record | Verdict, anchor | Can fail |
|---|---|---|---|---|---|---|
| F1 Cp | Cp at 7 spanwise stations, ONERA M6, M 0.8395 | experiment | OBTAINED, AGARD AR-138 Case 2308, `case_2308.dat` archived verbatim | GATE REACHED | suction-side RMS 0.049 to 0.114 Cp, `ba88dff4` | ARGUED. **No pre-declared RMS tolerance exists anywhere in the record**; GATE REACHED was asserted after the numbers were read |
| F1 shock location | x/c of steepest upper-surface Cp rise | experiment | OBTAINED, same file | GATE REACHED | shock aft by 0.02 to 0.10 x/c at 6 of 7 stations, `ba88dff4` | ARGUED, no band |
| F1 adjoint | one FD-verified adjoint gradient | none (FD) | **NOT OBTAINED.** The adjoint never ran: 8 disclosed mitigations all OOM'd. Path: a host with materially more RAM, peak DAJacCon RSS measured first | **BLOCKED** | `ba88dff4` | DEMONSTRATED, it is the failure |
| F2 shock position | suction-side shock x/c, NACA0012 M 0.8 alpha 1.25 Re 6e6, band 0.35 to 0.60 c | numerical benchmark | **NOT OBTAINED.** The record's own words: "no citable digitized dataset was retained; the reference is a literature-recalled x/c ~ 0.60 stated to two significant figures **with no retained citation**". No acquisition path named | PASS (banded, qualitative, resolution-limited) | `515d9093` | DEMONSTRATED but degenerate. The detector emits only 8 distinct values across 280 runs; the pass turns on one quantisation level. **The claimed +0.044 c deviation is smaller than one detector increment (0.052 c) and was withdrawn** |
| F3 wedge p2/p1 | surface pressure ratio behind an oblique shock, M 2.0/2.5/3.0 | **exact theory** | OBTAINED, own theta-beta-M solver checked to 6 figures against NASA GRC `oblshk.f` | PASS | 0.01 to 0.07 percent at fine mesh, `d8a81e55` | ARGUED. Coarse mesh gave +4.56 percent, so the metric moves; no declared tolerance |
| F3 wedge beta | shock angle from the peak density-gradient locus | exact theory | OBTAINED, same | PASS, method-sensitive | 0.2 to 1.5 percent, `d8a81e55` | ARGUED. Both fits are reported precisely so the choice cannot be made after the fact |
| F3 cone pc/p1 | cone surface pressure, M 2.35 and M 3.0 | exact theory | OBTAINED, own Taylor-Maccoll solver. **NASA GRC's own cone10 "Theory" row was found self-inconsistent and not used** | PASS | +1.44 to +0.29 percent, `d8a81e55` | ARGUED |
| F3 cone beta | conical shock angle | exact theory | OBTAINED, same | PASS, not fully grid-converged, disclosed | +2.1 to +2.8 percent at fine, `d8a81e55` | ARGUED |
| F3 diamond cd | wave drag, double wedge M 2.0 and M 2.5 | exact theory | OBTAINED, shock-expansion closed form cross-checked against Ackeret | PASS, the strongest gate in this family | 0.18 to 0.55 percent, `d8a81e55` | ARGUED |
| F4 Gate 1 | shock standoff at the stagnation point, cylinder M 6/7/8 | published correlation | OBTAINED, Billig 1967 via Anderson Eq. 5.37; a web-sourced coefficient 4.76 was rejected for the printed 4.67 | PASS, with M 8 fine "NOT resolved above its own noise floor" | 0.7 to 2.3 percent, `d8a81e55` | ARGUED. No declared band; convergence is non-monotonic and the record says coarse-mesh agreement "is largely coincidental" |
| F4 Gate 2 | windward Cp against modified Newtonian | exact theory | OBTAINED, Anderson Eqs. 3.15 to 3.19, checked against the M to infinity limit 1.839 | PASS | 3.87 to 3.91 percent of Cp_max, `d8a81e55` | ARGUED |
| F4 Gate 3 | shock-wave/boundary-layer separation onset, Kussoy and Horstman M 7.05 cylinder-flare | **experiment** | OBTAINED, NASA TM 101075 downloaded and re-verified by text grep. The Settles alternative is **NOT OBTAINABLE**: 5 DOIs `is_oa: false`, CR-177638 excerpt only, CR-177577 on unreadable floppies | **Not run.** The warm-up is "NOT a usable physics result", root cause not identified | `d8a81e55` | **NO, skipped not failed.** The band is pre-registered but no gate case was ever built; the warm-up crashed then was found never wall-resolved (y+ 86 against a design of 1) |
| F5a batch | Strouhal at Re 100/150/180 | published correlation | **PARTIAL.** Roshko 1954 and Williamson 1996 are named in the code, but the gate form is "the exact form given in this task's gate"; no primary artifact retained | PASS | 0.7 to 4.6 percent, `515d9093` | ARGUED. No run in the gated set failed and no control was planted |
| F5a Re 1000 | Cd, St, Cl_rms | numerical benchmark and experiment | **OBTAINED.** Jiang and Cheng 2017 JFM 832, open-access accepted manuscript read directly; their tables carry Henderson, Papaioannou, Tong, Williamson and Brown, Norberg | GATE REACHED, correctly attributed | agrees with 2D DNS to a few percent, then deviates from 3D data by a mechanistically explained amount, `fe121af2` | ARGUED, with a genuine independent 2D-DNS cross-check as the falsifier |
| F5a Re 1000 3D pilot | 3D Cd, Cl_rms, St at 1.34 M cells | numerical benchmark | OBTAINED, same | **PRELIMINARY, not graded. "Sanity reading only"** | `fe121af2` | **NO, NOT A RESULT.** Also carries a disclosed defect: every coefficient over-normalized by a factor of 60 |
| F5a Re 2000 | Cd, St | experiment, regime band only | **PARTIAL.** "No paper was found that reports a point value". Norberg 2003, Williamson 1996, Fey 1998 all paywalled with no OA copy. Fell back to Zdravkovich 1990 reproduced as Fig. 3.3 of a 2014 PhD thesis, a **secondary** source. Path: institutional access to Norberg 2003 or Williamson 1996 | GATED, BANDED, LOWER CONFIDENCE, not a point gate | `fe121af2` | ARGUED, weakly. The band Cd 1.0 to 1.2, St 0.19 to 0.21 is wide enough that only a gross error trips it |
| F5a Re 3900 | Cd, St, base pressure, recirculation length | numerical benchmark and PIV | OBTAINED, six-source table read from He, Zhao and Wan ICCM2018, tabulating Lourenco and Shih PIV, Ma, Xu, Frederic and Tremblay, Kravchenko and Moin | GATE REACHED (PROVISIONAL) **as a model-deviation measurement, not a solver validation** | Cd +53.9 to +108.9 percent, `fe121af2` | **DEMONSTRATED.** The rung's own pre-registered prediction is scored **FALSIFIED** and "recorded as wrong rather than quietly re-fit" |
| F5a Re 3900 L_rec | mean recirculation length | numerical benchmark | OBTAINED, same | **NOT MEASURABLE BY THIS METRIC ON THIS FLOW.** "BLOCKED is not FAIL" | no mean reversed flow anywhere, `fe121af2` | **NO.** The metric is inapplicable: the flow holds no mean bubble, so the quantity does not exist to compare |
| F5b | CL/CM hysteresis loop, pitching NACA0012 dynamic stall | experiment | **PARTIAL.** NASA TP-1100 downloaded and OCR'd, but it "does NOT give a digitized, machine-readable CL(alpha) time series for case (e)". Fallback declared: qualitative comparison only | Feasibility PASS; **Physics and Gate rows are literal `[to be completed]` placeholders** | `881866b9` | **NO GATE EXISTS** |
| F5c | reattachment length x_r/H, Driver and Seegmiller backward-facing step | **experiment** | OBTAINED, DOI 10.2514/3.8890, parameters via the NASA TMR mirror cross-checked against a second source, x_r/H = 6.26 plus or minus 0.10 | **GATE NOT REACHED**, then "NO F5c RUN HAS EVER CONVERGED at any iteration count up to 20,000", headline **WITHDRAWN to unmeasured** | `27a94361`, `881866b9` | **DEMONSTRATED twice.** An archived planted sign-convention control (plain channel, no step, negative wall shear at all 100 faces) overturned the published reading; and a 2x2 relaxation factorial (6.876 against 2.652) proves non-convergence independently |
| F6a separation | separation x/c, NASA wall-mounted hump | **experiment** | OBTAINED, `noflow_cp.exp.dat` and `noflow_cf.exp.dat` fetched live from the NASA TMR and retained | GATE REACHED | -1.6 percent, `f4bf2c89` | ARGUED. No declared tolerance; "close" is assigned after the number |
| F6a reattachment | reattachment x/c, same case | experiment | OBTAINED, same | GATE REACHED, deviation labelled "documented SST bias, expected" | **+13.9 percent**, `f4bf2c89` | **NO, as posed.** A +13.95 percent miss reads GATE REACHED with no threshold that a larger miss would have crossed |
| F6a cross-check | separation and reattachment against NASA's own SST CFD | another solver | OBTAINED, NASA TMR SST page | not tiered, called "near-exact" | +0.06 percent, `f4bf2c89` | **NO. Near-identity.** Same closure, same benchmark, same experiment-matched geometry; this is a reproduction, not an independent test |
| F6a scorer self-check | our score against the benchmark's published floor on the shipped baseline field | own earlier run | OBTAINED | "reproduction verified" | 0.0622 against 0.0621, `f4bf2c89` | **NO.** It scores the shipped field against the shipped floor on the shipped mesh; a 0.02 percent field-vs-field MAE is a re-read of the same data |
| F6a epistemic band | does a model-form band on hump reattachment contain the experimental 1.100 | experiment plus a multi-closure ensemble | OBTAINED | band [1.0717, 1.2534]; C3 corner rows **WITHDRAWN AS CORNER STATES**; oneC/twoC gates "NO, not converging at all" | "YES, but the band is very wide"; the pre-registered claim that channel 1 alone under-covers is scored **FALSE**, `40401742` | DEMONSTRATED. The pre-registration was falsified after re-running kOmega to a real gate, having been "propped up by 5800 fewer iterations than it needed" |
| F6a diffusion T1 control | stock kOmegaSST rebuilt in a fresh clone must reproduce 1.2534 within 0.005 | own earlier run | OBTAINED | **PASSED, exactly** | identical to every printed digit, `b2315dcd` | **NO. Near-identity by construction.** "The clone is the baseline" |
| F6a diffusion T1 probe | reattachment and peak stress against the SST shear limiter a1 = 0.25/0.31/0.40 | own earlier run | n/a, internal | NOT FALSIFIED; the a1 = 0.25 arm is **NOT_CONVERGED, no gate-met scalar exists** | `b2315dcd` | DEMONSTRATED. Three falsifiers were written before the runs and each is answered; one arm produced no gateable number |
| F6a diffusion T2 | Spearman correlation between peak stress and reattachment across closures | own earlier runs | n/a | **interim.** SSG is "a rank inversion against H"; LRR is "a characterized limit cycle, not a gate-met value" | final scoring waits on EBRSM, `b2315dcd` | ARGUED, unresolved. No final score exists |
| F6b shipped mesh | separation and reattachment x/h, periodic hills Re 10595 | **numerical benchmark (LES)** | OBTAINED, Frohlich et al. 2005 JFM 526, via ERCOFTAC UFR 3-30 and the NASA TMR, "fetched live this session, not recalled from memory"; the case ships LES fields on the identical mesh | GATE REACHED, prediction falsified | reattaches at 7.6439 against 4.6 to 4.7, **+63 to +66 percent**, `d0f30f15` | **DEMONSTRATED.** The pre-registration is scored FALSIFIED on both magnitude and sign, and the prediction file is left unedited |
| F6b Gate V | our own ERCOFTAC-polynomial mesh must reattach within 5 percent of the shipped-mesh value | own earlier run | OBTAINED | PASS "by two orders of magnitude more margin than it asked for" | 0.043 percent, `ca7bbf1c` | ARGUED. The mesh is genuinely independently generated (wall agrees to 1.3e-7 h) so a fail was reachable; none was planted |
| F6b Gate P | reattachment against the ERCOFTAC LES band | numerical benchmark | OBTAINED | **FAIL, by over-prediction, exactly as pre-registered** | +63 to +82 percent; the pre-registered [7.0, 8.3] held, `ca7bbf1c` | DEMONSTRATED |
| F6b Gate Q | scaled MAE of velocity at the 9 standard stations | numerical benchmark | OBTAINED | PASS | 12.82 percent, inside the predicted [10, 16], `ca7bbf1c` | ARGUED |
| F6b fine rungs | existence of a steady solution at 31,280 and 62,400 cells | n/a | n/a | **"no, and not falling". The finest rung will not converge at all** | "the most interesting thing here, and nobody registered a prediction for it", `ca7bbf1c` | DEMONSTRATED, it is the failure |
| F6b QCR arm | change in reattachment from swapping in `kOmegaSSTQCR`, materiality bar 0.10 x/h | own earlier run | OBTAINED | **OUTCOME N, the null generalises** | 0.034, below the bar and marginally away from the band, `9a21d65c` | ARGUED. Branches P and R were declared in advance and did not occur; the same library moved the duct number 0.0811 to 0.0455 |
| F6b relaxation invariance | is the reattachment fixed point invariant under relaxation, bar 0.5 percent | own earlier run | OBTAINED | **CONFIRMED on both alternative settings** | 7.6472 / 7.6480 / 7.6458, `59f58b1e` | **DEMONSTRATED, and this is the strongest control in the F series.** "The instrument was shown able to fail before it was allowed to pass. A positive control, the same case stopped early, was refused certification at all four sample points, including two with a well-formed two-crossing bubble" |
| F6c duct | in-plane secondary-flow RMS as a percentage of bulk velocity, square and rectangular duct | **numerical benchmark (DNS)** | OBTAINED, the benchmark ships `0/U_LES` on the identical mesh | **GATE MEASURED, FAIL, reported as measured** | RANS gives ~1e-15 percent against DNS 2.07 to 2.22 percent, `f4bf2c89` | **NO, and it is the inverse case: this gate cannot PASS.** The linear Boussinesq closure has zero normal-stress anisotropy by construction, so the answer is identically zero for any mesh, any convergence, any setup. It carries information about the closure, not about the solver |
| F6d null test | that propagating an unperturbed stress leaves the F6b baseline unmoved | own earlier run | n/a | described as the end-to-end verification of sign, field I/O, frozen turbulence and discretisation | 7.643814 against 7.643915, `40401742` | **NO. Identity by construction**, and the record says why: the perturbation "is then identically zero at the baseline velocity field". It does calibrate a useful noise floor of 1.0e-4 in x/h |
| F6d propagated band | 90 percent interval on reattachment from 40 random-matrix members | numerical benchmark plus own corner runs | OBTAINED, Xiao, Wang and Ghanem arXiv:1603.09656 fetched and read | **Result 1, negative** | contains the LES truth but is 5.0x wider than the eigenspace corner union, `40401742` | DEMONSTRATED. The hoped-for outcome was falsified; the sampler was verified against 15 stated properties of the paper with 0 failures **before** any CFD |
| F6d gating bias | does residual-gating the ensemble bias the band away from truth | own ensemble | n/a | **Result 2, negative and pre-registered** | gated subset stops containing the LES range at the larger perturbation, `40401742` | DEMONSTRATED, and the risk was written down before the work |
| F6d sign error | does the eigenvalue perturbation apply with the intended sign | own code plus OpenFOAM sources | n/a | **Result 3, correction** | all 18 perturbation `fvOptions` apply the wrong sign; the 1C corner is non-realizable in 95.93 percent of cells, `40401742` | DEMONSTRATED four independent ways, including a one-character A/B replication |
| F6D Option A | control member must not move more than 0.25 x/h | own control | n/a | **VOID.** Separately, not one of the 13 members reached a settled state | control moved -0.491 against a 0.25 threshold, `54dacbb5` | **DEMONSTRATED.** "A gate that can be dissolved by post-hoc argument is not a gate": it fired and was honoured on the literal reading even though the mechanism it named was shown absent |
| F6D collision check | did a duplicate process contaminate the published trajectory | independent re-derivation from artifacts | n/a | measurement only | "section 6.1's chain is wrong at three of its five links", `4dec8fec` | DEMONSTRATED, and run by an agent that produced none of the work being checked |
| F7 rung (a) | dam-break leading-front position, Martin and Moyce 1952, tolerance 5 percent | **experiment** | **PARTIAL.** "No tabulated numeric data for Martin and Moyce (1952) could be located". Reference reconstructed by programmatic digitisation of a 2021 figure at 600 dpi, stated uncertainty plus or minus 0.05 in T. **No acquisition path for the primary is named** | **GATE FAILED** | best +8.2 percent mean, +11.0 percent max, `d8a81e55` | **DEMONSTRATED.** The failure survived a full knob sweep, each setting making it worse |
| F7a re-gate | max deviation of depth-integrated front position at 6 stations, pass at 5 percent | experiment | PARTIAL, same digitisation | **GATE (a): FAIL, +11.03 percent**, "un-relitigable" | `1ca28872`, contract executed `86704ddf` | **DEMONSTRATED and instrumented.** The contract is executable (`f7a_contract.py`, 42 tests, 0 passing against the pre-commit tree), and executing it **struck two previously published conclusions** and disqualified the original gate case |
| F7 rung (b) | Wigley hull wave resistance | | | **BLOCKED, not started** | "do not start (b) until (a) passes its gate, and (a) did not", `d8a81e55` | **NO GATE** |
| F7c | DTMB 5415 free surface, sinkage and trim | experiment, planned | **NOT OBTAINED.** Stage 0, geometry acquisition, "is a hard blocker" | **BLOCKED** | `724314ab` | **NO GATE.** Acceptance criteria are pre-written per stage ("A stage that cannot state what it is checked against does not exist as a stage") but nothing has run |
| F8 | low-speed-shaft torque, UAE Phase VI Sequence S wind turbine, MRF | **experiment** | **PARTIAL, and the record says so on its face.** Both NREL primaries were fetched and read in full and **neither publishes a tabulated 7 m/s torque**; the docket's citation "conflated two reports" and was corrected. The 800 N m reference is **secondary tier**, from a 2024 journal table | **NO VERDICT, and that is the result** | force band 19x wider than the pre-declared maximum, `a10ebc31` | **DEMONSTRATED.** The width cap and drift test were declared before the force history was read, and the width cap fired. The rotation-flip control run is a real mechanism test |
| F9 Gate 1 | cycle-mean pressure drop against the same case's own steady map | **own earlier run** | OBTAINED, own 4 steady solves | PASS both runs; section 9.7 reclassifies it as "internal consistency, unsteady against quasi-steady" | 1.6 percent and 0.22 percent, `52d4f3ae` | **NO, near self-reference.** It grades a run against a curve fitted to the same solver, same mesh, same geometry. The record's own line: "F9 is verified in part and validated against nothing" |
| F9 Gate 2 | radial velocity profile against the closed-form Womersley solution | **exact theory** | OBTAINED, Womersley 1955 implemented | **FAIL as a point comparison, reported as measured** | 20 to 414 percent error at every phase, `52d4f3ae` | **DEMONSTRATED.** It fails, the first proposed cause was itself tested and refuted, and a second made a prediction that was tested and held |
| F9 Gate 3 | cycle-weighted pressure drop against the lab's own reduced-order screen | **own earlier run** | n/a, internal | prediction direction and order confirmed, point value missed; the supporting discharge coefficients are **WITHDRAWN** | -94.0 percent against a pre-registered 150 to 250 Pa band, `52d4f3ae` | DEMONSTRATED, but the reference is the lab's own model |
| F9 stationarity | cycle-to-cycle periodicity of the fixed-BC reference runs | own criteria | n/a | passes on the throat differential, **fails on the downstream differential** | all three fail downstream, `d8a81e55` | DEMONSTRATED. The same instrument passes one signal and fails another on the same runs, which is the discrimination a gate needs |
| F10 quality gates (4) | checkMesh verdict, non-orthogonality and skew, mean y+, residual, drag drift | own standards | OBTAINED, thresholds reused verbatim; the y+ band corroborated against A4's mean y+ on the identical mesh | non-negotiable, all four measured per row | "a row that fails any gate is never silently kept", `1a7ebdd2` | **DEMONSTRATED.** A poison design surfaced as `ok=False` at 0.0 s, and the y+ gate is shown firing for real with a raised RuntimeError |
| F10 Ahmed 25 | frontal-rebased Cd, Ahmed 25 degree slant | **experiment** | OBTAINED, SAE 840300, band [0.2423, 0.3278] | **inside band, VALIDATED** | 13.28 percent relative error, `1a7ebdd2` | **DEMONSTRATED**, the 35-degree sibling on the same instrument lands outside its band |
| F10 Ahmed 35 | same, 35 degree slant | experiment | OBTAINED, band [0.221, 0.299] | **outside band, documented TREND ONLY** | 20.94 percent, `1a7ebdd2` | DEMONSTRATED, it is the failing case |
| F11 | centreline u(y) and v(x) against Ghia, Ghia and Shin 1982, Re 100 and 1000, n = 64 and 128 | **numerical benchmark**, explicitly verification and not validation | **PARTIAL, checked before the case was chosen.** The primary JCP article: `is_oa: false`, `has_repository_copy: false`, `oa_locations: []`. Values taken from **two independently hosted secondary transcriptions** by different authors, fetched separately and cross-checked; the Re 400/3200/10000 columns are documented as carrying transcription defects and were deliberately avoided | GATE REACHED, both rungs, both quantities, both resolutions | max deviation 1.73 percent of lid speed, `d8a81e55` | ARGUED on the physics gate (no numeric tolerance is declared anywhere), **DEMONSTRATED on the admission gate**: one case was caught NOT_CONVERGED at its 4,000-iteration cap and had to be resumed to 5,285 |
| F12 | RAE 2822 Case 9: mesh admission, Cp RMS, shock position, normal force, drag, five numeric bands | **experiment** | OBTAINED, AFOSR-HTTM/Stanford flow case 8621 via the NASA TMR, files retained in `F12_runs/reference/`, labelled secondary everywhere it is used | **NOT A RESULT.** Pre-registration only; **no results file exists** | `343c9163`. `CALIBRATION_SCORECARD_2026-08.md:264` counts F12 as an **ORPHANED pre-registration** | **CANNOT FAIL YET, skipped not failed.** The design is unusually falsifiable: four numeric gates, a shock detector chosen specifically to avoid F2's quantisation trap, a tolerance justified against tap spacing "and cannot be met by luck". No run exists |

**Index defects found by this sweep, and they matter to a newcomer.**
`CAMPAIGN_STATUS.md` at `d8a81e55` says F10 is "NOT STARTED (no record file
exists)". **That is false.** `F10_3D_VISCOUS_FAMILY.md` at `1a7ebdd2` carries
four quality gates and a two-point Ahmed validation gate. F1 has no
`F1_*.md` at all: its record is `dafoam/ladder-a/A3_onera_m6.md`, and the index
does not point at it. **Do not take a campaign list from `CAMPAIGN_STATUS.md`.**

### 3.4 The DAFoam adjoint ladders, and the closure challenge

Records at `demo-output/website/dafoam/` and `research/closure/md/` in HEAD's
layout. **Ladder A gates a gradient, not a flow.** Its unit is "does the adjoint
derivative agree with a finite difference of the same solver", so its reference
class is an **internal FD of the same code**, and no rung on it can reach
VALIDATED by construction. That is a correct design for what it is testing and it
is worth stating plainly, because "ladder A6, VALIDATED" appears on the nine-act
table and means something much weaker than it reads.

| Rung | What it gates | Ref class | Obtained? | Tier of record | Verdict, anchor | Can fail |
|---|---|---|---|---|---|---|
| A1 NACA0012 | adjoint dCD/dshape against central-difference FD, DAFoam's own tutorial | internal FD | OBTAINED, `check_totals` | verified with a documented blocker | run 1 crashed in 10 s on both ranks and is reported, not hidden; run 2 accepted. Aggregate 11.43 percent CD-wrt-shape, `7879bf97` | **DEMONSTRATED.** W5 re-ran it under a corrected derivative and "the whole shape chain collapses" while the FD never moves |
| A2 MACH wing | same, 105 design variables, 210 full primal re-solves | internal FD | OBTAINED | "**verified**, at or better than the calibration scale"; **the tutorial page states no before/after CD**, so there is no external target and the record says so | CD/shape 1.71 percent, CL/shape 1.17 percent, `895ff4af` | DEMONSTRATED, and then **withdrawn**: W5 section 3's headline is withdrawn because "1.71 percent, VERIFIED" was never safe, the state it was measured at no longer exists, and nobody can reproduce it |
| A3 ONERA M6 Cp | Cp at 7 spanwise stations against AGARD AR-138 | **experiment** | OBTAINED | GATE REACHED, no declared tolerance (this is F1's row) | `ba88dff4` | ARGUED |
| A3 adjoint | one FD-verified adjoint gradient | internal FD | **NOT OBTAINED** | **BLOCKED, documented and not hidden.** Adjoint OOM at both 399,360 and 99,840 cells; eight mitigations ruled out | `ba88dff4` | DEMONSTRATED, it is the failure |
| A4 Ahmed primal | CD against SAE 840300 and against the lab's own earlier OpenFOAM run | experiment plus own earlier run | PARTIAL (see nine-act row 6: no extraction record) | the pre-existing run is chipped **VALIDATED** at 12.95 percent relative error inside a plus or minus 15 percent tolerance | `7ca80f8d` | DEMONSTRATED at family level |
| A4 adjoint gradient | adjoint against FD on a 2,777-cell coarse mesh | internal FD | OBTAINED | **graded CONDITIONAL at 10.04 percent, then superseded 2026-08-04: the verdict of record is PASS**, the 10.04 percent being an artifact of DAFoam's default `scotch` decomposition | `7ca80f8d`; W5 moves it 1.09 points and settles it at **0.76 percent against the shipped toolchain**, `56a5a911` | **DEMONSTRATED.** The original strike is retained in place beside the live verdict |
| A5 U-bend | adjoint dOBJ/dshape against FD, pressure-loss objective | internal FD | OBTAINED | **hypothesis REFUTED**; "A5's defect remains unidentified" | `0363764f`; W5 closes the published 46.6 percent to **2.24 percent**, a claim moving **up**, and says so and gives it extra scrutiny | DEMONSTRATED |
| A6 CRM wing-body | converged primal only; drag against DAFoam's own CRM_Wing tutorial | **another solver** | OBTAINED, tutorial page fetched | the case record calls it "essentially an exact reproduction of the tutorial's own stated result" and **explicitly not evidence about drag prediction accuracy** | `a9528284`. **The nine-act table chips it VALIDATED anyway** | **NO.** Same code, same mesh, same options. The gradient was "known infeasible on this host per A3's measured evidence" and not attempted |
| W5 regrade | every published shape-gradient claim, re-run under the corrected derivative | internal FD, with a control | OBTAINED | per-claim verdicts of holds / moves / withdrawn | `56a5a911` | **DEMONSTRATED, and this is the best-controlled instrument in the DAFoam work.** The control is that **the finite difference must not move**: the patch touches only derivative code, so if a patched run's FD column differed, the comparison would be between two different functions. "It does not differ, in any row, in any case: every `Fd Magnitude` is bit-identical." A second control requires the stock re-runs to reproduce the published tables to every digit |
| B2 duct baseline | duct baseline primal | own earlier run | OBTAINED | baseline only | `e2c45ab9` | n/a |
| B3 duct field inversion | field-inversion recovery on the duct | own earlier run | OBTAINED | **Stage 3 (timed adjoint pilot): BLOCKED, not silently routed around** | `a29d7852` | DEMONSTRATED, it is the failure |
| S1 CBFS inversion | field inversion against the closure-challenge CBFS case | **third-party benchmark data** | **OBTAINED, and it is the lab's cleanest external referent.** `github.com/rmcconke/closure-challenge-benchmark`, authored outside the lab, locally unmodified, and the inlet premise independently recomputed by a parser written for the audit reproducing **150 faces, mean 0.9149216132, min 0.202035889, max 1.00537467**, every digit | used as the **positive control** of `docs/EXTERNAL_REFERENT_AUDIT.md` section 1.1 | `df4d4cbe` | n/a as a gate; it is the referent |
| S1 `varianceU` cross-check | that `Sigma/(3N)` reproduces the printed objective to 13 digits | **self-referential, fitted** | n/a | disclosed in the record's own words as "audit arithmetic identical to the failed run's coverage audit" | `S1_CBFS_REINVERSION_PREREGISTRATION.md:170` | **NO.** The divisor `3N` was fitted to the printed value in the sibling document; the check re-applies the convention and recovers the number. **A check whose parameter was solved for by requiring the check to pass cannot fail.** Used as the **negative control** of the external-referent audit |
| Closure C1 | a test-blind baseline-error gate for the periodic-hills correction | **third-party benchmark**, train/validation split only | OBTAINED | built and validated **only** on the training/validation split already exposed; **no flow solver was run** | `0869284e` | ARGUED. The blindness is the design |
| Closure C2 | where the closure deficit actually lives | third-party benchmark | OBTAINED | **twice corrected in place**, including "the floor was the wrong yardstick" | `0869284e` | DEMONSTRATED by its own two corrections |
| Closure C6 | whether the NASA hump can be improved at all | third-party benchmark | OBTAINED, the benchmark's own split table | a decision record, not a result: "It is a fact about which two candidates somebody compared" | `0869284e` | n/a |
| Round-5 entry | overall closure score, 8 cases | third-party benchmark, scored locally | OBTAINED, pinned clone `deb91557` | **rank 1 on the point estimate and NOT first within noise.** The one-seed uncertainty bound 0.002419 is **177 percent of the margin 0.001365** | `docs/PRODUCT_LIST.md` section 4B makes the caveats mandatory | n/a. **Best-on-board individual cases: 2 of 8, both of them declined rows. Cases won by the lab's own model: 0 of 8** |

### 3.5 The W, R, B52 and D families: pre-registered, and mostly withdrawn

These are the lab's shortest-cycle rungs, and they behave differently from every
other family on this page in two ways that a newcomer should notice.

**First, every one of them names a pre-registration commit made before any solve
ran.** W3_CUBE_SETTLE at `ee30a7c3`, W3_RACE_NUMERICAL at `05abf189`, R7 at
`14eb8f11`, B52 rung 8 at `48cfedfb`, D5 at `45c0103`, DMR at `74797a57`, W1 at
`3e252b5c`. That discipline is not decoration: it is what makes the second
observation possible.

**Second, this is where the lab withdrew the most.** Two chief rulings on
2026-08-10, `7abb0ba3` and `8f5bf878`, withdrew the "turn" claims from the B-52
and Ahmed ladders. **The gates in this family demonstrably bite, and what they
mostly bit was the lab's own headline.**

| Rung | What it gates | Ref class | Obtained? | Tier / verdict of record, anchor | Can fail |
|---|---|---|---|---|---|
| W1 bump on NASA's own grids | SST on NASA's published grid family, driven by a settle criterion | **numerical benchmark**, NASA TMR grids | OBTAINED, NASA's own grids | rung-by-rung against `settle_verdict` peak-to-peak, `3e252b5c` prereg | DEMONSTRATED, the settle criterion gates every rung |
| W1 hump challenge | whether the QCR2000 constitutive term moves hump separation | own earlier run | OBTAINED | **outcome two: the term does not touch it.** Both gates decided, gate reached, `9a21d65c` | DEMONSTRATED, the outcomes were declared in advance and outcome two occurred |
| W1 hump A1 | whether the SST shear limiter is a mechanism | own earlier run | OBTAINED | **OUTCOME ONE: the limiter is a mechanism**, `2544c9af` | DEMONSTRATED |
| W2 SpaRTA regression | reproducing the paper's model form | **published method** | OBTAINED | "the regression pipeline reproduces the paper's model FORM exactly", `7e8311fa` | ARGUED |
| W5 SpaRTA gate | the gate both escalation items demand | own earlier run | OBTAINED | "met three days before they were worked", `519afd67` | n/a, a status finding |
| W3 NACA0012 wall row | whether the wall's published verdict reproduces | own earlier run | OBTAINED | **"The row's verdict is not reproducible."** Nothing withdrawn, one thing put in proportion, `8fffd578` | **DEMONSTRATED, and it is the finding** |
| W3 mesh noise floor | mesh-construction scatter as a noise floor under ladder claims | own repeated draws | OBTAINED | **WITHDRAWN 2026-08-10**, chief ruling `7abb0ba3`: the published -4.055e-3 is max(rung 6) minus min(rung 7) of either ladder, `5ba5db81` | DEMONSTRATED |
| W3 cube settle | how much of the cube's published envelope is the solve not stopping | own earlier run | OBTAINED | **three predictions, three scored FALSE**, `e16452d0` | **DEMONSTRATED three times over** |
| W3 NACA4412 resolution scatter | drag stateable with a bounded mesh-construction scatter | own repeated draws | OBTAINED | **"Twelve of twelve meshes are outside the"** band; "the verdict survives everywhere" and "now cannot be blamed on one mesh", `8fffd578` | DEMONSTRATED |
| W3 wing valid family | family-level validity | own earlier runs | OBTAINED | **AMENDED 2026-08-10**, chief ruling `8f5bf878`: the Ahmed row's "turns" is WITHDRAWN, `8ad4107f` | DEMONSTRATED |
| W3 race numerical | shrinking the dominant numerical term | own earlier run | OBTAINED | gates fixed at `05abf189` before any solve below alpha = 0, `bf56add6` | ARGUED |
| W3 QCR duct falsifier | a structural claim about QCR on the duct | own earlier run | OBTAINED | **the structural claim is CONFIRMED**, `303247bb` | DEMONSTRATED, it is written as a falsifier |
| R4 Ahmed asymptotic | the Ahmed 25 degree ladder's TURN as a feature | own repeated draws | OBTAINED | **WITHDRAWN 2026-08-10** as a FEATURE, chief ruling `8f5bf878`: four same-recipe draws at c3 give s = 2.77e-3, `8ad4107f` | DEMONSTRATED |
| R7 Strouhal spacing | the cylinder ladder's Strouhal gate at Re 1000 across mesh spacing | own earlier run plus correlation | OBTAINED | gates fixed at `14eb8f11`, twin launched one minute later, `03a5a39d` | ARGUED |
| B52 rung 7 | the B-52 ladder's turn | own repeated draws | OBTAINED | **WITHDRAWN 2026-08-10**, chief ruling `7abb0ba3`, `8ad4107f` | DEMONSTRATED |
| B52 rung 8 | eighth-rung UQ against its pre-registration | own earlier run | OBTAINED, prereg `48cfedfb` before any eighth-rung mesh existed | `dfc50ee8` | ARGUED |
| B52 turn closure | whether the turn survives at all | own repeated draws | OBTAINED | **structure stays withdrawn**; the author's own extension ask is **WITHDRAWN** because it would not have worked, `c12c876b` | DEMONSTRATED, including against the author's own proposal |
| B52 certificate | the sealed one-page PDF certificate | own earlier run | OBTAINED | the only certificate class the lab ships | n/a |
| D5 RSM | Reynolds-stress models on the square duct, scored against a prediction committed first | **own earlier run** plus DNS context | OBTAINED, prediction at `45c0103` before any RSM run | scored without editing the prediction, `fe612d03` | DEMONSTRATED by construction: the prediction cannot be edited after the fact |
| DMR Gate V | incident-shock kinematics, double Mach reflection | **exact theory**, `x = 1/6 + (y+4)/sqrt(3)` at t = 0.2 | OBTAINED | **PASS, both rungs**, +0.15 and +0.17 percent of travel against a 1 percent tolerance, and the fine rung's error is below the coarse rung's as predicted, `84933043` | **DEMONSTRATED. This is the best-posed gate in the family**: exact theory, a tolerance fixed as a fraction of travelled distance, and a pre-committed detector |
| DMR Gate P1 | double-Mach structure detector: two slope discontinuities on the leading front | own detector | OBTAINED | **FAIL as registered, and the failure is the detector's geometry, recorded** rather than explained away, `84933043` | DEMONSTRATED, it failed |
| DPW8 V2 Joukowski | lift and pressure against the Joukowski closed form | **exact theory** | OBTAINED, `joukowski_theory.py` | staged L1 feasibility / L3 physics / L4 gate, `demo-output/website/campaign/DPW8_V2_joukowski.md` | ARGUED |
| 4G TMR mesh aspect ratio | mesh aspect ratio against the NASA TMR structured grids | numerical benchmark | OBTAINED | a measurement record | ARGUED |

### 3.6 Ladder V, sixteen rungs, and why it is in a different class

`demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md` plus roughly
fifty grade, re-grade and round documents. **Not one of these rungs gates a
physical quantity.** They gate the integrity of the closure entry's own claim
surfaces: whether a score reproduces in a clean environment, whether a
pre-registration chain exists, whether a claim in a table is supported by the
artifact it cites. The reference class is therefore **the lab's own earlier run
or its own text**, for every rung, by design.

**They are included because a newcomer will meet them first**, they are the
largest single body of rung records in the repository, and it would be easy to
read sixteen rungs carrying twelve passes as sixteen validated results. They are
not results about the world at all.

Verdicts are the latest for each rung, with what they were re-graded from. The
consolidated state document is `LADDER_V_STATE_2026-08-16.md` at `4d13ec13`, and
it is the right place to start; it is a measurement rather than a summary and it
prints its own disagreements.

| Rung | What it gates | Ref class | Obtained? | Verdict of record, anchor | Re-graded from |
|---|---|---|---|---|---|
| V1 | The round-5 score re-computed in a clean environment | own earlier run | OBTAINED | **PASS**, `LADDER_V_PASS1_2026-08-11.md:85` | first grade |
| V2 | That a pre-registration chain exists for every scored decision | own text | OBTAINED | **PASS**, same, `:224` | first grade |
| V3 | Leakage assertions: that nothing fitted on is scored | own text and code | OBTAINED | **PASS**. Leg (c) **failed on re-run** and was fixed by the chief at `2ef8ae3b`, then verified line by line | leg (c) FAIL to PASS |
| V4 | The duct case traced end to end | own earlier run | OBTAINED | **PASS**, `:394` | first grade |
| V5 | QCR provenance | own text | OBTAINED | **FAIL**, `LADDER_V_V5_V14_REGRADE_2026-08-16.md:232`, `6d95f812` | re-graded **from PASS WITH EXCEPTIONS to FAIL** |
| V6 | Compliance audit against the round-5 package | own text | OBTAINED | **PASS WITH RESIDUALS** (three), `60073572` | re-graded from FAIL on currency |
| V7 | That known defects are dead | own code | OBTAINED | **PASS**, and it found three defects rather than the two the lab knew about. **Fifth grade**, `f7a14346` | four prior grades |
| V8 | The claims table: every claim supported by the artifact it cites | own text and artifacts | OBTAINED | **PASS** on the repair grade, `7f601662` (17:13Z). Earlier the same day a non-author re-verification returned **GATE FAIL on one blocking finding**, `101079fd` (15:04Z) | **This is the rung that cost a full re-grade over a verdict with no record.** `4a207196`: "Eleven verdict cells cited no grade record at all, and the round this repair exists for filed none either, so V8 states the last verdict that still has an artifact" |
| V9 | Prior-art completeness | own text | OBTAINED | **PASS**, re-graded by a non-author, `66bd94ea`. The verdict held; **the certification that reached it did not** | FAIL to FIXED to PASS |
| V10 | Cross-surface mechanical sweep | own text across surfaces | OBTAINED | **PASS**, closed by a non-author at `bec3f2e5`, fifth non-author grade at `8c01202f` | **FAIL** at `60073572`, whose four named blockers were repaired 19 minutes later at `cca64eaf` and sat ungraded |
| V11 | Cold reproduction from the package alone | own package | OBTAINED | **PASS**, bit for bit, `LADDER_V_PASS3_COLD_2026-08-11.md:170` | first grade |
| V12 | The skeptic's report | own text | OBTAINED | **PASS WITH RESIDUALS** (R1, R2, R3, all since repaired at `6dbb3be6`, ungraded), `9c2734f8` | first grade |
| V13 | Close-out | own text | OBTAINED | **PASS WITH RESIDUALS** (four), `9c2734f8` | first grade |
| V14 | Mechanical surface discovery | own surfaces | OBTAINED | **PASS WITH RESIDUALS** (six), `6d95f812` | re-graded; ledger says "PASS as executed", re-run "NOT clean" |
| V15 | Ladder-written text re-entering V8's claims table | own text | OBTAINED | **FAIL**, round 10, `680d56ef`. Round 8 introduced **30 findings, four new shapes, NOT belief-neutral**, and six of them were defects written that same day **by the repairs** | ten rounds, none closing |
| V16 | Rank-claim guard reach | own guards | OBTAINED | **PASSES** at round 15, closed by a non-author of every prior round, `b2534057` | fifteen rounds; round 11 was 8 findings, four new shapes, NOT belief-neutral |
| TERMINATION RULE | All sixteen PASS **and** a full re-run of V8, V10, V14 and V15 over the previous round's text introduces zero new failures, measured by a non-author | own text | n/a | **NOT MET. The gate is shut.** R-VALUE consecutive-neutral count stands at **ZERO** on both rungs that track it, re-graded at `51d8eb43`, and **no round anywhere in this ladder's record has ever declared itself belief-neutral** | |

**Two things this ladder proves that no physics rung in the lab proves.**

First, **its gates demonstrably fail.** V5 was re-graded from a pass to a FAIL;
V15 has failed ten rounds running; V3's leg (c) failed on re-run after passing;
V8 failed a non-author re-verification hours after a pass. A body of sixteen
rungs where four are open and the termination rule is not met is a ladder whose
gates bite.

Second, **its own guards are documented as unable to confirm anything**, and the
state document says so before its own numbers: `board_placement_faults` has no
arithmetic predicate (D88), binds an ordinal only to a named published entrant so
it is structurally incapable of faulting a claim about the lab's own placement
(D151), skips strike-marked sentences (D85), and returns `([], [])` on a shipping
member carrying four placements. `_best_on_board_faults` never opens those files
in production (D129) and its pattern is bounded by `[^.\n]` so a wrapped sentence
defeats it (D223). **"A zero from any of these confirms nothing."** That sentence
is the single best piece of writing in this repository about what a gate is.

**And the independence every one of these grades rests on is not checkable from
the tree.** All commits on this box carry one identity; there is no `user.name`
configured. Independence rests on untracked per-machine dispatch records (D130),
and `scripts/check_rung_attribution.py` "is not cited here and must not be cited
by anyone" because it names a session rather than an agent and returns
`VERDICT: AUTHOR` for every pairing (D173).

---

## 4. The counts

**139 rows** are tabulated in section 3. Four of the nine-act rows re-present a
gate counted elsewhere (act 6 is F10/A4's Ahmed, act 7 is F6a's hump, act 8 is
F1's ONERA M6, act 9 is ladder A6's CRM), so the population is **135 distinct
gates or rungs** across every campaign in the lab.

### 4.1 By what the gate was checked against

Counted over the reference-class column. A row naming two classes is counted in
both, so these sum above 139.

| Reference class | Rows | Share |
|---|---|---|
| **This lab's own earlier run, its own text, its own code, or an internal finite difference** | **60** | **43 percent** |
| Published experiment | 23 | 17 percent |
| Published numerical benchmark | 15 | 11 percent |
| Exact theory | 12 | 9 percent |
| None, a published correlation with no retained primary, a third-party benchmark file, or explicitly self-referential | 14 | 10 percent |
| Another solver or another model | 4 | 3 percent |

**The largest reference class in this lab, by a factor of two and a half over
the next, is the lab itself.** That is not a scandal: verification against your
own prior state is a legitimate and necessary activity, and Ladder V's sixteen
rungs are entirely of that kind by design. It is, however, the fact a newcomer
most needs before reading any campaign record, because a rung graded against the
lab's own earlier run cannot tell you the lab is right about the world. It can
only tell you the lab is consistent.

### 4.2 By tier, and this is the headline

Counted on the strongest word the row's own tier or verdict cell carries. No row
was upgraded; where a record says TREND-ONLY it is counted TREND-ONLY.

| Tier or verdict class | Rows |
|---|---|
| **VALIDATED, chip actually awarded** | **5 rows, on 3 distinct cases** |
| GATE REACHED or PASS against an obtained reference, no tier chip awarded | 26 |
| SOLVER-BACKED or TREND ONLY, stated | 7 |
| Capability rung, or explicitly NOT A RESULT | 7 |
| GATE FAIL, VOID, falsified, or NOT REPRODUCIBLE | 6 |
| WITHDRAWN or amended in place after a ruling | 12 |
| BLOCKED, NOT RUN, or no gate exists at all | 14 |
| UNGRADED, UNCONVERGED, or NOT MEASURABLE by the metric posed | 3 |
| Ladder V process rungs, which gate the lab's own records rather than a physical quantity | 17 |

**Three cases in this entire laboratory carry a VALIDATED chip: the NASA
wall-mounted hump, the CRM wing-body, and the Ahmed body at 25 degrees.** They
appear five times between them because two of them are recorded twice.

**And all three are qualified, one of them fatally:**

- **CRM wing-body** is a code-to-code reproduction of DAFoam's own tutorial,
  same code, same mesh, same options, agreeing to 0.007 percent.
  `sdk/chief_engineer/lab.py:456` states in terms that this path **never grants
  VALIDATED**. The correct declaration exists in the case record and does not
  travel to the table that was filmed. This one is a category error, not a
  caveat.
- **NASA hump** is a genuine experimental comparison against retained NASA TMR
  data, and its separation figure is good at -1.6 percent. Its **reattachment
  misses by +13.9 percent** and the row still reads VALIDATED, because **no band
  is printed and no threshold exists that a larger miss would have crossed.**
- **Ahmed 25 degrees** sits inside a plus or minus 15 percent tolerance at 12.95
  percent, against a real and uniquely identified paper. **No record anywhere
  states which table, figure or page the reference value came from**, and a
  sibling file from the same import commit was caught being a hand-set estimate
  wearing a citation.

**Say it plainly, because it is the most useful sentence on this page and it is
the one a summary is most tempted to soften: almost nothing in this lab is
validated against the world.** The lab is large, careful, heavily instrumented
and unusually honest about its own limits, and its output is overwhelmingly
**solver-backed, capability-only, verification against itself, or blocked.**
Twenty-three rows compare against a published experiment; three cases earn the
chip; none of the three is unqualified.

**The counterweight, and it is real.** This lab withdraws things. Twelve rows
carry a withdrawal or a post-ruling amendment, six carry an outright failure, and
fourteen say plainly that they are blocked or that no gate exists. A corpus that
publishes fourteen "there is no gate here" rows is not a corpus that is hiding
its gaps. The problem this page documents is not dishonesty; it is that the
honest state is much thinner than the volume of work suggests.

---

## 5. Where there is no gate at all

Listed because a missing gate is invisible in every other view, and because
`VERIFICATION_CHARTER.md` section 2 requires that a gate not reached is stated as
not reached rather than replaced by a nearer one that was.

| Where | State |
|---|---|
| **F14 rung K2c-B, the raised floor** | **No gate rows exist and none were written.** Eight paywalled primaries, every Unpaywall check dated. Any tile-supply solve is TREND-ONLY however well it converges. This is the largest single hole on this page and it is correctly declared |
| F5b, pitching NACA0012 dynamic stall | Physics and Gate rows are literal `[to be completed]` placeholders |
| F7 rung (b), Wigley hull | Not started, correctly: "do not start (b) until (a) passes its gate, and (a) did not" |
| F7c, DTMB 5415 | Stage 0, geometry acquisition, is a hard blocker. Acceptance criteria are pre-written per stage and nothing has run |
| F12, RAE 2822 Case 9 | Five numeric gates pre-registered, unusually well posed, **nothing has run**. Counted an ORPHANED pre-registration by the lab's own scorecard |
| F4 Gate 3, shock-wave/boundary-layer separation | Band pre-registered, no gate case ever built. The warm-up crashed and was then found never wall-resolved |
| F1 | Has no `F1_*.md` record at all. Its record is `dafoam/ladder-a/A3_onera_m6.md`, and the campaign index does not point at it |
| F10 | The campaign index says "NOT STARTED (no record file exists)". **That is false**: four quality gates and a two-point Ahmed validation gate exist at `1a7ebdd2` |

---

## 6. Rungs blocked on a reference that was never obtained

Sorted by how many rows each unblocks. **The lab's NOT OBTAINED convention is
used in campaign F14 and essentially nowhere else**: at `fa2c8bb0` the token
appears 15 times in `K2c_RACK_ROW_VALIDATION_SEARCH.md`, 4 in F14's `README.md`,
3 each in `K2c_DIGITIZATION_ADDENDUM.md`, `K0d_...GATE.md` and `K0c_RESULTS.md`,
and twice in the whole of the rest of the corpus. Elsewhere the same state is
recorded in other words, or not recorded at the gate at all. The rows below are
therefore drawn from two different kinds of record and that is stated per row.

| Reference not obtained | Rows it unblocks | Why not obtained | Price to unblock |
|---|---|---|---|
| **Eight raised-floor / perforated-tile primaries**: Karki 2003 `10.1080/10789669.2003.10391062`; Schmidt and Cruz 2002 `10.1109/itherm.2002.1012507`; Schmidt 2004 `10.1109/itherm.2004.1319226`; VanGilder and Schmidt `10.1115/ipack2005-73375` and `10.1016/j.buildenv.2005.03.005`; Abdelmaksoud 2010 `10.1109/itherm.2010.5501413`; Arghode 2014 `10.1115/1.4028835`; Athavale 2018 `10.1115/1.4039025` | **All of F14 rung K2c-B, plus the tile-momentum arbitration of K2a section 2.2.** This is not a rung with unfilled rows: **no gate rows exist and none were written** | Every one Unpaywall `is_oa: false`, checked 2026-08-17. No repository copies | **Zero compute; institutional access or per-article purchase.** IEEE and ASME conference papers, roughly 8 x 15 to 35 USD at list, or one library route. **Read Wibron et al. 2019 `10.3390/en12081473` first, OA via the DiVA route, at no cost.** Largest single unblock on this page |
| **Blay, Mergui and Niculae 1992**, ASME HTD Vol. 213 pp. 65-72 | **All of F14 rung K0d**, currently TREND-ONLY with gate rows fixed and reference numbers awaiting the primary | **No DOI exists.** CrossRef bibliographic query on the full title, 2026-08-17, returned no matching record; ASME HTD volumes of that era are unregistered. Venue independently corroborated by CiNii CRID 1573105974176827520. The profiles exist today only as figures in secondary papers | **Zero compute; a document-delivery request, not a download.** ASME HTD proceedings of 1992 are not online. Interlibrary loan or an ASME digital-collection request. The alternative the spec names is tabulated digitisation from the secondaries with stated provenance, which is zero-cost but leaves the rung at TREND-ONLY |
| **de Vahl Davis 1983** `10.1002/fld.1650030305`, or **Le Quere 1991** `10.1016/0045-7930(91)90025-D` | F14 K0c **laminar** rung, the stratification half of its mandate. Four measured values sit UNGRADED today | Both paywalled, Unpaywall `is_oa: false`, checked 2026-08-17. Neither carries the tabulated core temperature gradient openly | **Zero compute; one paywalled article.** Roughly 40 to 50 USD, or the MIT access route in `docs/research/MIT_ACCESS_DOCKET.md`. Unblocks 4 rows on a rung that already passed everything else |
| **Betts and Bokhari 2000** `10.1016/S0142-727X(00)00033-3` | F14 K0c **turbulent** rung, the heat-transfer row. The rest of that rung's reference is already in hand | Paywalled, `is_oa: false`. The ERCOFTAC database provides no Nusselt files | **Zero compute; one paywalled article**, roughly 40 USD. Or derive wall heat flux from the near-wall temperature files already committed, with the derivation and its resolvable increment stated by addendum, at zero cost |
| **Norberg 2003 / Williamson 1996** point values for cylinder Re 2000 | F5a Re 2000 rung, currently GATED, BANDED, LOWER CONFIDENCE against a **secondary** source (Zdravkovich 1990 reproduced as Fig. 3.3 of a 2014 thesis) | "No paper was found that reports a point value". All candidates paywalled with no OA copy | **Zero compute; institutional access.** Converts a wide band into a point gate |
| **Martin and Moyce 1952** tabulated dam-break front positions | F7 rung (a) and the F7a re-gate. Both currently grade against a **programmatic digitisation of a 2021 figure at 600 dpi**, stated uncertainty plus or minus 0.05 in T | "No tabulated numeric data could be located." **No acquisition path is named in the record**, which is itself the gap | **Unknown, and naming it is the first task.** A 1952 Phil. Trans. paper; the digitisation may be the honest permanent answer, in which case the record should say so rather than leave the path blank |
| **NACA Report 1191**, to settle which Strouhal form governs Re 100 | Act 1 of the nine-act gate table, the lab's most-filmed row | Not attempted. The repo holds **two mutually inconsistent versions of its own cited reference** and the gate passes against the unattributed one | **Zero compute, zero cost.** NACA reports are public domain and on the NASA NTRS. This is the cheapest row on this page and it sits on the most visible surface |
| **The extraction route for `cd: 0.285`**, Ahmed 25 degree | Act 6 of the nine-act table, F10's Ahmed 25 validation gate, W3's Ahmed preregistration, which calls the yaml the "single source of truth" | The paper (SAE 840300) is real and resolvable. **No record anywhere states which table, figure or page the number came from.** A sibling file from the same import commit `5336dd57` was caught being a hand-set estimate wearing a citation | **Zero compute; one paper read and one provenance note written.** SAE 840300 is roughly 30 USD. This does not change a number; it makes an existing VALIDATED chip checkable |
| **AGARD AR-138 Cp**, already obtained, but never gated to a tolerance | F1's two GATE REACHED rows | Obtained. **What is missing is a declared band**, not a reference | **Zero compute, zero cost.** Declare the RMS tolerance the rung should have carried, then re-read the existing numbers against it |
| **NASA TP-1100 digitised CL(alpha)** | F5b, whose Physics and Gate rows are literal `[to be completed]` placeholders | The report was downloaded and OCR'd; it "does NOT give a digitized, machine-readable CL(alpha) time series for case (e)" | Digitisation of the published hysteresis loops, zero compute, or the rung stays qualitative and says so |
| **DTMB 5415 hull geometry** | All of F7c. Stage 0 is "a hard blocker" | Not acquired | Geometry acquisition, then a staged campaign. The largest compute commitment on this list and the one furthest from a result |

---

## 7. Gates that cannot fail

`VERIFICATION_CHARTER.md` section 2a: *"A gate whose quantity is derivable by
construction from its own inputs is an IDENTITY, not a control. It may be
reported. It may never be gated on."* A gate that cannot fail is not a gate.

**They share one mechanism.** In every instance below, **the gate's quantity is
derived from, or fixed by, the thing it is supposed to test.** That is the
signature to look for, and it is more useful than the list: a new gate is
suspect the moment its reference and its measurement share a parent.

**The census below holds twenty-seven instances**: fourteen in section 7.1 where
the inability to fail was demonstrated, and thirteen in section 7.2 that cannot
fail as posed and were never exercised. **The lab found most of them itself**,
which is the reassuring half of this section, and section 7.4 gives the opposite
pole equal space. They are separated
below by whether the inability to fail was **demonstrated** or only **argued**,
because that distinction is the whole point of the rule.

### 7.1 Demonstrated, with the demonstration cited

| Gate | Where | Why it cannot fail | The demonstration |
|---|---|---|---|
| Boundary heat balance on a sealed cavity | F14 K0a A4, K0b B4, all four K0c energy-balance rows, every K2e case | On a sealed, impermeable, steady domain with no source the discrete temperature equation conserves at every iteration, converged or not. `div(phi,T)` integrates to zero over the domain, so the boundary conduction terms are forced to sum to zero. It closes whether or not the physics is right | K0b's control C3 **predicted** over 20 percent imbalance on an unconverged snapshot and **measured 0.0128 percent**, never above 0.13 percent at any iteration (`32d4ae0d`). The prediction failure is what identified the identity. C3 was replaced by C3b, a planted 5 mW source, which reads 35.94 percent and exits 1. K0c then reports the rows and **excludes them from the rung's evidence** (`4afefe54`), and K2e stamps `heat_balance_closure_is_evidence_on_sealed_case: false` (`b845b603`) |
| The advective-closure control on a uniform-temperature duct | F14 KV1b | The duct had adiabatic walls and an inlet at 305 K, so it converged to exactly 305 K everywhere. `Q_adv(inlet) = +0.146191 W`, `Q_adv(outlet) = -0.146191 W`, **sum identically zero**. Flip the sign of the whole advective term: still zero. Scale it by two: still zero. **The closure passes for any scaling and any sign of the term it was built to validate** | It closed at 0.0000 percent, net 1.8e-12 W, exit 0, and was worth nothing. Caught by asking the mutation question rather than the closure question: four independent wrongnesses were planted and **three of the four changed nothing at all**. The fix was KV1c, a heated-wall duct with two independent non-zero terms that must cancel, on which the same mutations bit hard: sign flipped 45.66 percent FAIL, scaled by two 17.44 percent FAIL, one open patch dropped 100 percent FAIL. **The degenerate case was kept as the negative control, not deleted.** L-106 at `0ab6c39a`, rung record at `65684e7c` |
| `--allow-advective`, the flag that computed nothing and vouched for it | `scripts/heat_balance.py`, docket D360 | The flag "adds the term but the report is then stamped UNVALIDATED" was **false in both halves**. The only per-patch heat computed anywhere was `Q = kcond * G`, pure conduction; `a.allow_advective` was read at exactly one place, the refusal guard, and set no key and printed no line. With the guard silenced, `sealed = not nonwall` went False, so the report printed *"NOT of the identity class, so the balance is a genuine constraint here rather than a restatement of the discretisation"* **over a ledger the advective term was never in**. The flag's only effect was to silence the refusal that was protecting the reader | Confirmed by readback rather than by reading the code, all five D360 statements re-derived at HEAD and a sixth found (`267a4021`), then repaired and validated at +2.40e-08 percent on a planted source (`b8c398a4`, `65684e7c`). `closure_is_identity_class` moved from `false` to `null`/UNKNOWN on an incomplete ledger, because a balance missing a term is neither an identity nor a constraint |
| The proposed imbalance normaliser, refused before it was installed | F14 K1c, proposal P1 | With no inward patch, `sum(Q<0)` **is** the net, so the proposed ratio is `|net| / |net| = 1` exactly. It would print 100.0000 percent for every such case whatever the source size. A second identity | Measured rather than argued: plant the mirror defect, a **sink** instead of a source, and the existing code already prints `100.000000000 %` (control `KC2_sink_5mW`). The same measurement found that an adiabatic patch carrying **+7.94e-24 W** of floating-point residue made the reported imbalance **6.25e+22 percent**. "A denominator of residue is not a denominator." The remedy adopted instead declares the ratio UNDEFINED when `Q_in <= 0` or `Q_in < |Q_net|`, proved not more permissive over 13 field sets with 0 exit-code changes. `4afefe54` |
| F6d's null test | `demo-output/website/campaign/F6d_random_matrix_uq.md` | The perturbation "is then identically zero at the baseline velocity field", so propagating an unperturbed stress must leave the baseline unmoved. Identity by construction | The record says so itself and keeps the test only for the noise floor it calibrates, 1.0e-4 in x/h (`40401742`) |
| F6a's diffusion T1 control | `demo-output/website/campaign/F6a_DIFFUSION_RESULTS.md` | Rebuilding stock kOmegaSST in a fresh clone and requiring it to reproduce 1.2534 within 0.005. **"The clone is the baseline."** Near-identity by construction | It passed exactly, to every printed digit (`b2315dcd`), which is what an identity does |
| The `3N` divisor cross-check | `demo-output/website/dafoam/ladder-b/S1_CBFS_REINVERSION_PREREGISTRATION.md:170` | The divisor `3N` was **fitted to the printed value in the first place**, in the sibling document: `Sigma\|U-UData\|^2 = 961.1569839` over 21,000 cells divided by 3N = 63,000 recovers the recorded `varianceU`. The later cross-check re-applies that convention and recovers the printed number. **A check whose parameter was solved for by requiring the check to pass cannot fail** | Established mechanically in `docs/EXTERNAL_REFERENT_AUDIT.md` section 1.2, using the record's own disclosure, and used as that audit's **negative control**. It is a transcription-fidelity check and a worthwhile one; it is not evidence that the convention is the right loss |
| **G-P4**, three-leg gradient agreement | closure gradient work | **Three legs are one number reported three times.** The cosine is recoverable from the other two legs to **2.2e-16**, so the third leg adds nothing, and **the treatment the gate exists to catch passes it** | **WITHDRAWN** by the lab on exactly this ground |
| **G-P1** | same | A closed form in four numbers **the document supplies itself** | **Self-flagged** in the record. The lab declared it rather than being caught |
| **R1**, correlation and overlap | same | rho = **+1.0000** and **100 percent overlap** are identities under the gate's own pre-stated null, not findings | **Correctly declared inconclusive** rather than reported as confirmation. This is the right handling and it is what the others should look like |
| **W4's CBFS gate** | `dafoam/ladder-b/W4_ADJOINT_PC_UNBLOCK.md` | FD-versus-adjoint agreement is a property of **the objective as built**, so it is insensitive to whether the objective is the right one | **DEMONSTRATED, expensively.** It **passed while every objective value ran on an inlet overwritten 27 percent wrong** |
| **F4's mesh-draw scatter rule** | F4 hypersonic | **Identically zero by construction**: all eleven ladders use a deterministic structured `blockMesh`, so the draw-to-draw scatter the rule measures does not exist | **DEMONSTRATED by execution: 7.5 core-minutes spent with nothing to measure** |
| **V16's clause C4** | `V16_C4_AMENDMENT_PROPOSAL.md` | The clause requires the check to **state** its false-positive rate rather than to **meet** one, so it is **satisfiable at a false-positive rate of 100 percent** | An amendment proposal exists against it |
| **Monitor signature S13**, as applied in K2b | `docs/standards/MONITOR_STANDARD.md`, found in K2b tonight | It **returns its best possible score on a field that has not moved**, so a dead case scores as a perfectly converged one | Found `fa2c8bb0`, in the rung that also reports the split where the case showing recirculation fails S13 and the case passing S13 never closes its heat balance |
| F6D Option A's control member | `demo-output/website/campaign/F6D_OPTION_A_RESULT.md` | Not a cannot-fail gate: the opposite, and it earns its place here because it is the counter-example. The control moved -0.491 against a 0.25 threshold | **The gate fired and was honoured on its literal reading even though the mechanism it named was shown absent.** "A gate that can be dissolved by post-hoc argument is not a gate." Result VOID (`54dacbb5`) |

### 7.2 Cannot fail as posed, and not demonstrated as such

These are the ones a newcomer should be most careful with, because they carry a
passing verdict on a visible surface.

| Gate | Where | Why it cannot fail as posed |
|---|---|---|
| NASA hump reattachment | Nine-act row 7, F6a reattachment | The row misses by **+13.9 percent** and reads **VALIDATED** / GATE REACHED. **No band is printed and no threshold exists that a larger miss would have crossed.** The deviation is labelled "documented SST bias, expected" after the number was read |
| CRM wing-body drag | Nine-act row 9 | Same code, same downloaded mesh, same unmodified `daOptions` as DAFoam's own tutorial, agreeing to **0.007 percent**, and chipped **VALIDATED** against `lab.py:456`, which states this path never grants it. It can catch a broken pipeline; it cannot catch a modelling error |
| F6a's cross-check against NASA's own SST CFD | `F6a_nasa_hump.md` | Same closure, same benchmark, same experiment-matched geometry, agreeing to +0.06 percent. A reproduction, not an independent test |
| F6a's scorer self-check | same | Scores the shipped baseline field against the shipped floor on the shipped mesh. A 0.02 percent field-vs-field MAE is a re-read of the same data |
| F9 Gate 1 | `F9_pulsatile_valve.md` | Grades an unsteady run against a curve fitted to the same solver, same mesh, same geometry. The record's own line: **"F9 is verified in part and validated against nothing"** |
| F6c duct secondary flow | `F6c_duct_vs_dns.md` | The **inverse** case, and it belongs here: the linear Boussinesq closure has zero normal-stress anisotropy by construction, so RANS returns ~1e-15 percent for any mesh, any convergence, any setup. **This gate cannot PASS.** It carries information about the closure, not about the solver, and the record reports it as measured |
| F4 Gate 3 | `F4_hypersonic_blunt_body.md` | **Skipped, not failed.** The band is pre-registered and no gate case was ever built. The warm-up crashed, then was found never wall-resolved, y+ 86 against a design of 1 |
| F12, all five gates | `F12_PREREGISTRATION.md` | **Skipped, not failed.** The design is unusually falsifiable and nothing has run. `CALIBRATION_SCORECARD_2026-08.md:264` counts it an **ORPHANED pre-registration** |
| `scripts/case_preflight.sh` | `docs/INSTRUMENT_INTEGRITY_LEDGER.md` section 4.1 | **The canonical skipped-not-failed instrument.** Its PASS does not distinguish "5 of 5 checks ran and passed" from "2 of 5 ran and 3 were skipped for missing inputs". The two skip notes are the only evidence anything was skipped, and `--quiet`, which is exactly how `launch_solve.sh` invokes it, suppresses them. It is not a rubber stamp (a `0/U` with no `class` entry gives FAIL, exit 1); **it simply counts nothing** |
| `audit_transcripts.sh` | same, section 4.2 | Reports `clean: no banned vocabulary in any act transcript`, exit 0, over an **empty directory** and over **a path that does not exist**. This is the pre-filming discretion gate, whose own header calls the no-reveal rule "the single most important rule" |
| A2 MACH wing, **as originally reasoned** | `dafoam/ladder-a/A2_mach_tutorial_wing.md` | A near-miss rather than an instance. It was graded inside a **"1 to 12 percent normal band"** calibrated on a number that W5 later measured to be about **99 percent rotation defect**. The gate was real; the yardstick was not. W5 withdrew the headline |
| F1's two GATE REACHED rows | `dafoam/ladder-a/A3_onera_m6.md` | **No pre-declared RMS tolerance exists anywhere in the record.** GATE REACHED was asserted after the numbers were read |
| F3, F4 Gates 1 and 2, F5a batch | those records | Same shape, less starkly: exact-theory comparisons with no declared band. They are close, and "close" is assigned afterwards |

### 7.3 A gate whose evidence its own tooling deletes

`scripts/heat_balance.py:770` runs
`shutil.rmtree(os.path.join(case, "postProcessing"), ignore_errors=True)` before
its own postProcess pass, and that directory is the in-pass function-object
history. Twelve K2e cases lost `hotFlux`, `coldFlux`, `Umax` and `Tcentre` the
moment they were audited. Filed as **D375** at `e4a977ef`, with **D376** (no path
for a compressible case) and **D377** (six refusal paths exit 1, which the
docstring reserves for "the balance did not close", so a caller cannot tell a
refusal from a finding) beside it. Re-derived here: **`git ls-tree -r HEAD`
returns zero tracked `postProcessing` paths anywhere under
`docs/campaigns/F14-cooling-ladder/`.** K0c's convergence gate survives only
because `check_convergence.py --monitor-regex` reads solver logs rather than that
directory, and the logs are committed. That is luck, not design.


### 7.4 The opposite pole, and a newcomer should read it before the list above

**The strongest gate in this lab is the closure stability and physicality
audit**, `research/closure/md/closure_challenge_stability_physicality_audit.md`
at `0869284e`. It is what good looks like here, and every property that makes it
strong is a property the hollow gates lack.

| Property | How this gate has it |
|---|---|
| The referent is **exact theory**, not a fit | It grades **continuity** on the corrected fields. Continuity is not a number anyone chose |
| The instrument is **independently validated first** | The gradient reconstruction `sdk/scripts/closure_mesh_recon.py` was validated at **r = 0.9997 to 1.0000** before it was used to grade anything |
| The lines are **pre-registered** | Both materiality lines are stated in section 0 before the run, and the verdicts are given against those lines and not against what was found |
| It **can fail, and it did** | **MATERIAL on both.** Continuity error degrades **58.0x** on one PH-corrected case and **123.6x** on another; **35 of 36** corrected fields degrade |
| The finding runs **against the lab's own interest** | The sign is against us. This is a result that makes the lab's own entry look worse and it was published anyway |
| The referent is one the scoring metric **structurally cannot see** | The benchmark's metric enforces continuity on face fluxes, not on reconstructed cell fields, so nothing in the scoring would ever have surfaced this. The gate reaches past the metric rather than restating it |

**That last row is the whole lesson.** A gate that measures something its own
scoring cannot see is the opposite of a gate whose quantity is fixed by the
thing it tests. When designing a new gate here, the question to ask is not "will
this pass" and not even "can this fail", but **"does the reference come from
somewhere the measurement cannot reach?"**
---

## 8. What would move the most rows

Ordered by rows moved per unit of cost. **None of this is a compute request.**
Seven of the nine items below cost no core-minutes at all, which is the most
surprising thing this audit found.

| # | Action | Rows it moves | Cost |
|---|---|---|---|
| 1 | **Read NACA Report 1191 and settle which Strouhal form governs Re 100.** The repo holds two mutually inconsistent versions of its own cited reference and the most-filmed gate in the lab passes against the unattributed one, missing by 5.54 percent against the cited one | 1 row, on the highest-visibility surface the lab has | **Zero.** NACA reports are public domain on the NASA NTRS. Cheapest row on this page |
| 2 | **Make row 9 of the nine-act table carry its own qualifier.** The correct declaration already exists in `ladder-a/A6_crm_wingbody.md:154` and does not travel to the table. This is not a new finding and not a new number; it is a transmission repair | 1 row, plus the class it stands for: **four of the external-referent audit's seven live findings are transmission losses, not gaps** | **Zero.** A caption change on a generated table |
| 3 | **Buy the eight raised-floor primaries, after reading Wibron 2019 free first.** Today F14 rung K2c-B has **no gate rows at all**, and any tile-supply solve is TREND-ONLY however well it converges | An entire sub-rung, from zero rows to a gate. Also arms K2a section 2.2's tile-momentum arbitration | Roughly **8 x 15 to 35 USD**, or one library route. Zero compute. Largest single unblock here |
| 4 | **Declare the bands that were never declared.** F1's two rows, F3's five, F4's Gates 1 and 2, F5a's batch and F6a's two all compare against an obtained reference with **no pre-registered tolerance**, so "close" is assigned after the number is read | Roughly **12 rows move from ARGUED to a real gate** without a single new solve | **Zero compute.** One pass over records that already hold every number |
| 5 | **Acquire de Vahl Davis 1983 or Le Quere 1991, and Betts and Bokhari 2000** | 4 UNGRADED K0c stratification rows become gradeable; K0c's turbulent heat-transfer row becomes armable. The Betts row has a **zero-cost alternative**: derive wall heat flux from the near-wall temperature files already committed, with the increment stated | Roughly **80 to 90 USD** for two articles, or the MIT access route |
| 6 | **Record the extraction route for `cd: 0.285`.** The paper is real; the number's route from paper to file is not recorded anywhere, and a sibling file from the same import commit was caught being a hand-set estimate wearing a citation | 3 rows that currently carry a citation they cannot support: nine-act row 6, F10's Ahmed 25 VALIDATED gate, W3's Ahmed preregistration | Roughly **30 USD** and one provenance note |
| 7 | **Fix `scripts/case_preflight.sh` and `audit_transcripts.sh` to answer "did the check run" before "what did it find".** Both currently return a green over an empty or nonexistent input set, and one of them is the pre-filming discretion gate | 2 instruments, and every gate downstream of them | **Zero compute.** The three-valued pattern is already written and wired in `K1c` and `check_convergence.py`; this is applying it |
| 8 | **Execute D375, D376 and D377 on `scripts/heat_balance.py`.** It deletes the case's `postProcessing/` before its own pass, has no path for a compressible case, and six of its refusal paths exit 1 where the docstring reserves 1 for "the balance did not close" | Restores the designated evidence for every thermal convergence gate the campaign runs, and lets the instrument audit the solver class the Boussinesq limit points the next rung at | **Zero compute.** All three filed at `e4a977ef`; the first is one line plus a decision about archive size |
| 9 | **Run F14's K0c turbulent rung.** Its reference is **already in hand**: 22 primary experimental data files from the ERCOFTAC Case 079 archive, byte-identical, SHA-256 recorded | **The only rung in the cooling campaign eligible for VALIDATED**, and one of very few anywhere in the lab whose experimental reference is already obtained, retained and machine-readable | Real compute, and **the owner's authorization, which has not been given.** Named here as the highest-value authorized-compute request on the board, not as a request |

**The one-sentence version.** This lab's binding constraint is not compute and is
not solver capability. It is **reference acquisition and reference transmission**:
getting the published number into the building, and keeping it attached to the
verdict once it is there.

---

## 9. What this page does not establish

- **No number here was re-derived from a solve.** Every value is quoted from the
  record that owns it. Where I re-derived something myself it is marked
  "re-derived here", and there are four such places: the `postProcessing` count
  under F14, the function-object write counts in K0c's logs, the nine-act
  artifacts' tracked status, and the ID sets in section 1.1.
- **It does not audit whether the numbers are right.** It audits what they were
  checked against. A row can be reference-obtained, in band, failable and still
  wrong.
- **It does not grade independence.** Every commit on this box carries one
  identity. Where a record says a grade was taken by a non-author, this page
  repeats the claim and does not verify it, per D130 and D173.
- **It is a frame, not a constant.** Two commits landed while it was being
  written and one of them changed a row in it. Re-derive.
- **It does not replace the campaign records.** Every row is a pointer. The
  record holds the derivation, the controls, the cost and the caveats, and this
  page deliberately holds none of them. What it holds is the one thing no
  individual record can show: the shape of the whole.

## Related

- `docs/charters/VERIFICATION_CHARTER.md` sections 1, 2a, 3, 9. The rules this
  page measures against.
- `sdk/chief_engineer/lab.py:178` to `:200`. The tier definitions, in code.
- `docs/EXTERNAL_REFERENT_AUDIT.md`. Classifies verifications as EXTERNAL,
  SELF-REFERENTIAL or NONE. This page joins that axis to tier and failability.
- `docs/FAIL_OPEN_GATE_AUDIT.md`, `docs/FAIL_OPEN_GATE_POPULATION.md`. The
  instrument-level half of section 7.
- `docs/INSTRUMENT_INTEGRITY_LEDGER.md`. Where the skipped-not-failed instruments
  are reproduced firsthand.
- `demo-output/website/campaign/NOT_PASSING_REGISTER.md`. What is not passing,
  maintained by the lab rather than by this audit.
- `docs/campaigns/F14-cooling-ladder/README.md`. The model for what a campaign
  record should look like, and the only one using the NOT OBTAINED convention.
