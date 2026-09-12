# SUBOFF **A1c** — THE α-SWEEP, AND THE REFERENCES SANAA NAMED ARE NOW **ON THE BOX** — PRE-REGISTRATION

**STATUS: DRAFT. NOT FROZEN. NOT LAUNCHED.** §9 is blank and is the cfd-supervisor's
personally, undelegated (check 4). No solver has been started by this document and the
queue entries it implies do not exist yet.

**Author:** cfd `lab-lane`, 2026-09-12.
**Predecessor:** `SUBOFF_A1b_PREREGISTRATION.md` (frozen; §11 freeze block completed
2026-09-12T19:17:53Z). A1c does not move, narrow or revive any A1b gate.

---

## 0. 🔴 WHY THIS DOCUMENT EXISTS: A1b §10.6's PREMISE HAS BEEN OVERTURNED BY RETRIEVAL

A1b §10.6 refused to write Sanaa's validation registration, and its stated reason was
**availability**:

> "the validation registration Sanaa specified CANNOT BE WRITTEN AS SPECIFIED. A band per
> derivative referenced to a paper the lab does not hold would be fabrication"

That reason was correct **on the evidence then available**, and this lane re-verified the
underlying facts before acting: the off-repository reference pack directory
`/home/ubuntu/paper-incoming/CERTONOMOUS_REFERENCE_PACKS_BOTH/CERTONOMOUS_REFERENCE_PACKS/02_NAVIER_CLASS_PARITY_CASES/PDFs/CASE_1_DARPA_SUBOFF/`
does contain **exactly one file, `README.txt`**, a twelve-entry bibliography; all twelve
companion `Links/` entries are `.url` stubs and **ten of the twelve point at a Google
Scholar *search query*, not at a document**.

**That premise no longer holds. The papers have been retrieved.** Four sources are now on
the box, each title-page-verified under rule 15 by rendering page 1 to PNG and **reading
it**, never by filename, file type or hash:

| Filed path (all under `/home/ubuntu/Certonomous/docs/papers/benchmark_test_cases/`) | Read from the rendered title page |
|---|---|
| `roddy_1990_dtrc_shd1298_08_darpa_suboff_captive_model.pdf` | David Taylor Research Center, Bethesda MD 20084-5000 · **DTRC/SHD-1298-08** · **September 1990** · Ship Hydromechanics Department, Departmental Report · "INVESTIGATION OF THE STABILITY AND CONTROL CHARACTERISTICS OF SEVERAL CONFIGURATIONS OF THE DARPA SUBOFF MODEL (DTRC MODEL 5470) FROM CAPTIVE-MODEL EXPERIMENTS" · by **Robert F. Roddy** · AD-A227 715 · Approved for public release, distribution unlimited · 116 pp. |
| `huang_1989_dtrc_shd1298_02_darpa_suboff_experiments.pdf` | David Taylor Research Center, Bethesda MD 20084-5000 · **DTRC/SHD-1298-02** · **December 1989** · Ship Hydromechanics Department, Departmental Report · "EXPERIMENTS OF THE DARPA SUBOFF PROGRAM" · by **Thomas T. Huang, Han-Lieh Liu, Nancy C. Groves** · AD-A218 797 · Approved for public release · 48 pp. |
| `liu_1998_crdknswc_hd1298_11_darpa_suboff_data_summary.pdf` | Naval Surface Warfare Center, Carderock Division (NSWCCD), 9500 MacArthur Blvd, West Bethesda MD 20817-5700 · **CRDKNSWC/HD-1298-11** · **June 1998** · Hydromechanics Directorate · "Summary of DARPA Suboff Experimental Program Data" · by **Han-Lieh Liu, Thomas T. Huang** · Approved public release · 28 pp. |
| `gertler_1967_nsrdc_2510_submarine_equations_of_motion.pdf` | "STANDARD EQUATIONS OF MOTION FOR SUBMARINE SIMULATION" · by **Morton Gertler and Grant R. Hagen** · **JUNE 1967** · AD 653 861 · SR 009 01 01, Task 0102 · 42 pp. **Disclosed defect in this title-page read: the cover carries NO institution and NO report number.** "NSRDC" and "Hydromechanics Laboratory" were read from the report body, not the title page; the number **2510 was NOT read from the document at all** and survives in our filename only from the third-party bibliography. Treat the filename's `2510` as unverified. |

