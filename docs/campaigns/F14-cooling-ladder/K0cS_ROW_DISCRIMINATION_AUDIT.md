# K0cS row-discrimination audit: which graded rows separated the hypothesis from its absence

**Campaign F14, cooling ladder. Audit executed 2026-08-18.**
**Frame:** the figures were read from `gate_k0cs.json`, `gate_k0ct.json` and
`gate_k0c.json`, each verified **byte-identical to HEAD** by `git hash-object`
against `git rev-parse HEAD:<path>` at frames `d9475c07` and `da6c28e9`, and the
reading was identical at both. The run trees, not a moving HEAD, are the anchor.
**Zero compute.** Every number below was read from run trees already on disk;
no solver ran and nothing was queued. Instrument:
[`scripts/check_row_discrimination.py`](../../../scripts/check_row_discrimination.py),
which regenerates every table here with `--verbose`.

**Nothing here was submitted, sent, filed, uploaded or registered. Submissions
were PARKED.**

---

## 0. Verdict

| | |
| --- | --- |
| Registered rungs | **6** |
| Cells evaluated (graded row x graded arm, against a declared null arm) | **35** |
| Cells NOT measured, and why is in section 6 | **29** |
| Cells that separated the hypothesis from its absence | **14 of 35** |
| Cells that carried no evidence about the hypothesis in either direction | **14 of 35** |
| PASS cells on graded arms | **17** |
| **PASS cells that the trivial baseline also passed** | **8 of 17** |

**Eight of the seventeen passes this audit could evaluate - 47 percent - were
read as evidence about a hypothesis that they did not separate from that
hypothesis being absent.** That figure was measured over 35 cells on four
rungs. It was not extrapolated to the other gates in the lab, and section 6
names every population this audit could not reach.

**The rung-level readings, stated without softening:**

| Rung, graded arm | grade rows | discriminated | hollow passes | passes that carried evidence |
| --- | ---: | ---: | ---: | --- |
| K0cS, kOmegaSST fine | 10 | 2 | **2** | **0 of 2** |
| K0cS, kEpsilon fine | 10 | 6 | 1 | 3 of 4 |
| K0cT-hi, kOmegaSST fine | 9 | **1** | **4** | **1 of 5** |
| K0c-Ra1e5, laminar buoyant fine | 6 | **5** | 1 | 5 of 6 |

---

## 1. The rule, and where it stopped

`VERIFICATION_CHARTER.md` section 2a already refused one kind of hollow row: a
quantity derivable by construction from its own inputs was an IDENTITY and could
never be gated on. That rule caught a row whose value was fixed by **algebra**.
K0cS found the sibling, whose value was fixed by nothing **the hypothesis
controlled**. The full statement of the new rule and its boundary was appended
to that charter as section 2c.

The boundary, because a rule with a boundary nobody can state gets applied
wrongly:

- A **GRADE row** had its verdict read as evidence about the hypothesis under
  test. Its referent came from outside the run. Its FAIL withdrew the
  **hypothesis**. It was counted in the rung's "N of M rows" tally. The rule
  covered these and only these.
- A **GUARD row** had its verdict read as evidence about the **run**:
  conservation closure, convergence, a boundary condition applied, a marker
  written. Its FAIL withdrew the **run**, not the hypothesis. It was supposed to
  pass for the treatment and for the trivial baseline alike, and demanding that
  it discriminate would have been section 17a's over-reach.

The question that separated them, asked at creation: **if this row fails, what
is withdrawn - the hypothesis, or the run?**

---

## 2. What was measured, and the classes

Each (graded row x arm) cell was classified against the rung's declared null
arm. Separation was expressed in units of the row's own band, so a separation of
1.000 meant the two arms sat exactly one band apart.

