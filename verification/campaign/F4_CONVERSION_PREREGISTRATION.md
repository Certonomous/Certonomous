# F4 hypersonic blunt-body suite — CONVERSION PRE-REGISTRATION

**FROZEN BY THIS COMMIT. Nothing below may be altered after the first solver
starts; changes land only as dated addenda that cannot alter a gate, threshold,
cap or label, and originals are struck, never rewritten (standing rule 2).**

**Freeze history, recorded rather than tidied away.** This document was drafted,
held **uncommitted** through two cfd-supervisor check-1 diff reads of its
grading path, and frozen only after the second returned CLEARED. The first read
**found a real defect** in the grader (§7) and it was repaired **pre-compute, at
zero cost**. Holding the pin across the review is the whole reason the repair was
legal: rule 2 fixes the grading path *at the pre-registration commit*, so
freezing earlier would have frozen the defect.

**Written 2026-08-25, before any solver in this conversion has started.**
**Frame:** repo `/home/ubuntu/Certonomous`. **Team:** cfd. **Lane:** lab-lane
under cfd-supervisor.

**Rule-2 condition, to be checked by `test -e` in the freeze commit's own shell
invocation and not recalled:** the run root
`verification/runs/F4_runs/conversion_2026-08-25/runs/` **does not exist**; no
case directory, no `0/`, no time directory and no `log.rhoCentralFoam` exists
beneath it. The condition as checked at 2026-08-25T21:10:19Z and recorded in
`verification/runs/F4_runs/LANE_REPORT_F4_STATE_2026-08-25.md` §4 was **ABSENT**
for all three candidate roots.

**Why this document exists.** Two gate verdicts recorded as **`PASS`** on
2026-07-28 were graded against bands written after their numbers were known.
Under standing rule 2 the freeze *is* the evidentiary content of a
pre-registration. This document fixes the gate, the reference, the band, the
cap, the label vocabulary and the grading path **before** the re-run.

**WHAT THIS DOCUMENT IS NOT MOTIVATED BY, STATED FIRST.** The text *"CFD team —
Re-run under frozen pre-registrations, <40 core-min each: F3, F11, F4 — the
early PASSes that lack prereqs convert to HOLDS"* is **a cfd brief's paraphrase,
NOT Sanaa's words.** Its attribution was withdrawn on `docs/LAB_STATE.md:4385`
and, on the artifact that bore it, in `F3_CONVERSION_PREREGISTRATION.md`
AMENDMENT 1 §A1.1, whose own re-run of the source search found the text
reproduced in **exactly one commit message in the entire history — `2bf4915a`,
the F3 pre-registration's own freeze commit.** Three consequences bind this
document:

1. **It is never cited here as her words**, and never as a compute authorisation.
2. **Its "<40 core-min" figure does NOT set this document's cap.** The cap in §9
   is derived from F4's own measured cost basis and from nothing else (L-309: an
   attribution authorising spend must carry its source when recorded).
3. **`HOLD` is not in the rule-1 vocabulary and is not what this conversion
   does.** What is owed is narrower: re-run the gates under a frozen
   pre-registration so that whatever verdict issues is defensible. **Nothing
   here is pre-decided** — see §12's outcome map, and §12.1, where this lane
   records its prediction *before* the run rather than after it.

---

## 1. The defect being repaired, in the record's own numbers

`verification/campaign/F4_hypersonic_blunt_body.md` (2026-07-28, repo @
`b23138d`) records **`PASS` on two gates** across nine `rhoCentralFoam` runs.
There is no pre-registration for either. The only F4 pre-registration at HEAD is
`F4_SIGFPE_STEP01_PREREGISTRATION.md`, a SIGFPE crash diagnostic on a *different
case tree* whose own §0 forbids issuing any `PASS` from it.

**Two specific defects, and they are worse than "no band existed":**

**(a) Gate 1 was graded `PASS` over a triple that standing rule 5 forbids
grading at all.** §4's own table records standoff as **non-monotone** with
refinement — M=6: −0.33 → −0.60 → **+2.06 %**; M=8: +6.62 → −1.69 → **+0.70 %**
(coarse→medium→fine). Rule 5 clause 2 makes a `DIVERGENT`, `STAGNANT`,
`OSCILLATORY` or `EXACT` triple **`NOT A RESULT`**, whatever the value, and
forbids quoting a GCI when the three values are not monotone. The 2026-07-28
record issued a `PASS` and attached the caveat as prose: *"Verdict: PASS, with
the above caveats stated plainly rather than buried."* Rule 1 is explicit that
honesty is carried by the value and the label, **never by adjectives**.

**(b) Gate 2 was graded `PASS` against NO THRESHOLD AT ALL.** §5's verdict reads
*"PASS — clean, near-monotonic grid convergence at all three Mach numbers"*, and
the Summary table's **Deviation column for Gate 2 is literally `—`**. There is no
band, no threshold and no reference value the RMS was required to fall within.
A verdict with no threshold is not a gate; it is a description.

**(c) The 2026-07-28 run recorded NO RETURN CODE — anywhere.** Found while
verifying the §7 repair end to end: pointed at the nine real cases the grader
refuses all nine at its *first* clause, because **there is no `RC.txt` in the
2026-07-28 tree at all.** Rule 4's first clause is `rc = 0`, and that record's
completion rests on the runner's own `solver_completed_to_endTime` field in
`result.json` — **the runner's judgment of its own success, which is exactly
what a grader must not trust.** The conversion's launcher writes `RC.txt`,
`sync`s, and the grader **reads it back rather than inferring it**; `set -e`
does not gate at tool top level nor inside `( set -e; … )`, so an inferred rc is
not an rc.