**Retrieval route, recorded because it will be needed again:** `apps.dtic.mil` served an
**"Under Maintenance" HTML page for every request** on 2026-09-12 (1,408 bytes, not a PDF —
caught only because the fetch asserted the `%PDF` magic rather than trusting a non-zero
file size). All four PDFs came instead from the **Internet Archive DTIC mirror**,
`https://archive.org/download/DTIC_<ADnumber>/DTIC_<ADnumber>.pdf`.

**A rule-15 catch worth recording.** The local bibliography calls the 1998 report
**"NSWCCD/HD-1298-11"**. Its title page reads **"CRDKNSWC/HD-1298-11"**, and the search
engine that found it asserted "July 1998" where the title page reads **June 1998**. Small,
and exactly the failure mode rule 15 names: *a manifest can be internally consistent and
externally false.* Every report identifier in this document is the one on the page.

---

## 1. 🔴 THE FINDING THAT DECIDES THIS REGISTRATION: **RODDY 1990 DOES NOT CONTAIN A HULL+SAIL VERTICAL-PLANE DERIVATIVE**

Sanaa's instruction is: *"reference = Roddy 1990 captive-model forces and moments (band per
derivative written first) … quantities Z, M … derivatives by linear fit over |α| ≤ 8;
neutral point from Z_w and M_w"*.

**We now hold Roddy 1990. It does not contain that measurement for our geometry.**

Roddy **Table 4** (report p. 19; PDF p. 27 of the filed file) — read from the page rendered
at 150 dpi, with every figure confirmed against the OCR text layer, and the OCR confirmed
against the page:

**Vertical Plane — ONE column only, `Config 1, Fully Appended`:**

| | `Z_w'` | `M_w'` | `Z_q'` | `M_q'` | `Z_ẇ'` | `M_ẇ'` | `Z_q̇'` | `M_q̇'` | `G` | `Z_δs'` | `M_δs'` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Config 1 | −0.013910 | 0.010324 | −0.007545 | −0.003702 | −0.014529 | −0.000561 | −0.000633 | −0.000860 | −1.162874 | −0.005603 | −0.002409 |

**Horizontal Plane — five columns:**

| | Config 3 Bare Hull | **Config 4 B.H. + Sail** | Config 5 B.H. + 4 Planes | Config 6 B.H. + Ring Wing 1 | Config 2 Fully Appended |
|---|---|---|---|---|---|
| `Y_v'` | −0.005948 | **−0.023008** | −0.010494 | −0.005943 | −0.027834 |
| `N_v'` | −0.012795 | **−0.015534** | −0.011254 | −0.012939 | −0.013648 |
| `Y_r'` | 0.001811 | −0.000023 | 0.006324 | 0.003811 | 0.005251 |
| `N_r'` | −0.001597 | −0.002378 | −0.003064 | −0.002325 | −0.004444 |
| `G` | −20.38506 | **−4.081818** | −3.152048 | −12.43748 | −0.443297 |

Roddy **Table 3** (report pp. 16–17) gives the reason, in the experiment schedule itself:
**Configuration 1 is the only vertical-plane configuration in the entire programme**, and it
is *fully appended with ring wing no. 1*. Configurations 2–6 are **all horizontal-plane**
(drift angle β → `Y`, `N`). Configuration 4 — `HORIZONTAL PLANE, HULL AND SAIL ONLY`,
static stability at ±18° drift, 6.5 knots — is the only hull+sail static sweep Roddy ran,
**and it is in the wrong plane.**

**Our geometry is hull + sail, and it has NO FINS.** Verified directly, not inherited:
`constant/polyMesh/boundary` in every SUBOFF_A1 level (`L0c`, `L1`, `L1_SHIFT`, `SOLVE_L2`)
lists exactly six patches — `inlet outlet farfield symm hull sail` — and nothing else.