| class | meaning |
| --- | --- |
| **DISCRIMINATES** | the verdict differed between the treatment and the null arm, in either direction |
| **HOLLOW PASS** | PASS for the treatment and PASS for the null arm. **The PASS was not evidence about the hypothesis** |
| **INERT FAIL** | GATE FAIL for both, less than one band apart. The row failed for a reason the hypothesis did not control, so the FAIL was not evidence against it either |
| **BOTH FAIL, SEPARATED** | GATE FAIL for both, one band or more apart. The row graded; both arms were simply outside it |
| **UNMEASURED** | no null value on disk. Reported in its own bucket and never counted clean |

---

## 3. K0cS, square cavity, Ra 1.58e9

Null arm **`C1_laminar`**, registered as a RECOGNITION control in
`K0cS_PREREGISTRATION.md` **before the run**, with the turbulence model switched
off. C1 ran on the coarse mesh; the graded verdict was taken on the fine mesh,
so the coarse arms were carried as the mesh-matched comparison and are shown
beside the graded ones.

### 3.1 kOmegaSST, fine mesh - the graded arm

| row | quantity | class | treat | null | separation |
| --- | --- | --- | --- | --- | ---: |
| G1 | Nu_hot | **INERT FAIL** | GATE FAIL | GATE FAIL | 0.048 bands |
| G2 | Nu_cold | **INERT FAIL** | GATE FAIL | GATE FAIL | 0.591 |
| G3 | Nu_bot | DISCRIMINATES | GATE FAIL | PASS | 0.520 |
| G4 | Nu_top | DISCRIMINATES | GATE FAIL | PASS | 0.199 |
| G5 | Nu_mid_hot | **HOLLOW PASS** | PASS | PASS | 0.125 |
| G6 | Nu_max_hot | **INERT FAIL** | GATE FAIL | GATE FAIL | 0.196 |
| G7 | Sp | **INERT FAIL** | GATE FAIL | GATE FAIL | 0.440 |
| G8 | Vpeak | BOTH FAIL, SEPARATED | GATE FAIL | GATE FAIL | 1.012 |
| G9 | Vpeak_X | **HOLLOW PASS** | PASS | PASS | 0.244 |
| G10 | uv_peak | BOTH FAIL, SEPARATED | GATE FAIL | GATE FAIL | 1.091 |

**Both of kOmegaSST's two passes were hollow, which is D411 re-derived from the
cell values rather than from the pass sets.** Four further rows failed for both
arms less than a band apart, so on this arm **six of ten rows carried no
information about the closure in either direction.**

**On the mesh-matched comparison G5's separation was 0.000 bands.** The coarse
kOmegaSST solve returned `Nu_mid_hot = 53.03220894956695` and the laminar
control on the same mesh returned `53.028986872242` - **0.0055 percent of the
reference apart**, against a 12 percent band.

### 3.2 kEpsilon, fine mesh - the graded arm

| row | class | treat | null | separation |
| --- | --- | --- | --- | ---: |
| G1 | BOTH FAIL, SEPARATED | GATE FAIL | GATE FAIL | 3.345 bands |
| G2 | BOTH FAIL, SEPARATED | GATE FAIL | GATE FAIL | 3.937 |
| G3 | DISCRIMINATES | GATE FAIL | PASS | 1.396 |
| G4 | DISCRIMINATES | GATE FAIL | PASS | 1.007 |
| G5 | DISCRIMINATES | GATE FAIL | PASS | 3.964 |
| G6 | **INERT FAIL** | GATE FAIL | GATE FAIL | 0.120 |
| G7 | DISCRIMINATES | PASS | GATE FAIL | 1.771 |
| G8 | DISCRIMINATES | PASS | GATE FAIL | 2.850 |
| G9 | **HOLLOW PASS** | PASS | PASS | 0.038 |
| G10 | DISCRIMINATES | PASS | GATE FAIL | 2.884 |

Six of ten discriminated, and three of kEpsilon's four passes carried evidence.
K0cS_RESULTS.md section 1 said so from the pass sets; the cell measurement
agreed and put a number on it.

### 3.3 G9 could not have failed on this rung