**One thing the old record did honestly, and it is preserved here.** §4 states
that M=8 fine is **not resolved above its own noise floor** (deviation +0.70 %
against snapshot scatter 0.8 %), and §3 discloses a real detector failure mode —
at θ≈60° the detector *"pins `standoff` at the domain edge (0.70 = R_top−R) — at
every resolution level, including fine."* **That disclosure is load-bearing for
this document**: it is the empirical proof, in §6.1, that this gate quantity is
not censored into passing.

---

## 2. FULL DISCLOSURE — every measured value this lane had already seen when it
   wrote the bands below

**Naivety is impossible here and this lane does not claim it.** Before writing a
single band, this lane read `F4_hypersonic_blunt_body.md` in full. The values
already seen are listed exhaustively so that no band below can later be defended
as having been written in ignorance, and so the supervisor can re-derive any of
them independently rather than accept an assurance.

**Standoff δ/R, all nine cases (§2 and §4 tables):**

| M | coarse | medium | fine | fine dev vs Billig |
|---|---|---|---|---|
| 6.0 | 0.4380 ± 0.0155 | 0.4368 ± 0.0099 | **0.4485 ± 0.0017** | **+2.06 %** |
| 7.0 | 0.4281 ± 0.0025 | 0.4386 ± 0.0072 | **0.4345 ± 0.0017** | **+2.33 %** |
| 8.0 | 0.4427 ± 0.0125 | 0.4082 ± 0.0030 | **0.4181 ± 0.0033** | **+0.70 %** |

**Cp RMS as % of Cp_max, all nine cases (§5 table):** M=6: 4.48 / 4.21 / **3.91**;
M=7: 4.69 / 3.85 / **3.91**; M=8: 4.08 / 3.89 / **3.87**.

**Also seen:** the nine `ExecutionTime` values from the logs on disk (§9), the
per-station Cp difference profile in §5, and the §3 detector failure mode.

**How the bands below are protected from that knowledge.** Every band in §5 is
produced by **one formula applied uniformly to every Mach number and every
refinement level**, whose only inputs are (i) the Billig reference and (ii) the
radial cell height read out of the written `blockMeshDict`. **No CFD value is an
input to any band.** The formula is implemented in the frozen grader as
`standoff_band_pct()` and its outputs are value-checked in `--selftest`, so the
supervisor can recompute all nine numbers without running a solver. §5.3 states
plainly what this band does and does not discriminate, **including the fact that
a different but also-defensible choice would have flipped two rows** — and why
that choice was rejected on rule-2 grounds rather than on outcome grounds.

---

## 3. The gates, fixed now

Nine cases: M ∈ {6.0, 7.0, 8.0} × level ∈ {coarse, medium, fine}. Three gate
families, each instantiated per Mach number.

| gate | quantity | reference | band | label vocabulary |
|---|---|---|---|---|
| **G-F4-1**-M | Roache triple on standoff δ/R across the three levels | — (a verification gate; no external reference) | rule 5 clause order | `CONVERGING` → proceed to G-F4-2; otherwise **`NOT A RESULT`** |
| **G-F4-2**-M | standoff δ/R at the **fine** level, deviation vs Billig | Billig (1967), §4 | ±§5.1 band, per M | **`PASS`** inside / **`GATE FAIL`** outside / **`NOT A RESULT`** if G-F4-1-M is not `CONVERGING` |
| **G-F4-3**-M | Roache triple on RMS(Cp−Cp_Newton) as % of Cp_max | — (verification gate) | rule 5 clause order | `CONVERGING` / **`NOT A RESULT`** |

**Gate 0 (admissibility, per case, all nine)** — every clause **refuses**, and a
refusal is not a `GATE FAIL`: strict completion (§7), the endpoint-censoring
guard (§6.1), and ladder similarity measured from the written `blockMeshDict`s
(§8).

**Rule 5's one-way door is registered explicitly.** The triple gate can turn a
`PASS` or a `GATE FAIL` **into** a `NOT A RESULT`. It can never turn a
`NOT A RESULT` into a `PASS`. Implemented at `grade_f4.py` `grade_all()`, where
G-F4-2's verdict is overwritten to `NOT A RESULT` whenever G-F4-1 is not
`CONVERGING`, and never in the other direction.

**No verdict from this document is issued on the SWBLI limb — see §14.**

---

## 4. The reference values, frozen to full double precision

Computed by `verification/runs/F4_runs/billig_theory.py` (HEAD blob
`8ae1847e8534e32d952b82353c2341e01c3a15e4`), whose primary source is verified in
`F4_hypersonic_blunt_body.md` §0: Anderson, *Hypersonic and High-Temperature Gas
Dynamics*, 2nd ed., §5.4 Eqs. 5.36–5.38 and §3.3 Eqs. 3.15–3.19, itself citing
Billig, F. S., *J. Spacecraft and Rockets* **4**(6), 1967, pp. 822–823. §0
records that an initial web search returned a wrong coefficient (4.76) and that
the printed primary value (**4.67**) was taken from the textbook page itself.

**Billig cylinder-wedge standoff**, δ/R = 0.386·exp(4.67/M²):

| M | δ/R, full double precision |
|---|---|
| 6.0 | `0.4394656652111482` |
| 7.0 | `0.4245982772504153` |
| 8.0 | `0.4152190114522218` |