> ### CONSEQUENCE, STATED AS A REFUSAL
>
> **A band on `Z_w'` or `M_w'` for a hull+sail body in pitch CANNOT BE CITED TO RODDY 1990,
> because Roddy 1990 never measured it.** Citing Roddy's Config 1 would band our finless
> hull against a body carrying four sternplanes and a ring wing — and Roddy's own conclusion
> is that the vertical-plane instability is *"due to the relatively small planform area and
> outreach of **the sternplanes**"* (p. 6). The sternplanes are the dominant term in the very
> derivative being banded, and our mesh does not have them.
>
> **A1b §10.6's refusal therefore stands — but its GROUND has changed, and the new ground is
> stronger.** It is no longer *"we do not hold the paper"*. It is **"we hold the paper, we
> read it, and the measurement is not in it."** That is an evidence-based refusal, and it
> cannot be overturned by finding a better download.

---

## 2. WHAT RODDY **DOES** GIVE US — THREE REAL, CITED NUMBERS

### 2.1 A measured uncertainty — this is the band width Sanaa asked for

Roddy **Appendix C, report p. 105** (PDF p. 113), read from the rendered page:

> "The total uncertainties in the stability derivatives `Z_w'` and `M_w'` are calculated to
> be **about 4 percent** for both derivatives."

and, assigned from the DTRC submarine stability database across repeated experiments:

> "(1) static derivatives `Z_w'`, `M_w'`, `Y_v'`, and `N_v'` **4 to 5 percent**, (2) rotary
> derivatives … about 10 percent, (3) control derivatives 6 to 10 percent, (4) added mass
> and moment of inertia derivatives … about 7 percent."

Provenance of the 4%: the slope of normal force vs angle of attack **was read independently
by 10 engineers**; sample mean `Z_w' = −0.006489`, sample standard deviation `0.000262`,
`t₁ = 2.262`, precision `P/m = 0.0289`, combined with bias into ≈4%.
**`U(Z_w') = U(M_w') = 4%` is a measured, sourced, quotable band width.** It is used below.

### 2.2 Bare-hull derivatives that DO map into our plane

For an **axisymmetric bare hull** the vertical and horizontal planes are geometrically
equivalent, so Roddy's Config 3 maps in: `|Z_w'|(bare hull) = |Y_v'| = 0.005948` and
`|M_w'|(bare hull) = |N_v'| = 0.012795`. **This is a legitimate use of Roddy and the only
one available in our plane.** It is a *bare-hull* reference; our body additionally carries
a sail.

### 2.3 The sail's measured contribution — in drift, which bounds it in pitch

From the same table, the sail's measured increment in the horizontal plane is
`ΔY_v' = −0.023008 − (−0.005948) = −0.017060` and
`ΔN_v' = −0.015534 − (−0.012795) = −0.002739`.
In **drift** the sail is broadside — full planform normal to the flow. In **pitch** it is
edge-on. The pitch increment is therefore **strictly smaller in magnitude and of the same
sign**, and that is what makes a bracket constructible below.

### 2.4 An internal consistency check that supports the sign convention assumed here

With `x_np/L = −M_w'/Z_w'`: bare hull → `−0.012795 / −0.005948 = 2.151`; fully appended →
`−0.010324 / −0.013910 = 0.742`. The neutral point moves **aft** as appendages are added,
tracking the measured stability margins `G` (bare hull −20.385 → fully appended −0.443 in
plane, −1.163 in the vertical). **The ordering is self-consistent.** It is presented as a
supporting check, **not as a proof of convention** — see §7.1 for the gap that remains.

---

## 3. 🔴 THE BAND, WRITTEN FIRST, AND TIERED HONESTLY

Sanaa's instruction is that the band is *written first*. It is written here, before any
sweep is launched, and each row carries the tier it is actually entitled to.

### 3.1 THE ANCHOR — `Cp` at α = 0 — **CANNOT BE REGISTERED WITH VALUES, AND HERE IS WHY**