`Vpeak_X` returned **five distinct values across the ten solved cases.** Five of
the ten returned the identical `0.006076756898666667` - kOmegaSST coarse,
LaunderSharmaKE coarse, and the three kOmegaSST sensitivity arms C2, C3 and C4 -
and two more returned the identical `0.006921195513333333`: **the laminar
control and kEpsilon coarse, which agreed with each other to every digit.**

| | |
| --- | --- |
| full range of `Vpeak_X` across all ten cases | **0.00122** |
| the row's band | **0.005** |
| band divided by the entire spread the rung produced | **4.1x** |
| largest deviation any of the ten cases produced | **0.000968, 19.4 percent of the band** |

**No case on this rung got more than a fifth of the way to failing G9.** The row was
hollow for both graded models and it was passed by every control as well. It sat
at the intersection of the two roads: near-identity in the section 2a sense, and
non-discriminating in the section 2c sense.

### 3.4 The REFUSED model, measured from a direction that never looks at nu_t

`S_LS_f` was the LaunderSharmaKE fine case that K0cS **REFUSED** on its
convergence criterion, and whose eddy viscosity had collapsed four orders of
magnitude below molecular. Measured against the laminar null:

| arm | rows that discriminated | maximum separation over all ten rows |
| --- | ---: | ---: |
| `S_LS_f` fine | **0 of 10** | **0.642 bands** |
| `S_LS_c` coarse | 1 of 10 | 0.679 bands |

**Zero of ten rows separated LaunderSharmaKE-fine from no turbulence model at
all, and no row got past two thirds of a band.** That corroborated section 4 of
`K0cS_RESULTS.md` by a route that never reads `nu_t`.

**And the coarse mesh carried a finding the rung did not record.** `S_LS_c` held
a domain-maximum `nu_t/nu` of **17.3** - a real eddy viscosity, not a collapsed
one - and still sat inside 0.679 bands of the laminar control on every one of
the ten graded quantities. **LaunderSharmaKE was already indistinguishable from
laminar on the coarse mesh, where the record had located the laminarisation at
the fine mesh only.** `S_LS_c` also failed the convergence criterion (3.09 and
2.76 percent), so its numbers were a time-varying quantity sampled once; that
widens its own error bars and is why this is recorded as an observation and not
as a verdict.

---

## 4. K0cT-hi, tall cavity, Ra 1.43e6

Null arm **`C1_hi_c_laminar`**, the rung's own registered RECOGNITION control.
Graded arm `T_hi_f`.

| row | quantity | class | treat | null | separation |
| --- | --- | --- | --- | --- | ---: |
| R9 | core stratification S | BOTH FAIL, SEPARATED | GATE FAIL | GATE FAIL | 3.609 bands |
| R10 | peak upward velocity (magnitude) | BOTH FAIL, SEPARATED | GATE FAIL | GATE FAIL | 9.725 |
| R11 | peak upward velocity (**location**) | **HOLLOW PASS** | PASS | PASS | 0.577 |
| R12 | peak downward velocity (magnitude) | BOTH FAIL, SEPARATED | GATE FAIL | GATE FAIL | 8.176 |
| R13 | peak downward velocity (**location**) | **HOLLOW PASS** | PASS | PASS | 0.577 |
| R14 | mid-width T at y/H = 0.30 | **INERT FAIL** | GATE FAIL | GATE FAIL | 0.316 |
| R15 | mid-width T at y/H = 0.50 | **HOLLOW PASS** | PASS | PASS | 0.886 |
| R16 | mid-width T at y/H = 0.70 | DISCRIMINATES | PASS | GATE FAIL | 0.829 |
| R17 | antisymmetry defect | **HOLLOW PASS** | PASS | PASS | 0.910 |

**One of nine rows discriminated. Four of the arm's five passes were hollow.**
The single pass that carried evidence about the closure was the mid-width
temperature at y/H = 0.70.