**Cp_max, exact Rayleigh–Pitot** (used by G-F4-3's normalisation only):

| M | Cp_max |
|---|---|
| 6.0 | `1.818063718892768` |
| 7.0 | `1.8236917275355162` |
| 8.0 | `1.8273541997099865` |

All six are value-checked to 1e-15 in `grade_f4.py --selftest`.

---

## 5. Where the band comes from — derived, not fitted

### 5.1 The G-F4-2 band: ± one local radial cell at the shock

**The derivation, in one sentence with no CFD input.** The detector locates the
shock at the sample point of maximum |dρ/ds| along a radial line; that line is
interpolated (`interpolationScheme cellPoint`) from cells whose local **radial
height at the shock** is Δr; two shock positions separated by less than Δr
therefore produce the *same* detected locus; so a deviation smaller than Δr/δ is
**below the instrument's resolution and is not a resolved disagreement.**

**Band(M, level) = 100 · Δr(M, level) / δ_Billig(M) percent.**

Δr is computed in closed form from the **written** `blockMeshDict`, not from a
requested value (`MESH_STANDARD.md` §9.2). The dict writes, at line 27 of each
case's `system/blockMeshDict`:

```
hex (0 1 2 3 4 5 6 7) (nTheta nR 1) simpleGrading (1 8.0 1)
```

with the radial span `L = (R_top/R − 1)·R = 0.7` (`make_cylinder_case.py:46`
`R = 1.0`; `:48` `R_TOP_OVER_R = 1.7`) and the expansion ratio
`E = 8.0` (`:56` `RADIAL_GRADING = 8.0`). For a `simpleGrading` block of `nR`
cells, ratio per cell `k = E^(1/(nR−1))`, first cell `h₁ = L(k−1)/(k^nR − 1)`,
cell *i* height `h₁·k^i`; Δr is the height of the cell containing radial
distance δ_Billig from the wall. Implemented as `cell_at_distance()`.

**The nine bands (all value-checked in `--selftest`):**

| M | coarse (nR=20) | medium (nR=40) | **fine (nR=80)** |
|---|---|---|---|
| 6.0 | ±13.3916 % | ±6.4598 % | **±3.1747 %** |
| 7.0 | ±13.8605 % | ±6.6860 % | **±3.2005 %** |
| 8.0 | ±12.7042 % | ±6.4820 % | **±3.2728 %** |

**G-F4-2 is graded at the fine level only**, so the operative bands are
**±3.1747 %, ±3.2005 %, ±3.2728 %**. The coarse and medium bands are tabulated
because the same formula produces them and a supervisor re-deriving the fine
number should be able to check the formula's behaviour across the ladder: **the
band tightens by a factor of ~2 per refinement level, which is the correct
signature of an instrument-resolution band and is asserted in `--selftest`.**

**A second, smaller floor was computed and is NOT the band.** The sample line
carries `nPoints 400` over the same 0.7 span, giving a spacing of
`0.0017543859649122805` R — **fixed at all three levels, because `nPoints` does
not refine with the mesh.** At the fine level this is ~8× smaller than Δr, so the
cell height dominates and the sample-line spacing never binds. It is recorded
here so that a reader knows it was considered and why it is not the band.

### 5.2 No band is registered for G-F4-3, and the reason is the point

**No absolute band is registered on the Cp RMS**, and this is a deliberate
refusal rather than an omission. The quantity is a deviation from **modified
Newtonian theory**, whose accuracy away from the stagnation point has **no
citable uncertainty available on this box**. `F4_hypersonic_blunt_body.md` §5
diagnoses the deviation as a real local-inclination-theory limitation growing
monotonically toward the shoulder, and gives no numerical tolerance for it.

**A band invented for it would be exactly the defect this conversion repairs.**
G-F4-3 is therefore registered as a **verification gate only** — does the
functional converge under refinement, and at what observed order — and issues
`CONVERGING` or `NOT A RESULT`. It issues no `PASS`.

**This is itself the finding about the 2026-07-28 Gate 2 verdict** (§1(b)): that
`PASS` had no threshold, and the honest conversion of a thresholdless PASS is
not a new PASS but a narrower, gradable question.

### 5.3 What this band discriminates — and the alternative that was rejected

**Stated plainly, and before the run.** Against the ±3.17 / ±3.20 / ±3.27 %
fine-level bands, the three deviations this lane has already seen (+2.06 %,
+2.33 %, +0.70 %) all lie **inside**. **So if the re-run reproduces the
2026-07-28 numbers and the triples converge, G-F4-2 would return three
`PASS`es, and this band would not have discriminated among them.**

**A defensible alternative would have flipped two of the three.** Taking the
detector's resolution as ±½ cell rather than ±1 cell — the convention that the
peak can be misassigned by at most half a cell when the true peak lies between
sample points — gives ±1.5873 / ±1.6002 / ±1.6364 %, under which **M=6 (+2.06 %)
and M=7 (+2.33 %) would be `GATE FAIL` and M=8 would `PASS`.**

**The ±1 cell convention is registered, and the reason is rule 2, not the
outcome.** Two shock positions inside one cell are genuinely indistinguishable
to a `cellPoint`-interpolated peak-gradient locus — that is a statement about the
instrument. The ½-cell convention describes an *assignment* error given a
resolved peak, which is a different and weaker claim about a smeared,
shock-captured front spread over several cells. **Choosing between two
conventions after having seen which outcome each produces is precisely the
fitting rule 2 exists to prevent**, so the choice is made on the instrument
argument and recorded here with the rejected alternative and its numerical
consequence in full view. **The supervisor may overrule this choice pre-compute;
after first compute it is closed.**

**What actually bites in this conversion is G-F4-1, not the band** — see §12.1.

---

## 6. Every gate quantity CAN fail and CAN pass — proved on this solver's actual
   on-disk output, with the write path named

**This is the defect class that produced `NOT A RESULT` on ansys-verification's
VMFL059 (a mis-specified gate quantity that could never have passed) and on
F12's P4 (`pressureControl::limit()` censors `p` on the way to disk, so a limited
cell reads exactly AT the bound and never outside it — the registered quantity
could not have been non-zero whatever the run did).** Each gate below is proved
non-degenerate rather than asserted to be.