Sanaa specified *"Huang 1992 surface pressure at α = 0 as the anchor"*. We now hold two
Huang-authored SUBOFF reports. **Neither carries the `Cp` values.**

- **`huang_1989_…_shd1298_02` is a TEST PLAN, not a data report.** It is written in the
  future tense throughout — *"The measurement plane **will be** at x/L = 0.978"*,
  *"Resistance measurement … **will be** measured"*. It defines the cryptic test notation
  (`AFF-1`…`AFF-8`, `PP` for static-pressure-coefficient profiles), the tap layout and the
  test-condition tables. It contains **no measured `Cp(x/L)`**.
- **`liu_1998_…_hd1298_11` is a DATA CATALOGUE, not a data listing.** Its tables are
  *Data Directory Organization*, *Test Numbers*, *Data File Structures*, *File Directory
  Structure*. Table 4 gives the **tap inventory** — 21 upper-hull, 7 port, 7 lower, 7
  starboard, **30 fairwater (sail) surface**, 76 fairwater/hull intersection, 33 upper
  rudder, 41 stern-appendage/hull, **222 total** — i.e. *where* the taps are, not what they
  read. The numeric `Cp` lives in the accompanying data files, **which are not on this box
  and are not inside either PDF.**

> **`Cp(α = 0)` IS REGISTERED AS `PENDING: <data files not held>`.** It is a display/queue
> state under rule 1 — "not yet run" — and **not** a softened failure. The sweep may still
> be run; the anchor is simply not yet gradeable, and **no `Cp` number may be quoted against
> a band in any A1c result until the data files are in hand.**

**One measured fact from the test plan that constrains the anchor permanently** (SHD-1298-02
p. 6): *"The maximum body angle of attack or drift in the DTRC AFF **will be limited to two
degrees**."* The wind-tunnel surface-pressure programme therefore covers **α = 0 and α = 2°
only**. Sanaa's choice of α = 0 as the anchor is the correct and the only available one —
**and it constrains exactly one of the seven sweep points. It cannot validate the sweep.**

### 3.2 THE DERIVATIVE BANDS — ONE ROW PER DERIVATIVE, EACH WITH ITS TIER

Definitions fixed here, before any solve:
`Z_w' ≡ ∂Z'/∂w'` and `M_w' ≡ ∂M'/∂w'` by **least-squares linear fit over the five points
|α| ≤ 8** (α = −8, −4, 0, +4, +8), nondimensionalised on `L`, with α = ±12 carried in the
sweep but **excluded from the fit** and reported separately as the linearity check.
`x_np/L ≡ −M_w'/Z_w'`.

| # | Quantity | Registered band | Tier | Source of the band |
|---|---|---|---|---|
| **B1** | `Z_w'` — **BARE HULL**, if a bare-hull arm is run | `[−0.006186, −0.005710]` (= −0.005948 ± 4%) | **MEASURED** | Roddy Table 4 Config 3 `Y_v'`, via axisymmetric plane-equivalence; width from Roddy App. C |
| **B2** | `\|M_w'\|` — **BARE HULL**, if a bare-hull arm is run | `[0.012283, 0.013307]` (= 0.012795 ± 4%) | **MEASURED**, sign UNVERIFIED (§7.1) | Roddy Table 4 Config 3 `N_v'`; width from Roddy App. C |
| **B3** | `Z_w'` — **HULL + SAIL, our geometry** | `[−0.008847, −0.005710]` | 🔴 **LAB-CONSTRUCTED BRACKET — NOT A RODDY BAND** | §3.3 |
| **B4** | `\|M_w'\|` — **HULL + SAIL, our geometry** | `[0.012283, 0.013734]` | 🔴 **LAB-CONSTRUCTED BRACKET — NOT A RODDY BAND** | §3.3 |
| **B5** | `x_np/L` — **HULL + SAIL** | `[1.43, 2.34]` | 🔴 **LAB-CONSTRUCTED BRACKET** | propagated from B3/B4 |
| **B6** | `Cp(x/L)` at α = 0 | — | **`PENDING`** | §3.1 — data files not held |
| **B7** | Sweep antisymmetry: `Z(+α) = −Z(−α)`, `M(+α) = −M(−α)` to within 2% of the α = 8 value | `≤ 2%` | **CODE-VERIFIED** (internal consistency, no experiment) | §5 |