**R17 is the most fixable row in this audit.** The graded solve returned an
antisymmetry defect of **0.0055 percent** and the laminar control returned
**9.10 percent**, against a band of **10 percent**. The quantity moved 0.91 of a
band; the band was wide enough to admit the null arm with 0.9 percentage points
to spare. **The row's quantity was sound and its band was not.** Tightening the
band to 5 percent would have made it discriminate on the numbers already on
disk, at zero compute.

**R11 and R13 are the same shape as K0cS's G9**, and that is the finding that
travels. `Vpeak_X` on the square cavity and both velocity-peak **locations** on
the tall cavity were hollow passes - **the same physical quantity, on two
geometries, three Rayleigh decades apart.** A velocity peak's location did not
grade a turbulence closure in either cavity.

The classification was checked against the mesh confound. `T_hi_c`, mesh-matched
to the coarse null, returned the identical class on all nine rows, and `S_SST_c`
returned the identical class on all ten K0cS rows. **The result was not a mesh
artefact.**

---

## 5. K0c-Ra1e5, de Vahl Davis cavity - the counter-example, and a live D3

Null arm **`C1_Ra1e5_m128_g0`**, an exact twin of the graded fine case with
`constant/g` set to `(0 0 0)`, registered as a RECOGNITION control before it
ran. With no buoyancy source the cavity solved pure conduction.

| row | class | treat | null | separation |
| --- | --- | --- | --- | ---: |
| Nu_avg | DISCRIMINATES | PASS | GATE FAIL | **78.1 bands** |
| Nu_max | DISCRIMINATES | PASS | GATE FAIL | 43.8 |
| Nu_min | DISCRIMINATES | PASS | GATE FAIL | 18.7 |
| u1max | DISCRIMINATES | PASS | GATE FAIL | 49.9 |
| u2max | DISCRIMINATES | PASS | GATE FAIL | 50.3 |
| energy_balance | **HOLLOW PASS** | PASS | PASS | **0.000** |

**Five of six rows discriminated, at separations of 19 to 78 bands.** This rung
is what a discriminating gate looked like, and it is the reason this audit's
figures are a statement about particular rows rather than a check tuned to
condemn everything.

**The sixth row raised the audit's only D3-GUARD-GRADED.**
`docs/VALIDATION_INVENTORY.md` section 7.1 lists all four K0c energy-balance
rows as a **demonstrated** identity, and records that the rung reported them and
excluded them from its evidence. **The comparator output still carried all four
inside `gate_k0c.json`'s `gate_rows`, its graded tally, with `passed: true`.**
The g = 0 control put the number on it: **energy_balance was the only one of the
six rows the null arm also passed**, at a separation of 0.000 bands
(1.95e-05 against 2.76e-05 percent). The prose excluded the row; the machine-
readable tally did not, and a later reader counting `gate_rows` would have
counted 24 graded rows where 20 graded anything.

**What would settle it:** drop the four energy-balance entries from `gate_rows`
into a `reported_never_graded` block, which is what K0cS's own comparator
already did for its heat balance. No re-solve, no re-grade, and the 20 remaining
rows keep their verdicts unchanged.

---

## 6. What could NOT be measured, and why

**This audit measured 35 cells. `docs/VALIDATION_INVENTORY.md` counted 139 rows
over 135 distinct gates. Nothing here was extrapolated to the rest.**

| population | size | why it was not measured |
| --- | ---: | --- |
| **K0cT-lo**, Ra 0.86e6 | 9 rows x 1 arm | The turbulence-off control C1 was run at the **hi** rung only. A null at a different Rayleigh number is a different null and was not borrowed |
| **K0c at Ra 1e3, 1e4, 1e6** | 18 rows x 1 arm | `C1_g0` twinned the Ra = 1e5 case only |
| **K2e**, Boussinesq against variable density | 30 cases | **Excluded by design, not by absence.** Every K2e row was already a difference between a treatment and its null on identical geometry, so a discrimination test on top of it would have restated its own input. This is boundary case 2 of the rule |
| **Every gate outside these four rungs** | the remainder of the 135 | Enumerated rather than assumed. A complete sweep of every `.json` under `verification/runs/`, `research/` and `demo-output/` - **550 files** - found **8** carrying a per-case map at all, and of those **2** carried a case whose name marked it a null arm (`C1_laminar`, `C1_hi_c_laminar`). Two more (`gate_k0c.json`, `gate_k2e.json`) were adjudicated by hand and are in the table above. **The rest of the lab's gates have no machine-readable null arm on disk**, so their discrimination is unknown - not clean, not violating, unknown |