### 6.1 G-F4-2, standoff — and the censoring that IS present, registered as a refusal

**The write path, named end to end.** `rhoCentralFoam` (vanilla — **not**
`rhoCentralFoamBounded`, which is the binary that clamps) writes `<time>/rho` in
ASCII at `writePrecision 8`. **No bounding or limiting is applied to ρ on this
path**; that is the whole difference between the two solvers, and it is why the
F4 SIGFPE work needed a separate instrumented binary. The `sample` utility then
writes
`postProcessing/sampleDict/<time>/r0_T_p_rho.xy`, `setFormat raw`, four columns.
`find_shock()` reads column 3 and returns `dist[argmax|∇ρ|]`.

**Column order is verified, not assumed.** OpenFOAM names the file after the
fields in the order it wrote them, and the frozen reader **refuses** any file
whose basename does not end `_T_p_rho.xy`. This closes the `coefficient.dat`
trap — a positional read of a column-sorted writer — by construction. The order
was additionally confirmed against physics on the existing output: at the wall,
column 1 = 8.2417, which is the exact M=6 stagnation ratio
`T₀/T∞ = 1 + 0.2·36 = 8.2`; column 2 = 46.7436, the M=6 Rayleigh–Pitot
`p₀₂/p₁ ≈ 46.8`; and column 3 = 7.9402 = `γ·p/T` = 1.4·46.7436/8.2417, the
equation of state for this non-dimensional gas. **Three independent
confirmations, none of them the filename alone.**

**CAN PASS.** At M=6 the band admits δ/R ∈ [0.4255, 0.4535]. The sample line
carries 400 points over [0, 0.7] at spacing 1.7544e-3, so **16 sample points lie
inside that window** — a passing value is representable.

**CAN FAIL.** A value of 0.30 or 0.55 R is equally representable on the same
line. **And this is not a thought experiment: the record documents the detector
actually returning 0.70** — the far end of its range — at θ≈60° at every
resolution (`F4_hypersonic_blunt_body.md` §3). **The instrument has been observed
producing an out-of-band value on this solver's real output.**

**The censoring that IS present, and the refusal that answers it.**
`np.argmax` returns an index in [0, 399], so the reported standoff is
**structurally confined to [0, 0.7]** whatever the flow does — a value at either
endpoint is the instrument's **range limit**, not a measurement. `standoff()`
therefore **refuses** any snapshot whose located index is 0 or 399. The
`--selftest` proves the reader really does return index 399 when a plant is
placed there, so the guard is guarding a reachable state rather than an
imaginary one.

### 6.2 G-F4-1 and G-F4-3, the Roache triples

The graded outcome is `roache_triple`'s `state` ∈ {`CONVERGING`, `DIVERGENT`,
`STAGNANT`, `OSCILLATORY`, `EXACT`, `NO_ORDER`}. **CAN take the converging
value** — `--selftest` grades the synthetic monotone triple (1.10, 1.04, 1.01)
`CONVERGING` at observed order 1.000. **CAN take a failing value** —
`--selftest` grades the non-monotone triple (1.00, 1.10, 1.02) `OSCILLATORY` →
`NOT A RESULT`, **with `GCI_pct` returned as `None`**, so no GCI can be quoted
off a non-monotone triple even by accident. Both branches are exercised in the
frozen instrument, not argued for in prose.

### 6.3 The quantity that is NOT registered because it could not discriminate

**Considered and rejected:** "number of cells whose ρ or p is non-physical".
`rhoCentralFoam` writes ρ unbounded, so this quantity *could* be non-zero — but
it is the SIGFPE line's question, it belongs to a different pre-registration and
a different binary, and registering it here would duplicate a gate whose event
ordinal is currently on Sanaa's desk. **It is not registered.**

---

## 7. The completion rule (standing rule 4), and its ONE declared adaptation

Per case, all nine, every clause refusing:

1. **`rc = 0`**, **read from `RC.txt`** and never inferred. `set -e` does not
   gate at tool top level nor inside `( set -e; … )`; the launcher must write
   the return code to a file, `sync`, and the grader reads it back.
2. An **`End`** line in `log.rhoCentralFoam`.
3. The **`Time =` block count equals the `ExecutionTime` line count** (a
   truncated or interleaved log is refused).
4. **The last logged `Time =` equals the latest written time directory**, to
   1e-6.