**B3/B4/B5 are labelled `LAB-CONSTRUCTED BRACKET` in every downstream artifact, figure
caption and results row. They are NOT validation against Roddy and must never be reported
as such.** They are falsifiable predictions this lab is making from Roddy's measured
numbers, which is a real and gradeable thing — it is simply not the thing a measured band is.

### 3.3 HOW B3/B4/B5 WERE CONSTRUCTED — THE ARITHMETIC, SO IT CAN BE ATTACKED

Registered assumption, frozen here: **in pitch the sail contributes between 0% and 15% of
the increment it contributes in drift.** 0% is the rigorous lower bound (an edge-on fin
cannot *reduce* the hull's normal-force slope); 15% is a deliberately generous upper bound
for a dorsal fin at incidence in its own plane. The assumption is **the falsifiable part**
and it is stated so it can be rejected on its own merits rather than hidden inside a number.

- `Z_w'` ∈ `[−0.005948 + 0.15×(−0.017060), −0.005948]` = `[−0.008507, −0.005948]`,
  widened by Roddy's 4% → **`[−0.008847, −0.005710]`**.
- `|M_w'|` ∈ `[0.012795, 0.012795 + 0.15×0.002739]` = `[0.012795, 0.013206]`,
  widened by 4% → **`[0.012283, 0.013734]`**.
- `x_np/L` from the bracket corners: `0.012795/0.005948 = 2.151` down to
  `0.013206/0.008507 = 1.552`; with the 4% → **`[1.43, 2.34]`**.

**Sanity ordering that the result must not violate:** our hull+sail `|Z_w'|` must sit
**between** bare hull (0.005948) and fully appended (0.013910), and much nearer the former.
A result outside `[0.005710, 0.013910]` falsifies either the mesh or the post-processing
before it says anything about the sail.

---

## 4. 🔴 A GEOMETRY CORRECTION SANAA'S INSTRUCTION NEEDS: **"hull/fin split" HAS NO REFERENT**

Sanaa's run instruction asks for *"quantities Z, M, **hull/fin split**"*. **This geometry has
no fin patch.** The six patches are `inlet outlet farfield symm hull sail`. A1c therefore
registers the **`hull` / `sail` split**, which is the split that exists, and says so in the
open rather than silently renaming her request.

**Instrument consequence, and it is a real change that must land before launch:** the
current `forceCoeffs` function object covers `(hull sail)` **together**, so it cannot
produce the split at all. A1c requires a **second `forceCoeffs`** so that `hull` and `sail`
are integrated separately, with the *same* `CofR`, `lRef`, `Aref`, `magUInf` and `rhoInf` as
the combined one, and the registered check that **`hull` + `sail` sums to the combined
`forceCoeffs` to within 1e-9 relative** at every written time. Without that check the split
is two unvalidated numbers rather than a decomposition.

**What is NOT changed, and was verified rather than assumed:** a pitch sweep rotates the
freestream **within** the `z = 0` plane, so it **preserves** the `symmetryPlane` on `symm`.
The half model stays valid, and the frozen `liftDir (0 1 0)` with `CmPitch` about `z` are
already the correct quantities. **No full mesh is needed for the α sweep.**

> **And the corollary, which is a genuine constraint on any future attempt to fix §1:** the
> one Roddy configuration that matches our geometry exactly — **Config 4, hull + sail** — is
> a **drift** sweep. Running it would need a **full (non-half) mesh**, because a yaw sweep
> breaks the `z = 0` symmetry plane. That is roughly **2× the cells and 2× the cost per
> point** on every level. It is the only route to a MEASURED-tier band for a hull+sail body
> in this programme, and it is a cross-family call, not a lane's.

---

## 5. THE RUNS

Carried from A1b §3 unchanged except for incidence: `simpleFoam`, `kOmegaSST`,
`nutUSpaldingWallFunction` on `hull` and `sail`, half model, `Re_L = 1.2e7`,
`U = 2.7547576 m/s`, `endTime 3000`, `deltaT 1`, 4 ranks, no `residualControl`,
`0/T`-age-guarded, checkpointed per Sanaa's run instruction (30 min wall, last two kept).

**Sweep: α = −12, −8, −4, 0, +4, +8, +12 — seven points per level**, imposed by rotating the
inlet velocity vector in the `x–y` plane, mesh unchanged between points (the mesh is
identical for all seven; only `0/U` and the `forceCoeffs` `liftDir`/`dragDir` rotate).

**`B7` is why the sweep is symmetric rather than one-sided.** Seven points where five would
fit the derivative buys an internal falsifier: the geometry is symmetric about `y = 0` in
the hull but **not** in the sail (dorsal), so `Z(+α) ≠ −Z(−α)` is *physically expected* at
the sail and *not* expected at the hull — the `hull`-only channel from §4 must pass B7 even
where the combined channel does not. **This is the only genuinely experiment-free falsifier
in the document and it is the one that catches a broken rotation convention.**

---

## 6. COST — REGISTERED, AND **NOT A KILL**

Sanaa's instruction: *"Cost estimate registered too but doesnt stop the run"*, consistent
with her 2026-09-12 directive #17 (no run stopped by a time or budget cap).

Derived from A1b §6's per-level figures — themselves anchored on the **worse, later**
measured rate (10 s/it at 01:15Z under peer load, after a measured **2.4× intra-night swing**):

| Level | Per point | × 7 points | Derived $ |
|---|---|---|---|
| **L1** | 6,280 core-min | **43,960 core-min** | **$37.59** |
| **L2** | 17,540 core-min | **122,780 core-min** | **$104.98** |
| **Family** | — | **166,740 core-min** | **$142.57** |

`cost_basis`: **$0.0513/core-h is OWNER-STATED** (Sanaa 2026-08-21/22), **not measured** —
the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5). **These are predictions
to be scored at completion under rule 12**, against actuals in core-minutes from the logs,
with contention attributed on its own line and never absorbed into the actual/predicted
ratio, landing as a row in `docs/COST_CALIBRATION.md`.