**Candidates that a hand registration could reach at zero compute, and were
not registered here:** `verification/runs/W1_hump_runs/` holds a stock-SST arm
beside two `a1` variants, which is a treatment-and-null pair for "does moving
`a1` help"; `research/closure/data/closure_challenge_round5_qcr_forward.json`
holds an `AR_7_Ret_180_sst` baseline beside four QCR arms. Neither carries its
bands in machine-readable form, and D383 already records that several rows in
that family carry no pre-registered tolerance at all, so choosing a band now
would be choosing it after the numbers were read. **They were named and left
unmeasured rather than measured against a band invented today.**

---

## 7. The check and its controls

`scripts/check_row_discrimination.py`, run with `--selftest`, planted **9 row
shapes into a synthetic gate document: 5 that had to fire and 9 that had to
survive**, over a population of 20 synthetic cells. Every one behaved.

**The negative controls are the half that matters**, because a rule that
condemns the whole inventory gets scrolled past:

| shape | outcome |
| --- | --- |
| GRADE row PASS/FAIL and FAIL/PASS | survived, DISCRIMINATES |
| GRADE row FAIL/FAIL four bands apart | survived, BOTH FAIL SEPARATED - the row graded, both arms were outside |
| GUARD row showing the exact hollow-pass signature | **survived** |
| the same hollow shape on an **ungraded** arm | survived - it was measured, and a measurement is not a verdict |
| a row whose null arm never ran | reported **UNMEASURED**, never clean |
| a rung with no null arm | reported **NOT MEASURED** with its cell count, never PASS |
| an A/B-by-construction rung | excluded with its reason stated |

**The live negative control ran on real data.** `theta_centre` on K0cS read PASS
for kOmegaSST and PASS for the laminar null 0.193 bands apart - the exact hollow
signature - and it was correct that it did: Tian p. 862 states a Boussinesq
solve returns 0.5 by symmetry, so the row measured the non-Boussinesq defect and
never the closure. It was declared GUARD and it survived. **D3 is what keeps
that exemption honest**: the same declaration applied to a row sitting in the
graded tally fired, on K0c, on real data.

**This check is not the mutation control and does not replace it.** K0cS's own
mutation control had already stamped `every_row_reachable_both_ways: true` over
all twenty of its graded rows, and it was right. It perturbs the **measured
number** and asks whether the verdict *can* move. This check perturbs the
**hypothesis** and asks whether the verdict *does* move. Twenty of twenty passed
the first; eight of twenty carried evidence under the second.

---

## 8. Cost

**Zero.** Ten K0cS cases, nine K0cT cases and eleven K0c cases were already
solved and committed. No solver was launched, no queue was touched, and no part
of the $25 standing authorization was drawn.

---

## 9. What this audit does NOT establish

- **It does not withdraw any verdict.** K0cS was GATE FAIL for both graded
  models before this audit and remained so after it. What moved is which rows
  may be cited as the reason.
- **It does not say the hollow rows were wrong.** G5, G9, R11, R13, R15 and R17
  reported the numbers they measured, correctly. They did not separate a closure
  from no closure, which is a different defect and the only one claimed here.
- **It does not transfer to the 135 gates.** Section 6 is the honest boundary
  and it is a large one.
- **It does not validate kEpsilon or the K0c laminar solver.** A row that
  discriminates is a row worth grading on; it is not a promotion of whatever
  passed it.
- **A wrong null arm gives a wrong answer with no warning.** Each null above was
  declared with the record that registered it, before its own run. A null chosen
  after the fact would make this instrument the thing it exists to detect.