5. **THE ONE DECLARED ADAPTATION — THE REACH TEST.** Rule 4's clause is *last
   time == `endTime`*. This case family runs `adjustTimeStep yes` with
   `maxCo 0.3` and `maxDeltaT 1e-3` (`system/controlDict`), so the solver sizes
   its final step from the Courant condition and stops on the first step that
   would pass `endTime` — **its last written time therefore lands on EITHER SIDE
   of `endTime` by O(1e-4)**. Measured on the nine 2026-07-28 logs: **four land
   BELOW 6.0** (M6/coarse `5.9998543386`, M7/fine `5.9999993531`, M8/coarse
   `5.99979092006`, M8/fine `5.999927519`) and five land above.

   **The clause registered is `t_last + Δt_final > endTime`** — the solver could
   not have taken another step without passing `endTime`. `Δt_final` is read
   from **the run's own log** (the difference of its last two `Time =` lines);
   it is a property of `maxCo`, the mesh and the local wave speed, and **it
   never looks at whether the run passed**, which is what makes it a derivation
   and not a threshold fitted to the answer.

   **A two-sided band `|t_last − endTime| ≤ ε` is REFUSED as the expression of
   this clause**, and is named here so it cannot be reintroduced: choosing ε
   after seeing which runs it admits is precisely the fit rule 2 exists to
   prevent, and it would be no better for coming from a supervisor.

   **Rule 4 loses no refusing power.** A run that died at the previous write
   sits at `5.25`, four orders of magnitude clear of a Δt of order 1e-4:
   `5.25 + max Δt = 5.251 ≤ 6.0`, still refused. And the clause is
   **self-scaling** — it registers no constant that a later mesh or a different
   `maxCo` could silently invalidate.

   **`t_last ≤ endTime·1.001` is retained unchanged as the runaway guard.** The
   two together are complete: the reach test refuses a run that stopped short,
   the runaway guard refuses one that ran on.

   **PROVENANCE, RECORDED RATHER THAN QUIETLY FIXED.** This clause was first
   drafted as `t_last ≥ endTime`, which **would have refused four of the nine
   runs this conversion exists to re-derive** — 4 of 9, scattered, with no
   pattern in Mach number and none in refinement, reported under rule 4 as
   `NOT A RESULT` and reading to any reader as a physical finding when there is
   none. It was caught by the cfd supervisor's check-1 diff read **before a
   single core-minute was spent**, recorded at
   `verification/campaign/CFD_CHECK1_FINDING_2026-08-25_GRADE_F4.md`
   (`780e49d8`), and repaired pre-compute at `ae296f69`. *(Declared under the
   same discipline as `T1b_L4_AMENDMENT.md` §7, where rule 4's clause list
   originates.)*
6. **Fields present at the latest time: `T U p rho`** — the four this solver
   writes. (The seven-field list in rule 4 is the *thermal* family's; this is
   the compressible inviscid family and the field set is named explicitly here
   rather than inherited.)
7. **THE AGE GUARD.** Every one of those four fields must be **NEWER than the
   case's own `0/T`**. `0/T` is touched last at launch and so dates the run
   allowed to produce the answer.
8. **Per-case runaway guard: `ExecutionTime ≤ 1200 wall s`** (§9).