**Two honest reductions available to the supervisor, neither taken unilaterally:** α = 0 at
both levels may already exist from A1b's `SOLVE_L1`/`SOLVE_L2` (−1 point each, if and only
if the age guard and the completion rule pass on those runs); and L2 need not run all seven
points if L1's sweep falsifies B3 outright.

---

## 7. WHAT A1c DOES NOT CLAIM, AND WHAT THIS LANE COULD NOT VERIFY

### 7.1 🔴 The `M_w'` SIGN CONVENTION IS UNVERIFIED, AND IT IS LOAD-BEARING FOR B2/B4/B5

The mapping `|M_w'|(bare hull) = |N_v'|` is safe in **magnitude** by axisymmetry. Its
**sign** depends on the axis and moment-reference conventions, which Roddy takes from
Gertler & Hagen. **This lane retrieved and title-page-verified Gertler & Hagen 1967 but did
NOT verify the sign mapping from it** — the scan's OCR of the nomenclature tables is
badly degraded and this lane did not render and read the axes/nomenclature pages. The §2.4
consistency check supports the assumed convention but does not prove it.

> **Recommendation to the cfd-supervisor, for check 4:** either render and read Gertler &
> Hagen's axes/sign-convention and nomenclature pages before freezing B2/B4/B5, **or freeze
> only `Z_w'` (B1/B3), whose sign is unambiguous, and carry `M_w'` and `x_np/L` as
> `PENDING`.** Freezing a moment band on an unverified sign is the same class of error as
> citing a band to a paper we do not hold.

### 7.2 Sources named by Sanaa or by the bibliography that were **NOT** retrieved