**The launch-side guard (rule 4's last clause).** `check_no_preexisting()` in the
frozen grader **refuses a case directory in which `0/` or any time directory
already exists**. The launcher must call it before building any case.

**And it has a live example.** `verification/runs/F4_runs/conversion_2026-08-24/`
**exists on disk, is EMPTY, and is untracked at HEAD** (mtime 2026-08-24 19:14) —
a run root a prior lane created on the F3 conversion's date and never populated.
**It was inspected and NOT removed.** An unexpected directory is inspected, never
deleted, and deleting another agent's directory to clear this lane's own path
would be exactly the reverting move rule 10 forbids in the git case. **This
document therefore registers `conversion_2026-08-25/` as its run root**, so the
rule-2 absence condition is true of the path actually registered. Recorded in
full at `verification/runs/F4_runs/LANE_REPORT_F4_STATE_2026-08-25.md` §4.1.

---

## 8. Planted-zero controls (standing rule 3) — the grader refuses if the reader
   cannot see the plant

All three run **before any gate is graded**, and each **refuses (exit 2)** rather
than degrading. A zero — or any number — from a reader not shown able to see a
non-zero is not evidence.

| control | what is planted | what must happen | what it rules out |
|---|---|---|---|
| **P1** | a dominating ρ spike written into an `.xy` file at **two** interior sample indices, **137 and 300**, each read back from disk and proved to have landed to 1e-12 | `find_shock()` must locate the peak **within one sample of each plant** | a reader that ignores the file. **Two locations, not one**, so a reader that happens to peak near the first cannot pass by luck. **Mutation-tested:** `--selftest` replaces the reader with one returning a constant and requires P1 to **fail**. |
| **P2** | the same spike planted into **`r3_T_p_rho.xy`** — the θ≈36° station, a file the θ=0 gate does **not** select | the θ=0 gate value must be **bit-identical** before and after, and the file must restore | **the negative control the brief requires: the selector must be UNABLE to see a plant at a different location.** A gate that moves when a file it does not declare is perturbed is reading something it did not declare. |
| **P3** | one level's **written `blockMeshDict`** perturbed from `(100 40 1)` to `(100 41 1)` | `measure_similarity()` must **stop** calling the ladder similar | a similarity check that always says yes, which is indistinguishable from no check at all. |
| **C1** | two synthetic cases built on disk: one landing under `endTime` by **0.4·Δt**, one by **3·Δt** | `check_completion()` must **accept** the first and **refuse** the second | **a completion checker that does not discriminate a real `adjustTimeStep` landing from an early stop.** P1–P3 are all about the *readers*; **nothing exercised the completion path against a real landing time, and that is exactly how the defect in §7 survived a 21-check selftest.** C1 runs in `grade_all()` **before any case is graded**, not only in `--selftest`. **Mutation-tested:** the selftest replaces the checker with a stub that never refuses and requires C1 to **fail**. |

**Plants go through F4's own parser on F4's own on-disk format** — the raw
`setFormat raw` `.xy` file the `sample` utility actually writes — not through a
synthetic fixture standing in for it.

**A hazard this created, and the guard that answers it.** P2 mutates a case
directory and restores it. Aimed at the 2026-07-28 production tree it would
touch the mtimes of a **graded** artifact and could break that tree's own age
guard. `grade_all()` therefore **refuses any root not under a `conversion_*`
directory**, verified to exit 2 with that message. **An instrument that could
silently corrupt the artifact it measures is a hazard, not an instrument.**

---

## 9. The ladder, standing rule 5, and the pinned instrument

### 9.1 Similarity, measured from the WRITTEN dicts

`MESH_STANDARD.md` §9.2 — *"the requested value is the thing that lied."*
`measure_similarity()` reads nothing from `RES`; it parses the `hex` line out of
the `blockMeshDict` **the mesher was actually handed** in each case, and refuses
unless: cell counts are exactly 1000 / 4000 / 16000; `(nθ, nR)` are exactly
(50,20) / (100,40) / (200,80); the written radial grading is exactly 8.0; the
refinement ratios agree to 1e-9; and the **near-wall first-cell heights** refine
within 5 % of 2.

**Measured from the written dicts at HEAD, before any re-run:** r(coarse→medium)
= **2.000000** and r(medium→fine) = **2.000000** at `dim = 2` (h ∝ N^(−1/2)),
gap **0**. First-cell heights `1.021550186e-02 / 5.154018643e-03 /
2.588258312e-03`, ratios **1.982046** and **1.991308** — within 0.9 % of 2.
**This is a genuinely equal-ratio, geometrically similar ladder**, which is
uncommon in this lab and is what makes rule 5 gradable here at all.

**Independently corroborated, and not by this lane.**
`verification/campaign/LADDER_RECIPE_CONSISTENCY_SWEEP_2026-08-10.md` classifies
the F4 blunt-body ladder as **single-recipe (CLEAN)**: one knob, `RES` = 50×20 /
100×40 / 200×80, with `RADIAL_GRADING` held constant. **Its increments really are
discretisation increments, not a recipe fork** — so a non-monotone triple here is
a property of the detector or the physics and cannot be dismissed as two
different experiments compared across a change of method
(`VERIFICATION_CHARTER.md` §3.2). **The conversion has a real ladder to work
with.**

**Recorded before any band was written:** `RADIAL_GRADING = 8.0` is held constant
while `nR` doubles, which fixes the **total** wall-to-farfield expansion and not
the first-cell height. The h₁ ratios above are the **measurement** that the
near-wall spacing nevertheless halves; they are not an assumption, and the 5 %
tolerance is what refuses the ladder if a future variant breaks it.

### 9.2 The instrument, pinned

**`scripts/roache_triple.py`**, HEAD blob
**`8dee0d31e94d3f59d28658f88a4cd6df80ae8e39`**, sha256
**`452f475181c9897000ea530b39a84bd3e7e9927e0a3fd39fe8b1105f538ac051`**, disk
copy `cmp`-identical to that blob. Settings, all fixed here: **`dim = 2`**,
**`fs = 1.25`**, **`form = "equal"`**.

**`form="equal"` and never `"auto"`.** `"equal"` **REFUSES** when
`|r21 − r32| > 1e-9`; `"auto"` silently falls through to the Celik unequal
formula. **A silent fallback is how a mis-built ladder gets a plausible order.**
`--selftest` asserts `FORM == "equal"` and asserts `FS == roache_triple.FS`.

### 9.3 The instrument this document is FORBIDDEN to use

**No GCI, observed order or Richardson value in this conversion comes from
`sdk/workflows/tmr_verification.py`.** Three implementations in this repository
quote a **negative GCI (−10.714 %) on a divergent triple** and that file is one
of them. Its geometry helpers may be used; its GCI may not. `grade_f4.py` does
not import it.

### 9.4 Rule 5's clause order, as registered

1. Any level failing §7 completion or the §6.1 endpoint guard → **`NOT A
   RESULT`** (and the gate is refused, not graded).
2. Triple `DIVERGENT`, `STAGNANT`, `OSCILLATORY`, `EXACT` or `NO_ORDER`, or not
   monotone → **`NOT A RESULT`**, with the values, the state and the order
   printed beside it and **`GCI_pct` returned as `None`**.
3. `CONVERGING` and monotone → GCI at `fs = 1.25` printed; G-F4-2 then grades
   `PASS` inside its band else `GATE FAIL`.

---

## 10. Cost (standing rule 12), and the cap

### 10.1 The basis, MEASURED from artifacts on disk

`ExecutionTime` read from the nine 2026-07-28 `log.rhoCentralFoam` files, all
serial (`np = 1`), so core-minutes = wall s / 60:

| M | coarse | medium | fine | row total (wall s) |
|---|---|---|---|---|
| 6.0 | 5.86 | 30.08 | 216.81 | 252.75 |
| 7.0 | 6.18 | 34.56 | 249.05 | 289.79 |
| 8.0 | 6.96 | 38.80 | 278.90 | 324.66 |

**Total 867.20 wall s = 14.4533 core-minutes**, solver only. *(The 2026-07-28
record states 14.66 core-min; the 0.2067 difference is `blockMesh`, `checkMesh`
and the two sampling passes, which that figure includes and this one does not.
The discrepancy is stated rather than reconciled away.)* **Basis: measured from
logs.**

### 10.2 The prediction, arithmetic shown

- Solver + mesh + sampling basis: **14.66 core-min**.
- Contention factor **1.15**. Justification: `docs/COST_CALIBRATION.md` row
  **C-33** measured cfd's own F4 SIGFPE solvers at **1.058×** their basis; this
  box is busier now (three heat-transfer `buoyantBoussinesqSimpleFoam`, dafoam
  IPOPT tasks and two other cfd lanes), and these are memory-bandwidth-bound
  serial runs, so 1.15 is taken rather than 1.058. **Estimate.**
- 14.66 × 1.15 = **16.86 core-min**.
- Grading: pure Python, no solver, **≤ 0.5 core-min**. **Estimate.**
- **PREDICTED TOTAL: 17.36 core-minutes.**

### 10.3 The HARD CAP — a runaway guard, not a budget gate

**HARD CAP: 24.0 core-minutes** for the nine solver runs combined, plus a
**per-case guard of 1200 wall s**.

**Justification, because a cap 5× a prediction is a rubber stamp.** 24.0 is
**1.38× the prediction** and **1.66× the measured basis**. The known F4 runaway
mode is documented in `F4_hypersonic_blunt_body.md` §2: an exploratory run
integrated to t≈9.3 (≈1.55× `endTime`) before a floating-point exception, with
Courant numbers bounded throughout — **so a runaway here does not announce itself
as a CFL blow-up and a loose cap would not catch it.** At 1.38×, a single case
running ~3.4× its basis trips the batch cap. The per-case 1200 s guard is 4.3×
the slowest measured case (278.90 s) and well under
`COMPUTE_BUDGET_CHARTER.md`'s 3600 s stall definition — tight enough to catch one
hung case without killing a merely-slow one.

**Dollars: 24.0 core-min = 0.4 core-h × $0.0513/core-h = $0.02052.**
**DERIVED, NOT MEASURED** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so no dollar figure from it is a measurement.

**If the cap is crossed the run STOPS and it is REPORTED to the cfd supervisor,
who decides.** This lane does not extend a cap, and does not stop work to save
money — cost is not what is being guarded here.

### 10.4 THE LAUNDERING TRAP, NAMED

***"Cost constraints are lifted" reads as "the cap can be raised", and it
cannot.*** Rule 2 closes caps after first compute on **evidentiary** grounds: a
cap raised after seeing which rows it refused is a cap **re-posed to fit an
answer**. Sanaa lifted a *spending* constraint; she did not retire rule 2, and
retiring a threshold is reserved to her alone. **The lawful route is always a
successor registration with its own cap.** This applies to §10.3's cap the
moment the first solver starts.

### 10.5 The calibration row owed at completion

Rule 12's estimate-versus-actual comparison is **owed at this conversion's
completion** and lands as a row in `docs/COST_CALIBRATION.md`: actual
core-minutes from the logs, the ratio actual/predicted against **17.36**, the gap
attributed (contention / waste / misprediction), **waste named separately and
never absorbed into the ratio**, and dollars **derived, not measured**. The row
id is derived **tolerantly and by hand from the HEAD blob inside the committing
shell invocation** — matching both plain and bold id forms, because
`append_record.py` hands out colliding ids and its regex missed a bold format
(the real maximum was C-83, not C-76).

---

## 11. The run matrix, fixed now

Nine cases, run root
**`verification/runs/F4_runs/conversion_2026-08-25/runs/cyl/M<M>/<level>/`**.

| | coarse 50×20 | medium 100×40 | fine 200×80 |
|---|---|---|---|
| **M = 6.0** | ✓ | ✓ | ✓ |
| **M = 7.0** | ✓ | ✓ | ✓ |
| **M = 8.0** | ✓ | ✓ | ✓ |

Solver **vanilla `rhoCentralFoam`**, inviscid (μ=0), γ=1.4, `endTime = 6.0`,
`adjustTimeStep yes`, `maxCo 0.3`, 8 writes, **last 3 snapshots averaged**.
Case generation by `make_cylinder_case.py` (HEAD blob
`466a4f55800ce6f039d276e6c170c4e7d6b49276`), unchanged.

**Execution constraints:** all runs `np = 1`; **at most 6 concurrent cases**, so
the two other live cfd lanes retain room; **no process this lane did not start is
touched, reniced or killed** — three heat-transfer solvers and dafoam IPOPT tasks
are live.

**Log capture is an assertion, not a hope.** `.gitignore` lines 260–266 hide
`verification/runs/*_runs/**/log.*` and `F4_runs` **matches**.
`git update-index --add` bypasses ignore rules so the logs **can** land; the
standing requirement is the **assertion that they did** — every log path
confirmed in `git diff-tree --stat` before `commit-tree`, and
`git cat-file -e HEAD:<logpath>` for every one after, **failing loudly on any
miss.** The primary evidence is otherwise silently absent from the record.

---

## 12. The grading path, fixed at this commit

**`verification/runs/F4_runs/conversion_2026-08-25/grade_f4.py`**, repaired and
committed at **`ae296f690d4b5903fb2cb73814355e87fa05c350`**, HEAD blob
**`f51961435729558dc768d89e429c1818e8ae1da6`**, sha256
**`55636d92a8def8729ad3d5bc811adaa06067b268b76d3d0b0df3ee8283bbe410`**.
**`--selftest` passes 27 checks including four mutations that must fail.**
Before grading, the file that runs is hashed against this blob; a mismatch is a
**refusal**, not a note.

**The superseded blob is named so it cannot be pinned by mistake:**
`48d4a479d6fb8292d57cfaeb3763f36d4fa22cfc` (commit `ad6f2f6b`) carried the §7
completion defect and **must never be pinned.**

**Three of the selftest's checks hard-code the nine real 2026-07-28 landing
times and their Δt values**, so the §7 defect cannot return silently: that
exactly four land below `endTime`, that the reach test accepts all nine
(minimum margin **1.466e-04**), and that a run stopping at the previous write is
still refused. The repair was additionally verified **end to end on the nine
real logs** — 9/9 accepted, margins **+1.4655e-04 to +1.1294e-03** — using
read-only replicas staged outside the repository and deleted afterwards; **the
2026-07-28 production tree was never touched.**

### 12.1 What each outcome will mean — and this lane's prediction, recorded BEFORE the run

**The prediction is registered so that it cannot be claimed afterwards.** On the
2026-07-28 values, **all three standoff triples are non-monotone** — M=6
(0.4380, 0.4368, 0.4485) falls then rises; M=7 (0.4281, 0.4386, 0.4345) rises
then falls; M=8 (0.4427, 0.4082, 0.4181) falls then rises. **This lane predicts
G-F4-1 returns `OSCILLATORY` → `NOT A RESULT` at all three Mach numbers, and
that G-F4-2 is therefore `NOT A RESULT` at all three regardless of the band.**
For G-F4-3, M=6 (4.48, 4.21, 3.91) and M=8 (4.08, 3.89, 3.87) are monotone and
may converge; M=7 (4.69, 3.85, 3.91) is not and is predicted `NOT A RESULT`.

| outcome | what it means |
|---|---|
| G-F4-1 `NOT A RESULT`, G-F4-2 `NOT A RESULT` (**predicted**) | The 2026-07-28 `PASS` on Gate 1 **does not survive conversion.** The standoff detector's resolution-dependent bias, already diagnosed in §4 of that record, is confirmed to be large enough that the ladder does not converge — and rule 5 forbids a value verdict on it. This is a **successful conversion**, not a failure of it: the defensible label replaces an undefendable one. |
| G-F4-1 `CONVERGING`, G-F4-2 `PASS` | The re-run's triple converges where the original's did not, and the fine-level deviation is within the instrument's resolution. Gate 1 converts to a **defensible `PASS`**. |
| G-F4-1 `CONVERGING`, G-F4-2 `GATE FAIL` | The ladder converges and the converged answer is outside one local cell of Billig. A real disagreement, resolved above the instrument. |
| G-F4-3 `CONVERGING` | The Cp functional converges under refinement at a measured observed order. **This is strictly more than the 2026-07-28 Gate 2 `PASS` said**, because that PASS had no threshold at all. |
| G-F4-3 `NOT A RESULT` | The Cp functional does not converge monotonically; no order and no GCI are quoted. |
| Any case fails §7 or §6.1 | **Refusal**, and the gate is `NOT A RESULT`. **A crash or a runaway stop is `NOT A RESULT`, NEVER `GATE FAIL`** — the gate can only turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse. A crash is a **finding** about the case, the method or the toolchain until triage says otherwise, and **triage is the supervisor's and is not delegated.** |

---

## 13. Cross-checks this document does NOT make, stated so nobody assumes them

- **No claim is made about the SWBLI limb** — see §14.
- **No mesh-draw scatter is measured**, and none exists to measure: the mesh is a
  deterministic structured polar O-grid built from `RES` with `RADIAL_GRADING`
  fixed, so the same parameters give a byte-identical mesh every time. Draw
  scatter is a property of `snappyHexMesh`'s nondeterministic castellation and
  this ladder contains no snappy. *(This point was settled on this exact record
  on 2026-08-10, and the ~7.5 core-min approved to measure it was correctly
  **not spent.**)*
- **No P-tier claim.** F4's references are Billig (1967), a **correlation**, and
  modified Newtonian, a **theory**. `F_FAMILY_TRIPLE_CROWN_SURVEY.md` line 152
  records that F4 **cannot reach the P tier via its own references**. This
  conversion makes the V/G limbs defensible; it does not buy a P.

---

## 14. The SWBLI limb is `BLOCKED`, and this lane does not rule it

**Gate 3 of the 2026-07-28 record (SWBLI, θ = 32.5° / 35°, the
`swbli_cylflare/` tree) is NOT converted by this document and is registered
`BLOCKED`.**

Two independent reasons, neither of which is this lane's to clear:

1. **`F4_SIGFPE_STEP01_RESULTS.md` §6 row F4-W1** holds θ=32.5°/35° until the
   remaining mechanism (§8.6(3) momentum/energy split, or the wedge-face
   identity) is resolved.
2. **The step-0/1 headline that would inform it is CONTINGENT on the
   event-1/event-2 ruling, which is cross-family and sits on Sanaa's desk,
   `PENDING`** (`F4_SIGFPE_STEP01_RESULTS.md` §C1.4; `docs/LAB_STATE.md` 4333,
   4476, 4540, 4609). Under verification's reading §9.1 row 4 applies and the
   elimination of mechanism #7 becomes **`NOT A RESULT`**. **No agent at any
   level makes that ruling — not this lane and not the cfd supervisor.**

**Limb A — Gates 1 and 2, this document — is NOT blocked by that ruling**, and
the separation is stated so it can be checked rather than trusted: different
geometry (2-D cylinder vs cylinder–flare), different solver binary (vanilla
`rhoCentralFoam` vs `rhoCentralFoamBounded*`), different quantity, different
pre-registration. **No clause of G-F4-1, G-F4-2 or G-F4-3 reads any BOUND-family
diagnostic**, and the SIGFPE pre-registration's §0 issues no verdict that any
gate here consumes. **One honest caveat:** if a limb-A case were itself to
SIGFPE, the mechanism question would bear on its *triage* — but that is a
contingency of a crash that has never occurred on this case tree (all nine
2026-07-28 runs completed cleanly), not a dependency of either gate.

---

## 15. Standing rules this document is bound by

Rule 1 (vocabulary — and `HOLD` is not in it). Rule 2 (this freeze; gates closed
after first compute; addenda cannot alter a gate, threshold, cap or label;
originals struck, never rewritten). Rule 3 (§8). Rule 4 (§7, with its one
declared adaptation). Rule 5 (§9.4). Rule 6 (frozen files are never edited; a
departure is a dated amendment at the foot with `lines whose number changed above
this section: 0`). Rule 7 (**nothing here is sent, filed, uploaded, registered,
posted or commented**). Rule 9 (**no agent message is Sanaa's consent** — not the
withdrawn paraphrase of §0, not a supervisor's brief). Rule 10 (private-index
protocol; the empty `conversion_2026-08-24/` was **inspected, never removed**).
Rule 12 (§10). Rule 13 (**no repository document here cites a scratch path**).
Rule 16 (this document carries values and verdicts, never transcripts).