| Source | What was tried | Outcome |
|---|---|---|
| **Huang et al. 1992**, 19th Symp. Naval Hydrodynamics, Seoul — the paper Sanaa named | Four searches; National Academy Press proceedings; TRID; Semantic Scholar; DTIC | **NOT RETRIEVED.** Conference proceedings volume, not open. **Partially superseded**: its lead author's DTRC programme report (SHD-1298-02) and the consolidated database report (HD-1298-11) are both now held — but neither carries the `Cp` values (§3.1). |
| **The SUBOFF measured data files** (`AFF-*` surface pressure, wake, BL profiles) | Searched for a digitised/open mirror | **NOT RETRIEVED.** Referenced by directory and test number in HD-1298-11; the files themselves are not on this box. **This is the single blocker on the α = 0 anchor.** |
| **Crook 1990**, DTRC/SHD-1298-07 (resistance) | Not attempted — not needed for the α sweep | Not retrieved. Note: HD-1298-11 **Table 14** does carry DTMB tow-tank resistance (bare hull 74.85 lb / 332.9 N at 11.84 kn, residual resistance coeff 0.00030; fully appended 87.50 lb / 389.2 N at 11.85 kn, ratio 1.169; tripwires at 5% chord) — a possible future `CT` reference, **outside A1c's scope and not registered here**. |
| **Toxopeus 2008** (RANS bare hull at incidence) | Not attempted | Not retrieved. Would be a **code-to-code** comparison, not measured tier, and is bare hull not hull+sail. |
| **`ADA246217`** — retrieved, then **discarded** | Title-page check | It is **DTRC/SHD-1355-03**, *"…Turbulence at the Stern of an Axisymmetric Model…"*, a **different report series** on turbulence ingestion. **Rule 15 caught this**: the search engine had offered it as the Huang 1992 full text. Not filed. |

### 7.3 A disclosed systematic: our Reynolds number sits inside Roddy's own sensitivity band

Roddy's static stability experiments ran at **6.5 knots, `Re_L ≈ 14 million`** (report p. 3),
nondimensionalised on `LBP = 13.9792 ft (4.261 m)`. **Our solve is at `Re_L = 1.2e7`.**
Roddy states (same page) that the coefficients *"vary with Reynolds number up to a Reynolds
number … of about **10 to 15 million**, but above this value the coefficients no longer
significantly change"*. **Our 12 million is inside that transition band, not above it.**
The Re mismatch is therefore **not** negligible by Roddy's own criterion and is registered
here as a disclosed systematic on B1–B5, un-quantified.

*(Corroboration, in our favour on a different axis: SHD-1298-02 p. 19 states the HSMB PMM
statics were conducted at **`Re = 1.2×10⁷` based on model length** — our exact Reynolds
number. Our Re matches the PMM static programme; it does not match Roddy's 6.5-knot runs.)*

### 7.4 Standing limits

- A1c does **not** move, narrow, revive or relabel any A1b gate. L1's `NOT ADMITTED` and
  `CT`'s `NOT A RESULT` stand as frozen at `8efe38e8f`.
- A1c does **not** claim validation. With B6 `PENDING` and B3/B4/B5 lab-constructed, the
  **highest tier any A1c row can reach is CODE-VERIFIED with the disavowal "NOT
  experiment-validated"** — the ceiling A1b §8 already set — **except** B1/B2, which reach
  MEASURED tier **only if a bare-hull arm is actually run**.
- A1c does **not** freeze itself. §8 is blank.
- A1c has **launched nothing**. No queue entry exists.
- Nothing here is sent, filed, uploaded or registered outside this box (rule 7).

---

## 8. FREEZE BLOCK — cfd-SUPERVISOR, CHECK 4, UNDELEGATED

**INTENTIONALLY BLANK.** To be completed by the cfd-supervisor personally.
Before signing, §7.1 requires a decision: verify the Gertler & Hagen sign convention, or
drop B2/B4/B5 to `PENDING`.

```
Frozen at commit:      ____________________
Date/time (UTC):       ____________________
Pre-compute condition: the run directories named in §5 do not exist. Checked by: ________
Signed:                ____________________
```
